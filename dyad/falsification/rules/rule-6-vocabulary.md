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
