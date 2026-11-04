# Incident mode 29 — presence identity and claims not bound to the holder (fresh uuid per call, per-process writer, shared name, rows from the whole ledger, root string compare)

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 12 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
presence identity and claims not bound to the holder (fresh uuid per call, per-process writer, shared name, rows from the whole ledger, root string compare).

**What would have to change** (the derivation's one-sentence test): presence keys and claims come from the holder's harness session id and its own named rows, refusing when unset, at touch.

**Predecessor:** mode R of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-r.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 25 | 2026-09-16 | #30 | V1-15 |
| 31 | 2026-09-16 | #35 | V1-16 |
| 96 | 2026-10-07 | #231 | V1-13 |
| 145 | 2026-10-12 | #285 | V1-13 |
| 152 | 2026-10-14 | #290 | V1-16 |
| 153 | 2026-10-14 | #290 | V1-14 |
| 180 | 2026-10-15 | #301 | V1-16 |
| 192 | 2026-10-17 | #341 | V1-16 |
| 205 | 2026-10-13 | #286 | V1-13 |
| 208 | 2026-10-24 | #401, #369 | V1-15 |
| 226 | 2026-10-20 | #348 | V1-43 |
| 228 | 2026-10-21 | #348 | V1-14 |

Secondary mechanism on rows: none. Recurrence after a mitigation the cells describe: yes: 205 after stable DYAD_SESSION; 228 after F1 (#32); 180, 192 after #130.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| a presence write refuses with `DYAD_SESSION` unset | `dyad/guards/agent/sessions.py:288-289` `touch` raises `SessionUnset` | call | 96, 145, 205, 226 (no unnamed file is minted) | 226's absence of any touch | shipped (#480, 2026-10-28) | none after |
| writer keyed on the harness session id | `sessions.py:129` `writer` (`holder() or _PROCESS`) | call | 153, 228 | — | shipped (#350, 2026-10-25) | none after (153, 228 were after the F1 fence of #32, 2026-09-16 — the fence was the defect) |
| bare touch claims only owned rows | `sessions.py:512` `touch_owned` | call | 31, 152, 180, 192 | — | shipped (#567, 2026-11-03) | none after (180, 192 recurred after #130's conduct note) |
| touch refuses words other than `-r`/`-f` | `sessions.py:718-722` | call | 192-shape | — | shipped (#479, 2026-10-28) | none after |
| claimed rows' plan files enter `files` | `sessions.py` `touch` (`file_set |= files_of_rows`, #311 note) | call | 152 (`files`) | — | shipped (#567) | — |
| same-root qualified by host and holder | `sessions.py:564` `shares_checkout` | `session touch/list` | 208 | — | shipped (#434, 2026-10-25) | none after |
| id collision / contiguity | `rows.py:466-467` `check_id_collisions`, `contiguity_problems` | push | 25 (id collision) | 25 (duplicate work) | shipped | — |
| one holder behind two seats | backlog #313 | — | — | — | candidate | — |
| a session-start touch that never happened | nothing reads an absent presence file | — | — | 226 | — | — |

Closure: (1) fenced at the call (`touch` refuses, keys and claims from the holder); residuals: backlog #313 (one holder,
two seats) and 226 (no touch at all) — NEW: the SessionStart hook (`.claude/settings.json`) runs `dyad session touch`
after bootstrap when `DYAD_SESSION` is set (engineer; moment: session start). 25's duplicate work stays conduct
(Rule-16's pre-plan read).

## Status
Exit 1 — fenced.
