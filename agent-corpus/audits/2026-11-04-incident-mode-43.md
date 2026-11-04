# Incident mode 43 — a mutating verb run on live state to probe its check

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a mutating verb run on live state to probe its check.

**What would have to change** (the derivation's one-sentence test): read-only form of each check, at probe.

**Predecessor:** mode O of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-o.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 184 | 2026-10-15 | #202 | V1-22 |
| 231 | 2026-10-25 | #346 | V1-22 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| read-only form of the close checks | `package.py:114-117` `dwork state … --check`, flag table `:1858` (#464, 2026-10-28) | call | 184, 231 | other mutating verbs (`board set`, `inbox read`, `land`) have no `--check` | shipped | no (184 10-15, 231 10-25) |
| tests own a temp repo | `dyad/tests/guards/agent/test_rows.py` `Repo` | test | 184 (the alternative named) | — | shipped | — |

Closure: (1) fenced for the verb both rows used — `dwork state --check` at call; a probe of another verb is conduct (the
fence is a read-only twin per verb, which #276 mode O covers).

## Status
Exit 1 — fenced.
