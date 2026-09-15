# Falsification record — syseng craft rule `verifiable-code.md` (d-work #162)

**Claim:** Rule-12's p1, p3, p4 and the test mapping are craft practice; the kernel keeps p2.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 12.3 | Overlap with Rule-11 p5 (scripted, tested install). | Survives | Rule-11 keeps "built and installed by one code path, tested in CI"; this rule keeps how the path is chosen. |
| 12.5 | More code is more surface. | Survives | Unchanged: the check is the condition of entry (Rule-12 p2, kernel). |
| 162.7 | Two owners for "a module has a test". | Survives, scoped | Runner runs; craft maps (`guards/tests.py`); `check_rule_12` no longer maps. |
| 162.13 | The plan's craft mapping `crafts/<craft>/tests/test_<entity>.py` differs from the #155 layout `tests/guards/test_<entity>.py` on `main`. | **Confirmed** | The rule and the guard keep the layout on `main` (`tests/guards/` for a craft guard); reported as a difference from the plan. |

Cut from: Rule-12 p1, p3, p4 and Enforcement's mapping (`dyad/falsification/rules/rule-12-verifiable-code.md`, amendment #162).

Disposition: see ledger #162.
