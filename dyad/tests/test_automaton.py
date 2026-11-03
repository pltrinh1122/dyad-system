"""`dyad automaton scan|run` (scripts/automaton.py, d-work #556), over an installed scratch world: a real scratch
install as the seed, a bare origin, a racer clone that pushes PR heads as `refs/pull/<n>/head` and lands on main, and
a seat clone whose pre-push hook only logs.

The cases:
- `scan` lists the acts and writes nothing.
- `run` merges the PR a recorded `Y done` names, then closes the row, its accreted row and its board entry in the same
  run; a second run has nothing to do.
- A `Y done` naming a head the PR has moved off is refused. The refusal is posted once to the home's inbox (the board
  `_cos` holder), naming the row and quoting no entry; a second run does not post it again.
- A planned row with a board entry notifies each owner once.
- A push race is re-merged at once, without backoff.
- A row naming two PRs lands them as one cut: one push (#562).
- Misuse is exit 2."""
import contextlib, io, os, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib, livetest
from test_steps import World, git, ROW, REC, INST

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
HOME = "program-aaaaaaaa"


def run(argv, repo, **envs):
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, **envs}), \
         contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = am.main(argv, repo)
    return rc, out.getvalue(), err.getvalue()


class AutomatonTests(unittest.TestCase):
    def setUp(self):
        seed = SCRATCH.copy(False)
        top = SCRATCH.mkdtemp(); moved = top / "seed"; seed.rename(moved)
        git(moved, "branch", "-M", "main")
        self.w = World(moved)
        self.sha = self.w.pr(7, "dyad/zz-pr.txt", "pr\n")
        rows, prov, b = f"{INST}/d-work/rows", f"{INST}/d-work/provenance", f"{INST}/d-work/board"
        self.files = {
            f"{rows}/9.md": ROW.format(id=9, state="planned", disposed=f"2026-11-02 Y plan; 2026-11-02 Y done (accreted #10, merges PR #7 at {self.sha})"),
            f"{prov}/9.md": REC.format(id=9),
            f"{rows}/10.md": ROW.format(id=10, state="open", disposed="2026-11-02 Y plan (mandate #9)"),
            f"{prov}/10.md": "# Provenance #10\n\n## 1 disposition 2026-11-02 mandate #9, 2026-11-02\n\n```\nY\n```\n\n",
            f"{b}/9.md": f"holder: {HOME}\nwaiting-on: operator\nwriter: h1\n",
            f"{b}/_cos.md": f"holder: {HOME}\nwriter: h1\n"}

    def on_main(self, rel):
        r = subprocess.run(["git", "show", f"main:{rel}"], cwd=self.w.origin, capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None

    def inbox(self, seat):
        r = subprocess.run(["git", "ls-tree", "--name-only", f"main:{INST}/d-work/inbox/{seat}"], cwd=self.w.origin,
                           capture_output=True, text=True)
        return [self.on_main(f"{INST}/d-work/inbox/{seat}/{n}") for n in r.stdout.split() if n.endswith(".md")]

    def test_scan_lists_and_run_merges_then_closes(self):
        self.w.write_main(self.files)
        before = git(self.w.origin, "rev-parse", "main")
        rc, out, err = run(["scan"], self.w.seat)
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.strip(), f"merge PR #7 at {self.sha} (row #9)")
        self.assertEqual(git(self.w.origin, "rev-parse", "main"), before)                 # scan writes nothing
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"merged PR #7 at {self.sha}", out)
        self.assertIn("state: done", self.on_main(f"{INST}/d-work/rows/9.md"))
        self.assertIn("state: done", self.on_main(f"{INST}/d-work/rows/10.md"))
        self.assertIsNone(self.on_main(f"{INST}/d-work/board/9.md"))
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual((rc, out.strip()), (0, "nothing to do"))

    def test_a_moved_head_is_refused_and_told_once(self):
        self.w.write_main(self.files)
        self.w.pr(7, "dyad/zz-pr.txt", "moved\n")                                       # the PR moved after the Y
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"refused, posted a notice to {HOME} (row #9)", out)
        (msg,) = self.inbox(HOME)
        self.assertIn("from: automaton", msg); self.assertIn("row: 9", msg); self.assertIn("automaton: merge of PR #7 refused for row #9", msg)
        self.assertNotRegex(msg, r"\d{4}-\d{2}-\d{2} Y done")                         # names the row, quotes no entry
        rc, out, _ = run(["run"], self.w.seat)
        self.assertIn(f"refused, already told {HOME}", out)
        self.assertEqual(len(self.inbox(HOME)), 1)
        self.assertIn("state: planned", self.on_main(f"{INST}/d-work/rows/9.md"))

    def test_a_planned_row_notifies_each_owner_once(self):
        self.w.write_main({f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                           f"{INST}/d-work/board/12.md": f"holder: {HOME}\nowner: engineer-1537d8fb s1; counsel-0032b4c0 s2\nwriter: h1\n"})
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        for seat in ("engineer-1537d8fb", "counsel-0032b4c0"):
            (msg,) = self.inbox(seat)
            self.assertIn("body: row #12 planned; read plans/12.md", msg); self.assertIn("kind: notice", msg)
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")

    def test_a_push_race_is_retried(self):
        self.w.write_main(self.files)
        calls = []
        real = am.merge_mod.merge_all
        def flaky(repo, cut):
            calls.append(1)
            if len(calls) == 1:
                raise am.Refused("main moved under the push 2 times: nothing landed; run it again")
            return real(repo, cut)
        with unittest.mock.patch.object(am.merge_mod, "merge_all", flaky):
            rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err); self.assertEqual(len(calls), 2)
        self.assertIn(f"merged PR #7 at {self.sha}", out)

    def test_a_row_with_two_prs_is_one_cut(self):
        eight = self.w.pr(8, "dyad/zz-eight.txt", "eight\n", base=self.sha)
        self.files[f"{INST}/d-work/rows/9.md"] = ROW.format(
            id=9, state="planned", disposed=f"2026-11-02 Y plan; 2026-11-02 Y done (accreted #10, merges PR #7 at {self.sha}, PR #8 at {eight})")
        self.w.write_main(self.files)
        before = git(self.w.origin, "rev-parse", "main")
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual(out.splitlines()[0], f"merge PR #7 at {self.sha}, PR #8 at {eight} (row #9)")
        seen = []
        real = am.merge_mod.merge_all
        with unittest.mock.patch.object(am.merge_mod, "merge_all", lambda repo, cut: seen.append(cut) or real(repo, cut)):
            rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(seen, [[(7, self.sha), (8, eight)]])                         # one call, the row's order
        merges = git(self.w.origin, "rev-list", "--merges", "--first-parent", f"{before}..main").split()
        self.assertEqual(len(merges), 2)
        self.assertIn("state: done", self.on_main(f"{INST}/d-work/rows/9.md"))

    def test_misuse(self):
        self.assertEqual(run([], self.w.seat)[0], 2)
        self.assertEqual(run(["go"], self.w.seat)[0], 2)
        self.assertEqual(run(["--help"], self.w.seat)[0], 0)
        self.assertEqual(dyadlib.check_invariants(am), len(am.INVARIANTS) + len(am.TREE_INVARIANTS))


if __name__ == "__main__":
    unittest.main()
