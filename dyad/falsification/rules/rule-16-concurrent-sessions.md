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

## Amendment — d-work #37 (2026-09-16, `archived`)
Transition table gains `done → archived; archived → none`; the store sentence names `archived` as
`done`'s one further step, itself terminal. Attacks and pairwise: Rule-3's record, amendment #37
(attacks 1, 3, 5). Disposition: see ledger #37.

## Amendment — d-work #290 (2026-10-14, `backlog → archived`, an optional `mode`, and what a plan-less row costs the presence store)
**Claim (Operator, 2026-10-14, plan #290 revision 5):** the transition table has no exit from where
most of the board is. Store gains `backlog → archived`, and `dyadlib.TRANSITIONS`
(`dyad/scripts/dyadlib.py:443-450`) gains the same edge in the same commit —
`dyad/tests/test_dyadlib_rows.py:17-28` (`test_rule_16_bullet_enumerates_transitions`) parses the Store
sentence out of this Rule's text and asserts it equals the table, so the Rule and the code cannot diverge. The disposition that uses it is Rule-3's
**retirement form**, `Y/N: archive #a, #b, … #k?`, one Operator question over k rows, executed
clerically by `dyad dwork state <id> archived`, the verb the store already has. Two further changes belong to this store and are
attacked below: Store gains one **optional** field, `mode` (`explicit` or `implicit`, Rule-3
Scope), and Presence gains the sentence that says what an accreted row costs the `files` union.

Measured, at `main` 6ca6827: **`archived` has 0 uses in 280 rows**; **75 rows are `backlog`**, median
age **21 days**, 44 of them ≥14 days, the oldest 30; of the 37 rows ever born with a `Y backlog` first
entry, **35 are still `backlog`** — a **5.4% drain** — and `TRANSITIONS["backlog"]` is
`frozenset({"open"})`, so a surfaced row can only be retired by being *worked*.

| # | attack | result | survivor |
|---|---|---|---|
| 7 | A new edge reopens the promise this Rule's `#37` amendment bought: "state never regresses". | **Refuted.** `backlog → archived` moves away from work, never back toward it, and `archived` stays terminal. Both invariants hold untouched: `archived-is-terminal` (`not TRANSITIONS["archived"]`) and `done-never-reopens` (`TRANSITIONS["done"] == frozenset({"archived"})`), `dyad/scripts/dyadlib.py:597-598`. No state gains a successor it did not already have in the other direction. |  `archived` keeps exactly one meaning — retired from the working board — reachable now from the two states that can hold a row forever, `done` and `backlog`. |
| 8 | Then allow `backlog → done` too, and the parent gate's problem disappears without a new edge. | **Refuted.** `done` is the Operator's verification that a d-work's intent was delivered (Rule-3 Completion); a `backlog` row has delivered nothing, and `blocked → done` is refused for the same reason. Retirement says "this will not be worked", which is a different fact and needs its own state. | Two distinct exits, neither pretending to be the other: `done` for delivered work, `archived` for retired rows. The parent gate's own fix is Rule-3's — it accepts a `backlog` child — and is not smuggled in here. |
| 9 | An archive is a view: filter the board by age or by id and no state is needed. | **Refuted, and already refuted once** — this Rule's `#37` amendment, attack 2: age needs a clock, which a projection may not have (`crafts/syseng/rules/determinism.md`), an id cutoff is arbitrary, and "retired" is a fact about the row. Cited, not re-litigated. | The state stays stored, and nothing moves: the row file, its plan and its record stay where they are (Rule-20 resolves them as before). |
| 10 | The Agent will retire rows to tidy the board, which is the board becoming the Agent's to curate. | **Refuted by the same route as `#37` attack 4.** An Operator disposition names the rows; `dyad dwork state <id> archived` is clerical execution of it and a ledger-only commit, and no new verb is added — the one the store already has gains one legal source state. The Agent proposes the set and may never archive on its own judgment. | The retirement form is a counter-prompt, so the one question is the Operator's and the set is readable in it. |
| 11 | One question over k rows is a rubber stamp, and k could be 75. | **Survives, scoped.** It is Rule-3's batch discipline applied to a new class: a `Y` ratifies exactly the named set and `N` authorizes none of it, so the cost of a doubt is one re-reading of a list the Agent must still write row by row. The alternative is priced: clearing #259's 23 children one question at a time is 47 dispositions strictly one-per-question. | No ceiling is set here — the number of rows one retirement question may name is the Operator's, as the mandate ceiling is. |

| 12 | The row's fields are closed: `dyadlib.FIELDS` is `('id','title','opened','state','disposed','refs')` (`dyad/scripts/dyadlib.py:439`), pinned by a pure import-time invariant in the row guard (`dyad/guards/agent/rows.py:38-39`) and by `row-fields-match-dataclass` (`dyadlib.py:600`), so a seventh field either breaks the invariant or is silently dropped. | **Confirmed, and it chose the field's shape.** An extra `key: value` line parses clean today and is dropped, which is worse than refusing it. A seventh *required* field would also rewrite 280 row files to say what every one of them already means. | `mode` is **optional**: absent reads `explicit`, so no row is migrated and every row written before the field existed reads correctly; a row that carries it never loses it (the fence's own rule). The six required fields and their invariant are untouched, which is why this is one Store bullet and not a field-set change. |
| 13 | The presence store is unaffected by a row that has no plan file. | **Refuted, and it is this design's cost to this Rule.** `sessions.touch_from_open_rows` (`dyad/guards/agent/sessions.py`) builds `files` from the stored plan files of the session's `open` and `planned` rows (Rule-15 phase 1). An accreted row has none, so it appears in `rows` and contributes **nothing** to `files` — a reduction in exactly the coverage #185 built this store for: two sessions on *different* rows about the *same* file. | Stated in Presence, not fixed: the files are named in the **mandate's** plan file, which the mandate's own row carries while its children work, and reading a child's files through its `refs: parent #N` is the follow-on #290's plan names. Never a guard FAIL, as nothing in this store is. |

**Pairwise (Rule-5).** **16–3**: Rule-3 defines the states and the retirement disposition, Rule-16 the
store and the table — one-way each, as `#37` left them. **16–15**: the row file gains the optional `mode` field and the mandate pointer in `disposed`, and
attack 13's loss is a consequence of Rule-15 phase 2's plan-less row — Rule-15 owns the plan file,
this Rule owns the store that cannot find one. **16–2**: a
retirement is an Operator disposition Rule-2 already covers through Rule-3's reference; no event is
declared here. **16–1**: the store stays agent zone and a retirement is ledger-only. **16–7**: a
retirement writes one `disposed` entry and one record entry, so property 5's per-commit count holds
with no change. **16–12**: the table's test couples the Rule's sentence to the code
(`test_dyadlib_rows.py:17-28`), and the fence's own tests gain the new edge. **16–20**: nothing moves,
so every reference resolves as before. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #290.
