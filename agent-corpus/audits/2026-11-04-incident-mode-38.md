# Incident mode 38 — delegated or targeted verification ran a subset of what the push gate runs

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
delegated or targeted verification ran a subset of what the push gate runs.

**What would have to change** (the derivation's one-sentence test): drafter verification is the full gate command, before push.

**Predecessor:** mode E of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-e.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 95 | 2026-10-06 | #227 | V1-58 |
| 222 | 2026-10-25 | #447 | V1-58 |

Secondary mechanism on rows: 95 (V2-01). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| the push gate runs every root | `dyad/hooks/pre-push` → `package.py check --guards --pre-push` (`cmd_guards`, `package.py:1151`); Rule-12 property 2 | push | 95, 222 (both caught there, nothing landed) | — | shipped | n/a — the gate is what caught both |
| levels-seed obligation readable by a guard, not only the full suite | `crafts/syseng/guards/tests.py:9-11,30,59` `LEVELS_SEED` (#484, 2026-10-29) | `check --guards`, push, evidence | 222 | 95 (a released craft's own test pin) | shipped | no (222 is 10-25) |
| sub-agent briefed to run the full gate | none | — | — | 95, 222 | — | — |

Closure: (1) fenced — the pre-push gate (`dyad/hooks/pre-push`, push) refuses every instance before it leaves the
machine; the mode's cost is one refused push, and #484 moves row 222's obligation into `check --guards`.

## Status
Exit 1 — fenced.
