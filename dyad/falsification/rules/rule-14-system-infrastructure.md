# Falsification record — Rule-14 (System Infrastructure), Architecture Rule 4 (ledger #75)

**Claim (operator, 2026-09-13):** the System Infrastructure is the surface between The Dyad
System and The World and encapsulates integration dependency; kernel = Claude Code (or other
CLI agents), Python (pinned), Git (local, not hosted); library = everything not kernel.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Git local, not hosted" vs GitHub running every guard today. | Confirmed | GitHub is library, an adapter; #24 is its named replacement; property 3 requires a kernel-only path (gap I2). |
| 2 | Bash is not kernel; all five guards sit on library. | Confirmed | Gap I1: migrate to Python with tests. |
| 3 | Where does the OS sit? | Survives | The World provides the kernel; the OS is observed, never pinned (property 5). |
| 4 | Claude Code's version cannot be pinned by us. | Survives | Recorded as observed with the minimum last verified. |
| 5 | "Everything else is library" is unbounded. | Survives | Only what the package or the Agent's workflow invokes. |
| 6 | A manifest nobody reads. | Survives | `infrastructure.sh` will read it (gap I5); until then it is the declared surface. |

## Rule-5 pairwise statements (Rule-14 added)
- 14–1: manifest is agent zone; no path change. 14–2: no event. 14–3: gaps are d-works. 14–4:
  block. 14–5: this statement. 14–6: six terms. 14–8: host actions cross the surface through
  declared entries; Rule-8 classes them, Rule-14 declares them; one-way each. 14–9: this record.
  14–10: gaps framed per Rule-10. 14–11: manifest moves to the package root with A1; Rule-14
  names Rule-11. 14–12: Rule-12 chooses paths; Rule-14 names what they may call. 14–13
  (pending): Rule-13 chooses library entries; Rule-14 declares them. Coherent, orthogonal.

## Rule-6: six terms added, owner 14.

## Rule-5 pairwise (#125, property 3 sentence added): 14–2: Rule-14 owns the kernel-only path and the adapter row; Rule-2 consumes it as evidence, no check semantics move (S4). 14–3: Rule-3 states the state, Rule-14 defines it. 14–11: the scratch-install test (Rule-11 p5) has no kernel-only path — gap `check --install`, noted, Rule-11's. 14–12/13 unchanged. Coherent, orthogonal. Record: `agent-corpus/falsification/ci-absent.md`.

## #138 amendment (property 3: the kernel-only path is the evidence for every merge)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 7 | Property 3 already had a kernel-only path; #125 made it evidence only "when the CI adapter is absent", so CI's mere presence overrode it. | Confirmed | Order inverted: `check --evidence` on the exact head is always the evidence; hosted CI corroborates when it runs. |
| 8 | "Unreachable hosting" stops the ratified merge, not the checks: no push, no PR merge. | Confirmed | Git is kernel, hosting is library: the merge executes locally (`git merge --no-ff`, message citing PR and Done-Y) and pushes on reconnect. |
| 9 | A self-run check is a self-report. | Survives, scoped | The evidence block carries head, tree, dirty flag and a sha256 the Operator can reproduce; a lying Agent is still inference (Rule-2 Enforcement). |
| 10 | Plan gate and fence read `origin/main`; offline that is stale. | Survives, scoped | They read the local `main`; the reply states "evidence at <sha>, hosting unreachable"; re-run on reconnect before push. |
| 11 | Local merges bypass the LAN server's future required checks (#16). | Refuted for now | None exist; when #16 lands the fallback applies only when *it* is unreachable, which #16 must state. |

Rule-5 pairwise (#138, property 3 reworded): 14–1: no zone or path change. 14–2: Rule-14 owns the path and the evidence block; Rule-2 consumes it as the binding evidence and classes the local merge as clerical — dependency, no overlap. 14–3: Rule-3 owns the completion reply; Rule-14 says what the reply pastes, not when it is asked. 14–4: block intact. 14–5: this statement. 14–6: one term, `evidence block`, owner 14. 14–8: no host action (git is repo transaction). 14–9: this record. 14–10: framed in plan #138. 14–11: `check --evidence` is a `package.py` subcommand the Rule-11 runner exposes; Rule-14 owns its semantics (S4). 14–12: the subcommand carries tests. 14–13: no import. 14–15/16: the local merge respects the transition table and plan gate on local `main`. 14–17: no surface. 14–18: no Operator-run command. 14–19: no server. Coherent, orthogonal. Record: `agent-corpus/falsification/self-ci.md`.

Disposition: see ledger #75.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/infrastructure.py` → `dyad/guards/infra/manifest.py`, data `infrastructure_rules.txt` → `manifest_rules.txt` beside it; the scan covers `guards/` and `tests/guards/` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #154 (2026-09-14, craft reframe)
Boundaries: The Dyad System = Operator, Agent, the core craft, the Tended crafts, the instance
(vocabulary row edited, owner 14). Conditions: "a craft file". Manifest, kernel and evidence path
untouched.
| # | attack | result | survivor |
|---|---|---|---|
| 12 | "process kernel" (Rule-5 Homes) collides with Rule-14's `kernel`. | Confirmed | Rule-5 says "process kernel of a Rule that splits", never bare "kernel"; no new vocabulary row; Rule-14's `kernel` is untouched. |

Pairwise: 14–11: the system definition is Rule-14's term; the craft tree is Rule-11's. 14–1: a
Tended craft's files fall under the same manifest scan when they invoke anything — no zone or
path change now. No other concern moves. Coherent, orthogonal.

Disposition: see ledger #154.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
p1's six cells, p4 (library) and p5 (The World observed) moved to `crafts/sysarch/rules/manifest.md`; p4 here now points
there; the kernel (p2, p3 with the evidence block, Enforcement's run) stays. `manifest` stays an Agent term (its kernel
uses it; plan #160 attack 14); `library` moves. Enforcement's token-map mechanics stay pending #162 (D1). Pairwise:
14–11, 14–12 as above; 14–13 unchanged. Coherent, orthogonal. Disposition: see ledger #160.

## #168 amendment (2026-09-14): local CI first
| # | attack | result | survivor |
|---|---|---|---|
| A | Without PR-triggered CI a hook-skipping session merges unchecked. | Survives, scoped | The evidence block on the exact head is the gate (Rule-2 Binding, #138); CI was never the gate since #125. |
| B | `main` pushes still spend quota on ledger commits. | Confirmed | Workflows ignore `agent-corpus/d-work/**`. |
Pairwise: Rule-14 gains one clause on *when* hosted CI runs; Rule-14 owns the adapter's place, Rule-2 what a Y relies on, Rule-3 the plan gate's mechanism — no concern moves. Coherent and orthogonal with every other Rule as before.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
Enforcement's scan mechanics (the token classes, the stdlib / internal / third-party classification, `import:<module>`)
moved to `crafts/syseng/rules/imports.md` property 4; Enforcement keeps that the guard runs, what it fails and what it
warns; Boundaries name the craft rule. `import` leaves the Agent vocabulary for the craft's. Pairwise: 14–11, 14–12
unchanged; 14–13: Rule-13 keeps the process clauses, the craft the selection and the scan — no shared concern.
Coherent, orthogonal. Disposition: see ledger #162.

## Amendment — d-work #31 (2026-09-16, pydantic admitted to the kernel)
d-work #30 evaluated a schema-definition flow for the syseng craft and found pydantic the fitter
library on every ground except one: `pydantic-core` is a compiled wheel, and putting it on the
kernel-only path (property 3) would break `check --evidence`'s reproducibility on a bare kernel.
Its reconciliation named the fork explicitly and left it to the Operator. The Operator disposed it:
pydantic joins the kernel by name.
| # | attack | result | survivor |
|---|---|---|---|
| 13 | Kernel is explicitly "minimal" (three items); a fourth, third-party package changes it from zero-install to "run one `pip install` first," eroding property 3's basis. | Survives, scoped | Python itself already requires an install step matched to a pinned version — kernel was never "nothing to set up," only "nothing beyond {agent, Python, git}, pinned and observed." Extending that discipline to one named, pinned package is a difference of degree, not kind, and is scoped to pydantic by name — not a standing invitation for the next library to self-nominate. |
| 14 | `pydantic-core` is a compiled Rust wheel; a compiled dependency has no place in a kernel meant to run "on the kernel alone." | Refuted | Both existing non-Python kernel members are themselves compiled binaries (the CPython interpreter, git). "No compiled code" was never the real constraint; property 3's actual constraint is reproducibility without a library/hosting adapter — installable, pinned, offline-capable once installed, exactly as Python's own interpreter is. |
| 15 | This reverses d-work #30's own recommended path (a stdlib emitter) without amending that record. | Confirmed | #30's reconciliation named this precise fork as the Operator's to decide. That record is not rewritten — it stands as the reasoning that led here — and gains one pointer line to this amendment so it is not read as still-current advice against pydantic. |
| 16 | Nothing in the corpus imports pydantic yet; naming it kernel before any code uses it is premature. | Survives, scoped | Classification and adoption are separate acts — Rule-12 still chooses the implementation path when code is actually written. This d-work only clears the kernel-membership question; the manifest row pins a real, current release (2.13.5, checked via `pip index versions pydantic` the same day) rather than a placeholder. |

Pairwise: 14–13: Rule-13's criteria (`import-licenses`, `import-support`) already clear pydantic as
an import; this amendment only reclassifies its Rule-14 partition, not Rule-13's selection process.
14–12: Rule-12 still chooses the implementation path when code is written; this removes one
objection to that future choice and decides nothing about it. 14–11: no package-layout change, the
manifest stays at the package root. 14–1: no zone or path change. 14–6: the vocabulary's `kernel`
row is edited in the same d-work to keep pace (Rule-6 master record: on divergence the vocabulary
wins and the Rule is a bug). No other concern moves. Coherent, orthogonal.

*Residue, not fixed here:* `crafts/sysarch/rules/manifest.md`'s own header paraphrases the kernel
list and is now stale by the same margin; craft zone, its own PR (Rule-1: change the referent,
Rule-14, before the referrer, the craft rule).

Disposition: see ledger #31.

## Amendment — d-work #105 (2026-09-21, craft-contributed token map)

**Finding (workstation, intake):** `infrastructure_contrib.md` lets a craft contribute manifest
*rows* (Rule-11 property 2, #101), but `manifest.py`'s token map (`manifest_rules.txt`) is
core-only, with no equivalent. Three mechanisms verified against the live code: (1) `scan()`
treated every non-`.py` file under a scanned craft directory as shell text, so a craft's own
`guards/README.md` had its prose parsed for "invoked tokens"; (2) a craft's own script invoking a
tool only that craft knows about failed even after the craft declared the component, because the
token itself still resolved only against the core file; (3) `craft_python_dirs()` did not scan a
craft's `server/` directory — already an anticipated craft-file location
(`crafts/syseng/rules/invariants.md`'s own `exempt: crafts/*/server/*.py`) — so a sibling test's
import of the craft's own server module was misread as an undeclared third-party import.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A craft's `manifest_rules_contrib.txt` could silently redirect an existing core token to a different component. | Refuted | The merge is `dict.setdefault` per component and `check`'s own `tok2comp.setdefault` per token — both first-wins; a core-resolved token is never reassigned, only an unresolved one gains a resolver. |
| 2 | Skipping every non-`.py`, non-`.sh`, non-shebang file in `scan()` could silently stop scanning a real script with an unconventional extension. | Survives, scoped | Every script this repo or a craft ships either ends `.sh` or opens with a shebang line (the same two signals `shebang()` already used); a file with neither is, by the same evidence, not a script the package or craft actually executes. |
| 3 | `manifest_rules_contrib.txt` is a *new* trust boundary, wider than `infrastructure_contrib.md`'s (a row can only ever be inert data; a token can silence a real undeclared-invocation failure). | Survives, scoped | The same boundary `REFERENCES_CONTRIB` and `infrastructure_contrib.md` already accept for craft-shipped data (Rule-11 property 2); a craft's own manifest gap is reported under the contributing craft's own name, never silently, exactly as those two already are. |

Mutation: `craft_manifest_rules()` (new, mirrors `craft_infra_rows()`), merged into `check_manifest()`'s
`rules` before `check()` runs; `scan()`'s file loop only treats `.sh` or a real-shebang file as
shell text; `craft_python_dirs()` gains `server/`.

Pairwise: 14–11: no package-layout change, the contribution mechanism is Rule-11 property 2's, not
a new one. 14–13: no import. 14–12: the fix's own tests are the check. 14–1: agent-zone file only.
No other concern moves. Coherent, orthogonal.

*Residue, not fixed here:* `crafts/sysarch/rules/manifest.md` gains the matching craft-contribution
sentence in its own, later PR (Rule-1: this file, the referent, before the craft rule, the
referrer — the same order this record's own #31 amendment already established for this exact
craft-zone file).

Disposition: see ledger #105.

## Amendment — d-work #175 (2026-09-25, profiles and the instance contribution)
**Finding:** the core manifest (`dyad/infrastructure/INFRASTRUCTURE.md`) shipped dyad-system's own
operating rows — Gitea, Docker Engine + Compose, GHCR, curl — to every install, and
`crafts/sysarch/rules/manifest.md` said the running manifest "stays core: its values are observed on
this system". Observed values are instance. Survivor: one kernel, two library profiles, one manifest
as a union; a seventh cell `profile` (`authoring` | `operating` | `both`, kernel rows `both`); the
instance contribution `<host path>/INFRASTRUCTURE.md` beside the craft contributions; the four
operating rows move there (`workstation-corpus/INFRASTRUCTURE.md` on dyad-system).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Two manifests (authoring, operating) are simpler. | Refuted | Contradicts property 1 (one manifest) and duplicates the kernel, which then drifts between them. |
| 2 | A profile cell alone fixes the shipped operating rows. | Refuted | The rows still ship in the core file; they must leave it, hence the instance contribution. |
| 3 | The instance contribution breaks "one manifest". | Refuted | The union is one manifest exactly as craft contributions already are (#101); a component declared twice across core, crafts and instance fails naming both (`test_duplicate_across_core_and_instance_fails`). |
| 4 | Moving rows breaks token mapping mid-sequence. | Survives as ordering | The instance file lands first (unread by the old guard); this PR reads it and removes the core rows together. The four rows' `manifest_rules.txt` lines leave the core too: a core map naming a component only one instance declares would fail on every other system. |
| 5 | An instance row with no token warns forever ("declared but no token maps"). | Refuted by construction | The scan covers the core and the crafts only; the package never invokes an instance row, so `check` exempts instance rows from that warning (`untokened`). Core and craft rows keep it. |
| 6 | A kernel row marked `authoring` or `operating` is a quiet split of the kernel. | Refuted | `check` fails a kernel row whose profile is not `both` (`test_kernel_row_must_be_both`); the invariant `profiles-fixed` pins the set. |
| 7 | A craft's existing six-cell `infrastructure_contrib.md` now reads as malformed. | Confirmed, accepted | No craft in this tree ships one; the form (`manifest.md` p1) now says seven cells for all three sources, and core 0.10.0 is the minor bump that announces it. |
| 8 | The union changes dyad-system's manifest. | Refuted | Same 15 components, same values; rows only moved (the guard reports `15 components`, as before), plus the added `profile` cell. |

Pairwise: 14–1: the instance file's path is Rule-1's host path, read, not redefined. 14–11: the
instance contribution is instance data outside every craft (property 1); the craft contribution
mechanism (property 2) is unchanged. 14–13: no import. 14–12: the guard's tests carry the change.
14–19: server software rows are still manifest rows — now instance rows where the server is the
system's own. New term `profile` (owner 14); `manifest` redefined as the union (Rule-6, used by 14
only; it still reads correctly). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #175.

## Amendment — d-work #194 (2026-09-29, the pre-push hook judges what is pushed)
**Finding:** `dyad/hooks/pre-push` ran `package.py check --guards` and ignored the
`<local ref> <local sha> <remote ref> <remote sha>` lines git writes to its stdin. The transaction
guards judged `origin/main..HEAD` and every state check the tree on disk, so three pushes were judged
on something other than what left the machine: a branch other than the checked-out one (`git push
origin gap` while on `main`, and the reverse: a clean push failed over an unrelated HEAD), a dirty
working tree (the state checks read uncommitted files), and a tag pushed on its own (its commit is
not HEAD). Survivor: the hook runs `check --guards --pre-push`; `package.pushed_refs` reads git's
lines, skips a deletion and a ref whose commit `origin/main` already holds, refuses any other ref
not at HEAD (naming `git switch <ref> && git push`) and a working tree with tracked changes or
untracked files (ignored files excepted); otherwise the guards run as before with the transaction
head the pushed commit. Without `--pre-push` — by hand, and the evidence path — nothing changes.
Property 3 gains one sentence.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Judge each pushed ref in a temporary worktree at its commit, rather than refusing. | Refuted, scoped | It costs the full suite once per ref, and a worktree's hook environment is the #152/#169 class of bug. Refusing with the one command to run judges exactly what leaves, at no extra cost. |
| 2 | Use the remote sha as the transaction base, the true "new commits". | Refuted | The plan gate would then fail a follow-up push whose new commits do not re-cite the d-work — a behaviour change nobody asked for. The base stays `origin/main`; only the head moves. |
| 3 | Refusing a dirty tree blocks ordinary work (a stray scratch file). | Survives, scoped | Ignored files pass (`git status --porcelain` honours `.gitignore`; `test_c_a_dirty_tree_is_refused` pushes past an ignored `*.pyc`); scratch belongs outside the repo or in `.gitignore`. A dirty tree is exactly when the state checks judge the wrong thing, and the refusal names the files. |
| 4 | A release pushes a tag from a checkout that is not the tagged commit. | Survives | A ref whose commit is already on `origin/main` adds no commit and passes before any check (`test_e_…`, an annotated tag, with HEAD elsewhere and the tree dirty); a tag on an unpushed commit is judged like a branch. |
| 5 | Fetch `origin` in the hook to get a fresh base. | Refuted | The kernel-only path must not depend on the hosting (property 3). A stale `origin/main` only widens the range judged — and may refuse a ref another session already pushed, which a fetch clears — conservative either way. |
| 6 | An annotated tag's local sha is the tag object, never equal to HEAD, so every annotated tag on an unpushed HEAD is refused. | Refuted by construction | Each local sha is peeled to its commit (`<sha>^{commit}`) before the comparison; a ref that peels to no commit (a tag on a tree or blob) carries no commit to judge and is skipped. |
| 7 | `git push origin HEAD:refs/heads/x`, or several refs at one commit, confuse "the pushed commit". | Refuted | The comparison is by commit, not by ref name: every judged ref must peel to HEAD, so there is at most one pushed commit, and it is the one the tree on disk holds. |
| 8 | The refusal is a new way to skip the guards (a refused push is retried with `--no-verify`). | Survives, unchanged | `--no-verify` bypassed the hook before this change as well; Rule-1 already forbids bypassing a hook that runs and fails (#23). The refusal names the command that lets the hook judge the push, so the honest path is the short one. |

Pairwise (Rule-5): **14–1** Rule-1's push condition now names `check --guards --pre-push` and the
refs being pushed (Rule-1's amendment #194); containment's *commits* mode over the range is
unchanged, only the range's head is the pushed commit. Rule-1 owns what a transaction may touch,
Rule-14 the path that runs the check. **14–3** the plan gate still reads every commit message of
`origin/main..<head>` (attack 2); the head is the pushed commit, which the refusal makes HEAD, so
the gate judges the commits that leave. **14–7** Rule-7's transaction check runs over the same
range, now the pushed one; its semantics are untouched. **14–12** Rule-12 property 2's push-time
suite runs as before and now only on a push the hook can judge; the suite skip for a ledger-only
range reads the same head. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #194.

## Amendment — d-work #476 (2026-10-26, child C3 of #473: the evidence block cited by its sha256 and its brief form)
**Claim (plan #473, the Operator's `Y` of 2026-10-26, asking to reduce time and tokens in verification, evidence
collection above all):** the completion reply cites the evidence block by its `evidence-sha256` and its brief form,
as `check --evidence --brief` prints it — one count line, the baseline compared against, the warnings already
standing on that baseline folded per guard, every failing, skipped or other line, and every warning of a kind new
since the baseline (the Operator's `Y` escalating #476, 2026-10-26); the full block, over which the sha256 is computed unchanged, is
stored per checkout and never tracked (`<git common dir>/dyad-evidence/<sha256>.txt`) and shown byte for byte on
request (`check --evidence --show <sha256>`); the Operator may re-run the evidence on the same head and compare.

| # | attack | result |
|---|---|---|
| 1 | A brief block weakens the merge evidence: the Operator no longer reads every line. | Survives, scoped: the sha256 still covers every line, every failing or skipped line and every warning new since `main` are still in the reply, and the full block is one command away; what the Operator verifies — the same head yields the same sha256 — is unchanged. Only what is pasted shrinks. |
| 2 | A stored block can be edited after the fact to match a claimed sha256. | Refuted: the sha256 is recomputed by re-running on the head, never read back from the store; the store is a convenience for reading, not evidence of its own. |
| 3 | The store is per checkout, so another clone cannot show it. | Survives, accepted: the re-run on the same head is the cross-clone check, as before; showing is for the clone that ran it. |
| 4 | Folding standing warnings into counts hides a warning that changed, or a check that silently stopped running. | Refuted, scoped: a warning of a kind not already on `main` is printed in full; a check that stopped running changes the count line; with no baseline found nothing is folded, and a line says so; and the sha256 covers the full block, so any changed line changes it. |

**Pairwise (Rule-5).** **14–2**: Binding cites the block by its sha256 and its brief form; property 3 owns how it is printed, stored and shown. **14–12**: unchanged — `check --evidence` never reads the suite memo, so the evidence still observes. **14–6**: the vocabulary row `evidence block` is amended (owner 14, used by 2 and 14); both Rules read it correctly. **14–11**: unchanged — the store is under the git common dir, never tracked, never a generated file in the tree. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #476.

## Amendment — d-work #562 (2026-11-03, property 3: the evidence block's code digest and the hook's skip)
Claim (plan #562): the evidence block prints the head's code digest, the identity of its tree with `<instance>/d-work/`
and `<runbooks>/events/` pruned, and the pre-push hook skips the suite on a pushed tree whose code equals that of a head an
operative `Y done` names, as Rule-12 property 2 states; `check --evidence` itself never skips.

| # | attack | result |
|---|---|---|
| 1 | A new `code=` line changes every evidence sha256, so blocks before and after cannot be compared. | Survives, accepted: a block is compared only with a re-run on the same head under the same code, which prints the same line. |
| 2 | The hook now trusts a run it did not make. | Survives, scoped: only the run the operator ratified the merge on, for identical code; the operator decided it on plan #562; the guards still run on every pushed tree, and hosted CI corroborates on `main`. |
| 3 | "One push per cut" (plan #562 (a)) belongs in this Rule. | Refuted: how the merge verb and the automaton push is execution (Rule-2, Enforcement), not the kernel-only path; this Rule says only what the hook judges. |

**Pairwise (Rule-5).** **14–12**: Rule-12 property 2 owns the skip; property 3 names it and owns the block. **14–2**:
Binding's evidence still observes every root. **14–6**: the vocabulary rows `evidence block` and `suite memo` are
amended (owners 14 and 12); Rules 2, 12 and 14 read them correctly. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #562.

## Amendment — d-work #564 (2026-11-03, property 3: corroboration where the merge ran; the scheduled sweep)
Claim (plan #564 revision 2, the operator's plan-`Y` after the amend "evaluate expansion of the automaton scope to reduce
per CI run"): after a merge, corroboration runs where the merge ran — the automaton's own job, or hosted CI for any other
push to `main` — once per landed tree, the suite only when the landed code differs from code a done-`Y`'s evidence
passed; a read-only scheduled sweep twice a day runs every whole-store guard and the suite in the hosting's environment;
the push gate keeps every transaction guard and the checks of the records a push touches; `check --evidence` is
unchanged. The plan's attacks A1–A8 and E1–E5 are its record; the ones bearing on Rule text follow. One amendment here
covers the sentences this d-work changes in Rules 2, 3, 7, 12 and 14.

| # | attack | result |
|---|---|---|
| 1 | (A1) Hosted CI on `main` can be dropped. | Refuted: it is Binding's after-merge corroboration, and it never ran on the ledger pushes that dominate. It stays, slimmed (E2, E3), for pushes the automaton did not make. |
| 2 | (Revision 2's finding) The automaton's merges are corroborated. | Confirmed false: a push made with the workflow's token starts no other workflow, so the #558 cut and #562's merges had no corroboration; property 3 said hosted CI does it. Fixed by corroboration in the automaton's own job (E1); recorded as an incident in engineer's PR. |
| 3 | (E2) Corroboration can skip the suite. | Survives, scoped: only when the landed code equals code a done-`Y`'s evidence passed, the trust of #562 applied after the merge; the scheduled sweep runs the suite in the hosting's environment within 12 hours, the same corroboration of the same trust. The operator's decision 4, bound by the plan-`Y`. |
| 4 | (E3) Every merge needs its own run. | Refuted: a cut lands as one push (#562 (a)); a newer push cancels the run on the older tree, so the tree that stands is the one corroborated. |
| 5 | (A4) A whole-store gap goes unalarmed for longer. | Survives, scoped: at most 12 hours (the operator's decision 1); every done-`Y`'s evidence runs every guard, so no unalarmed gap reaches a merge or a release. Rule-7's sentence says where the alarm now sounds. |
| 6 | (A6) A missed or disabled sweep goes unnoticed. | Survives with the event: each sweep writes one event (events-only, Rule-3), which is also repository activity, and the automaton's run-book's health command is the last sweep's age. |
| 7 | The automaton both executes and checks its own merge. | Survives, accepted: it decides nothing in either act; the check is the same `check --corroborate` hosted CI runs, and the sweep re-checks independently. |
| 8 | The vocabulary already has `sweep` (Rule-5's pairwise check). | Confirmed: the new term is `scheduled sweep`, so neither row is redefined. |
| 9 | Rules 1, 3, 4 and 6 still name the CI job's steps by their old names, which corroboration replaces. | Confirmed (distribute's finding, the infra-zone PR): the job's steps became one, `check --corroborate`, so each Rule now names corroboration and its own step in it — `rule-1 containment (push range)` and `(tree)`, `rule-3 fence (push range)`, and `check` for the Rule-4 and Rule-6 guards. Same guards, same trigger (`main` pushed), still detecting. |

**Rule-6.** New rows: `corroboration` (owner 14; used by 1, 2, 3, 4, 6, 14 — Rules 1, 3, 4 and 6 by attack 9) and `scheduled sweep` (owner 14; used by 3, 7, 12, 14);
each listed Rule now uses the term in this sense.
**Pairwise (Rule-5).** **14–2**: Binding names corroboration where the merge ran; property 3 owns what it runs. **14–12**:
property 2 owns what the pre-push path runs and names the sweep as where the whole-store guards and the suite go;
property 3 owns the sweep's description. **14–3**: Rule-3's monitoring clause classes the sweep as no d-work; the events
it writes are Rule-3's events-only commits. **14–7**: Rule-7's state check is unchanged in content; only where its alarm
sounds is named. **14–5**: `sweep` and `scheduled sweep` are distinct terms. **14–1, 14–4, 14–6**: each Rule owns its
guard and names the corroboration step that runs it; property 3 owns corroboration. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #564.

## Amendment — d-work #593 (2026-11-04, property 2: a host that runs only the automaton; backlog row #55)
Accreted under mandate #570; plan `agent-corpus/d-work/plans/593.md`.

| # | attack | result | survivor |
|---|---|---|---|
| P5 | Property 2 must drop the CLI agent from the kernel (#55, workstation#224 gap e). | Survives, narrowed | The agent is the proposer; without it there is no dyad, so the kernel keeps it and stays one (a kernel row is `both`, `crafts/sysarch/rules/manifest.md`). What changes is the reading: the kernel-only path (property 3) and every automaton run need only Python, Git and pydantic, so a host running only those has no agent session, while its system keeps its agent party elsewhere. |
| A1 | Then the `operating` profile should mark Claude Code `authoring`. | Refuted | The profile says which activity of a *system* needs a row, not which host; an operating system still has an agent party. The manifest is unchanged. |
| A2 | "Needs only Python, Git and pydantic" is false: the automaton runs in a hosted job. | Survives, scoped | The hosting is a library adapter (property 3); what the automaton's code imports and invokes is the kernel's, which the manifest guard checks as it checks every invocation. |

**Rule-4.** Block holds. **Rule-6.** `automaton` is now used by Rule-14; its `used by` cell gains 14 in #585's window
(reported to counsel).
**Pairwise (Rule-5).** **14–2**: Rule-2 owns the automaton as execution; property 2 states only what it runs on. **14–8**:
Rule-8 classes what an automaton does on a host; property 2 says what that host needs. **14–11**: the profile cell's
meaning is unchanged (A1). **14–19**: Rule-19's automaton runs its read-only commands through the core runner, kernel
code. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #593.

## Amendment — d-work #617 (2026-11-06: the scheduled sweep becomes the automaton sweep, on activity)
Claim (plan #617, revision 3): the term `scheduled sweep` becomes `automaton sweep`, matching its verb (`sweep` alone is
Rule-5's). It runs after each landed merge, once per landed cut: every whole-store guard, the suite in the hosting's
environment, and drift. Its `--stores` mode runs the whole-store guards alone after each ledger push, in the
automaton's job. No clock starts either. What waits on time rather than activity (heads not landed, a code push not
corroborated, a stale board, work in flight, backlog hygiene) leaves the sweep's notice for the home's read, `dyad board
resume`, at session start and at each operator prompt. Rules 3, 7, 12, 14 and 19 read the new way; their records point
here.

| # | attack | result |
|---|---|---|
| 1 | Code can change between merges, so a sweep per merge misses some. | Refuted: the main fence refuses every direct code commit to `main` (Rule-3 Mechanisms); code arrives only by a merge (plan G1). |
| 2 | The stores change between merges, unswept. | Confirmed for the stores, so built: 315 ledger commits against 14 merges in one day, 36 of them the automaton's own with no pre-push hook (G2, G3). The `--stores` mode runs after each ledger push. |
| 3 | Stalls need a clock. | Survives, moved: none of them is an event, so the home reads them at each prompt, from the ledger, under a 5-second ceiling (G4, P5). |
| 4 | Outside drift goes unseen between merges. | Survives, delayed: found at the next merge's sweep; nothing ships before then (G5). |
| 5 | Renaming the term breaks installers. | Refuted: vocabulary terms are not on the frozen surface; `dyad automaton sweep` and `dyad-sweep.yml` keep their names (P6). |
| 6 | Rule-7's alarm is weaker without the 12-hour bound. | Refuted: a gap reaches the tree only by a push, and every ledger push now runs the stores check, so the alarm comes at the next push, never later than the bound did. |

**Rule-6.** `scheduled sweep` is renamed `automaton sweep` and redefined; `used by` gains 19, which already used the
term (3 7 12 14 19). Each user still reads correctly: Rule-3 Ledger (its notice, and the home's read), Rule-7
Enforcement (the alarm at the next stores check), Rule-12 property 2 (where the whole-store guards and the hosting's
suite run), Rule-14 property 3 (the definition's home), Rule-19 property 1 (an automaton's read-only health commands).
Provenance sentences that say "scheduled sweep" are history and keep their words.
**Pairwise (Rule-5).** **14–3**: the sweep is Rule-14's; the home's read of what it no longer posts is Rule-3's Ledger.
**14–12**: Rule-12 names where its suite runs, Rule-14 when. **14–7**: Rule-7's alarm reads the stores check Rule-14
schedules. **14–19**: Rule-19 keeps the event's `role`; the sweep is one runner. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #617.

## Amendment — d-work #618 (2026-11-06: property 3 names the check-trigger criterion and its five inputs)
Claim (plan #618, revision 2): which event runs each check is a decision criterion, `dyad/dmc/check-trigger.jsonld`,
home Rule-14 property 3. A check reads one or more inputs and runs on the union of their triggers. There are five
inputs: the code tree (after each landed merge), the ledger stores (after each ledger push, `sweep --stores`), the
event store (after each events-only push, `sweep --stores`), absence (the home's read in `dyad board resume` at each
operator prompt) and the outside world (the next merge's sweep). The suite splits into `suite` (code tree) and
`suite:live` (the `LiveCase` tests, stores). A test fails on an unclassed registry label or sweep part, and on an input
with no delivered trigger.

| # | attack | result |
|---|---|---|
| H1 | Every check fits exactly one class. | Refuted: `agent/references`, `agent/plans` and `agent/merges` each read records and code or commits, so each changes on a merge and on a ledger push. Survivor: a check declares its inputs, one or more, and runs on the union of their triggers; the class belongs to the input. |
| H2 | Four classes cover the inputs. | Refuted: `sysadmin/events` reads the run-book event store, which only events-only pushes change (Rule-3 Ledger), and #617's triggers sent the sweep only code pushes and ledger pushes, so the event store waited for the next merge. Survivor: a fifth input, the event store, its trigger each events-only push (the stores path of `dyad-automaton.yml`). |
| H3 | A test can list the checks the sweep runs. | Survives, scoped: the guards come from one registry and the sweep's parts are a fixed set, so the table is keyed by registry label and sweep part; a craft guard's row whose label is no longer registered is ignored, a registered label with no row fails. The guard contract is unchanged. |
| H4 | The suite reads only the code tree. | Refuted: the `LiveCase` tests (15 classes) read the live stores. Survivor: `suite` after each landed merge, `suite:live` in `--stores`; measured about 36 s for `suite:live` and 12 s for the whole-store guards, inside #617's 2-minute ceiling. |

**Rule-6.** No term is added: the five inputs and `suite:live` are named in the criterion and its table, and `automaton
sweep` keeps its definition, its `--stores` mode now also running after events-only pushes.
**Pairwise (Rule-5).** **14–3**: the absence input is read where Rule-3's Ledger already puts the home's read; Rule-3's
events-only commit is the event store's trigger, unchanged. **14–12**: Rule-12 property 2 names where the suite runs;
the split says which tests run where, and Rule-12's pre-push path is unchanged. **14–19**: the event store is Rule-19's
evidence; the criterion schedules its check and changes nothing of the event. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #618.

## Amendment — d-work #619 (2026-11-06: the audit's coded checks in the sweep; the report; a sweep not delivered)
Claim (plan #619): every coded check the audit and hardening play-books ran by their own steps runs in the full
automaton sweep instead, as the part `sweep_audit` — each a warning, its counts never-posted `reading:` lines — so it
runs after each landed merge and is told to the home once. Run with no `--row`, the sweep lands and posts nothing and
prints the report (every check line, findings `standing` and `new`, readings, the stall block, `checks-sha256`,
`report-sha256`), stored per checkout, which the audit reads in place of running those checks. Among the absences the
home reads, a sweep not delivered: no full sweep at or after the newest landed merge, or no stores sweep at or after
the newest ledger-only or events-only push. The check-trigger test also fails on a part classed with an input whose
trigger never calls it.

| # | attack | result |
|---|---|---|
| F1 | The no-`--row` sweep lands its health event, so an auditor's run writes an event recorded `role: automaton`. | Refuted: `land_events` returns before any landing without `--row`. Survivor: nothing lands; the audit's own record of the run is its run-book step's event, under the auditing party's role. |
| F2 | The exec-bit check runs only in the audit. | Refuted: `syseng/naming` reads `dyad/bin/*` and `dyad/hooks/*` at `100755` from git's index, and syseng is bundled with the core. Survivor: a duplicate, so the audit step goes and the report carries the guard's line. |
| F6 | The report can anchor the self-diagnostic's re-run by one digest. | Survives, scoped: the stall lines read time, the standing marks read the inbox and drift reads the world, so the whole text never repeats. Survivor: `checks-sha256` over the tree's own check lines, which repeats on one head; `report-sha256` names the stored text. |
| F7 | The audit's watermark, counts and listings can be findings. | Refuted: the watermark differs after every merge, a hosted run's interpreter is the runner's, and counts grow. Survivor: they print as `reading:` lines, never posted and never compared. |
| F9 | `sweep_ci`'s outside-world input is delivered by the merge sweep. | Refuted: `sweep()` never calls it; only the home's read does. Survivor: its input is absence, and the behavioural test fails a part classed with an input whose trigger never calls it. |
| F10 | Delivery counts successful runs. | Refuted: a sweep with a failing finding exits 1 and was delivered, and one still running after a merge would read as missing. Survivor: queued, in progress, success and failure count; cancelled and skipped do not. |
| F11 | Every ledger push starts a stores sweep. | Survives, scoped: the workflow's token starts no workflow, so the automaton's own pushes are swept by its same run's stores step and skipped by the delivery check; the sweep's own events commit is swept by none, its pre-push gate its only check. Stated, not fixed. |
| F18 | The automaton run-book's health can read delivery from the event store. | Refuted: `--stores` lands no event (#617). Survivor: the health reads the home's read, and a hosting not read is no pass. |

The plan's other attacks (F3–F5, F8, F12–F17) bear on the play-books, the audit module and the run-books, not on this
Rule's sentence; they are in plan #619's falsification table.

**Rule-6.** No term is added. `automaton sweep` gains the audit part, the no-`--row` report and the sweep not
delivered; each Rule in its `used by` still reads correctly: Rule-3 Ledger (the home's read, now naming a sweep not
delivered), Rule-7 Enforcement (its alarm at the next stores check, unchanged), Rule-12 property 2 and Boundaries
(where the suite runs, and the self-diagnostic reading the report), Rule-14 property 3 (the definition's home),
Rule-19 property 1 (an automaton's read-only health commands, unchanged). `coded check` gains that the
self-diagnostic reads them from the report; Rule-12, its one user, reads correctly.
**Pairwise (Rule-5).** **14–3**: Rule-14 says which sweep runs and when; Rule-3's Ledger lists what the home reads,
and a sweep not delivered is one of those absences — named in both, owned by Rule-14, read by Rule-3. **14–12**:
Rule-12 keeps the names of the two kinds of check and that a module carries one; Rule-14 says where the coded ones
run; the audit play-book reads them. **14–7**: Rule-7's alarm reads the stores check, unchanged. **14–19**: the sweep
is one runner of read-only health commands; Rule-19 keeps the event's `role`. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #619.
