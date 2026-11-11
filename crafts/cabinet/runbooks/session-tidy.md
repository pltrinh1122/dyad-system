# Run-book: session-tidy (the census of units and sessions) — play-book `crafts/cabinet/playbooks/session-tidy.md`, #444, #640, #669
# sections: Census

The session-tidy play-book's one step, run through the core runner as `cabinet:session-tidy` from the git root, which
records an event in `<runbooks>/events/cabinet-session-tidy.jsonl`. `ACCOUNT` names the file the cos writes from the
account's own session list (`list_sessions`, `mine: true`); `HARNESS`, a transcribed harness list with no repository
column, is still read as before. The step is read-only; every tidy act is the cos's, never a command here.

```text
dyad runbook list cabinet:session-tidy
ACCOUNT=<file> dyad runbook run cabinet:session-tidy census
```

## Census
Each of this system's units and sessions, its facts and its act, and the outside count, by the play-book's record:
```dyad-cmd
name: census
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/sessions/, the ledger rows, the instance's mandates table, session reconcile's reading and the account list (read)

dyad/bin/dyad-python crafts/cabinet/scripts/tidy.py ${ACCOUNT:+--harness "$ACCOUNT"} ${HARNESS:+--harness "$HARNESS"}
```
