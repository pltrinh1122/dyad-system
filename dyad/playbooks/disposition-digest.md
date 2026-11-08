# Play-book: disposition digest (core craft, `dyad-operator`; #290, #626)

How much of the operator's attention a d-work spends, and on what: which questions are asked, which a mandate already
answered, and which rows leave the board. Read by Rule-3's Scope, Plan, Ledger, Completion counter-prompt and Batch
disposition, by Rule-2's Binding, and by the preferences `accretion`, `batch-disposition-mode` and `merge-disposition`.
Steps: `dyad/runbooks/disposition-digest.md` — `board`, `budget`, `accrete`, `held`, `sweep`, `retire` — run as
`dyad runbook run disposition-digest <step>`. Terms are the countersign model's (`dyad/playbooks/countersign-model.md`).

## Parameter
`BOARD_THRESHOLD` — the `backlog` count at which a retirement sweep is proposed; default **40** (about a fortnight's
inflow on this instance). Per-step ids — `DWORK`, `MANDATE`, `TITLE`, `ROWS`, `SAID` — are required where used, with
no default:

    BOARD_THRESHOLD=<n> dyad runbook run disposition-digest sweep

## Trigger
Every reply, for the board; inside a d-work, also when a plan is written, before a row is accreted, when completion
evidence is gathered, and at session start or after a row reaches `backlog`. It opens nothing of its own (Rule-3 Scope).

## Steps
1. **Board** — `board`: report the board at the end of every reply while any line is non-empty, as `dmc:board-lines`
   forms it.
2. **Budget** — the plan declares its disposition budget; `budget` reads it against the row, judged by
   `dmc:disposition-budget`. The designed figure is 2, one plan-`Y` and one done-`Y`.
3. **Accrete** — before a row is opened under a mandate, apply `dmc:escalate-edge-test` (T1–T5); never accretable,
   whatever a plan says: a destructive host action (Rule-8), a release (Rule-11), an intake (Rule-7 property 4), a
   preference change (Rule-2), a mutation the plan did not describe. A born row whose work departs from the scope
   returns to explicit mode by the escalate edge: reported, asked, never unwound. Then `accrete`.
4. **Accreted list** — in the completion evidence, one line per accreted row, `#<id> implicit (mandate #<m>) [<state>] —
   <title> — <what it holds> — <dispositions it cost>`, and the count against the ceiling; an escalated row appears with
   its escalation. The Done question names them.
5. **Held PRs** — `held`: under `merge-disposition: with-done` each PR is handled by `dmc:held-pr`; the Done-`Y`
   still verifies the output as it stands in the PR, before merge.
6. **Retire** — `sweep`: `dmc:retirement-sweep` over the live count; each `backlog` row read, oldest first, judged by
   `dmc:retirement-candidate`; ask the retirement form; on `Y`, `retire`. `archived` is terminal: a new row refs it.

## Question
- The retirement form, `Y/N: archive #a, #b, … #k?`, each row listed with what it held and its ground; a `Y` retires
  exactly the named set, anything else none. It is its own question, asked after the Done is answered or in a reply of
  its own, never folded into a plan or Done batch.
- A row the escalate edge returns is asked as any row.

## Evidence
The completion reply carries the declared budget and the row's count, any difference named; the accreted list
against its ceiling, or that none was accreted; every held PR with its zone, age, rebase count and observed
mergeability; every escalation and the disposition that answered it; and the board's four figures. The agent never
archives on its own judgment: `dyad dwork retire` executes a naming disposition, a ledger-only commit.
