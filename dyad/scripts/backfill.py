#!/usr/bin/env python3
"""The structured backfill of the decision log (core script, read-only; d-work #644 plan step 5(a)). Kernel: Python 3.12+.
It reads the sources whose cells already hold a DMC record's own outcome name, so no inference labels a case, and prints
one candidate per case as a JSON line, the form a `--decisions` file may take (the decision log itself is
`decisions/<row>.md` blocks, `guards/agent/decision_log.py`): `{record, case, fields, inputs, outcome, row, source:
"structured"}`, the covering row the row whose ruling it was. The home lists them, beside the
two-reader prose cases, before the operator's precedent question; `dwork state <row> … -d 'Y precedent (…)' --decisions
<file>` then writes the listed ones `precedent`. It writes nothing and decides nothing.
Sources (`SOURCES`):
- the change log (`<host>/CHANGELOG.md`): each row's `class` cell, an outcome of `dmc:host-action-class`, and its
  `actor` cell, read as `dmc:party-kind` only where the cell is that record's own outcome name (`agent`; `operator` is
  none of its names, so it is counted as skipped, never mapped);
- the rows' `disposed` entries `Y archive (…)`, `Y open (promotion …)` and `Y release …`, as `dmc:retirement-candidate`,
  `dmc:promotion` and `dmc:release-class`, each only where the entry's text names one of the record's outcomes;
- verdict tables: a markdown table with a `result` column in a plan file (`<instance>/d-work/plans/<id>.md`, the plan's
  row covering it) or a falsification record (`<instance>/falsification/`, `dyad/falsification/`, the row the nearest
  heading above it names), whose result cell opens with an outcome name of `dmc:attack-result`.
A cell that names no outcome is counted, per source, in the summary on stderr, never guessed. `for_row` and `capture`
(#648) scope the sources to one row for its Done: `board draft`'s Candidates and the `Y done` refusal read them.
  backfill.py [--record <id>] [repo-root]      (JSON lines on stdout, the counts on stderr)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("backfill.py: Python 3.12+ required")
import json, re
from collections import Counter
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

ENTRY_RECORDS = {"archive": "retirement-candidate", "open": "promotion", "release": "release-class"}
ENTRY = re.compile(r"\d{4}-\d{2}-\d{2} Y (archive|open|release)\b(.*)$")
HEADING_ROW = re.compile(r"^#{1,6} .*?#(\d+)")
SOURCES = ("changelog", "entries", "verdicts")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("entry-records-are-three", lambda: set(ENTRY_RECORDS) == {"archive", "open", "release"}),
    ("entry-reads-the-kind", lambda: ENTRY.match("2026-11-08 Y open (promotion P2)").group(1) == "open"
                                     and ENTRY.match("2026-11-08 Y plan") is None),
    ("cells-split-on-unescaped-pipes", lambda: cells("| a | b \\| c | d |") == ["a", "b | c", "d"]),
    ("outcome-opens-the-cell", lambda: opens_with("survives, scoped", {"survives": "survives"}) == "survives"
                                       and opens_with("unconfirmed", {"confirmed": "confirmed"}) is None),
]


def cells(line: str) -> list[str]:
    """The cells of one markdown table line, `\\|` kept as a literal pipe."""
    body = line.strip().strip("|")
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def opens_with(text: str, names: dict[str, str]) -> str | None:
    """The outcome whose name or code `text` opens with, as a whole word (case-insensitive); None when none does."""
    t = re.sub(r"[*_`]", "", text).strip().lower()
    for name, code in sorted(names.items(), key=lambda kv: -len(kv[0])):
        if re.match(rf"{re.escape(name.lower())}(?![\w-])", t):
            return code
    return None


def names_in(text: str, names: dict[str, str]) -> list[str]:
    """The outcome codes whose name or code occurs in `text` as a whole word, each once, in record order."""
    t = text.lower()
    return list(dict.fromkeys(code for name, code in names.items() if re.search(rf"(?<![\w-]){re.escape(name.lower())}(?![\w-])", t)))


def outcomes(root: Path) -> dict[str, dict[str, str]]:
    """{record: {name or termCode, lowercase: termCode}} over every DMC store (the dmc guard's)."""
    dmc, out = dyadlib.load_guard("agent", "dmc"), {}
    for _, p, _ in dmc.records(Path(root)):
        try:
            doc = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        m = {}
        for o in doc.get("hasDefinedTerm") or []:
            if isinstance(o, dict) and o.get("termCode"):
                m[str(o["termCode"]).lower()] = o["termCode"]
                if o.get("name"):
                    m[str(o["name"]).lower()] = o["termCode"]
        out[p.stem] = m
    return out


def case_id(*parts) -> str:
    """A decision-log case id from its parts: `:`-joined, every other character a `-`, at most 80 characters."""
    s = ":".join(re.sub(r"[^A-Za-z0-9._#/-]+", "-", str(p)).strip("-") for p in parts)
    return s[:80].rstrip("-:")


def line(record, case, outcome, row, inputs="", fields=None) -> dict:
    return {"record": record, "case": case, "fields": dict(fields or {}), "inputs": inputs, "outcome": outcome,
            "row": row, "source": "structured"}


def from_changelog(root: Path, names: dict, skipped: Counter) -> list[dict]:
    p = Path(root) / dyadlib.host_path(root) / "CHANGELOG.md"
    if not p.is_file():
        return []
    out, head = [], None
    for n, raw in enumerate(p.read_text().splitlines(), 1):
        if not raw.startswith("|"):
            head = None; continue
        c = cells(raw)
        if head is None:
            head = [x.lower() for x in c]; continue
        if set("".join(c)) <= set("-: "):
            continue
        row = dict(zip(head, c))
        m = re.search(r"#(\d+)", row.get("d-work", ""))
        if not m:
            skipped["changelog: no d-work"] += 1; continue
        rid, action = int(m.group(1)), row.get("action", "")
        for col, record in (("class", "host-action-class"), ("actor", "party-kind")):
            code = (names.get(record) or {}).get(row.get(col, "").strip().lower())
            if code:
                out.append(line(record, case_id("changelog", n, col), code, rid, action))
            elif col in row:
                skipped[f"changelog {col}: {row[col].strip() or '(empty)'}"] += 1
    return out


def from_entries(root: Path, names: dict, skipped: Counter) -> list[dict]:
    out = []
    for r in dyadlib.read_rows(root):
        for k, e in enumerate(x.strip() for x in (r.disposed or "").split(";")):
            m = ENTRY.match(e)
            if not m:
                continue
            kind, text = m.groups()
            record = ENTRY_RECORDS[kind]
            if kind == "open" and not text.strip().startswith("(promotion"):
                continue
            found = names_in(text, names.get(record) or {})
            if len(found) == 1:
                out.append(line(record, case_id("entry", r.id, k), found[0], r.id, e))
            else:
                skipped[f"entries Y {kind}: {'no outcome named' if not found else 'several outcomes named'}"] += 1
    return out


def verdict_files(root: Path) -> list[tuple[Path, int | None]]:
    """(file, its covering row when the file gives one): every plan file and every falsification record."""
    inst = dyadlib.instance(root)
    out = [(p, int(p.stem)) for p in sorted((inst / "d-work" / "plans").glob("*.md")) if p.stem.isdigit()]
    for d in (inst / "falsification", dyadlib.PKG / "falsification"):
        out += [(p, None) for p in sorted(d.rglob("*.md"))] if d.is_dir() else []
    return out


def from_verdicts(root: Path, names: dict, skipped: Counter, rows: set[int],
                  files: list[tuple[Path, int | None]] | None = None) -> list[dict]:
    names = names.get("attack-result") or {}
    out = []
    for p, file_row in (verdict_files(root) if files is None else files):
        covering, head, t = file_row, None, 0
        for raw in p.read_text(errors="replace").splitlines():
            if file_row is None and (h := HEADING_ROW.match(raw)):
                covering = int(h.group(1))
            if not raw.startswith("|"):
                head = None; continue
            c = cells(raw)
            if head is None:
                head, t, k = [x.lower() for x in c], t + 1, 0
                continue
            if "result" not in head or set("".join(c)) <= set("-: "):
                continue
            k += 1
            row = dict(zip(head, c))
            code = opens_with(row.get("result", ""), names)
            if code is None:
                skipped["verdicts: result names no outcome"] += 1; continue
            if covering is None or covering not in rows:
                skipped["verdicts: no covering row"] += 1; continue
            key = next((row[x] for x in ("id", "#") if re.fullmatch(r"[A-Za-z0-9.]{1,12}", row.get(x, ""))), k)
            prose = " — ".join(row[x] for x in ("claim", "attack", "evidence") if row.get(x))
            stem = p.stem if file_row is None else f"plan-{file_row}"
            out.append(line("attack-result", case_id("verdict", stem[:40], t, key), code, covering, prose))
    return out


def backfill(root: Path, record: str | None = None) -> tuple[list[dict], Counter]:
    """(candidate lines, skipped counts) over every source, in source order; `record` keeps that record's alone."""
    root = Path(root)
    names, skipped = outcomes(root), Counter()
    rows = {r.id for r in dyadlib.read_rows(root)}
    got = from_changelog(root, names, skipped) + from_entries(root, names, skipped) + from_verdicts(root, names, skipped, rows)
    got = [g for g in got if g["row"] in rows]
    seen, out = set(), []
    for g in got:
        if (g["record"], g["case"]) not in seen and (record is None or g["record"] == record):
            seen.add((g["record"], g["case"])); out.append(g)
    return out, skipped


def for_row(root: Path, rid: int) -> list[dict]:
    """#648: the candidate rulings of row `rid` alone, from the sources this script reads — its plan file's verdict
    tables, its own `Y archive` / `Y open (promotion …)` / `Y release` entries and the change-log rows naming it — each
    renamed to the one case id form `<record>-<rid>-<n>` (n counting from 1 per record, in source order, so #645's one id
    per ruling holds), source `done`: the rulings its Done records."""
    root = Path(root)
    names, skipped = outcomes(root), Counter()
    rows = {r.id for r in dyadlib.read_rows(root)}
    plan = dyadlib.instance(root) / "d-work" / "plans" / f"{rid}.md"
    got = [g for g in from_changelog(root, names, skipped) + from_entries(root, names, skipped) if g["row"] == rid]
    got += from_verdicts(root, names, skipped, rows, [(plan, rid)] if plan.is_file() else [])
    n: Counter = Counter()
    out = []
    for g in got:
        n[g["record"]] += 1
        out.append({**g, "case": f"{g['record']}-{rid}-{n[g['record']]}", "source": "done"})
    return out


def capture(root: Path, rid: int) -> list[dict]:
    """The candidates of `for_row` that `dmc:precedent-admission` could admit (`precedent.gate`): what row `rid`'s
    `Y done` must record with `--decisions` (#648)."""
    pr = dyadlib.load_module(dyadlib.PKG / "scripts" / "precedent.py", "dyad_precedent")
    return pr.gate(Path(root), for_row(root, rid))[0]


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    record = None
    if "--record" in a:
        i = a.index("--record")
        if i + 1 >= len(a):
            print("refused: --record needs a record id", file=sys.stderr); return 1
        record = a[i + 1]; del a[i:i + 2]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    out, skipped = backfill(root, record)
    for g in out:
        print(json.dumps(g, ensure_ascii=False))
    for rec, n in sorted(Counter(g["record"] for g in out).items()):
        print(f"candidates: dmc:{rec} {n}", file=sys.stderr)
    for why, n in sorted(skipped.items()):
        print(f"skipped: {why}: {n}", file=sys.stderr)
    return 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
