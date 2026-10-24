# Incident mode C — a value stated from memory or a digest instead of read from its source

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10, 13 of 140 rows.*

## Definition
The mechanism: at the moment a value was used — in a reply, a plan, a row title, a change-log
cell, a file name, an API argument — it was produced from the Agent's own earlier reading, from a
digest or summary line, or from a remembered figure, and not from the store that owns it. The
source was readable at that moment, by a command the Agent already knew, and was not read. The
value is then correct about a past state of the world or about nothing at all, and the reader
cannot tell which, because the record carries the figure and not its provenance.

**What would have to change.** Every value a reply or a record states must be re-derived from its
owning store at the moment of use, so that no figure survives the interval between its reading and
its use.

Boundaries against the neighbours it is most easily confused with:
- **D, the wrong object read** — C and D are each other's nearest neighbours, and the test that
  separates them is whether anything was read at the moment of use. In C nothing was: the value
  came out of memory or a digest. In D a read was made and the thing read was not the thing in
  question. Boundary pair: row 92 (C) is a sha typed from the short form seen earlier in push
  output; row 125 (D) is a real `.pyc` file name, present in the tree and read right then, used in
  place of the host's `python3 -V`.
- **R, a derived key that does not identify** — R is the code's own version of the same family. In
  C and D a party composes or mis-resolves a value by hand, once; in R a module composes a key, a
  pattern or an id on every run and resolves it to the wrong object or to nothing, with no one
  reading anything at that moment. Boundary pair: row 92 (C, the Agent typed the sha) and row 139
  (R, `rows.py` keys the rule it applies on the checked-out branch name rather than on the range it
  was handed).
- **S, a form typed from memory, not seeded from its governing definition** — S's unread source is
  a *definition* (a header, a template, a section set) that the craft ships; C's is an
  *observation* about current state. Test: would reading a template have fixed it (S), or only
  running a command against the live tree (C)?
- **T, a stale or partial view of shared state** — in T the read was made and was correct when
  made, and the state then moved under a concurrent party; the fix is to fetch or refresh. In C no
  read was made at the moment of use at all. Boundary row: row 63 carries both — the figure came
  from the Agent's own earlier reading and `main` had moved under it across a rebase — and C is
  primary because the authoritative file sat in the working tree unread, with T secondary.

## Incidents (13)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #6 | the stated cause of 108 wrongly-755 paths was wrong, and a residual hazard plus a guard were proposed on it | the cause was asserted from an earlier reading of how a new path records here, never re-derived; `_mode()` and the #194 seed were the whole path, found only by workstation#212's observation with evidence |
| 2026-09-16 | #26, #34 | twice in one hour `<id>.md` files were written before `dwork new` printed the id; a peer's #27 plan and provenance were overwritten on `origin/main` | the id was taken from the last row seen rather than read from the allocator, which fetches first |
| 2026-09-16 | #27 | the provenance record for #27 was first written as `26.md`, and 26 had just been taken by a peer session's row | `dyad dwork new` and the `cat >` were issued as one command, so the name was fixed before the allocator's answer could be read |
| 2026-09-23 | #114 | 11 broken tests across 7 root causes were reported and delegated; an eighth surfaced only once the seven were applied | the failure list was read from a summary line instead of being re-derived after each fix, the earlier errors having masked it |
| 2026-09-24 | #156 | the Agent wrote #156's provenance into `provenance/154.md`, a peer session's existing record, overwriting it in the working tree | a hard-coded id was used before the allocator's output was read; peers had taken 154 and 155 since the last fetch |
| 2026-09-24 | #81 | the Agent's own delegation prompt asserted that d-work #82 "has since repaired" the failure, and the drafter encoded it as fact in nine load-bearing places | #82 was `planned` with PR #134 open; "planned, and authorized" was escalated to the present perfect when the context was written, never re-read from the tree |
| 2026-09-25 | #166 | the first commit of the disposed two-zone departure downgraded `dyad/VERSION` from 0.10.0 to 0.9.1 | the bump was written from a reading of that file taken hours earlier and was never re-read after rebasing onto current `main` |
| 2026-09-29 | #192 | the Operator was told that #186's three sub-agents were "still running"; all three had ended 64 minutes earlier, having delivered no report | the delegated state was reported from memory of having launched them, and nothing reads agent liveness before the per-turn report |
| 2026-10-05 | #223 | the first merge of ledger-only PR #314 was refused with 409 Head branch was modified, the `expectedHeadSha` having been typed from memory | the guard value was composed from the short sha seen in push output instead of from `git rev-parse HEAD`, and the tool accepts any 40-hex string |
| 2026-10-07 | #229 | the Agent reported in two replies that `trace.py` placed a Done-question reply 25 hours late, and opened row #240 on it; the 25 h was the plan question's wait | the preview's two timestamps were read as one misplaced reply and never checked against the commit times in git before being reported |
| 2026-10-08 | #242 | the plan revision of #242 attributed the 405 draft-merge failure to PR #334; it was PR #325 | the findings table was written from the audit digest and from memory of the session rather than re-read from the tool output that held the number |
| 2026-10-09 | #256 | the change-log row merged by PR #362 describes its undo as restoring five seeded comment lines; `.git/info/exclude` holds six | a count written from memory, in the same cell as a sha256 that was exact and against which the restore was actually verified |
| 2026-10-09 | #259 | row #259's immutable title states that 95 rows lie beyond the last grouping and calls the owed rows fifteen; the figures are 85 and sixteen | the live count was derived after the title was written, from a half-remembered figure sitting between an earlier audit's 58 and the true 85 |

## Pattern
What the thirteen share is an interval. In every one the authoritative source was one command away
at the moment of use — `dyad dwork new`'s printed id, `git rev-parse HEAD`, `cat dyad/VERSION`,
`python3 dyad/scripts/incidents.py`, a re-run of the suite, a live listing of the delegated agents,
the tool output already in the transcript — and in every one the value came instead from something
the Agent had itself produced earlier: a short sha, a summary line, a last-row-seen, an audit
digest, a prose recollection. Two sub-shapes carry the weight. Four rows (3, 28, 29, 92) are an
*identifier* composed before its allocator or its store answered; the other nine (4, 8, 27, 63, 71,
113, 114, 130, 131) are a *fact or figure* restated in prose. The second sub-shape is the one that
reaches the Operator: rows 4, 71, 113, 114, 130 and 131 each put a false statement in front of the
Operator or into an immutable record, and two of them (113, 131) landed in a row title that Rule-16
makes uneditable, so the only correction available is another row.

Recurrence against the mitigations a consequence cell describes:
- Row 28's consequence names the conduct adopted — "never write `<id>.md` before the id is printed"
  — and row 3 (ledger #156) repeats the fault 130 ledger ids later, on a different file of the same
  store.
- Row 71's consequence names the conduct adopted — "Every delegated-state report since is taken
  from a live listing, not from memory" — and no later row of this mode is a delegated-state
  report, so that one holds on the log's own evidence.
- Row 113's consequence names the correction appended to `plans/240.md` in #242, and row 114 (#242
  itself) is the next row of this mode, logged there as "a small sibling of the row above". The
  correction did not interrupt the mechanism inside the very d-work that made it.
- Row 63's consequence names reading `BUNDLE.md` as what caught the downgrade; rows 92, 113, 114,
  130 and 131 all post-date it by ledger id.

Note on dating: this repo's commit dates do not track its ledger dates
(`dyad/guards/infra/bundle.py` is a 2026-09-15 commit carrying d-work #21 and #196), so recurrence
above is ordered by the rows' own dates and ledger ids, not by `git log`.

## Mitigations (phase 2)

**1. The id allocator.** `dyad/scripts/package.py:948-954` (`cmd_dwork`, verb `new`): `git fetch -q
origin main`, `remote = {r.id for r in dyadlib.read_rows(REPO, at="origin/main")}`, `rid =
max(set(rows) | remote, default=0) + 1`, then `print(f"{rid}")` at `:964`. Fires when the Agent runs
`dyad dwork new`. **Shipped** (`dyad/scripts/package.py:948`, `:954`, `:964`). Reaches rows 3, 28 and
29 only by making the guess unnecessary: all three ran the allocator and then named a file from a
remembered id, row 29 in the same shell command as the allocator itself. It cannot stop a guess, and
the mode recurred after it in row 3 (#156).

**2. The fresh-record refusal.** `dyad/scripts/package.py:878-886`, `append_provenance(...,
fresh=True)`: "refused: {path} already exists for the new id #{rid}; it holds words no row owns —
resolve it first". Fires inside `dyad dwork new`, before the first write, as `write_row(...,
first=lambda: append_provenance(rid, entries, today, fresh=True))` at `:961`. **Shipped.** Reaches
row 3's exact fault — writing #156's provenance over an existing `154.md` — but only on the CLI
path; rows 3, 28 and 29 all wrote the file by hand, which this never sees. Reaches no other row of
the mode.

**3. The id-collision check.** `dyad/guards/agent/rows.py:212-238`, `check_id_collisions`: on a
branch, a row file the range adds or modifies must not name an id that already exists at `base`
under a different title (d-work #32 F2). Fires at `dyad check --guards --pre-push`
(`dyad/hooks/pre-push:4`) and at `dyad check --pr`. **Shipped.** Reaches rows 28 and 29 as detection
at push, never prevention, and only for the *row* file — the plan and provenance files those rows
actually overwrote are outside it. Its own docstring says so (`rows.py:215-216`): "Silent otherwise:
this is not the append-only fence".

**4. The provenance transaction check.** `dyad/guards/agent/provenance.py:287-299`,
`check_transaction` over `dyadlib.range_commits`, each non-merge commit against its parent and each
merge against both: a record only grows, its earlier entries word for word, and is never deleted
(Rule-7 property 3, Enforcement). Fires at `dyad check --guards --pre-push`. **Shipped.** Reaches
row 3's and row 28's overwrites: a commit that rewrote a peer's record would fail that push. It
post-dates both by ledger id (Rule-7's #191 amendment against #26/#27/#34 and #156), so no
occurrence has tested it, and it reaches none of the mode's eleven other rows.

**5. The bundle version comparison.** `dyad/guards/infra/bundle.py:143-149`: a bundle row whose
version differs from the craft's live `VERSION` fails at `:149`, unless the live version is ahead
and untagged, which warns at `:146-147`. Fires in Rule-11's runner (`package.py check`, guard
`infra/bundle`) and at pre-push. **Shipped.** Reaches row 63 exactly: a live `dyad/VERSION` of 0.9.1
against a bundle row of 0.10.0 makes `behind` false at `:145`, so the hard FAIL at `:149` would have
met the downgrade at the next push. The row's own account is that it was caught by hand first; this
is the standing net underneath it, and the only mechanical mitigation in this inventory that reaches
a row of this mode at its own moment.

**6. The drift check.** `dyad/guards/infra/bundle.py:84-100`, `check_drift`: a craft tree differing
from its own tag while `VERSION` is unchanged fails at `:99`; an unresolvable tag is one
`warning: skip` line at `:93`. Fires at the same moments. **Shipped**, and it reaches none of this
mode's rows. It is named here because row 63's *blocker report* rested on drift firing and the row's
cause is that drift stopped firing while the question was outstanding — the mechanism whose state
moved, not a mitigation of the mode.

**7. The evidence block.** `dyad/scripts/package.py:693-708`, `cmd_evidence`: `head=`, `tree=` and
`dirty=` read from `git rev-parse` and `git status --porcelain` at that moment (`:698-700`), every
check and guard line, and `evidence-sha256=` over them (`:707`). Fires when the main Agent runs
`dyad check --evidence` on the exact head being merged (Rule-14 property 3; Rule-2 Binding).
**Shipped.** Reaches row 92 in form — the sha this block prints is read, never typed — and did not
reach it in fact, because the value row 92 mis-typed went to a GitHub API argument, a surface
Rule-14 property 2 keeps outside the kernel. Reaches none of rows 4, 8, 27, 71, 113, 114, 130, 131.

**8. The suite, re-run rather than re-read.** `dyad/scripts/package.py:216-236` (`check_rule_12`)
and `:419-445` (`cmd_tests`), Rule-12 property 2: the suite is run by the runner, and one target at
a time through `dyad check --tests <target>`. Fires in the runner, at `dyad check --tests`, and at
pre-push. **Shipped.** Reaches row 8 as the right instrument and not as a fence: on failure the
runner prints exactly `r.stderr.strip().splitlines()[-1]` (`:233`) or `err.strip().splitlines()[-1]`
(`:442`), so a re-run hands back one summary line — the artifact row 8 was read from. The same two
lines are mode E's load-bearing finding.

**9. The live incident count.** `dyad/scripts/incidents.py:116-118`, `summary`: `f"{len(rows)}
incidents, {len(by_year_month(rows))} month(s)"`, parsed from the log at call time. Fires as the
guard's summary line in `package.py check` and from `python3 dyad/scripts/incidents.py`. **Shipped.**
Reaches row 131's figure — it was one command away — and fires at no moment a row title is written.
Nothing reads a row title against a figure, and `rows.py`'s immutable-title rule means nothing could
correct one afterwards.

**10. The preferences `delegation: plan-and-execute` and `concise-mode: on`**
(`preferences-corpus/PREFERENCES.md`), read by Rule-3 Scope and Rule-10 Form. Fires: inference,
stated, at reply time. Reaches rows 4 and 71 adversely rather than as mitigation — both are faults
*inside* the delegation path, one a false premise handed to a drafter, one a delegated-state report
from memory. For row 71 there is no mechanism at all: `grep -rn "ListAgents|liveness|live agent"
dyad/ crafts/` returns nothing, read today.

**11. Rule-3's completion-evidence clause** — "each check's result as observed, never assumed"
(`dyad/rules/RULE-3-d-work.md`, Completion counter-prompt) — and the frame's memory-cache convention
("On divergence the corpus wins", `dyad/CLAUDE.md`, Repo conventions; `cache.source->path` is listed
with resolver `world` at `dyad/guards/agent/references.py:431`, one warn line). Fires: **inference,
stated.** This is the only mitigation that reaches rows 4, 8, 27, 71, 113, 114, 130 and 131 — eight
of thirteen — and for those eight rows **the mode's only mitigation is inference, stated.**

## Remediation candidate, under attack
One fence: extend the fresh-record refusal from the provenance record alone to a **plan-file
identity check at push**, as a new case inside `dyad/guards/agent/rows.py`'s transaction path beside
`check_id_collisions` (`:212-238`): for every `<instance>/d-work/plans/<id>.md` the pushed range
modifies, the file at `head` must carry a `# Plan #<id>` title whose id equals its file name and
equals the id the file carried at `base`. Fires at `dyad check --guards --pre-push` and at `dyad
check --pr <base> <head>` — the same moment and the same parser (`dyad/guards/agent/plans.py`
`_TITLE`, `:25`) the plan guard already uses for its own shape check.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Not a fence on the fault. Rows 3, 28 and 29 wrote the file by hand with `cat >`, and a push-time check fires long after the overwrite; row 28's overwrite reached `origin/main` for about a minute, which is exactly the window a push-time check cannot close. | confirmed | Prevention does not survive; detection at the one moment the corpus is published does. The candidate converts a silent overwrite of a peer's plan into a refused push, which is what `provenance.check_transaction` already does for the record beside it. |
| 2 | Redundant: the provenance transaction check already fails a commit that rewrites a peer's record, and rows 3, 28 and 29 all touched a record. | refuted | Reading `provenance.py:291-298` and `plans.py:5-6` together: the transaction check walks `rows_rel` and `rec_rel` only, and the plan guard checks "Existence of these parts, nothing more". A plan file has no append-only or identity fence anywhere in the tree. Rows 28 and 29 overwrote a peer's *plan* as well as its record, and nothing would have failed on the plan half. Rule-9 easy agreement: this is the attack pushed to a verdict before the candidate was accepted. |
| 3 | A plan is legitimately rewritten — #221 reached revision 3 and #185 revision 4 — so any "only grows" rule is false of plans and would refuse honest work. | confirmed | "Append-only" does not survive. What survives is identity only: the title id must equal the file name and must not change between `base` and `head`. That is the collision signature and nothing else, and it leaves every revision free. |
| 4 | Coverage: 3 of 13 rows, and none of the nine prose-figure rows. A candidate that leaves the sub-shape which reaches the Operator untouched is not a remedy for the mode. | confirmed | Survives only as a partial, named as such. The figure sub-shape stays inference: Rule-5's Enforcement already states the shape of that limit, and a guard reading a row title against a derived count would have to know which count a title meant. |
| 5 | A new case in `rows.py` is package code and carries Rule-12 property 1's cost — a mechanical check run in CI, a test under `dyad/tests/guards/agent/`, and the syseng test-mapping guard. | survives, scoped | Admissible on Rule-13 property 1 (the second occurrence of an inference task yields a code path), and scoped to reusing `plans._TITLE` rather than a second parser — `crafts/sysarch/rules/guards.md`'s contract makes the entity's parser the thing other guards import. |

Read together: as a remedy for mode C the candidate does not survive — attack 4 holds without
reconciliation. What survives is a plan-file identity check at push, closing the one gap attack 2
found by reading the code, for 3 of 13 rows.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build** (exit 2), proposed only. What the row would say: a
plan-file identity case beside `rows.check_id_collisions`, firing at `dyad check --guards
--pre-push` and `--pr`, refusing a pushed range in which a modified
`<instance>/d-work/plans/<id>.md` carries a `# Plan #<id>` title that does not equal its file name
or that changed since `base`. Which rows it would have caught: 28 and 29 (the peer plan overwritten
on `origin/main`), and 3 on the plan half of the same store collision — 3 of 13. The remaining ten,
rows 4, 8, 27, 63, 71, 92, 113, 114, 130 and 131, hold none of the three exits: row 63 alone has a
shipped mechanical mitigation that reaches it (`bundle.py:149`), and the other nine have inference,
stated, and nothing else. The mode therefore stays **open** in the index whatever this record
proposes, and the Agent neither closes it nor asserts it addressed (play-book Conduct, Rule-2).

## Delta 2026-10-24 (#259 revision 5; 13 → 20 rows)
**Rows added:** 158 (#252: `fields-are-five` read as a scope from its name), 161 (#241: the `requires:`
floor's two readers conflated from a name), 186 (#326: a count repeated from the previous reply into an
immutable title), 193 (#356: an id read from memory, overwriting another seat's plan file), 195 (#369: a
tag written from `VERSION` without reading `git tag`), 199 (#378: the gate's suite run reported in words
as the evidence), 200 (#378: a hosting behaviour assumed, never verified). Seven rows in twelve days —
the ledger's largest mode, and the one whose delta is the most even across seats (five seats, two
hosts).
**Mitigations re-read from the code.** No mitigation of this mode shipped since 2026-10-10: the
2026-10-10 inventory's eleven items stand as read (`bundle.py` version comparison the only one at a
fault's own moment; `cmd_evidence` the block that is read, never typed). Row 199 is the one the
evidence block was built against and it recurred in the relay shape — the block existed and words
travelled instead; row 193 is the one the id allocator's own print exists against (`dwork new` prints
the id) and the print was not read. Candidate from the 2026-10-10 record (the plan-file identity case
beside `check_id_collisions`) would have reached 193's second half (the overwritten `plans/339.md`).
**Recurrence after a mitigation shipped:** every row post-dates every shipped item; none of the seven
is in any item's reach.
**Exit after the delta:** open, as before; #264 `backlog`, nothing built. Measured: 7 rows in 12 days
against 13 in 28.
