# Verifiable code (syseng craft, Tended rule)

Read by Rule-12's kernel (`dyad/rules/RULE-12-verifiable-code.md`): the core keeps one property —
*"Code entering the package carries its mechanical check, run in CI; code without a check is not
verifiable and does not enter."* — and the sentence that the mapping and the invariant protocol
are this craft's while the runner runs both. Text cut from Rule-12 by d-work #162 (plan (a)3).
Terms (`implementation path`, `mechanical check`, arriving from the core vocabulary):
`../vocabulary/CRAFT.md`. Guard: `../guards/tests.py` (registry label `syseng/tests`, entity `test`).

## Properties
1. **Code over inference.** *"Prefer code over inference wherever the check can be mechanical;
   what cannot be checked mechanically stays inference and says so."* (Rule-12 p1 as cut.)
2. **The chosen path is named.** *"A plan with alternatives names the chosen path and what it
   yields for reuse."* (Rule-12 p3.)
3. **Reuse yield is scoped.** *"Reuse yield is judged within the plan's scope; refactoring beyond
   it is a new plan."* (Rule-12 p4.)
4. **The test mapping.** From Rule-12's Enforcement as cut: *"`check_rule_12`: every Python file in
   `dyad/scripts/` has `dyad/tests/test_<name>.py` and the tests pass"*, with the #151 amendment
   *"maps `dyad/guards/<corpus>/<entity>.py` → `dyad/tests/guards/<corpus>/test_<entity>.py`"* and
   the #155/#160 widening to a Tended craft: `crafts/<craft>/guards/<entity>.py` →
   `crafts/<craft>/tests/guards/test_<entity>.py`; `crafts/<craft>/projectors/<name>.py` and
   `crafts/<craft>/scripts/<name>.py` → `crafts/<craft>/tests/test_<name>.py`. `package.py` and
   `_`-prefixed modules are exempt. The mapping is one-way: a test without a module of that name
   is legal (`dyad/tests/test_dyadlib_rows.py`). The runner's `check_rule_12` keeps "run the tests"
   (discovery of the test roots stays the runner's); this craft's `tests.py` keeps "every module
   has its test at the mapped path" — two predicates, two owners (plan #162 attack 7).
5. **A model's own check is an invariant.** The check a module carries for its constants is its
   `INVARIANTS` list (`invariants.md`); a unit test asserts once that every invariant holds, so the
   predicate is written once (attack 2).
6. **A live test states its empty-instance behaviour.** A *live test* reads the system it runs in —
   the instance's stores, or which Tended crafts are installed — instead of a fixture it builds. It
   states what it does when that store is empty or that craft is absent: it asserts the *documented*
   empty behaviour, or it skips with a stated reason. `dyad/scripts/livetest.py` is the one place that
   statement is written (`store_empty`, `instance_is_empty`, `LiveCase.require_store | require_instance
   | require_craft | require_guard`); a skip carries `empty instance` or `absent craft` and `unittest`
   prints and counts it, so the runner's per-suite line (`Ran N tests … OK (skipped=k)`) shows how much
   of a suite a fresh install turned off. Asserting is preferred wherever the code documents a
   behaviour (`dyad ledger` renders a header-only view; the events projection says "No events recorded
   yet"; the ERD omits the section of a kind with no entity). A live test that instead asserts *this*
   workstation's shape is a false failure in every install — the reason `dyad check` had never been
   green in a scratch install (d-work #171).

## Inference, stated
Whether a test is *adequate* is inference at falsification time; the guard checks presence at the
mapped path and the runner checks that the suites pass. Property 6 is inference too: `livetest` gives
the statement one form and `test_livetest.py` checks that form, but whether a given live test needs a
skip or can assert the empty case is read, not computed. The skip count in the runner's per-suite line
is the standing evidence: a live suite that turned itself off cannot do so silently.
