"""ledgerd: the ledger-schema seam (crafts/syseng/rules/invariants.md). Kernel: Python 3.12+, stdlib.
A ledger schema is a Python module meeting SCHEMA_CONTRACT: `NAME`, `VERSION` (the schema's, written
into the `meta` table), `STORES` (the ledger's paths relative to the store root, what the store adapter
materializes), `TABLES` (`{name: (columns, primary key)}`; a column is a name or `(name, kind)` with
kind `text` or `integer`), `VIEWS` (`{name: sql}`), `RENDERED` (the views rendered to files on every
refresh), `load(tree) -> {table: [row dict, ...]}` and `INVARIANTS`; optionally `DEFAULT_VIEW` (the
view the navigator opens on; the first of RENDERED when absent), `DETAIL` (`{table: key column}` for
the detail panel) and `TREE_INVARIANTS`. `schema_problem(mod)` is the one check, in the shape of
`dyadlib.contract_problem`. The generic parsers (`kv_lines`, `jsonl`, `md_table`, `md_sections`) are
what a simple ledger declares its `load` with; a schema whose parser a guard already owns uses the
guard's (Rule-13). This module knows nothing of d-works: the first schema is `schemas/dwork.py`.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("schema.py: Python 3.12+ required")
import json, re
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]                 # dyad/server/ledgerd
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):   # the component root; dyad/scripts
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib

SCHEMA_CONTRACT = ("NAME", "VERSION", "STORES", "TABLES", "VIEWS", "RENDERED", "load", "INVARIANTS")
SCHEMA_OPTIONAL = ("DEFAULT_VIEW", "DETAIL", "TREE_INVARIANTS")
COLUMN_KINDS = ("text", "integer")
DEFAULT_KIND = "text"
SCHEMAS_DIR = COMPONENT / "ledgerd" / "schemas"
MODULE_PREFIX = "module:"
META_TABLE = "meta"                                              # the core's own table: key, value
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("contract-names-distinct", lambda: len(set(SCHEMA_CONTRACT)) == len(SCHEMA_CONTRACT)),
    ("optional-disjoint-from-contract", lambda: not (set(SCHEMA_OPTIONAL) & set(SCHEMA_CONTRACT))),
    ("contract-has-load-and-invariants", lambda: "load" in SCHEMA_CONTRACT and "INVARIANTS" in SCHEMA_CONTRACT),
    ("default-kind-is-a-kind", lambda: DEFAULT_KIND in COLUMN_KINDS and len(set(COLUMN_KINDS)) == 2),
    ("meta-table-is-a-name", lambda: bool(_NAME.match(META_TABLE))),
]

# ---- the contract
def column_spec(c) -> tuple[str, str]:
    """(name, kind) of one column declaration: a bare name is `text`."""
    if isinstance(c, str):
        return c, DEFAULT_KIND
    return c[0], c[1]

def columns_of(mod, table: str) -> list[str]:
    return [column_spec(c)[0] for c in mod.TABLES[table][0]]

def schema_problem(mod) -> str | None:
    """None when `mod` is a ledger schema; else the problem text (the shape of dyadlib.contract_problem)."""
    missing = [n for n in SCHEMA_CONTRACT if not hasattr(mod, n)]
    if missing:
        return f"lacks {', '.join(missing)} (ledger schema contract, dyad/server/ledgerd/README.md)"
    if not isinstance(mod.NAME, str) or not _NAME.match(mod.NAME):
        return f"NAME {mod.NAME!r} is not an identifier"
    if not isinstance(mod.STORES, (list, tuple)) or not mod.STORES or not all(isinstance(s, str) and s and not s.startswith("/") for s in mod.STORES):
        return "STORES must be a non-empty tuple of relative paths"
    if not isinstance(mod.TABLES, dict) or not mod.TABLES:
        return "TABLES must be a non-empty dict {name: (columns, primary key)}"
    for name, spec in mod.TABLES.items():
        if not _NAME.match(str(name)) or name == META_TABLE:
            return f"table {name!r}: not a legal name (and never {META_TABLE!r}, the core's own)"
        if not (isinstance(spec, tuple) and len(spec) == 2):
            return f"table {name!r}: expected (columns, primary key)"
        cols, pk = spec
        try:
            names = [column_spec(c)[0] for c in cols]
            kinds = [column_spec(c)[1] for c in cols]
        except (TypeError, IndexError):
            return f"table {name!r}: a column is a name or (name, kind)"
        if not names or len(set(names)) != len(names) or not all(_NAME.match(n) for n in names):
            return f"table {name!r}: columns must be distinct identifiers"
        if any(k not in COLUMN_KINDS for k in kinds):
            return f"table {name!r}: column kinds are {', '.join(COLUMN_KINDS)}"
        keys = (pk,) if isinstance(pk, str) else tuple(pk)
        if not keys or any(k not in names for k in keys):
            return f"table {name!r}: primary key {pk!r} is not among its columns"
    if not isinstance(mod.VIEWS, dict) or not all(_NAME.match(str(v)) and isinstance(s, str) and s.strip() for v, s in mod.VIEWS.items()):
        return "VIEWS must be a dict {name: sql}"
    if set(mod.VIEWS) & set(mod.TABLES):
        return "a view may not share a table's name"
    if not isinstance(mod.RENDERED, (list, tuple)) or any(v not in mod.VIEWS for v in mod.RENDERED):
        return "RENDERED must name views of VIEWS"
    if not callable(mod.load):
        return "load is not callable"
    if not isinstance(mod.INVARIANTS, (list, tuple)):
        return "INVARIANTS is not a list"
    dv = getattr(mod, "DEFAULT_VIEW", None)
    if dv is not None and dv not in mod.VIEWS:
        return f"DEFAULT_VIEW {dv!r} is not a view"
    detail = getattr(mod, "DETAIL", None)
    if detail is not None and (not isinstance(detail, dict) or any(t not in mod.TABLES or k not in columns_of(mod, t) for t, k in detail.items())):
        return "DETAIL must map a table to one of its columns"
    return None

def default_view(mod) -> str | None:
    """The navigator's opening view: DEFAULT_VIEW, else the first RENDERED view, else the first view."""
    dv = getattr(mod, "DEFAULT_VIEW", None)
    if dv:
        return dv
    if mod.RENDERED:
        return mod.RENDERED[0]
    return next(iter(mod.VIEWS), None)

def detail_of(mod) -> dict[str, str]:
    return dict(getattr(mod, "DETAIL", None) or {})

def primary_key(mod, table: str) -> tuple[str, ...]:
    pk = mod.TABLES[table][1]
    return (pk,) if isinstance(pk, str) else tuple(pk)

def load_schema(spec: str):
    """The schema module `spec` names: `<name>` is `schemas/<name>.py` here; `module:<path>` any file. The
    module is loaded by path (`dyadlib.load_module`) and checked against the contract; a problem raises
    ValueError before anything is written (the init refusal)."""
    if spec.startswith(MODULE_PREFIX):
        path = Path(spec[len(MODULE_PREFIX):]).expanduser().resolve()
        name = f"ledgerd_schema_{path.stem}"
    else:
        if not _NAME.match(spec):
            raise ValueError(f"schema {spec!r}: not a shipped schema name nor module:<path>")
        path = SCHEMAS_DIR / f"{spec}.py"
        name = f"ledgerd.schemas.{spec}"
    if not path.is_file():
        raise ValueError(f"schema {spec!r}: no module at {path}")
    mod = dyadlib.load_module(path, name)
    problem = schema_problem(mod)
    if problem:
        raise ValueError(f"schema {spec!r}: {problem}")
    return mod

def describe(mod) -> dict:
    """The schema as data (`dyad ledger schema`, `GET /schema`): tables with columns and keys, views, rendered."""
    return {"name": mod.NAME, "version": str(mod.VERSION), "stores": list(mod.STORES),
            "tables": {t: {"columns": [list(column_spec(c)) for c in spec[0]], "primary_key": list(primary_key(mod, t))} for t, spec in mod.TABLES.items()},
            "views": dict(mod.VIEWS), "rendered": list(mod.RENDERED), "default_view": default_view(mod), "detail": detail_of(mod)}

# ---- generic parsers: what a simple ledger declares its `load` with
def kv_lines(text: str) -> dict[str, str]:
    """`key: value` lines (the row-file form); blank and `#` lines skipped. The one definition is dyadlib's."""
    return dyadlib.parse_kv(text)

def jsonl(text: str) -> list[dict]:
    """One JSON object per non-blank line; a malformed line raises ValueError naming it."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"line {i}: not a JSON object ({e.msg})") from None
    return out

def md_table(text: str) -> tuple[list[str], list[list[str]]]:
    """The first markdown table: (header cells, body rows); dyadlib's reader."""
    return dyadlib.table_header(text), dyadlib.table_rows(text)

def md_sections(text: str, level: int = 2) -> dict[str, str]:
    """{heading: body} for every `## ` heading (or another level), bodies stripped, in file order; text before
    the first heading is under ''."""
    marker = "#" * level + " "
    out, current, body = {}, "", []
    for line in text.splitlines():
        if line.startswith(marker):
            out[current] = "\n".join(body).strip(); current, body = line[len(marker):].strip(), []
        else:
            body.append(line)
    out[current] = "\n".join(body).strip()
    if "" in out and not out[""]:
        del out[""]
    return out

def first_sentence(text: str) -> str:
    """The first sentence of a paragraph (to the first `.`, `!` or `?` followed by a space or the end), one line;
    a leading list marker (`1.`, `-`, `*`) or a heading's `#` is not a sentence and is skipped."""
    flat = " ".join(text.split())
    flat = re.sub(r"^(?:(?:\d+[.)]|[-*+]|#+)\s+)+", "", flat)
    m = re.search(r"[.!?](?:\s|$)", flat)
    return flat[: m.end()].strip() if m else flat

def read_tree(tree: Path, rel: str, pattern: str = "*") -> list[Path]:
    """The files of one store path under a materialized tree, sorted; empty when the path is absent."""
    d = Path(tree) / rel
    return sorted(p for p in d.glob(pattern) if p.is_file()) if d.is_dir() else []

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
