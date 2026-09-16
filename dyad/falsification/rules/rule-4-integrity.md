# Falsification record — Rule-4 (rule integrity)

**Claim (operator, 2026-09-12):** each Rule satisfies integrity criteria: clarity of intent,
target, boundaries, conditions; and constraints intent[1] imperative, target[1],
boundaries[1+], conditions[1+].

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Rule-4 must satisfy itself or it is void. | Passed | Rule-4 carries the block; the script checks it like any other. |
| 2 | "Clarity" (criteria 1–4) is not decidable by a script. | Survives, scoped | Counts (5a, 5c, 5d, 5e) are mechanical; clarity and imperative mood (5b) are inference at falsification. Stated in the rule. |
| 3 | Target[1] fails on Rule-1, which governs commits *and* PRs. | Refuted | Target is "a repo transaction"; commit and PR are its two kinds. Rule-2: "a ratification event"; Rule-3: "a d-work". |
| 4 | Rule-1's text is in the infra zone; the retrofit and the mechanism cannot be one PR with the agent-zone retrofits. | Survives | Two PRs, agent first (no CI yet), then infra (Rule-1 block + script + workflow) so the check is never red on `main`. |
| 5 | The Rule-1 stub in `rules/` will fail the check as a Rule without a block. | Refuted | The script skips the stub by name; the stub says so. The Rule is the `## Rule-1` section of root `CLAUDE.md`, which the script parses. |
| 6 | A block is boilerplate that drifts from the prose below it. | Survives, scoped | The block is the *normative summary*; on divergence the block wins and the prose is a bug. Rule-5's coherence trigger fires on every rule edit. |
| 7 | Overlap with Rule-5: both trigger on a rule change. | Survives | Same trigger, disjoint concern: Rule-4 = shape of one Rule; Rule-5 = relations among Rules. Each names the other as out of scope. |

Disposition: see ledger #49.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/rule_integrity.py` → `dyad/guards/agent/rules.py` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #154 (2026-09-14, craft reframe)
Boundaries, Tended-Rules bullet: Tended Rules live in `workstation-corpus/rules/` or in a Tended
craft's `rules/`; the guard names the core craft. No block change (counts unchanged).
| # | attack | result | survivor |
|---|---|---|---|
| 8 | Rule-4's target says "a file in `dyad/rules/`"; the Homes sentence (Rule-5) says Architecture Rules become Tended in `crafts/sysarch/` — Rule-4's classification and Rule-5's target disagree once #160 lands. | Survives, scoped | Today nothing moves and both stay true. The sentence states the future home with the d-work (#160) that edits both targets, with their records. #154 does not pre-edit them: that would describe a tree that does not exist. |

Pairwise: Rule-4 still classifies (Agent vs Tended); Rule-11 names that classification in its
Boundaries as not its own; Rule-5's Homes paragraph scopes the sweep, not the classification.
Coherent, orthogonal.

Disposition: see ledger #154.
## Amendment — d-work #156 (2026-09-14, the craft guard)
Boundaries, Tended-Rules bullet: the craft guard warns on Agent-process tokens in a Tended craft's rules; the
scan is Rule-4's (`rules.py check_tended`, README exempt, tokens data in `crafts_rules.txt`); the classification
stays inference (plan #156 attack A12: a fail would force editing a Tended Rule to satisfy a guard, which Rule-8
forbids). No block change. Pairwise: see `rule-11-distribution-structure.md` (11–4). Coherent, orthogonal.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
Rules 17 and 21 removed from `dyad/rules/` (numbers retired, never reused; the README says so); the guard counts the files
present, so a numbering gap is not a miss. Boundaries already name a Tended craft's `rules/` (#156). No block change.
Disposition: see ledger #160.
