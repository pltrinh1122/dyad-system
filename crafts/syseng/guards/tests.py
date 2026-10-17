#!/usr/bin/env python3
"""Test-mapping guard (entity `test`, corpus `craft`; the syseng craft's `rules/verifiable-code.md` p4 owns the mapping;
placed per crafts/sysarch/rules/guards.md under the craft's root; d-work #162). Kernel: Python 3.12+.
The mapping moved from the runner's `check_rule_12` (which keeps "run the tests"): `dyad/scripts/<n>.py` ->
`dyad/tests/test_<n>.py` (`package.py` and `_`-prefixed exempt); `dyad/guards/<c>/<e>.py` -> `dyad/tests/guards/<c>/test_<e>.py`;
`crafts/<craft>/guards/<e>.py` -> `crafts/<craft>/tests/guards/test_<e>.py`; `crafts/<craft>/projectors/<n>.py` and
`crafts/<craft>/scripts/<n>.py` -> `crafts/<craft>/tests/test_<n>.py`. A module without its test at the mapped path fails.
The component clause (#336, `verifiable-code.md` p4): a *component* is `dyad/<kind>/<component>/` or
`crafts/<craft>/<kind>/<component>/` that holds its own `tests/` directory (`<kind>` never `tests`); every `*.py` under
it outside `tests/` — recursively, sub-packages included, `_`-prefixed names and so `__init__.py` excluded — maps to
`<component>/tests/test_<stem>.py`, and two modules of one component sharing a stem across its sub-packages fail (the
mapping could not tell their tests apart). Generic by design: the same clause serves `dyad/server/<x>/`,
`dyad/tools/<x>/` or any craft's packaged component, each needing only its own `kind:` row of `naming_rules.txt`.
The mapping is one-way: a test without a module is legal. Whether a test is adequate is inference.
  tests.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("tests.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/syseng/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "test", "craft", False
NAME, OWNER = "test mapping (module -> test)", "crafts/syseng/rules/verifiable-code.md"
FIELDS = ("module", "test", "present")
EXEMPT = ("package.py",)                                   # the runner has no test file of its own name (test_package.py tests it as the CLI)
CRAFT_CODE = ("scripts", "projectors")                     # a craft's non-guard code directories, mapped flat to tests/
COMPONENT_TESTS = "tests"                                 # the directory a component holds that makes it one (the component clause, #336)
NOT_A_KIND = ("tests",)                                   # a `<kind>` level that never holds components: a tests tree is a tests tree

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-in-order", lambda: FIELDS == ("module", "test", "present")),
    ("craft-code-dirs-distinct", lambda: len(set(CRAFT_CODE)) == len(CRAFT_CODE) and "guards" not in CRAFT_CODE),
    ("component-tests-dir-is-tests", lambda: COMPONENT_TESTS == "tests" and COMPONENT_TESTS in NOT_A_KIND),
]

# ---- the component clause
def components(pkg: Path = dyadlib.PKG) -> list[Path]:
    """Every component directory: `dyad/<kind>/<component>/` then `crafts/<craft>/<kind>/<component>/`, each
    holding its own `tests/` directory; `<kind>` never one of NOT_A_KIND; sorted within each root."""
    def under(root: Path, depth: str) -> list[Path]:
        if not root.is_dir():
            return []
        found = (d.parent for d in root.glob(f"{depth}/{COMPONENT_TESTS}") if d.is_dir())
        return sorted(c for c in found if c.parent.name not in NOT_A_KIND and "__pycache__" not in c.parts)
    return under(pkg, "*/*") + under(dyadlib.crafts_dir(pkg), "*/*/*")

def component_of(py: Path, pkg: Path = dyadlib.PKG) -> Path | None:
    """The component directory a module belongs to — `dyad/<kind>/<component>/` or
    `crafts/<craft>/<kind>/<component>/`, holding `tests/` — or None for a flat-mapped module or a test."""
    for root, depth in ((pkg, 2), (dyadlib.crafts_dir(pkg), 3)):
        if py.is_relative_to(root) and len(py.relative_to(root).parts) > depth:   # <kind>/<component>/<file> at least
            parts = py.relative_to(root).parts
            comp = root.joinpath(*parts[:depth])
            if parts[depth - 2] not in NOT_A_KIND and parts[depth] != COMPONENT_TESTS and (comp / COMPONENT_TESTS).is_dir():
                return comp
    return None

def component_modules(comp: Path) -> list[Path]:
    """Every `*.py` of one component outside its `tests/`, sub-packages included, sorted; `_`-prefixed names (so
    `__init__.py`) dropped as everywhere in this mapping."""
    return sorted(p for p in comp.rglob("*.py")
                  if COMPONENT_TESTS not in p.relative_to(comp).parts and "__pycache__" not in p.parts and not p.name.startswith("_"))

def collisions(pkg: Path = dyadlib.PKG) -> list[str]:
    """One message per stem two modules of one component share across its sub-packages: both would map to the
    same `tests/test_<stem>.py`, so the mapping could not tell their tests apart (fail)."""
    root, msgs = pkg.parent, []
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    for comp in components(pkg):
        by_stem: dict[str, list[Path]] = {}
        for m in component_modules(comp):
            by_stem.setdefault(m.stem, []).append(m)
        for stem, ms in sorted(by_stem.items()):
            if len(ms) > 1:
                msgs.append(f"{rel(comp)}: modules {', '.join(rel(m) for m in ms)} share the stem {stem!r}: "
                            f"both map to {rel(comp / COMPONENT_TESTS / f'test_{stem}.py')} (verifiable-code.md p4, the component clause)")
    return msgs

def test_for(py: Path, pkg: Path = dyadlib.PKG) -> Path:
    """The test path the mapping assigns to a module of the core (`pkg`) or of a craft under `crafts_dir(pkg)`;
    a component's module (the component clause) maps to `<component>/tests/test_<stem>.py`."""
    comp = component_of(py, pkg)
    if comp is not None:
        return comp / COMPONENT_TESTS / f"test_{py.stem}.py"
    if py.is_relative_to(pkg):
        rel = py.relative_to(pkg)
        if rel.parts[0] == "guards":
            return pkg / "tests" / "guards" / rel.parts[1] / f"test_{py.stem}.py"
        return pkg / "tests" / f"test_{py.stem}.py"
    base = py.parents[1]                                  # crafts/<craft>/{guards,scripts,projectors}/<n>.py
    return base / "tests" / ("guards" if py.parent.name == "guards" else "") / f"test_{py.stem}.py"

def modules(pkg: Path = dyadlib.PKG) -> list[Path]:
    """Every mapped module: core scripts, core and craft guards, craft scripts and projectors (flat), then every
    component's modules (the component clause); sorted within each group, exemptions dropped."""
    craft = [p for d in CRAFT_CODE for p in dyadlib.craft_glob(f"{d}/*.py", pkg)]
    comp = [p for c in components(pkg) for p in component_modules(c)]
    out = sorted((pkg / "scripts").glob("*.py")) + dyadlib.guard_files(pkg) + sorted(craft) + comp
    return [p for p in out if p.name not in EXEMPT and not p.name.startswith("_")]

def mapping(pkg: Path = dyadlib.PKG) -> list[dict]:
    root = pkg.parent
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    return [{"module": rel(m), "test": rel(test_for(m, pkg)), "present": test_for(m, pkg).exists()} for m in modules(pkg)]

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return [f"{m['module']}: no {m['test']} (verifiable-code.md p4)" for m in mapping(pkg) if not m["present"]] + collisions(pkg)

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    ms = mapping(pkg)
    return f"{len(ms)} modules mapped, {sum(m['present'] for m in ms)} tests present, {len(components(pkg))} components"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ms = mapping(pkg); ex = ms[0] if ms else {}
    return {"store": "dyad/scripts/, dyad/guards/<corpus>/, crafts/<craft>/{guards,scripts,projectors}/ -> the tests/ trees; a component (`dyad/<kind>/<component>/`, `crafts/<craft>/<kind>/<component>/`, holding `tests/`) -> its own tests/", "parser": "`tests.mapping` (`tests.test_for`, `tests.components`)",
            "observed": len(ms), "note": "one-way: every module has its test at the mapped path; extra tests are legal; a component's modules map to its own tests/ by stem, a shared stem fails; the runner runs the suites (check_rule_12)",
            "fields": [("module", "path", "a Python file of the core or a craft, `package.py` and `_`-prefixed exempt", True, ex.get("module", ""), "tests.FIELDS"),
                       ("test", "path", "the mapped test file", True, ex.get("test", ""), "tests.FIELDS"),
                       ("present", "bool", "the test file exists", True, str(ex.get("present", "")).lower(), "tests.FIELDS")]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"FAIL [tests] {m}", file=sys.stderr)
    if not msgs:
        print(f"ok   [tests] {summary(root)}")
    return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
