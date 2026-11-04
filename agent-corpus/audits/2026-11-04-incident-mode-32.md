# Incident mode 32 — unnamed local branches deleted as cleanup under momentum

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 4 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
unnamed local branches deleted as cleanup under momentum.

**What would have to change** (the derivation's one-sentence test): branch deletion only through a verb that refuses a branch no plan names, at deletion.

**Predecessor:** mode P of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-p.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 67 | 2026-09-25 | #167 | V1-19 |
| 77 | 2026-09-29 | #133, #191 | V1-19 |
| 80 | 2026-09-29 | #194 | V1-19 |
| 85 | 2026-09-30 | #199 | V1-19 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no (rule recorded only).

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| tool-owned worktrees (`land`, `merge`) leave no ledger branches to clean | `land.py` `<git common dir>/dyad-land`; `merge.py` | call | 77, 80, 85 shape (ledger branches no longer made) | 67 | shipped (#447, 2026-10-25) | none after |
| any branch-deletion check | none in `dyad/scripts` (no `branch -d/-D`) | — | — | all | — | — |

Closure: (2) backlog #277 (mode P); NEW fence: the `PreToolUse` Bash hook refuses `git branch -d|-D <b>` unless `<b>`
is named in an open or planned plan file (engineer; moment: tool call). Branch deletion is a local git act no core
guard sees, so without the hook it is (3).

## Status
Exit 3 — impossible on this kernel.

**Reclassified at reconciliation (index, decision 4):** the inventory above proposes a Claude Code hook in `.claude/settings.json`. Such a hook runs on one harness and not on the kernel-only path every guard must run on (Rule-14 property 3), so on the kernel this mode is exit 3: no kernel mechanism reads the Agent's shell before a command runs. The hook stays an Operator-side option, like the harness permission mode (Rule-8 Boundaries), named in the index for the Operator to weigh.
