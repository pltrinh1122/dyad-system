"""Concurrent-session simulation for the d-work row store (Rule-16; ledger #109).

Two sessions, A and B, are two clones of one bare `origin`; d-work state is written with
`dyadlib.format_row_file`, read back with `parse_row_file`, and every hand resolution is judged
by `rows.check_range` (the main fence, `guards/agent/rows.py`) exactly as the pre-push guard does.  What the scenarios prove:

1. id allocation — both sessions compute max+1 from the same `origin/main` and get the same id.
   Git rejects the second push (non-fast-forward) and, after fetch + rebase, reports an add/add
   conflict on `rows/<id>.md`.  Collision is detected by git, never silently merged, and never
   by `package.py dwork new` (Rule-16: "the push rejects" — verified, not prevented).
2. same id, two branches — A writes `state: planned`, B (stale) writes `state: done`.  Second
   push rejected; rebase yields a content conflict on the `state:` line.  Three hand
   resolutions through the fence: keep `done` -> passes (state is free); change `title:` ->
   fails "changes id or title"; delete the row -> fails "deletes row file".
   2b (d-work #112, sweep-6 gap T5): a regression `done -> open` resolved by hand is refused by
   the fence ("state regresses") and `check_range` catches the regressing commit even after it
   is pushed — the pre-push hook would have stopped it; `dyadlib.TRANSITIONS` is the table.
3. disjoint files, one id — planner writes `plans/<id>.md`, executor edits `rows/<id>.md`:
   second push rejected, fetch + rebase merges clean, both sides fast-forward.
4. two ids — `rows/a.md` and `rows/b.md`: as 3, no conflict.

Scratch repos versus hosting (falsification sweep-6, attack 1): non-fast-forward rejection and
conflict detection are git's semantics, identical on a bare origin and a hosted one; only
required-status-checks are hosting, and no scenario relies on them.  Kernel only: git, python.
"""
import subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib
m = dyadlib.load_guard("agent", "rows")   # the main fence (Rule-3), guards/agent/rows.py since #151

ROWS = "agent-corpus/d-work/rows"
PLANS = "agent-corpus/d-work/plans"


def sh(*a, cwd):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout


def fails(*a, cwd):
    """Run a git command expected to fail; return its stderr."""
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True)
    if r.returncode == 0:
        raise AssertionError(f"expected failure: {' '.join(a)}")
    return r.stderr


class Session:
    """One clone of origin, identity set (Rule-16: a session)."""
    def __init__(self, origin: Path, name: str):
        self.d = Path(tempfile.mkdtemp(prefix=f"session-{name}-"))
        sh("git", "clone", "-q", str(origin), str(self.d), cwd=origin)
        sh("git", "config", "user.email", "t@t", cwd=self.d)
        sh("git", "config", "user.name", "t", cwd=self.d)

    def write_row(self, r: dyadlib.Row):
        p = self.d / ROWS / f"{r.id}.md"; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(dyadlib.format_row_file(r))

    def read_row(self, rid: int) -> dyadlib.Row:
        return dyadlib.parse_row_file((self.d / ROWS / f"{rid}.md").read_text())

    def next_id(self) -> int:
        """What `package.py dwork new` computes: max(origin/main, local)+1."""
        sh("git", "fetch", "-q", "origin", "main", cwd=self.d)
        ids = {r.id for r in dyadlib.read_rows(self.d)} | {r.id for r in dyadlib.read_rows(self.d, at="origin/main")}
        return max(ids, default=0) + 1

    def commit(self, msg="c"):
        sh("git", "add", "-A", cwd=self.d); sh("git", "commit", "-q", "-m", msg, cwd=self.d)
        return self.head()

    def head(self):
        return sh("git", "rev-parse", "HEAD", cwd=self.d).strip()

    def push(self):
        sh("git", "push", "-q", "origin", "main", cwd=self.d)

    def push_rejected(self) -> str:
        err = fails("git", "push", "-q", "origin", "main", cwd=self.d)
        assert "rejected" in err and ("fetch first" in err or "non-fast-forward" in err), err
        return err

    def fetch_rebase(self) -> subprocess.CompletedProcess:
        sh("git", "fetch", "-q", "origin", "main", cwd=self.d)
        return subprocess.run(["git", "rebase", "origin/main"], cwd=self.d, capture_output=True, text=True)

    def unmerged(self) -> list[str]:
        return sh("git", "diff", "--name-only", "--diff-filter=U", cwd=self.d).split()

    def status(self) -> str:
        return sh("git", "status", "--porcelain", cwd=self.d)


class ConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.origin = Path(tempfile.mkdtemp(prefix="origin-"))
        sh("git", "init", "-q", "--bare", "-b", "main", str(self.origin), cwd=self.origin)
        seed = Session(self.origin, "seed")
        seed.write_row(dyadlib.Row(1, "one", "2026-09-13", "open", "2026-09-13 Y plan", ""))
        seed.commit("root"); seed.push()
        self.A = Session(self.origin, "A"); self.B = Session(self.origin, "B")

    def origin_main(self) -> str:
        return sh("git", "rev-parse", "main", cwd=self.origin).strip()

    # -- scenario 1: id allocation ------------------------------------------------------
    def test_1_same_id_rejected_then_add_add_conflict(self):
        a_id, b_id = self.A.next_id(), self.B.next_id()
        self.assertEqual(a_id, b_id, "both sessions allocate max+1 from the same origin/main")
        self.A.write_row(dyadlib.Row(a_id, "A's work", "d", "open", "", "")); self.A.commit(); self.A.push()
        self.B.write_row(dyadlib.Row(b_id, "B's work", "d", "open", "", "")); self.B.commit()
        self.B.push_rejected()
        r = self.B.fetch_rebase()
        self.assertNotEqual(r.returncode, 0, "rebase must stop on the collision, never merge silently")
        self.assertIn("AA", self.B.status(), "add/add conflict on the same new row file")
        self.assertEqual(self.B.unmerged(), [f"{ROWS}/{a_id}.md"])
        sh("git", "rebase", "--abort", cwd=self.B.d)

    # -- scenario 2: same id, two branches ----------------------------------------------
    def conflict_on_state(self):
        """A: planned, pushed. B (stale): done, rejected, rebase conflict. Returns (before, stale)."""
        self.A.write_row(dyadlib.Row(1, "one", "2026-09-13", "planned", "2026-09-13 Y plan", "")); self.A.commit(); self.A.push()
        before = self.origin_main()
        self.B.write_row(dyadlib.Row(1, "one", "2026-09-13", "done", "2026-09-13 Y plan; 2026-09-13 Y done", ""))
        stale = self.B.commit()
        self.B.push_rejected()
        r = self.B.fetch_rebase()
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.B.unmerged(), [f"{ROWS}/1.md"])
        self.assertIn("UU", self.B.status())
        text = (self.B.d / ROWS / "1.md").read_text()
        self.assertIn("<<<<<<<", text); self.assertIn("state: planned", text); self.assertIn("state: done", text)
        return before, stale

    def resolve(self, before, stale, resolution) -> list[str]:
        """Apply a hand resolution to the live conflict, continue the rebase, run the fence, then
        rewind B to its stale commit and re-raise the same conflict for the next resolution."""
        resolution()
        sh("git", "-c", "core.editor=true", "rebase", "--continue", cwd=self.B.d)
        out = m.check_range(before, self.B.head(), cwd=self.B.d)
        sh("git", "reset", "-q", "--hard", stale, cwd=self.B.d)
        self.assertNotEqual(self.B.fetch_rebase().returncode, 0)
        return out

    def test_2_same_id_conflict_and_three_resolutions(self):
        before, stale = self.conflict_on_state()
        row = self.B.d / ROWS / "1.md"
        keep_done = dyadlib.Row(1, "one", "2026-09-13", "done", "2026-09-13 Y plan; 2026-09-13 Y done", "")

        def keep_b():
            row.write_text(dyadlib.format_row_file(keep_done)); sh("git", "add", str(row), cwd=self.B.d)
        self.assertEqual(self.resolve(before, stale, keep_b), [], "state is free: planned -> done passes")
        self.assertEqual(self.B.read_row(1).state, "done")

        def retitle():
            row.write_text(dyadlib.format_row_file(dyadlib.Row(1, "renamed", "2026-09-13", "done", "", "")))
            sh("git", "add", str(row), cwd=self.B.d)
        out = self.resolve(before, stale, retitle)
        self.assertEqual(len(out), 1); self.assertIn("changes id or title", out[0])

        def delete():
            sh("git", "rm", "-q", str(row), cwd=self.B.d)
        out = self.resolve(before, stale, delete)
        self.assertEqual(len(out), 1); self.assertIn("deletes row file", out[0])
        sh("git", "rebase", "--abort", cwd=self.B.d)

    def test_2b_state_regression_refused(self):
        # d-work #112: Rule-16 "state never regresses" — the fence refuses done -> open.
        self.A.write_row(dyadlib.Row(1, "one", "2026-09-13", "done", "Y plan; Y done", "")); self.A.commit(); self.A.push()
        before = self.origin_main()
        self.B.write_row(dyadlib.Row(1, "one", "2026-09-13", "open", "Y plan", "")); self.B.commit()
        self.B.push_rejected()
        self.assertNotEqual(self.B.fetch_rebase().returncode, 0, "same line, still a conflict")
        row = self.B.d / ROWS / "1.md"
        row.write_text(dyadlib.format_row_file(dyadlib.Row(1, "one", "2026-09-13", "open", "Y plan", "")))
        sh("git", "add", str(row), cwd=self.B.d)
        sh("git", "-c", "core.editor=true", "rebase", "--continue", cwd=self.B.d)
        out = m.check_range(before, self.B.head(), cwd=self.B.d)
        self.assertEqual(len(out), 1, out); self.assertIn("state regresses done\u2192open", out[0])
        # The pre-push hook (`package.py check --guards`) runs this same check and would refuse the
        # push. Push anyway (bare git has no hook) and show the regressing commit is still caught
        # on the pushed range: origin carries it only because the guard was bypassed.
        self.B.push()
        self.assertEqual(dyadlib.read_rows(self.B.d, at="origin/main")[0].state, "open")
        out = m.check_range(before, self.origin_main(), cwd=self.B.d)
        self.assertEqual(len(out), 1, out); self.assertIn("state regresses done\u2192open", out[0])

    # -- scenario 3: disjoint files, one id --------------------------------------------
    def test_3_plan_file_and_row_file_merge_clean(self):
        plan = self.A.d / PLANS / "1.md"; plan.parent.mkdir(parents=True)
        plan.write_text("# Plan #1\nintent as read: one\n"); self.A.commit("plans: #1"); self.A.push()
        self.B.write_row(dyadlib.Row(1, "one", "2026-09-13", "planned", "2026-09-13 Y plan", "")); self.B.commit("ledger: #1 planned")
        self.B.push_rejected()
        r = self.B.fetch_rebase()
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(self.B.unmerged(), [])
        self.B.push()
        sh("git", "pull", "-q", "--ff-only", "origin", "main", cwd=self.A.d)
        self.assertEqual(self.A.head(), self.B.head())
        self.assertEqual(self.A.read_row(1).state, "planned"); self.assertTrue((self.B.d / PLANS / "1.md").exists())
        self.assertEqual(m.check_range(sh("git", "rev-parse", "HEAD~2", cwd=self.A.d).strip(), self.A.head(), cwd=self.A.d), [])

    # -- scenario 4: two ids ----------------------------------------------------------
    def test_4_two_ids_merge_clean(self):
        self.A.write_row(dyadlib.Row(2, "two", "d", "open", "", "")); self.A.commit("ledger: #2 open"); self.A.push()
        self.B.write_row(dyadlib.Row(1, "one", "2026-09-13", "done", "Y plan; Y done", "")); self.B.commit("ledger: #1 done")
        self.B.push_rejected()
        r = self.B.fetch_rebase()
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(self.B.unmerged(), [])
        self.B.push()
        sh("git", "pull", "-q", "--ff-only", "origin", "main", cwd=self.A.d)
        rows = {x.id: x.state for x in dyadlib.read_rows(self.A.d)}
        self.assertEqual(rows, {1: "done", 2: "open"})
        self.assertEqual(m.check_range(sh("git", "rev-parse", "HEAD~2", cwd=self.A.d).strip(), self.A.head(), cwd=self.A.d), [])


if __name__ == "__main__":
    unittest.main()
