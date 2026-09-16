#!/usr/bin/env python3
"""Row-file guard (entity `row`, agent corpus; Rule-3 owns the content and the fence, Rule-16 the
store; placed per Rule-11 property 1). Kernel: Python 3.12+.

Package check (`check_package`): every `<instance>/d-work/rows/<id>.md` parses (dyadlib.FIELDS), its
id equals its file name, its state is one of dyadlib.STATES, and no id is duplicated.

Transaction check (`check_transaction`, TRANSACTION; the main fence, referenced by Rule-2): a commit
pushed directly to main (non-merge, first-parent) may touch only <instance>/d-work/ and, for row
files, may only add a file or change state/disposed/refs: never delete a row file or change its id
or title (C3). A state change must be a transition in dyadlib.TRANSITIONS (Rule-16: state never
regresses; d-work #112) and a new row file must start in dyadlib.NEW_STATES. The rendered
LEDGER.md is untracked (d-work #111) and is not diffed. This full fence applies on `main` only;
on a branch `check_transaction` instead runs `check_id_collisions` (d-work #32 F2): a row id this
range adds or modifies must not already exist at the base under a *different* title — the
signature of two sessions racing the allocator — leaving the append-only rules themselves to this
same fence once the branch reaches `main`, and the plan gate to `prs.py`. The append-only rule of the run-book event store
(the sysadmin craft's server-instances rule) lives in the craft's guard `crafts/sysadmin/guards/events.py`;
the CLI below runs both when that guard is installed, as the former `main_fence.py` did (#155).
  rows.py <before> <after>          the main fence over a pushed range (rows and events)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("rows.py: Python 3.12+ required")
import os, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "row", "agent", True
NAME, OWNER = "d-work row file", "Rule-3 (content), Rule-16 (store)"
FIELDS = dyadlib.FIELDS
INVARIANTS = [("fields-are-dyadlib-fields", lambda: FIELDS is dyadlib.FIELDS)]   # crafts/syseng/rules/invariants.md
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

def git(*a, cwd, stderr=None): return subprocess.check_output(["git", *a], cwd=cwd, text=True, stderr=stderr)

def parent(sha, cwd):
    p = git("rev-list", "--parents", "-n", "1", sha, cwd=cwd).split()
    return p[1] if len(p) > 1 else EMPTY_TREE

def branch(cwd) -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd).strip()

# ---- package check
def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    d = dyadlib.rows_dir(root)
    if not d.is_dir():
        return []
    fails, seen = [], set()
    for p in sorted(d.glob("*.md"), key=lambda p: int(p.stem) if p.stem.isdigit() else -1):
        if not p.stem.isdigit():
            continue
        rel = p.relative_to(root) if p.is_relative_to(root) else p
        try:
            r = dyadlib.parse_row_file(p.read_text())
        except ValueError as e:
            fails.append(f"{rel}: {e}"); continue
        if r.id != int(p.stem):
            fails.append(f"{rel}: id {r.id} differs from the file name")
        if r.state not in dyadlib.STATES:
            fails.append(f"{rel}: state '{r.state}' not one of {' '.join(sorted(dyadlib.STATES))}")
        if r.id in seen:
            fails.append(f"{rel}: duplicate id {r.id}")
        seen.add(r.id)
    return fails

def summary(root: Path | None = None) -> str:
    root = root or dyadlib.repo_root()
    d = dyadlib.rows_dir(root)
    return f"{sum(1 for p in d.glob('*.md') if p.stem.isdigit()) if d.is_dir() else 0} rows"

# ---- transaction check (the main fence)
def check_commit(sha: str, cwd, instance: str) -> list[str]:
    label = sha[:9]
    paths = git("diff-tree", "--root", "--no-commit-id", "-r", "--name-only", sha, cwd=cwd).split()
    bad = [p for p in paths if not p.startswith(f"{instance}/d-work/")]
    if bad:
        return [f"FAIL [main-fence]: direct commit {label} touches non-ledger paths: {' '.join(bad)}"]
    fails = []
    par = parent(sha, cwd)
    for st, path in (l.split("\t", 1) for l in git("diff-tree", "--root", "--no-commit-id", "-r", "--name-status", "--no-renames", sha, cwd=cwd).splitlines() if "\t" in l):
        if not path.startswith(f"{instance}/d-work/rows/"):
            continue
        if st.startswith("D"):
            fails.append(f"FAIL [main-fence]: {label} deletes row file {path}"); continue
        if st.startswith("M"):
            before = dyadlib.parse_row_file(git("show", f"{par}:{path}", cwd=cwd))
            after = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd))
            if before.id != after.id or before.title != after.title:
                fails.append(f"FAIL [main-fence]: {label} changes id or title of row file {path}"); continue
            if not dyadlib.allowed(before.state, after.state):
                how = "leaves the table" if after.state not in dyadlib.STATES else "regresses"
                fails.append(f"FAIL [main-fence]: {label} row file {path} state {how} {before.state}→{after.state}")
        elif st.startswith("A"):
            new = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd))
            if new.state not in dyadlib.NEW_STATES:
                fails.append(f"FAIL [main-fence]: {label} adds row file {path} in state {new.state} (not one of {' '.join(sorted(dyadlib.NEW_STATES))})")
    return fails

def check_range(before: str, after: str, cwd=None) -> list[str]:
    """Row rules over every non-merge first-parent commit of before..after."""
    cwd = cwd or dyadlib.repo_root()
    instance = os.environ.get("DYAD_INSTANCE", "agent-corpus")
    fails = []
    for sha in git("rev-list", "--first-parent", "--no-merges", f"{before}..{after}", cwd=cwd).split():
        fails += check_commit(sha, cwd, instance)
    return fails

def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """The fence judges direct commits to `main`; on any other branch it checks only that a new
    or modified row id does not collide with a different title already at `base` — two sessions
    independently allocating the same id for different work (d-work #32) — leaving everything
    else (the append-only rules) to this same fence once the branch reaches `main`."""
    if branch(root) != "main":
        return check_id_collisions(root, base, head)
    return check_range(base, head, cwd=root)

def check_id_collisions(root: Path, base: str, head: str) -> list[str]:
    """On a branch: a row file this range adds or modifies must not name an id that already
    exists at `base` under a *different* title — the signature of two sessions racing the
    allocator (d-work #32 F2). Silent otherwise: this is not the append-only fence, which only
    ever runs on `main`; a malformed row file is reported separately by `check_package`, so a
    parse failure here is skipped rather than crashing this guard."""
    instance = os.environ.get("DYAD_INSTANCE", "agent-corpus")
    prefix = f"{instance}/d-work/rows/"
    try:
        paths = git("diff", "--name-only", f"{base}..{head}", "--", prefix, cwd=root).split()
    except subprocess.CalledProcessError:
        return []
    fails = []
    for path in paths:
        stem = Path(path).stem
        if not stem.isdigit():
            continue
        try:
            head_row = dyadlib.parse_row_file(git("show", f"{head}:{path}", cwd=root, stderr=subprocess.DEVNULL))
        except (subprocess.CalledProcessError, ValueError):
            continue
        try:
            # a brand-new row at head legitimately has no base:path — git's own "not in <sha>"
            # is expected here, not an error worth printing
            base_row = dyadlib.parse_row_file(git("show", f"{base}:{path}", cwd=root, stderr=subprocess.DEVNULL))
        except (subprocess.CalledProcessError, ValueError):
            continue
        if base_row.id == head_row.id and base_row.title != head_row.title:
            fails.append(f"FAIL [row-id]: {path} id {base_row.id} already names {base_row.title!r} "
                         f"at the base — a concurrent session likely allocated the same id "
                         f"for different work ({head_row.title!r})")
    return fails

# ---- entity card (the entities projector reads it; crafts/sysarch/templates/entity-card.md)
def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    rows = dyadlib.read_rows(root) if dyadlib.rows_dir(root).is_dir() else []
    ex = max(rows, key=lambda r: r.id) if rows else None
    trans = "; ".join(f"{a} → {', '.join(sorted(b)) or '∅'}" for a, b in sorted(dyadlib.TRANSITIONS.items()))
    types = {"id": "int", "title": "text", "opened": "date", "state": "enum", "disposed": "text", "refs": "text"}
    allowed = {"id": "unique, allocated by `package.py dwork new`", "opened": "YYYY-MM-DD",
               "state": f"{' | '.join(sorted(dyadlib.STATES))}; new rows: {' | '.join(sorted(dyadlib.NEW_STATES))}",
               "disposed": "`<date> <Y|N> <plan|done|merge #n|reason>` entries joined by `;` (Rule-3)", "refs": "`#<id>`, `parent #<id>`, `children #a–#b`, `PR #n` (Rule-3)"}
    rel = dyadlib.rows_dir(root); rel = rel.relative_to(root) if rel.is_relative_to(root) else rel
    return {"store": f"{rel}/<id>.md", "parser": "`dyadlib.parse_row_file` / `read_rows`", "observed": len(rows),
            "note": f"append-only; id and title immutable; transitions (`dyadlib.TRANSITIONS`): {trans}",
            "fields": [(f, types[f], allowed.get(f, ""), True, str(getattr(ex, f)) if ex else "", "dyadlib.FIELDS") for f in FIELDS]}

def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    root = dyadlib.repo_root()
    ev = dyadlib.find_guard("workstation", "events")
    fails = check_range(argv[0], argv[1], cwd=root) + (ev.check_range(argv[0], argv[1], cwd=root) if ev else [])
    for f in fails:
        print(f, file=sys.stderr)
    print("main fence OK" if not fails else "main fence FAILED")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
