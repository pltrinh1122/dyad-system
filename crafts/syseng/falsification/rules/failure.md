# Falsification record — syseng craft rule `failure.md` (d-work #27; home by d-work #35)

**Claim:** Systems should fail early and fail loud (Operator prompt, 2026-09-16).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Early" means abort at the first failure. | Refuted | `invariants.md` p3 bans `assert` partly *because* it "stops at the first failure", on the Operator's own rule at #161. Survivor: early is the earliest knowable *point* (p1's ladder), not a moment to stop at. |
| 2 | "Loud" means every issue becomes a hard failure. | Refuted | Standard usage opposes *silent* failure, not *soft* failure. A `skip <kind>: <reason>` line is loud without being fatal, and the absent-store skip exists so a fresh install is not red (Rule-11 p5, Rule-20 p2). Survivor: loud covers what was not checked as well as what failed; loud and fatal are independent axes (p2, p3). |
| 3 | Taken literally the claim contradicts four ratified positions at once — `invariants.md` p3 and p4, Rule-20 p2, Rule-11 p7, Rule-7's warn-not-fail. | **Confirmed** of the literal reading | Which is why the rule states the reading this system already holds rather than a new one, and cites all four by name rather than overriding them. |
| 4 | This re-owns Rule-20 property 2's severity. | Survives, scoped | The orthogonality line the rule must hold: per-entity severity stays with the Rule that owns the entity. *Severity is not this rule's to set* states the stance and defers every decision by name; deciding one would be taking another Rule's concern. |
| 5 | A rule with no mechanical check is decoration, in a system built on mechanical checks. | Survives, scoped | The honest cost, conceded rather than argued away — as `projection.md`'s "whether a surface is legible … is inference" is. Its bite: plans cite it and it names the ladder deciding where a future check belongs (#25 is its first instance). Making it mechanical means a guard per instrument, never a checker for a stance. |
| 6 | **sysarch, not syseng** — the Operator said *architecture*, and Rules 17 and 21 were both retired into sysarch Tended rules at #160, so a rule about how checks are built and reported has a precedent there. Raised independently by a concurrent session under d-work #33, which *refuted* the move. | Refuted by **#35** | The precedent is narrower than it looks: Rule-17 was projection *surfaces* and Rule-21 *guard containment* — layout and contract, which is why they sit beside `manifest.md` and `stores.md`. Neither says what a run does on finding a fault; `invariants.md` does, and it is syseng. Two of p1–p3 are run-time behaviour and the third places a *detection*, not a file. Placing it in sysarch would split one concern across two crafts — sysarch owning where a fault is detected, syseng owning what a run does having found one. Survivor: `crafts/syseng/rules/failure.md`. |
| 7 | Two sessions falsifying one claim is waste, so #33 should have been silent. | Refuted | It is the two-models invariant working. #33 declined to re-encode the rule *text* — the actual duplication — while contributing the strongest counter to attack 6, carried above rather than discarded. |

Cut from: nothing — new text (plan `agent-corpus/d-work/plans/27.md`, home by plan `.../35.md`).

Disposition: see ledger #27.
