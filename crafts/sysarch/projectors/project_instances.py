#!/usr/bin/env python3
"""instance-traversal projector (crafts/sysarch/rules/projection.md; d-work #50, an Operator audit
surface). Kernel: Python 3.12+, stdlib only.

Projects entity INSTANCES — one row, one rule, one falsification record, one term — and the edges
between them, for an Operator to walk by clicking, never by reading source. Every edge is a row of
Rule-20's own register (`references.REFERENCES`, read via `dyadlib.load_guard('agent',
'references')`); this projector hand-draws no edge and holds no relation table of its own
(`projection.md` p1). Complements `project_entities.py`, which projects entity *kinds* (schemas);
this projects entity *instances* (data).

The register's own shape bounds what a mechanical reader can do here, stated rather than hidden:
an extractor yields `(where, token)`; `token` is a clean target id, but `where` is a free-text
location whose only structural guarantee is that it *begins with a repo-relative path* (verified:
every `where` on this corpus splits cleanly on the first space). A source instance is therefore
keyed by that leading path. For a one-instance-per-file entity (row, plan, provenance, rule, a
falsification record) this is exact. For a multi-instance-per-file entity (a term in
VOCABULARY.md, an incident row in INCIDENTS.md, a preference, a change-log row) every instance in
that file collapses onto one node, and the remainder of `where` — the field or the quoted instance
name — is shown as the edge's own label, verbatim, never parsed further. This is the file's one
accepted limitation (Rule-9: falsified in the d-work #50 plan, survives, scoped) and the legend
below states it in the Operator's own view, not only in this docstring.

A target token is linked back into a live, expandable node only for the three kinds this module
can place with a Corpus-backed store already parsed by the reference guard — row (a digit token),
rule (a digit token, or a `RULE-<n>-` token from a guard-delegated import), record (a path token
resolved the same way `file_exists` resolves it) — using the SAME data the resolver already holds,
never a second parser. Every other target kind (craft, pr, commit, component, file, event, command,
changelog, ops) renders as a terminal chip: `<kind>: <token>`, not expandable, its resolution status
shown from the SAME resolver Rule-20's guard already owns (never re-verified by a second mechanism).

Traversal: the top level lists entity kinds, then their instances, each a `<details>` element —
closed by default, which is `<details>`'s own default, so "every drawer closed" is structural, not
a script's reset. Opening an instance shows its outgoing edges grouped by reference kind; opening
an edge lazily builds a NESTED `<details>` for its target from the same in-page JSON graph, so
drilling down never duplicates a subtree in the static HTML (this instance's own register produces
1111 edges over ~20 rules alone — a pre-rendered tree would be exponential, not linear). A target
already open on the current path (a cycle: `rule.text->rule` is not acyclic) renders as a marked
chip that jumps to and opens the target's one canonical (top-level) drawer instead of recursing.

Output: one self-contained HTML file (inline CSS and JS, no external reference), deterministic
(sorted iteration, no timestamp), written to <instance>/projections/instances.html.
  project_instances.py        write the projection and print node/edge counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_instances.py: Python 3.12+ required")
import html, json, re
from dataclasses import dataclass, field
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (projection.md p2)
import dyadlib
references = dyadlib.load_guard("agent", "references")

# ---- model -------------------------------------------------------------------------------------

@dataclass
class Edge:
    kind: str            # the reference kind, e.g. "row.refs->row" (references.REFERENCES[i][0])
    label: str           # the source field, plus where's own remainder for a multi-instance file
    status: str          # "ok" | "fail" | "world" | "delegated" | "unresolved" (see `edge_status`)
    target: str = ""     # a node key (expandable) — set iff terminal_text is ""
    terminal_text: str = ""   # "<kind>: <token>" (not expandable) — set iff target is ""

@dataclass
class Node:
    key: str             # stable id: "<kind>:<instance-id-or-path>"
    kind: str             # display kind: row | plan | provenance | rule | record | term | ...
    label: str            # short label shown on the drawer's summary line
    path: str             # the repo-relative path backing this node ("" if none, e.g. a bare craft)
    edges: list[Edge] = field(default_factory=list)

@dataclass
class Model:
    nodes: dict[str, Node] = field(default_factory=dict)
    kind_notes: list[tuple[str, str, int, str]] = field(default_factory=list)   # (kind, src->tgt, n edges, note) — the legend table

EDGE_STATUSES = frozenset({"ok", "fail", "world", "delegated", "unresolved"})   # every value `_edge_status` can return
INVARIANTS = [("status-titles-cover-every-status", lambda: set(_STATUS_TITLE) == EDGE_STATUSES)]   # crafts/syseng/rules/invariants.md

# ---- collect: parse, never hand-draw -------------------------------------------------------------

def _rel(root: Path, p: Path) -> str:
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)

def _seed(m: Model, key: str, kind: str, label: str, path: str) -> Node:
    n = m.nodes.get(key)
    if n is None:
        n = Node(key=key, kind=kind, label=label, path=path)
        m.nodes[key] = n
    return n

def _seed_stores(m: Model, root: Path, c) -> None:
    """Every entity this instance's stores hold, whether or not it happens to carry an edge —
    a row with no `refs`, a Rule nobody imports, is still an instance to browse (#50 intent).
    Keyed by `<kind>:<repo-relative path>` throughout — the SAME key the edge loop below derives
    from `where`'s leading path — so a seeded node and an edge-carrying node are never two
    different objects for the one instance (caught live, #50's own incident: an id-keyed seed and
    a path-keyed edge target silently diverged in the first draft)."""
    for rid, p in sorted(c.row_files.items()):
        rel = _rel(root, p)
        _seed(m, f"row:{rel}", "row", f"#{rid}", rel)
    for p in c.plans:
        rel = _rel(root, p)
        _seed(m, f"plan:{rel}", "plan", f"#{p.stem}", rel)
    for p in c.provenance:
        rel = _rel(root, p)
        _seed(m, f"provenance:{rel}", "provenance", f"#{p.stem}", rel)
    for n, p in sorted(c.rules.items()):
        rel = _rel(root, p)
        _seed(m, f"rule:{rel}", "rule", f"Rule-{n}", rel)
    for p in sorted(c.records):
        rel = _rel(root, p)
        _seed(m, f"record:{rel}", "record", p.name, rel)
    for p in sorted(c.craft_rules):
        rel = _rel(root, p)
        _seed(m, f"craft_rule:{rel}", "craft_rule", p.name, rel)
    for p in sorted(c.ops):
        rel = _rel(root, p)
        _seed(m, f"ops:{rel}", "ops", p.name, rel)
    frame = c.pkg / "CLAUDE.md"
    if frame.exists():
        _seed(m, "frame:" + _rel(root, frame), "frame", "the operating frame", _rel(root, frame))
    vocab = c.pkg / "vocabulary" / "VOCABULARY.md"
    if vocab.exists():
        _seed(m, "term:" + _rel(root, vocab), "term", "vocabulary (every term, one file)", _rel(root, vocab))
    prefs = root / "preferences-corpus" / "PREFERENCES.md"
    if prefs.exists():
        _seed(m, "preference:" + _rel(root, prefs), "preference", "preferences (every key, one file)", _rel(root, prefs))
    inc = c.inst / "audits" / "INCIDENTS.md"
    if inc.exists():
        _seed(m, "incident:" + _rel(root, inc), "incident", "incidents (every row, one file)", _rel(root, inc))
    cl = root / "workstation-corpus" / "CHANGELOG.md"
    if cl.exists():
        _seed(m, "changelog:" + _rel(root, cl), "changelog", "change log (every row, one file)", _rel(root, cl))
    bundle = root / "BUNDLE.md"
    if bundle.exists():   # bundle.component->craft has no extractor (declared, unwalkable) — seeded so it is still visible, per failure.md's "loud" property
        _seed(m, "bundle:" + _rel(root, bundle), "bundle", "bundle manifest", _rel(root, bundle))

_RULE_NUM = re.compile(r"RULE-(\d+)-")

def _normalize_target(root: Path, c, target_kind: str, token: str) -> tuple[str, str]:
    """(node_key, "") for a target this module can place as a live node from a store the reference
    guard already parsed; ("", "<kind>: <token>") otherwise — a terminal chip, never a second
    parser reaching past what Rule-20's own Corpus holds."""
    if target_kind == "row" and token.isdigit() and int(token) in c.row_files:
        return "row:" + _rel(root, c.row_files[int(token)]), ""
    if target_kind == "rule":
        if token.isdigit() and int(token) in c.rules:
            return "rule:" + _rel(root, c.rules[int(token)]), ""
        m = _RULE_NUM.search(token)
        if m and int(m.group(1)) in c.rules:
            return "rule:" + _rel(root, c.rules[int(m.group(1))]), ""
    if target_kind == "record":
        for base in (c.pkg / "rules", c.pkg, c.root):   # file_exists' own search order
            p = base / token
            if p.exists():
                return "record:" + _rel(root, p), ""
    return "", f"{target_kind}: {token}"

def _edge_status(c, target_kind: str, resolve, token: str) -> str:
    """Mirrors `references.check()`'s own severity order (never a second engine): a `crafts/…`
    file token or a bare craft-name token is judged by `c.craft_state` first — the same install
    check the guard runs — before falling through to the plain resolver, so an absent-but-unknown
    craft reads `world` here exactly as it prints `warn … inference` there, never a false `fail`."""
    craft_path = target_kind == "file" and token.startswith("crafts/")
    if craft_path or target_kind == "craft":
        if c.crafts_absent:
            return "world"
        state = c.craft_state(token)
        if state:
            return "fail" if state[0] == "FAIL" else "world"
    if isinstance(resolve, str):
        return "world" if resolve == "world" else "delegated"       # "guard:<corpus>/<entity>.py" — another Rule's guard verifies it
    try:
        return "ok" if resolve(c, token) else "fail"
    except Exception:
        return "unresolved"        # a resolver that needs state this projector's Corpus build didn't reach — shown, not hidden

def collect(root: Path, pkg: Path = dyadlib.PKG) -> Model:
    m = Model()
    c = references.Corpus(root, pkg)
    _seed_stores(m, root, c)
    for kind, src_entity, src_field, extract, target_kind, resolve in references.REFERENCES:
        if extract is None:
            n = 0   # pr.body->row, cache.source->path, bundle.component->craft: declared, no extractor at all
        else:
            pairs = sorted(extract(c))
            n = len(pairs)
            for where, token in pairs:
                path = where.split(" ", 1)[0]
                remainder = where[len(path):].strip()
                src_key = f"{src_entity}:{path}"
                src = m.nodes.get(src_key) or _seed(m, src_key, src_entity, path.rsplit("/", 1)[-1], path)
                target_key, terminal_text = _normalize_target(root, c, target_kind, token)
                status = _edge_status(c, target_kind, resolve, token)
                label = remainder if remainder else src_field   # `where`'s remainder is self-describing on every kind (verified); prefixing the field name a second time doubled it (#50's own incident, caught live)
                src.edges.append(Edge(kind=kind, label=label, status=status, target=target_key, terminal_text=terminal_text))
        note = ("no extractor (declared, unwalkable)" if extract is None
                else "unresolvable (The World)" if resolve == "world"
                else f"resolved by {resolve}" if isinstance(resolve, str)
                else "")
        m.kind_notes.append((kind, f"{src_entity} → {target_kind}", n, note))
    for n in m.nodes.values():
        n.edges.sort(key=lambda e: (e.kind, e.label, e.target or e.terminal_text))
    return m

# ---- render --------------------------------------------------------------------------------------

def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)

CSS = """
body{font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:0;padding:24px 32px 64px;background:#0b0d10;color:#d8dee4}
h1{font-size:20px;margin:0 0 4px}
p.sub{color:#8b96a3;margin:0 0 18px;max-width:80ch}
#legend{background:#12151a;border:1px solid #262b33;border-radius:8px;padding:10px 14px;margin-bottom:16px;max-width:90ch}
#legend li{margin:2px 0}
table.kt{border-collapse:collapse;margin-bottom:20px;font-size:12.5px}
table.kt td,table.kt th{border-bottom:1px solid #262b33;padding:3px 10px 3px 0;text-align:left}
table.kt td.n{text-align:right;color:#8b96a3}
input#q{background:#12151a;border:1px solid #262b33;color:#d8dee4;border-radius:6px;padding:5px 9px;width:32ch;margin-bottom:14px}
details.kind{margin-bottom:6px}
details.kind>summary{font-weight:600;cursor:pointer;padding:5px 0;color:#e7ecf2}
details.kind>summary .cnt{color:#657081;font-weight:400}
details.inst{margin:2px 0 2px 18px;border-left:2px solid #232830;padding-left:10px}
details.inst>summary{cursor:pointer;padding:3px 0;color:#c7d0da}
details.inst>summary .path{color:#657081;margin-left:8px;font-size:12px}
details.inst[open]>summary{color:#fff}
.edges{margin:4px 0 8px}
.egroup{margin:3px 0}
.egroup .k{color:#657081;margin-right:6px}
.chip{display:inline-block;border-radius:5px;padding:1px 7px;margin:1px 3px 1px 0;font-size:12px;border:1px solid #2b313b}
.chip.ok{background:#0f1f16;border-color:#1f4430;color:#8fd6a8}
.chip.fail{background:#2a1414;border-color:#5a2323;color:#f0a3a3}
.chip.world{background:#1c1a10;border-color:#4a3f1c;color:#e0c877}
.chip.delegated{background:#12181f;border-color:#233042;color:#8fb4d6}
.chip.unresolved{background:#1a1a1a;border-color:#333;color:#999}
.chip.term{cursor:default}
a.jump{color:#9dc4ee;text-decoration:none;cursor:pointer}
a.jump:hover{text-decoration:underline}
.cycle{color:#e0c877}
.hidden{display:none !important}
mark{background:#3a3410;color:#fff}
"""

_STATUS_TITLE = {"ok": "resolves", "fail": "does NOT resolve", "world": "unresolvable (The World) — inference",
                 "delegated": "verified by another guard, not this surface", "unresolved": "could not be checked here"}

def _kind_table(notes: list[tuple[str, str, int, str]]) -> str:
    rows = "".join(
        f"<tr><td><code>{_esc(k)}</code></td><td>{_esc(se)}</td><td class='n'>{n}</td><td>{_esc(note)}</td></tr>"
        for k, se, n, note in notes)
    return f"<table class='kt'><thead><tr><th>reference kind</th><th>source → target</th><th>edges</th><th>note</th></tr></thead><tbody>{rows}</tbody></table>"

def render(m: Model) -> str:
    graph = {k: {"kind": n.kind, "label": n.label, "path": n.path,
                 "edges": [{"kind": e.kind, "label": e.label, "status": e.status,
                            "target": e.target, "text": e.terminal_text} for e in n.edges]}
              for k, n in sorted(m.nodes.items())}
    by_kind: dict[str, list[str]] = {}
    for k, n in sorted(m.nodes.items()):
        by_kind.setdefault(n.kind, []).append(k)
    kinds_html = []
    for kind in sorted(by_kind):
        keys = by_kind[kind]
        kinds_html.append(
            f'<details class="kind" data-kind="{_esc(kind)}"><summary>{_esc(kind)} <span class="cnt">({len(keys)})</span></summary>'
            f'<div class="instances" data-kind="{_esc(kind)}"></div></details>')
    n_edges = sum(len(n["edges"]) for n in graph.values())
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\">"
        "<title>The Dyad System — instance traversal</title><style>" + CSS + "</style></head><body>"
        "<h1>The Dyad System — instance traversal (sysarch instances projection)</h1>"
        f"<p class='sub'>{len(m.nodes)} instances, {n_edges} edges, drawn from Rule-20's reference register "
        "(<code>agent/references.py</code>) alone — no edge here is hand-drawn. "
        "Every drawer is closed by default; click a kind, then an instance, then an edge to drill in.</p>"
        "<ul id='legend'>"
        "<li>An instance is keyed by the leading repo-relative path of its reference-guard location; a multi-instance file "
        "(a term in <code>VOCABULARY.md</code>, a row in <code>INCIDENTS.md</code>, a preference, a change-log row) collapses "
        "onto <b>one</b> drawer, and the specific instance is named on the edge's own label instead — stated limitation, d-work #50.</li>"
        "<li><span class='chip ok'>ok</span> the target resolves (Rule-20) &nbsp; <span class='chip fail'>fail</span> it does not "
        "&nbsp; <span class='chip world'>world</span> unresolvable by design, inference only "
        "&nbsp; <span class='chip delegated'>delegated</span> another guard verifies it, not this surface "
        "&nbsp; <span class='chip unresolved'>unresolved</span> could not be checked while building this page.</li>"
        "<li>A target shown as plain text (<code>kind: token</code>, no link) is a terminal — this surface has no live "
        "drawer for that kind (a commit, a craft, a PR, a manifest component, a run-book command, …); its resolution status "
        "is still the one Rule-20's own guard computed.</li>"
        "<li>A cycle (e.g. <code>rule.text-&gt;rule</code>) marks the repeat as <span class='chip cycle'>&#8635; already open above</span> "
        "and jumps to the one canonical (top-level) drawer for that instance rather than recursing.</li></ul>"
        + _kind_table(m.kind_notes) +
        "<p><input id='q' type='search' placeholder='filter instances by label or path…' aria-label='filter'></p>"
        "<div id='tree'>" + "".join(kinds_html) + "</div>"
        "<script>const GRAPH=" + json.dumps(graph, sort_keys=True, separators=(",", ":")) + ";\n" + _JS + "</script>"
        "</body></html>\n")

_JS = r"""
function esc(s){return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function statusTitle(s){return {ok:'resolves',fail:'does NOT resolve',world:'unresolvable (The World) — inference',
  delegated:'verified by another guard, not this surface',unresolved:'could not be checked here'}[s] || s;}
function topId(key){return 'top-' + key.replace(/[^a-zA-Z0-9_-]/g, '_');}

function edgesHTML(edges){
  if(!edges.length) return "<p class='sub'>no outgoing reference</p>";
  const groups = {};
  for(const e of edges){ (groups[e.kind] ||= []).push(e); }
  let out = "<div class='edges'>";
  for(const kind of Object.keys(groups).sort()){
    out += "<div class='egroup'><span class='k'>" + esc(kind) + "</span>";
    for(const e of groups[kind]){
      const title = esc(e.label) + ' — ' + statusTitle(e.status);
      if(e.target){
        out += "<span class='chip " + e.status + " jumpwrap' data-target='" + esc(e.target) + "' title=\"" + title + "\">"
             + esc(e.label) + " →</span>";
      } else {
        out += "<span class='chip " + e.status + " term' title=\"" + title + "\">" + esc(e.label) + ": " + esc(e.text) + "</span>";
      }
    }
    out += "</div>";
  }
  return out + "</div>";
}

function buildInstance(key, ancestors){
  const node = GRAPH[key];
  const d = document.createElement('details');
  d.className = 'inst'; d.dataset.key = key;
  if(ancestors.length === 0) d.id = topId(key);
  const s = document.createElement('summary');
  s.innerHTML = esc(node.label) + (node.path ? "<span class='path'>" + esc(node.path) + "</span>" : "");
  d.appendChild(s);
  let built = false;
  d.addEventListener('toggle', () => {
    if(!d.open || built) return;
    built = true;
    const body = document.createElement('div');
    body.innerHTML = edgesHTML(node.edges);
    d.appendChild(body);
    body.querySelectorAll('.jumpwrap').forEach(chip => {
      const tgt = chip.dataset.target;
      chip.style.cursor = 'pointer';
      chip.addEventListener('click', (ev) => {
        ev.stopPropagation();
        if(ancestors.includes(tgt) || key === tgt){
          const marker = document.createElement('span');
          marker.className = 'chip cycle';
          marker.textContent = '↺ already open above';
          marker.style.marginLeft = '4px';
          marker.style.cursor = 'pointer';
          marker.addEventListener('click', (e2) => { e2.stopPropagation(); revealTop(tgt); });
          if(!chip.nextSibling || !chip.nextSibling.classList || !chip.nextSibling.classList.contains('cycle'))
            chip.after(marker);
          return;
        }
        let nested = chip.nextSibling;
        if(nested && nested.tagName === 'DETAILS'){ nested.open = !nested.open; return; }
        nested = buildInstance(tgt, ancestors.concat([key]));
        nested.style.marginLeft = '14px';
        chip.after(nested);
        nested.open = true;
      });
    });
  });
  return d;
}

function revealTop(key){
  const el = document.getElementById(topId(key));
  if(!el) return;
  let p = el;
  while(p){ if(p.tagName === 'DETAILS') p.open = true; p = p.parentElement; }
  el.open = true;
  el.scrollIntoView({behavior:'smooth', block:'center'});
  el.style.outline = '2px solid #9dc4ee';
  setTimeout(() => { el.style.outline = ''; }, 1500);
}

document.querySelectorAll('details.kind').forEach(kd => {
  let built = false;
  kd.addEventListener('toggle', () => {
    if(!kd.open || built) return;
    built = true;
    const kind = kd.dataset.kind;
    const holder = kd.querySelector('.instances');
    Object.keys(GRAPH).filter(k => GRAPH[k].kind === kind).sort().forEach(k => {
      holder.appendChild(buildInstance(k, []));
    });
  });
});

document.getElementById('q').addEventListener('input', (ev) => {
  const q = ev.target.value.trim().toLowerCase();
  document.querySelectorAll('details.kind').forEach(kd => {
    if(q) kd.open = true;
    let anyVisible = false;
    if(!kd.querySelector('.instances').children.length && q){ kd.dispatchEvent(new Event('toggle')); }
  });
  setTimeout(() => {
    document.querySelectorAll('details.inst').forEach(inst => {
      const key = inst.dataset.key, node = GRAPH[key];
      const hay = (node.label + ' ' + node.path).toLowerCase();
      const show = !q || hay.includes(q);
      inst.classList.toggle('hidden', !show);
      if(q && show) inst.open = true;
    });
  }, 0);
});
"""

def main() -> int:
    root = dyadlib.repo_root()
    out = dyadlib.instance(root) / "projections" / "instances.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    m = collect(root, dyadlib.PKG)
    text = render(m)
    out.write_text(text)
    n_edges = sum(len(n.edges) for n in m.nodes.values())
    print(f"ok   [project] instances: {len(m.nodes)} instances, {n_edges} edges -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
