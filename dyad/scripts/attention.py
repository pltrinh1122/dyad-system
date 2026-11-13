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
lines `kind` (asked, answered, in-flight, landed), `system`, `unit`, `row` (the bare id: the slug is the row file's own
field, resolved when printed and never stored), `ref` (`<path>@<commit>`, the board entry at the event), `what` (the
question's kind by dmc:disposition-request, or `pr <n> at <head>`), `writer`. No question text, evidence or disposition
is written; every `Y` stays in its own system's ledger. The open set is each (system, row, what) whose last event is
`asked` or `in-flight`.

  dyad attention [--full]   the aggregate desk, folded to at most FOLD lines (the full form on request): a header
                            with the fetch's age and the counts by system, then the oldest open items, each resolved
                            from the reader's checkout of its system or printed as its reference, `(unresolved)`
  dyad attention sync       derive this system's events from its board store and append what the central store
                            lacks: one inline try of pull and push (an outage delays an entry, never loses one: the
                            board stays the source and the next sync derives it again); `0 entries` when nothing is new
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("attention.py: Python 3.12+ required")
import datetime, os, re, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

USAGE = "usage: dyad attention [--full] | dyad attention sync"
KINDS = ("asked", "answered", "in-flight", "landed")
OPENS = {"asked": "answered", "in-flight": "landed"}     # an opening kind and the kind that closes it
FOLD = 7                                                  # the aggregate desk's bound, header and tail included
STORE = "attention"
FIELDS = ("kind", "system", "unit", "row", "ref", "what", "writer")
PR_LINE = re.compile(r"^\s*pr:\s*(\d+)\s+at\s+([0-9a-f]{7,40})\s*$", re.M)
NONE_NAMED = "attention: no central repository named in this checkout (git config dyad.attention.clone <path>)"


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
    return (f.get("system", ""), f.get("row", ""), f.get("what", ""))


def open_set(got: list[tuple[str, dict[str, str]]]) -> list[tuple[str, dict[str, str]]]:
    """Each (system, row, what) whose last event opens it (`asked`, `in-flight`), with the name of its opening file."""
    last: dict[tuple, tuple[str, dict[str, str]]] = {}
    for name, f in got:
        if f.get("kind") in KINDS:
            last[key(f)] = (name, f)
    return [(n, f) for n, f in last.values() if f.get("kind") in OPENS]


def derive(repo: Path, system: str) -> dict[tuple[str, str, str], dict[str, str]]:
    """This system's open events now, from its board store as the checkout holds it: each recorded question asked and
    not answered (`asked`, `what` its kind by dmc:disposition-request, `unit` the entry's holder) and each `pr: <n> at
    <sha>` whose head is not on `origin/main` (`in-flight`, `unit` the entry's unit or owner)."""
    board = dyadlib.load_guard("agent", "board")
    inst = dyadlib.instance(repo)
    head = git(["rev-parse", "HEAD"], repo).stdout.strip()
    live = {r.id for r in dyadlib.read_rows(repo) if r.state not in dyadlib.TERMINAL_STATES}
    out = {}
    for n, f in board.load(repo):
        if not n.isdigit() or int(n) not in live:
            continue
        ref = f"{(inst / 'd-work' / 'board' / (n + '.md')).relative_to(repo).as_posix()}@{head}"
        if (kind := board.asked_kind(f)):
            ev = {"kind": "asked", "system": system, "unit": (f.get("holder") or "-").strip() or "-", "row": n,
                  "ref": ref, "what": kind}
            out[key(ev)] = ev
        text = (repo / ref.split("@")[0]).read_text(errors="ignore")
        unit = (re.search(r"^\s*unit:\s*(\S+)", text, re.M) or re.search(r"^owner:\s*(\S+)", text, re.M))
        for pr, sha in PR_LINE.findall(text):
            if git(["merge-base", "--is-ancestor", sha, "origin/main"], repo).returncode == 0:
                continue
            ev = {"kind": "in-flight", "system": system, "unit": unit.group(1) if unit else "-", "row": n, "ref": ref,
                  "what": f"pr {pr} at {sha[:12]}"}
            out[key(ev)] = ev
    return out


def safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", name.replace("/", "--")) or "-"


def plan_sync(clone_open: list[tuple[str, dict[str, str]]], now_open: dict, system: str, writer: str,
              stamp: str) -> list[tuple[str, dict[str, str]]]:
    """The events to append: an opening event for each key open now and not open in the store, and the closing event
    for each of this system's keys open in the store and no longer open now. Pure; names are relative to the clone."""
    had = {key(f): f for _, f in clone_open if f.get("system") == system}
    new = [dict(f) for k, f in sorted(now_open.items()) if k not in had]
    new += [{**f, "kind": OPENS[f["kind"]]} for k, f in sorted(had.items()) if k not in now_open]
    out, seq = [], {}
    for f in new:
        f["writer"] = writer
        u = safe(f.get("unit", "-"))
        seq[u] = seq.get(u, 0) + 1
        out.append((f"{STORE}/{safe(system)}/{u}/{stamp}-{seq[u]}.md", f))
    return out


def render(f: dict[str, str]) -> str:
    return "".join(f"{k}: {f.get(k, '')}\n" for k in FIELDS)


def sync(repo: Path, out=print) -> int:
    """Append this system's new events to the central store: one try of pull, one of push. A failed push keeps the
    commit in the clone for the next sync; it never fails the caller (the board's own write already landed)."""
    c = config(repo)
    if c["clone"] is None:
        out(NONE_NAMED)
        return 0
    clone = c["clone"]
    if not (clone / ".git").exists():
        out(f"attention: the clone named in this checkout is not a git checkout; nothing synced")
        return 0
    git(["pull", "-q", "--rebase"], clone, timeout=120)                 # one try; an outage leaves the clone as it is
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    todo = plan_sync(open_set(entries(clone)), derive(repo, c["system"]), c["system"],
                     os.environ.get("DYAD_SESSION", "-"), stamp)
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
    pending = git(["rev-list", "--count", "@{u}..HEAD"], clone)
    ahead = int(pending.stdout.strip() or 0) if pending.returncode == 0 else (1 if todo else 0)
    if ahead and git(["push", "-q"], clone, timeout=120).returncode != 0:
        out(f"attention: {len(todo)} entries committed, the push failed; the next sync pushes them")
        return 0
    out(f"attention: {len(todo)} entries")
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
    label = f"#{rid}"
    rowf = git(["show", f"{commit}:{Path(path).parent.parent.as_posix()}/rows/{rid}.md"], co)
    if rowf.returncode == 0 and (m := re.search(r"^slug:\s*(\S+)", rowf.stdout, re.M)):
        label += f"-{m.group(1)}"
    q = next((l.strip() for l in reversed(shown.stdout.splitlines()) if l.strip().startswith("question:")), "")
    return f"{label} {q.split(':', 1)[1].strip()}" if q else label


def fold(items: list[tuple[str, dict[str, str]]], checkouts: dict[str, Path], age: str, full: bool = False) -> list[str]:
    """The aggregate desk's lines: a header (age, counts by system), then the items oldest first, each resolved or
    printed as its reference; at most FOLD lines unless `full`."""
    items = sorted(items, key=lambda t: Path(t[0]).name)
    by: dict[str, int] = {}
    for _, f in items:
        by[f.get("system", "")] = by.get(f.get("system", ""), 0) + 1
    head = f"attention: {len(items)} open, fetched {age}" + (
        " — " + ", ".join(f"{s} {n}" for s, n in sorted(by.items())) if by else "")
    lines = []
    for _, f in items:
        r = resolve(f, checkouts)
        what = f.get("what", "")
        body = r if r else f"#{f.get('row', '')} (unresolved)"
        lines.append(f"  {f.get('system', '')} {f.get('unit', '')} {f.get('kind', '')} {what}: {body}")
    if not full and len(lines) > FOLD - 1:
        keep = FOLD - 2
        lines = lines[:keep] + [f"  +{len(items) - keep} more (dyad attention --full)"]
    return [head] + lines


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
        return sync(repo)
    if argv not in ([], ["--full"]):
        print(USAGE, file=sys.stderr)
        return 1
    c = config(repo)
    if c["clone"] is None:
        print(NONE_NAMED)
        return 0
    git(["fetch", "-q"], c["clone"], timeout=120)                       # one try; the age line says how fresh it is
    git(["merge", "-q", "--ff-only", "@{u}"], c["clone"])
    print("\n".join(fold(open_set(entries(c["clone"])), c["checkouts"], fetch_age(c["clone"]), full=argv == ["--full"])))
    return 0


INVARIANTS = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("every-opening-kind-has-its-closer", lambda: all(k in KINDS and v in KINDS for k, v in OPENS.items())),
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
