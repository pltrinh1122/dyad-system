# Incident audit by failure mode — 2026-10-10

*Audit of `agent-corpus/audits/INCIDENTS.md` as of commit `052bf58`. d-work #259, parent of the
twenty-three per-mode records #262–#284. Detects and counts; disposes nothing (frame: detect,
don't dispose; play-book `dyad/playbooks/incident-hardening.md`, Conduct).*

**Ledger:** `agent-corpus/audits/INCIDENTS.md` · **covered through:** 146 rows, latest 2026-10-12

The live ledger holds 153 rows when this line lands — 147 at the head this amendment was written
against, plus the six this d-work's Part C appends — and the watermark deliberately stops at 146,
the last contiguous row carrying a mode. Rows 141 to 146 arrived while phases 1, 2 and 4 ran and
carry a mode assigned **by inference**, not by phase 1's two-view reconciliation: 141 to 144 in the
delta section below, 145 and 146 in their own consequence cells, both mode R with child row #279.
Row 147 is grouped by nobody — a concurrent session logged it, and grouping it is the next survey's
delta work rather than this amendment's — so the watermark stops before it. That is deliberate: the
play-book's phase 0 no-ops phases 1 to 3 when the live count **equals** the watermark and runs the
delta when it exceeds it, so a watermark of 152 would leave row 147 ungrouped for good, while 146
makes the next survey re-read from 147 on. The rows Part C appends are ahead of the watermark for
the same reason and name their own mode in their own cells; a concurrent session appending again
leaves this line correct, because it claims nothing about any row after 146.

## Phase 0 — the survey that made this a full derivation

Run through the core runner, `LEDGER=agent-corpus/audits/INCIDENTS.md dyad runbook run
incident-hardening survey`, at commit `052bf58` (event `incident-hardening-20261010T175000Z-survey`,
`workstation-corpus/runbooks/events/incident-hardening.jsonl`):

    live: 140 rows, latest 2026-10-10  (agent-corpus/audits/INCIDENTS.md)
    no index audit names agent-corpus/audits/INCIDENTS.md: first exercise, full derivation

No index audit had ever carried a `covered through:` line for this ledger, so the gate's first
outcome applied: the full derivation of phases 1 to 4. This file carries the watermark, so the next
invocation compares against it rather than re-deriving.

The 2026-09-22 exercise is the **prior population**, not the prior mode set: 34 rows in 9 modes
(`2026-09-22-incident-failure-modes.md`, records `#117`–`#125`). Those records stay where they are;
nothing here deletes, moves or renumbers them, and their letters are theirs. The play-book forbids
reading a previous index as the mode set, and names the case that falsified doing so — `#128`'s
attack 7 found a tenth mechanism one day after that index was written. 106 of this population's 140
rows were logged after it.

## Method — two independent derivations, then a reconciliation

The grouping is the load-bearing judgment of the whole exercise, so it was made twice, by two
subagents working separately over the same 140 rows, each forbidden to open the 2026-09-22 index or
its records, neither seeing the other's work (`delegation: plan-and-execute`, Rule-3 Scope: a
subagent reads, searches and drafts, and every row, commit and counter-prompt stays with the main
Agent). Both reported the sentinel before drafting.

- **View 1** derived **28 modes**, reading each row's `cause` cell first and its `what` cell second,
  and deliberately keeping small modes apart from large neighbours where the fence that would stop
  them differs.
- **View 2** derived **20 modes**, working bottom-up from the `cause` cells and testing every
  candidate by a one-sentence rule: if no single sentence names a change that would stop every row
  in a candidate, the candidate is two modes. It also recorded, per mode, whether the ledger shows
  the mode recurring *after* a mitigation some row's consequence cell describes.

Both assigned all 140 rows with no row in two modes and no row unassigned, and both verified their
own arithmetic. Row numbers throughout are positions among the lines matching `^| 20`, 1-based, in
file order — which is **not** date order, because rows are appended at the tail by several sessions
and some are backfilled for an earlier d-work.

The main Agent reconciled the two into the **23 modes** below and verified the result mechanically:
23 modes, 140 rows, every row of 1..140 in exactly one mode, counts summing to 140. The
reconciliation is this audit's own claim, and the decisions it turned on are recorded below rather
than smoothed over, because a taxonomy whose soft edges are hidden reads as firmer than it is.

## Modes

| mode | observed failure mode | rows | d-work | record | proposed exit |
|------|-----------------------|------|--------|--------|---------------|
| A | acting before the authorizing disposition | 13 | #262 | `2026-10-10-incident-mode-a.md` | 2 — backlog row |
| B | a disposition recorded that the Operator never gave | 3 | #263 | `2026-10-10-incident-mode-b.md` | 3 — unfenceable |
| C | a value stated from memory or a digest instead of read from its source | 13 | #264 | `2026-10-10-incident-mode-c.md` | 2 — backlog row |
| D | the wrong object read | 9 | #265 | `2026-10-10-incident-mode-d.md` | 2 — backlog row |
| E | an instrument narrower than the question | 4 | #266 | `2026-10-10-incident-mode-e.md` | 2 — backlog row |
| F | the d-work #N citation form used for a cross-reference | 3 | #267 | `2026-10-10-incident-mode-f.md` | 1 — fenced |
| G | a flag taken as a positional argument | 5 | #268 | `2026-10-10-incident-mode-g.md` | 2 — backlog row |
| H | the present enumeration pinned as an invariant | 6 | #269 | `2026-10-10-incident-mode-h.md` | 2 — backlog row |
| I | verified in one environment, run in another | 4 | #270 | `2026-10-10-incident-mode-i.md` | open |
| J | a call site added without its call graph | 3 | #271 | `2026-10-10-incident-mode-j.md` | 2 — backlog row |
| K | a plan incomplete against its own text | 8 | #272 | `2026-10-10-incident-mode-k.md` | open |
| L | a plan ordering no disposition sequence can authorize | 5 | #273 | `2026-10-10-incident-mode-l.md` | 2 — backlog row |
| M | no legal order, no verb | 11 | #274 | `2026-10-10-incident-mode-m.md` | open |
| N | a target named by an ambiguous pattern | 3 | #275 | `2026-10-10-incident-mode-n.md` | 2 — backlog row |
| O | a git write used as a read | 3 | #276 | `2026-10-10-incident-mode-o.md` | 2 — backlog row |
| P | unplanned cleanup under momentum | 4 | #277 | `2026-10-10-incident-mode-p.md` | 2 — backlog row |
| Q | an obligation no mechanism reads | 12 | #278 | `2026-10-10-incident-mode-q.md` | 2 — backlog row |
| R | a derived key that does not identify | 7 | #279 | `2026-10-10-incident-mode-r.md` | 2 — backlog row |
| S | a form typed from memory, not seeded from its governing definition | 4 | #280 | `2026-10-10-incident-mode-s.md` | 2 — backlog row |
| T | a stale or partial view of shared state | 10 | #281 | `2026-10-10-incident-mode-t.md` | open |
| U | the World moved | 6 | #282 | `2026-10-10-incident-mode-u.md` | 3 — unfenceable |
| V | enforcement routed around | 2 | #283 | `2026-10-10-incident-mode-v.md` | 2 — backlog row |
| W | the suite's environment leaked into the live repository | 2 | #284 | `2026-10-10-incident-mode-w.md` | 1 — fenced |
| | **total** | **140** | | | |

## What the reconciliation decided, and against what

Where the two views disagreed, these are the calls and the test applied. The test throughout: two
mechanisms are one mode only if one sentence names a change that would stop both, at one moment.

1. **A split three ways, not merged into one.** View 2 put 16 rows in one "acting before the
   authorization" mode. The reconciliation keeps **A** (the act ran early), **B** (a disposition the
   Operator never gave was written into the row) and leaves view 1's grab-bag "sequence bundled"
   mode dissolved. B is separate because it already has a live mechanical fence — Rule-7 property
   5's disposition count, which caught rows 20 and 70 — and A has none at all. Same family,
   different fence, different moment.
2. **C and D are separated by whether anything was read.** View 1 called them *from memory* and
   *neighbouring reading*; view 2 called them *from memory* and *the wrong object*. The boundary is
   the same in both and it holds: in C no source was consulted at the moment of use, in D a real
   artifact was read and it did not govern the question. Row 27 (a cause asserted and a guard
   proposed on it, untested) goes to C on that test, against view 1.
3. **The delegation boundary is not a mode.** View 1 made one of four rows (81, 83, 87, 100). Under
   the test it dissolves: 81 and 100 are D (the fork read its own clone's head, the redirect never
   reached the checkout and the default branch was searched instead), 83 is I (an assertion about
   "the live tree" that also runs inside a scratch install), 87 is K (a brief that named the method
   and not its host residue). What survives is an observation, recorded in D: three of its nine rows
   arose at a delegation hand-off, which is where that mode concentrates — not a mechanism of its own.
4. **Plan faults split three ways.** **K** is a plan that does not satisfy its own text, **L** is a
   plan whose step order no disposition sequence can authorize, **M** is a change the Rules and the
   tooling admit no order or verb for at all. The test for M is that no plan could have succeeded;
   the test between K and L is contents against order. View 2 merged K and L; view 1 split them, and
   the split is kept because the fence differs — derive the file list from the plan's own text,
   against derive the order from what authorizes each step.
5. **Declared departures stay with the deadlock that caused them.** View 1 made a mode of "the
   prescribed path was unusable, so a stated departure was taken" (rows 110, 121, 126). Rows 121,
   126, 128 and 129 are in **M**, because what made the path unusable in each is a two-constraint
   interaction with no legal order. Row 110 goes to **Q**: nothing in the corpus names a
   draft-to-ready step at all, which is an absent obligation and not a deadlock.
6. **"A defect in the tooling" is not a mode; a key that cannot identify is.** View 1's tooling-defect
   mode and view 2's *derived key that does not identify* cover nearly the same rows. **R** keeps
   view 2's name, because it states the mechanism: the trace anchor, `session_id()`, the presence
   store's derived `rows`, the table parser's cell split, the `_MERGE` regex and `check_transaction`'s
   dispatch on the checked-out branch all fail the same way — the key does not identify the thing its
   callers believe it identifies.
7. **The environment leak stays its own mode.** View 2 folded rows 57 and 58 into *verified in one
   environment, run in another*. They are kept as **W**, two rows, because the mechanism is an
   exported `GIT_DIR` reaching the suite's children and the damage was done to the live repository —
   a different fence (strip or override the environment at the hook boundary) at a different moment
   from I's (exercise the check in each environment it can run in).
8. **Momentum was refused as a mode**, on view 2's reasoning, which the reconciliation adopts: several
   rows across A, P and C name momentum or an attentional slip as the cause in as many words, but it
   names a state of the Agent rather than a mechanism, and no single sentence states a change that
   would stop it. Where momentum appears, the mode is what the momentum ran past.

Three candidate mechanisms were seen and **not** raised to modes, and are recorded here so the next
exercise can find them rather than re-derive them:

- *Package or instance leakage* — a craft artifact pinning one system's instance state (rows 12, 59,
  83). Three partial cells, each fitting H or I better.
- *A prescribed form too costly to follow at scale* (row 126 alone) — four 217-line evidence blocks
  cited by digest instead of pasted verbatim.
- *A measurement invalidated by the act of measuring* (rows 74, 123, and 127's monotonic anchor
  degradation). View 2 believes this one is real and under-evidenced: three rows, three instruments,
  and in each case observing changed what was observed. Left in U, I and R.

## Rows whose mechanism the ledger itself does not establish

- **Row 123** (2026-10-09, #256) — 23 of 624 tests did not run under the pre-push gate where the same
  tree passed directly, and the row states **cause not established**. Row 124 records that the
  `ERROR:` text which would have identified it was destroyed by a case-sensitive filter before anyone
  read it. Filed **I** on shape alone. Both derivations named it the one row in the population whose
  mechanism is genuinely unknown; plan #256 revision 4's two candidates — reproduce with the memo
  removed, and widen the memo key or deny the pre-push skip — are the only route to one.
- **Row 17** (2026-09-14, #13/#16) — an `HTTP 403: Resource not accessible by integration` that
  persisted after the Operator set `default_workflow_permissions: write`. The row says in as many
  words that the actual cause is not known. Filed **U**, where its evidence points. Row 133 records
  that the condition "no longer obtains", which closes the symptom and names no mechanism.

## Phase 4 — the exits each mode proposes

Two modes close by a fence that already exists and was verified at its moment: **F** (the plan gate's
`check_transaction`, which refused all three occurrences before anything reached `origin`) and **W**
(`suite_env` at both suite spawns, with a control test asserting the damage recurs without it).

Two close by a recorded impossibility on this kernel: **B**, on Rule-7's own Enforcement — whether an
entry is a faithful transcription is inference — and **U**, on Rule-14 property 2, a hosted git
service is never kernel.

Fifteen close by a `backlog` row naming a fence to build. Those rows are #262–#284's own business:
each mode's record states what the row would say and which of its incidents the fence would have
caught, and nothing is built here, because phase 3 is excluded from #259's plan-`Y` by that plan's
own text.

**Four modes — I, K, M, T — reach no exit at all and are stated open.** The play-book requires that
be said rather than deferred: a mode holding none of the three exits is open whatever its record says
about it. K and M are the two largest of them and the reason is the same in both — a shipped fence
exists and catches a downstream symptom, not the mechanism. T reaches no single exit because it is
two modes (see below).

Plan #137's attack 3 — that the previous exercise produced nine mode records and zero fences — is
**not refuted by this one either**. No new mechanical check was built. What is different is that
fifteen candidates are now rows with ids, each beside its mode's record, instead of paragraphs in an
audit: that is the specific failure the play-book was written to prevent, and it is the only thing
this exercise can claim to have fixed.

## Findings verified during phase 2

Every delegated finding below was re-read by the main Agent against the tree at `cff41fb` before it
was written down (plan #260's shape: a fork's finding is not evidence until the main Agent verifies
it). Each is a measurement taken today, not a figure quoted from a row.

1. **A failing suite is reported as one line.** `check_rule_12` reports a non-zero suite child as
   `r.stderr.strip().splitlines()[-1]` (`dyad/scripts/package.py:233`) and `cmd_tests` prints
   `err.strip().splitlines()[-1]` (`:442`). The 29 `ERROR:` blocks behind row 123 were therefore
   destroyed inside the runner, before any filter the Agent wrote. Incident row 124's cause is wrong
   about where the evidence was lost; **row 141** is that correction, and row 124 stays as written
   because rows are the record.
2. **Rule-16's overlap signal is blind for most plans.** `sessions.files_touched`
   (`dyad/guards/agent/sessions.py:64-78`) reads the inline `files touched:` line and states in its
   own docstring that the `## files touched` heading form "is not read". Run over all 184 stored plan
   files today it returns nothing for **106** of them. The one signal Rule-16's presence store exists
   to carry — two sessions on different rows about the same file — is absent from 58% of plans.
3. **Mode G is unfixed on at least five surfaces.** `#133`'s refusal covers `dwork` only.
   `dyad check --help` falls through `package.py:1062-1073` to `cmd_check()` at `:1074`, and
   `craft export <craft> --help` still writes a file named `--help` (`dyad/scripts/craft.py:171`).
   No test anywhere asserts that `--help` exits 0.
4. **A live enumeration pin.** `dyad/tests/test_package.py:60` asserts the guard list *derived from
   disk* is **equal** to the literal `CORE + CRAFT` at `:5-6` — row 95's exact shape. Backlog #10
   cannot be mode H's fence row: its immutable title says the work was delivered and the row is a
   note only.
5. **The presence store has got worse, not better.** 64 presence files, 57 of them `unnamed-*`,
   against row 96's measurement of 55 and 49; `session_id()` still mints a fresh id per call.
6. **Rule-11's two amendments for the version/zone family left a hole in the middle.** `#156` made an
   unreleased craft warn (`dyad/guards/infra/bundle.py:155-156`) and `#230` added a warn path gated on
   `(comp, ver) in tagged` (`:146`); a `VERSION` bump *between* releases matches neither, so control
   falls to the hard FAIL at `:149` — which is why row 115 recurred hours after the second amendment.
   `rows/170.md` is still `backlog` although `rows/230.md` reads as closing it.
7. **The release automation exists.** `.github/workflows/dyad-release.yml` is present and works, so
   mode Q's row 133 is "nothing checks that the workflow was used", not "no automation exists". That
   also makes backlog **#20**'s premise partly stale — surfaced here, not altered: the row is the
   Operator's.
8. **The manifest's kernel row for Git is stale.** `dyad/infrastructure/INFRASTRUCTURE.md:14` records
   `2.43.0 observed`; the live host answers `git version 2.53.0`. Rule-14 property 2 asks for versions
   recorded as observed. Surfaced, not fixed: a manifest row is its own d-work.
9. **Four Rule-8 change-log rows are missing.** Mode P's four branch deletions and the commands behind
   modes N and O have no row in `workstation-corpus/CHANGELOG.md`, which Rule-8's Conduct makes a
   breach for each reversible or destructive action. Surfaced as a finding of this audit; writing them
   now would be a workstation-zone d-work of its own, and the rows that record the actions already
   exist in this log.

## The delta this exercise logged itself

The derivation covered rows 1–140. Executing phases 1 and 2 then logged four more rows in this same
log, and all four are classified here rather than left for the next survey. (This paragraph read
"two more rows" and "the watermark above reads 142" until d-work #259's revision-4 amendment; two of
the four below arrived after it was written, and the watermark is now 146.)

- **row 141** → mode **D**, the wrong object read: row 124's cause asserted from the half of the
  pipeline the Agent had written, without reading the half it had not.
- **row 142** → mode **R**, a derived key that does not identify: `dyadlib.tables` split row 141 on
  the separator characters inside a quoted `grep -E` alternation and refused it as seven cells. Second
  authoring-side occurrence after row 99, which opened backlog **#171**, where it still stands.

- **row 143** → mode **S**, a form typed from memory: the 23 child rows were opened with the
  ledger's bare-id `refs` form instead of the `refs: parent #259` the play-book and this plan both
  write out. Corrected on all 23 rows, `refs` being mutable where id and title are not. Third
  instance of mode S inside this one d-work, after rows 140 and 142.
- **row 144** → mode **M**, no legal order: plan #259 required one child row per mode, and Rule-3
  says a decomposed parent's counter-prompt is asked only when every child is `done` or `blocked`.
  All 23 are `backlog`, which is neither, so **#259 cannot reach its own Done question**. Recorded as
  plan #259 revision 3 before any question was asked. The consequence is the same escape revision 2
  used: PR #365 and PR #366 take their own merge `Y`, Part B's output lands, and #259 stays `planned`
  until the Operator disposes the 23 modes.

The child rows' titles name their counts "of the 2026-10-10 derivation over 140" and are immutable
(Rule-16); these four rows are additions beyond that derivation, so D, R, S and M held ten, eight,
five and twelve rows respectively when this section was first written.

Row 144 is classified three ways in the corpus and this amendment does not settle it: its own cause
cell in the log says mode L, its consequence cell says mode Q with child #278, and this section says
mode M. The play-book's phase 1 gives the rule — the mechanism that *started* it is primary and the
other is named secondary — and it was not applied. Surfaced here, not resolved: the log is
append-only and a third reading would only add to the count. It is excluded from mode Q's record
below for that reason.

Seven further rows arrived after those four — rows 145, 146 and 147, and the six this d-work's Part
C appends (rows 148 to 153). Each is classified in its own consequence cell, in the form rows 145 and
146 already use, naming its mode and the child row that disposes it, and each mode's own record now
carries it:

- **row 145** (2026-10-12, #285) → mode **R**, sub-shape *not stable*: a third presence file shed
  for this one working tree, `session_id()` minting a fresh id per call with `DYAD_SESSION` unset.
- **row 146** (2026-10-12, #261) → mode **R**, sub-shape *not the right dimension*: `check
  --evidence` keying the tree it judges on the invoked entrypoint's own directory rather than on the
  head it was asked about, and printing a self-signed 0-FAIL block for the wrong one.
- **row 147** (2026-10-13, #287) → **no mode**. A concurrent session logged it; grouping it is the
  next survey's delta work, and the watermark above stops before it for that reason.
- **row 148** (2026-10-12, #260) → mode **R**, *not able to match the form written*: which of two
  window-end branches runs, decided by whether the Done disposition anchors.
- **row 149** (2026-10-12, #261) → mode **Q**: the trace play-book's Evidence clause, whose object
  is a completion reply no code parses.
- **row 150** (2026-10-12, #260, #261, #285) → **no mode assigned**. Its mechanism is the
  named-but-not-raised candidate of this audit, *a measurement invalidated by the act of measuring*
  (the Modes section above, left in U, I and R), and no child row owns that candidate. Left
  unassigned rather than forced into R.
- **row 151** (2026-10-13, #222, #231, #232) → mode **Q**: the play-book's own order of `dwork state
  done` before `trace --out`, read by no code, with `check_store` holding the state it would need.
- **row 152** (2026-10-13, #259) → mode **R**, sub-shape *not stable*, with the new sub-shape that
  the mitigation for a non-stable key was itself held in non-durable state.
- **row 153** (2026-10-13, #259) → mode **W** inverted: the mode is the suite's environment leaking
  into the live repository, and this is the live push invocation's `-c` config leaking into the
  suite, through a variable `GIT_VARS` does not drop. It is also the cause row 123 lacked. Child
  row #284.

So mode Q now holds 14 rows, mode R 12 and mode W 3, counting the derivation's own and these additions; the
immutable child-row titles and the modes table above keep naming the derivation's 12 and 7.

One of the four is a fact about this exercise rather than about the ledger: following the play-book's
own phase-1 prescription is what made the parent uncloseable. The play-book says to open a child row
per mode and Rule-3 says the parent waits for all of them, and nothing reads either clause — mode M
meeting mode Q, in the exercise written to find them.

## What the next derivation should look at first

- **Split T.** Its id races and its partial-view rows reach different exits, which is why it reaches
  none. Two modes, two fences.
- The three candidate mechanisms named above — package or instance leakage, a prescribed form too
  costly at scale, and a measurement invalidated by the act of measuring — each had too few rows
  today. The third is the one both derivations thought was real.
- **Row 123 and row 17**, whose mechanisms the ledger does not establish. Finding 1 above changes
  row 123's prospects: the reason is a one-line report in shipped code, so persisting the failing
  child's stderr (mode E's candidate, child #266) is a route to a cause that did not exist before.

## Phases 2 and 4

Each mode's record carries its own phase-2 inventory — every live mitigation read from the code and
the Rule text, never from an audit's prose, with the path and identifier, the moment it fires, the
rows it reaches and those it does not, whether it is shipped or a candidate, and whether anything of
that mode recurred after it shipped — and one remediation candidate under attack (Rule-9). Each
record proposes exactly one of the play-book's three phase-4 exits, or states the mode open. Nothing
in this audit or in any record closes a mode: a proposal is not a disposition, and phase 3 — building
a survivor — is excluded from #259's plan-`Y` by that plan's own text and belongs to each child row's
own plan-`Y`.

*Disposition: see the Done-`Y` of d-work #259 (Rule-2, Rule-9 Form).*
