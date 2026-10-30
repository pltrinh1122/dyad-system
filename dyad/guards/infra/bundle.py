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

A craft released and then changed (#170, the released half of #156): its craft-zone PR bumps `VERSION`,
and Rule-1 forbids that PR from carrying the infra-zone row. So a row that is *behind* the live
`VERSION` warns, not fails, while it still names a released version (its own `<name>-v<row>` tag
exists) and the live version has no tag yet — the infra-zone PR that updates the row follows. Any
other mismatch fails: a row ahead of the tree, a row naming an untagged version, or a row left
behind once the live version is itself tagged (a release cannot be cut against a row the tree
contradicts). One exception warns (#481, #522's 0.12.3): a released craft's row behind its live `VERSION`
naming a number never tagged, while the live one is not tagged either — the row was moved to a number no
release cut, and the craft-zone bump that followed it is not one either; the infra-zone PR that corrects
the row follows. Tags not fetched read as untagged, so such a checkout keeps the strict form.

Drift (#91, after #61/#67/#71/#90): property 4's converse. Once `<name>-v<VERSION>` exists, the
tree under that craft's root at HEAD must be the tree the tag holds; `check_drift` fails a craft
whose root differs from its own tag while `VERSION` is unchanged. A tag that does not resolve
locally (never released, or tags not fetched — the kernel-only path never fetches) skips with one
warning line. HEAD, not the working tree: the pre-push hook judges commits.

The bundled-craft criterion (d-work #504, Rule-11 property 2): a Tended craft is bundled with the core
when (a) a core Rule cites it by path, or (b) it serves the system's purpose, declared with a one-line
`PURPOSE` reason. `check_citations` keeps both. (a) Every craft a core Agent Rule (`<pkg>/rules/RULE-*.md`,
the core craft's own Rules, read under `pkg` so an installed tree judges its own) names by path,
`crafts/<name>/`, that is present in the tree and does not declare `BUNDLED_WITH_CORE = True` in one of
its own guard modules fails, naming the citing Rules: a core-only install would ship Rules citing a craft
it does not carry. A cited craft absent from the tree warns, never fails: an installed system, or a
core-only install of a core whose cited craft is not yet declared, has nothing here to judge, and
the craft that would carry the declaration is the one missing. (b) A craft that declares itself and that
no core Rule cites must carry a non-empty one-line `PURPOSE = "..."` in the same guard module as the
declaration; a cited craft may carry one and need not. The clause runs whether or not `BUNDLE.md`
exists: it judges what the core's *release* carries (property 2), not the bundle (property 7). Both
assignments are read as text (`DECLARED`, `PURPOSE_LINE`), never executed: a guard module of another
tree is never imported (`package.bundled_crafts`'s own reading of an `--from` tree, #353), this guard
stays free of `package.py`, which loads it, and a declaration this reading misses — any form but the
literal `BUNDLED_WITH_CORE = True` — fails as undeclared, the strict side.
  bundle.py [repo-root]
"""
import re
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
# d-work #504 (Rule-11 property 2): a core Rule's path citation of a craft, a craft's bundling
# declaration and its purpose line, each read as text from one line (module docstring).
CITATION = re.compile(r"crafts/([a-z0-9][a-z0-9_-]*)/")
DECLARED = re.compile(r"^BUNDLED_WITH_CORE\s*=\s*True\b", re.M)
PURPOSE_LINE = re.compile(r"""^PURPOSE\s*=\s*(?:"[^"\n]*\S[^"\n]*"|'[^'\n]*\S[^'\n]*')""", re.M)
INVARIANTS = [("two-fields", lambda: len(FIELDS) == 2 and len(set(FIELDS)) == 2),   # crafts/syseng/rules/invariants.md
              ("tag-name-is-prefix-v-version", lambda: tag_name("x", "1.2.3") == "x-v1.2.3"),
              ("citation-reads-a-craft-path-not-a-placeholder",
               lambda: CITATION.findall("`crafts/sysarch/rules/x.md`, `crafts/<craft>/`") == ["sysarch"]),
              ("declaration-is-the-literal-true-line",
               lambda: DECLARED.search("BUNDLED_WITH_CORE = True\n") is not None
                       and DECLARED.search("BUNDLED_WITH_CORE = False\n") is None
                       and DECLARED.search("# BUNDLED_WITH_CORE = True\n") is None),
              ("purpose-is-a-non-empty-one-line-string",
               lambda: PURPOSE_LINE.search('PURPOSE = "serves every Operator"\n') is not None
                       and PURPOSE_LINE.search('PURPOSE = ""\n') is None
                       and PURPOSE_LINE.search('PURPOSE = "  "\n') is None)]

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

def tagged_versions(root: Path, components) -> set[tuple[str, str]]:
    """{(component, version)} for every local release tag `<name>-v<version>` (property 4)."""
    out = set()
    for c in components:
        prefix = f"{c}-v"
        for t in _git(root, "tag", "-l", tag_pattern(c)).stdout.split():
            if t.startswith(prefix):
                out.add((c, t[len(prefix):]))
    return out

def _semver(v: str) -> tuple[int, ...] | None:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return None

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

def check(version: str, rows: list[tuple[str, str]], live: dict[str, str], released: set[str] | None = None,
          tagged: set[tuple[str, str]] | None = None, departed: set[str] | None = None) -> list[str]:
    """`released`: the components with a release tag of their own; None treats every one as released
    (the strict form). A released craft with no row fails; an unreleased one warns (Rule-11 p7, #156).
    `tagged`: the (component, version) pairs with a release tag; None is the strict form, where every
    version mismatch fails. Given, a row behind an untagged live version that names a tagged one warns
    (#170): the craft-zone bump lands first and the row follows. `departed`: the row components absent from
    the tree that hold a release tag of their own; such a row warns (#423) — the craft-zone PR that removes or
    renames a released craft lands first and the infra-zone PR removing the row follows. None, or a component
    never released, keeps the strict form: a row naming a craft not in the tree fails."""
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
            if departed is not None and comp in departed:
                msgs.append(f"warning: '{comp}' has left the tree but holds a release tag ({tag_pattern(comp)}): the row is removed by an infra-zone PR (#423)")
            else:
                msgs.append(f"'{comp}': not a craft in this tree")
        elif ver != live[comp]:
            row_v, live_v = _semver(ver), _semver(live[comp])
            behind = row_v is not None and live_v is not None and row_v < live_v
            if tagged is not None and behind and (comp, ver) in tagged and (comp, live[comp]) not in tagged:
                msgs.append(f"warning: '{comp}': bundle names {ver}, the tree has {live[comp]}, which is unreleased: the row follows in an infra-zone PR (#170)")
            elif tagged is not None and behind and comp in released and (comp, ver) not in tagged and (comp, live[comp]) not in tagged:
                msgs.append(f"warning: '{comp}': bundle names {ver}, which was never released (no {comp}-v{ver} tag), and the tree has "
                            f"{live[comp]}, also unreleased: the row names a number no archive holds, and an infra-zone PR moves it "
                            f"to the last release or to the version being cut (#481)")
            else:
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
    gone = {c for c, _ in rows if c and c not in live}
    return version, rows, check(version, rows, live, released_components(root, live), tagged_versions(root, live),
                                released_components(root, gone))

def cited_crafts(pkg: Path = dyadlib.PKG) -> dict[str, list[str]]:
    """{craft: [citing Rule file names]}: every craft a core Agent Rule (`<pkg>/rules/RULE-*.md`) names
    by path, `crafts/<name>/`. Rules only — a citation in any other file (a play-book, a record, a
    README) is prose, not a dependency of the core's Rules (d-work #504)."""
    out: dict[str, list[str]] = {}
    for f in sorted((pkg / "rules").glob("RULE-*.md"), key=lambda f: (len(f.name.split("-")[1]), f.name)):
        for name in sorted(set(CITATION.findall(f.read_text()))):
            out.setdefault(name, []).append(f.name)
    return out

def declarations(craft: Path) -> list[tuple[str, bool]]:
    """[(guard module name, carries PURPOSE)] for every guard module of one craft that declares
    `BUNDLED_WITH_CORE = True`, read as text (module docstring). Same discovery as
    `dyadlib.guard_files`: `crafts/<craft>/guards/*.py`, names starting `_` excluded."""
    out = []
    for py in sorted((craft / "guards").glob("*.py")):
        if py.name.startswith("_"):
            continue
        text = py.read_text()
        if DECLARED.search(text):
            out.append((py.name, PURPOSE_LINE.search(text) is not None))
    return out

def check_citations(pkg: Path = dyadlib.PKG) -> list[str]:
    """Rule-11 property 2's criterion (d-work #504): cited and present and undeclared fails; cited and
    absent warns; declared and uncited without a `PURPOSE` beside the declaration fails."""
    msgs: list[str] = []
    cited = cited_crafts(pkg)
    present = {d.name: d for d in dyadlib.craft_dirs(pkg)}
    for name, rules in cited.items():
        if name not in present:
            msgs.append(f"warning: '{name}': cited by path in {', '.join(rules)} but not in this tree — nothing here to judge (#504)")
        elif not declarations(present[name]):
            msgs.append(f"'{name}': cited by path in {', '.join(rules)} but not bundled — declare `BUNDLED_WITH_CORE = True` "
                        f"in one of crafts/{name}/guards/*.py (Rule-11 property 2, #504)")
    for name, d in present.items():
        decl = declarations(d)
        if decl and name not in cited and not any(has for _, has in decl):
            msgs.append(f"'{name}': declares `BUNDLED_WITH_CORE` in {', '.join(m for m, _ in decl)} but no core Rule cites it — "
                        f"a one-line `PURPOSE = \"...\"` beside the declaration is required (Rule-11 property 2, #504)")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    return check_bundle(root, pkg)[2] + check_drift(root, pkg) + check_citations(pkg)

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
        msgs = check_citations(pkg)          # property 2's criterion holds without a bundle (#504)
        for m in msgs:
            if m.startswith("warning:"):
                print(f"warn [bundle] {m.removeprefix('warning:').strip()}")
            else:
                print(f"FAIL [bundle] {m}", file=sys.stderr)
        return 1 if any(not m.startswith("warning:") for m in msgs) else 0
    version, rows, msgs = check_bundle(root, pkg)
    msgs += check_drift(root, pkg) + check_citations(pkg)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"):
            print(f"warn [bundle] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [bundle] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [bundle] {len(rows)} components, v{version}")
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main())
