#!/usr/bin/env python3
"""Test-mapping guard (entity `test`, corpus `craft`; the syseng craft's `rules/verifiable-code.md` p4 owns the mapping;
placed per crafts/sysarch/rules/guards.md under the craft's root; d-work #162). Kernel: Python 3.12+.
The mapping moved from the runner's `check_rule_12` (which keeps "run the tests"): `dyad/scripts/<n>.py` ->
`dyad/tests/test_<n>.py` (`package.py` and `_`-prefixed exempt); `dyad/guards/<c>/<e>.py` -> `dyad/tests/guards/<c>/test_<e>.py`;
`crafts/<craft>/guards/<e>.py` -> `crafts/<craft>/tests/guards/test_<e>.py`; `crafts/<craft>/projectors/<n>.py` and
`crafts/<craft>/scripts/<n>.py` -> `crafts/<craft>/tests/test_<n>.py`. A module without its test at the mapped path fails.
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

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-in-order", lambda: FIELDS == ("module", "test", "present")),
    ("craft-code-dirs-distinct", lambda: len(set(CRAFT_CODE)) == len(CRAFT_CODE) and "guards" not in CRAFT_CODE),
]

def test_for(py: Path, pkg: Path = dyadlib.PKG) -> Path:
    """The test path the mapping assigns to a module of the core (`pkg`) or of a craft under `crafts_dir(pkg)`."""
    if py.is_relative_to(pkg):
        rel = py.relative_to(pkg)
        if rel.parts[0] == "guards":
            return pkg / "tests" / "guards" / rel.parts[1] / f"test_{py.stem}.py"
        return pkg / "tests" / f"test_{py.stem}.py"
    base = py.parents[1]                                  # crafts/<craft>/{guards,scripts,projectors}/<n>.py
    return base / "tests" / ("guards" if py.parent.name == "guards" else "") / f"test_{py.stem}.py"

def modules(pkg: Path = dyadlib.PKG) -> list[Path]:
    """Every mapped module: core scripts, core and craft guards, craft scripts and projectors; sorted, exemptions dropped."""
    craft = [p for d in CRAFT_CODE for p in dyadlib.craft_glob(f"{d}/*.py", pkg)]
    out = sorted((pkg / "scripts").glob("*.py")) + dyadlib.guard_files(pkg) + sorted(craft)
    return [p for p in out if p.name not in EXEMPT and not p.name.startswith("_")]

def mapping(pkg: Path = dyadlib.PKG) -> list[dict]:
    root = pkg.parent
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    return [{"module": rel(m), "test": rel(test_for(m, pkg)), "present": test_for(m, pkg).exists()} for m in modules(pkg)]

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return [f"{m['module']}: no {m['test']} (verifiable-code.md p4)" for m in mapping(pkg) if not m["present"]]

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    ms = mapping(pkg)
    return f"{len(ms)} modules mapped, {sum(m['present'] for m in ms)} tests present"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ms = mapping(pkg); ex = ms[0] if ms else {}
    return {"store": "dyad/scripts/, dyad/guards/<corpus>/, crafts/<craft>/{guards,scripts,projectors}/ -> the tests/ trees", "parser": "`tests.mapping` (`tests.test_for`)",
            "observed": len(ms), "note": "one-way: every module has its test at the mapped path; extra tests are legal; the runner runs the suites (check_rule_12)",
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
