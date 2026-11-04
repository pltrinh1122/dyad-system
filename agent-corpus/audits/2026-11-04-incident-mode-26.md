# Incident mode 26 — suite or scratch children reach the live repository through inherited git env, cwd or the package path

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
suite or scratch children reach the live repository through inherited git env, cwd or the package path.

**What would have to change** (the derivation's one-sentence test): every child runs in a scrubbed env against an explicit scratch path, at spawn.

**Predecessor:** mode W of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-w.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 57 | 2026-09-25 | #161 | V1-20 |
| 58 | 2026-09-25 | #152 | V1-20 |
| 123 | 2026-10-09 | #256 | V1-62 |
| 230 | 2026-10-13 | #259 | V1-20 |
| 233 | 2026-10-26 | #461 | V1-21 |
| 247 | 2026-11-02 | #536 | V1-21 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: yes: 57 after #152 PR-1; 230; 247 after suite_env.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| scrubbed child env (GIT_VARS dropped) | `dyad/scripts/package.py:724` `suite_env` | spawn | 57, 58 | 123, 230, 233, 247 | shipped (2026-09-25) | **yes**: 123 (10-09), 230 (10-13), 247 (11-02) after it |
| `GIT_CONFIG_PARAMETERS` dropped | `package.py:738` | spawn | 123, 230 | 233, 247 | shipped (#456, 2026-10-26) | none after |
| fixture git never auto-maintains | `package.py:720` `SUITE_GIT_CONFIG`; `dyad/scripts/livetest.py:52` | spawn | (236, V2-33) | — | shipped (#474/#475, 2026-10-27) | — |
| hook-exported GIT_DIR ignored for REPO | `package.py:267` | call | 57, 58 | — | shipped (#142) | — |
| checkout cleanliness snapshot around every root | `package.py:388` `checkout_snapshot`, `:413` `cleanliness_problem`, `:430/:441`, `:885` | push, evidence, targeted runs | 247 | 233 (not a suite run) | shipped (#552, 2026-11-02) | none after |
| new row ids contiguous from base max+1 | `dyad/guards/agent/rows.py:568` `contiguity_problems`, called at `:466-467` | push | 233 (the fabricated `999`) | scratch work that writes no row | shipped (#467, 2026-10-28) | none after |

Closure: (1) fenced at spawn (`suite_env`) and at suite end (`checkout_snapshot`, push and evidence); 233's residual
(an agent-run simulation losing its `cd`) is fenced only where it writes a row (contiguity at push) — otherwise (3):
no mechanism reads the Agent's shell cwd.

## Status
Exit 1 — fenced.
