# Falsification record — token efficiency: what to mechanize and delegate (d-work #333)

**Claim (relayed Operator prompt, 2026-10-17).** The dyad-system Agent can be made more
token-efficient by mechanizing and delegating its frequent activities to code; a thorough audit of
past activity (ledger, git commits, PRs) shows which. The audit is
`../audits/2026-10-17-token-efficiency.md`. This record attacks its method and each ranked candidate.

**Disposition:** disposed by the Done-`Y` of d-work #333 (Rule-2; see ledger #333).

## Method

| # | attack | result | survivor |
|---|---|---|---|
| F1 | Tokens cannot be measured per act without transcripts; the ranking dresses estimates as findings. | survives, scoped | Session totals are measured; per-call ≈ $0.20 is derived with its formula. Each rank is kept only where it holds against its neighbour under a 2× error in that estimate. Candidates 1–4 survive this; 6–10 are listed in order but not distinguished. |
| F2 | The derived prices are guessed. | refuted | Priced at the published per-MTok rates with cache writes at 2×; the derivation reproduces `cost_usd` within 3% for every session under $150. The four large Sonnet sessions are under-derived by up to 2.3×, stated as unexplained, and excluded from no total. |
| F3 | Raw token counts mislead: cache reads are 99% of tokens and cheap. | confirmed (plan F5) | Ranked by dollars. Cache reads are still 49% of cost, so "cheap per token" does not make them small. |
| F4 | Sixteen sessions are too few; the craft sessions of September dominate and are atypical. | survives, scoped | The shares (output ~10%, cache ~90%) hold per session across all 14 priced sessions (output 6–22%), not only in the total, so the conclusion "turns × context" does not depend on the outliers. |
| F5 | #154/#161/#204 already did this. | refuted | Their survivors were all test-time; §4 shows none touched the clerical sequences or the context-size cost, which a seconds measurement cannot see. |
| F6 | Easy agreement on "mechanize the ledger" (the obvious answer). | pushed | Attack C1b below. |

## Candidates

| # | attack | result | survivor |
|---|---|---|---|
| C1a | A commit-and-push verb removes the Agent's judgment of what goes in each ledger commit. | refuted | The verb stages only the files the same verb just wrote. The ledger-only fence and every guard still run on the push it makes. Judgment was never exercised there: the subject restates the transition. |
| C1b | Ledger commits are 74% of commits but cheap, a few hundred bytes each; the saving is illusory. | refuted | Their cost is not their bytes but the 3–5 full-context calls each takes (§2: a call ≈ $0.20 at 300 k context). 737 × 3 calls is the largest frequency × calls product in the audit. |
| C1c | Pushing from a script races concurrent seats exactly as the Agent does. | survives, scoped | Yes, so the verb owns the fetch → rebase → retry loop, and the race costs a loop iteration instead of a turn. It must refuse, not retry, on a guard FAIL (Rule-1: never bypass a hook that runs and fails). |
| C2a | Slimming the frame weakens the agent: the Rules ground anti-cave and two-models, and an unloaded Rule is not obeyed. | survives, scoped | This is the strongest counter in the audit. The block (Intent, Target, Boundaries, Conditions) is what triggers a Rule's use, and Rule-4 already makes it countable. The survivor is a proposal for the Operator to weigh, not a recommendation to cut. The ≈ $470 is derived, and it rises as Rules grow (+65% in one month). |
| C2b | The frame is cached, so it costs only cache-read prices. | refuted | Cache reads are 49% of cost; the frame is ~13% of each read and is written again whenever a session's cache is rebuilt. |
| C3 | The Done order is subtle (#202); code will get it wrong where inference got it right. | refuted | Inference did not get it right: 12 incident rows and 7 recovery rows are that one mechanism (#202's own amendment). The fence `rows.landing_problems` already decides ancestry. The verb calls what the fence checks. |
| C4 | Housekeeping rows are where the Operator asks for reassurance; a command answers a different question than the one asked. | survives, scoped | The command gathers the facts (branches, heads, PRs); the Agent still answers. Six "falsify banked" rows re-gathered the same facts by hand. |
| C5 | "Work at small context" is conduct, which #188/#192/#195 already falsified, and delegation still did not fire. | survives, scoped | Conduct did not change behaviour, which is the finding. The survivor names the measured price: craft sessions at 530–680 k context cost 3–37× a cabinet. Whether it becomes a preference or a mechanism is the Operator's call. |
| C6–C10 | Each saves too little to rank. | confirmed | Listed, not ranked against each other (F1). C9 is kept because it removes an incident mode, not for its tokens. |
| C11 | Rule-13 property 1: this is the fourth hand-run activity audit, so the miner should have been built now. | survives, scoped | It ranks 10th by saving. Building it inside this d-work would have widened a plan that proposed no code (Rule-12). It is listed as candidate 10. |

## Rule-5
No Rule is edited; no pairwise statement is owed.
