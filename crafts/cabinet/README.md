# cabinet — the AI-agent cabinet: one chief of staff beside the Operator, secretaries over the functions, desks under them (Tended craft, `crafts/cabinet/`, zone `craft`)

M4 as the default organization: a tree of Operator–seat pairs in which the cos and every secretary keep a board, authority is
granted by content-scoped charters in the Operator's hand, and every pair reads and writes the same ledgers
(`rules/organization.md`); the seat-name form `<function>[-<topic>]-<hp>` and its reading rule (`rules/naming.md`);
an advisory guard over the presence store and the mandates table (`guards/seats.py`); the mandates template; and
the **Operating Guide for Operators** (`docs/operating-guide.md`). Authored in dyad-system under #369 (child C9, row
#383) after the countersign craft was retired into the core (C1–C5), so it requires the core only
(`MANIFEST.md`: `dyad-operator>=0.11.0`) and defines no term the core or another craft defines. Scaffolded by
`dyad craft new cos` (renamed `cabinet` by #417, after #415 and #416) through the craft run-book (`dyad/playbooks/craft-instantiation.md`; events
`craft-20261022T011829Z-new`, `craft-20261022T011831Z-check`); version `VERSION` (0.1.1: the Operating Guide carries #384's invariant, #385 G; 0.1.2: the three modes of attendance and the route table, #388; 0.1.3: attendance declared by `attended-seats`, the Operator's span beside the leader's, #412; 0.2.0: renamed `cabinet`, its role terms cos, secretary and desk, a fresh tag line `cabinet-v0.2.0` — `cos-v0.1.2` stays as history, #417; within 0.2.0, before its first tag, audit narrowed to the incident ledger and its hardening, the rest to the domain owners, #433). Not bundled with the core:
a one-pair system needs nothing here (`docs/operating-guide.md` §6), and no core Rule cites this craft by path —
Rule-16 names the form's existence and reads the installed organization craft for its check (#369 C7).

| path | holds |
|------|-------|
| `rules/organization.md` | M4: the tree (§1), the same-ledgers precondition (§2), charters as the mandates table in the #253 band form (§3), the default six functions and the seams between them (§4), the standing conduct of every seat (§5) |
| `rules/naming.md` | the seat-name form (§1), the reading rule — leader, secretary, desk from the tokens alone (§2), the session title (§3), the names history keeps (§4) |
| `vocabulary/CRAFT.md` | `charter`, `cos`, `desk`, `roll-up`, `function`, `topic` — referenced by the Agent vocabulary as `cabinet:<term>`, never defined there; `cos-board`, `secretary`, `seat name` are the core's (#369 C7) |
| `guards/seats.py`, `guards/seats_rules.txt` | entity `seat`, corpus `agent`: every presence file's name against the form (one summary line for the names outside it, never a failure — Rule-16 Presence), the mandates table against the template's columns and the function list (one line per row that differs; absent table, one `skip`); the data holds the form's one regex and the standing functions, read by the guard and by the core's `dyad session name` |
| `templates/mandates.md` | the mandates table with the default organization's six charters; copied by hand to `preferences-corpus/MANDATES.md` (the Operator's PR; no `seeds:` line, `MANIFEST.md` says why) |
| `docs/operating-guide.md` | the Operating Guide: reading a board, opening and naming a seat, writing a charter, what only the Operator disposes, the one-pair case, and what the first live run of M4 cost |
| `falsification/rules/` | one record per rule: `organization.md` (the tree, the precondition, the charters, the conduct), `naming.md` (the form, the syseng-table question, the history) |
| `tests/guards/test_seats.py` | the form and its reading rule, the advisory lines over a fixture, the template's table passing the guard, the live repo never failing |

## Installing the organization
`dyad craft install cabinet-<version>.tar.gz` writes `crafts/cabinet/` and its registry row (Rule-11 property 2) and
nothing else. Then, by hand and by the Operator's own preferences-zone PR:

    cp crafts/cabinet/templates/mandates.md preferences-corpus/MANDATES.md

and edit the rows to the seats the system will open (`docs/operating-guide.md` §3–§4). Until the table exists
`seats.py` prints one `skip` line and the seats run on conduct, as dyad-system's did before #369's PR-B. The
preference `organization` (its key and row: the core's template, #369 C7) says whether a system runs M4 at all.

## Not in this craft
The preference value and the instance's mandates table (preferences zone, the Operator's); the seat-name sentence
of Rule-16, the vocabulary rows `cos-board`, `secretary`, `seat name`, and `dyad session name` (the core, #369
C7); the bus and the rendered board (backlog #303, #304); any host value.
