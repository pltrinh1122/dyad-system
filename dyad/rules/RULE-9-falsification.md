# Rule-9: falsification

**Intent:** Falsify every claim before it is encoded in a Rule, a plan, a preference or a verdict.
**Target:** a claim

## Boundaries (out of scope)
- A disposition is not a claim. The agent challenges before the operator disposes and executes
  after; it never falsifies a `Y` (Rule-2).
- The shape of a Rule — Rule-4; relations — Rule-5; terms — Rule-6; host actions — Rule-8.
- How a proposal is framed once the survivor is known — Rule-10.

## Conditions (triggers)
- An operator prompt asserts or proposes a claim that a Rule, plan, preference or verdict
  would encode.
- The agent is about to plan (Rule-3: the plan is falsified first).
- An audit or sweep surfaces a claim.
- Easy agreement: when the agent agrees with a claim on first reading, at least one attack
  is pushed to *confirmed* or *refuted* before the claim is accepted.

## Form
- A falsification record in `agent-corpus/falsification/`: a table of attack, result
  (confirmed / refuted / survives, scoped), survivor. Only survivors are implemented.
- A result reads one way only (`dyad/dmc/attack-result.jsonld`, #644): confirmed means the attack holds, and the
  claim falls as attacked; refuted means the attack fails, and the claim stands against it; survives means the claim
  survives the attack, scoped or not.
- "No attack found" is permitted only by naming what was tried.
- The record is disposed by the done-`Y` of its d-work (Rule-2); its Disposition line says so
  by reference.

## Enforcement
Inference only, stated. Mechanically: a PR that edits a Rule without a record is a Rule-5
breach (the pairwise statement lives in the record); nothing else is checked.

## Provenance
Frame principle promoted by operator decision, gap E2 (audit 2026-09-12, completeness).
Falsified; see `../falsification/rules/rules-9-10-promotion.md`. Operator and agent are lowercase in prose and done-`Y` replaces Done-`Y`, 2026-11-02
(d-work #553): the dyad-native terms; see `../falsification/rules/rule-6-vocabulary.md`, amendment #553 (part D). Form gains
the line saying how each result reads 2026-11-08 (d-work #644): the blind precedent test of plan #644 found the
outcome names read two ways, of the attack or of the claim, so the record names them attack holds, attack fails and
claim survives; see `../falsification/rules/rule-3-d-work.md`, amendment #644.

Set: System Requirements.
