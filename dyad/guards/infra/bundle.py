#!/usr/bin/env python3
"""Bundle guard (entity `bundle`, infra corpus; Rule-11 owns the check, placed per Rule-11 property 1). Kernel: Python 3.12+.
`BUNDLE.md` (repo root, infra zone — a distribution artifact of the authoring repo, never craft
content, so a core-only install carries no bundle naming a craft it lacks, Rule-11 property 7) names
the whole distribution this repo authors: one row per craft in the tree, the core craft
(`CORE_NAME`) plus every Tended craft `dyadlib.craft_dirs` finds. A row's version must equal that
craft's live `VERSION`; every craft in the tree needs a row and every row names a craft in the tree
— checked both directions. A missing `BUNDLE.md` skips (a core-only install, or this repo before
its first bundle): zero messages, never a failure.
  bundle.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("bundle.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "bundle", "infra", False
NAME, OWNER = "bundle row", "Rule-11"
CORE_NAME = "dyad-operator"                        # crafts/craft.py's own CORE_NAME; a bundle row uses the same name
FIELDS = ("component", "version")
INVARIANTS = [("two-fields", lambda: len(FIELDS) == 2 and len(set(FIELDS)) == 2)]   # crafts/syseng/rules/invariants.md

def bundle_path(root: Path) -> Path:
    return root / "BUNDLE.md"

def parse(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(version, rows): the `version:` line and the table's (component, version) pairs, emphasis
    stripped. A malformed row (not exactly 2 cells) contributes nothing; `check` reports it."""
    version = ""
    for line in text.splitlines():
        if line.startswith("version:"):
            version = dyadlib.plain(line.split(":", 1)[1]).strip()
            break
    rows = [tuple((dyadlib.plain(c).strip() for c in r)) for r in dyadlib.table_rows(text)]
    return version, [r for r in rows if len(r) == 2]

def live_components(pkg: Path = dyadlib.PKG) -> dict[str, str]:
    """{component: version} the tree actually holds: the core craft plus every Tended craft."""
    out = {CORE_NAME: (pkg / "VERSION").read_text().strip()}
    for d in dyadlib.craft_dirs(pkg):
        out[d.name] = (d / "VERSION").read_text().strip()
    return out

def check(version: str, rows: list[tuple[str, str]], live: dict[str, str]) -> list[str]:
    msgs: list[str] = []
    if not version:
        msgs.append("no `version:` line")
    seen: set[str] = set()
    for comp, ver in rows:
        if not comp or not ver:
            msgs.append(f"row {(comp, ver)!r}: malformed (needs a component and a version)"); continue
        if comp in seen:
            msgs.append(f"'{comp}': declared twice")
        seen.add(comp)
        if comp not in live:
            msgs.append(f"'{comp}': not a craft in this tree")
        elif ver != live[comp]:
            msgs.append(f"'{comp}': bundle names {ver}, the tree has {live[comp]}")
    for comp in live:
        if comp not in seen:
            msgs.append(f"'{comp}' is in the tree but has no bundle row")
    return msgs

def check_bundle(root: Path | None = None, pkg: Path = dyadlib.PKG) -> tuple[str, list[tuple[str, str]], list[str]]:
    """(version, rows, messages); (\"\", [], []) when `BUNDLE.md` is absent — skip, never fail."""
    root = root or dyadlib.repo_root()
    p = bundle_path(root)
    if not p.exists():
        return "", [], []
    version, rows = parse(p.read_text())
    return version, rows, check(version, rows, live_components(pkg))

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return check_bundle(root, pkg)[2]

def summary(root: Path | None = None) -> str:
    version, rows, _ = check_bundle(root)
    return f"{len(rows)} components (v{version})" if version or rows else "no bundle"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    p = bundle_path(root)
    _, rows, _ = check_bundle(root, pkg)
    ex = rows[0] if rows else None
    rel = p.relative_to(root) if p.is_relative_to(root) else p
    return {"store": str(rel), "parser": "`bundle.parse`", "observed": len(rows),
            "note": "one row per craft in the tree; a row's version must equal that craft's live VERSION",
            "fields": [(c, "text", "", True, ex[i] if ex else "", "bundle.FIELDS") for i, c in enumerate(FIELDS)]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    if not bundle_path(root).exists():
        print("skip [bundle] no BUNDLE.md")
        return 0
    version, rows, msgs = check_bundle(root)
    for m in msgs:
        print(f"FAIL [bundle] {m}", file=sys.stderr)
    if not msgs:
        print(f"ok   [bundle] {len(rows)} components, v{version}")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
