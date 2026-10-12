# Incident mode P — unplanned cleanup under momentum

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 4 of 140 rows.*

## Definition
A tidying act — in all four rows, deleting a local git branch — is performed while finishing a
d-work, although no plan named it, because sweeping up feels like part of the work in hand rather
than a mutation needing authorization. The act is deliberate and the omission is the authorization,
not the intent.

**What would have to change.** The act would have to meet a mechanism at the moment the ref is
deleted, since the only thing standing between the Agent and the act today is the Agent's own
reading of its plan.

Boundaries against the neighbours it is most easily confused with:
- **A, acting before the authorizing disposition** — A's act has a counter-prompt that was asked
  late, or not at all, for an act the plan did name. Separating test: is there a disposition this act
  was waiting for? A yes; P no — no plan item existed, so nothing was pending.
- **K, a plan incomplete against its own text** — K's plan omitted something its own text implied,
  found while executing. Separating test: does the plan's own text imply the act? K yes; P no — a
  branch deletion is not implied by any of these four plans' subject matter.
- **O, a git write used as a read** — both touch git state the plan never named. Separating test: did
  the Agent intend to change state? P yes, deliberately; O no — O's three commands were meant as
  reads.
- **Q, an obligation no mechanism reads** — Q is the omission of a required record; P is the
  commission of an unrequired act. Separating test: commission or omission? P commission — though
  all four rows also carry Q's shape as a secondary, since none has the change-log row Rule-8
  requires (below).

## Incidents (4)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-25 | #167 | the Agent deleted the local branch `dwork-sync-open`, which plan #167 did not name | the branch was merged and still on `origin`, and it was swept with the named branches under momentum |
| 2026-09-29 | #133, #191 | the Agent deleted five local branches no plan named, their content already on `main` or empty | cleanup under momentum, the #167 pattern again, and deleting them was not in either plan |
| 2026-09-29 | #194 | the Agent deleted local branch `dwork-open`, which no plan named, its content already on `main` | the #167 pattern, third occurrence, despite the previous row's prose fence |
| 2026-09-30 | #199 | while planning #199 the Agent deleted local branch `ledger-198-open`, created seconds earlier and holding no commits | the #167 pattern, fourth occurrence, one row after the third was recorded |

## Pattern
Four occurrences of one act in six days, all `git branch -D` of a local branch no plan named. All
four lost nothing: each branch's content was already on `main` or the branch was empty, and row 77's
consequence records the content being "checked file by file against `origin/main` before each
deletion". All four were disclosed by the Agent, three in the completion reply and one in a plan.

Recurrence evidence is unusually exact, because the log states it in the rows themselves. Row 77
(2026-09-29) wrote the prose fence: "second occurrence of #167's mode, so a local-branch deletion is
now named in a plan or not done." Row 80, the same day under #194, is the third occurrence "despite
that row's 'named in a plan or not done'", and says "The conduct fence in prose has now failed once
after being written". Row 85 (2026-09-30) is the fourth, "one row after #195 recorded the third", and
says "The prose fence … has failed again". So the prose fence failed in **row 80 and row 85** —
twice after being written — and both rows name the failure as evidence for a mechanical fence.

## Mitigations (phase 2)
**No mechanism reads a branch deletion.** Read from the code rather than asserted:
1. **The only place in the tree that reads refs at all** is `pushed_refs` in
   `dyad/scripts/package.py:549-579`, which judges the refs git is pushing from the pre-push hook's
   stdin (`dyad/hooks/pre-push:4`). It skips a deletion explicitly: `if set(local_sha) <= ZERO_SHA:
   continue  # a deletion carries no commit` (`package.py:563-564`, with `ZERO_SHA` at
   `package.py:547`). So even a *pushed* branch deletion is passed over by design, and none of these
   four deletions was pushed — all four branches stayed on `origin` or were local-only, so no hook
   ran at all. Git runs no hook on `git branch -D`. Reach: 0 of 4.
2. **A grep over `dyad/guards/` and `crafts/*/guards/`** for `branch -D`, `refs/heads` and
   `for-each-ref` returns one hit,
   `crafts/countersign/projectors/project_countersign.py:208`, which enumerates release tags in a
   projector. There is no guard over refs. `dyad check --list` prints 24 guards, every one over a
   store, a tracked tree or a commit range. Reach: 0 of 4.
3. **Rule-8's class, which does apply and was not followed.** A local-branch deletion is not a repo
   transaction (Rule-1's target is a commit or a PR) and is not read-only, so Rule-8's first trigger
   (`dyad/rules/RULE-8-host-mutation.md:23-24`) makes it a host action. By
   `crafts/sysadmin/rules/host-mutation.md:15-17` it is **reversible** when the commits are reachable
   elsewhere — row 67 states its own undo, `git branch dwork-sync-open 2f7d141` — and by
   `host-mutation.md:18-20` **destructive** when they are not, with "When in doubt, destructive" at
   line 20. On that reading all four rows are a reversible host action taken without the plan-`Y`
   that authorizes it (`RULE-8:38`). Moment: inference, stated. **Shipped** as Rule and craft-rule
   text, and it reached none of the four.
4. **The change-log row is missing in all four cases.** `workstation-corpus/CHANGELOG.md` holds no
   row naming #167, #133, #191, #194 or #199 for a branch deletion (grepped today). `RULE-8:58-59`
   makes a missing row for a known mutation a Rule-8 breach, so each of these four rows carries a
   second, unlogged breach — stated here as a finding of this audit, not corrected in it.
5. **The prose fence in the incident log** (row 77's "named in a plan or not done"). Moment:
   inference, at plan time. Not corpus content — it lives in a log cell, which is exactly the kind of
   mitigation `dyad/playbooks/incident-hardening.md` phase 2 forbids counting. It failed twice after
   being written (rows 80, 85).

## Remediation candidate, under attack
A `dyad/hooks/reference-transaction` hook — git's own hook for every ref update, which
`core.hooksPath dyad/hooks` already covers (set by the install, Rule-11 property 5). It returns 0
immediately unless the transaction deletes a ref under `refs/heads/` whose name is not `main`; for
such a deletion it appends the ref and sha to an untracked per-checkout log and refuses unless the
current d-work's plan file names the branch, or a typed opt-in is present. Moment: the instant the
ref is deleted, which is the only moment the act exists.

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | It adds a World dependency or a second install path. | refuted | Neither. Git is already kernel (`dyad/rules/RULE-14-system-infrastructure.md:34-37`; the manifest's Git row is `kernel`, `dyad/infrastructure/INFRASTRUCTURE.md:14`), `reference-transaction` has existed since git 2.28 and this host runs 2.53.0, and a new file under `dyad/hooks/` installs through the existing one distribution code path (Rule-11 property 5). No manifest row is added. Note in passing: the manifest records Git as "2.43.0 observed" against 2.53.0 live — a separate finding, not this mode's. |
| 2 | It fires on every ref update — every commit, fetch, reset and branch creation, three times per transaction (prepared, committed, aborted) with every ref on stdin. The `fail-loud check` term (vocabulary, Rule-12) says a check belongs "only at a strategic point … where control passes once per process or rarely, never per item". A hook on every ref update is per-item. | confirmed | The blanket form does not survive. Survivor: the hook reads stdin, returns 0 unless a line's new-value is all zeroes and its ref is `refs/heads/<not main>`, and does nothing else — a string test over a few lines, on a case that is rare by construction. |
| 3 | Prevention is forgeable by the mode it guards: an Agent under momentum that meets a refusal types the opt-in, which is attack 2 of `agent-corpus/audits/2026-09-22-incident-mode-a.md` applied here. | confirmed | Prevention does not survive; detection does. Survivor: the hook records every matching deletion to the per-checkout log unconditionally and refuses only when the plan does not name it, so a bypass is a typed opt-in leaving a trace rather than a silent sweep — and the trace is what a completion reply can cite. |
| 4 | Coverage against the rows. | survives | All eight branch names across the four rows match — `dwork-sync-open`, `dwork-133-plan-y`, `dwork-191-rev2`, `dwork-prov-plan`, `dwork-prov`, `dwork-191-plan-y`, `dwork-open`, `ledger-198-open` — and none is `main`. Reach: 4 of 4, the only candidate in this exercise's seven modes that reaches every row of its mode. |
| 5 | Easy agreement (Rule-9 Conditions): this candidate read as right on first sight, so attack its standing. Rule-1's Enforcement names `pre-commit` and `pre-push` as "the only *blocking* enforcement of Rule-1" until d-work #24 (`dyad/rules/RULE-1-containment.md:47-52`); a third blocking local hook changes that sentence, so this is a Rule-1 d-work with a falsification record, not a plain agent-zone PR. | survives (scoped) | Admissible at a stated price: the Rule-1 amendment is named in the plan rather than discovered during execution — which is mode K's own mechanism, and naming it here is how this record avoids it. |
| 6 | The untracked per-checkout log is new instance state and a new store, which Rule-16's store pattern and Rule-12 property 1 both price. | survives (scoped) | Only by reusing an existing shape rather than inventing one: the `suite memo` (vocabulary, Rule-12) is already a per-checkout file under the git common dir, shared by every worktree and never tracked. The deletion log takes that shape, so no tracked store and no new guard appear. |

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** The row would read: *add
`dyad/hooks/reference-transaction` — returning 0 unless the transaction deletes a `refs/heads/` ref
other than `main`, in which case it records the ref and sha to an untracked per-checkout log (the
suite-memo shape) and refuses unless the d-work's plan file names the branch or a typed opt-in is
given — and amend Rule-1's Enforcement sentence, which today names `pre-commit` and `pre-push` as
the only blocking local hooks.* It would have caught all four rows (67, 77, 80, 85), and it would
also have given the four missing change-log rows (`RULE-8:58-59`) something to be written from.

Why not exit 1: nothing mechanical reaches this mode today, and `pushed_refs` passes over a deletion
by design (`package.py:563-564`). Why not exit 3: neither Rule applies — the fault is not in a hosted
service (Rule-14 property 2), and "is this branch named in the plan?" is decided by reading the plan
file, not by a judgment Rule-5's Enforcement puts beyond a script. Proposed only — the Agent never
opens the row (Rule-3, Scope) and never closes the mode.
