#!/usr/bin/env python3
"""Preference guard (entity `preference`, preferences corpus; the frame owns the table (Operator-owned),
the Rule named in `read by` owns each value's meaning, the guard placed per Rule-11 property 1). Kernel: Python 3.12+.
`preferences-corpus/PREFERENCES.md` (instance; seeded from `dyad/templates/PREFERENCES.md`): the table
header is FIELDS; every row has a unique non-empty key, a value, an `allowed` cell and a `read by` cell
naming at least one `Rule-N` that exists (`dyadlib.rule_files`); when `allowed` is an enumeration
(alternatives separated by `\\|`, each backticked) the value is one of them; otherwise `allowed` is
free text and the value is inference. A missing file passes (an install seeds it). The template is
the preference schema (`dyad/vocabulary/VOCABULARY.md`'s `package` row: package-level, not
per-instance); a key it carries but the live corpus does not warns (`missing_keys`, #180) — an
instance never re-seeded after the template gained a key a Rule now reads.
  preferences.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("preferences.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "preference", "preferences", False
NAME, OWNER = "preference row", "frame (Operator-owned; read by the Rule named)"
FIELDS = ("key", "value", "allowed", "read by")
INVARIANTS = [("fields-in-order", lambda: FIELDS == ("key", "value", "allowed", "read by"))]   # crafts/syseng/rules/invariants.md
_RULE = re.compile(r"\bRule-(\d+)\b")

def preferences_path(root: Path) -> Path:
    return root / "preferences-corpus" / "PREFERENCES.md"

def parse(text: str) -> tuple[list[str], list[list[str]]]:
    """Header and rows; an escaped pipe `\\|` inside a cell is kept as `|`."""
    t = text.replace("\\|", "\x00")
    header, rows = dyadlib.table_header(t), dyadlib.table_rows(t)
    return [h.replace("\x00", "|") for h in header], [[c.replace("\x00", "|") for c in r] for r in rows]

def alternatives(allowed: str) -> list[str] | None:
    """The values an enumeration cell admits (`\\`a\\` | \\`b\\``), or None for free text."""
    if "|" not in allowed:
        return None
    parts = [dyadlib.plain(p).strip() for p in allowed.split("|")]
    return parts if all(parts) else None

def keys(text: str) -> set[str]:
    """The non-empty `key` cells of a preference table (first column; malformed rows contribute none)."""
    return {r[0] for r in parse(text)[1] if r and r[0]}

def missing_keys(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Template keys (the preference schema, package-level — every key a Rule reads) absent from the
    live corpus; empty when either file is absent (a missing live corpus is a fresh, unseeded install
    — Rule-11's own check; a missing template is this guard's own header check, not this one)."""
    root = root or dyadlib.repo_root()
    tmpl, p = pkg / "templates" / "PREFERENCES.md", preferences_path(root)
    if not tmpl.exists() or not p.exists():
        return []
    return sorted(keys(tmpl.read_text()) - keys(p.read_text()))

def check_text(text: str, where: str, rules: dict[int, Path]) -> list[str]:
    header, rows = parse(text); msgs, seen = [], set()
    if tuple(header) != FIELDS:
        msgs.append(f"{where}: header {header or 'missing'} is not {list(FIELDS)}")
        return msgs
    for k, r in enumerate(rows, 1):
        if len(r) != len(FIELDS):
            msgs.append(f"{where} row {k}: {len(r)} cells, want {len(FIELDS)}"); continue
        d = dict(zip(FIELDS, r))
        if not d["key"]:
            msgs.append(f"{where} row {k}: empty key"); continue
        if d["key"] in seen:
            msgs.append(f"{where}: `{d['key']}` defined twice")
        seen.add(d["key"])
        for f in ("value", "allowed", "read by"):
            if not d[f]:
                msgs.append(f"{where}: `{d['key']}` has an empty `{f}` cell")
        alts = alternatives(d["allowed"])
        if alts is not None and dyadlib.plain(d["value"]).strip() not in alts:
            msgs.append(f"{where}: `{d['key']}` value `{d['value']}` is not one of {' | '.join(alts)}")
        ns = _RULE.findall(d["read by"])
        if d["read by"] and not ns:
            msgs.append(f"{where}: `{d['key']}` read by names no Rule")
        for n in ns:
            if int(n) not in rules:
                msgs.append(f"{where}: `{d['key']}` read by Rule-{n}, which does not exist")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    rules = dyadlib.rule_files(pkg); msgs = []
    tmpl = pkg / "templates" / "PREFERENCES.md"
    if tmpl.exists():
        msgs += check_text(tmpl.read_text(), "templates/PREFERENCES.md", rules)
    p = preferences_path(root)
    if p.exists():
        rel = p.relative_to(root) if p.is_relative_to(root) else p
        msgs += check_text(p.read_text(), str(rel), rules)
    for k in missing_keys(root, pkg):
        msgs.append(f"warning: {p.relative_to(root) if p.is_relative_to(root) else p}: key `{k}` is in templates/PREFERENCES.md but has no row here — seed it (a fresh install would have)")
    return msgs

def summary(root: Path | None = None) -> str:
    p = preferences_path(root or dyadlib.repo_root())
    return f"{len(parse(p.read_text())[1]) if p.exists() else 0} preferences"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    p = preferences_path(root)
    rows = parse(p.read_text())[1] if p.exists() else []
    first = rows[0] if rows else []
    rel = p.relative_to(root) if p.is_relative_to(root) else p
    allowed = {"key": "unique", "allowed": "an enumeration (`a` \\| `b`) or free text", "read by": "Rule references (`Rule-N`)"}
    return {"store": str(rel), "parser": "`preferences.parse` (`dyadlib.table_header` / `table_rows`; template `templates/PREFERENCES.md`)", "observed": len(rows),
            "note": "Operator-owned; the Agent proposes a change by a preferences-zone PR and acts on the value on main",
            "fields": [(c, "text", allowed.get(c, ""), True, first[i] if i < len(first) else "", "preferences.FIELDS") for i, c in enumerate(FIELDS)]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs: print(f"FAIL [preferences] {m}", file=sys.stderr)
    if not msgs: print(f"ok   [preferences] {summary(root)}, read-by Rules resolve")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
