# Incident mode 21 — success read from filtered output, a pipeline's exit or a string match rather than the command's own exit and the remote state

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 7 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
success read from filtered output, a pipeline's exit or a string match rather than the command's own exit and the remote state.

**What would have to change** (the derivation's one-sentence test): each step's exit code and the remote object are checked directly after it, at command end.

**Predecessor:** mode E of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-e.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 7 | 2026-09-23 | #114 | V1-48 |
| 8 | 2026-09-23 | #114 | V1-33 |
| 98 | 2026-10-07 | #231 | V1-27 |
| 124 | 2026-10-09 | #256 | V1-27 |
| 187 | 2026-10-15 | #326 | V1-27 |
| 197 | 2026-10-22 | #387 | V1-27 |
| 232 | 2026-10-26 | #455–#460 | V1-27 |

Secondary mechanism on rows: 232 (V2-09). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| ledger landing reads the push's own return code, rebuilds on a moved main | `dyad/scripts/land.py:343-374` `land` (`r.returncode`, `fetch` re-read) | call | 7 (no ledger branch to forget), 98, 197 | 8, 124, 187 | shipped (#447, 2026-10-25) | none after |
| merge verb reads the push's return code and the live head | `dyad/scripts/merge.py:86-117` `attempt` | call | 98-shape for merges | — | shipped (#532, 2026-10-31) | none after |
| provenance numbering without gaps | `dyad/guards/agent/provenance.py:122` | push | 7 (a 1,2,3,5 record fails) | others | shipped (0.3.1 lineage) | 7 found by reading first |
| Done record carries its trace; verbs refuse before writing | `dyad/guards/agent/rows.py:181` `trace_problems`; `package.py:1980` `trace_refusal` | call, push | 232 | others | shipped (#465, 2026-10-26) | none after (232 was its trigger) |
| the Agent's own reading of shell output (filters, `&&` chains) | none | conduct | — | 8, 124, 187 | — | — |

Closure: (1) fenced for the landed-state rows (7, 98, 197, 232 — the verb or guard reads the remote and the exit);
residual rows 8, 124, 187 are (3): no mechanism on the kernel reads how the Agent filters its own tool output (Rule-14
p2: the harness is kernel and the dyad owns no layer between the Agent and its shell). Backlog #266 (mode E) holds the mode.

## Status
Exit 1 — fenced.
