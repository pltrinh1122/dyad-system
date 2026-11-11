# Bundle manifest (Rule-11 property 7)

The whole distribution this repo authors, at pinned versions: one row per craft in the tree — the
core craft (`dyad-operator`) plus every Tended craft. Checked both directions by
`dyad/guards/infra/bundle.py`: every row's version equal to that craft's live `VERSION`, every craft
in the tree has a row and every row names a craft in the tree. Built by `dyad bundle build [dir]`
(the one distribution code path, `dyad build` / `dyad craft export` per row — no second mechanism),
released as the unprefixed tag `vMAJOR.MINOR.PATCH` = `v` + the version below. A system that wants
only some components pins them individually by their own crafts' tags (`dyad-operator-vX.Y.Z`,
`<craft>-vX.Y.Z`) instead of this file.

## Release notes (1.3.0)

- **Precedent capture (#648).** At every Done, `dyad board draft` lists the row's candidate rulings and the Done record
  writes those the operator admits (`board draft --decisions-out`, `board advance --decisions`).
- **Precedent scope (#649).** `dmc:precedent-scope` decides which outcomes a precedent may settle, by the cost of a
  wrong match; each outcome carries a `dyad:effect`, and admit, decide, the gate and prompt read it.
- **Incident fences (#651).** The sweep finds incidents a reply promised and the log does not hold, and `board draft`
  lists a row's; the audit's Phase 3b reads them.
- **Done clauses (#659, #661).** The Done template carries the retires and releases clauses, and a done-Y's head must
  be the full 40-hex sha.
- **Bundling (#663).** `dmc:bundled-craft` judges a craft's purpose from its own tree, never an instance's content.
- **Coming (#665).** The closing line's Coming part is its own preference, `coming: on|off`, absent reading `on`.
- **Awaiting you (#670).** A question asked in another dyad unit's chat is listed with that unit.
- **cabinet 0.7.0 (#669).** Unit and session tidy, one play-book, run-book and record, with `tidy.py` classing each
  unit and counting sessions outside the system.
- **chronicle 0.4.0 (#650, #668, #671, #674).** The keyed form: a piece published as fiction declaring no truth, its key
  beside it, checked by the guard. Records for a product-marketing pitch, a lean-canvas review and problem depth.
- **sysadmin 0.3.3 (#649).** `changelog-actor` declares its outcomes' effects.

## Known limitations (1.3.0)

- Between a release's cut and its tag, a push that changes code, and `dyad check --evidence`, are refused for the
  missing core tag. Both pass once the publishing run, after the operator's approval, has made the tag.
- The automaton's board flip after a recorded plan answer can overwrite a newer board entry. Rewrite the entry with
  `dyad board set` after the flip.
- The stores sweep can tell a standing warning as new when it carries a count that grows with the ledger. It costs
  one extra notice; nothing fails.
- The sweep's mirror check does not run: `dyad-sweep.yml` sets no `MIRROR`.
- The GitHub Release's text is a fixed one-line template. These notes are in `BUNDLE.md`.
- Under `intent-reading: on`, the intent reading's plan file needs a `Base commit:` line before it is pushed. The
  plans guard refuses a plan file without one.
- The `released` health reads each Release from the hosting without a token, and can report "not read" under the
  hosting's rate limit.
- `dyad precedent prompt` sends no record whose outcomes are an operator's acts, so such records gain no precedents.
  `agreement` measures sets under 20 cases at max_df 0.5, and no record yet carries a bar, so none converts.
- An instance whose preference table predates 1.2.0 gets a warning that `awaiting-you` has no row, until its table
  is next edited. Its absent key reads `on` either way.

version: 1.3.0

| component | version |
|-----------|---------|
| dyad-operator | 1.3.0 |
| sysarch | 0.4.0 |
| syseng | 0.8.0 |
| sysadmin | 0.3.3 |
| cabinet | 0.7.0 |
| chronicle | 0.4.0 |

`disclosure` is in the tree and deliberately absent from the table: the Operator disposed that it is
not meant for release yet and is held until ready (d-work #232). Rule-11 property 7 permits an
unreleased craft to have no row, and `dyad bundle build` builds once per row, so nothing here publishes
it. The `not yet bundled` warning the guard prints for it describes that decision, not an unfinished
chore. Its first release adds its row.
