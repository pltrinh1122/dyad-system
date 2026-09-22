# Rule-3: d-work

**Intent:** Run every unit of operator-prompted work as a d-work that opens on the prompt, is authorized by a plan-`Y`, and closes only on the operator's Done-`Y`.
**Target:** a d-work

## Boundaries (out of scope)
- Who may ratify — Rule-2 (applied by reference to the events declared here).
- Which zone a change belongs to — Rule-1.
- Bare `Y`/`N` disposals: they answer a counter-prompt and open nothing.
- What the Agent may do on the live host — Rule-8 (a plan names host actions; Rule-8 classes them).
- Destructive-action counter-prompts: always one-per-question, never batched — Rule-8. Release
  counter-prompts: one-per-question by default; a release-specific batch naming several tags of
  one already-`done` d-work's own surfaced output is Rule-11's own form, never Rule-3's plan or
  Done batch.
- How another agent frames a proposal to its own Operator — that system's Rule-10; Rule-3 judges
  only what its message carries when it arrives here (Intake, below).

## Conditions (triggers)
- The operator sends a prompt (text, including text accompanying a disposal).
- The agent is about to mutate the repo for a d-work (plan gate).
- The agent believes a d-work is done (completion counter-prompt).
- A session starts (ledger report).
- A PR is opened or edited (`prs.py`); a commit is pushed to `main` (`rows.py`, the main fence).
- The Operator's reply to a counter-prompt is a new prompt rather than its bare disposal: under
  `batch-disposition-mode: on-ignore` (`preferences-corpus/PREFERENCES.md`), the engagement
  signal for a batch (Batch disposition, below).
- A message from another agent — a peer session, an installed system's Agent — proposes work
  (Intake, below).

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
  (Rule-15): the intent as read, the mutation proposed (falsified first, Rule-9; framed per Rule-10), and the last line `Y/N: proceed with #<id> as planned?` — or the batch form
  (Batch disposition, below) under `batch-disposition-mode`.
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
  d-work; `state` is `open`, `planned`, `done`, `blocked`, `backlog` or `archived` — defined in the vocabulary
  (Rule-6; transitions: Rule-16); the consequences of each state are:
  - `open` — started; the Agent is working it or it is suspended by a newer prompt.
  - `planned` — the plan file is authorized (plan-`Y`); execution may start in any session (Rule-15).
  - `blocked` — the Operator disposed a deferral naming another d-work; `refs` names it.
    Returns to `open` when the blocking d-work is `done`.
  - `backlog` — opened by an Operator disposition rather than worked immediately; not
    started. Becomes `open` when the Operator prompts for it.
  - `done` — the Operator answered `Y` to the completion counter-prompt.
  - `archived` — retired from the working board by an Operator disposition naming the row(s);
    terminal like `done` (a new row refs it, never reopens it). Nothing moves: its row, plan and
    provenance stay where they are (Rule-16 store; Rule-20 references). The Agent never archives on
    its own judgment; `dyad dwork state <id> archived` is clerical execution of the naming
    disposition, a ledger-only commit.
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
- PR bodies — and, on a branch, the commit messages `dyad/guards/agent/prs.py` reads as the body —
  cite `d-work #<id>`; the guard resolves each id against
  the ledger on the base branch and requires it to be `open`, `planned` or `blocked` and to carry a
  `Y plan` disposition (the plan gate, E3). The phrase is a claim of work on that d-work,
  not a mention, in a commit message exactly as in a PR body — cross-reference other rows as plain
  `#<id>` (#23).

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
- The reply that asks does not merge. The reply that receives the Done-`Y` merges, as clerical
  execution, after recording the disposition (`dyad dwork state <id> done`) — so the ledger's own
  record of the `Y` precedes every merge it ratifies. A merge before the `Y` is self-ratification
  (Rule-2) and an incident whatever the outcome (#47, #58, #67).
- The completion reply carries the evidence the verification needs (E8): every PR of the
  d-work by number and zone; each check's result as observed, never assumed, or "CI absent"
  with the local guard results (Rule-2, Binding); every host
  action taken, with its class and its change-log row (a missing row is stated as a Rule-8
  breach); anything in the plan not delivered; any departure from the plan; and anything the
  Agent could not verify, stated before the counter-prompt. An omission is a breach of this
  Rule, not a style choice.
- Form: `Y/N: Done with #<ledger id> <title>?` — one d-work per counter-prompt, or the batch
  form (Batch disposition, below) under `batch-disposition-mode`.
- When `merge-disposition` is `with-done` (`preferences-corpus/PREFERENCES.md`), the form
  names the d-work's unmerged PR(s): `Y/N: Done with #<id> <title> (merges PR #a, #b)?`.
  The `Y` ratifies those merges too (Rule-2, binding of approval).

## Batch disposition
Preference `batch-disposition-mode` (`preferences-corpus/PREFERENCES.md`). `off` — every plan
and completion counter-prompt above is asked and disposed singly. `on-ignore` — singly, until
the Operator leaves one outstanding (Conditions, above: the next message is a prompt, not its
bare disposal) — the engagement signal itself, nothing else needed. `always` — never singly:
the first pending item already opens the queue. Release counter-prompts have their own, narrower
batch form, owned by Rule-11 (several tags whose content one d-work's own Done-`Y` already
verified); it is never a plan or Done batch and never enters this section's pending queue.

Once engaged, the Agent holds a **pending queue**: every plan-ready d-work (its plan file
written, Rule-15, counter-prompt not yet asked as part of a batch) and, separately, every
done-ready d-work (its completion evidence gathered, Done question not yet asked as part of a
batch). Both counts are reported at the end of every reply while either is non-empty, so an
unintended engagement is visible within one turn. The queue is conversational, derived from the
ledger and the stored plan files — not a corpus file, nothing here is mechanically checked.

The batch forms replace the single forms above, one kind at a time — a plan batch and a done
batch are never the same question:
- `Y/N: proceed with #a, #b, #c as planned?` — authorizes the mutation of every named d-work;
  each already has its own stored plan file. A `Y` authorizes exactly the named set (Rule-2,
  Binding); `N`, or any other response, authorizes none of them (as the single form).
- `Y/N: Done with #a <title-a>, #b <title-b> (merges PR #w, #x, #y)?` — the reply carries full
  completion evidence for every named d-work before this line; `merges` lists the union of
  their unmerged PRs (`merge-disposition: with-done`). A `Y` verifies and ratifies the named set
  together; a d-work not yet done-ready waits for a later batch.

The queue drains as its items are named in a batch question and disposed. Under `on-ignore`,
engagement lapses back to singly-asking once both queues are empty; under `always` it never
lapses. Each disposed row's ledger entry names the full set it was batched with —
`<date> Y plan (batch #a,#b,#c)` / `<date> Y done (batch #a,#b, merges PR #w,#x,#y)` — so the
chain is reconstructible from any one row alone (D4, Ledger above). Provenance (Rule-7) is
unaffected: the Operator's one `Y` is written as the same entry into every named d-work's own
record.

## Intake (work proposed by another agent)
A message from another agent opens no d-work: only an Operator prompt or disposition does (Scope).
What a message may carry is an intake — a candidate row — which the Agent surfaces to the Operator
with exactly what it carries; the Operator's `Y` opens the row (`backlog` or `open`), its `refs`
naming the origin as `<system>-<id>`. Two shapes are admissible:
- A **defect** is admissible as an observation with evidence: what was observed, where (path,
  commit, run id), how it reproduces, the mechanism the sender verified — never a verdict, never a
  required fix (a fix's shape may be suggested). The evidence goes into the row's plan file; its
  provenance record's first entry is the Operator's own `Y`, since the observation is the sender's
  words, not the Operator's (Rule-7 property 4).
- An **enhancement** is admissible only with its Operator behind it: the verbatim Operator prompt
  that asked for it, or provenance to one — a row id in the sender's ledger whose provenance record
  holds that prompt, quoted in the message. The relayed prompt is the row's first provenance entry,
  noted `relayed via <session>` (Rule-7 property 4). An agent's own idea, however well argued, is
  not an intake: it is a proposal for the sender's own Operator, and if that Operator prompts for
  it, the prompt travels with the message.
Anything else is returned to the sender with the missing shape named, and reported to the Operator
as received, not as work. The Operator may still open a row for it by prompting — the rule bounds
what an agent may bring, never what the Operator may ask for.

## Incidents
- An incident is any action taken or outcome reached that the plan did not name, or a plan
  item not achieved as the plan said: an error, a recovery, a failed check, an unplanned edit.
- Reported in the reply where it occurred or in the completion reply, whichever comes first.
- Recorded: as an attack in the relevant falsification record if it falsifies a Rule or a
  mechanism; otherwise as a row in `agent-corpus/audits/INCIDENTS.md` (date, d-work, what,
  cause, consequence). Written in the d-work's own PR, or the next agent-zone PR for an
  incident during clerical work.
- If the plan changes as a result, a fresh plan-`Y` precedes any further mutation. (E9)
- Under `concise-mode: on` (`preferences-corpus/PREFERENCES.md`) the reply where it occurred and
  the completion reply are the same reply; the incident's record — the attack row or the
  `INCIDENTS.md` row, and the plan file's own falsification section — is written during the turn,
  before that single reply reports it, so an interrupted turn loses narration, never the record.

## Ratification events
- Answering `Y` to a plan counter-prompt (mutation authorization).
- Answering `Y` to a d-work completion counter-prompt (intent verification; under
  `merge-disposition: with-done` it also ratifies the named merges). Rule-2 applies by reference.

## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-3-d-work.md`. Batch
disposition added 2026-09-15 (d-work #17): a queued batch counter-prompt over several d-works, engaged
by an ignored counter-prompt or the `always` preference; see
`../falsification/rules/rules-2-3-batch-disposition.md`. Intake added 2026-09-16 (d-work #34):
three intakes from peer sessions in two days — one carrying its Operator's plan-`Y`, one a defect
with evidence, one an agent's own proposal — showed Scope had no clause for a message that is not
an Operator prompt; see `../falsification/rules/rule-3-d-work.md`, amendment #34. `archived` state added 2026-09-16 (d-work #37): a terminal step after `done`, by Operator disposition; see the same record, amendment #37. Completion clause gains the merge-sequence bullet 2026-09-18 (d-work #68): three merges run before their Done-`Y` in one session; see the same record, amendment #68. Boundaries and Batch disposition reworded 2026-09-21 (d-work #106): release's one-per-question rule rests on Rule-11's own "publishes to the world" reason, not Rule-8 destructiveness, and gains its own narrower batch form (Rule-11); destructive stays unconditional; see the same record, amendment #106. Incidents gains the
`concise-mode` bullet 2026-09-22 (d-work #113): under one reply per prompt the record precedes the
reply; see the same record, amendment #113.

Set: System Requirements.
