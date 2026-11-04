# Rule-3: d-work

**Intent:** Run every body of operator-prompted work as a d-work that opens on a prompt, is authorized by one plan-`Y` and closes on one done-`Y`, each `Y` binding every act its question names and nothing it does not.
**Target:** a d-work

## Boundaries (out of scope)
- Who may ratify, and which acts a `Y` may never carry — Rule-2 (Binding of approval), applied by reference to the
  events declared here.
- Which zone a change belongs to — Rule-1. The plan file and the two phases — Rule-15. The row store, its transition
  table, the board store, the inbox and presence — Rule-16. The words of every prompt and disposition — Rule-7.
- What the agent may do on the live host — Rule-8, which classes every host action a plan names and keeps a
  destructive action's own question, never batched and never carried.
- A release's question, its batch form and the release gate — Rule-11; never a plan or Done batch here.
- How another agent frames a proposal to its own operator — that system's Rule-10; this Rule judges only what its
  message carries when it arrives (Intake, below).
- The machine step by step — which input moves a row, whose act it is, which record it writes, which layer executes
  it — the d-work play-book (`dyad/playbooks/d-work.md`), its input alphabet `dyadlib.INPUTS`: read here, never a
  Rule (#309).

## Conditions (triggers)
- The operator sends a prompt, or answers a counter-prompt.
- The agent is about to mutate the repo for a d-work (the plan gate), or believes a d-work is done (the Done question).
- The agent opens a row while executing another, under the plan-`Y` that carries it (Scope, below).
- A message from another agent proposes work (Intake, below).
- A session starts (the ledger report).
- A PR is opened or edited (`prs.py`); a commit is pushed to `main` (`rows.py`, the main fence).
- Under `batch-disposition-mode: on-ignore` (`preferences-corpus/PREFERENCES.md`) the operator's reply to a
  counter-prompt is a new prompt rather than its bare disposal: the engagement signal for a batch (Batch
  disposition, below).

## Scope (what opens a row)
Three things open a row, and never the agent's own finding:
- **A prompt.** Every operator prompt opens a d-work, which terminates only on the operator's `Y` to its Done
  question; any other answer leaves it incomplete, to be resumed. A new prompt while a d-work is open suspends it and
  opens another: d-works stack. One exemption: a prompt whose answer only reads the corpus, writes nothing and asks
  no question opens none. The test is the reply's form, never the agent's inference: a reply that writes, proposes or
  carries a `Y/N` line is no read-only answer, and it opens its d-work before its question (#492).
- **A disposition that opens one**: the `Y` that admits an intake (Intake, below) or opens a row as `backlog`. A
  **bare** answer (`Y` or `N` to a counter-prompt) is not a prompt and opens nothing; text accompanying an answer is a
  prompt.
- **Accretion**: an **accreted row** is one the agent opens while executing another, under that row's plan-`Y`.
  Under the preference `accretion: implicit` a plan-`Y` carries the rows its plan describes inside the mandate scope
  it states and the rows a play-book it runs prescribes (Plan, below); such a row takes no disposition of its own and
  opens no d-work in the first bullet's sense, so nothing is suspended and nothing stacks. Under `accretion: explicit`
  it is asked for like any other row.

The terms are the countersign model's (`dyad/playbooks/countersign-model.md`), adopted rather than coined (Rule-13
property 1) and defined in the vocabulary (Rule-6): a **mandate** is the standing countersignature of **implicit
mode**; the plan-`Y` that creates one is the **delegate edge**; an accreted row whose work departs from the mandate
scope returns to explicit mode by the **escalate edge** — the agent reports it and asks — the implicit **mode
lifecycle** of that play-book's Part II §4.

A subagent's actions are the agent's, bound by the same plan and Rules. Subagents read, search and draft — under
`delegation: plan-and-execute`, the plan file and an execution branch's changes too — and a delegated subagent reports
the sentinel first. Subagents never write a row, ask or answer a counter-prompt, commit, push, open or update a PR,
merge, or run a reversible or destructive host action (Rule-8): those stay with the main agent, the party the
operator disposes to, which reports every delegated d-work's state each turn (E7, #107).

## Answer grammar
Three answers to a counter-prompt, the countersign model's **answer grammar** (`dyad/playbooks/countersign-model.md`
Part II §2):
- `Y` — the disposition asked for is given, binding every act the question names (What a `Y` binds, below).
- `N`, bare — nothing is authorized; the agent revises.
- `N` with text — **amend**: the proposal refused and its revision asked for in the same words, entered verbatim as a
  `prompt` entry of the refused d-work's record (Rule-7). When it asks for the same proposal revised it opens no
  second row, and the plan file is revised in place, the refused revision kept (Rule-15); text that asks for
  something else opens its own d-work. Either way the `N` authorizes nothing until the revision takes its own `Y`.

A `Y` with text is a `Y` plus a prompt. Silence is not consent: an unanswered counter-prompt authorizes nothing. An
answer is read by its meaning, never its case or spelling — `Y`, `y` and `yes` are one `Y`, `N`, `n` and `no` one
`N` — the row recording the token and the provenance record the words as typed (Rule-7); where two readings would lead to
different acts the agent asks, as a blocking question (Rule-8's form), never about spelling alone (`dyad/dmc/label-case.jsonld`, #553).

## What a `Y` binds
A `Y` binds every act its question names and nothing else (Rule-2, Binding of approval), and a question names what it
cites. A row of work takes two questions:
- the **plan question** cites the plan file, so its plan-`Y` binds the mutation the plan describes, every PR of the
  d-work, and every row the plan carries (Plan, below);
- the **Done question** names the d-work, its accreted rows, the rows its report retires and its unmerged PRs, so its
  done-`Y` verifies the output, closes the accreted set, archives exactly the retired rows and ratifies exactly those
  merges (Completion counter-prompt, below).

A batch counter-prompt binds each d-work it names as its single question would (Batch disposition, below). A carried
act was named in a question the operator answered, or it is not carried: anything the plan does not describe, or its
scope or play-book step does not cover, is a new plan needing a new `Y`. **Never carried**, whatever a plan or
play-book says, is Rule-2's list — a destructive host action, a release outside the release gate, an intake, a
preference value, a mutation the plan did not describe — each asked under the Rule that owns it.

## Plan (mutation authorization)
- The agent's first substantive reply to a prompt is a plan, stored first as a plan file (Rule-15): its definition of
  done, the intent as read, the mutation proposed (falsified first, Rule-9; framed per Rule-10), and the last line
  `Y/N: proceed with #<id> as planned?`, or the batch form. The definition of done is the operator's words, quoted
  from the provenance record, or one marked *proposed* that the plan-`Y` accepts and an amend corrects: one row per
  definition of done the operator can evaluate, over the largest scope it lets the operator judge (#574).
- The plan-`Y` authorizes the mutation and binds every PR of the d-work to the plan. Work that departs from it is a
  **new plan** needing a new `Y`; any other answer leaves the d-work open with nothing authorized. No exemptions: a
  plan may be one line, but the question is asked — and a row the plan-`Y` carries is never asked a second time.
- An **execution detail** is not a departure: a change of step order, of how PRs are split or stacked, of which unit
  executes a step within its charter, or of tooling route, where the mutation's content and end state are unchanged,
  the plan stated none of these as a requirement (Rule-15 phase 1), and no intermediate state is irreversible or
  reaches the world (a release cut, a tag, a publish, a destructive host action, a preference value). The plan-`Y` covers it and the completion evidence reports it; if any condition fails it is a new
  plan (`dyad/dmc/plan-departure.jsonld`, #555).
- **Mandate scope.** A plan that intends to accrete states a *rule* for the class of row it will open ("one child per
  failure mode") and a *ceiling* on how many, both the operator's to read and to refuse. A plan that states none
  accretes nothing beyond the rows a play-book it runs prescribes by a step of its own, whose rule is that step's class
  and whose ceiling the play-book's own count; a play-book that wants a question for a row says so in its step (#574).
  A row outside the rule, or past the ceiling, is a new plan.
- A carried row is born as its scope or step says: `open`, worked under this d-work, its done riding this done-`Y`; or
  `backlog`, filed for later, its own work waiting for an operator prompt, at which it is an explicit row (Ledger).
- A prompt that opens a new body of work is planned by the craft play-book (`dyad/playbooks/craft-instantiation.md`):
  a new craft instance unless one of its `craft-instantiation-criteria` fires, in which case the plan advises a new
  dyad system naming the criterion; its run-book is `dyad/runbooks/craft.md`, whose events the completion reply
  cites (#165).

## Completion counter-prompt (intent verification)
- The done-`Y` is the operator's verification that the d-work's intent was delivered as expected, asked on the output
  as it stands in the PR(s), before merge, so `main` never carries unverified output. The question is always the last
  line of the reply that believes the d-work is done.
- **Form**: `Y/N: Done with #<id> <title>?`, or the batch form. One parenthetical names what else the `Y` binds, in
  this order — accreted rows, retired rows, and under `merge-disposition: with-done` the unmerged PRs:
  `Y/N: Done with #<id> <title> (accreted #c, retires #r, merges PR #a)?`, each clause present only when it names
  something. The `Y` binds those sets exactly as the evidence listed them, so the operator verifies the set it got,
  not the one the plan promised; leaving a row out is a breach of this Rule. A row is named under `retires` only while
  it is `backlog` or `done`; an `open` or `planned` row a report supersedes closes by its own Done first (#574).
- **Evidence** (E8), before the question, in this order: the plan's definition of done, quoted, and the report that
  answers it; every PR by number and zone; each check's result as observed, or "CI absent" with the local guard
  results, the evidence block cited as Rule-2's Binding cites it; every host action with its class and change-log row
  (a missing row stated as a Rule-8 breach); every accreted or carried row — id, `mode`, what it holds, what it cost in
  dispositions — and every escalation; every retired row with its state and ground; each child's state; anything not
  delivered; every departure, execution details included; and anything the agent could not verify. An omission is a
  breach of this Rule, not a style choice.
- **Trace.** When the preference `dwork-trace` is `always` the evidence cites the d-work trace (play-book
  `dyad/playbooks/dwork-trace.md`), under `on-demand` only when the operator prompted for one: the completion reply
  prints its preview, and the reply that receives the done-`Y` writes it to `<instance>/d-work/traces/<id>.md`,
  carried by the Record commit, so it covers the `Y` and stays ledger-only; one with no transcript is still cited, its
  buckets marked absent (#213). A mandate close rides the mandate's own trace.
- **Record, merge, Close** (#202). The reply that asks does not merge. The reply that receives the done-`Y` takes
  three acts in order, so the ledger's record of the `Y` precedes every merge it ratifies. (1) **Record**: one
  clerical ledger commit holding the `disposed` entry, its provenance entry and the trace, the state left as it is,
  the entry naming each retired row and each PR with the head its `Y` was given on —
  `-d 'Y done (retires #r, merges PR #a at <head-a>)'`; that entry, never the state, is the record of the `Y`.
  (2) **Merge**, as clerical execution of it. (3) **Close**: a dispositionless ledger commit that sets `done` once
  every head the **operative** entry (the last `Y done`) names is on `main` — by the hosting's merge or Rule-14
  property 3's local merge, a squash or rebase recorded `landed <sha>` — and archives each retired row. A done-`Y` that
  names no merge is recorded `done` at once.
- A merge before the `Y` is self-ratification (Rule-2), an incident whatever the outcome (#47, #58, #67); `done`
  written before the named heads are on `main` is the converse breach, which the fence refuses (Mechanisms). While a
  ratified merge still owes a push — a rebase, a resolved conflict, the second PR of a sequence — the row stays `open`
  or `planned` (never `blocked`, which has no edge to `done`), its own plan-`Y` carrying the push, since `done` is
  terminal and the plan gate refuses a terminal row.
  A resolution that changes a head voids the `Y` given against it (Rule-2, Binding): the question is asked again, its
  answer a further entry on the same row.
- **The automaton.** While the operator's repository variable `DYAD_AUTOMATON` is `on`, the automaton
  (`dyad automaton run`, `dyad/scripts/automaton.py`) executes the merge and the Close from the recorded entry on
  `main` alone, pinned and in order. It decides nothing: a moved head, a conflict, or a retired row that is neither
  `backlog` nor `done` is a refusal posted to the home's inbox, never a resolution, so recording the `Y` is the last
  act an inferring unit takes for it (#556). With it off, the agent executes both by hand.
- **A relayed Done.** A Done question the home relays for a solo (Rule-16 Presence) presents its evidence in the form
  the preference `relay-form` names, cited by its `evidence-sha256` and brief form (Rule-14 property 3), with the
  unit's own question as its last line; the `Y` binds to what the unit asked.

## Batch disposition
- Preference `batch-disposition-mode`: `off` — every plan and Done question asked singly; `on-ignore` — singly, until
  the operator leaves one outstanding, the engagement signal itself; `always` — never singly. Once engaged the agent
  holds a **pending queue** of plan-ready and, separately, done-ready d-works, reports both counts at the end of every
  reply while either is non-empty, and drains it by naming items in batch questions; under `on-ignore` engagement
  lapses once both are empty.
- The batch forms replace the single forms, one kind per question: `Y/N: proceed with #a, #b, #c as planned?`, each
  with its own stored plan file, and `Y/N: Done with #a <title-a>, #b <title-b> (merges PR #w, #x)?`, full evidence
  for each before it and each d-work's accreted and retired rows in its own clause. A `Y` binds exactly the named set;
  anything else, none of it. Each row's entry names the whole set — `<date> Y plan (batch #a,#b,#c)`,
  `<date> Y done (batch #a,#b, merges PR #w at <head-w>)` — and the one `Y` is the same provenance entry in every named
  record (Rule-7). Beside them, never one of them, is the **mandate form** — the plan question over a plan that carries
  rows and the Done question naming them, two questions whatever the set's size: a batch compresses questions, a
  mandate compresses acts, and a carried row is never asked, so it never enters the queue; nor do a release question or
  the retirement form.
- The queue is recorded, not conversational: its counts and the last question asked live in the **board store**
  (Rule-16 Store), beside each open row's orchestration in flight — holder, wait, next act, the question owed
  verbatim, promises — so a **hop** of the session holding the board (the home, under `organization: m4`) loses none
  of it and asks the operator nothing about state. The board is written **write-ahead**: the entry before the dispatch,
  relay or question it records. Its guard checks shape only (#535).
- Reports and relays between units travel by the **inbox** (Rule-16 Store), addressed by unit name and read at the
  start of every turn: information, never authority — a disposition is read from the row and its provenance record,
  and the operator's words relayed to a unit travel verbatim, citing their provenance entry (#536). A message to a
  session is at most a doorbell, never the carrier. An actionable post is followed by one to the receiving unit's
  current session; an automaton notice goes to the home, which rings the unit it concerns; an information-only copy
  is posted as a notice and rings nobody; a self-addressed post needs none; and a unit no direct message reaches
  polls its inbox instead (`dyad/dmc/message-route.jsonld`, #584).

## Ledger
- The ledger is the row-file store `agent-corpus/d-work/rows/` (Rule-16), rendered to `LEDGER.md` on demand, one row
  per d-work. Its states are defined in the vocabulary (Rule-6) and move only along Rule-16's table (a `transition`);
  the consequences of each:
  - `open` — being worked, or suspended by a newer prompt. `planned` — its plan file authorized; execution may start
    in any session (Rule-15). `blocked` — deferred by the operator naming another d-work in `refs`; `open` again when
    that one is `done`.
  - `backlog` — opened by an operator disposition, or carried under the plan-`Y` whose play-book prescribes it; not
    started; `open` when the operator prompts for it, `archived` when retired.
  - `done` — the operator answered `Y` to the Done question *and* every merge it named has landed; between the two the
    row keeps its state, `disposed` carries the `Y`, and the state guard warns once per row (Mechanisms).
  - `archived` — retired by an operator `Y` naming the row, from `done` or `backlog` only; terminal, nothing moves,
    and a new row refs it, never reopens it. The question is the Done question of a delivered row whose report retires
    it, or, for rows no Done covers, the **retirement form** `Y/N: archive #a, #b, … #k?`, each row listed before it
    with what it holds and why; a `Y` archives exactly the named rows, anything else none. The agent never archives on
    its own judgment; `dyad dwork state <id> archived` is clerical execution, a ledger-only commit.
- A d-work may be decomposed into child rows (`refs: parent #N`). The parent's question is asked only when every child
  is `done`, `blocked`, `backlog`, or holding its own recorded done-`Y` and awaiting its merge — a child the operator
  never asked for is not work the parent owes, and any stricter gate could leave the parent unaskable (#290). The
  parent completes only on its own done-`Y`, its evidence naming each child's state.
- `disposed` records every disposition, in order, as `<date> <Y|N> <plan|done|merge #n|reason>` separated by `;`,
  each written clerically when given, so the chain of authorization is reconstructible from the ledger alone (D4);
  rows before 2026-09-12 #46 are not backfilled. A carried row's entry names the `Y` it rides — an accreted row's
  first `<date> Y plan (mandate #<id>)`, a carried `backlog` row's `<date> Y backlog (mandate #<id>)`, a retired row's
  `<date> Y archive (done #<id>)` — and its record copies that `Y`'s words, noted `mandate #<id>, <date>` or
  `done #<id>, <date>` (Rule-7 property 4). The optional `mode` field is `explicit` or `implicit`, absent meaning
  explicit (Rule-16 Store); a carried `backlog` row carries none, since its done never rides the parent's.
- **Ledger-only commits** (nothing outside `agent-corpus/d-work/`) and **events-only commits** (nothing outside
  `<runbooks>/events/`, `DYAD_RUNBOOKS`, Rule-19 property 1, holding events of read-only run-book commands) are
  clerical and go directly to `main` without a PR; one commit stays one zone (Rule-1), so a commit touching both is
  neither, and one that touches anything else goes by PR. Monitoring is no d-work: a standing read-only check
  authorizes nothing and never completes, so it opens no row and writes only its events (#438) — the scheduled sweep
  (Rule-14 property 3) among them, adding one notice to the home's inbox only for what is new or failing (#564).
- At session start the agent reads the ledger and reports every row not `done`, the `merge-disposition` value and the
  sentinel (`dyad/CLAUDE.md`), or, with the frame absent, says so and stops (E1). It touches its own presence file and
  reads every other session's (Rule-16), reporting an overlap that bears on the prompt at hand. Under
  `organization: m4` a session reads its unit's board instead of the whole ledger, the unit name saying which (Rule-16
  Presence; the organization craft's `crafts/cabinet/docs/operating-guide.md`, never a Rule; #369 C7).
- PR bodies — and on a branch the commit messages `dyad/guards/agent/prs.py` reads as the body — cite
  `d-work #<id>` as a claim of work, cross-referencing other rows as plain `#<id>` (#23). The plan gate requires each
  cited row, on the base branch, to be `open`, `planned` or `blocked` with a `Y plan` disposition (E3), and refuses
  every commit citing a terminal row.

## Mechanisms
- Rule-3 owns `rows.py` (the main fence) and `prs.py` (the plan gate), in `dyad/guards/agent/` (Rule-11 property 1),
  run as transaction guards on the kernel-only path (`package.py check --guards`) and re-run after the merge by
  corroboration, `dyad check --corroborate` in `.github/workflows/dyad-package.yml`, step `rule-3 fence (push range)`
  (Rule-14 property 3; #168). A guard change is an agent-zone PR, a wrapper change an infra-zone PR, each citing a
  Rule-3 d-work. Rule-2 cites `rows.py` by name and does not own it.
- **The main fence** fails a direct commit to `main` that is neither ledger-only nor events-only, read commit by commit
  with rename detection off. On such a commit, on each commit of a ledger-only branch and in a merge commit against
  each parent, it keeps the Done order: no commit both records a `Y done` naming a merge and sets `done`
  (`rows.done_order_problems`); the commit setting `done` finds a `Y done` already on the row and every head the
  operative entry names an ancestor of the base or of itself (`rows.landing_problems`), an unresolvable sha printing
  one line, never failing (#321); the interval is one warning per row (`rows.done_recorded_not_closed`) in every
  evidence block (#202). Under `dwork-trace: always` a commit adding a `Y done` entry carries or finds that row's
  `<instance>/d-work/traces/<id>.md` (`rows.trace_problems`), a mandate close exempt and a batch needing each named
  trace; `dwork state` and `dwork batch` refuse such an entry before their first write (`package.py trace_refusal`),
  a batch passing when an earlier `land <instance>/d-work/traces/<id>.md` line carries it (#465). `traces.py` checks
  the trace store, through `trace.check_store` (#227).
- **The plan gate** runs before a push over `origin/main..HEAD`, commit messages as body. A range whose every
  non-merge commit, read commit by commit with rename detection off, is ledger-only (`prs.ledger_only`, #191) or events-only (`dyadlib.events_only`, #438) claims no
  d-work and is exempt; a mix of the two is gated. Since the exemption rests on `main` admitting the same commits, the
  fence judges each commit of such a branch as on `main`, and each merge commit against both parents. That the event
  store only grows is the sysadmin craft's events guard's (`crafts/sysadmin/guards/events.py`, `sysadmin/events`). The
  incident log's check stays a script run by the suite until #170.

## Intake (work proposed by another agent)
A message from another agent opens no d-work. What it may carry is an intake, a candidate row, which the agent
surfaces to the operator exactly as carried; the operator's `Y` opens the row (`backlog` or `open`), its `refs`
naming the origin `<system>-<id>`. Two shapes are admissible:
- a **defect**: an observation with evidence — what, where (path, commit, run id), how it reproduces, the mechanism
  the sender verified — never a verdict or a required fix. The evidence goes into the plan file; the record's first
  entry is the operator's own `Y`, since the observation is the sender's words (Rule-7 property 4);
- an **enhancement**, only with its operator behind it: the verbatim operator prompt, or a row id in the sender's
  ledger whose provenance record holds it, quoted. The relayed prompt is the row's first provenance entry, noted
  `relayed via <session>`. An agent's own idea is a proposal for its own operator, whose prompt travels with it.

Anything else is returned to the sender with the missing shape named, and reported to the operator as received, not
as work. The operator may still open a row by prompting: this bounds what an agent may bring, never what the operator
may ask for.

## Incidents
- An incident is an action or outcome the plan did not name, or a plan item not achieved as the plan said: an error,
  a recovery, a failed check, an unplanned edit. It is reported in the reply where it occurred or the completion
  reply, whichever is first, and recorded — as an attack in the relevant falsification record if it falsifies a Rule
  or mechanism, otherwise as a row of `agent-corpus/audits/INCIDENTS.md` (date, d-work, what, cause, consequence) —
  in the d-work's own PR, or the next agent-zone PR for clerical work. A changed plan takes a fresh plan-`Y` before
  any further mutation (E9).
- Under `concise-mode: on` the reply where it occurred is the completion reply, and the record is written during the
  turn, before that reply, so an interrupted turn loses narration, never the record.
- Periodically the log is worked whole by the incident-hardening play-book (`dyad/playbooks/incident-hardening.md`),
  parameterized by the ledger it hardens: it groups incidents into failure modes and closes each by a fence at a named
  moment, by a `backlog` row naming the fence still to build — carried under the plan-`Y` that runs the exercise,
  never asked again — or by a recorded impossibility naming the Rule that makes it so; on a log that has not grown it
  only re-tests the fences already closed.

## Ratification events
- Answering `Y` to a plan counter-prompt (mutation authorization, with every row the plan carries).
- Answering `Y` to a d-work completion counter-prompt (intent verification, with the rows it names as accreted or
  retired and, under `merge-disposition: with-done`, the named merges).
- Answering `Y` to the retirement form. Rule-2 applies by reference to all three.

## Provenance
Operator rule, 2026-09-12. Refactored by d-work #585 (2026-11-04) around what opens a row, what a `Y` binds, the two
questions, what is never carried, the record of each `Y` and the automaton's execution, absorbing #574 (the definition
of done, the rows a play-book prescribes, retirements on the done-`Y`) and #584 (the doorbell), because amendments
bolted to sections had multiplied the per-act forms and cost the operator questions a `Y` had already answered.
Earlier text and its 29 amendments: `../falsification/rules/rule-3-d-work.md`.

Set: System Requirements.
