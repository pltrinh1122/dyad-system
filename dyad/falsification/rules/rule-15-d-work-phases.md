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

## Amendment — d-work #290 (2026-10-14, an accreted row's plan is the mandate's)
**Claim (Operator, 2026-10-14, plan #290 revision 5):** a row the Agent opens while executing
another, inside the **mandate scope** the authorized plan states, carries no plan of its own. Phases
gains one bullet: such a row has **no planning phase of its own** — its plan *is* the mandate's plan
file, which the mandate's plan-`Y` already bound — so it carries no base commit of its own and no
drift check, and re-planning fires on the mandate's base commit for the parent and every row
accreted under it together. Today that gap is **silent rather than stated**: `plans.py` and Rule-20's
`plan.base->commit` judge only the plan files that exist, so nothing fails and nothing says so.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 7 | Phase 1 is unconditional — "the plan file exists first" — so a row with no plan file breaks this Rule outright. | **Refuted.** A plan file does exist: the mandate's, written before the plan-`Y` that authorizes the class, as phase 1 requires. What the accreted row lacks is a plan file *of its own*, and phase 1 binds the plan-`Y`, not the row. | The row's `disposed` entry names the file the `Y` bound to — `<date> Y plan (mandate #<id>)` — so the plan a reader must fetch is identified from the row alone, which is what phase 2's "begins by reading the plan file" needs. |
| 8 | The drift check then never fires for an accreted row: `main` can move past a file the mandate's plan touches while a child row executes, and nothing re-plans. | **Confirmed, and it is the gap the sentence names.** The mandate's own base commit is the only one there is, so drift is judged once for the whole tree rather than per child. Rule-20's register already skips a terminal row's `plan.base->commit` silently (property 2), and an accreted row has no such reference at all. | Stated rather than solved: the mandate's base commit governs every row accreted under it, and a child whose touched files have moved under it is an **escalate edge** — reported and asked, not re-planned in silence. The per-row base commit is named as a follow-on, with the `mode` field as the field a guard would read. |
| 9 | Survivor **3–15** of Rule-3's `#137` amendment says the opposite in so many words: "each mode's child d-work stores its own plan before its plan-`Y`". | **Refuted there, by name** (Rule-3's record, amendment #290, attack 1): 3–15's coherence half — the exercise adds no phase to this Rule — stands verbatim and is what the pairwise question actually asked; its plan half is replaced for rows inside a stated mandate scope and survives for every escalated row and every plan that states no scope. | This Rule gains **no phase** and loses none: planning still precedes execution, and execution still begins by reading a plan file. Which file, and whose plan-`Y` bound it, is all that changes. |
| 10 | A plan-less row is invisible to another session: Rule-16's presence `files` union is built from stored plan files, so an accreted row appears in `rows` and contributes **nothing** to `files` — a loss in exactly the coverage that store was built for (two sessions on *different* rows about the *same* file). | **Confirmed, and it is the design's own cost to another Rule's store.** `sessions.touch_from_open_rows` (`dyad/guards/agent/sessions.py`) reads `plans/<id>.md` for each `open` and `planned` row of the session; there is no file to read. | Stated in Rule-16's Presence section rather than fixed here: the files are named in the **mandate's** plan file, and reading a child's files through its `refs: parent #N` is the follow-on #290's plan names. Until then the mandate's own row carries the union for the whole tree, which is why the mandate is `open` while its children work. |

**Pairwise (Rule-5).** **15–3**: one-way as before — Rule-3 owns the lifecycle, the mandate scope and
the accreted list; Rule-15 owns what a plan file holds and when it is read. **15–2**: the plan-`Y`
is Rule-2's event, now bound to a file *and* a class (its record, amendment #290); Rule-15 names only
the file. **15–16**: the row file carries the pointer and the optional `mode` field, and Rule-16's Presence
section records the `files`-union loss (attack 10); Rule-16 owns the store and the table. **15–7**: the mandate's words are Rule-7's; a plan file is still the Agent's
text and still not a provenance record. **15–20**: an accreted row has no `plan.base->commit`
reference, so no kind is added and none is left unresolved. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #290.
