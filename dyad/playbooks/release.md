# Play-book: release (when a change set warrants a release, and which number; core craft, `dyad-operator`; #493)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the agent follows for a
recurring decision; its steps are a run-book. This one decides two things for the unit that ships crafts (the
distribute unit under `organization: m4`): whether the change set accumulated since a craft's last release warrants
a release now, and which number that release takes. It exists because the operator refused a release that could
not say why it was one: "release should have clear threshold criteria, e.g. a critical bug fix, a significant
enhancement to an existing capability, a new capability, etc." (#489, plan #493). Steps: `dyad/runbooks/release.md`,
run through `dyad runbook run release <step>`, the core runner. Nothing here redefines a Rule. That a release is the
operator's to ratify, and how — under the release gate by the release d-work's own done-`Y` behind a fence,
authenticated by the hosting approval; with the gate off by the single `Y/N: release <tag>?` or the batch
`Y/N: release <tag-a>, <tag-b>?` for tags one d-work's own done-`Y` verified — is Rule-11's
(`dyad/rules/RULE-11-distribution-structure.md`, Ratification events). This play-book says which shape the unit's
reply takes in each case (Evidence, below). That a tag equals its craft's `VERSION`, and
the drift guard that forces a `VERSION` bump after a tag, are Rule-11 property 4's. The bundle is property 7's.
Publishing a ratified release is the `released` service's (`dyad release`, its run-book `released.md`; #461, #470).
The unit proposes; the operator disposes (Rule-2).

## Parameter
`CRAFT` (`dyad-operator` for the core, a Tended craft's name, or `bundle`) and `CLASS` (below), read by the `number`
step from the environment. No default for either: a number for the wrong craft or class is worse than none.

## Trigger
A d-work whose done-`Y` lands a change under a craft's root (`dyad/` or `crafts/<craft>/`). The unit runs `changes`,
classifies every d-work the list names since that craft's last tag, and takes the change set's class, the highest of
them (Classes, below). If that class releases, the unit proposes the release to the home. If it does not, the change
set waits. The operator may also ask for a release at any time; the classes still say which number it takes.

## Classes
Five classes. Three release, one breaks, one waits. Each is inference, but inference against stated evidence: a
class the unit cannot evidence is the class below it.

| class | `CLASS` | what counts | evidence the unit cites | number | release |
|---|---|---|---|---|---|
| critical fix | `critical-fix` | a defect that gives an installing system a wrong result it can act on (a wrong disposition, a ratification or merge path broken, an install or a release refused, a fence that passes what it must refuse), loses or leaks data, or turns its CI red | the incident row, the red run or a reproduction; the fixing PR and its done-`Y` | patch | yes, as soon as the fix lands |
| new capability | `capability` | something an installing system can do that it could not: a new verb or flag, a new guard or check, a new craft, a new Rule property | the d-work and PR, and the help text, the guard's registry line or the Rule sentence that names it | minor | yes, with the change set |
| significant enhancement | `enhancement` | an existing capability changed in what it does or decides for an installing system: a new mode of a verb, a check that now catches more, a path materially faster or cheaper in how a unit works | the d-work and PR, and a before/after observation (a timing, a line that now appears) | minor | yes, with the change set |
| breaking | `breaking` | an installing system must change something on upgrade: a verb or a file format removed or renamed, a Rule that now refuses what it allowed, an install contract changed; combines with the classes above | the changed contract and its upgrade step (`dyad/playbooks/port.md`) | major; minor while the major is 0, the question marking it **breaking** | yes, never without the upgrade step |
| maintenance | `maintenance` | nothing an installing system would notice: Rule wording with no behaviour change, records, docs, tests, internal refactors, an ordinary fix with no wrong result outside this repo | none | none (the drift guard's working bump only) | no: the change set waits for the next class that releases |

The order, highest first: breaking, then critical fix, new capability and significant enhancement, then maintenance.
A change set holding a critical fix and a new capability takes the minor number; the critical fix is why it is asked
now.

## Numbers
- **`VERSION` follows the class at release time, not the drift guard.** Between releases the first change under a
  craft's root after its tag bumps `VERSION` by a patch, because the drift guard (Rule-11 property 4) requires it to
  differ from the tag. That working number is not a release. The PR that prepares a release sets `VERSION` to the number
  the change set's class implies (`number`), and the tag equals it.
- **The order that keeps the bundle guard green.** `VERSION` (the craft's zone) and the bundle row (`BUNDLE.md`,
  infra) never move in one PR (Rule-1). Rule-11 property 7 lets a released craft's `VERSION` run ahead of its row
  only while the row still names that craft's **last release**. So: (1) the craft-zone or agent-zone PR sets `VERSION`
  to the class's number while the row names the last release; (2) the infra-zone PR moves the row to that number with
  the bundle's own version; (3) the cut is that merge. A row that names an unreleased number (#522 put 0.12.3 there)
  no longer pins `VERSION`: a later bump past it warns until the infra-zone PR moves the row, and fails once the new
  number is tagged (Rule-11 property 7, #481).
- **The bundle takes the highest class among its components** since the bundle's last tag, and moves the same part.
  A release of the core or of a Tended craft always also proposes the bundle that names it (Rule-11 property 7: the
  bundle is the front door), in the same PR that moves its row.
- **Below 1.0.0** a breaking change is a minor bump, as semver allows for a 0 major. Calling 1.0.0 is the operator's
  decision, never this play-book's.

## Steps
- `changes`: every craft's commits and cited d-works since its last tag, and the bundle's last tag.
- `number`: the tag `CLASS` implies for `CRAFT`.

Under the release gate (`RELEASE_APPROVAL=tap`, #545) the release runs in this order, each step the act of the party
named:
1. **Plan** (unit proposes, operator disposes): the release d-work's plan names every tag and its number, by class.
2. **Done** (operator): the Done question names the PR whose merge is the cut and every tag it releases; the reply
   carries the Evidence below. The `Y` is recorded before the merge (Rule-3).
3. **Merge** (unit, clerical): `dyad merge` of the cut PR.
4. **Fence and release-ready** (unit, clerical): after the merge, the fence is checked per tag — the released craft's
   root at the cut equals that root at the head the done-`Y` names, and the archive built at the cut has the sha256
   the evidence cited — and only then a release-ready entry is written per tag, `dyad release ready <row> <tag> --at <cut> --archive
   <sha256>`, which checks that fence itself and refuses on a mismatch, then landed by the usual ledger-only commit.
   A tag whose fence fails gets no entry: it returns to the chat question, with the difference stated.
5. **Approval** (operator, on the hosting): the publishing run the entries start waits for the operator's approval;
   a rejection or a timeout publishes nothing.
6. **Record** (home, clerical): once the run has completed, one `Y release <tag> at <cut> (archive <sha256>)` entry per
   tag, its provenance entry noted `by reference` with the body `run <id> approved by <login> at <time>` (Rule-7
   property 4).
   When neither the run's status nor its jobs can be read, nothing is recorded and the gap is said.
With the gate off, steps 4 to 6 are replaced by the chat release question (Evidence, below) and its recorded `Y`.

## Evidence
**Under the release gate the evidence goes into the Done reply, and no release question follows it.** The Done
reply holds everything listed below — classes, d-works, numbers, the cut PR's head and the sha256 each archive will
have at the cut — and its last line is the Done question naming the cut PR and the tags:

    Y/N: Done with #<id> <title> (merges PR #a, releases dyad-operator-v0.13.0, v0.17.0)?

After the merge the unit reports the fence's result per tag and the publishing run's link; that report carries no
`Y/N`, because the decision was the done-`Y` and the approval on the hosting is its authentication. Rule-2's Binding
still holds: the `Y` covers exactly the tags the question named.

**With the gate off: one question per d-work, not per tag.** When the tags come from one d-work's done-`Y`, the unit asks them as one
question in Rule-11's batch form; the usual case is a bundle plus the components it releases. The unit asks single
questions only for tags of different d-works. The release reply holds the evidence the batch line rests on, before
that line:
- for each tag, its class, each d-work that meets the class (one line each, with its evidence, as the Classes table
  names it) and the number the class implies;
- for the bundle, the component classes it takes the highest of;
- the cut, and each archive's sha256 at the cut (#478: one unit build per archive).

Its last line is Rule-11's batch form, naming the bundle last:

    dyad-operator-v0.13.0: class new capability (#474 dyad bootstrap; #476 check --evidence --brief/--show; #493 release play-book), significant enhancement (#475 parallel suite; #465 trace fence), critical fix (#475)
    v0.17.0: class new capability, the highest of its components (dyad-operator 0.13.0; cabinet, sysadmin, sysarch, syseng unchanged)
    cut ba7c47b; dyad-0.13.0.tar.gz 8a0572cd…b9a9; BUNDLE.sha256 b9060eb2…96e8
    Y/N: release dyad-operator-v0.13.0, v0.17.0?

One `Y` is recorded as one `Y release <tag> at <cut> (archive <sha256>)` entry per named tag, all in one ledger commit,
so `released` publishes them in one run. Each entry's provenance text is the same `Y`, as Rule-3's batch writes one `Y`
into every named row. Anything but `Y` releases none of the named tags (Rule-2, Binding).

A release question that names no class, or a class it cannot evidence, is not asked.
