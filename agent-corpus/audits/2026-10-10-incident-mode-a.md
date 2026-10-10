# Incident mode A — acting before the authorizing disposition

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10; 13 of the 140 rows.*

## Definition
The mechanism is that the act and its authorization are produced by one party in one turn, and the
act sits first in that party's habitual sequence. An act a counter-prompt authorizes — a merge, a
mutation, a host action, a delegation shape, a recorded disposition — is performed while the
counter-prompt is unasked or unanswered. The disposition is never in dispute: in every row of this
mode the `Y` either followed or would have, and only row 111 closed with a link permanently absent.
What fails is ordering against an authorization, never judgement about content, and the order that
wins is the one the Agent types: verify, merge, confirm, ask, rather than ask, receive, record,
merge.

**What would have to change.** The artifact that records the authorization must be written by a
command that cannot run before the disposition arrives, and the act must be in the same typed block
as that command, so the habitual sequence and the authorized sequence are the same sequence.

Boundaries against the neighbours it is most easily confused with:
- **B, a disposition recorded that the Operator never gave** — B's record is false and the
  authorization does not exist at all; A's record is true and merely late. Test: read the `disposed`
  entry against what the Operator sent. Boundary rows: row 20 (#18) is B — `dwork state 18 planned
  -d "Y plan"` for a question never asked; row 41 (#67) is A — the `Y` was real and fully specified
  the mutation, and the row and plan file it binds to were written after it.
- **L, a plan ordering no disposition sequence can authorize** — L's fault is in the plan text and
  is detectable before any act; A's fault is in the act, with the plan either silent or correct.
  Test: would following the plan exactly have produced the fault? Boundary row: row 84 (#200) is L
  because plan #196 *prescribed* merge-then-rebase-then-push; row 43 is A because the plan said
  nothing about executing before the `Y`.
- **P, unplanned cleanup under momentum** — P acts on work no plan names, while an authorization for
  other work exists; A acts on work the plan names, before the authorization exists. Test: is the act
  in the plan's mutation list? Boundary row: row 32 (#35) is A, not P — amending `plans/27.md` was
  plan #35's own mutation item 1.
- **V, enforcement routed around** — V meets a mechanism and goes past it (`--no-verify`); A either
  meets no mechanism or meets one that fails *after* the act. Test: did a check run and get
  overridden? Row 43 sits on this boundary: `agent/prs` did FAIL all three branches, and the FAIL was
  read as confirming evidence rather than as a block, which is A's reading of V's event.

## Incidents (13)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14 | #1 | ledger row #1 committed already in state `planned`, with no intervening `open`-state commit, and a doubled date in its disposition text | a row born `planned` carries its own authorization at birth, so the plan-`Y` is asserted by the same write that opens the d-work |
| 2026-09-14 | #16 | ledger row #16 committed already in state `planned`, the same main-fence FAIL as #1's, the same sequencing mistake repeated | second occurrence of the same ordering fault inside two days, with no mechanism between them |
| 2026-09-16 | #22 | a reversible host action, a scratchpad `python3`-to-3.12 symlink prepended to PATH, taken before its plan-`Y` | Rule-8 Classes authorizes a reversible action by the plan-`Y` of the plan naming it; the plan-`Y` came afterwards and named it retroactively |
| 2026-09-16 | #35 | plan #35's own mutation item 1, amending `plans/27.md`, executed in the same ledger commit that wrote plan #35, before the batch plan-`Y` | both artifacts are ledger files so writing them together felt clerical; the plan named the amendment as a mutation, which only the `Y` authorizes |
| 2026-09-16 | #47 | PR #35 merged with `gh pr merge` before the Done-`Y` counter-prompt was asked, under `merge-disposition: with-done` | the merge is Rule-2's own ratification event, reserved for clerical execution after that `Y`; the cause cell names momentum through identical cycles, an attentional slip |
| 2026-09-16 | #47 | the same PR #35 merge logged a second time, written under #68 because #47's own PR had closed before it could carry the row | one incident, two log rows; counted as two here because the reconciled set assigns both, and named as one occurrence in the Pattern |
| 2026-09-18 | #58 | PRs #45, #46 and #47 merged before the Done-`Y`, although `plans/58.md` itself said merged under one Done-`Y`; the counter-prompt then named closed PRs | second occurrence, same cause; the plan text did not interrupt the sequence, so the written plan was not the operative instruction |
| 2026-09-18 | #67 | PRs #50, #51 and #52 merged before the Done-`Y`, within an hour of the memory note about #47 and #58 | third occurrence; a principle-level note did not interrupt the motor sequence verify, merge, confirm, ask |
| 2026-09-18 | #67 | the d-work's `Y/N` asked before its row existed or its plan file was written | Rule-15 phase 1 puts the plan file before the counter-prompt, so the `Y` had no stored mutation to bind to |
| 2026-09-20 | #92, #103, #104 | code for three crafts written, committed to three branches, pushed, and PRs #78, #79 and #80 opened, all before the plan-`Y` was asked or received | Rule-15 phase 2 begins execution by reading the authorized plan; the combined-worktree verification pattern built for a pre-Done gate was reused one gate too early |
| 2026-09-22 | #110 | the d-work's own mutation written, committed and pushed and PR #95 opened before any plan-`Y`, the plan file and its mutation in one commit | same shape as the row above: the plan document and its delivered mutation treated as one lump instead of plan, authorize, execute |
| 2026-10-07 | #233 | the d-work closed on a Done-`Y` with no plan-`Y` at all, and local `main` fast-forwarded before the plan counter-prompt was asked | the plan file was written but its question never asked, so the authorization chain has one permanently missing link that append-only forbids repairing |
| 2026-10-09 | #260 | two forks launched to draft #259's Part A in the same reply that asked `Y/N: proceed with #260 as planned?` | the direction to delegate arrived as text on another row's plan-`Y`, and acting on it in the same reply read a disposition's text as its own authorization |

## Pattern
All thirteen skip a required ordering step, and in eleven of them the skipped step is the one that
*produces* the authorizing artifact — the `open`-state commit, the plan file, the asked question, the
`done` row. Three acts recur across the mode: a merge before the Done-`Y` (rows 34, 38, 39, 40); a
mutation, host action or delegation before the plan-`Y` (rows 21, 32, 43, 45, 136); and a row or a
question produced out of order (rows 13, 16, 41, 111). The mode is the largest in the population and
the longest-running: 2026-09-14 to 2026-10-09, 26 days, every week of the ledger.

Recurrence against each mitigation the consequence cells describe:

- **Row 13's fix, "commits split into open/plan-Y before push" (2026-09-14, conduct only).** Row 16
  post-dates it by hours, on the same shape. A conduct fix measured at one day.
- **Row 39's "a memory-cache note written" (2026-09-18).** Row 40 post-dates it by less than an
  hour, and its own cause cell says so: "a principle-level note did not interrupt the motor
  sequence". This is the mode's sharpest measurement. The note as first written stated the
  principle — merge only after the Done-`Y` — and a principle is read at the moment of reflection,
  not at the moment of typing. What was then rewritten, and is in the tree's per-machine cache today
  as `~/.claude/projects/-mnt-shared-data-dyad-dyad-system/memory/feedback_merge_after_done_y.md`,
  is an operational rule about a command block: `gh pr merge` appears only in a block that begins
  with `dyad dwork state <id> done -d …`, which cannot be typed before the `Y` has arrived. The note
  says of itself that only tying the merge command to the ledger's own record of the `Y` does the
  work. The three merge rows recurred against the first form and none has recurred against the
  second: no merge-before-Done-`Y` row appears after 2026-09-18, 21 days and roughly 190 ledger ids
  later. That is why three recurred against a note — the note changed what the Agent believed and
  not what it typed, and the fix that held changed the typed block.
- **Row 40's second mitigation, Rule-3's completion clause gaining the merge-sequence bullet
  (#68, 2026-09-18; `dyad/rules/RULE-3-d-work.md:131-134`).** Rows 43 (2026-09-20), 45 (2026-09-22),
  111 (2026-10-07) and 136 (2026-10-09) all post-date it. None is a merge, so the amendment's own
  sub-shape is clean; the mode moved to the plan-`Y` face, which that clause does not address.
- **#113's `concise-mode` + `delegation: plan-and-execute` coupling (2026-09-22), which the previous
  exercise's record credits with making rows 43 and 45 impossible where they happened.** Row 136
  (2026-10-09) post-dates it and is produced *by* the delegation shape it installed: two forks
  launched before the plan-`Y` that authorizes delegating. The fence named as the live cure is now
  the surface of the mode's newest instance. Stated plainly: the coupling moved the mode's object
  from a pushed branch to a launched fork, and nothing reads the launch.

Two log properties, stated and not corrected here (`INCIDENTS.md` is the main Agent's): rows 34 and
38 are one incident, the #47 merge, logged twice, both dated 2026-09-16, the second under #68 — so
thirteen rows carry twelve incidents. And rows 39 and 40 are dated 2026-09-18 in the log while
`rows/58.md` and `rows/67.md` date the same events 2026-09-17; the dates above are the log's, as the
reconciled set's are.

## Mitigations (phase 2)
Read from the code and the Rule text today, 2026-10-10, in this worktree.

### 1. A row cannot be born `planned` — shipped, three places
- **What.** `dyadlib.NEW_STATES = frozenset({"open", "backlog"})`
  (`dyad/scripts/dyadlib.py:443`), enforced by `dyadlib.require_transition`
  (`dyad/scripts/dyadlib.py:507-516`, "a new row starts in … not {after!r} (Rule-16)"), by the main
  fence `rows.check_commit` (`dyad/guards/agent/rows.py:150-151`), and by `dwork new` which only
  ever sets `open` or `backlog` (`dyad/scripts/package.py:955`).
- **Moment.** `require_transition` at `dyad dwork new|state`, before either write
  (`dyad/scripts/package.py:960-963`, 976-979); `rows.check_commit` at every push, through
  `dyad check --guards --pre-push` (`dyad/hooks/pre-push:4` → `package.py` `cmd_guards`,
  `dyad/scripts/package.py:583`, transaction loop at `:628`) and over each commit of a direct push
  to `main` (`rows.check_range`, `dyad/guards/agent/rows.py:155-162`).
- **Reaches.** Rows 13 and 16 completely — the write is now refused before it happens, and the fence
  catches it again if it reaches a commit. Reaches none of the other eleven.
- **Recurrence after it shipped.** No row of this shape after 2026-09-14. The two rows it covers are
  the two oldest in the mode.

### 2. The plan gate — shipped
- **What.** `prs.check` requires every cited `d-work #N` to be a ledger row at the base in state
  `open`, `planned` or `blocked` **and** to hold a `Y plan` disposition
  (`dyad/guards/agent/prs.py:44-47`). `"Y plan" not in row.disposed` is the only place in the tree
  that reads a disposition's text as authorization: a grep of `dyad/` and `crafts/` for `Y plan`,
  `Y done` and `Y release` outside tests returns `prs.py:4,46,47,71` and nothing else.
- **Moment.** `prs.check_transaction` (`dyad/guards/agent/prs.py:59-67`) on any branch but `main`,
  reading the range's commit messages as the PR body and the rows at the base, run before every push
  by the pre-push hook (`dyad/hooks/pre-push:4`, transaction loop `dyad/scripts/package.py:628`), and
  by `dyad check --pr <base> <head>` before a PR is opened (`dyad/scripts/package.py:655`).
- **Reaches.** Rows 43 and 45 exactly: a branch carrying a d-work's mutation whose row has no
  `Y plan` fails the push. It does not reach rows 13, 16, 21, 32, 34, 38, 39, 40, 41, 111 or 136 —
  a merge, a host action, a ledger-only commit, an unasked question and a launched fork each happen
  where this gate does not run. Two explicit holes matter for this mode: the gate returns `[]` on
  `main` (`:62-63`) and on a ledger-only range (`:64-65`, `dyadlib.ledger_only`), which is exactly
  why row 111's PR-less ledger range met nothing.
- **Shipped but conditional.** It runs only where `core.hooksPath` points at `dyad/hooks`. The
  install sets it (`dyad/scripts/package.py:753`) and Rule-1 Enforcement tells the Agent to set it
  (`dyad/rules/RULE-1-containment.md:47-50`), but no guard reads it: the only mechanism that looks is
  the audit play-book's own line (`dyad/playbooks/audit.md:66,69`), which is a procedure the Agent
  runs, not a gate. I could not establish from git history whether the hook was configured and
  running in this checkout on 2026-09-20 and 2026-09-22 — the package's history is squashed into one
  2026-09-14 commit (`52024e6`), so the gate's code is as old as those rows while the rows record
  pushes that succeeded. Rows 43 and 45 say `agent/prs` FAILed in a *combined verification*, i.e.
  after the push, which is consistent with the hook not having run at the push and inconsistent with
  it having run; I cannot verify which.
- **Recurrence after it shipped.** Rows 111 and 136 post-date it and are outside its reach by
  construction.

### 3. Rule-3's completion clause and Rule-2's Binding — shipped as Rule text, inference only
- **What.** "The reply that asks does not merge. The reply that receives the Done-`Y` merges, as
  clerical execution, after recording the disposition (`dyad dwork state <id> done`) — so the
  ledger's own record of the `Y` precedes every merge it ratifies. A merge before the `Y` is
  self-ratification (Rule-2) and an incident whatever the outcome (#47, #58, #67)"
  (`dyad/rules/RULE-3-d-work.md:131-134`); "No exemptions: a plan may be one line … but the question
  is asked" (`:55`); `Y` authorizes the mutation (`:52`); Rule-2's Binding (`dyad/rules/RULE-2-no-self-ratify.md:46`).
- **Moment.** Inference, stated: the Agent reads it when composing the reply. Rule-2's own
  Enforcement names one mechanical fence, `rows.py`, and says "Everything else is inference".
- **Reaches.** Every row of the mode in the sense that each breaches it; none mechanically.
- **Recurrence after it shipped.** Four rows post-date the #68 amendment (43, 45, 111, 136).

### 4. The row fence and the provenance transaction check — shipped, partial
- **What.** `rows.check_commit` refuses a direct commit to `main` that touches anything outside
  `<instance>/d-work/` and refuses an illegal transition (`dyad/guards/agent/rows.py:117-153`);
  `provenance.check_commit` requires a row's record to gain one `disposition` entry per `disposed`
  entry the same commit adds (`dyad/guards/agent/provenance.py:265-269`).
- **Moment.** Every push, per commit, on the kernel-only path (`dyad/hooks/pre-push:4`).
- **Reaches.** Row 111 only in its mechanical residue: `open` → `done` is a legal transition
  (`dyad/scripts/dyadlib.py:444-445`), so a Done-`Y` recorded with no `Y plan` before it passes both
  checks. Nothing reads the *order* of a row's disposition kinds. Row 111's own cause cell says "no
  guard sees it", and reading the code today confirms it.
- **Recurrence after it shipped.** Row 111 (2026-10-07) post-dates #191's transaction check
  (2026-09-29) and is precisely what it does not see.

### 5. Delegation and `concise-mode` — shipped as preference text, inference only
- **What.** `delegation: plan-and-execute` and `concise-mode: on`
  (`preferences-corpus/PREFERENCES.md:13,17`), with Rule-3 Scope's subagent clause and Rule-10's
  concise-mode bullet (`dyad/rules/RULE-10-proposal-framing.md:21-26`).
- **Moment.** Inference, stated: Rule-10's Enforcement is "Inference only, stated"
  (`dyad/rules/RULE-10-proposal-framing.md:30`). No code reads either key; the only machine reading
  of `delegation` anywhere is a *report* after the fact, `trace.py`'s `delegated share` line
  (`dyad/scripts/trace.py:547-551`).
- **Reaches.** Structurally fences rows 43 and 45 by moving execution into a fork that cannot push.
  Reaches none of the acts Rule-3 Scope reserves to the main Agent: merging, writing a row, running
  a host action, asking a question — rows 13, 16, 21, 32, 34, 38, 39, 40, 41, 111.
- **Recurrence after it shipped.** Row 136, which is a fault *of the shape this preference
  installs*, launched before the plan-`Y` that authorizes it.

Nothing in the tree fences the mode's two live faces — a Done-`Y` recorded with no plan-`Y`, and an
agent-side act such as a fork launch run on a disposition's text. For those two, this mode's only
mitigation is inference, stated.

## Remediation candidate, under attack
**The candidate.** A disposition-order check in the row fence: a row whose `disposed` gains an entry
whose text begins `Y done` while the chain holds no earlier `Y plan` entry fails. It lives beside
`rows.disposed_problems` in `dyad/guards/agent/rows.py` (which already judges only the entries a
range *adds*, `:85-92`), with the symmetric refusal in `package.py` `cmd_dwork` at
`dyad dwork state <id> done` (`dyad/scripts/package.py:965-980`), before either write. It fires at
two exact moments: at the CLI, before the row file is written, and at every push —
`dyad check --guards --pre-push` → `rows.check_transaction`
(`dyad/guards/agent/rows.py:164-173`), over each commit of a direct `main` push and over each commit
of a ledger-only branch (`check_ledger_branch`, `:175-188`), which is where a Done ledger commit
travels.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Coverage: it reaches row 111 and nothing else. Rows 34, 38, 39 and 40 wrote `Y done` into chains that already held `Y plan` — the chain was well formed and the *merge* was early, which no row-file state can see because the merge is a World act (Rule-14 property 3 keeps hosting out of the kernel). Rows 13, 16, 21, 32, 41, 43, 45 and 136 touch no `Y done` entry at all. | confirmed | 1 of 13 as prevention. Any reading of the candidate as a remedy for mode A does not survive; it survives only as a fence on the one face that produced a permanently unrepairable chain. |
| 2 | Forgeable by the mode next door: an Agent in row 111's position writes `Y plan` and `Y done` in one commit and passes. | confirmed | Prevention against a momentum fault does not survive; cost does. Two added `disposed` entries now require two new `disposition` entries each holding words (`dyad/guards/agent/provenance.py:265-269`), so forging it means fabricating two Operator utterances — mode B's fault, which the Operator's own copy of the chat contradicts. The candidate converts a silent missing link into a forged one. |
| 3 | It targets a shape that has happened once while the live face is row 136, an agent-side act in a reply that no guard can reach. | confirmed | The candidate's priority does not survive on frequency. It survives on severity: row 111 is the only row in the mode whose damage is permanent (append-only, Rule-16 Store; the row's own cell says it "cannot be repaired by editing"), and a fence at the `dwork state` moment is the only place that link can be demanded while it is still writable. |
| 4 | False refusal on legacy: 140 rows exist with chains written before any such fence, several of which hold a `Y done` with no `Y plan` — row 111's among them. A fence that fails the tree is bypassed on its first run. | survives, scoped | Only as a check over the entries a range **adds**, which is already `disposed_problems`'s own contract ("Entries already present are never re-judged", `dyad/guards/agent/rows.py:23`, implemented at `:88-89`). Scoped that way it never reads row 111's existing chain and never fails a historical tree. |
| 5 | Rule-9 easy agreement: I agreed with this candidate on first reading, because it looks like the plan gate one step later. Pushed: the plan gate resolves a row's state and one literal token at a *base commit* in another ref; this reads the order of two tokens inside one cell of one file. The analogy to the plan gate is wrong, and the check is strictly weaker than it looks. | refuted (the analogy) | The candidate stands only as what it is: a one-token precondition on one CLI verb and one added entry, not a second plan gate. Stating it as "the plan gate for Done" does not survive. |

## Proposed exit (phase 4)
**Exit 2 — a `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes.

The row would say: *a `Y done` entry added to a row whose `disposed` holds no earlier `Y plan` fails,
refused at `dyad dwork state <id> done` before either write and again in `rows.check_transaction` at
every push, judging only the entries a range adds.* It would have caught row 111 (#233) and no other
row of this mode, and it is proposed for severity, not frequency: row 111 is the mode's one
permanently unrepairable chain.

The mode as a whole stays **open** by the play-book's own test, and I am proposing no exit for the
rest of it. Its two live faces are unfenced and the fence above does not reach them: the
merge-before-Done face is quiet since 2026-09-18 under a memory note and a Rule clause that are both
inference; and the agent-side face (row 136, a fork launched on a disposition's text) is an act
inside a reply, which no mechanism in this system observes. Whether that second face is fenceable at
all on this kernel is a question for its own derivation — it looks like Rule-5 Enforcement territory,
a judgement no script can decide — and I do not propose closing it here on that basis.
