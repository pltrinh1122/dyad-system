# Run-book: ledgerd (the core craft's ledger server — systemd user unit `dyad-ledgerd.service` on Linux, launchd agent `com.dyad.ledgerd` on macOS) — d-work #336

Instance: `ledgerd`, the core craft's server component `dyad/server/ledgerd/` (plan #336 revisions 15–16), run from
the checkout that installed it, under the venv `init` made (`<state>/venv`, plan #336 revision 9), as one process:
`dyad ledger serve`. The host's deployment notes — the state directory, the conf keys, the chosen port and the
`ui-url` rule, the OAuth App registration — are `workstation-corpus/server/ledgerd/README.md`.
Supervisor (server-instances rule, property 1): on Linux a systemd **user** unit, `~/.config/systemd/user/dyad-ledgerd.service`,
`Restart=always`, enabled, with `loginctl enable-linger` so it starts at boot without a login (the linger line is
the one Operator-run step, `workstation-corpus/ops/336-h4-linger.sh`, Rule-18); on macOS a launchd user agent,
`~/Library/LaunchAgents/com.dyad.ledgerd.plist`, `KeepAlive` and `RunAtLoad`. Every command below is a `dyad ledger`
line, so one run-book serves both hosts: each verb prints the supervisor's native line (`systemctl --user …`,
`launchctl …`) before running it, so a reader can run that line by hand (server-instances rule, property 8).
Every command runs from the git root as the Operator's own user (no sudo; the two blocks marked `role: operator`
are Operator-run because the Operator's device or a destructive step is in the loop, Rule-8/Rule-18).

Every command is a `dyad-cmd` block (server-instances rule, properties 7–9): a header naming the command, its
Rule-8 class, the role that may run it, its undo, a postcondition (a shell test) and its scope, then the tool's
native command line unchanged. Both parties run it through the runner, which prints that line, records an event
in `events/ledgerd.jsonl` and tests the postcondition — before (a postcondition that already holds is
`already satisfied`, exit 0, and the command does not run) and after:

```text
dyad/bin/dyad runbook list ledgerd
dyad/bin/dyad runbook run ledgerd health
STATE="$HOME/Library/Application Support/dyad/ledgerd" dyad/bin/dyad runbook run ledgerd status   # a Mac
```

One parameter, read from the environment: `STATE`, the state directory `dyad ledger init --state <dir>` was
given. Its default here is the Linux one, `$HOME/.local/state/dyad/ledgerd` (the workstation, the host Rule-19's
pass is taken on); a Mac sets `STATE="$HOME/Library/Application Support/dyad/ledgerd"` (plan #336 revision 7).
Every line below spells the parameter out as `"${STATE:-$HOME/.local/state/dyad/ledgerd}"` so it runs as written.

The port is the one `init` selected: it walks up from **8731** and takes the first free port, records it in
`<state>/ledgerd.conf` and prints `ui-url: http://127.0.0.1:<port>/` as its last line (plan #336 revision 8).
The `ui-url` that `init` printed — repeated by `dyad ledger status` and by `/health` — is authoritative; the
lines below are written for **8731**, the port the rule selects first, and are edited (a workstation-zone PR)
if `init` on this host chose another. `serve` refuses a port that is no longer free rather than moving.

## Status/health
`status` prints the supervisor's own status line, the `ui-url`, the pin (the sha of `main` the projection was
built from) and, when logged in, the GitHub login:
```dyad-cmd
name: status
class: read-only
role: any
undo: none
postcondition: none
scope: dyad-ledgerd user unit (Linux) / com.dyad.ledgerd agent (macOS), 127.0.0.1:8731 (read)

dyad/bin/dyad ledger status --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```
Health (the pass criterion for Done — server-instances rule, property 4; Rule-19 kernel): HTTP 200 (`curl -f`
fails otherwise) and a body with `"ok": true` and `pin` a 40-hex sha — the projection is built and serving.
`/health` also reports `refresh_every`, `last_tick`, `last_fetch_ok` (a fetch that failed leaves the last good
build serving, so `ok` stays true and `last_fetch_ok` says what is wrong), `ui_url`, `auth` and `supervisor`:
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: h="$(curl -fsS http://127.0.0.1:8731/health)" && grep -Eq '"ok": *true' <<<"$h" && grep -Eq '"pin": *"[0-9a-f]{40}"' <<<"$h"
scope: 127.0.0.1:8731 (read)

curl -fsS http://127.0.0.1:8731/health
```

## Start
```dyad-cmd
name: start
class: reversible
role: any
undo: dyad/bin/dyad ledger stop --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
postcondition: curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:8731/health
scope: dyad-ledgerd user unit (Linux) / com.dyad.ledgerd agent (macOS), 127.0.0.1:8731

dyad/bin/dyad ledger start --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Stop
Stopping leaves the state directory as it is; the supervisor does not restart a unit that was stopped by hand
(`systemctl --user stop`, `launchctl bootout`), so the service stays down until `start`:
```dyad-cmd
name: stop
class: reversible
role: any
undo: dyad/bin/dyad ledger start --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
postcondition: ! curl -fsS --max-time 2 -o /dev/null http://127.0.0.1:8731/health
scope: dyad-ledgerd user unit (Linux) / com.dyad.ledgerd agent (macOS), 127.0.0.1:8731

dyad/bin/dyad ledger stop --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Restart
A restart is how an edit to `<state>/ledgerd.conf` (the refresh interval, the bind) takes effect. The postcondition is
false before and true after: the serving process (`ledger serve`, matched as `ledger [s]erve` so the test's own
shell never matches itself) is younger than a minute and answers `/health`:
```dyad-cmd
name: restart
class: reversible
role: any
undo: none needed (restart again)
postcondition: [[ "$(ps -o etime= -p "$(pgrep -n -f 'ledger [s]erve')" | tr -d ' ')" =~ ^0?0:[0-5][0-9]$ ]] && curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:8731/health
scope: dyad-ledgerd user unit (Linux) / com.dyad.ledgerd agent (macOS), 127.0.0.1:8731

dyad/bin/dyad ledger restart --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Logs
On Linux the journal (`journalctl --user -u dyad-ledgerd -n 50 --no-pager`); on macOS, where launchd has no journal,
the tail of `<state>/ledgerd.log`. A refresh tick that fetched nothing new logs one line; a failed fetch logs the error
the next tick retries:
```dyad-cmd
name: logs
class: read-only
role: any
undo: none
postcondition: none
scope: the user journal (Linux) / <state>/ledgerd.log (macOS) (read)

dyad/bin/dyad ledger logs --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Backup
What a backup is worth here: `ledgerd.db` is a projection, rebuilt from the pin on every refresh tick (60 s), so
its copy is a snapshot of the view at one sha and nothing that cannot be rebuilt — kept as the form asks (plan
#336 revision 4) and so that `restore` has something to restore. The Operator's own state in the directory is
`ledgerd.conf` (the client id, the port, the store URL) and `views/` (saved UI views, plan #336 revision 8); both
are plain files small enough to copy by hand, and `Data` below says what a fresh deployment does without them.
The postcondition is today's copy, so a second run on the same day is `already satisfied`:
```dyad-cmd
name: backup
class: reversible
role: any
undo: rm "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db.$(date +%F).bak"
postcondition: test -s "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db.$(date +%F).bak"
scope: <state>/ledgerd.db (read), <state>/ledgerd.db.<date>.bak

cp "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db" "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db.$(date +%F).bak"
```

## Restore
**`refresh` is the real restore.** The projection is never a source (plan #336 revision 4, P3): one `POST /refresh`
runs a tick now — fetch the store, compare the head of `main` to the pin, rebuild the database and re-render the
views when it moved — so a damaged or stale `ledgerd.db` is replaced by a fresh build from `main` without any file
being copied. The postcondition compares the pin `/health` reports to the head of `main` at the store, so a service
already at the head is `already satisfied` and a refresh that fetched nothing is not mistaken for one that did:
```dyad-cmd
name: refresh
class: reversible
role: any
undo: none needed (the previous build was the same data at an older sha; the next tick rebuilds in any case)
postcondition: [[ "$(curl -fsS http://127.0.0.1:8731/health | grep -Eo '"pin": *"[0-9a-f]{40}"' | grep -Eo '[0-9a-f]{40}')" == "$(git ls-remote https://github.com/pltrinh1122/dyad-system.git refs/heads/main | cut -f1)" ]]
scope: 127.0.0.1:8731, <state>/ledgerd.db, <state>/board.md, <state>/board.txt, <state>/schema.md

curl -fsS -X POST http://127.0.0.1:8731/refresh
```
`restore` is kept for the form (server-instances rule, property 2) and is stated as never needed: it stops the
service, copies today's backup over the live file and starts it again — destructive by the template's own form,
since the live file is overwritten and the next tick rebuilds it from the pin anyway. The runner confirms it on the
terminal; it is Operator-run:
```dyad-cmd
name: restore
class: destructive
role: operator
undo: none (the overwritten file was a projection; the next refresh tick, or `refresh`, rebuilds it from main)
postcondition: cmp -s "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db" "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db.$(date +%F).bak"
scope: <state>/ledgerd.db, dyad-ledgerd user unit (Linux) / com.dyad.ledgerd agent (macOS)

dyad/bin/dyad ledger stop --state "${STATE:-$HOME/.local/state/dyad/ledgerd}" && cp "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db.$(date +%F).bak" "${STATE:-$HOME/.local/state/dyad/ledgerd}/ledgerd.db" && dyad/bin/dyad ledger start --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Upgrade
The code the service runs is the checkout it was installed from (the Operator's own checkout of this repository on
the host), under the venv `init` made; the **data** pin moves every tick, the **code** moves only here (plan #336
revision 5, Q5). An upgrade is: move the checkout (`git pull` on `main` — a ratified merge, Rule-2 — or `git checkout
<ref>` for a branch under test, the Operator's or the terminal session's own act in its checkout), then `install`
again and `restart`. `install` is idempotent (`0 changes` when nothing differs): it re-derives the `pip install`
line from the manifest rows (`dyad/infrastructure/INFRASTRUCTURE.md`, the only list of the pinned packages, plan
#336 revision 9) and installs them into `<state>/venv`, rewrites the unit or plist when its content differs, enables
and starts it, and on Linux attempts `loginctl enable-linger` (the `336-h4-linger.sh` ops script if polkit refuses).
It is also the first-time install, H3 of the deploying d-work (its change-log row records the `ui-url`):
```dyad-cmd
name: install
class: reversible
role: any
undo: dyad/bin/dyad ledger uninstall --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
postcondition: test -f "$HOME/.config/systemd/user/dyad-ledgerd.service" || test -f "$HOME/Library/LaunchAgents/com.dyad.ledgerd.plist"
scope: <state>/venv, ~/.config/systemd/user/dyad-ledgerd.service (Linux) / ~/Library/LaunchAgents/com.dyad.ledgerd.plist (macOS), PyPI (read)

dyad/bin/dyad ledger install --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```
`upgrade` runs after the checkout moved. Its undo is the checkout moved back (`git checkout <previous sha>` in the
Operator's checkout, the sha the last `upgrade` event's `commit` field records) and this same command again; its
postcondition is `restart`'s — the process is younger than a minute and healthy — because a healthy service is the
state before the upgrade too, and a test that held before would never let the upgrade run:
```dyad-cmd
name: upgrade
class: reversible
role: any
undo: git checkout <previous sha> in the Operator's checkout (the `commit` of the last upgrade event in events/ledgerd.jsonl), then this command again
postcondition: [[ "$(ps -o etime= -p "$(pgrep -n -f 'ledger [s]erve')" | tr -d ' ')" =~ ^0?0:[0-5][0-9]$ ]] && curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:8731/health
scope: <state>/venv, the unit or plist, dyad-ledgerd user unit (Linux) / com.dyad.ledgerd agent (macOS), 127.0.0.1:8731, PyPI (read)

dyad/bin/dyad ledger install --state "${STATE:-$HOME/.local/state/dyad/ledgerd}" && dyad/bin/dyad ledger restart --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Credential rotation
The one credential is the GitHub OAuth token of the device flow, in `<state>/credentials` (mode 0600, git's
credential-store form; never printed, never in a reply, never in the repo — plan #336 revision 7). It does not expire;
it is rotated by logging out and in again: `auth logout` deletes the file (it revokes nothing on GitHub — the Operator
revokes the old grant at GitHub → Settings → Applications → Authorized OAuth Apps → `dyad-ledgerd`), and `auth login`
prints `Open https://github.com/login/device and enter the code XXXX-XXXX`, which the Operator does on any device
while the command polls; the new token lands in the file and nothing else. Operator-run: the Operator's device is in
the loop (and the command rotates a token, the credential word the runner gates on). Until the Operator has
registered the OAuth App (`workstation-corpus/server/ledgerd/README.md`), `auth login` refuses with the registration
steps, and the public store is fetched anonymously. The postcondition — the file is younger than a minute and
`auth status` reports a login — is false before the rotation, so the runner never reports it `already satisfied`:
```dyad-cmd
name: rotate-github-token
class: reversible
role: operator
undo: dyad/bin/dyad ledger auth login --state "${STATE:-$HOME/.local/state/dyad/ledgerd}" (the previous token is deleted by logout and not restored; a new login restores the logged-in state)
postcondition: test -n "$(find "${STATE:-$HOME/.local/state/dyad/ledgerd}" -maxdepth 1 -name credentials -mmin -1)" && dyad/bin/dyad ledger auth status --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
scope: <state>/credentials, github.com (the device flow)

dyad/bin/dyad ledger auth logout --state "${STATE:-$HOME/.local/state/dyad/ledgerd}" && dyad/bin/dyad ledger auth login --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```

## Data
Where state lives on the host: the state directory, `~/.local/state/dyad/ledgerd/` on Linux (`$XDG_STATE_HOME`
honoured) and `~/Library/Application Support/dyad/ledgerd/` on macOS, owned by the Operator's user, created by
`dyad ledger init --state <dir>`. It holds: `ledgerd.conf` (`key: value` lines — the schema `dwork`, the store URL,
the bind and the chosen port, the refresh interval, the OAuth App client id), `repo.git` (the bare data clone of the
store, fetched every tick), `ledgerd.db` (the SQLite projection, rebuilt atomically whenever the pin moves),
`board.md`, `board.txt` and `schema.md` (the rendered views, re-rendered with it), `views/` (the Operator's saved UI
views, `<name>.view` files), `venv/` (the pinned packages, made by `init`) and, once logged in, `credentials` (0600).
On macOS also `ledgerd.log`. **Nothing here is a source**: the files on `main` are canonical (Rule-16, the stores
rule), the database is a projection, and the directory is outside every repository. A fresh deployment needs no
file restored: `init` (with the same `--github-client-id` and, if the same port is wanted, `--port`), `install`,
then `auth login` if a private store is to be served — in that order; the first tick rebuilds the projection from
`main`. The only files worth carrying over are `ledgerd.conf` (to keep the client id and the port) and `views/`
(saved views are UI state, not ledger data — lost with the host unless copied, plan #336 revision 8 U4):
```text
dyad/bin/dyad ledger init --state "$STATE" --schema dwork --store git+https://github.com/pltrinh1122/dyad-system.git#main --refresh-every 60 --github-client-id <client id>
dyad/bin/dyad ledger install --state "$STATE"
dyad/bin/dyad ledger auth login --state "$STATE"
```
```dyad-cmd
name: data
class: read-only
role: any
undo: none
postcondition: none
scope: <state> (read)

ls -la "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```
What the projection holds — the tables, their columns and the views, as the `dwork` schema declares them (the
guards' own parsers are the tables; plan #336 revision 4):
```dyad-cmd
name: schema
class: read-only
role: any
undo: none
postcondition: none
scope: <state>/ledgerd.db (read)

dyad/bin/dyad ledger schema --state "${STATE:-$HOME/.local/state/dyad/ledgerd}"
```
