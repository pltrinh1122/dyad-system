#!/usr/bin/env python3
"""The audit's coded checks (core script; d-work #619; the play-books `dyad/playbooks/audit.md` and
`dyad/playbooks/incident-hardening.md` own what they mean). Kernel: Python 3.12+, git.
Each check reads one tree — a worktree at one commit of `main` — and prints lines of two kinds:
  `reading: …`  a number or a state nobody compares: the watermark, the registry's count, the incident sizing,
                the hardening watermark, stale presence files and unmerged branches. Never posted, never a finding.
  `finding: …`  a warning the sweep tells the home once: a guard that left the registry, Rules edited after the newest
                Rule-5 sweep record, rows past the hardening watermark, a fence row or fence the newest index names
                that does not resolve, an audit record missing a line, the levels file. No finding carries a count
                that grows, so one told is not new again until what it names changes.
The automaton sweep's part `sweep_audit` runs them all after each landed merge (`dyadlib.CHECK_INPUTS`: the code tree).
Read-only: it writes nothing. The two run-book entries:
  audits.py hardening [<ledger>]   the hardening survey (play-book phase 0): readings, findings, `verdict: <outcome>`
  audits.py record [<record>]      the newest audit record's two lines (or <record>'s); exit 1 when one is missing
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("audits.py: Python 3.12+ required")
import ast, hashlib, platform, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dyadlib

USAGE = "usage: audits.py hardening [<ledger>] | record [<record>]"
AUDITED = re.compile(r"^\*\*Audited:\*\*\s*(.*)$", re.M)           # the watermark line of an audit record (P1)
FENCES = re.compile(r"^\*\*Fences:\*\*\s*(.*)$", re.M)              # its registry line (P2)
DATED = re.compile(r"^20\d\d-\d\d-\d\d-.*\.md$")                    # a dated record of <instance>/audits/, pruned from P1
AUDIT_RECORD = re.compile(r"^.+-audit\.md$")                        # a standing audit's record (the play-book's name)
RULE_SWEEP = re.compile(r"^\d{4}-\d\d-\d\d-rule-sweep\.md$")         # a Rule-5 sweep record (P5)
INDEX = re.compile(r"^\d{4}-\d\d-\d\d-incident-failure-modes\.md$")  # a hardening index audit (P11, P16, P17)
WATERMARK = re.compile(r"\*\*covered through:\*\*\s*(\d+) rows, latest (\d{4}-\d\d-\d\d)")
REGISTRY = re.compile(r"registry (\d+) lines, sha256 ([0-9a-f]{16})")
LOG_ROW = re.compile(r"^\| (20[0-9-]*)", re.M)                      # a dated row of the incident log, as `survey` counted
FENCE_ROW = re.compile(r"#(\d+)")
TOKEN = re.compile(r"`([^`]+)`")
LABEL = re.compile(r"[a-z0-9_-]+/[a-z0-9_]+")
CORE_TAG = "dyad-operator-v*"
NONE_CELLS = ("", "—", "-", "–")
BRANCHES_SHOWN = 20            # unmerged branches named in the reading; the rest counted
OUTCOMES = ("first exercise", "no-op", "delta")                     # dyad/dmc/hardening-survey.jsonld's names
PATTERNS = (AUDITED, FENCES, DATED, AUDIT_RECORD, RULE_SWEEP, INDEX, WATERMARK, REGISTRY, LOG_ROW, FENCE_ROW, TOKEN, LABEL)
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("seam-patterns-distinct", lambda: len({p.pattern for p in PATTERNS}) == len(PATTERNS)),
    ("records-are-dated-records", lambda: all(DATED.match(n) for n in ("2026-11-06-audit.md", "2026-11-06-rule-sweep.md",
                                                                          "2026-11-06-incident-failure-modes.md"))),
    ("watermark-reads-the-index-line", lambda: WATERMARK.search("**covered through:** 252 rows, latest 2026-11-03") is not None),
    ("registry-reads-the-fences-line", lambda: REGISTRY.search("registry 24 lines, sha256 7a01f16b0d0692ae") is not None),
    ("outcomes-distinct", lambda: len(set(OUTCOMES)) == 3),
]


def _git(root: Path, *a: str) -> str | None:
    try:
        r = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def audits_dir(root: Path) -> Path:
    return dyadlib.instance(root) / "audits"


def newest(root: Path, pattern: re.Pattern) -> Path | None:
    d = audits_dir(root)
    names = sorted(p.name for p in d.iterdir() if p.is_file() and pattern.match(p.name)) if d.is_dir() else []
    return d / names[-1] if names else None


# ---- P1, the watermark (dyad/dmc/audit-watermark.jsonld)
def live_watermark(root: Path) -> str | None:
    """`tree <h> · python <v> · git <v>`: the code tree (`package.code_digest`, ledger and events pruned) with the
    dated audit records also pruned, and the interpreter and git that read it; None when git cannot say."""
    pkg = dyadlib.load_module(HERE / "package.py", "package")
    rel = dyadlib.instance_rel(root)
    prefix = f"{rel}/audits/" if rel else None
    tree = pkg.code_digest("HEAD", prune=lambda p: bool(prefix and p.startswith(prefix)
                                                        and DATED.match(p[len(prefix):])), repo=root)
    gv = _git(root, "--version")
    if not tree or not gv:
        return None
    return f"tree {tree} · python {platform.python_version()} · git {gv.removeprefix('git version ')}"


def watermark(root: Path) -> list[str]:
    live = live_watermark(root)
    if live is None:
        return ["reading: audit watermark: not read (git cannot say)"]
    rec, last = None, None
    d = audits_dir(root)
    for p in sorted(d.glob("*-audit.md")) if d.is_dir() else []:
        for m in AUDITED.finditer(p.read_text(errors="ignore")):
            rec, last = p.name, m.group(1)
    if last is None:
        return [f"reading: audit watermark: {live}; none: first exercise"]
    return [f"reading: audit watermark: {live}; {rec}: {'unchanged' if live in last else 'changed'}"]


# ---- P2, the registry (dyad/dmc/audit-fences.jsonld)
def registry_text(root: Path) -> str | None:
    r = subprocess.run([sys.executable, str(root / "dyad" / "scripts" / "package.py"), "check", "--list"], cwd=root,
                       capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
    return r.stdout.rstrip("\n") + "\n" if r.returncode == 0 else None


def registry(root: Path) -> list[str]:
    """The registry's line count and digest, as the audit's `fences` step printed them, against the newest record's
    `**Fences:**` line: same, grew, shrank (or changed, the count equal and the digest not)."""
    text = registry_text(root)
    if text is None:
        return ["reading: audit fences: registry not read (`check --list` failed)"]
    n, h = len(text.splitlines()), hashlib.sha256(text.encode()).hexdigest()[:16]
    rec, last = None, None
    d = audits_dir(root)
    for p in sorted(d.glob("*-audit.md")) if d.is_dir() else []:
        for m in FENCES.finditer(p.read_text(errors="ignore")):
            if (g := REGISTRY.search(m.group(1))):
                rec, last = p.name, (int(g.group(1)), g.group(2))
    if last is None:
        verdict = "none: first exercise"
    else:
        verdict = f"{rec}: " + ("same" if last == (n, h) else "grew" if n > last[0] else "shrank" if n < last[0] else "changed")
    return [f"reading: audit fences: registry {n} lines, sha256 {h}; {verdict}"]


def labels(root: Path) -> set[str]:
    pkg = root / "dyad"
    return {f"{g}/{e}" for _, g, e in (dyadlib.guard_key(py, pkg) for py in dyadlib.guard_files(pkg))}


def newest_tag(root: Path, pattern: str) -> str | None:
    tags = _git(root, "tag", "--merged", "HEAD", "--list", pattern, "--sort=-v:refname")
    return tags.split()[0] if tags else None


def guards_at(root: Path, tag: str, prefix: str, craft: bool) -> set[str]:
    """The guard labels a tag's tree holds under `prefix` (`dyad/guards` or `crafts/<c>/guards`)."""
    out = set()
    for p in (_git(root, "ls-tree", "-r", "--name-only", tag, "--", prefix) or "").splitlines():
        parts = p.split("/")
        if not parts[-1].endswith(".py") or parts[-1].startswith("_"):
            continue
        if craft and len(parts) == 4:
            out.add(f"{parts[1]}/{parts[3][:-3]}")
        elif not craft and len(parts) == 4:
            out.add(f"{parts[2]}/{parts[3][:-3]}")
    return out


def guards_left(root: Path) -> list[str]:
    """A guard the newest release tag reachable from HEAD holds and the registry does not: the core's against
    `dyad-operator-v*`, each craft's against its own `<craft>-v*`; a craft that left the tree is skipped (#618 Q3)."""
    now, out = labels(root), []
    tag = newest_tag(root, CORE_TAG)
    pairs = [(tag, guards_at(root, tag, "dyad/guards", False))] if tag else []
    tracked = (_git(root, "ls-tree", "-d", "--name-only", "HEAD", "crafts/") or "").splitlines()   # the tree's, not the disk's
    for c in sorted(Path(p).name for p in tracked):
        if (t := newest_tag(root, f"{c}-v*")):
            pairs.append((t, guards_at(root, t, f"crafts/{c}/guards", True)))
    for t, held in pairs:
        out += [f"finding: audit fences: guard {g} is in {t} and not in the registry" for g in sorted(held - now)]
    if not tag:
        out.append("reading: audit fences: no core release tag reachable from main; the guards that left are not read")
    return out


# ---- P5, the Rules against the newest Rule-5 sweep record
def rule_drift(root: Path) -> list[str]:
    rules = _git(root, "log", "-1", "--format=%H", "--", "dyad/rules")
    if not rules:
        return []
    rec = newest(root, RULE_SWEEP)
    if rec is None:
        return ["finding: audit drift: dyad/rules/ changed after the newest Rule-5 sweep record (none)"]
    added = _git(root, "log", "--diff-filter=A", "-1", "--format=%H", "--", str(rec.relative_to(root)))
    if added and _git(root, "merge-base", "--is-ancestor", rules, added) is None:
        return [f"finding: audit drift: dyad/rules/ changed after the newest Rule-5 sweep record ({rec.name})"]
    return []


# ---- P10 and P11, the incident log and the hardening watermark (dyad/dmc/hardening-survey.jsonld)
def incidents(root: Path) -> list[str]:
    inc = dyadlib.load_module(HERE / "incidents.py", "incidents")
    path = inc.log_path(root)
    rows = inc.parse(path)
    if not rows:
        return ["reading: incidents: no log" if not path.is_file() else "reading: incidents: 0 rows"]
    months = ", ".join(f"{k or 'undated'} {len(v)}" for k, v in inc.by_year_month(rows).items())
    per: dict[str, int] = {}
    for r in rows:
        for i in set(r["ids"]):
            per[i] = per.get(i, 0) + 1
    latest = max((r["date"] for r in rows if r["date"][:2] == "20"), default="none")
    return [f"reading: incidents: {len(rows)} rows, latest {latest}; per month {months}; "
            f"{sum(1 for n in per.values() if n > 1)} d-works carry two or more rows"]


def index_for(ledger: Path, root: Path | None = None) -> tuple[Path, int, str] | None:
    """(index, rows, latest) of the watermark line, among the index audits beside `ledger`, that names it (by its path
    from `root`, as the survey's `grep -F "$LEDGER"` matched) and comes last; None when none does."""
    name = ledger.relative_to(root).as_posix() if root and ledger.is_relative_to(root) else str(ledger)
    found = None
    for p in sorted(ledger.parent.glob("*-incident-failure-modes.md")):
        for line in p.read_text(errors="ignore").splitlines():
            if name in line and (m := WATERMARK.search(line)):
                found = (p, int(m.group(1)), m.group(2))
    return found


def hardening(root: Path, ledger: Path | None = None) -> tuple[list[str], str]:
    """(lines, outcome): the live ledger's row count and latest date against the newest index's watermark —
    `first exercise` when no index names the ledger, `no-op` when the two agree, `delta` when the ledger holds more."""
    ledger = Path(ledger) if ledger else audits_dir(root) / "INCIDENTS.md"
    if not ledger.is_absolute():
        ledger = root / ledger
    if not ledger.is_file():
        return [f"reading: hardening: no ledger {ledger.name}"], OUTCOMES[0]
    dates = LOG_ROW.findall(ledger.read_text(errors="ignore"))
    n, latest = len(dates), max(dates, default="none")
    live = f"reading: hardening: live {n} rows, latest {latest}"
    ix = index_for(ledger, root)
    if ix is None:
        return [f"{live}; no index audit names {ledger.name}: first exercise"], OUTCOMES[0]
    p, m, d = ix
    lines = [f"{live}; {p.name}: {m} rows, latest {d}"]
    if n > m or latest > d:
        return [f"finding: hardening: {ledger.name} holds rows past the watermark of {p.name}"] + lines, OUTCOMES[2]
    return lines, OUTCOMES[1]


# ---- P16 and P17, the newest index's fence rows and fences
def mode_table(text: str) -> tuple[list[str], list[list[str]]] | None:
    for h, rows in dyadlib.tables(text):
        if h and h[0].strip().lower() == "mode":
            return [c.strip().lower() for c in h], rows
    return None


def resolves(root: Path, token: str, known: set[str]) -> bool:
    """A fence token resolves: a registry label, a file or directory of the tree, or `<path>:<name>` whose file
    defines that top-level name (read with `ast`, never imported)."""
    token = token.strip()
    if LABEL.fullmatch(token) and token in known:
        return True
    path, _, name = token.partition(":")
    p = root / path
    if not name:
        return bool(path) and p.exists()
    if not (p.is_file() and p.suffix == ".py"):
        return False
    try:
        tree = ast.parse(p.read_text(errors="ignore"))
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return True
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                return True
    return False


def index_fences(root: Path, known: set[str] | None = None) -> list[str]:
    """P16: every fence-row cell of the newest index's mode table resolves to a ledger row (existence only, F8); the
    `fence row` column, or, on an index written before that column, the row cell of a mode closed by a row. P17: each
    token of the `fence` column of a mode closed by a fence (`exit` 1) resolves; an index with no `fence` column is
    one finding saying so, never silence."""
    ix = newest(root, INDEX)
    if ix is None:
        return []
    t = mode_table(ix.read_text(errors="ignore"))
    if t is None:
        return [f"finding: hardening: {ix.name} has no mode table; its fence rows and fences are not read"]
    cols, rows = t
    cell = lambda r, c: (r[cols.index(c)].strip() if c in cols and cols.index(c) < len(r) else "")
    rows_dir = dyadlib.instance(root) / "d-work" / "rows"
    out, cells = [], {}
    legacy = next((c for c in cols if "row" in c and c != "closed by"), None) if "fence row" not in cols else None
    for r in rows:
        mode = cell(r, "mode")
        if "fence row" in cols:
            v = cell(r, "fence row")
        elif legacy and cell(r, "closed by").lower().startswith("row"):
            v = cell(r, legacy)
        else:
            continue
        if v in NONE_CELLS:
            continue
        ids = FENCE_ROW.findall(v)
        if not ids or not all((rows_dir / f"{i}.md").is_file() for i in ids):
            cells.setdefault(v.replace("`", ""), []).append(mode)
    for v, modes in cells.items():
        out.append(f"finding: hardening: {ix.name} {'modes' if len(modes) > 1 else 'mode'} {', '.join(modes)} "
                   f"{'name' if len(modes) > 1 else 'names'} fence row {v}, which is no ledger row")
    if "fence" not in cols:
        return out + [f"finding: hardening: {ix.name} has no fence column; the closed modes' fences are not read"]
    known = labels(root) if known is None else known
    for r in rows:
        if "exit" in cols and cell(r, "exit") != "1":
            continue
        for tok in TOKEN.findall(cell(r, "fence")):
            if not resolves(root, tok, known):
                out.append(f"finding: hardening: {ix.name} mode {cell(r, 'mode')} names fence {tok}, which does not resolve")
    return out


# ---- P19, the newest record's two lines
def record_lines(root: Path, rec: Path | None = None) -> list[str]:
    rec = rec or newest(root, AUDIT_RECORD)
    if rec is None or not rec.is_file():
        return []
    text = rec.read_text(errors="ignore")
    return [f"finding: audit record: {rec.name} lacks its {k} line" for k, pat in (("**Audited:**", AUDITED), ("**Fences:**", FENCES))
            if not pat.search(text)]


# ---- P21 and Phase 3's readings
def levels(root: Path) -> list[str]:
    lv = dyadlib.load_module(HERE / "levels.py", "levels")
    return [f"finding: levels: {m}" for m in lv.check_instance(root)]


def presence(root: Path) -> list[str]:
    ss = dyadlib.load_guard("agent", "sessions")
    files = ss.read_all(root)
    return [f"reading: presence: {sum(1 for s in files if ss.is_stale(s.get('seen', '')))} files past the stale window"]


def branches(root: Path) -> list[str]:
    names = (_git(root, "branch", "-r", "--no-merged", "HEAD") or "").split()
    names = [n for n in names if n != "->" and not n.endswith("/HEAD")]
    shown = ", ".join(names[:BRANCHES_SHOWN]) + (f", and {len(names) - BRANCHES_SHOWN} more" if len(names) > BRANCHES_SHOWN else "")
    return [f"reading: branches: {len(names)} not merged into main{': ' + shown if names else ''}"]


def audit(root: Path) -> list[str]:
    """Every check above on the tree at `root`, readings and findings in a fixed order; a check that raises is one
    finding naming it, never a crash of the sweep."""
    out = []
    checks = (("watermark", watermark), ("registry", registry), ("guards_left", guards_left), ("rule_drift", rule_drift),
              ("incidents", incidents), ("hardening", lambda r: hardening(r)[0]), ("index_fences", index_fences),
              ("record_lines", record_lines), ("levels", levels), ("presence", presence), ("branches", branches))
    for name, f in checks:
        try:
            out += f(root)
        except Exception as e:                           # one check's failure is told, the others still run
            out.append(f"finding: audit: {name} not read ({type(e).__name__})")
    return out


def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    root = Path(root or dyadlib.repo_root())
    if a[:1] == ["hardening"] and len(a) <= 2:
        lines, outcome = hardening(root, Path(a[1]) if len(a) == 2 else None)
        print("\n".join(lines + [f"verdict: {outcome}"]))
        return 0
    if a[:1] == ["record"] and len(a) <= 2:
        rec = (Path(a[1]) if Path(a[1]).is_absolute() else root / a[1]) if len(a) == 2 else newest(root, AUDIT_RECORD)
        if rec is None or not rec.is_file():
            print(f"no audit record{f' {a[1]}' if len(a) == 2 else ''}", file=sys.stderr); return 1
        text, bad = rec.read_text(errors="ignore"), record_lines(root, rec)
        print(f"record: {rec.name}")
        print("\n".join(m.group(0) for p in (AUDITED, FENCES) if (m := p.search(text))))
        for line in bad:
            print(line)
        return 1 if bad else 0
    print(USAGE, file=sys.stderr)
    return 2


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
