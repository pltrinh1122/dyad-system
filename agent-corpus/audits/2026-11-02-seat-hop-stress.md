# Seat-hop stress test by simulation — findings (2026-11-02)

*Audit of PR #591's simulator, d-work #546, seat audit-e73be78c. It runs the matrix and grades each scenario against
plan #546's oracle. It detects and disposes nothing: the backlog rows proposed below are opened by the cos under
#546's mandate (ceiling 8).*

**Run:** PR #591 at head `9839d8aa53dbe6b836fc1659da8c3260ccb74a80`, in a detached worktree, with
`python3 -m unittest -v dyad.tests.sim.test_seat_hops`: `Ran 43 tests in 60.983s`, `OK (expected failures=8)`. No
unexpected success and no FAIL. Grading was done by reading `dyad/tests/sim/test_seat_hops.py` and
`dyad/tests/sim/world.py` at that head, plus one probe (below). It does not rely on the PR's description.

## How the harness keeps an expected failure honest
Each known gap has two tests:
- **Its own test** (`gap()`) asserts that the oracle's violations are *exactly* the gap's own list.
- **Its oracle test** is an `expectedFailure` asserting there are none.

So a fix turns the gap test red, a different or additional loss turns it red, and a gap with no named reason fails
`test_every_known_gap_is_named_and_reasoned`. That answers the mode-E risk this seat raised before the run (an xfail
hiding a failure the plan did not predict): an xfail here cannot absorb a second mechanism unseen. This is verified
in the code, not taken from the PR text.

## Per scenario

| scenario | hop (a) | at (b) | in flight (c) | other axes | result | oracle violation | mode | owner |
|---|---|---|---|---|---|---|---|---|
| S1 | cc | idle | — | | pass | — | | |
| S2 | cc | idle | question | lost push | pass | — | | |
| S3 | cc | before write-ahead | dispatch | | pass | — | | |
| S4 | cc | after write-ahead | dispatch | | pass | — | | |
| S5 | cc | idle | dispatch | report to the old id | **xfail** | lost: dispatch task-5 | — | #536 acceptance |
| S6 | ct | idle | dispatch | | **xfail** | lost: dispatch task-5 | — | #536 acceptance |
| S7 | cc | idle | dispatch | terminal desk | pass | — | | |
| S8 | cc | after write-ahead | dispatch | two holders | **xfail** | executed twice: task-5 (2 times) | — | #537 acceptance |
| S9 | cc | idle | question | stale board | **xfail** (F1) | visible: the closed row's question | T | proposed P1 |
| S10 | cc | merge | promised | lost push | pass | — | | |
| S11 | cc | release | gate | | pass | — | | |
| S12 | cc | idle | question | attended seat | pass | — | | |
| S13 | cc | idle | question | two cabinets | **xfail** (F2) | visible: cabinet B's question | R | proposed P2 |
| S14 | tc | idle | question | hosting unreachable | pass | — | | |
| S15 | tt | idle | promised | clock skew | pass (oracle); **xfail** (F3) on "skew reported" | negative age, unreported | E | proposed P3 |
| S16 | ct | before write-ahead | question | | pass | — | | |
| S17 | ct | after write-ahead | gate | | pass | — | | |
| S18 | ct | merge | relay | | **xfail** | lost: relay answer-5 | — | #536 acceptance |
| S19 | ct | release | promised | | pass | — | | |
| S20 | tc | before write-ahead | gate | | pass | — | | |
| S21 | tc | after write-ahead | relay | | pass | — | | |
| S22 | tc | merge | dispatch | | pass | — | | |
| S23 | tt | before write-ahead | relay | | pass | — | | |
| S24 | tt | after write-ahead | question | | pass | — | | |
| S25 | tt | merge | gate | | pass | — | | |
| S26 | tt | release | dispatch | | **xfail** | lost: dispatch task-5 | — | #536 acceptance |
| S27 | cc | idle | relay | | pass | — | | |
| S28 | tc | before write-ahead | promised | | pass | — | | |
| S29 | tc | release | question | | pass | — | | |
| S30 | cc | idle | gate | | pass | — | | |
| S31 | cc | after write-ahead | promised | | pass | — | | |
| S32 | cc | merge | question | | pass | — | | |
| S33 | cc | release | relay | | pass | — | | |

Hops: cc = cloud→cloud, ct = cloud→terminal, tc = terminal→cloud, tt = terminal→terminal.

The totals are 26 scenarios passing the oracle (S15 included) and 7 failing it as expected (S5, S6, S8, S9, S13,
S18, S26). With S15's skew test, which is a separate expected failure, that is the run's 8 expected failures. The
43 tests also include the gap, axis and reason tests, and none fail.

## The xfails beyond the plan's S5, S6 and S8

- **S18 and S26 are #536's inbox gap, and nothing else.** Both have a terminal new holder (ct, tt), a dispatch or
  relay in flight, and a hop after the write-ahead. The gap test asserts the single violation `lost: <c> <task> (its
  report never reached the holder)`: the S6 mechanism exactly, a holder that reads no `send_message`.
  `KNOWN_GAPS` derives them by that rule (terminal new holder, `c` in dispatch/relay, `b` not before-wa). The rule's
  edges agree:
  - S23 (tt, before-wa, relay) passes, because nothing was dispatched.
  - S21 (tc, after-wa, relay) passes, because the new holder is cloud.
  - S24 (tt, after-wa, question) passes, because a question rides the board, not a message.

  Confirmed: these are #536 acceptance tests, not new rows.
- **S9, S13 and S15-skew are findings F1, F2 and F3**, each with its own gap test and reason. They are not
  predicted by the plan and not #536's or #537's, so they are proposed below as rows.

## Findings this audit adds

**F4: the fill is pairwise over three of the six axes.** `test_the_set_covers_the_axes` checks two things: every
value of every axis appears at least once, and every *pair* of (a)×(b)×(c) values is some scenario's. The fill
S16–S33 fixes (d) secretaries, (e) one cabinet and (f) none. Each value of (d), (e) and (f) other than those appears
in exactly one scenario, at cc or one fixed hop, so their pairs are not covered. Examples:
- two cabinets with a terminal hop;
- an unreachable hosting during a merge or release;
- two holders at a release gate;
- a terminal desk with a terminal cos;
- skew with an after-write-ahead dispatch.

The plan claimed "pairwise-covering the axes" (falsification attack 2). That holds for (a)(b)(c) and not for
(d)(e)(f), so it is mode E: an instrument narrower than the question it reports on. The fix is either to extend the
fill pairwise over all six axes, which the harness can do (each scenario is seconds), or to state the scope in the
plan and the harness docstring. Proposed as P4. It could ride #591 before its merge if the cos prefers.

**F5: the writer warning cannot tell a hop from two live holders (engineer's observation, confirmed).** In a probe
of `Run("cc", "after-wa", "dispatch")`, an ordinary hop with no second holder, the new holder's write of
`board/5.md` printed `warn: board/5.md was last written by h-old, not this session (h-new): two holders may be
writing`. In the idle question hops (`cc`, `tc`), the new holder wrote nothing and nothing printed. So the warning
fires on every hop in which the new holder writes an entry the old holder wrote. Its key, "the last writer differs",
does not identify "two holders live" (`board.writer_warning`, `dyad/guards/agent/board.py`). That is mode R, a
derived key that does not identify, and the same mechanism as incident row 228 (the presence writer before #350).
The lease is what tells a hop (a take) from a second holder. The warning itself names #537 as its arbiter, so this
is **#537's acceptance**, not a new row: under the lease, a hop by `take` does not warn and a second live holder
does.

**Stated limits (not findings):**
- **Oracle clause 3 cannot fail in this simulation.** "No question is asked of the Operator about state" is
  detected only as an Operator line beginning `state?` (`world.oracle`), and the simulated cos never generates one.
  The clause passes vacuously. The live hop (plan #546 method 2) is the only check of it.
- **The real harness classifier, a real Remote Control attach and real terminal mailboxes** are modelled, not run,
  as the plan states. A terminal holder "cannot read" its mailbox by construction (`world.py`).

## Proposed backlog rows (opened by the cos under #546's mandate; 4 of a ceiling of 8)

| # | mode | scenario | row | moment | owner |
|---|---|---|---|---|---|
| P1 | T | S9 (F1) | `dyad board resume` skips, or marks as stale, an entry whose row is terminal. The board guard already warns, and `--drop` cleans it, but resume still re-presents the closed row's question | resume | engineer |
| P2 | R | S13 (F2) | the board store and `_cos.md` are keyed by cabinet (the leader's seat or Operator), so one cabinet's resume never lists another's rows | resume and every board write | engineer |
| P3 | E | S15 (F3) | a `since` in the future relative to this host renders as `skew` with its size, never a negative age | board render | engineer |
| P4 | E | F4 | the fill covers every pair over all six axes, or the plan and harness state the three-axis scope | the suite | engineer (may ride #591) |

Not rows, by #546's mandate: S5, S6, S18 and S26 go to #536 as its acceptance tests; S8 and F5 go to #537 as its
acceptance tests. They are to be appended to those rows' plans when they are worked.
