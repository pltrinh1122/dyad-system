# Run-book: incident-hardening (the incident ledger worked whole) — play-book `dyad/playbooks/incident-hardening.md`, #137, #626
# sections: Survey, Group, Inventory, Plan, Execute, Verify

The incident-hardening play-book's steps, run through the core runner from the git root, each recording an event in
`<runbooks>/events/incident-hardening.jsonl`. `LEDGER` (default `agent-corpus/audits/INCIDENTS.md`) is the parameter;
the instance is `${DYAD_INSTANCE:-agent-corpus}`. The records the exercise writes are the agent's, under its plan-`Y`,
never a command's.

```text
LEDGER=<path> dyad runbook list incident-hardening
LEDGER=<path> dyad runbook run incident-hardening survey
```

## Survey
Phase 0, the idempotence gate:
```dyad-cmd
name: survey
class: read-only
role: any
undo: none
postcondition: grep -q '^| 20' "${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
scope: <LEDGER> and the audits/ directory beside it (read)

LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
dyad/bin/dyad-python dyad/scripts/audits.py hardening "$LEDGER"
```

## Group
Phase 1:
```dyad-cmd
name: group
class: read-only
role: any
undo: none
postcondition: none
scope: the audits/ directory beside <LEDGER> (read)

LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
ls -1 "$(dirname "$LEDGER")" | grep -E 'incident-(failure-modes|mode-[a-z])\.md$' || echo "no mode record or index audit beside $LEDGER: first exercise"
```

## Inventory
Phase 2 inventories every live mitigation of a mode from the code and the Rule text, never from an audit's prose — the
failure of #116 and #128 was a candidate surfaced as a paragraph with no row and no moment:
```dyad-cmd
name: inventory
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --list
```

## Plan
Phase 2 ends by falsifying "this mode is addressed"; what survives and is not yet built is a `backlog` row naming the
fence still to build — one of phase 4's three exits, and the one that makes an undisposed candidate visible as a row
instead of a paragraph:
```dyad-cmd
name: plan
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/rows/ (read)

dyad/bin/dyad dwork list --state backlog
```

## Execute
Phase 3:
```dyad-cmd
name: execute
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --evidence
```

## Verify
Phase 4 is not gated by the watermark:
```dyad-cmd
name: verify
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --list; dyad/bin/dyad automaton sweep
```
