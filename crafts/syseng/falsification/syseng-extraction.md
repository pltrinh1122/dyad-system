# Falsification record — the syseng craft's extraction (d-work #162)

**Claim:** Implementation discipline — naming, run-time invariants, the test mapping, imports,
determinism, idempotence — is a craft, not the core process: it leaves Rules 11, 12, 13 and 14, the
sysarch `projection.md` and the sysadmin `ops-scripts.md` for `crafts/syseng/rules/`, and the core keeps
only the protocol code that runs every session and the kernel sentences Rule-2's Binding relies on.
The attack table is plan #162's, as executed (`agent-corpus/d-work/plans/162.md`).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Import-time invariants slow every command and break `--help`, `--list`, the projectors' imports and the tests' module loads. | **Confirmed** | Never at import: `INVARIANTS` is a list literal; `check_invariants` runs in the runner's pass (`check`, `check --guards`, `--evidence`) and at `dwork new|state` and `runbook.run`. `--help`/`--list` print no `[invariant]` line (`test_package.InvariantPassTests`). |
| 2 | Invariants duplicate unit tests. | Survives, scoped | Different reader, different time: a test asserts once that every invariant holds (the loop in every guard test); the invariant runs in production, is listed by name, projected (entities column) and reported per name. |
| 3 | The naming guard false-positives on legacy files; grandfathering by date hides drift. | **Confirmed** (two allow lines at execution, not four: `server.yml`, `rule-sets.md`; the UPPER_SNAKE host docs and `microphone_test.sh` are claimed by no kind, so no line) | `allow: <path> # <reason>`; a stale line fails, an unneeded one warns; the count is in the summary. |
| 4 | An `assert` grep hits strings, comments and prose. | **Confirmed** | `ast.Assert` nodes over Python files only (`test_invariants.ScanTests.test_assert_outside_tests_fails_by_ast_not_grep`). |
| 5 | A craft guard that reads core code crosses zones. | Survives, scoped | Reading is not a transaction; the semantics are syseng's, the runner discovers the guard like any other (S4); a system without syseng runs none of them. |
| 6 | `INVARIANTS` as data is indirection for no gain. | Refuted | The sentence-name is what the evidence prints and the surface shows; a list is countable and sortable; the four contract invariants are appended by the runner, never repeated per guard. |
| 7 | Rule-12's kernel and syseng's test mapping share one concern. | Survives, scoped | Runner: "run the tests" (`check_rule_12`); craft: "every module has its test at the mapped path" (`guards/tests.py`). Two predicates, two owners. |
| 8 | sysadmin's `ops-scripts.md` citing syseng makes one craft depend on another. | Survives, scoped | #161 chose it; the cite is a path; the sysadmin rule keeps one sentence per moved property so it reads alone (record `ops-scripts.md` 162.1). No `requires:` declared: the guards check shape, not the citation. |
| 9 | The invariant count is chosen to look thorough. | Survives, scoped | 142 at execution (29 modules; four contract invariants per guard, 20 guards, are 80 of them). Each named one names a fact a guard or incident relied on; the Operator may strike any. |
| 10 | Moving Rule-11 p5/p6 and projection p3/p5 out leaves core code owned by a craft. | **Confirmed** | Rule-11 keeps one-line stubs owning the data (`package_rules.txt`) and the check (`check_generated`, `dyad build|install`); the craft owns the discipline. |
| 11 | The plan binds to text #154–#160 changed. | **Confirmed** | Re-read at execution: Rule-17 gone (its p3/p5 lifted from `projection.md`); Rule-18's mechanics cut from `ops-scripts.md`'s marked block; craft-guard discovery and `crafts/` resolution already on `main`; `vocabulary.py` gains the `craft` owner literal here. Differences are in the completion reply. |
| 12 | The register's sources include entities only a craft provides; `sources-are-entity-keys` fails on a core-only install. | **Confirmed** (found by the invariant itself, `test_scratch_install_without_a_craft…`) | `references.CRAFT_ENTITIES` names them (`changelog`, `ops`, `command`, `event`) and a fourth invariant keeps that set disjoint from the core's entities; `incident` joins `NON_GUARD_SOURCES` (no guard, plan #151). |

Disposition: see ledger #162.
