# Incident mode 06 — a claim about a mechanism accepted on a proxy (name, docstring, advertised field, one grep, wrong tree/function/base, correlation) without positive observation

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 20 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a claim about a mechanism accepted on a proxy (name, docstring, advertised field, one grep, wrong tree/function/base, correlation) without positive observation.

**What would have to change** (the derivation's one-sentence test): a claim is scored only on a run or full read of the mechanism itself with a positive control, at falsification.

**Predecessor:** mode D of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-d.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 27 | 2026-09-16 | #6 | V1-33 |
| 72 | 2026-09-29 | #192 | V1-30 |
| 81 | 2026-09-30 | #185 | V1-33 |
| 100 | 2026-10-05 | #221 | V1-33 |
| 101 | 2026-10-05 | #221 | V1-30 |
| 102 | 2026-10-05 | #221 | V1-33 |
| 104 | 2026-10-05 | #221 | V1-33 |
| 105 | 2026-10-05 | #222 | V1-33 |
| 117 | 2026-10-08 | #241 | V1-30 |
| 118 | 2026-10-08 | #253 | V1-30 |
| 125 | 2026-10-09 | #256 | V1-33 |
| 135 | 2026-10-08 | #226 | V1-30 |
| 141 | 2026-10-10 | #259 | V1-33 |
| 156 | 2026-10-14 | #290 | V1-30 |
| 158 | 2026-10-15 | #252 | V1-30 |
| 161 | 2026-10-15 | #241 | V1-30 |
| 165 | 2026-10-14 | #297 | V1-30 |
| 191 | 2026-10-21 | #363 | V1-30 |
| 195 | 2026-10-21 | #369 | V1-29 |
| 200 | 2026-10-22 | #378 | V1-30 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| easy-agreement trigger: one attack pushed to confirmed/refuted | `RULE-9-falsification.md:17` | conduct (falsification) | — | all 20 | shipped 2026-09-12 | yes: all 20 rows after |
| record guard checks only the table shape and Disposition line | `dyad/guards/agent/records.py` header (`REQUIRED`), "whether … a result right … stays inference" | push / package check | none | all 20 | shipped | n/a |
| plan base drift resolved mechanically | `dyad/guards/agent/references.py:416` `plan.base->commit` | push | 81 (wrong base) partly | the rest | shipped (cited by row 22, 09-16) | 81 after |

Closure: (2) backlog — existing #265 (mode D, wrong object read) and #266 (mode E, instrument narrower than the question); NEW fence: `records.py` warns on an attack row whose result is `confirmed` or `refuted` and whose cell cites no observation (a backticked command, a `path:line`, a sha or a run id), at push; owner counsel (form) then engineer. Residual (3): whether the cited observation is the mechanism itself (row 81's wrong clone, 104's wrong row) is inference (Rule-9 Enforcement).

## Status
Exit 2 — backlog row; fence row proposed: **R-g** (index, Proposals).
