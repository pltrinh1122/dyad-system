# Play-book: disposition digest (core craft, `dyad-operator`; #290)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for
a recurring decision; its steps are a run-book. This one decides **how much of the Operator's attention
a d-work spends, and on what** — which questions are asked, which are folded into a mandate already
given, and which rows leave the board. It is the procedure behind four things no mechanism can decide:
the board reported in every reply, the disposition budget a plan declares, the accreted list the
completion evidence carries, and the held PR that waits for its Done-`Y` instead of asking for a merge.
Read by Rule-3's Scope, Plan, Ledger, Completion counter-prompt and Batch disposition clauses, by
Rule-2's Binding of approval, and by the preferences `accretion`, `batch-disposition-mode` and
`merge-disposition` (`preferences-corpus/PREFERENCES.md`). Steps: `dyad/runbooks/disposition-digest.md`
— `board`, `budget`, `accrete`, `held`, `sweep`, `retire`, one per section — run through
`dyad runbook run disposition-digest <step>`, the core runner, so each step leaves an event.

The vocabulary is the countersign model's (`dyad/playbooks/countersign-model.md`), adopted rather than
coined (Rule-13 property 1): **mandate**, **implicit mode**, **explicit mode**, **delegate edge**, **escalate
edge**, **amend** are Agent vocabulary rows, **basis** that play-book's glossary term, none redefined here
(Rule-6, Master record). The lifecycle this play-book runs is written out in that play-book's Part II §4: "**implicit:** Initiation (signal) → is it covered by a
mandate? If yes: execute within the mandate's scope, then a countersign report. If no: escalation →
explicit."

## Parameter
`BOARD_THRESHOLD` — the number of `backlog` rows at which the retirement sweep is proposed; default
**40**. The steps that read the board take it from the environment, exactly as
`dyad/runbooks/incident-hardening.md` reads `LEDGER` and `dyad/runbooks/dwork-trace.md` reads `DWORK`:

    BOARD_THRESHOLD=<n> dyad runbook run disposition-digest sweep

The default is derived rather than chosen: at the inflow this instance measured — about 2.5 `backlog`
rows a day net over a thirty-day span, against a 5.4% drain (35 of 37 rows ever born `Y backlog` were
still `backlog`) — a threshold of 40 fires roughly once a fortnight, which is a sweep the Operator can
read in one sitting. It is a number, not a judgment: a system with a different inflow sets its own,
and the parameter is what makes this core-craft content rather than one instance's habit.

The per-step ids are the step's own arguments and not the play-book's parameter: `DWORK` (the row whose
budget is read), `MANDATE` and `TITLE` (the mandate a row is accreted under, and the row's title),
`ROWS` (the ids one retirement question named). Each is required where it is used, with no default: a
digest of the wrong d-work is worse than none, which is `dwork-trace`'s own rule for `DWORK`.

## Trigger
Every reply the Agent writes, for the board; and, inside a d-work, at four further moments:
1. **Writing a plan** — the plan declares its disposition budget and, if it accretes anything, its
   mandate scope (Rule-3 Plan, Rule-15 phase 1). A plan with no mandate scope accretes nothing.
2. **About to open a row while executing another** — the escalate-edge test, below, before the row
   exists. Under `accretion: explicit` the test is skipped and the row is asked for, as before the
   preference.
3. **Gathering completion evidence** — the accreted list, the held PRs with their ages and rebase
   counts, and the budget's actual count against its declaration.
4. **Session start, and any reply after a row reaches `backlog`** — the board's `backlog` count
   against `BOARD_THRESHOLD`, which decides whether a retirement sweep is proposed in this reply.

The play-book runs *inside* the d-work the Operator's prompt opened; it opens nothing of its own. A
d-work that notices the board past its threshold states it as a finding and proposes the sweep, since
a d-work opens on an Operator prompt or disposition and never on the Agent's own finding (Rule-3,
Scope).

## The pending board
Three counts and one list, at the end of every reply while any of them is non-empty — the form
Rule-3's Batch disposition already requires of the pending queue, widened by the fourth line, which is
the one the queue never held:

    board: <p> plan-ready · <d> done-ready · <b> backlog (threshold <t>) · named not opened: <ids or none>

- **plan-ready** — every d-work whose plan file is written (Rule-15 phase 1) and whose counter-prompt
  has not yet been asked as part of a batch.
- **done-ready** — every d-work whose completion evidence is gathered and whose Done question has not
  yet been asked.
- **backlog** — the live count from the row store, beside `BOARD_THRESHOLD`, so the sweep's trigger is
  visible to the Operator in the same line that reports the board rather than announced when it fires.
- **named not opened** — the opening candidates this turn surfaced and did **not** open: an intake
  received (Rule-3, Intake), a fence a falsification record left as a candidate, a defect found while
  working something else. This line is why the board is not the pending queue: the queue holds work
  already authorized and waiting for a question, and this line holds work the Agent has decided not to
  put to the Operator at all. Without it the Operator reads a short board and cannot tell a quiet
  session from a session that is quietly accumulating.

The board is conversational, derived from the row store and the stored plan files, and no corpus file
holds it (Rule-3 says the same of the pending queue). Nothing mechanical checks a reply's shape; what
is checkable is the budget, below, and the `sweep` step's own comparison.

## The disposition budget
One line in the plan file, beside its `base commit` and `files touched` lines (Rule-15 phase 1):

    disposition budget: <n> — <what each of the n is>

`<n>` is the number of Operator dispositions the d-work expects to cost, enumerated. The designed
figure is **2** — one plan-`Y`, one Done-`Y` — and a d-work of any size may declare it, because a
mandate makes the number independent of the tree's width: 189 `done` rows hold 426 disposition
entries, mean 2.25, of which 109 cost exactly two and 51 cost more, 77 entries above the designed
figure.

The budget is a **declaration measured against the row**, never a cap on the Operator's right to answer
`N`. An `N` with text is an **amend** (the vocabulary: "the proposal refused and its revision asked
for in the same words, a linked re-entry") and costs a third disposition; the overrun is then stated in
the next revision's own budget line — declared, not absorbed. That is the whole mechanism: the plan
file holds a number, the row's `disposed` column holds a count, both are corpus, and the completion
evidence states the pair. Where they differ the reply says by how much and why.

A budget larger than two is not a fault: a d-work that must stop at a destructive host action (Rule-8),
a release (Rule-11) or a blocking question declares those dispositions in the budget, which is how the
Operator reads the cost before authorizing the shape.

## The escalate-edge test
Applied **before** a row is accreted at all, and answerable entirely from the corpus. An **accreted
row** is one the Agent opens while executing another; under `accretion: implicit` such a row may be
born in **implicit mode** — `open`, `disposed: <date> Y plan (mandate #<id>)`, its provenance entry 1
the mandate's own Operator words copied verbatim with the note `mandate #<id>, <the mandate's own
date>` (Rule-7 property 4) — and takes no disposition of its own. Five questions, every one of which
must pass. Any failure is the **escalate edge** (the vocabulary: "the unexpected returned
for a live countersignature"): the row returns to **explicit mode** and is asked for.

| # | question | failing means |
|---|---|---|
| T1 | does the authorized plan state a **mandate scope** — a rule naming the class of row, and a stated ceiling on how many | no mandate scope: the plan accretes nothing, and this row is asked for |
| T2 | does that rule name **this** row by a property a reader can decide (one child per failure mode, one row per surviving fence), not by resemblance | the class is not decidable: asked for |
| T3 | is the ceiling unspent — the rows already carrying `(mandate #<id>)` fewer than the number the plan stated | the ceiling is spent: asked for, and the plan's own number is reported as reached |
| T4 | is the row's work outside all five never-accretable classes (below) | inside one: asked for, under that Rule's own form |
| T5 | is the row's initiation the **mandate's own Operator words** — not another Operator's, not the Agent's | not the Operator's words: asked for |

**Never accretable, whatever a plan says.** Each has its own reason and none is a judgment call:
- a **destructive host action** — Rule-8 keeps its own counter-prompt naming the action, even inside a
  planned d-work, and Rule-3's Boundaries make it unbatchable too;
- a **release** — Rule-11's Ratification events: it publishes to the world, so it is the Operator's to
  ratify however few d-works it gathers;
- a **Rule-3 Intake** — its words are another Operator's, and Rule-7 property 4 binds them; no mandate
  of this Operator can stand for them. 28 of this instance's 117 accreted rows are intakes;
- a **preference change** — the Agent never changes a value on its own (Rule-2, Not ratification), and
  an authority preference is itself a mandate (`dyad/playbooks/countersign-model.md` Part II §5), so
  accreting one would be the Agent widening its own authorization;
- **any mutation the plan did not describe** — which Rule-3 already calls a new plan.

**The edge fires after birth too.** An implicit-mode row whose *work* departs from the mandate's scope
returns to explicit: the Agent reports the departure and asks, as Rule-3's Incidents clause already
requires of any departure. The row is not unwound — it stays, with its mandate entry — and the
departing work takes its own plan-`Y`. Row **#249** is why this is not decoration: its `disposed` reads
`Y backlog`, then `Y shape (…)`, then **`N plan`** — an accreted row the Operator opened and whose plan
it then refused, and #175 holds two `N plan` entries. Inheritance without the edge would have
authorized what the Operator declined.

**The test's default is `explicit`.** An unanswerable question is a failure, not a pass: T2's "by a
property a reader can decide" exists because `'Y plan' in row.disposed` is a substring test on free
text, so a mandate carried by that string inherits its unreliability (the 2026-10-08 chain-of-authority
audit's L2-2). Where the Agent cannot decide the class, the Operator decides it.

## The accreted list
The completion evidence lists **every row accreted under the mandate**, before the Done question, and
the Done question names them. One line per row:

    #<id> implicit (mandate #<m>) [<state>] — <title, short> — <what it holds> — <dispositions it cost>

and one summary line stating the count against the ceiling the plan declared. The state is in the line
because Rule-3's Ledger clause requires the completion evidence to name each child's state, so an
accreted row left undelivered is something the Operator reads rather than something the Done-`Y` is
read as having verified. The Operator verifies
**the set it got, not the set it was promised**: that asymmetry is the whole difference between this and
moving authority forward onto a promise, and it is why the list is enumerated rather than counted.

An omission is a breach of Rule-3, as every other omission of the completion evidence already is. A
row accreted and then escalated appears in the list with its escalation and the disposition that
answered it, so the list is the full record of what the mandate produced and not only its successes.

The measurement this list exists to make possible is not yet available per row: `dyad dwork trace`
anchors on a prompt and a Done-`Y` (`dyad/playbooks/dwork-trace.md`, Anchors), and an implicit-mode row
has neither of its own — the one 0-anchored trace of the store is exactly such a row. Stated as a
limit; the list is the record meanwhile.

## The held-PR protocol
Under `merge-disposition: with-done`, a PR of a d-work that is **not yet done waits for that d-work's
Done-`Y`**, which names it. The Operator is not asked about a merge. The Done-`Y` still verifies the
output as it stands in the PR, before merge, which is what Rule-3's completion clause exists for — the
gate survives intact and the question disappears. The price is the wait, and this is its protocol:

1. **Cut the tail-append paths narrow and land them first.** A tail-append file is one every session
   appends to at the one place: `agent-corpus/audits/INCIDENTS.md` is appended on most days of a working
   week, and `workstation-corpus/CHANGELOG.md`, `crafts/REGISTRY.md` and `BUNDLE.md` behave the same way.
   A PR carrying such a path and nothing else is a few lines, lands in one step, and takes the collision
   surface out of the held PR. A held PR that still carries a tail-append path is a conflict waiting on
   a clock.
2. **Rebase as `main` moves. Never merge `main` in.** A merge commit on the branch makes the fence judge
   both parents (Rule-3, Mechanisms) and puts `main`'s content in a diff Rule-1 asks to be one zone.
3. **A rebase changes the head, so it voids any disposition already given against it** (Rule-2,
   Binding). A rebase *after* a Done-`Y` is therefore re-prompted, never executed on the old `Y`.
4. **Count the rebases and state them.** The completion evidence names, per held PR: its number, its
   zone, its age in days, its rebase count, and its mergeability as observed — never assumed.
5. **A PR whose d-work cannot reach its Done question at all is an incident on the spot, not a wait.**
   That is the one case the hold does not cover, and it had a live instance: Rule-3's Ledger clause
   asked a decomposed parent's completion counter-prompt only when every child was `done` or `blocked`,
   and a `backlog` child was neither — one row's 23 children held its Done question unaskable while its
   PR waited. The clause now admits `backlog` too, and names each child's state in the completion
   evidence, so an undelivered child is something the Operator reads rather than something that stops
   the question being asked. Where a d-work still cannot reach Done, the hold is reported as the
   incident it is and the PR is not left to rot.

6. **The Done record opens an interval, not a closure.** Rule-3's completion clause records the Done-`Y`
   with the state left as it is, and sets `done` only once every merge that `Y` named has landed (#202).
   Inside that interval the row is still citable at the plan gate, so a refused merge is rebased and
   re-pushed under the row's own plan-`Y` — no recovery row, no reworded commit messages, no local merge
   through `prs.check_transaction`'s `main`-checkout return. Two things the interval does not buy: a rebase
   still changes the head and so voids the `Y` (step 3 above), which costs one fresh Done question on a live
   row instead of a recovery row's three dispositions; and nothing on the kernel-only path can tell a merge
   still pending from a state never written, so `rows.py`'s one warning per row — carried in every evidence
   block — is the reading, and this section's `held` step is the other.

The two prices are measured, not hypothesized. **PR #355**: a merge the Operator ratified on 2026-10-08
(`2026-10-08 Y done merges PR #355` on row #245) and that never ran — still open, `CONFLICTING`,
+423/−0, untouched since 2026-10-08T13:57Z, and the plan gate now refuses it against its own `done` row.
**PR #371**: `MERGEABLE`/`CLEAN` at `6f9150f`, `CONFLICTING`/`DIRTY` within two hours of a concurrent
session's PR #373 merging at `c28a19c` and appending to the same tail-append file. The first is the
hold's worst outcome — a disposition *given* and spent for nothing, which is strictly worse than a
disposition merely *asked* — and it is the reason step 1 is first.

## The retirement sweep
The board's only exit. Rule-3 already defines `archived` as "retired from the working board by an
Operator disposition naming the row(s)"; what made the exit unreachable was `dyadlib.TRANSITIONS`,
where `backlog` had exactly one successor, `open`. With `backlog → archived` in the table, the sweep is:

1. **Trigger.** The live `backlog` count reaches `BOARD_THRESHOLD`. Derived from the row store at
   session start, never carried between sessions.
2. **Candidates.** `backlog` rows, oldest first, each read before it is proposed. A candidate is a row
   whose fence is already recorded elsewhere, whose premise is dead, or whose work another row now
   carries — and the proposal says which, by path or row id. **A row the Agent has not read is proposed
   as a reading, never as a retirement.**
3. **Form.** `Y/N: archive #a, #b, … #k?` — one Operator question over k rows, each named individually,
   with its one line of what it was for and where its fence now lives, in the same reply before the
   question. A `Y` retires exactly the named set; anything else retires none of them (Rule-2, Binding).
4. **The entry.** The one `Y` is written as the same `disposition` entry into every named row's own
   record, which Rule-3's Batch disposition already prescribes — "the Operator's one `Y` is written as
   the same entry into every named d-work's own record" — so Rule-7 property 5's one-to-one count holds
   per row. The row's `disposed` gains `<date> Y archive (sweep #a,#b,#k)`.
5. **Terminal.** `archived → none` (Rule-16, Store). A retired row is never reopened: a new row refs it.
   The row, its plan and its provenance stay where they are — nothing moves (Rule-3, Ledger).

The refusal path is cheap by construction, which is why the sweep batches where a plan batch would not:
a refused *retirement* costs the Operator one reading, because no mutation was authorized and the Agent
re-proposes a narrower set. A refused plan batch, by contrast, unwinds authorization. The two are not
the same question and are never asked as one.

What the sweep is worth on this instance: `archived` has been used **zero times in 280 rows**, **75 rows
sit in `backlog`** with a median age of 21 days and 44 of them at a fortnight or more, and the drain is
**5.4%**. Cheapening the inflow without opening the drain makes the board worse, which is why the drain
is the first thing this play-book does and not the last.

## Reading
- **The board's fourth line first.** Three short counts say what is queued; `named not opened` says
  what the Agent decided alone. A board that is short for several replies while that line grows is the
  thing to read, and it is the only line no mechanism will ever raise.
- **The budget against the row.** An overrun says the plan's shape was wrong, not that the Operator
  answered wrongly. Two overruns of the same kind across two d-works is a claim about the system and is
  falsified (Rule-9) before any Rule or preference encodes it.
- **The accreted list against its ceiling.** A list at the ceiling means the next row escalates, and
  the reply says so rather than letting T3 fail silently.
- **A held PR's age, not its count.** One PR held a day is the protocol working; one held six days is
  PR #355, and its own row is `done`.
- **No verdict from one d-work.** A single expensive d-work is a fact about that d-work. The figures
  this play-book acts on — the question count, the board, the drain — are ledger-wide and reproducible
  from the row store.

## Evidence
The completion reply (Rule-3) carries, for every d-work this play-book ran inside: the declared
disposition budget and the row's actual count, with any overrun named; the accreted list with its
count against the stated ceiling, or the words that no row was accreted; every held PR by number and
zone with its age, rebase count and observed mergeability; every escalation the edge produced and the
disposition that answered it; and the board's four figures. A retirement sweep proposed in that reply
is its own question, asked after the Done question has been answered or in a reply of its own — never
folded into a plan or Done batch, because a retirement and a verification are different acts.

## Conduct
The play-book decides and records; it never disposes (frame: detect, don't dispose; Rule-2 — the Agent
proposes). The Agent never archives a row on its own judgment: `dyad dwork retire` is clerical
execution of a naming disposition, a ledger-only commit. It never accretes a row the mandate scope does
not name, never widens that scope after the plan-`Y` — a widening is a breach of Rule-3 and nothing
catches it, which is the design's stated residual risk, answered by enumerating the delivered set at
Done rather than by trusting the plan file — and never merges a held PR before the Done-`Y` that names
it.

The one thing this play-book cannot do is make a cheaper inflow safe on its own. A mandate that
authorizes rows and a board with no exit together produce a system that asks less and shows more, which
is not the objective. The drain and the escalate edge are the conditions of the mandate, not features
beside it.
