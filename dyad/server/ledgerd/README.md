# ledgerd — the core craft's server component (d-work #336)

`ledgerd` is a daemon that keeps a **queryable projection of a ledger** current. A ledger here is any
store of records a schema module can load; the first schema is the dyad's own d-work ledger (`rows/`,
`plans/`, `sessions/`, `provenance/`, `traces/` and the run-book events), the vocabulary's `ledger` being
its first instance (plan #336 revision 6, G6). The projection is one SQLite file rebuilt from the store's
**pin** — a commit sha for git, a content digest for a directory — whenever it moves (every
`refresh_every` seconds, default 60, and on `POST /refresh`), served over loopback HTTP as JSON, as
rendered text views (`/views/board.md`, `/board`) and as an HTML navigator. It is **never a source**: the
SQL text must be one `SELECT`/`WITH` statement and the connection is opened `mode=ro` with SQLite's own
authorizer denying every action but SELECT, READ and FUNCTION; a row changes through `dyad dwork` as
today. No clock, no timestamp and no version banner enters the database or a rendered view
(`crafts/syseng/rules/determinism.md` p3): two builds at one pin give one `iterdump()`.

A *server* is its own kind in the architecture (`crafts/syseng/rules/naming.md`, `dyad/server/<name>/`,
the component clause of `verifiable-code.md`): one directory holding the whole component, its own
`tests/` a test root the runner discovers, its model modules in the runner's invariant pass by their
`INVARIANTS` declarations, its imports in the manifest guard's scan. What makes it a server rather than
a script is Rule-19: its run-book and health command live at the instance
(`<host>/runbooks/ledgerd.md`, PR B of the plan).

## Layout
```
dyad/server/ledgerd/
  README.md                         this file
  ledgerd/__init__.py               the package (its version)
  ledgerd/core.py                   build, the refresh thread, the two read fences, renderers, saved views, the FastAPI app
  ledgerd/store.py                  the store-adapter seam: git, dir, module:<path>
  ledgerd/schema.py                 the ledger-schema seam: the contract, its check, the generic parsers
  ledgerd/auth.py                   GitHub OAuth device flow (stdlib urllib), the credential file
  ledgerd/supervisor.py             the supervisor seam: systemd, launchd, proc
  ledgerd/ui.py                     the htmx navigator's routes (Jinja2 fragments)
  ledgerd/cli.py                    `dyad ledger <verb> ...`
  ledgerd/schemas/dwork.py          the d-work schema — the ONE module that imports the guards' parsers
  templates/                        base, navigator, results, detail, sidebar (Jinja2)
  static/htmx.min.js                htmx 2.0.4, 0BSD, vendored (sha256 in dyad/infrastructure/INFRASTRUCTURE.md)
  dyad-ledgerd.service              systemd user-unit template ({python} {runner} {state} {log} filled at install)
  com.dyad.ledgerd.plist            launchd agent template, likewise
  tests/                            one test_<stem>.py per module; support.py holds the fixtures
```
The daemon modules (`core`, `store`, `schema`, `auth`, `supervisor`, `ui`, `cli`) import nothing under
`dyad/guards/` and know nothing of d-works; the `notes` schema in the tests — three `key: value` files
declared with the generic parsers — is the mechanical proof that the daemon serves any ledger.

## The three contracts
- **Store adapter** (`store.STORE_CONTRACT`): a module with `SCHEME` and `open(url, state, paths)`
  returning an object with `pin() -> str` (opaque; changes if and only if the content changed),
  `tree(pin, paths) -> Path` (the named paths at that pin, on disk) and `describe()`. The daemon performs
  one operation on a pin: equality. Shipped: `git` (`git+https://…`, `git+ssh://…`, `git+file:///…`,
  `#<ref>` default `main`; a mirror clone under `<state>/repo.git`, `git fetch` per pin, `git archive`
  for the tree, never a working tree); `dir` (`file:///…` or a bare path; pin = sha256 over the sorted
  relative paths and contents under the schema's STORES — the in-process fallback, honest about its pin);
  `module:<path>` (any Python file meeting the contract, loaded by path, checked by `store_problem`).
- **Ledger schema** (`schema.SCHEMA_CONTRACT`): `NAME`, `VERSION`, `STORES` (paths relative to the store
  root), `TABLES` (`{name: (columns, primary key)}`, a column a name or `(name, "integer")`), `VIEWS`
  (`{name: sql}`), `RENDERED` (views rendered to `<state>/views/<name>.md|.txt` on every refresh),
  `load(tree) -> {table: [row dict]}`, `INVARIANTS`; optional `DEFAULT_VIEW`, `DETAIL` (`{table: key
  column}` for the navigator's detail panel), `TREE_INVARIANTS`. Checked by `schema_problem`, the shape of
  `dyadlib.contract_problem`; `dyad ledger init --schema <name>` finds `ledgerd/schemas/<name>.py`,
  `--schema module:<path>` any file. A schema is Rule-12 code with its test; the daemon loads only the
  path `init` recorded in the conf, never anything from the store it serves (G2).
- **Supervisor adapter** (`supervisor.SUPERVISOR_CONTRACT`): `NAME`, `install`, `uninstall`, `start`,
  `stop`, `restart`, `status`, `is_active`, `logs`; each prints the native command line before running
  it. `hostadapter.supervisor()` picks one: `systemd` (Linux with a working `systemctl --user`: a user
  unit from the template, `enable --now`, `loginctl enable-linger` attempted and a refusal reported),
  `launchd` (macOS: `~/Library/LaunchAgents/com.dyad.ledgerd.plist`, `launchctl bootstrap gui/<uid>`),
  `proc` (anything else, a container: `serve` detached with a pid file under the state directory —
  **not persistent**, and it says so in `status` and `/health`).

## The CLI (`dyad ledger …`; the bare `dyad ledger` still renders LEDGER.md)
```
dyad ledger init --state <dir> --schema dwork --store git+https://github.com/<owner>/<repo>.git#main \
                 [--port N] [--refresh-every 60] [--bind 127.0.0.1] [--github-client-id <id>] [--force]
dyad ledger install --state <dir> [--python <interpreter>]      # <state>/venv + pip install of the manifest's pinned rows, a build, the supervisor
dyad ledger serve | build | status | start | stop | restart | logs | uninstall --state <dir>
dyad ledger query "<sql>" [--md] [--url <u> | --state <dir> | --at <sha>]
dyad ledger view <name> [--md]   |   dyad ledger board   |   dyad ledger schema
dyad ledger auth login | status | logout --state <dir>
```
`init` validates both contracts before it writes anything, chooses the port, writes `<state>/ledgerd.conf`
(`key: value` lines: schema, schema_version, store, bind, port, refresh_every, github_client_id, and
`venv` once `install` made one), builds once when the library rows are importable (else says so and
leaves the build to `install`), and prints **`ui-url: http://<bind>:<port>/`** as its last line. The
same values again print `0 changes`; different values are refused unless `--force`. The default
`--state` is `hostadapter.state_dir("ledgerd")`: `$XDG_STATE_HOME/dyad/ledgerd` (default
`~/.local/state/dyad/ledgerd`) on Linux, `~/Library/Application Support/dyad/ledgerd` on macOS.

**The `ui-url` rule.** `init` selects the port: `--port` when given, else the first port from 8731 on which
a bind to the configured address succeeds (a port in use fails the bind, the one reliable test). One port
serves the API and the UI (same origin). `serve` refuses a recorded port that is no longer free with the
one line that fixes it — `port <n> in use; run dyad ledger init --port <m> --force` — and never moves
silently, because the recorded URL is what the Operator and the run-book cite. `status`, `/health`
(`ui_url`) and the completion evidence print it. A LAN bind (`--bind 0.0.0.0`) is the Operator's explicit
flag: it exposes a read-only projection plus the saved-view writes, which are UI state, not the ledger.

**The client.** `query`, `view` and `board` ask the service (`--url`, else the conf under `--state`, else
the default state directory); when none answers they build **in process** from the current checkout
through the `dir` adapter (or from `<sha>` through the git adapter with `--at`) and print one line first:
`service unreachable (<reason>): built in-process from <pin>`. One code path, two homes for the database.

## Endpoints
`GET /health` (`ok`, `built_from`, `pin`, `schema`, `schema_version`, `store`, `tables`, `rows`,
`refresh_every`, `ticks`, `last_fetch_ok`, `last_error`, `supervisor`, `auth`, `ui_url`) · `GET /schema`
(the schema as data plus the built file reflected) · `POST /query` `{"sql": …}` → `{"columns", "rows",
"pin"}` (400 on refusal) · `POST /refresh` (one tick now) · `GET /views` · `GET /views/<name>.md|.txt`
(rendered) · `GET|PUT|DELETE /views/<name>` (saved views: `{"sql", "columns", "sort"}`, the SQL validated
by the read fence) · `GET /board` (the default view as text) · `GET /` (the navigator; `?view=<name>`,
`?sql=<encoded>`, `cols`, `sort`, `dir` reproduce a page) · `GET /ui/results|filter|detail|export|sidebar`,
`POST /ui/views`, `POST /ui/views/<name>/delete` (htmx fragments) · `GET /static/htmx.min.js` · `GET /docs`
(FastAPI's OpenAPI page).

## Authentication (the device-flow precondition)
A public repository is served anonymously; nothing of the Operator's `gh` login is read. For a private
ledger the git adapter authenticates with an OAuth token the Operator grants on their own device:
`dyad ledger auth login` prints `Open https://github.com/login/device and enter the code XXXX-XXXX`, polls
GitHub until the login completes, and writes `<state>/credentials` (git credential-store form, mode 0600,
never printed); every `git fetch`/`clone` then runs with `-c credential.helper="store --file
<state>/credentials"`. The flow needs the **client id of an OAuth App the Operator registers once** —
GitHub → Settings → Developer settings → OAuth Apps → New, name `dyad-ledgerd`, any homepage, no callback,
*Enable Device Flow* ticked — given to `init --github-client-id` (a client id is public by design; it is
instance data, never package). Until then `auth login` refuses with those five steps. `auth status` asks
`GET /user`; `auth logout` deletes the file and revokes nothing — the Operator revokes the grant on
GitHub's side.

## The per-instance venv
The five library rows — FastAPI, uvicorn, SQLAlchemy, Jinja2 (PyPI, pinned in
`dyad/infrastructure/INFRASTRUCTURE.md`, the one list `install` reads) and htmx (vendored) — are installed
by `dyad ledger install` into `<state>/venv`, never by `dyad install`, never into the host's Python. The
kernel-only path imports none of them: `dyad check --guards` prints `skip [invariant] ledgerd.core: needs
sqlalchemy …` on a host without the venv and the component's tests skip with one line; where the conf
names a venv, the runner adds its site-packages to the test child's path and the pass loads every module.
The unit and the plist run `<venv>/bin/python3 dyad/scripts/package.py ledger serve --state <dir>`.
