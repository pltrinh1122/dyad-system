# Bundle manifest (Rule-11 property 7)

The whole distribution this repo authors, at pinned versions: one row per craft in the tree — the
core craft (`dyad-operator`) plus every Tended craft. Checked both directions by
`dyad/guards/infra/bundle.py`: every row's version equal to that craft's live `VERSION`, every craft
in the tree has a row and every row names a craft in the tree. Built by `dyad bundle build [dir]`
(the one distribution code path, `dyad build` / `dyad craft export` per row — no second mechanism),
released as the unprefixed tag `vMAJOR.MINOR.PATCH` = `v` + the version below. A system that wants
only some components pins them individually by their own crafts' tags (`dyad-operator-vX.Y.Z`,
`<craft>-vX.Y.Z`) instead of this file.

version: 0.12.1

| component | version |
|-----------|---------|
| dyad-operator | 0.10.1 |
| sysarch | 0.3.0 |
| syseng | 0.4.0 |
| sysadmin | 0.2.1 |

`countersign` and `disclosure` are in the tree and deliberately absent from the table: the Operator
disposed that they are not meant for release yet and are held until ready (d-work #232). Rule-11
property 7 permits an unreleased craft to have no row, and `dyad bundle build` builds once per row,
so nothing here publishes them. The two `not yet bundled` warnings the guard prints for them describe
that decision, not an unfinished chore. Their first release adds their rows.
