# Falsification — batch test scenarios into one suite run to cut set-up and tear-down (d-work #205)

**Claim (Operator, 2026-10-04, verbatim):** "certain test scenarios should be batched up into a single
`test-suite` run to reduce set-up/tear-down overheads. falsify."

**Readings.** The claim can mean three different things, and each is attacked separately:
- **R1, shared fixture.** Scenarios that each build the same fixture share one build: `setUpClass`, a
  module fixture, or one method with `subTest`s.
- **R2, one process.** The test roots, currently one `unittest` child per root (Rule-12), run as a
  single suite.
- **R3, cached fixture.** The fixture is built once and copied per scenario, and each scenario keeps
  its own test.

**Method.** The `unittest` phases were timed on the core root `dyad/tests` (584 tests, 0 failures),
at `be680b5`, in the runner's environment (`DYAD_NO_NESTED_TESTS=1`, git variables dropped). A wrapper
around `_callSetUp`, `_callTearDown`, `_callTestMethod`, `doCleanups` and the suite's class and module
hooks assigned each second to exactly one phase. Two runs, n=1 each: this container as it is
(`commit.gpgsign=true` globally), and with `commit.gpgsign=false` through `GIT_CONFIG_COUNT`. A
micro-benchmark (n=15, warm) timed `git init` with config, one commit, and `copytree` of a one-commit
repo. All figures are wall seconds on one host; only the ratios carry over (`2026-10-02-test-execution-profile.md` §0).

| phase | signed (s) | unsigned (s) |
|---|---|---|
| test bodies | 107.4 | 84.1 |
| `setUp` | 19.0 | 5.9 |
| `tearDown` + cleanups | 2.1 | 2.2 |
| class + module fixtures | 2.4 | 2.6 |
| **all fixture phases** | **23.5 (18%)** | **10.7 (11%)** |
| wall | 130.4 | 94.1 |

| micro-benchmark | signed | unsigned |
|---|---|---|
| `git init` + 2 `config` | 10.6 ms | 11.6 ms |
| one commit | 99.1 ms | 10.6 ms |
| `copytree` of the repo | ~3 ms | ~3 ms |

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Set-up and tear-down are a significant share of test time. | **Refuted, scoped.** | All fixture phases together are 18% of wall time signed and 11% unsigned. About 80% of the time is in test bodies, which are the scenarios themselves: commits made under test, `dyad` children, guard calls. Batching cannot remove those. |
| 2 | The per-test set-up cost is inherent fixture building. | **Refuted.** | The heaviest classes pay about 100 ms per test (`FenceTests` 94, `TransactionTests` 103, `references.FixtureTests` 115, `FloorTests` 188), and one signed commit costs 99 ms. Signing the fixture's root commit is most of `setUp`. With signing off, `setUp` drops from 19.0 s to 5.9 s and the wall from 130 s to 94 s, with no test restructured. The 2026-10-02 audit's candidate row 3 (`commit.gpgsign=false` in fixtures) dominates any batching. |
| 3 | R1, after signing is off, cuts the remaining set-up materially. | **Survives, narrowly.** | The ceiling is about 6–8 s of 94 s (`setUp` 5.9 s plus part of tear-down), and only if no fixture were rebuilt at all. Most classes mutate their fixture: commits, branches, writes. Sharing a mutable fixture makes tests order-dependent, and one method full of `subTest`s still stops at the first error in shared state. R1 is sound only for classes whose scenarios only read an identical fixture. The clearest are `references.CraftPresenceTests` (0.38 s set-up against 0.07 s of bodies, unsigned) and `CraftReferencesContribTests` / `CraftRefsTests` (bodies 0.03 s each). |
| 4 | R3 gives R1's saving without R1's loss of isolation. | **Survives.** | `copytree` costs about 3 ms against about 22 ms to build a one-commit repo unsigned, or 110 ms signed. Each scenario keeps its own directory, its own `.git` and its own test, so failures stay isolated. #110 attack 4 and #138 attacks 6–9 already proved this and applied it to `test_craft.CraftCliTests` (19 real installs reduced to 1 per module run, about 2×). That class's remaining 10.7 s is body time: real `dyad craft` children under test. |
| 5 | R2 cuts per-root process overhead. | **Refuted.** | The runner already runs one suite per root (Rule-12 property 2), so the overhead is one interpreter start and discovery per root, about 2 s across 6 roots out of about 150 s. Merging the roots into one process would also put four packages named `guards` (`dyad/tests/guards/`, `crafts/{sysadmin,sysarch,syseng}/tests/guards/`) into one `sys.modules`, where they would collide. |
| 6 | Batching scenarios reduces the test count without reducing what is checked. | **Survives, conditionally.** | Merging methods into one with `subTest` keeps the checks, but a failure now names a sub-case rather than a test. #203 cut the test count by removing overlap, not by merging. Merging is only a count change, not a saving: the time saved is all in the shared fixture (attacks 3 and 4). |
| 7 | Overlap (Rule-16 presence): another session touches these test files. | **No overlap found.** | The presence store was read at `be680b5`, and no live session names `dyad/tests/`. |

**Survivor.**
- Batching scenarios into one suite run is not the lever. The fixture phases are 11–18% of the core
  root, and most of that is the fixture's signed commit.
- **Order of what pays:**
  1. Turn signing off in fixtures: about 36 s of 130 s on this host, with no test restructured.
  2. Where scenarios mutate their fixture, build it once and copy it per scenario (R3): it keeps
     isolation, and it is already applied where it paid most (#138).
  3. Where scenarios only read an identical fixture, share it (R1): `setUpClass`, about 1 s.
- R2 is refuted.

Disposition: see ledger #205.
