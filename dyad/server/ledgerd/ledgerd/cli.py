"""ledgerd: the command line, reached as `dyad ledger <verb> ...` (`dyad/scripts/package.py` dispatches here;
the bare `dyad ledger` still renders LEDGER.md). Kernel: Python 3.12+; the verbs that build or serve need
the library rows (`<state>/venv`, made by `install`), and import them only then, so `install`, `auth`,
`schema` and the supervisor verbs run on the kernel alone.

  dyad ledger init --state <dir> --schema <name|module:path> --store <url> [--port N] [--refresh-every N]
                   [--bind <host>] [--github-client-id <id>] [--force]
        validate both contracts, choose a free port (walking up from 8731 on the bind address unless --port),
        write <state>/ledgerd.conf, build once (when the library rows are importable) and print
        `ui-url: http://<bind>:<port>/` last; the same values again print `0 changes`; different values are
        refused unless --force
  dyad ledger serve --state <dir> [--supervisor <name>]
        serve and refresh; refuses a recorded port that is no longer free with the line that fixes it
  dyad ledger build --state <dir>               one build now
  dyad ledger query "<sql>" [--md] [--url <u> | --state <dir> | --at <sha>] [--schema <name>]
        ask the service; when none answers, build in process from the current checkout (or from <sha>) and
        say so: `service unreachable (<reason>): built in-process from <pin>`
  dyad ledger view <name> [--md] [--url|--state]   a RENDERED view as text;  dyad ledger board = the default view
  dyad ledger schema [--state <dir> | --schema <name>]
  dyad ledger install --state <dir> [--python <interpreter>]
        create <state>/venv and install the pinned rows (from the manifest, the one list) unless --python
        names an interpreter that already has them; build through it; then the host's supervisor adapter
  dyad ledger uninstall | start | stop | restart | status | logs --state <dir>
  dyad ledger auth login | status | logout --state <dir>
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("cli.py: Python 3.12+ required")
import importlib.util, json, socket, subprocess, tempfile, urllib.error, urllib.request
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib, hostadapter
from ledgerd import schema as schema_mod, store as store_mod, auth, supervisor

VERBS = ("init", "serve", "build", "query", "view", "board", "schema", "install", "uninstall", "start", "stop", "restart", "status", "logs", "auth")
SUPERVISOR_VERBS = ("uninstall", "start", "stop", "restart", "status", "logs")
AUTH_VERBS = ("login", "status", "logout")
VALUE_FLAGS = ("--state", "--schema", "--store", "--port", "--refresh-every", "--bind", "--github-client-id", "--url", "--at", "--python", "--supervisor")
BARE_FLAGS = ("--force", "--md")
LIBS = ("fastapi", "uvicorn", "sqlalchemy", "jinja2")          # the library rows (dyad/infrastructure/INFRASTRUCTURE.md); importable or the venv is missing
LEDGERD_ROW_MARK = "by `dyad ledger install`"                   # the purpose cell of every row `install` pins (the four library rows and pydantic)
VENDORED_MARK = "vendored"                                      # a row shipped in the tree, never pip-installed (htmx)
MANIFEST = COMPONENT.parents[1] / "infrastructure" / "INFRASTRUCTURE.md"
DEFAULT_SCHEMA = "dwork"
PORT_START, PORT_LIMIT = 8731, 200
STATE_NAME = "ledgerd"                                          # hostadapter.state_dir(STATE_NAME) is the default --state
UNREACHABLE = "service unreachable ({reason}): built in-process from {pin}"

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("verbs-distinct", lambda: len(set(VERBS)) == len(VERBS)),
    ("supervisor-verbs-are-verbs", lambda: set(SUPERVISOR_VERBS) <= set(VERBS) and set(SUPERVISOR_VERBS) <= set(supervisor.SUPERVISOR_CONTRACT)),
    ("auth-verbs-are-three", lambda: AUTH_VERBS == ("login", "status", "logout")),
    ("flags-distinct", lambda: not (set(VALUE_FLAGS) & set(BARE_FLAGS)) and all(f.startswith("--") for f in VALUE_FLAGS + BARE_FLAGS)),
    ("libs-are-four", lambda: len(LIBS) == 4 and len(set(LIBS)) == 4),
    ("port-start-above-privileged", lambda: PORT_START > 1024 and PORT_LIMIT > 0),
]

def usage() -> str:
    return __doc__

def parse(argv: list[str]) -> tuple[list[str], dict[str, str], set[str]]:
    """(positionals, {flag: value}, {bare flags}); an unknown flag is refused before anything runs."""
    pos, flags, bare, i = [], {}, set(), 0
    while i < len(argv):
        a = argv[i]
        if a in VALUE_FLAGS:
            if i + 1 >= len(argv):
                raise ValueError(f"{a} needs a value")
            flags[a] = argv[i + 1]; i += 2
        elif a in BARE_FLAGS:
            bare.add(a); i += 1
        elif a.startswith("--"):
            raise ValueError(f"unknown flag {a}")
        else:
            pos.append(a); i += 1
    return pos, flags, bare

def libs_missing() -> list[str]:
    return [n for n in LIBS if importlib.util.find_spec(n) is None]

def pins(manifest: Path = MANIFEST) -> list[str]:
    """`name==version` for every manifest row whose purpose says `dyad ledger install` installs it and that is not
    vendored — the four library rows and the kernel's pydantic: the rows are the one list (revision 9), never a
    requirements file beside them; the version is the cell's first MAJOR.MINOR.PATCH token."""
    out = []
    for r in dyadlib.table_rows(manifest.read_text()):
        if len(r) < 7 or LEDGERD_ROW_MARK not in r[3] or VENDORED_MARK in r[2] + r[3]:
            continue
        version = next((t for t in r[2].split() if dyadlib.SEMVER.fullmatch(t)), None)
        if version:
            out.append(f"{dyadlib.plain(r[0]).strip().lower()}=={version}")
    return out

def port_free(bind: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        try:
            s.bind((bind, port)); return True
        except OSError:
            return False

def free_port(bind: str, start: int | None = None, limit: int = PORT_LIMIT) -> int:
    """The first port from `start` (default PORT_START) a bind on `bind` succeeds on — a port in use fails the bind, the one reliable test."""
    start = PORT_START if start is None else start
    for port in range(start, start + limit):
        if port_free(bind, port):
            return port
    raise RuntimeError(f"no free port in {start}..{start + limit - 1} on {bind}")

def _core():
    from ledgerd import core
    return core

def _state(flags: dict[str, str]) -> Path:
    return Path(flags.get("--state") or hostadapter.state_dir(STATE_NAME)).expanduser().resolve()

# ---- init
def cmd_init(flags: dict[str, str], bare: set[str], out=print) -> int:
    state = _state(flags)
    spec, url = flags.get("--schema"), flags.get("--store")
    if not spec or not url:
        out("init needs --schema <name|module:path> and --store <url>"); return 2
    try:                                                            # every refusal before the first write
        mod = schema_mod.load_schema(spec)
        adapter = store_mod.adapter_for(url)
        if getattr(adapter, "SCHEME", "") == "dir":
            adapter.open(url, None, mod.STORES)
    except (ValueError, OSError) as e:
        out(f"init refused: {e}"); return 1
    bind = flags.get("--bind", "127.0.0.1")
    refresh = flags.get("--refresh-every", "60")
    if not refresh.isdigit() or int(refresh) <= 0:
        out("init refused: --refresh-every must be a positive number of seconds"); return 1
    existing = dyadlib.parse_kv((state / "ledgerd.conf").read_text()) if (state / "ledgerd.conf").is_file() else {}
    if "--port" in flags:
        if not flags["--port"].isdigit():
            out("init refused: --port must be a number"); return 1
        port = int(flags["--port"])
    elif existing.get("port", "").isdigit() and existing.get("bind", bind) == bind and port_free(bind, int(existing["port"])):
        port = int(existing["port"])
    else:
        port = free_port(bind)
    conf = {"schema": spec, "schema_version": str(mod.VERSION), "store": url, "bind": bind, "port": str(port), "refresh_every": refresh,
            "github_client_id": flags.get("--github-client-id", existing.get("github_client_id", ""))}
    if existing.get("venv"):
        conf["venv"] = existing["venv"]
    same = {k: v for k, v in existing.items() if k != "venv"} == {k: v for k, v in conf.items() if k != "venv" and v != ""}
    if existing and not same and "--force" not in bare:
        out(f"init refused: {state / 'ledgerd.conf'} holds different values; pass --force to replace them")
        for k in sorted(set(existing) | set(conf)):
            if existing.get(k, "") != conf.get(k, "") and k != "venv":
                out(f"  {k}: {existing.get(k, '(absent)')} -> {conf.get(k, '(absent)')}")
        return 1
    missing = libs_missing()
    if same:
        out("0 changes")
    else:
        state.mkdir(parents=True, exist_ok=True)
        p = _write_conf(state, conf)
        out(f"wrote {p}")
    if missing:
        out(f"build skipped: {', '.join(missing)} not importable here; `dyad ledger install --state {state}` creates {state / 'venv'} and builds")
    else:
        core = _core()
        service = core.Service(state, conf)
        if not same or not service.db.is_file():
            pin = service.build()
            out(f"built {service.db} from {service.pin_label(pin)}; rendered {', '.join(service.schema.RENDERED) or 'nothing'}")
    out(f"ui-url: http://{bind}:{port}/")
    return 0

def _write_conf(state: Path, conf: dict[str, str]) -> Path:
    """`core.write_conf` without importing core (the kernel-only init before the venv exists): the same
    `key: value` lines in the same order."""
    keys = ("schema", "schema_version", "store", "bind", "port", "refresh_every", "github_client_id", "venv")
    p = state / "ledgerd.conf"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(f"{k}: {conf[k]}\n" for k in keys if k in conf and conf[k] != ""))
    return p

# ---- serve, build
def cmd_serve(flags: dict[str, str], out=print) -> int:
    core = _core()
    state = _state(flags)
    conf = core.read_conf(state)
    bind, port = conf.get("bind", core.DEFAULT_BIND), int(conf.get("port", core.DEFAULT_PORT))
    if not port_free(bind, port):
        out(f"port {port} in use; run dyad ledger init --port {free_port(bind, port + 1)} --force"); return 1
    service = core.Service(state, conf, supervisor=flags.get("--supervisor") or hostadapter.supervisor())
    if not service.db.is_file():
        service.build()
    out(f"ledgerd serving {service.schema.NAME} from {service.store.describe()} at {core.ui_url(conf)} (refresh every {service.refresh_every} s; supervisor {service.supervisor})")
    core.serve(service, bind, port)
    return 0

def cmd_build(flags: dict[str, str], out=print) -> int:
    core = _core()
    state = _state(flags)
    service = core.Service(state)
    pin = service.build()
    out(f"built {service.db} from {service.pin_label(pin)}; rendered {', '.join(service.schema.RENDERED) or 'nothing'}")
    return 0

# ---- the client: query, view, board, schema
def service_url(flags: dict[str, str]) -> str | None:
    if flags.get("--url"):
        return flags["--url"].rstrip("/")
    if flags.get("--state"):
        p = Path(flags["--state"]).expanduser() / "ledgerd.conf"
        if p.is_file():
            conf = dyadlib.parse_kv(p.read_text())
            return f"http://{conf.get('bind', '127.0.0.1')}:{conf.get('port', PORT_START)}"
        return None
    p = Path(hostadapter.state_dir(STATE_NAME)) / "ledgerd.conf"
    if p.is_file():
        conf = dyadlib.parse_kv(p.read_text())
        return f"http://{conf.get('bind', '127.0.0.1')}:{conf.get('port', PORT_START)}"
    return None

def ask(url: str, path: str, body: dict | None = None, timeout: float = 10.0) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url + path, data=data, headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")

def local_service(flags: dict[str, str]):
    """The in-process fallback: the same core over a `dir` store of the current checkout — or, with `--at <sha>`,
    the git adapter reading that commit of the checkout's own repository — built into a temporary state."""
    core = _core()
    spec = flags.get("--schema") or DEFAULT_SCHEMA
    if flags.get("--state") and (Path(flags["--state"]).expanduser() / "ledgerd.conf").is_file():
        spec = dyadlib.parse_kv((Path(flags["--state"]).expanduser() / "ledgerd.conf").read_text()).get("schema", spec)
    root = dyadlib.repo_root()
    state = Path(tempfile.mkdtemp(prefix="ledgerd-local-"))
    url = f"git+file://{root}#{flags['--at']}" if flags.get("--at") else f"file://{root}"
    conf = {"schema": spec, "store": url, "bind": "127.0.0.1", "port": "0", "refresh_every": "0"}
    service = core.Service(state, conf)
    if flags.get("--at"):
        service.store = store_mod.GitStore.local(root, flags["--at"])
    service.build()
    return service

def cmd_query(pos: list[str], flags: dict[str, str], bare: set[str], out=print) -> int:
    if not pos:
        out("query needs the SQL text"); return 2
    sql = " ".join(pos)
    url = service_url(flags) if not flags.get("--at") else None
    reason = None
    if url:
        try:
            code, body = ask(url, "/query", {"sql": sql})
            if code == 200:
                r = json.loads(body)
                out(_render(r["columns"], r["rows"], "--md" in bare) + f"asof {r['pin']}")
                return 0
            if code == 400:
                out(f"refused: {json.loads(body).get('detail', body)}"); return 1
            reason = f"HTTP {code} from {url}"
        except (OSError, ValueError) as e:
            reason = f"{type(e).__name__}: {e}"
    else:
        reason = f"at {flags['--at']}" if flags.get("--at") else "no service configured"
    core = _core()
    service = local_service(flags)
    out(UNREACHABLE.format(reason=reason, pin=service.pin_label()))
    try:
        cols, rows = service.query(sql)
    except core.QueryError as e:
        out(f"refused: {e}"); return 1
    out(_render(cols, rows, "--md" in bare) + f"asof {service.pin_label()}")
    return 0

def _render(cols, rows, md: bool) -> str:
    core = _core()
    return core.render_md(cols, rows) if md else core.render_txt(cols, rows)

def cmd_view(pos: list[str], flags: dict[str, str], bare: set[str], out=print, default: bool = False) -> int:
    url = service_url(flags)
    ext = ".md" if "--md" in bare else ".txt"
    name = pos[0] if pos else None
    if url and (name or default):
        try:
            if default:
                code, body = ask(url, "/views")
                if code == 200:
                    name = json.loads(body).get("default") or name
            code, body = ask(url, f"/views/{name}{ext}")
            if code == 200:
                out(body.rstrip("\n")); return 0
            reason = f"HTTP {code} from {url}"
        except (OSError, ValueError) as e:
            reason = f"{type(e).__name__}: {e}"
    else:
        reason = "no service configured"
    core = _core()
    service = local_service(flags)
    name = name or schema_mod.default_view(service.schema)
    if name not in service.schema.RENDERED:
        out(f"{name!r} is not a rendered view of {service.schema.NAME} ({', '.join(service.schema.RENDERED)})"); return 1
    out(UNREACHABLE.format(reason=reason, pin=service.pin_label()))
    out(core.render_view(service.db, name, ext, service.header()).rstrip("\n"))
    return 0

def cmd_schema(flags: dict[str, str], out=print) -> int:
    spec = flags.get("--schema") or DEFAULT_SCHEMA
    if flags.get("--state") and (Path(flags["--state"]).expanduser() / "ledgerd.conf").is_file():
        spec = dyadlib.parse_kv((Path(flags["--state"]).expanduser() / "ledgerd.conf").read_text()).get("schema", spec)
    mod = schema_mod.load_schema(spec)
    d = schema_mod.describe(mod)
    out(f"schema {d['name']} {d['version']}; stores: {', '.join(d['stores'])}")
    for t, spec_ in d["tables"].items():
        out(f"  table {t} (key {', '.join(spec_['primary_key'])}): " + ", ".join(f"{n}:{k}" if k != "text" else n for n, k in spec_["columns"]))
    for v, sql in d["views"].items():
        out(f"  view {v}{' [rendered]' if v in d['rendered'] else ''}{' [default]' if v == d['default_view'] else ''}: {' '.join(sql.split())}")
    if d["detail"]:
        out("  detail: " + ", ".join(f"{t}.{k}" for t, k in d["detail"].items()))
    return 0

# ---- install and the supervisor verbs
def cmd_install(flags: dict[str, str], out=print, run=subprocess.run) -> int:
    state = _state(flags)
    if not (state / "ledgerd.conf").is_file():
        out(f"install needs an initialized state: dyad ledger init --state {state} ..."); return 1
    conf = dyadlib.parse_kv((state / "ledgerd.conf").read_text())
    python = flags.get("--python")
    if not python:
        venv = state / "venv"
        python = str(venv / "bin" / "python3")
        if not Path(python).is_file():
            argv = [sys.executable, "-m", "venv", str(venv)]
            out("$ " + " ".join(argv)); run(argv, check=True)
        argv = [python, "-m", "pip", "install", "--quiet", *pins()]
        out("$ " + " ".join(argv)); run(argv, check=True)
    conf["venv"] = str(Path(python).resolve().parent.parent) if not flags.get("--python") else conf.get("venv", "")
    _write_conf(state, conf)
    argv = [python, str(supervisor.RUNNER), "ledger", "build", "--state", str(state)]
    out("$ " + " ".join(argv)); r = run(argv, capture_output=True, text=True)
    out((r.stdout or "").rstrip())
    if r.returncode:
        out((r.stderr or "").rstrip()); return r.returncode
    name = hostadapter.supervisor()
    out(f"supervisor: {name}")
    return supervisor.adapter(name, state, python=python, out=out).install()

def cmd_supervisor(verb: str, flags: dict[str, str], out=print) -> int:
    state = _state(flags)
    conf = dyadlib.parse_kv((state / "ledgerd.conf").read_text()) if (state / "ledgerd.conf").is_file() else {}
    python = str(Path(conf["venv"]) / "bin" / "python3") if conf.get("venv") else sys.executable
    adapter = supervisor.adapter(flags.get("--supervisor") or hostadapter.supervisor(), state, python=python, out=out)
    rc = getattr(adapter, verb)()
    return int(rc or 0)

def cmd_auth(pos: list[str], flags: dict[str, str], out=print) -> int:
    if not pos or pos[0] not in AUTH_VERBS:
        out(f"auth takes one of {', '.join(AUTH_VERBS)}"); return 2
    state = _state(flags)
    if pos[0] == "login":
        conf = dyadlib.parse_kv((state / "ledgerd.conf").read_text()) if (state / "ledgerd.conf").is_file() else {}
        return auth.login(state, conf.get("github_client_id") or None, out=out)
    if pos[0] == "status":
        s = auth.status(state)
        out("anonymous (no credentials stored)" if s.get("anonymous") else f"login {s.get('login') or '?'}; scopes {s.get('scopes') or '(none)'}; HTTP {s.get('http')}")
        return 0 if s.get("anonymous") or s.get("ok") else 1
    out("logged out: credentials removed (revoke the grant on GitHub to retire the token)" if auth.logout(state) else "nothing to log out")
    return 0

def main(argv: list[str] | None = None, out=print) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] not in VERBS:
        out(usage()); return 2
    verb = a[0]
    try:
        pos, flags, bare = parse(a[1:])
    except ValueError as e:
        out(f"{verb}: {e}"); out(usage()); return 2
    try:
        if verb == "init":
            return cmd_init(flags, bare, out)
        if verb == "serve":
            return cmd_serve(flags, out)
        if verb == "build":
            return cmd_build(flags, out)
        if verb == "query":
            return cmd_query(pos, flags, bare, out)
        if verb == "view":
            return cmd_view(pos, flags, bare, out)
        if verb == "board":
            return cmd_view([], flags, bare, out, default=True)
        if verb == "schema":
            return cmd_schema(flags, out)
        if verb == "install":
            return cmd_install(flags, out)
        if verb in SUPERVISOR_VERBS:
            return cmd_supervisor(verb, flags, out)
        return cmd_auth(pos, flags, out)
    except ImportError as e:
        out(f"{verb}: {e}; the library rows are installed per instance by `dyad ledger install --state <dir>` into <state>/venv"); return 1
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        out(f"{verb}: {e}"); return 1

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding

if __name__ == "__main__":
    sys.exit(main())
