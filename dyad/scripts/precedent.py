#!/usr/bin/env python3
"""The blind two-reader labelling of precedent cases (core script, read-only; d-work #645, the bootstrap play-book
`dyad/playbooks/precedent-bootstrap.md` runs it; #644 did it by hand). Kernel: Python 3.12+, stdlib.
A cases file holds one JSON object per line, `{case, record, row, facts, label}`: a case id, the DMC record it applies,
its covering row, its facts as prose, and the outcome the source recorded (the label the readers never see).
  dyad precedent prompt <cases-file> [--out <file>]
      the blind prompt: per record (sorted by identifier) its question, inputs, outcomes with their when and then,
      precedence and default, then each case (sorted by id) with its id and facts, never its label; the same inputs give
      the same bytes. Refused, before anything is written, when a case lacks a key, names no record, names an outcome
      that is not its record's, or names a record not judged by inference or operator-side (`dmc:precedent-admission`:
      a precedent settles agent-side calls only).
  dyad precedent score <cases-file> <answers-a> <answers-b> [--kept <file>]
      each reader's answers (`<case id>: <outcome>` lines, or JSON lines `{case, label}`) against the labels: per record
      the count and each reader's score, the kept cases (both readers match the label) and each mismatch, classed
      `model-limit` (one reader missed) or `context-gap` (both missed). With --kept, the kept cases are written as a
      `dwork state … --decisions` file (JSON lines, source `two-readers`).
It decides nothing: the kept cases go before the operator's precedent question, and only its `Y` admits them.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("precedent.py: Python 3.12+ required")
import json, re
from collections import defaultdict
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

KEYS = ("case", "record", "row", "facts", "label")
ANSWER = re.compile(r"^\s*(?:[-*]\s*)?`?([A-Za-z0-9][A-Za-z0-9._:#/-]*)`?\s*[:=]\s*`?([A-Za-z0-9][A-Za-z0-9-]*)`?\s*$")
MISMATCH = ("model-limit", "context-gap")
USAGE = "usage: dyad precedent prompt <cases-file> [--out <file>] | score <cases-file> <answers-a> <answers-b> [--kept <file>]"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("answer-reads-a-case-line", lambda: ANSWER.match("- `plan-departure-619-1`: new-plan").groups() == ("plan-departure-619-1", "new-plan")
                                         and ANSWER.match("619-1 is new-plan") is None),
    ("mismatch-classes-are-two", lambda: MISMATCH == ("model-limit", "context-gap")),
    ("a-label-is-never-in-the-prompt", lambda: "SECRET-LABEL" not in render(
        {"r": {"identifier": "r", "name": "R", "dyad:decides": "q?", "dyad:inputs": ["x"],
               "hasDefinedTerm": [{"termCode": "a", "name": "a", "dyad:when": "w", "dyad:then": "t"}]}},
        [{"case": "c1", "record": "r", "row": 1, "facts": "f", "label": "SECRET-LABEL"}])),
]


def read_cases(path: Path) -> list[dict]:
    out = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"{path} line {n} is not JSON ({e.msg})")
        if not isinstance(obj, dict):
            raise ValueError(f"{path} line {n} is not a JSON object")
        out.append(obj)
    return out


def records(root: Path) -> dict[str, dict]:
    """{identifier: record} over every DMC store (the dmc guard's)."""
    out = {}
    for _, p, _ in dyadlib.load_guard("agent", "dmc").records(Path(root)):
        try:
            out[p.stem] = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
    return out


def codes(doc: dict) -> list[str]:
    return [o["termCode"] for o in doc.get("hasDefinedTerm") or [] if isinstance(o, dict) and o.get("termCode")]


def problems(cases: list[dict], recs: dict[str, dict]) -> list[str]:
    """Every reason the cases cannot be labelled blind, one line each; [] when they can."""
    similar = dyadlib.load_module(dyadlib.PKG / "scripts" / "similar.py", "similar")
    bad, seen = [], set()
    for n, c in enumerate(cases, 1):
        who = c.get("case", f"line {n}")
        if missing := [k for k in KEYS if k not in c]:
            bad.append(f"{who}: lacks {', '.join(missing)}"); continue
        if (c["record"], c["case"]) in seen:
            bad.append(f"{who}: named twice for dmc:{c['record']}")
        seen.add((c["record"], c["case"]))
        doc = recs.get(c["record"])
        if doc is None:
            bad.append(f"{who}: names no DMC record {c['record']!r}"); continue
        kind = (doc.get("dyad:judgedBy") or {}).get("dyad:kind")
        if kind != "inference":
            bad.append(f"{who}: dmc:{c['record']} is judged {kind}, not by inference: nothing to label")
        elif similar.operator_side(doc):
            bad.append(f"{who}: dmc:{c['record']} is operator-side (dmc:precedent-admission): a precedent settles agent-side calls only")
        if c["label"] not in codes(doc):
            bad.append(f"{who}: label {c['label']!r} is no outcome of dmc:{c['record']}")
        if not ANSWER.match(f"{c['case']}: x"):
            bad.append(f"{who}: the case id is not one word an answer line can name")
    return bad


def render(recs: dict[str, dict], cases: list[dict]) -> str:
    """The prompt text: deterministic, every label left out."""
    by = defaultdict(list)
    for c in cases:
        by[c["record"]].append(c)
    out = [f"# Blind labelling: {len(cases)} case(s) of {len(by)} record(s)", "",
           "For each case below, choose exactly one outcome code of its record, judging only from the record and the",
           "case's facts. Answer with one line per case, `<case id>: <outcome code>`, and nothing else.", ""]
    for rid in sorted(by):
        d = recs[rid]
        out += [f"## Record {rid}: {d.get('name', rid)}", f"Question: {d.get('dyad:decides', '')}",
                "Inputs: " + "; ".join(d.get("dyad:inputs") or []), "Outcomes:"]
        out += [f"- `{o['termCode']}` ({o.get('name', o['termCode'])}): when {o.get('dyad:when', '')}; then {o.get('dyad:then', '')}"
                for o in d.get("hasDefinedTerm") or [] if isinstance(o, dict) and o.get("termCode")]
        if d.get("dyad:precedence"):
            out.append(f"Precedence: {d['dyad:precedence']}")
        if d.get("dyad:default"):
            out.append(f"Default: {d['dyad:default']}")
        out.append("")
        for c in sorted(by[rid], key=lambda c: str(c["case"])):
            out += [f"### Case {c['case']}", " ".join(str(c["facts"]).split()), ""]
    return "\n".join(out).rstrip("\n") + "\n"


def prompt(root: Path, cases: list[dict]) -> str:
    recs = records(root)
    if bad := problems(cases, recs):
        raise ValueError("; ".join(bad))
    return render(recs, cases)


def read_answers(text: str) -> dict[str, str]:
    """{case id: outcome} from a reader's answer: `<case id>: <outcome>` lines (a list marker or backticks allowed), or
    JSON lines `{case, label}`; any other line is ignored, and a case answered twice keeps its first answer."""
    out = {}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("{"):
            try:
                obj = json.loads(s)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("case"), str) and isinstance(obj.get("label"), str):
                out.setdefault(obj["case"], obj["label"])
            continue
        if m := ANSWER.match(s):
            out.setdefault(m.group(1), m.group(2))
    return out


def score(cases: list[dict], a: dict[str, str], b: dict[str, str]) -> tuple[dict, list[dict], list[tuple]]:
    """({record: (n, a right, b right, kept)}, kept cases, [(case, record, label, a, b, class)])."""
    per, kept, miss = {}, [], []
    for c in sorted(cases, key=lambda c: (c["record"], str(c["case"]))):
        n, ra, rb, k = per.get(c["record"], (0, 0, 0, 0))
        ga, gb = a.get(c["case"]), b.get(c["case"])
        oka, okb = ga == c["label"], gb == c["label"]
        per[c["record"]] = (n + 1, ra + oka, rb + okb, k + (oka and okb))
        if oka and okb:
            kept.append(c)
        else:
            miss.append((c["case"], c["record"], c["label"], ga, gb, MISMATCH[0] if (oka or okb) else MISMATCH[1]))
    return per, kept, miss


def decisions_lines(kept: list[dict]) -> list[dict]:
    """The kept cases as `--decisions` input: candidates the precedent question may admit, source `two-readers`."""
    return [{"record": c["record"], "case": c["case"], "fields": dict(c.get("fields") or {}),
             "inputs": " ".join(str(c["facts"]).split()), "outcome": c["label"], "row": c["row"], "source": "two-readers"}
            for c in kept]


def report(per: dict, miss: list[tuple]) -> list[str]:
    out = [f"record {r}: n {n}; reader a {ra}/{n}; reader b {rb}/{n}; kept {k}" for r, (n, ra, rb, k) in sorted(per.items())]
    out += [f"mismatch {case} (dmc:{rec}): label {lab}, a {ga or '-'}, b {gb or '-'}: {cls}" for case, rec, lab, ga, gb, cls in miss]
    tot = [sum(v[i] for v in per.values()) for i in range(4)]
    out.append(f"total: n {tot[0]}; reader a {tot[1]}/{tot[0]}; reader b {tot[2]}/{tot[0]}; kept {tot[3]}; "
               f"model-limit {sum(m[5] == MISMATCH[0] for m in miss)}; context-gap {sum(m[5] == MISMATCH[1] for m in miss)}")
    return out


def _flag(a: list[str], flag: str) -> str | None:
    if flag not in a:
        return None
    i = a.index(flag)
    if i + 1 >= len(a):
        raise ValueError(f"{flag} needs a value")
    v = a[i + 1]; del a[i:i + 2]
    return v


def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    root = Path(root or dyadlib.repo_root())
    try:
        if a[:1] == ["prompt"]:
            out = _flag(a, "--out")
            if len(a) != 2:
                raise ValueError(USAGE)
            text = prompt(root, read_cases(Path(a[1])))
            if out:
                Path(out).write_text(text, encoding="utf-8")
                print(f"prompt: {out}, {len(text.encode())} bytes")
            else:
                sys.stdout.write(text)
            return 0
        if a[:1] == ["score"]:
            kept_out = _flag(a, "--kept")
            if len(a) != 4:
                raise ValueError(USAGE)
            cases = read_cases(Path(a[1]))
            if bad := problems(cases, records(root)):
                raise ValueError("; ".join(bad))
            per, kept, miss = score(cases, read_answers(Path(a[2]).read_text(encoding="utf-8")),
                                    read_answers(Path(a[3]).read_text(encoding="utf-8")))
            print("\n".join(report(per, miss)))
            if kept_out:
                Path(kept_out).write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in decisions_lines(kept)),
                                          encoding="utf-8")
                print(f"kept: {kept_out}, {len(kept)} case(s) as --decisions input")
            return 0
        raise ValueError(USAGE)
    except (OSError, ValueError) as e:
        print(f"refused: {e}", file=sys.stderr); return 1


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
