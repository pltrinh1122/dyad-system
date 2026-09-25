#!/usr/bin/env python3
"""Ops-script guard (entity `ops`, store zone `workstation`; the sysadmin craft's `ops-scripts.md` owns the form this
checks, Rule-18's kernel binds delivery, placed per Rule-11 property 1 — a Tended craft's guard, `crafts/sysadmin/guards/`,
discovered by the core runner as `sysadmin/ops_scripts`, #155). Kernel: Python 3.12+.
Every `<ops>/*.sh` — the scripts the Operator runs for the Agent (plan #128) — passes `bash -n`,
is tracked `100755` in git's index (`dyadlib.tracked_mode`, never the bit on disk: `core.fileMode=false`
hides a 100644 behind a 755 on disk, #135/#141; a script not yet in the index falls back to the disk bit
and warns `untracked: disk mode used`), starts with `#!/usr/bin/env bash`, contains `set -euo pipefail`, and carries the
header lines `# d-work:`, `# class:`, `# undo:`, `# change-log:`, `# postcondition:`, defines a
`postcondition()` function and names `postcondition` at least three times (definition, pre-check,
final assert — property 6, idempotent), carries `# destructive:` and, when its value is not `none`,
defines a `confirm()` function and names `confirm` at least twice in code (definition + one call —
property 7 of the craft rule, destructive steps confirmed at run time). `<ops>` is `DYAD_OPS`, default
`<host>/ops` — `<host>` the host path, preference `host-path`, default `workstation-corpus` (#175) —
(instance, the host zone), relative to the git root; a missing
directory passes. bash is a declared library row (Rule-14); the package never runs the scripts.
  ops_scripts.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("ops_scripts.py: Python 3.12+ required")
import os
import re
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))  # the core craft's library
import dyadlib

ENTITY, CORPUS, TRANSACTION = "ops", "workstation", False
NAME, OWNER = "ops script", "Rule-18"

SHEBANG = "#!/usr/bin/env bash"
STRICT = "set -euo pipefail"
HEADERS = ("# d-work:", "# class:", "# undo:", "# change-log:", "# postcondition:", "# destructive:")
DESTRUCTIVE = "# destructive:"
CONFIRM = "confirm"
CONFIRM_MIN = 2  # definition + one call (Rule-18 property 7)
POSTCOND = "postcondition"
POSTCOND_MIN = 3  # definition + pre-check + final assert (Rule-18 property 6)
# The header schema, in file order: shebang, the six `# key:` lines, strict mode, the two functions.
FIELDS = ("shebang",) + tuple(h[2:] for h in HEADERS) + ("strict mode", f"{POSTCOND}()", f"{CONFIRM}()")
INVARIANTS = [("headers-well-formed", lambda: all(h.startswith("# ") and h.endswith(":") for h in HEADERS) and DESTRUCTIVE in HEADERS),   # crafts/syseng/rules/invariants.md
              ("mins-positive", lambda: CONFIRM_MIN >= 1 and POSTCOND_MIN >= 1)]
_FUNC_RE = re.compile(r"^\s*(?:function\s+)?postcondition\s*\(\s*\)\s*\{?|^\s*function\s+postcondition\b")
_CONFIRM_RE = re.compile(r"^\s*(?:function\s+)?confirm\s*\(\s*\)\s*\{?|^\s*function\s+confirm\b")
_DWORK_HASH = re.compile(r"#(\d+)\b")
_CL_KEY = re.compile(r'row "#(\d+) (H\d+)"')

# REFERENCES_CONTRIB (Rule-11 property 2's contribution mechanism, `agent-corpus/falsification/
# extensibility.md` #101, d-work #100): rows the core register carried as `ops.dwork->row` and
# `ops.changelog->changelog` until PR 2 of #100 retired them — this craft declares its own now.
def ops_dwork(c):
    """`# d-work: #N` header line of each ops script."""
    return [(f"{c.rel(p)} # d-work:", t) for p, text in c.ops.items() for l in text.splitlines() if l.startswith("# d-work:") for t in _DWORK_HASH.findall(l)]

def _row_id_exists(c, t):
    return t.isdigit() and int(t) in c.rows

def ops_changelog_key(c):
    """`# change-log: ... row "#N Hk"` header line of each ops script."""
    return [(f"{c.rel(p)} # change-log:", f"#{m.group(1)} {m.group(2)}") for p, text in c.ops.items()
            for l in text.splitlines() if l.startswith("# change-log:") for m in [_CL_KEY.search(l)] if m]

def _changelog_row_exists(c, t):
    """`#N Hk`: at least one change-log row with d-work `#N` whose action starts `Hk` (re-runs share a key)."""
    header, rows = c.changelog
    if "d-work" not in header or "action" not in header:
        return False
    d, a = header.index("d-work"), header.index("action")
    n, hk = t.split()
    return any(len(r) > max(d, a) and r[d].strip() == n and re.match(rf"{hk}\b", r[a].strip()) for r in rows)

REFERENCES_CONTRIB = [
    ("ops.dwork->row",           "ops", "d-work:",     ops_dwork,        "row",       _row_id_exists),
    ("ops.changelog->changelog", "ops", "change-log:", ops_changelog_key, "changelog", _changelog_row_exists),
]

def destructive_value(lines: list[str]) -> str | None:
    """Value of the `# destructive:` header, or None when absent."""
    for l in lines:
        if l.startswith(DESTRUCTIVE):
            return l[len(DESTRUCTIVE):].strip()
    return None

def ops_dir(root: Path | None = None) -> Path:
    """`DYAD_OPS`, else `<host path>/ops` of the repo at `root` (preference `host-path`, #175)."""
    root = root or dyadlib.repo_root()
    return root / (os.environ.get("DYAD_OPS") or f"{dyadlib.host_path(root)}/ops")

def check_mode(path: Path, root: Path | None) -> list[str]:
    """The script is executable where it counts: `100755` in git's index (`dyadlib.tracked_mode`).
    The bit on disk is not evidence — `core.fileMode=false` on an NTFS checkout shows 755 for a file
    tracked 100644, which is how `135-h2/h4/h5` passed this check while tracked non-executable (#135,
    #141). A script not yet in the index (just written, `DYAD_OPS` outside the work tree) is judged by
    the disk bit and says so, so a new script is still checked and the weaker evidence is named."""
    mode = dyadlib.tracked_mode(root, path) if root is not None else None
    if mode is None:
        fails = [] if os.access(path, os.X_OK) else [f"{path.name}: executable bit not set (chmod 755)"]
        return fails + [f"warning: {path.name}: untracked: disk mode used"]
    return [] if mode == dyadlib.MODE_EXEC else [f"{path.name}: tracked mode {mode} (git update-index --chmod=+x)"]

def check_script(path: Path, text: str | None = None, root: Path | None = None) -> list[str]:
    """Failures for one script, each prefixed by its name; `root` is the work tree whose index holds
    the mode (None: the disk bit, warned as such)."""
    text = path.read_text(errors="ignore") if text is None else text
    lines = text.splitlines()
    fails = []
    if not lines or lines[0].strip() != SHEBANG:
        fails.append(f"{path.name}: first line is not `{SHEBANG}`")
    if not any(l.strip() == STRICT for l in lines):
        fails.append(f"{path.name}: missing `{STRICT}`")
    for h in HEADERS:
        if not any(l.startswith(h) for l in lines):
            fails.append(f"{path.name}: missing header line `{h}`")
    if not any(_FUNC_RE.match(l) for l in lines):
        fails.append(f"{path.name}: no `{POSTCOND}()` function defined")
    code = "\n".join(l for l in lines if not l.lstrip().startswith("#"))
    n = len(re.findall(rf"\b{POSTCOND}\b", code))
    if n < POSTCOND_MIN:
        fails.append(f"{path.name}: `{POSTCOND}` named {n} time(s) in code, need {POSTCOND_MIN} (definition, pre-check, final assert)")
    d = destructive_value(lines)
    if d is not None and d != "none":
        if not any(_CONFIRM_RE.match(l) for l in lines):
            fails.append(f"{path.name}: `{DESTRUCTIVE}` is not `none` but no `{CONFIRM}()` function defined")
        c = len(re.findall(rf"\b{CONFIRM}\b", code))
        if c < CONFIRM_MIN:
            fails.append(f"{path.name}: `{CONFIRM}` named {c} time(s) in code, need {CONFIRM_MIN} (definition, one call before the destructive step)")
    fails += check_mode(path, root)
    r = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        fails.append(f"{path.name}: bash -n failed: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
    return fails

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Failures over every `*.sh` in the ops dir of `root`; no ops dir is ok. `root` is also the work
    tree whose index carries the scripts' modes (check_mode)."""
    root = Path(root) if root is not None else dyadlib.repo_root()
    d = ops_dir(root)
    if not d.is_dir():
        return []
    fails = []
    for p in sorted(d.glob("*.sh")):
        fails += check_script(p, root=root)
    return fails

def summary(root: Path | None = None) -> str:
    d = ops_dir(root)
    return f"{len(list(d.glob('*.sh'))) if d.is_dir() else 0} ops scripts"

def _line_after(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ops = ops_dir(root)
    scripts = sorted(ops.glob("*.sh")) if ops.is_dir() else []
    ex = scripts[0].read_text(errors="ignore") if scripts else ""
    lines = ex.splitlines()
    rel = ops.relative_to(root) if ops.is_relative_to(root) else ops
    fields = []
    for f in FIELDS:
        hdr = f"# {f}"
        if f == "shebang":
            fields.append((f, "line", f"`{SHEBANG}` as line 1", True, lines[0] if lines else "", "ops_scripts.FIELDS"))
        elif f == "strict mode":
            fields.append((f, "line", f"`{STRICT}`", True, next((l.strip() for l in lines if l.strip() == STRICT), ""), "ops_scripts.FIELDS"))
        elif f == f"{POSTCOND}()":
            fields.append((f, "function", f"defined; named >= {POSTCOND_MIN} times in code", True, next((l.strip() for l in lines if _FUNC_RE.match(l)), ""), "ops_scripts.FIELDS"))
        elif f == f"{CONFIRM}()":
            fields.append((f, "function", f"defined and named >= {CONFIRM_MIN} times when `# destructive:` is not `none`", False, next((l.strip() for l in lines if _CONFIRM_RE.match(l)), ""), "ops_scripts.FIELDS"))
        else:
            fields.append((f, "line", "`none` | the destructive step" if hdr == DESTRUCTIVE else "", True, _line_after(ex, hdr), "ops_scripts.FIELDS"))
    return {"store": f"{rel}/<d-work>-<hN>-<slug>.sh", "parser": "`ops_scripts.check_script`", "observed": len(scripts),
            "note": "one file per change-log row; `bash -n` clean, tracked 100755; the package never runs it", "fields": fields}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:                                   # the runner's convention: a `warning:` message is not a failure
        if m.startswith("warning:"):
            print(f"warn [rule-18] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [rule-18] {m}", file=sys.stderr)
    if not fails:
        d = ops_dir(root)
        n = len(list(d.glob("*.sh"))) if d.is_dir() else 0
        print(f"ok   [rule-18] {n} ops scripts")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
