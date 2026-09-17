#!/usr/bin/env python3
"""Run-book event guard (entity `event`, store zone `workstation`; the sysadmin craft's `server-instances.md`
owns the store's shape and its append-only fence (borrowed from Rule-3), placed per Rule-11 property 1 — a Tended
craft's guard, `crafts/sysadmin/guards/`, discovered by the core runner as `sysadmin/events`, #155).
Kernel: Python 3.12+, stdlib and git.

Store: `<runbooks>/events/<instance>.jsonl`, one JSON object per line, written only by the core runner
(`dyad/scripts/runbook.py`, which owns EVENT_FIELDS and the readers this guard re-exports; #155
amendment), committed like a change-log row. Package check: every line parses as an object carrying
every EVENT_FIELDS key and no other; `class` is a Rule-8 class (dyadlib.HOST_CLASSES), `role` one of
RUN_ROLES, `postcondition` one of POSTCONDITION_RESULTS, `instance` the file's name, `id`
`<instance>-<ts>-<name>`. Transaction check (TRANSACTION, on `main`, formerly in `main_fence.py`):
every first-parent commit — merges included, since events arrive by PR — may only add lines at the
end of an event file, never delete it, never change or remove a line (append-only).
  events.py [repo-root]              the package check
  events.py range <before> <after>   the append-only fence over a range
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("events.py: Python 3.12+ required")
import json, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))  # the core craft's library
import dyadlib
import runbook as _rb                                                   # the core runner: store paths, readers, EVENT_FIELDS

ENTITY, CORPUS, TRANSACTION = "event", "workstation", True
NAME, OWNER = "run-book event", "Rule-19"
FIELDS = _rb.EVENT_FIELDS
EVENT_FIELDS = FIELDS
CLASSES = dyadlib.HOST_CLASSES
RUN_ROLES = _rb.RUN_ROLES                                                # who ran it (event `role`)
POSTCONDITION_RESULTS = _rb.POSTCONDITION_RESULTS
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("event-fields-cover-dataclass", lambda: {"class" if f.name == "cls" else f.name for f in __import__("dataclasses").fields(_rb.Event)} <= set(EVENT_FIELDS)),
    ("classes-are-host-classes", lambda: CLASSES is dyadlib.HOST_CLASSES),
    ("postcondition-results-distinct", lambda: len(set(POSTCONDITION_RESULTS)) == len(POSTCONDITION_RESULTS)),
]
# re-exports (the runner owns the store's paths and readers)
events_dir, events_path, read_events, all_events = _rb.events_dir, _rb.events_path, _rb.read_events, _rb.all_events
runbooks_rel, runbooks = _rb.runbooks_rel, _rb                      # `runbooks.DEFAULT_RUNBOOKS` / `runbooks_dir` keep reading (the runner holds them)

# ---- package check: shape
def check_event(e, where: str, instance: str) -> list[str]:
    if not isinstance(e, dict):
        return [f"{where}: not a JSON object"]
    msgs, keys = [], set(e)
    missing = [k for k in FIELDS if k not in keys]
    if missing:
        msgs.append(f"{where}: missing field(s) {' '.join(missing)} (EVENT_FIELDS)")
    extra = sorted(keys - set(FIELDS))
    if extra:
        msgs.append(f"{where}: unknown field(s) {' '.join(extra)}")
    if e.get("class") not in CLASSES:
        msgs.append(f"{where}: class `{e.get('class')}` is not one of {', '.join(CLASSES)} (Rule-8)")
    if e.get("role") not in RUN_ROLES:
        msgs.append(f"{where}: role `{e.get('role')}` is not one of {', '.join(RUN_ROLES)}")
    if e.get("postcondition") not in POSTCONDITION_RESULTS:
        msgs.append(f"{where}: postcondition `{e.get('postcondition')}` is not one of {', '.join(POSTCONDITION_RESULTS)}")
    if e.get("instance") != instance:
        msgs.append(f"{where}: instance `{e.get('instance')}` is not the file's `{instance}`")
    if not missing and not str(e.get("id", "")).startswith(f"{instance}-") or not str(e.get("id", "")).endswith(f"-{e.get('name', '')}"):
        msgs.append(f"{where}: id `{e.get('id')}` is not `<instance>-<ts>-<name>`")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    d = events_dir(root)
    if not d.is_dir():
        return []
    msgs = []
    for p in sorted(d.glob("*.jsonl")):
        rel = p.relative_to(root) if p.is_relative_to(root) else p
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError as err:
                msgs.append(f"{rel}:{i}: not a JSON object ({err.msg})"); continue
            msgs += check_event(e, f"{rel}:{i}", p.stem)
    return msgs

def summary(root: Path | None = None) -> str:
    evs = all_events(root)
    return f"{sum(len(v) for v in evs.values())} events, {len(evs)} instances"

# ---- transaction check: append-only on main
def git(*a, cwd): return subprocess.check_output(["git", *a], cwd=cwd, text=True)

def parent(sha, cwd):
    p = git("rev-list", "--parents", "-n", "1", sha, cwd=cwd).split()
    return p[1] if len(p) > 1 else EMPTY_TREE

def check_events(sha: str, cwd, events_prefix: str | None = None) -> list[str]:
    """Rule-19 property 7: an event file under `<runbooks>/events/` only grows (append-only), against
    the commit's first parent — so a merge is judged on what the PR added."""
    prefix = events_prefix if events_prefix is not None else f"{runbooks_rel()}/events/"
    label, fails = sha[:9], []
    par = parent(sha, cwd)
    for st, path in (l.split("\t", 1) for l in git("diff-tree", "--root", "--no-commit-id", "-r", "--name-status", "--no-renames", "-m", "--first-parent", sha, cwd=cwd).splitlines() if "\t" in l):
        if not (path.startswith(prefix) and path.endswith(".jsonl")):
            continue
        if st.startswith("D"):
            fails.append(f"FAIL [main-fence]: {label} deletes event file {path} (append-only)"); continue
        if st.startswith("M"):
            before = git("show", f"{par}:{path}", cwd=cwd)
            after = git("show", f"{sha}:{path}", cwd=cwd)
            if not after.startswith(before) or (before and not before.endswith("\n")):
                fails.append(f"FAIL [main-fence]: {label} rewrites event file {path}; events are append-only")
    return fails

def check_range(before: str, after: str, cwd=None) -> list[str]:
    cwd = cwd or dyadlib.repo_root()
    fails = []
    for sha in git("rev-list", "--first-parent", f"{before}..{after}", cwd=cwd).split():
        fails += check_events(sha, cwd)
    return fails

def check_transaction(root: Path, base: str, head: str) -> list[str]:
    if git("rev-parse", "--abbrev-ref", "HEAD", cwd=root).strip() != "main":
        return []
    return check_range(base, head, cwd=root)

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    evs = [(inst, ev) for inst, lst in sorted(all_events(root).items()) for ev in lst]
    ex = evs[-1][1] if evs else None
    d = events_dir(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    allowed = {"id": "`<instance>-<utc ts>-<name>`", "ts": "ISO 8601 UTC", "role": " | ".join(RUN_ROLES), "class": " | ".join(CLASSES),
               "exit": "the command's exit code", "duration_ms": "milliseconds", "postcondition": " | ".join(POSTCONDITION_RESULTS),
               "output_sha256": "sha256 of stdout+stderr", "output_tail": "last lines of the output, bounded by the runner",
               "commit": "`git rev-parse --short HEAD` when run", "runbook_sha256": "sha256 of the run-book file when run"}
    types = {"exit": "int", "duration_ms": "int", "ts": "date", "role": "enum", "class": "enum", "postcondition": "enum"}
    return {"store": f"{rel}/<instance>.jsonl", "parser": "`events.read_events`", "observed": len(evs),
            "note": "append-only on main (this guard's transaction check); written only by the core runner (`dyad/scripts/runbook.py`); the change-log row of a host action cites `event: <id>` (Rule-8)",
            "fields": [(f, types.get(f, "text"), allowed.get(f, ""), True, str(ex.get(f, "")) if ex else "", "runbook.EVENT_FIELDS") for f in FIELDS]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = dyadlib.repo_root()
    if a and a[0] == "range" and len(a) == 3:
        fails = check_range(a[1], a[2], cwd=root)
        for f in fails: print(f, file=sys.stderr)
        print("events append-only OK" if not fails else "events append-only FAILED")
        return 1 if fails else 0
    root = Path(a[0]).resolve() if a else root
    msgs = check_package(root)
    for m in msgs: print(f"FAIL [rule-19] {m}", file=sys.stderr)
    if not msgs: print(f"ok   [rule-19] {summary(root)}")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
