# Run-book: sessions (the harness's session list against the presence store) — d-work #431, #626
# sections: Status/health, Seats, Harness, Tidy, Bootstrap

Instance: not a server. The harness's own session records (read through `dyad/scripts/hostadapter.py`, so another
kernel plugs in as data) against the presence store, `agent-corpus/d-work/sessions/<seat>.md` (Rule-16 Presence). The
harness side is The World and is never written; each presence file has one writer. Every command but `bootstrap` is
read-only: operate detects and reports, and the writer remedies (Rule-8 Conduct).

**Trigger.** Session start, and the program seat's request.

**Evidence.** A run with a new reading appends one event to `events/sessions.jsonl`, committed events-only (#438);
a repeated reading leaves none. A mismatch goes to operate's board; the audit seat reads the events.

## Status/health
Step: `dmc:sessions-health` over `dyad session reconcile` (its mismatch kinds: `dmc:session-reconcile`). Advisory,
never a guard failure. The postcondition is the pass, silent.
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: o=$(dyad/bin/dyad session reconcile 2>/dev/null) || { [ "$(printf %s "${CLAUDE_CODE_REMOTE:-}" | tr A-Z a-z)" = true ] && ! printf '%s\n' "$o" | grep -E '^(no presence|stale while titled|title differs):' | grep -v '(no title recorded)' | grep -q .; }
scope: agent-corpus/d-work/sessions/ and the harness's session records (read)

dyad/bin/dyad session reconcile
```

## Seats
The presence side: every seat's presence file, freshness, rows, holder and host, the attendance mode, and a same-root
flag, counted only when the `host` lines agree and, on a cloud kernel, the holders agree.
```dyad-cmd
name: seats
class: read-only
role: any
undo: none
postcondition: none
scope: agent-corpus/d-work/sessions/ (read)

dyad/bin/dyad session list
```

## Harness
The seat name with its form, the holder, and the harness session title the reconcile expects. Set `DYAD_SESSION` to
the seat whose title is read.
```dyad-cmd
name: name
class: read-only
role: any
undo: none
postcondition: none
scope: the environment and the harness's session title (read)

dyad/bin/dyad session name
```

## Tidy
The census of open sessions and the consolidation it proposes (play-book of plan #444). **North star:** the only
sessions open are live seats and live desks. A session is archived when every row it holds is `done` and its
presence is past the window, after the cos relays the Operator's `Y` naming the batch; a desk is closed by its
secretary when its topic's rows close.

The `census` command prints both sides: the reconcile reading, then every presence file with its freshness, rows
and holder. The Agent joins them to the harness list the cos transcribes from the Operator's UI — on a cloud
kernel each container sees only its own session (#434, attack 52) — and sorts each session into one class, by
plan #444's table:

| class | test |
|---|---|
| live seat | a charter row of `preferences-corpus/MANDATES.md` names it, presence within the window |
| live desk | a desk (`<function>-<topic>-<hp>`) holding an open or planned row, presence within the window |
| neglected | holds an open or planned row, presence past the window |
| done | every row it holds is `done` or `archived`, presence past the window |
| stale | holds no row, presence past the window |
| never registered | no presence file matches it by name or by `holder` |

The join is inference, stated: this is the play-book's first recurring task by hand, and its second run proposes a
`dyad session census` verb in the engineer's zone (Rule-13 property 1). **Pass:** every session is a live seat or a
live desk. Anything else goes to operate's board as one line per class and to the cos as a batch proposal, in this
order: done, stale and never registered first; then a charter seat with nothing open, alone; then the neglected,
only after the Operator disposes each row they hold, since a `planned` row cannot be archived (Rule-16) and an
archived session moves no row. Operate never archives, retitles or touches another seat's presence: archiving is
the cos's hosting action, Rule-8 reversible with the undo `unarchive_session`, one change-log row per call; a
terminal session the Operator closes by hand. Cadence: session start and on the program's request. A census is a
reading: under #438 an event is written only when it changes.
```dyad-cmd
name: census
class: read-only
role: any
undo: none
postcondition: none
scope: agent-corpus/d-work/sessions/, the ledger rows and the harness's session records (read)

dyad/bin/dyad session reconcile; dyad/bin/dyad session list
```

## Bootstrap
A seat's clone, prepared once at container start (`dyad bootstrap`, `dyad/scripts/bootstrap.py`): hook path, full
history, tags; idempotent, never blocking. The SessionStart hook that calls it is distribute's. Step:
`dmc:bootstrap-state`; the pass is no `warn` line from `--check`, the postcondition. After it, evidence then push from
the same clone with no fetch between: a tag fetch after `check --evidence` changes the suite memo's key (#473).
```dyad-cmd
name: bootstrap
class: reversible
role: any
undo: git config --unset core.hooksPath (fetched history and tags only add; nothing else to undo)
postcondition: ! dyad/bin/dyad bootstrap --check | grep -q '^warn '
scope: this clone's git config and fetched history

dyad/bin/dyad bootstrap
```
```dyad-cmd
name: bootstrap-check
class: read-only
role: any
undo: none
postcondition: none
scope: this clone's git config, shallow state and tags (read)

dyad/bin/dyad bootstrap --check
```
