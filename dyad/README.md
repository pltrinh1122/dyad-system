# dyad — package map (and the instance it runs on)

The core craft `dyad-operator` (`dyad/`; "the package", Rule-11): the Agent's operating frame, Rules, vocabulary, guards,
templates. The instance lives, by default and as an install creates it, in `agent-corpus/`
(`DYAD_INSTANCE` overrides) (ledger, audits, gap records),
`preferences-corpus/` and `workstation-corpus/`. Canonical; the per-machine
memory cache summarises it and never overrides it. Only `d-work/` reaches `main` without an
Operator `Y` (clerical ledger commits, fenced by `guards/agent/rows.py`); everything else lands by a
PR the Operator ratified. Any d-work that adds a directory here updates this map in the same PR.

| path | owner | holds | reaches `main` without a `Y`? |
|------|-------|-------|-------------------------------|
| `CLAUDE.md` | frame | operating frame, principles, imports, sentinel, conventions | no |
| `rules/` | Rule-4 (shape), Rule-5 (relations) | Agent Rules `RULE-<n>-*.md`, Rule-1 included (A2) | no |
| `vocabulary/VOCABULARY.md` | Rule-6 | master record of terms (term, definition, owner, used by) | no |
| `VERSION` | Rule-11 | the core craft's version; a release tag equals `v` + this | no |
| `bin/dyad` | Rule-11 | the one command-line entrypoint, `dyad <noun> <verb>` (property 2; preference `cli-pattern`, #152) | no |
| `scripts/` | Rule-11 (`package.py`, `dyadlib.py`, `distribute.py`, `craft.py`), Rule-19 (`runbook.py`, the runner); Rule-12 (the invariant protocol and pass, #162) | the runner `package.py` (the invariant pass first — `invariant_modules`, `cmd_invariants`, one `[invariant]` line per model module — then check / build / install / craft / ledger / dwork / project / runbook), the shared library `dyadlib.py` (paths, rows, the guard loader over two roots, the guard contract, `InvariantError` / `check_invariants` / `contract_invariants` / `runner_module`; every model module carries `INVARIANTS`, syseng `invariants.md`), the one distribution code path `distribute.py` (deterministic build, idempotent install, the instance-state scan; #156), the Tended-craft CLI `craft.py` (`list | check | export | install`), the run-book runner (parser, event store, `list | run | new`; its check is the sysadmin craft's guard) — never a guard, never a projector (`crafts/sysarch/rules/guards.md`; the projectors left for `../crafts/sysarch/projectors/` in #160) | no |
| `scripts/package_rules.txt` | Rule-11 | data for the package check: refused strings, artifact names, headers | no |
| `guards/<corpus>/<entity>.py` | Rule-11 property 1 (placement); the sysarch craft's `guards.md` (the contract, `dyadlib.CONTRACT`); each guard's check its Requirements Rule | one guard per entity kind under the corpus of its store, data beside it; discovered by `package.py check` (`--list` prints the registry) | no |
| `guards/agent/` | Rules 3 (`rows.py` the fence, `prs.py` the plan gate, both transaction guards; `plans.py`), 4 (`rules.py`), 6 (`vocabulary.py`), 9 (`records.py`), 20 (`references.py`), frame (`frame.py`) | the agent-corpus entity guards | no |
| `../crafts/sysadmin/guards/` | the sysadmin craft's rules (`host-mutation.md`: `changelog.py`; `ops-scripts.md`: `ops_scripts.py`; `server-instances.md`: `runbooks.py` the check, `events.py` the store's shape and append-only fence, a transaction guard); kernels Rules 8, 18, 19 | the workstation-corpus entity guards, in the craft since #155; discovered as `sysadmin/<entity>` (second guard root, `crafts/sysarch/rules/guards.md` p4) | no |
| `guards/craft/` | Rule-11 (`crafts.py` + `crafts_rules.txt`: the craft's shape — VERSION, no instance state, vocabulary namespaced via `agent/vocabulary.py`, guards meet the contract, Agent-process tokens warn via `agent/rules.py`, `requires`) | the craft entity guard, discovered as `craft/crafts`; run by hand as `dyad craft check` (#156) | no |
| `../crafts/REGISTRY.md` | Rule-11 (the craft registry; instance state in the craft zone) | one row per installed Tended craft (craft, version, source, sha256, d-work), written by `dyad craft install`; authored crafts have no row | no |
| `guards/preferences/preferences.py` | frame (Operator-owned table; each value's meaning is the Rule named) | the preference table's shape, enumerations, `read by` Rules | no |
| `guards/infra/` | Rules 1 (`containment.py`, zones, a transaction guard), 14 (`manifest.py` + `manifest_rules.txt`, the token→component map), 11 p7 (`bundle.py`, `BUNDLE.md` against the tree's craft VERSIONs, both directions) | the infra entity guards | no |
| `../crafts/sysarch/projectors/` | the sysarch craft's `projection.md` | projectors, since #160: each renders one surface (ERD: `project_erd.py`; system schema, five bands and labelled arrows: `project_schema.py`; entity schemas, one card per data entity with its fields: `project_entities.py`; the events surface is `../crafts/sysadmin/projectors/project_events.py`) from parsed corpus data; discovered by `dyad project --list` as `<surface> <craft> <module>`; a core-only install prints one line naming the craft to install | no |
| `../agent-corpus/projections/` | the sysarch craft's `projection.md` | generated projections (`erd.html`, `schema.html`, `entities.html`, `events.html`); untracked, refused by `package_rules.txt` `generated:` | never tracked |
| `tests/`, `tests/guards/<corpus>/` | Rule-12 (the suites run); the syseng craft's `verifiable-code.md` (the mapping, guard `syseng/tests`) | `unittest` tests: `test_<name>.py` per script, `guards/<corpus>/test_<entity>.py` per guard; run by `package.py check`, which then runs every `crafts/<craft>/tests/` present; each guard test asserts its `INVARIANTS` hold | no |
| `bin/dyad` | the one command-line entrypoint, `dyad <noun> <verb>` (Rule-11 property 2; preference `cli-pattern`) |
| `hooks/pre-commit`, `hooks/pre-push` | Rule-1; Rule-14 (I2) | containment on commit (`guards/infra/containment.py staged`); every guard on push (`package.py check --guards`; containment in `commits` mode — a push range is not a transaction, #166); `dyad check --pr <base> <head>` before opening a PR (the whole-diff `range` mode, the Agent's to run); `git config core.hooksPath dyad/hooks` | no |
| `templates/` | Rule-11 | empty ledger, incidents, preferences for a new instance (the change log's seed is the sysadmin craft's, #155) | no |
| `../agent-corpus/d-work/plans/<id>.md` | Rule-15 | stored plans; a plan-Y binds to the file | no |
| `../agent-corpus/d-work/rows/<id>.md` | Rule-3 (content), Rule-16 (store) | one file per d-work: state, every disposition, refs; `LEDGER.md` rendered, untracked | yes, row and plan files |
| `falsification/rules/` | Rule-9 | one record per Rule — package (A6) | no |
| `../agent-corpus/falsification/` | Rule-9 | records for gaps and other claims — instance | no |
| `../agent-corpus/audits/` | Rule-5 (sweeps), Rule-3 (`INCIDENTS.md`) | audits, sweeps, remediation plans, the incident log | no |
| `../crafts/sysarch/` | Rule-11 (a Tended craft, zone `craft`); its rules Tended — the System Architecture set since #160 | the system-architecture craft: six rules (`distribution`, `guards`, `manifest`, `projection`, `references`, `stores`), seven terms, three templates (guard, projector, entity card), the three core projectors with tests, one guard (`registry.py`: projector tests present, one craft per surface, core entities reachable), the records of retired Rules 17 and 21 | no |
| `../crafts/syseng/` | Rule-11 (a Tended craft, zone `craft`); its rules Tended — the implementation clauses of Rules 11, 12, 13, 14 since #162 | the system-engineering craft: six rules (`naming` — THE naming table, `invariants` — run-time invariants, never `assert`, `verifiable-code`, `imports`, `determinism`, `idempotence`), five terms (+ five moved from this vocabulary), two templates (a model module, its test), three guards with tests (`naming.py` + `naming_rules.txt`, `invariants.py` + `invariants_rules.txt`, `tests.py`), records | no |
| `../crafts/sysadmin/` | Rule-11 (a Tended craft, zone `craft`); its rules Tended | the system-administration craft: rules, vocabulary, templates, guards with tests, the reference git-server deployment (`server/`: `Dockerfile`, `entrypoint.sh`, `init.py`, `receiver.py`, `compose.yaml`, `.env.example`, `README.md`, `tests/test_server.py` — Rule-14 rows Gitea, Docker; never invoked by the core), docs, records; extracted by #155 | no |
| `../workstation-corpus/ops/` | Rule-18; instance, workstation zone | scripts the Operator runs for the Agent (`<d-work>-<hN>-<slug>.sh`, one per change-log row); checked by `crafts/sysadmin/guards/ops_scripts.py`; `ops/*.log` generated, never tracked | no |
| `infrastructure/INFRASTRUCTURE.md` | Rule-14 | manifest of every dependency on The World (kernel / library) | no |
| `../agent-corpus/d-work/provenance/<id>.md` | Rule-7 | one record per d-work: the Operator's prompts and dispositions, verbatim, in fenced entries, written clerically as they happen; raw session transcripts never enter (property 2) | yes, like rows and plans |

Two sets, three homes (Rule-5 `## Sets`, #160): **System Requirements** — the core craft's Agent
Rules (Rule-4 shape, Rule-5 sweep, Rule-6 terms), what the process must satisfy and what each guard
checks, the kernels of Rules 11, 12, 14, 16 and 20 included (a kernel is core because Rule-2's
Binding or Rule-3's completion evidence relies on it; each carries `Set: System Requirements
(kernel; content: crafts/sysarch/rules/<name>.md)`) — and **System Architecture** — how
infrastructure and guards are built, run and deployed: the sysarch craft's Tended rules,
`../crafts/sysarch/rules/`, swept by the craft's own form (Rules 13 and 19 carry the kernel label
since #162, content in the syseng and sysadmin crafts). The implementation discipline — how code is
written so it stays verifiable — is a third home, the syseng craft's `../crafts/syseng/rules/`,
read by the kernels of Rules 11, 12, 13 and 14 (#162). Boundary: a Requirement Rule owns
its guard's check; an Architecture Rule owns where and how it runs and never redefines the check
(ledger #71). Numbers 17 and 21 are retired (their rules are `../crafts/sysarch/rules/projection.md`
and `guards.md`); a gap in the numbering is not an error (Rule-4 counts the files present).

Rules 1–10: 1 containment, 2 no-self-ratify, 3 d-work,
4 rule integrity, 5 rule-set coherence, 6 vocabulary, 7 provenance, 8 host mutation, 9 falsification,
10 proposal-framing; 18 ops scripts. Tended Rules live in `crafts/<craft>/rules/` (the sysadmin craft's: `crafts/sysadmin/rules/`) and, host-specific, in `workstation-corpus/rules/`, outside this corpus.
