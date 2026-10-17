# ledgerd on this host — deployment notes (d-work #336)

The host's counterpart of the core craft's server component `dyad/server/ledgerd/` (plan #336 revisions 15–16):
what this workstation's instance of `ledgerd` is made of, where it keeps its state, which port it serves, how it
is supervised and how it authenticates to GitHub. The run-book that operates it is `../../runbooks/ledgerd.md`
(`dyad runbook run ledgerd <name>`; its health command is Rule-19's observed pass); the one Operator-run step is
the ops script `../../ops/336-h4-linger.sh` (Rule-18). Every host action of the deployment — `init`, `auth login`,
`install`, the linger line — is a row in `../../CHANGELOG.md` (Rule-8), written by the session whose hands ran it.
Nothing in this directory is a source: the service is a projection of the files on `main` (Rule-16).

## What runs
One process, `dyad ledger serve`, started by the supervisor from the checkout that ran `dyad ledger install`
(the Operator's own checkout of this repository on the host) under the interpreter of the venv `init` made
(`<state>/venv/bin/python3`): FastAPI on uvicorn for the API and the HTML navigator, SQLAlchemy Core for the
projection, Jinja2 and a vendored htmx for the pages, the kernel's git for the store and the stdlib for the
device flow (plan #336 revision 9; the pinned rows are `dyad/infrastructure/INFRASTRUCTURE.md`, the only list —
`install` derives its `pip install` line from them). Every 60 s (`--refresh-every`, in the conf) a refresh thread
fetches the store, compares the head of `main` to the pin, and when it moved rebuilds `ledgerd.db` atomically and
re-renders `board.md`, `board.txt` and `schema.md`. The database accepts no write: one read statement per query,
and SQLite's own authorizer on a read-only connection (plan #336 revision 4, P3). The **data** pin moves every
tick; the **code** moves only by the run-book's `upgrade` (revision 5, Q5).

## The state directory
`dyad ledger init --state <dir>` creates it; the run-book's `STATE` parameter names it. By the host adapter's rule
(`dyad/scripts/hostadapter.py` `state_dir()`, revision 7):

| host | state directory | supervisor |
|---|---|---|
| Linux (this workstation) | `~/.local/state/dyad/ledgerd/` (`$XDG_STATE_HOME` honoured) | systemd user unit `~/.config/systemd/user/dyad-ledgerd.service`, `Restart=always`, enabled; `loginctl enable-linger` for boot |
| macOS | `~/Library/Application Support/dyad/ledgerd/` | launchd user agent `~/Library/LaunchAgents/com.dyad.ledgerd.plist`, `KeepAlive`, `RunAtLoad`; logs to `<state>/ledgerd.log` |
| neither (a cloud container) | as Linux | `proc`: a detached process with a pid file; **not persistent**, and `status` and `/health` say so (`supervisor: proc`) — a prototype, never the Rule-19 pass |

What it holds, all of it generated or Operator-local, nothing of it in any repository:

| file | what | kept across a fresh deployment? |
|---|---|---|
| `ledgerd.conf` | `key: value` lines written by `init`: the schema (`dwork`), the store URL, the bind address and the chosen port, the refresh interval, the OAuth App client id. The exact key names are the component's own README, `dyad/server/ledgerd/README.md` | worth copying: it carries the client id and the port; otherwise `init` writes a new one |
| `repo.git` | the bare data clone of the store, fetched every tick (never a working tree: builds export from the sha with `git archive`) | no — re-cloned by `init` |
| `ledgerd.db` | the SQLite projection, rebuilt whenever the pin moves | no — a projection |
| `board.md`, `board.txt`, `schema.md` | the rendered views at the pin, served at `/board`, `/board.md`, `/schema` | no — re-rendered |
| `views/` | the Operator's saved navigator views, `<name>.view` files (UI state, never ledger data; revision 8) | worth copying: lost with the host otherwise (`dyad ledger view export <name>` prints one's SQL) |
| `venv/` | the pinned packages (`init`; `install` re-runs the pip line) | no — rebuilt from the manifest rows |
| `credentials` | the GitHub OAuth token, git's credential-store form, mode 0600, present only after `auth login` | no — `auth login` again; the old grant is revoked at GitHub by the Operator |
| `ledgerd.log` | macOS only (launchd has no journal); on Linux the user journal | no |

A fresh deployment is, in order: `init` (same `--github-client-id`; `--port` if the same port is wanted),
`install`, then `auth login` only if a private store is to be served. The first tick rebuilds the projection from
`main`. Nothing is restored, because nothing here is a source.

## The port and the `ui-url`
`init` selects the port (plan #336 revision 8): `--port N` if given, else it walks up from **8731** and takes the
first port a bind on the loopback address succeeds on, records `bind` in the conf, and prints
`ui-url: http://127.0.0.1:<port>/` as its last line. That line is authoritative; `dyad ledger status` and
`/health` (`ui_url`) repeat it, and the change-log row of `install` records it. One port serves the navigator
(`/`), the API (`/health`, `/schema`, `/query`, `/refresh`, `/views`) and the rendered views. `serve` refuses to
start on a port that is no longer free — `port <n> in use; run dyad ledger init --port <m> --force` — and never
moves silently, because the recorded URL is what the run-book cites. The run-book is written for 8731, the port
the rule selects first; if `init` on this host printed another, the run-book's lines are edited to it (a
workstation-zone PR) and this file records the port chosen:

- **Port chosen on this host:** not yet observed — written by the session that runs `init` here, with the
  `ui-url` it printed.

A loopback bind is the default. A LAN bind (`init --bind 0.0.0.0`) exposes a read-only projection of a public
repository plus the saved-views store (UI state, the one thing a LAN peer could change) and is the Operator's own
flag, never a default.

## Health
The run-book's `health`: `curl -fsS http://127.0.0.1:<port>/health`, pass criterion HTTP 200 and a body with
`"ok": true` and `pin` a 40-hex sha. `/health` also carries `refresh_every`, `last_tick`, `last_fetch_ok` (a failed
fetch leaves the last good build serving: `ok` stays true, `last_fetch_ok` says what is wrong), `ui_url`,
`auth` (`<login>` or `anonymous`) and `supervisor`. Run through `dyad runbook run ledgerd health`, whose event in
`../../runbooks/events/ledgerd.jsonl` is the completion evidence the deploying d-work cites (Rule-19 property 2).

## GitHub authentication (OAuth device flow)
The store adapter fetches with an OAuth token the Operator grants on their own device (plan #336 revision 7). The
repository is public today, so until the Operator logs in every fetch is anonymous and nothing is lost; the flow
exists because `ledgerd` serves any ledger, private ones included, and because the credential should be the
Operator's own.

**Register the OAuth App once** (the Operator's GitHub account; not a host action, not a corpus mutation):
1. GitHub → **Settings** → **Developer settings** → **OAuth Apps** → **New OAuth App**.
2. Application name `dyad-ledgerd`; any homepage URL; no authorization callback is needed for the device flow
   (GitHub requires the field — the homepage URL again is fine).
3. Tick **Enable Device Flow**. Register.
4. Copy the **Client ID** (public by design: it is what every device-flow CLI ships; instance data, stored in the
   conf, never in the package). No client secret is needed or used.
5. Give it to `init`: `dyad ledger init --state <dir> … --github-client-id <client id>`, or re-run `init` with it.
Not borrowed from another tool's registration (`gh`'s client id is theirs).

**Log in** — `dyad ledger auth login --state <dir>`: the command posts to `github.com/login/device/code`
(`scope=repo`), prints `Open https://github.com/login/device and enter the code XXXX-XXXX` (neither is a secret;
the code expires in 15 minutes), polls `login/oauth/access_token` at GitHub's interval while the Operator logs in
on any device, and writes the token to `<state>/credentials` (git's credential-store form, mode 0600) and
nowhere else — never printed, never in a reply, never in the repo. In a cloud session the Agent runs it in the
background and puts the link and code in its reply. `auth status` calls `api.github.com/user` with the token and
prints the login and scopes; `auth logout` deletes the file and revokes nothing on GitHub — the Operator revokes a
grant at GitHub → Settings → Applications → Authorized OAuth Apps. The git adapter passes the file as
`credential.helper=store --file <state>/credentials` only when it exists, so the token never appears on a command
line. Rotation is the run-book's `rotate-github-token` (Operator-run: the device is in the loop).

Manifest rows (Rule-14, `../../INFRASTRUCTURE.md`): `GitHub OAuth App dyad-ledgerd (device flow)` and the
supervisor, `systemd (user units, loginctl linger)` — on macOS launchd, observed where an install runs.

## Linger (Linux)
A systemd **user** unit runs only while the user's manager runs, which by default is while the user is logged in.
`loginctl enable-linger <user>` keeps the manager running from boot, so the unit starts without a login and
survives a logout. `dyad ledger install` attempts it; most distributions let a user enable linger for themselves,
and if polkit refuses it without `sudo` the installer reports that and exits 0 with the rest done, and the one line
is delivered as the ops script `../../ops/336-h4-linger.sh` (undo `336-h4-linger-undo.sh`) for the Operator to run
— with `sudo` by choice if their polkit asks for it (plan #336 revision 7, H4; revision 4, P6). Until linger is on
the service starts at login rather than at boot: degraded, not broken, and `status` shows it. Check:
`loginctl show-user "$USER" -p Linger` prints `Linger=yes`. macOS needs none of this: a launchd user agent with
`RunAtLoad` starts at login and `KeepAlive` restarts it.

## What was observed here
Written by the session that deploys on this host, after the change-log rows and the health event:
- `init`: port and `ui-url` — not yet observed.
- `install`: `systemctl --version` first line (the manifest row's version) — not yet observed.
- linger: enabled by `install`, or by the ops script — not yet observed.
- health: the event id in `../../runbooks/events/ledgerd.jsonl` — not yet observed.
