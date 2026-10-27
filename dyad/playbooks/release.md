# Play-book: release (when a change set warrants a release, and which number; core craft, `dyad-operator`; #493)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision; its steps are a run-book. This one decides two things for the seat that ships crafts (the
distribute seat under `organization: m4`): whether the change set accumulated since a craft's last release warrants
a release now, and which number that release takes. It exists because the Operator refused a release that could
not say why it was one: "release should have clear threshold criteria, e.g. a critical bug fix, a significant
enhancement to an existing capability, a new capability, etc." (#489, plan #493). Steps: `dyad/runbooks/release.md`,
run through `dyad runbook run release <step>`, the core runner. Nothing here redefines a Rule. That a release is the
Operator's to ratify, and its two forms, the single `Y/N: release <tag>?` and the batch `Y/N: release <tag-a>, <tag-b>?`
for tags one d-work's own Done-`Y` verified, are Rule-11's (`dyad/rules/RULE-11-distribution-structure.md`, Ratification
events). This play-book makes the batch its default (Evidence, below). That a tag equals its craft's `VERSION`, and
the drift guard that forces a `VERSION` bump after a tag, are Rule-11 property 4's. The bundle is property 7's.
Publishing a ratified release is the `released` service's (`dyad release`, its run-book `released.md`; #461, #470).
The seat proposes; the Operator disposes (Rule-2).

## Parameter
`CRAFT` (`dyad-operator` for the core, a Tended craft's name, or `bundle`) and `CLASS` (below), read by the `number`
step from the environment. No default for either: a number for the wrong craft or class is worse than none.

## Trigger
A d-work whose Done-`Y` lands a change under a craft's root (`dyad/` or `crafts/<craft>/`). The seat runs `changes`,
classifies every d-work the list names since that craft's last tag, and takes the change set's class, the highest of
them (Classes, below). If that class releases, the seat proposes the release to the cos. If it does not, the change
set waits. The Operator may also ask for a release at any time; the classes still say which number it takes.

## Classes
Five classes. Three release, one breaks, one waits. Each is inference, but inference against stated evidence: a
class the seat cannot evidence is the class below it.

| class | `CLASS` | what counts | evidence the seat cites | number | release |
|---|---|---|---|---|---|
| critical fix | `critical-fix` | a defect that gives an installing system a wrong result it can act on (a wrong disposition, a ratification or merge path broken, an install or a release refused, a fence that passes what it must refuse), loses or leaks data, or turns its CI red | the incident row, the red run or a reproduction; the fixing PR and its Done-`Y` | patch | yes, as soon as the fix lands |
| new capability | `capability` | something an installing system can do that it could not: a new verb or flag, a new guard or check, a new craft, a new Rule property | the d-work and PR, and the help text, the guard's registry line or the Rule sentence that names it | minor | yes, with the change set |
| significant enhancement | `enhancement` | an existing capability changed in what it does or decides for an installing system: a new mode of a verb, a check that now catches more, a path materially faster or cheaper in how a seat works | the d-work and PR, and a before/after observation (a timing, a line that now appears) | minor | yes, with the change set |
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
  pins `VERSION` until the row goes back to the last release or the number is released.
- **The bundle takes the highest class among its components** since the bundle's last tag, and moves the same part.
  A release of the core or of a Tended craft always also proposes the bundle that names it (Rule-11 property 7: the
  bundle is the front door), in the same PR that moves its row.
- **Below 1.0.0** a breaking change is a minor bump, as semver allows for a 0 major. Calling 1.0.0 is the Operator's
  decision, never this play-book's.

## Steps
- `changes`: every craft's commits and cited d-works since its last tag, and the bundle's last tag.
- `number`: the tag `CLASS` implies for `CRAFT`.

## Evidence
**One question per d-work, not per tag.** When the tags come from one d-work's Done-`Y`, the seat asks them as one
question in Rule-11's batch form; the usual case is a bundle plus the components it releases. The seat asks single
questions only for tags of different d-works. The release reply holds the evidence the batch line rests on, before
that line:
- for each tag, its class, each d-work that meets the class (one line each, with its evidence, as the Classes table
  names it) and the number the class implies;
- for the bundle, the component classes it takes the highest of;
- the cut, and each archive's sha256 at the cut (#478: one seat build per archive).

Its last line is Rule-11's batch form, naming the bundle last:

    dyad-operator-v0.13.0: class new capability (#474 dyad bootstrap; #476 check --evidence --brief/--show; #493 release play-book), significant enhancement (#475 parallel suite; #465 trace fence), critical fix (#475)
    v0.17.0: class new capability, the highest of its components (dyad-operator 0.13.0; cabinet, sysadmin, sysarch, syseng unchanged)
    cut ba7c47b; dyad-0.13.0.tar.gz 8a0572cd…b9a9; BUNDLE.sha256 b9060eb2…96e8
    Y/N: release dyad-operator-v0.13.0, v0.17.0?

One `Y` is recorded as one `Y release <tag> at <cut> (archive <sha256>)` entry per named tag, all in one ledger commit,
so `released` publishes them in one run. Each entry's provenance text is the same `Y`, as Rule-3's batch writes one `Y`
into every named row. Anything but `Y` releases none of the named tags (Rule-2, Binding).

A release question that names no class, or a class it cannot evidence, is not asked.
