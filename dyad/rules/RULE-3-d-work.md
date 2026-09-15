# Rule-3: d-work

**Intent:** Run every unit of operator-prompted work as a d-work that opens on the prompt, is authorized by a plan-`Y`, and closes only on the operator's Done-`Y`.
**Target:** a d-work

## Boundaries (out of scope)
- Who may ratify — Rule-2 (applied by reference to the events declared here).
- Which zone a change belongs to — Rule-1.
- Bare `Y`/`N` disposals: they answer a counter-prompt and open nothing.
- What the Agent may do on the live host — Rule-8 (a plan names host actions; Rule-8 classes them).

## Conditions (triggers)
- The operator sends a prompt (text, including text accompanying a disposal).
- The agent is about to mutate the repo for a d-work (plan gate).
- The agent believes a d-work is done (completion counter-prompt).
- A session starts (ledger report).
- A PR is opened or edited (`prs.py`); a commit is pushed to `main` (`rows.py`, the main fence).

A `d-work` starts with an Operator prompt and terminates only when the Operator
disposes `Y` to the Agent's counter-prompt of completion (`Y/N: Done with {d-work}?`).
Any other response leaves it incomplete, to be resumed later.

## Scope
- Every Operator prompt opens a d-work. There are no exemptions.
- A new prompt while a d-work is open suspends it and opens another. d-works stack.
- A **bare** disposal response (`Y` or `N` to an Agent counter-prompt) is not a prompt and opens
  nothing. Text accompanying a disposal is a prompt and opens a d-work.
- A subagent's actions are the Agent's actions, bound by the same plan and Rules. Subagents
  read, search and draft. With the preference `delegation: plan-and-execute`
  (`preferences-corpus/PREFERENCES.md`), drafting includes the plan file (Rule-15) and an
  execution branch's changes, so the main Agent stays free for the next prompt; a delegated
  subagent reports the sentinel first, and the main Agent reports every delegated d-work's
  state each turn. Subagents never write a row, ask or answer a counter-prompt, commit to or
  push a branch, open or update a PR, merge, or run a reversible or destructive host action
  (Rule-8); those stay with the main Agent, the party the Operator disposes to. (E7, #107)

## Plan (mutation authorization)
- The Agent's first substantive reply to a prompt is a plan, stored first as a plan file
  (Rule-15): the intent as read, the mutation proposed (falsified first, Rule-9; framed per Rule-10), and the last line `Y/N: proceed with #<id> as planned?`.
- `Y` authorizes the mutation and binds every PR of the d-work to the plan. Work that departs
  from the plan is a new plan and needs a new `Y`. Any other response leaves the d-work
  open with no mutation authorized; the Agent revises the plan.
- No exemptions: a plan may be one line, and a PR may accompany it, but the question is asked.
- A prompt that opens a new body of work is planned by the craft play-book
  (`dyad/playbooks/craft-instantiation.md`): the plan assumes a new craft instance unless one of
  the play-book's `craft-instantiation-criteria` fires, in which case it advises a new dyad system
  naming the criterion; the play-book's steps are its run-book (`dyad/runbooks/craft.md`), whose
  events the completion reply cites (#165).
- The plan-`Y` is disposition (2) of the operator's model (audit 2026-09-12, disposition
  chain); the Done-`Y` below is disposition (1).

## Ledger
- The ledger is the row-file store `agent-corpus/d-work/rows/` (Rule-16), rendered to
  `agent-corpus/d-work/LEDGER.md` on demand. One row per
  d-work; `state` is `open`, `planned`, `done`, `blocked`, or `backlog` — defined in the vocabulary
  (Rule-6; transitions: Rule-16); the consequences of each state are:
  - `open` — started; the Agent is working it or it is suspended by a newer prompt.
  - `planned` — the plan file is authorized (plan-`Y`); execution may start in any session (Rule-15).
  - `blocked` — the Operator disposed a deferral naming another d-work; `refs` names it.
    Returns to `open` when the blocking d-work is `done`.
  - `backlog` — opened by an Operator disposition rather than worked immediately; not
    started. Becomes `open` when the Operator prompts for it.
  - `done` — the Operator answered `Y` to the completion counter-prompt.
- The Agent may decompose a d-work into child rows (`refs: parent #N`). The parent's
  counter-prompt is asked only when every child is `done` or `blocked`; the parent
  completes only on its own Done-`Y`.
- The Agent appends a row when a d-work starts and sets `done` only after the Operator's
  `Y` to the completion counter-prompt (clerical execution, Rule-2).
- Ledger-only commits (touching nothing outside `agent-corpus/d-work/`; row and plan files) are clerical and
  go directly to `main` without a PR. `dyad/guards/agent/rows.py` (the main fence) fails any direct
  commit to `main` that touches anything else.
- The `disposed` column records every disposition the row receives, in order, as
  `<date> <Y|N> <plan|done|merge #n|reason>` separated by `;`. The Agent writes each entry
  clerically when the disposition is given, so the chain of authorization is reconstructible
  from the ledger alone (D4). Rows opened before 2026-09-12 #46 are not backfilled.
- At session start the Agent reads the ledger and reports every row that is not `done`,
  the current `merge-disposition` value, and the sentinel (`dyad/CLAUDE.md`). If the
  frame is absent the only permitted action is to say so and stop (E1). The Agent also touches
  its own presence file and reads every other session's (Rule-16); an overlap found there is
  reported when it bears on the prompt at hand, not narrated for its own sake.
- PR bodies cite `d-work #<id>`; `dyad/guards/agent/prs.py` resolves each id against
  the ledger on the base branch and requires it to be `open`, `planned` or `blocked` and to carry a
  `Y plan` disposition (the plan gate, E3). The phrase is a claim of work on that d-work,
  not a mention — cross-reference other rows as plain `#<id>`.

## Mechanisms
Rule-3 owns the row guard `rows.py` (the main fence) and the PR guard `prs.py` (the plan gate). They
live in `dyad/guards/agent/` (agent zone, Rule-1; placed per Rule-11 property 1) and run on the kernel-only path
as transaction guards (`package.py check --guards`); their workflow wrapper
(`.github/workflows/dyad-d-work.yml`) is infra zone. Changing a guard is an agent-zone PR, changing
the wrapper an infra-zone PR, each citing a Rule-3 d-work. The plan gate is enforced before a push
by the kernel-only path (the PR guard over `origin/main..HEAD` with the commit messages as body);
the wrapper corroborates on `main` only (#168). Rule-2 references `rows.py` by name; it
does not own it.

## Completion counter-prompt (intent verification)
- Done-`Y` is the Operator's verification that the original intent of the d-work was
  delivered in alignment with the Operator's expectation of the output. It is asked on the
  output as it stands in the PR(s), before merge, so `main` never carries unverified output.
- Always the last line of the Agent's reply that believes the d-work is done.
- The completion reply carries the evidence the verification needs (E8): every PR of the
  d-work by number and zone; each check's result as observed, never assumed, or "CI absent"
  with the local guard results (Rule-2, Binding); every host
  action taken, with its class and its change-log row (a missing row is stated as a Rule-8
  breach); anything in the plan not delivered; any departure from the plan; and anything the
  Agent could not verify, stated before the counter-prompt. An omission is a breach of this
  Rule, not a style choice.
- Form: `Y/N: Done with #<ledger id> <title>?` — one d-work per counter-prompt.
- When `merge-disposition` is `with-done` (`preferences-corpus/PREFERENCES.md`), the form
  names the d-work's unmerged PR(s): `Y/N: Done with #<id> <title> (merges PR #a, #b)?`.
  The `Y` ratifies those merges too (Rule-2, binding of approval).

## Incidents
- An incident is any action taken or outcome reached that the plan did not name, or a plan
  item not achieved as the plan said: an error, a recovery, a failed check, an unplanned edit.
- Reported in the reply where it occurred or in the completion reply, whichever comes first.
- Recorded: as an attack in the relevant falsification record if it falsifies a Rule or a
  mechanism; otherwise as a row in `agent-corpus/audits/INCIDENTS.md` (date, d-work, what,
  cause, consequence). Written in the d-work's own PR, or the next agent-zone PR for an
  incident during clerical work.
- If the plan changes as a result, a fresh plan-`Y` precedes any further mutation. (E9)

## Ratification events
- Answering `Y` to a plan counter-prompt (mutation authorization).
- Answering `Y` to a d-work completion counter-prompt (intent verification; under
  `merge-disposition: with-done` it also ratifies the named merges). Rule-2 applies by reference.

## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-3-d-work.md`.

Set: System Requirements.
