# Play-book: audit (core craft, `dyad-operator`; #223)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the agent follows for
a recurring decision; its steps are a run-book. This one is the **standing audit**: the topic-free,
whole-system pass that is run again and again, and that the per-change gate leaves to audit — #220's
survivor, "unit regression of everything else is an audit job", with its cadence an open parameter.
An audit (vocabulary) is an agent-authored review that elevates gaps for operator disposition; until
now nothing said what the standing one reads, in what order, what it writes, or when it writes nothing.
Steps: `dyad/runbooks/audit.md` — `report`, `hooks`, `host`, `record` — run through `dyad runbook run audit <step>`,
the core runner, so each step leaves an event. Beside it, since #381, the **self-diagnostic** (below): the gated,
budgeted four-level run of the countersign model, whose steps are `dyad/runbooks/self-diagnostic.md`; the two share
one observation, the automaton sweep's report on `main`, and nothing else.

**What the automaton runs and what is left here (#619).** Every coded check the audit once ran by its own steps is a
part of the **automaton sweep** (`dyad automaton sweep`, Rule-14 property 3): the suite on `main` in every root, every
whole-store guard, drift outside the repo, and, as its part `sweep_audit`, the audit's own checks — the watermark, the
registry and a guard that left it, the Rules edited since the newest Rule-5 sweep record, incident sizing and the
hardening watermark, the hardening index's fence rows and fences, the newest record's two lines, the levels file —
each classed by the check-trigger criterion, so it runs after every landed merge and reaches the home once, as a new
finding, between audits. The audit runs the same sweep on `main` with no `--row` as its first act, which posts
nothing and prints the **report**: every check line, every finding as `standing` or `new`, the `reading:` lines, the
stall block of the home's read, and two digests. What remains in the phases below is marked: **kept, inference** —
reading the report and judging each line, which no code decides — or, once, **kept, local** — a fact of the
auditor's own checkout the hosted sweep cannot see. No phase re-runs a check the report carries.

Since #433 the standing audit is a composite whose phases are run by their domain owners, and the audit unit keeps
the incident ledger. Since #619 the coded half of every phase is the automaton's, whose code engineer owns, and every
phase's owner owns the judgement of its own lines in the report: Phase 0 and Phase 4 by whichever unit runs the
exercise; Phase 1 by engineer; Phase 2 by audit (hardening's `verify`, generalized to every shipped fence); Phase 3
split by item; Phase 3b by audit. The self-diagnostic's L1–L2 are engineer's and its L3–L4 counsel's: one run, its
gate and budget unchanged.

It is not a topic audit. A review the operator asks for on one subject (a performance profile, a sweep
of one craft, the subset CI should run) stays an operator prompt with its own plan; it may borrow the
Conduct below and nothing else here.

## Trigger
An operator prompt asking for the audit. No Rule requires it: contrast `incident-hardening.md`, which
Rule-3's Incidents clause reads, and like `ds-report-incidents.md` this one is read on a prompt. The play-book
runs inside the d-work the prompt opened and is planned there (Rule-15 phase 1) before any record is
written; a d-work of another kind that notices the gate below would open states it as a finding and opens
nothing, since a d-work opens on an operator prompt or disposition and never on the agent's own finding
(Rule-3, Scope).

The cadence is #220's open parameter and is not set here. A clock is not the gate: it would add a second,
weaker one carrying its own failure mode — a changed system ignored because the calendar said no, an
unchanged one re-read because it said yes. Phase 0's watermark decides whether there is anything to read, and
between audits the automaton sweep tells the home each new finding after the merge that made it (#619).

## Phase 0 — Survey (the idempotence gate)
The first act is the step `report`: `dyad automaton sweep` on `main`, checked out, with no `--row` (#619). It
lands nothing and posts nothing; the runner records its event under the auditing party's role. The full text is
stored at `<git common dir>/dyad-sweep/<report-sha256>.txt`, never tracked, as the evidence block is stored.

The record of phase 4 carries two lines. The first is the watermark:

    **Audited:** tree <hash> · python <v> · git <v> · covered through <sha>, <YYYY-MM-DD>

`tree` is the digest of the **code tree** — the tree with `<instance>/d-work/` and `<runbooks>/events/` pruned, as
the evidence block's `code=` prunes it (Rule-14 property 3) — **minus the dated audit records**
(`<instance>/audits/<date>-*.md`; `INCIDENTS.md` is not dated and stays in). The records are the audit's own
output: with them in the hash, the record this audit commits would change the tree, and the next audit could
never see an unchanged one. The ledger and the event store are out for the same reason in kind: their own checks
run in the stores sweep after each push that changes them, and no phase here reads them by its own code, so ledger
churn alone does not reopen this audit's reading (#619, Q1). `python` is the interpreter that ran the report and
`git` its version. The report's `reading: audit watermark` line derives the live line and compares it to the one of
the newest record; the gate is read from that line, never computed again. Three outcomes, and only the last two
derive anything new:
- **Same tree, same interpreter, same git** — **unchanged**: phases 1 and 3 are a no-op: nothing new is there to
  find, and a deterministic suite on an unchanged tree says what it said. The audit prints both lines, writes no
  file and says "unchanged since <record>" (`0 changes`, the shape `crafts/syseng/rules/idempotence.md` property 1
  sets for the install). **Phase 2 still runs**, below.
- **Any of the three differs** — the **full exercise**.
- **No record carries the line** — the **first exercise**, full derivation. The first audit after #619 reads
  `changed` once, since its tree became the code tree.

The watermark is compared, never believed: the live line is derived by the report, so a hand-edited record
is caught by the comparison.

## Phase 1 — Regression (in the report)
Owner: engineer (#433).
The whole suite, every root, **observed** on `main` in the report: the sweep runs it in the hosting's environment
after each merge and in the auditor's own run here, and never reads the suite memo (Rule-12 property 2), so the
result is a run and not a recollection. No step re-runs it, and `dyad check --evidence` is not run here: the
evidence block remains the merge evidence of each PR (Rule-14 property 3), and the report's suite is the same run on
the head every merge landed on. The record cites the report by its `checks-sha256` and `report-sha256` and pastes
its check lines verbatim.

**Kept, inference:** judging a red line — a regression, a check the merge evidence should have caught, or one the
environment changed (the report's interpreter and git are the runner's) — and stating which.

This is the job #220 assigned to audit. It assumes #220's adoption (a): the merge evidence stays full, so
this phase re-observes on `main` what every merge observed at its own head. Under adoption (b), where
the evidence narrows, it is the only full run left. The play-book is the same under both; its weight is not.
Seconds are one machine's (#204 section 0): the record states the interpreter and, beside any absolute, a
ratio.

## Phase 2 — Fences (ungated)
Owner: audit (#433): this is incident hardening's `verify` applied to every shipped fence.
A shipped fence can rot with no commit to the tree, so this phase runs on every invocation, the unchanged
tree's included (the reason `incident-hardening.md` gives its own phase 4). It reads, in the report:
- **the guard registry as installed** — the `reading: audit fences` line, its line count and digest compared to
  the `**Fences:**` line of the newest record:

      **Fences:** registry <n> lines, sha256 <first 16 hex> · hooksPath <value>

  A guard that left the registry is a **finding** — the report names it, comparing the registry to the newest core
  release tag's guards, and a craft guard to its craft's own newest tag (#619); a registry that grew is
  **reported, not judged**;
- **the mode of every file git or the entrypoint runs by path** — `dyad/hooks/*` and `dyad/bin/*` must be `100755`
  (#24: a lost exec bit left a hook inert and the push gate vacuous) — the `syseng/naming` guard's own line in the
  report's checks, bundled with the core, so a fence that cannot execute fails the report.

**Kept, local:** the step `hooks` reads `core.hooksPath` in the auditor's own checkout — a repo whose hooks are not
enabled has no blocking Rule-1 enforcement (Rule-1) — and the auditor writes its value into the `**Fences:**` line.
The hosted sweep's checkout is not the one an agent pushes from, so the report cannot carry it.
**Kept, inference:** judging each line. A fence that cannot execute is a finding whatever the registry says.

## Phase 3 — Drift (detect only)
Owners, by item (#433): each bullet names its own.
What moved since the newest record, read and never repaired:
- **Rules edited since the last Rule-5 sweep.** A sweep is inference (Rule-5, Enforcement). A Rule-5 sweep record
  is `<instance>/audits/<date>-rule-sweep.md`, and only a record so named is one: the report's `audit drift` finding
  compares the newest commit to `dyad/rules/` with the commit that added the newest such record, or says `none`
  (#619). **Kept, inference:** the audit states the staleness and does not sweep. (counsel)
- **Rows with no activity** — the home's read (`dyad board resume`), its `untouched`, `quiet` and `unplanned` lines,
  carried in the report's stall block; the `backlog` count. (program)
- **Presence files** past the stale window — the report's `reading: presence` line (Rule-16): reported, never
  guards. (operate)
- **Unmerged remote branches** — the report's `reading: branches` line: **kept, inference**, the pruning question of
  #43, asked as a list. (program)
- **Host documents older than the running kernel** (the frame's convention) — **kept, inference**: read only on the
  host that keeps them, through the step `host`, which lists them. Anywhere else the record says "unobserved" and
  names the host path: an audit does not read a document about a machine it is not on and call it verified
  (Rule-8). (operate)

## Phase 3b — Incidents
Owner: audit (#433).
The incident log is read here and worked by `incident-hardening.md`: one owner per concern (Rule-5), so this
phase ingests, sizes and surfaces, and never groups. The report carries:
- **the ingestion**, through the log's one parser, `dyad/scripts/incidents.py` — `parse`, `check_log` — and not by
  counting lines: the `reading: incidents` line (row count, rows per month, the d-works that carry two or more rows),
  and the log's shape among the checks;
- **hardening's survey**, the same function the hardening run-book's `survey` calls: the `reading: hardening` line,
  the live row count against the watermark of the newest index audit, and a `hardening` finding when rows lie past
  it. The **delta** is the rows past that watermark.
**Kept, inference:**
- **States the gap**: the delta, and whether `incident-hardening` has run since it was written. A delta with no
  hardening run behind it is the audit's finding, and the record lists "run `incident-hardening` on the delta"
  as a proposed row, never opened.
- **Does not classify.** Assigning rows to failure modes is inference that hardening's phase 1 re-derives each
  time, "never read off the previous index"; writing it here would be done twice and discarded once, and would
  open a child row per mode, which an audit cannot. Mode records, the mitigation inventory and the child
  d-works are hardening's.

## Phase 4 — Record
One record, `<instance>/audits/<date>-audit.md`, written only when phase 0 found something to read. It opens
with the title, the two watermark lines above, and `Disposition:` by reference to the d-work (Rule-2: the
done-`Y` of the d-work that ran the audit disposes it); then, in order: the **report** — its mechanical section, the
check lines, findings standing and new, readings and stall block verbatim, cited by `checks-sha256` and
`report-sha256` — then fences, drift, incidents, **findings**, **proposed rows**, **not observed**.

**Kept, inference:** each finding is a claim and is falsified before it is written (Rule-9, trigger "an audit
surfaces a claim"): what was tried against it, and its result — confirmed, refuted, or survives scoped — in the
d-work's falsification record. A claim a command's observed line does not carry is marked inference. A reference the
record states resolves cites the guard's line, or says the kind is unresolvable (Rule-20, trigger). **Proposed
rows** are candidate d-works with the evidence each would carry, in Rule-3's intake shape; a candidate is a
row-shaped entry and never a paragraph, because a candidate with no row is the failure `incident-hardening.md`
exists to prevent. **Not observed** says what the audit could not read and why. The `record` step reads the new
record's two watermark lines back through the report's own check of the newest record: that record is a new file
the report could not see, so this is no re-run.

## Conduct
The audit detects and sizes; it disposes nothing (frame: detect, don't dispose; Rule-2: the agent proposes). It
changes no Rule and no code, opens no row and closes no mode and no row: the operator's prompt or disposition
opens a row, and a finding is "proposed, not opened" until then. Every run-book command is read-only, and the report
posts nothing. The first exercise on a system is a baseline for the next watermark, and a record of what ran, not a
verdict on this play-book: the session that authored it and the session that first ran it were the same
(no-self-ratify, Rule-2; the operator's done-`Y` disposes both).

## The self-diagnostic — four levels, coded checks before prose claims
Authored for countersign-system (its d-work #3) in dyad-system #308 as the countersign craft's
`rules/self-diagnostic.md`, carried here since #381 (the consolidation, #369 C3) with its record
`dyad/falsification/countersign-self-diagnostic.md` (C1–C6, D1–D25). It **describes** a model — what a system's
self-diagnostic is made of, in what order, what passes and what a run leaves behind — and binds nothing by itself:
what becomes of a finding is what the Rules already say (§5). Where it and the standing audit above overlap is one
place only: both read the automaton sweep's report on `main` (D15, #619) — the audit's Phase 1 its suite, L1 and L2
its failing tests and check lines, L3 its invariant reading — and neither re-runs what the report carries. Otherwise they
differ in kind — the audit is the topic-free pass with a watermark and no attack table; the diagnostic is a gated
2×2 grid with a budget of inference per run — and a diagnostic record's dated name falls outside the audit's
watermark, so neither perturbs the other.

### Intent
Describe one self-diagnostic any Countersign system can run on itself: four levels, built from two kinds of check
at two scopes, run one at a time, so that cheap mechanical proof comes before inference and no inference is spent
reading a system whose code already fails; every command read-only, and the runner's events and one record a
run's only writes (§8).

### 1. Two kinds of check (C1–C6)
Every check a system makes of itself is of one of two kinds, and a self-diagnostic needs both (C4):
- a **coded check** — a test, a guard or an invariant: mechanical, re-runnable, cheap; on the same tree it says
  the same thing every run;
- a **prose claim** — a sentence the system asserts about itself, checked by reading it **against a written
  attack**: the attack names what would have to be found for the claim to be false, and the reading looks for
  exactly that. A claim with no attack is not a check (C2).

The kind is *how* a thing is checked, never *what* is checked (C3): a coded check may examine prose —
dyad-system's `rules.py` counts a Rule's block, `vocabulary.py` its terms, `references.py` its references — and a
prose claim may examine code, as L3's contract coverage does. "Coded rule" is not used: in a dyad corpus a Rule is
prose (C1). A prose claim whose attack has failed on successive runs, by a reading that could be written down, is
a candidate for code (C5): the record marks it (§7, `codify?`), in the shape of the model's codify edge (a
practice done by hand becomes a definition a non-inferring party runs) and of dyad-system's Rule-13 property 1
(recurrence proposes code).

### 2. The grid: four diagnostic levels
The two kinds of check at two scopes are the four levels (C6):

| | coded check | prose claim, with its attack |
|---|---|---|
| **unit** — one module | **L1**: unit tests | **L3**: each unit's contract is covered by its invariants and tests |
| **system** — modules together, the live tree | **L2**: integration tests, the guards on the live tree, read from the automaton sweep's report | **L4**: a fixed list of system claims, and the instance's own |

Order: coded before prose, and unit before system within each kind — L1, L2, L3, L4, the order the countersign-system
prompt names. Each level gates the next (§3).

Owners (#433): the coded-check levels L1 and L2 are engineer's, the prose-claim levels L3 and L4 counsel's; one run,
in the order above, so the gate and the budget stay one.

#### L1 — unit × coded check
- **Verifies:** each unit's own tests — the test modules the levels file (§6) classifies `unit`.
- **How:** the step `unit` runs the report once — `dyad automaton sweep` on `main` with no `--row`, whose suite runs
  every root, observed and never from a memo (dyad-system Rule-12 property 2, Rule-14 property 3) — and classes its
  failing tests by the levels file's `unit` list (`levels.py list unit`). No module is run a second time: the report
  names each failing test, and the levels file says which level it belongs to (#619). The step's event carries the
  report's two digests.
- **Passes:** no failing test in a `unit` module.

#### L2 — system × coded check
- **Verifies:** modules together — the test modules classified `integration` (scratch repos, git, installs, the
  runner spawned); the guards on the live tree, among them the coded checks of prose (Rule blocks, vocabulary,
  references, provenance counts, zones, the manifest) — every check the automaton sweep's report on `main` carries.
- **How:** the step `integration` reads the report L1 stored, never a second run: its failing tests in the modules
  the levels file classes `integration`, and every failing check line — the runner's invariant pass, every check and
  every guard on the kernel alone, which the sweep runs on `main` (dyad-system Rule-14 property 3). The record keeps
  the report's `checks-sha256`, the digest of the tree's own check lines in the order they printed, so anyone can
  re-run the sweep on the same head of `main` and compare (D4). It is not the `report-sha256`, which names the stored
  text and never repeats: the report's stall lines read time, its standing marks read the inbox, and its drift reads
  the world (#619). The run's own uncommitted events cannot reach the digest, since the sweep reads the committed
  tree of `main` (D21).
- **On `main`:** the head diagnosed is the head of `main`, checked out, and the sweep reads `main` whatever is checked
  out. The `health` step requires HEAD to equal `origin/main`, so the record's head is the one the report read; its
  pass criterion fails off `main` (D24).
- **Passes:** no failing test in an `integration` module, and no failing check line in the report.

#### L3 — unit × prose claim
- **Verifies:** that each unit's invariants and tests cover the contract it states. A **unit** here is a module
  that declares an `INVARIANTS` list — a module carrying a data model (syseng `invariants.md` property 1).
- **How:** the coded half first — the runner's invariant pass, one `[invariant]` line per module, which every check
  run prints before any check; the step `invariants` reads the report's invariant reading (`invariants <i> ok, <f>
  FAIL`), so a report that holds none still fails (#619). Then the
  prose half over K units in rotation (§4): for each, the claim *"this unit's invariants and tests cover its
  stated contract"* — its contract being its module docstring and the rule that owns it — is read against the
  attack *"name a contract clause whose breaking no invariant and no test would catch"*.
- **Passes:** every `[invariant]` line `ok`, and the attack lands on no sampled unit. A landed attack is a finding:
  the uncovered clause, and the invariant or test that would cover it (§5).
- **codify?:** a clause an invariant or a test already covers is code and needs nothing; a clause the attack could
  decide only by reading, read so on two successive runs that sampled its unit, is a codify candidate.

#### L4 — system × prose claim
- **Verifies:** a fixed list of claims about the whole system, each with its attack — the eight imperatives of this
  craft's interaction model (`countersign-model.md` Part II §3, I1–I8), then three of the system's own — and the claims an
  instance adds. Each claim's coded half, where it has one, already ran at L2 or runs in the step that prints the
  sample; L4 reads what that half cannot decide.

| # | claim | attack | coded half |
|---|---|---|---|
| S1 | only a human countersigns (`countersign-model.md` I1) | among P sampled acts, find a countersignature whose signer is not the human party, or a disposition with no human's words behind it | the projector's `check` (I1), where the countersign projector runs: its live test at L2 and the `acts` step |
| S2 | one question per reply, its last line (I2) | in the session that runs the diagnostic, find a reply asking more than one question, or asking one anywhere but its last line | none: a question lives in the conversation, not in a store (`countersign-model.md` Part II §3) |
| S3 | falsified before proposed (I3) | among P sampled rows, find one carrying a plan whose plan file holds no falsification section and no pointer to a falsification record | none: the record's existence is the evidence (`countersign-model.md` Part II §3) |
| S4 | detect, don't dispose (I4) | in the session that runs the diagnostic, find a finding repaired rather than proposed, or a change to the tree since the head diagnosed besides the run's two writes (§8) | the line naming what the checkout holds besides the event store, printed before the report |
| S5 | the ledger and the provenance agree (I5) | for P sampled rows, find a `disposed` entry whose provenance text does not carry that answer | dyad-system's `agent/provenance` (the count, Rule-7 property 5) |
| S6 | no act is self-initiated (I6) | among the projector's I6 warnings and P sampled acts, find an act opened on a non-human party's own finding | the projector's `interaction`, warnings only |
| S7 | every act carries its mode and a countersignature reference (I7) | among P sampled acts, find one with no mode, a mode its processor contradicts, or an answered question no countersignature resolves to | the projector's schema validation and `check` (I7): a red one is the finding, and the reading confirms the sample |
| S8 | silence is not consent (I8) | among P sampled rows, find a state past `open` or a merge for which the row's `disposed` column records no answer: an act taken on silence | the projector derives no countersignature from an absent answer (`countersign-model.md` I8); dyad-system's plan gate (`agent/prs`) refuses a branch whose cited row carries no `Y plan` |
| S9 | the host record matches the host | find a kernel component whose observed version or presence differs from the system's host record under its host path, or a zone or profile the observed host contradicts | the manifest guard (the record's form, never its truth) |
| S10 | the Rules are coherent | for P Rule pairs in rotation, find a trigger on which the two instruct differently | none: coherence is inference (dyad-system Rule-5) |
| S11 | the frame loads | find the frame's sentinel absent from the start report of the session that runs the diagnostic | none |

- **Where each is read:** three imperatives live in conversation, not in a store, and a dyad corpus keeps the human
  party's words and no other's (dyad-system Rule-7 property 4); so S2 and S4 are read over the one conversation a run
  can see — the session that runs it — whole, as S11 is, and not over the system's history (D23). I8 leaves a trace
  in the ledger, a state no recorded answer allows, which S8 reads over the sampled rows. I7 and I1 are decided by
  their coded halves; their readings only confirm the sample.

- **The instance block:** a system adds its own claims in the same three columns, in its own run-book — in
  countersign-system its hand-over criteria H1–H5, each with the claim *"its status is as recorded"* and the attack
  *"find an H whose stated status the corpus contradicts"*.
- **Passes:** no attack lands. Each landed attack is a finding (§5).
- **codify?:** as at L3 — a claim held on two successive runs by a reading that could be written down is a codify
  candidate; a claim its coded half already decides needs nothing.

### 3. The gate
L1 always runs; level N runs only when level N−1 passed. A level that does not pass ends the run: every later level
is recorded `not run (gate)`, and nothing is repaired inside the diagnostic — a repair is its own body of work in
the system's own process (§5). The reason is cost and confidence: a reading done over code that already fails reads
a system other than the one on disk, and the cheap mechanical proof is what says so. The invariant pass is coded
but sits at the head of L3, not in L2: it is the unit-scope fact L3's reading rests on, and placing it there costs
nothing, since the report L2 read has already printed it — and a false invariant has already turned that report's
checks red, so at L3 the coded half re-reads what L2 decided (D2). A landed L3 attack stops L4 for the same reason:
L4's claims rest on the units' contracts, and reading the system over a contract already known to be uncovered
spends inference on a model known to be incomplete. A run may also be asked to end after a given level (the
command's argument, §8): every level after it is recorded `not run (last level <n>)`, which is no finding, and a
run that ends at L2 spends no inference.

### 4. Budget and rotation
Inference is bounded per run: **K** units at L3 (default 4) and **P** samples at L4 (default 3: P acts or rows for
S1, S3 and S5–S8, P Rule pairs for S10; S2, S4, S9 and S11 are read whole). The values a run used are in its
record. A **rotation cursor** makes successive runs cover everything (D5): each record ends with where the next run
starts — the next K
units in sorted module-path order, the next P rows by id, the next P Rule pairs in sorted pair order, each wrapping
at its end — and a run reads the newest previous record's cursor before it samples; with none, every order starts
at its first item. With n units, every unit is read once in ⌈n/K⌉ runs that reach L3. The bound is dyad-system
#143's concern — inference budget first, more tokens accepted only for more reliability — made explicit.

### 5. Findings, and where each goes
A finding is what a level surfaced: a coded check that failed (L1, L2, L3's invariant pass), an attack that landed
(L3, L4), or a codify candidate. The diagnostic decides none of them, and no finding is a verdict: L3 and L4 detect,
they do not prove (D1). In the countersign model the record is a **countersign report**
(`countersign-model.md` Part II §1): evidence that never asks. What it surfaces unsigned is an **escalation**, which becomes a
countersign proposal in explicit mode. In a dyad system the core's Rules already say what each kind becomes:
- a failed coded check — a test, a guard or an invariant that fails, a defect — is an incident (Rule-3,
  Incidents: "a failed check"; for an invariant, Rule-12 property 1 too), reported as observed, never assumed
  (Rule-3's completion evidence), its repair a plan of its own (Rule-3, Plan);
- a landed L3 attack — a contract clause no invariant or test covers — and a landed L4 attack — a system claim
  shown false — are proposals (Rule-10), each adopted, if at all, as a plan of its own (Rule-3, Plan), or held as
  a `backlog` row by the disposition that opens one (Rule-3, Ledger);
- an outcome the diagnostic's own plan did not name is an incident (Rule-3, Incidents);
- a codify candidate is an inference task met a second time, which proposes code (Rule-13 property 1).

### 6. The levels file
Which test module is L1's and which L2's is instance data: the system that runs the diagnostic owns its installed
inventory, and a list in the core would couple the core's suite to every craft's tests (D8). The file is
`<host>/self-diagnostic-levels.txt`, `<host>` the host path (`dyadlib.host_path`; dyad-system preference
`host-path`, default `workstation-corpus`; countersign-system `infrastructure`). It is seeded from
`dyad/templates/self-diagnostic-levels.txt`, by hand — the
run-book's header gives the command; an install never copies it (Rule-11 property 2).
- **Form:** one entry per line, `<level> <path>` — `level` is `unit` or `integration`, `path` a repo-relative test
  module (`dyad/tests/test_dyadlib_rows.py`, `crafts/sysadmin/tests/guards/test_runbooks.py`); `#` comments and blank
  lines are allowed.
- **Inventory:** a system's test modules are every `test_*.py` under the runner's test roots — `dyad/tests/` and
  every `crafts/<craft>/tests/` present (`package.test_suites()`). The roots are the runner's; within them that set
  is what `unittest discover` runs only where the syseng craft's naming guard keeps the two equal — no other
  `test*.py`, no test module outside a package. Where that craft is not installed, a helper the suite runs may go
  unlisted and a module it never runs must still be placed (the levels script).
- **Granularity: the module** (D16). A module that mixes kinds is `integration` when any one of its tests builds a
  scratch repo, runs git, installs, or spawns the runner; otherwise it is `unit`.
- **Check:** `dyad/scripts/levels.py`, a script and not a guard (D20), checks that the file is complete
  and names what exists, never that it is right. It fails on a test module present but unclassified, an entry
  whose path names no test module of the tree, a malformed line, or a path listed twice. It runs where the
  classification is used: the automaton sweep's `sweep_audit` part prints its line as a `levels` finding, after each
  landed merge and in the report every run reads (#619), and the `unit` and `integration` steps read the file
  through its `list`, which refuses a file that fails. No runner discovers a script, so it runs on no push: a
  module added without its line is found at the next merge's sweep, or at the next run's report, before any level is
  judged. It skips with one line
  when the file is absent, so a system that runs no diagnostic — dyad-system, which authors the model — is
  unaffected by it (D17, D25). The file's paths are references the
  script resolves itself, outside dyad-system's reference register (D19). Whether a module is rightly `unit` is
  read.

### 7. The record
One of a run's two writes (§8): `<instance>/audits/<YYYY-MM-DD>-self-diagnostic.md` (`DYAD_INSTANCE`, default
`agent-corpus`), where the core keeps audits, in zone `agent`. It holds:
- the head diagnosed, and the K and P the run used;
- per level, its result — `pass`, `fail`, `not run (gate)` or `not run (last level <n>)` (§3) — its evidence (the
  observed output lines of its commands; at L2 the report's `checks-sha256` line) and its findings;
- for L3 and L4, a table `claim | attack | result | codify?`, one row per sampled unit or claim sample;
- the rotation cursor (§4): where the next run's K units, P rows and P Rule pairs begin.

The run-book fixes the lines its steps read back: `**Diagnosed:** head <sha> · K <k> · P <p> · checks-sha256
<value>` (it read `evidence-sha256` before #619, which a record written then keeps), one `**Result:**` line under each level's heading, and `**Cursor:** units=<path> rows=<id> pairs=<a>-<b>`,
each value the first item the next run reads, at or after it and wrapping, so an item added or removed since does
not break the rotation. The name is one per day (UTC): a later run on a day that already has a record rewrites
that day's record, after reading its cursor, and the earlier text survives in the system's history once the unit
of work that wrote it has committed it.

The record is evidence and asks nothing (§5). Its dated name falls under the core's `<instance>/audits/<date>-*.md`,
which the standing audit above leaves out of its watermark (Phase 0), so a
diagnostic record never makes an unchanged tree look changed (D15).

### 8. The run-book and the command
The steps are the core run-book `dyad/runbooks/self-diagnostic.md`, in the sysadmin craft's run-book form
(`crafts/sysadmin/rules/server-instances.md`) with its own section set, `# sections: Level 1, Level 2, Level 3,
Level 4`: a run-book that declares its sections is checked against them, as every core run-book is, and is not a
server's (that rule's property 2). Its steps run through the core runner, `dyad runbook run self-diagnostic
<step>`, which records one event per step. A system that wants its own L4 claims in a run-book copies the core
one under its host path (`<host>/runbooks/self-diagnostic.md`, the same name, so `dyad runbook run` finds the
instance one) and adds them there; otherwise its claims are rows of its record's Level 4 table. Every command is
read-only, and a run writes two things, in two zones:
- **the events** — the runner's telemetry, one per step, appended to `<host>/runbooks/events/self-diagnostic.jsonl`:
  a store that is committed and append-only on `main` (the sysadmin craft's `server-instances.md` property 7), in
  the host path's zone (`workstation` in dyad-system, `infra` in countersign-system);
- **the record** (§7), in zone `agent`, made by the party that ran the diagnostic and never by a step, since its
  L3 and L4 tables are a reading.

A repo transaction touches one zone (dyad-system Rule-1), so the two land as two changes: the events first, then the
record that cites their ids — the referent before the referrer, the order Rule-1 sets. Until the events are
committed they are a change in the working tree: the last step, `record`, reads the record back against them there;
the report never sees them, since it reads the committed tree of `main` (§2, L2); and dyad-system's pre-push path
refuses a push from a tree that holds them (Rule-14 property 3). A record committed without its events could not be
read back against them from the history (D22). The audit run-book (`dyad/runbooks/audit.md`) likewise leaves its record
to the party and reads it back last.
`/diagnose [level]` (`dyad/templates/commands/diagnose.md`) is a command adapter (`countersign-model.md` Part II §6) whose argument
is the last level to run (§3); it reads this section and the run-book and follows them, and is never the
procedure.

### When
- A level, the gate, the budget, a kind of finding or the record's form changes: this section, the run-book and
  the record `dyad/falsification/countersign-self-diagnostic.md` change in the same d-work, and the script with
  them when the levels file's form moves.
- A test module is added to a system that keeps the levels file: it is classified in the same body of work, or the
  next sweep's `levels` finding names it (§6).
- A system adds an L4 claim: in its own run-book's instance block, by its own body of work.

### Inference, stated
- L3 and L4 detect and never prove (D1): an attack that did not land means the reading found nothing, not that
  nothing is there.
- What a unit's contract is — its docstring and the rule that owns it — and whether a clause is covered, is read.
- The levels file's classification is read; the script checks only that it is complete and names what exists, and
  only when a run uses it (§6).
- A system diagnosing itself is circular (D4): the report's `checks-sha256` (§2, L2) lets anyone re-run the sweep on
  the same head of `main` and compare it, and no L3 or L4 finding settles itself (§5).
- L2's verdict is the head of `main`'s (D24); a run on another ref is judged on that ref's own range, which the
  run-book's first step reports.
- S2 and S4 are read over the session that runs the diagnostic, never over the system's past conversations, which
  no store holds (D23).
- Whether a codify candidate's reading can be written as code is for the proposal that takes it up to show.

### Sources
countersign-system #3: the prompt (four levels, one at a time, L1 to L4), and the answer to its first plan that
set the model — "two categories of tests/guards: coded rules and prose claims. both are required. falsify."
(provenance #3, entry 2) — with plan revisions 2–4; countersign-system #4 (the core owns d-work; countersign
describes); dyad-system #308 (this authoring), #143 (the inference budget) and #223 (the standing audit, D15); the
countersign model (report, escalation, command adapters; the codify edge).
