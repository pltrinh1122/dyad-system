#!/usr/bin/env python3
"""<Module> (<what it holds>; crafts/syseng/rules/invariants.md). Kernel: Python 3.12+.
One paragraph: the data model this module carries (its upper-case constants) and who reads it.
  <module>.py [args]

Skeleton of a model module. Copy to dyad/scripts/<module>.py, crafts/<craft>/scripts/<module>.py or a
projector/guard, write its test from crafts/syseng/templates/test.py, and add the module to the runner's
pass (package.invariant_modules) if the discovery order does not already reach it.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("<module>.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))   # adjust to reach dyad/scripts
import dyadlib

# ---- the data model: upper-case constants, literals (a tuple, dict, set, frozenset), never mutated
STATES = frozenset({"a", "b"})
TRANSITIONS: dict[str, frozenset[str]] = {"a": frozenset({"b"}), "b": frozenset()}

# ---- crafts/syseng/rules/invariants.md p1: the architectural facts the constants encode, one predicate each,
# named in words, sorted and run by dyadlib.check_invariants — by the runner's pass and before any write below.
# Never `assert` (p3); never run at import.
INVARIANTS: list[dyadlib.Invariant] = [
    ("transitions-keys-are-states", lambda: set(TRANSITIONS) == STATES),
    ("transition-targets-are-states", lambda: all(t <= STATES for t in TRANSITIONS.values())),
]

def write(path: Path, text: str) -> None:
    """A mutating call site: check the model before the write (p1); an InvariantError is an incident (p5)."""
    dyadlib.check_invariants(INVARIANTS, label="<module>")
    path.write_text(text)

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    return 0

if __name__ == "__main__":
    sys.exit(main())
