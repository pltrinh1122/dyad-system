# Bundle manifest (Rule-11 property 7)

The whole distribution this repo authors, at pinned versions: one row per craft in the tree — the
core craft (`dyad-operator`) plus every Tended craft. Checked both directions by
`dyad/guards/infra/bundle.py`: every row's version equal to that craft's live `VERSION`, every craft
in the tree has a row and every row names a craft in the tree. Built by `dyad bundle build [dir]`
(the one distribution code path, `dyad build` / `dyad craft export` per row — no second mechanism),
released as the unprefixed tag `vMAJOR.MINOR.PATCH` = `v` + the version below. A system that wants
only some components pins them individually by their own crafts' tags (`dyad-operator-vX.Y.Z`,
`<craft>-vX.Y.Z`) instead of this file.

## Release notes (1.2.0)

- **Row slugs (#622).** Under the preference `dwork-slug: on` (shipped `on`), a row id is shown as `#<id>-<slug>`, with
  two or three tags after the number. Stored references stay the bare number.
- **Backlog grooming (#625).** A play-book, `dyad/playbooks/backlog-groom.md`, grooms the whole backlog in one pass:
  hygiene, retirement, sizing, promotion and a forward release plan. Its one command is `dyad board groom`.
- **Decision criteria in records (#626, #641).** Play-books and run-books cite their criteria as `dmc:<id>`
  records. 15 core records once judged by inference are now decided by code, and their tests pin every outcome.
- **Internal realization (#643).** Rule-3's execution detail admits three changes whose effect stays inside a PR:
  placement, implied means and compatible extension.
- **Precedent (#642, #644, #645).** A decision kind, `precedent`, is decided by code from past rulings the operator
  admitted, and abstains when unsure. The decision log (`<instance>/d-work/decisions/`) and the precedent question,
  `Y/N: admit as precedents …?`, admit them. The play-book `precedent-bootstrap` and `dyad precedent
  prompt|score|gate|agreement` fill an upgrading instance's store from its own ledger, with the admission check run
  before the question.
- **Awaiting you (#646).** Every reply's closing line counts the questions the operator has been asked and not
  answered, in a d-work group and a merge group, by the record `dmc:disposition-request`. `dyad board` generates it.
  The preference is `awaiting-you: on|off`, and an absent key reads `on`.
- **cabinet 0.6.0 (#620, #640).** Session tidy ships as the craft's play-book, run-book and script. The unit-lifecycle
  criterion counts dyad units.
- **syseng 0.8.0 (#640).** The naming guard admits a craft's `playbooks/` and `runbooks/`.

## Known limitations (1.2.0)

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
