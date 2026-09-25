#!/usr/bin/env python3
"""Events projector (crafts/sysarch/rules/projection.md; the sysadmin craft's surface, its data Rule-19's). Kernel: Python 3.12+, stdlib only.
Projects every run-book event (`<runbooks>/events/<instance>.jsonl`; the core runner's
`runbook.all_events` and `runbook.EVENT_FIELDS`, which the sysadmin craft's events guard re-exports; #155) onto one table per instance: ts, role, name, class, exit, postcondition,
duration, with the output tail expandable per row; badges for exit (0 / non-zero), postcondition
(ok, already, n/a, failed), role and class; one inline filter over every cell; a count line per
instance and per command. The convenient review of run-book events an audit of a process playbook
needs (plan #150, property 7). Output: one self-contained HTML file (inline CSS and JS, no external
reference), deterministic (events sorted by instance, ts, id; no timestamps of its own), written to
<instance>/projections/events.html. An empty or absent store renders a valid page saying so.
  project_events.py         write the projection and print event/instance counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_events.py: Python 3.12+ required")
import collections, html
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib
import runbook                                              # the core runner: read_events, all_events, EVENT_FIELDS, events_dir, runbooks_rel
runbooks = runbook                                           # the store's path (runbooks_rel); kept as a name for the tests

COLUMNS = ("ts", "role", "name", "class", "exit", "postcondition", "duration_ms")   # the table, in order; each is an EVENT_FIELDS name
INVARIANTS = [("columns-are-event-fields", lambda: set(COLUMNS) <= set(runbook.EVENT_FIELDS) and len(set(COLUMNS)) == len(COLUMNS))]   # crafts/syseng/rules/invariants.md

def collect(root: Path) -> dict[str, list[dict]]:
    """{instance: events sorted by (ts, id)}; every event carries every EVENT_FIELDS key ("" when absent)."""
    out = {}
    for inst, evs in sorted(runbook.all_events(root).items()):
        rows = [{k: e.get(k, "") for k in runbook.EVENT_FIELDS} for e in evs]
        out[inst] = sorted(rows, key=lambda e: (str(e["ts"]), str(e["id"])))
    return out

def _esc(s) -> str:
    """Escaped, and any `http(s)://` defanged with a zero-width space (`cmd`/`output_tail`/`scope`
    are free text from a real command line and can legitimately contain one, e.g. `curl … http://
    git.lan:3000/…` — the page must stay self-contained with no external reference, so the literal
    substring never survives into the output even inside inert `<pre>`/`<code>` text)."""
    return html.escape(str(s), quote=True).replace("http://", "http\u200b://").replace("https://", "https\u200b://")

def _badge(kind: str, value) -> str:
    v = str(value)
    if kind == "exit":
        cls = "ok" if v == "0" else "bad"
    elif kind == "postcondition":
        cls = {"ok": "ok", "already": "ok", "n/a": "na", "failed": "bad"}.get(v, "na")
    else:
        cls = f"{kind}-{v}"
    return f'<span class="badge {kind} {cls}">{_esc(v)}</span>'

def render(store: dict[str, list[dict]], events_rel: str) -> str:
    n = sum(len(v) for v in store.values())
    parts = [HEAD, "<h1>Run-book events (Rule-19 property 7, sysarch projection.md)</h1>",
             f"<p>{n} event{'s' if n != 1 else ''} in {len(store)} instance{'s' if len(store) != 1 else ''}, read from <code>{_esc(events_rel)}/&lt;instance&gt;.jsonl</code> "
             "(append-only; one JSON object per execution of a run-book command by either party). "
             "Type a word to filter rows; click a row's <code>tail</code> to see the last lines of its output.</p>",
             '<p><input id="q" type="search" placeholder="filter… (name, role, class, exit, postcondition, id)" aria-label="filter rows"></p>',
             '<ul id="legend"><li><span class="badge exit ok">0</span> exit 0</li><li><span class="badge exit bad">1</span> non-zero exit</li>'
             '<li><span class="badge postcondition ok">ok</span> / <span class="badge postcondition ok">already</span> postcondition held</li>'
             '<li><span class="badge postcondition bad">failed</span> postcondition failed after the command</li><li><span class="badge postcondition na">n/a</span> none declared</li>'
             '<li><span class="badge role role-operator">operator</span> / <span class="badge role role-agent">agent</span> who ran it</li>'
             '<li><span class="badge class class-read-only">read-only</span> <span class="badge class class-reversible">reversible</span> <span class="badge class class-destructive">destructive</span> Rule-8 class</li></ul>']
    if not store:
        parts.append('<p class="empty" id="empty">No events recorded yet: nothing has been run through <code>package.py runbook run</code>.</p>')
    for inst, evs in store.items():
        by_name = collections.Counter(str(e["name"]) for e in evs)
        fails = sum(1 for e in evs if str(e["exit"]) != "0" or e["postcondition"] == "failed")
        counts = ", ".join(f"<code>{_esc(k)}</code> ×{v}" for k, v in sorted(by_name.items()))
        rows = []
        for e in evs:
            cells = "".join(
                f"<td>{_badge(c, e[c])}</td>" if c in ("exit", "postcondition", "role", "class") else f"<td class=\"{c}\">{_esc(e[c])}</td>"
                for c in COLUMNS)
            tail = _esc(e["output_tail"]) if e["output_tail"] else '<span class="none">(no output)</span>'
            rows.append(f'<tr class="ev" id="ev-{_esc(e["id"])}" data-id="{_esc(e["id"])}" title="{_esc(e["id"])}">{cells}'
                        f'<td><details><summary>tail</summary><pre>{tail}</pre>'
                        f'<p class="meta">id <code>{_esc(e["id"])}</code> · cmd <code>{_esc(e["cmd"])}</code> · scope {_esc(e["scope"])} · '
                        f'commit {_esc(e["commit"])} · run-book sha256 {_esc(str(e["runbook_sha256"])[:12])}… · output sha256 {_esc(str(e["output_sha256"])[:12])}…</p></details></td></tr>')
        parts.append(f'<section class="inst" id="i-{_esc(inst)}"><h2>{_esc(inst)}</h2>'
                     f'<p class="meta">{len(evs)} event{"s" if len(evs) != 1 else ""}, {fails} with a non-zero exit or a failed postcondition; per command: {counts or "none"}</p>'
                     f'<div class="tw"><table><thead><tr>{"".join(f"<th>{_esc(c)}</th>" for c in COLUMNS)}<th>output</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>')
    parts.append(TAIL)
    return "".join(parts)

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>dyad run-book events</title>
<style>
:root{--bg:#fafafa;--fg:#1a1a1a;--card:#fff;--line:#c9c9c9;--muted:#5b5b5b;--zebra:#f4f4f4;--ok:#dcfce7;--ok-fg:#14532d;--bad:#fee2e2;--bad-fg:#7f1d1d;
--na:#e5e7eb;--na-fg:#374151;--op:#dbeafe;--op-fg:#1e3a8a;--ag:#f3e8ff;--ag-fg:#581c87;--ro:#ecfccb;--ro-fg:#365314;--rv:#fef3c7;--rv-fg:#92400e;--de:#fee2e2;--de-fg:#7f1d1d}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#e6e6e6;--card:#1f1f1f;--line:#444;--muted:#a3a3a3;--zebra:#242424;--ok:#14532d;--ok-fg:#dcfce7;--bad:#7f1d1d;--bad-fg:#fee2e2;
--na:#374151;--na-fg:#e5e7eb;--op:#1e3a8a;--op-fg:#dbeafe;--ag:#581c87;--ag-fg:#f3e8ff;--ro:#365314;--ro-fg:#ecfccb;--rv:#92400e;--rv-fg:#fef3c7;--de:#7f1d1d;--de-fg:#fee2e2}}
body{margin:0;padding:16px;font:14px system-ui,sans-serif;background:var(--bg);color:var(--fg)}
h1{font-size:18px;margin:0 0 4px}h2{font-size:15px;margin:0 0 6px}p{margin:0 0 8px}
#q{font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:4px;background:var(--card);color:var(--fg);width:min(100%,420px)}
#legend{display:flex;flex-wrap:wrap;gap:8px 18px;list-style:none;margin:0 0 12px;padding:0;color:var(--muted)}
.inst{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin-bottom:14px;min-width:0}
.badge{display:inline-block;padding:1px 7px;border-radius:10px;font-size:12px;font-family:ui-monospace,monospace}
.ok{background:var(--ok);color:var(--ok-fg)}.bad{background:var(--bad);color:var(--bad-fg)}.na{background:var(--na);color:var(--na-fg)}
.role-operator{background:var(--op);color:var(--op-fg)}.role-agent{background:var(--ag);color:var(--ag-fg)}
.class-read-only{background:var(--ro);color:var(--ro-fg)}.class-reversible{background:var(--rv);color:var(--rv-fg)}.class-destructive{background:var(--de);color:var(--de-fg)}
.meta,.empty{color:var(--muted);font-size:12px}.empty{font-size:14px;font-style:italic}.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:4px 0 8px}th,td{text-align:left;vertical-align:top;padding:3px 6px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600}tbody tr:nth-child(even){background:var(--zebra)}td.ts,td.name,td.duration_ms{font-family:ui-monospace,monospace;white-space:nowrap}
tr.off{display:none}tr:target{outline:2px solid var(--rv-fg)}details summary{cursor:pointer;color:var(--muted)}pre{margin:4px 0;white-space:pre-wrap;word-break:break-word;font-size:12px}
.none{color:var(--muted);font-style:italic}
</style></head><body>
"""
TAIL = """<script>
(function(){
  var q=document.getElementById('q'),rows=document.querySelectorAll('tr.ev');
  q.addEventListener('input',function(){var s=q.value.trim().toLowerCase();
    rows.forEach(function(r){r.classList.toggle('off',!!s&&(r.textContent+' '+r.dataset.id).toLowerCase().indexOf(s)<0);});});
})();
</script></body></html>
"""

def main() -> int:
    root = dyadlib.repo_root()
    out = dyadlib.instance(root) / "projections" / "events.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    store = collect(root)
    text = render(store, runbooks.runbooks_rel(root) + "/events")
    out.write_text(text)
    n = sum(len(v) for v in store.values())
    print(f"ok   [project] events: {n} events, {len(store)} instances -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
