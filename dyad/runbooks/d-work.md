# Run-book: d-work (one d-work from its prompt to its Done-Y) — play-book `dyad/playbooks/d-work.md`, #299
# sections: Open, Plan, Authorize, Execute, Evidence, Complete, Defer, Resume

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the d-work play-book as `dyad-cmd`
blocks, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/d-work.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above). Every step that acts on a row takes its id from the environment — `DWORK`, the
play-book's parameter, with no default — and the Operator's words as files, verbatim: `SAID`, `PROMPT`
(Rule-7); a new row takes `TITLE`, `REFS` and `PROMPT`; a deferral takes `BLOCKER` and the full `REFS` the
row is to carry. Every step reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property
3) and runs from the git root. `plan`, `execute` and `evidence` are **read-only**; the others write the
ledger's own files and are **reversible** — their undo restores the files from `HEAD`, which is the
clerical commit's boundary. Retirement (`backlog` or `done` → `archived`) is `dyad/runbooks/disposition-digest.md`'s
`retire` step and is not repeated here. The native commands are the play-book's default (#247); this
run-book is for a step run through the runner by choice, which then leaves an event.

```text
DWORK=<id> dyad runbook list d-work
DWORK=<id> SAID=<file> dyad runbook run d-work authorize
```

## Open
A row born `open` on the Operator's prompt (the machine's first birth): the row file and its provenance
record, entry 1 the prompt verbatim. The postcondition is the birth's own idempotence — a row of this title
exists — so a repeat opens no duplicate; the undo removes the newest row and its record, the two files the
command wrote:
```dyad-cmd
name: open
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; N="$(basename "$(ls -t "$I"/d-work/rows/*.md | head -n 1)")"; rm -f "$I/d-work/rows/$N" "$I/d-work/provenance/$N"
postcondition: grep -lxF "title: ${TITLE:?row title}" "${DYAD_INSTANCE:-agent-corpus}"/d-work/rows/*.md | grep -q .
scope: <instance>/d-work/rows/<new id>.md and <instance>/d-work/provenance/<new id>.md (two new files)

dyad/bin/dyad dwork new "${TITLE:?row title}" "${REFS:-}" --prompt-file "${PROMPT:?prompt file}"
```

## Plan
The plan file's parts (Rule-15 phase 1, `dyadlib.PLAN_PARTS`), present or absent, before the counter-prompt
is asked. The plan itself is the Agent's inference and no command writes it:
```dyad-cmd
name: plan
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/plans/<DWORK>.md (read)

I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; f="$I/d-work/plans/$D.md"; test -f "$f" && { for p in "intent as read" "mutation" "files touched" "base commit" "falsification"; do if grep -qi "$p" "$f"; then echo "present: $p"; else echo "absent:  $p"; fi; done; }
```

## Authorize
The plan-`Y` (open → planned): the `disposed` entry and the record's `disposition` entry in one write, then
the presence touch Rule-16 asks for at every plan-`Y`:
```dyad-cmd
name: authorize
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"
postcondition: grep -qx 'state: planned' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance}/<DWORK>.md and <instance>/d-work/sessions/<seat>.md

D="${DWORK:?d-work id}"; dyad/bin/dyad dwork state "$D" planned -d "Y plan" --said-file "${SAID:?disposition file}" && dyad/bin/dyad session touch -r "$D"
```

## Execute
The PR transaction judged before a PR is opened (Rule-1 binds a commit and a PR; `dyad check --pr` is the
whole-diff `range` mode the Agent runs, since no hosted job judges a PR before it merges, #168):
```dyad-cmd
name: execute
class: read-only
role: any
undo: none
postcondition: none
scope: the checked-out branch's diff against origin/main (read)

dyad/bin/dyad check --pr origin/main HEAD
```

## Evidence
The evidence block of the exact head the Done question is asked on (Rule-14 property 3), pasted verbatim in
the completion reply (Rule-3):
```dyad-cmd
name: evidence
class: read-only
role: any
undo: none
postcondition: none
scope: the working tree at HEAD (read; runs every check and guard)

dyad/bin/dyad check --evidence
```

## Complete
The Done-`Y` (open or planned → done): the row and the record first, then the trace, so the Done ledger
commit carries all three (`dwork-trace.md`); the merges come after that commit and are not in this step:
```dyad-cmd
name: complete
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"; rm -f "$I/d-work/traces/$D.md"
postcondition: grep -qx 'state: done' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance,traces}/<DWORK>.md

D="${DWORK:?d-work id}"; dyad/bin/dyad dwork state "$D" done -d "Y done" --said-file "${SAID:?disposition file}" && dyad/bin/dyad dwork trace "$D" --out
```

## Defer
A deferral (open or planned → blocked) naming the blocking d-work, which the row's `refs` then carries —
`REFS` is the full list the row is to hold, the blocker among it, since `-r` replaces the field:
```dyad-cmd
name: defer
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"
postcondition: grep -qx 'state: blocked' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance}/<DWORK>.md

D="${DWORK:?d-work id}"; dyad/bin/dyad dwork state "$D" blocked -d "Y blocked #${BLOCKER:?blocking d-work id}" --said-file "${SAID:?disposition file}" -r "${REFS:?the row's refs, the blocker among them}"
```

## Resume
Back to `open`: from `backlog` on an Operator prompt, which the record gains as a `prompt` entry (Rule-7's
transaction check), or from `blocked` when the blocking d-work is done, which is clerical and brings no words:
```dyad-cmd
name: resume
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"
postcondition: grep -qx 'state: open' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance}/<DWORK>.md

I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; if grep -qx 'state: backlog' "$I/d-work/rows/$D.md"; then dyad/bin/dyad dwork state "$D" open --prompt-file "${PROMPT:?prompt file}"; else dyad/bin/dyad dwork state "$D" open; fi
```
