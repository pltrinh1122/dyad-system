# syseng — the system-engineering craft (Tended craft, `crafts/syseng/`, zone `craft`)

*Implementation* discipline — how the code that realizes a design is written so it stays
verifiable — as one contained, versioned, exportable tree (Rule-11: a Tended craft; Rule-1: zone
`craft`). Extracted from Agent Rules 11, 12, 13 and 14, from the sysarch craft's `projection.md`
(p3, p5) and the sysadmin craft's `ops-scripts.md` (the mechanics block) by d-work #162 (plan
`agent-corpus/d-work/plans/162.md`; the classification of #161). The core craft `dyad-operator`
(`dyad/`) keeps the kernels of those Rules and the protocol code that runs every session
(`dyadlib.InvariantError`, `check_invariants`, the runner's invariant pass); each kernel cites the
craft rule it reads by path. Version: `VERSION` (0.1.1). Requires the core (`dyad/`) and, for the
projectors its guards cover, any craft that ships them (none required).

| path | holds |
|------|-------|
| `rules/` | seven Tended rules — `naming.md` (THE naming table), `invariants.md` (run-time invariants, never `assert`), `verifiable-code.md` (Rule-12's cut clauses and the test mapping), `imports.md` (Rules 13/14's cut clauses), `determinism.md` (Rule-11 p6, projection p3/p5), `idempotence.md` (Rule-11 p5, ops-script mechanics), `host-facts.md` (Rule-14 p4, Rule-11 p2: one place per host fact, `dyad/scripts/hostadapter.py`) — and their index `README.md` |
| `vocabulary/CRAFT.md` | the craft's terms (`naming pattern`, `allow line`, `assert scan`, `idempotent`, `deterministic`, `host fact`, and the five rows moved from the Agent vocabulary: `generated file`, `implementation path`, `mechanical check`, `import`, `author`) |
| `templates/` | `module.py` (a model module: constants, `INVARIANTS`, `main`), `test.py` (its test: every invariant holds, the module is in the runner's pass) |
| `guards/` | `naming.py` + `naming_rules.txt` (every tracked path and registered symbol matches its pattern; reasoned allow lines), `invariants.py` + `invariants_rules.txt` (no `assert` outside `tests/`; model modules expose `INVARIANTS`; entries well-formed), `tests.py` (the test mapping moved from `check_rule_12`) — discovered by the core runner as `syseng/<entity>`, `CORPUS = "craft"` |
| `tests/guards/test_<entity>.py` | one per guard; run by `dyad check` |
| `falsification/` | `syseng-extraction.md` (this d-work's attack table) and `rules/<rule>.md`, one per craft rule, naming what was cut from where |
| `docs/naming.md` | the naming table's rationale, one page |

## What stays in the core craft
The protocol (`dyad/scripts/dyadlib.py`: `Invariant`, `InvariantError`, `invariants_of`,
`check_invariants`, `contract_invariants`, `runner_module`, `projector_files`), the pass
(`dyad/scripts/package.py`: `invariant_modules`, `cmd_invariants`, run first by `check` and
`check --guards`), the call sites (`dyad dwork new|state`, `runbook.run`), and one `INVARIANTS`
list per model module of the core. The runner's `check_rule_12` keeps "run the tests". The
manifest guard keeps the token scan (Rule-14's). `check_generated` keeps the generated-file data
(Rule-11's).

## Importing this craft into another dyad system
`dyad craft export syseng` here, `dyad craft install syseng-0.1.0.tar.gz` there (core first). The
three guards then appear in `dyad check --list` as `syseng/naming`, `syseng/invariants`,
`syseng/tests`, and the entities surface gains their cards. A system without this craft runs none
of them — it does not practise engineering (plan #162 attack 5). Nothing under this tree names a host.
