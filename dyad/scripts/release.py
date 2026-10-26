#!/usr/bin/env python3
"""`dyad release [--scan]`: the release service, the core's verb (d-work #470; born `.github/released.py`, d-work #461,
plan revisions 3 and 4), run by the `released` workflow (`.github/workflows/dyad-release.yml`) on every push to main
touching the rows and on dispatch. Kernel: Python 3.12+, git; `gh` is its library adapter (Rule-14).

The trigger is the ledger entry that records the Operator's release Y (Rule-11 Ratification events), written on the
release's row by the cos, ledger-only: `<date> Y release <tag> at <cut sha> (archive <sha256>)`. This verb reads every
row's `disposed` entries of that shape from the instance's row store (`<instance>/d-work/rows`, `DYAD_INSTANCE`) and,
for each one, checks the cut sha is on main (an ancestor of HEAD, the checkout of main) and tag == VERSION at it, builds
by the one code path in a detached worktree at that sha (Rule-11 property 5: that tree's own `dyad/scripts/package.py
build|bundle build` or `craft.py export`, run by this interpreter), verifies the archive sha256, then creates the
annotated tag, pushes it to `origin` and creates the GitHub Release (`gh release create`). Idempotent: a tag at the cut
sha with its Release is `already` and nothing runs; a tag at the cut sha without a Release gets its Release; a tag
elsewhere is refused (tags never move). An entry `Y release <tag>` without `at` predates the service and is not read; a
`Y release <tag> at …` of another shape is refused. Clerical execution of the recorded Y, never a disposer (Rule-2).

It writes nothing to the repo (plan #461 revision 4): its record is the annotated tag, the Release (with
`<tag>.release.json`) and the run's log and summary; the build worktree and its scratch dir are removed after each
entry. On a push it reads only the entries the push added (`BEFORE`, the push's `before` sha), so an entry refused once
is not re-run, and re-red, on every later push; a dispatch with `tag` (`ONLY`) retries one.

  dyad release --scan   read-only: print `pending: <tags>|none` and, when GITHUB_OUTPUT is set, append
                        `pending=true|false` to it, for the gated job; nothing is built, tagged or written; exit 0
  dyad release          publish every pending entry: one JSON line per entry (tag, row, outcome released | already |
                        refused | failed, detail), a table appended to GITHUB_STEP_SUMMARY when set, `<n> release
                        entries`; exit 1 when any entry is refused or failed, or `ONLY` names no entry

Environment: BEFORE (the push's before sha; empty or all-zero on a dispatch), ONLY (one tag), GITHUB_REPOSITORY,
GATE (default `ledger`), GITHUB_OUTPUT, GITHUB_STEP_SUMMARY, GITHUB_SERVER_URL, GITHUB_RUN_ID, GITHUB_SHA, GH_TOKEN
(read by `gh`). Every git and Python child runs under `dyadlib.git_env()` (a hook's GIT_VARS dropped, #142).
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("release.py: Python 3.12+ required")
import hashlib, json, os, re, shutil, subprocess, tempfile
from dataclasses import dataclass
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

TAG_RE = re.compile(r"(?:(?P<craft>[a-z0-9][a-z0-9-]*)-)?v(?P<ver>\d+\.\d+\.\d+)")
ENTRY_RE = re.compile(r"\S+ Y release (?P<tag>\S+) at (?P<sha>[0-9a-f]{7,40}) \(archive (?P<sha256>[0-9a-f]{64})\)")
DISPOSED_RE = re.compile(r"^disposed:[ \t]*(.*)$", re.M)

_ENTRY = "2026-10-26 Y release dyad-operator-v0.12.2 at abc1234 (archive " + "0" * 64 + ")"
INVARIANTS = [   # crafts/syseng/rules/invariants.md: the two shapes the Operator's recorded Y is read through
    ("tag-shape-reads-bundle-core-and-craft", lambda: [TAG_RE.fullmatch(t)["craft"] for t in ("v0.16.2", "dyad-operator-v0.12.2", "sysadmin-v1.0.0")] == [None, dyadlib.CORE_CRAFT, "sysadmin"]),
    ("tag-shape-refuses-a-bare-or-short-version", lambda: not any(TAG_RE.fullmatch(t) for t in ("0.12.2", "v0.12", "dyad-operator-0.12.2"))),
    ("entry-shape-reads-tag-cut-and-archive", lambda: (lambda g: (g["tag"], g["sha"], g["sha256"]) == ("dyad-operator-v0.12.2", "abc1234", "0" * 64))(ENTRY_RE.fullmatch(_ENTRY))),
    ("entry-shape-needs-the-archive-digest", lambda: ENTRY_RE.fullmatch(_ENTRY.replace("0" * 64, "0" * 63)) is None and ENTRY_RE.fullmatch(_ENTRY.split(" (archive")[0]) is None),
]


class Refused(Exception):
    """An entry the service will not publish: one `refused` line, exit 1."""


@dataclass(frozen=True)
class Ctx:
    """One run's inputs, read from the environment by `context` (never at import, so a test can import the module)."""
    root: Path                       # the checkout of main
    rows: Path                       # `<instance>/d-work/rows` on disk
    rows_rel: str | None             # the same, repo-relative, for `git show <BEFORE>:…`; None outside the work tree
    only: str                        # ONLY: one tag, or ''
    repo: str                        # GITHUB_REPOSITORY, `owner/name`
    gate: str                        # GATE: `ledger` or `tap`
    old: frozenset | None            # (row, entry) pairs on main before this push; None: read every entry


# ---- children
def child_env() -> dict[str, str]:
    """Every child's environment: the hook's GIT_VARS stripped (#142), bytecode off (as land.py, #412–#414)."""
    return {**dyadlib.git_env(), "PYTHONDONTWRITEBYTECODE": "1"}


def git(root: Path, *a: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, env=child_env())
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a[:2])} exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r


def gh(*a: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["gh", *a], capture_output=True, text=True, env=child_env())
    if check and r.returncode:
        raise RuntimeError(f"gh {' '.join(a[:2])} exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r


def builder(tree: Path, script: str, *a: str) -> None:
    """The cut's own builder (`dyad/scripts/<script>`) run by this interpreter — the one the entrypoint pinned."""
    r = subprocess.run([sys.executable, str(tree / "dyad" / "scripts" / script), *a], cwd=tree, capture_output=True,
                       text=True, env=child_env())
    if r.returncode:
        raise RuntimeError(f"{script} {' '.join(a[:2])} exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")


# ---- the entries
def context(root: Path, environ=None) -> Ctx:
    env = os.environ if environ is None else environ
    before, only = env.get("BEFORE", "").strip(), env.get("ONLY", "").strip()
    rows, inst = dyadlib.rows_dir(root), dyadlib.instance_rel(root)
    rows_rel = f"{inst}/d-work/rows" if inst is not None else None
    old = None
    if before and set(before) != {"0"} and not only:
        old = frozenset(entries_at(root, rows_rel, before))
    return Ctx(root, rows, rows_rel, only, env.get("GITHUB_REPOSITORY", ""), env.get("GATE", "ledger"), old)


def split_disposed(text: str) -> list[str]:
    m = DISPOSED_RE.search(text)
    return [e.strip() for e in m.group(1).split(";")] if m else []


def entries_at(root: Path, rows_rel: str | None, rev: str) -> set[tuple[str, str]]:
    """The (row, entry) pairs on the rows at `rev` (git show), for the push filter."""
    if rows_rel is None:
        return set()
    seen = set()
    for n in git(root, "ls-tree", "--name-only", f"{rev}:{rows_rel}", check=False).stdout.split():
        seen.update((n[:-3], e) for e in split_disposed(git(root, "show", f"{rev}:{rows_rel}/{n}", check=False).stdout))
    return seen


def parse_entry(e: str) -> tuple[str, str, str] | None:
    """(tag, sha, sha256) of a release entry; None when `e` is no release entry to read (not `Y release`, or one
    without `at`, which predates the service); a `Y release … at …` of another shape comes back with the fields it
    lacks empty, so it is refused rather than skipped."""
    w = e.split()
    if w[1:3] != ["Y", "release"] or " at " not in e:
        return None
    g = ENTRY_RE.fullmatch(e)
    return (g["tag"], g["sha"], g["sha256"]) if g else ((w[3] if len(w) > 3 else ""), "", "")


def entries(ctx: Ctx) -> list[tuple[str, str, str, str]]:
    """(row, tag, sha, sha256) for every release entry on the rows main holds, not on main before this push."""
    out = []
    rows = sorted(ctx.rows.glob("*.md"), key=lambda p: (len(p.stem), p.stem)) if ctx.rows.is_dir() else []
    for p in rows:
        for e in split_disposed(p.read_text()):
            parsed = parse_entry(e)
            if parsed is None or (ctx.old is not None and (p.stem, e) in ctx.old):
                continue                           # not a release entry, or on main before this push: an earlier run's
            out.append((p.stem, *parsed))
    return out


# ---- one entry
def want_tag(tag: str, tree: Path) -> tuple[str, str, str]:
    """(kind, craft, the tag VERSION names at `tree`): bundle v + BUNDLE.md's version; core dyad-operator-v +
    dyad/VERSION; craft <craft>-v + its VERSION."""
    m = TAG_RE.fullmatch(tag)
    if not m:
        raise Refused(f"`{tag}` is no release tag (vX.Y.Z, dyad-operator-vX.Y.Z, <craft>-vX.Y.Z)")
    craft = m["craft"]
    if not craft:
        v = re.search(r"^version:[ \t]*(\S+)", (tree / "BUNDLE.md").read_text(), re.M) if (tree / "BUNDLE.md").is_file() else None
        return "bundle", "", f"v{v.group(1) if v else '?'}"
    if craft == dyadlib.CORE_CRAFT:
        return "core", craft, f"{craft}-v{(tree / 'dyad' / 'VERSION').read_text().strip()}"
    vf = tree / "crafts" / craft / "VERSION"
    if not vf.is_file():
        raise Refused(f"no craft `{craft}` at the cut sha")
    return "craft", craft, f"{craft}-v{vf.read_text().strip()}"


def tag_commit(root: Path, tag: str) -> str:
    return git(root, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", check=False).stdout.strip()


def release_exists(ctx: Ctx, tag: str) -> bool:
    return gh("api", f"repos/{ctx.repo}/releases/tags/{tag}", check=False).returncode == 0


def build(ctx: Ctx, tag: str, sha: str, tmp: Path) -> tuple[str, str, list[str]]:
    """The one distribution code path in a worktree at the cut sha, under `tmp`: (kind, sha256, archive files)."""
    tree, out = tmp / "tree", tmp / "out"; out.mkdir()
    git(ctx.root, "worktree", "add", "-q", "--detach", str(tree), sha)
    kind, craft, want = want_tag(tag, tree)
    if want != tag:
        raise Refused(f"tag {tag} != {want} at {sha[:7]} (Rule-11 properties 4, 7)")
    ver = tag.rsplit("v", 1)[-1]
    if kind == "bundle":
        builder(tree, "package.py", "bundle", "build", str(out))
        digest_of = out / "BUNDLE.sha256"
    elif kind == "core":
        digest_of = out / f"dyad-{ver}.tar.gz"
        builder(tree, "package.py", "build", str(digest_of))
    else:
        digest_of = out / f"{craft}-{ver}.tar.gz"
        builder(tree, "craft.py", "export", craft, str(digest_of))
    return kind, hashlib.sha256(digest_of.read_bytes()).hexdigest(), sorted(str(f) for f in out.iterdir())


def run_url(ctx: Ctx) -> str:
    return f"{os.environ.get('GITHUB_SERVER_URL', '')}/{ctx.repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"


def publish(ctx: Ctx, row: str, tag: str, sha: str, want_sha256: str) -> tuple[str, str, str]:
    """One entry: (outcome, postcondition, detail); raises Refused, or anything else as a failure."""
    if not (tag and sha and want_sha256):
        raise Refused("a release entry is `<date> Y release <tag> at <cut sha> (archive <64-hex sha256>)`")
    full = git(ctx.root, "rev-parse", "-q", "--verify", f"{sha}^{{commit}}", check=False).stdout.strip()
    if not full or git(ctx.root, "merge-base", "--is-ancestor", full, "HEAD", check=False).returncode:
        raise Refused(f"cut sha {sha} is not a commit on main")
    at = tag_commit(ctx.root, tag)
    if at and at != full:
        raise Refused(f"tag {tag} exists at {at[:7]}, not {full[:7]}: tags never move")
    if at and release_exists(ctx, tag):
        return "already", "already", f"{tag} at {full[:7]} and its Release exist; nothing done"
    tmp = Path(tempfile.mkdtemp(prefix="dyad-release-"))
    try:
        kind, observed, files = build(ctx, tag, full, tmp)
        if observed != want_sha256:
            raise Refused(f"archive sha256 {observed} != recorded {want_sha256}")
        if not at:
            git(ctx.root, "tag", "-a", tag, full, "-m", f"{tag} (row #{row}; released, d-work #461)")
            git(ctx.root, "push", "origin", f"refs/tags/{tag}")
        note = tmp / f"{tag}.release.json"
        note.write_text(json.dumps({"tag": tag, "row": row, "sha": full, "sha256": observed, "gate": ctx.gate,
                                    "run": run_url(ctx), "service": os.environ.get("GITHUB_SHA", "")}, sort_keys=True) + "\n")
        gh("release", "create", tag, *files, str(note), "--repo", ctx.repo, "--verify-tag", "--title", tag,
           "--notes", f"dyad {kind} {tag}: row #{row}, cut {full[:7]}, sha256 {observed} (released, d-work #461)")
        return "released", "ok", f"{tag} at {full[:7]}: {'tag created' if not at else 'tag existed'}, Release created, sha256 {observed}"
    finally:
        git(ctx.root, "worktree", "remove", "--force", str(tmp / "tree"), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
        git(ctx.root, "worktree", "prune", check=False)


def pending(ctx: Ctx) -> list[str]:
    """Entries the publishing job has work for: added by this push (or named by a dispatch) and not already tagged at
    their cut sha with a Release."""
    out = []
    for _, tag, sha, _ in entries(ctx):
        if ctx.only and tag != ctx.only:
            continue
        full = git(ctx.root, "rev-parse", "-q", "--verify", f"{sha}^{{commit}}", check=False).stdout.strip() if sha else ""
        if full and tag_commit(ctx.root, tag) == full and release_exists(ctx, tag):
            continue
        out.append(tag)
    return out


def main(a: list[str] | None = None, root: Path | None = None) -> int:
    a = sys.argv[1:] if a is None else list(a)
    if [x for x in a if x != "--scan"]:
        print("usage: dyad release [--scan]", file=sys.stderr)
        return 2
    ctx = context(Path(root) if root else dyadlib.repo_root())
    if not ctx.repo and entries(ctx):
        # the hosting is asked whether each tag's Release exists; with no `owner/name` every answer is "no", so a hand
        # run would report every recorded release as pending, or try to publish it (#470, distribute's finding)
        print("refused: GITHUB_REPOSITORY (owner/name) is unset, so no Release can be looked up; set it to run by hand",
              file=sys.stderr)
        return 2
    if "--scan" in a:   # read-only: nothing is built, tagged or written but GITHUB_OUTPUT
        p = pending(ctx)
        print(f"pending: {' '.join(p) or 'none'}")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"pending={'true' if p else 'false'}\n")
        return 0
    seen, bad = [], 0
    for row, tag, sha, want_sha256 in entries(ctx):
        if ctx.only and tag != ctx.only:
            continue
        try:
            outcome, _, detail = publish(ctx, row, tag, sha, want_sha256)
        except Refused as e:
            outcome, detail = "refused", str(e); bad += 1
        except Exception as e:
            outcome, detail = "failed", str(e)[-300:]; bad += 1
        seen.append((tag, row, outcome, detail))
        print(json.dumps({"tag": tag, "row": row, "outcome": outcome, "detail": detail}, sort_keys=True))
    if ctx.only and not seen:
        print(f"no release entry names {ctx.only}"); bad += 1
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as s:
            s.write("| tag | row | outcome | detail |\n|---|---|---|---|\n")
            s.writelines(f"| {t} | {r} | {o} | {d} |\n" for t, r, o, d in seen)
    print(f"{len(seen)} release entries")
    return 1 if bad else 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main())
