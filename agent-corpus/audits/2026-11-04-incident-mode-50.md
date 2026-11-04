# Incident mode 50 — a push to a public remote quotes private material; no check at push

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 1 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a push to a public remote quotes private material; no check at push.

**What would have to change** (the derivation's one-sentence test): pre-push refusal of private citations on a public remote.

**Predecessor:** mode Q of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-q.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 245 | 2026-10-27 | #498 | V1-44 |

Secondary mechanism on rows: 245 (V2-12). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| private-citation fence | `dyad/scripts/privatecite.py` `check_push`, called from `package.py:1162-1169` in `cmd_guards` pre-push; instance data `agent-corpus/public_remotes.local.txt` (names `github.com/pltrinh1122/dyad-system`), `agent-corpus/private_repos.local.txt` (36 hashes) (#518, 2026-10-28) | push (`dyad/hooks/pre-push` passes `$@`) | 245 | quotes without a citation shape near them (stated as inference in the module docstring) | shipped | no (245 is 10-27) |

Closure: (1) fenced — `privatecite.check_push` at push, fail-closed, no override.

## Status
Exit 1 — fenced.
