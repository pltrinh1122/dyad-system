# Incident mode E — an instrument narrower than the question

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10, 4 of 140 rows.*

## Definition
The mechanism: the instrument the Agent used to answer a question could not, by construction,
express the answer — a search pattern that cannot match the form actually present, an exit code
taken from a pipeline rather than from the command inside it, an error-handling setting placed
where it does not fire, a filter whose cases do not cover what the command prints. The object read
is the right one and the reading apparatus is short of the question; the instrument's silence is
then read as a negative and its zero exit as a success. The fault is invisible from the output,
because the output is exactly what a true answer would also have looked like.

**What would have to change.** Every success and every negative must be taken from the thing's own
result, and an instrument must be shown able to produce the positive — a positive control — before
its absence is read as one.

Boundaries against the neighbours it is most easily confused with:
- **D, the wrong object read** — the test is whether the object or the apparatus was wrong. D's
  instrument worked and pointed at something else; E's instrument pointed at the right thing and
  could not say. The two sit side by side inside one d-work, which is the boundary: row 100 (D, a
  sound search over the wrong branch of the right repository) and row 102 (E, one grep pattern over
  the right repository that could not match `git -c credential.helper= push`).
- **C, a value stated from memory or a digest** — C read nothing at the moment of use; E read, with
  an instrument that could not answer. The boundary row is row 8 (C): a failure count taken off a
  summary line already printed, where row 124 (E) is a fresh run whose output was filtered past the
  errors. They meet in one place in the code — `package.py:233` and `:442`, the two lines that print
  only the last stderr line, which is how E's narrow run manufactures C's digest.
- **R, a derived key that does not identify** — R is the code's own version of this family: a
  module's own pattern or key fails to match or fails to identify, on every run, with no party
  reading anything. E is the Agent's own instrument, composed in the moment. Boundary pair: row 102
  (E, the Agent's grep pattern) and row 99 (R, `dyadlib.tables` splitting a cell on a separator
  inside it, `dyadlib.py:489-492`).
- **G, a flag taken as a positional argument** — G's command was mis-typed and the tool said so or
  silently did something else; E's command was well-formed and the *reading* of its result was
  short. Row 49 carries both: `git cherry-pick -q` is a G-shaped mis-flag, and it is filed E here
  because the mechanism that *started* it is `set -e` not firing for a command inside an `&&` list,
  which is why ten failures ran silently to the end instead of one stopping the loop (phase 1: the
  mechanism that started it is primary, the other secondary).
- **T, a stale or partial view of shared state** — T's instrument read a real but older state; E's
  read the current state and could not express part of it.

## Incidents (4)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-22 | #116–#125 | a loop meant to rebuild ten branches on their pushed heads ran `git reset --hard` on all ten and then failed to re-apply the rename commit on each | `set -e` does not fire for a command inside an `&&` list unless it is the last, so a cherry-pick dying on every iteration let the loop run silently to the end |
| 2026-10-05 | #221 | plan #221 revision 1 asserted as verified that nothing in that repository commits or pushes the bus; one Operator-run script does both | the negative came from one grep pattern that could not match the script's actual form, and the absence of output was read as the absence of the thing rather than the limit of the pattern |
| 2026-10-07 | #231 | two ledger pushes were written as `git push` piped into a tail, chained to an echo, which printed PUSH OK after git had rejected the push | the pipeline's exit code hid the push's own; tail exits 0 on a rejection's hint lines, and no PIPESTATUS check or status read followed |
| 2026-10-09 | #256 | the ERROR text of 29 suite errors was never captured; the push output was read through a case-sensitive grep alternation that matched only the summary line | a command's output read through a filter whose cases do not cover what the command prints; second occurrence of filter-masks-output, the first with a case-sensitive pattern |

## Pattern
All four are the Agent's own shell, typed in the moment, and in all four the apparatus was
*composed* rather than chosen: a loop with an `&&` list, a grep alternation, a pipe into tail, a
single pattern standing in for a search. None is an ops script, none is package code, and none ran
through any verb the dyad ships — which is the single fact that decides this mode's whole
mitigation inventory, because every shipped fence in the vicinity governs a file class or a moment
these four are outside of.

Two sub-shapes: rows 49 and 98 take a *success* from the wrong place (an `&&` list's last command,
a pipeline's exit code); rows 102 and 124 take a *negative* from the wrong place (an unmatched
pattern, a filter's uncovered cases). The second pair is the one that produced a false statement:
row 102's wrong negative stood in a stored plan file and in a reply for one turn, and row 124's
destroyed the only evidence that would have identified a cause — "the one piece of evidence that
would have identified the cause is gone, which is why the row above states no cause."

Recurrence against the mitigations a consequence cell describes:
- Row 98's consequence names the conduct adopted — "every later push in this d-work was followed by
  `git status -sb` as the check" — and states the durable fix as conduct: "The durable fix is not to
  pipe a push through `tail` at all". Row 124 post-dates it by two days and two ledger ids, and its
  own cause cell cites row 98 by line as the same mechanism: "second occurrence of
  filter-masks-output".
- Row 102's consequence names the correction in plan #221 revision 2, before any plan-`Y`. Rows 98
  and 124 post-date it and are the success-side and negative-side of the same shape.
- No consequence cell of this mode names a mechanism that was built. Row 124's names one still
  owed: "the capture is owed by the candidate row named there."

## Mitigations (phase 2)

**1. The ops-script strictness requirement.** `crafts/sysadmin/rules/ops-scripts.md:14` ("first line
`#!/usr/bin/env bash`, then `set -euo pipefail`") and `:27`, enforced by
`crafts/sysadmin/guards/ops_scripts.py:33`, `STRICT = "set -euo pipefail"`, per its docstring at
`:8`; seeded by `crafts/sysadmin/templates/ops-script.sh:8`. Fires at `package.py check` as
`sysadmin/ops_scripts`, in Rule-11's runner and on the kernel-only path. **Shipped.** Reaches **none
of this mode's four rows.** All four are inline Bash the Agent ran for itself, and Rule-18's own
Boundaries scope the ops script to "a command the Operator runs on the Agent's behalf"; its Conduct
clause ("Never an inline block") binds only commands the Operator is asked to run. The syseng craft
states the limit of the setting itself at `crafts/syseng/rules/idempotence.md:25`: "(d) `set -euo
pipefail` stays; it orders, it does not skip — the guards do". Row 49's `set -e` fault is exactly a
case this requirement would not have caught anyway, because `pipefail` and `-e` do not fire inside
an `&&` list.

**2. The pre-push hook's unmediated exit code.** `dyad/hooks/pre-push:4`: `exec
"$(git rev-parse --show-toplevel)/dyad/bin/dyad-python" ".../package.py" check --guards --pre-push`
— `exec`, with no pipeline between the guards and git, so the guards' own status is the push's.
Fires at every push. **Shipped.** Reaches row 98's *consequence* and not its act: the hook governs
the push git performs, while row 98's fault is the Agent reading its own `git push` through a tail
and an `&&`, which the hook cannot see and which ran after the hook had already passed. Reaches
rows 49, 102, 124 not at all.

**3. The suite runner's own output reduction.** `dyad/scripts/package.py:409-417` (`run_suite`),
`:216-236` (`check_rule_12`) and `:419-445` (`cmd_tests`). The child's full stderr is captured
(`subprocess.run(..., capture_output=True)`, `:414`, `:227`) and returned (`:417`), then reduced to
lines beginning `Ran `, `OK` or `FAILED` (`:416`, `:230`); on failure the caller prints exactly one
line — `r.stderr.strip().splitlines()[-1]` at `:233`, `err.strip().splitlines()[-1]` at `:442`.
Fires in Rule-11's runner, at `dyad check --tests`, and at `dyad check --guards --pre-push`.
**Shipped — and it is itself an instrument narrower than the question.** It reaches row 124 as that
row's actual mechanism: the last line of a failing `unittest` run is `FAILED (errors=29)`, and the
29 `ERROR:` blocks above it are discarded inside `package.py` before any grep of the Agent's could
have matched them. Row 124's cause cell blames the Agent's `grep -E`; read from the code, the text
was already gone.

**4. Rule-12 property 2's suite memo.** `dyad/scripts/package.py:238-250` and `suite_memo_clause`,
consulted only under `pre_push` (`:361-364`) and "never by `check --evidence`" (`:347-348`); written
only after a full all-roots pass on an unmoved tree (`:225`, `:234-235`). Fires at pre-push.
**Shipped**, and it reaches row 124 **adversely**: it is the mechanism that made the failure
unreachable once a tree had passed, which the row records — "a suite memo had made the failure
unreachable without deleting the memo, which no plan authorized". Not a mitigation of the mode; a
multiplier of the cost of one instance of it.

**5. Rule-3's completion-evidence clause** — "each check's result as observed, never assumed"
(`dyad/rules/RULE-3-d-work.md`, Completion counter-prompt) — and Rule-14 property 3's evidence block
(`package.py:693-708`), which runs the checks itself rather than reading any report of them. Fires:
**inference, stated**, at the completion reply. This is the obligation all four rows breached and
the only mitigation that reaches any of them at its own moment.

**For this mode the only mitigation that fires at the moment the fault occurs is inference,
stated.** Of the four shipped mechanisms above, one governs a file class none of the rows belong to,
one governs a moment after the reading, and two are themselves narrow instruments that rows of this
mode were caught by rather than caught with.

## Remediation candidate, under attack
One fence: **persist the failing suite's own output.** In `run_suite`
(`dyad/scripts/package.py:409-417`), when the child's return code is non-zero, write `r.stderr`
whole to `<git common dir>/dyad-suite-fail/<root-slug>.log` — the same home and the same lifetime as
the suite memo (`:238-243`: "One file per key under `<git common dir>/dyad-suite-memo/`, so every
worktree of the checkout shares it; never tracked") — and have the two callers print that path
beside the one summary line they already print (`check_rule_12:233`, `cmd_tests:442`). Fires wherever
the suite runs: Rule-11's runner, `dyad check --tests`, and `dyad check --guards --pre-push`. Three
lines in one function, on the one code path Rule-12 property 2 already requires every run to use.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The text was never lost: the Bash tool returns the child's stderr, so this fixes a logging gap the Agent could have closed by reading its own tool output. Nothing in `package.py` needed changing. | refuted | Reading `:227-233`: the child's stderr is captured by `subprocess.run(capture_output=True)` *inside* `package.py` and is never written to any stream the caller sees — only the `Ran`/`OK`/`FAILED` summary and `splitlines()[-1]` reach stdout and stderr. Row 124's "the `ERROR:` text of those 29 errors was never captured" is the code's behaviour, not a lapse of the Agent's logging. Rule-9 easy agreement: this is the attack pushed to a verdict before the candidate was accepted. |
| 2 | Coverage: 1 of 4 rows. Rows 49, 98 and 102 are the Agent's own shell — a loop, a pipe into tail, a grep — which no package code touches and no guard can reach. | confirmed | Survives only as a partial, named as such. The general form (a positive control before a negative is believed) stays inference: Rule-5's Enforcement states the shape of that limit for judgments no script can decide, and nothing in the kernel observes a command the Agent types. |
| 3 | New untracked state outside the repository carries Rule-11 property 6 (a generated file is never tracked) and, if anything new writes it, a Rule-14 manifest row. | survives, scoped | Scoped to the suite memo's own home under `<git common dir>` and to `pathlib`/`subprocess`, already imported and already declared — no new component, no tracked path, and a `SUITE_MEMO_KEEP`-style cap (`:245`) so the directory cannot grow without bound. |
| 4 | It makes the evidence block non-deterministic, and `:230` says in terms that the block must be deterministic (timings are stripped for exactly that reason). | refuted | The path is printed only by the failure message, and `cmd_evidence` (`:693-708`) returns non-zero whenever that fires, so no merge evidence is ever pasted from a run that printed it (Rule-2 Binding admits only observed passes). On a passing run nothing is written and nothing printed. |
| 5 | It rewards the wrong habit: the real fault is reading any run through a filter, and giving the filter a better corpus to miss does not change that. | survives, scoped | Conceded as stated: the candidate does not teach the habit. What it buys is that the one artifact that identifies a cause survives the run, so the next occurrence of the habit is recoverable instead of terminal — which is precisely what row 124 lost and what its consequence cell says is owed. |

Read together: as a remedy for mode E the candidate does not survive — attack 2 holds without
reconciliation, and three of four rows are in a place no mechanism reaches. What survives is that
one shipped instrument found by reading the code is narrower than the question it answers, and can
be widened for the price of three lines.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build** (exit 2), proposed only. What the row would say: on a
non-zero suite child, `run_suite` writes the child's whole stderr beside the suite memo under
`<git common dir>/dyad-suite-fail/`, capped as the memo is, and `check_rule_12`/`cmd_tests` print
that path beside the summary line — so a suite failure's own text survives the run that produced it
and a memoized tree cannot make it unreachable. Which row it would have caught: 124, and only that
one. Rows 49, 98 and 102 hold none of the three exits and stay open as conduct: the Agent's own
shell is outside every guard in the tree, and "unfenceable on this kernel" would be an overreach
here, because Rule-14 property 2 bounds what the *kernel* contains and says nothing about what the
Agent types — the honest statement is that no fence has been found, not that none can exist. The
mode therefore stays **open** in the index, and the Agent neither closes it nor asserts it addressed
(play-book Conduct, Rule-2).
