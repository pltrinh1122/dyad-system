#!/usr/bin/env python3
"""`dyad dwork … --land` and `dyad dwork land` (d-work #447, child C1 of plan #443). Kernel: Python 3.12+, git.

One call per ledger record, in place of the series a seat ran by hand — fetch, reset, `dwork state`, commit, a
push to `main` through the pre-push hook, retries when `main` had moved, then a mirror push (plan #443 Evidence:
4–6 tool calls and about 2.1 hook runs per record):

  dyad dwork new|state … --land [--mirror <branch>]
                          run the verb in the tool-owned worktree, commit what it wrote, push it; with
                          `state … --check` run only the check there and land nothing (#464)
  dyad dwork land <path>... -m <msg> [--mirror <branch>]
                          copy the named files (plan files, presence, traces) from this checkout into that worktree,
                          commit and push them the same way
  dyad dwork batch <file>|- --land [--mirror <branch>]
                          several of those in one commit and one push (#459): one `dwork` argv per line,
                          shell-quoted — `new …`, `state …` or `land <path>…`; blank and `#` lines skipped

The worktree is `<git common dir>/dyad-land`: one per clone, shared by its linked worktrees, guarded by a lock file
beside it, created or reused detached at a freshly fetched `origin/main` and cleaned of every untracked and ignored
file before each use (`git clean -ffdx`), so a stale `__pycache__` can neither reach it nor survive in it
(#412–#414); every child runs with PYTHONDONTWRITEBYTECODE=1. The seat's own checkout is never reset: the verb runs
there through the worktree's own runner (`dyad/scripts/package.py`, what its `dyad/bin/dyad` execs), which resolves
its repo from its own location, so its row, provenance and plan writes land in the worktree (#427). Every path
written must lie under `<instance>/d-work/`, else nothing is committed — a commit outside it would not be
ledger-only (Rule-2, Rule-3 Ledger). The commit holds only the written paths, under a generated `ledger: …` subject
that cites no `d-work #` (a ledger-only commit claims no d-work, Rule-3 Ledger). One `git push origin HEAD:main
[HEAD:refs/heads/<branch>]`, `--atomic` when it names the mirror, carries both refs or neither, so the pre-push hook
runs once and judges both, guards unchanged (Rule-14 property 3).

A push refused while `origin/main` moved is rebuilt from the inputs, never rebased: the verb runs again on the
new `origin/main` (a `new` re-allocates its id). Before every run the entry is looked for on `origin/main` and
the call is refused as `already landed` when it is there — the disposition is already the row's last `disposed`
entry with the same words last in its record, the prompt already the record's last entry, the state already
reached, a `new` with the same title and words already a row, the files already identical — so a retry, or a
re-run after an ambiguous failure, never records twice (plan #443 attack 11; syseng `idempotence.md` p1). At
most TRIES tries. On success the landed sha is printed and, when this checkout is on a clean `main`, it is
fast-forwarded to it; otherwise only the sha is printed. After a `land` of paths, a checkout on `main` whose only
changes are landed paths, each byte-identical to its blob at the landed sha, has them restored from its HEAD and is
then fast-forwarded: the content restored is the content landed, so nothing is lost (#459, the #443 finding that a
landed copy left the checkout dirty forever); any other change, or one differing byte, leaves it as it is.

A batch (#459) parses every line first and refuses the whole batch before any fetch on a line that names `-m`,
`--land`, `--mirror` or a verb other than `new`, `state`, `land`, and on one row id that both records a
merge-naming `Y done` and is set `done` — the fence's `rows.done_order_problems`, said where it costs a line
instead of a push, so a ratified set travels as a record batch, the merges, then a close batch. It then runs as
one worktree pass: each line already on `origin/main` is skipped by name (`skipped (already landed): …`, the
per-line test above), a batch with no line left is refused, the rest run in order through the worktree's runner,
and a line it refuses stops the batch with nothing committed. One commit, `ledger: batch …`, one push; a moved
`main` rebuilds the whole batch from its lines. A later line cannot name an id a `new` line of the same batch
creates: that id is allocated in the worktree and is re-allocated on a rebuild. Lines run in order, a `land` line's
files copied into the worktree before the next line runs, so a `Y done` line under `dwork-trace: always` lands when an
earlier `land <instance>/d-work/traces/<id>.md` line carries its trace — the runner refuses it otherwise, and the single
`state … --land` form, which lands only what the verb writes, refuses it unless the trace is already on `origin/main`
(#465).
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("land.py: Python 3.12+ required")
import contextlib, datetime, os, shlex, shutil, subprocess
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

TRIES = 3                       # plan #443 attack 11: at most three tries, then stop and print the state
WORKTREE = "dyad-land"          # under the git common dir, beside the suite memo (Rule-12 p2)
NETWORK_TIMEOUT = 300           # seconds for a fetch or a push; the push includes the hook's guards


class Refused(Exception):
    """A refusal: printed as one `refused: …` line, exit 1, nothing pushed."""


def env() -> dict[str, str]:
    """The environment of every child here: the hook's GIT_VARS stripped (a git call must see the tree it is
    pointed at, #142), bytecode off (#412–#414)."""
    return {**dyadlib.git_env(), "PYTHONDONTWRITEBYTECODE": "1"}


def git(cwd: Path, *a: str, check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, env=env(), timeout=timeout)
    if check and r.returncode:
        raise Refused(f"git {' '.join(a)}: {(r.stderr or r.stdout).strip()}")
    return r


def out(cwd: Path, *a: str, **kw) -> str:
    return git(cwd, *a, **kw).stdout.strip()


# ---- the arguments
def split_argv(a: list[str], value_flags) -> tuple[list[str], str | None]:
    """The verb's own argv and the mirror branch: `--land` and `--mirror <branch>` removed by position (a flag's
    value is never a flag, as `dwork_args` reads it, #133), and a `--prompt-file` / `--said-file` path made
    absolute, because the verb runs in the worktree, not in the caller's directory."""
    argv, mirror, i = [], None, 0
    while i < len(a):
        x = a[i]
        if x in value_flags or x in ("--mirror", "-m"):
            if i + 1 >= len(a):
                raise Refused(f"{x} needs a value")
            v = a[i + 1]
            if x == "--mirror":
                mirror = v
            else:
                argv += [x, os.path.abspath(v) if x in ("--prompt-file", "--said-file") else v]
            i += 2; continue
        if x != "--land":
            argv.append(x)
        i += 1
    return argv, mirror


def check_mirror(repo: Path, mirror: str | None) -> None:
    if mirror is None:
        return
    if mirror == "main" or git(repo, "check-ref-format", "--branch", mirror, check=False).returncode:
        raise Refused(f"--mirror {mirror!r} is not a branch other than main")


# ---- the worktree
@contextlib.contextmanager
def locked(common: Path):
    """One land at a time per clone: `<common>/dyad-land.lock` holds the pid of its holder. A lock whose pid
    is not alive is stale and taken over; a live one refuses."""
    p = common / f"{WORKTREE}.lock"
    for _ in range(2):
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                pid = int(p.read_text().strip() or "0")
                os.kill(pid, 0)
            except (ValueError, ProcessLookupError, FileNotFoundError):
                p.unlink(missing_ok=True); continue
            except PermissionError:
                pass
            raise Refused(f"another land holds {p} (pid {pid}); wait for it, or remove the file if that process is gone")
    else:
        raise Refused(f"could not take {p}")
    try:
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
        yield
    finally:
        p.unlink(missing_ok=True)


def fetch(repo: Path) -> str:
    """Fetch `origin`'s main into `origin/main` and return its sha."""
    git(repo, "fetch", "-q", "origin", "+refs/heads/main:refs/remotes/origin/main", timeout=NETWORK_TIMEOUT)
    return out(repo, "rev-parse", "refs/remotes/origin/main")


def prepare(repo: Path, wt: Path, sha: str) -> None:
    """The tool-owned worktree, detached at `sha` and clean of every untracked and ignored file. Created when
    absent or broken; never the caller's checkout."""
    top = git(wt, "rev-parse", "--show-toplevel", check=False).stdout.strip() if (wt / ".git").is_file() else ""
    ok = bool(top) and Path(top).resolve() == wt.resolve()
    if not ok:
        shutil.rmtree(wt, ignore_errors=True)
        git(repo, "worktree", "prune")
        git(repo, "worktree", "add", "-q", "--detach", "-f", str(wt), sha)
    else:
        git(wt, "checkout", "-q", "--detach", "-f", sha)
        git(wt, "reset", "-q", "--hard", sha)
    git(wt, "clean", "-q", "-ffdx")


def written(wt: Path) -> list[str]:
    """Every path the worktree differs from its HEAD in: modified, added or untracked, ignored files left out."""
    raw = git(wt, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split("\0")   # unstripped: a status column may be a space
    return sorted({e[3:] for e in raw if len(e) > 3})


def outside(paths: list[str], prefix: str) -> list[str]:
    return [p for p in paths if not p.startswith(prefix)]


# ---- already landed (plan #443 attack 11)
def store(wt: Path, inst: str) -> Path:
    return wt / inst / "d-work"


def row_at(wt: Path, inst: str, rid: int) -> dyadlib.Row | None:
    p = store(wt, inst) / "rows" / f"{rid}.md"
    return dyadlib.parse_row_file(p.read_text()) if p.is_file() else None


def record_at(wt: Path, inst: str, rid: int) -> list[dict[str, str]]:
    p = store(wt, inst) / "provenance" / f"{rid}.md"
    return dyadlib.load_guard("agent", "provenance").parse(p.read_text(encoding="utf-8")) if p.is_file() else []


def already_landed(wt: Path, inst: str, pos: list[str], vals: dict, bare: set, words, today: str) -> str | None:
    """Why the entry this verb would write is already on the tree checked out at `wt`, or None. Read before the
    verb runs, on every try, so a rebuild after a moved `main` — or a re-run after a push whose outcome was not
    seen — never records twice."""
    prompt, said, d = words(vals, "prompt"), words(vals, "said"), vals.get("-d")
    verb = pos[0]
    if verb == "new" and len(pos) >= 2:
        title, mandate = pos[1], vals.get("--mandate")
        rows = sorted(store(wt, inst).joinpath("rows").glob("*.md"))
        for p in rows:
            if not p.stem.isdigit():
                continue
            r = dyadlib.parse_row_file(p.read_text())
            if r.title != title:
                continue
            first = (record_at(wt, inst, r.id) or [{}])[0]
            if mandate is not None and f"(mandate #{mandate})" in r.disposed:
                return f"#{r.id} {title!r} is already accreted under mandate #{mandate}"
            if first.get("text") in {t for t in (prompt, said) if t is not None}:
                return f"#{r.id} {title!r} already holds these words as its entry 1"
        return None
    if verb == "state" and len(pos) >= 3 and pos[1].isdigit():
        rid, state = int(pos[1]), pos[2]
        r = row_at(wt, inst, rid)
        if r is None:
            return None                     # the verb refuses it with its own words
        es = record_at(wt, inst, rid)
        if "--mandate" in vals:
            return f"#{rid} is already {state}" if r.state == state else None
        if d is not None:
            entries = [e.strip() for e in r.disposed.split(";") if e.strip()]
            last = [e for e in es if e["kind"] == "disposition"][-1:]
            if entries and entries[-1] == f"{today} {d}" and last and last[0]["text"] == said:
                return f"#{rid}'s last disposed entry is already {entries[-1]!r} with these words"
            return None
        if prompt is not None:
            return f"#{rid}'s record already ends with this prompt" if es and es[-1]["kind"] == "prompt" and es[-1]["text"] == prompt else None
        if r.state == state and ("-r" not in vals or vals["-r"] == r.refs):
            return f"#{rid} is already {state}"
    return None


# ---- commit and push
def subject(verb: str, pos: list[str], vals: dict, bare: set, stdout: str) -> str:
    """The generated `ledger: …` subject. It cites no `d-work #`: a ledger-only commit claims no d-work (Rule-3
    Ledger), so any such phrase in a title or an entry is written as a bare `#<id>`."""
    d, line = vals.get("-d"), (stdout.strip().splitlines() or [""])[-1]
    if verb == "new":
        rid = line.strip()
        what = f"accreted under mandate #{vals['--mandate']}" if "--mandate" in vals else ("backlog" if "--backlog" in bare else "open")
        s = f"ledger: #{rid} {what}{f' ({d})' if d else ''}: {pos[1]}"
    elif "--mandate" in vals:
        s = f"ledger: #{pos[1]} {pos[2]} (mandate #{vals['--mandate']})"
    else:
        s = f"ledger: #{pos[1]} {pos[2]}" + (f" ({d})" if d else " (prompt received)" if "--prompt" in vals or "--prompt-file" in vals else "")
    return dyadlib.load_guard("agent", "prs").CITE.sub(r"#\1", s)


def push(wt: Path, mirror: str | None) -> subprocess.CompletedProcess:
    refs = ["HEAD:refs/heads/main"] + ([f"HEAD:refs/heads/{mirror}"] if mirror else [])
    return git(wt, "push", "--porcelain", *(["--atomic"] if mirror else []), "origin", *refs, check=False, timeout=NETWORK_TIMEOUT)


def restore_landed(repo: Path, sha: str, landed) -> bool:
    """The caller-copy fix (#459): when every change of the checkout is a landed path, each byte-identical to its
    blob at `sha`, restore those paths from HEAD — a tracked one checked out from HEAD, an untracked or added one
    removed — so the fast-forward can bring the same bytes back. Every condition is read before the first write;
    any change outside `landed`, a rename, a deletion, a conflict or one differing byte returns False untouched."""
    raw = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split("\0")   # unstripped: a status column may be a space
    changed = {e[3:]: e[:2] for e in raw if len(e) > 3}
    if not changed or not set(changed) <= set(landed) or any(c in xy for xy in changed.values() for c in "RCDU"):
        return False
    for rel in changed:
        blob = git(repo, "rev-parse", "-q", "--verify", f"{sha}:{rel}", check=False).stdout.strip()
        if not blob or blob != out(repo, "hash-object", "--no-filters", "--", rel):
            return False
    tracked = [rel for rel in changed if git(repo, "cat-file", "-e", f"HEAD:{rel}", check=False).returncode == 0]
    fresh = [rel for rel in changed if rel not in tracked]
    if tracked:
        git(repo, "checkout", "-q", "HEAD", "--", *tracked)
    if fresh:
        git(repo, "rm", "-q", "--cached", "--ignore-unmatch", "--", *fresh)
        for rel in fresh:
            (repo / rel).unlink(missing_ok=True)
    print(f"restored {', '.join(sorted(changed))} from HEAD: each identical to its landed blob")
    return True


def fast_forward(repo: Path, sha: str, landed=()) -> None:
    """The caller's checkout, fast-forwarded only when it is on `main`, clean, and behind `sha`; else one line.
    With `landed` (the paths a `land` copied from it), a checkout whose only changes are those paths, identical
    to the landed blobs, is restored first (`restore_landed`) and then fast-forwarded (#459)."""
    branch = git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False).stdout.strip()
    dirty = out(repo, "status", "--porcelain", "--untracked-files=normal")
    behind = git(repo, "merge-base", "--is-ancestor", "HEAD", sha, check=False).returncode == 0
    if branch == "main" and dirty and behind and landed:
        try:
            if restore_landed(repo, sha, landed):
                dirty = out(repo, "status", "--porcelain", "--untracked-files=normal")
        except Refused as e:
            print(f"this checkout was not restored ({e})")
    if branch == "main" and not dirty and behind:
        git(repo, "merge", "-q", "--ff-only", sha)
        print(f"fast-forwarded main to {sha[:12]}")
    else:
        why = "not on main" if branch != "main" else "has changes" if dirty else "is not behind it"
        print(f"this checkout {why}: left as it is (origin/main is {sha[:12]})")


def land(repo: Path, inst: str, mirror: str | None, build, label: str, landed=()) -> int:
    """The loop: fetch, prepare, `build(wt)` -> (paths, subject, verb stdout) or a Refused, commit, push; a push
    refused while `origin/main` moved is rebuilt, at most TRIES times. `landed` names the caller's paths a `land`
    copies, for the caller-copy fix after the push (`fast_forward`)."""
    prefix = f"{inst}/d-work/"
    common = Path(out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / WORKTREE
    with locked(common):
        for attempt in range(1, TRIES + 1):
            base = fetch(repo)
            prepare(repo, wt, base)
            paths, msg, stdout = build(wt)
            bad = outside(paths, prefix)
            if bad:
                raise Refused(f"{label} wrote {', '.join(bad)}, outside {prefix}: that commit would not be ledger-only; nothing landed")
            if not paths:
                raise Refused(f"{label} wrote nothing; nothing to land")
            git(wt, "add", "-A", "--", *paths)
            git(wt, "commit", "-q", "-m", msg)
            sha = out(wt, "rev-parse", "HEAD")
            r = push(wt, mirror)
            if r.returncode == 0:
                if stdout.strip():
                    print(stdout.strip())
                print(f"landed {sha} on main{f' and {mirror}' if mirror else ''}")
                fast_forward(repo, sha, landed)
                return 0
            now = fetch(repo)
            if now == base:
                raise Refused(f"the push failed with main unmoved; nothing landed:\n{(r.stdout + r.stderr).strip()}")
            print(f"main moved to {now[:12]} (try {attempt}/{TRIES}): rebuilding from the inputs", file=sys.stderr)
        raise Refused(f"main moved on each of {TRIES} tries; nothing landed (origin/main is {now[:12]}); run it again")


# ---- the entries
def run_verb(wt: Path, inst: str, argv: list[str]) -> subprocess.CompletedProcess:
    """The worktree's own runner, as its `dyad/bin/dyad` would exec it, under this (already pinned) interpreter:
    its REPO is the worktree, so every write lands there (#427)."""
    return subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "dwork", *argv], cwd=wt, capture_output=True, text=True,
                          env={**env(), "DYAD_INSTANCE": inst})


def verb_builder(argv: list[str], pos: list[str], vals: dict, bare: set, inst: str, words):
    today = datetime.date.today().isoformat()
    def build(wt: Path):
        why = already_landed(wt, inst, pos, vals, bare, words, today)
        if why:
            raise Refused(f"already landed: {why}; nothing pushed")
        r = run_verb(wt, inst, argv)
        if r.returncode:
            sys.stderr.write(r.stderr); sys.stdout.write(r.stdout)
            raise Refused(f"dwork {pos[0]} refused it in the worktree; nothing landed")
        return written(wt), subject(pos[0], pos, vals, bare, r.stdout), r.stdout
    return build


def check_only(repo: Path, inst: str, argv: list[str], pos: list[str], vals: dict, bare: set, words) -> int:
    """`dwork state … --check --land` (#464): the verb's own `--check` run where `--land` would run it — the tool-owned
    worktree at a freshly fetched origin/main, after the `already landed` test — and nothing committed or pushed; the
    worktree is cleaned before its next use as always. Exit 0 on `ok`, the verb's refusal and 1 otherwise."""
    common = Path(out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / WORKTREE
    with locked(common):
        base = fetch(repo)
        prepare(repo, wt, base)
        why = already_landed(wt, inst, pos, vals, bare, words, datetime.date.today().isoformat())
        if why:
            raise Refused(f"already landed: {why}; nothing pushed")
        r = run_verb(wt, inst, argv)
        sys.stderr.write(r.stderr); sys.stdout.write(r.stdout)
        print(f"checked against origin/main {base[:12]}; nothing landed")
        return 1 if r.returncode else 0


def identical(repo: Path, wt: Path, rels: list[str]) -> bool:
    """Every named file of the caller already holds, byte for byte, what the worktree's tree holds."""
    return all((wt / rel).is_file() and (wt / rel).read_bytes() == (repo / rel).read_bytes() for rel in rels)


def copy_paths(repo: Path, wt: Path, rels: list[str]) -> None:
    for rel in rels:
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / rel, wt / rel)


def paths_builder(repo: Path, rels: list[str], msg: str):
    def build(wt: Path):
        copy_paths(repo, wt, rels)
        paths = written(wt)
        if not paths:
            raise Refused(f"already landed: {', '.join(rels)} on origin/main are identical; nothing pushed")
        return paths, msg, ""
    return build


def land_rels(repo: Path, inst: str, names: list[str], label: str = "dwork land") -> list[str]:
    """The paths a `land` names, each a file of this work tree under `<instance>/d-work/`, repo-relative."""
    if not names:
        raise Refused(f"{label} names at least one path")
    rels = []
    for p in names:
        src = Path(os.path.abspath(p))
        if not src.is_relative_to(repo):
            raise Refused(f"{p} lies outside this work tree")
        rel = src.relative_to(repo).as_posix()
        if not rel.startswith(f"{inst}/d-work/"):
            raise Refused(f"{rel} lies outside {inst}/d-work/: that commit would not be ledger-only")
        if not src.is_file():
            raise Refused(f"{rel} is not a file")
        rels.append(rel)
    return rels


# ---- the batch (#459)
BATCH_USAGE = ("usage: dwork batch <file>|- --land [--mirror <branch>] — one `dwork` argv per line, shell-quoted: "
               "`new …`, `state …` or `land <path>…`; blank and `#` lines are skipped; -m, --land and --mirror are the "
               "batch's, never a line's. A later line cannot name an id a `new` line of the same batch creates: that id "
               "is allocated in the worktree and re-allocated on a rebuild. Under `dwork-trace: always` a `Y done` line's "
               "trace rides the batch: a `land <instance>/d-work/traces/<id>.md` line before it (#465)")
SUBJECT_MAX = 200   # the generated subject is one line, cut to this many characters


class Line:
    """One parsed batch line: its number, its text, its verb and argv as the verb reads them, and for a `land`
    line its repo-relative paths."""
    def __init__(self, n: int, text: str, pos: list[str], vals: dict, bare: set, argv: list[str], rels: list[str]):
        self.n, self.text, self.pos, self.vals, self.bare, self.argv, self.rels = n, text, pos, vals, bare, argv, rels
        self.verb = pos[0]

    def where(self) -> str:
        return f"line {self.n} ({self.text})"


def as_refused(n: int, f, *a):
    """The runner's own readers (`dwork_args`, `words`) refuse by `sys.exit`; in a batch that is this line's
    refusal, named, never the process's exit."""
    try:
        return f(*a)
    except SystemExit as e:
        raise Refused(f"line {n}: {str(e.code).removeprefix('refused: ')}") from None


def read_batch(src: str, repo: Path, inst: str, value_flags, parse) -> list[Line]:
    """Every line of the batch parsed before anything runs; any refusal refuses the whole batch."""
    try:
        text = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise Refused(f"dwork batch {src}: {e}") from None
    lines = []
    for n, raw in enumerate(text.splitlines(), 1):
        t = raw.strip()
        if not t or t.startswith("#"):
            continue
        try:
            toks = shlex.split(t)
        except ValueError as e:
            raise Refused(f"line {n}: {e}") from None
        pos, vals, bare = as_refused(n, parse, toks)
        for flag, given in (("-m", "-m" in vals), ("--mirror", "--mirror" in vals), ("--land", "--land" in bare)):
            if given:
                raise Refused(f"line {n}: {flag} is the batch's, never a line's: the batch generates one subject, "
                              f"takes one --mirror and lands every line ({BATCH_USAGE})")
        verb = pos[0] if pos else None
        if verb not in ("new", "state", "land"):   # the verbs --land lands, and land
            raise Refused(f"line {n}: a batch line is `new`, `state` or `land <path>…`, not {verb!r}")
        if "--check" in bare:   # #464: a line that writes nothing has nothing to land; check it alone
            raise Refused(f"line {n}: --check writes nothing, so a batch cannot land it; run `dwork state … --check` alone")
        if verb == "land":
            if vals or bare:
                raise Refused(f"line {n}: land does not take {' '.join(sorted(set(vals) | bare))}")
            lines.append(Line(n, t, pos, vals, bare, [], land_rels(repo, inst, pos[1:], f"line {n}: land")))
        else:
            argv, _ = split_argv(toks, value_flags)          # a --prompt-file / --said-file made absolute
            lines.append(Line(n, t, pos, vals, bare, argv, []))
    if not lines:
        raise Refused(f"the batch holds no line ({BATCH_USAGE})")
    return lines


def done_order(lines: list[Line], today: str) -> None:
    """The fence's Done order (`rows.done_order_problems`, #202) kept before running: one commit may not both
    record a merge-naming `Y done` for a row and set that row `done`, so a batch may not either — whether one
    line does both or two lines do. The fence is unchanged and still judges the commit at the gate."""
    rg = dyadlib.load_guard("agent", "rows")
    records, closes = {}, {}
    for ln in lines:
        if ln.verb != "state" or len(ln.pos) < 3 or not ln.pos[1].isdigit():
            continue
        rid, d = int(ln.pos[1]), ln.vals.get("-d")
        if d is not None and rg.DONE_MERGES.search(f"{today} {d}"):
            records.setdefault(rid, ln)
        if ln.pos[2] == "done":
            closes.setdefault(rid, ln)
    for rid, rec in records.items():
        close = closes.get(rid)
        if close is None:
            continue
        both = (f"{rec.where()} records {rec.vals['-d']!r} and sets #{rid} done" if rec is close else
                f"{rec.where()} records {rec.vals['-d']!r} and {close.where()} sets #{rid} done")
        raise Refused(f"{both}, in one commit (Rule-3 Completion: the state follows the merge — record the entry "
                      f"with the state unchanged, merge, then `dyad dwork state <id> done`): land the record batch, "
                      f"merge, then the close batch; nothing landed")


def line_landed(repo: Path, wt: Path, inst: str, ln: Line, words, today: str) -> str | None:
    if ln.verb == "land":
        return f"{', '.join(ln.rels)} identical on origin/main" if identical(repo, wt, ln.rels) else None
    return as_refused(ln.n, already_landed, wt, inst, ln.pos, ln.vals, ln.bare, words, today)


def land_part(inst: str, rel: str) -> str:
    """A landed path, named for the subject: `presence <seat>`, `plan #<id>`, `trace #<id>`, else its path."""
    sub = rel.removeprefix(f"{inst}/d-work/")
    head, _, name = sub.partition("/")
    stem = name.removesuffix(".md")
    kind = {"sessions": "presence", "plans": "plan", "traces": "trace", "provenance": "provenance", "rows": "row"}.get(head)
    if kind is None or "/" in name:
        return sub
    return f"{kind} {stem}" if kind == "presence" else f"{kind} #{stem}"


def batch_subject(parts: list[str]) -> str:
    s = " ".join(f"ledger: batch {', '.join(parts)}".split())     # one line, whatever a title held
    if len(s) > SUBJECT_MAX:
        s = s[:SUBJECT_MAX - 1].rstrip(", ") + "…"
    return dyadlib.load_guard("agent", "prs").CITE.sub(r"#\1", s)


def batch_builder(repo: Path, lines: list[Line], inst: str, words):
    today = datetime.date.today().isoformat()
    def build(wt: Path):
        run = []
        for ln in lines:      # judged against origin/main before any line runs, on every try
            why = line_landed(repo, wt, inst, ln, words, today)
            if why:
                print(f"skipped (already landed): {ln.where()}: {why}")
            else:
                run.append(ln)
        if not run:
            raise Refused("already landed: every line of the batch is on origin/main; nothing pushed")
        parts, outs = [], []
        for ln in run:
            if ln.verb == "land":
                copy_paths(repo, wt, ln.rels)
                parts += [land_part(inst, rel) for rel in ln.rels]
                continue
            r = run_verb(wt, inst, ln.argv)
            if r.returncode:
                sys.stderr.write(r.stderr); sys.stdout.write(r.stdout)
                raise Refused(f"{ln.where()}: dwork {ln.verb} refused it in the worktree; the batch stops and nothing landed")
            outs.append(r.stdout.strip())
            parts.append(subject(ln.verb, ln.pos, ln.vals, ln.bare, r.stdout).removeprefix("ledger: "))
        return written(wt), batch_subject(parts), "\n".join(o for o in outs if o)
    return build


def batch(a_pos: list[str], vals: dict, bare: set, repo: Path, inst: str, mirror: str | None, value_flags, parse, words) -> int:
    if "--land" not in bare:
        raise Refused(f"dwork batch runs only with --land ({BATCH_USAGE})")
    if len(a_pos) != 2 or vals or bare - {"--land"}:
        raise Refused(BATCH_USAGE)
    lines = read_batch(a_pos[1], repo, inst, value_flags, parse)
    done_order(lines, datetime.date.today().isoformat())
    landed = sorted({rel for ln in lines for rel in ln.rels})
    return land(repo, inst, mirror, batch_builder(repo, lines, inst, words), "dwork batch", landed)


def main(a: list[str], repo: Path, value_flags, parse, words) -> int:
    """`a` is the `dwork` argv. `parse` and `words` are the runner's own (`package.dwork_args`, `package.words`),
    so a flag is read here exactly as the verb reads it."""
    repo = Path(repo)
    try:
        inst = dyadlib.instance_rel(repo)
        if inst is None:
            raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree; land writes only a tracked store")
        if a and a[0] == "batch":
            _, _, given = parse(a)
            argv, mirror = split_argv(a, value_flags)
            check_mirror(repo, mirror)
            pos, vals, bare = parse(argv)
            return batch(pos, vals, bare | (given & {"--land"}), repo, inst, mirror, value_flags, parse, words)
        argv, mirror = split_argv(a, value_flags)
        check_mirror(repo, mirror)
        pos, vals, bare = parse(argv)
        verb = pos[0] if pos else None
        if verb == "land":
            msg = vals.get("-m")
            if not msg or not msg.strip():
                raise Refused("usage: dwork land <path>... -m <message> [--mirror <branch>]")
            if set(vals) - {"-m"} or bare:
                raise Refused(f"dwork land does not take {' '.join(sorted((set(vals) - {'-m'}) | bare))}")
            if dyadlib.load_guard("agent", "prs").CITE.search(msg):
                raise Refused("-m cites a `d-work #`; a ledger-only commit claims no d-work (Rule-3 Ledger): write it as #<id>")
            rels = land_rels(repo, inst, pos[1:])
            return land(repo, inst, mirror, paths_builder(repo, rels, msg), "dwork land", rels)
        if verb not in ("new", "state"):
            raise Refused(f"--land lands `dwork new` or `dwork state`, not {verb!r}")
        if "-m" in vals:
            raise Refused(f"dwork {verb} --land generates its own subject; -m is `dwork land`'s")
        if "--check" in bare:
            return check_only(repo, inst, argv, pos, vals, bare, words)
        return land(repo, inst, mirror, verb_builder(argv, pos, vals, bare, inst, words), f"dwork {verb}")
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
