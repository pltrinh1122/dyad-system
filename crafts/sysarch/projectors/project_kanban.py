#!/usr/bin/env python3
"""kanban-board projector (crafts/sysarch/rules/projection.md; d-work #186). Kernel: Python 3.12+, stdlib only.
Projects the d-work store onto one column per ledger state (`dyadlib.STATES`, in the order the
board reads left to right: open, planned, blocked, backlog, done, archived), one card per row (id,
title, refs, disposition count) with a **phase strip** — the row's whole life-cycle, every phase
read from the store and nothing else (no clock; determinism.md): opened (the row) · plan (the plan
file exists, Rule-15) · plan-Y · PRs (`merges PR #n` in `disposed`) · Done-Y · provenance (prompt /
disposition counts of the record, Rule-7) · archived. A phase present out of order — a Done-Y with
no plan-Y, a plan file for a backlog row, a state the dispositions do not support — is drawn
flagged (`ph warn`), which is what a board is for (d-work #37). It holds no row parser of its own —
`dyadlib.read_rows` is the source (Rule-17 property 1: never hand-drawn). A row with
`state: blocked` draws its `refs` on the card, since Rule-3's convention already puts the blocking
id there. The `archived` column is collapsed behind a native `<details>` by default (the retired set
is what to hide; done stays open): sorted, deterministic (no timestamps), self-contained (inline
CSS, no script, no external reference). Output: one HTML file, written to
<instance>/projections/kanban.html.
  project_kanban.py            write the projection and print column counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_kanban.py: Python 3.12+ required")
import html, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib

COLUMNS = ("open", "planned", "blocked", "backlog", "done", "archived")   # dyadlib.STATES, board order
PHASES = ("opened", "plan", "plan-Y", "PRs", "Done-Y", "provenance", "archived")   # the strip, left to right (#37)
COLLAPSED = "archived"                                                              # the one column behind <details>
INVARIANTS = [("columns-are-states", lambda: set(COLUMNS) == dyadlib.STATES and len(COLUMNS) == len(dyadlib.STATES)),   # crafts/syseng/rules/invariants.md
              ("collapsed-is-a-column", lambda: COLLAPSED in COLUMNS),
              ("phases-distinct", lambda: len(set(PHASES)) == len(PHASES) and PHASES[0] == "opened" and PHASES[-1] == "archived")]

def collect(root: Path, pkg: Path = dyadlib.PKG, craft: str | None = None) -> dict[str, list[dyadlib.Row]]:
    """Every row, grouped by state and sorted by id within the group. A state `dyadlib.read_rows`
    returns that is not in COLUMNS (should never happen; STATES and COLUMNS are the same set,
    enforced by INVARIANTS) is dropped rather than raising — a corrupt row file is a fence
    problem (Rule-16), not this projector's to diagnose. `craft`: keep only rows whose `refs`
    carries this bare token (row.refs->craft, Rule-20; d-work #22) — the same routing tag
    `dyad dwork list --craft` reads, so the text and board surfaces agree on one row's set."""
    out: dict[str, list[dyadlib.Row]] = {c: [] for c in COLUMNS}
    for r in dyadlib.read_rows(root):
        if craft is not None and craft not in r.refs.split():
            continue
        if r.state in out:
            out[r.state].append(r)
    for c in out:
        out[c].sort(key=lambda r: r.id)
    return out

def _esc(s: str) -> str:
    return html.escape(s, quote=True)

def _cut(s: str, n: int = 88) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"

def _disposed_count(disposed: str) -> int:
    return len([d for d in disposed.split(";") if d.strip()]) if disposed else 0

_LABEL = {"open": "Open", "planned": "Planned", "blocked": "Blocked", "backlog": "Backlog", "done": "Done", "archived": "Archived"}
_PR = re.compile(r"#(\d+)")
_ENTRY = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(Y|N)\s+(.*)$")
_PROV_HEAD = re.compile(r"^## \d+ (prompt|disposition)\b", re.M)

def _entries(disposed: str) -> list[tuple[str, str, str]]:
    """(date, Y|N, text) per `;`-separated entry of a row's `disposed` column (Rule-3 Ledger)."""
    out = []
    for e in (disposed or "").split(";"):
        m = _ENTRY.match(e.strip())
        if m:
            out.append((m.group(1), m.group(2), m.group(3)))
    return out

def lifecycle(r: dyadlib.Row, root: Path | None = None) -> dict:
    """The phases of one row from the store alone: which are lit, with what detail, and which are out
    of order (`warn`). `root` None (a render without an instance): plan and provenance read as unknown."""
    es = _entries(r.disposed)
    plan_y = next((d for d, y, t in es if y == "Y" and t.startswith("plan")), None)
    done_y = next((d for d, y, t in es if y == "Y" and t.startswith("done")), None)
    prs = sorted({int(n) for d, y, t in es if "PR" in t for n in _PR.findall(t.split("PR", 1)[1])})
    plan_file = prov = None
    if root is not None:
        inst = dyadlib.instance(root) / "d-work"
        plan_file = (inst / "plans" / f"{r.id}.md").exists()
        pf = inst / "provenance" / f"{r.id}.md"
        if pf.exists():
            kinds = _PROV_HEAD.findall(pf.read_text(errors="ignore"))
            prov = (kinds.count("prompt"), kinds.count("disposition"))
        else:
            prov = (0, 0)
    ph = {"opened": (True, r.opened), "plan": (plan_file, "plan file" if plan_file else ("no plan file" if plan_file is False else "unknown")),
          "plan-Y": (plan_y is not None, plan_y or ""), "PRs": (bool(prs), ", ".join(f"#{n}" for n in prs)),
          "Done-Y": (done_y is not None, done_y or ""), "provenance": (bool(prov and (prov[0] or prov[1])), f"{prov[0]} prompt, {prov[1]} disposition" if prov else "unknown"),
          "archived": (r.state == "archived", "archived" if r.state == "archived" else "")}
    warn = set()
    if done_y and not plan_y: warn.add("Done-Y")
    if r.state == "backlog" and plan_file: warn.add("plan")
    if r.state == "planned" and not plan_y: warn.add("plan-Y")
    if r.state in ("done", "archived") and not done_y: warn.add("Done-Y")
    if prov and len(es) != prov[1] and root is not None: warn.add("provenance")   # Rule-7 property 5, drawn not enforced
    return {"phases": ph, "warn": warn}

def _strip(life: dict) -> str:
    pips = []
    for name in PHASES:
        on, detail = life["phases"][name]
        cls = "ph warn" if name in life["warn"] else ("ph on" if on else ("ph unknown" if on is None else "ph"))
        tip = _esc(f"{name}: {detail}" if detail else name)
        pips.append(f'<span class="{cls}" title="{tip}">{_esc(name)}</span>')
    return '<div class="phases">' + "".join(pips) + "</div>"

def _card(r: dyadlib.Row, root: Path | None = None) -> str:
    title = _esc(r.title)
    cut = _esc(_cut(r.title))
    refs_html = (f'<div class="refs">refs: {_esc(r.refs)}</div>' if r.refs.strip() else "")
    n = _disposed_count(r.disposed)
    badge = f'<span class="badge" title="{n} disposition{"s" if n != 1 else ""} recorded">{n}</span>' if n else ""
    blocked_cls = " blocked" if r.state == "blocked" else ""
    return (f'<div class="card{blocked_cls}" id="d-{r.id}">'
            f'<div class="card-head"><span class="id">#{r.id}</span>{badge}</div>'
            f'<div class="title" title="{title}">{cut}</div>{refs_html}{_strip(lifecycle(r, root))}</div>')

def render(groups: dict[str, list[dyadlib.Row]], craft: str | None = None, root: Path | None = None) -> str:
    total = sum(len(v) for v in groups.values())
    heading = f"d-work kanban — {html.escape(craft)}" if craft else "d-work kanban"
    sub = (f"{total} row{'s' if total != 1 else ''} tagged `{html.escape(craft)}`, generated from the row store"
           if craft else f"{total} rows, generated from the row store") + " — Rule-17 (never hand-edited; re-run to refresh)"
    cols = []
    for c in COLUMNS:
        rows = groups[c]
        cards = "\n".join(_card(r, root) for r in rows)
        body = f'<div class="cards">{cards}</div>' if cards else '<div class="empty">none</div>'
        if c == COLLAPSED and rows:
            col = (f'<section class="col col-{c}"><h2>{_LABEL[c]} <span class="count">{len(rows)}</span></h2>'
                   f'<details><summary>show {len(rows)} {c} row{"s" if len(rows) != 1 else ""}</summary>{body}</details></section>')
        else:
            col = f'<section class="col col-{c}"><h2>{_LABEL[c]} <span class="count">{len(rows)}</span></h2>{body}</section>'
        cols.append(col)
    board = "\n".join(cols)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{heading}</title>
<style>
:root {{ --bg:#f6f5f2; --card:#ffffff; --ink:#1f2320; --muted:#6b7269; --line:#dcd8cf; --accent:#5b7c6a;
  --open:#5b7c6a; --planned:#7a8b5e; --blocked:#b0523f; --backlog:#8b8577; --done:#9aa39b; --archived:#b9b3a6; --warn:#b0523f; }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#1b1d1a; --card:#242722; --ink:#e8e6df; --muted:#9aa198; --line:#3a3d37; }}
}}
:root[data-theme="dark"] {{ --bg:#1b1d1a; --card:#242722; --ink:#e8e6df; --muted:#9aa198; --line:#3a3d37; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--ink); font:14px/1.4 -apple-system,"Segoe UI",Roboto,sans-serif;
  margin:0; padding:20px 16px; }}
h1 {{ font-size:18px; margin:0 0 4px; }}
.sub {{ color:var(--muted); margin:0 0 18px; font-size:12px; }}
.board {{ display:grid; grid-template-columns:repeat(6,minmax(180px,1fr)); gap:12px; align-items:start; }}
@media (max-width:900px) {{ .board {{ grid-template-columns:1fr; }} }}
.col {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:10px; min-width:0; }}
.col h2 {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; margin:0 0 8px;
  display:flex; justify-content:space-between; color:var(--muted); }}
.col-open h2 {{ color:var(--open); }} .col-planned h2 {{ color:var(--planned); }}
.col-blocked h2 {{ color:var(--blocked); }} .col-backlog h2 {{ color:var(--backlog); }} .col-done h2 {{ color:var(--done); }} .col-archived h2 {{ color:var(--archived); }}
.count {{ font-variant-numeric:tabular-nums; }}
.cards {{ display:flex; flex-direction:column; gap:8px; }}
.card {{ background:var(--bg); border:1px solid var(--line); border-left:3px solid var(--accent);
  border-radius:6px; padding:7px 9px; }}
.col-open .card {{ border-left-color:var(--open); }} .col-planned .card {{ border-left-color:var(--planned); }}
.col-blocked .card, .card.blocked {{ border-left-color:var(--blocked); }}
.col-backlog .card {{ border-left-color:var(--backlog); }} .col-done .card {{ border-left-color:var(--done); }} .col-archived .card {{ border-left-color:var(--archived); }}
.phases {{ display:flex; flex-wrap:wrap; gap:3px; margin-top:6px; }}
.ph {{ font-size:10px; line-height:1; padding:2px 5px; border-radius:8px; border:1px solid var(--line); color:var(--muted); background:transparent; }}
.ph.on {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
.ph.unknown {{ border-style:dashed; }}
.ph.warn {{ background:var(--warn); border-color:var(--warn); color:#fff; }}
.card-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; }}
.id {{ font-weight:600; font-variant-numeric:tabular-nums; }}
.badge {{ background:var(--line); color:var(--muted); border-radius:10px; padding:0 6px; font-size:11px; }}
.title {{ overflow-wrap:break-word; }}
.refs {{ color:var(--muted); font-size:11px; margin-top:4px; overflow-wrap:break-word; }}
.empty {{ color:var(--muted); font-size:12px; font-style:italic; }}
details summary {{ cursor:pointer; color:var(--muted); font-size:12px; margin-bottom:6px; }}
</style></head><body>
<h1>{heading}</h1>
<p class="sub">{sub}</p>
<div class="board">
{board}
</div>
</body></html>
"""

def _flag(name: str, argv: list[str]) -> str | None:
    return argv[argv.index(name) + 1] if name in argv else None

def main() -> int:
    craft = _flag("--craft", sys.argv[1:])          # `dyad project kanban --craft <name>` (d-work #22)
    root = dyadlib.repo_root()
    slug = f"kanban-{craft}.html" if craft else "kanban.html"   # a separate file: the full board stays byte-identical (determinism.md)
    out = dyadlib.instance(root) / "projections" / slug
    out.parent.mkdir(parents=True, exist_ok=True)
    groups = collect(root, dyadlib.PKG, craft)
    text = render(groups, craft, root)
    out.write_text(text)
    counts = " ".join(f"{c}={len(groups[c])}" for c in COLUMNS)
    label = f"kanban --craft {craft}" if craft else "kanban"
    print(f"ok   [project] {label}: {counts} -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
