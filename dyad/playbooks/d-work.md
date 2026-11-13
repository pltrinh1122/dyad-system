# Play-book: d-work (core craft, `dyad-operator`; #309, #626)

Which transition of a d-work is legal now, what input it takes and from whom, and which record the move writes. Read
by Rule-3's Boundaries; every state, form and store is the Rule's that owns it, and on divergence the Rule wins. Its
steps are `dyad/runbooks/d-work.md` — `open`, `plan`, `authorize`, `execute`, `verify-prs`, `evidence`, `record`,
`done-record`, `complete`, `close-landed`, `defer`, `resume`, `sync-mirror` — run as `DWORK=<id> dyad runbook run d-work
<step>`, or by their native commands, the default for a ledger commit (#247). The terms are the countersign model's
(`dyad/playbooks/countersign-model.md` Part II §4).

## Parameter
`DWORK`, the row a step acts on, required, no default. Words come as files holding the operator's text verbatim
(Rule-7): `SAID`, `PROMPT`; a new row's `TITLE`, `REFS`, `SLUG`; a deferral's `BLOCKER`. The instance is
`${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3).

## Trigger
Rule-3's conditions: an operator prompt or disposition, or an accretion under a mandate. The play-book opens nothing
of its own; a row opens only on the machine's first two lines, never on the agent's finding (Rule-3 Scope).

## Entity records
Five records under `<instance>/d-work/`, one file per id; each guard is its parser, and the fields column is that
guard's `FIELDS` (pinned by `dyad/tests/test_playbooks.py`). The plan's parts are `dyadlib.PLAN_PARTS`.

| entity | store | guard | fields | written by | when | register kinds (Rule-20) |
|---|---|---|---|---|---|---|
| row | `rows/<id>.md` | `rows` | `id` `title` `opened` `state` `disposed` `refs` + optional `mode` `slug` | `dyad dwork new`, `dyad dwork state`, `dyad dwork retire` | at birth; at every disposition; at every transition | `row.refs->row`, `row.refs->rule`, `row.refs->craft`, `row.disposed->pr` |
| plan | `plans/<id>.md` | `plans` | `id` `title` `base commit` `intent` | the agent, before the plan counter-prompt (Rule-15 phase 1) | once; revised in place on an amend; absent for an accreted row | `plan.id->row`, `plan.base->commit` |
| provenance | `provenance/<id>.md` | `provenance` | `n` `kind` `date` `note` `text` | `dyad dwork new`, `dyad dwork state`, `dyad dwork retire`, with the row, in the same clerical commit | at every prompt received and every disposition given (Rule-7 property 3) | `provenance.id->row`, `provenance.legacy->row` |
| presence | `sessions/<unit>.md` | `sessions` | `session` `seen` `root` `rows` `files` | `dyad session touch`, by the unit alone | at session start and at every plan-Y (Rule-16) | a leaf (`crafts/sysarch/rules/references.md`) |
| trace | `traces/<id>.md` | `traces` | `Timeline` `Buckets` `Counts` `Bottleneck` `Limits` | `dyad dwork trace <id> --out` | at the done-Y, before the Done record commit (`dwork-trace.md`) | `trace.id->row` |

Referenced, not owned: the incident row (Rule-3), the falsification record (Rule-9), the change-log row (Rule-8), the
PR (the plan gate) and the run-book event (Rule-19). `LEDGER.md` is a rendered view (Rule-16).

## The machine
States `dyadlib.STATES`, births `dyadlib.NEW_STATES`, edges `dyadlib.TRANSITIONS`, inputs `dyadlib.INPUTS`, each of a
kind in `dyadlib.INPUT_KINDS` (`dmc:dwork-input-kind`). δ(state, input) → state, pinned to `INPUTS` edge by edge:

| from | to | input | kind | writes | countersign |
|---|---|---|---|---|---|
| — | open | an operator prompt; the `Y` that admits an intake; a mandate's plan-`Y` for an accreted row | prompt · disposition | the row (`open`; `mode: implicit` under a mandate), record entry 1 (`prompt`, or `disposition` noted `mandate #m, <date>`), the presence touch | initiation; or countersignature `yes`, basis `mandate` |
| — | backlog | an operator disposition opening it (`Y backlog`) | disposition | the row, record entry 1 (`disposition`) | countersignature `yes`, basis `per-act` |
| open | planned | the plan-`Y` | disposition | a `disposed` entry, a record entry, the presence touch; the plan file already exists and is now bound (Rule-15) | countersignature `yes`, basis `per-act`; the countersign proposal is the plan file |
| open | blocked | a deferral naming the blocking d-work | disposition | a `disposed` entry, a record entry, `refs` | countersignature |
| open | archived | the bare `N` to the intent question (`N intent`), on a row holding no `Y plan` (#615); or the retirement `Y` naming the stale row (#697) | disposition | a `disposed` entry `N intent`, or `Y archive (sweep …)` naming the row, a record entry, the state line, in one commit; the fence admits the edge on nothing else (`rows.intent_close_problems`) | countersignature `no`, basis `per-act`, the countersign proposal the intent reading; or countersignature `yes` over the set |
| open | done | the done-`Y` | disposition | a `disposed` entry naming each PR and the head its `Y` was given on, a record entry, the trace — all in the record commit, the state unchanged; then the merges; then the state, in a second dispositionless commit (#202) | countersignature `yes`; the countersign report (the completion evidence) precedes it |
| planned | open | re-planning: `main` moved past a touched file (Rule-15 phase 2), or the operator's amend of the plan | clerical · disposition | a plan revision in place; an `N` entry when the operator gave one | none, or `amend` |
| planned | blocked | a deferral naming the blocking d-work | disposition | as open → blocked | countersignature |
| planned | archived | the retirement `Y` naming the stale row (#697) | disposition | a `disposed` entry `Y archive (sweep …)` naming the row, a record entry, the state line; refused while its board entry records an unlanded PR | countersignature `yes` over the set |
| planned | done | the done-`Y` | disposition | as open → done | countersignature `yes` |
| blocked | open | the blocking d-work reaching `done` | clerical | the state line only | none |
| backlog | open | an operator prompt for it | prompt | a record `prompt` entry, the state line | initiation |
| backlog | archived | the retirement `Y` over the named set | disposition | a `disposed` entry `Y archive (sweep …)`, a record entry | countersignature `yes` over the set |
| done | archived | the retirement `Y` over the named set | disposition | as backlog → archived | countersignature `yes` over the set |

A bare `N` writes a `disposed` entry and its record entry and moves nothing; an amend adds a `prompt` entry and the
plan is revised in place; silence moves nothing. The machine's invariants are `dyadlib`'s, enforced at import (Rule-12
property 1).

## Steps
1. **Open** — `open`: the row is born `open` on the prompt, entry 1 the words (Rule-7). An intake opens by the
   operator's `Y`; a relayed prompt is noted `relayed via <session>`.
2. **Intent** (under `intent-reading: on`) — classify each portion of the prompt by `dmc:intent-reading` against
   `dyad dwork intent <id>`, size it by `dmc:altitude` (one row per definition of done the operator can evaluate,
   still owed per `dyad/dmc/retirement-candidate.jsonld`), and store the reading as the plan file's first section;
   ask the intent question (Question). Board phase `intent-asked`. Re-partitioning many rows at once, the home
   proposes every definition of done in one document, the operator amends only those it would define differently, and
   the counts are kept: rows in, definitions out, absorbed, merged, split, delivered or no longer owed, and amended.
3. **Plan** — `plan`: the plan file (Rule-15 phase 1), opening with its definition of done, after the presence read
   (Rule-16); a play-book the plan runs carries the rows its steps prescribe, stated with their number (Rule-3 Plan);
   a plan split among units names each part on one line, `parts: <unit>: <part>; …`, which the automaton's plan notice
   quotes to each owner, so the home relays only what the plan does not say (#572); ask the plan question.
4. **Authorize** — `authorize`: on `Y`, `open → planned` and the presence touched; a bare `N` revises; `N` with text
   amends in place.
5. **Execute** — `execute`, `verify-prs`: Rule-15 phase 2; branches and PRs cite `d-work #<id>`, `dyad check --pr`
   before each; accreted rows inside the mandate scope, escalated by `dyad/dmc/escalate-edge-test.jsonld` where it
   does not cover them; a fault from outside the row's diff is homed by `dmc:blocker-home`; every departure an
   incident (`dyad/dmc/plan-departure.jsonld`). A plan carries the blocker-fix class only by stating it, other
   carried rows on the same line, the total last:

       Mandate scope: the d-work play-book's blocker-fix row (a restore that stops this row from outside its diff); ceiling 1.

6. **Evidence** — `evidence`: `dyad check --evidence` on each head; at `done-ready`, `dyad board draft <id>` prints the
   data half of the completion evidence, and the agent writes the judgement; its **Candidates** section lists the
   row's structured rulings, one `<record>-<row>-<n>` case each, kept only where `dmc:precedent-admission` could admit
   them, and a `TODO plan-departure: facts | outcome` slot per departure line, which the agent fills; ask the Done
   question.
7. **Record, merge, close** — `record`, `done-record`, `complete`, `close-landed`: record the done-`Y` with the state
   unchanged (`-d 'Y done (merges PR #a at <head-a>)'`, the trace and the candidates in the same commit: `board draft
   <id> --decisions-out <file>`, then `--decisions <file>` on the record, which `dwork state` requires while the draft
   lists a candidate); merge as clerical execution;
   set `done` in a second commit once every named head is on `main` (Rule-3, #202). With the automaton on, the record
   is the last inferring act; it merges and closes from that line.
8. **Defer, resume, mirror** — `defer`, `resume`, `sync-mirror`: a deferral names the blocking row in `refs`; a
   `blocked` row re-enters at 5 when that row is terminal. Retirement is `dyad/runbooks/disposition-digest.md`'s
   `retire`.
9. **Read the backlog and the work in flight** — at session start and each operator prompt, `dyad board resume`
   prints `dmc:backlog-hygiene` and `dmc:work-in-flight`; the home acts on each line as the record says, and judges a
   retirement by `dyad/dmc/retirement-candidate.jsonld`. Hygiene is no guard: no sweep posts it (#617).
10. **Promotion** — when a unit is idle or about to be and nothing is owed, rank the backlog by `dmc:promotion`, the
    release plan of `dyad/playbooks/backlog-groom.md` read within a class; ask the promotion question.
11. **Messages** — a message reaches the operator's chat only as `dmc:message-overhead` says; every other goes to the
    inbox, the automaton or the orchestrating solo.
12. **A question asked again** — `dyad board resume`'s owed list judges each question asked and not answered by
    `dmc:re-present`, printing its outcome and the reason beside it; the home presents it again as the record says,
    one `Y/N` per reply, a revised plan recorded before it is asked again.
    What a trigger says is due and nobody has started is shown, not asked, in the closing line's third part by
    `dmc:recommended-next`, the home recording each inferred item first (`dyad board set _cos recommended=…`).
13. **Orchestration** — between the plan-`Y` and the Done the row stays still and its board entry's phase moves
    (Rule-16 Store): `dyad board phases` prints `dyadlib.ORCH_EVENTS`, and `dyad board advance <id>… <event> --expect
    <phase>` is the one writer, one ledger-only commit per transition, printing the doorbells owed (#587).

Branches: an accreted row skips 2–4 and its Done rides the mandate's; a `backlog` row enters at 1 on a later prompt or
leaves by a Done's `retires` or the retirement form; a terminal row is never reopened, a new row refs it. Run each step
by name; a hand-written script that repeats one is a recurring task (Rule-13 property 1) and becomes a step through its
own row.

Layers (#556). Each step is executed by the layer whose inputs it needs (Rule-16 Presence):

| layer | unit kind | executes | inputs |
|---|---|---|---|
| interaction | dyad unit — the home | 1, 2, 4, 7's record: the operator's words read, the questions presented (`relay-form`), every disposition transcribed and recorded | the operator, live |
| orchestration and execution | solo | 3, 5, 6, 9–12: drafting, dispatching, verifying heads and evidence, judging departures | the ledger and the inbox |
| run-book execution | auto — the automaton | 7's merges and close, plan notices, refusals to the home's inbox (`dyad automaton scan|run`, while `DYAD_AUTOMATON` is `on`) | ledger lines on `main` only |

A report is its own record: the home writes the board only when a row's next act or owner changes, and a unit posts
one report to every box that needs it (`inbox post --cc`). Three acts stay the home's, since no record decides them:
ringing a doorbell, recording a disposition (Rule-7 property 4), and drafting the questions the operator answers.

Tunables (#590): every threshold a cited record names is a preference whose default the record holds
(`dyadlib.tunable`).

## Question
- Intent: `Y/N: intent aligned for #<id> <title>?` — `Y` accepts the reading and its definition of done; `N` with text
  amends; a bare `N` archives the row (`open → archived`).
- Plan: `Y/N: proceed with #<id> as planned?`, or the batch form (Rule-3).
- Done: `Y/N: Done with #<id> <title> (accreted #c, retires #r, merges PR #a)?`, each clause where it names something.
- Retirement: `Y/N: archive #a, #b, … #k?`, executed by `dyad dwork retire <id>... -d '<entry>' --said '<words>'` in
  one ledger commit.
- Promotion: `Y/N: open #a (<class>, <reason>, <owner>), …?`, as `dmc:promotion` forms it.
- A deletion of a branch is its own question (Rule-8).

## Evidence
The completion reply cites, for its row: the transitions taken in order with each input (from `disposed` and the
record), the records written (the row, the plan and its revisions, the record's entry count, the trace), and every
accreted row with its mode. A step run through the runner names its event id. Each ruling the reply names on a decision record — a departure
line (`dyad/dmc/plan-departure.jsonld`, an internal realization among them) or a class line, a record's outcome given
to a case — is a candidate for the row's decision log (Rule-16 Store), written with the `Y` that covers the work and
made a precedent only by a later precedent-`Y` (Rule-3, What a `Y` binds; #644).
