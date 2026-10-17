# Falsification — the d-work ↔ countersign mapping, and the three-layer split (d-work #330)

Record for `agent-corpus/audits/2026-10-17-dwork-countersign-mapping.md`. Three claims the audit encodes, each
attacked before the audit was written (Rule-9); only survivors are stated there.

**C1.** *Design, architecture and framework, as defined in the audit's §1, are exhaustive and non-overlapping for
what this corpus holds.*
**C2.** *The d-work framework is the countersign core's dyad-system profile, reached by projection and by
nothing else; no d-work store is in the core's shape and nothing in the core binds the dyad's process.*
**C3.** *The audit's divergence list (D-1…D-10) is complete against the craft's own derivation rules D1–D8 and
its §7 of owed refactors.*

| # | attack | result | survivor |
|---|--------|--------|----------|
| A1 | C1: a guard's docstring is design (why), architecture (its `FIELDS`) and framework (what it refuses at push) in one file; the split fails on the corpus's commonest unit. | survives, scoped | The split classifies *statements*, not files: §1 says so and gives the three tests. A file carrying all three is the norm (a craft carries all three by design); a *sentence* that is two at once is the refactor's finding. C1 is restated as exhaustive and non-overlapping over statements. |
| A2 | C1: "checked by" is not a defining property; a design could be guarded (a lint on ADR headings) and an architecture could be unguarded. | refuted | The column records how each layer *is* checked here, not how it must be; the definitions rest on the question each answers. The column is kept as evidence of the corpus's practice, labelled as such. |
| A3 | C1: Rule-5 already has two sets (Requirements, Architecture) and the sysarch README a third home (syseng, "implementation discipline"); a fourth word, *framework*, duplicates "System Requirements". | survives, scoped | Not quite: System Requirements is a *set of Rules*; framework is the procedure those Rules plus the play-books and verbs constitute. The audit says the corpus already applies two of the three; it does not claim the names coincide. Whether `System Requirements` should be renamed is the refactor's, and it is not proposed. |
| A4 | C2: "by nothing else" is false — Rule-3 cites the craft by path for mandate, implicit mode, the escalate edge and the answer grammar (#290), so the core *does* bind the dyad's process through its vocabulary. | survives, scoped | The terms are adopted by craft name (Rule-13 property 1), and Rule-3 is what binds; the craft's own `interaction.md` says it "binds no system's agent by itself". C2 is restated: the core reaches the process only through terms a Rule adopts, and the stores only through the projector. The audit's §5 records this as agreement by adoption. |
| A5 | C2: the stores are already partly in the core's shape — `mode` on rows is the core's attribute, stored. | survives, scoped | One field, adopted in name and values (`explicit`, `implicit`; the core's third value `automatic` is not in `dyadlib.MODES`). The audit's §3 marks it exact in name and stale in projection. C2 holds for the stores as wholes; the row is the first store field in the core's vocabulary, and option (c) of D-10 is the recognition that this is the trajectory. |
| A6 | C3: the list misses the self-diagnostic (0.3.0), which the dyad has not adopted; that is an owed refactor the craft's §7 predates. | confirmed | Added: §4.2 maps the self-diagnostic to the standing audit and the evidence block, and gap 5 of §7 names adoption under (c). C3 is restated as complete against D1–D8, §7 and 0.3.0's self-diagnostic. |
| A7 | C3: D7's heuristic (any `<system>-<id>` ref is an intake origin) is a divergence the list omits. | refuted | It is a stated derivation, not a divergence: `schema.md` D7 says "stated, not checked". The audit's §3 carries it as *derived* with the note. |
| A8 | C3: `relayed prompt` (vocabulary, #253 R29) has no core counterpart and the list does not say so. | confirmed | Added to §3 (the relay note is not read; no core counterpart) under the Initiation row; D-6 covers it. |
| A9 | The audit should choose D-10's direction; elevating it is evasion. | refuted | Detect, don't dispose. F7's survivor forbids migration today, so (b) changes a craft rule's survivor and (c) changes Rule-3's citations: each is a plan the Operator disposes. The audit gives each its cost and states which is already in the ledger's trajectory, which is the most an audit may say. |
| A10 | The mapping duplicates `schema.md` D1–D8 and the play-book's countersign column. | refuted | Those are the core's view outward (how each core field is filled) and the machine's view of its own edges; neither carries per-row *status*, the stale bridge, the §5 table's gaps, the lifecycle status or the costed options. The audit cites both and adds those. |
| A11 | The costs in §6 are guesses. | survives, scoped | They are sized by zone and by what each touches (one craft PR; a Rule sentence plus record; a schema version; every Rule and 319 rows), not by hours; "weeks" for (b) is the only duration word and is marked unmeasured in Not observed. |
| A12 | Easy agreement. | pushed | A6 and A8 landed and changed the audit's text before it was written. |

**Survivors encoded.** C1 over statements, with the three tests and the *mixed* finding; C2 as projection for
the stores and adoption for the terms; C3 as complete against D1–D8, §7 and the self-diagnostic, with the two
additions A6 and A8 brought in.

Disposition: see ledger #330.
