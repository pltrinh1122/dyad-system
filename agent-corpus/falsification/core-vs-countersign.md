# Falsification — "the core = countersign" and "d-work is an instance of countersign" (d-work #334)

Two claims the Operator asked to have falsified, for understanding and for the consolidation #330 §6 (D-10)
will cite. Attacked against the corpus as it stands: the core craft `dyad-operator` at `dyad/`, the Tended
craft `crafts/countersign/` 0.3.0, and the mapping audit `agent-corpus/audits/2026-10-17-dwork-countersign-mapping.md`
(#330). Each claim is refuted as stated and survives scoped; the survivors are not the claims.

**C1.** *dyad-system's `core` is `countersign`.*
**C2.** *`d-work` is an instance of `countersign`.*

## C1 — the core = countersign

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1.1 | They are one tree. | refuted | The core craft is `dyad-operator` at `dyad/` (agent zone, Rule-11 property 1). `countersign` is a Tended craft at `crafts/countersign/`, `VERSION` 0.3.0 (craft zone). Rule-1 forbids a PR that touches both, so the corpus itself holds them apart. |
| 1.2 | The core ships countersign: a core-only install has it. | refuted | Only `crafts/sysadmin/guards/changelog.py` declares `BUNDLED_WITH_CORE`. A core-only install has no countersign tree, and `infra/bundle` reports countersign "in the tree but unreleased". |
| 1.3 | Countersign binds this system's Agent, as the core does. | refuted | Its README says `rules/self-diagnostic.md` "binds no system's agent", and its rules are Tended Rules (Rule-4 Boundaries). Only `dyad/rules/` binds the Agent's process. |
| 1.4 | The core depends on countersign. | survives, scoped | Since #290 Rule-3 adopts four of its terms by citation (mandate, implicit mode, escalate edge, amend; Rule-13 property 1) and the vocabulary references them by craft name. The core reads the craft's words, not its code: no core guard imports it, and the declared dependency runs the other way (`crafts/countersign/MANIFEST.md`, `requires: dyad-operator>=0.10.1`). |
| 1.5 | Countersign is the core's own model, abstracted from it. | confirmed | The craft was authored here (#146 to #156) by projecting the core's countersigning spine. Its imperatives I1–I8 map onto Rules 2, 3, 7, 9, 10 and the frame (#330 §4); its mapping contract F1–F7 is satisfied "by projection", the core "keeping its own entities as a profile outside the core" (README). |
| 1.6 | The two have the same extent. | refuted, both ways | The core is larger: Rules 1, 8, 11–20 (zones, host mutation, distribution, infrastructure, stores, references) have no countersign counterpart. Countersign is larger elsewhere: automatic mode and the executor, the `release` entity, three party kinds, check timing, the self-diagnostic's four levels. |
| 1.7 | Easy agreement: the equality reads naturally after #330's audit. | pushed to 1.1 and 1.6 | Both refute it. |

**Survivor C1.** `countersign` is the portable model of the core's countersigning spine, authored from it and
kept as a separate Tended craft. The core conforms to that model by projection and cites its vocabulary.
Neither is the other, and neither contains the other. Which of the two should own the spine going forward is
D-10 of #330, elevated and not decided here.

## C2 — d-work is an instance of countersign

"Instance" has three senses in this corpus, and the claim is judged in each.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 2.1 | Instance in Rule-11's sense: one system's state of a craft. | refuted | A craft is installed, never instantiated (Rule-11 property 2). Countersign's instance data would be its projector's output and the self-diagnostic's records; the d-work store (rows, plans, provenance, presence, traces) is the core's instance data, owned by Rules 3, 7, 15 and 16. |
| 2.2 | Instance as one entity record: a d-work is one countersign `act`. | confirmed, scoped | By the craft's derivation rules D1–D8 (`rules/schema.md`) a row projects to one `act` with its proposals (plan files), countersignatures (dispositions) and escalations (incidents). Scoped: the projection is stale on `mode` (`project_countersign.py` fixes `DERIVED_MODE` at explicit), on `basis` (always per-act, never the mandate) and on `amend` (never derived), as #330 §3 found. |
| 2.3 | Instance as a realization of the model: the d-work framework implements the interaction model. | confirmed, scoped | Inputs, forms and lifecycles map onto the five primitives and I1–I8 (#330 §4). Scoped to explicit and implicit modes: the d-work machine (`dyadlib.INPUTS`) has no automatic mode and no executor. |
| 2.4 | A realization is a subset of its model. | refuted | The d-work framework is a superset profile. The machine with its input alphabet, the plan phases (Rule-15), presence files (Rule-16) and the trace have no countersign entity; countersign's `release` and `event` have no d-work counterpart beyond projection. |
| 2.5 | The dependency runs from d-work to countersign. | refuted | It runs both ways. The projector reads the core's stores through `dyadlib.read_rows` and the provenance guard; the core's Rule-3 reads the craft's terms. Neither can be removed without editing the other. |
| 2.6 | Easy agreement. | pushed to 2.1 and 2.4 | Both refute it as stated. |

**Survivor C2.** A d-work is, by projection, one countersign `act` with its proposals, countersignatures and
escalations, and the d-work framework is a conformant realization of countersign's interaction model in its
explicit and implicit modes. It is a superset profile that countersign describes, not an instance countersign
owns.

**Survivors encoded.** Nothing: both survivors are statements of what is, elevated to the consolidation
(#330 §6, D-10). No Rule, craft or vocabulary changes under this record.

Disposition: see ledger #334.
