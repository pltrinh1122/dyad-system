# Run-book: judgement-trace (the agent's judgement, traced from a symptom) — play-book `dyad/playbooks/judgement-trace.md`, #690
# sections: Symptom, Trace, Cause

The judgement trace's commands, run through the core runner from the git root, each recording an event in
`<runbooks>/events/judgement-trace.jsonl`. They read and decide nothing: steps T3, T5 and T6 have no command, and T4's
classing is inference by `dmc:judgement-cause`. `DWORK` names the row where the act happened, and `CITE` names one cited
line as `<path>:<line>` or `<path>:<first>-<last>`; neither has a default. The instance is `${DYAD_INSTANCE:-agent-corpus}`.

```text
dyad runbook list judgement-trace
DWORK=<id> dyad runbook run judgement-trace symptom
CITE=<path>:<line> dyad runbook run judgement-trace trace
dyad runbook run judgement-trace cause
```

## Symptom
T1: the row's stored files and the commits that cite it, so the act is quoted from where it happened:
```dyad-cmd
name: symptom
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/{rows,provenance,plans}/<DWORK>.md and git history (read)

I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; for k in rows provenance plans; do if [ -f "$I/d-work/$k/$D.md" ]; then echo "present: $I/d-work/$k/$D.md"; else echo "absent:  $I/d-work/$k/$D.md"; fi; done; git log --format='%h %aI %s' -E --grep="#$D([^0-9]|$)" | head -n 20
```

## Trace
T2: one cited line as it reads on `origin/main` now, never from memory:
```dyad-cmd
name: trace
class: read-only
role: any
undo: none
postcondition: none
scope: one file at origin/main (read)

C="${CITE:?<path>:<line> or <path>:<first>-<last>}"; P="${C%:*}"; L="${C##*:}"; git fetch -q origin main 2>/dev/null; git show "origin/main:$P" | awk -v r="$L" 'BEGIN{n=split(r,a,"-"); lo=a[1]; hi=(n>1?a[2]:a[1])} NR>=lo && NR<=hi {printf "%s:%d: %s\n", "'"$P"'", NR, $0}'
```

## Cause
T4: the classes of `dmc:judgement-cause` in its precedence order, each with its effect, for the agent's reading:
```dyad-cmd
name: cause
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/dmc/judgement-cause.jsonld (read)

dyad/bin/dyad-python -c "import json; d=json.load(open('dyad/dmc/judgement-cause.jsonld')); print(d['dyad:decides']); [print('%-13s %-8s %s' % (t['termCode'], t['dyad:effect'], t['dyad:when'])) for t in d['hasDefinedTerm']]; print('precedence:', d['dyad:precedence'])"
```
