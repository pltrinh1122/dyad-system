#!/usr/bin/env python3
"""ERD projector (crafts/sysarch/rules/projection.md). Kernel: Python 3.12+, stdlib only.
Projects the corpus onto an entity-relationship surface: every entity is a data model the
package already parses — the guards' parsers (sysarch guards.md: `vocabulary.parse`, `manifest.parse_manifest`,
`containment.ZONES`) and dyadlib's (Rules, rows, plans, preference keys, falsification records,
audits); every edge is a reference those parsers yield. Output: one self-contained HTML file (inline CSS, JS, SVG),
deterministic (sorted iteration, no timestamps), written to <instance>/projections/erd.html.
  project_erd.py            write the projection and print entity/edge counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_erd.py: Python 3.12+ required")
import html, re
from dataclasses import dataclass, field
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib
vocabulary, infrastructure, containment = (dyadlib.load_guard("agent", "vocabulary"), dyadlib.load_guard("infra", "manifest"), dyadlib.load_guard("infra", "containment"))

# entity kinds in column order (fixed: the layout is part of the projection's determinism)
KINDS = ("Set", "Rule", "Term", "Record", "Preference", "Component", "Zone", "Path", "Row", "Plan", "Audit")
INVARIANTS = [("kinds-distinct", lambda: len(set(KINDS)) == len(KINDS))]   # crafts/syseng/rules/invariants.md

@dataclass(frozen=True)
class Entity:
    kind: str
    id: str
    label: str
    attrs: tuple[tuple[str, str], ...] = ()
    @property
    def key(self) -> str:
        return f"{self.kind}:{self.id}"

@dataclass(frozen=True)
class Edge:
    src: str   # Entity.key
    dst: str
    label: str

@dataclass
class Graph:
    entities: list[Entity] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    def add(self, e: Entity) -> None:
        self.entities.append(e)
    def link(self, src: str, dst: str, label: str) -> None:
        self.edges.append(Edge(src, dst, label))
    def by_kind(self) -> dict[str, list[Entity]]:
        out: dict[str, list[Entity]] = {}
        for e in sorted(self.entities, key=lambda e: (e.kind, _sort_id(e.id))):
            out.setdefault(e.kind, []).append(e)
        return out

def _sort_id(s: str):
    return (0, int(s), "") if s.isdigit() else (1, 0, s)

# ---- parsing helpers (each reads a shape its owning Rule's code already defines)
_RULE_TITLE = re.compile(r"^# Rule-(\d+):\s*(.+)$", re.M)
_SET = re.compile(r"^Set:\s*([^(\n]+?)\s*(?:\(.*\))?\.?\s*$", re.M)   # `Set: <name> (kernel; content: …).` names the set before the parenthesis (#160)
_TARGET = re.compile(r"^\*\*Target:\*\*\s*(.+)$", re.M)
_RECORD = re.compile(r"^rules?-((?:\d+-)+)")
_RULE_REF = re.compile(r"Rule-(\d+)")
_RANGE = re.compile(r"#(\d+)\s*[–—-]\s*#?(\d+)")
_BARE = re.compile(r"#(\d+)")

def parse_refs(refs: str) -> list[tuple[int, str]]:
    """(target id, label) for every d-work reference in a row's `refs` cell: `parent #N`,
    `children #a–#b` (a range, en dash or hyphen), bare `#N`. A segment naming PRs
    (`PR #9`, `PRs #65 #66`) refers to pull requests, not rows, and is skipped."""
    out = []
    for seg in re.split(r"[;,]", refs):
        seg = seg.strip()
        if not seg or seg.lower().startswith("pr"):
            continue
        low = seg.lower()
        if low.startswith("children"):
            m = _RANGE.search(seg)
            ids = range(int(m.group(1)), int(m.group(2)) + 1) if m else [int(x) for x in _BARE.findall(seg)]
            out += [(i, "child") for i in ids]
        elif low.startswith("parent"):
            out += [(int(x), "parent") for x in _BARE.findall(seg)]
        else:
            out += [(int(x), "refs") for x in _BARE.findall(seg)]
    return out

def collect(root: Path, pkg: Path = dyadlib.PKG) -> Graph:
    """Every entity and edge the corpus parsers yield, for the instance under `root`."""
    g = Graph()
    inst = dyadlib.instance(root)
    for s in ("System Requirements", "System Architecture"):
        g.add(Entity("Set", s, s))
    terms = vocabulary.parse((pkg / "vocabulary" / "VOCABULARY.md").read_text())
    owned: dict[str, int] = {}
    for term, _, owner, _ in terms:
        owned[owner] = owned.get(owner, 0) + 1
    rules = dyadlib.rule_files(pkg)
    for n, p in sorted(rules.items()):
        text = p.read_text()
        title = (m.group(2) if (m := _RULE_TITLE.search(text)) else p.stem).strip()
        rset = (m.group(1) if (m := _SET.search(text)) else "").strip()
        target = (m.group(1) if (m := _TARGET.search(text)) else "").strip()
        g.add(Entity("Rule", str(n), f"Rule-{n}: {title}",
                     (("set", rset), ("target", target), ("owned terms", str(owned.get(str(n), 0))))))
        if rset:
            g.link(f"Rule:{n}", f"Set:{rset}", "in set")
    for term, _, owner, used in sorted(terms):
        g.add(Entity("Term", term, term, (("owner", owner), ("used by", used))))
        if owner.isdigit():
            g.link(f"Term:{term}", f"Rule:{owner}", "owner")
        for r in used.split():
            if r.isdigit() and r != owner:
                g.link(f"Term:{term}", f"Rule:{r}", "used by")
    for p in sorted((pkg / "falsification" / "rules").glob("*.md")):
        g.add(Entity("Record", p.stem, p.stem))
        if m := _RECORD.match(p.name):
            for n in m.group(1).strip("-").split("-"):
                g.link(f"Record:{p.stem}", f"Rule:{n}", "falsifies")
    prefs = root / "preferences-corpus" / "PREFERENCES.md"
    if prefs.exists():
        for key, value, _, read_by in vocabulary.parse(prefs.read_text().replace("\\|", "/")):  # `\|` escapes a pipe in `allowed`
            if key == "key":
                continue
            g.add(Entity("Preference", key, key, (("value", value), ("read by", read_by))))
            for n in sorted(set(_RULE_REF.findall(read_by)), key=int):
                g.link(f"Preference:{key}", f"Rule:{n}", "read by")
    for _, row in infrastructure.manifest_rows(pkg, root)[0]:   # the one manifest: core, crafts, instance (#175)
        comp = dyadlib.plain(row[0])
        g.add(Entity("Component", comp, comp, (("partition", row[1]), ("version", row[2]))))
        g.link(f"Component:{comp}", "Rule:14", "declared by")
    for zone, pat in containment.ZONES:
        if not any(e.kind == "Zone" and e.id == zone for e in g.entities):
            g.add(Entity("Zone", zone, zone))
        g.add(Entity("Path", pat, pat))
        g.link(f"Zone:{zone}", f"Path:{pat}", "claims")
    rows = dyadlib.read_rows(root) if dyadlib.rows_dir(root).is_dir() else []
    ids = {r.id for r in rows}
    for r in rows:
        g.add(Entity("Row", str(r.id), f"#{r.id}", (("state", r.state), ("title", r.title[:60]))))
        for tid, label in parse_refs(r.refs):
            if tid in ids:
                g.link(f"Row:{r.id}", f"Row:{tid}", label)
    plans = inst / "d-work" / "plans"
    for p in sorted(plans.glob("*.md"), key=lambda p: int(p.stem) if p.stem.isdigit() else -1):
        if p.stem.isdigit():
            g.add(Entity("Plan", p.stem, f"plan {p.stem}"))
            if int(p.stem) in ids:
                g.link(f"Plan:{p.stem}", f"Row:{p.stem}", "plans")
    audits = inst / "audits"
    n_aud = len([p for p in audits.glob("*.md") if p.name != "INCIDENTS.md"]) if audits.is_dir() else 0
    g.add(Entity("Audit", "audits", "audits", (("count", str(n_aud)),)))
    keys = {e.key for e in g.entities}
    g.edges = sorted((e for e in g.edges if e.src in keys and e.dst in keys), key=lambda e: (e.src, e.dst, e.label))
    return g

# ---- rendering: layered layout, one column per kind, entities sorted; fixed geometry
W, GAP_X, GAP_Y, LINE, PAD = 210, 90, 14, 14, 10

def _esc(s: str) -> str:
    return html.escape(s, quote=True)

def _cut(s: str, n: int = 30) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

def render(graph: Graph) -> str:
    cols = [(k, graph.by_kind()[k]) for k in KINDS if k in graph.by_kind()]
    pos: dict[str, tuple[int, int, int]] = {}  # key -> (x, y, h)
    for ci, (_, ents) in enumerate(cols):
        y = 40
        for e in ents:
            h = PAD * 2 + LINE * (1 + len(e.attrs))
            pos[e.key] = (ci * (W + GAP_X) + 20, y, h)
            y += h + GAP_Y
    width = len(cols) * (W + GAP_X) + 20
    height = max((y + h for _, y, h in pos.values()), default=60) + 20
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    for ci, (kind, ents) in enumerate(cols):
        out.append(f'<text class="col" x="{ci * (W + GAP_X) + 20}" y="24">{_esc(kind)} ({len(ents)})</text>')
    for ed in graph.edges:
        (x1, y1, h1), (x2, y2, h2) = pos[ed.src], pos[ed.dst]
        if x1 < x2:
            ax, ay, bx, by = x1 + W, y1 + h1 // 2, x2, y2 + h2 // 2
        elif x1 > x2:
            ax, ay, bx, by = x1, y1 + h1 // 2, x2 + W, y2 + h2 // 2
        else:
            ax, ay, bx, by = x1 + W, y1 + h1 // 2, x2 + W, y2 + h2 // 2
        cx = (ax + bx) // 2 if x1 != x2 else ax + 40
        out.append(f'<g class="edge" data-src="{_esc(ed.src)}" data-dst="{_esc(ed.dst)}">'
                   f'<path d="M{ax},{ay} C{cx},{ay} {cx},{by} {bx},{by}"/>'
                   f'<text x="{(ax + bx) // 2}" y="{(ay + by) // 2 - 3}">{_esc(ed.label)}</text></g>')
    for _, ents in cols:
        for e in ents:
            x, y, h = pos[e.key]
            lines = [f'<text class="t" x="{x + PAD}" y="{y + PAD + 11}">{_esc(_cut(e.label))}</text>']
            for i, (k, v) in enumerate(e.attrs):
                lines.append(f'<text class="a" x="{x + PAD}" y="{y + PAD + 11 + LINE * (i + 1)}">{_esc(_cut(f"{k}: {v}", 34))}</text>')
            out.append(f'<g class="node" data-key="{_esc(e.key)}" data-kind="{_esc(e.kind)}">'
                       f'<title>{_esc(e.label)}</title><rect x="{x}" y="{y}" width="{W}" height="{h}" rx="4"/>{"".join(lines)}</g>')
    out.append("</svg>")
    sections = "".join(
        f'<section data-kind="{_esc(k)}"><label><input type="checkbox" checked data-kind="{_esc(k)}"> {_esc(k)} '
        f'<small>({len(ents)})</small></label></section>' for k, ents in cols)
    return (HEAD + f'<h1>dyad corpus — entity-relationship projection (sysarch projection.md)</h1>'
            f'<p>{len(graph.entities)} entities, {len(graph.edges)} edges. Hover a box to highlight its edges; untick a type to hide it.</p>'
            f'<nav id="filters">{sections}</nav><div id="canvas">{"".join(out)}</div>' + TAIL)

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>dyad ERD projection</title>
<style>
:root{--bg:#fafafa;--fg:#1a1a1a;--box:#fff;--line:#8a8a8a;--edge:#b0b0b0;--hi:#d97706;--dim:.15}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#e6e6e6;--box:#1f1f1f;--line:#777;--edge:#555;--hi:#fbbf24}}
body{margin:0;padding:16px;font:14px system-ui,sans-serif;background:var(--bg);color:var(--fg)}
h1{font-size:18px;margin:0 0 4px}p{margin:0 0 8px}
#filters{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:10px}#filters section label{cursor:pointer}
#canvas{overflow:auto;border:1px solid var(--line);background:var(--bg)}
svg{display:block;font:11px ui-monospace,monospace}
text.col{font-weight:700;font-size:13px;fill:var(--fg)}
.node rect{fill:var(--box);stroke:var(--line);stroke-width:1}.node text.t{fill:var(--fg);font-weight:700}.node text.a{fill:var(--fg);opacity:.75}
.edge path{fill:none;stroke:var(--edge);stroke-width:1}.edge text{fill:var(--edge);font-size:9px}
.node.hi rect{stroke:var(--hi);stroke-width:2}.edge.hi path{stroke:var(--hi);stroke-width:2}.edge.hi text{fill:var(--hi)}
svg.focus .node:not(.hi),svg.focus .edge:not(.hi){opacity:var(--dim)}
.off{display:none}
</style></head><body>
"""
TAIL = """<script>
(function(){
  var svg=document.querySelector('svg'),nodes=svg.querySelectorAll('.node'),edges=svg.querySelectorAll('.edge');
  nodes.forEach(function(n){
    n.addEventListener('mouseenter',function(){
      var k=n.dataset.key;svg.classList.add('focus');n.classList.add('hi');
      edges.forEach(function(e){if(e.dataset.src===k||e.dataset.dst===k){e.classList.add('hi');
        var o=svg.querySelector('.node[data-key="'+CSS.escape(e.dataset.src===k?e.dataset.dst:e.dataset.src)+'"]');if(o)o.classList.add('hi');}});
    });
    n.addEventListener('mouseleave',function(){svg.classList.remove('focus');svg.querySelectorAll('.hi').forEach(function(x){x.classList.remove('hi');});});
  });
  document.querySelectorAll('#filters input').forEach(function(cb){cb.addEventListener('change',function(){
    var off={};document.querySelectorAll('#filters input').forEach(function(c){if(!c.checked)off[c.dataset.kind]=1;});
    nodes.forEach(function(n){n.classList.toggle('off',!!off[n.dataset.kind]);});
    edges.forEach(function(e){e.classList.toggle('off',!!(off[e.dataset.src.split(':')[0]]||off[e.dataset.dst.split(':')[0]]));});
  });});
})();
</script></body></html>
"""

def main() -> int:
    root = dyadlib.repo_root()
    g = collect(root, dyadlib.PKG)
    out = dyadlib.instance(root) / "projections" / "erd.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = render(g)
    out.write_text(text)
    print(f"ok   [project] erd: {len(g.entities)} entities, {len(g.edges)} edges -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
