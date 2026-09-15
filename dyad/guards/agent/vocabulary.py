#!/usr/bin/env python3
"""Vocabulary guard (entity `term`, agent corpus; Rule-6 owns the check, placed per Rule-11 property 1). Kernel: Python 3.12+.
Table rows well-formed; no term defined twice; owner is `frame`, `craft` (a Tended craft's term a kernel references) or an existing Rule; every
used-by Rule exists and mentions the term (case-insensitive, emphasis stripped, whitespace
folded so a term may break across lines). Sense is inference.
  vocabulary.py
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("vocabulary.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "term", "agent", False
NAME, OWNER = "vocabulary term", "Rule-6"
COLUMNS = ("term", "definition", "owner", "used by")   # the table parse() yields, in order
FIELDS = COLUMNS
OWNER_LITERALS = ("frame", "craft")                    # owners that are not a Rule number: the frame; a Tended craft's term referenced from a core kernel (#154, #160)
INVARIANTS = [("owner-literals", lambda: OWNER_LITERALS == ("frame", "craft")),   # crafts/syseng/rules/invariants.md
              ("columns-in-order", lambda: COLUMNS == ("term", "definition", "owner", "used by") and CRAFT_COLUMNS[:2] == COLUMNS[:2])]

def fold(text: str) -> str:
    return re.sub(r"\s+", " ", dyadlib.plain(text)).lower()

def parse(table: str) -> list[tuple[str, str, str, str]]:
    rows = []
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in ("term", "") or set(cells[0]) <= {"-"}:
            continue
        rows.append(tuple(cells + [""] * (4 - len(cells)))[:4])
    return rows

def check(table: str, rules: dict[int, str]) -> tuple[int, list[str]]:
    """rules: {number: text}. Returns (term count, failures)."""
    fails, seen = [], set()
    folded = {n: fold(t) for n, t in rules.items()}
    for term, definition, owner, used in parse(table):
        if not (definition and owner and used):
            fails.append(f"FAIL [rule-6] '{term}': malformed row"); continue
        if term in seen:
            fails.append(f"FAIL [rule-6] '{term}': defined twice")
        seen.add(term)
        if owner not in OWNER_LITERALS and not (owner.isdigit() and int(owner) in rules):
            fails.append(f"FAIL [rule-6] '{term}': owner '{owner}' is not a Rule")
        for r in used.split():
            if not (r.isdigit() and int(r) in rules):
                fails.append(f"FAIL [rule-6] '{term}': used-by Rule {r} does not exist"); continue
            if fold(term) not in folded[int(r)]:
                fails.append(f"FAIL [rule-6] '{term}': Rule {r} does not mention it")
    return len(seen), fails

def check_vocabulary(pkg: Path = dyadlib.PKG) -> tuple[int, list[str]]:
    rules = {n: p.read_text() for n, p in dyadlib.rule_files(pkg).items()}
    return check((pkg / "vocabulary" / "VOCABULARY.md").read_text(), rules)

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return [f[5:] if f.startswith("FAIL ") else f for f in check_vocabulary(pkg)[1]]

# ---- a Tended craft's vocabulary (Rule-6 Boundaries: craft terms are referenced, never defined, by the Agent
# vocabulary; #156 namespacing check, called by the craft guard through load_guard — Rule-6 owns it, S4)
CRAFT_COLUMNS = ("term", "definition", "rule")   # `rule`: the craft rule (`rules/<rule>.md`) that owns the term

def parse_craft(table: str) -> list[tuple[str, str, str]]:
    return [(r[0], r[1], r[2]) for r in (tuple(x + ("",) * (3 - len(x)))[:3] for x in parse(table))]

def check_craft(pkg: Path, craft_root: Path) -> list[str]:
    """`<craft_root>/vocabulary/CRAFT.md`: a `term | definition | rule` table, well-formed; no term defined twice;
    every `rule` cell names an existing `rules/<rule>.md` of the craft (space-separated when several); no term
    equal (folded, emphasis stripped) to an Agent vocabulary term — either direction is one fault, reported here.
    Bare lines fail. Whether a differently spelled term collides in *sense* is inference."""
    craft_root = Path(craft_root); name = craft_root.name
    f = craft_root / "vocabulary" / "CRAFT.md"
    if not f.exists():
        return [f"crafts/{name}: no vocabulary/CRAFT.md"]
    header = dyadlib.table_header(f.read_text())
    if header[:2] != ["term", "definition"] or len(header) != 3:
        return [f"crafts/{name}/vocabulary/CRAFT.md: header {header} is not term | definition | rule"]
    agent = {fold(t): t for t, *_ in parse((pkg / "vocabulary" / "VOCABULARY.md").read_text())} if (pkg / "vocabulary" / "VOCABULARY.md").exists() else {}
    fails, seen = [], set()
    for term, definition, rule in parse_craft(f.read_text()):
        where = f"crafts/{name}/vocabulary/CRAFT.md '{term}'"
        if not (term and definition and rule):
            fails.append(f"{where}: malformed row"); continue
        if fold(term) in seen:
            fails.append(f"{where}: defined twice")
        seen.add(fold(term))
        for r in rule.split():
            if not (craft_root / "rules" / f"{r}.md").exists():
                fails.append(f"{where}: rule '{r}' is not crafts/{name}/rules/{r}.md")
        if fold(term) in agent:
            fails.append(f"{where}: equals the Agent vocabulary term '{agent[fold(term)]}' (a craft term is referenced there, never defined; Rule-6)")
    return fails

def craft_terms(craft_root: Path) -> set[str]:
    f = Path(craft_root) / "vocabulary" / "CRAFT.md"
    return {fold(t) for t, *_ in parse_craft(f.read_text())} if f.exists() else set()

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(parse((pkg / 'vocabulary' / 'VOCABULARY.md').read_text()))} terms"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    vocab = pkg / "vocabulary" / "VOCABULARY.md"
    terms = parse(vocab.read_text()) if vocab.exists() else []
    ex = terms[0] if terms else None
    allowed = {"term": "unique", "owner": "`frame` | `craft` | a Rule number", "used by": "Rule numbers, space-separated"}
    rel = vocab.relative_to(root) if vocab.is_relative_to(root) else vocab
    return {"store": str(rel), "parser": "`vocabulary.parse`", "observed": len(terms), "note": "defined once; every used-by Rule must mention it",
            "fields": [(c, "text", allowed.get(c, ""), True, ex[i] if ex else "", "vocabulary.COLUMNS") for i, c in enumerate(COLUMNS)]}

def main():
    n, fails = check_vocabulary()
    for f in fails: print(f, file=sys.stderr)
    if not fails: print(f"ok   [rule-6] {n} terms, owners and used-by resolve")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
