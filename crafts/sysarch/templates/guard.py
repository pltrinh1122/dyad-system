#!/usr/bin/env python3
"""<Entity> guard (entity `<entity>`, corpus `<corpus>`; <owning Rule> owns the check; placed per
crafts/sysarch/rules/guards.md). Kernel: Python 3.12+.
One paragraph: what this guard checks (fail), what it warns on, and what it leaves to inference.
  <entity>.py [repo-root]

Skeleton of the guard contract (crafts/sysarch/rules/guards.md property 3; one definition:
dyadlib.CONTRACT). Copy to dyad/guards/<corpus>/<entity>.py (core) or crafts/<craft>/guards/<entity>.py
(a Tended craft; CORPUS is then the zone of the entity's store) and write its test at
dyad/tests/guards/<corpus>/test_<entity>.py or crafts/<craft>/tests/guards/test_<entity>.py.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("<entity>.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))          # core: dyad/guards/<corpus>/ -> dyad/scripts
# a craft guard instead: sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "<entity>", "<corpus>", False   # TRANSACTION True adds check_transaction below
NAME, OWNER = "<entity, as the entities surface names it>", "<Rule-N or the craft rule>"
FIELDS = ("<field-a>", "<field-b>")                              # the entity's parsed fields, in order
INVARIANTS = [("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS))]   # crafts/syseng/rules/invariants.md: the facts the constants encode; the runner's pass runs them

def parse(path: Path) -> dict:
    """The entity's parser: one instance -> its FIELDS. Other guards and projectors import this
    (`dyadlib.load_guard`) rather than re-parsing."""
    return {}

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Bare lines fail; lines starting `warning:` warn. An absent or empty store is a skip line, never a failure."""
    root = Path(root or dyadlib.repo_root())
    return []

# def check_transaction(root: Path, base: str, head: str) -> list[str]:
#     """When TRANSACTION: what `base..head` may not do to the store (append-only, immutable ids, ...)."""
#     return []

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return "0 <entities>"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    """The entity card (crafts/sysarch/templates/entity-card.md): store, parser, observed, note, and one
    row per FIELDS entry, in FIELDS order, then any derived field."""
    return {"store": "<path pattern>", "parser": "`<entity>.parse`", "observed": 0, "note": "",
            "fields": [(f, "text", "<meaning>", True, "<example>", f"{ENTITY}.FIELDS") for f in FIELDS]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        print(f"FAIL [{ENTITY}] {m}" if not m.startswith("warning:") else f"warn [{ENTITY}] {m.removeprefix('warning:').strip()}", file=sys.stderr if not m.startswith("warning:") else sys.stdout)
    if not fails:
        print(f"ok   [{ENTITY}] {summary(root)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
