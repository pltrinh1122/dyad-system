# Incident mode 10 — dwork verbs write a commit or entry the fence or format will refuse (open+planned in one commit, doubled date)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 4 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
dwork verbs write a commit or entry the fence or format will refuse (open+planned in one commit, doubled date).

**What would have to change** (the derivation's one-sentence test): the verb validates against the fence's rules before its first write, at write.

**Predecessor:** mode S of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-s.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 13 | 2026-09-14 | #1 | V1-07 |
| 16 | 2026-09-14 | #16 | V1-07 |
| 147 | 2026-10-13 | #287 | V1-07 |
| 164 | 2026-10-14 | #297 | V1-09 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| a new row file must start in `NEW_STATES` | `rows.py:439` in `check_commit` | push | 13, 16, 147 | — | shipped 2026-09-14 (`52024e66`) | 147 (detected) |
| each added `disposed` entry must match `<date> <Y|N> …` | `rows.py:139` `disposed_problems`, `ENTRY` `:71` | push | 164 (`2026-10-14 2026-10-14 Y plan` fails `ENTRY`) | — | shipped 2026-09-29 (`06d4a55b`) | 164 (detected) |
| `--land` makes one commit per verb call | `land.py` (module doc) | call | 13, 16, 147 (new + state no longer share a commit) | — | shipped 2026-10-25 | none after |
| `dwork state --check` runs every refusal and writes nothing | `package.py:2119` | call | 147, 164 when used | — | shipped 2026-10-28 (`9aeb8784`, #464) | none after |
| batch refuses one id both recording a merge-naming `Y done` and set `done` | `land.py:547` `done_order` | batch parse | — | — | shipped 2026-10-26 (`41b07539`) | — |

Gap: the verb does not itself refuse a `-d` that begins with a date (it refuses only `;` and line breaks, `package.py:2028`, `:2030-2033`); the shape is caught at push.

Closure: (1) fenced — at push by `rows.check_commit` (`:439`, `disposed_problems`); prevention at the call by `--land` and `--check`. Candidate refinement: `dwork state|new` refuse `-d` text matching `^\d{4}-\d{2}-\d{2} ` before the first write (engineer).

## Status
Exit 1 — fenced.
