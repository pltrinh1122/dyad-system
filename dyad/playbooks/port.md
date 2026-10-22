# Play-book: port (install and port between dyad systems; core craft, `dyad-operator`; #353)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision; its steps are a run-book. This one decides how a craft moves between dyad systems — an
**authoring** system that releases it (`pltrinh1122/dyad-system` for the core craft), and the systems that
run it — in each of three directions, so that every move is one recorded command whose output is the record
the receiving system's Rules already require, and never a sync. Cited by the sysarch craft's
`crafts/sysarch/rules/distribution.md` (Receiving-instance upgrade order, #178), beside the install path
Rule-11 property 2 owns (`dyad/rules/RULE-11-distribution-structure.md`). Steps: `dyad/runbooks/port.md`,
run through `dyad runbook run port <step>`, the core runner, so each step leaves an event in the instance's
`<runbooks>/events/port.jsonl`. Nothing here redefines a Rule: what an install writes is Rule-11's, the order
of a receiving system's upgrade is `distribution.md`'s, the host prerequisites, the class of every step and
its change-log row are the sysadmin craft's `crafts/sysadmin/rules/host-install.md`; a port's row and
provenance are Rule-3's Intake and Rule-7 property 4's.

## Parameter
Every step takes its arguments from the environment, as `craft.md` reads `CRAFT`: `SRC` — a release archive
(`dyad-<version>.tar.gz`, `<craft>-<version>.tar.gz`) or a tree (an authoring clone checked out at its tag);
`TAG` — the release tag the port is about (`dyad-operator-vX.Y.Z`, `<craft>-vX.Y.Z` or a bundle's `vX.Y.Z`,
Rule-11 property 4); `CRAFT` — the craft a diff or a port is about (`dyad-operator` for the core); `TARGET`
— the receiving repository's root for an install into another checkout (default: the git root the command
runs from). No default for `SRC`, `TAG` or `CRAFT`: a port of the wrong thing is worse than none.

## Trigger
One of three, each an Operator prompt in the system where the step runs (Rule-3: a prompt opens the d-work;
a message from another system's agent opens nothing — Intake):
- **forward** — a receiving system is to run a newer release of a craft it has installed (or to install one
  it lacks). Precondition: the release exists as a tag of the authoring repo (Rule-11 property 4); a craft
  whose live `VERSION` has moved past its last tag is released first, by the authoring Operator's
  `Y/N: release <tag>?` — this play-book never cuts a tag.
- **diff** — a receiving system's registry row no longer matches its tree (`dyad craft list` prints
  `(modified)`): what changed, by path, is to be read before it is overwritten or carried upstream.
- **back** — a change made in a receiving system's tree is to reach the authoring system: a port owed.

Not a trigger: a **retired craft** — one the authoring tree no longer holds (the instance: `crafts/countersign/`,
which #369 C5 retires once its model and code are the core's, C3–C4). Retirement is no release (Rule-11 property
4), so it ports nothing: a receiving system holding `countersign` ≤0.3.0 keeps it until its own Operator prompts
for the port that replaces it, and a forward port of a later core release never removes it — an install writes
only under the installed craft's root and rewrites only that craft's registry row (Rule-11 property 2), so the
retired craft's row stays `installed` against the source it names. That source is the authoring clone at the
last commit that touched the craft (`346a9a2`, 0.3.0): no `countersign-v*` tag was ever cut, so a diff or a
patch of it names that commit as `SRC`, never a tag. The authoring Agent may tell the receiving system this — a
notice carrying its Operator's verbatim words, sent on that Operator's `Y` — and nothing more: the port is the
receiving Operator's own prompt (Rule-3 Intake; Rule-2), never this play-book's step.

## Default
**Every port is a PR its receiving repository's Operator disposes; nothing is mirrored.** A sync that
merges without a disposer is self-ratification by machine (`dyad/rules/RULE-2-no-self-ratify.md`), so no
step here writes to a repository other than the one it runs in, and no step merges. What the play-book
streamlines is producing, in one command each, the install, the diff and the PR with its provenance.

## Procedures
### Forward (authoring → receiving)
In the receiving repository, in the order `distribution.md` rules (the core first, then every Tended craft
the core's Rule text cites, `check --guards` asked to be clean against the whole pass, not each PR):
1. `install` — `dyad install <TARGET> --from <SRC>`: the core craft from the release, VERSION, roots and
   bundled crafts read from the release itself; the registry's `dyad-operator` row records the archive's
   name or `<clone>@<TAG>` as its `source` (`distribute.source_name`), so the row says which release runs.
2. `crafts` — `dyad craft install <SRC> --dwork <DWORK>` once per cited Tended craft the release does not
   bundle, each its own craft-zone PR (Rule-1); `requires:` floors refuse a craft on too old a core.
3. `guards` — `dyad check --guards` exits 0 on the kernel alone (Rule-14 property 3): the pass's postcondition.
4. The install's change-log row, in the receiving system's host corpus, as `host-install.md` states
   (class, undo, the install's printed line, the registry row); instance state — ledger, preferences, host
   corpus — never travels (Rule-11 property 1). Each PR cites that system's own d-work.

### Diff (what a receiving system changed)
1. `diff` — `dyad craft diff <CRAFT> --against <SRC>`: one line per path, `added`, `removed`, `modified`
   or `mode`, read from the installed side, then a summary; exit 0 unchanged, 1 differing. `SRC` is the
   source the registry row names — the release archive, or the authoring clone at that tag.
2. A non-empty diff is a **port owed**: either the change goes back (below) or the tree is reinstalled
   `--force` and the change is given up — the Operator's call, asked as its own question.

### Back (receiving → authoring)
1. `patch` — `dyad craft diff <CRAFT> --against <SRC> --patch > <CRAFT>.patch`: the unified diff, source →
   installed, which applied to the authoring tree at `TAG` reproduces the change.
2. `port` — in the authoring repository, on a branch from `main`: apply the patch (`git apply`), then open the
   row **in one command on the receiving row's own Operator prompt**, the cheapest admissible same-Operator
   form (Rule-3 Intake; Rule-7 property 4):

       dyad dwork new "<title>" "<refs>" --prompt-file <the receiving row's provenance entry> \
           --relayed-via <system>-<row> -d 'Y plan' --said 'Y'

   The receiving row's `prompt` entry is that system's Operator's own words, carried verbatim; `--relayed-via`
   notes where they were given (`<system>-<row>`, e.g. `client-dyad-system-12`). The row is born on the
   plan-`Y`, so the intake's opening `Y` and the plan-`Y` are one question — asked with the plan and the patch
   in the same reply, by the Agent of the authoring system to its own Operator — and the Done-`Y` is the
   second: two dispositions, Rule-3's floor, and nothing skipped. A different Operator on the two sides is
   the same form with the Operator's `Y` opening the row first (Intake), never this shortcut.
3. The PR cites `d-work #<id>` (the authoring row) and the receiving `<system>-<row>` in its body; one zone
   (Rule-1); the receiving system then takes the change back as a **forward** port of the next release, and
   its tree reads `installed` again. A defect ported without an Operator prompt behind it carries its
   evidence in the plan file instead (Intake's defect shape); it opens its row on the Operator's `Y` alone.

## Steps
The run-book `dyad/runbooks/port.md`, sections `Install`, `Crafts`, `Guards`, `Diff`, `Patch`, `Port`; the
steps are `install`, `crafts`, `guards`, `diff`, `patch`, `port`. `install`, `crafts` and `port` are
reversible (each names its undo and postcondition); `guards`, `diff` and `patch` read only.

## Evidence
The completion reply (Rule-3) cites: the direction; the event ids of the run-book commands run
(`<runbooks>/events/port.jsonl`); for a forward port, the registry row written (`source`, `sha256`) and the
`check --guards` pass; for a diff, the summary line; for a back-port, the PR by number and zone and the
`<system>-<row>` it carries. A step run outside the runner is an incident (Rule-3).
