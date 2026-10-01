# Falsification record — Rule-12 (verifiable code), Architecture Rule 2 (ledger #74)

**Claim (operator, 2026-09-13):** during implementation, select the path that maximizes the
yield of reusable code, because code can be mechanically verified.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Maximize" as a sole objective licenses scope growth against the plan-`Y` and unplanned refactors. | Confirmed | Choose among paths that satisfy the plan; reuse beyond scope is a new plan (property 4). |
| 2 | "Code can be verified" is a claim: none of the five guards has a test. | Confirmed | Code is verifiable only when it ships with its check (property 2); audit V1 records the gap. |
| 3 | Overlap with Rule-11 property 5 (scripted, tested install). | Survives | Rule-11: the package is tested; Rule-12: how to choose the path that yields testable code. One-way, named. |
| 4 | Some checks are inference-only (Rules 2, 5, 9, 10). | Survives | Property 1: what cannot be checked mechanically stays inference and says so. |
| 5 | More code is more surface. | Survives | The check is the condition of entry; unchecked code does not enter. |

## Rule-5 pairwise statements (Rule-12 added)
- 12–1: no paths. 12–2: no event. 12–3: scope is the plan's; one-way. 12–4: block. 12–5:
  this statement. 12–6: two terms. 12–8: a host action is not code; disjoint. 12–9: the path
  choice is a claim in the plan, falsified there. 12–10: alternatives are framed per Rule-10.
  12–11: named in Boundaries, one-way. Coherent, orthogonal.

## Rule-6: `implementation path`, `mechanical check` added, owner 12.

Disposition: see ledger #74.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
Enforcement: `check_rule_12` maps `dyad/guards/<corpus>/<entity>.py` → `dyad/tests/guards/<corpus>/test_<entity>.py` beside the `scripts/` mapping (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
`check_rule_12`'s mapping gains the craft branch (`crafts/<craft>/guards/<e>.py` → `crafts/<craft>/tests/guards/test_<e>.py`; a craft script's, when one exists, → `tests/test_<n>.py`) and runs each present `crafts/<craft>/tests/` as its own suite; Enforcement says so. Pairwise: 12–21 as in `rule-21-guard-containment.md`; 12–11: the runner still owns no semantics. Coherent, orthogonal.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
p1's design half restated in `crafts/sysarch/rules/guards.md`; `check_rule_12`'s mapping gains a craft's `projectors/`
(`crafts/<craft>/projectors/<n>.py` → `crafts/<craft>/tests/test_<n>.py`) so the moved projector code stays checked on every
push (plan #160 attack 5); Boundaries name the craft rules. p1's implementation half, p3, p4 stay pending #162 (D1).
Pairwise: 12–11 as in `rule-11-distribution-structure.md`; 12–20 unchanged. Coherent, orthogonal. Disposition: see ledger #160.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
p1 (code over inference), p3, p4 and Enforcement's test mapping moved to `crafts/syseng/rules/verifiable-code.md`;
the kernel keeps one property (code carries its check, run in CI) and gains the term `invariant` (Rule-6, owner 12):
the check a module carries for its own model, run by the runner's pass before any check (`dyad check`,
`check --guards`, `--evidence`: `[invariant]` lines) and at the mutating call sites (`dwork new|state`, `runbook run`);
its form (never `assert`; `INVARIANTS`, `check_invariants`, `InvariantError`) is `crafts/syseng/rules/invariants.md`.
`check_rule_12` keeps "run the tests"; the mapping is the craft guard `syseng/tests`, the `assert` ban and the
must-declare check the craft guard `syseng/invariants` (plan #162 attack 7: two predicates, two owners). `implementation
path` and `mechanical check` leave the Agent vocabulary for the craft's `CRAFT.md`; the Target keeps the phrase and
means the craft's sense. Pairwise: 12–11 the runner runs the pass, Rule-11's Enforcement names it, Rule-12 owns the term;
12–3 a false invariant is an incident (Rule-3's form, referenced); 12–20 unchanged; 12–13, 12–14 unchanged. Coherent,
orthogonal. Disposition: see ledger #162.

## Amendment — d-work #159 (2026-09-24, property 2: the suite is the runner's to run)

**Claim:** a release that ships a push-time test gate must also ship the directive to use it —
the Agent defers the suite to that gate and does not hand-run a whole test root.

Occasioned by an Operator prompt during the release d-work #158, and by #154's audit: the capability
to run the suite cheaply had existed all along (`check_rule_12` sets `DYAD_NO_NESTED_TESTS` for the
child it spawns), and the Agent still paid about three times for it, 134 times in one session,
3,894 s — the largest single number in that audit and required by no Rule.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A Rule that says "prefer this command" is not a Rule: Rule-4 wants a process binding, not a style tip. | Survives, scoped | It binds what the Agent does before asking for a Done-`Y`: the evidence it cites comes from the gate, not from a hand-run whose environment it may have forgotten. Written as a property of Rule-12's own check, never as advice. |
| 2 | Rule-13 already makes recurrence propose code, and #155 built it — the directive is redundant. | Refuted | Rule-13 binds the *plan* that proposes code. Nothing said the Agent must then use it, and the audit measured exactly that gap. |
| 3 | The gate cannot be deferred to where it does not run: no remote, no `origin/main`. | Refuted by #158 | `cmd_guards` returned before the gate on an unresolvable base; #158 moved the suite above that return and made an unknown range run it. This property lands after that. |
| 4 | "Never hand-run" is too absolute: a failing case needs its own output. | **Confirmed — and the property says so** | It names `dyad check --tests <target>` for one module, class or method as the debugging path, and reserves the objection to a whole root, which the gate has already covered. |
| 5 | It slows the Agent: it must push to learn that a test fails. | Survives, scoped | It must push *or* run one target. What it may no longer do is re-run 490 tests it did not change. |
| 6 | The directive belongs in the incident-hardening play-book (#137), not in a Rule. | Refuted | That play-book is a procedure for a recurring decision about incidents; this is a standing constraint on every d-work, and a play-book is read by a Rule, never instead of one. |

Pairwise (Rule-5): 12–14 property 3 owns *where* the kernel-only path runs and when it is the merge
evidence; property 2 owns *who runs Rule-12's suite*, and cites Rule-14 rather than restating it.
12–13 Rule-13 owns the move from inference to code (recurrence proposes it); property 2 owns the use
of the code once it exists — no shared ownership. 12–11 the runner is Rule-11's and runs the pass;
Rule-12 keeps its check's semantics, unchanged. 12–3 a d-work's completion evidence is Rule-3's; this
property says only which run produced it. 12–1, 12–2, 12–15, 12–16, 12–20 untouched. Coherent,
orthogonal. Disposition: see ledger #159.

## Amendment — d-work #199 (2026-09-30, node N2 for backlog row #162: property 2 gains the suite memo)

**Claim:** the pre-push path may skip Rule-12's suite when a suite memo on this checkout proves the
same tree already passed every root in the same environment, and `check --evidence` never reads one.

Occasioned by #161's C2: `check --evidence` runs the suite on a branch head, and the post-merge push
of `main` runs it again over a merge commit whose tree, for 53 of 112 merges in seven days, is the
same tree. Mechanism (`dyad/scripts/package.py`): `check_rule_12` and `cmd_tests()` without a target
write `<git common dir>/dyad-suite-memo/<key>` after a full, all-roots pass on a clean tree
(`os.replace`, pruned to the newest 64); `suite_gate` reads it only under `pre_push`, as its last
clause before "run" — first `head`'s own tree, then a ledger-only branch's merge-base tree.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Unobserved evidence: a memo puts an assumed pass where Rule-3 wants every result "as observed, never assumed" (#161 C2 attack 1). | **Refuted by construction** | The memo is read in one place, `suite_memo_clause`, reached only from `suite_gate` under `pre_push`. `cmd_evidence` runs `cmd_check` (the suite, observed) and then `cmd_guards()` without `pre_push`; `check --guards` without `--pre-push` never reads it either. Tests plant a matching memo and assert both still run the suite and record no memo read. The skip line is printed by the hook, never into an evidence block. |
| 2 | Key completeness: a tree hash misses inputs the suite reads outside the tree. | **Confirmed; survives as a closed list, stated** | Keyed: the tree; `sys.executable` and `sys.version`; `git --version`; the sorted roots `test_suites()` runs (a craft added or removed is a new root); the env knobs the runner, `dyadlib` and the craft guards read (`DYAD_INSTANCE`, `DYAD_HOST`, `DYAD_HOST_ZONE`, `DYAD_OPS`, `DYAD_RUNBOOKS`, `DYAD_ROLE`; not `DYAD_SESSION`, a presence id, nor `DYAD_NO_NESTED_TESTS`, unset whenever a memo is read or written); a digest of `refs/tags` (`check_drift`); a digest of the instance's `*.local.txt` (git ignores `provenance_legacy.local.txt`, which the provenance guard reads, so it can differ between worktrees of one tree); the UTC date, which bounds every unkeyed input to one day. Not keyed, stated: installed third-party packages (none is imported today; pydantic is a kernel row "adopted when a plan first imports it" — that plan adds its version to the key), and `origin/main` (below). A miss only costs a real run. |
| 3 | `origin/main` is an input — real-repo `check --guards` children judge `origin/main..HEAD` — and plan #199 listed the base sha in the key. | **Survives, scoped; a departure from the plan's key list, reported** | The history-dependent verdicts are the transaction guards, and the push gate runs every one of them on every push, unmemoized: the memo skips the suite, never a guard. Keying the base would also make the second clause unreachable by definition (a ledger branch behind `origin/main` is one whose base has moved past its merge-base). The node brief omitted it; the omission is stated here and in the completion reply. |
| 4 | A stale memo after a force-push: history is rewritten, the memo still says "passed". | **Survives** | The memo is keyed by tree, never by commit or ref; a force-push to a tree that passed is still that tree, and one to any other tree is a miss. What depends on history is attack 3's guards, which run. A memo past its day is dead by key. |
| 5 | A memo shared across worktrees lets one worktree's pass stand for another's different state. | **Survives, scoped** | Sharing is the point (the merge runs in one worktree, the push from another checkout of `main`). What differs between worktrees of one tree is untracked or ignored state: untracked files make the tree dirty, and no memo is read or written then; the ignored instance data the guards read is keyed (attack 2). The ignored build output (`__pycache__/`, `*.pyc`) cannot change a verdict. A test writes from a linked worktree under the hook's `GIT_DIR` and finds the file in the common dir, and a hit from the main worktree. |
| 6 | A poisoned memo: anyone can write a 64-hex file by hand and skip the suite. | **Survives; trust model stated** | Writing `.git/dyad-suite-memo/` needs the same user, on the same checkout, as editing `.git/hooks`, setting `core.hooksPath` or pushing with `--no-verify` — each of which already skips the whole hook. The memo grants that party nothing it lacks; the hook is the Agent's fence against its own mistakes, never a boundary against the checkout's owner. The merge evidence never reads it (attack 1), and hosted CI corroborates on `main` after the merge (Rule-14 property 3). A file that is not the key of a pass only ever produces a hit for the exact key it names. |
| 7 | A partial, failed, targeted or moving run could be memoized. | **Refuted by construction** | Only `check_rule_12` (every root) and `cmd_tests()` with no target write, only when every root passed, and only when the parts read before the run equal those read after it (a commit, a tag or an untracked file mid-run is no write). Tests: a dirty tree, a dotted target, one root by path and a failure each leave the store empty; a clean full pass writes exactly its key. |
| 8 | The second clause (ledger branch behind `origin/main`) passes a merge commit's own changes as ledger-only. | **Confirmed of the walk alone; closed** | The three-dot walk (`dyadlib.ledger_only`, the plan gate's) reads non-merge commits only, so the clause also requires the tree difference between the merge-base and `head` to lie under `<instance>/d-work/` (`dyadlib.ledger_only(..., merge_base=False)`); the premise that a ledger-only difference cannot change a suite's outcome is #155's, unchanged. A branch with one non-ledger commit runs (tested). |
| 9 | N1's invariant — an unknown or unreadable range runs — is weakened by a memo hit. | **Refuted** | The memo clause is reached only after the range was read and found neither empty nor ledger-only; an unresolvable base or an unreadable range returns "run" before it. |

Pairwise (Rule-5): 12–2 Binding names `check --evidence` as the merge evidence; the memo is never read
there, so the Binding is unchanged and property 2 cites it. 12–3 the completion evidence is Rule-3's
and pastes the evidence block, which carries no memo line; property 2 changes which push runs the
suite, not what a Done-`Y` is asked on. 12–11 the runner is Rule-11's and owns no semantics; when the
suite may be skipped is Rule-12's own check's concern, placed in the runner as `check_rule_12` is. The
memo lives under the git directory, never in the tree, so property 6 (generated files never tracked)
is not engaged and no craft carries instance state. 12–14 property 3 owns where the kernel-only path
runs, that the pre-push hook is the only check before a merge and that `--evidence` is the merge
evidence; property 2 owns only when its own suite may be skipped on that path, and cites property 3
rather than restating it — the guards the hook runs are never skipped. 12–16 the memo is not the
d-work store and touches no row, plan or presence file; concurrent sessions on one checkout share it
by design, each write atomic and each file named by its own key, so two writers never collide on
content. 12–1 `.git/` is no zone's path and the memo is no repo transaction. 12–6 one term added,
`suite memo`, owner 12, used by 12. 12–8 the memo is a file the runner writes inside the checkout's
git directory, as git writes its index — stated as inference, not a host action the Agent takes.
12–4 the block is unchanged. 12–7, 12–9, 12–10, 12–13, 12–15, 12–18, 12–19, 12–20 untouched.
Coherent, orthogonal. Disposition: see ledger #199.

## Amendment — d-work #199 (2026-10-01, node N5 for backlog row #176: property 2 gains the installed-root skip)

**Claim:** the pre-push path may skip a test root whose installed tree is byte-identical to its craft
registry row (Rule-11 property 2), and `check --evidence` runs every root.

Occasioned by #176 (relayed via #175 S6): a system that installs the crafts and authors none of them
ran their authoring suites on every push (countersign-system: 494 core tests per push), over trees it
had installed and never changed. Mechanism (`dyad/scripts/package.py` `installed_roots`, consulted by
`cmd_guards` only under `pre_push`, only after `suite_gate` — its memo clause included — has said
run): a root `dyad/tests` maps to the `dyad-operator` row and `dyad/`, a root `crafts/<c>/tests` to row
`<c>` and `crafts/<c>/`; `craft.unmodified` compares the row's `sha256` with `craft.tree_sha`, the
computation `dyad craft install` already writes. The roots left run through `cmd_tests(roots=…)`, a
partial run, never memoized.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A modified file under an installed root still skips. | **Refuted by construction** | The hash is `distribute.archive_sha256` of the tree on disk: one byte, one mode bit, one added or removed file (untracked or ignored included; only `__pycache__` and `.git` are skipped) is another sha, and the root runs. Under `--pre-push` the tree is the pushed commit's (#194 refuses a dirty one). Tested: a test file added under `dyad/tests` runs the core root. |
| 2 | A registry row edited by hand (or a sha recomputed to match a modified tree) buys a skip. | **Survives, scoped** | A range that changes `crafts/REGISTRY.md` runs every root, so a hand-edited or a newly written row is first judged by a full run in this system; tested. A row edited in a range the hook never judged (`--no-verify`, a hook unset) is N2's attack 6 again: the party that can do it can already skip the whole hook. The merge evidence never reads the registry for this purpose (attack 4). |
| 3 | An authoring repo that also has rows skips the suite of what it authors. | **Refuted as stated; scoped** | A craft authored here has no row (Rule-11 property 2: `dyad craft list` shows it `authored`), so its root runs; this repo's registry has no row at all and its gate is unchanged. A row exists only for a tree an install wrote, and the first edit to that tree changes its sha. A repo that installs one craft from elsewhere skips that craft's root alone, exactly while it is the installed bytes. |
| 4 | The evidence path loses roots: an assumed pass in the merge evidence. | **Refuted by construction** | `installed_roots` is called from `cmd_guards` only when `pre_push` is set; `cmd_evidence` calls `cmd_check()` (every root, observed) and `cmd_guards()` without it, and `check --guards` without `--pre-push` never calls it. Tested: under `--evidence` the suite runs through `check`, and without `--pre-push` `cmd_tests` gets every root; neither prints an `installed unmodified` line. Every merge an operating system makes still runs every root (Rule-14 property 3). |
| 5 | Plan A4: what an installed system checks at push is the Operator's policy — a preference (`system-profile`) — not a refactor. | **Survives, scoped (as the plan's A4)** | A preference is refuted as the mechanism: an Operator-owned value set to `operating` in an authoring repo would drop the suite by configuration. What skips is decided by bytes alone — only a tree identical to a recorded install — and only at the push gate, never at the merge evidence. It still changes every installed system's push and edits Rules 11 and 12, which is why the plan named both amendments for its `Y` to bind and placed this node last; conceded, as there, that the Operator may want it decided alone, and an `N` re-plans this node only. |
| 6 | Roots are not independent: a craft's tests import the core, and the core's tests read the crafts and the instance. | **Confirmed; closed for the first, scoped for the second** | A Tended craft's root skips only while the core's tree is unmodified too (tested: a core edit runs every root). Neither `requires:` between Tended crafts nor the instance is hashed: the core's live tests (`LiveCase`) read the instance's stores, which change on every push. The guards judge those stores on every push, unmemoized; the live tests over them run at every merge's evidence and on any push that changes the registry. A live test that fails where its guard passes is found there, one merge later at most. |
| 7 | The installed tree passed in its authoring system, not in this one: another interpreter, another git, another instance. | **Survives, scoped** | The first push after an install changes the registry and so runs every root here (attack 2). An interpreter or git upgrade later is not keyed (unlike the memo, N2 attack 2): it is observed at the next `check --evidence`, which runs every root. |
| 8 | A bundled craft (Rule-11 property 2) is written by `dyad install` with no row, so its root never skips. | **Confirmed; out of scope, reported** | Conservative: no row is "run". The missing row is backlog #201 (opened 2026-10-01), which also blocks `dyad craft install` of that craft afterwards; when #201 writes the row, this clause skips that root with no further change. |
| 9 | A partial pre-push run writes a suite memo under the all-roots key, so a later push skips roots that never ran. | **Refuted by construction** | `cmd_tests(roots=…)` sets no memo parts, as a targeted run does (N2 attack 7); the memo key's `roots` part stays `test_suites()`, every root, so a hit still means every root passed. Tested: the gated push leaves the memo store empty, and a full run after it writes exactly its key. The memo clause precedes this one, so a memo hit skips every root before any hash is computed. |
| 10 | An unreadable range or an unresolved base skips through the registry. | **Refuted** | `installed_roots` returns every root when `range_paths` is None, and `cmd_guards` never calls it without a resolved base; N1's invariant ("an unknown range runs") is unchanged. |

Measured (a scratch operating install; Falsification A5's method): see the completion reply of node N5
and the audit M.

Pairwise (Rule-5): 12–11 the registry and its row are Rule-11's (property 2, amended in the same
d-work); property 2 here reads the row and owns only when its own suite may skip on the push path.
12–2 Binding names `check --evidence` as the merge evidence, which runs every root; unchanged. 12–3
the completion evidence pastes the evidence block, which never carries this skip line. 12–14 property
3 owns where the kernel-only path runs; property 2 cites it and skips no guard. 12–1 the registry stays
craft zone and is written by an install, never by this check. 12–6 the term `craft registry` gains
Rule-12 as a user; its definition gains the core row. 12–16 no row, plan or presence file is read.
12–4 the block is unchanged. 12–7, 12–8, 12–9, 12–10, 12–13, 12–15, 12–18, 12–19, 12–20 untouched.
Coherent, orthogonal. Disposition: see ledger #199.
