#!/usr/bin/env python3
"""Naming guard (entity `name`, corpus `craft`; the syseng craft's `rules/naming.md` owns the table; placed per
crafts/sysarch/rules/guards.md under the craft's root; d-work #162). Kernel: Python 3.12+, git.
Reads `naming_rules.txt` beside it: `kind: <pattern> = <path glob> = <regex>` — every path the tree holds
(tracked or not yet committed, `git ls-files -co --exclude-standard`) that the glob selects (`*` one path
segment, `**` any) matches the regex over the whole path, a named group `id` is unique within the kind, a
group `beside` names `<dir>/<beside>.py` that exists (fail); `mode: <pattern> = <path glob> = <tracked mode>` —
every selected path is tracked at that mode in git's index (`dyadlib.tracked_mode`; the bit on disk is not evidence,
`core.fileMode=false` shows 755 for a file tracked 100644, #135/#141), an untracked one warns and falls back to the
disk bit; every `kind:` and `mode:` pattern is a row of the table in
`rules/naming.md` (fail: the data and the table never drift); `symbol: <module glob> : <name|regex> …` — each
selected module defines each plain name at top level and at least one top-level name per regex (fail);
`env: NAME …` — the `DYAD_<NAME>` variables package code reads (`dyad/scripts`, `dyad/guards`, every craft's
`guards/`, `projectors/`, `scripts/`) equal the listed set (fail either way: unlisted or stale); `allow: <path> #
<reason>` — a path a kind claims but that does not match it: no reason fails, a gone package path (`dyad/`, `crafts/`)
fails (the list only shrinks), a gone instance path warns (the data travels to installs whose instance differs), a path
that matches again warns. Whether a name is apt is inference.
  naming.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("naming.py: Python 3.12+ required")
import ast, fnmatch, os, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/syseng/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "name", "craft", False
NAME, OWNER = "naming pattern (table row)", "crafts/syseng/rules/naming.md"
FIELDS = ("pattern", "names", "owner", "example", "checkable")   # the table's columns, in order
CRAFT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / "naming_rules.txt"
TABLE = CRAFT / "rules" / "naming.md"
PACKAGE_ROOTS = ("dyad/", "crafts/")                                   # paths that travel with an install; an allow line for one is stale-fails, for an instance path stale-warns
CODE_GLOBS = ("dyad/scripts/*.py", "dyad/guards/*/*.py", "crafts/*/guards/*.py", "crafts/*/projectors/*.py", "crafts/*/scripts/*.py")   # where `env:` is scanned
_ENV = re.compile(r"""environ(?:\.get)?\s*[\[(]\s*["'](DYAD_[A-Z_]+)["']""")
_TICK = re.compile(r"`([^`]+)`")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-are-the-table-columns", lambda: FIELDS == ("pattern", "names", "owner", "example", "checkable")),
    ("code-globs-select-python", lambda: all(g.endswith(".py") for g in CODE_GLOBS)),
    ("package-roots-are-craft-trees", lambda: PACKAGE_ROOTS == ("dyad/", "crafts/")),
]

# ---- data
def parse_rules(text: str) -> dict[str, list]:
    """{'kind': [(pattern, glob, regex)], 'mode': [(pattern, glob, tracked mode)], 'symbol': [(glob, [tokens])],
    'env': [names], 'allow': [(path, reason)]}. Malformed lines are kept under 'bad' with their text."""
    out = {"kind": [], "mode": [], "symbol": [], "env": [], "allow": [], "bad": []}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        if key in ("kind", "mode") and rest.count(" = ") >= 2:
            pattern, glob, value = (x.strip() for x in rest.split(" = ", 2))
            out[key].append((pattern, glob, value))
        elif key == "symbol" and " : " in rest:
            glob, toks = rest.split(" : ", 1)
            out["symbol"].append((glob.strip(), toks.split()))
        elif key == "env":
            out["env"].extend(rest.split())
        elif key == "allow":
            path, _, reason = rest.partition("#")
            out["allow"].append((path.strip(), reason.strip()))
        else:
            out["bad"].append(line)
    return out

def load_rules(path: Path = DATA) -> dict[str, list]:
    return parse_rules(path.read_text())

def table_patterns(table: Path = TABLE) -> set[str]:
    """Every backticked token of the table's first column (`rules/naming.md`)."""
    if not table.exists():
        return set()
    return {t for _h, rows in dyadlib.tables(table.read_text()) for r in rows if r for t in _TICK.findall(r[0])}

def rows(table: Path = TABLE) -> list[dict[str, str]]:
    """The table as the entities surface shows it (FIELDS)."""
    if not table.exists():
        return []
    ts = [(h, r) for h, r in dyadlib.tables(table.read_text()) if [c.strip() for c in h] == list(FIELDS)]
    return [dict(zip(FIELDS, r)) for _h, rs in ts[:1] for r in rs if len(r) == len(FIELDS)]

# ---- selection
def glob_re(glob: str) -> re.Pattern:
    """A path glob: `**` spans segments, `*` one segment, `?` one character; anchored over the whole path."""
    out, i = "", 0
    while i < len(glob):
        c = glob[i]
        if glob.startswith("**", i):
            out += ".*"; i += 2
        elif c == "*":
            out += "[^/]*"; i += 1
        elif c == "?":
            out += "[^/]"; i += 1
        else:
            out += re.escape(c); i += 1
    return re.compile(f"^{out}$")

def tree_paths(root: Path) -> list[str]:
    """Every path the tree holds: tracked plus untracked-not-ignored (a guard sees a file before its commit)."""
    out = subprocess.check_output(["git", "ls-files", "-co", "--exclude-standard"], cwd=root, text=True).split("\n")
    return sorted({p for p in out if p})

def instance_rel(root: Path) -> str:
    inst = dyadlib.instance(root)
    return str(inst.relative_to(root)) if inst.is_relative_to(root) else str(inst)

def top_names(py: Path) -> set[str]:
    """Module-level names a Python file binds (assignments, defs, classes)."""
    names = set()
    for n in ast.parse(py.read_text(errors="ignore"), filename=str(py)).body:
        if isinstance(n, ast.Assign):
            names |= {t.id for tg in n.targets for t in (tg.elts if isinstance(tg, ast.Tuple) else [tg]) if isinstance(t, ast.Name)}
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            names.add(n.target.id)
        elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            names.add(n.name)
    return names

# ---- checks
def check_kinds(paths: list[str], kinds, allow: dict[str, str], inst: str, root: Path) -> tuple[list[str], set[str]]:
    """(messages, paths an allow line covered). Each selected path matches its kind's regex or is allowed."""
    msgs, used = [], set()
    for pattern, glob, regex in kinds:
        sel, rx = glob_re(glob.replace("<instance>", inst)), re.compile("^" + regex.replace("<instance>", re.escape(inst)) + "$")
        ids: dict[str, str] = {}
        for p in paths:
            if not sel.match(p):
                continue
            m = rx.match(p)
            if not m:
                if p in allow:
                    used.add(p); continue
                msgs.append(f"{p}: does not match `{pattern}` ({regex})"); continue
            gd = m.groupdict()
            if gd.get("id") is not None:
                if gd["id"] in ids:
                    msgs.append(f"{p}: id {gd['id']!r} already used by {ids[gd['id']]} (`{pattern}`)")
                ids.setdefault(gd["id"], p)
            if gd.get("beside") is not None and not (root / Path(p).parent / f"{gd['beside']}.py").exists():
                msgs.append(f"{p}: no {Path(p).parent}/{gd['beside']}.py beside it (`{pattern}`)")
    return msgs, used

def check_table(kinds, patterns: set[str], label: str = "kind") -> list[str]:
    return [f"naming_rules.txt: {label} `{pattern}` is not a row of rules/naming.md" for pattern, _g, _r in kinds if pattern not in patterns]

def check_modes(paths: list[str], modes, root: Path, inst: str) -> list[str]:
    """Every path a `mode:` glob selects is tracked at the stated mode. The mode git records, never
    `os.access(p, os.X_OK)`: on a checkout with `core.fileMode=false` (NTFS) every file reads 755 on
    disk whatever the index holds, which shipped an entrypoint tracked 100644 that could not exec and
    passed three ops scripts (#135, #141). A path not yet in the index warns and falls back to the disk
    bit, so a file added in this working tree is judged before its commit."""
    msgs = []
    for pattern, glob, mode in modes:
        sel = glob_re(glob.replace("<instance>", inst))
        for p in (q for q in paths if sel.match(q)):
            tracked = dyadlib.tracked_mode(root, p)
            if tracked is None:
                msgs.append(f"warning: {p}: untracked: disk mode used (`{pattern}` wants {mode})")
                if mode == dyadlib.MODE_EXEC and not os.access(root / p, os.X_OK):
                    msgs.append(f"{p}: not executable on disk and not tracked (`{pattern}` wants {mode})")
            elif tracked != mode:
                hint = " (git update-index --chmod=+x)" if mode == dyadlib.MODE_EXEC else ""
                msgs.append(f"{p}: tracked mode {tracked}, not {mode} (`{pattern}`){hint}")
    return msgs

def check_symbols(paths: list[str], symbols, root: Path) -> list[str]:
    msgs = []
    for glob, toks in symbols:
        sel = glob_re(glob)
        for p in (q for q in paths if sel.match(q) and q.endswith(".py") and not Path(q).name.startswith("_")):
            names = top_names(root / p)
            for t in toks:
                if _IDENT.match(t):
                    if t not in names:
                        msgs.append(f"{p}: defines no top-level `{t}` (symbol rule {glob})")
                elif not any(re.fullmatch(t, n) for n in names):
                    msgs.append(f"{p}: no top-level name matches /{t}/ (symbol rule {glob})")
    return msgs

def env_names(paths: list[str], root: Path) -> dict[str, list[str]]:
    """{DYAD_<NAME>: [file, …]} read by package code."""
    found: dict[str, list[str]] = {}
    sels = [glob_re(g) for g in CODE_GLOBS]
    for p in paths:
        if any(s.match(p) for s in sels):
            for name in _ENV.findall((root / p).read_text(errors="ignore")):
                found.setdefault(name, []).append(p)
    return found

def check_env(found: dict[str, list[str]], listed: list[str]) -> list[str]:
    msgs = [f"{', '.join(sorted(set(ws)))}: reads {n}, not in the naming table (`DYAD_<NAME>` row / `env:` line)" for n, ws in sorted(found.items()) if n not in listed]
    msgs += [f"naming_rules.txt: env {n} is listed but no package code reads it (stale)" for n in listed if n not in found]
    return msgs

def check_allow(allow: list[tuple[str, str]], paths: set[str], used: set[str]) -> list[str]:
    msgs = []
    for path, reason in allow:
        if not reason:
            msgs.append(f"naming_rules.txt: allow {path} has no reason")
        if path not in paths:
            if path.startswith(PACKAGE_ROOTS):
                msgs.append(f"naming_rules.txt: allow {path} is stale (no such path); remove the line")
            else:   # an instance path differs per install; the craft's data travels, so absence warns here and fails only where the path is package
                msgs.append(f"warning: naming_rules.txt: allow {path} names no path of this tree (an instance path; remove the line if it is gone for good)")
        elif path not in used:
            msgs.append(f"warning: naming_rules.txt: allow {path} is no longer needed (the path matches its pattern)")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG, data: Path = DATA, table: Path = TABLE) -> list[str]:
    root = Path(root or dyadlib.repo_root())
    r = load_rules(data)
    msgs = [f"naming_rules.txt: malformed line {l!r}" for l in r["bad"]]
    paths = tree_paths(root)
    allow = dict(r["allow"])
    inst = instance_rel(root)
    m, used = check_kinds(paths, r["kind"], allow, inst, root)
    pats = table_patterns(table)
    msgs += m + check_table(r["kind"], pats) + check_table(r["mode"], pats, "mode") + check_symbols(paths, r["symbol"], root)
    msgs += check_modes(paths, r["mode"], root, inst)
    msgs += check_env(env_names(paths, root), r["env"]) + check_allow(r["allow"], set(paths), used)
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    r = load_rules()
    return f"{len(rows())} patterns, {len(r['kind'])} kinds, {len(r['mode'])} mode rules, {len(r['symbol'])} symbol rules, {len(r['allow'])} allowed"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    rs = rows(); ex = rs[0] if rs else {}
    meaning = {"pattern": "the shape, `<…>` for a variable part", "names": "the kind of thing the pattern names", "owner": "the core Rule or craft rule that owns it",
               "example": "one name in the tree", "checkable": "`yes` (a `kind:`/`mode:`/`symbol:`/`env:` line of naming_rules.txt) or `no` (inference or another guard)"}
    return {"store": "crafts/syseng/rules/naming.md (the table); crafts/syseng/guards/naming_rules.txt (its checkable half)", "parser": "`naming.rows` / `naming.parse_rules`",
            "observed": len(rs), "note": "one owner per pattern; every kind and mode line is a table row; a mode is the tracked one; allow lines carry a reason and only shrink",
            "fields": [(f, "text", meaning[f], True, ex.get(f, ""), "naming.FIELDS") for f in FIELDS]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"):
            print(f"warn [naming] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [naming] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [naming] {summary(root)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
