#!/usr/bin/env python3
"""Plan-file guard (entity `plan`, agent corpus; Rule-15 owns the plan file, placed per Rule-11 property 1). Kernel: Python 3.12+.
Every `<instance>/d-work/plans/<id>.md` starts with a title line `# Plan #<id>` whose id equals the
file name (a title after ` — ` is free text), carries a base-commit line (`base commit:` in any
case, Rule-15 phase 1). Existence of these parts, nothing more: what a plan says stays inference
(plan #151, mutation 6). A plan naming no intent (no line mentioning `intent`), or never mentioning
a part of dyadlib.PLAN_PARTS, is reported as a warning: plans ratified before Rule-15 keep their
form (plan #138 states a claim instead of an intent). The id → row and base commit → commit references are resolved by
`references.py` (Rule-20).
  plans.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("plans.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "plan", "agent", False
NAME, OWNER = "plan file", "Rule-15"
FIELDS = ("id", "title", "base commit", "intent")     # the header parse() yields; the prose parts are dyadlib.PLAN_PARTS
INVARIANTS = [("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS))]   # crafts/syseng/rules/invariants.md
_TITLE = re.compile(r"^# Plan #(\d+)(?:\s*[—–-]+\s*(.*))?$")
_BASE = re.compile(r"(?i)base commit[^:\n]*:\s*(\S+)")
_INTENT = re.compile(r"(?i)\bintent\b")

def plans_dir(root: Path) -> Path:
    return dyadlib.instance(root) / "d-work" / "plans"

def plans(root: Path) -> list[Path]:
    d = plans_dir(root)
    return sorted((p for p in d.glob("*.md") if p.stem.isdigit()), key=lambda p: int(p.stem)) if d.is_dir() else []

def parse(text: str) -> dict[str, str]:
    """{id, title, base commit, intent}: id and title from the first line, the base-commit value, and
    the first line naming an intent ("" when absent)."""
    first = text.splitlines()[0] if text else ""
    m = _TITLE.match(first)
    b = _BASE.search(text)
    intent = next((l.strip() for l in text.splitlines() if _INTENT.search(l)), "")
    return {"id": m.group(1) if m else "", "title": (m.group(2) or "").strip() if m else "", "base commit": b.group(1) if b else "", "intent": intent}

def check_plan(path: Path, text: str | None = None) -> list[str]:
    text = path.read_text() if text is None else text
    d = parse(text); msgs = []
    if not d["id"]:
        msgs.append(f"{path.name}: first line is not `# Plan #<id>`")
    elif d["id"] != path.stem:
        msgs.append(f"{path.name}: title id #{d['id']} differs from the file name")
    if not d["base commit"]:
        msgs.append(f"{path.name}: no base commit line (Rule-15 phase 1)")
    if not d["intent"]:
        msgs.append(f"warning: {path.name}: names no intent (Rule-15 phase 1)")
    low = text.lower()
    for part in dyadlib.PLAN_PARTS:
        if part not in low:
            msgs.append(f"warning: {path.name}: never mentions `{part}` (dyadlib.PLAN_PARTS)")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    msgs = []
    for p in plans(root):
        msgs += check_plan(p)
    return msgs

def summary(root: Path | None = None) -> str:
    return f"{len(plans(root or dyadlib.repo_root()))} plans"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ps = plans(root)
    texts = {p: p.read_text() for p in ps}
    ex = parse(texts[ps[-1]]) if ps else {}
    d = plans_dir(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    allowed = {"id": "the row it plans (file name)", "title": "free text after ` — `", "base commit": "a commit of `main` (Rule-15)", "intent": "a line naming the intent as read"}
    fields = [(f, "int" if f == "id" else "line", allowed[f], f != "title", ex.get(f, ""), "plans.FIELDS") for f in FIELDS]
    for part in (x for x in dyadlib.PLAN_PARTS if x not in FIELDS):
        n = sum(1 for t in texts.values() if part in t.lower())
        ex_line = next((l.strip() for l in texts[ps[-1]].splitlines() if part in l.lower()), "") if ps else ""
        fields.append((part, "line", f"present in {n}/{len(ps)} plans (observed)" if ps else "", False, ex_line, "dyadlib.PLAN_PARTS"))
    return {"store": f"{rel}/<id>.md", "parser": "`plans.parse` (header); parts named by `dyadlib.PLAN_PARTS`", "observed": len(ps),
            "note": "free-form prose after the header; a plan-Y binds to the file; the id is the row it plans", "fields": fields}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning: ")]
    for m in msgs:
        if m.startswith("warning: "): print(f"warn [rule-15] {m[9:]}")
        else: print(f"FAIL [rule-15] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [rule-15] {len(plans(root))} plans")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
