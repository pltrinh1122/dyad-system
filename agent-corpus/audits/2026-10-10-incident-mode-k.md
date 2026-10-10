# Incident mode K — a plan incomplete against its own text

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10. 8 rows of 140.*

## Definition
The mechanism: the plan's binding list and the plan's own prose were written from different
drafts, or the list was written from the deliverables rather than from the plan's own contents, so
a consequence the plan states in one place is absent from the list execution binds to — the
`## Files touched` section, the "not in this mutation" list, or the PR split. A legal order
existed throughout; what failed is the plan's internal agreement with itself.

**What would have to change.** A plan's binding lists must be derived from the plan's own prose and
from the tree it names — each path's zone re-derived from `containment.py zones`, each mechanism's
call sites searched before the list is closed — instead of typed beside the prose from memory.

Boundaries against the neighbours it is most easily confused with:
- **M, no legal order, no verb** — M's tree admits no correct plan; K's admitted one and the plan
  did not carry it. Test: on the tree as it stood, could a complete plan have been written?
  Boundary pair, both version/zone shaped: row 23 is K (plan #22's `crafts/sysarch/VERSION` bump
  was optional, and not bumping is both legal and what happened), row 61 is M (the play-book had to
  live under `dyad/`, so both bump and no-bump failed the same guard).
- **L, a plan ordering no disposition sequence can authorize** — L's defect is the *sequence* of
  authorizations, K's the *completeness* of the text. Test: is the missing thing an item (a path, a
  file, a zone) or an order? Boundary pair: row 33 is L (plan #32's PR 2 was sequenced behind a
  merge that did not come), row 103 is K (a path owed by Rule-3 was omitted from the file list).
- **C, a value stated from memory instead of read from its source** — C quotes a wrong *value*; K
  omits an *item* from the plan's own list. Row 18's half (a) sits closest to the line: the
  falsification-record path was wrong because Rule-11's craft/instance root was never read. It is
  bound to K because the defect is the plan naming its own artefacts, not a figure quoted from
  elsewhere. Least-certain assignment in this mode.
- **S, a form typed from memory, not seeded from its governing definition** — S's artefact has the
  wrong *shape* because no template seeded it; K's plan is correctly shaped and its content
  incomplete.

## Incidents (8)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-15 | #17 | plan #17 named a core-craft Rule record under the instance path, and grouped a preferences file with an agent-zone file as one PR | the plan was written without checking Rule-11's craft/instance root for a Rule falsification record, or re-deriving each touched file's zone from `containment.py zones` |
| 2026-09-16 | #22 | plan #22 named a `crafts/sysarch/VERSION` patch bump that would have dragged `BUNDLE.md` into a two-zone plan | a craft's `VERSION` is bumped by its own release d-work, not by each feature change; the plan asserted the bump without checking that precedent |
| 2026-09-22 | #114 | the plan says the craft zone does not change, but the mechanism the same plan names can only be made by the craft | the mechanism paragraph was added immediately before the plan-`Y` and its consequence for the craft zone was never carried back into the "not in this mutation" list, which still read from the earlier draft |
| 2026-09-23 | #126 | merging #114 left `main` red: `check_drift` fails `dyad/` against its own tag over #114's six core-craft files | #114's plan named a craft `VERSION` bump and a `BUNDLE.md` row but never the core craft's own, though the same d-work changed six files under `dyad/`, and no falsification asked what the core's version should do |
| 2026-10-01 | #199 | node M's measurement on the BASE clone leaked 162 `/tmp/dyad-floor-*` directories, an outcome the plan did not name | measuring the base means running the defect being measured; the brief named the clone method but not its host residue, and the fix existed only in the AFTER clones |
| 2026-10-05 | #221 | plan revision 3's `## Files touched` omitted `INCIDENTS.md` while three incidents recorded above it owed rows | the file list was written from the deliverables rather than from the plan's own contents, so a Rule-3 obligation stated three paragraphs earlier was never carried into it |
| 2026-10-07 | #228 | the fix touched `dyad/scripts/package.py`, which the plan's `## Files touched` did not name | the plan located the mechanism in `craft.py` without noting that the core install's call site, which decides which rows are written, is `cmd_install` in `package.py`; the mutation needs both and one was listed |
| 2026-10-07 | #228 | the first push was refused by the pre-push gate: one core test pinned the very defect the fix removes | the plan named neither that test nor its file; it searched for the mechanism and for the check proving the new behaviour, and never searched the existing tests for ones asserting the old behaviour; third plan-vs-file-list miss in this one d-work |

## Pattern
Five of eight are a missing path or file in a binding list — the `## Files touched` section (rows
103, 107, 108) or the "not in this mutation" list (row 11) or the PR split (row 18, half b). Three
are an un-asked consequence whose list was complete for what the plan said: the core craft's own
`VERSION` (row 6), the host residue of a measurement (row 87), and a precedent the plan asserted
against (row 23). Two of the eight sit in one d-work, #228, whose own row text calls row 108 the
"third plan-vs-file-list miss in this d-work, counting `package.py`: the same failure mode each
time" — so the log itself records a third instance inside that d-work beyond the two rows carried.

Catch moments, from the rows: row 6 by `check_drift` run on `main` **after** the three merges (the
row says the drift only exists once the commits are there); row 108 by the pre-push gate before
anything left the machine; rows 11, 18, 23, 87 and 103 by the Agent re-reading before the
counter-prompt; row 107 stated in the completion evidence rather than caught. Six of eight were
therefore caught by inference, one by a gate and one only on `main`.

Recurrence evidence: no mitigation in this inventory has ever shipped *for this mode*, so no row
post-dates a fence built against it. What the dates do show is that the list-omission half runs the
whole length of the ledger — 2026-09-15 (row 18) to 2026-10-07 (rows 107, 108) — and that its
density rises rather than falls, three of the five list-omission rows falling in the last six days
of the population.

## Mitigations (phase 2)
1. **The plan-file guard's parts check.** `dyad/guards/agent/plans.py` `check_plan` at
   `dyad/guards/agent/plans.py:45-60`: a missing base-commit line is a FAIL
   (`dyad/guards/agent/plans.py:52-53`), and a plan never mentioning a part of
   `dyadlib.PLAN_PARTS` — the five parts including `files touched`
   (`dyad/scripts/dyadlib.py:455`) — is a **warning**
   (`dyad/guards/agent/plans.py:57-59`). Moment: every guard's `check_package` in Rule-11's runner
   (`package.py check`, registry label `agent/plans`) and at `dyad check --guards --pre-push`, via
   `dyad/scripts/package.py:606`. Reaches: a plan with no files-touched section at all. Reaches
   **none** of the eight rows — every one of the eight had the section and it was incomplete. The
   module states its own limit: "Existence of these parts, nothing more: what a plan says stays
   inference" (`dyad/guards/agent/plans.py:5`). **Shipped**, and by construction out of reach of
   this mode.
2. **The zone guard.** `dyad/guards/infra/containment.py` `ZONES`, run in `staged` mode by
   `dyad/hooks/pre-commit:4` (blocking at commit) and over the pushed range at `dyad check --guards
   --pre-push`. Reaches rows 18 (half b) and 23: a plan that grouped two zones is caught at the
   first commit that mixes them, which for row 18 is what split PR #6 from PR #7 and for row 23 is
   what the revert restored. Does not reach rows 6, 11, 87, 103, 107, 108 — in all six the omitted
   path is in the same zone as the listed ones, and row 107 says so explicitly ("Same zone (agent),
   so Rule-1 is unaffected"). **Shipped**.
3. **The drift guard.** `dyad/guards/infra/bundle.py` `check_drift` at
   `dyad/guards/infra/bundle.py:84-100`, reached through `check_package`
   (`dyad/guards/infra/bundle.py:169`); same moments as 1. Reaches row 6 and only row 6 — but, as
   the row records, only once the commits are on `main`, because a tree matching its own tag cannot
   drift before the merge. **Shipped**; row 6 is itself the measurement of it, and the measurement
   is that it detects after the ratification rather than before it.
4. **Rule-12's suite at the push gate.** `check_rule_12` at `dyad/scripts/package.py:216-236`,
   gated by `suite_gate` (`dyad/scripts/package.py:335`), fires at `dyad check --guards
   --pre-push` and in `check --evidence`. Reaches row 108, which was caught exactly there. Reaches
   no omission whose absence breaks no test — which is rows 11, 18, 23, 87, 103 and 107.
   **Shipped**.
5. **The presence store's plan reader.** `dyad/guards/agent/sessions.py` `files_touched` at
   `dyad/guards/agent/sessions.py:63-80`, read by `dyad session touch` and `dyad session list`.
   It *consumes* the plan's file list, so an incomplete list silently under-reports an overlap; it
   checks nothing and cannot reach any row of this mode. Two separate findings about it, both
   verified today: its docstring states that "the `## files touched` heading form some plans use
   … is not this pattern and is not read" (`dyad/guards/agent/sessions.py:70-72`), and every one of
   the seven plans behind this mode's rows (#17, #22, #114, #126, #199, #221, #228) uses the
   heading form. Running `files_touched` over all 184 stored plans today yields an empty list for
   **106** of them, including plans 17, 22, 221 and 228. So the one mechanism in the tree that reads
   a plan's file list reads nothing from well over half the plans. **Shipped** as a reader, never a
   check.
6. **Rule-3's Incidents clause and Rule-15 phase 2.** `dyad/rules/RULE-3-d-work.md` Incidents ("If
   the plan changes as a result, a fresh plan-`Y` precedes any further mutation") and
   `dyad/rules/RULE-15-d-work-phases.md` phase 2 (re-plan if `main` moved past a touched file).
   Moment: **inference, stated**. Reaches all eight rows after the fact, which is what every one of
   their consequence cells records; prevents none.

Not inference-only, but close: three mechanical mitigations are shipped (2, 3, 4) and together they
reach 4 of 8 rows, one of them only after the merge. The mode's own mechanism — a plan's list
disagreeing with the plan's prose — has no mechanical reader at all; mitigation 1 is the guard that
would be its home and explicitly declines the job.

## Remediation candidate, under attack
**One fence.** A coverage check in `dyad/guards/agent/plans.py`, added as `check_transaction`
(making the module `TRANSACTION = True`, `dyad/guards/agent/plans.py:20`): for each `open`,
`planned` or `blocked` row whose plan file carries a files-touched list, compare that list to the
paths the pushed range actually changes (`dyadlib.range_paths`, `dyad/scripts/dyadlib.py:285-299`)
and report every changed path the plan does not list. What it checks: that the plan the plan-`Y`
bound to still names what execution touched. Where it lives: the existing `agent/plans` guard.
When it fires: `dyad check --guards --pre-push`, where transaction guards run over `base..head`
(`dyad/scripts/package.py:625-628`), and `dyad check --pr <base> <head>`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The list is prose, not a parsed field. `sessions.py:70-72` already records two incompatible forms, and 106 of 184 stored plans yield nothing to the one parser that exists — so a coverage check would refuse correct work on the majority of plans, which is mode M manufactured on purpose. | confirmed | The check is admissible only paired with one parsed form and a writer that emits it (a `dyad dwork plan` scaffold, or a seeded `files touched:` line). Without that pairing the candidate does not survive at all. |
| 2 | It makes the plan a mechanical contract and so forbids a legitimate in-flight addition. Row 107's own disposition was that the mutation was the one the plan described; a FAIL there would have forced a fresh plan-`Y` for a same-zone file. | survives (scoped) | Only as a **warning** naming the unlisted paths, promoted to FAIL when an unlisted path's zone differs from every listed path's zone — the Rule-1 consequence, which is exactly what rows 18b and 23 cost. |
| 3 | Rule-9 easy agreement: a coverage check reads as obviously right. Measured against the rows, it would have reached at most 4 of 8 (11, 103, 107, 108), and in rows 11 and 103 the Agent had already caught it by re-reading before the counter-prompt, while row 108 was already caught by the pre-push suite. Its unique yield is row 107. | confirmed | One row in eight does not justify a new transaction guard on its own. It survives only as a cheap addition to a guard already loaded, at a moment the range is already being read, and must be costed that way rather than as a remedy. |
| 4 | It cannot reach the un-asked-consequence half. Rows 6, 23 and 87 had complete lists for what their plans said; what was missing was a question nobody asked — what should the core's own `VERSION` do, what does measuring the defect leave on the host, does the precedent allow this bump. | confirmed | The mode splits. A list-coverage half is fenceable at the push gate; a consequence half is the shape Rule-5's Enforcement describes, a judgement no script can decide, and is not fenced by this or any candidate here. |
| 5 | A plan is amended during execution (plan #221 reached revision 3, #256 revision 4). A gate reading the plan at push time reads a file the Agent may legitimately have just widened, so the check can always be satisfied by editing the plan rather than by noticing the omission. | survives (scoped) | Only because the plan edit is itself a ledger commit the fence and the provenance guard judge, so widening is on the record. The candidate's claim narrows to "an unlisted path is never silent", never "the plan was right". |

## Proposed exit (phase 4)
**Open.** No exit of the three holds. The three shipped mechanical mitigations (the zone guard, the
drift guard, the push-gate suite) are fences at named moments but none of them fences *this*
mechanism — each catches a downstream symptom of it, and one of them only after a merge. There is no
`backlog` row naming a fence for it. And it is not wholly unfenceable: the list-coverage half is
mechanically decidable once one parsed form exists.

Proposed to the Operator, not taken:
- A `backlog` row naming the two-part fence: one parsed files-touched form with a writer that seeds
  it, then the coverage check of the candidate above as a warning at `dyad check --guards
  --pre-push` promoted to FAIL on a zone mismatch. It would have caught row 107 outright, caught
  rows 11, 103 and 108 earlier than they were caught, and it would also repair the separate finding
  in mitigation 5 — that `agent/sessions` currently reads no file list from 106 of 184 plans, which
  is the overlap signal Rule-16's presence store was built for.
- The consequence half (rows 6, 23, 87) recorded as the Rule-5-Enforcement shape: no script decides
  which question a plan failed to ask. Stated here as a finding for the Operator's disposition, not
  asserted as this mode's closure.
