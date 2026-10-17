"""ledgerd: the HTML navigator (plan #336 revision 8, built per revision 9: Jinja2 fragments swapped by
htmx, every view a Python route). The JIRA issue-navigator pattern, named so the mapping can be checked:
a sidebar of the schema's views and the Operator's saved views; a basic mode whose filter bar is derived
from the default view's columns (a multi-select for a column with at most MAX_DISTINCT distinct values none
longer than MAX_VALUE, a "contains" box otherwise, and a free-text search over every column) composed into SQL the page shows
read-only; an advanced mode where the SQL itself is typed; results as a table with header sort, a column
chooser, `n of m` and the pin in the footer, Markdown and CSV export; a detail panel for one record
(every table the schema's DETAIL names, keyed by the clicked value); save-as for custom views; and a
shareable URL (`/?view=<name>` or `/?sql=<encoded>`, pushed by the server's `HX-Push-Url` header). Same
origin only: every `src`, `href`, `hx-get`, `hx-post` and `action` is a path on this server, the one
script the vendored `static/htmx.min.js` (0BSD). Every query runs under the core's two fences; the one
write surface, saved views, stores a validated read-only SQL text as UI state. Form bodies are parsed
with `urllib.parse` (no form-parsing dependency). Nothing here knows what a d-work is.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("ui.py: Python 3.12+ required")
import urllib.parse
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib
from ledgerd import core, schema as schema_mod
from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = COMPONENT / "templates"
STATIC_DIR = COMPONENT / "static"
HTMX = "htmx.min.js"
MAX_DISTINCT = 12                                   # a column with at most this many distinct values gets a multi-select
MAX_VALUE = 60                                      # ... when every value is at most this long; a column of titles gets a contains box
PAGE = "navigator.html"
FRAGMENTS = {"results": "results.html", "detail": "detail.html", "sidebar": "sidebar.html"}
ROUTES = ("/", "/ui/results", "/ui/filter", "/ui/detail", "/ui/export", "/ui/sidebar", "/ui/views", "/static/" + HTMX)
EXPORTS = {"md": ("text/markdown; charset=utf-8", "md"), "csv": ("text/csv; charset=utf-8", "csv")}
DIRECTIONS = ("asc", "desc")

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("routes-are-same-origin-paths", lambda: all(r.startswith("/") and not r.startswith("//") for r in ROUTES)),
    ("fragments-are-templates", lambda: all(v.endswith(".html") for v in FRAGMENTS.values()) and PAGE.endswith(".html")),
    ("max-distinct-positive", lambda: MAX_DISTINCT > 0 and MAX_VALUE > 0),
    ("exports-are-md-and-csv", lambda: set(EXPORTS) == {"md", "csv"}),
    ("directions-are-asc-desc", lambda: DIRECTIONS == ("asc", "desc")),
]
TREE_INVARIANTS: list[dyadlib.Invariant] = [
    ("templates-exist", lambda: all((TEMPLATES_DIR / t).is_file() for t in list(FRAGMENTS.values()) + [PAGE, "base.html"])),
    ("htmx-is-vendored", lambda: (STATIC_DIR / HTMX).is_file()),
]

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)

def qi(name: str) -> str:
    """A quoted identifier."""
    return '"' + str(name).replace('"', '""') + '"'

def ql(value) -> str:
    """A quoted string literal."""
    return "'" + str(value).replace("'", "''") + "'"

def view_columns(service, view: str) -> list[str]:
    return service.query(f"SELECT * FROM {qi(view)} LIMIT 0")[0]

def filter_spec(service, view: str) -> list[dict]:
    """The basic-mode bar, derived from the view's columns: `select` with its values when distinct values are
    few, else `text` (contains)."""
    spec = []
    for col in view_columns(service, view):
        _, rows = service.query(f"SELECT DISTINCT {qi(col)} FROM {qi(view)} ORDER BY 1 LIMIT {MAX_DISTINCT + 1}")
        values = ["" if r[0] is None else str(r[0]) for r in rows]
        short = len(values) <= MAX_DISTINCT and all(len(v) <= MAX_VALUE for v in values)
        spec.append({"name": col, "kind": "select", "values": values} if short else {"name": col, "kind": "text"})
    return spec

def compose(view: str, columns: list[str], selected: dict[str, list[str]], contains: dict[str, str], q: str) -> str:
    """Basic mode -> SQL, shown read-only so the Operator sees what the bar asks."""
    where = []
    for col in columns:
        vals = [v for v in selected.get(col, []) if v != ""]
        if vals:
            where.append(f"{qi(col)} IN ({', '.join(ql(v) for v in vals)})")
        s = contains.get(col, "").strip()
        if s:
            where.append(f"CAST({qi(col)} AS TEXT) LIKE {ql('%' + s + '%')}")
    if q.strip():
        where.append("(" + " OR ".join(f"CAST({qi(c)} AS TEXT) LIKE {ql('%' + q.strip() + '%')}" for c in columns) + ")")
    return f"SELECT * FROM {qi(view)}" + (" WHERE " + " AND ".join(where) if where else "")

def wrap(sql: str, cols: list[str], sort: str, direction: str) -> str:
    """The results query: the statement (fenced) as a subquery with the chosen columns and sort."""
    base = core.read_statement(sql)
    select = ", ".join(qi(c) for c in cols) if cols else "*"
    out = f"SELECT {select} FROM ({base})"
    if sort:
        out += f" ORDER BY {qi(sort)} {'DESC' if direction == 'desc' else 'ASC'}"
    return out

def run(service, sql: str, cols: list[str], sort: str, direction: str) -> dict:
    """{columns, all_columns, rows, total, error, sql}: the result or the refusal, never an exception."""
    out = {"columns": [], "all_columns": [], "rows": [], "total": 0, "error": "", "sql": sql, "sort": sort, "dir": direction, "cols": cols}
    try:
        out["all_columns"] = service.query(wrap(sql, [], "", ""))[0]
        out["columns"], out["rows"] = service.query(wrap(sql, cols, sort, direction))
        out["total"] = len(out["rows"])
    except core.QueryError as e:
        out["error"] = str(e)
    return out

def _multi(params) -> tuple[dict[str, list[str]], dict[str, str], str]:
    selected, contains, q = {}, {}, ""
    for k, v in params.multi_items():
        if k.startswith("f_"):
            selected.setdefault(k[2:], []).append(v)
        elif k.startswith("c_"):
            contains[k[2:]] = v
        elif k == "q":
            q = v
    return selected, contains, q

def _cols(params) -> list[str]:
    return [c for c in params.getlist("cols") if c]

def _direction(params) -> str:
    d = params.get("dir", "asc")
    return d if d in DIRECTIONS else "asc"

def state_url(sql: str, view: str, cols: list[str], sort: str, direction: str) -> str:
    """The shareable URL that reproduces the page."""
    q = [("view", view)] if view else [("sql", sql)]
    q += [("cols", c) for c in cols]
    if sort:
        q += [("sort", sort), ("dir", direction)]
    return "/?" + urllib.parse.urlencode(q)

def context(service, request: Request) -> dict:
    """What every page and fragment can see."""
    return {"schema_name": service.schema.NAME, "views": list(service.schema.VIEWS), "rendered": list(service.schema.RENDERED),
            "saved": core.saved_views(service.state), "default_view": schema_mod.default_view(service.schema),
            "detail_keys": sorted(set(schema_mod.detail_of(service.schema).values())), "pin": service.pin_label(), "health": service.health()}

def results_response(service, request: Request, sql: str, view: str, cols: list[str], sort: str, direction: str, shown_sql: str | None = None) -> HTMLResponse:
    ctx = {**context(service, request), **run(service, sql, cols, sort, direction), "view": view, "shown_sql": shown_sql,
           "state_url": state_url(sql, view, cols, sort, direction)}
    html = _env.get_template(FRAGMENTS["results"]).render(ctx)
    return HTMLResponse(html, headers={"HX-Push-Url": ctx["state_url"]})

def mount(app, service) -> None:
    """Join the navigator's routes to the app (core.create_app calls this)."""

    @app.get("/", response_class=HTMLResponse)
    def page(request: Request):
        p = request.query_params
        view, sql = p.get("view", ""), p.get("sql", "")
        if not view and not sql:
            view = schema_mod.default_view(service.schema) or ""
        if view and view not in service.schema.VIEWS:
            saved = core.read_view(service.state, view)
            if saved:
                sql, view = saved.get("sql", ""), ""
            else:
                view = schema_mod.default_view(service.schema) or ""
        if view:
            sql = f"SELECT * FROM {qi(view)}"
        cols, sort, direction = _cols(p), p.get("sort", ""), _direction(p)
        ctx = {**context(service, request), **run(service, sql, cols, sort, direction), "view": view,
               "filter_view": view if view in service.schema.VIEWS else (schema_mod.default_view(service.schema) or ""),
               "state_url": state_url(sql, view, cols, sort, direction)}
        ctx["filters"] = filter_spec(service, ctx["filter_view"]) if ctx["filter_view"] else []
        ctx["shown_sql"] = sql
        return HTMLResponse(_env.get_template(PAGE).render(ctx))

    @app.get("/ui/results", response_class=HTMLResponse)
    def results(request: Request):
        p = request.query_params
        return results_response(service, request, p.get("sql", ""), p.get("view", ""), _cols(p), p.get("sort", ""), _direction(p), shown_sql=p.get("sql", ""))

    @app.get("/ui/filter", response_class=HTMLResponse)
    def filtered(request: Request):
        p = request.query_params
        view = p.get("view", "") or schema_mod.default_view(service.schema) or ""
        if view not in service.schema.VIEWS:
            return HTMLResponse("<p class=\"error\">no such view</p>", status_code=404)
        selected, contains, q = _multi(p)
        sql = compose(view, view_columns(service, view), selected, contains, q)
        return results_response(service, request, sql, "", _cols(p), p.get("sort", ""), _direction(p), shown_sql=sql)

    @app.get("/ui/detail", response_class=HTMLResponse)
    def detail(request: Request):
        value = request.query_params.get("value", "")
        sections = []
        for table, key in schema_mod.detail_of(service.schema).items():
            try:
                cols, rows = service.query(f"SELECT * FROM {qi(table)} WHERE CAST({qi(key)} AS TEXT) = ?", (value,))
            except core.QueryError as e:
                cols, rows = ["error"], [[str(e)]]
            sections.append({"table": table, "key": key, "columns": cols, "rows": rows})
        return HTMLResponse(_env.get_template(FRAGMENTS["detail"]).render({**context(service, request), "value": value, "sections": sections}))

    @app.get("/ui/export")
    def export(request: Request):
        p = request.query_params
        fmt = p.get("format", "md")
        if fmt not in EXPORTS:
            return Response("format is md or csv", status_code=400)
        r = run(service, p.get("sql", ""), _cols(p), p.get("sort", ""), _direction(p))
        if r["error"]:
            return Response(r["error"], status_code=400)
        body = core.render_md(r["columns"], r["rows"]) if fmt == "md" else core.render_csv(r["columns"], r["rows"])
        media, ext = EXPORTS[fmt]
        return Response(body, media_type=media, headers={"Content-Disposition": f"attachment; filename=\"{service.schema.NAME}.{ext}\""})

    @app.get("/ui/sidebar", response_class=HTMLResponse)
    def sidebar(request: Request):
        return HTMLResponse(_env.get_template(FRAGMENTS["sidebar"]).render({**context(service, request), "message": ""}))

    @app.post("/ui/views", response_class=HTMLResponse)
    async def save(request: Request):
        form = urllib.parse.parse_qs((await request.body()).decode(), keep_blank_values=True)
        one = lambda k: (form.get(k) or [""])[0]
        try:
            core.save_view(service.state, service.db, service.schema, one("name").strip(), one("sql"), " ".join(form.get("cols", [])), one("sort"))
            message = f"saved view {one('name').strip()}"
        except core.QueryError as e:
            message = f"not saved: {e}"
        return HTMLResponse(_env.get_template(FRAGMENTS["sidebar"]).render({**context(service, request), "message": message}))

    @app.post("/ui/views/{name}/delete", response_class=HTMLResponse)
    def delete(name: str, request: Request):
        message = f"deleted {name}" if core.delete_view(service.state, name) else f"no saved view {name}"
        return HTMLResponse(_env.get_template(FRAGMENTS["sidebar"]).render({**context(service, request), "message": message}))

    @app.get("/static/" + HTMX)
    def htmx():
        return FileResponse(STATIC_DIR / HTMX, media_type="text/javascript")

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
