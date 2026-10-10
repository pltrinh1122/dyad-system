# Incident mode L — a plan ordering no disposition sequence can authorize

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10; 5 of the 140 rows.*

## Definition
The mechanism is that a plan is written and falsified against *what* it changes — which files, which
zone, which PR, whether the change is owed — and never against *which disposition authorizes each
step*. The plan is then authorized, execution starts, and the sequence stops at a step whose
authorization the earlier steps have already consumed or foreclosed: a second PR that cannot exist
for the Operator to review until the first merges, a rebase that needs a push after the Done-`Y` has
already set the row `done`, a `.gitignore` line blocked by the dirty-tree refusal it exists to
remove, a phase 1 that must read a ledger its own PR-1 is still adding. The plan is internally
consistent, deliverable in isolation, and impossible in the only order the Rules permit.

**What would have to change.** The plan's falsification must take the authorization sequence as one
of its objects: for each step, which disposition authorizes it and which steps that disposition has
already closed — so the question "what authorizes this step" is asked in writing, before the plan-`Y`
is asked, rather than discovered by a guard refusing a push.

Boundaries against the neighbours it is most easily confused with:
- **K, a plan incomplete against its own text** — K's plan is deliverable in some order and part of
  it was not delivered; L's plan has no admissible order. Test: is there a disposition sequence that
  would have delivered the whole plan? Boundary row: row 33 (#32) reads as K — item 7 simply was not
  delivered — and is L because the plan's own sequencing, PR 2 after PR 1 lands on `main`, cannot
  coexist with `merge-disposition: with-done`, which merges a d-work's PRs at its own Done-`Y`.
- **M, no legal order, no verb** — M's impossibility is in the repo's own fences (two zones, two
  guards, no order of PRs satisfies both); L's is in the disposition chain. Test: name what blocks
  the step — a guard over paths, or a `Y` that has been spent. Boundary: row 2 (#156, the
  craft-versus-`BUNDLE.md` deadlock) is M; row 84 (#200) is L, and its quoted FAIL is `#196 is done,
  not open` — a row's state the Done-`Y` set, not a zone.
- **A, acting before the authorizing disposition** — L is readable from the plan text before any act;
  A is readable only from the act. Test: would following the plan exactly have produced the fault?
  Boundary: row 84 is L because plan #196 prescribed the impossible sequence; had the rebase been
  pushed anyway without a new plan-`Y`, that push would have been A.
- **T, a stale or partial view of shared state** — T's state moved under the Agent; L's state was
  written by this same Agent and never read back. Test: was the contradicting fact already in the
  corpus when the plan was written? Boundary row: row 73 (#185) — the plan said "#190 owns the
  bytecode-retained profile" while row #190's `refs` already read `185`, both facts the Agent itself
  had recorded.

## Incidents (5)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #32 | plan #32's item 7, PR 2 correcting a sysarch craft rule, undeliverable in the d-work: it was sequenced to open only after PR 1 landed on `main` | under `merge-disposition: with-done` a d-work's PRs merge at its own Done-`Y`, asked on the PRs as they stand, so PR 2 cannot exist for the Operator to review without an extra unplanned merge ratification for PR 1 alone |
| 2026-09-29 | #185 | the plan-`Y` was asked while the plan's own text said "#190 owns the bytecode-retained profile" and row #190's `refs` already read `185` | the dependency was recorded as data in two places and never read back before the counter-prompt, and nothing checks a plan's question against the `refs` of the rows it names |
| 2026-09-30 | #200 | the ratified-but-unmergeable deadlock recurred inside its own recovery: plan #196 prescribed merge, then rebase, then merge, and the rebase was refused with `#196 is done, not open` | a rebase requires a push and Rule-3 sets the row `done` before the first merge, so the plan prescribed a sequence its own authorization could not survive; three blocked merges in the chain |
| 2026-10-09 | #256 | plan #256 revision 1 verified that a `.gitignore` line works, by a throwaway `core.excludesFile`, and never asked how the line arrives; revision 2 proved the fix blocked by the thing it fixes | the plan's falsification attacked whether the line was owed and where it belonged, never the order of operations; the dirty-tree refusal precedes every guard and the plan gate resolves rows at `origin/main` |
| 2026-10-09 | #259 | plan #259's ordering had PR-1 merged first and alone before any mode record exists, while its phase 1 groups a ledger that includes PR-1's own rows | under `with-done` a PR merges at its d-work's Done-`Y`, and #259 cannot be done until the phases that were to follow that merge are delivered, so read literally nothing could happen after Part A |

## Pattern
All five are plans whose falsification sections attacked content and not sequence. Three of the five
(rows 33, 84, 138) break on the same clause: `merge-disposition: with-done` ties a d-work's merges to
its own Done-`Y`, which closes the row, and a step that needs the row open afterwards has nowhere to
stand. Two (rows 73, 122) break on a precondition recorded elsewhere in the corpus — another row's
`refs`, the dirty-tree refusal — that the plan did not consult. Four of the five cost one
counter-prompt and no lost work; row 84 cost three blocked merges and left three rows whose
`disposed` permanently names more merges than that moment executed.

Row 138's own cause cell states the shared mechanism in the form I have adopted here: "an ordering
written without asking what authorizes each step", and names row 122 (`:129` of `INCIDENTS.md`, F11
of plan #256) as the same shape.

Recurrence against each mitigation the consequence cells describe:

- **Row 33's mitigation, "named explicitly in #32's completion evidence rather than silently
  dropped; proposed there as a small follow-up d-work" (2026-09-16).** A disclosure practice, not a
  fence. Rows 73, 84, 122 and 138 all post-date it.
- **Row 84's mitigation, the single-PR shape: "one PR, one merge, nothing to push after the
  Done-`Y`" (2026-09-30).** The shape held for the d-work that adopted it; the mode recurred on other
  objects nine days later (rows 122 and 138). The same cell names what was *not* fixed — "Rule-3's
  completion clause still has no case for a ratified set that must merge in sequence. That is its own
  d-work with three instances of evidence behind it" — and that d-work exists, as `backlog` row #202,
  opened 2026-10-01 (`agent-corpus/d-work/rows/202.md`, state `backlog`, refs 185 186 196 200).
  Rows 122 and 138 post-date that row by eight days. The row made the candidate visible and prevented
  nothing, which is exactly what the play-book's exit 2 claims and all it claims.
- **Rows 122 and 138's mitigation, Rule-3's Incidents clause (`dyad/rules/RULE-3-d-work.md:217`): a
  plan revision and a fresh plan-`Y` before further mutation.** Both rows used it, both were caught
  before any mutation ran out of order, and row 138 post-dates row 122 by zero days — the same
  session, the same mechanism, on a different plan. That is the clearest statement available of what
  this mitigation is: a recovery that costs one counter-prompt, applied twice in one day, with no
  detection moved earlier.

## Mitigations (phase 2)
Read from the code and the Rule text today, 2026-10-10, in this worktree.

### 1. The plan file and its parts — shipped, and deliberately blind to sequence
- **What.** Rule-15 phase 1 requires the plan file before the counter-prompt
  (`dyad/rules/RULE-15-d-work-phases.md:14,20-22`); `plans.check_plan` checks that a plan opens
  `# Plan #<id>` with a matching id and carries a base-commit line, and warns when it names no intent
  or never mentions a part of `dyadlib.PLAN_PARTS` (`dyad/guards/agent/plans.py:45-60`;
  `PLAN_PARTS = ("intent as read", "mutation", "files touched", "base commit", "falsification")`,
  `dyad/scripts/dyadlib.py:455`).
- **Moment.** `plans.check_package` (`dyad/guards/agent/plans.py:62-67`) in the guard pass of
  `package.py check` and of `dyad check --guards`, i.e. at every push
  (`dyad/hooks/pre-push:4`, package loop `dyad/scripts/package.py:601-615`) and in every
  `check --evidence` block (`dyad/scripts/package.py:693`). `TRANSACTION = False`
  (`dyad/guards/agent/plans.py:20`), so there is no per-commit check.
- **Reaches.** None of the five rows. Every one of them had a plan file with all five parts; the
  guard's own docstring says why — "Existence of these parts, nothing more: what a plan says stays
  inference" (`dyad/guards/agent/plans.py:5-6`). This is the mode's central fact: the one guard over
  the entity where the fault lives declines, by design, to read it.
- **Recurrence after it shipped.** All five rows post-date Rule-15 (2026-09-13).

### 2. The plan gate, as a detector of L — shipped
- **What.** `prs.check` fails a cited row that is not `open`, `planned` or `blocked`
  (`dyad/guards/agent/prs.py:44-45`) and one with no `Y plan` (`:46-47`).
- **Moment.** `prs.check_transaction` over the commits being pushed, on any branch but `main`
  (`dyad/guards/agent/prs.py:59-67`), at every push through the pre-push hook
  (`dyad/hooks/pre-push:4` → transaction loop `dyad/scripts/package.py:628`); and at
  `dyad check --pr <base> <head>` (`dyad/scripts/package.py:655`).
- **Reaches.** Row 84 exactly, and it is the mechanism that *exposed* it: the row quotes
  `FAIL [guards] agent/prs [d-work]: #196 is done, not open`. It reaches row 122's second half too —
  the row names the plan gate resolving rows at `origin/main` as one of the two things that block the
  fix. It does not reach rows 33, 73 or 138, none of which reaches a push.
- **Limit.** It fires at the moment the impossible step is attempted, which is after the plan-`Y` has
  been spent and, in row 84's case, after the first merge. It can refuse the push; it cannot restore
  the ordering.
- **Recurrence after it shipped.** Rows 122 and 138 post-date it and are of the shape it does not
  see.

### 3. The reference register's `row.refs->row` resolver — shipped, existence only
- **What.** `("row.refs->row", "row", "refs", rows_refs, "row", row_exists)`
  (`dyad/guards/agent/references.py:409`) and `("plan.id->row", …)` (`:413`), `("plan.base->commit",
  …)` (`:414`).
- **Moment.** `references.check_package` in the guard pass of every push and every evidence run
  (Rule-20 Conditions; `dyad/scripts/package.py:601-615`).
- **Reaches.** Row 73's fault in its *data* and not in its *meaning*: the register resolves that row
  #190 exists, never that row #185's plan asks a question row #190's `refs` has already answered.
  Rule-20 property 1 is explicit that a resolver "decides that the target instance exists and nothing
  more". Reaches none of the other four.
- **Recurrence after it shipped.** Rows 84, 122 and 138 post-date Rule-20 (2026-09-14).

### 4. `merge-disposition`'s own escape clause — shipped as preference text, inference only
- **What.** "A PR whose d-work is *not* yet done still needs its own merge `Y`"
  (`preferences-corpus/PREFERENCES.md:28-29`).
- **Moment.** Inference, stated: nothing in `dyad/` or `crafts/` reads the key
  `merge-disposition`; the only preference keys any code reads are `host-path` and `host-zone`
  (`dyad/scripts/dyadlib.py:350-370`) and `ledger-pr-merge`, read by a projector as a Mandate rather
  than a fence (`crafts/countersign/projectors/project_countersign.py:52`).
- **Reaches.** Rows 33 and 138 as the way out, both retroactively: row 138's cause cell says the
  preference "names the way out in as many words". It reached neither plan before it was written.
- **Recurrence after it shipped.** Rows 33, 73, 84, 122 and 138 — all five.

### 5. `backlog` row #202 — a candidate, surfaced and never built
- **What.** `agent-corpus/d-work/rows/202.md`, state `backlog`, opened 2026-10-01: "Rule-3's
  completion clause has no case for a ratified set whose members must merge in sequence … three
  instances, #185/#186, #196, #200", `refs: 185 186 196 200`.
- **Moment.** None — it is a row, not a check.
- **Reaches.** Rows 33 and 84 by naming their clause; nothing by firing.
- **Recurrence after it shipped.** Rows 122 and 138, eight days later.

## Remediation candidate, under attack
**The candidate.** A sixth plan part. Add `authorization` to `dyadlib.PLAN_PARTS`
(`dyad/scripts/dyadlib.py:455`) and make `plans.check_plan` **fail** rather than warn when a plan
whose text names more than one step carries no `authorization` section — a section holding one line
per step naming the disposition that authorizes it (plan-`Y`, Done-`Y`, a per-PR merge `Y`, a
destructive `Y`, a release `Y`) and, for each, what that disposition has already closed. It fires in
the guard pass of `package.py check` and therefore at every push
(`dyad/hooks/pre-push:4` → `dyad/scripts/package.py:601-615`) and inside every `check --evidence`
block — which means it is already run before the plan-`Y` is asked, because a plan file reaches
`main` as a ledger-only commit whose push runs the same pass.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | `PLAN_PARTS` is pinned at exactly five by a fail-loud invariant: `("plan-parts-distinct", lambda: len(set(PLAN_PARTS)) == len(PLAN_PARTS) == 5 and "base commit" in PLAN_PARTS)` (`dyad/scripts/dyadlib.py:604`), enforced at import. A sixth part is a Rule-15 amendment, an invariant rewrite and a core-craft release — and pinning the present enumeration is itself a logged failure mode of this ledger (mode H, 6 rows). | survives, scoped | Only with the invariant rewritten to the new count in the same commit and Rule-15 phase 1 amended in the same d-work, which is the ordinary cost of a Rule change and not an obstacle. The mode-H risk is real and is the reason the count must move with the list rather than be loosened to a range. |
| 2 | Existence is not correctness. Plan #259 revision 1 could have carried an `authorization` section reading "step 1: plan-`Y`; step 2: Done-`Y`" and still been impossible — the fault is the *relation* between steps, which no existence check reads. Row 138 is exactly that fault, and `plans.py`'s own docstring already concedes the territory: "what a plan says stays inference". | confirmed | The check buys the question being asked in writing, never the answer being right. "Fences mode L" does not survive; "forces the mode's own question into the plan before the plan-`Y`" survives. Rule-5's Enforcement — no script can decide — holds for the ordering itself. |
| 3 | Coverage, row by row: rows 33, 84, 122 and 138 would have been prompted to state the authorizing disposition per step, and in each the contradiction is visible in one line once written. Row 73 would not: its fault is a dependency sitting in another row's `refs`, which an `authorization` section need not mention, and which only a state-aware resolver reaches. | survives, scoped | 4 of 5 by prompting, 1 of 5 untouched. Row 73 needs a separate, smaller thing: a resolver kind `plan.names->row.state` that warns when a plan's text names a row whose `refs` point at the plan's own row — a second candidate, not this one. |
| 4 | A failing check over 140-odd existing plan files fails the tree on its first run, and a check that must be bypassed teaches bypass — the lesson `dyad/falsification/rules/rule-1-containment.md` draws about hooks. | survives, scoped | Only as `plans.py` already handles its own history: the missing-part report is a *warning* for plans ratified before the part existed (`dyad/guards/agent/plans.py:55-59` and its docstring's note that "plans ratified before Rule-15 keep their form"). Scoped to fail only for a plan whose `base commit` is newer than the amendment, warn otherwise. |
| 5 | Rule-9 easy agreement: I agreed on first reading, because rows 122 and 138 both say in as many words that the plan "never asked what authorizes each step", so a part that asks it looks like the fix the rows themselves name. Pushed: a row's own account of its cause is the Agent's prose about its own fault, which is the weakest evidence in the ledger — and attack 2 shows the part relocates the judgement rather than mechanizing it. | confirmed (the easy agreement) | Accepting the candidate on the rows' own wording does not survive. It is accepted, if at all, as a prompt that costs one section and one invariant edit, on the explicit understanding that the judgement stays inference. |

## Proposed exit (phase 4)
**Exit 2 — a `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes.

The row would say: *Rule-15 phase 1 gains an `authorization` part — one line per plan step naming
the disposition that authorizes it and what that disposition closes — failed by
`plans.check_plan` for plans whose base commit post-dates the amendment and warned otherwise,
with `dyadlib.PLAN_PARTS` and its count invariant moved in the same commit.* It would have caught
rows 33 (#32), 84 (#200), 122 (#256) and 138 (#259) by forcing the contradiction into one written
line before the plan-`Y`; it would not have caught row 73 (#185), which needs the state-aware
resolver named in attack 3.

Two things belong in the Operator's view of this exit. First, `backlog` row #202 already stands for
the merge-sequence clause two of these rows break on, and rows 122 and 138 post-date it by eight
days — so this would be the second row naming a fence for this mode, and the honest reading of the
first one is that a row prevents nothing. Second, by attack 2 the part is a prompt and not a fence:
if the Operator wants exit 1 for this mode, the fence has to be something that reads the relation
between steps, and I did not find a shape for that which Rule-5's Enforcement would admit.
