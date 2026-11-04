# Incident mode 47 — a hosted CI result produced and never read back, or its absence never compared

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a hosted CI result produced and never read back, or its absence never compared.

**What would have to change** (the derivation's one-sentence test): a step compares main's pushes with completed green corroborations.

**Predecessor:** mode Q of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-q.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 251 | 2026-11-02 | #560 | V1-60 |
| 252 | 2026-11-03 | #562, #558 | V1-60 |

Secondary mechanism on rows: 252 (V2-33). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| one CI run per landed tree | `.github/workflows/dyad-package.yml:14` `concurrency: { group: main, cancel-in-progress: true }` (#564, 2026-11-03) | CI after merge | 251 | 252 | shipped | no |
| automaton corroborates its own cuts | `dyad/scripts/automaton.py:349-375` `corroborate` (#564 E1) | automaton, after a cut lands | 252 | — | shipped | no |
| sweep compares code pushes with green corroborations | `automaton.py:164-165,223-252` `sweep_ci` | scheduled sweep (24 h window) | 251, 252 | — | shipped | no (rows 11-02, 11-03; fix 11-03) |

Closure: (1) fenced — `automaton.sweep_ci` twice daily and `automaton.corroborate` at each landed cut.

## Status
Exit 1 — fenced.
