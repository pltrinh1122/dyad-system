#!/usr/bin/env python3
"""system-schema projector (crafts/sysarch/rules/projection.md). Kernel: Python 3.12+, stdlib only.
Projects The Dyad System onto a block diagram: five bands (parties and Rule sets; repo
structure; guard pipeline — hooks, the runner, `dyad/scripts/`, one box per `dyad/guards/<corpus>/` and per `crafts/<craft>/guards/`
(sysarch guards.md), CI wrappers; System Infrastructure; stores), every box filled by a parser the
owning Rule already provides, every arrow one of contains / owns / mentions / runs / wraps /
replaces / reads. Output: one self-contained HTML file (inline CSS, JS, SVG), deterministic
(sorted iteration, no timestamps), written to <instance>/projections/schema.html.
  project_schema.py         write the projection and print layer/box/arrow counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_schema.py: Python 3.12+ required")
import fnmatch, html, importlib.util, re, subprocess
from dataclasses import dataclass, field
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib
vocabulary, infrastructure, containment = (dyadlib.load_guard("agent", "vocabulary"), dyadlib.load_guard("infra", "manifest"), dyadlib.load_guard("infra", "containment"))

LABELS = ("contains", "owns", "mentions", "runs", "wraps", "replaces", "reads")
LAYERS = ("parties and Rule sets", "repo structure", "guard pipeline", "System Infrastructure", "stores")
INVARIANTS = [("labels-and-layers-distinct", lambda: len(set(LABELS)) == len(LABELS) and len(set(LAYERS)) == len(LAYERS))]   # crafts/syseng/rules/invariants.md

@dataclass
class Box:
    id: str                      # unique; an item is addressed as "<box id>/<item key>"
    kind: str                    # party | set | zone | tree | hook | runner | guards | ci | partition | store
    title: str
    items: list[tuple[str, str]] = field(default_factory=list)   # (key, text)
    def item_keys(self) -> set[str]:
        return {f"{self.id}/{k}" for k, _ in self.items}

@dataclass(frozen=True)
class Arrow:
    src: str
    dst: str
    label: str

@dataclass
class Schema:
    layers: list[tuple[str, list[Box]]] = field(default_factory=list)
    arrows: list[Arrow] = field(default_factory=list)
    def boxes(self) -> list[Box]:
        return [b for _, bs in self.layers for b in bs]

_RULE_TITLE = re.compile(r"^# Rule-(\d+):\s*(.+)$", re.M)
_SET = re.compile(r"^Set:\s*([^(\n]+?)\s*(?:\(.*\))?\.?\s*$", re.M)   # `Set: <name> (kernel; content: …).` names the set before the parenthesis (#160)
_PY = re.compile(r"\b([\w-]+\.py)\b")
_HOOK = re.compile(r"\bhooks/(pre-[\w-]+)\b")
_YML = re.compile(r"\b([\w-]+\.yml)\b")
_OWN_SECTIONS = re.compile(r"^## (?:Mechanisms|Enforcement)\b.*?(?=^## |\Z)", re.M | re.S)
_RULE_REF = re.compile(r"Rule-(\d+)")

def _generated(path: str, patterns: list[str]) -> bool:
    """Same match as package.py's generated check: whole path, any component, any suffix."""
    parts = path.split("/")
    cands = [path] + parts + ["/".join(parts[i:]) for i in range(1, len(parts))]
    return any(fnmatch.fnmatch(c, g) for g in patterns for c in cands)

def _files(root: Path, rel: str, generated: list[str] = ()) -> list[str]:
    """Tracked paths under `rel` (git); on disk, minus generated files, when `root` is not a
    repository or `rel` lies outside it (an absolute DYAD_INSTANCE)."""
    try:
        if (root / ".git").exists() and not Path(rel).is_absolute():
            return sorted(subprocess.run(["git", "ls-files", "--", rel], cwd=root, capture_output=True, text=True, check=True).stdout.split())
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    p = root / rel
    return sorted(f"{rel}/{q.relative_to(p)}" for q in p.rglob("*") if q.is_file() and not _generated(str(q.relative_to(p)), generated)) if p.exists() else []

def _load(path: Path):
    prev, sys.dont_write_bytecode = sys.dont_write_bytecode, True   # no __pycache__ side effect: file counts stay deterministic
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prev
    return mod

def collect(root: Path, pkg: Path = dyadlib.PKG) -> Schema:
    """Every box and arrow the corpus parsers yield, for the instance under `root`."""
    s, inst = Schema(), dyadlib.instance(root)
    rules_txt = pkg / "scripts" / "package_rules.txt"
    generated = [l.split(":", 1)[1].strip() for l in rules_txt.read_text().splitlines() if l.startswith("generated:")] if rules_txt.exists() else []
    tracked = lambda rel_: _files(root, rel_, generated)
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)   # DYAD_INSTANCE may be absolute (tests)
    scripts = sorted(p.name for p in (pkg / "scripts").glob("*.py"))
    # guards by corpus (sysarch guards.md): dyad/guards/<corpus>/<entity>.py; a `.py` name in Rule text, a hook or a
    # workflow resolves to a script first, else to the guard of that name
    guards = {d.name: sorted(p.name for p in d.glob("*.py") if not p.name.startswith("_")) for d in sorted((pkg / "guards").glob("*")) if d.is_dir()}
    craft_guards = {d.parent.name: sorted(p.name for p in d.glob("*.py") if not p.name.startswith("_")) for d in dyadlib.craft_glob("guards", pkg) if d.is_dir()}   # a Tended craft's guards (#155)
    craft_projectors = {d.parent.name: sorted(p.name for p in d.glob("project_*.py")) for d in dyadlib.craft_glob("projectors", pkg) if d.is_dir()}   # a craft's projectors (sysarch projection.md p2, #160)
    guard_key = {n: f"guards:{c}/{n}" for c, names in list(guards.items()) + list(craft_guards.items()) for n in names}
    def code_key(name):
        return f"scripts/{name}" if name in scripts else guard_key.get(name)
    hooks = sorted(p.name for p in (pkg / "hooks").iterdir()) if (pkg / "hooks").is_dir() else []
    wf_dir = root / ".github" / "workflows"
    workflows = sorted(p.name for p in wf_dir.glob("dyad-*.yml")) if wf_dir.is_dir() else []
    # 1. parties (vocabulary rows owned by frame) and Rule sets (Set: line), Rules with the mechanisms their text names
    terms = vocabulary.parse((pkg / "vocabulary" / "VOCABULARY.md").read_text())
    parties = [Box(t, "party", t, [("def", d)]) for t, d, o, _ in sorted(terms) if o == "frame" and t in ("Operator", "Agent")]
    sets: dict[str, Box] = {}
    rule_reads: list[tuple[str, str]] = []
    for n, p in sorted(dyadlib.rule_files(pkg).items()):
        text = p.read_text()
        title = (m.group(2) if (m := _RULE_TITLE.search(text)) else p.stem).strip()
        rset = (m.group(1) if (m := _SET.search(text)) else "unset").strip()
        box = sets.setdefault(rset, Box(f"set:{rset}", "set", rset))
        box.items.append((str(n), f"Rule-{n}: {title}"))
        own = "".join(_OWN_SECTIONS.findall(text))
        for name in sorted(set(_PY.findall(text))):
            if code_key(name):
                s.arrows.append(Arrow(f"set:{rset}/{n}", code_key(name), "owns" if name in own else "mentions"))
        for name in sorted(set(_HOOK.findall(text))):
            if name in hooks:
                s.arrows.append(Arrow(f"set:{rset}/{n}", f"hook:{name}", "owns" if name in own else "mentions"))
        for name in sorted(set(_YML.findall(text))):
            wf = name if name in workflows else f"dyad-{name}"
            if wf in workflows:
                s.arrows.append(Arrow(f"set:{rset}/{n}", f"ci:{wf}", "owns" if name in own else "mentions"))
    s.layers.append((LAYERS[0], parties + [sets[k] for k in sorted(sets)]))
    # 2. repo structure: zone -> path pattern (containment.ZONES) -> package | instance trees
    pkg_files = [f for f in tracked(rel(pkg)) + tracked(".github/workflows") if f.startswith(rel(pkg) + "/") or Path(f).name.startswith("dyad-")]
    host = dyadlib.host_path(root)                     # the host path (preference `host-path`, #175)
    inst_trees = [t for t in (rel(inst), host, "preferences-corpus") if (root / t).is_dir()]
    inst_files = [f for t in inst_trees for f in tracked(t)]
    zones: dict[str, Box] = {}
    for zone, pat in containment.table(root):
        zones.setdefault(zone, Box(f"zone:{zone}", "zone", zone)).items.append((pat, pat))
        for tree, files in (("package", pkg_files), ("instance", inst_files)):
            if any(fnmatch.fnmatchcase(f, pat) for f in files):
                s.arrows.append(Arrow(f"zone:{zone}/{pat}", f"tree:{tree}", "contains"))
    package = Box("tree:package", "tree", "package", [(rel(pkg), f"{rel(pkg)}/ ({len([f for f in pkg_files if f.startswith(rel(pkg) + '/')])} files)"),
                                                     ("workflows", f".github/workflows/dyad-*.yml ({len(workflows)})")])
    instance = Box("tree:instance", "tree", "instance", [(t, f"{t}/ ({len(tracked(t))} files)") for t in inst_trees])
    s.layers.append((LAYERS[1], [zones[z] for z in sorted(zones)] + [package, instance]))
    # 3. guard pipeline: hooks -> scripts, the runner (CHECKS, PROJECTORS), CI wrappers with the manifest's status cell
    hook_boxes = []
    for h in hooks:
        b = Box(f"hook:{h}", "hook", f"hooks/{h}")
        for name in sorted(set(_PY.findall((pkg / "hooks" / h).read_text()))):
            if code_key(name):
                b.items.append((name, name)); s.arrows.append(Arrow(f"hook:{h}/{name}", code_key(name), "runs"))
        hook_boxes.append(b)
    runner = Box("runner", "runner", "package.py check"); registry = Box("registry", "runner", "package.py project")
    if (pkg / "scripts" / "package.py").exists():
        mod = _load(pkg / "scripts" / "package.py")
        for k, fn in sorted(getattr(mod, "CHECKS", {}).items()):
            runner.items.append((k, f"{k}: {getattr(fn, '__name__', fn)}" if not hasattr(fn, "__name__") or fn.__name__ != "<lambda>" else f"{k}: check_package"))
            if "/" in k and guard_key.get(k.split("/")[1] + ".py"):
                s.arrows.append(Arrow(f"runner/{k}", guard_key[k.split("/")[1] + ".py"], "runs"))
        for surface, m in sorted(getattr(mod, "PROJECTORS", {}).items()):   # m: `crafts/<craft>/projectors/project_<surface>.py` (discovered, #160)
            registry.items.append((surface, f"{surface}: {m}"))
            parts = m.split("/")
            if len(parts) == 4 and parts[3] in craft_projectors.get(parts[1], []):
                s.arrows.append(Arrow(f"registry/{surface}", f"projectors:{parts[1]}/{parts[3]}", "runs"))
    script_box = Box("scripts", "runner", "dyad/scripts/", [(n, n) for n in scripts])
    guard_boxes = [Box(f"guards:{c}", "guards", f"dyad/guards/{c}/", [(n, n) for n in names]) for c, names in guards.items()]
    guard_boxes += [Box(f"guards:{c}", "guards", f"crafts/{c}/guards/", [(n, n) for n in names]) for c, names in craft_guards.items()]
    projector_boxes = [Box(f"projectors:{c}", "runner", f"crafts/{c}/projectors/", [(n, n) for n in names]) for c, names in craft_projectors.items()]
    rows = [r for _, r in infrastructure.manifest_rows(pkg, root)[0]]   # the one manifest: core, crafts, instance (#175)
    status = next((r[3] for r in rows if "Actions" in r[0]), "no Actions row in the manifest")
    ci_boxes = []
    for wf in workflows:
        b = Box(f"ci:{wf}", "ci", wf, [("status", f"status: {status}")])
        for name in sorted(set(_PY.findall((wf_dir / wf).read_text()))):
            if code_key(name):
                b.items.append((name, name)); s.arrows.append(Arrow(f"ci:{wf}/{name}", code_key(name), "wraps"))
        ci_boxes.append(b)
    s.layers.append((LAYERS[2], hook_boxes + [runner, registry, script_box] + projector_boxes + guard_boxes + ci_boxes))
    # 4. System Infrastructure: kernel | library | The World from the manifest; replacement -> replaces arrow or stub
    parts: dict[str, Box] = {}
    comps = [(dyadlib.plain(r[0]), r) for r in rows]
    for comp, r in sorted(comps):
        parts.setdefault(r[1], Box(f"part:{r[1]}", "partition", r[1])).items.append((comp, f"{comp} — {r[2]}"))
    for comp, r in sorted(comps):
        repl = dyadlib.plain(r[5])
        named = [(c2, r2) for c2, r2 in comps if c2 != comp and re.search(rf"\b{re.escape(c2)}\b", repl)]
        if named:
            for c2, r2 in named:
                s.arrows.append(Arrow(f"part:{r2[1]}/{c2}", f"part:{r[1]}/{comp}", "replaces"))
        elif repl and repl not in ("—", "-"):
            parts[r[1]].items.append((f"{comp}~repl", f"  ↳ replacement: {repl}"))
    s.layers.append((LAYERS[3], [parts[k] for k in ("kernel", "library", "The World") if k in parts] + [parts[k] for k in sorted(parts) if k not in ("kernel", "library", "The World")]))
    # 5. stores: each shown only if present, with its file count; projections/ is generated (package_rules.txt)
    stores = []
    for d in (inst / "d-work" / "rows", inst / "d-work" / "plans", inst / "projections", inst / "audits", inst / "falsification", pkg / "falsification" / "rules"):
        if d.is_dir():
            gen = any(fnmatch.fnmatch(f"{d.name}/x", g) for g in generated)
            name = f"<instance>/{d.relative_to(inst)}" if d.is_relative_to(inst) else rel(d)
            stores.append(Box(f"store:{name}", "store", f"{name}/{' (generated)' if gen else ''}",
                              [("count", "untracked, generated" if gen else f"{len(tracked(rel(d)))} files tracked")]))
    changelog = root / dyadlib.host_path(root) / "CHANGELOG.md"
    if changelog.exists():
        stores.append(Box("store:changelog", "store", rel(changelog), [("count", f"{len(changelog.read_text().splitlines())} lines")]))
    prefs = root / "preferences-corpus" / "PREFERENCES.md"
    if prefs.exists():
        b = Box("store:preferences", "store", rel(prefs))
        for key, value, _, read_by in vocabulary.parse(prefs.read_text().replace("\\|", "/")):
            if key != "key":
                b.items.append((key, f"{key} = {value[:24]}"))
                for n in sorted(set(_RULE_REF.findall(read_by)), key=int):
                    rule_reads.append((n, key))
        stores.append(b)
    s.layers.append((LAYERS[4], stores))
    keys = {b.id for b in s.boxes()} | {k for b in s.boxes() for k in b.item_keys()}
    rule_key = {n: f"{b.id}/{n}" for b in s.boxes() if b.kind == "set" for n, _ in b.items}
    s.arrows += [Arrow(rule_key[n], f"store:preferences/{key}", "reads") for n, key in rule_reads if n in rule_key]
    s.arrows = sorted({a for a in s.arrows if a.src in keys and a.dst in keys}, key=lambda a: (a.src, a.dst, a.label))
    return s

# ---- rendering: five horizontal bands, boxes on a fixed grid, arrows between item or box anchors
W, GAP_X, GAP_Y, LINE, PAD, HEAD_H, BAND_PAD, COLS, LEFT = 250, 30, 24, 14, 8, 22, 34, 6, 20

def _esc(s: str) -> str:
    return html.escape(s, quote=True)

def _cut(s: str, n: int = 40) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

def render(s: Schema) -> str:
    pos: dict[str, tuple[int, int, int, int]] = {}   # key -> (x, y, w, h)
    bands, y = [], 30
    for name, boxes in s.layers:
        top, row_h, col = y + BAND_PAD, 0, 0
        for b in boxes:
            if col == COLS:
                col, top = 0, top + row_h + GAP_Y; row_h = 0
            h = HEAD_H + PAD + LINE * len(b.items)
            x = LEFT + col * (W + GAP_X)
            pos[b.id] = (x, top, W, h)
            for i, (k, _) in enumerate(b.items):
                pos[f"{b.id}/{k}"] = (x, top + HEAD_H + LINE * i, W, LINE)
            row_h, col = max(row_h, h), col + 1
        bands.append((name, y, top + row_h + PAD - y, len(boxes)))
        y = top + row_h + PAD + GAP_Y
    width = LEFT * 2 + COLS * (W + GAP_X) - GAP_X
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}" viewBox="0 0 {width} {y}">']
    for name, by, bh, n in bands:
        out.append(f'<g class="band" data-layer="{_esc(name)}"><rect x="{LEFT // 2}" y="{by}" width="{width - LEFT}" height="{bh}" rx="6"/>'
                   f'<text x="{LEFT}" y="{by + 18}">{_esc(name)} ({n})</text></g>')
    for a in s.arrows:
        (x1, y1, w1, h1), (x2, y2, w2, h2) = pos[a.src], pos[a.dst]
        ay, by_ = y1 + h1 // 2, y2 + h2 // 2
        ax, bx = (x1 + w1, x2) if x1 + w1 <= x2 else (x1, x2 + w2) if x2 + w2 <= x1 else (x1 + w1, x2 + w2)
        cx = (ax + bx) // 2 if ax != bx else ax + 40
        out.append(f'<g class="arrow {a.label}" data-src="{_esc(a.src)}" data-dst="{_esc(a.dst)}">'
                   f'<path d="M{ax},{ay} C{cx},{ay} {cx},{by_} {bx},{by_}"/>'
                   f'<text x="{(ax + bx) // 2}" y="{(ay + by_) // 2 - 3}">{_esc(a.label)}</text></g>')
    for layer, boxes in s.layers:
        for b in boxes:
            x, yb, w, h = pos[b.id]
            items = "".join(f'<text class="i" data-key="{_esc(f"{b.id}/{k}")}" x="{x + PAD}" y="{yb + HEAD_H + LINE * i + 11}"><title>{_esc(t)}</title>{_esc(_cut(t))}</text>'
                            for i, (k, t) in enumerate(b.items))
            out.append(f'<g class="box {b.kind}" data-key="{_esc(b.id)}" data-layer="{_esc(layer)}"><title>{_esc(b.title)}</title>'
                       f'<rect x="{x}" y="{yb}" width="{w}" height="{h}" rx="4"/><text class="t" x="{x + PAD}" y="{yb + 15}">{_esc(_cut(b.title, 36))}</text>{items}</g>')
    out.append("</svg>")
    sections = "".join(f'<section data-layer="{_esc(n)}"><label><input type="checkbox" checked data-layer="{_esc(n)}"> {_esc(n)} <small>({len(bs)})</small></label></section>'
                       for n, bs in s.layers)
    by_label = {l: sum(1 for a in s.arrows if a.label == l) for l in LABELS}
    legend = "".join(f'<li class="arrow {l}"><svg width="28" height="10"><path d="M0,5 L28,5"/></svg> {l} <small>({by_label[l]})</small></li>' for l in LABELS)
    kinds = "".join(f'<li class="box {k}"><svg width="14" height="14"><rect x="1" y="1" width="12" height="12" rx="2"/></svg> {k}</li>'
                    for k in sorted({b.kind for b in s.boxes()}))
    return (HEAD + f'<h1>The Dyad System — schema projection (sysarch projection.md)</h1>'
            f'<p>{len(s.layers)} layers, {len(s.boxes())} boxes, {len(s.arrows)} arrows. Hover a box or a line to highlight its arrows; untick a layer to hide it.</p>'
            f'<nav id="filters">{sections}</nav><ul id="legend">{legend}{kinds}</ul><div id="canvas">{"".join(out)}</div>' + TAIL)

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>dyad system schema</title>
<style>
:root{--bg:#fafafa;--fg:#1a1a1a;--box:#fff;--line:#8a8a8a;--band:#f0f0f0;--hi:#d97706;--dim:.12;
--contains:#6b7280;--owns:#2563eb;--mentions:#93c5fd;--runs:#16a34a;--wraps:#9333ea;--replaces:#dc2626;--reads:#ca8a04}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#e6e6e6;--box:#1f1f1f;--line:#777;--band:#1a1a1a;--hi:#fbbf24}}
body{margin:0;padding:16px;font:14px system-ui,sans-serif;background:var(--bg);color:var(--fg)}
h1{font-size:18px;margin:0 0 4px}p{margin:0 0 8px}
#filters{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:6px}#filters label{cursor:pointer}
#legend{display:flex;flex-wrap:wrap;gap:14px;list-style:none;margin:0 0 10px;padding:0}#legend li{display:flex;align-items:center;gap:4px}
#legend svg{overflow:visible}#legend .arrow path{stroke-width:2}
#canvas{overflow:auto;border:1px solid var(--line);background:var(--bg)}
svg{display:block;font:11px ui-monospace,monospace}
.band rect{fill:var(--band);stroke:none}.band text{font-weight:700;font-size:13px;fill:var(--fg)}
.box rect{fill:var(--box);stroke:var(--line);stroke-width:1}.box text.t{fill:var(--fg);font-weight:700}.box text.i{fill:var(--fg);opacity:.8}
.box.party rect{stroke-width:2}.box.set rect{stroke-dasharray:4 2}.box.store rect{rx:10}.box.guards rect{stroke-width:1.5;stroke-dasharray:2 2}
.arrow path{fill:none;stroke:currentColor;stroke-width:1;opacity:.6}.arrow text{display:none;font-size:9px;fill:currentColor}
.contains{color:var(--contains)}.owns{color:var(--owns)}.mentions{color:var(--mentions)}.runs{color:var(--runs)}
.wraps{color:var(--wraps)}.replaces{color:var(--replaces)}.reads{color:var(--reads)}
.arrow.hi path{stroke-width:2.5;opacity:1}.arrow.hi text{display:block}
.box.hi rect{stroke:var(--hi);stroke-width:2}text.i.hi{fill:var(--hi);opacity:1;font-weight:700}
svg.focus .box:not(.hi),svg.focus .arrow:not(.hi){opacity:var(--dim)}
.off{display:none}
</style></head><body>
"""
TAIL = """<script>
(function(){
  var svg=document.querySelector('#canvas svg'),boxes=svg.querySelectorAll('.box'),arrows=svg.querySelectorAll('.arrow'),items=svg.querySelectorAll('text.i');
  function box(k){return k.split('/')[0];}
  function clear(){svg.classList.remove('focus');svg.querySelectorAll('.hi').forEach(function(x){x.classList.remove('hi');});}
  function focus(k,exact){
    clear();svg.classList.add('focus');
    var self=svg.querySelector('.box[data-key="'+CSS.escape(box(k))+'"]');if(self)self.classList.add('hi');
    arrows.forEach(function(a){
      var s=a.dataset.src,d=a.dataset.dst,hit=exact?(s===k||d===k):(box(s)===k||box(d)===k);
      if(!hit)return;a.classList.add('hi');
      [s,d].forEach(function(e){var b=svg.querySelector('.box[data-key="'+CSS.escape(box(e))+'"]');if(b)b.classList.add('hi');
        var t=svg.querySelector('text.i[data-key="'+CSS.escape(e)+'"]');if(t)t.classList.add('hi');});
    });
  }
  boxes.forEach(function(b){b.addEventListener('mouseenter',function(){focus(b.dataset.key,false);});b.addEventListener('mouseleave',clear);});
  items.forEach(function(t){t.addEventListener('mouseenter',function(ev){ev.stopPropagation();focus(t.dataset.key,true);});});
  document.querySelectorAll('#filters input').forEach(function(cb){cb.addEventListener('change',function(){
    var off={};document.querySelectorAll('#filters input').forEach(function(c){if(!c.checked)off[c.dataset.layer]=1;});
    var hidden={};boxes.forEach(function(b){var o=!!off[b.dataset.layer];b.classList.toggle('off',o);if(o)hidden[b.dataset.key]=1;});
    svg.querySelectorAll('.band').forEach(function(g){g.classList.toggle('off',!!off[g.dataset.layer]);});
    arrows.forEach(function(a){a.classList.toggle('off',!!(hidden[box(a.dataset.src)]||hidden[box(a.dataset.dst)]));});
  });});
})();
</script></body></html>
"""

def main() -> int:
    root = dyadlib.repo_root()
    out = dyadlib.instance(root) / "projections" / "schema.html"
    out.parent.mkdir(parents=True, exist_ok=True)   # before collect: the projections/ store is part of the state projected
    s = collect(root, dyadlib.PKG)
    text = render(s)
    out.write_text(text)
    print(f"ok   [project] schema: {len(s.layers)} layers, {len(s.boxes())} boxes, {len(s.arrows)} arrows -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
