#!/usr/bin/env python3
"""Decision-log guard (entity `decision`, agent corpus; Rule-3 owns the decision log as the record of the rulings a
`Y` covers, d-work #644, placed per Rule-11 property 1). Kernel: Python 3.12+.
The store is `<instance>/d-work/decisions/<row>.md`, the d-work store pattern (`crafts/sysarch/rules/stores.md`, plan
#644 revision 2: a tracked `*.jsonl` under d-work is a transcript to Rule-7 property 2): one block per ruling a
disposition of row `<row>` (the file's row, the row whose entry records it) names, under `## <case id>` (`## <case id>
precedent` for a precedent block), of `key: value` lines: `record` (a DMC record's identifier), `outcome` (one of its
`termCode`s), `row` (the covering row, where the case was ruled), `status` (`candidate` or `precedent`), `source`
(`done`, `structured` or `two-readers`), `date` (the UTC date of the write), `precedent-entry` (a precedent block's `Y
precedent (…)` entry of the file's row, verbatim), `precedent-set` (only on a ruling a precedent set gave: that set's
sha256, so `precedent-admission` refuses it as self-derived), one `field.<name>: <value>` line per structured input (a
string), and `inputs: <prose>` on one line. A `candidate` block of source `done` sits in the file of a row holding a
`Y done`. Parsed, a block is a dict (`record`, `case`, `fields`, `inputs`, `outcome`, `row`, `status`, `source`, `date`,
`y`, `precedent`).
Append-only: a block is never edited or removed; a case's status moves by a later block (`candidate` → `precedent`),
so a file only grows, and the latest block of a (record, case) is its state (`latest`). Written by `dwork state …
--decisions <file>` in the commit that records the `Y` (`lines_for`, every refusal before a write; <file> holds blocks
of this form, or one JSON object per line); read by `similar.admit`.
An absent store passes (no ruling logged yet, a fresh install).
  decision_log.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("decision_log.py: Python 3.12+ required")
import datetime, json, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "decision", "agent", True
NAME, OWNER = "decision log", "Rule-3"
STORE_REL = "d-work/decisions"
FIELDS = ("record", "case", "fields", "inputs", "outcome", "row", "status", "source", "date", "y", "precedent")
REQUIRED = FIELDS[:9]
STATUSES = ("candidate", "precedent")
SOURCES = ("done", "structured", "two-readers")
PRECEDENT_Y = re.compile(r"\d{4}-\d{2}-\d{2} Y precedent \([^;]*\)")   # `<date> Y precedent (<n> cases: <record>×<k>, …)`
DONE_Y = re.compile(r"\d{4}-\d{2}-\d{2} Y done\b")
FILE = re.compile(r"(\d+)\.md")
HEADING = re.compile(r"## (\S+)( precedent)?")
KEYS = {"precedent-entry": "y", "precedent-set": "precedent"}   # stored key -> parsed key; the rest keep their names
ORDER = ("record", "outcome", "row", "status", "source", "date", "precedent-entry", "precedent-set")
CASE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:#/-]{0,79}")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("required-fields-lead", lambda: FIELDS[:len(REQUIRED)] == REQUIRED and set(FIELDS) - set(REQUIRED) == {"y", "precedent"}),
    ("precedent-y-reads-the-entry", lambda: bool(PRECEDENT_Y.fullmatch("2026-11-08 Y precedent (5 cases: attack-result×5)"))
                                            and not PRECEDENT_Y.fullmatch("2026-11-08 Y plan (precedent)")),
    ("statuses-are-two", lambda: STATUSES == ("candidate", "precedent")),
]


def store(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / STORE_REL


def files(root: Path) -> list[Path]:
    d = store(root)
    return sorted(d.glob("*.md"), key=lambda p: (int(p.stem) if p.stem.isdigit() else 0, p.name)) if d.is_dir() else []


def parse(text: str) -> list[dict]:
    """The blocks of one file, each a dict; JSON lines are read too (a `--decisions` input file). A line outside a
    block, a line that is no `key: value` or a heading whose ` precedent` disagrees with its `status` raises ValueError
    naming its number."""
    if text.lstrip().startswith("{"):
        out = []
        for n, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"line {n} is not JSON ({e.msg})")
            if not isinstance(obj, dict):
                raise ValueError(f"line {n} is not a JSON object")
            out.append(obj)
        return out
    out, cur, heads = [], None, []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("## "):
            m = HEADING.fullmatch(line.rstrip())
            if not m:
                raise ValueError(f"line {n}: a block opens `## <case id>` or `## <case id> precedent`")
            cur = {"case": m.group(1), "fields": {}}; out.append(cur); heads.append((n, bool(m.group(2))))
            continue
        k, sep, v = line.partition(":")
        if cur is None or not sep or not k.strip() or k != k.strip():
            raise ValueError(f"line {n} is no `key: value` line of a block")
        k, v = k.strip(), v.strip()
        if k.startswith("field."):
            cur["fields"][k[6:]] = v
        else:
            cur[KEYS.get(k, k)] = int(v) if k == "row" and v.isdigit() else v
    for (n, prec), b in zip(heads, out):
        b.setdefault("inputs", "")
        if prec != (b.get("status") == "precedent"):
            raise ValueError(f"line {n}: the heading says {'precedent' if prec else 'candidate'}, the block's status {b.get('status')!r}")
    return out


def render(ln: dict) -> str:
    """One block, as `append` writes it; a value is one line (a line break becomes a space)."""
    one = lambda v: " ".join(str(v).split())
    out = [f"## {ln['case']}" + (" precedent" if ln.get("status") == "precedent" else "")]
    out += [f"{k}: {one(ln[KEYS.get(k, k)])}" for k in ORDER if KEYS.get(k, k) in ln]
    out += [f"{k}: {one(v)}" for k, v in ln.items() if k not in {KEYS.get(o, o) for o in ORDER} | {"case", "fields", "inputs"}]
    out += [f"field.{k}: {one(v)}" for k, v in (ln.get("fields") or {}).items()]
    out.append(f"inputs: {one(ln.get('inputs', ''))}")
    return "\n".join(out) + "\n"


def read(root: Path) -> dict[int, list[dict]]:
    """{file row: [line…]} over the store; an unreadable file is left out (the guard reports it)."""
    out = {}
    for p in files(root):
        m = FILE.fullmatch(p.name)
        try:
            out[int(m.group(1))] = parse(p.read_text()) if m else []
        except ValueError:
            continue
    return out


def latest(lines) -> dict[tuple[str, str], dict]:
    """{(record, case): the latest line naming it}: the case's state, as the append-only order gives it."""
    out = {}
    for ln in lines:
        out[(ln.get("record"), ln.get("case"))] = ln
    return out


def outcomes_by_record(root: Path) -> dict[str, set[str]]:
    """{record identifier: its termCodes} over every DMC store (the dmc guard's)."""
    dmc, out = dyadlib.load_guard("agent", "dmc"), {}
    for _, p, _ in dmc.records(Path(root)):
        try:
            doc = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        out[p.stem] = {o.get("termCode") for o in doc.get("hasDefinedTerm") or [] if isinstance(o, dict)}
    return out


def line_problems(ln: dict, file_row: int, disposed: str | None, rows: set[int], codes: dict[str, set[str]]) -> list[str]:
    """What is wrong with one block of `<file_row>.md`, given that row's `disposed` (None: no such row)."""
    bad = []
    keys = set(ln)
    if missing := [k for k in REQUIRED if k not in keys]:
        bad.append(f"lacks {', '.join(missing)}")
    if extra := sorted(keys - set(FIELDS)):
        bad.append(f"carries unknown key(s) {', '.join(extra)}")
    rec, case, outcome = ln.get("record"), ln.get("case"), ln.get("outcome")
    if isinstance(rec, str) and rec not in codes:
        bad.append(f"names no DMC record {rec!r}")
    elif isinstance(rec, str) and outcome not in codes[rec]:
        bad.append(f"outcome {outcome!r} is no outcome of dmc:{rec} ({', '.join(sorted(c for c in codes[rec] if c))})")
    if "case" in keys and not (isinstance(case, str) and CASE.fullmatch(case)):
        bad.append(f"case {case!r} is not a case id")
    if "fields" in keys and not isinstance(ln.get("fields"), dict):
        bad.append("fields is not an object")
    elif "fields" in keys and (odd := [k for k, v in ln["fields"].items()
                                       if not (re.fullmatch(r"[A-Za-z0-9_.-]+", str(k)) and isinstance(v, str))]):
        bad.append(f"field(s) {', '.join(map(str, odd))}: a field is `field.<name>: <value>`, its value a string")
    if "inputs" in keys and not isinstance(ln.get("inputs"), str):
        bad.append("inputs is not a string")
    if "row" in keys and not (isinstance(ln.get("row"), int) and ln["row"] in rows):
        bad.append(f"row {ln.get('row')!r} is no row")
    if "status" in keys and ln.get("status") not in STATUSES:
        bad.append(f"status {ln.get('status')!r} is not one of {', '.join(STATUSES)}")
    if "source" in keys and ln.get("source") not in SOURCES:
        bad.append(f"source {ln.get('source')!r} is not one of {', '.join(SOURCES)}")
    if "date" in keys:
        try:
            datetime.date.fromisoformat(str(ln.get("date")))
        except ValueError:
            bad.append(f"date {ln.get('date')!r} is not YYYY-MM-DD")
    if "precedent" in keys and not (isinstance(ln["precedent"], str) and re.fullmatch(r"[0-9a-f]{64}", ln["precedent"])):
        bad.append("precedent is not a set's sha256")
    entries = [e.strip() for e in (disposed or "").split(";")]
    if ln.get("status") == "precedent":
        y = ln.get("y")
        if not (isinstance(y, str) and PRECEDENT_Y.fullmatch(y)):
            bad.append("a precedent line names no `Y precedent (…)` entry in `y`")
        elif y not in entries:
            bad.append(f"its `Y precedent` entry {y!r} is not on row #{file_row}")
    elif "y" in keys:
        bad.append("a candidate line carries `y`; only a precedent line names its `Y precedent`")
    if ln.get("status") == "candidate" and ln.get("source") == "done" and not any(DONE_Y.match(e) for e in entries):
        bad.append(f"a candidate of source done sits in #{file_row}'s file, which holds no `Y done`")
    return bad


def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = Path(root or dyadlib.repo_root())
    d = store(root)
    if not d.is_dir():
        return []
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    codes, msgs = outcomes_by_record(root), []
    for p in sorted(d.iterdir()):
        m = FILE.fullmatch(p.name)
        if not m:
            msgs.append(f"{p.name}: not `<row>.md`; the decision log holds one file per row (#644)"); continue
        fr = int(m.group(1))
        if fr not in rows:
            msgs.append(f"{p.name}: names no row"); continue
        try:
            lines = parse(p.read_text())
        except ValueError as e:
            msgs.append(f"{p.name}: {e}"); continue
        for n, ln in enumerate(lines, 1):
            msgs += [f"{p.name} block {n}: {b}" for b in line_problems(ln, fr, rows[fr].disposed, set(rows), codes)]
    return msgs


def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """Append-only: no non-merge commit of `base..head` deletes a decision-log file or changes a line already in it."""
    inst = dyadlib.instance_rel(root)
    commits = dyadlib.range_commits(root, base, head)
    if not inst or not commits:
        return []
    prefix, msgs = f"{inst}/{STORE_REL}/", []
    show = lambda rev, path: subprocess.run(["git", "show", f"{rev}:{path}"], cwd=root, capture_output=True, text=True,
                                            env=dyadlib.git_env(), timeout=120)
    for c in commits:
        r = subprocess.run(["git", "diff-tree", "--root", "--no-commit-id", "-r", "--no-renames", "--name-status", c],
                           cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
        for line in r.stdout.splitlines():
            status, _, path = line.partition("\t")
            if not path.startswith(prefix) or status == "A":
                continue
            if status == "D":
                msgs.append(f"{c[:12]}: {path} is deleted; the decision log is append-only (#644)"); continue
            old, new = show(f"{c}^", path).stdout, show(c, path).stdout
            if not new.startswith(old):
                msgs.append(f"{c[:12]}: {path} changes a line already logged; the decision log is append-only, a "
                            f"case's status moves by a later line (#644)")
    return msgs


def lines_for(root: Path, file_row: int, entry: str, given: list[dict], today: str,
              rows: dict | None = None) -> list[dict]:
    """The lines `dwork state <file_row> … -d <entry> --decisions <file>` appends, every refusal raised as ValueError
    before any write. Under a `Y done` entry each given line is a `candidate` (source `done` unless given); under a
    `Y precedent (…)` entry each becomes a `precedent` line naming that entry, from the candidate already logged for its
    (record, case) when there is one, so the precedent-Y admits exactly the listed lines. Any other entry is refused."""
    root = Path(root)
    rows = rows if rows is not None else {r.id: r for r in dyadlib.read_rows(root)}
    if file_row not in rows:
        raise ValueError(f"no row {file_row}")
    stamped = f"{today} {entry}"
    precedent = bool(PRECEDENT_Y.fullmatch(stamped))
    if not precedent and not DONE_Y.match(stamped):
        raise ValueError("--decisions rides a `Y done` (its rulings logged as candidates) or a `Y precedent (…)` "
                         "(the listed lines admitted as precedents), and no other entry (#644)")
    if not given:
        raise ValueError("--decisions names no line")
    logged = latest(read(root).get(file_row, []))
    disposed = (rows[file_row].disposed + "; " if rows[file_row].disposed else "") + stamped
    codes, out = outcomes_by_record(root), []
    for n, g in enumerate(given, 1):
        if not isinstance(g, dict):
            raise ValueError(f"--decisions block {n} is not a block")
        base = dict(logged.get((g.get("record"), g.get("case")), {})) if precedent else {}
        ln = {**base, **{k: v for k, v in g.items() if k not in ("status", "y", "date")}}
        if isinstance(ln.get("fields"), dict):   # stored as `field.<name>: <value>` lines: a value is a string
            ln["fields"] = {k: v if isinstance(v, str) else json.dumps(v) for k, v in ln["fields"].items()}
        if isinstance(ln.get("inputs"), str):
            ln["inputs"] = " ".join(ln["inputs"].split())   # one line, as the block holds it
        ln.setdefault("source", "done")
        ln.update(status="precedent" if precedent else "candidate", date=today)
        if precedent:
            ln["y"] = stamped
        else:
            ln.pop("y", None)
        ln = {k: ln[k] for k in FIELDS if k in ln}
        bad = line_problems(ln, file_row, disposed, set(rows), codes)
        if bad:
            raise ValueError(f"--decisions block {n} ({g.get('record')}/{g.get('case')}): {'; '.join(bad)}")
        out.append(ln)
    seen = [(ln["record"], ln["case"]) for ln in out]
    if dup := sorted({k for k in seen if seen.count(k) > 1}):
        raise ValueError(f"--decisions names {dup[0][0]}/{dup[0][1]} twice")
    return out


def append(root: Path, file_row: int, lines: list[dict]) -> Path:
    p = store(root) / f"{file_row}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(render(ln) for ln in lines)
    with p.open("a", encoding="utf-8") as f:
        f.write(("\n" if p.stat().st_size else "") + text)   # one blank line between blocks
    return p


def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    got = read(root or dyadlib.repo_root())
    n = sum(len(v) for v in got.values())
    p = sum(1 for v in got.values() for ln in latest(v).values() if ln.get("status") == "precedent")
    return f"{n} decision block(s) in {len(got)} file(s), {p} case(s) precedent"


def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    d = store(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    return {"store": f"{rel}/<row>.md",
            "parser": "`decision_log.parse` (`## <case id>` blocks of `key: value` lines)",
            "observed": sum(len(v) for v in read(root).values()),
            "note": "one block per ruling a disposition names, append-only; a case's status moves by a later block (#644)",
            "fields": [(f, "json", "", f in REQUIRED, "", "decision_log.FIELDS") for f in FIELDS]}


def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"FAIL [rule-3] {m}", file=sys.stderr)
    if not msgs:
        print(f"ok   [rule-3] {summary(root)}")
    return 1 if msgs else 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1)

if __name__ == "__main__":
    sys.exit(main())
