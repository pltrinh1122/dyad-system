# Incident mode 31 — a plan question not checked against stored constraints (refs dependencies, charter ceiling)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a plan question not checked against stored constraints (refs dependencies, charter ceiling).

**What would have to change** (the derivation's one-sentence test): the plan-ask verb reads the plan against refs and charter rows, at the plan question.

**Predecessor:** mode Q of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-q.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 73 | 2026-09-29 | #185 | V1-56 |
| 210 | 2026-10-24 | #400, #385, #388, #395 | V1-44 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `--mandate` refuses a mandate row lacking its disposition | `package.py:1940-1946` | call | none (refs/ceiling unread) | 73, 210 | shipped | — |
| MANDATES `ceiling` column parsed | `crafts/cabinet/guards/seats.py:37` `MANDATE_COLUMNS` | push (shape only) | none | 210 | shipped (shape only) | — |

Closure: (2) NEW fence (engineer, with counsel for one Rule-3 sentence): `dwork state <id> planned` warns when a row the
plan names as a dependency is open in `refs` of the row, and refuses an `accreted` row (`--mandate`) past the
seat's `MANDATES.md` ceiling; moment: the plan-`Y` record (call).

## Status
Exit 2 — backlog row; fence row proposed: **R-c** (index, Proposals).
