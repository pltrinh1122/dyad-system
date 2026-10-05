# The test subset CI should run if the full suite runs only at audit (2026-10-05)

*d-work #219. The Operator's prompt, verbatim: "if the full test suite is executed only during
'audit', identify the subset that should be executed during CI." "CI" here means the local push
gate, which is this system's CI (Rule-14 property 3); hosted CI only corroborates on `main`. This
audit detects and sizes. It changes no Rule and no code, and it opens no row.*

**Carried from `2026-10-02-test-execution-profile.md` §0:** an absolute second is a property of one
machine and one day; only a ratio travels. The seconds below are the #204 per-test durations: core
root, signed commits, at `7034d76`. Since #206 the gate runs unsigned, about 0.74× those figures.
The shares are what to read.

## Method
- **Dependency map.** A static map of all 45 test files (921 tests) at `9fafb51`. For each file it
  records the modules the file imports, loads with `load_guard` or `load_package`, or names by
  `*.py`. A change selects every test file whose dependency set meets the changed modules.
- **Time per file.**
  - Core-root files use the sum of their #204 per-test durations (n=1).
  - Craft-root files use their root's #204 median, scaled by the file's share of that root's tests.
  - `test_trace.py` and `test_playbooks.py` postdate `7034d76` and carry no measured time. Both are
    sub-second.
- **Full suite, on that basis:** 921 tests, about 140.6 s summed.
- **Code:** the map and its sizing are session-local scratch (`impact219.json`, `t219.py`), not
  corpus. They are the input to a `dyad check --impacted`, if one is ever wanted.

## The subset rule
The per-change gate runs, in this order:
1. **Always:** the invariant pass and every guard, about 4 s. These are unchanged; they are the
   live-repo verdicts.
2. **Always:** every test that spawns the entrypoint, because a spawned `dyad/bin/dyad` imports
   whatever it dispatches to and so has no static dependency set. These are `test_entrypoint`,
   `test_dyadlib`, `test_trace` and syseng `test_naming`, together under 1 s.
3. **The selected files:** every test file whose dependency set meets a module the range changes.
4. **The checks that exist only as tests,** when the range touches the records they read. #217
   found three: redaction, `incidents.check`, and the trace store's `check_store`. Until they are
   promoted to guards, their test files join the subset whenever the range touches
   `agent-corpus/audits/INCIDENTS.md`, provenance, or `agent-corpus/d-work/traces/`.
5. **The full suite instead,** when the range changes any of these:
   - a hub module — `dyadlib` (42 of 45 files depend on it), `package` (12), `rows` (12),
     `livetest` (11);
   - any test file, or the runner itself (`package.py`'s `check_rule_12` and `cmd_tests`);
   - `dyad/bin/dyad`;
   - the craft discovery path. Discovery decides which roots and guards exist, so a static map
     cannot see past it.
6. **Nothing beyond step 1** for a ledger-only or record-only range. This is the status quo for
   ledger-only (Rule-12 property 2); for record-only it is the survivor of #210.

## Measured subsets
| change | test files | tests (of 921) | summed s | share of time | the rule's verdict |
|---|---:|---:|---:|---:|---|
| `package.py` | 12 | 290 | 92.2 | 66% | full (hub) |
| `trace.py` + `package.py` | 13 | 302 | 92.2 | 66% | full (hub) |
| the `rows` guard | 12 | 311 | 91.1 | 65% | full (hub) |
| `dyadlib` | 42 | 882 | 137.9 | 98% | full (hub) |
| the `provenance` guard | 4 | 193 | 71.2 | 51% | subset |
| `livetest` | 11 | 195 | 22.7 | 16% | full (hub) |
| a projector (`project_kanban`) | 2 | 61 | 6.0 | 4% | subset |
| `trace.py` alone | 1 | 12 | <1 | <1% | subset |
| a craft guard (`changelog`) | 1 | 20 | 1.2 | 1% | subset |
| the `vocabulary` guard | 1 | 8 | <1 | <1% | subset |
| record-only | 0 | 0 | 0 | 0% | guards only |

## What this finds
- **The saving is uneven.** A change to a leaf module (a craft guard, a projector, `trace.py`, most
  core guards) drops from about 140 s to under 7 s. A change to `package.py`, `rows` or `dyadlib`
  saves little even as a raw subset (34%, 35%, 2%), and the rule sends it to the full suite anyway.
  `test_package` alone is 46% of core time (#204) and sits in every `package` subset.
- **What #204–#219 actually changed.** Over this window the code d-works touched `package.py`
  (#206, #213), so every one of their pushes would still have run the full suite. The other d-works
  of the window wrote records only (audits and falsification records), and those are already
  guards-only under #210's and #211's survivors. **In this window the subset rule would have saved
  almost nothing.** It pays on craft and guard work, which this window did not do.
- **A hub's cost is the hub's shape, not the rule's.** Splitting `test_package` would shrink the
  subsets that select it. So would moving the runner-level fixtures that `test_package` shares out
  of `package.py`. Either is a follow-up, not this audit.

## Blind spots of the static map (stated)
- **Dynamic dependencies.** The map cannot see `load_module` by a built path, guard and root
  discovery, or a spawned entrypoint. Steps 2 and 5 cover these by always-run or full-suite, not by
  analysis.
- **Data files.** A change to a `*_rules.txt` or `*_contrib.txt` file selects only the files that
  name it by path. A guard's data drives that guard's own test, so the map adds the guard's module
  whenever its data beside it changes. That is a convention to implement, not something measured
  here.
- **Count is not time.** Every share above is time, from #204, not a test count.

## What the change costs in the Rules (not made)
Running the full suite only at audit amends three Rules. The audit names each and makes none:
- **Rule-12 property 2:** "the pre-push path runs [the suite] on every push whose range touches
  anything outside `<instance>/d-work/`." The suite would become the subset.
- **Rule-14 property 3 and Rule-2 Binding:** `check --evidence` runs every root and is the merge
  evidence. If the evidence also ran the subset, a merge would be ratified on fewer observed tests.
  The narrower option keeps `check --evidence` full and subsets only the push gate. It saves the
  push-time suite (#209) and leaves merge time as it is.
- **The regression window.** A regression in an unselected file lands on `main` and is caught at the
  next audit or at the next full-suite push, whichever comes first. With full evidence at merge
  (the narrower option), that window closes at every merge.

**Proposed (not opened):** if wanted, one backlog row for `dyad check --impacted`, implementing
steps 1–6 for the pre-push path only, with `check --evidence` unchanged. Its value is limited to
leaf-module work, as measured above.
