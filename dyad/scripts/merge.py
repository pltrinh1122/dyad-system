#!/usr/bin/env python3
"""`dyad merge <pr> --head <sha>` (d-work #532, revision 5). Kernel: Python 3.12+, git.

A seat merges a PR itself, on the record alone, when the Operator's Done-`Y` that names it is already on `main`:

  dyad merge <pr> --head <sha>
                          fetch `origin/main`; act only when, on it, some row's operative `Y done` (the row's last
                          disposition, when that is a `Y done`: a later `Y done` voids an earlier, Rule-2 Binding,
                          and a later `N` revokes it, #541) names `PR #<pr> at <sha>`, `<sha>` written
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

`merge_all` merges a cut — every PR one `Y done` names, in its order — in one worktree and one push, so the gate
judges the cut's final tree once and a refusal at any PR pushes nothing (d-work #562 (a)); the automaton calls it.

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
CLI_FLAGS = dyadlib.cli_forms("merge")   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
HEAD_FLAG, = CLI_FLAGS[None].value_flags

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("one-retry-after-a-race", lambda: TRIES == 2),
    ("full-sha-is-forty-hex", lambda: bool(FULL_SHA.fullmatch("a" * 40)) and not FULL_SHA.fullmatch("a" * 39)),
]


def parse(argv: list[str]) -> tuple[int, str]:
    """(pr, sha) from `<pr> --head <sha>`; Refused on anything else."""
    a = list(argv)
    if len(a) != 3 or a[1] != HEAD_FLAG or not a[0].isdigit() or not FULL_SHA.fullmatch(a[2]):
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
    for r in rows:                         # a Y done that names it, revoked by a later disposition (#541, R4)
        es = rg.entries(r.disposed)
        if r.state in dyadlib.TERMINAL_STATES or not es or rg.DONE_Y.search(es[-1]):
            continue
        if any(rg.DONE_Y.search(e) and (str(pr), sha) in rg.PR_AT.findall(e) for e in es):
            raise Refused(f"row #{r.id}'s last disposition is {es[-1]!r}, after the Y done naming PR #{pr}: "
                          f"that Y is no longer operative (#541)")
    raise Refused(f"no operative Y done on origin/main names PR #{pr} (a Done-Y is recorded before its merge, Rule-3)")


def y_binding(named: dict[int, str], pr: int, live: str) -> str:
    """dmc:y-binding (#641): whether a recorded Y binds the merge of PR `pr` whose live head is `live`. `named` maps each
    PR the operative `Y done` names to the head it was given on. `bound` (named in the question) when the PR is named
    and its head is unchanged; `re-prompt` (re-prompts) when a named head changed since the question was asked;
    `fresh-y` (fresh Y) when the PR is new to the question, one created to recover from an error included."""
    if pr not in named:
        return "fresh-y"
    return "bound" if named[pr] == live else "re-prompt"

def live_head(repo: Path, pr: int) -> str:
    r = land.git(repo, "ls-remote", "origin", f"refs/pull/{pr}/head", timeout=land.NETWORK_TIMEOUT)
    return (r.stdout.split() or [""])[0]


def attempt(repo: Path, wt: Path, items: list[tuple[int, str]]):
    """One try over a cut: read, check every PR, merge each in order, push once (d-work #562 (a)). Returns
    ([(pr, sha, merge sha, row, entry)], base) on success; None when the push lost a race to `main` (the caller
    re-reads); Refused otherwise, with nothing pushed: a cut lands whole or not at all."""
    base = land.fetch(repo)
    rows = dyadlib.read_rows(repo, at=base)                # read once per try, not once per PR
    auth = [(pr, sha, *authorizing(rows, pr, sha)) for pr, sha in items]
    for pr, sha, _, _ in auth:
        live = live_head(repo, pr)
        if live != sha:
            raise Refused(f"PR #{pr}'s live head is {live or 'absent'}, not {sha}: a moved head voids the Y (Rule-2 Binding)")
        land.git(repo, "fetch", "-q", "origin", f"refs/pull/{pr}/head", timeout=land.NETWORK_TIMEOUT)
        if land.git(repo, "merge-base", "--is-ancestor", sha, base, check=False).returncode == 0:
            raise Refused(f"{sha} is already on origin/main: PR #{pr} has landed")
    land.prepare(repo, wt, base)
    done = []
    for pr, sha, rid, entry in auth:
        msg = (f"Merge PR #{pr} at {sha}\n\nExecuted by `dyad merge` on the Done-Y recorded on main: row #{rid}, "
               f"{entry!r} (Rule-2 Binding, clerical execution; Rule-14 property 3; #532)")
        m = land.git(wt, "merge", "-q", "--no-ff", "-m", msg, sha, check=False)
        if m.returncode:
            land.git(wt, "merge", "--abort", check=False)
            onto = f"PR #{done[-1][0]}'s merge" if done else f"origin/main {base[:12]}"
            raise Refused(f"PR #{pr} at {sha} does not merge cleanly onto {onto}: "
                          f"{(m.stdout + m.stderr).strip().splitlines()[-1:] or ['conflict']}; nothing pushed")
        done.append((pr, sha, land.out(wt, "rev-parse", "HEAD"), rid, entry))
    p = land.git(wt, "push", "--porcelain", "origin", "HEAD:refs/heads/main", check=False, timeout=land.NETWORK_TIMEOUT)
    if p.returncode == 0:
        return done, base
    if land.fetch(repo) != base:          # main moved under the push: a race, re-read and re-checked by the caller
        return None
    raise Refused(f"the push failed with main unmoved; nothing landed:\n{(p.stdout + p.stderr).strip()}")


def merge_all(repo: Path, items: list[tuple[int, str]]) -> list[str]:
    """Merge a cut — the PRs one operative `Y done` names, in its order — as one push through the gate, so the gate
    judges the cut's final tree once (d-work #562 (a)). One line per PR merged."""
    common = Path(land.out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / land.WORKTREE
    with land.locked(common):
        for n in range(TRIES):
            got = attempt(repo, wt, items)
            if got:
                done, base = got
                prev, out = base, []
                for pr, sha, head, rid, entry in done:
                    out.append(f"merged PR #{pr} at {sha} onto main {prev[:12]} as {head}: authorized by row #{rid} "
                               f"{entry!r}")
                    prev = head
                return out
        raise Refused(f"main moved under the push {TRIES} times: nothing landed; run it again")


def merge(repo: Path, pr: int, sha: str) -> str:
    return merge_all(repo, [(pr, sha)])[0]


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
