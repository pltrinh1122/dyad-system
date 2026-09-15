# Falsification record — syseng craft rule `invariants.md` (d-work #162)

**Claim:** Architectural integrity is validated by invariants that execute in production code, never by `assert` (#161).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A predicate that raises is silently green. | **Confirmed** | `check_invariants` counts a raising predicate as false (`test_failed_invariants_raise_with_names_sorted`). |
| 2 | A guard can declare `INVARIANTS = {...}` or a 3-tuple and the pass accepts it. | **Confirmed** | The guard's (iii) fails a non-list, a non-pair, a non-kebab or a duplicate name (`EntryTests`). |
| 3 | Requiring `INVARIANTS` of every module with an upper-case literal catches HTML `HEAD`, a `SHEBANG`, a regex. | Refuted | Only collection literals and constructors count (`model_constants`); strings and regexes are exempt by construction. |
| 4 | The reference deployment (`server/receiver.py`) carries a table the runner never loads; demanding `INVARIANTS` there is theatre. | **Confirmed** | `exempt: crafts/*/server/*.py # …` with its reason; a stale exempt line fails. |
| 5 | The runner's own module cannot be reached from a guard without a second import of `package.py`. | **Confirmed** | `dyadlib.runner_module`: the running `__main__` or the imported module by `__file__`, else loaded once as `package`. |

Cut from: #161's five properties (new text); the protocol from plan #162 (b).

Disposition: see ledger #162.
