# Run-book: sessions (the harness's session list against the presence store) — d-work #431, #626
# sections: Status/health, Seats, Harness, Bootstrap

Instance: not a server. The harness's own session records (read through `dyad/scripts/hostadapter.py`, so another
kernel plugs in as data) against the presence store, `agent-corpus/d-work/sessions/<seat>.md` (Rule-16 Presence). The
harness side is The World and is never written; each presence file has one writer. Every command but `bootstrap` is
read-only: operate detects and reports, and the writer remedies (Rule-8 Conduct).

**Trigger.** Session start, and the program seat's request.

**Evidence.** A run with a new reading appends one event to `events/sessions.jsonl`, committed events-only (#438);
a repeated reading leaves none. A mismatch goes to operate's board; the audit seat reads the events.

Tidy: `dyad runbook run cabinet:session-tidy census`; play-book `crafts/cabinet/playbooks/session-tidy.md`. Archiving stays the cos's Rule-8 reversible act, one change-log row per call.

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

The census pointer: kept so the census events already recorded resolve (Rule-20); the census itself is the cabinet's.
```dyad-cmd
name: census
class: read-only
role: any
undo: none
postcondition: none
scope: agent-corpus/d-work/sessions/, the ledger rows and the harness's session records (read)

dyad/bin/dyad runbook run cabinet:session-tidy census
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
