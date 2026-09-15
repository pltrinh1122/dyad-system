# syseng craft vocabulary (Tended terms)

One row per term. Craft terms are referenced, never defined, by the Agent vocabulary
(`dyad/vocabulary/VOCABULARY.md`, Rule-6 Boundaries); a core kernel may say `deterministic` and
means the sense here. `rule` names the craft rule (`../rules/`) that owns the term. `invariant`
is not here: it is an Agent term (owner Rule-12) because the runner's pass and Rule-2's evidence
read it. The rows moved from the Agent vocabulary (`generated file`, `import`, `author`,
`implementation path`, `mechanical check`) arrived by the fourth PR of d-work #162, after the core
dropped them (a craft term equal to an Agent term fails the craft check — the #160 lesson).
Checked by the craft guard (`dyad craft check syseng`: well-formed, namespaced, every `rule` exists).

| term | definition | rule |
|------|------------|------|
| naming pattern | one row of the naming table: a path, symbol or token shape, the kind of thing it names, one owner, one example, and whether `naming.py` checks it | naming |
| allow line | an `allow: <path> # <reason>` entry of `naming_rules.txt`: a path a pattern claims but that does not match it, listed with its reason; stale when the path is gone, unneeded when it matches again; the list only shrinks | naming |
| assert scan | the `ast.Assert` walk over every Python file under `dyad/` and `crafts/` outside `tests/`; any hit fails the invariants guard | invariants |
| idempotent | of a script, install or command: run any number of times it converges to one state and exits 0 once that state holds; a second run changes nothing | idempotence |
| deterministic | of a build, projection or evidence block: the same input state yields byte-identical output — sorted iteration, no timestamps, no banners; tested by running twice | determinism |
| generated file | a tracked-path candidate produced by running a craft or its tests rather than authored; never committed; matched by the `generated:` data of `package_rules.txt` | determinism |
| implementation path | one of the ways a plan's mutation can be realized; the path chosen is the one that leaves reusable code carrying a mechanical check | verifiable-code |
| mechanical check | a test, guard or invariant that verifies code or a rule without inference; what makes code verifiable | verifiable-code |
| live test | a test that reads the system it runs in — the instance's stores, or which Tended crafts are installed — rather than a fixture it builds; it states its empty-instance behaviour (`dyad/scripts/livetest.py`) | verifiable-code |
| import | bringing existing code into a craft or the agent's workflow under the import criteria, declared and pinned in the manifest | imports |
| author | writing code that could not be imported; permitted only when no candidate meets the criteria, the plan stating what was searched | imports |
| host fact | a fact about the machine the package runs on — path resolution (symlinks), filesystem case-sensitivity, line endings — read through `dyad/scripts/hostadapter.py`, never inlined at a call site | host-facts |
