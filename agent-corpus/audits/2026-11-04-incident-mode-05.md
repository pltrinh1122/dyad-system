# Incident mode 05 — a figure, sha, state or rule clause stated from the Agent's memory or a digest, not re-read from its source in the same turn

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 11 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a figure, sha, state or rule clause stated from the Agent's memory or a digest, not re-read from its source in the same turn.

**What would have to change** (the derivation's one-sentence test): every value in a reply or record is pasted from a command run in that turn, at write time.

**Predecessor:** mode C of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-c.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 4 | 2026-09-24 | #81 | V1-29 |
| 63 | 2026-09-25 | #166 | V1-29 |
| 71 | 2026-09-29 | #192 | V1-29 |
| 92 | 2026-10-05 | #223 | V1-29 |
| 113 | 2026-10-07 | #229 | V1-33 |
| 114 | 2026-10-08 | #242 | V1-29 |
| 130 | 2026-10-09 | #256 | V1-29 |
| 131 | 2026-10-09 | #259 | V1-29 |
| 186 | 2026-10-15 | #326 | V1-29 |
| 227 | 2026-10-20 | #348 | V1-29 |
| 238 | 2026-10-26 | #475 | V1-60 |

Secondary mechanism on rows: 63 (V2-07), 238 (V2-47). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| merge verb takes a full sha and refuses unless it is the PR's live head | `dyad/scripts/merge.py:55` `parse` (FULL_SHA), `:96` live-head refusal | merge | 92 | all others | shipped 2026-10-31 (`846df15c`, #532) | none after |
| `steps done-record` composes the Done entry from the PRs' live heads | `dyad/scripts/steps.py` (module doc, `done-record`) | call | heads in Done records | all rows of this group | shipped 2026-11-02 (`5ea1ff90`) | none after |
| evidence block cited by sha256, re-runnable | `package.py:1287` `cmd_evidence`; Rule-14 p3 | `check --evidence` | merge-evidence figures | 4, 63, 71, 113, 114, 130, 131, 186, 227, 238 | shipped (#476, 10-26) | 238 (10-26, same day) |
| bundle/VERSION guard fails a live VERSION not matching its row | `bundle.py:161` `check` (strict clause) | push | 63 (the downgrade would fail) | — | shipped | — |
| Rule-10/Rule-9 enforcement is inference | `RULE-10-proposal-framing.md:30`, `RULE-9-falsification.md:28` | conduct | — | 4, 71, 113, 114, 130, 131, 186, 227, 238 | shipped (stated inference) | n/a |

Closure: (3) impossible on this kernel for the residue — a value written into a reply, a plan's prose, an immutable row title (186, 131) or a change-log cell (130) is checked by no mechanism that knows the true value: Rule-7 Boundaries keep the transcript out of the corpus, and Rule-10/Rule-9 Enforcement are "inference only, stated". The machine-read sub-case (heads, shas) is fenced by `dyad merge` and `steps done-record`. Backlog #264 should close on this recorded impossibility.

## Status
Exit 3 — impossible on this kernel.
