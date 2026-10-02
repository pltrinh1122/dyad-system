# Test reduction — what the six nodes of #203 removed, and what it cost (2026-10-02)

*d-work #203, node M, plan `agent-corpus/d-work/plans/203.md` (the M row; Falsification A1, A6).
Measured 2026-10-02 by a delegated sub-agent in throwaway clones under the session scratchpad.
Nothing in the working repo was touched except this file, and no ref outside the clones moved. The
raw per-run data (`out/runs.tsv`, `out/runs2.tsv`, `out/imp.tsv`, one log per run and the loader
counts per node) is session-local, not corpus, and goes with the container. Detects and counts;
disposes nothing. Each follow-up below is proposed as a backlog row and none is opened.*

**§0, carried from `2026-09-25-optimization-opportunities.md`: an absolute second is a property of
one machine and one day; only a ratio travels.** The absolutes are printed so the ratios can be
recomputed. **§ method, carried from `2026-09-29-bytecode-retention-profile.md` and
`2026-09-30-test-performance-refactor.md`: a second, independently built copy of identical code is
the control**, and AFTER2/AFTER is the noise floor.

## Method
Three clones, each made with `git clone --no-hardlinks /home/user/dyad-system`, then
`git config core.hooksPath dyad/hooks`, then the git-ignored
`agent-corpus/provenance_legacy.local.txt` copied in (byte-identical to the working repo's):
- **BASE** at `8dc883c`, the plan's base commit;
- **AFTER** at `fe9bc2d`, the head of `origin/dwork-203-n3`, which carries the whole stack
  N1 → N2 → P1 → P2 → P3 → N3 (PRs #248, #249, #250, #251, #252, #253);
- **AFTER2**, a second clone of `fe9bc2d` built independently: the control.

In each clone `refs/remotes/origin/main` was set to `HEAD~1` before (b), as the #199 M audit did,
so `--evidence` judges a non-empty range. Every clone stayed clean (`dirty=no` in every block).

Only the runner's own commands were used (Rule-12 p2):
- **(a)** `dyad/bin/dyad check --tests dyad/tests` — the core root, in the runner's child and
  environment. The entrypoint resolves `python3.13` (3.13.12) through `dyad/bin/dyad-python`;
- **(b)** `python3.12 dyad/scripts/package.py check --evidence` (3.12.3) — every root, every guard,
  the invariant pass;
- **(c)** the import cost of `import dyadlib, package` under `python3.12`, timed in-process with
  `perf_counter` from the clone root, one discarded warm-up per clone, then n = 5.

n = 3 for (a) and (b), interleaved by act, the clone order rotated each round: B·A·A2, A·A2·B,
A2·B·A. (c) used the same rotation over five rounds. The 1-minute load was recorded before every
run: 0.15 to 1.11 for (a)/(b), 0.74 to 0.76 for (c). `/tmp/dyad-floor-*` stayed at 1,712 before and
after every run (BASE postdates #199's N3b leak fix).

A second phase, not in the brief, was added to attribute (b)'s rise (see Results): **(d)**
`dyad check --guards` on an empty range (`origin/main := HEAD`, so the suite is skipped and every
guard runs) and **(e)** `dyad check --tests crafts/syseng/tests`, n = 3 each, same rotation.

`Ran` per module comes from `unittest` discovery without running (the loader's count, as the plan's
inventory did), in the BASE and AFTER clones and, for the per-node table, in a fourth throwaway
clone checked out at each node head in turn. Per-root `Ran` is read from the evidence blocks.

**Environment.** 4 CPUs, 15 GB, kernel 6.18.44-fc-v51. Every exit code of (a), (b) and (e) was 0;
(d) exits 1 at BASE and AFTER alike on the known `agent/prs` empty-range FAIL (#199 M audit,
finding 10), and no other line failed.

## Results

### `Ran` per root (from the evidence blocks)
| root | BASE | AFTER | Δ | plan |
|------|-----:|------:|--:|------|
| `dyad/tests` | 634 | **584** | **−50** | −51 (634 → 583) |
| `crafts/syseng/tests` | 53 | 62 | +9 | "+k" (P1's guard cases) |
| `crafts/sysadmin/tests` | 94 | 94 | 0 | 0 |
| `crafts/sysarch/tests` | 89 | 89 | 0 | 0 |
| `crafts/countersign/tests` | 40 | 40 | 0 | 0 |
| `crafts/disclosure/tests` | 35 | 35 | 0 | 0 |
| total (evidence) | 945 | **904** | −41 | |

### `Ran` per node, core root (loader counts at each node head)
| node | PR | head | `Ran` after | Δ observed | Δ planned | Δ the PR states |
|------|----|------|-----:|-----:|-----:|-----:|
| BASE | — | `8dc883c` | 634 | | | |
| N1 | #248 | `99a7b94` | 633 | −1 | −1 | −1 |
| N2 | #249 | `885fcaa` | 594 | **−39** | −40 | −39 |
| P1 | #250 | `ce86a44` | 594 | 0 | 0 (syseng +k) | 0 (syseng 53 → 62) |
| P2 | #251 | `8494fe2` | 596 | +2 | +2 | +2 |
| P3 | #252 | `ce9f9ff` | 596 | 0 | 0 | 0 |
| N3 | #253 | `fe9bc2d` | 584 | −12 | −12 | −12 |
| **sum** | | | | **−50** | **−51** | −50 |

**Why 584 and not 583.** The whole difference of one is N2's. The plan counted 39 methods in
channel 1 as `Ran` −40, because `test_contract_mode` also runs in `TransactionInstanceTests` (A11).
N2 kept `test_crafts::test_live_sysadmin_craft_passes`, which the plan listed for deletion: it pins
the live sysadmin `seeds:` line and the exact warning text, which no guard FAIL covers, so the plan's
own rule ("not taken where the test is stricter") kept it. 38 methods went, `Ran` −39.

**P2 was not off by one.** The brief for this node said P2's count was off by one. The loader count
at each node head refutes that: P2 added exactly 2 cases (`test_dyadlib` +2), as planned and as its
PR states. The plan's arithmetic (−1 −40 +2 −12 = −51, 583) is internally consistent; only N2's
departure moves it. Stated as found, not resolved here.

### `Ran` per module, core root
| module | BASE | N1 | N2 | P2 | N3 | AFTER | Δ |
|--------|-----:|---:|---:|---:|---:|------:|--:|
| test_bundle | 31 | | −2 | | | 29 | −2 |
| test_concurrency | 5 | | | | | 5 | 0 |
| test_containment | 31 | | −3 | | −1 | 27 | −4 |
| test_craft | 16 | | −1 | | | 15 | −1 |
| test_crafts | 36 | −1 | −1 | | | 34 | −2 |
| test_distribute | 19 | | −1 | | | 18 | −1 |
| test_dyadlib | 40 | | −1 | +2 | −1 | 40 | 0 |
| test_dyadlib_rows | 5 | | | | | 5 | 0 |
| test_entrypoint | 10 | | | | | 10 | 0 |
| test_frame | 8 | | −3 | | | 5 | −3 |
| test_hostadapter | 12 | | −1 | | | 11 | −1 |
| test_incidents | 10 | | | | −2 | 8 | −2 |
| test_livetest | 13 | | | | −1 | 12 | −1 |
| test_manifest | 42 | | −2 | | | 40 | −2 |
| test_package | 89 | | −4 | | −2 | 83 | −6 |
| test_plans | 10 | | −2 | | −1 | 7 | −3 |
| test_playbooks | 4 | | | | | 4 | 0 |
| test_preferences | 14 | | −2 | | | 12 | −2 |
| test_provenance | 63 | | −3 | | | 60 | −3 |
| test_prs | 11 | | −1 | | | 10 | −1 |
| test_records | 8 | | −1 | | −1 | 6 | −2 |
| test_references | 41 | | −1 | | | 40 | −1 |
| test_rows | 39 | | −3 | | −1 | 35 | −4 |
| test_rules | 9 | | −1 | | −1 | 7 | −2 |
| test_runbook | 24 | | −1 | | −1 | 22 | −2 |
| test_sessions | 33 | | −2 | | | 31 | −2 |
| test_vocabulary | 11 | | −3 | | | 8 | −3 |
| **total** | **634** | −1 | −39 | +2 | −12 | **584** | **−50** |

P1 and P3 change no core module (craft zone). No test file was deleted: 27 modules at both ends, so
the syseng mapping guard's count is unchanged.

### Seconds — the ratios
| act | BASE | AFTER | AFTER2 | AFTER/BASE | AFTER2/BASE | AFTER2/AFTER (noise) |
|-----|-----:|------:|-------:|-----------:|------------:|---------------------:|
| (a) `check --tests dyad/tests` | 127.39 | 124.49 | 126.68 | **0.977** | **0.994** | 1.018 |
| (b) `check --evidence` | 141.58 | 148.02 | 147.39 | **1.045** | **1.041** | 0.996 |
| (c) `import dyadlib, package`, ms, median | 138.0 | 139.2 | 129.0 | 1.009 | 0.935 | 0.927 |
| (c) same, mean | 134.0 | 141.4 | 133.8 | 1.055 | 0.999 | 0.947 |
| (d) `check --guards`, empty range | 2.52 | 2.83 | 2.78 | 1.123 | 1.104 | 0.982 |
| (e) `check --tests crafts/syseng/tests` | 1.64 | 2.17 | 2.30 | 1.326 | 1.407 | 1.061 |

Mean seconds (ms for (c)); n = 3, n = 5 for (c). Spreads (max − min), BASE / AFTER / AFTER2:
(a) 18.00 / 2.42 / 4.30 — BASE's first run (117.36 s) is the run at load 0.15, the lowest of the
day; (b) 6.87 / 6.80 / 6.06; (c) 21.7 / 43.6 / 42.0 ms; (d) 0.21 / 0.22 / 0.09; (e) 0.21 / 0.31 / 0.08.

- **(a) The core root: 0.977 / 0.994, against a noise floor of 1.8%.** Inside the noise, as the plan
  predicted ("about 3% … close to the noise floor"; A1). BASE's own spread (18 s, 14%) is three times
  the predicted saving (3.97 s). Per test the core root is 1.06 / 1.08 of BASE: the 50 cases that
  went were the cheap ones, as the plan's per-candidate durations said.
- **(b) Evidence: 1.045 / 1.041, outside the noise floor (0.4%).** Every AFTER and AFTER2 run
  (144.85–152.05 s) is slower than every BASE run (137.77–144.64 s), though the gap of the means
  (≈6 s) is about one spread. What it is made of, from (d) and (e):
  - the syseng root, +0.5–0.7 s: P1's 9 guard cases, whose check (v) spawns an audited child;
  - the guards, +0.3 s per pass: syseng guard (v)'s child import of every pass module. Evidence runs
    the guard pass twice (`check` and `--guards`), so about +0.6 s;
  - the core root, −0.7 to −2.9 s (a).
  That accounts for roughly +0.4 to +1.2 s of the ≈ +6 s. **The rest is unattributed**: it is
  within one spread of (b) and n = 3 cannot separate it from noise. Stated, not explained.
- **(c) P2's price: none measurable.** Medians 1.009 / 0.935 against a control ratio of 0.927; the
  per-run spread (22–44 ms) is many times the 0.13 ms all `enforce` calls take (P2's PR). P2's own
  figure, 176.0 → 171.4 ms, is likewise noise. Import-time enforcement costs less than the jitter of
  one interpreter start.
- **(d)** The guard pass is 0.3 s slower (1.10–1.12), outside its control (0.98): check (v) is the
  only new work in it.

**What the stack buys, in one line each.**
- `Ran` on the core root: −50 (−7.9%), every removed case's check named in the plan.
- Seconds on the core root: none, within noise — as planned.
- Evidence: about +4% slower, of which about 1 s is attributable to P1's new guard work; the
  syseng root is +9 cases.
- Every import of a core module now asserts its pure invariants, at no measurable cost.

### Time verdict
The plan claimed about 3% of the core root in seconds and "no more" (A1, confirmed at planning).
Measured: 2.3% / 0.6%, inside a 1.8% noise floor with a BASE spread of 14%. **The time claim is
neither confirmed nor refuted; it is below what this method resolves.** The reduction is a reduction
in checks that restated other checks, not in wall-clock. The merge evidence got slightly slower, not
faster, because P1 added guard work that runs on every `check`.

## Departures from the plan, as executed
- **P1, check (v) warns before it fails.** The plan said it fails on any I/O; failing at P1 would
  have turned `main` red until P2 moved the 12 impure predicates, breaking the plan's "green at every
  node". It fails only for a module that already calls `enforce`. **And it watches more**: the audit
  hook alone caught 8 of the 12, so the guard also wraps `os.stat` and `os.environ` — partly closing
  the gap the plan left to inference (environment reads, A7).
- **P2, `load_module` fix (not in the plan).** `load_module` now drops a module from `sys.modules`
  when its import raised; before, a second load returned the half-built module silently, so a false
  invariant would have failed loud only once per process.
- **N3, `write_row(first=...)` and the provenance callable.** `write_row` takes the provenance
  append as an argument so `require_transition` runs before either write, and a refusal leaves
  nothing behind (Rule-7 property 5). **`done-never-reopens` made exact** (`done → {archived}`),
  keeping what the deleted rows test pinned.
- **N2, one test kept.** `test_crafts::test_live_sysadmin_craft_passes` stays (above); `Ran` −39.
- **N3's new code carries no tests of its own**: the kept dwork tests and the push-time fence cover
  it (plan A9).
- **M itself**: the plan's M row asked for `test_package` seconds and the import cost of
  `dyad --help` and `dyad check --list`; the brief replaced them with (c). Phase 2 ((d), (e)) and a
  fourth clone for per-node counts were added to explain (b) and the 584. See Incidents.

## Follow-ups — proposed backlog rows, not opened
1. **sysarch `relations-from-register` does I/O.** Live in every AFTER evidence block: `warn
   [syseng/invariants] project_sysarch_entities: invariant 'relations-from-register' does I/O
   (dyadlib.load_module, os.scandir, os.stat, pathlib.Path.glob); move it to TREE_INVARIANTS`. The
   sysarch projector reads only `INVARIANTS`, so moving it needs the projector to read both lists
   (craft zone).
2. **syseng `failure.md` property 3 ("Fatal is not early") needs a fail-closed note.** The conceded
   case — a false invariant in `dyadlib` or `package` stops every command — contradicts it as
   written (named in P1's PR, not amended).
3. **`naming_rules.txt` symbols.** `TREE_INVARIANTS` and `enforce` are not in the `symbol:` lines
   for `dyad/scripts/dyadlib.py`, `package.py`, the guards and the projectors.
4. **Two syseng READMEs are stale**: `crafts/syseng/README.md` (the template row still says the
   test asserts "every invariant holds") and `crafts/syseng/rules/README.md` (the `invariants.md` row
   names only `INVARIANTS` and the runner's pass, not `enforce` or `TREE_INVARIANTS`).
5. **Rule-11 Enforcement wording.** It describes the invariant pass as "every model module's
   `INVARIANTS`", which no longer names `TREE_INVARIANTS` or import-time enforcement; named in P2's PR
   and Rule-12's record (amendment #203), not edited.
6. **18 Tended-craft modules do not yet call `enforce`**, each a warning in every check:
   countersign 1, disclosure 2, sysadmin 5, sysarch 7, syseng 3. The plan's first proposed row (the
   crafts adopt `enforce` and drop their own `InvariantTests`) covers them.
7. **Assertions dropped with no surviving check**, accepted in N2/N3 as small losses, listed so a
   reviewer can reverse any: the sessions `ENTITY == "presence"` literal; the frame `summary()` text;
   the sorted order of the `dyadlib` hold test's names (now only indirect); runbook's "no event is
   written when an invariant is false" (the call-site check stays, its no-write effect is untested).
8. The plan's second proposed row (dyadlib `semver-*` and bundle `tag-name-*` invariants restate
   input-validator tests) is unchanged by the execution.

## Incidents
- **During P1 (already recorded in `INCIDENTS.md` by P2's PR):** a drafting subagent ran
  `dyad/bin/dyad check --help`, which started a full `check` (incident mode G, #123); stopped after
  about 120 s, nothing changed.
- **During this measurement, actions the brief did not name** (for the main Agent to record or not):
  - a fourth throwaway clone (`nodes/`), checked out at each node head for the loader counts;
  - phase 2, (d) and (e), 18 runs, to attribute (b)'s rise; (d) required setting the clones'
    `origin/main` to `HEAD`;
  - several shell commands were refused by the session's worktree-isolation fence for their form
    (a compound command naming git, or a runtime-computed operand); each was re-run as plain separate
    commands, which the refusal text itself prescribed. No action was refused in substance.
  No tracked file in the working repo changed except this one; nothing was committed or pushed;
  `/tmp/dyad-floor-*` did not grow (1,712 throughout).

## What was cut, and why
- **Per-node seconds.** Only BASE and the stack's head were timed; per-node `Ran` was counted, not
  timed. The saving is inside the noise at the head, so no node's share would resolve.
- **`test_package` seconds** (the plan's M row): not run separately; the core root (a) contains it.
- **`dyad --help` / `check --list` import cost** (the plan's M row, A6): replaced by (c) per the
  brief. `check --help` is mode G and was not run.
- **n beyond 3** for (b): the unattributed ≈5 s of (b)'s rise would need n ≈ 10 per clone to separate
  from noise, about 75 min more.

## Disposition
Disposed by the Done-`Y` of d-work #203 (Rule-2, Rule-9 Form); see ledger #203.
