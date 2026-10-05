# Run-book: dwork-trace (where a d-work's time went) — play-book `dyad/playbooks/dwork-trace.md`, #213
# sections: Locate, Trace, Compare

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the d-work trace play-book as
`dyad-cmd` blocks, run by either party through the core runner, which prints the native line, records an
event in the instance's `<runbooks>/events/dwork-trace.jsonl` and tests the postcondition. Its section set is
its own (the `# sections:` line above; the sysadmin craft's server sections are a server's). Every step takes
the d-work id from the environment — `DWORK`, the play-book's parameter, with no default: a trace of the
wrong d-work is worse than none — and reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11
property 3). Every command runs from the git root. Locate and Compare are **read-only**; Trace is the one
writing step, **reversible**: it writes one file of the trace store, `<instance>/d-work/traces/<DWORK>.md`
(plan #213 revision 2), and its undo deletes it.

```text
DWORK=<id> dyad runbook list dwork-trace
DWORK=<id> dyad runbook run dwork-trace locate
```

## Locate
The inputs the trace reads, before it reads them: the row, its provenance record and its plan file, and the
commits that cite the d-work. A missing provenance record is an anchorless trace — every bucket absent —
and is said so here rather than discovered in the trace. The postcondition tests the one input without which
there is nothing to trace, the row:
```dyad-cmd
name: locate
class: read-only
role: any
undo: none
postcondition: test -f "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/${DWORK:?d-work id}.md"
scope: <instance>/d-work/{rows,provenance,plans}/<DWORK>.md and git history (read)

I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; for k in rows provenance plans; do if [ -f "$I/d-work/$k/$D.md" ]; then echo "present: $I/d-work/$k/$D.md"; else echo "absent:  $I/d-work/$k/$D.md"; fi; done; git log --format='%h %aI %s' -E --grep="d-work #$D([^0-9]|$)" | head -n 20
```

## Trace
The trace itself, written to the trace store at the Done-`Y` — after `dyad dwork state <DWORK> done` has
written the row and its provenance entry, before the Done ledger commit, which then carries all three (the
store lies under `<instance>/d-work/`, so that commit stays ledger-only). Timeline, buckets, counts,
bottleneck line and limits, in the play-book's format, from the row, its provenance and plan, git and the
newest transcript of this working tree's harness project directory (read in place, never copied, never
quoted). The completion reply's preview is the native command without `--out`, which writes nothing; a
d-work worked in another session is traced by the native command with `--transcript <path>`, outside this
step, and said so. The postcondition tests that the file exists and is not empty:
```dyad-cmd
name: trace
class: reversible
role: any
undo: rm "${DYAD_INSTANCE:-agent-corpus}/d-work/traces/${DWORK:?d-work id}.md"
postcondition: test -s "${DYAD_INSTANCE:-agent-corpus}/d-work/traces/${DWORK:?d-work id}.md"
scope: <instance>/d-work/traces/<DWORK>.md (one new file)

dyad/bin/dyad dwork trace "${DWORK:?d-work id}" --out
```

## Compare
The bottleneck line of this trace beside every other trace's agent-side seconds, the figures the play-book's
Reading compares against their median. An empty listing beyond this d-work's own line is the first trace,
and the step says nothing more:
```dyad-cmd
name: compare
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/traces/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; grep -h '^\*\*Top 3:\*\*' "$I/d-work/traces/${DWORK:?d-work id}.md"; grep -H '^\*\*Agent-side:\*\*' "$I"/d-work/traces/*.md
```
