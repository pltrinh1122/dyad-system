#!/usr/bin/env python3
"""`dyad dwork … --land` and `dyad dwork land` (d-work #447, child C1 of plan #443). Kernel: Python 3.12+, git.

One call per ledger record, in place of the series a seat ran by hand — fetch, reset, `dwork state`, commit, a
push to `main` through the pre-push hook, retries when `main` had moved, then a mirror push (plan #443 Evidence:
4–6 tool calls and about 2.1 hook runs per record):

  dyad dwork new|state … --land [--mirror <branch>]
                          run the verb in the tool-owned worktree, commit what it wrote, push it
  dyad dwork land <path>... -m <msg> [--mirror <branch>]
                          copy the named files (plan files, presence, traces) from this checkout into that worktree,
                          commit and push them the same way

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
fast-forwarded to it; otherwise only the sha is printed.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("land.py: Python 3.12+ required")
import contextlib, datetime, os, shutil, subprocess
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


def fast_forward(repo: Path, sha: str) -> None:
    """The caller's checkout, fast-forwarded only when it is on `main`, clean, and behind `sha`; else one line."""
    branch = git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False).stdout.strip()
    dirty = out(repo, "status", "--porcelain", "--untracked-files=normal")
    if branch == "main" and not dirty and git(repo, "merge-base", "--is-ancestor", "HEAD", sha, check=False).returncode == 0:
        git(repo, "merge", "-q", "--ff-only", sha)
        print(f"fast-forwarded main to {sha[:12]}")
    else:
        why = "not on main" if branch != "main" else "has changes" if dirty else "is not behind it"
        print(f"this checkout {why}: left as it is (origin/main is {sha[:12]})")


def land(repo: Path, inst: str, mirror: str | None, build, label: str) -> int:
    """The loop: fetch, prepare, `build(wt)` -> (paths, subject, verb stdout) or a Refused, commit, push; a push
    refused while `origin/main` moved is rebuilt, at most TRIES times."""
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
                fast_forward(repo, sha)
                return 0
            now = fetch(repo)
            if now == base:
                raise Refused(f"the push failed with main unmoved; nothing landed:\n{(r.stdout + r.stderr).strip()}")
            print(f"main moved to {now[:12]} (try {attempt}/{TRIES}): rebuilding from the inputs", file=sys.stderr)
        raise Refused(f"main moved on each of {TRIES} tries; nothing landed (origin/main is {now[:12]}); run it again")


# ---- the two entries
def verb_builder(argv: list[str], pos: list[str], vals: dict, bare: set, inst: str, words):
    today = datetime.date.today().isoformat()
    def build(wt: Path):
        why = already_landed(wt, inst, pos, vals, bare, words, today)
        if why:
            raise Refused(f"already landed: {why}; nothing pushed")
        # the worktree's own runner, as its `dyad/bin/dyad` would exec it, under this (already pinned) interpreter:
        # its REPO is the worktree, so every write lands there (#427)
        r = subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "dwork", *argv], cwd=wt, capture_output=True, text=True,
                           env={**env(), "DYAD_INSTANCE": inst})
        if r.returncode:
            sys.stderr.write(r.stderr); sys.stdout.write(r.stdout)
            raise Refused(f"dwork {pos[0]} refused it in the worktree; nothing landed")
        return written(wt), subject(pos[0], pos, vals, bare, r.stdout), r.stdout
    return build


def paths_builder(repo: Path, rels: list[str], msg: str):
    def build(wt: Path):
        for rel in rels:
            (wt / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / rel, wt / rel)
        paths = written(wt)
        if not paths:
            raise Refused(f"already landed: {', '.join(rels)} on origin/main are identical; nothing pushed")
        return paths, msg, ""
    return build


def main(a: list[str], repo: Path, value_flags, parse, words) -> int:
    """`a` is the `dwork` argv. `parse` and `words` are the runner's own (`package.dwork_args`, `package.words`),
    so a flag is read here exactly as the verb reads it."""
    repo = Path(repo)
    try:
        inst = dyadlib.instance_rel(repo)
        if inst is None:
            raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree; land writes only a tracked store")
        argv, mirror = split_argv(a, value_flags)
        check_mirror(repo, mirror)
        pos, vals, bare = parse(argv)
        verb = pos[0] if pos else None
        if verb == "land":
            msg, rels = vals.get("-m"), []
            if not msg or not msg.strip():
                raise Refused("usage: dwork land <path>... -m <message> [--mirror <branch>]")
            if set(vals) - {"-m"} or bare:
                raise Refused(f"dwork land does not take {' '.join(sorted((set(vals) - {'-m'}) | bare))}")
            if dyadlib.load_guard("agent", "prs").CITE.search(msg):
                raise Refused("-m cites a `d-work #`; a ledger-only commit claims no d-work (Rule-3 Ledger): write it as #<id>")
            if len(pos) < 2:
                raise Refused("dwork land names at least one path")
            for p in pos[1:]:
                src = Path(os.path.abspath(p))
                if not src.is_relative_to(repo):
                    raise Refused(f"{p} lies outside this work tree")
                rel = src.relative_to(repo).as_posix()
                if not rel.startswith(f"{inst}/d-work/"):
                    raise Refused(f"{rel} lies outside {inst}/d-work/: that commit would not be ledger-only")
                if not src.is_file():
                    raise Refused(f"{rel} is not a file")
                rels.append(rel)
            return land(repo, inst, mirror, paths_builder(repo, rels, msg), "dwork land")
        if verb not in ("new", "state"):
            raise Refused(f"--land lands `dwork new` or `dwork state`, not {verb!r}")
        if "-m" in vals:
            raise Refused(f"dwork {verb} --land generates its own subject; -m is `dwork land`'s")
        return land(repo, inst, mirror, verb_builder(argv, pos, vals, bare, inst, words), f"dwork {verb}")
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
