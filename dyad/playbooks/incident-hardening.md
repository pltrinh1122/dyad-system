# Play-book: incident hardening (core craft, `dyad-operator`; #137)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for
a recurring decision; its steps are a run-book. This one decides, given an incident ledger, which
observed failure modes that ledger holds and which mitigation of a mode is worth building next — the
decision the last three exercises made by hand and differently each time (#116 the grouping, #128 the
inventory and its falsification, #135 the kinds of mitigation). Read by Rule-3's Incidents clause.
Steps: `dyad/runbooks/incident-hardening.md` — `survey`, `group`, `inventory`, `plan`, `execute`,
`verify`, one per phase and two for phase 2 — run through `LEDGER=<path> dyad runbook run
incident-hardening <step>`, the core runner, so each step leaves an event. The exercise is periodic
because the system it hardens keeps mutating: every new guard, Rule clause and craft is new surface
for a new mechanism of failure, and reliability and resilience are properties of the fences built
from the log, never of the log itself.

## Parameter
`LEDGER` — the incident ledger to harden; default `agent-corpus/audits/INCIDENTS.md`, the audits of
the default instance location (`DYAD_INSTANCE`, Rule-11 property 3: paths printed here are the
defaults). The run-book's ledger-reading steps take it from the environment, exactly as `dyad/runbooks/craft.md`
reads `CRAFT`; the steps that read the system rather than the ledger — the guard registry, the rows,
the evidence path — take no parameter:

    LEDGER=<path> dyad runbook run incident-hardening survey

The parameter is what makes this core-craft content rather than one instance's procedure: the same
exercise runs against another system's incident log, or against a craft's own, with no edit to this
file. The records it writes go beside that ledger, in the same instance's `audits/`.

Boundary: the path names a ledger inside the running system's own tree. Hardening a peer's log means
having that log *here* — which is an intake (Rule-3, Intake: a defect is admissible as an observation
with evidence, and the Operator's `Y` opens the row), not a cross-repository write. Stated as a
boundary rather than enforced: no guard reaches another repository.

## Trigger
An Operator prompt asking for the exercise, or a d-work that finds the parameter ledger has grown
past the watermark the last index audit recorded (Phase 0). The play-book runs inside the d-work the
prompt opened, and its phases are planned there, in that d-work's plan file (Rule-15 phase 1), before
any record is written; a d-work of another kind that notices the growth states it as a finding and
opens nothing, since a d-work opens on an Operator prompt or disposition and never on the Agent's
own finding (Rule-3, Scope).

## Phase 0 — Survey (the idempotence gate)
The watermark is one line the index audit of phase 1 carries:

    **Ledger:** `<LEDGER>` · **covered through:** <n> rows, latest <YYYY-MM-DD>

Survey derives the live row count and latest row date of `LEDGER` and compares them to the watermark
of the most recent index audit naming that same `LEDGER`. Three outcomes, and only the third derives
anything new:
- **No index audit names this ledger** — the first exercise on it: full derivation, phases 1 to 4.
- **Live count equals the watermark** — a no-op for phases 1 to 3: the survey step prints both
  numbers and the exercise stops there, opening no d-work and writing no file.
- **Live count exceeds the watermark** — the exercise runs on the delta: only the new rows are
  classified, only the affected mode records are updated, and the watermark advances. A full
  re-derivation happens on the Operator's word, or when a new row's mechanism is named by no existing
  mode — the tenth-pattern case (`agent-corpus/falsification/incident-gaps-addressed.md` attack 7,
  #128), which this play-book must keep able to happen.

The gate is the watermark and not a clock. Time alone cannot make an unchanged ledger worth
re-reading, and a ledger that grew an hour ago is worth reading whatever the interval; a minimum
interval would add a second, weaker gate carrying its own failure mode — a fresh incident ignored
because the calendar said no. The watermark is only ever compared, never believed: the live count is
derived from `LEDGER` at survey time, so a hand-edited audit is caught by the comparison rather than
trusted through it.

**Phase 4 is not gated.** A shipped fence can rot without any new row being logged, and a no-op that
stopped the whole exercise would hide exactly that. An invocation on an unchanged ledger is therefore
not "do nothing" but "re-verify the closed modes' fences and report": it writes no file when every
fence still holds, which is what `0 changes` means here — the shape
`crafts/syseng/rules/idempotence.md` property 1 already sets for the install.

## Phase 1 — Group
One **observed failure mode** per row of the ledger (`failure mode`, vocabulary): the mechanism that
would have to change for the incident not to recur — never the Rule it breached, never the harm it
cost. Where a row carries two mechanisms, the one that *started* it is primary and the other is named
secondary in that mode's own record (#116's own answer to this, carried forward rather than
re-litigated).

Output: an index audit in the instance's `audits/`, carrying the watermark line above, the population
it read and the mode table; plus one record per mode holding that mode's definition — bounded against
the neighbouring modes it is most easily confused with, as #116's own records are — its incidents by
date and d-work, the pattern across them, and one remediation candidate under attack (Rule-9). One
child d-work per mode, `refs: parent #<id>` (Rule-3, Ledger): the parent's completion counter-prompt
is asked only when every child is `done` or `blocked`, and the parent completes only on its own
Done-`Y`.

The modes are re-derived from the ledger each exercise, never read off the previous index. The
taxonomy is not closed: #128's attack 7 found a tenth mechanism the nine modes of #116 do not name,
one day after the index was written. Reading the previous index's list as the mode set would have
made that row unclassifiable or, worse, filed under the nearest wrong mode.

## Phase 2 — Plan
For each mode, inventory every live mitigation of it **from the code and the Rule text, never from an
audit's prose**. Per mitigation: what it is, by path and identifier (a guard module and the function
that checks, a Rule clause by name, a hook, a preference key); how and at which moment it fires
(`dyad/hooks/pre-commit` at commit time, `dyad check --guards` before a push on the kernel-only path,
`package.py check` in the runner, the plan gate `dyad/guards/agent/prs.py` over the commits being
pushed, a counter-prompt in the reply, or inference at plan time — stated as inference where it is
one); which of the mode's incidents it reaches and which it does not, row by row; whether it is
**shipped** (in the tree today, verified by reading it) or still a **candidate** (surfaced in a mode
record, never implemented); and whether anything of that mode recurred *after* it shipped — the
recurrence is the measurement, and it is evidence about that mitigation, not about the mode.

Then falsify the claim *this mode is addressed* (Rule-9), in a record beside that instance's others
(`agent-corpus/falsification/`, Rule-9 Form; the default instance location, Rule-11 property 3): an
attack per mitigation and per gap between the mitigations and the mode's own rows, each pushed to
confirmed, refuted or survives-scoped — and where the Agent agrees with a mitigation on first reading,
one attack pushed to confirmed or refuted before it is accepted (Rule-9 Conditions, easy agreement).
Only survivors reach phase 3.

## Phase 3 — Execute
Each survivor is executed under its own plan-`Y` (Rule-3, Plan), carried by that mode's child d-work
and stored as that d-work's plan file (Rule-15 phase 1) before the counter-prompt is asked. One zone
per PR (Rule-1): a guard and its test are agent zone, its workflow wrapper infra, a craft's rule the
craft zone, a preference its own — so one survivor may be several PRs of one child row, never one PR
across zones. A survivor the Operator declines stays a candidate, and is written back into the mode's
record as declined, with the date.

## Phase 4 — Verify
Re-group the rows logged since the last exercise (phase 1 over the delta), and test each shipped
mitigation against the incidents it claimed: name the moment it fires, and state whether a fault of
that shape presented at that moment would now meet it. Ungated by the survey, for the reason Phase 0
gives.

A mode closes by exactly one of three exits, and by no other means:
1. **Fenced at a named moment** — a mechanical check that would catch a fault of the mode, named
   together with the moment it runs.
2. **A `backlog` row that names the fence to build** — the fence does not exist, but the row does, and
   the row names what would be built and which incidents it would have caught.
3. **Recorded unfenceable on this kernel**, naming the Rule that makes it so — Rule-14 property 2 for
   a fault that lives in a hosted service the kernel never contains (a hosted git service is never
   kernel), Rule-5's Enforcement for a judgment no script can decide (it says so of coherence and
   orthogonality).

A mode holding none of the three is open, whatever its record says about it, and stays in the index
as open.

## Conduct
The play-book decides and records; it never disposes (frame: detect, don't dispose; Rule-2 — the
Agent proposes). Every phase's output is proposed to the Operator: the grouping and the mode set at
phase 1, each survivor at its plan-`Y` in phase 3, each closure and each exit taken at phase 4. The
Agent never adopts a remediation candidate on its own judgment, and never closes a mode by asserting
it addressed.

A candidate with no row is the failure this play-book exists to prevent. Plan #137's attack 3 — that
the previous exercise produced nine mode records and zero fences (#116, then #128's inventory) — is
**confirmed**, and it is the reason phase 2 reads the code rather than the prose and phase 4 admits
only three exits. The play-book cannot make the Operator dispose; it can make an undisposed candidate
visible as a row instead of a paragraph.
