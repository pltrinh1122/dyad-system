# Run-book: port (install and port between dyad systems) — play-book `dyad/playbooks/port.md`, #353
# sections: Install, Crafts, Guards, Diff, Patch, Port

A core run-book (agent zone): the port play-book's steps as `dyad-cmd` blocks, run by either party through the core
runner, which prints the native line, records an event in `<runbooks>/events/port.jsonl` and tests the
postcondition. Its sections are its own (`# sections:` above). Each command reads `SRC`, `TAG`, `CRAFT`, `TARGET`
(default `.`), `DWORK` or `PATCH` from the environment, and runs from the git root it acts in: the receiving
repository for every step but Port, which runs in the authoring repository.

```text
SRC=dyad-0.11.0.tar.gz TARGET=. dyad runbook run port install
CRAFT=dyad-operator SRC=../dyad-system dyad runbook run port diff
```

## Install
The core craft from a release (play-book, forward 1): VERSION, roots and bundled crafts read from `SRC`:
```dyad-cmd
name: install
class: reversible
role: any
undo: git -C "${TARGET:-.}" checkout -- dyad crafts/REGISTRY.md && git -C "${TARGET:-.}" clean -fdq dyad
postcondition: dyad/bin/dyad craft list | grep -q "dyad-operator"
scope: <TARGET>/dyad/, bundled crafts/<craft>/, crafts/REGISTRY.md, the core's hooks (Rule-11 p2)

dyad/bin/dyad install "${TARGET:-.}" --from "${SRC:?release archive or authoring clone at its tag}"
```

## Crafts
One cited Tended craft the release does not bundle (play-book, forward 2); once per craft, each its own PR:
```dyad-cmd
name: crafts
class: reversible
role: any
undo: git checkout -- crafts && git clean -fdq crafts
postcondition: dyad/bin/dyad craft list | grep -q "installed"
scope: crafts/<name>/ and crafts/REGISTRY.md

dyad/bin/dyad craft install "${SRC:?archive or crafts/<name> directory}" --dwork "${DWORK:?d-work id}"
```

## Guards
The pass's postcondition (play-book, forward 3; Rule-14 property 3): exit 0, no `FAIL` line:
```dyad-cmd
name: guards
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --guards
```

## Diff
What this system changed in an installed tree, by path (play-book, diff 1): `dmc:port-diff`:
```dyad-cmd
name: diff
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/ or crafts/<CRAFT>/ (read), <SRC> (read)

dyad/bin/dyad craft diff "${CRAFT:?dyad-operator or a craft name}" --against "${SRC:?release archive or authoring clone at its tag}"
```

## Patch
The back-port's patch, source -> installed (play-book, back 1):
```dyad-cmd
name: patch
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/ or crafts/<CRAFT>/ (read), <SRC> (read); writes <CRAFT>.patch in the git root

dyad/bin/dyad craft diff "${CRAFT:?dyad-operator or a craft name}" --against "${SRC:?release archive or authoring clone at its tag}" --patch > "${CRAFT:?}.patch"
```

## Port
In the authoring repository, on a branch from `main`: apply the patch (play-book, back 2). The row is the Agent's
`dyad dwork new`, by `dmc:port-row`, once its `Y` is given: a ledger write the runner never makes (Rule-2):
```dyad-cmd
name: port
class: reversible
role: any
undo: git apply -R "${PATCH:?}"
postcondition: git diff --quiet --exit-code -- . ; test $? -eq 1
scope: the paths the patch names, in the authoring checkout

git apply "${PATCH:?path of the <CRAFT>.patch}"
```
