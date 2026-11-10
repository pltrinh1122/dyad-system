# Rule-3: d-work

**Intent:** Run every body of operator-prompted work as a d-work that opens on a prompt, is authorized by one plan-`Y` and closes on one done-`Y`, each `Y` binding exactly the acts its question names.
**Target:** a d-work

## Boundaries (out of scope)
- Who may ratify, and the kinds of act a `Y` may bind — Rule-2 (Binding of approval), applied by reference to the events
  declared here.
- Which zone a change belongs to — Rule-1. The plan file and the two phases — Rule-15. The row store, its transition
  table, the board store, the inbox and presence — Rule-16. The words of every prompt and disposition — Rule-7.
- What the agent may do on the live host — Rule-8, which classes every host action a plan names and keeps a destructive
  action's own question, asked singly and bound by its own `Y`.
- A release's question, its batch form and the release gate — Rule-11; a release question is asked under that Rule,
  apart from the plan and Done batches here.
- How another agent frames a proposal to its own operator — that system's Rule-10; this Rule judges what its message
  carries when it arrives (Intake, below).
- The machine step by step — which input moves a row, whose act it is, which record it writes, which layer executes it —
  the d-work play-book (`dyad/playbooks/d-work.md`), its input alphabet `dyadlib.INPUTS`: read here, never a Rule
  (#309).

## Conditions (triggers)
- The operator sends a prompt, or answers a counter-prompt.
- A prompt opens a row, or reopens one from `backlog`, under `intent-reading: on` (the intent question, Plan below).
- The agent is about to mutate the repo for a d-work (the plan gate), or believes a d-work is done (the Done question).
- The agent opens a row while executing another, under the plan-`Y` that carries it (Scope, below).
- A message from another agent proposes work (Intake, below).
- A session starts (the ledger report).
- A PR is opened or edited (`prs.py`); a commit is pushed to `main` (`rows.py`, the main fence).
- Under `batch-disposition-mode: on-ignore` (`preferences-corpus/PREFERENCES.md`) the operator's reply to a
  counter-prompt is a new prompt rather than its bare disposal: the engagement signal for a batch (Batch disposition,
  below).

## Scope (what opens a row)
Three things open a row: an operator prompt, an operator disposition, and a plan-`Y` whose plan names the row's class
(accretion).
- **A prompt**: operator text sent alone, text sent with a `Y`, and an amend's text that asks for something else (Answer
  grammar). It opens its d-work when the reply writes, proposes or carries a `Y/N` line, and it opens it before that
  question, so the answer has a row to land on (#492). The test is the reply's form, never the agent's inference. A new
  prompt while a d-work is open suspends it and opens another: d-works stack.
- **A disposition that names a row to open**: the `Y` that admits an intake (Intake, below), or files a row as
  `backlog`. A **bare** answer (`Y` or `N` to a counter-prompt) is not a prompt; the rows it opens are the ones its
  question names (What a `Y` binds, below).
- **Accretion**: an **accreted row** is one the agent opens while executing another, under that row's plan-`Y`. Under
  the preference `accretion: implicit` a plan-`Y` carries the rows its plan names a class for (Plan, below); such a row
  takes no disposition of its own and opens no d-work in the first bullet's sense, so nothing is suspended and nothing
  stacks. Under `accretion: explicit` it is asked for like any other row.

A **read-only answer** — a reply that only reads the corpus, writes nothing and asks no question — opens no row and
records nothing: it decides nothing (#492). A finding of the agent's reaches a row through one of the three above: the
agent reports it (Incidents, below) or proposes it, or a plan-`Y` names its class.

A d-work a prompt opened terminates on the operator's `Y` to its Done question; until then it is incomplete, to be
resumed. A `backlog` row, never started, ends when a `Y` archives it (Ledger).

The terms are the countersign model's (`dyad/playbooks/countersign-model.md`), adopted rather than coined (Rule-13
property 1) and defined in the vocabulary (Rule-6): a **mandate** is the standing countersignature of **implicit mode**;
the plan-`Y` that creates one is the **delegate edge**; an accreted row whose work departs from the mandate scope
returns to explicit mode by the **escalate edge** — the agent reports it and asks — the implicit **mode lifecycle** of
that play-book's Part II §4.

A subagent's actions are the agent's, bound by the same plan and Rules. Subagents read, search and draft — under
`delegation: plan-and-execute`, the plan file and an execution branch's changes too — and a delegated subagent reports
the sentinel first. Writing a row, asking or answering a counter-prompt, committing, pushing, opening or updating a PR,
merging, and running a reversible or destructive host action (Rule-8) are the main agent's alone, the party the operator
disposes to, which reports every delegated d-work's state each turn (E7, #107).

The automaton (Rule-2 Enforcement) is the third party, an executor: it opens no row, answers no question and decides
nothing; what it runs it records under its own name — a run-book event's `role: automaton` (Rule-19), a change-log
row's `actor: automaton` (Rule-8) (#593).

## Answer grammar
Three answers to a counter-prompt, the countersign model's **answer grammar** (`dyad/playbooks/countersign-model.md`
Part II §2):
- `Y` — the disposition asked for is given, binding the acts the question names (What a `Y` binds, below).
- `N`, bare — nothing is authorized; the agent revises. To the **intent question** (Plan, below) a bare `N` archives the
  row instead: nothing was built, so there is nothing to revise from, and the row leaves the board (#615).
- `N` with text — **amend**: the proposal refused and its revision asked for in the same words, entered verbatim as a
  `prompt` entry of the refused d-work's record (Rule-7). When it asks for the same proposal revised it opens no second
  row, and the plan file is revised in place, the refused revision kept (Rule-15); text that asks for something else
  opens its own d-work. Either way the `N` authorizes nothing; the revision takes its own `Y`.

A `Y` with text is a `Y` plus a prompt. Silence is not consent: an unanswered counter-prompt authorizes nothing. An
answer is read by its meaning: `Y`, `y` and `yes` are one `Y`, `N`, `n` and `no` one `N`, the row recording the token
and the provenance record the words as typed (Rule-7). Where two readings lead to different acts the agent asks, as a
blocking question (Rule-8's form); the listed variants of one answer lead to one act
(`dyad/dmc/label-case.jsonld`, #553).

## What a `Y` binds
A `Y` binds exactly the acts its question names (Rule-2, Binding of approval): what the question states and what it
cites directly. A row of work takes two questions, or three under the preference `intent-reading: on`
(`preferences-corpus/PREFERENCES.md`; absent, `off`), the intent question first:
- the **intent question** cites the intent reading, the plan file's first section, so its **intent-Y** binds the reading
  and the definition of done it proposes, and nothing else: no mutation, no row, no PR (Plan, below);
- the **plan question** cites the plan file, which states each carried class in words and with its number — its
  mandate scope, or a play-book step's class, the step id only a pointer — so its plan-`Y` binds the mutation the plan describes, every PR of the d-work, and every row the plan carries
  (Plan, below);
- the **Done question** names the d-work, its accreted rows, the rows its report retires and its unmerged PRs, so its
  done-`Y` verifies the output, closes the accreted set, archives exactly the retired rows and ratifies exactly those
  merges (Completion counter-prompt, below).

Beside a row's questions stands the **precedent question**, `Y/N: admit as precedents <cases>?`, listing decision-log
entries (Rule-16 Store) by record and case id before it: its **precedent-Y** binds exactly the listed entries, which become
precedents of their records' kind `precedent` (`dyad/dmc/judgement-complexity.jsonld`), and nothing else. A done-`Y`
covers the work and its rulings only as candidates; a ruling becomes a precedent only by a precedent-`Y` naming it
(#644). Which outcomes a precedent may settle at all is `dmc:precedent-scope`'s, by each outcome's declared effect
(Rule-2, Binding of approval; #649).

A batch counter-prompt binds each d-work it names as its single question would (Batch disposition, below). A row or act
is **carried** when another's question names it — a plan question naming its class, a Done question naming it under
`retires` — so that `Y` binds it with no question of its own. Work the plan does not describe, and a row its scope or
play-book step does not cover, is a new plan needing a new `Y`. What a plan-`Y` may carry is bounded by Rule-2's list:
it carries no act of these kinds — a destructive host action (Rule-8), a release (Rule-11), an intake (Intake, below), a
change to a preference value, a mutation the plan did not describe — and each is asked under the Rule that owns it. A
release under the release gate is named in its own d-work's Done question (Rule-11), so that done-`Y` binds it as a
named act.

Under the preference `dwork-slug: on` (`preferences-corpus/PREFERENCES.md`; absent, `off`), every row id presented to
the operator — in a reply, a counter-prompt line, a relay and the CLI's listings — reads `#<id>-<slug>`, the row's row
slug (Rule-16 Store) after its number; a row without one reads `#<id>`, and the forms in this Rule are written bare. The
slug is presentation: a question binds the rows it names by their numbers, and every stored reference — `refs`, a
`disposed` entry, a provenance record, an inbox message, a PR body's `d-work #<id>` — stays the bare number (#622).

## Plan (mutation authorization)
- Under `intent-reading: on`, the agent's first substantive reply to a prompt that opens a row, or reopens one from
  `backlog`, is the **intent reading**, stored first as the plan file's first section (Rule-15): each portion of the
  prompt classed by `dyad/dmc/intent-reading.jsonld` — new, overlap (duplicate when complete), supersede, adjacent,
  ambiguous or false premise — against the candidates `dyad dwork intent <id>` prints, the capabilities and the board;
  the definition of done it proposes; and the last line `Y/N: intent aligned for #<id> <title>?`, or the batch form. The
  intent-`Y` accepts the reading and its definition of done; an amend corrects it in place; a bare `N` archives the row
  (Answer grammar). The plan follows the intent-`Y`, and `dyad plan check` warns on a prompt-opened row planned with no
  `Y intent` (#615). Under `intent-reading: off` no intent question is asked, and the plan below is the first reply.
- The agent's first substantive reply to a prompt that opens a d-work, after its intent-`Y` where one is asked, is a
  plan, stored first as a plan file (Rule-15): its definition of done, the intent as read, the mutation proposed
  (falsified first, Rule-9; framed per Rule-10), and the last line `Y/N: proceed with #<id> as planned?`, or the batch form. The definition of done is the operator's
  words, quoted from the provenance record, or one marked *proposed* that the intent-`Y` accepts under
  `intent-reading: on` and the plan-`Y` under `off`, and an amend corrects:
  one row per definition of done the operator can evaluate, over the largest scope it lets the operator judge (#574).
- A row moved to `planned` (`dwork state <id> planned`) has had its plan read by `dyad plan check <id>` — a second
  zone among the files touched, a touched module whose test is not listed, a released craft touched without a
  `VERSION` bump, callers of a function the mutation names, a `refs` row not done, `order: required` with no `step:`
  line — each a warning for the plan's reader, never a refusal (#592).
- The plan-`Y` authorizes the mutation and binds every PR of the d-work to the plan. Work that departs from it is a
  **new plan** needing a new `Y`; until a `Y` the d-work stays open with nothing authorized. Every plan is asked, a
  one-line plan included; a row the plan-`Y` carries was named in that question and is asked no second time.
- An **execution detail** is a change of step order, of how PRs are split or stacked, of which unit executes a step
  within its charter, or of tooling route, where the mutation's content and end state are unchanged, the plan stated
  none of these as a requirement (Rule-15 phase 1), and no intermediate state is irreversible or reaches the world (a
  release cut, a tag, a publish, a destructive host action, a preference value). So is an **internal realization**, a
  change whose effect stays inside the PR, in one of three forms: **placement**, a file's path differing where the
  move stays within one zone and one craft root, the content is byte-identical, the old path never landed on `main`,
  no file outside the PR refers to it, it is in no released craft's tree and the plan did not name it as a
  requirement; **implied means**, where the plan's text names the effect and the means adds no public surface; and
  **compatible extension**, an optional parameter of an internal function that defaults to the old behaviour, with no
  caller changed and a test showing it. Public surface is a `dyadlib.CLI` row, a `dyad/surface.md` row, a path in a
  released craft's tree, or Rule or preference text, and each use of an internal realization is a departure line in
  the completion evidence (`dmc:plan-departure`, #643). The plan-`Y` covers an execution detail and the completion
  evidence reports it. A change that meets fewer than all of these conditions is a departure, and so a new plan
  (`dyad/dmc/plan-departure.jsonld`, #555).
- **Mandate scope.** A plan carries rows from two sources, each stated in the plan file, so the plan question names it.
  (a) A **mandate scope** the plan states: a *rule* for the class of row it will open ("one child per failure mode") and
  a *ceiling* on how many. (b) A step of a play-book the plan runs that prescribes a class of row: the plan states that
  class in words, which is the rule, and a number, which is the ceiling — the step's count, or an upper bound where the
  count is known only in execution (#574). Rule and ceiling are the operator's to read before the plan-`Y` and to
  refuse. A play-book that wants a
  question for a row says so in its step. A plan stating neither source carries no row. A row outside the rule, or past
  the ceiling, is a new plan, so `dwork new … --mandate <id>` refuses, before any write, the row past the ceiling the
  mandate's latest plan revision states (#592).
- A carried row is born as its scope or step says: `open`, worked under this d-work; or `backlog`, filed for later, its
  work waiting for an operator prompt. Its Done is the question its plan names: this d-work's done-`Y`, which then names
  it, or its own (Completion counter-prompt).
- A prompt that opens a new body of work is planned by the craft play-book (`dyad/playbooks/craft-instantiation.md`):
  when none of its `craft-instantiation-criteria` fires the plan assumes a new craft instance, and when one fires it
  advises a new dyad system naming the criterion; its run-book is `dyad/runbooks/craft.md`, whose events the completion
  reply cites (#165).

## Completion counter-prompt (intent verification)
- The done-`Y` is the operator's verification that the d-work's intent was delivered as expected, asked on the output as
  it stands in the PR(s), before merge, so `main` never carries a PR holding a path outside `agent-corpus/d-work/` before its done-`Y`. The question is
  always the last line of the reply that believes the d-work is done.
- **Form**: `Y/N: Done with #<id> <title>?`, or the batch form. One parenthetical names what else the `Y` binds, in this
  order — accreted rows, retired rows, and under `merge-disposition: with-done` the unmerged PRs:
  `Y/N: Done with #<id> <title> (accreted #c, retires #r, merges PR #a)?`, each clause present when it names something;
  `accreted` names the accreted rows this `Y` closes, and one already terminal by its own Done is reported in the
  evidence, not named (#587).
  The `Y` binds those sets exactly as the evidence listed them, so the operator verifies the set it got, not the one the
  plan promised; leaving a row out is a breach of this Rule. A row named under `retires` is `backlog` or `done` when
  named; an `open` or `planned` row a report supersedes closes by its own Done first (#574).
- **Evidence** (E8), before the question, in this order: the plan's definition of done, quoted, and the report that
  answers it; every PR by number and zone; each check's result as observed, or "CI absent" with the local guard results,
  the evidence block cited as Rule-2's Binding cites it; every host action with its class and change-log row (a missing
  row stated as a Rule-8 breach); every accreted or carried row — id, `mode`, what it holds, what it cost in
  dispositions — and every escalation; every retired row with its state and ground; each child's state; anything not
  delivered; every departure, execution details included; and anything the agent could not verify. An omission is a
  breach of this Rule, not a style choice. For a row phased `done-ready`, `dyad board draft <id>` prints the data half
  — the definition of done quoted, the PRs with their zones and recorded heads, the evidence by its sha256, the accreted
  rows, the trace, and the question as `board advance … asked` stores it — and the agent writes the judgment (#587).
- **Trace.** When the preference `dwork-trace` is `always` the evidence cites the d-work trace (play-book
  `dyad/playbooks/dwork-trace.md`); under `on-demand` it cites one when the operator prompted for one. The completion
  reply prints its preview, and the reply that receives the done-`Y` writes it to `<instance>/d-work/traces/<id>.md`
  from the Done words (`dwork trace --out --said-file`), never as the preview (Mechanisms); the Record commit carries
  it, so it covers the `Y` and stays ledger-only; one with no transcript is still cited, its
  buckets marked absent (#213). A mandate close rides the mandate's own trace.
- The reply that asks does not merge. A done-`Y` that names no merge has nothing in flight: one ledger commit holds its
  `disposed` entry, its provenance entry, the trace and the row's candidates (Record, below), sets `done` at once, and
  archives each retired row it names.
- **Record, merge, Close** (#202), for a done-`Y` that names a merge. The reply that receives it takes three acts in
  order, so the ledger's record of the `Y` precedes every merge it ratifies. (1) **Record**: one clerical ledger commit
  holding the `disposed` entry, its provenance entry and the trace, the state left as it is, the entry naming each
  retired row and each PR with the head its `Y` was given on — `-d 'Y done (retires #r, merges PR #a at <head-a>)'`;
  that entry is the record of the `Y`, and the state is not. The same commit carries the row's rulings as decision-log
  candidates (Rule-16 Store): the file `dyad board draft <id> --decisions-out <file>` writes, the structured
  candidates of the row's own sources and the prose lines the agent filled in its slots, recorded by `--decisions`
  on `dwork state … -d 'Y done …'` or `board advance … answered-Y`; `dwork state` refuses, before any write, a `Y done`
  with no `--decisions` on a row whose draft lists a candidate, and the evidence names any line the agent dropped with
  its reason (#648). (2) **Merge**, as clerical execution of it. (3) **Close**:
  a dispositionless ledger commit that sets `done` once every head the **operative** entry (the last `Y done`) names is
  on `main` — by the hosting's merge or Rule-14 property 3's local merge, a squash or rebase recorded `landed <sha>` —
  and archives each retired row.
- A merge before the `Y` is self-ratification (Rule-2), an incident whatever the outcome (#47, #58, #67); `done` written
  before the named heads are on `main` is the converse breach, which the fence refuses (Mechanisms). While a ratified
  merge still owes a push — a rebase, a resolved conflict, the second PR of a sequence — the row stays `open` or
  `planned` — the states the plan gate admits that have an edge to `done` — its own plan-`Y` carrying the push. A
  resolution that changes a head voids the `Y` given against it (Rule-2, Binding): the question is asked again, its
  answer a further entry on the same row.
- **The automaton.** While the operator's repository variable `DYAD_AUTOMATON` is `on`, the automaton
  (`dyad automaton run`, `dyad/scripts/automaton.py`) executes the merge and the Close from the recorded entry on `main`
  alone, pinned and in order. It decides nothing: a moved head, a conflict, or a retired row whose state is `open`,
  `planned`, `blocked` or `archived` is a refusal posted to the home's inbox, never a resolution, so recording the `Y`
  is the last act an inferring unit takes for it (#556). While it is `off`, the agent executes both by hand.
- **A relayed Done.** A Done question the home relays for a solo (Rule-16 Presence) presents its evidence in the form
  the preference `relay-form` names, cited by its `evidence-sha256` and brief form (Rule-14 property 3), with the unit's
  own question as its last line; the `Y` binds to what the unit asked.

## Batch disposition
- Preference `batch-disposition-mode`: `off` — every intent, plan and Done question asked singly; `on-ignore` — singly, until
  the operator leaves one outstanding, the engagement signal itself; `always` — never singly. Once engaged the agent
  holds a **pending queue** of intent-ready, plan-ready and, separately, done-ready d-works, and drains it by naming items
  in batch questions; under `on-ignore` engagement lapses once both are empty.
- Every reply ends, before its one `Y/N` line, with the **closing line** in the form the preference `awaiting-you`
  (`preferences-corpus/PREFERENCES.md`; absent, `on`) names. Under `on` it reads
  `Awaiting you: <n> <kind> (#id…), …`, or `Awaiting you: nothing.`, then `Coming: <n> <kind>`, each part shown only
  when non-zero, the Coming part only under the preference `coming` (absent, `on`; #665). **Awaiting you** counts the questions asked and not answered, a batch question once, by the kind
  `dmc:disposition-request` gives each recorded question, in two groups printed d-work first —
  `Awaiting you: d-work 1 plan (#647); merge 1 (PR #723).`: the d-work group (`intent`, `plan`, `done`, `retirement`,
  `precedent`) and the merge group (`merge`, `release`, `destructive`); a recorded question of no listed form, `none`,
  counts nothing and is warned. **Coming** counts the pending queue. Under `off` it reports the queue's
  counts while any is non-empty. Either way `dyad board` generates the line from the questions the board
  records and the agent copies it. A question is recorded on its row's entry before it is asked: an intent, plan or
  Done question by its phase, any other as the entry's `question` (write-ahead, below). So a question asked unrecorded
  is an incident (Incidents), never a line the agent adds by hand. The line counts what the records show; its form
  authorizes nothing (#646).
- The batch forms replace the single forms, one kind per question: `Y/N: intent aligned for #a, #b, #c?`, each with its
  own stored intent reading; `Y/N: proceed with #a, #b, #c as planned?`, each with
  its own stored plan file; and `Y/N: Done with #a <title-a>, #b <title-b> (merges PR #w, #x)?`, full evidence for each
  before it and each d-work's accreted and retired rows in its own clause. A `Y` binds exactly the named set; every
  answer short of `Y` binds none of it. Each row's entry names the whole set — `<date> Y plan (batch #a,#b,#c)`,
  `<date> Y done (batch #a,#b, merges PR #w at <head-w>)` — and the one `Y` is the same provenance entry in every named
  record (Rule-7). Beside the batch forms stands the **mandate form** — the plan question over a plan that carries rows
  and the Done question naming them, two questions whatever the set's size: a batch compresses questions, a mandate
  compresses acts. A carried row, a release question and the retirement form never enter the queue: the first is never
  asked, the others are asked on their own. The precedent question is its own kind too, never folded into a Done
  question: candidates wait and are asked as one batch at the next backlog grooming or once at least five are pending,
  whichever is first (#644).
- The queue is recorded: its counts and the last question asked live in the **board store** (Rule-16 Store), beside each
  open row's orchestration in flight — holder, wait, next act, the question owed verbatim, promises — so a **hop** of
  the session holding the board (the home, under `organization: m4`) loses none of it and asks the operator nothing
  about state. The board is written **write-ahead**: the entry before the dispatch, relay or question it records. Its
  guard checks shape (#535). An entry with an orchestration phase is moved only by the recorded events of Rule-16's
  table (`dyad board advance`), which derives the wait, the next act and the question, so no unit composes them by hand
  (#587).
- Reports and relays between units travel by the **inbox** (Rule-16 Store), addressed by unit name and read at the start
  of every turn: information, never authority — a disposition is read from the row and its provenance record, and the
  operator's words relayed to a unit travel verbatim, citing their provenance entry (#536). A message to a session is at
  most a doorbell, never the carrier. An actionable post to a unit whose current session a direct message reaches is
  followed by one to that session; an automaton notice goes to the home, which rings the unit it concerns; an
  information-only copy is posted as a notice and rings nobody; a self-addressed post rings nobody; and a unit no direct
  message reaches — a terminal desk, a unit with no live session — polls its inbox (`dyad/dmc/message-route.jsonld`,
  #584).

## Ledger
- The ledger is the row-file store `agent-corpus/d-work/rows/` (Rule-16), rendered to `LEDGER.md` on demand, one row per
  d-work. Its states are defined in the vocabulary (Rule-6) and move along Rule-16's table (a `transition`); the
  consequences of each:
  - `open` — being worked, or suspended by a newer prompt. `planned` — its plan file authorized; execution may start in
    any session (Rule-15). `blocked` — deferred by the operator naming another d-work in `refs`; `open` again when that
    one is terminal (`done` or `archived`).
  - `backlog` — opened by an operator disposition, or carried under the plan-`Y` whose play-book prescribes it; not
    started; `open` when the operator prompts for it, `archived` when retired.
  - `done` — the operator answered `Y` to the Done question *and* every merge it named has landed; between the two the
    row keeps its state, `disposed` carries the `Y`, and the state guard warns once per row (Mechanisms).
  - `archived` — retired by an operator `Y` naming the row, from `done` or `backlog`, or reached from `open` by the
    operator's bare `N` to the row's intent question while it holds no `Y plan` (#615); terminal, nothing moves, and a new
    row refs it, never reopens it. The question is the Done question of a delivered row whose report retires it, or, for
    rows no Done covers, the **retirement form** `Y/N: archive #a, #b, … #k?`, each row listed before it with what it
    holds and why; a `Y` archives exactly the named rows, and every answer short of `Y` archives none. The agent
    archives on an operator `Y` alone; `dyad dwork state <id> archived` is clerical execution, a ledger-only commit.
- A d-work may be decomposed into child rows (`refs: parent #N`). The parent's question is asked only when every child
  is terminal (`done` or `archived`), `blocked`, `backlog`, or holding its own recorded done-`Y` and awaiting its merge
  — a child the operator never asked for is not work the parent owes, and a stricter gate could leave the parent
  unaskable (#290). The parent completes on its own done-`Y`, its evidence naming each child's state.
- For every row opened from 2026-09-12 #46 on, `disposed` records every disposition, in order, as
  `<date> <Y|N> <plan|done|merge #n|reason>` separated by `;`, `<date>` the UTC date (`dyadlib.utc_date`, #592), each
  written clerically when given, so the chain of
  authorization is reconstructible from the ledger alone (D4). A carried row's entry names the `Y` it rides — an
  accreted row's first `<date> Y plan (mandate #<id>)`, a carried `backlog` row's `<date> Y backlog (mandate #<id>)`, a
  retired row's `<date> Y archive (done #<id>)` — and a precedent-`Y`'s entry, on the row whose decision log holds the
  entries, is `<date> Y precedent (<n> cases: <record>×<k>, …)`, its words copied into that row's record as any
  disposition's are (Rule-7 property 5); a carried row's record copies that `Y`'s words, noted `mandate #<id>, <date>`
  or `done #<id>, <date>` (Rule-7 property 4). The optional `mode` field names how a row was opened (Rule-16 Store):
  `implicit` on an accreted row, born `open` under another row's plan-`Y`; `explicit`, or the field absent, on every
  other row, a carried `backlog` row included. It says nothing of which Done closes the row. The agent chooses a
  row's row slug from its title when the row opens (`dwork new --slug`, which refuses a row without one under
  `dwork-slug: on`): 2–3 tags, a defined term in its own case (`intent-Y`); it is never changed, and a terminal row
  never gains one.
- **Ledger-only commits** (nothing outside `agent-corpus/d-work/`) and **events-only commits** (nothing outside
  `<runbooks>/events/`, `DYAD_RUNBOOKS`, Rule-19 property 1, holding events of read-only run-book commands) are clerical
  and go directly to `main` without a PR. One commit stays one zone (Rule-1), so a commit touching both is **neither**
  and goes by PR, as a commit that **touches anything else** does. Monitoring is no d-work: a standing read-only check
  authorizes nothing and never completes, so it opens no row (#438). Its writes are its events and, for the automaton
  sweep (Rule-14 property 3), one notice to the home's inbox for what is new or failing (#564, #617).
- At session start the agent reports the rows not `done`, the `merge-disposition` value and the sentinel
  (`dyad/CLAUDE.md`), or, with the frame absent, says so and stops (E1). Under `organization: flat` it reads the whole
  ledger; under `organization: m4` it reads its unit's board, the unit name saying which (Rule-16 Presence; the
  organization craft's `crafts/cabinet/docs/operating-guide.md`, never a Rule; #369 C7). It touches its own presence
  file and reads every other session's (Rule-16), reporting an overlap that bears on the prompt at hand. The home
  reads `dyad board resume` at session start and at each operator prompt: it prints, from the ledger alone, what waits
  on time rather than on activity — heads not landed, a code push not corroborated, a sweep not delivered (#619), a
  stale board, work in flight and backlog hygiene — which no sweep posts (Rule-14 property 3, #617).
- PR bodies — and on a branch the commit messages `dyad/guards/agent/prs.py` reads as the body — cite `d-work #<id>` as
  a claim of work, cross-referencing other rows as plain `#<id>` (#23). The plan gate requires each cited row, on the
  base branch, to be `open`, `planned` or `blocked` with a `Y plan` disposition (E3), and refuses every commit citing a
  terminal row.

## Mechanisms
- Rule-3 owns `rows.py` (the main fence) and `prs.py` (the plan gate), in `dyad/guards/agent/` (Rule-11 property 1), run
  as transaction guards on the kernel-only path (`package.py check --guards`) and re-run after the merge by
  corroboration, `dyad check --corroborate` in `.github/workflows/dyad-package.yml`, step `rule-3 fence (push range)`
  (Rule-14 property 3; #168). A guard change is an agent-zone PR, a wrapper change an infra-zone PR, each citing a
  Rule-3 d-work. Rule-2 cites `rows.py` by name and does not own it.
- **The main fence** admits a direct commit to `main` that is ledger-only or events-only and fails every direct commit
  of another class, read commit by commit with rename detection off. On a direct commit, on each commit of a ledger-only
  branch and in a merge commit against each parent, it keeps the Done order: no commit both records a `Y done` naming a
  merge and sets `done` (`rows.done_order_problems`); the commit setting `done` finds a `Y done` already on the row and
  every head the operative entry names an ancestor of the base or of itself (`rows.landing_problems`), judged on the
  heads this clone resolves, a sha it cannot resolve getting one printed line that states no judgement (#321); the
  interval is one warning per row (`rows.done_recorded_not_closed`) in every evidence block (#202). Under
  `dwork-trace: always` a commit adding a `Y done` entry carries or finds `<instance>/d-work/traces/<id>.md` for each
  d-work its Done question named as `Done with #<id>` — the one, or each one of a batch (`rows.trace_problems`); an
  accreted row's entry, noted `mandate #<id>`, is a mandate close, and the trace it needs is the mandate's.
  `dwork state` and `dwork batch` refuse an entry lacking its trace before their first write
  (`package.py trace_refusal`), a batch passing when an earlier `land <instance>/d-work/traces/<id>.md` line carries it
  (#465). It fails such an entry whose trace, carried or already on the base, is a preview; `traces.py` checks the
  trace store, through `trace.check_store` (#227), and fails a stored preview the instance's
  `traces_preview_legacy.local.txt` does not name (#592).
- **The plan gate** runs before a push over `origin/main..HEAD`, commit messages as body, and judges every range that
  claims a d-work. A range whose every non-merge commit, read commit by commit with rename detection off, is ledger-only
  (`prs.ledger_only`, #191) or events-only (`dyadlib.events_only`, #438) claims none, and the gate skips it; a range
  mixing the two claims one and is gated. Since the skip rests on `main` admitting the same commits, the fence judges
  each commit of such a branch as on `main`, and each merge commit against both parents. That the event store only grows
  is the sysadmin craft's events guard's (`crafts/sysadmin/guards/events.py`, `sysadmin/events`). The incident log's
  check stays a script run by the suite until #170.

## Intake (work proposed by another agent)
Intake judges a message that proposes work no row holds yet. A message about a row already open — a report, a relay of
the home's instruction, a notice — is information (Batch disposition, the inbox) and is judged by none of what follows.
Within one dyad system, an operator prompt relayed verbatim by another unit is a **relayed prompt**: a prompt (Scope),
entered with the note `relayed via <session>` (Rule-7 property 4). A message from another agent that carries no relayed
prompt of this system's operator opens no d-work. What it may carry is an intake, a candidate row, which the agent
surfaces to the operator exactly as carried; the operator's `Y` opens the row (`backlog` or `open`), its `refs` naming
the origin `<system>-<id>`. An agent's message may bring two shapes:
- a **defect**: an observation with evidence — what, where (path, commit, run id), how it reproduces, the mechanism the
  sender verified — never a verdict or a required fix. The evidence goes into the plan file; the record's first entry is
  the operator's own `Y`, since the observation is the sender's words (Rule-7 property 4);
- an **enhancement**, carrying its operator's verbatim prompt, or a row id in the sender's ledger whose provenance
  record holds it, quoted. The relayed prompt is the row's first provenance entry, noted `relayed via <session>`. An
  agent's own idea is a proposal for its own operator, whose prompt travels with it.

A message of neither shape is returned to the sender with the missing shape named, and reported to the operator as
received, not as work. These shapes bound what an agent's message may bring; an operator prompt on the same matter opens
a row as every prompt does (Scope).

## Incidents
- An incident is an action or outcome the plan did not name, or a plan item not achieved as the plan said: an error, a
  recovery, a failed check, an unplanned edit. It is reported in the reply where it occurred or the completion reply,
  whichever is first, and recorded: as an attack in the relevant falsification record when it falsifies a Rule or
  mechanism, and as a row of `agent-corpus/audits/INCIDENTS.md` (date, d-work, what, cause, consequence) when it
  falsifies neither — in the d-work's own PR, or for clerical work in the next agent-zone PR. A changed plan takes a
  fresh plan-`Y` before any further mutation (E9).
- A fault that stops a row's next act from outside the row's own diff takes the home `dyad/dmc/blocker-home.jsonld`
  gives it (the d-work play-book): a fix that only restores what a Rule, record, check or test already states is a row
  the blocked row's plan carries when it states that class (Plan, Mandate scope), asked no plan question; a fix that
  changes what one of them decides is a revision of the blocked row's plan; and a row of its own is proposed only for a
  fix that adds what the system did not have, or that no open row can carry or revise (#623).
- Under `concise-mode: on` the reply where it occurred is the completion reply, and the record is written during the
  turn, before that reply, so an interrupted turn loses narration, never the record.
- Periodically the log is worked whole by the incident-hardening play-book (`dyad/playbooks/incident-hardening.md`),
  parameterized by the ledger it hardens: it groups incidents into failure modes and closes each by a fence at a named
  moment, by a `backlog` row naming the fence still to build — carried under the plan-`Y` that runs the exercise and
  asked no second time — or by a recorded impossibility naming the Rule that makes it so; on a log that has not grown
  its one act is re-testing the fences already closed.

## Ratification events
- Answering `Y` to an intent question (the reading and its definition of done accepted, under `intent-reading: on`).
- Answering `Y` to a plan counter-prompt (mutation authorization, with every row the plan carries).
- Answering `Y` to a d-work completion counter-prompt (intent verification, with the rows it names as accreted or
  retired and, under `merge-disposition: with-done`, the named merges).
- Answering `Y` to the retirement form.
- Answering `Y` to a precedent question (the listed decision-log entries admitted as precedents). Rule-2 applies by
  reference to all five.

## Provenance
Operator rule, 2026-09-12. Refactored by d-work #585 (2026-11-04) around what opens a row, what a `Y` binds and the two
questions, absorbing #574 and #584, and re-scoped by its plan revision 2 so that every claim survives falsification and
holds within its own scope. Earlier text, its 29 amendments and the claim table:
`../falsification/rules/rule-3-d-work.md`. Plan, Completion counter-prompt, Ledger and Mechanisms state the fences of #592 2026-11-05 (d-work
#606): the plan check at `planned`, the mandate ceiling at `dwork new`, the trace written from the Done words and UTC
dates had landed as code with no sentence; see the same record, amendment #606. Batch disposition and Completion counter-prompt gain the orchestration
phase and `board draft` 2026-11-05 (d-work #587); see `../falsification/rules/rule-16-concurrent-sessions.md`, amendment
#587. Scope names the automaton as the third party 2026-11-05 (d-work #593, P6): Rules 8, 14 and 19 had made it a
party in their records, and this Rule still knew two; see `../falsification/rules/rule-3-d-work.md`, amendment #593.
Conditions, Answer grammar, What a `Y` binds, Plan, Batch disposition, Ledger and Ratification events gain the intent
question 2026-11-06 (d-work #615), under the preference `intent-reading` (`off` ships): 27 of 60 refusals in the
ledger had restated intent or scope after a full plan, six of them after a delivery, and nothing asked the reading
before the plan; see `../falsification/rules/rule-3-d-work.md`, amendment #615. Ledger names the automaton sweep and
the home's read of `dyad board resume` at session start and at each operator prompt 2026-11-06 (d-work #617): the
stall findings left the twice-daily sweep for the home's read; see
`../falsification/rules/rule-14-system-infrastructure.md`, amendment #617. Ledger's list of what the home reads gains
a sweep not delivered 2026-11-06 (d-work #619); see the same record, amendment #619. What a `Y` binds and Ledger gain
the row slug 2026-11-07 (d-work #622), under the preference `dwork-slug`: the operator asked that a row id be presented
with two or three tags after its number, so a row is known by more than a number; the question still binds by the
number; see `../falsification/rules/rule-3-d-work.md`, amendment #622. Incidents gains the blocker home 2026-11-07 (d-work
#623): a fault found downstream had been fixed under three homes in one week at up to three questions each, with nothing
to say which; see the same record, amendment #623. Plan's execution detail gains internal realization 2026-11-08
(d-work #643): two file moves ruled execution detail (#626, #640) and two #619 cases ratified as planned or as
execution detail fitted none of the record's differences, and a blind precedent test read all four as new plans; one
clause, fenced by no effect outside the PR, admits the three forms and overrules #626's move; see the same record,
amendment #643. What a `Y` binds, Batch disposition, Ledger and Ratification
events gain the precedent question 2026-11-08 (d-work #644): a done-`Y` had covered every ruling inside its work
without the operator examining one (#626's zone move), so a ruling becomes a precedent only by a `Y` that names it;
see the same record, amendment #644. Batch disposition gains the closing line, `Awaiting you` under the preference
`awaiting-you`, 2026-11-08 (d-work #646): the line every reply ended with counted rows ready for a question not yet
asked, which is the agent's work, and never a question asked and not answered, the one thing that waits on the operator;
it was written by hand. It is now generated from the asks the board records, each classed by the record
`dmc:disposition-request` (plan revision 3), which also counts merge questions; see the same record, amendment #646.
Completion counter-prompt's Record step carries the row's decision-log candidates 2026-11-09 (d-work #648): the log was
filled only by hand-run backfills, so a ruling named in a Done reached it only if someone later searched for it; see
the same record, amendment #648. What a `Y` binds cites the precedent's scope 2026-11-09 (d-work #649); see
`../falsification/rules/rule-2-no-self-ratify.md`, amendment #649. Batch disposition's closing line shows its Coming
part under the preference `coming` 2026-11-10 (d-work #665): the operator asked that the part counting the agent's own
queue be a setting of its own, on by default, while `awaiting-you: off` hid the Awaiting part with it; see
`../falsification/rules/rule-3-d-work.md`, amendment #665.

Set: System Requirements.
