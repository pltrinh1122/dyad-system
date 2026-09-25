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

## Amendment — d-work #159 (2026-09-24, property 2: the suite is the runner's to run)

**Claim:** a release that ships a push-time test gate must also ship the directive to use it —
the Agent defers the suite to that gate and does not hand-run a whole test root.

Occasioned by an Operator prompt during the release d-work #158, and by #154's audit: the capability
to run the suite cheaply had existed all along (`check_rule_12` sets `DYAD_NO_NESTED_TESTS` for the
child it spawns), and the Agent still paid about three times for it, 134 times in one session,
3,894 s — the largest single number in that audit and required by no Rule.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A Rule that says "prefer this command" is not a Rule: Rule-4 wants a process binding, not a style tip. | Survives, scoped | It binds what the Agent does before asking for a Done-`Y`: the evidence it cites comes from the gate, not from a hand-run whose environment it may have forgotten. Written as a property of Rule-12's own check, never as advice. |
| 2 | Rule-13 already makes recurrence propose code, and #155 built it — the directive is redundant. | Refuted | Rule-13 binds the *plan* that proposes code. Nothing said the Agent must then use it, and the audit measured exactly that gap. |
| 3 | The gate cannot be deferred to where it does not run: no remote, no `origin/main`. | Refuted by #158 | `cmd_guards` returned before the gate on an unresolvable base; #158 moved the suite above that return and made an unknown range run it. This property lands after that. |
| 4 | "Never hand-run" is too absolute: a failing case needs its own output. | **Confirmed — and the property says so** | It names `dyad check --tests <target>` for one module, class or method as the debugging path, and reserves the objection to a whole root, which the gate has already covered. |
| 5 | It slows the Agent: it must push to learn that a test fails. | Survives, scoped | It must push *or* run one target. What it may no longer do is re-run 490 tests it did not change. |
| 6 | The directive belongs in the incident-hardening play-book (#137), not in a Rule. | Refuted | That play-book is a procedure for a recurring decision about incidents; this is a standing constraint on every d-work, and a play-book is read by a Rule, never instead of one. |

Pairwise (Rule-5): 12–14 property 3 owns *where* the kernel-only path runs and when it is the merge
evidence; property 2 owns *who runs Rule-12's suite*, and cites Rule-14 rather than restating it.
12–13 Rule-13 owns the move from inference to code (recurrence proposes it); property 2 owns the use
of the code once it exists — no shared ownership. 12–11 the runner is Rule-11's and runs the pass;
Rule-12 keeps its check's semantics, unchanged. 12–3 a d-work's completion evidence is Rule-3's; this
property says only which run produced it. 12–1, 12–2, 12–15, 12–16, 12–20 untouched. Coherent,
orthogonal. Disposition: see ledger #159.
