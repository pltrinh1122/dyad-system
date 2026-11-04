# Incident mode 03 — a file or command uses an id assumed or remembered before the allocator's printed answer is read

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 4 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a file or command uses an id assumed or remembered before the allocator's printed answer is read.

**What would have to change** (the derivation's one-sentence test): writers take the id from the allocator's output in the same verb (no separate id typing), at file creation.

**Predecessor:** mode C of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-c.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 3 | 2026-09-24 | #156 | V1-04 |
| 28 | 2026-09-16 | #26, #34 | V1-04 |
| 29 | 2026-09-16 | #27 | V1-04 |
| 193 | 2026-10-21 | #356 | V1-04 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| a provenance record only grows; overwriting another row's record fails | `dyad/guards/agent/provenance.py:241` `_grows`, `:246` `check_commit` | push (transaction) | 3, 29 (record overwrite) | 28 (plan + row files), 193 (plan file of another row) | shipped 2026-09-29 (`0d59f1a3`, #191) | none after for records; 193 (10-21) is a plan, unreached |
| new row ids contiguous from base max+1 | `dyad/guards/agent/rows.py:568` `contiguity_problems` | push | a hand-typed row id | 3, 28, 29, 193 (the row id was right; the *other* files used a wrong one) | shipped 2026-10-28 (`54326428`, #467) | n/a |
| `--land` runs the verb and commits only what it wrote | `dyad/scripts/land.py` (module doc; `fetch:151`, `written:172`) | call | — | 193 (plan files are written by hand, outside the verb) | shipped 2026-10-25 (`abf9db93`, #447) | none after |

`plans.py` checks only that `# Plan #<id>` equals the file name (`dyad/guards/agent/plans.py:45` `check_plan`); nothing refuses a commit that rewrites another row's existing plan.

Closure: (2) backlog — NEW fence: the row fence's transaction check refuses a commit that changes the title line `# Plan #<id> — <title>` of an existing plan file, or writes a plan whose title differs from row `<id>`'s title (plan title immutable like the row's, `rows.py:397` pattern), at push; owner engineer. (Alternative at write: `dwork new` seeds `plans/<id>.md` itself.)

## Status
Exit 2 — backlog row; fence row proposed: **R-c** (index, Proposals).
