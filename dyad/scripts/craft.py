#!/usr/bin/env python3
"""Tended-craft CLI (Rule-11 property 5, #156): `dyad craft <verb>`, dispatched by package.py. One distribution
code path with the core craft's build/install: scripts/distribute.py. Kernel: Python 3.12+.

  dyad craft new <name>                    scaffold crafts/<name>/ (VERSION 0.1.0, README, rules/, vocabulary/CRAFT.md,
                                           templates/, guards/, docs/, falsification/rules/) so `dyad craft check <name>`
                                           passes; refuses an existing directory (the craft play-book's first step, #165)
  dyad craft list                          every crafts/<craft>/ with its VERSION and origin — `authored`
                                           (no registry row) or `installed <sha256[:8]>` — and the core craft
  dyad craft check [<craft>]               the craft guard (guards/craft/crafts.py) for one or every craft
  dyad craft export <craft> [out.tar.gz]   deterministic archive of crafts/<craft>/ (entries `crafts/<craft>/…`),
                                           default <craft>-<version>.tar.gz; a failing craft is not exported
  dyad craft install <src> [--force] [--dwork N] [--craft <name>] [--source <text>]
                                           <src>: an archive, a `…/crafts/<name>` directory, or a repo root with
                                           --craft. Checks the source craft, its `requires:`, and refuses a
                                           locally modified or authored tree unless --force; then installs
                                           (prune: the tree is the craft's) and writes its crafts/REGISTRY.md row.
                                           Writes nothing else: no hooks, no import line, no git config. If the
                                           installed craft's MANIFEST.md declares `seeds:` (#180) and a seed's
                                           destination is absent, prints a reminder naming the `cp` to run by
                                           hand — advisory only, never copied (Rule-11 p2: host-side hooks are
                                           the core craft's only).
"""
import re, shutil, sys, tempfile
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, distribute

REGISTRY = "crafts/REGISTRY.md"
REGISTRY_FIELDS = ("craft", "version", "source", "sha256", "d-work")
REGISTRY_HEAD = ("# Craft registry (instance state in the craft zone, Rule-11 property 2; #156)\n\n"
                 "One row per *installed* Tended craft, written by `dyad craft install`, never by hand. A craft authored\n"
                 "in this system has no row (`dyad craft list` shows it as `authored`). `sha256` is `distribute.archive_sha256`\n"
                 "of the installed tree — the proof it is unmodified; `source` is where the archive came from (a `world`\n"
                 "reference); `d-work` the installing d-work. No date: a second install of the same version changes nothing.\n\n"
                 "| craft | version | source | sha256 | d-work |\n|-------|---------|--------|--------|--------|\n")

INVARIANTS = [("registry-fields-distinct", lambda: len(set(REGISTRY_FIELDS)) == len(REGISTRY_FIELDS)),
              ("registry-head-names-fields", lambda: REGISTRY_HEAD.rstrip().splitlines()[-2] == "| " + " | ".join(REGISTRY_FIELDS) + " |")]   # crafts/syseng/rules/invariants.md

def guard():
    return dyadlib.load_guard("craft", "crafts", PKG)

def registry_rows(repo: Path) -> dict[str, dict[str, str]]:
    f = Path(repo) / REGISTRY
    if not f.exists():
        return {}
    ts = dyadlib.tables(f.read_text())
    if not ts or tuple(ts[0][0]) != REGISTRY_FIELDS:
        return {}
    return {r[0]: dict(zip(REGISTRY_FIELDS, r)) for r in ts[0][1] if len(r) == len(REGISTRY_FIELDS)}

def write_registry(repo: Path, rows: dict[str, dict[str, str]]) -> None:
    body = "".join("| " + " | ".join(r[k] for k in REGISTRY_FIELDS) + " |\n" for _, r in sorted(rows.items()))
    (Path(repo) / REGISTRY).write_text(REGISTRY_HEAD + body)

def tree_sha(repo: Path, name: str) -> str:
    """The identity of the tree on disk (tracked or not: an install is not yet committed)."""
    return distribute.archive_sha256(repo, [f"crafts/{name}"], tracked=False)

def cmd_list(repo: Path) -> int:
    g = guard(); rows = registry_rows(repo)
    core = (repo / "dyad" / "VERSION")
    print(f"{'craft':<16} {'version':<10} origin")
    if core.exists():
        print(f"{g.CORE_NAME:<16} {core.read_text().strip():<10} core (dyad/)")
    for d in g.crafts(repo):
        row = rows.get(d.name)
        origin = f"installed {row['sha256'][:8]}" + ("" if row["sha256"] == tree_sha(repo, d.name) else " (modified)") if row else "authored"
        print(f"{d.name:<16} {g.version(d) or '?':<10} {origin}")
    return 0

SCAFFOLD_VERSION = "0.1.0"
_NAME = re.compile(r"^[a-z][a-z0-9-]*$")

def scaffold(name: str) -> dict[str, str]:
    """The files of a new craft (relative to crafts/<name>/): the shape guards/craft/crafts.py checks, each directory
    holding a README so git tracks it. Every file is package text (no instance state, Rule-11 p1)."""
    h = f"crafts/{name}/"
    return {
        "VERSION": f"{SCAFFOLD_VERSION}\n",
        "README.md": f"# {name} — a Tended craft (`{h}`, zone `craft`)\n\nWhat this craft practises, in one paragraph. Scaffolded by `dyad craft new {name}` "
                     f"(the craft play-book, `dyad/playbooks/craft-instantiation.md`); version `VERSION` ({SCAFFOLD_VERSION}).\n\n"
                     "| path | holds |\n|------|-------|\n| `rules/` | the craft's Tended Rules (any form; no Rule-4 block) and their index `README.md` |\n"
                     "| `vocabulary/CRAFT.md` | the craft's terms (`term | definition | rule`; never an Agent term) |\n| `templates/` | seeds the craft's commands copy into an instance |\n"
                     "| `guards/` | `<entity>.py` guards meeting the contract (`dyad check --list` shows them as `" + name + "/<entity>`) |\n"
                     "| `docs/` | generic procedures (no host values) |\n| `falsification/rules/` | one record per craft rule |\n",
        "rules/README.md": f"# Tended Rules of the {name} craft\n\nOne file per rule, any form; each opens with the core Rule whose kernel reads it, if any.\n\n| rule | read by | what it holds |\n|------|---------|---------------|\n",
        "vocabulary/CRAFT.md": f"# {name} craft vocabulary (Tended terms)\n\nOne row per term; `rule` names the craft rule (`../rules/<rule>.md`) that owns it. A craft term is referenced,\nnever defined, by the Agent vocabulary (Rule-6).\n\n| term | definition | rule |\n|------|------------|------|\n",
        "templates/README.md": f"# {name} templates\n\nSeeds an instance copies (exempt from the instance-state scan).\n",
        "guards/README.md": f"# {name} guards\n\nOne `<entity>.py` per entity kind, meeting the guard contract (Rule-21); its test at `../tests/guards/test_<entity>.py`.\n",
        "docs/README.md": f"# {name} docs\n\nGeneric procedures of the craft; host values stay in the instance.\n",
        "falsification/rules/README.md": f"# {name} falsification records\n\nOne record per craft rule (Rule-9 form: attack, result, survivor).\n",
    }

def cmd_new(repo: Path, a) -> int:
    if not a or not _NAME.match(a[0]):
        print("usage: dyad craft new <name>   (name: [a-z][a-z0-9-]*)", file=sys.stderr); return 2
    name = a[0]; d = repo / "crafts" / name
    if d.exists():
        print(f"refused: crafts/{name} exists; not overwritten", file=sys.stderr); return 2
    if name == guard().CORE_NAME:
        print(f"refused: {name} is the core craft's name", file=sys.stderr); return 2
    files = scaffold(name)
    for rel, text in files.items():
        f = d / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    print(f"scaffolded crafts/{name} {SCAFFOLD_VERSION}: {len(files)} files; next `dyad craft check {name}`")
    return 0

def cmd_check(repo: Path, a) -> int:
    return guard().main(a)

def cmd_export(repo: Path, a) -> int:
    if not a:
        print(__doc__, file=sys.stderr); return 2
    g = guard(); name = a[0]; d = repo / "crafts" / name
    if not d.is_dir():
        print(f"no craft crafts/{name}", file=sys.stderr); return 2
    msgs = g.check_craft(repo, d, PKG, others=[o for o in g.crafts(repo) if o != d])
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in fails: print(f"FAIL [craft] {m}", file=sys.stderr)
    if fails:
        print(f"refused: crafts/{name} fails its check; not exported", file=sys.stderr); return 1
    out = Path(a[1]) if len(a) > 1 else Path(f"{name}-{g.version(d)}.tar.gz")
    distribute.build(repo, [f"crafts/{name}"], out)
    print(f"exported crafts/{name} {g.version(d)} -> {out} (sha256 {tree_sha(repo, name)[:8]})")
    return 0

def stage(src: Path, craft: str | None, tmp: Path) -> Path:
    """The source as a tree root holding exactly one `crafts/<name>/`: an archive extracted, a `…/crafts/<name>`
    directory copied under `tmp/crafts/`, or a repo root with --craft used as it is (its other crafts ignored)."""
    src = Path(src)
    if src.is_file():
        return distribute.extract(src, tmp)
    if not src.is_dir():
        raise FileNotFoundError(f"no such source {src}")
    if craft:
        if not (src / "crafts" / craft).is_dir():
            raise FileNotFoundError(f"{src} has no crafts/{craft}")
        return src
    if not (src / "VERSION").exists():
        raise ValueError(f"{src} is not a craft (no VERSION); a repo root needs --craft <name>")
    shutil.copytree(src, tmp / "crafts" / src.name, ignore=shutil.ignore_patterns("__pycache__"))
    return tmp

def cmd_install(repo: Path, a) -> int:
    if not a:
        print(__doc__, file=sys.stderr); return 2
    g = guard()
    opt = lambda k: a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else None
    force, dwork, craft, source = "--force" in a, opt("--dwork"), opt("--craft"), opt("--source")
    src = Path(a[0])
    tmp = Path(tempfile.mkdtemp(prefix="dyad-craft-"))
    try:
        try:
            root = stage(src, craft, tmp)
        except (FileNotFoundError, ValueError) as e:
            print(f"refused: {e}", file=sys.stderr); return 2
        names = [d.name for d in g.crafts(root)] if not craft else [craft]
        if len(names) != 1:
            print(f"refused: {src} holds {len(names)} crafts ({', '.join(names)}); one per install", file=sys.stderr); return 2
        name = names[0]; sd = root / "crafts" / name; ver = g.version(sd)
        msgs = g.check_craft(root, sd, PKG, others=[o for o in g.crafts(repo) if o.name != name])
        fails = [m for m in msgs if not m.startswith("warning:")]
        for m in fails: print(f"FAIL [craft] {m}", file=sys.stderr)
        if fails:
            print(f"refused: crafts/{name} fails its check; not installed", file=sys.stderr); return 1
        missing = g.unmet(repo, sd)
        if missing:
            for m in missing: print(f"FAIL [craft] crafts/{name}: {m}", file=sys.stderr)
            print(f"refused: crafts/{name} {ver}: requirements unmet in {repo}; install them first (never fetched)", file=sys.stderr); return 1
        rows = registry_rows(repo); dest = repo / "crafts" / name
        if dest.is_dir() and not force:
            row = rows.get(name)
            if row is None or row["sha256"] != tree_sha(repo, name):
                print(f"refused: crafts/{name} is locally modified or authored here; `--force` overwrites, or export it first", file=sys.stderr); return 1
        changed = distribute.install(root, repo, [f"crafts/{name}"], prune=True, hooks=None)
        new = {"craft": name, "version": ver, "source": source or src.name, "sha256": tree_sha(repo, name), "d-work": f"#{dwork}" if dwork else (rows.get(name, {}).get("d-work", ""))}
        if rows.get(name) != new:
            rows[name] = new; write_registry(repo, rows); changed += 1
        print(f"installed crafts/{name} {ver}: {changed} changes")
        for m in g.seed_status(repo, dest):   # advisory only; never written here (Rule-11 p2, #180)
            print(f"warn [craft] {m.removeprefix('warning:').strip()}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main(a=None) -> int:
    a = sys.argv[1:] if a is None else list(a)
    repo = dyadlib.repo_root()
    if not a or a[0] not in ("new", "list", "check", "export", "install"):
        print(__doc__, file=sys.stderr); return 2
    return {"new": lambda: cmd_new(repo, a[1:]), "list": lambda: cmd_list(repo), "check": lambda: cmd_check(repo, a[1:]), "export": lambda: cmd_export(repo, a[1:]),
            "install": lambda: cmd_install(repo, a[1:])}[a[0]]()

if __name__ == "__main__":
    sys.exit(main())
