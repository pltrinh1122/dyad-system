# Falsification record — "dyad-system upgraded to 0.7.0" (d-work #69)

**Claim (Operator prompt, 2026-09-18):** dyad-system upgraded to 0.7.0.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "0.7.0 names the current state." | **Confirmed false** | `BUNDLE.md`'s `version:` on `main` right now is **0.7.1**. `v0.7.0` (2026-09-17 17:10:06) and `v0.7.1` (2026-09-17 17:41:55) both exist as tags; `git merge-base --is-ancestor v0.7.0 v0.7.1` confirms `v0.7.1` is a strict descendant, 31 minutes later. Survivor: the system upgraded *through* 0.7.0 to 0.7.1; naming 0.7.0 as the destination is one release behind. |
| 2 | "The 31-minute gap is incidental — 0.7.0 itself was sound, 0.7.1 just a quick patch." | **Refuted** | `dyad/VERSION` and `crafts/sysarch/VERSION` were static at `0.6.0`/`0.1.4` while `dyad/` and `crafts/sysarch/` kept changing underneath (verified: `git diff --stat dyad-operator-v0.6.0..v0.7.0 -- dyad/` is 9 files changed against an unmoved `VERSION`). `v0.7.0`'s own `BUNDLE.md` rows (`dyad-operator: 0.6.0`, `sysarch: 0.1.4`) understated what was actually in the tree at the moment that tag was cut. `v0.7.1` (d-work #67) is the correction of a versioning defect in `v0.7.0` itself, found and fixed inside the same working session that cut it — not a routine patch on sound ground. |
| 3 | "The defect attack 2 names is still live." | **Refuted, checked live** | `git diff --stat <tag>..main -- <tree>` is empty for all three released crafts against their current tags: `dyad-operator-v0.6.1` vs `dyad/`, `sysarch-v0.1.5` vs `crafts/sysarch/`, `sysadmin-v0.1.0` vs `crafts/sysadmin/` — no drift right now. What survives is process, not content: plan #67 deferred "a mechanical guard against this recurring" as its own future d-work; no such row is visible in this corpus (searched). Whether it was named in that session's own chat reply (outside the corpus, Rule-7's stated boundary) cannot be verified here — stated, not asserted as a breach. |
| 4 | "Backlog row #61 (a third-party install's finding that `sysarch-v0.1.4`'s archive predates the #50 merge) is moot now that #67 bumped past it." | **Refuted as moot; survives as root-caused but not closed** | #67's fix stops the recurrence; it cannot and does not touch `sysarch-v0.1.4` itself — tags never move (Rule-11 property 4, its own provenance line). Anyone who already pinned `sysarch-v0.1.4` keeps the stale archive #61 found, permanently, by design. #61 is still `backlog`, unreferenced by #67 or #68, describing the exact defect class #67 just fixed for the next occurrence. Detected, not disposed: not this record's row to reclassify. |
| 5 | "The release-tag ratification itself (Rule-11: `Y/N: release <tag>?`, an event distinct from a d-work's Done-`Y`) is on record for these five tags." | **Cannot be confirmed from the corpus** | `provenance/58.md` and `provenance/67.md` each hold exactly two disposition entries, matching their rows' `disposed` columns (plan + done) — no third, distinctly-worded release disposition for `sysadmin-v0.1.0`/`v0.7.0` (#58) or `dyad-operator-v0.6.1`/`sysarch-v0.1.5`/`v0.7.1` (#67) appears anywhere. Not the same finding as #68 (already `planned`; its three occurrences are *PR merges* executed before their Done-`Y`, never mentioning release-tag ratification). Whether the release question was asked and answered outside the provenance record (a Rule-7 completeness gap; Rule-7 property 5 checks only that the disposition *count* matches, and both already do, at 2 — so no mechanical check would catch this either way) or skipped entirely (a Rule-2/Rule-11 breach) is left for the Operator to confirm against the Operator's own copy of the chat (Rule-7 Enforcement). |
| 6 | Overlap (Rule-16). | Checked, none found | `web-sysarch-adh151`'s presence file lists files under `crafts/syseng/`, `dyad/guards/agent/{rows,sessions}.py`, `dyad/scripts/package.py` — none touched here. |

**Survivor:** "upgraded to 0.7.0" survives only as "upgraded *through* 0.7.0, which needed an
immediate version-accounting correction, to the actual current release, 0.7.1." No live drift
exists right now (attack 3). #61 (backlog) and attack 5 (a new finding, opened as its own backlog
row citing #58, #67, #68) are both real and both left for the Operator, not fixed by inference here.

**Strongest counter:** none of this changes what's actually deployed or usable — 0.7.0 and 0.7.1
differ only in three `VERSION` numbers and a `BUNDLE.md` table, not in behavior, so treating "0.7.0"
as close enough might be a fair reading in casual conversation.
**Reconciliation:** the Operator's own word was "falsify," which is exactly the case for treating
the two as distinct: the difference between them is *itself* the record of a real defect (attack 2)
this session had to catch and fix within the hour, and the record would be worth less if it rounded
that away.

Cut from: nothing — new record (plan `agent-corpus/d-work/plans/69.md`).

Disposition: see ledger #69.
