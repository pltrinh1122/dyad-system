# Run-book: sessions (the harness's session list against the presence store) — d-work #431
# sections: Status/health, Seats, Harness, Tidy

Instance: not a server — the agent application's own session records (Claude Code: `~/.claude/projects/<slug>/`,
one kernel's path, read through `dyad/scripts/hostadapter.py` so another kernel plugs in as data; plan #431
attack 4) read against the dyad's presence store, `agent-corpus/d-work/sessions/<seat>.md` (Rule-16 Presence).
Nothing here runs under a supervisor and nothing persists: the harness side is The World (Rule-14), a host
artifact the dyad observes and never writes; the presence side is written only by the seat that owns each
file (Rule-16, one writer). So this run-book's section set is its own (the `# sections:` line above; the
sysadmin craft's `server-instances.md` property 2 admits it) and every command is **read-only**: the
`operate` seat detects and reports (Rule-8 Conduct, detect don't dispose); remediation is the writer's — the
seat touches its presence file, the program seat retitles or archives the harness session — never a write of
this run-book's (plan #431 attack 2). Every command runs from the git root, `sudo`-free, as either party:

```text
dyad runbook list sessions
dyad runbook run sessions health
```

Operate runs `health` at every reply and on the program seat's request; each run leaves an event in
`events/sessions.jsonl` (server-instances rule, property 7), which the audit seat reads and grades (a seat
repeatedly `stale while titled` is an incident-hardening input, #409 G1; plan #431 revision 2) and never on a
cadence of its own. A mismatch goes to operate's board; the writer fixes it.

## Status/health
Health (the pass criterion for Done — server-instances rule, property 4; Rule-19 kernel): the reconcile
command compares the two lists both ways — for each live presence file a harness session whose title is the
seat's `dyad session name` form, and for each harness session titled in the seat form a live presence file —
and prints one line per mismatch (the command is #431 C1, `dyad session reconcile`, the engineer seat's, #434):
`no harness session: <seat>`, `no presence: <title>`, `title differs: <seat> (<title>)`, `stale while
titled: <seat>`, then a count line; exit 0 and one `ok [reconcile] … aligned` line when the lists agree. A
title matches on its `<seat>: <kernel> (<system>)` prefix, so a suffix the harness appends is no mismatch.

**Pass:** exit 0 — or, on a cloud kernel (`CLAUDE_CODE_REMOTE=true`), exit 1 whose mismatch lines are all of
the two kinds that kernel produces by construction: `no harness session: <seat>` and `title differs: <seat>
(no title recorded)`. Each cloud container's harness store holds only its own session and never the UI title
(#434, record attack 52), so in any one container every *other* live seat reads `no harness session` and the
seat's own reads `title differs (no title recorded)`: those two lines carry no information there and are not
read as failures; a `no presence`, a `stale while titled`, or a `title differs` with a title recorded still
fails. On a terminal kernel the harness store holds every session with its title and the criterion is exit 0
alone. The postcondition is that test; a hosting-side session list would be a further adapter behind
`hostadapter.harness_sessions()` and would retire the cloud clause — stated, not built here. The check is
advisory (Rule-16 Presence: never a guard failure); a failed postcondition is operate's report to its board,
not a fence, and the writer remedies.
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
The presence side on its own: every seat's presence file, its freshness, rows, holder and host, the
attendance mode over the live seats, and a same-root flag (Rule-16 Presence) — counted only when the `host` lines agree and, on a cloud kernel, the
holders agree, since every cloud container reports the same `root` by name and not by filesystem (found
opening this seat, #431 H0; #434).
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
The harness side for the seat running the command: the seat name with its form, the holder, and the harness
session title as the adapter reads it from the environment — the title the reconcile command expects to
match the seat's form. Set `DYAD_SESSION` to the seat whose title is being read.
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
