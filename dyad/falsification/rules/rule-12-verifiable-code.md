# Falsification record — Rule-12 (verifiable code), Architecture Rule 2 (ledger #74)

**Claim (operator, 2026-09-13):** during implementation, select the path that maximizes the
yield of reusable code, because code can be mechanically verified.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Maximize" as a sole objective licenses scope growth against the plan-`Y` and unplanned refactors. | Confirmed | Choose among paths that satisfy the plan; reuse beyond scope is a new plan (property 4). |
| 2 | "Code can be verified" is a claim: none of the five guards has a test. | Confirmed | Code is verifiable only when it ships with its check (property 2); audit V1 records the gap. |
| 3 | Overlap with Rule-11 property 5 (scripted, tested install). | Survives | Rule-11: the package is tested; Rule-12: how to choose the path that yields testable code. One-way, named. |
| 4 | Some checks are inference-only (Rules 2, 5, 9, 10). | Survives | Property 1: what cannot be checked mechanically stays inference and says so. |
| 5 | More code is more surface. | Survives | The check is the condition of entry; unchecked code does not enter. |

## Rule-5 pairwise statements (Rule-12 added)
- 12–1: no paths. 12–2: no event. 12–3: scope is the plan's; one-way. 12–4: block. 12–5:
  this statement. 12–6: two terms. 12–8: a host action is not code; disjoint. 12–9: the path
  choice is a claim in the plan, falsified there. 12–10: alternatives are framed per Rule-10.
  12–11: named in Boundaries, one-way. Coherent, orthogonal.

## Rule-6: `implementation path`, `mechanical check` added, owner 12.

Disposition: see ledger #74.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
Enforcement: `check_rule_12` maps `dyad/guards/<corpus>/<entity>.py` → `dyad/tests/guards/<corpus>/test_<entity>.py` beside the `scripts/` mapping (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
`check_rule_12`'s mapping gains the craft branch (`crafts/<craft>/guards/<e>.py` → `crafts/<craft>/tests/guards/test_<e>.py`; a craft script's, when one exists, → `tests/test_<n>.py`) and runs each present `crafts/<craft>/tests/` as its own suite; Enforcement says so. Pairwise: 12–21 as in `rule-21-guard-containment.md`; 12–11: the runner still owns no semantics. Coherent, orthogonal.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
p1's design half restated in `crafts/sysarch/rules/guards.md`; `check_rule_12`'s mapping gains a craft's `projectors/`
(`crafts/<craft>/projectors/<n>.py` → `crafts/<craft>/tests/test_<n>.py`) so the moved projector code stays checked on every
push (plan #160 attack 5); Boundaries name the craft rules. p1's implementation half, p3, p4 stay pending #162 (D1).
Pairwise: 12–11 as in `rule-11-distribution-structure.md`; 12–20 unchanged. Coherent, orthogonal. Disposition: see ledger #160.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
p1 (code over inference), p3, p4 and Enforcement's test mapping moved to `crafts/syseng/rules/verifiable-code.md`;
the kernel keeps one property (code carries its check, run in CI) and gains the term `invariant` (Rule-6, owner 12):
the check a module carries for its own model, run by the runner's pass before any check (`dyad check`,
`check --guards`, `--evidence`: `[invariant]` lines) and at the mutating call sites (`dwork new|state`, `runbook run`);
its form (never `assert`; `INVARIANTS`, `check_invariants`, `InvariantError`) is `crafts/syseng/rules/invariants.md`.
`check_rule_12` keeps "run the tests"; the mapping is the craft guard `syseng/tests`, the `assert` ban and the
must-declare check the craft guard `syseng/invariants` (plan #162 attack 7: two predicates, two owners). `implementation
path` and `mechanical check` leave the Agent vocabulary for the craft's `CRAFT.md`; the Target keeps the phrase and
means the craft's sense. Pairwise: 12–11 the runner runs the pass, Rule-11's Enforcement names it, Rule-12 owns the term;
12–3 a false invariant is an incident (Rule-3's form, referenced); 12–20 unchanged; 12–13, 12–14 unchanged. Coherent,
orthogonal. Disposition: see ledger #162.
