"""`dyad dwork … --land` and `dyad dwork land` (scripts/land.py; d-work #447, child C1 of plan #443). Every case runs over
a scratch world: a bare `origin`, a seed carrying a real core install and one row, and a seat cloned from it whose
`core.hooksPath` is a scratch pre-push hook that logs each run's stdin — so nothing reaches the real origin, the
real guards never run, and a run of the hook is countable. The cases: a record lands (one commit, ledger-only, no
`d-work #`, the seat fast-forwarded); a racing commit is rebuilt and a `new` re-allocated; an entry already landed is
refused; a path outside `<instance>/d-work/` is refused; `main` and the mirror go in one push, one hook run; an
ignored `__pycache__` reaches neither the worktree nor survives in it. The batch (#459): three lines are one commit and
one hook run; a refused line lands nothing; a line already landed is skipped and the rest lands, a batch of only such
lines is refused; a merge-naming `Y done` and `done` on one row are refused before any push; a racing commit rebuilds
the batch; a line naming -m, --land, --mirror or another verb is refused. The caller-copy fix: a `land` restores an
identical copy and fast-forwards, and leaves a checkout with any other change, or a differing byte, as it is."""
import contextlib, importlib.util, io, os, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest
land_mod = dyadlib.load_module(PKG / "scripts" / "land.py", "land")

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
        self.top = top

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
        rc, out, err = self.dwork("new", "mine", "--prompt", "open mine", "--slug", "mine-row", "--land")
        self.assertEqual(rc, 0, err)
        self.assertIn("main moved", err)
        self.assertEqual(len(self.hook_runs()), 2, "the first push raced, the rebuild pushed")
        rows = [n for n in git(self.origin, "ls-tree", "--name-only", f"main:{INST}/d-work/rows").split() if n[0].isdigit()]
        self.assertEqual(rows, ["1.md", "2.md", "3.md"])
        self.assertIn("title: racer", git(self.origin, "show", f"main:{INST}/d-work/rows/2.md"))
        self.assertIn("title: mine", git(self.origin, "show", f"main:{INST}/d-work/rows/3.md"))
        self.assertEqual(out.splitlines()[0], "3")
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", "main").startswith("ledger: #3 open: mine"))

    def test_a_carried_backlog_row_lands_with_its_subject_and_once(self):
        """#574: `new --backlog --mandate` lands as `#N backlog, carried under mandate #M`, and a re-run is refused."""
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        rc, out, err = self.dwork("new", "a fence", "--backlog", "--mandate", "1", "--slug", "a-fence", "--land")
        self.assertEqual(rc, 0, err)
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", "main").startswith("ledger: #2 backlog, carried under mandate #1: a fence"))
        head = self.main_at_origin()
        rc, _, err = self.dwork("new", "a fence", "--backlog", "--mandate", "1", "--slug", "a-fence", "--land")
        self.assertEqual(rc, 1); self.assertIn("already carried under mandate #1", err)
        self.assertEqual(self.main_at_origin(), head)

    def test_an_already_landed_entry_is_refused(self):
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        rc, _, err = self.dwork("new", "two", "--prompt", "open two", "--slug", "two-row", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        rc, _, err = self.dwork("new", "two", "--prompt", "open two", "--slug", "two-row", "--land")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        self.assertEqual(self.main_at_origin(), head, "nothing pushed")

    def test_a_slug_line_lands_once_the_row_holds_it(self):
        """#622 Decision 2: `state <id> <same state> --slug <s>` is not already landed until the row holds that slug,
        and its subject says so; the same line again is."""
        rc, _, err = self.dwork("state", "1", "open", "--slug", "one-row", "--land")
        self.assertEqual(rc, 0, err)
        self.assertEqual(git(self.origin, "log", "-1", "--format=%s", "main"), "ledger: #1 open (slug one-row)")
        self.assertIn("slug: one-row", git(self.origin, "show", f"main:{INST}/d-work/rows/1.md"))
        head = self.main_at_origin()
        rc, _, err = self.dwork("state", "1", "open", "--slug", "one-row", "--land")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        self.assertEqual(self.main_at_origin(), head)

    # ---- presence (#567): the acts that hand a unit a row touch that unit's own presence file, in the same land
    def seed_origin(self, files: dict):
        """Write `files` (repo-relative) in the seat and put them on origin/main past the hook (setup, not a land)."""
        for rel, text in files.items():
            (self.seat / rel).parent.mkdir(parents=True, exist_ok=True); (self.seat / rel).write_text(text)
        git(self.seat, "add", "-A"); git(self.seat, *livetest.IDENTITY, "commit", "-qm", "ledger: setup")
        git(self.seat, "-c", "core.hooksPath=/dev/null", "push", "-q", "origin", "HEAD:main")
        self.log.unlink(missing_ok=True)

    def presence(self, seat, rev="main"):
        return dyadlib.load_guard("agent", "sessions").parse(git(self.origin, "show", f"{rev}:{INST}/d-work/sessions/{seat}.md"))

    def test_an_owners_plan_y_lands_its_presence_with_the_plans_files_and_drops_a_done_row(self):
        s = f"{INST}/d-work/"
        self.seed_origin({s + "plans/1.md": "# Plan #1\n\nFiles touched: dyad/scripts/x.py, dyad/tests/test_x.py\n",
                          s + "board/1.md": "holder: program-aaaaaaaa\nowner: engineer-bbbbbbbb s1\n",
                          s + "rows/5.md": ROW.format(id=5, title="five").replace("state: open", "state: done"),
                          s + "sessions/engineer-bbbbbbbb.md": "session: engineer-bbbbbbbb\nseen: 2026-10-01T00:00:00+00:00\n"
                                                              "root: /old\nrows: 5\nfiles: dyad/old.py\n"})
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "engineer-bbbbbbbb"}):
            rc, out, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(self.files_of(head), [s + "provenance/1.md", s + "rows/1.md", s + "sessions/engineer-bbbbbbbb.md"])
        self.assertEqual(len(self.hook_runs()), 1, "one commit, one push: the presence rides the record")
        f = self.presence("engineer-bbbbbbbb")
        self.assertEqual(f["rows"], "1", "the claimed row in, the done row #5 out")
        self.assertEqual(f["files"], "dyad/old.py dyad/scripts/x.py dyad/tests/test_x.py")
        self.assertEqual(f["root"], str(self.seat.resolve()), "the caller's checkout, not land's worktree")
        self.assertGreater(f["seen"], "2026-10-01T00:00:00+00:00")
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        self.assertEqual(self.main_at_origin(), head, "an entry already landed carries no presence change either")

    def test_the_homes_plan_y_for_another_units_row_claims_nothing(self):
        s = f"{INST}/d-work/"
        self.seed_origin({s + "board/1.md": "holder: program-aaaaaaaa\nowner: engineer-bbbbbbbb s1\n"})
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-aaaaaaaa"}):
            rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        self.assertIn(s + "sessions/program-aaaaaaaa.md", self.files_of(self.main_at_origin()))
        f = self.presence("program-aaaaaaaa")
        self.assertEqual((f["rows"], f["files"]), ("", ""), "seen refreshed, the row left to its owner")

    def test_a_new_row_with_no_owner_is_claimed_and_a_batch_plan_y_touches_once(self):
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "solo-cccccccc"}):
            rc, out, err = self.dwork("new", "mine", "--prompt", "open mine", "--slug", "mine-row", "--land")
            self.assertEqual(rc, 0, err)
            self.assertEqual(self.presence("solo-cccccccc")["rows"], "2", "no board entry: the flat case, the actor claims")
            rc, _, err = self.batch("state 1 planned -d 'Y plan' --said Y\n")
            self.assertEqual(rc, 0, err)
        self.assertEqual(self.presence("solo-cccccccc")["rows"], "1 2")
        self.assertEqual(len(self.hook_runs()), 2)
        with unittest.mock.patch.dict(os.environ, {}):
            os.environ.pop("DYAD_SESSION", None)
            rc, _, err = self.dwork("state", "2", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("sessions/", " ".join(self.files_of(self.main_at_origin())), "no DYAD_SESSION: no presence, the land still lands")

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

    def test_another_prefix_and_kind_fence_what_lands(self):
        """`prefix` and `kind` (#593): a builder writing outside the prefix is refused under its kind and nothing
        lands; the same builder writing only under it lands; with no prefix the fence is `<instance>/d-work/`."""
        ev = "workstation-corpus/runbooks/events/x.jsonl"
        def build(outside):
            def b(w):
                (w / ev).parent.mkdir(parents=True, exist_ok=True); (w / ev).write_text('{"name": "health"}\n')
                if outside:
                    (w / INST / "d-work" / "rows" / "1.md").write_text(ROW.format(id=1, title="one") + "mode: explicit\n")
                return land_mod.written(w), "events: x", ""
            return b
        before = self.main_at_origin()
        with self.assertRaisesRegex(land_mod.Refused, "would not be events-only"):
            land_mod.land(self.seat, INST, None, build(True), "x", prefix="workstation-corpus/runbooks/events/",
                          kind="events-only")
        self.assertEqual(self.main_at_origin(), before)
        with self.assertRaisesRegex(land_mod.Refused, f"outside {INST}/d-work/: that commit would not be ledger-only"):
            land_mod.land(self.seat, INST, None, build(False), "x")
        self.assertEqual(self.main_at_origin(), before)
        with contextlib.redirect_stdout(io.StringIO()):
            land_mod.land(self.seat, INST, None, build(False), "x", prefix="workstation-corpus/runbooks/events/",
                          kind="events-only")
        self.assertEqual(self.files_of("main"), [ev])

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

    # ---- the batch (#459)
    def batch(self, text, *extra):
        f = self.top / "batch.txt"; f.write_text(text)
        return self.dwork("batch", str(f), "--land", *extra)

    def status(self):
        return git(self.seat, "status", "--porcelain", "--untracked-files=all")

    def second_row(self):
        """Row 2 on origin/main and the seat, pushed past the scratch hook so it counts no run."""
        add_row(self.seat, 2, "two", "open two")
        git(self.seat, "add", "-A"); git(self.seat, "commit", "-qm", "ledger: #2 open")
        git(self.seat, "push", "-q", "--no-verify", "origin", "HEAD:main")

    def test_a_batch_is_one_commit_and_one_hook_run(self):
        self.second_row()
        before = self.main_at_origin()
        presence = self.seat / INST / "d-work" / "sessions" / "s1.md"
        presence.parent.mkdir(parents=True); presence.write_text("session: s1\n")
        t1, t2 = self.write_trace(1), self.write_trace(2)   # #465: under `dwork-trace: always` each Done rides with its trace
        rc, out, err = self.batch("# a close round\n\n"
                                  f"land {t1} {t2}\n"
                                  "state 1 done -d 'Y done' --said Y\n"
                                  "state 2 done -d 'Y done' --said 'Y, both'\n"
                                  f"land {presence}\n")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-parse", "main~1"), before, "one commit")
        self.assertEqual(len(self.hook_runs()), 1, "one push, one hook run")
        s = f"{INST}/d-work/"
        self.assertEqual(self.files_of(head), [s + "provenance/1.md", s + "provenance/2.md", s + "rows/1.md", s + "rows/2.md",
                                               s + "sessions/s1.md", s + "traces/1.md", s + "traces/2.md"])
        msg = git(self.origin, "log", "-1", "--format=%B", "main")
        self.assertEqual(msg, "ledger: batch trace #1, trace #2, #1 done (Y done), #2 done (Y done), presence s1"); self.assertNotIn("d-work #", msg)
        for rid in (1, 2):
            self.assertIn("state: done", git(self.origin, "show", f"main:{s}rows/{rid}.md"))
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), head, "the landed copy restored, the seat fast-forwarded")
        self.assertEqual(self.status(), "")

    def write_trace(self, rid):
        t = self.seat / INST / "d-work" / "traces" / f"{rid}.md"
        t.parent.mkdir(parents=True, exist_ok=True); t.write_text(f"# Trace #{rid}\n")
        return t

    def test_a_done_line_lands_only_with_its_trace_before_it(self):
        """#465: the scratch install's preferences say `dwork-trace: always`, so the worktree's runner refuses a `Y done`
        line whose trace is not in the worktree; a `land traces/<id>.md` line before it puts it there, and the trace
        rides the same commit. The single `--land` form lands only what the verb writes, so it is refused too."""
        self.assertEqual(dyadlib.preference("dwork-trace", self.seat), "always")
        before = self.main_at_origin()
        t = self.write_trace(1)
        rc, out, err = self.batch("state 1 done -d 'Y done' --said Y\n")
        self.assertEqual(rc, 1); self.assertIn("write it first: dyad dwork trace 1 --out", err)
        self.assertIn("line 1 (state 1 done", err); self.assertIn("nothing landed", err)
        rc, _, err = self.dwork("state", "1", "done", "-d", "Y done", "--said", "Y", "--land")
        self.assertEqual(rc, 1); self.assertIn("dyad dwork trace 1 --out", err)
        rc, _, err = self.batch(f"state 1 done -d 'Y done' --said Y\nland {t}\n")   # the trace after the line: too late
        self.assertEqual(rc, 1); self.assertIn("dyad dwork trace 1 --out", err)
        self.assertEqual(self.main_at_origin(), before); self.assertEqual(self.hook_runs(), [])
        rc, out, err = self.batch(f"land {t}\nstate 1 done -d 'Y done' --said Y\n")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-parse", "main~1"), before, "one commit")
        s = f"{INST}/d-work/"
        self.assertEqual(self.files_of(head), [s + "provenance/1.md", s + "rows/1.md", s + "traces/1.md"])
        self.assertEqual(git(self.origin, "log", "-1", "--format=%s", "main"), "ledger: batch trace #1, #1 done (Y done)")
        self.assertEqual(len(self.hook_runs()), 1)

    # ---- #586 E2: board and post lines ride the batch; any refusal lands none of them
    def holder_env(self):
        return unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-aaaaaaaa", "CLAUDE_CODE_SESSION_ID": "h-home"})

    def test_a_record_board_and_relay_are_one_commit_and_print_the_ring(self):
        s = f"{INST}/d-work/"
        with self.holder_env():
            rc, out, err = self.batch("state 1 planned -d 'Y plan' --said Y\n"
                                      "board 1 owner=engineer-bbbbbbbb waiting-on='unit engineer-bbbbbbbb' next='build it'\n"
                                      "post engineer-bbbbbbbb --row 1 --kind relay 'row 1 planned; yours: the code'\n"
                                      "post orchestrate-cccccccc --row 1 --kind notice 'fyi'\n")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        self.assertEqual(git(self.origin, "rev-list", "--count", "main~1..main"), "1"); self.assertEqual(len(self.hook_runs()), 1)
        files = self.files_of(head)
        self.assertIn(s + "board/1.md", files); self.assertIn(s + "rows/1.md", files)
        self.assertEqual(sum(f.startswith(s + "inbox/engineer-bbbbbbbb/") for f in files), 1)
        self.assertEqual(sum(f.startswith(s + "inbox/orchestrate-cccccccc/") for f in files), 1)
        self.assertIn("ring: engineer-bbbbbbbb (a doorbell", out)                     # a notice is not rung
        with self.holder_env():                                                        # a re-run posts nothing twice
            rc, out, err = self.batch("post engineer-bbbbbbbb --row 1 --kind relay 'row 1 planned; yours: the code'\n")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)

    def test_a_batch_relay_to_a_non_owner_keeps_its_owner_on_a_re_run(self):
        """#586 E1 inside a batch, and the review's blocking case: the relay adds its receiver as owner; a re-run of
        the whole batch, its board line included, lands nothing and keeps that owner; --cc rings, --drop lands."""
        s, text = f"{INST}/d-work/", ("board 1 owner=program-aaaaaaaa waiting-on='unit program-aaaaaaaa'\n"
                                     "post engineer-bbbbbbbb --row 1 --kind relay 'go' \n"
                                     "post program-aaaaaaaa --cc orchestrate-cccccccc --row 1 --kind report 'up'\n")
        bd = dyadlib.load_guard("agent", "board")
        with self.holder_env():
            rc, out, err = self.batch(text)
        self.assertEqual(rc, 0, err); self.assertEqual(len(self.hook_runs()), 1)
        owners = lambda: bd.owners(bd.parse(git(self.origin, "show", f"main:{s}board/1.md"))[0])
        self.assertEqual(owners(), ["program-aaaaaaaa", "engineer-bbbbbbbb"])
        self.assertIn("ring: engineer-bbbbbbbb, program-aaaaaaaa, orchestrate-cccccccc", out)
        head = self.main_at_origin()
        with self.holder_env():
            rc, out, err = self.batch(text + "state 1 planned -d 'Y plan' --said Y\n")   # the old lines and one new
        self.assertEqual(rc, 0, err)
        self.assertIn("skipped (already landed): line 1 (board 1", out); self.assertNotIn("ring:", out)   # nothing rung twice
        self.assertEqual(owners(), ["program-aaaaaaaa", "engineer-bbbbbbbb"])
        self.assertEqual(self.files_of(self.main_at_origin()),                        # the new line and its presence (#567)
                         [s + "provenance/1.md", s + "rows/1.md", s + "sessions/program-aaaaaaaa.md"])
        with self.holder_env():
            rc, out, err = self.batch("board 1 --drop\n")
        self.assertEqual(rc, 0, err)
        self.assertNotIn(f"{s}board/1.md", git(self.origin, "ls-tree", "-r", "--name-only", "main", f"{s}board"))

    def test_a_body_file_that_is_no_utf8_is_a_line_refusal(self):
        bad = self.top / "bad.bin"; bad.write_bytes(b"\xff\xfe\x80")
        with self.holder_env():
            rc, _, err = self.batch(f"post engineer-bbbbbbbb --row 1 --kind report --body-file {bad}\n")
        self.assertEqual(rc, 1); self.assertIn("line 1: post:", err); self.assertNotIn("Traceback", err)

    def test_a_refused_disposition_drops_its_board_and_relays(self):
        """Today's #573 slip: a `;` in `-d` refused the record while its relays had already gone out."""
        before = self.main_at_origin()
        with self.holder_env():
            rc, out, err = self.batch("board 1 owner=engineer-bbbbbbbb waiting-on='unit engineer-bbbbbbbb'\n"
                                      "post engineer-bbbbbbbb --row 1 --kind relay 'go'\n"
                                      "state 1 planned -d 'Y B3 (a; b)' --said Y\n")
        self.assertEqual(rc, 1); self.assertIn("line 3", err); self.assertIn("nothing landed", err)
        self.assertEqual(self.main_at_origin(), before); self.assertEqual(self.hook_runs(), [])
        self.assertNotIn("ring:", out)

    def test_a_bad_board_or_post_line_is_refused_before_anything_runs(self):
        before = self.main_at_origin()
        with self.holder_env():
            for text, says in (("board 1 colour=red\n", "unknown key 'colour'"),
                               ("post engineer-bbbbbbbb --row 1 --kind report '2026-11-04 Y plan'\n", "disposition-shaped"),
                               ("post engineer-bbbbbbbb --row 1 --kind order 'x'\n", "usage")):
                rc, _, err = self.batch("state 1 planned -d 'Y plan' --said Y\n" + text)
                self.assertEqual(rc, 1, text); self.assertIn("line 2: ", err); self.assertIn(says, err)
        self.assertEqual(self.main_at_origin(), before); self.assertEqual(self.hook_runs(), [])

    def test_a_refused_line_lands_nothing(self):
        before = self.main_at_origin()
        rc, out, err = self.batch("state 1 planned -d 'Y plan' --said Y\nstate 99 open --prompt 'no such row'\n")
        self.assertEqual(rc, 1)
        self.assertIn("line 2 (state 99 open", err); self.assertIn("nothing landed", err)
        self.assertEqual(self.main_at_origin(), before)
        self.assertEqual(self.hook_runs(), [])

    def test_a_landed_line_is_skipped_and_the_rest_lands(self):
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        before = self.main_at_origin()
        rc, out, err = self.batch("state 1 planned -d 'Y plan' --said Y\nstate 1 open --prompt 'more words'\n")
        self.assertEqual(rc, 0, err)
        self.assertIn("skipped (already landed): line 1 (state 1 planned", out)
        self.assertEqual(git(self.origin, "rev-parse", "main~1"), before)
        self.assertEqual(git(self.origin, "log", "-1", "--format=%s", "main"), "ledger: batch #1 open (prompt received)")
        self.assertIn("state: open", git(self.origin, "show", f"main:{INST}/d-work/rows/1.md"))

    def test_a_batch_of_landed_lines_is_refused(self):
        rc, _, err = self.dwork("state", "1", "planned", "-d", "Y plan", "--said", "Y", "--land")
        self.assertEqual(rc, 0, err)
        head = self.main_at_origin()
        with unittest.mock.patch("sys.stdin", io.StringIO("state 1 planned -d 'Y plan' --said Y\n")):
            rc, out, err = self.dwork("batch", "-", "--land")
        self.assertEqual(rc, 1)
        self.assertIn("skipped (already landed): line 1", out); self.assertIn("every line of the batch", err)
        self.assertEqual(self.main_at_origin(), head, "nothing pushed")
        self.assertEqual(len(self.hook_runs()), 1)

    def test_a_merge_naming_done_and_its_close_are_refused_before_any_push(self):
        before = self.main_at_origin()
        rc, _, err = self.batch("state 1 open -d 'Y done (merges PR #3 at abc1234)' --said Y\nstate 1 done\n")
        self.assertEqual(rc, 1)
        self.assertIn("line 1 (state 1 open", err); self.assertIn("line 2 (state 1 done)", err)
        self.assertIn("the state follows the merge", err)
        rc, _, err = self.batch("state 1 done -d 'Y done (merges PR #3 at abc1234)' --said Y\n")
        self.assertEqual(rc, 1); self.assertIn("and sets #1 done", err)
        self.assertEqual(self.main_at_origin(), before)
        self.assertEqual(self.hook_runs(), [])
        self.assertFalse(self.wt.exists(), "refused before the worktree was touched")

    def test_read_batch_text_reads_as_read_batch(self):
        """#587: `board advance` composes its lines and parses them with `read_batch_text`, `read_batch`'s own loop."""
        land = dyadlib.load_module(PKG / "scripts" / "land.py", "land")
        presence = self.seat / INST / "d-work" / "sessions" / "s1.md"
        presence.parent.mkdir(parents=True); presence.write_text("session: s1\n")
        said = self.top / "said.txt"; said.write_text("Y\n")
        text = ("# a round\n\n"
                f"state 1 planned -d 'Y plan' --said-file {said}\n"
                f"land {presence}\n"
                "board 1 owner=engineer-bbbbbbbb waiting-on='unit engineer-bbbbbbbb' next='build it'\n"
                "post engineer-bbbbbbbb --row 1 --kind relay 'row 1 planned; yours: the code'\n"
                "post orchestrate-cccccccc --row 1 --kind notice --cc counsel-dddddddd 'fyi'\n")
        f = self.top / "batch.txt"; f.write_text(text)
        a = land.read_batch(str(f), self.seat, INST, self.pkg.DWORK_VALUE_FLAGS, self.pkg.dwork_args)
        b = land.read_batch_text(text, self.seat, INST, self.pkg.DWORK_VALUE_FLAGS, self.pkg.dwork_args)
        shape = lambda ls: [(l.n, l.verb, l.argv, l.rels, getattr(l, "parsed", None)) for l in ls]
        self.assertEqual(shape(a), shape(b))
        self.assertEqual([l.verb for l in b], ["state", "land", "board", "post", "post"])

    def test_a_racing_commit_rebuilds_the_batch(self):
        git(self.seat.parent, "clone", "-q", str(self.origin), str(self.racer))
        add_row(self.racer, 2, "racer", "open racer")
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", "ledger: #2 open")
        self.race.write_text("")
        rc, out, err = self.batch("new mine --prompt 'open mine'\nstate 1 planned -d 'Y plan' --said Y\n")
        self.assertEqual(rc, 0, err)
        self.assertIn("main moved", err)
        self.assertEqual(len(self.hook_runs()), 2, "the first push raced, the rebuild pushed")
        self.assertIn("title: mine", git(self.origin, "show", f"main:{INST}/d-work/rows/3.md"))
        self.assertIn("state: planned", git(self.origin, "show", f"main:{INST}/d-work/rows/1.md"))
        self.assertEqual(git(self.origin, "log", "-1", "--format=%s", "main"), "ledger: batch #3 open: mine, #1 planned (Y plan)")
        self.assertEqual(git(self.origin, "log", "-1", "--format=%s", "main~1"), "ledger: #2 open")

    def test_a_line_naming_m_land_mirror_or_another_verb_is_refused(self):
        for line, says in (("state 1 open --prompt x -m hi", "-m is the batch's"),
                           ("state 1 open --prompt x --land", "--land is the batch's"),
                           ("state 1 open --prompt x --mirror w", "--mirror is the batch's"),
                           ("state 1 open --prompt x --check", "--check writes nothing"),   # #464
                           ("retire 1 -d 'Y archive' --said Y", "not 'retire'"),
                           ("land a b -m hi", "-m is the batch's"),
                           ("'unbalanced", "line 1")):
            rc, _, err = self.batch(line + "\n")
            self.assertEqual(rc, 1, line); self.assertIn(says, err, line)
        rc, _, err = self.dwork("batch", str(self.top / "batch.txt"))
        self.assertEqual(rc, 1); self.assertIn("only with --land", err)
        self.assertEqual(self.hook_runs(), [])

    # ---- the caller-copy fix (#459)
    def test_land_restores_an_identical_copy_and_leaves_a_differing_one(self):
        plan = self.seat / INST / "d-work" / "plans" / "1.md"
        rel = plan.relative_to(self.seat).as_posix()
        plan.parent.mkdir(parents=True); plan.write_text("# Plan #1\n")
        rc, out, err = self.dwork("land", str(plan), "-m", "ledger: plan #1")       # untracked, identical: removed, then fast-forwarded
        self.assertEqual(rc, 0, err)
        self.assertIn("restored", out); self.assertEqual(git(self.seat, "rev-parse", "HEAD"), self.main_at_origin()); self.assertEqual(self.status(), "")
        plan.write_text("# Plan #1\nrevision 2\n")
        rc, out, err = self.dwork("land", str(plan), "-m", "ledger: plan #1 revised")  # tracked, identical: checked out, then fast-forwarded
        self.assertEqual(rc, 0, err)
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), self.main_at_origin()); self.assertEqual(self.status(), "")
        self.assertEqual(plan.read_text(), "# Plan #1\nrevision 2\n")
        here = git(self.seat, "rev-parse", "HEAD")
        plan.write_text("# Plan #1\nrevision 3\n"); (self.seat / "other.txt").write_text("mine\n")
        rc, out, err = self.dwork("land", str(plan), "-m", "ledger: plan #1 again")    # another change: untouched
        self.assertEqual(rc, 0, err)
        self.assertIn("has changes", out); self.assertNotIn("restored", out)
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), here)
        self.assertEqual(plan.read_text(), "# Plan #1\nrevision 3\n"); self.assertTrue((self.seat / "other.txt").exists())
        (self.seat / "other.txt").unlink()
        plan.write_text("# Plan #1\nrevision 3!\n")                                  # one differing byte: untouched
        o = io.StringIO()
        with contextlib.redirect_stdout(o):
            sys.modules["land"].fast_forward(self.seat, self.main_at_origin(), [rel])
        self.assertIn("has changes", o.getvalue()); self.assertNotIn("restored", o.getvalue())
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), here)
        self.assertEqual(plan.read_text(), "# Plan #1\nrevision 3!\n")

    def test_off_main_an_identical_copy_is_restored_and_a_differing_one_named(self):
        """#466 (R3 of #463): a seat on its own branch keeps its own work; each landed path is judged alone."""
        git(self.seat, "checkout", "-q", "-b", "feature")
        d = self.seat / INST / "d-work" / "plans"; d.mkdir(parents=True)
        same, diff = d / "1.md", d / "2.md"
        same.write_text("# Plan #1\n"); diff.write_text("# Plan #2\n")
        (self.seat / "mine.txt").write_text("feature work\n")
        here = git(self.seat, "rev-parse", "HEAD")
        rc, out, err = self.dwork("land", str(same), str(diff), "-m", "ledger: plans 1 2")
        self.assertEqual(rc, 0, err)
        self.assertIn(f"restored {INST}/d-work/plans/1.md, {INST}/d-work/plans/2.md from HEAD", out)
        self.assertFalse(same.exists()); self.assertFalse(diff.exists())       # both identical to main: on main now
        self.assertTrue((self.seat / "mine.txt").exists())                     # the branch's own work is untouched
        self.assertEqual(git(self.seat, "rev-parse", "HEAD"), here)            # never fast-forwarded off main
        self.assertIn("not on main", out)
        diff.write_text("# Plan #2\nedited after landing\n")
        same.write_text("# Plan #1\n")
        o = io.StringIO()
        with contextlib.redirect_stdout(o):
            sys.modules["land"].fast_forward(self.seat, self.main_at_origin(),
                                             [f"{INST}/d-work/plans/1.md", f"{INST}/d-work/plans/2.md"])
        self.assertIn(f"restored {INST}/d-work/plans/1.md from HEAD", o.getvalue())
        self.assertIn(f"left changed here: {INST}/d-work/plans/2.md", o.getvalue())
        self.assertFalse(same.exists()); self.assertEqual(diff.read_text(), "# Plan #2\nedited after landing\n")



class UtcDateTests(unittest.TestCase):
    """#592 R-b: `land`'s already-landed test and the batch's Done-order test are given UTC's date, whatever the host's
    local day; each is stubbed to capture the date it is handed and stop."""
    def setUp(self):
        self.land = dyadlib.load_module(PKG / "scripts" / "land.py", "land_utc")

    def test_already_landed_is_given_the_utc_date(self):
        got = []
        def stop(wt, inst, pos, vals, bare, words, today):
            got.append(today); return "stubbed"
        with livetest.off_utc() as (utc, local), unittest.mock.patch.object(self.land, "already_landed", stop):
            self.assertNotEqual(utc, local)
            build = self.land.verb_builder(["dwork", "state", "1", "planned"], ["state", "1", "planned"], {}, set(), INST, None)
            with self.assertRaises(self.land.Refused):
                build(Path("."))
        self.assertEqual(got, [utc])

    def test_done_order_is_given_the_utc_date(self):
        got = []
        def stop(lines, today):
            got.append(today); raise self.land.Refused("stubbed")
        with livetest.off_utc() as (utc, local), unittest.mock.patch.object(self.land, "read_batch", lambda *a: []), \
                unittest.mock.patch.object(self.land, "done_order", stop):
            with self.assertRaises(self.land.Refused):
                self.land.batch(["batch", "-"], {}, {"--land"}, Path("."), INST, None, set(), None, None)
        self.assertEqual(got, [utc])


if __name__ == "__main__":
    unittest.main()
