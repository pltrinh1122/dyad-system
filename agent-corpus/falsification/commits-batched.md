# Falsification — we can batch the commits (d-work #208)

**Claim (Operator, 2026-10-04, verbatim):** "we can batch the commits. falsify." It was made in
reply to #207, which found that signing cannot be batched and that what signing still costs is the
Agent's own real commits.

**What a commit costs here.** Signing costs about 88 ms per commit (#207) and does not matter. What
matters is the cycle around each ledger event. A session fenced off a direct push to `main`
(Rule-1, #23) records every ledger event through a ledger-only PR under `ledger-pr-merge: agent`:
branch, commit, push (ledger-only, so guards only and no suite), create the PR, merge the PR. That
is three or four tool calls and one inference turn around them per event. Observed this session:

| d-work | ledger PRs | work PRs |
|---|---|---|
| #204 | 4 (#256 open, #257 plan, #258 plan-Y, #260 Done) | 1 |
| #205 | 3 so far (#261 open, #262 plan, #264 plan-Y) | 1 |
| #206 | 2 so far (#266 open with plan, #267 plan-Y) | 1 |
| #207 | 2 so far (#269 open with plan, #270 plan-Y) | 1 |

The wall time per cycle was not measured. It is dominated by tool calls and inference, not by git.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A d-work's ledger events can all go in one commit. | **Refuted.** | Four events, ordered by the Operator's answers: the opening prompt with the plan, the plan-`Y`, the work, and the Done-`Y`. A `Y` cannot be recorded before it is given. Rule-7 property 3 says an entry is written when its event happens, never gathered later. |
| 2 | The row's opening and its plan file can share one commit. | **Survives, and is already done.** | Since #206, row, prompt and plan file go in one ledger commit and one PR: 2 cycles became 1 (#204 and #205 used 2, #206 and #207 used 1). Both come before the plan question, and the plan file must exist before it is asked (Rule-15). |
| 3 | The plan-`Y` record can ride on the work PR. | **Refuted.** | The plan gate (`prs.py`, Rule-3) resolves the cited d-work on the base branch's ledger and requires a `Y plan` there. On the work PR's own branch the plan-`Y` is not yet on `main`, so the push and the PR are refused. The plan-`Y` must land on `main` first. |
| 4 | The Done-`Y` record can ride on the work PR, as one extra ledger-only commit merged with it. | **Mechanically admitted; refuted by the Rules as written.** | Probed at `6cd89d6`, not pushed: a branch carrying the work and a `207 → done` row commit passes every transaction guard and `check --pr`. But Rule-2's Binding lets a Done-`Y` merge only heads unchanged since it was asked. A Done commit changes the head after the question, so the evidence no longer names the merged head. Rule-3 (#68) also requires the record to precede the merge. Landing it in the same merge is a reading the Rule does not state. Allowing it is a Rule-2 and Rule-3 amendment, which is the Operator's decision. |
| 5 | Ledger events of different d-works can share one ledger commit and PR. | **Survives.** | Every Rule constrains the order within one d-work, never across d-works. When one reply records several events, for example #205's Done with #208's opening, or a batch disposition, which already writes one entry per named row (Rule-3), one ledger commit and one PR carry them all. That saves one cycle per extra event, and only when events coincide. Each event is still committed when it happens (Rule-7 property 3), so this batches pushes, not deferred writes. |
| 6 | The work commits can be batched, by squashing. | **Refuted as a saving.** | Every work PR this session is already one commit. |
| 7 | Batching commits saves signing time. | **Refuted.** | About 88 ms per commit (#207). The saving that matters is cycles, not signatures. |

**Survivor.**
- Each d-work needs at least three ledger cycles (open with plan, plan-`Y`, Done) and one work PR,
  under the Rules as written.
- Batching already removed one cycle: open and plan share a commit (attack 2).
- Batching saves more only across d-works whose events coincide in one reply (attack 5). The
  survivor is to do that whenever events coincide.
- Going below three needs a Rule change. Letting the Done record ride on the work PR (attack 4)
  would make it two plus the work PR, but it amends Rule-2's heads-unchanged binding and Rule-3's
  record-before-merge. That is the Operator's decision.
- The underlying cost is the fence that forbids a direct push of a ledger-only commit to `main`
  (#23). Each ledger event is a PR only because of it. Lifting that fence for ledger-only commits,
  which Rule-2 and Rule-3 already make clerical, removes the cycle entirely. It is an
  environment/session setting, not a repo change.

Disposition: see ledger #208.
