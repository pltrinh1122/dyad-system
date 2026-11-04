# Incident mode 45 — evidence carried as paraphrase or selection instead of the command's own output form

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 3 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
evidence carried as paraphrase or selection instead of the command's own output form.

**What would have to change** (the derivation's one-sentence test): cite the brief form and sha256 verbatim, at completion reply.

**Predecessor:** mode C of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-c.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 126 | 2026-10-09 | #256 | V1-47 |
| 199 | 2026-10-22 | #378 | V1-47 |
| 202 | 2026-10-12 | #285, #260, #261 | V1-47 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| brief form and sha256 as the citable unit | `package.py:49` `check --evidence --brief`, `:1287` `cmd_evidence`, `:1313` `EVIDENCE_STORE`; Rule-2 Binding, Rule-14 p3 (#476, 2026-10-26) | evidence run | 126 (now the Rule's own form) | 199 (words for a block), 202 (trace lines recomposed) | shipped | no (126 10-09; 199 10-22; 202 10-12) |
| Operator re-run compares sha256 | Rule-14 p3 `check --evidence --show` | Operator, at Done | — | — | shipped | — |
| anything reading the completion reply | none | — | — | 126, 199, 202 | — | — |

Closure: (3) impossible on this kernel — the completion reply is chat, which no mechanism reads (Rule-3 Completion is
inference; the Operator's re-run of the sha256 is the only comparison). A partial fence is possible: the `Y done` entry
could carry the cited `evidence-sha256`, checked against the store at record — offered as a candidate, not required.

## Status
Exit 3 — impossible on this kernel.
