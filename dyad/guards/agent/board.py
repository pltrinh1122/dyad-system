#!/usr/bin/env python3
"""Board guard and CLI (entity `board`, agent corpus; Rule-3 owns the orchestration it records, Rule-16 the store
beside the rows; placed per Rule-11 property 1; d-work #535, cos mode P1). Kernel: Python 3.12+, git.

What the cos holds in flight lived only in its chat, so a hop of the mode from one session to another lost it (plan
#535): the questions owed to the Operator, the work dispatched to seats, the gates, the relays, the promises, the seat
table. The board store puts it on `main`:

  <instance>/d-work/board/<id>.md   one per row not terminal with orchestration in flight
  <instance>/d-work/board/_cos.md   the cross-row items: the seat table, the last question asked, the promises (the
                                    pending queue is derived at read since #572 K4; a stored `queue` is still read)
  <instance>/d-work/board/_cos-<operator>.md
                                    the same, for the cabinet `program-<operator>` (#594): one `_cos` file per cabinet

**Cabinets (#594).** A cabinet is one operator's leader and the board it keeps: `program` (the solo leader, and every
seat under `organization: flat`) or `program-<operator>` (a member pair's leader, `program-<operator>-<hp>`), the
leader's seat name without its `-<hp>` (`cabinet_of`). A row's entry carries an optional `cabinet`, absent meaning
`program`, written by `board set` alone when it creates the entry and never typed or changed; `_cos.md` is `program`'s
cross-row file, `_cos-<operator>.md` another cabinet's (`is_cos`). A leader writes only its own cabinet's entries and
`_cos` file (`board set _cos` resolves to it); another seat may write an existing entry, its cabinet kept, and only
`queue`/`seats` of a `_cos` file whose `seats` names it; a non-leader's first write on a new entry files it under the
cabinet whose `seats` names it (refused when two cabinets exist and not exactly one does). `--drop` of a row's entry
stays cabinet-agnostic, and `board advance` keeps the same fence and files a birth the same way. A seat is matched to
a `_cos` file's `seats` by full name, its seat key only as the fallback (two cabinets' `engineer-<hp>` units share
one key). The writer is `DYAD_SESSION`, or with none set the `holder=<seat>` the pairs name. `resume` and `dyad board`
read the resumer's cabinet only.

Each file is `key: value` lines; a value continues on the lines after it that start with two spaces (so a question
is kept verbatim, newlines and all); blank and `#` lines are skipped. Keys of a row's file: `holder` (the cos session
that holds the mode), `owner` (the seat doing the work, and its session id), `waiting-on` (`operator` | `unit <name>`
| `external <ref>`), `next` (the next act), `since`, `question` (verbatim, when the Operator owes one), `promised`
(follow-ups named to the Operator), and `writer`, which `board set` writes and nobody types — the harness session
that wrote the file last (`sessions.writer`, Rule-16's writer pattern, #350). `_cos.md` takes `queue` and `seats` in
place of `owner` and `waiting-on`, and `release-plan` (#625: the backlog grooming play-book's release plan, which
the `promotion` criterion reads). Unlike a row the store is overwritten freely; its history is git's.

  dyad board                         render the board from the working tree: one line per entry, oldest wait first
  dyad board set <id>|_cos[-<operator>] key=value… [--drop]
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
  dyad board draft <id> [--out <file>]
                                     read-only: the Done skeleton of a row phased at `done-ready` (#587 X7) — the DoD
                                     quoted from plans/<id>.md, each PR's zone and head, the evidence sha256 and its
                                     brief when stored here, the accreted rows, the trace, orchestrate's sections
                                     marked, and the question `asked` would store; printed, or written to a file outside
                                     the work tree; never posted (the inbox refuses a disposition-shaped body)
  dyad board groom                   read-only: the backlog grooming report (#625, scripts/groom.py, dispatched by
                                     package.py): each backlog row's facts — refs, nearest board anchor, promises,
                                     plan roots, its hygiene lines — then each craft's last tag; never a judgement

**The machine (#587).** An entry may carry `phase` (one of `dyadlib.ORCH_PHASES`; its continuation lines the sub-keys
`unit`, `pr` (`<n> at <hex>`, repeating), `evidence`, `from`, `on`) and `note` (free text: the one field no table
derives). On a phased entry `waiting-on`, `next`, `since`, `question` and `phase` are written by `board advance` alone:
`waiting-on` and `next` are `derive(phase, holder)` and the guard fails a drift; `question` exists only in an asked
phase. An entry without `phase` behaves exactly as before. `owner` accumulates (`opened` adds the unit). One event has no
effect (`dyadlib.ORCH_NO_EFFECT`, #587 S10): `read`, a self-loop on every phase that changes neither the phase, the
derived fields nor `since`; `dyad inbox read <message>…` fires it in the land that writes the message's marker, and
`board advance` refuses it.

`dyad board` and `board set` warn when the file's last `writer` is not this session (an unphased entry only): two holders may be writing
(plan #535 attack 6; the lease, #537, arbitrates later). A warning, never a refusal. The cos writes the board before
it sends the message or asks the question it records (write-ahead, plan #535 attack 3).

The check (`check_package`): every file is `<id>.md` or `_cos[-<operator>].md`, well-formed, keys known and not repeated, `holder`
present, `waiting-on`, `since` and `cabinet` in their forms, and each id a row (fails otherwise, Rule-20); a row that is
terminal is a stale entry, a warning. Not checked: staleness by age, and append-only (the store is overwritten).
  board.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("board.py: Python 3.12+ required")
import datetime, os, re, shlex, subprocess, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "board", "agent", False
NAME, OWNER = "board entry", "Rule-3"
BOARD_REL = "d-work/board"
COS = "_cos"
FIELDS = ("holder", "cabinet", "phase", "owner", "waiting-on", "next", "since", "question", "promised", "note", "writer")   # #587: phase, note
COS_FIELDS = ("holder", "queue", "seats", "next", "since", "question", "promised", "release-plan", "writer")   # #625: release-plan
REQUIRED = ("holder",)
CABINET = re.compile(r"program(?:-[a-z0-9]+)*")      # #594: `program` or `program-<operator>`; never a seat's `-<hp>`,
                                                     # so an operator segment of eight hex is no cabinet (sessions.name_problems)
SOLO = "program"                                     # the cabinet an entry without `cabinet` is filed under
HP_TAIL = re.compile(r"-[0-9a-f]{8}$")               # a seat name's `-<hp>`, which `sessions._seat_key` strips
CONT = "  "                                          # a continuation line's prefix
WAITING = re.compile(r"operator|unit \S+|external \S.*")
RETIRED_WAITING = "seat "                           # #604: `seat <name>`, removed in 1.0; refused naming `unit <name>`
KEY = re.compile(r"[a-z][a-z-]*")
CLI_FLAGS = dyadlib.cli_forms("board")   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
DROP, = CLI_FLAGS["set"].bare
OUT, DECISIONS_OUT = CLI_FLAGS["draft"].value_flags   # #587 X7: the skeleton's file, never under the work tree; #648
PROSE_SLOT = "TODO plan-departure: facts | outcome"   # #648: the draft's fixed slot for a prose ruling
USAGE = ("usage: dyad board | dyad board set <id>|_cos[-<operator>] key=value… [--drop] | dyad board resume | dyad board phases | "
         "dyad board advance <id> [<id>…] <event> --expect <phase>|none [key=value…] [--said-file <path>] [--mirror <branch>] | "
         "dyad board draft <id> [--out <file>] | dyad board groom")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("holder-is-required-everywhere", lambda: all(k in FIELDS and k in COS_FIELDS for k in REQUIRED)),
    ("writer-is-a-key-of-both", lambda: "writer" in FIELDS and "writer" in COS_FIELDS),
    ("waiting-on-forms", lambda: all(WAITING.fullmatch(v) for v in ("operator", "unit counsel-015qiPLU", "external run 1"))
                                 and not WAITING.fullmatch("someone") and not WAITING.fullmatch(RETIRED_WAITING + "counsel-015qiPLU")),
    ("store-under-d-work", lambda: BOARD_REL.startswith("d-work/")),
    ("cabinet-form", lambda: all(CABINET.fullmatch(v) for v in (SOLO, "program-bob"))
                             and not any(CABINET.fullmatch(v) for v in ("someone", "program-", "Program"))),
    ("cabinet-is-a-field-of-entries-only", lambda: "cabinet" in FIELDS and "cabinet" not in COS_FIELDS),
    ("cos-names-its-cabinet", lambda: [cos_cabinet(n) for n in (COS, COS + "-bob", COS + "-bob-cccccccc", "_cosx", "5")]
                                      == [SOLO, "program-bob", None, None, None]
                              and cos_name(cos_cabinet(COS + "-bob")) == COS + "-bob" and cos_name(SOLO) == COS),
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
    return COS_FIELDS if is_cos(name) else FIELDS


# ---- cabinets (#594)
def cos_cabinet(name: str) -> str | None:
    """The cabinet a cross-row file's stem names — `_cos` -> `program`, `_cos-<operator>` -> `program-<operator>` — or
    None when the stem is no `_cos` file."""
    if name == COS:
        return SOLO
    if name.startswith(COS + "-") and valid_cabinet(SOLO + name[len(COS):]):
        return SOLO + name[len(COS):]
    return None


PROMISE_SPLIT = re.compile(r";\s+(?=\d{4}-\d{2}-\d{2} |incident|finding)")   # #651: a promise opens a date, or the word
INCIDENT = re.compile(r"^(?:\d{4}-\d{2}-\d{2} )?incident")                  # #651 A1: the entries the fence reads


def promises(value: str) -> list[str]:
    """The entries of a `promised` value (#651). Entries are `;`-separated, but an entry may hold `;` itself, so the
    value splits only where `; ` is followed by a date, `incident` or `finding`, the forms the home opens an entry
    with. A promise of another form that follows an incident stays part of that incident's text."""
    return [e.strip() for e in PROMISE_SPLIT.split(" ".join((value or "").split())) if e.strip()]


def promised_incidents(repo: Path) -> list[tuple[str, str]]:
    """(file stem, entry) for every `promised` entry of every cabinet's cross-row file (`_cos*.md`) that opens
    `<date> incident` or `incident`: an incident promised for the log and not yet in it (#651, Rule-3 Incidents). It
    reads the board, never the log: an entry stays here until the home removes it."""
    d, out = store(repo), []
    for f in sorted(d.glob(f"{COS}*.md")) if d.is_dir() else []:
        if not is_cos(f.stem):
            continue
        fields = parse(f.read_text(errors="replace"))[0]
        out += [(f.stem, e) for e in promises(fields.get("promised", "")) if INCIDENT.match(e)]
    return out


def names_row(entry: str, rid: int) -> bool:
    return re.search(rf"#{rid}(?!\d)", entry) is not None


def is_cos(name: str) -> bool:
    """True when `name` is a cabinet's cross-row file: `_cos` or `_cos-<operator>` (K8: the one predicate every reader
    that skips the cross-row file uses before `int(name)`)."""
    return cos_cabinet(name) is not None


def cos_name(cabinet: str) -> str:
    """The cross-row file's stem of `cabinet`: `_cos` for `program`, `_cos-<operator>` for `program-<operator>`."""
    return COS + cabinet[len(SOLO):]


def valid_cabinet(v: str) -> bool:
    """A cabinet value in its form and with no `-<hp>` tail: a seat key (`sessions._seat_key(v) == v`, the tree
    invariant `hp-tail-is-the-seat-keys`), never a seat name."""
    return bool(CABINET.fullmatch(v or "")) and not HP_TAIL.search(v)


def entry_cabinet(f: dict[str, str]) -> str:
    """The cabinet an entry is filed under: its `cabinet`, absent meaning `program` (zero migration)."""
    return f.get("cabinet") or SOLO


def cabinet_of(seat: str | None, root: Path | None = None) -> str | None:
    """The cabinet `seat` leads, or None: under `organization: flat` every seat (and none) is `program`'s; under `m4` a seat whose
    function is the leader function leads its seat key (`program-<hp>` -> `program`, `program-<operator>-<hp>` ->
    `program-<operator>`), any other seat none (K4)."""
    s = sessions()
    if s.organization(root) != "m4":
        return SOLO
    if not seat:
        return None
    parsed = s.parse_seat(seat)
    if parsed is None or parsed["function"] != s.LEADER_FUNCTION:
        return None
    key = s._seat_key(seat)
    return key if valid_cabinet(key) else None


def names_seat(cos: dict[str, str], seat: str | None, exact: bool = False) -> bool:
    """True when a `_cos` file's `seats` names `seat`: by its full name, or — unless `exact` — by its seat key (the key
    outlives a hop)."""
    if not seat:
        return False
    key = sessions()._seat_key
    return any(o == seat or (not exact and key(o) == key(seat))
               for o in owners({"owner": cos.get("seats", "").replace("\n", ";")}))


def naming_cabinets(seat: str | None, coses: dict[str, dict[str, str]]) -> tuple[list[str], bool]:
    """(the cabinets whose `seats` name `seat`, whether by full name): the full-name matches when any `_cos` file holds
    one, else the seat-key matches. Two cabinets' units of one function share a seat key (`engineer-aaaaaaaa`,
    `engineer-bbbbbbbb`), so the key is only the fallback for a seat no file names in full (#594)."""
    exact = sorted(c for c, f in coses.items() if names_seat(f, seat, exact=True))
    if exact or not seat:
        return exact, True
    return sorted(c for c, f in coses.items() if names_seat(f, seat)), False


def filing_cabinet(seat: str | None, coses: dict[str, dict[str, str]]) -> str:
    """K7: the cabinet a non-leader's first write on a new entry is filed under, from `coses` ({cabinet: its `_cos`
    fields}): with no `_cos` file `program`, with one its cabinet (a departure from plan #594's K7, which said
    `program`: a board holding only `_cos-<operator>.md` is that cabinet's); with two or more the one whose `seats`
    names the seat in full, else the one whose `seats` hold its seat key when that key carries a topic
    (`function-topic`; a bare function's key is shared across cabinets) — Refused when none or several do."""
    if len(coses) <= 1:
        return next(iter(coses), SOLO)
    naming, exact = naming_cabinets(seat, coses)
    parsed = sessions().parse_seat(seat) if seat else None
    if not exact and not (parsed and parsed["topic"]):
        naming = []
    if len(naming) != 1:
        raise Refused(f"{seat or 'this seat'} is named by the seats of {', '.join(naming) if naming else 'no cabinet'} "
                      f"among {', '.join(sorted(coses))}: a new entry is filed under exactly one cabinet; ask its "
                      f"leader to write it, or to list this seat in its `_cos` seats (#594 K7)")
    return naming[0]


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
    if not is_cos(name) and not name.isdigit():
        return [f"{where}: not `<id>.md` or `{COS}[-<operator>].md`"]
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
    if "cabinet" in fields and not valid_cabinet(fields["cabinet"]):
        msgs.append(f"{where}: 'cabinet' is not `program` or `program-<operator>` with no `-<hp>` ({fields['cabinet']!r}, #594)")
    if name.isdigit():
        state = states.get(int(name))
        if state is None:
            msgs.append(f"{where}: no row #{name} (Rule-20: an unresolved reference)")
        elif state in dyadlib.TERMINAL_STATES:
            msgs.append(f"warning: {where}: row #{name} is {state}; a stale entry — `dyad board set {name} --drop`")
        elif (q := unclassed_question(fields)):
            msgs.append(f"warning: {where}: its question {q[:60]!r} is a `Y/N:` of no form dmc:disposition-request lists, "
                        f"so Awaiting you counts nothing for it (#646)")
    if "phase" in fields and not is_cos(name):
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
    return msgs + seat_table_problems(files)


def seat_table_problems(files: list[Path]) -> list[str]:
    """#587 S3: a cabinet's seat table (`_cos`, or `_cos-<operator>`, #594) is hand-written, so a phased entry's owner or
    unit its own cabinet's table omits is a warning — the replayed slip had orchestrate routed by `opened` while the
    table `resume` announces from still lacked it. Silent for a cabinet whose cross-row file holds no `seats` (a fresh
    install, or a flat organization)."""
    by = {p.stem: parse(p.read_text(errors="replace"))[0] for p in files}
    out = []
    for name, f in sorted(by.items()):
        if is_cos(name) or "phase" not in f:
            continue
        table = by.get(cos_name(f.get("cabinet") or SOLO), {}).get("seats", "")
        if not table.strip():
            continue
        seated = {item.split()[0] for item in table.replace("\n", ";").split(";") if item.split()}
        try:
            unit = first(phase_of(f["phase"])[1], "unit")
        except ValueError:
            continue
        for s in dict.fromkeys(owners(f) + ([unit] if unit else [])):
            if s not in seated:
                cos = cos_name(f.get("cabinet") or SOLO)
                out.append(f"warning: board/{name}.md: {s} owns this entry and is missing from the `{cos}` seat table — "
                           f"`dyad board set {cos} seats=…` adds it (#587 S3)")
    return out


def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(entries(root or dyadlib.repo_root()))} board file(s)"


def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    d = store(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    return {"store": f"{rel}/<id>.md and {rel}/{COS}[-<operator>].md",
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
    """(name, pairs, drop) from `<id>|_cos[-<operator>] key=value… [--drop]`."""
    if not a:
        raise Refused(USAGE)
    name, rest = a[0], a[1:]
    if not is_cos(name) and not name.isdigit():
        raise Refused(f"{name!r} is not a row id or {COS}[-<operator>]")
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
        if k in ("writer", "cabinet"):
            raise Refused(f"`{k}` is written by `board set` itself, never typed"
                          + (" (#594: filed once, when the entry is created)" if k == "cabinet" else ""))
        if k not in keys_for(name):
            raise Refused(f"unknown key {k!r} for {name} (keys: {', '.join(k for k in keys_for(name) if k not in ('writer', 'cabinet'))})")
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
    actor = seat or pairs.get("holder") or None           # no DYAD_SESSION: the `holder=<seat>` path names the writer
    def build(wt: Path):
        mine = cabinet_of(actor, wt)
        target = cos_name(mine) if name == COS and mine else name   # `board set _cos` is the writer's own cabinet's
        path = wt / inst / BOARD_REL / f"{target}.md"
        rel = path.relative_to(wt).as_posix()
        old = parse(path.read_text())[0] if path.exists() else {}
        cabinet_fence(target, old, pairs, drop, actor, mine, cos_files(wt / inst / BOARD_REL))
        if drop:
            if not path.exists():
                raise Refused(f"already landed: {rel} is not on origin/main; nothing pushed")
            path.unlink()
            return [rel], f"ledger: board {target} dropped", ""
        if target.isdigit():
            row = next((r for r in dyadlib.read_rows(wt) if r.id == int(target)), None)
            if row is None:
                raise Refused(f"no row #{target} on origin/main")
            if row.state in dyadlib.TERMINAL_STATES:
                raise Refused(f"row #{target} is {row.state} on origin/main: a terminal row has no board entry")
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
        if target.isdigit() and not old:                 # #594 K7: filed once, by code, when the entry is created
            cab = mine or filing_cabinet(actor, cos_files(wt / inst / BOARD_REL))
            if cab != SOLO:
                new["cabinet"] = cab
        if old.get("phase") and name.isdigit():          # #587 X1: a holder change re-derives; the phase's `since` stays
            unit = first(phase_of(old["phase"])[1], "unit")
            if unit and unit not in owners(new):
                raise Refused(f"board/{name}.md's phase names unit {unit}: `owner` keeps it (#587)")
            new.update(derive(int(name), new))
            if old.get("since"):
                new["since"] = old["since"]
        if not new.get("holder"):
            raise Refused("no holder: set DYAD_SESSION or pass holder=<seat>")
        text = render(new, keys_for(target))
        if path.exists() and path.read_text() == text:
            raise Refused(f"already landed: {rel} on origin/main is identical; nothing pushed")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return [rel], f"ledger: board {target} ({', '.join(sorted(pairs))})", ""
    return build


def cos_files(d: Path) -> dict[str, dict[str, str]]:
    """{cabinet: its `_cos` file's fields} for every cross-row file in the board directory `d`."""
    return {cos_cabinet(p.stem): parse(p.read_text(errors="replace"))[0]
            for p in (sorted(d.glob("*.md")) if d.is_dir() else []) if is_cos(p.stem)}


def cabinet_fence(name: str, old: dict[str, str], pairs: dict[str, str], drop: bool, seat: str | None,
                  mine: str | None, coses: dict[str, dict[str, str]] | None = None) -> None:
    """K6: Refused when the writer may not write `name`. A leader (`mine`) writes only its own cabinet's `_cos` file
    and entries; another seat may write an existing entry (its cabinet kept) and only `queue`/`seats` of a `_cos` file
    whose `seats` names it in full, or by its seat key when no other cabinet's `seats` (`coses`, every `_cos` file;
    `{name's cabinet: old}` without it) hold that key. `--drop` of a row's entry is cabinet-agnostic: a terminal row
    owes nothing."""
    cc = cos_cabinet(name)
    if cc is None:
        if drop or not old or mine is None or entry_cabinet(old) == mine:
            return
        raise Refused(f"board/{name}.md is filed under cabinet {entry_cabinet(old)}, and {seat} leads {mine}: a leader "
                      f"writes only its own cabinet's entries (#594 K6)")
    if mine is not None:
        if mine != cc:
            raise Refused(f"board/{name}.md is cabinet {cc}'s, and {seat} leads {mine}: a leader writes only its own "
                          f"cabinet's `_cos` file ({cos_name(mine)}, #594 K6)")
        return
    extra = sorted(set(pairs) - {"queue", "seats"})
    naming, exact = naming_cabinets(seat, {**(coses or {}), cc: old})
    if drop or extra or cc not in naming or not (exact or naming == [cc]):
        raise Refused(f"board/{name}.md is cabinet {cc}'s and {seat or 'this seat'} leads none: another seat writes only "
                      f"`queue` or `seats` of a `_cos` file whose `seats` names it"
                      + (f" (not {', '.join(extra)})" if extra else "") + " (#594 K6; set DYAD_SESSION to the leader's "
                      "seat, or with none pass holder=<the leader's seat>)")


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


def viewer_cabinet(root: Path) -> str:
    """The cabinet `dyad board` and `resume` read: the one `DYAD_SESSION` leads, `program` for any other seat."""
    return cabinet_of(os.environ.get("DYAD_SESSION") or None, root) or SOLO


def split_cabinets(got: list[tuple[str, dict[str, str]]], cab: str):
    """(this cabinet's `_cos` fields, its row entries, the other cabinets' row entries) of a loaded board."""
    cos = dict(got).get(cos_name(cab), {})
    rows = [(n, f) for n, f in got if not is_cos(n)]
    return cos, [(n, f) for n, f in rows if entry_cabinet(f) == cab], [(n, f) for n, f in rows if entry_cabinet(f) != cab]


def board_lines(root: Path, now: datetime.datetime | None = None) -> list[str]:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    me = sessions().writer()
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    on = dyadlib.slugs_on(root)                                    # #622: read once
    L = lambda n: dyadlib.row_label(int(n), rows, on)
    got = load(root)
    cab = viewer_cabinet(root)
    cos, items, others = split_cabinets(got, cab)
    items.sort(key=lambda nf: parse_since(nf[1].get("since", "")) or now)
    out = [f"board: {len(items)} entr{'y' if len(items) == 1 else 'ies'}, holder {cos.get('holder') or '?'} "
           f"(read from the working tree; `git pull` first for main's)"]
    for n, f in items:
        r = rows.get(int(n))
        state, title = (r.state, r.title) if r else ("?", "")
        ph = f"phase {phase_name(f)} " if f.get("phase") else ""
        out.append(f"{L(n)} {state:<8} {ph}waiting-on {f.get('waiting-on', '-')} for {age(f.get('since', ''), now)} | "
                   f"owner {f.get('owner', '-')} | next: {(f.get('next') or '-').splitlines()[0]} | {title[:60]}")
        if f.get("question"):
            out.append(f"    question: {f['question'].splitlines()[-1]}")
    if others:                                            # #594: one count line, only when another cabinet holds any
        by = {}
        for n, f in others:
            by.setdefault(entry_cabinet(f), []).append(n)
        out.append(f"{len(others)} entr{'y' if len(others) == 1 else 'ies'} on other cabinets' boards ("
                   + "; ".join(f"{c}: {' '.join(L(n) for n in sorted(ns, key=int))}" for c, ns in sorted(by.items())) + ")")
    out.append(closing_line(root, got, cab))
    if cos:
        for k in ("queue", "seats", "question"):
            if cos.get(k):
                out.append(f"{cos_name(cab)} {k}: {cos[k].splitlines()[-1] if k == 'question' else ' / '.join(cos[k].splitlines())}")
    live = [i for i, r in rows.items() if r.state in ("open", "planned", "blocked")]
    missing = sorted(set(live) - {int(n) for n, _ in items + others})
    out.append(f"{len(missing)} open, planned or blocked row(s) carry no board entry")
    mine = {n for n, _ in items} | {cos_name(cab)}
    out += [w for n, f in got if n in mine and not f.get("phase") and (w := writer_warning(n, f, me))]   # #587: units write a phased one
    return out


def derived_queue(root: Path, got: list[tuple[str, dict[str, str]]] | None = None,
                  cabinet: str | None = None) -> dict[str, list[int]]:
    """#572 K4: the pending queue read from records instead of written to `_cos`: `plan-ready`, the open rows with a
    stored plan and no `Y plan` entry, not accreted under a mandate; `done-ready`, the live entries whose question is a
    Done question (`Done with`). Rule-3's counts, so no write keeps them. With `cabinet` (#594 K10), that cabinet's
    share: a row with an entry counts to its entry's cabinet, a row with none to `program`."""
    got = load(root) if got is None else got
    if cabinet is not None:
        filed = {int(n): entry_cabinet(f) for n, f in got if n.isdigit()}
        q = derived_queue(root, got)
        return {k: [i for i in v if filed.get(i, SOLO) == cabinet] for k, v in q.items()}
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


# ---- the closing line (d-work #646): the questions the operator owes, read from the questions the board records
CLOSING_KEY, CLOSING_VALUES, CLOSING_DEFAULT = "awaiting-you", ("on", "off"), "on"   # plan #646 revision 2
# dmc:disposition-request (#646 revision 3): what kind of request for the operator's disposition a recorded question is,
# the phase over the form, `none` the default; the outcome names and groups are the record's
REQUEST_PHASES = {"intent-asked": "intent", "plan-asked": "plan", "done-asked": "done"}
REQUEST_FORMS = (("Y/N: archive", "retirement"), ("Y/N: admit as precedents", "precedent"), ("Y/N: merge", "merge"),
                 ("Y/N: release", "release"), ("Y/N: run", "destructive"))
REQUEST_GROUPS = (("d-work", ("intent", "plan", "done", "retirement", "precedent")),
                  ("merge", ("merge", "release", "destructive")))
REQUEST_NONE = "none"
AWAITING_KINDS = tuple(k for _, ks in REQUEST_GROUPS for k in ks)
PR_REF = re.compile(r"\bPR #(\d+)")


def disposition_request(phase: str | None, question: str | None) -> str:
    """dmc:disposition-request (#646): the kind of request a board entry records. A phased entry is classed by its phase
    alone (intent-asked → intent, plan-asked → plan, done-asked → done, any other phase → none); an unphased one by the
    form its stored question's last line opens (`Y/N: archive` → retirement, `Y/N: admit as precedents` → precedent,
    `Y/N: merge` → merge, `Y/N: release` → release, `Y/N: run` → destructive); `none` otherwise, which counts nothing.
    `waiting-on` is never an input: a wait with no question owes no answer (#503)."""
    if phase:
        return REQUEST_PHASES.get(phase, REQUEST_NONE)
    lines = (question or "").strip().splitlines()
    last = lines[-1].strip() if lines else ""
    return next((kind for form, kind in REQUEST_FORMS if re.match(rf"{re.escape(form)}(?![\w-])", last)), REQUEST_NONE)


def asked_kind(f: dict[str, str]) -> str | None:
    """The disposition request a live entry records (`disposition_request` over its phase and question), None for none."""
    kind = disposition_request(phase_name(f) if f.get("phase") else None, f.get("question"))
    return None if kind == REQUEST_NONE else kind


def unclassed_question(f: dict[str, str]) -> str | None:
    """The last line of an unphased entry's question when it is a `Y/N:` question of no listed form: the record's default,
    which counts nothing and so is a warning (a question the operator owes that `Awaiting you` cannot count)."""
    if f.get("phase"):
        return None
    lines = (f.get("question") or "").strip().splitlines()
    last = lines[-1].strip() if lines else ""
    return last if last.startswith("Y/N:") and asked_kind(f) is None else None


def awaiting(root: Path, got: list[tuple[str, dict[str, str]]] | None = None,
             cabinet: str | None = None) -> list[tuple[str, str, list[int]]]:
    """[(kind, question, row ids)]: each question asked and not answered, once however many rows a batch names, in
    AWAITING_KINDS order then by first row; with `cabinet`, that cabinet's entries alone (#594)."""
    got = load(root) if got is None else got
    live = {r.id for r in dyadlib.read_rows(root) if r.state not in dyadlib.TERMINAL_STATES}
    groups: dict[tuple[str, str], list[int]] = {}
    for n, f in got:
        if not n.isdigit() or int(n) not in live or (cabinet is not None and entry_cabinet(f) != cabinet):
            continue
        kind = asked_kind(f)
        if kind:
            q = (f.get("question") or "").strip()
            groups.setdefault((kind, q or f"#{n}"), []).append(int(n))
    out = [(k, q, sorted(ids)) for (k, q), ids in groups.items()]
    return sorted(out, key=lambda t: (AWAITING_KINDS.index(t[0]), t[2][0]))


def intent_ready(root: Path, got: list[tuple[str, dict[str, str]]] | None = None) -> list[int]:
    """Under `intent-reading: on`: the open rows a prompt opened (its record's entry 1 a `prompt`) that hold no `Y intent`
    and no `Y plan`, are not accreted, and carry no phased entry (so no intent question asked)."""
    got = load(root) if got is None else got
    phased = {int(n) for n, f in got if n.isdigit() and f.get("phase")}
    prov = dyadlib.instance(root) / "d-work" / "provenance"
    out = []
    for r in dyadlib.read_rows(root):
        if r.state != "open" or r.id in phased or "mandate #" in r.disposed:
            continue
        if re.search(r"\bY (?:intent|plan)\b", r.disposed or ""):
            continue
        p = prov / f"{r.id}.md"
        if p.is_file() and re.search(r"(?m)^## 1 prompt\b", p.read_text(errors="ignore")):
            out.append(r.id)
    return sorted(out)


def awaiting_line(root: Path, got: list[tuple[str, dict[str, str]]] | None = None, cabinet: str | None = None) -> str:
    """`Awaiting you: d-work <n> <kind> (#id…), …; merge <n> (PR #…), <n> release (#id…), ….` — the questions asked and
    not answered by dmc:disposition-request's groups, d-work first, each group and kind only when non-zero, a kind named
    after its count unless it is the group's own name, a merge counted by the PR numbers its questions name — or
    `Awaiting you: nothing.`; then ` Coming: <n> <kind>, ….` from the derived queue, intent-ready included under
    `intent-reading: on` (#646)."""
    got = load(root) if got is None else got
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    on = dyadlib.slugs_on(root)
    L = lambda i: dyadlib.row_label(i, rows, on)
    by: dict[str, list[tuple[str, list[int]]]] = {}
    for kind, q, ids in awaiting(root, got, cabinet):
        by.setdefault(kind, []).append((q, ids))
    groups = []
    for group, kinds in REQUEST_GROUPS:
        items = []
        for kind in kinds:
            if not (qs := by.get(kind)):
                continue
            prs = sorted({int(p) for q, _ in qs for p in PR_REF.findall(q)}) if kind == "merge" else []
            refs = " ".join(f"PR #{p}" for p in prs) if prs else " ".join(L(i) for i in sorted({i for _, ids in qs for i in ids}))
            items.append(f"{len(qs)}{'' if kind == group else ' ' + kind} ({refs})")
        if items:
            groups.append(f"{group} " + ", ".join(items))
    line = "Awaiting you: " + ("; ".join(groups) if groups else "nothing") + "."
    q = derived_queue(root, got, cabinet)
    if (dyadlib.preference("intent-reading", root) or "").strip() == "on":
        filed = {int(n): entry_cabinet(f) for n, f in got if n.isdigit()}
        q = {"intent-ready": [i for i in intent_ready(root, got) if cabinet is None or filed.get(i, SOLO) == cabinet], **q}
    coming = [f"{len(v)} {k}" for k, v in q.items() if v]
    return line + (f" Coming: {', '.join(coming)}." if coming else "")


def closing_line(root: Path, got: list[tuple[str, dict[str, str]]] | None = None, cabinet: str | None = None) -> str:
    """The board's last count line: `awaiting_line` under the preference `awaiting-you: on`, which an absent key reads,
    and the derived queue's line under `off` (plan #646 revision 2)."""
    v = (dyadlib.preference(CLOSING_KEY, root) or CLOSING_DEFAULT).strip()
    if v == "off":
        return queue_line(derived_queue(root, got, cabinet))
    return awaiting_line(root, got, cabinet)


def owners(f: dict[str, str]) -> list[str]:
    """Every seat an entry's `owner` names: `<seat> [<session>]` parts separated by `;` (co-owners, #551)."""
    return [part.split()[0] for part in f.get("owner", "").split(";") if part.split()]


def resume_view(root: Path) -> dict:
    """What a new holder resumes from, as data (`resume_lines` prints it; a caller acts on it):
    - `cabinet` (the resumer's, #594), `cos` (its `_cos` file), `live` and `stale` entries of that cabinet (`stale`: the row is terminal or gone, #547);
    - `owed` (the live entries waiting on the Operator), `gates` (on an external ref) and `seats` (every seat a live
      entry waits on or names as an owner, co-owners included, #551);
    - `unread`: this seat's unread inbox messages (#536)."""
    got = load(root)
    try:                                                   # #622: the rows read once, for the states and the labels
        rows = {r.id: r for r in dyadlib.read_rows(root)}
    except (OSError, ValueError, KeyError):
        rows = {}
    states = {i: r.state for i, r in rows.items()}
    cab = viewer_cabinet(root)
    cos, items, _ = split_cabinets(got, cab)               # #594: the resumer's cabinet only (S13)
    stale = [(n, f) for n, f in items if states.get(int(n)) in dyadlib.TERMINAL_STATES or int(n) not in states]
    live = [(n, f) for n, f in items if (n, f) not in stale]
    seats = sorted({f["waiting-on"].split()[1] for _, f in live if f.get("waiting-on", "").startswith("unit ")}
                   | {o for _, f in live for o in owners(f)})
    seat = os.environ.get("DYAD_SESSION") or None
    return {"cabinet": cab, "cos": cos, "live": live, "stale": stale, "states": states, "rows": rows,
            "slugs": dyadlib.slugs_on(root),
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
    L = lambda n: dyadlib.row_label(int(n), v["rows"], v["slugs"])   # #622; the stall block below stays bare (Q4)
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
    out.append(closing_line(root, None, v["cabinet"]))
    if cos:
        block(f"{cos_name(v['cabinet'])}:", cos, COS_FIELDS)
    for n, f in v["live"]:
        block(f"{L(n)}:" + (f" phase {phase_name(f)}" if f.get("phase") else ""), f, FIELDS)
    for n, f in v["stale"]:
        out.append(f"{L(n)}: stale — row #{n} is {v['states'].get(int(n), 'not a row')}; nothing here is owed "
                   f"(`dyad board set {n} --drop`, #547)")
    out.append(f"owed to the Operator ({len(v['owed'])}): re-present each question verbatim, or report it pending")
    for n, f in v["owed"]:
        out.append(f"  {L(n)} since {f.get('since', '?')}:")
        out += [f"    {line}" for line in (f.get("question") or "(no question recorded)").split("\n")]
    out.append(f"external gates ({len(v['gates'])}): " + ("; ".join(f"{L(n)} {w}" for n, w in v["gates"]) or "none"))
    out.append(f"announce to ({len(v['seats'])}): {', '.join(v['seats']) or 'none'}" + (f"; seat table: {' / '.join(cos['seats'].splitlines())}" if cos.get("seats") else ""))
    if v["seats"]:
        now = datetime.datetime.now(datetime.timezone.utc)
        out.append("last ledger act (presence `seen`, information only, #567): " + ", ".join(
            f"{s} {age(v['last_act'][s], now) if v['last_act'].get(s) else 'none'}" for s in v["seats"]))
    out += stall_block(root, v["cabinet"])
    out.append("then: `dyad board set _cos holder=<this seat>` before any other act (write-ahead)")
    return out


def stall_block(root: Path, cabinet: str | None) -> list[str]:
    """#617: the stall findings the sweep no longer posts, read from the ledger at this checkout's HEAD
    (`automaton.stall_lines`): heads not landed, corroboration, a stale board, the work in flight of the resumer's
    cabinet, and the backlog's hygiene. Information only; a reading that fails says so in one line, never a crash."""
    try:
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
        lines = automaton().stall_lines(root, base, cabinet=cabinet)
    except Exception as e:                               # a read for the home: unreadable is a line, never a crash
        return [f"stalls: not read ({type(e).__name__})"]
    return [f"stalls ({len(lines)}, read from the ledger at {base[:12]}; information, the home judges):"] + [f"  {l}" for l in lines]


# ---- the orchestration machine (d-work #587: X1 derived fields, X2 relays, X3 questions, X4 the answer, X9 --expect)
PHASE_SUBKEYS = ("unit", "pr", "evidence", "from", "on")
PR_HEAD = re.compile(r"(\d+) at ([0-9a-f]{7,40})")      # a stored head reads 7-40 hex, as `rows.PR_AT` accepts: history
HEX64 = re.compile(r"[0-9a-f]{64}")
HEAD_HEX = re.compile(r"[0-9a-f]{40}")                  # #661: a head written by `pr-up`/`head-moved` is full, as merge.FULL_SHA
DERIVED = ("phase", "waiting-on", "next", "since", "question")   # written by `board advance` alone on a phased entry
PHASE_REQUIRES = {                                       # phase -> the sub-keys it must carry beside `unit`
    "verifying": ("pr",), "landing": ("pr", "evidence"), "done-ready": ("evidence",), "done-asked": ("evidence",),
    "held": ("from", "on")}
ADVANCE_USAGE = ("usage: dyad board advance <id> [<id>…] <event> --expect <phase>|none [key=value…] "
                 "[--said-file <path>] [--mirror <branch>]")
MULTI_ID_EVENTS = ("asked", "answered-Y", "answered-N")
ASKED_KIND = {"intent-asked": "intent", "plan-asked": "plan", "done-asked": "done"}
INTENT_KEY = "intent-reading"                           # #615: the preference that asks the intent question (absent: off)
BARE_N = frozenset({"n", "no"})                         # #615: a bare N's words (Rule-3 Answer grammar: one N, any case)
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
    "intent-asked": ("operator",    "record the Operator's answer: dyad board advance <the question's ids> answered-Y|answered-N --expect intent-asked --said-file <F> (a bare N archives)"),
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
def mandated(rid: int, rows: dict) -> list[int]:
    """Every row accreted under `rid`'s mandate, terminal ones included: a `disposed` holding `mandate #<rid>` and refs
    naming it (`parent #<rid>`, `#<rid>` or `<rid>`)."""
    names = {f"#{rid}", str(rid)}
    return sorted(r.id for r in rows.values() if r.id != rid and re.search(rf"\bmandate #{rid}\b", r.disposed)
                  and names & set(r.refs.replace("parent ", "").split()))


def accreted_of(rid: int, rows: dict) -> list[int]:
    """The rows accreted under `rid`'s mandate that are not terminal (`mandated`): the ones a Done question names."""
    return [i for i in mandated(rid, rows) if rows[i].state not in dyadlib.TERMINAL_STATES]


def union_prs(ids, entries: dict) -> list[int]:
    out = []
    for i in ids:
        for n, _ in pr_list(phase_of(entries[i]["phase"])[1]):
            if n not in out:
                out.append(n)
    return out


def question(kind: str, ids, entries: dict, rows: dict, pref: str | None, slugs: bool = False) -> str:
    """The counter-prompt `asked` stores verbatim on every named entry (Rule-3's forms): `plan` — `Y/N: proceed with #a[,
    #b] as planned?`; `done` — `Y/N: Done with #a <title> (accreted #c, merges PR #w, #x)?`, each clause only when
    non-empty, or the batch `Y/N: Done with #a <ta> (accreted #c), #b <tb> (merges PR #w, #x)?` whose merges clause is
    the union in id order. PRs without heads (Rule-3 form). Refused with PRs unless `merge-disposition` is
    `with-done`: under `separate` the merge is its own question, asked by hand (#587 risk 6). With `slugs` (#622,
    `dwork-slug: on`) every row id it writes is a label, `#<id>-<slug>`; PR numbers never are."""
    ids = list(ids)
    L = lambda i: dyadlib.row_label(i, rows, slugs)
    for i in ids:
        r = rows.get(i)
        if r is not None and any(unicodedata.category(c) == "Cc" for c in r.title):
            raise Refused(f"row #{i}'s title holds a control character: a Y binds the question as asked, and a title is "
                          f"immutable (Rule-16), so the remedy is a new row (counsel's ruling 3, #587)")
    if kind == "plan":
        return f"Y/N: proceed with {', '.join(L(i) for i in ids)} as planned?"
    if kind == "intent":                                  # #615: the intent question, asked before any plan is drafted
        return "Y/N: intent aligned for " + ", ".join(f"{L(a)} {rows[a].title}" for a in ids) + "?"
    prs = union_prs(ids, entries)
    if prs and pref != "with-done":
        raise Refused(f"merge-disposition is {pref or 'unset'}, not with-done: a Done question naming PRs is not composed "
                      f"here; ask the merge and the Done by hand (#587)")
    merges = f"merges PR {', '.join(f'#{n}' for n in prs)}" if prs else ""
    def acc(a):
        got = accreted_of(a, rows)
        return f"accreted {', '.join(L(c) for c in got)}" if got else ""
    if len(ids) == 1:
        a = ids[0]
        clauses = [c for c in (acc(a), merges) if c]
        return f"Y/N: Done with {L(a)} {rows[a].title}" + (f" ({', '.join(clauses)})" if clauses else "") + "?"
    parts = [f"{L(a)} {rows[a].title}" + (f" ({acc(a)})" if acc(a) else "") for a in ids]
    return "Y/N: Done with " + ", ".join(parts) + (f" ({merges})" if merges else "") + "?"


QUESTION_LINE = re.compile(r"Y/N: (?:proceed with (?P<plan>.*) as planned|Done with (?P<done>.*)|intent aligned for (?P<intent>.*))\?")


def question_kind(q: str) -> str | None:
    m = QUESTION_LINE.fullmatch(((q or "").strip().splitlines() or [""])[-1])
    return None if m is None else "plan" if m["plan"] is not None else "intent" if m["intent"] is not None else "done"


def bare_n(text: str | None) -> bool:
    """Whether an answer's words are a bare `N` (#615, Rule-3 Answer grammar): `N`, `n` or `no`, alone."""
    return (text or "").strip().lower().rstrip(".") in BARE_N


def ids_of(q: str) -> list[int]:
    """The ids a stored question names, read back: every `#<n>` of a plan question; of a Done question, every `#<n>`
    that opens an item at parenthesis depth 0 (a title holding `, #<n>` reads as one more id, so a binding check over
    it refuses rather than widens)."""
    m = QUESTION_LINE.fullmatch(((q or "").strip().splitlines() or [""])[-1])
    if m is None:
        return []
    if m["plan"] is not None:
        return [int(x) for x in re.findall(r"#(\d+)", m["plan"])]
    span, out, depth = m["done"] if m["done"] is not None else m["intent"], [], 0
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


ACCRETED_LABEL = r"#\d+(?:-[A-Za-z0-9][A-Za-z0-9.]*)*"   # #622: an id, or a label `#<id>-<slug>`

def accreted_in(q: str) -> list[int]:
    got = re.findall(rf"accreted ({ACCRETED_LABEL}(?:, {ACCRETED_LABEL})*)", ((q or "").strip().splitlines() or [""])[-1])
    return [int(x) for x in re.findall(r"#(\d+)", got[-1])] if got else []


# ---- relays (X2): templates of the event's own fields; free text travels on the board (`note`), never in a body
NOTICE_BODY = None   # sentinel: the body is `automaton.notice_body` (the plan notice K2 and `inbox.handed_rows` read)
RELAYS: dict[tuple[str, str], tuple[str, str, str | None]] = {   # (event, target) -> (to, kind, body template)
    ("opened", "planning"):            ("unit", "relay", "row #{id} planning: write plans/{id}.md; advance plan-landed when it is on main"),
    ("plan-landed", "plan-ready"):     ("holder", "report", "row #{id} plan-ready: plans/{id}.md is on main; the plan question is owed"),
    ("answered-Y", "building"):        ("owners", "notice", NOTICE_BODY),   # K2's shape: one per owner, its own part
    ("answered-N", "planning"):        ("unit", "relay", "row #{id} planning: the operator answered N with words; read provenance/{id}.md and revise plans/{id}.md"),
    ("answered-Y", "planning"):        ("unit", "relay", "row #{id} planning: the intent reading is aligned; draft the plan in plans/{id}.md, then advance plan-landed"),
    ("answered-N", dyadlib.ORCH_DROP): ("owners", "notice", "row #{id} archived: the intent question's answer was a bare N; nothing is planned"),
    ("pr-up", "verifying"):            ("holder", "report", "row #{id} verifying: PR #{pr} at {head} is up from {sender}; verify {prs}"),
    ("evidence-verified", "done-ready"): ("holder", "report", "row #{id} done-ready: evidence {ev12} on {prs}; the Done question is owed"),
    ("evidence-failed", "building"):   ("unit", "relay", "row #{id} building: the evidence failed; the failing line is the board's note"),
    ("head-moved", "verifying"):       ("holder", "report", "row #{id} verifying: PR #{pr} moved to {head}; the evidence and any question on the earlier head are withdrawn (X6)"),
    ("withdrawn", "done-ready"):       ("holder", "report", "row #{id} done-ready: the batch Done question naming it was withdrawn, a head it named moved (see board/{id}.md note); re-ask (X6)"),
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
        recips = [holder] + ([o for o in owners(entry) if o not in (sender, holder)] if event in ("pr-up", "head-moved") else [])
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
def actor_ok(actor: str, entry: dict[str, str], sender: str, automaton: bool = False) -> str | None:
    """Why `sender` may not fire an event of `actor` (one actor, or several joined by `dyadlib.ORCH_OR`) on `entry`, or
    None. `automaton` is the automaton's own call (scripts/automaton.py, never the CLI): it may fire exactly the events
    whose cell names the automaton (#587 X5, X6)."""
    actors = dyadlib.orch_actors(actor)
    if automaton:
        return None if "automaton" in actors else f"a {actor} event is never the automaton's"
    why = []
    for a in sorted(actors):
        holder = entry.get("holder") or sender
        if a == "home" and sender != holder:
            why.append(f"a home event is the holder's ({holder}), not {sender}'s")
        elif a == "unit" and sender not in set(owners(entry)) | {entry.get("holder", "")}:
            why.append(f"a unit event is an owner's or the holder's ({', '.join(owners(entry) + [entry.get('holder', '?')])}), not {sender}'s")
        elif a == "automaton":
            why.append("an automaton event never comes from the CLI")
        else:
            return None
    return "; ".join(why) or None


def transition(rid: int, entry: dict[str, str], row, event: str, pairs: dict[str, str], sender: str, now: str,
               recorded: bool = False, question_text: str | None = None,
               automaton: bool = False, bare: bool = False) -> tuple[str, dict[str, str] | None]:
    """(target, the new entry or None when it is dropped) of one event on one entry; Refused when the table does not
    allow it. `entry` is {} when absent; `pairs` the event's own fields; the new entry's `writer` is left to the
    caller. `bare`: the answer's words are a bare `N`, which archives the row at intent-asked (#615). Pure: no file, no
    git."""
    cur = phase_name(entry)
    key = (cur, event)
    if key not in dyadlib.ORCH_EVENTS:
        legal = sorted(e for f, e in dyadlib.ORCH_EVENTS if f == cur and (automaton or e in dyadlib.ORCH_CLI_EVENTS))
        raise Refused(f"#{rid} is at {cur or 'no phase'}: {event} is not an event from there (legal: {', '.join(legal) or 'none'})")
    targets, actor, required = dyadlib.ORCH_EVENTS[key]
    if not recorded and (why := actor_ok(actor, entry, sender, automaton)):
        raise Refused(f"#{rid} {event}: {why} (#587)")
    missing = [r for r in required if r != "said-file" and not pairs.get(r)]
    if missing:
        raise Refused(f"#{rid} {event} needs {', '.join(f'{m}=' for m in missing)}")
    if event in dyadlib.ORCH_NO_EFFECT:                   # S10: a self-loop that changes nothing, `since` and writer kept
        return targets[0], dict(entry)
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
    if event == "answered-N" and cur == "intent-asked" and bare:   # #615: the bare intent-N archives the row
        target = dyadlib.ORCH_DROP
    if event == "opened":
        sub["unit"] = [pairs["unit"]]
        if pairs["unit"] not in owners(new):
            new["owner"] = "; ".join(x for x in (new.get("owner", "").strip(), pairs["unit"]) if x)
    elif event == "pr-up":
        sub = pr_add(sub, int(pairs["pr"]), pairs["head"])
    elif event == "head-moved":                           # X6: the new head recorded, the evidence on the old one void;
        sub = pr_add(sub, int(pairs["pr"]), pairs["head"])   # the question is a DERIVED field, so it is dropped below
        sub.pop("evidence", None)
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


def ledger_lines(ids, entries: dict, rows: dict, event: str, said_abs: str, pref: str | None = None,
                 slugs: bool = False, decisions_abs: str | None = None) -> list[str]:
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
    if kind == "intent":                                  # #615: Y and N amend keep the state; the bare N archives
        bare = yn == "N" and bare_n(Path(said_abs).read_text() if said_abs and Path(said_abs).is_file() else "")
        d = f"{yn} intent ({batch})" if len(ids) > 1 else f"{yn} intent"
        for i in ids:
            out.append(shlex.join(["state", str(i), "archived" if bare else rows[i].state, "-d", d, "--said-file", said_abs]))
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
    if q != question("done", ids, entries, rows, pref, slugs):    # #622: a Done asked bare and answered labelled is asked again
        raise Refused(f"the stored question no longer matches the rows ("
                      + "; ".join(f"#{i} accreted {' '.join(f'#{c}' for c in acc[i]) or 'none'}" for i in ids)
                      + "): ask again (Rule-2, Binding)")
    def accl(i):
        return [f"accreted {', '.join(f'#{c}' for c in acc[i])}"] if acc[i] else []
    for i in ids:
        clauses = ([batch] if len(ids) > 1 else []) + accl(i) + ([f"merges {merges}"] if merges else [])
        d = "Y done" + (f" ({', '.join(clauses)})" if clauses else "")
        out.append(shlex.join(["state", str(i), "done" if not prs else rows[i].state, "-d", d, "--said-file", said_abs]
                              + (["--decisions", decisions_abs] if decisions_abs else [])))   # #648: each row its own lines
        if not prs:                                       # done at once: its accreted rows close under its mandate now,
            out += [shlex.join(["state", str(c), "done", "--mandate", str(i)]) for c in acc[i]]   # as close_landed would
    return out


# ---- the builder (X4, X9): one code path for every event, run on every try in land's worktree
def parse_advance(a: list[str]) -> tuple[list[int], str, dict[str, str], str | None, str | None, str | None, str | None]:
    """(ids, event, pairs, expect, said-file made absolute, mirror, decisions file made absolute) from the argv; every
    refusal here is before any fetch."""
    ids, i = [], 0
    while i < len(a) and a[i].isdigit():
        ids.append(int(a[i])); i += 1
    if not ids or i >= len(a) or a[i].startswith("-") or "=" in a[i]:
        raise Refused(ADVANCE_USAGE)
    event, rest = a[i], a[i + 1:]
    if event in dyadlib.ORCH_NO_EFFECT:
        raise Refused(f"{event} changes nothing on the entry and is fired by `dyad inbox read <message>…`, which writes its "
                      f"marker; board advance does not take it (#587 S10)")
    if event not in dyadlib.ORCH_CLI_EVENTS:
        raise Refused(f"{event!r} is not an event (events: {', '.join(sorted(dyadlib.ORCH_CLI_EVENTS))})")
    if len(ids) > 1 and event not in MULTI_ID_EVENTS:
        raise Refused(f"only {', '.join(MULTI_ID_EVENTS)} take several ids, not {event}")
    if len(set(ids)) != len(ids):
        raise Refused("an id named twice")
    expect = said = mirror = decisions = None
    pairs: dict[str, str] = {}
    j = 0
    while j < len(rest):
        x = rest[j]
        if x in ("--expect", "--said-file", "--mirror", "--decisions"):
            if j + 1 >= len(rest):
                raise Refused(f"{x} needs a value")
            v = rest[j + 1]; j += 2
            if x == "--expect":
                expect = v
            elif x == "--said-file":
                said = os.path.abspath(v)
            elif x == "--decisions":
                decisions = os.path.abspath(v)
            else:
                mirror = v
            continue
        k, sep, v = x.partition("=")
        if not sep or k not in PAIR_KEYS:
            raise Refused(f"{x!r} is not one of {', '.join(f'{p}=' for p in PAIR_KEYS)}, --expect, --said-file, --decisions or --mirror")
        if k in pairs:
            raise Refused(f"{k}= given twice")
        pairs[k] = v; j += 1
    if expect is None:
        raise Refused(ADVANCE_USAGE)
    if expect != "none" and expect not in dyadlib.ORCH_PHASES:
        raise Refused(f"--expect is a phase ({', '.join(dyadlib.ORCH_PHASES)}) or none, not {expect!r}")
    key = (None if expect == "none" else expect, event)
    if key not in dyadlib.ORCH_EVENTS:
        legal = sorted(e for f, e in dyadlib.ORCH_EVENTS if f == key[0] and e in dyadlib.ORCH_CLI_EVENTS)
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
            raise Refused(f"{k}={v!r} is not {dict(unit='a seat', pr='a PR number', head='40 hex (the full sha, #661)', evidence='64 hex', on='`operator`, `unit <name>` or `external <ref>`', note='text')[k]}")
    if "note" in pairs and inbox().DISPOSITION.search(pairs["note"]):
        raise Refused("note= is disposition-shaped (a `Y/N:` line or a ledger entry): the board carries information, "
                      "never authority (#587 X2)")
    if decisions is not None and (event, expect) != ("answered-Y", "done-asked"):
        raise Refused("--decisions rides the Done answer only: answered-Y --expect done-asked (#648)")
    if decisions is not None and not Path(decisions).is_file():
        raise Refused(f"--decisions {decisions} is not a file")
    return ids, event, pairs, expect, said, mirror, decisions


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
                    repo: Path, value_flags, parse, words, sender: str, recorded: bool = False, landed=None, ran=None,
                    automaton: bool = False, decisions_abs: str | None = None):
    """land's builder for one `board advance` (section 7 of plan #587 PR2). On every try, in land's worktree on a freshly
    fetched origin/main: read and refuse (`--expect`, the cabinet fence of `board set` on an existing entry (#594 K6),
    the table, the actor, the fields, the binding set), and file a birth under the sender's cabinet as `board set`
    files a new entry (#594 K7); compose the
    ledger lines, write the board, compose the relays; then run the composed text through `dwork batch`'s own parser
    and builder, so every refusal of `dwork state` and `inbox post` holds. A refusal raises before `git commit`; the
    next `land.prepare` discards what was written. `recorded` (the automaton's catch-up only, never the CLI) writes no
    ledger line, checks no trace and waives the actor. `automaton` (the automaton's X5 and X6 only, never the CLI) fires
    an event whose actor cell names the automaton, and only such an event."""
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
            if entries[rid] and not (recorded or automaton):   # #594 K6 on the phased path; the automaton leads none
                cabinet_fence(str(rid), entries[rid], pairs, False, sender, cabinet_of(sender, wt))
            _, actor, _ = dyadlib.ORCH_EVENTS[(cur, event)]
            if not recorded and (why := actor_ok(actor, entries[rid], sender, automaton)):
                raise Refused(f"#{rid} {event}: {why} (#587)")
        # event preconditions
        if event == "plan-landed":
            for rid in ids:
                if not (wt / inst / "d-work" / "plans" / f"{rid}.md").is_file():
                    raise Refused(f"#{rid} plan-landed: plans/{rid}.md is not on origin/main; land it first (`dyad dwork land`)")
        qtext = None
        if event == "asked" and exp == "planning":       # #615: the intent question is the preference's, never the agent's
            if dyadlib.preference(INTENT_KEY, wt) != "on":
                raise Refused(f"intent-reading is {dyadlib.preference(INTENT_KEY, wt) or 'absent (off)'}, not on: the intent "
                              f"question is not asked (Rule-3 Plan, #615)")
            for rid in ids:
                if not (wt / inst / "d-work" / "plans" / f"{rid}.md").is_file():
                    raise Refused(f"#{rid} asked: the intent reading is plans/{rid}.md's first section, and it is not on "
                                  f"origin/main; land it first (`dyad dwork land`)")
        if event == "asked":
            kind = {"planning": "intent", "plan-ready": "plan"}.get(exp, "done")
            qtext = question(kind, ids, entries, rows, dyadlib.preference("merge-disposition", wt), dyadlib.slugs_on(wt))
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
        bare = event == "answered-N" and exp == "intent-asked" and bare_n(words({"--said-file": said_abs}, "said") if said_abs else "")
        results = {rid: transition(rid, entries[rid], rows[rid], event, pairs, sender, now, recorded, qtext, automaton, bare)
                   for rid in ids}
        lines = []
        if not recorded:
            if event == "answered-Y" and aexp == "done-asked":
                tl, rels = trace_lines(ids, wt, inst, repo)
                lines += tl
                landed[:] = rels
            lines += ledger_lines(ids, entries, rows, event, said_abs or "", dyadlib.preference("merge-disposition", wt),
                                  slugs=dyadlib.slugs_on(wt), decisions_abs=decisions_abs)
        changed, paths = [], []
        for rid in ids:
            target, new = results[rid]
            p = bdir / f"{rid}.md"
            if new is None:
                if p.exists():
                    p.unlink(); changed.append(rid)
            else:
                if old_text[rid] is None and "cabinet" not in new:   # #594 K7: a birth is filed once, as `board set` files one
                    cab = cabinet_of(sender, wt) or filing_cabinet(sender, cos_files(bdir))
                    if cab != SOLO:
                        new["cabinet"] = cab
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


def read_event(wt: Path, inst: str, rid: int, row, sender: str) -> str | None:
    """#587 S10: the `read` event on row `rid`'s entry in `wt`, fired by `inbox read <message>…` in its own land: one
    line naming the phase it was read at, or None when the entry is absent or unphased (no machine to record in).
    The event changes nothing (ORCH_NO_EFFECT), so no board file is written; the transition is still run, so the table
    and the fields are checked as for any other event. Raises when the table's self-loop would change the entry — an
    impossible condition the import-time invariant already rules out (Rule-12 p1: the fail-loud check)."""
    p = wt / inst / BOARD_REL / f"{rid}.md"
    if not p.is_file():
        return None
    entry = parse_entry(p.read_text(errors="replace"))[0]
    cur = phase_name(entry)
    if cur is None:
        return None
    target, new = transition(rid, entry, row, "read", {}, sender, now_iso(), recorded=True)
    if target != cur or new != entry:
        raise Refused(f"#{rid} read: the table's `read` would move the entry ({cur} -> {target}); it must change nothing (#587 S10)")
    return f"board #{rid}: read at {cur}, nothing changed (#587 S10)"


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
        ids, event, pairs, expect, said, mirror, decisions = parse_advance(a)
        L.check_mirror(repo, mirror)
        inst = dyadlib.instance_rel(repo)
        if inst is None:
            raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree; a board write lands a tracked store")
        sender = os.environ.get("DYAD_SESSION") or ""
        if not inbox().SEAT.fullmatch(sender):
            raise Refused("DYAD_SESSION names no seat: an event is fired from a seat (#587)")
        landed, ran = [], []
        build = advance_builder(ids, event, pairs, expect, said, inst, repo, value_flags, dwork_args, words, sender,
                                landed=landed, ran=ran, decisions_abs=decisions)
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


# ---- the Done skeleton (X7): the machine's part of a completion reply, read-only; orchestrate writes the rest
DRAFT_PHASE = "done-ready"
ORCHESTRATE = "_orchestrate writes this section; the machine does not judge it._"
ORCHESTRATE_SECTIONS = (   # (heading, what goes there): Rule-3's completion evidence (E8) that is inference, not data
    ("Host actions", "every host action taken, its class and its change-log row (a missing row is a Rule-8 breach)"),
    ("Departures", "anything in the plan not delivered, any departure from it, every escalation"),
    ("Unverified", "anything that could not be verified, stated before the question"),
    ("DoD judgment", "whether the output meets the definition of done quoted above, part by part"),
)


QUOTE = "  "                                         # the fixed prefix of every quoted line inside a fence (F2)
CONTROL = re.compile(r"[\x00-\x08\x0a-\x1f\x7f\x85\u2028\u2029]")   # C0 but tab, DEL, and the line breaks splitlines reads (F8)
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
QUESTION_START = re.compile(r"^Y/N:", re.M)


def _git(repo: Path, *a: str, strip: bool = True) -> str | None:
    """One read-only git call in `repo`: its stdout (stripped unless told not to), None when git fails."""
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, env=dyadlib.git_env())
    return (r.stdout.strip() if strip else r.stdout) if r.returncode == 0 else None


def clean(text: str) -> str:
    """`text` with every control character but tab written as `\\xNN` (or `\\uNNNN`), so repo data printed by the
    draft can neither break a line nor drive a terminal (F8)."""
    return CONTROL.sub(lambda m: f"\\x{ord(m[0]):02x}" if ord(m[0]) < 0x100 else f"\\u{ord(m[0]):04x}", text)


def dod_sections(text: str) -> list[str]:
    """Every `## Definition of done…` section of a plan (dyadlib.PLAN_PARTS' last part), heading included, verbatim,
    in file order (a revision may add its own); [] when there is none. A `## ` line inside a code fence (a run of three
    or more backticks or tildes, closed by a run of the same character at least as long) is text, not a heading (F3)."""
    part, out, cur, fence = dyadlib.PLAN_PARTS[-1], [], None, None
    for line in text.split("\n"):
        m = FENCE.match(line)
        if fence is None and m:
            fence = m[1]
        elif fence is not None and m and m[1][0] == fence[0] and len(m[1]) >= len(fence) and not line[m.end():].strip():
            fence = None
        elif fence is None and line.startswith("## "):
            if cur is not None:
                out.append("\n".join(cur).rstrip("\n"))
            cur = [line] if line[3:].strip().lower().startswith(part) else None
            continue
        if cur is not None:
            cur.append(line)
    if cur is not None:
        out.append("\n".join(cur).rstrip("\n"))
    return out


def fenced(text: str) -> list[str]:
    """`text` in a code fence longer than any run of backticks it holds, every line behind the fixed prefix QUOTE and
    cleaned (`clean`), so no quoted line can close the fence or start a line of its own — a `Y/N:` above all (F2)."""
    f = "`" * max(3, 1 + max((len(m) for m in re.findall(r"`+", text)), default=0))
    return [f, *(QUOTE + clean(l) for l in text.split("\n")), f]


def cell(text: str) -> str:
    return clean(text).replace("|", "\\|")


def pr_draft(repo: Path, base: str | None, n: int, head: str) -> str:
    """One PR's table row: number, zone(s) of its files (`containment.classify`) from the merge base with `base` to its
    recorded head, the head, the file count; the zone cell says why when the head is not in this clone, or is already
    on `base`. Names are read NUL-separated and unquoted, so a space or a non-ASCII byte is one path (F4)."""
    full = _git(repo, "rev-parse", "--verify", "-q", f"{head}^{{commit}}")
    if full is None:
        return f"| #{n} | ? (head not in this clone: fetch refs/pull/{n}/head) | {head} | ? |"
    mb = _git(repo, "merge-base", base, full) if base else None
    if mb is None:
        return f"| #{n} | ? (no merge base with {base or 'origin/main'}) | {head} | ? |"
    if mb == full:
        return f"| #{n} | head already on {base} (merged before the Done?) | {head} | - |"
    raw = _git(repo, "-c", "core.quotePath=false", "diff", "--name-only", "-z", "--no-renames", f"{mb}..{full}", strip=False)
    files = [f for f in (raw or "").split("\0") if f]
    cz = dyadlib.load_guard("infra", "containment")
    t = cz.table(repo)
    zones = sorted({cz.classify(p, zones=t) for p in files})
    z = ", ".join(zones) + (f" ({len(zones)} zones: Rule-1)" if len(zones) > 1 else "") if zones else "none (no file)"
    return f"| #{n} | {z} | {head} | {len(files)} |"


def evidence_draft(repo: Path, sha: str) -> list[str]:
    """The evidence a phase records, as its brief form when the full block is stored in this checkout
    (`<git common dir>/dyad-evidence/<sha256>.txt`, Rule-14 property 3) and matches its own sha256; the baseline is
    looked up only where it costs nothing (self, cached, stored), never computed. A stored block that does not match
    is named and not shown (F7); an absent one is one line saying where to read it. `sha` is 64 hex (`evidence_lines`)."""
    pk = dyadlib.runner_module()
    common = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    d = Path(common) / pk.EVIDENCE_STORE if common else None
    path = d / f"{sha}.txt" if d is not None else None
    if path is None or not path.is_file():
        return [f"block not stored here; run `dyad check --evidence --show {sha}` in the checkout that ran it"]
    block = path.read_text(errors="replace").splitlines()
    if not block or block[-1] != pk.EVIDENCE_SHA + sha or block[-1] != pk.EVIDENCE_SHA + pk.evidence_sha256(block[:-1]):
        return [f"stored block {clean(str(path))} does not match its sha256 (tampered or truncated); not shown"]
    main = _git(repo, "rev-parse", "--verify", "-q", "origin/main^{commit}")
    baseline: tuple = (None, "origin/main does not resolve")
    if main:
        name = f"origin/main {main[:12]}"
        if block[0] == f"head={main}":
            baseline = (pk.evidence_warn_kinds(block[:-1]), f"{name} (self)")
        elif (k := pk.evidence_baseline_cache_read(d / pk.BASELINE_CACHE.format(sha=main), main)) is not None:
            baseline = (k, f"{name} (cached)")
        elif (k := pk.evidence_baseline_stored(d, main)) is not None:
            baseline = (k, f"{name} (stored)")
        else:
            baseline = (None, "not computed by board draft")
    return fenced("\n".join(pk.evidence_brief(block, path, baseline)))


def evidence_lines(repo: Path, sub: dict[str, list[str]]) -> list[str]:
    """The Evidence section's body: the recorded sha256 only when it is 64 hex (HEX64, the guard's own pattern), and
    never echoed or put in a command otherwise (F6)."""
    ev = first(sub, "evidence")
    if not ev:
        return ["none recorded on the phase"]
    if not HEX64.fullmatch(ev):
        return ["evidence malformed (not 64 hex)"]
    return [f"evidence-sha256 `{ev}`, recorded on the phase over {prs_text(sub) or 'no PR'}", ""] + evidence_draft(repo, ev)


def draft_lines(rid: int, repo: Path) -> list[str]:
    """The Done skeleton of row `rid` (X7), Markdown, from the working tree: Refused unless its board entry is phased
    at `done-ready` and `check_phased` finds nothing in it (F1). The machine's sections — the DoD quoted from
    plans/<id>.md, the PRs (zone, head), the evidence (sha256 and brief), the accreted rows, the trace — then
    orchestrate's (ORCHESTRATE_SECTIONS, marked), and last the question `asked` would store (`question`), composed by the
    same function. Every repo field is `clean`ed, and the one line starting `Y/N:` is the last: a fail-loud check
    raises before anything is printed if another did (F2). Reads only; writes and posts nothing."""
    p = store(repo) / f"{rid}.md"
    entry = parse(p.read_text(errors="replace"))[0] if p.is_file() else {}
    cur = phase_name(entry)
    if cur != DRAFT_PHASE:
        raise Refused(f"#{rid} is at {clean(cur or ('no phase' if entry else 'no board entry'))}: board draft drafts a "
                      f"{DRAFT_PHASE} row only")
    rows = {r.id: r for r in dyadlib.read_rows(repo)}
    row = rows.get(rid)
    if row is None:
        raise Refused(f"#{rid}: no such row")
    problems = check_phased(str(rid), entry, rows)
    if problems:
        raise Refused(f"board/{rid}.md is not a clean {DRAFT_PHASE} entry ({len(problems)} problem(s)), first: "
                      f"{clean(problems[0].removeprefix('warning:').strip())}")
    sub = phase_of(entry["phase"])[1]
    prs = pr_list(sub)
    inst = dyadlib.instance(repo)
    on = dyadlib.slugs_on(repo)                                    # #622: read once
    L = lambda i: dyadlib.row_label(i, rows, on)
    rel = lambda q: q.relative_to(repo).as_posix() if q.is_relative_to(repo) else str(q)
    at = (_git(repo, "rev-parse", "--short=12", "HEAD") or "?")
    out = [f"# Done {L(rid)} {clean(row.title)}: skeleton", "",
           f"Drafted by `dyad board draft {rid}` from the working tree at {at} (`git pull` first for main's). The machine's "
           f"sections are data; the sections marked for orchestrate are not the machine's. Nothing here was posted.", ""]
    plan = inst / "d-work" / "plans" / f"{rid}.md"
    out += [f"## Definition of done (quoted from {rel(plan)})", ""]
    secs = dod_sections(plan.read_text(errors="replace")) if plan.is_file() else []
    if secs:
        for s in secs:
            out += fenced(s) + [""]
    else:
        out += [f"{rel(plan)} {'has no `## Definition of done` section' if plan.is_file() else 'does not exist'}: "
                f"orchestrate quotes the DoD by hand", ""]
    base = "origin/main" if _git(repo, "rev-parse", "--verify", "-q", "origin/main^{commit}") else None
    out += [f"## PRs (zones from the merge base with {base or '?'} to the recorded head)", ""]
    if prs:
        out += ["| PR | zone | head | files |", "|---|---|---|---|"] + [pr_draft(repo, base, n, h) for n, h in prs] + [""]
    else:
        out += ["none recorded on the phase", ""]
    out += ["## Evidence", ""] + evidence_lines(repo, sub) + [""]
    acc = mandated(rid, rows)
    named = set(accreted_of(rid, rows))
    out += [f"## Accreted rows (`mandate #{rid}` in `disposed`, refs naming #{rid})", ""]
    if acc:
        ents = rows_guard().entries
        out += ["| row | state | mode | dispositions | title |", "|---|---|---|---|---|"]
        out += [f"| {L(i)}{'' if i in named else ' (terminal: not in the question)'} | {cell(rows[i].state)} | {cell(rows[i].mode)} | "
                f"{len(ents(rows[i].disposed))} | {cell(rows[i].title)} |" for i in acc] + [""]
    else:
        out += ["none", ""]
    tr = inst / "d-work" / "traces" / f"{rid}.md"
    pref = dyadlib.preference(rows_guard().TRACE_KEY, repo)
    out += ["## Trace", "", f"`{rel(tr)}`: " + ("present" if tr.is_file() else
            f"absent (dwork-trace: {clean(pref or 'unset')}; write it with `dyad dwork trace {rid} --out`)"), ""]
    cands = candidates(repo, rid)
    out += [f"## Candidates (dmc:precedent-admission over this row's sources; its `Y done` records them with "
            f"`--decisions`, #648)", ""]
    if cands:
        out += [f"- `{c['record']}` {clean(c['case'])}: {clean(c['outcome'])} — {clean(' '.join(c['inputs'].split())[:100])}"
                for c in cands]
        out += ["", f"Write them with `dyad board draft {rid} {DECISIONS_OUT} <file>`; drop a line only with its reason, "
                    f"named in the evidence.", ""]
    else:
        out += ["none: this Done records no `--decisions`", ""]
    inc = [(f, e) for f, e in promised_incidents(repo) if names_row(e, rid)]
    out += [f"## Promised incidents (`promised` entries of the cross-row file naming #{rid}; its PR logs them in "
            f"INCIDENTS.md, Rule-3 Incidents, #651)", ""]
    out += [f"- {clean(e)} ({f}.md)" for f, e in inc] + [""] if inc else ["none", ""]
    out += [f"## Prose rulings (orchestrate)", "", ORCHESTRATE,
            f"{PROSE_SLOT}   <!-- one line per departure line the evidence names, judged by dmc:plan-departure -->", ""]
    for head, what in ORCHESTRATE_SECTIONS:
        out += [f"## {head} (orchestrate)", "", ORCHESTRATE, f"<!-- {what} -->", ""]
    try:
        q = clean(question("done", [rid], {rid: entry}, rows, dyadlib.preference("merge-disposition", repo), on))
    except Refused as e:
        q = f"(question not composed: {clean(str(e))})"
    out += ["## Question (as `asked` would store it)", "", q]
    text = "\n".join(out)
    starts = [m.start() for m in QUESTION_START.finditer(text)]
    if starts[:-1] or (starts and starts[-1] != text.rfind("\n") + 1):   # F2's fail-loud check, before the one print
        raise Refused(f"#{rid}: the draft holds a line starting `Y/N:` other than its last; not printed (#587 X7)")
    return out


def candidates(repo: Path, rid: int) -> list[dict]:
    """#648: row `rid`'s candidate rulings its Done records (`backfill.capture`): its own sources, admissible ones only."""
    return dyadlib.load_module(dyadlib.PKG / "scripts" / "backfill.py", "dyad_backfill").capture(Path(repo), rid)


def out_roots(repo: Path) -> list[Path]:
    """Every place the skeleton may never be written: each worktree of `repo`'s repository (`git worktree list
    --porcelain`) and its common git dir (F5)."""
    roots = [Path(repo).resolve()]
    for line in (_git(repo, "worktree", "list", "--porcelain") or "").splitlines():
        if line.startswith("worktree "):
            roots.append(Path(line[len("worktree "):]).resolve())
    common = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common:
        roots.append(Path(common).resolve())
    return list(dict.fromkeys(roots))


def out_refusal(dest: Path, repo: Path) -> None:
    """Refused when `--out`'s destination is under a worktree or the git dir of this repository, or already exists."""
    for root in out_roots(repo):
        if dest.is_relative_to(root):
            raise Refused(f"{OUT} {clean(str(dest))} is under {clean(str(root))}, a worktree or the git dir of this repository; "
                          f"the skeleton is never written to the repo (give a scratch path)")
    if dest.exists() or dest.is_symlink():
        raise Refused(f"{OUT} {clean(str(dest))} exists; the skeleton never overwrites a file (give a new path)")


def cmd_draft(a: list[str], repo: Path) -> int:
    """`dyad board draft <id> [--out <file>] [--decisions-out <file>]`: print the Done skeleton, or write it to a file
    outside the work tree; --decisions-out writes the row's candidate rulings as `--decisions` lines (#648), and given
    alone it needs no done-ready entry and prints no skeleton."""
    got = dyadlib.cli_parse(CLI_FLAGS["draft"], list(a))
    usage = dyadlib.cli_usage(("board", "draft"))
    if got.helped:
        print(usage); return 0
    if got.unknown or got.extra or len(got.pos) != 1 or not got.pos[0].isdigit() \
            or any(f in got.values and not got.one(f) for f in (OUT, DECISIONS_OUT)):
        print(usage, file=sys.stderr); return 2
    try:
        dest = Path(got.one(OUT)).resolve() if got.one(OUT) else None
        ddest = Path(got.one(DECISIONS_OUT)).resolve() if got.one(DECISIONS_OUT) else None
        for d in (dest, ddest):
            if d is not None:
                out_refusal(d, Path(repo))
        # #648: --decisions-out alone needs no done-ready entry, so a Done recorded by hand can write its file too
        lines = draft_lines(int(got.pos[0]), Path(repo).resolve()) if dest is not None or ddest is None else []
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr); return 1
    if ddest is not None:   # #648: the structured candidates as `--decisions` lines, source done
        import json
        cands = candidates(Path(repo).resolve(), int(got.pos[0]))
        try:
            ddest.parent.mkdir(parents=True, exist_ok=True)
            with ddest.open("x") as h:
                h.write("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cands))
        except OSError as e:
            print(f"refused: {DECISIONS_OUT} {clean(str(ddest))}: {clean(e.strerror or type(e).__name__)}", file=sys.stderr); return 1
        print(f"wrote {clean(str(ddest))} ({len(cands)} candidate(s) as --decisions input)")
        if dest is None:
            return 0
    if dest is None:
        print("\n".join(lines)); return 0
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("x") as h:                     # `x`: a file created meanwhile is not overwritten either
            h.write("\n".join(lines) + "\n")
    except OSError as e:
        print(f"refused: {OUT} {clean(str(dest))}: {clean(e.strerror or type(e).__name__)}", file=sys.stderr); return 1
    print(f"wrote {clean(str(dest))} ({len(lines)} lines)")
    return 0


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
    if a and a[0] == "draft":
        return cmd_draft(a[1:], repo)
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
    ("draft-phase-is-a-phase", lambda: DRAFT_PHASE in dyadlib.ORCH_PHASES and ASKED_OF.get(DRAFT_PHASE) == "done-asked"),   # X7
    ("orchestrate-sections-distinct", lambda: len({h for h, _ in ORCHESTRATE_SECTIONS}) == len(ORCHESTRATE_SECTIONS)
                                              and all(h and w and "Y/N" not in h + w for h, w in ORCHESTRATE_SECTIONS)),
    ("relays-name-known-events", lambda: all(e in dyadlib.ORCH_EVENT_NAMES and (t in dyadlib.ORCH_PHASES or t in (dyadlib.ORCH_DROP, dyadlib.ORCH_FROM)) for e, t in RELAYS)),
]
INVARIANTS += [   # #646: the closing line reads the questions recorded, never the wait (crafts/syseng/rules/invariants.md)
    ("disposition-request-phase-over-form", lambda: disposition_request("done-asked", "Y/N: merge PR #1?") == "done"
                                                    and disposition_request("building", "Y/N: merge PR #1?") == "none"
                                                    and disposition_request(None, "x\nY/N: admit as precedents 3?") == "precedent"
                                                    and disposition_request(None, "Y/N: runner?") == "none"
                                                    and disposition_request(None, None) == "none"),
    ("closing-default-is-a-value", lambda: CLOSING_DEFAULT in CLOSING_VALUES and set(REQUEST_PHASES.values()) <= set(AWAITING_KINDS)
                                           and {k for _, k in REQUEST_FORMS} <= set(AWAITING_KINDS)),
]
TREE_INVARIANTS = [   # loads inbox and automaton, so never at import (crafts/syseng/rules/invariants.md)
    ("kinds-are-dmc-disposition-request", lambda: {o["termCode"] for o in __import__("json").loads(
        (dyadlib.PKG / "dmc" / "disposition-request.jsonld").read_text())["hasDefinedTerm"]} == set(AWAITING_KINDS) | {REQUEST_NONE}),
    ("hp-tail-is-the-seat-keys", lambda: all((sessions()._seat_key(v) == v) == (not HP_TAIL.search(v))
                                             for v in (SOLO, "program-bob", "program-aaaaaaaa", "program-bob-cccccccc", "program-1234567"))),
    ("relays-are-information", lambda: not any(inbox().DISPOSITION.search(relay_body(587, e, t if t != dyadlib.ORCH_FROM else "plan-ready",
        {"holder": "home-1", "owner": "unit-1; unit-2", "phase": "verifying\nunit: unit-1\npr: 650 at 9bbb5cc8\nevidence: " + "0" * 64},
        "unit-2", "parts: unit-1: " + RELAY_SAMPLE["part"], {"pr": RELAY_SAMPLE["pr"], "head": RELAY_SAMPLE["head"]})[2]) for e, t in RELAYS)),
]

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
