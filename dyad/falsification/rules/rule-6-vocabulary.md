# Falsification record — Rule-6 (vocabulary)

**Claim (operator, 2026-09-12):** all Agent Rules share and cohere with one set of terms,
consolidated as an Agent vocabulary in `agent-corpus`; the vocabulary is the master record and
a mutation to it is coherent across all Agent Rules.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Coherent" is a Rule-5 term (same-trigger contradiction). Rule-6 overloads it — a vocabulary rule failing its own test. | Confirmed | Rule-6 says *consistent*; both words are vocabulary entries with distinct owners. |
| 2 | Master record + inline definitions = two sources (the zone-table defect, G3). | Confirmed | Definitions moved to the vocabulary; Rules 2–5 cite it. Rules keep operational consequences, not definitions. |
| 3 | Overlap with Rule-4 (shape) and Rule-5 (relations). | Survives | Terms are a third concern. Rules 4 and 5 name Rule-6 in Boundaries; Rule-6 names both. One-way each. |
| 4 | Whether a use matches the definition is not mechanisable. | Survives, scoped | Script checks form, owner, duplicates, orphans and `used by`; sense is inference at falsification. |
| 5 | Terms defined outside `agent-corpus` (preference keys, Tended terms). | Survives | Referenced, never defined, in the vocabulary. |
| 6 | Vocabulary change is a new ratification event. | Refuted | It is a PR merge in a d-work; Rules 2 and 3 already cover it. |
| 7 | The vocabulary is itself a Rule and needs a block. | Refuted | It is a record owned by Rule-6; listed as not-a-Rule in Rules 4 and 5. |

## Rule-5 pairwise statement (Rules 2, 3, 4, 5 edited; Rule-6 added)
- 6–1: Rule-1 defines no term inline; `zone` and `repo transaction` now live in the vocabulary with owner 1. Coherent, orthogonal (Rule-6 owns terms, Rule-1 owns paths).
- 6–2: `ratification event`, `proposer`, `disposer`, `clerical` owned by 2, defined in the vocabulary; Rule-2 cites it. One-way. Coherent, orthogonal.
- 6–3: ledger states and `d-work`, `plan`, `plan-Y`, `Done-Y`, `counter-prompt`, `disposition` owned by 3; Rule-3 keeps state consequences, cites the vocabulary for definitions. Coherent, orthogonal.
- 6–4: Rule-4 classifies (Agent vs Tended); the vocabulary defines the two terms. Rule-4 names Rule-6 in Boundaries. Coherent, orthogonal.
- 6–5: Rule-5's Definitions section now points to the vocabulary; Rule-5 names Rule-6 in Boundaries; Rule-6 names Rule-5 for *coherent*. Coherent, orthogonal.
- All other pairs: unchanged by this d-work.

Disposition: see ledger #53.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/vocabulary.py` → `dyad/guards/agent/vocabulary.py` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
fourteen rows (owners 8, 18, 19) moved to `crafts/sysadmin/vocabulary/CRAFT.md`; Boundaries bullet 2 names the craft file; the preamble lists the moved terms by craft name. Each Rule in the moved rows' `used by` (8, 18, 19, and 3 for none) still reads correctly: the kernels mention the terms in the craft's sense and reference the craft rule by path (attack 12 of plan #155; `vocabulary.py` checks defined rows only). Pairwise: 6–8, 6–18, 6–19 as above; 6–21: `guard` and `corpus` rows widened for the second root. Coherent, orthogonal.
## Amendment — d-work #156 (2026-09-14, craft vocabulary check)
Conditions gains the craft-vocabulary trigger (`vocabulary.py check_craft`: `term | definition | rule` well-formed,
no duplicate, every `rule` an existing craft rule file, no term equal to an Agent term); Master record states the
namespacing (referenced as `<craft>:term`, never defined twice). Terms added elsewhere: `export`, `craft registry`
(owner 11). Pairwise: 6–11 as in `rule-11-distribution-structure.md`; the craft guard invokes the check, Rule-6
owns it. Coherent, orthogonal.
## Amendment — d-work #302 (2026-10-15, seat, holder, relayed prompt)
Three rows added, no Rule edited: `seat` and `holder` (owner 16, used by 16) — in Rule-16 Presence since
#294 and defined nowhere — and `relayed prompt` (owner 3, used by 3) — in Rule-3 Intake since #34, likewise.
Each named Rule still reads correctly (the term check: `ok [rule-6] 98 terms, owners and used-by resolve`); the statements per term are in
`agent-corpus/falsification/communication-planes.md`. Rule-7 property 4 describes the relayed prompt without
the phrase and is not listed. Four further terms the same synthesis proposed — `announcement`, `carrier`,
`relay`, `report by state` — are #253 §0's and enter with the bus craft as `bus:` references (Master record),
never as orphans now. Pairwise: 6–16, 6–3 as the record states. Coherent, orthogonal.

## Amendment — d-work #477 (2026-10-26, C4 of #473: the guard wrapper is a step of `dyad-package.yml`)
**Claim (plan #473, the Operator's `Y` of 2026-10-26, and the Y recorded on #477 at 3393b19):** the CI wrapper this
Rule names, `.github/workflows/dyad-vocabulary.yml`, becomes a named step of `.github/workflows/dyad-package.yml` (job `package`),
same guard, same trigger (push to `main`, ledger-only paths ignored, and dispatch), still detecting; the Rule's
sentence names the new file and step, meaning unchanged.

| # | attack | result |
|---|---|---|
| 1 | One job couples the guards: a failure in one step hides the others. | Survives, scoped: CI here only corroborates after the merge (Rule-14 property 3); the blocking checks run before the push on the kernel-only path, every guard in one run. |
| 2 | Re-pointing before the old file is removed leaves two names for one check. | Refuted: this PR lands first and resolves on today's `main`, where both files exist; the removal PR follows, so no state names a missing file. |

**Pairwise (Rule-5).** **6–1**: the wrapper stays infra zone. **6–20**: the new path resolves on today's `main`. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #477.

## Amendment — d-work #553 (2026-11-02, part B: the crosswalk and the label-case criterion)
**Claim (plan #553 revisions 1–2, the operator's `Y` of 2026-11-02 with the four recommendations):** the dyad-native
vocabulary replaces `seat`, `attended`/`unattended`, `executor`, the structural `cos` and "a unit of work"; a crosswalk
beside the vocabulary maps every old term, key, form and file to its new one, so history stays readable unrewritten;
the criterion `label-case` (L1–L6) decides a label's case. This part adds the crosswalk and the criterion; the new
vocabulary rows enter with the Rule text that uses them (part D), because this Rule's guard fails a row whose `used by`
Rules do not mention it.

| # | attack | result |
|---|---|---|
| V1 | The crosswalk defines terms beside the vocabulary, so there are two master records. | **Refuted**: it maps and defines nothing; every new term's one definition is its vocabulary row (Master record). Its header says so. |
| V2 | Adding the rows first, as the plan's step 1 orders, keeps the plan's order. | **Confirmed impossible**: `vocabulary.py` fails a row whose `used by` Rules do not mention it, and no Rule mentions `solo`, `home`, `pair` or `dyad unit` yet; Rule-6 Conditions puts a term a Rule introduces in the same PR. The rows ride part D; the order change was put to the cos before any push. |
| V3 | "dyad" is overloaded: the system, the pair, a unit kind. | **Survives with the operator's convention** (plan attack 1): "dyad unit" where the system is also in view; the row (part D) states the three senses. |
| V4 | "unit" collides with "unit test". | **Survives, scoped** (plan attack 2): "unit test" is its own compound; the freed "unit of work" leaves live text only. |
| V5 | History in old terms becomes unreadable. | **Refuted** (plan attack 6): the crosswalk maps it; history is append-only and never rewritten. |
| V6 | `label-case` lives in the core but its home is a craft's rule. | **Survives, scoped**: syseng is a bundled craft (Rule-11 property 2), so the home ships with the core; the DMC schema admits a `../crafts/…` home and warns, never fails, where a craft is absent. |

**Pairwise (Rule-5).** No Rule changes in this part; the pairwise statements for the Rules part D edits are written
there.

Disposition: see ledger #553.

## Amendment — d-work #553 (2026-11-02, part D: the dyad-native terms in the Rules and the play-books)

**Claim (plan #553 revisions 1–3, the operator's `Y` of 2026-11-02 with the four recommendations):** the Agent Rules
and the four play-books move to the dyad-native vocabulary — `unit` for the generic seat, `dyad unit` and `solo` for
an attended and an unattended seat, `pair`/`unpair` for declaring attendance, `home` for the structural cos,
`automaton`/`auto` for the countersign model's executor, `d-work` redefined as a body of work, `done-Y` for Done-Y, and
`operator`/`agent` lowercase in prose — with the vocabulary rows entering in the same PR as the Rule text that uses
them (Rule-6 Conditions), alias rows for `seat`, `attended` and `executor`, and Rule-3's answer grammar reading an
answer by meaning. Mechanisms, the Rules' force and history are unchanged (scope 2): every old word history carries is
mapped by `dyad/vocabulary/crosswalk.md` (part B), and every form a tool reads keeps its alias (part C).

Rules edited: 2, 3, 7, 8, 9, 11, 12, 14, 15, 16, 18. Play-books edited: audit, countersign-model, d-work, release.

**Attacks.**
| # | attack | result |
|---|---|---|
| D1 | Lowercasing `operator` and `agent` at the start of a sentence breaks English and reads as a typo. | **Refuted, by construction**: the pass lowercases only inside a sentence; a sentence-initial word keeps its capital, as any word does (Rule-8's Provenance "Operator gap E5", Rule-15's "the done-`Y` as Rule-3"). The term is lowercase; the sentence's first letter is typography. |
| D2 | `Agent Rule` is a term and would be lowercased with `agent`. | **Refuted**: the pass leaves `Agent Rule` and every backticked span untouched; `vocabulary.py` still finds `Agent Rule` in Rules 4, 5 and 6, which this part does not edit. |
| D3 | The case change alters a guard's reading: `vocabulary.py` matched "Operator" and "Done-Y". | **Refuted**: `vocabulary.fold` lowercases both sides, so `operator` and `done-y` match the same text; the guard's observed line after the edit is `ok [rule-6] 131 terms, owners and used-by resolve`. |
| D4 | Rules 1, 4, 5, 6, 10, 13, 19 and 20 also carry `Operator`/`Agent`, so the Rule set is now mixed in case. | **Confirmed, reported as a finding**: those Rules are outside plan #553's files touched (Rules 2, 3, 7, 8, 9, 11, 12, 14, 15, 16, 18), so editing them is a departure needing its own `Y`. The mix is case only; no meaning differs, and the vocabulary's conventions paragraph says which form is canonical. A follow-up row can sweep them. |
| D5 | `unit` names a position now, so "every unit of operator-prompted work" in Rule-3's Intent and "the collision-free unit" in Rule-15 read as positions. | **Confirmed and fixed**: Rule-3's Intent says "every body of operator-prompted work", Rule-15 "the collision-free record", and the play-books' "unit of work" becomes "body of work". |
| D6 | The cabinet guard's entity is still `seat`, `seats.py`, `seats_rules.txt`; Rule-16 citing them beside `unit` contradicts the rename. | **Survives, scoped** (crosswalk, entity row): identifiers are not vocabulary; renaming them would change the registry, `check --list` and the references register, a mechanism scope 2 excludes. The `seat` alias row says so. |
| D7 | Rule-16 names the key `paired-units` while the operator's preferences table still holds `attended-seats`. | **Survives**: part C reads `paired-units` first and `attended-seats` as its alias (`sessions.declared_preference`), so the Rule is true of the code either way; renaming the operator's own key is the cos's preferences-zone question (plan step 7), never accretable (Rule-2, Binding). `references.py` resolves no preference key named in prose, and the preferences guard is green. |
| D8 | Reading `yes` as `Y` lets the agent put a disposition in the operator's mouth. | **Refuted** (plan revision 2, R2): the provenance record keeps the words as typed (Rule-7 property 4), and the row records the token the answer grammar defines; a reading that could lead to two acts is asked, never chosen. |
| D9 | A mid-row pairing reroutes a question already in flight. | **Survives with the board** (plan decision 3): the board's `question` line records where the question was asked, and Rule-16 says a question already asked keeps that route. |
| D10 | `home` and the cabinet craft's `cos` define the same thing twice. | **Refuted**: `cos` is the cabinet craft's title for the unit (`crafts/cabinet/vocabulary/CRAFT.md`), `home` the core's structural term for it; `check_craft` compares terms, and none is equal. Rule-16 says "the home is titled cos there". |
| D12 | The vocabulary's `Operator` and `Agent` rows can be lowercased with the prose. | **Confirmed false at the push gate**: the sysarch craft's schema projector (`crafts/sysarch/projectors/project_schema.py`) selects the party boxes by the exact term `Operator`/`Agent`, and its live test failed. That code is craft zone and outside the plan's files touched, so the two term cells keep their capitals and their definitions say lowercase in prose; a follow-up row can make the projector casefold (L6) and then lowercase the cells. |
| D11 | `auto` and `automaton` are defined with nothing that realizes them. | **Survives, scoped**: both rows say reserved / none yet; they name the gap the countersign model's automatic mode leaves (the play-book's executor row now points to them), and nothing reads them as live. |

**Rule-6: every Agent Rule in a changed term's `used by`.**
- `Operator` (2 3 4 5 6), `Agent` (1 2 3 4 5 6): the definition gains the prose convention, the term cells unchanged (D12); each listed Rule still mentions it (the guard folds case) and reads correctly.
- `done-Y` (2 3): Rules 2 and 3 say done-`Y`; meaning unchanged.
- `d-work` (2 3 4 6 7): the definition names a body of work and its scope; no use in those Rules depends on "unit", and each reads correctly.
- `unit` (3 7 16), `seat` (16), `dyad unit` (16), `solo` (3 16), `automaton` (16), `auto` (16), `executor` (16), `home` (3 16), `pair` (16), `unpair` (16), `unit name` (3 16), `attended` (16): Rules 3, 7 and 16 now use them in these senses, and only these Rules list them.
- `hop`, `inbox`, `cos-board`, `secretary`, `party`: wording inside the definition (home for cos, unit for seat, automaton beside executor); the Rules listing them (3, 16; 2 3 18 19 for `party`) read unchanged.

**Pairwise (Rule-5).**
Every edit is of words, not of what a Rule owns, so no concern moves between Rules.
- **3–16**: Rule-3 says the home relays a solo's questions and the inbox is addressed by unit name; Rule-16 defines the kinds and the inbox path with `<unit>`. Coherent: both name one route; Rule-16 owns the store and the kinds, Rule-3 the counter-prompt.
- **3–7**: Rule-3's answer grammar reads an answer by meaning and cites Rule-7 for the words kept verbatim; Rule-7's property 4 is unchanged in force (`relayed via <unit>`). Coherent, orthogonal.
- **3–8**: Rule-3 now cites Rule-8's blocking-question form for an ambiguous answer; Rule-8 owns the form. Coherent.
- **2–3, 2–11, 3–11**: done-`Y` in all three, one sense. Coherent.
- **16–2**: Rule-16 says pairing is the operator's act through a preference; Rule-2 says a preference value is the operator's to dispose. Coherent.
- **7–16**: Rule-7's `relayed via <unit>` and Rule-16's attendance check reading the note; same text, unchanged force.
- **8, 9, 12, 14, 15, 18** with every other Rule: case only (and Rule-15's "record" for "unit"); no instruction differs.
- **1, 4, 5, 6, 10, 13, 19, 20** with every edited Rule: unchanged; they keep `Operator`/`Agent` capitalized (D4), which differs in case only.
No gap is found beyond D4.

Disposition: see ledger #553.

## Amendment — d-work #560 (2026-11-02: three layers, three vocabularies; the organization's roles leave the core)
**Claim (plan #560, the operator's plan-`Y` of 2026-11-02, the model C1–C7 and criteria D1–D5 of its provenance entry 1):**
the core vocabulary names kinds of unit and acts every system has, the organization craft names roles, the instance
names its own positions, and no layer defines another's words; a unit is spoken of by name, then title, then kind,
only as needed. Plan #560's attacks A1–A19 are this claim's falsification; the ones this part acts on follow.

| # | attack | result |
|---|---|---|
| E1 | (A1, F7) `secretary` and `cos-board` are rows of this vocabulary, owner 16, though only a multi-unit organization has them. | **Confirmed and fixed**: both rows leave the core; the introduction lists them among the cabinet craft's terms, and Rule-3 (Ledger) and Rule-16 (Presence) say "a unit with a function" and cite the organization craft's `secretary` and `cos-board`. The cabinet's `CRAFT.md` gains the two rows in the craft-zone PR that follows this one (`check_craft` refuses a term defined in both, so the core row goes first). |
| E2 | (A13, F5) Rule-16 named an instance position, "the operate unit's". | **Confirmed and fixed**: "the unit whose charter holds the host". |
| E3 | The conventions paragraph needs examples, and the natural ones are this system's own units. | **Confirmed and avoided**: examples naming `program` or `engineer` would put instance names into the core, the failure C1 names; the paragraph uses `<name>` placeholders. |
| E4 | D1 needs its own criterion. | **Refuted** (A15, Rule-13): `term-home.jsonld` already decides where a term is defined; it gains the layer as an input and precedence, its two outcomes' conditions name the core and the cabinet layer, and one outcome for the instance, named by Rule-6's own "terms defined elsewhere". |
| E5 | D2 belongs in a new criterion beside `attendance.jsonld`. | **Refuted** (A16): the same criterion gains the four conditions and the span as inputs and two advisory outcomes, `pairs` and `solo`; its precedence says the declaration still decides the route and the conditions only advise the operator's act. |
| E6 | D4 has no prose home in the files the plan named. | **Confirmed, a departure stated**: a criterion's outcome names must appear in its home file, and none of the plan's files states the overhead test; `dyad/playbooks/d-work.md` gains one paragraph after Layers, the place the layers it routes between are defined. Reported in the completion evidence as a departure. |
| E7 | Core code still says `secretary`: `sessions.seat_kind` returns it, and its tests pin it. | **Survives, scoped**: an identifier and a printed value, not a vocabulary term, like the `seat` entity (crosswalk, D6 of #553); renaming it is code, outside this plan, and a candidate for #554's alias removal. |

**Rule-6: every Agent Rule in a changed term's `used by`.**
- `secretary` (3 16), `cos-board` (3 16): removed from this file. Rules 3 and 16 now cite them as the organization
  craft's, by name, and read correctly; the vocabulary guard no longer requires them there.
- No other term changes; the conventions paragraph defines no term. The crosswalk gains one row, "the cos as a mode" → "home follows you" (F2), which maps and defines nothing.

**Pairwise (Rule-5).** Rules 3 and 16 change words only: the session-start bullet and Presence describe the same boards
as before, and Rule-16's reconcile owner is named by charter. No concern moves between Rules; every other pair is
unchanged. No gap is found.

Disposition: see ledger #560.

## Amendment — d-work #564 (2026-11-03: corroboration where the merge ran; the scheduled sweep)
This Rule names the corroboration step that runs its guard in place of the CI job's own step, which corroboration
replaced; the claim, its attacks (attack 9) and the pairwise statements are recorded once, in
`rule-14-system-infrastructure.md`, amendment #564.

Disposition: see ledger #564.
