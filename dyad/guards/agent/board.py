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

  dyad board phases                  read-only: the orchestration machine as data (`dyadlib.ORCH_EVENTS`, d-work #587)
  dyad board advance <id> [<id>…] <event> --expect <phase>|none [key=value…] [--said-file <path>] [--mirror <branch>]
                                     fire one event of the machine on a fresh origin/main and land its every effect in one
                                     ledger-only commit: the board (the derived fields), the ledger lines of an answer
                                     (`dwork state`, composed from the stored question and `--said-file`, never typed),
                                     the trace, and the relays; refused when the phase is not `--expect` (#587 X9)

**The machine (#587).** An entry may carry `phase` (one of `dyadlib.ORCH_PHASES`; its continuation lines the sub-keys
`unit`, `pr` (`<n> at <hex>`, repeating), `evidence`, `from`, `on`) and `note` (free text: the one field no table
derives). On a phased entry `waiting-on`, `next`, `since`, `question` and `phase` are written by `board advance` alone:
`waiting-on` and `next` are `derive(phase, holder)` and the guard fails a drift; `question` exists only in an asked
phase. An entry without `phase` behaves exactly as before. `owner` accumulates (`opened` adds the unit).

`dyad board` and `board set` warn when the file's last `writer` is not this session (an unphased entry only): two holders may be writing
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
import datetime, os, re, shlex
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "board", "agent", False
NAME, OWNER = "board entry", "Rule-3"
BOARD_REL = "d-work/board"
COS = "_cos"
FIELDS = ("holder", "phase", "owner", "waiting-on", "next", "since", "question", "promised", "note", "writer")   # #587: phase, note
COS_FIELDS = ("holder", "queue", "seats", "next", "since", "question", "promised", "writer")
REQUIRED = ("holder",)
CONT = "  "                                          # a continuation line's prefix
WAITING = re.compile(r"operator|unit \S+|external \S.*")
RETIRED_WAITING = "seat "                           # #604: `seat <name>`, removed in 1.0; refused naming `unit <name>`
KEY = re.compile(r"[a-z][a-z-]*")
CLI_FLAGS = dyadlib.cli_forms("board")   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
DROP, = CLI_FLAGS["set"].bare
USAGE = ("usage: dyad board | dyad board set <id>|_cos key=value… [--drop] | dyad board resume | dyad board phases | "
         "dyad board advance <id> [<id>…] <event> --expect <phase>|none [key=value…] [--said-file <path>] [--mirror <branch>]")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("holder-is-required-everywhere", lambda: all(k in FIELDS and k in COS_FIELDS for k in REQUIRED)),
    ("writer-is-a-key-of-both", lambda: "writer" in FIELDS and "writer" in COS_FIELDS),
    ("waiting-on-forms", lambda: all(WAITING.fullmatch(v) for v in ("operator", "unit counsel-015qiPLU", "external run 1"))
                                 and not WAITING.fullmatch("someone") and not WAITING.fullmatch(RETIRED_WAITING + "counsel-015qiPLU")),
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


parse_entry = parse   # the board's own reader, by a name no builder parameter shadows (#587: `parse` is the runner's there)


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


def retired_waiting(value: str) -> str | None:
    """#604 (#573 step 4): the refusal for a `waiting-on` in the removed `seat <name>` form, naming the form to write,
    else None. Never rewritten silently: a stored entry fails the guard and `board set` refuses it."""
    if not value.startswith(RETIRED_WAITING):
        return None
    rest = value[len(RETIRED_WAITING):].strip()
    form = f"unit {rest}" if WAITING.fullmatch(f"unit {rest}") else "unit <name>"   # never suggest a form WAITING refuses
    return f"`waiting-on: {value}` uses `seat <name>`, removed in dyad-operator 1.0; write `waiting-on: {form}` (#604)"


def check_entry(name: str, text: str, states: dict[int, str], rows: dict | None = None) -> list[str]:
    """One file's problems; `name` its stem, `states` row id -> state, `rows` row id -> Row (the phased entry's row
    checks; skipped without it). An entry with no `phase` is judged exactly as before #587."""
    where = f"board/{name}.md"
    if name != COS and not name.isdigit():
        return [f"{where}: not `<id>.md` or `{COS}.md`"]
    fields, problems = parse(text)
    msgs = [f"{where}: {p}" for p in problems]
    allowed = keys_for(name)
    msgs += [f"{where}: unknown key {k!r} (keys: {', '.join(allowed)})" for k in fields if k not in allowed]
    msgs += [f"{where}: '{k}' missing" for k in REQUIRED if not fields.get(k)]
    if "waiting-on" in fields and (r := retired_waiting(fields["waiting-on"])):
        msgs.append(f"{where}: {r}")
    elif "waiting-on" in fields and not WAITING.fullmatch(fields["waiting-on"]):
        msgs.append(f"{where}: 'waiting-on' is not `operator`, `unit <name>` or `external <ref>` ({fields['waiting-on']!r})")
    if "since" in fields and parse_since(fields["since"]) is None:
        msgs.append(f"{where}: 'since' is not an ISO-8601 date or time ({fields['since']!r})")
    if name.isdigit():
        state = states.get(int(name))
        if state is None:
            msgs.append(f"{where}: no row #{name} (Rule-20: an unresolved reference)")
        elif state in dyadlib.TERMINAL_STATES:
            msgs.append(f"warning: {where}: row #{name} is {state}; a stale entry — `dyad board set {name} --drop`")
    if "phase" in fields and name != COS:
        msgs += check_phased(name, fields, rows)
    return msgs


def check_phased(name: str, f: dict[str, str], rows: dict | None) -> list[str]:
    """#587 X1: a phased entry's derived fields are the table's output, its sub-keys well-formed and present for its
    phase, its question only in an asked phase; the ledger ahead of the board warns (the automaton catches up)."""
    where = f"board/{name}.md"
    try:
        p, sub = phase_of(f["phase"])
    except ValueError as e:
        return [f"{where}: 'phase' is malformed: {e}"]
    if p not in dyadlib.ORCH_PHASES:
        return [f"{where}: phase {p!r} is not one of {', '.join(dyadlib.ORCH_PHASES)}"]
    msgs = []
    bad_pr = [v for v in sub.get("pr", []) if not PR_HEAD.fullmatch(v)]
    msgs += [f"{where}: phase pr {v!r} is not `<n> at <7-40 hex>`" for v in bad_pr]
    if sub.get("evidence") and not HEX64.fullmatch(sub["evidence"][0]):
        msgs.append(f"{where}: phase evidence {sub['evidence'][0]!r} is not 64 hex")
    for k in ("unit",) + PHASE_REQUIRES.get(p, ()):
        if not sub.get(k):
            msgs.append(f"{where}: phase {p} needs sub-key {k!r}")
    if p == "held":
        if sub.get("from") and (sub["from"][0] not in dyadlib.ORCH_PHASES or sub["from"][0] == "held"):
            msgs.append(f"{where}: phase held: 'from' {sub['from'][0]!r} is not a phase other than held")
        if sub.get("on") and not WAITING.fullmatch(sub["on"][0]):
            msgs.append(f"{where}: phase held: 'on' {sub['on'][0]!r} is not a waiting-on form")
    if sub.get("unit") and sub["unit"][0] not in owners(f):
        msgs.append(f"{where}: phase unit {sub['unit'][0]} is not among the owners ({', '.join(owners(f)) or 'none'})")
    if not msgs and name.isdigit():
        want = derive(int(name), f)
        for k in ("waiting-on", "next"):
            if f.get(k, "") != want[k]:
                msgs.append(f"{where}: {k!r} is {f.get(k, '')!r}; phase {p} derives {want[k]!r} — dyad board advance is "
                            f"its only writer (#587 X1)")
    q = f.get("question", "")
    if p in dyadlib.ORCH_ASKED:
        last = (q.strip().splitlines() or [""])[-1]
        if not last.startswith("Y/N: ") or not re.search(rf"#{name}\b", last):
            msgs.append(f"{where}: phase {p} needs its question, a last line `Y/N: …` naming #{name}")
    elif q:
        msgs.append(f"{where}: a question outside an asked phase (phase {p}): `asked` writes it, every other event removes it")
    r = (rows or {}).get(int(name)) if name.isdigit() else None
    if r is not None:
        rg = rows_guard()
        es = [e for e in rg.entries(r.disposed) if not rg.is_ready(e)]
        od = rg.operative_done(r.disposed)
        if p in CATCH_UP_PLAN and r.state == "planned" and es and rg.PLAN_Y.match(es[-1]):
            msgs.append(f"warning: {where}: row #{name}'s plan-Y is recorded and the board is still at {p}: the "
                        f"ledger is ahead (the automaton catches up)")
        elif r.state == "planned" and p in ("planning", "plan-ready", "plan-asked"):
            msgs.append(f"warning: {where}: row #{name} is planned and the board is at {p}")
        if p in CATCH_UP_DONE and od:
            msgs.append(f"warning: {where}: row #{name}'s Done-Y is recorded and the board is still at {p}: the "
                        f"ledger is ahead (the automaton catches up)")
        elif p in ("building", "verifying") and od:
            prs = ", ".join(f"PR #{pr}" for _, pr, _, _ in rg.named_heads([r]) if pr) or "none"
            msgs.append(f"warning: {where}: row #{name}'s Y done is recorded outside done-asked (phase {p}); the board "
                        f"cannot follow — `dyad board advance {name} hold --expect {p} on=external merge {prs} note=…` "
                        f"or re-ask (#587)")
        if p == "landing" and not od:
            msgs.append(f"warning: {where}: phase landing and row #{name} carries no operative Y done")
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
    try:
        rows = {r.id: r for r in dyadlib.read_rows(root)}
    except (OSError, ValueError, KeyError):
        rows = {}
    msgs = []
    for p in files:
        msgs += check_entry(p.stem, p.read_text(errors="replace"), states, rows)
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
    drop = DROP in rest
    rest = [x for x in rest if x != DROP]
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
        if k == "waiting-on" and (r := retired_waiting(v)):
            raise Refused(r)
        if k == "waiting-on" and v and not WAITING.fullmatch(v):
            raise Refused(f"waiting-on is `operator`, `unit <name>` or `external <ref>`, not {v!r}")
        if k == "since" and v and parse_since(v) is None:
            raise Refused(f"since is an ISO-8601 date or time, not {v!r}")
        if k == "note" and v and dyadlib.load_guard("agent", "inbox").DISPOSITION.search(v):
            raise Refused("note is disposition-shaped (a `Y/N:` line or a ledger entry): the board carries information (#587 X2)")
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
        if "phase" in pairs and not old.get("phase"):
            raise Refused(f"{rel} carries no phase: a phase is born only by `dyad board advance` (#587 X1)")
        if old.get("phase"):
            derived = sorted(k for k in pairs if k in DERIVED)
            if derived:
                raise Refused(f"board/{name}.md carries phase {phase_name(old)}: its derived fields are written by "
                              f"`dyad board advance` (#587 X1); not {', '.join(derived)}")
        w = None if old.get("phase") else writer_warning(name, old, me)   # #587: units write a phased entry; --expect guards it
        if w:
            print(w, file=sys.stderr)
        new = merged(old, pairs, seat, me, now_iso())
        if old.get("phase") and name.isdigit():          # #587 X1: a holder change re-derives; the phase's `since` stays
            unit = first(phase_of(old["phase"])[1], "unit")
            if unit and unit not in owners(new):
                raise Refused(f"board/{name}.md's phase names unit {unit}: `owner` keeps it (#587)")
            new.update(derive(int(name), new))
            if old.get("since"):
                new["since"] = old["since"]
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
        ph = f"phase {phase_name(f)} " if f.get("phase") else ""
        out.append(f"#{n} {state:<8} {ph}waiting-on {f.get('waiting-on', '-')} for {age(f.get('since', ''), now)} | "
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
    out += [w for n, f in got if not f.get("phase") and (w := writer_warning(n, f, me))]   # #587: units write a phased one
    return out


def derived_queue(root: Path, got: list[tuple[str, dict[str, str]]] | None = None) -> dict[str, list[int]]:
    """#572 K4: the pending queue read from records instead of written to `_cos`: `plan-ready`, the open rows with a
    stored plan and no `Y plan` entry, not accreted under a mandate; `done-ready`, the live entries whose question is a
    Done question (`Done with`). Rule-3's counts, so no write keeps them."""
    got = load(root) if got is None else got
    plans = dyadlib.instance(root) / "d-work" / "plans"
    rows = dyadlib.read_rows(root)
    live = {r.id for r in rows if r.state not in dyadlib.TERMINAL_STATES}
    phased = {int(n): phase_name(f) for n, f in got if n.isdigit() and f.get("phase")}   # #587 X3: the phase says it
    plan_ready = sorted({r.id for r in rows if r.id not in phased and r.state == "open" and (plans / f"{r.id}.md").exists()
                         and " Y plan" not in f" {r.disposed}" and "mandate #" not in r.disposed}
                        | {i for i, p in phased.items() if p == "plan-ready" and i in live})
    done_ready = sorted({int(n) for n, f in got if n.isdigit() and int(n) not in phased and int(n) in live
                         and "Done with" in (f.get("question") or "")}
                        | {i for i, p in phased.items() if p == "done-ready" and i in live})
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
    seats = sorted({f["waiting-on"].split()[1] for _, f in live if f.get("waiting-on", "").startswith("unit ")}
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
        block(f"#{n}:" + (f" phase {phase_name(f)}" if f.get("phase") else ""), f, FIELDS)
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


# ---- the orchestration machine (d-work #587: X1 derived fields, X2 relays, X3 questions, X4 the answer, X9 --expect)
PHASE_SUBKEYS = ("unit", "pr", "evidence", "from", "on")
PR_HEAD = re.compile(r"(\d+) at ([0-9a-f]{7,40})")      # heads take 7-40 hex, as `rows.PR_AT` accepts
HEX64 = re.compile(r"[0-9a-f]{64}")
HEAD_HEX = re.compile(r"[0-9a-f]{7,40}")
DERIVED = ("phase", "waiting-on", "next", "since", "question")   # written by `board advance` alone on a phased entry
PHASE_REQUIRES = {                                       # phase -> the sub-keys it must carry beside `unit`
    "verifying": ("pr",), "landing": ("pr", "evidence"), "done-ready": ("evidence",), "done-asked": ("evidence",),
    "held": ("from", "on")}
ADVANCE_USAGE = ("usage: dyad board advance <id> [<id>…] <event> --expect <phase>|none [key=value…] "
                 "[--said-file <path>] [--mirror <branch>]")
MULTI_ID_EVENTS = ("asked", "answered-Y", "answered-N")
ASKED_KIND = {"plan-asked": "plan", "done-asked": "done"}
CATCH_UP_PLAN = ("plan-ready", "plan-asked")            # a hand-recorded Y plan is caught up from either (#587)
CATCH_UP_DONE = ("done-ready", "done-asked")            # a hand-recorded Y done likewise
ASKED_OF = {"plan-ready": "plan-asked", "done-ready": "done-asked"}   # the catch-up reads a *-ready entry as asked
BATCH_IDS = re.compile(r"\bbatch (#\d+(?:,#\d+)*)")
PAIR_KEYS = ("unit", "pr", "head", "evidence", "on", "note")


def phase_of(value: str) -> tuple[str, dict[str, list[str]]]:
    """(phase name, {sub-key: [values]}) from a `phase` value: its first line the name, each later line `key: value`
    (a stored value's lines lose their two-space prefix in `parse`; an indented one is read too). ValueError when the
    value is malformed: no name, a sub-line that is not `key: value`, an unknown sub-key, or one other than `pr`
    repeated."""
    first, *rest = (value or "").split("\n")
    name = first.strip()
    if not name or " " in name:
        raise ValueError(f"no phase name in {first!r}")
    sub: dict[str, list[str]] = {}
    for line in rest:
        t = line.strip()
        if not t:
            continue
        k, sep, v = t.partition(": ")
        if not sep or not v.strip():
            raise ValueError(f"sub-line {t!r} is not `key: value`")
        if k not in PHASE_SUBKEYS:
            raise ValueError(f"unknown sub-key {k!r} (sub-keys: {', '.join(PHASE_SUBKEYS)})")
        if k != "pr" and k in sub:
            raise ValueError(f"sub-key {k!r} repeated (only `pr` repeats)")
        sub.setdefault(k, []).append(v.strip())
    return name, sub


def phase_render(name: str, sub: dict[str, list[str]]) -> str:
    """The `phase` value: the name, then each sub-key in PHASE_SUBKEYS order (`render` indents the later lines)."""
    lines = [name]
    for k in PHASE_SUBKEYS:
        for v in sub.get(k, []):
            lines.append(f"{k}: {f'{v[0]} at {v[1]}' if isinstance(v, tuple) else v}")
    return "\n".join(lines)


def first(sub: dict[str, list[str]], k: str) -> str:
    return (sub.get(k) or [""])[0]


def pr_list(sub: dict[str, list[str]]) -> list[tuple[int, str]]:
    """The PRs a phase lists, in arrival order, as (number, head); a value not `<n> at <hex>` is skipped (the guard
    names it)."""
    return [(int(m[1]), m[2]) for v in sub.get("pr", []) if (m := PR_HEAD.fullmatch(v))]


def pr_add(sub: dict[str, list[str]], n: int, head: str) -> dict[str, list[str]]:
    """`sub` with PR `n` at `head`: a PR already listed has its head replaced in place, a new one is appended."""
    out = {k: list(v) for k, v in sub.items()}
    prs = pr_list(out)
    prs = [(p, head if p == n else h) for p, h in prs] if any(p == n for p, _ in prs) else prs + [(n, head)]
    out["pr"] = [f"{p} at {h}" for p, h in prs]
    return out


def prs_text(sub: dict[str, list[str]]) -> str:
    return ", ".join(f"PR #{n} at {h}" for n, h in pr_list(sub))


def merge_text(sub: dict[str, list[str]]) -> str:
    """The landing wait, exactly the string `automaton.pending_flip` writes (#572 K3)."""
    return "external merge " + ", ".join(f"PR #{n}" for n, _ in pr_list(sub))


DERIVE: dict[str, tuple[str, str]] = {   # phase -> (waiting-on template, next template)
    "planning":   ("unit {unit}",   "write plans/{id}.md; then: dyad board advance {id} plan-landed --expect planning"),
    "plan-ready": ("unit {holder}", "ask the plan question: dyad board advance {id} asked --expect plan-ready"),
    "plan-asked": ("operator",      "record the Operator's answer: dyad board advance <the question's ids> answered-Y|answered-N --expect plan-asked --said-file <F>"),
    "building":   ("unit {unit}",   "execute plans/{id}.md; then: dyad board advance {id} pr-up --expect building pr=<n> head=<sha>"),
    "verifying":  ("unit {holder}", "verify {prs} (dyad check --evidence on each head); then: dyad board advance {id} evidence-verified --expect verifying evidence=<sha256>"),
    "done-ready": ("unit {holder}", "ask the Done question: dyad board advance {id} asked --expect done-ready"),
    "done-asked": ("operator",      "record the Operator's answer: dyad board advance <the question's ids> answered-Y|answered-N --expect done-asked --said-file <F>"),
    "landing":    ("{merge}",       "the automaton merges {prs}, then closes the row"),
    "held":       ("{on}",          "held (see note): dyad board advance {id} release --expect held"),
}


def derive(rid: int, f: dict[str, str]) -> dict[str, str]:
    """{"waiting-on": …, "next": …} of a phased entry: read from `holder` and the phase's sub-keys only — never a
    row's title, an accreted row or `note` — so an unrelated commit can never make an entry drift (X1)."""
    name, sub = phase_of(f["phase"])
    wo, nx = DERIVE[name]
    vals = {"id": rid, "unit": first(sub, "unit"), "holder": f.get("holder", ""), "prs": prs_text(sub),
            "merge": merge_text(sub), "on": first(sub, "on")}
    return {"waiting-on": wo.format(**vals), "next": nx.format(**vals)}


def phase_name(f: dict[str, str]) -> str | None:
    """The entry's phase, None when it carries none; a malformed value reads as its first word (the guard names it)."""
    if not f.get("phase"):
        return None
    try:
        return phase_of(f["phase"])[0]
    except ValueError:
        return f["phase"].split("\n")[0].strip() or "?"


# ---- questions (X3): composed only by `asked`, read back by `answered-*` as the binding set (Rule-2, Binding)
def accreted_of(rid: int, rows: dict) -> list[int]:
    """The rows accreted under `rid`'s mandate: not terminal, a `disposed` holding `mandate #<rid>` and refs naming it
    (`parent #<rid>`, `#<rid>` or `<rid>`)."""
    names = {f"#{rid}", str(rid)}
    return sorted(r.id for r in rows.values() if r.id != rid and r.state not in dyadlib.TERMINAL_STATES
                  and re.search(rf"\bmandate #{rid}\b", r.disposed) and names & set(r.refs.replace("parent ", "").split()))


def union_prs(ids, entries: dict) -> list[int]:
    out = []
    for i in ids:
        for n, _ in pr_list(phase_of(entries[i]["phase"])[1]):
            if n not in out:
                out.append(n)
    return out


def question(kind: str, ids, entries: dict, rows: dict, pref: str | None) -> str:
    """The counter-prompt `asked` stores verbatim on every named entry (Rule-3's forms): `plan` — `Y/N: proceed with #a[,
    #b] as planned?`; `done` — `Y/N: Done with #a <title> (accreted #c, merges PR #w, #x)?`, each clause only when
    non-empty, or the batch `Y/N: Done with #a <ta> (accreted #c), #b <tb> (merges PR #w, #x)?` whose merges clause is
    the union in id order. PRs without heads (Rule-3 form). Refused with PRs unless `merge-disposition` is
    `with-done`: under `separate` the merge is its own question, asked by hand (#587 risk 6)."""
    ids = list(ids)
    if kind == "plan":
        return f"Y/N: proceed with {', '.join(f'#{i}' for i in ids)} as planned?"
    prs = union_prs(ids, entries)
    if prs and pref != "with-done":
        raise Refused(f"merge-disposition is {pref or 'unset'}, not with-done: a Done question naming PRs is not composed "
                      f"here; ask the merge and the Done by hand (#587)")
    merges = f"merges PR {', '.join(f'#{n}' for n in prs)}" if prs else ""
    def acc(a):
        got = accreted_of(a, rows)
        return f"accreted {', '.join(f'#{c}' for c in got)}" if got else ""
    if len(ids) == 1:
        a = ids[0]
        clauses = [c for c in (acc(a), merges) if c]
        return f"Y/N: Done with #{a} {rows[a].title}" + (f" ({', '.join(clauses)})" if clauses else "") + "?"
    parts = [f"#{a} {rows[a].title}" + (f" ({acc(a)})" if acc(a) else "") for a in ids]
    return "Y/N: Done with " + ", ".join(parts) + (f" ({merges})" if merges else "") + "?"


QUESTION_LINE = re.compile(r"Y/N: (?:proceed with (?P<plan>.*) as planned|Done with (?P<done>.*))\?")


def question_kind(q: str) -> str | None:
    m = QUESTION_LINE.fullmatch(((q or "").strip().splitlines() or [""])[-1])
    return None if m is None else "plan" if m["plan"] is not None else "done"


def ids_of(q: str) -> list[int]:
    """The ids a stored question names, read back: every `#<n>` of a plan question; of a Done question, every `#<n>`
    that opens an item at parenthesis depth 0 (a title holding `, #<n>` reads as one more id, so a binding check over
    it refuses rather than widens)."""
    m = QUESTION_LINE.fullmatch(((q or "").strip().splitlines() or [""])[-1])
    if m is None:
        return []
    if m["plan"] is not None:
        return [int(x) for x in re.findall(r"#(\d+)", m["plan"])]
    span, out, depth = m["done"], [], 0
    for i, c in enumerate(span):
        if c == "(":
            depth += 1
        elif c == ")":
            depth = max(0, depth - 1)
        elif c == "#" and depth == 0 and (i == 0 or span[i - 2:i] == ", ") and (mm := re.match(r"#(\d+)\b", span[i:])):
            out.append(int(mm[1]))
    return out


def merges_of(q: str) -> list[int]:
    """The PR numbers a stored Done question's merges clause names, [] when it has none."""
    got = re.findall(r"merges PR (#\d+(?:, #\d+)*)", ((q or "").strip().splitlines() or [""])[-1])
    return [int(x) for x in re.findall(r"\d+", got[-1])] if got else []


def accreted_in(q: str) -> list[int]:
    got = re.findall(r"accreted (#\d+(?:, #\d+)*)", ((q or "").strip().splitlines() or [""])[-1])
    return [int(x) for x in re.findall(r"\d+", got[-1])] if got else []


# ---- relays (X2): templates of the event's own fields; free text travels on the board (`note`), never in a body
NOTICE_BODY = None   # sentinel: the body is `automaton.notice_body` (the plan notice K2 and `inbox.handed_rows` read)
RELAYS: dict[tuple[str, str], tuple[str, str, str | None]] = {   # (event, target) -> (to, kind, body template)
    ("opened", "planning"):            ("unit", "relay", "row #{id} planning: write plans/{id}.md; advance plan-landed when it is on main"),
    ("plan-landed", "plan-ready"):     ("holder", "report", "row #{id} plan-ready: plans/{id}.md is on main; the plan question is owed"),
    ("answered-Y", "building"):        ("owners", "notice", NOTICE_BODY),   # K2's shape: one per owner, its own part
    ("answered-N", "planning"):        ("unit", "relay", "row #{id} planning: the plan was refused; read provenance/{id}.md and revise plans/{id}.md"),
    ("pr-up", "verifying"):            ("holder", "report", "row #{id} verifying: PR #{pr} at {head} is up from {sender}; verify {prs}"),
    ("evidence-verified", "done-ready"): ("holder", "report", "row #{id} done-ready: evidence {ev12} on {prs}; the Done question is owed"),
    ("evidence-failed", "building"):   ("unit", "relay", "row #{id} building: the evidence failed; the failing line is the board's note"),
    ("answered-Y", "landing"):         ("owners", "notice", "row #{id} landing: the Done answer is recorded on main; the automaton merges {prs}"),
    ("answered-Y", dyadlib.ORCH_DROP): ("owners", "notice", "row #{id} closed: the Done answer is recorded and the row is done"),
    ("answered-N", "building"):        ("unit", "relay", "row #{id} building: the Done was refused; read provenance/{id}.md"),
    ("hold", "held"):                  ("owners", "notice", "row #{id} held: see board/{id}.md note"),
    ("release", dyadlib.ORCH_FROM):    ("owners", "notice", "row #{id} released to {phase}"),
}
RELAY_SAMPLE = {"id": 587, "prs": "PR #650 at 9bbb5cc8, PR #651 at f35eb112", "pr": "651", "head": "f35eb112",
                "sender": "engineer-1537d8fb", "ev12": "0123456789ab", "part": "the verb", "phase": "plan-ready"}


def automaton():
    return dyadlib.load_module(dyadlib.PKG / "scripts" / "automaton.py", "automaton")


def relay_body(rid: int, event: str, target: str, entry: dict[str, str], sender: str, plan_text: str = "",
               pairs: dict[str, str] | None = None) -> tuple[str, str, str] | None:
    """(to-kind, message kind, body) of the relay `RELAYS` names for this transition, or None."""
    pairs = pairs or {}
    key = (event, dyadlib.ORCH_FROM if event == "release" else target)
    if key not in RELAYS:
        return None
    to, kind, tmpl = RELAYS[key]
    sub = phase_of(entry["phase"])[1] if entry.get("phase") else {}
    if tmpl is NOTICE_BODY:
        am = automaton()
        body = am.notice_body(rid, am.part_for(am.plan_parts(plan_text or ""), first(sub, "unit")))
    else:
        body = tmpl.format(id=rid, prs=prs_text(sub), pr=pairs.get("pr", ""), head=pairs.get("head", ""), sender=sender,
                           ev12=(first(sub, "evidence") or pairs.get("evidence", ""))[:12], phase=target, part="")
    return to, kind, body


def relay_lines(rid: int, event: str, target: str, entry: dict[str, str], sender: str, plan_text: str = "",
                pairs: dict[str, str] | None = None) -> list[str]:
    """The `post` batch lines of one transition (X2), shell-quoted: to the unit, the holder (a `pr-up` report cc'ing the
    other owners) or every owner, never to the sender itself; [] when the table names none or nobody is left."""
    key = (event, dyadlib.ORCH_FROM if event == "release" else target)
    if key in RELAYS and RELAYS[key][2] is NOTICE_BODY:   # #572 K2: each owner its own notice, quoting its own part
        am = automaton()
        parts, out = am.plan_parts(plan_text or ""), []
        for o in dict.fromkeys(owners(entry)):
            if o and o != sender:
                body = am.notice_body(rid, am.part_for(parts, o))
                if inbox().DISPOSITION.search(body):
                    raise Refused(f"the relay body for #{rid} {event} is disposition-shaped: {body!r} (#587 X2)")
                out.append(shlex.join(["post", o, "--row", str(rid), "--kind", RELAYS[key][1], body]))
        return out
    got = relay_body(rid, event, target, entry, sender, plan_text, pairs)
    if got is None:
        return []
    to, kind, body = got
    if inbox().DISPOSITION.search(body):                  # X2: checked before the first write, as the TREE_INVARIANT
        raise Refused(f"the relay body for #{rid} {event} is disposition-shaped: {body!r} (#587 X2)")
    sub = phase_of(entry["phase"])[1] if entry.get("phase") else {}
    holder = entry.get("holder", "")
    if to == "unit":
        recips = [first(sub, "unit")]
    elif to == "holder":
        recips = [holder] + ([o for o in owners(entry) if o not in (sender, holder)] if event == "pr-up" else [])
    else:
        recips = owners(entry)
    seen = []
    for r in recips:
        if r and r != sender and r not in seen:
            seen.append(r)
    if not seen:
        return []
    cc = [x for c in seen[1:] for x in ("--cc", c)]
    if kind == "relay":                                   # a relay goes to the one unit its entry names (#552)
        return [shlex.join(["post", r, "--row", str(rid), "--kind", kind, body]) for r in seen]
    return [shlex.join(["post", seen[0], "--row", str(rid), "--kind", kind, *cc, body])]


def inbox():
    return dyadlib.load_guard("agent", "inbox")


def rows_guard():
    return dyadlib.load_guard("agent", "rows")


def land_mod():
    return dyadlib.load_module(dyadlib.PKG / "scripts" / "land.py", "land")


# ---- a transition, pure (X1, X9)
def actor_ok(actor: str, entry: dict[str, str], sender: str) -> str | None:
    """Why `sender` may not fire an event of `actor` on `entry`, or None."""
    holder = entry.get("holder") or sender
    if actor == "home" and sender != holder:
        return f"a home event is the holder's ({holder}), not {sender}'s"
    if actor == "unit" and sender not in set(owners(entry)) | {entry.get("holder", "")}:
        return f"a unit event is an owner's or the holder's ({', '.join(owners(entry) + [entry.get('holder', '?')])}), not {sender}'s"
    if actor == "automaton":
        return "an automaton event never comes from the CLI"
    return None


def transition(rid: int, entry: dict[str, str], row, event: str, pairs: dict[str, str], sender: str, now: str,
               recorded: bool = False, question_text: str | None = None) -> tuple[str, dict[str, str] | None]:
    """(target, the new entry or None when it is dropped) of one event on one entry; Refused when the table does not
    allow it. `entry` is {} when absent; `pairs` the event's own fields; the new entry's `writer` is left to the
    caller. Pure: no file, no git."""
    cur = phase_name(entry)
    key = (cur, event)
    if key not in dyadlib.ORCH_EVENTS:
        legal = sorted(e for f, e in dyadlib.ORCH_EVENTS if f == cur and e != "closed")
        raise Refused(f"#{rid} is at {cur or 'no phase'}: {event} is not an event from there (legal: {', '.join(legal) or 'none'})")
    targets, actor, required = dyadlib.ORCH_EVENTS[key]
    if not recorded and (why := actor_ok(actor, entry, sender)):
        raise Refused(f"#{rid} {event}: {why} (#587)")
    missing = [r for r in required if r != "said-file" and not pairs.get(r)]
    if missing:
        raise Refused(f"#{rid} {event} needs {', '.join(f'{m}=' for m in missing)}")
    sub = phase_of(entry["phase"])[1] if cur else {}
    new = {k: v for k, v in entry.items() if k not in DERIVED}
    if cur is None:                                       # a birth, or the adoption of an unphased entry
        if entry:
            if "note" not in pairs and entry.get("next"):
                new["note"] = entry["next"]
            if event == "plan-landed" and (row is None or row.state != "open"
                                           or any(rows_guard().PLAN_Y.match(e) for e in rows_guard().entries(row.disposed))):
                raise Refused(f"#{rid}: plan-landed adopts only an open row with no Y plan (row is "
                              f"{row.state if row else 'absent'}); a planned row is adopted by pr-up (#587)")
        else:
            new["holder"] = sender
        sub = {"unit": [pairs.get("unit") or sender]}
    target = targets[0]
    if event == "answered-Y" and cur == "done-asked" and not pr_list(sub):
        target = dyadlib.ORCH_DROP
    if event == "opened":
        sub["unit"] = [pairs["unit"]]
        if pairs["unit"] not in owners(new):
            new["owner"] = "; ".join(x for x in (new.get("owner", "").strip(), pairs["unit"]) if x)
    elif event == "pr-up":
        sub = pr_add(sub, int(pairs["pr"]), pairs["head"])
    elif event == "evidence-verified":
        sub["evidence"] = [pairs["evidence"]]
    elif event == "evidence-failed" or (event == "answered-N" and cur == "done-asked"):
        sub.pop("evidence", None)
    elif event == "hold":
        sub["from"], sub["on"] = [cur], [pairs["on"]]
    elif event == "release":
        target = dyadlib.orch_release_to(first(sub, "from"))
        sub.pop("from", None); sub.pop("on", None)
    if "note" in pairs:
        new["note"] = pairs["note"]
    if target == dyadlib.ORCH_DROP:
        return target, None
    new["phase"] = phase_render(target, sub)
    new.update(derive(rid, new))
    new["since"] = entry.get("since", now) if target == cur and entry.get("since") else now
    if event == "asked":
        new["question"] = question_text or ""
    if not new.get("question"):
        new.pop("question", None)
    if phase_of(new["phase"])[1].get("unit", [""])[0] not in owners(new):
        new["owner"] = "; ".join(x for x in (new.get("owner", "").strip(), first(phase_of(new["phase"])[1], "unit")) if x)
    return target, new


def ledger_lines(ids, entries: dict, rows: dict, event: str, said_abs: str, pref: str | None = None) -> list[str]:
    """The `dwork state` lines of an answer (X4), composed from the phase and the question the machine stored at
    `asked`, never typed: one per named row, each carrying the same `--said-file`, so the one `Y` is written into each
    record (Rule-3 Batch, Rule-7). [] for any other event."""
    if event not in ("answered-Y", "answered-N"):
        return []
    ids = list(ids)
    q = entries[ids[0]].get("question", "")
    kind = question_kind(q)
    yn = "Y" if event == "answered-Y" else "N"
    batch = f"batch {','.join(f'#{i}' for i in ids)}"
    out = []
    if kind == "plan":
        d = f"Y plan ({batch})" if len(ids) > 1 and yn == "Y" else f"{yn} plan"
        for i in ids:
            out.append(shlex.join(["state", str(i), "planned" if yn == "Y" else rows[i].state, "-d", d, "--said-file", said_abs]))
        return out
    prs = []
    for i in ids:
        for n, h in pr_list(phase_of(entries[i]["phase"])[1]):
            if n not in [p for p, _ in prs]:
                prs.append((n, h))
    merges = ", ".join(f"PR #{n} at {h}" for n, h in prs)
    if yn == "N":
        for i in ids:
            out.append(shlex.join(["state", str(i), rows[i].state, "-d", "N done", "--said-file", said_abs]))
        return out
    # the accreted sets come from the rows the question was composed from, never re-parsed from its text (a title may
    # hold `accreted #n`); a stored question that no longer matches them is refused, as the merges drift is
    acc = {i: accreted_of(i, rows) for i in ids}
    if q != question("done", ids, entries, rows, pref):
        raise Refused(f"the stored question no longer matches the rows ("
                      + "; ".join(f"#{i} accreted {' '.join(f'#{c}' for c in acc[i]) or 'none'}" for i in ids)
                      + "): ask again (Rule-2, Binding)")
    def accl(i):
        return [f"accreted {', '.join(f'#{c}' for c in acc[i])}"] if acc[i] else []
    for i in ids:
        clauses = ([batch] if len(ids) > 1 else []) + accl(i) + ([f"merges {merges}"] if merges else [])
        d = "Y done" + (f" ({', '.join(clauses)})" if clauses else "")
        out.append(shlex.join(["state", str(i), "done" if not prs else rows[i].state, "-d", d, "--said-file", said_abs]))
        if not prs:                                       # done at once: its accreted rows close under its mandate now,
            out += [shlex.join(["state", str(c), "done", "--mandate", str(i)]) for c in acc[i]]   # as close_landed would
    return out


# ---- the builder (X4, X9): one code path for every event, run on every try in land's worktree
def parse_advance(a: list[str]) -> tuple[list[int], str, dict[str, str], str | None, str | None, str | None]:
    """(ids, event, pairs, expect, said-file made absolute, mirror) from the argv; every refusal here is before any
    fetch."""
    ids, i = [], 0
    while i < len(a) and a[i].isdigit():
        ids.append(int(a[i])); i += 1
    if not ids or i >= len(a) or a[i].startswith("-") or "=" in a[i]:
        raise Refused(ADVANCE_USAGE)
    event, rest = a[i], a[i + 1:]
    if event not in dyadlib.ORCH_CLI_EVENTS:
        raise Refused(f"{event!r} is not an event (events: {', '.join(sorted(dyadlib.ORCH_CLI_EVENTS))})")
    if len(ids) > 1 and event not in MULTI_ID_EVENTS:
        raise Refused(f"only {', '.join(MULTI_ID_EVENTS)} take several ids, not {event}")
    if len(set(ids)) != len(ids):
        raise Refused("an id named twice")
    expect = said = mirror = None
    pairs: dict[str, str] = {}
    j = 0
    while j < len(rest):
        x = rest[j]
        if x in ("--expect", "--said-file", "--mirror"):
            if j + 1 >= len(rest):
                raise Refused(f"{x} needs a value")
            v = rest[j + 1]; j += 2
            if x == "--expect":
                expect = v
            elif x == "--said-file":
                said = os.path.abspath(v)
            else:
                mirror = v
            continue
        k, sep, v = x.partition("=")
        if not sep or k not in PAIR_KEYS:
            raise Refused(f"{x!r} is not one of {', '.join(f'{p}=' for p in PAIR_KEYS)}, --expect, --said-file or --mirror")
        if k in pairs:
            raise Refused(f"{k}= given twice")
        pairs[k] = v; j += 1
    if expect is None:
        raise Refused(ADVANCE_USAGE)
    if expect != "none" and expect not in dyadlib.ORCH_PHASES:
        raise Refused(f"--expect is a phase ({', '.join(dyadlib.ORCH_PHASES)}) or none, not {expect!r}")
    key = (None if expect == "none" else expect, event)
    if key not in dyadlib.ORCH_EVENTS:
        legal = sorted(e for f, e in dyadlib.ORCH_EVENTS if f == key[0] and e != "closed")
        raise Refused(f"{event} is not an event from {expect} (legal: {', '.join(legal) or 'none'})")
    _, _, required = dyadlib.ORCH_EVENTS[key]
    allowed_keys = (set(required) - {"said-file"}) | {"note"} | ({"unit"} if key[0] is None else set())   # adoption
    extra = sorted(set(pairs) - allowed_keys)
    if extra:
        raise Refused(f"{event} does not take {', '.join(f'{k}=' for k in extra)} (it takes {', '.join(sorted(f'{k}=' for k in allowed_keys))})")
    missing = [r for r in required if r != "said-file" and not pairs.get(r)]
    if missing:
        raise Refused(f"{event} needs {', '.join(f'{m}=' for m in missing)}")
    if ("said-file" in required) != (said is not None):
        raise Refused(f"--said-file is {'required by' if 'said-file' in required else 'refused by'} {event}: the Operator's "
                      f"words enter only with an answer (Rule-7)")
    if said is not None and not Path(said).is_file():
        raise Refused(f"--said-file {said} is not a file")
    for k, v in pairs.items():
        if k == "on" and (r := retired_waiting(v)):
            raise Refused(f"on={v!r}: {r}")
        bad = {"unit": not inbox().SEAT.fullmatch(v), "pr": not v.isdigit(), "head": not HEAD_HEX.fullmatch(v),
               "evidence": not HEX64.fullmatch(v), "on": not WAITING.fullmatch(v), "note": not v.strip()}[k]
        if bad:
            raise Refused(f"{k}={v!r} is not {dict(unit='a seat', pr='a PR number', head='7-40 hex', evidence='64 hex', on='`operator`, `unit <name>` or `external <ref>`', note='text')[k]}")
    if "note" in pairs and inbox().DISPOSITION.search(pairs["note"]):
        raise Refused("note= is disposition-shaped (a `Y/N:` line or a ledger entry): the board carries information, "
                      "never authority (#587 X2)")
    return ids, event, pairs, expect, said, mirror


def trace_lines(ids, wt: Path, inst: str, repo: Path) -> tuple[list[str], list[str]]:
    """Under `dwork-trace: always`, (the `land` line of each Done-`Y` row's trace that is in the caller's checkout and
    not identical on origin/main, their repo-relative paths); Refused, in `trace_refusal`'s words, when one is in
    neither."""
    rg = rows_guard()
    if dyadlib.preference(rg.TRACE_KEY, wt) != rg.TRACE_ALWAYS:
        return [], []
    out, rels = [], []
    for rid in ids:
        rel = f"{inst}/d-work/traces/{rid}.md"
        mine, there = Path(repo) / rel, wt / rel
        if mine.is_file() and not (there.is_file() and there.read_bytes() == mine.read_bytes()):
            out.append(shlex.join(["land", str(mine)])); rels.append(rel)
        elif not mine.is_file() and not there.is_file():
            raise Refused(f"a `Y done` entry is recorded with its trace under `dwork-trace: always` (Rule-3 Completion: the "
                          f"Done record commit carries it, #465), and {rel} does not exist; write it first: "
                          f"run dyad dwork trace {rid} --out first, and re-run")
    return out, rels


def answered_already(ids, rows: dict, event: str, said_abs: str | None, wt: Path, inst: str, words,
                     expect: str | None = None) -> bool:
    """A re-run of an answer that already landed: each row's last `disposed` entry is today's answer of the kind the
    expected phase asks (`plan` for plan-asked, `done` for done-asked), with these words last in its record (the
    `already landed` test of `land`, read without the question it consumed)."""
    if event not in MULTI_ID_EVENTS[1:] or said_abs is None:
        return False
    kind = ASKED_KIND.get(expect or "")
    if kind is None:
        return False
    import datetime
    today = dyadlib.utc_date()
    said = words({"--said-file": said_abs}, "said")
    yn = "Y" if event == "answered-Y" else "N"
    for rid in ids:
        r = rows.get(rid)
        es = rows_guard().entries(r.disposed) if r else []
        rec = [e for e in land_mod().record_at(wt, inst, rid) if e["kind"] == "disposition"]
        if not (es and re.match(rf"{today} {yn} {kind}\b", es[-1]) and rec and rec[-1]["text"] == said):
            return False
    return True


def recorded_prs(row) -> list[int]:
    return sorted(int(pr) for _, pr, _, _ in rows_guard().named_heads([row]) if pr)


def recorded_done_heads(rid: int, row, sub: dict[str, list[str]]) -> list[tuple[int, str]] | None:
    """The (PR, head) pairs a hand-recorded operative `Y done` names, when they cover this entry: every PR the phase
    lists is among them, and any other they name is allowed only by a batch entry naming this row (the batch's
    merges are the union, and every row of it waits on the whole union, as `board advance` writes it). None when
    they do not cover it: the board cannot follow, and the guard's warning stands. Pure."""
    rg = rows_guard()
    named = [(int(pr), h) for _, pr, h, _ in rg.named_heads([row]) if pr]
    ns, own = {n for n, _ in named}, {n for n, _ in pr_list(sub)}
    if not own <= ns:
        return None
    if ns - own:
        m = BATCH_IDS.search(rg.operative_done(row.disposed) or "")
        if m is None or rid not in {int(x) for x in re.findall(r"\d+", m[1])}:
            return None
    return named


def batch_union(ids, entries: dict) -> dict:
    """{id: entry} for a Done batch whose union of PRs is not empty: each entry's phase lists every PR of the union
    (its own head kept for its own), so a row with no PR of its own waits on the batch's merges in `landing` as its
    ledger entry does, rather than being dropped while the row stays open. {} when the union is empty."""
    union = []
    for i in ids:
        for n, h in pr_list(phase_of(entries[i]["phase"])[1]):
            if n not in [p for p, _ in union]:
                union.append((n, h))
    if not union:
        return {}
    out = {}
    for rid in ids:
        nm, sub = phase_of(entries[rid]["phase"])
        mine = {p for p, _ in pr_list(sub)}
        for n, h in union:
            if n not in mine:
                sub = pr_add(sub, n, h)
        out[rid] = {**entries[rid], "phase": phase_render(nm, sub)}
    return out


def advance_builder(ids, event: str, pairs: dict[str, str], expect: str | None, said_abs: str | None, inst: str,
                    repo: Path, value_flags, parse, words, sender: str, recorded: bool = False, landed=None, ran=None):
    """land's builder for one `board advance` (section 7 of plan #587 PR2). On every try, in land's worktree on a freshly
    fetched origin/main: read and refuse (`--expect`, the table, the actor, the fields, the binding set); compose the
    ledger lines, write the board, compose the relays; then run the composed text through `dwork batch`'s own parser
    and builder, so every refusal of `dwork state` and `inbox post` holds. A refusal raises before `git commit`; the
    next `land.prepare` discards what was written. `recorded` (the automaton's catch-up only, never the CLI) writes no
    ledger line, checks no trace and waives the actor."""
    L = land_mod()
    me = sessions().writer()
    landed = [] if landed is None else landed
    ran = [] if ran is None else ran
    exp = None if expect in (None, "none") else expect
    aexp = ASKED_OF.get(exp, exp) if recorded else exp    # the catch-up reads a *-ready entry as its asked phase (#587)
    def build(wt: Path):
        import datetime
        ran[:] = []                                       # a try that runs no batch rings nobody (a retry's stale posts)
        rows = {r.id: r for r in dyadlib.read_rows(wt)}
        bdir = wt / inst / BOARD_REL
        old_text, entries = {}, {}
        for rid in ids:
            p = bdir / f"{rid}.md"
            old_text[rid] = p.read_text() if p.is_file() else None
            entries[rid] = parse_entry(old_text[rid])[0] if old_text[rid] is not None else {}
        frm = phase_name(entries[ids[0]]) or "none"       # the subject names the phase as stored
        for rid in ids:
            r, cur = rows.get(rid), phase_name(entries[rid])
            if (cur != exp or (r is not None and r.state in dyadlib.TERMINAL_STATES)) and not recorded \
                    and answered_already(ids, rows, event, said_abs, wt, inst, words, exp):
                raise Refused(f"already landed: the {event} on {', '.join(f'#{i}' for i in ids)} is the rows' last entry with "
                              f"these words on origin/main; nothing pushed")
            if r is None:
                raise Refused(f"no row #{rid} on origin/main")
            if r.state in dyadlib.TERMINAL_STATES:
                raise Refused(f"row #{rid} is {r.state} on origin/main: a terminal row has no board entry")
            if cur != exp:
                raise Refused(f"phase moved: #{rid} is {cur or 'none'} on origin/main, expected {expect}; nothing landed — "
                              f"re-read dyad board and re-decide (#587 X9)")
            if aexp != exp:                               # recorded only: the transition runs from the asked phase
                nm, sub = phase_of(entries[rid]["phase"])
                entries[rid] = {**entries[rid], "phase": phase_render(aexp, sub)}
                continue
            _, actor, _ = dyadlib.ORCH_EVENTS[(cur, event)]
            if not recorded and (why := actor_ok(actor, entries[rid], sender)):
                raise Refused(f"#{rid} {event}: {why} (#587)")
        # event preconditions
        if event == "plan-landed":
            for rid in ids:
                if not (wt / inst / "d-work" / "plans" / f"{rid}.md").is_file():
                    raise Refused(f"#{rid} plan-landed: plans/{rid}.md is not on origin/main; land it first (`dyad dwork land`)")
        qtext = None
        if event == "asked":
            kind = "plan" if exp == "plan-ready" else "done"
            qtext = question(kind, ids, entries, rows, dyadlib.preference("merge-disposition", wt))
        if event in MULTI_ID_EVENTS[1:]:
            qs = {entries[rid].get("question", "") for rid in ids}
            q = next(iter(qs))
            if not recorded:
                if len(qs) != 1 or sorted(ids) != sorted(ids_of(q)):
                    raise Refused(f"the Y binds to the question asked: {q.splitlines()[-1] if q else '(none stored)'} "
                                  f"— answer exactly its ids, {' '.join(str(i) for i in ids_of(q)) or 'none'} (Rule-2, Binding)")
                if exp == "done-asked" and sorted(merges_of(q)) != sorted(union_prs(ids, entries)):
                    raise Refused(f"the stored question names PR(s) {merges_of(q)} and the phases list {union_prs(ids, entries)}: "
                                  f"the question no longer matches the entries; re-ask (#587, fail-loud)")
            elif aexp == "done-asked":                   # the catch-up: the ledger's heads govern (Rule-2, Binding)
                rid = ids[0]
                sub = phase_of(entries[rid]["phase"])[1]
                named = recorded_done_heads(rid, rows[rid], sub)
                if named is None:
                    raise Refused(f"#{rid}: the recorded Y done names PR(s) {recorded_prs(rows[rid])}, the phase lists "
                                  f"{sorted(n for n, _ in pr_list(sub))} and no batch covers the rest; no catch-up")
                for n, h in named:
                    sub = pr_add(sub, n, h)
                entries[rid] = {**entries[rid], "phase": phase_render(phase_of(entries[rid]["phase"])[0], sub)}
        if event == "answered-Y" and aexp == "done-asked" and not recorded and len(ids) > 1:
            entries.update(batch_union(ids, entries))     # a Done batch with PRs: every row waits on the whole union
        now = now_iso()
        results = {rid: transition(rid, entries[rid], rows[rid], event, pairs, sender, now, recorded, qtext) for rid in ids}
        lines = []
        if not recorded:
            if event == "answered-Y" and aexp == "done-asked":
                tl, rels = trace_lines(ids, wt, inst, repo)
                lines += tl
                landed[:] = rels
            lines += ledger_lines(ids, entries, rows, event, said_abs or "", dyadlib.preference("merge-disposition", wt))
        changed, paths = [], []
        for rid in ids:
            target, new = results[rid]
            p = bdir / f"{rid}.md"
            if new is None:
                if p.exists():
                    p.unlink(); changed.append(rid)
            else:
                new["writer"] = me
                text = render(new, FIELDS)
                if text != old_text[rid]:
                    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text); changed.append(rid)
            paths.append(p.relative_to(wt).as_posix())
        for rid in ids:
            target, new = results[rid]
            plan_text = (wt / inst / "d-work" / "plans" / f"{rid}.md")
            lines += relay_lines(rid, event, target, new if new is not None else entries[rid], sender,
                                 plan_text.read_text(errors="replace") if plan_text.is_file() else "", pairs)
        subj = advance_subject(ids, event, frm, results[ids[0]][0])
        head = (qtext + "\n") if qtext else ""
        if not lines:
            if not changed:
                raise Refused(f"already landed: {', '.join(paths)} on origin/main is identical; nothing pushed")
            return sorted(set(L.written(wt))), subj, head.rstrip("\n")
        parsed = L.read_batch_text("\n".join(lines) + "\n", repo, inst, value_flags, parse)
        L.done_order(parsed, dyadlib.utc_date())
        try:
            _, bsubj, out = L.batch_builder(repo, parsed, inst, words, ran)(wt)
        except L.Refused as e:
            if str(e).startswith("already landed") and changed:
                return sorted(set(L.written(wt))), subj, head.rstrip("\n")
            raise
        return sorted(set(L.written(wt))), advance_subject(ids, event, frm,
                                                           results[ids[0]][0], bsubj.removeprefix("ledger: batch ")), (head + out).strip("\n")
    return build


def advance_subject(ids, event: str, frm: str, to: str, parts: str = "") -> str:
    """`ledger: board advance #<ids> <event> (<from> -> <to>)` plus the batch's parts: one line, cut to land's
    SUBJECT_MAX, every `d-work #` masked (a ledger-only commit claims no d-work, Rule-3 Ledger), as `batch_subject`."""
    L = land_mod()
    s = " ".join((f"ledger: board advance {', '.join(f'#{i}' for i in ids)} {event} ({frm} -> {to})"
                  + (f", {parts}" if parts else "")).split())
    if len(s) > L.SUBJECT_MAX:
        s = s[:L.SUBJECT_MAX - 1].rstrip(", ") + "…"
    return dyadlib.load_guard("agent", "prs").CITE.sub(r"#\1", s)


def cmd_advance(a: list[str], repo: Path, value_flags, dwork_args, words) -> int:
    """`dyad board advance`: exit 0 landed, 1 refused (one `refused: …` line, nothing landed), 2 usage."""
    L = land_mod()
    try:
        ids, event, pairs, expect, said, mirror = parse_advance(a)
        L.check_mirror(repo, mirror)
        inst = dyadlib.instance_rel(repo)
        if inst is None:
            raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree; a board write lands a tracked store")
        sender = os.environ.get("DYAD_SESSION") or ""
        if not inbox().SEAT.fullmatch(sender):
            raise Refused("DYAD_SESSION names no seat: an event is fired from a seat (#587)")
        landed, ran = [], []
        build = advance_builder(ids, event, pairs, expect, said, inst, repo, value_flags, dwork_args, words, sender,
                                landed=landed, ran=ran)
        rc = L.land(repo, inst, mirror, build, "board advance", landed)
        ring = L.ring_list(ran)
        if rc == 0 and ring:
            print(f"ring: {', '.join(ring)} (a doorbell is the session's act, #586 X4)")
        return rc
    except (Refused, L.Refused) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2 if str(e) == ADVANCE_USAGE else 1


def phases_lines() -> list[str]:
    """`dyad board phases`: the machine as data (DoD part 1) — each phase's derived waiting-on and next, then every
    event of `dyadlib.ORCH_EVENTS`."""
    out = ["phase | waiting-on | next"]
    out += [f"{p} | {DERIVE[p][0]} | {DERIVE[p][1]}" for p in dyadlib.ORCH_PHASES]
    out += ["", "from | event | to | actor | required fields"]
    order = {p: i for i, p in enumerate(dyadlib.ORCH_PHASES)}
    for (f, e), (ts, actor, req) in sorted(dyadlib.ORCH_EVENTS.items(), key=lambda kv: (-1 if kv[0][0] is None else order[kv[0][0]], kv[0][1])):
        out.append(f"{f or 'none'} | {e} | {' or '.join(ts)} | {actor} | {', '.join(req) or '-'}")
    return out


def cli(a: list[str], repo: Path | None = None) -> int:
    repo = Path(repo or dyadlib.repo_root())
    if a and a[0] in ("-h", "--help"):
        print(__doc__); return 0
    if a and a[0] == "set":
        return cmd_set(a[1:], repo)
    if a and a[0] == "resume" and len(a) == 1:
        print("\n".join(resume_lines(repo))); return 0
    if a == ["phases"]:
        print("\n".join(phases_lines())); return 0
    if a and a[0] == "advance":                       # the runner routes here with its own readers (package.cmd_board)
        run = dyadlib.runner_module()
        return cmd_advance(a[1:], repo, run.DWORK_VALUE_FLAGS, run.dwork_args, run.words)
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


INVARIANTS += [   # #587: the machine's derived fields (crafts/syseng/rules/invariants.md)
    ("derive-covers-phases", lambda: set(DERIVE) == set(dyadlib.ORCH_PHASES)),
    ("landing-is-k3-form", lambda: derive(1, {"holder": "h", "phase": "landing\n  unit: u\n  pr: 1 at abc1234\n  evidence: " + "0" * 64})["waiting-on"] == "external merge PR #1"),
    ("derived-waiting-on-forms", lambda: all(WAITING.fullmatch(derive(1, {"holder": "h", "phase": phase_render(p, {"unit": ["u"], "pr": ["1 at abc1234"], "on": ["operator"]})})["waiting-on"]) for p in dyadlib.ORCH_PHASES)),
    ("subkeys-distinct", lambda: len(set(PHASE_SUBKEYS)) == len(PHASE_SUBKEYS)),
    ("phase-and-note-are-fields", lambda: {"phase", "note"} <= set(FIELDS) and not {"phase", "note"} & set(COS_FIELDS)),
    ("relays-name-known-events", lambda: all(e in dyadlib.ORCH_EVENT_NAMES and (t in dyadlib.ORCH_PHASES or t in (dyadlib.ORCH_DROP, dyadlib.ORCH_FROM)) for e, t in RELAYS)),
]
TREE_INVARIANTS = [   # loads inbox and automaton, so never at import (crafts/syseng/rules/invariants.md)
    ("relays-are-information", lambda: not any(inbox().DISPOSITION.search(relay_body(587, e, t if t != dyadlib.ORCH_FROM else "plan-ready",
        {"holder": "home-1", "owner": "unit-1; unit-2", "phase": "verifying\nunit: unit-1\npr: 650 at 9bbb5cc8\nevidence: " + "0" * 64},
        "unit-2", "parts: unit-1: " + RELAY_SAMPLE["part"], {"pr": RELAY_SAMPLE["pr"], "head": RELAY_SAMPLE["head"]})[2]) for e, t in RELAYS)),
]

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
