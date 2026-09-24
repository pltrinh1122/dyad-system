# countersign — the Countersign Architecture's core schema (Tended craft, `crafts/countersign/`, zone `craft`)

The one schema every Countersign system maps to: eight entities (party, act, proposal,
countersignature, mandate, release, event, escalation) and one attribute (check timing), with
#153's definition of **mode** — explicit, implicit, automatic: modes of an act, never sub-systems —
and the mapping contract F1–F7 that both dyad-system and dsys satisfy **by projection**, each keeping
its own entities as a profile outside the core (plan `agent-corpus/d-work/plans/156.md`). Version:
`VERSION` (0.1.0), equal to the schema document's `schema_version`.

Authored here first, in dyad-system, per the craft-instantiation play-book's D3' ("authored here
first, extracted later"). **Not bundled with the core** (no `BUNDLED_WITH_CORE` declaration): a
core-only install (`dyad build|install`) does not carry it, so nothing a core-only system runs
changes. It is the craft #152 planned to seed into `pltrinh1122/countersign-system`; that system
receives it by `dyad craft export countersign` here and `dyad craft install
countersign-0.1.0.tar.gz` there — the one distribution path (Rule-11 p5), never by hand. dsys pins
a copy of the schema file with its version and sha256 (plan #156, PR-C).

| path | holds |
|------|-------|
| `rules/schema.md` | the one Tended rule: the core (§1), mode (§2), the mapping contract F1–F7 for dyad-system and dsys (§3), dyad-system's derivation rules D1–D7 (§4) |
| `vocabulary/CRAFT.md` | the craft's terms (`countersign:<term>`), prefixed where the word is already an Agent or another craft's term; the #142 §2 collisions resolved by namespace |
| `templates/countersign-core.json` | the core as a JSON Schema (draft 2020-12). Under `templates/`, not `schema/`: `schema/` is not an allowed craft child (syseng `naming.md`), and a template is what a projecting system copies and pins |
| `projectors/project_countersign.py` | projects this system's rows, plans, provenance, preferences, release tags, run-book events and incidents onto the core; stdlib only; its `validate` is the JSON Schema subset the schema file uses, `check` adds references, the human signer and the mode–processor rule; declares `INVARIANTS` |
| `tests/test_project_countersign.py` | a fixture system (with and without git), the validator's rejections, determinism, and a live run: every instance validates, every mode is one of three, every signer human |
| `falsification/schema.md` | F1–F7 ("maps cleanly"), verdict and survivor |

## Running the projector
- `dyad/bin/dyad project countersign` (or `countersign/countersign`) writes
  `<instance>/projections/countersign.json` — generated, never tracked — and prints one line of
  per-entity counts; it exits 1 when the document does not check.
- `dyad project --list` shows `countersign/countersign <path>`.
- Tests: `dyad check` runs `crafts/countersign/tests/` as its own suite (Rule-12's `check_rule_12`).

Output is a JSON document rather than an HTML page: it is a data projection other systems read and
validate, not a viewing surface; it keeps every other discipline of the syseng `determinism.md`
(generated, never committed, byte-identical — sorted keys, arrays sorted by id, no clock).

## Not in this craft
Stored `mode`/`processor` fields, a Mandate record type, and any rename of either system's model
(plan #156, not in scope). Nothing under this tree names a host.
