# Falsification record — Rule-16 (concurrent sessions) (ledger #106)

**Claim (operator, 2026-09-13):** the store should support concurrent sessions with minimum
collision surface and minimum merging (one session planning, another executing).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Every guard and test parses one table. | Survives | They parse rows; `dyadlib` is the one reader; the table parser stays for rendering and tests. |
| 2 | An untracked view scatters the record. | Survives | `package.py ledger` renders it; session start uses the render. |
| 3 | Two sessions allocate the same id. | Survives | Fetch before allocate; a true collision is a push rejection. |
| 4 | Planning and executing sessions edit the same row file. | Survives | Sequential by state (`planned` before execution); the fence keeps id/title immutable. |
| 5 | The transition commit cannot be checked against a base that has only the table. | Confirmed | `read_rows(at=)` falls back to the table at that commit; also serves upgrading instances. |
| 6 | git merges append-only tables cleanly. | Refuted | Neighbouring-line conflicts on every row edit; this session rebased ledger commits repeatedly. |

Local: 50 tests pass; render 95 rows; dwork_link passes against `origin/main` via the fallback.

## Rule-5 pairwise (Rule-16 added; Rule-3 edited)
- 16–3: Rule-3 owns lifecycle and fence semantics, cites Rule-16 for storage; Rule-16 names
  the fence it relies on; one-way each for what it does not own. 16–15: plan files unchanged.
  16–1: store stays agent zone. Others unchanged. Coherent, orthogonal.
- 2026-09-13, ledger #115 (T4): Store bullet 3 reworded from a session property to Rule-15's
  phases; 16–15 one-sided per object (15 owns the split and the transition, 16 the file), named
  in the new Boundaries bullet. See `agent-corpus/falsification/t4-phase-wording.md`.
## Rule-6: `row file`, `rendered view` added; `ledger` changed — users 2, 3, 4, 5, 16 read correctly.

Disposition: see ledger #106.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
Store and Enforcement name the row guard `dyad/guards/agent/rows.py` (was `main_fence.py`) and the PR guard `prs.py` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
Store bullets on id allocation, hand edits, the append-only fence and phase-ordered edits moved to
`crafts/sysarch/rules/stores.md` as the file-per-instance pattern (plan #160 D2, attack 13); the canonical path and the
transition table stay (#159: operator-craft semantics); Enforcement states the fence's three checks. Pairwise: 16–3, 16–15
unchanged; 16–11 the pattern is the craft's, the path Rule-16's. Coherent, orthogonal. Disposition: see ledger #160.

## Amendment — d-work #185 (2026-09-14, session presence store)
| # | attack | result | survivor |
|---|---|---|---|
| 1 | A lock/reservation on a row is simpler than presence + inference. | Refuted | Rule-16 already rejects locking for the store (disjoint files, collision only on id); a lock needs release semantics and risks a permanent block if a session ends without one — nothing here guarantees a clean session-end hook. |
| 2 | The harness's own session directory already shows this. | Survives, scoped | It shows session identity and live status, not which files a session's *current* d-work touches; platform-level, ephemeral, unreadable by a fresh session reading only the corpus. |
| 3 | A presence file can go stale. | Survives, scoped | Advisory only, never a guard FAIL; `seen` lets a reader judge freshness. |
| 4 | Row-id overlap is the wrong signal: the near-miss that prompted this was two *different* row ids about the *same file*. | Confirmed | The store lists files (from each row's stored plan), not just row ids; the check that matters is file overlap. |
| 5 | Semantic overlap detection needs real code. | Refuted | Not mechanized: the mechanism is write/read the store; judging whether an overlap matters stays inference, as Rule-5 and Rule-9 already work. |
Pairwise: Rule-3 gains one sentence on the session-start report; Rule-6 gains one vocabulary row (`presence file`, owner 16); no other Rule's concern moves — the store is Rule-16's own (d-work store), the guard checks shape only (Rule-12's concern, delegated), overlap judgment is Rule-9's kind of inference, not a new one. Coherent, orthogonal. Disposition: see ledger #185.

## Addendum — d-work #185 (2026-09-14, same-root as a sharper signal)
Operator directive after the plan-Y: verify the store distinguishes multiple sessions started
from the same working directory, not only file overlap. Confirmed live during this d-work's own
execution — a peer session's direct `git merge`/`git reset --hard` in the shared checkout landed
on this session's uncommitted commits while both were mid-work in the same directory; recovered
without loss, but by neither party's tooling. `root` (the resolved working-tree path) added to
the presence file; `same_root()` flags a live session sharing it, reported by `touch` and `list`.
Never a guard FAIL — same discipline as file overlap: the mechanism surfaces the finding, the
Agent (or Operator) decides to move the work into a worktree. Pairwise unchanged: still Rule-16's
own store; no other Rule's concern moves. Disposition: see ledger #185.
