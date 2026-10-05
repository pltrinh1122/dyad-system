# Falsification — there are no duplicates between guards and tests (d-work #217)

**Claim (Operator, 2026-10-05, verbatim):** "there are no duplicates between guards vs. tests. falsify."

**Reading.** A duplicate is a test whose assertion is a guard's own verdict on the live repository:
it calls a registered guard's check over `repo_root()` and asserts that it passes. Every push and every
`check --evidence` already runs that guard over the same tree. A test of a guard's logic on fixtures is
not a duplicate. It is the guard's own test, which Rule-12 requires.

**Method.** At `3073f2e` (main, 2026-10-05), every test in all six test roots that calls `repo_root()`
was listed: 42 tests. Each was timed alone in the runner's environment (`DYAD_NO_NESTED_TESTS=1`). The
test body was read to find whether it calls a guard's check over the live tree. The guard registry was
taken from `package.py check --guards`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | No test re-asserts a guard's verdict on the live repository. | **Refuted.** | 15 tests do. They assert that a registered guard's check over `repo_root()` returns nothing, which the same `check` run's guard pass already asserts: `agent/prs`, `agent/rules`, `agent/vocabulary`, `agent/records`, `agent/references` (`LiveTests`), `agent/provenance`, `preferences/preferences`, `sysadmin/changelog`, `sysadmin/events`, `sysadmin/ops_scripts`, `sysadmin/runbooks` (`test_live_runbooks_pass`), `sysarch/registry`, `syseng/tests`, `syseng/naming`, `syseng/invariants`. |
| 2 | Those duplicates are costly. | **Refuted.** | Together they take about 1.7 s per suite run, of about 100 s. `syseng/invariants` takes 1.2 s of that, `naming` 0.2 s, `references` 0.2 s, and the rest are under 0.1 s each. Removing them saves about 2% of a run. |
| 3 | Every live test is a duplicate. | **Refuted.** | Three call a check that **no guard runs**, so the suite is the only place it runs: `disclosure` `redaction.check` (`test_live_check_passes`), `incidents.check` (`test_live_log_passes`) and `trace.check_store` (`test_live_trace_store_is_well_formed`). The projector live runs (countersign 3.9 s, sysarch instances, schema, entities and ERD together about 3 s) and the CLI tests are not guard calls either. These are #210's and #211's suite-only checks, which no guard covers. |
| 4 | A duplicate adds nothing. | **Survives, narrowly.** | Each duplicate also proves that the guard passes when run inside the test environment, and inside a scratch install, where CI runs this suite (`test_records`' own comment). The guard pass proves the same on every install's own `check`. The extra assurance is the import path under `unittest`, which the guard's fixture tests already exercise. |

**Survivor.**
- The claim is refuted: 15 tests duplicate a guard's verdict on the live repository. They cost about
  1.7 s a run, and removing them is #203's channel 1 (overlap), worth about 2%.
- The live tests that matter are the opposite case. Three checks run only in the suite, with no guard:
  `redaction`, `incidents` and the trace store. With the projector live runs (about 7 s), they are
  what #210 and #211 found a ledger-only or record-only push skips.
- The useful direction is to promote those suite-only checks to guards and delete the 15
  duplicates. Named here, not opened.

Disposition: see ledger #217.
