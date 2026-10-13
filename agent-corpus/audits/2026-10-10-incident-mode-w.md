# Incident mode W — the suite's environment leaked into the live repository

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10. 2 rows of 140 phase
1 derived, plus 1 logged after it and assigned here by inference — 3 rows in all (the final
section).*

## Definition
The mechanism: a process the Agent's own gate spawns inherits an environment that re-points its
writes at the repository being judged, so a test's fixture becomes a mutation of live state. Git
exports `GIT_DIR` to a hook, and in a linked worktree exports it absolute (with `GIT_COMMON_DIR`
beside it); a test child that shells out to `git` without clearing them addresses the pushing
repository rather than its own scratch directory. These are the two highest-damage rows in the
population: between them they set `core.bare=true` on the live repo, overwrote `user.name` and
`user.email` with the fixtures' `t`/`t@t`, moved local `main` and two real branch refs to fixture
commits, created fixture branches and a fixture tag, and put three commits authored `t <t@t>` onto
`main`, where history is not rewritten.

**What would have to change.** Every process the runner spawns must be given its environment
explicitly, with git's hook variables stripped at the spawn, and a new spawn site must be refused
until it is classified — so that inheriting the ambient environment is never the default.

Boundaries against the neighbours it is most easily confused with:
- **I, verified in one environment, run in another** — I is a *verdict* about the other
  environment; W is a *write* into it. Same `GIT_VARS` asymmetry, two sides: row 123 (I) is a suite
  pass that does not transfer between a hook run and a direct one, rows 57 and 58 (W) are the hook
  run writing into the repository it was judging.
- **O, a git write used as a read** — O is a git command the Agent chose whose write effect it did
  not intend (`git checkout origin/main -- .` to read one file); W is a write the Agent never
  issued at all, made by a child process under an inherited variable. Test: who ran the writing
  command? Boundary row: row 5 is O (the Agent typed the checkout), row 58 is W (the suite's own
  fixtures did it).
- **V, enforcement routed around** — V bypasses a fence; W is a fence that, when it ran, damaged
  what it was protecting. Row 57's gate "then reported 20 failures and 6 errors — failures *of the
  clobber*, not of the diff", so the fence's own output became unreadable.
- **T, a stale or partial view of shared state** — T is a concurrent session's own writes seen late.
  Row 57 names a peer session live in the same checkout at the time, which is T-adjacent, but the
  damage came from the suite's children, not from the peer.

## Incidents (2)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-25 | #152 | pushing from a worktree ran the pre-push hook, whose suite wrote `core.bare=true`, a fixture branch, a tag and the fixtures' identity into the live repository | git exports `GIT_DIR` to a hook, absolute in a linked worktree, and `check_rule_12` / `run_suite` spawned the suite with `{**os.environ}`, so every scratch-repo git call resolved to the real repository; `dyadlib.git_env()` already existed for this and was not used |
| 2026-09-25 | #161 | pushing from a worktree let the suite's git children operate on the shared repository, moving local `main` and a real branch to fixture commits | three fixture branches were created too; the same leak from the second direction: a linked worktree's hook also exports `GIT_COMMON_DIR`, which #152's partial repair did not drop; a peer session was live in the same checkout, and the gate's own 20 failures were failures of the clobber |

## Pattern
Both rows are the same day, both are a push from a **linked worktree**, and both were caught
immediately — row 58 from `git status` showing another tree, row 57 by the gate's own nonsense
output. Neither pushed anything in the damaged state. The two rows together establish why one
repair was not enough: #152's PR-1 fixed the spawn for `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE`, and #161 then found that a linked worktree's hook exports `GIT_COMMON_DIR` too,
which the first list did not hold. Row 57's own cause cell says so: "#152's PR-1 repaired one
instance of this … and the leak is evidently not closed".

The mode's most consequential residue is logged in row 58's consequence cell and found later under
#169: every commit that session made between the incident and the discovery was authored `t <t@t>`,
three of them already on `main` (`6ba6efb`, `f35dbe7`, `0fb8bc7`), which is why #152's Done-`Y`
could not execute those merges.

Recurrence after the mitigations each cell describes: row 58's cell names the fix as
`package.suite_env()` dropping `GIT_VARS` for every test child, with `SuiteEnvTests` asserting it,
and closes backlog row 165's defect; row 57's cell names backlog #165 as opened for the fix and
records `GIT_COMMON_DIR` being added to `dyadlib.GIT_VARS`. Both are in the tree today (see
mitigations 1 to 3). **No row of this mode post-dates them** — the two rows are both 2026-09-25 and
the population runs to 2026-10-10, fifteen days and roughly 80 further rows with no recurrence.
That is the measurement, and it is the strongest such measurement in the four modes of this audit.

## Mitigations (phase 2)
1. **The variable list and the clean environment.** `dyadlib.GIT_VARS` at
   `dyad/scripts/dyadlib.py:239` — `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`,
   with the comment naming both rows — and `dyadlib.git_env()` at `dyad/scripts/dyadlib.py:242-244`,
   which returns `os.environ` without them. A fail-loud `INVARIANTS` entry sits on the list:
   `("git-vars-distinct", …)` at `dyad/scripts/dyadlib.py:602`, enforced at import by
   `enforce(INVARIANTS, __name__)` at `dyad/scripts/dyadlib.py:612`, so a malformed list fails every
   import of `dyadlib`. Moment: import of `dyadlib` for the invariant, and every call site for the
   function. Reaches both rows as the primitive the fix is built from; on its own it reaches
   neither, because it must be *used*. **Shipped.**
2. **Every python child spawned with a cleaned environment.** `package.suite_env()` at
   `dyad/scripts/package.py:396-407`, whose first line is
   `env = {**dyadlib.git_env(), "DYAD_NO_NESTED_TESTS": "1"}` (`dyad/scripts/package.py:404`), and
   whose docstring names #152's damage verbatim (`:398-401`). Both spawns of the suite use it:
   `check_rule_12` at `dyad/scripts/package.py:227-229` and `run_suite` at
   `dyad/scripts/package.py:414-415`. Moment: `package.py check` in Rule-11's runner, `dyad check
   --guards --pre-push` (the hook, `dyad/hooks/pre-push:4`), `dyad check --evidence`, and `dyad
   check --tests <target>`. Reaches **both** rows at the exact boundary where each happened.
   **Shipped.**
3. **The spawn-site fence.** `SpawnSiteTests` at `dyad/tests/test_package.py:1179-1228` parses
   `dyad/scripts/package.py` with `ast` (`:1199`) and finds every `subprocess` / `os` spawn call
   (`:1183-1184`). A python child without `env=suite_env()` is a failure (`:1218-1219`); a `git`
   call whose enclosing function is not in `GIT_ALLOWED` is a failure (`:1220-1223`), and
   `GIT_ALLOWED` (`:1185-1196`) carries a written reason per function for why that call may inherit
   the parent's environment; a stale entry also fails (`:1228`). Moment: inside Rule-12's suite, so
   `check_rule_12` at the push gate and in `check --evidence`. This is the mitigation that makes the
   mode not recur by *construction* rather than by memory: a new spawn site in `package.py` is
   refused until judged. **Shipped.**
4. **The reproduction as a control.** `SuiteEnvTests` at `dyad/tests/test_package.py:1108-1132`
   asserts `GIT_VARS` dropped and `GIT_COMMON_DIR` absent (`:1116-1117`).
   `SuiteEnvWorktreeTests` at `dyad/tests/test_package.py:1134-1177` builds a real shared repo with
   a linked worktree, takes the hook variables the worktree's pre-push hook actually receives
   (`:1153`), and runs two cases: a child under `suite_env()` leaves the shared repo's config and
   every ref unchanged (`:1157-1167`), and the **control** child under the raw hook environment
   writes `core.bare=true`, `user.name=x` and `refs/heads/feature` into it (`:1168-1177`). So the
   damage of rows 57 and 58 is reproduced on every run, and the day the fix regresses the control
   stops being a control. Moment: as 3. **Shipped.**
5. **Other modules' own use of `git_env`.** `dyad/scripts/livetest.py:146` and `:158` (its git
   calls and its `package.py install` child), `dyadlib.repo_root` at `dyad/scripts/dyadlib.py:250`,
   `dyadlib.tracked_mode` at `dyad/scripts/dyadlib.py:265-266`, `dyadlib.range_paths` at
   `dyad/scripts/dyadlib.py:293-294`, `distribute.py:205-206`, and the memo's `_git` at
   `dyad/scripts/package.py:252-256`. Moment: wherever each is called. Reaches both rows' mechanism
   in the modules the fence of 3 does not cover. **Shipped**, but by convention: see the residue
   below.

### Is the leak closed today?
**Yes, at the boundary where both rows happened, and I can cite it.** The hook itself still runs
under git's exported variables — `dyad/hooks/pre-push:4` execs `dyad/bin/dyad-python` with
`package.py check --guards --pre-push` and strips nothing — so the *runner* inherits `GIT_DIR` and,
in a worktree, `GIT_COMMON_DIR`. What is closed is every spawn beneath it: both suite spawns pass
`env=suite_env()` (`dyad/scripts/package.py:229`, `:415`), `suite_env` is `git_env()` plus one
variable (`:404`), `git_env` drops all four names (`dyad/scripts/dyadlib.py:242-244`), the AST fence
refuses a new unguarded python child in that file (`dyad/tests/test_package.py:1218-1219`), and the
worktree control test asserts the damage still happens without it
(`dyad/tests/test_package.py:1168-1177`). The runner's own git calls are read-only and enumerated
with reasons (`dyad/tests/test_package.py:1185-1196`), and `repo_root` strips the variables itself
before asking for the toplevel (`dyad/scripts/dyadlib.py:250`), the #142 work that row 58's cause
cell says "already existed for exactly this … and was not used at the suite's spawn".

**One residue, stated.** The AST fence of mitigation 3 parses exactly one file
(`dyad/tests/test_package.py:1199`). Two python-child spawns outside it pass no `env` at all:
`dyad/guards/craft/crafts.py:260` and `dyad/guards/craft/crafts.py:280`, the craft guard's floor
children, which run under the pre-push hook's environment with `GIT_DIR` intact. I read what those
children do — they load a floor package's modules and print invariant results, and `dyadlib`'s own
`repo_root` strips the variables before its one git call — so I found no write path from them today.
But nothing refuses a new spawn site, or a floor module's new git call, in `crafts.py`,
`runbook.py`, `distribute.py`, `craft.py` or `trace.py`. That is the gap, and it is the gap the
candidate below closes.

## Remediation candidate, under attack
**One fence.** Lift `SpawnSiteTests` (`dyad/tests/test_package.py:1179-1228`) from a one-file test
into a guard check that runs over **every** module of the core craft and of each installed Tended
craft: each python child must pass `env=suite_env()` or `env=dyadlib.git_env()`, and each `git`
call's enclosing function must appear in a per-module allow table with a written reason. Where it
lives: a `TREE_INVARIANTS` entry or a check function in an existing guard module — the natural home
is `crafts/syseng/guards/invariants.py` (registry label `syseng/invariants`), which already walks
every module and spawns an audit child. When it fires: `package.py check` in Rule-11's runner and
at `dyad check --guards --pre-push`, i.e. before every push rather than only inside Rule-12's
suite.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Rule-9 easy agreement: "generalize the fence that worked" read as obviously right. But the mode has not recurred in fifteen days and roughly 80 rows, and the two rows it has were both pushes from a linked worktree — a configuration Rule-16's Presence clause now advises into. A generalized fence buys nothing measurable and adds a guard to every push. | survives (scoped) | The fence survives only as the cheapest form that keeps the existing coverage honest: an allow table per module, no new guard module, and no new moment. "Generalize because it worked" does not survive; "the fence's own scope must be visible" does. |
| 2 | It is a static check and the real surface is dynamic. A floor module loaded from a *released archive* (`crafts.py:260`'s `_FLOOR_SCRIPT` runs an older package's code) is not in the tree the check parses, so an old module's unguarded git call is reachable and unfenceable this way. | confirmed | The static check cannot reach a floor package's own code. Survivor: the check is scoped to tracked modules, and the floor-child case is instead closed by passing `env=dyadlib.git_env()` at `dyad/guards/craft/crafts.py:260` and `:280` — a two-line change that needs no fence at all and should be proposed on its own. |
| 3 | A per-module allow table is the pinned-enumeration class the ledger has four other modes for (`GIT_ALLOWED`'s stale-entry assertion at `dyad/tests/test_package.py:1228` already exists because of it). Every new helper that calls git has to edit a table in another craft's guard. | survives (scoped) | Only if the table is discovered per module — declared in the module that spawns, like `INVARIANTS` and `BUNDLED_WITH_CORE` are — so the data leaves with the module and no central list is edited. A central table does not survive. |
| 4 | It targets the write path, and the write path is already closed where it mattered: both rows' damage came through `package.py`'s two suite spawns, both of which are fenced today and reproduced as a control. | confirmed | The candidate is not a remedy for the mode's two rows; those are fenced. It is a remedy for the fence's blind spot, which is a different and smaller claim, and must be presented as that. |
| 5 | Cost at the wrong moment: parsing every module of every craft on every push adds to the gate that Rule-12 property 2 and the suite memo exist to keep cheap. | survives (scoped) | Admissible only inside the module walk `syseng/invariants` already performs, adding no new traversal; as a standalone pass it does not survive. |

## Proposed exit (phase 4)
**Fenced at a named moment.** The mechanism of both rows — a suite child inheriting a hook's git
variables and writing into the live repository — is checked by `SpawnSiteTests`
(`dyad/tests/test_package.py:1218-1223`), which refuses a python child in `dyad/scripts/package.py`
that does not pass `env=suite_env()` and refuses an unclassified `git` call site, and by
`SuiteEnvWorktreeTests` (`dyad/tests/test_package.py:1157-1177`), whose control case asserts the
damage still occurs without the fix. The moment both fire: `check_rule_12`
(`dyad/scripts/package.py:216-236`), i.e. at `dyad check --guards --pre-push` before every push and
again in `dyad check --evidence` for the merge evidence. A fault of this shape presented at that
moment today — a new spawn site in the runner written with the ambient environment — fails the gate
before the push leaves the machine.

Proposed to the Operator, not taken, as the residue above is not part of that fence:
- the two-line change passing `env=dyadlib.git_env()` at `dyad/guards/craft/crafts.py:260` and
  `:280`, so the one unguarded python spawn under the hook's environment is removed rather than
  reasoned about;
- a `backlog` row naming the candidate fence in its surviving, scoped form — a per-module declared
  allow table checked inside `syseng/invariants`'s existing module walk — which would have caught
  nothing in this mode's two rows and is offered only to make the existing fence's scope visible.

Where verification stopped: I did not push from a linked worktree to observe the hook's exported
variables live; the hook variables I relied on are the ones
`dyad/tests/test_package.py:1153` records as observed under git 2.43.0, and the claim that
`dyad/hooks/pre-push` strips nothing is read from its four lines, not from a live run.


## Rows added after the derivation (1)

Logged after phase 1's reconciliation and assigned to this mode **by inference**, not by the two-view
derivation. The counts in this record's title, in child row #284's immutable title and in the index's
modes table are the derivation's and do not move (Rule-16). It is the mode read in the other
direction, and the Definition covers it only by symmetry: the two derived rows are the suite writing
into the live repository, and this one is the live invocation's own config reaching into the suite.
Both are one process inheriting an environment that re-points its git calls at a tree it was not
asked about.

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-10-13 | #259 | the pre-push gate refused twice with 29 suite errors that no hand-run of the same suite could reproduce, because `git -c core.hooksPath` exports `GIT_CONFIG_PARAMETERS` to every child and all 29 fixture-repo commits inherited a hooks path relative to a scratch repo | one process inherits an environment that re-points its git calls, which is this mode read in the other direction. `GIT_VARS` drops four variables and none of the `GIT_CONFIG_*` family, so the one-command `-c` is not local to the command. It is also the mechanism row 123 lacked |
