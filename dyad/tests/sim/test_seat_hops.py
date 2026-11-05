"""Seat-hop stress test by simulation (d-work #546; the subject is #535's board store and `dyad board resume`, P1 of
the cos as a mode). Each scenario scripts a hop of the cos mode from one session to another over the simulator's world
(`world.py`: a bare origin, one clone per session, the inbox (#536), seats, the Operator's log)
and then judges the plan's oracle:
- no item in flight is lost;
- no act is executed twice;
- no question about state is asked of the Operator;
- at most one line, "cos resumed in <session>", is visible to the Operator beyond the questions it truly owes.

The scenario set is `SCENARIOS`, the exact list: S1–S15 as plan #546 names them, then S16–S33, the greedy pairwise fill.
That fill covers every pair of values across axes (a) where, (b) when and (c) what, and every value of axes (d)–(f)
at least once. 25 pairs of (b)×(c) alone need more than the plan's estimated nine (S16–S24); `test_the_set_covers_the_axes`
checks the coverage.

A **known gap** is a scenario whose oracle P1 does not meet, by design or by a finding. It is two tests, never a skip:
- `test_Sn` asserts the violations are exactly the gap's;
- `test_Sn_oracle` is an `expectedFailure` asserting none.

So when the gap is fixed, the first fails and the second turns into an unexpected success: both are red until the
expectation is updated. #536 (the inbox, with #547 and #551) turned S5, S6, S9, S18 and S26 from gaps into passes. S8
stays #537's (lease) acceptance test, and S13 is finding F2 (#548), both in `KNOWN_GAPS`; S15's skew report is F3.

Not simulated, stated: the real harness's classifier, a real Remote Control attach, and a real `send_message`
transport.
"""
import itertools, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import world as W
from world import Host, Item, Operator, oracle

SCRATCH = W.livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup

A = {"cc": ("cloud", "cloud"), "ct": ("cloud", "terminal"), "tc": ("terminal", "cloud"), "tt": ("terminal", "terminal")}
B = ("idle", "before-wa", "after-wa", "merge", "release")
C = ("question", "dispatch", "gate", "relay", "promised")
D = ("secretaries", "terminal-desk", "attended")
E = ("one", "two")
F = ("none", "two-holders", "stale-board", "lost-push", "unreachable", "clock-skew")

# (id, a, b, c, d, e, f): S1–S15 as the plan names them, S16–S33 the pairwise fill over (a)×(b)×(c).
SCENARIOS = [
    ("S1", "cc", "idle", None, "secretaries", "one", "none"),
    ("S2", "cc", "idle", "question", "secretaries", "one", "lost-push"),
    ("S3", "cc", "before-wa", "dispatch", "secretaries", "one", "none"),
    ("S4", "cc", "after-wa", "dispatch", "secretaries", "one", "none"),
    ("S5", "cc", "idle", "dispatch", "secretaries", "one", "none"),
    ("S6", "ct", "idle", "dispatch", "secretaries", "one", "none"),
    ("S7", "cc", "idle", "dispatch", "terminal-desk", "one", "none"),
    ("S8", "cc", "after-wa", "dispatch", "secretaries", "one", "two-holders"),
    ("S9", "cc", "idle", "question", "secretaries", "one", "stale-board"),
    ("S10", "cc", "merge", "promised", "secretaries", "one", "lost-push"),
    ("S11", "cc", "release", "gate", "secretaries", "one", "none"),
    ("S12", "cc", "idle", "question", "attended", "one", "none"),
    ("S13", "cc", "idle", "question", "secretaries", "two", "none"),
    ("S14", "tc", "idle", "question", "secretaries", "one", "unreachable"),
    ("S15", "tt", "idle", "promised", "secretaries", "one", "clock-skew"),
] + [(f"S{16 + i}", a, b, c, "secretaries", "one", "none") for i, (a, b, c) in enumerate([
    ("ct", "before-wa", "question"), ("ct", "after-wa", "gate"), ("ct", "merge", "relay"), ("ct", "release", "promised"),
    ("tc", "before-wa", "gate"), ("tc", "after-wa", "relay"), ("tc", "merge", "dispatch"), ("tt", "before-wa", "relay"),
    ("tt", "after-wa", "question"), ("tt", "merge", "gate"), ("tt", "release", "dispatch"), ("cc", "idle", "relay"),
    ("tc", "before-wa", "promised"), ("tc", "release", "question"), ("cc", "idle", "gate"), ("cc", "after-wa", "promised"),
    ("cc", "merge", "question"), ("cc", "release", "relay")])]

GAP_537 = ("#537 (lease): two live holders both act on one written-ahead entry — since #552's write-ahead fence, only "
           "when the old holder relays and stops before recording it sent, so the new holder relays again")
KNOWN_GAPS = {
    "S8": GAP_537,
    "S13": "F2 (finding, #546; row #548): one board store and one `_cos.md` for two cabinets: resume lists the other leader's rows and the new holder re-presents its questions to this Operator",
}

QUESTION = "Y/N: approve the release of row 5?\n(evidence 3f1c…; the run waits at its gate)"
PROMISE = "report #514 after season 1"
OLD, SEAT = "program-aaaaaaaa", "engineer-11111111"
NEW = OLD   # the mode keeps its seat across a hop; only the holder (the harness session) changes


def host(kind: str, name: str, **kw) -> Host:
    return Host(name, kind, **kw)


class Run:
    """One scripted hop: the old holder puts `c` in flight on row 5, the hop happens at `b`, the new holder resumes and
    the world settles; then the oracle."""
    def __init__(self, a="cc", b="idle", c=None, *, seat_kind="cloud", new_os="linux", report_at_hop=False,
                 relayed_unrecorded=False,
                 two_holders=False, outage=False, skew=0, race=False):
        self.w = W.World(SCRATCH, rows={5: "planned", 6: "done", 8: "planned"}, pr=(b == "merge"))
        self.op = Operator()
        old_kind, new_kind = A[a]
        self.old = self.w.cos(OLD, host(old_kind, "old", skew_minutes=skew), "h-old", self.op)
        self.seat = self.w.seat(SEAT, host(seat_kind, "seat"), "h-seat")
        self.truth, self.owed = [], []
        crash = b if b in ("before-wa", "after-wa") else None
        self.put(c, crash)
        if b == "merge":
            self.old.s.set(9, next=f"merge 7 at {self.w.pr_sha}", waiting_on="unit " + SEAT)
            self.w.merge(self.old.s, 7, self.w.pr_sha)            # landed; the hop comes before the board says so
        if b == "release":
            self.w.runs["42"] = "pending"
            self.old.gate(8, "42")
            self.truth.append(Item("gate", "42", 8))
        if relayed_unrecorded:
            self.old.send_pending(5, finish=False)                # relayed, then stopped before recording it sent
        if report_at_hop:
            self.seat.step()                                      # the seat acts and reports while the old holder dies
        self.mark = len(self.op.lines)
        self.new = self.w.cos(NEW, host(new_kind, "new", os=new_os), "h-new", self.op)
        if outage:
            self.w.outage()
        if race:
            self.w.arm_race()
        self.resumed = self.new.resume()
        self.released_early = sum(n for k, n in self.w.acts.items() if k.startswith("release "))
        if two_holders:
            self.old.send_pending(5)                              # the old holder was not dead: it finishes its turn
        self.w.settle(self.new)
        for run in self.w.runs:
            self.w.runs[run] = "completed"
        self.new.read_reports()

    def put(self, c, crash) -> None:
        if c is None:
            return
        in_flight = crash != "before-wa"
        if c == "question":
            self.old.ask(5, QUESTION, crash)
            if in_flight:
                self.truth.append(Item("question", QUESTION, 5)); self.owed.append(QUESTION)
        elif c in ("dispatch", "relay"):
            task = "task-5" if c == "dispatch" else "relay answer-5"
            self.old.dispatch(5, self.seat, task, crash)
            if in_flight:
                self.truth.append(Item(c, task, 5))
        elif c == "gate":
            self.w.runs["41"] = "pending"
            self.old.gate(5, "41", crash)
            if in_flight:
                self.truth.append(Item("gate", "41", 5))
        elif c == "promised":
            self.old.promise(5, PROMISE, crash)
            if in_flight:
                self.truth.append(Item("promised", PROMISE, 5))

    def violations(self) -> list[str]:
        v = oracle(self.w, self.truth, self.op, self.mark, self.new, self.owed)
        if self.w.pr_sha and self.w.landings(self.w.pr_sha) != 1:
            v.append(f"merge of PR #7 landed {self.w.landings(self.w.pr_sha)} times")
        if self.released_early:
            v.append("executed early: a release recorded before its run completed")
        return v


class SeatHopTests(unittest.TestCase):
    maxDiff = None

    def gap(self, sid, got, expected):
        """A known gap's own test: the violations are exactly the gap's, so a fix or a new loss both turn it red."""
        self.assertIn(sid, KNOWN_GAPS)
        self.assertEqual(got, expected, f"{sid}: {KNOWN_GAPS[sid]}")

    # ---- S1–S15
    def test_S1_idle_hop_owes_nothing(self):
        r = Run("cc", "idle")
        self.assertIn("owed to the Operator (0)", r.resumed)
        self.assertEqual(r.new.s.entries()["_cos"]["holder"], NEW)
        self.assertEqual(r.violations(), [])
        self.assertEqual(r.op.lines[r.mark:], [W.RESUMED.format(seat=NEW)])

    def test_S2_an_open_question_is_re_presented_verbatim_once(self):
        r = Run("cc", "idle", "question", race=True)              # the new holder's first write loses a push race
        self.assertEqual(r.op.lines[r.mark:], [W.RESUMED.format(seat=NEW), QUESTION])
        self.assertEqual(r.violations(), [])
        self.assertEqual(r.w.raced, 1)

    def test_S3_a_crash_before_write_ahead_loses_and_doubles_nothing(self):
        r = Run("cc", "before-wa", "dispatch")
        self.assertEqual(r.w.acts["task-5"], 0)                  # never dispatched, so nothing in flight to lose
        self.assertEqual(r.violations(), [])

    def test_S4_after_write_ahead_the_new_holder_sends_once(self):
        r = Run("cc", "after-wa", "dispatch")
        self.assertEqual(r.w.acts["task-5"], 1)
        self.assertEqual(r.violations(), [])

    def test_S5_a_report_sent_at_the_hop_reaches_the_new_holder(self):
        r = Run("cc", "idle", "dispatch", report_at_hop=True)
        self.assertEqual(r.w.acts["task-5"], 1)
        self.assertIn("task-5", r.w.completed)                    # addressed to the mode's seat, read by the new holder
        self.assertEqual(r.violations(), [])

    def test_S6_a_terminal_holder_reads_its_inbox(self):
        r = Run("ct", "idle", "dispatch", new_os="mac")
        self.assertIn("task-5", r.w.completed)
        self.assertEqual(r.violations(), [])

    def test_S7_a_terminal_desk_reports_by_its_inbox(self):
        r = Run("cc", "idle", "dispatch", seat_kind="terminal")
        self.assertEqual(r.w.acts["task-5"], 1)
        self.assertIn("task-5", r.w.completed)
        self.assertEqual(r.violations(), [])

    def test_S8_a_stale_holders_relay_is_refused(self):
        """Two live holders: the old one finishes its turn after the new one resumed. Its relay is refused by the
        write-ahead fence, since the entry is the new holder's now (#552); the act runs once."""
        r = Run("cc", "after-wa", "dispatch", two_holders=True)
        self.assertTrue(any("was last written by h-new, not this session (h-old)" in l for l in r.old.refused), r.old.refused)
        self.assertEqual(r.old.s.warnings, [])                   # it never wrote: its stale view called the entry its own
        self.assertEqual(r.w.acts["task-5"], 1)
        self.assertEqual(r.violations(), [])

    def test_S8(self):
        r = Run("cc", "after-wa", "dispatch", relayed_unrecorded=True)
        self.gap("S8", r.violations(), ["executed twice: task-5 (2 times)"])

    @unittest.expectedFailure
    def test_S8_oracle(self):
        self.assertEqual(Run("cc", "after-wa", "dispatch", relayed_unrecorded=True).violations(), [])

    def stale(self):
        """S9: row 5 carries an open question on the board, then the row is closed under it; then the hop."""
        w = W.World(SCRATCH, rows={5: "planned", 6: "done"})
        op = Operator()
        old = w.cos(OLD, host("cloud", "old"), "h-old", op)
        old.ask(5, QUESTION)
        author = w.session("author", host("cloud", "a"), "h-author")
        rows = author.dir / W.INST / "d-work" / "rows" / "5.md"
        rows.write_text(W.ROW.format(id=5, state="done", disposed="2026-11-02 Y plan; 2026-11-02 Y done"))
        W.git(author.dir, "commit", "-qam", "ledger: #5 done"); W.git(author.dir, "push", "-q", "origin", "HEAD:main")
        mark = len(op.lines)
        new = w.cos(NEW, host("cloud", "new"), "h-new", op)
        new.resume()
        return w, op, mark, new

    def test_S9_a_stale_entry_is_marked_and_owes_nothing(self):
        w, op, mark, new = self.stale()
        with new.s.acting():
            msgs = W.bd.check_package(new.s.dir)
            view = W.bd.resume_view(new.s.dir)
        self.assertEqual([m.split(";")[0] for m in msgs], ["warning: board/5.md: row #5 is done"])   # the guard warns
        self.assertEqual(([n for n, _ in view["stale"]], view["owed"]), (["5"], []))                 # #547
        self.assertEqual(oracle(w, [], op, mark, new, []), [])
        self.assertEqual(new.s.board("set", "5", "--drop")[0], 0)                                     # --drop cleans it
        with new.s.acting():
            self.assertEqual(W.bd.check_package(new.s.dir), [])

    def test_S10_a_hop_during_dyad_merge_lands_once(self):
        r = Run("cc", "merge", "promised", race=True)            # merged before the hop; the new holder's merge refuses
        self.assertEqual(r.w.landings(r.w.pr_sha), 1)
        self.assertEqual(r.violations(), [])
        w = W.World(SCRATCH, rows={5: "planned"}, pr=True)        # and written ahead, not merged: the new holder merges
        op = Operator()
        old = w.cos(OLD, host("cloud", "old"), "h-old", op)
        old.s.set(9, next=f"merge 7 at {w.pr_sha}")
        new = w.cos(NEW, host("cloud", "new"), "h-new", op)
        w.arm_race()                                               # its merge push loses a race once, then lands
        new.resume()
        self.assertEqual(w.landings(w.pr_sha), 1)
        self.assertEqual(new.s.entries()["9"]["next"], "merged 7")

    def test_S11_a_gated_release_is_not_recorded_before_its_run(self):
        r = Run("cc", "release", "gate")
        self.assertIn("external gates (2): #5 external run 41; #8 external run 42", r.resumed)
        self.assertEqual(r.released_early, 0)
        self.assertEqual((r.w.acts["release 41"], r.w.acts["release 42"]), (1, 1))
        self.assertEqual(r.violations(), [])

    def test_S12_an_attended_seats_question_stays_in_its_chat(self):
        w = W.World(SCRATCH, rows={5: "planned"})
        op = Operator()
        old = w.cos(OLD, host("cloud", "old"), "h-old", op)
        w.seat("communicate-22222222", host("cloud", "c"), "h-comm")
        old.s.set(5, owner="communicate-22222222 h-comm", waiting_on="unit communicate-22222222",
                  next="attended: asks in its own chat")
        op.show(QUESTION)                                          # asked in the attended seat's own chat
        mark = len(op.lines)
        new = w.cos(NEW, host("cloud", "new"), "h-new", op)
        new.resume(); w.settle(new)
        self.assertEqual(op.lines[mark:], [W.RESUMED.format(seat=NEW)])
        self.assertEqual(oracle(w, [Item("question", QUESTION, 5)], op, mark, new, []), [])

    def cabinets(self):
        """S13: two leaders share the instance; A asks its Operator on row 5, B its own on row 8; A's leader hops."""
        w = W.World(SCRATCH, rows={5: "planned", 8: "planned"})
        op_a, op_b = Operator("A"), Operator("B")
        a = w.cos(OLD, host("cloud", "a"), "h-a", op_a)
        b = w.cos("program-cccccccc", host("cloud", "b"), "h-b", op_b)
        q_b = "Y/N: B's release of row 8?"
        a.ask(5, QUESTION); b.ask(8, q_b)
        mark = len(op_a.lines)
        a2 = w.cos(NEW, host("cloud", "a2"), "h-a2", op_a)
        a2.resume()
        return w, op_a, op_b, mark, a2, q_b

    def test_S13(self):
        w, op_a, op_b, mark, a2, q_b = self.cabinets()
        self.assertEqual(op_b.lines, [q_b])                        # B's leader and Operator are unaffected
        self.gap("S13", oracle(w, [Item("question", QUESTION, 5)], op_a, mark, a2, [QUESTION]),
                 [f"visible: {q_b!r} (not owed at the hop)"])

    @unittest.expectedFailure
    def test_S13_oracle(self):
        w, op_a, op_b, mark, a2, q_b = self.cabinets()
        self.assertEqual(oracle(w, [Item("question", QUESTION, 5)], op_a, mark, a2, [QUESTION]), [])

    def test_S14_hosting_unreachable_resumes_from_the_local_clone(self):
        r = Run("tc", "idle", "question", outage=True)
        self.assertIn(QUESTION.splitlines()[0], r.resumed)         # read from the local clone while unreachable
        self.assertEqual(r.w.outages_seen, 1)                      # its first write was refused, the retry landed
        self.assertEqual(r.violations(), [])

    def test_S15_clock_skew_keeps_the_oracle(self):
        r = Run("tt", "idle", "promised", skew=10)
        self.assertEqual(r.violations(), [])

    @unittest.expectedFailure
    def test_S15_skew_is_reported(self):
        """F3 (finding, #546): a `since` written by a host whose clock runs ahead renders as a negative age and is not
        reported as skew. The oracle holds (S15); this is the plan's "or the skew is reported"."""
        r = Run("tt", "idle", "promised", skew=10)
        line = next(l for l in r.new.s.board()[1].splitlines() if l.startswith("#5 "))
        self.assertNotIn("for -", line)

    # ---- the set
    def test_the_set_covers_the_axes(self):
        ids = [s[0] for s in SCENARIOS]
        self.assertEqual(ids, [f"S{n}" for n in range(1, 34)])
        for axis, values in ((1, tuple(A)), (2, B), (3, C), (4, D), (5, E), (6, F)):
            self.assertEqual({s[axis] for s in SCENARIOS if s[axis]} >= set(values), True, (axis, values))
        triples = [s[1:4] for s in SCENARIOS if s[3]]
        pairs = {(i, t[i], j, t[j]) for t in triples for i, j in ((0, 1), (0, 2), (1, 2))}
        need = {(0, a, 1, b) for a in A for b in B} | {(0, a, 2, c) for a in A for c in C} | {(1, b, 2, c) for b in B for c in C}
        self.assertEqual(need - pairs, set(), "every pair of (a)×(b)×(c) values is some scenario's")

    def test_every_known_gap_is_named_and_reasoned(self):
        for sid, why in KNOWN_GAPS.items():
            self.assertIn(sid, [s[0] for s in SCENARIOS])
            self.assertRegex(why, r"#537|F\d \(finding, #546; row #\d+\)")


def fill_test(sid, a, b, c):
    def test(self):
        r = Run(a, b, c)
        if sid in KNOWN_GAPS:
            task = "task-5" if c == "dispatch" else "relay answer-5"
            self.gap(sid, r.violations(), [f"lost: {c} {task} (its report never reached the holder)"])
        else:
            self.assertEqual(r.violations(), [])
    test.__doc__ = f"{sid}: {a} hop, at {b}, with {c} in flight (pairwise fill)"
    return test


def fill_oracle(a, b, c):
    @unittest.expectedFailure
    def test(self):
        self.assertEqual(Run(a, b, c).violations(), [])
    return test


for _sid, _a, _b, _c, *_ in SCENARIOS[15:]:
    setattr(SeatHopTests, f"test_{_sid}_{_a}_{_b.replace('-', '_')}_{_c}", fill_test(_sid, _a, _b, _c))
    if _sid in KNOWN_GAPS:
        setattr(SeatHopTests, f"test_{_sid}_oracle", fill_oracle(_a, _b, _c))


if __name__ == "__main__":
    unittest.main()
