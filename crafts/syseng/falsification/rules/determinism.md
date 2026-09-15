# Falsification record — syseng craft rule `determinism.md` (d-work #162)

**Claim:** Generated-never-committed, self-contained output and byte-identical output are one discipline, a craft's.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 17.3 | Sorting is forgotten in one iteration and the twice-render test still passes by luck. | Survives, scoped | Unchanged from Rule-17's record: the twice-render test over the live instance; a new projector inherits it from the sysarch template. |
| 162.10 | `check_generated` runs in the core but its rule is a craft's. | **Confirmed** | Rule-11 keeps a one-line p6 stub owning the data and the check; this rule owns what counts as generated. |
| 162.15 | The evidence block now prints the pass twice (`check` and `check --guards`). | Survives, scoped | Deterministic and identical both times (`test_evidence_block_deterministic`); one hash. Noted for the Operator. |

Cut from: Rule-11 p6; sysarch `projection.md` p3, p5 (their records, amendments #162).

Disposition: see ledger #162.
