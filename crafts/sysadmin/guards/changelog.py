#!/usr/bin/env python3
"""Change-log guard (entity `changelog`, store zone `workstation`; the sysadmin craft's `host-mutation.md` owns the
row's columns, Rule-8's kernel binds that a row exists, placed per Rule-11 property 1 — a Tended craft's guard,
`crafts/sysadmin/guards/`, discovered by the core runner as `sysadmin/changelog`, #155). Kernel: Python 3.12+.
`workstation-corpus/CHANGELOG.md` (instance; seeded from `crafts/sysadmin/templates/CHANGELOG.md`): the
template's header is always FIELDS; an instance header is FIELDS, or FIELDS with its OPTIONAL trailing
columns dropped (`actor`, #216 — an instance mid-migration between a craft-zone PR that adds a column and the
workstation-zone PR that backfills it, Rule-1: referent before referrer). Each row has a `YYYY-MM-DD` date, a
`#<id>` d-work cell (resolved by `references.py`, Rule-20), a class in dyadlib.HOST_CLASSES, a non-empty
action, an `actor` in ACTORS where the column is present (the party whose hands executed the action
— an Operator-run ops script is `operator`, an Agent-run command `agent`; a divergent credential is
named in `outcome`, host-mutation.md), and — for a reversible or
destructive action — a non-empty undo (Rule-8 Conduct; a destructive action may say `none` and why). A missing
change log passes (fresh install before the first host action). Whether the row matches the plan's H-row
stays inference (Rule-8).
  changelog.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("changelog.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))  # the core craft's library
import dyadlib

CRAFT = Path(__file__).resolve().parents[1]           # crafts/sysadmin: the template sits beside the rule
ENTITY, CORPUS, TRANSACTION = "changelog", "workstation", False
NAME, OWNER = "change-log row", "Rule-8"
FIELDS = ("date", "d-work", "class", "action", "undo", "outcome", "actor")
OPTIONAL = ("actor",)   # trailing suffix of FIELDS an *instance* header may omit while migrating (#216);
                        # the template (check_package) is always FIELDS exactly — never truncated
ACTORS = ("operator", "agent")   # actor enum: the party whose hands executed the action (a divergent credential is named in outcome, host-mutation.md)
CLASSES = dyadlib.HOST_CLASSES
LOGGED = ("reversible", "destructive")      # classes that need an undo cell (read-only is not normally logged)
INVARIANTS = [("logged-classes-subset", lambda: set(LOGGED) <= set(CLASSES)),   # crafts/syseng/rules/invariants.md
              ("fields-name-key-columns", lambda: {"d-work", "class", "action", "undo", "outcome"} <= set(FIELDS)),
              ("optional-is-fields-suffix", lambda: FIELDS[len(FIELDS) - len(OPTIONAL):] == OPTIONAL)]
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DWORK = re.compile(r"^#\d+(\s*[,;]\s*#\d+)*$")
_EVENT = re.compile(r"\bevent:\s*`?([A-Za-z0-9][\w.-]*)`?")

# REFERENCES_CONTRIB (Rule-11 property 2's contribution mechanism, `agent-corpus/falsification/
# extensibility.md` #101, d-work #100): rows the core register (`dyad/guards/agent/references.py`)
# carried as `changelog.action->ops` and `changelog.event->event` until PR 2 of #100 retired them —
# this craft declares its own now, discovered the same way a guard is. Each extractor takes the
# same `Corpus` object the core register's own extractors do.
def changelog_action_ops(c):
    """`<ops dir>/<name>.sh` paths named in a change-log action cell."""
    header, rows = c.changelog
    i = header.index("action") if "action" in header else None
    if i is None:
        return []
    ops = dyadlib.find_guard("workstation", "ops_scripts", c.pkg)
    if ops is None:
        return []
    pat = re.compile(re.escape(c.rel(ops.ops_dir(c.root))) + r"/[\w.-]+\.sh")
    return [(f"workstation-corpus/CHANGELOG.md row {k + 1} action", m) for k, r in enumerate(rows) if len(r) > i for m in pat.findall(r[i])]

def _ops_path_exists(c, t):
    return (c.root / t).exists()

def changelog_event_outcome(c):
    """`event: <id>` tokens in a change-log outcome cell (Rule-8 Conduct: the event is the row's evidence)."""
    header, rows = c.changelog
    i = header.index("outcome") if "outcome" in header else None
    if i is None:
        return []
    return [(f"workstation-corpus/CHANGELOG.md row {k + 1} outcome", m) for k, r in enumerate(rows) if len(r) > i for m in _EVENT.findall(r[i])]

def _event_id_exists(c, t):
    return any(e.get("id") == t for evs in c.events.values() for e in evs)

REFERENCES_CONTRIB = [
    ("changelog.action->ops",  "changelog", "action",  changelog_action_ops,   "ops",   _ops_path_exists),
    ("changelog.event->event", "changelog", "outcome", changelog_event_outcome, "event", _event_id_exists),
]

def changelog_path(root: Path) -> Path:
    return root / "workstation-corpus" / "CHANGELOG.md"

def parse(text: str) -> tuple[list[str], list[list[str]]]:
    return dyadlib.table_header(text), dyadlib.table_rows(text)

def accepted_headers() -> list[tuple[str, ...]]:
    """FIELDS, and FIELDS with its OPTIONAL trailing columns stripped — the second only while OPTIONAL is
    non-empty; an instance header may be either, a template header (check_package) only the first."""
    return [FIELDS, FIELDS[:len(FIELDS) - len(OPTIONAL)]] if OPTIONAL else [FIELDS]

def check_text(text: str, where: str) -> list[str]:
    header, rows = parse(text); msgs = []
    accepted = accepted_headers()
    if tuple(header) not in accepted:
        want = " or ".join(str(list(h)) for h in accepted)
        msgs.append(f"{where}: header {header or 'missing'} is not {want}")
        return msgs
    fields = tuple(header)   # the accepted header actually present — same length as every row's cells
    for k, r in enumerate(rows, 1):
        if len(r) != len(fields):
            msgs.append(f"{where} row {k}: {len(r)} cells, want {len(fields)}"); continue
        d = dict(zip(fields, r))
        if not _DATE.match(d["date"]):
            msgs.append(f"{where} row {k}: date `{d['date']}` is not YYYY-MM-DD")
        if not _DWORK.match(d["d-work"]):
            msgs.append(f"{where} row {k}: d-work `{d['d-work']}` is not `#<id>`")
        if d["class"] not in CLASSES:
            msgs.append(f"{where} row {k}: class `{d['class']}` is not one of {', '.join(CLASSES)} (Rule-8)")
        if not d["action"]:
            msgs.append(f"{where} row {k}: empty action")
        if d["class"] in LOGGED and not d["undo"]:
            msgs.append(f"{where} row {k}: {d['class']} action with an empty undo (Rule-8)")
        if "actor" in d and d["actor"] not in ACTORS:
            msgs.append(f"{where} row {k}: actor `{d['actor']}` is not one of {', '.join(ACTORS)}")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG, craft: Path = CRAFT) -> list[str]:
    root = root or dyadlib.repo_root()
    msgs = []
    tmpl = craft / "templates" / "CHANGELOG.md"
    if tmpl.exists() and tuple(dyadlib.table_header(tmpl.read_text())) != FIELDS:
        msgs.append(f"templates/CHANGELOG.md: header is not {list(FIELDS)}")
    cl = changelog_path(root)
    if cl.exists():
        rel = cl.relative_to(root) if cl.is_relative_to(root) else cl
        msgs += check_text(cl.read_text(), str(rel))
    return msgs

def summary(root: Path | None = None) -> str:
    cl = changelog_path(root or dyadlib.repo_root())
    return f"{len(dyadlib.table_rows(cl.read_text())) if cl.exists() else 0} rows"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    cl = changelog_path(root)
    rows = dyadlib.table_rows(cl.read_text()) if cl.exists() else []
    last = rows[-1] if rows else []
    classes = sorted({r[2] for r in rows if len(r) > 2})
    rel = cl.relative_to(root) if cl.is_relative_to(root) else cl
    allowed = {"date": "YYYY-MM-DD", "d-work": "`#<id>`", "class": " | ".join(CLASSES) + (f" (observed: {', '.join(classes)})" if classes else ""),
               "undo": f"non-empty for {' and '.join(LOGGED)}", "actor": " | ".join(ACTORS)}
    return {"store": str(rel), "parser": "`changelog.parse` (`dyadlib.table_header` / `table_rows`; template `crafts/sysadmin/templates/CHANGELOG.md`)", "observed": len(rows),
            "note": "one row per reversible or destructive host action, written in the same d-work (Rule-8; columns: the sysadmin craft's host-mutation rule)",
            "fields": [(c, "date" if c == "date" else "enum" if c == "class" else "text", allowed.get(c, ""), True, last[i] if i < len(last) else "", "changelog.FIELDS") for i, c in enumerate(FIELDS)]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs: print(f"FAIL [rule-8] {m}", file=sys.stderr)
    if not msgs: print(f"ok   [rule-8] change log: {summary(root)}")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
