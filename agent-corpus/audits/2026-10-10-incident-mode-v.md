# Incident mode V — enforcement routed around

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 2 of 140 rows.*

## Definition
The Agent reached the repository by a path the blocking enforcement does not sit on: `--no-verify`
past `dyad/hooks/pre-commit`, with a compensating hand-run of the guard that either substituted for
a hook that genuinely could not execute, or was issued at a moment where it had nothing to read and
so proved nothing. The mechanism exists and runs; what is missing is its input.

**What would have to change.** Every path to a commit and to the remote would have to pass a check the
Agent cannot skip — which Rule-1's own Enforcement puts in d-work #24's hosting-side required status
checks and not in any local hook — or a compensating hand-run would have to be verifiable as having
read the real staged set.

Boundaries against the neighbours it is most easily confused with:
- **A, acting before the authorizing disposition** — Separating test: is the missing thing an Operator
  disposition or a guard run? A a disposition; V a guard run. Row 47 also carries A's and P's shape
  as secondary, since "No plan named a bypass"; the routing-around is primary because the decision to
  pass `--no-verify` is what started it.
- **M, no legal order, no verb** — the closest neighbour, and the boundary row is row 76 (#133,
  #191): seven ledger-only PRs pushed through the hosting API, so the pre-push hook and every guard
  never ran on them. Assigned to **M**, not here. Separating test: did a legal path exist? Row 76's
  cause cell says none did — "the plan gate (`prs.py`) refused each ledger commit because it cited no
  d-work, and one that opens or plans a row can cite none … this session is fenced off a direct push
  to `main` (Rule-1, #23), so the API was taken". V's two rows had a path: row 30's hook genuinely
  could not execute, which Rule-1 expressly permits, and row 47's hook was working.
- **P, unplanned cleanup under momentum** — Separating test: was the act the means of delivering the
  d-work? V yes, the commit itself; P no, a sweep beside the work.
- **Q, an obligation no mechanism reads** — Separating test: does a mechanism exist for it? V yes, and
  it was not shown the input; Q no mechanism exists at all.

## Incidents (2)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #25, #27, #35 | three commits were pushed with `--no-verify`, two of them ledger-only direct to `main`, one per zone branch | the pre-commit hook exited 126 before running, the guard's exec bit lost against the 644 mode rule |
| 2026-09-22 | #116–#125 | all ten branch commits were made with `--no-verify`, and each compensating guard run was issued after the commit with nothing staged | the hook was working and was bypassed anyway; the compensating run checked an empty set and proved nothing |

## Pattern
Both rows are `git commit --no-verify` past `dyad/hooks/pre-commit`, and they differ on exactly one
thing: whether the hook could run.

Row 30 is the path Rule-1 permits. The hook exited 126 — `dyad/hooks/pre-commit` execs
`containment.py` by path and the syseng mode rules kept every tracked `.py` at 644 — and Rule-1's own
clause covers that case: "A hook that cannot execute at all … leaves that enforcement vacuous, so the
Agent runs the guard by hand, records its observed line and the bypass in the commit message, and
reports an incident (Rule-3); … and never bypasses a hook that runs and fails (#23)"
(`dyad/rules/RULE-1-containment.md:51-56`). Row 30's consequence records the procedure followed each
time, with `containment OK [staged]` and exit 0 in each commit message.

Row 47 is the path the same clause forbids. The hook was working; ten commits took a blanket flag;
and the compensating run was issued *after* each commit, when nothing was staged, so it "checked an
empty set and proved nothing". Row 47 post-dates row 30 by six days and post-dates the Rule-1 clause
that already distinguished the two cases — that is the recurrence, and it is a recurrence past Rule
text, not past a mechanism. Both rows were caught by the Agent before any push; row 47's ten commits
were re-made under the hook and their shas changed before the first push, so nothing left the machine
unchecked in either row.

## Mitigations (phase 2)
1. **`dyad/hooks/pre-commit`** — `dyad/hooks/pre-commit:4`, exec'ing `dyad/guards/infra/containment.py
   staged` through `dyad/bin/dyad-python`. Moment: commit time, blocking. **Shipped.** It is the
   mechanism both rows went around, and `git commit --no-verify` skips it unconditionally with no
   record anywhere in the corpus that it was skipped. Reach as a fence: 0 of 2. Row 30 is the case
   where it could not run at all; row 47 the case where it could and did not.
2. **`dyad/hooks/pre-push` → `package.py check --guards --pre-push`** — `dyad/hooks/pre-push:4`,
   `dyad/scripts/package.py:583` (`cmd_guards`), judging the refs git is pushing from stdin via
   `pushed_refs` (`package.py:549-579`), refusing a ref that is not the checked-out HEAD or a dirty
   tree. Moment: push time, blocking. **Shipped.** It is the reason neither row reached the remote
   unchecked. Reach: both rows, as a later gate — but `--no-verify` skips it too, and this log records
   that being contemplated (row 14's withdrawn `--no-verify` push, mode T).
3. **`.github/workflows/dyad-containment.yml` and `dyad-d-work.yml`** — the detecting runners.
   Moment: `on: push: branches: [main]` with `paths-ignore: ['agent-corpus/d-work/**']`
   (`dyad-containment.yml:3-5`, `dyad-d-work.yml:3-5`) plus `workflow_dispatch`; never on a branch
   push and never on a PR event, which Rule-14 property 3 states as a property, not an accident
   (`dyad/rules/RULE-14-system-infrastructure.md:46-49`: CI "is never a gate"). **Shipped.** Reach:
   row 30's two ledger-only direct pushes to `main` are excluded by the `paths-ignore` — the one
   detecting runner is blind to exactly the path row 30 used and the path row 76 used. Row 47 never
   pushed, so nothing on `main` could see it.
4. **Rule-1's bypass clause** — `dyad/rules/RULE-1-containment.md:51-56`. Moment: inference, stated.
   **Shipped** as Rule text. Reach: row 30 followed it; row 47 breached it. Nothing anywhere verifies
   that a recorded `containment OK [staged]` line was produced on a non-empty index — row 47 is the
   proof, since its recorded runs were on an empty one, and the record read as compliance.
5. **A live, uncovered path to `main`, named rather than implied.** Verified today: a write that
   reaches `origin` through the hosting's API rather than `git push` invokes no local hook at all,
   and the two detecting workflows run only on a push to `main` with `agent-corpus/d-work/**`
   ignored (`dyad-containment.yml:3-5`, `dyad-d-work.yml:3-5`). So a ledger-only write through the
   API reaches `main` with **zero** mechanical coverage — neither the pre-push path nor CI.
   `prs.ledger_only` (`dyad/guards/agent/prs.py:54-57` and `prs.py:64-65`, the #191 exemption) removed
   the *reason* to take that route, which row 76's consequence states, and did not remove the route.
   For that path there is **no mechanism at all**.

## Remediation candidate, under attack
A `main`-side detector that cannot be routed around because it runs on what landed: drop
`paths-ignore` from `.github/workflows/dyad-containment.yml` and `dyad-d-work.yml` so the fence and
the provenance guard judge ledger commits on `main` too, and add a `dyad check --audit-main` verb
that walks `origin/main`'s commits since a per-checkout watermark and reports any commit whose
guards were never observed. Moments: on every push to `main` (the workflows, detecting) and at
session start (the verb).

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | CI cannot fence this. Rule-14 property 3 says it "is never a gate: it runs on `main` after a merge and on manual dispatch … the pre-push hook is the only check run before a merge" (`dyad/rules/RULE-14-system-infrastructure.md:46-49`). | confirmed | "Fenced" does not survive for the CI half. Detection does — and detection is what this mode's name asks for, since a path routed *around* is by construction discovered after the fact. The candidate must be offered as a detector, never as a gate. |
| 2 | Dropping `paths-ignore` runs the containment and d-work workflows on the most frequent commit in the system, the clerical ledger commit, which is presumably why the ignore is there. | survives (scoped) | Only for the checks that already judge a ledger commit: Rule-3's Mechanisms says the fence and the provenance guard judge each commit of a ledger-only range as they would on `main`, so those two run and the plan gate stays exempt by `prs.ledger_only` (`prs.py:64-65`). Running the whole suite on every ledger commit does not survive. |
| 3 | The session-start verb needs a stored "last audited sha", which is new instance state — Rule-16's store pattern and Rule-12 property 1's cost for a store nobody asked for. | survives (scoped) | Only by reusing an existing shape: the `suite memo` (vocabulary, Rule-12) is already a per-checkout file under the git common dir, untracked and shared by every worktree. The watermark takes that shape, so no tracked store and no new guard appear. |
| 4 | Easy agreement (Rule-9 Conditions): the uncovered API path read as the obvious live gap, so attack its urgency. The only use of that route in the whole log is row 76 (#133, #191), and #191's exemption removed its reason — a detector that detects nothing is cost without yield. | refuted as urgency, confirmed as coverage | The route is open and unguarded today, verified at `dyad-containment.yml:3-5`, and the log shows it taken once for seven PRs. Whether it is taken again is not something the code decides, which is why the survivor is a cheap detector rather than a gate — but the priority claim does not survive. |
| 5 | Row 47 is unreachable by any of this. Its ten commits never left the machine; what failed was a hand-run's *input*, and the only thing that can know a `containment OK [staged]` line was produced on a non-empty index at that commit is the hook `--no-verify` skipped. | confirmed | No part of the candidate reaches row 47. A fence for it would have to be inside the mechanism being bypassed, and `--no-verify` is git's flag, not the dyad's — so the fence for row 47 is Rule-1's own named successor, d-work #24's required status checks (`dyad/rules/RULE-1-containment.md:47-52`). |
| 6 | Attack the mode's own composition: row 30 is the Rule-permitted path, followed correctly, so is it an incident of this mode at all or merely a logged event? | survives (scoped) | It is an incident by Rule-3's definition — an action the plan did not name — and it belongs here because the *mechanism* is the same routing-around; what differs is that Rule-1 authorizes it when the hook cannot execute. So the mode's two rows are one mechanism under two authorizations, and only row 47 wants a fence. |

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** The row would read: *drop `paths-ignore:
['agent-corpus/d-work/**']` from `.github/workflows/dyad-containment.yml` and `dyad-d-work.yml` so
the fence and the provenance guard judge ledger commits that land on `main`, and add `dyad check
--audit-main`, which walks `origin/main` since a per-checkout watermark (the suite-memo shape) and
reports any commit whose guards were never observed — a detector on `main`, never a gate (Rule-14
property 3).* It would have caught row 30's two ledger-only direct pushes and the boundary row 76's
seven hosting-API PRs. It would **not** have caught row 47.

Stated against the exit, for the Operator to weigh. Row 47 is the more serious of the two rows — a
working hook bypassed, and a compensating record that read as compliance while proving nothing — and
nothing above reaches it. Its fence is the one Rule-1's Enforcement already names: "Until d-work #24
(internal LAN git server with required status checks) lands, these hooks are the only *blocking*
enforcement of Rule-1; CI only detects" (`dyad/rules/RULE-1-containment.md:47-52`). Exit 3 does not
apply to row 47: `--no-verify` is in Git, which Rule-14 property 2 places *in* the kernel rather than
in a hosted service, and the question "was this line produced on a non-empty index" is decidable, so
Rule-5's Enforcement does not cover it either. The Operator may therefore judge V still open on row
47 even with the proposed row opened. Proposed only — nothing closed here.

## Delta 2026-10-24 (#259 revision 5; 2 → 3 rows)
**Row added:** 176 (#297: `core.hooksPath=/dev/null` by reflex in a scratch worktree; re-made with the
hook). **Mitigations re-read:** unchanged; no path to a commit passes a check the Agent cannot skip
(Rule-1 Enforcement names the hosting's required checks). **Exit:** as proposed (#283 `backlog`); row
176 is the row-47 shape, which the proposed detector does not reach.
