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


CORROBORATED = []
def passing(repo, before, after):
    CORROBORATED.append((before, after)); return True, ["ok   [corroborate] check"]

def run(argv, repo, corroborate=passing, **envs):
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, **envs}), \
         unittest.mock.patch.object(am, "corroborate", corroborate), \
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

    def sweep(self, check=(), hygiene=((), ()), inflight=(), **kw):
        with unittest.mock.patch.object(am, "sweep_check", lambda wt: list(check)), \
             unittest.mock.patch.object(am.hygiene_mod, "hygiene", lambda repo, base, now: (list(hygiene[0]), list(hygiene[1]))), \
             unittest.mock.patch.object(am.hygiene_mod, "inflight", lambda repo, base, now, pulls: list(inflight)), \
             unittest.mock.patch.object(am, "sweep_pulls", lambda: None), \
             unittest.mock.patch.object(am, "sweep_drift", lambda repo, wt, base: []), \
             unittest.mock.patch.object(am, "sweep_ci", lambda repo, base, now: []):
            return run(["sweep", "--row", "9"], self.w.seat, **kw)

    def test_the_sweep_tells_only_what_is_new(self):
        files = dict(self.files)
        files[f"{INST}/d-work/rows/9.md"] = ROW.format(id=9, state="planned",
            disposed=f"2026-11-02 Y plan; 2026-11-01 Y done (accreted #10, merges PR #7 at {self.sha})")
        self.w.write_main(files)
        rc, out, err = self.sweep(check=[(False, "warn [agent/plans] 43.md: an old warning")])
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"finding: row #9's done answer of 2026-11-01 names heads not on main: PR #7 at {self.sha[:12]}", out)
        self.assertIn("finding: warn [agent/plans] 43.md: an old warning", out)
        (msg,) = self.inbox(HOME)
        self.assertIn("automaton sweep at", msg); self.assertIn(", findings: ", msg); self.assertIn("PR #7 at <sha>", msg)
        self.assertIn("43.md: an old warning", msg)
        rc, out, _ = self.sweep(check=[(False, "warn [agent/plans] 43.md: an old warning")])
        self.assertIn("0 new", out); self.assertEqual(len(self.inbox(HOME)), 1)            # told once
        rc, out, _ = self.sweep(check=[(True, "FAIL [agent/rows] broken")])
        self.assertEqual(rc, 1, out); self.assertEqual(len(self.inbox(HOME)), 2)           # a new failure is told
        self.assertEqual(run(["sweep", "--row"], self.w.seat)[0], 2)

    def test_the_sweep_tells_new_hygiene_once_grouped_by_kind(self):
        """#565: hygiene findings and similarity candidates ride the sweep's new-only notice."""
        self.w.write_main(self.files)
        hyg = (["hygiene I1 untouched: backlog row #10 (ten), no commit in 40 days"],
               ["candidate: #9 and #10 similar (0.50): nine / ten"])
        rc, out, err = self.sweep(hygiene=hyg)
        self.assertEqual(rc, 0, out + err)                                        # hygiene never fails the sweep
        self.assertIn("finding: hygiene I1 untouched: backlog row #10", out); self.assertIn("candidate: #9 and #10", out)
        msgs = self.inbox(HOME)
        self.assertEqual(sum(", backlog hygiene: " in m for m in msgs), 1)       # one notice per kind
        self.assertEqual(sum(", similarity candidates: " in m for m in msgs), 1)
        self.assertTrue(any(", backlog hygiene: hygiene I1 untouched: backlog row #10" in m for m in msgs), msgs)
        self.assertTrue(any(", similarity candidates: candidate: #9 and #10" in m for m in msgs), msgs)
        rc, out, _ = self.sweep(hygiene=hyg)
        self.assertIn("0 new", out); self.assertEqual(len(self.inbox(HOME)), len(msgs))

    def test_work_in_flight_is_told_one_notice_per_kind(self):
        """#569: each W kind its own notice to home, new-only like every finding; never failing the sweep."""
        self.w.write_main(self.files)
        flight = ["inflight W1 relay unread: row #9's relay to eng-1 sent 2026-11-01T00:00:00Z has no read marker (over 4h)",
                  "inflight W9 operator wait: row #9 waits on the operator with no question recorded",
                  "inflight W9 operator wait: row #10 waits on the operator with no question recorded"]
        rc, out, err = self.sweep(inflight=flight)
        self.assertEqual(rc, 0, out + err)
        msgs = self.inbox(HOME)
        self.assertEqual(sorted(m.split(", ")[1].split(":")[0] for m in msgs if "work in flight" in m),
                         ["work in flight W1", "work in flight W9"])
        self.assertTrue(any("work in flight W9: inflight W9 operator wait: row #9" in m and "row #10" in m for m in msgs), msgs)
        rc, out, _ = self.sweep(inflight=flight)
        self.assertIn("0 new", out); self.assertEqual(len(self.inbox(HOME)), len(msgs))

    def test_a_long_group_is_split_never_cut(self):
        lines = [f"finding: warn [x/y] line {i} " + "z" * 200 for i in range(40)]
        parts = am.notice_parts([am.finding_key(l.removeprefix("finding: ")) for l in lines])
        self.assertGreater(len(parts), 1)
        self.assertEqual(sum(len(p) for p in parts), 40)                          # every line in exactly one part
        self.assertTrue(all(len(" | ".join(p)) < am.NOTICE_CHARS for p in parts))

    def test_misuse(self):
        self.assertEqual(run([], self.w.seat)[0], 2)
        self.assertEqual(run(["go"], self.w.seat)[0], 2)
        self.assertEqual(run(["--help"], self.w.seat)[0], 0)
        self.assertEqual(dyadlib.check_invariants(am), len(am.INVARIANTS) + len(am.TREE_INVARIANTS))


if __name__ == "__main__":
    unittest.main()
