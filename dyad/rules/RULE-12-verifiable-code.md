# Rule-12: verifiable code

**Intent:** Choose, among the implementation paths that satisfy a plan, the one that leaves
behind reusable code carrying a mechanical check.
**Target:** an implementation path

## Boundaries (out of scope)
- The package's structure and its tested install — Rule-11.
- What any guard checks — the System Requirements Rule that owns it.
- Importing versus authoring code — Rule-13. Kernel versus library — Rule-14.
- Scope: the plan's (Rule-3). Rule-12 chooses among realizations of the plan; it never widens it.
- The design of a check — mechanical wherever it can be, inference stated where it cannot — and
  where a guard or a projector lives: the sysarch craft's `crafts/sysarch/rules/guards.md` and
  `crafts/sysarch/rules/projection.md`. Rule-12 keeps the sentence Rule-2's Binding relies on:
  code carries a check that runs (#160).
- How the code is written so it stays verifiable — code over inference, the chosen path and its
  reuse yield, the test mapping, the invariant protocol's form and the `assert` ban: the syseng
  craft's `crafts/syseng/rules/verifiable-code.md` and `crafts/syseng/rules/invariants.md` (#162).

## Conditions (triggers)
- A plan admits more than one realization.
- Code is added to the package.
- A check runs by inference where code could run it.

## Properties
1. Code entering the package carries its mechanical check, run in CI; code without a check
   is not verifiable and does not enter. The check a module carries for its own data model is
   its invariant list (vocabulary): a named predicate over the module's constants, listed in
   `INVARIANTS`, run by the runner before any check and reported as `[invariant]`; a false one is
   an incident (Rule-3). The test mapping and the invariant protocol's form are the syseng
   craft's (`crafts/syseng/rules/verifiable-code.md`, `crafts/syseng/rules/invariants.md`); the
   runner runs both.
2. The suite is run by the runner, not by hand. Rule-14 property 3's pre-push path runs it on every
   push whose range touches anything outside `<instance>/d-work/`, so by the time the Agent asks for
   a Done-`Y` the gate has already run what a hand-run would have run. One target — a module, a
   class, a method — is run while fixing it, through `dyad check --tests <target>`, which is the
   same child the runner spawns. A hand-typed `unittest` over a whole test root is not an error and
   nothing refuses it; it is the expensive path, because it does not set the environment the runner
   sets for itself and so pays about three times (120 s against 40 s on the core root, measured in
   `agent-corpus/audits/2026-09-24-performance-bottlenecks.md`), and it re-runs what the gate will
   run again. Which environment and which child: `check_rule_12` and `cmd_tests` in
   `dyad/scripts/package.py`.

## Enforcement
Rule-12 owns its check — package code carries a mechanical check — implemented as a function that
Rule-11's runner (`package.py check`) invokes, `check_rule_12`: the tests pass, one `unittest`
suite per test root (`dyad/tests/`, whose `guards/<corpus>/` subdirectories are packages, and each
Tended craft's `crafts/<craft>/tests/`, discovered by the runner, #155). Which module maps to which test file is the syseng craft's guard
(`crafts/syseng/guards/tests.py`, registry label `syseng/tests`); which module must declare an
invariant and that none uses `assert` is its guard `crafts/syseng/guards/invariants.py`
(`syseng/invariants`); whether every invariant holds is the runner's pass (`dyad/scripts/dyadlib.py`
`check_invariants`, `dyad/scripts/package.py` `invariant_modules`). The runner owns no check
semantics (S4).

## Provenance
Operator rule, 2026-09-13 (Architecture Rule 2). Falsified; see
`../falsification/rules/rule-12-verifiable-code.md`. Design half of p1 restated in
`crafts/sysarch/rules/guards.md` 2026-09-14 (#160); the kernel stays here. Implementation clauses
(p1's implementation half, p3, p4, the test mapping) moved to `crafts/syseng/rules/verifiable-code.md`
2026-09-14 (#162); the one property kept gains the term `invariant` (Rule-6) and cites
`crafts/syseng/rules/invariants.md`. Property 2 added 2026-09-24 (d-work #159): the suite is the
runner's to run — at Rule-14 property 3's push gate, or one target at a time — after an audit
measured 134 hand-runs in one session at about three times the runner's price (#154); see the
same record, amendment #159.

Set: System Requirements (kernel; content: crafts/sysarch/rules/guards.md, crafts/syseng/rules/verifiable-code.md, crafts/syseng/rules/invariants.md).
