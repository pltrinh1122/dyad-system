"""ledgerd: the daemon core (plan #336 revisions 4-9). Kernel: Python 3.12+; library: SQLAlchemy Core,
FastAPI (pydantic models), uvicorn — installed per instance into `<state>/venv` by `dyad ledger install`,
never on the kernel-only path.
Build: store -> tree (the ledger's files at one pin) -> `schema.load(tree)` -> one SQLite file written
beside the live one and `os.replace`d — atomic for every reader, which opens a connection per request.
The `meta` table holds `built_from` (the pin), `schema` and `schema_version`; no clock, no timestamp,
no version banner enters the database (crafts/syseng/rules/determinism.md p3): two builds at one pin give
one `iterdump()`. Refresh: one thread, every `refresh_every` seconds, asks the store for its pin and
rebuilds (and re-renders the RENDERED views to `<state>/views/<name>.md|.txt`) only when it moved;
`POST /refresh` runs one tick now; a failed fetch leaves the last build serving and `/health` says
`last_fetch_ok: false` with the error. Never a source: two fences refuse every write — the SQL text must
be one SELECT/WITH statement (`read_statement`, the friendly refusal) and the connection is opened
`mode=ro` with `set_authorizer` denying every action but SELECT, READ and FUNCTION (`open_ro`, SQLite's
own). Saved views (`<state>/views/<name>.view`, `key: value` lines) are Operator state of the UI, never
ledger data, validated by the same fence before they are stored. Nothing here knows what a d-work is.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("core.py: Python 3.12+ required")
import csv, io, os, re, sqlite3, threading
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib
from ledgerd import schema as schema_mod, store as store_mod, auth
from sqlalchemy import Column, Integer, MetaData, Table, Text, create_engine, insert, inspect, text
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel

CONF = "ledgerd.conf"
DB = "ledgerd.db"
VIEWS_DIR = "views"
VIEW_EXT = ".view"
RENDER_EXTS = (".md", ".txt")
CONF_KEYS = ("schema", "schema_version", "store", "bind", "port", "refresh_every", "github_client_id", "venv")
DEFAULT_BIND, DEFAULT_PORT, DEFAULT_REFRESH = "127.0.0.1", 8731, 60
READ_ACTIONS = frozenset({sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION})
READ_KEYWORDS = ("SELECT", "WITH")
META_COLUMNS = ("key", "value")
_VIEW_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_LEADING_COMMENTS = re.compile(r"^(?:\s|--[^\n]*\n|/\*.*?\*/)*", re.S)

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("read-actions-are-select-read-function", lambda: READ_ACTIONS == {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}),
    ("read-keywords-are-select-and-with", lambda: set(READ_KEYWORDS) == {"SELECT", "WITH"}),
    ("conf-keys-distinct", lambda: len(set(CONF_KEYS)) == len(CONF_KEYS) and {"schema", "store", "bind", "port", "refresh_every"} <= set(CONF_KEYS)),
    ("defaults-sane", lambda: DEFAULT_PORT > 1024 and DEFAULT_REFRESH > 0 and DEFAULT_BIND == "127.0.0.1"),
    ("render-exts-are-md-and-txt", lambda: set(RENDER_EXTS) == {".md", ".txt"} and VIEW_EXT not in RENDER_EXTS),
    ("meta-columns-are-key-value", lambda: META_COLUMNS == ("key", "value")),
]

class QueryError(ValueError):
    """A statement the read fence refuses, or SQLite refused; its message is what the client sees."""

# ---- conf
def read_conf(state: Path) -> dict[str, str]:
    p = Path(state) / CONF
    if not p.is_file():
        raise FileNotFoundError(f"{p}: no ledgerd.conf (run dyad ledger init --state {state} ...)")
    return dyadlib.parse_kv(p.read_text())

def format_conf(conf: dict[str, str]) -> str:
    """`key: value` lines in CONF_KEYS order (one config, written by code, never typed)."""
    return "".join(f"{k}: {conf[k]}\n" for k in CONF_KEYS if k in conf and conf[k] != "")

def write_conf(state: Path, conf: dict[str, str]) -> Path:
    p = Path(state) / CONF; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(format_conf(conf)); return p

def ui_url(conf: dict[str, str]) -> str:
    return f"http://{conf.get('bind', DEFAULT_BIND)}:{conf.get('port', DEFAULT_PORT)}/"

# ---- the read fences
def _semicolon_outside_literals(sql: str) -> bool:
    i, n = 0, len(sql)
    while i < n:
        c = sql[i]
        if c in ("'", '"', "`"):
            j = sql.find(c, i + 1)
            while j != -1 and j + 1 < n and sql[j + 1] == c:   # a doubled quote inside the literal
                j = sql.find(c, j + 2)
            i = n if j == -1 else j + 1; continue
        if c == "[":
            j = sql.find("]", i + 1); i = n if j == -1 else j + 1; continue
        if sql.startswith("--", i):
            j = sql.find("\n", i); i = n if j == -1 else j + 1; continue
        if sql.startswith("/*", i):
            j = sql.find("*/", i + 2); i = n if j == -1 else j + 2; continue
        if c == ";":
            return True
        i += 1
    return False

def read_statement(sql: str) -> str:
    """The friendly fence: one complete SELECT or WITH statement, or QueryError saying why."""
    body = sql.strip()
    while body.endswith(";"):
        body = body[:-1].rstrip()
    if not body:
        raise QueryError("empty statement")
    if _semicolon_outside_literals(body):
        raise QueryError("one statement only (a `;` separates statements; the projection accepts one read statement)")
    if not sqlite3.complete_statement(body + ";"):
        raise QueryError("incomplete statement")
    head = body[_LEADING_COMMENTS.match(body).end():]
    first = re.match(r"[A-Za-z]+", head)
    if not first or first.group(0).upper() not in READ_KEYWORDS:
        raise QueryError(f"read-only: a query is one {' or '.join(READ_KEYWORDS)} statement (got {first.group(0).upper() if first else '?'})")
    return body

def _authorizer(action, arg1, arg2, db_name, trigger):
    return sqlite3.SQLITE_OK if action in READ_ACTIONS else sqlite3.SQLITE_DENY

def open_ro(db_path: Path) -> sqlite3.Connection:
    """The mechanical fence: `mode=ro` and SQLite's own authorizer denying everything but SELECT, READ and
    FUNCTION, so an UPDATE, a PRAGMA or an ATTACH is refused by the library, not by this module."""
    cx = sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro", uri=True, check_same_thread=False)
    cx.set_authorizer(_authorizer)
    return cx

def run_query(db_path: Path, sql: str, params=()) -> tuple[list[str], list[list]]:
    """(columns, rows) of one read statement through both fences; QueryError on refusal or SQL error."""
    body = read_statement(sql)
    cx = open_ro(db_path)
    try:
        try:
            cur = cx.execute(body, tuple(params))
        except sqlite3.Error as e:
            raise QueryError(str(e)) from None
        cols = [d[0] for d in cur.description or []]
        rows = [list(r) for r in cur.fetchall()]
    finally:
        cx.close()
    return cols, rows

# ---- renderers (deterministic: no clock, no banner)
def _cell(v) -> str:
    return "" if v is None else str(v).replace("\r", "").replace("\n", " ")

def render_md(columns: list[str], rows: list[list]) -> str:
    esc = lambda s: _cell(s).replace("|", "\\|")
    out = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"

def render_txt(columns: list[str], rows: list[list]) -> str:
    cells = [[_cell(c) for c in r] for r in rows]
    widths = [max([len(h)] + [len(r[i]) for r in cells]) for i, h in enumerate(columns)]
    line = lambda r: "  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip()
    return "\n".join([line(columns), line(["-" * w for w in widths])] + [line(r) for r in cells]) + "\n"

def render_csv(columns: list[str], rows: list[list]) -> str:
    buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n")
    w.writerow(columns); w.writerows([[_cell(c) for c in r] for r in rows])
    return buf.getvalue()

def render_view(db_path: Path, name: str, ext: str, header: str) -> str:
    cols, rows = run_query(db_path, f'SELECT * FROM "{name}"')
    body = render_md(cols, rows) if ext == ".md" else render_txt(cols, rows)
    return f"# {name} ({header})\n\n{body}"

# ---- the build (SQLAlchemy Core)
def metadata_for(mod) -> MetaData:
    md = MetaData()
    for name, (cols, pk) in mod.TABLES.items():
        keys = schema_mod.primary_key(mod, name)
        Table(name, md, *[Column(n, Integer if k == "integer" else Text, primary_key=n in keys) for n, k in (schema_mod.column_spec(c) for c in cols)])
    Table(schema_mod.META_TABLE, md, Column(META_COLUMNS[0], Text, primary_key=True), Column(META_COLUMNS[1], Text))
    return md

def _coerce(value, kind: str):
    if value is None:
        return None
    if kind == "integer":
        s = str(value).strip()
        if s == "":
            return None
        return int(s) if s.lstrip("-").isdigit() else s
    return value if isinstance(value, str) else str(value)

def normalize(mod, table: str, rows) -> list[dict]:
    """Every row with every column (absent -> None), kinds coerced, sorted by primary key then by every
    column — the insert order, so two builds at one pin give one dump."""
    specs = [schema_mod.column_spec(c) for c in mod.TABLES[table][0]]
    keys = schema_mod.primary_key(mod, table)
    out = [{n: _coerce(r.get(n), k) for n, k in specs} for r in rows]
    one = lambda v: (v is None, isinstance(v, str), 0 if v is None else v)   # None last; ints and strings never compared with each other
    return sorted(out, key=lambda r: tuple(one(r[k]) for k in keys) + tuple(one(r[n]) for n, _ in specs))

def build(store, mod, db_path: Path, pin: str | None = None) -> str:
    """store -> tree -> load -> SQLite, atomically replaced. Returns the pin built from."""
    db_path = Path(db_path); db_path.parent.mkdir(parents=True, exist_ok=True)
    pin = pin or store.pin()
    tree = store.tree(pin, mod.STORES)
    try:
        data = mod.load(Path(tree))
    finally:
        store_mod.remove_tree(tree)
    tmp = db_path.with_name(db_path.name + ".tmp")
    for p in (tmp, tmp.with_name(tmp.name + "-journal")):
        if p.exists():
            p.unlink()
    md = metadata_for(mod)
    engine = create_engine(f"sqlite:///{tmp}")
    try:
        md.create_all(engine)
        with engine.begin() as cx:
            for name in mod.TABLES:
                rows = normalize(mod, name, data.get(name, []))
                if rows:
                    cx.execute(insert(md.tables[name]), rows)
            for name, sql in mod.VIEWS.items():
                cx.execute(text(f'CREATE VIEW "{name}" AS {read_statement(sql)}'))
            cx.execute(insert(md.tables[schema_mod.META_TABLE]), [{"key": "built_from", "value": pin}, {"key": "schema", "value": mod.NAME},
                                                                  {"key": "schema_version", "value": str(mod.VERSION)}])
    finally:
        engine.dispose()
    os.replace(tmp, db_path)
    return pin

def built_from(db_path: Path) -> str | None:
    if not Path(db_path).is_file():
        return None
    cols, rows = run_query(db_path, f'SELECT value FROM "{schema_mod.META_TABLE}" WHERE key = \'built_from\'')
    return rows[0][0] if rows else None

def reflect(db_path: Path) -> dict:
    """`/schema` by reflection over the built file: tables with columns, views with their definitions."""
    engine = create_engine(f"sqlite:///file:{Path(db_path).resolve()}?mode=ro&uri=true")
    try:
        ins = inspect(engine)
        tables = {t: [{"name": c["name"], "type": str(c["type"]).lower()} for c in ins.get_columns(t)] for t in sorted(ins.get_table_names())}
        views = {v: (ins.get_view_definition(v) or "").strip() for v in sorted(ins.get_view_names())}
    finally:
        engine.dispose()
    return {"tables": tables, "views": views}

def counts(db_path: Path, mod) -> tuple[int, int]:
    total = 0
    for name in mod.TABLES:
        total += run_query(db_path, f'SELECT count(*) FROM "{name}"')[1][0][0]
    return len(mod.TABLES), total

# ---- saved views (Operator state of the UI, never ledger data)
def views_dir(state: Path) -> Path:
    return Path(state) / VIEWS_DIR

def saved_views(state: Path) -> list[str]:
    d = views_dir(state)
    return sorted(p.stem for p in d.glob(f"*{VIEW_EXT}")) if d.is_dir() else []

def read_view(state: Path, name: str) -> dict[str, str] | None:
    p = views_dir(state) / f"{name}{VIEW_EXT}"
    return dyadlib.parse_kv(p.read_text()) if p.is_file() else None

def save_view(state: Path, db_path: Path, mod, name: str, sql: str, columns: str = "", sort: str = "") -> Path:
    """Validated by the same read fence before it is stored (a write-shaped SQL is refused here), and run once
    so a view that cannot execute is never saved."""
    if not _VIEW_NAME.match(name or ""):
        raise QueryError("a view name is 1-64 letters, digits, `_` or `-`")
    if name in mod.VIEWS or name in mod.TABLES:
        raise QueryError(f"{name!r} is the schema's; a saved view takes another name")
    body = read_statement(sql)
    run_query(db_path, f"SELECT * FROM ({body}) LIMIT 0")
    d = views_dir(state); d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}{VIEW_EXT}"
    p.write_text(f"name: {name}\nsql: {' '.join(body.split())}\ncolumns: {' '.join(columns.split())}\nsort: {' '.join(sort.split())}\n")
    return p

def delete_view(state: Path, name: str) -> bool:
    p = views_dir(state) / f"{name}{VIEW_EXT}"
    if _VIEW_NAME.match(name or "") and p.is_file():
        p.unlink(); return True
    return False

# ---- the service
class Service:
    """One initialized instance: its state directory, conf, schema, store, database and refresh loop."""
    def __init__(self, state: Path, conf: dict[str, str] | None = None, supervisor: str = "", refresh_every: int | None = None):
        self.state = Path(state).resolve()
        self.conf = conf if conf is not None else read_conf(self.state)
        self.schema = schema_mod.load_schema(self.conf["schema"])
        self.store = store_mod.open_store(self.conf["store"], self.state, self.schema.STORES)
        self.supervisor = supervisor
        self.refresh_every = int(refresh_every if refresh_every is not None else self.conf.get("refresh_every", DEFAULT_REFRESH))
        self.db = self.state / DB
        self.lock = threading.Lock()
        self.pin = built_from(self.db) if self.db.is_file() else None
        self.last_fetch_ok, self.last_error, self.ticks = None, "", 0
        self._stop = threading.Event()
        self._thread = None
    def pin_label(self, pin: str | None = None) -> str:
        p = pin or self.pin
        return store_mod.pin_label(self.store, p) if p else "none"
    def header(self) -> str:
        return f"built from {self.pin_label()}; schema {self.schema.NAME} {self.schema.VERSION}"
    def render_all(self) -> list[Path]:
        d = views_dir(self.state); d.mkdir(parents=True, exist_ok=True)
        out = []
        for name in self.schema.RENDERED:
            for ext in RENDER_EXTS:
                p = d / f"{name}{ext}"; p.write_text(render_view(self.db, name, ext, self.header())); out.append(p)
        return out
    def build(self, pin: str | None = None) -> str:
        with self.lock:
            self.pin = build(self.store, self.schema, self.db, pin)
            self.render_all()
        return self.pin
    def tick(self) -> dict:
        """One refresh: ask the store for its pin; rebuild only when it moved. A fetch that fails leaves the last
        build serving and is reported, never raised."""
        self.ticks += 1
        try:
            pin = self.store.pin()
        except Exception as e:
            self.last_fetch_ok, self.last_error = False, f"{type(e).__name__}: {e}"
            return {"pin": self.pin_label(), "rebuilt": False, "last_fetch_ok": False, "error": self.last_error}
        self.last_fetch_ok, self.last_error = True, ""
        rebuilt = pin != self.pin or not self.db.is_file()
        if rebuilt:
            self.build(pin)
        return {"pin": self.pin_label(), "rebuilt": rebuilt, "last_fetch_ok": True, "error": ""}
    def _loop(self):
        while not self._stop.wait(self.refresh_every):
            self.tick()
    def start_refresh(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._loop, name="ledgerd-refresh", daemon=True); self._thread.start()
    def stop_refresh(self):
        self._stop.set()
    def health(self) -> dict:
        n_tables, n_rows = counts(self.db, self.schema) if self.db.is_file() else (0, 0)
        return {"ok": self.db.is_file(), "built_from": self.pin, "pin": self.pin_label(), "schema": self.schema.NAME,
                "schema_version": str(self.schema.VERSION), "store": self.store.describe(), "tables": n_tables, "rows": n_rows,
                "refresh_every": self.refresh_every, "ticks": self.ticks, "last_fetch_ok": self.last_fetch_ok, "last_error": self.last_error,
                "supervisor": self.supervisor or "", "auth": auth.health_label(self.state), "ui_url": ui_url(self.conf)}
    def query(self, sql: str, params=()) -> tuple[list[str], list[list]]:
        return run_query(self.db, sql, params)
    def rendered(self, name: str, ext: str) -> str | None:
        p = views_dir(self.state) / f"{name}{ext}"
        if name not in self.schema.RENDERED or ext not in RENDER_EXTS:
            return None
        if not p.is_file():
            self.render_all()
        return p.read_text()

# ---- the app (FastAPI; the UI routes join from ui.py)
class Query(BaseModel):
    sql: str

class SavedView(BaseModel):
    sql: str
    columns: list[str] = []
    sort: str = ""

def create_app(service: Service, with_ui: bool = True) -> FastAPI:
    app = FastAPI(title="ledgerd", docs_url="/docs", redoc_url=None)
    app.state.service = service

    @app.get("/health")
    def health():
        return service.health()

    @app.get("/schema")
    def schema_route():
        return {**schema_mod.describe(service.schema), "reflected": reflect(service.db) if service.db.is_file() else {}}

    @app.post("/query")
    def query_route(q: Query):
        try:
            cols, rows = service.query(q.sql)
        except QueryError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"columns": cols, "rows": rows, "pin": service.pin_label()}

    @app.post("/refresh")
    def refresh_route():
        return service.tick()

    @app.get("/views")
    def views_route():
        return {"schema": list(service.schema.VIEWS), "rendered": list(service.schema.RENDERED), "saved": saved_views(service.state),
                "default": schema_mod.default_view(service.schema)}

    @app.get("/views/{name}")
    def view_route(name: str):
        stem, ext = os.path.splitext(name)
        if ext in RENDER_EXTS:
            body = service.rendered(stem, ext)
            if body is None:
                raise HTTPException(status_code=404, detail=f"no rendered view {name}")
            return Response(body, media_type="text/markdown; charset=utf-8" if ext == ".md" else "text/plain; charset=utf-8")
        saved = read_view(service.state, name)
        if saved is not None:
            return {"name": name, "sql": saved.get("sql", ""), "columns": saved.get("columns", "").split(), "sort": saved.get("sort", ""), "saved": True}
        if name in service.schema.VIEWS:
            return {"name": name, "sql": service.schema.VIEWS[name], "saved": False}
        raise HTTPException(status_code=404, detail=f"no view {name}")

    @app.put("/views/{name}")
    def put_view(name: str, body: SavedView):
        existed = read_view(service.state, name) is not None
        try:
            p = save_view(service.state, service.db, service.schema, name, body.sql, " ".join(body.columns), body.sort)
        except QueryError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return JSONResponse({"name": name, "path": str(p)}, status_code=200 if existed else 201)

    @app.delete("/views/{name}")
    def delete_view_route(name: str):
        if not delete_view(service.state, name):
            raise HTTPException(status_code=404, detail=f"no saved view {name}")
        return {"deleted": name}

    @app.get("/board")
    def board():
        dv = schema_mod.default_view(service.schema)
        body = service.rendered(dv, ".txt") if dv else None
        if body is None:
            raise HTTPException(status_code=404, detail="the schema renders no default view")
        return PlainTextResponse(body)

    if with_ui:
        from ledgerd import ui
        ui.mount(app, service)
    return app

def serve(service: Service, bind: str, port: int, log_level: str = "warning") -> None:
    """Run the app under uvicorn, refreshing; returns when the server stops."""
    import uvicorn
    service.start_refresh()
    try:
        uvicorn.run(create_app(service), host=bind, port=port, log_level=log_level)
    finally:
        service.stop_refresh()

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
