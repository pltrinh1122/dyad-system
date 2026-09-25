#!/usr/bin/env python3
"""Zone guard (entity `zone`, infra corpus; Rule-1 owns the check, placed per Rule-11 property 1). Kernel: Python 3.12+.

The ZONES table below is the single source of truth. A transaction (staged index, one commit,
or a PR) passes iff it adds/modifies no unclassified path and every path it touches lies in
ONE zone. Deleting an unclassified path is tolerated so a passing tree can be reached.

Rule-1 binds a commit and a PR; a push range is neither, so the two are separate modes (#166):
`commits` walks each non-merge commit of `base..head` (the pre-push path, `check_transaction`);
`range` walks those commits **and** the whole `base...head` diff, which is the PR (`check_pr`, the
`range` CLI, `dyad check --pr`, and the hosted detector over what landed on `main`). The result
line names the mode that ran.

  containment.py staged               pre-commit: check the index
  containment.py commit <sha>         one commit
  containment.py commits <base> <head> each non-merge commit of a push range
  containment.py range <base> <head>  a PR: each non-merge commit + the whole diff
  containment.py tree                 every tracked file must be classified
  containment.py zones                print the zone table
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("containment.py: Python 3.12+ required")
import fnmatch, subprocess
from collections.abc import Callable
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "zone", "infra", True
NAME, OWNER = "zone", "Rule-1"

# (zone, glob) — first match wins; globs match the whole path. The host row is instance data: its
# path and zone are the preferences `host-path` / `host-zone` of the repo being checked (dyadlib.host_path,
# host_zone; defaults `workstation-corpus` / `workstation`, #175). `infra` folds the host records into the
# infra zone and the system has four zones; the table's order and every other row never change.
ZONE_FIELDS = ("zone", "pattern")
FIELDS = ZONE_FIELDS
HOST_ROW = 2                                          # the index of the host row in every table
ALL_ZONE_NAMES = ("agent", "workstation", "preferences", "infra", "craft")   # the zone set of a default system (Rule-1; `craft` since #154)

def zones_for(host_path: str = dyadlib.DEFAULT_HOST, host_zone: str = dyadlib.DEFAULT_HOST_ZONE) -> list[tuple[str, str]]:
    """The zone table for one host path and zone; the defaults give the five-zone table."""
    return [
        ("agent", "agent-corpus/*"),
        ("agent", "dyad/*"),
        (host_zone, f"{host_path}/*"),
        ("preferences", "preferences-corpus/*"),
        ("craft", "crafts/*"),
        ("infra", ".github/*"),
        ("infra", ".githooks/*"),
        ("infra", "CLAUDE.md"),
        ("infra", "README.md"),
        ("infra", "LICENSE"),                             # a public distribution repo carries one (#192)
        ("infra", ".gitignore"),
        ("infra", "BUNDLE.md"),                           # the bundle manifest (Rule-11 property 7, #196)
        ("infra", ".claude/*"),                           # committed harness adapters: slash commands, skills (#152)
    ]

def zone_names_for(host_zone: str = dyadlib.DEFAULT_HOST_ZONE) -> tuple[str, ...]:
    """The zone set: the five zones, less `workstation` when the host row is in another zone."""
    return tuple(z for z in ALL_ZONE_NAMES if z != "workstation" or host_zone == "workstation")

def table(root: Path | str | None = None) -> list[tuple[str, str]]:
    """The zone table of the repo at `root` (None: this repo's, `ZONES`), read from its preferences."""
    if root is None:
        return ZONES
    return zones_for(dyadlib.host_path(Path(root)), dyadlib.host_zone(Path(root)))

def _live_root() -> Path | None:
    try:
        return dyadlib.repo_root()
    except Exception:                                  # not inside a work tree: the defaults
        return None

_LIVE = _live_root()
ZONES = zones_for(dyadlib.host_path(_LIVE), dyadlib.host_zone(_LIVE)) if _LIVE is not None else zones_for()
ZONE_NAMES = zone_names_for(ZONES[HOST_ROW][0])   # the zone set of this repo (Rule-1)

def corpora(root: Path | str | None = None) -> set[str]:
    """The names a craft guard may declare as CORPUS: every zone of `root`'s table plus the logical
    host corpus (dyadlib.HOST_CORPUS), which names the host's stores whatever zone holds them."""
    return {z for z, _ in table(root)} | {dyadlib.HOST_CORPUS}

def corpus_zone(corpus: str, root: Path | str | None = None) -> str:
    """The zone a guard's CORPUS resolves to: the host row's zone for the logical host corpus, else itself."""
    return table(root)[HOST_ROW][0] if corpus == dyadlib.HOST_CORPUS else corpus

# The two checks over a pair of commits (#166). A push range is not a transaction: the runner's
# transaction hook runs `commits`, its PR hook `range`; both print the name they ran under.
MODES = {"commits": "each non-merge commit of base..head (a push range; Rule-1 binds a commit, not the range)",
         "range": "each non-merge commit and the whole base...head diff (a PR)"}
TRANSACTION_MODE, PR_MODE = "commits", "range"

# The verb the shipped `dyad/hooks/pre-commit` passes: this module's whole contract with the hook,
# named here so `hook-verb-is-a-verb` trips on a rename that forgets the table (#25).
HOOK_VERB = "staged"

def _disjoint(zones=None) -> bool:
    zones = ZONES if zones is None else zones
    pats = [p for _, p in zones]
    if len(set(pats)) != len(pats):
        return False
    return not any(fnmatch.fnmatchcase(p, q) for z, p in zones for y, q in zones if z != y)

_INFRA_HOST = zones_for(dyadlib.DEFAULT_HOST, "infra")   # the four-zone variant, checked beside the live table

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("zone-patterns-disjoint", _disjoint),
    ("every-zone-non-empty", lambda: {z for z, _ in ZONES} == set(ZONE_NAMES)),
    ("zone-names-known", lambda: {z for z, _ in ZONES} <= set(ZONE_NAMES) and len(set(ZONE_NAMES)) == len(ZONE_NAMES)),
    ("default-host-row", lambda: zones_for()[HOST_ROW] == ("workstation", "workstation-corpus/*")),
    ("host-zones-are-zones", lambda: set(dyadlib.HOST_ZONES) <= set(ALL_ZONE_NAMES)),
    ("infra-host-four-zones", lambda: _disjoint(_INFRA_HOST) and {z for z, _ in _INFRA_HOST} == set(zone_names_for("infra")) and len(zone_names_for("infra")) == 4),
    ("modes-declared-and-distinct", lambda: {TRANSACTION_MODE, PR_MODE} <= set(MODES) and TRANSACTION_MODE != PR_MODE),
    ("modes-are-verbs", lambda: set(MODES) <= set(VERBS)),                 # every documented check mode dispatches
    ("hook-verb-is-a-verb", lambda: HOOK_VERB in VERBS),                   # the pre-commit hook's verb still exists
    ("verbs-in-usage", lambda: all(f"containment.py {v}" in (__doc__ or "") for v in VERBS)),   # a verb added without its usage line
]

def classify(path: str, root: Path | str | None = None, zones: list[tuple[str, str]] | None = None) -> str:
    """The zone of `path` in `zones`, else in the table of the repo at `root` (None: this repo's, `ZONES`)."""
    for zone, pat in (zones if zones is not None else table(root)):
        if fnmatch.fnmatchcase(path, pat):
            return zone
    return "unclassified"

def git(*args, cwd=None) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)

def check_paths(label: str, entries: list[tuple[str, str]], root: Path | str | None = None) -> list[str]:
    """entries: (status, path), classified by the table of the repo at `root`. Returns failure messages (empty = pass)."""
    fails, zones, t = [], set(), table(root)
    for status, path in entries:
        if not path:
            continue
        zone = classify(path, zones=t)
        if zone == "unclassified":
            if status.startswith("D"):
                continue
            fails.append(f"FAIL [{label}]: unclassified path: {path}")
            continue
        zones.add(zone)
    if len(zones) > 1:
        fails.append(f"FAIL [{label}]: touches multiple zones: {' '.join(sorted(zones))}")
    return fails

def name_status(*diff_args, cwd=None) -> list[tuple[str, str]]:
    out = git("diff", "--name-status", "--no-renames", *diff_args, cwd=cwd)
    return [tuple(line.split("\t", 1)) for line in out.splitlines() if "\t" in line]

def check_staged(cwd=None): return check_paths("staged", name_status("--cached", cwd=cwd), cwd)
def check_commit(sha, cwd=None):
    out = git("diff-tree", "--root", "--no-commit-id", "-r", "--name-status", "--no-renames", sha, cwd=cwd)
    return check_paths(f"commit {sha[:7]}", [tuple(l.split("\t", 1)) for l in out.splitlines() if "\t" in l], cwd)
def check_commits(base, head, cwd=None):
    """Mode `commits`: each non-merge commit of `base..head`, nothing about the range itself (#166)."""
    fails = []
    for sha in git("rev-list", "--no-merges", f"{base}..{head}", cwd=cwd).split():
        fails += check_commit(sha, cwd=cwd)
    return fails
def check_range(base, head, cwd=None):
    """Mode `range`: the commits **and** the whole `base...head` diff — the PR transaction."""
    return check_commits(base, head, cwd=cwd) + check_paths(f"range {base[:7]}..{head[:7]}", name_status(f"{base}...{head}", cwd=cwd), cwd)
def check_tree(cwd=None):
    t = table(cwd)
    return [f"FAIL [tree]: unclassified path: {p}" for p in git("ls-files", cwd=cwd).split() if classify(p, zones=t) == "unclassified"]

def print_zones(args: list[str]) -> None:
    """The `zones` verb: prints the table Rule-1 sends a reader to, and returns no fails list."""
    print("zone         pattern")
    for z, p in ZONES:
        print(f"{z:<12} {p}")

# Every CLI verb, declared (#25). A handler takes the argv tail and returns the fails list, or
# `None` when it printed its own output and there is nothing to summarise (`zones`). Lifting this
# out of `main` is what lets the three invariants above see it.
VERBS: dict[str, Callable[[list[str]], list[str] | None]] = {
    "staged":  lambda args: check_staged(),
    "commit":  lambda args: check_commit(args[0]),
    "commits": lambda args: check_commits(args[0], args[1]),
    "range":   lambda args: check_range(args[0], args[1]),
    "tree":    lambda args: check_tree(),
    "zones":   print_zones,
}

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Every tracked file of `root` is classified (the `tree` mode)."""
    return [f[5:] if f.startswith("FAIL ") else f for f in check_tree(cwd=root or dyadlib.repo_root())]

def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """The push path (pre-push, `dyad check --guards`): each non-merge commit of `base..head` stays
    in one zone (mode `commits`). The range itself is not a transaction — Rule-1 binds a commit and
    a PR — so several single-zone commits spanning zones are a correct push (#166, found in #155)."""
    return check_commits(base, head, cwd=root)

def check_pr(root: Path, base: str, head: str) -> list[str]:
    """The PR path (`dyad check --pr <base> <head>`, the runner's optional hook): mode `range` — the
    commits and the whole diff, because a PR *is* a transaction Rule-1 binds."""
    return check_range(base, head, cwd=root)

def summary(root: Path | None = None) -> str:
    return f"tree: {len(git('ls-files', cwd=root or dyadlib.repo_root()).split())} files classified"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ex = ZONES[0] if ZONES else None
    names = sorted({z for z, _ in ZONES})
    rel = pkg.relative_to(root) if pkg.is_relative_to(root) else pkg
    return {"store": f"{rel}/guards/infra/containment.py (`ZONES`)", "parser": "`containment.ZONES` / `classify`", "observed": len(ZONES),
            "note": "first match wins; a transaction touches exactly one zone; zones: " + ", ".join(names),
            "fields": [(c, "enum" if i == 0 else "path", " | ".join(names) if i == 0 else "fnmatch glob over the whole path", True, ex[i] if ex else "", "containment.ZONE_FIELDS") for i, c in enumerate(ZONE_FIELDS)]}

def main(argv):
    if not argv:
        sys.exit(__doc__)
    mode, args = argv[0], argv[1:]
    fn = VERBS.get(mode)
    if fn is None:
        sys.exit(__doc__)
    fails = fn(args)
    if fails is None:              # the verb printed its own output (`zones`)
        return 0
    for f in fails:
        print(f, file=sys.stderr)
    print(f"containment {'OK' if not fails else 'FAILED'} [{mode}]")   # which mode ran (#166)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
