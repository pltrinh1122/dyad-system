# Incident mode 23 — a -f process match whose pattern appears in the matching command's own line

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a -f process match whose pattern appears in the matching command's own line.

**What would have to change** (the derivation's one-sentence test): match by pid or by a pattern absent from the command line, at the process match.

**Predecessor:** mode N of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-n.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 54 | 2026-09-24 | #155 | V1-23 |
| 56 | 2026-09-25 | #161 | V1-23 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| none in code or Rule text | — | conduct | — | 54, 56 | — | — |

Closure: (2) NEW fence: the same `PreToolUse` Bash hook refuses `pkill -f`/`pgrep -f` whose pattern is not
self-excluding (no `[x]yz` bracket form) (engineer; moment: tool call). Without the hook, (3): nothing reads the Agent's shell.

## Status
Exit 3 — impossible on this kernel.

**Reclassified at reconciliation (index, decision 4):** the inventory above proposes a Claude Code hook in `.claude/settings.json`. Such a hook runs on one harness and not on the kernel-only path every guard must run on (Rule-14 property 3), so on the kernel this mode is exit 3: no kernel mechanism reads the Agent's shell before a command runs. The hook stays an Operator-side option, like the harness permission mode (Rule-8 Boundaries), named in the index for the Operator to weigh.
