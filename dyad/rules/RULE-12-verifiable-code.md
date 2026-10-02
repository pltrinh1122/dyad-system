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
   its invariants (vocabulary), in two lists. The pure ones, listed in `INVARIANTS`, are a
   fail-loud check (vocabulary): the module enforces them at import
   (`dyadlib.enforce(INVARIANTS, __name__)`), so a false one fails every import of the module, and
   nothing switches it off. The ones that read the package tree or load modules, listed in
   `TREE_INVARIANTS`, never run at import. The runner's pass runs both lists before any check and
   reports each module as `[invariant]`; a false invariant is an incident (Rule-3). A fail-loud
   check at a strategic point is that code's mechanical check, and a test that only exercises its
   condition is redundant with it. The lists' form, the placement criterion and the test mapping
   are the syseng craft's (`crafts/syseng/rules/invariants.md`,
   `crafts/syseng/rules/verifiable-code.md`); the runner runs both.
2. The suite is run by the runner, not by hand. Rule-14 property 3's pre-push path runs it on every
   push whose range touches anything outside `<instance>/d-work/`, so by the time the Agent asks for
   a Done-`Y` the gate has already run what a hand-run would have run. That path alone may skip the
   suite when a suite memo on this checkout proves the same tree already passed every root in the
   same environment; `check --evidence` never reads one, so the merge evidence always observes
   (Rule-2, Binding; Rule-14 property 3). That path also skips a test root whose installed tree is
   byte-identical to its craft registry row (Rule-11 property 2) — a Tended craft's root only while
   the core's tree is too — unless the pushed range changes the registry; `check --evidence` runs
   every root. One target — a module, a
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
(`syseng/invariants`); whether every invariant holds is each module's own import for `INVARIANTS`
(`dyad/scripts/dyadlib.py` `enforce`) and the runner's pass for both lists (`dyadlib.check_invariants`,
`dyad/scripts/package.py` `invariant_modules`, where a module whose import fails is one red line). The
runner owns no check semantics (S4).

## Provenance
Operator rule, 2026-09-13 (Architecture Rule 2). Falsified; see
`../falsification/rules/rule-12-verifiable-code.md`. Design half of p1 restated in
`crafts/sysarch/rules/guards.md` 2026-09-14 (#160); the kernel stays here. Implementation clauses
(p1's implementation half, p3, p4, the test mapping) moved to `crafts/syseng/rules/verifiable-code.md`
2026-09-14 (#162); the one property kept gains the term `invariant` (Rule-6) and cites
`crafts/syseng/rules/invariants.md`. Property 2 added 2026-09-24 (d-work #159): the suite is the
runner's to run — at Rule-14 property 3's push gate, or one target at a time — after an audit
measured 134 hand-runs in one session at about three times the runner's price (#154); see the
same record, amendment #159. Property 2 gains the suite memo 2026-09-30 (d-work #199, node N2 for
backlog row #162): 53 of 112 merges pushed a tree `check --evidence` had already passed, and the
push gate ran the suite on it again (#161, C2); see the same record, amendment #199. Property 2
gains the installed-root skip 2026-10-01 (d-work #199, node N5 for backlog row #176): a system that
installs the crafts ran their authoring suites on every push (countersign-system: 494 core tests);
see the same record, amendment #199 (N5). Property 1 gains the fail-loud check 2026-10-02 (d-work
#203): the Operator asked for checks in the code itself, at import or on every use, at strategic
points, in place of the tests that only exercise them; pure `INVARIANTS` are enforced at import and
`TREE_INVARIANTS` stay in the runner's pass; see the same record, amendment #203.

Set: System Requirements (kernel; content: crafts/sysarch/rules/guards.md, crafts/syseng/rules/verifiable-code.md, crafts/syseng/rules/invariants.md).
