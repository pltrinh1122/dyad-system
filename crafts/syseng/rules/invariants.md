# Run-time invariants (syseng craft, Tended rule)

Read by Rule-12's kernel (`dyad/rules/RULE-12-verifiable-code.md`): the core Rule binds *that*
code entering a craft carries its mechanical check and that the runner runs it; this rule is the
form of the check a module carries for its own data model. The Operator's rule, stated at #161:
architectural integrity is validated by invariants that execute in production code, never by
`assert`. Term: `invariant` is an Agent-vocabulary term (owner Rule-12; the kernel and the runner
use it); `assert scan` is this craft's (`../vocabulary/CRAFT.md`). Protocol code: core,
`dyad/scripts/dyadlib.py` (`InvariantError`, `check_invariants`, `contract_invariants`,
`runner_module`) and the runner's pass (`dyad/scripts/package.py`, `invariant_modules`,
`cmd_invariants`). Guard: `../guards/invariants.py` (registry label `syseng/invariants`, entity
`invariant`), data `../guards/invariants_rules.txt`. Skeletons: `../templates/module.py`,
`../templates/test.py`.

## Properties
1. **Every data model declares its invariants as code that runs when the model is used.** A
   module that carries a data model — an upper-case module-level name bound to a tuple, list,
   dict, set or frozenset — exposes `INVARIANTS: list[tuple[str, Callable[[], bool]]]`: the name
   is the architectural fact in words (`transitions-keys-are-states`), the callable a one-line
   predicate over the module's constants (never over the instance corpus). `dyadlib.check_invariants`
   runs every entry sorted by name, raises `InvariantError` naming the false ones (a predicate
   that raises is false) and returns the count. It is called by the runner before any check and
   at the mutating call sites — `dyad dwork new|state` before a row is written, `runbook.run`
   before a command runs or an event is appended — and never at import (plan #162 attack 1:
   `--help`, `--list` and the tests' module loads pay only for a list literal). A module whose
   only constants are strings or regexes is exempt (`HEAD`/`TAIL` HTML, a `SHEBANG`).
2. **Invariants name architectural facts.** The seed list is the runner's pass (`dyad check
   --evidence` prints it): the transition table's closure and `done` terminal, a dataclass's
   fields equal to its `FIELDS`, a register's sources and targets being entity keys, zone
   patterns disjoint, a guard's contract restated (`dyadlib.contract_invariants`, four per guard,
   appended by the runner so no guard repeats them). Each names a fact a guard or a past incident
   relied on (#112, #113, #136, #140, #151).
3. **`assert` is forbidden in craft code outside `tests/`.** An `assert` vanishes under `-O`,
   cannot be listed, projected or reported by name, and stops at the first failure. The guard
   scans `ast.Assert` nodes over every Python file under `dyad/` and `crafts/` whose path has no
   `tests` component — by `ast`, never by grep, so strings, comments and prose never
   false-positive (attack 4). Tests may assert.
4. **Invariants run in the evidence path.** `dyad check`, `dyad check --guards` and therefore
   `dyad check --evidence` print `ok   [invariant] <module> (<n>)` per module, or `FAIL
   [invariant] <module>: <name>` per false name; a FAIL is red but the checks still run, so the
   evidence stays complete. A violated invariant is a red merge (Rule-2 Binding reads the block).
5. **A failed invariant is an incident.** The architecture and the code disagree; the fix is a
   plan, not a patch in place (Rule-3 Incidents).

## The check (what the guard verifies)
`invariants.py`: (i) no `ast.Assert` outside `tests/` under `dyad/` and `crafts/`; (ii) every
module that defines a data-model constant exposes `INVARIANTS`, unless an `exempt:` line of
`invariants_rules.txt` names it with a reason (a reference deployment the runner never loads); (iii)
every entry of every module the runner's pass covers (`package.invariant_modules`) is a
`(str, callable)` pair with a unique kebab-case name. Whether the invariants *hold* is the runner's
pass, not the guard's; whether a fact is *architectural* is inference.
