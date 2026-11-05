# Orchestration replays through the machine (#587, 2026-11-05)

*Drafted by engineer-1537d8fb for row #587, the report its definition of done asks for. The branch is `587-replays`, on
`587-skeleton`: main, plus #587's PR2 (the machine), PR3 (the automaton's X5, X6 and X10, and the S11 fix) and PR4
(`dyad board draft`). Every replay runs in a scratch world. That world is a scratch install, a bare origin holding
`refs/pull/<n>/head`, a seat clone and a racer. The same world is the test module `dyad/tests/test_replays.py`. Each
output below is that module's transcript, trimmed to the decisive lines. The seat names, rows and PR numbers are the
day's. The heads are the scratch world's.*

**The DoD (plan #587).** Revision 1: "1. The transition table, one page: phases, events, the effect of each transition,
and who or what fires it. 2. Today's orchestration replayed through it (rows #564–#586, 2026-11-04). Each of today's
slips S1–S10 is shown as either refused or prevented by a transition, or put on the ring list home is shown. Each with
the command output. 3. The tests that pin the table." Revision 2 adds: "today's #573 combined red and #572's stale #650
head, replayed. Each must be caught by the automaton with no unit's turn." Home added S11.

**Verdicts at a glance.**

| case | verdict |
|---|---|
| S1, S4, S7, S8 | **prevented** by a transition |
| S2 | **refused**: derived, and hand writes are refused |
| S3, S5 | **prevented, partly** |
| S6 | **ring list**. The doorbell stays home's act (X8). |
| S9 | **partly**. The state is visible, but no timer fires at 13 h. |
| S10 | **not caught** |
| S11 | **prevented** on the unphased path; **not caught** on the phased path (a defect, section 4) |
| R2 #573 combined red | **caught by the automaton**, no unit's turn |
| R2 #572 stale #650 head | **caught by the automaton**, no unit's turn |

## 1. The transition table

The table below is `dyad board phases`, printed verbatim from `dyadlib.ORCH_EVENTS` and board.py's `DERIVE`.

```
phase | waiting-on | next
planning | unit {unit} | write plans/{id}.md; then: dyad board advance {id} plan-landed --expect planning
plan-ready | unit {holder} | ask the plan question: dyad board advance {id} asked --expect plan-ready
plan-asked | operator | record the Operator's answer: dyad board advance <the question's ids> answered-Y|answered-N --expect plan-asked --said-file <F>
building | unit {unit} | execute plans/{id}.md; then: dyad board advance {id} pr-up --expect building pr=<n> head=<sha>
verifying | unit {holder} | verify {prs} (dyad check --evidence on each head); then: dyad board advance {id} evidence-verified --expect verifying evidence=<sha256>
done-ready | unit {holder} | ask the Done question: dyad board advance {id} asked --expect done-ready
done-asked | operator | record the Operator's answer: dyad board advance <the question's ids> answered-Y|answered-N --expect done-asked --said-file <F>
landing | {merge} | the automaton merges {prs}, then closes the row
held | {on} | held (see note): dyad board advance {id} release --expect held

from | event | to | actor | required fields
none | opened | planning | home | unit
none | plan-landed | plan-ready | unit | -
none | pr-up | verifying | unit | pr, head
planning | hold | held | home | note, on
planning | plan-landed | plan-ready | unit | -
plan-ready | asked | plan-asked | home | -
plan-ready | hold | held | home | note, on
plan-asked | answered-N | planning | home | said-file
plan-asked | answered-Y | building | home | said-file
plan-asked | hold | held | home | note, on
building | evidence-verified | done-ready | home | evidence
building | hold | held | home | note, on
building | pr-up | verifying | unit | pr, head
verifying | evidence-failed | building | home or automaton | note
verifying | evidence-verified | done-ready | home or automaton | evidence
verifying | head-moved | verifying | automaton | pr, head
verifying | hold | held | home | note, on
verifying | pr-up | verifying | unit | pr, head
done-ready | asked | done-asked | home | -
done-ready | head-moved | verifying | automaton | pr, head
done-ready | hold | held | home | note, on
done-asked | answered-N | building | home | said-file
done-asked | answered-Y | landing or (closed) | home | said-file
done-asked | head-moved | verifying | automaton | pr, head
done-asked | hold | held | home | note, on
done-asked | withdrawn | done-ready | automaton | note
landing | closed | (closed) | automaton | -
held | release | @from | home | -
```

**The effect of each transition.** `dyad board advance` writes all of them in one ledger-only commit, or writes none.

- **Board.** `phase`, `waiting-on`, `next` and `since` are derived, as above. `question` exists only in an asked phase.
  `owner` accumulates the unit.
- **Messages.** The relay or report is fixed by `board.RELAYS`, keyed by event and target:
  - `opened`, `answered-N` and `evidence-failed` relay to the unit.
  - `plan-landed`, `pr-up`, `evidence-verified`, `head-moved` and `withdrawn` report to the holder. `pr-up` and
    `head-moved` cc every other owner.
  - A plan-`Y`, a Done-`Y`, `hold` and `release` send a notice to every owner.
  - Nobody receives a message they sent.
- **Ledger, for an answer.** The ledger line, composed from the stored question. The provenance entry, from
  `--said-file`. The trace check.
- **Ring list.** It prints `ring: …`. The automaton prints `ring owed: …`.

`--expect` refuses an event when the phase has moved (X9). The automaton fires its own events:

- `head-moved` and `withdrawn` (X6);
- `evidence-verified` and `evidence-failed` on the combined merge (X5);
- `closed` (`steps.close_landed`);
- the catch-up of a `Y` that home recorded by hand.

## 2. The replays

Every command runs in the scratch world. `dyad board …` is `bd.cli`, which `dyad board` routes to. `dyad automaton …`
is `automaton.main`, with two stubs. `corroborate` is stubbed. `evidence_at` is a stub that reads the cut's own tree,
because the real `check --evidence` runs the whole suite. What is replayed is the firing, not the suite.

### S1. Distribute was idle on #564 and was never told #631 was up
**Mechanism.** No state said "PR up → relay distribute".
**Replay.** #564 is at `building`. Its owners are engineer, distribute, counsel and orchestrate, as on main at
16:44Z on 2026-11-03.
```
$ DYAD_SESSION=engineer-1537d8fb dyad board advance 564 pr-up --expect building pr=631 head=ab12cd34…
posted …-engineer-1537d8fb-1.md to program-59cec502 (cc distribute-a603e150, counsel-0032b4c0, orchestrate-d688fecf)
ring: program-59cec502, distribute-a603e150, counsel-0032b4c0, orchestrate-d688fecf (a doorbell is the session's act, #586 X4)
```
**Caught by** `(building, pr-up)` and its report, which cc's every other owner. **Prevented.** Distribute is told in
the same commit and is named on the ring list.

### S2. #498/#503 were marked waiting on communicate, but were actually waiting on the operator
**Mechanism.** `waiting-on` was hand-written and never derived.
```
$ DYAD_SESSION=program-59cec502 dyad board advance 498 hold --expect building note=the operator's persona corrections in the paired communicate chat on=operator
(exit 0)                                    # waiting-on: operator (derived from held's `on`)
$ dyad board set 498 waiting-on=unit communicate-17f24597
refused: board/498.md carries phase held: its derived fields are written by `dyad board advance` (#587 X1); not waiting-on
(the board guard over the file hand-edited the same way)
board/498.md: 'waiting-on' is 'unit communicate-17f24597'; phase held derives 'operator' — dyad board advance is its only writer (#587 X1)
```
**Refused** by X1's derivation, by `board set`'s refusal and by the guard's drift check.

### S3. Orchestrate was missing from the unit table
**Mechanism.** The `_cos` seat table was hand-written.
**Replay.** The `_cos` seat table omits orchestrate.
```
$ dyad board advance 573 opened --expect none unit=orchestrate-d688fecf
posted …-program-59cec502-1.md to orchestrate-d688fecf
ring: orchestrate-d688fecf (…)
$ dyad board resume
announce to (1): orchestrate-d688fecf; seat table: program-59cec502 (home); engineer-1537d8fb; counsel-0032b4c0
```
**Prevented, partly.** `opened` makes the unit an owner. Relays, the ring list and `resume` all read owners, so routing
no longer depends on the table. The table itself is still hand-written and unchecked, and the stale table above shows
it.

### S4. Counsel's #567/#568 PRs were up, but the board still said "waiting on counsel"
**Mechanism.** The board was not advanced by the report.
```
$ DYAD_SESSION=counsel-0032b4c0 dyad board advance 567 pr-up --expect building pr=637 head=1111…
posted … to program-59cec502 (cc engineer-1537d8fb)
$ DYAD_SESSION=counsel-0032b4c0 dyad board advance 568 pr-up --expect building pr=638 head=2222…
$ dyad board
#567 planned  phase verifying waiting-on unit program-59cec502 … | next: verify PR #637 at 1111… (dyad check --evidence on each head) …
#568 planned  phase verifying waiting-on unit program-59cec502 … | next: verify PR #638 at 2222… …
```
**Prevented** by `(building, pr-up)`. The report and the board move in one commit.

### S5. Orchestrate had 10 unread copies for 13 h
**Mechanism.** No state named who must act next.
```
$ dyad board advance 573 opened --expect none unit=orchestrate-d688fecf
posted …-program-59cec502-1.md to orchestrate-d688fecf        # waiting-on: unit orchestrate-d688fecf
(the sweep's inflight, 13 h later)
inflight W1 relay unread: row #573's relay to orchestrate-d688fecf sent 2026-11-05T06:55:25Z has no read marker (over 4h)
```
**Prevented, partly.**
- One seat is named as acting next.
- A relay goes to the unit only. A report goes to the holder, with cc's: one message, not one copy per seat.
- The unread relay is the sweep's W1 after 4 h. W1 predates #587; it came with #569.

What is not prevented: a seat can still leave its inbox unread. W1 tells home, and the ring is home's act.

### S6. B3's relays had no doorbell
**Mechanism.** Ringing was left to memory.
```
$ dyad board advance 573 evidence-failed --expect verifying note=combined merge fails test_s3
posted …-program-59cec502-1.md to orchestrate-d688fecf
ring: orchestrate-d688fecf (a doorbell is the session's act, #586 X4)
```
**On the ring list.** Every advance that posts a message prints the seats to ring, and so does every automaton act
(`ring owed: …`, section R2). The doorbell itself stays home's act: X8 is a confirmed limit, since the CLI cannot call
`send_message`. An unrung relay is backstopped by W1.

### S7. Relays were sent before #573's record
**Mechanism.** Record, board and relays were separate commands.
```
$ dyad board advance 573 answered-Y --expect plan-asked --said-file said.txt
573: planned
posted …-program-59cec502-1.md to orchestrate-d688fecf
$ git show --name-only main
agent-corpus/d-work/board/573.md
agent-corpus/d-work/inbox/orchestrate-d688fecf/…-program-59cec502-1.md
agent-corpus/d-work/provenance/573.md
agent-corpus/d-work/rows/573.md
agent-corpus/d-work/sessions/program-59cec502.md
$ dyad board advance 574 answered-Y --expect plan-asked --said-file said.txt     # row 574 is blocked on origin
transition blocked→planned not in the table (Rule-16); allowed from blocked: open
refused: line 1 (state 574 planned -d 'Y plan' --said-file …): dwork state refused it in the worktree; the batch stops and nothing landed
```
**Prevented.** The row, the words, the board and the relay land in one commit. A refused ledger line lands no board and
no relay; main is unchanged.

### S8. A relay was refused three times because the receiver was not an owner
**Mechanism.** Owners were hand-written.
```
$ DYAD_SESSION=engineer-1537d8fb dyad inbox post orchestrate-d688fecf --row 574 --kind relay 'verify PR #646'
refused: a relay needs its board entry first (write-ahead, #552): board/574.md names owner(s) counsel-0032b4c0, not orchestrate-d688fecf
$ dyad board advance 574 opened --expect none unit=orchestrate-d688fecf
posted …-program-59cec502-1.md to orchestrate-d688fecf
ring: orchestrate-d688fecf (…)
```
**Prevented** by `(none, opened)`. It adopts the unphased entry and adds the unit to `owner` in the same commit as its
relay. `owner` is now counsel-0032b4c0; orchestrate-d688fecf.

### S9. #569's Done was held 13 h after its draft
**Mechanism.** No state said "done-ready, not asked".
**On main.** The draft is from 02:11Z, the board waited on home, and the question was asked at 15:26Z.
```
$ dyad board advance 569 evidence-verified --expect verifying evidence=8d0ba6f9…
$ dyad board
#569 planned  phase done-ready waiting-on unit program-59cec502 for 0h | … | next: ask the Done question: dyad board advance 569 asked --expect done-ready | row 569
queue (derived, #572): plan-ready 0, done-ready 1 (#569)
(the sweep's inflight, 13 h later)
                                                           # nothing
(the sweep's inflight, 73 h later)
inflight W11 phase age: row #569 in done-ready since 2026-11-05T06:55Z
```
**Partly.**
- The state now exists. The board, `resume` and the derived queue count it, and the `next` act says what is owed.
- Nothing fires at 13 h. W11's threshold for `done-ready` is 72 h; only the asked phases have 24 h. W2 is 3 days.
- The hold that happened is now visible, but it is not swept until day 3. Lowering `INFLIGHT_W11_HOURS["done-ready"]`
  is a tunable for the Operator.

### S10. Reports were marked read unseen (#568, #571)
**Mechanism.** Reading was a side effect, not an event.
```
$ DYAD_SESSION=counsel-0032b4c0 dyad board advance 568 pr-up --expect building pr=638 head=2222…
$ DYAD_SESSION=program-59cec502 dyad inbox read
* …-counsel-0032b4c0-1  row #568 report from counsel-0032b4c0 …
inbox program-59cec502: 1 marked read
```
After the read, board/568.md is unchanged: `verifying`, waiting on unit program-59cec502.

**Not caught.**
- Plan F7's survivor ("S10 becomes an event `read` with no side effect") was not built. `ORCH_EVENTS` has no `read`,
  and `inbox read` still marks a message read when it prints it.
- What #587 does change is the consequence. A phase moves only by an event, so a report marked read unseen no longer
  loses the state. The entry still names the reader, and the queue and W11 still see it.

### S11. The automaton's flip erased plan revision 9's question (05:29:17Z, c31d76d)
**Mechanism.** K1's `planned_flip` read row 570's older `Y plan` as fresh and overwrote home's later board write.

**Unphased path (the one the day ran).**
```
$ dyad automaton scan
notice audit-e73be78c: row #570 planned; read plans/570.md      # K2's notice; no "board #570" flip
$ dyad automaton run
posted a notice to audit-e73be78c (row #570)                     # board/570.md byte-identical: the question stands
```
**Prevented** by `board_after_plan_y`: a board written after the row's last `Y plan` is home's act.

**Phased path: not caught (a defect).** A revision of a planned row has no edge in the table: `building` has no way
back to a plan question, because F5's `amend` was not built. So home re-enters the entry, and the catch-up then reads
the older `Y plan` as this question's answer:
```
$ dyad board advance 570 opened --expect none unit=audit-e73be78c                 (exit 0)
$ DYAD_SESSION=audit-e73be78c dyad board advance 570 plan-landed --expect planning  (exit 0)
$ dyad board advance 570 asked --expect plan-ready
Y/N: proceed with #570 as planned?
$ dyad automaton scan
catch up #570 answered-Y (recorded on the ledger)
$ dyad automaton run
board #570: caught up answered-Y from plan-asked (recorded on the ledger)       # → building, the question gone
```
This is S11's mechanism, moved from `planned_flip` to `catch_ups`, which does not apply `board_after_plan_y`. It is
pinned as an expected failure, so the test flips when the defect is fixed. Section 4 lists the fix shapes.

### R2. #573's combined red
**Mechanism.** PR #642, PR #651 (stacked on #642) and PR #652 each pass alone. On main they fail together:
`FAIL [Rule-12] test_surface test_s3_preference_keys` (orchestrate's report, 17:50Z). Orchestrate found it with a
scratch merge by hand.
```
$ dyad automaton scan
evidence #573: combined merge of PR #642 at 4a502555…, PR #651 at 663c22e4…, PR #652 at 9befe996… onto main
$ dyad automaton run
posted …-automaton-1.md to engineer-1537d8fb
board #573: evidence-failed from verifying (note=combined evidence at 0eb2c6fa0d29: FAIL [Rule-12] test_surface test_s3_preference_keys: 'attended-seats' : an S3 key that is no preference); ring owed: engineer-1537d8fb (home rings, #587 X8)
```
**Caught by the automaton**, by X5 and `(verifying, evidence-failed)`. The row goes back to `building` with the FAIL
line as its note, and the unit is relayed. No unit takes a turn. The verdict comes from the stub (each head alone
passes, the three together fail). The real `check --evidence` is the stub's place in the job.

### R2. #572's stale #650 head
**Mechanism.** The Done draft (17:34Z) names #650 at f40c4bcf. #650 then moved to 9bbb5cc8, and nothing noticed.
```
$ dyad automaton scan
head-moved #572 from done-ready: PR #650 now at 2081cb20…
$ dyad automaton run
posted …-automaton-1.md to program-59cec502 (cc orchestrate-d688fecf, engineer-1537d8fb, counsel-0032b4c0)
board #572: head-moved from done-ready (head=2081cb20…, pr=650); ring owed: program-59cec502, orchestrate-d688fecf, engineer-1537d8fb, counsel-0032b4c0 (home rings, #587 X8)
board #572: evidence-verified from verifying (evidence=8d0ba6f9…); ring owed: program-59cec502 (home rings, #587 X8) [combined head 100d6d9df69b, evidence 8d0ba6f9e4c7]
$ git log -2 --format=%s main
ledger: board advance #572 evidence-verified (verifying -> done-ready), inbox program-59cec502 (report, row 572)
ledger: board advance #572 head-moved (done-ready -> verifying), inbox program-59cec502 (cc …) (report, row 572)
```
**Caught by the automaton**, by X6 `(done-ready, head-moved)`, then X5 in the same run.
- The new head is recorded and the old evidence is withdrawn. The holder is told, with the owners cc'd.
- The new heads are re-verified.
- No unit takes a turn. The Done question is asked again by home, on the new head.

## 3. The tests that pin the table and the replays

**The table.**
- `test_dyadlib.py`: `test_the_table_holds` and `test_each_invariant_flips_on_a_patched_copy`. These are
  `orch_invariants`: every phase reachable and exiting, answers only from asked phases and only by home, the automaton
  takes no words, the `head-moved` and `withdrawn` shapes, and the hold closure.
- `test_board.py` `MachineTests`: `test_derive_golden_for_every_phase`, `test_relay_lines_for_every_row_of_the_table`,
  `test_transition_is_pure_and_keeps_since_on_a_self_loop`, `test_head_moved_withdraws_the_question_and_the_evidence`,
  `test_withdrawn_steps_a_batch_sibling_back_to_done_ready` and `test_the_automaton_fires_only_its_own_events`.
- `test_board.py` `AdvanceTests`: `test_board_phases_prints_every_event`, plus the `test_replay_x4_*`, `test_replay_x9_*`,
  `test_replay_s4_*` and `test_replay_s7_*` cases.
- `test_automaton.py`:
  - X5: `test_verifying_with_every_pr_up_is_verified_once` and `test_a_failing_evidence_returns_the_row_to_its_unit`;
  - X6: `test_a_moved_head_withdraws_the_question_and_is_reverified` and
    `test_a_moved_head_withdraws_the_batch_question_from_its_other_rows`;
  - S11: `test_s11_a_question_asked_of_a_planned_row_is_never_flipped_away`.
- `test_hygiene.py`: `test_w11_phase_age`.

**The replays (`dyad/tests/test_replays.py`, one test per case).**
- `test_s1_a_pr_up_tells_every_co_owner_and_rings_them`
- `test_s2_waiting_on_is_derived_and_a_hand_write_is_refused`
- `test_s3_routing_reads_owners_not_the_seat_table`
- `test_s4_a_co_owners_pr_up_moves_the_wait_off_the_reporter`
- `test_s5_who_acts_next_is_named_and_an_unread_relay_is_swept`
- `test_s6_a_relay_names_its_doorbell_on_the_ring_list`
- `test_s7_record_board_and_relays_are_one_commit_or_none`
- `test_s8_the_relay_goes_to_an_owner_the_event_made`
- `test_s9_a_drafted_done_is_a_phase_the_queue_counts`, which also asserts that no W11 line appears at 13 h
- `test_s10_a_read_moves_no_phase`, which also asserts that there is no `read` event
- `test_s11_a_question_asked_of_a_planned_row_is_never_flipped_away`
- `test_s11_phased_a_revision_asked_through_the_machine_is_never_caught_up` (`expectedFailure`, the defect)
- `test_r2_573_combined_red`
- `test_r2_572_stale_head`

## 4. What is not caught

- **S11 on the phased path is a defect.** `automaton.catch_ups` proposes `answered-Y` for any phased `plan-ready` or
  `plan-asked` entry of a planned row whose last disposition is a `Y plan`. It never asks `board_after_plan_y`. Two
  more holes let a planned row reach `plan-asked` at all:
  - `(planning, plan-landed)` does not check the row's state; only the adoption does.
  - The table has no `amend` edge, which plan F5 named.

  Fix shapes, the engineer's to propose: apply `board_after_plan_y`, or the asked question's own commit, in
  `catch_ups`; refuse `plan-landed` and `asked` on a planned row; add the `amend` escape edge.
- **S10 is not built.** There is no `read` event, and a read is still a side effect of printing. Only its consequence
  is removed.
- **S9 has no timely timer.** At 13 h, `done-ready` and `verifying` are W11-silent; their threshold is 72 h.
- **S3 is partly covered.** The `_cos` seat table stays hand-written and unchecked.
- **The ring stays home's act (S6, X8).** The machine lists the ring; it does not ring.
- **The scope is phased entries only.** An entry without `phase` behaves as before #587. `board set` still writes its
  `waiting-on` and `next` freely, so S2, S4 and S8 recur on any entry home keeps unphased.
- **The replays run the automaton by hand.** Whether the automaton job fires promptly on a board, rows or inbox push
  (X10's trigger) is not replayed here. Neither is the real `check --evidence` inside X5; it is stubbed.
