# Operating Guide — running a dyad system as a tree of seats (M4)

For the Operator. Written by the counsel seat of dyad-system during #369, the first program run under M4 (the
Operator's words: provenance #366–#369; the practice: `../rules/organization.md`; the names: `../rules/naming.md`).
It tells you what the organization asks of you, what it gives back, and what it cost the first time. It binds
nothing: your Rules do (`dyad/rules/`), and every sentence here that says "a seat may" means "its charter, which
you wrote, lets it".

## 1. What M4 is, in one paragraph
The organization is an AI-agent **cabinet**: one chief of staff beside you, secretaries over the functions, desks
under them. You keep one seat beside you — the leader, your **cos**, named `program-<hp>` — and it keeps the board
of programs: every parent row you opened and the children it was decomposed into, across the member seats. Each
member seat is a **secretary**: it holds one function you want to watch — `counsel`, `audit`, `engineer`,
`distribute`, `operate` by default — under a **charter** you wrote in the mandates table, and keeps its own board
of the rows and the **desks** under it, a desk being a seat it opens for one topic (`engineer-ledgerd-<hp>`). Every
seat reads and writes the same ledgers, on the same `main`, so you never need a message to know where anything
stands: the row's state, its record and its presence file are the report. You dispose, every seat proposes;
nothing moves on silence. The leader holds your attention, not authority; the members hold authority you granted
by content — paths and kinds of act — never by who they are, because who they are is the one thing the system
cannot check.

## 2. Reading a board
- **Your board is the leader's roll-up**: one line per member seat — children held, open questions, the oldest,
  the stale. At most seven lines. If it is longer, that is the signal: a function to split, or a seat to
  retire or re-home, each by its own row that you dispose.
- **Desks are not on your board.** A secretary opens desks as its concurrent work needs; a desk is unattended
  unless `attended-seats` names it; the leader reads secretaries, never desks. There is no count of desks to keep
  under seven: what bounds them is the secretary's charter, its ceiling read per plan (#416).
- **A seat's state is on `main`**: `dyad dwork list` (every row by state), the row file (`disposed` is the chain
  of your answers), `dyad session list` (every presence file: who holds what, how fresh). A PR number in a row's
  `disposed` entry names the head you said `Y` on.
- **The leader relays, you dispose acts, never merges.** Your own invariant (#384): you dispose the plan review and
  the execution review, never an individual merge, push or pull. Under a mandate the execution review is one
  question: when the member seats' children are done, their evidence travels through the leader into the
  parent's completion reply, and you answer once over the set that reply lists (the mandate form of Rule-3:
  `Y/N: Done with #<id> … (accreted #a, #b, …, merges PR #w, #x, …)?`). A `Y` ratifies exactly that set — the rows
  and the PRs — and a child or a PR left out of the list is left out of the `Y`. After it, each seat executes its
  own merges clerically, referent before referrer (Rule-2: execution is clerical, never disposal), and the leader
  closes the parent once every named head is on `main` (Rule-3's three acts, #202). No seat asks you a Done of its
  own, and no merge is asked separately; a release (Rule-11) and a destructive host action (Rule-8) stay their own
  questions whatever the mandate says. How the Rules' text is reconciled with that invariant is #384's work.

## 3. Opening a seat
1. **Name it before it exists.** Pick the function (a row of your mandates table) and, for a desk, the topic.
   The seat's own handle (`<hp>`) is the first eight hex characters of the harness session you are about to create,
   so the full name is known only once the session exists.
2. **Create the session** (a cloud or terminal session of your harness with the repository attached) and **title
   it** `<seat>: cloud (ds) - <topic>` — the seat name first, then the kernel, your system's handle and what the
   seat is on. Your harness's session list then reads as your board does.
3. **The seat's first act is its registration row**, accreted under the program that opens it or under your own
   prompt: `dyad dwork new "registration of seat <seat>: …"` and `DYAD_SESSION=<seat> dyad session touch -r
   <row>` — always `-r`: a bare touch claims every open row on the board (#130, #325). The presence file now
   carries `host` and `holder`, and `seats.py` reads its name against the form.
4. **Relay the words, not a summary.** What a seat acts on is your verbatim prompt and the plan disposition that
   authorized it, carried by the leader with the row and date they were given on. A seat never acts on the
   leader's paraphrase.
Four seats were opened this way in #369 — the leader renamed twice as the name form was falsified (`cos-1` →
`cos-59cec502` → `program-59cec502`; the old files stay, that is the store's memory), then `counsel`, `engineer`,
`distribute` — each registering itself within minutes of creation.

## 4. Writing a charter
A charter is a row of `preferences-corpus/MANDATES.md` (seeded from `../templates/mandates.md`), yours alone, by
the ordinary preferences-zone PR. Write the **fence as paths and kinds of act**, because that is what the zone
guard and the plan gate can read; write the **ceiling as a number**, because an accreting plan states a ceiling
and the seat's rows are counted against it; write the **escalations** as the things you want asked whatever a plan
says. Under every charter stand the acts no plan may ever cover — a merge or push to `main`, a destructive host
action, a release, a preference value, an intake's words, any mutation the plan did not describe — so you never
need to write them into a fence. A charter narrows; if you find yourself widening one, you are describing a new
seat. Revoke by removing or rewriting the row; a seat acts on the table as it stands on `main` and on nothing
else.

## 5. What only you dispose
Every plan (`Y/N: proceed with #<id> as planned?`), every completion — the execution review, which under a
mandate names every accreted row and every PR of the program at once (§2) — every release tag, every destructive
host action, every preference value, every seat opened or retired, every intake's admission. Not the merges,
pushes and pulls themselves (#384): a leader or member *executes* what you ratified — a merge after your Done-`Y`
is clerical — and may never decide it. When a seat finds that the plan it holds cannot be done as written (the first run found three such cases,
§7), it does not improvise: it records the finding, states the shapes that would work, and waits for your word,
while doing everything the finding does not block.

## 6. The one-pair case
With one seat beside you, you are already running M4: that seat is the leader, your ledger is its board, and the
core's Rules are its charter. Install this craft when you open the second seat; until then nothing here applies
and nothing in the core waits for it (`dyad session touch` prints one advisory line about the name form when the
craft is absent, and checks nothing).

## 7. What the first run cost (dyad-system #369, 2026-10-21 → 22), so you can price the next
- **Three seats idle while a chain is sequential.** The program's children were a chain (C1 → C9) with two
  seats' work gated on the first's; the leader's plan said so and chose the seats anyway, because the organization
  was the point. Expect it: a seat whose predecessor has not landed waits *by state* and says so, which is cheap,
  and starts the children that need nothing of the chain (C4's data rows, C8's notice) which is where the parallel
  time went.
- **A fence the plan did not foresee stops a child without stopping the seat.** Counsel found that the core's
  vocabulary guard refuses a craft term equal to an Agent term, so the words the program adopts could not enter the
  vocabulary while the craft still defined them. The child landed its table, held its rows, recorded the two
  shapes that satisfy the fence, and went on to the next child; you dispose the shape. Budget one such finding per
  program and read it as the program working, not failing.
- **Corrections travel as state, not as orders.** A member found that a tag the plan cited had never been cut;
  the leader wrote a Corrections section into the plan on `main`, announced it to every seat, and ordered nothing.
  Each seat read it at its next push. The cost was one ledger commit and one message; the alternative — a plan
  revision needing your `Y` — would have cost you a question for a fact.
- **Stacked PRs are the price of a shared record — and the rule for dependent children.** Two children of one
  seat edit one record (C1 writes it, C2 appends); the second PR stacks on the first and rebases when it lands.
  The program made it the rule (plan #385, revision 2): within one mandate, a child that depends on another
  child's output stacks on that child's branch, with the predecessor's branch as its PR base; merge order is
  stack order; a head that moves is re-asked. You see two PRs; you dispose both in one Done over the set. What
  it cost before the rule: a stacked copy of a commit beside its merged original is an add/add conflict at the
  merge (the C2 case), paid once.
- **Names are rewritten until they carry the model.** Four falsifications of the seat names in one day (`cos-1`,
  `cos-counsel`, `cos-engineering`, `build` for the machine's seat) ended at `program, counsel, audit, engineer,
  distribute, operate`; each rename cost the leader a presence file and the Operator one question. The names you
  see on your board are the mental model; spend the questions.
- **What a seat never did.** No seat merged, released, wrote a preference, touched another's presence file, or
  acted on the host. Every row of the program was accreted under the one plan-`Y` you gave on revision 10, and
  every one is named in the Done question you will be asked.

## 8. The three modes of attendance, and where a question is asked
You are not at every seat at once. The organization has three **modes**, read from the seats you declare you
attend and checked against what you did (#388, #412; the rule's own sentence: `../rules/organization.md` §6):
- **pure M3** — only the program seat is attended: every member seat's question comes to you through the
  leader;
- **pure M4** — every live seat is attended: each seat asks you in its own chat;
- **hybrid** — the program seat and some of the others are attended: the attended ones ask you directly, the
  rest through the leader.

**Two spans, two numbers.** Your span is how many seats you attend — sit at, read, answer in their own chat.
The leader's span is how many member seats it reads directly: at most seven lines (§2). They are different
numbers over different sets, and neither is how many seats run. A hundred seats are one span for you while you
attend only the program seat and it orchestrates the rest through its members; what you would feel is a second
or a third seat you have to watch, never the hundredth you do not (#412).

**Attendance is declared, and the records check it.** The seats you attend beside the program seat are the
preference `attended-seats`, yours to set: seat names, or seat names without their `-<hp>` (`counsel` covers every
holder of the counsel seat), or `none`. Its default is `none`: only the program seat is attended, and every
other seat's question reaches you through the leader. Declaring a seat is a preferences-zone PR you dispose, like
any preference; nothing a seat writes about itself makes it attended (#295: a holder is what the process says).
The records are the check, read over the **attendance window** (the preference `attendance-window`, default 7
days): a disposition you gave in a live seat's own chat — not a mandate's inherited `Y`, not a relayed one — that
the preference does not declare prints `undeclared`, because you answered where you said you were not — the
leader reports it to you once, and no member seat reports it as an incident of its own; a declared
seat with no disposition of yours within the window prints `warn`, because you said you were there and have not
been. The mode is read over the live seats (presence files within the stale window): only the program seat
attended → M3, the default; every live seat → M4; otherwise hybrid. `dyad session list` prints the declared set,
the mode, each seat's `attended` or `relayed`, and the two check lines.

**The route table.** An escalation — a counter-prompt a seat owes you (a plan, a Done, a fence it cannot cross,
a release or destructive action that is always its own question) — is asked where you will see it:

| the seat is | the question is asked | the answer travels | the record |
|---|---|---|---|
| attended | in the seat's own chat, by the seat | directly: your words in that seat's provenance | the seat's provenance record (Rule-7) |
| not attended | in the leader's chat, by the leader, verbatim, with the seat named | relayed back to the seat verbatim (R29: a cos relays, never answers) | the seat's plan file quotes the question; the leader's provenance carries your answer; the seat's row cites it (#314's shape, until the bus of #303 lands) |
| the leader itself | in the leader's chat | — | the leader's provenance |

The board lists every outstanding question with its route (R17), so you see in one place what to answer and
where. What never changes with the mode: who disposes (you), what a seat may do without asking (its charter,
§4), and what is never accretable (§5). What changes is only the chat a question reaches you in — and the
seats never guess it: the route follows the set you declared, the same set the mode is read from.
