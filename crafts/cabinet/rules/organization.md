# Organization (cabinet craft, Tended rule)

Read by Rule-3's Ledger clause through the Operating Guide it cites (`../docs/operating-guide.md`, #369 C7) and
by the preference `organization` (`preferences-corpus/PREFERENCES.md`, the Operator's; its template row is the
core's). A Tended rule: any form, no Rule-4 block, no sweep, no Agent-vocabulary row. It holds the *practice* —
how the seats beside one or many Operators are organized — and never the process: what a row is, who disposes,
what a mandate binds and what may never be accreted stay the core's Rules (2, 3, 7, 15, 16) and are cited, not
restated. Terms: `../vocabulary/CRAFT.md`; the core's `seat`, `holder`, `presence file`, `mandate`, `mandate scope`,
`accreted row`, `mode`, `escalation` (`dyad/vocabulary/VOCABULARY.md`). Record: `../falsification/rules/organization.md`.
Source: dyad-system #366 (M1–M4, stress-tested for a solo and an enterprise Operator), #367 (M4 against
organizational-design practice), #368 (the tree and the charters), #369 revisions 4–10 (this craft, the seats and
their names), #253 §6–§7 (the bands and the cos), #285 and #306 (the standing conduct) — the Operator's words in
those rows' provenance records.

## Intent
State one organization every dyad system runs under unless its Operator says otherwise — **M4**: a tree of
Operator–seat pairs in which the cos and every secretary keep a board, authority is granted by content-scoped charters and
never by identity, and every pair reads and writes the same ledgers — so that one Operator's attention scales to
five to seven secretaries, and a secretary's to as many desks as its concurrent work needs, without a second
disposer anywhere.

## 1. The tree
- **One pair is the whole organization until it is not.** A dyad system with one seat beside its Operator runs M4
  already: that seat is its cos, its board is the ledger, and no charter is needed — the core's Rules are the
  charter. Nothing in this rule asks a one-pair system to open a second seat (the core's `d-work` play-book and
  Rule-16 cover the one-pair case without this craft installed).
- **The cos** sits beside the Operator and keeps the board of programs: every parent row and its children
  across the member seats. It relays the Operator's words to a seat verbatim (the core's relayed prompt, Rule-7
  property 4), writes no row for a seat, answers no seat's question, merges nothing — it holds attention, not
  authority (#253 R28), and does itself only the five acts the Guide names — receive, route, present, relay back,
  board — handing every other on (`../docs/operating-guide.md` §2, #432). What it reads: one roll-up line per
  member seat, at most seven.
- **A secretary** holds one function — what the Operator watches on its board — under a charter of the mandates
  table. It keeps its own cos-board of the rows it holds and the desks on it, reports by state on `main` and in
  its presence file, announces and never orders, and asks nothing of the leader: every question is the Operator's.
- **A desk** holds one topic of a member's function under that member's charter (a narrower fence, never
  a wider one); it sits on the member's board. The tree is as deep as the fences nest and never deeper.
- **Span of control.** A reader keeps five to seven lines: the Operator reads the leader's board, and the leader
  reads one line per secretary — never a desk. A leader's board longer than seven is the signal to consolidate (a
  secretary's seat retired or re-homed by its own row) or to split a function — proposed to the Operator, never
  done by a seat. Desks are unbounded: a secretary opens as many as its concurrent work needs, one session each,
  bounded only by its own charter's ceiling (#416 prompt 4); a desk is unattended unless `attended-seats` names it,
  so desks never count against the Operator's span (§6).
- **Workstations: a cos per Operator, a desk per workstation** (dyad-system #531). A cos belongs to an Operator's
  attention, never to a machine; a workstation is a place where acts run, so it gets a desk. One cos per Operator,
  bound to no machine. A workstation is a **topic**, never a function: a function whose acts are machine-bound on a
  host — operate's host actions, engineer's builds and tests that only that host can run — opens a desk with the host
  as its topic (`operate-mac-<hp>`, `engineer-mac-<hp>`), standing while the host has a stream of work and opened per
  act otherwise, on its own function's board, so the charters stay orthogonal and the leader's seven lines do not
  change. With several Operators, each Operator's leader is `program-<operator>-<hp>` under one cos, and the
  workstations of each are desks as above. Eight topologies were scored on ten criteria
  (`../dmc/seat-topology.jsonld`): **a cos per workstation** and **a subordinate workstation cos** fail the gates of
  one board, one relay and N Operators; **host-first secretaries** fail orthogonal charters; **a cos re-seated
  onto each workstation** and **a system per workstation** fail N Operators, the second also one board and the same
  ledgers; **roaming seats** survive and merge into the selected topology as its desks opened per act. Selected:
  **a cos per Operator and a desk per (function, workstation)**, with **a leader per Operator** as its extension
  to several Operators. A second live `program` seat of one Operator is a re-seating in progress or a mistake,
  never a second cos: `guards/seats.py` warns on it. Where the cos itself is headed — a mode any unseated session
  can hold, rather than one session — is the Guide's (`../docs/operating-guide.md` §10).

## 2. The precondition: the same ledgers
Every pair of the tree reads and writes **the same ledgers** — one row store, one provenance store, one presence
store, one incident log (`<instance>/d-work/`, `<instance>/audits/`), on one `main` in the default case of one
repository; in the enterprise case of several repositories, every pair's ledgers are the same set and `main` is
each repository's own (#368, revisions 4–5). What this buys is that a seat's state is readable by every other seat
and by every Operator from the corpus alone, with no message anyone has to have received: a row's `state`, its
`disposed` column, its record and its presence file are the report. A seat whose ledger another seat cannot read
is not in the tree; it is another system, and work for it is an intake (Rule-3 Intake).

## 3. Charters: the mandates table
Authority in M4 is a standing mandate in the Operator's hand, written as one row per seat of the **mandates
table** (`preferences-corpus/MANDATES.md`, preferences zone — the Operator's, by the ordinary preferences-zone PR;
seeded from `../templates/mandates.md`). A charter is a band in #253's sense (R23–R27) and keeps its properties:
- **content-scoped, never identity-scoped** (R24): the fence is over paths and kinds of act, because identity is
  the one thing this system cannot check — a seat is a presence file and a holder is what the process says;
- **mechanically checkable where it can be** (R25): the fence names paths the zone guard and the plan gate already
  read; what no guard reads is stated as inference in the charter's own row;
- **under the ceiling** (R26): no charter contains what the core never lets a plan accrete — a merge to `main`, a
  direct push to `main`, a destructive host action, a release, a preference value, an intake's words, a mutation
  no plan described (Rule-2 Binding, Rule-3 Scope); charters narrow and never widen;
- **superseded only by the Operator** (R27): a charter ends by the revocation its row names, which is always a
  preferences-zone change; no seat revokes another's.
The columns: `seat` (the name, or the name's form for a seat not yet opened), `function`, `domain` (what it owns,
in the words the Operator watches), `fence` (the paths and act kinds its rows may touch), `ceiling` (how many rows
one plan of that seat may accrete), `escalations` (what returns to the Operator as an explicit question whatever
the plan says), `revocation` (the change that ends the charter). `guards/seats.py` reads the table's shape and the
function column; what a charter *permits* is the Operator's reading, never a guard's.

## 4. The default organization
Six functions, one leader and five members (plan #369 revisions 8–10, falsified there), each named by what the
Operator watches on its board — verbs for flows, a noun for the portfolio:

| function | kind | domain | the seam it keeps |
|---|---|---|---|
| `program` | cos | the board of programs: every parent row and its children, across the members; relay, roll-up; the board's stale rows and unmerged branches (#433) | accretes nothing; owns no domain |
| `counsel` | secretary | the Rules, the vocabulary, the model (`dyad/playbooks/countersign-model.md`), the crafts' governance and shape; the Rule-5 sweeps and the self-diagnostic's prose claims (#433) | Rule text and craft shape, never the machine's code |
| `audit` | secretary | the incident ledger and its hardening (all but the execute step, which the seat owning the fence runs), and the re-test of every shipped fence (#433) | delegates nothing and accretes nothing: the one member whose rows are findings, never fixes (Three Lines) |
| `engineer` | secretary | the product: the core craft's machine — guards, CLI, stores, trace, board, their tests (`dyad check` is its verb); the standing regression and the self-diagnostic's coded checks (#433) | the machine, never its shipping |
| `distribute` | secretary | the shipping of every craft: install, port, release, bundle, registry, their tests (`dyad build`, `install`, `export` are its verbs) | the seam `package.py` already draws between `check` and `build/install` |
| `operate` | secretary | the host: read-before-act, classes, ops scripts the Operator runs, run-books, change-log rows, the services behind boards; host documents older than the running kernel and presence past the stale window (#433) | the sysadmin craft's whole practice, delivered by the seat and executed by the Operator |

A system adopts the six by copying the template; it renames, drops or adds a function by editing its own table —
the craft ships the default, never the instance.

## 5. The standing conduct of every seat
What a seat does and never does, as the Operator tends it (#285, #306; the process residue — what a row is,
who disposes — stays the core's):
- **Relay verbatim.** The Operator's words reach a seat as the Operator gave them, with the row and date they were
  given on (the core's relayed prompt and the mandate note of Rule-7 property 4); a seat adds its own words beside
  them, never inside them. Verbatim binds that seat-bound direction only: a seat's question reaches the Operator
  through the cos in the form the preference `relay-form` names (the Guide §3), the seat's own question its last line.
- **Preferences and charters through the cos.** The cos presents a preference value or a charter, each as its own
  question, and never pushes it; a secretary never asks one itself — the secretary whose row needs it drafts the
  exact `preferences-corpus/` diff, pushes the branch and opens the PR for the cos to present, a proposal and not
  the write the never-list below forbids (#427, #432).
- **Announce, never order.** A seat reports by state — the row on `main`, its presence file, the PR — and by one
  roll-up line; it asks the Operator and never another seat; it tells another seat what it found and never what
  to do.
- **Hold the question.** The leader relays each seat's completion evidence into the parent's own completion reply;
  the Operator disposes once, over the set the evidence lists (Rule-3's Completion clause, the mandate
  form). No seat merges on another seat's reading, and no seat reads silence as consent.
- **Keep the board short.** A roll-up line is children held, open questions, the oldest, the stale — and nothing a
  reader could get from the row itself.
- **Escalate at the fence.** A row whose work leaves the charter's fence, or that the charter's ceiling does not
  cover, returns to explicit mode and is asked (the escalate edge, Rule-3 Scope) — the escalation is the seat's own
  line in its evidence, never a quiet widening.
- **Never:** merge to `main` without the Operator's Done disposition, cut a release tag, write a preference value,
  touch another seat's presence file, act on the host outside an ops script or a run-book the Operator runs
  (Rule-8), or open a seat the mandates table does not name (a fourth seat is a new plan, plan #369 revision 5).

## 6. Attendance, declared — checked against the records
Which seats an Operator attends is declared by the Operator and checked against the record, never claimed by a
seat: a seat is **attended** when it is the leader or the preference `attended-seats` (the Operator's, default
`none`) names it. The constraint it states is the Operator's span — how many seats the Operator sits at — which is
not the leader's span of at most seven direct lines (the Guide, §2) and not how many seats run (#412). Over the
live seats this yields the organization's **mode** — pure M3 (only the leader attended, the default), pure M4
(every seat), hybrid — and from the declared set the **route** of every question a seat owes the Operator: asked in
the seat's own chat when attended, relayed through the leader verbatim and answered verbatim otherwise (#253 R17,
R29). The record is the check: a disposition given in a live seat's own chat within the attendance window (the
preference `attendance-window`) — not a mandate's inherited one, not a relayed one — in a seat the preference does
not declare is `undeclared`, reported by the leader alone — a reading of the board, never a Rule-3 incident, since
the act is the Operator's; a declared seat holding none is a `warn`. No presence file carries an attendance
line, because a line a seat writes about itself is a claim nobody verifies (#295); the declaration is the
Operator's preference and the proof is Rule-7's record. The reading is the core's (#388, #412: `dyad session
list`); this rule states what it means and the Guide (`../docs/operating-guide.md` §8) what the Operator does
with it.

## When
- A seat is opened, renamed, re-homed or retired: a row of its own, under the Operator's disposition; the mandates
  table changes by the Operator's preferences-zone PR, before the seat acts under the new row.
- A function is added or a charter widened: the Operator's table change first; a seat never acts on a charter that
  is not yet on `main`.
- The tree gains a second Operator: each member pair's leader is named `program-<operator>-<hp>` (`naming.md`),
  its ledgers the same set as the tree's (§2), its charters rows of the same table.

## Inference, stated
Whether a seat stayed inside its fence is read from its PRs' paths (the zone guard reads the zone, never the
charter); whether a roll-up line was honest is read against the rows it summarizes; whether a holder is the seat it
claims is never verifiable (the core's `holder`, `agent-corpus/falsification/seat-vs-harness-session.md`). The
guard counts names and columns and nothing more.
