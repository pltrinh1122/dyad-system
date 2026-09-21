#!/usr/bin/env python3
"""Manifest guard (entity `component`, infra corpus; Rule-14 owns the check, placed per Rule-11 property 1). Kernel: Python 3.12+.
The manifest (infrastructure/INFRASTRUCTURE.md) is well-formed and every invocation token the
package makes — shebang interpreters, subprocess argv[0], shell command words in hooks and
`.sh` files, `uses:` and `run:` words in the dyad-* workflows, and third-party Python `import`s
(token `import:<module>`) — maps, through guards/infra/manifest_rules.txt (beside this guard), to
a declared component. An unmapped token FAILs; a declared component with no token in the rules
file (and no `-` marking it never invoked) warns. Imports are classified stdlib
(`sys.stdlib_module_names`, covered by the kernel row Python) / package-internal (a `<name>.py`
in scripts/, guards/*/ or tests/**, or a relative import — The Dyad System, not The World) /
third-party; only third-party needs a row. Whether a row's version, license or replacement is
*right* is inference (Rule-13 criteria).
  manifest.py
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("manifest.py: Python 3.12+ required")
import ast
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "component", "infra", False
NAME, OWNER = "manifest row", "Rule-14"
RULES_FILE = Path(__file__).resolve().parent / "manifest_rules.txt"
PARTITIONS = {"kernel", "library", "The World"}
FIELDS = ("component", "partition", "version", "purpose", "license", "replacement")
INVARIANTS = [("partitions-fixed", lambda: PARTITIONS == {"kernel", "library", "The World"}),   # crafts/syseng/rules/invariants.md
              ("six-fields", lambda: len(FIELDS) == 6 and len(set(FIELDS)) == 6)]
# shell words that name no program: builtins, keywords, syntax
SHELL_SKIP = {"cd", "set", "[", "[[", "]", "]]", "exit", "export", "return", "shift", "true", "false",
              "if", "then", "else", "elif", "fi", "for", "while", "do", "done", "in", "case", "esac",
              "{", "}", "!", ".", "source", "local", "trap", "wait", "read", "unset", "eval", "time", "-"}
_SUBPROCESS = re.compile(
    r"subprocess\.(?:run|call|check_call|check_output|Popen)\(\s*\[\s*"
    r"(?:\"([^\"]*)\"|'([^']*)'|([A-Za-z_][\w.]*))")
_USES = re.compile(r"^\s*-?\s*uses:\s*(\S+)")
_RUN = re.compile(r"^(\s*)-?\s*run:\s*(.*)$")

# ---- manifest
def parse_manifest(text: str) -> list[tuple[str, ...]]:
    """Rows of the first markdown table: 6-tuples (short rows padded with '')."""
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in ("component", "") or set(cells[0]) <= {"-"}:
            continue
        rows.append(tuple((cells + [""] * 6)[:6]))
    return rows

def parse_rules(text: str) -> dict[str, list[str]]:
    """`component: token token ...`; `#` comments and blank lines ignored. A lone `-` token
    marks a component that is declared but never invoked by the package (no warning)."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        comp, sep, toks = line.partition(":")
        if not sep:
            continue
        out.setdefault(dyadlib.plain(comp.strip()), []).extend(toks.split())
    return out

def load_rules(path: Path) -> dict[str, list[str]]:
    return parse_rules(Path(path).read_text())

# ---- scanning
def _word(w: str) -> str:
    w = w.strip("\"'")
    if w.startswith("${{"):
        return ""
    return w.rsplit("/", 1)[-1] if w.startswith(("/", "./")) else w

def shell_words(text: str) -> list[str]:
    """First command word of every simple command in shell text, including inside `$(...)`.
    Leading `exec`, env assignments, and SHELL_SKIP words are dropped; words that are
    quoted expansions (`"$(...)/path"`) name no program and are dropped."""
    out = []
    for line in text.splitlines():
        line = re.sub(r"\$\{\{.*?\}\}", "", line).strip()
        if not line or line.startswith("#"):
            continue
        for inner in re.findall(r"\$\(([^()]*)\)", line):
            out.extend(shell_words(inner))
        line = re.sub(r"\$\([^()]*\)", "$SUB", line)
        for seg in re.split(r"&&|\|\||;|\|", line):
            words = seg.split()
            while words and (words[0] in ("exec", "sudo", "env", "{", "}", "!") or re.fullmatch(r"[A-Za-z_]\w*=.*", words[0])):
                words = words[1:]
            if not words:
                continue
            w = _word(words[0])
            if w and not w.startswith(("$", "-")) and w not in SHELL_SKIP and not w.endswith(".py"):
                out.append(w)
    return out

def shebang(text: str) -> str | None:
    first = text.splitlines()[0] if text else ""
    if not first.startswith("#!"):
        return None
    parts = first[2:].split()
    if not parts:
        return None
    if parts[0].endswith("/env") and len(parts) > 1:
        return parts[1]
    return parts[0].rsplit("/", 1)[-1]

def python_calls(text: str) -> list[str]:
    """argv[0] of every subprocess call with a list literal. `sys.executable` is python3;
    another identifier cannot be resolved statically and is reported as itself."""
    out = []
    for m in _SUBPROCESS.finditer(text):
        lit, lit2, ident = m.groups()
        if ident == "sys.executable":
            out.append("python3")
        elif ident:
            out.append(f"<{ident}>")
        else:
            out.append(_word(lit if lit is not None else lit2))
    return out

def workflow_words(text: str) -> list[str]:
    """`uses:` values and command words of every `run:` (single line or `|` block)."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if m := _USES.match(line):
            out.append(m.group(1)); i += 1; continue
        if m := _RUN.match(line):
            indent, rest = len(m.group(1)), m.group(2).strip()
            if rest in ("|", ">", "|-", ">-"):
                block, i = [], i + 1
                while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                    block.append(lines[i]); i += 1
                out.extend(shell_words("\n".join(block)))
            else:
                if len(rest) > 1 and rest[0] == rest[-1] and rest[0] in "'\"":
                    rest = rest[1:-1]
                out.extend(shell_words(rest)); i += 1
            continue
        i += 1
    return out

def craft_python_dirs(pkg: Path = dyadlib.PKG) -> list[Path]:
    """Every installed craft's own guards/, tests/, scripts/, projectors/ and server/ that exist —
    a craft's Python files carry their own imports, discovered the same way the core's are
    (Rule-11 property 2's craft-shipped contribution, `agent-corpus/falsification/extensibility.md`
    #101). `server/` is a craft-file location this repo's own `crafts/syseng/rules/invariants.md`
    already anticipates (`exempt: crafts/*/server/*.py`); omitting it here left a sibling test
    import of a craft's own server module invisible to `python_imports`'s `internal` set (#105)."""
    dirs = []
    for c in dyadlib.craft_dirs(pkg):
        dirs += [d for d in (c / "guards", c / "tests", c / "scripts", c / "projectors", c / "server") if d.is_dir()]
    return dirs

def python_dirs(pkg: Path = dyadlib.PKG) -> list[Path]:
    """scripts/, every guards/<corpus>/, tests/ and every tests/guards/<corpus>/ that exists (core),
    plus every installed craft's own (craft_python_dirs)."""
    dirs = [pkg / "scripts"] + sorted(d for d in (pkg / "guards").glob("*") if d.is_dir()) + [pkg / "tests"]
    dirs += sorted(d for d in (pkg / "tests" / "guards").glob("*") if d.is_dir()) + [pkg / "tests" / "guards"]
    dirs += craft_python_dirs(pkg)
    return [d for d in dirs if d.is_dir()]

def python_imports(pkg: Path = dyadlib.PKG) -> dict[str, list[str]]:
    """{`import:<name>`: [file, ...]} for every third-party Python import under scripts/, guards/
    and tests/. Walks the whole AST (imports inside functions and `try:` fallbacks count). The
    top-level module name is taken (`a.b.c` -> `a`; `import x as y` -> `x`). Stdlib names
    (`sys.stdlib_module_names`, the running kernel's set) ship with the kernel row Python;
    internal names (`<name>.py` in any of those directories, a test package directory, and any
    relative `ImportFrom`) are The Dyad System, not The World (Rule-14 Boundaries). Neither needs
    a manifest row; the rest do."""
    dirs = python_dirs(pkg)
    internal = {p.stem for d in dirs for p in d.glob("*.py")} | {d.name for d in dirs}
    found: dict[str, list[str]] = {}
    for d in dirs:
        for p in sorted(d.glob("*.py")):
            rel = str(p.relative_to(pkg) if p.is_relative_to(pkg) else p.relative_to(pkg.parent))
            tree = ast.parse(p.read_text(errors="ignore"), filename=rel)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0 or node.module is None:
                        continue
                    names = [node.module]
                else:
                    continue
                for n in names:
                    top = n.split(".", 1)[0]
                    if top in sys.stdlib_module_names or top in internal:
                        continue
                    found.setdefault(f"import:{top}", []).append(rel)
    return found

def scan(pkg: Path = dyadlib.PKG, workflows_dir: Path | None = None) -> dict[str, list[str]]:
    """{token: [where, ...]} over scripts/, hooks/, *.sh and the dyad-* workflows, plus every
    installed craft's own guards/, scripts/ and *.sh (Rule-11 property 2's craft-shipped
    contribution: a craft's own invocation tokens are discovered the same way the core's are)."""
    workflows_dir = workflows_dir if workflows_dir is not None else dyadlib.repo_root(pkg) / ".github" / "workflows"
    found: dict[str, list[str]] = {}
    def add(tok, where):
        if tok:
            found.setdefault(tok, []).append(where)
    files = sorted((pkg / "scripts").glob("*")) + sorted((pkg / "guards").glob("*/*")) + sorted((pkg / "hooks").glob("*")) + sorted(pkg.rglob("*.sh"))
    for c in dyadlib.craft_dirs(pkg):
        files += sorted((c / "guards").glob("*")) if (c / "guards").is_dir() else []
        files += sorted((c / "scripts").glob("*")) if (c / "scripts").is_dir() else []
        files += sorted((c / "projectors").glob("*")) if (c / "projectors").is_dir() else []
        # templates/ is seed material for an instance file (Rule-11 property 2), never invoked by
        # the craft itself, so it is excluded from this "what the package/craft invokes" scan.
        files += [p for p in sorted(c.rglob("*.sh")) if not p.is_relative_to(c / "templates")]
    for p in files:
        if not p.is_file() or p.name.endswith((".txt", ".pyc")):
            continue
        rel = str(p.relative_to(pkg) if p.is_relative_to(pkg) else p.relative_to(pkg.parent)); text = p.read_text(errors="ignore")
        sb = shebang(text)
        add(sb, f"{rel}:1")
        if p.suffix == ".py":
            for t in python_calls(text):
                add(t, rel)
        elif p.suffix == ".sh" or sb:
            for t in shell_words(text):
                add(t, rel)
        # else: not a recognized script (a craft's own README, data file, ...) -- shell_words is
        # never run over prose; only a `.sh` file or one with a real shebang is shell text (#105)
    if workflows_dir.is_dir():
        for p in sorted(workflows_dir.glob("dyad-*.yml")):
            for t in workflow_words(p.read_text()):
                add(t, p.name)
    for t, where in python_imports(pkg).items():
        for w in where:
            add(t, w)
    return found

# ---- check
def check(rows: list[tuple[str, ...]], rules: dict[str, list[str]], tokens: dict[str, list[str]] | set[str]) -> list[str]:
    """Failures (bare) and warnings (`warning:` prefix), in the package.py convention."""
    msgs, comps = [], []
    if not isinstance(tokens, dict):
        tokens = {t: [] for t in tokens}
    for r in rows:
        comp = dyadlib.plain(r[0])
        if not all(r) or len(r) < 6:
            msgs.append(f"'{r[0]}': malformed row (needs {', '.join(FIELDS)})"); continue
        if r[1] not in PARTITIONS:
            msgs.append(f"'{r[0]}': partition '{r[1]}' not in {sorted(PARTITIONS)}")
        if comp in comps:
            msgs.append(f"'{r[0]}': declared twice")
        comps.append(comp)
    tok2comp = {}
    for comp, toks in rules.items():
        if comp not in comps:
            msgs.append(f"rules map '{comp}' which the manifest does not declare")
        for t in toks:
            tok2comp.setdefault(t, comp)
    for t, where in sorted(tokens.items()):
        if t in tok2comp:
            continue
        if t.startswith("import:"):
            msgs.append(f"'{t}' imported by {', '.join(sorted(set(where))) or 'the package'} is an undeclared Python import")
        else:
            msgs.append(f"'{t}' invoked by {', '.join(sorted(set(where))) or 'the package'} maps to no declared component")
    for comp in comps:
        if not rules.get(comp):
            msgs.append(f"warning: '{comp}' declared but no token maps to it (add tokens or `-` in manifest_rules.txt)")
    return msgs

def craft_manifest_rules(pkg: Path = dyadlib.PKG) -> list[tuple[str, dict[str, list[str]]]]:
    """[(craft, rules)] from every installed craft's own `manifest_rules_contrib.txt` (same
    `component: token token ...` grammar `parse_rules` already reads): a craft's own invocation
    tokens resolve against its own contributed rules too, not only the core's `manifest_rules.txt`
    (Rule-11 property 2, `agent-corpus/falsification/extensibility.md` #101, #105 — the token-map
    half of the contribution `infrastructure_contrib.md` gave only manifest *rows*, not this).
    Empty when a craft ships none."""
    out = []
    for c in dyadlib.craft_dirs(pkg):
        f = c / "manifest_rules_contrib.txt"
        if f.is_file():
            out.append((c.name, parse_rules(f.read_text())))
    return out

def craft_infra_rows(pkg: Path = dyadlib.PKG) -> list[tuple[str, tuple[str, ...]]]:
    """[(craft, row)] from every installed craft's own `infrastructure_contrib.md` (same six cells
    as INFRASTRUCTURE.md, parsed by the same `parse_manifest`): a core-owned table accepting a
    craft-shipped contribution, discovered like a guard (Rule-11 property 2,
    `agent-corpus/falsification/extensibility.md` #101). Empty when a craft ships none."""
    out = []
    for c in dyadlib.craft_dirs(pkg):
        f = c / "infrastructure_contrib.md"
        if f.is_file():
            out += [(c.name, row) for row in parse_manifest(f.read_text())]
    return out

def check_manifest(pkg: Path = dyadlib.PKG) -> tuple[int, int, list[str]]:
    """(components, tokens, messages) over the live package plus every installed craft's own
    contributed rows and rules. A contributed component already declared (by the core manifest or
    an earlier craft) fails, naming both sources — a component leaves with its craft, so it is
    never shared. A craft's own `manifest_rules_contrib.txt` rows merge into the token map the same
    way its `infrastructure_contrib.md` rows merge into the manifest (#105): a token the core map
    already resolves is unaffected (`dict.setdefault`, first-wins, matching `check`'s own `tok2comp`
    merge order); an unresolved token is only ever the caller's, never blamed on a craft that has
    not contributed a mapping for it."""
    core_rows = parse_manifest((pkg / "infrastructure" / "INFRASTRUCTURE.md").read_text())
    rules = dict(load_rules(pkg / "guards" / "infra" / "manifest_rules.txt"))
    for craft, craft_rules in craft_manifest_rules(pkg):
        for comp, toks in craft_rules.items():
            rules.setdefault(comp, []).extend(toks)
    tokens = scan(pkg)
    all_rows, msgs, seen = list(core_rows), [], {dyadlib.plain(r[0]): "the manifest" for r in core_rows}
    for craft, row in craft_infra_rows(pkg):
        comp = dyadlib.plain(row[0])
        if comp in seen:
            msgs.append(f"'{row[0]}' (crafts/{craft}/infrastructure_contrib.md): already declared by {seen[comp]}")
            continue
        seen[comp] = f"crafts/{craft}/infrastructure_contrib.md"
        all_rows.append(row)
    msgs += check(all_rows, rules, tokens)
    return len(all_rows), len(tokens), msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return check_manifest(pkg)[2]

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    n, m, _ = check_manifest(pkg)
    return f"{n} components, {m} tokens"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    manifest = pkg / "infrastructure" / "INFRASTRUCTURE.md"
    comps = parse_manifest(manifest.read_text()) if manifest.exists() else []
    ex = comps[0] if comps else None
    rel = manifest.relative_to(root) if manifest.is_relative_to(root) else manifest
    return {"store": str(rel), "parser": "`manifest.parse_manifest`", "observed": len(comps),
            "note": "every invocation token maps to a row through `manifest_rules.txt`",
            "fields": [(c, "enum" if c == "partition" else "text", " | ".join(sorted(PARTITIONS)) if c == "partition" else "", True, ex[i] if ex else "", "manifest.FIELDS") for i, c in enumerate(FIELDS)]}

def main():
    n, m, msgs = check_manifest()
    fails = [x for x in msgs if not x.startswith("warning:")]
    for x in msgs:
        print(("warn [rule-14] " if x.startswith("warning:") else "FAIL [rule-14] ") + x.removeprefix("warning: "), file=sys.stderr)
    if not fails:
        print(f"ok   [rule-14] {n} components, {m} tokens resolve")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
