# countersign — the Countersign Architecture's core schema and interaction model (Tended craft, `crafts/countersign/`, zone `craft`)

The one schema every Countersign system maps to: eight entities (party, act, proposal,
countersignature, mandate, release, event, escalation) and one attribute (check timing), with
#153's definition of **mode** — explicit, implicit, automatic: modes of an act, never sub-systems —
and the mapping contract F1–F7 that both dyad-system and dsys satisfy **by projection**, each keeping
its own entities as a profile outside the core (plan `agent-corpus/d-work/plans/156.md`). Version:
`VERSION` (0.3.0). `rules/schema.md` When holds it equal to the schema document's `schema_version`, which
moves with it to 0.3.0, as it moved to 0.2.0 with an unchanged schema (`falsification/self-diagnostic.md` D18).

Since 0.2.0 (plan `agent-corpus/d-work/plans/152.md`, revision 2): the **Countersign Interaction Model** —
five primitives (initiation, countersign proposal, countersignature, countersign report, escalation), eight
imperatives I1–I8, one lifecycle per mode, the answer grammar (`yes` / `no` / `amend`) every system's own words map
onto, and preferences classified as form or authority (a mandate) — in `rules/interaction.md`; and **command
adapters**, slash-command templates that invoke a procedure and never are one (#115).

Since 0.3.0 (dyad-system plan `agent-corpus/d-work/plans/308.md`, authored for countersign-system's d-work #3):
the **self-diagnostic** — a system verifies its own integrity in four diagnostic levels, two kinds of check (a
coded check; a prose claim, read against a written attack) at two scopes (unit, system): L1 unit tests, L2
integration tests with the guards and the evidence block, L3 each unit's contract against its invariants and
tests, L4 a fixed list of system claims — the interaction model's I1–I8, the host, coherence, the frame — plus
the instance's own; on the head of `main`, one level at a time, each gating the next, every command read-only, K
units and P samples of inference per run in rotation, the evidence block computed in a clean clone so it can be
re-run; two writes in two zones, the runner's events (host path's zone) and then the record (agent zone) citing
them. `rules/self-diagnostic.md` describes the model and binds no system's agent (countersign-system #4's
survivor); the steps are a run-book template, the unit/integration classification an instance file seeded from a
template and checked for completeness by the craft's script `scripts/levels.py` — run by the run-book's `health`
step, where the classification is used, and not on every push: a script, not a guard
(`falsification/self-diagnostic.md` D20); `/diagnose` is its command adapter. Install copies neither template, and the craft declares no `seeds:` (D25). 0.3.0 also carries `rules/interaction.md` §3's I6 severity as dyad-system
#194 restated it under 0.2.0 — resting on core #191's `<instance>/provenance_legacy.local.txt` — so a system
whose core predates #191 (countersign-system's 0.10.1) receives a reason its own core does not yet hold
(`falsification/self-diagnostic.md` D10).

Authored here first, in dyad-system, per the craft-instantiation play-book's D3' ("authored here
first, extracted later"). **Not bundled with the core** (no `BUNDLED_WITH_CORE` declaration): a
core-only install (`dyad build|install`) does not carry it, so nothing a core-only system runs
changes. It is the craft #152 planned to seed into `pltrinh1122/countersign-system`; that system
receives it by `dyad craft export countersign` here and `dyad craft install
countersign-<version>.tar.gz` there — the one distribution path (Rule-11 p5), never by hand. dsys pins
a copy of the schema file with its version and sha256 (plan #156, PR-C); its 0.1.0 pin stays valid for 0.1.0 —
0.2.0 and 0.3.0 change only `schema_version`, and re-pinning is dsys's own change.

| path | holds |
|------|-------|
| `rules/schema.md` | the core (§1), mode (§2), the mapping contract F1–F7 for dyad-system and dsys (§3), dyad-system's derivation rules D1–D7 (§4) |
| `rules/interaction.md` | the Countersign Interaction Model: primitives (§1), answer grammar (§2), imperatives I1–I8 and which are checked, with D8 — I6's derivation (§3), lifecycles (§4), preference classes (§5), command adapters (§6), each system's refactors, not yet adopted (§7) |
| `vocabulary/CRAFT.md` | the craft's terms (`countersign:<term>`), prefixed where the word is already an Agent or another craft's term; the #142 §2 collisions resolved by namespace |
| `rules/self-diagnostic.md` | the self-diagnostic model, descriptive: two kinds of check, C1–C6 (§1), the four diagnostic levels and each one's pass, L4's claims S1–S11 among them (§2), the gate (§3), budget K and P with the rotation cursor (§4), findings and where the core's Rules already send each (§5), the levels file (§6), the record (§7), the run-book, its two writes and the command (§8) |
| `templates/commands/` | command adapters: `falsify.md` (`/falsify {claim\|path}`, Rule-9's form), `pb-craft.md` and `pb-harden.md` (the two core play-books), `pb-playbook-template.md` (the `/pb-<playbook>` pattern), `diagnose.md` (`/diagnose [level]`, the self-diagnostic); each reads its procedure's file and ends with one question |
| `templates/runbooks/self-diagnostic.md` | the self-diagnostic's run-book template (`# sections: Level 1, Level 2, Level 3, Level 4`), steps run through `dyad runbook run self-diagnostic <step>`, every command read-only, `evidence` in a clean clone of the head; the runner's events are one of the run's two writes, the record — made by the party that ran it and read back by the last step, `record` — the other; seed of `<host>/runbooks/self-diagnostic.md` |
| `templates/self-diagnostic-levels.txt` | the levels file's seed: one `<level> <path>` per test module, `unit` or `integration`; seed of `<host>/self-diagnostic-levels.txt` |
| `templates/countersign-core.json` | the core as a JSON Schema (draft 2020-12). Under `templates/`, not `schema/`: `schema/` is not an allowed craft child (syseng `naming.md`), and a template is what a projecting system copies and pins |
| `scripts/levels.py` | the levels file's check, a script and not a guard (D20): fails on an unclassified test module, an entry naming none, a malformed line or a duplicate path; skips when the file is absent; `levels.py list <unit\|integration>` prints one level's modules and refuses a failing file. Run by the run-book's `health`, `unit` and `integration` steps, never on a push (no runner discovers a script); declares `INVARIANTS` and `TREE_INVARIANTS`, both run by its own command line first (`self_check`) |
| `projectors/project_countersign.py` | projects this system's rows, plans, provenance, preferences, release tags, run-book events and incidents onto the core; stdlib only; its `validate` is the JSON Schema subset the schema file uses, `check` adds references, the human signer (I1) and the mode–processor rule (I7), `interaction` the I6 warnings over each act's derived initiation (D8); declares `INVARIANTS` |
| `tests/test_project_countersign.py` | a fixture system (with and without git), the validator's rejections, determinism, D8 and the I6 check (an act without initiation flagged), and a live run: every instance validates, every mode is one of three, every signer human |
| `tests/test_levels.py` | the levels script on fixture trees in temporary directories, never a system's inventory (the one live read: this craft's own test modules and seed); wherever the craft's suite runs — every push of this repo; on a system that installed the craft unmodified, whose push gate may skip the root, L2's evidence run (dyad-system Rule-12 property 2) — what no runner checks of a script: its pure invariants and the seed invariant, and the seed's form and its lines for this craft's own test modules; and the run-book template's steps, sections, classes and gates, parsed and never run |
| `falsification/schema.md` | F1–F7 ("maps cleanly"), verdict and survivor |
| `falsification/interaction.md` | R1–R12 ("one interaction model across the three modes and systems"), verdict and survivor |
| `falsification/self-diagnostic.md` | C1–C6 (the two kinds of check) and D1–D25 (the diagnostic: plan #3's D1–D14, D15–D20 found while drafting and integrating, D21–D24 in review, D25 after plan #308's revision 2), verdict, departures and survivor |

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

## Installing the self-diagnostic
A system that runs the diagnostic copies the two templates by hand (`<host>` is its host path; the craft declares
no `seeds:`, so `dyad craft check` names neither, `falsification/self-diagnostic.md` D25):

    cp crafts/countersign/templates/self-diagnostic-levels.txt <host>/self-diagnostic-levels.txt
    mkdir -p <host>/runbooks && cp crafts/countersign/templates/runbooks/self-diagnostic.md <host>/runbooks/self-diagnostic.md

then classifies every test module of its tree in the levels file — `scripts/levels.py`, at the run-book's
`health` step, stops every run until it does: it deletes the seed's lines naming modules its own core lacks (the
seed's header names three a core labelled 0.10.1 lacks) and re-observes the level of each module it keeps, since
the seed's levels are the authoring tree's (on a 0.10.1 core five of its `unit` modules start git) — and adds
its own L4 claims to the run-book's instance block (`rules/self-diagnostic.md` §2). Both files are then that
system's own, in its host path's zone, and so is the event store the run-book's steps append to
(`<host>/runbooks/events/self-diagnostic.jsonl`), committed in that zone before the record that cites it. A
system that copies neither runs no diagnostic and nothing reads the levels file, and nothing warns of
it (`falsification/self-diagnostic.md` D25).

## Not in this craft
Stored `mode`/`processor` fields, a Mandate record type, a stored Initiation entity, and any rename of either
system's model (plan #156, not in scope); every refactor `rules/interaction.md` §7 lists (not yet adopted); the
`/sc-author` command (deferred); any system's levels file, run-book or diagnostic record (instance files: seeds,
never copied by install). Nothing under this tree names a host.
