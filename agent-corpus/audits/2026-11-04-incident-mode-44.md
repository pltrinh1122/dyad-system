# Incident mode 44 — a release's publication step is untied to the tag mechanism; hand path used

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a release's publication step is untied to the tag mechanism; hand path used.

**What would have to change** (the derivation's one-sentence test): only the workflow publishes, and a ratified tag without a release fails a check.

**Predecessor:** mode A of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-a.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 132 | 2026-09-24 | #158 | V1-49 |
| 133 | 2026-10-08 | #241 | V1-49 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| one release service makes tag and Release from the recorded entry | `dyad/scripts/release.py:1-30`, `publish` `:228-254`, `pending` `:344` (#470, 2026-10-26); `.github/workflows/dyad-release.yml:14-51` (gated environment `:51`, #545) | push to main touching rows (CI) | 132, 133 | a hand `gh release create` is still possible (The World, Rule-14) | shipped | no (09-24, 10-08) |
| sweep: ratified tag without tag/Release | `dyad/scripts/automaton.py:206-215` `sweep_drift` (`no tag:`, `tag not at cut:`, `no Release:` from `runbook run released health`) (#564, 2026-11-03) | scheduled sweep, twice daily | 132-shape (an `at` entry with no Release) | 132 itself: a pre-service `Y release v0.11.0` without `at` is not read (`release.py:13-14`) | shipped | no |

Closure: (1) fenced — `release.py` at the rows push publishes, and the sweep's `released` health detects a ratified tag
with no Release; the hand path is World-side and only detectable.

## Status
Exit 1 — fenced.
