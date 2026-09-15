# Determinism (syseng craft, Tended rule)

Read by Rule-11's kernel (`dyad/rules/RULE-11-distribution-structure.md`, the one-line p6 stub:
generated files are never tracked; data `package_rules.txt`, check `check_generated`) and by the
sysarch craft's `crafts/sysarch/rules/projection.md` (p3 and p5 lifted here by d-work #162 — the one
double move, plan #160 attack 7). Terms (`deterministic`, `generated file` — the latter arriving
from the core vocabulary): `../vocabulary/CRAFT.md`. No guard of its own: `check_generated`
(Rule-11's runner), the projector tests' twice-render, and `test_package`'s twice-run of the evidence
block are the checks.

## Properties
1. **Generated files are never committed.** *"A generated file — one produced by running the
   package (bytecode, caches, rendered views) — is not tracked; `package.py check` refuses any
   tracked path matching a generated pattern; the list is data (`package_rules.txt`, `generated:`
   entries, ledger #108)."* (Rule-11 p6 as cut.) Ownership of the data and the check stays where
   the code runs (Rule-11); what counts as generated and why it is never tracked is this rule's.
2. **Self-contained output.** *"One HTML file with inline CSS, JS and SVG; no external script,
   stylesheet or CDN … Written under `<instance>/projections/`, which `package_rules.txt` lists as
   `generated` (Rule-11 property 6)."* (projection.md p3 as lifted.)
3. **Byte-identical output.** *"The same corpus state yields byte-identical output: no timestamps,
   no version banners, every iteration sorted. The tests assert it by rendering twice."*
   (projection.md p5 as lifted.) The same discipline governs the evidence block: no timing in the
   Rule-12 summary line (#138), every registry and invariant list sorted, so two runs on one head
   print one sha256.
4. **Builds are deterministic.** Two builds of one tree are byte-identical (entries sorted, mtime
   0, no owner, gzip header mtime 0), so an archive's sha256 identifies a tree (Rule-11 p5, the
   distribution path `distribute.py`).

## Inference, stated
Whether an iteration is sorted *everywhere* is checked only where a test renders twice; a new
projector inherits the check by its template (`crafts/sysarch/templates/project_surface.py`).
