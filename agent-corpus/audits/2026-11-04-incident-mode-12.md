# Incident mode 12 — an act (mutation, dispatch, ask) taken before the record that must precede it (plan file, plan-Y, board entry); no verb checks order

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 8 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
an act (mutation, dispatch, ask) taken before the record that must precede it (plan file, plan-Y, board entry); no verb checks order.

**What would have to change** (the derivation's one-sentence test): mutating/dispatching verbs refuse unless the preceding record exists on origin, at the act.

**Predecessor:** mode A of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-a.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 32 | 2026-09-16 | #35 | V1-18 |
| 41 | 2026-09-18 | #67 | V1-18 |
| 43 | 2026-09-20 | #92, #103, #104 | V1-18 |
| 45 | 2026-09-22 | #110 | V1-18 |
| 111 | 2026-10-07 | #233 | V1-18 |
| 136 | 2026-10-09 | #260 | V1-18 |
| 225 | 2026-10-20 | #348 | V1-18 |
| 246 | 2026-11-02 | #546 | V1-18 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| plan gate: a non-clerical range citing a row without `Y plan` fails | `dyad/guards/agent/prs.py:75` `check_transaction`, `:42` `check`, `:34` `has_plan_y` | push | 43, 45 (in principle) | 32 (same ledger commit), 41, 111, 136, 225, 246 | shipped 2026-09-14 (`52024e66`); entry-parsed 2026-10-28 (#250) | yes: 43 (09-20), 45 (09-22) after — why the gate did not fire is NOT verified (hooksPath unset, or the cited row already held a `Y plan`) |
| hooksPath set at session start | `bootstrap.py:184` `step_hooks` | session start | 43, 45 if the hook was unset | — | shipped 2026-10-26 | none after |
| relay refused unless the board entry is on origin/main, names the recipient, written by this session | `dyad/guards/agent/inbox.py:224` `write_ahead_problem` | `inbox post` call | 246 (relay half) | 246 (plan-file landing and session start without board entry) | shipped 2026-11-02 (`dcf8f1b5`, #552) | 246 same day, order unknown |
| board resume tells the new holder to `board set _cos holder=` before any act | `board.py:417` | hop | — | — | shipped (#535) | — |
| Rule-3 write-ahead; Rule-15 plan file before the counter-prompt | `RULE-3-d-work.md:344`; `RULE-15-d-work-phases.md` Phases 1 | conduct | — | 41, 136, 225 | shipped | yes |

No fence refuses a `Y done` added to a row whose `disposed` holds no `Y plan` (grep `PLAN_Y`: used only by `prs.py:40` and `automaton.py:141`).

Closure: (2) backlog #262 (mode A) and #277 (mode P). NEW fence: the row fence (`rows.check_commit`) fails an added `Y done` entry on a row whose prior entries hold no `Y plan` and which is not mandate-born, at push — reaches 111; owner engineer. Residue (3): asking before the plan file exists (41), dispatching forks before the `Y` (136) and a raw `git merge --ff-only` (225) are chat/shell acts no dyad mechanism reads (a harness hook could, as in V2-08).

## Status
Exit 2 — backlog row; fence row proposed: **R-d** (index, Proposals).
