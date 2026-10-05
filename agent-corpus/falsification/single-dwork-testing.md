# Falsification — only a single d-work is necessary to execute all of the testing (d-work #209)

**Claim (Operator, 2026-10-05, verbatim):** "only a single `d-work` is necessary to execute all of the
testing. falsify."

**Reading.** The test-performance run of 2026-10-02 to 10-05 used five d-works, #204 to #208. The
claim is that one d-work would have carried all of it. A second reading is attacked too: that the
testing a d-work triggers should run once, not per push.

**Observed.** These are the cycles the five d-works cost.

| d-work | prompt | ledger PRs | work PR | full suite runs (push gate + evidence) |
|---|---|---|---|---|
| #204 profile | 2026-10-02 | 4 (#256 #257 #258 #260) | #259 | 2 |
| #205 batch scenarios | 2026-10-04 | 4 (#261 #262 #264 #275) | #265 | 2 |
| #206 signing requirement | 2026-10-04 | 3 (#266 #267 #276) | #268 | 2 |
| #207 signing batched | 2026-10-04 | 3 (#269 #270 #277) | #271 | 2 |
| #208 commits batched | 2026-10-04 | 3 (#272 #273 #278) | #274 | 2 |
| **total** | | **17** | **5** | **10** (each about 100–155 s, so about 20 min) |

All five Done-`Y`s came after the last plan-`Y`, from 2026-10-04 17:3x to 10-05 12:1x. No d-work's
output merged before a later d-work needed it.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The Rules allow one d-work for five prompts. | **Refuted.** | Rule-3, Scope: "Every Operator prompt opens a d-work. There are no exemptions," and "A new prompt while a d-work is open suspends it and opens another." The work came as five prompts: #204, then four "falsify" prompts, each reacting to the last result. So five d-works were mandatory. The count of d-works is set by the count of prompts, not by the work. |
| 2 | One prompt could have carried all the work, so one d-work would do. | **Refuted for this sequence; survives as a counterfactual.** | Each claim answered the previous result: #206 asked about the signing that #205 found, #207 batched what #206 explained, and #208 followed #207's finding. They could not have been planned in advance. Inside one d-work, each new claim is a plan revision with its own plan-`Y` (Rule-3: "Work that departs from the plan is a new plan and needs a new `Y`"; #199 revision 2 is the precedent). One d-work would therefore have saved the opening and the Done of four rows, 8 of the 17 ledger PRs, not the plan-`Y`s. |
| 3 | Five d-works bought separate verification and earlier landing. | **Refuted as practised.** | Each Done-`Y` verified one output, which is a real but small gain. Nothing landed early: every work PR waited until after the last plan. #206's 50 s per push saving reached `main` only on 10-05, after the other pushes had already paid without it. |
| 4 | One d-work means testing runs once. | **Refuted.** | Testing scales with work pushes, not d-works. The push gate runs the full suite on every push whose range touches anything outside `<instance>/d-work/` (Rule-12 property 2, `suite_gate`), and evidence runs it again on the merged head (Rule-2 Binding). One d-work with five work PRs still runs it 10 times. Only one work PR, carrying all outputs and pushed once, runs it twice. |
| 5 | Four of the five work PRs did not need the suite at all. | **Survives, scoped; not this claim.** | #204, #205, #207 and #208 added only an audit or a falsification record, with no code. The suite still ran, 8 runs and about 16 min, because those paths are outside `d-work/`. It is not pure waste: live-repo tests read the instance corpus (`test_records`, which counts `dyad/falsification/rules/` and calls `check_package(repo_root())`, and `test_references.LiveTests`), so a malformed record can turn the suite red. But those live tests duplicate the `agent/records` and `agent/references` guards, which run on every push anyway (#203's overlap channel). A suite skip for record-only ranges is a candidate for its own falsification, not a survivor here. |

**Survivor.**
- Refuted as stated. Rule-3 makes the number of d-works equal the number of Operator prompts. This
  work came as five prompts, each reacting to the last result.
- One prompt per arc, with each further claim answered as a plan revision of the same d-work, would
  have cost 9 ledger PRs instead of 17.
- Fewer d-works does not mean less testing. Testing scales with work pushes: one work PR at the end
  would have run the suite 2 times instead of 10.
- The larger testing waste is the suite running on ranges that only add a record (8 of 10 runs
  here). Those runs are justified only by live tests that duplicate guards already run. Named here
  as a candidate, not opened.

Disposition: see ledger #209.
