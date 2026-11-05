#!/usr/bin/env python3
"""`dyad steps <name>` — the d-work run-book's harvested steps (d-work #556, revision 3). Kernel: Python 3.12+, git.

Each step is a recurring script a seat used to re-author by hand, with different parameters each time (plan #556 P3:
69 hand-written runs of the first, 391 of the last, in one session), now one parameterized, idempotent command. Each
takes its parameters from the environment, as every run-book step does, and is run by name — through
`dyad runbook run d-work <step>`, which records an event, or directly. The automaton (`dyad automaton`, #556 PR 2)
calls the same functions.

  dyad steps verify-prs       PRS="582 583 584": each PR's live head (`refs/pull/<n>/head`), its files and zones against
                              origin/main, whether each head is stacked on the one before, and every head merged in
                              order onto origin/main with `git merge-tree` (no worktree touched). Read-only. Exit 1 when
                              a head is missing or a merge in the sequence conflicts.
  dyad steps done-record      DWORK, PRS, SAID (the operator's words, a file) [ACCRETED="547 551"] [--land]: the Done-Y
                              entry composed from the PRs' live heads — `Y done (accreted #c, merges PR #a at <head-a>, …)`
                              — recorded on the row with the state left as it is, and its trace (Rule-3's record act).
                              Without --land it writes the checkout's files, as the run-book's `record` step does;
                              with --land one ledger-only batch carries both. Refuses when the row's operative Y done is
                              already that entry.
  dyad steps close-landed     DWORK [--land]: when every head the row's operative Y done names is on origin/main, the
                              row is set `done`, every row the entry names as accreted (`accreted #c` or
                              `mandate rows #c`) is closed under it (`--mandate`), and — under --land — its board entry
                              is dropped; every row it names under `retires #r` that is backlog or done is archived
                              on its words (`dwork state <r> archived --retired-by <id>`, #574), any other named row
                              printed `not archived: …`. Refuses while a named head is not yet on main.
  dyad steps sync-mirror      MIRROR=<branch>: fast-forward the branch to origin/main; never a force push.

Every step fetches `origin/main` first and reads the ledger there (`dyadlib.read_rows(at=…)`), never the checkout's,
so a stale checkout cannot misjudge a merge. One line out per fact; `refused: <reason>` on stderr, exit 1.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("steps.py: Python 3.12+ required")
import datetime, os, re, shlex, subprocess, tempfile
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

land = dyadlib.load_module(Path(__file__).resolve().parent / "land.py", "land")
Refused = land.Refused
STEPS = ("verify-prs", "done-record", "close-landed", "sync-mirror")
ACCRETED = re.compile(r"\b(?:accreted|mandate rows) (#\d+(?:, #\d+)*)")
FULL_SHA = re.compile(r"[0-9a-f]{40}")
CLI_FLAGS = dyadlib.cli_forms("steps", STEPS)   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
USAGE = "usage: dyad steps verify-prs|done-record|close-landed|sync-mirror [--land] (parameters from the environment)"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("four-steps", lambda: STEPS == ("verify-prs", "done-record", "close-landed", "sync-mirror")),
    ("retires-clause-parses", lambda: retired_rows("Y done (accreted #9, retires #262, #263, merges PR #1 at a)") == [262, 263]
                                    and retired_rows("Y done (merges PR #1 at a)") == []),
    ("accreted-clause-parses", lambda: ACCRETED.search("Y done (accreted #547, #551, merges PR #1 at a)").group(1) == "#547, #551"
                                     and ACCRETED.search("Y done (mandate rows #304, #314, merges PR #2 at b)").group(1) == "#304, #314"),
]


# ---- reading
def rows_guard():
    return dyadlib.load_guard("agent", "rows")


def env(name: str, required: bool = True) -> str | None:
    v = (os.environ.get(name) or "").strip()
    if required and not v:
        raise Refused(f"{name} is not set ({USAGE})")
    return v or None


def prs_of(text: str) -> list[int]:
    nums = text.replace(",", " ").replace("#", " ").split()
    if not nums or not all(n.isdigit() for n in nums):
        raise Refused(f"PRS must be PR numbers, space-separated, not {text!r}")
    return [int(n) for n in nums]


def live_head(repo: Path, pr: int) -> str | None:
    r = land.git(repo, "ls-remote", "origin", f"refs/pull/{pr}/head", check=False, timeout=land.NETWORK_TIMEOUT)
    sha = (r.stdout.split() or [""])[0]
    return sha if FULL_SHA.fullmatch(sha) else None


def fetch_head(repo: Path, pr: int) -> None:
    land.git(repo, "fetch", "-q", "origin", f"refs/pull/{pr}/head", timeout=land.NETWORK_TIMEOUT)


def row_at(repo: Path, base: str, rid: int):
    r = next((r for r in dyadlib.read_rows(repo, at=base) if r.id == rid), None)
    if r is None:
        raise Refused(f"no row #{rid} on origin/main")
    return r


def ancestor(repo: Path, sha: str, of: str) -> bool:
    return land.git(repo, "merge-base", "--is-ancestor", sha, of, check=False).returncode == 0


def zone_of(repo: Path, paths: list[str]) -> list[str]:
    try:
        cz = dyadlib.load_guard("infra", "containment")
        return sorted({cz.classify(p, repo) for p in paths})
    except Exception:
        return []


# ---- the steps
def verify_prs(repo: Path, prs: list[int]) -> list[str]:
    """Lines describing each PR and the sequential merge; Refused on a missing head or a conflict."""
    base = land.fetch(repo)
    out, heads, problems = [f"origin/main {base[:12]}"], [], []
    for pr in prs:
        head = live_head(repo, pr)
        if head is None:
            problems.append(f"PR #{pr}: no live head (refs/pull/{pr}/head)")
            continue
        fetch_head(repo, pr)
        files = land.out(repo, "diff", "--name-only", "--no-renames", f"{base}...{head}").split()
        zones = zone_of(repo, files)
        stacked = f"; stacked on PR #{heads[-1][0]}" if heads and ancestor(repo, heads[-1][1], head) else ""
        landed = "; already on main" if ancestor(repo, head, base) else ""
        out.append(f"PR #{pr} at {head}: {len(files)} file(s){' in ' + ', '.join(zones) if zones else ''}{stacked}{landed}")
        heads.append((pr, head))
    cur = base
    for pr, head in heads:
        if ancestor(repo, head, cur):
            out.append(f"merge-tree: PR #{pr} adds nothing onto {cur[:12]}")
            continue
        r = land.git(repo, "merge-tree", "--write-tree", "--name-only", cur, head, check=False)
        if r.returncode:
            problems.append(f"merge-tree: PR #{pr} conflicts onto {cur[:12]}: {', '.join(r.stdout.split()[1:6]) or 'conflict'}")
            break
        tree = r.stdout.split()[0]
        cur = land.out(repo, "commit-tree", tree, "-p", cur, "-p", head, "-m", f"verify-prs: PR #{pr}")
        out.append(f"merge-tree: PR #{pr} merges cleanly in order (tree {tree[:12]})")
    if problems:
        raise Refused("\n".join(out + problems))
    return out


def done_entry(repo: Path, prs: list[int], accreted: list[int]) -> str:
    parts = []
    if accreted:
        parts.append("accreted " + ", ".join(f"#{a}" for a in accreted))
    heads = []
    for pr in prs:
        h = live_head(repo, pr)
        if h is None:
            raise Refused(f"PR #{pr} has no live head; the Done-Y names a head, so there is nothing to record")
        heads.append(f"PR #{pr} at {h}")
    if heads:
        parts.append("merges " + ", ".join(heads))
    return "Y done" + (f" ({', '.join(parts)})" if parts else "")


def runner(repo: Path, *argv: str) -> subprocess.CompletedProcess:
    """This checkout's own runner (`dyad/scripts/package.py`), as `dyad/bin/dyad` execs it."""
    return subprocess.run([sys.executable, str(repo / "dyad" / "scripts" / "package.py"), *argv], cwd=repo,
                          capture_output=True, text=True, env={**land.env()})


def run_or_refuse(repo: Path, *argv: str) -> str:
    r = runner(repo, *argv)
    if r.returncode:
        raise Refused(f"dyad {' '.join(argv[:3])} refused:\n{(r.stdout + r.stderr).strip()}")
    return r.stdout.strip()


def batch(repo: Path, lines: list[str]) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".batch", delete=False) as f:
        f.write("\n".join(lines) + "\n")
    try:
        return run_or_refuse(repo, "dwork", "batch", f.name, "--land")
    finally:
        os.unlink(f.name)


def done_record(repo: Path, rid: int, prs: list[int], said: Path, accreted: list[int], landing: bool) -> list[str]:
    base = land.fetch(repo)
    row = row_at(repo, base, rid)
    if row.state in dyadlib.TERMINAL_STATES:
        raise Refused(f"row #{rid} is {row.state}")
    entry = done_entry(repo, prs, accreted)
    if rows_guard().operative_done(row.disposed) and rows_guard().operative_done(row.disposed).split(" ", 1)[1] == entry:
        raise Refused(f"already recorded: row #{rid}'s operative entry is {entry!r}")
    if not said.is_file():
        raise Refused(f"SAID {said} is not a file (the operator's words, verbatim, Rule-7)")
    trace = dyadlib.instance(repo) / "d-work" / "traces" / f"{rid}.md"
    run_or_refuse(repo, "dwork", "trace", str(rid), "--out", "--said-file", str(said))   # #592 R-b: through the Done words
    if landing:
        rel = trace.relative_to(repo).as_posix()
        out = batch(repo, [f"land {shlex.quote(rel)}",
                           f"state {rid} {row.state} -d {shlex.quote(entry)} --said-file {shlex.quote(str(said))}"])
    else:
        out = run_or_refuse(repo, "dwork", "state", str(rid), row.state, "-d", entry, "--said-file", str(said))
    return [f"row #{rid}: {entry}", out]


RETIRES = re.compile(r"\bretires (#\d+(?:, #\d+)*)")   # #574 revision 3, as package.RETIRES
NOT_ARCHIVED = "not archived: "

def retired_rows(entry: str) -> list[int]:
    m = RETIRES.search(entry or "")
    return [int(x) for x in re.findall(r"#(\d+)", m.group(1))] if m else []


def mandate_rows(entry: str) -> list[int]:
    m = ACCRETED.search(entry)
    return [int(x) for x in re.findall(r"#(\d+)", m.group(1))] if m else []


def close_landed(repo: Path, rid: int, landing: bool) -> list[str]:
    base = land.fetch(repo)
    rows = {r.id: r for r in dyadlib.read_rows(repo, at=base)}
    row = rows.get(rid)
    if row is None:
        raise Refused(f"no row #{rid} on origin/main")
    if row.state in dyadlib.TERMINAL_STATES:
        raise Refused(f"already closed: row #{rid} is {row.state}")
    entry = rows_guard().operative_done(row.disposed)
    if entry is None:
        raise Refused(f"row #{rid}'s last disposition is no Y done: nothing to close on")
    heads = [h for _, _, h, _ in rows_guard().named_heads([row])]
    owed = [h for h in heads if not ancestor(repo, h, base)]
    if owed:
        raise Refused(f"row #{rid}: {', '.join(h[:12] for h in owed)} not yet on origin/main {base[:12]}; the state follows the merge (Rule-3)")
    children = [c for c in mandate_rows(entry) if c in rows and rows[c].state not in dyadlib.TERMINAL_STATES]
    cmds = [["state", str(rid), "done"]] + [["state", str(c), "done", "--mandate", str(rid)] for c in children]
    out = [f"row #{rid}: every named head is on origin/main {base[:12]} ({len(heads)})"]
    # #574 G5: the rows the Done retires, archived on its words; any other is refused, never resolved here
    for r in retired_rows(entry):
        st = rows[r].state if r in rows else None
        if st in ("backlog", "done") or r in children:   # an accreted row this batch closes is done when its line runs
            cmds.append(["state", str(r), "archived", "--retired-by", str(rid)])
        elif st != "archived":
            out.append(f"{NOT_ARCHIVED}row #{r} is {st or 'no row'}; row #{rid}'s Done retires only a backlog or done row (#574 G2)")
    if landing:
        out.append(batch(repo, [" ".join(shlex.quote(a) for a in c) for c in cmds]))
        board = dyadlib.instance(repo) / "d-work" / "board" / f"{rid}.md"
        if land.git(repo, "cat-file", "-e", f"origin/main:{board.relative_to(repo).as_posix()}", check=False).returncode == 0:
            out.append(run_or_refuse(repo, "board", "set", str(rid), "--drop"))
    else:
        for c in cmds:
            out.append(run_or_refuse(repo, "dwork", *c))
        out.append(f"then: dyad board set {rid} --drop (a board write always lands)")
    return out


def sync_mirror(repo: Path, branch: str) -> list[str]:
    base = land.fetch(repo)
    r = land.git(repo, "ls-remote", "origin", f"refs/heads/{branch}", check=False, timeout=land.NETWORK_TIMEOUT)
    old = (r.stdout.split() or [""])[0]
    if old == base:
        raise Refused(f"already: {branch} is origin/main {base[:12]}")
    if old and not ancestor(repo, old, base):
        land.git(repo, "fetch", "-q", "origin", f"refs/heads/{branch}", check=False, timeout=land.NETWORK_TIMEOUT)
        if not ancestor(repo, old, base):
            raise Refused(f"{branch} at {old[:12]} is not behind origin/main {base[:12]}: it holds work main lacks; never forced")
    p = land.git(repo, "push", "-q", "origin", f"{base}:refs/heads/{branch}", check=False, timeout=land.NETWORK_TIMEOUT)
    if p.returncode:
        raise Refused(f"the push of {branch} failed:\n{(p.stdout + p.stderr).strip()}")
    return [f"{branch}: {old[:12] or 'absent'} -> {base[:12]} (MIRROR_WAS={old or 'absent'})"]


def main(argv: list[str], repo: Path) -> int:
    a = list(argv)
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return 0 if a else 2
    name, flags = a[0], set(a[1:])
    try:
        if name not in STEPS or flags - set(CLI_FLAGS[name].flags):
            raise Refused(USAGE)
        repo = Path(repo)
        if name == "verify-prs":
            lines = verify_prs(repo, prs_of(env("PRS")))
        elif name == "done-record":
            acc = prs_of(env("ACCRETED")) if env("ACCRETED", required=False) else []
            lines = done_record(repo, int(env("DWORK")), prs_of(env("PRS")) if env("PRS", required=False) else [],
                                Path(env("SAID")), acc, "--land" in flags)
        elif name == "close-landed":
            lines = close_landed(repo, int(env("DWORK")), "--land" in flags)
        else:
            lines = sync_mirror(repo, env("MIRROR"))
        print("\n".join(l for l in lines if l))
        return 0
    except ValueError:
        print(f"refused: DWORK must be a row id ({USAGE})", file=sys.stderr)
        return 1
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2 if str(e) == USAGE else 1


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], dyadlib.repo_root()))
