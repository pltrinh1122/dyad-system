# Incident audit by failure mode — 2026-09-22

*Audit of `agent-corpus/audits/INCIDENTS.md` as of commit `c34c36d`. d-work #116, parent of the
nine per-mode records #117–#125. Detects and counts; disposes nothing (frame: detect, don't
dispose).*

## Method
Every row of the incident log was read and assigned one **observed failure mode**: the mechanism
by which the departure happened, not the Rule it breached and not the harm it caused. The mode is
the thing that would have to change for the incident not to recur. Where a row carries two
mechanisms, the one that *started* it is primary and the other is named secondary in that mode's
own record (for example #80: an unfetched ref is the primary, the wrong cause asserted on top of
it is the consequence).

## Population
34 rows, 33 incidents: the #47 merge-before-Done-`Y` incident is logged twice — once at the time
and once again under #68, when #47's own PR had been closed before it could carry the row. Counted
once. The duplicate is named here rather than deleted: rows are the record.

One further incident occurred while this audit was being opened (mode G, below), giving **34
incidents** across **9 modes**.

| mode | observed failure mode | count | d-work | record |
|------|----------------------|------:|--------|--------|
| A | acting before the Operator's `Y` | 9 | #117 | `2026-09-22-incident-mode-a.md` |
| G | mechanism defect | 6 | #123 | `2026-09-22-incident-mode-g.md` |
| B | stale local view of the remote | 5 | #118 | `2026-09-22-incident-mode-b.md` |
| F | form error in a clerical record | 4 | #122 | `2026-09-22-incident-mode-f.md` |
| C | concurrent-session race | 3 | #119 | `2026-09-22-incident-mode-c.md` |
| E | plan content wrong | 3 | #121 | `2026-09-22-incident-mode-e.md` |
| D | wrong cause asserted, then retracted | 2 | #120 | `2026-09-22-incident-mode-d.md` |
| H | fence collision not surfaced | 1 | #124 | `2026-09-22-incident-mode-h.md` |
| I | external environment | 1 | #125 | `2026-09-22-incident-mode-i.md` |

Each mode's record holds its definition, its incidents with dates and d-work ids, the pattern
across them, and one remediation candidate with its attacks. The candidates are surfaced for the
Operator; adopting any of them is a further prompt on that row.

## Mode definitions
- **A — acting before the Operator's `Y`.** A mutation, a merge, a host action or a recorded
  disposition ran before the counter-prompt that authorizes it was asked or answered. Includes the
  case where the counter-prompt itself was asked before the row and plan file existed.
- **B — stale local view of the remote.** A conclusion drawn, or a branch cut, from a ref that had
  never been fetched, or from a local ref that had fallen behind the remote.
- **C — concurrent-session race.** Two sessions on one instance, with indistinguishable presence
  identity or independently allocated ids, colliding on a row, an id or a file.
- **D — wrong cause asserted, then retracted.** A diagnosis stated as fact rather than hypothesis,
  acted on, and later refuted by evidence.
- **E — plan content wrong.** The plan named a path, a zone, a precedent or a sequence that did not
  hold when the plan was executed.
- **F — form error in a clerical record.** A row, commit message or staging step written in the
  wrong shape or the wrong order, failing a guard that reads it.
- **G — mechanism defect.** A hook, guard, CLI or suite did not do what its own design says.
- **H — fence collision not surfaced.** The corpus-legal half of a fenced action was done and the
  "state the rest and ask" half was omitted (Rule-1's #23 case).
- **I — external environment.** Resource contention or interruption from outside the dyad.

## What the counts say
Modes A, B and C together are 17 of 34 — exactly half the log — and all three are **ordering
faults against something that already existed**: a `Y` not yet given, a remote not yet read, an id
not yet printed. Content faults (D and E, 5 incidents) are the minority; mechanism defects (G, 6)
are the second-largest single mode and the only one with an occurrence in this audit's own d-work.

Mode A is the largest single mode and the most stubborn. It has recurred after every remedy so far:
a memory-cache note (#58 then #67 within the hour), then a Rule-3 Completion bullet (#68, followed
by #92/#103/#104 and #110 in two different sessions). Both remedies were conduct. The one
structural change shipped against it is #113's delegation fence — a subagent may not commit, push,
merge or ask — which is too new here to have been measured. #117 holds the mode's own record.

## Coverage — incidents known but never logged
Listed so the count is honest about what it is a count *of*. These are not included in the 34:
- Four drifted releases (#61, #67, #71, #90) recorded only as Rule-11's amendment #91 in
  `dyad/falsification/rules/rule-11-distribution-structure.md`, never as incident rows.
- The literal `;` in a row's `disposed` text, five occurrences across #47/#48/#49, #67 and #100,
  held only in the per-machine memory cache (mode F in kind).
- The three releases batched under one `Y` earlier in this session: the substance became Rule-11's
  release-batch form (#106) and the incident row was drafted but never landed, because `prs.py`
  refuses an incident-log PR citing a `done` d-work and no open row was available to cite at the
  time.

That last one is itself a finding about the log: an incident discovered during clerical work has
no home until some other d-work opens, so the log under-counts late-discovered incidents by
construction. Rule-3 Incidents says such a row is written "in the next agent-zone PR"; nothing
carries it if none is opened.

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #116 (Rule-9 Form). The nine
per-mode records are disposed by their own Done-`Y`s, #117–#125.
