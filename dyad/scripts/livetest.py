#!/usr/bin/env python3
"""Live-test support (crafts/syseng/rules/verifiable-code.md p6; d-work #171). Kernel: Python 3.12+, stdlib
only (Rule-14: no new row).

A *live test* reads the system it runs in — the instance's stores, and the Tended crafts installed beside the
core craft — instead of a fixture it builds. A fresh install has neither: its instance is empty and a core-only
install has no craft. A live test that asserts this workstation's shape therefore fails in every scratch
install, which is why `dyad check` has never been green in one (recorded as pre-existing by #151, #155, #160,
#162). This module is the one place a live test states that case, so the statement is written once and reads
the same everywhere:

  - `store_empty` / `instance_is_empty` — ask, then assert the *documented* empty behaviour. Preferred
    wherever the code documents one (`dyad ledger` renders a header-only view; the events projector renders
    "No events recorded yet"; the ERD omits the section of a kind with no entity): asserting it tests more
    than skipping does, and costs a line.
  - `LiveCase.require_store` / `require_instance` / `require_craft` / `require_guard` — skip with a stated
    reason when there is no documented behaviour to assert. `unittest` prints the reason and counts the skip,
    so the runner's per-suite line (`Ran N tests ... OK (skipped=k)`, `check_rule_12`) shows how much of a
    suite an empty instance turned off.

What a live test proves is that *this* instance parses and that the projectors and guards run over it. What
the code does is proved by the fixture tests beside it, which build their own corpus and run everywhere. A
skip here therefore removes no coverage of the logic — only of this instance's data.

The module also holds the fixture for the other side of the same question: a *fresh* install (#163, d-work
#199 N3a). Rule-13 wants one place for it, so it was lifted from `test_craft.py` rather than copied into
`test_package.py`:

  - `ScratchInstalls` — one per test module. `copy(with_craft)` returns an independent scratch repo holding
    the core craft, installed by the real install path (`package.py install`) and committed. With
    `with_craft`, every Tended craft of this tree is copied in beside it. The install runs once per variant
    per module run (the *template*). Each copy has the template's bytes, modes, index and commit, with new
    inodes and mtimes and its index re-stat'ed clean, so every copy of one variant shares one HEAD sha.
    `mkdtemp` tracks any other scratch dir. `cleanup` removes them all; it is the module's
    `tearDownModule`, with `atexit` as the backstop.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit(f"livetest.py: Python 3.12+ required (kernel pin), found {sys.version.split()[0]}")
import atexit, shutil, subprocess, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import dyadlib

EMPTY = "empty instance"       # every empty-store skip reason begins with this
ABSENT = "absent craft"        # every craft-absent skip reason begins with this
REASONS = (EMPTY, ABSENT)
ROW_GLOB = "[0-9]*.md"         # a row or plan file is named by its d-work id; README.md and VERSION are install seeds
VARIANTS = (False, True)       # ScratchInstalls: core only, or core plus every Tended craft of this tree
IDENTITY = ("-c", "user.name=t", "-c", "user.email=t@t")   # the committer of a scratch install's one commit

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("reasons-distinct", lambda: len(set(REASONS)) == len(REASONS)),
    ("reasons-non-empty", lambda: all(isinstance(r, str) and r for r in REASONS)),
    ("row-glob-excludes-seeds", lambda: not any(Path(n).match(ROW_GLOB) for n in ("README.md", "VERSION"))),
    ("variants-are-the-two-booleans", lambda: VARIANTS == (False, True)),
]


def store_files(*paths, pattern: str = "*") -> list[Path]:
    """Every file matching `pattern` directly under each directory of `paths` (a path that is itself a file
    counts as one), sorted. A path that does not exist contributes nothing: for a live test an absent store
    and an empty one are the same case."""
    out: list[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            out += [f for f in p.glob(pattern) if f.is_file()]
        elif p.is_file():
            out.append(p)
    return sorted(out)


def store_empty(*paths, pattern: str = "*") -> bool:
    """True when `store_files` finds nothing — the condition a live test states its behaviour for."""
    return not store_files(*paths, pattern=pattern)


def instance_is_empty(root: Path | None = None) -> bool:
    """True when no d-work has been opened in this instance: `<instance>/d-work/rows/<id>.md` and
    `<instance>/d-work/plans/<id>.md` are both empty of id files (the `rows/README.md` and `d-work/VERSION`
    an install seeds are not rows). Every instance entity a projection draws — Row, Plan — comes from them."""
    inst = dyadlib.instance(root)
    return store_empty(dyadlib.rows_dir(root), inst / "d-work" / "plans", pattern=ROW_GLOB)


def crafts_installed(pkg: Path | None = None) -> list[str]:
    """The Tended crafts installed beside the core craft, by name, sorted (empty on a core-only install)."""
    return [p.name for p in dyadlib.craft_dirs(pkg or dyadlib.PKG)]


def craft_installed(name: str, pkg: Path | None = None) -> bool:
    return name in crafts_installed(pkg)


class LiveCase(unittest.TestCase):
    """Base class for a test that reads the system it runs in — the instance's stores, or which Tended crafts
    are installed beside the core. Every such test states what it does when that store is empty or the craft
    is absent: it asserts the documented behaviour, or calls one of the `require_*` methods below and is
    skipped with the reason printed and counted. A test that builds its own fixture needs none of this."""

    def require_store(self, what: str, *paths, pattern: str = "*") -> list[Path]:
        """The files of the store, or skip: `<EMPTY>: no <what> in this instance`."""
        found = store_files(*paths, pattern=pattern)
        if not found:
            self.skipTest(f"{EMPTY}: no {what} in this instance")
        return found

    def require_instance(self) -> None:
        """Skip when no d-work has been opened here (`instance_is_empty`)."""
        if instance_is_empty():
            self.skipTest(f"{EMPTY}: no d-work row or plan in this instance")

    def require_craft(self, *names: str) -> None:
        """Skip unless every named Tended craft is installed beside the core craft."""
        missing = [n for n in names if not craft_installed(n)]
        if missing:
            self.skipTest(f"{ABSENT}: {', '.join(missing)} not installed (crafts/)")

    def require_guard(self, corpus: str, entity: str):
        """The guard module for one entity kind, or skip when no installed craft provides it (#155)."""
        mod = dyadlib.find_guard(corpus, entity)
        if mod is None:
            self.skipTest(f"{ABSENT}: no installed craft provides guard {corpus}/{entity}")
        return mod


class ScratchInstalls:
    """A test module's scratch installs (#163, d-work #199 N3a), lifted from `test_craft.py` (#138). The real
    install runs once per variant per module run, and every case gets its own copy of it, so a module pays one
    `package.py install` per variant instead of one per case. The template is read only inside `copy`, never
    returned or written. Every dir made here is registered before it is filled, so `cleanup` removes it even
    when a test fails. `cleanup` is idempotent and is also registered with `atexit`."""

    def __init__(self, pkg: Path | None = None):
        self.pkg = Path(pkg or dyadlib.PKG)
        self.templates: dict[bool, Path] = {}
        self.made: list[Path] = []
        atexit.register(self.cleanup)   # backstop for an interrupt or an importer outside unittest

    def mkdtemp(self, prefix: str | None = None) -> Path:
        """A new empty scratch dir, removed by `cleanup`."""
        d = Path(tempfile.mkdtemp(prefix=prefix)); self.made.append(d)
        return d

    def _git(self, d: Path, *a: str) -> str:
        r = subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, env=dyadlib.git_env())
        if r.returncode:
            raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
        return r.stdout

    def install(self, with_craft: bool = False, prefix: str | None = None) -> Path:
        """The real install path: `git init`, then `package.py install` of this tree's core craft. With
        `with_craft`, every `crafts/<craft>/` of this tree and its `REGISTRY.md` are copied over it. Then one
        commit. `install` has already written every *bundled* craft (Rule-11 p2). Its files are a subset of the
        tree copied, so the copy leaves exactly this tree's crafts."""
        d = self.mkdtemp(prefix=prefix); self._git(d, "init", "-q")
        r = subprocess.run([sys.executable, str(self.pkg / "scripts" / "package.py"), "install", str(d)],
                           capture_output=True, text=True, env=dyadlib.git_env())
        if r.returncode:
            raise RuntimeError(f"package.py install {d}: {r.stdout}{r.stderr}")
        if with_craft:
            for c in dyadlib.craft_dirs(self.pkg):
                shutil.copytree(c, d / "crafts" / c.name, ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
            reg = dyadlib.crafts_dir(self.pkg) / "REGISTRY.md"   # the craft zone's instance state (#156)
            if reg.is_file():
                shutil.copy(reg, d / "crafts" / "REGISTRY.md")
        self._git(d, "add", "-A"); self._git(d, *IDENTITY, "commit", "-qm", "scratch")
        return d

    def copy(self, with_craft: bool = False) -> Path:
        """An independent copy of this module's one install of the variant, made on first use. Its index is
        re-stat'ed (`update-index --refresh`), which fails on any content difference, so the copy starts clean."""
        if with_craft not in VARIANTS:
            raise ValueError(f"with_craft must be one of {VARIANTS}, not {with_craft!r}")
        if with_craft not in self.templates:
            self.templates[with_craft] = self.install(with_craft, prefix="dyad-scratch-template-")
        d = self.mkdtemp()
        shutil.copytree(self.templates[with_craft], d, copy_function=shutil.copy, dirs_exist_ok=True)   # modes kept; mtimes new
        self._git(d, "update-index", "--refresh")   # no -q: -q would continue past a stale entry
        return d

    def cleanup(self) -> None:
        """Remove every dir this instance made, templates included."""
        for d in self.made:
            shutil.rmtree(d, ignore_errors=True)
        self.made.clear(); self.templates.clear()

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)
