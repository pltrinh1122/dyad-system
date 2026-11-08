# Run-book: dwork-trace (where a d-work's time went) — play-book `dyad/playbooks/dwork-trace.md`, #213, #626
# sections: Locate, Trace, Compare

The d-work trace play-book's steps, each a call of `dyad dwork trace`, run through the core runner from the git root
by choice (the native command is the default, #247), recording an event in `<runbooks>/events/dwork-trace.jsonl`.
`DWORK` names the d-work, with no default; `trace` also reads `SAID`. The instance is
`${DYAD_INSTANCE:-agent-corpus}`.

```text
DWORK=<id> dyad runbook list dwork-trace
DWORK=<id> dyad runbook run dwork-trace locate
```

## Locate
The inputs the trace reads, before it reads them:
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
The trace itself, written to the trace store at the Done-`Y` — through the Operator's Done words, the file `SAID`
names, which the record act then records with the state left as it is (`dyad dwork state <DWORK> <that state> -d 'Y
done (merges PR #n at <head>)' --said-file "$SAID"`, Rule-3 Completion, #202); without `SAID`, and with no Done entry
in the record, the command refuses and writes nothing, since a stored trace is never a preview (#592) — and before the
Done record commit, which then carries all three (the store lies under `<instance>/d-work/`, so that commit stays
ledger-only):
```dyad-cmd
name: trace
class: reversible
role: any
undo: rm "${DYAD_INSTANCE:-agent-corpus}/d-work/traces/${DWORK:?d-work id}.md"
postcondition: test -s "${DYAD_INSTANCE:-agent-corpus}/d-work/traces/${DWORK:?d-work id}.md"
scope: <instance>/d-work/traces/<DWORK>.md (one new file)

dyad/bin/dyad dwork trace "${DWORK:?d-work id}" --out ${SAID:+--said-file "$SAID"}
```

## Compare
The bottleneck line of this trace beside every other trace's agent-side seconds, the figures the play-book's Reading
compares against their median:
```dyad-cmd
name: compare
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/traces/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; grep -h '^\*\*Top 3:\*\*' "$I/d-work/traces/${DWORK:?d-work id}.md"; grep -H '^\*\*Agent-side:\*\*' "$I"/d-work/traces/*.md
```
