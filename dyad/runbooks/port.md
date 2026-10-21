# Run-book: port (install and port between dyad systems) — play-book `dyad/playbooks/port.md`, #353
# sections: Install, Crafts, Guards, Diff, Patch, Port

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the port play-book as `dyad-cmd`
blocks, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/port.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above; the sysadmin craft's server sections are a server's). Each command reads its
arguments from the environment, as the native line shows — `SRC` (a release archive or a tree), `TAG`,
`CRAFT` (`dyad-operator` for the core), `TARGET` (the receiving root, default `.`), `DWORK` — and runs from
the git root of the repository it acts in: Install, Crafts and Guards in the receiving repository; Diff and
Patch in the receiving repository; Port in the authoring repository.

```text
SRC=dyad-0.11.0.tar.gz TARGET=. dyad runbook run port install
CRAFT=dyad-operator SRC=../dyad-system dyad runbook run port diff
```

## Install
The core craft from a release (play-book, Forward 1): VERSION, roots and bundled crafts read from `SRC`:
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
One cited Tended craft the release does not bundle (play-book, Forward 2); once per craft, each its own PR:
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
The pass's postcondition (play-book, Forward 3; Rule-14 property 3), pass criterion: exit 0, no `FAIL` line:
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
What this system changed in an installed tree, by path (play-book, Diff); exit 1 is a port owed:
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
The back-port's patch, source -> installed (play-book, Back 1):
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
In the authoring repository, on a branch from `main`: apply the patch (play-book, Back 2); the row is opened
on the receiving Operator's own words by the Agent's `dwork new … --relayed-via … -d 'Y plan' --said 'Y'`
once that `Y` is given — a ledger write the runner never makes for the Operator (Rule-2):
```dyad-cmd
name: port
class: reversible
role: any
undo: git apply -R "${PATCH:?}"
postcondition: git diff --quiet --exit-code -- . ; test $? -eq 1
scope: the paths the patch names, in the authoring checkout

git apply "${PATCH:?path of the <CRAFT>.patch}"
```
