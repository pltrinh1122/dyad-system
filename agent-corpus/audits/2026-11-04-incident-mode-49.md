# Incident mode 49 — provenance transcription not verbatim; nothing compares it with the Operator's typed words

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
provenance transcription not verbatim; nothing compares it with the Operator's typed words.

**What would have to change** (the derivation's one-sentence test): entries are copied from the original characters, with a comparison, at entry.

**Predecessor:** mode B of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-b.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 249 | 2026-11-02 | #560 | V1-55 |
| 250 | 2026-11-03 | #561 | V1-55 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| words by file, not retyped | `package.py:1855-1858` `--prompt-file`, `--said-file`; `inbox post --body-file` `package.py:228` | call | 250 (relay could carry a file) | 249 (the copy was already normalized) | shipped | — |
| count check | `dyad/guards/agent/provenance.py` state check (Rule-7 p5) | push | neither (counts, not characters) | 249, 250 | shipped | — |
| trace reads the transcript and matches entries | `trace.py:334-336` `_matches` (whitespace-only `norm` `:100`) | trace | 249 would show as `unmatched`, unlabelled | 250 (relay seat's transcript) | shipped (incidental) | — |

Closure: (2) backlog, NEW fence — `dwork trace` labels an entry that anchors only after normalisation, or not at all
while its turn exists, as `not verbatim`, at trace (the Done record); owner engineer, counsel on Rule-7 p2's reading
(the trace reads the harness file in place and writes none of it, so p2 is not breached). 250's relay copy remains
inference unless the relaying seat's transcript is the one traced.

## Status
Exit 2 — backlog row; fence row proposed: **R-b** (index, Proposals).
