# countersign — the Countersign Architecture's core schema and interaction model (Tended craft, `crafts/countersign/`, zone `craft`)

The one schema every Countersign system maps to: eight entities (party, act, proposal,
countersignature, mandate, release, event, escalation) and one attribute (check timing), with
#153's definition of **mode** — explicit, implicit, automatic: modes of an act, never sub-systems —
and the mapping contract F1–F7 that both dyad-system and dsys satisfy **by projection**, each keeping
its own entities as a profile outside the core (plan `agent-corpus/d-work/plans/156.md`). Version:
`VERSION` (0.2.0), equal to the schema document's `schema_version`.

Since 0.2.0 (plan `agent-corpus/d-work/plans/152.md`, revision 2): the **Countersign Interaction Model** —
five primitives (initiation, countersign proposal, countersignature, countersign report, escalation), eight
imperatives I1–I8, one lifecycle per mode, the answer grammar (`yes` / `no` / `amend`) every system's own words map
onto, and preferences classified as form or authority (a mandate) — in `rules/interaction.md`; and **command
adapters**, slash-command templates that invoke a procedure and never are one (#115).

Authored here first, in dyad-system, per the craft-instantiation play-book's D3' ("authored here
first, extracted later"). **Not bundled with the core** (no `BUNDLED_WITH_CORE` declaration): a
core-only install (`dyad build|install`) does not carry it, so nothing a core-only system runs
changes. It is the craft #152 planned to seed into `pltrinh1122/countersign-system`; that system
receives it by `dyad craft export countersign` here and `dyad craft install
countersign-<version>.tar.gz` there — the one distribution path (Rule-11 p5), never by hand. dsys pins
a copy of the schema file with its version and sha256 (plan #156, PR-C); its 0.1.0 pin stays valid for 0.1.0 —
0.2.0 changes only `schema_version`, and re-pinning is dsys's own change.

| path | holds |
|------|-------|
| `rules/schema.md` | the core (§1), mode (§2), the mapping contract F1–F7 for dyad-system and dsys (§3), dyad-system's derivation rules D1–D7 (§4) |
| `rules/interaction.md` | the Countersign Interaction Model: primitives (§1), answer grammar (§2), imperatives I1–I8 and which are checked, with D8 — I6's derivation (§3), lifecycles (§4), preference classes (§5), command adapters (§6), each system's refactors, not yet adopted (§7) |
| `vocabulary/CRAFT.md` | the craft's terms (`countersign:<term>`), prefixed where the word is already an Agent or another craft's term; the #142 §2 collisions resolved by namespace |
| `templates/commands/` | command adapters: `falsify.md` (`/falsify {claim\|path}`, Rule-9's form), `pb-craft.md` and `pb-harden.md` (the two core play-books), `pb-playbook-template.md` (the `/pb-<playbook>` pattern); each reads its procedure's file and ends with one question |
| `templates/countersign-core.json` | the core as a JSON Schema (draft 2020-12). Under `templates/`, not `schema/`: `schema/` is not an allowed craft child (syseng `naming.md`), and a template is what a projecting system copies and pins |
| `projectors/project_countersign.py` | projects this system's rows, plans, provenance, preferences, release tags, run-book events and incidents onto the core; stdlib only; its `validate` is the JSON Schema subset the schema file uses, `check` adds references, the human signer (I1) and the mode–processor rule (I7), `interaction` the I6 warnings over each act's derived initiation (D8); declares `INVARIANTS` |
| `tests/test_project_countersign.py` | a fixture system (with and without git), the validator's rejections, determinism, D8 and the I6 check (an act without initiation flagged), and a live run: every instance validates, every mode is one of three, every signer human |
| `falsification/schema.md` | F1–F7 ("maps cleanly"), verdict and survivor |
| `falsification/interaction.md` | R1–R12 ("one interaction model across the three modes and systems"), verdict and survivor |

## Running the projector
- `dyad/bin/dyad project countersign` (or `countersign/countersign`) writes
  `<instance>/projections/countersign.json` — generated, never tracked — and prints one line of
  per-entity counts and one `I6` line (`ok`, or `warn` with the uninitiated count and the first ids); it exits 1
  when the document does not check, never for an I6 warning.
- `dyad project --list` shows `countersign/countersign <path>`.
- Tests: `dyad check` runs `crafts/countersign/tests/` as its own suite (Rule-12's `check_rule_12`).

Output is a JSON document rather than an HTML page: it is a data projection other systems read and
validate, not a viewing surface; it keeps every other discipline of the syseng `determinism.md`
(generated, never committed, byte-identical — sorted keys, arrays sorted by id, no clock).

## Installing the command adapters
A system that wants the commands copies them into its harness's command directory:

    mkdir -p .claude/commands && cp crafts/countersign/templates/commands/*.md .claude/commands/

and renames `pb-playbook-template.md` to `pb-<name>.md` per play-book it adds (the template says how). Nothing in
this craft writes there: `dyad craft install` writes only `crafts/countersign/` (Rule-11 p2), and host-side files
are the core's only. In a dyad-governed tree, `.claude/` must first belong to a zone — dyad-system's
`containment.py` gains `("infra", ".claude/*")` by a sibling PR (plan #152 PR-1); until then a committed
`.claude/commands/*.md` is an unclassified path, which Rule-1 forbids (`falsification/interaction.md` R4). The
copied files are then that system's own, changed by its own infra-zone PRs.

## Not in this craft
Stored `mode`/`processor` fields, a Mandate record type, a stored Initiation entity, and any rename of either
system's model (plan #156, not in scope); every refactor `rules/interaction.md` §7 lists (not yet adopted); the
`/sc-author` command (deferred). Nothing under this tree names a host.
