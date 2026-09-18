# Run-book events (sysadmin craft, server-instances rule property 7)

One file per server instance, `<instance>.jsonl`, one JSON object per line: one event per execution
of a run-book command through the runner (`dyad runbook run <instance> <name>`), by either party.
Fields (`dyad/scripts/runbook.py`, `EVENT_FIELDS`): id, ts, role, instance, name, cmd, class, scope,
exit, duration_ms, postcondition, output_sha256, output_tail, commit, runbook_sha256.

- Written only by the runner; never hand-edited. On `main` the files are append-only
  (`crafts/sysadmin/guards/events.py`): a PR may add lines at the end, never change or remove one.
- Committed like a change-log row: an event records something that happened once (Rule-11
  property 6 does not apply). A change-log row for a reversible or destructive run-book command
  cites its event as `event: <id>` in the outcome cell (Rule-8); Rule-20 resolves the id.
- Reviewed with `dyad project events` (`crafts/sysarch/rules/projection.md`; the projector is this craft's, `crafts/sysadmin/projectors/project_events.py`), which renders every instance's events with exit
  and postcondition badges and a filter.
- The store starts empty.
