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

## Amendment — d-work #203 (import-time enforcement, the strategic-point criterion)
**Claim:** a model module's pure invariants are enforced in the code itself, at import, with no
off-switch; the predicates that read the tree or load modules move to `TREE_INVARIANTS` and stay in
the runner's pass; a fail-loud check goes only at a strategic point — a boundary, a state
transition or an impossible condition, passed once per process or rarely — and a test that only
exercises such a condition is replaced by it. Operator's words, provenance #203 entries 2–3.
Plan: `agent-corpus/d-work/plans/203.md` (attacks A1–A11; this table is the craft's share).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 203.1 | This reverses #162 attack 1 (`../syseng-extraction.md`, confirmed then): import-time invariants slow every command and break `--help`, `--list`, the projectors' imports and the tests' loads. | Survives, scoped | Only the pure list runs at import. The cost #162 measured is the I/O predicates (the plan: all 127 together 10.3 ms warm, the references seven and the register ones dominating); they are the `TREE_INVARIANTS`, kept out by check (v). `--help` and `--list` break only when an invariant is false, which is the loudness asked for. `../syseng-extraction.md` attack 1 is superseded by this row for the pure list; its survivor still holds for the tree list. |
| 203.2 | "Pure" cannot be checked mechanically: an audit hook sees only what CPython audits. | **Confirmed** on the first draft, then narrowed | The hook alone flagged 8 of the 12 impure predicates (seven of `agent/references` and the entities projector's register); `references`' `resolver-shape`, `package`'s `templates-exist` and `projector-modules-exist-with-main` and `craft`'s `core-name-is-the-guards` passed, because `Path.is_file` is a bare `os.stat` and `dyadlib.load_module` of a module already loaded opens nothing — yet both read the disk in a fresh process at import. Survivor: the child also wraps `os.stat`/`os.lstat`, `os.environ` reads and `dyadlib.load_module`; all 12 are now flagged — one more than the plan named: `resolver-shape` stats a guard file, and the tests pin open, stat, listdir and environment. Residue, inference: a C-level `getenv`, a value read at import and compared later. |
| 203.3 | Run (v) in the runner's own process. | Refuted | An audit hook cannot be removed (`sys.addaudithook`); it would sit on every later event of `dyad check`. One child per check: about 0.5 s of the guard's 1.1 s, measured (check (iv) 0.1 s). |
| 203.4 | A check at import can break imports where it is installed, and a false invariant in `dyadlib` kills every `dyad` command, the `dwork` that would record the incident included. | **Confirmed**, conceded (plan A7) | A pure predicate over literals has one value on every host, so a false one cannot pass a green evidence block and reach an install: the evidence's own import would have raised. For the runner's own modules the outcome is fail-closed — `rc ≠ 0`, one `InvariantError` line, no block, which Rule-2's Binding reads as an absent check — and the incident is recorded by hand. p4's "the evidence stays complete" becomes "complete except when the runner itself cannot import". |
| 203.5 | An off-switch (an environment knob) would let an operating system recover from 203.4. | Refuted | A switch turns fail-loud into fail-optional, and an evidence block made with it off proves nothing. The recovery is the fix in a plan (p5), as for any false invariant. p1 states "no off-switch". |
| 203.6 | Check (iv) as a failure now turns `main` red: `dyadlib.enforce` does not exist until the core's node (P2). | **Confirmed** | (iv) warns. While `dyadlib.enforce` is absent it is one summary line (40 modules: 22 under `dyad/`, 18 under `crafts/`; the template `module.py` already complies), never a crash and never 40 lines; once it exists, one line per core module and one per craft. P3 flips it by data (`ENFORCE_FAILS_UNDER = ("dyad",)`), guarded by the invariant `enforce-fails-only-under-the-core`. |
| 203.7 | Check (v) as "any event fails" turns `main` red the same way: the twelve I/O predicates are in `INVARIANTS` today. | **Confirmed**; differs from the plan's wording | Severity follows enforcement: an I/O predicate fails in a module that calls `enforce` (it would do I/O in every process) and warns in one that does not yet. P2 moves the twelve and adds `enforce` to every core module, after which every core finding fails with no further flip; a craft module warns until it adopts `enforce`, as (iv) does. |
| 203.8 | A grep for `dyadlib.enforce(` passes a call inside a function or an `if`, or one placed before a later `INVARIANTS.append`. | **Confirmed** | (iv) reads `ast`: only a module-level expression statement counts, its first argument the name `INVARIANTS`, its line after the list's last binding (`=`, `+=`, `.append`, `.extend`). Tested. |
| 203.9 | Deleting the per-module hold test loses the only red line for a false invariant in a module the pass does not cover (`livetest`, `incidents`). | Refuted | The test module imports the module; the import raises `InvariantError`, and `unittest` reports the module's load as an error, red. `verifiable-code.md` p5: the import is the assertion. |
| 203.10 | "Strategic point" is a judgment; the criterion could license deleting any test. | Survives, scoped | It is inference and says so. It is bounded twice: the point (boundary, transition, impossible condition), and the frequency (once per process or rarely, never per item); a behaviour test never converts, and `verifiable-code.md` p7's floor keeps the validation itself. |
| 203.11 | Easy agreement: the template's `require_transition` is cheap, so it may sit anywhere. | Refuted | Cost is not the criterion; place is. It is called once, before the one write, never on the read path, so a refusal writes nothing by construction — the shape plan #203's N3 gives `dyadlib.write_row`. |

**Pairwise (Rule-5 form, the craft's own set and the kernels it is read by).**
- `failure.md`: p1's ladder is unchanged — an import-time invariant is still the *declaration* rung,
  now run at declaration too. **Gap, named:** p3, *fatal is not early* ("a run completes and reports
  every fault"), now has one exception, 203.4's runner self-import, which `failure.md` does not state.
  `failure.md` is not among plan #203's files; reported for the Operator, not edited here.
- `verifiable-code.md`: p5 amended in the same d-work (the import is the assertion); p4's mapping
  untouched; p7's floor cited from p1, not restated. Coherent, orthogonal.
- `naming.md`: its protocol row (`INVARIANTS`, `check_invariants`, `InvariantError`) does not yet
  name `TREE_INVARIANTS` or `enforce`. Not a contradiction — the row lists names it checks — but a gap
  for the node that ships `enforce` (the symbol line for `dyadlib.py` would fail before then).
- `imports.md`: the child is `sys.executable` (Python, a kernel row) and `json`/`subprocess` are
  stdlib. Coherent.
- `determinism.md`: the child's report is sorted; the guard's lines are deterministic over one tree.
  `idempotence.md`, `host-facts.md`: no shared concern.
- Core kernels: Rule-12 p1 says the runner runs the invariants; this rule adds the import, and P2
  amends Rule-12 p1 (agent zone) to say so — between P1 and P2 the craft states more than the kernel,
  never the contrary. Rule-2's Binding reads the evidence block, whose absence 203.4 makes fail-closed.
  Rule-11's guard contract is unchanged (entity, corpus, fields). Rule-14: no new World row.

Disposition: see ledger #203.
