# Audit: how many times the Operator is asked — the measurement behind d-work #290

*d-work #290. Opened 2026-10-14 on the Operator's prompt and executed the same day under plan
`agent-corpus/d-work/plans/290.md` revision 5 (`disposed: 2026-10-14 N plan` then
`2026-10-14 Y plan (revision 5)`). Standing: `main` at `6ca6827`,
python 3.14.4 (`python3 --version`), git 2.53.0, **280 numeric rows**, 260 provenance records, 45
stored traces, 65 presence files, 50 tags.*

**What this is for.** Not a verdict: a measurement, written so that a later session re-derives rather
than re-counts. Every figure below carries either the command that produced it or a `file:line`, and
is marked **[live]** where this record re-derived it at the standing above, or **[carried]** where it
comes from plan #290's own derivation and was not re-observed here. Where the two disagree the
disagreement is printed, never averaged.

**It is a topic audit, not the standing one.** `dyad/playbooks/audit.md` says in its own words that a
review the Operator asks for on one subject "stays an Operator prompt with its own plan; it may borrow
the Conduct below and nothing else here". So this record carries **no** `**Audited:**` or
`**Fences:**` watermark line, runs no phase 0 idempotence gate and no regression block, and borrows
exactly the Conduct: it detects and sizes, disposes nothing, changes no Rule and no code, and opens no
row. Findings are *proposed, not opened*.

**The conflict of interest, named as the 2026-10-08 audit named it.** The Operator asked how its own
attention is spent, and the Agent is counting the Operator's questions. Two constraints were binding:
no figure here argues for removing a Rule-2 base event, a Rule-8 destructive counter-prompt or a
Rule-11 release counter-prompt, and every reduction named is a reduction in **how many times** a
question is asked, never in **what** a `Y` authorizes. Rule-2's Binding is what makes that distinction
real: a batch `Y` "ratifies exactly the named set, each still checked against its own evidence".

## Method

Three independent derivations, in this order.

1. **Four parallel readers** (subagents, read-only — Rule-3 Scope) over the row store, the provenance
   store, the trace store and the transcript, at `1ed8d25`. **[carried]**
2. **The main Agent's own re-derivation** at the same standing, which corrected the readers in seven
   places; the corrections are listed in plan #290's *What revisions 1–4 got wrong*. **[carried]**
3. **This record's re-derivation** at `main` `6ca6827`, by one script over the live stores
   (`git ls-files`, `git log --diff-filter=A`, `git show <sha>:<path>`, and a parse of every
   `rows/<id>.md` and `provenance/<id>.md`). Its output is what every **[live]** figure below
   reports. **[live]**

Two conventions the figures depend on.

- **An entry is not a question.** `disposed` is free text with no kind field, so every
  question-count is a grouping choice. The live derivation groups by the `(batch …)` note; the
  main Agent's derived act count groups by commit, which is the one grouping that reads no note.
- **A disposition is the Operator's cheapest act.** Rule-3 Scope: "A **bare** disposal response … is
  not a prompt and opens nothing." A prompt has to be composed, and it is the only thing that opens
  a d-work or moves a `backlog` row to `open` (`dyad/scripts/package.py:971-972`,
  `dyad/guards/agent/provenance.py:262-264` both refuse that transition without the Operator's own
  words). So the prompt count is the expensive channel and is reported separately throughout.

## 1 — What the current flow costs

### 1.1 Dispositions

| figure | value | derivation |
|---|---|---|
| numeric rows | **280** | `ls agent-corpus/d-work/rows/*.md \| wc -l` → 281, less `README.md` **[live]** |
| `disposed` entries | **509** | every row's `disposed` split on `;`, blanks dropped **[live]**; 507 at the plan's snapshot, 505/506 at the readers' **[carried]** — the ledger grew by this d-work's own plan-`Y` |
| distinct Operator **questions** | **≈409**, bracketed 407–434 | collapse by `(batch …)` set; the bracket is "a bare `Y plan` repeated across rows on one date cannot be told from an unlabelled batch without the transcripts" **[carried]** |
| derived Operator **acts** | **370 dispositions, 193 prompts, 563 acts from 708 entries** | walk every commit that touched the provenance store and group its added entries by (commit, kind, verbatim text) — the one count that reads no note **[carried]** |
| active days | **25**, about **16 questions a day** | `opened:` span over the row store **[carried]** |
| provenance entries | **503 `disposition`, 199 `prompt`, across 260 records** | `grep -h '^## [0-9]' agent-corpus/d-work/provenance/*.md \| awk '{print $3}' \| sort \| uniq -c` **[live]**; 500/198 across 258 at the snapshot **[carried]** |

**By kind, live, over all 509 entries** — regex `^\d{4}-\d{2}-\d{2} ([YN]) *(\w+)?` per entry
**[live]**:

| kind | n | kind | n | kind | n |
|---|---|---|---|---|---|
| `Y done` | 190 | `N plan` | 22 | `Y merge` | **3** |
| `Y plan` | 174 | `Y release` | 8 | `Y departure` | 3 |
| `Y backlog` | 37 | `N done` | 6 | bare `Y` | 4 |
| `Y intake` | 30 | `Y open` | 23 | three singletons | 3 |

The 190 `Y done` entries agree in both directions with the 190 rows in `state: done`
(`grep -h '^state:' agent-corpus/d-work/rows/*.md \| sort \| uniq -c` → 190 done, 75 backlog, 9 open,
6 planned, **0 blocked, 0 archived**) **[live]**. **Fourteen distinct kind tokens over free text** is
the measurement's own limit and the audit's finding **A3** below.

### 1.2 The merge question the Operator named

Three entries in the whole ledger **[live, grep `Y merge`]**:

| row | entry | ISO week |
|---|---|---|
| #241 | `2026-10-07 Y merge #350` | W41 |
| #259 | `2026-10-10 Y merge PR #363,#364 (its own merge Y, the d-work not yet done)` | W41 |
| #259 | `2026-10-12 Y merge PR #365,#366 (its own merge Y, the d-work not yet done)` | W42 |

Per ISO week W38–W42: 0, 0, 0, 2, 1. The first 359 dispositions of a thirty-day ledger hold none; two
of the three are one row's; **184 of 189 merges rode a Done-`Y` — 97.4%** **[carried]**. The generator
is not a Rule: it is the `with-done` bullet's last sentence in `preferences-corpus/PREFERENCES.md`
("A PR whose d-work is *not* yet done still needs its own merge `Y`"), while Rule-2's Ratification
events require only that *some* Operator disposition ratify a merge and name two shapes **[live, file
read]**. The count is a **floor, not a total**: a counter-prompt asked and left standing writes no
entry, so only answered questions are countable.

### 1.3 Batching, as actually used

| figure | value | derivation |
|---|---|---|
| batch entries | **110 of 509** | entries containing `batch` **[live]** |
| distinct batch answers | **36** by id-set, **37** by the plan's grouping | group batch entries by their sorted `#<id>` set **[live]**; the plan counted 37 **[carried]** — see finding **A2** |
| set sizes | 2 (×12), 3 (×9), 4 (×5), 5 (×2), 6, 7 (×3), 8, 10, 14, 15 | same grouping **[live]**; the plan reports 2×20, 3×11, 4×3, 6×1, 10×2 **[carried]** |
| questions compressed | **about 73** | 110 entries behind ~37 answers **[live arithmetic]** |
| questions **removed** | **0** | Rule-2 Binding: a batch `Y` ratifies exactly the named set **[inference, stated]** |
| single questions in a form that *has* a batch form | **278** | **[carried]** |
| release dispositions asked one tag at a time | **8**, on two rows (#158 × 3, #241 × 5), though Rule-11 has carried a release batch form since #106 | `grep -l 'Y release'` over the row store **[live]** |

**The classes with no batch form at all.** Rule-3's Batch disposition defines exactly two forms, plan
and done. Row-opening (`Y open` 23, `Y backlog` 37) and Intake (`Y intake` 30) have none: **90
entries, 17.7% of every disposition ever given, with no defined way to batch them** **[live]**.
Rule-8's destructive counter-prompt is unbatchable by Rule and stays so.

### 1.4 Cost per d-work

| figure | value | derivation |
|---|---|---|
| `done` rows | **190**, holding **428** entries | **[live]** |
| mean / median entries per `done` row | **2.25 / 2** | **[live]**; identical to the snapshot's 2.25 / 2 **[carried]** |
| rows costing exactly the designed two | 109 | **[carried]** |
| rows costing one | 29 | **[carried]** |
| rows costing more than two | **51 — 77 entries above the ideal** | **[carried]**; #152 alone took five (a departure, a harness permission ask, a non-destructive detour, auto mode off, a second departure) |
| same-day rows | **88.8%** (229 of 258 with any disposition) | **[carried]** |
| entries, multi-day vs same-day | **3.10 against 1.81** — a d-work left open overnight costs about **71% more** | **[carried]** |

### 1.5 Wall time, and the honest correction to it

All **[carried]**, from the 45-file trace store (`agent-corpus/d-work/traces/`, 41 of which carry a
bucket table — #207, #228, #230 and #256 do not **[live, grep `| operator`]**):

- **176.3 h** of measured window, of which **110.7 h — 62.8% — is the `operator` bucket**, the wait on
  a reply ending in a `Y/N:` line; 63.9% counting `idle`. The top bucket is `operator` in **27 of 40**
  traces that had one at the snapshot.
- Median Operator wait per traced d-work **1,055 s**; mean wait per counter-prompt **6,129 s** with a
  **median of 639 s**; largest single wait **#204's plan question at 30 h 23 m**. By kind: 32 plan
  waits, median 531 s; 29 Done waits, median 713 s.
- The Agent partition is **229,212 s**, of which **189,093 s (82.5%) is self-flagged dead time** — the
  traces' own Limits bullet for agent-side segments of fifteen minutes or more, concentrated in six
  traces (#261 alone 166,393 s). Net of it: **Operator 112.6 h to Agent 11.1 h, about 10:1**.
- **All mechanical buckets together — suite, git, guards, github, subagent — are 5.8 h** across the
  whole store. So no fence, cache or faster suite moves this: the only lever on ~90% of the measured
  time is how many times the system stops to ask.

## 2 — Accretion, measured

An **accreted row** is one the Agent opens while executing another. Two mechanical marks, both read
from git rather than inferred:

1. the row was **born `backlog`** in its own add commit — surfaced, not worked:
   `git log --diff-filter=A --format=%H --name-only -- agent-corpus/d-work/rows`, then
   `git show <sha>:<path>` matched against `^state: backlog` → **94** **[live]**;
2. its **provenance entry 1 is a `disposition`** rather than a `prompt` — the kinds
   `dyad/guards/agent/provenance.py:254-261` forces at birth: `^## 1 (\w+)` per record → **89**
   **[live]**.

| ledger-wide | value |
|---|---|
| born `backlog` ∪ entry-1 `disposition` | **117 of 280 rows (41.8%)** **[live, exact — agrees with the plan]** |
| born with **no Operator act at all** (empty `disposed`, no record) | **14** — #38, #70, #129–#132, #134, #136, #170–#173, #177, #181 **[live; the same fourteen the 2026-10-08 audit's C6 names]** |
| Rule-3 **Intakes** among them (another Operator's words, Rule-7 property 4) | **28** **[carried]** — 30 `Y intake` entries across 29 rows ledger-wide **[live]**, of which 28 fall inside the 117 |

**And the measurement refutes the premise the plan brought to it.** Accreted rows that were *worked*
cost the Operator **more**, not less **[live]**:

| class | rows | mean `disposed` entries |
|---|---|---|
| accreted **and** `done` | **40** | **2.65** |
| prompt-born **and** `done` | **150** | **2.15** |

Not one entry-1-accreted row ever closed on a single disposition. **The only four accreted rows in
280 that cost one are #162, #163, #164 and #165** — and each holds exactly one `disposed` entry,
`2026-10-02 Y done (batch #199,#165,#164,#162,#163,#176, merges PR #234,…)`, with **no `Y plan` entry
and no plan file at all** (`ls agent-corpus/d-work/plans/16[2-5].md` → no such file) **[live]**. So
the saving is not "accretion is cheap" but **"accretion handled as #199 handled it is cheap, and it
has been handled that way exactly once."**

| handling of a child row | live case | Operator cost per child | where they are now |
|---|---|---|---|
| its own opening `Y`, then worked individually | #262–#284 (23 rows under `parent #259`) | ≥2 | **23 of 23 still `backlog`, 0 plan files** **[live]** |
| worked individually to done | #117–#125 (9 rows under `parent #116`) | **exactly 2 each — 18 dispositions** | all 9 `done` **[live]** |
| born with nothing, re-authorized by one shared prompt, closed in one shared Done-`Y` | #162–#165 under #199 | **1** | all 4 `done` **[live]** |

### 2.1 The per-chat question, and why the answer is a band

The Operator asked how many of these rows this chat opened. **Nothing in the corpus attributes a row
to a chat.** What exists, and what each gives:

| candidate attribution | what it holds | verdict |
|---|---|---|
| presence store `<instance>/d-work/sessions/` | **65 tracked files** (`git ls-files agent-corpus/d-work/sessions/ \| wc -l`), one per session, each with `session`, `seen`, `root`, `rows`, `files` | advisory and current-only (Rule-16): it says what a session *is* working, never what it *opened*. Every file but this session's is stale **[live]** |
| provenance records' `session:` line | **41 of 260** records carry one (`grep -l '^session:'`), **4** name this session | optional by Rule-7 property 1, so absence proves nothing **[live]** |
| row fields | `dyadlib.FIELDS` is `('id','title','opened','state','disposed','refs')` (`dyad/scripts/dyadlib.py:439`), closed by a pure import-time invariant in the row guard (`dyad/guards/agent/rows.py:38-39`) | **no session field exists, and an extra `key: value` line parses clean and is silently dropped** **[live]** |
| the `Claude-Session:` trailer of each row file's add commit | **394 commits** carry this session's id; **143 row files** are added in them (`git log --all --grep=<id> --diff-filter=A --name-only -- agent-corpus/d-work/rows`) | a **commit-message convention, not corpus data** — the soundest record available, and named as such **[live]** |
| the harness transcript | 27,443 records, 2026-09-14 18:38 → 2026-10-14 11:33 PDT | **never corpus** (Rule-7 property 2); read for the plan's first derivation only, and it was wrong both ways **[carried]** |

**So the per-chat answer is a band: 139–143 rows opened, of which ~82 accreted (69–83 by the choice
of mark).** The band's components **[carried]**: born `backlog` 69, entry-1 `disposition` 71, union
82, of which 8 born with no Operator act (#129–#132, #134, #136, #177, #181) and ≈27 Intakes;
prompt-born 57. The ledger-wide figure (117 of 280) is exact and reproducible; the per-chat figure is
not, and the five attributions above give five answers. A first derivation from the transcript's own
`dwork new` calls returned **105** and was wrong in both directions: 6 ids were listing output misread
as allocations, and 43 rows were missed — 34 whose id was never printed on a bare line and **9
(#102–#113) that were never created by `dwork new` at all**, their row files written directly
**[carried]**.

## 3 — The design is already in this tree

Three readings, each a file in the repo rather than an inference.

**3.1 The vocabulary exists, in a craft at v0.2.0** (`crafts/countersign/`, #152). The
Operator's words map onto it one for one **[live, file read]**:

| the Operator's words | `crafts/countersign/vocabulary/CRAFT.md` |
|---|---|
| meta-disposition | **mandate** — "a standing countersignature for one class of act (scope: event class, plan template, budget, rights); the countersignature of implicit mode" |
| an accreted row skipping its plan-`Y` | **implicit mode** — "countersigned in advance by a standing mandate; an agent processes" |
| a disposition's kind of coverage | **basis** — `per-act`, `mandate` or `release` |
| superseding the individual dispositions | **delegate edge** — "the mode change explicit → implicit" |
| the veto that must remain | **escalate edge** — implicit → explicit, "the unexpected returned for a live countersignature" |
| this very `N` with text | **amend** — "the proposal refused and its revision asked for in the same words, a linked re-entry" |

`crafts/countersign/rules/interaction.md` §4 writes the lifecycle ("is it covered by a mandate? If
yes: execute within the mandate's scope, then a countersign report. If no: escalation → explicit"),
§5 classifies `accretion` as an **authority preference** against the four existing **form
preferences**, and §7 — *"Adoption: refactors each system still needs — **not yet adopted**"* — lists
four for dyad-system, three of which are this prompt: `amend` in the answer grammar (**I2**), a
mandate *record* rather than preference prose (**I7**), a `mode` field on rows (**I7**), and an
initiation recorded for every row (**I6**). Rule-13 property 1 therefore makes this an adoption, not
a coinage.

**3.2 The kernel already permits the shape, verified by running it** — `prs.check` called in-process
against synthetic rows during planning **[carried]**:

| row as born | plan gate |
|---|---|
| `open`, `disposed: 2026-10-14 Y plan (mandate #259)`, `refs: parent #259` | **PASS** |
| `open`, `disposed:` empty | FAIL — no `Y plan` disposition |
| `open`, `disposed: 2026-10-14 Y mandate #259` | FAIL — no `Y plan` disposition |
| `backlog`, `disposed: 2026-10-14 Y plan (mandate #259)` | FAIL — `is backlog, not open` |

Five facts the design must respect, each a line of code **[live, file read]**:

1. **A pointer cannot go in `disposed`.** `dyad/guards/agent/rows.py:40` —
   `ENTRY = re.compile(r"\d{4}-\d{2}-\d{2} [YN](?: |$)")` — makes every entry a dated `Y` or `N`, so
   a mandate is carried by replication of the Operator's words plus a note.
2. **`append_provenance` stamps today's date unconditionally** (`dyad/scripts/package.py:878`), so the
   mandate's own date belongs in the note or the record misdates the Operator.
3. **A row born with no Operator act is refused, correctly** —
   `dyad/guards/agent/provenance.py:254-258` and `:259-261`, `dyad/scripts/package.py:946`; the
   craft's imperative **I6** says the same, and all 14 such rows are still `backlog`.
4. **`backlog → open` needs the Operator's own prompt** (`provenance.py:262-264`,
   `package.py:971-972`), so an implicit-mode row must be born **`open`**.
5. **The Rule sentence and the table are already coupled**:
   `dyad/tests/test_dyadlib_rows.py:17-28` parses "Transitions are exactly: … (`dyadlib.TRANSITIONS`"
   out of Rule-16's text and asserts it equals the table.

**3.3 Four rows the Operator opened already name the fence** — phase 1 of #259, 2026-10-10
**[live, titles read]**:

| row | mode | what it names |
|---|---|---|
| #273 | L | a plan ordering no disposition sequence can authorize — 5 rows, and #259's own parent gate is the live instance |
| #274 | M | no legal order, no verb — 11 rows |
| #278 | Q | an obligation no mechanism reads — 12 rows, the parent gate itself, which no guard resolves |
| #281 | T | a stale or partial view of shared state — 10 rows, the presence store's defects |

## 4 — The larger lever: the board has no exit

All **[live]** except the inflow rate.

| figure | value | derivation |
|---|---|---|
| `archived` | **0 uses in 280 rows** | state histogram |
| `blocked` | **0 live rows** (used once ever, #185, and returned to `open`) | state histogram; **[carried]** for the history |
| `backlog` rows | **75** | state histogram |
| median age | **21 days**; 44 of them ≥14 days; oldest **30** | `today − opened:` per backlog row |
| rows born with a `Y backlog` first entry | **37**, of which **35 are still `backlog`** — a **5.4% drain** | first entry per row |
| `backlog` rows carrying a `Y intake` entry | **20** — another Operator's words, excluded by design | grep |
| net inflow | **~2.5 backlog rows a day** over the 30-day span; at that rate the board passes 150 in a month | **[carried]** |
| the table, at this standing and before this d-work's own mutation | `TRANSITIONS["backlog"] == frozenset({"open"})` — **a `backlog` row cannot be retired without being worked** | `dyad/scripts/dyadlib.py:448`; `backlog → archived` and `backlog → done` both refused |

Rule-3 already *defines* `archived` as "retired from the working board by an Operator disposition
naming the row(s)". Only the table forbade it from where 75 of the rows are. Two of the six states
this system defines have never been exercised, and the only exit it has used is `done` (190 rows).

**And the cost of clearing the one live instance by hand** **[carried]**: #259's 23 `backlog` children
take **47 dispositions** strictly one-per-question (23 prompts to open, 23 deferrals, one Done-`Y`),
70 if each is worked to done, 93 by the archive route — against 3 if the two batch forms are stretched
to cover row-opening, which Rule-3 does not today say they do.

## 5 — Reconciliation with the 2026-10-08 audit

`agent-corpus/audits/2026-10-08-disposition-chain-of-authority.md` (#251, six days before this one) inventoried **thirteen counter-prompt forms**, found **eleven of thirteen add authority
nothing else supplies**, and **recommended nothing** by its own method. That is not in conflict with
this record, and the two must not be read as disagreeing:

- **Different questions.** That audit asked *which questions are unnecessary*. This one asks *how few
  times the Operator is asked*. Its own three `friction` rows are the only overlap, and this record
  proposes removing none of them.
- **Batching and mandates remove no authority.** Rule-2's Binding makes a batch `Y` ratify exactly the
  named set; a mandate's `Y` authorizes a class the question states and its Done-`Y` verifies an
  enumerated delivered set. The authority count is unchanged; the question count is what moves.
- **Its findings are this record's inputs, not its targets.** Its **L2-1/L2-2** (the plan gate is a
  substring test over free text, five strings pass it meaning the opposite) is exactly why a mandate
  carried in `disposed` inherits an unreliable key, and its **candidate row 2** — *parse `disposed`
  into kinded entries* — is the fence this measurement names and does not build. Its **C2** (nothing
  couples a state transition to a disposition) is why #162–#165 could reach `done` on one entry at
  all. Its **L6-8** (the release batch is structurally unreachable when the tags are the deliverable)
  is why the 8 release dispositions were asked singly.
- **One of its limits is closed here and one is not.** It recorded "`blocked` and `archived` are
  unexercised: zero live rows in either state"; this record prices that — 0 uses of `archived` in 280
  rows, 75 rows with no exit — and the mutation opens the edge. Its limit "whether the 42 undisposed
  tags lack a disposition or only its record cannot be settled from the repo" stands untouched.

## Findings

Each is a claim and was attacked before it was written (Rule-9, trigger "an audit surfaces a claim");
the attacks are in `agent-corpus/falsification/2026-10-14-operator-attention-scaling.md` and in the
per-Rule amendments.

**A1. The merge counter-prompt is a symptom; a parent gated by `backlog` children is the mechanism.**
3 of 509 dispositions ever, all in the last eight days, two on one row — and that row's Done question
is mechanically unaskable, so its PRs had to be ratified some other way. Rule-3's Ledger clause plus
`TRANSITIONS["backlog"] == {"open"}` is the whole generator. One live instance.

**A2. Three of the plan's own figures are not reproducible as stated, and the reason is the same in
all three: `disposed` has no kind field.** (a) *Presence files*: the plan reports 67; the tracked
count is **65** — `ls -a` counts `.` and `..`. (b) *Batch answers*: the plan reports 37, this record
36 distinct id-sets; the unit "an answer" is undefined because two entries written on one date with
the same set cannot be told from one answer. (c) *Backlog rows accreted*: the plan reports 54 of 75;
by the plan's own two marks **all 75** are accreted, since a row born `open` cannot reach `backlog`
(no such transition), and 20 of the 75 carry a `Y intake` entry, leaving 55 under this Operator's own
hand. None of the three changes a conclusion; all three are printed rather than reconciled.

**A3. Fourteen distinct kind tokens appear in `disposed`** — `done`, `plan`, `backlog`, `intake`,
`open`, `release`, `merge`, `departure`, `harness`, `non…`, `auto…`, `shape`, `re-plan`, and a bare
`Y` with no token (4 entries). Every count in section 1.1 is therefore a grep over prose, which is
the 2026-10-08 audit's candidate row 2 restated from the other end.

**A4. The expensive channel has never been measured before this record.** 199 `prompt` entries
against 503 `disposition` entries: a disposition is a bare `Y`, a prompt must be composed, and only a
prompt opens a row or moves one out of `backlog`. Every prior count — this record's included —
reported the cheap act.

**A5. The mandate shape has already been executed once, successfully, and nobody noticed.** #162–#165
under #199: one shared prompt, one shared batch Done-`Y`, no plan file, no `Y plan` entry, four rows
`done` at one disposition each. It is the design's only live precedent and it predates the design.

**A6. Two of six states are unexercised and the board has one exit.** 190 `done`, 75 `backlog`, 9
`open`, 6 `planned`, 0 `blocked`, 0 `archived`.

**A7. The per-chat question is unanswerable from the corpus, by construction.** No row field, 41 of
260 records with a `session:` line, a presence store that is current-only by Rule-16's own design, and
a transcript Rule-7 property 2 keeps out. The answer is a band and the method is a commit-message
trailer.

## Proposed rows — surfaced, never opened

Strongest first; the Operator disposes each. None is opened by this d-work (play-book Conduct).

1. **Parse `disposed` into kinded entries** — the plan gate requiring `^\d{4}-\d{2}-\d{2} Y plan\b` on
   the *last* `plan` entry, and a grammar for `release <tag>`, `mandate #<id>` and `archive`. Closes
   A3, the 2026-10-08 audit's L2-1, L2-2, L6-1 and L6-3, and makes a mandate's key reliable.
2. **A per-row base commit for an accreted row**, or an explicit statement that the mandate's governs:
   Rule-15 phase 2's drift check cannot fire for a row with no plan file of its own (that Rule's
   amendment #290, attack 8).
3. **Trace an implicit-mode row.** `dyad/scripts/trace.py` anchors on a prompt and a Done-`Y`, and an
   accreted row has neither of its own; #256 is the one 0-anchored trace of 45. The design's own
   metric is not yet measurable per row.
4. **Two projectors the design breaks**: `project_kanban.py` would draw every implicit-mode row as a
   warn, and `project_countersign.py`'s `OPENING_WORDS` leaves 40 rows underivable.
5. **Re-land PR #355** under a new row that refs #245: the plan gate refuses the old one
   (`FAIL [d-work]: #245 is done, not open`), a ratified merge that never ran and the fifth
   gate-after-Done occurrence.
6. **Normalise the six child links using `parent-46`/`parent-49`** instead of `parent #N`, which
   `references.py`'s `hash_ids` cannot resolve — required before any mechanism keys on the parent link.
7. **Move the evidence block to the PR body**, with its `evidence-sha256` in the reply: at ~217 lines
   × 190 `Y done` dispositions it is the largest single thing the Operator is handed, and the accreted
   list makes it longer. A Rule-2 and Rule-14 property 3 change, and it should probably precede the
   mandate.

## Not observed

- **No transcript was read for this record.** Rule-7 property 2 keeps it out of the corpus; every
  per-chat figure here comes from commit trailers, and the transcript-derived figures are marked
  **[carried]** from the plan.
- **The trace arithmetic was not re-run.** Section 1.5 is carried whole. Its known biases are upward
  on the agent side (+32.5 s median, `INCIDENTS.md` row 151) and downward on the window (row 148);
  3.6% of the Operator sum is double-counted across shared turns; five traces record `operator = 0`
  against a real wait; four carry no bucket table. **No claim of hours saved is made or supportable
  from it.**
- **The Operator's reading time is unobservable.** The 110.7 h `operator` bucket is elapsed time — how
  long this system stood still — not attention spent. The count of questions is the figure the
  proposal acts on.
- **The largest question channel is outside this corpus**: the harness permission mode, which Rule-8's
  Boundaries place there by construction, with one ledger footprint in 280 rows (#152's two entries).
- **Rules 8, 18 and 19 generate zero Operator questions on this instance**: 0 ops scripts, 3
  change-log rows all `reversible`/`actor: agent`, every run-book event `role: agent`. Stated so that
  "this touches no destructive counter-prompt" is not read as care taken.
- **Rows opened before 2026-09-12 #46 are not backfilled**, so early `disposed` entries are
  undercounted.
- **No write, commit, push, merge, tag, `gh` call or host action** was made by any seat of this
  measurement. The live derivation read the stores and the git history only.

*Disposition: see ledger #290.*
