# Incident mode 39 — the table parser splits on separators inside quoted or escaped cells

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
the table parser splits on separators inside quoted or escaped cells.

**What would have to change** (the derivation's one-sentence test): the parser honours escapes, at parse.

**Predecessor:** mode J of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-j.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 99 | 2026-10-07 | #231 | V1-12 |
| 142 | 2026-10-10 | #259 | V1-12 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| unescaped-only cell split | `dyad/scripts/dyadlib.py:544` `_CELL_SEP = (?<!\\)\|`, `:551` `split_cells` (#171, #7, 2026-10-28) | every parse (incidents check `dyad/scripts/incidents.py:49`, every guard reading a table) | 99, 142 (an escaped `\|` now reads as content) | a raw `|` inside backticks still splits (GFM semantics; the author must escape) | shipped | no (rows 10-07, 10-10) |
| cell-count check | `incidents.py` via `dyadlib.tables` — refused both rows before commit | commit/push suite | 99, 142 (detected) | — | shipped | — |

Closure: (1) fenced — `dyadlib.split_cells` (`dyadlib.py:551`) at parse; a raw separator is still refused by the incident
parser's cell count, which is the intended behaviour.

## Status
Exit 1 — fenced.
