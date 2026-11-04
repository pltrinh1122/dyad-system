# Incident mode 46 — cross-session coordination carried on channels the acting session does not read before acting (unpushed work, chat queue)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 3 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
cross-session coordination carried on channels the acting session does not read before acting (unpushed work, chat queue).

**What would have to change** (the derivation's one-sentence test): coordination state lives in a store the acting verb reads, at the act.

**Predecessor:** mode T of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-t.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 14 | 2026-09-14 | #3 | V1-34 |
| 229 | 2026-10-21 | #348 | V1-35 |
| 248 | 2026-11-02 | #558 | V1-35 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| presence `files` overlap | `dyad/guards/agent/sessions.py:539` `overlaps` (Rule-16 Presence, #185 2026-09-14; refreshed by #567) | plan time, advisory | 14 (same file, different seat) | 229 (prompts in flight), 248 (a hold) | shipped | yes: 229 (10-21), 248 (11-02) are after, of a shape it does not read |
| "behind origin/main by n" | `sessions.py:733` (#482, 2026-10-28) | session touch | 14 | 229, 248 | shipped | 248 after |
| inbox and board on `main` | `dyad/guards/agent/inbox.py:289` `post`; `board.py` (#536, #535, 2026-11-02) | read each turn (conduct) | — | 248 (the hold went by chat; no push reads either store) | shipped | 248 same day |
| pre-push reads a hold | none (`hold` absent from `package.py` pre-push path; `done_head_refusals` `:1064` guards heads, not holds) | — | — | 248 | candidate | — |

Closure: (2) backlog #281 (mode T) — NEW fence for 248: a `hold:` line in `board/_cos.md` that `check --guards
--pre-push` refuses a push to `main` on, at push; owner engineer. 229 (unpushed prompts) stays inference.

## Status
Exit 2 — backlog row; fence row proposed: **R-e** (index, Proposals).
