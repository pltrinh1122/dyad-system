# Falsification — skip the suite for record-only pushes (d-work #210)

**Claim (Operator, 2026-10-05, verbatim):** "falsify skipping the suite for record-only pushes". This is
#209's attack 5: four of the five work PRs only added an audit or a falsification record, and still
ran the full suite twice each.

**Reading.** Extend `suite_gate` (Rule-12 property 2) so that a range touching only instance records
skips the suite at the push gate, as a range touching only `<instance>/d-work/` already does.
Instance records are `agent-corpus/audits/` and `agent-corpus/falsification/`.

**Method.** Read at `60b5886`. Every test that reads the live repository (`dyadlib.repo_root()`) was
listed, and each one's input was traced to a guard that runs on every push (`check --guards`) or to
none.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Nothing in the suite reads a record that a guard does not already check. | **Refuted.** | The disclosure craft has no guard (`crafts/disclosure/guards/` does not exist). Its checks run only in the suite. `test_project_disclosure.LiveTests` assembles this instance's incident log, `agent-corpus/audits/INCIDENTS.md`, and asserts `redaction.findings(...) == []`, the gate that keeps a host name, address or credential shape out of a disclosure. A record-only push that adds such a value to an incident row passes every guard and fails only the suite. Skipping the suite would let it reach `main` silently. |
| 2 | Falsification records and audits other than `INCIDENTS.md` are safe to skip. | **Not shown.** | The sysarch projectors (`project_instances`, `project_erd`, `project_schema`) and `project_countersign` read `falsification/` and `audits/`. Their live tests render over this instance, with no guard counterpart. Whether a malformed record raises in them was not probed. Not refuted, but not established either, so not a basis for a skip. |
| 3 | The live tests that do read records duplicate guards. | **Survives, partly.** | `test_records` (`check_package(repo_root()) == []`) and `test_references.LiveTests` call the same functions as the `agent/records` and `agent/references` guards, which run on every push. Those two are pure overlap (#203 channel 1). Attacks 1 and 2 are not overlap. |
| 4 | The skip removes the suite's cost for a record-only change. | **Refuted, scoped.** | It removes one of two runs. `check --evidence` always runs the suite on the head to be merged (Rule-12 property 2, Rule-2 Binding), so a record-only PR would still pay one run, about 100 s. |
| 5 | A path rule by suffix (`*.md`) would do. | **Refuted.** | `suite_gate`'s own docstring records #137: a markdown run-book under `dyad/` falsified a pinned count and broke the core suite. Any skip must be by prefix, never by suffix. |

**Survivor.**
- Refuted as stated. A record-only range is read by suite-only checks with no guard: the disclosure
  live test's redaction gate over `INCIDENTS.md`, and the projectors' live renders. Skipping the
  suite drops them.
- The skip becomes sound only after those checks run as guards: a disclosure guard running
  `redaction.findings` over the incident log, and a projector smoke guard. Then the suite's live
  tests are overlap, and a record-only skip loses nothing.
- Even then it saves one of two runs, because evidence always runs the suite.
- The guard promotion is named here as the prerequisite, not opened.

Disposition: see ledger #210.
