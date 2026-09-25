# Countersign Interaction Model (countersign craft, Tended rule)

Read by this craft's projector (`../projectors/project_countersign.py`, `interaction`: I6; `check`: I1 and I7), by
its command adapters (`../templates/commands/`), and by every system that adopts the model — dyad-system through
its Agent Rules, dsys through its own mapping module, countersign-system natively; no core Rule reads it. A Tended
rule: any form, no Rule-4 block, no sweep. It states the model a system's interaction is *checked against*; it
binds no system's agent by itself — in dyad-system only its Agent Rules do, and §7 lists where they still differ.
Terms: `../vocabulary/CRAFT.md` (rule `interaction`). Record: `../falsification/interaction.md` (R1–R12).
Source: plan #152 revision 2 §1–§3 and §6 (`agent-corpus/d-work/plans/152.md` in dyad-system).

## Intent
State one interaction model between the human and the system — five primitives, eight imperatives, one
lifecycle per mode — that is the same in explicit, implicit and automatic mode (`schema.md` §2) and the same in
every Countersign system, so that a system's own words for asking and answering map onto it without loss.

## 1. Five primitives
The same in every mode and every system. Each is an entity or an attribute of the core (`schema.md` §1), or a
derived profile field where the core has none yet (Initiation, D8 below).

| primitive | who → who | carries | asks? |
|---|---|---|---|
| **Initiation** | human → system (*prompt*); registered source → system (*signal*); executor (*release trigger*) | the originating words or payload, kept verbatim | — |
| **Countersign proposal** | agent → human | one path, its strongest counter, a reconciliation (dyad-system Rule-10; dsys's "DFD turn") | exactly one question, the last line |
| **Countersignature** | human → system | answer ∈ {`yes`, `no`, `amend` + text}; basis ∈ {`per-act`, `mandate`, `release`}; the verbatim text; bound to a head or hash | — |
| **Countersign report** | agent or executor → human | evidence: an evidence block, event ids, counts | nothing — a report never asks |
| **Escalation** | system → human | what was unsigned or unhandled, and why | becomes a countersign proposal, in explicit mode |

A report that surfaces something unsigned does not ask; it raises an escalation, which does (R5).

## 2. The answer grammar
Three answers, one sense in every system. A system's own words map onto them at its boundary; no system's
words are renamed in its own store (`schema.md` F4).

| answer | dyad-system (Rule-3) | dsys (CTA response) | meaning |
|---|---|---|---|
| `yes` | a bare `Y` | `yes` | the proposal is countersigned as asked |
| `no` | a bare `N`, or any response that is not a disposal | `no` | nothing is authorized (I8) |
| `amend` | `N` with text: today a new row linked to the refused one (de facto; §7) | `counter` | a linked re-entry: the proposal is refused *and* its revision is asked for in the same words |
| — | `Y` with text | — | a `yes`, plus a new Initiation (a prompt) carried by the same message |

dsys's five disposition kinds (its `DispositionMode` values) are *bases and occasions*,
never answers (#156 F4): `set_standing` is a countersignature whose basis is `mandate`; the others are
`per-act`. The answer stays one of three (R2).

## 3. Eight imperatives (I1–I8)
Binding in all three modes. "Checked" names the mechanism in this craft; everything else is inference, stated.

| # | imperative | source | checked |
|---|---|---|---|
| **I1** | **Only a human countersigns.** Proposer ≠ disposer. | dyad-system Rule-2; dsys I-2 | **yes** — `check()`: a countersignature's signer is a `human` party, a proposal's author an `agent` party |
| **I2** | **One question per reply, the last line.** The answer grammar is §2's. | Rule-3 Scope, Rule-10 Form; dsys E3 `counter` | inference (a question lives in the conversation, not in a store) |
| **I3** | **Falsify before proposing.** | Rule-9; dsys playbook gates | inference; the record's existence is the evidence (`/falsify` produces one) |
| **I4** | **Detect, don't dispose.** Challenge intent, surface bare claims, never overrule. | dyad-system frame | inference |
| **I5** | **Words kept verbatim.** Every prompt and every countersignature is stored as given. | Rule-7; dsys DecisionRecord | partly — the projector takes a countersignature's text from the provenance record when its count matches the row (D3), and marks `text_source: ledger` when not; the fidelity of a transcription is inference |
| **I6** | **No self-initiation.** An act starts only from a prompt, a registered signal or a countersigned release. | Rule-3 Scope and Intake; dsys "three keys" (the ambient invents no work) | **yes, as a warning** — `interaction()` over D8 (below) |
| **I7** | **Every act carries its mode and a countersignature reference.** | #153; `schema.md` | **yes** — the schema requires `mode` (one of three) on every act, and `check()` the processor kind the mode requires and that every countersignature's subject resolves. An act still awaiting its first answer has no countersignature, by I8: that is not a finding |
| **I8** | **Silence is not consent.** An unanswered question authorizes nothing. | Rule-3 ("any other response"); dsys E5 | inference; the projector derives no countersignature from an absent answer (D3) |

### I6's derivation (D8, dyad-system)
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
schema check's. Three reasons, each observed: rows opened before Rule-7 carry no prompt entry, and dyad-system's
`provenance.SINCE_ID` (164) lies above every row id of this instance, so no id cut-off separates the legitimate
gaps; a concurrent session opens rows without having loaded Rule-7 (the reason Rule-7 itself only warns); and D8
is a heuristic (a `<system>-<id>` token read as an intake origin). A red projection is the wrong way to learn any
of the three. What a warning names is a candidate for the Operator, never a verdict: a row opened by the agent's
own finding (a backlog row with an empty `disposed`) is exactly what I6 forbids, and the warning makes it visible.

## 4. Lifecycles, one per mode, built only from the primitives
- **explicit:** Initiation (prompt) → countersign proposal (the plan) → countersignature → execute → countersign
  report + countersign proposal (done) → countersignature.
- **implicit:** Initiation (signal) → is it covered by a mandate? If yes: execute within the mandate's scope, then a
  countersign report. If no: escalation → explicit.
- **automatic:** a countersigned release → the executor runs on its trigger (Initiation: release trigger) →
  countersign events. An unhandled trigger: escalation → explicit.

The mode-specific parts are only *which basis* the countersignature has and *who* processes; both are
attributes of the act (#153), so one model spans the three (R1).

## 5. Preferences in the model
A preference is a standing countersignature, of one of two kinds:
- a **form preference** shapes how countersign proposals and reports look, and authorizes nothing;
- an **authority preference** is a mandate: it countersigns in advance one class of act.

dyad-system's eight, classified:

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

A new preference is classified here when it is added: an authority preference that is not projected as a mandate
is an I7 gap (its covered acts would carry no countersignature reference).

## 6. Command adapters
A slash command is an **adapter** that invokes a procedure, never the procedure (#115's survivor: "the adapter,
never the artifact"). The procedure stays a play-book, a run-book or a Rule, versioned with its craft and working
under any kernel; the command is one kernel's way to *offer* it. Templates: `../templates/commands/`.

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

Installing: copy `../templates/commands/*.md` into the system's `.claude/commands/`. In a dyad-governed tree
`.claude/` must first be claimed by a zone (plan #152 PR-1, `("infra", ".claude/*")`); until then a committed
command is an unclassified path, which Rule-1 forbids (R4).

## 7. Adoption: refactors each system still needs — **not yet adopted**
Listed, not authorized here: each is its own unit of work in its own system, because each changes a Rule or a
deployed core (plan #152 §6).

| system | refactor | imperative |
|---|---|---|
| dyad-system | Rule-3: name `amend` in the answer grammar (`N` with text = a linked re-entry) | I2 — today implicit in "any other response" |
| dyad-system | a mandate *record* (`ledger-pr-merge` moved from preference prose to a countersigned record) | I7 — needs data, not prose |
| dyad-system | a `mode` field on rows | I7 — today derived (D1) |
| dyad-system | an initiation recorded for every row (a `prompt` entry, or the intake origin) | I6 — today derived (D8) and warned |
| dsys-repo | slash-command family `eval-*` → `/falsify`; `pb-*` kept | one adapter per procedure |
| dsys-repo | a licence decision | gates any reuse of its playbook texts |
| countersign-system | its Rules amended toward this model by its own units of work | hand-over criterion H3 |

## When
- An interaction primitive, imperative, answer or lifecycle changes: this rule, the projector's `interaction` or
  `check`, its test and `VERSION` change in the same unit of work.
- A preference is added to a system that projects onto the core: it is classified in §5.
- A command adapter is added: its template names the procedure file it reads, and §6 lists it.

## Sources
dyad-system #146 and #147 (the modes and edges), #150 (the countersign), #153 (modes of an act), #156 (the core
schema, F4's answer mapping), #115 (a command is the adapter, never the artifact), #152 revision 2 (this model);
dsys by name only: its decision-record and CTA specification (answers yes / no / counter, disposition kinds),
its "three keys" invariant, its E3 and E5 rules, and its slash commands `pb-decide`, `pb-extend`, `eval-meta`,
`eval-pb`, `eval-rb`, `eval-sc`, `sc-author`.
