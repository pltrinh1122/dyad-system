#!/usr/bin/env python3
"""Plan-file guard (entity `plan`, agent corpus; Rule-15 owns the plan file, placed per Rule-11 property 1). Kernel: Python 3.12+.
Every `<instance>/d-work/plans/<id>.md` starts with a title line `# Plan #<id>` whose id equals the
file name (a title after ` — ` is free text), carries a base-commit line (`base commit:` in any
case, Rule-15 phase 1). Existence of these parts, nothing more: what a plan says stays inference
(plan #151, mutation 6). A plan naming no intent (no line mentioning `intent`), or never mentioning
a part of dyadlib.PLAN_PARTS, is reported as a warning: plans ratified before Rule-15 keep their
form (plan #138 states a claim instead of an intent). `definition of done` (#574) is asked only of a plan whose row
opened on or after dyadlib.DOD_SINCE, so the plans written before it keep their five parts. The id → row and base commit → commit references are resolved by
`references.py` (Rule-20).

The plan check (#592 R-c): `dyad plan check <id>` (`cli`, dispatched by `package.py` as the noun `plan`) reads one
plan beside its row and the tree and prints warnings, never a refusal: the files touched span a second zone (Rule-1,
`containment.classify`); a touched module whose mapped test (`syseng/tests`, `tests.test_for`) is not listed; a touched
craft whose `VERSION` is already its release tag, so the merge drifts (`bundle.check_drift`, mode 18); the callers of
each `module.function` the Mutation names (mode 37); a `refs` dependency not `done`; `order: required` with no `step:`
line (mode 17). `dwork state <id> planned` runs it before its first write. `mandate_ceiling` reads the ceiling a plan's
mandate scope states, which `dwork new --mandate` refuses past (`ceiling_check`); the seat's charter ceiling
(`MANDATES.md`) only warns (the home's answer to #592 F11).
  plans.py [repo-root]
  plans.py check <id>          (as `dyad plan check <id>`)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("plans.py: Python 3.12+ required")
import re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "plan", "agent", False
NAME, OWNER = "plan file", "Rule-15"
FIELDS = ("id", "title", "base commit", "intent")     # the header parse() yields; the prose parts are dyadlib.PLAN_PARTS
_TITLE = re.compile(r"^# Plan #(\d+)(?:\s*[—–-]+\s*(.*))?$")
_BASE = re.compile(r"(?i)base commit[^:\n]*:\s*(\S+)")
_INTENT = re.compile(r"(?i)\bintent\b")
VERBS = ("check",)                                  # `dyad plan <verb>` (#592 R-c)
CLI_FLAGS = dyadlib.cli_forms("plan", VERBS)   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
REFS_NOT_DEPENDENCY = ("parent", "PR", "PRs", "children", "child", "modes", "mode")   # a refs id after one of these is not a dependency of the plan
REFS_ONE = ("parent",)                              # of those, the ones naming one id; the rest name every id up to the next word
DEPENDENCY_DONE = ("done", "archived")              # a dependency in one of these states is met
CALLERS_SHOWN = 8                                   # caller files named per function before `+n more`
USAGE = "usage: dyad plan check <id>   (warnings on one plan, beside its row and the tree; #592 R-c)"
INVARIANTS = [("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS)),   # crafts/syseng/rules/invariants.md
              ("fields-in-order", lambda: FIELDS == ("id", "title", "base commit", "intent")),   # the parse contract parse() yields (#203)
              ("verbs-distinct", lambda: len(set(VERBS)) == len(VERBS) and "check" in VERBS),   # #592 R-c
              ("dependency-done-holds-done", lambda: "done" in DEPENDENCY_DONE and len(set(DEPENDENCY_DONE)) == len(DEPENDENCY_DONE)),
              ("refs-skip-holds-parent", lambda: "parent" in REFS_NOT_DEPENDENCY and len(set(REFS_NOT_DEPENDENCY)) == len(REFS_NOT_DEPENDENCY)),
              ("refs-one-is-a-skip", lambda: set(REFS_ONE) <= set(REFS_NOT_DEPENDENCY)),   # #592 R-c
              ("callers-shown-positive", lambda: CALLERS_SHOWN > 0)]
_FILES = re.compile(r"(?i)^\s*(?:#+\s*)?[-*\s]*\**files touched\**\s*:?\**")
_PATH = re.compile(r"(?<![\w/.-])((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.*<>-]+)")
_ORDER = re.compile(r"(?im)^[\s>*-]*order:\s*required\b")   # the declaration, on a line of its own; a backticked mention is prose
_STEP = re.compile(r"(?im)^[\s>*-]*step\b[^:\n]{0,12}:")
_MODFUNC = re.compile(r"`(?:[\w./-]*/)?([A-Za-z_]\w*)\.py`\s+`([A-Za-z_]\w*)`|`(?:[\w./-]*/)?([A-Za-z_]\w*)\.([A-Za-z_]\w*)(?:\(\))?`")
_CEILING = re.compile(r"(?i)\bceiling\W{0,6}(?:of\s+)?(\d+)")
_MANDATE_LINE = re.compile(r"(?i)mandate\W{0,4}(?:scope|ceiling)")
_CEILING_MOVES = re.compile(r"(?i)\bceiling\s+(?:rises|is\s+raised|drops|falls|moves|is\s+lowered)\s+to\s+(\d+)")   # a revision's statement

def plans_dir(root: Path) -> Path:
    return dyadlib.instance(root) / "d-work" / "plans"

def plans(root: Path) -> list[Path]:
    d = plans_dir(root)
    return sorted((p for p in d.glob("*.md") if p.stem.isdigit()), key=lambda p: int(p.stem)) if d.is_dir() else []

def parse(text: str) -> dict[str, str]:
    """{id, title, base commit, intent}: id and title from the first line, the base-commit value, and
    the first line naming an intent ("" when absent)."""
    first = text.splitlines()[0] if text else ""
    m = _TITLE.match(first)
    b = _BASE.search(text)
    intent = next((l.strip() for l in text.splitlines() if _INTENT.search(l)), "")
    return {"id": m.group(1) if m else "", "title": (m.group(2) or "").strip() if m else "", "base commit": b.group(1) if b else "", "intent": intent}

def parts_for(opened: str | None) -> tuple[str, ...]:
    """The PLAN_PARTS a plan is asked for: all six when its row opened on or after DOD_SINCE, else the first five
    (#574: the part is new, and a stored plan is never asked to grow one)."""
    return dyadlib.PLAN_PARTS if opened and opened >= dyadlib.DOD_SINCE else dyadlib.PLAN_PARTS[:-1]

def replan(accreted: bool, moved: list[str]) -> str:
    """dmc:replan (#641): whether execution re-plans. `accreted` (accreted row) for a row accreted under a mandate,
    which has no drift check of its own; `replan` (re-plans) when `main` has moved past a file the plan touches
    (`moved`, from `moved_files`); `as-written` (executes as written) otherwise."""
    if accreted:
        return "accreted"
    return "replan" if moved else "as-written"

def moved_files(root: Path, base: str, files: list[str], main: str = "origin/main") -> list[str]:
    """The files of `files` some commit in `base..main` touches (`git log --name-only`), in `files`' order; [] when the
    base or main does not resolve (no drift can be read, so none is claimed)."""
    r = subprocess.run(["git", "log", "--format=", "--name-only", f"{base}..{main}", "--", *files], cwd=root,
                       capture_output=True, text=True, env=dyadlib.git_env())
    touched = set(r.stdout.split()) if r.returncode == 0 else set()
    return [f for f in files if f in touched]

def check_plan(path: Path, text: str | None = None, opened: str | None = None) -> list[str]:
    text = path.read_text() if text is None else text
    d = parse(text); msgs = []
    if not d["id"]:
        msgs.append(f"{path.name}: first line is not `# Plan #<id>`")
    elif d["id"] != path.stem:
        msgs.append(f"{path.name}: title id #{d['id']} differs from the file name")
    if not d["base commit"]:
        msgs.append(f"{path.name}: no base commit line (Rule-15 phase 1)")
    if not d["intent"]:
        msgs.append(f"warning: {path.name}: names no intent (Rule-15 phase 1)")
    low = text.lower()
    for part in parts_for(opened):
        if part not in low:
            msgs.append(f"warning: {path.name}: never mentions `{part}` (dyadlib.PLAN_PARTS)")
    return msgs

# ---- the plan check (#592 R-c): warnings only; what the plan says stays inference, these are its cheap tells
def files_touched(text: str) -> list[str]:
    """The repo paths a plan's `Files touched` part names: the rest of its line and the lines after it, up to a blank
    line or a heading; a path is a token holding a `/`. Order kept, duplicates dropped."""
    lines, out, on = text.splitlines(), [], False
    for line in lines:
        if not on:
            m = _FILES.match(line)
            if m:
                on, line = True, line[m.end():]
            else:
                continue
        elif not line.strip() or line.lstrip().startswith("#"):
            break
        for t in _PATH.findall(line.replace("`", " ")):
            t = t.rstrip(".")
            if t not in out:
                out.append(t)
    return out

def section(text: str, name: str) -> str:
    """The body of the `## <name>…` heading, up to the next `## ` heading; "" when the plan has none."""
    out, on = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if on:
                break
            on = line[3:].strip().lower().startswith(name)
            continue
        if on:
            out.append(line)
    return "\n".join(out)

def stated_ceiling(text: str) -> int | None:
    """The ceiling the plan's mandate scope states: the number after `ceiling` on a line naming a `mandate scope` or a
    `mandate ceiling`, or the number a revision moves it to (`the ceiling rises to 14`, plan #570 revision 2); the last
    such statement in the file wins (a revision appends; the live statement is the last); None when none states one."""
    found = None
    for line in text.splitlines():
        hits = []
        m = _MANDATE_LINE.search(line)
        if m and (c := _CEILING.search(line, m.start())):
            hits.append((c.start(), int(c.group(1))))
        hits += [(r.start(), int(r.group(1))) for r in _CEILING_MOVES.finditer(line)]
        if hits:
            found = max(hits)[1]
    return found

def mandate_ceiling(mid: int | str, root: Path | None = None) -> int | None:
    """The ceiling plan `<mid>` states for its mandate (Rule-3 Plan: the Operator's number); None without a plan file
    or a stated ceiling."""
    p = plans_dir(root or dyadlib.repo_root()) / f"{int(mid)}.md"
    return stated_ceiling(p.read_text(encoding="utf-8")) if p.is_file() else None

def children(rows, mid: int) -> list[int]:
    """The rows whose refs name `parent #<mid>`: the rows accreted (or carried) under that mandate."""
    pat = re.compile(rf"\bparent #{int(mid)}\b")
    return sorted(r.id for r in (rows.values() if isinstance(rows, dict) else rows) if pat.search(r.refs or ""))

def record_seat(mid: int, root: Path) -> str | None:
    """The seat a mandate was given in: its provenance record's `session:` line (Rule-16 Presence), else None."""
    p = dyadlib.instance(root) / "d-work" / "provenance" / f"{int(mid)}.md"
    m = re.search(r"(?m)^session:\s*(\S+)", p.read_text(encoding="utf-8")) if p.is_file() else None
    return m.group(1) if m else None

def charter_ceiling(seat: str | None, root: Path) -> int | None:
    """The `ceiling` cell of the seat's charter row in `preferences-corpus/MANDATES.md` (the cabinet's mandates table),
    matched by seat name first, then by function — a `<function>-<hp>` row, or a row whose function column is the
    seat's function, so a seat re-held under a new `<hp>` (or with a topic) still finds its charter; its leading
    number, else None."""
    p = root / "preferences-corpus" / "MANDATES.md"
    if not seat or not p.is_file():
        return None
    func = seat.split("-", 1)[0]                     # `<function>[-<topic>]-<hp>` (Rule-16 Presence)
    rows = [r for r in dyadlib.table_rows(p.read_text(encoding="utf-8")) if len(r) >= 5]
    exact = [r for r in rows if dyadlib.plain(r[0]).strip() == seat]
    by_func = [r for r in rows if (lambda name: name.endswith("-<hp>") and name[:-5] == func)(dyadlib.plain(r[0]).strip())
               or dyadlib.plain(r[1]).strip() == func]
    for r in exact + by_func:
        m = re.match(r"\s*(\d+)", dyadlib.plain(r[4]))
        return int(m.group(1)) if m else None
    return None

def ceiling_check(rows, mid: int, root: Path | None = None) -> tuple[str | None, list[str]]:
    """(refusal, warnings) for one more row under mandate `<mid>` (`dwork new --mandate`): refused when the mandate
    already has as many children as its plan's stated ceiling; a warning past the seat's charter ceiling, which never
    refuses (the home's answer to #592 F11); a warning when the plan exists and states none."""
    root = root or dyadlib.repo_root()
    n, warns = len(children(rows, mid)), []
    ceiling = mandate_ceiling(mid, root)
    if ceiling is None and (plans_dir(root) / f"{int(mid)}.md").is_file():
        warns.append(f"warning: plan #{mid} states no mandate ceiling (Rule-3 Plan: a plan stating none accretes nothing)")
    seat = record_seat(mid, root)
    charter = charter_ceiling(seat, root)
    if charter is not None and n + 1 > charter:
        warns.append(f"warning: #{mid} would hold {n + 1} children, past seat {seat}'s charter ceiling {charter} (MANDATES.md); "
                     f"the plan's stated ceiling governs (#592 F11)")
    if ceiling is not None and n >= ceiling:
        return (f"refused: mandate #{mid} already has {n} children, its plan's stated ceiling {ceiling}; a row past it "
                f"departs from the plan and needs a new plan-Y (Rule-3 Plan, mandate scope)"), warns
    return None, warns

def _pkg(root: Path) -> Path:
    return root / "dyad" if (root / "dyad" / "VERSION").is_file() else dyadlib.PKG

def zone_warnings(name: str, paths: list[str], root: Path) -> list[str]:
    ct = dyadlib.find_guard("infra", "containment")
    if ct is None:
        return []
    zones = sorted({z for z in (ct.classify(p, root) for p in paths) if z != "unclassified"})
    return [f"warning: {name}: files touched span zones {', '.join(zones)} (Rule-1: one zone per PR; split the PRs by zone)"] if len(zones) > 1 else []

def test_warnings(name: str, paths: list[str], root: Path) -> list[str]:
    tg = dyadlib.find_guard("craft", "tests")
    if tg is None:
        return []
    pkg, out = _pkg(root), []
    for p in paths:
        py = root / p
        if not p.endswith(".py") or py.name.startswith(("test_", "_")):
            continue
        parts = Path(p).parts
        code = (parts[:1] == (pkg.name,) and len(parts) >= 3 and parts[1] in ("scripts", "guards")) or \
               (parts[:1] == ("crafts",) and len(parts) == 4 and parts[2] in ("guards", "scripts", "projectors"))
        if not code:
            continue
        t = tg.test_for(py, pkg)
        rel = t.relative_to(root).as_posix() if t.is_relative_to(root) else str(t)
        if rel not in paths:
            out.append(f"warning: {name}: touches {p} but not its test {rel} (crafts/syseng/rules/verifiable-code.md p4)")
    return out

def version_warnings(name: str, paths: list[str], root: Path) -> list[str]:
    """A craft the plan touches whose live `VERSION` is already a release tag: the merge drifts from that tag unless the
    plan also bumps `VERSION` (bundle.check_drift, mode 18)."""
    bd = dyadlib.find_guard("infra", "bundle")
    pkg = _pkg(root)
    if bd is None or not pkg.is_relative_to(root):
        return []
    out, live = [], bd.live_components(pkg)
    for comp, rel in bd.component_roots(root, pkg).items():
        r = rel.as_posix()
        if not any(p.startswith(f"{r}/") for p in paths) or f"{r}/VERSION" in paths:
            continue
        tag = bd.tag_name(comp, live[comp])
        if subprocess.run(["git", "rev-parse", "--verify", "-q", f"{tag}^{{commit}}"], cwd=root, capture_output=True).returncode == 0:
            out.append(f"warning: {name}: touches {r}/ while its VERSION {live[comp]} is release tag {tag}; bump {r}/VERSION "
                       f"or the merge drifts (bundle.check_drift, mode 18)")
    return out

def _modules(root: Path) -> dict[str, Path]:
    pkg = _pkg(root)
    found = sorted((pkg / "scripts").glob("*.py")) + sorted((pkg / "guards").glob("*/*.py"))
    for d in ("guards", "scripts", "projectors"):
        found += dyadlib.craft_glob(f"{d}/*.py", pkg)
    out: dict[str, Path] = {}
    for p in found:
        out.setdefault(p.stem, p)
    return out

def caller_warnings(name: str, text: str, root: Path) -> list[str]:
    """For each `module.function` (or `` `module.py` `function` ``) the Mutation names and the module defines, the other
    code files that call it (mode 37: a changed function's callers, read at plan time; no diff exists yet)."""
    mutation = section(text, "mutation")
    if not mutation:
        return []
    mods, named = _modules(root), []
    for m in _MODFUNC.finditer(mutation):
        mod, fn = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))   # `x.py` `f`, else `x.f`
        if mod in mods and (mod, fn) not in named and re.search(rf"(?m)^\s*def {re.escape(fn)}\b", mods[mod].read_text(encoding="utf-8")):
            named.append((mod, fn))
    if not named:
        return []
    pkg = _pkg(root)
    files = [p for base in (pkg, pkg.parent / "crafts") if base.is_dir() for p in sorted(base.rglob("*.py")) if "__pycache__" not in p.parts]
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in files}
    out = []
    for mod, fn in named:
        callers = [p for p, t in texts.items() if p != mods[mod] and calls(t, mod, fn)]
        if callers:
            rel = [p.relative_to(root).as_posix() if p.is_relative_to(root) else str(p) for p in callers]
            more = f" +{len(rel) - CALLERS_SHOWN} more" if len(rel) > CALLERS_SHOWN else ""
            out.append(f"warning: {name}: the Mutation names {mod}.{fn}, called from {len(rel)} other file(s): "
                       f"{', '.join(rel[:CALLERS_SHOWN])}{more} (mode 37)")
    return out

def calls(text: str, mod: str, fn: str) -> bool:
    """True when `text` calls `mod.fn`: through a name bound to the module — `import mod [as x]`, or `x = …"mod"…` (a
    `load_guard`, `find_guard` or `load_module` of it) — as `x.fn(`, or a bare `fn(` after `from mod import … fn`. A
    same-named function another module defines and calls is not a caller (mode 37)."""
    m, f = re.escape(mod), re.escape(fn)
    names = {mod} if re.search(rf"(?m)^\s*import\s+(?:[\w.]+\s*,\s*)*(?:[\w.]+\.)?{m}\b(?!\s+as\b)", text) else set()
    names |= set(re.findall(rf"(?m)^\s*import\s+(?:[\w.]+\.)?{m}\s+as\s+(\w+)", text))
    names |= set(re.findall(rf"(?m)^\s*from\s+[\w.]+\s+import\s+[^\n]*?\b{m}\b(?:\s+as\s+(\w+))?", text)) - {""}
    if re.search(rf"(?m)^\s*from\s+[\w.]+\s+import\s+[^\n]*\b{m}\b(?!\s+as\b)", text):
        names.add(mod)
    names |= set(re.findall(rf"(?m)^\s*(\w+)\s*=\s*[^\n]*[\"']{m}(?:\.py)?[\"']", text))
    if any(re.search(rf"(?<![\w.]){re.escape(n)}\.{f}\(", text) for n in names):
        return True
    if re.search(rf"(?m)^\s*from\s+(?:[\w.]+\.)?{m}\s+import\s+[^\n]*\b{f}\b", text):
        return any(not re.match(rf"\s*def\s+{f}\(", line) and re.search(rf"(?<![\w.]){f}\(", line) for line in text.splitlines())
    return False

def refs_warnings(name: str, row, rows: dict) -> list[str]:
    """A refs token that is a bare row id names a dependency; one not done warns. Not a dependency: the one id after
    `parent`, and every id after `PR`, `children`, `modes` (and the like, `REFS_NOT_DEPENDENCY`) up to the next word."""
    if row is None:
        return []
    out, toks, span = [], (row.refs or "").replace(",", " ").split(), None
    for t in toks:
        m = re.fullmatch(r"#?(\d+)", t)
        if not m:
            span = ("one" if t in REFS_ONE else "all") if t in REFS_NOT_DEPENDENCY else None   # "all": up to the next word
            continue
        if span:
            span = None if span == "one" else span
            continue
        dep = rows.get(int(m.group(1)))
        if dep is not None and dep.id != row.id and dep.state not in DEPENDENCY_DONE:
            out.append(f"warning: {name}: refs dependency #{dep.id} is {dep.state}, not done")
    return out

def order_warnings(name: str, text: str) -> list[str]:
    if _ORDER.search(text) and not _STEP.search(text):
        return [f"warning: {name}: says `order: required` but names no `step:` line (Rule-15 phase 1, mode 17)"]
    return []

INTENT_KEY = "intent-reading"                                   # #615: the preference; an absent key reads `off`
INTENT_Y = re.compile(r"\d{4}-\d{2}-\d{2} Y intent(?:$| \()")

def intent_warnings(name: str, row, root: Path) -> list[str]:
    """#615: under `intent-reading: on`, a row a prompt opened or reopened (its record holds a `prompt` entry; an
    accreted row's never does) that is open or planned with no `Y intent` in `disposed` — a warning for the plan's
    reader, never a refusal (F6: a refusal would break 1.x). `off`, or the key absent, warns on nothing."""
    if row is None or row.state not in ("open", "planned") or dyadlib.preference(INTENT_KEY, root) != "on":
        return []
    if any(INTENT_Y.match(e) for e in dyadlib.load_guard("agent", "rows").entries(row.disposed)):
        return []
    pv = dyadlib.load_guard("agent", "provenance")
    rec = pv.store(root) / f"{row.id}.md"
    if not rec.is_file() or not any(e["kind"] == "prompt" for e in pv.parse(rec.read_text(encoding="utf-8"))):
        return []
    return [f"warning: {name}: row #{row.id} was opened by a prompt and holds no `Y intent`; under intent-reading: on "
            f"the intent question comes before the plan (Rule-3 Plan, #615)"]

def check_dwork(rid: int | str, root: Path | None = None) -> list[str]:
    """Every message of `dyad plan check <rid>`: the plan file's own check (`check_plan`) and the warnings above. A
    missing plan file is the one non-warning message."""
    root = root or dyadlib.repo_root()
    path = plans_dir(root) / f"{int(rid)}.md"
    if not path.is_file():
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        return [f"no plan file {rel} (Rule-15 phase 1)"]
    try:
        rows = {r.id: r for r in dyadlib.read_rows(root)}
    except (OSError, ValueError, KeyError):
        rows = {}
    row = rows.get(int(rid))
    text = path.read_text(encoding="utf-8")
    paths, name = files_touched(text), path.name
    return (check_plan(path, text, opened=row.opened if row else None) + zone_warnings(name, paths, root)
            + test_warnings(name, paths, root) + version_warnings(name, paths, root) + caller_warnings(name, text, root)
            + refs_warnings(name, row, rows) + order_warnings(name, text) + intent_warnings(name, row, root))

def print_messages(msgs: list[str], label: str = "plan") -> int:
    """Print as the runner does — `warn [<label>]` on stdout, `FAIL [<label>]` on stderr; the count of failures."""
    fails = [m for m in msgs if not m.startswith("warning: ")]
    for m in msgs:
        if m.startswith("warning: "): print(f"warn [{label}] {m[9:]}")
        else: print(f"FAIL [{label}] {m}", file=sys.stderr)
    return len(fails)

def cli(a: list[str], root: Path | None = None) -> int:
    """`dyad plan check <id>` (#592 R-c): exit 0 with its warnings, 1 on a failure or a refused form."""
    if not a or a[0] in ("-h", "--help") or (a[0] in VERBS and any(x in ("-h", "--help") for x in a[1:])):
        print(USAGE); return 0
    if a[0] not in VERBS:
        print(f"refused: dyad plan has no verb {a[0]!r}; {USAGE}", file=sys.stderr); return 1
    extra = [x for x in a[1:] if x.startswith("-")]
    if extra:
        print(f"refused: dyad plan check does not take {' '.join(extra)}", file=sys.stderr); return 1
    if len(a) != 2 or not a[1].isdigit():
        print(f"refused: {USAGE}", file=sys.stderr); return 1
    root = root or dyadlib.repo_root()
    msgs = check_dwork(a[1], root)
    if print_messages(msgs):
        return 1
    print(f"ok   [plan] #{a[1]}: {len(msgs)} warning(s)")
    return 0

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    msgs, ps = [], plans(root)
    try:
        opened = {str(r.id): r.opened for r in dyadlib.read_rows(root)} if ps else {}
    except (OSError, ValueError, KeyError):
        opened = {}
    for p in ps:
        msgs += check_plan(p, opened=opened.get(p.stem))
    return msgs

def summary(root: Path | None = None) -> str:
    return f"{len(plans(root or dyadlib.repo_root()))} plans"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ps = plans(root)
    texts = {p: p.read_text() for p in ps}
    ex = parse(texts[ps[-1]]) if ps else {}
    d = plans_dir(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    allowed = {"id": "the row it plans (file name)", "title": "free text after ` — `", "base commit": "a commit of `main` (Rule-15)", "intent": "a line naming the intent as read"}
    fields = [(f, "int" if f == "id" else "line", allowed[f], f != "title", ex.get(f, ""), "plans.FIELDS") for f in FIELDS]
    for part in (x for x in dyadlib.PLAN_PARTS if x not in FIELDS):
        n = sum(1 for t in texts.values() if part in t.lower())
        ex_line = next((l.strip() for l in texts[ps[-1]].splitlines() if part in l.lower()), "") if ps else ""
        fields.append((part, "line", f"present in {n}/{len(ps)} plans (observed)" if ps else "", False, ex_line, "dyadlib.PLAN_PARTS"))
    return {"store": f"{rel}/<id>.md", "parser": "`plans.parse` (header); parts named by `dyadlib.PLAN_PARTS`", "observed": len(ps),
            "note": "free-form prose after the header; a plan-Y binds to the file; the id is the row it plans", "fields": fields}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    if a and a[0] in VERBS:
        return cli(a)
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning: ")]
    for m in msgs:
        if m.startswith("warning: "): print(f"warn [rule-15] {m[9:]}")
        else: print(f"FAIL [rule-15] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [rule-15] {len(plans(root))} plans")
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main())
