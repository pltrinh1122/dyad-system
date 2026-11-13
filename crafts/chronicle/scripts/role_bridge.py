#!/usr/bin/env python3
"""Role bridge (chronicle craft script; record `collateral-role-bridge`, `rules/collateral.md` §5). Kernel: Python
3.12+, stdlib only. Judges every occupation of a public taxonomy against each way of working with agents, and ranks
the occupations from greatest beneficiary to least, so a ranking over about a thousand occupations is code, never
inference (the core's Rule-13). The inference it rests on is made once, in `role_bridge_rules.txt` beside it.
Inputs, read from one directory of O*NET's CSV release: `occupation_data.csv`, `task_statements.csv`,
`task_ratings.csv` (importance, scale IM), `work_context.csv` (Consequence of Error, element 4.C.3.a.1, scale CX)
and, optional, a per-occupation exposure index `exposure.csv` (code, value 0–1).
  role_bridge.py rank <dir> [--version V] [--exposure-source S]   print the ranked table as Markdown
  role_bridge.py check                                          check the data file
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("role_bridge.py: Python 3.12+ required")
import csv
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/scripts/ -> dyad/scripts
import dyadlib

DATA = Path(__file__).with_name("role_bridge_rules.txt")
OUTCOMES = ("demanded", "emerging", "drifting", "net-cost", "absent", "unsourced")   # rank key 1, greatest beneficiary first
# judged in another order: net-cost is checked before emerging (judge), and ranks below it, since it loses attention
WAYS = ("intent-specification", "decision-framing", "evaluation", "oversight", "orchestration")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("outcomes-distinct", lambda: len(set(OUTCOMES)) == len(OUTCOMES)),
    ("demanded-first-unsourced-last", lambda: OUTCOMES[0] == "demanded" and OUTCOMES[-1] == "unsourced"),
    ("ways-distinct", lambda: len(set(WAYS)) == len(WAYS) == 5),
    ("data-beside-module", lambda: DATA.parent == Path(__file__).parent),
]
dyadlib.enforce(INVARIANTS, __name__)


def rules(data: Path = DATA) -> tuple[dict, list[str], dict, list[str]]:
    """(ways {id: [verb]}, objects, thresholds, problems)."""
    ways, objects, th, problems = {}, [], {}, []
    for n, raw in enumerate(data.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        if key in ("way", "threshold"):
            name, _, val = (p.strip() for p in rest.partition("="))
            if not name or not val:
                problems.append(f"line {n}: {key} needs `<name> = <value>`")
            elif key == "way":
                ways[name] = [v.strip() for v in val.split("|") if v.strip()]
            else:
                try:
                    th[name] = float(val)
                except ValueError:
                    problems.append(f"line {n}: threshold {name} is not a number")
        elif key == "object":
            objects += [v.strip() for v in rest.split("|") if v.strip()]
        else:
            problems.append(f"line {n}: unknown key {key!r}")
    if tuple(ways) != WAYS:
        problems.append(f"ways {tuple(ways)} differ from {WAYS}")
    if not objects:
        problems.append("no object line")
    if "handed-over" not in th:
        problems.append("no threshold handed-over")
    return ways, objects, th, problems


def _pattern(words: list[str]) -> re.Pattern:
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")", re.I)


def stated(task: str, verbs: re.Pattern, objects: re.Pattern) -> bool:
    """A task states a way's work: its verb, on an object of information work (B2)."""
    return bool(verbs.search(task)) and bool(objects.search(task))


def judge(tasks: list[tuple[str, float]], exposure: float | None, consequence: float | None,
          verbs: re.Pattern, objects: re.Pattern, handed: float) -> tuple[str, float]:
    """(outcome, benefit score) of one occupation for one way. tasks: [(statement, importance 1–5)];
    exposure 0–1 or None; consequence of error 1–5 or None. drifting needs two taxonomy versions, so it is
    never reached from one."""
    if not tasks:
        return "unsourced", 0.0
    e = exposure or 0.0
    c = ((consequence or 1.0) - 1.0) / 4.0           # 0 (none) – 1 (very serious)
    net = round(e * (1.0 - c), 4)                    # net attention: the gain left after checking (H)
    total = sum(w for _, w in tasks) or 1.0
    share = sum(w for t, w in tasks if stated(t, verbs, objects)) / total
    if share > 0:
        return "demanded", round(share * net, 4)
    if e >= handed and c > e:
        return "net-cost", net
    if e >= handed:
        return "emerging", net
    return "absent", net


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load(d: Path) -> tuple[dict, dict, dict, dict]:
    """(titles, tasks {code: [(stmt, importance)]}, consequence {code: v}, exposure {code: v})."""
    titles = {r["O*NET-SOC Code"]: r["Title"] for r in _read(d / "occupation_data.csv")}
    imp = {(r["O*NET-SOC Code"], r["Task ID"]): float(r["Data Value"])
           for r in _read(d / "task_ratings.csv") if r["Scale ID"] == "IM"}
    tasks: dict = {}
    for r in _read(d / "task_statements.csv"):
        k = (r["O*NET-SOC Code"], r["Task ID"])
        tasks.setdefault(k[0], []).append((r["Task"], imp.get(k, 3.0)))
    cons = {r["O*NET-SOC Code"]: float(r["Data Value"]) for r in _read(d / "work_context.csv")
            if r["Element ID"] == "4.C.3.a.1" and r["Scale ID"] == "CX"}
    exp = {}
    if (d / "exposure.csv").exists():
        exp = {r["code"]: float(r["value"]) for r in _read(d / "exposure.csv") if r.get("value")}
    return titles, tasks, cons, exp


def rank(titles: dict, tasks: dict, cons: dict, exp: dict, data: Path = DATA) -> list[dict]:
    """Every occupation, ranked: key 1 the best outcome over the ways, key 2 its score; ties share a rank."""
    ways, objects, th, problems = rules(data)
    if problems:
        raise ValueError("; ".join(problems))
    obj = _pattern(objects)
    pats = {w: _pattern(v) for w, v in ways.items()}
    rows = []
    for code, title in titles.items():
        per = {w: judge(tasks.get(code, []), exp.get(code), cons.get(code), p, obj, th["handed-over"])
               for w, p in pats.items()}
        best = min(per, key=lambda w: (OUTCOMES.index(per[w][0]), -per[w][1], WAYS.index(w)))
        rows.append({"code": code, "title": title, "per": per, "best": best,
                     "outcome": per[best][0], "score": per[best][1]})
    _ranks(rows, lambda r: (OUTCOMES.index(r["outcome"]), -r["score"]), "rank")
    for w in WAYS:
        _ranks(rows, lambda r, w=w: (OUTCOMES.index(r["per"][w][0]), -r["per"][w][1]), w)
    rows.sort(key=lambda r: (r["rank"], r["code"]))
    return rows


def _ranks(rows: list[dict], key, name: str) -> None:
    """Competition ranking (1, 2, 2, 4): a tie is shown, never broken by hand."""
    ordered = sorted(rows, key=key)
    prev, at = None, 0
    for i, r in enumerate(ordered, 1):
        k = key(r)
        if k != prev:
            prev, at = k, i
        r.setdefault("ranks", {})[name] = at
        if name == "rank":
            r["rank"] = at


def markdown(rows: list[dict], version: str, exposure_source: str) -> str:
    counts = {o: sum(r["outcome"] == o for r in rows) for o in OUTCOMES}
    per_way = {w: {o: sum(r["per"][w][0] == o for r in rows) for o in OUTCOMES} for w in WAYS}
    o = [f"Ranked by `crafts/chronicle/scripts/role_bridge.py` from O*NET {version} and the exposure index "
         f"{exposure_source}; never edited by hand. {len(rows)} occupations.", "",
         "| outcome | overall | " + " | ".join(WAYS) + " |", "|---|---|" + "---|" * len(WAYS)]
    o += [f"| `{x}` | {counts[x]} | " + " | ".join(str(per_way[w][x]) for w in WAYS) + " |" for x in OUTCOMES]
    o += ["", "| rank | occupation | code | outcome | best way | score | " + " | ".join(f"{w} rank" for w in WAYS) + " |",
          "|---|---|---|---|---|---|" + "---|" * len(WAYS)]
    for r in rows:
        o.append(f"| {r['rank']} | {r['title']} | {r['code']} | `{r['outcome']}` | {r['best'] if r['outcome'] != 'unsourced' else '—'} | {r['score']:.3f} | "
                 + " | ".join(str(r["ranks"][w]) for w in WAYS) + " |")
    return "\n".join(o) + "\n"


def main(argv: list[str]) -> int:
    if argv[:1] == ["check"]:
        *_, problems = rules()
        for p in problems:
            print(f"FAIL role_bridge_rules.txt {p}")
        print("ok   role_bridge_rules.txt" if not problems else "")
        return 1 if problems else 0
    if argv[:1] == ["rank"] and len(argv) >= 2:
        opts = dict(zip(argv[2::2], argv[3::2]))
        rows = rank(*load(Path(argv[1])))
        sys.stdout.write(markdown(rows, opts.get("--version", "(version not stated)"),
                                  opts.get("--exposure-source", "(none)")))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
