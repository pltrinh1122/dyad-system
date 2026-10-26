# Incident mode M — no legal order, no verb

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10. 11 rows of 140.*

## Definition
The mechanism: two separately-correct constraints — or a tool with no verb for the operation —
jointly leave a change the practice itself requires with **zero** admissible sequences, so the
Agent's only moves are to bypass a fence that runs and fails, to hand-write what no command
expresses, or to stop and ask. Nothing here is a wrong judgement: in every row both constraints
were read correctly and both held.

**What would have to change.** Wherever two constraints can jointly close every path, the one that
owns the later moment must carry an explicit admissible intermediate — a warn window, a declared
two-step state, or a CLI verb — so that a legitimate change always has at least one legal order.

Boundaries against the neighbours it is most easily confused with:
- **K, a plan incomplete against its own text** — K's tree admitted a correct plan and the plan's
  own lists failed to carry it; M's tree admits no correct plan. Test: on the tree as it stood,
  could a complete plan have been written? Boundary pair, both version/zone shaped: row 23 is K
  (plan #22's `crafts/sysarch/VERSION` bump was optional — not bumping was legal and is what
  happened), row 61 is M (the play-book the prompt asked for must live under `dyad/`, so tracked
  core files were unavoidable and both bump and no-bump failed the same guard).
- **L, a plan ordering no disposition sequence can authorize** — L missed an order that existed;
  M has none to miss. Test: does an admissible sequence exist on the tree as it stands? Existing
  but unchosen is L. Boundary pair: row 33 is L (plan #32 sequenced PR 2 behind a merge that did
  not come; a different sequencing was available), row 129 is M (a step that may only run after
  its own merge can carry no PR of its own d-work at all).
- **V, enforcement routed around** — V is a choice taken once M is met; M is the state of having no
  path. Row 76 is logged M because the closed door started it, with the hosting-API route as its
  secondary mechanism; row 30 is V, a `--no-verify` push where a legal route existed.
- **Q, an obligation no mechanism reads** — Q's obligation has a path and no reader; M's has a
  reader that refuses every path.

## Incidents (11)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-24 | #156 | no order of PRs could add the countersign craft; craft-first fails "no bundle row", row-first fails "not a craft in this tree" | Rule-1 splits `crafts/` (craft) from `BUNDLE.md` (infra), and `dyad/guards/infra/bundle.py` `check` tests both directions, so neither branch was pushable without bypassing a hook that runs and fails |
| 2026-09-25 | #166 | plan #166's realization is blocked before its first push; either new guard forces an edit to a released craft's pinned test | the released-craft side of the same pair: the tree then differs from `sysarch-v0.2.2` while `VERSION` is unchanged, and bumping `VERSION` fails the other direction because the bundle row must equal it |
| 2026-09-25 | #166 | revision 2 removed the coupling for the craft half but not the core; the play-book must live in `dyad/playbooks/`, so `infra/bundle` fails | the core craft is itself a released craft with its own tag; the two-file version pair `dyad/VERSION` (agent) plus `BUNDLE.md` (infra) is one commit spanning two zones |
| 2026-09-29 | #133, #191 | seven ledger-only PRs were pushed through the hosting API, so the pre-push hook and every guard never ran on them | the plan gate refused each ledger commit for citing no d-work, and a commit that opens or plans a row can cite none; this session was also fenced off a direct push to `main` |
| 2026-09-30 | #196 | a Done-`Y` named three PRs, two merges hit conflicts, and the conflict resolution could not be pushed at all | Rule-3 sets the rows `done` before the merge it ratifies and `done` never regresses, so `prs.py` refuses every commit of the fix; a ratified merge had no branch its fix could reach |
| 2026-10-07 | #241 | bumping `dyad/VERSION` 0.10.1 to 0.11.0 turned the bundle guard red at once and the push gate refused it | `bundle.check`'s #170 warn path needs the row's version to be a release tag of its own; 0.10.1 was never tagged, so a bump between releases is a hard failure until an infra-zone row Rule-1 forbids in the same PR |
| 2026-10-08 | #242 | after #242's Done was recorded the merge failed on a peer's appended `INCIDENTS.md` row, and the resolved branch could not be pushed | the same gate-after-Done closure as 2026-09-30, met from the peer-conflict direction; resolving voids the Done-`Y` and the gate refuses a row already `done`; the row says "no rule names the case" |
| 2026-10-09 | #256 | the renumbered row, provenance record and plan file of #256 were written by `sed` rather than through `dyad dwork` | no command expresses a renumber: `dwork new` allocates its own id and `dwork state` refuses `planned` to `planned`, so replaying three dispositions through the CLI would have dropped two and broken Rule-7 property 5 |
| 2026-10-09 | #256 | the batch completion reply cited four evidence blocks by digest instead of pasting them verbatim as Rule-2's Binding says | four blocks are 217 lines each, about 870 lines in one reply, and no mechanism expresses the prescribed artefact in a usable form; the departure was chosen and stated rather than taken silently |
| 2026-10-09 | #256 | three traces were written by native `dyad dwork trace` rather than through the run-book step that records an event | the runner writes its event into a workstation-zone file, a ledger-only commit may touch nothing outside `<instance>/d-work/`, and `pushed_refs` refuses a push whose working tree holds any change, so the prescribed step leaves the Done commit unpushable |
| 2026-10-09 | #256 | the change-log row for #256's `.git/info/exclude` revert can be carried by no PR of #256 | the revert may only run once the `.gitignore` line is on `main`, which happens at the merge the Done-`Y` ratifies, and by then the row is `done` and the plan gate refuses it |

## Pattern
All eleven are closures rather than errors, and ten of eleven were reported as blocking questions
or stated departures rather than bypassed — row 76 is the single exception, and that is the one row
logged with a route around every guard. Four sub-families, each a pair of constraints:

- **version/zone** (rows 2, 60, 61, 115): Rule-1's one-zone-per-PR against Rule-11 property 7's
  "each row's version equal to that craft's live `VERSION`", with `check_drift`'s converse behind
  it. Four rows over fourteen days.
- **gate-after-Done** (rows 82, 116, 129): Rule-3's "record the Done, then merge" against
  `prs.py`'s refusal of a `done` row, with Rule-16's no-regression behind it. Three rows.
- **clerical scope** (rows 76, 128): the ledger-only path's "nothing outside `<instance>/d-work/`"
  against the plan gate (76) and against the dirty-tree refusal (128).
- **no verb** (rows 121, 126): the store pattern's "no hand edits" with no renumber verb; Rule-2's
  verbatim-paste Binding with no compact form.

Recurrence after each mitigation a consequence cell describes:
- #156's own consequence cell names the PR-0 amendment that made an unreleased craft warn
  (commit `5c7818c`, 2026-09-24). Rows 60 and 61 post-date it by **one day** — the same pair
  reached from the released side, which the amendment did not cover.
- row 115's cell names backlog #170 "from the both-untagged side". The #170 warn path shipped in
  commit `8f79b93` at 2026-10-07T16:36:23Z; row 115 was logged in commit `cc64e3f` at
  2026-10-07T16:53:37-07:00, roughly seven hours later, on the same day, in the next d-work.
- #191's ledger-only exemption, named in row 76's cell as removing the reason for the API route,
  shipped 2026-09-29. Row 128 (2026-10-09) post-dates it: the same clerical-scope pair from the
  run-book direction, which the exemption does not touch.
- row 82's gap was opened as backlog `agent-corpus/d-work/rows/202.md` on 2026-10-01, naming three
  instances. Rows 116 (2026-10-08) and 129 (2026-10-09) post-date that row. A row is not a fence,
  and these two are the measurement of that.

## Mitigations (phase 2)
1. **Unreleased-craft warning.** `dyad/guards/infra/bundle.py` `check`, the `else` branch at
   `dyad/guards/infra/bundle.py:155-156` ("in the tree but unreleased … not yet bundled"), reached
   through `check_package` at `dyad/guards/infra/bundle.py:169`. Fires in Rule-11's runner
   (`package.py check`, registry label `infra/bundle`) and at `dyad check --guards --pre-push`,
   where `cmd_guards` runs every guard's `check_package` at `dyad/scripts/package.py:606`. Reaches
   row 2 exactly and no other row: 60, 61 and 115 are all released components, for which the hard
   FAIL at `dyad/guards/infra/bundle.py:154` still stands. **Shipped**
   (`dyad/guards/infra/bundle.py:156`). The mode recurred the next day, rows 60 and 61.
2. **The #170 warn path.** `dyad/guards/infra/bundle.py:143-147` — a row behind an unreleased live
   bump warns, but only when `(comp, ver) in tagged` and `(comp, live[comp]) not in tagged`
   (`dyad/guards/infra/bundle.py:146`). Same moments as 1. Reaches a released craft whose row names
   a **tagged** version while the tree runs ahead untagged. Does **not** reach row 115: 0.10.1 was
   never tagged, so the condition is false and control falls to the hard FAIL at
   `dyad/guards/infra/bundle.py:149`. Does not reach rows 60 or 61, which predate it.
   **Shipped** (`dyad/guards/infra/bundle.py:147`). The mode recurred about seven hours later, row 115.
3. **Rule-11 property 7's two prose sentences** — the unreleased-craft sentence (#156) and the
   released-craft sentence (#230), both in `dyad/rules/RULE-11-distribution-structure.md` property
   7. Moment: **inference, stated** at plan time; they are the clauses mitigations 1 and 2
   implement, and they reach the same rows those do and no others. Named here because phase 2 asks
   for the Rule text as well as the code.
4. **Rule-1's fence clause.** `dyad/rules/RULE-1-containment.md`, Boundaries: where a fence forbids
   what a Rule prescribes, "the Agent does the corpus-legal part it can, states the rest and asks;
   it never reads permission out of the Rule alone." Moment: **inference, stated** — a blocking
   question in the reply. Reaches every row of the mode as the disclosure discipline that got ten of
   eleven stated rather than bypassed; prevents none of them. Row 76 is the one row where it was not
   taken. Shipped as Rule text, never as a check.
5. **The ledger-only exemption.** `dyad/guards/agent/prs.py` `ledger_only` at
   `dyad/guards/agent/prs.py:54-57`, consulted by `check_transaction` at
   `dyad/guards/agent/prs.py:64-65`. Fires as a transaction guard at `dyad check --guards
   --pre-push` and at `dyad check --pr <base> <head>`. Reaches row 76 — it removes the plan gate as
   the reason for the API route. Does **not** reach row 128, whose obstruction is the *zone scope*
   of a ledger-only commit together with `pushed_refs`'s dirty refusal at
   `dyad/scripts/package.py:576-580`, not the gate. **Shipped**. Row 128 post-dates it.
6. **The CLI's flag refusal.** `DWORK_VERB_FLAGS` at `dyad/scripts/package.py:825-828` holds
   exactly `new`, `state` and `list`; unexpected flags and positionals are refused before any write
   at `dyad/scripts/package.py:909-915`. Fires at every `dyad dwork` invocation. This is row 121's
   *cause*, not its mitigation: there is no renumber verb, and `dyadlib.TRANSITIONS`
   (`dyad/scripts/dyadlib.py:594-599`, enforced at import at `dyad/scripts/dyadlib.py:612`) forbids
   `planned` to `planned`. Reaches no row of this mode. Shipped as a refusal.
7. **Backlog `agent-corpus/d-work/rows/170.md`** (`state: backlog`, opened 2026-09-25, refs 166
   156) names the version/zone gap. Not a fence and no moment. It is still `backlog` although
   `agent-corpus/d-work/rows/230.md` (`done`, 2026-10-07) is titled "closes #170"; row 115 is the
   recurrence that shows what #230 closed and what it did not. **Candidate.**
8. **Backlog `agent-corpus/d-work/rows/202.md`** (`state: backlog`, opened 2026-10-01, refs 185 186
   196 200) names the gate-after-Done gap and its three instances. It names the gap, not a fence to
   build. **Candidate.** Rows 116 and 129 post-date it.

Not inference-only: mitigations 1, 2 and 5 are mechanical and shipped. Between them they reach 2 of
the mode's 11 rows.

## Remediation candidate, under attack
**One fence.** In `dyad/guards/infra/bundle.py` `check`, drop the `(comp, ver) in tagged`
requirement at `dyad/guards/infra/bundle.py:146`, so that a bundle row *behind* a live `VERSION`
that is itself untagged **always** warns, whatever the row's own tag status; keep the hard FAIL for
a live version that is tagged with no row (`:154`), for a row naming a craft absent from the tree
(`:142`), and for a row *ahead* of the tree. What it checks: a craft-zone `VERSION` bump may land
before its infra-zone `BUNDLE.md` row, and the debt is collected at the release rather than at the
gate. Where it lives: the existing `infra/bundle` guard. When it fires: in Rule-11's runner
(`package.py check`) and at `dyad check --guards --pre-push`, through
`dyad/scripts/package.py:606`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | It weakens the guard: an infra row that never follows leaves `BUNDLE.md` permanently wrong, and the bundle release then publishes versions nobody pinned. | survives (scoped) | Only paired with a hard FAIL at the one moment the equality must hold — the release path, `cmd_bundle` and the `Y/N: release <tag>?` counter-prompt (Rule-11 Ratification events). Warn at the gate, fail at the tag. |
| 2 | It moves the mode rather than closing it: Rule-1 against any core-owned table that must agree with a craft-zone file closes the path the same way, and backlog row 248 is a `requires:` floor of exactly that shape. | confirmed | The fence is only the one enumerated case. The general claim — every cross-zone invariant needs a declared warn window — is not fenced by it and is not proposed here. |
| 3 | Rule-9 easy agreement: "warn instead of fail" read as obviously right on first reading. But #156's amendment and #230's warn path were each exactly that, and the mode recurred within one day of the first and within hours of the second. A third warn window carries a measured prior of recurring. | confirmed | The candidate does not survive as "this closes M". It survives as closing the single both-untagged case row 115 names, with its own test stated in advance: a fourth version/zone row refutes it. |
| 4 | Warning fatigue: the gate already prints `warn [bundle] …` lines and a permanently-warning tree trains the reader to skim them. | survives (scoped) | Admissible only if the warning names the owed infra-zone PR and the exact row text to write, and the release path fails on it — the debt collected at a named moment rather than by attention. |
| 5 | It reaches 1 of 11 rows. The gate-after-Done family (rows 82, 116, 129 — three rows and the one still recurring) and the no-verb family (121, 126) are untouched, and those are fenced by nothing at all. | confirmed | Priority does not survive: the candidate is the cheapest, not the largest. The largest unfenced sub-family is gate-after-Done, which row 202 already names and which needs its own fence proposal. |

## Proposed exit (phase 4)
**Open.** No exit of the three holds today. Mitigations 1, 2 and 5 are fences at named moments but
reach 2 of 11 rows and the mode recurred after each; rows 170 and 202 name gaps, not fences, so
neither is exit 2 as the play-book defines it; and nothing here is unfenceable on this kernel — the
version/zone and gate-after-Done pairs are both mechanically decidable.

Proposed to the Operator, not taken: two `backlog` rows that would make this exit 2.
- One refs 170, naming the fence of the candidate above — a bundle-row warn window for a
  both-untagged bump plus a hard failure on the release path. It would have caught row 115.
- One refs 202, naming the fence for gate-after-Done: a `prs.py` clause admitting a commit that
  cites a `done` row when the range's own commits change no file outside the already-ratified diff,
  or an equivalent recorded-but-not-yet-merged state between `planned` and `done`. It would have
  reached rows 82, 116 and 129.

Rows 121 and 126 (no verb) are proposed as a third, smaller row only if the Operator wants a
`dyad dwork renumber` verb; nothing in this audit argues they are worth package code on their own.

## Delta 2026-10-24 (#259 revision 5; 11 → 16 rows)
**Rows added:** 149 (#245/#290: `done` with `merges PR #355` never merged, six days), 169 (#243: `done`
with `merges PR #349`, closed unmerged), 154 (#290: no entry form for an inherited authorization — the
no-verb face), 188 (#326: a `DYAD_*` name needing the craft zone, the version/zone face), 207
(#369/#385/#388/#395: seventeen accreted rows closed by a hand-composed `Y done (mandate …)` entry, no
`--mandate` form on `dwork state` — the no-verb face). Secondary member of 173, 174, 175, 183 (X).
**Mitigations re-read from the code — one shipped, the first fence of this mode at a named moment.**
#202 (`0a4060e`, 2026-10-15): `rows.done_order_problems` refuses one commit that both records a merge-
ratifying `Y done` and sets `done`; `rows.landing_problems` refuses the commit that sets `done` while the
head the operative entry names is not an ancestor of `main`; `rows.done_recorded_not_closed` warns per
row in the interval; `cmd_dwork state` refuses the same before the first write (`package.py:1095-1125`).
Moment: the CLI call, and every push per commit (`check_transaction`, including a ledger-only branch's
commits and a merge commit against each parent). Reaches: the gate-after-Done face — rows 82, 116, 129
of the 2026-10-10 population and 149, 169 of this delta would be refused at the close, and the
recovery push would be legal because the row is still live. **Recurrence after it shipped:** none of
that face in nine days with five to seven seats live; row 194 (2026-10-21), the first conflicted Done
after the fence, shows the new shape — re-recorded `Y`, rebase, no deadlock. The hand-write face:
#290 shipped the accreted row's plan entry (`dwork new --mandate`) for row 154's shape; row 207 shows
the Done half still has no verb. The version/zone face: #170 is `archived` after #230's Rule-11 p7
sentence; row 188 (2026-10-15) post-dates it, on the `DYAD_*` naming table rather than `BUNDLE.md`.
**Exit after the delta:** split. The gate-after-Done cluster (rows 82, 116, 129, 149, 169 and the
secondary four) — **exit 1, fenced at a named moment** by #202, re-verified in the code today, zero
recurrence since. The no-verb face (121, 126, 154, 207) and the version/zone face (60, 61, 115, 188) —
open; #274 `backlog`. One candidate the delta adds, stated for the engineer seat: `dwork state <id> done
--mandate <id>`, copying the mandate's operative `Y done` entry with its heads (row 207).

## Delta 2026-10-26 (d-work #472, seat audit-e73be78c)

Rows from the delta of 2026-10-26 (index `2026-10-10-incident-failure-modes.md`, its section of that date, where the reconciliation, the code read at `d36b1bd` and the attacks are).

- **215** (2026-10-25, #417): a released craft leaving the tree had no order of PRs. Fenced since by #423 (Rule-11 property 7's departed-craft sentence and its `bundle.py` warning).
- **216** (2026-10-25, #433): a `VERSION` bump past a row naming an *untagged* version fails by design (`bundle.py:18–20`), and Rule-1 forbids the infra row in the same push. This is the version/zone face again (60, 61, 115, 188), one transitional state at a time. Proposed as P3: one more sentence and warning, as #230 and #423 did. **18 rows.** Status: split, as before.
