# sysarch craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`)
and by `dyad craft install`. `requires:` names the minimum version of another craft this one
depends on; `dyad craft install` refuses to install this craft when a requirement is unmet
(`crafts.unmet`), and `dyad craft check` warns the same finding, labelled "checked at install".

Rules 11, 12, 14, 16 and 20 (`dyad/rules/`) cite `crafts/sysarch/rules/*.md` paths by backtick
(d-work #160); the reference guard (`dyad/guards/agent/references.py`) skips those citations,
never fails them, while no `crafts/` tree is installed (`Corpus.crafts_absent`) — so a core-only
install is not blocked by the citations themselves. What a core alone cannot do is run `dyad craft
install` at all: the verb is code this craft's kernel depends on and ships only inside the core
craft (`dyad/scripts/craft.py`), added by the same d-work that added these citations. `requires:`
below guards the narrower case a missing verb does not: a core new enough to run `dyad craft
install` (#160 landed) but older than `dyad/VERSION` actually reached when this craft last
verified against it — `dyad/VERSION` was not bumped at #160 itself (it moved 0.1.0 -> 0.2.0 only
at #162), so `0.1.0` cannot distinguish core before #160 from core just after it; `0.2.0` is the
first recorded version guaranteed to postdate #160 (#178, d-work #178's empirical replay).

D1 (#100): `0.2.0` was the verb-availability floor above, never checked against what this craft's
own code actually reads from `dyadlib`. `project_kanban.py`'s `columns-are-states` invariant
(`set(COLUMNS) == dyadlib.STATES`) needs `archived`, which entered `dyadlib.STATES` at `0.6.0`
(d-work #37) — a floor a craft can now hand nothing but its own already-declared `INVARIANTS`
to verify, mechanically, against the tag's real code (`crafts.floor_problems`, no second
hand-maintained "feature added in version N" table to drift from this one). D1 itself then caught
a second, higher floor this same d-work introduces: `project_entities.py`'s `RELATIONS` now calls
`references.craft_references_contrib`, which exists only from `dyad-operator` `0.8.0` on (this
d-work's own core PR) — raised here rather than left for D1 to fail against once that release
exists to check against.

#175: raised to `0.10.0` — this craft's projectors now read `dyadlib.host_path` and
`manifest.manifest_rows` (the host path and the union manifest), both first shipped in `0.10.0`.

name: sysarch
requires: dyad-operator>=0.10.0
