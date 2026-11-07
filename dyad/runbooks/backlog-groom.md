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
`dyad board groom`: a head line (`groom report: N backlog row(s) on <sha12>; K board anchor(s)`), then one block per
`backlog` row, by id — `#<id>[-<slug>] [backlog, <age>d] <title>` and its `refs:`, `adjacency:` (`#<anchor> <cosine>`,
or `none` when no anchor reaches 0.005), `promised:` and `roots:` lines, each row's hygiene lines beneath, imported
from the hygiene code and never recomputed — then `releases:` (each craft's last tag and live `VERSION`, and the
bundle's) and `last grooming:`. It writes nothing; it refuses any argument with exit 1 and otherwise exits 0:
```dyad-cmd
name: report
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/{rows,plans,board}/ and the release tags (read)

dyad/bin/dyad board groom
```
