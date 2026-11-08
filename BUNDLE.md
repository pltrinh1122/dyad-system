# Bundle manifest (Rule-11 property 7)

The whole distribution this repo authors, at pinned versions: one row per craft in the tree — the
core craft (`dyad-operator`) plus every Tended craft. Checked both directions by
`dyad/guards/infra/bundle.py`: every row's version equal to that craft's live `VERSION`, every craft
in the tree has a row and every row names a craft in the tree. Built by `dyad bundle build [dir]`
(the one distribution code path, `dyad build` / `dyad craft export` per row — no second mechanism),
released as the unprefixed tag `vMAJOR.MINOR.PATCH` = `v` + the version below. A system that wants
only some components pins them individually by their own crafts' tags (`dyad-operator-vX.Y.Z`,
`<craft>-vX.Y.Z`) instead of this file.

## Release notes (1.1.0)

- **Intent reading (#615).** Under the new preference `intent-reading: on`, a prompt that opens a row is first
  answered by an intent reading. Each portion of the prompt is classed against the candidates `dyad dwork intent`
  prints. The reading is asked as `Y/N: intent aligned for #<id> <title>?` before any plan, and a bare `N` archives
  the row. The preference ships `off`.
- **Release timing (#616).** A decision criterion, `dyad/dmc/release-timing.jsonld`, says when a critical fix is
  released: fix first, cut now, fold into a minor, or hold.
- **The automaton sweep (#617).** The twice-daily scheduled sweep is gone, and with it 1.0.0's known limitation. The
  full sweep runs after each landed merge, and `dyad automaton sweep --stores` runs the whole-store guards after each
  ledger push. What waits on time, such as heads not landed, is read by the home in `dyad board resume`.
- **Check triggers (#618).** A decision criterion, `check-trigger`, maps each sweep check to the activity that changes
  what it reads. A test fails a check that no trigger runs.
- **The audit report (#619).** `dyad automaton sweep` with no `--row` prints the audit's coded checks as one report,
  with `checks-sha256` and `report-sha256`. The audit play-books read it instead of running those checks again. The
  home's read also reports a sweep that was not delivered.
- **Fix (#621).** After a release's cut, a ledger-only or events-only push no longer waits for the release tag. In
  1.0.0 the pre-push gate refused them, the release-ready lines included, until the tag existed.

## Known limitations (1.1.0)

- Between a release's cut and its tag, a push that changes code, and `dyad check --evidence`, are refused for the
  missing core tag. Both pass once the publishing run, after the operator's approval, has made the tag.
- The automaton's board flip after a recorded plan answer can overwrite a newer board entry. Rewrite the entry with
  `dyad board set` after the flip.
- The stores sweep can tell a standing warning as new when it carries a count that grows with the ledger. It costs
  one extra notice; nothing fails.
- The sweep's mirror check does not run: `dyad-sweep.yml` sets no `MIRROR`, so a mirror branch behind `main` is not
  reported.
- The GitHub Release's text is a fixed one-line template. These notes are in `BUNDLE.md`.
- Under `intent-reading: on`, the intent reading's plan file needs a `Base commit:` line before it is pushed. The
  plans guard refuses a plan file without one.
- The `released` health reads each Release from the hosting without a token, and can report "not read" under the
  hosting's rate limit.

version: 1.2.0

| component | version |
|-----------|---------|
| dyad-operator | 1.2.0 |
| sysarch | 0.4.0 |
| syseng | 0.8.0 |
| sysadmin | 0.3.2 |
| cabinet | 0.6.0 |
| chronicle | 0.3.0 |

`disclosure` is in the tree and deliberately absent from the table: the Operator disposed that it is
not meant for release yet and is held until ready (d-work #232). Rule-11 property 7 permits an
unreleased craft to have no row, and `dyad bundle build` builds once per row, so nothing here publishes
it. The `not yet bundled` warning the guard prints for it describes that decision, not an unfinished
chore. Its first release adds its row.
