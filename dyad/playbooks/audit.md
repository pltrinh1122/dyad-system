# Play-book: audit (core craft, `dyad-operator`; #223, #619, #626)

The standing audit: the topic-free, whole-system pass, run on an operator prompt, that detects and sizes and disposes
nothing. Its steps are `dyad/runbooks/audit.md` — `report`, `hooks`, `host`, `record` — run as `dyad runbook run audit
<step>`. Every coded check is the automaton sweep's (`dyad automaton sweep`, Rule-14 property 3): the audit reads its
report and judges each line, and no step re-runs a check the report carries. Beside it, the self-diagnostic (below),
whose steps are `dyad/runbooks/self-diagnostic.md`. Owners per phase are the domain units' (#433): Phase 1 engineer's,
Phase 2 and 3b audit's, Phase 3 per item, the self-diagnostic's coded-check levels engineer's and its prose-claim
levels counsel's. A topic review the operator asks for is its own prompt and plan.

## Trigger
An operator prompt asking for the audit, or the sweep's due state by `dmc:audit-trigger`, which the home presents as
that record weighs it; no Rule requires it. Either way only the operator's `Y` opens the audit row, and it runs inside
that d-work, planned there first (Rule-15). No clock is the gate: the due state is read from the full sweep's lines after
each landed merge (`audits.py`, the `audit due` line) and by the home when it lands a release; Phase 0's watermark decides
whether there is anything to read, and between audits the sweep tells the home each new finding after the merge that
made it.

## Steps
### Phase 0 — Survey (the gate)
Run `report`: `dyad automaton sweep` on `main` with no `--row`, which lands and posts nothing and stores its text at
`<git common dir>/dyad-sweep/<report-sha256>.txt`. Its `reading: audit watermark` line compares the live watermark with
the newest record's:

    **Audited:** tree <hash> · python <v> · git <v> · covered through <sha>, <YYYY-MM-DD>

`tree` is the code tree (Rule-14 property 3) minus the dated audit records `<instance>/audits/<date>-*.md`. The gate is
`dmc:audit-watermark`, read from that line and never computed again; on an unchanged watermark phases 1 and 3 are a
no-op, no file is written, and Phase 2 still runs.

### Phase 1 — Regression (in the report)
The suite, every root, observed on `main` in the report, never from a memo (Rule-12 property 2); `dyad check
--evidence` is not run here. Judge each red line: a regression, a check the merge evidence should have caught, or an
environment change, and state which.

### Phase 2 — Fences (ungated)
Runs on every invocation. Read the report's `reading: audit fences` line (registry line count and digest against the
newest record's) and the `syseng/naming` line (`dyad/hooks/*`, `dyad/bin/*` mode `100755`). Run `hooks`: it reads
`core.hooksPath` in the auditor's own checkout, which the hosted sweep cannot see, and its value goes into:

    **Fences:** registry <n> lines, sha256 <first 16 hex> · hooksPath <value>

Judge each line by `dmc:audit-fences`.

### Phase 3 — Drift (detect only)
Read, never repair: Rules edited since the newest `<instance>/audits/<date>-rule-sweep.md` (the report's `audit drift`
finding; counsel); rows with no activity, from the stall block, and the `backlog` count (program); stale presence
files, `reading: presence` (operate); unmerged remote branches, `reading: branches`, asked as one list (program); host
documents older than the running kernel, through `host`, on the host that keeps them only, else "unobserved" (operate).

### Phase 3b — Incidents
The report carries the ingestion through `dyad/scripts/incidents.py` (`reading: incidents`) and hardening's survey
(`reading: hardening`, a `hardening` finding when rows lie past the watermark). State the delta and whether
`incident-hardening` ran since; a delta with none behind it is a finding, with "run `incident-hardening` on the delta" a
proposed row. It also carries **promised incidents not logged** (#651): each incident a cabinet's board `promised`
line still holds (an entry opening `incident`), so not yet a row of `INCIDENTS.md`, one `finding: audit: incident promised, not logged (<file>): <first
words>` line apiece, and their count, `reading: incidents promised on the board, not logged: <n>`. A board line is no
log (Rule-3 Incidents), so each is a finding, with "log the promised incidents in the next agent-zone PR" a proposed row.
Does not classify: failure modes, mitigations and child rows are `dyad/playbooks/incident-hardening.md`'s.

### Phase 4 — Record
Only when Phase 0 found something to read: `<instance>/audits/<date>-audit.md` — the title, the two watermark lines,
`Disposition:` by reference to the d-work (Rule-2); then the report's mechanical section verbatim, cited by
`checks-sha256` and `report-sha256`; then fences, drift, incidents, findings, proposed rows, not observed. Each finding is
falsified before it is written (Rule-9); a reference stated to resolve cites the guard's line (Rule-20); a proposed row is
row-shaped, in Rule-3's intake shape. Run `record`, which reads the new record's two lines back through the report's own
check of the newest record.

## Question
None. The audit opens no row and closes none: a finding is proposed, not opened, until the operator's prompt or
disposition opens it; a branch deletion it proposes is its own question (Rule-8).

## Evidence
The record above, its `report-sha256`, and the run-book events of each step.

## The self-diagnostic
A gated, budgeted run over four levels, two kinds of check at two scopes — a coded check and a prose claim with its
attack (Rule-12) — whose steps are `dyad/runbooks/self-diagnostic.md` and whose record is
`dyad/falsification/countersign-self-diagnostic.md` (C1–C6, D1–D25). It shares with the audit only the report on `main`
(D15); a diagnostic record's dated name falls outside the audit's watermark.
- **Levels**: `dmc:diag-level`, coded before prose and unit before system, each gating the next. The coded-check levels
  class the report's failing tests by the levels file (`audits.py level`) and read its check lines and its
  `checks-sha256`; the prose-claim levels read K units' contracts against "name a contract clause whose breaking no
  invariant and no test would catch", and the fixed system claims S1–S11 with their attacks (the run-book's Level 4),
  then the instance's own.
- **Gate and result**: `dmc:diag-result`; nothing is repaired inside a run. A run ends after a given level on request.
- **Budget and rotation**: K units (default 4) and P samples (default 3) per run; each record's `**Cursor:**` line names
  where the next run starts, wrapping, so every unit is read once in ⌈n/K⌉ runs.
- **Findings**: `dmc:diag-finding-route`; a clause or claim read the same way on two runs is judged by
  `dmc:codify-candidate`.
- **The levels file**: `<host>/self-diagnostic-levels.txt`, `<level> <path>` per line, seeded by hand from
  `dyad/templates/self-diagnostic-levels.txt`; each module classed by `dmc:diag-levels-file`; checked complete by
  `dyad/scripts/levels.py`, in the sweep's `sweep_audit` part, skipping when the file is absent.
- **The record**: `<instance>/audits/<YYYY-MM-DD>-self-diagnostic.md`, one per UTC day, holding
  `**Diagnosed:** head <sha> · K <k> · P <p> · checks-sha256 <value>`, one `**Result:**` line per level, the L3/L4
  tables `claim | attack | result | codify?`, and `**Cursor:** units=<path> rows=<id> pairs=<a>-<b>`. The run's events
  land first, then the record that cites them (Rule-1). `/diagnose [level]` (`dyad/templates/commands/diagnose.md`) is a
  command adapter that follows this section and the run-book.
- **Inference, stated**: the prose-claim levels detect and never prove (D1); a system diagnosing itself is circular, so
  anyone may re-run the sweep on the same head and compare `checks-sha256` (D4); S2 and S4 are read over the session
  that runs the diagnostic only (D23).
