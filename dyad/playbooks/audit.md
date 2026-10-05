# Play-book: audit (core craft, `dyad-operator`; #223)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for
a recurring decision; its steps are a run-book. This one is the **standing audit**: the topic-free,
whole-system pass that is run again and again, and that the per-change gate leaves to audit — #220's
survivor, "unit regression of everything else is an audit job", with its cadence an open parameter.
An audit (vocabulary) is an agent-authored review that elevates gaps for Operator disposition; until
now nothing said what the standing one reads, in what order, what it writes, or when it writes nothing.
Steps: `dyad/runbooks/audit.md` — `survey`, `regression`, `fences`, `drift`, `incidents`, `record` —
run through `dyad runbook run audit <step>`, the core runner, so each step leaves an event.

It is not a topic audit. A review the Operator asks for on one subject (a performance profile, a sweep
of one craft, the subset CI should run) stays an Operator prompt with its own plan; it may borrow the
Conduct below and nothing else here.

## Trigger
An Operator prompt asking for the audit. No Rule requires it: contrast `incident-hardening.md`, which
Rule-3's Incidents clause reads, and like `ds-report-incidents.md` this one is read on a prompt. The play-book
runs inside the d-work the prompt opened and is planned there (Rule-15 phase 1) before any record is
written; a d-work of another kind that notices the gate below would open states it as a finding and opens
nothing, since a d-work opens on an Operator prompt or disposition and never on the Agent's own finding
(Rule-3, Scope).

The cadence is #220's open parameter and is not set here. A clock is not the gate: it would add a second,
weaker one carrying its own failure mode — a changed system ignored because the calendar said no, an
unchanged one re-read because it said yes. Phase 0's watermark decides whether there is anything to read.

## Phase 0 — Survey (the idempotence gate)
The record of phase 4 carries two lines. The first is the watermark:

    **Audited:** tree <hash> · python <v> · git <v> · covered through <sha>, <YYYY-MM-DD>

`tree` is the sha256 of `git ls-tree -r HEAD` **minus the dated audit records**
(`<instance>/audits/<date>-*.md`; `INCIDENTS.md` is not dated and stays in). The records are the audit's own
output: with them in the hash, the record this audit commits would change the tree, and the next audit could
never see an unchanged one. `python` is the interpreter the entrypoint resolves (`dyad/bin/dyad-python`),
`git` its version. Survey derives the live line and compares it to the one of the newest record. Three
outcomes, and only the last two derive anything new:
- **Same tree, same interpreter, same git** — phases 1 and 3 are a no-op: nothing new is there to find, and
  a deterministic suite on an unchanged tree says what it said. The audit prints both lines, writes no file
  and says "unchanged since <record>" (`0 changes`, the shape `crafts/syseng/rules/idempotence.md` property 1
  sets for the install). **Phase 2 still runs**, below.
- **Any of the three differs** — the full exercise.
- **No record carries the line** — the first exercise, full derivation.

The watermark is compared, never believed: the live line is derived at survey time, so a hand-edited record
is caught by the comparison.

## Phase 1 — Regression
The whole suite, every root, **observed** on the exact head: `dyad check --evidence`, the command the merge
evidence already runs (Rule-14 property 3; Rule-13: reused, not rebuilt). It never reads the suite memo
(Rule-12 property 2), so the result is a run and not a recollection. The record pastes the block verbatim.

This is the job #220 assigned to audit. It assumes #220's adoption (a): the merge evidence stays full, so
this phase re-observes at the audit's head what every merge observed at its own. Under adoption (b), where
the evidence narrows, it is the only full run left. The play-book is the same under both; its weight is not.
Seconds are one machine's (#204 section 0): the record states the interpreter and, beside any absolute, a
ratio.

## Phase 2 — Fences (ungated)
A shipped fence can rot with no commit to the tree, so this phase runs on every invocation, the unchanged
tree's included (the reason `incident-hardening.md` gives its own phase 4). The `fences` step reads:
- **the guard registry as installed** — `dyad check --list` — with its line count and a digest, compared to
  the `**Fences:**` line of the newest record:

      **Fences:** registry <n> lines, sha256 <first 16 hex> · hooksPath <value>

  A guard that left the registry is a finding; a registry that grew is reported, not judged;
- **`core.hooksPath`** — a repo whose hooks are not enabled has no blocking Rule-1 enforcement (Rule-1);
- **the mode of every file git or the entrypoint runs by path** — `dyad/hooks/*` and `dyad/bin/*` — which
  must be `100755` (#24: a lost exec bit left a hook inert and the push gate vacuous).
A fence that cannot execute is a finding whatever the registry says.

## Phase 3 — Drift (detect only)
What moved since the newest record, read and never repaired. The `drift` step lists:
- **Rules edited since the last Rule-5 sweep.** A sweep is inference (Rule-5, Enforcement), so the step prints
  the date of the last commit to `dyad/rules/` and the newest sweep record in `<instance>/audits/`; the audit
  states the staleness and does not sweep.
- **Rows with no activity.** Every `open` and `planned` row, `blocked` rows, with the date of the last commit
  to its row file; the `backlog` count.
- **Presence files** past the stale window (`dyad session list`, Rule-16): reported, never guards.
- **Unmerged remote branches** (`git branch -r --no-merged`): the pruning question of #43, asked as a list.
- **Host documents older than the running kernel** (the frame's convention) are read only on the host that
  keeps them. Anywhere else the record says "unobserved" and names the host path: an audit does not read a
  document about a machine it is not on and call it verified (Rule-8).

## Phase 3b — Incidents
The incident log is read here and worked by `incident-hardening.md`: one owner per concern (Rule-5), so this
phase ingests, sizes and surfaces, and never groups. The `incidents` step:
- **Ingests** the log through its one parser, `dyad/scripts/incidents.py` — `parse`, `check_log` — and not by
  counting lines: the shape verdict, the row count, rows per month, and the d-works that carry two or more
  rows.
- **Runs hardening's `survey`** (`dyad runbook run incident-hardening survey`), which compares the live row
  count to the watermark of the newest index audit. The **delta** is the rows past that watermark.
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
Done-`Y` of the d-work that ran the audit disposes it); then, in order: the regression block verbatim, fences,
drift, incidents, **findings**, **proposed rows**, **not observed**.

Each finding is a claim and is falsified before it is written (Rule-9, trigger "an audit surfaces a claim"):
what was tried against it, and its result — confirmed, refuted, or survives scoped — in the d-work's
falsification record. A claim a command's observed line does not carry is marked inference. A reference the
record states resolves cites the guard's line, or says the kind is unresolvable (Rule-20, trigger). **Proposed
rows** are candidate d-works with the evidence each would carry, in Rule-3's intake shape; a candidate is a
row-shaped entry and never a paragraph, because a candidate with no row is the failure `incident-hardening.md`
exists to prevent. **Not observed** says what the audit could not read and why. The `record` step tests that
the newest record carries both watermark lines.

## Conduct
The audit detects and sizes; it disposes nothing (frame: detect, don't dispose; Rule-2: the Agent proposes). It
changes no Rule and no code, opens no row and closes no mode and no row: the Operator's prompt or disposition
opens a row, and a finding is "proposed, not opened" until then. Every run-book command is read-only. The first
exercise on a system is a baseline for the next watermark, and a record of what ran, not a verdict on this
play-book: the session that authored it and the session that first ran it were the same (no-self-ratify,
Rule-2; the Operator's Done-`Y` disposes both).
