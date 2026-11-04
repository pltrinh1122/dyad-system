# Incident mode 14 — a push to a PR branch already named by a pending or given Done-Y

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a push to a PR branch already named by a pending or given Done-Y.

**What would have to change** (the derivation's one-sentence test): pre-push refuses a push to a branch whose head a Y done or pending Done question names, at push.

**Predecessor:** mode A of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-a.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 198 | 2026-10-22 | #383 | V1-59 |
| 235 | 2026-10-26 | #476 | V1-59 |

Secondary mechanism on rows: 235 (V2-46). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| pre-push refuses moving a head an operative `Y done` names while unlanded | `package.py:1064` `done_head_refusals`, called `:1170` | push | 198, 235 | a push not through the hook (hosting UI, MCP `push_files`/`create_or_update_file`, a clone without hooksPath); a head named only by a *pending* Done question not yet recorded | shipped 2026-10-28 (`9d3e630e`, #495) | none after |
| `dyad merge` refuses a moved live head | `merge.py:96` | merge | 198, 235 (void detected at merge) | — | shipped 2026-10-31 | none after |

Closure: (1) fenced at push by `done_head_refusals`. Residue: a pending (asked, unrecorded) Done question names no head on any ref, so the interval between asking and recording is unfenced (conduct).

## Status
Exit 1 — fenced.
