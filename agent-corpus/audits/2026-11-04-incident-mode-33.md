# Incident mode 33 — an environment property the step relies on differs from the authoring host (interpreter, gh account, clone depth/tags, draft PRs, CI git version, token semantics)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 8 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
an environment property the step relies on differs from the authoring host (interpreter, gh account, clone depth/tags, draft PRs, CI git version, token semantics).

**What would have to change** (the derivation's one-sentence test): a preflight probes the property the step needs and refuses on mismatch, at step start.

**Predecessor:** mode I of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-i.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 21 | 2026-09-16 | #22 | V1-38 |
| 65 | 2026-09-28 | #178 | V1-42 |
| 90 | 2026-10-05 | #223 | V1-36 |
| 110 | 2026-10-06 | #226 | V1-42 |
| 160 | 2026-10-15 | #301 | V1-36 |
| 162 | 2026-10-15 | #302 | V1-36 |
| 189 | 2026-10-17 | #333 | V1-36 |
| 236 | 2026-10-26 | #474 | V1-38 |

Secondary mechanism on rows: 21 (V2-24). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| interpreter resolver against the kernel pin | `dyad/bin/dyad-python:24-40`; pin test `dyad/tests/test_entrypoint.py` | every `dyad` call and hook | 21 | — | shipped (#82, 2026-09-24) | none after |
| shallow/tagless clone: bootstrap and evidence refusal | `bootstrap.py:155`, `:202` `step_history`, `:215`; `package.py:1294` | session start, evidence | 90, 160, 162, 189 | push path (still runs on a shallow clone) | shipped (#474 2026-10-26, #505) | none after |
| fixture git auto-maintenance disabled | `livetest.py:52`; `package.py:720` | spawn | 236 | — | shipped (2026-10-27) | none after |
| merges through git, not the hosting API | `merge.py:86-117` (`git merge --no-ff`, push) | call | 65 (gh account), 110 (draft) | — | shipped (#532, 2026-10-31) | none after |
| token semantics, other World properties | Rule-14 p4 (The World observed, never pinned) | — | — | residual | — | — |

Closure: (1) fenced for each property met so far (interpreter, clone depth/tags, CI git, hosting account/draft);
the class itself is (3) for the next unknown property — Rule-14 p4: The World is observed, not pinned. Backlog #270
(mode I), #282 (mode U).

## Status
Exit 1 — fenced.
