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

## Amendment — d-work #15 (craft-contributed data)
**Claim:** an installed craft may contribute its own `exempt:` rows directly
(`crafts/<craft>/guards/invariants_contrib.txt`, attack 4's mechanism, one craft at a time), so a
craft's own reference code stops depending on a native `crafts/*/…` wildcard glob written by
syseng in its absence.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 15.1 | Attack 4's own `exempt: crafts/*/server/*.py` already covers every craft's server code; nothing needs contributing. | Refuted, scoped | It covers *lan-git's* shape today by a wildcard glob no craft asked for; a craft that ships its own `invariants_contrib.txt` states its own exemption instead of relying on a syseng-authored guess at its layout. No live row moves — this repo has no lan-git craft to migrate (`naming.md`'s amendment, attack 15.1). |
| 15.2 | `scan()`'s two hardcoded `invariants_rules.txt:` message prefixes can just stay; a contributed exempt is close enough to native that misattributing it costs nothing. | Refuted | The whole point of `#15` is that a malformed or stale row names its own author; leaving the prefix hardcoded would blame syseng for a craft's own stale glob, undoing the naming guard's own parallel design in the same d-work. |
| 15.3 | Adding `labels` to `scan()`'s signature changes its contract for every existing caller. | Refuted, tested | `labels: dict[str, str] | None = None` defaults every glob to `"invariants_rules.txt"`, byte-for-byte the prior behaviour; all nine pre-existing `ScanTests`/`LiveTests` cases pass unmodified. |
| 15.4 | Testing this needed only two independent scratch trees — one for the fake craft's `pkg`, one for the files it exempts — the way `naming.md`'s tests already do. | **Confirmed**, then fixed before merge | `invariants.python_files(root, pkg)` derives its *entire* scan tree from `pkg`'s own parent (`crafts_dir(pkg) = pkg.parent / "crafts"`), ignoring `root` outright — unlike `naming.tree_paths`, which scans `root` via `git ls-files` and uses `pkg` only for auxiliary lookups. A `pkg` and a `root` built as two separate temp dirs silently scan an *empty* crafts tree: the first draft of every test here passed by construction, checking nothing. Caught by asserting a specific stale message and getting an unrelated one back. Fixed: one `craft_root` helper builds `pkg` and every scanned file under one shared root. |

Disposition: see ledger #15.

Disposition: see ledger #162.
