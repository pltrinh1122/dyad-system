# Run-book: session-tidy (the census of open sessions) — play-book `crafts/cabinet/playbooks/session-tidy.md`, #444, #640
# sections: Census

The session-tidy play-book's one step, run through the core runner as `cabinet:session-tidy` from the git root, which
records an event in `<runbooks>/events/cabinet-session-tidy.jsonl`. `HARNESS` names an optional file holding the
transcribed harness session list. The step is read-only; archiving is the cos's act, never a command here.

```text
dyad runbook list cabinet:session-tidy
HARNESS=<file> dyad runbook run cabinet:session-tidy census
```

## Census
Each open session's facts and its class, by the play-book's record:
```dyad-cmd
name: census
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/sessions/, the ledger rows, the instance's mandates table and the harness list (read)

dyad/bin/dyad-python crafts/cabinet/scripts/tidy.py ${HARNESS:+--harness "$HARNESS"}
```
