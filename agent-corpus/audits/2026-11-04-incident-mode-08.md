# Incident mode 08 — a raw path-scoped git checkout/reset used over live uncommitted or hand-resolved state

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 5 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a raw path-scoped git checkout/reset used over live uncommitted or hand-resolved state.

**What would have to change** (the derivation's one-sentence test): reads use git show and syncs use a verb that refuses over a dirty or unmerged tree, at the git call.

**Predecessor:** mode O of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-o.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 5 | 2026-09-23 | #127 | V1-06 |
| 10 | 2026-09-22 | #114 | V1-06 |
| 44 | 2026-09-22 | #110 | V1-06 |
| 62 | 2026-09-25 | #166 | V1-06 |
| 190 | 2026-10-17 | #331 | V1-06 |

Secondary mechanism on rows: 44 (V2-07). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| ledger writes in a tool-owned worktree; the seat's checkout never reset | `land.py:157` `prepare`, module doc | call (`--land`) | 10, 190 (ledger sync) | 5, 44, 62 (reads and conflict resolution by raw git) | shipped 2026-10-25 (`abf9db93`) | none after |
| only byte-identical landed copies restored; the rest named | `land.py:285` `restore_landed_paths`, `:316` `fast_forward` | call | 190 shape | — | shipped 2026-10-29 (`ddaa05e2`, #466) | none after |
| push refused over a dirty working tree | `package.py:1057-1061` in `pushed_refs` | push | none (fires after the loss) | all | shipped | — |
| same-root warning | `sessions.py:552` `same_root` | session start | — | all | shipped 2026-09-16 (#32 F4) | yes: 44, 62, 10, 5, 190 after |

No mechanism at HEAD reads the Agent's shell command before it runs; `.claude/settings.json` holds only an allow rule for `dyad merge` and the SessionStart hook.

Closure: (2) backlog #276 (mode O, "a git write used as a read"). NEW fence: a PreToolUse hook in `.claude/settings.json` refusing `git checkout <ref> -- <path>`, `git reset --hard|--soft` and `git checkout -- .` when `git status --porcelain` is non-empty or an unmerged path exists, at the Bash call; owner engineer (an Operator-side harness fence, Rule-1 and Rule-8 Boundaries — the Operator commits it).

## Status
Exit 3 — impossible on this kernel.

**Reclassified at reconciliation (index, decision 4):** the inventory above proposes a Claude Code hook in `.claude/settings.json`. Such a hook runs on one harness and not on the kernel-only path every guard must run on (Rule-14 property 3), so on the kernel this mode is exit 3: no kernel mechanism reads the Agent's shell before a command runs. The hook stays an Operator-side option, like the harness permission mode (Rule-8 Boundaries), named in the index for the Operator to weigh.
