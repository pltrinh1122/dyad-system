# Falsification record — Rule-21 (guard containment), Operator rule 2026-09-14 (ledger #151)

**Claim (operator, 2026-09-14):** "extend Rules: all entity guards (e.g. referential integrity) a
contained and stored separately of instances but share the same broader corpus, e.g. `agent-corpus`
for Agent entities."

Observed at the base commit (4590b57, #150 in flight): eleven guard modules in one flat `dyad/scripts/`
next to the runner, `dyadlib.py`, four projectors and the run-book runner; the guards of four
workstation entities (change log — none, ops scripts, run-books, events) in the same directory as the
agent ones; four entity kinds (plan file, falsification record, change-log row, preference row) checked
by inference only; the projector listing fourteen entities by hand-written cards.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Reading A: guards move *into* `agent-corpus/guards/` (instance side), as the prompt says literally. | Refuted | Guard code is package (Rule-11 p1: identical across sessions, travels with install); an instance copy diverges per session and a fresh install would have no guards. "Same broader corpus" is satisfied by the zone (`agent` = `agent-corpus` + `dyad`, Rule-1), where the code already is. Reading A is the record's Counter; an `N` naming it re-plans around a Rule-11 change. |
| 2 | Reading B: nothing to do — guards are already apart from instances (`dyad/` vs `agent-corpus/`). | Refuted | Containment failed on (b) and (c): one flat directory mixed guards with the runner, libraries and projectors, and workstation-entity guards lived in the agent directory. The prompt's word *contained* is the ask; property 1 names the layout. |
| 3 | Zone (c) contradicts Rule-1: `dyad/guards/workstation/` is under `dyad/*`, an agent-zone path, so a workstation guard still commits in the agent zone. | Survives, scoped | Zoning is by path (Rule-1 sees paths only) and the package is one tree with one root (Rule-11 p1) — it cannot straddle zones. The survivor is *named* corpus containment inside the package, not zone relocation; Rule-21 Boundaries say so, and Rule-1 is not edited beyond its guard's path. |
| 4 | A big-bang move breaks every path a Rule names and every hook. | Refuted, with a finding | Hooks call `package.py` (pre-push) or the guard by its new path (pre-commit, edited here); Rule text paths are checked by Rule-20 kind 11, which failed 22 stale paths in the PR until the fifteen Rules were edited — the guard did its work. Finding: five `.github/workflows/dyad-*.yml` still invoke the old `dyad/scripts/<guard>.py` paths; infra zone, reported for a separate PR, and CI is absent (billing) so nothing runs them today. |
| 5 | One guard per entity multiplies files (15 guards, 15 tests) for no new check. | Refuted, partly | Six guards are new checks that were inference (plans, records, frame, change-log, preferences, event shape); the rest are moves. The count is the point: one entity, one guard, one test, one data file. Two entity kinds still have no guard and drop off the entities surface (incident row, projector registry entry): stated in Rule-21 Enforcement as inference, a follow-up d-work. |
| 6 | `CHECKS` discovery is magic; a mis-named module silently never runs. | Refuted | Discovery lists what it found (`check --list`); a module under `guards/` that does not load or lacks the contract is a failing check (`test_broken_guard_fails_the_run`); the entities surface shows every guard-backed entity, so an unguarded entity is visible by absence. |
| 7 | This overlaps Rule-11 (layout) and Rule-12 (every code has a check). | Refuted | Rule-11 owns package vs instance and install (its p1 gains one sentence pointing here); Rule-12 owns that code carries a check (its mapping gains the `tests/guards/` branch); Rule-21 owns the guard *contract and placement* — where a guard lives, what it declares, who runs it. Pairwise below. |
| 8 | Easy agreement (Rule-9): the frame's import check moved out of Rule-20's register into `frame.py` is a second resolver for kinds 12 and 13 — Rule-20 property 2 breached. | Refuted | The register keeps both kinds with resolver `guard:agent/frame.py` and never re-runs them (the `test_frame_kinds_are_the_frame_guards` test rewrites the frame and expects no FAIL from the references guard); exactly one resolver, the frame guard's. |

Deferred, named: whether a guard's `FIELDS` matches the Rule's prose; the content of a plan's
sections (mutation 6). Follow-ups: guards for the incident row and the projector registry entry; the
five workflow wrappers (infra zone).

## Rule-5 pairwise statements (Rule-21 added; Rules 1, 2, 3, 4, 6, 11–20 edited for paths only)
- 21–1: Rule-1 owns zones and transactions; Rule-21 names the zone as a directory inside the package and
  moves no path across zones; the containment guard keeps its check and gains the transaction slot.
  21–2: no ratification event; the fence's path changes, its semantics do not. 21–3: the row and PR
  guards keep Rule-3's semantics (fence on `main`, plan gate on a branch) and become TRANSACTION guards;
  the plans guard checks existence of a plan's parts, Rule-3/15 keep what a plan says. 21–4: block
  conforms (intent 1, target 1, boundaries 5, conditions 4); Rule-4's guard keeps its check. 21–5: this
  statement. 21–6: three terms (`guard`, `guard contract`, `corpus`), owner 21; the vocabulary guard
  keeps its check. 21–8: the change-log guard checks the row's shape (columns, class, undo present);
  Rule-8 keeps class, authorization and the row's content. 21–9: this record; the records guard checks a
  record's form (attack table, Disposition line), Rule-9 its substance. 21–10: framed in the plan.
  21–11: one sentence in p1 points here; package vs instance, install and release stay Rule-11's; the
  runner still owns no semantics (S4). 21–12: the test mapping gains one branch; Rule-12 keeps "code
  carries a check". 21–13: no import; stdlib. 21–14: the manifest guard scans `guards/` too; no new
  World row. 21–15: the plans guard reads the plan file's header; Rule-15 keeps the phases. 21–16: the
  row guard keeps the transition table and the fence; the store is untouched. 21–17: the entities
  projector builds its cards from the guards' `describe` (p1 satisfied by construction); rendering stays
  Rule-17's. 21–18: the ops-script guard moves; Rule-18 keeps its properties. 21–19: the run-book guard
  holds the parser, the runner imports it; the event guard holds the store's shape and the append-only
  fence; Rule-19 keeps the rule. 21–20: the register lists guard-owned kinds by `guard:<corpus>/<entity>.py`;
  kinds 12 and 13 are the frame guard's; Rule-20 keeps the register. Coherent, orthogonal.

## Rule-6: three terms added (`guard`, `guard contract`, `corpus`), owner 21.

Disposition: see ledger #151.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 9 | A second guard root (`crafts/<craft>/guards/`) breaks "one tree, one root" (attack 3's survivor). | Refuted | The *core* stays one tree; a Tended craft is its own tree with its own root (Rule-11, #154). The registry is one list over two roots, labelled `<corpus>/<entity>` and `<craft>/<entity>`; `check --list` prints each entry's root. |
| 10 | A craft guard's `CORPUS` cannot equal its directory (`guards/`), so property 3 fails by construction. | Confirmed | Property 3 amended: for a craft guard `CORPUS` is a zone name in `containment.ZONES` (the store's zone); the runner refuses any other (`test_craft_guard_with_a_bad_corpus_fails_the_run`). |
| 11 | Importers that `load_guard("workstation", …)` break on a system without the craft. | Confirmed | `load_guard` falls back to a craft guard by `CORPUS`; `find_guard` returns `None`; `references.py`, `rows.py` and the events surface skip with a line (Rule-20 property 4 extended from "store absent" to "guard absent"); scratch-install tests with and without the craft. |

Pairwise: 21–1 (craft zone holds the craft's guards), 21–11 (two roots named in Enforcement), 21–12 (mapping gains the craft branch; each craft's tests one suite), 21–20 (kind 11 extracts `crafts/…` tokens; core-only installs skip them), 21–6 (`guard`, `corpus` definitions widened; no new term). Coherent, orthogonal.
## Amendment — d-work #156 (2026-09-14, the craft guard and one contract definition)
p1's corpus list gains `craft` (the craft guard `dyad/guards/craft/crafts.py`, entity `craft`, checks the entities
stored under `crafts/*` — plan #156 precondition P1 found the zone declared but the list without it); p3 names the
one contract definition (`dyadlib.CONTRACT`, `dyadlib.contract_problem`) the runner and the craft guard share, so a
Tended craft's guards are checked against the same contract before export and install. Pairwise: 21–11 as in
`rule-11-distribution-structure.md`. Coherent, orthogonal.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
Rule-21 retired; this record travels with its text to `crafts/sysarch/rules/guards.md` (#153 attack 7). Origin commit of
the core copy: 616f506. What the core keeps is the mechanical statement (`dyadlib.CONTRACT`, `dyadlib.contract_problem`,
the runner's discovery) and two kernel sentences — Rule-11 p1's layout sentence, Rule-12 p2's "carries a check" — so a
system without this craft runs the contract and reads Rules 11/12 (plan #160 attack 4). Projectors leave `dyad/scripts/`
for a craft's `projectors/` (p1 amended). Attacks 1–11 hold as written. Disposition: see ledger #160.
