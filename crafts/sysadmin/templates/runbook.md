# Run-book: <instance> (<what it is, container or unit name>) — d-work #<id>

Instance: <container or unit>, image/package <name:version> built from `<path>` (Compose project or unit name).
Supervisor (server-instances rule, property 1): <Docker restart policy `unless-stopped` | systemd `Restart=`>, enabled at boot.
Every command runs from the git root as <user> (no sudo unless the block says `role: operator` — those are
Operator-run, Rule-8/Rule-18).

Every command is a `dyad-cmd` block (server-instances rule, properties 7–9): a header naming the command, its
Rule-8 class, the role that may run it, its undo, a postcondition (a shell test) and its scope, then the tool's
native command line unchanged. Both parties run it through the runner, which prints that line, records an event
in `events/<instance>.jsonl` and tests the postcondition:

```text
dyad runbook list <instance>
dyad runbook run <instance> <name> [--as operator]
```

<Spell out any abbreviation used below, e.g. `DC` = `docker compose -f <compose> --env-file <env-file>`.>

## Status/health
```dyad-cmd
name: status
class: read-only
role: any
undo: none
postcondition: none
scope: <container> (read)

<status command, e.g. docker ps --filter name=<container> --format '{{.Names}} {{.Status}}'>
```
Health (the pass criterion for Done — server-instances rule, property 4; Rule-19 kernel):
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: <the shell test that means healthy, e.g. docker inspect --format '{{.State.Health.Status}}' <container> | grep -qx healthy>
scope: <container> (read)

<health command; pass criterion: <exact output, exit code or HTTP status>>
```

## Start
```dyad-cmd
name: start
class: reversible
role: any
undo: <stop command>
postcondition: <test that it is running>
scope: <container>, <network>

<start command>
```

## Stop
```dyad-cmd
name: stop
class: reversible
role: any
undo: <start command>
postcondition: <test that it is stopped>
scope: <container>

<stop command>
```

## Restart
```dyad-cmd
name: restart
class: reversible
role: any
undo: none needed (restart again)
postcondition: <test false before, true after — e.g. started within the last 60 s>
scope: <container>

<restart command>
```

## Logs
```dyad-cmd
name: logs
class: read-only
role: any
undo: none
postcondition: none
scope: <container> (read)

<logs command>
```

## Backup
```dyad-cmd
name: backup
class: reversible
role: any
undo: <remove the backup file>
postcondition: <test that today's backup exists>
scope: <container>, <backup path>

<backup command>
```

## Restore
```dyad-cmd
name: restore
class: destructive
role: operator
undo: none
postcondition: <test that the restored state is live>
scope: <data path>, <container>

<restore command; the runner confirms it on the terminal>
```

## Upgrade
```dyad-cmd
name: upgrade
class: reversible
role: any
undo: <rebuild or reinstall the previous version>
postcondition: <test that the new version runs>
scope: <image or package>, <container>

<upgrade command>
```

## Credential rotation
```dyad-cmd
name: rotate-<credential>
class: reversible
role: operator
undo: <restore the previous credential>
postcondition: <test that the new credential works>
scope: <credential file>, <container>

<rotation command; names a credential word, so role operator>
```

## Data
Where state lives on the host: <data path> (<filesystem, owner, mode>). A fresh deployment needs:
<what to restore and in what order>.
```dyad-cmd
name: data
class: read-only
role: any
undo: none
postcondition: none
scope: <data path> (read)

<command that lists the data directory>
```
