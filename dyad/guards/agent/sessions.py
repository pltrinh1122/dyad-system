#!/usr/bin/env python3
"""Session presence guard (entity `presence`, agent corpus; Rule-16 owns the store, placed per
Rule-11 property 1). Kernel: Python 3.12+.
A concurrent session's claim of what it is currently working, so another session reads it before
opening related work — advisory, never a lock. One file per session, only that session ever
writes it: `<instance>/d-work/sessions/<id>.md`, `key: value` lines (session, seen, root, rows,
files). `rows` is the space-list of d-work ids this session has open or planned; `files` is the
deduplicated union of every `files touched:` line from those rows' stored plan files (Rule-15) —
one signal that matters (d-work #185): two sessions on different rows about the same file. `root`
is the resolved filesystem path of the working tree this session is running `dyad` from — the
*sharper* signal (d-work #185's own near-miss, verified live): two sessions with the *same* `root`
share one mutable checkout, where a raw git command from either can clobber the other's uncommitted
state regardless of which files are in play; two sessions in separate worktrees of the same repo
never can, even with identical `files`. `seen` is an ISO-8601 UTC timestamp; the check only
validates shape (well-formed lines, a parseable timestamp) and never fails on overlap, same-root,
or staleness — a session that ended without a clean shutdown leaves a file nothing here punishes; a
reader judges freshness from `seen` and may cross-check the harness's own session directory for
whether the name is still live. An optional `writer` field (outside FIELDS, checked only when
present) is this process's own id, written by `touch()`: two *processes* configured with the same
`DYAD_SESSION` collide on one file despite the "only that session writes it" promise above (F1,
d-work #32) — `touch()` detects a different, still-live `writer` already in the file and warns
loudly instead of silently unioning the other process's rows and files into its own. Two more optional lines, written by `touch()`
from the environment and checked only when present (d-work #294): `host: <kernel> <os> <arch>`
— kernel `cloud` when the harness reports `CLAUDE_CODE_REMOTE=true`, else `terminal` (the token is
what the harness says, `terminal` when it says nothing — one harness's variable, Rule-14 property
2); os from `platform.system()` lower-cased (`darwin` → `macos`); arch `platform.machine()` — and
`holder: <harness session id>` from `CLAUDE_CODE_SESSION_ID`, absent when that is unset. Together
they say who holds the seat now; the seat is the file's name
(`agent-corpus/falsification/seat-vs-harness-session.md`, #295). Both are code-written, never
typed: a hand-added key does not survive the next `touch()`.
  sessions.py [repo-root]              check every presence file
  sessions.py touch [-r <row>]... [-f <file>]...   write/refresh this session's file
  sessions.py list                     print every file, flag one older than the stale window
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("sessions.py: Python 3.12+ required")
import datetime, os, platform, re, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "presence", "agent", False
NAME, OWNER = "session presence file", "Rule-16"
FIELDS = ("session", "seen", "root", "rows", "files")
STALE_AFTER = datetime.timedelta(hours=6)   # advisory only (#185 falsification attack 3)
_SESSION_ID = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
_WRITER = uuid.uuid4().hex[:12]   # this process's own id (F1, d-work #32): computed once at import,
                                  # so it is stable for the process's life — a session re-touching
                                  # its own file always matches its own writer and stays silent.
_KERNELS = frozenset({"terminal", "cloud"})   # the `host` line's first token (d-work #294)
# The seat name (Rule-16 Presence; #369 C7, d-work #379): under `organization: m4` a presence file's name has a form,
# `<function>[-<topic>]-<hp>` — the installed organization craft's data where one is installed (its `seat` guard,
# `crafts/cos/guards/seats_rules.txt`), this bare form otherwise. Read advisorily: `touch()` prints one line, never
# fails (the store is advisory); `dyad session name` prints the name and the session title from the environment.
ORGANIZATION = "organization"                   # the preference key (`preferences-corpus/PREFERENCES.md`; the template seeds it)
ORGANIZATIONS = ("flat", "m4")                  # one pair, one board, no form read | the tree of cos-boards (plan #369)
DEFAULT_ORGANIZATION = "m4"                     # the Operator's default (#369: "codify M4 as the default organizational preference")
SEAT_FORM = re.compile(r"^(?P<function>[a-z]+)(?:-(?P<topic>[a-z0-9]+(?:-[a-z0-9]+)*))?-(?P<hp>[0-9a-f]{8})$")   # plan #369 revision 10
HP_LEN = 8                                      # `<hp>`: the first eight hex of the holder's harness session id
LEADER_FUNCTION = "program"                     # the function whose bare seat is the leader (revision 10)
# Attendance (Rule-16 Presence; d-work #388 children 1–3 as #393, declared by #412 C2 as #414): which seats an Operator
# sits at is declared by the `attended-seats` preference — the leader always, the listed seats beside it, `none` the
# default — and checked against the provenance records: a seat holds an own disposition when a record whose `session:`
# line names it holds a disposition given there (noted neither `mandate #<id>` nor `relayed via`) within the
# `attendance-window` preference. A live undeclared seat holding one is an incident; a declared seat holding none, a warning.
ATTENDED_SEATS = "attended-seats"               # the preference key: seat names beside the leader, or `none` (the template seeds `none`)
NO_SEATS = "none"
ATTENDANCE_WINDOW = "attendance-window"         # the preference key: days (the template seeds 7)
DEFAULT_ATTENDANCE_DAYS = 7
ATTENDANCE_MODES = ("M3", "M4", "hybrid")       # only the leader attended | every live seat | some (#366, #388)
ROUTES = ("chat", "relayed")                    # where a seat's counter-prompt is asked: its own chat, or through the leader (R29)
_RECORD_SESSION = re.compile(r"^session:\s*(\S+)\s*$", re.M)
_MANDATE_NOTE, _RELAYED_NOTE = "mandate #", "relayed via"
INVARIANTS = [("fields-are-five", lambda: FIELDS == ("session", "seen", "root", "rows", "files")),
              ("stale-window-positive", lambda: STALE_AFTER.total_seconds() > 0),
              ("organizations-hold-the-default", lambda: DEFAULT_ORGANIZATION in ORGANIZATIONS and len(set(ORGANIZATIONS)) == 2),
              ("seat-form-names-its-three-groups", lambda: set(SEAT_FORM.groupindex) == {"function", "topic", "hp"} and bool(SEAT_FORM.match("engineer-ledgerd-1537d8fb")) and not SEAT_FORM.match("cos-1")),
              ("hp-is-eight-hex", lambda: HP_LEN == 8 and bool(SEAT_FORM.match(f"{LEADER_FUNCTION}-{'a' * HP_LEN}"))),
              ("attendance-modes-and-routes", lambda: len(set(ATTENDANCE_MODES)) == 3 and ROUTES == ("chat", "relayed") and DEFAULT_ATTENDANCE_DAYS > 0),
              ("declared-default-is-none", lambda: NO_SEATS == "none" and ATTENDED_SEATS == "attended-seats"),
              ("writer-is-well-formed", lambda: bool(re.fullmatch(r"[0-9a-f]{12}", _WRITER)))]   # crafts/syseng/rules/invariants.md

def sessions_dir(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / "d-work" / "sessions"

def session_id() -> str:
    """`DYAD_SESSION` when set and shaped like a path segment; else a fresh id *each call*, so an
    unconfigured caller never overwrites another session's file merely by chance of naming — it
    simply gets whichever fresh id the caller resolved once (#185). Not memoized: a caller needing
    one stable value per logical operation resolves it once and threads it through (`touch()`
    does); per-*process* identity, for detecting two processes sharing one configured session
    name, is `_WRITER` instead (F1, d-work #32), computed once at import."""
    v = os.environ.get("DYAD_SESSION", "")
    return v if _SESSION_ID.match(v) else f"unnamed-{uuid.uuid4().hex[:12]}"

def host_line() -> str:
    """`<kernel> <os> <arch>` as the environment says it (d-work #294): `cloud` when the harness
    sets `CLAUDE_CODE_REMOTE=true`, else `terminal` — what the harness reports, `terminal` when it
    reports nothing (Rule-14 property 2: one harness's variable, never the dyad's); the OS and
    arch come from Python and hold on any kernel. Spaces in a token are collapsed so the line
    always parses back to exactly three tokens."""
    kernel = "cloud" if os.environ.get("CLAUDE_CODE_REMOTE", "").lower() == "true" else "terminal"
    system = platform.system().lower() or "unknown"
    system = {"darwin": "macos"}.get(system, system)
    machine = platform.machine() or "unknown"
    return " ".join(t.replace(" ", "_") for t in (kernel, system, machine))

def holder() -> str | None:
    """The harness session id holding this seat now (`CLAUDE_CODE_SESSION_ID`), or None when the
    harness sets none — then no `holder` line is written (d-work #294, #295)."""
    v = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return v if _SESSION_ID.match(v) else None

def parse(text: str) -> dict[str, str]:
    return dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)

def organization(root: Path | None = None) -> str:
    """The `organization` preference: `m4` when the preferences corpus exists and the key is absent or holds a value
    outside ORGANIZATIONS (the default the Operator set, #369; the template seeds it); `flat` — one pair, no seat
    form read — when the system keeps no preferences corpus at all (a tree that is not yet a seeded instance, as
    the preference guard reads a missing live corpus)."""
    if not ((root or dyadlib.repo_root()) / dyadlib.PREFERENCES_REL).is_file():
        return "flat"
    v = dyadlib.preference(ORGANIZATION, root)
    return v if v in ORGANIZATIONS else DEFAULT_ORGANIZATION

def seat_form(pkg: Path = dyadlib.PKG) -> tuple[re.Pattern, list[str] | None, str]:
    """(form, functions, source): the installed organization craft's seat form and its standing functions (its `seat`
    guard's `rules()`, corpus `agent`), source `craft`; else the bare SEAT_FORM, no function list, source `core`. A
    craft whose data does not load gives the bare form too — the reading is advisory, so nothing here may fail."""
    g = dyadlib.find_guard("agent", "seat", pkg)
    if g is not None and callable(getattr(g, "rules", None)):
        try:
            form, functions = g.rules()
            return form, list(functions), "craft"
        except (OSError, ValueError, TypeError, AttributeError, re.error):
            pass
    return SEAT_FORM, None, "core"

def parse_seat(name: str, form: re.Pattern | None = None) -> dict[str, str | None] | None:
    """{function, topic, hp} when `name` is in the form, else None."""
    m = (form or SEAT_FORM).match(name)
    return {"function": m.group("function"), "topic": m.group("topic"), "hp": m.group("hp")} if m else None

def seat_kind(seat: dict[str, str | None], functions: list[str] | None) -> str:
    """The reading rule of the form: `leader` (the leader function, bare), `member-cos` (another function, bare),
    `cabinet` (a function and a topic); `unknown-function` when the craft's list is known and does not hold it."""
    if functions is not None and seat["function"] not in functions:
        return "unknown-function"
    if seat["topic"]:
        return "cabinet"
    return "leader" if seat["function"] == LEADER_FUNCTION else "member-cos"

def name_problems(sid: str, root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Advisory lines about a seat name under `organization: m4`: outside the form, or a function the installed
    craft does not list, or an `<hp>` that is not the holder's. Empty under `flat`, and never a guard failure."""
    if organization(root) != "m4":
        return []
    form, functions, source = seat_form(pkg)
    seat = parse_seat(sid, form)
    if seat is None:
        return [f"seat name {sid!r} is outside the form <function>[-<topic>]-<hp> ({source}; Rule-16 Presence, organization m4) — `dyad session name` prints one"]
    out = []
    if seat_kind(seat, functions) == "unknown-function":
        out.append(f"seat name {sid!r}: function {seat['function']!r} is none of {', '.join(functions or [])} (the organization craft's data)")
    h = holder()
    if h and seat["hp"] != h[:HP_LEN]:
        out.append(f"seat name {sid!r}: <hp> {seat['hp']} is not this holder's ({h[:HP_LEN]}…) — a renamed session or a reused file")
    return out

def files_touched(plan_text: str) -> list[str]:
    """A stored plan's own `files touched:` line (Rule-15) and any continuation lines that
    follow it up to a blank line or a heading — real plans wrap a long list across several
    physical lines (#24, #179, #185 among them). Bare paths, comma- or space-separated, a
    trailing `(...)` annotation and punctuation stripped. A `{a,b}`-brace shorthand group is
    dropped whole rather than split on the comma inside it, which produced a garbled fragment
    the first time this ran over a real plan (#185, this d-work's own plan file) — advisory,
    so a plan using brace shorthand under-reports rather than corrupts. Not attempted here: the
    `## files touched` heading form some plans use (#174, #181) is not this pattern and is not
    read; a stated limitation, not a crash."""
    lines, out, i = plan_text.splitlines(), [], 0
    while i < len(lines):
        m = re.match(r"^\s*files touched(?: \([^)]*\))?:\s*(.*)$", lines[i], re.I)
        if not m:
            i += 1; continue
        chunk = [m.group(1)]; i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith("#"):
            chunk.append(lines[i]); i += 1
        for tok in re.split(r"[,\s]+", " ".join(chunk).strip()):
            tok = tok.strip().rstrip(".,;")
            # splitting on the comma inside a `{a,b}` group breaks it into two brace-bearing
            # fragments (`x/{a` and `b}*.md`); both, and any other brace fragment, are dropped
            # whole rather than partially parsed (#185: a real plan's own shorthand corrupted
            # the store the first time this ran).
            if (tok and tok not in ("and", "—", "-") and "{" not in tok and "}" not in tok
                    and not re.fullmatch(r"\([^()]*\)", tok)):   # a bare "(new)"-style annotation
                out.append(tok)
    return out

def touch(root: Path, rows: list[str], files: list[str]) -> Path:
    root = root or dyadlib.repo_root()
    d = sessions_dir(root); d.mkdir(parents=True, exist_ok=True)
    sid = session_id()   # resolved once (F4, d-work #32): the path and the body must agree
    p = d / f"{sid}.md"
    prev = parse(p.read_text()) if p.exists() else {}
    prev_writer = prev.get("writer")
    if prev_writer and prev_writer != _WRITER and not is_stale(prev.get("seen", "")):
        print(f"warning: {p.name} was last written by a different, still-live process "
              f"(writer {prev_writer}) under this same session id {sid!r} — two sessions "
              f"configured with the same DYAD_SESSION silently merge their presence otherwise "
              f"(F1, d-work #32); recording only this process's rows and files, not unioning "
              f"the other's", file=sys.stderr)
        row_set = sorted({r.lstrip("#") for r in rows})
        file_set = sorted(set(files))
    else:
        row_set = sorted(set(prev.get("rows", "").split()) | {r.lstrip("#") for r in rows})
        file_set = sorted(set(prev.get("files", "").split()) | set(files))
    p.write_text(f"session: {sid}\n"
                 f"seen: {datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')}\n"
                 f"root: {Path(root).resolve()}\n"
                 f"rows: {' '.join(row_set)}\n"
                 f"files: {' '.join(file_set)}\n"
                 f"writer: {_WRITER}\n"
                 f"host: {host_line()}\n"
                 + (f"holder: {h}\n" if (h := holder()) else ""))
    for w in name_problems(sid, root):   # advisory (Rule-16 Presence): the seat name against the organization's form
        print(f"warning: {w}", file=sys.stderr)
    return p

def attendance_window(root: Path | None = None) -> datetime.timedelta:
    """The `attendance-window` preference as days (a positive integer), DEFAULT_ATTENDANCE_DAYS when absent or malformed."""
    v = dyadlib.preference(ATTENDANCE_WINDOW, root)
    try:
        days = int(str(v).split()[0]) if v else DEFAULT_ATTENDANCE_DAYS
    except ValueError:
        days = DEFAULT_ATTENDANCE_DAYS
    return datetime.timedelta(days=days if days > 0 else DEFAULT_ATTENDANCE_DAYS)

def own_disposition(note: str) -> bool:
    """A disposition the Operator gave in the seat whose record holds it: noted neither as a mandate's words copied
    onto an accreted row (`mandate #<id>, <date>`, Rule-7 property 4) nor as relayed through another seat."""
    n = note.strip()
    return not n.startswith(_MANDATE_NOTE) and _RELAYED_NOTE not in n

def attendance_index(root: Path | None = None, now: datetime.date | None = None) -> dict[str, str]:
    """{seat: latest date} over every provenance record whose `session:` line names a seat: the latest own disposition
    within the window (`attendance_window`). Derived on every call from the store, never cached in a file (#295: the
    record is the proof); a store that is absent gives {}."""
    root = root or dyadlib.repo_root()
    prov = dyadlib.load_guard("agent", "provenance")
    d = prov.store(root)
    if not d.is_dir():
        return {}
    today = now or datetime.datetime.now(datetime.UTC).date()
    window, out = attendance_window(root), {}
    for p in sorted(d.glob("*.md")):
        text = p.read_text(errors="ignore")
        m = _RECORD_SESSION.search(text)
        if not m:
            continue
        seat = m.group(1)
        for e in prov.parse(text):
            if e["kind"] != "disposition" or not own_disposition(e["note"]):
                continue
            try:
                given = datetime.date.fromisoformat(e["date"])
            except ValueError:
                continue
            if datetime.timedelta(0) <= today - given <= window and e["date"] > out.get(seat, ""):
                out[seat] = e["date"]
    return out

def declared_seats(root: Path | None = None) -> list[str]:
    """The `attended-seats` preference as a sorted list of entries: [] when the key is absent or holds `none` (the
    default, #412: only the leader attended). Words are split on spaces and commas; `none` beside a name is dropped."""
    words = str(dyadlib.preference(ATTENDED_SEATS, root) or "").replace(",", " ").split()
    return sorted({w for w in words if w != NO_SEATS})

def _seat_key(name: str) -> str:
    """A seat name without its `-<hp>` suffix: the function and topic, which outlive a change of holder."""
    m = re.fullmatch(r"(.+)-[0-9a-f]{%d}" % HP_LEN, name)
    return m.group(1) if m else name

def declares(entries: list[str], seat: str) -> bool:
    """True when an `attended-seats` entry names `seat`: its full seat name, or the name without `-<hp>`
    (`engineer` declares `engineer-1537d8fb` and every later holder of that seat)."""
    return seat in entries or _seat_key(seat) in entries

def attended(seat: str, root: Path | None = None, now: datetime.date | None = None) -> str | None:
    """The date of the latest disposition the Operator gave in `seat` within the window, or None: the record-derived
    reading (plan #388 child 1), which since #412 checks the declared set rather than defining it."""
    return attendance_index(root, now).get(seat)

def live_seats(root: Path | None = None) -> list[dict[str, str]]:
    """Every presence file whose `seen` is within the stale window, as `read_all` parses it."""
    return [s for s in read_all(root) if not is_stale(s.get("seen", ""))]

def is_leader(seat: str, form: re.Pattern | None = None, functions: list[str] | None = None) -> bool:
    parsed = parse_seat(seat, form)
    return parsed is not None and seat_kind(parsed, functions) == "leader"

def attendance(root: Path | None = None, now: datetime.date | None = None) -> dict:
    """The mode read over the live seats (plan #388 child 2, declared by #412): {mode, attended: {seat: date or ""},
    relayed: [seat], leaders: [seat], declared: [entry], incidents: [(seat, date)], warnings: [entry], window_days}.
    Attended = the live leaders ∪ the live seats `attended-seats` declares; the value is the seat's latest own
    disposition within the window, "" when it holds none. Only leaders attended → M3 (the default, and the reading
    with no live seat); every live seat attended → M4; otherwise hybrid. The record-derived reading is the fence: a
    relayed live seat holding an own disposition within the window is an incident (read over the live seats, as the
    mode is: a seat past the stale window is off the board); an entry that names no seat holding one is a warning (the
    Operator declared a seat and has not disposed there within the window)."""
    root = root or dyadlib.repo_root()
    form, functions, _ = seat_form()
    index, live = attendance_index(root, now), [s.get("session", s["_path"].removesuffix(".md")) for s in live_seats(root)]
    declared = declared_seats(root)
    leaders = [s for s in live if is_leader(s, form, functions)]
    att = {s: index.get(s, "") for s in live if s in leaders or declares(declared, s)}
    relayed = [s for s in live if s not in att]
    incidents = sorted((s, index[s]) for s in relayed if s in index)
    warnings = [e for e in declared if not any(e == s or e == _seat_key(s) for s in index)]
    mode = "M3" if set(att) <= set(leaders) else ("M4" if not relayed else "hybrid")
    return {"mode": mode, "attended": att, "relayed": relayed, "leaders": leaders, "declared": declared,
            "incidents": incidents, "warnings": warnings, "window_days": attendance_window(root).days}

def route(seat: str, root: Path | None = None, now: datetime.date | None = None) -> str:
    """Plan #388 child 3: where a counter-prompt this seat owes the Operator is asked — `chat` (its own) when the seat is
    attended, `relayed` (through the leader, verbatim both ways, R29) otherwise."""
    return ROUTES[0] if seat in attendance(root, now)["attended"] else ROUTES[1]

def attendance_line(a: dict) -> str:
    n_live = len(a["attended"]) + len(a["relayed"])
    return (f"mode: {a['mode']} — {len(a['attended'])} of {n_live} live seat(s) attended; declared: "
            f"{' '.join(a['declared']) or NO_SEATS} beside the leader (`{ATTENDED_SEATS}`, Rule-16 Presence; the others' "
            f"questions are relayed through the leader)")

def fence_lines(a: dict) -> list[str]:
    """The record-derived check against the declared set, one line each (#412): `incident` for a disposition given in
    an undeclared seat, `warn` for a declared entry with none within the window."""
    return ([f"incident: {s} holds an own disposition of {d} but `{ATTENDED_SEATS}` does not declare it (Rule-16 Presence)"
             for s, d in a["incidents"]]
            + [f"warn: {e} is declared attended but holds no own disposition within {a['window_days']} day(s)"
               for e in a["warnings"]])

def system_handle(root: Path) -> str:
    """The system's short handle in a session title, `(ds)` for dyad-system: the initials of the repository
    directory's hyphenated name, or `--system` on the command line."""
    return "".join(part[0] for part in Path(root).resolve().name.split("-") if part) or "system"

def seat_name_report(root: Path, args: list[str]) -> tuple[int, list[str]]:
    """`dyad session name [--function f] [--topic t] [--hp h] [--system s] [--on text]`: (exit code, lines). The seat
    name from the environment — the function and topic from the flags, else from `DYAD_SESSION` when it is in the
    form; the `<hp>` from the holder's id — and the harness session title to set, `<seat>: <kernel> (<system>) -
    <on>`, for the Operator to paste or compare (the organization craft's `rules/naming.md` §3). Prints only; the
    hosting is The World (Rule-14) and nothing here sets a title."""
    opts, i = {}, 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            opts[args[i][2:]] = args[i + 1]; i += 2
        else:
            return 2, [f"usage: dyad session name [--function <f>] [--topic <t>] [--hp <8 hex>] [--system <handle>] [--on <text>] (got {args[i]!r})"]
    form, functions, source = seat_form()
    current = parse_seat(session_id(), form) if os.environ.get("DYAD_SESSION") else None
    function = opts.get("function") or (current or {}).get("function")
    topic = opts.get("topic") or (current or {}).get("topic")
    h = holder()
    hp = opts.get("hp") or (h[:HP_LEN] if h else None)
    if not function:
        return 2, ["no function: pass --function <f>" + (f" (one of {', '.join(functions)})" if functions else "") + " or set DYAD_SESSION to a name in the form"]
    if not hp:
        return 2, ["no <hp>: the harness reports no CLAUDE_CODE_SESSION_ID; pass --hp <the first 8 hex of the holder's id>"]
    seat = "-".join(t for t in (function, topic, hp) if t)
    parsed = parse_seat(seat, form)
    if parsed is None:
        return 2, [f"{seat!r} is outside the form <function>[-<topic>]-<hp> ({source})"]
    kernel = host_line().split()[0]
    on = opts.get("on") or topic or function
    lines = [f"seat:   {seat} ({seat_kind(parsed, functions)}; form: {source})",
             f"holder: {h or '(none reported)'}",
             f"title:  {seat}: {kernel} ({opts.get('system') or system_handle(root)}) - {on}"]
    if os.environ.get("DYAD_SESSION") and os.environ["DYAD_SESSION"] != seat:
        lines.append(f"note:   DYAD_SESSION is {os.environ['DYAD_SESSION']!r}; the presence file keeps that name until the seat is retaken")
    return 0, lines

def touch_from_open_rows(root: Path | None = None) -> Path:
    """Session start / plan-Y (Rule-16): every row this instance's own store lists as open or
    planned, with the files each one's stored plan (if any) names."""
    root = root or dyadlib.repo_root()
    rows = [str(r.id) for r in dyadlib.read_rows(root) if r.state in ("open", "planned")]
    files = []
    for rid in rows:
        p = dyadlib.instance(root) / "d-work" / "plans" / f"{rid}.md"
        if p.exists():
            files += files_touched(p.read_text(errors="ignore"))
    return touch(root, rows, sorted(set(files)))

def read_all(root: Path | None = None) -> list[dict[str, str]]:
    root = root or dyadlib.repo_root()
    d = sessions_dir(root)
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.md")):
        fields = parse(p.read_text(errors="ignore"))
        fields["_path"] = p.name
        out.append(fields)
    return out

def is_stale(seen: str) -> bool:
    try:
        t = datetime.datetime.fromisoformat(seen)
    except ValueError:
        return True
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.UTC)
    return datetime.datetime.now(datetime.UTC) - t > STALE_AFTER

def overlaps(root: Path, my_files: set[str], exclude: str | None = None) -> list[tuple[str, set[str]]]:
    """Other sessions' presence files whose `files` set intersects `my_files` — the finding a new
    plan's falsification section states (#185); never a guard FAIL — the mechanism only surfaces
    the candidates, judgment stays inference (attack 5)."""
    out = []
    for s in read_all(root):
        if s.get("session") == exclude:
            continue
        hit = set(s.get("files", "").split()) & my_files
        if hit:
            out.append((s.get("session", s["_path"]), hit))
    return out

def same_root(root: Path, exclude: str | None = None) -> list[str]:
    """Other *live* (not stale) sessions whose recorded `root` equals this one's resolved path —
    the sharper signal a live near-miss confirmed (#185, plan addendum): two sessions in one
    mutable checkout can clobber each other's uncommitted state via a raw git command regardless
    of which files either is editing, where two sessions in separate worktrees of the same repo
    cannot. Reported at session start (Rule-3), not only before a plan; never a guard FAIL — a
    session that finds this true works through worktrees for the rest of its turn, the discipline
    stated, not enforced."""
    here = str(Path(root).resolve())
    return [s.get("session", s["_path"]) for s in read_all(root)
            if s.get("session") != exclude and s.get("root") == here and not is_stale(s.get("seen", ""))]

def check_record(p: Path, text: str | None = None) -> list[str]:
    text = p.read_text(errors="ignore") if text is None else text
    fields = parse(text)
    msgs = [f"{p.name}: field '{f}' missing" for f in FIELDS if f not in fields]
    if "seen" in fields:
        try:
            datetime.datetime.fromisoformat(fields["seen"])
        except ValueError:
            msgs.append(f"{p.name}: 'seen' is not an ISO-8601 timestamp ({fields['seen']!r})")
    # optional lines, checked only when present — never failing an absent one (d-work #294)
    if "host" in fields:
        toks = fields["host"].split()
        if len(toks) != 3:
            msgs.append(f"{p.name}: 'host' is not three tokens <kernel> <os> <arch> ({fields['host']!r})")
        elif toks[0] not in _KERNELS:
            msgs.append(f"{p.name}: 'host' kernel {toks[0]!r} is not one of {sorted(_KERNELS)}")
    if "holder" in fields and not _SESSION_ID.match(fields["holder"]):
        msgs.append(f"{p.name}: 'holder' is not a path-segment token ({fields['holder']!r})")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    msgs = []
    for p in sorted(sessions_dir(root).glob("*.md")):
        msgs += check_record(p)
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    root = root or dyadlib.repo_root()
    return f"{len(list(sessions_dir(root).glob('*.md')))} session(s)"

_ALLOWED = {"session": "free text", "seen": "ISO-8601 UTC timestamp",
            "root": "an absolute filesystem path (the working tree's resolved root)"}

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    d = sessions_dir(root); rel = d.relative_to(root) if d.is_relative_to(root) else d   # absolute DYAD_INSTANCE (rows.py does the same)
    return {"store": f"{rel}/<session>.md",
            "parser": "`sessions.parse` (key: value lines)",
            "observed": len(list(d.glob("*.md"))) if d.is_dir() else 0,
            "note": "one file per session, only that session writes it; advisory, never a lock",
            "fields": [(f, "text", _ALLOWED.get(f, "space-separated tokens"), True, "", "sessions.FIELDS") for f in FIELDS]}

def main(a: list[str]) -> int:
    root = dyadlib.repo_root()
    if a and a[0] == "touch":
        rows, files, i = [], [], 1
        while i < len(a):
            if a[i] == "-r" and i + 1 < len(a): rows.append(a[i + 1]); i += 2
            elif a[i] == "-f" and i + 1 < len(a): files.append(a[i + 1]); i += 2
            else: i += 1
        p = touch(root, rows, files) if (rows or files) else touch_from_open_rows(root)
        print(f"touched {p.relative_to(root)}")
        same = same_root(root, exclude=p.stem)   # F4, d-work #32: the id `touch()` actually wrote, not a fresh call
        if same:
            print(f"warning: same working tree as: {', '.join(same)} — a raw git command from either "
                  f"can clobber the other's uncommitted state; work through a worktree, not this checkout, "
                  f"while both are active")
        return 0
    if a and a[0] == "name":
        rc, lines = seat_name_report(root, a[1:])
        for line in lines:
            print(line, file=sys.stderr if rc else sys.stdout)
        return rc
    if a and a[0] == "list":
        rows = read_all(root)
        if not rows:
            print("no session presence files"); return 0
        a = attendance(root)
        print(attendance_line(a))
        for line in fence_lines(a):
            print(line)
        for s in rows:
            flag = "stale" if is_stale(s.get("seen", "")) else "live"
            name = s.get("session", s["_path"].removesuffix(".md"))
            att = ((f" attended={a['attended'][name]}" if a["attended"][name] else " attended") if name in a["attended"]
                   else (" relayed" if name in a["relayed"] else ""))
            same_flag = " [SAME ROOT AS YOU]" if (s.get("root") == str(Path(root).resolve()) and s.get("session") != session_id()) else ""
            where = (f" host={s['host']}" if s.get("host") else "") + (f" holder={s['holder']}" if s.get("holder") else "")
            print(f"{s.get('session', s['_path']):24} {flag:6} seen={s.get('seen',''):20} rows={s.get('rows',''):16} files={len(s.get('files','').split())}{where}{att}{same_flag}")
        return 0
    msgs = check_package(Path(a[0]) if a else None)
    for m in msgs:
        print(f"FAIL [sessions] {m}")
    print(f"ok   [sessions] {summary(Path(a[0]) if a else None)}" if not msgs else f"FAIL [sessions] {len(msgs)} problem(s)")
    return 1 if msgs else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
