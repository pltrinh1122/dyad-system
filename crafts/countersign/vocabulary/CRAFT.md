# countersign craft vocabulary (Tended terms)

One row per term. Craft terms are referenced, never defined, by the Agent vocabulary
(`dyad/vocabulary/VOCABULARY.md`, Rule-6 Boundaries), as `countersign:<term>`. `rule` names the craft
rule (`../rules/`) that owns the term. No Agent term is redefined and no dyad-system term renamed
(plan #156, F4): where the Countersign word is already an Agent term (`release`, `proposal`) or
another craft's (`event`, the sysadmin craft's), the term here carries the `countersign` prefix; `countersign report`
carries it too, so the Agent Rules' ordinary verb *report* is not bound to the primitive's sense (a report never asks).
Checked by the craft guard (`dyad craft check countersign`: well-formed, namespaced, every `rule`
exists).

| term | definition | rule |
|------|------------|------|
| countersign | to sign as the second, independent party an instrument the first party authored, without which the instrument is void; in a dyad, the human's answer to what the agent proposes | schema |
| countersignature | one human act covering one act: a signer (always a human party), an answer (`yes`, `no`, `amend`), a basis, the verbatim text, a bound hash when the subject carries one, and a time; an interaction primitive | schema interaction |
| Countersign core | the eight entities — party, act, countersign proposal, countersignature, mandate, countersign release, countersign event, escalation — and the check attribute, as `../templates/countersign-core.json`; logical, reached by projection, never a storage format | schema |
| party | who acts in a Countersign system, of one kind: `human`, `agent` or `executor`; only a human countersigns | schema |
| act | one consequential unit of work, in exactly one countersign mode at a time, processed by one party; a dyad-system d-work row projects to one | schema |
| countersign mode | the way one act obtains its countersignature and who processes it: explicit, implicit or automatic; a mode of an act, never of the architecture and never a sub-system (#153) | schema |
| explicit mode | countersigned live by a human, per act; an agent processes | schema |
| implicit mode | countersigned in advance by a standing mandate; an agent processes | schema |
| automatic mode | countersigned beforehand by a countersigned release; a non-inferring executor processes | schema |
| executor | the non-inferring party that processes automatic acts; the one mode-exclusive sub-system | schema |
| basis | how a countersignature covers its act: `per-act`, `mandate` or `release`; what dsys calls a disposition's mode, renamed here so the word `mode` keeps one sense | schema |
| mandate | a standing countersignature for one class of act (scope: event class, plan template, budget, rights); the countersignature of implicit mode; in dyad-system, the preference `ledger-pr-merge: agent` (an authority preference) | schema interaction |
| countersign proposal | what is put up for countersignature: one act's plan or question, authored by an agent party, with its body and, when it has one, its artifact hash; as an interaction primitive, one path, its strongest counter, a reconciliation and exactly one question, last | schema interaction |
| countersign release | a countersigned, versioned, hashed definition (run-book, flow, craft tree) an executor runs; in dyad-system, a release tag | schema |
| countersign event | one append-only execution record of an act, numbered by its position; in dyad-system, a run-book event | schema |
| escalation | the unexpected returned to a human: from an act (or one outside the document), with a reason, opening an explicit act or none; in dyad-system, an intake origin or an incident; an interaction primitive, which becomes a countersign proposal in explicit mode | schema interaction |
| delegate edge | the mode change explicit → implicit: a live countersignature becomes a mandate | schema |
| codify edge | the mode change explicit or implicit → automatic: a practice becomes a countersigned release | schema |
| escalate edge | the mode change automatic or implicit → explicit: the unexpected is returned for a live countersignature | schema |
| check timing | when a check judges its target: `before` (it blocks, as dyad-system's guards do) or `after` (it judges, as dsys's referee does); a policy attribute, not a structure | schema |
| system profile | the entities and fields a system keeps outside the Countersign core, carried in an instance's `profile` object; never mapped into the core | schema |
| derivation rule | a stated rule by which a projector fills a core field a system does not store (dyad-system's D1–D8, `../rules/schema.md` §4 and `../rules/interaction.md` §3) | schema |
| Countersign Interaction Model | the one interaction model of every Countersign system, in every mode: five interaction primitives, the imperatives I1–I8, one mode lifecycle per countersign mode (`../rules/interaction.md`) | interaction |
| interaction primitive | one of the five kinds of exchange the model is built from: initiation, countersign proposal, countersignature, countersign report, escalation | interaction |
| initiation | the origin of an act, kept verbatim: a prompt (human → system), a signal (a registered source → system) or a release trigger (the executor running a countersigned release); an act with none is self-initiated, which I6 forbids | interaction |
| signal | an initiation from a registered source rather than a human: in implicit mode, what a mandate may cover; in dyad-system, an intake the Operator's `Y` admitted | interaction |
| release trigger | the initiation of an automatic act: the occasion on which the executor runs a countersigned release | interaction |
| countersign report | agent or executor → human: evidence (an evidence block, event ids, counts) that never asks; what it surfaces unsigned becomes an escalation | interaction |
| answer grammar | the three answers of a countersignature — `yes`, `no`, `amend` — and each system's words mapped onto them at its boundary (dyad-system `Y` / `N` / `N` with text; dsys yes / no / counter) | interaction |
| amend | the third answer: the proposal refused and its revision asked for in the same words, a linked re-entry; dyad-system's `N` with text, dsys's `counter` | interaction |
| interaction imperative | one of I1–I8, binding in all three modes: only a human countersigns; one question, last; falsify before proposing; detect, don't dispose; words verbatim; no self-initiation; every act carries its mode and a countersignature reference; silence is not consent | interaction |
| mode lifecycle | the sequence of interaction primitives one mode's act passes through (explicit: initiation, proposal, countersignature, report and done proposal; implicit: signal, mandate or escalation; automatic: release, trigger, events or escalation) | interaction |
| form preference | a standing countersignature that shapes how countersign proposals and reports look and authorizes nothing (dyad-system: `concise-mode`, `batch-disposition-mode`, `merge-disposition`, `delegation`) | interaction |
| authority preference | a standing countersignature that authorizes one class of act in advance: a mandate (dyad-system: `ledger-pr-merge`) | interaction |
| command adapter | a slash-command file that invokes a procedure (a play-book, a run-book, a Rule's form) by reading it, never the procedure itself (#115); one kernel's way to offer it (`../templates/commands/`) | interaction |

## Collisions resolved by namespace (#142 §2)
The words below mean different things in dyad-system and dsys. The Countersign core uses none of them
as a field; where a mapping must name one, it names the owning system's sense by namespace, and no
dyad-system term is renamed. (A list, not a table: the craft guard reads every table here as terms.)
- **run-book** — `countersign:run-book`: a release definition an executor runs, zero inference
  (automatic mode). dyad-system: `sysadmin:run-book`, a curated shell reference with telemetry,
  runnable by agent or Operator. dsys: the Automaton plane's JSON step list. *Inverted.*
- **event** — `countersign:event` (countersign event, above). dyad-system: `sysadmin:event`, one
  run-book command's execution, evidence only. dsys: AutomatonEvent, replayed. *Overlap.*
- **role** — not a core field (a party's `kind` instead). dyad-system: `sysadmin:role`, who may run a
  run-book command. dsys: a sealed prompt bundle. *Collision.*
- **`dyad`** — not used. dyad-system: the entrypoint `dyad/bin/dyad`. dsys: the retired CLI, renamed
  `dsys`. *Inverted.*
- **mode** — `countersign:mode` (countersign mode, above). dyad-system: no term. dsys:
  `DispositionMode`, mapped to `basis` at dsys's mapping boundary (F4). *Collision.*
- **release** — `countersign:release` (countersign release, above). dyad-system: `release`, a git tag
  (Agent term, Rule-11). dsys: a tag, or an AutomatonRelease. *Overlap.*
