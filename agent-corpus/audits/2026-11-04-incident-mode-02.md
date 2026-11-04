# Incident mode 02 — cross-zone coupled state (VERSION, BUNDLE.md rows, tags, craft-zone naming table) whose guards admit no one-zone PR order

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 9 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
cross-zone coupled state (VERSION, BUNDLE.md rows, tags, craft-zone naming table) whose guards admit no one-zone PR order.

**What would have to change** (the derivation's one-sentence test): the coupled guards admit every one-zone intermediate state of a legitimate change, checked when a guard or coupling is added.

**Predecessor:** mode M of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-m.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 2 | 2026-09-24 | #156 | V1-02 |
| 60 | 2026-09-25 | #166 | V1-02 |
| 61 | 2026-09-25 | #166 | V1-02 |
| 115 | 2026-10-07 | #241 | V1-02 |
| 188 | 2026-10-15 | #326 | V1-02 |
| 215 | 2026-10-25 | #417, #418, #420 | V1-02 |
| 216 | 2026-10-25 | #433 | V1-02 |
| 240 | 2026-10-29 | #526 | V1-02 |
| 244 | 2026-10-27 | #493 | V1-02 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: yes: 60, 61 after #156; 115, 216, 244 after #230; 215, 240 after both.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| unreleased craft without a bundle row warns | `dyad/guards/infra/bundle.py:204` in `check` | push / evidence / CI | 2 | all others | shipped 2026-09-24 (`5c7818c7`, #156) | yes: 60, 61 (09-25) are other couplings, not this clause |
| row behind an untagged bump of a released craft warns | `bundle.py:191` | push / evidence | 115, 216 (shape) | 244 (row named a never-tagged number) | shipped 2026-10-07 (`8f79b93d`, #170/#230) | yes: 216 (10-25), 244 (10-27) after |
| row naming a never-released number behind an untagged bump warns | `bundle.py:193` | push / evidence | 244, 216 | — | shipped 2026-10-29 (`ff669800`, #481) | none after |
| departed released craft keeps its row with a warning | `bundle.py:184` | push / evidence | 215 | — | shipped 2026-10-25 (`ba4c1fd1`, #423) | 215 same day, order unknown |
| evidence does not refuse a head proposing the core release it cuts | `dyad/scripts/bootstrap.py:144` `proposed_core_release`, used in `:155` `clone_problems` | `check --evidence` | 240 | — | shipped 2026-10-29 (`3895ca6c`, #526) | none after |
| Tended-craft contribution to a core table (data leaves with the craft) | Rule-11 p2 (craft-shipped contribution) | design | — | 60, 61 (guard registry/craft scan coupling), 188 (syseng naming guard refuses an env var name) | shipped (Rule-11 p2, #100) | yes: 60, 61, 188 after |

Closure: (2) backlog #274 (mode M, "no legal order, no verb"). The BUNDLE/VERSION/tag sub-case is fenced at push (rows 2, 115, 215, 216, 240, 244 reached by shipped clauses, none after #481/#526); the general coupling (60, 61, 188) has no fence. NEW fence: a sysarch-craft rule plus test that every guard pair coupling two zones ships a test walking each one-zone intermediate state of an add/rename/bump (the pattern of `bundle.check`'s warn clauses), checked at push by `syseng/tests`; owner counsel (rule) then engineer (test).

## Status
Exit 2 — backlog row; fence row proposed: **R-h** (index, Proposals).
