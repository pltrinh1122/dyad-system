# Run-book: backlog-groom (the backlog grooming report) — play-book `dyad/playbooks/backlog-groom.md`, #625
# sections: Report

A core run-book (package, `dyad/runbooks/`; agent zone): the one step of the backlog-grooming play-book as a
`dyad-cmd` block, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/backlog-groom.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above). The run takes no parameter; it reads the live backlog, the board and the release tags,
reaching the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3), and runs from the git root. The
step is **read-only**: the report prints facts, and every judgement it leads to — a retirement ground, a size, a
promotion class, a release target — is the home's reading under the play-book, never a run-book command. The event
this step records is the play-book's last grooming event, which the next run's floor reads.

```text
dyad runbook list backlog-groom
dyad runbook run backlog-groom report
```

## Report
`dyad board groom`: one block per `backlog` row, oldest first — `#<id>-<slug>`, its age, its refs' states, its
adjacency score against the board's anchors, whether a `promised` entry of the board names it, the craft roots its
plan file touches — each row's hygiene lines beneath it, imported from the hygiene code and never recomputed; then the
last release tag per craft and the last grooming event. It writes nothing:
```dyad-cmd
name: report
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/{rows,plans,board}/ and the release tags (read)

dyad/bin/dyad board groom
```
