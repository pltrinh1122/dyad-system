#!/usr/bin/env python3
"""Invariants guard (entity `invariant`, corpus `craft`; the syseng craft's `rules/invariants.md` owns the check;
placed per crafts/sysarch/rules/guards.md under the craft's root; d-work #162). Kernel: Python 3.12+.
(i) No `assert` statement outside `tests/` under `dyad/` and `crafts/` — `ast.Assert` nodes, never grep, so strings,
comments and prose cannot false-positive (fail). (ii) Every module that defines a data-model constant — an
upper-case module-level name bound to a tuple, list, dict, set or frozenset literal — exposes `INVARIANTS`, unless
an `exempt: <path glob> # <reason>` line of `invariants_rules.txt` names it (fail; a stale exempt line fails too).
(iii) Every `INVARIANTS` entry of every module the runner's pass covers (`package.invariant_modules`) is a
`(str, callable)` pair with a unique kebab-case name (fail). Whether the invariants *hold* is the runner's pass
(`dyad check`), reported as `[invariant]` lines; whether a fact is architectural is inference.
  invariants.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("invariants.py: Python 3.12+ required")
import ast, re
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

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-in-order", lambda: FIELDS == ("module", "name", "holds")),
    ("constructors-are-collections", lambda: CONSTRUCTORS == {"frozenset", "set", "dict", "tuple", "list"}),
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
        if not name.isupper() or name == "INVARIANTS":
            continue
        if isinstance(value, LITERALS) or (isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in CONSTRUCTORS):
            out.append(name)
    return out

def declares_invariants(tree: ast.Module) -> bool:
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "INVARIANTS" for t in n.targets):
            return True
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == "INVARIANTS":
            return True
    return False

def scan(root: Path, pkg: Path = dyadlib.PKG, exempt: list[tuple[str, str]] | None = None) -> tuple[list[str], set[str]]:
    """(messages of checks (i) and (ii), exempt globs that matched a file). Paths are repo-relative."""
    import fnmatch, re
    exempt = exemptions() if exempt is None else exempt
    msgs, used = [], set()
    for glob, reason in exempt:
        if not reason:
            msgs.append(f"invariants_rules.txt: exempt {glob} has no reason")
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
                msgs.append(f"warning: invariants_rules.txt: exempt {glob} matches no file here (a craft not installed); not checked")   # dyad-system #1
            else:
                msgs.append(f"invariants_rules.txt: exempt {glob} matches no module that needs it (stale)")
    return msgs, used

# ---- (iii): the entries of every module in the runner's pass
def entries(pkg: Path = dyadlib.PKG) -> list[tuple[str, str, bool]]:
    """(module label, invariant name, holds) for every entry of every module the runner's pass covers, sorted."""
    out = []
    runner = dyadlib.runner_module(pkg)
    if not hasattr(runner, "invariant_modules"):      # a fixture or foreign package without the pass: nothing to list
        return out
    for label, mod, extra in runner.invariant_modules():
        for e in dyadlib.invariants_of(mod, extra):
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
        own = getattr(mod, "INVARIANTS", [])
        if not isinstance(own, (list, tuple)):
            msgs.append(f"{label}: INVARIANTS is not a list"); continue
        seen = set()
        for e in list(own) + list(extra):
            if not (isinstance(e, tuple) and len(e) == 2 and isinstance(e[0], str) and callable(e[1])):
                msgs.append(f"{label}: entry {e!r} is not a (name, callable) pair"); continue
            if not _NAME.match(e[0]):
                msgs.append(f"{label}: name {e[0]!r} is not kebab-case")
            if e[0] in seen:
                msgs.append(f"{label}: name {e[0]!r} declared twice")
            seen.add(e[0])
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = Path(root or dyadlib.repo_root())
    msgs, _ = scan(root, pkg)
    return msgs + check_entries(pkg)

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    es = entries(pkg)
    return f"{len(es)} invariants in {len({e[0] for e in es})} modules, 0 asserts outside tests"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    es = entries(pkg); ex = es[0] if es else ("", "", True)
    return {"store": "`INVARIANTS` of every model module the runner's pass covers (`package.invariant_modules`)", "parser": "`invariants.entries` (`dyadlib.invariants_of`)",
            "observed": len(es), "note": "never `assert` outside tests; a model module without INVARIANTS fails; the runner prints `[invariant]` per module before any check",
            "fields": [("module", "text", "the pass label: `dyadlib`, `package`, `<group>/<entity>`, `project_<surface>`, `runbook`, `craft`, `distribute`", True, ex[0], "invariants.FIELDS"),
                       ("name", "text", "kebab-case, the architectural fact in words, unique per module", True, ex[1], "invariants.FIELDS"),
                       ("holds", "bool", "the predicate's value now; a false one is an incident", True, str(ex[2]).lower(), "invariants.FIELDS")]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
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
