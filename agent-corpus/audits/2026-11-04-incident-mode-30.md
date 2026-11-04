# Incident mode 30 — a conduct preference (concise, delegation, batch signal) loaded but read by no mechanism at reply time

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a conduct preference (concise, delegation, batch signal) loaded but read by no mechanism at reply time.

**What would have to change** (the derivation's one-sentence test): a turn-end check reads the reply against the preference, at reply.

**Predecessor:** mode Q of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-q.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 68 | 2026-09-29 | #188 | V1-43 |
| 69 | 2026-09-29 | #183 | V1-43 |
| 78 | 2026-09-29 | #195 | V1-43 |
| 79 | 2026-09-29 | #195 | V1-43 |
| 119 | 2026-10-09 | #254 | V1-43 |
| 151 | 2026-10-14 | #290 | V1-43 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| trace measures the `subagent` bucket | `dyad/scripts/trace.py:35`, `:48` | Done (post hoc) | 79, 119 (measured, not prevented) | 68, 69, 78, 151 | shipped (#213) | 119 (10-09) after |
| pending queue recorded in the board store | `dyad/guards/agent/board.py:54` `COS_FIELDS` (`queue`) | write-ahead (conduct) | 69, 151 (a place to record it) | — | shipped (#535, 2026-11-02) | none after |
| reply-time check | none (`.claude/settings.json` holds only a SessionStart hook) | — | — | all | — | — |

Closure: (2) NEW fence (engineer): a Claude Code `Stop` hook that reads the turn from the harness's transcript path and
warns when a turn emitted more than one text block under `concise-mode: on`, or when an Operator message followed an
unanswered `Y/N:` without the next reply printing queue counts under `batch-disposition-mode`; moment: turn end. It is
one kernel's adapter and only warns; on another kernel the mode is (3) (Rule-14 p2; Rule-10 Enforcement "inference
only"). Delegation (79, 119) stays measured at Done. Backlog #278 (mode Q).

## Status
Exit 3 — impossible on this kernel.

**Reclassified at reconciliation (index, decision 4):** the inventory above proposes a Claude Code hook in `.claude/settings.json`. Such a hook runs on one harness and not on the kernel-only path every guard must run on (Rule-14 property 3), so on the kernel this mode is exit 3: no kernel mechanism reads the Agent's shell before a command runs. The hook stays an Operator-side option, like the harness permission mode (Rule-8 Boundaries), named in the index for the Operator to weigh.
