# Tended rules of the sysarch craft

Operator-tended rules of the system-architecture craft: how the dyad's infrastructure is shaped,
as opposed to how the process runs. Any form. They are not Agent Rules (Rule-4 classifies): no
block, no coherence sweep, no Agent-vocabulary discipline; their terms are `../vocabulary/CRAFT.md`.
Each opens with one line naming the core Rule whose kernel reads it (or, for a rule with no kernel,
the retired Rule it replaces); the kernel binds the process, the craft rule the design (#160, D1).
The System Architecture set of Agent Rules (`Set: System Architecture`) is this directory since
#160; Rule-5 says so under its `## Sets`.

| rule | read by | what it holds |
|------|---------|---------------|
| `distribution.md` | Rule-11 | what is craft and what is instance; craft-relative paths and `DYAD_INSTANCE`; the archive shape and the version seed; the entrypoint shape |
| `guards.md` | Rules 12 and 21 (retired) | the guard layout, one guard per entity, apart from instances; the guard contract in full; the registry discovered and printed; the CLI kept; a check chosen mechanical wherever it can be |
| `manifest.md` | Rule-14 | one manifest of six cells at the package root; library rows replaceable, each naming its replacement; The World observed, never pinned |
| `projection.md` | Rule-17 (retired) | parsed data is the source; a projector is craft code with a check; self-contained, deterministic output; the registry discovered by the core runner |
| `references.md` | Rule-20 | one register, one resolver per kind, existence and nothing more; surface and guard share the data; the craft-contributed register as design; the leaf entities |
| `stores.md` | Rule-16 | the file-per-instance `key: value` store pattern: rendered view untracked, ids `max(origin, local)+1`, no hand edits, append-only fence, phase-ordered edits |

Implementation clauses of Rules 11, 12, 13 and 14 (#161's table: scripted install, generated files,
test mapping, token map, import criteria) are the syseng craft's since #162 (`../../syseng/rules/`);
Rule-17's p3 and p5, written into `projection.md` by #160, were lifted to
`crafts/syseng/rules/determinism.md` by #162 (the one double move, plan #160 attack 7).
