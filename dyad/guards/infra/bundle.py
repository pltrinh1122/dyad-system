#!/usr/bin/env python3
"""Bundle guard (entity `bundle`, infra corpus; Rule-11 owns the check, placed per Rule-11 property 1). Kernel: Python 3.12+.
`BUNDLE.md` (repo root, infra zone — a distribution artifact of the authoring repo, never craft
content, so a core-only install carries no bundle naming a craft it lacks, Rule-11 property 7) names
the whole distribution this repo authors: one row per craft in the tree, the core craft
(`CORE_NAME`) plus every Tended craft `dyadlib.craft_dirs` finds. A row's version must equal that
craft's live `VERSION`; every *released* craft in the tree needs a row and every row names a craft
in the tree — checked both directions. A craft with no release tag of its own (`<name>-v*`, see
`released_components`) and no row warns instead: it is unreleased, so it has no archive to bundle,
and its first release adds its row (#156: a new craft otherwise had no order satisfying both Rule-1's
one zone per PR and this guard). A missing `BUNDLE.md` skips (a core-only install, or this repo
before its first bundle): zero messages, never a failure.

Drift (#91, after #61/#67/#71/#90): property 4's converse. Once `<name>-v<VERSION>` exists, the
tree under that craft's root at HEAD must be the tree the tag holds; `check_drift` fails a craft
whose root differs from its own tag while `VERSION` is unchanged. A tag that does not resolve
locally (never released, or tags not fetched — the kernel-only path never fetches) skips with one
warning line. HEAD, not the working tree: the pre-push hook judges commits.
  bundle.py [repo-root]
"""
import subprocess
import sys
if sys.version_info < (3, 12):
    sys.exit("bundle.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "bundle", "infra", False
NAME, OWNER = "bundle row", "Rule-11"
CORE_NAME = "dyad-operator"                        # crafts/craft.py's own CORE_NAME; a bundle row uses the same name
FIELDS = ("component", "version")
INVARIANTS = [("two-fields", lambda: len(FIELDS) == 2 and len(set(FIELDS)) == 2),   # crafts/syseng/rules/invariants.md
              ("tag-name-is-prefix-v-version", lambda: tag_name("x", "1.2.3") == "x-v1.2.3")]

def tag_name(component: str, version: str) -> str:
    """Rule-11 property 4: `<name>-v<VERSION>` for every craft, the core included (`dyad-operator-v…`)."""
    return f"{component}-v{version}"

def tag_pattern(component: str) -> str:
    """The `git tag -l` pattern for every release of one craft (property 4): `<name>-v*`."""
    return f"{component}-v*"

def component_roots(root: Path, pkg: Path = dyadlib.PKG) -> dict[str, Path]:
    """{component: root-relative craft root}: the core craft's `dyad/` plus every Tended craft's."""
    out = {CORE_NAME: pkg.resolve().relative_to(root.resolve())}
    for d in dyadlib.craft_dirs(pkg):
        out[d.name] = d.resolve().relative_to(root.resolve())
    return out

def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)

def released_components(root: Path, components) -> set[str]:
    """The components with at least one local release tag of their own (`<name>-v*`). Tags not
    fetched read as unreleased — the kernel-only path never fetches — which only softens a missing
    row to a warning; it never hides a row naming a craft not in the tree."""
    return {c for c in components if _git(root, "tag", "-l", tag_pattern(c)).stdout.strip()}

def check_drift(root: Path, pkg: Path = dyadlib.PKG) -> list[str]:
    """Per component: tag absent -> `warning: skip …`; tree at HEAD == tag's -> nothing; differs -> FAIL."""
    msgs: list[str] = []
    if _git(root, "rev-parse", "--verify", "-q", "HEAD^{commit}").returncode != 0:
        return [f"warning: skip drift: no HEAD commit here"]
    roots = component_roots(root, pkg)
    for comp, ver in live_components(pkg).items():
        tag = tag_name(comp, ver)
        if _git(root, "rev-parse", "--verify", "-q", f"{tag}^{{commit}}").returncode != 0:
            msgs.append(f"warning: skip '{comp}': no tag {tag} here (not yet released, or tags not fetched)")
            continue
        rel = roots[comp].as_posix()
        r = _git(root, "diff", "--name-only", tag, "HEAD", "--", rel)
        changed = [l for l in r.stdout.splitlines() if l.strip()]
        if changed:
            msgs.append(f"'{comp}': {rel}/ differs from tag {tag} ({len(changed)} file(s)) while VERSION is still {ver} — bump VERSION")
    return msgs

def bundle_path(root: Path) -> Path:
    return root / "BUNDLE.md"

def parse(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(version, rows): the `version:` line and the table's (component, version) pairs, emphasis
    stripped. A malformed row (not exactly 2 cells) contributes nothing; `check` reports it."""
    version = ""
    for line in text.splitlines():
        if line.startswith("version:"):
            version = dyadlib.plain(line.split(":", 1)[1]).strip()
            break
    rows = [tuple((dyadlib.plain(c).strip() for c in r)) for r in dyadlib.table_rows(text)]
    return version, [r for r in rows if len(r) == 2]

def live_components(pkg: Path = dyadlib.PKG) -> dict[str, str]:
    """{component: version} the tree actually holds: the core craft plus every Tended craft."""
    out = {CORE_NAME: (pkg / "VERSION").read_text().strip()}
    for d in dyadlib.craft_dirs(pkg):
        out[d.name] = (d / "VERSION").read_text().strip()
    return out

def check(version: str, rows: list[tuple[str, str]], live: dict[str, str], released: set[str] | None = None) -> list[str]:
    """`released`: the components with a release tag of their own; None treats every one as released
    (the strict form). A released craft with no row fails; an unreleased one warns (Rule-11 p7, #156)."""
    released = set(live) if released is None else released
    msgs: list[str] = []
    if not version:
        msgs.append("no `version:` line")
    seen: set[str] = set()
    for comp, ver in rows:
        if not comp or not ver:
            msgs.append(f"row {(comp, ver)!r}: malformed (needs a component and a version)"); continue
        if comp in seen:
            msgs.append(f"'{comp}': declared twice")
        seen.add(comp)
        if comp not in live:
            msgs.append(f"'{comp}': not a craft in this tree")
        elif ver != live[comp]:
            msgs.append(f"'{comp}': bundle names {ver}, the tree has {live[comp]}")
    for comp in live:
        if comp in seen:
            continue
        if comp in released:
            msgs.append(f"'{comp}' is in the tree but has no bundle row")
        else:
            msgs.append(f"warning: '{comp}' is in the tree but unreleased (no {tag_pattern(comp)} tag): not yet bundled")
    return msgs

def check_bundle(root: Path | None = None, pkg: Path = dyadlib.PKG) -> tuple[str, list[tuple[str, str]], list[str]]:
    """(version, rows, messages); (\"\", [], []) when `BUNDLE.md` is absent — skip, never fail."""
    root = root or dyadlib.repo_root()
    p = bundle_path(root)
    if not p.exists():
        return "", [], []
    version, rows = parse(p.read_text())
    live = live_components(pkg)
    return version, rows, check(version, rows, live, released_components(root, live))

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    return check_bundle(root, pkg)[2] + check_drift(root, pkg)

def summary(root: Path | None = None) -> str:
    version, rows, _ = check_bundle(root)
    return f"{len(rows)} components (v{version})" if version or rows else "no bundle"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    p = bundle_path(root)
    _, rows, _ = check_bundle(root, pkg)
    ex = rows[0] if rows else None
    rel = p.relative_to(root) if p.is_relative_to(root) else p
    return {"store": str(rel), "parser": "`bundle.parse`", "observed": len(rows),
            "note": "one row per craft in the tree; a row's version must equal that craft's live VERSION",
            "fields": [(c, "text", "", True, ex[i] if ex else "", "bundle.FIELDS") for i, c in enumerate(FIELDS)]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    pkg = (root / "dyad") if a else dyadlib.PKG        # an explicit root names its own core craft
    if not bundle_path(root).exists():
        print("skip [bundle] no BUNDLE.md")
        return 0
    version, rows, msgs = check_bundle(root, pkg)
    msgs += check_drift(root, pkg)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"):
            print(f"warn [bundle] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [bundle] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [bundle] {len(rows)} components, v{version}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
