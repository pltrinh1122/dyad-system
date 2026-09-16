"""The one distribution code path (Rule-11 property 5, #156): every craft — the core craft `dyad/` and
each Tended craft `crafts/<craft>/` — is built and installed by the functions here. `package.py build|install`
(core: roots=["dyad"] + the `dyad-*` workflows, hooks=the core's) and `craft.py export|install` (a Tended craft:
roots=["crafts/<name>"], no hooks, prune) are thin callers. A library: no check semantics (S4) except
`instance_state`, whose semantics are Rule-11 property 1's and whose data is `package_rules.txt`.
Kernel: Python 3.12+; stdlib only (Rule-14: no new row; `hostadapter` is package-internal).

Deterministic build: entries sorted by path, arcname = repo-relative path, mtime 0, uid/gid 0, empty
uname/gname, mode 0644 or 0755, gzip header mtime 0 and no name — so two builds of one tree are
byte-identical and `archive_sha256` is a stable identity of a tree (the craft registry's `sha256`,
Rule-11 p2). Install copies every file whose bytes or mode differ, creates missing ones and, with
`prune`, deletes files under `roots` the source lacks; a second run on an unchanged source is 0
changes. Every path this module resolves to canonical form goes through `hostadapter.resolve`
(crafts/syseng/rules/host-facts.md, d-work #179), never `Path(...).resolve()` inline, so a host's own
filesystem layout (a symlinked temp dir) is read in exactly one place.

Modes come from the git index (`git_modes`, a source work tree) or an archive's own tar members
(`archive_modes`, a source built here) — never `os.access(p, os.X_OK)` beyond a last-resort fallback
for a bare directory that is neither: on a `core.fileMode=false` checkout (an NTFS mount, `#135`/`#141`,
`dyadlib.tracked_mode`'s own trap) the disk bit reads executable for every file, executable or not, so
a build from one and an install into one both need the index, not the filesystem, as the source of
truth (workstation#173, #196 d-work #6). `install()` writes a changed 755 file's bit to the
destination's index too (`git update-index --chmod`) when the destination is a work tree — the one
channel `core.fileMode=false` leaves for the bit to reach a later `git add`."""
import filecmp, fnmatch, gzip, hashlib, io, os, shutil, subprocess, tarfile, tempfile
from dataclasses import dataclass, field
from pathlib import Path
import hostadapter

SKIP_DIRS = {"__pycache__", ".git"}
INVARIANTS = [("skip-dirs-are-generated-or-git", lambda: SKIP_DIRS <= {"__pycache__", ".git", ".pytest_cache"}),   # crafts/syseng/rules/invariants.md
              ("skip-dirs-non-empty", lambda: bool(SKIP_DIRS))]


def _git_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}


def _is_work_tree(repo: Path) -> bool:
    """`repo` itself (not a subdirectory of one — an extracted archive under a repo walks instead, same
    boundary `_git_files` already draws)."""
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=repo, capture_output=True, text=True, env=_git_env())
    return top.returncode == 0 and hostadapter.resolve(top.stdout.strip()) == hostadapter.resolve(repo)


def _git_files(repo: Path, roots) -> list[str] | None:
    """Tracked files under `roots` (directories or exact paths), repo-relative, sorted; None if `repo` is
    not a git work tree (then the caller walks the tree instead)."""
    if not _is_work_tree(repo):
        return None
    r = subprocess.run(["git", "ls-files", "-z", "--", *roots], cwd=repo, capture_output=True, env=_git_env())
    if r.returncode != 0:
        return None
    out = sorted(p for p in r.stdout.decode().split("\0") if p and (repo / p).is_file())
    return out


def git_modes(repo: Path, roots) -> dict[str, int]:
    """{repo-relative path: 0o755 | 0o644} from the git index (`git ls-files -s`) under `roots`, one call —
    never the disk bit, which `core.fileMode=false` (an NTFS checkout) decouples from what a build, a clone
    or CI actually see (module docstring; #196 d-work #6). Empty when `repo` is not a work tree."""
    if not _is_work_tree(repo):
        return {}
    r = subprocess.run(["git", "ls-files", "-s", "-z", "--", *roots], cwd=repo, capture_output=True, env=_git_env())
    if r.returncode != 0:
        return {}
    out = {}
    for line in r.stdout.decode().split("\0"):
        if not line:
            continue
        meta, _, path = line.partition("\t")
        out[path] = 0o755 if meta.split()[0] == "100755" else 0o644
    return out


def archive_modes(archive: Path) -> dict[str, int]:
    """{archive-relative path: 0o755 | 0o644} straight from a tar.gz's own members, read before extraction
    could lose them: on a `core.fileMode=false` mount `chmod` after `extract()` does not reliably stick
    (the same disk-bit trap `git_modes` avoids on the build side), so an install *from an archive* must
    read modes from the archive itself, never re-derive them from the extracted tree's disk bits."""
    with tarfile.open(archive, "r:gz") as tar:
        return {m.name: (0o755 if m.mode & 0o111 else 0o644) for m in tar.getmembers() if m.isreg()}


def _walk_files(root: Path, roots) -> list[str]:
    out = []
    for r in roots:
        p = root / r
        if p.is_file():
            out.append(r)
        elif p.is_dir():
            for dp, dns, fns in os.walk(p):
                dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
                for fn in fns:
                    out.append(str((Path(dp) / fn).relative_to(root)).replace(os.sep, "/"))
    return sorted(set(out))


def files(repo: Path, roots, extra=(), tracked: bool = True) -> list[str]:
    """Every file of the tree under `roots` plus `extra` exact paths: tracked files when `repo` is a git work
    tree (and `tracked`), else a walk (an extracted archive; an install destination, whose stale files may be
    untracked). Repo-relative, sorted, `__pycache__` excluded."""
    repo = Path(repo)
    got = _git_files(repo, [*roots, *extra]) if tracked else None
    if got is None:
        got = _walk_files(repo, [*roots, *extra])
    return sorted(p for p in got if not any(part in SKIP_DIRS for part in p.split("/")))


def _mode(p: Path) -> int:
    return 0o755 if os.access(p, os.X_OK) and not p.is_dir() else 0o644


def archive_bytes(repo: Path, roots, extra=(), tracked: bool = True) -> bytes:
    """The deterministic tar.gz of `files(repo, roots, extra, tracked)`; see the module docstring."""
    repo = Path(repo)
    modes = git_modes(repo, [*roots, *extra]) if tracked else {}   # {} when repo is not a work tree: _mode(p) falls back below
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz, tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar:
        for rel in files(repo, roots, extra, tracked):
            p = repo / rel
            info = tarfile.TarInfo(rel)
            info.size = p.stat().st_size; info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = ""
            info.mode = modes.get(rel, _mode(p)); info.type = tarfile.REGTYPE
            with p.open("rb") as fh:
                tar.addfile(info, fh)
    return buf.getvalue()


def build(repo: Path, roots, out, extra=()) -> Path:
    out = Path(out)
    out.write_bytes(archive_bytes(repo, roots, extra))
    return out


def archive_sha256(repo: Path, roots, extra=(), tracked: bool = True) -> str:
    """sha256 of the deterministic archive of a tree — a stable identity (the registry's column; there the tree
    on disk is hashed, `tracked=False`, since an installed tree is not yet committed)."""
    return hashlib.sha256(archive_bytes(repo, roots, extra, tracked)).hexdigest()


def extract(archive: Path, into: Path) -> Path:
    """Unpack an archive built here into `into` (regular files only, no absolute or `..` members)."""
    into = Path(into)
    with tarfile.open(archive, "r:gz") as tar:
        for m in tar.getmembers():
            if not m.isreg() or m.name.startswith("/") or ".." in Path(m.name).parts:
                raise ValueError(f"{archive}: refused member {m.name!r}")
            dst = into / m.name; dst.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(m) as fh:
                dst.write_bytes(fh.read())
            dst.chmod(m.mode & 0o777)
    return into


@dataclass(frozen=True)
class Hooks:
    """The host-side hooks of a core install (Rule-11 property 2): instance seeds copied from
    `<template_dir>/<name>` to `<dest>/<path>` when absent, one import line appended to the host frame,
    and, when `gitignore`, a `.gitignore` seed written by `hostadapter.write_gitignore` (d-work #179,
    G9) — derived from `package_rules.txt`, not a template file, since its content must never drift
    from the generated: list `check_generated` itself reads. A Tended craft install passes
    `hooks=None` and writes nothing outside its roots."""
    templates: dict[str, str] = field(default_factory=dict)   # template name -> dest-relative path
    import_line: str = ""
    frame: str = "CLAUDE.md"
    template_dir: str = "dyad/templates"
    gitignore: bool = False


def source_tree(src: Path, tmp: str | None = None) -> Path:
    """`src` as a directory: itself when a directory, else the archive extracted under a temp dir."""
    src = Path(src)
    if src.is_dir():
        return src
    return extract(src, Path(tmp or tempfile.mkdtemp(prefix="dyad-install-")))


def install(src: Path, dest: Path, roots, prune: bool = False, hooks: Hooks | None = None, extra=()) -> int:
    """Install the tree under `roots` (+ `extra` exact paths) of `src` — a repo/tree directory or an archive —
    into `dest`. Returns the number of changes: files written (new or differing bytes or mode), files pruned,
    seeds and import lines added. Second call on an unchanged source: 0."""
    dest = hostadapter.resolve(dest)
    src_path = Path(src)
    is_archive = not src_path.is_dir()
    tmp = tempfile.mkdtemp(prefix="dyad-install-") if is_archive else None
    try:
        root = source_tree(src, tmp)
        wanted = files(root, roots, extra)
        # source modes: an archive's own members (extraction cannot be trusted to preserve them on a
        # core.fileMode=false mount, module docstring); else the source work tree's index; else the disk
        # bit, for a bare directory that is neither (e.g. a test fixture with no .git at all)
        src_modes = archive_modes(src_path) if is_archive else git_modes(root, [*roots, *extra])
        dest_is_repo = _is_work_tree(dest)
        dest_modes = git_modes(dest, [*roots, *extra]) if dest_is_repo else {}
        changed = 0
        for rel in wanted:
            s, d = root / rel, dest / rel
            mode = src_modes.get(rel, _mode(s))
            if d.exists() and filecmp.cmp(s, d, shallow=False) and dest_modes.get(rel, _mode(d)) == mode:
                continue
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(s, d); d.chmod(mode)
            if dest_is_repo:   # the disk chmod above is not what `git add` later reads (fileMode=false); stage the bit itself
                subprocess.run(["git", "update-index", "--add", "--chmod=" + ("+x" if mode == 0o755 else "-x"), "--", rel],
                                cwd=dest, capture_output=True, env=_git_env())
            changed += 1
        if prune:
            have = set(wanted)
            for rel in files(dest, roots, tracked=False):
                if rel not in have:
                    (dest / rel).unlink(); changed += 1
            for r in roots:   # then the directories left empty, deepest first; the root itself stays
                for dp in sorted((Path(d) for d, _, _ in os.walk(dest / r)), key=lambda x: -len(x.parts)):
                    if dp != dest / r and not any(dp.iterdir()):
                        dp.rmdir()
        if hooks:
            for t, dst_rel in hooks.templates.items():
                d = dest / dst_rel
                if not d.exists():
                    d.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / hooks.template_dir / t, d); changed += 1
            if hooks.import_line:
                frame = dest / hooks.frame
                text = frame.read_text() if frame.exists() else ""
                if hooks.import_line not in text.splitlines():
                    frame.write_text(text.rstrip("\n") + ("\n" if text else "") + hooks.import_line + "\n"); changed += 1
            if hooks.gitignore and hostadapter.write_gitignore(dest):
                changed += 1
        return changed
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


def instance_state(repo: Path, roots, rules: dict, exempt=("templates",), names=(), what: str = "the package", extra=(), tracked: bool = True) -> list[str]:
    """Rule-11 property 1 over the craft tree(s) `roots` (repo-relative; `extra` exact files too): a host-specific
    `string:` in a file's text, an instance artifact by file `name:` or first-line `header:` (data:
    `package_rules.txt`, plus craft-specific `names` — a basename, a glob, or a `dir/` that must not be a path
    component, e.g. `REGISTRY.md`, `*.jsonl`, `events/`, `rows/`); `<root>/<exempt>/` directories are seeds and
    skipped, as is `package_rules.txt` itself (it holds the markers). `tracked=False` scans the tree on disk (a
    craft tree, whose untracked files would ship or be pruned; #156). Bare lines: failures."""
    repo = Path(repo); fails = []
    roots = [roots] if isinstance(roots, str) else list(roots)
    for rel in files(repo, roots, extra, tracked):
        root = next((r for r in roots if rel.startswith(r.rstrip("/") + "/")), None)
        inner = rel[len(root.rstrip("/")) + 1:] if root else rel
        if any(inner.startswith(e.rstrip("/") + "/") for e in exempt) or Path(rel).name == "package_rules.txt":
            continue
        p = repo / rel
        text = p.read_text(errors="ignore")
        for m in rules.get("string", []):
            if m in text:
                fails.append(f"{rel}: host-specific string '{m}' inside {what}")
        for n in [*rules.get("name", []), *names]:
            if n.endswith("/"):
                if n.rstrip("/") in inner.split("/")[:-1]:
                    fails.append(f"{rel}: instance store directory '{n}' inside {what}")
            elif p.name == n or p.name.endswith(n) or fnmatch.fnmatch(p.name, n):
                fails.append(f"{rel}: instance artifact by name '{n}' inside {what}")
        first = text.splitlines()[0] if text else ""
        for h in rules.get("header", []):
            if first.startswith(h):
                fails.append(f"{rel}: instance artifact by header '{h}' inside {what}")
    return fails
