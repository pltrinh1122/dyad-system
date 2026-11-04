# Incident mode 25 — a working hook bypassed (--no-verify, hooksPath=/dev/null)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a working hook bypassed (--no-verify, hooksPath=/dev/null).

**What would have to change** (the derivation's one-sentence test): a bypass is refused or recorded mechanically at commit/push.

**Predecessor:** mode V of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-v.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 47 | 2026-09-22 | #116–#125 | V1-51 |
| 176 | 2026-10-15 | #297 | V1-51 |

Secondary mechanism on rows: 47 (V2-28). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| pre-push re-judges every pushed commit's zone (commits mode) | `package.py` `cmd_guards --pre-push` → `containment.py` per commit (Rule-1 Conditions) | push | 47 (effect re-checked) | 176 (a scratch-worktree commit never pushed) | shipped | — |
| CI corroborates on `main` | `.github/workflows/dyad-package.yml` (on push to main) | CI | anything that lands | unpushed bypasses | shipped | — |
| bootstrap restores `core.hooksPath` | `dyad/scripts/bootstrap.py:184` `step_hooks`; `.claude/settings.json` SessionStart | session start | a cleared hooksPath in config | `-c core.hooksPath=` per command, `--no-verify` | shipped (#474, 2026-10-26) | none after |
| record of a skipped hook | none: git keeps no trace of a skipped hook | — | — | 47, 176 | — | — |

Closure: (2) backlog #283 (mode V) holds it; NEW fence: the `PreToolUse` Bash hook refuses `--no-verify` and
`core.hooksPath=` overrides unless the command also runs `containment.py staged` (Rule-1's hook-cannot-execute path)
(engineer; moment: tool call). The bypass itself is (3) on the kernel-only path: git records no skipped hook; its
effects are fenced at push and on `main`.

## Status
Exit 3 — impossible on this kernel.

**Reclassified at reconciliation (index, decision 4):** the inventory above proposes a Claude Code hook in `.claude/settings.json`. Such a hook runs on one harness and not on the kernel-only path every guard must run on (Rule-14 property 3), so on the kernel this mode is exit 3: no kernel mechanism reads the Agent's shell before a command runs. The hook stays an Operator-side option, like the harness permission mode (Rule-8 Boundaries), named in the index for the Operator to weigh.
