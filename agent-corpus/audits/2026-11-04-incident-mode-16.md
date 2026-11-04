# Incident mode 16 — PRs held for a Done-Y on a shared tail-append file conflict with concurrent appends

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 7 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
PRs held for a Done-Y on a shared tail-append file conflict with concurrent appends.

**What would have to change** (the derivation's one-sentence test): tail-append records leave the PR (per-row files, or landed separately before the hold), at PR cut.

**Predecessor:** mode X of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-x.md` / `2026-10-24-incident-mode-x.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 116 | 2026-10-08 | #242 | V1-24 |
| 150 | 2026-10-14 | #259, #290 | V1-25 |
| 173 | 2026-10-15 | #310 | V1-25 |
| 174 | 2026-10-15 | #322 | V1-24 |
| 175 | 2026-10-15 | #297 | V1-24 |
| 183 | 2026-10-15 | #321 | V1-24 |
| 194 | 2026-10-21 | #338 | V1-25 |

Secondary mechanism on rows: 116 (V2-15), 173 (V2-15), 174 (V2-15), 175 (V2-15), 183 (V2-15), 194 (V2-15). Recurrence after a mitigation the cells describe: yes: 173, 174, 183, 194 after the #290 cut-narrow-land-first protocol.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| protocol: a PR touching a tail-append file is cut narrow and landed first | `preferences-corpus/PREFERENCES.md:42` (`merge-disposition`); `dyad/playbooks/disposition-digest.md:173` | conduct (PR cut) | — | 173, 174, 175, 183, 194 | shipped 2026-10-14 (`c42e633d`, #290) | yes: 173, 174, 175, 183 (10-15), 194 (10-21) |
| three-act Done order makes the conflict recoverable (row stays pushable) | `rows.py:147`, `:229` | push | 116, 150, 173-175 (recovery path exists) | the conflict itself | shipped 2026-10-15 | — |
| `steps verify-prs` merges each head in order onto origin/main with `git merge-tree` | `dyad/scripts/steps.py:101` `verify_prs`, `:122-124` | call, read-only (run before the Done question if the seat runs it) | conflicts visible before asking | not required by anything | shipped 2026-11-02 (`5ea1ff90`) | none after |
| `dyad merge` refuses a conflicting merge, nothing pushed | `merge.py:110` | merge | all (clean refusal) | — | shipped 2026-10-31 | none after |

`agent-corpus/audits/INCIDENTS.md` is still one tail-append table; no `.gitattributes` exists on origin/main (no union merge driver).

Closure: (2) backlog — NEW fence: `check --evidence` warns, in the brief form the Done question cites, when the evidenced range touches a path listed as tail-append (data beside the runner; `INCIDENTS.md` first), so a held PR carrying one is visible at Done time; or structurally, the incident log moves to one file per row like the d-work store (Rule-16 pattern). Owner engineer (evidence warning), counsel (store change: Rule-3 Incidents names `INCIDENTS.md`).

## Status
Exit 2 — backlog row; fence row proposed: **R-f** (index, Proposals).
