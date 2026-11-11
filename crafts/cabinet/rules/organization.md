# Organization (cabinet craft, Tended rule)

Read by Rule-3's Ledger clause through the Operating Guide it cites (`../docs/operating-guide.md`, #369 C7) and
by the preference `organization` (`preferences-corpus/PREFERENCES.md`, the operator's; its template row is the
core's). A Tended rule: any form, no Rule-4 block, no sweep, no agent-vocabulary row. It holds the *practice* —
how the units beside one or many operators are organized — and never the process: what a row is, who disposes,
what a mandate binds and what may never be accreted stay the core's Rules (2, 3, 7, 15, 16) and are cited, not
restated. Terms: `../vocabulary/CRAFT.md`; the core's `seat`, `holder`, `presence file`, `mandate`, `mandate scope`,
`accreted row`, `mode`, `escalation` (`dyad/vocabulary/VOCABULARY.md`). Record: `../falsification/rules/organization.md`.
Source: dyad-system #366 (M1–M4, stress-tested for a single operator and an enterprise operator), #367 (M4 against
organizational-design practice), #368 (the tree and the charters), #369 revisions 4–10 (this craft, the units and
their names), #253 §6–§7 (the bands and the cos), #285 and #306 (the standing conduct) — the operator's words in
those rows' provenance records.

## Intent
State one organization every dyad system runs under unless its operator says otherwise — **M4**: a tree of
operator–unit pairs in which the cos and every secretary keep a board, authority is granted by content-scoped charters and
never by identity, and every pair reads and writes the same ledgers — so that one operator attends at most seven
dyad units, while the solos beside them, secretaries and as many desks as their work needs, scale with the host's
capacity, without a second disposer anywhere.

## 1. The tree
- **One pair is the whole organization until it is not.** A dyad system with one unit beside its operator runs M4
  already: that unit is its cos, its board is the ledger, and no charter is needed — the core's Rules are the
  charter. Nothing in this rule asks a one-pair system to open a second unit (the core's `d-work` play-book and
  Rule-16 cover the one-pair case without this craft installed).
- **The cos** sits beside the operator and keeps the board of programs: every parent row and its children
  across the member units. It relays the operator's words to a unit verbatim (the core's relayed prompt, Rule-7
  property 4), writes no row for a unit, answers no unit's question, merges no unit's PR as its own act — a unit
  executes its own merge (§5), and the cos executes one only as the reported fallback for a merge a unit's harness
  refused (#540) — it holds attention, not authority (#253 R28), and does itself only the five acts the Guide names — receive, route, present, relay back,
  board — handing every other on (`../docs/operating-guide.md` §2, #432). What it reads: one roll-up line per
  member unit, folded to at most seven lines (Span of control).
- **A secretary** holds one function — what the operator watches on its board — under a charter of the mandates
  table. It keeps its own cos-board of the rows it holds and the desks on it, reports by state on `main` and in
  its presence file, announces and never orders, and asks nothing of the home: every question is the operator's.
- **A desk** holds one topic of a member's function under that member's charter (a narrower fence, never
  a wider one); it sits on the member's board. The tree is as deep as the fences nest and never deeper.
- **Span of control.** The operator's span is the dyad units, the home and every unit `paired-units` names: **at
  most seven dyad units**, the units the operator attends (Rule-16 Presence, #412; dyad-system #620). A solo,
  secretary or desk, is **never counted**: how many run is bounded by the host's capacity and each charter's
  ceiling, read when a unit is opened (`../dmc/unit-lifecycle.jsonld`). **Pairing past seven** is the signal to
  unpair a unit, proposed to the operator and never done by a unit. No solo is retired, merged or split to keep a
  span or a board short. The home reads one roll-up line per secretary, never a desk, folded to seven lines for
  its one reader. A longer board is **a channel matter** (`../dmc/attention-problem.jsonld`, the Guide §12),
  never the span's. Desks are unbounded: a secretary opens as many as its concurrent work needs, one session
  each, bounded only by its own charter's ceiling (#416 prompt 4); a desk is solo unless `paired-units` names it
  (§6).
- **Workstations: a cos per operator, a desk per workstation** (dyad-system #531). A cos belongs to an operator's
  attention, never to a machine; a workstation is a place where acts run, so it gets a desk. One cos per operator,
  bound to no machine. A workstation is a **topic**, never a function: a function whose acts are machine-bound on a
  host — operate's host actions, engineer's builds and tests that only that host can run — opens a desk with the host
  as its topic (`operate-mac-<hp>`, `engineer-mac-<hp>`), standing while the host has a stream of work and opened per
  act otherwise, on its own function's board, so the charters stay orthogonal and the home's seven lines do not
  change. With several operators, each operator's leader is `program-<operator>-<hp>` under one cos, and the
  workstations of each are desks as above. Eight topologies were scored on ten criteria
  (`../dmc/seat-topology.jsonld`): **a cos per workstation** and **a subordinate workstation cos** fail the gates of
  one board, one relay and N Operators; **host-first secretaries** fail orthogonal charters; **a cos re-seated
  onto each workstation** and **a system per workstation** fail N Operators, the second also one board and the same
  ledgers; **roaming units** survive and merge into the selected topology as its desks opened per act. Selected:
  **a cos per operator and a desk per (function, workstation)**, with **a leader per operator** as its extension
  to several operators. A second live `program` unit of one operator is a re-seating in progress or a mistake,
  never a second cos: `guards/seats.py` warns on it. Where the cos itself is headed — a mode any unseated session
  can hold, rather than one session — is the Guide's (`../docs/operating-guide.md` §10).

## 2. The precondition: the same ledgers
Every pair of the tree reads and writes **the same ledgers** — one row store, one provenance store, one presence
store, one incident log (`<instance>/d-work/`, `<instance>/audits/`), on one `main` in the default case of one
repository; in the enterprise case of several repositories, every pair's ledgers are the same set and `main` is
each repository's own (#368, revisions 4–5). What this buys is that a unit's state is readable by every other unit
and by every operator from the corpus alone, with no message anyone has to have received: a row's `state`, its
`disposed` column, its record and its presence file are the report. A unit whose ledger another unit cannot read
is not in the tree; it is another system, and work for it is an intake (Rule-3 Intake).

## 3. Charters: the mandates table
Authority in M4 is a standing mandate in the operator's hand, written as one row per unit of the **mandates
table** (`preferences-corpus/MANDATES.md`, preferences zone — the operator's, by the ordinary preferences-zone PR;
seeded from `../templates/mandates.md`). A charter is a band in #253's sense (R23–R27) and keeps its properties:
- **content-scoped, never identity-scoped** (R24): the fence is over paths and kinds of act, because identity is
  the one thing this system cannot check — a unit is a presence file and a holder is what the process says;
- **mechanically checkable where it can be** (R25): the fence names paths the zone guard and the plan gate already
  read; what no guard reads is stated as inference in the charter's own row;
- **under the ceiling** (R26): no charter contains what the core never lets a plan accrete — a merge to `main`, a
  direct push to `main`, a destructive host action, a release, a preference value, an intake's words, a mutation
  no plan described (Rule-2 Binding, Rule-3 Scope); charters narrow and never widen;
- **superseded only by the operator** (R27): a charter ends by the revocation its row names, which is always a
  preferences-zone change; no unit revokes another's.
The columns: `seat` (the name, or the name's form for a unit not yet opened), `function`, `domain` (what it owns,
in the words the operator watches), `fence` (the paths and act kinds its rows may touch), `ceiling` (how many rows
one plan of that unit may accrete), `escalations` (what returns to the operator as an explicit question whatever
the plan says), `revocation` (the change that ends the charter). `guards/seats.py` reads the table's shape and the
function column; what a charter *permits* is the operator's reading, never a guard's.

## 4. The default organization
Seven functions, one leader and six members (plan #369 revisions 8–10, falsified there; `orchestrate` added by dyad-system #557), each named by what the
operator watches on its board — verbs for flows, a noun for the portfolio:

| function | kind | domain | the seam it keeps |
|---|---|---|---|
| `program` | cos | the board of programs: every parent row and its children, across the members; relay, roll-up; the board's stale rows and unmerged branches (#433) | accretes nothing; owns no domain |
| `counsel` | secretary | the Rules, the vocabulary, the model (`dyad/playbooks/countersign-model.md`), the crafts' governance and shape; the Rule-5 sweeps and the self-diagnostic's prose claims (#433) | Rule text and craft shape, never the machine's code |
| `audit` | secretary | the incident ledger and its hardening (all but the execute step, which the unit owning the fence runs), and the re-test of every shipped fence (#433) | delegates nothing and accretes nothing: the one member whose rows are findings, never fixes (Three Lines) |
| `engineer` | secretary | the product: the core craft's machine — guards, CLI, stores, trace, board, their tests (`dyad check` is its verb); the standing regression and the self-diagnostic's coded checks (#433) | the machine, never its shipping |
| `distribute` | secretary | the shipping of every craft: install, port, release, bundle, registry, their tests (`dyad build`, `install`, `export` are its verbs) | the seam `package.py` already draws between `check` and `build/install` |
| `operate` | secretary | the host: read-before-act, classes, ops scripts the operator runs, run-books, change-log rows, the services behind boards; host documents older than the running kernel and presence past the stale window (#433) | the sysadmin craft's whole practice, delivered by the unit and executed by the operator |
| `orchestrate` | secretary | the d-work play-book's orchestration layer for every row the home routes: dispatch by inbox relay, collect reports, verify heads and evidence, judge departures and incidents, draft the completion evidence and the Done question for the home to present (#557) | orchestrates, never authors: ledger-only commits to the board and the inbox, read-only over the tree, no branch, PR or merge of its own; accretes nothing |

A system adopts the seven by copying the template; it renames, drops or adds a function by editing its own table —
the craft ships the default, never the instance.

## 5. The standing conduct of every unit
What a unit does and never does, as the operator tends it (#285, #306; the process residue — what a row is,
who disposes — stays the core's):
- **Relay verbatim.** The operator's words reach a unit as the operator gave them, with the row and date they were
  given on (the core's relayed prompt and the mandate note of Rule-7 property 4); a unit adds its own words beside
  them, never inside them. Verbatim binds that unit-bound direction only: a unit's question reaches the operator
  through the cos in the form the preference `relay-form` names (the Guide §3), the unit's own question its last line.
- **Preferences and charters through the cos.** The cos presents a preference value or a charter, each as its own
  question, and never pushes it; a secretary never asks one itself — the secretary whose row needs it drafts the
  exact `preferences-corpus/` diff, pushes the branch and opens the PR for the cos to present, a proposal and not
  the write the never-list below forbids (#427, #432).
- **Announce, never order.** A unit reports by state — the row on `main`, its presence file, the PR — and by one
  roll-up line; it asks the operator and never another unit; it tells another unit what it found and never what
  to do.
- **Report by inbox.** A unit's report to the cos, and the cos's relay to a unit, is a message in the addressee's
  inbox (the core's inbox store, `dyad inbox post <seat> --row <id> --kind <kind>`), addressed by unit name and read at
  the start of every turn; a chat message to a session is at most a doorbell that one is waiting. A message informs
  and never authorizes: a disposition is read from the row and its record, and the operator's words relayed to a unit
  travel verbatim, citing the record entry they were given in (dyad-system #536).
- **Hold the question.** The home relays each unit's completion evidence into the parent's own completion reply;
  the operator disposes once, over the set the evidence lists (Rule-3's Completion clause, the mandate
  form). No unit merges on another unit's reading, and no unit reads silence as consent.
- **Execute your own merge, on the record.** A unit merges its own PR itself, clerically (Rule-2), once the
  operator's Done disposition naming that PR at its head is recorded on `main` — given in the unit's own chat or in
  the cos's — with `dyad merge <pr> --head <sha>`, which acts only on that recorded entry and the PR's live head and
  refuses anything else (dyad-system #532, its exit test passed in #540). It runs the verb from `main`'s code (a
  fresh worktree of `origin/main` when the unit's checkout predates it), never from its own branch's. A unit whose
  harness refuses the verb stops, reports the refusal word for word, and the cos executes that merge as the
  fallback, reported to the operator — never a way around the refusal, and never the cos's merge by default.
  While the operator's repository variable `DYAD_AUTOMATON` is `on`, the automaton executes the merge and the close
  from the recorded entry instead (the d-work play-book's run-book layer, dyad-system #556): no unit merges a row it
  serves, and a refusal it posts to the home's inbox is resolved by the owning unit, never merged around.
- **Keep the board short.** A roll-up line is children held, open questions, the oldest, the stale — and nothing a
  reader could get from the row itself.
- **Escalate at the fence.** A row whose work leaves the charter's fence, or that the charter's ceiling does not
  cover, returns to explicit mode and is asked (the escalate edge, Rule-3 Scope) — the escalation is the unit's own
  line in its evidence, never a quiet widening.
- **Never:** merge to `main` without the operator's Done disposition, cut a release tag, write a preference value,
  touch another unit's presence file, act on the host outside an ops script or a run-book the operator runs
  (Rule-8), or open a unit the mandates table does not name (a fourth unit is a new plan, plan #369 revision 5).

## 6. Attendance, declared — checked against the records
Which units an operator attends is declared by the operator and checked against the record, never claimed by a
unit: a unit is **paired** when it is the home or the preference `paired-units` (the operator's, default
`none`) names it. The constraint it states is the operator's span — how many units the operator sits at — at most
seven dyad units (§1, Span of control); the home's roll-up of at most seven lines is a channel, not a span (the
Guide, §2), and neither is how many units run (#412). Over the
live units this yields the organization's **mode** — pure M3 (only the home paired, the default), pure M4
(every unit), hybrid — and from the declared set the **route** of every question a unit owes the operator: asked in
the unit's own chat when paired, relayed through the home verbatim and answered verbatim otherwise (#253 R17,
R29). The record is the check: a disposition given in a live unit's own chat within the attendance window (the
preference `attendance-window`) — not a mandate's inherited one, not a relayed one — in a unit the preference does
not declare is `undeclared`, reported by the home alone — a reading of the board, never a Rule-3 incident, since
the act is the operator's; a declared unit holding none is a `warn`. No presence file carries an attendance
line, because a line a unit writes about itself is a claim nobody verifies (#295); the declaration is the
operator's preference and the proof is Rule-7's record. The reading is the core's (#388, #412: `dyad session
list`); this rule states what it means and the Guide (`../docs/operating-guide.md` §8) what the operator does
with it.

## When
- A unit is opened, renamed, re-homed or retired: a row of its own, under the operator's disposition; the mandates
  table changes by the operator's preferences-zone PR, before the unit acts under the new row. Which of these a
  moment calls for, an idle unit, a re-seat (a rename under a new holder), a desk, a new function, a re-home, a
  retirement or nothing, is `../dmc/unit-lifecycle.jsonld` for opening and keeping, read after `scale-out`; a unit's
  ending, re-homing its rows and retiring it with the changes that makes, is the unit and session tidy play-book's
  (`../playbooks/session-tidy.md`), each act decided by `../dmc/session-tidy.jsonld` (#669).
- A function is added or a charter widened: the operator's table change first; a unit never acts on a charter that
  is not yet on `main`.
- The tree gains a second operator: each member pair's leader is named `program-<operator>-<hp>` (`naming.md`),
  its ledgers the same set as the tree's (§2), its charters rows of the same table.

## Inference, stated
Whether a unit stayed inside its fence is read from its PRs' paths (the zone guard reads the zone, never the
charter); whether a roll-up line was honest is read against the rows it summarizes; whether a holder is the unit it
claims is never verifiable (the core's `holder`, `agent-corpus/falsification/seat-vs-harness-session.md`). The
guard counts names and columns and nothing more.
