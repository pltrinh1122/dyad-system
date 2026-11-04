# Incident mode 04 — ids allocated max(origin,local)+1 by sessions holding unpushed ids collide

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 6 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
ids allocated max(origin,local)+1 by sessions holding unpushed ids collide.

**What would have to change** (the derivation's one-sentence test): one shared allocator (or reservation) visible before the id is used, at allocation.

**Predecessor:** mode T of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-t.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 64 | 2026-09-28 | #178 | V1-05 |
| 91 | 2026-10-05 | #223 | V1-05 |
| 94 | 2026-10-05 | #225 | V1-05 |
| 120 | 2026-10-09 | #256 | V1-05 |
| 148 | 2026-10-14 | #291 | V1-05 |
| 168 | 2026-10-08 | #243 | V1-05 |

Secondary mechanism on rows: 168 (V2-15). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `dwork new` fetches origin/main before allocating | `dyad/scripts/package.py:2091` | call | shrinks the window | 64, 91, 94, 120, 148, 168 (all held the id unpushed) | shipped 2026-09-16 (`67f0d883`, #32 F3) | yes: all six after |
| id reused at base under another title fails | `rows.py:530` `check_id_collisions` (branch), wired `rows.py:466` | push | 91, 120, 148, 168 (detected, refused) | 94 (hosting refused the merge; same detection) | shipped 2026-09-16 (`67f0d883`) | yes: detection only |
| allocate, commit and push in one call on a fresh origin/main; a refused push re-allocates | `land.py` module doc ("a `new` re-allocates its id"), `fetch:151`, `prepare:157` | call (`dwork new … --land`) | all six (no unpushed id is ever held) | a plain `dwork new` without `--land` | shipped 2026-10-25 (`abf9db93`, #447) | none after |

Closure: (1) fenced — prevention at the call by `dwork new --land` (`land.py`), detection at push by `rows.check_id_collisions` + `contiguity_problems`. Residue: `--land` is not mandatory; a plain `dwork new` can still hold an id unpushed, which the push fence catches.

## Status
Exit 1 — fenced.
