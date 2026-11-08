"""The decision functions of d-work #641: each record codified there is decided by one function beside the inputs it
reads, and this file pins every outcome of each, by the record's own `termCode`s. A table per record lists a case for
each outcome; the test fails if a case's result is not its outcome, or if the cases do not cover exactly the record's
outcomes (read from `dyad/dmc/<record>.jsonld`), so an outcome added to a record without a case is caught too."""
import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
load = lambda name: dyadlib.load_module(PKG / "scripts" / f"{name}.py", f"decisions_{name}")
merge, land, levels, trace, runbook, automaton = (load(n) for n in (
    "merge", "land", "levels", "trace", "runbook", "automaton"))
sessions, rows, plans = (dyadlib.load_guard("agent", g) for g in ("sessions", "rows", "plans"))


def codes(record: str) -> set[str]:
    return {o["termCode"] for o in json.loads((PKG / "dmc" / f"{record}.jsonld").read_text())["hasDefinedTerm"]}


CASES = {   # record: [(outcome termCode, a call that must decide it)]
    "session-overlap": [
        ("same-root", lambda: sessions.session_overlap({"a.py"}, "/r", {"root": "/r", "files": "a.py"})),   # outranks
        ("overlap", lambda: sessions.session_overlap({"a.py", "b.py"}, "/r", {"root": "/s", "files": "b.py c.py"})),
        ("disjoint", lambda: sessions.session_overlap({"a.py"}, "/r", {"root": "/s", "files": "c.py"}))],
    "y-binding": [
        ("bound", lambda: merge.y_binding({7: "abc"}, 7, "abc")),
        ("re-prompt", lambda: merge.y_binding({7: "abc"}, 7, "def")),
        ("fresh-y", lambda: merge.y_binding({7: "abc"}, 8, "abc"))],
    "message-route": [
        ("self", lambda: land.message_route(True, True, True, False)),          # self-addressed outranks all
        ("home-rings", lambda: land.message_route(True, True, False, True)),
        ("poll", lambda: land.message_route(False, True, False, False)),
        ("copy", lambda: land.message_route(False, False, False, True)),
        ("post-and-ring", lambda: land.message_route(False, True, False, True))],
    "diag-level": [
        ("l1", lambda: levels.diag_level("coded", "unit")), ("l2", lambda: levels.diag_level("coded", "system")),
        ("l3", lambda: levels.diag_level("prose", "unit")), ("l4", lambda: levels.diag_level("prose", "system"))],
    "trace-bottleneck": [
        ("operator", lambda: trace.bottleneck_side("idle")), ("inference", lambda: trace.bottleneck_side("inference")),
        ("mechanical", lambda: trace.bottleneck_side("suite"))],
    "parent-askable": [
        ("askable", lambda: rows.parent_askable([("done", False), ("blocked", False), ("planned", True), ("backlog", False)])),
        ("unaskable", lambda: rows.parent_askable([("done", False), ("open", False)]))],
    "replan": [
        ("accreted", lambda: plans.replan(True, ["a.py"])), ("replan", lambda: plans.replan(False, ["a.py"])),
        ("as-written", lambda: plans.replan(False, []))],
    "ci-red-vs-absent": [
        ("red", lambda: automaton.ci_state(True, True, {"conclusion": "failure"})),
        ("passes", lambda: automaton.ci_state(True, True, {"conclusion": "success"})),
        ("absent", lambda: automaton.ci_state(False, True, None))],
    "answer-grammar": [
        ("y", lambda: dyadlib.answer_kind("yes, and add a test")), ("n-bare", lambda: dyadlib.answer_kind("n")),
        ("n-bare-intent", lambda: dyadlib.answer_kind("N", intent=True)),
        ("amend", lambda: dyadlib.answer_kind("N: split it in two")), ("silence", lambda: dyadlib.answer_kind(None))],
}


class DecisionTests(unittest.TestCase):
    def test_every_outcome_of_every_record_is_decided(self):
        for record, cases in CASES.items():
            with self.subTest(record=record):
                self.assertEqual({c for c, _ in cases}, codes(record), "the cases cover exactly the record's outcomes")
                for code, call in cases:
                    self.assertEqual(call(), code, f"{record}: {code}")

    def test_the_undecided_cases_say_none_or_refuse(self):
        self.assertIsNone(dyadlib.answer_kind("maybe later"))                 # two readings: the agent asks
        self.assertIsNone(automaton.ci_state(False, True, {"conclusion": "success"}))
        for bad in (lambda: levels.diag_level("coded", "module"), lambda: trace.bottleneck_side("lunch")):
            with self.assertRaises(ValueError):
                bad()

    def test_moved_files_and_deployed_done_read_the_tree(self):
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        env = {**os.environ, **dyadlib.git_env()}
        run = lambda *a: subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                        check=True, capture_output=True, text=True, env=env).stdout.strip()
        run("init", "-q", "-b", "main"); (d / "a.py").write_text("1\n"); (d / "b.py").write_text("1\n")
        run("add", "-A"); run("commit", "-qm", "base"); base = run("rev-parse", "HEAD")
        (d / "a.py").write_text("2\n"); run("commit", "-qam", "move a")
        self.assertEqual(plans.moved_files(d, base, ["a.py", "b.py"], "HEAD"), ["a.py"])
        self.assertEqual(plans.moved_files(d, "nosuch", ["a.py"], "HEAD"), [])
        os.environ.pop("DYAD_RUNBOOKS", None)
        rb = d / runbook.DEFAULT_RUNBOOKS; rb.mkdir(parents=True)
        self.assertEqual(runbook.deployed_done(d, "srv"), "not-done")         # no run-book
        block = lambda n, c: f"```dyad-cmd\nname: {n}\nclass: read-only\nrole: any\nundo: none\npostcondition: none\nscope: x\n\n{c}\n```\n"
        (rb / "srv.md").write_text("# Run-book: srv\n\n## Status/health\n" + block("health", "true"))
        self.assertEqual(runbook.deployed_done(d, "srv"), "not-done")         # no passing event yet
        ep = runbook.events_path(d, "srv"); ep.parent.mkdir(parents=True)
        ep.write_text(json.dumps({"name": "health", "ts": "2026-11-08T10:00:00Z", "exit": 0, "postcondition": "n/a"}) + "\n")
        self.assertEqual(runbook.deployed_done(d, "srv"), "deployed")
        self.assertEqual(runbook.deployed_done(d, "srv", since="2026-11-08T09:00:00Z"), "deployed")
        self.assertEqual(runbook.deployed_done(d, "srv", since="2026-11-08T11:00:00Z"), "not-done")   # before the plan-Y
        ep.write_text(ep.read_text() + json.dumps({"name": "health", "exit": 1, "postcondition": "n/a"}) + "\n")
        self.assertEqual(runbook.deployed_done(d, "srv"), "not-done")         # the latest event decides


if __name__ == "__main__":
    unittest.main()
