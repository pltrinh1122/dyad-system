# Incident mode 19 — a corpus artifact written in a guarded form from memory or local habit; the guard runs only at push

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a corpus artifact written in a guarded form from memory or local habit; the guard runs only at push.

**What would have to change** (the derivation's one-sentence test): guarded artifacts are seeded from a template/verb or the guard runs at write.

**Predecessor:** mode S of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-s.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 48 | 2026-09-22 | #116–#125 | V1-10 |
| 89 | 2026-10-05 | #220 | V1-10 |
| 109 | 2026-10-06 | #226 | V1-10 |
| 140 | 2026-10-10 | #261 | V1-10 |
| 143 | 2026-10-10 | #259 | V1-10 |
| 155 | 2026-10-14 | #290 | V1-10 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| file-name pattern guard | `crafts/syseng/guards/naming.py` (`syseng/naming`) | push, evidence | 48 | 89, 109, 140, 143, 155 | shipped | — |
| records guard (attack table header, `Disposition:` line) | `dyad/guards/agent/records.py:21` `FIELDS`, `:25` `DISPOSITION` | push | 89, 109 | others | shipped (form since 0.3.1, 2026-09-14) | 89, 109 after it — caught at push each time |
| incident-log shape (5 cells) | `dyad/scripts/incidents.py:98-99` | suite at push / by hand | 140 | others | shipped | 140 caught by it |
| refs shape fence (no `[]'",`) | `dyad/guards/agent/rows.py:84` `REFS_REFUSED`, `:324` `refs_shape_problems`; `package.py:2040` at `-r` | call, push | none (`parent-46` and bare ids pass) | 143, 155 | shipped (#439, 2026-10-25) | — |
| seeded run-book | `dyad runbook new` (Rule-19 p1) | call | none of these rows | all | shipped | — |

Closure: (2) backlog — #280 (mode S) is the inventory row; NEW fences: (a) seed verbs `dyad record new <slug>` and
`dyad incident add` that write the header/row from `records.FIELDS` and `incidents.FIELDS` (engineer; moment: write);
(b) `rows.refs_shape_problems` refuses a `parent-<n>` token and a bare `parent` (engineer; moment: call and push),
closing 155's silent-edge shape. Row 143 (bare ids where `parent #N` was asked) stays conduct: both forms are legal refs.

## Status
Exit 2 — backlog row; fence row proposed: **R-g** (index, Proposals).
