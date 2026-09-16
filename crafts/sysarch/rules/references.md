# References (sysarch craft, Tended rule)

Read by Rule-20's kernel (`dyad/rules/RULE-20-referential-integrity.md`): the core Rule binds
*that* every reference from one entity instance to another is resolved mechanically by one
registered resolver per kind, and the severity of a miss (an unresolved reference fails, a `world`
kind warns once, an absent or empty store skips). This rule is the *design* of the register that
sentence reads. Text moved from Rule-20 properties 1, 2, 3, 5 and 6 and conditions 2 and 4 by
d-work #160; a Tended rule — any form, no Rule-4 block, no sweep. Terms (`reference`, `resolver`):
`crafts/sysarch/vocabulary/CRAFT.md`. Guard (core): `dyad/guards/agent/references.py`, the
register `references.REFERENCES` and its tests; the register stays core code — its rows bind
Python callables, and a data file naming them by string would add a lookup table and no check
(#160 D6).

## Properties
1. **One register.** `references.REFERENCES` (data, in the reference guard) lists every reference
   kind: source entity and field, extractor, target entity, resolver. A kind absent from the
   register is checked by nobody, and the next audit that bridges it by inference names the gap.
2. **One resolver per kind.** Each entry names exactly one resolver: a function of the reference
   guard, an existing guard of another Rule (`guard:<corpus>/<entity>.py`, listed and not re-run),
   or `world` (unresolvable). Two resolvers for one kind is a breach.
3. **Existence, nothing more.** A resolver decides that the target instance exists — a row file, a
   Rule file, a record file, a path in the working tree (a token with `<…>` or `*` is a glob needing
   one match; a generated path is accepted), a commit, a change-log row keyed by d-work and H-row.
   State, date, wording and whether the right target was meant stay with the owning Rule and stay
   inference. Existence needs no cutoff: instances older than any later convention still exist; a
   field segment annotated `(pre-ledger)` names no instance and is not a reference.
4. **Surface and guard share the data.** The entities projector's relations (`projection.md`) are
   `REFERENCES` filtered to the entities on the surface; the projector holds no relation table of
   its own, so what the Operator sees drawn is what the guard resolved.
5. **Kernel only.** Stdlib Python and `git`; no World row (`manifest.md`).
6. **Craft-contributed rows (design).** The core register today holds kinds whose source or target
   is a sysadmin entity (`changelog.*`, `ops.*`, `event.*`, `incident.*`), listed with the craft
   guard that parses them and skipped with a line when no installed craft provides it (#155). The
   design that fits crafts is that *each craft guard contributes its own `REFERENCES` rows and the
   core register concatenates them by discovery*, so a craft's kinds leave with the craft. Not
   mechanised here: #155 kept the sysadmin kinds in the core register (`GUARD_KINDS`), so the
   mechanism is a backlog row, not this d-work's (plan #160 attack 10).

## Leaves
Entities that are neither a source nor a target of any register row, by design: `zone` (the
zone table is read by paths, not by references), `reference` (the register itself),
`presence` (Rule-16, d-work #185: a session's own claim of what it is working; its rows field
names ids by design without a resolver — a row gone stale in another session's file is expected,
never an error, so it is read, not mechanically checked against the ledger). The
craft guard (`registry.py`) checks that every core guard's `ENTITY` occurs in the register as a
source or target or is listed in this section as a leaf in backticks. The craft entity left this
list 2026-09-16 (#196): a new reference kind (`bundle.component->craft`, Rule-11 property 7) makes
it a real target — a craft is still named by its directory and its own `requires:` still checked
at install (`distribution.md`), but it is now also referenced, so the register is where it belongs.

## When
- A new reference kind appears in a store, a template or a Rule: the same d-work adds its register
  entry and resolver, or lists it as unresolvable.
- An entity's parser or store changes (`projection.md`, When): the entries naming it adapt in the
  same d-work.

## Inference, stated
Whether an unresolved kind's inference is right, and whether a resolved reference names the
intended instance, is inference at falsification time.
