# Incident mode X — tail-append contention under a held PR

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 revision 5 (seat `audit-89a934d6`),
2026-10-24; 6 of the 69 rows the delta derivation read (rows 145–213), a mode no record of the
2026-10-10 derivation names. Detects and counts; disposes nothing (play-book
`dyad/playbooks/incident-hardening.md`, Conduct). Letter continues the 2026-10-10 taxonomy (A–W); the
index is `2026-10-10-incident-failure-modes.md`, delta section of 2026-10-24.*

## Definition
A PR is held across a counter-prompt — under `merge-disposition: with-done` a PR waits for its d-work's
Done-`Y` — and carries an append to `agent-corpus/audits/INCIDENTS.md`, the one file every seat's PR
appends to at the same place. A peer's PR lands first inside the hold window; the hosting refuses the
merge (`405 … merge conflicts`); the rebase that resolves it changes the head the `Y` was given on, so
under Rule-2's Binding the question is asked again — and may conflict again before the second `Y` is
executed (row 194, twice in one afternoon). The fault is structural: the probability is a function of
the hold's length and the number of live seats, not of the PR's content, and every seat is told by the
preference's own note to avoid it and does not.

**What would have to change.** An incident row must never ride a held PR: either the protocol becomes a
check — a PR whose diff touches `INCIDENTS.md` beside any other path is warned at `dyad check --pr` and
listed on the board while held — or the log becomes a per-row store with no shared tail,
`<instance>/audits/incidents/<n>.md`, the shape `rows/` already takes for exactly this reason (Rule-16:
concurrent sessions touch disjoint files and almost never merge).

Boundaries against the neighbours it is most easily confused with:
- **M, no legal order, no verb (the gate-after-Done cluster)** — M's deadlock *followed* four of these
  six rows (173, 174, 175, 183): the Done record made the row terminal and the plan gate refused the
  recovery. That cluster is fenced since #202 (2026-10-15). Separating test: remove the gate-after-Done
  fence's absence and ask what remains — row 194, after #202, shows X alone: two re-asked questions, a
  rebase, no deadlock. The 2026-10-10 derivation filed row 123 (#242, the same peer-append cause) under M
  because the deadlock was its cost; on a full re-derivation 123, 149 and 171 would be read against X.
- **T, a stale or partial view of shared state** — T's change (refresh the view at the moment of the
  act) does not stop X: row 183 re-read mergeability in the reply that asked and was conflicted 28 s
  before the record was written. The view was fresh; the hold was the exposure.
- **L, a plan ordering no disposition sequence can authorize** — L's fault is in a plan's text before
  any act; X's PR was legally ordered and would have merged in an empty system.
- **U, the World moved** — the hosting's refusal is correct behaviour on a real conflict; nothing
  outside The Dyad System changed. The peer that landed first is a seat of this system.

## Incidents (6)
| row | date | d-work | what |
|-----|------|--------|------|
| 150 | 2026-10-14 | #259, #290 | PR #371 `CLEAN` at 09:52 and `CONFLICTING` two hours later after PR #373 appended; its parent gate made the hold unbounded |
| 173 | 2026-10-15 | #310 | the Done-`Y` on PR #396's head refused by the hosting on conflict; then the gate-after-Done deadlock |
| 174 | 2026-10-15 | #322 | the recovery PR for 173 conflicted in the minute between the mergeability read and the merge call |
| 175 | 2026-10-15 | #297 | PR #385 unmergeable before its Done question was asked (five conflicting rows on `main` 31–57 min earlier); the deadlock entered knowingly |
| 183 | 2026-10-15 | #321 | PR #402 conflicted by PR #396's rows 28 s before the Done record; executed as a local `--no-ff` merge of the unchanged head |
| 194 | 2026-10-21 | #338 | the `Y` on 94804cd voided by a conflict, re-recorded on 24fc1b3, conflicted again; the Operator cut the rows into their own narrow PR |

## Pattern
Six rows in eight days, five seats, both hosts; four on one day (2026-10-15) with five seats live. The
protocol — cut a tail-append file narrow and land it first — was written into `merge-disposition`'s own
note and into `dyad/playbooks/disposition-digest.md` on 2026-10-14 (#290, from row 150 and PR #355), and
rows 173, 174, 175, 183 and 194 breached it afterwards, each saying so in its own cause cell. The
breach is not ignorance: it is that the protocol asks the writer to open a second PR for one row, and
Rule-3's Incidents clause says the row rides "the d-work's own PR, or the next agent-zone PR", which
every writer reads as the PR already open. The two prose rules point opposite ways and nothing reads
either.

## Mitigations (phase 2)
Read from the code and the Rule text on 2026-10-24 at `97e9cf7`.
1. **The hold protocol — shipped as prose, inference only.** `preferences-corpus/PREFERENCES.md`
   (`merge-disposition`, the `with-done` paragraph) and `dyad/playbooks/disposition-digest.md` item 1.
   Moment: the plan, if the writer reads it. Reaches all six rows in the sense that each breached it;
   none mechanically. Recurred after it shipped: five of six.
2. **#202's fence — shipped, reaches the consequence.** `rows.landing_problems` and
   `done_order_problems` (`dyad/guards/agent/rows.py:116-174`) and the `cmd_dwork state` refusals
   (`package.py:1095-1125`). Moment: the CLI call and every push. Reaches the deadlock that followed 173,
   174, 175, 183 — and not the conflict that started them. Recurred after it shipped: the conflict yes
   (194), the deadlock no.
3. **The mergeability re-read before the question — conduct, shipped as a memory note.** Row 183 did
   it and was conflicted anyway: a read before a question cannot see what lands after it.
4. **`check --pr`'s containment range mode** (`dyad/guards/infra/containment.py`) — shipped, reads zones,
   not file contention; a PR touching `INCIDENTS.md` beside ten other agent-zone paths is one zone and
   passes. No guard reads which paths a PR shares with other open PRs; the hosting's mergeability is a
   library read (Rule-14 property 3) and can only ever be reported.
5. **Rule-16's per-file store pattern** (`crafts/sysarch/rules/stores.md`) — shipped for rows, plans,
   provenance, sessions and traces; not for incidents, which stay one table in one file. The pattern is
   the mode's own fix already built four times for other entities.

## Remediation candidate, under attack
**Candidate.** The incident log becomes a per-row store: `<instance>/audits/incidents/<n>.md` (or the
rows carried as `key: value` files like `rows/`), `INCIDENTS.md` rendered from them on demand as
`LEDGER.md` is, `incidents.py` reading the store, the row number allocated `max(origin, local)+1` as ids
are. Then no two PRs touch one file to add a row, and a held PR carrying a row conflicts only on a true
id collision, which the fence already makes loud.

| attack | result |
|---|---|
| The protocol already exists; a store is package code for a conduct problem | **refuted.** Five breaches in seven days after the protocol was written is the measurement that prose does not hold here; and the id-allocation pattern is the system's own answer to the same contention for rows (Rule-16), which has had one collision since. |
| A per-row store moves the contention to id allocation, which T already shows colliding | **survives, scoped.** It does; but an id collision fails loud at the push (`check_id_collisions`) and costs a renumber, where a tail conflict costs a voided `Y` and a re-asked question. Loud and cheap against silent and dear. |
| Rendering `INCIDENTS.md` on demand breaks every reader that greps `^\| 20` — this exercise, the survey step, the disclosure projector | **confirmed; scoped by the alternative.** A rendered-but-tracked table would carry the same tail. The cheaper half of the candidate is the check, not the store: a `check --pr` warning when a PR touching `INCIDENTS.md` touches anything else, and a board line for held PRs that touch it. That reaches the six rows as a warning at the cut, and costs no reader. |
| The right fix is #202's — it already made the conflict survivable | **refuted.** Row 194 is after #202: survivable cost two Done questions, two evidence runs and a rebase, and the Operator's own intervention to cut the PR. The fence changed the price, not the mechanism. |

Survivor: **the check first** (a `check --pr` warning and a board line), the store if the warning is
breached as the prose was. Phase 3 is the child row's own plan-`Y`.

## Proposed exit (phase 4)
**Exit 2 — a `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes and the
audit seat opens nothing. The row would say: *`dyad check --pr` warns when the PR's diff touches
`agent-corpus/audits/INCIDENTS.md` beside any other path, and the d-work board lists every held PR that
touches it with its age; if breached, the per-row incident store.* It would have met all six rows at the
cut (as a warning) and reports the hold the Operator has twice intervened in by hand. Not exit 1: no
mechanism reaches the mode today. Not exit 3: a hosting's merge refusal is The World's, but the
contention is the dyad's own and is decidable from the diff.
