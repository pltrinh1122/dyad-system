# Fail early and loud (syseng craft, Tended rule)

Read by Rule-12's kernel (`dyad/rules/RULE-12-verifiable-code.md`): the core Rule binds *that* code
entering a craft carries a mechanical check and that the runner runs it; this rule is the stance
that decides **where** such a check belongs and **what a run does** when one fires. The Operator's
rule, stated at d-work #27: systems should fail early and fail loud. Nearest neighbour:
`invariants.md`, which is this stance's first and sharpest instance. Home decided by d-work #35 —
the craft boundary, not the word *architecture*: two of the three properties below are run-time
behaviour and the third places a *detection*, not a file, so this belongs beside the instruments it
governs rather than in the sysarch craft with the layout rules. Terms: none new; the words are
`../vocabulary/CRAFT.md`'s and `dyad/vocabulary/VOCABULARY.md`'s. No guard of its own — see *What is not
checked*.

## Properties

1. **Early is a place, not a moment.** A fault is detected where it is first *knowable*, as high as
   it goes on this ladder:

   | rung | what runs there | example in this tree |
   |------|-----------------|----------------------|
   | **declaration** | a predicate over a module's own constants, before any check | `INVARIANTS` (`invariants.md` p1) |
   | **transaction** | a hook, before the commit or the push | `dyad/hooks/pre-commit`, `pre-push` |
   | **run** | a guard over the tree | every `check_package` |
   | **use** | the call site | an exception where the value is read |

   A plan that adds a check names the rung it chose and why the rung above could not hold it. The
   worked example is d-work #24: the broken `pre-commit` was perfectly loud at *use* — exit 126,
   `Permission denied` — but the fault was introduced by a mode sweep and was knowable at
   *declaration*, so it survived a whole d-work cycle unnoticed. d-work #25 is the same shape one
   level down: a verb rename is knowable at declaration, and until #25 nothing declared the verbs.

2. **Loud is named and attributable.** Every fault prints a line naming itself — and so does every
   check that was *skipped*, with its reason. The forms already in use are the standard:
   `FAIL [invariant] <module>: <name>`, `FAIL [<label>]: <what>: <where>`, `warn <kind>: … inference`,
   `skip <kind>: <reason>`. A mechanism that cannot check something says so on its own line; silence
   is never a pass. This is what makes a check's absence visible in the evidence block, which is why
   Rule-2's Binding can read that block at all.

3. **Fatal is not early.** A run completes and reports every fault it found. "Stops at the first
   failure" is refused — it is one of the stated reasons `invariants.md` p3 bans `assert`, and p4
   says it plainly of the invariant pass: *a FAIL is red but the checks still run*. "Cannot be
   checked here" stays a printed skip, never a failure: a fresh install with no instance and no
   Tended craft is green, by Rule-11 p5, Rule-20 p2 and Rule-11 p7's missing-`BUNDLE.md` skip.
   Loud and fatal are independent axes; this rule raises the first and leaves the second alone.

## Severity is not this rule's to set

Per-entity severity stays with the Rule that owns the entity: Rule-20 p2 for a reference, Rule-11
p7 for the bundle, Rule-7 for a missing provenance record ("a red `main` is the wrong way to learn
that"). This rule states the stance and defers every severity decision by name. If it ever decides
one, it has taken another Rule's concern.

## What is not checked

Nothing here is mechanical, and that is the honest cost rather than an oversight. It is a design
stance, in the manner of the sysarch craft's `projection.md` ("whether a surface is legible … is
inference"). Its bite is that plans cite it and it names the ladder that decides where a future
check belongs. Making it mechanical means a guard per instrument — never a checker for a stance.

## Provenance
Operator prompt, 2026-09-16 (d-work #27, plan `agent-corpus/d-work/plans/27.md`). Falsified there
and in d-work #33, a concurrent session's independent attack on the same claim; home moved from the
sysarch craft to this one by d-work #35, with #33's contrary reading recorded as the counter.
