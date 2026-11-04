# Incident mode 07 — an unfetched or local-only view of shared state (refs, tags, local main, pre-rebase sha) read as origin's

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 7 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
an unfetched or local-only view of shared state (refs, tags, local main, pre-rebase sha) read as origin's.

**What would have to change** (the derivation's one-sentence test): reads of shared state go through a verb that fetches (tags included) and reads origin, at read time.

**Predecessor:** mode T of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-t.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 22 | 2026-09-16 | #22 | V1-33 |
| 24 | 2026-09-16 | #22 | V1-34 |
| 42 | 2026-09-18 | #80 | V1-33 |
| 170 | 2026-10-15 | #301 | V1-37 |
| 172 | 2026-10-15 | #310 | V1-37 |
| 178 | 2026-10-15 | #297 | V1-37 |
| 224 | 2026-10-20 | #348 | V1-34 |

Secondary mechanism on rows: 172 (V2-21). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| SessionStart hook runs `dyad bootstrap`: unshallow, fetch tags, hooksPath | `.claude/settings.json` SessionStart; `bootstrap.py:202` `step_history`, `:215` `step_tags` | session start | 42 (tags) | 22, 24, 170, 172, 178, 224 (branches/main not fetched) | shipped 2026-10-26 (`1f1dabf8`, #474) | none after |
| evidence refuses a shallow or tagless clone | `bootstrap.py:155` `clone_problems` | `check --evidence` | 42 | the rest | shipped 2026-10-26 | none after |
| `session touch` prints "behind origin/main by n" | `dyad/guards/agent/sessions.py` `behind_origin` (docstring: "never fetching"), printed in `main` | session start / plan-Y | 224 (if origin/main ref is fresh) | 224 when the ref itself is stale | shipped 2026-10-28 (`e5d21c3e`, #482) | none after |
| ledger and merge verbs fetch and read origin/main | `land.py:151` `fetch`; `merge.py` (reads only origin/main + `ls-remote`) | call | 24, 178 shape for ledger writes | reads by raw git | shipped 2026-10-25 / 10-31 | none after |
| local-only base sha fails | `references.py:416` `plan.base->commit` | push | 170, 172 (detected) | — | shipped (≤09-16) | 170, 172 after (detected) |

Discrepancy: row #482's title says "after a fetch"; the code at HEAD says `behind_origin` "never fetch[es]" — it counts against the last-fetched `origin/main` ref, so a never-fetched clone prints nothing.

Closure: (2) backlog #281 (mode T). NEW fence: `dyad session touch` fetches `origin` (refs and tags, with a timeout and a skip line) before computing `behind_origin`, so the session-start report is stated against a fresh origin, at session start and plan-Y; owner engineer. Raw `git log main`/`git tag` reads by the Agent stay unfenceable by the dyad (harness-side only).

## Status
Exit 2 — backlog row; fence row proposed: **R-e** (index, Proposals).
