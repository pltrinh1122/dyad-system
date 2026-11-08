# Play-book: port (install and port between dyad systems; core craft, `dyad-operator`; #353)

A play-book (vocabulary, Rule-3) for moving a craft between an **authoring** system that releases it
(`pltrinh1122/dyad-system` for the core) and the systems that run it: every move is one recorded command,
never a sync, and nothing is mirrored (`dyad/rules/RULE-2-no-self-ratify.md`). Its steps are `dyad/runbooks/port.md`, run by
`dyad runbook run port <step>`, each leaving an event in `<runbooks>/events/port.jsonl`. What an install writes is
Rule-11 property 2's (`dyad/rules/RULE-11-distribution-structure.md`); a receiving system's upgrade order is
`crafts/sysarch/rules/distribution.md`'s; host prerequisites, step classes and the change-log row are
`crafts/sysadmin/rules/host-install.md`'s; a port's row and provenance are Rule-3 Intake's and Rule-7 property 4's.

## Parameter
From the environment: `SRC` (a release archive, `dyad-<version>.tar.gz` or `<craft>-<version>.tar.gz`, or an
authoring clone at its tag), `TAG` (`dyad-operator-vX.Y.Z`, `<craft>-vX.Y.Z` or a bundle's `vX.Y.Z`), `CRAFT`
(`dyad-operator` for the core), `TARGET` (the receiving root, default the git root), `DWORK`, `PATCH`. `SRC`, `TAG`
and `CRAFT` have no default.

## Trigger
An Operator prompt in the system where the step runs; its direction is `dmc:port-direction`.

## Steps
| direction | step | act | class | repository |
|---|---|---|---|---|
| forward | 1 | `install`: `dyad install <TARGET> --from <SRC>`; the registry's `dyad-operator` row names the release as its `source` | reversible | receiving |
| forward | 2 | `crafts`: `dyad craft install <SRC> --dwork <DWORK>`, once per cited craft the release does not bundle; `requires:` refuses too old a core | reversible | receiving |
| forward | 3 | `guards`: `dyad check --guards` exits 0 on the kernel alone (Rule-14 property 3) | read-only | receiving |
| forward | 4 | the install's change-log row, as `host-install.md` states; each PR cites that system's own d-work | clerical | receiving |
| diff | 1 | `diff`: `dyad craft diff <CRAFT> --against <SRC>`; its result is `dmc:port-diff` | read-only | receiving |
| back | 1 | `patch`: `dyad craft diff <CRAFT> --against <SRC> --patch > <CRAFT>.patch` | read-only | receiving |
| back | 2 | `port`: `git apply <PATCH>` on a branch from `main`, the row opened by `dmc:port-row` (`--relayed-via <system>-<row>`) | reversible | authoring |

No step writes to a repository other than the one it runs in, and none merges: every port is a PR its repository's
Operator disposes. A craft the authoring tree no longer holds is no trigger, and a forward port never removes it
(`dmc:port-direction`).

## Question
- A port owed: the change goes back, or the tree is reinstalled `--force` and the change is given up, asked as its
  own question.
- A back-port: the plan-`Y` and the patch in one reply, then the Done-`Y` (`dmc:port-row`).

## Evidence
The direction; the event ids of the run-book commands run (`<runbooks>/events/port.jsonl`); for a forward port, the
registry row written (`source`, `sha256`) and the `check --guards` pass; for a diff, the summary line; for a
back-port, the PR by number and zone and the `<system>-<row>` it carries. A step run outside the runner is an
incident (Rule-3).
