#!/usr/bin/env python3
"""Board guard and CLI (entity `board`, agent corpus; Rule-3 owns the orchestration it records, Rule-16 the store
beside the rows; placed per Rule-11 property 1; d-work #535, cos mode P1). Kernel: Python 3.12+, git.

What the cos holds in flight lived only in its chat, so a hop of the mode from one session to another lost it (plan
#535): the questions owed to the Operator, the work dispatched to seats, the gates, the relays, the promises, the seat
table. The board store puts it on `main`:

  <instance>/d-work/board/<id>.md   one per row not terminal with orchestration in flight
  <instance>/d-work/board/_cos.md   the cross-row items: the seat table, the last question asked, the promises (the
                                    pending queue is derived at read since #572 K4; a stored `queue` is still read)

Each file is `key: value` lines; a value continues on the lines after it that start with two spaces (so a question
is kept verbatim, newlines and all); blank and `#` lines are skipped. Keys of a row's file: `holder` (the cos session
that holds the mode), `owner` (the seat doing the work, and its session id), `waiting-on` (`operator` | `unit <name>`
| `external <ref>`), `next` (the next act), `since`, `question` (verbatim, when the Operator owes one), `promised`
(follow-ups named to the Operator), and `writer`, which `board set` writes and nobody types — the harness session
that wrote the file last (`sessions.writer`, Rule-16's writer pattern, #350). `_cos.md` takes `queue` and `seats` in
place of `owner` and `waiting-on`. Unlike a row the store is overwritten freely; its history is git's.

  dyad board                         render the board from the working tree: one line per entry, oldest wait first
  dyad board set <id>|_cos key=value… [--drop]
                                     merge the pairs into the file as it stands on a freshly fetched origin/main, in
                                     land's worktree, and land it as a ledger-only commit (`dwork land`'s loop, so a
                                     moved `main` re-merges from the inputs). `holder` defaults to this seat
                                     (`DYAD_SESSION`), `since` to now when `waiting-on` changes, `writer` is always this
                                     session; `key=` removes a key; `--drop` removes the file
  dyad board resume                  what a new holder needs: this seat's unread inbox count (#536), every entry in
                                     full, the questions owed verbatim, the gates, the seats to announce to (every
                                     owner, co-owners included, #551); an entry whose row is terminal is marked stale
                                     and owes nothing (#547)

`dyad board` and `board set` warn when the file's last `writer` is not this session: two holders may be writing
(plan #535 attack 6; the lease, #537, arbitrates later). A warning, never a refusal. The cos writes the board before
it sends the message or asks the question it records (write-ahead, plan #535 attack 3).

The check (`check_package`): every file is `<id>.md` or `_cos.md`, well-formed, keys known and not repeated, `holder`
present, `waiting-on` and `since` in their forms, and each id a row (fails otherwise, Rule-20); a row that is
terminal is a stale entry, a warning. Not checked: staleness by age, and append-only (the store is overwritten).
  board.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("board.py: Python 3.12+ required")
import datetime, os, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "board", "agent", False
NAME, OWNER = "board entry", "Rule-3"
BOARD_REL = "d-work/board"
COS = "_cos"
FIELDS = ("holder", "owner", "waiting-on", "next", "since", "question", "promised", "writer")
COS_FIELDS = ("holder", "queue", "seats", "next", "since", "question", "promised", "writer")
REQUIRED = ("holder",)
CONT = "  "                                          # a continuation line's prefix
WAITING = re.compile(r"operator|(?:unit|seat) \S+|external \S.*")   # `seat <name>` is `unit <name>`'s alias (#553)
UNIT_ALIAS = "seat "                                # read until the release after next; `board set` writes `unit `
KEY = re.compile(r"[a-z][a-z-]*")
USAGE = ("usage: dyad board | dyad board set <id>|_cos key=value… [--drop] | dyad board resume")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("holder-is-required-everywhere", lambda: all(k in FIELDS and k in COS_FIELDS for k in REQUIRED)),
    ("writer-is-a-key-of-both", lambda: "writer" in FIELDS and "writer" in COS_FIELDS),
    ("waiting-on-forms", lambda: all(WAITING.fullmatch(v) for v in ("operator", "unit counsel-015qiPLU", "seat counsel-015qiPLU", "external run 1"))
                                 and not WAITING.fullmatch("someone")),
    ("store-under-d-work", lambda: BOARD_REL.startswith("d-work/")),
]


# ---- the form
def store(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / BOARD_REL


def parse(text: str) -> tuple[dict[str, str], list[str]]:
    """(fields, problems): `key: value` lines, two-space continuation lines appended to the value with a newline."""
    fields, problems, last = {}, [], None
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith(CONT):                       # first: a value's own blank or `#` line is still its text
            if last is None:
                problems.append(f"line {n}: a continuation with no key before it")
            else:
                fields[last] += "\n" + line[len(CONT):]
            continue
        if not line.strip() or line.startswith("#"):
            last = None
            continue
        k, sep, v = line.partition(": ")
        if not sep and line.endswith(":"):
            k, sep, v = line[:-1], ":", ""
        if not sep or not KEY.fullmatch(k):
            problems.append(f"line {n}: not `key: value` ({line[:60]!r})")
            last = None
            continue
        if k in fields:
            problems.append(f"line {n}: key {k!r} repeated")
        fields[k], last = v, k
    return fields, problems


def render(fields: dict[str, str], keys) -> str:
    """The file text: known keys in their order, each value's later lines as continuations."""
    out = []
    for k in keys:
        if k in fields and fields[k] != "":
            first, *rest = fields[k].split("\n")
            out.append(f"{k}: {first}".rstrip())
            out += [CONT + r for r in rest]
    return "\n".join(out) + "\n"


def keys_for(name: str):
    return COS_FIELDS if name == COS else FIELDS


def parse_since(v: str) -> datetime.datetime | None:
    try:
        d = datetime.datetime.fromisoformat(v)
    except ValueError:
        try:
            d = datetime.datetime.combine(datetime.date.fromisoformat(v), datetime.time())
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def check_entry(name: str, text: str, states: dict[int, str]) -> list[str]:
    """One file's problems; `name` its stem, `states` row id -> state."""
    where = f"board/{name}.md"
    if name != COS and not name.isdigit():
        return [f"{where}: not `<id>.md` or `{COS}.md`"]
    fields, problems = parse(text)
    msgs = [f"{where}: {p}" for p in problems]
    allowed = keys_for(name)
    msgs += [f"{where}: unknown key {k!r} (keys: {', '.join(allowed)})" for k in fields if k not in allowed]
    msgs += [f"{where}: '{k}' missing" for k in REQUIRED if not fields.get(k)]
    if "waiting-on" in fields and not WAITING.fullmatch(fields["waiting-on"]):
        msgs.append(f"{where}: 'waiting-on' is not `operator`, `unit <name>` (alias `seat <name>`) or `external <ref>` ({fields['waiting-on']!r})")
    if "since" in fields and parse_since(fields["since"]) is None:
        msgs.append(f"{where}: 'since' is not an ISO-8601 date or time ({fields['since']!r})")
    if name.isdigit():
        state = states.get(int(name))
        if state is None:
            msgs.append(f"{where}: no row #{name} (Rule-20: an unresolved reference)")
        elif state in dyadlib.TERMINAL_STATES:
            msgs.append(f"warning: {where}: row #{name} is {state}; a stale entry — `dyad board set {name} --drop`")
    return msgs


def entries(root: Path) -> list[Path]:
    d = store(root)
    return sorted(d.glob("*.md")) if d.is_dir() else []


def row_states(root: Path) -> dict[int, str]:
    try:
        return {r.id: r.state for r in dyadlib.read_rows(root)}
    except (OSError, ValueError, KeyError):
        return {}


# ---- the guard contract
def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    files = entries(root)
    if not files:
        return []
    states = row_states(root)
    msgs = []
    for p in files:
        msgs += check_entry(p.stem, p.read_text(errors="replace"), states)
    return msgs


def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(entries(root or dyadlib.repo_root()))} board file(s)"


def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    d = store(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    return {"store": f"{rel}/<id>.md and {rel}/{COS}.md",
            "parser": "`board.parse` (key: value lines, two-space continuations)",
            "observed": len(entries(root)),
            "note": "the cos's orchestration in flight, one file per row not terminal; overwritten, history is git's",
            "fields": [(f, "text", "", f in REQUIRED, "", "board.FIELDS") for f in FIELDS]}


# ---- the CLI
def sessions():
    return dyadlib.load_guard("agent", "sessions")


def writer_warning(name: str, fields: dict[str, str], me: str) -> str | None:
    w = fields.get("writer")
    if w and w != me:
        return (f"warn: board/{name}.md was last written by {w}, not this session ({me}): two holders may be writing "
                f"(plan #535 attack 6; the lease, #537, arbitrates)")
    return None


def merged(old: dict[str, str], pairs: dict[str, str], seat: str | None, me: str, now: str) -> dict[str, str]:
    """`old` with `pairs` applied (`key=` removes), `holder` defaulted to `seat` only when the entry holds none (#572 K7:
    a default that re-took the holder on every write flipped it in 44 of 130 writes), `since` to `now` when
    `waiting-on` changes or the entry is new, and `writer` set to `me`."""
    new = dict(old)
    for k, v in pairs.items():
        if v == "":
            new.pop(k, None)
        else:
            new[k] = v
    if "holder" not in pairs and seat and not new.get("holder"):
        new["holder"] = seat
    if "since" not in pairs and (not old or new.get("waiting-on") != old.get("waiting-on")):
        new["since"] = now
    new["writer"] = me
    return new


class Refused(Exception):
    pass


def parse_set(a: list[str]) -> tuple[str, dict[str, str], bool]:
    """(name, pairs, drop) from `<id>|_cos key=value… [--drop]`."""
    if not a:
        raise Refused(USAGE)
    name, rest = a[0], a[1:]
    if name != COS and not name.isdigit():
        raise Refused(f"{name!r} is not a row id or {COS}")
    drop = "--drop" in rest
    rest = [x for x in rest if x != "--drop"]
    if drop and rest:
        raise Refused("--drop takes no key=value")
    if not drop and not rest:
        raise Refused(USAGE)
    pairs = {}
    for x in rest:
        k, sep, v = x.partition("=")
        if not sep or not KEY.fullmatch(k):
            raise Refused(f"{x!r} is not key=value")
        if k == "writer":
            raise Refused("`writer` is written by `board set` itself, never typed")
        if k not in keys_for(name):
            raise Refused(f"unknown key {k!r} for {name} (keys: {', '.join(k for k in keys_for(name) if k != 'writer')})")
        if k in REQUIRED and v == "":
            raise Refused(f"{k!r} cannot be removed")
        if k == "waiting-on" and v and not WAITING.fullmatch(v):
            raise Refused(f"waiting-on is `operator`, `unit <name>` or `external <ref>`, not {v!r}")
        if k == "waiting-on" and v.startswith(UNIT_ALIAS):
            v = "unit " + v[len(UNIT_ALIAS):]           # the canonical form is written; the alias is only read (#553)
        if k == "since" and v and parse_since(v) is None:
            raise Refused(f"since is an ISO-8601 date or time, not {v!r}")
        pairs[k] = v
    return name, pairs, drop


def set_builder(name: str, pairs: dict[str, str], drop: bool, inst: str):
    """land's builder: the merge runs in land's worktree, on a freshly fetched origin/main, on every try."""
    s = sessions()
    me = s.writer()
    seat = os.environ.get("DYAD_SESSION") or None
    def build(wt: Path):
        path = wt / inst / BOARD_REL / f"{name}.md"
        rel = path.relative_to(wt).as_posix()
        if drop:
            if not path.exists():
                raise Refused(f"already landed: {rel} is not on origin/main; nothing pushed")
            path.unlink()
            return [rel], f"ledger: board {name} dropped", ""
        if name.isdigit():
            row = next((r for r in dyadlib.read_rows(wt) if r.id == int(name)), None)
            if row is None:
                raise Refused(f"no row #{name} on origin/main")
            if row.state in dyadlib.TERMINAL_STATES:
                raise Refused(f"row #{name} is {row.state} on origin/main: a terminal row has no board entry")
        old = parse(path.read_text())[0] if path.exists() else {}
        w = writer_warning(name, old, me)
        if w:
            print(w, file=sys.stderr)
        new = merged(old, pairs, seat, me, now_iso())
        if not new.get("holder"):
            raise Refused("no holder: set DYAD_SESSION or pass holder=<seat>")
        text = render(new, keys_for(name))
        if path.exists() and path.read_text() == text:
            raise Refused(f"already landed: {rel} on origin/main is identical; nothing pushed")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return [rel], f"ledger: board {name} ({', '.join(sorted(pairs))})", ""
    return build


def cmd_set(a: list[str], repo: Path) -> int:
    land = dyadlib.load_module(dyadlib.PKG / "scripts" / "land.py", "land")
    try:
        name, pairs, drop = parse_set(a)
        inst = dyadlib.instance_rel(repo)
        if inst is None:
            raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree; a board write lands a tracked store")
        return land.land(repo, inst, None, set_builder(name, pairs, drop, inst), "board set")
    except (Refused, land.Refused) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2 if str(e) == USAGE else 1


def age(since: str, now: datetime.datetime) -> str:
    d = parse_since(since)
    if d is None:
        return "?"
    h = int((now - d).total_seconds() // 3600)
    return f"{h // 24}d{h % 24}h" if h >= 24 else f"{h}h"


def load(root: Path) -> list[tuple[str, dict[str, str]]]:
    return [(p.stem, parse(p.read_text(errors="replace"))[0]) for p in entries(root)]


def board_lines(root: Path, now: datetime.datetime | None = None) -> list[str]:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    me = sessions().writer()
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    got = load(root)
    cos = dict(got).get(COS, {})
    items = [(n, f) for n, f in got if n != COS]
    items.sort(key=lambda nf: parse_since(nf[1].get("since", "")) or now)
    out = [f"board: {len(items)} entr{'y' if len(items) == 1 else 'ies'}, holder {cos.get('holder') or '?'} "
           f"(read from the working tree; `git pull` first for main's)"]
    for n, f in items:
        r = rows.get(int(n))
        state, title = (r.state, r.title) if r else ("?", "")
        out.append(f"#{n} {state:<8} waiting-on {f.get('waiting-on', '-')} for {age(f.get('since', ''), now)} | "
                   f"owner {f.get('owner', '-')} | next: {(f.get('next') or '-').splitlines()[0]} | {title[:60]}")
        if f.get("question"):
            out.append(f"    question: {f['question'].splitlines()[-1]}")
    out.append(queue_line(derived_queue(root, got)))
    if cos:
        for k in ("queue", "seats", "question"):
            if cos.get(k):
                out.append(f"_cos {k}: {cos[k].splitlines()[-1] if k == 'question' else ' / '.join(cos[k].splitlines())}")
    live = [i for i, r in rows.items() if r.state in ("open", "planned", "blocked")]
    missing = sorted(set(live) - {int(n) for n, _ in items})
    out.append(f"{len(missing)} open, planned or blocked row(s) carry no board entry")
    out += [w for n, f in got if (w := writer_warning(n, f, me))]
    return out


def derived_queue(root: Path, got: list[tuple[str, dict[str, str]]] | None = None) -> dict[str, list[int]]:
    """#572 K4: the pending queue read from records instead of written to `_cos`: `plan-ready`, the open rows with a
    stored plan and no `Y plan` entry, not accreted under a mandate; `done-ready`, the live entries whose question is a
    Done question (`Done with`). Rule-3's counts, so no write keeps them."""
    got = load(root) if got is None else got
    plans = dyadlib.instance(root) / "d-work" / "plans"
    rows = dyadlib.read_rows(root)
    plan_ready = [r.id for r in rows if r.state == "open" and (plans / f"{r.id}.md").exists()
                  and " Y plan" not in f" {r.disposed}" and "mandate #" not in r.disposed]
    live = {r.id for r in rows if r.state not in dyadlib.TERMINAL_STATES}
    done_ready = sorted(int(n) for n, f in got if n.isdigit() and int(n) in live and "Done with" in (f.get("question") or ""))
    return {"plan-ready": plan_ready, "done-ready": done_ready}


def queue_line(q: dict[str, list[int]]) -> str:
    return ("queue (derived, #572): " + ", ".join(f"{k} {len(v)}" + (f" ({' '.join(f'#{i}' for i in v)})" if v else "")
                                                 for k, v in q.items()))


def owners(f: dict[str, str]) -> list[str]:
    """Every seat an entry's `owner` names: `<seat> [<session>]` parts separated by `;` (co-owners, #551)."""
    return [part.split()[0] for part in f.get("owner", "").split(";") if part.split()]


def resume_view(root: Path) -> dict:
    """What a new holder resumes from, as data (`resume_lines` prints it; a caller acts on it):
    - `cos` (the `_cos` entry), `live` and `stale` entries (`stale`: the row is terminal or gone, #547);
    - `owed` (the live entries waiting on the Operator), `gates` (on an external ref) and `seats` (every seat a live
      entry waits on or names as an owner, co-owners included, #551);
    - `unread`: this seat's unread inbox messages (#536)."""
    got = load(root)
    states = row_states(root)
    items = [(n, f) for n, f in got if n != COS]
    stale = [(n, f) for n, f in items if states.get(int(n)) in dyadlib.TERMINAL_STATES or int(n) not in states]
    live = [(n, f) for n, f in items if (n, f) not in stale]
    seats = sorted({f["waiting-on"].split()[1] for _, f in live if f.get("waiting-on", "").startswith(("unit ", UNIT_ALIAS))}
                   | {o for _, f in live for o in owners(f)})
    seat = os.environ.get("DYAD_SESSION") or None
    return {"cos": dict(got).get(COS, {}), "live": live, "stale": stale, "states": states,
            "owed": [(n, f) for n, f in live if f.get("waiting-on") == "operator"],
            "gates": [(n, f["waiting-on"]) for n, f in live if f.get("waiting-on", "").startswith("external ")],
            "seats": seats, "unread": dyadlib.load_guard("agent", "inbox").unread(root, seat) if seat else 0,
            "last_act": last_acts(root, seats)}


def last_acts(root: Path, seats: list[str]) -> dict[str, str]:
    """#567 F8: {seat: its presence file's `seen`, "" when it has none} — the time of its last ledger act (a plan-`Y`
    it recorded, an inbox read, a session start). Information only: a unit deep in a branch writes none for hours, so
    the board's own `waiting-on` and `since` stay the idle reading."""
    d = sessions().sessions_dir(root)
    out = {}
    for seat in seats:
        p = d / f"{seat}.md"
        out[seat] = sessions().parse(p.read_text(errors="ignore")).get("seen", "") if p.exists() else ""
    return out


def resume_lines(root: Path) -> list[str]:
    v = resume_view(root)
    cos = v["cos"]
    me, seat = sessions().writer(), os.environ.get("DYAD_SESSION") or "?"
    out = [f"resume: this session {seat} (writer {me}); the board's holder {cos.get('holder') or '?'}, "
           f"last written by {cos.get('writer') or '?'}",
           f"inbox {seat}: {v['unread']} unread — `dyad inbox read` before any other act"]
    def block(title, f, keys):
        out.append(title)
        for k in keys:
            if f.get(k):
                first, *rest = f[k].split("\n")
                out.append(f"  {k}: {first}"); out.extend(f"    {r}" for r in rest)
    out.append(queue_line(derived_queue(root)))
    if cos:
        block(f"{COS}:", cos, COS_FIELDS)
    for n, f in v["live"]:
        block(f"#{n}:", f, FIELDS)
    for n, f in v["stale"]:
        out.append(f"#{n}: stale — row #{n} is {v['states'].get(int(n), 'not a row')}; nothing here is owed "
                   f"(`dyad board set {n} --drop`, #547)")
    out.append(f"owed to the Operator ({len(v['owed'])}): re-present each question verbatim, or report it pending")
    for n, f in v["owed"]:
        out.append(f"  #{n} since {f.get('since', '?')}:")
        out += [f"    {line}" for line in (f.get("question") or "(no question recorded)").split("\n")]
    out.append(f"external gates ({len(v['gates'])}): " + ("; ".join(f"#{n} {w}" for n, w in v["gates"]) or "none"))
    out.append(f"announce to ({len(v['seats'])}): {', '.join(v['seats']) or 'none'}" + (f"; seat table: {' / '.join(cos['seats'].splitlines())}" if cos.get("seats") else ""))
    if v["seats"]:
        now = datetime.datetime.now(datetime.timezone.utc)
        out.append("last ledger act (presence `seen`, information only, #567): " + ", ".join(
            f"{s} {age(v['last_act'][s], now) if v['last_act'].get(s) else 'none'}" for s in v["seats"]))
    out.append("then: `dyad board set _cos holder=<this seat>` before any other act (write-ahead)")
    return out


def cli(a: list[str], repo: Path | None = None) -> int:
    repo = Path(repo or dyadlib.repo_root())
    if a and a[0] in ("-h", "--help"):
        print(__doc__); return 0
    if a and a[0] == "set":
        return cmd_set(a[1:], repo)
    if a and a[0] == "resume" and len(a) == 1:
        print("\n".join(resume_lines(repo))); return 0
    if not a:
        print("\n".join(board_lines(repo))); return 0
    print(USAGE, file=sys.stderr)
    return 2


def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"{'warn' if m.startswith('warning:') else 'FAIL'} [rule-3] {m.removeprefix('warning:').strip()}")
    print(f"ok   [rule-3] {summary(root)}")
    return 1 if any(not m.startswith("warning:") for m in msgs) else 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
