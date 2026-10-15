# Self-diagnostic (countersign craft, Tended rule)

Read by this craft's script `../scripts/levels.py` (the levels file's check, §6), by its run-book template
`../templates/runbooks/self-diagnostic.md` (the steps, §8) and its command adapter
`../templates/commands/diagnose.md` (`/diagnose`), and by every system that installs the craft and runs the
diagnostic on itself — countersign-system first (its d-work #3); no core Rule reads it. A Tended rule: any form,
no Rule-4 block, no sweep. It **describes** a model — what a system's self-diagnostic is made of, in what order,
what passes and what a run leaves behind — and binds no system's agent by itself: in a dyad system only its core
Rules bind, and where this file says what becomes of a finding it says what those Rules already do, by reference
(§5). That is countersign-system #4's survivor (the core craft owns d-work whole; countersign describes the model
a system is checked against and binds nothing) applied to its plan #3 (D11). Terms: `../vocabulary/CRAFT.md`
(rule `self-diagnostic`). Record: `../falsification/self-diagnostic.md` (C1–C6, D1–D25). Source:
countersign-system plan #3, revisions 2–4 (`agent-corpus/d-work/plans/3.md` there), authored here under
dyad-system #308.

## Intent
Describe one self-diagnostic any Countersign system can run on itself: four levels, built from two kinds of check
at two scopes, run one at a time, so that cheap mechanical proof comes before inference and no inference is spent
reading a system whose code already fails; every command read-only, and the runner's events and one record a
run's only writes (§8).

## 1. Two kinds of check (C1–C6)
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
a candidate for code (C5): the record marks it (§7, `codify?`), in the shape of this craft's codify edge (a
practice done by hand becomes a definition a non-inferring party runs) and of dyad-system's Rule-13 property 1
(recurrence proposes code).

## 2. The grid: four diagnostic levels
The two kinds of check at two scopes are the four levels (C6):

| | coded check | prose claim, with its attack |
|---|---|---|
| **unit** — one module | **L1**: unit tests | **L3**: each unit's contract is covered by its invariants and tests |
| **system** — modules together, the live tree | **L2**: integration tests, the guards on the live tree, the transaction guards, the evidence block | **L4**: a fixed list of system claims, and the instance's own |

Order: coded before prose, and unit before system within each kind — L1, L2, L3, L4, the order the countersign-system
prompt names. Each level gates the next (§3).

### L1 — unit × coded check
- **Verifies:** each unit's own tests — the test modules the levels file (§6) classifies `unit`.
- **How:** each module through the runner's one-target path, `dyad check --tests <target>`, the same child the
  full suite spawns (dyad-system Rule-12 property 2).
- **Passes:** every `unit` module OK.

### L2 — system × coded check
- **Verifies:** modules together — the test modules classified `integration` (scratch repos, git, installs, the
  runner spawned); the guards on the live tree, among them the coded checks of prose (Rule blocks, vocabulary,
  references, provenance counts, zones, the manifest); the transaction guards; and the evidence block.
- **How:** each `integration` module as L1 runs its own; then `dyad check --evidence` on the head diagnosed, which
  runs the runner's invariant pass, every check and every guard on the kernel alone, observed and never read from a
  suite memo, and prints the evidence block (dyad-system Rule-14 property 3, Rule-12 property 2). It runs in a clean
  clone of that head — the same commit, the same branch name, the same `origin/main`, nothing uncommitted — because
  in the checkout the block would hash the run's own uncommitted events (its `dirty=` line and the event guard's
  count, §8), which no later run on that head can reproduce (D21). The record keeps the block's `evidence-sha256`
  line, so anyone can re-run `dyad check --evidence` on the same head, on `main`, in a clean checkout, and compare
  (D4).
- **On `main`:** the head diagnosed is the head of `main`, checked out. The block's transaction guards judge the
  checked-out ref: dyad-system's plan gate (`agent/prs`) passes `main` and judges any other branch's or a detached
  head's own commits, failing a range that cites no d-work — an empty one included — so a run off `main` would
  report the ref, not the system (D24). The run-book's first step names the branch, and its pass criterion fails off
  `main`.
- **Passes:** every `integration` module OK, and the evidence block green.

### L3 — unit × prose claim
- **Verifies:** that each unit's invariants and tests cover the contract it states. A **unit** here is a module
  that declares an `INVARIANTS` list — a module carrying a data model (syseng `invariants.md` property 1).
- **How:** the coded half first — the runner's invariant pass, one `[invariant]` line per module, which `dyad
  check`, `--guards` and `--evidence` print before any check (the evidence block L2 recorded holds them). Then the
  prose half over K units in rotation (§4): for each, the claim *"this unit's invariants and tests cover its
  stated contract"* — its contract being its module docstring and the rule that owns it — is read against the
  attack *"name a contract clause whose breaking no invariant and no test would catch"*.
- **Passes:** every `[invariant]` line `ok`, and the attack lands on no sampled unit. A landed attack is a finding:
  the uncovered clause, and the invariant or test that would cover it (§5).
- **codify?:** a clause an invariant or a test already covers is code and needs nothing; a clause the attack could
  decide only by reading, read so on two successive runs that sampled its unit, is a codify candidate.

### L4 — system × prose claim
- **Verifies:** a fixed list of claims about the whole system, each with its attack — the eight imperatives of this
  craft's interaction model (`interaction.md` §3, I1–I8), then three of the system's own — and the claims an
  instance adds. Each claim's coded half, where it has one, already ran at L2 or runs in the step that prints the
  sample; L4 reads what that half cannot decide.

| # | claim | attack | coded half |
|---|---|---|---|
| S1 | only a human countersigns (`interaction.md` I1) | among P sampled acts, find a countersignature whose signer is not the human party, or a disposition with no human's words behind it | the projector's `check` (I1), where this craft's projector runs: its live test at L2 and the `acts` step |
| S2 | one question per reply, its last line (I2) | in the session that runs the diagnostic, find a reply asking more than one question, or asking one anywhere but its last line | none: a question lives in the conversation, not in a store (`interaction.md` §3) |
| S3 | falsified before proposed (I3) | among P sampled rows, find one carrying a plan whose plan file holds no falsification section and no pointer to a falsification record | none: the record's existence is the evidence (`interaction.md` §3) |
| S4 | detect, don't dispose (I4) | in the session that runs the diagnostic, find a finding repaired rather than proposed, or a change to the tree since the head diagnosed besides the run's two writes (§8) | the line naming what the checkout holds besides the event store, printed before the evidence block |
| S5 | the ledger and the provenance agree (I5) | for P sampled rows, find a `disposed` entry whose provenance text does not carry that answer | dyad-system's `agent/provenance` (the count, Rule-7 property 5) |
| S6 | no act is self-initiated (I6) | among the projector's I6 warnings and P sampled acts, find an act opened on a non-human party's own finding | the projector's `interaction`, warnings only |
| S7 | every act carries its mode and a countersignature reference (I7) | among P sampled acts, find one with no mode, a mode its processor contradicts, or an answered question no countersignature resolves to | the projector's schema validation and `check` (I7): a red one is the finding, and the reading confirms the sample |
| S8 | silence is not consent (I8) | among P sampled rows, find a state past `open` or a merge for which the row's `disposed` column records no answer: an act taken on silence | the projector derives no countersignature from an absent answer (`interaction.md` I8); dyad-system's plan gate (`agent/prs`) refuses a branch whose cited row carries no `Y plan` |
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

## 3. The gate
L1 always runs; level N runs only when level N−1 passed. A level that does not pass ends the run: every later level
is recorded `not run (gate)`, and nothing is repaired inside the diagnostic — a repair is its own unit of work in
the system's own process (§5). The reason is cost and confidence: a reading done over code that already fails reads
a system other than the one on disk, and the cheap mechanical proof is what says so. The invariant pass is coded
but sits at the head of L3, not in L2: it is the unit-scope fact L3's reading rests on, and placing it there costs
nothing, since L2's evidence run has already printed it — and a false invariant has already turned that evidence
block red, so at L3 the coded half re-reads what L2 decided (D2). A landed L3 attack stops L4 for the same reason:
L4's claims rest on the units' contracts, and reading the system over a contract already known to be uncovered
spends inference on a model known to be incomplete. A run may also be asked to end after a given level (the
command's argument, §8): every level after it is recorded `not run (last level <n>)`, which is no finding, and a
run that ends at L2 spends no inference.

## 4. Budget and rotation
Inference is bounded per run: **K** units at L3 (default 4) and **P** samples at L4 (default 3: P acts or rows for
S1, S3 and S5–S8, P Rule pairs for S10; S2, S4, S9 and S11 are read whole). The values a run used are in its
record. A **rotation cursor** makes successive runs cover everything (D5): each record ends with where the next run
starts — the next K
units in sorted module-path order, the next P rows by id, the next P Rule pairs in sorted pair order, each wrapping
at its end — and a run reads the newest previous record's cursor before it samples; with none, every order starts
at its first item. With n units, every unit is read once in ⌈n/K⌉ runs that reach L3. The bound is dyad-system
#143's concern — inference budget first, more tokens accepted only for more reliability — made explicit.

## 5. Findings, and where each goes
A finding is what a level surfaced: a coded check that failed (L1, L2, L3's invariant pass), an attack that landed
(L3, L4), or a codify candidate. The diagnostic decides none of them, and no finding is a verdict: L3 and L4 detect,
they do not prove (D1). In this craft's interaction model the record is a **countersign report**
(`interaction.md` §1): evidence that never asks. What it surfaces unsigned is an **escalation**, which becomes a
countersign proposal in explicit mode. In a dyad system the core's Rules already say what each kind becomes:
- a failed coded check — a test, a guard or an invariant that fails, a defect — is an incident (Rule-3,
  Incidents: "a failed check"; for an invariant, Rule-12 property 1 too), reported as observed, never assumed
  (Rule-3's completion evidence), its repair a plan of its own (Rule-3, Plan);
- a landed L3 attack — a contract clause no invariant or test covers — and a landed L4 attack — a system claim
  shown false — are proposals (Rule-10), each adopted, if at all, as a plan of its own (Rule-3, Plan), or held as
  a `backlog` row by the disposition that opens one (Rule-3, Ledger);
- an outcome the diagnostic's own plan did not name is an incident (Rule-3, Incidents);
- a codify candidate is an inference task met a second time, which proposes code (Rule-13 property 1).

## 6. The levels file
Which test module is L1's and which L2's is instance data: the system that runs the diagnostic owns its installed
inventory, and a list in the craft would couple this craft's suite to every other craft's tests (D8). The file is
`<host>/self-diagnostic-levels.txt`, `<host>` the host path (`dyadlib.host_path`; dyad-system preference
`host-path`, default `workstation-corpus`; countersign-system `infrastructure`). It is seeded from
`../templates/self-diagnostic-levels.txt`, by hand (`../README.md`); an install never copies it (dyad-system
Rule-11 property 2).
- **Form:** one entry per line, `<level> <path>` — `level` is `unit` or `integration`, `path` a repo-relative test
  module (`dyad/tests/test_dyadlib_rows.py`, `crafts/sysadmin/tests/guards/test_runbooks.py`); `#` comments and blank
  lines are allowed.
- **Inventory:** a system's test modules are every `test_*.py` under the runner's test roots — `dyad/tests/` and
  every `crafts/<craft>/tests/` present (`package.test_suites()`). The roots are the runner's; within them that set
  is what `unittest discover` runs only where the syseng craft's naming guard keeps the two equal — no other
  `test*.py`, no test module outside a package. Where that craft is not installed, a helper the suite runs may go
  unlisted and a module it never runs must still be placed (`../scripts/levels.py`).
- **Granularity: the module** (D16). A module that mixes kinds is `integration` when any one of its tests builds a
  scratch repo, runs git, installs, or spawns the runner; otherwise it is `unit`.
- **Check:** `../scripts/levels.py`, a script of this craft and not a guard (D20), checks that the file is complete
  and names what exists, never that it is right. It fails on a test module present but unclassified, an entry
  whose path names no test module of the tree, a malformed line, or a path listed twice. It runs where the
  classification is used: the run-book's `health` step runs it, and the `unit` and `integration` steps read the
  file through its `list`, which refuses a file that fails. No runner discovers a script, so it runs on no push: a
  module added without its line is found at the next run's `health`, before any test runs. It skips with one line
  when the file is absent, so a system that runs no diagnostic — dyad-system, which authors this craft — is
  unaffected by it (D17, D25). The file's paths are references the
  script resolves itself, outside dyad-system's reference register (D19). Whether a module is rightly `unit` is
  read.

## 7. The record
One of a run's two writes (§8): `<instance>/audits/<YYYY-MM-DD>-self-diagnostic.md` (`DYAD_INSTANCE`, default
`agent-corpus`), where the core keeps audits, in zone `agent`. It holds:
- the head diagnosed, and the K and P the run used;
- per level, its result — `pass`, `fail`, `not run (gate)` or `not run (last level <n>)` (§3) — its evidence (the
  observed output lines of its commands; at L2 the `evidence-sha256` line) and its findings;
- for L3 and L4, a table `claim | attack | result | codify?`, one row per sampled unit or claim sample;
- the rotation cursor (§4): where the next run's K units, P rows and P Rule pairs begin.

The run-book fixes the lines its steps read back: `**Diagnosed:** head <sha> · K <k> · P <p> · evidence-sha256
<value>`, one `**Result:**` line under each level's heading, and `**Cursor:** units=<path> rows=<id> pairs=<a>-<b>`,
each value the first item the next run reads, at or after it and wrapping, so an item added or removed since does
not break the rotation. The name is one per day (UTC): a later run on a day that already has a record rewrites
that day's record, after reading its cursor, and the earlier text survives in the system's history once the unit
of work that wrote it has committed it.

The record is evidence and asks nothing (§5). Its dated name falls under the core's `<instance>/audits/<date>-*.md`,
which dyad-system's standing audit leaves out of its watermark (`dyad/playbooks/audit.md`, Phase 0), so a
diagnostic record never makes an unchanged tree look changed (D15).

## 8. The run-book and the command
The steps are a run-book in the sysadmin craft's run-book form (`crafts/sysadmin/rules/server-instances.md`) with
its own section set, `# sections: Level 1, Level 2, Level 3, Level 4`: a run-book that declares its sections is
checked against them, as a core run-book is, and is not a server's (that rule's property 2). Template
`../templates/runbooks/self-diagnostic.md`, seeded to `<host>/runbooks/self-diagnostic.md`; its steps run through
the core runner, `dyad runbook run self-diagnostic <step>`, which records one event per step. Every command is
read-only, and a run writes two things, in two zones:
- **the events** — the runner's telemetry, one per step, appended to `<host>/runbooks/events/self-diagnostic.jsonl`:
  a store that is committed and append-only on `main` (the sysadmin craft's `server-instances.md` property 7), in
  the host path's zone (`workstation` in dyad-system, `infra` in countersign-system);
- **the record** (§7), in zone `agent`, made by the party that ran the diagnostic and never by a step, since its
  L3 and L4 tables are a reading.

A repo transaction touches one zone (dyad-system Rule-1), so the two land as two changes: the events first, then the
record that cites their ids — the referent before the referrer, the order Rule-1 sets. Until the events are
committed they are a change in the working tree: the last step, `record`, reads the record back against them there;
the evidence block never sees them, being computed in a clean clone (§2, L2); and dyad-system's pre-push path
refuses a push from a tree that holds them (Rule-14 property 3). A record committed without its events could not be
read back against them from the history (D22). The core's audit run-book (`dyad/runbooks/audit.md`) likewise leaves
its record to the party and reads it back last.
`/diagnose [level]` (`../templates/commands/diagnose.md`) is a command adapter (`interaction.md` §6) whose argument
is the last level to run (§3); it reads this rule and the instance's run-book and follows them, and is never the
procedure.

## When
- A level, the gate, the budget, a kind of finding or the record's form changes: this rule, the run-book template,
  the falsification record and `VERSION` change in the same unit of work, and the script with them when the levels
  file's form moves.
- A test module is added to a system that keeps the levels file: it is classified in the same unit of work, or the
  next run's `health` step fails on it (§6).
- A system adds an L4 claim: in its own run-book's instance block, by its own unit of work.

## Inference, stated
- L3 and L4 detect and never prove (D1): an attack that did not land means the reading found nothing, not that
  nothing is there.
- What a unit's contract is — its docstring and the rule that owns it — and whether a clause is covered, is read.
- The levels file's classification is read; the script checks only that it is complete and names what exists, and
  only when a run uses it (§6).
- A system diagnosing itself is circular (D4): the evidence block, computed in a clean clone of the head (§2, L2),
  lets anyone re-run L2 on the same head, on `main`, and compare its sha, and no L3 or L4 finding settles itself (§5).
- L2's verdict is the head of `main`'s (D24); a run on another ref is judged on that ref's own range, which the
  run-book's first step reports.
- S2 and S4 are read over the session that runs the diagnostic, never over the system's past conversations, which
  no store holds (D23).
- Whether a codify candidate's reading can be written as code is for the proposal that takes it up to show.

## Sources
countersign-system #3: the prompt (four levels, one at a time, L1 to L4), and the answer to its first plan that
set the model — "two categories of tests/guards: coded rules and prose claims. both are required. falsify."
(provenance #3, entry 2) — with plan revisions 2–4; countersign-system #4 (the core owns d-work; countersign
describes); dyad-system #308 (this authoring), #143 (the inference budget) and #223 (the standing audit, D15); this
craft's `interaction.md` (report, escalation, command adapters) and `schema.md` (the codify edge).
