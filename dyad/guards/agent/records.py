#!/usr/bin/env python3
"""Falsification-record guard (entity `record`, agent corpus; Rule-9 owns the form, placed per Rule-11 property 1). Kernel: Python 3.12+.
Every record — a Rule's in `dyad/falsification/rules/` (package, Rule-11 A6), any other in
`<instance>/falsification/` — holds at least one attack table whose header names `attack`,
`result` and `survivor` (any case; a leading `#` column is usual) and a `Disposition:` line
(Rule-9 Form: disposed by the Done-Y of its d-work, by reference). Whether an attack is fair,
a result right or a survivor implemented stays inference; the `ledger #N` reference is resolved
by `references.py` (Rule-20).
  records.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("records.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "record", "agent", False
NAME, OWNER = "falsification record (attack row)", "Rule-9"
FIELDS = ("#", "Attack", "Result", "Survivor")          # the attack-table header, as the records write it
REQUIRED = ("attack", "result", "survivor")             # header cells the check needs, lower-cased
INVARIANTS = [("required-in-fields", lambda: set(REQUIRED) <= {f.lower() for f in FIELDS})]   # crafts/syseng/rules/invariants.md
DISPOSITION = re.compile(r"\bDisposition:")

def record_files(root: Path, pkg: Path = dyadlib.PKG) -> list[Path]:
    """Package records first, then instance records, each sorted."""
    out = []
    for d in (pkg / "falsification" / "rules", dyadlib.instance(root) / "falsification"):
        if d.is_dir():
            out += sorted(d.glob("*.md"))
    return out

def attack_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every table whose header carries the REQUIRED cells."""
    return [(h, rows) for h, rows in dyadlib.tables(text) if set(REQUIRED) <= {c.lower() for c in h}]

def parse(text: str) -> list[list[str]]:
    """The rows of the first attack table (`#`, attack, result, survivor order as written)."""
    t = attack_tables(text)
    return t[0][1] if t else []

def check_record(path: Path, text: str | None = None) -> list[str]:
    text = path.read_text(errors="ignore") if text is None else text
    msgs = []
    if not attack_tables(text):
        msgs.append(f"{path.name}: no attack table (header cells attack, result, survivor)")
    if not DISPOSITION.search(text):
        msgs.append(f"{path.name}: no `Disposition:` line (Rule-9 Form)")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    msgs = []
    for p in record_files(root, pkg):
        msgs += check_record(p)
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(record_files(root or dyadlib.repo_root(), pkg))} records"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    recs = record_files(root, pkg)
    texts = {p: p.read_text(errors="ignore") for p in recs}
    ex_rows = next((parse(t) for t in texts.values() if parse(t)), [])
    results = sorted({m.group(0).lower() for t in texts.values() for h, rows in attack_tables(t)
                      for r in rows if len(r) > [c.lower() for c in h].index("result") and (m := re.search(r"[A-Za-z]+", dyadlib.plain(r[[c.lower() for c in h].index("result")])))})
    inst = dyadlib.instance(root); rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    allowed = {"#": "attack number", "Result": (" | ".join(results) + " (observed first words; Rule-9 Form names confirmed / refuted / survives, scoped)") if results else ""}
    return {"store": f"{rel(pkg)}/falsification/rules/*.md (package) · {rel(inst / 'falsification')}/*.md (instance)",
            "parser": "`records.attack_tables` (every table headed attack / result / survivor)", "observed": len(recs),
            "note": "prose record: title, **Claim**, the attack table(s), a `Disposition: see ledger #N` line; a Rule's record is package (`rule-<n>-` prefix), any other instance",
            "fields": [(c, "enum" if c == "Result" else "text", allowed.get(c, ""), True, ex_rows[0][i] if ex_rows and i < len(ex_rows[0]) else "", "records.FIELDS") for i, c in enumerate(FIELDS)]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"FAIL [rule-9] {m}", file=sys.stderr)
    if not msgs:
        print(f"ok   [rule-9] {len(record_files(root))} records")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
