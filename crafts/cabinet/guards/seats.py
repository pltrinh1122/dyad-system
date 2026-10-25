#!/usr/bin/env python3
"""Seat guard (entity `seat`, corpus `agent`; the cabinet craft's one guard — its rules `naming.md` (the seat-name
form) and `organization.md` (the mandates table) own the check; placed per `crafts/sysarch/rules/guards.md`
under `crafts/cabinet/guards/`; d-work #383, #369 C9). Kernel: Python 3.12+.
Advisory, never failing — Rule-16 Presence: a presence file is a claim, not a lock, and a seat name from
before the form (`cab-2`, `cos-1`, `unnamed-<hex>`) is history the store keeps. Two reads:
- every presence file `<instance>/d-work/sessions/<seat>.md` against the seat-name form of
  `seats_rules.txt` (`form:`, one regex with the groups `function`, `topic`, `hp`; `function:` lines, the
  standing functions); one summary line names how many are outside the form, with the first three;
- the mandates table, `<preferences>/MANDATES.md` (seeded from `../templates/mandates.md`; absent: one
  `warning: skip` line, the bundle guard's convention), against the template's columns and the function list: one line per row whose columns differ
  or whose function is unknown.
What a seat may do under its charter is the Operator's reading of the charter, never this guard's.
  seats.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("seats.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/cabinet/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "seat", "agent", False
NAME, OWNER = "seat (presence file name)", "crafts/cabinet/rules/naming.md"
FIELDS = ("seat", "function", "topic", "hp")                    # what `parse_seat` yields from one presence-file name
DATA = Path(__file__).resolve().with_name("seats_rules.txt")
MANDATES = "MANDATES.md"                                        # under the preferences corpus; the template's seed
MANDATE_COLUMNS = ("seat", "function", "domain", "fence", "ceiling", "escalations", "revocation")
LEADER = "program"                                              # the function whose bare seat is the leader (plan #369 revision 10)
INVARIANTS = [("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS) and FIELDS[0] == "seat"),   # crafts/syseng/rules/invariants.md
              ("mandate-columns-distinct", lambda: len(set(MANDATE_COLUMNS)) == len(MANDATE_COLUMNS) and MANDATE_COLUMNS[:2] == ("seat", "function")),
              ("leader-is-a-function", lambda: LEADER.isalpha() and LEADER.islower())]
dyadlib.enforce(INVARIANTS, __name__)

def rules(data: Path = DATA) -> tuple[re.Pattern, list[str]]:
    """(the seat-name form, the standing functions) from `seats_rules.txt`: one `form:` line (a regex with the
    named groups function, topic, hp), any number of `function:` lines; `#` comments and blank lines ignored."""
    form, functions = None, []
    for line in data.read_text().splitlines():
        s = line.split("#", 1)[0].strip()
        if not s:
            continue
        key, _, val = s.partition(":")
        if key.strip() == "form":
            form = re.compile(val.strip())
        elif key.strip() == "function":
            functions.append(val.strip())
    if form is None or {"function", "topic", "hp"} - set(form.groupindex):
        raise ValueError(f"{data.name}: one `form:` regex with the groups function, topic, hp is required")
    return form, functions

def parse_seat(name: str, form: re.Pattern) -> dict[str, str] | None:
    """{seat, function, topic, hp} for a name in the form, else None."""
    m = form.fullmatch(name)
    return {"seat": name, "function": m.group("function"), "topic": m.group("topic") or "", "hp": m.group("hp")} if m else None

def kind(seat: dict[str, str], functions: list[str]) -> str:
    """leader | secretary | desk | unknown-function — the reading rule of naming.md: `program-<hp>` is the
    leader, and so is `program-<operator>-<hp>` (the middle token is an Operator's handle, a member pair's leader
    in a multi-Operator tree — the leader keeps no desk by construction, so no `program-<topic>` exists); a
    bare `<function>-<hp>` is a secretary; `<function>-<topic>-<hp>` a desk on that function's board; a
    function not in the standing list is reported, never refused."""
    if seat["function"] not in functions:
        return "unknown-function"
    if seat["function"] == LEADER:
        return "leader"
    return "desk" if seat["topic"] else "secretary"

def presence_names(root: Path) -> list[str]:
    d = dyadlib.instance(root) / "d-work" / "sessions"
    return sorted(p.stem for p in d.glob("*.md")) if d.is_dir() else []

def check_names(names: list[str], form: re.Pattern, functions: list[str]) -> list[str]:
    """One summary line when any name is outside the form, one per unknown function; never a failure."""
    outside = [n for n in names if parse_seat(n, form) is None]
    msgs = []
    if outside:
        msgs.append(f"warning: {len(outside)} of {len(names)} presence file(s) are outside the seat form `<function>[-<topic>]-<hp>` "
                    f"(history the store keeps, Rule-16; first: {', '.join(outside[:3])})")
    unknown = [n for n in names if (s := parse_seat(n, form)) and kind(s, functions) == "unknown-function"]
    if unknown:
        msgs.append(f"warning: {len(unknown)} presence file(s) name a function outside seats_rules.txt ({', '.join(functions)}); "
                    f"first: {', '.join(unknown[:3])}")
    return msgs

def mandates_path(root: Path) -> Path:
    return root / "preferences-corpus" / MANDATES

def check_mandates(text: str, functions: list[str], where: str = MANDATES) -> list[str]:
    """The table's header equals MANDATE_COLUMNS; every row has that many cells and a standing function."""
    header, rows = dyadlib.table_header(text), dyadlib.table_rows(text)
    if tuple(header) != MANDATE_COLUMNS:
        return [f"warning: {where}: columns {header} are not {list(MANDATE_COLUMNS)} (templates/mandates.md)"]
    msgs = []
    for r in rows:
        if len(r) != len(MANDATE_COLUMNS):
            msgs.append(f"warning: {where}: row {r[0] if r else '?'!r} has {len(r)} cells, not {len(MANDATE_COLUMNS)}")
        elif r[1] not in functions:
            msgs.append(f"warning: {where}: row {r[0]!r} names function {r[1]!r}, not a standing function ({', '.join(functions)})")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    form, functions = rules()
    msgs = check_names(presence_names(root), form, functions)
    mp = mandates_path(root)
    if mp.exists():
        msgs += check_mandates(mp.read_text(), functions, str(mp.relative_to(root)))
    else:
        msgs.append(f"warning: skip mandates: no preferences-corpus/{MANDATES} here (the Operator's; seeded from crafts/cabinet/templates/mandates.md)")
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    root = root or dyadlib.repo_root()
    form, functions = rules()
    names = presence_names(root)
    inside = [n for n in names if parse_seat(n, form)]
    return f"{len(inside)} seat(s) in the form of {len(names)} presence file(s), {len(functions)} standing functions"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    form, functions = rules()
    names = presence_names(root)
    seats = [s for s in (parse_seat(n, form) for n in names) if s]
    ex = seats[0] if seats else None
    allowed = {"seat": "the presence file's stem", "function": "one of " + ", ".join(functions), "topic": "a desk's topic, or empty", "hp": "8 hex: the holder's harness session id prefix"}
    return {"store": "<instance>/d-work/sessions/<seat>.md (names only; the file's fields are agent/sessions')",
            "parser": "`seats.parse_seat` over `seats_rules.txt` `form:`", "observed": len(seats),
            "note": "advisory: names outside the form are counted, never failed (Rule-16 Presence)",
            "fields": [(f, "text", allowed[f], f != "topic", ex[f] if ex else "", "seats.FIELDS") for f in FIELDS]}

def main(a: list[str]) -> int:
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(m)
    print(f"ok   [cabinet/seats] {summary(root)}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
