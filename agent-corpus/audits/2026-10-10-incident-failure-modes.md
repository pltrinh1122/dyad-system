# Incident audit by failure mode — 2026-10-10

*Audit of `agent-corpus/audits/INCIDENTS.md` as of commit `052bf58`. d-work #259, parent of the
twenty-three per-mode records #262–#284. Detects and counts; disposes nothing (frame: detect,
don't dispose; play-book `dyad/playbooks/incident-hardening.md`, Conduct).*

**Ledger:** `agent-corpus/audits/INCIDENTS.md` · **covered through:** 233 rows, latest 2026-10-26 (the 2026-10-10 derivation covered 144; rows 145–213 were grouped by the delta derivation of 2026-10-24, d-work #259 revision 5; rows 214–233 by the delta of 2026-10-26, d-work #472, both below)

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

The derivation covered rows 1–140. Executing phases 1 and 2 then logged two more rows in this same
log, so the watermark above reads 142 and both are classified here rather than left for the next
survey:

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
(Rule-16); these four rows are additions beyond that derivation, so D, R, S and M hold ten, eight,
five and twelve rows respectively as of this commit.

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

## Delta 2026-10-24 — rows 145–213, grouped against the 23 modes (d-work #259 revision 5, seat audit-89a934d6)

Phase 0's third outcome: the ledger held 200 rows against the watermark 144, and 213 after this
PR's own thirteen (five owed by the 2026-10-12 Done turn, eight for this week). Only the new rows are
classified here; the 140 rows of the 2026-10-10 derivation keep their modes. The method is the
2026-10-10 one: two subagents, forbidden the 2026-10-10 records and this index, grouped rows 145–200
independently — view 1 derived 24 modes reading `cause` first, view 2 derived 15 reading `what` first
and the moment a check could meet it — and this seat mapped each row to one of the 23, or to none.
Both views assigned all 56 rows with none in two modes; the reconciliation below was verified
mechanically (56 + 13 rows, each in exactly one mode, counts summing). The thirteen rows this PR
appends (201–213) were written by this derivation and carry their mode in their own cells.

### Rows 145–213 by mode

| mode | delta rows (145–200) | rows 201–213 | delta | was | now |
|------|----------------------|--------------|-------|-----|-----|
| A | 198 | — | 1 | 13 | 14 |
| B | — | — | 0 | 3 | 3 |
| C | 158, 161, 186, 193, 195, 199, 200 | — | 7 | 13 | 20 |
| D | 156, 184, 191 | — | 3 | 9 | 12 |
| E | 157, 165, 172, 187, 197 | 209, 212 | 7 | 4 | 11 |
| F | 166 | — | 1 | 3 | 4 |
| G | 159, 182, 196 | 213 | 4 | 5 | 9 |
| H | — | — | 0 | 6 | 6 |
| I | 147, 160, 162, 189 | — | 4 | 4 | 8 |
| J | — | — | 0 | 3 | 3 |
| K | 181 | — | 1 | 8 | 9 |
| L | 163 | — | 1 | 5 | 6 |
| M | 149, 154, 169, 188 | 207 | 5 | 11 | 16 |
| N | 179 | — | 1 | 3 | 4 |
| O | 190 | — | 1 | 3 | 4 |
| P | — | — | 0 | 4 | 4 |
| Q | 151, 171 | 202, 204, 206, 210 | 6 | 12 | 18 |
| R | 145, 146, 152, 153, 155, 167, 180, 192 | 201, 203, 205, 208 | 12 | 7 | 19 |
| S | 164 | 211 | 2 | 4 | 6 |
| T | 148, 168, 170, 178 | — | 4 | 10 | 14 |
| U | — | — | 0 | 6 | 6 |
| V | 176 | — | 1 | 2 | 3 |
| W | — | — | 0 | 2 | 2 |
| **X** (new) | 150, 173, 174, 175, 183, 194 | — | 6 | — | 6 |
| **Y** (new) | 177, 185 | — | 2 | — | 2 |
| | | | **69** | **140** | **209** |

### Two mechanisms no existing mode names

Both were seen by both views as modes of their own, and the 2026-10-10 definitions were read against
each row before either was admitted (the test throughout: does one sentence name a change that stops
every row of the candidate at one moment, and is that sentence already some mode's).

**X — tail-append contention under a held PR.** A PR held across a counter-prompt carries an append to
`agent-corpus/audits/INCIDENTS.md`, the one file every seat's PR appends to at the same place; a peer
lands first inside the hold window, the hosting refuses the merge, and the rebase that resolves it
changes the head the `Y` was given on (Rule-2, Binding) so the question is asked again. Rows 150, 173,
174, 175, 183, 194. Not T: T's change (refresh the view at the moment of the act) does not stop a
conflict that arises *during* a hold, however fresh the view was when the question was asked (row 183:
mergeability re-read in the asking reply, conflicted 28 s before the record). Not M: M's deadlock
followed four of these six and is fenced since #202 (below); row 194, after that fence, shows what X
is without M — two re-asked Done questions and no deadlock. The 2026-10-10 derivation filed row 123
(#242), the same peer-append cause, under M because the deadlock was what it cost; on a full
re-derivation 123 and the #355 rows (149, 171) would be read against X. What would have to change:
an incident row never rides a held PR — it lands first in its own narrow PR (the protocol
`merge-disposition`'s own note and `dyad/playbooks/disposition-digest.md` already state, breached in
five of six rows after it was written), or the log becomes a per-row store with no shared tail
(`<instance>/audits/incidents/<n>.md`, the shape `rows/` already takes for the same reason, Rule-16).

**Y — the gate starved of a host resource by the system's own process.** The pre-push suite died at its
600 s ceiling because a foreground spin-wait of the Agent's own took a core it needed (177), and died on
`ENOSPC` because 24,876 of the suite's own orphaned fixture directories had exhausted `/tmp`'s inodes
(185); in both the push could not leave any clone. Both rows say in their own cells that no mode of
A–W fits. Not U: U's fault is The World's (a hosting, an account, another process's load), observed
and never pinned; here the consumer was the dyad's own process. Not J or W: nothing was spawned
without its guard and nothing leaked *into* the repository. What would have to change: every process
the gate runs must bound the host resources it consumes and release them — the suite sweeps its own
temp root per child (shipped by #326, 2026-10-15, `9c3daec`), and a wait sleeps, never spins (conduct,
row 177's own rule; no mechanism reads the Agent's shell).

The play-book's Phase 0 says a full re-derivation happens on the Operator's word or when a new row's
mechanism is named by no existing mode. This exercise asked and ran the delta only (plan #259 revision
5); the two new modes are recorded with their delta rows and proposed as child rows, and whether the
whole 213 are re-derived against 25 modes is stated as the Operator's question, not taken.

### What the reconciliation decided, and against what

1. **The presence store's eleven rows are R and G, not a mode of their own.** View 1 made four modes of
   them (bare touch, minted id, writer scope, `-r` token) and view 2 one (`session touch` writes before
   it parses). Under the 2026-10-10 definitions they divide on one test — was a flag misread (G: 159,
   182, 196, 213) or a key derived that does not identify (R: 145, 152, 153, 155, 180, 192, 201, 203,
   205, 208)? — because the fence differs: a dispatch reader for the first, a key shown to identify at
   its definition for the second. The store is where R now concentrates: twelve of its nineteen rows.
2. **The shallow clone is I, not a mode.** Views 1 and 2 both carved rows 147, 160, 162 and 189 out as
   "guard verdict depends on clone depth". The 2026-10-10 definition of I — a verdict observed in one
   environment and asserted of another that differs in an input nothing had named — holds: the guards
   were written against a full clone, the clone's depth is the unnamed input, and the change I names
   (make the difference an explicit input of the assertion) is the fix: skip with one line on a shallow
   clone, as Rule-20 property 2 does for an absent store. Row 147's first refusal (open and planned in
   one commit) is a fence working as designed on a clerical slip and is not a mode; its second half is I.
3. **The `dbfe778` wedge is T; the swallowed push that started it is E.** Rows 170 and 178 are two clones
   receiving one event and stay in T as their authors placed them. Row 172, the writer's side, started
   with a `grep` over `git push`'s output hiding the refusal (E, the row 123 class) and then read `HEAD` as
   pushed (T, secondary). Row 197's lost push is the same instrument (a loop reading ` -> main`) and is E.
4. **Gate-after-Done stays M and its rows go to X where the conflict started them.** Rows 173, 174, 175
   and 183 each ran: a peer append conflicted the held PR, then the Done record made the row terminal and
   the gate refused the recovery. The conflict is the mechanism that started each; M is secondary. Rows
   149 and 169 (PR #349, PR #355: merges never attempted, no conflict first) stay M. Row 154's missing
   entry form and row 188's version/zone pair are M's other two faces (no verb, no legal order), and
   row 207 (the hand-composed `Y done (mandate …)` entries) is the no-verb face again.
5. **Stated-not-read divides C from D by whether anything was read.** View 1 put ten rows in one
   "behaviour stated instead of read" mode and view 2 thirteen. The 2026-10-10 boundary holds: no source
   consulted → C (158, 161, 186, 193, 195, 199, 200: a `VERSION` file, an invariant's name, a remembered
   count, an assumption about GitHub); a real object read that did not govern → D (156 read the write
   format and not the readers; 191 read Rule-16's text and not the code; 184 wrote the live row where the
   fixture was the object). Row 165 (an attack disposed on a correlation that could not discriminate) is
   E: the instrument, not the object.
6. **Row 198 is A.** A push to a PR already named in a pending Done question is an act whose
   authorization was pending; that the two parties were two seats (the M4 relay delay) is the condition
   that made it likely, not the mechanism. Row 199 (evidence in words, not the block) is C, as the Part A
   row for cited-by-digest blocks was.
7. **Row 151 is Q**, fenced since 2026-10-14 by removal — `batch-disposition-mode: always` — which is a
   preference value and not a check; it is recorded as such in Q's record rather than counted as exit 1.

### Phase 2 over the affected modes — what shipped, what recurred

Read from the code on 2026-10-24 at `97e9cf7`, never from the 2026-10-10 prose; each affected record
carries the detail in its own `## Delta 2026-10-24` section. In twelve days three mechanisms shipped that
reach a mode of this ledger, and none of them was built *as* a mode's fence by a child row:
- **#202 (`0a4060e`, 2026-10-15) — the Done state follows the merge.** `rows.done_order_problems`,
  `rows.landing_problems`, `rows.done_recorded_not_closed`, and the matching `cmd_dwork state` refusals
  before the first write. Moment: the CLI call and every push, per commit. Reaches M's gate-after-Done
  cluster (rows 82, 116, 129, 149, 169, and 173, 174, 175, 183 as their secondary) and Q's row 171. Zero
  recurrence of that shape since; row 194 (2026-10-21) is the first conflicted Done after it and shows a
  rebase and a re-asked `Y` where the nine earlier rows show a deadlock.
- **#290 (`7e8a405`, 2026-10-14) — the accreted row's entry form** (`dwork new --mandate`), `backlog →
  archived`, the parent gate admitting `backlog`. Reaches M's row 154 (fixed) and this d-work's own
  revision 3 obstacle (lifted). Row 207 shows the Done half of the same form still has no verb.
- **#326 (`9c3daec`, 2026-10-15) — the suite sweeps its own temp root per child.** Reaches Y's row 185
  at the gate; nothing reaches 177.
Preference changes that removed a signal rather than fencing it: `batch-disposition-mode: always`
(Q, row 151). Additions that touched a mode's store without changing its key: #294's `host`/`holder`
lines and #393's attendance (R: `same_root` and liveness read neither; row 208, row 209).

**Recurrence, the measurement.** Of the seventeen modes the delta touched, two (F, W) are fenced and
F's one new row was caught by its fence; one (M) gained a fence for its largest cluster after the fact
and that cluster has not recurred; the other fourteen recurred with no mitigation at the fault's moment
— R twelve times, C seven, E seven, Q six, G four, I four, T four. Fifteen `backlog` rows (#262–#284
less the fenced two) have stood since 2026-10-10 naming a fence to build, and not one has been built:
69 new rows against zero fences from this exercise's own children is plan #137's attack 3 confirmed a
second time, at a larger population.

### Falsification — is each affected mode still addressed as the 2026-10-10 record said?

Written here, not in `agent-corpus/falsification/`, because the audit seat's charter forbids it that
directory (plan #259 revision 5, fence item 1); the amendment of
`agent-corpus/falsification/2026-10-10-incident-modes-addressed.md` is proposed to the counsel seat below.
One attack per affected mode and two on the exercise; each pushed to confirmed, refuted or
survives-scoped; Rule-9's easy-agreement trigger fired on F and W (agreement on first reading) and both
were attacked by reading the fence's code and its reach today.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A is addressed as the record said (open; exit 2 for one face) | **confirmed as open.** Row 198 is a third face — a seat pushing to a branch named in a pending Done — reached by nothing | open; the proposed row stands; the new face is conduct unless branch protection, which is not kernel |
| 2 | C is addressed (open, exit 2 for 3 of 13) | **refuted, and worse than the record said.** Seven recurrences, none in any shipped item's reach; the id-print and the evidence block both existed and were not read | open; the plan-file identity case would reach 193's second half only |
| 3 | D is addressed (open) | **confirmed as open.** Three recurrences; the one fence that fired (184) fires on the consequence, not the choice of object | open |
| 4 | E is addressed (open, exit 2 for 1 of 4) | **refuted, and the mode is in shipped code twice over.** `pushed_refs`'s empty-stdin line (212) and the attendance liveness read (209) are instruments narrower than their questions, and five more rows are filters the Agent typed | open; two code-reachable rows stated for the engineer seat |
| 5 | F is addressed (fenced) | **confirmed.** `prs.check_transaction` unchanged; row 166 met it; four of four | exit 1 holds |
| 6 | G is addressed (exit 2 proposed) | **refuted as "addressed", confirmed as "named".** Four recurrences on the verbs #133 did not cover, three of them one command; #268 names the fence and nothing is built | exit 2 stands; the measurement attack 7 asked for is in |
| 7 | I is addressed (open) | **survives, scoped.** The shallow-clone sub-shape now has a `backlog` row naming its fence (#315), which it lacked on 2026-10-10; row 123's sub-shape is unchanged | exit 2 reachable for one sub-shape, open for the other |
| 8 | K, L, N, O, S, V are addressed as their records said | **confirmed as the records said**, one recurrence each, no mitigation reached any; L's row 163 is the one whose specific step #202 since made legal | as proposed |
| 9 | M is addressed (open) | **refuted as a single claim; the mode splits.** The gate-after-Done cluster is fenced at a named moment by #202 and has not recurred; the no-verb face (154, 207) and the version/zone face (188) recurred and have no fence | exit 1 for the cluster; open for the two faces; one candidate stated (`dwork state … done --mandate`) |
| 10 | Q is addressed (exit 2 proposed) | **refuted.** Six recurrences; two of its shapes gained fences from other d-works (#202, `always`) and four new obligations no mechanism reads were added by the organization work itself (charter ceiling, ops-script delivery, preview traces, trace evidence lines) | open; the register candidate stands; two candidates added |
| 11 | R is addressed (exit 2 proposed) | **refuted, and the mode nearly tripled.** Twelve recurrences; four fences named by rows that already exist (#311, #312, #313, #286), zero built; the store this record measured at 64 files holds 88 | open; the honest statement is that R's fences are the cheapest in the ledger and the least built |
| 12 | T is addressed (open, split recommended) | **confirmed as open, and a third family added.** Unpushed state published as shared (170, 172, 178) joins the id races and the unfetched views | open; the split stands with three halves |
| 13 | W is addressed (fenced) | **confirmed.** Both test classes present, `suite_env` at both spawns, zero rows of the shape in 69 | exit 1 holds |
| 14 | the 23 modes are still the right 23 | **refuted.** Two mechanisms no mode names, each seen by both views: X (tail-append contention under a held PR, six rows) and Y (the gate starved by the system's own process, two rows). The record X is written; Y's record is owed (plan #259 revision 5 bounded new records to one) and its definition stands in this index | 24 recorded, 25 derived; the full re-derivation the play-book names for this case is the Operator's word |
| 15 | this exercise produced fences, not paragraphs (plan #137's attack 3) | **refuted a second time.** Every fence that reached this ledger in twelve days came from a d-work opened for another reason (#202, #290, #326); the exercise's own 23 children produced none. The exercise is now a measuring instrument and not yet a hardening one | the finding is stated for the Operator: the children are `backlog` and open on a prompt; the ones with the highest recurrence per fence named are R (#311–#313, #286), G (#268), M's no-verb face |

### Phase 4 — every mode after the delta

| mode | rows | exit on 2026-10-10 | re-verified 2026-10-24 | status |
|------|------|--------------------|------------------------|--------|
| A | 14 | 2 proposed (one face) | #262 `backlog`, nothing built; +1 new face | open |
| B | 3 | 3, Rule-7 Enforcement | sentence unchanged; 0 recurrence | exit 3 proposed |
| C | 20 | 2 proposed (3 of 13) | #264 `backlog`; +7 | open |
| D | 12 | 2 proposed (1 of 9) | #265 `backlog`; +3 | open |
| E | 11 | 2 proposed (1 of 4) | #266 `backlog`; +7, two in shipped code | open |
| F | 4 | 1, `prs.check_transaction` | code unchanged, row 166 caught | **exit 1 holds** |
| G | 9 | 2 proposed | #268 `backlog`; +4 on uncovered verbs | exit 2 named, unbuilt |
| H | 6 | 2 proposed | #269 `backlog`; 0 recurrence | exit 2 named, unbuilt |
| I | 8 | open | #270 `backlog`; +4, and #315 now names the sub-shape's fence | open; exit 2 reachable |
| J | 3 | 2 proposed | #271 `backlog`; 0 recurrence | exit 2 named, unbuilt |
| K | 9 | open | #272 `backlog`; +1 | open |
| L | 6 | 2 proposed | #273 `backlog`; +1 | exit 2 named, unbuilt |
| M | 16 | open | #202 fences the gate-after-Done cluster (0 recurrence since 2026-10-15); no-verb and version/zone faces +3 | **split: exit 1 for the cluster, open otherwise** |
| N | 4 | 2 proposed | #275 `backlog`; +1 | exit 2 named, unbuilt |
| O | 4 | 2 proposed | #276 `backlog`; +1 | exit 2 named, unbuilt |
| P | 4 | 2 proposed | #277 `backlog`; 0 recurrence | exit 2 named, unbuilt |
| Q | 18 | 2 proposed | #278 `backlog`; +6; rows 7, 75 fenced (#191), 171's shape fenced (#202), 151 removed (`always`) | open |
| R | 19 | 2 proposed | #279 `backlog`; +12; four fences named by #311, #312, #313, #286, none built | open |
| S | 6 | 2 proposed | #280 `backlog`; +2 | exit 2 named, unbuilt |
| T | 14 | open, split recommended | #281 `backlog`; +4; a third family | open |
| U | 6 | 3, Rule-14 p2 | sentence unchanged; 0 recurrence | exit 3 proposed |
| V | 3 | 2 proposed | #283 `backlog`; +1 of the row-47 shape the proposal does not reach | open |
| W | 2 | 1, `SpawnSiteTests`, `SuiteEnvWorktreeTests` | both present, `suite_env` at both spawns; 0 recurrence | **exit 1 holds** |
| X | 6 | — | new; the protocol is prose and was breached five times after it was written | open; child row proposed |
| Y | 2 | — | new; #326 fences 185 at the gate; 177 is conduct | open; record and child row proposed |

"Exit 2 named, unbuilt" is the play-book's exit 2 read literally — the row exists and names the fence —
and is reported with that qualifier because fifteen such rows in fourteen days have fenced nothing; the
Operator reads the qualifier, the Agent closes no mode (play-book Conduct).

### Proposed, opened by nobody here (the audit charter: proposes rows, opens none)

Each is a row for the Operator to open by prompt, or for the program under a mandate the Operator
grants; the mode and the rows it would reach are stated so the Operator can price it.
1. **Child row for mode X** (`refs: parent #259`): the tail-append contention record's exits — the
   protocol as a check (a PR guard warning when a held PR's diff touches `INCIDENTS.md` beside other
   paths) or the per-row incident store. Reaches 150, 173, 174, 175, 183, 194 and, on re-derivation, 123,
   149, 171.
2. **Child row for mode Y** and its record file: the gate's host-resource bound. Reaches 177, 185.
3. **Counsel seat:** amend `agent-corpus/falsification/2026-10-10-incident-modes-addressed.md` with
   attacks 1–15 above (its directory is counsel's fence, not audit's).
4. **Engineer seat, one line each, the cheapest reaches in the ledger:** `session touch` refuses an
   unknown word (G: 159, 182, 196 — three of four); `session_id()` refuses to write under no
   `DYAD_SESSION` (R: 145, 205); `cmd_guards` prints its own line for an empty pre-push stdin (E: 212);
   `touch` validates each `-r` token (S: 211); `dwork state -d` refuses text beginning with a date (S: 164).
5. **Engineer seat:** `dwork state <id> done --mandate <id>`, copying the mandate's operative `Y done`
   entry with its heads, so the fence's landing check reads an accreted row's close (M: 207).
6. **Engineer seat:** `plan.base->commit` must be an ancestor of `origin/main` at the writer's push
   (T: 170, 172, 178); the shallow-clone advice at the pre-push path is #315 already.
7. **Engineer seat:** the attendance liveness read uses `holder` against the live sessions or a window
   of its own, not `STALE_AFTER` (E: 209); `trace.check_store` refuses a `- preview:` line on a `done`
   row (Q: 204, ten files today).
8. **Operator:** the program charter's `ceiling 0` against the four plans' mandate scopes (Q: 210) — a
   preference question, not a row, unless the Operator wants the ceiling read by `seats.py`.
9. **Operator's word:** whether the 213 rows are re-derived against 25 modes (the play-book's full
   re-derivation on a new mode), or the delta method stands until the next exercise.
Each of the 23 children #262–#284 stays `backlog`; none is closed, re-opened or archived here.

## Note 2026-10-26 — rows 231–233 against the modes (d-work #463, seat audit-e73be78c)

Not a delta: the `covered through:` watermark stayed at 213, and rows 214–230 were still ungrouped (since grouped by the 2026-10-26 delta below; the next
delta's work, Phase 0's third outcome). This note classifies only the three rows #463 names — 231 (#346, the
close run to read its refusal), 232 (six Done records without their traces, #455–#460) and 233 (#461's
fabricated row 999) — and tests the candidate mode #463's plan names: *a refusal discarded, or a mutating
command run to read its output*.

**The candidate is two modes, not one.** The test throughout: one sentence naming a change that stops every
row at one moment. Row 231 is stopped at the call by a form of `dwork state` that runs every refusal and writes
nothing — the refusal was observed and was the point, and the command wrote because the check passed. Row 232
is stopped at the Done-record commit by a check that the trace the preference requires is in it — the refusal
was produced, at the call, and discarded by the caller's redirect; a read-only form of `dwork trace` would have
been discarded the same way. Different change, different moment: two modes.
- **Row 231 is O, with O widened.** O's definition names git (`git checkout <ref> -- <path>`), but its change
  — "the read would have to be done by a command that writes nothing" — is row 231's exactly; the dyad's own
  CLI is the second instance of it, and for the dyad's verbs the read-only form does not exist yet, which is
  why the row's own cell placed it in Q (no read-only form of the check). Q's change (a register of obligations
  read by a mechanism) would not have stopped it. O: 4 → 5.
- **Row 232 is E primary, Q secondary.** E (row 123's class, 172, 197: a filter the Agent typed hid the
  refusal) is what made the six d-works possible; Q (the trace obligation of `dwork-trace: always` read by no
  guard) is why it lasted across four commits and was caught only by `land` at the seventh. G (the switch's
  arity from memory) started it and is not the mechanism: had the refusal been read, nothing would follow. E:
  11 → 12.
- **Row 233 is W, with W widened.** W is "the suite's environment leaked into the live repository"; row 233 is
  the same mechanism without the suite — scratch work whose target was the current directory reached the live
  checkout. W's fences (`suite_env`, the spawn-site tests) read the suite and cannot reach a hand simulation.
  W: 2 → 3; W's "exit 1 holds" holds for the suite only.

**Where the two halves meet.** Rows 231 and 232 were both the cos, both on the dwork CLI, within a day, and in
both the CLI's refusal was the only channel by which its check could be seen. That is the one thing they share,
and it is a property of the CLI, not a mode: a verb whose checks are visible only as a refusal makes reading
the check cost a write (231) and makes discarding the refusal cost a silent miss (232).

**Proposed exits** (proposed to the program seat with #463's mitigation plan; the Operator's `Y` opened them as `backlog` rows #464–#467 at `6244976`, the program seat's commit — none by this seat):
1. O, row 231 — exit 2: a backlog row (#464) for `dyad dwork state <id> <state> … --check`, every refusal run, nothing
   written, a `would write` line; moment: the call.
2. E/Q, row 232 — exit 2 → 1: a backlog row (#465) for a transaction check — under `dwork-trace: always`, a commit
   that adds a `Y done` entry to row N carries `traces/N.md` or finds it already on the base; the same refusal in
   `dwork state -d 'Y done …'` and `dwork batch` before the first write; moment: the call and every push.
   It makes the discarded refusal harmless rather than forbidding the discard, which no mechanism reads.
3. Row 232's consequence — a backlog row (#466): `land.fast_forward` restores identical landed copies off `main` too
   (the bytes are on `main` whatever branch the caller holds), or prints one line naming the untracked copies
   it left; moment: the land.
4. W, row 233 — exit 2 for the consequence, exit 3 for the mechanism: a backlog row (#467) for the fence's id check —
   the new rows of a range take ids `max(base)+1…` contiguously, so 999 over 463 fails at the commit and the
   push; the lost `cd` itself is conduct (name the target, `git -C <scratch>`), since no mechanism of the
   kernel-only path reads the Agent's shell (as row 177's).

## Delta 2026-10-26 — rows 214–233, grouped against the 25 modes (d-work #472, seat audit-e73be78c)

Phase 0's third outcome. The survey (event `incident-hardening-20261026T215444Z-survey`, committed at `d36b1bd`)
read 233 live rows, latest 2026-10-26, against the watermark of 213. The delta is rows 214–233: rows 214–230,
ungrouped since 2026-10-24, and rows 231–233, which #463's note above had grouped by one view only. The method
is the 2026-10-24 one with two views:
- **View 1** is a subagent forbidden this index, the mode records and the falsification directory. It
  reported the sentinel first, derived 13 modes bottom-up from the `cause` cells and then the `what` cells, and
  applied the one-sentence test.
- **View 2** is this seat, mapping each row to one of A–Y or to none.

Both views assigned all 20 rows with none in two modes. The reconciliation below was checked mechanically: 20
rows, each primary in exactly one mode, counts summing to 20. **No row needs a mode A–Y does not name**: every
one of view 1's 13 modes falls inside one existing mode's definition. So the play-book's trigger for a full
re-derivation (a new row's mechanism named by no mode) does not fire again. The 2026-10-24 question (re-derive
213 rows against 25 modes) stays the Operator's and stays unanswered.

### Rows 214–233 by mode

| mode | delta rows | view 1 | delta | was | now |
|------|------------|--------|-------|-----|-----|
| C | 227 | M9 | 1 | 20 | 21 |
| E | 232 | M9 (secondary) | 1 | 11 | 12 |
| G | 217 | M3 | 1 | 9 | 10 |
| I | 230 | M12 | 1 | 8 | 9 |
| J | 218, 219, 220, 221 | M4 | 4 | 3 | 7 |
| M | 215, 216 | M2 | 2 | 16 | 18 |
| O | 225, 231 | M7 | 2 | 4 | 6 |
| Q | 222, 223, 226 | M5, M6 (223), M8 | 3 | 18 | 21 |
| R | 214, 228 | M1, M10 | 2 | 19 | 21 |
| T | 224, 229 | M6, M11 | 2 | 14 | 16 |
| W | 233 | M13 | 1 | 2 | 3 |
| | | | **20** | | |

"Was" is the 2026-10-24 table's "now". The #463 note's provisional counts (O 5, E 12, W 3) are replaced by this
table. Modes A, B, D, F, H, K, L, N, P, S, U, V, X and Y gain nothing.

### What the reconciliation decided, and against what

1. **Row 225 is O, not P.** The row's own cell says P (unplanned action under momentum). View 1 put it with 231
   in one mode, "a command that writes is run to get a read". O's original definition covers it word for word:
   a git write (`merge --ff-only`) used as a read (to see the current Rules and allocate an id), where `git show
   origin/main:<path>` was the read that writes nothing. P's change (stop and plan the cleanup) is not the
   change that would have stopped it. O's two faces now differ only in whether the non-writing read exists:
   for git it does (225 and the three original rows), and for the dyad's own verbs it does not yet (231; #464
   is the row to build it).
2. **Row 232 keeps E primary over view 1's reading.** View 1 made the arity misremembered from memory primary
   (C/G's family) because it started the incident, and said a reader taking the uncaught act as primary would
   choose Q. The play-book's rule is that the mechanism that *started* a row is primary. But a failure mode is
   by definition "the mechanism that would have to change". The starting act met its fence: `trace.py`
   refused the stray argument correctly and needs no change. What would have to change is the discard (E), and
   the unread obligation (Q, secondary) is the fence #465 is building. The disagreement is recorded rather
   than smoothed over.
3. **Row 223 is Q, not T.** View 1 placed it with 224 (planned from a clone that had not fetched) and flagged
   the fit as weak itself. The cell has two causes, and the one that would have stopped it is the obligation:
   the first agent-zone change after a core release owes a patch bump, and nothing tells the next row so.
   Fetching first would not help if the tag was cut after the plan was written. Stale tags are secondary (T).
4. **Rows 218–221 are one mechanism, J,** with Q secondary, as their cells say and as view 1 found
   independently (M4). Four rows record 29 closes. J gains more in one day than in its first two weeks.
5. **Row 214 is R.** View 1's M1, "a directory is read as a craft", is R's definition of a derived key that
   does not identify: directory existence stands in for being a craft. The check lives in
   `dyad/guards/craft/crafts.py` `crafts()`, not in `dyadlib.craft_dirs()` as view 1 guessed:
   `craft_dirs()` already requires a `VERSION`.
6. **Row 230 is I, not W.** View 1's M12 is "the caller's environment leaked into the suite", which is W's
   direction reversed. The 2026-10-10 definition of I holds: hand runs and the gate gave different verdicts,
   and the input nothing had named was `GIT_CONFIG_PARAMETERS`. The row also replaces the causes rows 124 and
   141 gave for row 123 (view 1 names them as earlier misattributions). Those rows keep their modes. This row
   is their established cause, stated in I's record.
7. **Row 229 is T.** View 1's M11 agrees and finds it conduct only, and this seat finds the same: the presence
   store carries no prompts in flight, and nothing here proposes that it should.

### Phase 2 over the affected modes — read from the code at `d36b1bd`

- **J — fenced.** `rows.refs_shape_problems` (`dyad/guards/agent/rows.py:206`, called from the transaction
  check at `:310`; #439) refuses a `refs` value holding `[ ] ' " ,` at every commit and push. No row on `main`
  carries the list today. 0 recurrence since #439. Exit 1 for the refs shape. J's original three rows are
  untouched by it.
- **R — 228 fenced, 214 not.** `sessions.writer()` keys the writer on the holder (#350, `sessions.py:19–24`),
  which reaches 228. `crafts.crafts()` (`crafts.py:413–416`) still lists every directory under `crafts/`
  ("a VERSION or not"), so 214 reproduces on any checkout that holds a retired craft's ignored caches.
- **I — 230 fenced.** `suite_env()` drops `GIT_CONFIG_PARAMETERS` (`package.py:511–513`; #456, PR #496, merged
  at `4406580`). 0 recurrence since.
- **M — 215 fenced, 216 not.** The departed-craft warning (#423, Rule-11 property 7's sentence, `bundle.py`)
  reaches 215. 216's case, a `VERSION` moving past a row that names an *untagged* version, still fails by
  design (`bundle.py:18–20`: "a row naming an untagged version … fails"). That is the version/zone face of
  rows 60, 61, 115 and 188, with no order to land the two zones.
- **G — unfenced.** `sessions.main` `touch` (`sessions.py:624–630`) skips any word other than `-r` and `-f`
  without refusing, so `touch --help` writes. This is the 2026-10-24 proposal 4, unbuilt, and now its fourth
  row on this verb (159, 182, 196, 217).
- **Q — unfenced.** 222: no guard reads `dyad/templates/self-diagnostic-levels.txt` against the test modules
  (`crafts/syseng/guards/tests.py` holds no `levels`); only `test_levels` in the whole-root suite does. 223:
  the push gate's drift check is the fence that caught it, and nothing reads the obligation at plan time.
  226: `session_id()` (`sessions.py:96–105`) still mints `unnamed-<uuid>` per call. That is the 2026-10-24
  proposal 4 for 145 and 205, unbuilt, and now 226.
- **T — unfenced.** Rule-3's session-start clause reads the ledger and names no fetch or base. Plan #348 names
  the fence and nothing built it (224). 229 is conduct.
- **O — 231 has #464 `backlog` (R1). 225 is conduct:** the non-writing read exists.
- **C (227)** is conduct, as C's twenty earlier rows are. **E/Q (232)** has #465 `planned` (R2 with
  `--latest=false`). **W (233)** has #467 `backlog` (R4) for the consequence, and the mechanism is exit 3.

### Falsification — is each affected mode still addressed as its record says?

This is written here and not in `agent-corpus/falsification/`, by the audit charter (plan #472 attack 5), as on
2026-10-24. The amendment of `agent-corpus/falsification/2026-10-10-incident-modes-addressed.md` is proposed
to counsel. Rule-9's easy-agreement trigger fired on J and I, where I agreed on first reading; both were
attacked by reading the fence's code and its reach today.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | J is fenced by #439 | **survives, scoped.** `refs_shape_problems` is in the transaction check and no row holds the list. But it fences one field's shape, not the mechanism (a name rebound by an added loop and written later); a rebind of `disposed` or `title` would pass | exit 1 for refs; the mechanism stays open, with no cheap fence |
| 2 | I's GIT_CONFIG_PARAMETERS sub-shape is fenced by #456 | **confirmed.** `suite_env` drops it, and #456's behavioural test sits beside #206's | exit 1 for the sub-shape; I stays open for the others |
| 3 | R is addressed (the 2026-10-24 record: open) | **confirmed as open.** 228 fenced by #350; 214 is a new key in a new store (the craft tree) with a one-line fix | open |
| 4 | M's version/zone face is addressed by #423 and #230 | **refuted as a whole.** Each sentence admitted one more transitional state, and 216 is the next one (an untagged row). The face recurs one state at a time | open; one more sentence plus a warning in `bundle.py` proposed (P3) |
| 5 | G is addressed (exit 2 named, #268) | **refuted again.** A fourth row on `session touch`, and #268 still `backlog` | the one-line refusal is the cheapest fence in the ledger, proposed as its own row (P1) |
| 6 | Q is addressed | **refuted.** Three more rows, each an obligation only the full gate or nothing reads. 226's fence was proposed on 2026-10-24 and not built | open; P2, P6 |
| 7 | T is addressed | **confirmed as open.** 224's fence is named in plan #348 and unbuilt; 229 is conduct | open; P4 |
| 8 | O is addressed now that #464 exists | **survives, scoped.** #464 reaches 231 and the dyad's own verbs; 225 had its non-writing read and did not use it, which no mechanism reads | the dyad-verb face reaches exit 2; the git face stays conduct |
| 9 | C, E, W are addressed as #463's note said | **confirmed.** One row each, already placed and owned (#465, #467) | as proposed |
| 10 | the 25 modes still cover the ledger | **survives.** View 1's 13 modes each fall inside one, and no row is left | 25; no re-derivation trigger |
| 11 | this exercise hardens rather than measures (2026-10-24 attack 15) | **survives, scoped.** Since 2026-10-24, three fences reached delta rows (#439, #350, #456) and #464–#467 were opened within the hour of their proposal. But every 2026-10-24 engineer proposal (its items 4–7) is still unbuilt, and two of them reach rows of this delta (217, 226) | the recurrence of unbuilt proposals is the finding; P1 and P2 are those proposals again, now with a recurrence each |

### Phase 4 — affected modes after the delta

| mode | rows | status 2026-10-24 | re-verified 2026-10-26 | status |
|------|------|-------------------|------------------------|--------|
| C | 21 | open | +1, conduct | open |
| E | 12 | open | +1; #465 planned | open; exit 2 → 1 on #465 |
| G | 10 | exit 2 named, unbuilt | +1 on `session touch` | exit 2 named, unbuilt |
| I | 9 | open; exit 2 reachable | +1, fenced by #456 | open; exit 1 for one sub-shape |
| J | 7 | exit 2 named, unbuilt | +4, refs shape fenced by #439 | **exit 1 for the refs shape**; mechanism open |
| M | 18 | split | +2; 215 fenced by #423, 216 not | split as before |
| O | 6 | exit 2 named, unbuilt | +2; #464 backlog | exit 2 named, unbuilt |
| Q | 21 | open | +3 | open |
| R | 21 | open | +2; 228 fenced by #350 | open |
| T | 16 | open | +2 | open |
| W | 3 | exit 1 holds | +1 outside the suite; #467 backlog | exit 1 for the suite; open outside it |

### Proposed, opened by nobody here (the audit charter: proposes rows, opens none)

The Operator's `Y` opened P1–P6 as `backlog` rows #479–#484 at `bdbf324`, the program seat's commit; none by this seat. These are ranked by rows reached per fence. Each states its mode, its rows, its moment and its owner. P1 and
P2 are the 2026-10-24 proposal 4 again, unbuilt and now recurred.
1. **P1, G** (#479) — `session touch` refuses any word other than `-r <id>` and `-f <path>`, and `--help` prints usage
   and exits, before the first write. Reaches 159, 182, 196, 217 (four rows, one verb). Moment: the call.
   Owner: engineer.
2. **P2, Q/R** (#480) — `session_id()` refuses to write when `DYAD_SESSION` is unset, instead of minting `unnamed-*`.
   Reaches 145, 205, 226. Moment: the call. Owner: engineer.
3. **P3, M** (#481) — a Rule-11 property 7 sentence and a `bundle.py` warning for a `VERSION` ahead of a row that names
   an untagged version, until that row's release or its infra-zone PR, as #230 and #423 did for their states.
   Reaches 216 and the face's next state. Moment: the push. Owners: counsel (the sentence and its amendment),
   then engineer.
4. **P4, T** (#482) — the session-start report states its base and its distance from `origin/main` (`dyad session
   touch` prints `behind origin/main by <n>` after a fetch). Reaches 224.
   Moment: session start. Owner: engineer.
5. **P5, R** (#483) — `crafts.crafts()` counts only a directory holding a tracked file, as `craft_dirs()` already
   requires a `VERSION`. Reaches 214. Moment: every check. Owner: engineer.
6. **P6, Q** (#484) — `syseng/tests` also checks that every test module has a line in
   `dyad/templates/self-diagnostic-levels.txt`, so `check --guards` and a targeted run see it. Reaches 222.
   Moment: the push and the call. Owner: engineer (craft zone).
7. **Counsel** — amend `agent-corpus/falsification/2026-10-10-incident-modes-addressed.md` with attacks 1–11
   above.

Rows #262–#284 and #464–#467 are neither closed, re-opened nor archived here.

## Note 2026-10-27 — rows 234–239 (d-work #487, seat audit-e73be78c)

Not a delta. The watermark stays at 233, and the next delta grades these five rows with two views, as it graded
#463's. One view, this seat's, placed each row, and each row carries its mode in its own cells:

| row | d-work | mode | secondary |
|-----|--------|------|-----------|
| 234 | #477 | I (the tagless sub-shape; its worst face: a skip hid a FAIL) | — |
| 235 | #476 | A (third face, row 198's: a push to a branch a Done names) | C |
| 236 | #474 | I (git's version and its auto-maintenance, the unnamed input) | — |
| 237 | #486 | S (a counter-prompt form typed from memory, not seeded from `merge-disposition`) | M, unverified |
| 238 | #475 (PR #518) | C (CI state stated, not read) | — |
| 239 | #487 | F (a PR number in the d-work column; caught by Rule-20's resolver, the fence holding) | — |

Two of these are the second instance of a face within a week. Row 235 repeats row 198, and the 2026-10-24 delta
called that face conduct "unless branch protection". Row 234 repeats the tagless skip, which the delta of
2026-10-24 placed in I. Both now have a mechanism within reach:
- **F1 (A, rows 198 and 235).** The pre-push gate already reads the refs being pushed (Rule-14 property 3) and
  the ledger. It can refuse a push whose remote old sha is a head that an operative `Y done` names on a row not
  yet `done`. The moment is the push, before the commit leaves the clone. It corrects the 2026-10-24 attack 1's
  survivor: the face is mechanizable without branch protection.
- **F2 (S, row 237).** `rows.py` can warn on a `Y merge` disposition while `merge-disposition` is `with-done`.
  It exempts the case the 2026-10-25 entries show (#432, #433, #436, #441 are each noted "its own question per
  #427", the charter and preference PRs Rule-2 has the Operator dispose as their own PR). The moment is the
  ledger commit.
- **Row 234** has its fence already: #474 (`check --evidence` refuses a shallow or tagless clone, and the pre-push
  path names the skip), so no new candidate is needed.

F1 and F2 go to the program seat as their own questions. Nothing is opened here.
