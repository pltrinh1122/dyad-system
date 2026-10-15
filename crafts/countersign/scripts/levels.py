#!/usr/bin/env python3
"""Test-level check (a countersign craft script, not a guard: the craft's `rules/self-diagnostic.md` §6 owns the
classification; placed as `crafts/disclosure/scripts/redaction.py` is, an allowed craft child; d-work #308, for
countersign-system #3 D8; a guard until #308's plan revision 2, falsification D20). Kernel: Python 3.12+.
`<host>/self-diagnostic-levels.txt` (the host path, preference `host-path`, default `workstation-corpus`, #175;
instance; seeded from `crafts/countersign/templates/self-diagnostic-levels.txt`) classifies every test module of the
tree as `unit` or `integration`, the two coded levels of the self-diagnostic (L1 runs the first, L2 the second): one
`<level> <path>` per line, `path` repo-relative posix, a `#` comment (a whole line, or after whitespace) and a blank
line carrying nothing; the file is read as UTF-8, a leading BOM dropped, and one that does not decode is one
failure, never an exception. The granularity is the module. The test modules of a tree are every `test_*.py` under
the runner's test roots — `dyad/tests/` and every `crafts/<craft>/tests/` present, the roots `package.test_suites()`
returns (`test-roots-are-the-runners`, a TREE_INVARIANT, holds the two lists of roots equal on the live tree). The
roots are the runner's; within them the module set is every `test_*.py`, which is what `unittest discover` runs only
where the syseng craft's naming guard keeps the two equal (no non-`test_` module named `test*.py`, no test module
outside a package): where that craft is not installed — countersign-system — a `testhelpers.py` the suite runs goes
unlisted, and a `test_*.py` in a directory with no `__init__.py`, which discover never runs, must still be placed.
Fails on: a malformed line, a level outside LEVELS, a path not shaped `.../test_*.py`, a path listed twice, an entry
naming no test module of the tree (stale), and a test module present but unclassified. The craft's own seed is
checked for form only (it is classified against the tree that authors it, never against the tree it is copied
into). An absent instance file passes with nothing to judge, so a system that keeps none (dyad-system) is
unaffected; `summary` and the command line say `skip` in one line.
Where it runs: where the partition is used — the run-book's `health` step runs the check, and its `unit` and
`integration` steps read the file through `list`, which refuses a file that fails — and nowhere else. No runner
discovers a script, so it never runs on a push: a module added without its line is caught at the next run's
`health`, before any test runs. Nor does the runner's invariant pass or the craft guard's floor check load a script,
so the command line runs both invariant lists itself first (`self_check`); the craft's suite (`tests/test_levels.py`)
runs the pure list, the seed invariant and the seed's form wherever that suite runs: on every push of the repo that
authors the craft, but not at the push gate of a system that installed it unmodified, which may skip its test root
(dyad-system Rule-12 property 2) — there they run in L2's evidence run, which runs every root, and the invariants
again in `self_check`. Whether a module sits at the right
level — a module any of whose tests builds a scratch repo, runs git, installs or spawns the runner is `integration`
(rules/self-diagnostic.md) — is inference, stated; the seed records how it was observed.
  levels.py [repo-root]                           the check; one result line (FAIL lines on stderr)
  levels.py list <unit|integration> [repo-root]   that level's module paths, one per line, sorted; rc 1 when the
                                                  file fails the check, 2 when it is absent or the call is malformed
  Either form exits 1 first, judging nothing, when one of this script's own invariants is false.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("levels.py: Python 3.12+ required")
import re
from pathlib import Path, PurePosixPath
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/countersign/scripts/ -> dyad/scripts
import dyadlib

CRAFT = Path(__file__).resolve().parents[1]         # crafts/countersign: the seed sits in its templates/
FIELDS = ("level", "path")                          # one entry of the levels file, in line order
LEVELS = ("unit", "integration")                    # L1 runs the first, L2 the second (rules/self-diagnostic.md)
FILE = "self-diagnostic-levels.txt"                 # `<host>/FILE` (instance) and `templates/FILE` (the seed)
TEST_PREFIX, TEST_SUFFIX = "test_", ".py"           # a test module's name, inside unittest discover's `test*.py`
CORE = "dyad"                                       # the core craft's root; its `tests/` is the first test root
CORE_SYMBOLS = ("host_path", "repo_root", "craft_glob", "runner_module")   # what this script's checks call in the
                                                    # core's dyadlib (beside `dyadlib.PKG`, read by a tree invariant
                                                    # only). Outside the list: `check_invariants` and `InvariantError`,
                                                    # which `self_check` uses to run the list itself, so a core lacking
                                                    # them fails there before any invariant could name them; both are
                                                    # at the floor tag (`label` included) and in countersign-system's core
EXIT_ABSENT = 2                                     # `list` with no file, or a malformed call: nothing listed, no verdict
_COMMENT = re.compile(r"(^|\s)#.*$")

def parse_line(line: str) -> tuple[str, ...]:
    """The fields of one line, its comment and surrounding whitespace dropped; () for a blank or comment line."""
    return tuple(_COMMENT.sub("", line).split())

def is_test_name(name: str) -> bool:
    """A test module's file name, `test_*.py` — the one predicate `path_ok` and `test_modules` share, so a name the
    tree counts is a name an entry may carry (`test_.py` included: the glob's `*` matches nothing)."""
    return name.startswith(TEST_PREFIX) and name.endswith(TEST_SUFFIX)

def path_ok(path: str) -> bool:
    """`path` is repo-relative posix in canonical form (no `/` lead, no `.` or `..` part, no `\\`) and names a
    `test_*.py` file. Shape only: whether the tree holds that module is `check_text`'s question."""
    p = PurePosixPath(path)
    return (bool(path) and "\\" not in path and not p.is_absolute() and p.as_posix() == path
            and not any(part in (".", "..") for part in p.parts) and is_test_name(p.name))

# crafts/syseng/rules/invariants.md p1. Pure: this module's literals and its own pure functions, plus one read of
# an attribute of the already-imported dyadlib (no file, git, environment or module load). Not passed to
# `dyadlib.enforce` at import, as no Tended craft module does yet (the syseng guard's per-craft warning, "a craft
# follow-up"): the core countersign-system runs (`dyad/VERSION` 0.10.1, labelled before this repo's
# `dyad-operator-v0.10.1` tag was cut, #249; plan 3 D10) ships no `enforce`, and a call to it would stop this
# script loading there. No runner's pass covers a script and the craft guard's floor check loads only a craft's
# guards and projectors, so `core-provides-the-symbols-this-script-calls` — false on any core older than
# `host_path` (0.10.0) — is checked where the script runs (`self_check`) and by the craft's suite, never at the
# `requires:` floor: the floor `dyad-operator>=0.10.1` is stated (MANIFEST.md, falsification D10).
INVARIANTS = [
    ("levels-are-two-distinct-lowercase-words", lambda: len(LEVELS) == 2 == len(set(LEVELS)) and all(l.isalpha() and l.islower() for l in LEVELS)),
    ("fields-are-level-then-path", lambda: FIELDS == ("level", "path")),
    ("a-line-parses-to-one-value-per-field", lambda: parse_line("unit dyad/tests/test_x.py  # why") == ("unit", "dyad/tests/test_x.py")
                                                    and len(parse_line("unit dyad/tests/test_x.py")) == len(FIELDS)),
    ("comments-and-blanks-carry-no-fields", lambda: parse_line("# integration dyad/tests/test_x.py") == () == parse_line("   ")),
    ("path-shape-takes-a-test-module-and-refuses-a-climb", lambda: path_ok("crafts/a/tests/guards/test_x.py") and not path_ok("../dyad/tests/test_x.py")
                                                                   and not path_ok("/dyad/tests/test_x.py") and not path_ok("dyad/tests/x.py")
                                                                   and not path_ok("./dyad/tests/test_x.py") and not path_ok("dyad\\tests\\test_x.py")),
    ("a-name-the-tree-counts-is-a-name-an-entry-may-carry", lambda: is_test_name("test_.py") and path_ok("dyad/tests/test_.py")
                                                                    and not is_test_name("testhelpers.py")),
    ("exit-absent-is-no-verdict", lambda: EXIT_ABSENT not in (0, 1)),
    ("core-provides-the-symbols-this-script-calls", lambda: all(callable(getattr(dyadlib, n, None)) for n in CORE_SYMBOLS)),
]
# Read the package tree, or load the runner (which starts git): never at import. The command line runs both with
# `INVARIANTS` before it judges anything (`self_check`), on either core; the craft's suite runs the seed's alone,
# since loading the runner would start git in a module the seed classifies `unit`.
TREE_INVARIANTS = [
    ("test-roots-are-the-runners", lambda: [p.resolve() for p in test_roots(dyadlib.PKG.parent)]
                                           == [p.resolve() for p in dyadlib.runner_module().test_suites()]),
    ("seed-template-exists", lambda: (CRAFT / "templates" / FILE).is_file()),
]

def levels_path(root: Path) -> Path:
    return Path(root) / dyadlib.host_path(Path(root)) / FILE   # the host path (preference `host-path`, #175)

def _rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix() if p.is_relative_to(root) else str(p)

def test_roots(root: Path) -> list[Path]:
    """`<root>/dyad/tests` then every `<root>/crafts/<craft>/tests`, sorted — `package.test_suites()` computed over
    `root` rather than over the running core, so a fixture tree is judged by its own roots."""
    pkg = Path(root) / CORE
    return [pkg / "tests"] + dyadlib.craft_glob("tests", pkg)

def test_modules(root: Path) -> list[str]:
    """Every `test_*.py` under the test roots, repo-relative posix, sorted; `__pycache__` below a root never holds
    one (judged below the root, so a repo inside a directory of that name loses nothing)."""
    root = Path(root); out = set()
    for d in test_roots(root):
        if d.is_dir():
            out.update(_rel(p, root) for p in d.rglob(f"{TEST_PREFIX}*{TEST_SUFFIX}")
                       if p.is_file() and is_test_name(p.name) and "__pycache__" not in p.relative_to(d).parts)
    return sorted(out)

def read(p: Path) -> str:
    """The levels file's text as UTF-8, a leading BOM dropped (a Windows editor writes one); bytes that do not
    decode raise UnicodeDecodeError, which `check_file` turns into one failure line."""
    return p.read_text(encoding="utf-8-sig")

def check_file(p: Path, where: str, modules: list[str] | None = None) -> list[str]:
    """`check_text` over the file at `p`; a file that is not UTF-8 is one failure, never an exception, so the
    check still prints its one result line and `list` still refuses with exit 1."""
    try:
        text = read(p)
    except UnicodeDecodeError as e:
        return [f"{where}: not UTF-8 (byte {e.start}: {e.reason})"]
    return check_text(text, where, modules)

def parse(text: str) -> tuple[list[tuple[int, str, str]], list[tuple[int, str]]]:
    """(entries, malformed): each line carrying fields is an entry `(line number, level, path)` when it has exactly
    two fields, else `(line number, raw line)` in malformed. Level and path are judged by `check_text`."""
    entries, malformed = [], []
    for n, line in enumerate(text.splitlines(), 1):
        f = parse_line(line)
        if not f:
            continue
        if len(f) == len(FIELDS):
            entries.append((n, f[0], f[1]))
        else:
            malformed.append((n, line.strip()))
    return entries, malformed

def check_text(text: str, where: str, modules: list[str] | None = None) -> list[str]:
    """Form (every line `<level> <path>`, the level in LEVELS, the path shaped, no path twice) and, when `modules`
    is given, completeness against them both ways: no entry names a path outside it, no module goes unclassified."""
    entries, malformed = parse(text); msgs = []
    msgs += [f"{where} line {n}: `{raw}` is not `<level> <path>`" for n, raw in malformed]
    first: dict[str, int] = {}
    for n, level, path in entries:
        if level not in LEVELS:
            msgs.append(f"{where} line {n}: level `{level}` is not one of {', '.join(LEVELS)}")
        if not path_ok(path):
            msgs.append(f"{where} line {n}: path `{path}` is not a repo-relative `{TEST_PREFIX}*{TEST_SUFFIX}` path"); continue
        if path in first:
            msgs.append(f"{where} line {n}: {path} already classified at line {first[path]}"); continue
        first[path] = n
    if modules is None:
        return msgs
    present = set(modules)
    msgs += [f"{where} line {n}: {p} names no test module of this tree (stale; test roots: {CORE}/tests/, crafts/<craft>/tests/)"
             for p, n in sorted(first.items(), key=lambda e: e[1]) if p not in present]
    msgs += [f"{where}: {m} is a test module this file does not classify (unit or integration)" for m in modules if m not in first]
    return msgs

def check_instance(root: Path) -> list[str]:
    """The instance file against the tree's test modules; [] when the file is absent (nothing to judge)."""
    root = Path(root); p = levels_path(root)
    return check_file(p, _rel(p, root), test_modules(root)) if p.is_file() else []

def check_package(root: Path | None = None, craft: Path | None = None) -> list[str]:
    """The seed's form (`craft`, default this craft) and the instance file of `root` (default the live repo)."""
    root = Path(root or dyadlib.repo_root())
    tmpl = Path(craft or CRAFT) / "templates" / FILE
    msgs = check_file(tmpl, f"templates/{FILE}") if tmpl.is_file() else []
    return msgs + check_instance(root)

def _entries(p: Path) -> list[tuple[int, str, str]]:
    """The entries of the file at `p`; none when it is absent or does not decode (`check_file` reports that)."""
    try:
        return parse(read(p))[0] if p.is_file() else []
    except UnicodeDecodeError:
        return []

def listing(root: Path, level: str) -> list[str]:
    """The paths the instance file places at `level`, sorted (the first entry of a path listed twice)."""
    seen: dict[str, str] = {}
    for _, lv, path in _entries(levels_path(root)):
        seen.setdefault(path, lv)
    return sorted(path for path, lv in seen.items() if lv == level)

def summary(root: Path | None = None) -> str:
    root = Path(root or dyadlib.repo_root()); p = levels_path(root)
    if not p.is_file():
        return f"skip: no {_rel(p, root)}"
    counts = {lv: len(listing(root, lv)) for lv in LEVELS}
    return f"{sum(counts.values())} modules: " + ", ".join(f"{n} {lv}" for lv, n in counts.items())

def self_check() -> list[str]:
    """Both invariant lists, run where this script runs, since no runner pass covers a script: the names of the
    false ones, sorted; [] when every one holds. A list is passed rather than the module, so a core whose
    `check_invariants` reads `INVARIANTS` only (countersign-system's) runs the tree list too."""
    try:
        dyadlib.check_invariants(list(INVARIANTS) + list(TREE_INVARIANTS), label="levels")
    except dyadlib.InvariantError as e:
        return list(e.failed)
    return []

def main(argv=None) -> int:
    a = list(argv if argv is not None else sys.argv[1:])
    if a and a[0] == "list":
        if len(a) not in (2, 3) or a[1] not in LEVELS:
            print(f"usage: levels.py list <{'|'.join(LEVELS)}> [repo-root]", file=sys.stderr)
            return EXIT_ABSENT
        root = Path(a[2]).resolve() if len(a) == 3 else dyadlib.repo_root()
        if not levels_path(root).is_file():
            print(f"skip [levels] no {_rel(levels_path(root), root)}", file=sys.stderr)
            return EXIT_ABSENT
        fails = [m for m in check_instance(root) if not m.startswith("warning:")]
        for m in fails:
            print(f"FAIL [levels] {m}", file=sys.stderr)
        if fails:
            return 1
        for path in listing(root, a[1]):
            print(path)
        return 0
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"FAIL [levels] {m}", file=sys.stderr)
    if msgs:
        return 1
    print(f"skip [levels] no {_rel(levels_path(root), root)}" if not levels_path(root).is_file() else f"ok   [levels] {summary(root)}")
    return 0

if __name__ == "__main__":
    bad = self_check()
    for name in bad:
        print(f"FAIL [invariant] levels: {name}", file=sys.stderr)
    sys.exit(1 if bad else main())
