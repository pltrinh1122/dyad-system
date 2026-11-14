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
whether the name is still live. An optional `writer` field (outside FIELDS, never validated) is
written by `touch()`: the holder's harness session id when the harness reports one, else this
process's own id (`writer()`, d-work #350). Two holders configured with the same `DYAD_SESSION`
collide on one file despite the "only that session writes it" promise above (F1, d-work #32) —
`touch()` detects a different, still-live `writer` already in the file and warns loudly instead
of silently unioning the other's rows and files into its own; a session's own later `dyad`
process carries the same holder and stays silent. Two more optional lines, written by `touch()`
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
  sessions.py reconcile                compare the live presence files with the harness's session list (#434)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("sessions.py: Python 3.12+ required")
import datetime, os, platform, re, subprocess, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib, hostadapter

ENTITY, CORPUS, TRANSACTION = "presence", "agent", False
NAME, OWNER = "session presence file", "Rule-16"
FIELDS = ("session", "seen", "root", "rows", "files")
STALE_AFTER = datetime.timedelta(hours=6)   # advisory only (#185 falsification attack 3)
_SESSION_ID = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
_PROCESS = uuid.uuid4().hex[:12]   # this process's own id, computed once at import: the fallback
                                   # writer when the harness names no holder (F1, d-work #32)
_KERNELS = frozenset({"terminal", "cloud"})   # the `host` line's first token (d-work #294)
# The seat name (Rule-16 Presence; #369 C7, d-work #379): under `organization: m4` a presence file's name has a form,
# `<function>[-<topic>]-<hp>` — the installed organization craft's data where one is installed (its `seat` guard,
# `crafts/cabinet/guards/seats_rules.txt`), this bare form otherwise. Read advisorily: `touch()` prints one line, never
# fails (the store is advisory); `dyad session name` prints the name and the session title from the environment.
ORGANIZATION = "organization"                   # the preference key (`preferences-corpus/PREFERENCES.md`; the template seeds it)
ORGANIZATIONS = ("flat", "m4")                  # one pair, one board, no form read | the tree of cos-boards (plan #369)
DEFAULT_ORGANIZATION = "m4"                     # the Operator's default (#369: "codify M4 as the default organizational preference")
SEAT_FORM = re.compile(r"^(?P<function>[a-z]+)(?:-(?P<topic>[a-z0-9]+(?:-[a-z0-9]+)*))?-(?P<hp>[0-9a-f]{8})$")   # plan #369 revision 10
HP_LEN = 8                                      # `<hp>`: the first eight hex of the holder's harness session id
LEADER_FUNCTION = "program"                     # the function whose bare seat is the leader (revision 10)
# Attendance (Rule-16 Presence; d-work #388 children 1–3 as #393, declared by #412 C2 as #414): which seats an Operator
# sits at is declared by the `paired-units` preference — the leader always, the listed seats beside it, `none` the
# default — and checked against the provenance records: a seat holds an own disposition when a record whose `session:`
# line names it holds a disposition given there (a note holding neither `mandate #` nor `relayed via`, #422) within the
# `attendance-window` preference. A live undeclared seat holding one prints `undeclared`; a declared seat holding none, `warn`.
PAIRED_UNITS = "paired-units"                   # the preference key (#553): unit names beside the leader, or `none` (the template seeds `none`)
RETIRED_KEYS = {"attended-seats": PAIRED_UNITS}  # #604: a retired key -> its name; no longer read, and a table holding it fails
UNIT_KINDS = ("dyad", "solo", "auto")           # #553: a paired (attended) unit, an unpaired one, an automaton's (none keeps a presence file yet)
NO_SEATS = "none"
ATTENDANCE_WINDOW = "attendance-window"         # the preference key: days, a tunable whose default is dmc/attendance-check.jsonld's (#590)
ATTENDANCE_MODES = ("M3", "M4", "hybrid")       # only the leader attended | every live seat | some (#366, #388)
ROUTES = ("chat", "relayed")                    # where a seat's counter-prompt is asked: its own chat, or through the leader (R29)
_RECORD_SESSION = re.compile(r"^session:\s*(\S+)\s*$", re.M)
_MANDATE_NOTE, _RELAYED_NOTE = "mandate #", "relayed via"
_DONE_NOTE = "done #"   # #574 G6: a Done's words copied onto a row it retires, given on that row, never in this seat
_BY_REFERENCE_NOTE = "by reference"   # #545: a hosting approval (provenance.BY_REFERENCE), given in no seat
_MANDATE_PREFERENCE_NOTE = "mandate preference"   # #692: the grant's words copied onto a row a mandate preference opens
# Reconcile (d-work #434, child C1 of #431): the live presence files against the harness's own session list
# (`hostadapter.harness_sessions`), one line per mismatch — the operate seat's run-book health command, advisory, never
# a guard failure. A title in the seat form begins with the prefix `dyad session name` prints, `<seat>: <kernel> (<system>)`,
# followed by the end or a separator and any text — ` - <on>`, or a suffix the harness appends (observed: ` - operate`).
TITLE_FORM = re.compile(r"^(?P<seat>\S+): (?P<kernel>\S+) \((?P<system>[^()]*)\)(?:\s*[-–—|:·,]\s*(?P<on>.*))?$")
READINGS = ("no harness session", "no presence", "title differs", "stale while titled")
FETCH_TIMEOUT = 10                              # #592 R-e (mode 07): seconds `touch` gives `git fetch` before it reports and goes on
CLI_FLAGS = dyadlib.cli_forms("session")   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
NO_LIVE_SEAT = "no live seat"                   # #592 (mode 28): `session list` with no live seat reads no mode
INVARIANTS = [("fields-are-five", lambda: FIELDS == ("session", "seen", "root", "rows", "files")),
              ("stale-window-positive", lambda: STALE_AFTER.total_seconds() > 0),
              ("organizations-hold-the-default", lambda: DEFAULT_ORGANIZATION in ORGANIZATIONS and len(set(ORGANIZATIONS)) == 2),
              ("seat-form-names-its-three-groups", lambda: set(SEAT_FORM.groupindex) == {"function", "topic", "hp"} and bool(SEAT_FORM.match("engineer-ledgerd-1537d8fb")) and not SEAT_FORM.match("cos-1")),
              ("hp-is-eight-hex", lambda: HP_LEN == 8 and bool(SEAT_FORM.match(f"{LEADER_FUNCTION}-{'a' * HP_LEN}"))),
              ("attendance-modes-and-routes", lambda: len(set(ATTENDANCE_MODES)) == 3 and ROUTES == ("chat", "relayed")),
              ("declared-default-is-none", lambda: NO_SEATS == "none" and PAIRED_UNITS == "paired-units" and UNIT_KINDS[:2] == ("dyad", "solo")),
              ("retired-keys-name-their-key", lambda: RETIRED_KEYS == {"attended-seats": PAIRED_UNITS} and PAIRED_UNITS not in RETIRED_KEYS),
              ("reconcile-readings-are-four", lambda: len(set(READINGS)) == 4 and bool(TITLE_FORM.match("engineer-1537d8fb: cloud (ds) - ledger")) and not TITLE_FORM.match("dyad-system-ea")),
              ("fetch-is-bounded", lambda: 0 < FETCH_TIMEOUT <= 10 and NO_LIVE_SEAT == "no live seat"),
              ("process-id-is-well-formed", lambda: bool(re.fullmatch(r"[0-9a-f]{12}", _PROCESS)))]   # crafts/syseng/rules/invariants.md
TREE_INVARIANTS = [   # reads the DMC store, so the runner's pass only, never at import
    ("attendance-window-is-the-record", lambda: dyadlib.tunables_read_by("guards/agent/sessions.py") == {ATTENDANCE_WINDOW}),   # #590: one home
]

def sessions_dir(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / "d-work" / "sessions"

def session_id() -> str:
    """`DYAD_SESSION` when set and shaped like a path segment; else (reads only: `touch()` refuses, #480) a fresh id *each call*, so an
    unconfigured caller never overwrites another session's file merely by chance of naming — it
    simply gets whichever fresh id the caller resolved once (#185). Not memoized: a caller needing
    one stable value per logical operation resolves it once and threads it through (`touch()`
    does); the identity for detecting two holders sharing one configured session name is
    `writer()` instead (F1, d-work #32; the holder since #350), its fallback `_PROCESS` computed
    once at import."""
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

def writer() -> str:
    """Who is writing: the harness session id when the harness reports one — the same value the
    `holder` line carries, stable across every `dyad` invocation that session makes, so a session
    re-touching its own file matches itself and stays silent and only a *different* holder under
    the same `DYAD_SESSION` warns (d-work #350). The fence of #32 compared a uuid computed per
    process, and every `dyad` command is its own process, so it warned on a session's own previous
    command every time; with no harness id the per-process uuid is all there is, as before."""
    return holder() or _PROCESS

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
    """The reading rule of the form: `leader` (the leader function, bare), `secretary` (another function, bare),
    `desk` (a function and a topic); `unknown-function` when the craft's list is known and does not hold it."""
    if functions is not None and seat["function"] not in functions:
        return "unknown-function"
    if seat["topic"]:
        return "desk"
    return "leader" if seat["function"] == LEADER_FUNCTION else "secretary"

def name_problems(sid: str, root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Advisory lines about a seat name under `organization: m4`: outside the form, or a function the installed
    craft does not list, or a leader whose operator segment ends in eight hex (#594: it reads as a `-<hp>`, so no
    cabinet is recognised), or an `<hp>` that is not the holder's. Empty under `flat`, and never a guard failure."""
    if organization(root) != "m4":
        return []
    form, functions, source = seat_form(pkg)
    seat = parse_seat(sid, form)
    if seat is None:
        return [f"seat name {sid!r} is outside the form <function>[-<topic>]-<hp> ({source}; Rule-16 Presence, organization m4) — `dyad session name` prints one"]
    out = []
    if seat_kind(seat, functions) == "unknown-function":
        out.append(f"seat name {sid!r}: function {seat['function']!r} is none of {', '.join(functions or [])} (the organization craft's data)")
    if seat["function"] == LEADER_FUNCTION and seat["topic"] and re.search(r"-[0-9a-f]{%d}$" % HP_LEN, "-" + seat["topic"]):
        out.append(f"seat name {sid!r}: the operator segment {seat['topic']!r} ends in {HP_LEN} hex, which reads as a `-<hp>`: "
                   f"this leader's cabinet is not recognised (board.valid_cabinet, #594) — name the operator otherwise")
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
    so a plan using brace shorthand under-reports rather than corrupts. A token is kept only if
    it is path-shaped (`_is_path`), and a matched line that names text but no path at all is
    prose that happens to begin with the phrase: it contributes nothing and takes no continuation
    lines (#350). Not attempted here: the `## files touched` heading form some plans use (#174,
    #181) is not this pattern and is not read; a stated limitation, not a crash."""
    lines, out, i = plan_text.splitlines(), [], 0
    while i < len(lines):
        m = re.match(r"^\s*files touched(?: \([^)]*\))?:\s*(.*)$", lines[i], re.I)
        if not m:
            i += 1; continue
        first = _path_tokens(m.group(1)); i += 1
        if m.group(1).strip() and not first:
            continue                     # prose that begins with the phrase: no paths, no continuation
        out += first
        chunk = []
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith("#"):
            chunk.append(lines[i]); i += 1
        out += _path_tokens(" ".join(chunk))
    return out

_PATH_TOKEN = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_.*-]*(?:/[A-Za-z0-9_.*-]+)*/?")
_EXTENSION = re.compile(r"\.[A-Za-z0-9]{1,8}$")

def _is_path(tok: str) -> bool:
    """A token that can be a repo path: made of path characters, and either has a directory
    separator or ends in an extension. `amends`, `twenty-three`, `PR-4` and `(ledger-only` are
    prose, not paths (d-work #350: plan 336 mentions the phrase `files touched` 17 times in running
    text and the union held every word after it). Under-reports a bare top-level name with no
    extension (`Makefile`) — advisory, so a missed signal costs nothing a corruption would."""
    return bool(_PATH_TOKEN.fullmatch(tok)) and ("/" in tok or bool(_EXTENSION.search(tok)))

def _path_tokens(text: str) -> list[str]:
    out = []
    for tok in re.split(r"[,\s]+", text.strip()):
        tok = tok.strip().strip("`'\"()").rstrip(".,;:")
        # splitting on the comma inside a `{a,b}` group breaks it into two brace-bearing
        # fragments (`x/{a` and `b}*.md`); both, and any other brace fragment, are dropped
        # whole rather than partially parsed (#185: a real plan's own shorthand corrupted
        # the store the first time this ran). A bare "(new)"-style annotation, `and` and a
        # dash are not path-shaped and fall to `_is_path`.
        if tok and "{" not in tok and "}" not in tok and _is_path(tok):
            out.append(tok)
    return out

class SessionUnset(Exception):
    """#480 P2 (modes Q/R): a write with no usable `DYAD_SESSION` would mint a stray `unnamed-*` file."""

def plan_files(root: Path, rid: str) -> list[str]:
    """The files the row's stored plan file names (Rule-15), [] when it has none."""
    p = dyadlib.instance(root) / "d-work" / "plans" / f"{rid}.md"
    return files_touched(p.read_text(errors="ignore")) if p.exists() else []

def files_of_rows(root: Path, rows) -> list[str]:
    """#567 F4 (#311 item 1): the union of `files touched:` over the rows' stored plans — what `files` derives from."""
    return sorted({f for rid in rows for f in plan_files(root, str(rid).lstrip("#"))})

def board_owners(root: Path, rid: str) -> list[str]:
    """The seats the row's board entry names as `owner` (#551 co-owners); [] when it has no entry or names none."""
    b = dyadlib.load_guard("agent", "board")
    p = b.store(root) / f"{rid}.md"
    return b.owners(b.parse(p.read_text(errors="replace"))[0]) if p.exists() else []

def claim(root: Path, rows) -> list[str]:
    """#567 F1/F3: the rows of `rows` this unit may claim — those whose board entry names `DYAD_SESSION` among its
    owners, or names no owner at all (a flat system, a self-run row). Under m4 the home records the plan-`Y` of rows
    other units run; the owner gate keeps them off its file, so #130's instance-wide claim does not come back."""
    sid = os.environ.get("DYAD_SESSION", "")
    out = []
    for r in rows:
        rid = str(r).lstrip("#")
        o = board_owners(root, rid)
        if not o or sid in o:
            out.append(rid)
    return out

def owned_rows(root: Path) -> list[str]:
    """The non-terminal rows whose board entry names `DYAD_SESSION` among its owners (the no-argument touch, #130)."""
    sid = os.environ.get("DYAD_SESSION", "")
    b = dyadlib.load_guard("agent", "board")
    states = {str(r.id): r.state for r in dyadlib.read_rows(root)}
    return sorted((n for n, f in b.load(root) if not b.is_cos(n) and sid in b.owners(f)
                   and states.get(n) not in (None, *dyadlib.TERMINAL_STATES)), key=int)

def touch(root: Path, rows: list[str], files: list[str], here: Path | None = None) -> Path:
    """Write this unit's presence file under `root`'s instance. `here` is the checkout the unit runs `dyad` from, the
    `root:` line; it defaults to `root` and differs only when a land writes the file in its own worktree (#567)."""
    if not _SESSION_ID.match(os.environ.get("DYAD_SESSION", "")):   # #480 P2: before any write; reads keep session_id()'s fallback
        raise SessionUnset("refused: set DYAD_SESSION=<seat> (a path-safe name) before `session touch` — nothing written")
    root = root or dyadlib.repo_root()
    d = sessions_dir(root); d.mkdir(parents=True, exist_ok=True)
    sid = session_id()   # resolved once (F4, d-work #32): the path and the body must agree
    p = d / f"{sid}.md"
    prev = parse(p.read_text()) if p.exists() else {}
    prev_writer, me = prev.get("writer"), writer()
    if prev_writer and prev_writer != me and not is_stale(prev.get("seen", "")):
        print(f"warning: {p.name} was last written by a different, still-live process "
              f"(writer {prev_writer}, this one is {me}) under this same session id {sid!r} — two sessions "
              f"configured with the same DYAD_SESSION silently merge their presence otherwise "
              f"(F1, d-work #32); recording only this process's rows and files, not unioning "
              f"the other's", file=sys.stderr)
        row_set = {r.lstrip("#") for r in rows}
        file_set = set(files)
    else:
        row_set = set(prev.get("rows", "").split()) | {r.lstrip("#") for r in rows}
        file_set = set(prev.get("files", "").split()) | set(files)
    # #567 F3/F4: a row now terminal or gone leaves the file, with the files only its plan named; `files` gains every
    # claimed row's plan files (#311), so `-r` alone no longer writes it empty
    states = {str(r.id): r.state for r in dyadlib.read_rows(root)} if dyadlib.rows_dir(root).is_dir() else {}
    if states:   # a store that holds no row judges nothing
        dropped = {r for r in row_set if states.get(r) in dyadlib.TERMINAL_STATES or (r.isdigit() and r not in states)}
        row_set -= dropped
        file_set -= set(files_of_rows(root, dropped)) - set(files_of_rows(root, row_set)) - set(files)
    file_set |= set(files_of_rows(root, row_set))
    row_set = sorted(row_set, key=lambda r: (not r.isdigit(), int(r) if r.isdigit() else 0, r))
    file_set = sorted(file_set)
    p.write_text(f"session: {sid}\n"
                 f"seen: {datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')}\n"
                 f"root: {Path(here or root).resolve()}\n"
                 f"rows: {' '.join(row_set)}\n"
                 f"files: {' '.join(file_set)}\n"
                 f"writer: {me}\n"
                 f"host: {host_line()}\n"
                 + (f"holder: {h}\n" if (h := holder()) else ""))
    for w in name_problems(sid, root):   # advisory (Rule-16 Presence): the seat name against the organization's form
        print(f"warning: {w}", file=sys.stderr)
    return p

def attendance_window(root: Path | None = None) -> datetime.timedelta:
    """The `attendance-window` preference as days (a positive integer), read through `dyadlib.tunable`: the DMC default
    (dmc/attendance-check.jsonld) when absent or malformed (#590)."""
    try:
        return datetime.timedelta(days=dyadlib.tunable(ATTENDANCE_WINDOW, root))
    except OverflowError:   # a valid but huge preference falls back, as a malformed one does (#590)
        return datetime.timedelta(days=dyadlib.tunable_default(ATTENDANCE_WINDOW))

def own_disposition(note: str) -> bool:
    """A disposition the Operator gave in the seat whose record holds it: its note holds, anywhere, neither a mandate's
    words copied onto an accreted row (`mandate #<id>, <date>`, Rule-7 property 4) nor `relayed via` another seat.
    Anywhere, not only at the start (#422): the accreted rows closed before `dwork state <id> done --mandate <id>`
    existed carry the note `Y done (mandate #<id>, <date>)`, and they read silent without rewriting a record
    (Rule-7 property 4: a record only grows). Nor `by reference` (#545): a hosting approval recorded by reference was
    given on the hosting, in no seat. Nor `mandate preference` (#692): the words that granted a standing mandate,
    copied onto each row it opens, were given where the grant was."""
    n = note.strip()
    return all(m not in n for m in (_MANDATE_NOTE, _RELAYED_NOTE, _BY_REFERENCE_NOTE, _DONE_NOTE, _MANDATE_PREFERENCE_NOTE))

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

def declared_preference(root: Path | None = None) -> tuple[str, str | None]:
    """(key, value) of the pairing preference `paired-units` (#553). Its old name `attended-seats` is no longer read
    (#604); a table still holding it fails the guard (`retired_key_problems`) rather than reading as unpaired."""
    return PAIRED_UNITS, dyadlib.preference(PAIRED_UNITS, root)

def declared_seats(root: Path | None = None) -> list[str]:
    """The `paired-units` preference (#553) as a sorted list of entries: [] when the key is
    absent or holds `none` (the default, #412: only the leader paired). Words are split on spaces and commas; `none`
    beside a name is dropped."""
    words = str(declared_preference(root)[1] or "").replace(",", " ").split()
    return sorted({w for w in words if w != NO_SEATS})

def _seat_key(name: str) -> str:
    """A seat name without its `-<hp>` suffix: the function and topic, which outlive a change of holder."""
    m = re.fullmatch(r"(.+)-[0-9a-f]{%d}" % HP_LEN, name)
    return m.group(1) if m else name

def declares(entries: list[str], seat: str) -> bool:
    """True when a `paired-units` entry names `seat`: its full seat name, or the name without `-<hp>`
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

ATTENTION_UNNAMED = ("attention: this home's checkout names no central repository (git config dyad.attention.clone "
                     "<path>); the operator's desks are not logged")

def attention_warning(root: Path, seat: str | None) -> str | None:
    """#703: the one line the home prints when its checkout names no central repository; None for any other unit, or
    when one is named. It reads this checkout's git config alone, never the network, and never refuses."""
    if not seat or not is_leader(seat):
        return None
    r = subprocess.run(["git", "config", "--get", "dyad.attention.clone"], cwd=root, capture_output=True, text=True,
                       env=dyadlib.git_env())
    return None if r.returncode == 0 and r.stdout.strip() else ATTENTION_UNNAMED

def attendance(root: Path | None = None, now: datetime.date | None = None) -> dict:
    """The mode read over the live seats (plan #388 child 2, declared by #412): {mode, attended: {seat: date or ""},
    relayed: [seat], leaders: [seat], declared: [entry], undeclared: [(seat, date)], warnings: [entry], window_days}.
    Attended = the live leaders ∪ the live seats `paired-units` declares; the value is the seat's latest own
    disposition within the window, "" when it holds none. Only leaders attended → M3 (the default, and the reading
    with no live seat); every live seat attended → M4; otherwise hybrid. The record-derived reading is the fence: a
    relayed live seat holding an own disposition within the window is `undeclared` (read over the live seats, as the
    mode is: a seat past the stale window is off the board); an entry that names no seat holding one is a warning (the
    Operator declared a seat and has not disposed there within the window)."""
    root = root or dyadlib.repo_root()
    form, functions, _ = seat_form()
    index, live = attendance_index(root, now), [s.get("session", s["_path"].removesuffix(".md")) for s in live_seats(root)]
    declared = declared_seats(root)
    leaders = [s for s in live if is_leader(s, form, functions)]
    att = {s: index.get(s, "") for s in live if s in leaders or declares(declared, s)}
    relayed = [s for s in live if s not in att]
    undeclared = sorted((s, index[s]) for s in relayed if s in index)
    warnings = [e for e in declared if not any(e == s or e == _seat_key(s) for s in index)]
    mode = "M3" if set(att) <= set(leaders) else ("M4" if not relayed else "hybrid")
    return {"mode": mode, "attended": att, "relayed": relayed, "leaders": leaders, "declared": declared,
            "undeclared": undeclared, "warnings": warnings, "window_days": attendance_window(root).days,
            "retired": retired_key_problems(root)}   # #604: the reading that drops a retired key says so

def route(seat: str, root: Path | None = None, now: datetime.date | None = None) -> str:
    """Plan #388 child 3: where a counter-prompt this seat owes the Operator is asked — `chat` (its own) when the seat is
    attended, `relayed` (through the leader, verbatim both ways, R29) otherwise."""
    return ROUTES[0] if seat in attendance(root, now)["attended"] else ROUTES[1]

def attendance_line(a: dict) -> str:
    """The mode line of `session list`; `no live seat` when none is live (#592, mode 28: an empty board is no mode)."""
    n_live = len(a["attended"]) + len(a["relayed"])
    if n_live == 0:
        return NO_LIVE_SEAT
    return (f"mode: {a['mode']} — {len(a['attended'])} of {n_live} live unit(s) dyad, the rest solo; paired: "
            f"{' '.join(a['declared']) or NO_SEATS} beside the leader (`{PAIRED_UNITS}`, Rule-16 "
            f"Presence; a solo unit's questions are relayed through the leader)")

def fence_lines(a: dict) -> list[str]:
    """The record-derived check against the declared set, one line each (#412): `undeclared` for a disposition given in
    an undeclared seat, `warn` for a declared entry with none within the window. A board reading, not a Rule-3
    incident: the act it shows is the Operator's, and the leader, which tracks attendance, is its one reporter. A retired
    key the table still holds (#604) prints one `refused:` line, so the reading that does not read it says so."""
    return ([f"undeclared: {s} holds an own disposition of {d} but `{PAIRED_UNITS}` does not pair it (Rule-16 Presence)"
             for s, d in a["undeclared"]]
            + [f"warn: {e} is paired but holds no own disposition within {a['window_days']} day(s)"
               for e in a["warnings"]]
            + [f"refused: {m}; until then this reading pairs none of its units" for m in a.get("retired", [])])

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
        if args[i] in CLI_FLAGS["name"].value_flags and i + 1 < len(args):
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

def refresh_in(wt: Path, inst: str, candidates, here: Path) -> str | None:
    """#567: refresh this unit's own presence inside a land's worktree `wt` (instance `inst`, repo-relative), claiming
    only the `candidates` that `claim` gives it against the board as it stands there; the caller's checkout `here` is
    the `root:` line. Returns the presence path relative to `wt` for the land's commit, or None when `DYAD_SESSION`
    is unset or not path-safe — a land never fails for want of a presence file (Rule-16: advisory)."""
    if not _SESSION_ID.match(os.environ.get("DYAD_SESSION", "")):
        return None
    saved = os.environ.get("DYAD_INSTANCE")
    os.environ["DYAD_INSTANCE"] = inst
    try:
        p = touch(wt, claim(wt, candidates), [], here=here)
    finally:
        if saved is None:
            os.environ.pop("DYAD_INSTANCE", None)
        else:
            os.environ["DYAD_INSTANCE"] = saved
    return p.relative_to(wt).as_posix()

def touch_owned(root: Path | None = None) -> Path:
    """The no-argument `session touch` (session start, Rule-16): the rows already claimed ∪ the board rows that name
    this unit as an owner, with their plans' files — never every open row of the instance (#130, plan #567)."""
    root = root or dyadlib.repo_root()
    return touch(root, owned_rows(root), [])

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

def is_stale(seen: str, now: datetime.datetime | None = None) -> bool:
    try:
        t = datetime.datetime.fromisoformat(seen)
    except ValueError:
        return True
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.UTC)
    return (now or datetime.datetime.now(datetime.UTC)) - t > STALE_AFTER

def session_overlap(my_files: set[str], my_root: str, other: dict[str, str]) -> str:
    """dmc:session-overlap (#641): one other session's presence file against this session's new plan.
    `same-root` (same root) when its `root` is this session's, the sharper signal, which outranks a file overlap;
    `overlap` (overlaps) when its `files` set meets the plan's touched files; `disjoint` (different) otherwise."""
    if my_root and (other.get("root") or "") == my_root:
        return "same-root"
    return "overlap" if my_files & set((other.get("files") or "").split()) else "disjoint"

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
            if s.get("session") != exclude and shares_checkout(s, here) and not is_stale(s.get("seen", ""))]

def shares_checkout(s: dict[str, str], here: str, me_host: str | None = None, me_holder: str | None = None) -> bool:
    """True when presence file `s` may share this process's checkout: the same `root`, and — when both sides record
    them — the same `host` line, and not two different holders on a `cloud` kernel: separate cloud containers have the
    same path and never one filesystem (#434, the operate seat's report). A side that records no
    host or no holder cannot be told apart, so it still counts: the signal errs toward warning."""
    if s.get("root") != here:
        return False
    me_host = me_host if me_host is not None else host_line()
    me_holder = me_holder if me_holder is not None else holder()
    other_host, other_holder = s.get("host"), s.get("holder")
    if other_host and me_host and other_host != me_host:
        return False
    cloud = "cloud" in (me_host.split()[:1] + (other_host or "").split()[:1])
    if cloud and other_holder and me_holder and other_holder != me_holder:
        return False
    return True

def title_seat(title: str, form: re.Pattern | None = None) -> dict[str, str] | None:
    """{seat, kernel, system, on} when a harness session title is in the seat form `dyad session name` prints — its
    seat a name in the organization's form — else None."""
    m = TITLE_FORM.match(title or "")
    if not m or parse_seat(m.group("seat"), form) is None:
        return None
    return {k: m.group(k) or "" for k in ("seat", "kernel", "system", "on")}

def _holder_match(h: str, ids: list[str]) -> str | None:
    """The harness session id a presence `holder` names: the full id, or its first HP_LEN hex as a seat's `<hp>`."""
    if h in ids:
        return h
    return next((i for i in ids if len(h) == HP_LEN and i[:HP_LEN] == h), None)

def reconcile(root: Path | None = None, harness: list[dict] | None = None, now: datetime.datetime | None = None) -> list[str]:
    """The live presence files against the harness's own session list (d-work #434, child C1 of #431), one line per
    mismatch, [] when they align or when the harness reports no session at all (a kernel that keeps no store — the
    caller is itself a session, so an empty list is the kernel's silence, never a finding):
      `no harness session: <seat>` — a live presence file whose holder (its `holder` line, else the seat name's `<hp>`)
        matches no harness session;
      `no presence: <title>` — a harness session titled in the seat form whose seat has no live presence file and
        which no live presence file holds;
      `title differs: <seat> (<title>)` — the holder's harness session title does not begin with the prefix
        `dyad session name` prints, `<seat>: <kernel> (<system>)` — the kernel compared when the presence file records
        its host, the system the main checkout's handle (`system_handle`) — followed by the end or a separator; what
        follows the separator (`- <on>`, a harness suffix) is never compared;
      `stale while titled: <seat>` — a presence file past the stale window whose holder's harness session still
        carries the seat's own seat-form title.
    Advisory: the remedy is the writer's (the seat touches; the program retitles or closes), never this reading's."""
    root = root or dyadlib.repo_root()
    harness = hostadapter.harness_sessions(root) if harness is None else harness
    if not harness:
        return []
    now = now or datetime.datetime.now(datetime.UTC)
    form, _, _ = seat_form()
    system = system_handle(hostadapter.checkouts(root)[-1])   # a worktree's titles name the repo's main checkout
    titles = {h["id"]: h.get("title") or "" for h in harness}
    ids = sorted(titles)
    out, claimed_ids, live_names = [], set(), set()
    for s in read_all(root):
        name = s.get("session") or s["_path"].removesuffix(".md")
        h = s.get("holder") or (parse_seat(name, form) or {}).get("hp")
        hid = _holder_match(h, ids) if h else None
        t = title_seat(titles.get(hid, ""), form) if hid else None
        if is_stale(s.get("seen", ""), now):
            if t and t["seat"] == name:
                out.append(f"stale while titled: {name}"); claimed_ids.add(hid)
            continue
        live_names.add(name)
        if hid is None:
            out.append(f"no harness session: {name}" + ("" if h else " (no holder line)"))
            continue
        claimed_ids.add(hid)
        kernel = (s.get("host") or "").split()[:1]
        if t is None or t["seat"] != name or t["system"] != system or (kernel and t["kernel"] != kernel[0]):
            out.append(f"title differs: {name} ({titles[hid] or 'no title recorded'})")
    for hid in ids:
        t = title_seat(titles[hid], form)
        if t and hid not in claimed_ids and t["seat"] not in live_names:
            out.append(f"no presence: {titles[hid]}")
    return out

def reconcile_report(root: Path | None = None, harness: list[dict] | None = None,
                     now: datetime.datetime | None = None) -> tuple[int, list[str]]:
    """`dyad session reconcile`: (exit code, lines) — the mismatch lines and exit 1, or one `ok` line and exit 0. A
    health command (the operate seat's run-book), never a guard: `check_package` does not call it."""
    root = root or dyadlib.repo_root()
    harness = hostadapter.harness_sessions(root) if harness is None else harness
    if not harness:
        return 0, [f"ok   [reconcile] the harness reports no session for this repo ({hostadapter.harness_dir()}); nothing to compare"]
    lines = reconcile(root, harness, now)
    live = len([s for s in read_all(root) if not is_stale(s.get("seen", ""), now)])
    if lines:
        return 1, lines + [f"{len(lines)} mismatch(es) — {live} live presence file(s), {len(harness)} harness session(s) (Rule-16 Presence; the writer remedies)"]
    return 0, [f"ok   [reconcile] {live} live presence file(s), {len(harness)} harness session(s) aligned"]

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

def retired_key_problems(root: Path | None = None) -> list[str]:
    """#604 (#573 step 4, plan B4): one failure per retired key the preference table still holds, naming its new key.
    The old key is no longer read, so ignoring it silently would unpair every unit it names."""
    return [f"preference `{old}` was removed in dyad-operator 1.0 and is no longer read; rename the key to `{new}` "
            f"(value unchanged) by a preferences PR (#604)"
            for old, new in RETIRED_KEYS.items() if dyadlib.preference(old, root) is not None]

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    msgs = []
    for p in sorted(sessions_dir(root).glob("*.md")):
        msgs += check_record(p)
    return msgs + retired_key_problems(root)

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

TOUCH_USAGE = ("usage: dyad session touch [-r <row>]... [-f <file>]... (no word: the rows already claimed and the "
               "board rows naming this unit as owner; `files` from their plans)")

def fetch_origin(root: Path, timeout: float = FETCH_TIMEOUT) -> str | None:
    """#592 R-e (mode 07): `git fetch --quiet origin`, read-only — it moves only the remote-tracking refs, never HEAD,
    the index or the working tree — bounded by `timeout` seconds and never prompting. None when it fetched; otherwise
    the reason it did not (git's last stderr line, or the timeout), which `touch` prints as a warning and goes on."""
    env = {**dyadlib.git_env(), "GIT_TERMINAL_PROMPT": "0",   # ssh opens /dev/tty itself: BatchMode fails it at once
           "GIT_SSH_COMMAND": os.environ.get("GIT_SSH_COMMAND", "ssh") + " -o BatchMode=yes"}
    try:
        r = subprocess.run(["git", "fetch", "--quiet", "origin"], cwd=root, capture_output=True, text=True, env=env,
                           timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return f"timed out after {timeout:g} s"
    except OSError as e:
        return str(e) or type(e).__name__
    if r.returncode == 0:
        return None
    lines = [l.strip() for l in (r.stderr or "").splitlines() if l.strip()]
    return lines[-1] if lines else f"git fetch exited {r.returncode}"

def behind_origin(root: Path) -> int | None:
    """#482 P4 (mode T): commits on the local `origin/main` ref that HEAD lacks — counted against the ref as last
    fetched (`touch` fetches first, `fetch_origin`, #592); None when there is no such ref or git cannot say."""
    try:
        r = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"], cwd=root, capture_output=True,
                           text=True, env=dyadlib.git_env(), timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return int(r.stdout) if r.returncode == 0 and r.stdout.strip().isdigit() else None

def main(a: list[str]) -> int:
    root = dyadlib.repo_root()
    if a and a[0] == "touch":
        if any(w in ("-h", "--help") for w in a[1:]):   # #479 P1: usage before any write
            print(TOUCH_USAGE); return 0
        rows, files, i = [], [], 1
        while i < len(a):   # #479 P1 (mode G): every word is -r <id> or -f <path>; anything else refuses, nothing written
            if a[i] in CLI_FLAGS["touch"].value_flags and i + 1 < len(a) and (a[i] == "-f" or a[i + 1].split()):   # `-r ""` claims nothing: refused
                if a[i] == "-r":
                    rows.extend(a[i + 1].split())   # #592 R-e: `-r "592 594"` claims both rows
                else:
                    files.append(a[i + 1])
                i += 2
            else:
                print(f"refused: `session touch` does not take {a[i]!r}{' without a value' if a[i] in ('-r', '-f') else ''} "
                      f"— nothing written; {TOUCH_USAGE}", file=sys.stderr)
                return 2
        try:
            p = touch(root, rows, files) if (rows or files) else touch_owned(root)
        except SessionUnset as e:
            print(e, file=sys.stderr); return 2
        print(f"touched {p.relative_to(root)}")
        n = dyadlib.load_guard("agent", "inbox").unread(root, p.stem)   # #536: the inbox is read at every turn start
        print(f"inbox {p.stem}: {n} unread" + (" — `dyad inbox read`" if n else ""))
        reason = fetch_origin(root)   # #592 R-e (mode 07): the base is stated against a fresh origin, or the line says why not
        print("fetched origin" if reason is None else f"warn [session] fetch skipped: {reason}")
        if n := behind_origin(root):   # #482 P4: the session-start report states its base; nothing when 0
            print(f"behind origin/main by {n}")
        if (w := attention_warning(root, p.stem)):   # #703: the home owes the log
            print(w)
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
    if a and a[0] == "reconcile":
        rc, lines = reconcile_report(root)
        for line in lines:
            print(line)
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
            att = ((f" dyad={a['attended'][name]}" if a["attended"][name] else " dyad") if name in a["attended"]
                   else (" solo" if name in a["relayed"] else ""))   # the unit kind (#553): paired, or not
            same_flag = " [SAME ROOT AS YOU]" if (shares_checkout(s, str(Path(root).resolve())) and s.get("session") != session_id()) else ""
            where = (f" host={s['host']}" if s.get("host") else "") + (f" holder={s['holder']}" if s.get("holder") else "")
            print(f"{s.get('session', s['_path']):24} {flag:6} seen={s.get('seen',''):20} rows={s.get('rows',''):16} files={len(s.get('files','').split())}{where}{att}{same_flag}")
        return 0
    msgs = check_package(Path(a[0]) if a else None)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        print(f"warn [sessions] {m.removeprefix('warning:').strip()}" if m.startswith("warning:") else f"FAIL [sessions] {m}")
    print(f"ok   [sessions] {summary(Path(a[0]) if a else None)}" if not fails else f"FAIL [sessions] {len(fails)} problem(s)")
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
