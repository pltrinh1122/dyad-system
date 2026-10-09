# Audit: the Operator-disposition chain of authority, down to git and GitHub

*d-work #251. Opened 2026-10-08 on the Operator's prompt; executed 2026-10-09 under plan
`agent-corpus/d-work/plans/251.md` (plan-`Y` 2026-10-09, batch #251,#252,#253). Standing: `main` at
`7bf55b3`, `origin/main` at `3cb9dba`, git 2.53.0, 243 rows, 222 provenance records, 50 tags.*

## The conflict of interest, named first

This audit was asked for by the Operator and written by the Agent, and half of what it was asked to
find is "unnecessary human-in-the-loop counter-prompts" — that is, the proposer auditing the
disposer's questions. Rule-2 exists because those two parties must not be the same. Three
constraints were therefore binding on every seat, and are restated here so a reader can check that
they held:

1. **No finding may propose removing a Rule-2 base event** (merge, direct push to `main`, a final
   verdict), a Rule-8 destructive counter-prompt, or a Rule-11 release counter-prompt. None does.
2. **Every `friction` finding states, in its own row, what authority would be lost** if the question
   were removed. A finding is `duplicates` only where the identical authorization is provably
   already recorded.
3. **The audit recommends nothing.** It surfaces candidate rows; the Operator disposes each.

The honest summary of the second half of the prompt, stated up front: **almost none of the
Operator's questions are unnecessary.** Of thirteen counter-prompt forms the Rules require, eleven
add authority that nothing else supplies. What the audit found instead is the opposite shape — the
questions are load-bearing and the *mechanisms* behind them are thinner than the Rules' own text
says.

## Method

Seven links, one seat per link, each given the same brief: what the chain *asserts* here, what a
mechanism *checks* here, and the gap between them, with every claim citing a path and line, a
commit, a tag, or an observed run. Six seats were subagents (Rule-3 Scope: read, search and draft
only — no row, no commit, no push, no PR, no merge, no host action, no `gh` write); the seventh,
the counter-prompt inventory, is the main Agent's. Classes: **adds authority** (the question
decides something undecided), **duplicates** (the same authorization already recorded), **friction**
(a keystroke that decides nothing). "No gap found" appears only where what was tried is named.

Every seat excluded `.claude/` from its searches: a subagent worktree sat inside the working tree
during the audit, a complete second copy of the repo, which would have double-counted every
recursive search. That exclusion is itself finding **H9** below.

---

## Link 1 — Capture: the Operator's words reaching the corpus

| # | what the chain asserts | what is mechanically checked | class | evidence |
|---|---|---|---|---|
| C1 | A disposition, once recorded, is immutable | Only **added** `disposed` entries are shape-checked; an entry rewritten in place passes. The record's entry `note` — where the verdict text lives — is outside `_grows`'s key | adds authority | `rows.py:89`; `provenance.py:229` (`key = (kind, date, text)`); observed `_grows` **True** when only the note `N done`→`Y done` changes |
| C2 | A row reaches `done` on a Done-`Y`, `planned` on a plan-`Y` | **Nothing couples a state transition to a disposition.** `dwork state <id> done` with no `-d/--said` writes the state, no `disposed` entry, no record entry; the count check then sees 0 = 0. Only `backlog→open` is coupled | adds authority | `package.py:965-977` (sole refusal is `:971`); `provenance.py:256-269`. Conduct has held: 180 `done` rows, **0** without a `* done` entry |
| C3 | Rule-7 p5 ties record to row one-to-one | A **count** only. Neither verdict, note text nor date of the i-th entry is compared | duplicates | `provenance.py:123-126`. Measured: 0 note/date mismatches for ids ≥ 194; 312 of 452 notes diverge below #193 |
| C4 | No credential shape reaches a record | `FAIL_SHAPES` is applied to fenced bodies only. Text above the first entry, between heading and fence, and after a closing fence is dropped by `parse` and never scanned | adds authority | `provenance.py:109-121`, `:70-89`; observed three `ghp_…` shapes in those positions → `check_record` `[]` |
| C5 | Enforcement fails "a missing or unterminated fenced body" | Missing: yes. **Unterminated: not implemented** — the body loop runs to EOF, swallowing later entries so no numbering gap is seen either | adds authority | `provenance.py:81-88`; observed a swallowed `## 2 disposition … Y plan` → `check_record` `[]` |
| C6 | Only a disposition opens a `backlog` row | For a legacy-listed row with `n=0` and no record, the check requires `disposed` to hold 0 entries — the list exempts the existence of any disposition record at all. **14 rows are `backlog` with empty `disposed` and no record** | adds authority | #38 #70 #129 #130 #131 #132 #134 #136 #170 #171 #172 #173 #177 #181; `provenance.py:183-192`. Bounded: `prs.py:44` excludes `backlog`, `provenance.py:262` demands words at `backlog→open` |
| C7 | The legacy list records words that cannot be written | `n` is a permanent subtraction, so writing a lost word later **fails** | friction — *authority lost if removed:* none may be removed; the reviewed-PR requirement is what stops the alarm being switched off | observed `check_record` for #84 with its lost disposition written → FAIL. Fence available: make `lost` an upper bound |
| C8 | Each legacy line states why the words are lost | `reason` is free text, never read. Rows #162–#165 are listed as "backlog with empty disposed" while being `done` with records and `Y done` entries | friction — *authority lost:* none; those four lines authorize nothing | observed dump; `provenance.py:142-165` |
| C9 | A `disposed` date is the date of the act | `ENTRY` validates shape only; not a calendar date. `dwork` always stamps `today`, so a disposition written late is misdated with no trace | adds authority | `rows.py:40`; observed `9999-13-45 Y` accepted |
| C10 | Every Operator prompt is written as an entry | `prompt` entries are **never counted** — the row has no prompt column to count against. 54 of 222 records hold no `prompt` entry | adds authority (impossibility) | `provenance.py:123`, `:256-264`. The one independent witness, the harness transcript, is forbidden the corpus (Rule-7 p2) |
| C11 | A record only grows; the legacy list changes only by reviewed PR | **Both hold.** A body rewrite fails `_grows`; the list is outside `d-work/`, so the fence refuses a direct commit and the plan gate covers a branch | adds authority — no gap found, named | observed `_grows` **False** on a body rewrite; `git log` on the list → one commit `0d59f1a`. What was tried: a local edit — refused, the tree goes dirty and the push is refused |

## Link 2 — Authorization to mutation: the plan gate

The one mechanically gated counter-prompt in the system. Its only live path is
`prs.check_transaction` called from `dyad/hooks/pre-push` with `base="origin/main"`; it reads the
branch's **commit messages** as the body and resolves ids against the rows as `origin/main` holds
them.

| # | what the chain asserts | what is mechanically checked | class | evidence |
|---|---|---|---|---|
| L2-1 | A PR's mutation is authorized by a plan-`Y` | `"Y plan" in row.disposed` — a case-sensitive substring over the whole free-text column. **Five strings that are not a plan-`Y` pass the gate** and also pass `rows.ENTRY` | subtracts authority | `prs.py:46`; `rows.py:40`. Observed to pass: `N plan (Operator: revise, then I will give Y plan)`; `Y planned`; `Y plan-withdrawn after revision`; `N done (waiting on #221's Y plan)`; `Y backlog (child of #249, which holds Y plan)`. **All 242 rows scanned: none satisfies the key accidentally today** |
| L2-2 | A withdrawn plan needs a fresh `Y` | Nothing. The key is monotone: `Y plan; N plan (withdrawn)` **passes**. `disposed` is append-only, so a revocation can only be appended, never cancel the substring | subtracts authority (latent) | observed; `prs.py:46`. Unexpressible today: `disposed` has no kind field |
| L2-3 | The gate resolves the id "against the ledger on the base branch" | It resolves against **`origin/main` as last fetched** — a local, writable ref. Nothing on the gate's path fetches | friction — *authority lost if removed:* the base-commit read is what stops a branch authoring its own `Y plan`; the friction is the **staleness**, not the read | Observed live: `main` `7bf55b3` holds the batch plan-`Y`; `origin/main` `3cb9dba` does not; `base=origin/main` → `FAIL: #251 has no 'Y plan' disposition`, `base=main` → PASS |
| L2-4 | Record the Done-`Y`, then merge | Taken with L2-3 the gate then **refuses the ratified branch**: `done` is not admissible and never regresses. A conflict appearing between the Done-`Y` and the merge leaves a ratified PR no branch its fix can reach | friction — *authority lost if removed:* admitting `done` would void the Done-`Y`'s binding to a head. Nothing removable; the cost is a **new** question each time | Recurred twice in 9 days: `INCIDENTS.md:89` (#196) and `:123` (#242, "it cost a plan, a Y/N, a force-with-lease and a Done-`Y` more than the content needed"). ~3 extra dispositions per occurrence |
| L2-5 | A plan-`Y` binds every PR of the d-work to the plan | **Nothing ties the diff to the plan.** Any diff, any size, any zone, citing one admissible id passes. `files touched:` is read only for presence and a warning, never compared to a diff | subtracts authority | `prs.py:31-48`; `grep -rn "files touched" --include=*.py` → 4 hits, all presence/warn. The parser exists (`sessions.plan_files`) and nothing calls it from the gate |
| L2-6 | Rule-15 phase 2: a moved base forces a re-plan | Nothing. The key never expires | subtracts authority | Row #81 is `planned` with a 21-day-old plan-`Y`; `main` has since moved past two of its own `files touched` |
| L2-7 | A plan-`Y` authorizes a mutation *before* it is made | The gate reads a state at push time, never that the entry predates the commits | subtracts authority | `INCIDENTS.md:50` (#92/#103/#104): three PRs pushed before the plan-`Y`; the `Y` then "retroactively authorizes the content already pushed". Strictness is foreclosed — Rule-3 permits a PR to accompany its plan |
| L2-8 | `d-work #N` is a claim, not a mention | The regex matches **every** occurrence, including inside code fences and prose quoting precedent | friction — *authority lost if removed:* a loose matcher is what makes the citation unforgeable by wording; excluding fenced code loses none of that | `INCIDENTS.md:43` (#15) — a prose precedent citation refused a merge and the repair **spent an Operator `Y` entirely on a regex**; `:93` (#199) — `"skip (d-work #164)"` copied into commit prose refused a push |
| L2-9 | "A PR body's `d-work #N`" (Rule-1 Conditions; the guard's own docstring) | **No mechanism ever reads a PR body.** `PR_BODY` has three occurrences, all inside `prs.py`; `prs.main()` has no caller; no workflow has a `pull_request` trigger | duplicates — provably: the identical check runs locally over commit messages | `grep -rn "PR_BODY"`, `grep -rn "pull_request" .github/workflows/` → empty. A PR whose **body** cites a `done` row merges without complaint if its commits cite correctly |
| L2-10 | A ledger-only range claims no d-work | `ledger_only` judges **each commit's own** first-parent diff. A branch that adds `code.py` then deletes it is **not** ledger-only though the net diff is empty; a single empty commit flips it too | subtracts authority (structural) + friction | `dyadlib.py:324-338`; observed. **The commit that writes the `Y plan` key is itself exempt from the gate the key opens** — the plan gate rests on links 1 and 3, not on itself. `INCIDENTS.md:83`: when the gate did apply to ledger commits, seven PRs went through the hosting API and **every** guard was skipped |
| L2-11 | `blocked` is deferred work | `blocked` is admissible, so a deferred d-work's PR passes. 0 live `blocked` rows | subtracts authority (latent) | `prs.py:44`. A Rule choice, not a guard bug |
| L2-12 | Intake rows name their origin `<system>-<id>` | The regex matches bare digits only: `d-work #196` resolves to **this** instance's row 196; `d-work #workstation-196` matches nothing | friction — *authority lost:* none; both directions are wrong in one place | `prs.py:25,29`; observed |

## Link 3 — The direct-push fence

Both hand-off questions answered up front: the fence carries the Operator's authority for direct,
first-parent, non-merge commits on `main` and for ledger-only branches, and carries **nothing** for
a row file arriving on `main` inside a merge of a mixed branch. It costs **no** human question — it
is the mechanism that removes them (the clerical ledger commit; `ledger-pr-merge: agent`). No
finding in this link is `friction`.

| # | what the chain asserts | what is mechanically checked | class | evidence |
|---|---|---|---|---|
| F1 | A direct commit to `main` is ledger-only or refused | Fully, for every non-merge first-parent commit of the range | adds authority | `rows.py:117-122`, `:155-173`. Rename-safety verified not assumed: `diff-tree` is plumbing and ignores `diff.renames` (observed three ways on `4540c41`) — so the #191 move-into-the-ledger hole is absent **by plumbing semantics, not by a flag**, a latent fragility if `:119` is rewritten as `git diff` |
| F2 | A PR merge lands commits this fence never visits — handed to `check_ledger_branch`, else to the plan gate | The hand-off is real for ledger branches and **empty** for every other branch: branch mode runs only `check_id_collisions` + `check_disposed`, neither of which reads `state` | adds authority | `rows.py:160`, `:171-188`. Measured: **498** non-merge commits on `main` touch `rows/`; only **306** are on the first-parent line — **192 (38.6%) arrived inside a merge**. Of those, **14** commits across 9 merges came from non-ledger-only branches and were judged by no invocation of this fence, ever. The tests assert the gap deliberately (`test_rows.py:192-195`, `:220-225`). All 14 were re-judged by hand against their parents: **none would have failed** |
| F3 | A merge commit is judged against both parents | True on a **ledger-only branch only**. `check_merge` has exactly one caller; on `main`, `--no-merges` excludes every merge — including the `git merge --no-ff` path Rule-14 p3 prescribes when the hosting is unreachable | adds authority | `rows.py:187`, `:190`. The sibling guard already does it: `provenance.py:297-298` calls its own `check_merge` on every range, any branch |
| F4 | State never regresses; `done` never reopens | Enforced at three points, **not** on a non-ledger-only branch. An agent-zone PR may legally carry `dyad/*` and `agent-corpus/*` (one zone), so `done→open` passes branch mode, then passes the first-parent walk at merge | adds authority | `dyadlib.py:444-451`, `:498-501`. Consequence: a `done` row pushed back to `open` makes its **spent plan-`Y` reusable** for new PRs with no new disposition |
| F5 | The ledger is append-only; `disposed` is the reconstructible chain | **Only the shape of entries the range adds.** Removal, truncation and in-place rewriting are not judged. Observed to pass: truncate a trailing entry; drop a middle entry; **rewrite `N plan` → `Y plan` in place**; `2099-01-01 Y done`; `2026-13-45 Y done`; a bare `2026-10-09 Y` with no kind | subtracts authority | `rows.py:40`, `:82-92`. Partial net: provenance's count catches *losing* an entry (k=−1, dk=0); it does **not** catch the in-place flip (k=0, dk=0), and nothing compares a record entry's text to the row's |
| F6 | `disposed` records dispositions the Operator gave | Nothing. Both texts are written by one Agent-authored command | **recorded impossibility on this kernel** | `package.py:928-946`; Rule-7 Enforcement's own closing sentence. The Agent holds the pen for both artifacts |
| F7 | id and title immutable | **id: genuinely immutable** (three independent mechanisms). **title: immutable** except for a row born on the same branch. **`opened`: never compared anywhere** | adds authority (low) | `rows.py:139-144`; `references.py` rows 5 and 7; `provenance.py:175`. Observed drift over all 242 rows: none. `refs` is likewise unconstrained — nothing enforces that a `blocked` row's `refs` names its blocker |
| F8 | The mode the fence ran in is part of the merge evidence | The mode is chosen by the **checked-out HEAD's name**, not the range, and the evidence block does not print it. `rows.py` declares no `TRANSACTION_MODE` while `provenance.py:39` and `containment.py:93` do | adds authority | Observed: identical range, two verdicts, depending only on which branch is checked out. Merge evidence is produced on the branch head being merged — i.e. **always in the weak mode of F2, silently** |
| F9 | Ledger-only is a path predicate, so everything under `d-work/` is clerical — including the plan file a plan-`Y` binds to | Nothing checks a plan file's content across commits. `plans.py:20`: `TRANSACTION = False`; provenance filters to `rows/` and `provenance/` only | adds authority | **The object the plan-`Y` binds to is the least fenced thing the ledger-only rule admits** |
| F10 | CI corroborates the fence after the merge | Inverted coverage: `dyad-d-work.yml` carries `paths-ignore: ['agent-corpus/d-work/**']`, so a ledger-only direct push to `main` — exactly what the fence judges — never triggers the job; and a code push to `main` is a merge, whose range the walk visits emptily | adds authority (narrow) | `.github/workflows/dyad-d-work.yml:4-6`, `:15` |

## Link 4 — The hook layer

Observed: `core.hooksPath` = `/mnt/shared_data/dyad/dyad-system/dyad/hooks` — **absolute**, not the
relative `dyad/hooks` Rule-1 prescribes. `core.fileMode=false`. Repo **public**, `main`
**unprotected**, rulesets `[]`. `crafts/REGISTRY.md` holds zero rows.

| # | what the chain asserts | what is mechanically checked | class | evidence |
|---|---|---|---|---|
| H1 | `check --guards --pre-push` judges the refs git pushes | A push whose every ref is a deletion, a non-commit-ish, or already an ancestor of `origin/main` returns **rc 0 having run zero guards and zero invariants** — the early return precedes `cmd_invariants()`. The `ok` line reads like a pass | adds authority | `package.py:589-597` vs `:600`. Observed: a tag ref on base → one line, `rc=0`. **Live instances: `git push origin <release tag>` and `git push origin :main` are unguarded by construction**, and `check_drift` — the one guard that exists *for* tags — is a `check_package` guard the early return skips |
| H2 | These hooks are the only *blocking* enforcement | **Nothing mechanical checks that hooks are enabled.** No guard reads `core.hooksPath`; the only readers are a play-book and an install print. `--no-verify` leaves no record and no detector | adds authority | `grep -rn hooksPath` over `dyad/ crafts/ .github/` → zero guard reads. Three historical `--no-verify` pushes recorded in `2026-09-16-pydantic-schema-prevention.md:50`. Recorded impossibility: a hook cannot police its own invocation |
| H3 | A lost exec bit leaves enforcement vacuous (#23) | Partly fenced, and **the fence is not shipped with the core**. `syseng/naming` checks the **index** mode of `dyad/hooks/*`; for a tracked path the disk bit is never read, and `core.fileMode=false` means git ignores a disk `chmod -x` entirely. `syseng` declares no `BUNDLED_WITH_CORE`, so a core-only install has no hook-mode fence | adds authority (scoped) | `naming_rules.txt:47-49`, `naming.py:218-235`; `grep -rn BUNDLED_WITH_CORE` → only `sysadmin/guards/changelog.py:36`. The original #23 shape is **gone**: the hooks now exec `dyad/bin/dyad-python <script>` |
| H4 | Every guard runs on the pinned kernel | **Fenced, fails closed.** `dyad-python` probes by *running* each candidate and exits 1 when none meets (3,12); the hook `exec`s it | adds authority — the one hole in the brief's list that is closed | `dyad/bin/dyad-python:22-54`; `test_entrypoint.py` pins the shell constant to the Python one. Tried: missing interpreter, below-pin interpreter, pin drift |
| H5 | `rows.py` fails any direct **commit** to `main` that is not ledger-only | `pre-commit` runs **only** containment. The fence and the plan gate are transaction guards that run **at push**, never at commit | adds authority (timing) | `dyad/hooks/pre-commit:4`. Low consequence today — nothing escapes without a push — but it is the sentence Rule-2's Enforcement cites by name |
| H6 | "A commit is created (`pre-commit`, blocking)" | **A merge commit is judged by nothing.** Git runs `pre-merge-commit` (absent) not `pre-commit`, and both push-side walks skip merges | adds authority | `ls -a dyad/hooks/` → only `pre-commit`, `pre-push`; `containment.py:164`, `rows.py:160`. The #138 local-merge path is exactly the one the Operator uses when CI cannot corroborate, so the gaps compose |
| H7 | The suite memo and the installed-root skip are safe because `check --evidence` never reads one | **Both hold as written, verified.** The residual hole is the memo's **key**: it covers tree, interpreter, git version, roots, six `DYAD_*` vars, a tags digest, a `*.local.txt` digest and the date — **not installed third-party packages.** pydantic is a *kernel* row, so a pydantic upgrade between a pass and a push yields a stale hit | adds authority (narrow) | `package.py:264-282`, `:361`, `:644`, `:703`; `test_package.py:1314`, `:1299`. Both skips were **inert** while read (dirty tree; registry empty). The installed-root skip's soundness rests on H9's dirty refusal — an undocumented coupling |
| H8 | Hosted CI corroborates after the merge | **No workflow is a gate and none sees a branch or a PR.** All six are `push: branches:[main]` or `push: tags`. Four of six have **no `setup-python`**, running the runner's default against a 3.12 pin. All five `main` workflows carry `paths-ignore: ['agent-corpus/d-work/**']`, so a ledger-only push to `main` is corroborated by nothing | adds authority | the six workflow files. **Answer to the brief's question: no, CI cannot substitute for any of link 4** |
| H9 | `pushed_refs` refuses a push whose tree differs from the commit | Dirt = `git status --porcelain --untracked-files=normal`: **untracked counts, ignored does not.** `.claude/` is untracked and not in `.gitignore`, so **every push of HEAD from this checkout is refused** while a subagent worktree exists. And `.claude/*` is a classified **infra** path, so the pre-commit hook would *permit* committing a second copy of the repo rather than refusing it | friction — *authority lost if removed:* the real one. Every state guard, the memo and the installed-root skip read the **working tree**, not the pushed commit; without the refusal the gate judges files absent from the merge and the evidence block attests to a different tree. **The refusal must stay; the gitignore gap is the removable half** | observed; `package.py:576`; `containment.py zones` → `infra  .claude/*`. Asymmetry worth its own row: `cmd_evidence` records `dirty=yes` and **does not refuse**, so the merge evidence Rule-2 relies on can be produced over a tree that is not the commit |
| H10 | "repo is private on a free plan; branch protection/rulesets return 403" (`falsification/rules/rule-1-containment.md:9`) | **The premise is now false.** `private: false`; protection → **404 "Branch not protected"**, not 403; rulesets → `[]`, readable | adds authority | three `gh` reads, 2026-10-09. The record's own survivor says "Becomes blocking if repo goes public or plan upgrades." It has gone public and the record has not been revisited |
| H11 | `core.hooksPath dyad/hooks` | The live value is **absolute**, so a linked worktree inherits the main checkout's hook *files* while the hooks exec the worktree's *code*. A worktree editing `pre-push` never runs the hook it is changing; deleting `dyad/hooks` in the main checkout silently disarms every worktree. Separately the hook discards git's `$1`/`$2`, so a push to any remote is judged against `origin/main` | adds authority | `git config --show-origin core.hooksPath`; `dyad/hooks/pre-push:4` has no `"$@"` |
| H12 | Non-HEAD refs are refused, not judged | So `git push --all` and any multi-branch push are refused outright | friction — *authority lost if removed:* the guards read the checked-out tree, so judging a non-HEAD ref would report a pass for an unexamined commit. **Keep** | `package.py:570-573`; `test_package.py:1071` |

## Link 5 — The git-to-GitHub boundary

| # | what the chain asserts | what is mechanically checked | class | evidence |
|---|---|---|---|---|
| L5-1 | Hooks are the only blocking enforcement; CI only detects | **Nothing at the hosting.** `main` unprotected, no ruleset, force-push and direct push unrestricted, one collaborator (admin) | adds authority | `/branches/main/protection` → 404; `/branches/main` → `protected:false, enforcement_level:"off"`; `/rulesets` → `[]`. A required check is blocked today because the workflows fire **after** the merge — it needs a `pull_request` trigger that #168 deliberately removed. **Both halves must move together** |
| L5-2 | CI is detecting-only, never on a branch or a PR event | **Confirmed exactly.** Zero `pull_request` triggers at HEAD; last 100 runs: 95 `push main`, 5 `push tag`, 0 PR events. Plus: every workflow's `paths-ignore` means a **ledger-only PR merge runs no CI at all** | adds authority | `grep -rn "pull_request" .github/`; `runs?head_sha=` → `total_count=0` for four sampled merge commits |
| L5-3 | `rows.py` fails any direct commit to `main` that is not ledger-only, so the exception cannot widen silently | **The fence visits zero commits on a PR merge** | adds authority | `git rev-list --first-parent --no-merges 3c7a500..0168ee0` → **0 lines** (the push that landed PR #358), and CI job 113384834035 logged `main fence OK` having judged nothing |
| L5-4 | Disposer ≠ proposer | **One identity for both parties.** Token scopes `gist, project, read:org, repo, workflow`; identity `pltrinh1122`, byte-identical to `git config user.email`, every commit author, and `merged_by` on every merged PR. `repo` + admin = unrestricted merge, push, force-push, tag, release | adds authority | `gh auth status`; `/collaborators` → one row, admin; 25/25 merged PRs `by=pltrinh1122`; 0 reviews on 20 sampled PRs |
| **L5-5** | "A merge before the `Y` is self-ratification and an incident whatever the outcome" | **Nothing would notice, ever.** Worked concretely for a web-UI merge of an open PR: the merge commit's ledger citation is free prose read by **no** guard; the row keeps `Y plan` and a legal state, so the fence, `check_disposed` and the transition table are silent; neither `disposed` nor the record grew, so Rule-7 p5's count matches; `dwork-trace` binds only a `done` row; `prs.py` runs pre-push on a branch, never at merge; and the post-merge CI judges zones and the tree, never a disposition | adds authority | `grep -rn "Merge pull request\|merges PR\|Y done\|mergedBy" dyad/guards/ dyad/scripts/ crafts/*/guards/` → one comment and transcript parsing only. **Historical sample of the 60 most recent merged PRs: 41 cite no d-work (ledger-only under `ledger-pr-merge: agent`), 19 cite one, and 19/19 are named in their row's `disposed` — 0 unnamed, 0 missing.** The naive matcher gives 2 false negatives; the column is free prose in at least four shapes |
| L5-6 | `row.disposed->pr` reads the `PR #n`/`merge #n` tokens (asserted in `falsification/message-bus-handover.md:23`, C13) | **False for the `PR #n` half.** `_MERGE = r"\bmerge #(\d+)\b"` matches only the `separate` form `Y merge #N`; the live preference is `with-done`, which writes `merges PR #N`. **140 of 243 rows cite a PR number in `disposed`; the register extracts exactly 1** — and its resolver is `world`, so even that is never resolved | adds authority | `references.py:90`, `:237-243`, `:412`; observed `warn [rule-20] row.disposed->pr: 1 reference(s)`. The `disposed`→PR citation is the only corpus-side link from a disposition to a merge, and it is unread. Unrecorded anywhere before this audit |
| L5-7 | "Until **d-work #24** (internal LAN git server with required status checks) lands…" (Rule-1 Enforcement) | **A stale citation nothing can catch.** Row #24 is `state: done` and titled "resolve the lost exec-bit gap…" — unrelated. No row tracks a git server with required status checks. The register kind `rule.text->row` has resolver `world`, so Rule text's 41 row citations are not even checked for existence | adds authority | `RULE-1-containment.md:50-51`; `rows/24.md`; `references.py:419`. Rule-1's own escape clause points at a closed, unrelated row, so the sentence reads as "a fix is tracked" when none is |
| L5-8 | The ledger's record of the `Y` precedes every merge it ratifies | **Satisfied locally, invisible at `origin`, checked by nothing.** 18 of 19 sampled code PRs had their row naming the PR at the merge's first parent. **One did not:** PR #315 (row #223) merged at `20:39:46Z` while `origin/main`'s row held only `N plan; Y plan`; the Done-`Y` existed as a local commit and reached `main` 32 s later. The merge body discloses it verbatim | adds authority | `gh api .../pulls/315`, `.../317`; `git log -1 a40cd8c0`. The invariant held in fact; nothing bounds the window, and an auditor reading only `origin` sees a merge with no recorded `Y`. **No `INCIDENTS.md` row exists for it** |
| L5-9 | CI and hosting are library adapters the package must not depend on | Confirmed — and the adapter's privilege is wide: `default_workflow_permissions: write`, `allowed_actions: all`, `sha_pinning_required: false`, floating `actions/checkout@v4` and `setup-python@v5`. Only `dyad-release.yml` declares `permissions:` | adds authority | `/actions/permissions`, `/actions/permissions/workflow`. Mitigation observed: `can_approve_pull_request_reviews: false` |
| L5-10 | "the platform cannot distinguish proposer from disposer" | **Confirmed and strengthened to an impossibility.** Every one of the last 60 first-parent merges has committer `GitHub <noreply@github.com>`, so an Agent `gh pr merge` and a human web-UI merge are **byte-indistinguishable**. `merged_by` is the one shared identity. The hosting's own disposer-shaped mechanism — a required approving review by a non-author — **cannot be satisfied here**: one collaborator, and GitHub refuses self-approval | **recorded impossibility on this kernel and this hosting** | `git log --first-parent --merges -60 --format='%cn'` → `60 GitHub`; 0 reviews. Every mechanical separation GitHub offers needs a second identity. **The mechanizable residue is content, not identity** — a check that the base row names this PR |
| L5-11 | Cross-zone work = separate branches, separate PRs | 175 remote branches, none protected; `delete_branch_on_merge: false`; all three merge methods enabled — **squash or rebase would destroy the merge-commit prose that is currently the only trace of a Done-`Y`** | friction — proposes no removal | `gh api .../dyad-system`; 60/60 recent merges are true merge commits |

## Link 6 — Tag and release

| # | what the chain asserts | what is mechanically checked | class | evidence |
|---|---|---|---|---|
| **L6-1** | A tag exists because the Operator answered `Y/N: release <tag>?` | **Nothing.** No code anywhere reads a release disposition. Strict parse of every row's `disposed`: **8 of 50 tags matched; 42 did not.** All 8 are rows #158 (3) and #241 (5) | adds authority (the counter-prompt is the only tie; off the table per the method) | `git tag -l` → 50; `grep -rn "Y release" --include=*.py --include=*.yml` → zero outside docstrings/tests; Rule-20's register has **no tag kind at all**, not even a `world` row. #70 names **five** tags, not three. Rule-11's counter-prompt text predates the first tag, so **none of the 42 predates the Rule** |
| L6-2 | Rule-7 p5 makes a dropped disposition visible | A disposition omitted from **both** balances | adds authority | `provenance/241.md`: 9 entries = 9 `disposed` entries. Only an external anchor — the tag itself — closes it |
| L6-3 | `disposed` is a reconstructible chain | `Y release <tag>` rides in the free-text `reason` slot; no form is defined and nothing parses it | adds authority | A naive grep matches `v0.4.0` inside `syseng-v0.4.0` — the #250 substring class, made worse by the bundle's unprefixed tag being a suffix of every craft tag. Four rows record the same fact in other shapes |
| **L6-4** | The kernel-only path judges every push | **A release-tag push runs zero guards** (the same early return as H1): the tag's *name* and *target* are new facts the local gate never sees; only CI checks them, after the tag is on `origin` | adds authority | observed `pushed_refs(["refs/tags/v0.12.1 …"])` → `(None, [])`; `package.py:549-580`, `:596` |
| L6-5 | `check_drift` is Rule-11 p4's converse | **The bundle's own unprefixed `vX.Y.Z` tag is not in the loop at all** — `live_components` returns the core plus craft dirs, and `tag_name()` can only build `<name>-v…`. The one tag Rule-11 p7 calls "the repo's one front door" has **no drift check, no warn line, nothing** | adds authority | observed guard output → exit 0, three skip lines, **no mention of `v0.12.1`**. Latent today (trees byte-identical) |
| L6-6 | Drift is caught before a push | Only where the tag resolves locally; a missing tag is one `warning: skip` that never sets `rc`. **Today 3 of 6 components skip, including the core craft** (`dyad/VERSION` 0.10.2, no such tag) — the core's drift is unchecked right now. Truly silent in two cases: a craft removed from the tree, and any path outside every craft root | adds authority | `bundle.py:92-94`; `package.py:607-612`. A tag moved with `git tag -f` also makes drift vanish, and nothing checks tag immutability |
| L6-7 | Rule-11 p2 refuses an unmet `requires:`; the floor check verifies a craft against the core | **Two different readers.** `unmet()` → the receiving repo's **`dyad/VERSION`** by semver, **no tag read**. `floor_problems()` → builds the **exact** tag `<req>-v<floor>` and warns-and-skips when absent | adds authority | `crafts.py:109-118`, `:300-337`. Live floors need `dyad-operator-v0.10.0` and `v0.9.1`; neither tag exists. **So three crafts' and disclosure's floor invariants have never run.** Plan #241 revision 2 retracts the opposite claim; row #248 is open on it |
| L6-8 | Rule-11 offers a batch form so several tags need one question | Its precondition is a Done-`Y` that **verifies** the content. **#241's order made it unavailable**, and nothing mechanical forces that order — `dyadlib.allowed` admits the `done→done` identity transition, and #158 appended three release dispositions to an already-`done` row | friction — *authority lost if the five questions were removed:* **all of it.** Rule-11's "a release publishes to the world" is the only fence on the one irreversible act. What the **batch form** costs is nothing: each tag is already named individually in the preceding evidence and Rule-2 Binding makes the `Y` ratify exactly the named set | #158 and #241's `disposed`. Measured: the five tags spanned **81m45s** of wall clock across five bare-`Y` keystrokes; `traces/241.md` puts the operator bucket at 92.6% of a 16h28m window. **The real constraint is scope, not mechanism:** when the tags *are* the deliverable, a Done-`Y` cannot precede and verify them, so the batch form is structurally out of reach — a Rule-5 coherence observation, not a fence |
| **L6-9** | #20: "CI publishes a GitHub Release automatically on a tag push" — still `backlog` | **The workflow exists and works.** 20 of 50 tag-push runs succeeded. The five 2026-10-08 failures are **not** permission errors: the step logs `a release with the same tag name already exists` — the hand `gh release create` beat CI by ~2 minutes each time | duplicates | `gh run list --workflow=dyad-release.yml` → 20 success, 30 failure; extracted logs for all five runs; `/actions/permissions/workflow` → `write`, so the #13/#16 403 condition no longer obtains. **50 tags, 49 releases, 20 CI-published → 29 published by hand, and the hand path runs no tag==VERSION check** |
| **L6-10** | A release `Y` is executed clerically | Nothing checks that it was. **`v0.11.0` is a ratified release that was never published** — the only one of 50 tags with no release | adds authority | Row #158 holds `2026-09-24 Y release v0.11.0`; the tag exists; `gh release view v0.11.0` → `release not found`. Run 36090475843 failed at `check and build` on the warning-treated-as-FAIL defect #241 later fixed. **No `INCIDENTS.md` row exists for it**; noticed 13 days later, incidentally, in plan #241 |
| L6-11 | The hosting is where the chain terminates | **No hosting-side fence of any kind**: no branch protection, no tag protection, no rulesets. Annotated tags carry `tagger=pltrinh1122` and messages naming only a version — **never a d-work or a disposition** | adds authority | `/tags/protection` → 404; `git for-each-ref` on three tags. Rule-2 Enforcement's stated condition extended to tags, which it does not name |
| L6-12 | Rule-8 records every mutation | Tagging and publishing are classed World actions, so no change-log row is owed. `workstation-corpus/CHANGELOG.md` holds **zero rows** | adds authority | file read. Consequence: 49 published archives have no corpus record other than each row's free-text `disposed` entry — the thing L6-1 and L6-3 show is unparsed and, in 42 cases, absent |

## Link 7 — The counter-prompt inventory (the main Agent's seat)

Thirteen counter-prompt forms the Rules require, classified. The Operator's own prompt asked for
the unnecessary ones; the honest answer is that there are almost none.

| form | Rule | class | what would be lost |
|---|---|---|---|
| plan-`Y` | 3 | **adds authority** | the only authorization for any mutation |
| Done-`Y` | 3 | **adds authority** | intent verification, and under `with-done` the merge ratification |
| merge `Y` for a PR whose d-work is not done | prefs | **adds authority** | a merge with no verification of the output |
| release `Y`, per tag | 11 | **adds authority** | the only fence on the one irreversible, world-facing act |
| destructive host action `Y` | 8 | **adds authority** | the act is irreversible by definition |
| intake `Y` | 3 | **adds authority** | a non-Operator proposal would open a row by itself |
| deferral / `archived` disposition | 3 | **adds authority** | the board would be the Agent's to curate |
| verdict-final `Y` | 2 | **adds authority** | the Agent would ratify its own verdict |
| plan batch / done batch | 3 | **adds authority**, fewer questions | nothing — Rule-2 Binding makes a batch `Y` ratify exactly the named set |
| release batch | 11 | **adds authority**, fewer questions — but **structurally unreachable** when the tags are the deliverable (L6-8) | nothing; the form exists and could not be used |
| `backlog`→`open` prompt | 3 + `provenance.py:262` | **friction, in shape only** | *authority lost if removed:* the row's first provenance entry would hold no Operator words (Rule-7 p4). Not removable. The cost is that **a bare `Y` can open a row but never start one** — four consecutive `Y`s in this session banked four rows and no work |
| the gate-after-Done repair (L2-4) | 3 + `prs.py` | **friction** | *authority lost if removed:* admitting `done` at the gate would void the Done-`Y`'s binding to a head. The ~3 extra dispositions per occurrence decide nothing new; twice in 9 days |
| the regex-repair `Y` (L2-8) | 3 + `prs.py:25` | **friction** | *authority lost:* none. One Operator `Y` was spent entirely on a citation matcher that counts prose and fenced code as a claim |

Two standing dispositions have already removed question classes and are the working precedent for
any further removal: `merge-disposition: with-done` (removed the duplicate merge question, ledger
#41) and `ledger-pr-merge: agent` (removed the per-instance ledger-PR question, with a scope that is
a path prefix, a whole-diff check before each use, and a merge commit that cites both).

## The composition — what this audit is actually for

Plan #251 F3 predicted the audit would rediscover known rows and that its value would be *ranking
and composition*. That held. Three compositions, none of which is a single row today.

**C-I. The chain's one mechanical fence rests on three unchecked things, and one edit defeats all
of them.** Between a disposition and a merge there is exactly one mechanical gate — `prs.py`'s
`"Y plan" in row.disposed`. It depends on (i) the Agent's own transcription, which is a recorded
impossibility (F6, C2: *nothing couples a state transition to a disposition*), (ii) a base ref the
Agent can move (L2-3, live right now), and (iii) a walk that visits **zero** commits on the merge
path (F2, L5-3). And the single sharpest break, found independently by two seats reading from
opposite ends: **flipping an existing `N` to `Y` in a row's `disposed` passes every guard on every
path** — `rows.disposed_problems` shape-checks only *added* entries, so an in-place rewrite yields
an empty `added` set (F5); `provenance._grows` keys on `(kind, date, text)` with the `note`, where
the verdict text lives, outside the key (C1); and Rule-7 p5's count is unchanged, 1 → 1. Two guards
over one store, and the flip is invisible to both. Nothing in the chain's history suggests this has
happened; the finding is that nothing would show it if it had.

**C-II. The two irreversible, world-facing acts are the two least-checked points.** A merge is
judged by a fence that visits no commits (L5-3) at a hosting with no protection, no ruleset, no
required check and no second identity, where a web-UI merge and an Agent merge are byte-identical
(L5-10) — and a release-tag push runs **zero guards and zero invariants**, skipping `check_drift`,
the one guard that exists for tags (H1, L6-4). Downstream of that: 42 of 50 tags carry no recorded
release disposition (L6-1), the bundle tag has no drift check at all (L6-5), and a ratified release
was never published without anything noticing for 13 days (L6-10).

**C-III. The impossibility that justifies all of it has expired, and its escape clause points at a
closed row.** Rule-1 says the hooks are the only blocking enforcement "until d-work #24 … lands".
Row #24 is `done` and is about an exec bit (L5-7). The falsification record behind that sentence
says protection is impossible because the repo is private on a free plan and the API returns 403
(H10). The repo is **public**; protection returns **404**, not 403; rulesets are readable and empty.
So the recorded impossibility behind C-I and C-II no longer describes the world, and the one fence
that would close H1, H2, H5, H6, H8, L5-1 and L5-3 at once is now reachable — but it needs **both**
halves at the same time: a `pull_request` trigger, which #168 deliberately removed for good
reasons, and a required status check. Neither half works alone.

## Falsification

| # | attack | result |
|---|---|---|
| A1 | The audit argues for fewer checks on the Agent — the conflict of interest in its purest form | **survives; it bound the method.** Of 13 counter-prompt forms, 11 are `adds authority` and none is proposed for removal. The three `friction` rows each state what would be lost, and two of the three cost the Operator nothing to keep |
| A2 | A six-seat cabinet is over-spawn for a reading task | **refuted, scoped.** The chain has these joints; one reader per joint is its own decomposition. Each seat was read-only, so the cost was tokens, not risk. Two independent seats converging on C-I's flip is the return on the redundancy |
| A3 | The audit will rediscover known rows and produce a bibliography | **survives as a finding, not a defect.** #24, #70, #20, #191, #248 and #250 all recur. What no row held is the composition above, and three things no row holds at all: C-I's `N`→`Y` flip, L6-10's unpublished `v0.11.0`, and L5-6's unread `row.disposed->pr` extractor |
| A4 | Easy agreement: the prompt names two things to find, so two things were found | **pushed.** Four findings are the *absence* of a gap, named with what was tried: C11 (record growth and the legacy list), H4 (the interpreter pin, attacked three ways), F1 (rename safety, attacked three ways), F7 (id immutability, three independent mechanisms). L5-5's historical sample found **0 undisposed merges in 60** and says so |
| A5 | L5-5's sample is biased — it only checked PRs that cite a d-work, so an undisposed merge is invisible to its own method | **survives, and sharpens the finding.** 41 of 60 legitimately cite nothing under `ledger-pr-merge: agent`; those were checked by diff instead. The method's blind spot is exactly the class the hosting also cannot see |
| A6 | C-I's flip is unreachable: only the Agent can write a row, and the Agent is already trusted to transcribe | **confirmed — and it is the honest reading.** The plan gate checks *that the Agent recorded a plan-`Y`*, not that the Operator gave one. Rule-7 Enforcement says as much. Recorded as the chain's load-bearing inference, not as a proposed fence |
| A7 | H9 is this session's own mess, not a system finding | **survives.** `.claude/` is created by the harness, is a classified infra path, and is absent from the gitignore seed, so every session on this kernel reproduces it and meets a refused push. Three `--no-verify` pushes are already on the record for a blocked local hook. A standing pressure toward the one bypass that voids the whole layer is a system finding |
| A8 | C-III overreaches: a public repo does not mean protection is configurable | **survives, scoped to the record.** The claim is only that the falsification record's stated premise ("private on a free plan … 403") no longer describes the repo. Whether protection *should* be set, and what it should require, is the Operator's |

## Candidate rows — surfaced, never opened

Strongest first. The Operator disposes each; none is opened by this d-work.

1. **Make `disposed` append-only by construction** — require `new[:len(old)] == old`, and add the
   record's `note` to `_grows`'s key. Closes C-I's flip, C1, F5. One guard pair, two one-line
   changes.
2. **Parse `disposed` into kinded entries** instead of searching free text — the plan gate requires
   `^\d{4}-\d{2}-\d{2} Y plan\b` on the *last* `plan` entry, and `release <tag>` joins Rule-3's
   grammar. Closes L2-1, L2-2, L6-1, L6-3; supersedes #250 by generalizing it.
3. **Judge the merge path** — call `check_merge` from `check_range` on `main` as `provenance.py`
   already does, and run the row rules over any branch that touches a row file. Closes F2, F3, F4,
   L5-3.
4. **`.gitignore` gains `.claude/`** (infra zone, one line, via the gitignore seed). Closes H9's
   removable half and the standing pressure toward `--no-verify`.
5. **Guard the tag push** — a `refs/tags/*` branch in `pushed_refs` that checks the tag against its
   `VERSION` and against a recorded release disposition; plus a `tag->row` reference kind. Closes
   H1, L6-4, L6-1, L6-11.
6. **Revisit the protection impossibility** — re-falsify `rule-1-containment.md`'s 403 premise, fix
   Rule-1's dead `#24` pointer, and decide the `pull_request`-trigger-plus-required-check pair as
   one question. Closes C-III, L5-1, L5-7, H10.
7. **Three owed `INCIDENTS.md` rows** found by this audit: `v0.11.0` ratified and never published
   (L6-10); the five hand `gh release create` calls of #241 causing five red CI runs (L6-9); PR
   #315's Done-`Y` reaching `origin` 32 s after its merge (L5-8).
8. **Fix `_MERGE` and correct the record** — `references.py:90` to the `with-done` form, and amend
   `falsification/message-bus-handover.md`'s C13, which asserts the tokens are read (L5-6).
9. Smaller, each one change: `cmd_evidence` refusing a dirty tree rather than reporting it (H9);
   `TRANSACTION_MODE` on `rows.py` so the evidence block says which fence ran (F8); `opened` added
   to the compared fields (F7); the memo key covering kernel package versions (H7); `setup-python`
   in the four workflows lacking it (H8); `permissions: contents: read` on the five non-release
   workflows and sha-pinned actions (L5-9); squash and rebase disabled so the merge-commit prose
   survives (L5-11); `rule.text->row` promoted from `world` to `row_exists` (L5-7); the bundle tag
   added to `check_drift` (L6-5); a plan-file freeze after its plan-`Y` (F9).

## Limits of this audit

- **No seat wrote, committed, pushed, merged, tagged, or ran a `gh` write or a host action.** The
  findings that describe a guard's behaviour on a crafted input were produced by importing the
  guard's own functions and passing strings, or in throwaway repos under the session scratchpad.
- **Most commit-time claims are code reads, not observed runs.** F2/F4's "passes with zero output"
  rests on code paths, the modules' own tests asserting `[]`, and 14 real unjudged commits — not on
  a constructed failing case. Each could become a test.
- **Whether the 42 undisposed tags lack a disposition or only its record cannot be settled from the
  repo.** That is exactly what #70 asks of the Operator's own chat record, which no seat can read.
- **Transcription faithfulness is unobservable from inside the repo by construction** (Rule-7 p2 and
  its attacks 2 and 10). F6 and A6 record it as an impossibility rather than a gap.
- **The hosting's own audit log is unreadable** (`404`, Enterprise/organization only), so a merge,
  settings change or force-push outside the PR and commit record cannot be established. Force-push
  history on `main` is likewise unobservable. The World (Rule-14 p4).
- **Pre-#168 CI history is not reconstructible** — the workflow files' git history is two commits in
  a seeded repo — so L5-2 is a claim about the live configuration only.
- **The installed-system case is unobserved.** H3(b) and H7's installed-root hole bite in a system
  that installs these crafts; no seat had access to one.
- `blocked` and `archived` are unexercised: zero live rows in either state.

## Addendum — seat 5's final pass

Three facts arrived after the tables above were written and sharpen them rather than change them:

- **The PR-event absence is exhaustive, not just current.** All **175** remote branches were
  searched for a `pull_request` trigger, not only HEAD: zero matches on every one. So L5-2's claim
  is about the repository's whole live surface, not a snapshot.
- **One merge body carries no disposition citation at all** — `74180d5` (PR #350), the release
  merge of #241. The convention that is the only human-readable trace of a Done-`Y` is not
  universal, which is a second reason it cannot be the check (L5-11).
- **The unreadable hosting audit log is part of the answer, not a limit of it.** `audit-log` is
  Enterprise/organization-scoped with no personal-account equivalent, so whether a merge came from
  the web UI or the API, by whom, and from where, cannot be established from the corpus or the
  hosting. The Operator's own browser security log is the only place it exists.

And the one-line summary the seat reached independently, which is the fairest statement of this
whole audit: **the record is clean; nothing holds it clean.** Over the 60 most recent merged PRs,
19 cite a d-work and 19 of 19 are named in their row's `disposed`; 41 are ledger-only and cite none
by design; 0 are unnamed. The chain has not been broken. What the audit found is that nothing
mechanical would show it if it were.

*Disposition: see ledger #251.*
