"""d-work #587's DoD replays: the 2026-11-04 orchestration slips S1-S10, home's S11 (2026-11-05T05:29:17Z) and plan
revision 2's two automaton cases (#573's combined red, #572's stale #650 head), each replayed through the machine
(`dyadlib.ORCH_EVENTS`, `board advance`, `automaton run`, the sweep's `inflight`) in a scratch world: a real scratch
install as the seed, a bare origin with `refs/pull/<n>/head`, a seat clone whose pre-push hook only reads its input,
and a racer that writes main past the hook (test_steps.World). Seat names are the day's; rows and PR numbers are the
day's; heads are the scratch world's.

Each case asserts what the report `agent-corpus/audits/2026-11-05-orchestration-replays.md` claims of it: refused,
prevented, put on the ring list, caught by the automaton with no unit's turn, or not caught (an expected failure, so
the gap is pinned and the test flips when it is closed). Every command and its output is kept in TRANSCRIPT, keyed by
the test's name, which is what the report quotes.

The combined evidence (X5) is a stub that reads the cut's tree, because the real `check --evidence` runs the whole
suite: what is under test is the automaton's firing on the verdict, not the suite. The corroboration is a stub too."""
import contextlib, io, os, subprocess, sys, time, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib, livetest
from test_steps import World, git, INST

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
bd = dyadlib.load_guard("agent", "board")
ib = dyadlib.load_guard("agent", "inbox")
am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "hygiene")

HOME, ENG, COU = "program-59cec502", "engineer-1537d8fb", "counsel-0032b4c0"
ORC, DIS, OPE, COM, AUD = "orchestrate-d688fecf", "distribute-a603e150", "operate-8cce8b10", "communicate-17f24597", "audit-e73be78c"
EV = "8d0ba6f9e4c786a1c3bc7d6df5024adefc73acdf1f7df4daac3cc31cdfbc65b0"   # #651's evidence-sha256 of 18:00:21Z
S3_FAIL = ("FAIL [Rule-12] test_surface test_s3_preference_keys: 'attended-seats' : an S3 key that is no preference")
TRANSCRIPT: dict[str, list[str]] = {}


def row(rid, state="planned", disposed="2026-11-04 Y plan"):
    """A row, its provenance (one entry per disposition) and its plan file."""
    n = len([e for e in disposed.split(";") if e.strip()])
    prov = f"# Provenance #{rid}\n\n## 1 prompt 2026-11-04\n\n```\nopen row {rid}\n```\n\n" + "".join(
        f"## {i + 2} disposition 2026-11-04\n\n```\nY\n```\n\n" for i in range(n))
    return {f"{INST}/d-work/rows/{rid}.md": f"id: {rid}\ntitle: row {rid}\nopened: 2026-11-04\nstate: {state}\n"
                                             f"disposed: {disposed}\nrefs: \n",
            f"{INST}/d-work/provenance/{rid}.md": prov,
            f"{INST}/d-work/plans/{rid}.md": f"# Plan #{rid}\n"}


def phased(rid, phase, sub, owner, question=None, since="2026-11-04T10:00Z"):
    """A phased entry exactly as `board advance` writes it (the derived fields from `derive`)."""
    f = {"holder": HOME, "phase": bd.phase_render(phase, sub), "owner": owner, "since": since, "writer": "h1"}
    f.update(bd.derive(rid, f))
    if question:
        f["question"] = question
    return {f"{INST}/d-work/board/{rid}.md": bd.render(f, bd.FIELDS)}


def evidence_by_tree(repo, sha):
    """The X5 stub: #573's three PRs pass alone and fail together (FAIL test_s3), read from the cut's own tree."""
    names = set(git(repo, "ls-tree", "-r", "--name-only", sha).split())
    together = {"dyad/zz-642-surface.txt", "dyad/zz-651-test-s3.txt", "dyad/zz-652-rename.txt"} <= names
    if together:
        return 1, [f"head={sha}", S3_FAIL, f"evidence-sha256={'f' * 64}"]
    return 0, [f"head={sha}", "ok   [rule-12] suite", f"evidence-sha256={EV}"]


class Replays(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "DYAD_SESSION": HOME,
                                                  "CLAUDE_CODE_SESSION_ID": "59cec502-replay", "GITHUB_ACTIONS": ""})
        e.start(); self.addCleanup(e.stop)
        seed = SCRATCH.copy(False)
        top = SCRATCH.mkdtemp(); moved = top / "seed"; seed.rename(moved)
        git(moved, "branch", "-M", "main")
        self.w = World(moved)
        self.w.write_main({f"{INST}/d-work/board/_cos.md": f"holder: {HOME}\nwriter: h1\n"})
        self.said = top / "said.txt"; self.said.write_text("Y\n")
        self.log = TRANSCRIPT.setdefault(self._testMethodName, [])

    # ---- the commands, each kept in the transcript
    def keep(self, cmd, rc, out, err):
        self.log.append(f"$ {cmd}")
        self.log += [l for l in (out + err).rstrip("\n").splitlines()] + [f"(exit {rc})"]

    def adv(self, *argv, session=HOME):
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": session, "CLAUDE_CODE_SESSION_ID": f"{session.rsplit('-', 1)[-1]}-replay"}), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bd.cli(["advance", *argv], self.w.seat)
        self.keep(f"DYAD_SESSION={session} dyad board advance {' '.join(argv)}", rc, out.getvalue(), err.getvalue())
        return rc, out.getvalue(), err.getvalue()

    def board_cli(self, *argv, session=HOME):
        git(self.w.seat, "pull", "-q", "--ff-only", "origin", "main")
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": session}), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bd.cli(list(argv), self.w.seat)
        self.keep(f"DYAD_SESSION={session} dyad board {' '.join(argv)}".rstrip(), rc, out.getvalue(), err.getvalue())
        return rc, out.getvalue(), err.getvalue()

    def auto(self, verb, evidence=evidence_by_tree):
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(am, "corroborate", lambda *a: (True, [])), \
             unittest.mock.patch.object(am, "evidence_at", evidence), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = am.main([verb], self.w.seat)
        self.keep(f"dyad automaton {verb}", rc, out.getvalue(), err.getvalue())
        return rc, out.getvalue(), err.getvalue()

    def sweep(self, hours_later):
        lines = [l for l in hy.inflight(self.w.seat, "origin/main", time.time() + hours_later * 3600, [],
                                        lambda s, n: True) if l.startswith("inflight W")]
        self.keep(f"(the sweep's inflight, {hours_later} h later)", 0, "\n".join(lines) + "\n", "")
        return lines

    # ---- reading origin/main
    def show(self, rel):
        r = subprocess.run(["git", "show", f"main:{INST}/d-work/{rel}"], cwd=self.w.origin, capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None

    def entry(self, rid):
        t = self.show(f"board/{rid}.md")
        return None if t is None else bd.parse(t)[0]

    def box(self, seat):
        r = subprocess.run(["git", "ls-tree", "--name-only", f"main:{INST}/d-work/inbox/{seat}"], cwd=self.w.origin,
                           capture_output=True, text=True)
        return [bd.parse(self.show(f"inbox/{seat}/{n}"))[0] for n in r.stdout.split() if n.endswith(".md")]

    def main_sha(self):
        return git(self.w.origin, "rev-parse", "main")

    def heads(self, rid):
        return bd.pr_list(bd.phase_of(self.entry(rid)["phase"])[1])

    # ---- S1-S10 (2026-11-04)
    def test_s1_a_pr_up_tells_every_co_owner_and_rings_them(self):
        """S1: distribute idle on #564, never told #631 was up. `pr-up` reports to the holder and cc's every other
        owner, distribute among them, in its own commit, and names them on the ring list."""
        owners = f"{ENG}; {DIS}; {COU}; {ORC}"
        self.w.write_main(row(564) | phased(564, "building", {"unit": [ENG]}, owners))
        rc, out, err = self.adv("564", "pr-up", "--expect", "building", "pr=631", "head=" + "ab12cd34" * 5, session=ENG)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(bd.phase_name(self.entry(564)), "verifying")
        self.assertTrue([m for m in self.box(DIS) if "PR #631" in m["body"]], self.box(DIS))
        self.assertIn(DIS, out.split("ring: ")[1])

    def test_s2_waiting_on_is_derived_and_a_hand_write_is_refused(self):
        """S2: #498 marked waiting on communicate while it waited on the operator. `hold on=operator` derives
        `waiting-on: operator`; `board set waiting-on=` is refused on a phased entry; a hand edit fails the guard."""
        self.w.write_main(row(498) | phased(498, "building", {"unit": [COM]}, COM))
        rc, out, err = self.adv("498", "hold", "--expect", "building",
                                "note=the operator's persona corrections in the paired communicate chat", "on=operator")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.entry(498)["waiting-on"], "operator")
        rc, out, err = self.board_cli("set", "498", f"waiting-on=unit {COM}")
        self.assertEqual(rc, 1); self.assertIn("written by `dyad board advance`", err)
        drifted = self.show("board/498.md").replace("waiting-on: operator", f"waiting-on: unit {COM}")
        fails = bd.check_entry("498", drifted, {498: "planned"})
        self.keep("(the board guard over board/498.md hand-edited to waiting-on: unit communicate-17f24597)", 0,
                  "\n".join(fails) + "\n", "")
        self.assertTrue(any("waiting-on" in m for m in fails), fails)

    def test_s3_routing_reads_owners_not_the_seat_table(self):
        """S3: orchestrate missing from the hand-written `_cos` seat table. `opened unit=` makes it an owner; the relay
        goes to it and `resume` announces to it, whatever the table says; the guard warns on the stale table."""
        self.w.write_main({f"{INST}/d-work/board/_cos.md": f"holder: {HOME}\nseats: {HOME} (home); {ENG}; {COU}\nwriter: h1\n"}
                          | row(573, "open", ""))
        rc, out, err = self.adv("573", "opened", "--expect", "none", f"unit={ORC}")
        self.assertEqual(rc, 0, out + err)
        self.assertIn(ORC, bd.owners(self.entry(573)))
        self.assertEqual([m["kind"] for m in self.box(ORC)], ["relay"])
        rc, out, _ = self.board_cli("resume")
        (line,) = [l for l in out.splitlines() if l.startswith("announce to")]
        self.assertIn(ORC, line.split("; seat table:")[0]); self.assertNotIn(ORC, line.split("; seat table:")[1])
        warns = [m for m in bd.check_package(self.w.seat) if "seat table" in m]    # the stale table itself is caught
        self.keep("dyad check (agent/board)", 0, "\n".join(warns) + "\n", "")
        self.assertEqual(warns, [f"warning: board/573.md: {ORC} owns this entry and is missing from the `_cos` seat "
                                 f"table — `dyad board set _cos seats=…` adds it (#587 S3)"])

    def test_s4_a_co_owners_pr_up_moves_the_wait_off_the_reporter(self):
        """S4: counsel's #567/#568 PRs up, the board still waiting on counsel. Counsel's `pr-up` moves each row to
        verifying, waiting on the holder, in the same commit as the report."""
        self.w.write_main(row(567) | row(568) | phased(567, "building", {"unit": [COU]}, f"{COU}; {ENG}")
                          | phased(568, "building", {"unit": [COU]}, f"{COU}; {ENG}"))
        for rid, pr, h in ((567, 637, "1" * 40), (568, 638, "2" * 40)):
            rc, out, err = self.adv(str(rid), "pr-up", "--expect", "building", f"pr={pr}", f"head={h}", session=COU)
            self.assertEqual(rc, 0, out + err)
            f = self.entry(rid)
            self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("verifying", f"unit {HOME}"))
        rc, out, _ = self.board_cli()
        self.assertNotIn(f"waiting-on unit {COU}", out)

    def test_s5_who_acts_next_is_named_and_an_unread_relay_is_swept(self):
        """S5: orchestrate's unread copies, 13 h. The entry names the one seat that acts next; the relay to it is one
        message; left unread it is the sweep's W1 line after 4 h, so at 13 h it has been told."""
        self.w.write_main(row(573, "open", ""))
        rc, out, err = self.adv("573", "opened", "--expect", "none", f"unit={ORC}")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.entry(573)["waiting-on"], f"unit {ORC}")
        self.assertEqual(len(self.box(ORC)), 1)
        lines = self.sweep(13)
        self.assertTrue([l for l in lines if l.startswith("inflight W1 relay unread: row #573") and ORC in l], lines)

    def test_s6_a_relay_names_its_doorbell_on_the_ring_list(self):
        """S6: B3 relays with no doorbell. Every advance that posts a relay prints `ring:` with the seat; the doorbell
        itself stays home's act (X8, a confirmed limit), and an unrung, unread relay is the sweep's W1."""
        self.w.write_main(row(573) | phased(573, "verifying", {"unit": [ORC], "pr": ["642 at " + "3" * 40]}, ORC))
        rc, out, err = self.adv("573", "evidence-failed", "--expect", "verifying", "note=combined merge fails test_s3")
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"ring: {ORC}", out)
        self.assertEqual([m["kind"] for m in self.box(ORC)], ["relay"])

    def test_s7_record_board_and_relays_are_one_commit_or_none(self):
        """S7: relays sent before #573's record. A plan-Y lands the row, the words, the board and the relay in one
        commit; when the ledger line is refused, nothing lands — no board, no relay."""
        self.w.write_main(row(573, "open", "") | phased(573, "plan-asked", {"unit": [ORC]}, ORC,
                                                         question="Y/N: proceed with #573 as planned?"))
        before = self.main_sha()
        rc, out, err = self.adv("573", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        files = sorted(git(self.w.origin, "show", "--name-only", "--format=", "main").split())
        self.keep("git show --name-only main", 0, "\n".join(files) + "\n", "")
        self.assertEqual(int(git(self.w.origin, "rev-list", "--count", f"{before}..main")), 1)
        for part in ("rows/573.md", "provenance/573.md", "board/573.md", f"inbox/{ORC}/"):
            self.assertTrue([f for f in files if part in f], part)
        self.w.write_main({f"{INST}/d-work/rows/574.md": "id: 574\ntitle: row 574\nopened: 2026-11-04\nstate: blocked\n"
                                                         "disposed: \nrefs: 573\n",
                           f"{INST}/d-work/provenance/574.md": "# Provenance #574\n\n## 1 prompt 2026-11-04\n\n```\nopen\n```\n\n"}
                          | phased(574, "plan-asked", {"unit": [COU]}, COU, question="Y/N: proceed with #574 as planned?"))
        before = self.main_sha()
        rc, out, err = self.adv("574", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 1); self.assertIn("refused it in the worktree", err)
        self.assertEqual(self.main_sha(), before); self.assertEqual(self.box(COU), [])

    def test_s8_the_relay_goes_to_an_owner_the_event_made(self):
        """S8: a relay refused three times, the receiver not an owner. Adopting the entry with `opened unit=` adds the
        unit to `owner` in the same commit as its relay; the plain `inbox post` before it shows the old refusal."""
        self.w.write_main(row(574, "open", "") | {f"{INST}/d-work/board/574.md":
                                                  f"holder: {HOME}\nowner: {COU}\nwaiting-on: unit {COU}\nnext: PR 1\nwriter: h1\n"})
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": ENG}), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = ib.cli(["post", ORC, "--row", "574", "--kind", "relay", "verify PR #646"], self.w.seat)
        self.keep(f"DYAD_SESSION={ENG} dyad inbox post {ORC} --row 574 --kind relay 'verify PR #646'", rc, out.getvalue(), err.getvalue())
        self.assertEqual(rc, 1); self.assertIn(f"not {ORC}", err.getvalue())
        rc, out, err = self.adv("574", "opened", "--expect", "none", f"unit={ORC}")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(bd.owners(self.entry(574)), [COU, ORC])
        self.assertEqual([m["kind"] for m in self.box(ORC)], ["relay"])

    def test_s9_a_drafted_done_is_a_phase_the_queue_counts(self):
        """S9: #569's Done held 13 h after its draft. Evidence verified makes the row done-ready, waiting on the holder
        with `ask the Done question` next, counted in the derived queue. Prevented: W11's done-ready threshold is the
        tunable `inflight-done-ready-hours` (default 4 h), so the 13 h hold is swept; a 3 h one is not."""
        self.w.write_main(row(569) | phased(569, "verifying", {"unit": [ORC], "pr": ["640 at " + "7" * 40]}, f"{ORC}; {ENG}"))
        rc, out, err = self.adv("569", "evidence-verified", "--expect", "verifying", f"evidence={EV}")
        self.assertEqual(rc, 0, out + err)
        f = self.entry(569)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("done-ready", f"unit {HOME}"))
        self.assertTrue(f["next"].startswith("ask the Done question"))
        rc, out, _ = self.board_cli()
        self.assertIn("Coming: 1 done-ready.", out)                       # #646: the closing line, awaiting-you on
        self.assertEqual(bd.derived_queue(self.w.seat)["done-ready"], [569])
        self.assertEqual([l for l in self.sweep(3) if "W11" in l], [])
        self.assertEqual(dyadlib.tunable("inflight-done-ready-hours", self.w.seat), 4)
        self.assertEqual(len([l for l in self.sweep(13) if "W11 phase age: row #569 in done-ready" in l]), 1)

    def read_cli(self, *names):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = ib.cli(["read", *names], self.w.seat)
        self.keep(f"DYAD_SESSION={HOME} dyad inbox read {' '.join(names)}".rstrip(), rc, out.getvalue()[-400:], err.getvalue())
        return rc, out.getvalue(), err.getvalue()

    def test_s10_reading_is_an_event_with_no_side_effect(self):
        """S10: reports marked read unseen (#568, #571). Prevented: printing marks nothing; a read is the event `read`
        naming what was read, which marks exactly the named messages in one land and, a self-loop with no effect on
        the phased entry, leaves board/568.md byte-identical: still verifying, still waiting on the reader."""
        self.w.write_main(row(568) | phased(568, "building", {"unit": [COU]}, COU))
        rc, out, err = self.adv("568", "pr-up", "--expect", "building", "pr=638", "head=" + "2" * 40, session=COU)
        self.assertEqual(rc, 0, out + err)
        board_text, before = self.show("board/568.md"), self.main_sha()
        rc, out, err = self.read_cli()
        self.assertEqual(rc, 0, err)
        self.assertIn(f"row #568 report from {COU}", out); self.assertIn(f"inbox {HOME}: 1 unread, none marked", out)
        self.assertEqual(self.main_sha(), before)                                       # printing landed nothing
        r = subprocess.run(["git", "ls-tree", "--name-only", f"main:{INST}/d-work/inbox/{HOME}"], cwd=self.w.origin,
                           capture_output=True, text=True)
        (name,) = [n.removesuffix(".md") for n in r.stdout.split() if n.endswith(".md")]
        self.assertNotIn(f"{name}.read", r.stdout.split())
        rc, out, err = self.read_cli(name)
        self.assertEqual(rc, 0, err)
        self.assertIn("board #568: read at verifying, nothing changed", out)
        self.assertEqual(git(self.w.origin, "rev-list", "--count", f"{before}..main"), "1")
        changed = git(self.w.origin, "diff", "--name-only", before, "main").splitlines()
        self.assertIn(f"{INST}/d-work/inbox/{HOME}/{name}.read", changed)
        self.assertNotIn(f"{INST}/d-work/board/568.md", changed)
        self.assertEqual(self.show("board/568.md"), board_text)                          # byte-identical
        f = self.entry(568)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("verifying", f"unit {HOME}"))
        self.assertIn("read", dyadlib.ORCH_NO_EFFECT)
        self.assertEqual(dyadlib.ORCH_EVENTS[("verifying", "read")], (("verifying",), "home or unit", ()))
        rc, _, err = self.read_cli(name)
        self.assertEqual(rc, 1); self.assertIn("already read", err)

    # ---- S11 (2026-11-05T05:29:17Z) and plan revision 2
    def test_s11_a_question_asked_of_a_planned_row_is_never_flipped_away(self):
        """S11, the unphased path the day ran: row 570 planned under `Y plan` (revision 8), home asks revision 9 on its
        board in a later commit. K1's flip read the older `Y plan` as fresh and erased the question (c31d76d); the
        automaton now proposes nothing on it (board_after_plan_y)."""
        self.w.write_main(row(570, disposed="2026-11-04 Y plan; 2026-11-05 Y plan (revision 8)")
                          | {f"{INST}/d-work/board/570.md": f"holder: {HOME}\nowner: {AUD} s1\nwaiting-on: unit {AUD}\nwriter: h1\n"})
        asked = (f"holder: {HOME}\nowner: {AUD} s1\nwaiting-on: operator\nnext: answer plan revision 9\n"
                 "question: Y/N: proceed with #570 revision 9 as planned?\nwriter: h1\n")
        self.w.write_main({f"{INST}/d-work/board/570.md": asked})
        rc, out, err = self.auto("scan")
        self.assertEqual(rc, 0, out + err); self.assertNotIn("board #570", out)      # K2's notice stands; no K1 flip
        self.auto("run")
        self.assertEqual(self.show("board/570.md"), asked)

    def test_s11_phased_a_revision_asked_through_the_machine_is_never_caught_up(self):
        """S11 on the phased path: NOT caught. The machine has no edge from building back to a plan question (F5's
        `amend` was not built), so a revision of a planned row is asked by re-entering the entry (drop, `opened`,
        `plan-landed`, `asked`); the catch-up then reads the row's older `Y plan` as this question's answer and moves the
        entry to building, the question gone — S11's mechanism on the phased path, found by these replays; fixed on
        #664 (catch_ups applies board_after_plan_y), so the question stands."""
        self.w.write_main(row(570, disposed="2026-11-04 Y plan; 2026-11-05 Y plan (revision 8)"))
        for argv in (("opened", "--expect", "none", f"unit={AUD}"), ("plan-landed", "--expect", "planning"),
                     ("asked", "--expect", "plan-ready")):
            rc, out, err = self.adv("570", *argv, session=AUD if argv[0] == "plan-landed" else HOME)
            self.assertEqual(rc, 0, out + err)
        q = self.entry(570)["question"]
        rc, out, _ = self.auto("scan")
        self.auto("run")
        self.assertEqual((bd.phase_name(self.entry(570)), self.entry(570).get("question")), ("plan-asked", q))

    def test_r2_573_combined_red(self):
        """Revision 2: #573's PRs #642, #651 (stacked on #642) and #652 pass alone and fail together. With every PR up
        at its recorded head, the automaton's run merges the three onto main, takes the evidence, fires
        `evidence-failed` with the FAIL line as the note, relays the unit and names the ring owed — no unit's turn."""
        a = self.w.pr(642, "dyad/zz-642-surface.txt", "aliases: attended-seats -> paired-units (alias)\n")
        b = self.w.pr(651, "dyad/zz-651-test-s3.txt", "stale filter exempts moving rows only\n", base=a)
        c = self.w.pr(652, "dyad/zz-652-rename.txt", "attended-seats -> paired-units\n")
        for sha in (a, b, c):
            self.assertEqual(evidence_by_tree(self.w.origin, sha)[0], 0)        # each alone: fail 0, as reported
        self.w.write_main(row(573) | phased(573, "verifying", {"unit": [ENG], "pr": [f"642 at {a}", f"651 at {b}", f"652 at {c}"]},
                                            f"{ENG}; {COU}; {ORC}"))
        rc, out, _ = self.auto("scan")
        self.assertIn("evidence #573: combined merge of PR #642", out)
        rc, out, err = self.auto("run")
        self.assertEqual(rc, 0, out + err)
        f = self.entry(573)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("building", f"unit {ENG}"))
        self.assertIn(S3_FAIL, f["note"])
        self.assertTrue([m for m in self.box(ENG) if m["kind"] == "relay" and m["from"] == "automaton"])
        self.assertIn(f"ring owed: {ENG}", out)

    def test_r2_572_stale_head(self):
        """Revision 2: #572's Done draft names #650 at f40c4bcf; #650 moves an hour later. The automaton's run sees the
        live head differ from the recorded one, fires `head-moved` (done-ready -> verifying, the new head recorded, the
        evidence withdrawn, the holder told), then verifies the new heads in the same run — no unit's turn."""
        h644 = self.w.pr(644, "dyad/zz-644.txt", "644\n")
        h649 = self.w.pr(649, "dyad/zz-649.txt", "649\n")
        h650 = self.w.pr(650, "dyad/zz-650.txt", "650 at f40c4bcf\n")
        self.w.write_main(row(572) | phased(572, "done-ready", {"unit": [ORC], "evidence": [EV],
                                                                "pr": [f"644 at {h644}", f"649 at {h649}", f"650 at {h650}"]},
                                            f"{ORC}; {ENG}; {COU}"))
        moved = self.w.pr(650, "dyad/zz-650.txt", "650 at 9bbb5cc8\n")
        rc, out, _ = self.auto("scan")
        self.assertIn(f"head-moved #572 from done-ready: PR #650 now at {moved}", out)
        rc, out, err = self.auto("run")
        self.assertEqual(rc, 0, out + err)
        log = git(self.w.origin, "log", "-2", "--format=%s", "main").splitlines()
        self.keep("git log -2 --format=%s main", 0, "\n".join(log) + "\n", "")
        self.assertIn("head-moved (done-ready -> verifying)", log[1]); self.assertIn("verifying -> done-ready", log[0])
        self.assertEqual(self.heads(572), [(644, h644), (649, h649), (650, moved)])
        self.assertTrue([m for m in self.box(HOME) if f"PR #650 moved to {moved}" in m["body"]])


if __name__ == "__main__":
    unittest.main()
