# Rule-6: vocabulary

**Intent:** Keep every term used by the Agent Rules defined once, in the vocabulary, and used
consistently by every Agent Rule.
**Target:** the vocabulary (`dyad/vocabulary/VOCABULARY.md`)

## Boundaries (out of scope)
- The shape of a Rule — Rule-4. Relations between Rules — Rule-5 (Rule-6 is *consistent*,
  not *coherent*; see the vocabulary for both).
- Terms defined elsewhere: preference keys (`preferences-corpus/`), Tended Rules' terms
  (`crafts/<craft>/vocabulary/CRAFT.md`, #155). The vocabulary references them, never defines them.
- Prose that uses no defined term.

## Conditions (triggers)
- A term is added, changed or removed: the PR's falsification record names every Agent Rule
  in the term's `used by` column and states that each still reads correctly.
- An Agent Rule is added or edited: any new term it introduces is added to the vocabulary in
  the same d-work (agent-zone PR), and it cites the vocabulary rather than defining inline.
- Every push to `main` and every PR: `dyad/guards/agent/vocabulary.py` runs.
- A craft vocabulary (`crafts/<craft>/vocabulary/CRAFT.md`, a `term | definition | rule` table) is added
  or edited: `vocabulary.py` `check_craft` runs, through the craft guard (`dyad craft check`, Rule-11) —
  well-formed, no term defined twice, every `rule` an existing `rules/<rule>.md` of the craft, no term
  equal to an Agent term (#156).

## Master record
The vocabulary is the only place a term is defined. A Rule may restate a term's operational
consequences (what happens in a state, what an event permits) but not redefine the term.
On divergence the vocabulary wins and the Rule is a bug. A craft term is referenced by the Agent
vocabulary (by craft name, as `<craft>:term`), never defined: a term defined in both is one fault,
reported once by `check_craft`.

## Mechanisms
Rule-6 owns `dyad/guards/agent/vocabulary.py` (agent zone; placed per Rule-11 property 1) and its workflow wrapper
`.github/workflows/dyad-vocabulary.yml` (infra zone; Rule-1). The script checks: the table is well-formed; every `owner` is an existing Rule
or `frame`; no term is defined twice; every term occurs in at least one Agent Rule (no
orphans); every Rule listed in `used by` mentions the term (case-insensitive, emphasis stripped,
across line breaks; I1). Whether a use matches the definition is inference at falsification time.

## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-6-vocabulary.md`.

Set: System Requirements.
