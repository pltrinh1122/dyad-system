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
TEMPLATE = Path(__file__).resolve().parent / "<module>.txt"

# ---- crafts/syseng/rules/invariants.md p1: the architectural facts the constants encode, one predicate each,
# named in words, unique across both lists. Never `assert` (p3).
# INVARIANTS: pure — over this module's literals only (no file, stat, git, environment, module load), so the same
# value on every host. Enforced at import by the call below, with no off-switch; a false one raises InvariantError.
INVARIANTS: list[dyadlib.Invariant] = [
    ("transitions-keys-are-states", lambda: set(TRANSITIONS) == STATES),
    ("transition-targets-are-states", lambda: all(t <= STATES for t in TRANSITIONS.values())),
]
# TREE_INVARIANTS: read the package tree or load modules; never at import — the runner's pass runs them.
TREE_INVARIANTS: list[dyadlib.Invariant] = [
    ("template-exists", lambda: TEMPLATE.is_file()),
]
dyadlib.enforce(INVARIANTS, __name__)   # after the list's last binding; the syseng guard checks it is here (iv)

class TransitionError(ValueError):
    """Operator input asked for a transition the table does not hold."""

def require_transition(before: str, after: str) -> None:
    """A fail-loud check at a strategic point (invariants.md p1): a state transition, checked once per disposition,
    in one function called from one place — before the one write. Never on the read path or per row."""
    if after not in TRANSITIONS.get(before, frozenset()):
        raise TransitionError(f"{before} -> {after} is not a transition (states: {', '.join(sorted(STATES))})")

def write_state(path: Path, before: str, after: str) -> None:
    """The one write: refused before anything is written, by construction."""
    require_transition(before, after)
    path.write_text(after + "\n")

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    return 0

if __name__ == "__main__":
    sys.exit(main())
