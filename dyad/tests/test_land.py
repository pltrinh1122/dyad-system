"""`dyad dwork … --land` and `dyad dwork land` (scripts/land.py; d-work #447, child C1 of plan #443). Every case runs over
a scratch world: a bare `origin`, a seed carrying a real core install and one row, and a seat cloned from it whose
`core.hooksPath` is a scratch pre-push hook that logs each run's stdin — so nothing reaches the real origin, the
real guards never run, and a run of the hook is countable. The cases: a record lands (one commit, ledger-only, no
`d-work #`, the seat fast-forwarded); a racing commit is rebuilt and a `new` re-allocated; an entry already landed is
refused; a path outside `<instance>/d-work/` is refused; `main` and the mirror go in one push, one hook run; an
ignored `__pycache__` reaches neither the worktree nor survives in it."""
import contextlib, importlib.util, io, os, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
INST = "agent-corpus"
ROW = "id: {id}\ntitle: {title}\nopened: 2026-10-01\nstate: open\ndisposed: \nrefs: \n"
RECORD = "# Provenance #{id}\n\n## 1 prompt 2026-10-01\n\n```\n{words}\n```\n"


def load_package():
    spec = importlib.util.spec_from_file_location("package", PKG / "scripts" / "package.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod); return mod


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


def add_row(d, rid, title, words):
    s = Path(d) / INST / "d-work"
    (s / "rows").mkdir(parents=True, exist_ok=True); (s / "provenance").mkdir(parents=True, exist_ok=True)
    (s / "rows" / f"{rid}.md").write_text(ROW.format(id=rid, title=title))
    (s / "provenance" / f"{rid}.md").write_text(RECORD.format(id=rid, words=words))


class LandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = load_package()

    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        os.environ.pop("DYAD_SESSION", None)
        old = self.pkg.REPO; self.addCleanup(setattr, self.pkg, "REPO", old)
        seed = SCRATCH.copy(False)
        git(seed, "branch", "-M", "main")
        add_row(seed, 1, "one", "open one")
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "ledger: #1 open")
        top = SCRATCH.mkdtemp()
        self.origin, self.seat, self.racer, hooks = top / "origin.git", top / "seat", top / "racer", top / "hooks"
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        git(top, "clone", "-q", str(self.origin), str(self.seat))
        for k, v in (("user.email", "t@example.com"), ("user.name", "t"), ("core.hooksPath", str(hooks))):
            git(self.seat, "config", k, v)
        self.log, self.race = top / "hook.log", top / "race"
        hooks.mkdir()
        (hooks / "pre-push").write_text(
            "#!/bin/sh\n"
            f"{{ cat; echo --; }} >> '{self.log}'\n"
            f"if [ -f '{self.race}' ]; then rm -f '{self.race}'; "
            f"env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git -C '{self.racer}' push -q origin HEAD:main; fi\n"
            "exit 0\n")
        (hooks / "pre-push").chmod(0o755)
        self.pkg.REPO = self.seat
        self.wt = self.seat / ".git" / "dyad-land"

    def dwork(self, *a):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = self.pkg.cmd_dwork(list(a))
        return rc, o.getvalue(), e.getvalue()

    def main_at_origin(self):
        return git(self.origin, "rev-parse", "main")

    def files_of(self, rev):
        return sorted(git(self.origin, "show", "--name-only", "--format=", rev).split())

    def hook_runs(self):
        return [r for r in self.log.read_text().split("--\n") if r.strip()] if self.log.exists() else []

    def test_a_record_lands(self):
        before = self.main_at_origin()
        rc, out, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-parse", "main~1"), before, "one commit")
        self.assertIn(f"landed {head} on main", out)
        self.assertEqual(self.files_of(head), [f"{INST}/d-work/provenance/1.md", f"{INST}/d-work/rows/1.md"])
        msg = git(self.origin, "log", "-1", "--format=%B", "main")
        self.assertTrue(msg.startswith("ledger: #1 planned (Y plan)"), msg); self.assertNotIn("d-work #", msg)
        self.assertIn("state: planned", git(self.origin, "show", f"main:{INST}/d-work/rows/1.md"))
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), head, "the seat on a clean main is fast-forwarded")
        self.assertEqual(len(self.hook_runs()), 1)

    def test_a_racing_commit_is_rebuilt_and_new_reallocated(self):
        git(self.seat.parent, "clone", "-q", str(self.origin), str(self.racer))
        add_row(self.racer, 2, "racer", "open racer")
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", "ledger: #2 open")
        self.race.write_text("")
        rc, out, err = self.dwork("new", "mine", "--prompt", "open mine", "--land")
        self.assertEqual(rc, 0, err)
        self.assertIn("main moved", err)
        self.assertEqual(len(self.hook_runs()), 2, "the first push raced, the rebuild pushed")
        rows = [n for n in git(self.origin, "ls-tree", "--name-only", f"main:{INST}/d-work/rows").split() if n[0].isdigit()]
        self.assertEqual(rows, ["1.md", "2.md", "3.md"])
        self.assertIn("title: racer", git(self.origin, "show", f"main:{INST}/d-work/rows/2.md"))
        self.assertIn("title: mine", git(self.origin, "show", f"main:{INST}/d-work/rows/3.md"))
        self.assertEqual(out.splitlines()[0], "3")
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", "main").startswith("ledger: #3 open: mine"))

    def test_an_already_landed_entry_is_refused(self):
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        rc, _, err = self.dwork("new", "two", "--prompt", "open two", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        rc, _, err = self.dwork("new", "two", "--prompt", "open two", "--land")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        self.assertEqual(self.main_at_origin(), head, "nothing pushed")

    def test_land_paths_and_a_path_outside_the_store_is_refused(self):
        before = self.main_at_origin()
        (self.seat / "README.md").write_text("not ledger\n")
        rc, _, err = self.dwork("land", str(self.seat / "README.md"), "-m", "ledger: x")
        self.assertEqual(rc, 1); self.assertIn("outside", err)
        self.assertEqual(self.main_at_origin(), before)
        plan = self.seat / INST / "d-work" / "plans" / "1.md"
        plan.parent.mkdir(parents=True); plan.write_text("# Plan #1\n")
        rc, _, err = self.dwork("land", str(plan), "-m", "ledger: plan d-work #1")
        self.assertEqual(rc, 1); self.assertIn("claims no d-work", err)
        rc, out, err = self.dwork("land", str(plan), "-m", "ledger: plan #1")
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.files_of("main"), [f"{INST}/d-work/plans/1.md"])
        self.assertIn("has changes", out, "a seat with changes is left as it is")
        rc, _, err = self.dwork("land", str(plan), "-m", "ledger: plan #1")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)

    def test_main_and_the_mirror_go_in_one_push(self):
        git(self.seat, "switch", "-q", "-c", "work")
        here = git(self.seat, "rev-parse", "HEAD")
        rc, out, err = self.dwork("state", "1", "open", "--prompt", "more words", "--land", "--mirror", "work")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-parse", "work"), head)
        runs = self.hook_runs()
        self.assertEqual(len(runs), 1, "one push, one hook run")
        self.assertIn("refs/heads/main", runs[0]); self.assertIn("refs/heads/work", runs[0])
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), here, "a seat off main is never moved")
        self.assertIn("not on main", out)

    def test_an_ignored_pycache_reaches_neither_worktree(self):
        ghost = self.seat / "crafts" / "ghost" / "__pycache__"
        ghost.mkdir(parents=True); (ghost / "x.pyc").write_bytes(b"\0")
        rc, _, err = self.dwork("state", "1", "open", "--prompt", "first", "--land")
        self.assertEqual(rc, 0, err)
        self.assertFalse((self.wt / "crafts" / "ghost").exists())
        stale = self.wt / "crafts" / "ghost" / "__pycache__"
        stale.mkdir(parents=True); (stale / "x.pyc").write_bytes(b"\0")   # left behind in the reused worktree
        rc, _, err = self.dwork("state", "1", "open", "--prompt", "second", "--land")
        self.assertEqual(rc, 0, err)
        self.assertFalse((self.wt / "crafts" / "ghost").exists(), "the reused worktree is cleaned")
        self.assertEqual(list(self.wt.rglob("__pycache__")), [], "the verb ran without writing bytecode")


if __name__ == "__main__":
    unittest.main()
