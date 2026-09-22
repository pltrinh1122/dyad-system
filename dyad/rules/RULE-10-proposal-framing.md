# Rule-10: proposal-framing

**Intent:** Frame every proposal as one path, its strongest counter, a reconciliation, and one `Y/N`.
**Target:** a proposal

## Boundaries (out of scope)
- The counter-prompt forms and which d-work a question belongs to — Rule-3.
- Who answers — Rule-2.
- What was falsified to reach the path — Rule-9.

## Conditions (triggers)
- The Agent asks the Operator for a disposition.
- The Agent recommends among options.

## Form
- One path: the recommended course, concrete enough to be bound to (Rule-3 plan).
- The strongest counter: the best case against it, or another option, stated fairly.
- A reconciliation: why the path holds despite the counter, or what it concedes.
- One `Y/N`, last line, one per reply. "No honest counter" may be stated once, as such; a
  fabricated counter is a breach.
- Under `concise-mode: on` (`preferences-corpus/PREFERENCES.md`) the reply is the only one the
  prompt gets: one synthesized block, emitted when the turn ends — done, or stopped at a
  blocking question (Rule-8) — with no preface and no progress lines before it; the `Y/N` is
  still its last line. Execution longer than a few tool calls is delegated (Rule-3 Scope, the
  `delegation` preference) so the reply is prompt and the Agent stays free; a harness prompt for
  a status mid-turn gets one line, never a second reply. A second reply to one prompt is an
  incident (Rule-3).

## Enforcement
Inference only, stated.

## Provenance
Frame principle promoted by Operator decision, gap E2 (audit 2026-09-12, completeness).
Falsified; see `../falsification/rules/rules-9-10-promotion.md`. Form gains the `concise-mode`
bullet 2026-09-22 (d-work #113): one synthesized reply per prompt under the preference, long
execution delegated; see the same record, amendment #113.

Set: System Requirements.
