# Play-book: incident hardening (core craft, `dyad-operator`; #137, #626)

Given an incident ledger, which failure modes it holds and which mitigation of a mode is worth building next. Read by
Rule-3's Incidents clause. Steps: `dyad/runbooks/incident-hardening.md` — `survey`, `group`, `inventory`, `plan`,
`execute`, `verify` — run as `LEDGER=<path> dyad runbook run incident-hardening <step>`.

## Parameter
`LEDGER` — the ledger to harden; default `agent-corpus/audits/INCIDENTS.md` (`DYAD_INSTANCE`, Rule-11 property 3).
Steps that read the system take none. The records it writes go beside the ledger. A peer's log is hardened only once
it is here, as an intake (Rule-3).

## Trigger
An operator prompt asking for the exercise, or a d-work finding the ledger grown past the watermark (Phase 0), which
it states as a finding and opens nothing for (Rule-3 Scope). The phases are planned in that d-work's plan file first.

## Steps
### Phase 0 — Survey (the idempotence gate)
`survey` runs `dyad/scripts/audits.py hardening [<ledger>]` against the newest index audit's watermark,

    **Ledger:** `<LEDGER>` · **covered through:** <n> rows, latest <YYYY-MM-DD>

which decides the run (`dyad/dmc/hardening-survey.jsonld`); the automaton sweep's `sweep_audit` part runs the same
check after each landed merge (#619). A full re-derivation runs on the operator's word, or when a new row's mechanism
is named by no existing mode. Phase 4 is never gated.

### Phase 1 — Group
`group`: one failure mode per row (vocabulary), its mechanism by `dmc:failure-mode-primary`, re-derived from the
ledger each exercise, never read off the previous index. Output: an index audit in `audits/` with the watermark line,
the population, and the mode table, whose last columns code reads — `exit` (`1`, `2`, `3` or `—`), `fence row`
(`#<id>` or `—`), `fence` (backticked `<path>`, `<path>:<name>` or registry labels, or `—`); one record per mode
(definition bounded against its neighbours, incidents by date and d-work, the pattern, one candidate under attack);
one child d-work per mode, `refs: parent #<id>`.

### Phase 2 — Plan
`inventory`: each live mitigation of a mode, read from the code and the Rule text, never from an audit's prose — by
path and identifier, the moment it fires, the incidents it reaches and misses, its status by `dmc:mitigation-status`,
and any recurrence after it shipped. `plan`: falsify "this mode is addressed" (Rule-9) in a record beside the
instance's others; only survivors go on.

### Phase 3 — Execute
`execute`: each survivor under its own plan-`Y`, on that mode's child d-work, one zone per PR (Rule-1).

### Phase 4 — Verify
`verify`: `dyad check --list; dyad automaton sweep`, whose report resolves every fence row and fence. Then re-group
the rows since the last exercise and test each shipped mitigation against its incidents at the moment it fires. A
mode closes only by `dmc:mode-exit`; the exit-2 row is carried under the plan-`Y` that runs the exercise (Rule-3
Plan, #574).

## Standing mandate
Under the preference `hardening-mandate: on` a carried row is worked without its own intent and plan questions when it
is hardening work by `dmc:hardening-work` and due by `dmc:hardening-due`: the home opens it with `dyad dwork state <id>
open --mandate-preference hardening-mandate`, which refuses a row whose source is not a hardening or audit run, and one
past the ceiling, before any write, and tells the operator in one notice line. Its Done is always asked, batched with
others ready (Rule-3 Batch disposition), naming the incident that made it due. Under `off`, or for a row either record
does not admit, the row waits for promotion and is asked as any other.

## Question
Each child's plan question and the parent's Done, as Rule-3 asks them. The exercise proposes the mode set, each
survivor and each closure; it never adopts a candidate on its own judgment or closes a mode by asserting it.

## Evidence
The index audit and its watermark, every mode with its exit, every carried `backlog` row, and each survivor's PR.
