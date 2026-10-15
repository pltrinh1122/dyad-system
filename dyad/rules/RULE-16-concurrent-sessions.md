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
- A session starts, or answers a plan-`Y`: its presence file is touched (Presence, below).
- The Agent is about to write a new plan file: every other session's presence file is read first.

## Store
- Canonical: `<instance>/d-work/rows/<id>.md`, one file per d-work, `key: value` lines
  (id, title, opened, state, disposed, refs). `LEDGER.md` is a rendered view
  (`package.py ledger`), untracked. The pattern this instantiates: `crafts/sysarch/rules/stores.md`.
- State never regresses. Transitions are exactly: open → planned, blocked, done;
  planned → open, blocked, done; blocked → open; backlog → open, archived; done → archived;
  archived → none (`dyadlib.TRANSITIONS`; a new row starts `open` or `backlog`,
  `dyadlib.NEW_STATES`). The fence refuses any other transition on `main`,
  `package.py dwork state` locally; a done d-work is never reopened — a new row refs it;
  `archived` (Rule-3) is its one further step, itself terminal (#37). `backlog → archived` is the
  board's only other exit: a row the Operator never asked for is retired by the disposition that
  names it (Rule-3's retirement form) instead of being worked to `done` first (#290).
- A row may carry one optional field beside those six: `mode`, `explicit` or `implicit` (Rule-3,
  Scope). Optional means absent is `explicit`, so every row written before the field existed reads
  correctly and nothing is migrated; a row that carries it never loses it.

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
  Two optional lines follow, written by `touch()` from the environment and checked only when
  present (never failing an absent one, as `writer` is handled): `host` (`<kernel> <os> <arch>`,
  the kernel token what the harness reports — `cloud` when it reports `CLAUDE_CODE_REMOTE=true`,
  `terminal` when it reports nothing — and the OS and arch from Python) and `holder` (the harness
  session id, `CLAUDE_CODE_SESSION_ID`, absent when unset): who holds the seat now, where the file's
  name is the seat (`agent-corpus/falsification/seat-vs-harness-session.md`, #294, #295).
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
  session directory for whether the name is still active.
- **A plan-less row is invisible to the `files` union.** `sessions.touch_from_open_rows`
  (`dyad/guards/agent/sessions.py`) builds `files` from the stored plan files of this session's
  `open` and `planned` rows; an accreted row (Rule-3, Scope) has no plan file of its own (Rule-15
  phase 2), so it appears in `rows` and contributes nothing to `files`. That is a reduction in
  exactly the coverage this store was built for — two sessions on *different* rows about the *same
  file* — and it is stated, not fixed here: those files are named in the mandate's own plan file,
  and reading a child's files through its `refs: parent #N` is the follow-on #290's plan names,
  not a mechanism this Rule yet has.
- Before writing a *new* plan file, the Agent reads every other session's presence file and, if
  its `files` set overlaps the new plan's own touched files, states the overlap in the plan's
  falsification section as a finding — never a guard FAIL; the judgment of whether it matters
  stays inference, as Rule-5 coherence and Rule-9 falsification already work.

## Enforcement
The row guard (`dyad/guards/agent/rows.py`, the fence) for row files: append-only, ids and titles
immutable, transitions in the table; the PR guard (`prs.py`) reads rows at the base commit; the
presence guard (`dyad/guards/agent/sessions.py`) checks only that a presence file is well-formed
(every field present, `seen` parses) — never overlap, never staleness (Presence, above); inference
for phase ownership and for whether an overlap the Agent found actually matters.

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
Presence gains the optional `host` and `holder` lines 2026-10-15 (d-work #294): the Operator asked
that every registration record carry host information, and a seat's record names its current
holder (#295); see the same record, amendment #294.

Set: System Requirements.
