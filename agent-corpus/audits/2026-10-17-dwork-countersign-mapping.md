# Audit — 2026-10-17, design, architecture, framework: the d-work framework and the countersign architecture and craft

*d-work #330. Opened 2026-10-17 in the seat `ds-cabinet-cloud-1` on the Operator's prompt ("explain the
relationship between the `d-work` framework in relationship to the `countersign` architecture and craft.
document this mapping as we'll need it in our effort to consolidate and refactor the overall `Dyad System`
design, architecture and framework. First align with me on differences between design, architecture and
framework."), planned on `agent-corpus/d-work/plans/330.md` (plan-`Y` 2026-10-17, which is the alignment on
the three terms; the prompt verbatim in `agent-corpus/d-work/provenance/330.md`). Standing: `main` at
`b5c48ca`, core craft 0.11.0, countersign craft 0.3.0, 319 rows; the d-work play-book
`dyad/playbooks/d-work.md` as amended by #202 (the Done state follows the merge).*

Disposition: see ledger #330 (Rule-2: the Done-`Y` of d-work #330 disposes this record).

**What this is.** A topic audit (`dyad/playbooks/audit.md`: an Operator-prompted review on one subject, which
borrows the standing audit's Conduct and nothing else). It detects and sizes, disposes nothing, changes no
Rule, craft, guard or projector, and opens no row: gaps are *proposed, not opened* (§7). Every claim carries a
path, a row id or an observed output. The companion record is
`agent-corpus/falsification/dwork-countersign-mapping.md` (C1–C3, attacks A1–A12).

## 1. The three terms, as aligned (plan #330, plan-`Y` 2026-10-17)

Each is defined by the question it answers, where this corpus already keeps it, and how it is checked.

| term | answers | where it lives in dyad-system today | checked by |
|---|---|---|---|
| **design** | *why* — the choices made, the alternatives refused, and the reasons | falsification records (Rule-9), plan files (Rule-15), the ADR audits (`2026-10-08-adr-disposition-architecture.md`, `2026-10-15-messaging-architecture.md`), the "design" paragraphs of `crafts/sysarch/rules/` (its README: "the design behind these kernels") | inference only: falsified (Rule-9) and swept (Rule-5), never guarded |
| **architecture** | *what* — the entities, their stores and fields, their relations, the states they carry, the boundaries that contain them | the countersign core schema (`crafts/countersign/rules/schema.md`, `templates/countersign-core.json`); the sysarch craft's rules (`stores.md`, `guards.md`, `references.md`, `projection.md`); `dyadlib.STATES`, `TRANSITIONS`, `INPUTS`; each guard's `FIELDS`; the reference register `references.REFERENCES`; the zone table `containment.ZONES` | mechanically: guards check the shape, projectors draw it, invariants hold it at import, the register resolves it |
| **framework** | *how* — the procedure a party follows to produce and move instances of the architecture: the binding Rules, the play-books and their run-books, the CLI verbs, the forms of question and answer | Rules 3, 7, 15, 16 (and 2, 10 for who answers and how a question is framed); the six play-books under `dyad/playbooks/`; `dyad dwork new|state|retire|trace`, `dyad session touch`; the counter-prompt forms and the answer grammar (Rule-3) | the transaction guards at the moment of each act (the plan gate `prs.py`, the main fence `rows.py`, the provenance check), and inference for conduct |

The three stack without overlapping. Design justifies the architecture; the architecture is what the framework
operates on; the framework produces the instances the architecture describes, and the design records why it could
not have been otherwise. Two things sit beside the three rather than inside them: a **craft** (Rule-11) is a
packaging and versioning unit that may carry all three — its `rules/` hold design and framework, its schema or
`FIELDS` hold architecture, its guards hold the checks; a **system** (dyad-system, countersign-system, dsys) is one
instance of all three under one Operator. Three tests tell the layers apart: a statement that names an alternative
is design; one a projector could draw is architecture; one with a verb a party performs is framework. A sentence
that is two of these at once is a finding for the refactor (§6, D-rows marked *mixed*), not a fault in the
definitions. The corpus already applies two of the three: Rule-5 `## Sets` splits System Requirements from System
Architecture, and the sysarch README splits "the design" from "the kernel".

## 2. The layer table

| layer | the d-work side (core craft `dyad-operator`) | the countersign side (Tended craft `crafts/countersign/`, 0.3.0) | how each is checked |
|---|---|---|---|
| **design** | `dyad/falsification/rules/rule-3-d-work.md` and its neighbours (Rules 2, 7, 15, 16); the plan files of #290, #309; #252 and #302 as ADRs | `falsification/schema.md` (F1–F7), `falsification/interaction.md` (R1–R12), `falsification/self-diagnostic.md` (C1–C6, D1–D25); plans #152, #153, #156 in this instance | inference: attacks, survivors, sweeps |
| **architecture** | five records (row, plan, provenance, presence, trace) with their guards' `FIELDS`; the machine `STATES` × `INPUTS` → `TRANSITIONS`; the register's `row.*`, `plan.*`, `provenance.*`, `trace.*` kinds; the store pattern (`stores.md`) | eight entities (party, act, proposal, countersignature, mandate, release, event, escalation) and one attribute (check timing), with `mode` on every act; the JSON Schema; the projector's `PROCESSOR_KIND`, `EDGES`, `ANSWERS`, `BASES` with their invariants | guards and invariants on the d-work side; `project_countersign.py` `validate` + `check` on the countersign side, its test on a fixture and on the live instance |
| **framework** | Rule-3 (open, plan, authorize, execute, report, close; accretion; the answer grammar; intake; incidents), Rule-7 (words verbatim), Rule-15 (phases), Rule-16 (store and presence), Rule-2 (who ratifies), Rule-10 (how a proposal is framed); the play-books `d-work`, `disposition-digest`, `dwork-trace`, `incident-hardening`, `audit`, `craft-instantiation`; the verbs | the interaction model (`rules/interaction.md`): five primitives, imperatives I1–I8, one lifecycle per mode, the answer grammar, preferences as form or authority, command adapters; the self-diagnostic (`rules/self-diagnostic.md`): four levels, read-only, a countersign report | transaction guards and the plan gate on the d-work side; on the countersign side I1 and I7 by `check()`, I6 as a warning by `interaction()`, the rest inference, stated |
| **packaging** | the core craft, bundled with `sysadmin`; every dyad system has it | a Tended craft, **not bundled** (no `BUNDLED_WITH_CORE`), installed by `dyad craft install`; authored here first, extracted later (D3') | `craft/crafts`, `sysarch/registry` |

**The relation in one sentence.** Countersign is the portable architecture-plus-framework that every Countersign
system maps onto *by projection*, keeping its own entities as a profile (F5, F7); the d-work framework is
dyad-system's concrete framework over dyad-system's own architecture, and it is a Countersign profile because
`crafts/countersign/projectors/project_countersign.py` derives the core from the d-work stores under D1–D8.
Nothing in the d-work stores is stored in the core's shape, and nothing in the core binds the dyad's process: the
craft's rules say so themselves (`schema.md`: "logical, not a storage format"; `interaction.md`: "binds no
system's agent by itself — in dyad-system only its Agent Rules do"). The bridge is one projector and its
derivation rules, and every divergence below is a place where that bridge is thin.

## 3. Architecture → architecture: the d-work records onto the core

Status: **exact** (a field copied as it is), **derived** (a stated rule fills a core field the store lacks),
**stale** (the rule no longer matches the store), **missing** (no rule, or no core entity, exists).

| d-work record · field | core entity · field | derivation | status | note |
|---|---|---|---|---|
| row · `id` | act · `id` (`act-<id>`) | D1 | exact | |
| row · `title` | act · `title` | D1 | exact | |
| row · `state` | act · `state` | D1 | exact, **asymmetric** | the core's `state` is a free string; the six states, the births, `TRANSITIONS` and `INPUTS` have no counterpart in the core: the machine is dyad's architecture, not the core's |
| row · `refs` | act · `refs` | D1 | exact | |
| row · `refs` (`<system>-<id>` token) | escalation · `from` = `ext:<token>`, `opens` → act | D7 | derived | heuristic, stated: a cross-reference shaped like an intake origin reads as one |
| row · `mode` (optional, #290) | act · `mode` | D1 | **stale** | `DERIVED_MODE = "explicit"` for every act (`project_countersign.py:50`, `:122`) although rows carry `mode: implicit` since #290 and `dyadlib.MODES` holds both; the row file and the core field now agree in name and the projector ignores the field |
| — | act · `processor` | D1 | derived | always `agent`: dyad-system has no executor (F3) |
| plan file (`plans/<id>.md`) | proposal · `body_ref`, `artifact_hash` | D2 | exact | the one proposal with a body in the store |
| any other question a disposition answers | proposal (named by the entry's first word) | D2 | derived | the question lived in the conversation; no body |
| row · `disposed` entry | countersignature · `answer` | D3 | derived, **incomplete** | `Y`→`yes`, `N`→`no`; `amend` is "never derived" (`:51`), yet since #290 an `N` with text is `amend` in Rule-3 and is stored as an `N` entry plus a `prompt` entry in the same record, so the shape is derivable |
| row · `disposed` entry `(mandate #<id>)` | countersignature · `basis` | D3 | **stale** | every basis is `per-act`; an accreted row's entry is the mandate's own `Y` and its basis is `mandate` (Rule-3 Ledger, Rule-7 property 4) |
| provenance · `disposition` entry `text` | countersignature · `text` | D3 | exact when counts match (Rule-7 property 5), else the ledger entry with `text_source: ledger` | |
| provenance · `prompt` entry | *profile* `initiation` (kind `prompt`) | D8 | derived | the core has **no Initiation entity**; I6 is checked as a warning over a profile field |
| provenance · `prompt` entry noted `relayed via <session>` | *profile* `initiation` | D8 | derived | the relay note is not read; the vocabulary term `relayed prompt` (#253 R29) has no core counterpart |
| plan · mandate scope (Rule-3 Plan) | mandate · `scope` | — | **missing** | D4 derives one mandate, from the preference `ledger-pr-merge`; a plan's stated mandate scope, the instrument #290 built accretion on, projects to nothing |
| preference `accretion: implicit` | mandate | — | **missing** | `interaction.md` §5 classifies eight preferences; `accretion` and `dwork-trace` are not in the table, though `PREFERENCES.md` says `accretion` "is an authority preference" by that craft's own classification |
| preference `ledger-pr-merge: agent` | mandate · `mandate-ledger-pr-merge` | D4 | derived | its countersignature is found by git archaeology over `PREFERENCES.md` |
| release tags `<craft>-vX.Y.Z`, `vX.Y.Z` | release | D5 | exact | no d-work record holds a release; the tag is the record |
| run-book event (`<runbooks>/events/*.jsonl`) | event | D6 | exact, **unlinked** | an event names no d-work, so no event is any row's act; one synthetic act per run-book instance |
| incident row (`audits/INCIDENTS.md`) | escalation · `from` → act, `opens` none | D7 | derived | |
| presence file | *profile* only | F5 | exact | a leaf in the register too (`references.md` Leaves) |
| trace (`traces/<id>.md`) | — | — | **missing** | the core has no measurement entity; the trace is dyad's alone |
| guards (`before`) | check · `timing` = `before` | F6 | exact | |
| Operator, Agent | party `operator` (human), `agent` (agent) | — | exact | no `executor` party (F3): the automatic mode has no instance here |

Read across: the **spine** maps (F1) and the **stores stay as they are** (F7). What does not map is exactly what
#290 and #309 added to dyad's architecture after the projector was written at 0.2.0: `mode` on rows, mandates
stated per plan, `amend` as a stored shape, and the machine with its inputs. The core is one version behind the
profile it was written for.

## 4. Framework → framework: the inputs and forms onto the primitives

### 4.1 The machine's inputs (`dyadlib.INPUTS`, `dyad/playbooks/d-work.md` §The machine)

| edge | input | primitive | answer · basis | imperative |
|---|---|---|---|---|
| — → open | an Operator prompt | initiation (prompt) | — | I5 (verbatim), I6 (no self-initiation) |
| — → open | the `Y` admitting an intake | initiation (signal) + countersignature | `yes` · `per-act` | I6: the signal is a registered source, the Operator's `Y` admits it |
| — → open | a mandate's plan-`Y` (accreted row) | countersignature, standing | `yes` · `mandate` | I7: the row carries the mandate's id in its entry |
| — → backlog | `Y backlog` | countersignature | `yes` · `per-act` | I1 |
| open → planned | the plan-`Y` | countersignature on the countersign proposal (the plan file) | `yes` · `per-act` | I1, I2 (one question, last), I3 (falsified first) |
| open/planned → blocked | a deferral naming the blocker | countersignature | `yes` (to a deferral) | I1 |
| open/planned → done | the Done-`Y` | countersignature on the done proposal, after the countersign report | `yes` · `per-act`; `merge-disposition: with-done` folds the merges in | I1, I2; the report asks nothing (R5) |
| planned → open | re-planning on a moved base, or the Operator's amend | none, or countersignature `amend` | `amend` | I2 (a linked re-entry), I8 |
| blocked → open | the blocker reaching `done` | none (clerical) | — | — |
| backlog → open | an Operator prompt for it | initiation (prompt) | — | I5, I6 |
| backlog/done → archived | the retirement `Y` over the named set | countersignature over a set | `yes` · `per-act` | I1, I2 (one question over k rows) |
| (no edge) bare `N` | — | countersignature | `no` | I8: nothing authorized |

Every edge into a terminal state is a countersignature and every birth is an initiation or a countersignature:
the two invariants `only-the-operator-closes` and `no-self-initiation` in `dyadlib` are I1 and I6 encoded as
data, which is the one place the core's framework is held mechanically on the d-work side.

### 4.2 The forms

| d-work form (Rule-3, Rule-10) | primitive | note |
|---|---|---|
| the plan reply: path, counter, reconciliation, one `Y/N` last | countersign proposal | I2; Rule-10's form *is* the primitive's definition in `interaction.md` §1 |
| the completion reply: PRs, checks observed, evidence block, host actions, accreted rows, departures, trace preview | countersign report | "a report never asks"; the Done question after it is a proposal (R5) |
| batch forms (`proceed with #a, #b`; `Done with #a, #b`) | one proposal | I2 holds: several items, one question |
| the mandate form (plan with a mandate scope; Done naming the accreted set) | proposal + mandate; report + proposal | a mandate compresses acts, a batch compresses questions (Rule-3 Batch disposition) |
| the retirement form (`archive #a … #k`) | proposal over a set | not a plan or Done batch; never enters the pending queue |
| `Y` / bare `N` / `N` with text | `yes` / `no` / `amend` | adopted by #290 (Rule-3 Answer grammar); silence is not consent (I8) |
| intake (defect with evidence; enhancement with its Operator's words) | signal; escalation when returned | Rule-3 Intake; I6 |
| incident row | escalation | Rule-3 Incidents; D7 |
| the escalate-edge test (`disposition-digest.md`, T1–T5) | the escalate edge (implicit → explicit) | adopted by #290 |
| `dyad check --evidence`, the guards, the suite | the self-diagnostic's L2; the evidence block is its named instrument | `self-diagnostic.md` §2; 0.3.0 |
| falsification records (attack, result, survivor) | prose claims with written attacks (L3, L4) | C2: a claim with no attack is no check |
| the standing audit (`audit.md`) | a countersign report whose findings are escalations | the self-diagnostic's record is the same kind of file, `<instance>/audits/<date>-self-diagnostic.md` |

### 4.3 The lifecycles

| mode (`interaction.md` §4) | d-work realization | status |
|---|---|---|
| explicit: initiation → proposal → countersignature → execute → report + proposal → countersignature | the play-book's lifecycle steps 1–6; Rule-3 whole | exact |
| implicit: signal → covered by a mandate? → execute within scope → report; else escalate → explicit | accretion under a plan's mandate scope (Rule-3 Scope, Plan); the escalate-edge test; the accreted list in the completion evidence | exact since #290, **unprojected** (§3: mandate scope missing) |
| automatic: countersigned release → executor runs on its trigger → events; unhandled → escalate | none: no executor party, no automatic act; run-book events exist but name no act and no release | **absent by design** (F3); the run-book's events are evidence (`sysadmin:event`), not a countersign event stream |

### 4.4 Preferences

| preference | `interaction.md` §5 says | this corpus says | status |
|---|---|---|---|
| `concise-mode`, `batch-disposition-mode`, `merge-disposition`, `delegation` | form | form | exact |
| `ledger-pr-merge` | authority → mandate | authority | exact |
| `accretion` | not listed | authority (`PREFERENCES.md`, by the craft's own §5) | **stale table** |
| `dwork-trace`, `host-path`, `host-zone` | not listed | form / not interaction | **stale table** |
| `cli-pattern`, `import-*` | not interaction | not interaction | exact |

## 5. Design → design: where the two records of *why* agree and where they part

Agree, by construction or by adoption:
- **One human countersigns** — Rule-2's no-self-ratify is I1; the record `rule-2-no-self-ratify.md` and R1 argue it from the same invariant (`bond:no-self-ratify`).
- **Modes are of an act, never sub-systems** (#153's survivor, quoted in `schema.md` §2) — Rule-3 Scope adopts it: an accreted row is a row in implicit mode, not a second ledger.
- **Projection, never migration** (F7) — Rule-11's craft/instance split and Rule-13's "adopt rather than coin" are the same decision from the other side: the stores are instance, the schema is craft, and the words travel without the files.
- **Timing before** (F6) — Rule-14 property 3's kernel-only path and `guards.md`'s "a check is mechanical wherever it can be" are the design behind `Check.timing = before`.
- **Words verbatim** (I5) — Rule-7 and dsys's DecisionRecord reach it independently; the craft's R-record cites both.

Part, and each is a decision for the refactor:
- **Two parties against three kinds.** dyad-system has Operator and Agent; the core has human, agent, executor. The executor is "the one mode-exclusive sub-system" and dyad-system has no automatic mode. The design choice is whether the Dyad System *wants* an automatic mode (a countersigned release an executor runs: a run-book under a release, or CI as the executor) or declares it out of scope; today it is neither chosen nor refused, only absent.
- **The machine against a free `state`.** dyad's architecture carries a state machine with inputs (Rule-16, `INPUTS`); the core carries `state` as a string and its lifecycle as prose. Either the core gains a machine (and `INPUTS` becomes its projection) or the machine stays a profile; `schema.md` F5 would admit the latter, but then "d-work also carries state and is a finite-state machine to complete a countersigned work session" (the Operator's prompt of #296) is a statement about the profile, not the core.
- **Initiation.** The core has no Initiation entity; I6 is derived into a profile field and warned. dyad's provenance record *is* an initiation store (entry 1, a `prompt`, or the mandate's own words). The craft's own §1 marks Initiation "derived profile field where the core has none yet": a 0.4.0 decision.
- **Measurement.** The trace is dyad's alone. Whether a Countersign system owes a measurement of its own attention and time is not a question the core asks; the self-diagnostic (0.3.0) measures correctness, not cost.
- **Two senses of `release`, `run-book`, `event`, `role`, `mode`** — resolved by namespace (`CRAFT.md`, Collisions), which the vocabulary carries as `countersign:<term>`. A consolidation that renames is where these collide again.

## 6. Divergences, each with its smallest fix and its cost

| # | divergence | layer | smallest fix | cost | who disposes |
|---|---|---|---|---|---|
| D-1 | D1 derives `explicit` for every act; rows carry `mode` | architecture (projection) | the projector reads `Row.mode`; `DERIVED_MODE` becomes the default for an absent line; invariant `derived-act-is-explicit-agent` adjusted | small, craft zone, one PR; §7's third refactor row is then *done* | the Operator, one plan-`Y` |
| D-2 | `amend` never derived | architecture (projection) | an `N` entry followed by a `prompt` entry in the same record projects as `amend` | small, craft zone | same |
| D-3 | every countersignature `basis` is `per-act` | architecture (projection) | an entry noted `(mandate #<id>)` projects basis `mandate`, its subject the mandate | small, craft zone | same |
| D-4 | `interaction.md` §5 does not classify `accretion`, `dwork-trace`, `host-path`, `host-zone` | framework (craft rule) | four rows | trivial, craft zone | same |
| D-5 | no mandate *record*; the preference and every plan's mandate scope are prose | architecture (store) | a store `<instance>/d-work/mandates/` or a parsed `mandate scope:` line in the plan file (the plans guard already parses the header) that the projector reads | medium: a guard or a plan-file field, the projector, §7's second refactor | the Operator; touches Rule-3 Plan, so a record and a Rule-5 sweep |
| D-6 | the core has no Initiation entity | architecture (core schema) | either a ninth entity (0.4.0, every system's projector follows) or the profile field kept and I6 stays a warning | medium: a craft version with a schema change, or nothing | the Operator, for the craft's own d-work |
| D-7 | run-book events name no d-work | architecture (store) | an optional `dwork` field on the event (the sysadmin craft's `EVENT_FIELDS`), set by the runner from `DWORK` when present | small-medium: two crafts (sysadmin, countersign) and the core runner | the Operator |
| D-8 | the core's `state` is free; the machine is dyad's | architecture (core schema) | the core gains `states`, `transitions`, `inputs` as data a profile fills, or declares the machine profile-only | large if the core moves, nil if declared | the Operator, with the consolidation's direction (D-10) |
| D-9 | the trace has no core counterpart | design | declare measurement a profile concern, or add a `measure` entity | nil or medium | the Operator |
| D-10 | **the direction of consolidation** | design | (a) **stay a profile by projection** — keep the stores and the Rules, repair D-1…D-4, land D-5 and D-7; two vocabularies forever, one bridge, the cheapest; (b) **adopt the core natively** — rename row→act, plan→proposal, disposition→countersignature, provenance entry→initiation or countersignature text, incident→escalation across every Rule, guard, verb and 319 rows; F7's survivor must be refuted first, Rule-6's master record rewritten, every reference kind re-registered; the most expensive thing this corpus could do; (c) **adopt the core's framework vocabulary while keeping the stores** — the direction #290 already took (mandate, implicit mode, escalate edge, amend adopted by craft name, stores untouched), continued: the remaining §7 rows, the self-diagnostic adopted as the standing audit's form, the core's lifecycle cited by Rule-3 as its own | (a) days; (b) weeks and a release of every craft; (c) days per row, incremental | the Operator; this audit chooses none — **decided 2026-10-21: (c) carried to its end** (plan #369 revision 3, plan-`Y` on revision 10; the record `agent-corpus/falsification/countersign-consolidation.md`, #374) |

Rows D-1 to D-4 are the stale bridge and cost one craft-zone d-work together. D-5 to D-9 are the places where
dyad's architecture outgrew the core, and each is a decision about *which side moves*. D-10 is the only design
decision; everything above it is cheaper once it is made, and (c) is the only option whose first steps are already
in the ledger.

## 7. Gaps elevated for disposition (proposed rows, never opened; Rule-3 Intake shape where a defect)

1. **Repair the bridge** — D-1, D-2, D-3, D-4 as one craft-zone d-work on `crafts/countersign/` (0.3.1): the
   projector reads `mode`, derives `amend` and the mandate basis, the §5 table gains four rows, §7's done rows
   are marked done. Evidence: `project_countersign.py:50-51,122`; `dyadlib.MODES`; Rule-3 Answer grammar.
2. **A mandate record** — D-5: whether the plan file's `mandate scope:` becomes a parsed line (the plans guard's
   `FIELDS` gains it) and the projector emits one mandate per such plan. Touches Rule-3 Plan by one sentence.
3. **Events name their d-work** — D-7: `DWORK` in the environment already parameterizes every core run-book; the
   runner writes it into the event when set.
4. **The core's 0.4.0 questions** — D-6, D-8, D-9: Initiation as an entity; a state machine in the core; a
   measurement entity. The craft's own d-work, after D-10.
5. **The direction** — D-10, as a plan the Operator disposes, with this audit as its evidence. The terms of §1
   become Agent vocabulary when a Rule first uses them (Rule-6), which the direction's plan would do.
6. **Rule-3 citing the countersign lifecycle as its own** — today Rule-3 Scope cites the craft for the mandate
   and the escalate edge, and the play-book cites §4; the explicit lifecycle itself is not cited by the Rule.
   One sentence, under (c).

## Not observed
dsys's mapping module and countersign-system's own stores were not read; this audit maps dyad-system only. The
projector was not run on the live instance for this audit (its test runs it on every push); the stale rows in
§3 are read from its source. Whether a renamed store would break the ledger's 319 rows at every historical
commit the plan gate reads was not measured; it is the reason (b)'s cost is stated as weeks and not estimated.
