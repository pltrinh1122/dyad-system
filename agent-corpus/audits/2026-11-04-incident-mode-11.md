# Incident mode 11 — disposition/provenance entries written by free text without the Operator's words or for no disposition

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 4 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
disposition/provenance entries written by free text without the Operator's words or for no disposition.

**What would have to change** (the derivation's one-sentence test): verbs write the row and its provenance entry together and refuse without the Operator's words, at write.

**Predecessor:** mode B of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-b.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 20 | 2026-09-15 | #18 | V1-18 |
| 55 | 2026-09-25 | #161 | V1-53 |
| 70 | 2026-09-29 | #185 | V1-53 |
| 75 | 2026-09-29 | #191 | V1-54 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `-d` refused without `--said`; a row refused without `--prompt` or `-d/--said`; `--backlog` needs `-d` | `package.py:2053`, and the `new` branch refusals after `:2070` | call | 55, 70, 75 (form) | 20 (words supplied but no question was asked) | shipped 2026-09-29 (`0d59f1a3`, #191) | none after |
| row and record move together: k disposed entries ⇔ k disposition entries; born row has an entry | `provenance.py:246` `check_commit` | push | 75 | 20, 55, 70 if fabricated words are given | shipped 2026-09-29 | none after |
| state check over the store (count parity, legacy list) | `provenance.py:181` `check_package` | package check / evidence | 75 | — | shipped 2026-09-29 | none after |

Closure: (1) fenced at the call and at push for the form (every row of this mode dated ≤ 09-29, none after). Residue (3): whether the words were the Operator's, or answered a question actually asked (row 20), is inference — `RULE-7-provenance.md:110` "Whether an entry is a faithful transcription is inference"; no mechanism reads the chat. Backlog #263 (mode B) can close on that.

## Status
Exit 1 — fenced.
