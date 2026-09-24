# Falsification — "remote pushes are too frequent, and a resilient host lets the frequency drop"

**Claim (Operator, 2026-09-24):** too much unnecessary git remote push is occurring given the risk
associated with an unstable host; the current host is resilient, so remote push frequency can be
reduced to eliminate unnecessary overhead.

Ledger #154. The attacks below were written against measurements taken before the plan-`Y`, and
every figure they rest on is reproduced with its command in
`agent-corpus/audits/2026-09-24-performance-bottlenecks.md`.

**Claim:** remote pushes are too frequent, and since the host is resilient their frequency can be
reduced to eliminate unnecessary overhead.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Measure the overhead a push actually carries. | **Refutes the premise** | A push costs the pre-push hook plus network: **1.75 s** of guards, no tests. At 201 commits over four days that is under six minutes of guard time in total. Push frequency is not where the wall-clock goes. |
| 2 | Then where does it go? | **Confirmed, and it is the audit's real subject** | `check --evidence` is **42.75 s** and runs the whole suite. Rule-2's Binding requires it once, on the exact head being merged. In this session it was run three or four times per d-work — before the PR, after a correction, and again after the merge — plus a throwaway worktree each time. One d-work's verification therefore cost minutes where the Rule asks for one run. |
| 3 | Grant the premise anyway: were pushes frequent *because* the host was unstable? | **Refuted** | Nothing in the corpus says so. The pushes are paced by Rule-3's Ledger ("the Agent writes each entry clerically when the disposition is given") and by Rule-3's Completion ("the ledger's own record of the `Y` precedes every merge it ratifies"), and by Rule-16, whose id allocator and collision guard both read `origin/main`. Host stability is named nowhere in that chain; the one host-resilience incident on record, #48, is about memory contention killing test runs, not about lost commits. |
| 4 | Reduce the frequency anyway — batch the ledger commits and push once per turn. | **Survives, scoped, and the scope is the cost** | It would work for a single-session instance. This instance is not one: a concurrent session is demonstrably active (rows #114, #126, #127, #138 landed mid-turn during these four days, and one push this session was rejected for a moved `origin/main`). `dwork new` allocates `max(origin, local)+1` after fetching, and `rows.check_id_collisions` judges a branch against the `origin/main` it can see; an unpushed ledger commit is invisible to both. Batching trades 1.75 s per push for the id races #30, #26/#34 and #27 already cost this ledger three renumberings and one overwrite. |
| 5 | Is the host in fact resilient, as the claim assumes? | **Survives, scoped** | Nothing observed this session contradicts it. But #48 records two OS kills of test runs on this machine under memory pressure from concurrent sessions, and the audit's own `check --evidence` timing will vary with that pressure. Resilient against power loss is not the same as unloaded; the claim is safe for durability and unsafe as an assumption about timing. |
| 6 | Is wall-clock even the right metric? | **Confirmed — the audit must carry a second axis** | The largest single wall-clock item observed in this session is not a git operation at all: one delegated workflow ran **32 minutes** and spent **1.15 M subagent tokens**; another spent 2.37 M. Delegation is what `concise-mode` and `delegation: plan-and-execute` prescribe, so this is the practice working as designed — but it dwarfs every git cost by two orders of magnitude, and an audit that measured only pushes would report the smallest item and miss the largest. |
| 7 | Steel-man the Operator: even 1.75 s × 201 is real, and each push also runs a network round trip. | **Survives, scoped** | It is real and it is small. The honest form of the Operator's intuition is not "push less" but "run the expensive verification once, where the Rule asks for it" — which is attack 2, and which the Operator's instinct located correctly even though the named mechanism was wrong. |

**Verdict.** The hypothesis is refuted as stated and right in its instinct. The overhead is in the
verification path, not the push path, and the dominant cost of all is delegated execution.

## What the audit found after these attacks were written
The measurements confirm attacks 1, 2 and 6 and sharpen attack 2. A push costs 2.5 s of which
1.65 s is the pre-push hook, and all 85 ledger pushes to `main` over four days cost about five
minutes between two sessions. `check --evidence` was run 79 times against 29 completed d-works,
2.72 times the once-per-merge that Rule-2's Binding asks. And a third cost, named by neither the
claim nor these attacks, is larger than both: 134 hand-run test suites, 3,894 s, none of them
required by any Rule, each paying roughly three times the runner's price because a hand-run does
not set the nested-test flag the runner sets for itself.

## Disposition
Surfaced for the Operator; nothing here changes a push, a hook or a Rule.
Disposition: see ledger #154.
