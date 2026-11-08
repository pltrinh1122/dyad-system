# Run-book: playbook-optimize (a play-book's profile) — play-book `dyad/playbooks/playbook-optimize.md`, #642
# sections: Profile

A core run-book (package, `dyad/runbooks/`; agent zone): the first step of the play-book-optimization play-book as a
`dyad-cmd` block, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/playbook-optimize.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above). `PLAYBOOK` names the play-book profiled, a stem in `dyad/playbooks/`; the run reads the
play-book, the records it cites and the instance's traces, reaching the instance through `${DYAD_INSTANCE:-agent-corpus}`
(Rule-11 property 3), and runs from the git root. The step is **read-only**: the profile prints facts, and every class
it leads to is the agent's reading under the play-book, never a run-book command.

```text
dyad runbook list playbook-optimize
PLAYBOOK=<name> dyad runbook run playbook-optimize profile
```

## Profile
`dyad playbook profile <name>`: each step's heading, words and the `dmc:` ids and commands it cites; each cited
record's words and kind; the run's total words; and the median inference and mechanical seconds over the traces of rows
whose plan names the play-book, with the per-play-book limit printed. It writes nothing; it refuses an unknown
play-book or flag with exit 1 and otherwise exits 0:
```dyad-cmd
name: profile
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/playbooks/, dyad/dmc/ and <instance>/d-work/{plans,traces}/ (read)

dyad/bin/dyad playbook profile "$PLAYBOOK"
```
