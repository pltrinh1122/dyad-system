#!/usr/bin/env python3
"""The operator's attention ledger, the aggregate desk (core script; d-work #700). Kernel: Python 3.12+, git.

One read-only view over every desk the operator attends at once — the home and every paired unit, in every dyad system,
on every host and account that syncs to one central repository the operator owns. It is a view and never a unit: no
presence file, no row, no question, and the home stays the one home.

Where the central repository is named: per checkout, never in a tracked file (its name may be private, and this store
may be public), by git config:
  dyad.attention.clone     the path of a local clone of the central repository (absent: every verb says so, and the
                           closing line is today's)
  dyad.attention.system    this system's name there (default: `origin`'s owner/repo)
  dyad.attention.checkout  repeated, `<system> <path>`: a local checkout of another system, to resolve its entries

The central store holds references, never copies (the operator's constraint, provenance #700 entry 4): one file per
event, `attention/<system>/<unit>/<stamp>-<n>.md` (`/` in a system name stored as `--`), append-only, its `key: value`
lines `kind` (asked, answered, in-flight, landed; paired, unpaired; registered), `system`, `unit`, `row` (the bare
id, or a cross-row file's stem `_cos[-<operator>]`: the slug is the row file's own field, resolved when printed and
never stored), `ref` (`<path>@<commit>`, the record at the event), `what` (the question's kind by
dmc:disposition-request, `pr <n> at <head>`, `paired-units` or `declared`, or `checkout`), `writer`. No question text,
evidence or disposition is written; every `Y` stays in its own system's ledger. The open set is each (system, row,
what) whose last event is `asked` or `in-flight`; the desks are each (system, unit) whose last pairing event is
`paired` (#703). A pairing is a reference, never authority: a system's `paired-units` preference stands wherever it
exists, the ledger only reflects it, and routing never reads the ledger.

Sync replays history (#703): from this system's watermark (the newest commit any of its entries references, or the
commit its `registered` entry names on the first run) it walks every commit since that touches the board, the rows or
the preferences, derives the open set and the desks at each, and appends what changed, stamped with that commit's
time, so a question asked and answered between two syncs is still an `asked` and an `answered`. Each checkout that
names a clone registers once (`registered`, ref'd at its presence file).

  dyad attention [--full]   the aggregate desk, folded to at most FOLD lines (the full form on request): a header
                            with the fetch's age and the counts by system, then the oldest open items, each resolved
                            from the reader's checkout of its system or printed as its reference, `(unresolved)`
  dyad attention sync [--since <commit>]
                            replay this system's events from its watermark and append what the central store lacks:
                            one inline try of pull and push (an outage delays an entry, never loses one: the board
                            stays the source and the next sync derives it again); `0 entries` when nothing is new;
                            `--since` names the commit a first registration starts from
  dyad attention pair <system>/<unit> --ref <path>@<commit> [--drop]
                            record a pairing no one system's preference can hold (`declared`), or drop it: refused
                            unless the ref resolves in a checkout the reader holds, and refused for a system whose
                            checkout keeps a `paired-units` row (its preference is the authority)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("attention.py: Python 3.12+ required")
import datetime, os, re, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

USAGE = ("usage: dyad attention [--full] | dyad attention sync [--since <commit>] | "
         "dyad attention pair <system>/<unit> --ref <path>@<commit> [--drop]")
KINDS = ("asked", "answered", "in-flight", "landed", "paired", "unpaired", "registered")
OPENS = {"asked": "answered", "in-flight": "landed"}     # an opening kind and the kind that closes it: the open set
PAIRS = {"paired": "unpaired"}                            # #703: the desks, apart from the open set
CLOSERS = {**OPENS, **PAIRS}
UNIT_KEYED = ("paired", "unpaired", "registered")        # kinds keyed by unit, since they name no row
PREF = "paired-units"
FOLD = 7                                                  # the aggregate desk's bound, header and tail included
STORE = "attention"
FIELDS = ("kind", "system", "unit", "row", "ref", "what", "writer")
PR_LINE = re.compile(r"^\s*pr:\s*(\d+)\s+at\s+([0-9a-f]{7,40})\s*$", re.M)
NONE_NAMED = "attention: no central repository named in this checkout (git config dyad.attention.clone <path>)"
SYNCED = "dyad.attention.synced"                        # #703: the commit this checkout last replayed through
DRIFT_MAX = FOLD - 4                                      # drift lines before the overflow line


def git(args: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=dyadlib.git_env(),
                          timeout=timeout)


def config(repo: Path) -> dict:
    """{clone, system, checkouts}: this checkout's naming of the central repository, from git config alone."""
    def get(key: str, all_: bool = False) -> list[str]:
        r = git(["config", "--get-all" if all_ else "--get", key], repo)
        return [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []
    clone = get("dyad.attention.clone")
    system = get("dyad.attention.system")
    if not system:
        url = get("remote.origin.url")
        m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", url[0]) if url else None
        system = [m.group(1) if m else repo.name]
    checkouts = {}
    for line in get("dyad.attention.checkout", all_=True):
        name, _, path = line.partition(" ")
        if name and path.strip():
            checkouts[name] = Path(path.strip())
    checkouts[system[0]] = repo
    return {"clone": Path(clone[0]) if clone else None, "system": system[0], "checkouts": checkouts}


def parse(text: str) -> dict[str, str]:
    return {k: v.strip() for k, _, v in (l.partition(":") for l in text.splitlines()) if k in FIELDS}


def entries(clone: Path) -> list[tuple[str, dict[str, str]]]:
    """[(name, fields)] of every event file under the store, in name order (the stamp leads the name, so time order
    within a unit; across units the stamp still orders them)."""
    base = clone / STORE
    if not base.is_dir():
        return []
    files = sorted(base.glob("*/*/*.md"), key=lambda p: (p.name, str(p)))
    return [(str(p.relative_to(clone)), parse(p.read_text(errors="ignore"))) for p in files]


def key(f: dict[str, str]) -> tuple[str, str, str]:
    if f.get("kind") in UNIT_KEYED:
        return (f.get("system", ""), "@" + f.get("unit", ""), f.get("kind") == "registered" and "checkout" or "pair")
    return (f.get("system", ""), f.get("row", ""), f.get("what", ""))


def open_set(got: list[tuple[str, dict[str, str]]], opens: dict = OPENS) -> list[tuple[str, dict[str, str]]]:
    """Each key whose last event opens it (by default `asked`, `in-flight`), with the name of its opening file."""
    last: dict[tuple, tuple[str, dict[str, str]]] = {}
    for name, f in got:
        if f.get("kind") in KINDS:
            last[key(f)] = (name, f)
    return [(n, f) for n, f in last.values() if f.get("kind") in opens]


def desks(got: list[tuple[str, dict[str, str]]]) -> list[tuple[str, dict[str, str]]]:
    """#703: each (system, unit) whose last pairing event is `paired`."""
    return open_set(got, PAIRS)


def show(repo: Path, commit: str, path: str) -> str | None:
    r = git(["show", f"{commit}:{path}"], repo)
    return r.stdout if r.returncode == 0 else None


def question_kind(board, f: dict[str, str]) -> str | None:
    """The disposition request an entry records, as `board.asked_kind`, except that a held entry is classed by its
    question's form as an unphased one is (#703: a question asked by hand on a held entry is recorded too)."""
    if board.phase_name(f) == "held":
        kind = board.disposition_request(None, f.get("question"))
        return None if kind == board.REQUEST_NONE else kind
    return board.asked_kind(f)


def paired_names(text: str | None) -> list[str]:
    """The unit names of a preferences file's `paired-units` row (`none` or absent: none)."""
    for r in dyadlib.table_rows(text or ""):
        if len(r) >= 2 and dyadlib.plain(r[0]).strip() == PREF:
            v = dyadlib.plain(r[1]).strip()
            return [] if v in ("", "none") else [u.strip() for u in v.split(",") if u.strip()]
    return []


def derive_at(repo: Path, system: str, commit: str, landed: list[str]) -> dict[tuple[str, str, str], dict[str, str]]:
    """This system's open events and desks at `commit`, read by `git show`: each recorded question asked and not
    answered on a live row's entry, on a held entry or on a cross-row file (`asked`, `what` its kind by
    dmc:disposition-request, `unit` the entry's holder); each `pr: <n> at <sha>` whose head is not an ancestor of every
    ref in `landed` (`in-flight`, `unit` the entry's unit or owner); and each unit the `paired-units` preference names
    (`paired`, `what: paired-units`)."""
    board = dyadlib.load_guard("agent", "board")
    inst = dyadlib.instance(repo).relative_to(repo).as_posix()
    bdir, rdir = f"{inst}/d-work/board", f"{inst}/d-work/rows"
    ls = git(["ls-tree", "--name-only", f"{commit}:{bdir}"], repo)
    out: dict = {}
    for name in (ls.stdout.split() if ls.returncode == 0 else []):
        n = name.removesuffix(".md")
        if not name.endswith(".md") or not (n.isdigit() or board.is_cos(n)):
            continue
        if n.isdigit():
            row = show(repo, commit, f"{rdir}/{n}.md") or ""
            st = re.search(r"^state:\s*(\S+)", row, re.M)
            if not st or st.group(1) in dyadlib.TERMINAL_STATES:
                continue
        text = show(repo, commit, f"{bdir}/{name}") or ""
        f = board.parse(text)[0]
        ref = f"{bdir}/{name}@{commit}"
        if (kind := question_kind(board, f)):
            ev = {"kind": "asked", "system": system, "unit": (f.get("holder") or "-").strip() or "-", "row": n,
                  "ref": ref, "what": kind}
            out[key(ev)] = ev
        if not n.isdigit():
            continue
        unit = (re.search(r"^\s*unit:\s*(\S+)", text, re.M) or re.search(r"^owner:\s*([^\s;]+)", text, re.M))
        for pr, sha in PR_LINE.findall(text):
            if all(git(["merge-base", "--is-ancestor", sha, l], repo).returncode == 0 for l in landed):
                continue
            ev = {"kind": "in-flight", "system": system, "unit": unit.group(1) if unit else "-", "row": n, "ref": ref,
                  "what": f"pr {pr} at {sha[:12]}"}
            out[key(ev)] = ev
    for u in paired_names(show(repo, commit, dyadlib.PREFERENCES_REL)):
        ev = {"kind": "paired", "system": system, "unit": u, "row": "-", "ref": f"{dyadlib.PREFERENCES_REL}@{commit}",
              "what": PREF}
        out[key(ev)] = ev
    return out


def derive(repo: Path, system: str) -> dict[tuple[str, str, str], dict[str, str]]:
    """This system's open events and desks now: `derive_at` HEAD, a PR landed when its head is on `origin/main`."""
    head = git(["rev-parse", "HEAD"], repo).stdout.strip()
    return derive_at(repo, system, head, ["origin/main"])


def safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", name.replace("/", "--")) or "-"


def plan_sync(clone_open: list[tuple[str, dict[str, str]]], now_open: dict, system: str, writer: str,
              stamp: str, at: str | None = None) -> list[tuple[str, dict[str, str]]]:
    """The events to append: an opening event for each key open now and not open in the store, and the closing event
    for each of this system's keys open in the store and no longer open now, ref'd at the commit `at` it closed at when
    given (#703: so the watermark passes it). Pure; names are relative to the clone."""
    had = {key(f): f for _, f in clone_open if f.get("system") == system and f.get("what") != "declared"}
    new = [dict(f) for k, f in sorted(now_open.items()) if k not in had]
    new += [{**f, "kind": CLOSERS[f["kind"]], **({"ref": f"{f['ref'].partition('@')[0]}@{at}"} if at else {})}
            for k, f in sorted(had.items()) if k not in now_open]
    out, seq = [], {}
    for f in new:
        f["writer"] = writer
        u = safe(f.get("unit", "-"))
        seq[u] = seq.get(u, 0) + 1
        out.append((f"{STORE}/{safe(system)}/{u}/{stamp}-{seq[u]}.md", f))
    return out


def render(f: dict[str, str]) -> str:
    return "".join(f"{k}: {f.get(k, '')}\n" for k in FIELDS)


def presence_rel(repo: Path, unit: str) -> str:
    return f"{dyadlib.instance(repo).relative_to(repo).as_posix()}/d-work/sessions/{unit}.md"


def watermark(repo: Path, mine: list[dict[str, str]]) -> str | None:
    """The newest commit on HEAD's line that any of this system's entries references, or that this checkout last
    synced through (`git config dyad.attention.synced`, per checkout and never tracked: a quiet stretch is then not
    walked again), or None."""
    refs = {f.get("ref", "").partition("@")[2] for f in mine} - {""}
    cached = git(["config", "--get", SYNCED], repo)
    if cached.returncode == 0 and cached.stdout.strip():
        refs.add(cached.stdout.strip())
    if not refs:
        return None
    full = {git(["rev-parse", "--verify", "-q", r + "^{commit}"], repo).stdout.strip() for r in refs} - {""}
    log = git(["rev-list", "HEAD"], repo)
    return next((c for c in log.stdout.split() if c in full), None)


def replay(repo: Path, system: str, got: list[tuple[str, dict[str, str]]], writer: str, since: str,
           now_stamp: str) -> list[tuple[str, dict[str, str]]]:
    """#703: the events that take the store from what it believed at `since` through every later commit touching the
    board, the rows or the preferences, then to the present (a PR landed by `origin/main`). Each historical event is
    stamped with its commit's UTC time; the present step with `now_stamp`. Pure of writes."""
    inst = dyadlib.instance(repo).relative_to(repo).as_posix()
    after = set(git(["rev-list", f"{since}..HEAD"], repo).stdout.split())
    mine = [(n, f) for n, f in got if f.get("system") == system]
    believed = [(n, f) for n, f in mine if f.get("ref", "").partition("@")[2] not in after]
    log = git(["log", "--reverse", "--format=%H %ct", f"{since}..HEAD", "--",
               f"{inst}/d-work/board", f"{inst}/d-work/rows", dyadlib.PREFERENCES_REL], repo)
    todo: list[tuple[str, dict[str, str]]] = []
    for line in log.stdout.splitlines():
        c, t = line.split()
        stamp = datetime.datetime.fromtimestamp(int(t), datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        step = plan_sync(open_set(believed, CLOSERS), derive_at(repo, system, c, [c, "origin/main"]), system, writer,
                         stamp, at=c)
        todo += step; believed += step
    head = git(["rev-parse", "HEAD"], repo).stdout.strip()
    step = plan_sync(open_set(mine + todo, CLOSERS), derive(repo, system), system, writer, now_stamp, at=head)
    return todo + step


def sync(repo: Path, out=print, since: str | None = None) -> int:
    """Append this system's new events to the central store: one try of pull, one of push. A failed push keeps the
    commit in the clone for the next sync; it never fails the caller (the board's own write already landed). A checkout
    that names a clone and holds no `registered` entry registers first, at `since` when given (else HEAD), and the
    replay starts there (#703)."""
    c = config(repo)
    if c["clone"] is None:
        out(NONE_NAMED)
        return 0
    clone = c["clone"]
    if not (clone / ".git").exists():
        out(f"attention: the clone named in this checkout is not a git checkout; nothing synced")
        return 0
    git(["pull", "-q", "--rebase"], clone, timeout=120)                 # one try; an outage leaves the clone as it is
    now = datetime.datetime.now(datetime.UTC)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    unit, writer = os.environ.get("DYAD_SESSION", "-"), os.environ.get("DYAD_SESSION", "-")
    got = entries(clone)
    mine = [f for _, f in got if f.get("system") == c["system"]]
    todo: list[tuple[str, dict[str, str]]] = []
    start = None
    if not any(f.get("kind") == "registered" and f.get("unit") == unit for f in mine):
        at = git(["rev-parse", "--verify", "-q", (since or "HEAD") + "^{commit}"], repo).stdout.strip()
        if not at:
            out(f"attention: --since {since} names no commit here; nothing synced")
            return 0
        reg = {"kind": "registered", "system": c["system"], "unit": unit, "row": "-",
               "ref": f"{presence_rel(repo, unit)}@{at}", "what": "checkout", "writer": writer}
        when = datetime.datetime.fromtimestamp(int(git(["show", "-s", "--format=%ct", at], repo).stdout.strip()),
                                               datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        todo.append((f"{STORE}/{safe(c['system'])}/{safe(unit)}/{when}-1.md", reg))
        start = at
    start = start or watermark(repo, mine) or git(["rev-parse", "HEAD"], repo).stdout.strip()
    t0 = now.timestamp()
    todo += replay(repo, c["system"], got, writer, start, stamp)
    secs = datetime.datetime.now(datetime.UTC).timestamp() - t0
    for name, f in todo:
        p = clone / name
        while p.exists():                                            # two syncs in one second: never overwrite
            stem, _, n = p.stem.rpartition("-")
            p = p.with_name(f"{stem}-{int(n) + 1}.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render(f))
    if todo:
        git(["add", STORE], clone)
        git(["commit", "-q", "-m", f"attention: {c['system']} {len(todo)} entr{'y' if len(todo) == 1 else 'ies'}"],
            clone)
    git(["config", SYNCED, git(["rev-parse", "HEAD"], repo).stdout.strip()], repo)   # committed in the clone: replayed
    pending = git(["rev-list", "--count", "@{u}..HEAD"], clone)
    ahead = int(pending.stdout.strip() or 0) if pending.returncode == 0 else (1 if todo else 0)
    tail = f" (replayed in {secs:.0f}s)" if secs >= 5 else ""
    if ahead and git(["push", "-q"], clone, timeout=120).returncode != 0:
        out(f"attention: {len(todo)} entries committed, the push failed; the next sync pushes them{tail}")
        return 0
    out(f"attention: {len(todo)} entries{tail}")
    return 0


def pair(repo: Path, target: str, ref: str, drop: bool = False, out=print, err=None) -> int:
    """#703: record (or drop) a pairing no one system's preference can hold, `what: declared`. Refused unless `ref`
    (`<path>@<commit>`) resolves in a checkout the reader holds, and refused for a system whose checkout keeps a
    `paired-units` row: its preference is the authority, so the pairing goes there."""
    err = err or (lambda m: print(m, file=sys.stderr))
    c = config(repo)
    if c["clone"] is None:
        out(NONE_NAMED)
        return 1
    system, _, unit = target.rpartition("/")
    path, _, commit = ref.partition("@")
    if not system or not unit or not path or not commit:
        err("refused: `attention pair <system>/<unit> --ref <path>@<commit>`")
        return 1
    co = c["checkouts"].get(system)
    if co is not None and any(dyadlib.plain(r[0]).strip() == PREF for r in dyadlib.table_rows(
            (co / dyadlib.PREFERENCES_REL).read_text() if (co / dyadlib.PREFERENCES_REL).is_file() else "") if r):
        err(f"refused: {system} keeps a `{PREF}` preference, which is the authority; pair {unit} there")
        return 1
    held = [c["checkouts"][system]] if system in c["checkouts"] else []
    held += [p for s, p in c["checkouts"].items() if s != system]
    if not any(show(p, commit, path) is not None for p in held):
        err(f"refused: --ref {ref} resolves in no checkout this reader holds")
        return 1
    clone = c["clone"]
    git(["pull", "-q", "--rebase"], clone, timeout=120)
    is_paired = any(f.get("system") == system and f.get("unit") == unit for _, f in desks(entries(clone)))
    if is_paired != drop:
        out(f"attention: {system}/{unit} is {'not ' if drop else ''}paired; 0 entries")
        return 0
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    f = {"kind": "unpaired" if drop else "paired", "system": system, "unit": unit, "row": "-", "ref": ref,
         "what": "declared", "writer": os.environ.get("DYAD_SESSION", "-")}
    p = clone / STORE / safe(system) / safe(unit) / f"{stamp}-1.md"
    while p.exists():
        stem, _, n = p.stem.rpartition("-")
        p = p.with_name(f"{stem}-{int(n) + 1}.md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(f))
    git(["add", STORE], clone)
    git(["commit", "-q", "-m", f"attention: {system} 1 entry"], clone)
    if git(["push", "-q"], clone, timeout=120).returncode != 0:
        out("attention: 1 entries committed, the push failed; the next sync pushes them")
        return 0
    out("attention: 1 entries")
    return 0


def resolve(f: dict[str, str], checkouts: dict[str, Path]) -> str | None:
    """The row's label with its slug and the question's last line, read from the reader's own checkout of the system at
    the referenced commit; None when the reader cannot read it (no checkout, or a commit it lacks)."""
    co = checkouts.get(f.get("system", ""))
    path, _, commit = f.get("ref", "").partition("@")
    if co is None or not path or not commit:
        return None
    shown = git(["show", f"{commit}:{path}"], co)
    if shown.returncode != 0:
        return None
    rid = f.get("row", "")
    label = f"#{rid}" if rid.isdigit() else rid
    rowf = git(["show", f"{commit}:{Path(path).parent.parent.as_posix()}/rows/{rid}.md"], co)
    if rowf.returncode == 0 and (m := re.search(r"^slug:\s*(\S+)", rowf.stdout, re.M)):
        label += f"-{m.group(1)}"
    q = next((l.strip() for l in reversed(shown.stdout.splitlines()) if l.strip().startswith("question:")), "")
    return f"{label} {q.split(':', 1)[1].strip()}" if q else label


def drift(got: list[tuple[str, dict[str, str]]], checkouts: dict[str, Path]) -> list[str]:
    """#703: one line per system whose `paired-units` preference, read from the reader's checkout of it, differs from
    the ledger's `paired-units` desks; a system the reader cannot read is not judged."""
    held: dict[str, set[str]] = {}
    for _, f in desks(got):
        if f.get("what") == PREF:
            held.setdefault(f.get("system", ""), set()).add(f.get("unit", ""))
    out = []
    for system in sorted(set(held) | set(checkouts)):
        p = checkouts.get(system)
        if p is None or not (p / dyadlib.PREFERENCES_REL).is_file():
            continue
        names = set(paired_names((p / dyadlib.PREFERENCES_REL).read_text(errors="ignore")))
        if names != held.get(system, set()):
            out.append(f"  drift: {system} {PREF} names {', '.join(sorted(names)) or 'none'}, the ledger holds "
                       f"{', '.join(sorted(held.get(system, set()))) or 'none'}; the preference stands "
                       f"(the next sync of {system} corrects it)")
    return out


def fold(items: list[tuple[str, dict[str, str]]], checkouts: dict[str, Path], age: str, full: bool = False,
         got: list[tuple[str, dict[str, str]]] | None = None) -> list[str]:
    """The aggregate desk's lines: a header (age, counts by system, desks, registered units), the drift lines (#703),
    then the items oldest first, each resolved or printed as its reference; at most FOLD lines unless `full`, which
    also lists the desks."""
    got = got or []
    items = sorted(items, key=lambda t: Path(t[0]).name)
    by: dict[str, int] = {}
    for _, f in items:
        by[f.get("system", "")] = by.get(f.get("system", ""), 0) + 1
    d = sorted(desks(got), key=lambda t: (t[1].get("system", ""), t[1].get("unit", "")))
    reg: dict[str, int] = {}
    for _, f in open_set(got, {"registered": None}):
        reg[f.get("system", "")] = reg.get(f.get("system", ""), 0) + 1
    head = f"attention: {len(items)} open, fetched {age}" + (
        " — " + ", ".join(f"{s} {n}" for s, n in sorted(by.items())) if by else "")
    if d:
        head += f"; desks {len(d)}"
    if reg:
        head += "; registered " + ", ".join(f"{s} {n}" for s, n in sorted(reg.items()))
    dl = drift(got, checkouts)
    if not full and len(dl) > DRIFT_MAX:
        dl = dl[:DRIFT_MAX - 1] + [f"  +{len(dl) - DRIFT_MAX + 1} systems drift (dyad attention --full)"]
    lines = []
    for _, f in items:
        r = resolve(f, checkouts)
        what = f.get("what", "")
        body = r if r else (f"#{f.get('row', '')}" if f.get("row", "").isdigit() else f.get("row", "")) + " (unresolved)"
        lines.append(f"  {f.get('system', '')} {f.get('unit', '')} {f.get('kind', '')} {what}: {body}")
    room = FOLD - 1 - len(dl)
    if not full and len(lines) > room:
        keep = room - 1
        lines = lines[:keep] + [f"  +{len(items) - keep} more (dyad attention --full)"]
    tail = [f"  desk {f.get('system', '')} {f.get('unit', '')} ({f.get('what', '')})" for _, f in d] if full else []
    return [head] + dl + lines + tail


def fetch_age(clone: Path) -> str:
    """How long ago the clone last fetched, from FETCH_HEAD's mtime, or `never`."""
    fh = clone / ".git" / "FETCH_HEAD"
    if not fh.exists():
        return "never"
    s = int(datetime.datetime.now().timestamp() - fh.stat().st_mtime)
    return f"{s // 3600}h{(s % 3600) // 60:02d}m ago" if s >= 3600 else f"{s // 60}m ago"


def foreign_open(repo: Path) -> list[dict[str, str]]:
    """For the closing line: the open entries of every other system (this system's own come from its board, so no
    question counts twice); [] when no clone is named or it holds nothing."""
    c = config(repo)
    if c["clone"] is None or not (c["clone"] / ".git").exists():
        return []
    return [f for _, f in open_set(entries(c["clone"])) if f.get("system") != c["system"]]


def main(argv: list[str], repo: Path | None = None) -> int:
    repo = repo or dyadlib.repo_root()
    if argv[:1] == ["sync"]:
        rest = argv[1:]
        if rest and (len(rest) != 2 or rest[0] != "--since"):
            print(USAGE, file=sys.stderr)
            return 1
        return sync(repo, since=rest[1] if rest else None)
    if argv[:1] == ["pair"]:
        rest, drop = [a for a in argv[1:] if a != "--drop"], "--drop" in argv[1:]
        if len(rest) != 3 or rest[1] != "--ref":
            print(USAGE, file=sys.stderr)
            return 1
        return pair(repo, rest[0], rest[2], drop)
    if argv not in ([], ["--full"]):
        print(USAGE, file=sys.stderr)
        return 1
    c = config(repo)
    if c["clone"] is None:
        print(NONE_NAMED)
        return 0
    git(["fetch", "-q"], c["clone"], timeout=120)                       # one try; the age line says how fresh it is
    git(["merge", "-q", "--ff-only", "@{u}"], c["clone"])
    got = entries(c["clone"])
    print("\n".join(fold(open_set(got), c["checkouts"], fetch_age(c["clone"]), full=argv == ["--full"], got=got)))
    return 0


INVARIANTS = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("every-opening-kind-has-its-closer", lambda: all(k in KINDS and v in KINDS for k, v in CLOSERS.items())),
    ("a-desk-is-never-in-the-open-set", lambda: not set(PAIRS) & set(OPENS)),
    ("a-pairing-is-keyed-by-its-unit", lambda: key({"kind": "paired", "system": "s", "unit": "a"})
        != key({"kind": "paired", "system": "s", "unit": "b"})),
    ("the-fold-bound-is-seven", lambda: FOLD == 7),
    ("an-entry-holds-no-text-field", lambda: not {"question", "body", "title", "slug"} & set(FIELDS)),
    ("sync-opens-then-closes", lambda: [f["kind"] for _, f in plan_sync(
        [("x", {"kind": "asked", "system": "s", "row": "1", "what": "plan", "unit": "u"})],
        {("s", "2", "done"): {"kind": "asked", "system": "s", "row": "2", "what": "done", "unit": "u"}},
        "s", "w", "T")] == ["asked", "answered"]),
]
dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
