# Run-book: craft (the operator craft's craft commands) — play-book `dyad/playbooks/craft-instantiation.md`, #165
# sections: New, Check, Guards, Tests, Export, Install, Registry, System

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the craft play-book as `dyad-cmd`
blocks, run by either party through the core runner, which prints the native line, records an event in
the instance's `<runbooks>/events/craft.jsonl` and tests the postcondition. Its section set is its own
(the `# sections:` line above; the sysadmin craft's server sections are a server's). Each command reads
its argument from the environment, as the native line shows; every command runs from the git root.

```text
CRAFT=<name> dyad runbook list craft
CRAFT=<name> dyad runbook run craft new
```

## New
Scaffold a craft (play-book Default; D3' author):
```dyad-cmd
name: new
class: reversible
role: any
undo: rm -r "crafts/${CRAFT:?}"
postcondition: dyad/bin/dyad craft check "${CRAFT:?}" >/dev/null
scope: crafts/<CRAFT>/ (new directory)

dyad/bin/dyad craft new "${CRAFT:?craft name}"
```

## Check
```dyad-cmd
name: check
class: read-only
role: any
undo: none
postcondition: none
scope: crafts/<CRAFT>/ (read)

dyad/bin/dyad craft check "${CRAFT:?craft name}"
```

## Guards
Every guard on the kernel-only path (Rule-14 property 3), pass criterion: exit 0, no `FAIL` line:
```dyad-cmd
name: guards
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --guards
```

## Tests
```dyad-cmd
name: tests
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

python3 -m unittest discover -s dyad/tests -q
```

## Export
```dyad-cmd
name: export
class: reversible
role: any
undo: rm -f "${CRAFT:?}"-*.tar.gz
postcondition: ls "${CRAFT:?}"-*.tar.gz >/dev/null 2>&1
scope: <CRAFT>-<version>.tar.gz in the git root

dyad/bin/dyad craft export "${CRAFT:?craft name}"
```

## Install
Import an existing craft corpus (D3'); `SRC` is an archive or a `…/crafts/<name>` directory, `DWORK` the d-work id:
```dyad-cmd
name: install
class: reversible
role: any
undo: git checkout -- crafts && git clean -fdq crafts
postcondition: dyad/bin/dyad craft list | grep -q "installed"
scope: crafts/<name>/ and crafts/REGISTRY.md

dyad/bin/dyad craft install "${SRC:?archive or crafts/<name> directory}" --dwork "${DWORK:?d-work id}"
```

## Registry
```dyad-cmd
name: registry
class: read-only
role: any
undo: none
postcondition: none
scope: crafts/REGISTRY.md (read)

dyad/bin/dyad craft list
```

## System
New dyad system (play-book, Steps: new dyad system; Operator-run — the remote credential is the Operator's):
`SYSTEM` is the fresh clone's path on the remote D1 selects.
```dyad-cmd
name: system-new
class: reversible
role: operator
undo: rm -r "${SYSTEM:?}/dyad"
postcondition: test -f "${SYSTEM:?}/dyad/VERSION"
scope: <SYSTEM>/ (a fresh clone; credential: the remote's)

dyad/bin/dyad install "${SYSTEM:?path of the fresh clone}"
```
