#!/usr/bin/env python3
"""<Surface> projector (crafts/sysarch/rules/projection.md): renders <what> from parsed corpus data —
<the parsers it consumes: dyadlib.read_rows, a guard's FIELDS/describe, references.REFERENCES, …> —
as one self-contained HTML file (inline CSS/SVG, no external resource), deterministic (sorted
iteration, no timestamps), written to <instance>/projections/<surface>.html.

Skeleton. Copy to crafts/<craft>/projectors/project_<surface>.py, write its test at
crafts/<craft>/tests/test_project_<surface>.py (fixture data, a live run, render twice and compare),
and the core runner discovers it: `dyad project --list` shows `<surface> <craft>`.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_<surface>.py: Python 3.12+ required")
import html
from dataclasses import dataclass, field
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts
import dyadlib

@dataclass
class Model:
    """The projection's data model: everything `render` needs, already sorted."""
    items: list[tuple[str, str]] = field(default_factory=list)

def collect(root: Path, pkg: Path = dyadlib.PKG) -> Model:
    """Parse, never hand-draw: consume the owning Rule's parser (a guard via `dyadlib.load_guard`,
    `dyadlib.read_rows`, …) and return the model with every list sorted."""
    return Model(items=sorted([]))

CSS = "body{font:14px system-ui,sans-serif;margin:24px}"

def render(m: Model) -> str:
    """Byte-identical for the same model: no timestamp, no version banner, sorted iteration."""
    body = "".join(f"<li>{html.escape(k)}: {html.escape(v)}</li>" for k, v in m.items)
    return f"<!doctype html><html><head><meta charset=\"utf-8\"><title><surface></title><style>{CSS}</style></head><body><ul>{body}</ul></body></html>\n"

def main() -> int:
    root = dyadlib.repo_root()
    out = dyadlib.instance(root) / "projections" / "<surface>.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = render(collect(root, dyadlib.PKG))
    out.write_text(text)
    print(f"ok   [project] <surface>: {len(text.encode())} bytes -> {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
