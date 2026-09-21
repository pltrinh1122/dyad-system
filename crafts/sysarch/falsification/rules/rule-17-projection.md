# Falsification record — Rule-17 (projection), Architecture Rule 5 (ledger #120)

**Claim (operator, 2026-09-13):** the architecture must be shaped so that every viewing surface
(ERD, sequence flow, block diagram, …) is produced mechanically from corpus data by package code,
never hand-drawn, and reliably (same corpus → same surface); a working ERD projector is the
evidence.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Diagrams need a layout engine; importing one breaks kernel-only (Rule-14) and adds a Rule-13 row. | Refuted | Observed: `project_erd.py` is 255 lines of stdlib (`html`, `re`, `dataclasses`, `pathlib`); the layout is one column per entity kind (fixed `KINDS` order), entities sorted, fixed box geometry, cubic edges. `package.py check` Rule-14: 0 new tokens; no import row. |
| 2 | An ERD of markdown files is a stretch — there is no schema. | Refuted | Every entity is a parsed model the guards already run on: `dyadlib.Row`, `vocabulary.parse` tuples, `infrastructure.parse_manifest` rows, `containment.ZONES`, `rule_files` + the Rule-4 block. Observed live: 261 entities, 329 edges, 11 kinds. One shape gap found: `refs` cells also name PRs (`PRs #65 #66`), which a bare-`#N` read would misfile as rows; `parse_refs` skips segments that start with `PR`, tested. |
| 3 | Self-contained HTML forbids mermaid, the obvious tool. | Survives, scoped | Mermaid is a script from The World; inline SVG needs none (the test asserts no `http(s)://` beyond the SVG namespace). A later projector may target the harness's native mermaid fence if the Operator declares that surface (a Rule-14 row). |
| 4 | A generated, untracked file is invisible in the repo; the Operator cannot review it. | Survives, scoped | Re-runnable in one command (`package.py project erd`) from any commit; viewed via the artifact surface; committing it would make every PR a diff of SVG (Rule-11 property 6; `generated: projections/*` refuses a tracked one — `test_tracked_projection_refused`). |
| 5 | Sequence and block diagrams need events and calls, which no parser yields; Rule-17 promises what it cannot deliver. | Survives, scoped | Rule-17 fixes the projector contract (properties 1–5); this d-work delivers ERD only; each further surface is its own d-work that adds its parser (owned by the data's Rule) and registers a projector. |
| 6 | Determinism fails on dict ordering, timestamps, or a version banner. | Confirmed | No timestamp or version in the output; every iteration sorted (`by_kind`, edges by `(src, dst, label)`); `test_render_deterministic_and_escaped` and the live test compare two renders byte for byte; two live runs observed with the same md5. |
| 7 | `package.py project` grows the runner into a semantics owner (S4). | Refuted | Observed: `cmd_project` is 12 lines — `--list` prints `PROJECTORS`, else `importlib` loads the module and returns its `main()`; every model and rendering decision is in `project_erd.py`. |

Observation (not an attack on the Rule): the vocabulary term `surface` also occurs in Rule-14
("governs its surface") and in the term *System Infrastructure*, in the sense of a boundary. The
check passes (used-by lists only 17); the sense difference is inference, noted for the next sweep.

## Rule-5 pairwise statements (Rule-17 added)
- 17–11: Rule-11 owns package layout and property 6 (generated); Rule-17 places its files there
  and adds one data line. 17–12: Rule-12 requires the check; Rule-17 says what a projector's check
  covers (fixture, live, determinism). 17–13: no import; Rule-13 unchanged. 17–14: no World
  dependency; a hosted surface would be a Rule-14 row, not Rule-17's. 17–6: three terms, defined
  once. 17–3: rows and plans are read, never written; the d-work lifecycle is untouched.
  17–15/16: stores read only. 17–4: block conforms (`rule_integrity.py`: intent 1, target 1,
  boundaries 5, conditions 4). 17–1: agent-zone files only; `.gitignore` is a separate infra PR.
  17–2, 17–8, 17–9, 17–10: no ratification event, no host action, this record, framing as
  in the plan. Coherent, orthogonal.

## Rule-6: three terms added (`projection`, `projector`, `surface`), owner 17.

Disposition: see ledger #120.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
p1 names the guards' parsers (`manifest.parse_manifest`, each guard's `FIELDS` and `describe`); the entities projector builds its cards from the registry (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
Rule-17 retired; this record travels with its text to `crafts/sysarch/rules/projection.md` (records travel with the
rules they falsify, #153 attack 7). Origin commit of the core copy: 616f506. p2's path is now
`crafts/<craft>/projectors/project_<surface>.py` + `crafts/<craft>/tests/test_project_<surface>.py`; p4's registry is
discovered by the core runner over `crafts/*/projectors/` (a surface in two crafts fails; no craft: one line and exit 2);
p3 and p5 are implementation and lift to `crafts/syseng/` on #162 (the one double move, plan #160 attack 7). The
events surface lives in the sysadmin craft (plan #160 D5, attack 6). Attacks 1–7 hold as written. Disposition: see ledger #160.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
p3 (self-contained, generated, never committed) and p5 (determinism) lifted to `crafts/syseng/rules/determinism.md`; p3 here
keeps the viewing sentence and cites the craft, p5 is a pointer. The projectors' twice-render tests stay (p2). Every projector
now declares `INVARIANTS` (`project_erd.KINDS` distinct, `project_schema.LABELS`/`LAYERS` distinct, `project_entities.RELATIONS`
equal to the register, `project_events.COLUMNS` ⊆ `EVENT_FIELDS`) and the entities surface shows an invariants column.
Disposition: see ledger #162.

## Amendment — d-work #100 (2026-09-20, D3: craft/surface, one collision check)

**Finding (#99, then #100's downstream report):** a bare surface name is the only craft-owned
namespace of this repo not qualified by craft (guards are `<craft>/<entity>`, craft vocabulary is
`<craft>:term`), and the "one craft per surface" refusal it needs was implemented *twice*, from two
independent sources: the core runner's own registry (`package.projectors()`) and this craft's guard
(`registry.py`, re-globbing `crafts/*/projectors/`). Fixing one side's keying alone did not silence
the other's failure — verified before attempting the narrower fix.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Qualifying the key (`craft/surface`) just moves the collision to the CLI: two crafts still fight over the bare `dyad project <surface>` invocation. | Confirmed, scoped | The registry itself is collision-free; the CLI's bare-name resolution degrades gracefully — unique, it resolves; ambiguous, it lists the qualified candidates and exits 2, never silently picking one. |
| 2 | This is the same shape as `dyad check --list`'s `<group>/<entity>` keying — reusing it is not a new falsification, just an application. | Confirmed | No new pattern introduced; `check_projectors`'s own collision loop is deleted outright rather than re-justified. |
| 3 | Two independent "one craft per surface" checks (core registry, `registry.py`) is itself the bug, not the keying — collapsing to one derivation matters more than qualifying the key. | Confirmed | `registry.py`'s `projectors()` now calls `dyadlib.projector_files` (the shared, parameterized discovery primitive `package.projectors()` also uses) instead of re-globbing the tree independently; its own collision check is deleted, not re-derived a second way. |

p4 rewritten: a registry keyed `craft/surface`, collision-free by construction; `dyad project
--list` prints `<craft/surface> <path>`.

Disposition: see ledger #100.

## Amendment — d-work #104 (2026-09-20, --list format is a compatibility surface)

**Finding (workstation-252):** the D3 rekey above changed `dyad project --list`'s output from one
column to two; a downstream craft (workstation's own `surfacer`) parsed the old shape and broke.
Fixed on their own side; no dyad-system defect (the change was #100's ratified survivor, already
documented) — surfaced only because p4 named the format without naming who else reads it.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Naming it a compatibility surface with no guard behind the claim is unenforceable prose. | Survives, scoped | Inference-only by design, matching every other property in this rule's "Inference, stated" section (whether a surface is legible, whether a projector hand-draws); the sentence's job is to change what a future *falsification* of a `--list` format change must weigh, not to add a mechanical check. |

p4 gains one sentence: the `--list` line is a compatibility surface for tooling outside this repo;
a further change to its columns or separator is falsified with that cost in view.

Disposition: see ledger #104.
