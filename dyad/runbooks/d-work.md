# Run-book: d-work (one d-work from its prompt to its done-Y) — play-book `dyad/playbooks/d-work.md`, #309, #626
# sections: Open, Plan, Authorize, Execute, Evidence, Record, Complete, Defer, Resume, Mirror

The d-work play-book's steps as `dyad-cmd` blocks, run through the core runner, which records an event in
`<runbooks>/events/d-work.jsonl` and tests the postcondition. `DWORK` names the row, with no default; the operator's
words come as files (`SAID`, `PROMPT`, Rule-7); a new row takes `TITLE`, `REFS`, `PROMPT`, `SLUG`; a deferral `BLOCKER`
and `REFS`. `plan`, `execute` and `evidence` are read-only; the rest are reversible, undone from `HEAD`. Retirement is
`dyad/runbooks/disposition-digest.md`'s `retire`. The native commands stay the default (#247).

```text
DWORK=<id> dyad runbook list d-work
DWORK=<id> SAID=<file> dyad runbook run d-work authorize
```

## Open
A row born `open` on the operator's prompt (the machine's first birth):
```dyad-cmd
name: open
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; N="$(basename "$(ls -t "$I"/d-work/rows/*.md | head -n 1)")"; rm -f "$I/d-work/rows/$N" "$I/d-work/provenance/$N"
postcondition: grep -lxF "title: ${TITLE:?row title}" "${DYAD_INSTANCE:-agent-corpus}"/d-work/rows/*.md | grep -q .
scope: <instance>/d-work/rows/<new id>.md and <instance>/d-work/provenance/<new id>.md (two new files)

dyad/bin/dyad dwork new "${TITLE:?row title}" "${REFS:-}" --prompt-file "${PROMPT:?prompt file}" ${SLUG:+--slug "$SLUG"}
```

## Plan
The plan file's parts (Rule-15 phase 1, `dyadlib.PLAN_PARTS`), present or absent, before the counter-prompt is asked:
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
The plan-`Y` (open → planned):
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
The PR transaction judged before a PR is opened (Rule-1 binds a commit and a PR; `dyad check --pr` is the whole-diff
`range` mode the agent runs, since no hosted job judges a PR before it merges, #168):
```dyad-cmd
name: execute
class: read-only
role: any
undo: none
postcondition: none
scope: the checked-out branch's diff against origin/main (read)

dyad/bin/dyad check --pr origin/main HEAD
```
The PRs a Done question is about to name, judged together (#556):
```dyad-cmd
name: verify-prs
class: read-only
role: any
undo: none
postcondition: none
scope: origin/main and refs/pull/<n>/head of every PR in PRS (read)

PRS="${PRS:?PR numbers in merge order}" dyad/bin/dyad steps verify-prs
```

## Evidence
The evidence block of the exact head the Done question is asked on (Rule-14 property 3), cited in the completion
reply by its sha256 and brief form (Rule-3):
```dyad-cmd
name: evidence
class: read-only
role: any
undo: none
postcondition: none
scope: the working tree at HEAD (read; runs every check and guard)

dyad/bin/dyad check --evidence
```

## Record
The done-`Y` recorded, with the state left as it is (#202):
```dyad-cmd
name: record
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"; rm -f "$I/d-work/traces/$D.md"
postcondition: grep -q '^disposed:.*Y done' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance,traces}/<DWORK>.md

D="${DWORK:?d-work id}"; I="${DYAD_INSTANCE:-agent-corpus}"; S="$(sed -n 's/^state: //p' "$I/d-work/rows/$D.md")"; dyad/bin/dyad dwork state "$D" "$S" -d "${DISPOSED:?the entry, e.g. 'Y done (merges PR #9 at <head>)'}" --said-file "${SAID:?disposition file}" && dyad/bin/dyad dwork trace "$D" --out
```
The same act with the entry composed rather than typed (#556, harvested):
```dyad-cmd
name: done-record
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"; rm -f "$I/d-work/traces/$D.md"
postcondition: grep -q '^disposed:.*Y done' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance,traces}/<DWORK>.md

DWORK="${DWORK:?d-work id}" SAID="${SAID:?disposition file}" PRS="${PRS:-}" ACCRETED="${ACCRETED:-}" dyad/bin/dyad steps done-record
```

## Complete
The state, once every head the recorded entry names is on `main` (#202):
```dyad-cmd
name: complete
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md"
postcondition: grep -qx 'state: done' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/rows/<DWORK>.md

D="${DWORK:?d-work id}"; dyad/bin/dyad dwork state "$D" done
```
The close in full once it is due (#556, harvested):
```dyad-cmd
name: close-landed
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/" "$I/d-work/provenance/"
postcondition: grep -qx 'state: done' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance}/<DWORK>.md and the rows its entry accreted

DWORK="${DWORK:?d-work id}" dyad/bin/dyad steps close-landed
```

## Defer
A deferral (open or planned → blocked) naming the blocking d-work, which the row's `refs` then carries — `REFS` is the
full list the row is to hold, the blocker among it, since `-r` replaces the field:
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
Back to `open`:
```dyad-cmd
name: resume
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; git restore --source=HEAD --worktree -- "$I/d-work/rows/$D.md" "$I/d-work/provenance/$D.md"
postcondition: grep -qx 'state: open' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance}/<DWORK>.md

I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; if grep -qx 'state: backlog' "$I/d-work/rows/$D.md"; then dyad/bin/dyad dwork state "$D" open --prompt-file "${PROMPT:?prompt file}"; else dyad/bin/dyad dwork state "$D" open; fi
```

## Mirror
A unit's branch kept equal to `origin/main` (#556):
```dyad-cmd
name: sync-mirror
class: reversible
role: any
undo: git push -q origin "+${MIRROR_WAS:?the branch's previous sha, from this step's output}:refs/heads/${MIRROR:?branch}"
postcondition: test "$(git ls-remote origin "refs/heads/${MIRROR:?branch}" | cut -f1)" = "$(git rev-parse origin/main)"
scope: origin's refs/heads/<MIRROR>

MIRROR="${MIRROR:?branch}" dyad/bin/dyad steps sync-mirror
```
