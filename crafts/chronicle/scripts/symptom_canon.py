#!/usr/bin/env python3
"""Symptom canon (chronicle craft script; record `collateral-symptom-canon`, `rules/collateral.md` §5). Kernel: Python
3.12+, stdlib only. The canon grows from observation: the operator's own, then interviews and readers' feedback through
the channels. Each entry's wording and each candidate's outcome are judged by inference, once, and stored in the canon;
this script checks what is mechanical (the core's Rule-13: a recurring check is code):
- every top-level symptom of every tree in the canvas set is an entry's source, a candidate or an exclusion;
- every tree source names a node that exists, and every entry carries at least one observation;
- every `served` or `partly` entry cites a path that exists.
Trees: `<canvas set>/<segment>/why-tree.md` (named by the segment) and `<canvas set>/reference/<name>.md` (named by the
file). Canon: `<canvas set>/symptoms.md`: entries `## S<n> <wording>` with `key: value` lines; then `## candidates` and
`## excluded`, each of lines `- <tree>:<id> <outcome>: <reason>`.
Sources: `observed:<row>#<entry>` (the operator's words, by provenance entry), `interview:<ref>`, `channel:<ref>`
(a reader's report, by a reference that names no one), and `<tree>:<id>` (a root, not an observation).
  symptom_canon.py check <canvas set> [<repo root>]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("symptom_canon.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/scripts/ -> dyad/scripts
import dyadlib

OBSERVATIONS = ("observed", "interview", "channel")            # source kinds that are an observation
CANDIDATE = ("unobserved",)                                    # waits under ## candidates until observed
EXCLUDED = ("cause", "unrooted", "unsourced", "restated")      # kept out of the canon, under ## excluded
SERVED = ("served", "partly", "not yet")
FIELDS = ("class", "proficiency", "way", "when", "served", "cite", "sources", "supersedes")
REQUIRED = ("class", "proficiency", "served", "sources")
ENTRY = re.compile(r"^## (S\d+) (.+)$")
LISTED = re.compile(r"^- (\S+:[A-Z][\w.]*) (\S+): (.+)$")
OBSERVED = re.compile(r"^observed:#?\d+#\d+$")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("outcomes-disjoint", lambda: not set(CANDIDATE) & set(EXCLUDED)),
    ("observation-kinds-distinct", lambda: len(set(OBSERVATIONS)) == 3),
    ("served-values-distinct", lambda: len(set(SERVED)) == 3),
    ("required-are-fields", lambda: set(REQUIRED) <= set(FIELDS)),
]
dyadlib.enforce(INVARIANTS, __name__)


def trees(canvas: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """({tree: node ids}, {tree: top-level symptom ids})."""
    nodes, tops = {}, {}
    files = [(p.parent.name, p) for p in sorted(canvas.glob("*/why-tree.md"))]
    files += [(p.stem, p) for p in sorted((canvas / "reference").glob("*.md"))]
    for name, p in files:
        ids, top = set(), set()
        for line in p.read_text().splitlines():
            m = re.match(r"^(\s*)([A-Z][\w.]*) \[(\w[\w-]*)", line)
            if m:
                ids.add(m.group(2))
                if not m.group(1) and m.group(3) == "symptom":
                    top.add(m.group(2))
        nodes[name], tops[name] = ids, top
    return nodes, tops


def parse(text: str) -> tuple[list[dict], dict[str, list[tuple[str, str, str, int]]], list[str]]:
    """(entries, {"candidates"|"excluded": [(source, outcome, reason, line)]}, problems)."""
    entries, listed, problems = [], {"candidates": [], "excluded": []}, []
    cur, section = None, None
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip() in ("## candidates", "## excluded"):
            section, cur = line.strip()[3:], None
            continue
        m = ENTRY.match(line)
        if m:
            section, cur = None, {"id": m.group(1), "wording": m.group(2)}
            entries.append(cur)
            continue
        if section and line.startswith("- "):
            e = LISTED.match(line)
            allowed = CANDIDATE if section == "candidates" else EXCLUDED
            if not e:
                problems.append(f"line {n}: a {section} line reads `- <tree>:<id> <outcome>: <reason>`")
            elif e.group(2) not in allowed:
                problems.append(f"line {n}: {section} outcome {e.group(2)!r} is none of {allowed}")
            else:
                listed[section].append((*e.groups(), n))
            continue
        if cur is not None and ":" in line and not line.startswith(("#", "-", " ", ">")):
            k, _, v = line.partition(":")
            k = k.strip()
            if k in FIELDS:
                cur[k] = v.strip()
            elif k:
                problems.append(f"line {n}: {cur['id']} unknown field {k!r}")
    return entries, listed, problems


def check(canvas: Path, root: Path) -> list[str]:
    canon = canvas / "symptoms.md"
    if not canon.exists():
        return [f"{canon}: no canon"]
    entries, listed, problems = parse(canon.read_text())
    nodes, tops = trees(canvas)
    seen, covered = set(), set()
    superseded = {e["supersedes"] for e in entries if e.get("supersedes")}
    for e in entries:
        i = e["id"]
        if i in seen:
            problems.append(f"{i}: id used twice")
        seen.add(i)
        for k in REQUIRED:
            if not e.get(k):
                problems.append(f"{i}: no {k}")
        if e.get("served") and e["served"] not in SERVED:
            problems.append(f"{i}: served {e['served']!r} is none of {SERVED}")
        if e.get("served") in ("served", "partly"):
            cite = [c.strip().strip("`") for c in e.get("cite", "").split(",") if c.strip()]
            if not cite:
                problems.append(f"{i}: {e['served']} cites nothing (R2)")
            problems += [f"{i}: cite {c} does not exist" for c in cite if not (root / c).exists()]
        sources = [s.strip() for s in e.get("sources", "").split(",") if s.strip()]
        observed = False
        for s in sources:
            kind, _, rest = s.partition(":")
            if kind in OBSERVATIONS:
                observed = True
                if kind == "observed" and not OBSERVED.match(s):
                    problems.append(f"{i}: source {s} reads `observed:<row>#<entry>`")
                elif not rest:
                    problems.append(f"{i}: source {s} names no reference")
            elif rest not in nodes.get(kind, set()):
                problems.append(f"{i}: source {s} names no tree node")
            elif i not in superseded:
                covered.add(s)
        if e.get("sources") and not observed:
            problems.append(f"{i}: no observation among its sources (observed, interview or channel)")
    for section, rows in listed.items():
        for s, _, _, n in rows:
            name, _, node = s.partition(":")
            if node not in nodes.get(name, set()):
                problems.append(f"line {n}: {section} {s} names no tree node")
            covered.add(s)
    for name, top in tops.items():
        problems += [f"{name}:{t} is a tree symptom no entry, candidate or exclusion holds"
                     for t in sorted(top) if f"{name}:{t}" not in covered]
    return problems


def main(argv: list[str]) -> int:
    if argv[:1] == ["check"] and len(argv) >= 2:
        root = Path(argv[2]) if len(argv) > 2 else Path.cwd()
        problems = check(Path(argv[1]), root)
        for p in problems:
            print(f"FAIL symptom-canon {p}")
        if not problems:
            print(f"ok   symptom-canon {argv[1]}")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
