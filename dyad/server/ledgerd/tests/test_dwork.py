"""ledgerd/schemas/dwork.py: the d-work schema — its tables equal the guards' parsers' fields (TREE_INVARIANTS run
here), `load` over the fixture instance (rows at several states, dispositions and refs split, the plan's parts
and its why/how, plan_files, sessions with session_rows and session_files, provenance entries, the trace's five
sections, the run-book event), and the `board`, `backlog` and `unheld` views' rows — `unnamed-*` claims never
count, `(no plan)` without a plan, `seat@holder` for every named seat. Also the assertion that the test mapping,
the runner's invariant pass and the manifest scan each name every ledgerd module (plan #336 revision 16): the
mapping part passes once the syseng component clause (PR S, branch 336-syseng-component-clause) is in the tree.
Importing the module runs its INVARIANTS (verifiable-code.md p5)."""
import unittest
from pathlib import Path
import support
from support import Case
import dyadlib
if not support.MISSING:
    from ledgerd import schema as S, core
    from ledgerd.schemas import dwork
    from test_core import service_for

class SchemaTests(Case):
    def test_contract_and_tree_invariants(self):
        self.assertIsNone(S.schema_problem(dwork))
        dyadlib.check_invariants(dwork)                           # TREE_INVARIANTS: the columns equal the guards' field tuples
        self.assertEqual(dwork.STORES, ("agent-corpus/d-work", "workstation-corpus/runbooks/events"))
        self.assertEqual(dwork.RENDERED, ("board", "backlog", "unheld")); self.assertEqual(dwork.DEFAULT_VIEW, "board")
    def test_tables_equal_the_parsers_fields(self):
        sessions = dyadlib.load_guard("agent", "sessions"); provenance = dyadlib.load_guard("agent", "provenance")
        runbook = dyadlib.load_module(dyadlib.PKG / "scripts" / "runbook.py", "runbook"); trace = dyadlib.load_module(dyadlib.PKG / "scripts" / "trace.py", "trace")
        self.assertEqual(tuple(S.columns_of(dwork, "rows")), dyadlib.FIELDS + dyadlib.OPTIONAL_FIELDS)
        self.assertEqual(tuple(S.columns_of(dwork, "sessions"))[:5], sessions.FIELDS)
        self.assertEqual(tuple(S.columns_of(dwork, "provenance"))[1:], provenance.FIELDS)
        self.assertEqual(tuple(S.columns_of(dwork, "events")), runbook.EVENT_FIELDS)
        self.assertEqual(tuple(S.columns_of(dwork, "traces"))[2:], tuple(s.lower() for s in trace.SECTIONS))
        self.assertEqual(tuple(S.columns_of(dwork, "plans")), ("id", "title", "base_commit", "intent", "intent_as_read", "mutation", "files_touched", "falsification", "why", "how"))
        self.assertEqual(S.columns_of(dwork, "dispositions"), ["row_id", "n", "date", "verdict", "note", "entry"])
        self.assertEqual(set(dwork.DETAIL), {"rows", "plans", "dispositions", "provenance", "session_rows"})
    def test_daemon_modules_import_no_guard(self):
        comp = support.COMPONENT / "ledgerd"
        for name in ("core", "store", "schema", "auth", "supervisor", "ui", "cli"):
            text = (comp / f"{name}.py").read_text()
            self.assertNotIn("load_guard", text, name); self.assertNotIn("dyad/guards", text.replace("dyad/guards/` ", ""), name); self.assertNotIn("d-work", text.lower().replace("knows nothing of d-work", "").replace("what a d-work is", "").replace("d-work #336", "").replace("d-work ledger", ""), name)
        self.assertIn("load_guard", (comp / "schemas" / "dwork.py").read_text())

class LoadTests(Case):
    def setUp(self):
        self.repo = support.instance(self.scratch())
        self.data = dwork.load(self.repo)
    def test_rows_dispositions_refs(self):
        rows = {r["id"]: r for r in self.data["rows"]}
        self.assertEqual(sorted(rows), [1, 2, 3, 4, 5, 6]); self.assertEqual(rows[6]["mode"], "implicit"); self.assertEqual(rows[1]["mode"], "explicit")
        d = [x for x in self.data["dispositions"] if x["row_id"] == 5]
        self.assertEqual(d, [{"row_id": 5, "n": 1, "date": "2026-10-01", "verdict": "Y", "note": "plan", "entry": "2026-10-01 Y plan"},
                             {"row_id": 5, "n": 2, "date": "2026-10-05", "verdict": "Y", "note": "done (merges PR #9 at abc1234)", "entry": "2026-10-05 Y done (merges PR #9 at abc1234)"}])
        self.assertEqual([x for x in self.data["refs"] if x["row_id"] == 2], [{"row_id": 2, "n": 1, "token": "parent"}, {"row_id": 2, "n": 2, "token": "#1"}])
        self.assertEqual(dwork.entry_parts("odd text", dyadlib.load_guard("agent", "rows").ENTRY), ("", "", "odd text"))
    def test_plans_and_plan_files(self):
        p = self.data["plans"][0]
        self.assertEqual((p["id"], p["title"], p["base_commit"]), (2, "a planned row with a plan", "0123456789abcdef0123456789abcdef01234567"))
        self.assertEqual(p["intent_as_read"], "Build the thing the Operator asked for. Then build the next thing.")
        self.assertEqual(p["why"], "Build the thing the Operator asked for."); self.assertEqual(p["how"], "Write module a.")
        self.assertTrue(p["mutation"].startswith("1. Write module a.")); self.assertIn("| A1 |", p["falsification"])
        self.assertEqual(p["files_touched"], "dyad/scripts/a.py dyad/scripts/b.py dyad/tests/test_a.py")
        self.assertEqual([f["path"] for f in self.data["plan_files"]], ["dyad/scripts/a.py", "dyad/scripts/b.py", "dyad/tests/test_a.py"])
    def test_part_text_forms(self):
        self.assertEqual(dwork.part_text("## Intent as read\nA.\n\n### sub\nB.\n## Mutation\nC.\n", "intent as read"), "A.\n\n### sub\nB.")
        self.assertEqual(dwork.part_text("**Intent as read:** A line.\nmore.\n\nnext para\n", "intent as read"), "A line.\nmore.")
        self.assertEqual(dwork.part_text("nothing here", "mutation"), "")
    def test_sessions(self):
        s = {x["session"]: x for x in self.data["sessions"]}
        self.assertEqual(set(s), {"seat-a", "seat-b", "unnamed-deadbeef0001"})
        self.assertEqual((s["seat-a"]["holder"], s["seat-a"]["kernel"], s["seat-a"]["os"], s["seat-a"]["arch"], s["seat-a"]["path"]), ("holder-a", "cloud", "linux", "x86_64", "seat-a.md"))
        self.assertEqual(s["unnamed-deadbeef0001"]["kernel"], "")
        self.assertEqual(sorted((x["session"], x["row_id"]) for x in self.data["session_rows"]), [("seat-a", 1), ("seat-a", 2), ("seat-b", 2), ("unnamed-deadbeef0001", 1), ("unnamed-deadbeef0001", 3)])
        self.assertEqual(self.data["session_files"], [{"session": "seat-a", "path": "dyad/scripts/a.py"}])
    def test_provenance_traces_events(self):
        self.assertEqual([(e["n"], e["kind"], e["text"]) for e in self.data["provenance"]], [(1, "prompt", "do the thing"), (2, "disposition", "Y"), (3, "disposition", "N: not yet")])
        t = self.data["traces"][0]
        self.assertEqual((t["id"], t["title"]), (5, "a done row")); self.assertIn("| 2026-10-01 10:00:00 | Operator | prompt |", t["timeline"]); self.assertEqual(t["bottleneck"], "none")
        e = self.data["events"][0]
        self.assertEqual((e["id"], e["exit"], e["duration_ms"], e["class"]), ("x-20261001T100000Z-status", 0, 12, "read-only"))
    def test_empty_tree_loads_empty_tables(self):
        d = self.scratch()
        self.assertEqual({k: v for k, v in dwork.load(d).items() if v}, {})

class ViewTests(Case):
    def test_board_backlog_unheld(self):
        svc, _ = service_for(self, git=False)
        cols, rows = svc.query("SELECT * FROM board")
        self.assertEqual(cols, ["id", "status", "what", "why", "how", "who", "seen"])
        self.assertEqual(rows, [
            [1, "open", "first open row", "(no plan)", "(no plan)", "seat-a@holder-a", "2026-10-10T10:00:00+00:00"],
            [2, "planned", "a planned row with a plan", "Build the thing the Operator asked for.", "Write module a.", "seat-a@holder-a seat-b@-", "2026-10-11T10:00:00+00:00"],
            [3, "blocked", "a blocked row", "(no plan)", "(no plan)", "-", None],
            [6, "open", "an accreted row", "(no plan)", "(no plan)", "-", None]])
        self.assertEqual(svc.query("SELECT * FROM backlog")[1], [[4, "a backlog row", "2026-10-01"]])
        self.assertEqual([r[0] for r in svc.query("SELECT * FROM unheld")[1]], [3, 6])
    def test_rendered_board_shape(self):
        svc, _ = service_for(self, git=False)
        md = svc.rendered("board", ".md")
        self.assertIn("| 2 | planned | a planned row with a plan | Build the thing the Operator asked for. | Write module a. | seat-a@holder-a seat-b@- | 2026-10-11T10:00:00+00:00 |", md)

class MechanismsNameEveryModuleTests(Case):
    """Revision 16: the three silent exemptions cannot occur — the syseng test mapping, the runner's invariant pass and
    the manifest scan each name every ledgerd module. The mapping clause lands with PR S (branch
    336-syseng-component-clause); until this branch is rebased onto it that subtest fails, by design."""
    def modules(self) -> list[Path]:
        comp = support.COMPONENT
        return sorted(p for p in (comp / "ledgerd").rglob("*.py") if not p.name.startswith("_") and "__pycache__" not in p.parts)
    def test_mapping_pass_and_scan(self):
        mods = self.modules(); root = support.PKG.parent
        rel = lambda p: p.relative_to(root).as_posix()
        with self.subTest("the runner's invariant pass (package.component_invariant_modules)"):
            runner = dyadlib.runner_module()
            labels = {l for l, _, _ in runner.component_invariant_modules()}
            expected = {p.relative_to(support.COMPONENT).with_suffix("").as_posix().replace("/", ".") for p in mods}
            self.assertEqual(labels, expected)
        with self.subTest("the manifest guard's import scan (manifest.python_dirs)"):
            manifest = dyadlib.load_guard("infra", "manifest")
            dirs = set(manifest.python_dirs())
            for p in mods:
                self.assertIn(p.parent, dirs, rel(p))
            self.assertIn(support.COMPONENT / "tests", dirs)
        with self.subTest("the syseng test mapping (crafts/syseng/guards/tests.py, the component clause of PR S)"):
            tests_guard = dyadlib.find_guard("craft", "tests")
            if tests_guard is None:
                self.skipTest("the syseng craft is not installed here")
            mapped = {m["module"]: m["test"] for m in tests_guard.mapping()}
            for p in mods:
                self.assertIn(rel(p), mapped, f"{rel(p)} is not in the test mapping: the syseng component clause (PR S) is not in this tree yet")
                self.assertEqual(mapped[rel(p)], rel(support.COMPONENT / "tests" / f"test_{p.stem}.py"))
                self.assertTrue((support.COMPONENT / "tests" / f"test_{p.stem}.py").is_file(), p.stem)
        with self.subTest("every stem is distinct across the component (the mapping could not tell two apart)"):
            stems = [p.stem for p in mods]
            self.assertEqual(sorted(set(stems)), sorted(stems))

if __name__ == "__main__":
    unittest.main()
