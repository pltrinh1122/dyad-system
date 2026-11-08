#!/usr/bin/env python3
"""Session census classifier (a cabinet script; its master record `crafts/cabinet/dmc/session-tidy.jsonld`, homed
in the play-book `crafts/cabinet/playbooks/session-tidy.md`; d-work #640). Kernel: Python 3.12+.
A reading, never a check: it is no guard, so no runner discovers it, and the census is printed by `main`, which the
run-book's `census` step runs (`dyad runbook run cabinet:session-tidy census`).

It reads four inputs and decides one class per session, as the record's outcomes say (the record is the master; the
codes here are its `termCode`s, TREE_INVARIANTS):
- the presence store, `<instance>/d-work/sessions/<unit>.md`, through the core's presence guard (`seen`, `rows`,
  `holder`);
- the rows, `dyadlib.read_rows`: a row is open when its state is not terminal (`dyadlib.TERMINAL_STATES`);
- the charters, the instance's mandates table through the path the cabinet's `seats` guard reads
  (`seats.mandates_path`): a unit is chartered when a row's `seat` names it, or its `<function>-<hp>` form does;
- the window, the `attendance-window` preference (`sessions.attendance_window`).
The harness side, for `never-registered`, is a transcribed list passed as `--harness <file>` (one `<session id>
[<title>]` per line, `#` comments) — on a cloud kernel each container sees only its own session — and without one
the harness's own records as `dyad session reconcile` reads them (`hostadapter.harness_sessions`).

One line per session, `<class> <unit or harness id> seen=<ts|-> rows=<ids|-> charter=yes|no holder=<hp|->`, sorted
by the record's proposal order, then one count line. Read-only: it writes nothing.
  tidy.py [repo-root] [--harness <file>]   (crafts/cabinet/scripts/)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("tidy.py: Python 3.12+ required")
import datetime, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/cabinet/scripts/ -> dyad/scripts
import dyadlib

RECORD = Path(__file__).resolve().parents[1] / "dmc" / "session-tidy.jsonld"   # the master of the classes (#626)
CLASSES = ("live-seat", "live-desk", "neglected", "done", "stale", "never-registered")   # the record's termCodes
UNCLASSED = "unclassed"   # the record's dyad:default: a session no outcome describes; reported, never proposed, fails the pass
ORDER = ("done", "stale", "never-registered", "live-seat", "neglected", "live-desk", UNCLASSED)   # proposal order, the pass, then the default
HARNESS_FLAG = "--harness"
FIELDS = ("class", "unit", "seen", "rows", "charter", "holder")
HP = re.compile(r"[0-9a-f]{8}")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("classes-distinct", lambda: len(set(CLASSES)) == len(CLASSES) == 6),
    ("order-is-every-class-and-the-default", lambda: sorted(ORDER) == sorted(CLASSES + (UNCLASSED,)) and UNCLASSED not in CLASSES),
    ("fields-open-with-class-and-unit", lambda: FIELDS[:2] == ("class", "unit") and len(set(FIELDS)) == len(FIELDS)),
]
dyadlib.enforce(INVARIANTS, __name__)

def record_codes(path: Path = RECORD) -> tuple[str, ...] | None:
    """The record's outcome codes, in its order; None while the record is absent."""
    if not path.is_file():
        return None
    return tuple(o.get("termCode") for o in json.loads(path.read_text()).get("hasDefinedTerm", []))

TREE_INVARIANTS = [   # reads the craft's tree: the runner's pass only
    ("classes-are-the-records", lambda: record_codes() is None or set(record_codes()) == set(CLASSES)),
]

def seats():
    return dyadlib.load_guard_file(Path(__file__).resolve().parents[1] / "guards" / "seats.py")

def presence():
    return dyadlib.load_guard_file(dyadlib.PKG / "guards" / "agent" / "sessions.py")

def charters(root: Path) -> list[str]:
    """The `seat` cells of the mandates table, backticks dropped; [] when the table is absent."""
    p = seats().mandates_path(root)
    return [dyadlib.plain(r[0]).strip() for r in dyadlib.table_rows(p.read_text()) if r] if p.is_file() else []

def chartered(name: str, rows: list[str]) -> bool:
    """True when a charter row names `name`, or names its `<function>-<hp>` form: `<function>-<hp>` with `<hp>` open."""
    if name in rows:
        return True
    fn, _, hp = name.rpartition("-")
    return bool(fn) and bool(HP.fullmatch(hp)) and f"{fn}-<hp>" in rows

def is_desk(name: str) -> bool:
    """A desk's name holds a topic: `<function>-<topic>-<hp>` (the seat form, `seats.parse_seat`)."""
    form, _ = seats().rules()
    s = seats().parse_seat(name, form)
    return bool(s and s["topic"] and s["function"] != seats().LEADER)

def read_harness(path: Path) -> list[dict]:
    """[{id, title}] from a transcribed list: one `<session id> [<title>]` per line; blank and `#` lines skipped."""
    out = []
    for line in path.read_text().splitlines():
        s = line.split("#", 1)[0].strip() if not line.lstrip().startswith("#") else ""
        if s:
            hid, _, title = s.partition(" ")
            out.append({"id": hid, "title": title.strip()})
    return out

def classify(live: bool, charter: bool, desk: bool, held: list[str], states: dict[int, str]) -> str:
    """One presence file's class. `held` the row ids its `rows` names; an id no row holds counts as no row. Within the
    window a chartered unit is a live seat and a desk holding an open row a live desk; any other session within the
    window is `unclassed`, the record's default (plan #640 F6: the six classes stay as the host's table states them);
    past the window, its rows decide: neglected, done or stale."""
    ids = [int(i) for i in held if i.isdigit() and int(i) in states]
    open_ = [i for i in ids if states[i] not in dyadlib.TERMINAL_STATES]
    if live and charter:
        return "live-seat"
    if live and desk and open_:
        return "live-desk"
    if live:
        return UNCLASSED
    if open_:
        return "neglected"
    return "done" if ids else "stale"

def census(root: Path, harness: list[dict] | None = None, now: datetime.datetime | None = None) -> list[dict[str, str]]:
    """[{class, unit, seen, rows, charter, holder}], in the proposal order (ORDER), then by unit."""
    now = now or datetime.datetime.now(datetime.UTC)
    pres = presence()
    window = pres.attendance_window(root)
    states = {r.id: r.state for r in dyadlib.read_rows(root)}
    charter_rows = charters(root)
    out, holders = [], []
    for s in pres.read_all(root):
        name = s.get("session") or s["_path"].removesuffix(".md")
        try:
            seen = datetime.datetime.fromisoformat(s.get("seen", ""))
            seen = seen if seen.tzinfo else seen.replace(tzinfo=datetime.UTC)
            live = now - seen <= window
        except ValueError:
            live = False
        held = (s.get("rows") or "").split()
        hp = s.get("holder") or name.rpartition("-")[2]
        holders.append((name, hp))
        ch = chartered(name, charter_rows)
        out.append({"class": classify(live, ch, is_desk(name), held, states), "unit": name, "seen": s.get("seen") or "-",
                    "rows": " ".join(held) or "-", "charter": "yes" if ch else "no", "holder": s.get("holder") or "-"})
    if harness is None:
        harness = dyadlib.load_module(dyadlib.PKG / "scripts" / "hostadapter.py", "hostadapter").harness_sessions(root)
    for h in harness:
        hid, title = h.get("id", ""), (h.get("title") or "").strip()
        named = title.split(":", 1)[0].split()[0] if title else ""
        if not hid or any(name == named or (hp and hid.startswith(hp)) for name, hp in holders):
            continue
        out.append({"class": "never-registered", "unit": hid, "seen": "-", "rows": "-", "charter": "no", "holder": "-"})
    return sorted(out, key=lambda c: (ORDER.index(c["class"]), c["unit"]))

def line(c: dict[str, str]) -> str:
    return f"{c['class']} {c['unit']} seen={c['seen']} rows={c['rows'].replace(' ', ',')} charter={c['charter']} holder={c['holder']}"

def counts(rows: list[dict[str, str]]) -> str:
    n = {k: sum(1 for c in rows if c["class"] == k) for k in ORDER}
    passed = all(c["class"] in ("live-seat", "live-desk") for c in rows)
    return f"census: {len(rows)} session(s); " + ", ".join(f"{k} {v}" for k, v in n.items()) + ("; pass" if passed else "")

def main(a: list[str]) -> int:
    a = list(a)
    harness = None
    if HARNESS_FLAG in a:
        i = a.index(HARNESS_FLAG)
        if i + 1 >= len(a):
            print(f"refused: {HARNESS_FLAG} takes a file", file=sys.stderr); return 1
        p = Path(a[i + 1])
        if not p.is_file():
            print(f"refused: no harness list {p}", file=sys.stderr); return 1
        harness = read_harness(p); del a[i:i + 2]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    rows = census(root, harness)
    for c in rows:
        print(line(c))
    print(counts(rows))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
