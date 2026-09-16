#!/usr/bin/env python3
"""Rule-19 run-book runner (owned by Rule-19; core craft). Kernel: Python 3.12+, stdlib, bash, git.
Holds the run-book *parser* (a `dyad-cmd` block: header FIELDS, blank line, the native command line),
the event store's primitives (EVENT_FIELDS, `<runbooks>/events/<instance>.jsonl`, `read_events`) and
the runner — so `dyad runbook list | run | new` works with no Tended craft installed (#155
amendment). What a run-book must *contain* (the sections, the health command, role and class
discipline) is the sysadmin craft's rule, checked by its guards `crafts/sysadmin/guards/runbooks.py`
(entity `command`) and `events.py` (entity `event`), which import this module's parser and
constants (crafts/sysarch/rules/guards.md p3: one parser, the guards re-export it). `runbook.py check` calls that guard when a
craft provides it and exits 2 when none does.

run(root, instance, name, role) — one execution path for both parties (Rule-19 property 8): prints
the commit and the run-book's sha256 (Rule-18 form), refuses a role mismatch (exit 2), pre-tests the
postcondition (`already satisfied`, exit 0, for a state-changing command), confirms a destructive
command on /dev/tty (exit 2 without one), runs the command with `bash -o pipefail -c` capturing
stdout and stderr, post-tests the postcondition, and appends one event (EVENT_FIELDS, one JSON
object per line) to `<runbooks>/events/<instance>.jsonl` — the telemetry an audit reads (property 7).
Events are append-only (the craft's events guard); an event id is `<instance>-<utc ts>-<name>`.

  runbook.py check                       check every run-book (the craft guard's CLI; exit 2 with no craft)
  runbook.py list <instance>             the commands of one run-book with class, role, section
                                         (<runbooks>/<instance>.md, else the core's dyad/runbooks/<instance>.md; #165)
  runbook.py run <instance> <name> [--as operator|agent]   execute one command (role: DYAD_ROLE, default agent)
  runbook.py new <instance>              seed <runbooks>/<instance>.md from the first crafts/*/templates/runbook.md
                                         (refuses to overwrite; exit 2 when no craft ships a template)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("runbook.py: Python 3.12+ required")
import datetime, hashlib, json, os, re, shutil, subprocess, time
from dataclasses import dataclass, asdict, fields
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

# ---- the run-book command: constants (the craft guard re-exports them; Rule-19 property 8)
FENCE = "dyad-cmd"
FIELDS = ("name", "class", "role", "undo", "postcondition", "scope")     # the header of a run-book command
CLASSES = dyadlib.HOST_CLASSES                                           # Rule-8 classes
ROLES = ("any", "operator")                                              # who may run it
CREDENTIAL_WORDS = ("sudo", "password", "token", "credential")           # force role `operator` (Rule-8: Operator-run)
NONE = "none"                                                            # an undo or postcondition that does not exist
PROSE_FENCES = {"", "bash", "sh", "shell", "console"}                    # refused by the guard: a command is a dyad-cmd block or it is prose
DEFAULT_RUNBOOKS = "workstation-corpus/runbooks"
CORE_RUNBOOKS = "dyad/runbooks"                                          # the core craft's own run-books (package; #165): the play-books' steps
SECTIONS_KEY = "sections:"                                               # header line `# sections: A, B, C` — the run-book's own section set (default: the craft rule's)
_CRED = re.compile(r"\b(" + "|".join(CREDENTIAL_WORDS) + r")\b", re.I)
_FENCE = re.compile(r"^```\s*(\S*)\s*$")

# ---- the event: constants (the craft's events guard re-exports them; Rule-19 property 7)
EVENT_FIELDS = ("id", "ts", "role", "instance", "name", "cmd", "class", "scope", "exit", "duration_ms",
                "postcondition", "output_sha256", "output_tail", "commit", "runbook_sha256")
RUN_ROLES = ("operator", "agent")                                        # who ran it (event `role`)
POSTCONDITION_RESULTS = ("n/a", "already", "ok", "failed")
TAIL_LINES, TAIL_CHARS = 5, 400

@dataclass(frozen=True)
class Command:
    name: str
    cls: str            # `class` in the header (a Python keyword)
    role: str
    undo: str
    postcondition: str
    scope: str
    cmd: str            # the command text (may span lines)
    section: str        # the `## ` heading the block sits under ("" before the first)
    line: int           # 1-based line of the opening fence

@dataclass(frozen=True)
class Event:
    id: str
    ts: str
    role: str
    instance: str
    name: str
    cmd: str
    cls: str
    scope: str
    exit: int
    duration_ms: int
    postcondition: str
    output_sha256: str
    output_tail: str
    commit: str
    runbook_sha256: str

# crafts/syseng/rules/invariants.md: the runner's facts, checked by the runner's pass and by run() before it runs
# a command or writes an event.
INVARIANTS = [
    ("fields-match-command-header", lambda: tuple("class" if f.name == "cls" else f.name for f in fields(Command)[:len(FIELDS)]) == FIELDS),
    ("event-fields-match-dataclass", lambda: tuple("class" if f.name == "cls" else f.name for f in fields(Event)) == EVENT_FIELDS),
    ("classes-are-host-classes", lambda: CLASSES is dyadlib.HOST_CLASSES),
    ("roles-distinct", lambda: len(set(ROLES)) == len(ROLES) and len(set(RUN_ROLES)) == len(RUN_ROLES)),
    ("postcondition-results-distinct", lambda: len(set(POSTCONDITION_RESULTS)) == len(POSTCONDITION_RESULTS)),
]

class Refused(Exception):
    """The runner did not run the command; `code` is the process exit code (2: role, tty, declined)."""
    def __init__(self, msg: str, code: int = 2):
        super().__init__(msg); self.code = code

# ---- paths
def runbooks_rel() -> str:
    return os.environ.get("DYAD_RUNBOOKS", DEFAULT_RUNBOOKS).rstrip("/")   # absolute allowed (tests)

def runbooks_dir(root: Path | None = None) -> Path:
    return (root or dyadlib.repo_root()) / runbooks_rel()

def runbook_path(root: Path, instance: str) -> Path:
    """`<runbooks>/<instance>.md`; when absent and a core run-book of that name exists, `dyad/runbooks/<instance>.md`
    (events still go to the instance's `<runbooks>/events/<instance>.jsonl`, #165)."""
    p = runbooks_dir(root) / f"{instance}.md"
    core = Path(root) / CORE_RUNBOOKS / f"{instance}.md"
    return core if not p.exists() and core.exists() else p

def runbooks(root: Path | None = None) -> dict[str, Path]:
    """{instance: run-book path} for every `<runbooks>/*.md` (README excluded)."""
    d = runbooks_dir(root)
    return {p.stem: p for p in sorted(d.glob("*.md")) if p.stem.lower() != "readme"} if d.is_dir() else {}

def core_runbooks(root: Path | None = None) -> dict[str, Path]:
    """{instance: path} for the core craft's run-books, `dyad/runbooks/*.md` (package, agent zone; README excluded)."""
    d = (root or dyadlib.repo_root()) / CORE_RUNBOOKS
    return {p.stem: p for p in sorted(d.glob("*.md")) if p.stem.lower() != "readme"} if d.is_dir() else {}

def all_runbooks(root: Path | None = None) -> dict[str, Path]:
    """Core run-books, then the instance's; an instance run-book of the same name wins (never expected)."""
    return {**core_runbooks(root), **runbooks(root)}

def events_dir(root: Path | None = None) -> Path:
    return runbooks_dir(root) / "events"

def events_path(root: Path, instance: str) -> Path:
    return events_dir(root) / f"{instance}.jsonl"

# ---- parser
def parse_text(text: str) -> list[Command]:
    """The dyad-cmd blocks of a run-book, in order. Header keys outside FIELDS are ignored; a missing
    key is "" (the guard reports it). A block with no blank line has an empty command."""
    out, section, lines, i = [], "", text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            section = line[3:].strip()
        m = _FENCE.match(line)
        if m and m.group(1) == FENCE:
            start, i = i + 1, i + 1
            hdr: dict[str, str] = {}
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("```"):
                k, sep, v = lines[i].partition(":")
                if sep and k.strip() in FIELDS:
                    hdr[k.strip()] = v.strip()
                i += 1
            if i < len(lines) and not lines[i].strip():
                i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i]); i += 1
            out.append(Command(hdr.get("name", ""), hdr.get("class", ""), hdr.get("role", ""), hdr.get("undo", ""),
                               hdr.get("postcondition", ""), hdr.get("scope", ""), "\n".join(body).strip(), section, start))
        elif m:
            i += 1                                   # another fence: skip its body verbatim
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
        i += 1
    return out

def parse(path: Path) -> list[Command]:
    return parse_text(path.read_text())

def prose_blocks(text: str) -> list[tuple[int, str]]:
    """(line, tag) of every fenced block that is a shell block or untagged — commands that are prose."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        m = _FENCE.match(lines[i])
        if m:
            if m.group(1) in PROSE_FENCES:
                out.append((i + 1, m.group(1) or "untagged"))
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
        i += 1
    return out

def sections(text: str) -> list[str]:
    return [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]

def declared_sections(text: str) -> list[str] | None:
    """The run-book's own section set from a header line `# sections: A, B, C` (or `sections: …`) before the first
    `## ` heading; None when it declares none (the guard then applies the craft rule's default set)."""
    for line in text.splitlines():
        if line.startswith("## "):
            break
        t = line.lstrip("#").strip()
        if t.lower().startswith(SECTIONS_KEY):
            return [s.strip() for s in t[len(SECTIONS_KEY):].split(",") if s.strip()]
    return None

def in_section(heading: str, section: str) -> bool:
    """`## Status/health (…)` belongs to `Status/health`; the match is the heading's first words."""
    return heading == section or heading.startswith(section + " ") or heading.startswith(section + " (")

def needs_operator(cmd: str) -> str | None:
    """The credential word that makes a command Operator-run, or None."""
    m = _CRED.search(cmd)
    return m.group(1).lower() if m else None

def counts(root: Path | None = None) -> tuple[int, int]:
    """(run-books, commands) under `root`."""
    rb = all_runbooks(root)
    return len(rb), sum(len(parse(p)) for p in rb.values())

# ---- events: reading
def read_events(path: Path) -> list[dict]:
    """The events of one `<instance>.jsonl`, in file order; a malformed line raises ValueError."""
    if not path.exists():
        return []
    out = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{i}: not a JSON object ({e.msg})") from None
    return out

def all_events(root: Path | None = None) -> dict[str, list[dict]]:
    """{instance: events} for every `<runbooks>/events/*.jsonl`."""
    d = events_dir(root)
    return {p.stem: read_events(p) for p in sorted(d.glob("*.jsonl"))} if d.is_dir() else {}

def event_line(e: Event) -> str:
    d = asdict(e); d["class"] = d.pop("cls")
    return json.dumps({k: d[k] for k in EVENT_FIELDS}, ensure_ascii=False) + "\n"

def tail(output: str, lines: int = TAIL_LINES, chars: int = TAIL_CHARS) -> str:
    t = "\n".join(output.rstrip("\n").splitlines()[-lines:])
    return t if len(t) <= chars else "…" + t[-(chars - 1):]

# ---- runner
def _git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"

def _bash(cmd: str, cwd: Path) -> tuple[int, str]:
    r = subprocess.run(["bash", "-o", "pipefail", "-c", cmd], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    return r.returncode, r.stdout

def _test(postcondition: str, cwd: Path) -> bool:
    return postcondition != NONE and _bash(postcondition, cwd)[0] == 0

def confirm(c: Command, out=sys.stdout) -> None:
    """Rule-18 property 7 form: print the step, its consequence and undo; read `Y` from /dev/tty; else Refused(2)."""
    print(f"destructive: {c.name}\n  command: {c.cmd}\n  scope: {c.scope}\n  undo: {c.undo}", file=out)
    if not sys.stdin.isatty() or not os.path.exists("/dev/tty"):
        print("no tty", file=out); raise Refused("no tty: a destructive command needs a terminal to confirm")
    try:
        with open("/dev/tty", "r+") as tty:
            tty.write(f"run {c.name}? Y/N: "); tty.flush(); ans = tty.readline().strip()
    except OSError:
        print("no tty", file=out); raise Refused("no tty: a destructive command needs a terminal to confirm")
    if ans != "Y":
        print("declined", file=out); raise Refused("declined")

def run(root: Path, instance: str, name: str, role: str, confirm_tty: bool = True, out=sys.stdout) -> Event:
    """Execute one run-book command as `role` and append its event. Raises Refused (nothing ran, no
    event) on an unknown run-book or command, a role mismatch, a missing tty or a declined confirm."""
    dyadlib.check_invariants(dyadlib, label="dyadlib"); dyadlib.check_invariants(INVARIANTS, label="runbook")   # a broken table must not write an event
    if role not in RUN_ROLES:
        raise Refused(f"role `{role}` is not one of {', '.join(RUN_ROLES)}")
    path = runbook_path(root, instance)
    if not path.exists():
        raise Refused(f"no run-book {path.relative_to(root) if path.is_relative_to(root) else path}")
    data = path.read_bytes()
    sha, commit = hashlib.sha256(data).hexdigest(), _git_commit(root)
    cmds = {c.name: c for c in parse_text(data.decode())}
    if name not in cmds:
        raise Refused(f"no command `{name}` in {path.name}; commands: {' '.join(sorted(cmds)) or 'none'}")
    c = cmds[name]
    print(f"commit: {commit}\n{sha}  {path.relative_to(root) if path.is_relative_to(root) else path}", file=out)
    if c.role == "operator" and role != "operator":
        raise Refused(f"{name} is role `operator` (Rule-8, Operator-run); refused for role `{role}`")
    print(f"{c.cls} {name} [{c.scope}]\n$ {c.cmd}", file=out)
    started = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    ts = started.strftime("%Y-%m-%dT%H:%M:%SZ")
    eid = f"{instance}-{started.strftime('%Y%m%dT%H%M%SZ')}-{name}"
    t0 = time.monotonic()
    if c.cls != "read-only" and _test(c.postcondition, root):
        print("already satisfied", file=out)
        ev = Event(eid, ts, role, instance, name, c.cmd, c.cls, c.scope, 0, int((time.monotonic() - t0) * 1000), "already",
                   hashlib.sha256(b"").hexdigest(), "", commit, sha)
    else:
        if c.cls == "destructive" and confirm_tty:
            confirm(c, out)
        t0 = time.monotonic()
        rc, output = _bash(c.cmd, root)
        ms = int((time.monotonic() - t0) * 1000)
        if output:
            print(output.rstrip("\n"), file=out)
        post = "n/a" if c.postcondition == NONE else ("ok" if _test(c.postcondition, root) else "failed")
        print(f"exit {rc}; postcondition {post}; {ms} ms", file=out)
        ev = Event(eid, ts, role, instance, name, c.cmd, c.cls, c.scope, rc, ms, post,
                   hashlib.sha256(output.encode()).hexdigest(), tail(output), commit, sha)
    ep = events_path(root, instance); ep.parent.mkdir(parents=True, exist_ok=True)
    with open(ep, "a") as f:
        f.write(event_line(ev))
    print(f"event {ev.id} -> {ep.relative_to(root) if ep.is_relative_to(root) else ep}", file=out)
    return ev

def exit_code(ev: Event) -> int:
    """Rule-18 property 7f: 0 done or already satisfied; 1 failed postcondition; else the command's exit."""
    if ev.exit:
        return ev.exit
    return 1 if ev.postcondition == "failed" else 0

def list_commands(root: Path, instance: str) -> list[Command]:
    path = runbook_path(root, instance)
    if not path.exists():
        raise Refused(f"no run-book {path}")
    return parse(path)

# ---- `new`: seed a run-book from a craft's template (the template is craft data, outside <runbooks>)
def template(pkg: Path = dyadlib.PKG) -> Path | None:
    """The first `crafts/*/templates/runbook.md` (sorted), or None when no craft ships one."""
    found = dyadlib.craft_glob("templates/runbook.md", pkg)
    return found[0] if found else None

def new(root: Path, instance: str, pkg: Path = dyadlib.PKG) -> Path:
    """Copy the craft template to `<runbooks>/<instance>.md`; Refused when it exists (never overwrite,
    exit 2) or when no craft provides a template (exit 2). Idempotent in the sense of refusing a second run."""
    t = template(pkg)
    if t is None:
        raise Refused("no craft provides a run-book template (crafts/*/templates/runbook.md)")
    dst = runbook_path(root, instance)
    if dst.exists():
        raise Refused(f"{dst.relative_to(root) if dst.is_relative_to(root) else dst} exists; not overwritten")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(t, dst)
    return dst

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = dyadlib.repo_root()
    if a and a[0] == "check":
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None:
            print("refused: no craft provides the run-book check (crafts/*/guards/runbooks.py)", file=sys.stderr); return 2
        return guard.main([str(root)])
    try:
        if a and a[0] == "list" and len(a) == 2:
            for c in list_commands(root, a[1]):
                print(f"{c.name:<26} {c.cls:<11} {c.role:<9} {c.section}")
            return 0
        if a and a[0] == "run" and len(a) >= 3:
            role = a[a.index("--as") + 1] if "--as" in a else os.environ.get("DYAD_ROLE", "agent")
            return exit_code(run(root, a[1], a[2], role))
        if a and a[0] == "new" and len(a) == 2:
            dst = new(root, a[1])
            print(f"seeded {dst.relative_to(root) if dst.is_relative_to(root) else dst} from {template().relative_to(root) if template().is_relative_to(root) else template()}; replace every <…> placeholder, then `runbook check`")
            return 0
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr); return e.code
    except dyadlib.InvariantError as e:
        print(f"refused: {e}", file=sys.stderr); return 2
    sys.exit(__doc__)

if __name__ == "__main__":
    sys.exit(main())
