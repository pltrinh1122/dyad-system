"""dyad package: shared path resolution, ledger and Rule parsing, and the guard registry loader over two
roots — the core craft's `dyad/guards/` and every Tended craft's `crafts/<craft>/guards/` (Rule-11 property 3;
crafts/sysarch/rules/guards.md; #155). Owns no check semantics (S4). Kernel: Python 3.12+."""
import importlib.util, os, re, subprocess, sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Callable

PKG = Path(__file__).resolve().parent.parent
GUARDS = PKG / "guards"

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
    craft = [p for p in craft_glob("guards/*.py", pkg) if not p.name.startswith("_")]
    return core + craft

def guard_key(py: Path, pkg: Path = PKG) -> tuple[str, str, str]:
    """(root, group, entity): ('core', <corpus>, <entity>) for dyad/guards/<corpus>/<entity>.py,
    ('craft', <craft>, <entity>) for crafts/<craft>/guards/<entity>.py. The registry label is `<group>/<entity>`."""
    if py.is_relative_to(pkg / "guards"):
        return ("core", py.parent.name, py.stem)
    return ("craft", py.parents[1].name, py.stem)

def load_module(path: Path, name: str | None = None):
    """Import a Python file by path without writing bytecode (file counts stay deterministic).
    The module is cached in sys.modules under `name` (default: the file stem) so two loaders of
    the same file share one module object."""
    name = name or path.stem
    if name in sys.modules and getattr(sys.modules[name], "__file__", None) == str(path):
        return sys.modules[name]
    prev, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
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

# ---- run-time invariants (crafts/syseng/rules/invariants.md): a module declares `INVARIANTS`, a list of
# (name, predicate) pairs over its own constants; the runner checks them before any check and the mutating
# call sites (dwork new|state, runbook run) before they write. Never at import, never `assert`.
Invariant = tuple[str, Callable[[], bool]]

class InvariantError(Exception):
    """A module's invariants did not hold: `module` is its label, `failed` the names, sorted."""
    def __init__(self, module: str, failed: list[str]):
        self.module, self.failed = module, list(failed)
        super().__init__(f"{module}: invariant(s) failed: {', '.join(self.failed)}")

def invariants_of(source, extra=()) -> list[Invariant]:
    """The entries of a module's `INVARIANTS` (or of a list passed directly) plus `extra`, sorted by name;
    a module with no `INVARIANTS` yields the extras only (which modules must declare one is the syseng
    guard's question, crafts/syseng/guards/invariants.py)."""
    own = source if isinstance(source, (list, tuple)) else getattr(source, "INVARIANTS", ())
    return sorted(list(own) + list(extra), key=lambda e: e[0] if isinstance(e, tuple) and e else str(e))

def check_invariants(source, extra=(), label: str | None = None) -> int:
    """Run every invariant of `source` (a module or a list); raise InvariantError naming the false ones (a
    predicate that raises counts as false); return the number checked."""
    entries = invariants_of(source, extra)
    failed = []
    for name, pred in entries:
        try:
            ok = bool(pred())
        except Exception:
            ok = False
        if not ok:
            failed.append(name)
    if failed:
        raise InvariantError(label or getattr(source, "__name__", "invariants"), failed)
    return len(entries)

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
    """Every `crafts/<craft>/projectors/project_<surface>.py`, sorted by craft then surface (the registry's discovery order)."""
    return craft_glob("projectors/project_*.py", pkg)

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
    return sorted(p for p in d.iterdir() if p.is_dir() and (p / "VERSION").exists()) if d.is_dir() else []

# Rule-8 host-action classes: the change-log row (Rule-8), a run-book command and its event (Rule-19)
# each declare one; the three guards read this tuple.
HOST_CLASSES = ("read-only", "reversible", "destructive")

# git's per-invocation variables: a hook exports them, and a command run from the work tree then reads
# another repository's dir, tree or index (d-work #142). Every git call here runs without them.
GIT_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
MODE_EXEC, MODE_FILE = "100755", "100644"   # the index modes tracked_mode reports (Rule-18's scripts, the hooks and bin/)

def git_env() -> dict[str, str]:
    """`os.environ` without GIT_VARS, for a git call that must see the tree it is pointed at."""
    return {k: v for k, v in os.environ.items() if k not in GIT_VARS}

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

_ROW = re.compile(r"^\|\s*(\d+)\s*\|")

def ledger_rows(text: str) -> list[Row]:
    """Parse ledger table rows. Non-row lines (header, separator, prose) are skipped.
    A duplicated id raises ValueError: the ledger is append-only and ids are unique."""
    rows, seen = [], set()
    for line in text.splitlines():
        if not _ROW.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            raise ValueError(f"ledger row with {len(cells)} cells: {line!r}")
        rid = int(cells[0])
        if rid in seen:
            raise ValueError(f"duplicate ledger id {rid}")
        seen.add(rid)
        rows.append(Row(rid, *cells[1:6]))
    return rows

FIELDS = ("id", "title", "opened", "state", "disposed", "refs")

# d-work states and the one transition table (Rule-16 Store cites this; Rule-3 defines the states).
STATES = frozenset({"open", "planned", "blocked", "backlog", "done"})
NEW_STATES = frozenset({"open", "backlog"})          # states a row may be created in
TRANSITIONS: dict[str, frozenset[str]] = {
    "open": frozenset({"planned", "blocked", "done"}),
    "planned": frozenset({"open", "blocked", "done"}),
    "blocked": frozenset({"open"}),
    "backlog": frozenset({"open"}),
    "done": frozenset(),
}

# Rule-15 phase 1: the parts a plan file carries. The file is prose (no parser); this names the
# parts so a projector (crafts/sysarch/rules/projection.md) can report which a plan mentions, never how it says them.
PLAN_PARTS = ("intent as read", "mutation", "files touched", "base commit", "falsification")

def table_header(text: str) -> list[str]:
    """Column names of the first markdown table in `text`: the `|` line followed by a `|---|`
    separator. Empty when there is none. Used to read a schema from a template or a record."""
    lines = text.splitlines()
    for i, line in enumerate(lines[:-1]):
        nxt = lines[i + 1].strip()
        if line.startswith("|") and nxt.startswith("|") and set(nxt) <= set("|-: "):
            return [c.strip() for c in line.strip().strip("|").split("|")]
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
            out.append([c.strip() for c in s.strip("|").split("|")])
    return out

def tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every markdown table in `text` as (header cells, body rows); a table is a `|` header line
    followed by a `|---|` separator line."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines) - 1:
        line, nxt = lines[i].strip(), lines[i + 1].strip()
        if line.startswith("|") and nxt.startswith("|") and set(nxt) <= set("|-: "):
            header = [c.strip() for c in line.strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            out.append((header, rows))
        else:
            i += 1
    return out

def allowed(a: str, b: str) -> bool:
    """True if a row may go from state `a` to state `b`. Same state is always allowed
    (disposed/refs edits); anything outside TRANSITIONS is refused."""
    return a == b or b in TRANSITIONS.get(a, frozenset())

def parse_row_file(text: str) -> Row:
    """One row file: `key: value` lines in FIELDS order (Rule-16)."""
    d = {}
    for line in text.splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip() in FIELDS:
            d[k.strip()] = v.strip()
    missing = [f for f in FIELDS if f not in d]
    if missing:
        raise ValueError(f"row file missing {missing}")
    return Row(int(d["id"]), d["title"], d["opened"], d["state"], d["disposed"], d["refs"])

def format_row_file(r: Row) -> str:
    return "".join(f"{k}: {getattr(r, k)}\n" for k in FIELDS)

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
        texts = [subprocess.check_output(["git", "show", f"{at}:{rel}/{n}"], cwd=root, text=True)
                 for n in sorted(names, key=lambda n: int(n[:-3]) if n[:-3].isdigit() else -1) if n.endswith(".md") and n[:-3].isdigit()]
    rows = [parse_row_file(t) for t in texts]
    ids = [r.id for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate ledger id in rows/")
    return rows

def render(rows: list[Row]) -> str:
    head = ("# d-work ledger (rendered view, Rule-16; canonical rows in rows/)\n\n"
            "| id | title | opened | state | disposed | refs |\n|----|-------|--------|-------|----------|------|\n")
    return head + "".join(f"| {r.id} | {r.title} | {r.opened} | {r.state} | {r.disposed} | {r.refs} |\n" for r in rows)

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

# crafts/syseng/rules/invariants.md: the architectural facts this module's tables encode, run by the runner's
# pass and before every row write (`dyad dwork new|state`). Each names a fact a guard or a past incident relied on.
INVARIANTS: list[Invariant] = [
    ("transitions-keys-are-states", lambda: set(TRANSITIONS) == STATES),
    ("transition-targets-are-states", lambda: all(t <= STATES for t in TRANSITIONS.values())),
    ("new-states-are-states", lambda: NEW_STATES <= STATES),
    ("done-is-terminal", lambda: not TRANSITIONS["done"]),
    ("row-fields-match-dataclass", lambda: FIELDS == tuple(f.name for f in fields(Row))),
    ("host-classes-distinct", lambda: len(set(HOST_CLASSES)) == 3),
    ("git-vars-distinct", lambda: len(set(GIT_VARS)) == len(GIT_VARS) and all(v.startswith("GIT_") for v in GIT_VARS)),
    ("index-modes-differ", lambda: MODE_EXEC != MODE_FILE and MODE_EXEC.endswith("755")),
    ("plan-parts-distinct", lambda: len(set(PLAN_PARTS)) == len(PLAN_PARTS)),
]
