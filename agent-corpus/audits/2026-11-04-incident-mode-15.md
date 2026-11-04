# Incident mode 15 — the Done record sets the row terminal before the merge, so a needed post-record push/merge has no path and the ledger claims merges that did not run

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
the Done record sets the row terminal before the merge, so a needed post-record push/merge has no path and the ledger claims merges that did not run.

**What would have to change** (the derivation's one-sentence test): the row's state follows the observed merge (state after landing), at close.

**Predecessor:** mode M of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-m.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 82 | 2026-09-30 | #196 | V1-24 |
| 84 | 2026-09-30 | #200 | V1-24 |
| 129 | 2026-10-09 | #256 | V1-24 |
| 149 | 2026-10-14 | #245, #290 | V1-24 |
| 169 | 2026-10-08 | #243 | V1-24 |
| 171 | 2026-10-15 | #239 | V1-24 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| one commit may not record a merge-naming `Y done` and set `done` | `rows.py:147` `done_order_problems` | push | 82, 84, 116-shape, 149, 169, 171 | — | shipped 2026-10-15 12:05 −0700 (`0a4060e3`, #202) | 171, 175 same day, order unknown; none after |
| `done` only when every head the operative entry names is on main | `rows.py:229` `landing_problems` | push | 149, 169, 171 | — | shipped 2026-10-15 | as above |
| verbs refuse `done` with a merge-naming entry, and `done` without a landed head | `package.py:2156`, `:1959` `landing_refusal` | call | all | — | shipped 10-15 / 10-25 | none after |
| recorded-not-closed interval warned in every evidence block | `rows.py:272` `done_recorded_not_closed` | evidence | 171 (an unexecuted Done becomes visible) | — | shipped 2026-10-15 | none after |
| a row stays open/planned until the merge lands, so a post-merge step can still cite it | Rule-3 Completion (`RULE-3-d-work.md:259`) | design | 129 | — | shipped 2026-10-15 | none after |
| `steps close-landed` sets done only when every head is on origin/main | `steps.py` (`close-landed`) | call | all | — | shipped 2026-11-02 | none after |

Closure: (1) fenced — at push by `rows.done_order_problems` + `rows.landing_problems`, at the call by the `dwork state` refusals, visible in evidence by `done_recorded_not_closed`.

## Status
Exit 1 — fenced.
