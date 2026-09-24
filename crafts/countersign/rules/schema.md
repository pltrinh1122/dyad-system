# Countersign core schema (countersign craft, Tended rule)

No core Rule reads it; Tended. Read by this craft's projector (`../projectors/project_countersign.py`)
and by any system that projects its own stores onto the Countersign core — dyad-system here, dsys by
its own mapping module (plan #156, PR-C). A Tended rule: any form, no Rule-4 block, no sweep; it never
binds the dyad's process, only what a projection onto this schema must satisfy. Terms:
`../vocabulary/CRAFT.md`. Schema file: `../templates/countersign-core.json` (JSON Schema, draft
2020-12). Record: `../falsification/schema.md` (F1–F7, the survivor this rule states).

## Intent
State one core schema of the Countersign Architecture — eight entities and one attribute — that
every Countersign system maps to **by projection**, keeping its own entities as a profile outside
the core.

## 1. The core (eight entities)
Logical, not a storage format. A system's stores stay as they are; a projector maps them.

| entity | fields (core) | meaning |
|---|---|---|
| **Party** | `id`, `kind` ∈ {human, agent, executor} | who acts; only a `human` countersigns |
| **Act** | `id`, `title`, `mode` ∈ {explicit, implicit, automatic}, `processor` → Party, `state`, `refs` | one consequential unit of work, in exactly one mode at a time |
| **Proposal** | `id`, `act` → Act, `author` → Party (agent), `body_ref`, `artifact_hash` (nullable) | what is put up for countersignature |
| **Countersignature** | `id`, `subject` → Proposal \| Escalation, `signer` → Party (human), `answer` ∈ {yes, no, amend}, `basis` ∈ {per-act, mandate, release}, `text` (verbatim), `bound_hash` (nullable), `at` | the human act; `basis` is *how* it covers the act |
| **Mandate** | `id`, `scope` (event class, plan template, budget, rights), `countersignature` → Countersignature | a standing countersignature (implicit mode) |
| **Release** | `id`, `definition_ref` (run-book, flow, craft tree), `version`, `hash`, `countersignature` → Countersignature | a countersigned definition an executor runs (automatic mode) |
| **Event** | `id`, `act` → Act, `seq`, `payload`, `at` | an append-only execution record |
| **Escalation** | `id`, `from` → Act (or `ext:<system>-<id>`, an act outside the document), `reason`, `opens` → Act (explicit, nullable) | the unexpected, returned to a human |
| *(attribute)* **Check** | `name`, `timing` ∈ {before, after}, `target` (one of the eight) | a guard or validator; timing is the axis two systems may invert (F6) |

One instance document holds `schema_version`, `system` (the profile name) and one array per entity
(`parties` … `escalations`), plus an optional `checks` array. Every instance may carry a `profile`
object: the projecting system's own fields, outside the core (F5). A reference names another
instance's `id` in the same document; `ext:` is the one form that names something outside it.

What a JSON Schema cannot say, a projection must still hold (the projector's `check`):
1. every `id` unique in the document, every reference resolves to an instance of the named entity;
2. a countersignature's `signer` is a `human` party; a proposal's `author` is an `agent` party;
3. an act's `processor` has the kind its mode requires (below);
4. an escalation opens an `explicit` act, or none.

## 2. Mode
> **Mode** — the way one act obtains its countersignature and who processes it: **explicit**
> (countersigned live by a human; an agent processes), **implicit** (countersigned in advance by a
> standing mandate; an agent processes), **automatic** (countersigned beforehand by a countersigned
> release; a non-inferring executor processes). Every act has exactly one mode at a time and changes
> mode only along an edge: **delegate** (explicit → implicit), **codify** (explicit or implicit →
> automatic), **escalate** (automatic or implicit → explicit). Modes are not sub-systems.
> **Sub-systems** — the agent runtime (explicit and implicit), the **executor** (automatic only; the
> one mode-exclusive sub-system), and the ledger, the guards, the countersign record and the
> intake (all modes).

(Plan #153's survivor, verbatim.) Its checkable consequence is condition 3 above and the
projector's `PROCESSOR_KIND` and `EDGES`, each with its invariant.

## 3. The mapping contract (F1–F7)
What a system must map, and how each known system does. Survived and refuted as recorded in
`../falsification/schema.md`; this table is the survivor's contract.

| # | contract | dyad-system | dsys |
|---|---|---|---|
| F1 | **The spine** maps without loss: Act → Proposal → Countersignature → Event → Escalation | d-work row → Act; plan file and every other answered question → Proposal; each `disposed` entry, its words from the provenance record → Countersignature; run-book event → Event; intake origin or incident → Escalation | DecisionRecord / HarnessRun → Act; draft / CTA → Proposal; Disposition → Countersignature (CTA yes / no / counter → yes / no / amend); AutomatonEvent → Event; Disclosure → Escalation |
| F2 | **Mandate and Release** have instances, even without a record type | the preference `ledger-pr-merge: agent` → Mandate; release tags → Release; neither has a record type (preference prose, git tags) | `set_standing` Dispositions → Mandate; PromotionRecord / AutomatonRelease → Release |
| F3 | **Mode and processor** are derived by a stated rule where no field stores them | every act `mode=explicit`, `processor=agent` (D1, below) | the entity type decides: AutomatonRun → automatic, executor; HarnessRun → explicit, or implicit when it runs under a standing disposition |
| F4 | **Vocabulary**: no core field takes a system's word in a different sense | no core term renamed; #142 §2 collisions resolved by namespace (`../vocabulary/CRAFT.md`) | `DispositionMode` maps to `basis` / kind, never to `mode`; renamed at the mapping boundary only, not in dsys's model |
| F5 | **Extensions** stay outside the core, as a profile | zone, craft, presence file, plan gate, evidence block: profile only | Principal, Hat, R, Fleet, CoS Directive, GateCheck, Application, LocalVeto, Claim, IFF gates: profile only |
| F6 | **Timing** is an attribute, not a structure | guards block before the transaction: `Check.timing = before` | the referee judges after: `Check.timing = after` |
| F7 | **Representation**: projection, never storage migration | markdown `key: value` stores → the projector here | pydantic `SystemState` → its own mapping module, validated against a pinned copy of the schema file (version and sha256 recorded) |

## 4. Derivation rules (dyad-system)
The projector applies exactly these; a change to one is a change to this rule and its test.
- **D1 — acts.** Every d-work row is an Act: `mode = explicit`, `processor = agent`. dyad-system has
  no implicit or automatic act by construction (F3).
- **D2 — proposals.** A row's plan file is the proposal `proposal-<id>-plan` (`body_ref` its path,
  `artifact_hash` its sha256). Every other question a disposition answers is a proposal named by the
  entry's first word (`done`, `open`, `intake`, `backlog`, …; `other` when there is none), authored
  by the agent, with no body in the store (the question lived in the conversation).
- **D3 — countersignatures.** Every `disposed` entry of a row is one Countersignature, in order:
  `signer = operator`, `answer` yes for `Y` and no for `N` (`amend` is never derived: text beside a
  disposal opens a new d-work in dyad-system), `basis = per-act`, `at` the entry's date. `text` is
  the verbatim body of the matching disposition entry of the provenance record when that record's
  disposition count equals the row's; otherwise the ledger entry itself, and the profile says
  `text_source: ledger`.
- **D4 — mandate.** The preference `ledger-pr-merge`, when its value is `agent`, is the Mandate
  `mandate-ledger-pr-merge` (event class: merge of a PR whose whole diff is ledger-only). Its
  countersignature is the last `yes` (a `done` one first) of the d-work that introduced the key — the
  oldest commit touching the key in `preferences-corpus/PREFERENCES.md` citing `d-work #N`; none when
  that cannot be resolved (no repository). The acts it covers are not derived: dyad-system records
  their use only in merge-commit messages.
- **D5 — releases.** Every tag `<craft>-vX.Y.Z` or `vX.Y.Z` is a Release: `definition_ref` the
  craft's tree (`dyad` for the core, `crafts/<craft>` otherwise), `BUNDLE.md` for an unprefixed tag,
  except `v0.3.1`, `v0.3.2`, `v0.4.0` (core-only, cut before the bundle existed); `hash` the tagged
  commit. Its countersignature is the first disposition whose text names the tag as a whole token;
  none otherwise — a release question is answered in the conversation and leaves a store record
  only when a row's entry names it.
- **D6 — events.** Every run-book event (`<runbooks>/events/<instance>.jsonl`) is an Event of one
  Act per run-book instance (`act-runbook-<instance>`, D1's mode and processor), `seq` its position
  in the append-only file; no d-work id is recorded on an event, so no row is its act.
- **D7 — escalations.** A row's `refs` token shaped `<system>-<id>` (other than `parent-<id>`) is
  an intake origin (Rule-3 Intake names its origin that way): an Escalation from `ext:<token>`
  opening the row's act. Every incident-log row is an Escalation from its d-work's act (or `ext:`
  when the row is not in this instance), opening none. Both are "where identifiable": a
  `<system>-<id>` token that is a plain cross-reference, not an intake, is read as one — stated, not
  checked.

## When
- A system maps its stores onto the core: it states its own F1–F7 column and derivation rules.
- The schema file or a derivation rule changes: the projector, its test and this rule change in the
  same d-work, and `VERSION` moves (the document's `schema_version` equals it; the test checks).
- A copy of the schema file is pinned elsewhere (dsys): the copy records the version and sha256 of
  this file, and its own check fails on a mismatch.

## Inference, stated
Whether a derivation is faithful — that a `<system>-<id>` ref was an intake, that a plan file is the
question a `Y plan` answered — is inference. The projector's test checks shape, references, the
human signer, the mode–processor rule and determinism, on a fixture and on the live instance.
