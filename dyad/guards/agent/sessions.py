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
loudly instead of silently unioning the other process's rows and files into its own.
  sessions.py [repo-root]              check every presence file
  sessions.py touch [-r <row>]... [-f <file>]...   write/refresh this session's file
  sessions.py list                     print every file, flag one older than the stale window
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("sessions.py: Python 3.12+ required")
import datetime, os, re, uuid
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
INVARIANTS = [("fields-are-five", lambda: FIELDS == ("session", "seen", "root", "rows", "files")),
              ("stale-window-positive", lambda: STALE_AFTER.total_seconds() > 0),
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

def parse(text: str) -> dict[str, str]:
    return dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)

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
                 f"writer: {_WRITER}\n")
    return p

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
    if a and a[0] == "list":
        rows = read_all(root)
        if not rows:
            print("no session presence files"); return 0
        for s in rows:
            flag = "stale" if is_stale(s.get("seen", "")) else "live"
            same_flag = " [SAME ROOT AS YOU]" if (s.get("root") == str(Path(root).resolve()) and s.get("session") != session_id()) else ""
            print(f"{s.get('session', s['_path']):24} {flag:6} seen={s.get('seen',''):20} rows={s.get('rows',''):16} files={len(s.get('files','').split())}{same_flag}")
        return 0
    msgs = check_package(Path(a[0]) if a else None)
    for m in msgs:
        print(f"FAIL [sessions] {m}")
    print(f"ok   [sessions] {summary(Path(a[0]) if a else None)}" if not msgs else f"FAIL [sessions] {len(msgs)} problem(s)")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
