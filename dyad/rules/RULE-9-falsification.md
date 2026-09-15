# Rule-9: falsification

**Intent:** Falsify every claim before it is encoded in a Rule, a plan, a preference or a verdict.
**Target:** a claim

## Boundaries (out of scope)
- A disposition is not a claim. The Agent challenges before the Operator disposes and executes
  after; it never falsifies a `Y` (Rule-2).
- The shape of a Rule — Rule-4; relations — Rule-5; terms — Rule-6; host actions — Rule-8.
- How a proposal is framed once the survivor is known — Rule-10.

## Conditions (triggers)
- An Operator prompt asserts or proposes a claim that a Rule, plan, preference or verdict
  would encode.
- The Agent is about to plan (Rule-3: the plan is falsified first).
- An audit or sweep surfaces a claim.
- Easy agreement: when the Agent agrees with a claim on first reading, at least one attack
  is pushed to *confirmed* or *refuted* before the claim is accepted.

## Form
- A falsification record in `agent-corpus/falsification/`: a table of attack, result
  (confirmed / refuted / survives, scoped), survivor. Only survivors are implemented.
- "No attack found" is permitted only by naming what was tried.
- The record is disposed by the Done-`Y` of its d-work (Rule-2); its Disposition line says so
  by reference.

## Enforcement
Inference only, stated. Mechanically: a PR that edits a Rule without a record is a Rule-5
breach (the pairwise statement lives in the record); nothing else is checked.

## Provenance
Frame principle promoted by Operator decision, gap E2 (audit 2026-09-12, completeness).
Falsified; see `../falsification/rules/rules-9-10-promotion.md`.

Set: System Requirements.
