#!/usr/bin/env python3
"""Unit and session census (a cabinet script; its master record `crafts/cabinet/dmc/session-tidy.jsonld`, homed in
the play-book `crafts/cabinet/playbooks/session-tidy.md`; d-work #640, widened by #669). Kernel: Python 3.12+.
A reading, never a check: it is no guard, so no runner discovers it, and the census is printed by `main`, which the
run-book's `census` step runs (`dyad runbook run cabinet:session-tidy census`).

It reads four inputs and gives each of this system's sessions one class, a census fact the record names, and from it
one act, the record's outcome (the record is the master: its `termCode`s are ACTS, TREE_INVARIANTS):
- the presence store, `<instance>/d-work/sessions/<unit>.md`, through the core's presence guard (`seen`, `rows`,
  `holder`);
- the rows, `dyadlib.read_rows`: a row is open when its state is not terminal (`dyadlib.TERMINAL_STATES`);
- the charters, the instance's mandates table through the path the cabinet's `seats` guard reads
  (`seats.mandates_path`): a unit is chartered when a row's `seat` names it, or its `<function>-<hp>` form does;
- the window, the `attendance-window` preference (`sessions.attendance_window`).
The harness side is the account's own session list the cos writes (`list_sessions`, `mine: true`), passed as
`--harness <file>`: one `<session id> <owner/repo|-> [<title>]` per line, `#` comments (#669). A list with no
repository column, a transcribed harness list, is read as before, each entry's repository unknown. Without a file,
the harness's own records as `dyad session reconcile` reads them (`hostadapter.harness_sessions`).
- An entry no presence file names by holder or title is `outside` when its repository is another one or none: it is
  counted, never listed, classed or named (the record's first outcome). It is `never-registered` when its repository
  is this one (`git remote get-url origin`) or unknown.
- An entry a presence file names keeps that unit's class; when its title does not open with the unit name, the unit
  also takes `retitle`.
The record's `retire` and `register` read what this script does not: a unit's ended work, and reconcile's
`no presence` lines. The cos reads them, as the play-book says; this script never proposes them.

One line per unit or session, `<act> <class> <unit or harness id> seen=<ts|-> rows=<ids|-> charter=yes|no
holder=<hp|->`, sorted by the record's proposal order, then the `outside:` count line, the count line and the batch
question's text. Read-only: it writes nothing.
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
CLASSES = ("live-seat", "live-desk", "neglected", "done", "stale", "never-registered")   # the record's census facts
ACTS = ("outside", "keep", "archive", "retire", "re-home", "retitle", "register")   # the record's termCodes (#669)
ACT_OF = {"live-seat": "keep", "live-desk": "keep", "neglected": "re-home", "done": "archive", "stale": "archive",
          "never-registered": "archive", "unclassed": "keep"}   # each class's act, as the record's outcomes say
PROPOSE = ("archive", "retire", "re-home", "retitle", "register")   # the batch's order; keep is never proposed
REPO_URL = re.compile(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$")   # owner/name of an origin URL
REPO_CELL = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|-")
UNCLASSED = "unclassed"   # the record's dyad:default: a session no outcome describes; reported, never proposed, fails the pass
ORDER = ("done", "stale", "never-registered", "live-seat", "neglected", "live-desk", UNCLASSED)   # proposal order, the pass, then the default
HARNESS_FLAG = "--harness"
FIELDS = ("class", "unit", "seen", "rows", "charter", "holder")
HP = re.compile(r"[0-9a-f]{8}")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("classes-distinct", lambda: len(set(CLASSES)) == len(CLASSES) == 6),
    ("order-is-every-class-and-the-default", lambda: sorted(ORDER) == sorted(CLASSES + (UNCLASSED,)) and UNCLASSED not in CLASSES),
    ("fields-open-with-class-and-unit", lambda: FIELDS[:2] == ("class", "unit") and len(set(FIELDS)) == len(FIELDS)),
    ("every-class-has-an-act", lambda: set(ACT_OF) == set(CLASSES) | {UNCLASSED} and set(ACT_OF.values()) <= set(ACTS)),
    ("proposed-acts-are-acts-not-keep-or-outside", lambda: set(PROPOSE) <= set(ACTS) and not {"keep", "outside"} & set(PROPOSE)),
    ("repo-url-reads-both-forms", lambda: REPO_URL.search("git@github.com:o/r.git")[1] == "o/r" == REPO_URL.search("https://h/o/r")[1]),
]
dyadlib.enforce(INVARIANTS, __name__)

def record_codes(path: Path = RECORD) -> tuple[str, ...] | None:
    """The record's outcome codes, in its order; None while the record is absent."""
    if not path.is_file():
        return None
    return tuple(o.get("termCode") for o in json.loads(path.read_text()).get("hasDefinedTerm", []))

TREE_INVARIANTS = [   # reads the craft's tree: the runner's pass only
    ("acts-are-the-records", lambda: record_codes() is None or set(record_codes()) == set(ACTS)),
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
    """[{id, repo, title}] from the account list: one `<session id> <owner/repo|-> [<title>]` per line, or a
    transcribed `<session id> [<title>]` with no repository column (`repo` None, unknown); blank and `#` lines
    skipped. A second word is the repository cell when it is `owner/name` or `-` (#669)."""
    out = []
    for line in path.read_text().splitlines():
        s = line.split("#", 1)[0].strip() if not line.lstrip().startswith("#") else ""
        if s:
            hid, _, rest = s.partition(" ")
            cell, _, title = rest.strip().partition(" ")
            if REPO_CELL.fullmatch(cell):
                out.append({"id": hid, "repo": None if cell == "-" else cell, "has_repo": True, "title": title.strip()})
            else:
                out.append({"id": hid, "repo": None, "has_repo": False, "title": rest.strip()})
    return out

def this_repo(root: Path) -> str | None:
    """This repository's `owner/name`, from `git remote get-url origin`; None when there is none."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"], capture_output=True, text=True,
                           env=dyadlib.git_env(), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    m = REPO_URL.search(r.stdout.strip()) if r.returncode == 0 else None
    return m[1] if m else None

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

def census(root: Path, harness: list[dict] | None = None, now: datetime.datetime | None = None,
           repo: str | None = None, outside: list | None = None) -> list[dict[str, str]]:
    """[{act, class, unit, seen, rows, charter, holder}], in the record's proposal order then ORDER, then by unit. An
    account entry outside the system is appended to `outside` (when given) and never listed; `repo` is this
    repository's `owner/name`, read from origin when None."""
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
        cls = classify(live, ch, is_desk(name), held, states)
        out.append({"act": ACT_OF[cls], "class": cls, "unit": name, "seen": s.get("seen") or "-",
                    "rows": " ".join(held) or "-", "charter": "yes" if ch else "no", "holder": s.get("holder") or "-"})
    if harness is None:
        harness = dyadlib.load_module(dyadlib.PKG / "scripts" / "hostadapter.py", "hostadapter").harness_sessions(root)
    repo = this_repo(root) if repo is None else repo
    by_unit = {c["unit"]: c for c in out}
    for h in harness:
        hid, title = h.get("id", ""), (h.get("title") or "").strip()
        named = title.split(":", 1)[0].split()[0] if title else ""
        match = next((name for name, hp in holders if name == named or (hp and hid.startswith(hp))), None)
        if not hid:
            continue
        if match is not None:                             # this system's: a presence file names it
            if title and named != match and by_unit[match]["act"] == "keep":
                by_unit[match] = {**by_unit[match], "act": "retitle"}
            continue
        if h.get("has_repo") and h.get("repo") != repo:   # another repository, or none: outside, never listed (#669)
            if outside is not None:
                outside.append(hid)
            continue
        out.append({"act": "archive", "class": "never-registered", "unit": hid, "seen": "-", "rows": "-", "charter": "no",
                    "holder": "-"})
    out = [by_unit.get(c["unit"], c) for c in out]
    rank = lambda a: PROPOSE.index(a) if a in PROPOSE else len(PROPOSE)
    return sorted(out, key=lambda c: (rank(c["act"]), ORDER.index(c["class"]), c["unit"]))

def line(c: dict[str, str]) -> str:
    return (f"{c['act']} {c['class']} {c['unit']} seen={c['seen']} rows={c['rows'].replace(' ', ',')} "
            f"charter={c['charter']} holder={c['holder']}")

def outside_line(n: int) -> str:
    """The record's `outside` outcome: a count, naming no session."""
    return f"outside: {n} sessions (not this system's; not read)"

def question(rows: list[dict[str, str]]) -> str:
    """The batch question's text, the play-book's form, its acts in the record's order; `none` when nothing is proposed."""
    acts = [f"{c['unit']}: {c['act']}" for c in rows if c["act"] in PROPOSE]
    return f"question: Y/N: tidy {', '.join(acts)}?" if acts else "question: none (nothing to propose)"

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
    out: list = []
    rows = census(root, harness, outside=out)
    for c in rows:
        print(line(c))
    print(outside_line(len(out)))
    print(counts(rows))
    print(question(rows))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
