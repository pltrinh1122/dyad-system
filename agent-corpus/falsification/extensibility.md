# Falsification record — "dyad-system does not support low-friction extensibility; patching is the most frictionful and least desirable path" (d-work #101)

**Claim (Operator, 2026-09-20, refusing #100's plan):** architecturally, dyad-system does not
support low-friction extensibility, where patching is the most frictionful and least desirable
path. Context: #100 proposed four fixes (D1–D4) to core, sysarch and syseng, each triggered by a
craft authored outside this repo (workstation's `automaton`, `dsys-repo`'s `cos`) needing to write
craft-varying data into a table this repo owns.

## Evidence

**Discovery mechanisms present** (a craft extends without touching this repo, `dyadlib.craft_dirs`
the common primitive): guards (`crafts/<c>/guards/*.py`, contract-checked, `<craft>/<entity>`
label), tests (`crafts/<c>/tests/`, Rule-12 discovery), projectors
(`crafts/<c>/projectors/project_*.py`), `invariants_contrib.txt` (`exempt:` lines — widening by
construction), `naming_contrib.txt` (merged, though see D4 below), Tended rules and craft
vocabulary (`<craft>:term`), templates + `seeds:`, `requires:`, `package_rules.local.txt` (the
installing *instance's* overlay, #192). Nine mechanisms, all by discovery, none hand-listing a
craft name.

**Patch-only points hit in the last four days**, each answered when it arose by editing this
repo's own tracked content rather than a craft's:

| need | owner constant / table | patch that answered it |
|---|---|---|
| a store for a craft's own instance data | `containment.ZONES` (data, core; no craft-declared addition) | none yet — a craft must overload `workstation` or `craft` |
| a World dependency of a craft's own code | `INFRASTRUCTURE.md` (core content, no craft rows; `manifest.py` scans only `dyad/`) | backlog #51 — workstation's `automaton` calls the Anthropic API over `urllib` to dodge the undeclared-import guard rather than close the gap |
| a reference kind from a craft's own entity | `references.REFERENCES`, `CRAFT_ENTITIES` (core; sysadmin's kinds hard-listed) | #22 (`row.refs->craft`), #196 (`bundle.component->craft`) — both core patches; `references.md` p6 already *names* "craft-contributed rows" as the fitting design and states it was never built (#155, #160 attack 10) |
| a surface name another craft already uses | `package.projectors()`'s bare key; the sysarch guard re-derives the same refusal independently | #99 / #100 D3 |
| a naming pattern wider than a native one | `naming.check_kinds`, conjunctive over the merged list | #100 D4 — 29 `allow:` lines across three crafts stand in for 3 `kind:` rows that don't work |
| a version that says "built from a release, not a release" | one strict `SEMVER` in two guards | #100 D2 |
| a `requires:` floor that is actually true | hand-typed, never checked against the named tag | #100 D1 |
| tests/registries that enumerate installed crafts by name | `test_package.KNOWN_CRAFTS` (fixed, #46) and, unfixed a second time, `test_project_entities.ENTITIES` | #46 (derived from discovery), #98 (workstation#247 — the identical bug, two files over, four years — days — later) |
| a ledger state or transition | `dyadlib.STATES`/`TRANSITIONS` | #37 — a core patch, examined below and found **not** a defect |
| a craft's own CLI noun | `package.main`'s hard-coded dispatch | none — no installed craft has asked for one yet |

Eight rows are craft-varying data blocked by a core-owned table; one (`STATES`) is examined
separately since it looks the same shape and is not.

## Falsification

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | The system *is* extensible: nine discovery mechanisms exist, and a craft install writes only its own root (Rule-11 p2). | Refuted as a general claim about the system, confirmed for the crafts already in it | Discovery covers exactly what sysarch, syseng and sysadmin needed when they were *extracted* from this repo (#155/#160/#162) — the core's constants already fit them by construction. Every patch-only row was hit by a craft authored *elsewhere* (`lan-git`, `surfacer`, `automaton`, `cos`) within days of it existing. The mechanisms are real; they were built by extraction, not by extension, and stop where extraction stopped. |
| 2 | "Most frictionful" is contingent — this repo turns an intake into a merged fix inside one session (#39–#46 in under a day). | Survives, scoped | Fast patching is still patching: it requires this repo's Operator, a release, and a downstream reinstall — and the reinstall itself can break (D1). The friction that matters is not turnaround time; it is *who must act*. Today, only this repo can. |
| 3 | Some points are correctly closed and should stay closed — `STATES`/`TRANSITIONS` (#37 added `archived`), Agent-process Rules (Rule-4). | Confirmed | `archived` is a d-work *lifecycle* state, added on an Operator disposition to the process every dyad instance shares (Rule-3's own ledger) — not a craft's data. The claim holds only for a table holding **craft-varying** data: a zone, a dependency row, a reference kind, a surface, a naming shape, a version form, a floor, a command, a craft-name enumeration. It does not hold for the dyad's own process state, and #37 was rightly a core change, not a symptom. |
| 4 | The D-shape recurs because each fix was a one-off: #46 derived `KNOWN_CRAFTS` from discovery; #98 is the identical hard-code, two files over, found four days later. | Confirmed | A patch fixes the instance and leaves the class. #46's fix was never generalised past the one file it touched. |
| 5 | The cross-cutting note in #100 (D3/D4 are "extension points the design anticipates and does not complete") generalises further: `references.md` p6 names craft-contributed rows as *design*, never built; `requires:` is *checked for presence*, never *verified for truth*. | Confirmed | The architecture already names three of these gaps in its own text and has not built the mechanism. That is the most damning finding and the most hopeful one: the design is not wrong, it is unfinished in specific, named places. |
| 6 | A general contribution mechanism is over-engineering; the existing `.local` instance overlay (#192) is enough. | Survives, scoped | `.local` answers what the *installing instance* needs to add (its own zone paths, its own allow lines) — it is deleted if the craft is removed and never travels with the craft. A craft's own data must ship *with the craft* so import/export (Rule-11 p5) carries it; `references.md` p6 says this in as many words. Both are needed; conflating them is what produced the 29-`allow`-line cost in D4. |

**Verdict on the claim, scoped:** true and precise where it bites — a table that holds
craft-varying data and has no craft-declared discovery path is patch-only, and every such table
found in four days of downstream use was hit. False where it doesn't — the dyad's own process
state (`STATES`, Agent Rules) is correctly closed, and calling that a symptom of the same disease
would be the wrong lesson to take from this record.

## The remedy is not one shape ten times — it is three shapes, sized to what each gap actually is

**(a) Genuine "a craft ships its own row into a core-owned table," the same shape three times** —
discovery (`dyadlib.craft_dirs`), a craft-owned file beside its guard, merged by the core check,
reported under the contributing craft's own name on failure (`invariants_contrib.txt`'s existing
pattern, generalised):
- *Zone.* A craft's `MANIFEST.md` gains an optional `instance-zone: <prefix>` line; `containment.py`
  reads every installed craft's `MANIFEST.md` and adds `(<craft>, "<prefix>-corpus/*")` to `ZONES`
  by discovery — no `_contrib.txt`, the manifest already carries craft-level declarations
  (`requires:`, `seeds:`). Closes the "no store for a craft's own instance data" row.
- *World dependency.* `crafts/<craft>/infrastructure_contrib.md`, same six-cell row shape as
  `INFRASTRUCTURE.md`; `manifest.py`'s scan reads the core file plus every installed craft's own,
  and scans `crafts/<c>/` (not just `dyad/`) for the tokens those rows must cover. Closes #51.
- *Reference kind.* A craft guard may export `REFERENCES_CONTRIB` (the same 6-tuple shape as a core
  `REFERENCES` row); `references.py`'s `Corpus` build concatenates every installed craft's, by
  discovery. This is `references.md` p6, built rather than left as design text; it also lets #22's
  `CRAFT_ENTITIES` hard-list retire the same way `KNOWN_CRAFTS` already did (#46).

**(b) Related gaps, each its own shape, not a contribution file** — already designed in #100's
plan, restated here as what they close: surface keying by `craft/surface` with unique-bare-name
resolution (closes D3 / #99); disjunctive `check_kinds` — a path valid when *any* selecting kind
accepts it (closes D4); one `SEMVER` grammar admitting `X.Y.Z+<local>` for a derived, unreleasable
tree (closes D2); a `requires:` floor checked by running the craft's own `INVARIANTS` against the
floor tag's `dyadlib`, not merely present (closes D1).

**(c) Not a new mechanism — propagate the one #46 already built.** `test_project_entities.ENTITIES`
derives from `SYSADMIN`/`LANGIT` flags instead of `G`'s own keys, exactly the bug `KNOWN_CRAFTS` had
before #46. No design work; apply #46's fix a second time. Closes #98.

**(d) Correctly out of scope, named so the record does not get cited to argue for it later.**
`dyadlib.STATES`/`TRANSITIONS` and Agent-process Rules: dyad-process state, not craft data — no
contribution mechanism proposed (attack 3).

**(e) A real gap, not yet needed.** A craft's own CLI noun: no installed craft has asked for one.
Ponytail's own rung 1 (`agent-corpus/audits/2026-09-18-ponytail.md`, adopted `verifiable-code.md`
p7): does this need to exist yet? No. Named, not built.

## Proposed for the Operator's disposition (not enacted by this d-work)
One Rule-11 property, for a fresh plan-`Y` if disposed: *"A core-owned table that holds
craft-varying data accepts a craft-shipped contribution, discovered like a guard and reported
under the contributing craft's own name, so the data leaves when the craft does."* This record
recommends adoption, scoped to categories (a) and (b) above — eight of the ten rows in the
evidence table — with (c) folded into #98's existing backlog row and (d)/(e) explicitly excluded.

Disposition: see ledger #101.
