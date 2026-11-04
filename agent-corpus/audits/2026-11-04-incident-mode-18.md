# Incident mode 18 — a plan's files/zones/version/old-behaviour-tests list written from the deliverables instead of derived from the mutation

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 8 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a plan's files/zones/version/old-behaviour-tests list written from the deliverables instead of derived from the mutation.

**What would have to change** (the derivation's one-sentence test): the list is generated (diff, zone table, drift check, test grep) before the plan-Y.

**Predecessor:** mode K of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-k.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 6 | 2026-09-23 | #126 | V1-03 |
| 11 | 2026-09-22 | #114 | V1-56 |
| 18 | 2026-09-15 | #17 | V1-29 |
| 23 | 2026-09-16 | #22 | V1-29 |
| 103 | 2026-10-05 | #221 | V1-56 |
| 107 | 2026-10-07 | #228 | V1-31 |
| 108 | 2026-10-07 | #228 | V1-31 |
| 223 | 2026-10-25 | #350 | V1-03 |

Secondary mechanism on rows: 108 (V2-01). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| drift guard: `dyad/` differs from its tag under unchanged VERSION | `dyad/guards/infra/bundle.py:122` `check_drift` (#91, 2026-09-18) | push, evidence, CI | 6 (caught on `main`), 223 (caught at push) | 11, 18, 23, 103, 107, 108 | shipped | 223 (2026-10-25) after it — the guard caught it; the plan still omitted the bump |
| zone guard per commit | `dyad/hooks/pre-commit:4` → `dyad/guards/infra/containment.py` `staged` | commit | 18(b), 23 (a two-zone commit cannot be made) | 6, 11, 103, 107, 108, 223 | shipped | — |
| suite on the pre-push path (old-behaviour test fails) | `dyad/hooks/pre-push:5` → `package.py check --guards --pre-push` (Rule-12 p2) | push | 108 | the rest | shipped (#155, 2026-09-24) | 108 (2026-10-07) caught by it |
| execution detail reported as a departure line | Rule-3 Plan, "execution detail" bullet (#555) | Done (completion evidence) | 107 (an unlisted same-zone file is reportable, not a re-plan) | all others | shipped (rule text) | — |
| per-PR files and zones listed before Done | `dyad/scripts/steps.py:101` `verify_prs` (#556, 2026-11-02) | Done-time, read-only | none at plan time | all | shipped | none after |
| plan-file guard | `dyad/guards/agent/plans.py:45` `check_plan` | push | none (checks title/base/intent only) | all | shipped | — |

Closure: (2) backlog — #272 (mode K) is the inventory row; NEW fence: `dyad plan check <id>` (engineer) run before the
plan question, which derives from the plan's branch or named modules the touched paths, their zones
(`containment.py zones`), the VERSION each touched craft owes (`check_drift` against the latest tag) and the tests that
import a touched module, and prints every one absent from `## Files touched`; moment: plan time (advisory — the plan is
partly written before the code exists, so it cannot be a refusal).

## Status
Exit 2 — backlog row; fence row proposed: **R-c** (index, Proposals).
