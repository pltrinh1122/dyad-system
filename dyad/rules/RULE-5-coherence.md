# Rule-5: rule-set coherence

**Intent:** Keep the set of Rules coherent in relationship and orthogonal in concern.
**Target:** the set of Agent Rules — System Requirements, `dyad/rules/` (Rule-4 recognizes them; never enumerated here).

## Boundaries (out of scope)
- The shape of any one Rule — Rule-4.
- Whether a Rule is right — falsification (frame).
- Preferences, principles, audits, the ledger, the vocabulary: not Rules, not members of the set.
- Terminology — Rule-6.
- Tended Rules (Rule-4 Boundaries): a separately contained set. Coherence with Agent Rules
  is not required. Whether a rule is Tended or Agent is Rule-4's classification (ledger #52).

## Conditions (triggers)
- A Rule is added or edited: the PR's falsification record states, for every other Rule,
  that the pair is coherent and orthogonal, or names the gap.
- The operator prompts a sweep of the set.
- A falsification record or audit finds an overlap or a contradiction.

## Definitions
*Coherent* and *orthogonal* are defined in the vocabulary (`../vocabulary/VOCABULARY.md`,
Rule-6). Shared ownership of a concern is a gap.

## Sets
The Rules have three homes. **System Requirements** — the core craft's Agent Rules, the kernels of
Rules 11, 12, 14, 16 and 20 included; a kernel is core because Rule-2's Binding or Rule-3's
completion evidence relies on it (the process kernel of a Rule that splits — 8, 18, 19 per #157;
11, 12, 14, 16, 20 per #158/#160 — stays here as an Agent Rule). **System Architecture** — the
`sysarch` craft's rules, `crafts/sysarch/rules/`: Tended (Rule-4 Boundaries), swept by the craft's
own form, not members of this set (#160); Rule-13 keeps that `Set:` line in the core pending #162.
Host and craft practice — `workstation-corpus/rules/`, `crafts/sysadmin/rules/`: Tended likewise.
This Rule sweeps the core craft's Rules; a Tended craft sweeps its own by its own form.

## Enforcement
Inference only, stated. No script can decide coherence or orthogonality; the Rule-4 block
gives inference its handle (Boundaries name the neighbours). Sweeps are recorded in
`agent-corpus/audits/`.

## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-5-coherence.md`.

Set: System Requirements.
