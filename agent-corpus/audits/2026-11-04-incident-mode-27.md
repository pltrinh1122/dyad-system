# Incident mode 27 — a checker judges a proxy of its object (checked-out branch, the entrypoint's own tree, on-disk dirs, one merge base, index vs working tree)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 5 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a checker judges a proxy of its object (checked-out branch, the entrypoint's own tree, on-disk dirs, one merge base, index vs working tree).

**What would have to change** (the derivation's one-sentence test): the checker resolves its object only from its explicit range/tree argument, at check.

**Predecessor:** mode D of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-d.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 19 | 2026-09-15 | #17 | V1-57 |
| 139 | 2026-10-10 | #261 | V1-21 |
| 146 | 2026-10-12 | #261 | V1-21 |
| 214 | 2026-10-25 | #412, #413, #414 | V1-15 |
| 241 | 2026-10-29 | #526 | V1-61 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| pre-push refuses a dirty working tree and a ref other than HEAD | `package.py:1030` `pushed_refs` (dirty at `:1057-1060`) | push | 19 (an unstaged file cannot be pushed past) | others | shipped (#194, 2026-09-30) | none |
| evidence prints `dirty=` | `package.py` `cmd_evidence` | evidence | 19 | — | shipped | — |
| a craft is a directory holding a tracked file | `dyad/guards/craft/crafts.py:435` `crafts` (`carried_crafts`) | push | 214 | — | shipped (#483, 2026-10-28) | none after |
| range mode uses the net merge diff on several merge bases | `dyad/guards/infra/containment.py:178` `merge_bases`, `:180-192` `range_diff` | `check --pr`, CI | 241 | — | shipped (2026-10-29) | none after |
| rows fence dispatch | `dyad/guards/agent/rows.py:462` — still `if branch(root) != "main"`: the checked-out branch, not the range | `check --pr` | — | 139 | **unfenced** | — |
| runner root | `package.py:267` `REPO` from the entrypoint's own tree (`PKG`); no comparison with the caller's cwd | evidence | — | 146 | **unfenced** | — |

Closure: (2) NEW fences (engineer): (a) `rows.check_transaction` takes the mode from `cmd_pr` (head is a PR head, not
`main`) instead of `branch(root)` (moment: `check --pr`); (b) `cmd_evidence` refuses when the caller's
`git rev-parse --show-toplevel` differs from `REPO` (moment: evidence). Rows 19, 214, 241 are fenced. Backlog #265 (mode D).

## Status
Exit 2 — backlog row; fence row proposed: **R-d** (index, Proposals).
