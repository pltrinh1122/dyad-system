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
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib, distribute

ENTITY, CORPUS, TRANSACTION = "craft", "craft", False
NAME, OWNER = "craft", "Rule-11"
DIRS = ("rules", "vocabulary", "templates", "guards", "docs", "falsification")
FIELDS = ("name", "version", *DIRS, "requires", "seeds")
INVARIANTS = [("dirs-distinct", lambda: len(set(DIRS)) == len(DIRS)),   # crafts/syseng/rules/invariants.md
              ("fields-cover-dirs", lambda: set(DIRS) <= set(FIELDS) and FIELDS[:2] == ("name", "version"))]
SEMVER = re.compile(r"\d+\.\d+\.\d+")
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

def semver(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.strip().split("."))

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

def seeds(craft_dir: Path) -> list[tuple[str, str]]:
    """[(template name, instance-relative dest)] from `seeds: CHANGELOG.md->workstation-corpus/CHANGELOG.md
    ...` (MANIFEST.md, space-separated `<template>-><dest>` tokens, the same shape as `requires:`);
    absent manifest = none. Never copied (Rule-11 p2: host-side hooks are the core craft's only) —
    `check_craft` validates the mapping (template exists, destination zone is one this craft's own
    guards claim) and `seed_status` reports an absent destination in a named repo; #180."""
    out = []
    for tok in manifest(craft_dir).get("seeds", "").split():
        tmpl, sep, dest = tok.partition("->")
        if sep and tmpl and dest:
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
                zones = {z for z, _ in containment.ZONES}
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
    for tmpl, dest in seeds(d):
        if not (d / "templates" / tmpl).is_file():
            msgs.append(f"{rel}/MANIFEST.md: seeds '{tmpl}->{dest}': no templates/{tmpl}")
        elif containment is None:
            msgs.append(f"{rel}/MANIFEST.md: seeds '{tmpl}->{dest}': cannot classify (infra/containment guard unavailable)")
        elif containment.classify(dest) not in own_corpora:
            msgs.append(f"{rel}/MANIFEST.md: seeds '{tmpl}->{dest}': destination zone '{containment.classify(dest)}' is not one this craft's own guards claim as CORPUS ({', '.join(sorted(own_corpora)) or 'none'})")
    if (d / "rules").is_dir():
        msgs += dyadlib.load_guard("agent", "rules", pkg).check_tended(d / "rules", data()["agent-token"], rel_to=repo)
    msgs += [f"warning: {rel}: {u} (checked at install)" for u in unmet(repo, d)]
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
            for tmpl, dest in seeds(d) if not (repo / dest).exists()]

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
