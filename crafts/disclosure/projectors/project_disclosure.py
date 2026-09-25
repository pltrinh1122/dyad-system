#!/usr/bin/env python3
"""Disclosure projector (the disclosure craft's surface; `crafts/disclosure/rules/redaction.md`). Kernel: Python 3.12+, stdlib only.
Assembles one **disclosure** from an instance's incident log and writes it to
`<instance>/projections/disclosure.html`: audience, level, watermark, a manifest, and one group per
month with its count, its consequence shapes and — at `LEVEL=standard` — the Agent-authored external
summary for that month if one exists.
Assembled by allow-list (property 1): every cell written here is a date, a count, a controlled value, a
pseudonym or Agent prose written for this audience. No cell is copied from the log. The **gate**
(property 2) runs over the assembled text before anything is written: one finding and nothing is
written and the exit code is 1.
One self-contained file, no external reference (property 6); deterministic, no timestamp of its own
(property 7). Grouping is by month — the coarsest grouping the log's own data supports without
inference; mode-level grouping waits for mode records that carry their row ids (backlog, d-work #166).
Parameters from the environment: `AUDIENCE` (required), `LEVEL` (`standard` | `minimal`), `LEDGER`.
  project_disclosure.py     assemble, gate and write; print the manifest
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_disclosure.py: Python 3.12+ required")
import html, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dyadlib
import redaction

SURFACE = "disclosure"
LEVELS = ("standard", "minimal")
SHAPES = (("caught before it reached the shared branch", ("caught before", "before any commit", "never on `main`", "nothing was pushed", "before any push")),
          ("reached the shared branch and was corrected", ("on `main`", "reached `main`", "red `main`", "landed")),
          ("no loss of data or work", ("nothing was lost", "no loss", "without loss", "recovered")),
          ("not classified", ()))
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("levels-distinct", lambda: len(set(LEVELS)) == len(LEVELS) and LEVELS[0] == "standard"),
    ("shapes-end-with-unclassified", lambda: SHAPES[-1][1] == () and len(SHAPES) >= 2),
    ("surface-matches-module", lambda: Path(__file__).stem == f"project_{SURFACE}"),
]

def incidents_parser():
    """The log's one parser (`dyad/scripts/incidents.py`). None when the core does not carry it yet —
    the absent-store pattern: this projector then refuses with a stated reason rather than parsing the
    log a second way (Rule-13)."""
    mod = Path(dyadlib.PKG) / "scripts" / "incidents.py"
    try:
        return dyadlib.load_module(mod, "dyad_incidents") if mod.is_file() else None
    except Exception:
        return None

def shape_of(consequence: str) -> str:
    """The controlled consequence value for one row: the first shape whose words the cell carries.
    The cell itself is never written to a disclosure."""
    low = consequence.lower()
    for name, words in SHAPES:
        if words and any(w.lower() in low for w in words):
            return name
    return SHAPES[-1][0]

def collect(root: Path, ledger: Path | None = None) -> dict:
    """{watermark, groups: [{key, count, shapes: {shape: n}, summary}]} — counts and controlled values
    only. `summary` is Agent prose from `<instance>/disclosure/summaries/<key>.md`, or ""."""
    inc = incidents_parser()
    rows = inc.parse(path=ledger, root=root) if inc else []
    latest = max((r["date"] for r in rows if r["date"]), default="")
    groups = []
    for key, rs in (inc.by_year_month(rows).items() if inc else []):
        shapes: dict[str, int] = {}
        for r in rs:
            s = shape_of(r["consequence"])
            shapes[s] = shapes.get(s, 0) + 1
        f = dyadlib.instance(root) / "disclosure" / "summaries" / f"{key or 'undated'}.md"
        groups.append({"key": key or "undated", "count": len(rs),
                       "shapes": {k: shapes[k] for k in sorted(shapes)},
                       "summary": f.read_text(errors="ignore").strip() if f.is_file() else ""})
    return {"watermark": f"covered through: {len(rows)} rows, latest {latest or 'none'}", "groups": groups}

def pseudonymize(text: str, root: Path) -> tuple[str, int]:
    """Replace every mapped Class B value in Agent prose by its pseudonym, longest real value first so
    a value containing another is replaced whole. Returns (text, replacements)."""
    n = 0
    for real, pseud in sorted(redaction.pseudonyms(root).items(), key=lambda kv: -len(kv[0])):
        if real and real in text:
            n += text.count(real)
            text = text.replace(real, pseud)
    return text, n

CSS = """<style>
:root{--bg:#fbfbfd;--fg:#1a1a1f;--mut:#5b5b66;--line:#dcdce4;--card:#fff}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14141a;--fg:#ececf2;--mut:#9a9aa8;--line:#2c2c38;--card:#1c1c24}}
:root[data-theme="dark"]{--bg:#14141a;--fg:#ececf2;--mut:#9a9aa8;--line:#2c2c38;--card:#1c1c24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:52rem;margin:0 auto;padding:2.2rem 16px 4rem}
h1{font-size:1.5rem;margin:0 0 .2rem}h2{font-size:1.1rem;margin:0 0 .6rem}
.mut{color:var(--mut)}.small{font-size:.86rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.1rem;margin:0 0 1rem}
table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{text-align:left;padding:.35rem .5rem;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--mut)}td.n{text-align:right;font-variant-numeric:tabular-nums}
.sum{white-space:pre-wrap;margin:.6rem 0 0}
</style>"""

def render(data: dict, audience: str, level: str) -> str:
    e = html.escape
    manifest = data["manifest"]
    out = ["<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">",
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
           f"<title>Incident summary for {e(audience)}</title>", CSS, "</head><body><main>",
           f"<h1>Incident summary</h1>",
           f"<p class=\"mut\">Prepared for <strong>{e(audience)}</strong> · level {e(level)}</p>",
           f"<p class=\"small mut\">{e(data['watermark'])}<br>",
           f"manifest: {manifest['removed']} identity value(s) withheld, {manifest['replaced']} internal name(s) replaced by stable labels, "
           f"{manifest['groups']} group(s) reported</p>",
           "<div class=\"card\"><h2>How to read this</h2><p class=\"small\">Counts and dates are exact. "
           "Internal component names are replaced by stable labels (<em>SUBSYSTEM-n</em>, <em>COMPONENT-n</em>): the same label "
           "means the same component across reports, and no label can be resolved from this document. "
           "Identity — hosts, paths, addresses, accounts — is withheld entirely, not labelled.</p></div>"]
    for g in data["groups"]:
        out.append(f"<div class=\"card\"><h2>{e(g['key'])} — {g['count']} incident(s)</h2>")
        out.append("<table><tr><th>consequence</th><th>count</th></tr>")
        for shape, n in g["shapes"].items():
            out.append(f"<tr><td>{e(shape)}</td><td class=\"n\">{n}</td></tr>")
        out.append("</table>")
        if g["summary"]:
            out.append(f"<p class=\"sum small\">{e(g['summary'])}</p>")
        out.append("</div>")
    if not data["groups"]:
        out.append("<div class=\"card\"><p>No incidents in the covered source.</p></div>")
    out.append("</main></body></html>\n")
    return "\n".join(out)

def assemble(root: Path, audience: str, level: str, ledger: Path | None = None) -> tuple[str, dict]:
    """(text, manifest). The gate is the caller's: `assemble` never writes."""
    data = collect(root, ledger)
    replaced = 0
    for g in data["groups"]:
        if level == "minimal":
            g["summary"] = ""
        elif g["summary"]:
            g["summary"], n = pseudonymize(g["summary"], root)
            replaced += n
    inc = incidents_parser()
    rows = inc.parse(path=ledger, root=root) if inc else []
    data["manifest"] = {"removed": sum(1 for r in rows for f in ("what", "cause", "consequence")
                                       for _ in redaction.findings(r[f], root)) if rows else 0,
                        "replaced": replaced, "groups": len(data["groups"])}
    return render(data, audience, level), data["manifest"]

def main() -> int:
    root = dyadlib.repo_root()
    if incidents_parser() is None:
        print(f"refused [project] {SURFACE}: the core craft carries no incident guard "
              "(dyad/scripts/incidents.py); nothing assembled", file=sys.stderr)
        return 2
    audience = os.environ.get("AUDIENCE", "").strip()
    if not audience:
        print(f"refused [project] {SURFACE}: AUDIENCE is required "
              "(dyad/playbooks/ds-report-incidents.md, Parameters)", file=sys.stderr)
        return 2
    level = os.environ.get("LEVEL", "standard").strip() or "standard"
    if level not in LEVELS:
        print(f"refused [project] {SURFACE}: LEVEL must be one of {', '.join(LEVELS)}", file=sys.stderr)
        return 2
    led = os.environ.get("LEDGER", "").strip()
    text, manifest = assemble(root, audience, level, Path(led) if led else None)
    hits = redaction.findings(text, root)
    if hits:
        for cls, name, hit in hits[:20]:
            print(f"FAIL [redaction] class {cls.upper()} {name}: {hit!r}", file=sys.stderr)
        print(f"refused [project] {SURFACE}: the gate found {len(hits)} finding(s) in the assembled "
              "document; nothing written (rules/redaction.md property 2)", file=sys.stderr)
        return 1
    out = dyadlib.instance(root) / "projections" / f"{SURFACE}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"ok   [project] {SURFACE}: {manifest['groups']} group(s), "
          f"{manifest['removed']} withheld, {manifest['replaced']} replaced -> {out} ({len(text.encode())} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
