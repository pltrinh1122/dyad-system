# sysadmin craft vocabulary (Tended terms)

One row per term. Craft terms are referenced, never defined, by the Agent vocabulary
(`dyad/vocabulary/VOCABULARY.md`, Rule-6 Boundaries); an Agent Rule's kernel may say `destructive`
or `event` and means the sense here. `rule` names the craft rule (`../rules/`) that owns the term.
Rows moved verbatim from the Agent vocabulary by d-work #155 (#157's list of fourteen). No guard
runs over this file until #156's `craft check`.

| term | definition | rule |
|------|------------|------|
| read-only | host-action class: observes, changes nothing; free | host-mutation |
| reversible | host-action class: changes state with a stated undo; authorized by the plan that names it | host-mutation |
| destructive | host-action class: no undo, data loss, or untested undo; needs its own counter-prompt | host-mutation |
| change log | `workstation-corpus/CHANGELOG.md`: one row per reversible or destructive host action | host-mutation |
| undo | the stated action that restores the state before a host action; what makes an action reversible | host-mutation |
| ops script | a committed, executable shell file in `workstation-corpus/ops/` that delivers one Operator-executed command with its header (d-work, class, undo, change-log row), commit, hash and verification; one per change-log row | ops-scripts |
| postcondition | the end state an ops script converges to: stated in its `# postcondition:` header line, tested by its `postcondition()` function before any mutation (exit 0 if it already holds) and asserted after | ops-scripts |
| supervisor | what keeps a server instance running independent of any session: a Docker restart policy (`unless-stopped`, `always`) or a systemd unit with `Restart=`, enabled at boot | server-instances |
| run-book | `workstation-corpus/runbooks/<instance>.md`: one server instance's CLI reference — status/health, start, stop, restart, logs, backup, restore, upgrade, credential rotation, data — runnable by Agent or Operator | server-instances |
| health command | the run-book command whose stated pass criterion (output, exit code or HTTP status) means the server instance is healthy | server-instances |
| run-book command | a fenced `dyad-cmd` block of a run-book: a header (name, class, role, undo, postcondition, scope) then the tool's native command line unchanged; parsed by `runbook.py`, run only through its runner | server-instances |
| event | one execution of a run-book command as recorded by the runner: one JSON object appended to `<runbooks>/events/<instance>.jsonl` (`runbook.EVENT_FIELDS`); append-only; the change-log evidence of a host action (distinct from a ratification event) | server-instances |
| role | who may run a run-book command (`any`, `operator`) and who ran it in an event (`operator`, `agent`); a command naming `sudo` or a credential word is role operator | server-instances |
| scope | the containers, paths and services a run-book command declares it may touch; recorded in its event, not enforced | server-instances |
