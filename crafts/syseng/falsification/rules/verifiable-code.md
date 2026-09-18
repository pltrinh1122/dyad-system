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

## Amendment — d-work #94 (2026-09-18, the ladder, after ponytail)
**Claim:** `verifiable-code.md` says what a check must be (properties 1, 4–6) but nothing about
how small the implementation it checks should be. `dietrichgebert/ponytail` (evaluated
`agent-corpus/audits/2026-09-18-ponytail.md`, scored in its Part 2a) supplies a measured discipline
for exactly that gap. Falsified there (Part 1.4, seven attacks) and here (plan #94: P1/P2/P3
survive as one property; P4's form survives, its Rule-20 mechanism deferred to #96; P5 survives as
a template; P6 refuted as premature; P7 survives as a proposal, deferred to #97).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A path-selection ladder duplicates Rule-13 p1 (recurrence proposes code) and `imports.md` p1 (import over author). | Refuted | Rung 2 *is* Rule-13's trigger restated as a step, not a duplicate rule; rung 5 *is* `imports.md` p1–2, cited by reference, not re-stated. Property 7 is the order they compose in, which neither owns. |
| 2 | The never-simplify floor is already implicit — every Rule that classes an action (Rule-8's destructive class, Rule-7's credential residue) already protects it. | Survives, scoped | True per-Rule; nothing named the *general* floor a lazier implementation must not cross. Stating it once, beside the rung that could cross it, is cheaper than re-deriving it per Rule. |
| 3 | The check sentence loosens property 4's test mapping. | Refuted | It does not touch the mapping (one test per module, at the mapped path); it says what may be *inside* that test — no guard, no test file location, changes. |
| 4 | Adopting a mechanism (P4's wiring) as unfinished text-only is worse than not adopting it — an unenforced convention drifts. | Survives, stated | Named as a live risk in the amendment and in `naming.md`'s row itself (`checkable: no`); #96 is the closing move, not an indefinite deferral. |

Pairwise (Rule-5): unchanged — property 7 sits inside this craft's existing set, cites Rule-13 and
`imports.md` by reference rather than restating them, and the core Rule-12 kernel is untouched.
Coherent, orthogonal. Disposition: see ledger #94.
