# Incident mode F — form error in a clerical record

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #122, child of #116 (2026-09-22).*

## Definition
Mode F names a write whose content was right and whose authorization was already in place, but
whose **shape, order or staging** was wrong: a ledger row committed in a state a row may not be
born in, a disposition string in a form the parser re-reads, a file not staged when the check that
reads it ran, a commit message using a phrase a guard reserves. The artifact is clerical — a row,
a commit message, a staging step — and the departure is in how it was written, not in what it said.

Boundaries against the modes it is most easily confused with (letters as #116 assigns them):

- **A, acting before the Operator's `Y`.** A's fault is a missing authorization; every mode-F
  record was authorized. #18's `dwork state 18 planned -d "Y plan"` is the same command as #1's and
  is mode A, because no `Y` existed to record.
- **G, mechanism defect.** In all four F rows the mechanism did exactly what its design says: the
  main fence refused a row added outside `dyadlib.NEW_STATES`, `agent/references` refused an
  unresolvable path, `agent/prs` refused an id the ledger does not hold. G is the tool
  misbehaving (`--help` taken as a positional path); F is the tool behaving and refusing a bad write.
- **E, plan content wrong.** #17 owns one row in each mode. E's row is the plan naming a wrong
  record path and grouping two zones in one PR item; F's is the correct file not being staged when
  the suite ran. E is what the plan said, F is how the artifact was written at execution.
- **C, concurrent-session race.** #27's provenance written as `26.md` reads like a naming-form
  error, but its mechanism is an id assumed before the allocator printed it, so it is C.

## Incidents (4)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14 | #1 | ledger row #1 committed already in state `planned` (main-fence FAIL); its `-d` disposition text carried a doubled date | `dwork new` then `dwork state … planned` in one commit, so the row's first committed appearance skips `open`. State and disposition were both authorized; only the shape of the write was wrong |
| 2026-09-14 | #16 | ledger row #16 committed already in state `planned` (main-fence FAIL) — same pattern as #1's | the identical sequencing, repeated. The log records no new cause: the first occurrence left nothing behind that could refuse the second |
| 2026-09-15 | #17 | the new falsification-record file was uncommitted when the scratch-install test suite first ran; `agent/references` failed to resolve it from the scratch copy (3 test failures) | the file's content was correct and named in the plan; `git add` came after the run instead of before. A staging-order fault, not a content fault |
| 2026-09-16 | #15 | commit `e74f3a2` (PR #36) wrote the `d-work #<id>` form naming 141 in prose as precedent; `prs.py`'s citation scanner read it as a claim of work on a row this ledger does not hold, and the merge evidence FAILed with `agent/prs [d-work]: #141 not in ledger` | Rule-3 Ledger reserves `d-work #<id>` for a claim of work and requires a bare `#<id>` for a cross-reference. The message said the right thing in the reserved form |

## Pattern
All four wrote correct, authorized content in a wrong shape or a wrong order, and all four were
caught by a mechanism that already existed — the main fence twice, `agent/references` once,
`agent/prs` once — never by the Agent noticing first. What varies is the artifact and the cost of
the rework: local commits reset and rewritten (#1), commits split before push (#16), the suite
re-run after staging (#17), a branch commit amended and force-pushed under the Operator's explicit
`Y` (#15). Nothing of mode F reached `main` mis-shaped; the whole cost is rework. The most recent
primary occurrence is 2026-09-16 (#15); #67's 2026-09-18 row carries three further form errors as
secondary under mode A3 — a row that cannot be born `planned`, a `;` splitting disposition text,
and the gate needing a literal `Y plan`. As the code stands today, `dyad dwork new` writes a row
only in `open` or `backlog` (`dyadlib.NEW_STATES`, `package.py` `cmd_dwork`) and the pre-push
kernel-only path runs `agent/prs` over `origin/main..HEAD` with the commit messages as body
(Rule-3 Mechanisms), which would fail #15's commit before the push rather than at merge evidence;
whether either mechanism postdates these four rows is not attested anywhere in `INCIDENTS.md` or
the plans, so no change *since* them is claimed here. Neither removes the `new` + `state … planned`
pair in one commit, which `dyad dwork state` still accepts.

## Remediation candidate (falsified, not disposed)
The candidate moves the refusal from the fence to the command: `dyad dwork state` would refuse a
transition on a row file whose creation is not yet committed — the row would be born outside
`dyadlib.NEW_STATES` — and `dwork state -d` would reject a `;` in the disposition text. Two of mode
F's four incidents (#1, #16) are the first defect; the second addresses the `;` recurrence #67's
row records.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | `rows.py` already refuses a row added outside `NEW_STATES` and did refuse both #1 and #16, so the candidate adds no enforcement | survives-scoped | The fence refuses after the commits exist: #1's consequence was "local commits reset and rewritten", #16's "commits split into open/plan-Y before push". The candidate refuses before the commit and replaces nothing; both stand, and the candidate is stated as rework avoided, not as a new gate |
| 2 | A ledger command that reads git stops being a pure file operation and breaks where the repo is unusual — a fresh install with no resolvable `HEAD` | refuted | `dwork new` already runs `git fetch -q origin main` and degrades to a printed warning when it cannot (`package.py` `cmd_dwork`). The candidate inherits that: warn and proceed when `HEAD` does not resolve, refuse only on a definite answer |
| 3 | A command-level refusal is bypassed by editing `rows/<id>.md` by hand | confirmed | Not contested. The candidate is ergonomics, never enforcement: `rows.py` on `main` stays the only fence and the stores rule's no-hand-edit discipline is unchanged |
| 4 | The `;` clause is not attested by any mode-F row. `INCIDENTS.md` carries the `;` defect once, inside #67's 2026-09-18 row, whose primary mode #116 assigns to A3 | survives-scoped | The clause is separable and rests on that row plus the memory cache's recurrence note. Plan #122's "five occurrences" (via #116: #47/#48/#49, #67, #100) is **not supported by the log** and is not verified here — those rows' own `disposed` cells carry no `;` inside text, being the corrected form. Dropping clause 2 leaves clause 1 intact |
| 5 | Mode F may already be closed: no primary occurrence in six days, and `dwork new` cannot write a `planned` row | survives-scoped | `dwork new` was never the path — both #1 and #16 came from `new` followed by `state … planned` in one commit, which `dwork state` accepts today, its transition check reading the file's current state and not its committed one. The mode is quiet, not mechanically closed |
| 6 | The candidate leaves the doubled date, the second of #1's two form errors, untouched: `dwork state -d` prepends the date itself, so an Operator-supplied date doubles | confirmed | Named as a gap, not remediated. Plan #122's candidate has two clauses and widening it is a new plan; the same `-d` text path on `dwork new` is likewise outside it |

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of its d-work — see ledger #122 (Rule-2,
Ratification events: a falsification record or audit is disposed that way and is not a separate
ratification event). Remediation itself is a further Operator prompt on this row, never taken here.
