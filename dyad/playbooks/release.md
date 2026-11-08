# Play-book: release (when a change set warrants a release, and which number; core craft, `dyad-operator`; #493)

A play-book (vocabulary, Rule-3) for the unit that ships crafts (distribute, under `organization: m4`). It decides
whether the change set since a craft's last tag releases now, and at which number. Its steps are
`dyad/runbooks/release.md`, run by `dyad runbook run release <step>`. Rule-11 owns the release's ratification
(`dyad/rules/RULE-11-distribution-structure.md`, Ratification events, `Y/N: release <tag>?`) and the drift guard
(property 4). Publishing is the `released` service's (`dyad release`, #461, #470). The unit proposes; the operator disposes
(Rule-2).

## Parameter
`CRAFT` (`dyad-operator`, a Tended craft's name, or `bundle`) and `CLASS` (`dmc:release-class`'s termCode), read by
`number` from the environment. Neither has a default.

## Trigger
A done-`Y` lands a change under a craft's root (`dyad/` or `crafts/<craft>/`), or the operator asks for a release.

## Steps
| step | act | class | party |
|---|---|---|---|
| 1 | `dyad runbook run release changes` | read-only | unit |
| 2 | class each d-work it lists, one at a time, and take the change set's highest class: `dmc:release-class` | inference | unit |
| 3 | a critical fix in the set: when to propose, `dmc:release-timing` | inference | unit |
| 4 | a break, once the major is above 0: `dmc:release-break`; its upgrade step is `dyad/playbooks/port.md` | inference | unit |
| 5 | `CRAFT=<c> CLASS=<k> dyad runbook run release number` per tag, VERSION and the bundle row: `dmc:release-number` | read-only | unit |
| 6 | **Plan**: the release d-work names every tag and its number | question | operator |
| 7 | **Done**: the reply and its question, `dmc:release-reply` | question | operator |
| 8 | **Merge** of the cut PR from the recorded done-`Y`: `dyad merge` | reversible | unit or automaton |
| 9 | **Fence and release-ready** per tag: `dyad release ready <row> <tag> --at <cut> --archive <sha256>`, landed ledger-only; a failed fence writes nothing and returns to the question with the difference | clerical | unit |
| 10 | **Approval** of the publishing run on the hosting; a rejection or timeout publishes nothing | question | operator |
| 11 | **Record**: one `Y release <tag> at <cut> (archive <sha256>)` per tag, provenance `by reference`, `run <id> approved by <login> at <time>` (Rule-7 property 4); an unreadable run records nothing and says so | clerical | home |

Steps 9 to 11 run under the release gate (`RELEASE_APPROVAL=tap`, #545). With the gate off they are replaced by the
chat release question of `dmc:release-reply` and its recorded `Y`. A change set that does not release waits for the
next done-`Y`.

## Question
- Under the release gate: `Y/N: Done with #<id> <title> (merges PR #a, releases dyad-operator-v0.13.0, v0.17.0)?`
- With the gate off: `Y/N: release dyad-operator-v0.13.0, v0.17.0?`, the bundle named last.

## Evidence
Per tag, its class, each d-work that meets it with the evidence its class names, and the number. For the bundle,
the component classes it takes the highest of. The cut, and each archive's sha256 at the cut. After the merge, each
tag's fence result and the publishing run's link. The `Y` covers exactly the tags the question named (Rule-2,
Binding). A reply with the gate off ends in lines like these:

    dyad-operator-v0.13.0: class new capability (#474 dyad bootstrap; #476 check --evidence --brief/--show; #493 release play-book), significant enhancement (#475 parallel suite; #465 trace fence), critical fix (#475)
    v0.17.0: class new capability, the highest of its components (dyad-operator 0.13.0; cabinet, sysadmin, sysarch, syseng unchanged)
    cut ba7c47b; dyad-0.13.0.tar.gz 8a0572cd…b9a9; BUNDLE.sha256 b9060eb2…96e8
    Y/N: release dyad-operator-v0.13.0, v0.17.0?
