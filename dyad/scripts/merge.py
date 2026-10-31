#!/usr/bin/env python3
"""`dyad merge <pr> --head <sha>` (d-work #532, revision 5). Kernel: Python 3.12+, git.

A seat merges a PR itself, on the record alone, when the Operator's Done-`Y` that names it is already on `main`:

  dyad merge <pr> --head <sha>
                          fetch `origin/main`; act only when, on it, some row's operative `Y done` (the row's last;
                          a later one voids an earlier, Rule-2 Binding) names `PR #<pr> at <sha>`, `<sha>` written
                          in full; when the PR's live head (`git ls-remote origin refs/pull/<pr>/head`) is `<sha>`;
                          and when `<sha>` is not yet an ancestor of `origin/main`. Then `git merge --no-ff <sha>`
                          onto `origin/main` in the tool-owned worktree, the message citing the PR, the row and the
                          entry, and one push to `main` through the pre-push gate — the local merge path Rule-14
                          property 3 sanctions, clerical execution of the recorded `Y` (Rule-2). One line out: the
                          merge and the entry that authorized it, or `refused: <reason>`.

Why a verb and not a message: the record on `main` holds the Operator's words (Rule-7), and an allow rule the Operator
commits names this verb, so the harness that runs it is pointed at that record by the Operator and by nothing an agent
says (plan #532, revision 5, R3). The verb therefore reads nothing but `origin/main` and the PR's live head, both
re-read on every try.

The worktree and its lock are `dyad dwork land`'s (`land.py`: `<git common dir>/dyad-land`, one land or merge at a time
per clone), so a merge never touches the caller's checkout. A push refused because `main` moved is re-read and
re-checked from the start once (a race: another seat landed something), never rebased; any other refusal stops with
nothing pushed. The rows fence admits the merge commit: it judges only first-parent non-merge commits (`rows.py`), and
the PR's own commits were gated when the PR was pushed.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("merge.py: Python 3.12+ required")
import re
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

land = dyadlib.load_module(Path(__file__).resolve().parent / "land.py", "land")
Refused = land.Refused
TRIES = 2                                   # the first try and one re-read after a push race (plan #532)
FULL_SHA = re.compile(r"[0-9a-f]{40}")
USAGE = "usage: dyad merge <pr> --head <full sha>"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("one-retry-after-a-race", lambda: TRIES == 2),
    ("full-sha-is-forty-hex", lambda: bool(FULL_SHA.fullmatch("a" * 40)) and not FULL_SHA.fullmatch("a" * 39)),
]


def parse(argv: list[str]) -> tuple[int, str]:
    """(pr, sha) from `<pr> --head <sha>`; Refused on anything else."""
    a = list(argv)
    if len(a) != 3 or a[1] != "--head" or not a[0].isdigit() or not FULL_SHA.fullmatch(a[2]):
        raise Refused(USAGE)
    return int(a[0]), a[2]


def authorizing(rows, pr: int, sha: str) -> tuple[int, str]:
    """(row id, entry): the operative `Y done` on `rows` that names `PR #<pr> at <sha>` in full. Refused naming why
    not: no operative entry names the PR, or the one that does names another head (a void or a stale `Y`)."""
    rg = dyadlib.load_guard("agent", "rows")
    named = [h for h in rg.named_heads(rows) if h[1] == str(pr)]
    hit = [h for h in named if h[2] == sha]
    if hit:
        return hit[0][0], hit[0][3]
    if named:
        rid, _, head, entry = named[0]
        raise Refused(f"row #{rid}'s operative Y done names PR #{pr} at {head}, not {sha}: {entry!r}")
    raise Refused(f"no operative Y done on origin/main names PR #{pr} (a Done-Y is recorded before its merge, Rule-3)")


def live_head(repo: Path, pr: int) -> str:
    r = land.git(repo, "ls-remote", "origin", f"refs/pull/{pr}/head", timeout=land.NETWORK_TIMEOUT)
    return (r.stdout.split() or [""])[0]


def attempt(repo: Path, wt: Path, pr: int, sha: str) -> tuple[str, str, int, str] | None:
    """One try: read, check, merge, push. (merge sha, base, row, entry) on success; None when the push lost a race
    to `main` (the caller re-reads); Refused otherwise."""
    base = land.fetch(repo)
    rid, entry = authorizing(dyadlib.read_rows(repo, at=base), pr, sha)
    live = live_head(repo, pr)
    if live != sha:
        raise Refused(f"PR #{pr}'s live head is {live or 'absent'}, not {sha}: a moved head voids the Y (Rule-2 Binding)")
    land.git(repo, "fetch", "-q", "origin", f"refs/pull/{pr}/head", timeout=land.NETWORK_TIMEOUT)
    if land.git(repo, "merge-base", "--is-ancestor", sha, base, check=False).returncode == 0:
        raise Refused(f"{sha} is already on origin/main: PR #{pr} has landed")
    land.prepare(repo, wt, base)
    msg = (f"Merge PR #{pr} at {sha}\n\nExecuted by `dyad merge` on the Done-Y recorded on main: row #{rid}, "
           f"{entry!r} (Rule-2 Binding, clerical execution; Rule-14 property 3; #532)")
    m = land.git(wt, "merge", "-q", "--no-ff", "-m", msg, sha, check=False)
    if m.returncode:
        land.git(wt, "merge", "--abort", check=False)
        raise Refused(f"PR #{pr} at {sha} does not merge cleanly onto origin/main {base[:12]}: "
                      f"{(m.stdout + m.stderr).strip().splitlines()[-1:] or ['conflict']}")
    head = land.out(wt, "rev-parse", "HEAD")
    p = land.git(wt, "push", "--porcelain", "origin", "HEAD:refs/heads/main", check=False, timeout=land.NETWORK_TIMEOUT)
    if p.returncode == 0:
        return head, base, rid, entry
    if land.fetch(repo) != base:          # main moved under the push: a race, re-read and re-checked by the caller
        return None
    raise Refused(f"the push failed with main unmoved; nothing landed:\n{(p.stdout + p.stderr).strip()}")


def merge(repo: Path, pr: int, sha: str) -> str:
    common = Path(land.out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / land.WORKTREE
    with land.locked(common):
        for n in range(TRIES):
            got = attempt(repo, wt, pr, sha)
            if got:
                head, base, rid, entry = got
                return (f"merged PR #{pr} at {sha} onto main {base[:12]} as {head}: authorized by row #{rid} "
                        f"{entry!r}")
        raise Refused(f"main moved under the push {TRIES} times: nothing landed; run it again")


def main(argv, repo: Path) -> int:
    a = list(argv)
    if a and a[0] in ("-h", "--help"):
        print(__doc__); return 0
    try:
        pr, sha = parse(a)
        print(merge(Path(repo), pr, sha))
        return 0
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2 if str(e) == USAGE else 1


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], dyadlib.repo_root()))
