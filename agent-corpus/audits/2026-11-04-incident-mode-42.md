# Incident mode 42 — the close path's landing test rebinds refs and writes it into the row

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 4 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
the close path's landing test rebinds refs and writes it into the row.

**What would have to change** (the derivation's one-sentence test): rename the variable (no shadowing) in cmd_dwork close.

**Predecessor:** mode J of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-j.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 218 | 2026-10-25 | #433 | V1-32 |
| 219 | 2026-10-25 | #417, #427, #431 | V1-32 |
| 220 | 2026-10-25 | #412, #422, #423, #424 | V1-32 |
| 221 | 2026-10-25 | #202, #259, #308, #326, #330, #331, #333, #334, #335, #337, #338, #340, #341, #342, #343, #353, #361, #369, #385, #388, #395 | V1-32 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| landing test extracted, no shadowing | `package.py:1959-1975` `landing_refusal` (own `branches` local), called `:2167` (#439, 2026-10-25) | call | 218-221 | — | shipped | no (all four 10-25, same day) |
| refs-shape fence | `dyad/guards/agent/rows.py:291-330` `refs_shape_problems` (transaction, `:428,:442,:512`) and state `rows.py:118` in `check_package` (#439) | commit/push, evidence | 218-221 | — | shipped | no |

Closure: (1) fenced — `rows.refs_shape_problems` at push (and `check_package` at every guard run); the general
call-graph mode is V2-37's #271.

## Status
Exit 1 — fenced.
