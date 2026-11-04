# Backlog by definition of done (draft, 2026-11-04)

*Drafted by the home for row #574, item 3 of its definition of done, as plan #570 revision 4 specifies it (V1–V3).
Read at `origin/main` 9a3de41. The definition-of-done step is applied as counsel wrote it on PR #646 at f35eb112, which
is not on `main` yet, so this report also tests the step (section 5). Every DoD below is the home's proposal, marked
*proposed*. Where your words are quoted, they come from a provenance record, and applying them to these rows is still
the proposal. Nothing is opened, retired or merged by this document. Its tracked home is
`agent-corpus/audits/2026-11-04-backlog-dod.md` (plan #570 named `2026-11-backlog-dod.md`; the audit naming guard
requires the day).*

**How to read it.** Section 3 holds the groups, section 4 every row. Amend only the DoDs you would define differently,
by group or row id. The number you amend is the measure of the proposals (plan #570, revision 4).

## 1. The definition of done this report answers

Row #574's definition of done, item 3 (plan #574):

> The first use is the home's backlog report on the 62 backlog rows (#570 revision 4, V1–V3): the counts of rows in, DoDs out, absorbed and split, and how many of the proposed DoDs you amended.

Your words behind it (provenance #570, entries 5 and 6):

> as you said, the granularity should be based on my ability to verify.  this means that as part of the playbook to drafting rows, you should elicit from me the definition of done and those definitions will inform the partitioning.

> as verification of the elicitation process, we can apply it to the existing backlog rows.

Your three examples, in the same entry:
- hardening: "i expect a report showing the number of resolved INCIDENTS"
- automaton: "i expect a report showing exactly where inferencing is required because i’m going to assume that everything else are handled by automaton"
- attention: "a pair of ‘Y’ that can produce the largest scope of work where i’m able to evaluate"

And on scale: "with cloud infrastructure set-up and configuration, i need more granular scoped rows."

On the rows a delivered row supersedes (provenance #574, entry 4): "i shouldn’t be disposing “archive” - i’m expecting ‘done-Y’"

**What this report does.**
- It proposes one DoD per piece of backlog work. Each is drawn from the row's title, refs, plan and provenance, and
  from the row whose record holds the prompt behind it. Most rows' own records hold only a `Y` (section 5).
- It partitions by those DoDs. Rows that one DoD covers merge into one row. A row whose parts you would judge apart
  splits. A row that an open row's DoD already covers is absorbed: it would ride that row's Done as `retires #r`
  (plan #574 revision 3, G1–G2; `backlog` and `done` rows only).
- It keeps the counts. The amendment count is added after your reply.

**49, not 62.** Plan #570 counted 62. Since then, 21 rows were archived on #571's report (#262–#283, except #267,
which was archived before), and the eight fence rows #576–#583 were opened. 62 − 21 + 8 = 49.

## 2. Counts

| measure | count | rows |
|---|---:|---|
| rows in (`backlog` at 9a3de41) | 49 | |
| merged into a new row (one DoD over several rows) | 28 | groups 1–6 |
| absorbed into an open row (rides its Done as `retires`) | 1 | #554 into #573's step 4 |
| split | 2 | #317 (one sentence to #585, one to #303); #319 (two new rows) |
| work already delivered (retire; ground: carried by #567, `done`) | 2 | #130, #311 |
| unchanged (own DoD, stays `backlog`) | 16 | |
| **DoDs out, on backlog work** | **24** | 6 groups + 2 from #319 + 16 unchanged |
| open rows whose DoD takes backlog work | 2 | #573's step 4 (#554), #585 (#317's sentence b) |
| rows that would leave the backlog | 33 | the 28 merged, #554, #317, #319, #130, #311 |
| new rows to open | 8 | groups 1–6, 319a, 319b |
| backlog afterwards, if all is accepted | 24 | 49 − 33 + 8 |
| DoDs you amended | — | after your reply |

Sum check: 28 merged + 1 absorbed + 2 split + 2 delivered + 16 unchanged = 49.

## 3. Proposed DoD groups

### 3.1 Absorbed into an open row

| open row | its DoD, as its plan states it | takes | ground |
|---|---|---|---|
| #573 public surface | *proposed* (plan #570 revision 4): "a report listing the surface 1.0 freezes and every alias removed, plus the one test that pins it." | #554, whole | plan #573, step 4: "#554 is carried by this step and closes with #573's done-`Y` (it is cited in this row's refs)." Your B3 answer moved step 4 after the 0.18.0 cut, and your done-`Y` on #573's 0.18.0 part (2026-11-04) did not name #554. So #554 rides step 4's own Done, the row that continues #573 under #570's mandate after the cut. |
| #585 Rule-3 refactor | *proposed* (plan #585): "A **clause map** you can read in one pass: every sentence of today's Rule-3 with its fate (kept, merged, moved to the Rule that owns its concern, or dropped), the reason, and the row or incident it came from. Beside it, the new Rule-3, with its length against today's." | #317, sentence (b) only | the new Rule-3 is organised around "what opens a row" (plan #585, Mutation). Sentence (b) says that a unit carrying your own prompt opens its row as a prompt does, noted `relayed via <unit>`. The new Rule-3 would hold it, and #585's completion evidence would name #317 as retired, with this ground. |

#571 is `done`, so it can absorb nothing. The eight fence rows its report proposed make up group 1.

Checked and not absorbed, because the open row's DoD as it stands does not cover the row:
- #54 and #572: #572's report says where inference is required, not which party a record names.
- #548, #549 and #587: #587 derives the board's fields from events. Cabinet keying and clock skew are not in its DoD.
- #579 (R-a) and #586: #586 fixes two sequencing errors. R-a is one refusing parser for every verb.
- #173 and #585: #585 keeps the never-carried list unchanged (its R5). Adding disclosure would widen it.
- #534 and #572: a quick-check would mechanize a judgment that #572 may list as inference. It is not in #572's DoD.
- #344 and #573: #573 keeps internal modules out of the frozen surface, so renaming `dyad/scripts/` does not touch the
  1.0 promise.

### 3.2 New rows: one DoD over several backlog rows

**Group 1. Hardening: the incidents still open.** #576, #577, #578, #579, #580, #581, #582, #583 (R-a…R-h). Tag
`v1.0.0`.
- Your DoD for hardening (provenance #570, entry 5): "i expect a report showing the number of resolved INCIDENTS"
- Applied here, *proposed*: #571's table of resolved incidents, read again on this row's PR heads. The 20 modes that
  R-a…R-h name move from "row (proposed)" to "fenced", each with its fence and the moment it fires. The count rises
  from 124 of 252. Any mode still open is named with its reason.
- Why one row: you judge the eight fences by one number. #571's index: "124 of 252 are resolved today. The other 128
  resolve as R-a…R-h are opened and built." #571 is `done`, so a new row carries the same DoD.
- Its Done would retire #576–#583.

**Group 2. Open audit findings on craft and play-book text.** #84, #85, #86, #87, #88, #89, #257, #318, #320.
- *Proposed*, in the shape of your hardening DoD: a report showing each of 12 open findings resolved. They are the
  sysadmin sweep's six (#84–#89), #255's four (#257: U2–U5) and #81's two citation residuals (#318, #320). Each shows
  its text or citation before and after, or the verb that now exists (#89), and the guard line that keeps it so where
  one is added. #84 and #85 are counted over every craft, since #84's title says "systemic: sysarch 18, syseng 18".
- Your words for the sweep (provenance #83, entry 1): "perform an audit sweep for completeness and coherence of the `sysadmin` craft and create a plan with corresponding backlog items for remediation - don't remediate."
- Why one row: every finding is judged the same way, by reading the before and the after.

**Group 3. The automaton as a party.** #54, #55.
- *Proposed*: a report of every Rule sentence and record field that names only the operator and the agent as parties,
  or presumes a CLI agent on every host: Rules 3, 8, 14 and 19, the run-book event's `role` and the change log's
  `actor`. Each gets its new text, naming the automaton where it acts. The tests on the PR head show an automaton run
  recorded under its own party. Today the scheduled sweep's events record `role: agent`.
- Your words (provenance #553, entry 1, the `automaton` row): "fills the #54 daemon gap". Plan #553, attack 4:
  "#54's gap is named, not built".

**Group 4. The cos as a mode: your G.** #537 (P3, the lease), #538 (P4, the mode), #539 (P5, follow).
- Your words (provenance #531, entry 3): "I want to eventually get to a G - where the `cos` follows me everywhere so it's not a stand-alone session but perhaps a "mode"."
- *Proposed*, from plan #531's roadmap tests, on a checkout of the row's PR heads: you open a session on any machine,
  say "cos", and are talking to the cos, with the board, the queue and every open question as they were. Handed from
  the cloud to the MacBook terminal and back, nothing is lost. A second live holder is warned, and an ordinary hop is
  not (the simulator's S8 and F5, which audit 2026-11-02 assigned to #537). A fresh session you write to takes the
  mode by itself; a paired secretary never does.
- Order: the MacBook leg needs 319a first.

**Group 5. Seat hops, every pair.** #313, #548, #549, #550.
- Your words (provenance #546, entry 1): "stress test the seat-hops through simulation - cover all scenarios across cabinets and hosts"
- *Proposed*: the seat-hop simulator's report on the row's PR head, filled pairwise over all six axes (#550). Every
  scenario passes except S8, which group 4 carries. In particular: a second cabinet's rows never appear in a home's
  resume (S13, #548); a `since` in the future shows as skew, never as a negative age (S15, #549); and
  `dyad session list` flags one holder behind two live units (#313).
- #313 comes from another audit (2026-10-15, G3). It joins because one holder behind two units is a hop case the
  simulator can cover, and you would read it in the same report.

**Group 6. Disclosure ready to hand over.** #172, #173.
- Your words (provenance #166, entry 1, its first sentence): "Create a plan for a `ds-report-incidences` playbook that groups existing INCIDENCES and redacts IP content."
- *Proposed*: a disclosure report generated from today's incident log, grouped by failure mode (the 51 modes of the
  2026-11-04 index) as well as by month, redacted, which you read and could hand over as it stands. Its delivery is
  declared by an Agent Rule as a question of its own, so no done-`Y` carries it.
- #172 waited for "incident mode records that carry their row ids". #571's 51 mode records now list their incident
  rows, so this group can start.

### 3.3 Split

**#319 into two new rows.** Its own title asks for "one row per platform when prompted".
- **319a, macOS**, *proposed*: on your MacBook, a host install of this repository. `dyad check --guards` exits 0 on the
  kernel alone. The entrypoint, both hooks and an ops script run. Each macOS item of the contract in
  `crafts/sysadmin/rules/host-platform.md` is marked observed.
- **319b, Windows**, *proposed*: the same on a Windows host, with the four shell files and the ops-script skeleton
  given a form that runs there.
- Your words (provenance #81, entry 1): "also in scope is to maintain and operate the host infrastructure abstraction - for example portability on top of MacOS and Windows." And (provenance #531, entry 1): "i'm managing work across multiple workstations (Linux and MacBook)."
- The split also follows your remark on cloud infrastructure (section 1). Reading host platforms as the same kind of
  domain is the home's reading.

**#317 into two existing rows.** Sentence (b), the relay inside one system, goes to #585 (section 3.1). Sentence (a),
the store as a sender's transport, joins #303's DoD, because plan #317, F1, says "Sentence (a) waits for #303".

### 3.4 Work already delivered

#130 and #311: #567 (`done`) delivered both. Plan #567, on #130 and #311: "this row delivers both rows' mutations." Their
ground for retirement is *carried* (`dyad/dmc/retirement-candidate.jsonld`). No open row's Done names them (section 6).

## 4. Every row

| id | title (shortened) | proposed DoD | disposition | ground |
|---|---|---|---|---|
| 4 | DYAD_CANONICAL: remote-agnostic base for cmd_guards, dwork new and the PR guard | *Proposed:* in a scratch clone whose main remote is not named `origin`, the push gate, `dwork new` and the PR guard read that remote's `main`, shown by their output. | unchanged | an intake from a peer system (2026-09-14); plan #301: "kept, LAN-git-era rows the Operator opens or retires" |
| 5 | package.py check refuses a sensitive registry row whose repo has a non-LAN remote | *Proposed:* a push is refused when the craft registry lists a craft marked sensitive and the remote is not one the instance lists as on its LAN, shown in a scratch repo; with no list, one skip line. | unchanged | as #4 |
| 54 | gap (d): no scheduled/daemon actor model across Rules 3/8/19 | → group 3 | merged into group 3 | provenance #553, entry 1: "fills the #54 daemon gap"; the sweep's events still record `role: agent` |
| 55 | gap (e): Rule-14 property 2 kernel wording presumes a CLI inferencing agent | → group 3 | merged into group 3 | plan #55: the kernel as worded has no member for a host with no CLI agent; the automaton's host is one |
| 60 | Rule-8 presumes every system has a host | *Proposed:* Rule-8 names where a system records the host actions it takes on a host it does not tend, with this instance's change log as the worked example. | unchanged | audit 2026-09-17-sysadmin-minimum.md, attack 3, elevated by #57 |
| 84 | sysadmin craft rules cite a foreign instance's d-work ids bare | → group 2 | merged into group 2 | the sweep of provenance #83, entry 1 ("for remediation") |
| 85 | craft rules cite agent-corpus/d-work/plans/{155,162,216}.md, instance paths absent here | → group 2 | merged into group 2 | same sweep; two of the three paths now resolve to unrelated plans here (155, 216) |
| 86 | sysadmin templates/events-README.md not declared in MANIFEST.md seeds: | → group 2 | merged into group 2 | same sweep; `seeds:` still lists only `CHANGELOG.md` |
| 87 | sysadmin docs/backup-timeshift.md owned by no craft rule, guard or term | → group 2 | merged into group 2 | same sweep; the doc is still unowned |
| 88 | sysadmin craft rules trip the Rule-4 guard's Agent-process warning, with no record of the judgment | → group 2 | merged into group 2 | same sweep |
| 89 | no scaffolder seeds an ops script from crafts/sysadmin/templates/ops-script.sh | → group 2 | merged into group 2 | same sweep; Rule-13 property 1 (recurrence proposes code) |
| 96 | wire ceiling markers into Rule-20 (P4 mechanism, ponytail adoption) | *Proposed:* a report listing every `# ceiling:` marker with the row it names and that row's state; a push adding a marker that names no row is refused, shown on a test marker, since the tree holds none today. | unchanged | provenance #94, entry 2: "You have everything you need to implement proposal for syseng to adopt some of the ponytail elements. falsify. implement survivor."; plan #94 deferred this wiring to its own row |
| 97 | ponytail benchmark harness for syseng (P7) | *Proposed:* a report of a first measured run: the task set, the scorer, and per task the lines of code and tokens with and without syseng's minimality rule, plus what the run cost. | unchanged | plan #94: "it needs a task set, a scorer, and a credentialed run (Rule-8, Rule-14)" |
| 102 | zone contribution mechanism design (deferred from #100 PR 2) | *Proposed:* a design you read in one pass: how a craft declares a zone of its own and what the containment guard then checks, with the craft that needs it. | unchanged | provenance #102, entry 1: "Y: drop zone contribution from PR 2" |
| 130 | --backlog (its refs: sessions.touch_from_open_rows lists every open or planned row) | none: the work is delivered | delivered: retire (carried by #567) | plan #567, on #130 and #311: "this row delivers both rows' mutations." |
| 139 | server instances have no side and no direction | *Proposed:* the vocabulary gives a server instance a side (inside the system or in The World) and, per instance it serves, a direction (afferent or efferent); each run-book this instance keeps states both. | unchanged | provenance #139, entry 1 (relayed): "these server instances exists as 'afferent' and 'efferent' between a `dyad-system` instance and the world." |
| 172 | disclosure surface groups by month only (#166) | → group 6 | merged into group 6 | provenance #166, entry 1; its trigger has come: #571's mode records list their rows |
| 173 | declare disclosure a ratification event (#166) | → group 6 | merged into group 6 | its title: the delivery question "is conduct until a Rule carries it" |
| 177 | withheld: the title names a client (section 6) | *Proposed:* a ui-design craft outside this repository's bundle, with its own guard, whose assets a surface here inlines unchanged. | unchanged | provenance #174, entry 2: "i believe designing ui should be a separate craft, but not necessarily a part of the core bundle." |
| 181 | a sysux craft for teaching the system, not running it | *Proposed:* a guide a new operator follows to run a first d-work from prompt to done-`Y`: the order the Rules are read in, and one worked example from this ledger. | unchanged | provenance #178, entry 3: "so the Operator's experience with the chat (CLI) interface with Agent is `sysux` (or `sysdialog`)."; plan #178, attack 20 |
| 244 | add an instance enumerator to every guard (the guard contract) | *Proposed:* the instances surface lists every instance of every entity kind straight from the guards, with no store seeded by hand, and its counts equal the stores' own. | unchanged | provenance #50, entry 1: "as the Operator, i want to be able to traverse the entity instances for audit purposes." |
| 248 | resolve a craft's requires: floor against the tags that exist | *Proposed:* `dyad craft check` shows the floor invariants of sysadmin, sysarch, syseng and disclosure run against the earliest tag that meets each floor, none skipped. | unchanged | its title: those invariants "have never run"; `floor_problems` still asks for the exact tag |
| 257 | fix-soon after #247: U2–U5 of #255 | → group 2 | merged into group 2 | plan #257: four defects, "each reproduced by a skeptic against `origin/main`"; all four still read as found |
| 303 | the bus craft: an announcement store over a neutral transport | *Proposed:* two dyad systems in separate repositories exchange an announcement through a shared store, a second git repository. One publishes, the other reads by a tune-in filter, and a disposition-shaped announcement is refused at publish. Rule-3 Intake names that store as a sender's transport (#317's sentence a). | unchanged; gains #317's sentence (a) | provenance #252, entry 1: "we don't want to have to have a point-to-point addressing but rather a tune-in filter."; entry 2: "with a second git repo, we may be able to have any dyad-system from anywhere to use it, not just those that are specific to a git repo as a message transport." |
| 311 | presence: dyad session touch -r reads the named rows' stored plan files | none: the work is delivered | delivered: retire (carried by #567) | plan #567, F4: "closes #311's item 1"; `files_of_rows` is on `main` |
| 313 | presence: dyad session list flags one holder behind two live seats | → group 5 | merged into group 5 | audit 2026-10-15 G3, under #310's mandate; a holder behind two units is a hop case the simulator can cover; the flag is still missing |
| 317 | Rule-3 Intake amendment: the store as the sender transport and the cos relayed-prompt sentence | (b) → #585; (a) → #303 | split into 2 | plan #317, F1: "Sentence (a) waits for #303; sentence (b) describes live practice (#301, #302) and may land alone." |
| 318 | reciprocal boundary sentence in syseng host-facts.md and sysarch distribution.md (residual of #81) | → group 2 | merged into group 2 | provenance #81, entry 1; neither file names host-install or host-platform yet |
| 319 | the platform gap: the macOS and Windows contracts host-platform.md declares are unmet | 319a and 319b (section 3.3) | split into 2 | its title: "one row per platform when prompted"; provenance #531, entry 1 |
| 320 | core-side citation of host-install.md and host-platform.md from Rule-11 p2 and Rule-8 (residual of #81) | → group 2 | merged into group 2 | provenance #81, entry 1; neither Rule cites them yet |
| 344 | rename dyad/scripts/ to dyad/tools/ and the other refactorings the taxonomy audit costed | *Proposed:* a table of the taxonomy audit's refactorings P1–P8, each landed or declined with its reason, with the core library's location read in one place (P2) before any rename. | unchanged | provenance #344, entry 1: "File is a backlog for refactoring to be performed by a separate session." |
| 514 | revisit chronicle's purpose ground for bundling with the core after episode 0 publishes | *Proposed:* once season 1's episode 0 is public, a one-page answer: the chronicle ships with the core or not, with the one-line purpose reason the bundle guard requires. | unchanged; waits on episode 0 (#503) | provenance #504, entry 1: "i believe the most distinguishing criterion is whether it directly contributes to the overall purpose of The Dyad System." |
| 533 | C2 order channel: authority down a strict chain on its own channel, held in reserve | *Proposed:* an order rooted in one of your recorded dispositions reaches a desk down the strict chain and executes only when every link traces to it; an order that widens it is refused; shown in a scratch repo. | unchanged; held in reserve | provenance #532, entry 2: "I believe a better solution is a clear command-and-control protocol that allows my authority to be applied down a strict chain of authority."; plan #532: "kept in case detection ever proves insufficient" |
| 534 | authority quick-check and reconciliation, held in reserve | *Proposed:* one command tells a unit whether an act on a row is covered (naming the entry), not covered (ask) or never carried, shown on three acts from this ledger; and a report maps every merge on `main` to its recorded `Y`. | unchanged; held in reserve | provenance #532, entry 3: "When a downstream seat can't honestly decide, we should provide a utility that allows the downstream to perform a quick-check against given authority." |
| 537 | cos mode P3: the lease | → group 4 | merged into group 4 | provenance #531, entry 3 |
| 538 | cos mode P4: the mode as one loadable unit | → group 4 | merged into group 4 | same |
| 539 | cos mode P5: follow into an unseated session | → group 4 | merged into group 4 | same; plan #531 marks P5 optional |
| 548 | board store and _cos.md keyed by cabinet | → group 5 | merged into group 5 | provenance #546, entry 1; simulator scenario S13 |
| 549 | board renders a since in the future of the reading host as skew, never a negative age | → group 5 | merged into group 5 | same; scenario S15 |
| 550 | seat-hop simulator: pairwise coverage over all six axes | → group 5 | merged into group 5 | same; audit 2026-11-02, finding F4 |
| 554 | remove the vocabulary aliases at the release after next | → #573's step 4 | absorbed into #573's step 4 | plan #573, step 4: "#554 is carried by this step"; step 4 follows the 0.18.0 cut (your B3), so it closes with step 4's Done, not with #573's 0.18.0 part |
| 576 | R-g fence (33 incidents) | → group 1 | merged into group 1 | provenance #570, entry 5 (hardening); #571's index, modes 01, 06, 19 |
| 577 | R-c fence (23 incidents) | → group 1 | merged into group 1 | same; modes 03, 17, 18, 31, 37 |
| 578 | R-h fence (16 incidents) | → group 1 | merged into group 1 | same; modes 02, 40 |
| 579 | R-a fence (15 incidents) | → group 1 | merged into group 1 | same; modes 09, 28 |
| 580 | R-d fence (13 incidents) | → group 1 | merged into group 1 | same; modes 12, 27 |
| 581 | R-e fence (10 incidents) | → group 1 | merged into group 1 | same; modes 07, 46 |
| 582 | R-f fence (10 incidents) | → group 1 | merged into group 1 | same; modes 16, 35 |
| 583 | R-b fence (8 incidents) | → group 1 | merged into group 1 | same; modes 41, 49 |

## 5. The step's test

The step is the paragraph "Definition of done (#574)" of `dyad/playbooks/d-work.md` at f35eb112 (lines 211–226).

**Enough, as written.**
- "drawn from the prompt, the row's refs and what the operator has judged before". Group 1 reuses your hardening DoD,
  already judged at #571's Done. Group 4 reuses your G and its roadmap's tests (#531). Group 5 reuses #546's prompt.
- "Work one DoD covers is one row". It produced the six merges, 28 rows into 6 DoDs. The clearest is group 1: eight
  fence rows under one count of resolved incidents.
- "work whose parts the operator would judge separately is split into rows". #319: its own title already asked for one
  row per platform.
- "the home proposes every DoD in one document ... and the counts are kept". This document.

**Unclear.**
1. "the agent takes the operator's DoD, when the prompt gives one, from the provenance record". Only 1 of the 49 rows
   holds a prompt in its own record (#139, relayed). 11 have no record (#84–#89, #130, #172, #173, #177, #181). 27 hold
   a bare `Y`, and 10 a disposition with a few words (#102, #344, #576–#583). The words were in the record of the row
   each came from (#50, #57, #81, #83, #94, #166, #174, #178, #252, #310, #504, #531, #532, #546, #553, #570). For
   #248 and #257 that record says nothing on the point (#241, #255). For #4, #5, #55 and #130 there are none; #54 is
   named only in passing, in #553's prompt. The step could say where to look: the row's record, then the record of the
   row its first `disposed` entry or its refs name.
2. "the row's refs". Refs are free text. #130's refs hold its description. #576–#583's hold mode numbers and an owner.
   #4, #5, #54, #55 and #139 cite a peer system's rows, which resolve nowhere here.
3. "its parts carried as accreted children". A `backlog` row cannot become an accreted child, because an accreted row
   is born `open` under a mandate (Rule-3 Scope). The step does not say what happens to existing backlog rows that one
   new DoD covers. This report proposes one new row per merged DoD and retires the members (groups 1–6).
4. Held PRs. One DoD over eight fences (group 1) means one done-`Y`, with every fence's PR held until that done-`Y`
   (#570 revision 2, B2). The step does not say how that cost weighs against "the largest scope".
5. Familiarity. "nothing else models the operator's familiarity" holds once you answer. For a proposal, the home has
   only your one example, cloud infrastructure. #319's split rests on reading host platforms as the same kind of
   domain.
6. "DoDs out". It does not say whether an open row's DoD that takes backlog work counts. This report counts it apart
   (section 2).
7. Rows that wait on an event or are held in reserve (#514, #533, #534). It does not say whether they get a DoD now or
   when the event comes. This report proposes one now.

**Missing.**
1. How an absorbed or merged row leaves. The step counts "absorbed" but names no route. The same play-book still says
   `archived` is reached "by the retirement form only" (line 134 at f35eb112). #574 revision 3's `retires` clause
   moved to #585 (its R7) and is not in the step. As written, each of the 33 rows here would cost a retirement-form
   question, which entry 4 of #574's record refuses.
2. Two outcomes the counts lack: a row *merged* into a new row, which is not absorbed into an existing one, and a row
   whose work is *already delivered* (#130, #311), which is neither. The grounds of `dyad/dmc/retirement-candidate.jsonld` (fenced, dead,
   carried, unread) are in the play-book's hygiene section but not linked from the step.
3. A check that a row is still owed before its DoD is proposed. #172's trigger has come. #96 has nothing to show (no
   ceiling marker in the tree). #60's premise is partly overtaken (section 6). The step proposes a DoD without asking.
4. A rule for quoting in a tracked document. Entry 1 of #166's record and entry 2 of #174's name a client or a company,
   and plans #54 and #55 quote another system's operator, naming outside services and a commercial deployment. The
   step says to quote with the entry. It should also say: quote only what may be published; otherwise cite the entry
   without quoting it.
5. Rule text the step cites that is not there yet. At f35eb112 Rule-3 is back at its base, its sentences moved to #585.
   So the step's citations of Rule-3, for the evidence opening with the DoD and for the carried `backlog` row, point to
   sentences that are not in Rule-3 until #585 lands. #574's own E1 found that a play-book sentence alone binds nothing.

## 6. The home's defaults (amend any by its number)

Each open point the draft found, with the path the home takes unless you amend it.

1. **How rows leave and open.** #574's Done question names every row this report retires (`retires #r, …`) and every
   new row it opens (groups 1–6, 319a, 319b). Your one done-`Y` opens the new rows as `backlog` first, then archives
   the rows they replace, in one record, so no row retires before its successor exists. Ground: "i shouldn’t be disposing “archive” - i’m expecting ‘done-Y’" (provenance #574, entry 4). The archiving is engineer's code from #574
   revision 3 (G5, G6), which rides the same Done. Amend "open later" to keep every row as it is today.
2. **Group 1 is one row.** You judge the eight fences by one number. The cost: each fence's PR waits for that one
   done-`Y`. The `v1.0.0` cut does not wait for group 1: #570's H1 counts a mode with a row as closed. Amend "keep
   eight" to keep R-a…R-h as eight rows.
3. **Group 2 is one report.** Every finding is judged the same way, by its before and after. Amend "per audit" for
   three rows.
4. **Groups 4 and 5 stay apart.** Group 4 is something you try: the cos follows you. Group 5 is a report you read: the
   simulator. #539 stays in group 4, since following you is your G. Amend "join 4 and 5" for one row.
5. **#173 stays in group 6.** #585's never-carried list stays as #585 planned it.
6. **Rows whose premise may be gone** keep the DoD above: #4 and #5 (plan #301: "LAN-git-era rows"); #60 (this
   instance has kept its own host change log since #175); #96 (no ceiling marker in the tree); #102 (no row since
   2026-09-20 mentions a zone contribution); #177 (the work of a downstream system); #533 and #534 (held in reserve
   "in case detection ever proves insufficient"). Amend "retire #n" for any you no longer want. The Done then retires it
   on the ground *dead*.
7. **Names.** The peer system, the client and the company stay unnamed. Their rows are cited by id: the titles of
   #54 and #55 are shortened, #177 is shown by id only, and the entries of #166 and #174 are quoted only in part.
8. **319b stays owed.** Your prompt on #81 names Windows portability.
9. **Order.** Group 4's MacBook leg needs 319a first. Group 1's R-c and group 3 each need a Rule-3 sentence, so they
   follow #585 (Rule-3 has one writer).
