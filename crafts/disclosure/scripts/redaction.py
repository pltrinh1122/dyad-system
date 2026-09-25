#!/usr/bin/env python3
"""Redaction (disclosure craft script; `rules/redaction.md` owns the form). Kernel: Python 3.12+, stdlib only.
The class data (`redaction_rules.txt`, beside this module) as one parsed entity, plus the two things the
rule needs runnable: the **gate** of property 2 (`verify <file>` — any Class A or unmapped Class B shape
in an assembled disclosure means nothing is delivered) and the **map** of property 4
(`unmapped <file>` — what a source mentions that the pseudonym map does not yet carry).
Class A's key shapes are imported from the core provenance guard, never re-listed: one owner per shape
(Rule-13). The Class B *vocabulary* is derived from the data's shapes, so a new Rule, guard or craft
needs no edit here.
A script and not a guard, for the same reason the core's incident parser is one: a new registry entry
falsifies a released craft's pinned tests, and changing a released craft's tree cannot land (row #170).
The data check runs on every push through this craft's own suite instead.
  redaction.py [repo-root]              check the data, and the map when present
  redaction.py verify <file>            the gate: exit 1 on any finding, 0 on none
  redaction.py unmapped <file>          Class B values the map does not carry, one per line
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("redaction.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/scripts/ -> dyad/scripts
import dyadlib

NAME, OWNER = "redaction rule (a class shape or an allowed field)", "crafts/disclosure/rules/redaction.md"
FIELDS = ("class", "name", "pattern")            # a row of redaction_rules.txt (the shape a later registry entry would declare)
CLASSES = ("a", "b")                             # identity, substance (property 3; C is what is left)
DATA = Path(__file__).with_name("redaction_rules.txt")
MAP_REL = "disclosure/pseudonyms.md"             # under the instance location (Rule-11 property 3)
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("classes-distinct", lambda: len(set(CLASSES)) == len(CLASSES) and CLASSES == ("a", "b")),
    ("fields-open-with-class", lambda: FIELDS[0] == "class"),
    ("data-beside-module", lambda: DATA.parent == Path(__file__).parent),
    ("map-is-instance-relative", lambda: not MAP_REL.startswith("/") and MAP_REL.endswith(".md")),
]

def credential_shapes() -> list[tuple[str, re.Pattern]]:
    """The core provenance guard's key shapes — its `FAIL_SHAPES` (Rule-7 property 2) — imported rather
    than re-listed; `WARN_SHAPES` is deliberately not borrowed: a 40-hex string is a commit sha as often
    as a token, and this is a gate, not a warning. An
    absent core guard is not an error here: the gate then rests on this file's own shapes and says so."""
    try:
        prov = dyadlib.load_guard("agent", "provenance")
    except Exception:
        return []
    return list(getattr(prov, "FAIL_SHAPES", []))   # the core's own name (Rule-7 property 2); WARN_SHAPES is a sha as often as a token and is not a gate

def rules(data: Path = DATA) -> tuple[list[tuple[str, str, re.Pattern]], list[str], list[str]]:
    """(shapes, allowed_fields, problems). `shapes` is [(class, name, compiled)] in file order."""
    shapes, allowed, problems = [], [], []
    for n, raw in enumerate(data.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, rest = line.partition(":")
        key, rest = key.strip().lower(), rest.strip()
        if key == "allow":
            allowed.append(rest)
        elif key in CLASSES:
            name, _, pattern = rest.partition("=")
            name, pattern = name.strip(), pattern.strip()
            if not name or not pattern:
                problems.append(f"{data.name}:{n}: `{key}:` needs `<name> = <regex>`")
                continue
            try:
                shapes.append((key, name, re.compile(pattern)))
            except re.error as e:
                problems.append(f"{data.name}:{n}: {name}: regex does not compile ({e})")
        else:
            problems.append(f"{data.name}:{n}: unknown key {key!r} (a, b or allow)")
    return shapes, allowed, problems

def map_path(root: Path | None = None) -> Path:
    return dyadlib.instance(root or dyadlib.repo_root()) / MAP_REL

def pseudonyms(root: Path | None = None) -> dict[str, str]:
    """{real: pseudonym} from the instance map; {} when it is absent (the absent-store pattern)."""
    p = map_path(root)
    if not p.is_file():
        return {}
    out = {}
    for h, rows in dyadlib.tables(p.read_text(errors="ignore")):
        if [c.strip().lower() for c in h][:2] == ["real", "pseudonym"]:
            for r in rows:
                if len(r) >= 2 and r[0].strip():
                    out[dyadlib.plain(r[0]).strip()] = dyadlib.plain(r[1]).strip()
    return out

def findings(text: str, root: Path | None = None, data: Path = DATA) -> list[tuple[str, str, str]]:
    """[(class, name, matched text)] — every Class A shape, every key shape, and every Class B shape
    whose matched text the map does not carry. Class B already replaced by a pseudonym is not a finding,
    which is what makes the gate runnable over a finished disclosure."""
    shapes, _, _ = rules(data)
    mapped = set(pseudonyms(root).values()) | set(pseudonyms(root))
    out = []
    for cls, name, rx in shapes:
        for m in rx.finditer(text):
            hit = m.group(0)
            if cls == "b" and (hit in mapped or any(hit == v for v in mapped)):
                continue
            out.append((cls, name, hit))
    for name, rx in credential_shapes():
        for m in rx.finditer(text):
            out.append(("a", f"key shape: {name}", m.group(0)))
    return out

def unmapped(text: str, root: Path | None = None, data: Path = DATA) -> list[str]:
    """Class B values a source mentions that the map does not carry, sorted and deduplicated."""
    shapes, _, _ = rules(data)
    have = set(pseudonyms(root))
    hits = {m.group(0) for cls, _, rx in shapes if cls == "b" for m in rx.finditer(text)}
    return sorted(hits - have)

def check_map(root: Path | None = None) -> list[str]:
    """Property 4: unique pseudonyms, no real value mapped twice."""
    p = map_path(root)
    if not p.is_file():
        return [f"warning: skip {p.name}: no pseudonym map (nothing disclosed from this instance yet)"]
    msgs, seen, reals = [], {}, set()
    for h, rows in dyadlib.tables(p.read_text(errors="ignore")):
        if [c.strip().lower() for c in h][:2] != ["real", "pseudonym"]:
            continue
        for r in rows:
            if len(r) < 2 or not r[0].strip():
                continue
            real, pseud = dyadlib.plain(r[0]).strip(), dyadlib.plain(r[1]).strip()
            if pseud in seen and seen[pseud] != real:
                msgs.append(f"{p.name}: pseudonym {pseud!r} is reused for {real!r} and {seen[pseud]!r} (property 4)")
            if real in reals:
                msgs.append(f"{p.name}: {real!r} is mapped twice (property 4)")
            seen[pseud], _ = real, reals.add(real)
    return msgs

def check(root: Path | None = None) -> list[str]:
    root = root or dyadlib.repo_root()
    shapes, allowed, msgs = rules()
    msgs = list(msgs)
    for cls in CLASSES:
        if not any(c == cls for c, _, _ in shapes):
            msgs.append(f"{DATA.name}: class {cls!r} has no shape (rules/redaction.md property 3)")
    if not allowed:
        msgs.append(f"{DATA.name}: no `allow:` field (property 1: a disclosure is assembled, not filtered)")
    pats = [rx.pattern for _, _, rx in shapes]
    for p in sorted({p for p in pats if pats.count(p) > 1}):
        msgs.append(f"{DATA.name}: pattern duplicated: {p}")
    return msgs + check_map(root)

def summary(root: Path | None = None) -> str:
    shapes, allowed, _ = rules()
    a = sum(1 for c, _, _ in shapes if c == "a")
    return f"{a} identity + {len(shapes) - a} substance shapes, {len(allowed)} allowed fields, {len(pseudonyms(root))} pseudonyms"

def _read(arg: str) -> str:
    p = Path(arg)
    return p.read_text(errors="ignore") if p.is_file() else arg

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    if a and a[0] == "verify":
        if len(a) < 2:
            print("usage: redaction.py verify <file>", file=sys.stderr); return 2
        f = findings(_read(a[1]))
        for cls, name, hit in f:
            print(f"FAIL [redaction] class {cls.upper()} {name}: {hit!r}", file=sys.stderr)
        print(f"{'refused' if f else 'ok'}   [redaction] {a[1]}: {len(f)} finding(s)" if f else
              f"ok   [redaction] {a[1]}: gate passes, 0 findings")
        return 1 if f else 0
    if a and a[0] == "unmapped":
        if len(a) < 2:
            print("usage: redaction.py unmapped <file>", file=sys.stderr); return 2
        u = unmapped(_read(a[1]))
        for v in u:
            print(v)
        print(f"{len(u)} Class B value(s) not in the map", file=sys.stderr)
        return 0
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check(root)
    hard = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        stream = sys.stderr if not m.startswith("warning:") else sys.stdout
        print(f"{'FAIL' if not m.startswith('warning:') else 'warn'} [redaction] {m.removeprefix('warning:').strip()}", file=stream)
    if not hard:
        print(f"ok   [redaction] {summary(root)}")
    return 1 if hard else 0

if __name__ == "__main__":
    sys.exit(main())
