# Incident mode 41 — trace windows anchor by text match and mixed date bases, and previews enter the store

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
trace windows anchor by text match and mixed date bases, and previews enter the store.

**What would have to change** (the derivation's one-sentence test): anchor by kind, id and one date base, and refuse a preview in the store, at trace.

**Predecessor:** mode R of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-r.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 93 | 2026-10-05 | #212 | V1-45 |
| 127 | 2026-10-09 | #251 | V1-45 |
| 167 | 2026-10-14 | #297 | V1-45 |
| 201 | 2026-10-12 | #285, #260, #261 | V1-45 |
| 203 | 2026-10-12 | #285, #260, #261 | V1-46 |
| 204 | 2026-10-12 | #222, #231, #232 | V1-46 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: yes: 127, 167, 201, 203, 204 after #212 rev 3's anchor fix.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| anchor by kind and date, first candidate only | `dyad/scripts/trace.py:355-367` `anchor` (`_note_kind`, `ynk`, `cands[:1]`) (#212 rev 3, 2026-10-05) | trace | 93 | 127, 167, 201, 203, 204 | shipped | **yes**: 127 (10-09), 167 (10-14), 201, 203, 204 (10-12) |
| compaction summary and non-human origins never anchor | `trace.py:246-261` (`isCompactSummary`, origin filter) (#240/#286, 2026-11-02) | trace | 127 (the compaction match) | Agent's own quotations in later replies are still Operator-candidates only by text; 167, 201, 203, 204 | shipped | no row after 11-02 |
| one date base | still mixed: entries stamped local `datetime.date.today()` `package.py:2014`, compared to UTC `trace.py:369` (`utc(...)[:10] == e["date"]`); `utc_date()` `package.py:471` exists but only for the suite memo | — | — | 167 | candidate | — |
| refuse a preview in the store | none: `--out` writes unconditionally `trace.py:686-690`; `check_store` `trace.py:460-482` checks name, row, header, sections only | — | — | 203, 204 | candidate | — |
| Done record must carry a trace | `package.py` `trace_refusal` (`:1994`), `rows.trace_problems` (#465, 2026-10-26) | call, push | none of the six (presence of the file, not its content) | 201-204 | shipped | — |

Closure: (2) backlog, NEW fence — `append_provenance` dates entries by `utc_date()` and `trace.check_store` fails a
stored file carrying a `- preview:` line while `--out` refuses a row with no Done disposition, at call and push
(`agent/traces`); owner engineer. The #240/#286 rows are done; no open row names this.

## Status
Exit 2 — backlog row; fence row proposed: **R-b** (index, Proposals).
