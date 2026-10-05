# Falsification — skipping the suite for ledger-only pushes (d-work #211)

**Claim (Operator, 2026-10-05, verbatim):** "falsify skipping ledger-only pushes." The practice under
attack is `suite_gate`'s existing skip (d-work #155, Rule-12 property 2): a range whose every path is
under `<instance>/d-work/` does not run the suite at the push gate.

**Method.** Read at `60b5886`. Every live-repo test that reads the d-work store (rows, plans,
provenance, sessions) was traced to a guard that runs on every push, ledger-only ones included
(`check --guards` runs all guards whatever the range), or to none. `INCIDENTS.md` was searched for an
incident caused by a ledger-only push.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Every suite check that reads the ledger is also a guard, so the skip loses nothing. | **Refuted.** | Most are duplicates. `test_provenance` live, `test_sessions` live (`describe`) and `test_references.LiveTests` call the `agent/provenance`, `agent/sessions` and `agent/references` guards' own functions. Two are not. `test_project_countersign` asserts `project_countersign.check(collect(repo_root())) == []` over the live ledger: every row becomes an act, a processor's kind must match its mode, and a signer must be human. `countersign` has no guard. `test_project_kanban` asserts every row is on the board. A ledger-only push that the row guard accepts but `countersign.check` rejects skips the suite, lands on `main`, and turns red the next unrelated code push. |
| 2 | That gap has bitten. | **Refuted, as observed.** | `INCIDENTS.md` holds no incident of a ledger-only push turning the suite red. The nearest, #175 (2026-09-25), is tests asserting live instance values, a different cause. The gap is real by construction and has not been observed. |
| 3 | Removing the skip is the fix. | **Refuted.** | Ledger-only pushes are the most frequent push. In #204 to #208 there were 17 ledger PRs against 5 work PRs (#209). At about 100 s a run, removing the skip adds roughly 28 min to such a run, to guard against an unobserved failure in two checks. |
| 4 | Run only the ledger-reading tests on a ledger-only push. | **Survives, as an option.** | The live countersign and kanban tests are a few seconds. But it adds a second gate list to keep in step with the tests, a recurring inference task (Rule-13). |
| 5 | Promote the two suite-only checks to guards. | **Survives.** | A `countersign` guard running `check(collect(root))`, and a kanban count, would run on every push, ledger-only ones included, through `check --guards` (Rule-14 property 3). The suite's live tests become overlap (#203), and the skip is then exact. |

**Survivor.**
- The skip survives, scoped. It is sound for every ledger-reading check except two:
  `project_countersign.check` and the kanban row count. Those run only in the suite, which a
  ledger-only push skips.
- The gap has not been observed.
- The fix is not removing the skip, which would add a full suite to the most frequent push. The fix
  is to make those two checks guards. That is the same promotion #210 needs for records, so one
  change closes both.
- Named here, not opened.

Disposition: see ledger #211.
