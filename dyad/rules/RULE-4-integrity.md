# Rule-4: rule integrity

**Intent:** Declare every Rule's intent, target, boundaries and conditions in a fixed block
that can be counted.
**Target:** an Agent Rule (vocabulary; a file in `dyad/rules/`). "Rule" in every Rule means Agent Rule.

## Boundaries (out of scope)
- The operating-frame principles in `dyad/CLAUDE.md`, preferences, audits,
  falsification records, the d-work ledger and the vocabulary are not Rules and carry no block.
- Whether a Rule is *wise* — Rule-4 checks shape, not content. Content is falsified (frame).
- Relations between Rules (coherence, orthogonality) — Rule-5.
- Tended Rules (vocabulary): a separately contained set — in `workstation-corpus/rules/` or in a
  Tended craft's `rules/` — no block, no check here. Guard: a rule that binds the Agent's process
  is an Agent Rule wherever it is written and belongs in the core craft, `dyad/rules/` (ledger
  #52; #153 attack 11); the craft guard warns on Agent-process tokens in a Tended craft's rules
  (`dyad/guards/agent/rules.py` `check_tended`, data `dyad/guards/craft/crafts_rules.txt`
  `agent-token:` lines; README exempt); the classification stays inference (#156).
- Terminology — Rule-6. The vocabulary defines Agent Rule and Tended Rule; Rule-4 classifies.

## Conditions (triggers)
- A Rule is added or edited: the PR must leave the block conforming.
- Once, retroactively, for Rules 1–3 (ledger #49).
- Every push to `main` and every PR: `dyad/guards/agent/rules.py` runs.

## Criteria
Each Rule, immediately after its title:
1. `**Intent:**` — exactly one, one sentence, expressed as an imperative (5a, 5b).
2. `**Target:**` — exactly one noun phrase naming the single kind of thing the Rule governs (5c).
3. `## Boundaries (out of scope)` — one or more bullets (5d).
4. `## Conditions (triggers)` — one or more bullets naming when the Rule applies (5e).
Clarity (criteria 1–4 of the operator's prompt) and the imperative mood (5b) are judged by
inference at falsification time; counts (5a, 5c, 5d, 5e) are checked mechanically.

## Mechanisms
Rule-4 owns `dyad/guards/agent/rules.py` (agent zone; placed per Rule-11 property 1) and its workflow wrapper
`.github/workflows/dyad-rule-integrity.yml` (infra zone; Rule-1). The script reads every `dyad/rules/RULE-*.md` and fails on any count miss (A2: Rule-1
is a file like the others).

## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-4-integrity.md`.

Set: System Requirements.
