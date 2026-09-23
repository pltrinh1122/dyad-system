# Incident mode B — stale local view of the remote

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #118, child of #116 (2026-09-22).*

## Definition

Mode B names one mechanism: a conclusion, a plan or a branch built on a git ref the clone had
never fetched, or on a local ref that had fallen behind the remote. The fault is in the view, not
in the judgment made from it — the information was already published, and one fetch would have
supplied it. Every row below is a claim of absence or of currency ("this sha does not exist", "no
tag exists", "this fix is still needed", "this is `main`") made from an object store that had not
been refreshed.

Boundaries against the neighbouring modes:

- **C (concurrent-session race).** C's colliding fact lives only in another session's local tree —
  an id not yet pushed (#30, #26/#34, #27), a presence name indistinguishable from a peer's. No
  fetch reaches it. B's fact is on the remote already, so a fetch resolves it. #3 sits on that line
  and is B: a peer session caused the staleness, but the peer's fix was on `origin/main` before #3
  executed, so the view, not the race, is what a refresh would have corrected.
- **D (wrong cause asserted).** Two rows here — #22's unfetched branch tip and #80's tags — also
  carried a wrong diagnosis; #116 marks D secondary in both. The stale view is what started it, the
  wrong cause is what the stale view produced. A D without a B is a misreading of evidence that was
  fully present locally (#6's `git add` mode claim).
- **A (acting before the Operator's `Y`).** #22 and #110 each own mode-A rows on the same dates.
  Those are ordering faults against a disposition; the rows below are ordering faults against a
  fetch. Nothing in A is corrected by reading the remote.

## Incidents (5)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14 | #3 | a planned craft-zone fix (stale `syseng` guard data) and a `--no-verify` push were both withdrawn before execution: a concurrent session's d-work #1 (PRs #1, #2) had already landed the identical fix on `origin/main` | the plan was written against `main` at `2dad9be` and reached execution at `eb9775c` (`plans/3.md`): by the time it executed, `origin/main` had moved and the remedy it proposed was already published there. Only the ledger rows executed |
| 2026-09-16 | #22 | `agent/references` `plan.base->commit` FAIL on `plans/19.md` (base `49e9988`) was reported to the Operator as a defect in the ledger with an unrecoverable sha | the clone had never fetched `origin/infra/18-release-secret`, whose tip *is* `49e9988`; the diagnosis was made from `git cat-file` alone. `git fetch origin` resolved it. Secondary: D (the cause asserted was wrong) |
| 2026-09-16 | #22 | the branches were cut from a `main` 4 commits behind; the rebase that followed regressed row #6 from `done` to `backlog` in the conflict | the session's clone was never fetched before branching, and d-work #6 (a peer session's) had completed and moved `main` meanwhile |
| 2026-09-18 | #80 | "dyad-system upgraded to 0.7.1" was falsified as false — "no release tag exists" — and that conclusion merged (PR #55); `v0.7.0`, `v0.7.1`, `dyad-operator-v0.6.0`/`0.6.1`, `sysarch-v0.1.5` and `sysadmin-v0.1.0` all existed, cut the day before | every check used `git fetch origin main`, an explicit refspec, which suppresses git's tag auto-following, so no tag was fetched all session; absence was concluded from a view that had never looked. Secondary: D |
| 2026-09-22 | #110 | `git checkout main -- .` restored 156 tracked files' content — index and working tree, on branch `dwork-108-done` — to an ancient state; `dyad/VERSION` read back `0.5.0` | a local branch `main`, created early in the session and last moved at `7ddffdb`, sat 328 commits behind `origin/main`; the command meant `origin/main` and the bare name resolved to the stale local ref |

## Pattern

All five make a claim about the remote from a clone that had not been refreshed; what varies is
the distance (4 commits, 328 commits, an unfetched peer branch, a fetch form that fetched no tag at
all) and the cost (three caught before harm, one misdiagnosis delivered to the Operator, one
conclusion merged as PR #55). Two are absence claims and three are currency claims, and in the two
absence claims the stale view produced a confident wrong cause as well. The mode is live: the most
recent occurrence is #110, 2026-09-22, the same day as this audit. Nothing mechanical has shipped
since — the discipline exists only as the "rule learned" sentences the log itself carries in #22,
#80 and #110, in no Rule, no guard and no command; the sole fetch in the core craft's commands and
guards is `dwork new`'s id allocation (`dyad/scripts/package.py:443`,
`crafts/sysarch/rules/stores.md`; the test suites fetch only inside their own scratch repos), and it uses the
explicit-refspec form `git fetch -q origin main` that #80 names as the cause. One narrowing did
land: Rule-20 property 2 now skips a `done` or `archived` row's base commit
(`references.base_commit`), so #22's exact FAIL cannot recur on a terminal row — an active row's
can.

## Remediation candidate (falsified, not disposed)

Candidate, as surfaced for the Operator's disposition, not as a course taken here: `dyad session
touch` would run `git fetch --tags --prune origin` before writing the presence file and print
`main`'s distance from `origin/main`, so that the first command of every session and every plan-`Y`
refreshes the view; and, as conduct rather than mechanism, this repo's own local `main` ref would
not be used bare — `origin/main` or an explicit sha instead.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | a fetch at touch time is already stale at execution time: touch runs at session start and at plan-`Y` only, and #22's misdiagnosis was made at a mid-session check run tied to neither point (the log carries the date, not the hour) | survives, scoped | the fetch is a floor, not a guarantee. What covers the window is the discipline the log learned twice (#22, #80) and never encoded: fetch before asserting that a commit, a branch or a tag does not exist. The command change narrows the window; the claim-time fetch closes it |
| 2 | the candidate would not have caught #110: fetching `origin/main` does not change what the bare name `main` resolves to, and the plan's framing — every case followed an explicit-refspec fetch or none at all — holds for #22's two rows and #80, not for #3 (a peer landing first) or #110 (a local ref never updated) | confirmed | the candidate is two moves, not one, and only the first is a command change. The never-bare clause is conduct — #110 never reached a commit, so no guard could have seen it — and is reported as conduct, unenforceable by the guards as they stand |
| 3 | Rule-14 property 3 keeps every guard on the kernel alone, hosting being a library adapter; `dyad/guards/infra/bundle.py` states it outright — "the kernel-only path never fetches" | refuted as a blocker, scoped | `dyad dwork new` already fetches (`package.py:443`: `check=False`, 30s timeout, a printed warning and a local-only fallback; `crafts/sysarch/rules/stores.md`). The precedent is a non-enforcing command fetching best-effort and degrading to a warning, which is what `session touch` is (Rule-16 Presence: advisory only, never a guard failure). The kernel-only check path (`check --guards`) stays fetch-free, and `--prune` drops tracking refs only, never objects already fetched |
| 4 | the corpus already has a staleness mechanism — a plan file records `main`'s base commit, Rule-15 phase 2 re-plans if `main` moved past a touched file, and Rule-20 resolves `plan.base->commit` on every push | refuted as sufficient | both read the local view. #22 is that mechanism firing correctly and being misread: the message is bare, `FAIL plan.base->commit: … does not resolve` (`dyad/guards/agent/references.py`), and names no remote. An additive, cheaper survivor: a commit-kind resolver that fails says the target is not known *locally* and names the fetch, so the guard's own words refuse the absence claim |
| 5 | coverage — the fetch clause mechanically addresses only the two rows whose missing object was on the remote (#22's branch tip, #80's tags); #3 and #22's 4-behind branches are addressed by the printed distance, which is advisory, and #110 by conduct alone | survives, scoped | 2 of 5 mechanically, 2 advisory, 1 conduct. Scoped as such: the candidate is a floor under the mode, not a fence around it, and it is reported that way rather than as a fix for the mode |

Net: the candidate survives only as two separable moves — one command change and one piece of
conduct — plus attack 4's additive resolver message. It does not survive as a single mechanism that
covers the mode.

## Disposition

Surfaced for the Operator; disposed by the Done-`Y` of ledger #118 (Rule-9 Form). Remediation
itself is a further Operator prompt on this row, never taken here.
