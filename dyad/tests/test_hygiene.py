"""Backlog hygiene (scripts/hygiene.py, d-work #565), over a scratch repo whose ledger holds a handful of rows:
- I1 untouched: a backlog row no commit touched in HYGIENE_STALE_DAYS is a finding; a fresh one is not;
- I2 malformed title: an empty title, or one starting with `-`;
- I4 orphaned: a backlog child whose parent row is terminal;
- I12 worked: a commit on an `origin/*` branch citing `d-work #N` for a backlog row;
- the ranking lists similar rows as candidates, skips siblings under one parent and drops boilerplate tokens;
- placement: no runner path (`check`, `--evidence`, `--corroborate`, the gate) and no guard reaches it;
- every line is information, never a disposition shape (the module's TREE_INVARIANTS);
- work in flight (d-work #569): one fixture per kind W1-W10', and the exemptions (A3, A4, A6, A9);
- W11 phase age (d-work #587 F5): a phased entry past its phase's threshold, worded from its `since` alone;
- two cabinets (d-work #594): each entry read with its own cabinet's `_cos` file, each line tagged with its cabinet."""
import os, shutil, subprocess, sys, tempfile, time, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "hygiene")
INST = "agent-corpus"
ROW = "id: {id}\ntitle: {title}\nopened: 2026-09-01\nstate: {state}\ndisposed: {disposed}\nrefs: {refs}\n"
OLD = "2026-09-01T00:00:00Z"


def git(d, *a, date=None):
    env = {**dyadlib.git_env(), **({"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else {})}
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=env)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class HygieneTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        git(self.d, "init", "-q", "-b", "main")
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            git(self.d, "config", k, v)

    def row(self, id, title, state="backlog", refs="", plan=None, date=None):
        rows = self.d / INST / "d-work" / "rows"; rows.mkdir(parents=True, exist_ok=True)
        (rows / f"{id}.md").write_text(ROW.format(id=id, title=title, state=state, refs=refs,
                                                  disposed="2026-09-01 Y backlog" if state == "backlog" else "2026-09-01 Y plan"))
        if plan:
            plans = self.d / INST / "d-work" / "plans"; plans.mkdir(parents=True, exist_ok=True)
            (plans / f"{id}.md").write_text(plan)
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", f"ledger: #{id}", date=date)

    def run_it(self):
        return hy.hygiene(self.d, "HEAD", time.time())

    def test_structural_findings(self):
        self.row(1, "a parent long done", state="done")
        self.row(2, "an old backlog row about widgets", date=OLD)
        self.row(3, "a fresh backlog row about gadgets")
        self.row(4, "--backlog")
        self.row(5, "a child of a done parent", refs="parent #1")
        git(self.d, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.d, "switch", "-qc", "feature"); (self.d / "x.txt").write_text("x\n"); git(self.d, "add", "-A")
        git(self.d, "commit", "-qm", "work on it (d-work #3)"); git(self.d, "update-ref", "refs/remotes/origin/feature", "HEAD")
        git(self.d, "switch", "-q", "main")
        findings, _ = self.run_it()
        self.assertTrue(any(f.startswith("hygiene I1 untouched: backlog row #2 ") for f in findings), findings)
        self.assertFalse(any("I1 untouched: backlog row #3 " in f for f in findings))
        self.assertIn("hygiene I2 malformed title: backlog row #4 has the title '--backlog'", findings)
        self.assertIn("hygiene I4 orphaned: backlog row #5's parent #1 is done", findings)
        self.assertTrue(any(f.startswith("hygiene I12 worked: backlog row #3 is cited by ") and f.endswith("on origin/feature")
                            for f in findings), findings)
        inbox = dyadlib.load_guard("agent", "inbox")
        self.assertFalse(any(inbox.DISPOSITION.search(f) for f in findings))      # information only

    def test_ranking_lists_near_duplicates_and_skips_siblings(self):
        self.row(10, "the parent", state="planned")
        for i, t in enumerate(["sweep the archive tags against their release entries",
                               "reconcile release tags against the archive entries", "an unrelated row about fonts",
                               "a second unrelated row about colours", "a third unrelated row about spacing",
                               "a fourth unrelated row about margins", "a fifth unrelated row about borders"], 11):
            self.row(i, t)
        self.row(20, "mode W fence: sibling one under the parent", refs="parent #10")
        self.row(21, "mode W fence: sibling two under the parent", refs="parent #10")
        _, candidates = self.run_it()
        self.assertTrue(any(c.startswith("candidate: #11 and #12 similar") for c in candidates), candidates)
        self.assertFalse(any("#20 and #21" in c for c in candidates))            # siblings share boilerplate (A5)

    def test_placement_no_runner_path_or_guard_reaches_it(self):
        runner = (PKG / "scripts" / "package.py").read_text()
        self.assertNotIn("hygiene", runner)
        self.assertFalse(any("hygiene" in str(p) for p in dyadlib.guard_files(PKG)))
        self.assertIn("hygiene_mod.hygiene(", (PKG / "scripts" / "automaton.py").read_text())

    def test_invariants(self):
        self.assertEqual(dyadlib.check_invariants(hy), len(hy.INVARIANTS) + len(hy.TREE_INVARIANTS))

    def test_tfidf_is_the_one_weighting(self):
        """#615: `ranking` reads `tfidf` and `cosine`, which `intent.candidates` reads too; boilerplate is dropped."""
        docs = {1: "zebra stripes", 2: "zebra horse", **{10 + k: f"common pad{k}" for k in range(8)}}
        vec, norm = hy.tfidf(docs)
        self.assertNotIn("common", vec[10])                                    # in 8 of 10 documents: boilerplate
        self.assertGreater(hy.cosine(vec, norm, 1, 2), 0); self.assertEqual(hy.cosine(vec, norm, 1, 10), 0.0)
        self.assertAlmostEqual(hy.cosine(vec, norm, 1, 1), 1.0)


NOW = 1_762_300_800.0          # 2025-11-05T00:00:00Z, the clock every in-flight case reads
DAY = 86400


def stamp(t: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FastReadTests(unittest.TestCase):
    """#617: the readers `board resume` calls at each prompt read in one process each, and say what the old one did."""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        git(self.d, "init", "-q", "-b", "main")
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            git(self.d, "config", k, v)

    def commit(self, rel, text, msg="c", at=None):
        f = self.d / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", msg, **({"date": at} if at else {}))

    def test_show_many_reads_every_path_and_leaves_out_the_absent(self):
        self.commit("a.md", "one\n"); self.commit("b/c.md", "two\nlines\n"); self.commit("e.md", "")
        got = dyadlib.show_many(self.d, "HEAD", ["a.md", "missing.md", "b/c.md", "e.md"])
        self.assertEqual(got, {"a.md": "one\n", "b/c.md": "two\nlines\n", "e.md": ""})
        self.assertEqual(dyadlib.show_many(self.d, "HEAD", []), {})

    def test_promise_since_agrees_with_the_pickaxe(self):
        rel = "board/_cos.md"
        self.commit(rel, "holder: h\npromised: alpha\n", at=stamp(NOW - 9 * DAY))
        self.commit(rel, "holder: h\npromised: alpha; beta\n", at=stamp(NOW - 5 * DAY))
        self.commit(rel, "holder: x\npromised: alpha; beta\n", at=stamp(NOW - 2 * DAY))     # a change touching neither
        log = {}
        for text in ("alpha", "beta", "gamma"):
            ts = git(self.d, "log", "--format=%ct", "-S", text, "HEAD", "--", rel).split()
            self.assertEqual(hy._promise_since(self.d, "HEAD", rel, text, log), int(ts[0]) if ts else None, text)
        self.assertEqual(list(log), [rel])                                        # one log per file, cached

    def test_cited_on_branches_reads_every_branch_in_one_log(self):
        self.commit("x", "x\n"); git(self.d, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.d, "update-ref", "refs/remotes/origin/HEAD", "HEAD")
        for b, n in (("one", 3), ("two", 4)):
            git(self.d, "switch", "-qc", b, "main"); self.commit(f"{b}.txt", b, msg=f"work (d-work #{n})")
            git(self.d, "update-ref", f"refs/remotes/origin/{b}", "HEAD")
        git(self.d, "switch", "-q", "main"); self.commit("y", "y\n", msg="on main (d-work #5)")
        got = hy.cited_on_branches(self.d)
        self.assertEqual({k: v[1] for k, v in got.items()}, {3: "origin/one", 4: "origin/two"})   # main's never

class InflightTests(unittest.TestCase):
    """Each W kind on a scratch repo whose records are written at fixed times against NOW."""
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        git(self.d, "init", "-q", "-b", "main")
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            git(self.d, "config", k, v)
        self.s = self.d / INST / "d-work"

    def put(self, rel, text):
        f = self.s / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)

    def row(self, id, state="planned", refs="", disposed="2025-10-01 Y plan", plan=True):
        self.put(f"rows/{id}.md", ROW.format(id=id, title=f"row {id}", state=state, refs=refs, disposed=disposed))
        if plan:
            self.put(f"plans/{id}.md", f"# Plan #{id}\n")

    def commit(self, at=NOW - 10 * DAY, msg="ledger"):
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", msg, date=stamp(at))
        git(self.d, "update-ref", "refs/remotes/origin/main", "HEAD")

    def run_it(self, pulls=(), fresh=None):
        return hy.inflight(self.d, "HEAD", NOW, None if pulls is None else list(pulls), fresh)

    def kinds(self, lines):
        return [l.split()[1] for l in lines]

    def test_w1_an_unread_relay_and_a_read_or_young_one(self):
        self.row(1); self.put("board/_cos.md", "holder: home-1\n")
        for n, sent, read in (("a", NOW - 5 * 3600, False), ("b", NOW - 5 * 3600, True), ("c", NOW - 3600, False)):
            self.put(f"inbox/unit-1/{n}.md", f"from: home-1\nto: unit-1\nrow: 1\nkind: relay\nsent: {stamp(sent)}\nbody: go\n")
            if read:
                self.put(f"inbox/unit-1/{n}.read", "read: x\nreader: unit-1\n")
        self.commit()
        got = [l for l in self.run_it() if " W1 " in l]
        self.assertEqual(len(got), 1, got); self.assertIn(f"relay to unit-1 sent {stamp(NOW - 5 * 3600)} has no read marker", got[0])

    def test_w2_a_quiet_planned_row_on_a_unit_and_the_exemptions(self):
        for i, waits in ((1, "unit eng-1"), (2, "operator"), (3, "unit eng-1")):
            self.row(i, disposed="2025-10-01 Y plan")
            self.put(f"board/{i}.md", f"holder: home-1\nowner: eng-1\nwaiting-on: {waits}\nsince: 2025-10-01T00:00Z\n")
        self.commit()
        git(self.d, "switch", "-qc", "w3"); (self.d / "x.txt").write_text("x")
        self.commit(at=NOW - DAY, msg="work (d-work #3)"); git(self.d, "update-ref", "refs/remotes/origin/w3", "HEAD")
        git(self.d, "switch", "-q", "main"); git(self.d, "update-ref", "refs/remotes/origin/main", "HEAD")
        got = [l for l in self.run_it() if " W2 " in l]
        self.assertEqual(len(got), 1, got)                  # #2 waits on the operator (A3); #3 has a citing commit
        self.assertTrue(got[0].startswith("inflight W2 planned row quiet: row #1 waits on unit eng-1 with nothing since 2025-10-01T00:00Z"), got)

    def test_w3_an_open_row_with_no_plan_and_its_exemptions(self):
        self.row(1, state="done")
        self.row(2, state="open", plan=False)
        self.row(3, state="open", refs="parent #1", plan=False)                       # a child (A4)
        self.row(4, state="open", disposed="2025-10-01 Y plan (mandate #1)", plan=False)   # under a mandate
        self.row(5, state="open")
        self.commit(at=NOW - 2 * DAY)
        self.row(6, state="open", plan=False); self.commit(at=NOW - 3600)            # too young
        got = [l for l in self.run_it() if " W3 " in l]
        self.assertEqual(len(got), 1, got); self.assertIn("row #2 (row 2)", got[0])

    def test_w4_w6_open_prs_and_the_skip_without_the_hosting(self):
        self.row(1); self.row(2, state="done"); self.commit()
        head = git(self.d, "rev-parse", "HEAD")
        pulls = [{"number": 7, "title": "x (d-work #1)", "body": "", "head_ref": "", "head_sha": head, "updated_at": stamp(NOW)},
                 {"number": 8, "title": "y", "body": "d-work #2", "head_ref": "", "head_sha": head, "updated_at": stamp(NOW)},
                 {"number": 9, "title": "z", "body": "", "head_ref": "", "head_sha": head, "updated_at": stamp(NOW)}]
        got = self.run_it(pulls)
        self.assertIn("inflight W4 orphan PR: PR #8 cites no live row (cites #2)", got)
        self.assertIn("inflight W4 orphan PR: PR #9 cites no live row (cites none)", got)
        self.assertTrue(any(l.startswith(f"inflight W6 stale PR head: PR #7 on row #1 has head {head[:12]}") for l in got), got)
        self.assertIn("inflight W4-W6 skipped: the hosting's open PRs were not read (no GITHUB_TOKEN/GITHUB_REPOSITORY)",
                      self.run_it(None))

    def test_w5_an_orphan_branch_and_the_exemptions(self):
        self.row(1); self.commit()
        for name, msg in (("orphan", "stray"), ("cited", "work (d-work #1)"), ("prd", "pr work")):
            git(self.d, "switch", "-qc", name, "main"); (self.d / f"{name}.txt").write_text(name)
            self.commit(msg=msg); git(self.d, "update-ref", f"refs/remotes/origin/{name}", "HEAD")
        git(self.d, "switch", "-q", "main"); git(self.d, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.d, "update-ref", "refs/remotes/origin/merged", "HEAD")            # on main (A6)
        got = [l for l in self.run_it([{"number": 3, "title": "d-work #1", "body": "", "head_ref": "prd",
                                         "head_sha": git(self.d, "rev-parse", "prd"), "updated_at": stamp(NOW)}]) if " W5 " in l]
        self.assertEqual(len(got), 1, got); self.assertTrue(got[0].startswith("inflight W5 orphan branch: orphan (tip "), got)

    def test_w7_the_unit_table_and_the_presence_gate(self):
        self.row(1)
        self.put("board/_cos.md", "holder: home-1\nseats: eng-1 s1; home-1 s0\n")
        self.put("board/1.md", "holder: home-1\nowner: eng-1; ops-2\nwaiting-on: unit eng-1\nsince: 2025-11-04T00:00Z\n")
        self.put("sessions/eng-1.md", "session: eng-1\nseen: 2025-10-01T00:00:00+00:00\nroot: /x\nrows: \nfiles: \n")
        self.commit()
        got = self.run_it()
        self.assertIn("inflight W7a unit not in table: ops-2 is named on the board but not in _cos's seats", got)
        self.assertIn("inflight W7b skipped: the presence store holds no fresh file (gated on #567)", got)
        got = self.run_it(fresh=lambda seat, at: False)
        self.assertIn("inflight W7b unit stale: row #1 waits on eng-1, whose presence file is stale", got)

    def test_w7c_the_retired_seat_form_is_named_not_skipped(self):
        """#604: W2/W7a/W7b read `unit <name>` only, so an entry still waiting on `seat <name>` gets its own line."""
        self.row(1); self.row(2)
        self.put("board/1.md", "holder: home-1\nwaiting-on: seat eng-1\nsince: 2025-10-01T00:00Z\n")
        self.put("board/2.md", "holder: home-1\nwaiting-on: unit eng-1\nsince: 2025-11-04T00:00Z\n")
        self.commit()
        got = [l for l in self.run_it() if " W7c " in l]
        self.assertEqual(got, ["inflight W7c retired form: row #1's board entry `waiting-on: seat eng-1` uses `seat <name>`, "
                               "removed in dyad-operator 1.0; write `waiting-on: unit eng-1` (#604)"])

    def test_w8_a_promise_listed_too_long(self):
        self.row(1); self.put("board/_cos.md", "holder: home-1\npromised: open a row for X\n"); self.commit(at=NOW - 5 * DAY)
        self.put("board/_cos.md", "holder: home-1\npromised: open a row for X; fix Y\n"); self.commit(at=NOW - DAY)
        got = [l for l in self.run_it() if " W8 " in l]
        self.assertEqual(got, [f"inflight W8 promise still listed: board _cos has promised 'open a row for X' since "
                               f"{stamp(NOW - 5 * DAY)[:10]} (over 3 days)"])

    def test_w9_the_operator_wait(self):
        for i in (1, 2, 3):
            self.row(i)
        self.put("board/1.md", "holder: h\nwaiting-on: operator\nsince: 2025-11-04T20:00Z\n")
        self.put("board/2.md", "holder: h\nwaiting-on: operator\nsince: 2025-11-01T00:00Z\nquestion: Y/N: go?\n")
        self.put("board/3.md", "holder: h\nwaiting-on: operator\nsince: 2025-11-04T20:00Z\nquestion: Y/N: go?\n")
        self.commit()
        got = [l for l in self.run_it() if " W9 " in l]
        self.assertEqual(got, ["inflight W9 operator wait: row #1 waits on the operator with no question recorded",
                               "inflight W9 operator wait: row #2's question to the operator stands since 2025-11-01T00:00Z (over 24h)"])

    def test_w10_a_report_newer_than_the_board(self):
        self.row(1); self.row(2)
        self.put("board/_cos.md", "holder: home-1\n")
        for i in (1, 2):
            self.put(f"board/{i}.md", f"holder: home-1\nowner: eng-1\nwaiting-on: unit eng-1\nsince: 2025-11-04T10:00Z\n")
        for n, row, sent in (("a", 1, "2025-11-04T12:00:00Z"), ("b", 2, "2025-11-04T09:00:00Z")):
            self.put(f"inbox/home-1/{n}.md", f"from: eng-1\nto: home-1\nrow: {row}\nkind: report\nsent: {sent}\nbody: done\n")
        self.commit()
        got = [l for l in self.run_it() if " W10' " in l]
        self.assertEqual(got, ["inflight W10' report after board: row #1's board since 2025-11-04T10:00Z, but eng-1 reported on it at 2025-11-04T12:00:00Z"])

    def test_w11_phase_age(self):
        """#587 F5: a phased entry older than its phase's threshold (asked phases 24 h, others 3 days); an unphased one
        is W11-silent; the line holds the record's `since`, never a computed age."""
        bd = dyadlib.load_guard("agent", "board")
        def phased(rid, phase, since, **sub):
            f = {"holder": "home-1", "owner": "eng-1", "since": since,
                 "phase": bd.phase_render(phase, {"unit": ["eng-1"], **{k: [v] for k, v in sub.items()}})}
            f.update(bd.derive(rid, f))
            if phase in dyadlib.ORCH_ASKED:
                f["question"] = f"Y/N: proceed with #{rid} as planned?"
            return bd.render(f, bd.FIELDS)
        for i in (1, 2, 3, 4):
            self.row(i)
        self.put("board/1.md", phased(1, "plan-asked", "2025-11-03T20:00Z"))          # 28 h asked: a finding
        self.put("board/2.md", phased(2, "building", "2025-11-03T20:00Z"))            # 28 h building: none
        self.put("board/3.md", phased(3, "building", "2025-11-01T00:00Z"))            # 4 days building: a finding
        self.put("board/4.md", "holder: h\nwaiting-on: unit eng-1\nsince: 2025-10-01T00:00Z\n")   # unphased: none
        self.commit()
        got = [l for l in self.run_it() if " W11 " in l]
        self.assertEqual(got, ["inflight W11 phase age: row #1 in plan-asked since 2025-11-03T20:00Z",
                               "inflight W11 phase age: row #3 in building since 2025-11-01T00:00Z"])
        self.assertEqual(set(hy.INFLIGHT_W11_HOURS) | set(hy.INFLIGHT_W11_TUNED), set(dyadlib.ORCH_PHASES))
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        groups = am.notice_groups([f"finding: {l}" for l in got] + ["finding: inflight W1 relay unread: x"])
        self.assertEqual([k for k, _ in groups], ["work in flight W1", "work in flight W11"])   # its own notice

    def test_two_cabinets_each_read_with_its_own_cos(self):
        """#594: on a two-cabinet board B's unit raises no W7a against A's seats, `_cos-bob`'s promise and row 2's entry's
        promise (whose text names row #1, of A's cabinet) are aged by W8 and tagged with their own files' cabinet,
        and B's W9 line and W10' read go to B's leader's home — each line tagged with its cabinet."""
        B = "program-bob-cccccccc"
        self.row(1); self.row(2)
        self.put("board/_cos.md", "holder: home-a\nseats: eng-1 s1\n")
        self.put("board/_cos-bob.md", f"holder: {B}\nseats: eng-b s2\npromised: B's follow-up\n")
        self.put("board/1.md", "holder: home-a\nowner: eng-1\nwaiting-on: unit eng-1\nsince: 2025-11-04T10:00Z\n")
        self.put("board/2.md", f"holder: {B}\ncabinet: program-bob\nowner: eng-b\nwaiting-on: operator\n"
                               "since: 2025-11-01T00:00Z\nquestion: Y/N: B's question?\npromised: merge after row #1\n")
        for box, n in ((B, "a"), ("home-a", "b")):
            self.put(f"inbox/{box}/{n}.md", "from: eng-b\nto: x\nrow: 2\nkind: report\nsent: 2025-11-04T12:00:00Z\nbody: done\n")
        self.commit(at=NOW - 5 * DAY)
        got = hy.inflight_cabinets(self.d, "HEAD", NOW, [], lambda seat, at: True)
        self.assertEqual([l for _, l in got], self.run_it(fresh=lambda seat, at: True))   # `inflight` is its lines
        self.assertFalse([l for _, l in got if " W7a " in l], got)                         # eng-b is in B's own seats
        w8 = sorted((c, l.split(" has promised")[0]) for c, l in got if " W8 " in l)
        self.assertEqual(w8, [("program-bob", "inflight W8 promise still listed: board 2"),     # its file's cabinet, never
                              ("program-bob", "inflight W8 promise still listed: board _cos-bob")])   # the `row #1` it names
        self.assertTrue(any(c == "program-bob" and l.startswith("inflight W8 promise still listed: board _cos-bob has promised")
                            for c, l in got), got)
        self.assertIn(("program-bob", "inflight W9 operator wait: row #2's question to the operator stands since "
                                      "2025-11-01T00:00Z (over 24h)"), got)
        w10 = [(c, l) for c, l in got if " W10' " in l]
        self.assertEqual(w10, [("program-bob", "inflight W10' report after board: row #2's board since 2025-11-01T00:00Z, "
                                               "but eng-b reported on it at 2025-11-04T12:00:00Z")])   # B's home's box, once
        self.put("board/1.md", "holder: home-a\nowner: eng-1; eng-b\nwaiting-on: unit eng-1\nsince: 2025-11-04T10:00Z\n")
        self.commit()
        got = hy.inflight_cabinets(self.d, "HEAD", NOW, [], lambda seat, at: True)
        self.assertIn(("program", "inflight W7a unit not in table: eng-b is named on the board but not in _cos's seats"), got)

    def test_w11_done_ready_is_the_tunable(self):
        """#587 S9: `done-ready`'s threshold is `inflight-done-ready-hours`, read when the sweep runs (default 4 h from
        dmc/work-in-flight.jsonld): a drafted Done held 13 h is a W11 line at the default and none under a 24 h
        preference; a 3 h hold says nothing at the default."""
        bd = dyadlib.load_guard("agent", "board")
        def phased(rid, since):
            f = {"holder": "home-1", "owner": "eng-1", "since": since,
                 "phase": bd.phase_render("done-ready", {"unit": ["eng-1"]})}
            f.update(bd.derive(rid, f))
            return bd.render(f, bd.FIELDS)
        self.assertEqual(dyadlib.tunable_default("inflight-done-ready-hours"), 4)
        self.assertNotIn("done-ready", hy.INFLIGHT_W11_HOURS)            # one home: the record's default, no constant
        self.row(1); self.row(2)
        self.put("board/1.md", phased(1, "2025-11-04T11:00Z"))             # 13 h before NOW
        self.put("board/2.md", phased(2, "2025-11-04T21:00Z"))             # 3 h
        self.commit()
        got = [l for l in self.run_it() if " W11 " in l]
        self.assertEqual(got, ["inflight W11 phase age: row #1 in done-ready since 2025-11-04T11:00Z"])
        prefs = self.d / dyadlib.PREFERENCES_REL; prefs.parent.mkdir(parents=True, exist_ok=True)
        prefs.write_text("| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"
                         "| inflight-done-ready-hours | 24 | a positive integer (hours) | Rule-3 |\n")
        self.assertEqual([l for l in self.run_it() if " W11 " in l], [])      # read at run time, from the preference

    def test_every_line_is_information_and_a_notice_kind(self):
        inbox = dyadlib.load_guard("agent", "inbox")
        self.row(1); self.put("board/1.md", "holder: h\nwaiting-on: operator\nsince: 2025-11-01T00:00Z\nquestion: Y/N: go?\n")
        self.commit()
        got = self.run_it()
        self.assertTrue(got)
        for l in got:
            self.assertFalse(inbox.DISPOSITION.search(l), l)
            self.assertIn(l.split()[1].split("-")[0], hy.INFLIGHT_KINDS)


if __name__ == "__main__":
    unittest.main()
