#!/usr/bin/env python3
"""Merge guard (entity `merge`, agent corpus; Rule-2 owns the check — every merge into `main` executes a recorded
Done-`Y` — placed per Rule-11 property 1; d-work #541, R2 and R5 of the chain-of-command stress test). Kernel:
Python 3.12+, git.

The fence judges first-parent non-merge commits only (`rows.py`), so a merge commit is unjudged twice over: its tree
may carry content no parent holds (A3, an "evil merge"), and nothing ties it to the Operator's `Y` (A5, and the merge
half of A2 — an allowed verb run from edited local code). For each first-parent merge commit in the judged range:
  (a) its tree must equal `git merge-tree --write-tree` of its two parents; otherwise warn, listing the paths that
      differ (a merge with resolved conflicts differs on those paths only, so a reader sees what the resolution
      changed; `dyad merge` never resolves one, so its merges match exactly);
  (b) its second parent must be named by an operative `Y done` on some row — the row's last disposition when that
      is a `Y done` (`rows.operative_done`), any state, by full sha or the prefix the entry records, read in the
      ledger at the merge's first parent (the `Y` is recorded before its merge, Rule-3, so it is there; a `Y release`
      written on the row after the merge must not void it); otherwise warn.
      A merge whose second parent is already on the pushed range's base (`main` brought into a branch), and a merge
      whose brought-in commits are ledger-only or events-only (clerical, Rule-2 and Rule-3; `ledger-pr-merge`), name
      no `Y` and are not read for it.
Every finding is a warning, never a failure: detection is the posture the Operator chose (#532 revision 3), and the
range is bounded so standing history does not flood. Package mode (the registry, CI): first-parent merges of
`origin/main` (else HEAD) since the instance's own starting point, one full sha in `<instance>/merges_since.local.txt`
(`SINCE_FILE`; `#` comments and blank lines allowed) — nothing before it is judged, and the core holds no instance sha
(#544). An absent file skips with one line; a sha this clone lacks skips as before; a file that is not exactly one full
sha warns and judges nothing. One ledger read per merge (about 0.15 s), so when the range grows slow the instance moves
its file forward.
Transaction mode (the kernel-only path, every push): first-parent merges of `base..head`.
Inference, stated: whether a listed resolution is right, and whether a `Y` named the PR the Operator meant.
  merges.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("merges.py: Python 3.12+ required")
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "merge", "agent", True
CLERICAL_READS = ()   # d-work #564: the ledger/events paths (instance-relative) its state check reads —
                          # its state check judges the first-parent merges since the instance's file; a clerical push brings none (its transaction check judges a pushed merge); on a clerical push touching none, the gate leaves it to the sweep
NAME, OWNER = "merge commit on main", "Rule-2"
FIELDS = ("merge", "parents", "tree", "named_by")
SINCE_FILE = "merges_since.local.txt"                # <instance>/: the sha package mode judges merges since (#544), instance data
TARGETS = ("origin/main", "HEAD")                     # the line package mode walks: the first that resolves

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("since-file-is-instance-local", lambda: SINCE_FILE.endswith(".local.txt") and "/" not in SINCE_FILE),
    ("package-mode-prefers-main", lambda: TARGETS[0] == "origin/main"),
    ("a-full-sha-is-forty-hex", lambda: full_sha("a" * 40) and not full_sha("a" * 39) and not full_sha("g" * 40)),
]
TREE_INVARIANTS = [   # reads the instance file of the live repo: the runner's pass only, never at import
    ("since-file-is-absent-or-one-full-sha", lambda: since(dyadlib.repo_root())[1] is None),
]


def full_sha(s: str) -> bool:
    return len(s) == 40 and all(c in "0123456789abcdef" for c in s)


def since_path(root: Path) -> Path:
    return dyadlib.instance(root) / SINCE_FILE


def since(root: Path) -> tuple[str | None, str | None]:
    """(sha, problem): the full sha `<instance>/merges_since.local.txt` holds — its one token once `#` comments and
    blank lines are dropped. (None, None) when the file is absent; (None, why) when it is not exactly one full sha."""
    p = since_path(root)
    if not p.is_file():
        return None, None
    try:
        toks = [t for line in p.read_text(encoding="utf-8").splitlines() for t in line.split("#", 1)[0].split()]
    except (OSError, UnicodeDecodeError) as e:
        return None, f"{SINCE_FILE}: unreadable ({e})"
    if len(toks) != 1 or not full_sha(toks[0]):
        return None, f"{SINCE_FILE}: wants exactly one full 40-hex sha, holds {len(toks)} token(s): {' '.join(toks)[:80]!r}"
    return toks[0], None


def git(root: Path, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)


def out(root: Path, *a: str) -> str | None:
    r = git(root, *a)
    return r.stdout.strip() if r.returncode == 0 else None


def first_parent_merges(root: Path, base: str, head: str) -> list[str] | None:
    """The merge commits on `head`'s first-parent line that `base` lacks, oldest first; None when git cannot say."""
    o = out(root, "rev-list", "--reverse", "--first-parent", "--merges", f"{base}..{head}")
    return None if o is None else o.split()


def tree_problem(root: Path, sha: str, p1: str, p2: str) -> str | None:
    """(a): None when the merge's tree is `git merge-tree` of its parents; else a warning listing the paths."""
    r = git(root, "merge-tree", "--write-tree", p1, p2)
    want = (r.stdout.splitlines() or [""])[0].strip()
    if not want:
        return f"warning: merge {sha[:12]}: git merge-tree of its parents gave no tree; not compared"
    got = out(root, "rev-parse", f"{sha}^{{tree}}")
    if got == want:
        return None
    paths = (out(root, "diff", "--name-only", "--no-renames", want, got or sha) or "").split()
    how = "a conflicted merge, resolved" if r.returncode == 1 else "a clean merge"
    return (f"warning: merge {sha[:12]}'s tree is not the merge of its parents ({how}); it differs on "
            f"{len(paths)} path(s): {', '.join(paths[:10])}{' …' if len(paths) > 10 else ''} (#541, A3)")


def clerical(root: Path, p1: str, p2: str) -> bool:
    return dyadlib.ledger_only(root, p1, p2) or dyadlib.events_only(root, p1, p2)


def authority_problem(root: Path, sha: str, p1: str, p2: str, heads, base: str | None = None) -> str | None:
    """(b): None when an operative `Y done` names the second parent, or the merge names none (see the docstring)."""
    if base and git(root, "merge-base", "--is-ancestor", p2, base).returncode == 0:
        return None                       # it brings in what `base` already holds: `main` merged into a branch
    if clerical(root, p1, p2):
        return None
    if any(p2.startswith(h) for _, _, h, _ in heads):
        return None
    return (f"warning: merge {sha[:12]} brings in {p2[:12]}, which no operative Y done names "
            f"(no row's last disposition is a `Y done` naming it; Rule-2 Binding, #541 A5)")


def rows_at(root: Path, ref: str, cache: dict | None = None) -> list:
    """The ledger's rows as they stood at `ref` (a merge is judged against the ledger it was made on: a `Y release`
    written on the row after its merge must not void the `Y done` it executed). The store is listed with its blob ids
    and only blobs not already in `cache` (blob id -> parsed row, or None for a row that does not parse) are read, in
    one `git cat-file --batch`: consecutive merges share all but the few rows a ledger commit changed, so judging n
    merges reads the store once and then only what changed (d-work #563 C4). Rows that do not parse are skipped; an
    unreadable store gives []."""
    cache = {} if cache is None else cache
    rel = dyadlib.rows_dir(root).relative_to(root).as_posix() if dyadlib.rows_dir(root).is_relative_to(root) else None
    listing = out(root, "ls-tree", f"{ref}:{rel}") if rel else None
    if not listing:
        return []
    blobs = []
    for line in listing.splitlines():
        meta, _, name = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob" and name.endswith(".md") and name[:-3].isdigit():
            blobs.append(parts[2])
    want = [b for b in dict.fromkeys(blobs) if b not in cache]
    if want:
        r = subprocess.run(["git", "cat-file", "--batch"], cwd=root, input="".join(f"{b}\n" for b in want).encode(),
                           capture_output=True, env=dyadlib.git_env(), timeout=120)
        data, i = r.stdout, 0
        while i < len(data):
            nl = data.index(b"\n", i)
            head = data[i:nl].split()
            i = nl + 1
            if len(head) < 3 or head[1] != b"blob":
                continue
            size = int(head[2]); text = data[i:i + size].decode(errors="replace"); i += size + 1
            try:
                cache[head[0].decode()] = dyadlib.parse_row_file(text)
            except (KeyError, ValueError):
                cache[head[0].decode()] = None
    return [cache[b] for b in blobs if cache.get(b) is not None]


def judge(root: Path, merges: list[str], base: str | None = None) -> list[str]:
    """Each merge against its parents (a), and against the operative `Y done`s of the ledger at its first parent (b)."""
    rg = dyadlib.load_guard("agent", "rows")
    msgs, cache = [], {}                                 # parsed rows by blob id, shared across the merges (#563 C4)
    for sha in merges:
        parents = (out(root, "rev-list", "--parents", "-n", "1", sha) or "").split()[1:]
        if len(parents) != 2:
            msgs.append(f"warning: merge {sha[:12]} has {len(parents)} parents; only two-parent merges are judged")
            continue
        p1, p2 = parents
        heads = rg.named_heads(rows_at(root, p1, cache), terminal=True)
        msgs += [m for m in (tree_problem(root, sha, p1, p2), authority_problem(root, sha, p1, p2, heads, base)) if m]
    return msgs


def target(root: Path) -> str | None:
    return next((t for t in TARGETS if out(root, "rev-parse", "--verify", "-q", f"{t}^{{commit}}")), None)


def start(root: Path) -> tuple[str | None, str | None, str]:
    """(target, since sha, why not) for package mode: both None, and the reason, when nothing is judged."""
    sha, problem = since(root)
    if problem:
        return None, None, problem
    if sha is None:
        return None, None, f"no {SINCE_FILE} in the instance (the merges since which this system judges); nothing judged"
    t = target(root)
    if t is None or out(root, "rev-parse", "--verify", "-q", f"{sha}^{{commit}}") is None:
        return None, None, f"{sha[:12]} ({SINCE_FILE}) is not in this clone; nothing judged"
    if git(root, "merge-base", "--is-ancestor", sha, t).returncode != 0:
        return None, None, f"{sha[:12]} ({SINCE_FILE}) is not on {t}; nothing judged"
    return t, sha, ""


def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Package mode: first-parent merges of `origin/main` (else HEAD) since the instance's `SINCE_FILE`. An absent
    file, or a sha this clone lacks (an installed system, with its own history), judges nothing and says so in the
    summary; a malformed file warns."""
    root = root or dyadlib.repo_root()
    t, sha, why = start(root)
    if t is None:
        return [f"warning: {why}"] if since(root)[1] else []
    merges = first_parent_merges(root, sha, t)
    return [] if not merges else judge(root, merges)


def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """Transaction mode: the first-parent merges a push brings (`base..head`), each read against the ledger at its first parent."""
    merges = first_parent_merges(root, base, head)
    return [] if not merges else judge(root, merges, base)


def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    root = root or dyadlib.repo_root()
    t, sha, why = start(root)
    if t is None:
        return f"skip: {why}"
    return f"{len(first_parent_merges(root, sha, t) or [])} merge(s) on {t} since {sha[:12]}"


def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    t, sha, _ = start(root)
    return {"store": "git history: first-parent merge commits of main", "parser": "`merges.first_parent_merges`",
            "observed": len(first_parent_merges(root, sha, t) or []) if t else 0,
            "note": "each merge's tree is git merge-tree of its parents, and its second parent is named by an operative Y done",
            "fields": [("merge", "sha", "40 hex", True, "", "merges.FIELDS"),
                       ("parents", "sha list", "two", True, "", "merges.FIELDS"),
                       ("tree", "sha", "git merge-tree --write-tree of the parents", True, "", "merges.FIELDS"),
                       ("named_by", "row", "a row whose last disposition is a Y done naming the second parent", True, "", "merges.FIELDS")]}


def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    for m in check_package(root):
        print(f"warn [rule-2] {m.removeprefix('warning:').strip()}")
    print(f"ok   [rule-2] {summary(root)}")
    return 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
