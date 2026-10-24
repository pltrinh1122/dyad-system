# Incident mode N — a target named by an ambiguous pattern

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 3 of 140 rows.*

## Definition
A command's target is given as a name or a pattern that the tool resolves against a wider set than
the author had enumerated: a bare `main` that git resolves to an abandoned local ref rather than the
remote's, and a `-f` process pattern that matches the matching process's own command line. The
author's mental model of the resolution set and the tool's actual one differ, and the command runs
against the tool's.

**What would have to change.** The target would have to be spelled unambiguously at the point of use
— a fully qualified ref, a pid — rather than named by a pattern whose resolution set the author has
not enumerated.

Boundaries against the neighbours it is most easily confused with:
- **O, a git write used as a read** — row 44 (`git checkout main -- .`) sits on the boundary and is
  assigned here. Separating test: remove the ambiguity and does the fault go away? With
  `origin/main` spelled, row 44 becomes row 5 — a bounded overwrite of a merged branch with newer
  content, caught by `git status`. With the bare name, it rewrote 156 tracked files to a 328-commit-old
  state, `dyad/VERSION` reading back `0.5.0`. The ambiguity set the scale, so it is primary and the
  write-used-as-read is secondary. In O's three rows there is no ambiguity to remove: the ref was
  exactly the one meant and the verb was wrong. O's record states the same split from its side.
- **T, a stale or partial view of shared state** — row 44 is staleness too, but every T row is a view
  of state shared with a peer session or the remote. Separating test: would `git fetch` have fixed
  it? T yes; row 44 no — the stale `main` was this session's own abandoned ref, which no fetch
  updates, and the remedy was `git branch -D main`.
- **D, the wrong object read** — D reads a different object and reports from it. Separating test: was
  anything mutated or blocked? N yes in all three (a tree rewritten, a shell killed, two loops
  hung); D's damage is confined to what was concluded.
- **R, a derived key that does not identify** — R's key is computed and fails to identify a record in
  one of the dyad's own stores. Separating test: whose namespace? R the dyad's; N an external tool's
  (git refs, the process table).

## Incidents (3)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-22 | #110 | `git checkout main -- .` restored 156 tracked files to a stale local branch's state in index and working tree | the bare name resolved to a local `main` 328 commits behind, not to the `origin/main` intended |
| 2026-09-24 | #155 | a `pkill -9 -f 'package.py check'` matched the running Bash command's own line and killed the shell before its chained edit ran | the pattern given to `-f` appeared verbatim in the command invoking it, so the command was its own match |
| 2026-09-25 | #161 | two measurement passes queued behind an `until ! pgrep -f` loop naming both scripts waited forever; neither pass ran | each waiting command's own line contained the pattern it grepped for, so each matched itself |

## Pattern
Three faults in two namespaces. Row 44 is git's ref namespace; rows 54 and 56 are the process table,
and 56 is 54's mechanism exactly, one day later, broadened from `pkill` to `pgrep`. Row 56's cause
cell names the generalisation the earlier row missed: "The rule was recorded as being about
`pkill`; it is about any `-f` process match whose pattern is visible in the matching process's own
command line." All three were caught by the Agent — by `git status` before any commit (44), by
missing output and an unchanged file (54), by an output file that stayed empty (56) — and none had
any corpus effect.

Recurrence evidence. Every mitigation a consequence cell describes is prose in the log itself: row
44's "this repo's own local `main` ref is not kept current and must never be used bare —
`origin/main` (or an explicit sha) only", and row 54's "a `pkill -f <pattern>` never shares a
command line with the pattern it matches". Row 56 post-dates row 54's prose by one day and is the
same mechanism; it is the recurrence. Row 44 also produced one concrete, narrow mitigation — the
stale ref was deleted (`git branch -D main`) "so the same name cannot resolve to it again" — which
fences one name in one checkout and not the mode.

## Mitigations (phase 2)
**There is no mechanism at all for this mode.** Verified rather than asserted: `dyad check --list`
prints 24 registered guards (`agent/frame` through `syseng/tests`), and every one of them reads a
store, a tracked tree or a commit range — none reads a shell command line before it runs, and a
grep over `dyad/guards/` and `crafts/*/guards/` for `branch -D`, `refs/heads` and `for-each-ref`
returns one hit, `crafts/countersign/projectors/project_countersign.py:208`, which enumerates
release tags in a projector and is not a guard over commands.

What carries the conduct instead:
1. **Rule-8's first trigger** — `dyad/rules/RULE-8-host-mutation.md:23-24`: anything the Agent runs
   on the machine that is neither a repo transaction nor read-only is a host action. Moment:
   inference, stated. All three commands qualify: `git checkout … -- .` writes the tree, `pkill -9`
   signals a process, and the `until` loop is read-only but blocking.
2. **The class table** — `crafts/sysadmin/rules/host-mutation.md:13-20`, with "When in doubt,
   destructive" at line 20. Moment: inference, stated, in the plan that names the action
   (`RULE-8:38` for reversible, `RULE-8:39-40` for destructive). Reach: row 44's command is
   reversible with a stated undo (`git restore --source=HEAD --staged --worktree -- .`, which is
   what was used); row 54's `pkill -9` has no undo and loses the process's remaining work, which is
   destructive by that table and so needed its own counter-prompt. Neither row carries a plan item
   or a counter-prompt for the command, and Rule-8's Enforcement is "Inference only, stated"
   (`RULE-8:58`), so nothing was going to notice.
3. **No change-log row exists for any of the three.** `workstation-corpus/CHANGELOG.md` holds no row
   naming #110, #155 or #161 for these commands (grepped today). By `RULE-8:58-59` a missing row for
   a known mutation is itself a Rule-8 breach; stated here as a finding of this audit, not corrected
   in it.

## Remediation candidate, under attack
One candidate, one moment: a harness-side deny rule (the Operator-side fence outside the corpus that
`dyad/rules/RULE-8-host-mutation.md:19-21` and `RULE-1:28-33` both name) firing at the moment a tool
call is issued, before the command runs, on two conjunctions — a `-f` process pattern that also
appears literally in the command line carrying it, and a `git checkout`/`git reset` naming a
non-`origin`, non-sha ref with a pathspec.

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | It is not the dyad's fence. `RULE-8:19-21` calls the harness permission mode "an Operator-side fence outside the corpus, per command; it neither replaces nor is replaced by this Rule" — so the core craft cannot ship it, Rule-12 property 1 cannot test it, and a completion reply cannot cite it as a guard result. | confirmed | "A fence the dyad builds" does not survive. What survives is a fence the Operator may set, proposed in this record and named in a row, with the corpus holding the proposal and not the mechanism. |
| 2 | Easy agreement (Rule-9 Conditions): a deny on `pkill -f` read as obviously right. But killing a runaway `package.py check` was row 54's actual and legitimate goal, and a refusal that must be routinely bypassed teaches bypass — the finding attack 5 of `agent-corpus/audits/2026-09-22-incident-mode-a.md` reached, and mode V's two rows are what bypass costs. | survives (scoped) | Only as a deny on the *conjunction* — a `-f` pattern that is a substring of the command line containing it — which is decidable by string containment and has no legitimate case, since such a command can only ever match itself. A deny on `pkill -f` as such does not survive. |
| 3 | Coverage: the conjunction test reaches rows 54 and 56 and nothing of row 44; a bare-ref test reaches row 44 and nothing of 54 and 56. One test does not reach three rows. | confirmed | A single fence does not survive. The mode is two mechanisms sharing one description, and the candidate is honestly two rules in one row — which the backlog row below says. |
| 4 | The bare-ref half already meets a fence of a shape nobody proposed: this session's own bash tool refused two commands today for naming git in a form it could not verify stayed inside the worktree (observed twice, live). So the moment exists and is enforceable there. | survives (scoped) | It shows the moment is real and already load-bearing; it does not show the moment catches a bare `main`, which it does not — both refusals were about argument *shape*, not ref resolution. The candidate is an addition at a proven moment, not a new moment. |
| 5 | A deny rule is per-machine and untracked, so it does not travel with the craft and a second system installing `dyad-operator` gets none of it — the opposite of Rule-11 property 2's "no clash on install", which is about what an install *writes*, and silent about what it cannot. | confirmed | The candidate does not survive as craft content. It survives as instance conduct with a corpus record: the mode record names the rule, and a system that wants it sets it, exactly as the harness permission mode already works. |

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** The row would read: *set a host-side deny rule on two
ambiguous-target conjunctions — a `-f` process pattern appearing literally in the command line that
carries it, and a `git checkout`/`git reset` with a pathspec naming a ref that is neither
`origin/…` nor a sha — firing at tool-call time, before the command runs; record the rule's text in
`workstation-corpus/` so the instance's fence is documented where its host facts live.* It would have
caught rows 54 and 56 on the first conjunction and row 44 on the second — 3 of 3, by two rules.

Stated against the exit, for the Operator to weigh: the fence lives outside the corpus by
`RULE-8:19-21`, so the row delivers a proposal and a record and never a guard, and no completion
evidence will ever cite it. Neither exit-3 Rule applies — the fault is not in a hosted service
(Rule-14 property 2) and is not a judgment no script can decide (Rule-5 Enforcement), since string
containment decides both halves. The Agent proposes the row; only an Operator prompt opens it
(Rule-3, Scope). Proposed only — the mode is not closed here.

## Delta 2026-10-24 (#259 revision 5; 3 → 4 rows)
**Row added:** 179 (#297: `check --tests test_incidents`, an under-qualified target loaded as a failing
test, the identifying stderr line never printed). **Mitigations re-read:** none; `cmd_tests` prints the
child's last stderr line only. **Exit:** exit 2 as proposed (#275 `backlog`); row 179's own reach is one
refusal in `cmd_tests`, which is `package.py`'s row rather than a host deny rule.
