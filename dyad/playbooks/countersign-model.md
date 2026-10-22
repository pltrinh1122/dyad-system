# Play-book: the countersign model (core craft, `dyad-operator`; #381)

The model the d-work framework is checked against: a core schema of eight entities and one attribute that every
countersigning system maps to **by projection** (Part I), and one interaction model — five primitives, eight
imperatives, one lifecycle per mode — that is the same in every mode and every system (Part II). It was
authored here as the Tended craft `crafts/countersign/` (0.1.0 #156, 0.2.0 #152, 0.3.0 #308), projected from the
core's own countersigning spine (`agent-corpus/falsification/core-vs-countersign.md`, #334), and is carried by the
core since #369 (direction (c) of the #330 audit's D-10, carried to its end: `agent-corpus/falsification/countersign-consolidation.md`),
its words adopted rather than coined (Rule-13 property 1). Its records travel with it:
`dyad/falsification/countersign-schema.md` (F1–F7), `countersign-interaction.md` (R1–R15),
`countersign-self-diagnostic.md` (C1–C6, D1–D25).

**Non-normative where the vocabulary carries no term.** This play-book binds nothing by itself: in a dyad system
only the Agent Rules bind, and a Rule that uses one of the model's words cites the vocabulary row for it (Rule-6).
Where a Rule and this model differ, the Rule is what the Agent obeys and the difference is a row of Part II §7.
It is not a procedure and has no run-book of its own: the d-work play-book (`dyad/playbooks/d-work.md`) is the
procedure that realizes Part II's explicit-mode lifecycle, and the audit play-book's self-diagnostic reads I1–I8
as its L4 claims. The projector that maps this system onto Part I and the levels check are code with tests
(`crafts/countersign/projectors/project_countersign.py`, `crafts/countersign/scripts/levels.py`, until C4 of
#369 moves them into `dyad/scripts/`).

## Part I — the Countersign core schema (eight entities, one attribute)
Read by the projector and by any system that projects its own stores onto the core — dyad-system here, dsys by
its own mapping module (plan #156, PR-C). Schema file: `crafts/countersign/templates/countersign-core.json` (JSON
Schema, draft 2020-12; C4 moves it to `dyad/templates/`). Record: `dyad/falsification/countersign-schema.md` (F1–F7).

### Intent
State one core schema of the Countersign Architecture — eight entities and one attribute — that
every Countersign system maps to **by projection**, keeping its own entities as a profile outside
the core.

### 1. The core (eight entities)
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

What a JSON Schema cannot say, a projection must still hold (the projector's `check`; the projector is `crafts/countersign/projectors/project_countersign.py` until C4 of #369 moves it to `dyad/scripts/`):
1. every `id` unique in the document, every reference resolves to an instance of the named entity;
2. a countersignature's `signer` is a `human` party; a proposal's `author` is an `agent` party;
3. an act's `processor` has the kind its mode requires (below);
4. an escalation opens an `explicit` act, or none.

### 2. Mode
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

### 3. The mapping contract (F1–F7)
What a system must map, and how each known system does. Survived and refuted as recorded in
`dyad/falsification/countersign-schema.md`; this table is the survivor's contract.

| # | contract | dyad-system | dsys |
|---|---|---|---|
| F1 | **The spine** maps without loss: Act → Proposal → Countersignature → Event → Escalation | d-work row → Act; plan file and every other answered question → Proposal; each `disposed` entry, its words from the provenance record → Countersignature; run-book event → Event; intake origin or incident → Escalation | DecisionRecord / HarnessRun → Act; draft / CTA → Proposal; Disposition → Countersignature (CTA yes / no / counter → yes / no / amend); AutomatonEvent → Event; Disclosure → Escalation |
| F2 | **Mandate and Release** have instances, even without a record type | the preference `ledger-pr-merge: agent` → Mandate; release tags → Release; neither has a record type (preference prose, git tags) | `set_standing` Dispositions → Mandate; PromotionRecord / AutomatonRelease → Release |
| F3 | **Mode and processor** are derived by a stated rule where no field stores them | every act `mode=explicit`, `processor=agent` (D1, below) | the entity type decides: AutomatonRun → automatic, executor; HarnessRun → explicit, or implicit when it runs under a standing disposition |
| F4 | **Vocabulary**: no core field takes a system's word in a different sense | no core term renamed; #142 §2 collisions resolved by namespace (the glossary below) | `DispositionMode` maps to `basis` / kind, never to `mode`; renamed at the mapping boundary only, not in dsys's model |
| F5 | **Extensions** stay outside the core, as a profile | zone, craft, presence file, plan gate, evidence block: profile only | Principal, Hat, R, Fleet, CoS Directive, GateCheck, Application, LocalVeto, Claim, IFF gates: profile only |
| F6 | **Timing** is an attribute, not a structure | guards block before the transaction: `Check.timing = before` | the referee judges after: `Check.timing = after` |
| F7 | **Representation**: projection, never storage migration | markdown `key: value` stores → the projector here | pydantic `SystemState` → its own mapping module, validated against a pinned copy of the schema file (version and sha256 recorded) |

### 4. Derivation rules (dyad-system)
The projector applies exactly these (D1–D7 here, D8 in Part II §3); a change to one is a change to this play-book and the projector's test.
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
- **D8 — initiations.** Owned by Part II (I6): each act's initiation is derived into its
  `profile.initiation`, never into a core field (the core has no Initiation entity yet).

### When
- A system maps its stores onto the core: it states its own F1–F7 column and derivation rules.
- The schema file or a derivation rule changes: the projector, its test and this play-book change in the
  same d-work, and the core's `VERSION` moves (the document's `schema_version` follows it; the test checks).
- A copy of the schema file is pinned elsewhere (dsys): the copy records the version and sha256 of
  this file, and its own check fails on a mismatch.

### Inference, stated
Whether a derivation is faithful — that a `<system>-<id>` ref was an intake, that a plan file is the
question a `Y plan` answered — is inference. The projector's test checks shape, references, the
human signer, the mode–processor rule and determinism, on a fixture and on the live instance.

## Part II — the Countersign Interaction Model
Read by the projector (`interaction`: I6; `check`: I1 and I7), by the command adapters, and by every system that
adopts the model — dyad-system through its Agent Rules, dsys through its own mapping module, countersign-system
natively. It states the model a system's interaction is *checked against*; it binds no system's agent by itself —
in dyad-system only its Agent Rules do, and §7 lists where they still differ. Record:
`dyad/falsification/countersign-interaction.md` (R1–R15). Source: plan #152 revision 2 §1–§3 and §6.

### Intent
State one interaction model between the human and the system — five primitives, eight imperatives, one
lifecycle per mode — that is the same in explicit, implicit and automatic mode (Part I §2) and the same in
every Countersign system, so that a system's own words for asking and answering map onto it without loss.

### 1. Five primitives
The same in every mode and every system. Each is an entity or an attribute of the core (Part I §1), or a
derived profile field where the core has none yet (Initiation, D8 below).

| primitive | who → who | carries | asks? |
|---|---|---|---|
| **Initiation** | human → system (*prompt*); registered source → system (*signal*); executor (*release trigger*) | the originating words or payload, kept verbatim | — |
| **Countersign proposal** | agent → human | one path, its strongest counter, a reconciliation (dyad-system Rule-10; dsys's "DFD turn") | exactly one question, the last line |
| **Countersignature** | human → system | answer ∈ {`yes`, `no`, `amend` + text}; basis ∈ {`per-act`, `mandate`, `release`}; the verbatim text; bound to a head or hash | — |
| **Countersign report** | agent or executor → human | evidence: an evidence block, event ids, counts | nothing — a report never asks |
| **Escalation** | system → human | what was unsigned or unhandled, and why | becomes a countersign proposal, in explicit mode |

A report that surfaces something unsigned does not ask; it raises an escalation, which does (R5).

### 2. The answer grammar
Three answers, one sense in every system. A system's own words map onto them at its boundary; no system's
words are renamed in its own store (Part I F4).

| answer | dyad-system (Rule-3) | dsys (CTA response) | meaning |
|---|---|---|---|
| `yes` | a bare `Y` | `yes` | the proposal is countersigned as asked |
| `no` | a bare `N`, or any response that is not a disposal | `no` | nothing is authorized (I8) |
| `amend` | `N` with text: today a new row linked to the refused one (de facto; §7) | `counter` | a linked re-entry: the proposal is refused *and* its revision is asked for in the same words |
| — | `Y` with text | — | a `yes`, plus a new Initiation (a prompt) carried by the same message |

dsys's five disposition kinds (its `DispositionMode` values) are *bases and occasions*,
never answers (#156 F4): `set_standing` is a countersignature whose basis is `mandate`; the others are
`per-act`. The answer stays one of three (R2).

### 3. Eight imperatives (I1–I8)
Binding in all three modes. "Checked" names the mechanism in the projector; everything else is inference, stated.

| # | imperative | source | checked |
|---|---|---|---|
| **I1** | **Only a human countersigns.** Proposer ≠ disposer. | dyad-system Rule-2; dsys I-2 | **yes** — `check()`: a countersignature's signer is a `human` party, a proposal's author an `agent` party |
| **I2** | **One question per reply, the last line.** The answer grammar is §2's. | Rule-3 Scope, Rule-10 Form; dsys E3 `counter` | inference (a question lives in the conversation, not in a store) |
| **I3** | **Falsify before proposing.** | Rule-9; dsys playbook gates | inference; the record's existence is the evidence (`/falsify` produces one) |
| **I4** | **Detect, don't dispose.** Challenge intent, surface bare claims, never overrule. | dyad-system frame | inference |
| **I5** | **Words kept verbatim.** Every prompt and every countersignature is stored as given. | Rule-7; dsys DecisionRecord | partly — the projector takes a countersignature's text from the provenance record when its count matches the row (D3), and marks `text_source: ledger` when not; the fidelity of a transcription is inference |
| **I6** | **No self-initiation.** An act starts only from a prompt, a registered signal or a countersigned release. | Rule-3 Scope and Intake; dsys "three keys" (the ambient invents no work) | **yes, as a warning** — `interaction()` over D8 (below) |
| **I7** | **Every act carries its mode and a countersignature reference.** | #153; Part I | **yes** — the schema requires `mode` (one of three) on every act, and `check()` the processor kind the mode requires and that every countersignature's subject resolves. An act still awaiting its first answer has no countersignature, by I8: that is not a finding |
| **I8** | **Silence is not consent.** An unanswered question authorizes nothing. | Rule-3 ("any other response"); dsys E5 | inference; the projector derives no countersignature from an absent answer (D3) |

#### I6's derivation (D8, dyad-system)
dyad-system stores no Initiation entity. The projector derives one per act into `profile.initiation`, trying in
order:
1. a `prompt` entry of the act's provenance record (Rule-7) → kind `prompt`, source `provenance`;
2. an intake origin `<system>-<id>` in the row's refs (Rule-3 Intake; the D7 heuristic) → kind `signal`, source
   `intake`;
3. a first disposition whose first word is `backlog`, `intake` or `opened` (a row opened by the Operator's own
   disposition, Rule-3) → kind `prompt`, source `opening-disposition`.

None found → `kind: null` and `missing` names what was looked for ("no provenance record", "no prompt entry in the
provenance record"). A run-book act (D6) is `underivable`: an event names no d-work, so no store reaches its
initiation; it is counted apart, never as a finding.

**Severity: a warning, never a failure.** `dyad project countersign` prints one `I6` line — `ok` when every
derivable act is initiated, `warn` with the count and the first three ids otherwise — and its exit code stays the
schema check's. The reason is that D8 is a heuristic (a `<system>-<id>` token read as an intake origin): a red
projection is the wrong way to learn what a heuristic only suspects. The gaps that are not heuristic are Rule-7's
already: rows opened before it carry no prompt entry, and the instance names exactly those rows — the ones whose
initiation words were never written — in `<instance>/provenance_legacy.local.txt`; any other row without its
record fails Rule-7's own check at the push that creates it (core d-work #191). A failing I6 would only repeat
that failure. What a warning names is a candidate for the Operator, never a verdict: a row opened by the agent's
own finding (a backlog row with an empty `disposed`) is exactly what I6 forbids, and the warning makes it visible.

### 4. Lifecycles, one per mode, built only from the primitives
- **explicit:** Initiation (prompt) → countersign proposal (the plan) → countersignature → execute → countersign
  report + countersign proposal (done) → countersignature.
- **implicit:** Initiation (signal) → is it covered by a mandate? If yes: execute within the mandate's scope, then a
  countersign report. If no: escalation → explicit.
- **automatic:** a countersigned release → the executor runs on its trigger (Initiation: release trigger) →
  countersign events. An unhandled trigger: escalation → explicit.

The mode-specific parts are only *which basis* the countersignature has and *who* processes; both are
attributes of the act (#153), so one model spans the three (R1).

### 5. Preferences in the model
A preference is a standing countersignature, of one of two kinds:
- a **form preference** shapes how countersign proposals and reports look, and authorizes nothing;
- an **authority preference** is a mandate: it countersigns in advance one class of act.

dyad-system's preferences, classified (the four rows after `import-support` close #330 D-4):

| preference | kind | note |
|---|---|---|
| `concise-mode` | form | one report or proposal per prompt |
| `batch-disposition-mode` | form | several questions folded into one; still one question per reply (I2) |
| `merge-disposition` | form | the done countersignature also covers the named merges |
| `delegation` | form | who drafts |
| `ledger-pr-merge` | **authority → mandate** | already a standing countersignature; the projector emits it as `mandate-ledger-pr-merge` (D4) |
| `cli-pattern` | not interaction | command-line form |
| `import-licenses` | not interaction | import criteria |
| `import-support` | not interaction | import criteria |
| `accretion` | **authority → mandate** | `implicit`: a plan-`Y` over a stated mandate scope countersigns every row the scope names (Rule-3 Scope, #290); the mandate the projector should emit per such plan is #330 D-5 |
| `dwork-trace` | form | whether the completion report carries the d-work trace |
| `host-path` | not interaction | where the host records live (Rule-1) |
| `host-zone` | not interaction | the zone of that row (Rule-1) |

A new preference is classified here when it is added: an authority preference that is not projected as a mandate
is an I7 gap (its covered acts would carry no countersignature reference).

### 6. Command adapters
A slash command is an **adapter** that invokes a procedure, never the procedure (#115's survivor: "the adapter,
never the artifact"). The procedure stays a play-book, a run-book or a Rule, versioned with its craft and working
under any kernel; the command is one kernel's way to *offer* it. Templates: `crafts/countersign/templates/commands/` (C4 of #369 moves them to `dyad/templates/commands/`).

| command | invokes | origin |
|---|---|---|
| `/falsify {claim\|path}` | Rule-9's form: attacks, results, survivors, a record | replaces dsys's `eval-meta`, `eval-pb`, `eval-rb`, `eval-sc` — one procedure, four target kinds |
| `/pb-craft` | `dyad/playbooks/craft-instantiation.md` and its run-book `dyad/runbooks/craft.md` | the `/pb-<playbook>` pattern (dsys's `pb-decide`, `pb-extend`) |
| `/pb-harden` | `dyad/playbooks/incident-hardening.md` and its run-book `dyad/runbooks/incident-hardening.md` | same pattern |
| `/pb-<playbook>` | any play-book: `pb-playbook-template.md` | same pattern |
| `/sc-author` | — | **deferred**: meta-authoring, needed once commands multiply |

Every adapter: (a) reads the procedure's file before acting and follows it, never a paraphrase in the command;
(b) is itself an Initiation — invoking it is a prompt, so it opens that system's unit of work and proposes
before it mutates; (c) never answers its own question: it ends with one question, the last line (I1, I2).
No dsys text is copied (dsys has no licence); the pattern is cited by name only (R6).

Installing: copy the command templates into the system's `.claude/commands/`. In a dyad-governed tree
`.claude/` must first be claimed by a zone (plan #152 PR-1, `("infra", ".claude/*")`); until then a committed
command is an unclassified path, which Rule-1 forbids (R4).

### 7. Adoption: refactors each system still needs
Listed, not authorized here: each is its own unit of work in its own system, because each changes a Rule or a
deployed core (plan #152 §6). The dyad-system rows are read against the corpus at #381 (2026-10-22).

| system | refactor | imperative | state at #381 |
|---|---|---|---|
| dyad-system | Rule-3: name `amend` in the answer grammar (`N` with text = a linked re-entry) | I2 | **done** — Rule-3 Answer grammar (#290) |
| dyad-system | a mandate *record* (the mandate moved from preference prose to a countersigned record) | I7 — needs data, not prose | open — the plan file's mandate scope is prose (#330 D-5) |
| dyad-system | a `mode` field on rows | I7 | **done** — the optional row field `mode` (#290, Rule-16 Store); the projector still derives `explicit` for every act until C4 of #369 (#330 D-1) |
| dyad-system | an initiation recorded for every row (a `prompt` entry, or the intake origin) | I6 — derived (D8) and warned | open — the projector derives it; Rule-7 fails a missing record since #191 |
| dsys-repo | slash-command family `eval-*` → `/falsify`; `pb-*` kept | one adapter per procedure | not this system's |
| dsys-repo | a licence decision | gates any reuse of its playbook texts | not this system's |
| countersign-system | its Rules amended toward this model by its own units of work | hand-over criterion H3 | not this system's |

### When
- An interaction primitive, imperative, answer or lifecycle changes: this play-book, the projector's `interaction` or
  `check` and its test change in the same d-work.
- A preference is added to a system that projects onto the core: it is classified in §5.
- A command adapter is added: its template names the procedure file it reads, and §6 lists it.

### Sources
dyad-system #146 and #147 (the modes and edges), #150 (the countersign), #153 (modes of an act), #156 (the core
schema, F4's answer mapping), #115 (a command is the adapter, never the artifact), #152 revision 2 (this model);
dsys by name only: its decision-record and CTA specification (answers yes / no / counter, disposition kinds),
its "three keys" invariant, its E3 and E5 rules, and its slash commands `pb-decide`, `pb-extend`, `eval-meta`,
`eval-pb`, `eval-rb`, `eval-sc`, `sc-author`.

## Glossary — the model's own terms, outside the Agent vocabulary
The terms below are **model-only** by the reconciliation table (`agent-corpus/falsification/countersign-consolidation.md`,
C2): no Agent Rule uses them, so Rule-6 keeps them out of `dyad/vocabulary/VOCABULARY.md`; they are defined here,
once, for the model's reader. The terms a Rule uses are Agent vocabulary rows (`mandate`, `mode`, `explicit mode`,
`implicit mode`, `escalate edge`, `delegate edge`, `escalation`, `answer grammar`, `amend`, `party`, `mode
lifecycle`, `countersign`, `coded check`, `prose claim`) and the vocabulary wins on divergence. Seven of the
model's words are **aliases** of core terms, recorded on the core row: `act` = `d-work` (by projection), `countersign
proposal` = `proposal`, `countersignature` = `disposition`, `countersign release` = `release`, `countersign event` =
the sysadmin craft's `event` (a run-book event; recorded here because the core never edits a craft's row), `signal` =
`intake`, `countersign report` = the evidence of a `completion reply`.

| term | definition |
|---|---|
| Countersign core | the eight entities — party, act, countersign proposal, countersignature, mandate, countersign release, countersign event, escalation — and the check attribute, as the schema file; logical, reached by projection, never a storage format |
| automatic mode | countersigned beforehand by a countersigned release; a non-inferring executor processes; the dyad realizes no automatic act |
| executor | the non-inferring party that processes automatic acts; the one mode-exclusive sub-system |
| basis | how a countersignature covers its act: `per-act`, `mandate` or `release`; in the dyad, the `(mandate #<id>)` note on a `disposed` entry, derived by the projector |
| codify edge | the mode change explicit or implicit → automatic: a practice becomes a countersigned release |
| check timing | when a check judges its target: `before` (it blocks, as the dyad's guards do) or `after` (it judges); a policy attribute, not a structure |
| system profile | the entities and fields a system keeps outside the core, carried in an instance's `profile` object; never mapped into the core |
| derivation rule | a stated rule by which a projector fills a core field a system does not store (D1–D8) |
| Countersign Interaction Model | Part II: five primitives, the imperatives I1–I8, one mode lifecycle per mode |
| interaction primitive | one of the five kinds of exchange the model is built from: initiation, countersign proposal, countersignature, countersign report, escalation |
| initiation | the origin of an act, kept verbatim: a prompt (human → system), a signal (a registered source → system) or a release trigger; in the dyad an Operator prompt, a relayed prompt, the `Y` that admits an intake, or the mandate's plan-`Y` for an accreted row, each already a core term; derived by the projector (D8) |
| release trigger | the initiation of an automatic act: the occasion on which the executor runs a countersigned release |
| interaction imperative | one of I1–I8, binding in all three modes; in the dyad, Rules 2, 3, 7, 9, 10 and the frame |
| form preference | a standing countersignature that shapes how proposals and reports look and authorizes nothing (`concise-mode`, `batch-disposition-mode`, `merge-disposition`, `delegation`, `dwork-trace`) |
| authority preference | a standing countersignature that authorizes one class of act in advance: a mandate (`ledger-pr-merge`, `accretion`) |
| command adapter | a slash-command file that invokes a procedure (a play-book, a run-book, a Rule's form) by reading it, never the procedure itself (#115) |
| coded check, prose claim, diagnostic level, self-diagnostic | the self-diagnostic's terms: `dyad/playbooks/audit.md`, The self-diagnostic |

