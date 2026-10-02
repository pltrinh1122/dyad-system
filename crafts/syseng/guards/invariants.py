#!/usr/bin/env python3
"""Invariants guard (entity `invariant`, corpus `craft`; the syseng craft's `rules/invariants.md` owns the check;
placed per crafts/sysarch/rules/guards.md under the craft's root; d-work #162, amended #203). Kernel: Python 3.12+.
(i) No `assert` statement outside `tests/` under `dyad/` and `crafts/` — `ast.Assert` nodes, never grep, so strings,
comments and prose cannot false-positive (fail). (ii) Every module that defines a data-model constant — an
upper-case module-level name bound to a tuple, list, dict, set or frozenset literal — exposes `INVARIANTS` (or
`TREE_INVARIANTS`), unless an `exempt: <path glob> # <reason>` line of `invariants_rules.txt` names it (fail; a stale
exempt line fails too). (iii) Every `INVARIANTS` and `TREE_INVARIANTS` entry of every module the runner's pass covers
(`package.invariant_modules`) is a `(str, callable)` pair with a kebab-case name unique across both lists (fail).
(iv) Every module that declares `INVARIANTS` calls `dyadlib.enforce(INVARIANTS, __name__)` at module level, after the
list's last binding — by `ast`, never grep. A warning until plan #203 P3 names `dyad` in `ENFORCE_FAILS_UNDER`, then a
failure under `dyad/`; a craft's module stays a warning until a craft follow-up. While `dyadlib.enforce` does not exist
(the core's protocol code, P2) it is one summary warning, never a crash. (v) One child process imports every module of
the runner's pass and runs each `INVARIANTS` predicate under a `sys.addaudithook` recording the events in `AUDITED`
(open, listdir/scandir/glob, subprocess, socket, a module import, filesystem writes), plus three the hook cannot see and
the child wraps instead (`os.stat`, an `os.environ` read, `dyadlib.load_module` of a module already loaded): a
predicate that raises one does I/O and belongs in `TREE_INVARIANTS` — a failure in a module that enforces at import, a
warning in one that does not yet. What neither sees — a C-level `getenv`, a value read from the environment or the
disk at import and then compared — stays inference, stated.
Whether the invariants *hold* is the runner's pass (`dyad check`), reported as `[invariant]` lines; whether a fact is
architectural is inference.
  invariants.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("invariants.py: Python 3.12+ required")
import ast, json, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/syseng/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "invariant", "craft", False
NAME, OWNER = "run-time invariant", "crafts/syseng/rules/invariants.md"
FIELDS = ("module", "name", "holds")
DATA = Path(__file__).resolve().parent / "invariants_rules.txt"
LITERALS = (ast.Tuple, ast.List, ast.Dict, ast.Set)
CONSTRUCTORS = {"frozenset", "set", "dict", "tuple", "list"}
_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
LISTS = ("INVARIANTS", "TREE_INVARIANTS")          # p1: the pure list, enforced at import; the tree list, run by the pass only
ENFORCE = "enforce"                                # p1: `dyadlib.enforce(INVARIANTS, __name__)`, at module level
ENFORCE_FAILS_UNDER: tuple[str, ...] = ()          # top-level dirs where (iv) fails rather than warns; plan #203 P3 sets ("dyad",)
# (v): the events that make a predicate impure — reading or writing a file, a stat, listing a directory, a child
# process, the network, an environment read, or loading a module. The last three lines' events have no audit hook and
# are recorded by wrappers in the child; what neither sees (a C-level getenv, a value read at import) is inference.
AUDITED = frozenset({
    "open", "os.listdir", "os.scandir", "glob.glob", "glob.glob/2", "pathlib.Path.glob", "pathlib.Path.rglob",
    "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork",
    "socket.connect", "socket.getaddrinfo", "socket.bind", "urllib.Request", "import",
    "os.mkdir", "os.remove", "os.rename", "os.rmdir", "os.chdir", "os.truncate", "os.chmod", "os.utime",
    "os.symlink", "os.link", "shutil.copyfile", "shutil.move", "shutil.rmtree",
    "os.stat", "os.environ", "dyadlib.load_module",   # no audit event: recorded by the child's wrappers (`_audit_child`)
})

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-in-order", lambda: FIELDS == ("module", "name", "holds")),
    ("constructors-are-collections", lambda: CONSTRUCTORS == {"frozenset", "set", "dict", "tuple", "list"}),
    ("lists-are-the-pure-then-the-tree", lambda: LISTS == ("INVARIANTS", "TREE_INVARIANTS")),
    ("enforce-fails-only-under-the-core", lambda: set(ENFORCE_FAILS_UNDER) <= {"dyad"}),
    ("audited-covers-the-plans-events", lambda: {"open", "os.listdir", "os.scandir", "subprocess.Popen", "import"} <= AUDITED),
]

# ---- data
def exemptions(path: Path = DATA) -> list[tuple[str, str]]:
    """[(path glob, reason)] from `exempt:` lines; a line without a reason keeps '' (reported)."""
    out = []
    if not path.exists():
        return out
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith("exempt:"):
            glob, _, reason = line.removeprefix("exempt:").partition("#")
            out.append((glob.strip(), reason.strip()))
    return out

def contrib_exemptions(pkg: Path = dyadlib.PKG) -> list[tuple[str, str, str]]:
    """[(glob, reason, source label)] from every installed craft's own `invariants_contrib.txt`, if
    it ships one (d-work #15): the craft-contributed half of `exemptions()`, kept separate by
    source so a malformed or stale row is reported naming that craft, never syseng. Same line
    format as the native file — `exemptions()` parses it unchanged."""
    out = []
    for d in dyadlib.craft_dirs(pkg):
        p = d / "guards" / "invariants_contrib.txt"
        if p.exists():
            label = f"crafts/{d.name}/guards/invariants_contrib.txt"
            out += [(glob, reason, label) for glob, reason in exemptions(p)]
    return out

# ---- scanning (ast)
def python_files(root: Path, pkg: Path = dyadlib.PKG) -> list[Path]:
    """Every .py under the core craft and every Tended craft, sorted; `__pycache__` skipped."""
    roots = [pkg] + ([dyadlib.crafts_dir(pkg)] if dyadlib.crafts_dir(pkg).is_dir() else [])
    return sorted(p for r in roots for p in r.rglob("*.py") if "__pycache__" not in p.parts)

def in_tests(rel: str) -> bool:
    return "tests" in Path(rel).parts

def asserts(tree: ast.AST) -> list[int]:
    return sorted(n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert))

def model_constants(tree: ast.Module) -> list[str]:
    """Upper-case module-level names bound to a collection literal or constructor call."""
    out = []
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            name, value = n.targets[0].id, n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
            name, value = n.target.id, n.value
        else:
            continue
        if not name.isupper() or name in LISTS:
            continue
        if isinstance(value, LITERALS) or (isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in CONSTRUCTORS):
            out.append(name)
    return out

def bindings(tree: ast.Module, name: str = "INVARIANTS") -> list[int]:
    """Line of every module-level statement that binds or extends `name`: `=`, `: T =`, `+=`, `.append/.extend(...)`."""
    out = []
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            out.append(n.lineno)
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and isinstance(n.target, ast.Name) and n.target.id == name:
            out.append(n.lineno)
        elif (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
              and n.value.func.attr in ("append", "extend") and isinstance(n.value.func.value, ast.Name)
              and n.value.func.value.id == name):
            out.append(n.lineno)
    return out

def declares_invariants(tree: ast.Module) -> bool:
    """(ii): the module binds either list (a module whose every fact reads the tree has only `TREE_INVARIANTS`)."""
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in LISTS for t in n.targets):
            return True
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id in LISTS:
            return True
    return False

def enforce_line(tree: ast.Module) -> int | None:
    """(iv): the line of the last module-level `dyadlib.enforce(INVARIANTS, ...)` (or `enforce(INVARIANTS, ...)`, as
    dyadlib itself would write it), else None. Only a top-level expression statement counts: inside a function, an
    `if` or a `try` it may never run."""
    line = None
    for n in tree.body:
        if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)):
            continue
        f, args = n.value.func, n.value.args
        named = ((isinstance(f, ast.Attribute) and f.attr == ENFORCE and isinstance(f.value, ast.Name) and f.value.id == "dyadlib")
                 or (isinstance(f, ast.Name) and f.id == ENFORCE))
        if named and args and isinstance(args[0], ast.Name) and args[0].id == "INVARIANTS":
            line = n.lineno
    return line

def enforcement_problem(tree: ast.Module) -> str | None:
    """(iv) for one parsed module: None when it declares no `INVARIANTS`, or enforces them after their last binding."""
    bound = bindings(tree)
    if not bound:
        return None
    line = enforce_line(tree)
    if line is None:
        return "declares INVARIANTS but never calls dyadlib.enforce(INVARIANTS, __name__) at module level"
    if line < max(bound):
        return f"dyadlib.enforce at line {line} precedes INVARIANTS' last binding at line {max(bound)}: later entries are never enforced"
    return None

def scan(root: Path, pkg: Path = dyadlib.PKG, exempt: list[tuple[str, str]] | None = None,
         labels: dict[str, str] | None = None) -> tuple[list[str], set[str]]:
    """(messages of checks (i) and (ii), exempt globs that matched a file). Paths are repo-relative.
    `labels`, when given, maps a glob to the file it came from (d-work #15: a craft's own
    `invariants_contrib.txt`) so a malformed or stale entry names that craft; a glob absent from
    `labels` reports `invariants_rules.txt`, today's only source and the default when `labels` is
    omitted entirely."""
    import fnmatch, re
    exempt = exemptions() if exempt is None else exempt
    labels = labels or {}
    label = lambda glob: labels.get(glob, "invariants_rules.txt")
    msgs, used = [], set()
    for glob, reason in exempt:
        if not reason:
            msgs.append(f"{label(glob)}: exempt {glob} has no reason")
    for py in python_files(root, pkg):
        rel = str(py.relative_to(root)) if py.is_relative_to(root) else str(py)
        try:
            tree = ast.parse(py.read_text(errors="ignore"), filename=rel)
        except SyntaxError as e:
            msgs.append(f"{rel}: does not parse ({e.msg}, line {e.lineno})"); continue
        if in_tests(rel):
            continue
        for line in asserts(tree):
            msgs.append(f"{rel}:{line}: `assert` in craft code (invariants.md p3: an invariant, never assert)")
        consts = model_constants(tree)
        if consts and not declares_invariants(tree):
            hit = next((g for g, _ in exempt if fnmatch.fnmatch(rel, g)), None)
            if hit:
                used.add(hit)
            else:
                msgs.append(f"{rel}: defines {', '.join(consts)} but no INVARIANTS (invariants.md p1)")
    tree = [str(q.relative_to(root)) for q in root.rglob("*") if q.is_file() and ".git" not in q.parts]
    for glob, _ in exempt:
        if glob not in used:
            if glob.startswith("crafts/") and not any(fnmatch.fnmatch(f, glob) for f in tree):
                msgs.append(f"warning: {label(glob)}: exempt {glob} matches no file here (a craft not installed); not checked")   # dyad-system #1
            else:
                msgs.append(f"{label(glob)}: exempt {glob} matches no module that needs it (stale)")
    return msgs, used

# ---- (iii): the entries of every module in the runner's pass
def own_entries(mod) -> list:
    """A module's `INVARIANTS` then `TREE_INVARIANTS`, as declared (a non-list contributes nothing; check_entries
    reports it). Read here rather than through `dyadlib.invariants_of`, so each entry is counted once whichever lists
    the core's reader covers."""
    return [e for n in LISTS if isinstance(getattr(mod, n, None), (list, tuple)) for e in getattr(mod, n)]

def entries(pkg: Path = dyadlib.PKG) -> list[tuple[str, str, bool]]:
    """(module label, invariant name, holds) for every entry of every module the runner's pass covers, sorted."""
    out = []
    runner = dyadlib.runner_module(pkg)
    if not hasattr(runner, "invariant_modules"):      # a fixture or foreign package without the pass: nothing to list
        return out
    for label, mod, extra in runner.invariant_modules():
        for e in own_entries(mod) + list(extra):
            if not (isinstance(e, tuple) and len(e) == 2 and callable(e[1])):
                continue                              # check_entries reports the shape
            name, pred = e
            try:
                ok = bool(pred())
            except Exception:
                ok = False
            out.append((label, name, ok))
    return sorted(out)

def check_entries(pkg: Path = dyadlib.PKG) -> list[str]:
    runner = dyadlib.runner_module(pkg)
    msgs = [] if hasattr(runner, "invariant_modules") else [f"{runner.__file__}: the runner has no invariant_modules (no pass to check)"]
    for label, mod, extra in (runner.invariant_modules() if not msgs else []):
        bad = [n for n in LISTS if not isinstance(getattr(mod, n, []), (list, tuple))]
        for n in bad:
            msgs.append(f"{label}: {n} is not a list")
        if bad:
            continue
        seen = set()
        for e in own_entries(mod) + list(extra):
            if not (isinstance(e, tuple) and len(e) == 2 and isinstance(e[0], str) and callable(e[1])):
                msgs.append(f"{label}: entry {e!r} is not a (name, callable) pair"); continue
            if not _NAME.match(e[0]):
                msgs.append(f"{label}: name {e[0]!r} is not kebab-case")
            if e[0] in seen:
                msgs.append(f"{label}: name {e[0]!r} declared twice")
            seen.add(e[0])
    return msgs

# ---- (iv): the import-time call
def enforces(py: Path) -> bool:
    try:
        return enforce_line(ast.parse(py.read_text(errors="ignore"))) is not None
    except (OSError, SyntaxError):
        return False

def check_enforce(root: Path, pkg: Path = dyadlib.PKG, present: bool | None = None,
                  fails_under: tuple[str, ...] | None = None) -> list[str]:
    """(iv): every module outside `tests/` that declares `INVARIANTS` enforces them at import. `present` is whether
    `dyadlib.enforce` exists (default: the imported dyadlib's); while it does not, one summary warning and no per-module
    line, since no module can call what the core does not ship yet. A module under a top-level dir named in
    `fails_under` (default `ENFORCE_FAILS_UNDER`) fails; any other warns, a craft's modules grouped one line per craft."""
    present = hasattr(dyadlib, ENFORCE) if present is None else present
    fails_under = ENFORCE_FAILS_UNDER if fails_under is None else fails_under
    found: list[tuple[str, str]] = []
    for py in python_files(root, pkg):
        rel = str(py.relative_to(root)) if py.is_relative_to(root) else str(py)
        if in_tests(rel):
            continue
        try:
            problem = enforcement_problem(ast.parse(py.read_text(errors="ignore"), filename=rel))
        except SyntaxError:
            continue                                   # scan() reports it
        if problem:
            found.append((rel, problem))
    if not found:
        return []
    if not present:
        core = sum(1 for rel, _ in found if not rel.startswith("crafts/"))
        return [f"warning: dyadlib.enforce does not exist yet (the core's protocol code, plan #203 P2): {core} module(s) "
                f"under dyad/ and {len(found) - core} under crafts/ declare INVARIANTS without the import-time call "
                f"(invariants.md p1); not checked per module until it does"]
    msgs, crafts = [], {}
    for rel, problem in found:
        parts = Path(rel).parts
        if parts[0] in fails_under:
            msgs.append(f"{rel}: {problem} (invariants.md p1)")
        elif parts[0] == "crafts" and len(parts) > 2:
            crafts.setdefault(parts[1], []).append(Path(*parts[2:]).as_posix())
        else:
            msgs.append(f"warning: {rel}: {problem} (invariants.md p1; fails from plan #203 P3)")
    for craft, files in sorted(crafts.items()):
        msgs.append(f"warning: crafts/{craft}: {len(files)} module(s) do not enforce INVARIANTS at import "
                    f"(invariants.md p1; a craft follow-up): {', '.join(sorted(files))}")
    return msgs

# ---- (v): pure means no audited event
def audit(modules: list[tuple[str, str, str]], timeout: int = 120) -> tuple[list[tuple[str, str, list[str]]], list[str]]:
    """Run every `INVARIANTS` predicate of `modules` — (label, module name, file) — in one child under an audit hook.
    Returns ([(label, invariant name, sorted events)] for every predicate that raised an `AUDITED` event, [problems]):
    a module the child cannot load is a problem (its loading is the registry's concern), a child that dies is one too."""
    if not modules:
        return [], []
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--audit-child"], input=json.dumps(modules),
                       capture_output=True, text=True, timeout=timeout)
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        tail = (r.stderr.strip().splitlines() or ["no output"])[-1]
        return [], [f"the audit child exited {r.returncode} without a report: {tail}"]
    return ([(l, n, ev) for l, n, ev in out["impure"]],
            [f"warning: {l}: the audit child could not load it: {e}" for l, e in out["errors"]])

def _audit_child(modules: list[list[str]]) -> dict:
    """The child's half of `audit`: load every module first (hook off), then run each predicate with the hook on.
    An audit hook cannot be removed once added, so it lives only in this process."""
    state = {"on": False, "events": set()}
    def hook(event, _args):
        if state["on"] and event in AUDITED:
            state["events"].add(event)
    loaded, errors = [], []
    for label, name, path in modules:
        try:
            loaded.append((label, dyadlib.load_module(Path(path), "package" if name == "__main__" else name)))
        except BaseException as e:                     # a module whose import raises is reported; the rest are audited
            errors.append((label, f"{type(e).__name__}: {e}"))
    sys.addaudithook(hook)
    # Three kinds of impurity raise no audit event, so the child wraps their entry points (only here, never in the
    # runner): a stat (`Path.exists`, `is_file`), an `os.environ` read, and a by-path load of a module already loaded,
    # which would read the disk in a fresh process at import.
    import os
    def recording(event, fn):
        def wrapped(*args, **kwargs):
            if state["on"]:
                state["events"].add(event)
            return fn(*args, **kwargs)
        return wrapped
    os.stat, os.lstat = recording("os.stat", os.stat), recording("os.stat", os.lstat)
    os._Environ.__getitem__ = recording("os.environ", os._Environ.__getitem__)
    os._Environ.__contains__ = recording("os.environ", os._Environ.__contains__)
    dyadlib.load_module = recording("dyadlib.load_module", dyadlib.load_module)
    impure = []
    for label, mod in loaded:
        own = getattr(mod, "INVARIANTS", [])
        for e in (own if isinstance(own, (list, tuple)) else []):
            if not (isinstance(e, tuple) and len(e) == 2 and callable(e[1])):
                continue                               # check_entries reports the shape
            state["events"] = set(); state["on"] = True
            try:
                e[1]()
            except Exception:
                pass                                   # holding is the pass's question; only the events matter here
            finally:
                state["on"] = False
            if state["events"]:
                impure.append((label, str(e[0]), sorted(state["events"])))
    return {"impure": sorted(impure), "errors": sorted(errors)}

def check_audit(pkg: Path = dyadlib.PKG) -> list[str]:
    """(v) over the runner's pass: an impure `INVARIANTS` entry fails in a module that enforces at import (it would do
    I/O in every process) and warns in one that does not yet (it must move before the module adopts `enforce`)."""
    runner = dyadlib.runner_module(pkg)
    if not hasattr(runner, "invariant_modules"):
        return []                                      # check_entries reports the missing pass
    mods = [(label, mod.__name__, mod.__file__) for label, mod, _ in runner.invariant_modules() if getattr(mod, "__file__", None)]
    impure, msgs = audit(mods)
    files = {label: path for label, _, path in mods}
    for label, name, events in impure:
        text = f"{label}: invariant {name!r} does I/O ({', '.join(events)}); move it to TREE_INVARIANTS (invariants.md p1)"
        msgs.append(text if enforces(Path(files[label])) else f"warning: {text}; not enforced at import yet")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = Path(root or dyadlib.repo_root())
    contrib = contrib_exemptions(pkg)   # d-work #15: every installed craft's own invariants_contrib.txt, if it ships one
    exempt = exemptions() + [(g, r) for g, r, _l in contrib]
    labels = {g: l for g, _r, l in contrib}
    msgs, _ = scan(root, pkg, exempt, labels)
    return msgs + check_entries(pkg) + check_enforce(root, pkg) + check_audit(pkg)

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    es = entries(pkg)
    return f"{len(es)} invariants in {len({e[0] for e in es})} modules, 0 asserts outside tests"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    es = entries(pkg); ex = es[0] if es else ("", "", True)
    return {"store": "`INVARIANTS` and `TREE_INVARIANTS` of every model module the runner's pass covers (`package.invariant_modules`)", "parser": "`invariants.entries` (`invariants.own_entries`)",
            "observed": len(es), "note": "never `assert` outside tests; a model module without INVARIANTS fails; INVARIANTS are pure and enforced at import, TREE_INVARIANTS run by the pass only; the runner prints `[invariant]` per module before any check",
            "fields": [("module", "text", "the pass label: `dyadlib`, `package`, `<group>/<entity>`, `project_<surface>`, `runbook`, `craft`, `distribute`", True, ex[0], "invariants.FIELDS"),
                       ("name", "text", "kebab-case, the architectural fact in words, unique per module across both lists", True, ex[1], "invariants.FIELDS"),
                       ("holds", "bool", "the predicate's value now; a false one is an incident", True, str(ex[2]).lower(), "invariants.FIELDS")]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    if a[:1] == ["--audit-child"]:                     # (v)'s child: the modules as JSON on stdin, one JSON report line out
        print(json.dumps(_audit_child(json.loads(sys.stdin.read()))))
        return 0
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        print(f"FAIL [invariants] {m}" if not m.startswith("warning:") else f"warn [invariants] {m.removeprefix('warning:').strip()}", file=sys.stderr if not m.startswith("warning:") else sys.stdout)
    if not fails:
        print(f"ok   [invariants] {summary(root)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
