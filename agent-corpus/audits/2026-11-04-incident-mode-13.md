# Incident mode 13 — a merge executed before the Done-Y is recorded on origin

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 5 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a merge executed before the Done-Y is recorded on origin.

**What would have to change** (the derivation's one-sentence test): merges run only through a verb that refuses unless origin holds Y done naming that PR at that head, at merge.

**Predecessor:** mode A of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-a.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 34 | 2026-09-16 | #47 | V1-17 |
| 38 | 2026-09-16 | #47 | V1-17 |
| 39 | 2026-09-18 | #58 | V1-17 |
| 40 | 2026-09-18 | #67 | V1-17 |
| 134 | 2026-10-05 | #223 | V1-17 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: yes: 39, 40 after the memory note of #47.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `dyad merge` refuses unless origin/main's operative `Y done` names PR at head, head is live, not yet on main | `merge.py:60` `authorizing`, `:81` `live_head`, `:96` | merge | 34, 38, 39, 40, 134 (when the verb is used) | a raw `gh pr merge` or MCP merge | shipped 2026-10-31 (`846df15c`, #532) | none after |
| harness allow rule for the verb | `.claude/settings.json` `permissions.allow` (`dyad/bin/dyad merge:*`) | Bash call | — | raw merges (no deny rule) | shipped (#532) | — |
| merge guard warns on a first-parent merge whose 2nd parent no operative `Y done` names | `dyad/guards/agent/merges.py:113` `authority_problem`, `:162` `judge` | push (transaction) / package check / evidence / CI | all, after the fact (warning only) | — | shipped 2026-10-31 (`62c8bfbd`, #541) | none after |
| memory note after #47 | per-machine cache | conduct | — | 39, 40 | shipped 09-16 | yes: 39, 40 (09-18), 134 (10-05) |

Closure: (2) backlog — NEW fence: a `deny` rule in `.claude/settings.json` for `gh pr merge`, `gh api …/merge` and the GitHub MCP `merge_pull_request` tools, leaving `dyad merge` the only allowed merge path, at the tool call; owner counsel (an Operator-side harness fence, Rule-1 Boundaries; the Operator commits it). Hosting branch protection is the World-side alternative (d-work #24). Until then prevention is conduct plus the verb, detection a warning.

## Status
Exit 1 — fenced.

**Reclassified at reconciliation (index, decision 4):** the harness deny rule named above is an Operator-side option, not a kernel fence. On the kernel this mode is exit 1: `dyad merge` refuses a merge its `Y done` does not name (Rule-2 Enforcement, #532), and `merges.py` warns at push on a merge commit no operative `Y done` names (#541).
