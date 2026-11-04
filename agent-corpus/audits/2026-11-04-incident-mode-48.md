# Incident mode 48 — an Operator-run command delivered inline and pasted

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 1 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
an Operator-run command delivered inline and pasted.

**What would have to change** (the derivation's one-sentence test): only committed ops-script files are offered.

**Predecessor:** mode S of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-s.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 206 | 2026-10-23 | #395 | V1-49 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: no.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| ops-script form guard | `crafts/sysadmin/guards/ops_scripts.py:134` `check_package` (`bash -n` per `<ops>/*.sh`) | push | none (`workstation-corpus/ops/` absent at HEAD: the guard checks 0 files) | 206 | shipped | — |
| release tagging no longer an Operator command | `release.py` (#470, 2026-10-26) | CI | 206's occasion | the class | shipped | no (206 is 10-23) |
| Rule-18 Conduct "never an inline block" | Rule-18 Conduct | conduct | — | 206 | shipped (text) | — |

Closure: (3) impossible on this kernel for the class — what the Agent prints in chat and the Operator pastes is read by
no mechanism; row 206's own occasion (release tags) is removed by `release.py`.

## Status
Exit 3 — impossible on this kernel.
