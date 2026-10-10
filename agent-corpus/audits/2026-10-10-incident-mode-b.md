# Incident mode B — a disposition recorded that the Operator never gave

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10; 3 of the 140 rows.*

## Definition
The mechanism is that the authorization chain is written by the party that needs the authorization,
with no second witness the kernel may read. The `-d` flag of `dyad dwork new|state` is a free-text
field in the one store that proves the Operator disposed; the Agent reaches for it at the moment it
*expects* a disposition — because the plan file is finished, because the backlog row is being
allocated, because a prompt has just arrived — and the field accepts whatever it is given. The row
then asserts an event that did not occur, and the assertion is indistinguishable, inside the repo,
from one that did.

**What would have to change.** A disposition entry must be producible only in the presence of
evidence the Agent did not author — the asked counter-prompt, at minimum — so that the chain records
an exchange rather than one party's expectation of one.

Boundaries against the neighbours it is most easily confused with:
- **A, acting before the authorizing disposition** — A's authorization is real and the act is early;
  B's authorization does not exist. Test: read the entry against what the Operator sent. Boundary
  rows: row 20 (#18) and row 41 (#67) share the mechanism of a required step skipped under momentum,
  and split on this test — #18's `Y plan` had never been asked, #67's `Y` was real and the row that
  records it was written after it.
- **S, a form typed from memory, not seeded from its governing definition** — S gets a record's
  *shape* wrong; B gets its *truth* wrong. Test: would a correct template have prevented it? Row 55
  (#161) sits on this boundary: `dwork new … -d "Y done (#161 audit)"` is both a misread of what `-d`
  records (the creating disposition) and a false claim about an unwritten audit. The false claim is
  primary; a perfectly shaped entry would have been just as false.
- **C, a value stated from memory instead of read from its source** — C restates something that
  exists somewhere and is stale or wrong; B records something with no source at all. Test: is there
  a source the value could have been read from? For all three B rows there is none.
- **Q, an obligation no mechanism reads** — row 134 (#223) looks like B from `origin`: PR #315 merged
  while `origin/main`'s row held only `N plan` and `Y plan`. It is Q, not B: the Done-`Y` existed and
  the local commit recording it preceded the merge by design; what was unfenced was the 32-second
  window before the push. Test: did the disposition exist anywhere when the entry was written?

## Incidents (3)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-15 | #18 | `dwork state 18 planned -d "Y plan"` run, recording a plan-`Y` disposition, before the Operator had been asked or had answered | the Agent went straight from writing the plan file to recording its authorization, skipping the counter-prompt that produces the disposition |
| 2026-09-25 | #161 | three backlog rows allocated with `dwork new … -d "Y done (#161 audit)"`, writing a Done-`Y` the Operator had not given and could not have, the audit being unwritten | `-d` records the creating disposition and was filled with the disposition the Agent expected the audit to receive; an Agent-opened backlog row has none until the Operator prompts it |
| 2026-09-29 | #185 | `dwork state 185 open -d "prompted …"` wrote a `disposed` entry for an Operator message that disposed nothing | the `-d` flag was reached for to record that a prompt arrived, conflating Rule-3's authorization chain with Rule-7's provenance store, where a prompt belongs |

## Pattern
Three rows over fourteen days, all three the same reach for the same field, and all three caught
before anything reached `main`. What they have in common is that `-d` was used to record something
other than a disposition the Agent had in hand: an expected plan-`Y` (row 20), an anticipated
Done-`Y` (row 55), an arrived prompt (row 70). None was an attempt to deceive; each was the field
closest to hand for a fact that wanted recording.

Recurrence against each mitigation the consequence cells describe:

- **Row 20's catch, the provenance guard's property-5 count (2026-09-15).** Row 70 (2026-09-29)
  post-dates it by fourteen days and was caught by the identical check, which its consequence cell
  quotes verbatim: `FAIL [guards] agent/provenance 185.md: 0 disposition entries, row #185 records 1
  (Rule-7 property 5)`. The mitigation detected the recurrence and did not prevent it — which is
  what a count check is for, and all it is for.
- **Row 55's catch is not a mitigation at all.** Its consequence cell says "caught before any
  commit, by reading the row back" — inference, in the same turn. No mechanism was involved, and
  the cell notes that the entry *would* also have broken property 5 had it been pushed.
- **#191's CLI coupling (2026-09-29, the same day as row 70): `-d` now requires `--said`.** No B row
  post-dates it. This is the mode's one measurement, and it reads two ways, so I state both: no
  instance of the mode has been logged in eleven days; and the coupling closes the gap that *caught*
  the last two instances. Before it, a false `-d` left the row's `disposed` count one ahead of its
  record's `disposition` count, and property 5 failed the push. After it, the row and the record are
  written in one step from the same two flags, so a fabricated disposition produces a *consistent*
  pair and property 5 passes. The residue is faithfulness of the words, which
  `dyad/guards/agent/provenance.py:27` and Rule-7's Enforcement both state is inference. Whether no
  B-shaped fault has occurred since 2026-09-29, or whether the mechanism that would have logged one
  no longer fires, is not decidable from the ledger. I could not establish which, and say so.

## Mitigations (phase 2)
Read from the code and the Rule text today, 2026-10-10, in this worktree.

### 1. `-d` requires `--said`, and every refusal precedes the first write — shipped
- **What.** `dyad dwork new|state` exits on `-d` without `--said`/`--said-file`: "refused: -d
  records a disposition; give its words verbatim with --said or --said-file (Rule-7)"
  (`dyad/scripts/package.py:926-928`), and symmetrically on `--said` without `-d` (`:929-930`).
  `--backlog` requires `-d` (`:943-944`); a new row requires the Operator's words in one form or the
  other (`:945-946`); a `backlog` → `open` transition requires `--prompt` (`:971-972`). Every fence
  check is made before the first write (`:935-936`, the comment states it).
- **Moment.** At the CLI, in `cmd_dwork` (`dyad/scripts/package.py:897`), before the row file or the
  record is touched.
- **Reaches.** Row 20: writing `-d "Y plan"` alone is now refused outright. Row 55: `dwork new …
  -d "Y done (#161 audit)"` is refused unless words are supplied. Row 70: `-d "prompted …"` is
  refused unless words are supplied — and the correct verb for that fact, `--prompt`, is named in
  the usage line (`dyad/scripts/package.py:60-62`). All three rows are reached in the sense that the
  exact command each ran is now refused. None is *prevented*: supplying a `--said` text the Operator
  never sent satisfies every one of these refusals.
- **Recurrence after it shipped.** None logged (see Pattern for why that is weak evidence).

### 2. The provenance state check, property 5 — shipped, and now blind to this mode
- **What.** `provenance.check_record` compares a record's `disposition` entry count to its row's
  `disposed` entry count and fails on a mismatch
  (`dyad/guards/agent/provenance.py:122-126`), less the `lost` count a listed legacy row carries
  (`:139-165`, the list at `agent-corpus/provenance_legacy.local.txt`, 30 lines today).
- **Moment.** `check_package` (`:167-200`) in the guard pass of `package.py check` and of
  `dyad check --guards`, i.e. every push (`dyad/hooks/pre-push:4`, loop at
  `dyad/scripts/package.py:601-615`) and every `check --evidence` run
  (`dyad/scripts/package.py:693`).
- **Reaches.** Rows 20 and 70 as they actually happened — both cells name it as the catch. It no
  longer reaches a fault of this shape produced by today's CLI, because mitigation 1 writes both
  sides together; the counts cannot diverge.
- **Recurrence after it shipped.** Row 70 post-dates row 20 by fourteen days under this same check.

### 3. The provenance transaction check — shipped
- **What.** `provenance.check_commit` requires, per non-merge commit against its parent: a row the
  commit adds brings at least one new entry; a row born `backlog` brings a `disposition`; a
  `backlog` → `open` brings a `prompt`; a row whose `disposed` gains k entries gains k `disposition`
  entries; and a record only grows (`dyad/guards/agent/provenance.py:232-270`, `_grows` at
  `:227-230`).
- **Moment.** `check_transaction` (`:287-299`), `TRANSACTION_MODE = "commits"` (`:39`), at every push
  on the kernel-only path (`dyad/hooks/pre-push:4` → `dyad/scripts/package.py:628`).
- **Reaches.** It fails the push that creates a count gap, where property 5 previously failed every
  later session's package check. Against this mode it reaches the same three rows as mitigation 2 and
  in the same way: a divergence, not a fabrication.
- **Recurrence after it shipped.** None logged.

### 4. "A `Y` binds only to the PR(s) or action(s) named in the question it answers" — shipped as Rule text, inference only
- **What.** Rule-2's Binding (`dyad/rules/RULE-2-no-self-ratify.md:46`) and Rule-7's Enforcement,
  whose closing sentence says that whether an entry is a faithful transcription is inference, with
  property 5's count as "its mechanical fence, and the Operator's own copy of the chat … the other".
- **Moment.** Inference, stated.
- **Reaches.** The mode's whole residue after mitigation 1: a well-formed, consistent, false pair.
- **Recurrence after it shipped.** Rows 55 and 70 post-date Rule-7 and Rule-2 by weeks.

The mode's live residue — a disposition recorded with fabricated words — has one mitigation and it
is inference, stated: the Operator's own copy of the chat.

## Remediation candidate, under attack
**The candidate.** Pair every disposition entry with the question it answers. The Agent records an
asked counter-prompt as a line in the d-work's plan file (`<instance>/d-work/plans/<id>.md`, Rule-15,
the Agent's own store) through a new verb `dyad dwork ask <id> <kind> "<question>"`; `dyad dwork
state <id> <state> -d "Y <kind> …"` then refuses unless the plan file holds an unanswered `asked:
<kind>` line, and `plans.py` checks the pairing over the store. It would fire at two moments: at the
CLI, before the first write (beside the refusals at `dyad/scripts/package.py:926-946`), and in the
guard pass of every push (`plans.check_package`, `dyad/guards/agent/plans.py:62-67`, which runs in
`cmd_guards`'s package loop at `dyad/scripts/package.py:601-615`).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The natural place for the question is the provenance record, and Rule-7 forbids it: property 4 is "The Operator's words only", and `provenance.KINDS` is pinned to exactly two by the invariant `kinds-are-two` (`dyad/guards/agent/provenance.py:42,60`), enforced at import (`:333`). A third kind is a Rule-7 amendment and a core-craft release. | confirmed | The record placement does not survive. Survivor: the question lives in the plan file, which is the Agent's own text by Rule-15 and by the vocabulary's `plan file` row, and the pairing check is Rule-15's guard rather than Rule-7's. |
| 2 | Self-asserted in one turn: the Agent types `dwork ask` and then `dwork state … -d` one command later, under the same momentum that produced all three rows. Row 41 (#67, mode A) is exactly a question asked out of order, so the ordering requirement is satisfiable falsely without leaving the keyboard. | confirmed | Prevention does not survive. What survives is an ordering *record*: the plan file's git history then shows whether the question existed before the answer was recorded, which today nothing shows at all. Detection, not prevention — the same demotion attack 2 of mode A's candidate produces. |
| 3 | It does not touch the mode's residue. The fabricated text is still fabricated; a false `--said` paired with a false `asked:` line passes. Rule-7 property 2 forbids the one witness the host holds — the raw transcript is never read and never committed — so the kernel cannot compare words against anything. | confirmed | "Addresses mode B" does not survive. Survives only as: the *existence* of the exchange becomes checkable, its *content* stays inference. |
| 4 | Cost against frequency: a new CLI verb, a Rule-15 amendment and a guard change, measured against three rows in fourteen days, the newest eleven days old, every one caught in the turn it happened — two by a check that still runs, one by reading the row back. | survives, scoped | Admissible only on Rule-13 property 1 (recurrence proposes code) read narrowly: the recurring task is recording a counter-prompt, which the Agent already does in prose every turn. Scoped to a line in the existing plan file and a refusal in the existing verb — no new store, no new provenance kind. |
| 5 | Rule-9 easy agreement: I agreed on first reading that recording the question fences the mode. Pushed against the one thing the mode's own history shows — mitigation 1 removed the signal that caught two of three rows — the honest reading is that this candidate restores a *different* signal and not the one that was lost. | survives, scoped | The candidate is a replacement for a mechanism this mode no longer has, not an addition to one it has. Framing it as strengthening an existing fence does not survive. |

## Proposed exit (phase 4)
**Exit 3 — recorded unfenceable on this kernel**, for the mode as it now stands. Proposed, not
taken; the Operator disposes.

The Rule that makes it so is Rule-7: its Enforcement states that "whether an entry is a faithful
transcription is inference, as every clerical write is", and property 2 forbids the only witness the
machine holds — "the Agent therefore writes the entry from the prompt it received, and never reads a
harness file to do it". Rule-14 property 2's reasoning stands behind that: the transcript's location
is a property of one kernel and one host, not of the dyad. A fabricated-but-consistent disposition
pair is therefore refutable only by the Operator's own copy of the chat, which Rule-7's Enforcement
names as the other fence. That is a judgement no script can decide, the shape Rule-5's Enforcement
already records for coherence.

Two things must be said with that exit, so it is not read as more than it is. First, the mode's
*existence* sub-shape — a `-d` with no words at all, which is how all three rows were actually
typed — **is** fenced at a named moment: the CLI refusals at `dyad/scripts/package.py:926-946`,
before the first write. Second, the mechanism that caught rows 20 and 70, property 5's count, has
been made blind to this mode by the same change that fenced the sub-shape; so the mode is better
defended against the careless form and worse instrumented against the deliberate one than it was on
2026-09-29. If the Operator prefers an exit 2 over an exit 3 here, the row to open is the
question-pairing candidate above, scoped as attack 1's survivor states it.
