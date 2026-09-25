# Falsification record — Rule-1 (containment)

**Claim (operator, 2026-09-12):** `agent-corpus` and `workstation-corpus` are contained;
containment is enforced when mutating the repo; mutations to each are independent
transactions (commits and PRs); honored by agent inference and enforced via CI.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Enforced via CI" — repo is private on a free plan; branch protection/rulesets return 403. CI cannot block a merge. | **Refuted as stated** | Enforcement point = versioned pre-commit hook (`core.hooksPath=.githooks`). CI = independent detector. Becomes blocking if repo goes public or plan upgrades. |
| 2 | Two zones leave root/CI files unclassifiable; a corpus change could ride along with a CI change. | Refuted | Third zone `infra`, fixed allowlist, equally isolated. Unclassified paths fail. |
| 3 | "Commits and PRs" — per-commit-clean commits can still span zones across a PR. | Refuted | Check each non-merge commit **and** the PR's whole diff. |
| 4 | Cross-zone references (agent cites workstation paths) break atomically on rename. | Survives as accepted cost | Ordering rule: referent first, referrer second. Transient dangling link tolerated. |
| 5 | Bootstrap violates itself (move + checker in one commit). | Refuted | Three stacked PRs, one per zone. Merge order: workstation → infra → agent. |
| 6 | Agent memory (`~/.claude`) is outside the corpus and unversioned. | Survives, scoped | Repo `agent-corpus/` canonical; memory is a cache. |
| 7 | Checker self-test: cross-zone stage, unclassified add, stacked range, tree on old main. | Passed | See commit adding `.github/scripts/containment.sh`. |
| 8 | Bootstrap execution: `gh pr merge --delete-branch` on the bottom of a stacked PR chain. GitHub closed the next PR (base gone) and the third merged into the infra branch — a cross-zone branch. | Refuted (agent error) | Merge stacked PRs bottom-up; delete branches only after the top merges. Recovered by resetting branches to single commits and re-opening (#4, #5). |
| 9 | Checkout lives on NTFS (`core.fileMode=false`): `+x` never recorded. CI exited 126, and git silently skips a non-executable hook on POSIX checkouts — the enforcement point was hollow. | Refuted (platform) | `git update-index --chmod=+x` on script and hook (#6). CI detector caught what the hook could not. |

Disposition: see ledger #10 (done 2026-09-12; PRs #1, #4, #5, #6).

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/containment.py` → `dyad/guards/infra/containment.py` (the zone guard, placed by Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #154 (2026-09-14, craft reframe)
A fifth zone, `craft` (`crafts/*`), declared in `ZONES` and in the Rule; no path yet matches it.
| # | attack | result | survivor |
|---|---|---|---|
| 10 | The `craft` zone is premature: no `crafts/` path exists before #155; a zone claiming nothing is dead data. | Survives, scoped | A zone is a claim over paths, not a directory; `classify` is pure and the test proves the claim (`test_globs`, `test_craft_zone_never_mixes_with_instance`). Declaring it here means #155's first `crafts/` commit is already classified; otherwise #155 would change the zone table and add craft files in one PR — cross-zone. Same bootstrap order as attack 5: checker before content. |
| 11 | Rule text (agent zone) cites `crafts/<craft>/` before any craft exists — a dangling referent (attack 4). | Survives, scoped | The referent is a pattern, not a file; `references.py` resolves backticked `dyad/…` paths only, so nothing fails. A resolver for craft paths is #156's `craft check`. |
| 12 | Add `crafts/README.md` so the zone is visibly real. | Refuted | Craft-zone file carrying no craft; an instance-side note #143 C6's registry row owns. Declared-only until #155 creates `crafts/sysadmin/`. |

Pairwise: Rule-1 gains a zone, its own concern; 1–11: Rule-11 governs a craft's tree, Rule-1 the
zone its transactions stay in — one-way, named in both Boundaries. No other Rule's concern moves.
Coherent, orthogonal.

Disposition: see ledger #154.

## Amendment — d-work #166 (2026-09-14, a push range is not a transaction)
Attack 3 above ("check each non-merge commit **and** the PR's whole diff") is **scoped, not
refuted**: it is true of a PR and false of a push. `check_transaction` (the pre-push path,
`dyad check --guards` over `origin/main..HEAD`) ran the whole-diff check and so refused a push of
four stacked single-zone branches in #155 — a correct state the guard called wrong. Split:
`check_commits` (mode `commits`, the push), `check_range` (mode `range`, unchanged: the commits and
the whole diff), `check_transaction` → commits, a new optional `check_pr` → range, run by
`dyad check --pr <base> <head>`; the mode that ran is printed.
| # | attack | result | survivor |
|---|---|---|---|
| 13 | Dropping the whole-diff check from the push path lets a mixed commit through. | Refuted | Commits mode checks every non-merge commit of the range; a commit touching two zones fails there as before (`test_mixed_commit_fails_in_both_modes`: same commit, both modes, both fail). |
| 14 | A PR whose commits are each single-zone but whose diff spans two zones now merges unchecked — attack 3 re-opened. | **Confirmed; open exposure, not closed here** | True since #168 removed the `pull_request` trigger, not since this change: the runner of the whole-diff check on a PR was that wrapper. Pre-merge the check is now `dyad check --pr <base> <head>` — mechanical, reproducible on the same head, and run by the Agent (conduct), never a gate. Post-merge `dyad-containment.yml` still runs `range` over what landed on `main`, detecting. Making it a gate again (the receiver judging a `pull_request` webhook, or `check --pr` inside the merge-evidence block) is a later d-work; stated in the Rule rather than implied by a green check. |
| 15 | `check_pr` widens the guard contract; every guard now owes a third function. | Refuted | Optional, discovered by `getattr`; `dyadlib.CONTRACT` / `contract_problem` unchanged, so `agent/rows`, `agent/prs` and `sysadmin/events` are still called through `check_transaction`. Follow-up (craft zone, one line): `crafts/sysarch/rules/guards.md` p3 gains "may provide `check_pr`" beside "may provide `summary(root)`". |
| 16 | The Rule needed no edit: its Target already said "a commit or a PR". | Survives, scoped | The Target did; the Conditions did not — one trigger named a CI wrapper that has not existed since #168. The edit corrects the triggers and names each runner and its mode; Intent and Target untouched. |
| 17 | Two modes hide that the whole-diff check uses `base...head` (merge-base) while the push path uses `base..head`. | Refuted | Both keep their form and `containment.MODES` states each in one line, printed by the CLI (`containment OK [commits]`). |
| 18 | The fix should also switch `dyad-containment.yml` (push to `main`) to commits mode, since a push to `main` is not a PR either. | Refuted | That workflow's range over `before..sha` is the last automatic whole-diff check in the system; switching it would delete the only mechanical catch for attack 14. It stays `range`, detecting, and its rare false refusal (two merges in one push) is accepted, named here. Infra zone in any case: a separate PR if ever wanted. |

Pairwise: Rule-1 keeps its concern (which paths a transaction may touch); Rule-14 p3 owns the
kernel-only path that runs the guard — what it checks changed, not who owns it; Rule-3's plan gate
(`agent/prs`) is unchanged and simply also runs in the new PR command; Rule-11 owns the runner,
which gains a subcommand and no check semantics (S4); Rule-12: the new code enters with its tests.
No other Rule's concern moves. Coherent, orthogonal.

Disposition: see ledger #166.

## Amendment — d-work #23 (2026-09-16, an outside fence, and a hook that cannot run)
Two additions, both from #22's execution: a session-level branch restriction collided with the
ledger-only push to `main` that Rule-2 and Rule-3 prescribe, and the pre-commit hook on `main`
could not execute at all (`dyad/guards/infra/containment.py` at mode 100644 since #6, while the
hook execs it by path).
| # | attack | result | survivor |
|---|---|---|---|
| 19 | There was a conflict between Rules to resolve. | Refuted | None: Rule-2 permits the ledger-only push, Rule-3 prescribes it, and `prs.py` reads cited rows *at the base* while returning `[]` on `main` — so the direct push is what makes the plan gate satisfiable at all. Observed both ways on one branch: `#22 not in ledger` before the ledger commit landed, clean after. The collision was with a fence outside the corpus, which no Rule but Rule-8 (host actions) had named. |
| 20 | The bullet imports a harness concept into the corpus, which Rule-11 keeps out. | Refuted | It names a *class* of Operator-side fence, never a harness or its wording, and mirrors a sentence Rule-8 already carries. A receiving system with no such fence reads a bullet that never fires. |
| 21 | The bullet decides nothing, so it earns no text. | Survives, scoped | It does not decide; it tells the Agent which layer it is in, which is what was missing. The decision procedure that follows — escalate where the costs are asymmetric — is conduct, deliberately unencoded. |
| 22 | The vacuous-hook sentence blesses `--no-verify`, which INCIDENTS treats as serious. | Survives, scoped | The #3 incident was a `--no-verify` *push* withdrawn with no compensating check. This permits it only where the hook physically cannot run, only with the same guard run by hand and its output in the commit message, only as a reported incident; a hook that runs and fails is still absolute. |
| 23 | The Agent should have chmod'ed the file instead. | Refuted | That edits a file of another d-work's diff from inside an unrelated one, silently reversing #6's intent, and `core.fileMode` is `true` here so it would have been staged. The repair is its own row. |

Pairwise: Rule-1 keeps its concern — which paths a transaction may touch. Rule-8 keeps the
harness permission mode per command; this is the same shape over repo transactions, so the pair
is parallel, not shared: neither owns the other's target. Rule-2 and Rule-3 are cited as the
prescription the fence can collide with; their ownership of the ledger-only push is untouched.
Rule-3 keeps incidents (the report this sentence requires is Rule-3's form). Rule-11 owns the
runner, Rule-12 the check a guard carries, Rule-14 the kernel-only path — none moves. No new term
(Rule-6). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #23.

## Amendment — d-work #24 (2026-09-16, the exec bit was never the Agent's to restore)
#23 left Rule-1's enforcement vacuous and its repair to this row. Reproduced first: staging a file
and running `dyad/hooks/pre-commit` gives `Permission denied`, exit 126.
| # | attack | result | survivor |
|---|---|---|---|
| 24 | Restore `+x` on `dyad/guards/infra/containment.py`; the hook is fine. | Refuted | `crafts/syseng/guards/naming_rules.txt` grants 100755 to four path classes only — `dyad/bin/*`, `dyad/hooks/*`, craft `templates/*.sh` and `server/*.sh` — and every tracked `.py` in the tree is 644 by that rule. #6 swept the modes to match it and was right. Restoring the bit carves a one-file exception into an Operator-tended rule and leaves every other guard module the same trap; with `core.fileMode` true it also stages itself from any checkout that carries the bit. |
| 25 | Then the hook is the bug — but which form? | Refuted (the question answers itself) | `dyad/hooks/pre-push` already calls its module through the interpreter. `pre-commit` gains the same form, and then depends on no file mode at all: the failure mode is removed, not detected. |
| 26 | Rule-1's own prose is a documentation nit, out of scope. | Refuted | Line 30 is an imperative a reader follows — "print it with `…containment.py zones`" — and it fails identically. Same gap, same d-work, one word. |
| 27 | Add a guard so no hook can ever exec a 644 path. | Survives, scoped — deferred | Real, but it can only catch a *future third hook*: after this fix no existing hook depends on a mode. It is syseng-craft code in a second zone and a second PR; proposed as a backlog row rather than bolted to a one-line repair (Rule-12: never widen the plan). |
| 28 | A `.py` in this flow should gain a run-time invariant (Operator, #25). | **Confirmed, and not here** | This d-work touches no `.py` at all, so nothing is skipped; and the fact it turns on — a hook not invoking a path the mode rules keep at 644 — is about tracked files and index modes, which `crafts/syseng/rules/invariants.md` p1 puts out of bounds ("never over the instance corpus"). But the flow *does* expose an invariant-shaped gap one level down, which #25 plans: the verb the hook passes, `staged`, lives in a dict literal inside `containment.main()`, so no constant names it and no invariant covers it, while its sibling `MODES` is covered by `modes-declared-and-distinct`. |

Pairwise: Rule-1 keeps its concern and gains no new one — the Enforcement sentence #23 added is
unchanged and now describes a state this repo is no longer in. The mode rules stay the syseng
craft's (`naming_rules.txt`), read here and never restated; Rule-11 keeps the hook's ship path and
the install that sets `core.hooksPath`; Rule-12 keeps the check a module carries, and #25 carries the
invariant this flow argues for. Rule-3's incident form is untouched. No new term (Rule-6). Others
unchanged. Coherent, orthogonal.

Disposition: see ledger #24.

## Amendment — d-work #152 (2026-09-25, `.claude/` belongs to the infra zone)
`.claude/` was claimed by no zone, so a committed slash command (`.claude/commands/*.md`) or
project Skill was an unclassified path Rule-1 forbids — `agent-corpus/falsification/playbook-vs-skill.md`
attack 4, blocking once #152 ships command adapters. `ZONES` gains `("infra", ".claude/*")`; the
Rule's text names no infra path (the table is `containment.py`'s alone) and is not edited.
| # | attack | result | survivor |
|---|---|---|---|
| 29 | `.claude/` is craft content (it carries play-book entry points), so it belongs in `agent` or `craft`, not `infra`. | Refuted | It holds harness configuration of one kernel — a library adapter (Rule-14), not System content — exactly as the root `CLAUDE.md`, the host frame, already is `infra`. A command changes with its harness, never with a Rule; `test_claude_adapter_rides_with_host_frame` keeps it in one transaction with `CLAUDE.md`. |
| 30 | Classifying `.claude/*` lets local settings and credentials (`settings.local.json`) be committed. | Survives, scoped | A zone classifies a path; it never decides whether the path is tracked. Before this a secret there failed only as *unclassified*, never as a secret — no protection was lost. The credential scan (Rule-7 property 2) covers provenance bodies only. Follow-up, infra zone: `.gitignore` gains `.claude/settings.local.json` (per-machine, as `~/.claude` is, attack 6); not in this PR — one zone, and `.gitignore` is seeded by `hostadapter.write_gitignore` from `package_rules.txt`, so the durable fix is there. |
| 31 | An adapter in `.claude/` duplicates `dyad/playbooks/` and splits the procedure's home. | Refuted | Per `playbook-vs-skill.md` attack 7's survivor: the adapter only invokes the play-book, never *is* it; the procedure stays agent zone, and `test_claude_adapter_never_mixes_with_package` makes the two separate transactions — referent (`dyad/…`) before referrer (`.claude/…`), attack 4. |
| 32 | Every installed system inherits a zone change it did not ask for. | Refuted | A core-only install gains one classification and nothing else: a tree with no `.claude/` path is unchanged, and one that had tracked it was already failing `tree` as unclassified. Invariants hold (`zone-patterns-disjoint`: `.claude/*` matches no other pattern; `test_invariants_hold`). |

Pairwise: Rule-1 keeps its concern — which paths a transaction may touch — and gains one row of its
own table. Rule-14 keeps whether the harness is a kernel or library row; Rule-7 keeps the credential
scan; Rule-11 keeps the install and the seeded `.gitignore`; Rule-12: the row enters with its tests.
No new term (Rule-6). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #152.
