# Rule-16: concurrent sessions

**Intent:** Store d-work state so that concurrent sessions on one instance touch disjoint
files and almost never merge.
**Target:** the d-work store

## Boundaries (out of scope)
- The d-work lifecycle, forms and fence semantics — Rule-3; the plan file — Rule-15.
- Zones — Rule-1 (the store stays in the agent zone). Who ratifies — Rule-2.
- Merging branches of code: git's, not this Rule's.
- The phase split itself (what each phase writes) — Rule-15.
- The store pattern — one file per instance, a rendered view untracked, ids allocated
  `max(origin, local)+1`, no hand edits, the append-only fence, phase-ordered edits: the sysarch
  craft's `crafts/sysarch/rules/stores.md` (#159, #160). Rule-16 keeps the canonical path and the
  transition table, which Rule-3's states and the fence rely on.

## Conditions (triggers)
- A d-work is opened, planned, disposed or completed: one row file changes.
- Two sessions push to `main`: the push rejects only a true collision on one id.
- A session starts: the ledger view is rendered, never read from the tracked tree.
- A row file changes state: the transition is in the table (Store, below).
- A session starts, records a plan-`Y` or opens a row for a row it owns, or reads the relay or notice that hands it
  a row: its presence file is touched (Presence, below).
- The agent is about to write a new plan file: every other session's presence file is read first.

## Store
- Canonical: `<instance>/d-work/rows/<id>.md`, one file per d-work, `key: value` lines
  (id, title, opened, state, disposed, refs). `LEDGER.md` is a rendered view
  (`package.py ledger`), untracked. The pattern this instantiates: `crafts/sysarch/rules/stores.md`.
- State never regresses. Transitions are exactly: open → planned, blocked, done, archived;
  planned → open, blocked, done; blocked → open; backlog → open, archived; done → archived;
  archived → none (`dyadlib.TRANSITIONS`; a new row starts `open` or `backlog`,
  `dyadlib.NEW_STATES`). The fence refuses any other transition on `main`,
  `package.py dwork state` locally; a done d-work is never reopened — a new row refs it;
  `archived` (Rule-3) is its one further step, itself terminal (#37). `backlog → archived` is the
  board's other exit: a row the operator never asked for is retired by the disposition that
  names it — the retirement form, or the done-`Y` of a delivered row whose Done question names it under `retires`
  (Rule-3, #585) — instead of being worked to `done` first (#290). `open → archived` is the intent question's: the fence
  admits it only on a row whose last `disposed` entry is a bare `N intent` and that holds no `Y plan`, so a row the
  operator declined before any plan leaves the board, and no other `open` row can (Rule-3 Answer grammar, #615).
- A row may carry two optional fields beside those six. `mode`, `explicit` or `implicit` (Rule-3,
  Scope): optional means absent is `explicit`, so every row written before the field existed reads
  correctly and nothing is migrated; a row that carries it never loses it. `slug`, the row slug (Rule-3): 2 to 4
  pieces joined by `-`, each of letters, digits or dots, the first opening with a letter, at most 32 characters
  (`dyadlib.SLUG`); written when the row is born, or once on a row that holds none, and never changed or removed
  after (`rows.slug_problems`); absent, the row has none.
- Beside the rows, the **board store**: `<instance>/d-work/board/<id>.md`, one file per row not terminal that has
  orchestration in flight, and one cross-row file per **cabinet** — `board/_cos.md` for `program`,
  `board/_cos-<operator>.md` for `program-<operator>` — for what crosses its rows (the pending queue's counts, the unit
  table with each unit's session id, the last question asked). `key: value` lines: `holder`, `owner`, `waiting-on`
  (`operator`, `unit <name>` or `external <ref>`; a stored `seat <name>`, the form before #553, fails the guard and
  `board set` refuses it, each naming `unit <name>`, #604), `next`, `since`, `question` (verbatim), `promised`, and `writer`,
  written by `dyad board set` as presence's is (#350), never typed; and an optional `cabinet`, absent meaning
  `program`, so no entry stored before it migrates — written once, when the entry is created, and never typed or
  changed. A cabinet's home writes only its own cabinet's entries and cross-row file, a unit's first entry is filed
  under the cabinet whose cross-row file names that unit (refused when that is ambiguous), `--drop` of a terminal
  row stays open to any unit, `dyad board resume` shows the resumer's cabinet alone, every notice the automaton or the sweep tells about a row
  goes to the home of that row's cabinet, and each cabinet's unit table is read from its own cross-row file (#594). Unlike a row it is **overwritten**, never
  append-only: it holds what is in flight now, and its history is git's. It is written by `dyad board set` as a
  ledger-only commit (Rule-3: it sits under `<instance>/d-work/`), read by `dyad board` and, after a **hop** — the
  session holding the board replaced by another — by `dyad board resume`, which prints what the new holder resumes.
  Its guard, `dyad/guards/agent/board.py`, checks only that each file is well-formed, names a row that is not
  terminal and carries `holder`; the warning that the last `writer` is not this session is the verbs', since a guard
  runs where "this session" means nothing. It is written write-ahead (Rule-3, Batch disposition) (#535). An entry
  may carry a `phase` — an **orchestration phase**, the entry's own machine beside the row's and never moving the row:
  `intent-asked` (under `intent-reading: on`, #615), `planning`, `plan-ready`, `plan-asked`, `building`, `verifying`,
  `done-ready`, `done-asked`, `landing`, or `held` —
  and a free-text `note`; the phases, the events that move between them, who fires each and the fields it must carry
  are data, `dyadlib.ORCH_EVENTS`, printed by `dyad board phases`. On a phased entry `phase`, `waiting-on`, `next`,
  `since` and `question` are derived from that table, and `dyad board advance <id>… <event> --expect <phase>` is their
  only writer: it refuses an event the table does not allow from the entry's phase, or a phase moved since `--expect`
  was read, and writes the derived fields, the templated relay to the next unit and, for an answer, the ledger entry and
  its provenance from `--said-file` (Rule-7), in one ledger-only commit, so a retry recomputes from `main` and never
  replays. The guard fails a phased entry whose derived fields differ from the table's; an entry with no `phase` reads
  as before. The automaton fires, from `main` alone, every event the table names it an actor of: `closed` once the
  merges have landed; `head-moved` when a PR's live head differs from the one a watched phase recorded, which takes back
  any question asked on it (Rule-2, Binding), and `withdrawn` for every other row a batch question named;
  `evidence-verified` or `evidence-failed` from `verifying`, from its own evidence run on the merge; and the catch-up
  `answered-Y` for a `Y` already recorded on `main` by hand. A recorded `Y` answers only the question it was given to:
  the catch-up, and any flip a `Y plan` implies, is skipped when the entry was written after the commit that recorded
  that `Y` (S11, `automaton.board_after_plan_y`) (#587).
- Beside the board, the **inbox**: `<instance>/d-work/inbox/<unit>/<stamp>-<from-unit>-<n>.md` (stamp
  `YYYYMMDDTHHMMSSZ`, UTC; `n` counting from 1 within one stamp and sender), one file per message, addressed by unit
  name and never by session id, so a hop changes nothing for the sender and concurrent senders never collide.
  `key: value` lines: `from`, `to`, `row`, `kind` (`report`, `relay`, `ack` or `notice`), `sent`, a verbatim `body`,
  and `writer`, written by `dyad inbox post` as presence's is (#350). Unlike the board it is **append-only**: a
  message is never edited or deleted, and reading it writes a marker beside it, the same name ending `.read`
  (`read`, `reader` — the box's own unit — and `writer`), so what was read and when is git's. It carries
  information, never authority: a body shaped like a disposition — a line opening `Y/N:`, a dated ledger entry
  (`<date> Y|N plan|done|release|backlog`), or a `Y plan (`, `Y done (` or `Y release (` entry — is refused at post
  and by the guard, because authority is read from the rows and the provenance store alone; a report therefore names
  the row whose entry it means and never quotes the entry. It is written by `dyad inbox post` (the sender is
  `DYAD_SESSION`) as a ledger-only commit — the same message to each `--cc` unit's box in that one commit (#572),
  and a post from the board's holder to a unit its entry does not yet name adds that unit to `owner` in the same commit,
  so the relay fence's write-ahead holds without a second write (#586) — read by `dyad inbox read` (its markers one ledger-only commit) and
  `dyad inbox list`, and its unread count is printed by `dyad board resume` and `dyad session touch`. Its guard,
  `dyad/guards/agent/inbox.py` (entity `message`), checks shape — `to` the box, `from` the sender in the name, `row`
  an existing row, no marker without its message — the refusal, and, on each commit pushed, append-only (#536).
- Beside the inbox, the **decision log**: `<instance>/d-work/decisions/<row>.md`, one file per row in the store
  pattern of the rows, the board and the inbox, one block per ruling the row's completion evidence names: a
  `## <case id>` heading, then `key: value` lines — `record`, `outcome`, `row`, `status` (`candidate` or `precedent`),
  `source` (`done`, `structured` or `two-readers`), `date` (the UTC date of the write), `precedent-entry` on a
  precedent block and, when a precedent set gave the outcome, `precedent-set` (that set's sha256, which admission refuses
  as self-derived); then one `field.<name>: <value>` per structured input and one `inputs: <prose>`. It is **append-only**: a block is never edited or deleted, and a status moves only
  from `candidate` to `precedent`, by a later block `## <case id> precedent` naming the `Y precedent` entry. It is
  written by `dyad dwork state … --decisions <file>` in the clerical commit that records the `Y` it rests on — a
  `Y done` writes `candidate` blocks, a `Y precedent` the blocks it admits (Rule-3, What a `Y` binds) — so it sits
  under `<instance>/d-work/` and is a ledger-only commit, and no `*.jsonl` is tracked there (Rule-7 property 2). Its
  guard, `dyad/guards/agent/decision_log.py`, checks shape, append-only, that each record is an existing decision
  record and each outcome one of its names, and that a `precedent` block names an existing `Y precedent` entry of its
  row (#644).

## Presence
- A session announces what it is working so another reads it *before* opening related work,
  never as a lock: `<instance>/d-work/sessions/<id>.md`, one file per session, only that
  session ever writes it — zero cross-session write conflict by construction, since no row
  file's append-only fence is needed here. `key: value` lines: `session`, `seen` (an
  ISO-8601 UTC timestamp), `root` (the resolved filesystem path of the working tree this
  session runs `dyad` from), `rows` (the space-list of d-work ids this session has open or
  planned), `files` (the deduplicated union of every `files touched:` line from those rows'
  stored plan files, Rule-15 — one signal that matters: two sessions on *different* rows about
  the *same file*, the near-miss this store was built to catch, d-work #185).
  An optional `writer` line, written by `touch()`, is the holder's harness session id when the harness
  reports one and a per-process id otherwise, so a session's own later `dyad` process matches it and
  only a different holder under the same `DYAD_SESSION` — the one way two sessions share a file, which
  nothing prevents — makes `touch()` warn and record only its own rows and files instead of unioning
  the other's: a warning, never a refusal (F1, d-work #32, #350).
  Two optional lines follow, written by `touch()` from the environment and checked only when
  present (never failing an absent one, as `writer` is handled): `host` (`<kernel> <os> <arch>`,
  the kernel token what the harness reports — `cloud` when it reports `CLAUDE_CODE_REMOTE=true`,
  `terminal` when it reports nothing — and the OS and arch from Python) and `holder` (the harness
  session id, `CLAUDE_CODE_SESSION_ID`, absent when unset): who holds the unit now, where the file's
  name is the **unit** (written seat before #553, `dyad/vocabulary/crosswalk.md`; `agent-corpus/falsification/seat-vs-harness-session.md`, #294, #295).
  That name is the **unit name**, and under `organization: m4` (`preferences-corpus/PREFERENCES.md`; `flat`
  is one pair and reads no form) it has a form, `<function>[-<topic>]-<hp>`: the installed organization
  craft's data where one is installed (`crafts/cabinet/guards/seats_rules.txt`, its `seat` guard the check)
  and the bare form of `sessions.py` otherwise; `touch()` prints one advisory line when a name is outside
  it, names a function the craft does not list, or carries an `<hp>` that is not the holder's, and
  `dyad session name` prints the name and the harness session title from the environment, setting
  nothing (#369 C7). What the names describe — the **home**'s board of programs (the home is titled cos there) and the board
  each unit with a function keeps over its charter's domain (the organization craft's `secretary` and `cos-board`) — is the organization craft's and its Operating Guide's
  (`crafts/cabinet/docs/operating-guide.md`), never this Rule's: this Rule keeps the form's existence and its
  advisory reading, as Rule-19 keeps a run-book's existence (#369 revision 4, attack 2).
  Which units an operator sits at is declared by the preference, checked against the records. The operator
  **pairs** a unit by naming it in the `paired-units` preference (`preferences-corpus/PREFERENCES.md`; default `none`;
  a table still holding the key's name before #553, `attended-seats`, fails the presence guard, naming `paired-units`, #604) and **unpairs** it by removing the name, by its
  unit name or by that name without its `-<hp>`. A unit is then of one kind: a **dyad unit** — the home always, and
  every unit paired — where the operator and the agent are both present and a live disposition is possible, said
  "dyad unit" whenever the system is also in view; a **solo** otherwise, where the agent works alone on authority
  carried verbatim from the ledger and its questions reach the operator through the home; or `auto`, an
  **automaton**'s unit — a non-inferring party running a released definition, the countersign model's executor —
  reserved, since no automaton keeps a presence file yet. Pairing changes a unit's
  kind and keeps its name and holder; a question already asked keeps the route the board recorded for it. Read over
  the live units this is a mode — every unit dyad, only the home, or some — which `dyad session list` prints with the
  paired set and each unit's kind and route, since a counter-prompt is asked in a dyad unit's own chat and relayed
  through the home otherwise (#253 R29; #388; #553). The check is the records': a unit holds an own disposition when a
  provenance record whose `session:` line names it holds a disposition given there — its note holding none of
  `mandate #<id>`, `mandate preference` or `relayed via`, anywhere (a mandate preference's entry copies a grant given
  elsewhere, Rule-7 property 4, #692) — within the `attendance-window` preference (default 7 days); a live
  unit holding one that is neither the home nor paired prints `undeclared`, a paired unit holding none prints `warn` —
  a reading of the board, not a Rule-3 incident: the act is the operator's, and the home alone reports it. The
  constraint the preference bounds is the operator's span — how many units the operator pairs — never how many units
  run (#412). No presence line is written for either: the preference is the declaration and the record the proof
  (#295).
- **Same root is the sharper signal.** Two sessions whose `root` is identical share one mutable
  checkout: a raw git command from either can clobber the other's uncommitted state regardless
  of which files either is editing — verified live during #185's own execution, when a peer
  session's direct `git merge`/`git reset --hard` in the shared checkout landed on top of this
  session's uncommitted commits (recovered without loss, but not by any mechanism here). Two
  sessions in separate worktrees of the same repo cannot collide this way even with identical
  `files`. `dyad session touch` reports a same-root session found; `dyad session list` flags one.
  Stated as the working discipline, not enforced: a session that finds this true moves its own
  work into a worktree rather than continuing to write in a checkout another session is using.
- Touched by `dyad session touch` at session start and at every plan-`Y` (piggybacked on the
  ledger commit already made then); read by `dyad session list` or directly. Advisory only: a
  session past the stale window, or one that ended without a clean write, is never a guard
  failure — a reader judges freshness from `seen`, and may cross-check the harness's own live
  session directory for whether the name is still active. `dyad session reconcile` makes that
  cross-check: it compares the live presence files with the harness's own session list, read through
  `hostadapter.harness_sessions()` (`dyad/scripts/hostadapter.py`), and prints one line per mismatch
  (`no harness session`, `no presence`, `title differs`, `stale while titled`) — advisory, a run-book's
  health command (the unit whose charter holds the host), never a guard failure; the remedy is the writer's (#434).
- **A plan-less row is invisible to the `files` union.** `sessions.touch_owned`
  (`dyad/guards/agent/sessions.py`) builds `files` from the stored plan files of the rows this unit
  owns — those it already claimed and those whose board entry names it an owner (#567); an accreted row (Rule-3, Scope) has no plan file of its own (Rule-15
  phase 2), so it appears in `rows` and contributes nothing to `files`. That is a reduction in
  exactly the coverage this store was built for — two sessions on *different* rows about the *same
  file* — and it is stated, not fixed here: those files are named in the mandate's own plan file,
  and reading a child's files through its `refs: parent #N` is the follow-on #290's plan names,
  not a mechanism this Rule yet has.
- Before writing a *new* plan file, the agent reads every other session's presence file and, if
  its `files` set overlaps the new plan's own touched files, states the overlap in the plan's
  falsification section as a finding — never a guard FAIL; the judgment of whether it matters
  stays inference, as Rule-5 coherence and Rule-9 falsification already work.

## Enforcement
The row guard (`dyad/guards/agent/rows.py`, the fence) for row files: append-only, ids and titles
immutable, transitions in the table, and new ids contiguous — on `main` and on a branch alike, the row ids a range
adds run from the base's highest id + 1 with none skipped, as the allocator writes them, so a skipped or hand-typed
id fails (`rows.contiguity_problems`, #560), and a row slug written at most once (`rows.slug_problems`, #622); the PR guard (`prs.py`) reads rows at the base commit; the
presence guard (`dyad/guards/agent/sessions.py`) checks only that a presence file is well-formed
(every field present, `seen` parses) — never overlap, never staleness (Presence, above); inference
for phase ownership and for whether an overlap the agent found actually matters.

## Provenance
Operator rule, 2026-09-13. Falsified; see `../falsification/rules/rule-16-concurrent-sessions.md`.
Store bullets on id allocation, hand edits, the append-only fence and phase-ordered edits moved to
`crafts/sysarch/rules/stores.md` 2026-09-14 (#160, D2); the kernel stays here. Presence store added
2026-09-14 (#185): a live cross-session near-miss — two sessions' rows both touching one guard
module, caught only because a peer chose to message first — falsified the claim that a session can
tell, from the corpus alone, what another concurrent session is currently working; survivor above.
Store gains `backlog → archived` and the optional `mode` field, and Presence the plan-less-row
sentence, 2026-10-14 (d-work #290): `archived` had been used 0 times in 280 rows while 75 sat in
`backlog` with one successor each, a 5.4% drain, and a row accreted under another row's mandate
carries no plan file for the `files` union to read; see the same record, amendment #290.
Presence gains the optional `host` and `holder` lines 2026-10-15 (d-work #294): the operator asked
that every registration record carry host information, and a seat's record names its current
holder (#295); see the same record, amendment #294. Presence gains the seat name and its form
2026-10-22 (d-work #379, #369 C7): thirteen live seats carried four naming conventions and two name
collisions (#368 §1), and a Rule reads a preference only if it names it; the form's table is the
organization craft's data and its reading stays advisory; see the same record, amendment #379. Presence gains
attendance, derived from the provenance records, and the mode it reads 2026-10-22 (d-work #393, children 1–3 of
#388): the relay between seats had been found to fit one attended pair at the leader with every other seat
unattended (#386), and nothing said which; see the same record, amendment #393. Presence's attendance
sentence turns from derived to declared 2026-10-25 (d-work #414, child C2 of #412): the operator's constraint is how
many seats it attends, not how many run, and by default it attends only the leader, a preference; the record-derived
reading stays as the check of the declaration; see the same record, amendment #414. Presence's
seat-name sentence names the cos, a secretary and the cabinet craft's paths 2026-10-25 (d-work #419, child C2 of
#417): the craft `cos` is renamed `cabinet`, `member-cos` becomes `secretary` and a topic seat a desk; see the same
record, amendment #419. Presence's own-disposition clause reads the note's whole text 2026-10-25 (d-work #422): every
accreted row's close had been noted `Y done (mandate #<id>, <date>)`, which the reading took for a disposition given in
the closing seat; see the same record, amendment #422. Presence gains `dyad session reconcile` 2026-10-25 (d-work
#434, child C1 of #431): the harness's list of sessions and the presence store had drifted apart with nothing to say
where, and the operate seat owns the check while the writer owns the fix; see the same record, amendment #434. Presence's
writer sentence 2026-10-25 (d-work #350, ported by #453 from PR #425): the F1 fence of #32 compared a uuid
computed per `dyad` invocation, so it warned on a session's own previous command and could not tell a second
holder from the same one; see the same record, amendment #350. Enforcement
names the row-id contiguity fence 2026-10-29 (d-work #525): the fence refused a range whose new ids skipped or were
typed by hand since #560, and no Rule named it; see the same record, amendment #525. Store gains the board
store 2026-11-02 (d-work #535): the orchestration in flight had no store, and a row, append-only and fenced, is the
wrong one for state overwritten many times a day; see the same record, amendment #535. Store gains the inbox
2026-11-02 (d-work #536): seats reported by message to a session id, so a report sent after a hop reached the old
session and a terminal holder could receive none (#546, S5, S6, S18, S26); see the same record, amendment #536. Store and Presence move to the
dyad-native terms 2026-11-02 (d-work #553): seat becomes unit, attended a dyad unit and the rest solo, toggling
`attended-seats` pairing (`paired-units`, the old key its alias), the leader the home, an automaton's kind `auto`
reserved; history keeps the old words and `dyad/vocabulary/crosswalk.md` maps them; see `../falsification/rules/rule-6-vocabulary.md`, amendment #553 (part D). Presence cites the organization
craft's roles and names the reconcile check's owner by charter 2026-11-02 (d-work #560): `secretary` and `cos-board` are the
cabinet's, and "the operate unit's" named an instance position; see the same record, amendment #560. Conditions'
presence trigger names the acts that hand a unit a row, and the plan-less-row bullet names `touch_owned`, 2026-11-03 (d-work #567): under `m4` the home answers every plan-`Y`, so
"answers a plan-`Y`" touched the home's file and never the owner's, and the files-overlap signal went stale; see the same
record, amendment #567. Store names the Done route of `backlog → archived`, `inbox post --cc`, and the holder's post that adds an
owner 2026-11-04 (d-work #585, carrying #572 and #586): the retirement form had been the only exit named, and two inbox
verbs had landed with no sentence; see `../falsification/rules/rule-3-d-work.md`, amendment #585. Store and Presence drop
the #553 aliases 2026-11-05 (d-work #604, H3 step 4 of #573): `seat <name>` and `attended-seats` are refused, naming their
new forms, after the 0.18.0 cut shipped their deprecation warnings; see the same record, amendment #604. Store's board
bullet gains the orchestration phase 2026-11-05 (d-work #587): owner, wait and next act were free text that drifted
from the work, and ten slips of one day (S1–S10) were each an unrecorded transition; see the same record, amendment #587. Store's board
bullet gains the cabinet 2026-11-05 (d-work #594, #548 S13): with two operators' homes on one instance, one shared
`_cos.md` let one home's queue and question overwrite the other's; see the same record, amendment #594. Store gains
`open → archived` and the board the `intent-asked` phase 2026-11-06 (d-work #615): a row the operator declines at its
intent question had no exit but a Done; see the same record, amendment #615. Store gains the optional `slug` field and
Enforcement its write-once fence 2026-11-07 (d-work #622): the row slug Rule-3 presents needs a home on the row; see
`../falsification/rules/rule-3-d-work.md`, amendment #622. Store gains the decision log 2026-11-08 (d-work #644): the rulings a
Done named were stored nowhere, so no precedent could be admitted or audited; see `../falsification/rules/rule-3-d-work.md`,
amendment #644. Presence's own-disposition clause excludes a `mandate preference` note 2026-11-12 (d-work #692, plan
revision 2): a row opened under `hardening-mandate` copies the grant's words into the unit that ran the verb, which the
reading took for a disposition given there; see `../falsification/rules/rule-3-d-work.md`, amendment #692.

Set: System Requirements.
