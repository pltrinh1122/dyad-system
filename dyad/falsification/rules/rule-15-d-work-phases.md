# Falsification record — Rule-15 (d-work phases) (ledger #105)

**Claim (operator, 2026-09-13):** d-work activities are resistant to interruption; planning
precedes execution; execution can occur at any later time.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Plans live only in chat; an interrupted session cannot execute what was authorized (two reboots proved it). | Confirmed | The plan is a file written before the counter-prompt; the plan-Y binds to it. |
| 2 | Plans as files double the writing. | Refuted | The reply reproduces the file; same text, now checkable. |
| 3 | Deferred execution runs a stale plan against a changed repo. | Confirmed | Plan names its base commit; execution re-plans if `main` moved past a touched file. |
| 4 | A new state widens the plan gate. | Survives | `planned` is accepted exactly where `open` is; tested. |
| 5 | Overlap with Rule-3. | Survives | Rule-3 owns lifecycle and forms; Rule-15 adds the stored plan and one state, named in Rule-3. |
| 6 | The live-package test pinned the Rule count (13), so adding a Rule breaks it. | Confirmed | Test asserts >= 13 and no failures; a count is not a shape. |

## Rule-5 pairwise (Rule-15 added; Rule-3 edited)
- 15–3: one-way, Rule-3 cites Rule-15 for the phases; no shared ownership. 15–2: the plan-Y is
  Rule-3's event, bound to a file now. 15–16 (pending): Rule-16 relocates files; Rule-15 names
  what a plan file holds. Others unchanged. Coherent, orthogonal.
## Rule-6: `planned`, `plan file`, `base commit` added, owner 15.

Disposition: see ledger #105.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
Enforcement names the PR guard `dyad/guards/agent/prs.py` (was `dwork_link.py`; Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
