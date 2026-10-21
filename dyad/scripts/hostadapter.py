"""dyad host adapter (`crafts/syseng/rules/host-facts.md`, d-work #179): the one place a host fact
is read, so every call site sees the same answer regardless of which one asked. Rule-14 ("Library
and The World"): The World is observed, not pinned — a host's own filesystem layout (macOS's `/var`
-> `/private/var`) is such an observation, not a thing the package controls or should special-case
per call site. A library: no check semantics of its own (S4); its own check is
`dyad/tests/test_hostadapter.py` (`crafts/syseng/rules/verifiable-code.md` p4's mapping). Kernel:
Python 3.12+; stdlib only (Rule-14: no new manifest row — `hostadapter` resolves as a
package-internal import, `dyad/guards/infra/manifest.py`'s `python_imports`).

Two functions, not a framework (`host-facts.md` property 2): `resolve` wraps `Path.resolve()` so
`distribute.py`/`package.py` never call it inline (G5, d-work #179: a test once compared an
unresolved path against `distribute.install`'s already-resolved one, passing only by the accident
that this kernel's `/tmp` is not itself a symlink). `ignore_patterns` derives the Rule-11 property 6
`generated:` list of `package_rules.txt` — never a second, hand-kept copy of it — translated to
gitignore syntax, and `write_gitignore` seeds it once (G9: a fresh install's first `dyad` command
writes `dyad/scripts/__pycache__/`, and `git add -A` then tracks it). A third host fact either fits
one of these two functions or earns its own, justified in the plan that adds it — never a generic
hook (`host-facts.md` property 2). `session_title` is that third fact (d-work #350, plan item A6):
the Operator's own name for a harness session, which only the harness records.
"""
import json, os, re
from pathlib import Path

TITLE_MAX = 120   # the presence file's `title` line is bounded; `sessions.check_record` enforces it

HEADER = "# seeded by dyad install (hostadapter.write_gitignore) from dyad/scripts/package_rules.txt\n"


def resolve(path) -> Path:
    """The one place a host path is resolved to its canonical, symlink-free form. Every
    install/build destination and repo-root comparison `distribute.py`/`package.py` make calls
    this instead of `Path(...).resolve()` inline — grepping the two files for `.resolve()` after
    this change finds only the bootstrap `PKG = Path(__file__).resolve().parent.parent` lines,
    which must run before this module can even be imported (`craft.py`'s own such line is the
    third; it has no other `.resolve()` call to route)."""
    return Path(path).resolve()


def _to_gitignore(pattern: str) -> str:
    """One `package_rules.txt` `generated:` pattern (matched by `check_generated` at any path
    depth, component-wise — the whole path, any one segment, or any suffix starting at a segment)
    as one gitignore line matching at the same depths: a `dir/*` pattern becomes `dir/` — a
    trailing-only slash is unanchored under gitignore's own rule ("a separator at the beginning or
    middle" anchors; one only at the end does not), so it matches a directory named `dir` at any
    depth. A literal `dir/*` would not: gitignore anchors a *middle* slash to the `.gitignore`
    file's own directory, so a naive translation would miss a nested `dyad/scripts/__pycache__/`
    (G9's exact case) and only catch a root-level one. Any other pattern with an interior slash
    (`ops/*.log`) is prefixed `**/` for the same any-depth match. A slash-free pattern (`*.pyc`,
    `LEDGER.md`) is already unanchored and needs no change."""
    if pattern.endswith("/*"):
        return pattern[:-1]
    return f"**/{pattern}" if "/" in pattern else pattern


def ignore_patterns(root) -> list[str]:
    """Rule-11 property 6's `generated:` patterns, translated by `_to_gitignore`; parsed straight
    from `<root>/dyad/scripts/package_rules.txt` — the same file `check_generated` reads — so the
    list can never drift from it (never hand-duplicated here). Sorted, deduplicated; `[]` when that
    file is not (yet) part of the tree at `root` (a Tended-craft-only root; a fixture without a
    core craft)."""
    p = Path(root) / "dyad" / "scripts" / "package_rules.txt"
    if not p.is_file():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, val = line.partition(":")
        if kind.strip() == "generated":
            out.append(_to_gitignore(val.strip()))
    return sorted(set(out))


def write_gitignore(dest) -> bool:
    """Seed `<dest>/.gitignore` from `ignore_patterns(dest)` when the file is absent. Never
    overwrites — idempotent (`crafts/syseng/rules/idempotence.md` property 1) and consistent with
    Rule-11 property 2, "never overwrites a host file". `True` when it wrote, so a caller can count
    it as one change the way `distribute.install`'s other hooks already do."""
    dest = Path(dest)
    f = dest / ".gitignore"
    if f.exists():
        return False
    patterns = ignore_patterns(dest)
    if not patterns:
        return False
    f.write_text(HEADER + "\n".join(patterns) + "\n")
    return True


def _clean_title(value) -> str | None:
    """One line, bounded, or None: whitespace (newlines included) collapses to single spaces so a
    title can never become a second `key: value` line of the file that stores it."""
    if not isinstance(value, str):
        return None
    s = " ".join(value.split())[:TITLE_MAX].strip()
    return s or None


def session_title(holder: str, config_dir=None) -> str | None:
    """The Operator's own name for harness session `holder`, as the harness records it, or None.

    Read, in order, from the harness's per-process record `<config>/sessions/<pid>.json` — its
    `name`, taken only when `nameSource` is `user`, so a name the harness generated never passes
    as the Operator's; where several pids have held the session the latest `nameSince` wins — and
    then from `<config>/projects/<slug>/<holder>/custom-title.json` (`customTitle`). `<config>` is
    `config_dir`, else `CLAUDE_CONFIG_DIR`, else `~/.claude`. A kernel that keeps neither file, an
    unreadable or malformed one, or a `holder` that is not a plain path segment gives None, never
    an error: the title is a convenience that joins the Operator's name for a session to the seat,
    and nothing depends on it."""
    if not holder or "/" in holder or holder.startswith("."):
        return None
    base = Path(config_dir) if config_dir else Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    best = None   # (nameSince, name)
    for f in sorted(base.glob("sessions/*.json")):
        try:
            rec = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(rec, dict) or rec.get("sessionId") != holder or rec.get("nameSource") != "user":
            continue
        name, since = _clean_title(rec.get("name")), rec.get("nameSince")
        since = since if isinstance(since, (int, float)) else 0
        if name and (best is None or since >= best[0]):
            best = (since, name)
    if best:
        return best[1]
    for f in sorted(base.glob(f"projects/*/{holder}/custom-title.json")):
        try:
            rec = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        name = _clean_title(rec.get("customTitle")) if isinstance(rec, dict) else None
        if name:
            return name
    return None
