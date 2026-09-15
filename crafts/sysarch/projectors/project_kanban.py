#!/usr/bin/env python3
"""kanban-board projector (crafts/sysarch/rules/projection.md; d-work #186). Kernel: Python 3.12+, stdlib only.
Projects the d-work store onto one column per ledger state (`dyadlib.STATES`, in the order the
board reads left to right: open, planned, blocked, backlog, done), one card per row (id, title,
refs, disposition count). It holds no row parser of its own — `dyadlib.read_rows` is the source
(Rule-17 property 1: never hand-drawn). A row with `state: blocked` draws its `refs` on the card,
since Rule-3's convention already puts the blocking id there. The `done` column is collapsed
behind a native `<details>` by default: sorted, deterministic (no timestamps), self-contained
(inline CSS, no script, no external reference). Output: one HTML file, written to
<instance>/projections/kanban.html.
  project_kanban.py            write the projection and print column counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_kanban.py: Python 3.12+ required")
import html
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib

COLUMNS = ("open", "planned", "blocked", "backlog", "done")   # dyadlib.STATES, board order
INVARIANTS = [("columns-are-states", lambda: set(COLUMNS) == dyadlib.STATES and len(COLUMNS) == len(dyadlib.STATES))]   # crafts/syseng/rules/invariants.md

def collect(root: Path, pkg: Path = dyadlib.PKG) -> dict[str, list[dyadlib.Row]]:
    """Every row, grouped by state and sorted by id within the group. A state `dyadlib.read_rows`
    returns that is not in COLUMNS (should never happen; STATES and COLUMNS are the same set,
    enforced by INVARIANTS) is dropped rather than raising — a corrupt row file is a fence
    problem (Rule-16), not this projector's to diagnose."""
    out: dict[str, list[dyadlib.Row]] = {c: [] for c in COLUMNS}
    for r in dyadlib.read_rows(root):
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

_LABEL = {"open": "Open", "planned": "Planned", "blocked": "Blocked", "backlog": "Backlog", "done": "Done"}

def _card(r: dyadlib.Row) -> str:
    title = _esc(r.title)
    cut = _esc(_cut(r.title))
    refs_html = (f'<div class="refs">refs: {_esc(r.refs)}</div>' if r.refs.strip() else "")
    n = _disposed_count(r.disposed)
    badge = f'<span class="badge" title="{n} disposition{"s" if n != 1 else ""} recorded">{n}</span>' if n else ""
    blocked_cls = " blocked" if r.state == "blocked" else ""
    return (f'<div class="card{blocked_cls}" id="d-{r.id}">'
            f'<div class="card-head"><span class="id">#{r.id}</span>{badge}</div>'
            f'<div class="title" title="{title}">{cut}</div>{refs_html}</div>')

def render(groups: dict[str, list[dyadlib.Row]]) -> str:
    total = sum(len(v) for v in groups.values())
    cols = []
    for c in COLUMNS:
        rows = groups[c]
        cards = "\n".join(_card(r) for r in rows)
        body = f'<div class="cards">{cards}</div>' if cards else '<div class="empty">none</div>'
        if c == "done" and rows:
            col = (f'<section class="col col-{c}"><h2>{_LABEL[c]} <span class="count">{len(rows)}</span></h2>'
                   f'<details><summary>show {len(rows)} done row{"s" if len(rows) != 1 else ""}</summary>{body}</details></section>')
        else:
            col = f'<section class="col col-{c}"><h2>{_LABEL[c]} <span class="count">{len(rows)}</span></h2>{body}</section>'
        cols.append(col)
    board = "\n".join(cols)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>d-work kanban</title>
<style>
:root {{ --bg:#f6f5f2; --card:#ffffff; --ink:#1f2320; --muted:#6b7269; --line:#dcd8cf; --accent:#5b7c6a;
  --open:#5b7c6a; --planned:#7a8b5e; --blocked:#b0523f; --backlog:#8b8577; --done:#9aa39b; }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#1b1d1a; --card:#242722; --ink:#e8e6df; --muted:#9aa198; --line:#3a3d37; }}
}}
:root[data-theme="dark"] {{ --bg:#1b1d1a; --card:#242722; --ink:#e8e6df; --muted:#9aa198; --line:#3a3d37; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--ink); font:14px/1.4 -apple-system,"Segoe UI",Roboto,sans-serif;
  margin:0; padding:20px 16px; }}
h1 {{ font-size:18px; margin:0 0 4px; }}
.sub {{ color:var(--muted); margin:0 0 18px; font-size:12px; }}
.board {{ display:grid; grid-template-columns:repeat(5,minmax(200px,1fr)); gap:12px; align-items:start; }}
@media (max-width:900px) {{ .board {{ grid-template-columns:1fr; }} }}
.col {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:10px; min-width:0; }}
.col h2 {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; margin:0 0 8px;
  display:flex; justify-content:space-between; color:var(--muted); }}
.col-open h2 {{ color:var(--open); }} .col-planned h2 {{ color:var(--planned); }}
.col-blocked h2 {{ color:var(--blocked); }} .col-backlog h2 {{ color:var(--backlog); }} .col-done h2 {{ color:var(--done); }}
.count {{ font-variant-numeric:tabular-nums; }}
.cards {{ display:flex; flex-direction:column; gap:8px; }}
.card {{ background:var(--bg); border:1px solid var(--line); border-left:3px solid var(--accent);
  border-radius:6px; padding:7px 9px; }}
.col-open .card {{ border-left-color:var(--open); }} .col-planned .card {{ border-left-color:var(--planned); }}
.col-blocked .card, .card.blocked {{ border-left-color:var(--blocked); }}
.col-backlog .card {{ border-left-color:var(--backlog); }} .col-done .card {{ border-left-color:var(--done); }}
.card-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; }}
.id {{ font-weight:600; font-variant-numeric:tabular-nums; }}
.badge {{ background:var(--line); color:var(--muted); border-radius:10px; padding:0 6px; font-size:11px; }}
.title {{ overflow-wrap:break-word; }}
.refs {{ color:var(--muted); font-size:11px; margin-top:4px; overflow-wrap:break-word; }}
.empty {{ color:var(--muted); font-size:12px; font-style:italic; }}
details summary {{ cursor:pointer; color:var(--muted); font-size:12px; margin-bottom:6px; }}
</style></head><body>
<h1>d-work kanban</h1>
<p class="sub">{total} rows, generated from the row store — Rule-17 (never hand-edited; re-run to refresh)</p>
<div class="board">
{board}
</div>
</body></html>
"""

def main() -> int:
    root = dyadlib.repo_root()
    out = dyadlib.instance(root) / "projections" / "kanban.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    groups = collect(root, dyadlib.PKG)
    text = render(groups)
    out.write_text(text)
    counts = " ".join(f"{c}={len(groups[c])}" for c in COLUMNS)
    print(f"ok   [project] kanban: {counts} -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
