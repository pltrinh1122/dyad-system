# Audit — 2026-10-14, the d-work workflow and the incident records

**Audited:** branch head `84d84d2` (plan delegated at `066b2b4`, before the renumbering) · `origin/main` `1ed8d25` ·
python 3.13.16 (`dyad/bin/dyad-python --version`) · git 2.43.0

Disposition: see ledger #291 (Rule-2: the Done-`Y` of d-work #291 disposes this record).

*d-work #291 (first opened as #289 on this session's branch; renumbered after a peer session's #289 and #290
reached `main` at `1ed8d25` first). A topic audit, play-book `dyad/playbooks/audit.md` Conduct borrowed and nothing
else: a subagent ran every read; the main Agent commits. Every count below is a command's output; every claim about
code carries its file:line. Scripts live in the session scratchpad and are not tracked. `rows/README.md` is skipped
in every census. Where a guard already judges a property, its observed line is cited and the property is not
recomputed (Rule-13; Rule-20 trigger 2). It detects and sizes; it opens nothing.*

## 1. Store census (`agent-corpus/d-work/`)

Rows 279 · plan files 187 · provenance records 259 · traces 44 · `agent-corpus/provenance_legacy.local.txt` 24 ids.

| state | rows | notes |
|-------|------|-------|
| done | 189 | 9 of them (#204–#212) traced although Rule-3's trace clause starts at #213 |
| backlog | 75 | opened 1–30 days ago, median 21; 44 of 75 are 14 days or older; 9 carry a plan file (#51–#55, #98, #240, #244, #257) |
| open | 9 | #99, #189, #216, #221, #239, #249, #258, #289, #290 — none carries a `Y plan`; #216, #221, #249 carry an `N plan` |
| planned | 6 | #81, #238, #252, #253, #259, #291 |
| blocked / archived | 0 | the `archived` state (Rule-3, #37) has never been used |

- Non-terminal rows: 90. Lacking a plan file: **72** (66 `backlog`, 6 `open`: #99, #189, #239, #258, #289, #290).
- Lacking a provenance record: **20**, all `backlog`, every one listed in the legacy file; four listed ids (#162–#165)
  now have a record, so 4 of the 24 legacy lines are spent.
- Empty `disposed`: **20** — 14 `backlog` (all legacy) and the 6 `open` rows above. #99 (opened 2026-09-19, 25 days)
  and #189 (2026-09-29, 15 days) are `open` with no disposition and no plan; Rule-3 Scope says a prompt opened each,
  and nothing since has touched them.
- `done` rows ≥ #213 with no trace: **#213, #214, #215** (the three that landed the trace mechanism). Traces carrying
  a `- preview:` line: **#222, #231, #232** — recorded by plan #259 revision 4 C4; counted, not re-reported.
- On `origin/main` `1ed8d25`, `rows/289.md` and `rows/290.md` are the peer session's rows (the WHAT/WHY/HOW of
  #259 that PR #371 belongs to; the cos attention-scaling prompt), both `open`, empty `disposed`, no plan file —
  two of the 6 open-without-plan rows above. This session's #289 became #291 (`rows/291.md`, `planned`).
- #286 (`backlog`, 2026-10-13): the compaction-summary defect its title records cites `trace.py:215-225`, `:303`
  and `:344`; today `_derive` is at `dyad/scripts/trace.py:202`, `anchor` at `:297`, `intervals` at `:326`, and no
  `isCompactSummary` test exists in the file (`grep -i compact` returns nothing). The row's lines are stale by
  13–18 lines after one day; the mechanism is unchanged.

## 2. Already fenced — cited, not redone

| property | guard | observed line |
|----------|-------|---------------|
| `disposed` ↔ provenance disposition counts (Rule-7 property 5) | `dyad/guards/agent/provenance.py:95` `check_record` | `ok   [rule-7] 259 records, 698 entries` |
| row shape, immutable id/title, transitions | `dyad/guards/agent/rows.py:53` `check_package` | 0 messages, `279 rows` |
| plan parts (Rule-15 phase 1) | `dyad/guards/agent/plans.py:45` `check_plan` | `ok   [rule-15] 187 plans`; 5 warnings: `151.md` (falsification), `240.md` ×2, `244.md` ×2 (mutation, falsification) |
| trace file shape | `dyad/guards/agent/traces.py:33` → `dyad/scripts/trace.py:393` `check_store` | `ok   [rule-3] 44 traces` |
| incident table shape | `dyad/scripts/incidents.py:88` `check_log` | `ok   [incidents] 147 incidents, 2 month(s)`, 0 messages |

Nothing below re-derives any of these five; what follows is what no guard computes.

## 3. Done-before-merge orderings (git timestamps, `origin/main`)

Method: for each `done` row ≥ #46, the oldest commit on `origin/main` whose `rows/<id>.md` contains `Y done` (the
Done record) against the `%ct` of the merge commit whose subject names each PR the row's `disposed` lists.

- 158 `done` rows ≥ #46 name 324 PRs. **195** PR merges follow their Done record; **124** precede it (the #68/#315
  shape, Rule-3 Completion: "a merge before the `Y` is self-ratification … and an incident whatever the outcome").
- Those 124 fall on **26 rows**: #47, #48, #50, #57, #58, #67, #68, #69, #71, #90, #91, #93, #94, #95, #101
  (2026-09-16 to 2026-09-19), #116–#125 and #223. The batch #116–#125 is one Done commit (`5c007eb`, 2026-09-22) after
  ten merges (PR #111–#120) that each of the ten rows names, so it contributes 100 of the 124 pairs and one event.
  Leads run from 3 s (#68, #93, #101) to 527 s (#67). The latest is #223: PR #315 merged `a40cd8c` 2026-10-05 20:39:46Z,
  Done record `30b0283` 20:39:52Z, 6 s. No row done after #223 shows the shape (inference from the script's
  output, which lists none).
- 5 named PRs have no merge commit on `origin/main`. By the REST API: #42 (row #56) and #60 (row #80) were
  squash-merged (`merged_at` set); **#349 (row #243) and #352 (row #242) are closed and never merged; #355 (row #245)
  is still open** — three `done` rows whose `disposed` reads `Y done merges PR #n` for a PR that did not land.
  `ef4bc9b` ("#242 incident 7, PR #352 conflicted after the Done-Y") records one of them; #245 is "re-land #243's
  banking", so #349 was replaced by #355, which is open. Whether #242's content landed elsewhere is not traced here.

## 4. Rule-15 phase 2 drift on `planned` rows

Method: each plan's base commit against `git log <base>..origin/main -- <file>` for every file on its
`files touched:` line.

| row | plan-`Y` | base | files touched | moved on `main` since base |
|-----|----------|------|---------------|-----------------------------|
| #81 | 2026-09-18 (26 days) | `b000af1` | 2 | 0 |
| #238 | 2026-10-07 | `83ec302` | 1 — its own `plans/238.md` | 1 commit, `152d97b`, the commit that created the plan |
| #252 | 2026-10-09 | `7e780b4` | 1 — the ADR audit file | 0 (plan #285 F-b read `rows/252.md`, `provenance/252.md`, `plans/252.md`, which the plan's own line does not name) |
| #253 | 2026-10-09 | `44cf0ed` | heading form `files touched (this d-work):` naming its own plan and row | 2 commits on `plans/253.md`, both clerical |
| #259 | 2026-10-13 (revision 4) | `c9489ac` | 8 | 0 |
| #291 | 2026-10-14 | `1ed8d25` | 5 | 0 |

The only files that have moved are a plan's own ledger files, moved by the clerical commits that recorded its
authorization — the F-b shape plan #285 named: a literal reading of phase 2 makes a plan's own `Y` look like drift.
#253's line is in the heading form `sessions.files_touched` does not read (2026-10-10 index, finding 2), so the
presence store carries no files for it. `open` rows carrying a `Y plan`: none.

## 5. Trace defects

All 44 traces have a Limits section. Lines grouped by kind (one trace may carry several):

| limit (normalised) | traces |
|--------------------|--------|
| inference is a wall-clock gap … (`trace.py:564`) | 44 |
| the trace stops at the Done-`Y` … (`trace.py:565`) | 44 |
| shared turns counted whole … (`:521`) | 26 |
| provenance prompt entry ambiguous in the transcript (`:458`) | 16 |
| **the Done disposition is not anchored: the window ends at the d-work's last event** (`:455`) | 11 — #204, #219, #220, #237, #241, #251, #254, #260, #261, #285, #287 |
| turn(s) asking only about other d-works (`:523`) | 10 |
| `Y plan` disposition unmatched (`:458`) | 9 |
| `Y done` disposition unmatched, batch or single (`:458`) | 11 across 7 phrasings |
| agent-side segment ≥ the long gap (`:511`) | 6 |
| preview: no Done disposition yet (`:450`) | 3 — #222, #231, #232 |
| no provenance entry anchored at all (`:461`) | 1 — #256 |

- The "stops at the Done-`Y`" line is appended **unconditionally** (`dyad/scripts/trace.py:564-566`, after every
  branch), so the 11 traces whose window did not reach the Done-`Y` state both that it did and that it did not.
  **#287 does not lack the line: it is `traces/287.md:60`.** What #287 lacks is the window: entry 2 (`Y plan`) and
  entry 3 (`Y done`) are unmatched (`:56-57`), so `:453-455` ran — `end = min(max(anchored ts, commits ts ≥ start),
  last record)` — and the last commit then in HEAD was the plan ledger commit at 13:17:34 (`traces/287.md:12-13`),
  giving a 2m14s window for a d-work whose Done commit `365b20f` came at 13:46:22. That commit carries the trace, so
  by construction it can never be inside the window it stores. Why the two `Y`s did not match is inference: no
  transcript was read here; #286's compaction mechanism is one candidate, a disposition typed with text another.
- The 11 unanchored-Done traces and the 3 previews are 14 of 44 stored traces (32%) whose window is not the
  d-work's; `median_agent_side` reads all of them (plan #259 C3).

## 6. `INCIDENTS.md` as a record

- Live: **147** rows (`incidents.py` `parse`, `:69`). Watermark: `2026-10-10-incident-failure-modes.md:7` reads
  `covered through: 144 rows`; `-mode-r.md:3` and `-mode-q.md:3` still say `140`. Delta **3**: row 145 (2026-10-12,
  #285, keys itself to row 96), row 146 (2026-10-12, #261, keys itself to row 139), row 147 (2026-10-13, #287, says
  "the first"). Each is a candidate for the hardening play-book's phase 1; none is classified here (audit play-book
  phase 3b).
- Rows per d-work, top: #256 ×10, #259 ×7, #114 ×5, #221 ×5, #22/#116/#166/#223 ×4. 10 rows name more than one
  d-work. By date: 2026-09-16 ×17, 2026-10-09 ×16, 2026-09-29 ×13, 2026-10-05 ×13.
- Duplicates: token-Jaccard over `what`+`cause` ≥ 0.5 yields **one pair, rows 34 and 38** (0.51): both 2026-09-16,
  both #47, both "PR #35 merged before the Done-`Y` was asked" — one mechanism written twice. No other pair reaches
  0.5 (inference: a lower threshold was not swept).
- "Owed": `grep -c owed` = 20 lines, but `grep -cw owed` = **8** — the other 12 match `followed`. Of the 8, none is an
  incident row still owed: line 74 is the row it says was owed; 91, 110, 122, 129, 131, 136, 138 describe owed records
  of other kinds (a change-log row at 136, a capture at 131). Plan #285's one owed row (`plans/285.md:147-153`,
  the presence file touched twice) **is written: row 145**. Plan #259 revision 4 Part C (`plans/259.md:244-262`)
  names **C1–C5**, five rows, plus the watermark and the mode-r/q line edits, all in **PR #371 — open, unmerged**
  (REST `merged_at: null`): five incidents stated as owed and not yet in the log. Plan files containing the word
  `owed`: 32; only #285 and #259 were read for this audit, as the plan says.
- Phase 4 of the index (`:157`): 2 modes exit by an existing fence (F, W), 2 by a recorded impossibility (B, U),
  **15 by "a `backlog` row naming a fence to build"**, 4 reach no exit (I, K, M, T). The 23 children **#262–#284**
  are all `backlog`, all opened 2026-10-10, **none has a plan file**, none has moved. Fifteen fences are named and
  none is built, as the index itself says ("No new mechanical check was built", `:179`).
- Hardening survey not run through the runner (plan step 7): `dyad runbook run incident-hardening survey` writes
  `workstation-corpus/runbooks/events/incident-hardening.jsonl`, workstation zone, which this agent-zone PR cannot
  carry (Rule-1). The comparison above reproduces it by hand: live 147, covered 144. A departure from the play-book's
  step, stated as plan #259 Part B stated it.

## 7. Findings — proposed, not opened

Each is one row-shaped candidate in Rule-3's intake shape; the Operator disposes. Sized by count and age.

1. **Done-before-merge is historical, not live.** 26 of 158 `done` rows (124 PR pairs, 100 of them one batch) merged
   before their Done record; the last is #223 on 2026-10-05; none since. Evidence: section 3; `5c007eb`, `a40cd8c`
   vs `30b0283`. *Proposed, not opened: a check over `origin/main` that fails a Done record younger than a merge it names.*
2. **Three `done` rows name a PR that never merged** (#242→#352 closed, #243→#349 closed, #245→#355 open). Evidence:
   REST `merged_at`; `rows/242.md`, `243.md`, `245.md` `disposed`. *Proposed, not opened: a world-kind resolver line
   for `merges PR #n` (Rule-20) and a sentence in Rule-3 for a Done whose PR is later closed.*
3. **The trace writes a contradiction in 11 of 44 files**: "stops at the Done-`Y`" (`trace.py:565`, unconditional)
   beside "window ends at the d-work's last event" (`:455`). 4 days old at most (#287). *Proposed, not opened: make
   `:565` conditional on `done_ts`, beside #286.*
4. **#287's trace measures 2m14s of a 31-minute d-work** because both `Y`s were unmatched and `:453-454` ends the
   window at the last commit then in HEAD; the Done commit that stores a trace can never be in its own window.
   Evidence: `traces/287.md:12-13,18,55-60`; `365b20f`. *Proposed, not opened: when a Done entry exists but is unanchored,
   end at the trace's own run time and say so; keep #286 for the anchoring.*
5. **Five incident rows are owed and unwritten** (plan #259 C1–C5), waiting in PR #371, open since 2026-10-13; the
   watermark and two mode records lag with them. Evidence: `plans/259.md:244-262`; REST state of #371. *Nothing to
   open: #259 owns it; recorded so the next audit's delta reads it as pending, not new.*
6. **15 fences named, 0 built, 23 children with no plan after 4 days** (#262–#284, all `backlog`). Evidence: index
   `:157-179`; census. *Proposed, not opened: nothing — this is the Reconciliation of plan #291 made measurable; the
   next audit's watermark reads it.*
7. **72 of 90 non-terminal rows have no plan file; 44 of 75 `backlog` rows are 14+ days old; two `open` rows (#99,
   #189) have had no disposition for 25 and 15 days.** Evidence: section 1. *Proposed, not opened: an Operator sweep
   naming rows for `archived` (Rule-3) — the state has never been used.*
8. **Rule-15 phase 2 fires only on a plan's own ledger files** (#238, #253; plan #285 F-b on #252): the literal
   drift check has no real hit among 6 `planned` rows, and #81 has sat `planned` 26 days with nothing moved.
   Evidence: section 4. *Proposed, not opened: a sentence excluding `<instance>/d-work/` from phase 2's touched set.*
9. **Rows 34 and 38 are one incident written twice** (#47, PR #35, 2026-09-16). Evidence: section 6, Jaccard 0.51.
   *Proposed, not opened: a correction row, as row 141 corrected row 124; rows are never deleted.*
10. **`grep owed` over-counts by 2.5×** (20 lines, 8 word matches) — plan #291 step 6's own figure at the base was
    the substring count. Evidence: section 6. *Nothing to open; stated so the number is not quoted onward.*
11. **The index's two mode records and the watermark disagree with the log by 3–7 rows** (`:7` 144, mode-r/q `:3`
    140, live 147). Evidence: section 6. *Covered by PR #371; listed so it is not re-found.*
12. **#286's row cites three `trace.py` line numbers that moved within a day** (`:215-225`→`:202`, `:303`→`:297`,
    `:344`→`:326`). Evidence: section 1. *Proposed, not opened: cite functions, not lines, in row titles (Rule-16: titles
    are immutable).*

Not observed: whether any Done-`Y` in section 3 was actually given before the merge it followed in git (the chat is the
Operator's record; git has only commit times); the content of PR #371 beyond its title and state; any transcript;
plan files other than #285, #259, #291 and the six `planned` ones; the 23 children's titles beyond their mode line.

## Conduct

Detect, don't dispose. This record changes nothing: no Rule, guard, play-book, trace, row, provenance entry,
presence file or incident row was written or edited; every candidate above is proposed, not opened, and the
Operator disposes it or leaves it. The scripts that produced the counts live in the session scratchpad and are not
in the tree; every figure can be re-derived from `origin/main` `1ed8d25` and the branch head with the commands named.
