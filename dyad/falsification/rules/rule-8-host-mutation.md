# Falsification record — Rule-8 (host mutation), gap E5 (ledger #61)

**Claim:** every host action the Agent takes can be classified, authorized at the level its
class demands, and recorded, by a Rule.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Class edges are fuzzy (`git config` is not a repo transaction; is it a host action?). | Survives | Definition by exclusion: not a repo transaction, not read-only → host action. `git config` is reversible. The plan lists each action with its class for review. |
| 2 | The Agent classifies its own actions. | Survives, scoped | Doubt resolves to destructive; the class is in the plan the Operator authorizes. Inference, as all of Rule-2. |
| 3 | The change-log row is written after the fact and can be skipped. | Survives, scoped | E8 (#65) will make the row part of the completion evidence; until then its absence is a stated breach. |
| 4 | A stated undo can be wrong. | Survives | The undo is in the plan and tried where cheap; an untested undo makes the action destructive. |
| 5 | The harness permission mode already gates risky commands. | Refuted as replacement | Per-command, outside the corpus, Operator-configured. Rule-8 ties the action to a plan, a class and a record. Named in Boundaries. |
| 6 | Number: Rule-7 is in backlog (#54); numbering 8 leaves a hole. | Survives | Numbers are ids, not an order; Rule-7 keeps its number when it lands. |

## Rule-5 pairwise statement (Rule-8 added; Rule-3 edited)
- 8–1: host ≠ repo; Rule-1 names Rule-8 in Boundaries (infra PR); one-way. 8–2: Rule-8 declares the
  destructive-action counter-prompt under its own `## Ratification events`; Rule-2 applies by
  reference and is not edited (G5). 8–3: Rule-3 names
  Rule-8 in Boundaries; Rule-8 names Rule-3; the plan is Rule-3's, the class is Rule-8's. 8–4:
  block conforms. 8–5: this statement. 8–6: five terms added, owner 8, used by 8 (and 3).
  Coherent, orthogonal.
- 8–18 (Rule-18 added, ledger #128): Rule-8 keeps class, authorization and the change-log row;
  Rule-18 owns the delivery form of a command the Operator runs for the Agent. Rule-8 names 18 in
  Boundaries and one Conduct bullet; ownership is not shared. Coherent, orthogonal.

Disposition: see ledger #61.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
text moved to `crafts/sysadmin/rules/host-mutation.md` (#155): the class table with its examples, Conditions bullet 4's read-before-act procedure, Conduct bullet 2's column list; the change-log seed to `crafts/sysadmin/templates/CHANGELOG.md`; the guard to `crafts/sysadmin/guards/changelog.py` (label `sysadmin/changelog`). Kept (attack 3 of plan #155): the three class names with their authorization levels, the blocking-question sentence, detect-don't-dispose, the row's existence, never-from-a-subagent, ops-script delivery. Pairwise (Rule-5): 8–18 and 8–19 unchanged in direction (Boundaries name them one-way); 8–4: block holds (intent 1, target 1, boundaries 6, conditions 4); 8–6: rows `read-only`, `reversible`, `destructive`, `change log`, `undo` left the Agent vocabulary for the craft's `CRAFT.md`; `host action`, `blocking question`, `mutation` stay, used by 8; 8–20: the change-log kinds resolve through the craft guard, skipping when absent; 8–21: the guard is a craft guard (second root). Coherent, orthogonal.
