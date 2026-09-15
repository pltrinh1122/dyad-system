# Projection (sysarch craft, Tended rule)

Replaces Rule-17 (projection, #120; retired by d-work #160, its text moved here whole). No core
kernel: what the process relies on — that projector code carries a check which runs on every push —
is Rule-12's kernel, and the core runner's `check_rule_12` discovers a craft's projector tests. A
Tended rule — any form, no Rule-4 block, no sweep. Terms (`projection`, `projector`, `surface`):
`crafts/sysarch/vocabulary/CRAFT.md`. Skeleton: `crafts/sysarch/templates/project_surface.py`.
Guard: `crafts/sysarch/guards/registry.py` (registry label `sysarch/registry`).

## Intent
Project the corpus onto every viewing surface mechanically, from parsed data, by craft code with
a check.

## Properties
1. **Parsed data is the source.** A projection is produced from corpus data that core or craft
   code already parses (`dyadlib.rule_files` / `read_rows`, and the guards' parsers —
   `vocabulary.parse`, `manifest.parse_manifest`, `containment.ZONES`, each guard's `FIELDS` and
   `describe`, `guards.md`). A projector consumes the parser the data's owning Rule provides; it
   never hand-draws an entity or an edge. The entities surface's relations are the reference
   register (`references.md`), never a table of its own.
2. **A projector is craft code with a check.** `crafts/<craft>/projectors/project_<surface>.py`
   carries `crafts/<craft>/tests/test_project_<surface>.py` (Rule-12): tests over fixture data,
   plus a live run over the instance that must produce valid output. A projector lives in the
   craft whose data it renders (the events surface is the sysadmin craft's, #160 D5); this rule is
   the discipline every craft's projector follows.
3. **Output form: the syseng craft's.** Self-contained, generated, never committed, byte-identical
   on the same corpus state — `crafts/syseng/rules/determinism.md` (properties 1–3; lifted from
   here by #162). The Operator views a projection by opening the file or through the harness's
   artifact surface.
4. **A registry, discovered.** The core runner discovers `crafts/*/projectors/project_<surface>.py`
   (sorted by craft, then surface); `dyad project <surface>` loads the module and calls its
   `main`, `dyad project --list` prints `<surface> <craft> <path>`. A surface provided by two
   crafts is a failing registry. Without any craft providing projectors the runner prints one line
   naming the install (`dyad craft install crafts/sysarch`) and exits 2. Every data model and every
   rendering decision lives in the projector (#71 S4).
5. *(Determinism: `crafts/syseng/rules/determinism.md` property 3; the twice-render test stays in
   every projector's test, property 2.)*

## When
- The Operator requests a surface: a projector is registered and run, never hand-drawn.
- A parser's data shape changes: the projector that consumes it adapts in the same d-work.
- Every push and PR: the projector tests run through `check_rule_12` (`dyad check`), one suite per
  installed craft.
- `dyad project <surface>` is invoked: the projection is (re)written under `<instance>/projections/`.

## Inference, stated
Whether a surface is legible, and whether a projector hand-draws, is inference at falsification
time.
