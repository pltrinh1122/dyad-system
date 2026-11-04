# Incident mode 01 — test asserts a literal snapshot of the authoring tree or live repo (crafts, counts, instance values, tags) that a legitimate change falsifies

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 7 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
test asserts a literal snapshot of the authoring tree or live repo (crafts, counts, instance values, tags) that a legitimate change falsifies.

**What would have to change** (the derivation's one-sentence test): tests derive expected values from what the run's own tree discovers (scratch or live), at test-write time.

**Predecessor:** mode H of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-h.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 1 | 2026-09-24 | #156 | V1-01 |
| 9 | 2026-09-22 | #114 | V1-01 |
| 12 | 2026-09-15 | #1 | V1-38 |
| 51 | 2026-09-23 | #137 | V1-01 |
| 59 | 2026-09-25 | #175 | V1-01 |
| 83 | 2026-09-30 | #186 | V1-01 |
| 242 | 2026-10-29 | #526 | V1-01 |

Secondary mechanism on rows: 12 (V2-33), 242 (V2-47). Recurrence after a mitigation the cells describe: yes: 59, 83, 242 after row 1's discovery-derived fix.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| the suite runs on every non-clerical push | `dyad/scripts/package.py:420` `check_rule_12`; Rule-12 p2 (`RULE-12-verifiable-code.md:43`) | push (`check --guards --pre-push`) | 1, 9, 51, 59 (detected: the breaking change is refused at its own push) | 12, 242 (red on `main` after a tag/release, not after a push of the change); 83 (only the scratch install fails) | shipped (pre-09-14) | yes: every row is a detection, never a prevention |
| CI scratch install runs the suite in a scratch repo | `.github/workflows/dyad-package.yml:24` step `corroborate` (`check --corroborate`) | CI after merge | 83, 9 | 1, 51, 59, 242 | shipped | yes (83 after) |
| one-off fix: projector tests derive from discovery | commit `5c7818c7` (2026-09-24, #156 PR-0) | test-write time, those tests only | 1 | 9, 12, 51, 59, 83, 242 | shipped (local) | yes: 59, 83, 242 after 09-24 |
| suite-cleanliness fence (a test changes nothing in the live checkout) | `package.py:413` `cleanliness_problem`, `:388` `checkout_snapshot` | every suite run | none of this mode (it fences writes, not reads, of the live repo) | all | shipped 2026-11-02 (`dcf8f1b5`, #552) | n/a |

No Rule or guard text requires a test to derive its expected value from the tree it runs in; `crafts/syseng/rules/verifiable-code.md` and `crafts/syseng/guards/tests.py` hold no such clause (grep for snapshot/literal/live repo: nothing).

Closure: (2) backlog — existing #269 (mode H, "the present enumeration pinned as an invariant") and #270 ("verified in one environment, run in another") cover it in prose; NEW fence: `syseng/tests` warns on a test module that reads the live repository (`dyadlib.repo_root()`, `REPO`, `origin/main`, live tags) outside a scratch fixture, at push (`check --guards`); owner engineer.

## Status
Exit 2 — backlog row; fence row proposed: **R-g** (index, Proposals).
