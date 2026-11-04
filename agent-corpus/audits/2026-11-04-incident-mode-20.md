# Incident mode 20 — a token in prose or a field (d-work #N, PR #N in a d-work cell) read by a parser as a claim or reference

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 5 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a token in prose or a field (d-work #N, PR #N in a d-work cell) read by a parser as a claim or reference.

**What would have to change** (the derivation's one-sentence test): the writing step lints reference tokens before commit (pre-commit runs the citation/reference parse).

**Predecessor:** mode F of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-f.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 36 | 2026-09-16 | #15 | V1-11 |
| 86 | 2026-10-01 | #199 | V1-11 |
| 137 | 2026-10-09 | #259 | V1-11 |
| 166 | 2026-10-14 | #297 | V1-11 |
| 239 | 2026-10-27 | #487 | V1-10 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no (36's lesson recorded only).

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| plan gate reads `d-work #N` in commit messages | `dyad/guards/agent/prs.py:28` `CITE`, run over the pushed range by `package.py` `cmd_guards --pre-push` | push | 36, 86, 137, 166 | 239 | shipped (0.3.1; pre-push over pushed refs #194, 2026-09-30) | 86, 137, 166 after it — each caught at push |
| Rule-20 incident `d-work` cell resolution | `dyad/guards/agent/references.py:428` `incident.dwork->row` | push | 239 | 36, 86, 137, 166 | shipped | 239 caught |
| ledger verbs generate subjects citing no `d-work #` | `dyad/scripts/land.py` (module doc: "a generated `ledger: …` subject that cites no `d-work #`") | call | the ledger-commit share of the mode | hand-written commit messages | shipped (#447, 2026-10-25) | none after |
| commit-msg lint | none (`dyad/hooks/` holds only pre-commit and pre-push) | — | — | all | candidate | — |

Closure: (1) fenced at push — `prs.CITE` and `references` refuse every instance before it leaves the clone; nothing
reached `main`. The recurrence is the fence's measured cost (one amended message), not a hole. Optional earlier
moment: a `dyad/hooks/commit-msg` running `prs.CITE` against the ledger (engineer).

## Status
Exit 1 — fenced.
