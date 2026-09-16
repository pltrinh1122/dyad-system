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
  planned → open, blocked, done; blocked → open; backlog → open; done → archived; archived → none
  (`dyadlib.TRANSITIONS`; a new row starts `open` or `backlog`, `dyadlib.NEW_STATES`). The
  fence refuses any other transition on `main`, `package.py dwork state` locally; a done
  d-work is never reopened — a new row refs it; `archived` (Rule-3) is its one further step, itself terminal (#37).

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

Set: System Requirements.
