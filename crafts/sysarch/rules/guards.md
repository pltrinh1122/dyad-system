# Guards (sysarch craft, Tended rule)

Read by Rule-12's kernel (`dyad/rules/RULE-12-verifiable-code.md`: code entering a craft carries
its mechanical check) and by Rule-11 property 1 (the guards live under `dyad/guards/<corpus>/`,
one module per entity kind beside its data). Replaces Rule-21 (guard containment, #151; retired by
d-work #160, its text moved here whole) and carries the design half of Rule-12 property 1. A Tended
rule — any form, no Rule-4 block, no sweep. Terms (`guard contract`): `crafts/sysarch/vocabulary/CRAFT.md`;
`guard` and `corpus` stay Agent terms (owner Rule-11 since #160). Skeleton:
`crafts/sysarch/templates/guard.py`. The one contract definition the core enforces is
`dyadlib.CONTRACT` / `dyadlib.contract_problem` (core; the mechanical statement of this rule).

## Intent
Place every entity guard as one contained module in the craft that owns its check — the core craft
under the corpus of the entities it checks, a Tended craft under its own root — apart from every
instance and from the runner, and bind it to one declared contract the runner discovers.

## A check is mechanical wherever it can be
Prefer code over inference wherever a check can be mechanical; what cannot be checked mechanically
stays inference and *says so* in the Rule or craft rule that owns it (Rule-12 property 1, design
half). A guard's docstring names what it checks and what it leaves to inference.

## Properties
1. **One guard per entity, under its corpus.** `dyad/guards/<corpus>/<entity>.py`, `<corpus>` one
   of `agent`, `workstation`, `preferences`, `infra`, `craft` — the Rule-1 zone of the entity's
   store (the craft guard, `dyad/guards/craft/crafts.py`, checks the entities stored under
   `crafts/*`; #156) — or, for a guard a Tended craft owns, `crafts/<craft>/guards/<entity>.py`
   (flat; `CORPUS` names the store's zone; #155). A guard's data file (`<entity>_rules.txt`, …)
   sits beside it. Nothing else lives under a guards directory: the runner (`package.py`), the
   shared library (`dyadlib.py`) and the run-book runner stay in `dyad/scripts/`; projectors live
   under a craft's `projectors/` (`projection.md`).
2. **Apart from instances.** A guard is craft (`distribution.md`): never inside an instance tree
   (`<instance>/`, `workstation-corpus/`, `preferences-corpus/`) and identical across systems.
3. **The guard contract.** A guard module declares `ENTITY` (the entity key the entities surface
   shows), `CORPUS` (equal to its directory under `dyad/guards/`; for a craft guard, a zone name in
   `containment.ZONES`), `FIELDS` (the schema constant, the entity's parsed fields in order),
   `TRANSACTION` (bool), `check_package(root) -> list[str]` (bare lines fail, `warning:` lines
   warn) and, when `TRANSACTION`, `check_transaction(root, base, head) -> list[str]`; it provides
   `describe(root, pkg)` for the entities surface (`templates/entity-card.md` names the fields) and
   may provide `summary(root)`. The contract has one definition, `dyadlib.CONTRACT` /
   `dyadlib.contract_problem`, read by the runner's registry and by the craft guard, which checks a
   Tended craft's guards before export and install (#156). The guard is the entity's parser: a
   projector or another guard imports it (`dyadlib.load_guard`) rather than re-parsing.
4. **A registry, discovered.** The runner's `CHECKS` is derived from the modules found under two
   roots — `dyad/guards/*/*.py` (sorted) then every `crafts/*/guards/*.py` (sorted; names starting
   `_` excluded) — labelled `<corpus>/<entity>` for the core and `<craft>/<entity>` for a craft; a
   module that does not load or lacks the contract is a failing check, never a silent skip.
   `dyadlib.load_guard(corpus, entity)` resolves the core root first, then a craft guard whose
   `CORPUS` matches; `dyadlib.find_guard` returns `None` when no root provides it, so a kind or a
   surface that needs a craft's guard skips with a printed line on a system without that craft
   (#155). The registry is printed with each entry's root (`dyad check --list`), not remembered.
5. **The CLI stays.** Each guard keeps a command line (`python3 dyad/guards/<corpus>/<entity>.py`,
   `python3 crafts/<craft>/guards/<entity>.py`) printing the same result line it printed before
   any move, so hooks and Rule text stay truthful.
6. **Zones.** The core craft is one tree under `dyad/*` (agent zone) and cannot straddle zones;
   the corpus directory names the entity's zone, it does not relocate the code (#151 attack 3). A
   Tended craft's guard is in the craft zone (`crafts/<craft>/`) and declares the zone of its
   entity's store as `CORPUS`.

## When
- A guard is added, moved or renamed: it lands at its property-1 path, its data beside it, its
  test at `dyad/tests/guards/<corpus>/test_<entity>.py` or `crafts/<craft>/tests/guards/test_<entity>.py`
  (the mapping is Rule-12's `check_rule_12`, implementation, `syseng` on #162).
- A new entity kind gains a mechanical check: one guard, one entity, one corpus.
- Every push and PR: `dyad check` discovers the registry and runs every guard's package check;
  `check --guards` adds every transaction guard over `<base>..HEAD`; `check --list` prints it.

## Inference, stated
Whether a guard's `FIELDS` matches its Rule's prose, and whether an entity kind still lacks a guard
(the incident row, #151), is inference, stated in the record.
