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
- The Agent opens a row while executing another, inside the mandate scope its authorized plan
  states (accretion, Scope below).

A `d-work` starts with an Operator prompt and terminates only when the Operator
disposes `Y` to the Agent's counter-prompt of completion (`Y/N: Done with {d-work}?`).
Any other response leaves it incomplete, to be resumed later.

## Scope
- Every Operator prompt opens a d-work. There are no exemptions.
- A new prompt while a d-work is open suspends it and opens another. d-works stack.
- A **bare** disposal response (`Y` or `N` to an Agent counter-prompt) is not a prompt and opens
  nothing. Text accompanying a disposal is a prompt and opens a d-work.
- A third thing opens a row, beside a prompt and a disposition: **accretion**, the Agent's own act
  under an authorized plan. An **accreted row** is one the Agent opens while executing another
  row. Under the preference `accretion: implicit` (`preferences-corpus/PREFERENCES.md`) a row the
  authorized plan already describes, inside the mandate scope that plan states (Plan, below), is
  born `open` carrying that plan-`Y` and takes no disposition of its own (Ledger, below); its Done
  rides the mandate's Done-`Y`, which names it (Completion counter-prompt, below). It opens no
  d-work in the sense of this section's first bullet: no Operator prompt was sent, so nothing is
  suspended and nothing stacks. Under `accretion: explicit` it is asked for like any other row.
  The terms are the countersign model's (`dyad/playbooks/countersign-model.md`), adopted rather
  than coined (Rule-13 property 1) and defined in the vocabulary (Rule-6): a **mandate** is the
  standing countersignature of **implicit mode**; the plan-`Y` that creates one is the **delegate
  edge**; and an accreted row whose work departs from the mandate scope returns to explicit mode by
  the **escalate edge** — the Agent reports it and asks — the implicit **mode lifecycle** of that
  play-book's Part II §4. Which acts are never accretable, whatever a plan says, is Rule-2's list
  (Binding of approval): what a `Y` may bind to is that Rule's concern.
- A subagent's actions are the Agent's actions, bound by the same plan and Rules. Subagents
  read, search and draft. With the preference `delegation: plan-and-execute`
  (`preferences-corpus/PREFERENCES.md`), drafting includes the plan file (Rule-15) and an
  execution branch's changes, so the main Agent stays free for the next prompt; a delegated
  subagent reports the sentinel first, and the main Agent reports every delegated d-work's
  state each turn. Subagents never write a row, ask or answer a counter-prompt, commit to or
  push a branch, open or update a PR, merge, or run a reversible or destructive host action
  (Rule-8); those stay with the main Agent, the party the Operator disposes to. (E7, #107)

## Answer grammar
Three answers to a counter-prompt, not two — the countersign model's **answer grammar**
(`dyad/playbooks/countersign-model.md` Part II §2), adopted rather than coined (Rule-13 property 1):
- `Y` — the disposition asked for is given, bound as Rule-2's Binding of approval binds it.
- `N`, bare — nothing is authorized. The d-work stays as it was and the Agent revises.
- `N` with text — **amend**: the proposal is refused *and* its revision is asked for in the same
  words. The text is a prompt and is entered verbatim as a `prompt` entry of the refused d-work's
  own record (Rule-7, whose trigger is a prompt that opens *or is received on* a d-work); when
  what it asks for is that same proposal revised, it opens no second row — the work it names is
  the row already open — and the plan file is revised in place, the refused revision kept
  (Rule-15). Text that asks for something else is a prompt like any other and opens its own
  d-work (Scope, above). Either way the `N` authorizes nothing until the revision takes its own
  `Y`.
A `Y` with text is a `Y` plus a prompt, which opens its own d-work (Scope). Silence is not
consent: a counter-prompt left unanswered authorizes nothing and is never read as a `Y`. Until
2026-10-14 `amend` had no name here and lived inside "any other response" (Plan, below); the live
instance is this Rule's own amendment, plan #290 refused on 2026-10-14 in the words that became
its revision 5.

## Plan (mutation authorization)
- The Agent's first substantive reply to a prompt is a plan, stored first as a plan file
  (Rule-15): the intent as read, the mutation proposed (falsified first, Rule-9; framed per Rule-10), and the last line `Y/N: proceed with #<id> as planned?` — or the batch form
  (Batch disposition, below) under `batch-disposition-mode`.
- `Y` authorizes the mutation and binds every PR of the d-work to the plan. Work that departs
  from the plan is a new plan and needs a new `Y`. Any other response leaves the d-work
  open with no mutation authorized; the Agent revises the plan.
- No exemptions, with one: the row the plan-`Y` has already authorized. A plan may be one line,
  and a PR may accompany it, but the question is asked — and a row accreted inside the plan's own
  **mandate scope** (next bullet) is not asked for a second time, because the question was asked
  when the plan that describes it was asked.
- **Mandate scope.** A plan that intends to accrete states it: a *rule* for the class of row it
  will open ("one child per failure mode", "a row per surviving fence") and a *ceiling* — at most
  how many such rows. Both are the Operator's to read before the plan-`Y` and to refuse. A plan
  that states no mandate scope accretes nothing, however much it describes; a row the stated rule
  does not cover, or the row after the stated ceiling, is work departing from the plan and so a
  new plan needing a new `Y`. How large a ceiling may be is the Operator's number, never this
  Rule's.
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
    started. Becomes `open` when the Operator prompts for it, or `archived` when an Operator
    disposition retires it (the retirement form, below).
  - `done` — the Operator answered `Y` to the completion counter-prompt *and* every merge that `Y`
    named has landed. Between the two the row keeps the state it had, and its `disposed` carries the
    recorded `Y`; the state guard reads that interval as one warning per row (Mechanisms).
  - `archived` — retired from the working board by an Operator disposition naming the row(s);
    terminal like `done` (a new row refs it, never reopens it), and reached from `done` or from
    `backlog` (Rule-16's table). Nothing moves: its row, plan and provenance stay where they are
    (Rule-16 store; Rule-20 references). The Agent never archives on
    its own judgment; `dyad dwork state <id> archived` is clerical execution of the naming
    disposition, a ledger-only commit. The question that names them is the **retirement form**,
    `Y/N: archive #a, #b, … #k?` — one question over k rows, each listed before it with what it
    holds and why it is proposed for retirement. A `Y` archives exactly the named rows; anything
    else archives none of them (Rule-2, Binding). It is not a plan or Done batch and does not
    enter the pending queue: nothing is planned and nothing is delivered by it.
- The machine whole — which input moves a row along each transition, whose act that input is, and
  which record the move writes — is stated once, as data beside the table (`dyadlib.INPUTS`) and as the
  d-work play-book (`dyad/playbooks/d-work.md`), which also lists every record a d-work is made of; read
  here, never a Rule (#309).
- The Agent may decompose a d-work into child rows (`refs: parent #N`). The parent's
  counter-prompt is asked only when every child is `done`, `blocked`, `backlog`, or carrying its own
  recorded Done-`Y` and waiting on the merge it ratified (Completion counter-prompt, below: a child in
  that interval has been verified and its output is landing, so it no longer owes the parent anything);
  the parent
  completes only on its own Done-`Y`, and the completion evidence names each child's state, so an
  undelivered child is something the Operator sees rather than something the Done-`Y` is read as
  claiming. `backlog` is admitted for the reason `blocked` already was — a child the Operator has
  not asked for is not work the parent owes — and because a `backlog` child could otherwise make
  the parent's question unaskable: one parent of this instance sat on 23 `backlog` children whose
  only transition was back to `open` (#290).
- The Agent appends a row when a d-work starts, records the Operator's `Y` to the completion
  counter-prompt when it is given, and sets `done` only once the merges that `Y` named have landed
  (both clerical execution, Rule-2; Completion counter-prompt, below).
- Ledger-only commits (touching nothing outside `agent-corpus/d-work/`; row and plan files) are clerical and
  go directly to `main` without a PR. `dyad/guards/agent/rows.py` (the main fence) fails any direct
  commit to `main` that touches anything else.
- The `disposed` column records every disposition the row receives, in order, as
  `<date> <Y|N> <plan|done|merge #n|reason>` separated by `;`. The Agent writes each entry
  clerically when the disposition is given, so the chain of authorization is reconstructible
  from the ledger alone (D4). Rows opened before 2026-09-12 #46 are not backfilled. An accreted
  row's first entry is the mandate's own plan-`Y`, written `<date> Y plan (mandate #<id>)` beside
  the `(batch #a,#b,#c)` shape this column already carries (Batch disposition, below); its record's
  entry 1 is that plan-`Y`'s own Operator words, copied verbatim with the note
  `mandate #<id>, <the mandate's own date>` (Rule-7 property 4). A row may also carry the optional
  field `mode`, `explicit` or `implicit`, absent meaning `explicit` (Rule-16 Store).
- At session start the Agent reads the ledger and reports every row that is not `done`,
  the current `merge-disposition` value, and the sentinel (`dyad/CLAUDE.md`). If the
  frame is absent the only permitted action is to say so and stop (E1). The Agent also touches
  its own presence file and reads every other session's (Rule-16); an overlap found there is
  reported when it bears on the prompt at hand, not narrated for its own sake. Under
  `organization: m4` (`preferences-corpus/PREFERENCES.md`) what a session reads and reports is its
  seat's: the leader — the cos — reads the cos-board of programs, a secretary the cos-board of its
  charter's domain, and the seat name says which (Rule-16 Presence); how a board is read, a seat opened or a
  charter written is the organization craft's Operating Guide (`crafts/cabinet/docs/operating-guide.md`),
  read beside the d-work play-book and never a Rule (#369 C7).
- PR bodies — and, on a branch, the commit messages `dyad/guards/agent/prs.py` reads as the body —
  cite `d-work #<id>`; the guard resolves each id against
  the ledger on the base branch and requires it to be `open`, `planned` or `blocked` and to carry a
  `Y plan` disposition (the plan gate, E3). The phrase is a claim of work on that d-work,
  not a mention, in a commit message exactly as in a PR body — cross-reference other rows as plain
  `#<id>` (#23). A ledger-only range claims no d-work — it is clerical (Rule-2) — so the gate skips
  it wherever it travels, on a branch as on `main`; the fence and the provenance guard judge each of
  its commits as they would on `main` (#191).

## Mechanisms
The fence keeps the Done order of the completion clause, on a direct commit to `main`, on each commit
of a ledger-only branch and in a merge commit's resolution against each parent: one commit may not both
record a `Y done` that names a merge and set the row `done` (`rows.done_order_problems`), since the
state follows the merge; the commit that does set `done` must find a `Y done` entry already on the row —
the `Y` it executes — and must show every head the operative entry names as an ancestor of the base
branch or of itself (`rows.landing_problems`), a sha this clone cannot resolve printing one line rather
than failing, because a hard failure on an unresolvable sha is a cross-clone denial of service (#321);
and the interval between the two is read by the state check as one warning per row
(`rows.done_recorded_not_closed`), carried in every evidence block and its sha256. Whether a merge ran
is not decidable from git at the moment of the record — a merge subject naming a PR is no merge of it —
so only the closing commit is fenced, and only against the head its own entry names (#202).

Rule-3 owns the row guard `rows.py` (the main fence) and the PR guard `prs.py` (the plan gate). They
live in `dyad/guards/agent/` (agent zone, Rule-1; placed per Rule-11 property 1) and run on the kernel-only path
as transaction guards (`package.py check --guards`); their workflow wrapper
(`.github/workflows/dyad-d-work.yml`) is infra zone. Changing a guard is an agent-zone PR, changing
the wrapper an infra-zone PR, each citing a Rule-3 d-work. The plan gate is enforced before a push
by the kernel-only path (the PR guard over `origin/main..HEAD` with the commit messages as body);
the wrapper corroborates on `main` only (#168). A state guard beside them checks the trace store on every
push and evidence run: `traces.py`, through `trace.check_store` (#227); the incident log's check stays a
script run by the suite until #170 lets a released craft's pinned entity list change. A range that touches only `<instance>/d-work/` is
exempt from the plan gate (`prs.ledger_only`, #191): every one of its own non-merge commits touches
only that path, read commit by commit with rename detection off, so a branch that ever touched
anything else — a move into the ledger, a reverted edit, code squashed into `main` since — is not
ledger-only. Before the exemption, a session fenced off a direct push to `main` (Rule-1, #23) moved
uncited ledger commits around the hook, which skipped every guard. The exemption rests on `main`
admitting the same commits, so the fence judges each commit of a ledger-only branch as it would on
`main`, and each of its merge commits against both parents — a PR merge lands them where the fence's
first-parent walk never looks. Rule-2 references `rows.py` by name; it does not own it.

## Completion counter-prompt (intent verification)
- Done-`Y` is the Operator's verification that the original intent of the d-work was
  delivered in alignment with the Operator's expectation of the output. It is asked on the
  output as it stands in the PR(s), before merge, so `main` never carries unverified output.
- Always the last line of the Agent's reply that believes the d-work is done.
- The reply that asks does not merge. The reply that receives the Done-`Y` records it, merges, and
  only then closes the row — three acts in that order, so the ledger's own record of the `Y` precedes
  every merge it ratifies and the row stays pushable until the merges have run. (1) **Record.** The
  disposition is written with the state left as it is: the `disposed` entry and its provenance entry
  in one clerical ledger commit, the commit that carries the trace, the entry naming each PR and the
  head its `Y` was given on — `-d 'Y done (merges PR #a at <head-a>)'`. That entry *is* the ledger's
  record of the `Y`; the state never was. (2) **Merge**, as clerical execution of it. (3) **Close.**
  A second, dispositionless ledger commit sets `done`, once git shows the head the **operative**
  entry names — the last `Y done`, since a resolution that changes a head voids the `Y` given against it
  (Rule-2, Binding) and the question is asked again — on `main` — the hosting's merge, or the local merge of Rule-14 property 3; where a hosting squashes or
  rebases, the entry records `landed <sha>` instead. A Done-`Y` that names no merge is recorded `done`
  at once, so nothing costs a second commit where nothing is in flight. A merge before the `Y` is
  self-ratification (Rule-2) and an incident whatever the outcome (#47, #58, #67); `done` written
  while the head the operative entry names is not yet on `main` is the converse breach, and the fence
  refuses the commit that writes it (Mechanisms). What the fence can decide is that head's reachability,
  not that PR #n merged: no resolver maps a PR number to a commit on the kernel-only path, and a merge
  subject naming a PR is no merge of it. The state is what the merge moves, because `done` is terminal
  (Rule-16) and the plan gate refuses every commit citing a terminal row: while a ratified merge
  still owes a push — a rebase onto a moved `main`, a conflict resolved, the second PR of a sequenced
  set — the row is still `open` or `planned`, and its own plan-`Y` carries that push (not `blocked`:
  Rule-16's table has no edge from it to `done`, and a row deferred on another d-work has no `Y` to
  execute). What
  the interval does not do is re-bind the `Y`: a resolution that changes a head voids it (Rule-2,
  Binding), the question is asked again, and its answer is a further entry on the same live row.
- The completion reply carries the evidence the verification needs (E8): every PR of the
  d-work by number and zone; each check's result as observed, never assumed, or "CI absent"
  with the local guard results (Rule-2, Binding); every host
  action taken, with its class and its change-log row (a missing row is stated as a Rule-8
  breach); every row accreted under this d-work's mandate — its id, its `mode`, what it holds
  and what it cost in dispositions — and every escalation that returned one to explicit mode;
  anything in the plan not delivered; any departure from the plan; and anything the
  Agent could not verify, stated before the counter-prompt. An omission is a breach of this
  Rule, not a style choice.
- When the preference `dwork-trace` (`preferences-corpus/PREFERENCES.md`) is `always`, the completion
  evidence cites the d-work trace of the d-work it completes (play-book `dyad/playbooks/dwork-trace.md`);
  under `on-demand`, only when the Operator has prompted for one. The completion reply prints its
  preview, from the prompt to the Done question; the reply that receives the Done-`Y` writes it to
  `<instance>/d-work/traces/<id>.md` before the Done **record** commit — the first of the two above —
  which carries it, so it covers the Done-`Y` and stays ledger-only; the merges after it, and the
  commit that closes the row, are not in it. A trace with no transcript is still
  cited, its buckets marked absent (#213).
- Form: `Y/N: Done with #<ledger id> <title>?` — one d-work per counter-prompt, or the batch
  form (Batch disposition, below) under `batch-disposition-mode`. A d-work that accreted rows
  names them in the question: `Y/N: Done with #<id> <title> (accreted #c, #d)?`. The `Y` verifies
  and closes that set as the completion evidence listed it (Rule-2, Binding), so the Operator
  verifies the set it got and not the set the plan promised; a row left out of the list is left
  out of the `Y`, and leaving one out is a breach of this Rule as every other omission is.
- When `merge-disposition` is `with-done` (`preferences-corpus/PREFERENCES.md`), the form
  names the d-work's unmerged PR(s): `Y/N: Done with #<id> <title> (merges PR #a, #b)?`.
  The `Y` ratifies those merges too (Rule-2, binding of approval). With an accreted set the one
  clause carries both, the rows before the PRs:
  `Y/N: Done with #<id> <title> (accreted #c, #d, merges PR #a, #b)?`.

## Batch disposition
Preference `batch-disposition-mode` (`preferences-corpus/PREFERENCES.md`). `off` — every plan
and completion counter-prompt above is asked and disposed singly. `on-ignore` — singly, until
the Operator leaves one outstanding (Conditions, above: the next message is a prompt, not its
bare disposal) — the engagement signal itself, nothing else needed. `always` — never singly:
the first pending item already opens the queue. Release counter-prompts have their own, narrower
batch form, owned by Rule-11 (several tags whose content one d-work's own Done-`Y` already
verified); it is never a plan or Done batch and never enters this section's pending queue. Nor is
a mandate a batch, and it likewise never enters the queue: the rows a plan-`Y` accretes are not
asked about at all, so they are neither plan-ready nor done-ready items (the mandate form, below).

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

Beside the batch forms, and never one of them, is the **mandate form** — the pair of questions by
which one d-work's own plan-`Y` and Done-`Y` cover every row it accreted (Scope, Plan, Completion
counter-prompt): `Y/N: proceed with #<id> as planned?` over a plan that states a mandate scope,
which authorizes the class of row that scope names as well as the mutation (Rule-2, Binding), and
`Y/N: Done with #<id> <title> (accreted #c, #d)?`, which verifies the delivered set. Two questions
whatever the set's size, because a mandate compresses *acts* where a batch compresses *questions*.
That is why nothing about it is pending, and why the two may hold one question without
interfering: a done batch naming several d-works names each one's accreted set in its own clause.

The queue drains as its items are named in a batch question and disposed. Under `on-ignore`,
engagement lapses back to singly-asking once both queues are empty; under `always` it never
lapses. Each disposed row's ledger entry names the full set it was batched with —
`<date> Y plan (batch #a,#b,#c)` / `<date> Y done (batch #a,#b, merges PR #w at <head-w>, PR #x at
<head-x>)`, every PR with the head its `Y` was given on, as the completion clause requires of any Done
entry that ratifies a merge — so the
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
- Periodically the incident log is worked whole rather than row by row: an exercise groups an
  incident ledger into failure modes and closes each one by a fence at a named moment, by a
  `backlog` row naming the fence still to build, or by a recorded impossibility on this kernel
  naming the Rule that makes it so — that exercise is the incident-hardening play-book
  (`dyad/playbooks/incident-hardening.md`), which takes the incident ledger it hardens as its
  parameter and, on one that has not grown since the last exercise, does nothing beyond
  re-testing the fences already closed.

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
reply; see the same record, amendment #113. Incidents gains the periodic-exercise bullet
2026-09-23 (d-work #137): the grouping-and-mitigation exercise run by hand in #116, #128 and #135
becomes a play-book Rule-3 reads, parameterized by the ledger it hardens and idempotent on one
that has not grown; see the same record, amendment #137. Ledger and Mechanisms gain the plan
gate's ledger-only exemption 2026-09-29 (d-work #191): the gate refused a clerical range, which
pushed ledger commits around the hook and past every other guard; see the same record, amendment
#191. Completion counter-prompt gains the d-work trace bullet 2026-10-05 (d-work #213): the
per-d-work performance measurement done by hand three times (#204, #212) becomes a play-book whose
trace the completion evidence cites, previewed in the completion reply and stored by the Done ledger
commit (plan revision 2), as the preference `dwork-trace` reads (revision 3, #215); see the same
record, amendment #213. Mechanisms gains the trace guard 2026-10-06 (d-work #227): the store's check
ran only inside Rule-12's suite, which a guard-only push skips (#217); see the same record, amendment #227.
Scope, Plan, Ledger, Completion counter-prompt and Batch disposition gain accretion under a mandate,
and Answer grammar is added, 2026-10-14 (d-work #290): 117 of this instance's 280 rows had been
accreted, and the ones actually worked cost the Operator *more* than prompt-born rows — mean 2.65
disposed entries against 2.15, with not one closing on a single disposition except #162–#165, the
four handled as a mandate under #199; meanwhile `archived` had been used 0 times in 280 rows, 75
rows sat in `backlog` at a median age of 21 days, and the transition table gave `backlog` one
successor, so the one parent ever gated on `backlog` children could not be asked its Done question
at all. The vocabulary is the countersign model's (then the Tended craft countersign, since #381
`dyad/playbooks/countersign-model.md`) — mandate, implicit mode, escalate edge, amend — adopted rather
than coined (Rule-13 property 1), and `amend` is the first of the four refactors that model's Part II
§7 lists as owed by this system. See the same record, amendment #290. Completion counter-prompt, Ledger and Mechanisms gain the three-act Done order 2026-10-15 (d-work
#202): recording the Done-`Y` set the row `done`, `done` is terminal, and the plan gate refuses every
commit citing a terminal row, so a ratified merge that still needed one push — a rebase onto a moved
`main`, a conflict resolved, the second PR of a sequenced set — had no admissible sequence at all.
Twelve rows of `agent-corpus/audits/INCIDENTS.md` between 2026-09-30 and 2026-10-15 are that one
mechanism — eleven distinct instances, two of them recorded as one event's two rows, four recovery rows were paid for it, and 164 rows' `disposed` claims a merge that nothing
reads — five of those claims are known false. The record of the `Y` is now the `disposed` entry and
its provenance entry, which still precede the merge; the state follows it. See the same record,
amendment #202. Ledger gains the d-work play-book 2026-10-15 (d-work #309): the lifecycle was spread over
five Rules, two play-books and the CLI help, and the transition table named no inputs — a successor relation,
not a machine; the input alphabet is now `dyadlib.INPUTS` with its invariants, and the play-book's tables are
pinned to it and to the guards; see the same record, amendment #309. Scope and Answer grammar cite the countersign
model by its core path, and Scope names the delegate edge and the mode lifecycle beside the escalate edge it already
named, 2026-10-22 (d-work #381, child C3 of #369): the countersign craft is retired and its model carried by the core
as a play-book; see the same record, amendment #381. Ledger's session-start bullet gains
the organization sentence 2026-10-22 (d-work #379, #369 C7): under `m4` a session reads a board, not the
whole ledger, and the Guide that says how is the organization craft's; see the same record, amendment #379. Ledger's
session-start bullet names the cos and a secretary, and the Guide's path the cabinet craft, 2026-10-25 (d-work #419,
child C2 of #417): the organization craft is renamed `cabinet` and its role terms cos and secretary; see the same
record, amendment #419.

Set: System Requirements.
