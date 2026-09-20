#!/usr/bin/env python3
"""Projector-registry guard (entity `projector`, corpus `craft`; the sysarch craft's one guard — its rules
`projection.md` p2/p4 and `references.md` Leaves own the check; placed per `guards.md`, a Tended craft's
guard under `crafts/sysarch/guards/`; d-work #160). Kernel: Python 3.12+.
Checks the craft's artifacts, never the core's: every `crafts/*/projectors/project_<surface>.py` has its
test `crafts/<craft>/tests/test_project_<surface>.py` and defines `main` (fail); no surface is provided by
two crafts (fail; the runner's discovery refuses it too); every core guard's `ENTITY` occurs in the
reference register (`references.REFERENCES`) as a source or a target, or is listed as a leaf in
`crafts/sysarch/rules/references.md` under `## Leaves` (fail). Whether a projector hand-draws, and
whether a leaf is rightly a leaf, stays inference (`projection.md`, `references.md`).
  registry.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("registry.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/sysarch/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "projector", "craft", False
NAME, OWNER = "projector (registry entry)", "crafts/sysarch/rules/projection.md"
FIELDS = ("surface", "craft", "module", "test")
INVARIANTS = [("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS) and FIELDS[0] == "surface")]   # crafts/syseng/rules/invariants.md
LEAVES_RULE = Path(__file__).resolve().parents[1] / "rules" / "references.md"
_MAIN = re.compile(r"^def main\(", re.M)
_TICK = re.compile(r"`([a-z_]+)`")

def projectors(root: Path, pkg: Path | None = None) -> list[dict]:
    """Every `crafts/<craft>/projectors/project_<surface>.py` under `root`, via `dyadlib.projector_files`
    — the one shared, parameterized discovery primitive the core runner's own registry
    (`package.projectors()`) also calls — as {surface, craft, module, test}. Craft/surface is
    collision-free by construction (D3, #100/#99), so this craft's own duplicate "one craft per
    surface" check (independently re-derived, the bug the report found) is retired: nothing left
    to enforce twice. `pkg` defaults to `<root>/dyad`, the core craft's conventional location."""
    root = Path(root); pkg = Path(pkg) if pkg is not None else root / "dyad"
    out = []
    for py in dyadlib.projector_files(pkg):
        craft, surface = py.parents[1].name, py.stem.removeprefix("project_")
        test = py.parents[1] / "tests" / f"test_{py.stem}.py"
        out.append({"surface": surface, "craft": craft, "module": str(py.relative_to(root)), "test": str(test.relative_to(root))})
    return out

def leaves(rule: Path = LEAVES_RULE) -> set[str]:
    """Backticked entity keys under `## Leaves` of references.md; empty when the rule or the section is absent."""
    if not rule.exists():
        return set()
    text = rule.read_text()
    m = re.search(r"^## Leaves\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return set(_TICK.findall(m.group(1))) if m else set()

def check_projectors(root: Path, entries: list[dict]) -> list[str]:
    """Test present, main defined. No collision check: craft/surface is collision-free by
    construction (D3, #100/#99) — the core registry's own key, not re-derived here."""
    root = Path(root); fails = []
    for e in entries:
        if not (root / e["test"]).exists():
            fails.append(f"{e['module']}: no {e['test']} (projection.md p2)")
        if not _MAIN.search((root / e["module"]).read_text(errors="ignore")):
            fails.append(f"{e['module']}: defines no main() (projection.md p4)")
    return fails

def check_entities(entities: dict[str, str], referenced: set[str], leaf: set[str]) -> list[str]:
    """`entities`: {ENTITY: guard path} of the core guards; `referenced`: every source and target key of the
    register; `leaf`: the keys references.md lists. An entity in neither is unreachable on the entities surface."""
    return [f"{path}: entity {ent!r} is neither a source nor a target in references.REFERENCES nor a leaf in crafts/sysarch/rules/references.md"
            for ent, path in sorted(entities.items()) if ent not in referenced and ent not in leaf]

def core_entities(pkg: Path) -> dict[str, str]:
    out = {}
    for py in dyadlib.guard_files(pkg):
        if dyadlib.guard_key(py, pkg)[0] == "core":
            out[dyadlib.load_guard_file(py, pkg).ENTITY] = str(py.relative_to(pkg.parent))
    return out

def referenced_keys(pkg: Path) -> set[str]:
    refs = dyadlib.load_guard("agent", "references", pkg).REFERENCES
    return {r[1] for r in refs} | {r[4] for r in refs}

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = Path(root or dyadlib.repo_root())
    fails = check_projectors(root, projectors(root, pkg))
    try:
        fails += check_entities(core_entities(pkg), referenced_keys(pkg), leaves())
    except FileNotFoundError as e:   # no core guards / no reference guard under pkg: nothing to check
        fails.append(f"warning: entity check skipped: {e}")
    return fails

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    ps = projectors(Path(root or dyadlib.repo_root()), pkg)
    return f"{len(ps)} projectors in {len({p['craft'] for p in ps})} craft(s)"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ps = projectors(root, pkg); ex = ps[0] if ps else {}
    return {"store": "crafts/<craft>/projectors/project_<surface>.py", "parser": "`registry.projectors`", "observed": len(ps),
            "note": "one entry per projector file, discovered; test present, main defined, one craft per surface; core entities reachable on the entities surface or listed as leaves",
            "fields": [("surface", "text", "the name after `project_`; `dyad project <surface>`", True, ex.get("surface", ""), "registry.FIELDS"),
                       ("craft", "text", "the craft whose `projectors/` holds it", True, ex.get("craft", ""), "registry.FIELDS"),
                       ("module", "path", "repo-relative path of the projector", True, ex.get("module", ""), "registry.FIELDS"),
                       ("test", "path", "`crafts/<craft>/tests/test_project_<surface>.py`, must exist", True, ex.get("test", ""), "registry.FIELDS")]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"):
            print(f"warn [registry] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [registry] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [registry] {summary(root)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
