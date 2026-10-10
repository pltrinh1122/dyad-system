# Incident mode I — verified in one environment, run in another

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10. 4 rows of 140.*

## Definition
The mechanism: a verdict was observed in whichever environment was at hand and then asserted of an
environment that differs in an input nothing had named — the working tree against the committed
tree, the disk bit against git's index mode, the authoring repo against a scratch install, a
hook-spawned run against a direct one. The observation was correct where it was made; what was
false was its scope.

**What would have to change.** Every environment difference that can change a verdict must be an
explicit input of whatever asserts or caches that verdict — a partition in the assertion, a key
part in the memo, the index read instead of the disk — so that a pass observed in one environment
can never stand for another.

Boundaries against the neighbours it is most easily confused with:
- **C, a value stated from memory or a digest instead of read from its source** — C read the wrong
  source, or none; I read the right source in the wrong place. Test: was the figure observed? Row
  83 is I because 31 *was* correctly counted in this repo and is simply not what the scratch
  install holds; a C row is one where nothing was counted.
- **D, the wrong object read** — D read a different object in the same environment; I read the same
  object in a different one. Test: hold the object fixed and change the environment — if the verdict
  moves, it is I.
- **U, the World moved** — U's environment changed under the Agent between two observations; I's two
  environments coexist and only one was ever looked at. Row 123 is I, not U: nothing in The World
  moved between the pre-push run and the direct run, they are two concurrent ways of running one
  tree.
- **W, the suite's environment leaked into the live repository** — W is a *write* into the other
  environment; I is a *verdict* about it. The two are the same `GIT_VARS` asymmetry seen from two
  sides: W's leak is closed at the spawn boundary, while row 123's suite-memo key still carries no
  part that distinguishes a hook run from a direct one.
- **T, a stale or partial view of shared state** — T is one environment seen late; I is two
  environments, one never seen.

## Incidents (4)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-15 | #17 | the new falsification-record file was uncommitted when the scratch-install suite first ran, and `agent/references` failed to resolve it from the scratch copy | `git add` came after that test run, not before: the verdict was taken on the working tree while the suite's second environment, the scratch copy, is built from the committed tree |
| 2026-09-16 | #6 | the mode correction set every `.py` to 644, including a module `dyad/hooks/pre-commit` then exec'd by path, so the hook dies in any fresh checkout | invisible on this mount, where every file reads executable; the row says so — the verdict was taken where the disk bit lies and asserted of a checkout where it does not |
| 2026-09-30 | #186 | the instruction told the drafter to raise a test floor to the live count, 31 here, where a fresh install yields 20 | no instance partition exists there at all; an assertion about "the live tree" written without asking which tree it runs in, and this suite runs in two; the clause being replaced was itself the reason the old floor was safe |
| 2026-10-09 | #256 | the pre-push gate refused three pushes with 29 errors while the same trees passed `dyad check --tests` and `check --evidence` on all six roots | **cause never established**, says the row: 23 of 624 tests did not run at all, the shape of a collection error, and the suite memo's key holds nothing that distinguishes a run under the hook from a direct one |

## Pattern
All four pit a verdict against an environment that differs in exactly one unnamed input: the commit
boundary (row 19), the filesystem's mode semantics (row 26), the instance partition (row 83), the
hook's own process environment (row 123). Three of the four were detected by running the other
environment — the scratch suite (19), the fresh checkout found by a peer session (26), the drafter
installing one and counting (83) — and the fourth, row 123, was detected only by the two runs
disagreeing, and its cause is still unknown.

What distinguishes row 123 from the rest: in rows 19, 26 and 83 the second environment was
*identified*, and the repair was to make the assertion name it. In row 123 the differing input has
not been identified at all, so there is nothing yet to name. The row's consequence cell states the
cost precisely: "a passing `check --evidence` run launders a failing pre-push suite on the same
tree, and three branch pushes went through on a suite the gate did not run."

Recurrence after a mitigation a consequence cell describes:
- Row 83's cell names the repair taken — the package partition pinned exactly at 20 and the
  instance partition left to `check_package` — and that is in the tree today
  (`dyad/tests/guards/agent/test_records.py:35-46`). Nothing of that shape recurs in the 10 days of
  ledger after it.
- Row 26's cell names #24 as the fix, which changed how the hook calls its module. Both hooks today
  invoke the interpreter and pass the module as an argument (`dyad/hooks/pre-commit:4`,
  `dyad/hooks/pre-push:4`), so no guard module needs an exec bit. Nothing of that shape recurs.
- Row 123 post-dates the mitigation it falsifies: the suite memo was built by d-work #162
  (`agent-corpus/d-work/rows/162.md`, `done` 2026-10-02) and row 123 is 2026-10-09, seven days
  later. The memo is this mode's one shipped mitigation that *created* an instance of the mode.

## Mitigations (phase 2)
1. **The index mode, never the disk bit.** `crafts/syseng/guards/naming.py` `check_modes` at
   `crafts/syseng/guards/naming.py:218-236`, reading `dyadlib.tracked_mode`
   (`dyad/scripts/dyadlib.py:252-270`) rather than `os.access(p, os.X_OK)`, over the globs
   `dyad/bin/*` and `dyad/hooks/*` at `100755` (`crafts/syseng/guards/naming_rules.txt:47-48`). The
   docstring states the mode's own mechanism: on `core.fileMode=false` "every file reads 755 on disk
   whatever the index holds" (`crafts/syseng/guards/naming.py:220-222`). Moment: `package.py check`
   in Rule-11's runner (registry label `syseng/naming`) and at `dyad check --guards --pre-push`,
   through `dyad/scripts/package.py:606`. Reaches row 26's environment asymmetry exactly. Does not
   reach rows 19, 83 or 123. **Shipped**; verified today that the four hook and entrypoint files are
   tracked `100755`. No recurrence.
2. **The hooks invoke an interpreter, not a module.** `dyad/hooks/pre-commit:4` and
   `dyad/hooks/pre-push:4` both exec `dyad/bin/dyad-python` with the script as an argument, so a
   guard module's own exec bit is no longer load-bearing — which is the other half of row 26, and
   the half Rule-1's Enforcement calls "a hook that cannot execute at all". Moment: commit and push.
   Reaches row 26 only. **Shipped**.
3. **One place that states the fresh-install case.** `dyad/scripts/livetest.py` — `store_empty` and
   `instance_is_empty` (`dyad/scripts/livetest.py:73-80`), `require_store` / `require_instance` /
   `require_craft` / `require_guard` (`:101-125`), and `ScratchInstalls` (`:127`), whose docstring
   says the module exists so "the statement is written once and reads the same everywhere"
   (`dyad/scripts/livetest.py:9-10`). The repair of row 83 is in the tree beside it: the package
   partition is asserted **exactly** at 20 with the two counts written into the test's own comment
   (`dyad/tests/guards/agent/test_records.py:35-46`, assertion at `:46`). Moment: inside Rule-12's
   suite, i.e. `check_rule_12` (`dyad/scripts/package.py:216-236`) at `dyad check --guards
   --pre-push` and in `check --evidence`. Reaches row 83 exactly, and reaches row 19's second
   environment (a scratch install built from the committed tree) as the place it is now built.
   **Shipped**. No recurrence.
4. **The dirty-tree refusal at the gate.** `pushed_refs` at `dyad/scripts/package.py:576-580`
   refuses a push whose working tree holds any change, untracked files included. Moment: the
   pre-push hook, before any check runs (`dyad/scripts/package.py:589-594`). Reaches row 19: a
   suite run over a tree holding an uncommitted file can no longer be the verdict a push rests on.
   Does not reach 26, 83 or 123. **Shipped** — and it post-dates row 19 by two weeks (#194,
   2026-09-29), so it is a fence built later over the same shape, not the fence that caught it.
5. **The evidence block reports its environment.** `cmd_evidence` prints `dirty=yes/no` at
   `dyad/scripts/package.py:700`. Moment: `dyad check --evidence`, the merge evidence. Reports the
   environment rather than refusing it; reaches row 19's shape as disclosure, no row as prevention.
   **Shipped**.
6. **`check --evidence` never reads a memo.** Rule-12 property 2's sentence and `suite_gate`'s
   `pre_push`-only read (`dyad/scripts/package.py:335`, `:361`). Moment: the merge evidence. It is
   why row 123's consequence cell can say the merge evidence "is unaffected in kind". Reaches row
   123's consequence, not its cause. **Shipped**.
7. **The suite memo's key — the mitigation this mode falsifies.** `SUITE_MEMO_ENV` at
   `dyad/scripts/package.py:249` and `suite_memo_parts` at `dyad/scripts/package.py:264-282`. The
   key holds the tree, `sys.executable`, `sys.version`, git's version, the suite roots, six `DYAD_*`
   variables, a `refs/tags` digest, a digest of the instance's `*.local.txt` files and the UTC date
   (`dyad/scripts/package.py:279-282`). It holds **nothing** that distinguishes a run under
   `dyad/hooks/pre-push` from a direct one: no `GIT_VARS`, no pre-push flag — which is exactly what
   row 123 says. Moment: wherever a memo is written (`dyad/scripts/package.py:234-235`) or read
   (`suite_gate` under `pre_push`). **Shipped**, and the mode's one instance *after* it shipped is
   row 123 itself.
8. **Row 123's own two candidates** — reproduce with the memo removed and `ERROR:` captured, or
   widen the key / deny the pre-push skip. Named in plan #256 revision 4; **neither opened as a
   row**, verified today (no row in `agent-corpus/d-work/rows/` names this). **Candidate.**

Not inference-only: four mechanical mitigations are shipped (1, 2, 3, 4) and between them they
reach 3 of 4 rows at named moments. The fourth row is unreached, and the mechanism that was meant
to help there is the one that produced it.

## Remediation candidate, under attack
**One fence.** Add to `suite_memo_parts` (`dyad/scripts/package.py:264-282`) the one input that
distinguishes the two runs: a `pre_push` boolean, plus the *names* of `dyadlib.GIT_VARS`
(`dyad/scripts/dyadlib.py:239`) present in the runner's own environment. What it checks: that a
suite pass observed by a direct run can never satisfy a pre-push gate, and the converse. Where it
lives: the memo's key function in `dyad/scripts/package.py`. When it fires: wherever a memo is
written or read — which, by Rule-12 property 2, is `dyad check --guards --pre-push` alone, never
`check --evidence`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The row says the cause was never established and that 23 of 624 tests did not run at all, the shape of a collection error. A key widened on a guess may omit the real input, and will then have bought a colder cache for nothing. | confirmed | The key change is premature. What survives is row 123's own first candidate instead: reproduce with the memo removed and `ERROR:` captured. The fence must wait on a cause. |
| 2 | Widening the key makes every memo colder. `GIT_VARS` values differ per worktree, so a gate pass in a worktree would never satisfy the main checkout's, which is the cost Rule-12 property 2 bought the memo to avoid (53 of 112 merges re-ran an already-passed tree, the row behind #199 N2). | survives (scoped) | Only keyed on a `pre_push` boolean and on the variable *names* present, never their values, so the cost is one extra entry per checkout rather than one per worktree. |
| 3 | Rule-9 easy agreement: "the key is missing an input" read as obviously right. But the memo is not in the causal chain — the three pushes failed *before* any memo existed for that tree, and the memo only laundered them afterwards. A key change prevents the laundering, not the failure. | confirmed | The claim narrows to detection: "a direct pass never launders a pre-push failure." It is not prevention of the 29 errors and must not be presented as such. |
| 4 | Row 123's second candidate — deny the pre-push skip entirely — reaches the same row more surely and needs no cause. | survives (scoped) | It survives as the stronger option and is named here for the Operator, with its price stated: it discards the whole measured benefit of #162's memo. The key change is the cheaper half of a two-way disposition, not the recommendation on its own. |
| 5 | It reaches 1 of 4 rows, and the other three are already fenced by mitigations 1 to 4. A fence proposal that touches only the unexplained row is the whole of what is left. | confirmed | Coverage is the point rather than an objection here: this is the only live sub-mode. Rows 19, 26 and 83 are fenced at named moments and none has recurred. |

## Proposed exit (phase 4)
**Open.** Three of four rows are fenced at named moments — row 26 by `syseng/naming`'s
`check_modes` at `package.py check` and the push gate plus the hooks' interpreter invocation, row 83
by the exactly-pinned package partition inside Rule-12's suite at the push gate, row 19 by
`pushed_refs`'s dirty refusal at the pre-push hook. Row 123 is fenced by nothing, its cause is
recorded as never established, and both candidates named in plan #256 revision 4 remain unopened.

Proposed to the Operator, not taken: a `backlog` row naming row 123's first candidate as the fence
to build — reproduce the pre-push failure with the memo removed and `ERROR:` output captured, then
either add the identified input to `suite_memo_parts` or deny the pre-push skip. It would have
caught row 123 by establishing what differs between the two runs, which is the one thing that row
still lacks, and it carries the two-way disposition attack 4 names.

Where verification stopped: I could not establish row 123's cause either. I read the memo key and
confirmed the absence of any pre-push discriminator, but I did not reproduce the 29-error run — a
push is outside a subagent's limits, and no transcript of those three runs is in the tree.
