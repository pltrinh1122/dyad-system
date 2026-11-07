# Play-book: d-work (core craft, `dyad-operator`; #309)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the agent follows for a
recurring decision; its steps are a run-book. This one decides, at every state change of a d-work, **which
transition is legal now, what input it takes and from whom, and which record the move writes** — the
decision Rule-3, Rule-7, Rule-15 and Rule-16 each own one part of, and that the agent made by inference
against the CLI help at every row write (Rule-13 property 1: the recurrence proposes code — the machine's
input alphabet is `dyadlib.INPUTS`, and this play-book's two tables are pinned to it and to the guards by
`dyad/tests/test_playbooks.py`). Read by Rule-3's Boundaries. Steps: `dyad/runbooks/d-work.md` —
`open`, `plan`, `authorize`, `execute`, `verify-prs`, `evidence`, `record`, `done-record`, `complete`,
`close-landed`, `defer`, `resume`, `sync-mirror` (the four harvested from recurring hand-written scripts, #556,
implemented by `dyad steps`) — run through
`DWORK=<id> dyad runbook run d-work <step>`, the core runner, so each step leaves an event. The native
commands stay the default for a ledger commit, for the reason `dwork-trace.md` records (#247: a runner
event is a workstation-zone file the ledger commit cannot carry).

It states the **architecture of the d-work framework**: the records a d-work is made of (Entity records),
the finite-state machine those records carry (The machine), and the lifecycle by which one d-work completes
a countersigned work session (The lifecycle) — the countersign model's explicit-mode lifecycle
(`dyad/playbooks/countersign-model.md` Part II §4), whose terms are adopted rather than coined (Rule-13
property 1): agent vocabulary rows where a Rule uses them, that play-book's glossary and aliases otherwise (Rule-6): initiation, countersign proposal, countersignature,
countersign report, escalation; mandate, implicit mode, amend. It redefines nothing: every state, form and
store is cited to the Rule that owns it, and on divergence the Rule wins and the test turns red.

## Parameter
`DWORK` — the id of the d-work a step acts on; required by every step that acts on one, with no default (a
step on the wrong d-work is worse than none, `dwork-trace.md`'s own rule). Steps that record words take
them from the environment too, as files holding the operator's text verbatim (Rule-7): `SAID` (a
disposition), `PROMPT` (a prompt); `TITLE` and `REFS` (a new row's); `BLOCKER` (the id a deferral names).
Every step reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3).

## Trigger
Rule-3's own conditions: an operator prompt (a row opens), an operator disposition (a row moves), an
accretion under a mandate (a row is born in implicit mode). The play-book runs inside the d-work and opens
nothing of its own; what opens a row is the first two lines of the machine's table, and it is never the
agent's finding (Rule-3 Scope; countersign I6).

## Entity records
One d-work is made of five records, all under `<instance>/d-work/`, one file per id (the store pattern:
`crafts/sysarch/rules/stores.md`). Each has one guard, which is its parser (`crafts/sysarch/rules/guards.md`
p3); the fields column is that guard's `FIELDS` and nothing else, and the test holds it so. The plan's
prose parts are `dyadlib.PLAN_PARTS` (intent as read, mutation, files touched, base commit, falsification).

| entity | store | guard | fields | written by | when | register kinds (Rule-20) |
|---|---|---|---|---|---|---|
| row | `rows/<id>.md` | `rows` | `id` `title` `opened` `state` `disposed` `refs` + optional `mode` `slug` | `dyad dwork new`, `dyad dwork state`, `dyad dwork retire` | at birth; at every disposition; at every transition | `row.refs->row`, `row.refs->rule`, `row.refs->craft`, `row.disposed->pr` |
| plan | `plans/<id>.md` | `plans` | `id` `title` `base commit` `intent` | the agent, before the plan counter-prompt (Rule-15 phase 1) | once; revised in place on an amend; absent for an accreted row | `plan.id->row`, `plan.base->commit` |
| provenance | `provenance/<id>.md` | `provenance` | `n` `kind` `date` `note` `text` | `dyad dwork new`, `dyad dwork state`, `dyad dwork retire`, with the row, in the same clerical commit | at every prompt received and every disposition given (Rule-7 property 3) | `provenance.id->row`, `provenance.legacy->row` |
| presence | `sessions/<unit>.md` | `sessions` | `session` `seen` `root` `rows` `files` | `dyad session touch`, by the unit alone | at session start and at every plan-Y (Rule-16) | a leaf (`crafts/sysarch/rules/references.md`) |
| trace | `traces/<id>.md` | `traces` | `Timeline` `Buckets` `Counts` `Bottleneck` `Limits` | `dyad dwork trace <id> --out` | at the done-Y, before the Done record commit (`dwork-trace.md`) | `trace.id->row` |

Records a d-work references but does not own, each with its owning Rule: the **incident row**
(`<instance>/audits/INCIDENTS.md`, Rule-3 Incidents; `incident.dwork->row`), the **falsification record**
(`<instance>/falsification/`, Rule-9; `record.ledger->row`), the **change-log row** (`<host-path>/CHANGELOG.md`,
Rule-8; `changelog.dwork->row`), the **PR** (the hosting's, citing `d-work #<id>` through Rule-3's plan gate;
`pr.body->row`), and the **run-book event** (`<runbooks>/events/<name>.jsonl`, Rule-19; `event.command->command`).
The ledger view `LEDGER.md` is rendered, never a record (Rule-16).

## The machine
The states are `dyadlib.STATES` (six, defined in Rule-3 Ledger and the vocabulary), the births
`dyadlib.NEW_STATES` (`open`, `backlog`), the edges `dyadlib.TRANSITIONS` (Rule-16 Store: state never
regresses), and the inputs `dyadlib.INPUTS` — one per edge and per birth, each of a kind in
`dyadlib.INPUT_KINDS`: **prompt** (an operator prompt: a `prompt` entry of the record), **disposition** (an
operator answer to a counter-prompt: an entry in the row's `disposed` and the matching `disposition` entry of
the record, Rule-7 property 5), **clerical** (an agent act a disposition already covers: no entry of its
own, Rule-2). δ(state, input) → state:

| from | to | input | kind | writes | countersign |
|---|---|---|---|---|---|
| — | open | an operator prompt; the `Y` that admits an intake; a mandate's plan-`Y` for an accreted row | prompt · disposition | the row (`open`; `mode: implicit` under a mandate), record entry 1 (`prompt`, or `disposition` noted `mandate #m, <date>`), the presence touch | initiation; or countersignature `yes`, basis `mandate` |
| — | backlog | an operator disposition opening it (`Y backlog`) | disposition | the row, record entry 1 (`disposition`) | countersignature `yes`, basis `per-act` |
| open | planned | the plan-`Y` | disposition | a `disposed` entry, a record entry, the presence touch; the plan file already exists and is now bound (Rule-15) | countersignature `yes`, basis `per-act`; the countersign proposal is the plan file |
| open | blocked | a deferral naming the blocking d-work | disposition | a `disposed` entry, a record entry, `refs` | countersignature |
| open | archived | the bare `N` to the intent question (`N intent`), on a row holding no `Y plan` (#615) | disposition | a `disposed` entry `N intent`, a record entry, the state line, in one commit; the fence admits the edge on nothing else (`rows.intent_close_problems`) | countersignature `no`, basis `per-act`; the countersign proposal is the intent reading |
| open | done | the done-`Y` | disposition | a `disposed` entry naming each PR and the head its `Y` was given on, a record entry, the trace — all in the record commit, the state unchanged; then the merges; then the state, in a second dispositionless commit (#202) | countersignature `yes`; the countersign report (the completion evidence) precedes it |
| planned | open | re-planning: `main` moved past a touched file (Rule-15 phase 2), or the operator's amend of the plan | clerical · disposition | a plan revision in place; an `N` entry when the operator gave one | none, or `amend` |
| planned | blocked | a deferral naming the blocking d-work | disposition | as open → blocked | countersignature |
| planned | done | the done-`Y` | disposition | as open → done | countersignature `yes` |
| blocked | open | the blocking d-work reaching `done` | clerical | the state line only | none |
| backlog | open | an operator prompt for it | prompt | a record `prompt` entry, the state line | initiation |
| backlog | archived | the retirement `Y` over the named set | disposition | a `disposed` entry `Y archive (sweep …)`, a record entry | countersignature `yes` over the set |
| done | archived | the retirement `Y` over the named set | disposition | as backlog → archived | countersignature `yes` over the set |

Twelve edges and two births: exactly `TRANSITIONS` and `NEW_STATES`, which the test holds equal to this
table edge by edge and kind by kind. Inputs that move nothing still write: a bare `N` writes a `disposed`
entry and its record entry and leaves the state; an **amend** (`N` with text, Rule-3 Answer grammar) writes
those and a `prompt` entry, and the plan file is revised in place. A disposition the operator never gave
moves nothing (countersign I8: silence is not consent).

Invariants, each enforced at `dyadlib`'s import and run again by the runner's pass (Rule-12 property 1):
- **inputs cover the machine** — `INPUTS` has one entry per edge of `TRANSITIONS` and per birth, no more;
- **only the operator closes** — every edge into `done` or `archived` is a disposition and nothing else;
  the clerical write that follows the merges executes that disposition, exactly as the merges do (#202)
  (Rule-2: the done-`Y` and the retirement form are ratification events);
- **no self-initiation** — no birth is a clerical act (countersign I6; Rule-3 Scope: a row opens on an
  operator prompt or disposition, never on the agent's finding; an accreted row's input is the mandate's own
  plan-`Y`);
- **`backlog → open` takes a prompt** — the one transition Rule-7's transaction check binds to a `prompt` entry;
- **terminal states stay terminal** — `done` and `archived` exit only to `archived` or nowhere (Rule-16; #37).

## The lifecycle
A d-work **completes a countersigned work session** when it reaches `done`: the countersign model's
explicit-mode lifecycle — initiation → countersign proposal → countersignature → execute → countersign
report + proposal (done) → countersignature — realized as, in order:
1. **Initiation.** An operator prompt; the row is born `open` and the record holds the words (Rule-7). An
   intake (Rule-3) is a signal admitted by the operator's `Y`; a relayed prompt is still the operator's words,
   noted `relayed via <session>`.
1a. **Intent reading** (under the preference `intent-reading: on`; under `off`, the default, this step is skipped and
   2 opens the row's questions, #615). Before any plan is drafted, the reply to a prompt that opens a row, or that
   reopens one from `backlog`, is the intent reading: the prompt's portions, each classed by
   `dyad/dmc/intent-reading.jsonld` against the candidates `dyad dwork intent <id>` prints (rows of any state and
   surface items, ranked, never thresholded) and against the play-books and the Rules. A portion is **new**; an
   **overlap** of a row or capability, a **duplicate** when the overlap is complete, so no row is opened for it;
   a **supersede** of one, the superseded row named for the Done's `retires`; **adjacent** to one, noted for the
   plan; **ambiguous**, both readings stated and one taken; or a **false premise**, assuming what is not true on
   `main`, read against `main` and never against an age. False premise and duplicate are judged first, then
   ambiguous. The reading proposes the definition of done (below, sized by `altitude`) and is stored as the plan
   file's first section; its last line is the **intent question**, `Y/N: intent aligned for #<id> <title>?`.
   `Y` (the **intent-Y**) accepts the reading and the definition of done, and the plan follows; `N` with text
   amends the reading in place; a bare `N` archives the row (`open → archived`), since nothing was built to
   revise from. The board's phase while it is asked is `intent-asked` (Orchestration, below).
2. **Proposal.** The plan file (Rule-15 phase 1; Rule-10's path, counter and reconciliation; the disposition
   budget and the mandate scope of `disposition-digest.md`), opening with its definition of done (below) — the one
   the intent-`Y` accepted under `intent-reading: on`, or one marked proposed under `off` — then the
   plan counter-prompt as the reply's last line. The Rule-16 presence read precedes the file.
3. **Countersignature.** `Y`: `open → planned`, the presence touched. A bare `N`: nothing moves, the agent
   revises. `N` with text: amend — the plan revised in place and asked again.
4. **Execution.** Rule-15 phase 2, in any session: branches and PRs citing `d-work #<id>` through the plan
   gate, `dyad check --pr` before each PR; rows accreted inside the mandate scope (implicit mode) and
   escalated back to explicit where the scope does not cover them (`disposition-digest.md`, the escalate-edge
   test); every departure an incident, a changed plan a fresh plan-`Y`.
5. **Report + proposal.** The completion evidence, opening with the plan's definition of done, quoted, and the
   report that answers it (Rule-3 Completion counter-prompt; then PRs by number and zone,
   checks as observed, the evidence block, host actions, accreted rows, departures, the trace preview) — a
   countersign report, which asks nothing — then the Done question as the last line, naming the accreted rows
   and, under `merge-disposition: with-done`, the held PRs.
6. **Countersignature.** `Y`, in three acts (Rule-3 Completion, #202): `dyad dwork state <id> <the state
   it is in> -d 'Y done (merges PR #a at <head-a>)'`, the trace written, the Done record commit; then
   the merges as clerical execution (the ledger's record of the `Y` — the `disposed` entry and the
   provenance entry — precedes every merge it ratifies); then `dyad dwork state <id> done`, a second
   commit with no disposition, once git shows every head those entries name on `main`. A done-`Y` that
   names no merge is recorded `done` at once. Anything else: the d-work stays as it was. When the automaton is
   on, the record is the last act an inferring unit takes: the automaton runs the merges and the close from
   that ledger line (Layers, below).

Branches. An **accreted row** (implicit mode) skips 2 and 3: born `open` carrying the mandate's plan-`Y`, no
plan file of its own (Rule-15), its Done riding the mandate's done-`Y`, which names it. A **`backlog`** row is
born by a disposition and enters at 1 on a later prompt, or leaves by the retirement form or the Done of a delivered row
that names it under `retires`. A **`blocked`**
row waits on the row its `refs` names and re-enters at 4 when that row is `done`. **`archived`** is the exit
from `done` and `backlog`, by the retirement form or a done-`Y` naming the row under `retires` (Rule-3 Completion
counter-prompt); a retired or done row is never reopened — a new row
refs it.

Layers. The lifecycle is executed in three layers, one per unit kind (Rule-16 Presence; #556 revision 2), and a
step belongs to the layer whose inputs it needs:

| layer | unit kind | what it executes | its inputs |
|---|---|---|---|
| interaction | dyad unit — the home | 1, 3 and 6 as the operator's: reading the intent from the operator's words, presenting the plan's and the Done's questions at the operator's altitude (`relay-form`), transcribing every disposition verbatim (Rule-7) and recording it (`record`, `done-record`) | the operator, live |
| orchestration and execution | solo | 2, 4 and 5: this play-book — drafting the plan, dispatching to units, collecting inbox reports, verifying heads and evidence (`verify-prs`), judging departures and incidents, drafting the completion evidence and the Done question for the home to present | the ledger and the inbox, never a live disposition |
| run-book execution | auto — the automaton | the clerical edges of 6 and the plan notice: merging the PRs a recorded `Y done` names, pinned and in order; `close-landed` once every named head is on `main`; one inbox notice to each board owner of a row whose last disposition is a `Y plan`; a refusal posted once to the home's inbox | ledger lines on `main` only |

The automaton is `dyad automaton scan|run` (`dyad/scripts/automaton.py`), run server-side on every push to
`main` from `main`'s own code by `.github/workflows/dyad-automaton.yml` while the operator's repository variable
`DYAD_AUTOMATON` is `on`, and by hand by any unit for recovery. It is stateless — every run re-reads the ledger
and every act is idempotent — and it decides nothing: it executes a `Y` the ledger already holds, the countersign
model's executor (Rule-2 Enforcement; Rule-3 Completion counter-prompt). Until an orchestrating solo is chartered
(row #557, the operator's `MANDATES.md`), the home executes the orchestration layer as it does today; with the
automaton off, the home or the unit that owns a PR runs the merges and the close by hand, as before.

Overhead test (`dyad/dmc/message-overhead.jsonld`, #560). A message from any layer **reaches the operator** only when
it asks a decision, reports a blocker only the operator can lift, or replaces more messages or decisions than it adds;
every other message — a hold, an acknowledgement, a still-running note — **stays out of the operator's chat** and goes
to the inbox, the automaton or the orchestrating solo. A mechanism that sends the operator messages is kept only if it
passes the same test.

Tunables (#590). Every threshold this play-book names is an operator preference whose default its decision criterion
holds (`dyad/dmc/schema.md`, `dyad:tunables`; the table, `agent-corpus/audits/2026-11-04-tunables.md`): the operator
tunes it by a preferences-zone PR, never by a code change, and the code reads it through `dyadlib.tunable`. The
families are hygiene (`hygiene-stale-days`, `hygiene-similar`, `hygiene-top`), work in flight (`inflight-*`), the
stall findings over time (`sweep-*`, keys named for the sweep that posted them until #617) and promotion (`promotion-ceiling`, `promotion-adjacency-min`).

Backlog hygiene (#565). The home's read, `dyad board resume` (Rule-3 Ledger, at session start and at each operator
prompt; #617), reads the `backlog` rows on `main` and finds only what is structural: a row untouched — no commit to its row, plan or provenance record —
for `hygiene-stale-days` days; a title that is empty or shaped like a flag; a child whose `refs: parent #N` names a
terminal row; a row a commit on any `origin` branch claims as `d-work #N` while it is still `backlog`. Beside those
it ranks pairs by similarity — TF-IDF cosine over the rows, siblings of one parent skipped, tokens common to more
than a fifth of the rows dropped — at or above `hygiene-similar`, the top `hygiene-top` pairs. A ranked pair is a candidate for the review, never
a finding. Hygiene is no guard: the runner never discovers it, and neither CI, the pre-push gate, `check --evidence`
nor `check --corroborate` runs it, and no sweep posts it (#617): the home reads it where it reads the board.

On that reading the home judges what no automaton can (the overhead test above: only a question reaches the operator):
- **The candidates.** Whether a ranked pair is the same work twice, whether a row is superseded by work since
  landed, whether its reason is gone, or whether it is still owed; a structural finding is a reason to read the
  row, never a verdict on it. An orphaned, untouched or malformed row is not thereby obsolete: a parent may close
  over a `backlog` child it never delivered (Rule-3 Ledger), so retirement takes one of the grounds of
  `dyad/dmc/retirement-candidate.jsonld`, and an orphan still owed is a promotion candidate like any other (#568).
- **The triggers.** A row whose plan or title waits on a named event is read against that event's state; one
  whose event has come is proposed for opening by the operator's prompt, never opened by the home.
- **A row worked under `backlog`.** Reported to the operator as an incident (Rule-3): work was claimed with no
  plan-`Y`, which the plan gate refuses at the push, so a commit on `origin` that claims it went around the hook.
- **The question.** The rows the home proposes to retire are asked in the retirement form, `Y/N: archive #a, #b,
  … #k?`, each listed before it with what it holds and the reason for retiring it (Rule-3 Ledger). A `Y` is
  executed by `dyad dwork retire <id>... -d '<entry>' --said '<the operator's words>'`, which writes the entry, the
  provenance record and `archived` in the one ledger commit: an archive has no merge between its record and its
  act, so it takes one commit where a Done takes two. Anything else retires none of them.

Work in flight (#569). The same read reads the work in flight from records alone — inbox files and their `.read`
markers, commits and branch tips, PR bodies and heads, the board, presence and the stored plans — and prints it, one
line per finding, each kind under its own heading (#617). Each threshold is a minimum age, the home reading at every
operator prompt; the ages below are the defaults of the `inflight-*` preference keys. On that reading the home acts per kind, and decides nothing an owner or the operator owns:
- **A relay or notice left unread** (4 h): the home rings the unit's doorbell, the one act that wakes a session; a
  reminder in the same unread inbox would go unread too, so it surfaces in the home's read alone.
- **A planned row gone quiet** (3 days, only while its board entry waits on a unit), **an open row with no plan file**
  (24 h; a child or a row under a mandate has none of its own and is exempt), or **a PR whose head has not moved**
  (3 days): the home asks the owner by relay what holds it.
- **A PR citing no live row**, or **a branch** whose tip is not on `main`, with no open PR and no row citing it: the
  home proposes a close or a delete. Deleting a branch is destructive, so each deletion is its own question to the
  operator (Rule-8), never folded into another.
- **A board unit missing from the unit table**, or a row waiting on a unit whose presence is stale (read only once #567's refreshed presence is on `main`, and skipped with one line until then): the home fixes
  the board (write-ahead, Rule-3).
- **A promise still listed** (3 days): the home opens its row, by the operator's `Y`, or drops the promise. A promise
  is written to `promised` in the turn it is made and removed in the turn its row opens or it is dropped, so a listed
  promise is one still owed; its age is read from the history of `_cos.md`.
- **A row waiting on the operator with no question recorded**, reported once and again only if it changes, or **a
  recorded question older than 24 h**: the home asks it, or records the question it is waiting on.
- **A drafted Done not asked** (4 h): a phased board entry in `done-ready`, its Done question drafted and not yet
  asked; the home asks the Done question or names what holds it (#587 S9: a drafted Done was held 13 h). Every other
  phase keeps W11's fixed age, an asked phase 24 h and every other 3 days.
- **A report newer than the board**: the owner posted a report on the row after the board entry's `since`, so the
  board may be stale; the home reads the report and fixes the board.
What cannot be read from records — a unit's chat state, a hold said only in conversation — stays the home's
inference. Clustering the backlog by `refs` waits for typed refs (#569 A12).

Definition of done (#574). A row is partitioned by what the operator will judge it by, never by the shape of the work:
one **definition of done** (DoD) the operator can evaluate is one row, its plan-`Y` and done-`Y` covering the largest
scope that DoD lets the operator judge (#570 revision 4). Before proposing one, the agent checks the row is still owed: a
trigger already come, nothing left to show, or a premise overtaken is a retirement candidate, not a DoD
(`dyad/dmc/retirement-candidate.jsonld`). It takes the operator's DoD, when the operator gave one, from the provenance
record: the row's own record first, then the record of the row its first `disposed` entry or its refs name, since a row
opened by a bare `Y` holds no words of its own. It quotes the words only where they may be published — a tracked file
is public to whoever reads the repository — and otherwise cites the entry without quoting it. With no words found, it
proposes one, marked *proposed*, drawn from the prompt, the row's refs (free text, read as such) and what the operator
has judged before. The plan opens with it
(Rule-15 phase 1); the plan-`Y` accepts it and `N` with text amends it (Rule-3 Answer grammar), so a DoD costs no
question of its own. Work one DoD covers is one row, its parts carried as accreted children verified through that
DoD's report; existing `backlog` rows one new DoD covers cannot become its children (an accreted row is born `open`,
Rule-3 Scope), so the new row is opened for the DoD and its Done question names them under `retires`, the done-`Y`
archiving them (Rule-3 Completion counter-prompt); work whose parts the operator would judge separately is split into rows, one per DoD; an unfamiliar
domain draws finer DoDs and so smaller rows, and nothing else models the operator's familiarity. For many rows at
once — a backlog being re-partitioned — the home proposes every DoD in one document, the operator amends only those
it would define differently, and the counts are kept: rows in, DoDs out, absorbed into an existing row, merged into a new row, split,
already delivered or no longer owed (each retired by the Done that covers it, or by the retirement form where no Done
does), and DoDs amended, the measure of how well the proposals fit. The completion evidence opens with the DoD, quoted, and the report that answers
it (Rule-3 Completion counter-prompt); the rest of the evidence follows. A play-book the plan runs carries the rows its
own steps prescribe — the incident-hardening play-book's `backlog` row naming a fence — under that plan-`Y`, never
asked again (Rule-3 Plan, the mandate scope; Ledger, the carried `backlog` row); each is listed in the completion
evidence like any accreted row.

Blocker home (#623; `dyad/dmc/blocker-home.jsonld`, beside `altitude`). A fault that stops a row's next act from
outside the row's own diff is fixed in the cheapest home that still shows the operator what its judgment could change.
The **blocked row** is the row whose next act the fault stops; a fault that only turns `main`'s own checks red has as
its blocked row the open row whose work found it, and one no row's work found has none and is the home's promotion
candidate. A fix is a **restore** when, after it, every Rule, record, check and test decides what its stated text
already says: no stated text changes, and no check leaves the evidence block or the pre-push gate; anything else is a
**change**, and a fix that cannot be told apart reads as one. In precedence order: an act Rule-2 never lets a `Y`
carry is **its own question**, under the Rule that owns it; a cause in the blocked row's diff is **the row's own**, and
`plan-departure` says whether that is a new plan; a fix already on `main` is **port the fix**, an execution detail;
a fix another open row's plan describes or its PR holds is **ride another open row**, the two Dones asked in one batch
and the blocked row's PR merged after, never by revising that row; a fix that adds what the system did not have, or
that no row can carry or revise, is **its own row**, proposed and ordered first; a restore under a plan that states the
class with its ceiling unspent is **a carried row**, born `open` under that plan-`Y` with its own plan file unasked;
and every other fix is **a revision** of the blocked row's plan, one question — the default. A carried row's Done rides
the blocked row's done-`Y` when it stops that row alone or only `main`'s own checks; joins the first Done question its
landing holds when it stops another row too; and is asked alone and lands first when it stops every code push or
every evidence run on `main`. Recurrence, zone and the unit that builds it move no outcome: the incident row names the
recurrence, another zone is another PR, and a unit within its charter is execution detail. This step prescribes one
class of row (Rule-3 Plan, the mandate scope); a plan carries it only by stating it, in one line, other carried rows
added to the same line with the total last:

    Mandate scope: the d-work play-book's blocker-fix row (a restore that stops this row from outside its diff); ceiling 1.

What the home writes, and what it leaves to the records (#572). An act whose content a recorded line already decides
is the automaton's or the code's, never an inferring unit's (the inventory: `agent-corpus/audits/2026-11-04-inference-map.md`).
A plan that splits its work among units names each unit's part on one line, `parts: <unit>: <part>; <unit>: <part>`,
by unit name or by its function alone (the name before its `-<hp>`); on the plan-`Y` the automaton's plan notice then
quotes each owner's own part and flips that row's board to wait on its owner, so the home sends no relay that
restates the plan, and relays only what the plan does not say — a sequencing, a review asked, the operator's further
words. A report is its own record: the home writes the board only when a row's next act or owner changes, never to
re-word a report the inbox already holds (the work-in-flight sweep, above, reads a report newer than the board), and
a unit posts one report to every box that needs it at once (`inbox post --cc`). Three acts stay the home's, because
no record decides them: the doorbell that wakes a unit, since only a session can ring one; recording a disposition,
since only the party that received the operator's words can enter them (Rule-7 property 4) — the reply that receives
a `Y` records it, and that is the reply the release counts; and drafting the questions the operator answers.

Promotion when the board is empty (#566; `dyad/dmc/promotion.jsonld`). When a unit is **idle** — no row that is not
terminal waits on it — or **about to be** — its one waiting row's `next` is a Done draft or a review — and nothing is
**owed** — no counter-prompt the home asked is unanswered (a row routed home with a board `question`, or a pending queue
that is not empty; work waiting in a paired unit's own chat does not count) — the home reads the `backlog` rows and
proposes which to open. An empty board is the case where every unit is idle. Otherwise the answer is **no proposal**.
A candidate's class, highest first:
- P1, **a live defect**: a defect in a live mechanism, or a monitoring gap;
- P2, **a promise**: a `promised` entry of the board made while working an anchor, matched to the row by the home;
- P3, **a fired trigger**: a row waiting on a named event that has come;
- P4, **adjacent to the last delivered row** (below);
- P5, **worked under backlog**: the sweep's finding of a `backlog` row a commit already claims (Backlog hygiene, above)
  — its other findings are reasons to read a row, never grounds to retire it or to promote it;
- P6, **the oldest valid row**: the oldest `backlog` row whose reason still holds.

A candidate need not be a row: a promise or a finding is named by its source (`promise on #N`, `I12 on #N`, `finding`)
and a one-line title. A row that is none of these, that duplicates another row, or that another row's plan names as
carried by it (**absorbed**) is **not a candidate**: a duplicate is replaced by the row it duplicates, and an absorbed
row is proposed only through the row that absorbed it, with the reason stated (#568). **Adjacency**, of a candidate to an anchor (a row on the board, or the row just
delivered): either strong signal alone — S1, the anchor's plan or completion evidence deferred the candidate or named
it as not built or a follow-up; S2, it was promised while working the anchor — or a score of 3 or more from S3 shared
files (2), counting only files that under a fifth of the stored plans touch, so a file most plans touch adds nothing;
S4 a shared mechanism — a verb, a guard or a store (2); S5 a `refs` edge (1); S6 the same owning unit, read from the
charter that covers the candidate's files, and counted only when the anchor's board `owner` names exactly one unit (1); S7 the same incident mode, read from the failure-mode derivation (1).
S1 and S5 are read from records; S2, S3, S4, S6 and S7 are inferred, and the reason is written beside the candidate.
Within a class, a candidate the **release plan** places in the next release comes first — the `release-plan` line of
`_cos`, written by the backlog-grooming play-book (`dyad/playbooks/backlog-groom.md`, `dyad/dmc/release-plan.jsonld`,
#625); then a candidate another depends on — whose fix the other's assumes, or which the other's refs or plan
name as a prerequisite; within P1, impact comes next: a defect that blocks or corrupts work, before one
that misleads a reading, before a cosmetic one; dependency and impact are inferred and carry their reason (#568).
Ties then go to an idle unit before a new one (#559), then one writer per file, then the smaller plan. The ceiling is the
smaller of `promotion-ceiling` (default 2) and the number of idle units, each candidate with a different owner: a promoted row costs the operator
three answers. The home judges every class; the sweep supplies only P5. The question is one line naming each candidate,
its class, its reason and its owner — `Y/N: open #a (P1, <reason>, <owner>), #b (P4, <reason>, <owner>)?` — and a `Y`
opens each named row (`backlog → open`, the operator's words its `prompt` entry, Rule-7) and, for each named promise
or finding, one new row born `open` with the operator's words as its first entry, the plan of each following; nothing
opens without it, and the overhead test above applies. Under `organization: flat` there is one unit, so S6 and the
unit tie-breaks drop out. Adjacency moves to its own `dyad/dmc/adjacency.jsonld` when a second decision needs it.

### Orchestration (#587)
Between a row's plan-`Y` and its Done the row machine stays still; what moves is its board entry's **orchestration
phase** (Rule-16 Store), a second machine beside the row's that never moves the row. Its table is data,
`dyadlib.ORCH_EVENTS`; `dyad board phases` prints it, with each phase's wait and next act.

| phase | waiting on | the act that moves it (event, actor) |
|---|---|---|
| `planning` | the unit | `plan-landed` (unit) → `plan-ready`; under `intent-reading: on`, `asked` (home) → `intent-asked` once the intent reading, the plan file's first section, is on `main` (#615) |
| `intent-asked` | the operator | `answered-Y` → `planning`; `answered-N` → `planning` with words (amend), or the entry dropped and the row archived on a bare `N` (home, with `--said-file`; #615) |
| `plan-ready` | the home | `asked` (home) → `plan-asked` |
| `plan-asked` | the operator | `answered-Y` → `building`; `answered-N` → `planning` (home, with `--said-file`) |
| `building` | the unit | `pr-up` (unit, `pr`, `head`) → `verifying`; `evidence-verified` (home, no PR) → `done-ready` |
| `verifying` | the home | `evidence-verified` (home or automaton, `evidence`) → `done-ready`; `evidence-failed` → `building` |
| `done-ready` | the home | `asked` (home) → `done-asked`; `board draft` prints the data half of the evidence |
| `done-asked` | the operator | `answered-Y` → `landing`, or the entry dropped when nothing merges; `answered-N` → `building` |
| `landing` | the automaton | `closed` (automaton) drops the entry once the merges have landed |
| `held` | what `on` names | `release` (home) → the phase it was held from, an asked phase stepping back to its `*-ready` |

Any phase but `landing` and `held` may be `hold`-ed with a `note` and an `on`. In `verifying`, `done-ready` and
`done-asked` the automaton compares each recorded PR head with the live one; a moved head fires `head-moved`, back to
`verifying`, and takes down any question asked on the old head (Rule-2, Binding: a `Y` binds only while the heads are
unchanged), a batch question's other rows stepping back to `done-ready` (`withdrawn`).

How a unit works it:
- **Fire, don't write.** On a phased entry, `phase`, `waiting-on`, `next`, `since` and `question` are derived; the one
  writer is `dyad board advance <id>… <event> --expect <phase> [key=value…]`. `--expect` names the phase read; a moved
  phase is refused, and the retry re-reads `main` and recomputes, never replaying a relay. Free text goes in `note`.
- **One commit per transition.** An advance writes the board, the templated relay to the next unit, and for an answer
  the ledger entry and its provenance from `--said-file`, all in one ledger-only commit; it prints the ring list, the
  doorbells only a session can ring (#586).
- **The question is composed, not typed.** `asked` stores the question line from the row's title, PRs and heads, a batch
  question from several rows; `answered-Y` writes the `Y plan` or `Y done` entry from the stored question, so the entry
  names what was asked.
- **The Done draft.** At `done-ready`, `dyad board draft <id>` prints the definition of done quoted, the PRs with their
  zones and recorded heads, the evidence by its sha256, the accreted rows, the trace and the question; the unit writes
  the judgment around it (Rule-3, Completion counter-prompt).
- **Unphased entries.** An entry with no `phase` behaves as before #587 (`board set`); the first `plan-landed` or `pr-up`
  adopts it into the machine.

## Reading
- **The machine before the forms.** What a row may do next is its state's rows of δ: the input named there
  is the only thing that moves it, and the kind says whose act it is.
- **The record before the row.** `disposed` holds the chain; the provenance record holds the words. Where
  the counts differ the push is refused (Rule-7 property 5), so a row read alone is read with its record.
- **Two countersignatures is the design.** A d-work that cost more than two dispositions is read against its
  plan's budget (`disposition-digest.md`), never against the operator's right to answer `N`.
- **A terminal state is terminal.** Nothing reopens `done` or `archived`; the next step is a new row.

## Evidence
The completion reply (Rule-3) of a d-work cites, for its own row: the transitions it took in order with the
input of each (read from `disposed` and the record), the records it wrote (the row, the plan with its
revisions, the record's entry count, the trace), and every accreted row with its mode. A step run through
the runner names its event id; the native command is the default and needs no statement.

## Conduct
Units run the run-book's steps by name, with their parameters (`DWORK`, `PRS`, `SAID`, …), and never re-author
them: a hand-written script that repeats a step is the recurring task Rule-13 property 1 turns into code, and a
new recurring script becomes a run-book step through its own row, never inline in another d-work (#556
revision 3).

The play-book decides and records; it never disposes (frame: detect, don't dispose; Rule-2 — the agent
proposes). It never moves a row on an input the table does not name, never writes a disposition the operator
did not give, and never reopens a terminal row. What it cannot do is make a transition the fence refuses
legal: `rows.py` judges the state line on `main`, and this play-book is read, never enforced, except where
its tables are pinned to the code that is.
