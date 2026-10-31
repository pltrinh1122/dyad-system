"""`dyad merge <pr> --head <sha>` (scripts/merge.py, d-work #532). Every case runs over a scratch world: a seed repo
whose ledger holds one row, a bare `origin` cloned from it, a PR branch pushed to `origin` as `refs/pull/7/head`, and a
seat cloned from that origin whose pre-push hook only logs (and, when asked, lands a racing commit on `main` first). The
row's operative `Y done` is written onto `origin/main` per case. The cases: a recorded Done-Y merges the PR (`--no-ff`,
the message citing the PR, the row and the entry) and one hook run carries it; no entry, a void entry (a later `Y done`
on another head), a short head, a moved live head, an already-landed head and a conflicting PR each refuse with nothing
pushed; a push race is re-read and re-checked once, then lands; misuse is exit 2; and the rows fence's main path admits
the merge commit the verb makes."""
import contextlib, io, os, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
INST = "agent-corpus"
ROW = "id: 9\ntitle: nine\nopened: 2026-10-30\nstate: planned\ndisposed: {disposed}\nrefs: \n"


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class MergeTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.mod = dyadlib.load_module(PKG / "scripts" / "merge.py", "merge")
        top = SCRATCH.mkdtemp()
        seed, self.origin, self.seat, self.racer, hooks = (top / "seed", top / "origin.git", top / "seat",
                                                           top / "racer", top / "hooks")
        seed.mkdir(); git(seed, "init", "-q", "-b", "main")
        (seed / INST / "d-work" / "rows").mkdir(parents=True)
        (seed / INST / "d-work" / "rows" / "9.md").write_text(ROW.format(disposed="2026-10-30 Y plan"))
        (seed / "dyad").mkdir(); (seed / "dyad" / "a.txt").write_text("a\n")
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "seed")
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        for d in (self.seat, self.racer):
            git(top, "clone", "-q", str(self.origin), str(d))
            for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
                git(d, "config", k, v)
        self.log, self.race = top / "hook.log", top / "race"
        hooks.mkdir()
        (hooks / "pre-push").write_text(
            "#!/bin/sh\n"
            f"{{ cat; echo --; }} >> '{self.log}'\n"
            f"if [ -f '{self.race}' ]; then rm -f '{self.race}'; "
            f"env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git -C '{self.racer}' push -q origin HEAD:main; fi\n"
            "exit 0\n")
        (hooks / "pre-push").chmod(0o755)
        git(self.seat, "config", "core.hooksPath", str(hooks))
        self.sha = self.pr_commit("dyad/b.txt", "b\n")

    def pr_commit(self, rel, text, base="origin/main", pr=7):
        """A PR branch off `base` in the racer clone, pushed to origin as `refs/pull/<pr>/head`; its sha."""
        git(self.racer, "fetch", "-q", "origin")
        git(self.racer, "checkout", "-q", "--detach", base)
        (self.racer / rel).parent.mkdir(parents=True, exist_ok=True); (self.racer / rel).write_text(text)
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", f"pr {rel}")
        sha = git(self.racer, "rev-parse", "HEAD")
        git(self.racer, "push", "-q", "-f", "origin", f"{sha}:refs/pull/{pr}/head")
        git(self.racer, "checkout", "-q", "--detach", "origin/main")
        return sha

    def record(self, disposed):
        """Write row 9's `disposed` onto origin/main, as the ledger commit recording a Y does."""
        git(self.racer, "fetch", "-q", "origin"); git(self.racer, "checkout", "-q", "--detach", "origin/main")
        (self.racer / INST / "d-work" / "rows" / "9.md").write_text(ROW.format(disposed=disposed))
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", "ledger: #9")
        git(self.racer, "push", "-q", "origin", "HEAD:main")

    def done(self, sha=None, pr=7):
        return f"2026-10-30 Y plan; 2026-10-31 Y done (merges PR #{pr} at {sha or self.sha})"

    def run_merge(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.mod.main(list(argv), self.seat)
        return rc, out.getvalue(), err.getvalue()

    def main_at_origin(self):
        return git(self.origin, "rev-parse", "main")

    def hook_runs(self):
        return [r for r in self.log.read_text().split("--\n") if r.strip()] if self.log.exists() else []

    def test_a_recorded_done_y_merges_the_pr(self):
        self.record(self.done())
        before = self.main_at_origin()
        rc, out, err = self.run_merge("7", "--head", self.sha)
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-list", "--parents", "-n", "1", head).split()[1:], [before, self.sha])
        msg = git(self.origin, "log", "-1", "--format=%B", head)
        self.assertTrue(msg.startswith(f"Merge PR #7 at {self.sha}"), msg)
        self.assertIn("row #9", msg); self.assertIn(f"merges PR #7 at {self.sha}", msg)
        self.assertNotIn("d-work #", msg)                      # a claim the plan gate would read; the merge claims none
        self.assertIn(f"merged PR #7 at {self.sha} onto main {before[:12]} as {head}: authorized by row #9", out)
        self.assertEqual(len(self.hook_runs()), 1)            # one push, through the gate
        self.assertEqual(git(self.seat, "status", "--porcelain"), "")   # the caller's checkout is never touched

    def refused(self, *argv, says):
        before = self.main_at_origin()
        rc, out, err = self.run_merge(*argv)
        self.assertEqual(rc, 1, out + err); self.assertEqual(out, "")
        self.assertIn("refused: ", err); self.assertIn(says, err)
        self.assertEqual(self.main_at_origin(), before); self.assertEqual(self.hook_runs(), [])

    def test_no_entry_refuses(self):
        self.refused("7", "--head", self.sha, says="no operative Y done on origin/main names PR #7")

    def test_a_void_entry_refuses(self):
        other = self.pr_commit("dyad/c.txt", "c\n", pr=8)
        self.record(self.done() + f"; 2026-10-31 Y done (merges PR #7 at {other})")   # a later Y on another head voids it
        self.refused("7", "--head", self.sha, says=f"row #9's operative Y done names PR #7 at {other}, not {self.sha}")

    def test_an_entry_for_another_pr_only_refuses(self):
        self.record(self.done(pr=8))
        self.refused("7", "--head", self.sha, says="no operative Y done on origin/main names PR #7")

    def test_a_short_head_in_the_entry_refuses(self):
        self.record(self.done(sha=self.sha[:12]))
        self.refused("7", "--head", self.sha, says=f"names PR #7 at {self.sha[:12]}, not {self.sha}")

    def test_a_moved_live_head_refuses(self):
        self.record(self.done())
        moved = self.pr_commit("dyad/d.txt", "d\n")            # the PR's head moves after the Y
        self.refused("7", "--head", self.sha, says=f"PR #7's live head is {moved}, not {self.sha}")

    def test_an_already_landed_head_refuses(self):
        self.record(self.done())
        self.assertEqual(self.run_merge("7", "--head", self.sha)[0], 0)
        self.log.unlink()
        self.refused("7", "--head", self.sha, says=f"{self.sha} is already on origin/main: PR #7 has landed")

    def test_a_conflict_refuses(self):
        git(self.racer, "fetch", "-q", "origin"); git(self.racer, "checkout", "-q", "--detach", "origin/main")
        (self.racer / "dyad" / "b.txt").write_text("main's b\n")
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", "main b")
        git(self.racer, "push", "-q", "origin", "HEAD:main")
        self.record(self.done())
        self.refused("7", "--head", self.sha, says="does not merge cleanly onto origin/main")

    def test_a_push_race_is_reread_and_rechecked_once(self):
        self.record(self.done())
        git(self.racer, "checkout", "-q", "--detach", "origin/main")
        (self.racer / "dyad" / "z.txt").write_text("z\n")
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", "racing")
        raced = git(self.racer, "rev-parse", "HEAD")
        self.race.write_text("1")                                # the first push's hook lands `raced` on main first
        rc, out, err = self.run_merge("7", "--head", self.sha)
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-list", "--parents", "-n", "1", head).split()[1:], [raced, self.sha])
        self.assertEqual(len(self.hook_runs()), 2)

    def test_misuse_is_exit_2(self):
        for argv in ([], ["7"], ["7", "--head", self.sha[:12]], ["x", "--head", self.sha], ["7", "--sha", self.sha]):
            rc, out, err = self.run_merge(*argv)
            self.assertEqual((rc, out), (2, ""), argv); self.assertIn(self.mod.USAGE, err)
        rc, out, _ = self.run_merge("--help")
        self.assertEqual(rc, 0); self.assertIn("dyad merge <pr> --head <sha>", out)

    def test_the_rows_fence_admits_the_merge_commit(self):
        """The fence's main path (`rows.check_range`) walks first-parent non-merge commits only: the merge commit the
        verb pushes is skipped, and the PR's own commit, reached through the second parent, is never visited."""
        self.record(self.done())
        before = self.main_at_origin()
        self.assertEqual(self.run_merge("7", "--head", self.sha)[0], 0)
        git(self.seat, "fetch", "-q", "origin")
        rg = dyadlib.load_guard("agent", "rows")
        self.assertEqual(rg.check_range(before, "origin/main", cwd=self.seat), [])
        self.assertEqual(git(self.seat, "rev-list", "--first-parent", "--no-merges", f"{before}..origin/main"), "")


if __name__ == "__main__":
    unittest.main()
