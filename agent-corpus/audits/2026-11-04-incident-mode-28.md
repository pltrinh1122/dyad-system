# Incident mode 28 — a check passes or reports confidently over empty or absent input

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 3 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a check passes or reports confidently over empty or absent input.

**What would have to change** (the derivation's one-sentence test): an empty or absent input set fails or prints its absence, at check.

**Predecessor:** mode E of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-e.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 209 | 2026-10-24 | #393, #388 | V1-15 |
| 212 | 2026-10-24 | #401 | V1-28 |
| 234 | 2026-10-26 | #477 | V1-36 |

Secondary mechanism on rows: 234 (V2-33). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| evidence refuses a shallow or tagless clone | `dyad/scripts/bootstrap.py:155` `clone_problems`, `package.py:1294-1296` | evidence | 234 | 212, 209 | shipped (#474 2026-10-26, #505 2026-10-28) | none after |
| bootstrap fetches the row's tag at session start | `bootstrap.py:215` `step_tags`; `.claude/settings.json` SessionStart | session start | 234 (in cloud sessions) | — | shipped | none after |
| drift check on a missing tag | `bundle.py:131` prints `warning: skip` | push | — | 234 at the push path (still a skip) | shipped (skip by design, Rule-11 p4) | — |
| empty pre-push stdin | `package.py:1179-1180`: `pushed is None` prints "every ref is a deletion or already on origin/main" — empty stdin still lands here | push | — | 212 | **unfenced** | — |
| attendance mode over no live seat | `dyad/guards/agent/sessions.py:412-431` `attendance` — "the reading with no live seat" is M3; `attendance_line` prints the declared set beside the count | `session list` | 209 (partly: the declaration is now printed) | 209 (0 of 0 still reads as a mode) | shipped (#414) | — |

Closure: (2) NEW fence (engineer): `cmd_guards --pre-push` (a) prints a distinct line for an empty stdin instead of the
deletion message and (b) runs `bootstrap.clone_problems` as it does in evidence, so a tagless clone refuses at push
rather than skipping the drift check; `attendance_line` prints "no live seat" rather than a mode when `n_live == 0`.
Moment: push / `session list`.

## Status
Exit 2 — backlog row; fence row proposed: **R-a** (index, Proposals).
