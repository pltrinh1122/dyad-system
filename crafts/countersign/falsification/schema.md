# Falsification record — "a unifying Countersign schema maps cleanly to dyad-system and dsys" (d-work #156)

**Claim (Operator's):** a unifying schema for the Countersign Architecture can be formed that maps
cleanly to the existing dyad-system and dsys. Compared: dyad-system `ee89625`, dsys-repo `37fc52e`.
The candidate is the eight-entity core of plan #156 §1, now `../rules/schema.md` §1. The attack
table is plan #156 §2's (`agent-corpus/d-work/plans/156.md`), carried with the rule it falsifies.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| F1 | **The spine**: do both repos' core records map onto Act → Proposal → Countersignature → Event → Escalation without loss? | Survives | dyad-system: d-work row → Act; plan file → Proposal; `disposed` entries with provenance → Countersignature (answer Y/N, text verbatim); run-book event → Event; intake or incident → Escalation. dsys: DecisionRecord / HarnessRun → Act; draft / CTA → Proposal; Disposition → Countersignature (yes / no / counter → answer); AutomatonEvent → Event; Disclosure → Escalation (`schema.py:215-316`). |
| F2 | **Mandate and Release**: do both have instances? | Survives, thinly | dsys: `set_standing` Dispositions → Mandate; PromotionRecord / AutomatonRelease → Release, both modelled. dyad-system: the preference `ledger-pr-merge: agent` *is* a Mandate (a standing Operator authority for one class of act); release tags → Release. dyad-system has no record type for either: they live in preference prose and git tags (derivation rules D4, D5). |
| F3 | **Mode and processor**: does either repo record them per act? | **Refuted as "cleanly"** | Neither does. dyad-system's acts are all explicit by construction, so a mapping derives `mode=explicit, processor=agent` (D1). dsys stores mode implicitly in the entity type and never marks implicit. Both are derivable only by rule, not from data. |
| F4 | **Vocabulary**: does any term mean opposite things? | **Refuted** | dsys's `DispositionMode` (ratify, authorize, set_standing, overrule, triage) uses "mode" for what the core calls a countersignature's *basis or kind*; #142's inverted terms (run-book, event, role, `dyad`) collide the same way. Survivor: the core field is `basis`; the rename happens at dsys's mapping boundary; this craft's terms are namespaced (`countersign:<term>`) and no dyad-system term is renamed. |
| F5 | **Extension entities**: does everything map? | **Refuted for the whole, survives for the core** | dsys's Principal, Hat, R, Fleet, CoS Directive, GateCheck, Application, LocalVeto, Claim and IFF gates have no dyad-system counterpart; dyad-system's zone, craft, presence file, plan gate and evidence block have none in dsys. A core plus per-system profiles maps (every instance's optional `profile`); a single flat schema does not. |
| F6 | **Timing**: checks before (dyad-system guards block) against after (dsys referee judges). Representable? | Survives | As the `Check.timing` attribute: a policy difference, not a structural one. |
| F7 | **Representation**: markdown `key: value` stores against pydantic `SystemState` JSON. | Survives by projection | Both project to the schema: dyad-system by this craft's projector (the sysarch projection mechanism), dsys by its own mapping module. Mapping is code in each repo, not a storage migration. |

**Verdict:** "a unifying schema maps cleanly to both" is **refuted as stated** (F3, F4, F5).

**Survivor:** a Countersign **core** schema (the eight entities) maps to both repos **by projection**,
after two renames on dsys's side (at its mapping boundary) and two derivation rules on both; each repo
keeps its extension entities as a profile outside the core. Stated as `../rules/schema.md`; the
dyad-system half is checked by `../tests/test_project_countersign.py` on a fixture and on the live
instance.

**Limits.** The dsys column is plan #156's reading of dsys-repo at `37fc52e`, verified there by its
own PR (PR-C), not by anything in this craft. The D7 intake heuristic (a `<system>-<id>` refs token
read as an intake origin) is inference, stated in the rule.

Disposition: disposed by the Done-Y of dyad-system d-work #156 (see ledger #156).
