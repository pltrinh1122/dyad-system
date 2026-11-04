# Incident mode 17 — a plan's step order or closure written without checking what authorizes each step (with-done, plan gate, backlog children)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a plan's step order or closure written without checking what authorizes each step (with-done, plan gate, backlog children).

**What would have to change** (the derivation's one-sentence test): each plan step is checked against the disposition and gate that admits it, before the plan-Y.

**Predecessor:** mode L of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-l.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 33 | 2026-09-16 | #32 | V1-26 |
| 122 | 2026-10-09 | #256 | V1-26 |
| 138 | 2026-10-09 | #259 | V1-26 |
| 144 | 2026-10-10 | #259 | V1-26 |
| 163 | 2026-10-15 | #249 | V1-26 |
| 181 | 2026-10-15 | #321 | V1-26 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| a decomposed parent is askable with `backlog` children and children awaiting a recorded merge | `RULE-3-d-work.md:156` (decompose bullet) | plan / Done | 144 | — | shipped 2026-10-14 (#290) | none after |
| three-act Done order: a ratified merge after the record has a path | `RULE-3-d-work.md:259` | design | 163 (the plan gate no longer refuses a not-yet-done row) | 33, 181 (hold across one counter-prompt is inherent to `with-done`) | shipped 2026-10-15 | none after |
| execution detail is not a departure; a needed order is stated `order: required` | `RULE-3-d-work.md:100`; `RULE-15-d-work-phases.md:23`; `dyad/dmc/plan-departure.jsonld` | plan time (inference) | — | 33, 122, 138, 181 | shipped 2026-11-02 (`798622fd`, #555) | none after |
| DMC records for held PRs and parent askability | `dyad/dmc/held-pr.jsonld`, `dyad/dmc/parent-askable.jsonld` | plan time (inference) | 138, 144 if consulted | — | shipped 2026-10-27 (`2d2d2481`, #508) | none after |

Closure: (2) backlog #273 (mode L) and #272 (mode K). No mechanism reads a plan's step sequence; plans are prose (`plans.py` checks header parts only). NEW fence: a plan stating `order: required` carries its step sequence as `step: <act> <- <authorizing input>` lines, which `plans.py` checks against `dyadlib.INPUTS` (each act's input exists and precedes it in the d-work machine), at push of the plan file before the plan-`Y`; owner counsel (form) then engineer.

---

## Counts

- (1) fenced: V2-04, V2-10, V2-11, V2-14, V2-15 — 5
- (2) backlog: V2-01, V2-02, V2-03, V2-06, V2-07, V2-08, V2-09, V2-12, V2-13, V2-16, V2-17 — 11 (existing rows: #269/#270, #274, #265/#266, #281, #276, #268, #262/#277, #273/#272; NEW proposals for V2-03, V2-13, V2-16 and a sharper fence for each of the others)
- (3) impossible on this kernel: V2-05 — 1 (with residues of class 3 noted under V2-06, V2-11, V2-12)

## Not verified

- Why the plan gate (shipped 09-14) did not stop rows 43/45 (09-20, 09-22): not determined from code.
- Live CLI defects under V2-09 were read from the code, not run (read-only task).
- Row 171/175 vs `0a4060e3` and row 215 vs `ba4c1fd1`, row 246 vs `dcf8f1b5`: same day, time order unknown.
- Row 188 (naming guard vs `DYAD_KEEP_TMP`) and rows 60/61: no fence identified; the naming guard's contribution path was not read.

## Status
Exit 2 — backlog row; fence row proposed: **R-c** (index, Proposals).
