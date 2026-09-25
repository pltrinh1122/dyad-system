# Optimization opportunities at current patterns of use (2026-09-25)

*d-work #161, plan `agent-corpus/d-work/plans/161.md`. Measured on this tree at `155a7eb` and, for
comparison, on `097b0ce` — the tree d-work #154's audit measured — in a throwaway worktree. Both on
**this** container: 4 CPUs, load 0.2–1.1, one measurement at a time, each act timed once. Detects and
ranks; disposes nothing. Every remedy is a backlog row, not a change made here.*

## 0. The first finding: seconds in this corpus do not travel

`agent-corpus/audits/2026-09-24-performance-bottlenecks.md` measured the core test root at **39.13 s**
with the runner's flag set. The same command on the same tree, here, takes **108.1 s**.

| tree | tests | core root, `DYAD_NO_NESTED_TESTS=1` |
|------|------:|------------------------------------:|
| `097b0ce`, on #154's machine | 479 | **39.1 s** |
| `097b0ce`, here | 479 | **108.1 s** |
| `155a7eb` (today), here | 491 | **118.7 s** (a second pass: 115.4 s) |

The 3× between #154's figure and today's is **the machine, not a regression**: this container is
about **2.8×** slower than the one #154 ran on, and the tree itself got **9.8% slower for 2.5% more
tests** in a day. Plan #161's attack A6 asked whether the 3× was the fifth craft, tests added since,
or a regression. It is none of those.

The consequence is a rule for this audit and every one after it: **an absolute second is a property
of one machine and one day; only a ratio travels.** Two figures now in the corpus are machine-local
— #154's whole table, and Rule-12 property 2's "120 s against 40 s on the core root". Neither is
wrong; neither is portable.

Property 2's *ratio* was tested here too, since it is the reason the Rule exists:

| the same core root | cost | ratio |
|--------------------|-----:|------:|
| hand-run, no `DYAD_NO_NESTED_TESTS` (nested suites recurse) | **628.0 s** | |
| `dyad check --tests dyad/tests` (the runner's own child) | **114.4 s** | **5.5×** |

Property 2 cites about 3×. Here the penalty is **5.5×**, so the Rule understates its own case on this
machine. The claim it rests on — a hand-run over a whole root costs multiples of the runner's — is
confirmed and stronger than written.

## 1. Where the time is

| act | cost here | what it is |
|-----|----------:|------------|
| `check --evidence` | **136.3 s** | `cmd_check()` (suite here) `\|` `cmd_guards()` (suite suppressed by `_SUITE_RAN`) |
| `check --guards`, range not ledger-only **or empty** | **128.8 s** | guards plus all five suites |
| `check --guards`, range ledger-only | **4.2 s** | guards only; suite skips (#155) |
| `check`, suite suppressed | **3.7 s** | the 24 non-suite checks |
| `check --pr`, `check --list`, `ledger`, `session list` | 0.2–0.3 s each | negligible |

**97% of a full run is Rule-12's five suites.** Everything the runner does besides the suites is
3.7 s, and it decomposes like this:

| part of a non-suite `check` | cost | note |
|-----------------------------|-----:|------|
| module import + registry build | 0.11 s | 23 guard modules |
| the invariant pass | **0.03 s** | 196 invariants, 35 modules — free |
| all 24 package checks | **3.20 s** | of which **`craft/crafts` alone is 2.09 s (65%)** |

And the suites decompose like this:

| root | cost | share |
|------|-----:|------:|
| `dyad/tests` | **115–119 s** | **92%** |
| `crafts/sysadmin/tests` | 4.4 s | 3.5% |
| `crafts/sysarch/tests` | 2.4 s | 1.9% |
| `crafts/syseng/tests` | 1.5 s | 1.2% |
| `crafts/countersign/tests` | 1.1 s | 0.9% |

Inside the core root, two modules are two thirds of it:

| module | cost | tests | per test |
|--------|-----:|------:|---------:|
| `test_package` | **64.7 s** | 50 | 1.29 s |
| `test_craft` | **13.5 s** | 15 | 0.90 s |
| `test_concurrency`, `test_distribute`, `test_runbook` | 3.9 / 3.2 / 3.0 s | | |
| everything else (8 modules under `guards/`) | ~25 s | | |

The per-case profile says what that cost *is*, and it is not what it looks like:

| act inside a test | cost |
|-------------------|-----:|
| one whole `scratch_install(with_craft=False)` — `git init` + `package.py install` (152 files) + `add -A` + commit | **1.24 s** |
| one `package.py check` child **in a scratch repo** (no crafts, no origin) | **0.64 s** |
| one `package.py check` child **in the real repo** | **3.66 s** |
| a bare interpreter start | 0.04 s |

`test_package` spawns **22** `package.py` children and **13** `scratch_install()`s; ten of its twelve
slowest cases (7.06 s down to 1.50 s) spawn a child that runs in the **real** repo, and each of those
pays the 3.66 s fixed cost above — of which 2.09 s is the `craft/crafts` guard scanning four craft
trees. The install itself, which looked like the obvious culprit, is **1.24 s** and is not the
problem.

## 2. Frequency: required, and observed

Seven days of `main`'s own first-parent history (a merge's file list is empty, so merges are counted
as merges, never as ledger-only — the trap #154 named):

| class | observed, 7 days |
|-------|-----------------:|
| ledger-only commits direct to `main` | **110** |
| merges into `main` | **111** |
| non-ledger commits direct to `main` | **0** — the main fence holds |
| d-works reaching `done` | **~64** (≈1.7 merges per d-work) |

| act | required by | granularity | consequence at today's cost |
|-----|-------------|-------------|----------------------------|
| `check --evidence` on the head being merged | Rule-2 Binding | **once per merge** | 111 × 136 s = **~4.2 h/week**, all of it *before* a Done-`Y` |
| `check --guards` at the push of the merge commit | Rule-14 property 3 | once per push | 111 × 129 s = **another ~4.0 h/week** |
| `check --guards` at a ledger push | Rule-14 property 3 | once per push | 110 × 4.2 s = **8 min/week** |
| a ledger commit per disposition | Rule-3 Ledger | once per disposition | negligible |
| hand-run suites | **nothing** (Rule-12 property 2) | zero | zero since #159 |

Branch pushes before a merge pay the full cost too and were not counted; the ~222 runs above are a
floor, not a total.

**The shape of the cost is two full runs per merge, ~8 h/week, and the Operator waits for half of
it.** Every evidence run sits inside a completion reply's critical path. #154's largest line — 3,894 s
of hand-run suites — is closed, by #155 and #159; what replaced it is the gate paying the same suite
twice per merge, which no amount of Agent discipline can reduce.

**Everything that is not the suite is 2.7% of a run.** That single number decides the ranking below:
only two things can matter — running the suite fewer times, and making the core root cheaper.

## 3. Candidates

### C2 — a merge pays the suite twice, and for 47% of merges the second tree is byte-identical
**~2.0 h/week; the largest single line.** `check --evidence` runs on the branch head; the post-merge
push of `main` runs the suite again over the merge commit. For a `--no-ff` merge whose base has not
moved, `tree(merge) == tree(branch head)` — measured: **53 of 112** merges in seven days.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A cached pass would put an unobserved line in the evidence block, and Rule-3 requires every result "as observed, never assumed". | **confirmed, and decisive** | The memo may short-circuit **only** the pre-push gate (Rule-14 property 3), never `check --evidence`, which always observes. The block's semantics stay whole and the second run still goes. |
| 2 | A tree hash captures neither the interpreter nor the installed craft set. | confirmed | Key = tree hash + interpreter version + the suite roots, stored per checkout under `.git/` (untracked, so Rule-11 property 6 is not engaged). A cold key — the Operator's machine — simply runs for real. |
| 3 | 53 of 112 is under half; the other 59 merges gain nothing. | confirmed | Scoped to ~47% of merges, and still the largest line. |
| 4 | Simpler: class the post-merge range ledger-only. | **refuted** | `origin/main..merge` contains the branch's own non-ledger commits; it is not ledger-only by any honest reading. A memo is the mechanism, or nothing is. |
| 5 | The memo is a cache, and this corpus already has one rule about caches (corpus wins on divergence). | survives | Same discipline: the memo is per-machine, never tracked, and its absence only costs time. On any doubt it is deleted and the suite runs. |

**Survivor → backlog #162:** a per-checkout, untracked suite-pass memo keyed on (tree hash,
interpreter, suite roots), consulted by the **push gate only**, never by `--evidence`.

### C4 — the core root's cost is child `package.py` runs in the real repo, not installs
**~20–35 s off every one of the ≥222 full runs a week: ~1.2–2.2 h/week.** Ten of `test_package`'s
twelve slowest cases spawn a real-repo `package.py` child at **3.66 s** each, and **2.09 s** of every
one of those is `craft/crafts` re-scanning four craft trees that the case does not care about. Two
independent levers:

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | The obvious fix — share one install, as `test_craft` already does with `_TEMPLATE`/`scratch()` — is the big win. | **refuted by measurement** | A whole `scratch_install` is 1.24 s; twelve shared copies save ~11 s, not the 25–45 s the plan guessed. Worth doing (and by lifting `test_craft`'s helper into `livetest.py`, not by copying it — Rule-13), but it is the *smaller* of the two levers. |
| 2 | The cases that spawn a full real-repo `check` need the whole runner. | **refuted in part** | Some assert on the runner's own composition and do need it; others assert one guard's line or one registry listing, and `check --list` costs 0.19 s against 3.66 s. Case by case, not wholesale. |
| 3 | Cutting `craft/crafts`' 2.09 s is a guard change, and Rule-11 owns that guard's semantics. | confirmed | So the survivor is scoped to *how* it scans, never *what* it decides: the same conclusions, reached without re-walking every craft tree per invocation. It pays twice in every evidence run as well (C3). |
| 4 | Test-only speedups are not worth a d-work. | refuted | The suite is 97% of every gate run, and the gate runs ≥222 times a week. Test cost *is* system cost here. |

**Survivor → backlog #163:** lift `test_craft`'s one-install-per-module template into `livetest.py`
and use it in `test_package` for every case that is not itself testing `install`; narrow the cases
that only need one guard's output; and treat `craft/crafts`' 2.09 s as its own measurement before
anything else is attempted.

### C1 — the suite runs on an empty range
`ledger_only_range` is `bool(paths) and all(…)`, so an **empty** range is not ledger-only and the
suite runs: `check --guards` on a synced `main` costs **128.8 s** to prove nothing about a range that
contains nothing.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | An empty range means nothing to push, so the hook never fires; this saves nothing. | **survives, scoped** | The hook does not, but `check --guards` is also the Agent's own local gate, which Rule-14 property 3 names, and it is run by hand — 80 occurrences in #154's window. Bounded, and the fix is one clause. |
| 2 | Skipping hides a broken **working tree**, which the suite reads and the range does not. | confirmed | True of the existing ledger-only skip too, and already surfaced: the evidence block prints `dirty=`. Noted, not widened. |
| 3 | `bool(paths)` was deliberate: "unknown range → False, so the suite runs". | refuted | An empty range is *known* and empty, not unknown. The comment's own reason — "a range that cannot change a suite's outcome" — covers the empty case exactly. |

**Survivor → backlog #164:** a resolvable empty range skips; an unknown range still runs.

### C3 — the evidence block pays the package checks twice
`cmd_evidence` is `cmd_check() | cmd_guards()`; `CHECKS` already contains every guard's
`check_package` (`dyad/scripts/package.py:295`) and `cmd_guards` runs every one again.
**Refuted on balance:** measured at **3.2 s of 136.3 s (2.4%)**, and removing it changes which lines
the block contains and therefore every `evidence-sha256` — a change to the artifact Rule-2's Binding
rests on, for 2.4%. Recorded as understood and deliberately not taken. If the block's format ever
changes for another reason, fold this in then. (C4's `craft/crafts` work reduces this by 65% for
free, without touching the block.)

### C5 — the five roots run in series
**Refuted as a priority.** The four craft roots together are **9.4 s** of ~125 s; perfect parallelism
across roots saves at most that, and after C4 the core root still dominates. Recorded so it is not
proposed again as though it were a win. If parallelism is ever wanted it belongs *inside*
`dyad/tests`, and that is a different d-work with a different risk (the suite spawns children and
writes temp trees; 44 orphaned processes once already, #155).

### C6 — push frequency
**Confirmed, unchanged from #154.** 110 ledger pushes a week at 4.2 s of hook each is **8 min**, and
each is what makes a disposition visible to the other sessions before one allocates an id — this
instance has paid for the alternative three times (#30, #26/#34, #27). Leave it alone.

## 4. Ranking

| rank | candidate | saving/week, this machine | risk | row |
|-----:|-----------|--------------------------:|------|-----|
| 1 | **C2** push-gate suite memo | ~2.0 h | medium — touches the push gate; must never touch `--evidence` | #162 |
| 2 | **C4** fewer and cheaper real-repo children in the suite | ~1.2–2.2 h | low — test-only, plus one guard's internals | #163 |
| 3 | **C1** empty range skips | bounded by hand-runs | low | #164 |
| — | C3, C5, C6 | — | not taken, reasons above | — |

C2 and C4 compose and are independent: C4 cuts the cost of a run, C2 cuts the number of runs. Taken
together they would put the ~8 h/week at roughly **4 h**, and the Operator's own wait — the evidence
run inside every completion reply — at about **3 h**.

## 5. Limits
- Every second here is this container's. Only the ratios travel (§0). A remedy's *ordering* is
  machine-independent; its payback in hours is not.
- Frequencies are seven days of one repository with several concurrent sessions. A quieter week
  scales all three savings down together.
- Each act was timed once, serially. Two earlier passes were **discarded, not reported**: one whose
  runs overlapped another's, and one that never ran at all (both recorded in `INCIDENTS.md`).
- Branch pushes before a merge were not counted, so ~222 full runs a week is a floor.
- No remedy is implemented here and nothing checks any of them. Each backlog row carries its own
  falsification when it is planned.

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #161.
