# Falsification record — Rule-16 (concurrent sessions) (ledger #106)

**Claim (operator, 2026-09-13):** the store should support concurrent sessions with minimum
collision surface and minimum merging (one session planning, another executing).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Every guard and test parses one table. | Survives | They parse rows; `dyadlib` is the one reader; the table parser stays for rendering and tests. |
| 2 | An untracked view scatters the record. | Survives | `package.py ledger` renders it; session start uses the render. |
| 3 | Two sessions allocate the same id. | Survives | Fetch before allocate; a true collision is a push rejection. |
| 4 | Planning and executing sessions edit the same row file. | Survives | Sequential by state (`planned` before execution); the fence keeps id/title immutable. |
| 5 | The transition commit cannot be checked against a base that has only the table. | Confirmed | `read_rows(at=)` falls back to the table at that commit; also serves upgrading instances. |
| 6 | git merges append-only tables cleanly. | Refuted | Neighbouring-line conflicts on every row edit; this session rebased ledger commits repeatedly. |

Local: 50 tests pass; render 95 rows; dwork_link passes against `origin/main` via the fallback.

## Rule-5 pairwise (Rule-16 added; Rule-3 edited)
- 16–3: Rule-3 owns lifecycle and fence semantics, cites Rule-16 for storage; Rule-16 names
  the fence it relies on; one-way each for what it does not own. 16–15: plan files unchanged.
  16–1: store stays agent zone. Others unchanged. Coherent, orthogonal.
- 2026-09-13, ledger #115 (T4): Store bullet 3 reworded from a session property to Rule-15's
  phases; 16–15 one-sided per object (15 owns the split and the transition, 16 the file), named
  in the new Boundaries bullet. See `agent-corpus/falsification/t4-phase-wording.md`.
## Rule-6: `row file`, `rendered view` added; `ledger` changed — users 2, 3, 4, 5, 16 read correctly.

Disposition: see ledger #106.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
Store and Enforcement name the row guard `dyad/guards/agent/rows.py` (was `main_fence.py`) and the PR guard `prs.py` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
Store bullets on id allocation, hand edits, the append-only fence and phase-ordered edits moved to
`crafts/sysarch/rules/stores.md` as the file-per-instance pattern (plan #160 D2, attack 13); the canonical path and the
transition table stay (#159: operator-craft semantics); Enforcement states the fence's three checks. Pairwise: 16–3, 16–15
unchanged; 16–11 the pattern is the craft's, the path Rule-16's. Coherent, orthogonal. Disposition: see ledger #160.

## Amendment — d-work #185 (2026-09-14, session presence store)
| # | attack | result | survivor |
|---|---|---|---|
| 1 | A lock/reservation on a row is simpler than presence + inference. | Refuted | Rule-16 already rejects locking for the store (disjoint files, collision only on id); a lock needs release semantics and risks a permanent block if a session ends without one — nothing here guarantees a clean session-end hook. |
| 2 | The harness's own session directory already shows this. | Survives, scoped | It shows session identity and live status, not which files a session's *current* d-work touches; platform-level, ephemeral, unreadable by a fresh session reading only the corpus. |
| 3 | A presence file can go stale. | Survives, scoped | Advisory only, never a guard FAIL; `seen` lets a reader judge freshness. |
| 4 | Row-id overlap is the wrong signal: the near-miss that prompted this was two *different* row ids about the *same file*. | Confirmed | The store lists files (from each row's stored plan), not just row ids; the check that matters is file overlap. |
| 5 | Semantic overlap detection needs real code. | Refuted | Not mechanized: the mechanism is write/read the store; judging whether an overlap matters stays inference, as Rule-5 and Rule-9 already work. |
Pairwise: Rule-3 gains one sentence on the session-start report; Rule-6 gains one vocabulary row (`presence file`, owner 16); no other Rule's concern moves — the store is Rule-16's own (d-work store), the guard checks shape only (Rule-12's concern, delegated), overlap judgment is Rule-9's kind of inference, not a new one. Coherent, orthogonal. Disposition: see ledger #185.

## Addendum — d-work #185 (2026-09-14, same-root as a sharper signal)
Operator directive after the plan-Y: verify the store distinguishes multiple sessions started
from the same working directory, not only file overlap. Confirmed live during this d-work's own
execution — a peer session's direct `git merge`/`git reset --hard` in the shared checkout landed
on this session's uncommitted commits while both were mid-work in the same directory; recovered
without loss, but by neither party's tooling. `root` (the resolved working-tree path) added to
the presence file; `same_root()` flags a live session sharing it, reported by `touch` and `list`.
Never a guard FAIL — same discipline as file overlap: the mechanism surfaces the finding, the
Agent (or Operator) decides to move the work into a worktree. Pairwise unchanged: still Rule-16's
own store; no other Rule's concern moves. Disposition: see ledger #185.

## Amendment — d-work #37 (2026-09-16, `archived`)
Transition table gains `done → archived; archived → none`; the store sentence names `archived` as
`done`'s one further step, itself terminal. Attacks and pairwise: Rule-3's record, amendment #37
(attacks 1, 3, 5). Disposition: see ledger #37.

## Amendment — d-work #290 (2026-10-14, `backlog → archived`, an optional `mode`, and what a plan-less row costs the presence store)
**Claim (Operator, 2026-10-14, plan #290 revision 5):** the transition table has no exit from where
most of the board is. Store gains `backlog → archived`, and `dyadlib.TRANSITIONS`
(`dyad/scripts/dyadlib.py:443-450`) gains the same edge in the same commit —
`dyad/tests/test_dyadlib_rows.py:17-28` (`test_rule_16_bullet_enumerates_transitions`) parses the Store
sentence out of this Rule's text and asserts it equals the table, so the Rule and the code cannot diverge. The disposition that uses it is Rule-3's
**retirement form**, `Y/N: archive #a, #b, … #k?`, one Operator question over k rows, executed
clerically by `dyad dwork state <id> archived`, the verb the store already has. Two further changes belong to this store and are
attacked below: Store gains one **optional** field, `mode` (`explicit` or `implicit`, Rule-3
Scope), and Presence gains the sentence that says what an accreted row costs the `files` union.

Measured, at `main` 6ca6827: **`archived` has 0 uses in 280 rows**; **75 rows are `backlog`**, median
age **21 days**, 44 of them ≥14 days, the oldest 30; of the 37 rows ever born with a `Y backlog` first
entry, **35 are still `backlog`** — a **5.4% drain** — and `TRANSITIONS["backlog"]` is
`frozenset({"open"})`, so a surfaced row can only be retired by being *worked*.

| # | attack | result | survivor |
|---|---|---|---|
| 7 | A new edge reopens the promise this Rule's `#37` amendment bought: "state never regresses". | **Refuted.** `backlog → archived` moves away from work, never back toward it, and `archived` stays terminal. Both invariants hold untouched: `archived-is-terminal` (`not TRANSITIONS["archived"]`) and `done-never-reopens` (`TRANSITIONS["done"] == frozenset({"archived"})`), `dyad/scripts/dyadlib.py:597-598`. No state gains a successor it did not already have in the other direction. |  `archived` keeps exactly one meaning — retired from the working board — reachable now from the two states that can hold a row forever, `done` and `backlog`. |
| 8 | Then allow `backlog → done` too, and the parent gate's problem disappears without a new edge. | **Refuted.** `done` is the Operator's verification that a d-work's intent was delivered (Rule-3 Completion); a `backlog` row has delivered nothing, and `blocked → done` is refused for the same reason. Retirement says "this will not be worked", which is a different fact and needs its own state. | Two distinct exits, neither pretending to be the other: `done` for delivered work, `archived` for retired rows. The parent gate's own fix is Rule-3's — it accepts a `backlog` child — and is not smuggled in here. |
| 9 | An archive is a view: filter the board by age or by id and no state is needed. | **Refuted, and already refuted once** — this Rule's `#37` amendment, attack 2: age needs a clock, which a projection may not have (`crafts/syseng/rules/determinism.md`), an id cutoff is arbitrary, and "retired" is a fact about the row. Cited, not re-litigated. | The state stays stored, and nothing moves: the row file, its plan and its record stay where they are (Rule-20 resolves them as before). |
| 10 | The Agent will retire rows to tidy the board, which is the board becoming the Agent's to curate. | **Refuted by the same route as `#37` attack 4.** An Operator disposition names the rows; `dyad dwork state <id> archived` is clerical execution of it and a ledger-only commit, and no new verb is added — the one the store already has gains one legal source state. The Agent proposes the set and may never archive on its own judgment. | The retirement form is a counter-prompt, so the one question is the Operator's and the set is readable in it. |
| 11 | One question over k rows is a rubber stamp, and k could be 75. | **Survives, scoped.** It is Rule-3's batch discipline applied to a new class: a `Y` ratifies exactly the named set and `N` authorizes none of it, so the cost of a doubt is one re-reading of a list the Agent must still write row by row. The alternative is priced: clearing #259's 23 children one question at a time is 47 dispositions strictly one-per-question. | No ceiling is set here — the number of rows one retirement question may name is the Operator's, as the mandate ceiling is. |

| 12 | The row's fields are closed: `dyadlib.FIELDS` is `('id','title','opened','state','disposed','refs')` (`dyad/scripts/dyadlib.py:439`), pinned by a pure import-time invariant in the row guard (`dyad/guards/agent/rows.py:38-39`) and by `row-fields-match-dataclass` (`dyadlib.py:600`), so a seventh field either breaks the invariant or is silently dropped. | **Confirmed, and it chose the field's shape.** An extra `key: value` line parses clean today and is dropped, which is worse than refusing it. A seventh *required* field would also rewrite 280 row files to say what every one of them already means. | `mode` is **optional**: absent reads `explicit`, so no row is migrated and every row written before the field existed reads correctly; a row that carries it never loses it (the fence's own rule). The six required fields and their invariant are untouched, which is why this is one Store bullet and not a field-set change. |
| 13 | The presence store is unaffected by a row that has no plan file. | **Refuted, and it is this design's cost to this Rule.** `sessions.touch_from_open_rows` (`dyad/guards/agent/sessions.py`) builds `files` from the stored plan files of the session's `open` and `planned` rows (Rule-15 phase 1). An accreted row has none, so it appears in `rows` and contributes **nothing** to `files` — a reduction in exactly the coverage #185 built this store for: two sessions on *different* rows about the *same* file. | Stated in Presence, not fixed: the files are named in the **mandate's** plan file, which the mandate's own row carries while its children work, and reading a child's files through its `refs: parent #N` is the follow-on #290's plan names. Never a guard FAIL, as nothing in this store is. |

**Pairwise (Rule-5).** **16–3**: Rule-3 defines the states and the retirement disposition, Rule-16 the
store and the table — one-way each, as `#37` left them. **16–15**: the row file gains the optional `mode` field and the mandate pointer in `disposed`, and
attack 13's loss is a consequence of Rule-15 phase 2's plan-less row — Rule-15 owns the plan file,
this Rule owns the store that cannot find one. **16–2**: a
retirement is an Operator disposition Rule-2 already covers through Rule-3's reference; no event is
declared here. **16–1**: the store stays agent zone and a retirement is ledger-only. **16–7**: a
retirement writes one `disposed` entry and one record entry, so property 5's per-commit count holds
with no change. **16–12**: the table's test couples the Rule's sentence to the code
(`test_dyadlib_rows.py:17-28`), and the fence's own tests gain the new edge. **16–20**: nothing moves,
so every reference resolves as before. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #290.

## Amendment — d-work #294 (2026-10-15, the optional `host` and `holder` lines of the presence file)
**Claim (Operator, 2026-10-14, extending #293 mid-turn; plan #294 revisions 1–2):** every session
registration record carries host information — terminal vs. cloud, the OS — and, per #295's survivor,
names who holds the seat now. The record is the presence file (the one per-session store there is);
`touch()` (`dyad/guards/agent/sessions.py`) writes `host: <kernel> <os> <arch>` and, when
`CLAUDE_CODE_SESSION_ID` is set, `holder: <harness session id>`; `check_record` judges both only when
present; `FIELDS` and its invariant `fields-are-five` are untouched.

| # | attack | result | survivor |
|---|---|---|---|
| 14 | The kernel token is one harness's word: `CLAUDE_CODE_REMOTE` is Claude Code's variable, and Rule-14 property 2 says a kernel's own facts are never the dyad's. Another CLI agent never sets it and every session it runs reads `terminal`. | **Survives, scoped.** The Rule sentence says whose word it is — *what the harness reports*, `terminal` when it reports nothing — so a wrong token is visible on the board and is the harness row's defect, not the store's. The OS and arch come from `platform`, which holds on any kernel. | The field states what the environment says, never what the host is; the guard checks shape (three tokens, kernel in {`terminal`, `cloud`}), never truth. |
| 15 | Make `host` and `holder` required fields: cleaner than two more "when present" clauses. | **Refuted.** 66 presence files on `main` lack them and would redden `check` in every session until each re-touched — and a `holder` cannot be required at all, since a harness that sets no session id has nothing to write. `writer` set the precedent (#32): optional, checked only when present. | Both optional; `FIELDS` and `fields-are-five` unchanged. Promotion later is a one-line change once every live file carries `host`. |
| 16 | A typed line in the row title, or a hand-added key, lands today with no code. | **Refuted.** A title is immutable prose the Agent typed about itself, and #293's plan already found that a hand-added key does not survive the next `touch()`, which rewrites the whole file. A session cannot be trusted to describe its own host; code reading the environment is the Rule-12/Rule-13 path, and the test pins the kernel token under a patched environment. | Code-written at every touch, never typed; the Rule sentence says so. |
| 17 | `holder` duplicates `writer`. | **Refuted.** `writer` is this *process's* random id, computed at import to detect two processes sharing one `DYAD_SESSION` (#32); `holder` is the *harness's* session id, the thing a reader can cross-check against the harness's own session directory (this record, amendment #185 attack 2). One is for collision detection, the other for naming the seat's current occupant. | Both kept, each with its one job. |
| 18 | `platform.machine()` or `platform.system()` can return an empty string or a value with spaces, breaking the three-token shape the guard requires. | **Confirmed, and it chose the writer's shape.** `host_line()` substitutes `unknown` for an empty value and collapses a space inside a token to `_`, so a line it writes always parses back to exactly three tokens. | The writer guarantees what the check demands; `test_touch_writes_host_*` asserts the token count. |

**Pairwise (Rule-5).** **16–3**: Rule-3 reads the presence file at session start as before; nothing in
what it reports changes. **16–7**: no prompt or disposition is written here — the presence file is not
a provenance record. **16–14**: the kernel token is read from a harness variable but the manifest gains
no row and nothing is pinned — Rule-14 property 2 is what scopes attack 14, not what it edits. **16–15**:
the plan file is untouched; `files` is built as before. **16–12**: the guard's new branches carry their
tests (`dyad/tests/guards/agent/test_sessions.py`, `HostAndHolderTests`). **16–1**: agent zone, one PR.
Others unchanged. Coherent, orthogonal.

**Rule-6 term check.** No term added. `presence file` (owner 16) gains "and, when written, its holder's
host and harness session id"; its users, Rules 3 and 16, still read correctly — Rule-3 names the file at
session start, Rule-16 defines it. `dyad/guards/agent/vocabulary.py` passes.

Disposition: see ledger #294.

## Amendment — d-work #379 (2026-10-22, #369 C7: the seat name and its form)
**Claim (plan #369, revisions 1, 4, 10, 12; the Operator's prompts of 2026-10-21):** a presence file's
name is a seat name with a form, `<function>[-<topic>]-<hp>`, read under the `organization` preference;
the form's table is the organization craft's data, the core keeps the form's existence and an advisory
reading, and `dyad session name` prints the name and the harness session title from the environment.

| # | attack | result | survivor |
|---|---|---|---|
| 27 | A form in the core for a craft's organization re-opens the Rule-11 p2 overlap revision 2 refuted: a core-only install names a form it cannot check. | Refuted, as revision 4 attack 2 was: Rule-19's precedent — the core keeps existence and the advisory line, the craft's `seat` guard the check; `seat_form()` reads the craft's data when installed and the bare regex otherwise, and a craft whose data does not load falls back too. | Kept. |
| 28 | `touch()` warning on every historical name (`cos.md`, `cab-2-8c27a6fd.md`, 75 files) makes the warning noise. | Refuted: `touch()` judges the name it writes, never the store; the store's state check stays well-formedness only (Enforcement), and the craft's guard counts the old names in one line. | Kept: one line, on this session's own name. |
| 29 | Under `flat` the form is meaningless, so the preference has one value. | Survives, scoped, as revision 1 scoped it: `flat` reads no form and warns on nothing; `m4` reads it. Two behaviours, two values; the default is the Operator's `m4`. | Kept. |
| 30 | `dyad session name` derives the system handle `(ds)` from the repository directory's initials — a guess. | Conceded as a convenience: `--system` overrides it, the line is printed for the Operator to paste, and nothing reads it back. | Stated in the help. |
| 31 | The `<hp>` check compares the name to `holder()`, which is what the process says (#295). | Conceded, as #295 conceded: the mismatch it catches is the honest one — a renamed session, a reused file — never a lie. | Kept. |
| 32 | #350 (PR #425) changes `touch()` and adds `title()` in the same file. | Survives as a sequencing fact: the additions here are three functions and one loop after the write; whichever lands second rebases, stated in the completion evidence. | — |

**Pairwise (Rule-5).** **16–2**: advisory, no ratification event. **16–3**: Rule-3 reads the preference for
what a session reads at start and cites the Guide; Rule-16 for the name — one owner each. **16–6**: three
terms added (`seat name`, `cos-board`, `member-cos`, owner 16, used by 3 and 16); the craft's six are
referenced by craft name. **16–11**: the form's table is craft data, the core keeps a bare regex; no craft
path is written by the core. **16–12**: every branch carries a test (`test_sessions.py` `SeatNameTests`).
**16–14**: `CLAUDE_CODE_SESSION_ID` and `CLAUDE_CODE_REMOTE` are read as #294 reads them; nothing pinned.
**16–19**: the existence-plus-advisory split is Rule-19's own. Others unchanged. Coherent, orthogonal.

**Rule-6 term check.** `seat name`, `cos-board`, `member-cos` added; `seat`, `holder`, `presence file` still
read correctly for Rules 3 and 16. `dyad/guards/agent/vocabulary.py` passes.

Disposition: see ledger #379 (accreted under mandate #369; Done rides its Done-`Y`).

## Amendment — d-work #393 (2026-10-22, children 1–3 of #388: attendance, mode and route, derived)
**Claim (plan #388, the Operator's `Y` of 2026-10-22, batch #385,#388):** whether an Operator sits at a seat is
derived from the provenance records — a disposition given in the seat, within a window — never declared; over
the live seats it reads as M3, M4 or hybrid; a seat's counter-prompt is routed by it.

| # | attack | result | survivor |
|---|---|---|---|
| 33 | A declared line (`attended: yes`) is simpler. | Refuted, as plan #388 refuted it: a declared line is a claim nobody verifies (#295); a disposition in the seat's own record is the one act that proves an Operator was there, and Rule-7 already records it. | Derived on every read; nothing written. |
| 34 | "The leader is attended by definition while any seat is" is circular when no seat is. | Scoped: with no attended seat the reading is M3, the degenerate one-pair case (a leader alone, relaying to no one); `attendance()` says so. | Stated in the docstring. |
| 35 | A seat whose rows were opened without `DYAD_SESSION` has records with no `session:` line and reads unattended whatever the Operator did there. | Confirmed as a cost, and true of this seat: its own rows (#377–#379, #393) carry no `session:` line. The reading is honest — no Operator has disposed in this seat's chat — but a seat that wants its attendance read must open rows under its `DYAD_SESSION`. Stated here and in the Guide (counsel's child 4). | Kept; the `dwork new` path already writes the line when the variable is set. |
| 36 | The WHO column of a board gains `attended`/`relayed` (child 2), but the core has no board verb: `dyad dwork board` does not exist; the boards are the sysarch kanban projector and ledgerd (#336). | Confirmed; survivor: the functions a board reads (`attendance`, `attended`, `route`) are the core's here; the column lands in whichever board exists, under that board's own row — the kanban projector is sysarch's (craft zone), ledgerd's is #336's. A departure from plan #388's wording, stated. | `dyad session list` carries the reading meanwhile. |
| 37 | The window slides, so hybrid flips. | Conceded as plan #388 conceded: the mode is a reading, the route is decided per question from the records as they stand. | — |

**Pairwise (Rule-5).** **16–7**: the records are read, never written or re-shaped; Rule-7 owns them. **16–3**: where a
question is asked is Rule-3's counter-prompt forms unchanged; this says only which chat, by the record. **16–2**: a
relayed answer is still the Operator's `Y`, bound as Rule-2 binds it. **16–6**: one term, `attended`, owner 16.
**16–12**: `AttendanceTests`. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #393 (accreted under mandate #388; Done rides its Done-`Y`).

## Amendment — d-work #414 (2026-10-25, child C2 of #412: attendance declared, the records its check)
**Claim (plan #412, the Operator's `Y` of 2026-10-25):** the Operator's constraint is how many seats it attends, not
how many run; the program seat tracks which seats beside it the Operator attends; by default only the program seat is
attended, and that default is a preference. Survivor of plan #412's attacks 1–5: attended = the leader ∪ the seats
`attended-seats` declares (default `none`); the record-derived reading of #393 stays, as the check of the declaration.

| # | attack | result | survivor |
|---|---|---|---|
| 38 | Attack 33 refuted a declared line as "a claim nobody verifies" (#295); a declared preference is the same claim. | Refuted in scope: #295's objection is to an unverified line a *seat* writes about itself. The preference is the Operator's own word in its own zone, disposed by its own PR (Rule-2, *Not ratification*), and the records still verify it: an undeclared live seat holding an own disposition prints `undeclared`, a declared seat holding none prints `warn`. | Declared by the Operator, checked by the records; nothing a seat writes. |
| 39 | A seat name carries `-<hp>`, the holder's harness id (#379), so a declared name dies with its holder and the Operator re-declares on every handover. | Confirmed; survivor: an entry also matches a seat name with its `-<hp>` removed (`counsel` declares `counsel-0032b4c0` and every later holder). The full name stays admissible for a declaration of one holder. A reading of plan #412's "seat names", stated as such in the completion evidence. Consequence (counsel, on #459): a bare entry declares every concurrent seat of that function and topic, so the Operator's span is the matched live seats, never the entry count; `dyad session list` counts the seats. | `declares()` in `sessions.py`. |
| 40 | The check fires on every seat that holds a disposition from before the preference existed: run on this repo on 2026-10-25, thirteen stale cabinet seats of 2026-10-21 printed a line. | Confirmed; survivor: the `undeclared` line is read over the live seats, as the mode is — a seat past the stale window is off the board, and a live relayed seat holding a fresh own disposition is the case #407 names. The warning reads every entry against every record, live or not, because a declaration outlives a seat's presence file. | `undeclared` from the relayed live seats only. |
| 41 | "The leader is attended by definition while any seat is" (attack 34) now reads as always, so a lone leader with no record is M4 (every live seat attended). | Refuted by the order of the test: only leaders attended reads M3 first, which is the default and the one-pair case; M4 needs a declared non-leader seat. | `mode` tests M3 before M4. |
| 42 | The route still follows the record (an undeclared seat the Operator disposed in gets `chat`). | Refuted: the route follows the declaration alone — an undeclared seat is `relayed` whatever its record holds, and the record's disagreement is the `undeclared` line. The Operator sees one reading, and the fence says where it and the record part. | `route()` reads `attended`, which is the declared set. |
| 43 | Two spans conflate (plan #412 attack 4): the leader's ≤ 7 direct lines (MANDATES.md) and the Operator's attended seats. | Refuted as plan #412 refuted it: different numbers over different sets. The Rule's sentence names only the Operator's span; the leader's is the organization craft's Guide (craft PR of this child). | — |
| 44 | `own_disposition()` excludes a `relayed via` note, but no disposition can carry one: `dyad dwork` refuses `--relayed-via` without `--prompt`, and the vocabulary's `relayed prompt` never attaches to `--said`. So a relayed `Y` written into a record whose `session:` names a member seat counts as that seat's own disposition (counsel, on #459). | Survives, scoped: sound only while every relayed disposition is written into a record whose `session:` is the leader's — #388's route, and the convention every seat follows — and nothing checks that. The convention is the fence; the `relayed via` branch is dead for dispositions and is kept only for a record written by hand. | Stated; no code change. |
| 45 | The board printing `incident` collides with Rule-3's term (vocabulary, owner 3): every seat reading the board would report one Rule-3 incident per seat for one Operator disposition, against Rule-3's session-start bullet ("when it bears on the prompt at hand"), and the act is the Operator's, not an Agent's (counsel, on #459). | Confirmed; survivor: the token is `undeclared`, no defined term, and the leader alone reports it (16–3 below). | `fence_lines()`, Rule-16 Presence, the vocabulary row `attended`. |

**Pairwise (Rule-5).** **16–7**: the records are read, never written; Rule-7 owns them. **16–2**: a preference value is the
Operator's to dispose (C1, #413, its own preferences-zone PR); Rule-16 reads the value on `main`. **16–3**: the counter-prompt
forms are unchanged; this says only which chat. The printed token is `undeclared`, not Rule-3's term `incident`
(attack 45): it is a reading of the board, the act it shows is the Operator's, and its one reporter is the leader,
which #412 makes the tracker of attendance — no member seat reports it, so one disposition is never several incidents. **16–6**: `attended` amended, owner 16,
used by 16; no new term (`attended-seats` is a preference key, defined in `preferences-corpus/`, Rule-6 Boundaries).
**16–12**: `AttendanceTests` gains the default, the declared seat, the `undeclared` line and the warning. Others unchanged. Coherent,
orthogonal.

Disposition: see ledger #414 (accreted under mandate #412; Done rides its Done-`Y`).

## Amendment — d-work #419 (2026-10-25, child C2 of #417: the cabinet craft's terms and paths in Presence)
**Claim (plan #417, the Operator's `Y` of 2026-10-25; #416 revision 2 and prompt 4):** the craft `cos` is renamed
`cabinet`; `member-cos` → `secretary`, the topic seat a desk, `cos-board` unchanged. Presence names the craft's new
paths; `sessions.seat_kind` reads `secretary` and `desk`, as the craft's `seats.py` does (#418).

| # | attack | result | survivor |
|---|---|---|---|
| 46 | The vocabulary row `member-cos` said "one of the at most seven lines the leader reads"; with desks unbounded (#416 prompt 4) a reader may take the seven to cover desks. | Refuted in scope: the row is `secretary`'s, and the leader reads secretaries, never desks (the craft's §1, #418). | The `secretary` row says a secretary opens desks as its concurrent work needs. |
| 47 | The plan's preamble names `secretary` among the cabinet craft's terms, but the core already defines the role term (as `member-cos`, owner 16), and a craft term equal to an Agent term is one fault (`check_craft`). | Confirmed as a plan inconsistency; survivor: `secretary` stays the core's row, owner 16, used by 3 and 16, because Rules 3 and 16 use it. The preamble lists the cabinet craft's own six: charter, cos, desk, roll-up, function, topic. A stated departure from plan #417's wording. | VOCABULARY.md preamble. |
| 48 | The plan order C1 → C2 → C3 is unpushable: the bundle guard fails C1 ('cos': not a craft in this tree) and fails C3 alone (a released craft with no row). | Confirmed; an incident (Rule-3), escalated to the Operator through the program seat with a proposal (a Rule-11 property 7 sentence for a released craft that has left the tree). Recorded in `agent-corpus/audits/INCIDENTS.md` by this d-work's agent-zone PR. | The Operator's `Y` opened #423 (Rule-11 property 7: a released craft that has left the tree keeps its row, warned); #417's C1 stacks on it. |

**Pairwise (Rule-5).** **16–3**: Rule-3 uses `secretary` and `cos-board`; Rule-16 owns them. **16–6**: `member-cos`
renamed `secretary`, `cos-board` reworded, owner 16. **16–11**: the bundle order is Rule-11's (attack 48). Others
unchanged. Coherent, orthogonal.

Disposition: see ledger #419 (accreted under mandate #417; Done rides its Done-`Y`).

## Amendment — d-work #422 (2026-10-25, #421's HOW: the own-disposition clause reads the whole note)
**Claim (plan #422, opened on the Operator's Done-`Y` to #421):** the two exclusions `own_disposition()` relies on
are reachable by the CLI's own forms, so the board stops printing a false `undeclared` after every mandate close.

| # | attack | result | survivor |
|---|---|---|---|
| 49 | `own_disposition()` excludes a note that *starts* with `mandate #`, but every accreted row was closed with `dwork state <id> done -d 'Y done (mandate #<id>, <date>)' --said 'Y'`, whose note is `Y done (mandate #412, 2026-10-25)` (#413 entry 2): the copied Done-`Y` counts as a disposition given in the closing seat, and an undeclared seat prints `undeclared` after every mandate close. Attack 44's relayed branch is the same defect for a relay (no CLI form wrote the note). | Confirmed (#421). Survivor: the clause reads the note's whole text — a note holding `mandate #` or `relayed via` anywhere is not an own disposition — so the records already written read silent without rewriting (Rule-7 property 3); `dwork state <id> done --mandate <id>` writes the close under Rule-7 property 4's note, and `--relayed-via` with `--said` writes a relayed disposition's (Rule-7 record, amendment #422). Attack 44's convention is no longer the only fence. | `own_disposition()` in `sessions.py`; Presence's sentence "its note holding neither … anywhere"; `AttendanceTests` (three note forms × declared/undeclared, #413's record). |

**Pairwise (Rule-5).** **16–7**: the notes are Rule-7's; Rule-16 reads them. **16–3**: an accreted row's Done still rides
its mandate's (Rule-3 Scope); the close form only records it. **16–6**: `attended` reworded to the whole-note reading,
owner 16. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #422.
