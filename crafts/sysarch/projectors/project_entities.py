#!/usr/bin/env python3
"""entity-schema projector (crafts/sysarch/rules/projection.md). Kernel: Python 3.12+, stdlib only.
Projects the schema of every data entity of The Dyad System onto one card each. Since plan #151
(sysarch guards.md) the entity list *is* the guard registry: every `dyad/guards/<corpus>/<entity>.py` and, since #155,
every Tended craft's `crafts/<craft>/guards/<entity>.py` declares
`ENTITY`, `FIELDS` (the schema constant) and `describe(root, pkg)` (store, parser, note, count, and
per field: type, allowed values, required flag, one example observed in the instance, marked as
example) and, since #162, its `INVARIANTS` names (the invariants column, crafts/syseng/rules/invariants.md); the projector zips `FIELDS` with the description and draws relations from the Rule-20
register (`references.REFERENCES`, property 5). It holds no entity list and no relation table of its
own. Output: one self-contained HTML file (inline CSS and JS, no external reference), deterministic
(sorted iteration, no timestamps), written to <instance>/projections/entities.html.
  project_entities.py         write the projection and print entity/field counts
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_entities.py: Python 3.12+ required")
import html, re
from dataclasses import dataclass, field
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib
references = dyadlib.load_guard("agent", "references")

@dataclass(frozen=True)
class Field:
    name: str
    type: str                 # int | date | text | enum | path | line | bullets | function | table
    allowed: str              # allowed values or format; "" when free
    required: bool
    example: str              # one value observed in the instance ("" when none observed)
    source: str               # the constant or header the name comes from

@dataclass
class Entity:
    key: str                  # sort key and DOM id (the guard's ENTITY)
    name: str
    owner: str                # the Rule (or frame) whose concern the entity is
    store: str                # path pattern
    parser: str               # the package code that parses it
    corpus: str = ""          # the guard's CORPUS (sysarch guards.md)
    guard: str = ""           # guards/<corpus>/<entity>.py, or crafts/<craft>/guards/<entity>.py
    fields: list[Field] = field(default_factory=list)
    relations: list[tuple[str, str]] = field(default_factory=list)   # (field, target entity key)
    observed: int = 0         # instances found
    note: str = ""
    invariants: list[str] = field(default_factory=list)   # the guard module's INVARIANTS names, sorted (crafts/syseng/rules/invariants.md; #162)

# Relations: (entity, anchor, target) — the entity an anchor's value names. An anchor is one of the
# entity's parsed field names, or a `<token>` of its store path (`<id>`). The set is the Rule-20
# register (`references.REFERENCES`, property 5): the projector holds no table of its own; a triple
# whose anchor or target is not on this surface is dropped, so the edges drawn are the ones the
# guard resolves. One anchor may name two targets (`row.refs` -> row and rule), hence triples.
RELATIONS = {(src, anchor, tgt) for _kind, src, anchor, _ext, tgt, _res in references.REFERENCES}
INVARIANTS = [("relations-from-register", lambda: bool(RELATIONS) and {(s, a, t) for s, a, t in RELATIONS} == {(r[1], r[2], r[4]) for r in references.REFERENCES})]   # crafts/syseng/rules/invariants.md

def collect(root: Path, pkg: Path = dyadlib.PKG, guards_pkg: Path = dyadlib.PKG) -> list[Entity]:
    """One entity per guard of `guards_pkg` (the registry, sysarch guards.md), described over the instance under
    `root` and the package data under `pkg`. A guard whose description does not name exactly its
    FIELDS, in order, is a bug and raises."""
    out: list[Entity] = []
    for py in dyadlib.guard_files(guards_pkg):
        root_kind, group, entity = dyadlib.guard_key(py, guards_pkg)
        g = dyadlib.load_guard_file(py, guards_pkg)
        d = g.describe(root, pkg)
        names = [f[0] for f in d["fields"]]
        if names[:len(g.FIELDS)] != list(g.FIELDS):
            raise ValueError(f"{py.name}: describe() fields {names} do not start with FIELDS {list(g.FIELDS)}")
        e = Entity(g.ENTITY, getattr(g, "NAME", g.ENTITY), getattr(g, "OWNER", ""), d["store"], d["parser"], g.CORPUS,
                   f"guards/{group}/{py.name}" if root_kind == "core" else f"crafts/{group}/guards/{py.name}", observed=d.get("observed", 0), note=d.get("note", ""))
        e.fields = [Field(*f) for f in d["fields"]]
        e.invariants = sorted(n for n, _ in getattr(g, "INVARIANTS", []))
        out.append(e)
    keys = {e.key for e in out}
    if len(keys) != len(out):
        raise ValueError("two guards declare the same ENTITY")
    for e in out:
        anchors = {f.name for f in e.fields} | set(re.findall(r"<[a-z]+>", e.store))
        e.relations = sorted((a, t) for k, a, t in RELATIONS if k == e.key and a in anchors and t in keys)
    return sorted(out, key=lambda e: e.key)

def _esc(s: str) -> str:
    return html.escape(s, quote=True)

def _cut(s: str, n: int = 160) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"

def render(entities: list[Entity]) -> str:
    cards = []
    for e in entities:
        rows = "".join(
            f'<tr><td class="f">{_esc(f.name)}{"" if f.required else " <small>(optional)</small>"}</td><td><span class="ty">{_esc(f.type)}</span></td>'
            f'<td>{_esc(f.allowed)}</td><td class="ex">{("<span class=\"tag\">example</span> " + _esc(_cut(f.example))) if f.example else "<span class=\"none\">none observed</span>"}</td></tr>'
            for f in e.fields)
        rels = "".join(f'<li><code>{_esc(fn)}</code> → <a href="#e-{_esc(t)}">{_esc(t)}</a></li>' for fn, t in e.relations)
        srcs = sorted({f.source for f in e.fields})
        invs = "".join(f"<li><code>{_esc(n)}</code></li>" for n in e.invariants)
        cards.append(
            f'<article class="card" id="e-{_esc(e.key)}" data-key="{_esc(e.key)}" data-owner="{_esc(e.owner)}">'
            f'<h2>{_esc(e.name)}</h2><p class="badges"><span class="badge owner">{_esc(e.owner)}</span><span class="badge store">{_esc(e.store)}</span>'
            f'<span class="badge count">{e.observed} observed</span><span class="badge guard">{_esc(e.corpus)} · {_esc(e.guard)}</span></p>'
            f'<p class="meta">parser: {_esc(e.parser)} · fields from: {_esc(", ".join(srcs))}</p>'
            f'<div class="tw"><table><thead><tr><th>field</th><th>type</th><th>allowed / format</th><th>example (instance)</th></tr></thead><tbody>{rows}</tbody></table></div>'
            + (f'<p class="note">{_esc(e.note)}</p>' if e.note else "")
            + (f'<ul class="rels">{rels}</ul>' if rels else '<p class="note">no relation</p>')
            + (f'<p class="meta">invariants ({len(e.invariants)}, syseng invariants.md):</p><ul class="rels inv">{invs}</ul>' if invs else '<p class="note">no invariant declared</p>') + '</article>')
    n_fields = sum(len(e.fields) for e in entities)
    n_inv = sum(len(e.invariants) for e in entities)
    toc = "".join(f'<a href="#e-{_esc(e.key)}">{_esc(e.name)}</a>' for e in entities)
    return (HEAD + '<h1>The Dyad System — entity schemas (sysarch projection.md)</h1>'
            f'<p>{len(entities)} entities, {n_fields} fields, {n_inv} invariants. One card per guard (sysarch guards.md): every field name comes from the guard\'s `FIELDS`; '
            'example values are read from this instance and marked <span class="tag">example</span>. '
            'Type a word to filter cards by name, field or owner.</p>'
            f'<nav id="toc">{toc}</nav><p><input id="q" type="search" placeholder="filter…" aria-label="filter cards"></p>'
            '<ul id="legend"><li><span class="badge owner">owner Rule</span></li><li><span class="badge store">store path</span></li><li><span class="badge guard">corpus · guard</span></li>'
            '<li><span class="badge count">instances observed</span></li><li><span class="ty">type</span> int · date · text · enum · path · line · bullets · function</li>'
            '<li><span class="tag">example</span> one value from the instance, not part of the schema</li>'
            '<li><code>invariants</code> the guard module\'s <code>INVARIANTS</code> names, run by the runner before any check (syseng)</li></ul>'
            f'<main id="grid">{"".join(cards)}</main>' + TAIL)

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>dyad entity schemas</title>
<style>
:root{--bg:#fafafa;--fg:#1a1a1a;--card:#fff;--line:#c9c9c9;--muted:#5b5b5b;--owner:#dbeafe;--owner-fg:#1e3a8a;--store:#ecfccb;--store-fg:#365314;
--count:#f3e8ff;--count-fg:#581c87;--tag:#fef3c7;--tag-fg:#92400e;--ty:#e5e7eb;--ty-fg:#374151;--zebra:#f4f4f4}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#e6e6e6;--card:#1f1f1f;--line:#444;--muted:#a3a3a3;--owner:#1e3a8a;--owner-fg:#dbeafe;
--store:#365314;--store-fg:#ecfccb;--count:#581c87;--count-fg:#f3e8ff;--tag:#92400e;--tag-fg:#fef3c7;--ty:#374151;--ty-fg:#e5e7eb;--zebra:#242424}}
body{margin:0;padding:16px;font:14px system-ui,sans-serif;background:var(--bg);color:var(--fg)}
h1{font-size:18px;margin:0 0 4px}h2{font-size:15px;margin:0 0 6px}p{margin:0 0 8px}
#toc{display:flex;flex-wrap:wrap;gap:6px 14px;margin-bottom:8px}#toc a{color:inherit}
#q{font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:4px;background:var(--card);color:var(--fg);width:min(100%,320px)}
#legend{display:flex;flex-wrap:wrap;gap:10px 18px;list-style:none;margin:0 0 12px;padding:0;color:var(--muted)}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;min-width:0}
.card.off{display:none}.card:target{outline:2px solid var(--tag-fg)}
.badges{display:flex;flex-wrap:wrap;gap:6px}.badge{display:inline-block;padding:1px 7px;border-radius:10px;font-size:12px}
.owner{background:var(--owner);color:var(--owner-fg)}.store{background:var(--store);color:var(--store-fg);font-family:ui-monospace,monospace}
.count{background:var(--count);color:var(--count-fg)}.guard{background:var(--ty);color:var(--ty-fg);font-family:ui-monospace,monospace}.tag{background:var(--tag);color:var(--tag-fg);padding:0 5px;border-radius:6px;font-size:11px}
.ty{background:var(--ty);color:var(--ty-fg);padding:0 5px;border-radius:4px;font-family:ui-monospace,monospace;font-size:12px}
.meta,.note{color:var(--muted);font-size:12px}.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:4px 0 8px}th,td{text-align:left;vertical-align:top;padding:3px 6px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600}tbody tr:nth-child(even){background:var(--zebra)}td.f{font-family:ui-monospace,monospace;white-space:nowrap}td.ex{font-family:ui-monospace,monospace;word-break:break-word}
.none{color:var(--muted);font-style:italic}.rels{margin:0;padding-left:18px;font-size:12.5px}.rels a{color:inherit}
</style></head><body>
"""
TAIL = """<script>
(function(){
  var q=document.getElementById('q'),cards=document.querySelectorAll('.card');
  q.addEventListener('input',function(){var s=q.value.trim().toLowerCase();
    cards.forEach(function(c){c.classList.toggle('off',!!s&&c.textContent.toLowerCase().indexOf(s)<0);});});
})();
</script></body></html>
"""

def main() -> int:
    root = dyadlib.repo_root()
    out = dyadlib.instance(root) / "projections" / "entities.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    ents = collect(root, dyadlib.PKG)
    text = render(ents)
    out.write_text(text)
    n_fields = sum(len(e.fields) for e in ents); n_inv = sum(len(e.invariants) for e in ents)
    print(f"ok   [project] entities: {len(ents)} entities, {n_fields} fields, {n_inv} invariants -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
