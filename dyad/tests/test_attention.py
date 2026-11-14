"""scripts/attention.py (the attention ledger, the aggregate desk; d-work #700): against a bare central repository and
two system checkouts in a temp dir — the central repository named per checkout by git config, never in a tracked file;
each event kind; the open set; sync idempotent, a failed push kept for the next sync; the fold at seven lines with its
`+n more`; an entry the reader cannot resolve printed as its reference; the slug resolved, never stored; no text copied
into the store; two readers at one fetch print the same text; and the closing line counting another system's question
and matter in flight, unchanged when no central repository is named. #703: one `registered` entry per checkout; a replay
that recovers an ask and answer made between syncs, from the registration on, appending nothing a second time; the
cross-row and held questions asked; `paired-units` desks and their `unpaired`; the pair verb's two refusals and its
declared pairing, which no sync closes; the drift line, unjudged where the reader cannot read; the fold's bound with
drift lines; and the home's warning, which no other unit prints."""
import contextlib, io, os, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dyadlib
att = dyadlib.load_module(Path(__file__).resolve().parents[1] / "scripts" / "attention.py", "dyad_attention_test")
board = dyadlib.load_guard("agent", "board")

ROW = "id: {id}\ntitle: t{id}\nopened: 2026-11-13\nstate: open\ndisposed: 2026-11-13 Y plan\nrefs: \nslug: {slug}\n"


def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=dyadlib.git_env(), check=True)


class AttentionTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus", "DYAD_SESSION": "eng-1"})
        e.start(); self.addCleanup(e.stop)
        self.tmp = Path(tempfile.mkdtemp()); self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.tmp)]))
        self.central = self.tmp / "central.git"
        git(["init", "-q", "--bare", "-b", "main", str(self.central)], self.tmp)
        seed = self.tmp / "seed"; git(["clone", "-q", str(self.central), str(seed)], self.tmp)
        (seed / "README").write_text("attention\n")
        git(["add", "README"], seed); git(["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "s"], seed)
        git(["push", "-q", "origin", "HEAD:main"], seed)
        self.a = self.system("a", "o/alpha")
        self.b = self.system("b", "o/beta")

    def system(self, name: str, ident: str) -> dict:
        repo = self.tmp / name
        git(["init", "-q", "-b", "main", str(repo)], self.tmp)
        git(["config", "user.name", "t"], repo); git(["config", "user.email", "t@t"], repo)
        clone = self.tmp / f"{name}-central"
        git(["clone", "-q", str(self.central), str(clone)], self.tmp)
        git(["config", "user.name", "t"], clone); git(["config", "user.email", "t@t"], clone)
        git(["config", "dyad.attention.clone", str(clone)], repo)
        git(["config", "dyad.attention.system", ident], repo)
        (repo / "agent-corpus" / "d-work" / "rows").mkdir(parents=True)
        (repo / "agent-corpus" / "d-work" / "board").mkdir(parents=True)
        self.commit(repo, "init", {"agent-corpus/d-work/rows/.keep": ""})
        git(["update-ref", "refs/remotes/origin/main", "HEAD"], repo)
        att.sync(repo, out=lambda m: None)                  # #703: the checkout registers once, at its first sync
        return {"repo": repo, "clone": clone, "system": ident}

    def commit(self, repo: Path, msg: str, files: dict[str, str]):
        for p, t in files.items():
            (repo / p).parent.mkdir(parents=True, exist_ok=True); (repo / p).write_text(t)
        git(["add", "-A"], repo); git(["commit", "-q", "-m", msg], repo)

    def ask(self, s: dict, rid: int, phase: str = "plan-asked", holder: str = "program-1", extra: str = ""):
        self.commit(s["repo"], f"ask {rid}", {
            f"agent-corpus/d-work/rows/{rid}.md": ROW.format(id=rid, slug=f"row{rid}-slug"),
            f"agent-corpus/d-work/board/{rid}.md": f"holder: {holder}\nphase: {phase}\n{extra}owner: eng-1\n"
                                                    f"question: Y/N: proceed with #{rid} as planned?\n"})

    def sync(self, s: dict) -> str:
        out = []
        att.sync(s["repo"], out=out.append)
        return "\n".join(out)

    def test_no_central_repository_named_says_so_and_the_line_is_todays(self):
        git(["config", "--unset", "dyad.attention.clone"], self.a["repo"])
        self.assertEqual(self.sync(self.a), att.NONE_NAMED)
        self.assertEqual(board.attention_open(self.a["repo"]), [])

    def test_sync_writes_references_only_and_is_idempotent(self):
        self.ask(self.a, 5)
        self.assertEqual(self.sync(self.a), "attention: 1 entries")
        self.assertEqual(self.sync(self.a), "attention: 0 entries")
        got = [e for e in att.entries(self.a["clone"]) if e[1]["kind"] != "registered"]
        self.assertEqual(len(got), 1)
        name, f = got[0]
        self.assertTrue(name.startswith("attention/o--alpha/program-1/"))
        self.assertEqual((f["kind"], f["row"], f["what"]), ("asked", "5", "plan"))
        text = (self.a["clone"] / name).read_text()
        self.assertNotIn("proceed with", text)          # no question text copied
        self.assertNotIn("slug", text)                  # the slug is resolved at print, never stored
        self.assertRegex(f["ref"], r"^agent-corpus/d-work/board/5\.md@[0-9a-f]{40}$")

    def test_an_answered_question_closes_and_leaves_the_open_set(self):
        self.ask(self.a, 5); self.sync(self.a)
        self.commit(self.a["repo"], "answer", {"agent-corpus/d-work/board/5.md": "holder: program-1\nphase: building\n"
                                                                              "owner: eng-1\n"})
        self.assertEqual(self.sync(self.a), "attention: 1 entries")
        kinds = [f["kind"] for _, f in att.entries(self.a["clone"]) if f["kind"] != "registered"]
        self.assertEqual(kinds, ["asked", "answered"])
        self.assertEqual(att.open_set(att.entries(self.a["clone"])), [])

    def test_a_pr_not_on_main_is_in_flight_and_lands_when_it_is(self):
        self.commit(self.a["repo"], "work", {"x.txt": "x"})
        head = git(["rev-parse", "HEAD"], self.a["repo"]).stdout.strip()
        self.commit(self.a["repo"], "pr", {
            "agent-corpus/d-work/rows/7.md": ROW.format(id=7, slug="r7"),
            "agent-corpus/d-work/board/7.md": f"holder: program-1\nphase: verifying\n  unit: eng-1\n  pr: 90 at {head}\n"
                                              "owner: eng-1\n"})
        self.sync(self.a)
        (_, f), = att.open_set(att.entries(self.a["clone"]))
        self.assertEqual((f["kind"], f["unit"], f["what"]), ("in-flight", "eng-1", f"pr 90 at {head[:12]}"))
        git(["update-ref", "refs/remotes/origin/main", "HEAD"], self.a["repo"])
        self.sync(self.a)
        self.assertEqual(att.open_set(att.entries(self.a["clone"])), [])

    def test_a_failed_push_keeps_the_commit_for_the_next_sync(self):
        self.ask(self.a, 5)
        git(["remote", "set-url", "origin", str(self.tmp / "nowhere.git")], self.a["clone"])
        out = self.sync(self.a)
        self.assertIn("the push failed", out)
        git(["remote", "set-url", "origin", str(self.central)], self.a["clone"])
        self.assertEqual(self.sync(self.a), "attention: 0 entries")    # nothing new to derive, the commit pushed
        log = git(["log", "--oneline", "main"], self.central).stdout
        self.assertIn("attention: o/alpha 1 entry", log)

    def test_the_closing_line_counts_another_systems_question_and_matter_in_flight(self):
        self.ask(self.b, 3, phase="done-asked", holder="program-2")
        head = git(["rev-parse", "HEAD"], self.b["repo"]).stdout.strip()
        self.commit(self.b["repo"], "pr", {
            "agent-corpus/d-work/rows/4.md": ROW.format(id=4, slug="r4"),
            "agent-corpus/d-work/board/4.md": f"holder: program-2\nphase: verifying\n  unit: eng-2\n  pr: 12 at {head}\n"
                                              "owner: eng-2\n"})
        git(["update-ref", "refs/remotes/origin/main", "HEAD~2"], self.b["repo"])
        self.sync(self.b)
        git(["pull", "-q"], self.a["clone"])
        line = board.awaiting_line(self.a["repo"], got=[], coming=True, reader="program-1")
        self.assertIn("#3 in o/beta/program-2", line)
        self.assertIn("in-flight 1", line)
        own = [f for f in board.attention_open(self.a["repo"])]
        self.assertTrue(all(f["system"] == "o/beta" for f in own))     # this system's own come from its board

    def test_the_fold_bounds_the_desk_at_seven_lines_and_resolves_or_says_unresolved(self):
        for rid in range(1, 10):
            self.ask(self.b, rid)
        self.sync(self.b)
        git(["pull", "-q"], self.a["clone"])
        git(["config", "--add", "dyad.attention.checkout", f"o/beta {self.b['repo']}"], self.a["repo"])
        c = att.config(self.a["repo"])
        items = att.open_set(att.entries(c["clone"]))
        lines = att.fold(items, c["checkouts"], "0m ago")
        self.assertEqual(len(lines), att.FOLD)
        self.assertTrue(lines[0].startswith("attention: 9 open, fetched 0m ago — o/beta 9"))
        self.assertEqual(lines[-1], "  +4 more (dyad attention --full)")
        self.assertIn("#1-row1-slug Y/N: proceed with #1 as planned?", lines[1])   # resolved from the reader's checkout
        self.assertEqual(len(att.fold(items, c["checkouts"], "0m ago", full=True)), 10)
        bare = att.fold(items, {}, "0m ago")
        self.assertIn("#1 (unresolved)", bare[1])                                 # no checkout: the reference alone

    def test_two_readers_at_one_fetch_print_the_same_text(self):
        self.ask(self.b, 2); self.sync(self.b)
        for s in (self.a, self.b):
            git(["pull", "-q"], s["clone"])
        ca, cb = att.config(self.a["repo"]), att.config(self.b["repo"])
        same = {"o/beta": self.b["repo"]}
        la = att.fold(att.open_set(att.entries(ca["clone"])), same, "x")
        lb = att.fold(att.open_set(att.entries(cb["clone"])), same, "x")
        self.assertEqual(la, lb)

    def test_the_verb_prints_the_desk_and_refuses_an_unknown_word(self):
        self.ask(self.a, 5); self.sync(self.a)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(att.main([], self.a["repo"]), 0)
        self.assertIn("attention: 1 open", buf.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(att.main(["--bogus"], self.a["repo"]), 1)

    # ---- #703: registered, replay, cross-row and held questions, pairings, the pair verb, drift, the home's warning

    def kinds(self, s: dict, *ks: str) -> list[dict[str, str]]:
        return [f for _, f in att.entries(s["clone"]) if f["system"] == s["system"] and (not ks or f["kind"] in ks)]

    def pref(self, names: str) -> str:
        return ("| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"
                f"| paired-units | {names} | `none`, or unit names | Rule-16 |\n")

    def test_a_checkout_registers_once_ref_d_at_its_presence_file(self):
        reg = self.kinds(self.a, "registered")
        self.assertEqual(len(reg), 1)
        self.assertEqual((reg[0]["unit"], reg[0]["what"], reg[0]["row"]), ("eng-1", "checkout", "-"))
        self.assertRegex(reg[0]["ref"], r"^agent-corpus/d-work/sessions/eng-1\.md@[0-9a-f]{40}$")
        self.sync(self.a)
        self.assertEqual(len(self.kinds(self.a, "registered")), 1)
        self.assertEqual(att.open_set(att.entries(self.a["clone"])), [])     # never in the open set

    def test_a_replay_recovers_an_ask_and_answer_made_between_two_syncs(self):
        self.ask(self.a, 5)
        asked_at = git(["rev-parse", "HEAD"], self.a["repo"]).stdout.strip()
        self.commit(self.a["repo"], "answer", {"agent-corpus/d-work/board/5.md": "holder: program-1\nphase: building\n"
                                                                              "owner: eng-1\n"})
        answered_at = git(["rev-parse", "HEAD"], self.a["repo"]).stdout.strip()
        self.assertEqual(self.sync(self.a), "attention: 2 entries")
        got = self.kinds(self.a, "asked", "answered")
        self.assertEqual([(f["kind"], f["ref"].partition("@")[2]) for f in got],
                         [("asked", asked_at), ("answered", answered_at)])
        self.assertEqual(self.sync(self.a), "attention: 0 entries")             # a second replay appends nothing

    def test_the_first_run_replays_from_the_registration_it_names(self):
        repo = self.tmp / "c"
        git(["init", "-q", "-b", "main", str(repo)], self.tmp)
        git(["config", "user.name", "t"], repo); git(["config", "user.email", "t@t"], repo)
        clone = self.tmp / "c-central"; git(["clone", "-q", str(self.central), str(clone)], self.tmp)
        git(["config", "user.name", "t"], clone); git(["config", "user.email", "t@t"], clone)
        git(["config", "dyad.attention.clone", str(clone)], repo); git(["config", "dyad.attention.system", "o/gamma"], repo)
        c = {"repo": repo, "clone": clone, "system": "o/gamma"}
        self.commit(repo, "init", {"agent-corpus/d-work/rows/.keep": "", "agent-corpus/d-work/board/.keep": ""})
        reg = git(["rev-parse", "HEAD"], repo).stdout.strip()
        self.ask(c, 4)
        self.commit(repo, "answer", {"agent-corpus/d-work/board/4.md": "holder: program-1\nphase: building\n"})
        git(["update-ref", "refs/remotes/origin/main", "HEAD"], repo)
        out = []
        att.sync(repo, out=out.append, since=reg)
        self.assertEqual(out, ["attention: 3 entries"])
        self.assertEqual([f["kind"] for f in self.kinds(c)], ["registered", "asked", "answered"])
        self.assertTrue(self.kinds(c, "registered")[0]["ref"].endswith("@" + reg))

    def test_a_cross_row_question_and_a_held_entrys_hand_asked_question_are_asked(self):
        self.commit(self.a["repo"], "cos", {
            "agent-corpus/d-work/board/_cos.md": "holder: program-1\nquestion: Y/N: archive #3, #4?\n",
            "agent-corpus/d-work/rows/6.md": ROW.format(id=6, slug="r6"),
            "agent-corpus/d-work/board/6.md": "holder: program-1\nphase: held\nowner: eng-1\n"
                                              "question: Y/N: merge PR #9?\n"})
        self.sync(self.a)
        got = {(f["row"], f["what"]) for _, f in att.open_set(att.entries(self.a["clone"]))}
        self.assertEqual(got, {("_cos", "retirement"), ("6", "merge")})

    def test_paired_units_become_desks_and_a_name_dropped_is_unpaired(self):
        self.commit(self.a["repo"], "pref", {"preferences-corpus/PREFERENCES.md": self.pref("communicate, counsel")})
        self.sync(self.a)
        desks = {(f["unit"], f["what"]) for _, f in att.desks(att.entries(self.a["clone"]))}
        self.assertEqual(desks, {("communicate", "paired-units"), ("counsel", "paired-units")})
        self.commit(self.a["repo"], "unpair", {"preferences-corpus/PREFERENCES.md": self.pref("communicate")})
        self.sync(self.a)
        self.assertEqual([f["unit"] for _, f in att.desks(att.entries(self.a["clone"]))], ["communicate"])
        self.assertEqual([f["unit"] for f in self.kinds(self.a, "unpaired")], ["counsel"])
        text = "".join((self.a["clone"] / n).read_text() for n, _ in att.entries(self.a["clone"]))
        self.assertNotIn("Rule-16", text)                               # a unit name is the only value held

    def test_the_pair_verb_refuses_an_unresolved_ref_and_a_system_that_keeps_the_preference(self):
        rows = git(["rev-parse", "HEAD"], self.a["repo"]).stdout.strip()
        errs = []
        self.assertEqual(att.pair(self.a["repo"], "o/new/desk", "nowhere.md@" + rows, out=lambda m: None,
                                  err=errs.append), 1)
        self.assertIn("resolves in no checkout", errs[-1])
        self.commit(self.a["repo"], "pref", {"preferences-corpus/PREFERENCES.md": self.pref("none")})
        self.assertEqual(att.pair(self.a["repo"], "o/alpha/desk", "agent-corpus/d-work/rows/.keep@" + rows,
                                  out=lambda m: None, err=errs.append), 1)
        self.assertIn("keeps a `paired-units` preference", errs[-1])

    def test_the_pair_verb_declares_and_drops_a_pairing_no_system_holds(self):
        rows = git(["rev-parse", "HEAD"], self.a["repo"]).stdout.strip()
        ref = "agent-corpus/d-work/rows/.keep@" + rows
        out = []
        self.assertEqual(att.pair(self.a["repo"], "o/new/desk", ref, out=out.append), 0)
        (_, f), = att.desks(att.entries(self.a["clone"]))
        self.assertEqual((f["system"], f["unit"], f["what"], f["ref"]), ("o/new", "desk", "declared", ref))
        self.sync(self.a)                                                # this system's sync never closes it
        self.assertEqual(len(att.desks(att.entries(self.a["clone"]))), 1)
        self.assertEqual(att.pair(self.a["repo"], "o/new/desk", ref, drop=True, out=out.append), 0)
        self.assertEqual(att.desks(att.entries(self.a["clone"])), [])
        self.assertEqual(out[-1], "attention: 1 entries")

    def test_a_drift_line_names_the_preference_as_the_one_that_stands(self):
        self.commit(self.a["repo"], "pref", {"preferences-corpus/PREFERENCES.md": self.pref("communicate")})
        self.sync(self.a)
        self.commit(self.a["repo"], "pref2", {"preferences-corpus/PREFERENCES.md": self.pref("communicate, counsel")})
        c = att.config(self.a["repo"])
        got = att.entries(c["clone"])
        lines = att.fold(att.open_set(got), c["checkouts"], "0m ago", got=got)
        self.assertIn("desks 1", lines[0])
        self.assertIn("registered o/alpha 1", lines[0])
        self.assertEqual(lines[1], "  drift: o/alpha paired-units names communicate, counsel, the ledger holds "
                                   "communicate; the preference stands (the next sync of o/alpha corrects it)")
        self.assertEqual(att.drift(got, {}), [])                          # a system the reader cannot read: no judgement
        self.sync(self.a)
        self.assertEqual(att.drift(att.entries(c["clone"]), c["checkouts"]), [])

    def test_the_fold_keeps_seven_lines_with_drift_lines_present(self):
        for rid in range(1, 10):
            self.ask(self.a, rid)
        self.sync(self.a)
        got = att.entries(self.a["clone"])
        checkouts = {f"o/s{i}": self.tmp / f"s{i}" for i in range(6)}
        for p in checkouts.values():
            (p / "preferences-corpus").mkdir(parents=True)
            (p / "preferences-corpus" / "PREFERENCES.md").write_text(self.pref("x"))
        lines = att.fold(att.open_set(got), checkouts, "0m ago", got=got)
        self.assertEqual(len(lines), att.FOLD)
        self.assertEqual(sum(1 for l in lines if l.startswith("  drift:")), att.DRIFT_MAX - 1)
        self.assertIn("  +4 systems drift (dyad attention --full)", lines)
        self.assertTrue(lines[-1].startswith("  +") and lines[-1].endswith("more (dyad attention --full)"))
        self.assertEqual(len(att.fold(att.open_set(got), checkouts, "0m ago", full=True, got=got)), 1 + 6 + 9)

    def test_the_home_warns_when_its_checkout_names_no_clone_and_no_other_unit_does(self):
        ss = dyadlib.load_guard("agent", "sessions")
        home = "program-59cec502"
        self.assertTrue(ss.is_leader(home))
        self.assertIsNone(ss.attention_warning(self.a["repo"], home))
        git(["config", "--unset", "dyad.attention.clone"], self.a["repo"])
        self.assertEqual(ss.attention_warning(self.a["repo"], home), ss.ATTENTION_UNNAMED)
        self.assertIsNone(ss.attention_warning(self.a["repo"], "engineer-1537d8fb"))


if __name__ == "__main__":
    unittest.main()
