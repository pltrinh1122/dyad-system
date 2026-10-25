"""dyad host adapter (`crafts/syseng/rules/host-facts.md`, d-work #179): the one place a host fact
is read, so every call site sees the same answer regardless of which one asked. Rule-14 ("Library
and The World"): The World is observed, not pinned — a host's own filesystem layout (macOS's `/var`
-> `/private/var`) is such an observation, not a thing the package controls or should special-case
per call site. A library: no check semantics of its own (S4); its own check is
`dyad/tests/test_hostadapter.py` (`crafts/syseng/rules/verifiable-code.md` p4's mapping). Kernel:
Python 3.12+; stdlib only, beside the package's own `dyadlib` for the import-time invariants (Rule-14: no new manifest row — `hostadapter` resolves as a
package-internal import, `dyad/guards/infra/manifest.py`'s `python_imports`).

Two functions, not a framework (`host-facts.md` property 2): `resolve` wraps `Path.resolve()` so
`distribute.py`/`package.py` never call it inline (G5, d-work #179: a test once compared an
unresolved path against `distribute.install`'s already-resolved one, passing only by the accident
that this kernel's `/tmp` is not itself a symlink). `ignore_patterns` derives the Rule-11 property 6
`generated:` list of `package_rules.txt` — never a second, hand-kept copy of it — translated to
gitignore syntax, and `write_gitignore` seeds it once (G9: a fresh install's first `dyad` command
writes `dyad/scripts/__pycache__/`, and `git add -A` then tracks it). A third host fact either fits
one of these two functions or earns its own, justified in the plan that adds it — never a generic
hook (`host-facts.md` property 2). The third, `harness_sessions`, earned its own in plan #431 (attack 4;
d-work #434): the harness's own list of sessions for this repo, read in one place so another kernel
plugs in here as data and `sessions.reconcile` never reads a harness path itself."""
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HEADER = "# seeded by dyad install (hostadapter.write_gitignore) from dyad/scripts/package_rules.txt\n"


def resolve(path) -> Path:
    """The one place a host path is resolved to its canonical, symlink-free form. Every
    install/build destination and repo-root comparison `distribute.py`/`package.py` make calls
    this instead of `Path(...).resolve()` inline — grepping the two files for `.resolve()` after
    this change finds only the bootstrap `PKG = Path(__file__).resolve().parent.parent` lines,
    which must run before this module can even be imported (`craft.py`'s own such line is the
    third; it has no other `.resolve()` call to route)."""
    return Path(path).resolve()


def _to_gitignore(pattern: str) -> str:
    """One `package_rules.txt` `generated:` pattern (matched by `check_generated` at any path
    depth, component-wise — the whole path, any one segment, or any suffix starting at a segment)
    as one gitignore line matching at the same depths: a `dir/*` pattern becomes `dir/` — a
    trailing-only slash is unanchored under gitignore's own rule ("a separator at the beginning or
    middle" anchors; one only at the end does not), so it matches a directory named `dir` at any
    depth. A literal `dir/*` would not: gitignore anchors a *middle* slash to the `.gitignore`
    file's own directory, so a naive translation would miss a nested `dyad/scripts/__pycache__/`
    (G9's exact case) and only catch a root-level one. Any other pattern with an interior slash
    (`ops/*.log`) is prefixed `**/` for the same any-depth match. A slash-free pattern (`*.pyc`,
    `LEDGER.md`) is already unanchored and needs no change."""
    if pattern.endswith("/*"):
        return pattern[:-1]
    return f"**/{pattern}" if "/" in pattern else pattern


def ignore_patterns(root) -> list[str]:
    """Rule-11 property 6's `generated:` patterns, translated by `_to_gitignore`; parsed straight
    from `<root>/dyad/scripts/package_rules.txt` — the same file `check_generated` reads — so the
    list can never drift from it (never hand-duplicated here). Sorted, deduplicated; `[]` when that
    file is not (yet) part of the tree at `root` (a Tended-craft-only root; a fixture without a
    core craft)."""
    p = Path(root) / "dyad" / "scripts" / "package_rules.txt"
    if not p.is_file():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, val = line.partition(":")
        if kind.strip() == "generated":
            out.append(_to_gitignore(val.strip()))
    return sorted(set(out))


def write_gitignore(dest) -> bool:
    """Seed `<dest>/.gitignore` from `ignore_patterns(dest)` when the file is absent. Never
    overwrites — idempotent (`crafts/syseng/rules/idempotence.md` property 1) and consistent with
    Rule-11 property 2, "never overwrites a host file". `True` when it wrote, so a caller can count
    it as one change the way `distribute.install`'s other hooks already do."""
    dest = Path(dest)
    f = dest / ".gitignore"
    if f.exists():
        return False
    patterns = ignore_patterns(dest)
    if not patterns:
        return False
    f.write_text(HEADER + "\n".join(patterns) + "\n")
    return True


# The harness's session store (d-work #434, child C1 of #431). One kernel's layout, observed, never pinned (Rule-14
# property 4): Claude Code keeps `<base>/projects/<slug>/<session id>.jsonl`, one transcript per session, `<slug>`
# the launch directory with every character outside [A-Za-z0-9] replaced by `-`; a session's title, when it has one,
# is the last `custom-title` record's `customTitle` (a title set by hand), else the last `ai-title` record's `aiTitle`.
HARNESS_DIR_ENV = "DYAD_HARNESS_DIR"                   # the dyad's override of the base (tests point it at a fake dir)
HARNESS_KERNEL_ENV = "CLAUDE_CONFIG_DIR"               # the harness's own override of its base, honoured next
TITLE_RECORDS = (("custom-title", "customTitle"), ("ai-title", "aiTitle"))   # in order of precedence


def harness_dir() -> Path:
    """The harness's base directory: `DYAD_HARNESS_DIR`, else `CLAUDE_CONFIG_DIR`, else `~/.claude`."""
    for var in (HARNESS_DIR_ENV, HARNESS_KERNEL_ENV):
        if os.environ.get(var):
            return Path(os.environ[var])
    return Path.home() / ".claude"


def _slug(path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def checkouts(root) -> list[Path]:
    """`root` resolved and, when it is a linked worktree, the main checkout beside it: a session is filed under the
    directory it was launched in, which for a worktree's work is usually the main checkout. Read from the `.git`
    file and its `commondir`, never by running git."""
    root = resolve(root)
    out, dotgit = [root], root / ".git"
    if dotgit.is_file():
        m = re.match(r"gitdir:\s*(.+)", dotgit.read_text(errors="ignore").strip())
        if m:
            gitdir = (root / m.group(1).strip()).resolve()
            common = gitdir / "commondir"
            base = (gitdir / common.read_text().strip()).resolve() if common.is_file() else gitdir.parent.parent
            if base.name == ".git" and base.parent not in out:
                out.append(base.parent)
    return out


def _title(transcript: Path) -> str:
    """The session's title from its transcript's title records — the last of the first kind in TITLE_RECORDS that
    occurs — or "". Only a line naming a title record is decoded; nothing else of the transcript is read into memory."""
    found: dict[str, str] = {}
    with transcript.open(errors="ignore") as f:
        for line in f:
            if "title" not in line:
                continue
            for kind, key in TITLE_RECORDS:
                if kind in line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        break
                    if isinstance(rec, dict) and rec.get("type") == kind and isinstance(rec.get(key), str):
                        found[kind] = rec[key]
                    break
    return next((found[k] for k, _ in TITLE_RECORDS if k in found), "")


def harness_sessions(root=None, base=None) -> list[dict]:
    """The harness's own session records for the repo at `root` (default the current directory): one
    `{"id": <harness session id>, "title": <title or "">}` per session, sorted by id. `[]` when the kernel keeps no
    store here (the directory is absent), so a harness that keeps none — or keeps it elsewhere — reads as data, not
    an error. Read-only; stdlib only."""
    projects = Path(base or harness_dir()) / "projects"
    out: dict[str, str] = {}
    for checkout in checkouts(root or Path.cwd()):
        d = projects / _slug(checkout)
        if not d.is_dir():
            continue
        for t in sorted(d.glob("*.jsonl")):
            if t.is_file() and t.stem not in out:
                try:
                    out[t.stem] = _title(t)
                except OSError:
                    out[t.stem] = ""
    return [{"id": k, "title": v} for k, v in sorted(out.items())]


INVARIANTS = [("title-records-custom-before-ai", lambda: [k for k, _ in TITLE_RECORDS] == ["custom-title", "ai-title"]
               and all(k and v for k, v in TITLE_RECORDS)),
              ("slug-keeps-only-alphanumerics", lambda: _slug("/srv/dyad-system") == "-srv-dyad-system"
               and _slug("/a/b.c_d") == "-a-b-c-d")]   # crafts/syseng/rules/invariants.md
dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (#203)
