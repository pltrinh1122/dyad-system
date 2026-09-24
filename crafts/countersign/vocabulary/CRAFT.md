# countersign craft vocabulary (Tended terms)

One row per term. Craft terms are referenced, never defined, by the Agent vocabulary
(`dyad/vocabulary/VOCABULARY.md`, Rule-6 Boundaries), as `countersign:<term>`. `rule` names the craft
rule (`../rules/`) that owns the term. No Agent term is redefined and no dyad-system term renamed
(plan #156, F4): where the Countersign word is already an Agent term (`release`, `proposal`) or
another craft's (`event`, the sysadmin craft's), the term here carries the `countersign` prefix.
Checked by the craft guard (`dyad craft check countersign`: well-formed, namespaced, every `rule`
exists).

| term | definition | rule |
|------|------------|------|
| countersign | to sign as the second, independent party an instrument the first party authored, without which the instrument is void; in a dyad, the human's answer to what the agent proposes | schema |
| countersignature | one human act covering one act: a signer (always a human party), an answer (`yes`, `no`, `amend`), a basis, the verbatim text, a bound hash when the subject carries one, and a time | schema |
| Countersign core | the eight entities — party, act, countersign proposal, countersignature, mandate, countersign release, countersign event, escalation — and the check attribute, as `../templates/countersign-core.json`; logical, reached by projection, never a storage format | schema |
| party | who acts in a Countersign system, of one kind: `human`, `agent` or `executor`; only a human countersigns | schema |
| act | one consequential unit of work, in exactly one countersign mode at a time, processed by one party; a dyad-system d-work row projects to one | schema |
| countersign mode | the way one act obtains its countersignature and who processes it: explicit, implicit or automatic; a mode of an act, never of the architecture and never a sub-system (#153) | schema |
| explicit mode | countersigned live by a human, per act; an agent processes | schema |
| implicit mode | countersigned in advance by a standing mandate; an agent processes | schema |
| automatic mode | countersigned beforehand by a countersigned release; a non-inferring executor processes | schema |
| executor | the non-inferring party that processes automatic acts; the one mode-exclusive sub-system | schema |
| basis | how a countersignature covers its act: `per-act`, `mandate` or `release`; what dsys calls a disposition's mode, renamed here so the word `mode` keeps one sense | schema |
| mandate | a standing countersignature for one class of act (scope: event class, plan template, budget, rights); the countersignature of implicit mode; in dyad-system, the preference `ledger-pr-merge: agent` | schema |
| countersign proposal | what is put up for countersignature: one act's plan or question, authored by an agent party, with its body and, when it has one, its artifact hash | schema |
| countersign release | a countersigned, versioned, hashed definition (run-book, flow, craft tree) an executor runs; in dyad-system, a release tag | schema |
| countersign event | one append-only execution record of an act, numbered by its position; in dyad-system, a run-book event | schema |
| escalation | the unexpected returned to a human: from an act (or one outside the document), with a reason, opening an explicit act or none; in dyad-system, an intake origin or an incident | schema |
| delegate edge | the mode change explicit → implicit: a live countersignature becomes a mandate | schema |
| codify edge | the mode change explicit or implicit → automatic: a practice becomes a countersigned release | schema |
| escalate edge | the mode change automatic or implicit → explicit: the unexpected is returned for a live countersignature | schema |
| check timing | when a check judges its target: `before` (it blocks, as dyad-system's guards do) or `after` (it judges, as dsys's referee does); a policy attribute, not a structure | schema |
| system profile | the entities and fields a system keeps outside the Countersign core, carried in an instance's `profile` object; never mapped into the core | schema |
| derivation rule | a stated rule by which a projector fills a core field a system does not store (dyad-system's D1–D7, `../rules/schema.md` §4) | schema |

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
