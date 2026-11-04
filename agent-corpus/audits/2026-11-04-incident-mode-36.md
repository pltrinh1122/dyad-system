# Incident mode 36 — test fixtures leak host resources (tmp dirs, inodes)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
test fixtures leak host resources (tmp dirs, inodes).

**What would have to change** (the derivation's one-sentence test): fixtures register cleanup, at fixture creation.

**Predecessor:** mode Y of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-y.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 87 | 2026-10-01 | #199 | V1-40 |
| 185 | 2026-10-15 | #202 | V1-40 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| suite temp-root sweep: each child gets its own `TMPDIR`, removed on pass | `package.py:786-795` `run_suite` (`mkdtemp(prefix="dyad-suite-")`, `shutil.rmtree` in `finally`), `suite_env` `:725-739` (#326, 2026-10-15) | every runner suite run (push gate, `check --evidence`, `check --tests`) | 185 | 87 (not a suite run: a measurement clone running base code); a hand-typed `unittest` (docstring `:778` says it "still leaks") | shipped | no: 185 is the same day as the fix |
| floor check removes its own temp dir | `dyad/guards/craft/crafts.py:151` (`mkdtemp(prefix="dyad-floor-")`, cleanup per docstring `:130,:144`); pinned by `dyad/tests/guards/craft/test_crafts.py:331-364` (#199 N3b, 2026-10-01) | guard call | 87 (the defect it measured) | — | shipped | no: 87 measured the pre-fix base the same day |
| fixtures register cleanup | 102 `mkdtemp` call sites still without cleanup (stated at `package.py:777`) | — | — | hand runs | candidate | — |

Closure: (1) fenced — `run_suite`'s temp-root sweep at every runner suite run (`package.py:786`); the hand-run residue is
Rule-12 property 2 conduct (the suite is the runner's), stated.

## Status
Exit 1 — fenced.
