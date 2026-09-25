#!/usr/bin/env python3
"""Craft guard (entity `craft`, corpus `craft`; Rule-11 owns the craft's shape, placed per Rule-11 property 1; #156). Kernel: Python 3.12+.
Per Tended craft `crafts/<name>/`: VERSION present and MAJOR.MINOR.PATCH (fail); no instance state inside the
tree — host strings, instance artifacts by name or header (distribute.instance_state with package_rules.txt,
the core's own scan, plus crafts_rules.txt `name:` entries; templates/ exempt) (fail); the vocabulary is
namespaced — `vocabulary/CRAFT.md` well-formed, no term equal to an Agent term (vocabulary.check_craft, Rule-6)
(fail; a word shared by two crafts warns); every `guards/*.py` loads and declares the guard contract
(dyadlib.contract_problem, crafts/sysarch/rules/guards.md) (fail); Agent-process tokens in `rules/*.md` warn (rules.check_tended,
Rule-4: the classification is inference); an unmet `MANIFEST.md` `requires:` warns here and refuses at install.
`MANIFEST.md` `seeds:` (`<template>-><instance path>`, #180) names an instance file a template
corresponds to: the named `templates/<file>` must exist and the destination's zone
(`containment.classify`) must be one this craft's own guards already declare as `CORPUS` (fail
otherwise — a craft may only seed what it already owns a guard for); a destination also declared
by another present craft warns (first Operator to copy wins; nothing is ever written here). It is
never copied — Rule-11 property 2 reserves host-side hooks to the core craft; `seed_status()`
below only reports a seed's destination as absent, in the real repo the caller names, so
`dyad craft check` and `dyad craft install` can point at the manual step.
The guard composes the Rule-4 and Rule-6 scans by import (crafts/sysarch/rules/guards.md p3); it owns only the craft shape.
  crafts.py [<craft>]        (from the git root; every craft when none is named)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("crafts.py: Python 3.12+ required")
import io, subprocess, tarfile, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib, distribute

ENTITY, CORPUS, TRANSACTION = "craft", "craft", False
NAME, OWNER = "craft", "Rule-11"
DIRS = ("rules", "vocabulary", "templates", "guards", "docs", "falsification")
FIELDS = ("name", "version", *DIRS, "requires", "seeds")
INVARIANTS = [("dirs-distinct", lambda: len(set(DIRS)) == len(DIRS)),   # crafts/syseng/rules/invariants.md
              ("fields-cover-dirs", lambda: set(DIRS) <= set(FIELDS) and FIELDS[:2] == ("name", "version")),
              ("semver-is-the-shared-grammar", lambda: SEMVER is dyadlib.SEMVER)]
SEMVER = dyadlib.SEMVER   # one grammar, shared with the core's own VERSION check (D2, #100)
CORE_NAME = "dyad-operator"                       # the name a `requires:` uses for the core craft
DATA = Path(__file__).resolve().parent / "crafts_rules.txt"

def data(path: Path = DATA) -> dict[str, list[str]]:
    out = {"name": [], "agent-token": []}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, _, v = line.partition(":"); out.setdefault(k.strip(), []).append(v.strip())
    return out

def package_rules(pkg: Path, root: Path | None = None) -> dict[str, list[str]]:
    """Rule-11's own data plus the instance's local rows (dyadlib.package_rules, #192): the same markers the core scan uses."""
    return dyadlib.package_rules(pkg, root)

semver = dyadlib.semver_tuple   # `+build` suffix stripped before comparing (D2, #100)

def manifest(craft_dir: Path) -> dict[str, str]:
    f = Path(craft_dir) / "MANIFEST.md"
    return dyadlib.parse_kv(f.read_text()) if f.exists() else {}

def requires(craft_dir: Path) -> list[tuple[str, str]]:
    """[(craft, minimum version)] from `requires: a>=1.0.0 b>=0.2.0`; absent manifest = none."""
    out = []
    for tok in manifest(craft_dir).get("requires", "").split():
        name, _, ver = tok.partition(">=")
        out.append((name, ver or "0.0.0"))
    return out

HOST_TOKEN = "<host>"   # in a `seeds:` destination: the receiving system's host path (dyadlib.host_path, #175)

def seeds(craft_dir: Path, root: Path | None = None) -> list[tuple[str, str]]:
    """[(template name, instance-relative dest)] from `seeds: CHANGELOG.md-><host>/CHANGELOG.md
    ...` (MANIFEST.md, space-separated `<template>-><dest>` tokens, the same shape as `requires:`);
    absent manifest = none. With `root`, a leading `<host>` in a destination is that repo's host path
    (`dyadlib.host_path`, #175); without, the destination is returned as written. Never copied
    (Rule-11 p2: host-side hooks are the core craft's only) — `check_craft` validates the mapping
    (template exists, destination zone is one this craft's own guards claim) and `seed_status`
    reports an absent destination in a named repo; #180."""
    out, host = [], dyadlib.host_path(Path(root)) if root is not None else None
    for tok in manifest(craft_dir).get("seeds", "").split():
        tmpl, sep, dest = tok.partition("->")
        if sep and tmpl and dest:
            if host is not None and dest.startswith(HOST_TOKEN + "/"):
                dest = host + dest[len(HOST_TOKEN):]
            out.append((tmpl, dest))
    return out

def version(craft_dir: Path) -> str:
    f = Path(craft_dir) / "VERSION"
    return f.read_text().strip() if f.exists() else ""

def parse(craft_dir: Path) -> dict:
    """The craft as the entities surface shows it (FIELDS)."""
    d = Path(craft_dir)
    row = {"name": d.name, "version": version(d)}
    row.update({k: (d / k).is_dir() for k in DIRS})
    row["requires"] = " ".join(f"{n}>={v}" for n, v in requires(d))
    row["seeds"] = " ".join(f"{t}->{p}" for t, p in seeds(d))
    return row

def installed_version(repo: Path, name: str) -> str:
    """The version of `name` present in `repo`: the core's `dyad/VERSION` (or the instance's record) for
    dyad-operator, else `crafts/<name>/VERSION`; '' when absent."""
    repo = Path(repo)
    if name == CORE_NAME:
        for f in (repo / "dyad" / "VERSION", dyadlib.instance(repo) / "d-work" / "VERSION"):
            if f.exists():
                return f.read_text().strip()
        return ""
    return version(repo / "crafts" / name)

def unmet(repo: Path, craft_dir: Path) -> list[str]:
    """Requirements `repo` does not satisfy, as text; empty when all are met."""
    out = []
    for name, ver in requires(craft_dir):
        have = installed_version(repo, name)
        if not have:
            out.append(f"requires {name}>={ver}: not installed")
        elif not SEMVER.fullmatch(have) or semver(have) < semver(ver):
            out.append(f"requires {name}>={ver}: found {have}")
    return out

def _floor_pkg(repo: Path, tag: str) -> Path | None:
    """The whole `dyad/` tree as it stood at `tag`, extracted into a scratch root (`git archive`
    piped through the stdlib `tarfile`, no new World dependency, Rule-14 property 2's kernel-only
    path): a craft's guard and projector modules call their own `dyadlib.load_guard`/`load_module`
    at import time to resolve sibling files, so a bare `dyadlib.py` alone made every one of them
    fail to *load* against the floor rather than testing its invariants — noise, not signal. `None`
    when the tag holds no `dyad/` (should not happen for a real release; named, not guessed at)."""
    archive = subprocess.run(["git", "archive", tag, "--", "dyad"], cwd=repo, capture_output=True)
    if archive.returncode != 0 or not archive.stdout:
        return None
    tmp = Path(tempfile.mkdtemp(prefix="dyad-floor-"))
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tf:
        tf.extractall(tmp, filter="data")
    pkg = tmp / "dyad"
    return pkg if (pkg / "scripts" / "dyadlib.py").is_file() else None

_FLOOR_SCRIPT = """\
import importlib.util, sys
from pathlib import Path
sys.dont_write_bytecode = True
scripts = Path({scripts!r})
sys.path.insert(0, str(scripts))

def _load(stem, path):
    if stem in sys.modules:
        return sys.modules[stem]
    spec = importlib.util.spec_from_file_location(stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[stem] = mod
    spec.loader.exec_module(mod)
    return mod

# Pre-seed every core script the floor tag ships, dyadlib first, so a plain `import <name>`
# anywhere below -- the target file, or anything it transitively imports -- finds the floor's own
# module through the sys.modules cache and never falls through to sys.path, where the target's
# own `sys.path.insert(0, .../dyad/scripts)` (its real, on-disk location -- crafts/ is never
# archived here, only dyad/) would otherwise put the *live* tree first and silently defeat the
# whole floor check (caught mechanically: a craft's own floor check kept passing at every version
# tried, including one confirmed by direct inspection to lack a symbol the craft's own invariant
# needs -- the check was always running against live code, never the floor's).
_load("dyadlib", str(scripts / "dyadlib.py"))
for _p in sorted(scripts.glob("*.py")):
    if _p.stem != "dyadlib":
        try:
            _load(_p.stem, str(_p))
        except Exception:
            pass   # a script that cannot load stand-alone at this floor is not this check's target

spec = importlib.util.spec_from_file_location("__floor_target__", {path!r})
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print("LOAD_ERROR", repr(e)); sys.exit(0)
for n, pred in getattr(mod, "INVARIANTS", []):
    try:
        ok = bool(pred())
    except Exception:
        ok = False
    print("INV", n, ok)
"""

def _check_invariants_against_floor(py: Path, floor_pkg: Path) -> tuple[str | None, list[tuple[str, bool]]]:
    """(load error or None, [(invariant name, holds)]) for `py`'s own `INVARIANTS`, run in a fresh
    subprocess whose `sys.path` is rooted at the floor's own `dyad/scripts` — so every import `py`
    makes, direct (`import dyadlib`) or transitive (a craft guard's own plain `import runbook`, the
    core's run-book module), resolves against the floor tag's real code, never something already
    cached in this process and bound to the live one. An in-process `sys.modules['dyadlib']` swap,
    tried first, only protects the one name swapped: `crafts/sysadmin/guards/runbooks.py` does
    `import runbook as _rb`, a second core module with its own `import dyadlib` — already cached
    live from this process's own earlier, unrelated invariant pass (`package.py`'s own
    `invariant_modules()` loads it before any craft check runs) — so the swap left `_rb.CLASSES`
    bound to the live `dyadlib.HOST_CLASSES` while the freshly-loaded `runbooks.py` compared it
    against the floor's, failing every floor check for that file regardless of whether the floor
    actually held (caught mechanically, D1 catching its own bug, before this PR was opened)."""
    script = _FLOOR_SCRIPT.format(scripts=str(floor_pkg / "scripts"), path=str(py))
    r = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=60)
    error, results = None, []
    for line in r.stdout.splitlines():
        if line.startswith("LOAD_ERROR "):
            error = line[len("LOAD_ERROR "):]
        elif line.startswith("INV "):
            _, inv_name, ok = line.split(" ", 2)
            results.append((inv_name, ok == "True"))
    if error is None and not results and r.returncode != 0:
        error = (r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f"exit {r.returncode}")
    return error, results

def floor_problems(repo: Path, craft_dir: Path, pkg: Path = dyadlib.PKG) -> list[str]:
    """D1 (#100): for each `requires: dyad-operator>=X` whose tag `dyad-operator-vX` resolves
    locally, re-run the craft's own guard and projector `INVARIANTS` against that tag's
    `dyad/scripts/dyadlib.py` instead of the live one — the craft's own already-declared facts,
    checked against the floor it actually claims. Refuted in the original report: deriving the
    floor from a hand-maintained "feature added in version N" table just recreates the bug (a
    second table to drift); this is the one check that can't drift from what the craft actually
    needs. A false invariant fails; no local tag, or the blob absent there, is one skip line each —
    the drift guard's own pattern (#91)."""
    repo, d = Path(repo), Path(craft_dir); name = d.name; msgs = []
    files = []
    for sub in ("guards", "projectors"):
        p = d / sub
        if p.is_dir():
            files += sorted(f for f in p.glob("*.py") if not f.name.startswith("_"))
    for req_name, ver in requires(d):
        if req_name != CORE_NAME:
            continue
        tag = f"{req_name}-v{ver}"
        rp = subprocess.run(["git", "rev-parse", "-q", "--verify", f"{tag}^{{commit}}"], cwd=repo, capture_output=True, text=True)
        if rp.returncode != 0:
            msgs.append(f"warning: {name}: floor {req_name}>={ver}: no tag {tag} here (not yet released, or tags not fetched)")
            continue
        floor_pkg = _floor_pkg(repo, tag)
        if floor_pkg is None:
            msgs.append(f"warning: {name}: floor {req_name}>={ver}: {tag}:dyad/ not found")
            continue
        for py in files:
            error, results = _check_invariants_against_floor(py, floor_pkg)
            if error is not None:
                msgs.append(f"crafts/{name}/{py.parent.name}/{py.name}: does not load against floor {req_name}>={ver}: {error}")
                continue
            for inv_name, ok in results:
                if not ok:
                    msgs.append(f"crafts/{name}/{py.parent.name}/{py.name}: floor {req_name}>={ver}: {inv_name} is false against {ver} — raise the floor")
    return msgs

def check_craft(repo: Path, craft_dir: Path, pkg: Path = dyadlib.PKG, others=()) -> list[str]:
    """One craft: bare lines fail, `warning:` lines warn. `repo` is the tree the craft sits in (the repo, or a
    staged export); `others` are the other craft roots present (shared-word warning)."""
    repo, d = Path(repo), Path(craft_dir); name = d.name; rel = f"crafts/{name}"; msgs = []; own_corpora = set()
    v = version(d)
    if not v:
        msgs.append(f"{rel}/VERSION: missing")
    elif not SEMVER.fullmatch(v) or len(Path(d / "VERSION").read_text().strip().splitlines()) != 1:
        msgs.append(f"{rel}/VERSION: '{v}' is not one MAJOR.MINOR.PATCH line")
    m = manifest(d)
    if m.get("name", name) != name:
        msgs.append(f"{rel}/MANIFEST.md: name '{m['name']}' is not the directory name '{name}'")
    msgs += distribute.instance_state(repo, [rel], package_rules(pkg, repo), names=data()["name"], what="a craft", tracked=False)
    voc = dyadlib.load_guard("agent", "vocabulary", pkg)
    msgs += voc.check_craft(pkg, d)
    mine = voc.craft_terms(d)
    for o in others:
        shared = sorted(mine & voc.craft_terms(o))
        if shared:
            msgs.append(f"warning: {rel}: terms also defined by crafts/{Path(o).name} ({', '.join(shared)}) — namespaced `<craft>:term`, a legibility finding")
    mine_seeds = {p for _, p in seeds(d)}
    for o in others:
        shared = sorted(mine_seeds & {p for _, p in seeds(o)})
        if shared:
            msgs.append(f"warning: {rel}: seed destination(s) also declared by crafts/{Path(o).name} ({', '.join(shared)}) — first Operator to copy wins, nothing is written by install")
    zones, containment = None, None
    for py in sorted((d / "guards").glob("*.py")) if (d / "guards").is_dir() else []:
        if py.name.startswith("_"):
            continue
        try:
            mod = dyadlib.load_module(py, f"dyad_crafts_{name}_{py.stem}")
        except Exception as e:
            msgs.append(f"{rel}/guards/{py.name}: does not load: {e}"); continue
        if zones is None:
            try:
                containment = dyadlib.load_guard("infra", "containment", pkg)
                zones = containment.corpora(repo)   # zones plus the logical host corpus (#175)
            except Exception:
                zones = None
        problem = dyadlib.contract_problem(mod, "craft", name, zones)
        if problem:
            msgs.append(f"{rel}/guards/{py.name}: {problem}")
        elif getattr(mod, "CORPUS", None):
            own_corpora.add(mod.CORPUS)
    if seeds(d) and containment is None:
        try:
            containment = dyadlib.load_guard("infra", "containment", pkg)
        except Exception:
            containment = None
    for tmpl, dest in seeds(d, repo):
        if not (d / "templates" / tmpl).is_file():
            msgs.append(f"{rel}/MANIFEST.md: seeds '{tmpl}->{dest}': no templates/{tmpl}")
        elif containment is None:
            msgs.append(f"{rel}/MANIFEST.md: seeds '{tmpl}->{dest}': cannot classify (infra/containment guard unavailable)")
        elif containment.classify(dest, repo) not in {containment.corpus_zone(c, repo) for c in own_corpora}:
            msgs.append(f"{rel}/MANIFEST.md: seeds '{tmpl}->{dest}': destination zone '{containment.classify(dest, repo)}' is not one this craft's own guards claim as CORPUS ({', '.join(sorted(own_corpora)) or 'none'})")
    if (d / "rules").is_dir():
        msgs += dyadlib.load_guard("agent", "rules", pkg).check_tended(d / "rules", data()["agent-token"], rel_to=repo)
    msgs += [f"warning: {rel}: {u} (checked at install)" for u in unmet(repo, d)]
    msgs += floor_problems(repo, d, pkg)
    return msgs

def seed_status(repo: Path, craft_dir: Path) -> list[str]:
    """`warning:` lines for this craft's declared seeds whose destination is absent in `repo` — the
    *real* repo/instance being examined, always given explicitly (never `check_craft`'s own `repo`,
    which during `craft install`'s pre-flight call is the staged source, not the destination; the
    same distinction `unmet(repo, craft_dir)` already draws). Existence only, never copies (Rule-11
    p2); points at the manual step (`dyad craft check`, and after `dyad craft install`, #180)."""
    repo, d = Path(repo), Path(craft_dir); rel = f"crafts/{d.name}"
    return [f"warning: {rel}: seed '{tmpl}' not copied to {dest} — copy it by hand: "
            f"cp {rel}/templates/{tmpl} {dest}"
            for tmpl, dest in seeds(d, repo) if not (repo / dest).exists()]

def crafts(root: Path) -> list[Path]:
    """Every `crafts/<name>/` directory of `root` (a VERSION or not: a directory beside REGISTRY.md is a craft)."""
    c = Path(root) / "crafts"
    return sorted(p for p in c.iterdir() if p.is_dir()) if c.is_dir() else []

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = Path(root or dyadlib.repo_root())
    all_ = crafts(root)
    return [m for d in all_ for m in check_craft(root, d, pkg, others=[o for o in all_ if o != d]) + seed_status(root, d)]

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(crafts(Path(root or dyadlib.repo_root())))} craft(s)"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ds = crafts(root); ex = parse(ds[0]) if ds else {}
    kinds = {"name": ("text", "the directory name"), "version": ("text", "MAJOR.MINOR.PATCH"), "requires": ("text", "`<craft>>=<semver>` list, from MANIFEST.md; may be empty"),
             "seeds": ("text", "`<template>-><instance path>` list, from MANIFEST.md; may be empty; each destination zone must be one this craft's own guards claim")}
    optional = ("requires", "seeds")
    return {"store": "crafts/<craft>/ (VERSION, MANIFEST.md optional)", "parser": "`crafts.parse`", "observed": len(ds),
            "note": "no instance state inside; vocabulary namespaced; guards meet the contract; Agent-process tokens warn (Rule-4)",
            "fields": [(k, kinds.get(k, ("bool", "directory present"))[0], kinds.get(k, ("bool", "directory present"))[1], k not in optional, str(ex.get(k, "")), "crafts.FIELDS") for k in FIELDS]}

def main(a=None):
    a = sys.argv[1:] if a is None else a
    root = dyadlib.repo_root()
    ds = crafts(root)
    if a:
        ds = [d for d in ds if d.name in a]
        if not ds:
            print(f"no craft {' '.join(a)} under crafts/", file=sys.stderr); return 2
    rc = 0
    for d in ds:
        msgs = check_craft(root, d, others=[o for o in crafts(root) if o != d]) + seed_status(root, d)
        for m in msgs:
            if m.startswith("warning:"): print(f"warn [craft] {m.removeprefix('warning:').strip()}")
        fails = [m for m in msgs if not m.startswith("warning:")]
        for f in fails: print(f"FAIL [craft] {f}", file=sys.stderr)
        if fails: rc = 1
        else: print(f"ok   [craft] crafts/{d.name} {version(d)}")
    return rc

if __name__ == "__main__":
    sys.exit(main())
