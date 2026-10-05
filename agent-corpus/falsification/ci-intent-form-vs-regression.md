# Falsification — CI validates integration form and structure; unit regression is an audit job (d-work #220)

**Claim (Operator, 2026-10-05, verbatim):** "intent of CI testing is to ensure that the integration
form and structure are valid.  unittesting regression verification is an audit job. falsify."

**Reading.** "CI" is the local push gate, which is this system's CI (Rule-14 property 3); hosted CI
only corroborates on `main`. The claim has two parts:
- the per-change gate should judge whether the integrated system is well-formed;
- running the unit tests to detect regressions belongs to audit, not to every change.

**Basis.** The data is #219's static dependency map (45 test files, 921 tests, at `9fafb51`) and
#204's per-test durations (core root, signed, at `7034d76`; craft roots scaled by test count).
Shares are of the 140.6 s summed suite. Absolute seconds are one machine's (#204 §0). For the audit
that sizes the subsets, see `../audits/2026-10-05-ci-test-subset.md` (#219).

**Terms used below.**
- *Gate code* is the code that does the gating: every guard (`dyad/guards/**`,
  `crafts/*/guards/**`), the runner and the writers it relies on (`package.py`, `dyadlib.py`), the
  install path (`distribute.py`, `craft.py`), `runbook.py` (its parser is imported by the
  sysadmin guards, Rule-19), and the hooks.
- *Non-gate code* is everything else the suite tests: projectors, `trace.py`, `livetest.py`,
  `hostadapter.py`, `incidents.py`, and the disclosure craft's `redaction.py`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A1 | "Form and structure" has no concrete referent here. | **Refuted.** | It does: the invariant pass (72 lines, ms) and the guards, about 25 state guards and 5 transaction guards in about 4 s. Between them they judge zones, rows and transitions, provenance against rows, Rule blocks, vocabulary, manifest, references, bundle and drift, naming and the test mapping. "Integration" adds one install smoke test, a scratch install of the core plus one craft, guards run there (Rule-11 property 5). That set already exists and already runs on every push. |
| A2 | **The gate validates itself.** The guards judge the live repo, not their own code. A regression in a guard, or in the runner, can make a check pass falsely. The repo is still valid, so CI stays green, but the fence is now blind, and any invalid structure pushed after that lands unseen until audit. | **Confirmed.** | The unit tests of the *gate code a range changes* are CI. They are the form check of the gate itself. Unit regression of non-gate code is an audit job. |
| A3 | **Three checks exist only as tests.** #217 found form checks with no guard: redaction (disclosure), `incidents.check`, and the trace store's `check_store`. Moving tests to audit-only removes these checks from CI altogether. | **Confirmed.** | They are promoted to guards before the split is adopted. Until then their tests stay in CI whenever the range touches the records they read. |
| A4 | **Rule-2 Binding.** A Done-`Y` merges only on the observed passes of `check --evidence`, which runs every root. If unit regression is audit-only, either the evidence still runs it, so nothing is saved at merge, or the Operator ratifies merges with no regression evidence. | **Confirmed as a Rule cost.** | There are two adoptions. **(a)** Narrow only the push gate (Rule-12 property 2) and keep `check --evidence` full, which needs no Rule-2 or Rule-14 change. **(b)** Narrow the evidence too, which amends Rule-2 Binding, Rule-12 property 2 and Rule-14 property 3. This record makes neither change. |
| A5 | **The push-time suite catches regressions.** | **Refuted, scoped.** | This host's transcripts hold 32 `git push` results carrying `[Rule-12]` lines, and none shows `FAILED`. Regressions were caught before the push, by hand runs and `check --evidence`, never by the gate's own suite. The scope is one host's transcripts: other hosts and other sessions' runs were not read, and #204's critic walked 112 pushes for timings, not failures. |
| A6 | **Splitting regression to audit saves time.** | **Mostly refuted.** | Gate code dominates the suite. The test files whose subject is gate code are 31 of 45 files, 707 of 921 tests, and **132.4 s of 140.6 s (94%)**. Non-gate tests are about 8 s (6%). A non-gate change (projector, `trace.py`, `livetest`) would drop to guards plus the smoke test. A gate-code change still runs that code's tests: see the table below. |
| A7 | **Regression window.** A regression found at audit has already landed on `main`, other sessions build on it (Rule-16), and the fix costs a bisect. | **Confirmed as the cost.** | It is bounded by the audit cadence, and the cadence is an open parameter the adoption must set. Under adoption (a) the window closes at every merge, because evidence stays full. |
| A8 | **The unit tests that judge the live repo are form checks.** #217 found 15 tests that re-judge the live repo, duplicating guard verdicts. | **Supports the claim.** | Under the survivor these leave both CI and audit, because the guards already give the verdict. Deleting them is follow-up work, about 1.7 s per run. |
| A9 | **"Unit" versus "integration" maps cleanly onto test files.** | **Refuted, scoped.** | `test_package` (83 tests, 46% of core time) mixes unit cases with scratch-install integration cases. `test_craft` and `test_concurrency` are integration through and through. The split is by *subject code* (gate or not), not by test style. The install smoke test is drawn from the integration cases that exist; it is not a new suite. |

## Sizes under the survivor (push gate)
"Selected" is #219's selection: the files whose dependency set meets the change. "Survivor" keeps
only the selected files whose subject is gate code. Guards, invariants and the smoke test run in
every row.

| change | #219 selected | survivor: gate-code tests | share of suite time |
|---|---|---|---:|
| `package.py` | 290 tests, 92.2 s | 232 tests, 88.4 s | 63% |
| the `rows` guard | 311, 91.1 s | 253, 87.3 s | 62% |
| `dyadlib` | 882, 137.9 s | 679, 129.7 s | 92% |
| the `provenance` guard | 193, 71.2 s | 175, 70.8 s | 50% |
| a craft guard (`changelog`) | 20, 1.2 s | 20, 1.2 s | 1% |
| the `vocabulary` guard | 8, <1 s | 8, <1 s | <1% |
| `livetest` | 195, 22.7 s | 0 | 0% |
| a projector (`project_kanban`) | 61, 6.0 s | 0 | 0% |
| `trace.py` | 12, <1 s | 0 | 0% |
| record-only | 0 | 0 | 0% |

## Survivor
CI's intent is two things:
- integration form and structure: invariants, guards, one install smoke test;
- *the gate's own validity*: the unit tests of any gate code the range changes.

Unit regression of everything else is an audit job.

Three preconditions apply before adoption:
1. The three checks that exist only as tests become guards (A3).
2. A choice between narrowing the push gate only (a) and narrowing the evidence too (b) (A4).
3. An audit cadence (A7).

**What it buys** is small in this repo, because 94% of the suite is gate code (A6). A non-gate
change drops to about 4 s plus the smoke test. A gate-code change still runs that code's own
tests, 50–92% of the suite for the core modules. The larger gain is in the test shape, not in
this split:
- `test_package`'s scratch installs are 46% of core time and sit under every `package` change;
- deleting the 15 duplicate live tests (A8).

## What was tried and found nothing
- **Hosted CI as the gate.** It is not the gate (Rule-14 property 3, #168), so the claim cannot
  move work to it.
- **Hooks as gate code.** `dyad/hooks/*` have no test file of their own. They are exercised
  through `test_package`, `test_concurrency`, `test_dyadlib` and `test_entrypoint`, all gate-code
  test files, so they need no separate entry in the sizing.

## Disposition
Disposed by the Done-`Y` of d-work #220 (Rule-2). No Rule or code is changed here. Adoption, if
wanted, is a later d-work carrying the three preconditions.
