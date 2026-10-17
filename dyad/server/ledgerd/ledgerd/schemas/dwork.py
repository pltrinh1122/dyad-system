"""ledgerd schema `dwork`: the dyad's d-work ledger (plan #336 revision 4's schema table) — the one ledgerd
module that imports the core craft's guards, because the tables are the guards' own parsers (Rule-13: one
parser per entity): rows (`dyadlib.parse_row_file`), dispositions (`provenance.dispositions` + `rows.ENTRY`),
refs, plans (`plans.parse` + `dyadlib.PLAN_PARTS`, with `why`/`how` the first sentence of the intent and
the mutation — what the board shows), plan_files (`sessions.files_touched`), sessions (`sessions.parse`,
+ session_rows, session_files), provenance (`provenance.parse`), traces (`trace.SECTIONS`), events
(`runbook.read_events`, `runbook.EVENT_FIELDS`). STORES are the ledger's paths relative to the repository
root: `<instance>/d-work` and `<host>/runbooks/events`, resolved from this checkout's own settings at
import (dyadlib.instance_rel, dyadlib.host_path; the defaults when no repository is at hand). Views:
`board` — every `open`, `planned` or `blocked` row with status, what, why, how (`(no plan)` without a
plan), who (`seat@holder` for every named seat claiming it, `-` when none; `unnamed-*` claims never
count) and the newest such seat's `seen`; `backlog`; `unheld` (board rows whose who is `-`). Kernel:
Python 3.12+ (nothing here needs the library rows).
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("dwork.py: Python 3.12+ required")
import os, re
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[2]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib
from ledgerd import schema as S

NAME, VERSION = "dwork", 1

def _instance_rel() -> str:
    """The instance's repo-relative path (`agent-corpus` by default), from this checkout when there is one. A store
    path is relative to the store root by contract, so an absolute `DYAD_INSTANCE` outside the checkout (a test's
    scratch copy) cannot be a store path and falls back to the default rather than failing the import."""
    try:
        rel = dyadlib.instance_rel(dyadlib.repo_root())
    except Exception:
        rel = None
    if rel:
        return rel
    v = os.environ.get("DYAD_INSTANCE", "").strip()
    return v.strip("/") if v and not v.startswith("/") and ".." not in Path(v).parts else "agent-corpus"

def _host_rel() -> str:
    try:
        return dyadlib.host_path(dyadlib.repo_root())
    except Exception:
        return dyadlib.DEFAULT_HOST

INSTANCE, HOST = _instance_rel(), _host_rel()
STORES = (f"{INSTANCE}/d-work", f"{HOST}/runbooks/events")
BOARD_STATES = ("open", "planned", "blocked")
EVENT_FIELDS = ("id", "ts", "role", "instance", "name", "cmd", "class", "scope", "exit", "duration_ms",
                "postcondition", "output_sha256", "output_tail", "commit", "runbook_sha256")   # runbook.EVENT_FIELDS (TREE_INVARIANTS pins it)
SESSION_FIELDS = ("session", "seen", "root", "rows", "files")                                   # sessions.FIELDS (pinned likewise)
PROVENANCE_FIELDS = ("n", "kind", "date", "note", "text")                                       # provenance.FIELDS
TRACE_SECTIONS = ("Timeline", "Buckets", "Counts", "Bottleneck", "Limits")                       # trace.SECTIONS
PLAN_PARTS = ("intent as read", "mutation", "files touched", "falsification")                    # dyadlib.PLAN_PARTS minus the base commit (a header field)
_part_column = lambda part: part.replace(" ", "_")
TABLES = {
    "rows": ((("id", "integer"),) + dyadlib.FIELDS[1:] + dyadlib.OPTIONAL_FIELDS, "id"),
    "dispositions": ((("row_id", "integer"), ("n", "integer"), "date", "verdict", "note", "entry"), ("row_id", "n")),
    "refs": ((("row_id", "integer"), ("n", "integer"), "token"), ("row_id", "n")),
    "plans": ((("id", "integer"), "title", "base_commit", "intent") + tuple(_part_column(p) for p in PLAN_PARTS) + ("why", "how"), "id"),
    "plan_files": ((("plan_id", "integer"), ("n", "integer"), "path"), ("plan_id", "n")),
    "sessions": (SESSION_FIELDS + ("writer", "host", "holder", "kernel", "os", "arch", "path"), "session"),
    "session_rows": (("session", ("row_id", "integer")), ("session", "row_id")),
    "session_files": (("session", "path"), ("session", "path")),
    "provenance": ((("row_id", "integer"), ("n", "integer")) + PROVENANCE_FIELDS[1:], ("row_id", "n")),
    "traces": ((("id", "integer"), "title") + tuple(s.lower() for s in TRACE_SECTIONS), "id"),
    "events": (tuple(("exit", "integer") if f == "exit" else ("duration_ms", "integer") if f == "duration_ms" else f for f in EVENT_FIELDS), "id"),
}
_WHO = ("(SELECT group_concat(x, ' ') FROM (SELECT s.session || '@' || COALESCE(NULLIF(s.holder, ''), '-') AS x "
        "FROM session_rows sr JOIN sessions s ON s.session = sr.session WHERE sr.row_id = r.id AND s.session NOT LIKE 'unnamed-%' ORDER BY s.session))")
_SEEN = ("(SELECT max(s.seen) FROM session_rows sr JOIN sessions s ON s.session = sr.session "
         "WHERE sr.row_id = r.id AND s.session NOT LIKE 'unnamed-%')")
VIEWS = {
    "board": ("SELECT r.id AS id, r.state AS status, r.title AS what, COALESCE(p.why, '(no plan)') AS why, COALESCE(p.how, '(no plan)') AS how, "
              f"COALESCE({_WHO}, '-') AS who, {_SEEN} AS seen FROM rows r LEFT JOIN plans p ON p.id = r.id "
              f"WHERE r.state IN ({', '.join(repr(s) for s in BOARD_STATES)}) ORDER BY r.id"),
    "backlog": "SELECT id, title AS what, opened FROM rows WHERE state = 'backlog' ORDER BY id",
    "unheld": "SELECT * FROM board WHERE who = '-'",
}
RENDERED = ("board", "backlog", "unheld")
DEFAULT_VIEW = "board"
DETAIL = {"rows": "id", "plans": "id", "dispositions": "row_id", "provenance": "row_id", "session_rows": "row_id"}
_TRACE_TITLE = re.compile(r"^# Trace #(\d+)\s+\S+\s+(.*)$")

INVARIANTS: list[dyadlib.Invariant] = [   # plan #336 revision 4: pure, enforced at import
    ("view-names-distinct", lambda: len(set(VIEWS)) == len(VIEWS) == 3),
    ("every-table-declares-a-key", lambda: all(bool(spec[1]) for spec in TABLES.values())),
    ("rows-columns-are-the-row-fields", lambda: tuple(S.column_spec(c)[0] for c in TABLES["rows"][0]) == dyadlib.FIELDS + dyadlib.OPTIONAL_FIELDS),
    ("rendered-are-views", lambda: set(RENDERED) <= set(VIEWS) and DEFAULT_VIEW in RENDERED),
    ("detail-keys-are-columns", lambda: all(t in TABLES and k in [S.column_spec(c)[0] for c in TABLES[t][0]] for t, k in DETAIL.items())),
    ("stores-are-two-relative-paths", lambda: len(STORES) == 2 and all(s and not s.startswith("/") for s in STORES)),
    ("board-states-are-the-live-states", lambda: set(BOARD_STATES) == dyadlib.STATES - dyadlib.TERMINAL_STATES - {"backlog"}),
    ("plan-parts-are-dyadlib-parts-minus-base", lambda: set(PLAN_PARTS) == set(dyadlib.PLAN_PARTS) - {"base commit"}),
    ("unheld-reads-the-board", lambda: "FROM board" in VIEWS["unheld"] and list(VIEWS).index("board") < list(VIEWS).index("unheld")),
]

def _guards() -> dict:
    """The guards' parsers, loaded once on first use (never at import: the daemon stays light)."""
    pkg = dyadlib.PKG
    return {"plans": dyadlib.load_guard("agent", "plans"), "sessions": dyadlib.load_guard("agent", "sessions"),
            "provenance": dyadlib.load_guard("agent", "provenance"), "rows": dyadlib.load_guard("agent", "rows"),
            "trace": dyadlib.load_module(pkg / "scripts" / "trace.py", "trace"), "runbook": dyadlib.load_module(pkg / "scripts" / "runbook.py", "runbook")}

TREE_INVARIANTS: list[dyadlib.Invariant] = [   # the columns pinned to the guards' own field tuples (they load modules)
    ("sessions-first-five-are-the-guard-fields", lambda: SESSION_FIELDS == _guards()["sessions"].FIELDS),
    ("provenance-columns-are-the-guard-fields", lambda: PROVENANCE_FIELDS == _guards()["provenance"].FIELDS),
    ("events-columns-are-event-fields", lambda: EVENT_FIELDS == _guards()["runbook"].EVENT_FIELDS),
    ("trace-sections-are-the-five", lambda: TRACE_SECTIONS == _guards()["trace"].SECTIONS),
    ("entry-shape-is-the-rows-guards", lambda: bool(_guards()["rows"].ENTRY.match("2026-01-01 Y plan")) and not _guards()["rows"].ENTRY.match("Y plan")),
]

# ---- parsers
def part_text(text: str, part: str) -> str:
    """The text of one plan part: the body under the first heading naming it (to the next heading of the same or
    a higher level), else the paragraph starting at the first line naming `<part>:`; '' when absent."""
    lines, low = text.splitlines(), part.lower()
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s*(.*)$", line)
        if m and low in m.group(2).lower():
            level, body = len(m.group(1)), []
            for nxt in lines[i + 1:]:
                h = re.match(r"^(#+)\s", nxt)
                if h and len(h.group(1)) <= level:
                    break
                body.append(nxt)
            return "\n".join(body).strip()
    for i, line in enumerate(lines):
        if re.search(rf"(?i)\b{re.escape(low)}\b[^:\n]*:", line):
            body = []
            for nxt in lines[i:]:
                if not nxt.strip() or (body and nxt.startswith("#")):
                    break
                body.append(nxt)
            return re.sub(r"^[*_\s]+", "", re.sub(rf"(?i)^.*?\b{re.escape(low)}\b[^:\n]*:\s*", "", "\n".join(body))).strip()
    return ""

def entry_parts(entry: str, ENTRY) -> tuple[str, str, str]:
    """(date, verdict, note) of one `disposed` entry; an entry outside the rows guard's shape keeps its text as the note."""
    if ENTRY.match(entry):
        return entry[:10], entry[11], entry[13:].strip()
    return "", "", entry

def trace_parts(text: str) -> tuple[str, str, dict[str, str]]:
    first = text.splitlines()[0] if text else ""
    m = _TRACE_TITLE.match(first)
    sections = S.md_sections(text)
    return (m.group(1) if m else ""), (m.group(2).strip() if m else ""), {s.lower(): sections.get(s, "") for s in TRACE_SECTIONS}

def load(tree: Path) -> dict[str, list[dict]]:
    """Every table from the ledger's files under `tree` (a repository tree, the STORES paths materialized)."""
    g = _guards()
    tree = Path(tree)
    out: dict[str, list[dict]] = {t: [] for t in TABLES}
    for p in S.read_tree(tree, f"{INSTANCE}/d-work/rows", "*.md"):
        if not p.stem.isdigit():
            continue
        row = dyadlib.parse_row_file(p.read_text())
        out["rows"].append({f: getattr(row, f) for f in dyadlib.FIELDS + dyadlib.OPTIONAL_FIELDS})
        for n, entry in enumerate(g["provenance"].dispositions(row.disposed), 1):
            date, verdict, note = entry_parts(entry, g["rows"].ENTRY)
            out["dispositions"].append({"row_id": row.id, "n": n, "date": date, "verdict": verdict, "note": note, "entry": entry})
        for n, tok in enumerate(row.refs.split(), 1):
            out["refs"].append({"row_id": row.id, "n": n, "token": tok})
    for p in S.read_tree(tree, f"{INSTANCE}/d-work/plans", "*.md"):
        if not p.stem.isdigit():
            continue
        text = p.read_text(errors="replace")
        d = g["plans"].parse(text)
        parts = {_part_column(part): part_text(text, part) for part in PLAN_PARTS}
        out["plans"].append({"id": int(p.stem), "title": d["title"], "base_commit": d["base commit"], "intent": d["intent"], **parts,
                             "why": S.first_sentence(parts["intent_as_read"]), "how": S.first_sentence(parts["mutation"])})
        for n, path in enumerate(g["sessions"].files_touched(text), 1):
            out["plan_files"].append({"plan_id": int(p.stem), "n": n, "path": path})
    for p in S.read_tree(tree, f"{INSTANCE}/d-work/sessions", "*.md"):
        f = g["sessions"].parse(p.read_text(errors="replace"))
        host = f.get("host", "").split()
        sid = f.get("session", p.stem)
        out["sessions"].append({**{k: f.get(k, "") for k in SESSION_FIELDS}, "session": sid, "writer": f.get("writer", ""), "host": f.get("host", ""),
                                "holder": f.get("holder", ""), "kernel": host[0] if len(host) > 0 else "", "os": host[1] if len(host) > 1 else "",
                                "arch": host[2] if len(host) > 2 else "", "path": p.name})
        for rid in sorted({r for r in f.get("rows", "").split() if r.isdigit()}, key=int):
            out["session_rows"].append({"session": sid, "row_id": int(rid)})
        for path in sorted(set(f.get("files", "").split())):
            out["session_files"].append({"session": sid, "path": path})
    for p in S.read_tree(tree, f"{INSTANCE}/d-work/provenance", "*.md"):
        if not p.stem.isdigit():
            continue
        for e in g["provenance"].parse(p.read_text(errors="replace")):
            out["provenance"].append({"row_id": int(p.stem), "n": int(e["n"]), "kind": e["kind"], "date": e["date"], "note": e["note"], "text": e["text"]})
    for p in S.read_tree(tree, f"{INSTANCE}/d-work/traces", "*.md"):
        if not p.stem.isdigit():
            continue
        tid, title, sections = trace_parts(p.read_text(errors="replace"))
        out["traces"].append({"id": int(p.stem), "title": title, **sections})
    for p in S.read_tree(tree, f"{HOST}/runbooks/events", "*.jsonl"):
        for e in g["runbook"].read_events(p):
            out["events"].append({f: e.get(f) for f in EVENT_FIELDS})
    return out

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
