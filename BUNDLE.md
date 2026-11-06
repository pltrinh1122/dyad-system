# Bundle manifest (Rule-11 property 7)

The whole distribution this repo authors, at pinned versions: one row per craft in the tree — the
core craft (`dyad-operator`) plus every Tended craft. Checked both directions by
`dyad/guards/infra/bundle.py`: every row's version equal to that craft's live `VERSION`, every craft
in the tree has a row and every row names a craft in the tree. Built by `dyad bundle build [dir]`
(the one distribution code path, `dyad build` / `dyad craft export` per row — no second mechanism),
released as the unprefixed tag `vMAJOR.MINOR.PATCH` = `v` + the version below. A system that wants
only some components pins them individually by their own crafts' tags (`dyad-operator-vX.Y.Z`,
`<craft>-vX.Y.Z`) instead of this file.

## Known limitations (1.0.0)

The twice-daily health sweep (`.github/workflows/dyad-sweep.yml`) depends on GitHub Actions' `schedule` event, which this release has not fully verified. Observed runs arrived about 5 to 7 hours after their slots, and missed slots were not made up. Push-triggered corroboration and the evidence gate do not depend on the schedule. A fix is planned for 1.x.

version: 1.0.0

| component | version |
|-----------|---------|
| dyad-operator | 1.0.0 |
| sysarch | 0.4.0 |
| syseng | 0.7.0 |
| sysadmin | 0.3.2 |
| cabinet | 0.5.1 |
| chronicle | 0.3.0 |

`disclosure` is in the tree and deliberately absent from the table: the Operator disposed that it is
not meant for release yet and is held until ready (d-work #232). Rule-11 property 7 permits an
unreleased craft to have no row, and `dyad bundle build` builds once per row, so nothing here publishes
it. The `not yet bundled` warning the guard prints for it describes that decision, not an unfinished
chore. Its first release adds its row.
