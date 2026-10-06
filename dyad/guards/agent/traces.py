#!/usr/bin/env python3
"""Trace-store guard (entity `trace`, agent corpus; Rule-3 owns the trace as completion evidence under
`dwork-trace`, placed per Rule-11 property 1). Kernel: Python 3.12+.
The registry entry for the trace store `<instance>/d-work/traces/`, whose parser and check stay in
`dyad/scripts/trace.py` (`check_store`): every file is `<id>.md` for an existing row, opens with
`# Trace #<id> — <title>`, and holds the five sections in order. Run in the guard pass on every push
and evidence run instead of only inside Rule-12's suite (d-work #227; #217 found it suite-only).
Whether a trace's figures are right stays inference: its own Limits section says what it could not
anchor. An absent store passes (no d-work traced yet, a fresh install).
  traces.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("traces.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib
tr = dyadlib.load_module(dyadlib.PKG / "scripts" / "trace.py", "dyad_trace")   # by path: `trace` is also a stdlib module

ENTITY, CORPUS, TRANSACTION = "trace", "agent", False
NAME, OWNER = "d-work trace", "Rule-3"
FIELDS = tr.SECTIONS                       # a trace's parts, in order: what the store check reads
INVARIANTS = [("fields-are-the-sections", lambda: FIELDS == tr.SECTIONS),   # crafts/syseng/rules/invariants.md
              ("store-under-d-work", lambda: tr.TRACES_REL == "d-work/traces")]

def store(root: Path) -> Path:
    return dyadlib.instance(root) / tr.TRACES_REL

def traces(root: Path) -> list[Path]:
    d = store(root)
    return sorted(d.glob("*.md")) if d.is_dir() else []

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return tr.check_store(root or dyadlib.repo_root())

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(traces(root or dyadlib.repo_root()))} traces"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    d = store(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    return {"store": f"{rel}/<id>.md",
            "parser": "`trace.check_store` (dyad/scripts/trace.py; the header line and the section headings)",
            "observed": len(traces(root)),
            "note": "one trace per d-work, written by `dyad dwork trace <id> --out`; transcript text never enters one",
            "fields": [(f, "section", "", True, "", "trace.SECTIONS") for f in FIELDS]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"FAIL [rule-3] {m}", file=sys.stderr)
    if not msgs:
        print(f"ok   [rule-3] {summary(root)}")
    return 1 if msgs else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1)

if __name__ == "__main__":
    sys.exit(main())
