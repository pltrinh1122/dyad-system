# Run-book: sessions (the harness's session list against the presence store) — d-work #431
# sections: Status/health, Seats, Harness

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
and prints one line per mismatch: `no harness session`, `no presence`, `title differs`, `stale while titled`
(plan #431 survivor; the command is #431 C1, `dyad session reconcile`, the engineer seat's). **Pass: no
mismatch line** — the postcondition greps the output for the four mismatch kinds and holds when none is
printed. The check is advisory (Rule-16 Presence: never a guard failure); a failed postcondition here is
operate's report to its board, not a fence.
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: ! dyad/bin/dyad session reconcile 2>/dev/null | grep -qE '(no harness session|no presence|title differs|stale while titled)'
scope: agent-corpus/d-work/sessions/ and the harness's session records (read)

dyad/bin/dyad session reconcile
```

## Seats
The presence side on its own: every seat's presence file, its freshness, rows, holder and host, the
attendance mode over the live seats, and a same-root flag (Rule-16 Presence). In a cloud container every
seat reports the same `root`; the flag then names a path two containers share by name and not by
filesystem, which is a reading to make, not a collision (found opening this seat, #431 H0).
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
