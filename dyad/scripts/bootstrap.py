#!/usr/bin/env python3
"""`dyad bootstrap [--check]`: make a clone fit to evidence and push from (d-work #474, child C1 of mandate #473).
Kernel: Python 3.12+, git. Run from a seat's container start (a SessionStart hook or the environment's set-up
script) and by hand; idempotent, and never blocking: every step prints one line and the verb exits 0 whatever git or
the network answers, so a session always starts. Exit 2 only on misuse (an unknown argument).

  dyad bootstrap           (a) `git config core.hooksPath dyad/hooks` when it is not already (Rule-1: the hooks are the
                           only blocking enforcement before a push); (b) a shallow clone is unshallowed and its tags
                           fetched, `git fetch --unshallow --tags origin`; (c) a full clone fetches tags,
                           `git fetch --tags origin`, only when the core release tag `BUNDLE.md` names
                           (`dyad-operator-v<row version>`) is not here — an older core tag does not stand in for it
  dyad bootstrap --check   read-only: the same three lines, nothing set and nothing fetched

Each line is `<state> [bootstrap] <step>: <detail>`, the state `ok` (nothing to do), `changed` (done now) or `warn`
(not done: the network, a missing remote, git's refusal — or, under `--check`, what a run would do).

Why both repairs: a shallow or tagless clone yields false FAILs — `infra/bundle` reads release tags (Rule-11 property
4's drift check) and Rule-20's `plan.base->commit` resolves base commits a shallow history lacks — so `check
--evidence` refuses one (`clone_problems`, the one test both share). The tag tested is the one the row names, not any
core tag: the bundle guard fails a row naming a version with no local tag, so a clone holding older core tags but not
the row's own read red in `infra/bundle` (d-work #505; the live case held tags below `dyad-operator-v0.13.0`). Why tags are fetched only when missing: the suite
memo keys on a digest of `refs/tags` (Rule-12 property 2), so a fetch that brings a new tag between an evidence run and
its push re-runs the whole suite at the push; this verb runs at container start, before any evidence, and on a warm
clone touches no network at all, while a plain `git fetch` already follows the tags that point into what it fetches.

When is a core release tag expected: when `BUNDLE.md` (Rule-11 property 7; the authoring repo's, never an install's)
has a `dyad-operator` row, since a row is added by a release; the tag expected is `dyad-operator-v<row version>`. An installed system carries no `BUNDLE.md` and a fresh
scratch repo no row, so neither is ever refused for having no tag; no network is read to decide it.

Every git child runs under `dyadlib.git_env()` (a hook's GIT_VARS dropped, #142) with `GIT_TERMINAL_PROMPT=0`, so a
fetch that would ask for credentials fails at once instead of hanging a session's start.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("bootstrap.py: Python 3.12+ required")
import subprocess
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HOOKS_PATH = "dyad/hooks"                       # Rule-1 Enforcement: `git config core.hooksPath dyad/hooks`
REMOTE = "origin"
CORE_TAGS = f"{dyadlib.CORE_CRAFT}-v*"          # Rule-11 property 4: every core release tag, `dyad-operator-vX.Y.Z`
STATES = ("ok", "changed", "warn")
FETCH_TIMEOUT = 600                             # an unshallow of a long history; a SessionStart hook has its own bound
UNSHALLOW = ("fetch", "--unshallow", "--tags", REMOTE)
FETCH_TAGS = ("fetch", "--tags", REMOTE)
REMEDY = "run ./dyad/bin/dyad bootstrap"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("states-are-ok-changed-warn", lambda: STATES == ("ok", "changed", "warn")),
    ("core-tag-pattern-is-the-core-release-prefix", lambda: CORE_TAGS == "dyad-operator-v*"),
    ("unshallow-also-fetches-tags", lambda: "--unshallow" in UNSHALLOW and "--tags" in UNSHALLOW and UNSHALLOW[-1] == REMOTE),
    ("fetches-name-one-remote", lambda: FETCH_TAGS[-1] == UNSHALLOW[-1] == REMOTE),
    ("expected-tag-is-the-core-prefix-and-the-row-version", lambda: core_tag("1.2.3") == "dyad-operator-v1.2.3"
                                                               and core_tag("1.2.3").startswith(CORE_TAGS[:-1])),
]


def git(repo: Path, *a: str, timeout: int = 60) -> subprocess.CompletedProcess | None:
    """One git child in `repo`; None when it could not run at all (no git, a timeout)."""
    try:
        return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, timeout=timeout,
                              env={**dyadlib.git_env(), "GIT_TERMINAL_PROMPT": "0"})
    except (OSError, subprocess.SubprocessError):
        return None


def _out(r) -> str | None:
    return r.stdout.strip() if r is not None and r.returncode == 0 else None


def _last(r) -> str:
    if r is None:
        return "git did not run"
    return (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or [f"exit {r.returncode}"])[-1]


def is_shallow(repo: Path) -> bool:
    return _out(git(repo, "rev-parse", "--is-shallow-repository")) == "true"


def core_tags(repo: Path) -> list[str]:
    return (_out(git(repo, "tag", "-l", CORE_TAGS)) or "").split()


def core_tag(version: str) -> str:
    """The core release tag of one version (Rule-11 property 4): `dyad-operator-v<version>`."""
    return f"{dyadlib.CORE_CRAFT}-v{version}"


def has_tag(repo: Path, tag: str) -> bool:
    return _out(git(repo, "rev-parse", "--verify", "-q", f"refs/tags/{tag}")) is not None


def expected_core_release(repo: Path) -> str | None:
    """The core version `BUNDLE.md` names, or None when it names none (no file, no `dyad-operator` row): a row is
    added by a release (Rule-11 property 7), so a row means a core release tag exists upstream. Parsed by the bundle
    guard's own parser, never a second one (Rule-13)."""
    path = repo / "BUNDLE.md"
    if not path.is_file():
        return None
    try:
        _, rows = dyadlib.load_guard("infra", "bundle").parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None
    return next((v for c, v in rows if c == dyadlib.CORE_CRAFT), None)


def clone_problems(repo: Path) -> list[str]:
    """What makes this clone unfit to evidence, one line each, local reads only (no network): a shallow history,
    and the missing tag `dyad-operator-v<version>` while `BUNDLE.md` names that core release — older core tags do
    not stand in for it (d-work #505). `check --evidence` refuses on the first."""
    out = []
    if is_shallow(repo):
        out.append(f"shallow clone: {REMEDY} (git fetch --unshallow --tags)")
    expected = expected_core_release(repo)
    if expected and not has_tag(repo, core_tag(expected)):
        out.append(f"no {core_tag(expected)} tag while BUNDLE.md names {dyadlib.CORE_CRAFT} {expected}: "
                   f"{REMEDY} (git fetch --tags)")
    return out


def line(state: str, step: str, detail: str) -> str:
    return f"{state:<4} [bootstrap] {step}: {detail}"


def step_hooks(repo: Path, check: bool) -> str:
    have = _out(git(repo, "config", "--get", "core.hooksPath"))
    if have == HOOKS_PATH:
        return line("ok", "hooksPath", HOOKS_PATH)
    if not (repo / HOOKS_PATH).is_dir():
        return line("warn", "hooksPath", f"no {HOOKS_PATH}/ in this tree; left {have or 'unset'}")
    if check:
        return line("warn", "hooksPath", f"{have or 'unset'}, want {HOOKS_PATH}")
    r = git(repo, "config", "core.hooksPath", HOOKS_PATH)
    if r is None or r.returncode:
        return line("warn", "hooksPath", f"git config failed: {_last(r)}")
    return line("changed", "hooksPath", f"{have or 'unset'} -> {HOOKS_PATH}")


def _has_remote(repo: Path) -> bool:
    return _out(git(repo, "remote", "get-url", REMOTE)) is not None


def step_history(repo: Path, check: bool) -> str:
    if not is_shallow(repo):
        return line("ok", "history", "full clone")
    if check:
        return line("warn", "history", f"shallow clone; a run would `git {' '.join(UNSHALLOW)}`")
    if not _has_remote(repo):
        return line("warn", "history", f"shallow clone and no {REMOTE} remote; nothing fetched")
    r = git(repo, *UNSHALLOW, timeout=FETCH_TIMEOUT)
    if r is None or r.returncode:
        return line("warn", "history", f"git {' '.join(UNSHALLOW)} failed: {_last(r)}")
    return line("changed", "history", f"unshallowed, tags fetched (git {' '.join(UNSHALLOW)})")


def step_tags(repo: Path, check: bool) -> str:
    expected = expected_core_release(repo)
    if not expected:
        have = core_tags(repo)
        if not have:
            return line("ok", "tags", f"no {CORE_TAGS} tag, none expected (BUNDLE.md names no {dyadlib.CORE_CRAFT} row)")
        return line("ok", "tags", f"{len(have)} {CORE_TAGS} tag(s), none expected "
                                  f"(BUNDLE.md names no {dyadlib.CORE_CRAFT} row)")
    tag = core_tag(expected)
    if has_tag(repo, tag):
        return line("ok", "tags", f"{tag} (BUNDLE.md names {dyadlib.CORE_CRAFT} {expected})")
    if check:
        return line("warn", "tags", f"no {tag} tag while BUNDLE.md names {dyadlib.CORE_CRAFT} {expected}; "
                                    f"a run would `git {' '.join(FETCH_TAGS)}`")
    if not _has_remote(repo):
        return line("warn", "tags", f"no {tag} tag and no {REMOTE} remote; nothing fetched")
    r = git(repo, *FETCH_TAGS, timeout=FETCH_TIMEOUT)
    if r is None or r.returncode:
        return line("warn", "tags", f"git {' '.join(FETCH_TAGS)} failed: {_last(r)}")
    if not has_tag(repo, tag):
        return line("warn", "tags", f"fetched, still no {tag} tag on {REMOTE}")
    return line("changed", "tags", f"fetched {tag}; {len(core_tags(repo))} {CORE_TAGS} tag(s)")


def run(repo: Path, check: bool = False) -> list[str]:
    """The three steps in order — hooks, history, tags — each one line; the tags step after the history step, so an
    unshallow that already fetched the tags leaves it `ok`."""
    return [step_hooks(repo, check), step_history(repo, check), step_tags(repo, check)]


def main(argv, repo: Path) -> int:
    a = list(argv)
    if a and a[0] in ("-h", "--help"):
        print(__doc__); return 0
    if any(x != "--check" for x in a):
        print("usage: dyad bootstrap [--check]", file=sys.stderr); return 2
    for l in run(Path(repo), check="--check" in a):
        print(l)
    return 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], dyadlib.repo_root()))
