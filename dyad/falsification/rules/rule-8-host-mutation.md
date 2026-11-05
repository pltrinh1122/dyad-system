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

## Amendment — d-work #593 (2026-11-04, the automaton as a party; accreted under mandate #570)
Intent, Conditions bullet 1 and Classes name a host action an automaton takes. Plan `agent-corpus/d-work/plans/593.md`
carries the full table; the attacks that bear on this Rule:

| # | attack | result | survivor |
|---|--------|--------|----------|
| P1 | The automaton is already a party. | Confirmed in the vocabulary (`party`, `automaton`, #556), refuted in the Rules | This Rule's Target was "every host action the agent takes"; the words exist, the Rule lagged. |
| P3 | The change log needs `actor: automaton`. | Survives as a reservation | Today the automaton takes no host action (its merges are repo transactions, Rule-1; the sweep is read-only). The craft's `actor` gains the value with its condition (plan step 3); this Rule only says when a row is owed, which is unchanged: every reversible or destructive action. |
| P4 | Rule-8 covers the automaton. | Confirmed (it did not) | read-only is free for an automaton; a reversible action is executed only from the ledger line that records the plan-`Y` naming it, deciding nothing (Rule-2 Enforcement); a destructive action is never an automaton's, since its counter-prompt is asked and answered live. |
| A1 | An automaton reading a plan-`Y` off the ledger is an automaton deciding what the plan meant. | Survives, scoped | It executes only an action the plan names verbatim, as the merge verb executes only a head a `Y done` names (Rule-2 Enforcement); anything that needs reading is no automaton's, and stays the agent's. |
| A2 | "Never destructive" is unenforced. | Survives, stated | Enforcement stays inference, as before; no automaton takes a host action today, and the run-book runner's `--as automaton` refusal of a non-read-only command is engineer's step 2, the mechanical form for run-book commands. |

**Rule-4.** Block holds: intent 1, target 1 (unchanged, `a host action`), boundaries 6, conditions 4.
**Rule-6.** `automaton` is now used by Rule-8; its `used by` cell gains 8 in #585's window (the vocabulary's single
writer). `host action` keeps its definition ("anything the agent does on the machine…"), which now reads narrower than
the Rule: its definition gains "or an automaton" in the same window. Both are reported to counsel, not written here.
**Pairwise (Rule-5).** **8–2**: Rule-2 Enforcement owns that the automaton is execution, never a disposer; Rule-8 cites it
and adds no ratification event; the destructive counter-prompt stays Rule-8's own. **8–3**: Rule-3 owns the plan-`Y` the
automaton executes from and, in #585, the sentence naming the automaton a party; no instruction differs. **8–14**: Rule-14
property 2 (this amendment's sibling) states the kernel an automaton's host needs; Rule-8 classes what it does there.
**8–16**: the automaton keeps no presence file (`auto` reserved); unaffected. **8–18**: an ops script is run by the
operator, never an automaton; unchanged. **8–19**: Rule-19 lets an automaton run `read-only` run-book commands, the case of
this Rule's free class; one direction each. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #593.
