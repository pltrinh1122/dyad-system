# Run-book: craft (the operator craft's craft commands) — play-book `dyad/playbooks/craft-instantiation.md`, #165, #626
# sections: New, Check, Guards, Tests, Export, Install, Registry, System

The craft-instantiation play-book's steps, run through the core runner from the git root, each recording an event in
`<runbooks>/events/craft.jsonl`. `CRAFT` names the craft; `system-new` is the operator's (a remote credential). Every
step that writes states its undo and postcondition.

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
Every guard on the kernel-only path (Rule-14 property 3), pass criterion:
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
New dyad system (play-book, Steps:
```dyad-cmd
name: system-new
class: reversible
role: operator
undo: rm -r "${SYSTEM:?}/dyad"
postcondition: test -f "${SYSTEM:?}/dyad/VERSION"
scope: <SYSTEM>/ (a fresh clone; credential: the remote's)

dyad/bin/dyad install "${SYSTEM:?path of the fresh clone}"
```
