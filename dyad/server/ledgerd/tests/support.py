"""Shared fixtures of the ledgerd suite (dyad/server/ledgerd/tests/; the component clause maps every
`ledgerd/**/<stem>.py` to `test_<stem>.py` here). Every test module skips, with one printed line naming what
is missing, when the library rows (`<state>/venv`, `dyad ledger install`) are not importable by this
interpreter — a host that serves no ledger never needs them (plan #336 revision 9). What is here:
`instance()` — a temporary git repository holding a d-work instance with rows at several states, a plan, a
named seat with a holder, an `unnamed-*` claim, a backlog row, a provenance record, a trace and a run-book
event; `notes_schema()` — a second schema, three `key: value` files declared with the generic parsers,
the mechanical proof that the daemon serves any ledger; `serve()` — uvicorn in a thread on a free port,
with `http()` as the stdlib client; and `Case`, the base class that skips."""
import importlib.util, json, shutil, socket, subprocess, sys, tempfile, threading, time, unittest, urllib.error, urllib.request
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
PKG = COMPONENT.parents[1]
for _p in (str(COMPONENT), str(PKG / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib

LIBS = ("fastapi", "uvicorn", "sqlalchemy", "jinja2")
MISSING = [n for n in LIBS if importlib.util.find_spec(n) is None]
if MISSING:
    print(f"skip [ledgerd tests] {', '.join(MISSING)} not importable by {sys.executable}: `dyad ledger install --state <dir>` creates <state>/venv (plan #336 revision 9)")

def requires_libs(cls):
    return unittest.skipIf(bool(MISSING), f"ledgerd needs {', '.join(MISSING)} (not installed)")(cls)

class Case(unittest.TestCase):
    """A test case of the component: skipped whole when the library rows are absent; a scratch directory per test."""
    @classmethod
    def setUpClass(cls):
        if MISSING:
            raise unittest.SkipTest(f"ledgerd needs {', '.join(MISSING)} (not installed)")
    def scratch(self, prefix="ledgerd-test-") -> Path:
        d = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

# ---- git helpers
def git(repo: Path, *a: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *a], text=True, env=dyadlib.git_env(), stderr=subprocess.STDOUT)

def commit(repo: Path, message: str = "x") -> str:
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", message)
    return git(repo, "rev-parse", "HEAD").strip()

def init_repo(d: Path) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main", str(d)], check=True, env=dyadlib.git_env())
    return d

# ---- the d-work instance fixture
ROWS = {
    1: ("open", "first open row", "2026-10-01 Y plan", "", ""),
    2: ("planned", "a planned row with a plan", "2026-10-02 Y plan; 2026-10-03 N done", "parent #1", ""),
    3: ("blocked", "a blocked row", "2026-10-02 N plan", "#2", ""),
    4: ("backlog", "a backlog row", "2026-10-04 Y backlog", "", ""),
    5: ("done", "a done row", "2026-10-01 Y plan; 2026-10-05 Y done (merges PR #9 at abc1234)", "", ""),
    6: ("open", "an accreted row", "2026-10-06 Y plan (mandate #2)", "parent #2", "implicit"),
}
PLAN_2 = """# Plan #2 — a planned row with a plan

## Intent as read
Build the thing the Operator asked for. Then build the next thing.

## Mutation
1. Write module a. Then test it.
2. Write module b.

files touched: dyad/scripts/a.py dyad/scripts/b.py dyad/tests/test_a.py

base commit: 0123456789abcdef0123456789abcdef01234567

## Falsification
| # | attack | result |
|---|---|---|
| A1 | it is wrong | refuted |
"""
PROVENANCE_2 = """# Provenance #2

## 1 prompt 2026-10-02
```
do the thing
```

## 2 disposition 2026-10-02
```
Y
```

## 3 disposition 2026-10-03
```
N: not yet
```
"""
TRACE_5 = """# Trace #5 — a done row

Sources: row `agent-corpus/d-work/rows/5.md`.

## Timeline

| UTC | actor | event |
|-----|-------|-------|
| 2026-10-01 10:00:00 | Operator | prompt |

## Buckets

Absent: no window.

## Counts

| count | value | source |
|-------|-------|--------|
| commits | 1 | git |

## Bottleneck

none

## Limits

none
"""
EVENT = {"id": "x-20261001T100000Z-status", "ts": "2026-10-01T10:00:00Z", "role": "agent", "instance": "x", "name": "status", "cmd": "true",
         "class": "read-only", "scope": "host", "exit": 0, "duration_ms": 12, "postcondition": "n/a", "output_sha256": "e3b0", "output_tail": "",
         "commit": "abc1234", "runbook_sha256": "deadbeef"}

def instance(d: Path | None = None, instance_rel: str = "agent-corpus", host_rel: str = "workstation-corpus") -> Path:
    """A temporary git repository with one d-work instance committed on `main`."""
    d = init_repo(Path(d) if d else Path(tempfile.mkdtemp(prefix="ledgerd-inst-")))
    dw = d / instance_rel / "d-work"
    for sub in ("rows", "plans", "sessions", "provenance", "traces"):
        (dw / sub).mkdir(parents=True, exist_ok=True)
    for rid, (state, title, disposed, refs, mode) in ROWS.items():
        row = dyadlib.Row(rid, title, "2026-10-01", state, disposed, refs, mode or "explicit")
        (dw / "rows" / f"{rid}.md").write_text(dyadlib.format_row_file(row))
    (dw / "plans" / "2.md").write_text(PLAN_2)
    (dw / "sessions" / "seat-a.md").write_text("session: seat-a\nseen: 2026-10-10T10:00:00+00:00\nroot: /tmp/x\nrows: 1 2\nfiles: dyad/scripts/a.py\n"
                                               "writer: 0123456789ab\nhost: cloud linux x86_64\nholder: holder-a\n")
    (dw / "sessions" / "seat-b.md").write_text("session: seat-b\nseen: 2026-10-11T10:00:00+00:00\nroot: /tmp/y\nrows: 2\nfiles: \nwriter: 0123456789ac\nhost: terminal linux x86_64\n")
    (dw / "sessions" / "unnamed-deadbeef0001.md").write_text("session: unnamed-deadbeef0001\nseen: 2026-10-12T10:00:00+00:00\nroot: /tmp/z\nrows: 1 3\nfiles: \n")
    (dw / "provenance" / "2.md").write_text(PROVENANCE_2)
    (dw / "traces" / "5.md").write_text(TRACE_5, encoding="utf-8")
    ev = d / host_rel / "runbooks" / "events"; ev.mkdir(parents=True, exist_ok=True)
    (ev / "x.jsonl").write_text(json.dumps(EVENT) + "\n")
    (d / "README.md").write_text("fixture\n")
    commit(d, "instance")
    return d

def add_row(d: Path, rid: int, title: str, state: str = "open", instance_rel: str = "agent-corpus") -> str:
    row = dyadlib.Row(rid, title, "2026-10-20", state, "2026-10-20 Y plan", "", "explicit")
    (d / instance_rel / "d-work" / "rows" / f"{rid}.md").write_text(dyadlib.format_row_file(row))
    return commit(d, f"row {rid}")

# ---- the second schema: three key: value files, declared with the generic parsers
NOTES_SCHEMA = '''"""notes: a second ledger schema for the tests — three `key: value` files under notes/, declared with the generic parsers."""
import sys
sys.path.insert(0, COMPONENT_PATH)
from ledgerd import schema as S
NAME, VERSION = "notes", 1
STORES = ("notes",)
TABLES = {"notes": (("name", "title", "owner", ("priority", "integer")), "name")}
VIEWS = {"open_notes": "SELECT name, title, owner FROM notes WHERE owner != '' ORDER BY priority DESC, name",
         "owners": "SELECT owner, count(*) AS n FROM notes GROUP BY owner ORDER BY owner"}
RENDERED = ("open_notes",)
DEFAULT_VIEW = "open_notes"
DETAIL = {"notes": "name"}
INVARIANTS = [("one-table", lambda: list(TABLES) == ["notes"])]
def load(tree):
    out = []
    for p in S.read_tree(tree, "notes", "*.md"):
        kv = S.kv_lines(p.read_text())
        out.append({"name": p.stem, "title": kv.get("title", ""), "owner": kv.get("owner", ""), "priority": kv.get("priority", "0")})
    return {"notes": out}
'''

def notes_schema(d: Path) -> Path:
    """Write the notes schema module beside a `notes/` store of three files under `d`; returns the module path."""
    (d / "notes").mkdir(parents=True, exist_ok=True)
    for name, title, owner, prio in (("alpha", "first note", "ann", 2), ("beta", "second note", "", 1), ("gamma", "third note", "bob", 3)):
        (d / "notes" / f"{name}.md").write_text(f"title: {title}\nowner: {owner}\npriority: {prio}\n")
    p = d / "notes_schema.py"
    p.write_text(NOTES_SCHEMA.replace("COMPONENT_PATH", repr(str(COMPONENT))))
    return p

# ---- the server in a thread
def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

class Served:
    def __init__(self, app):
        import uvicorn
        self.sock = socket.socket(); self.sock.bind(("127.0.0.1", 0)); self.port = self.sock.getsockname()[1]
        self.server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
        self.thread = threading.Thread(target=self.server.run, kwargs={"sockets": [self.sock]}, daemon=True)
        self.thread.start()
        for _ in range(200):
            if self.server.started:
                break
            time.sleep(0.02)
        self.base = f"http://127.0.0.1:{self.port}"
    def stop(self):
        self.server.should_exit = True
        self.thread.join(10)

def http(base: str, path: str, data=None, method: str | None = None, raw: bytes | None = None, headers: dict | None = None) -> tuple[int, str, dict]:
    """(status, body, headers) with the stdlib client; a JSON `data` is posted as such, `raw` as given."""
    body = json.dumps(data).encode() if data is not None else raw
    hdrs = {"Content-Type": "application/json"} if data is not None else ({"Content-Type": "application/x-www-form-urlencoded"} if raw is not None else {})
    hdrs.update(headers or {})
    req = urllib.request.Request(base + path, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace"), dict(e.headers)

def serve(case: Case, app) -> Served:
    s = Served(app)
    case.addCleanup(s.stop)
    return s
