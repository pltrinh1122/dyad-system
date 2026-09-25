#!/usr/bin/env python3
"""Incident log parser (core script; Rule-3 owns the log's form). Kernel: Python 3.12+.
The incident log `<instance>/audits/INCIDENTS.md` (Rule-3 Incidents) as one parsed entity: one row per
incident — date, d-work, what, cause, consequence — so that the log has **one** parser instead of the
four independent readers that grew without one (`references.py` `incident_ids`, the sysarch
`instances` and `erd` projectors, the countersign projector; d-work #166 plan, attack A5). Those four
are left exactly as they are; this is the home a fifth reader uses, and the one they move to in their
own d-work.
The check is shape only: the table is present and headed as FIELDS says, every row has five cells, the
date parses, and the `d-work` cell carries at least one `#<id>`. Whether the id resolves is Rule-20's
(`references.py` `incident_ids`), whether the row is *true* is inference, and whether its failure mode
is closed is Rule-3's own hardening exercise. An absent log skips: a fresh install has none
(Rule-11 property 5, the absent-store pattern).
It is a script and not a guard, deliberately: a new entry in the guard registry falsifies a *released*
craft's pinned tests, and changing a released craft's tree cannot land (row #170 carries that gap, and
`agent-corpus/audits/INCIDENTS.md` the incident). The shape check below therefore runs on every push
through Rule-12's suites — `dyad/tests/test_incidents.py` `LiveTests` — rather than through the
registry. A later d-work moves this module under `dyad/guards/agent/` with its `ENTITY`, `CORPUS`,
`describe` and registry entry, once #170 closes that gap; nothing else about it changes.
  incidents.py [repo-root]      check the instance's log and print its shape
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("incidents.py: Python 3.12+ required")
import datetime, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

NAME, OWNER = "incident (a row of the incident log)", "Rule-3"
FIELDS = ("date", "d-work", "what", "cause", "consequence")     # the header of the log's table, as Rule-3 Incidents names it
REL = "audits/INCIDENTS.md"                                     # under the instance location (Rule-11 property 3)
DWORK = re.compile(r"#(\d+)")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS)),
    ("fields-open-with-date", lambda: FIELDS[0] == "date"),
    ("rel-under-audits", lambda: REL.startswith("audits/") and REL.endswith(".md")),
]

def log_path(root: Path | None = None) -> Path:
    """The instance's incident log; may not exist (a fresh install has none)."""
    return dyadlib.instance(root or dyadlib.repo_root()) / REL

def _table(text: str) -> tuple[list[str], list[list[str]]] | None:
    """The first table whose header is FIELDS (case-insensitive), or None."""
    want = tuple(f.lower() for f in FIELDS)
    for h, rows in dyadlib.tables(text):
        if tuple(c.strip().lower() for c in h) == want:
            return h, rows
    return None

def parse_text(text: str) -> list[dict]:
    """[{date, d-work, what, cause, consequence, ids}] in file order; `ids` is every `#<id>` of the
    d-work cell. A row with the wrong cell count is still returned (short cells empty), so the check
    reports it rather than the parser hiding it."""
    t = _table(text)
    if not t:
        return []
    out = []
    for r in t[1]:
        row = {f: (r[i].strip() if i < len(r) else "") for i, f in enumerate(FIELDS)}
        row["cells"] = len(r)
        row["ids"] = DWORK.findall(row["d-work"])
        out.append(row)
    return out

def parse(path: Path | None = None, root: Path | None = None) -> list[dict]:
    """The log's rows; [] when the log is absent."""
    p = path or log_path(root)
    return parse_text(p.read_text(errors="ignore")) if p.is_file() else []

def by_year_month(rows: list[dict]) -> dict[str, list[dict]]:
    """{`YYYY-MM`: rows}, the coarsest grouping the log's own dates support. A row whose date does not
    parse groups under `""`, never silently dropped."""
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["date"][:7] if _date(r["date"]) else "", []).append(r)
    return {k: v for k, v in sorted(out.items())}

def _date(s: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(s.strip())
    except ValueError:
        return None

def check_log(path: Path) -> list[str]:
    text = path.read_text(errors="ignore")
    msgs = []
    if _table(text) is None:
        return [f"{path.name}: no incident table headed {', '.join(FIELDS)} (Rule-3 Incidents)"]
    rows = parse_text(text)
    if not rows:
        return [f"warning: {path.name}: incident table has no rows"]
    for i, r in enumerate(rows, 1):
        where = f"{path.name} row {i} ({r['date'] or 'no date'})"
        if r["cells"] != len(FIELDS):
            msgs.append(f"{where}: {r['cells']} cells, not {len(FIELDS)}")
        if _date(r["date"]) is None:
            msgs.append(f"{where}: date does not parse as YYYY-MM-DD")
        if not r["ids"]:
            msgs.append(f"{where}: d-work cell names no `#<id>`")
        for f in ("what", "cause", "consequence"):
            if not r[f]:
                msgs.append(f"{where}: {f} is empty")
    return msgs

def check(root: Path | None = None) -> list[str]:
    root = root or dyadlib.repo_root()
    p = log_path(root)
    if not p.is_file():
        return [f"warning: skip {dyadlib.rel(p, root) if hasattr(dyadlib, 'rel') else p.name}: no incident log (a fresh install has none)"]
    return check_log(p)

def summary(root: Path | None = None) -> str:
    rows = parse(root=root or dyadlib.repo_root())
    return f"{len(rows)} incidents, {len(by_year_month(rows))} month(s)"

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check(root)
    hard = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        print(f"{'FAIL' if not m.startswith('warning:') else 'warn'} [incidents] {m.removeprefix('warning:').strip()}",
              file=sys.stderr if not m.startswith("warning:") else sys.stdout)
    if not hard:
        print(f"ok   [incidents] {summary(root)}")
    return 1 if hard else 0

if __name__ == "__main__":
    sys.exit(main())
