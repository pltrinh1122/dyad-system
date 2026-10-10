# Incident mode Q — an obligation no mechanism reads

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10; 12 of the 140 rows.*

## Definition
The mechanism is that an obligation is written into the corpus — a preference value, a Rule clause, a
ratified disposition — and no code anywhere resolves it, so the only thing standing between the
obligation and its breach is the Agent remembering it inside a turn. The obligation is loaded (the
preference table is read at session start, the Rule is in the frame) and then not applied; nothing
fires, nothing warns, and the breach is found by a later audit, by the Operator naming it, or by
listing two stores side by side. The population divides into three shapes: a preference whose
`read by` column names a Rule whose Enforcement is inference (rows 37, 68, 69, 78, 79, 119); a
ledger obligation whose store had no transaction-time reader (rows 7, 75); and an obligation whose
object lives in a hosted service the kernel never contains (rows 110, 132, 133, 134).

**What would have to change.** Every obligation the corpus states must name, in a place a guard
reads, the mechanism that reads it — or the literal fact that none does — so an unread obligation is
a countable line in a register rather than something discovered when it is breached.

Boundaries against the neighbours it is most easily confused with:
- **V, enforcement routed around** — V has a mechanism and the Agent goes past it (`--no-verify`); Q
  has no mechanism to go past. Test: name the check that would have fired. Boundary row: row 75
  (#191, 24 rows with no provenance record) — property 5's count *existed*, and compared only where a
  record existed, so for a row with none there was no reader at all; Q, not V. Row 133 is the hardest
  call in the mode and sits right on this line: `dyad-release.yml` exists and works, and five
  releases were published by hand ahead of it. I classify it Q because nothing read the obligation
  "a ratified tag is published by the one mechanism", not because the Agent evaded a check it met.
- **A, acting before the authorizing disposition** — A acts too early; Q, in several rows, does not
  act at all. Test: was an act performed without authorization, or was an owed act never performed?
  Boundary row: row 37 (#65) — five ledger-only PRs were *parked* for the Operator, the opposite of
  acting early, and the obligation breached was Rule-1's "states the rest and asks", which no
  mechanism reads.
- **B, a disposition recorded that the Operator never gave** — B's record is false; Q's record is
  true and unread. Boundary row: row 134 (#223) reads as B from `origin` alone, where PR #315 merged
  while the row held only `N plan` and `Y plan`; it is Q because the Done-`Y` existed, the local
  order was right, and what was unfenced is the 32-second window before the push.
- **H, the present enumeration pinned as an invariant** — H is a mechanism reading too rigidly; Q is
  the absence of one. Test: did a check fire wrongly, or not at all?

## Incidents (12)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-17 | #65 | five ledger-only PRs each opened and left for the Operator to merge, with no counter-prompt naming the collision and no standing disposition sought | Rule-1's #23 case says the Agent does the corpus-legal part, states the rest and asks; the "states and asks" half was never done and nothing reads it, so each parked PR silently put a merge on the Operator's desk |
| 2026-09-23 | #114 | the third plan-`Y` was lost before it reached `main`: its ledger commit was pushed to a branch, no PR was opened, and re-cutting the branch dropped it | the row's `disposed` chain went one entry short and provenance numbered 1,2,3,5, and nothing re-checked that a pushed ledger branch actually landed |
| 2026-09-24 | #158 | bundle release `v0.11.0` was ratified and its tag cut and pushed, but no GitHub Release was ever published for it; `gh release view` returns not found | a release is two acts, the tag and the published artifact, and only the tag has a mechanism; nothing reads a release disposition and nothing checks that a ratified tag was published |
| 2026-09-29 | #188 | the main chat was held open for about five minutes waiting on background sub-agents before replying to the Operator | a delegation was treated as a blocking call, the opposite of what the delegation preference buys; nothing in the harness or the Rules forces a wait, and nothing reads whether the turn was held |
| 2026-09-29 | #183 | the `on-ignore` batch engagement signal was missed and the Agent went on asking singly, reporting no pending-queue counts for four consecutive prompts | the signal is conversational and nothing mechanical raises it; Rule-3 itself says the queue is not a corpus file and nothing in it is mechanically checked |
| 2026-09-29 | #191 | 24 rows carried no provenance record at all, eighteen of them backlog rows with an empty `disposed` and six recording one disposition each | no check tied a row to its record at the moment either was written, and the cut-off that was supposed to bound the gap named an id of an earlier ledger |
| 2026-09-29 | #195 | `concise-mode: on` was not kept: 93 assistant text blocks across about ten prompts, mostly unprompted progress narration, with several prompts drawing more than one reply | the preference was loaded in the frame at session start and not applied, and no mechanism reads it; Rule-10's enforcement is inference only |
| 2026-09-29 | #195 | `delegation: plan-and-execute` was not kept: 303 tool calls and 3 read-only Agent calls, so every line of three d-works' code was drafted by the main Agent on the main thread | the same shape as the row above, loaded and not applied, with no mechanism reading it; delegating would have broken no Rule |
| 2026-10-05 | #223 | PR #315 merged while `origin/main`'s row held only `N plan` and `Y plan`; the Done-`Y` reached `origin` 32 seconds after the merge it ratified | Rule-3 requires the ledger's record of the `Y` to precede every merge it ratifies, and nothing bounds the window between the local commit and its push |
| 2026-10-06 | #226 | the Done-`Y` merge of PR #325 failed with `405 Pull Request is still a draft`; the session creates every PR as a draft and no ready-for-review step preceded the merge | nothing in Rule-3's completion clause or Rule-2 says a PR created as a draft must first leave draft, and the setting is a harness fence outside the corpus |
| 2026-10-08 | #241 | five releases published by hand with `gh release create`, each beating CI by about two minutes, and all five corresponding workflow runs failed with a duplicate-tag error | the workflow that publishes on a tag push exists and works, and nothing reads the obligation to use it; the hand path runs no tag-equals-VERSION check |
| 2026-10-09 | #254 | `delegation: plan-and-execute` was not applied to drafting plan #252, 783 lines over seven revisions, nor plan #253; the trace reports the subagent bucket at 0 seconds | the artifact the preference assigns to a subagent was drafted by the main Agent, and nothing checks it because the preference is read by inference and no guard sees a turn's size |

## Pattern
Twelve rows over 22 days, and in every one the obligation was already in the corpus, in writing,
before the breach. Six are preference-shaped (37, 68, 69, 78, 79, 119) and four of those six are the
same two preferences — `concise-mode` and `delegation` — breached on 2026-09-29 and again on
2026-10-09. Two are ledger-store obligations (7, 75). Four have their object in a hosted service
(110, 132, 133, 134). The mode's characteristic signature is in the cause cells: five of the twelve
say in as many words that *nothing reads it* — "no mechanism reads it" (78, 79), "nothing re-checks"
(7), "nothing mechanical raises it" (69), "nothing reads a release disposition" (132), "nothing
bounds the window" (134). The other seven say the same thing in other words.

Recurrence against each mitigation the consequence cells describe:

- **Row 37's mitigation, the preference `ledger-pr-merge` (#66, 2026-09-17).** The Operator disposed
  a standing disposition directly and it was captured as a preference row
  (`preferences-corpus/PREFERENCES.md:16`, value `agent`). No further parked-ledger-PR row is logged
  in 23 days. It is the mode's one mitigation that converted an unread obligation into a *value*, and
  it still has no mechanical reader — the only code that touches the key is a projector reading it as
  a Mandate (`crafts/countersign/projectors/project_countersign.py:52`), which reports and does not
  gate.
- **Row 7's mitigation, "caught by reading the restored row before committing the Done-`Y`"
  (2026-09-23).** Inference, in the turn. Row 75 (2026-09-29) is the same store's obligation,
  unrecorded at scale, six days later.
- **Row 75's mitigation, #191's own delivery: the provenance transaction check and `dwork` writing
  both files in one step (2026-09-29).** This is the mode's only shipped fence. No row of this
  shape post-dates it.
- **Rows 78 and 79's mitigation, stated conduct: "Conduct from #195 on is one synthesis per prompt"
  and "From #195 on, execution is drafted in worktree forks" (2026-09-29).** Row 119 (2026-10-09)
  post-dates it by ten days and is the `delegation` breach again, measured this time at 0 seconds of
  subagent time across a 22h41m window. A conduct statement measured at ten days. Row 78's cell also
  proposes a fence — "a stop hook counting assistant text blocks per turn" — and marks it as a
  harness setting and a host action, "proposed for the Operator to open as its own row, not built
  here"; I found no row for it.
- **Row 119's mitigation, the trace's `delegated share` line (2026-10-09, delivered by the same
  d-work).** Shipped (`dyad/scripts/trace.py:547-551`). Nothing of this mode post-dates it yet; one
  day is no measurement, and it is a report at Done rather than a gate.
- **Row 132's named fence, `backlog` row #20 (opened 2026-09-15, "CI publishes a GitHub Release
  automatically on a tag push").** Row 132 (2026-09-24) and row 133 (2026-10-08) both post-date the
  row by weeks. Worse for the row than that: reading the tree today, the fence it names **exists** —
  `.github/workflows/dyad-release.yml` triggers on `tags: ["v*", "*-v*"]` (`:2-4`), checks that the
  tag equals its `VERSION` (`:22-33`) and publishes with `gh release create` (`:47-49`). The row was
  reaffirmed on 2026-10-08 from #241 (`agent-corpus/d-work/rows/20.md`, `disposed` second entry)
  after row 133, which says the same thing from the other side: "the workflow … exists and works, and
  backlog #20 names it as if it did not". So the mitigation for this sub-shape is shipped and the
  breach is that a hand path beat it by two minutes, five times.

## Mitigations (phase 2)
Read from the code, the workflow and the Rule text today, 2026-10-10, in this worktree.

### 1. The provenance transaction check and the legacy list — shipped
- **What.** `provenance.check_commit` requires, per non-merge commit against its parent: a row the
  commit adds brings at least one new entry; a row born `backlog` brings a `disposition`; a
  `backlog` → `open` brings a `prompt`; k new `disposed` entries bring k new `disposition` entries;
  and a record only grows (`dyad/guards/agent/provenance.py:232-270`). `check_package` fails a row
  with no record unless the instance names it in `provenance_legacy.local.txt`
  (`:167-200`, `legacy` at `:142-165`; the instance's list is
  `agent-corpus/provenance_legacy.local.txt`, 30 lines today). Entry numbering with no gaps is
  checked at `:109-111`.
- **Moment.** `check_transaction` at every push on the kernel-only path
  (`dyad/hooks/pre-push:4` → transaction loop `dyad/scripts/package.py:628`,
  `TRANSACTION_MODE = "commits"`, `:39`); `check_package` in the guard pass of every push and every
  `check --evidence` (`dyad/scripts/package.py:601-615`, `:693`).
- **Reaches.** Row 75 completely — it is #191's own delivery, and the 24 rows are recorded in the
  list rather than repaired. Row 7's shape too: a record numbered 1,2,3,5 fails `:109-111` in every
  session, and a row whose `disposed` lost an entry fails property 5 at `:122-126`. Reaches none of
  the other ten.
- **Recurrence after it shipped.** No ledger-store row of this shape after 2026-09-29. Rows 110, 119,
  133 and 134 post-date it and are outside it.

### 2. The `delegated share` line in the d-work trace — shipped, a report not a gate
- **What.** `trace.py` prints `| delegated share | <pct>% (<n> s of <m> s agent-side, <k> output
  tokens) | transcript |` (`dyad/scripts/trace.py:547-551`), with the comment stating the reading:
  "0% on a token-heavy d-work is `delegation: plan-and-execute` not firing for work it covers". The
  trace store has a guard (`dyad/guards/agent/traces.py:33-34` → `trace.check_store`), registered as
  `agent/traces` and run in the guard pass since #227 (`dyad/guards/agent/traces.py:6-7`).
- **Moment.** At the completion reply, because `dwork-trace` is `always`
  (`preferences-corpus/PREFERENCES.md:20`) and Rule-3's completion clause requires the evidence to
  cite the trace (`dyad/rules/RULE-3-d-work.md:142-143`). The guard checks the *shape* of traces that
  exist, at every push; it does not check that a `done` row has one.
- **Reaches.** Rows 79 and 119 as measurement after the fact — row 119's own consequence cell says
  the count was added "so the next omission is visible at the next Done". Reaches row 78
  (`concise-mode`) not at all: no bucket counts assistant text blocks.
- **Recurrence after it shipped.** One day old; nothing to measure, and I say so rather than
  claiming a quiet period.

### 3. `.github/workflows/dyad-release.yml` — shipped, and beaten by hand
- **What.** Triggers on `tags: ["v*", "*-v*"]` and on `workflow_dispatch` with an existing tag
  (`.github/workflows/dyad-release.yml:2-8`); refuses a tag that does not equal its `VERSION` for the
  bundle, the core craft or a Tended craft (`:22-33`); publishes the archives with `gh release
  create` (`:47-49`).
- **Moment.** On a tag push, in hosted CI — a library adapter, never kernel (Rule-14 property 3).
- **Reaches.** Rows 132 and 133 as the mechanism that *should* have run: row 132's ratified tag
  `v0.11.0` would have been published by it, and row 133's five hand publications are the workflow
  losing a two-minute race it would otherwise have won. It reaches neither as a fence, because
  nothing refuses the hand path, and nothing can: `gh` is a World tool and Rule-14 property 2 keeps
  The World observed, never pinned (`dyad/rules/RULE-14-system-infrastructure.md:56`), with a hosted
  service never kernel (`:37`).
- **Recurrence after it shipped.** Rows 132 (2026-09-24) and 133 (2026-10-08) both post-date it; row
  133 is five occurrences in one d-work.

### 4. Nothing reads a ratified disposition other than `Y plan` — the mode's central verified fact
- **What I read.** A grep of `dyad/` and `crafts/` for `Y plan`, `Y done` and `Y release`, excluding
  tests, returns only `dyad/guards/agent/prs.py:4,46,47,71` — the plan gate's literal `"Y plan" not
  in row.disposed` (`:46`) — plus two regexes in `trace.py` that classify a disposition note into a
  timeline bucket (`dyad/scripts/trace.py:62-63,142`). Rule-20's register holds no tag or release
  kind at all: the 29 kinds at `dyad/guards/agent/references.py:408-437` resolve rows, rules, crafts,
  PRs (to `world`), commits, terms, files, components, events and traces, and nothing resolves a
  release.
- **Moment.** Not applicable: this is the absence.
- **Reaches.** Explains rows 132, 133 and 134 directly, and row 7 historically. A `Y release` or
  `Y done` entry is, to every mechanism in the tree, free text.
- **Recurrence.** Row 132's cause cell cites the 2026-10-08 audit
  (`agent-corpus/audits/2026-10-08-disposition-chain-of-authority.md`, finding L6-1) for the same
  conclusion; I reproduced it from the code rather than from that audit's prose, as phase 2 requires.

### 5. The preference text and the Rules' own Enforcement sections — shipped as text, inference only
- **What.** `concise-mode: on` and `delegation: plan-and-execute`
  (`preferences-corpus/PREFERENCES.md:13,17`) read by Rule-10, whose Enforcement is "Inference only,
  stated" (`dyad/rules/RULE-10-proposal-framing.md:30`); `batch-disposition-mode: on-ignore` (`:15`)
  with Rule-3 stating the pending queue "is conversational … not a corpus file, nothing here is
  mechanically checked" (`dyad/rules/RULE-3-d-work.md:169`); `ledger-pr-merge: agent` (`:16`);
  Rule-8's Boundaries placing the harness permission mode outside the corpus
  (`dyad/rules/RULE-8-host-mutation.md:15`), which is where row 110's draft-PR setting lives. The
  only preference keys any code reads are `host-path` and `host-zone`
  (`dyad/scripts/dyadlib.py:350-370`).
- **Moment.** Inference, stated.
- **Reaches.** Rows 37, 68, 69, 78, 79, 110, 119 — seven of twelve — and reaches them only as the
  text that was breached.
- **Recurrence after it shipped.** All seven post-date the preference or Rule they breach.

For seven of this mode's twelve rows, the only mitigation is inference, stated.

## Remediation candidate, under attack
**The candidate.** One new reference kind in Rule-20's existing register:
`preference.read_by->mechanism`. For each row of `preferences-corpus/PREFERENCES.md`, the resolver
takes the key and the `read by` column (already parsed at
`dyad/guards/agent/references.py:303`, and already resolved to a Rule by the kind
`preference.read_by->rule` at `:424`) and resolves it to a mechanism: a guard module and function, or
a CLI refusal, that mentions the key — or, where the named Rule's `## Enforcement` section says
"Inference only, stated", to the literal `inference`. It **fails** when a Rule's Enforcement names a
mechanism that does not read the key, and prints one `warn … inference` line per obligation whose
only reader is inference, which Rule-20 property 2 already prescribes for a `world` kind. It fires in
`references.check_package`, in the guard pass of every push
(`dyad/hooks/pre-push:4` → `dyad/scripts/package.py:601-615`) and inside every `check --evidence`
block (`:693`).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A register of unread obligations reads no obligation. Rows 68, 78, 79, 110, 119 and 134 would each have produced a `warn … inference` line and happened anyway — the Agent would have read the warning in the same guard output it already reads every push, and the mode is precisely the failure to act on what is written. | confirmed | "Addresses mode Q" does not survive. Survives only as: an unread obligation becomes a countable line in a register instead of a fact an audit discovers, which is the difference between 2026-09-29's four simultaneous rows and a running count. |
| 2 | Self-ratifying data: if the mechanism column is authored, the guard checks the Agent's own claim about its own code, which is the shape Rule-20's own property 1 avoids by making every resolver resolve against a live store. | confirmed | The authored form does not survive. Survivor: both sides derived — the population from the preference table and from each Rule's `## Enforcement` section, the resolution by searching the craft trees for the key string. Nothing hand-listed, exactly as the registry and `check --list` are discovered rather than listed. |
| 3 | Coverage: it is preference-shaped only. It reaches rows 37, 68, 69, 78, 79 and 119 (6 of 12). It misses rows 7 and 75, already fenced; and it misses 110, 132, 133 and 134, whose obligations are a harness setting and a hosted publication, neither of which is a preference row. | confirmed | Half the mode, and not the expensive half: row 132 is a ratified publication that never reached the world, row 133 is five of them. Those need a second kind, `row.disposed->release`, resolving a `Y release` entry to a published release — which Rule-20 property 2 makes `world`, hence warn-only. |
| 4 | Cost and overlap: `preference.read_by->rule` already exists (`dyad/guards/agent/references.py:424`), so this is a second kind over the same two columns, and Rule-20 property 1 is "one register, one resolver per kind" — two kinds reading one field invites the question which is authoritative. | survives, scoped | Admissible because the kinds have different targets: one resolves the Rule, the other the mechanism. Scoped to the existing register and the existing guard, no new module — which is also what keeps it from becoming a second registry the core maintains by hand. |
| 5 | Rule-9 easy agreement: I agreed with this candidate on first reading because Rule-20's precedent is strong — the register is exactly what turned reference-bridging from inference into a check. Pushed: Rule-20's kinds resolve *existence of a target instance*, which is decidable; "is this obligation read by a mechanism" is decidable only up to a string search, and "is the obligation kept" is not decidable at all. The precedent supports the form and not the claim. | refuted (the precedent argument) | The candidate may not be justified by analogy to Rule-20. It stands or falls on attack 1's narrower survivor: visibility, counted, at a named moment. |

## Proposed exit (phase 4)
**Exit 2 — a `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes.

The row would say: *Rule-20's register gains two kinds — `preference.read_by->mechanism`, failing
when a Rule's Enforcement names a mechanism that does not read its preference key and warning once
per obligation whose only reader is inference; and `row.disposed->release`, resolving a `Y release`
entry to a published release as a `world` kind under Rule-20 property 2. Both derived from the
preference table and the Rules' Enforcement sections, in the existing guard, run in the guard pass of
every push.* It would have surfaced, before the fact and as a countable line, rows 37, 68, 69, 78, 79
and 119 (the preference shape) and rows 132 and 133 (the release shape, as a warning). It would have
caught none of them in the sense of refusing anything.

The mode does not have one shape, and the Operator may prefer to split it into child rows rather than
take one exit; I state the split rather than choose it. Rows 7 and 75 are already at **exit 1**,
fenced at a named moment: the provenance transaction check, per commit, at every push
(`dyad/guards/agent/provenance.py:232-299`). Rows 110, 133 and 134 look like **exit 3** on this
kernel — a draft-PR setting is a harness fence outside the corpus
(`dyad/rules/RULE-8-host-mutation.md:15`), and a hand `gh release create` and the window before a
push both live in a hosted service that Rule-14 property 2 keeps observed and never pinned
(`dyad/rules/RULE-14-system-infrastructure.md:37,56`); no check the kernel can run reaches them. The
remaining six are what the candidate addresses, and only as visibility. Nothing here closes the mode,
and I assert nothing about it being addressed.
