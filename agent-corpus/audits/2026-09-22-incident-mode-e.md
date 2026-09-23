# Incident mode E — plan content wrong

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #121, child of #116 (2026-09-22).*

## Definition
The plan file was well-formed, written before its counter-prompt, and authorized by a plan-`Y` —
and what it authorized did not hold. A path, a zone grouping, a precedent or a sequence was
asserted from memory or analogy rather than derived from the mechanism that owns it
(`containment.py zones`; Rule-11 property 1's craft roots; Rule-11 property 7's `VERSION` →
`BUNDLE.md` coupling; Rule-3's completion-on-the-PRs-as-they-stand). The fault is in the decision
document, present at the moment the `Y` was given, and discovered at execution.

Boundaries against the modes it is most easily confused with:
- **A (acting before the Operator's `Y`)** — A's ordering is wrong and its content is fine; in E
  the ordering is correct (row, plan file, counter-prompt, `Y`, execute) and the content is wrong.
  d-work #22 owns rows in both, and they are different faults.
- **D (wrong cause asserted)** — D is a backward claim about something observed, retracted later
  with evidence. E is a forward claim about where a file goes or how PRs sequence, refuted by
  execution itself.
- **F (form error in a clerical record)** — F is a record written in the wrong shape or order after
  the decision. E is the decision document. d-work #17 owns one row in each: the record's *path*
  (E) and the record left unstaged (F).
- **G (mechanism defect)** — in G a hook, guard or CLI did not do what its design says. In all
  three E incidents every mechanism behaved correctly; none was asked the question.

## Incidents (3)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-15 | #17 | The plan named the falsification record at `agent-corpus/falsification/rules/batch-disposition.md`; a core-craft Rule's record lives under `dyad/falsification/rules/` and its name must match the `syseng/naming` pattern. The same plan's Mutation item 1 grouped `preferences-corpus/PREFERENCES.md` with `dyad/templates/PREFERENCES.md` as one PR. Written instead at `dyad/falsification/rules/rules-2-3-batch-disposition.md`; the item split into PR #6 and PR #7. | Two content faults in one authorized plan: a path that contradicts Rule-11 property 1 (a Rule's record travels with the core craft; vocabulary, *falsification record*), and a grouping that contradicts Rule-1 (one zone per PR). Both were derivable before the `Y` and were not derived. |
| 2026-09-16 | #22 | The plan named a `crafts/sysarch/VERSION` patch bump. Executing it would have required a matching `BUNDLE.md` row (infra zone) in the same d-work and broken `infra/bundle`. Reverted before commit; both PRs stayed one-zone. | The plan asserted a precedent that does not hold: a craft's `VERSION` is bumped by its own release d-work (#13/#21), not by each feature change. `BUNDLE.md` is nowhere in plan #22's `Files touched`; the second zone arrives through Rule-11 property 7's coupling, which the plan never consulted. |
| 2026-09-16 | #32 | The plan sequenced PR 2 (`crafts/sysarch/rules/stores.md`) to open only after PR 1 had landed on `main`. Under `merge-disposition: with-done` the Done-`Y` is asked on the PRs as they stand, so PR 2 could not exist for the Operator to review; item 7 was undeliverable and was named as such in the completion evidence. | A sequence fault, not a path fault: Rule-1's "change the referent before the referrer" was applied without checking it against Rule-3's completion clause and the live `merge-disposition` value. The plan was internally coherent and impossible to execute as written. |

## Pattern
All three plans skipped the same step: deriving a location, a grouping or a sequence from the
mechanism that already defines it, when that mechanism was one lookup away
(`containment.classify`, Rule-11 properties 1 and 7, Rule-3's completion clause plus the
preference table). What varies is which mechanism went unconsulted and how late the fault surfaced:
#17 and #22 were caught during execution — #22 reverted before commit, #17 corrected so that
neither of its PRs reached `main` mis-shaped; #32 surfaced only at the completion reply, where
item 7 was named rather than dropped and spun out as row #45, `done` the same day (PR #32). None
of the three cost a merge, a revert on `main` or an Operator correction — the cost was rework
inside the d-work and, in #32's case, a second row. The mode's most recent occurrence is
2026-09-16, six days before this audit. Nothing shipped since would have caught any of them: the
mechanism that checks plan files, `dyad/guards/agent/plans.py`, fails only on the header (a
`# Plan #<id>` line whose id matches the file name; a base-commit line) and merely warns when a
`dyadlib.PLAN_PARTS` section is missing, stating "Existence of these parts, nothing more: what a
plan says stays inference"; the only other reader of a plan file, `agent/references`, resolves its
id and its base commit and nothing else; and Rule-15's Enforcement is "Inference otherwise". The
mode is unremedied, and currently unobserved.

## Remediation candidate (falsified, not disposed)
Candidate, as plan #121 sketches it: extend the plan guard (`agent/plans`) to read every plan
file's `Files touched` line and fail when one Mutation item spans two zones or names a path under
no zone.

*Result* is the attack's: **confirmed** = the attack lands against the candidate.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | Two of the three incidents contain no zone fault. #17(a)'s wrong path and its correct one are both agent zone (`containment.py zones`: `agent-corpus/*`, `dyad/*`); the fault is the craft root, not the zone. #32's fault is a sequence and names no path at all. | confirmed | The zone check reaches #17(b) and half of #22 — one and a half incidents of three. |
| 2 | #22's second zone is a path the plan never listed. `BUNDLE.md` is absent from `Files touched`; it is implied by Rule-11 property 7 and enforced by `infra/bundle`. A reader of `Files touched` sees `crafts/sysarch/VERSION` as one more craft-zone path, with no infra path beside it, and has nothing to fail on. | confirmed | Only a check that models the `VERSION` → `BUNDLE.md` implication reaches #22; that is `bundle.py`'s data, not a zone lookup. |
| 3 | "One zone per plan" is not a Rule. Rule-1 binds a commit and a PR. Plans #22 and #32 each legitimately span two zones with two branches and two PRs, and each says so. A guard failing a multi-zone `Files touched` would FAIL correct plans. | confirmed | Any such check must be per-PR-group; per-plan it is wrong by construction. |
| 4 | There is no per-PR grouping in a plan file to read. `Files touched` is a flat `;`-separated list carrying brace expansion (`agent-corpus/d-work/{rows,plans,provenance}/22.md`); which Mutation item owns which path is prose. The sketch's own scoping — "one zone per listed group" — names a syntax no plan on `main` has. | confirmed | The candidate presupposes a Rule-15 plan-file form change. That is a different d-work from a guard, and it is the load-bearing half. |
| 5 | The guard already declines this by a recorded decision: `plans.py` checks existence only, citing plan #151 mutation 6, and Rule-15 Enforcement is inference. Making a plan's content mechanical reverses that decision without revisiting it. | survives-scoped | A derivation that reports and does not judge would stay inside the existing scope: it would print each `Files touched` path's zone and root and leave the verdict with the Agent. |
| 6 | A push-time check fires after the plan-`Y`. `agent/plans` runs in `package.py check`; all three plans were authorized before any push, and each fault surfaced at execution. A FAIL at push cannot stop a wrong plan being authorized — it can only report one already ratified. | confirmed | The derivation would belong before the counter-prompt (Rule-15 phase 1), a step the Agent runs rather than a gate a push runs. |
| 7 | Rule-13 property 1's trigger is recurrence. Three occurrences, all on 2026-09-15 and 2026-09-16, none since. Code proposed on a trigger last seen six days ago may answer a fault the corpus no longer shows. | survives-scoped | The recurrence is real and bounded; Rule-13 property 1 leaves the decline with the Operator ("The Operator may decline it"), so surfacing this without code stays inside the Rule. |

**The candidate does not survive as stated.** Attacks 1–4 leave it covering one grouping fault of
three incidents, and only after a plan-file form change it does not itself propose; attack 6 places
it at the wrong moment. What survives is not a guard but the shape of a derivation step that
would run while the plan is written and before the counter-prompt — for each `Files touched` path,
its zone (`containment.classify`, already imported by the craft guard `dyad/guards/craft/crafts.py`)
and whether a `falsification/rules/…` path sits under a craft root — its result stated in the
plan's falsification section, the judgment left where Rule-15 leaves it. That scoped survivor
covers #17 whole and #22's named path. It does not reach #22's unnamed `BUNDLE.md` coupling or
#32's sequencing, because neither is a fact about a listed path; those two are surfaced here
without a candidate.

*Noted against the plan:* plan #121's falsification line says each of the three plans "named a path
or zone without deriving it from `containment.py` zones or Rule-11's roots". The log does not
support that for #32, whose recorded cause is the `with-done` completion sequence and names no path
or zone. Mode E's own definition (parent #116: "path, zone, precedent or sequence") does hold for
all three.

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #121 (Rule-2: "a falsification
record or audit is disposed by the Done-`Y` of its d-work"). Remediation itself is a further
Operator prompt on this row, never taken here.
