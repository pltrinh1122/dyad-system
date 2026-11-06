"""dyad package: shared path resolution, ledger and Rule parsing, and the guard registry loader over two
roots — the core craft's `dyad/guards/` and every Tended craft's `crafts/<craft>/guards/` (Rule-11 property 3;
crafts/sysarch/rules/guards.md; #155). Owns no check semantics (S4). Kernel: Python 3.12+."""
import datetime, importlib.util, os, re, subprocess, sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Callable

PKG = Path(__file__).resolve().parent.parent
GUARDS = PKG / "guards"
CORE_LIBRARY = "dyad/scripts"   # surface S9 (#612): the repo path every Tended craft guard puts on sys.path for the core's modules
CRAFT_LAYOUT = ("VERSION", "guards", "tests", "vocabulary/CRAFT.md")   # surface S9 (#612): what makes crafts/<craft>/ a craft, its
                                                                     # guards and tests roots, and its vocabulary

# ---- guards (crafts/sysarch/rules/guards.md): dyad/guards/<corpus>/<entity>.py (core) and crafts/<craft>/guards/<entity>.py (a
# Tended craft's, #155), one module per entity kind, loaded by path
def crafts_dir(pkg: Path = PKG) -> Path:
    """The Tended crafts' root, `crafts/` beside the core craft's `dyad/` (Rule-11; absent on a core-only install)."""
    return pkg.parent / "crafts"

def craft_glob(pattern: str, pkg: Path = PKG) -> list[Path]:
    """Every `crafts/<craft>/<pattern>` that exists, sorted; empty when no craft is installed."""
    d = crafts_dir(pkg)
    return sorted(d.glob(f"*/{pattern}")) if d.is_dir() else []

def guard_files(pkg: Path = PKG) -> list[Path]:
    """Every guard module: the core root sorted by corpus then entity, then every craft root sorted by
    craft then entity; names starting `_` are not guards (crafts/sysarch/rules/guards.md p4, two roots)."""
    core = sorted(p for p in (pkg / "guards").glob("*/*.py") if not p.name.startswith("_"))
    craft = [p for p in craft_glob(f"{CRAFT_LAYOUT[1]}/*.py", pkg) if not p.name.startswith("_")]
    return core + craft

def guard_key(py: Path, pkg: Path = PKG) -> tuple[str, str, str]:
    """(root, group, entity): ('core', <corpus>, <entity>) for dyad/guards/<corpus>/<entity>.py,
    ('craft', <craft>, <entity>) for crafts/<craft>/guards/<entity>.py. The registry label is `<group>/<entity>`."""
    if py.is_relative_to(pkg / "guards"):
        return ("core", py.parent.name, py.stem)
    return ("craft", py.parents[1].name, py.stem)

def load_module(path: Path, name: str | None = None):
    """Import a Python file by path, executing the file that is on disk. The module is cached in
    sys.modules under `name` (default: the file stem) so two loaders of the same file share one
    module object.

    Why `dont_write_bytecode` is set here (#185, and two earlier reasons that are refuted): a
    by-path import must execute the source, never a `.pyc` whose validation is (mtime-to-the-
    second, size) and therefore cannot see a same-size rewrite inside one second. Measured with
    the suppression removed: this function returned `VALUE = 111` from a path whose source read
    `222`. The guard registry is loaded only through here, so that is `dyad check` reporting on
    code that is not on disk — the one artifact Rule-2's Binding cannot tolerate, since the
    evidence block must be about the head being merged.

    Both earlier reasons are **refuted**; neither is a reason to keep or drop this line:
      - "file counts stay deterministic" — false. Both counts the runner prints come from
        `distribute.files(tracked=True)`, i.e. `git ls-files`, which an untracked `.pyc` cannot move.
      - "a read-only command leaves no files behind" — false. With this suppression and
        `crafts.py`'s `_FLOOR_SCRIPT` one both in place, `dyad check --guards` still leaves
        `dyad/scripts/__pycache__`, written by `package.py`'s own `sys.path` imports, which this
        function does not mediate.

    Cost, measured: about 0.3 s per full gate. `crafts/sysarch/tests` is the only root where
    retaining bytecode replicates as faster (−12.5% of that root, 0.3% of total suite time);
    `dyad/tests`, `check --guards` and `check --evidence` are all inside their own between-run
    spread. See `agent-corpus/audits/2026-09-29-bytecode-retention-profile.md` (#190). Keeping the
    cache *and* being correct is available at the price of a `compileall --invalidation-mode
    checked-hash` step in the install path, refused on that price (plan #185 A5, revision 3)."""
    name = name or path.stem
    if name in sys.modules and getattr(sys.modules[name], "__file__", None) == str(path):
        return sys.modules[name]
    prev, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        except BaseException:
            # as the import system does: a module whose import raised (an `enforce` at its bottom, #203) never
            # stays cached half-initialised, or the next load would hand it out without raising again
            if sys.modules.get(name) is mod:
                del sys.modules[name]
            raise
    finally:
        sys.dont_write_bytecode = prev
    return mod

def load_guard_file(py: Path, pkg: Path = PKG):
    """The guard module at `py`, cached as `dyad_guards_<corpus>_<entity>` (core) or
    `dyad_crafts_<craft>_<entity>` (a craft's)."""
    root, group, entity = guard_key(py, pkg)
    return load_module(py, f"dyad_guards_{group}_{entity}" if root == "core" else f"dyad_crafts_{group}_{entity}")

def load_guard(corpus: str, entity: str, pkg: Path = PKG):
    """The guard module for one entity kind: `dyad/guards/<corpus>/<entity>.py` first, else the first
    craft guard `crafts/*/guards/<entity>.py` whose `CORPUS` is `corpus` (the zone of the entity's
    store), aliased in sys.modules as `dyad_guards_<corpus>_<entity>` so importers keep one name.
    FileNotFoundError when neither root has it (use find_guard for the absent-safe form)."""
    core = pkg / "guards" / corpus / f"{entity}.py"
    if core.exists():
        return load_module(core, f"dyad_guards_{corpus}_{entity}")
    for py in craft_glob(f"guards/{entity}.py", pkg):
        mod = load_guard_file(py, pkg)
        if getattr(mod, "CORPUS", None) == corpus:
            sys.modules.setdefault(f"dyad_guards_{corpus}_{entity}", mod)
            return mod
    raise FileNotFoundError(f"no guard {corpus}/{entity} under {pkg / 'guards'} or {crafts_dir(pkg)}/*/guards")

def find_guard(corpus: str, entity: str, pkg: Path = PKG):
    """load_guard, or None when no root provides the guard (a system without that craft; #155). A
    guard that exists but does not import still raises — that is a failing guard, not a missing one."""
    try:
        return load_guard(corpus, entity, pkg)
    except FileNotFoundError:
        return None

# crafts/sysarch/rules/guards.md p3: the guard contract, one definition shared by the runner's registry (package.py) and the
# craft guard (guards/craft/crafts.py, which checks a Tended craft's guards before export/install; #156).
CONTRACT = ("ENTITY", "CORPUS", "FIELDS", "TRANSACTION", "check_package")

def contract_problem(mod, root: str = "core", group: str | None = None, zones: set[str] | None = None) -> str | None:
    """None when `mod` declares the contract; else the problem text. `root` 'core': CORPUS must equal `group`
    (the directory under dyad/guards/); 'craft': CORPUS must be a zone name in `zones` (containment.ZONES)."""
    missing = [n for n in CONTRACT if not hasattr(mod, n)]
    if missing:
        return f"lacks {', '.join(missing)} (guard contract, crafts/sysarch/rules/guards.md)"
    if mod.TRANSACTION and not hasattr(mod, "check_transaction"):
        return "TRANSACTION but no check_transaction (guard contract, crafts/sysarch/rules/guards.md)"
    if root == "core" and group is not None and mod.CORPUS != group:
        return f"declares CORPUS {mod.CORPUS!r} but lives under guards/{group}/"
    if root == "craft" and zones is not None and mod.CORPUS not in zones:
        return f"declares CORPUS {mod.CORPUS!r}, not a zone in containment.ZONES ({', '.join(sorted(zones))})"
    return None

# ---- run-time invariants (crafts/syseng/rules/invariants.md p1, amended #203): a module declares two lists of
# (name, predicate) pairs. `INVARIANTS` is pure (its own literals only) and the module enforces it at import with
# `enforce(INVARIANTS, __name__)`, a fail-loud check (Rule-12 p1) with no off-switch; `TREE_INVARIANTS` reads the
# package tree or loads modules and never runs at import. The runner's pass runs both before any check, and the
# mutating call sites (dwork new|state, runbook run) run both before they write. Never `assert`.
Invariant = tuple[str, Callable[[], bool]]
LISTS = ("INVARIANTS", "TREE_INVARIANTS")   # the pure list, enforced at import; the tree list, run by the pass only

class InvariantError(Exception):
    """A module's invariants did not hold: `module` is its label, `failed` the names, sorted."""
    def __init__(self, module: str, failed: list[str]):
        self.module, self.failed = module, list(failed)
        super().__init__(f"{module}: invariant(s) failed: {', '.join(self.failed)}")

def invariants_of(source, extra=()) -> list[Invariant]:
    """The entries of a module's `INVARIANTS` and `TREE_INVARIANTS` (or of a list passed directly) plus `extra`,
    sorted by name; a module with neither list yields the extras only (which modules must declare one is the
    syseng guard's question, crafts/syseng/guards/invariants.py)."""
    own = list(source) if isinstance(source, (list, tuple)) else [e for n in LISTS for e in getattr(source, n, ())]
    return sorted(own + list(extra), key=lambda e: e[0] if isinstance(e, tuple) and e else str(e))

def false_invariants(entries) -> list[str]:
    """The names of the entries whose predicate is false or raises, sorted."""
    failed = []
    for name, pred in entries:
        try:
            ok = bool(pred())
        except Exception:
            ok = False
        if not ok:
            failed.append(name)
    return sorted(failed)

def check_invariants(source, extra=(), label: str | None = None) -> int:
    """Run every invariant of `source` (a module's two lists, or a list); raise InvariantError naming the false
    ones (a predicate that raises counts as false); return the number checked."""
    entries = invariants_of(source, extra)
    failed = false_invariants(entries)
    if failed:
        raise InvariantError(label or getattr(source, "__name__", "invariants"), failed)
    return len(entries)

def enforce(invariants: list[Invariant], name: str) -> int:
    """The import-time fail-loud check (Rule-12 p1; crafts/syseng/rules/invariants.md p1): a module calls
    `dyadlib.enforce(INVARIANTS, __name__)` at module level after the list's last binding. Every predicate runs;
    one that is false or raises makes it raise InvariantError naming every false name, sorted, so the import
    fails. No `assert`, no off-switch (no environment knob, flag or `-O` path skips it). The list is pure, so
    this costs microseconds; `TREE_INVARIANTS` is never passed here. Returns the number checked."""
    failed = false_invariants(invariants)
    if failed:
        raise InvariantError(name, failed)
    return len(invariants)

def contract_invariants(mod, root: str = "core", group: str | None = None, zones: set[str] | None = None) -> list[Invariant]:
    """The guard contract restated as four invariants the runner appends to every guard's list (the registry's
    fail-on-missing stays; these make the contract visible on the invariant surface)."""
    def corpus_ok():
        if root == "core":
            return group is None or mod.CORPUS == group
        return zones is None or mod.CORPUS in zones
    return [("entity-non-empty", lambda: isinstance(getattr(mod, "ENTITY", None), str) and bool(mod.ENTITY)),
            ("corpus-matches-directory", corpus_ok),
            ("fields-unique-strings", lambda: bool(mod.FIELDS) and all(isinstance(f, str) for f in mod.FIELDS) and len(set(mod.FIELDS)) == len(mod.FIELDS)),
            ("transaction-implies-check_transaction", lambda: not mod.TRANSACTION or callable(getattr(mod, "check_transaction", None)))]

def runner_module(pkg: Path = PKG):
    """The runner (`scripts/package.py`) as a module: the one already running (`__main__`) or imported, else
    loaded once by path as `package`."""
    p = pkg / "scripts" / "package.py"
    for m in list(sys.modules.values()):
        if getattr(m, "__file__", None) == str(p):
            return m
    return load_module(p, "package")

def projector_files(pkg: Path = PKG) -> list[Path]:
    """The core craft's own `dyad/scripts/project_<surface>.py` first (sorted by surface), then every
    `crafts/<craft>/projectors/project_<surface>.py`, sorted by craft then surface (the registry's discovery order;
    crafts/sysarch/rules/projection.md p4, #378)."""
    return sorted((pkg / "scripts").glob("project_*.py")) + craft_glob("projectors/project_*.py", pkg)

CORE_CRAFT = "dyad-operator"   # the core craft's name (Rule-11 p1; its registry row, p2): the key a core projector is discovered under

def projector_craft(py: Path, pkg: Path = PKG) -> str:
    """The craft a projector file belongs to: `dyad-operator` for one under the core's `scripts/`, else the craft directory's name."""
    return CORE_CRAFT if Path(py).resolve().parent == (pkg / "scripts").resolve() else Path(py).parents[1].name

def parse_kv(text: str) -> dict[str, str]:
    """`key: value` lines (the row-file form; a craft's MANIFEST.md too, #156); blank and `#` lines skipped."""
    out = {}
    for line in text.splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip() and not line.lstrip().startswith("#"):
            out[k.strip()] = v.strip()
    return out

def craft_dirs(pkg: Path = PKG) -> list[Path]:
    """Every Tended craft root `crafts/<craft>/` (a directory holding a VERSION), sorted by name."""
    d = crafts_dir(pkg)
    return sorted(p for p in d.iterdir() if p.is_dir() and (p / CRAFT_LAYOUT[0]).exists()) if d.is_dir() else []

# One version grammar (Rule-11 property 4), shared by every craft, core included: strict
# MAJOR.MINOR.PATCH, with an optional `+build` suffix for a locally-derived, unreleased tree — the
# drift guard's own escape hatch (`dyad/guards/infra/bundle.py` check_drift): a craft whose tree has
# diverged from its release tag under an unchanged VERSION says so honestly (`X.Y.Z+local`) rather
# than colliding with whatever plain bump is later released under that number (D2, #100).
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:\+[0-9A-Za-z.-]+)?")

def semver_tuple(s: str) -> tuple[int, ...]:
    """The comparable (major, minor, patch) of a SEMVER string, `+build` suffix stripped."""
    return tuple(int(x) for x in s.strip().split("+", 1)[0].split("."))

# Rule-8 host-action classes: the change-log row (Rule-8), a run-book command and its event (Rule-19)
# each declare one; the three guards read this tuple.
HOST_CLASSES = ("read-only", "reversible", "destructive")

# git's per-invocation variables: a hook exports them, and a command run from the work tree then reads
# another repository's dir, tree or index (d-work #142). Every git call here runs without them.
GIT_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR")   # a hook in a linked worktree exports GIT_COMMON_DIR too (#161, #169)
MODE_EXEC, MODE_FILE = "100755", "100644"   # the index modes tracked_mode reports (Rule-18's scripts, the hooks and bin/)

def git_env() -> dict[str, str]:
    """`os.environ` without GIT_VARS, for a git call that must see the tree it is pointed at."""
    return {k: v for k, v in os.environ.items() if k not in GIT_VARS}

def utc_date() -> str:
    """Today in UTC, `YYYY-MM-DD`: the one date every store writes — a row's `disposed` entry, a provenance entry's
    heading, `land`'s already-landed and Done-order tests, `release ready`'s entry (#592 R-b, the audit's mode 41).
    The host's local day differed from it by one around midnight, while every reader (`board.parse_since`, the
    trace's anchoring) already read a bare date as UTC. Earlier entries keep the date they were written with."""
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()

def repo_root(start: Path | None = None) -> Path:
    """The git work tree containing the package. Git hooks export GIT_DIR, under which
    `--show-toplevel` from a subdirectory reports that subdirectory (d-work #142); discovery
    from `start` without the hook's variables gives the true root, in a linked worktree too."""
    return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=start or PKG, text=True, env=git_env()).strip())

def tracked_mode(root: Path, rel: str | Path) -> str | None:
    """The mode git records in the index for one path under `root` (`100755`, `100644`, `120000`), or
    None when the path is not tracked there, `root` is no work tree, or `rel` lies outside it. The
    index is what an install, `git archive`, a clone and CI see; with `core.fileMode=false` (an NTFS
    checkout) the bit on disk is not — every file reads 755 whatever git holds, which passed three ops
    scripts tracked 100644 and shipped an entrypoint that could not exec (#135, #141). Read the mode
    here, never `os.access(p, os.X_OK)`; `git update-index --chmod=+x` is the fix it reports."""
    p = Path(rel)
    if p.is_absolute():
        if not p.is_relative_to(root):
            return None
        p = p.relative_to(root)
    try:                                          # `:(literal)`: the path is a name, never a glob, and never a directory
        r = subprocess.run(["git", "ls-files", "-s", "--", f":(literal){p.as_posix()}"], cwd=root, text=True,
                           capture_output=True, env=git_env(), timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = r.stdout.splitlines() if r.returncode == 0 else []
    return lines[0].split()[0] if len(lines) == 1 else None   # 0 lines: untracked; more: a directory or a conflict, no single mode

def instance(root: Path | None = None) -> Path:
    return (root or repo_root()) / os.environ.get("DYAD_INSTANCE", "agent-corpus")

def instance_rel(root: Path | None = None) -> str | None:
    """The instance as a repo-relative posix path, whatever form DYAD_INSTANCE takes (relative, with a
    trailing slash, or absolute inside the work tree); None when it lies outside the work tree, where
    nothing is tracked and no range can touch it (#191)."""
    root = root or repo_root()
    try:
        return Path(os.path.normpath(instance(root))).relative_to(Path(os.path.normpath(root))).as_posix()
    except ValueError:
        return None

def range_paths(root: Path, base: str, head: str, merge_base: bool = True) -> list[str] | None:
    """Every path a range touches, or None when git cannot say. Rename detection is off, so a move
    lists its source as well as its destination — `git diff --name-only` shows only the destination,
    which let a move of code into `<instance>/d-work/` pass as ledger-only (#191). NUL-separated, so
    no path is split or trimmed. `merge_base`: the three-dot form, the head side's own commits only,
    so paths `main` gained after a branch point are never the branch's."""
    spec = f"{base}...{head}" if merge_base else f"{base}..{head}"
    try:
        r = subprocess.run(["git", "diff", "--no-renames", "-z", "--name-only", spec], cwd=root,
                           capture_output=True, env=git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    return [p for p in r.stdout.decode("utf-8", "surrogateescape").split("\0") if p]

def commit_paths(root: Path, sha: str) -> list[str] | None:
    """The paths one commit changes against its first parent (every path, for a root commit), rename
    detection off; None when git cannot say. `diff-tree --root` needs no empty-tree id, so it holds in a
    sha256 repository as in a sha1 one."""
    try:
        r = subprocess.run(["git", "diff-tree", "--root", "--no-commit-id", "-r", "--no-renames", "-z", "--name-only", sha],
                           cwd=root, capture_output=True, env=git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    return [p for p in r.stdout.decode("utf-8", "surrogateescape").split("\0") if p]

def range_commits(root: Path, base: str, head: str, merges: bool = False) -> list[str] | None:
    """The commits `head` has that `base` lacks, oldest first — the non-merge ones, or with `merges`
    the merge commits; None when git cannot say."""
    try:
        r = subprocess.run(["git", "rev-list", "--reverse", "--merges" if merges else "--no-merges", f"{base}..{head}"],
                           cwd=root, capture_output=True, text=True, env=git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.split() if r.returncode == 0 else None

def ledger_only(root: Path, base: str, head: str, merge_base: bool = True) -> bool:
    """True when a range is clerical — Rule-2's and Rule-3's ledger-only commits and nothing else.
    `merge_base` (the gates, #191): every one of the range's own non-merge commits touches only
    `<instance>/d-work/`, judged commit by commit, the same walk the fence then makes; a branch that
    ever touched anything else — even reverted, or squashed into `main` since — is not ledger-only and
    goes through the plan gate. Without it (Rule-12's suite skip, #155): the two-dot tree difference,
    since what the suite tests is the tree. An empty or unreadable range, or an instance outside the
    work tree, is never ledger-only."""
    rel = instance_rel(root)
    if not rel:
        return False
    inside = lambda paths: bool(paths) and all(p.startswith(f"{rel}/d-work/") for p in paths)
    if not merge_base:
        return inside(range_paths(root, base, head, merge_base=False))
    commits = range_commits(root, base, head)
    return bool(commits) and all(inside(commit_paths(root, c)) for c in commits)

EVENTS_REL = "runbooks/events"   # under the host path: the run-book event store (Rule-19; the runner's `events_dir` default)

def events_rel(root: Path | None = None) -> str | None:
    """The run-book event store as a repo-relative posix path: `<host>/runbooks/events` (`host_path`, the
    preference `host-path`, d-work #175), or `<DYAD_RUNBOOKS>/events` when that override is set — the same
    directory the runner writes (`runbook.events_dir`) and the events guard fences, so what the gates exempt
    is exactly what that guard judges (#438). None when the host path is unusable (an empty, absolute or `..`
    value) or the store lies outside the work tree, where no range can be shown events-only."""
    root = root or repo_root()
    try:
        rb = (os.environ.get("DYAD_RUNBOOKS") or f"{host_path(root)}/runbooks").rstrip("/")
        rel = Path(os.path.normpath(Path(root) / rb / "events")).relative_to(Path(os.path.normpath(root))).as_posix()
    except ValueError:
        return None
    return None if rel in ("", ".") or rel.startswith("..") else rel

def events_only(root: Path, base: str, head: str, merge_base: bool = True) -> bool:
    """True when a range is clerical as monitoring's record — every path under `<host>/runbooks/events/`
    and nothing else (d-work #438): an event records an observation, never a decision, as a ledger-only
    commit records a prompt or a disposition. The same reading as `ledger_only`: with `merge_base` (the
    gates) every one of the range's own non-merge commits, commit by commit, rename detection off; without
    it (Rule-12's suite skip) the two-dot tree difference. A commit touching both the ledger and the event
    store is neither, since each commit is one zone (Rule-1); an empty or unreadable range, or an unusable
    host path, is never events-only."""
    rel = events_rel(root)
    if not rel:
        return False
    inside = lambda paths: bool(paths) and all(p.startswith(f"{rel}/") for p in paths)
    if not merge_base:
        return inside(range_paths(root, base, head, merge_base=False))
    commits = range_commits(root, base, head)
    return bool(commits) and all(inside(commit_paths(root, c)) for c in commits)

# ---- the host path and zone (Rule-1, d-work #175): where an instance keeps its host and operating
# records, and which zone holds them. Instance data, read from the Operator's preferences (`host-path`,
# `host-zone`) so hooks, CI and a fresh session all see the same value; `DYAD_HOST` / `DYAD_HOST_ZONE`
# override for tests, as `DYAD_INSTANCE` does. The defaults reproduce the five-zone table of every
# system before #175; `infra` folds the host records into the infra zone (a four-zone system).
# A guard's logical corpus for these stores stays `workstation` (HOST_CORPUS) whatever the zone.
DEFAULT_HOST, DEFAULT_HOST_ZONE = "workstation-corpus", "workstation"
HOST_ZONES = ("workstation", "infra")
HOST_CORPUS = "workstation"
PREFERENCES_REL = "preferences-corpus/PREFERENCES.md"

def preference(key: str, root: Path | None = None) -> str | None:
    """The value cell of one preference row (emphasis stripped), or None when the file or the row is
    absent. The table's grammar is the preference guard's (`guards/preferences/preferences.py`); this is
    the one read the core needs before any guard loads."""
    p = (root or repo_root()) / PREFERENCES_REL
    if not p.is_file():
        return None
    for r in table_rows(p.read_text()):   # `table_rows` keeps an escaped `\\|` inside its cell (#171)
        if len(r) >= 2 and plain(r[0]).strip() == key:
            return canonical_value(plain(r[1]).strip(), r[2] if len(r) >= 3 else "")
    return None

# ---- tunables (d-work #590): an operator-tunable number is a preference whose default has one home, the
# `dyad:defaultValue` of the DMC record that claims its key under `dyad:tunables` (`dyad/dmc/schema.md`). Every reader
# the record's `dyad:readBy` names calls `tunable` at use time, so a preference written after import is read.
DMC_STORE = "dmc"                                                  # the core's DMC store, under the package
_TUNABLE_BETWEEN = re.compile(r"between\s+(-?\d+(?:\.\d+)?)\s+and\s+(-?\d+(?:\.\d+)?)")

def _tunable_entries(pkg: Path = PKG):
    """(record name, entry) for every `dyad:tunables` entry of the core's DMC records, in file order."""
    import json
    for p in sorted((pkg / DMC_STORE).glob("*.jsonld")):
        text = p.read_text()
        if '"dyad:tunables"' in text:   # a cheap filter: most records carry none
            for t in json.loads(text).get("dyad:tunables") or ():
                if isinstance(t, dict):
                    yield p.name, t

def tunable_entry(key: str, pkg: Path = PKG) -> dict[str, str]:
    """The `dyad:tunables` entry of the core DMC record that claims `key` (`dyad/dmc/*.jsonld`), with `_record` its
    file name. KeyError when no record claims it: an unknown tunable is a programming error, never a silent default."""
    for name, t in _tunable_entries(pkg):
        if t.get("dyad:preference") == key:
            return {**t, "_record": name}
    raise KeyError(f"tunable {key!r}: no record in {pkg.name}/{DMC_STORE}/ claims it under dyad:tunables")

def tunables_read_by(rel: str, pkg: Path = PKG) -> set[str]:
    """The tunable keys whose `dyad:readBy` is `rel` (package-relative, as the records write it): a reader's
    TREE_INVARIANTS pins its own key list against this, so the code and the records cannot drift apart."""
    return {t["dyad:preference"] for _, t in _tunable_entries(pkg)
            if t.get("dyad:readBy") == rel and t.get("dyad:preference")}

def tunable_value(text: str | None, default: int | float, allowed: str) -> int | float | None:
    """`text` parsed to `default`'s type (its first word: `7 days` reads 7), or None when it does not parse or falls
    outside what `allowed` states: `between A and B` needs A < value < B; `positive` needs value > 0."""
    try:
        v = type(default)((text or "").split()[0])
    except (ValueError, IndexError):
        return None
    m = _TUNABLE_BETWEEN.search(allowed)
    if m and not float(m.group(1)) < v < float(m.group(2)):
        return None
    if "positive" in allowed and not v > 0:
        return None
    return v

def tunable_default(key: str, pkg: Path = PKG) -> int | float:
    """The record's `dyad:defaultValue` for `key`, an int when it reads as one, else a float. KeyError on an unknown
    key; ValueError when the default does not parse or is not valid by its own `dyad:allowed` (fail-loud: the one
    home of the default is wrong)."""
    t = tunable_entry(key, pkg)
    raw, allowed = t.get("dyad:defaultValue", ""), t.get("dyad:allowed", "")
    try:
        typed: int | float = int(raw)
    except ValueError:
        typed = float(raw)
    default = tunable_value(raw, typed, allowed)
    if default is None:
        raise ValueError(f"tunable {key!r}: the default {raw!r} of {t['_record']} is not {allowed!r}")
    return default

def tunable(key: str, root: Path | None = None, pkg: Path = PKG) -> int | float:
    """The tunable `key`, read at use time: the instance's preference value (`preference`) parsed to the type of the
    DMC default when it is valid by the record's `dyad:allowed`, else the record's `dyad:defaultValue` — absent and
    malformed both fall back, as `attendance-window` always did. KeyError on an unknown key (fail-loud)."""
    default = tunable_default(key, pkg)
    v = preference(key, root)
    got = tunable_value(v, default, tunable_entry(key, pkg).get("dyad:allowed", "")) if v is not None else None
    return default if got is None else got

_PREF_ALT = re.compile(r"`([^`]+)`")

def canonical_value(value: str, allowed: str) -> str:
    """L6 (#553): an operator types a preference value directly, so its case is not meaningful. When `allowed` is an
    enumeration (every `|`-separated part one backticked value) and `value` matches one of them under casefold, that
    canonical spelling is returned; otherwise `value` unchanged. The preferences guard warns on the difference."""
    parts = [p.strip() for p in allowed.split("|")] if allowed else []
    alts = [m.group(1).strip() for m in (_PREF_ALT.fullmatch(p) for p in parts) if m] if parts else []
    if not alts or len(alts) != len(parts) or value in alts:
        return value
    return next((a for a in alts if a.casefold() == value.casefold()), value)

def host_path(root: Path | None = None) -> str:
    """The host path, repo-relative, no trailing `/`: `DYAD_HOST`, else preference `host-path`, else
    DEFAULT_HOST. ValueError on an empty, absolute or `..` path."""
    v = os.environ.get("DYAD_HOST") or preference("host-path", root) or DEFAULT_HOST
    v = v.strip().rstrip("/")
    if not v or v.startswith("/") or ".." in Path(v).parts:
        raise ValueError(f"host-path {v!r}: must be a relative path inside the repo")
    return v

def host_zone(root: Path | None = None) -> str:
    """The zone of the host path: `DYAD_HOST_ZONE`, else preference `host-zone`, else DEFAULT_HOST_ZONE.
    ValueError on a value outside HOST_ZONES (never a silent fallback: #175 F1)."""
    v = (os.environ.get("DYAD_HOST_ZONE") or preference("host-zone", root) or DEFAULT_HOST_ZONE).strip()
    if v not in HOST_ZONES:
        raise ValueError(f"host-zone {v!r}: not one of {', '.join(HOST_ZONES)}")
    return v

RULES_LOCAL = "package_rules.local.txt"   # <instance>/: this host's own refuse-list rows (Rule-11 property 1; d-work #192)

def package_rules(pkg: Path | None = None, root: Path | None = None) -> dict[str, list[str]]:
    """Rule-11 check data: `dyad/scripts/package_rules.txt` (generic, ships with the package) plus, when
    present, `<instance>/package_rules.local.txt` — the concrete strings of *this* host (its hostname, its
    home path), which the package must refuse but must never carry (#192: the refuse-list itself leaked
    them into every release archive). Same line grammar in both; kinds merge. `root=None` skips the
    local file (a scratch tree with no instance)."""
    out: dict[str, list[str]] = {"string": [], "name": [], "header": [], "generated": []}
    files = [(pkg or PKG) / "scripts" / "package_rules.txt"]
    if root is not None:
        local = instance(root) / RULES_LOCAL
        if local.is_file():
            files.append(local)
    for f in files:
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            kind, _, val = line.partition(":")
            out.setdefault(kind.strip(), []).append(val.strip())
    return out

def ledger_path(root: Path | None = None) -> Path:
    """Rendered view (untracked, Rule-16); the canonical ledger is rows_dir()."""
    return instance(root) / "d-work" / "LEDGER.md"

def rows_dir(root: Path | None = None) -> Path:
    return instance(root) / "d-work" / "rows"

@dataclass(frozen=True)
class Row:
    id: int
    title: str
    opened: str
    state: str
    disposed: str
    refs: str
    mode: str = "explicit"   # mode: the countersign model's countersign mode, adopted (Rule-3 Scope; dyad/playbooks/countersign-model.md); optional and last, d-work #290

_ROW = re.compile(r"^\|\s*(\d+)\s*\|")

def ledger_rows(text: str) -> list[Row]:
    """Parse ledger table rows. Non-row lines (header, separator, prose) are skipped.
    A duplicated id raises ValueError: the ledger is append-only and ids are unique."""
    rows, seen = [], set()
    for line in text.splitlines():
        if not _ROW.match(line):
            continue
        cells = split_cells(line)
        if len(cells) < 6:
            raise ValueError(f"ledger row with {len(cells)} cells: {line!r}")
        rid = int(cells[0])
        if rid in seen:
            raise ValueError(f"duplicate ledger id {rid}")
        seen.add(rid)
        rows.append(Row(rid, *cells[1:6]))
    return rows

FIELDS = ("id", "title", "opened", "state", "disposed", "refs")
# d-work #290: `mode` is read when its line is present and defaulted when it is absent, and it is *not* in
# FIELDS. It cannot be: `parse_row_file` raises on a missing FIELDS key, and the plan gate parses rows at
# historical commits (`guards/agent/prs.py`, `read_rows(root, at=base)`), none of which carry the line — a
# required `mode` would make every past commit unparseable and the gate unrunnable. The fence reads `mode`
# off the parsed Row, never off FIELDS, so `rows.FIELDS is dyadlib.FIELDS` stays true.
OPTIONAL_FIELDS = ("mode",)
MODES = frozenset({"explicit", "implicit"})   # the mode of a row (the countersign model's term); a disposition's coverage is `basis`, not this
DEFAULT_MODE = Row.mode                       # the dataclass's own default: one source of truth for an absent line

# d-work states and the one transition table (Rule-16 Store cites this; Rule-3 defines the states).
STATES = frozenset({"open", "planned", "blocked", "backlog", "done", "archived"})   # archived: retired from the board, terminal (d-work #37)
NEW_STATES = frozenset({"open", "backlog"})          # states a row may be created in
TRANSITIONS: dict[str, frozenset[str]] = {
    "open": frozenset({"planned", "blocked", "done", "archived"}),   # #615: archived on the bare intent-N, before any plan
    "planned": frozenset({"open", "blocked", "done"}),
    "blocked": frozenset({"open"}),
    "backlog": frozenset({"open", "archived"}),   # #290: the board had no exit from where 75 of its 280 rows sit (`archived`, 0 uses)
    "done": frozenset({"archived"}),   # done never reopens; archived is one further step the same way (#37)
    "archived": frozenset(),
}

# d-work #309: the machine's input alphabet. TRANSITIONS is a successor relation — which state may follow which;
# a finite-state machine needs the input that moves a row along each edge and whose act it is. One entry per
# edge of TRANSITIONS and per birth (from None into a NEW_STATES state): the input as the d-work play-book names
# it (`dyad/playbooks/d-work.md`, whose machine table is pinned to this by dyad/tests/test_playbooks.py), and the
# kinds it may be — `prompt` (an Operator prompt: a `prompt` entry of the provenance record), `disposition` (an
# Operator answer: a `disposed` entry and its `disposition` record entry, Rule-7 property 5), `clerical` (an
# Agent act a disposition already covers: no entry of its own, Rule-2). Data, not a decision: nothing reads it to
# refuse a write yet (`dwork state`'s refusals stay hand-written branches in package.py).
INPUT_KINDS = frozenset({"prompt", "disposition", "clerical"})
TERMINAL_STATES = frozenset({"done", "archived"})   # exit only to `archived` or nowhere; only the Operator closes (Rule-2)
INPUTS: dict[tuple[str | None, str], tuple[str, frozenset[str]]] = {
    (None, "open"):          ("an Operator prompt; the Y that admits an intake; a mandate's plan-Y for an accreted row", frozenset({"prompt", "disposition"})),
    (None, "backlog"):       ("an Operator disposition opening it (Y backlog)", frozenset({"disposition"})),
    ("open", "planned"):     ("the plan-Y", frozenset({"disposition"})),
    ("open", "blocked"):     ("a deferral naming the blocking d-work", frozenset({"disposition"})),
    ("open", "archived"):    ("the bare N to the intent question (N intent) on a row holding no Y plan (#615)", frozenset({"disposition"})),
    ("open", "done"):        ("the Done-Y, recorded when it is given; the state follows once the merges it named have landed (#202)", frozenset({"disposition"})),
    ("planned", "open"):     ("re-planning: main moved past a touched file (Rule-15 phase 2), or the Operator's amend of the plan", frozenset({"clerical", "disposition"})),
    ("planned", "blocked"):  ("a deferral naming the blocking d-work", frozenset({"disposition"})),
    ("planned", "done"):     ("the Done-Y, recorded when it is given; the state follows once the merges it named have landed (#202)", frozenset({"disposition"})),
    ("blocked", "open"):     ("the blocking d-work reaching done", frozenset({"clerical"})),
    ("backlog", "open"):     ("an Operator prompt for it", frozenset({"prompt"})),
    ("backlog", "archived"): ("the retirement Y over the named set", frozenset({"disposition"})),
    ("done", "archived"):    ("the retirement Y over the named set", frozenset({"disposition"})),
}

# d-work #587 (X1-X4, X9): the orchestration machine of a board entry, beside the row's own machine above and never
# touching it. A board entry that carries a `phase` is in this machine; one that carries none behaves as before #587.
# An event moves an entry from a phase (None: the entry is absent or unphased, an adoption) to its target, fired by
# one actor, with the fields the event must carry. `said-file` is the Operator's words (Rule-7), carried only by an
# answer. Data, read by `board advance` (guards/agent/board.py), which is the derived fields' only writer.
ORCH_PHASES = ("planning", "intent-asked", "plan-ready", "plan-asked", "building", "verifying",
               "done-ready", "done-asked", "landing", "held")      # stored phases, in lifecycle order
ORCH_ASKED = frozenset({"intent-asked", "plan-asked", "done-asked"})
ORCH_DROP = "(closed)"     # target sentinel: the entry file is deleted (never stored)
ORCH_FROM = "@from"        # target sentinel: release returns to phase.from (an asked phase steps back to its *-ready)
ORCH_ACTORS = frozenset({"home", "unit", "automaton"})
ORCH_HOLDABLE = ("planning", "intent-asked", "plan-ready", "plan-asked", "building", "verifying", "done-ready", "done-asked")
ORCH_WATCHED = ("verifying", "done-ready", "done-asked")   # #587 X6: the phases whose recorded PR heads the automaton
                                                           # compares with the live heads; a move fires `head-moved`
ORCH_OR = " or "           # an actor cell naming several actors: `home or automaton` (#587 X5), any one may fire it
# #587 S10 (plan F7's survivor): the events with no side effect on the entry, a self-loop on every phase that changes
# neither the phase, the derived fields nor `since`. `read` is fired by `dyad inbox read <message>…` (the reader, the
# box's own seat: the holder or a unit) when a named message's row has a phased entry; its record is the message's
# `.read` marker, never a board write, so `board advance` does not take it.
ORCH_NO_EFFECT = frozenset({"read"})
# (from-phase | None, event) -> (targets, actor, required fields)
ORCH_EVENTS: dict[tuple[str | None, str], tuple[tuple[str, ...], str, tuple[str, ...]]] = {
    (None, "opened"):                   (("planning",), "home", ("unit",)),
    (None, "plan-landed"):              (("plan-ready",), "unit", ()),             # adoption of an unphased entry
    (None, "pr-up"):                    (("verifying",), "unit", ("pr", "head")),  # adoption
    ("planning", "plan-landed"):        (("plan-ready",), "unit", ()),
    # #615: under `intent-reading: on` the intent question is asked from planning, before the plan is drafted; its Y
    # returns the entry to planning, an N with text (amend) likewise, and the bare N archives the row (ORCH_DROP)
    ("planning", "asked"):              (("intent-asked",), "home", ()),
    ("intent-asked", "answered-Y"):     (("planning",), "home", ("said-file",)),
    ("intent-asked", "answered-N"):     (("planning", ORCH_DROP), "home", ("said-file",)),   # ORCH_DROP on a bare N
    ("plan-ready", "asked"):            (("plan-asked",), "home", ()),
    ("plan-asked", "answered-Y"):       (("building",), "home", ("said-file",)),
    ("plan-asked", "answered-N"):       (("planning",), "home", ("said-file",)),
    ("building", "pr-up"):              (("verifying",), "unit", ("pr", "head")),
    ("verifying", "pr-up"):             (("verifying",), "unit", ("pr", "head")),  # self-loop
    ("building", "evidence-verified"):  (("done-ready",), "home", ("evidence",)),  # no-PR d-work, or heads already listed
    ("verifying", "evidence-verified"): (("done-ready",), "home or automaton", ("evidence",)),   # X5: the automaton's
    ("verifying", "evidence-failed"):   (("building",), "home or automaton", ("note",)),         # combined evidence
    ("done-ready", "asked"):            (("done-asked",), "home", ()),
    ("done-asked", "answered-Y"):       (("landing", ORCH_DROP), "home", ("said-file",)),   # ORCH_DROP when no PR
    ("done-asked", "answered-N"):       (("building",), "home", ("said-file",)),
    ("landing", "closed"):              ((ORCH_DROP,), "automaton", ()),           # steps.close_landed drops the entry
    ("held", "release"):                ((ORCH_FROM,), "home", ()),
    **{(p, "hold"): (("held",), "home", ("note", "on")) for p in ORCH_HOLDABLE},
    # X6: a live PR head that differs from the one the phase records voids the evidence and any question asked on it
    # (Rule-2, Binding: a Y binds only while the heads are unchanged), so the entry goes back to verifying
    **{(p, "head-moved"): (("verifying",), "automaton", ("pr", "head")) for p in ORCH_WATCHED},
    # X6 for a batch: a Done question naming several rows is void once any head it names moves (Rule-2, Binding), so
    # every other row it names steps back to done-ready, its own heads and evidence unchanged, its question withdrawn
    ("done-asked", "withdrawn"):        (("done-ready",), "automaton", ("note",)),
    # S10: reading a message is an event, and changes nothing on the entry (ORCH_NO_EFFECT)
    **{(p, "read"): ((p,), "home or unit", ()) for p in ORCH_PHASES},
}

def orch_actors(cell: str) -> frozenset[str]:
    """The actors an `ORCH_EVENTS` actor cell names: one, or several joined by `ORCH_OR`."""
    return frozenset(a.strip() for a in cell.split(ORCH_OR))

ORCH_EVENT_NAMES = frozenset(e for _, e in ORCH_EVENTS)
# the events some non-automaton actor may fire, so `board advance` takes them; `closed` (steps.close_landed) and
# `head-moved` (automaton.py) are the automaton's own, and `read` (ORCH_NO_EFFECT) is `inbox read`'s
ORCH_CLI_EVENTS = frozenset(e for _, e in ORCH_EVENTS
                            if e not in ORCH_NO_EFFECT and any(orch_actors(a) - {"automaton"} for (_, ee), (_, a, _) in ORCH_EVENTS.items() if ee == e))

def orch_release_to(frm: str) -> str:
    """Where `release` returns an entry held at `frm`: an asked phase steps back to its `*-ready`, since `hold` took its
    question down; any other phase is restored as it was."""
    return {"intent-asked": "planning", "plan-asked": "plan-ready", "done-asked": "done-ready"}.get(frm, frm)

def orch_successors(events, phase) -> set[str]:
    """Every target an event from `phase` may reach, `ORCH_FROM` expanded to the phases `release` may restore."""
    out = set()
    for (f, _), (targets, _, _) in events.items():
        if f != phase:
            continue
        for t in targets:
            if t == ORCH_FROM:
                out |= {orch_release_to(q) for (q, e) in events if e == "hold" and q is not None}
            else:
                out.add(t)
    return out

def orch_reach(events, start) -> set[str]:
    """Every phase (and ORCH_DROP) reachable from `start` (a phase, or None for the births and adoptions)."""
    seen, todo = set(), [start]
    while todo:
        for t in orch_successors(events, todo.pop()):
            if t not in seen:
                seen.add(t)
                if t != ORCH_DROP:
                    todo.append(t)
    return seen

def orch_invariants(events, phases=ORCH_PHASES) -> list:
    """The machine's invariants over a table: the module's own (in INVARIANTS), or a patched copy a test passes."""
    froms = {f for f, e in events if e not in ORCH_NO_EFFECT}   # a no-effect self-loop is no exit
    answers = {k: v for k, v in events.items() if k[1] in ("answered-Y", "answered-N")}
    return [
        ("orch-keys-known", lambda: all((f is None or f in phases) and orch_actors(a) <= ORCH_ACTORS
                                        and all(t in phases or t in (ORCH_DROP, ORCH_FROM) for t in ts)
                                        and (ORCH_FROM not in ts or (f, e) == ("held", "release"))
                                        for (f, e), (ts, a, _) in events.items())),
        ("orch-every-phase-reachable", lambda: set(phases) <= orch_reach(events, None)),
        ("orch-every-phase-exits", lambda: set(phases) <= froms),
        ("orch-drop-reachable", lambda: all(ORCH_DROP in orch_reach(events, p) for p in phases)),
        ("orch-answers-from-asked-by-home", lambda: all(f in ORCH_ASKED and a == "home" for (f, _), (_, a, _) in answers.items())
                                                    and all(("said-file" in r) == (k in answers) for k, (_, _, r) in events.items())),
        ("orch-automaton-takes-no-words", lambda: all("said-file" not in r for _, (_, a, r) in events.items() if "automaton" in orch_actors(a))),
        # an asked phase is left by the answer, by `hold`, by `head-moved` or by `withdrawn` — the non-answer exits
        # besides hold, because Rule-2's Binding voids a Y given on a moved head (`head-moved`, the row whose PR moved),
        # and a batch Y when any head it names moves (`withdrawn`, every other row the batch question names), so the
        # question must come down before it is answered
        ("orch-asked-exits-on-answer", lambda: all(e in ("answered-Y", "answered-N", "hold", "head-moved", "withdrawn")
                                                   or e in ORCH_NO_EFFECT for f, e in events if f in ORCH_ASKED)),
        # S10: a no-effect event is a self-loop from every phase and from no birth, carrying no field and no words, and
        # fired by no automaton (the reader is a seat)
        ("orch-no-effect-is-a-self-loop-everywhere", lambda: all(
            all(events.get((p, e), ((),))[0] == (p,) for p in phases) and (None, e) not in events
            for e in ORCH_NO_EFFECT)
            and all(ts == (f,) and not r and "automaton" not in orch_actors(a)
                    for (f, e), (ts, a, r) in events.items() if e in ORCH_NO_EFFECT)),
        ("orch-head-moved-returns-to-verifying", lambda: all(ts == ("verifying",) and orch_actors(a) == {"automaton"}
                                                             and {"pr", "head"} <= set(r) and f in ORCH_WATCHED
                                                             for (f, e), (ts, a, r) in events.items() if e == "head-moved")
                                                         and all((p, "head-moved") in events for p in ORCH_WATCHED)),
        ("orch-withdrawn-is-the-automatons-from-done-asked", lambda: all(f == "done-asked" and ts == ("done-ready",)
                                                                          and orch_actors(a) == {"automaton"}
                                                                          for (f, e), (ts, a, _) in events.items() if e == "withdrawn")),
        ("orch-automaton-evidence-from-verifying-only", lambda: all(f == "verifying" for (f, e), (_, a, _) in events.items()
                                                                    if e.startswith("evidence-") and "automaton" in orch_actors(a))),
        ("orch-hold-closure", lambda: all((p, "hold") in events for p in phases if p not in ("held", "landing"))
                                      and ("held", "release") in events),
    ]

# d-work #618: what each check reads, and what starts it (the decision criterion `dyad/dmc/check-trigger.jsonld`, home
# Rule-14 property 3). A check reads one or more INPUTS; its triggers are the union of its inputs' (plan #618 H1). The
# keys of CHECK_INPUTS are every registry label (`dyad check --list`, `<group>/<entity>`), every part of the sweep and
# the suite in its two halves; a label whose craft is not installed is ignored, a registered label with no row fails
# (dyad/tests/test_check_trigger.py, plan Q3). Data, read by that test; nothing refuses a run on it.
CHECK_INPUT_NAMES = ("code tree", "ledger stores", "event store", "absence", "outside world")
CODE, LEDGER, EVENTS, ABSENCE, WORLD = CHECK_INPUT_NAMES
INPUT_TRIGGERS: dict[str, tuple[str, str]] = {   # input -> (its trigger, the delay it accepts)
    CODE:    ("each landed merge: the full sweep (dyad-sweep.yml, dispatched by dyad-automaton.yml or started by a code push)", "none"),
    LEDGER:  ("each ledger push: `dyad automaton sweep --stores` (dyad-automaton.yml)", "until the next ledger push"),
    EVENTS:  ("each events-only push: `dyad automaton sweep --stores` (dyad-automaton.yml)", "until the next events push"),
    ABSENCE: ("the home's read at each operator prompt: `dyad board resume`, its stall lines", "until the operator's next prompt"),
    WORLD:   ("the next landed merge's full sweep (dyad-sweep.yml)", "until the next merge"),
}
CHECK_INPUTS: dict[str, tuple[str, ...]] = {
    # core guards
    "agent/board": (LEDGER,), "agent/dmc": (CODE,), "agent/frame": (CODE,), "agent/inbox": (LEDGER,),
    "agent/merges": (CODE, LEDGER), "agent/plans": (CODE, LEDGER), "agent/provenance": (LEDGER,), "agent/prs": (CODE,),
    "agent/records": (CODE,), "agent/references": (CODE, LEDGER), "agent/rows": (LEDGER,), "agent/rules": (CODE,),
    "agent/sessions": (LEDGER,), "agent/traces": (LEDGER,), "agent/vocabulary": (CODE,), "craft/crafts": (CODE,),
    "infra/bundle": (CODE,), "infra/containment": (CODE,), "infra/manifest": (CODE,), "preferences/preferences": (CODE,),
    # craft guards (ignored while their craft is absent, Q3)
    "cabinet/seats": (CODE, LEDGER), "chronicle/episodes": (CODE, LEDGER), "sysadmin/changelog": (CODE,),
    "sysadmin/events": (EVENTS,), "sysadmin/ops_scripts": (CODE,), "sysadmin/runbooks": (CODE,), "sysarch/registry": (CODE,),
    "syseng/invariants": (CODE,), "syseng/naming": (CODE,), "syseng/tests": (CODE,),
    # the sweep's parts (scripts/automaton.py, scripts/hygiene.py)
    "sweep_check": (CODE, LEDGER, EVENTS), "sweep_drift": (WORLD,), "sweep_ledger": (ABSENCE,), "sweep_ci": (ABSENCE, WORLD),
    "hygiene": (ABSENCE,), "inflight": (ABSENCE,),
    # the suite: every test that is not a livetest.LiveCase reads the tree; the LiveCase tests read the stores (H4)
    "suite": (CODE,), "suite:live": (LEDGER, EVENTS),
}
SWEEP_PARTS = ("sweep_check", "sweep_drift", "sweep_ledger", "sweep_ci", "hygiene", "inflight")

# Rule-15 phase 1: the parts a plan file carries. The file is prose (no parser); this names the
# parts so a projector (crafts/sysarch/rules/projection.md) can report which a plan mentions, never how it says them.
PLAN_PARTS = ("intent as read", "mutation", "files touched", "base commit", "falsification", "definition of done")
DOD_SINCE = "2026-11-05"   # #574: `definition of done` is asked only of plans whose row opened on or after this date

_CELL_SEP = re.compile(r"(?<!\\)\|")   # a `|` not preceded by `\`: an escaped `\|` is cell content (#171)

def escape_cell(text: str) -> str:
    """A cell's text as a markdown table writes it: every `|` escaped as `\\|`, so a cell holding one stays one
    cell (#7). `split_cells` reads it back."""
    return text.replace("|", "\\|")

def split_cells(line: str) -> list[str]:
    """The cells of one markdown table line, stripped: split on every unescaped `|`, the leading and trailing
    separators dropped, and each escaped `\\|` returned as `|` (#171). The one cell splitter of every table parser
    here; a caller that replaced `\\|` before parsing still reads the same cells."""
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().replace("\\|", "|") for c in _CELL_SEP.split(s)]

def table_header(text: str) -> list[str]:
    """Column names of the first markdown table in `text`: the `|` line followed by a `|---|`
    separator. Empty when there is none. Used to read a schema from a template or a record."""
    lines = text.splitlines()
    for i, line in enumerate(lines[:-1]):
        nxt = lines[i + 1].strip()
        if line.startswith("|") and nxt.startswith("|") and set(nxt) <= set("|-: "):
            return split_cells(line)
    return []

def table_rows(text: str) -> list[list[str]]:
    """Body rows of the first markdown table (after the header and separator), cells stripped."""
    out, seen_sep = [], False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if seen_sep:
                break
            continue
        if set(s) <= set("|-: "):
            seen_sep = True; continue
        if seen_sep:
            out.append(split_cells(s))
    return out

def tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every markdown table in `text` as (header cells, body rows); a table is a `|` header line
    followed by a `|---|` separator line."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines) - 1:
        line, nxt = lines[i].strip(), lines[i + 1].strip()
        if line.startswith("|") and nxt.startswith("|") and set(nxt) <= set("|-: "):
            header = split_cells(line)
            rows, i = [], i + 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_cells(lines[i])); i += 1
            out.append((header, rows))
        else:
            i += 1
    return out

def allowed(a: str, b: str) -> bool:
    """True if a row may go from state `a` to state `b`. Same state is always allowed
    (disposed/refs edits); anything outside TRANSITIONS is refused."""
    return a == b or b in TRANSITIONS.get(a, frozenset())

class TransitionError(ValueError):
    """A row write that would leave Rule-16's table: an unknown state, a transition the table lacks, or a new row
    in a state rows are not created in. The message is the refusal `dyad dwork` prints."""

def require_transition(before: str | None, after: str) -> None:
    """The fail-loud check at the d-work state transition (crafts/syseng/rules/invariants.md p1, #203): raise
    TransitionError unless `after` is a state and the table allows `before`→`after` — or, for a new row
    (`before` None), `after` is one of NEW_STATES. Called once per disposition, by `write_row` only, before its
    first write; never on the read path (`read_rows`, the fence and the renderers do not call it)."""
    if after not in STATES:
        raise TransitionError(f"no such state {after!r}; states: {' '.join(sorted(STATES))}")
    if before is None:
        if after not in NEW_STATES:
            raise TransitionError(f"a new row starts in {' or '.join(sorted(NEW_STATES))}, not {after!r} (Rule-16)")
    elif not allowed(before, after):
        raise TransitionError(f"transition {before}→{after} not in the table (Rule-16); allowed from {before}: "
                              f"{' '.join(sorted(TRANSITIONS.get(before, ()))) or 'none'}")

def write_row(root: Path, row: Row, before: str | None, first: Callable[[], object] | None = None,
              dry_run: bool = False) -> Path:
    """The one write of a row file (Rule-16): `require_transition(before, row.state)` first, so a refused
    transition writes nothing; then `first` (the caller's other write of the same disposition, its provenance
    entry, Rule-7) and the row file. `before` is the row's state on disk, None for a new row. With `dry_run`
    the transition is checked and nothing is written, neither `first` nor the row (`dwork state --check`,
    d-work #464): the same refusal at the same point, so a check can never disagree with the write it stands for."""
    require_transition(before, row.state)
    if dry_run:
        return rows_dir(root) / f"{row.id}.md"
    if first is not None:
        first()
    path = rows_dir(root) / f"{row.id}.md"
    path.write_text(format_row_file(row))
    return path

def parse_row_file(text: str) -> Row:
    """One row file: `key: value` lines in FIELDS order, then any of OPTIONAL_FIELDS (Rule-16). A missing
    FIELDS key raises; an absent OPTIONAL_FIELDS line takes the Row's own default, so a row file written
    before the field existed — every row at every past commit the plan gate parses — reads unchanged
    (d-work #290). A `mode` outside MODES raises, so a hand-edited row file is a parse failure the package
    check reports rather than a silent third mode."""
    d = {}
    for line in text.splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip() in FIELDS + OPTIONAL_FIELDS:
            d[k.strip()] = v.strip()
    missing = [f for f in FIELDS if f not in d]
    if missing:
        raise ValueError(f"row file missing {missing}")
    mode = d.get("mode", DEFAULT_MODE)
    if mode not in MODES:
        raise ValueError(f"row file mode {mode!r} not one of {' '.join(sorted(MODES))}")
    return Row(int(d["id"]), d["title"], d["opened"], d["state"], d["disposed"], d["refs"], mode)

def format_row_file(r: Row) -> str:
    """Every FIELDS line, then an OPTIONAL_FIELDS line only where the value differs from the dataclass
    default: `mode: implicit` is written and `mode: explicit` is not. So reading any of the 280 rows that
    predate the field and writing it back is byte-identical, which is why no migration of the store is
    needed — a ledger commit's diff still shows only what the disposition changed (d-work #290)."""
    return ("".join(f"{k}: {getattr(r, k)}\n" for k in FIELDS)
            + "".join(f"{k}: {getattr(r, k)}\n" for k in OPTIONAL_FIELDS if getattr(r, k) != getattr(Row, k)))

def show_many(root: Path, at: str, paths: list[str]) -> dict[str, str]:
    """{path: text} of every `paths` entry at commit `at`, read in one `git cat-file --batch` (#617: one process, not
    one `git show` per file, so `dyad board resume`'s ledger reads stay under its ceiling); a path absent at `at` is
    left out. Raises CalledProcessError when git fails."""
    if not paths:
        return {}
    r = subprocess.run(["git", "cat-file", "--batch"], cwd=root, input="".join(f"{at}:{p}\n" for p in paths).encode(),
                       capture_output=True, check=True)
    out, data, i = {}, r.stdout, 0
    for p in paths:
        nl = data.index(b"\n", i)
        head = data[i:nl].split()
        i = nl + 1
        if len(head) == 3 and head[1] == b"blob":
            size = int(head[2])
            out[p] = data[i:i + size].decode("utf-8", errors="replace")
            i += size + 1
    return out

def read_rows(root: Path | None = None, at: str | None = None) -> list[Row]:
    """All rows from rows_dir(); with `at`, from that git commit (Rule-16)."""
    root = root or repo_root()
    if at is None:  # working tree: DYAD_INSTANCE may be absolute and outside root (tests, d-work #112)
        files = sorted(rows_dir(root).glob("*.md"), key=lambda p: int(p.stem) if p.stem.isdigit() else -1)
        texts = [p.read_text() for p in files if p.stem.isdigit()]
    else:
        rel = rows_dir(root).relative_to(root)
        try:
            names = subprocess.check_output(["git", "ls-tree", "--name-only", f"{at}:{rel}"], cwd=root, text=True, stderr=subprocess.DEVNULL).split()
        except subprocess.CalledProcessError:
            # transition / legacy: a commit before Rule-16 has only the table
            table_rel = ledger_path(root).relative_to(root)
            return ledger_rows(subprocess.check_output(["git", "show", f"{at}:{table_rel}"], cwd=root, text=True))
        want = [f"{rel.as_posix()}/{n}" for n in sorted(names, key=lambda n: int(n[:-3]) if n[:-3].isdigit() else -1)
                if n.endswith(".md") and n[:-3].isdigit()]
        got = show_many(root, at, want)                 # one process for every row file (#617)
        texts = [got[w] for w in want]
    rows = [parse_row_file(t) for t in texts]
    ids = [r.id for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate ledger id in rows/")
    return rows

def render(rows: list[Row]) -> str:
    head = ("# d-work ledger (rendered view, Rule-16; canonical rows in rows/)\n\n"
            "| id | title | opened | state | disposed | refs |\n|----|-------|--------|-------|----------|------|\n")
    e = escape_cell   # every cell escaped, so a `|` in any field stays in its cell (#7); `ledger_rows` reads it back
    return head + "".join(f"| {r.id} | {e(r.title)} | {e(r.opened)} | {e(r.state)} | {e(r.disposed)} | {e(r.refs)} |\n" for r in rows)

def ledger_row(text: str, rid: int) -> Row | None:
    return next((r for r in ledger_rows(text) if r.id == rid), None)

def rule_files(pkg: Path = PKG) -> dict[int, Path]:
    """{number: path} for every dyad/rules/RULE-<n>-*.md."""
    out = {}
    for p in sorted((pkg / "rules").glob("RULE-*.md")):
        m = re.match(r"RULE-(\d+)-", p.name)
        if m:
            out[int(m.group(1))] = p
    return out

def plain(text: str) -> str:
    """Strip markdown emphasis so `Y` and *coherent* match their vocabulary terms."""
    return text.replace("`", "").replace("*", "")

# ---- the CLI table (#592 R-a; the S1 surface of `dyad/surface.md`): every `dyad <noun> [<verb>] [flags]` form, the
# words it takes, and the gate `package.py`'s `__main__` runs before any dispatch. The sub-parsers stay where they are
# (each noun's own module); the gate only refuses a flag no form of that verb takes and answers `-h`/`--help` with the
# form's usage, then passes `a` through unchanged (plan #592 F2). A flag that takes a value takes the next word whole,
# whatever it spells (`dwork state 1 open --said -x`), as `package.dwork_args` reads it (#133). `check` picks its
# form by the first mode flag in `__main__`'s own order (CHECK_MODES), every other noun by the word after it; a noun
# with a `None` verb has a form of its own for any other word. `package.DWORK_VERB_FLAGS` and `DWORK_VALUE_FLAGS` are
# views of this table; every other module's own flag constant is pinned to it by `dyad/tests/test_cli.py`.
class CliForm(tuple):
    """(positionals as usage shows them, ((flag, metavar), …) for the flags that take a value, (flag, …) for the bare
    ones, (flag, …) for the flags that may be given more than once, the index of the positional from which every word
    is free text or None). Every other flag is read once: a second copy is refused, never silently kept over the first
    (the Operator's words would be lost). The positional bound, `most`, is read off `pos`: one per `<…>`, none when it
    holds `...` (k words) or the form has free text."""
    __slots__ = ()
    def __new__(cls, pos: str = "", values: tuple = (), bare: tuple = (), repeat: tuple = (), text: int | None = None):
        return super().__new__(cls, (pos, tuple(values), tuple(bare), tuple(repeat), text))
    pos = property(lambda s: s[0])
    values = property(lambda s: s[1])
    bare = property(lambda s: s[2])
    repeat = property(lambda s: s[3])
    text = property(lambda s: s[4])
    most = property(lambda s: None if s[4] is not None or "..." in s[0] else s[0].count("<"))
    value_flags = property(lambda s: tuple(f for f, _ in s[1]))
    flags = property(lambda s: tuple(f for f, _ in s[1]) + s[2])

class CliRead(tuple):
    """What `cli_parse` read: positionals, {value flag: [values]} (a flag given last, with no value, maps to []), the
    bare flags given, the unknown flags, the positionals past the form's bound, the flags given twice that may not be,
    and whether `-h`/`--help` was a word."""
    __slots__ = ()
    pos = property(lambda s: s[0]); values = property(lambda s: s[1]); bare = property(lambda s: s[2])
    unknown = property(lambda s: s[3]); extra = property(lambda s: s[4]); twice = property(lambda s: s[5])
    helped = property(lambda s: s[6])
    def one(self, flag: str) -> str | None:
        """The value given to `flag`, or None when it was not given or given last with no value."""
        return self[1][flag][0] if self[1].get(flag) else None

HELP_FLAGS = ("-h", "--help")
FLAG_SHAPE = re.compile(r"--?[A-Za-z][A-Za-z0-9-]*")   # a word read as a flag: `-x`, `--x-y`; `-`, `-1 rows`, `- item` are words
CHECK_MODES = ("--evidence", "--corroborate", "--pr", "--guards", "--list", "--tests")   # `__main__`'s order of tests
LAND_FLAG = "--land"
LAND_FLAGS = (("--mirror", "<branch>"),)   # `dwork new|state … --land [--mirror <branch>]`: land.py's, beside the verb's own (#447)
_SAID = (("-d", "<entry>"), ("--said", "<words>"), ("--said-file", "<file>"))
CLI: dict[tuple[str, str | None], CliForm] = {
    ("check", None):            CliForm(),
    ("check", "--list"):        CliForm(),
    ("check", "--guards"):      CliForm("[<remote> <url>]", (), ("--pre-push",)),
    ("check", "--corroborate"): CliForm("[<before> [<after>]]"),
    ("check", "--pr"):          CliForm("<base> [<head>]"),
    ("check", "--tests"):       CliForm("[<target>]"),
    ("check", "--evidence"):    CliForm("", (("--at", "<rev>"), ("--show", "<sha256>")), ("--brief",)),
    ("build", None):            CliForm("[<out>]"),
    ("install", None):          CliForm("<repo>", (("--from", "<src>"),)),
    ("bundle", "check"):        CliForm(),
    ("bundle", "build"):        CliForm("[<dir>]"),
    ("craft", "new"):           CliForm("<name>"),
    ("craft", "list"):          CliForm(),
    ("craft", "check"):         CliForm("[<craft>]"),
    ("craft", "export"):        CliForm("<craft> [<out>]"),
    ("craft", "install"):       CliForm("<src>", (("--dwork", "<N>"), ("--craft", "<name>"), ("--source", "<text>")), ("--force",)),
    ("craft", "diff"):          CliForm("<craft>", (("--against", "<src>"),), ("--patch",)),
    ("ledger", None):           CliForm(),
    ("dwork", "new"):           CliForm("<title> [<refs>]", (_SAID[0], ("-r", "<refs>"), ("--prompt", "<words>"), ("--prompt-file", "<file>"),
                                                             *_SAID[1:], ("--relayed-via", "<seat>"), ("--mandate", "<id>")) + LAND_FLAGS, ("--backlog", LAND_FLAG)),
    ("dwork", "state"):         CliForm("<id> <state>", (_SAID[0], ("-r", "<refs>"), ("--prompt", "<words>"), ("--prompt-file", "<file>"),
                                                         *_SAID[1:], ("--said-ref", "<ref>"), ("--relayed-via", "<seat>"),
                                                         ("--mandate", "<id>"), ("--retired-by", "<id>")) + LAND_FLAGS,
                                        ("--check", LAND_FLAG)),
    ("dwork", "retire"):        CliForm("<id>...", _SAID),
    ("dwork", "list"):          CliForm("", (("--state", "<state>"), ("--craft", "<craft>"))),
    ("dwork", "land"):          CliForm("<path>...", (("-m", "<message>"),) + LAND_FLAGS),
    ("dwork", "batch"):         CliForm("<file>|-", LAND_FLAGS, (LAND_FLAG,)),
    ("dwork", "intent"):        CliForm("<id>"),   # #615: the intent reading's candidates, ranked, no threshold
    ("dwork", "trace"):         CliForm("<id>", (("--transcript", "<path>"), ("--said-file", "<file>")), ("--out",), ("--transcript",)),
    ("plan", "check"):          CliForm("<id>"),
    ("session", None):          CliForm("[<root>]"),
    ("session", "name"):        CliForm("", (("--function", "<f>"), ("--topic", "<t>"), ("--hp", "<8 hex>"), ("--system", "<handle>"), ("--on", "<text>"))),
    ("session", "touch"):       CliForm("", (("-r", "<rows>"), ("-f", "<file>")), (), ("-r", "-f")),
    ("session", "list"):        CliForm(),
    ("session", "reconcile"):   CliForm(),
    ("project", None):          CliForm("[<surface>]", (("--craft", "<name>"),), ("--list",)),   # --craft: the kanban projector's (#22)
    ("runbook", "check"):       CliForm(),
    ("runbook", "list"):        CliForm("<instance>"),
    ("runbook", "run"):         CliForm("<instance> <name>", (("--as", "operator|agent|automaton"),)),
    ("runbook", "new"):         CliForm("<instance>"),
    ("release", None):          CliForm("", (), ("--scan",)),
    ("release", "ready"):       CliForm("<row> <tag>", (("--at", "<cut>"), ("--archive", "<sha256>"))),
    ("merge", None):            CliForm("<pr>", (("--head", "<sha>"),)),
    ("board", None):            CliForm(),
    ("board", "set"):           CliForm("<id>|_cos[-<operator>] key=value...", (), ("--drop",)),
    ("board", "resume"):        CliForm(),
    ("board", "advance"):       CliForm("<id>... <event> key=value...", (("--expect", "<phase>|none"), ("--said-file", "<path>"),
                                                                       ("--mirror", "<branch>"))),
    ("board", "phases"):        CliForm(),
    ("board", "draft"):         CliForm("<id>", (("--out", "<file>"),)),   # #587 X7: the Done skeleton, read-only
    ("inbox", "post"):          CliForm("<unit> [<body>...]", (("--row", "<id>"), ("--kind", "report|relay|ack|notice"),
                                                               ("--body-file", "<path>"), ("--cc", "<unit>")), (), ("--cc",), 1),
    ("inbox", "read"):          CliForm("[<message>...]"),   # #587 S10: no names prints, names mark; `--all` removed
    ("inbox", "list"):          CliForm("[<unit>]"),
    ("automaton", "scan"):      CliForm(),
    ("automaton", "run"):       CliForm("", (("--evidence-from", "<file>"),)),
    ("automaton", "evidence"):  CliForm("", (("--out", "<file>"),)),
    ("automaton", "sweep"):     CliForm("", (("--row", "<id>"),), ("--stores",)),   # #617: --stores, the whole-store guards only
    ("steps", "verify-prs"):    CliForm(),
    ("steps", "done-record"):   CliForm("", (), (LAND_FLAG,)),
    ("steps", "close-landed"):  CliForm("", (), (LAND_FLAG,)),
    ("steps", "sync-mirror"):   CliForm(),
    ("bootstrap", None):        CliForm("", (), ("--check",)),
}

def cli_nouns() -> tuple[str, ...]:
    return tuple(dict.fromkeys(n for n, _ in CLI))

def cli_forms(noun: str, verbs=None) -> dict[str | None, CliForm]:
    """{verb: form} of one noun, every verb or the ones named: the `CLI_FLAGS` a module's own parser reads (#592 F3)."""
    return {v: f for (n, v), f in CLI.items() if n == noun and (verbs is None or v in verbs)}

def cli_usage(key: tuple[str, str | None]) -> str:
    """`usage: dyad <noun> [<verb>] <positionals> [<flag> <metavar>]… [<flag>]…` for one form."""
    f = CLI[key]
    words = ["dyad", key[0], *([key[1]] if key[1] else []), *([f.pos] if f.pos else []),
             *(f"[{flag} {meta}]" for flag, meta in f.values), *(f"[{flag}]" for flag in f.bare)]
    return "usage: " + " ".join(words)

def cli_form(a: list[str]) -> tuple[tuple[str, str | None] | None, list[str]]:
    """(the form `a` names, the words after its noun and verb); (None, …) when the noun has no form for it — an
    unknown noun, or a word after the noun that is no verb of a noun without a `None` form: its module answers."""
    if not a or a[0] not in cli_nouns():
        return None, a[1:]
    noun, rest = a[0], a[1:]
    if noun == "check":
        flagged = [m for m in CHECK_MODES if m in rest]   # `__main__` tests `in a`, in this order
        return ("check", flagged[0] if flagged else None), [x for x in rest if not flagged or x != flagged[0]]
    if rest and (noun, rest[0]) in CLI:
        return (noun, rest[0]), rest[1:]
    if (noun, None) in CLI:
        return (noun, None), rest
    return None, rest

def cli_parse(form: CliForm, rest: list[str]) -> CliRead:
    """The gate's one reading of the words after a form's noun and verb, which a module that reads flags by hand
    calls too, so both read `a` alike (#592): a value flag takes the next word whole, whatever it spells
    (`dwork state 1 open --said -x`); a word not shaped like a flag (`-`, `- item`, `-1 rows`) is a positional; from
    the form's free-text positional on (`inbox post`'s body) every word not one of its flags is a positional."""
    pos, vals, bare, unknown, twice, helped, seen, i = [], {}, [], [], [], False, set(), 0
    value_flags = set(form.value_flags)
    while i < len(rest):
        x = rest[i]
        if x in value_flags or x in form.bare:
            if x in seen and x not in form.repeat and x not in twice:
                twice.append(x)
            seen.add(x)
            if x in form.bare:
                bare.append(x); i += 1; continue
            vals.setdefault(x, []).extend(rest[i + 1:i + 2])
            i += 2; continue
        if x in HELP_FLAGS:
            helped = True
        elif FLAG_SHAPE.fullmatch(x) and (form.text is None or len(pos) < form.text):
            unknown.append(x)
        else:
            pos.append(x)
        i += 1
    extra = pos[form.most:] if form.most is not None else []
    return CliRead((pos, vals, bare, unknown, extra, twice, helped))

def cli_words(form: CliForm, rest: list[str]) -> tuple[list[str], bool]:
    """(the unknown flags in `rest`, whether `-h`/`--help` is one of its words): `cli_parse`, two of its fields."""
    r = cli_parse(form, rest)
    return r.unknown, r.helped

def _noun_value_flags(noun: str) -> set[str]:
    return {f for (n, _), x in CLI.items() if n == noun for f in x.value_flags}

def cli_gate(a: list[str], doc: str | None = None, out=None, err=None) -> int | None:
    """Before any dispatch (#592 R-a): None to run `a` as given; else the exit code, after printing — the usage and
    0 for `-h`/`--help` anywhere outside a flag's value (nothing else runs: no child, no write), one `refused:` line
    and 1 for a flag the form does not take (`refused: dyad <noun> <verb> does not take <flag>`), a word past the
    form's positionals (`… does not take <word>`) or a flag given twice that is read once (`… takes <flag> once`)."""
    out, err = out or sys.stdout, err or sys.stderr
    if a and a[0] in HELP_FLAGS:
        print(doc or "\n".join(cli_usage(k) for k in CLI), file=out); return 0
    key, rest = cli_form(a)
    if key is None:
        if a and a[0] in cli_nouns() and rest:
            noun = a[0]
            forms = [k for k in CLI if k[0] == noun]
            vals, i, helped = _noun_value_flags(noun), 0, False
            while i < len(rest):   # `--help` before the verb, or after an unknown one, outside any of the noun's values
                if rest[i] in vals:
                    i += 2; continue
                helped = helped or rest[i] in HELP_FLAGS; i += 1
            if helped:
                print("\n".join(cli_usage(k) for k in forms), file=out); return 0
            if FLAG_SHAPE.fullmatch(rest[0]) and not any(rest[0] in CLI[k].flags for k in forms):
                print(f"refused: dyad {noun} does not take {rest[0]}", file=err); return 1   # a known flag before the verb: its module's
        return None
    r = cli_parse(CLI[key], rest)
    if r.helped:
        forms = [k for k in CLI if k[0] == key[0]] if key[1] is None else [key]
        print("\n".join(cli_usage(k) for k in forms), file=out); return 0
    name = " ".join(w for w in key if w)
    if r.unknown or r.extra:
        print(f"refused: dyad {name} does not take {' '.join(r.unknown + r.extra)}", file=err); return 1
    if r.twice:
        print(f"refused: dyad {name} takes {' '.join(r.twice)} once", file=err); return 1
    return None

# crafts/syseng/rules/invariants.md: the architectural facts this module's tables encode, enforced at import (the
# call at the bottom), run again by the runner's pass and before every row write (`dyad dwork new|state`). Each
# names a fact a guard or a past incident relied on.
INVARIANTS: list[Invariant] = [
    ("transitions-keys-are-states", lambda: set(TRANSITIONS) == STATES),
    ("transition-targets-are-states", lambda: all(t <= STATES for t in TRANSITIONS.values())),
    ("new-states-are-states", lambda: NEW_STATES <= STATES),
    ("archived-is-terminal", lambda: not TRANSITIONS["archived"]),
    ("done-never-reopens", lambda: TRANSITIONS["done"] == frozenset({"archived"})),   # its one step is archived (#37)
    ("no-self-transition", lambda: all(s not in t for s, t in TRANSITIONS.items())),   # same state is `allowed`'s edit, never a table entry (#203)
    ("row-fields-match-dataclass", lambda: FIELDS + OPTIONAL_FIELDS == tuple(f.name for f in fields(Row))),
    ("row-optional-fields-disjoint", lambda: not (set(FIELDS) & set(OPTIONAL_FIELDS))),   # #290: a key in both would be required and optional at once
    ("row-mode-default-is-a-mode", lambda: DEFAULT_MODE in MODES and len(MODES) == 2),    # #290: the value an absent line takes is a legal mode
    ("backlog-exits-to-archived", lambda: TRANSITIONS["backlog"] == frozenset({"open", "archived"})),   # #290: the board's drain
    ("table-cell-escape-round-trips", lambda: split_cells(f"| {escape_cell('a | b')} | c |") == ["a | b", "c"]),   # #7, #171: a rendered `|` stays in its cell
    ("inputs-cover-the-machine", lambda: set(INPUTS) == {(a, b) for a, t in TRANSITIONS.items() for b in t} | {(None, s) for s in NEW_STATES}),   # #309: one input per edge and per birth
    ("input-kinds-known", lambda: all(k and k <= INPUT_KINDS for _, k in INPUTS.values())),
    ("terminal-states-stay-terminal", lambda: TERMINAL_STATES <= STATES and all(TRANSITIONS[s] <= {"archived"} for s in TERMINAL_STATES)),
    ("only-the-operator-closes", lambda: all(k == {"disposition"} for (_, to), (_, k) in INPUTS.items() if to in TERMINAL_STATES)),   # #309: Rule-2 — Done-Y and the retirement form
    ("no-self-initiation", lambda: all("clerical" not in INPUTS[(None, s)][1] for s in NEW_STATES)),   # #309: countersign I6 — a row is born on the Operator's words
    ("backlog-opens-on-a-prompt", lambda: INPUTS[("backlog", "open")][1] == {"prompt"}),   # #309: Rule-7's transaction check binds the edge to a `prompt` entry
    ("host-classes-distinct", lambda: len(set(HOST_CLASSES)) == 3),
    ("git-vars-distinct", lambda: len(set(GIT_VARS)) == len(GIT_VARS) and all(v.startswith("GIT_") for v in GIT_VARS)),
    ("index-modes-differ", lambda: MODE_EXEC != MODE_FILE and MODE_EXEC.endswith("755")),
    ("plan-parts-distinct", lambda: len(set(PLAN_PARTS)) == len(PLAN_PARTS) == 6 and "base commit" in PLAN_PARTS
                                    and PLAN_PARTS[-1] == "definition of done"),   # Rule-15 phase 1's six parts (#203, #574)
    ("dod-since-is-a-date", lambda: bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", DOD_SINCE))),
    ("semver-accepts-build-metadata", lambda: bool(SEMVER.fullmatch("1.2.3")) and bool(SEMVER.fullmatch("1.2.3+local.1")) and not SEMVER.fullmatch("1.2")),
    ("semver-tuple-strips-build", lambda: semver_tuple("1.2.3+local.1") == (1, 2, 3)),
    ("host-default-zone-allowed", lambda: DEFAULT_HOST_ZONE in HOST_ZONES and len(set(HOST_ZONES)) == len(HOST_ZONES)),
    ("host-corpus-is-default-zone", lambda: HOST_CORPUS == DEFAULT_HOST_ZONE),
    ("host-default-path-relative", lambda: bool(DEFAULT_HOST) and not DEFAULT_HOST.startswith("/") and not DEFAULT_HOST.endswith("/")),
    ("check-inputs-known", lambda: all(v and set(v) <= set(CHECK_INPUT_NAMES) for v in CHECK_INPUTS.values())
                                   and set(INPUT_TRIGGERS) == set(CHECK_INPUT_NAMES)
                                   and all(t and d for t, d in INPUT_TRIGGERS.values())
                                   and set(SWEEP_PARTS) | {"suite", "suite:live"} <= set(CHECK_INPUTS)),   # #618
    ("tunable-value-reads-allowed", lambda: tunable_value("7 days", 1, "a positive integer (days)") == 7
        and tunable_value("-2", 1, "a positive integer") is None and tunable_value("none", 1, "a positive integer") is None
        and tunable_value("0.5", 0.35, "a number between 0 and 1") == 0.5 and tunable_value("1", 0.35, "a number between 0 and 1") is None),   # #590
    ("cli-flags-are-flags", lambda: all(f.startswith("-") and f not in HELP_FLAGS and f != "-" for x in CLI.values() for f in x.flags)),   # #592 R-a
    ("cli-form-flags-distinct", lambda: all(len(set(x.flags)) == len(x.flags) for x in CLI.values())),   # a flag takes a value or none, never both
    ("cli-check-modes-are-its-forms", lambda: set(CHECK_MODES) == {v for n, v in CLI if n == "check" and v}
                                              and all(v is None or not v.startswith("-") for n, v in CLI if n != "check")),
    ("cli-land-rides-new-and-state", lambda: all("--land" in CLI[("dwork", v)].bare and "--mirror" in CLI[("dwork", v)].value_flags for v in ("new", "state"))),
    ("cli-a-value-is-never-a-flag", lambda: cli_words(CLI[("dwork", "state")], ["1", "open", "--said", "-x", "-d", "--help"]) == ([], False)
                                            and cli_words(CLI[("dwork", "batch")], ["-", "--land"]) == ([], False)
                                            and cli_words(CLI[("check", "--guards")], ["--pre-push", "--bogus", "-h"]) == (["--bogus"], True)),
    ("cli-a-word-not-shaped-as-a-flag-is-a-word", lambda: cli_parse(CLI[("check", "--tests")], ["-1 rows"]).pos == ["-1 rows"]
                                                         and cli_parse(CLI[("inbox", "post")], ["cos", "- item", "-urgent", "--row", "5"]).pos
                                                             == ["cos", "- item", "-urgent"]
                                                         and cli_parse(CLI[("inbox", "post")], ["--bogus"]).unknown == ["--bogus"]),
    ("cli-positionals-bounded-by-the-form", lambda: cli_parse(CLI[("check", "--list")], ["x"]).extra == ["x"]
                                                    and cli_parse(CLI[("dwork", "retire")], ["1", "2", "3"]).extra == []
                                                    and (CLI[("dwork", "new")].most, CLI[("dwork", "list")].most, CLI[("dwork", "retire")].most) == (2, 0, None)),
    ("cli-a-flag-read-once-is-given-once", lambda: cli_parse(CLI[("dwork", "new")], ["t", "--prompt", "a", "--prompt", "b"]).twice == ["--prompt"]
                                                   and cli_parse(CLI[("inbox", "post")], ["x", "--cc", "a", "--cc", "b"]).twice == []
                                                   and all(f in x.flags for x in CLI.values() for f in x.repeat)),
    ("cli-text-index-within-the-positionals", lambda: all(x.text is None or 0 <= x.text <= x.pos.count("<") for x in CLI.values())),
    ("cli-check-form-by-mode-order", lambda: cli_form(["check", "--brief", "--evidence"]) == (("check", "--evidence"), ["--brief"])
                                             and cli_form(["check", "--tests", "x"]) == (("check", "--tests"), ["x"])),
    ("events-store-relative", lambda: bool(EVENTS_REL) and not EVENTS_REL.startswith("/") and not EVENTS_REL.endswith("/") and "d-work" not in EVENTS_REL),   # #438: the event store never overlaps the ledger
    *orch_invariants(ORCH_EVENTS),   # #587: the board entry's orchestration machine (X1-X4, X9)
]
TREE_INVARIANTS: list[Invariant] = [   # reads the DMC store, so the runner's pass only, never at import
    ("tunable-defaults-valid", lambda: all(isinstance(tunable_default(t["dyad:preference"]), (int, float))
                                           for _, t in _tunable_entries())),   # #590: every default parses and is allowed
]

enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
