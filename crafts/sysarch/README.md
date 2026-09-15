# sysarch — the system-architecture craft (Tended craft, `crafts/sysarch/`, zone `craft`)

The engineering practice that built this dyad's core: its entities and their relations, the
contract every guard meets, the manifest's form, the projection surfaces, the store patterns and
the release shape — as one contained, versioned, exportable tree (Rule-11: a Tended craft; Rule-1:
zone `craft`). Extracted from Agent Rules 11, 12, 14, 16, 17, 20 and 21 by d-work #160 (plan
`agent-corpus/d-work/plans/160.md`; the classification table of #158, narrowed by #161). The core
craft `dyad-operator` (`dyad/`) keeps only the *kernel* sentences of those Rules — the ones Rule-2's
Binding and Rule-3's completion evidence rely on — and each kernel cites the craft rule it reads by
path. Rules 17 and 21 had no kernel and moved whole; their numbers are retired, never reused.
Version: `VERSION` (0.1.0).

Who imports this craft: any system that *changes* a craft — the core included. A system that only
runs the process needs the core alone; `dyad project` then prints one line naming this craft.

| path | holds |
|------|-------|
| `rules/` | six Tended rules — `distribution.md` (Rule-11), `guards.md` (Rules 12 and 21), `manifest.md` (Rule-14), `projection.md` (Rule-17), `references.md` (Rule-20), `stores.md` (Rule-16) — and their index `README.md` |
| `vocabulary/CRAFT.md` | the craft's terms (seven rows moved from the Agent vocabulary; referenced there, never defined) |
| `templates/` | `guard.py` (the guard contract as a skeleton), `project_surface.py` (a projector skeleton: collect, render, main; deterministic), `entity-card.md` (the fields a guard's `describe` yields) |
| `projectors/` | `project_erd.py`, `project_schema.py`, `project_entities.py`, `project_kanban.py` (#186) — discovered by the core runner (`dyad project --list`) as `<surface> sysarch`; each imports `dyad/scripts/dyadlib.py` and the guards' parsers and declares `INVARIANTS` (syseng `invariants.md`); the entities surface carries an invariants column per card (#162); kanban groups the d-work store by ledger state, no parser of its own |
| `tests/` | `test_project_<surface>.py` per projector, `guards/test_registry.py` for the guard; run by `dyad check` (Rule-12 mapping for crafts) |
| `guards/registry.py` | the craft's one guard (entity `projector`, `CORPUS = "craft"`): every `crafts/*/projectors/project_<surface>.py` has its test and a `main`; no surface is provided twice; every core guard's entity is a source or target in the reference register or a listed leaf (`rules/references.md`) |
| `falsification/rules/` | the records of Rules 17 and 21, moved with the rules they falsify (records travel with their rules, #153), each with one amendment naming #160 |

## Bootstrap order
A change to the core is made with this craft present: install the core, import sysarch, edit,
release the core. The core runs its guards on its own code; this craft's rules *describe* the
contract that code enforces (a compiler built with itself). The craft's own guard checks the
craft's artifacts, not the core's.

## What stays in the core craft
Every guard that runs every session and every data file those guards read (`dyad/guards/**`,
`package_rules.txt`, `manifest_rules.txt`, `INFRASTRUCTURE.md`); `dyadlib.py` (paths, rows, the
guard loader and the one contract definition `CONTRACT`); the runner `package.py` (the guard
registry, `check_rule_12`, projector discovery, the invariant pass, `dyad ledger|dwork|craft|runbook`); the ledger store
itself (`rows.py`). The implementation clauses of Rules 11, 12, 13 and 14 (#161's table) are the
syseng craft's since #162 (`../syseng/`); its `determinism.md` holds what `projection.md` p3/p5 held.

## Importing this craft into another dyad system
`dyad craft export sysarch` here, `dyad craft install sysarch-0.1.0.tar.gz` there (core first). The
projectors then appear in `dyad project --list`; `dyad check --list` shows `sysarch/registry`.
Nothing under this tree names a host.
