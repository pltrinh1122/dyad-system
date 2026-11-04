# Incident mode 24 — the hook execs its guard by path, so a mode change or missing exec bit kills it

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 2 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
the hook execs its guard by path, so a mode change or missing exec bit kills it.

**What would have to change** (the derivation's one-sentence test): the hook invokes the guard through the interpreter, at hook design.

**Predecessor:** mode V of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-v.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 26 | 2026-09-16 | #6 | V1-52 |
| 30 | 2026-09-16 | #25, #27, #35 | V1-52 |

Secondary mechanism on rows: 30 (V2-25). Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| hooks run their guard through the interpreter resolver | `dyad/hooks/pre-commit:4`, `dyad/hooks/pre-push:5` → `dyad/bin/dyad-python:24-40` | hook design | 26, 30 | — | shipped (#24, 2026-09-16; resolver #82, 2026-09-24) | none |
| call sites pinned by test | `dyad/tests/test_entrypoint.py:26` `CALL_SITES`; `dyad/tests/test_livetest.py:150` (modes kept) | push (suite) | 26, 30 | — | shipped | none |

Closure: (1) fenced — the hook execs `dyad-python <guard>`, so a lost exec bit no longer kills it; the call sites are
pinned by the suite at push.

## Status
Exit 1 — fenced.
