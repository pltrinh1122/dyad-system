# Tended rules of the syseng craft

Operator-tended rules of the system-engineering craft: how the code that realizes a design is
written so it stays verifiable — as opposed to how the process runs (the core Rules) or how the
infrastructure is shaped (the sysarch craft). Any form. They are not Agent Rules (Rule-4
classifies): no block, no coherence sweep, no Agent-vocabulary discipline; their terms are
`../vocabulary/CRAFT.md`. Each opens with one line naming the core Rule whose kernel reads it, or
the craft rule it was cut from (#161's classification table, executed by #162).

| rule | read by | what it holds |
|------|---------|---------------|
| `naming.md` | every Rule that names a pattern (Rules 3, 4, 9, 11, 15, 16, 20; the sysadmin and sysarch rules) | THE naming table: one row per pattern the corpus uses, one owner each; checked by `guards/naming.py` from `guards/naming_rules.txt` |
| `invariants.md` | Rule-12 (kernel: code carries its check; the term `invariant`) | run-time invariants: `INVARIANTS`, `check_invariants`, `InvariantError`; the runner's pass; never `assert`; a false invariant is an incident |
| `verifiable-code.md` | Rule-12 | code over inference where the check can be mechanical; the chosen path and its reuse yield; the test mapping (`guards/tests.py`) |
| `imports.md` | Rules 13 and 14 | import over author; every import declared and pinned; kernel ecosystem first; the token and import scan the manifest guard runs |
| `determinism.md` | Rule-11 (p6 stub), the sysarch `projection.md` | generated files never committed; self-contained, byte-identical output; the evidence block's determinism |
| `idempotence.md` | Rule-11 (p5 stub), the sysadmin `ops-scripts.md` and `server-instances.md` | scripted, idempotent, tested install; the `postcondition`/"already satisfied" form of an ops script and a run-book command |
| `failure.md` | Rule-12 (kernel: code carries a check that runs) | fail early and loud: early is a *place* (declaration → transaction → run → use), loud is named and attributable (every fault **and** every skip prints a line), fatal is not early (a run reports every fault); a stance, no guard of its own |
| `host-facts.md` | Rule-14 (p4: The World observed, not pinned), Rule-11 (p2) | one place per host fact — path resolution, case-sensitivity, line endings — through `dyad/scripts/hostadapter.py`; two functions, not a framework |
