# Test-execution profile: where the time goes, and how much of it is inference (2026-10-02)

*d-work #204. The Operator's prompt, verbatim: "profile dyad-system test execution for bottlenecks.
\* hot spot (time spent) \* inference time spent vs. mechanical execution time spent". Measured
2026-10-02 by delegated sub-agents. The mechanical side was measured in a throwaway clone at
`7034d76` under the session scratchpad. The inference side came from two independent code-only
walks (A, B) of this session's 47 transcripts, which were then reconciled call by call, and a critic
checked the result. Nothing in the working repo was touched. The raw data (`p204/measure/`,
`p204/transcripts-A/`, `p204/transcripts-B/`, `p204/reconcile/`, `p204/critic/`) is session-local,
not corpus, and goes with the container. This audit detects and counts and disposes nothing. Each
bottleneck below is proposed as a backlog row, and none is opened.*

**§0, carried from `2026-09-25-optimization-opportunities.md`: an absolute second is a property of
one machine and one day; only a ratio travels.** This matters more here than usual. The container
signs every git commit through a local signing service, and that cost is about a quarter of the
core root (§1.3). The Operator's own host may not sign at all.

## Method
**Mechanical side (clone at `7034d76`).** The clone has `core.hooksPath=dyad/hooks` and the git-ignored
`provenance_legacy.local.txt` copied in.
- **Roots.** Each test root was timed through the runner's own child:
  - core root, n=6 warm, signed;
  - core root, n=2, with `commit.gpgsign=false` set through `GIT_CONFIG_COUNT`. This was a paired A/B run that passes through `suite_env`;
  - each craft root, n=3.
- **Modules.** Each module was run alone, n=1, or n=2 for the top 8.
- **Per-test durations, n=1.** These came from a hand-typed equivalent of the runner's child, with the same interpreter, cwd, env and argv plus `--durations 0`. Its wall time, 128.5 s, matches the runner.
- **Spawn attribution, n=2.** A `sitecustomize` audit hook logged every subprocess and every copy or rmtree. It adds about 5 s. `attrib.py` assigns time exclusively: a child's logged grandchildren are subtracted from the child.
- **Profiles.** cProfile and strace, n=1.
- **Gate acts, n=3 each:** `check --list`; `check --guards` on an empty range; `check --guards --pre-push` with a memo hit and cold; `check --evidence`.

The core root and module numbers are Python 3.13 (`dyad-python`'s first candidate). The gate acts
ran as `python3.12 dyad/scripts/package.py`. The machine has 4 vCPU and kernel 6.18.44. The 1-minute load average stayed between 0.15 and 1.36,
and no two timed runs overlapped. The first core run (254.9 s, cold page and `.pyc` caches) is
excluded. All timings are wall time; no CPU user or sys time was recorded.

**Inference side (transcripts).** The scope is the main transcript, 16 subagents and 30 workflow
agents from 3 finished workflows, over 2026-09-16T10:08Z to 2026-10-02T17:08Z (the full window). A
second cut starts at 2026-09-29T00:00Z and covers the test-performance d-works #190 to #203. This
measurement's own workflow is excluded.

Two variants were written independently, both as code (Rule-13):
- **A** is an event-sequence walk with completion-order attribution.
- **B** builds a per-call table and partitions the timeline, splitting each gap evenly among the calls in flight.

Both reproduce their own headlines. All 3,321 calls match one to one between them. Each
disagreement was traced to a definition or to a named misclassified call and decided by reading the
command text (`reconcile/resolve.py`). The headline uses B's even split; A's split moves the test
total by 0.4%.

A **critic** then re-ran the attribution and walked all 112 `git push` results in the transcripts
for the `[Rule-12]` lines (`critic/pushes.py`). It cross-checked the module table and the gate
order. Its surviving corrections are applied below and listed under *What the critic changed*.

## (1) Hot spots by time spent

### 1.1 Roots
| root | tests | warm runs (s) | median | share of suite |
|------|------:|---------------|-------:|---------------:|
| `dyad/tests`, signed commits | 584 | 129.44, 129.72, 121.24, 122.47, **182.86**, 132.81 | **129.6** | ~91% |
| `dyad/tests`, `commit.gpgsign=false` (A/B) | 584 | 95.70, 96.77 | 96.2 | |
| `crafts/sysadmin/tests` | 94 | 5.87, 6.16, 5.34 | 5.87 | |
| `crafts/sysarch/tests` | 89 | 3.59, 5.31, 3.12 | 3.59 | |
| `crafts/syseng/tests` | 62 | 2.02, 2.21, 2.28 | 2.21 | |
| `crafts/countersign/tests` | 40 | 1.50, 1.37, 1.40 | 1.40 | |
| `crafts/disclosure/tests` | 35 | 0.84, 0.80, 0.76 | 0.80 | |

- The core root is the suite. All five craft roots together take about 13 s.
- The 182.9 s outlier ran at load 0.36, so it was most likely latency in the signing service, not CPU.

### 1.2 Modules and tests (core root)
Shares are of the **126.7 s summed per-test duration**, the consistent source. The isolated-module
runs add up to 142.7 s, 110% of the root, because each one pays its own startup and its own shared
scratch-install fixture. Their shares are therefore overstated by about 10% and are not used.

| module | summed per-test s | share | cause (attribution, §1.3) |
|--------|------------------:|------:|---------------------------|
| `test_package` (83 tests) | 58.8 | 46% | 112 real `package.py` children (30.8 s); scratch installs; 82 signed commits (8.2 s); 2,350 other git calls (11.2 s) |
| `test_craft` (15) | 13.9 | 11% | 47 `dyad craft install/check` children (9.3 s); copytree and rmtree 2.0 s |
| `guards.agent.test_provenance` (60) | 11.9 | 9% | pure git fixture: 104 signed commits, 9.6 s (76% of module) |
| `guards.agent.test_rows` (35) | 10.8 | 9% | pure git fixture: 96 signed commits, 8.8 s (79%) |
| `guards.agent.test_references` (40) | 7.0 | 6% | 51 signed commits, 6.2 s (53%); rmtree 0.9 s |
| **five modules** | **102.4** | **80.8%** | |
| next: `test_crafts`, `test_containment`, `test_concurrency` | ~11 | ~9% | signed commits; craft children; clone, fetch and push between scratch repos |

**Pareto (per-test, n=1).**
- Top 1% (4 tests): 14.1% of the time. Top 5% (21 tests): 35.7%. Top 10% (58 tests): 57.8%.
- 135 tests run under 0.05 s each and add up to 1.2 s together.

The slowest tests are all `test_package` or `test_craft` integration cases:
| test | s | cause |
|------|--:|-------|
| `PackageTests.test_scratch_install_with_one_row_survives_referential_integrity` | 6.09 | real `package.py` child (90%); 143 spawns |
| `InvariantPassTests.test_pass_order_and_lines` | 4.47 | runs the check runner in process; 287 git calls |
| `PackageTests.test_evidence_block_shape_and_hash` | 4.35 | the same; 290 git calls |
| `PackageTests.test_scratch_install_with_the_sysadmin_craft_discovers_its_guards` | 3.02 | scratch install plus a `package.py` child (93%) |
| `PackageTests.test_check_pr_refuses_a_two_zone_pr_that_the_push_path_accepts` | 2.19 | `package.py` child (63%), signed commits (17%), copytree |
| `PackageTests.test_dwork_refuses_a_row_or_a_disposition_without_its_words` | 2.14 | 10 python children (90%) |
| `CoreRowTests.test_core_row_and_unmodified` (`test_craft`) | 2.08 | git init and other git calls (39%), scratch install |
| `test_references.FixtureTests.test_a_broken_reference_fails_under_its_own_kind` | 1.85 | 14 signed commits (55%) |

The full top 40 is in `measure/top40.json`.

### 1.3 Attribution of the core root by cause
These figures come from the instrumented run (135 s, of which about 5 s is the audit hook). Time is assigned exclusively.

| cause | s | share | what it is |
|-------|--:|------:|------------|
| signed `git commit` | 46.0 | 34% | 482 commits at 95.8 ms each; unsigned, a commit costs about 9 ms (microbenchmark) |
| python child processes (exclusive) | 44.2 | 33% | 218 spawns, of which 25 `package.py check` children do real work (15.4 s). The other ~190 (craft, dwork, runbook, project, install, `--audit-child`) cost 170–350 ms each, mostly interpreter and import startup: **about 30–35 s**, inflated by part of the ~5 s audit-hook overhead |
| other git calls | 27.0 | 20% | 5,826 spawns, ~4.6 ms each: init, add, config, rev-parse in fixtures |
| in-process python (residual) | 13.0 | 10% | test duration minus logged spawns and copies, so it also absorbs any unlogged wait |
| rmtree + copytree | 4.9 | 4% | scratch installs and fixture copies |
| sleep / network | 0.03 / 0 | | |

**The signing cost, as the A/B gives it.** Signing costs **26–48 s** (20–35%), not a firm 46 s:
- Median signed against unsigned is 129.6 − 96.2 = **33.4 s**.
- The non-outlier warm runs (121–133 s) give 25–37 s.
- Earlier `nosign` runs (79–81 s, method unrecorded) would imply ~48 s. They are excluded from the conclusions because there may have been a second variable.

Signing is I/O wait on a local service, not CPU. It is specific to this container, but **it was
paid**: the session profiled in (2) ran in this same signing container.

**Parallel headroom.** The suite runs serially on 4 vCPU at load ~1, so about three cores sit idle.
Nothing measured how much a parallel runner would save.

### 1.4 Gate paths (Python 3.12, n=3)
| act | runs (s) | mean | what costs |
|-----|----------|-----:|------------|
| `check --list` | 0.22, 0.18, 0.19 | 0.20 | import plus guard discovery; startup is cheap **at the gate** |
| `check --guards`, empty range | 3.50, 2.98, 3.20 | 3.23 | guards only. Under cProfile (5.5 s): manifest AST import scan ~2.0 s (37%; called twice, ~350 `ast.parse`); `syseng/invariants` ~1.2 s; `references` ~0.75 s; 251 git spawns ~0.9 s |
| `--pre-push`, memo hit | 3.24, 3.22, 2.91 | 3.12 | guards; suite skipped on the memo |
| `--pre-push`, cold | 150.30, 154.05, 141.51 | 148.6 | guards plus the full suite over 6 roots (suite ~98%) |
| `check --evidence` | 158.11, 159.41, 149.58 | 155.7 | the full suite plus two guard passes. It never reads the memo (Rule-12 p2), by design |

**What the gate numbers don't show.**
- **The memo-hit row is the best case, not the typical one.** In this run the memo-hit act always followed an evidence act that had just written the memo for the same tree. In the real session the order is push first, then evidence. Of the 11 suite-running pushes after the suite memo (N2) landed on 10-01, **none hit the memo**, and no push output in the transcripts contains "already passed" (`critic/pushes.json`). The observed hit rate is 0 of 11.
- **The ~3 s guard pass is a floor.** The clone has no tags, so `infra/bundle` skipped `check_drift` for all 6 crafts. `agent/references` skipped the empty event store, and `agent/prs` judged only synthetic ranges (hence rc=1 on every gate act, which is not a defect in the tree).

## (2) Inference vs mechanical execution

### 2.1 Totals, full window
| scope | inference | foreground tool | other | notes |
|-------|----------:|----------------:|-------|-------|
| **main thread, wall clock** | 18,345–18,458 s (49%) | 18,428 s (49%) | compaction 754 s (model time, over 5 compactions); overhead or harness 139–152 s | active wall ~37,700 s |
| all 47 transcripts, agent-seconds | ~29,900 s | 34,393 s | compaction 754 s | these overlap; wall-clock union of activity 59,161 s |

The main thread also spent time outside its active wall:
- idle on the Operator: 1,315,2xx s;
- idle waiting on its own background work: ~24,600 s;
- container down: 30,045 s (2026-09-29 14:25 to 22:46).

The idle time on its own background work is in neither the inference column nor the tool column. B splits it by what woke the turn: agents 17,344 s, background tests 3,354 s, workflows 3,258 s.

**Second cut (since 2026-09-29), main thread.** Active ~14,250 s: inference ~4,200 s (~30%), tool 9,923 s
(~70%). The testing-performance d-works were tool-heavy, as expected.

### 2.2 Foreground tool time by class (all transcripts, full window, reconciled)
| class | calls | s | share of 34,393 s |
|-------|------:|--:|------------------:|
| direct test runs | 484 | 20,356 | 59.2% |
| foreground waits on background test runs | 45 | 8,749 | 25.4% |
| waits on workflows | 6 | 1,884 | 5.5% |
| other bash | 1,737 | 2,385 | 6.9% |
| GitHub MCP | ~430 | ~660 | 1.9% |
| agent delegation, workflow, file read/write, other | | ~350 | ~1% |

- Waits overlap the background runs they block on. **Never add the waits to the background test seconds.**
- Background test runs: 23 runs, 19,205 s from launch to end, 18,335 s beyond their foreground part, 15,350 s of wall-clock union.
- Background agents: 16 agents, 20,998 s.

### 2.3 Direct test runs by subclass, after the critic's re-split
| subclass | calls | s | correction |
|----------|------:|--:|-----------|
| full `package.py check` / `dyad check` | 55 | 5,709 | main 46 calls / 4,676 s, often run whole only to grep one guard line |
| push (pre-push gate) | 109 | 3,297 | **only 18 ran the suite (~2,780 s)**. 89 show no Rule-12 line and are guard-only: median 4 s, 619 s in total. 2 hit the ledger-only skip (14 s). None hit the memo. |
| `check --evidence` | 30 | 3,232 | 3 of these calls also pushed, so they carry two suites each (634.5 s, e.g. 275.5 s and 259.8 s). 7 suite-running pushes in all sit inside the evidence and full-check subclasses |
| wrapper and harness scripts | 56 | 2,173 | landing cascades, measurement and profiling scripts (`mut.py`, `iso.py`, `timeit.py`) |
| `check --guards` | 60 | 2,098 | **48 of 60 finished in under 15 s** (203 s, median 4.1 s; the suite was skipped). 12 calls (~1,895 s) ran the suite |
| `check --tests` | 81 | 2,065 | 51 of 81 under 15 s, i.e. single targets as Rule-12 p2 intends |
| `unittest` by hand | 93 | 1,781 | the expensive path Rule-12 p2 names; 30 calls (802 s) in workflow agents |

**Main thread alone.** Direct test runs take 13,131 s over 291 calls. That is 71% of main tool
time and 35% of main active wall. Foreground waits on tests add 1,101 s.

**Inside subagents.** Direct runs are only 38% of tool time and waits are 59%. The subagent hot spot is two
measurement audits, #199 M (4,567 s of waits) and #203 M (2,388 s), blocking on their own
background timing runs in 600-s-capped `until … sleep` loops. Those loops are also the 15 slowest
single calls. The slowest direct runs are 300.9 s (`check --guards`, then a full check), 279.0 s
(two pushes), 275.5, 266.2 and 259.8 s (evidence, push included), and 216.1 s.

**These seconds are not the current suite's cost.** Over the window the core root grew from 584 to 647 tests
and was later cut back to 584 by #203. In the second cut, subagents ran suites in parallel with main,
and the per-call means rose: full check 158 s against 104 s, push 65 s against 30 s. The transcript
seconds and the 129.6 s profile cannot be added together into one cost model.

### 2.4 Inference around tests
- The model requests that issued a test, plus the first request after its result, carry **about 6,800 s, 23% of ~29,900 s of inference**. A's own code gives 6,780 s and B's gives 6,853 s.
- Widening the window to the next three requests gives 11,459 s (38%). That window takes in 40% of all requests, at the mean latency, so it mostly counts ordinary follow-on work.
- **Qualified by the critic.** Each of these figures is a choice of window, not a bound in either direction. The earlier reading, "tests cost wall time, not extra model thought, because per-request latency around tests (8.6 s) is below the mean (9.5 s)", is **withdrawn**. A failing or slow test adds *requests* (diagnosis turns, polling turns), not longer ones. Nobody counted requests caused by tests against a baseline, so whether tests raise inference is **unanswered**.

### 2.5 Tokens (all transcripts)
| field | count |
|-------|------:|
| input (uncached) | 6,474 |
| cache_creation | 30.27 M |
| cache_read | 1,030.0 M |
| output | at least 1.80 M |

- Main-thread output is exact: 1,485,733.
- In 999 subagent and workflow messages only a streaming snapshot of usage survives. Their output count is a placeholder, so the true output total is unknown.
- An independent recount over the raw JSONL reproduces A exactly. B undercounts the input side by 14–31% because it drops the snapshot messages.

### 2.6 Cross-check
The harness cost-state counters cover 2026-09-21T21:23Z to 2026-10-02T13:07Z. Against them:
- API time is 19,965 s, and inference plus in-window compaction comes to 7.1–7.8% less;
- tool time is 26,236 s, and the measured tool time comes to 7.0% more.

What the counters count is undocumented, so this is corroboration, not calibration.

### 2.7 Verdict
On the main thread, the clock the Operator waits on, active time splits **about evenly: ~49%
inference, ~49% mechanical** (51/49 if compaction counts as inference). **Test execution is the
mechanical side**: direct test runs are 71% of main tool time and 35% of main active wall, and
waits and idle on background test runs add more. The suite's own cost (§1) is dominated by process
spawning and git fixtures, not test logic.

**What is still unanswered:**
- a wall-clock partition of the 59,161 s union into inference-only, mechanical-only and both-at-once;
- whether tests raise inference by adding requests.

## Ranked bottlenecks: proposed backlog rows, not opened
The prize is stated in its own unit. Per-run seconds are from §1 at `7034d76` on this container.
Session totals are from §2 over the full window, against a larger suite under contention.

1. **Full `check` run by hand where a target or one guard would do.**
   - **Evidence:** 55 calls, 5,709 s, 4,676 s of it on the main thread at ~100 s each. They were often run only to grep one guard line. Rule-12 p2 already names the cheaper path for tests, but there is no single-guard path for guards.
   - **Prize:** ~100 s per call avoided; ~4.7k s of main-thread wall over the window.
   - **Candidate row:** a `dyad check --guard <label>` path, or conduct, plus a play-book line.
2. **The suite memo never hits at the push gate in practice.**
   - **Evidence:** 0 of 11 suite-running pushes since N2 hit the memo. The session pushes first and runs evidence afterwards, and evidence, which writes the memo, never reads one (by design).
   - **Prize:** ~145 s per push (148.6 → 3.1 s). Over the window that is up to ~2.7k s across 18 suite-running pushes, plus the 7 hidden in evidence and full-check calls.
   - **Candidate row:** order evidence before push on the same tree, or let the push gate write the memo its own cold run earns. Investigate which one keeps Rule-2's Binding intact.
3. **Signed commits in test fixtures.**
   - **Evidence:** 482 commits at ~96 ms against ~9 ms unsigned. The A/B (n=2 against n=6) saves 26–48 s (median 33 s, ~26%).
   - **Prize:** ~33 s per core-root run, so per cold push and per evidence, on any host that signs. It was paid on every suite run in this session.
   - **Candidate row:** the fixture helpers set `commit.gpgsign=false` in their scratch repos. Tests never verify signatures, so this does not weaken what they check.
4. **Interpreter and import startup of short python children.**
   - **Evidence:** ~190 children at 170–350 ms each, ~30–35 s per core root (~25%). This is an upper estimate that includes audit-hook overhead. Startup is negligible at the gate (0.2 s once) but not in the suite.
   - **Prize:** ~20–30 s per core-root run.
   - **Candidate row:** call the CLI entrypoints in process (`main(argv)` with captured output) where a test is not about the process boundary. Keep one real-subprocess test per verb.
5. **Foreground wait loops on the session's own background runs.**
   - **Evidence:** 8,749 s over 45 calls, 7,648 s of it in subagents, mostly #199 M and #203 M polling in 600-s `until … sleep` loops. These are agent-seconds that overlap the runs they wait on, not extra machine time.
   - **Prize:** agent occupancy and the main thread's ~1.1k s, not suite speed.
   - **Candidate row:** measurement subagents rely on the completion notification or Monitor instead of polling loops. This is a conduct and play-book line.
6. **Git fixture setup outside commits.**
   - **Evidence:** 5,826 spawns, 27 s per core root. `test_provenance`, `test_rows` and `test_references` are almost pure git fixtures.
   - **Prize:** part of 27 s per run, plus most of the 4.3 s that unsigned commits still cost.
   - **Candidate row:** build each module's fixture repo once and copy it per test, or batch the git calls through `fast-import`.
7. **Serial suite on 4 vCPU.** About 3 cores are idle during every run.
   - **Prize:** unmeasured; potentially the largest per run.
   - **Candidate row:** measure a parallel run of the core root first. Module-level sharding would need isolated scratch dirs and the suite memo semantics re-checked.
8. **Manifest guard's AST scan, run twice per guard pass.**
   - **Evidence:** ~2.0 s of a 5.5 s profiled guard pass.
   - **Prize:** ~1 s per gate, and twice per evidence, over ~109 pushes per window (~0.1–0.2k s).
   - **Candidate row:** parse once per run and share the result.

## What the critic changed
- **Signing.** "46.0 s (34%)" became **26–48 s by A/B**. "Not intrinsic" was qualified: the cost is environment-specific, but this session paid it.
- **Startup.** "Python children include their git work" and "startup is not a bottleneck" were both **refuted**. Attribution is exclusive, so startup of the short children is ~30–35 s (~25%) of the core root. It is a bottleneck in the suite, though not at the gate.
- **Module shares.** The isolated-run shares (sum 110%) were **replaced** by the summed per-test shares.
- **Memo hit.** The ~3 s memo hit was **qualified** as best case. The observed hit rate is 0 of 11, which became bottleneck 2.
- **Gate guard pass.** ~3 s was **qualified** as a floor (no tags, empty event store, synthetic ranges).
- **Pushes.** "109 push calls = test execution" was **re-split**: 18 ran the suite, 89 were guard-only and 2 were ledger-only. A further 7 suite-running pushes were found inside evidence and full-check calls.
- **`check --guards`.** "Runs the suite" was **re-split**: 48 of 60 calls ran in seconds.
- **"Tests don't make the model think longer"** was **withdrawn**. 23% is a window, not a bound.
- **Two measures were stated as missing and left unanswered** rather than estimated: a wall-clock partition of inference vs mechanical, and CPU time.
- **Transcript seconds and the profile** were stated as **not one cost model**: the suite changed over the window and ran under contention.

## Caveats
- **This machine only.** The container signs commits through a local service. No run was made on the Operator's host, so a ratio travels better than an absolute.
- **Small samples.**
  - The core root has n=6 signed runs and n=2 unsigned runs.
  - Module timings have n=1 or 2.
  - Per-test durations have n=1, and `--durations` reported 426 of the 584 tests; the rest round to 0.
  - cProfile and strace have n=1.
- **Data provenance.** Most mechanical data was written by an earlier, interrupted run of this same task at the same commit, and was reused after the clone's state was checked. The new data from this run is the signed/unsigned A/B and the microbenchmark.
- **Wall time only, and some figures are residuals.** No CPU user or sys time was recorded. "In-process python" is a residual, and the by-cause figures carry about 5 s of instrumentation.
- **Gate acts.** They ran in a tagless clone over synthetic ranges, so each exits rc=1 from `agent/prs`, which is expected. The guard pass with tags fetched was not measured.
- **Transcript classification.** Classes come from command text. About 7 s of A's harness false positives were not opened individually. The output-token total is a floor.
- **Not measured:**
  - per-module times for the craft roots (~13 s in total);
  - permission and classifier latency inside tool time;
  - the request count caused by tests;
  - the overlap-aware wall-clock split.
- **Scratchpad hygiene.** `reconcile/join.pkl` holds command excerpts from the transcripts. It sits in the session scratchpad and should be deleted when no longer needed.

## Disposition
Disposed by the Done-`Y` of d-work #204 (Rule-2, Rule-9 Form); see ledger #204.
