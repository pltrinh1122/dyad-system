"""`dyad steps` (scripts/steps.py, d-work #556): the d-work run-book's harvested steps, over scratch worlds.

Two worlds:
- A plain one: a seed repo, a bare origin, a racer clone that pushes PR heads as `refs/pull/<n>/head`, and a seat
  clone.
- An installed one: a real scratch install (`livetest.ScratchInstalls`), so `dwork batch --land` runs a real runner
  whose hook only logs.

The cases:
- verify-prs: two stacked PRs report their heads, files and stacking, then merge in order; a conflicting PR and a
  missing head refuse.
- The Done entry is composed from live heads and the accreted rows. The accreted clause is parsed back, in both
  spellings.
- close-landed:
  - refuses while a named head is off main;
  - once it lands, it sets the row done, closes its accreted row under `--mandate` and drops its board entry, all
    landed;
  - a second run refuses as already closed.
- sync-mirror fast-forwards, refuses a diverged branch, and says `already` when equal.
- Misuse is exit 2."""
import contextlib, io, os, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
INST = "agent-corpus"
st = dyadlib.load_module(PKG / "scripts" / "steps.py", "steps")


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class World:
    def __init__(self, seed: Path):
        top = seed.parent
        self.origin, self.seat, self.racer, hooks = top / "origin.git", top / "seat", top / "racer", top / "hooks"
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        hooks.mkdir(exist_ok=True); (hooks / "pre-push").write_text("#!/bin/sh\ncat >/dev/null\nexit 0\n"); (hooks / "pre-push").chmod(0o755)
        for d in (self.seat, self.racer):
            git(top, "clone", "-q", str(self.origin), str(d))
            for k, v in (("user.email", "t@example.com"), ("user.name", "t"), ("core.hooksPath", str(hooks))):
                git(d, "config", k, v)

    def pr(self, n, rel, text, base="origin/main"):
        git(self.racer, "fetch", "-q", "origin"); git(self.racer, "checkout", "-q", "--detach", base)
        (self.racer / rel).parent.mkdir(parents=True, exist_ok=True); (self.racer / rel).write_text(text)
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", f"pr {n}")
        sha = git(self.racer, "rev-parse", "HEAD")
        git(self.racer, "push", "-q", "-f", "origin", f"{sha}:refs/pull/{n}/head")
        return sha

    def land_on_main(self, sha):
        git(self.racer, "fetch", "-q", "origin"); git(self.racer, "checkout", "-q", "--detach", "origin/main")
        git(self.racer, *livetest.IDENTITY, "merge", "-q", "--no-ff", "-m", "merge", sha)
        git(self.racer, "push", "-q", "origin", "HEAD:main")

    def write_main(self, files, msg="ledger"):
        git(self.racer, "fetch", "-q", "origin"); git(self.racer, "checkout", "-q", "--detach", "origin/main")
        for rel, text in files.items():
            (self.racer / rel).parent.mkdir(parents=True, exist_ok=True); (self.racer / rel).write_text(text)
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", msg)
        git(self.racer, "push", "-q", "origin", "HEAD:main")


def run(argv, repo, **envs):
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, **envs}), \
         contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = st.main(argv, repo)
    return rc, out.getvalue(), err.getvalue()


class PlainTests(unittest.TestCase):
    def setUp(self):
        top = SCRATCH.mkdtemp(); seed = top / "seed"; seed.mkdir()
        git(seed, "init", "-q", "-b", "main")
        (seed / "dyad").mkdir(); (seed / "dyad" / "a.txt").write_text("a\n")
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "seed")
        self.w = World(seed)

    def test_verify_prs_reports_stacking_and_merges_in_order(self):
        a = self.w.pr(7, "dyad/b.txt", "b\n")
        b = self.w.pr(8, "dyad/c.txt", "c\n", base=a)
        rc, out, err = run(["verify-prs"], self.w.seat, PRS="7 8")
        self.assertEqual(rc, 0, err)
        self.assertIn(f"PR #7 at {a}: 1 file(s)", out)
        self.assertIn(f"PR #8 at {b}: 2 file(s)", out); self.assertIn("stacked on PR #7", out)
        self.assertIn("merge-tree: PR #7 merges cleanly in order", out); self.assertIn("merge-tree: PR #8 merges cleanly in order", out)

    def test_verify_prs_refuses_a_conflict_and_a_missing_head(self):
        self.w.pr(7, "dyad/a.txt", "pr 7's a\n")
        self.w.pr(8, "dyad/a.txt", "pr 8's a\n")
        rc, _, err = run(["verify-prs"], self.w.seat, PRS="7 8")
        self.assertEqual(rc, 1); self.assertIn("merge-tree: PR #8 conflicts onto", err)
        rc, _, err = run(["verify-prs"], self.w.seat, PRS="7 99")
        self.assertEqual(rc, 1); self.assertIn("PR #99: no live head", err)

    def test_done_entry_and_accreted_clause(self):
        a = self.w.pr(7, "dyad/b.txt", "b\n")
        self.assertEqual(st.done_entry(self.w.seat, [7], [547, 551]), f"Y done (accreted #547, #551, merges PR #7 at {a})")
        self.assertEqual(st.done_entry(self.w.seat, [], []), "Y done")
        self.assertEqual(st.mandate_rows(f"2026-11-02 Y done (accreted #547, #551, merges PR #7 at {a})"), [547, 551])
        self.assertEqual(st.mandate_rows("2026-11-02 Y done (mandate rows #304, #314, merges PR #588 at abc)"), [304, 314])
        self.assertEqual(st.mandate_rows("2026-11-02 Y done (merges PR #7 at abc)"), [])

    def test_sync_mirror(self):
        rc, out, err = run(["sync-mirror"], self.w.seat, MIRROR="claude/x")
        self.assertEqual(rc, 0, err); self.assertIn("claude/x: absent ->", out)
        main = git(self.w.origin, "rev-parse", "main")
        self.assertEqual(git(self.w.origin, "rev-parse", "claude/x"), main)
        rc, _, err = run(["sync-mirror"], self.w.seat, MIRROR="claude/x")
        self.assertEqual(rc, 1); self.assertIn("already: claude/x is origin/main", err)
        self.w.write_main({"dyad/d.txt": "d\n"})
        rc, out, err = run(["sync-mirror"], self.w.seat, MIRROR="claude/x")
        self.assertEqual(rc, 0, err); self.assertIn(f"(MIRROR_WAS={main})", out)
        git(self.w.racer, "checkout", "-q", "--detach", main)
        (self.w.racer / "dyad" / "e.txt").write_text("e\n"); git(self.w.racer, "add", "-A")
        git(self.w.racer, *livetest.IDENTITY, "commit", "-qm", "work main lacks")
        git(self.w.racer, "push", "-q", "-f", "origin", "HEAD:refs/heads/claude/x")
        rc, _, err = run(["sync-mirror"], self.w.seat, MIRROR="claude/x")
        self.assertEqual(rc, 1); self.assertIn("holds work main lacks; never forced", err)

    def test_misuse(self):
        for argv in (["bogus"], ["verify-prs", "--land"], ["sync-mirror", "--x"]):
            self.assertEqual(run(argv, self.w.seat)[0], 2, argv)
        self.assertEqual(run([], self.w.seat)[0], 2)
        rc, _, err = run(["verify-prs"], self.w.seat)
        self.assertEqual(rc, 1); self.assertIn("PRS is not set", err)
        rc, _, err = run(["close-landed"], self.w.seat, DWORK="x")
        self.assertEqual(rc, 1); self.assertIn("DWORK must be a row id", err)


ROW = "id: {id}\ntitle: row {id}\nopened: 2026-11-02\nstate: {state}\ndisposed: {disposed}\nrefs: \n"
REC = ("# Provenance #{id}\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n"
       "## 2 disposition 2026-11-02 Y done\n\n```\nY\n```\n\n")


class InstalledTests(unittest.TestCase):
    """close-landed over a real install: the batch and the board drop land through the installed runner."""
    def setUp(self):
        seed = SCRATCH.copy(False)
        top = SCRATCH.mkdtemp(); moved = top / "seed"; seed.rename(moved)
        git(moved, "branch", "-M", "main")                   # an install's first branch is git's default; the world's is main
        self.w = World(moved)
        self.sha = self.w.pr(7, "dyad/zz-pr.txt", "pr\n")
        rows, prov = f"{INST}/d-work/rows", f"{INST}/d-work/provenance"
        self.w.write_main({
            f"{rows}/9.md": ROW.format(id=9, state="planned", disposed=f"2026-11-02 Y plan; 2026-11-02 Y done (accreted #10, merges PR #7 at {self.sha})"),
            f"{prov}/9.md": REC.format(id=9),
            f"{rows}/10.md": ROW.format(id=10, state="open", disposed="2026-11-02 Y plan (mandate #9)"),
            f"{prov}/10.md": "# Provenance #10\n\n## 1 disposition 2026-11-02 mandate #9, 2026-11-02\n\n```\nY\n```\n\n",
            f"{INST}/d-work/board/9.md": "holder: program-aaaaaaaa\nwaiting-on: operator\nwriter: h1\n"})

    def test_close_landed_waits_for_the_merge_then_closes_all(self):
        rc, _, err = run(["close-landed", "--land"], self.w.seat, DWORK="9")
        self.assertEqual(rc, 1); self.assertIn("not yet on origin/main", err)
        self.w.land_on_main(self.sha)
        rc, out, err = run(["close-landed", "--land"], self.w.seat, DWORK="9", DYAD_SESSION="program-aaaaaaaa")
        self.assertEqual(rc, 0, out + err)
        main = lambda p: subprocess.run(["git", "show", f"main:{p}"], cwd=self.w.origin, capture_output=True, text=True)
        self.assertIn("state: done", main(f"{INST}/d-work/rows/9.md").stdout)
        r10 = main(f"{INST}/d-work/rows/10.md").stdout
        self.assertIn("state: done", r10); self.assertIn("Y done (mandate #9,", r10)
        self.assertNotEqual(main(f"{INST}/d-work/board/9.md").returncode, 0)             # the board entry is dropped
        rc, _, err = run(["close-landed", "--land"], self.w.seat, DWORK="9")
        self.assertEqual(rc, 1); self.assertIn("already closed: row #9 is done", err)


class DoneRecordTests(unittest.TestCase):
    """done-record --land over a real install: the entry names the PR's live head, the trace rides the batch, and a
    second run refuses as already recorded."""
    def setUp(self):
        seed = SCRATCH.copy(False)
        top = SCRATCH.mkdtemp(); moved = top / "seed"; seed.rename(moved)
        git(moved, "branch", "-M", "main")
        self.w = World(moved)
        self.sha = self.w.pr(7, "dyad/zz-pr.txt", "pr\n")
        self.w.write_main({f"{INST}/d-work/rows/11.md": ROW.format(id=11, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/11.md": "# Provenance #11\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n"})
        git(self.w.seat, "pull", "-q", "origin", "main")
        self.said = top / "said.txt"; self.said.write_text("Y\n")

    def test_done_record_lands_the_entry_and_the_trace_once(self):
        rc, out, err = run(["done-record", "--land"], self.w.seat, DWORK="11", PRS="7", SAID=str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"row #11: Y done (merges PR #7 at {self.sha})", out)
        main = lambda p: subprocess.run(["git", "show", f"main:{p}"], cwd=self.w.origin, capture_output=True, text=True)
        row = main(f"{INST}/d-work/rows/11.md").stdout
        self.assertIn(f"Y done (merges PR #7 at {self.sha})", row); self.assertIn("state: planned", row)   # the state waits for the merge
        self.assertEqual(main(f"{INST}/d-work/traces/11.md").returncode, 0)
        self.assertNotIn("\n- preview:", main(f"{INST}/d-work/traces/11.md").stdout)   # #592 R-b: through the Done words
        self.assertIn("Y done", main(f"{INST}/d-work/provenance/11.md").stdout)
        rc, _, err = run(["done-record", "--land"], self.w.seat, DWORK="11", PRS="7", SAID=str(self.said))
        self.assertEqual(rc, 1); self.assertIn("already recorded", err)


if __name__ == "__main__":
    unittest.main()
