"""`dyad automaton scan|run` (scripts/automaton.py, d-work #556), over an installed scratch world: a real scratch
install as the seed, a bare origin, a racer clone that pushes PR heads as `refs/pull/<n>/head` and lands on main, and
a seat clone whose pre-push hook only logs.

The cases:
- `scan` lists the acts and writes nothing.
- `run` merges the PR a recorded `Y done` names, then closes the row, its accreted row and its board entry in the same
  run; a second run has nothing to do.
- A `Y done` naming a head the PR has moved off is refused. The refusal is posted once to the home's inbox (the board
  `_cos` holder), naming the row and quoting no entry; a second run does not post it again.
- A planned row with a board entry notifies each owner once; the board is set waiting on its first owner and each
  notice quotes the owner's part from the plan's `parts:` line (#572 K1, K2); a Done whose cut does not land waits on
  its merge (K3).
- A push race is re-merged at once, without backoff.
- A row naming two PRs lands them as one cut: one push (#562).
- A landed cut is corroborated once, before..after; a failed corroboration is posted to home and the run exits 1
  (#564).
- The sweep (#564) prints every finding, tells the home only what no automaton notice has told yet, and exits 1
  when a finding fails.
- A health run the sweep makes that appends an event (`role: automaton`) is landed on main as an events-only commit
  citing no d-work; a second, identical reading lands nothing; without `--row` nothing lands (#593).
- #587 X6: a PR head that moved off the head a phased entry records (verifying, done-ready, done-asked) fires
  `head-moved`: back to verifying, the new head recorded, the evidence and the question withdrawn, the holder told and
  the owners cc'd; the new heads are then verified in the same run.
- #587 X5: a verifying entry whose every PR is up at its recorded head gets the combined merge onto main and its
  evidence: `evidence-verified` with the sha256, or `evidence-failed` with the conflict or the first FAIL line as the
  note; an evidence run that says nothing about the PRs is told to home and fires nothing.
- #594: the home is per cabinet — `home(…, cabinet)` reads that cabinet's `_cos[-<operator>]` file, `escalate` tells
  the home of the row's cabinet, and the sweep tells each cabinet's home its own in-flight lines.
- #587 X10: `evidence --out` writes those verdicts as JSON lines and fires, posts and lands nothing, refused in a job
  holding a write token; `run --evidence-from` fires each line only once it passes every check (its shape, a verdict
  of the machine's table, the row in verifying, its heads the board's recorded and the live ones), never computing.
- Misuse is exit 2."""
import contextlib, io, json, os, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib, livetest
from test_steps import World, git, ROW, REC, INST

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
HOME = "program-aaaaaaaa"
BOB = "program-bob-cccccccc"                 # a second cabinet's leader (#594)


CORROBORATED = []
def passing(repo, before, after):
    CORROBORATED.append((before, after)); return True, ["ok   [corroborate] check"]

EVIDENCED = []
EV = "0123456789abcdef" * 4
def evidence_ok(repo, sha):
    EVIDENCED.append(sha); return 0, [f"head={sha}", "ok   [rule-12] suite", f"evidence-sha256={EV}"]

def run(argv, repo, corroborate=passing, evidence=evidence_ok, **envs):
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "GITHUB_ACTIONS": "", **envs}), \
         unittest.mock.patch.object(am, "corroborate", corroborate), \
         unittest.mock.patch.object(am, "evidence_at", evidence), \
         contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = am.main(argv, repo)
    return rc, out.getvalue(), err.getvalue()


class SweepCiTests(unittest.TestCase):
    """#617: `sweep_ci` reads the public run list with or without a token, one listing per workflow; only a failed
    request is "not read"."""
    def setUp(self):
        import tempfile, shutil, datetime
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        g = lambda *a: subprocess.run(["git", "-C", str(self.d), *a], check=True, capture_output=True, text=True).stdout.strip()
        g("init", "-q", "-b", "main"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
        (self.d / "x.py").write_text("x"); g("add", "-A"); g("commit", "-qm", "code")
        self.c = g("rev-parse", "HEAD"); self.g = g
        self.now = datetime.datetime.now(datetime.timezone.utc)
    def ci(self, runs=None, token="", slug="o/r", fail=None):
        import io as _io, json as _json
        seen = []
        def urlopen(req, timeout=None):
            seen.append((req.full_url, req.headers.get("Authorization")))
            if fail:
                raise fail
            name = next(n for n, f in am.CI_FILES.items() if f"/{f}/" in req.full_url)
            body = [w for w in (runs or []) if w["name"] == name]
            return contextlib.closing(_io.BytesIO(_json.dumps({"workflow_runs": body}).encode()))
        with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": token, "GITHUB_REPOSITORY": slug}), \
             unittest.mock.patch("urllib.request.urlopen", urlopen):
            return am.sweep_ci(self.d, "HEAD", self.now), seen
    def test_a_corroborated_push_without_a_token_is_no_finding(self):
        got, seen = self.ci([{"name": "rule-11 package", "head_sha": self.c, "conclusion": "success"}])
        self.assertEqual(got, [])
        self.assertEqual(sorted(u.split("/workflows/")[1].split("/")[0] for u, _ in seen),
                         ["dyad-automaton.yml", "dyad-package.yml", "dyad-sweep.yml"])           # #619: the full sweep too
        self.assertEqual(sorted("status=success" in u for u, _ in seen), [False, False, True])   # delivery reads every status
        self.assertTrue(all(a is None for _, a in seen))                                 # no token: no header
        self.assertTrue(all(f"per_page={am.CI_PAGE}" in u for u, _ in seen))
    def test_an_uncorroborated_push_is_a_failing_finding_and_a_token_is_sent(self):
        got, seen = self.ci([], token="t0k")
        self.assertEqual(got, [(True, f"finding: code push {self.c[:12]} to main has no successful corroboration (rule-11 package, d-work automaton)")])
        self.assertTrue(all(a == "Bearer t0k" for _, a in seen))
    def test_only_a_failed_request_is_not_read(self):
        got, _ = self.ci(fail=OSError("down"))
        self.assertEqual(got, [(False, "finding: corroboration not read from the hosting (OSError)")])
        got, seen = self.ci(slug="")                                                      # no hosting named at all
        self.assertEqual((got[0][1].split(" not read")[0], seen), ("finding: corroboration of 1 code push(es) to main", []))
    def aged(self, files: dict[str, str], hours: float = 1, email: str = "t@t") -> str:
        """One commit of `files`, committed `hours` ago by `email`: past the delivery grace."""
        import datetime as _dt
        when = (self.now - _dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S+0000")
        for rel, text in files.items():
            (self.d / rel).parent.mkdir(parents=True, exist_ok=True); (self.d / rel).write_text(text)
        self.g("add", "-A")
        subprocess.run(["git", "-C", str(self.d), "-c", f"user.email={email}", "commit", "-qm", "c"], check=True,
                       env={**os.environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_EMAIL": email})
        return self.g("rev-parse", "HEAD")
    def test_a_sweep_not_delivered_is_a_finding_and_a_run_at_or_after_delivers(self):
        """#619 Decision 4: the newest code push needs a `d-work sweep` run at it or later, the newest ledger push a
        `d-work automaton` run; queued, in progress, success or failure count, cancelled and skipped do not."""
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}):
            code = self.aged({"y.py": "y"}, hours=2)
            ledger = self.aged({"agent-corpus/d-work/rows/1.md": "id: 1\n"}, hours=1)
            ok = {"name": "rule-11 package", "head_sha": code, "conclusion": "success", "status": "completed"}
            got, _ = self.ci([ok])
            self.assertEqual([l for _, l in got], [
                f"finding: delivery: no full sweep started on main at or after the landed merge {code[:12]}",
                f"finding: delivery: no stores sweep started on main at or after the push {ledger[:12]}"])
            for status, conclusion, counts in (("queued", None, True), ("in_progress", None, True), ("completed", "failure", True),
                                               ("completed", "success", True), ("completed", "cancelled", False),
                                               ("completed", "skipped", False)):
                runs = [ok, {"name": "d-work sweep", "head_sha": ledger, "status": status, "conclusion": conclusion},
                        {"name": "d-work automaton", "head_sha": ledger, "status": status, "conclusion": conclusion}]
                got, _ = self.ci(runs)
                self.assertEqual(got == [], counts, (status, conclusion, got))
            got, _ = self.ci([ok, {"name": "d-work sweep", "head_sha": self.c, "status": "completed", "conclusion": "success"}])
            self.assertIn("no full sweep", got[0][1])                                 # a run before the push delivers nothing
    def test_the_workflows_own_pushes_and_a_young_push_are_not_judged(self):
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}):
            self.aged({"agent-corpus/d-work/rows/1.md": "id: 1\n"}, hours=1, email=am.WORKFLOW_IDENTITY)
            (self.d / "agent-corpus/d-work/rows/2.md").write_text("id: 2\n"); self.g("add", "-A")
            self.g("commit", "-qm", "young")                                          # within the grace: waits
            self.assertEqual(self.ci([{"name": "rule-11 package", "head_sha": self.c, "conclusion": "success"}])[0], [])
    def test_the_slug_is_read_off_origin(self):
        with unittest.mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": ""}):
            self.assertIsNone(am.repo_slug(self.d))
            for url, want in (("https://github.com/o/r.git", "o/r"), ("git@github.com:o/r", "o/r"),
                              ("http://local_proxy@127.0.0.1:1/git/o/r", "o/r"), ("/srv/o/r.git", None)):
                self.g("remote", "remove", "origin") if "origin" in self.g("remote") else None
                self.g("remote", "add", "origin", url)
                self.assertEqual(am.repo_slug(self.d), want, url)
        with unittest.mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "a/b"}):
            self.assertEqual(am.repo_slug(self.d), "a/b")


class CorroboratedTests(unittest.TestCase):
    """#614: `sweep_ci`'s decision on one code push, over a real first-parent history and the runs the hosting reports."""
    def setUp(self):
        import tempfile, shutil
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        g = lambda *a: subprocess.run(["git", "-C", str(self.d), *a], check=True, capture_output=True, text=True).stdout.strip()
        self.g = g
        g("init", "-q", "-b", "main"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
        def commit(name, msg=None):
            (self.d / name).write_text(name); g("add", "-A"); g("commit", "-qm", msg or name)
            return g("rev-parse", "HEAD")
        self.a = commit("a")                          # #693's merge: its run cancelled by the next push
        self.b = commit("b")                          # #694's merge: likewise
        self.c = commit("c")                          # #695's merge: its run succeeded
        self.d_ = commit("d")                         # a later push whose run was cancelled, no success after it
        g("checkout", "-qb", "side", self.a); self.side = commit("s"); g("checkout", "-q", "main")
        self.fp = set(g("rev-list", "--first-parent", "main").split())

    wf = staticmethod(lambda sha, conclusion="success", name="rule-11 package", at="2026-11-05T21:00:00Z":
                       {"head_sha": sha, "conclusion": conclusion, "name": name, "created_at": at})

    def test_a_cancelled_run_a_later_success_covers_is_corroborated(self):
        listed = [self.wf(self.c)]
        for sha in (self.a, self.b):
            self.assertTrue(am.corroborated(self.d, sha, [self.wf(sha, "cancelled")], listed, self.fp, []), sha)
        self.assertTrue(am.corroborated(self.d, self.c, [self.wf(self.c)], listed, self.fp, []))

    def test_a_cancelled_run_no_later_success_covers_fails(self):
        listed = [self.wf(self.c), self.wf(self.d_, "cancelled")]
        self.assertFalse(am.corroborated(self.d, self.d_, [self.wf(self.d_, "cancelled")], listed, self.fp, []))
        self.assertFalse(am.corroborated(self.d, self.a, [], [self.wf(self.c, "failure")], self.fp, []))    # a failed run covers nothing
        self.assertFalse(am.corroborated(self.d, self.a, [], [self.wf(self.side)], self.fp, []))           # off main's first parent
        self.assertFalse(am.corroborated(self.d, self.a, [], [self.wf(self.c, name="d-work sweep")], self.fp, []))   # not a corroborating workflow

    def test_a_dyad_merge_is_corroborated_by_the_automaton_run_that_merged_it(self):
        (self.d / "m").write_text("m"); self.g("add", "-A")
        self.g("commit", "-qm", "Merge PR #1 at x\n\nExecuted by `dyad merge` on the Done-Y recorded on main")
        m = self.g("rev-parse", "HEAD"); fp = self.fp | {m}
        later = self.wf(m, name="d-work automaton", at="2999-01-01T00:00:00Z")
        self.assertTrue(am.corroborated(self.d, m, [], [], fp, [later]))
        earlier = self.wf(m, name="d-work automaton", at="2000-01-01T00:00:00Z")
        self.assertFalse(am.corroborated(self.d, m, [], [], fp, [earlier]))


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

    def test_a_done_naming_no_merge_archives_its_retired_rows_next_run(self):
        """#574 G5: a Done that names no merge is recorded `done` at once, so no close runs; the automaton archives."""
        rows, prov = f"{INST}/d-work/rows", f"{INST}/d-work/provenance"
        self.w.write_main({f"{rows}/9.md": ROW.format(id=9, state="done", disposed="2026-11-02 Y plan; 2026-11-02 Y done (retires #11)"),
                           f"{prov}/9.md": REC.format(id=9), f"{rows}/11.md": ROW.format(id=11, state="backlog", disposed=""),
                           f"{INST}/d-work/board/_cos.md": f"holder: {HOME}\nwriter: h1\n"})
        rc, out, err = run(["scan"], self.w.seat)
        self.assertEqual(out.strip(), "archive #11 (retired by row #9's Done)")
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(am.dyadlib.parse_row_file(self.on_main(f"{rows}/11.md")).state, "archived")
        self.assertEqual(run(["run"], self.w.seat)[1].strip(), "nothing to do")

    def test_a_no_merge_done_tells_home_once_of_a_retired_row_gone_open(self):
        rows, prov = f"{INST}/d-work/rows", f"{INST}/d-work/provenance"
        self.w.write_main({f"{rows}/9.md": ROW.format(id=9, state="done", disposed="2026-11-02 Y plan; 2026-11-02 Y done (retires #11)"),
                           f"{prov}/9.md": REC.format(id=9), f"{rows}/11.md": ROW.format(id=11, state="open", disposed=""),
                           f"{INST}/d-work/board/_cos.md": f"holder: {HOME}\nwriter: h1\n"})
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        (msg,) = self.inbox(HOME); self.assertIn("row #11 is open", msg)
        self.assertEqual(am.dyadlib.parse_row_file(self.on_main(f"{rows}/11.md")).state, "open")
        self.assertEqual(run(["run"], self.w.seat)[1].strip(), "nothing to do")

    def test_a_done_archives_exactly_the_rows_it_retires(self):
        """#574 G5: the close archives each named row that is backlog or done, on the Done's words; a named row that
        is open is told to home and left as it is."""
        rows, prov = f"{INST}/d-work/rows", f"{INST}/d-work/provenance"
        files = dict(self.files)
        files[f"{rows}/9.md"] = ROW.format(id=9, state="planned",
            disposed=f"2026-11-02 Y plan; 2026-11-02 Y done (accreted #10, retires #11, #12, #13, merges PR #7 at {self.sha})")
        files[f"{prov}/9.md"] = REC.format(id=9)
        for rid, st in ((11, "backlog"), (12, "done"), (13, "open"), (14, "backlog")):
            files[f"{rows}/{rid}.md"] = ROW.format(id=rid, state=st, disposed="")
        self.w.write_main(files)
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        st = lambda rid: am.dyadlib.parse_row_file(self.on_main(f"{rows}/{rid}.md"))
        self.assertEqual([st(r).state for r in (9, 11, 12, 13, 14)], ["done", "archived", "archived", "open", "backlog"])
        self.assertRegex(st(11).disposed, r"Y archive \(done #9\)$")
        self.assertRegex(self.on_main(f"{prov}/11.md"), r"## 1 disposition \d{4}-\d{2}-\d{2} done #9, 2026-11-02\n")
        self.assertTrue(any("archive on close refused for row #9: row #13 is open" in m for m in self.inbox(HOME)), self.inbox(HOME))
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")
        files = {f"{rows}/13.md": ROW.format(id=13, state="done", disposed="2026-11-03 Y done")}   # #13 done later, on its own
        self.w.write_main(files)
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do"); self.assertEqual(st(13).state, "done")   # refused once, never resolved

    def test_a_plan_y_flips_the_board_and_the_notice_quotes_each_part(self):
        """#572 K1/K2: the board waits on the first owner with the plan as its next act and no question; each owner's
        notice quotes its own part from the plan's `parts:` line, matched by seat or by function; one write, once."""
        b = f"{INST}/d-work/board/12.md"
        self.w.write_main({f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                           f"{INST}/d-work/plans/12.md": "# Plan #12\n\nparts: engineer: PR 2, the verb; counsel-0032b4c0: PR 1, the Rule\n",
                           b: f"holder: {HOME}\nowner: engineer-1537d8fb s1; counsel-0032b4c0 s2\nwaiting-on: operator\n"
                              f"question: Y/N: proceed with #12 as planned?\nwriter: h1\n"})
        rc, out, err = run(["scan"], self.w.seat)
        self.assertIn("board #12: next=execute plans/12.md, question removed, waiting-on=unit engineer-1537d8fb", out)
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        f = am.board().parse(self.on_main(b))[0]
        self.assertEqual((f["waiting-on"], f["next"], f["holder"]), ("unit engineer-1537d8fb", "execute plans/12.md", HOME))
        self.assertNotIn("question", f)
        (eng,), (cou,) = self.inbox("engineer-1537d8fb"), self.inbox("counsel-0032b4c0")
        self.assertIn("body: row #12 planned; read plans/12.md; yours: PR 2, the verb", eng)
        self.assertIn("body: row #12 planned; read plans/12.md; yours: PR 1, the Rule", cou)
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")

    def test_a_retired_seat_entry_is_told_to_home_and_never_rewritten(self):
        """#604: a planned row's entry still waiting on `seat <name>` (removed in 1.0) is not flipped — the unit it names
        and its open question would be lost — but told once to home, with the form to write."""
        self.assertIsNone(am.planned_flip(5, {"waiting-on": "seat counsel-0032b4c0", "question": "Y/N: x?", "holder": "h"},
                                          ["engineer-1537d8fb"]))
        b = f"{INST}/d-work/board/12.md"
        entry = (f"holder: {HOME}\nowner: engineer-1537d8fb s1\nwaiting-on: seat counsel-0032b4c0\n"
                 f"question: Y/N: x?\nwriter: h1\n")
        self.w.write_main({f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                           b: entry, f"{INST}/d-work/board/_cos.md": f"holder: {HOME}\nwriter: h1\n"})
        rc, out, err = run(["scan"], self.w.seat)
        self.assertIn("tell home: automaton: board flip refused for row #12", out)
        self.assertIn("write `waiting-on: unit counsel-0032b4c0`", out)
        self.assertNotIn("board #12:", out)
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.on_main(b), entry)                                        # left as it stands
        (msg,) = self.inbox(HOME)
        self.assertIn("board flip refused for row #12", msg)
        rc, out, _ = run(["run"], self.w.seat)
        self.assertNotIn("tell home", out); self.assertEqual(len(self.inbox(HOME)), 1)

    def test_a_done_whose_cut_does_not_land_waits_on_its_merge(self):
        """#572 K3: the merge is refused this run, so the board waits on the merge, its question removed; once."""
        files = dict(self.files)
        files[f"{INST}/d-work/board/9.md"] = f"holder: {HOME}\nwaiting-on: operator\nquestion: Y/N: Done with #9?\nwriter: h1\n"
        self.w.write_main(files)
        self.w.pr(7, "dyad/zz-pr.txt", "moved\n")                                       # the merge is refused
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        f = am.board().parse(self.on_main(f"{INST}/d-work/board/9.md"))[0]
        self.assertEqual((f["waiting-on"], f["holder"]), ("external merge PR #7", HOME)); self.assertNotIn("question", f)
        self.assertIn("board #9: question removed, waiting-on=external merge PR #7", out)
        rc, out, _ = run(["run"], self.w.seat)
        self.assertNotIn("board #9", out)

    # ---- d-work #587: a phased entry is in the machine, so K1-K3 leave it alone and a Y recorded by hand is caught up
    def phased(self, rid, phase, sub, question=None, owner="engineer-1537d8fb"):
        b = am.board()
        f = {"holder": HOME, "phase": b.phase_render(phase, sub), "owner": owner, "since": "2026-11-04T10:00Z", "writer": "h1"}
        f.update(b.derive(rid, f))
        if question:
            f["question"] = question
        return b.render(f, b.FIELDS)

    def test_s11_a_question_asked_of_a_planned_row_is_never_flipped_away(self):
        """#587 S11, the 05:29:17Z replay: row 570 planned with a `Y plan` last, then home asks plan revision 9 on its
        board (a later commit). K1's flip read that as a fresh plan-Y and erased the question (c31d76d); a board written
        after the row's last `Y plan` is home's act, so the automaton writes nothing over it."""
        row, board_f = f"{INST}/d-work/rows/570.md", f"{INST}/d-work/board/570.md"
        self.w.write_main({row: ROW.format(id=570, state="planned", disposed="2026-11-04 Y plan; 2026-11-05 Y plan (revision 8)"),
                           f"{INST}/d-work/provenance/570.md": "# Provenance #570\n\n## 1 disposition 2026-11-04 Y plan\n\n```\nY\n```\n\n"
                                                               "## 2 disposition 2026-11-05 Y plan (revision 8)\n\n```\nY\n```\n\n",
                           board_f: f"holder: {HOME}\nowner: audit-e73be78c s1\nwaiting-on: unit audit-e73be78c\nwriter: h1\n"})
        asked = (f"holder: {HOME}\nowner: audit-e73be78c s1\nwaiting-on: operator\nnext: answer plan revision 9\n"
                 "question: Y/N: proceed with #570 revision 9 as planned?\nwriter: h1\n")
        self.w.write_main({board_f: asked})
        rc, out, err = run(["scan"], self.w.seat)
        self.assertEqual(rc, 0, out + err); self.assertNotIn("board #570", out)
        run(["run"], self.w.seat)
        self.assertEqual(self.on_main(board_f), asked)                                  # the question stands

    def test_a_phased_planned_entry_gets_no_k1_flip_and_no_k2_notice(self):
        self.w.write_main({f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                           f"{INST}/d-work/board/12.md": self.phased(12, "building", {"unit": ["engineer-1537d8fb"]})})
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual((rc, out.strip()), (0, "nothing to do"))

    def test_a_phased_landing_entry_gets_no_k3_flip(self):
        files = dict(self.files)
        files[f"{INST}/d-work/board/9.md"] = self.phased(9, "landing", {"unit": ["engineer-1537d8fb"], "pr": [f"7 at {self.sha}"],
                                                                         "evidence": ["0" * 64]})
        self.w.write_main(files)
        self.w.pr(7, "dyad/zz-pr.txt", "moved\n")                                       # the merge is refused
        before = self.on_main(f"{INST}/d-work/board/9.md")
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("board #9", out)
        self.assertEqual(self.on_main(f"{INST}/d-work/board/9.md"), before)

    def test_s11_phased_a_question_asked_after_the_plan_y_is_not_caught_up(self):
        """S11 on the phased path (found by #587's replays): the row's `Y plan` lands first, then home asks a revision
        on the phased board (plan-asked) in a later commit; the catch-up must not read the older `Y` as its answer."""
        rows = f"{INST}/d-work/rows/12.md"
        self.w.write_main({rows: ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n"})
        asked = self.phased(12, "plan-asked", {"unit": ["engineer-1537d8fb"]}, "Y/N: proceed with #12 revision 2 as planned?")
        self.w.write_main({f"{INST}/d-work/board/12.md": asked})
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual((rc, out.strip()), (0, "nothing to do"))
        run(["run"], self.w.seat)
        self.assertEqual(self.on_main(f"{INST}/d-work/board/12.md"), asked)

    def test_a_plan_y_recorded_by_hand_is_caught_up_with_no_ledger_line(self):
        rows = f"{INST}/d-work/rows/12.md"
        self.w.write_main({rows: ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                           f"{INST}/d-work/board/12.md": self.phased(12, "plan-asked", {"unit": ["engineer-1537d8fb"]},
                                                                      "Y/N: proceed with #12 as planned?")})
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual(out.strip(), "catch up #12 answered-Y (recorded on the ledger)")
        row_before = self.on_main(rows)
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        f = am.board().parse(self.on_main(f"{INST}/d-work/board/12.md"))[0]
        self.assertEqual((am.board().phase_name(f), f["waiting-on"]), ("building", "unit engineer-1537d8fb"))
        self.assertNotIn("question", f)
        (msg,) = self.inbox("engineer-1537d8fb")
        self.assertIn("body: row #12 planned; read plans/12.md", msg); self.assertIn("from: automaton", msg)
        self.assertEqual(self.on_main(rows), row_before)                                  # the ledger already held it
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")

    def test_a_done_naming_another_pr_set_is_not_caught_up(self):
        files = dict(self.files)
        files[f"{INST}/d-work/board/9.md"] = self.phased(9, "done-asked", {"unit": ["engineer-1537d8fb"], "pr": [f"8 at {self.sha}"],
                                                                            "evidence": ["0" * 64]}, "Y/N: Done with #9 nine (merges PR #8)?")
        self.w.write_main(files)
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertNotIn("catch up", out)
        self.assertIn(f"merge PR #7 at {self.sha} (row #9)", out)

    def test_a_plan_y_recorded_by_hand_at_plan_ready_is_caught_up(self):
        """The question was asked in chat without `asked`: the entry is still at plan-ready, and the catch-up still moves
        it to building and posts the plan notice (#587, a K1/K2 parity the skip of phased entries would otherwise lose)."""
        self.w.write_main({f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="planned", disposed="2026-11-02 Y plan"),
                           f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                           f"{INST}/d-work/board/12.md": self.phased(12, "plan-ready", {"unit": ["engineer-1537d8fb"]})})
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual(out.strip(), "catch up #12 answered-Y (recorded on the ledger)")
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        f = am.board().parse(self.on_main(f"{INST}/d-work/board/12.md"))[0]
        self.assertEqual((am.board().phase_name(f), f["waiting-on"]), ("building", "unit engineer-1537d8fb"))
        (msg,) = self.inbox("engineer-1537d8fb")
        self.assertIn("body: row #12 planned; read plans/12.md", msg)
        self.assertIn("plan-ready -> building", git(self.w.origin, "log", "-2", "--format=%s", "main"))

    def test_a_batch_y_done_recorded_by_hand_at_done_ready_is_caught_up_per_row(self):
        """A batch `Y done` names the union; each row's entry lists only its own PR. Each is caught up to landing,
        waiting on the union with the heads the entry names, as `board advance` writes a batch."""
        sha8 = self.w.pr(8, "dyad/zz-pr8.txt", "pr8\n")
        d = f"2026-11-02 Y plan; 2026-11-02 Y done (batch #11,#13, merges PR #7 at {self.sha}, PR #8 at {sha8})"
        files = {}
        for rid, pr in ((11, f"7 at {self.sha}"), (13, f"8 at {sha8}")):
            files[f"{INST}/d-work/rows/{rid}.md"] = ROW.format(id=rid, state="planned", disposed=d)
            files[f"{INST}/d-work/provenance/{rid}.md"] = REC.format(id=rid)
            files[f"{INST}/d-work/board/{rid}.md"] = self.phased(rid, "done-ready", {"unit": ["engineer-1537d8fb"], "pr": [pr],
                                                                                    "evidence": ["0" * 64]})
        self.w.write_main(files)
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertIn("catch up #11 answered-Y (recorded on the ledger)", out)
        self.assertIn("catch up #13 answered-Y (recorded on the ledger)", out)
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}):
            for rid in (11, 13):
                self.assertIn("caught up", am.catch_up(self.w.seat, rid, "done-ready"))
        for rid in (11, 13):
            f = am.board().parse(self.on_main(f"{INST}/d-work/board/{rid}.md"))[0]
            b = am.board()
            self.assertEqual((b.phase_name(f), f["waiting-on"]), ("landing", "external merge PR #7, PR #8") if rid == 11
                             else ("landing", "external merge PR #8, PR #7"), rid)
            self.assertEqual(dict(b.pr_list(b.phase_of(f["phase"])[1])), {7: self.sha, 8: sha8})
            self.assertEqual(self.on_main(f"{INST}/d-work/rows/{rid}.md"), files[f"{INST}/d-work/rows/{rid}.md"])   # no ledger line

    def test_a_y_done_recorded_at_verifying_is_reported_and_the_board_is_left(self):
        files = dict(self.files)
        files[f"{INST}/d-work/board/9.md"] = self.phased(9, "verifying", {"unit": ["engineer-1537d8fb"], "pr": [f"7 at {self.sha}"]})
        self.w.write_main(files)
        self.w.pr(7, "dyad/zz-pr.txt", "moved\n")                                       # the merge is refused
        before = self.on_main(f"{INST}/d-work/board/9.md")
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("board #9 phase verifying: Y done recorded by hand, merge PR #7 pending; board not flipped", out)
        self.assertNotIn("catch up #9", out)
        # #587 X6: the move itself is the machine's to record — the new head on the entry, still verifying, never landing
        f = am.board().parse(self.on_main(f"{INST}/d-work/board/9.md"))[0]
        self.assertEqual(am.board().phase_name(f), "verifying")
        self.assertNotEqual(self.on_main(f"{INST}/d-work/board/9.md"), before)

    # ---- d-work #587 X5, X6: the automaton's own events
    ENG = "engineer-1537d8fb"

    def verifying_row(self, rid, phase, prs, question=None, evidence=None):
        sub = {"unit": [self.ENG], "pr": [f"{n} at {h}" for n, h in prs]} | ({"evidence": [evidence]} if evidence else {})
        return {f"{INST}/d-work/rows/{rid}.md": ROW.format(id=rid, state="planned", disposed="2026-11-02 Y plan"),
                f"{INST}/d-work/provenance/{rid}.md": f"# Provenance #{rid}\n\n## 1 disposition 2026-11-02 Y plan\n\n```\nY\n```\n\n",
                f"{INST}/d-work/board/{rid}.md": self.phased(rid, phase, sub, question),
                f"{INST}/d-work/board/_cos.md": f"holder: {HOME}\nwriter: h1\n"}

    def entry(self, rid):
        text = self.on_main(f"{INST}/d-work/board/{rid}.md")
        return am.board().parse(text)[0] if text else None

    def test_verifying_with_every_pr_up_is_verified_once(self):
        """X5: the combined merge of the recorded heads onto main, its evidence, then `evidence-verified` through the
        machine: done-ready, the sha256 recorded, the holder told; a second run has nothing to do."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual(out.strip(), f"evidence #14: combined merge of PR #7 at {self.sha} onto main")
        EVIDENCED.clear()
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        (head,) = EVIDENCED
        self.assertEqual(git(self.w.seat, "rev-list", "--parents", "-n", "1", head).split()[2], self.sha)   # base, then PR #7
        f = self.entry(14)
        b = am.board()
        self.assertEqual((b.phase_name(f), b.first(b.phase_of(f["phase"])[1], "evidence"), f["waiting-on"]),
                         ("done-ready", EV, f"unit {HOME}"))
        self.assertEqual(b.check_phased("14", f, None), [])
        (msg,) = self.inbox(HOME)
        self.assertIn("kind: report", msg); self.assertIn("from: automaton", msg); self.assertIn("row #14 done-ready", msg)
        self.assertIn("ring owed: " + HOME, out)
        self.assertIn("verifying -> done-ready", git(self.w.origin, "log", "-1", "--format=%s", "main"))
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")

    def test_the_combined_merge_is_the_same_commit_for_the_same_heads(self):
        base = git(self.w.seat, "rev-parse", "origin/main")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}):
            a, _ = am.combined_head(self.w.seat, base, [(7, self.sha)])
            b, _ = am.combined_head(self.w.seat, base, [(7, self.sha)])
        self.assertEqual(a, b)

    def test_a_failing_evidence_returns_the_row_to_its_unit(self):
        """X5: the first FAIL line is the note, the unit gets the relay and owes a ring; the row is building."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        failing = lambda repo, sha: (1, [f"head={sha}", "ok   [a] fine", "FAIL [agent/rows] 2026-11-02 Y done broke",
                                          "FAIL [b] second", f"evidence-sha256={EV}"])
        rc, out, err = run(["run"], self.w.seat, evidence=failing)
        self.assertEqual(rc, 0, out + err)
        f = self.entry(14)
        self.assertEqual(am.board().phase_name(f), "building")
        self.assertTrue(f["note"].startswith("combined evidence at "), f["note"])
        self.assertIn("FAIL [agent/rows] [an entry, read in the ledger] broke", f["note"])   # masked as post masks
        (msg,) = self.inbox(self.ENG)
        self.assertIn("kind: relay", msg); self.assertIn("row #14 building: the evidence failed", msg)
        self.assertIn(f"ring owed: {self.ENG}", out)

    def test_a_combined_conflict_fails_without_running_the_evidence(self):
        eight = self.w.pr(8, "dyad/zz-pr.txt", "eight's version\n")                   # the same file as PR #7
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha), (8, eight)]))
        EVIDENCED.clear()
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(EVIDENCED, [])
        f = self.entry(14)
        self.assertEqual(am.board().phase_name(f), "building")
        self.assertEqual(f["note"], f"combined merge: PR #8 at {eight[:12]} does not merge cleanly onto the merges before it: "
                                    "dyad/zz-pr.txt")                       # the paths only, never git's messages
        self.assertNotIn("Auto-merging", f["note"])

    def test_an_unknown_head_is_refused_not_a_conflict(self):
        """A head the fetch did not bring (the PR moved between ls-remote and fetch) is no verdict on the PRs: Refused,
        so `do_evidence` tells home and fires nothing; the next run's watch sees the move."""
        base = git(self.w.seat, "rev-parse", "origin/main")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}):
            with self.assertRaises(am.Refused) as c:
                am.combined_head(self.w.seat, base, [(7, "ab" * 20)])
        self.assertIn("not in the object store", str(c.exception))

    def test_an_evidence_that_cannot_be_taken_is_told_to_home_and_fires_nothing(self):
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        unfit = lambda repo, sha: (2, ["FAIL [evidence] a shallow clone"])
        before = self.on_main(f"{INST}/d-work/board/14.md")
        rc, out, err = run(["run"], self.w.seat, evidence=unfit)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.on_main(f"{INST}/d-work/board/14.md"), before)
        (msg,) = self.inbox(HOME)
        self.assertIn(f"the combined evidence of PR #7 at {self.sha[:12]} refused for row #14: FAIL [evidence] a shallow clone (exit 2)", msg)

    def test_a_told_evidence_refusal_is_neither_re_run_nor_re_told_when_main_moves(self):
        """The escalation is keyed on the row and the cut's heads, never on main's sha: after main moves, the next run
        finds it told, posts nothing and does not pay for the evidence again."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        calls = []
        unfit = lambda repo, sha: calls.append(sha) or (2, ["FAIL [evidence] a shallow clone"])
        run(["run"], self.w.seat, evidence=unfit)
        self.assertEqual((len(calls), len(self.inbox(HOME))), (1, 1))
        self.w.write_main({f"{INST}/d-work/zz-unrelated.md": "main moves\n"})
        rc, out, err = run(["run"], self.w.seat, evidence=unfit)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((len(calls), len(self.inbox(HOME))), (1, 1))
        self.assertIn("refused, already told", out)

    def test_no_evidence_is_taken_in_a_job_holding_a_write_token(self):
        """In GitHub Actions without `AUTOMATON_EVIDENCE_SANDBOX=on` the PR heads' code is never run: home is told once."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        before = self.on_main(f"{INST}/d-work/board/14.md")
        EVIDENCED.clear()
        rc, out, err = run(["run"], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(EVIDENCED, [])
        self.assertEqual(self.on_main(f"{INST}/d-work/board/14.md"), before)
        (msg,) = self.inbox(HOME)
        self.assertIn("not taken in a job holding a write token", msg)
        run(["run"], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(len(self.inbox(HOME)), 1)                                     # told once
        rc, out, err = run(["run"], self.w.seat, GITHUB_ACTIONS="true", AUTOMATON_EVIDENCE_SANDBOX="on")
        self.assertEqual(len(EVIDENCED), 1, out + err)
        self.assertEqual(am.board().phase_name(self.entry(14)), "done-ready")

    def test_a_hanging_ls_remote_costs_the_run_nothing_else(self):
        """A timeout reading a live head proposes nothing for that row; the merge and close acts stand."""
        files = dict(self.files)
        files.update({k: v for k, v in self.verifying_row(14, "verifying", [(7, self.sha)]).items() if "_cos" not in k})
        self.w.write_main(files)
        def hang(repo, n):
            raise subprocess.TimeoutExpired(["git", "ls-remote"], 1)
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}), \
             unittest.mock.patch.object(am.steps, "live_head", hang):
            _, acts = am.plan(self.w.seat)
        self.assertEqual([a[:2] for a in acts], [("merge", 9)])

    def test_a_moved_head_withdraws_the_question_and_is_reverified(self):
        """X6 (the #572 #650 replay): a done-asked entry whose PR moved after the question goes back to verifying, the
        new head recorded, the question and evidence withdrawn, the holder told; then X5 verifies the new head in the
        same run."""
        self.w.write_main(self.verifying_row(14, "done-asked", [(7, self.sha)], "Y/N: Done with #14 row 14 (merges PR #7)?", EV))
        moved = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual(out.strip(), f"head-moved #14 from done-asked: PR #7 now at {moved}")
        EVIDENCED.clear()
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        log = git(self.w.origin, "log", "-2", "--format=%s", "main").splitlines()
        self.assertIn("head-moved (done-asked -> verifying)", log[1]); self.assertIn("verifying -> done-ready", log[0])
        reports = [m for m in self.inbox(HOME) if "kind: report" in m]
        self.assertTrue(any(f"row #14 verifying: PR #7 moved to {moved}" in m for m in reports), reports)
        self.assertEqual(len(EVIDENCED), 1)
        f = self.entry(14)
        b = am.board()
        self.assertEqual(b.pr_list(b.phase_of(f["phase"])[1]), [(7, moved)])
        self.assertEqual(b.phase_name(f), "done-ready"); self.assertNotIn("question", f)   # asked again by home, on the new head
        rc, out, _ = run(["run"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")

    def test_two_moved_prs_are_both_recorded_then_verified(self):
        """X6: one head-moved per moved PR, the first from the recorded phase, the second through verifying's own
        self-loop; both new heads recorded, then X5 verifies the pair in the same run."""
        eight = self.w.pr(8, "dyad/zz-eight.txt", "eight\n")
        self.w.write_main(self.verifying_row(14, "done-asked", [(7, self.sha), (8, eight)],
                                             "Y/N: Done with #14 row 14 (merges PR #7, #8)?", EV))
        seven2 = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        eight2 = self.w.pr(8, "dyad/zz-eight.txt", "eight moved\n")
        EVIDENCED.clear()
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        log = git(self.w.origin, "log", "-3", "--format=%s", "main").splitlines()
        self.assertIn("head-moved (done-asked -> verifying)", log[2])
        self.assertIn("head-moved (verifying -> verifying)", log[1])
        self.assertIn("verifying -> done-ready", log[0])
        f = self.entry(14)
        b = am.board()
        self.assertEqual(b.pr_list(b.phase_of(f["phase"])[1]), [(7, seven2), (8, eight2)])
        self.assertEqual((b.phase_name(f), len(EVIDENCED)), ("done-ready", 1))
        self.assertNotIn("question", f)

    def test_a_moved_head_after_a_recorded_y_done_is_withdrawn_not_caught_up(self):
        """The #572 replay: the Y done recorded at done-asked on the old head, then the head moves. The Y is void
        (Rule-2), so no catch-up: head-moved takes the entry back to verifying with the new head and no question, the
        merge is refused and home told once, and X5 leaves the row to home."""
        files = dict(self.files)
        files[f"{INST}/d-work/board/9.md"] = self.phased(9, "done-asked", {"unit": [self.ENG], "pr": [f"7 at {self.sha}"],
                                                                         "evidence": [EV]},
                                                       "Y/N: Done with #9 row 9 (accreted #10, merges PR #7)?")
        self.w.write_main(files)
        moved = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        EVIDENCED.clear()
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("caught up", out)
        f = self.entry(9)
        b = am.board()
        self.assertEqual((b.phase_name(f), b.pr_list(b.phase_of(f["phase"])[1])), ("verifying", [(7, moved)]))
        self.assertNotIn("question", f)
        self.assertEqual(EVIDENCED, [])
        refusals = [m for m in self.inbox(HOME) if "refused for row #9" in m]
        self.assertEqual(len(refusals), 1, self.inbox(HOME))
        self.assertIn("board #9 phase verifying: Y done recorded by hand", out)

    def test_a_moved_head_withdraws_the_batch_question_from_its_other_rows(self):
        """X6 for a batch: rows #14 and #15 share one Done question; PR #7 of #14 moves. #14 goes back to verifying
        (then X5 re-verifies it); #15, whose own head did not move, steps back to done-ready with no question."""
        eight = self.w.pr(8, "dyad/zz-eight.txt", "eight\n")
        q = "Y/N: Done with #14 row 14, #15 row 15 (merges PR #7, #8)?"
        files = self.verifying_row(14, "done-asked", [(7, self.sha)], q, EV)
        files.update(self.verifying_row(15, "done-asked", [(8, eight)], q, EV))
        self.w.write_main(files)
        moved = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertIn(f"withdrawn #15 from done-asked: the batch Done question it shares is void (PR #7 of #14 moved to {moved[:12]})", out)
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        b = am.board()
        f14, f15 = self.entry(14), self.entry(15)
        self.assertEqual(b.pr_list(b.phase_of(f14["phase"])[1]), [(7, moved)])
        self.assertNotIn("question", f14)
        self.assertEqual((b.phase_name(f15), b.pr_list(b.phase_of(f15["phase"])[1])), ("done-ready", [(8, eight)]))
        self.assertNotIn("question", f15)
        self.assertEqual(b.first(b.phase_of(f15["phase"])[1], "evidence"), EV)           # its own heads' evidence kept
        self.assertIn("PR #7 of #14 moved to", f15["note"])
        self.assertTrue(any("row #15 done-ready: the batch Done question naming it was withdrawn" in m for m in self.inbox(HOME)))

    def test_an_abbreviated_recorded_head_is_not_a_move(self):
        self.w.write_main(self.verifying_row(14, "done-ready", [(7, self.sha[:8])], evidence=EV))
        rc, out, _ = run(["scan"], self.w.seat)
        self.assertEqual(out.strip(), "nothing to do")

    # ---- #587 X10: evidence computed in a sandbox job, fired by the write job from its artifact
    def evidence_file(self, *lines):
        f = SCRATCH.mkdtemp() / "evidence.jsonl"
        f.write_text("".join(l + "\n" for l in lines))
        return f

    def test_evidence_out_writes_the_verdict_and_fires_nothing(self):
        """`evidence --out`: one JSON line per evidence act, and main, the board and every inbox untouched; `run
        --evidence-from` in a write-token job then fires it without running any evidence itself."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        before = git(self.w.origin, "rev-parse", "main")
        f = SCRATCH.mkdtemp() / "evidence.jsonl"
        EVIDENCED.clear()
        rc, out, err = run(["evidence", "--out", str(f)], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(len(EVIDENCED), 1)
        self.assertEqual(am.json.loads(f.read_text()), {"rid": 14, "event": "evidence-verified", "evidence": EV,
                                                         "heads": [[7, self.sha]]})
        self.assertEqual(len(f.read_text().splitlines()), 1)
        self.assertEqual(git(self.w.origin, "rev-parse", "main"), before)                  # nothing landed, nothing posted
        self.assertEqual(self.inbox(HOME), [])
        EVIDENCED.clear()
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(EVIDENCED, [])                                                   # served, never computed
        g = self.entry(14)
        b = am.board()
        self.assertEqual((b.phase_name(g), b.first(b.phase_of(g["phase"])[1], "evidence")), ("done-ready", EV))
        self.assertIn("[evidence file, line 1]", out)
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(out.strip(), "evidence line 1 dropped: row #14 has no evidence act at those heads now")

    def test_evidence_out_is_refused_in_a_job_holding_a_write_token(self):
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        f = SCRATCH.mkdtemp() / "evidence.jsonl"
        EVIDENCED.clear()
        rc, out, err = run(["evidence", "--out", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 1)
        self.assertIn("never in a job holding a write token", err)
        self.assertFalse(f.exists()); self.assertEqual(EVIDENCED, [])
        rc, out, err = run(["evidence", "--out", str(f)], self.w.seat, GITHUB_ACTIONS="true", AUTOMATON_EVIDENCE_SANDBOX="on")
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(f.exists())

    def test_a_row_with_no_line_is_left_not_computed_nor_told(self):
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        before = self.on_main(f"{INST}/d-work/board/14.md")
        EVIDENCED.clear()
        rc, out, err = run(["run", "--evidence-from", str(self.evidence_file())], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"evidence #14: no line for the combined evidence of PR #7 at {self.sha[:12]} in the evidence file", out)
        self.assertEqual((EVIDENCED, self.on_main(f"{INST}/d-work/board/14.md"), self.inbox(HOME)), ([], before, []))
        rc, out, err = run(["run", "--evidence-from", str(SCRATCH.mkdtemp() / "absent.jsonl")], self.w.seat,
                           GITHUB_ACTIONS="true")                                     # a missing artifact costs the run nothing
        self.assertEqual(rc, 0, out + err)
        self.assertIn("unreadable (FileNotFoundError); nothing fired from it", out)

    def test_a_moved_head_drops_the_line(self):
        """The line's heads are re-checked: a PR that moved after the evidence job is `head-moved`, and the stale line is
        dropped rather than fired onto the new head."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        f = self.evidence_file(am.json.dumps({"rid": 14, "event": "evidence-verified", "evidence": EV, "heads": [[7, self.sha]]}))
        moved = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("evidence line 1 dropped: row #14's heads are not the board's recorded and live heads", out)
        g = self.entry(14)
        b = am.board()
        self.assertEqual((b.phase_name(g), b.pr_list(b.phase_of(g["phase"])[1])), ("verifying", [(7, moved)]))
        base = git(self.w.seat, "rev-parse", "origin/main")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}):
            self.assertIsNone(am.heads_problem(self.w.seat, base, 14, [(7, moved)]))
            self.assertIn("records other heads", am.heads_problem(self.w.seat, base, 14, [(7, self.sha)]))
            self.assertIn("lists other PRs", am.heads_problem(self.w.seat, base, 14, [(8, moved)]))
            self.assertIn("has no board entry", am.heads_problem(self.w.seat, base, 99, [(7, moved)]))
            later = self.w.pr(7, "dyad/zz-pr.txt", "later\n")                         # live moved, board not yet
            self.assertIn(f"PR #7 is no longer at {moved[:12]}", am.heads_problem(self.w.seat, base, 14, [(7, moved)]))
        self.assertNotEqual(later, moved)

    def test_evidence_out_takes_a_moved_rows_live_heads_and_run_fires_them_after_head_moved(self):
        self.w.write_main(self.verifying_row(14, "done-asked", [(7, self.sha)], "Y/N: Done with #14 row 14 (merges PR #7)?", EV))
        moved = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        f = SCRATCH.mkdtemp() / "evidence.jsonl"
        rc, out, err = run(["evidence", "--out", str(f)], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(am.json.loads(f.read_text())["heads"], [[7, moved]])
        EVIDENCED.clear()
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(EVIDENCED, [])
        log = git(self.w.origin, "log", "-2", "--format=%s", "main").splitlines()
        self.assertIn("head-moved (done-asked -> verifying)", log[1]); self.assertIn("verifying -> done-ready", log[0])

    def test_a_null_verdict_is_told_to_home_once_never_fired(self):
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        f = SCRATCH.mkdtemp() / "evidence.jsonl"
        unfit = lambda repo, sha: (2, ["FAIL [evidence] a shallow clone"])
        rc, out, err = run(["evidence", "--out", str(f)], self.w.seat, evidence=unfit)
        self.assertEqual(rc, 0, out + err)
        self.assertIsNone(am.json.loads(f.read_text())["event"])
        before = self.on_main(f"{INST}/d-work/board/14.md")
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.on_main(f"{INST}/d-work/board/14.md"), before)
        (msg,) = self.inbox(HOME)
        self.assertIn("refused for row #14: FAIL [evidence] a shallow clone (exit 2)", msg)
        run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(len(self.inbox(HOME)), 1)

    def test_evidence_lines_are_checked_strictly(self):
        """The file is another job's artifact, written after the PR heads' code ran: every line is checked, a bad one
        dropped with a reason that echoes nothing it holds."""
        sha, d = "a" * 40, am.json.dumps
        good = {"rid": 14, "event": "evidence-failed", "note": "x", "heads": [[7, sha]]}
        bad = ["{not json", d([1]), d(good | {"event": "answered-Y"}), d(good | {"EVIL": 1}), d(good | {"rid": True}),
               d(good | {"rid": "14"}), d(good | {"heads": [[7, "abc123"]]}), d(good | {"heads": [[7, sha], [7, sha]]}),
               d(good | {"heads": []}), d({"rid": 14, "event": "evidence-verified", "evidence": "f" * 63, "heads": [[7, sha]]}),
               d(good | {"note": " "}), d(good | {"event": ["evidence-failed"]}), d({"rid": 14, "heads": [[7, sha]], "note": "x"})]
        pending, dropped = am.read_evidence(self.evidence_file(*bad, "", d(good | {"rid": 15}), d(good | {"rid": 16}), d(good | {"rid": 16})))
        self.assertEqual(list(pending), [15])
        self.assertEqual(len(dropped), len(bad) + 2, dropped)
        self.assertTrue(all("EVIL" not in l and "answered" not in l for l in dropped), dropped)
        self.assertIn("evidence line 3 dropped: not an evidence event of the machine's table", dropped)
        self.assertEqual(dropped[-1], f"evidence line {len(bad) + 4} dropped: row #16 is named by 2 lines")
        big = SCRATCH.mkdtemp() / "big.jsonl"; big.write_text("x" * (am.EVIDENCE_FILE_BYTES + 1))
        self.assertEqual(am.read_evidence(big)[0], {})
        deep = self.evidence_file("[" * 100000, d(good | {"rid": 15}))                # recurses past the stack in json
        self.assertEqual((list(am.read_evidence(deep)[0]), am.read_evidence(deep)[1]),
                         ([15], ["evidence line 1 dropped: not JSON"]))
        pending, dropped = am.read_evidence(SCRATCH.mkdtemp())                       # a directory, a FIFO: never read
        self.assertEqual(pending, {}); self.assertIn("not a regular file; nothing fired from it", dropped[0])
        # a well-formed line for a row that is not in verifying is dropped by the run, never fired
        self.w.write_main(self.verifying_row(14, "done-ready", [(7, self.sha)], evidence=EV))
        before = git(self.w.origin, "rev-parse", "main")
        f = self.evidence_file(d({"rid": 14, "event": "evidence-failed", "note": "forged", "heads": [[7, self.sha]]}))
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(out.strip(), "evidence line 1 dropped: row #14 has no evidence act at those heads now")
        self.assertEqual(git(self.w.origin, "rev-parse", "main"), before)

    def test_a_deeply_nested_evidence_line_costs_the_run_none_of_its_merges(self):
        self.w.write_main(self.files)
        f = self.evidence_file("[" * 100000)
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("evidence line 1 dropped: not JSON", out)
        self.assertIn(f"merged PR #7 at {self.sha}", out)
        self.assertIn("state: done", self.on_main(f"{INST}/d-work/rows/9.md"))

    def test_evidence_out_reads_an_unmoved_prs_full_live_head_beside_a_moved_one(self):
        """A moved two-PR row whose unmoved PR the board records abbreviated: the line carries both full live heads, so
        `run --evidence-from` fires it after head-moved rather than dropping it."""
        eight = self.w.pr(8, "dyad/zz-eight.txt", "eight\n")
        self.w.write_main(self.verifying_row(14, "done-ready", [(7, self.sha), (8, eight[:8])], evidence=EV))
        moved = self.w.pr(7, "dyad/zz-pr.txt", "moved\n")
        f = SCRATCH.mkdtemp() / "evidence.jsonl"
        rc, out, err = run(["evidence", "--out", str(f)], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(am.json.loads(f.read_text())["heads"], [[7, moved], [8, eight]])
        rc, out, err = run(["run", "--evidence-from", str(f)], self.w.seat, GITHUB_ACTIONS="true")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("[evidence file, line 1]", out)
        self.assertEqual(am.board().phase_name(self.entry(14)), "done-ready")

    def test_a_long_refusal_still_writes_an_admissible_note(self):
        """A no-verdict note is what `escalate` keeps (first line, 300 characters), so a long `git merge-tree` refusal
        passes `evidence_line_problem` and reaches home."""
        self.w.write_main(self.verifying_row(14, "verifying", [(7, self.sha)]))
        base = git(self.w.seat, "rev-parse", "origin/main")
        long = am.Refused("git merge-tree exited 128: " + "x" * 5000 + "\nsecond line")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}), \
             unittest.mock.patch.object(am, "evidence_event", side_effect=long):
            rec, _ = am.evidence_verdict(self.w.seat, base, 14, [(7, self.sha)])
        self.assertIsNone(am.evidence_line_problem(rec))
        self.assertEqual(rec["note"], ("git merge-tree exited 128: " + "x" * 5000)[:300])
        self.assertEqual((am.home_note("\n  \n"), am.home_note("\n a \nb")), ("no reason given", "a"))

    def test_plan_parts_and_part_for(self):
        parts = am.plan_parts("# Plan\nParts: engineer: a; counsel-0032b4c0: b; bad\n")
        self.assertEqual(parts, {"engineer": "a", "counsel-0032b4c0": "b"})
        self.assertEqual((am.part_for(parts, "engineer-1537d8fb"), am.part_for(parts, "counsel-0032b4c0"),
                          am.part_for(parts, "audit-e73be78c")), ("a", "b", None))
        self.assertEqual(am.plan_parts("# Plan\n"), {})
        self.assertNotRegex(am.notice_body(1, "after 2026-11-02 Y plan (x)"), r"\d{4}-\d{2}-\d{2} Y plan")   # masked as post masks

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

    def test_a_landed_cut_is_corroborated_once(self):
        self.w.write_main(self.files)
        before = git(self.w.origin, "rev-parse", "main")
        CORROBORATED.clear()
        rc, out, err = run(["run"], self.w.seat)
        self.assertEqual(rc, 0, out + err)
        (b, a), = CORROBORATED
        self.assertEqual(b, before)
        self.assertIn(f"corroborated row #9's cut at {a[:12]}", out)
        self.assertIn(self.sha, git(self.w.origin, "rev-list", "--parents", "-n", "1", a))

    def test_a_failed_corroboration_is_told_and_the_run_exits_1(self):
        self.w.write_main(self.files)
        failing = lambda repo, before, after: (False, ["ok   [corroborate] check", "FAIL [corroborate] build: boom"])
        rc, out, err = run(["run"], self.w.seat, corroborate=failing)
        self.assertEqual(rc, 1, out + err)
        (msg,) = self.inbox(HOME)
        self.assertIn("corroboration of the landed cut refused for row #9: FAIL [corroborate] build: boom", msg)

    def sweep(self, check=(), hygiene=((), ()), inflight=(), argv=("sweep", "--row", "9"), audit=(), check_lines=(), **kw):
        seen = self.swept = []
        def fake_check(wt, stores=False):
            seen.append(stores); am.CHECK_LINES[:] = list(check_lines); return list(check)
        with unittest.mock.patch.object(am, "sweep_check", fake_check), \
             unittest.mock.patch.object(am.hygiene_mod, "hygiene", lambda repo, base, now, prefs=None: (list(hygiene[0]), list(hygiene[1]))), \
             unittest.mock.patch.object(am.hygiene_mod, "inflight_cabinets", lambda repo, base, now, pulls, prefs=None:
                                        [l if isinstance(l, tuple) else ("program", l) for l in inflight]), \
             unittest.mock.patch.object(am, "sweep_pulls", lambda: None), \
             unittest.mock.patch.object(am, "sweep_drift", lambda repo, wt, base: [(False, "finding: drift seen")]), \
             unittest.mock.patch.object(am, "sweep_audit", lambda wt: list(audit)), \
             unittest.mock.patch.object(am, "sweep_ci", lambda repo, base, now, prefs=None: []):
            return run(list(argv), self.w.seat, **kw)

    def stalls(self, hygiene=((), ()), inflight=(), cabinet=None):
        """`stall_lines` on origin/main with hygiene and in-flight stubbed, the ledger read for real (#617)."""
        git(self.w.seat, "fetch", "-q", "origin")
        base = git(self.w.origin, "rev-parse", "main")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "AUTOMATON_HOME": "", "GITHUB_TOKEN": ""}), \
             unittest.mock.patch.object(am.hygiene_mod, "hygiene", lambda repo, base, now, prefs=None: (list(hygiene[0]), list(hygiene[1]))), \
             unittest.mock.patch.object(am.hygiene_mod, "inflight_cabinets", lambda repo, base, now, pulls, prefs=None:
                                        [l if isinstance(l, tuple) else ("program", l) for l in inflight]), \
             unittest.mock.patch.object(am, "sweep_ci", lambda repo, base, now, prefs=None: []):
            return am.stall_lines(self.w.seat, base, cabinet=cabinet)

    def test_the_sweep_tells_only_what_is_new(self):
        files = dict(self.files)
        files[f"{INST}/d-work/rows/9.md"] = ROW.format(id=9, state="planned",
            disposed=f"2026-11-02 Y plan; 2026-11-01 Y done (accreted #10, merges PR #7 at {self.sha})")
        self.w.write_main(files)
        rc, out, err = self.sweep(check=[(False, "warn [agent/plans] 43.md: an old warning")])
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("names heads not on main", out)                          # #617: a stall, the home's read now
        self.assertIn("finding: warn [agent/plans] 43.md: an old warning", out); self.assertIn("finding: drift seen", out)
        (msg,) = self.inbox(HOME)
        self.assertIn("automaton sweep at", msg); self.assertIn(", findings: ", msg)
        self.assertIn("43.md: an old warning", msg)
        rc, out, _ = self.sweep(check=[(False, "warn [agent/plans] 43.md: an old warning")])
        self.assertIn("0 new", out); self.assertEqual(len(self.inbox(HOME)), 1)            # told once
        rc, out, _ = self.sweep(check=[(True, "FAIL [agent/rows] broken")])
        self.assertEqual(rc, 1, out); self.assertEqual(len(self.inbox(HOME)), 2)           # a new failure is told
        self.assertEqual(run(["sweep", "--row"], self.w.seat)[0], 2)
        self.assertEqual(self.swept, [False])                                             # the full check

    def test_readings_print_first_and_findings_in_two_groups(self):
        """#619 Decision 1: readings first, never posted or counted; then `standing` and `new`."""
        self.w.write_main(self.files)
        audit = ["reading: audit watermark: tree t; none: first exercise", "finding: audit fences: guard a/b is in v1 and not in the registry"]
        rc, out, err = self.sweep(check=[(False, "warn [agent/plans] 43.md: old")], audit=audit)
        lines = out.splitlines()                         # the inbox verb's own lines print as the notice lands
        self.assertEqual(rc, 0, out + err)
        i = lines.index(audit[0])
        self.assertEqual(lines[i + 1:i + 5], ["standing: 0 finding(s) already told to the home", "new: 3 finding(s) not yet told",
                                      "finding: warn [agent/plans] 43.md: old", "finding: drift seen"])
        self.assertIn(audit[1], lines)
        (msg,) = self.inbox(HOME); self.assertNotIn("first exercise", msg); self.assertIn("guard a/b", msg)
        rc, out, _ = self.sweep(check=[(False, "warn [agent/plans] 43.md: old")], audit=audit)
        self.assertIn("standing: 3 finding(s) already told to the home", out); self.assertIn("new: 0 finding(s) not yet told", out)
        self.assertEqual(len(self.inbox(HOME)), 1)

    def test_with_no_row_the_sweep_is_the_report_and_lands_nothing(self):
        """#619 Decision 1: the stall block, checks-sha256 over the tree's own check lines, report-sha256 over the
        text, the text stored; nothing posted, nothing landed."""
        self.w.write_main(self.files)
        before = git(self.w.origin, "rev-parse", "main")
        kw = dict(check=[(False, "warn [y] two")], check_lines=["ok   [x] one", "warn [y] two"], argv=("sweep",))
        rc, out, err = self.sweep(hygiene=(["hygiene I1 untouched: backlog row #10 (t), no commit in 40 days"], []), **kw)
        rc2, out2, _ = self.sweep(**kw)
        lines = out.splitlines()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("finding: hygiene I1 untouched: backlog row #10 (t), no commit in 40 days", lines)   # the stall block
        self.assertTrue(any(l.startswith("stalls: ") for l in lines))
        import hashlib
        self.assertIn(f"checks-sha256={hashlib.sha256(b'ok   [x] one' + chr(10).encode() + b'warn [y] two').hexdigest()}", lines)
        rep = next(l for l in lines if l.startswith("report-sha256="))
        body = lines[:lines.index(rep)]
        self.assertEqual(rep, f"report-sha256={hashlib.sha256(chr(10).join(body).encode()).hexdigest()}")
        stored = Path(lines[-1].removeprefix("stored: "))
        self.assertEqual(stored.read_text(), "\n".join(lines[:-1]) + "\n")
        self.assertEqual(next(l for l in out2.splitlines() if l.startswith("checks-sha256=")),
                         next(l for l in lines if l.startswith("checks-sha256=")))     # same head, same checks
        self.assertEqual(self.inbox(HOME), []); self.assertEqual(git(self.w.origin, "rev-parse", "main"), before)
        self.assertIn("not told (no --row or no home)", out)

    def test_the_stores_sweep_runs_the_guards_alone_and_tells_only_what_is_new(self):
        """#617: `sweep --stores` runs `check --guards` (stores=True), no drift and no events, told new-only."""
        self.w.write_main(self.files)
        rc, out, err = self.sweep(check=[(False, "warn [agent/plans] 43.md: an old warning")], argv=("sweep", "--stores", "--row", "9"))
        self.assertEqual(rc, 0, out + err); self.assertEqual(self.swept, [True])
        self.assertNotIn("drift seen", out); self.assertNotIn("events:", out); self.assertIn("stores sweep of main", out)
        (msg,) = self.inbox(HOME); self.assertIn("automaton stores sweep at", msg); self.assertIn("43.md: an old warning", msg)
        rc, out, _ = self.sweep(check=[(False, "warn [agent/plans] 43.md: an old warning")])   # the full sweep: told already
        self.assertEqual(len(self.inbox(HOME)), 2)                                 # only the drift line is new to it
        self.assertNotIn("43.md", self.inbox(HOME)[-1])
        for bad in (("sweep", "--stores", "--stores"), ("sweep", "--stores", "--row"), ("sweep", "--bogus")):
            self.assertEqual(run(list(bad), self.w.seat)[0], 2, bad)

    def test_sweep_check_stores_runs_the_guards_with_no_suite(self):
        seen = []
        def fake(argv, **kw):
            seen.append((argv, kw.get("env", {}).get("DYAD_NO_NESTED_TESTS")))
            return subprocess.CompletedProcess(argv, 0, "ok   [guards] x\nwarn [guards] y z\n", "ERROR: test_e (m.C.test_e) — e\n")
        with unittest.mock.patch.object(am.subprocess, "run", fake), \
             unittest.mock.patch.object(am, "sweep_live", lambda wt: [(True, "FAIL [suite:live] r: one")]):   # #618 H4
            got = am.sweep_check(PKG.parent, stores=True)
            am.sweep_check(PKG.parent)
        self.assertEqual(got, [(False, "warn [guards] y z"), (True, "ERROR: test_e (m.C.test_e) — e"),
                               (True, "FAIL [suite:live] r: one")])                     # suite:live after the guards
        self.assertEqual([a[2:] for a, _ in seen], [["check", "--guards"], ["check"]])
        self.assertEqual(seen[0][1], "1")                                         # the suite never runs under --stores

    def test_check_readings_carry_the_suite_and_the_invariant_pass(self):
        """#619: the self-diagnostic reads both in the report; none printed when the check printed neither."""
        lines = ["ok   [invariant] a (3)", "FAIL [invariant] b: x", "     [Rule-12] dyad/tests: Ran 9 tests OK", "ok   [g] y"]
        self.assertEqual(am.check_readings(lines), ["reading: suite dyad/tests: Ran 9 tests OK", "reading: invariants 1 ok, 1 FAIL"])
        self.assertEqual(am.check_readings(["ok   [g] y"]), [])

    def test_the_live_listing_keeps_only_livecase_tests(self):
        """#618 H4: `suite:live` is every `livetest.LiveCase` test of a root, listed by the runner's child."""
        with tempfile.TemporaryDirectory() as t:
            Path(t, "test_m.py").write_text("import unittest, livetest\nclass A(livetest.LiveCase):\n    def test_a(self): pass\n"
                                            "class B(unittest.TestCase):\n    def test_b(self): pass\n")
            r = subprocess.run([sys.executable, "-c", am.LIVE_LIST_CHILD, t, str(PKG / "scripts")], capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout.split()), (0, ["test_m.A.test_a"]), r.stderr)

    def test_the_sweep_no_longer_posts_stalls_and_stall_lines_reads_them(self):
        """#617: hygiene, candidates and in-flight lines are `stall_lines`', which `board resume` prints; the sweep
        posts none of them."""
        files = dict(self.files)
        files[f"{INST}/d-work/rows/9.md"] = ROW.format(id=9, state="planned",
            disposed=f"2026-11-02 Y plan; 2026-11-01 Y done (accreted #10, merges PR #7 at {self.sha})")
        self.w.write_main(files)
        hyg = (["hygiene I1 untouched: backlog row #10 (ten), no commit in 40 days"], ["candidate: #9 and #10 similar (0.50): nine / ten"])
        flight = ["inflight W9 operator wait: row #9 waits on the operator with no question recorded"]
        rc, out, err = self.sweep(hygiene=hyg, inflight=flight)
        self.assertEqual(rc, 0, out + err)
        self.assertFalse(any(k in out for k in ("hygiene I1", "candidate:", "inflight W9", "names heads not on main")), out)
        self.assertFalse(any("hygiene" in m or "work in flight" in m for m in self.inbox(HOME)))
        got = self.stalls(hyg, flight)
        self.assertIn(f"finding: row #9's done answer of 2026-11-01 names heads not on main: PR #7 at {self.sha[:12]}", got)
        self.assertIn("finding: hygiene I1 untouched: backlog row #10 (ten), no commit in 40 days", got)
        self.assertIn("finding: inflight W9 operator wait: row #9 waits on the operator with no question recorded", got)
        self.assertEqual(got[-1], "candidate: #9 and #10 similar (0.50): nine / ten")
        self.assertEqual(self.inbox(HOME)[-1:], self.inbox(HOME)[-1:])            # read-only: nothing posted by it

    def two_cabinets(self):
        """#594: B's cabinet beside A's — `_cos-bob.md` held by B's leader, row 12 filed under `program-bob`."""
        files = dict(self.files)
        files.update({f"{INST}/d-work/board/_cos-bob.md": f"holder: {BOB}\nwriter: h2\n",
                      f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="open", disposed="2026-11-02 Y open"),
                      f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y open\n\n```\nY\n```\n\n",
                      f"{INST}/d-work/board/12.md": f"holder: {BOB}\ncabinet: program-bob\nwaiting-on: operator\nwriter: h2\n"})
        self.w.write_main(files)

    def test_home_is_per_cabinet(self):
        self.two_cabinets()
        base = git(self.w.origin, "rev-parse", "main")
        git(self.w.seat, "fetch", "-q", "origin")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "AUTOMATON_HOME": ""}):
            self.assertEqual((am.home(self.w.seat, base, "program"), am.home(self.w.seat, base, "program-bob"),
                              am.home(self.w.seat, base, "program-eve")), (HOME, BOB, HOME))   # no _cos-eve: program's
            with self.assertRaises(TypeError):
                am.home(self.w.seat, base)                                    # no default: a missed site fails loudly
            self.assertEqual((am.row_cabinet(self.w.seat, base, 12), am.row_cabinet(self.w.seat, base, 9),
                              am.row_cabinet(self.w.seat, base, 10)), ("program-bob", "program", "program"))
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "AUTOMATON_HOME": "ops-1"}):
            self.assertEqual(am.home(self.w.seat, base, "program-bob"), "ops-1")       # the override wins

    def test_escalate_for_a_row_of_bs_cabinet_posts_to_bs_home(self):
        self.two_cabinets()
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "AUTOMATON_HOME": ""}):
            got = am.escalate(self.w.seat, 12, "a test act", "because")
        self.assertIn(f"posted a notice to {BOB} (row #12)", got)
        (msg,) = self.inbox(BOB)
        self.assertIn("automaton: a test act refused for row #12: because", msg)
        self.assertEqual(self.inbox(HOME), [])

    def eve_entry(self):
        """#594: row 12 filed under `program-eve`, a cabinet with no `_cos-eve.md` and so no holder of its own."""
        files = dict(self.files)
        files.update({f"{INST}/d-work/rows/12.md": ROW.format(id=12, state="open", disposed="2026-11-02 Y open"),
                      f"{INST}/d-work/provenance/12.md": "# Provenance #12\n\n## 1 disposition 2026-11-02 Y open\n\n```\nY\n```\n\n",
                      f"{INST}/d-work/board/12.md": "holder: program-eve-dddddddd\ncabinet: program-eve\nwaiting-on: operator\nwriter: h3\n"})
        self.w.write_main(files)

    def test_a_cabinet_with_no_home_falls_back_to_programs(self):
        self.eve_entry()
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "AUTOMATON_HOME": ""}):
            got = am.escalate(self.w.seat, 12, "a test act", "because")
        self.assertIn(f"posted a notice to {HOME} (row #12)", got)
        (msg,) = self.inbox(HOME)
        self.assertIn("automaton: a test act refused for row #12: because", msg)
        line = "inflight W9 operator wait: row #12 waits on the operator with no question recorded"
        self.assertIn(f"finding: {line}", self.stalls(inflight=[("program-eve", line)], cabinet="program"))   # program's read

    def test_stall_lines_show_each_cabinets_home_its_own_lines(self):
        self.two_cabinets()
        flight = [("program-bob", "inflight W9 operator wait: row #12 waits on the operator with no question recorded"),
                  ("program", "inflight W9 operator wait: row #9 waits on the operator with no question recorded")]
        b, a = self.stalls(inflight=flight, cabinet="program-bob"), self.stalls(inflight=flight, cabinet="program")
        self.assertTrue(any("row #12 waits" in l for l in b)); self.assertFalse(any("row #9 waits" in l for l in b))
        self.assertTrue(any("row #9 waits" in l for l in a)); self.assertFalse(any("row #12 waits" in l for l in a))
        self.assertEqual(len([l for l in self.stalls(inflight=flight) if "W9" in l]), 2)   # no cabinet: every line

    def test_run_reports_a_landed_merge_for_its_job(self):
        """#617: `landed_report` writes the job's outputs, and the line names the last merge."""
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "o"
            with unittest.mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(out)}):
                self.assertEqual(am.landed_report([]), "landed: 0 merge(s)")
                self.assertEqual(am.landed_report(["a" * 40, "b" * 40]), "landed: 2 merge(s), the last at bbbbbbbbbbbb")
            self.assertEqual(out.read_text(), "landed=false\nlanded-at=\nlanded=true\nlanded-at=" + "b" * 40 + "\n")
        with unittest.mock.patch.dict(os.environ, {"GITHUB_OUTPUT": ""}):
            self.assertEqual(am.landed_report([]), "landed: 0 merge(s)")         # no job: the line alone

    def test_a_long_group_is_split_never_cut(self):
        lines = [f"finding: warn [x/y] line {i} " + "z" * 200 for i in range(40)]
        parts = am.notice_parts([am.finding_key(l.removeprefix("finding: ")) for l in lines])
        self.assertGreater(len(parts), 1)
        self.assertEqual(sum(len(p) for p in parts), 40)                          # every line in exactly one part
        self.assertTrue(all(len(" | ".join(p)) < am.NOTICE_CHARS for p in parts))

    def test_the_sweeps_health_run_is_the_automatons_own(self):
        """The sweep reads `released` health as the automaton, a read-only run under its own party (#593)."""
        seen = []
        def fake(argv, **kw):
            seen.append(argv); return subprocess.CompletedProcess(argv, 0, "", "")
        with unittest.mock.patch.object(am.subprocess, "run", fake), unittest.mock.patch.dict(os.environ, {"MIRROR": ""}):
            am.sweep_drift(PKG.parent, PKG.parent, "HEAD")
        self.assertEqual(seen[0][-4:], ["released", "health", "--as", "automaton"])
    HEALTH = ("# Run-book: released\n# sections: Status/health\n\n## Status/health\n```dyad-cmd\nname: health\n"
              "class: read-only\nrole: any\nundo: none\npostcondition: none\nscope: nothing (read)\n\necho '0 entries read'\n```\n")
    EVENTS = "workstation-corpus/runbooks/events/released.jsonl"

    def real_drift_sweep(self, argv=("sweep", "--row", "9")):
        """The sweep with its real `released` health run in the swept worktree; every other kind of finding stubbed."""
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_RUNBOOKS", "DYAD_HOST", "MIRROR")}
        with unittest.mock.patch.dict(os.environ, env, clear=True), \
             unittest.mock.patch.object(am, "sweep_check", lambda wt, stores=False: []), \
             unittest.mock.patch.object(am, "sweep_audit", lambda wt: []), \
             unittest.mock.patch.object(am.hygiene_mod, "hygiene", lambda repo, base, now, prefs=None: ([], [])), \
             unittest.mock.patch.object(am.hygiene_mod, "inflight", lambda repo, base, now, pulls, prefs=None: []), \
             unittest.mock.patch.object(am, "sweep_pulls", lambda: None), \
             unittest.mock.patch.object(am, "sweep_ci", lambda repo, base, now, prefs=None: []):
            return run(list(argv), self.w.seat)

    def test_the_sweeps_health_event_lands_events_only(self):
        """#593 DoD 2: the sweep's own `released` health run, recorded under `role: automaton`, reaches main as an
        events-only commit that cites no d-work; an identical second reading lands nothing."""
        self.w.write_main({**self.files, "workstation-corpus/runbooks/released.md": self.HEALTH})
        before = git(self.w.origin, "rev-parse", "main")
        rc, out, err = self.real_drift_sweep(("sweep",))                          # no --row: nothing lands
        self.assertIn("events: released not landed (no --row", out, out + err)
        self.assertEqual(git(self.w.origin, "rev-parse", "main"), before)
        rc, out, err = self.real_drift_sweep()
        self.assertRegex(out, r"events: released landed on main as [0-9a-f]{12} \(events-only\)", out + err)
        (ev,) = [json.loads(l) for l in self.on_main(self.EVENTS).splitlines()]
        self.assertEqual((ev["role"], ev["instance"], ev["name"], ev["exit"]), ("automaton", "released", "health", 0))
        commits = git(self.w.origin, "rev-list", f"{before}..main").split()
        landed = next(c for c in commits if self.EVENTS in git(self.w.origin, "diff-tree", "--no-commit-id", "--name-only", "-r", c))
        self.assertEqual(git(self.w.origin, "diff-tree", "--no-commit-id", "--name-only", "-r", landed).split(), [self.EVENTS])
        self.assertNotIn("d-work #", git(self.w.origin, "log", "-1", "--format=%B", landed))
        self.assertTrue(dyadlib.events_only(self.w.origin, f"{landed}^1", landed))
        head = git(self.w.origin, "rev-parse", "main")
        rc, out, err = self.real_drift_sweep()                                    # the same reading again
        self.assertIn("events: no new reading to land", out, out + err)
        self.assertEqual(git(self.w.origin, "rev-parse", "main"), head)
        self.assertEqual(len(self.on_main(self.EVENTS).splitlines()), 1)

    def test_a_refused_event_landing_never_fails_the_sweep(self):
        fresh = {self.EVENTS: '{"name": "health", "output_sha256": "x", "exit": 0}\n'}
        def refuse(*a, **kw):
            raise am.Refused("the push failed with main unmoved; nothing landed:\npermission denied")
        with unittest.mock.patch.object(am.land, "land", refuse):
            line = am.land_events(self.w.seat, "workstation-corpus/runbooks/events", fresh, 9)
        self.assertEqual(line, "events: released not landed (the push failed with main unmoved; nothing landed:)")
        with unittest.mock.patch.object(am.land, "land", lambda *a, **kw: 1 / 0):
            self.assertIn("not landed (ZeroDivisionError", am.land_events(self.w.seat, "x", fresh, 9))

    LINE = '{"name": "health", "instance": "released", "output_sha256": "abc", "exit": 0, "role": "automaton"}\n'

    def clean_racer(self, files):
        """The racer at a main holding `files`: a clean worktree to read or build in, with the default event store."""
        self.w.write_main(files)
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_RUNBOOKS", "DYAD_HOST")}
        e = unittest.mock.patch.dict(os.environ, env, clear=True); e.start(); self.addCleanup(e.stop)
        return self.w.racer

    def test_a_rebuild_over_the_same_reading_lands_nothing(self):
        """events_builder on a main whose events file already ends with the same reading: refused, nothing written."""
        wt = self.clean_racer({self.EVENTS: self.LINE})
        with self.assertRaisesRegex(am.Refused, "already landed"):
            am.events_builder({self.EVENTS: self.LINE})(wt)
        self.assertEqual(am.land.written(wt), [])
        self.assertEqual((wt / self.EVENTS).read_text(), self.LINE)
        other = self.LINE.replace('"abc"', '"def"')                      # a different reading is appended
        paths, msg, _ = am.events_builder({self.EVENTS: other})(wt)
        self.assertEqual((paths, msg), ([self.EVENTS], "events: released (automaton sweep)"))
        self.assertEqual((wt / self.EVENTS).read_text(), self.LINE + other)

    def test_new_events_notes_a_rewrite_and_a_removal_and_lands_neither(self):
        wt = self.clean_racer({self.EVENTS: self.LINE})
        (wt / self.EVENTS).write_text(self.LINE.replace('"abc"', '"zzz"'))
        rel, fresh, notes = am.new_events(wt)
        self.assertEqual((rel, fresh), ("workstation-corpus/runbooks/events", {}))
        self.assertEqual(notes, [f"events: {self.EVENTS} changed other than by an append; not landed"])
        (wt / self.EVENTS).unlink()
        self.assertEqual(am.new_events(wt)[1:], ({}, [f"events: {self.EVENTS} removed or not a file; not landed"]))
        (wt / self.EVENTS).write_bytes(self.LINE.encode() + b"\xff\n")
        self.assertEqual(am.new_events(wt)[1:], ({}, [f"events: {self.EVENTS} not read (UnicodeDecodeError); not landed"]))

    def test_a_removed_events_file_never_stops_the_sweeps_findings(self):
        """An events file deleted in the swept worktree is one note; the findings and the summary still print."""
        self.w.write_main({**self.files, self.EVENTS: self.LINE})
        def drift(repo, wt, base):
            (wt / self.EVENTS).unlink(); return [(True, "finding: released: no tag: x")]
        with unittest.mock.patch.object(am, "sweep_drift", drift):
            rc, out, err = self.real_drift_sweep()
        self.assertEqual(rc, 1, out + err)
        self.assertIn("finding: released: no tag: x", out)
        self.assertIn(f"events: {self.EVENTS} removed or not a file; not landed", out)
        self.assertIn("events: no new reading to land", out)
        self.assertIn("sweep of main", out)
        with unittest.mock.patch.object(am, "sweep_drift", lambda repo, wt, base: []), \
             unittest.mock.patch.object(am, "new_events", lambda wt: 1 / 0):
            rc, out, err = self.real_drift_sweep()
        self.assertIn("events: not read (ZeroDivisionError); not landed", out, out + err)
        self.assertIn("sweep of main", out)

    def test_a_refusal_reason_carries_the_failing_lines_never_empty(self):
        """#592: a failed push's refusal ends its first line with a colon and puts the hook's output after it; the
        notice carried only that first line, so its reason read empty."""
        why = ("the push failed with main unmoved; nothing landed:\n"
               "ok   [guards] agent/rules (19 Rules)\n"
               "FAIL [guards] agent/traces 584.md: a stored preview\n"
               "FAIL [guards] agent/traces 585.md: a stored preview\n"
               "error: failed to push some refs to 'origin'")
        r = am.reason(why)
        self.assertTrue(r.startswith("the push failed with main unmoved; nothing landed: | FAIL [guards] agent/traces 584.md"))
        self.assertIn("585.md", r); self.assertIn("error: failed to push", r); self.assertNotIn("ok   [guards]", r)
        self.assertEqual(am.reason("a one-line refusal"), "a one-line refusal")
        self.assertEqual(am.reason("introduced:\nsome plain line"), "introduced: | some plain line")
        self.assertEqual(am.reason(""), "no reason given")
        self.assertLessEqual(len(am.reason("x:\n" + "\n".join(f"FAIL {'y' * 300}" for _ in range(9)))), am.REASON_CHARS)
    def test_misuse(self):
        self.assertEqual(run([], self.w.seat)[0], 2)
        self.assertEqual(run(["go"], self.w.seat)[0], 2)
        self.assertEqual(run(["evidence"], self.w.seat)[0], 2)
        self.assertEqual(run(["evidence", "--to", "f"], self.w.seat)[0], 2)
        self.assertEqual(run(["run", "--evidence-from"], self.w.seat)[0], 2)
        self.assertEqual(run(["--help"], self.w.seat)[0], 0)
        self.assertEqual(dyadlib.check_invariants(am), len(am.INVARIANTS) + len(am.TREE_INVARIANTS))


class PrecedentLinesTests(unittest.TestCase):
    """#642 revision 3 (R3): sweep_audit re-measures each precedent record's set leave-one-out and reports a fallen one."""
    def test_a_precedent_record_is_re_measured_and_fallen_is_a_finding(self):
        import shutil
        sim = dyadlib.load_module(PKG / "scripts" / "similar.py", "similar")
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, True)
        pkg = root / "dyad"; (pkg / "dmc").mkdir(parents=True); (pkg / "rules").mkdir()
        (pkg / "dmc" / "context.jsonld").write_text(json.dumps({"@context": ["https://schema.org", {"dyad": "urn:dyad:term:"}]}))
        sim.freeze([("a", "alpha beta gamma", {}, 1), ("a", "alpha beta delta", {}, 2), ("b", "omega psi chi", {}, 3)],
                   pkg / "dmc" / "s.jsonl", {1, 2, 3}, "base", max_df=1.0)
        tun = lambda k, v: {"dyad:preference": k, "dyad:defaultValue": v}
        rec = {"identifier": "p", "dyad:judgedBy": {"dyad:kind": "precedent"},
               "dyad:tunables": [tun("t", "0.0"), tun("m", "0.0")],
               "dyad:precedents": {"dyad:set": "dmc/s.jsonl", "dyad:threshold": "t", "dyad:margin": "m", "dyad:bar": 0.5}}
        (pkg / "dmc" / "p.jsonld").write_text(json.dumps(rec))
        os.environ.pop("DYAD_INSTANCE", None)
        lines = am.precedent_lines(root)
        self.assertTrue(lines[0].startswith("reading: precedent p: agreement 0.67 (2 of 3, 1 abstained), bar 0.5"), lines)
        self.assertEqual(len(lines), 1)                                      # 0.67 meets 0.5: not fallen
        rec["dyad:precedents"]["dyad:bar"] = 0.9; (pkg / "dmc" / "p.jsonld").write_text(json.dumps(rec))
        self.assertEqual(am.precedent_lines(root)[1], "finding: precedent p fallen: agreement 0.67 below its bar 0.9")


if __name__ == "__main__":
    unittest.main()
