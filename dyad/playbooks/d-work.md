# Play-book: d-work (core craft, `dyad-operator`; #299)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision; its steps are a run-book. This one decides, at every state change of a d-work, **which
transition is legal now, what input it takes and from whom, and which record the move writes** — the
decision Rule-3, Rule-7, Rule-15 and Rule-16 each own one part of, and that the Agent made by inference
against the CLI help at every row write (Rule-13 property 1: the recurrence proposes code — the machine's
input alphabet is `dyadlib.INPUTS`, and this play-book's two tables are pinned to it and to the guards by
`dyad/tests/test_playbooks.py`). Read by Rule-3's Ledger clause. Steps: `dyad/runbooks/d-work.md` —
`open`, `plan`, `authorize`, `execute`, `evidence`, `complete`, `defer`, `resume` — run through
`DWORK=<id> dyad runbook run d-work <step>`, the core runner, so each step leaves an event. The native
commands stay the default for a ledger commit, for the reason `dwork-trace.md` records (#247: a runner
event is a workstation-zone file the ledger commit cannot carry).

It states the **architecture of the d-work framework**: the records a d-work is made of (Entity records),
the finite-state machine those records carry (The machine), and the lifecycle by which one d-work completes
a countersigned work session (The lifecycle) — the countersign craft's explicit-mode lifecycle
(`crafts/countersign/rules/interaction.md` §4), whose terms are adopted rather than coined (Rule-13
property 1) and named by craft name (Rule-6): initiation, countersign proposal, countersignature,
countersign report, escalation; mandate, implicit mode, amend. It redefines nothing: every state, form and
store is cited to the Rule that owns it, and on divergence the Rule wins and the test turns red.

## Parameter
`DWORK` — the id of the d-work a step acts on; required by every step that acts on one, with no default (a
step on the wrong d-work is worse than none, `dwork-trace.md`'s own rule). Steps that record words take
them from the environment too, as files holding the Operator's text verbatim (Rule-7): `SAID` (a
disposition), `PROMPT` (a prompt); `TITLE` and `REFS` (a new row's); `BLOCKER` (the id a deferral names).
Every step reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3).

## Trigger
Rule-3's own conditions: an Operator prompt (a row opens), an Operator disposition (a row moves), an
accretion under a mandate (a row is born in implicit mode). The play-book runs inside the d-work and opens
nothing of its own; what opens a row is the first two lines of the machine's table, and it is never the
Agent's finding (Rule-3 Scope; countersign I6).

## Entity records
One d-work is made of five records, all under `<instance>/d-work/`, one file per id (the store pattern:
`crafts/sysarch/rules/stores.md`). Each has one guard, which is its parser (`crafts/sysarch/rules/guards.md`
p3); the fields column is that guard's `FIELDS` and nothing else, and the test holds it so. The plan's
prose parts are `dyadlib.PLAN_PARTS` (intent as read, mutation, files touched, base commit, falsification).

| entity | store | guard | fields | written by | when | register kinds (Rule-20) |
|---|---|---|---|---|---|---|
| row | `rows/<id>.md` | `rows` | `id` `title` `opened` `state` `disposed` `refs` + optional `mode` | `dyad dwork new`, `dyad dwork state`, `dyad dwork retire` | at birth; at every disposition; at every transition | `row.refs->row`, `row.refs->rule`, `row.refs->craft`, `row.disposed->pr` |
| plan | `plans/<id>.md` | `plans` | `id` `title` `base commit` `intent` | the Agent, before the plan counter-prompt (Rule-15 phase 1) | once; revised in place on an amend; absent for an accreted row | `plan.id->row`, `plan.base->commit` |
| provenance | `provenance/<id>.md` | `provenance` | `n` `kind` `date` `note` `text` | `dyad dwork new`, `dyad dwork state`, `dyad dwork retire`, with the row, in the same clerical commit | at every prompt received and every disposition given (Rule-7 property 3) | `provenance.id->row`, `provenance.legacy->row` |
| presence | `sessions/<seat>.md` | `sessions` | `session` `seen` `root` `rows` `files` | `dyad session touch`, by the seat alone | at session start and at every plan-Y (Rule-16) | a leaf (`crafts/sysarch/rules/references.md`) |
| trace | `traces/<id>.md` | `traces` | `Timeline` `Buckets` `Counts` `Bottleneck` `Limits` | `dyad dwork trace <id> --out` | at the Done-Y, before the Done ledger commit (`dwork-trace.md`) | `trace.id->row` |

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
`dyadlib.INPUT_KINDS`: **prompt** (an Operator prompt: a `prompt` entry of the record), **disposition** (an
Operator answer to a counter-prompt: an entry in the row's `disposed` and the matching `disposition` entry of
the record, Rule-7 property 5), **clerical** (an Agent act a disposition already covers: no entry of its
own, Rule-2). δ(state, input) → state:

| from | to | input | kind | writes | countersign |
|---|---|---|---|---|---|
| — | open | an Operator prompt; the `Y` that admits an intake; a mandate's plan-`Y` for an accreted row | prompt · disposition | the row (`open`; `mode: implicit` under a mandate), record entry 1 (`prompt`, or `disposition` noted `mandate #m, <date>`), the presence touch | initiation; or countersignature `yes`, basis `mandate` |
| — | backlog | an Operator disposition opening it (`Y backlog`) | disposition | the row, record entry 1 (`disposition`) | countersignature `yes`, basis `per-act` |
| open | planned | the plan-`Y` | disposition | a `disposed` entry, a record entry, the presence touch; the plan file already exists and is now bound (Rule-15) | countersignature `yes`, basis `per-act`; the countersign proposal is the plan file |
| open | blocked | a deferral naming the blocking d-work | disposition | a `disposed` entry, a record entry, `refs` | countersignature |
| open | done | the Done-`Y` | disposition | a `disposed` entry, a record entry, the trace; then the merges it ratifies | countersignature `yes`; the countersign report (the completion evidence) precedes it |
| planned | open | re-planning: `main` moved past a touched file (Rule-15 phase 2), or the Operator's amend of the plan | clerical · disposition | a plan revision in place; an `N` entry when the Operator gave one | none, or `amend` |
| planned | blocked | a deferral naming the blocking d-work | disposition | as open → blocked | countersignature |
| planned | done | the Done-`Y` | disposition | as open → done | countersignature `yes` |
| blocked | open | the blocking d-work reaching `done` | clerical | the state line only | none |
| backlog | open | an Operator prompt for it | prompt | a record `prompt` entry, the state line | initiation |
| backlog | archived | the retirement `Y` over the named set | disposition | a `disposed` entry `Y archive (sweep …)`, a record entry | countersignature `yes` over the set |
| done | archived | the retirement `Y` over the named set | disposition | as backlog → archived | countersignature `yes` over the set |

Twelve edges and two births: exactly `TRANSITIONS` and `NEW_STATES`, which the test holds equal to this
table edge by edge and kind by kind. Inputs that move nothing still write: a bare `N` writes a `disposed`
entry and its record entry and leaves the state; an **amend** (`N` with text, Rule-3 Answer grammar) writes
those and a `prompt` entry, and the plan file is revised in place. A disposition the Operator never gave
moves nothing (countersign I8: silence is not consent).

Invariants, each enforced at `dyadlib`'s import and run again by the runner's pass (Rule-12 property 1):
- **inputs cover the machine** — `INPUTS` has one entry per edge of `TRANSITIONS` and per birth, no more;
- **only the Operator closes** — every edge into `done` or `archived` is a disposition and nothing else
  (Rule-2: the Done-`Y` and the retirement form are ratification events);
- **no self-initiation** — no birth is a clerical act (countersign I6; Rule-3 Scope: a row opens on an
  Operator prompt or disposition, never on the Agent's finding; an accreted row's input is the mandate's own
  plan-`Y`);
- **`backlog → open` takes a prompt** — the one transition Rule-7's transaction check binds to a `prompt` entry;
- **terminal states stay terminal** — `done` and `archived` exit only to `archived` or nowhere (Rule-16; #37).

## The lifecycle
A d-work **completes a countersigned work session** when it reaches `done`: the countersign craft's
explicit-mode lifecycle — initiation → countersign proposal → countersignature → execute → countersign
report + proposal (done) → countersignature — realized as, in order:
1. **Initiation.** An Operator prompt; the row is born `open` and the record holds the words (Rule-7). An
   intake (Rule-3) is a signal admitted by the Operator's `Y`; a relayed prompt is still the Operator's words,
   noted `relayed via <session>`.
2. **Proposal.** The plan file (Rule-15 phase 1; Rule-10's path, counter and reconciliation; the disposition
   budget and the mandate scope of `disposition-digest.md`), then the plan counter-prompt as the reply's last
   line. The Rule-16 presence read precedes the file.
3. **Countersignature.** `Y`: `open → planned`, the presence touched. A bare `N`: nothing moves, the Agent
   revises. `N` with text: amend — the plan revised in place and asked again.
4. **Execution.** Rule-15 phase 2, in any session: branches and PRs citing `d-work #<id>` through the plan
   gate, `dyad check --pr` before each PR; rows accreted inside the mandate scope (implicit mode) and
   escalated back to explicit where the scope does not cover them (`disposition-digest.md`, the escalate-edge
   test); every departure an incident, a changed plan a fresh plan-`Y`.
5. **Report + proposal.** The completion evidence (Rule-3 Completion counter-prompt: PRs by number and zone,
   checks as observed, the evidence block, host actions, accreted rows, departures, the trace preview) — a
   countersign report, which asks nothing — then the Done question as the last line, naming the accreted rows
   and, under `merge-disposition: with-done`, the held PRs.
6. **Countersignature.** `Y`: `dyad dwork state <id> done`, the trace written, the Done ledger commit, then
   the merges as clerical execution (the ledger's record of the `Y` precedes every merge it ratifies).
   Anything else: the d-work stays as it was.

Branches. An **accreted row** (implicit mode) skips 2 and 3: born `open` carrying the mandate's plan-`Y`, no
plan file of its own (Rule-15), its Done riding the mandate's Done-`Y`, which names it. A **`backlog`** row is
born by a disposition and enters at 1 on a later prompt, or leaves by the retirement form. A **`blocked`**
row waits on the row its `refs` names and re-enters at 4 when that row is `done`. **`archived`** is the exit
from `done` and `backlog`, by the retirement form only; a retired or done row is never reopened — a new row
refs it.

## Reading
- **The machine before the forms.** What a row may do next is its state's rows of δ: the input named there
  is the only thing that moves it, and the kind says whose act it is.
- **The record before the row.** `disposed` holds the chain; the provenance record holds the words. Where
  the counts differ the push is refused (Rule-7 property 5), so a row read alone is read with its record.
- **Two countersignatures is the design.** A d-work that cost more than two dispositions is read against its
  plan's budget (`disposition-digest.md`), never against the Operator's right to answer `N`.
- **A terminal state is terminal.** Nothing reopens `done` or `archived`; the next step is a new row.

## Evidence
The completion reply (Rule-3) of a d-work cites, for its own row: the transitions it took in order with the
input of each (read from `disposed` and the record), the records it wrote (the row, the plan with its
revisions, the record's entry count, the trace), and every accreted row with its mode. A step run through
the runner names its event id; the native command is the default and needs no statement.

## Conduct
The play-book decides and records; it never disposes (frame: detect, don't dispose; Rule-2 — the Agent
proposes). It never moves a row on an input the table does not name, never writes a disposition the Operator
did not give, and never reopens a terminal row. What it cannot do is make a transition the fence refuses
legal: `rows.py` judges the state line on `main`, and this play-book is read, never enforced, except where
its tables are pinned to the code that is.
