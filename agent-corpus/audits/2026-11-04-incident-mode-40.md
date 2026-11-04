# Incident mode 40 — the practice requires an act the CLI or store has no form or verb for, so it is hand-written or routed around

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 7 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
the practice requires an act the CLI or store has no form or verb for, so it is hand-written or routed around.

**What would have to change** (the derivation's one-sentence test): add the verb or entry form, at design.

**Predecessor:** mode M of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-m.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 37 | 2026-09-17 | #65 | V1-48 |
| 76 | 2026-09-29 | #133, #191 | V1-50 |
| 121 | 2026-10-09 | #256 | V1-50 |
| 128 | 2026-10-09 | #256 | V1-50 |
| 154 | 2026-10-14 | #259, #290 | V1-50 |
| 207 | 2026-10-22 | #369, #385, #388, #395 | V1-50 |
| 237 | 2026-10-26 | #486 | V1-10 |

Secondary mechanism on rows: 76 (V2-25). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `ledger-pr-merge: agent` standing disposition | `preferences-corpus/PREFERENCES.md` key `ledger-pr-merge` (#66, 2026-09-18) | conduct at merge | 37 | others | shipped | no (37 is 09-17) |
| ledger-only range exempt from the plan gate | `dyad/guards/agent/prs.py:65` `ledger_only`; `dyadlib.py:332` (#191) | push | 76 | others | shipped (09-24/09-29) | no |
| events-only clerical class | `dyadlib.py:365` `events_only`, `prs.py:12` (#438/#440, 2026-10-25) | push | 128 (events can reach `main` clerically) | others | shipped | no |
| mandate entry form | `package.py:93` `dwork new --mandate`, `:120` `dwork state <id> done --mandate` (state form 2026-10-24) | call | 154, 207 | others | shipped | 207 (10-22) is before the state form |
| `Y merge` under with-done warns | `dyad/guards/agent/rows.py:205-213` `merge_disposition_warnings` (#519, 2026-10-28) | commit/push (warn) | 237 | others | shipped | no (237 is 10-26) |
| renumber verb | none (`grep renumber package.py` empty) | — | — | 121 | — | — |

Closure: (2) backlog #274 (mode M, no legal order, no verb) — six of seven rows have their verb; row 121's renumber
still has none (NEW: `dyad dwork renumber <old> <new>` replaying row, plan and record, at call; owner engineer).

## Status
Exit 2 — backlog row; fence row proposed: **R-h** (index, Proposals).
