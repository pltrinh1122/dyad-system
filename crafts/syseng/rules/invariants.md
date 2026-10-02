# Run-time invariants (syseng craft, Tended rule)

Read by Rule-12's kernel (`dyad/rules/RULE-12-verifiable-code.md`): the core Rule binds *that*
code entering a craft carries its mechanical check and that the runner runs it; this rule is the
form of the check a module carries for its own data model. The Operator's rule, stated at #161:
architectural integrity is validated by invariants that execute in production code, never by
`assert`. Term: `invariant` is an Agent-vocabulary term (owner Rule-12; the kernel and the runner
use it); `assert scan` is this craft's (`../vocabulary/CRAFT.md`). Protocol code: core,
`dyad/scripts/dyadlib.py` (`InvariantError`, `enforce`, `check_invariants`, `contract_invariants`,
`runner_module`; `enforce` ships with d-work #203's core node P2, and until it does only this
craft's guard warns) and the runner's pass (`dyad/scripts/package.py`, `invariant_modules`,
`cmd_invariants`). Guard: `../guards/invariants.py` (registry label `syseng/invariants`, entity
`invariant`), data `../guards/invariants_rules.txt`. Skeletons: `../templates/module.py`,
`../templates/test.py`.

## Properties
1. **Every data model declares its invariants as code that fails loud where the model is used.** A
   module that carries a data model — an upper-case module-level name bound to a tuple, list, dict,
   set or frozenset — declares its invariants in two lists of `(name, predicate)` pairs
   (`list[tuple[str, Callable[[], bool]]]`). The name is the architectural fact in words
   (`transitions-keys-are-states`), unique across both lists; the predicate is one line.
   - `INVARIANTS` holds the **pure** predicates: over the module's own literals only — no
     filesystem, git, network, child process, module loading or environment read — so a predicate
     has the same value on every host. The module calls `dyadlib.enforce(INVARIANTS, __name__)` at
     module level, after the list's last binding: every entry runs at import and a false one raises
     `InvariantError` naming every false name (a predicate that raises is false). There is no
     off-switch — no environment knob, flag or `-O` path skips it, since a switch would turn
     fail-loud into fail-optional.
   - `TREE_INVARIANTS` holds the predicates that read the package tree or load modules (a register
     whose targets are guard files, a template that must exist). They never run at import: the
     runner's pass runs them beside `INVARIANTS` (p4), and `dyadlib.check_invariants` still runs a
     module's lists at the mutating call sites — `dyad dwork new|state` before a row is written,
     `runbook.run` before a command runs or an event is appended.
   A module whose only constants are strings or regexes is exempt (`HEAD`/`TAIL` HTML, a `SHEBANG`).
   Import-time enforcement reverses #162 attack 1's "never at import" for the pure list only
   (amendment #203): the predicates that made import slow are the tree ones, and they stay out.

   **Where a fail-loud check goes.** A fail-loud check — an import-time invariant, or a function
   that raises before the one write it guards (the template's `require_transition`) — belongs only
   at a strategic point: a **boundary** (a dispatch table, Operator input entering a store), a
   **state transition**, or a condition that should be **impossible** (a parse contract that
   contradicts itself, a transition table that is not closed). It sits where control passes once
   per process (at import) or rarely (once per disposition, once before a host command), never on
   a per-item path (per row, per file, per path). A test that only exercises such a condition is
   redundant with the check and is replaced by it; a test that verifies behaviour — outputs,
   messages, side effects, a guard's verdict over a fixture — stays a test, and input validation at
   a trust boundary stays on the floor (`verifiable-code.md` p7: the validation is kept; only its
   restating test goes). The Operator's words (#203): *"strategic use is required. for example,
   boundary-checking or state transition, "impossible conditions" that a current test is
   exercising would no longer need to be tested."* Whether a point is strategic is inference.
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
4. **Invariants run in the evidence path, and a false one surfaces where it is enforced.** `dyad
   check`, `dyad check --guards` and therefore `dyad check --evidence` print `ok   [invariant]
   <module> (<n>)` per module over both lists, or `FAIL [invariant] <module>: <name>` per false
   name. A false `INVARIANTS` entry surfaces first at import: a guard or pass module whose import
   raises is one red line (the registry's `does not load`, or the pass's FAIL for that module) and
   every other check still runs, so the evidence stays complete **except when the runner itself
   cannot import**. Conceded, fail-closed (amendment #203, attack 203.4): a false invariant in the
   runner's own modules — `dyadlib`, `package` — stops every `dyad` command, `dwork` included, with
   `rc ≠ 0`, one `InvariantError` line on stderr and no evidence block. Rule-2's Binding reads an
   absent block as an absent check, so nothing merges on it, and the incident is recorded by hand.
   A violated invariant is a red merge (Rule-2 Binding reads the block).
5. **A failed invariant is an incident.** The architecture and the code disagree; the fix is a
   plan, not a patch in place (Rule-3 Incidents).

## The check (what the guard verifies)
`invariants.py`: (i) no `ast.Assert` outside `tests/` under `dyad/` and `crafts/`; (ii) every
module that defines a data-model constant exposes `INVARIANTS` (or `TREE_INVARIANTS`), unless an
`exempt:` line of `invariants_rules.txt` names it with a reason (a reference deployment the runner
never loads); (iii) every entry of both lists of every module the runner's pass covers
(`package.invariant_modules`) is a `(str, callable)` pair with a kebab-case name unique across the
two; (iv) every module outside `tests/` that declares `INVARIANTS` calls
`dyadlib.enforce(INVARIANTS, __name__)` as a module-level statement after the list's last binding,
read by `ast` — a warning until d-work #203's P3 names `dyad` in `ENFORCE_FAILS_UNDER`, then a
failure under `dyad/`; a craft's modules stay a warning, one line per craft, until a craft
follow-up; while `dyadlib.enforce` does not exist it is one summary warning; (v) one child process
imports every module of the pass and runs each `INVARIANTS` predicate under a `sys.addaudithook`,
with wrappers for what raises no audit event (`os.stat`, an `os.environ` read, a by-path load of
a module already loaded): a predicate that opens, stats, lists, spawns, connects, reads the
environment or loads a module fails in a module that enforces at import and warns in one that does
not yet — "move it to `TREE_INVARIANTS`". What neither the hook nor a wrapper sees — a C-level
`getenv`, a value read at import and then compared — is inference, stated. Whether the invariants
*hold* is the runner's pass, not the guard's; whether a fact is *architectural*, and whether a point
is *strategic* (p1), is inference.

## Craft contribution
An `exempt:` line for a module a craft not installed here would ship (`crafts/*/server/*.py`, a
reference deployment's own code) already warns rather than fails under `crafts/` (dyad-system #1);
that stays. A craft that *is* installed may also ship its own exemptions directly:
`crafts/<craft>/guards/invariants_contrib.txt`, the same `exempt: <glob> # <reason>` line format as
`invariants_rules.txt`, discovered from every installed craft (`invariants.contrib_exemptions`) and
merged into the scan. A malformed or stale contributed line is reported naming that craft's own
file, never `invariants_rules.txt` — the same protocol `naming.md`'s Craft contribution section
states for the naming guard, and this rule's own first worked instance of it (d-work #15).
