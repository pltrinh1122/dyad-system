# Incident mode 22 — an ad hoc shell script continues after a failed step (set -e inside &&, unquoted heredoc)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 3 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
an ad hoc shell script continues after a failed step (set -e inside &&, unquoted heredoc).

**What would have to change** (the derivation's one-sentence test): scripts run with fail-stop semantics per step (pipefail, quoted heredocs, checked restores), at script write.

**Predecessor:** mode E of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-e.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 49 | 2026-09-22 | #116–#125 | V1-27 |
| 157 | 2026-10-14 | #295 | V1-27 |
| 243 | 2026-10-27 | #492 | V1-27 |

Secondary mechanism on rows: 157 (V2-08), 243 (V2-21). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `set -euo pipefail` required in ops scripts | `crafts/sysadmin/guards/ops_scripts.py:33` `STRICT` | push | none (Operator ops scripts only) | 49, 157, 243 | shipped | — |
| ledger writes moved into one verb (no hand sequence) | `dyad/scripts/land.py` `dwork … --land`, `dwork batch` | call | 157's shape (sync + record + new row by hand) | 49, 243 | shipped (#447, 2026-10-25; batch #459) | 243 (2026-10-27) after — a plan file still written by heredoc |
| plan `Y/N` question restored by provenance/plan guards | none read a plan's question line | — | — | 243 | — | — |

Closure: (2) NEW fence: a Claude Code `PreToolUse` hook on Bash in `.claude/settings.json` (engineer; infra zone)
that refuses an unquoted heredoc whose body holds a backtick or `$(` when it writes under a tracked path; moment: the
tool call. It is one kernel's adapter (Rule-14 p3: runners are library), so the residual for other kernels is (3).

## Status
Exit 3 — impossible on this kernel.

**Reclassified at reconciliation (index, decision 4):** the inventory above proposes a Claude Code hook in `.claude/settings.json`. Such a hook runs on one harness and not on the kernel-only path every guard must run on (Rule-14 property 3), so on the kernel this mode is exit 3: no kernel mechanism reads the Agent's shell before a command runs. The hook stays an Operator-side option, like the harness permission mode (Rule-8 Boundaries), named in the index for the Operator to weigh.
