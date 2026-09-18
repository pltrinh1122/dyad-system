# Server instances (sysadmin craft, Tended Rule)

Read by Rule-19's kernel (`dyad/rules/RULE-19-server-instances.md`): the core Rule binds *that* every
server instance the Agent deploys or operates leaves a run-book at the instance path and a health
command whose observed pass is completion evidence; this rule is the run-book's *form* — supervisor,
sections, commands, health, telemetry, one execution path, contained mutation. Text moved verbatim
from Rule-19 Properties 1–4 and 6–9 by d-work #155; a Tended Rule — any form, no Rule-4 block, no
sweep, no Agent-vocabulary row. Terms (`supervisor`, `run-book`, `health command`, `run-book command`,
`event`, `role`, `scope`): `crafts/sysadmin/vocabulary/CRAFT.md`. Template:
`crafts/sysadmin/templates/runbook.md` (`dyad runbook new <instance>` seeds it). Guards:
`crafts/sysadmin/guards/runbooks.py` (`sysadmin/runbooks`) and `events.py` (`sysadmin/events`).
Runner: `dyad runbook` (`dyad/scripts/runbook.py`, core craft — it holds the parser and writes the
event, so it works with no craft installed; #155 amendment).

## Properties
1. **Persistence.** A server instance runs under a supervisor (vocabulary): a Docker
   restart policy of `unless-stopped` or `always`, or a systemd unit with `Restart=`, enabled at
   boot. It survives the end of the agent session that started it and a host reboot; nothing
   about it depends on a chat, a terminal or a harness process staying open. A plan that
   deploys a server names the supervisor and the policy.
2. **Run-book.** Every server instance has `<runbooks>/<instance>.md`
   (instance, workstation zone; `DYAD_RUNBOOKS`, default `workstation-corpus/runbooks`, in the
   manner of Rule-11 property 3). Its sections, each holding CLI commands: `Status/health`,
   `Start`, `Stop`, `Restart`, `Logs`, `Backup`, `Restore`, `Upgrade`, `Credential rotation`,
   `Data`. `Data` states where state lives on the host and what a fresh deployment needs to
   recover it. These ten are the default section set; a run-book whose header carries
   `# sections: A, B, C` (`runbook.declared_sections`) is checked against that set instead — the
   form of the core craft's run-books (`dyad/runbooks/<name>.md`, a play-book's steps, #165), which
   the guard reads as well; a run-book with its own set is not a server's and its server-directory
   warning is skipped.
3. **Commands.** Each command is one copy-pasteable line or fenced block, runnable as written by
   the Agent or the Operator from the git root, `sudo`-free wherever the host permits; a command
   that needs `sudo` or credentials says so beside it and the Agent treats it as Operator-run
   (Rule-8, Rule-18). A command that changes state names its Rule-8 class and its undo. Under the
   preference `cli-pattern: industry-standard` (`preferences-corpus/PREFERENCES.md`) a command is
   the tool's native CLI shown verbatim; a runner that wraps it prints the identical line (#152).
4. **Health.** The `Status/health` section has a health command with a stated pass criterion —
   the exact output, exit code or HTTP status that means healthy. Where the server ships a
   healthcheck (a Docker `HEALTHCHECK`, a `/healthz` endpoint) the command reads it rather than
   re-implementing it.
5. *(Kept in Rule-19's kernel: "Deployed means run-book and health".)*
6. **Every server instance.** The properties bind every long-running service the Agent deploys or
   the Operator asks the Agent to operate on the host — the git server and any later one. A
   service already present that neither party operates through the dyad is out of scope until a
   d-work touches it; the plan of that d-work brings it under this Rule.
7. **Telemetry.** Every execution of a run-book command leaves an event (vocabulary): one
   JSON object appended to `<runbooks>/events/<instance>.jsonl` by the runner — when, the role
   that ran it, instance, command name, the exact command line, class, scope, exit code, duration,
   postcondition result, a digest and the tail of the output, the commit and the run-book's hash
   (`runbook.EVENT_FIELDS`). The store is instance, committed (an event records something that
   happened once; it is not a generated file, Rule-11 property 6) and append-only on `main`
   (`crafts/sysadmin/guards/events.py`, the event guard's transaction check, in the form of Rule-3's
   fence; this rule owns the rule). An audit reads events
   through `dyad project events` (`crafts/sysarch/rules/projection.md`; the projector is this craft's, `crafts/sysadmin/projectors/project_events.py`) and resolves them through Rule-20 (an event's
   command name names a command of its run-book; a change-log row's `event: <id>` names an event).
8. **One execution path.** A run-book command (vocabulary) is data, not prose: a fenced block
   tagged `dyad-cmd` whose header (`runbook.FIELDS`: name, class, role, undo, postcondition, scope)
   is followed by the tool's native command line unchanged. Operator and Agent run the same bytes
   through the same runner, which prints that line before running it so the reader can copy it
   out; a bare shell block in a run-book fails the check. The role (vocabulary) gates who may run
   it: a command whose line names `sudo` or a credential word (`runbook.CREDENTIAL_WORDS`) is role
   `operator` and the runner refuses it under the agent role (exit 2) — the mechanical form of
   property 3's "Operator-run" (Rule-8). *(Borderline, moved with a note — #155 attack 3: this
   sentence binds the runner, craft-served code; Rule-8's kernel already binds the Agent to
   Operator-run for sudo and credentials.)* The header vocabulary (class, undo, postcondition,
   destructive confirmation) is the ops-scripts rule's; this rule adds role, scope and the event.
9. **Contained mutation.** Every state-changing command declares its Rule-8 class, its undo, a
   postcondition (a shell test, ops-scripts rule property 6 form) and its scope (vocabulary): the containers,
   paths and services it may touch. The runner tests the postcondition before (a command whose
   postcondition already holds is "already satisfied", exit 0, and does not run) and after (a
   failed postcondition is recorded and exits 1); a destructive command is confirmed on the
   terminal (ops-scripts rule property 7 form; exit 2 without one). The scope is declared and recorded,
   not enforced: full sandboxing is out of scope and stated (plan #150, attack 6).

## The check (what the guards verify)
`crafts/sysadmin/guards/runbooks.py` (`check_package`, registered as `sysadmin/runbooks` in Rule-11's
runner and on the kernel-only path; tests in `crafts/sysadmin/tests/guards/test_runbooks.py`): every
run-book under `<runbooks>` parses; every property-2 section holds at least one `dyad-cmd` command;
every command carries every header field, a Rule-8 class, a role, a unique name; a command naming
`sudo` or a credential word is role `operator`; a reversible command names an undo, a state-changing
command a postcondition; no bare shell block remains; a run-book citing no `crafts/*/server*/` or
`workstation-corpus/server*/` directory warns. The events store's shape is checked and its append-only
fence kept by `crafts/sysadmin/guards/events.py` (`sysadmin/events`); Rule-20 resolves event references.
Not checked, stated: the restart policy inside a compose file or unit (property 1), whether a command
works, whether the health criterion is right, and whether a command stays inside its declared scope —
inference, tested by running them and read from the events.

## Reference deployment
The lan-git craft ships one implementation of "a git server" (Gitea in Docker, with the merge-gate
receiver) at `crafts/lan-git/server/` (its own craft since #181, extracted from this one — `#155`
attack 4's "a second implementation is a sibling directory" reads as a sibling *craft* now that the
deployment has its own publish/lock/deploy-path practice; property 1 stays implementation-neutral
either way). Host values never live in the image files: `compose.yaml` reads them from an env file
(`.env.example` is the placeholder set).

## Provenance
Rule-19 Properties 1–4, 6–9 and the Enforcement check list, moved by #155 (plan
`agent-corpus/d-work/plans/155.md`, attack 3). Record: `../falsification/rules/server-instances.md`.
