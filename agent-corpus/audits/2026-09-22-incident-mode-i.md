# Incident mode I — external environment

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #125, child of #116 (2026-09-22).*

## Definition
Mode I names a departure whose mechanism is a condition of the machine or of a service outside
The Dyad System — the host's memory and CPU, another process on it, a hosted runner — observed and
never pinned (Rule-14 property 4, *The World*). Its signature is non-reproduction: the identical
command against an identical, unchanging tree gives a different result, or the run is ended by
something that is not the run.

Boundary against the three modes it is most easily confused with:
- **G (mechanism defect)** — a hook, guard, CLI or suite not doing what its design says. G
  reproduces on an unchanged tree wherever it runs; I does not. The separating test is #48's own:
  a 2-fail run and a 0-fail run of the same command, seconds apart, with no tree change between.
- **D (wrong cause asserted)** — a diagnosis stated as fact and then retracted. An external cause
  can sit underneath a D row and the row still belongs to D: the `HTTP 403: Resource not accessible
  by integration` on `v0.3.2` (2026-09-14–15, #13/#16) is hosting-side, yet #116 places it in D
  because the mechanism of that incident is the asserted-then-refuted cause, not the hosting. I
  claims only rows where the external condition is itself the mechanism and no cause was retracted.
- **B (stale local view of the remote)** — also looks environmental, but the fault is a local ref
  the Agent could have refreshed and did not. In I nothing under the Agent's control changes the
  outcome.

## Incidents (1)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #48 | `dyad/tests` showed 2 failures on the v0.6.0 release CI run and on one local fresh-clone run of the identical, unchanging tree; a second identical run showed 0; two further attempts were killed by the OS for low memory, at two different, unrelated stalled tests. `free`/`ps` during both kills showed large swings in available memory; the host carries several concurrent `claude` CLI sessions, a local vLLM inference server and heavy browser use. No corpus defect found, no code change made; a third confirmation run was not attempted, two OS kills having already cost a shared machine real disruption. | The two OS kills landed on two unrelated tests (`test_evidence_block_deterministic` and `test_check_runs_and_reports_rules_and_guards`, both `test_package.py`, per `agent-corpus/d-work/plans/48.md`), which refutes one broken test; the 2-fail/0-fail pair on an unchanging tree refutes a deterministic corpus bug. What is left is the machine, not the corpus. |

## Pattern
One incident, and the count reconciles: plan #125 names one (#48), the index
(`2026-09-22-incident-failure-modes.md`) counts one, and re-reading `INCIDENTS.md` row by row finds
one — 34 rows at #116's base commit, 35 as the log now stands with the `--help` row #116 adds, which
is mode G. No row was added or dropped here. The other row with an external condition underneath it,
the `v0.3.2` 403, stays in D for the reason the Definition gives.

Row #48's d-work ran a full plan-and-evidence cycle — four runs of the identical command — and found
nothing to fix in the corpus: plan #48's Mutation section reads "None in `dyad/` or any craft — no
defect found to fix", and what its PR carried was two rows of this log (row #48's `disposed` records
`Y done (merges PR #37)`).

The condition the row names is a property of the machine #48 observed — several concurrent `claude`
CLI sessions, a local vLLM inference server, heavy browser use — and no later row records it
changing. The corpus's other mention of a local vLLM service is Rule-19's own falsification record
(`dyad/falsification/rules/rule-19-server-instances.md`, attack 8), where a pre-existing privileged
service enters the Rule only when a d-work touches it and whether to bring vLLM under Rule-19 at all
is left as open question Q3; that the two mentions name the same machine is not established anywhere
in the corpus. The mode has not recurred in the log in the six days since 2026-09-16.

Nothing in the corpus would surface a recurrence mechanically. No guard reads host load: no
`getloadavg`, `psutil`, `loadavg`, `meminfo` or `free -h` token appears anywhere under `dyad/` or
`crafts/`. The evidence block's sha256 is a function of its own lines and nothing else —
`dyad/tests/test_package.py`
`test_evidence_block_deterministic` asserts that `evidence_sha256` of the same lines is equal and
that adding a line changes it — which is what makes Rule-14 property 3's "re-run on the same head to
compare" work, and equally what keeps any load figure out of it. The one corpus item touching where
such a condition would be recorded at all is row #60, opened 2026-09-17 and still `backlog`.

## Remediation candidate (falsified, not disposed)
**Candidate (the null candidate, as plan #125 states it):** there is no corpus-side remediation —
mode I is recorded and counted so the log stays honest, and its remedy, if one is wanted, is
host-side under Rule-8 and belongs to whichever system tends this host.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A mode with no remediation should be dropped from the audit; carrying it pads the mode set. | Refuted | Dropping it hides a real cost — a full d-work spent, two OS kills on a shared machine — and makes #116's totals wrong. Kept, counted, with no mutation beyond this file. |
| 2 | A corpus-side remedy does exist: make `package.py check --evidence` carry host load (available memory, load average) so a contended run is visible in the merge evidence. | Refuted | Rule-14 property 3 has the Operator re-run the block on the exact head being merged and compare it with the one the completion reply pasted, the block carrying a sha256 of its own lines. A load line differs between two runs of one head, so the sha differs and the comparison Rule-2's Binding rests on is gone. What the suite fixes is narrower than "deterministic" but enough here: `dyad/tests/test_package.py` `test_evidence_block_deterministic` asserts `evidence_sha256` is equal over the same lines and changes when a line is added — and it is one of the two tests an OS kill stalled on in #48. |
| 3 | A conduct remedy costs nothing: before a test failure on an unchanged tree is written down as a corpus defect, re-run the identical command once and record both results. | Survives, scoped | Sound, but already owned: Rule-9's easy-agreement trigger requires one attack pushed to confirmed or refuted before a claim is accepted, and #48 did precisely this (runs 1 and 2) without any new rule. Scoped to "already covered"; nothing new to encode. |
| 4 | The plan's own path — "host-side, a workstation d-work if wanted" — is available, so the null candidate understates what could be done. | Confirmed | This instance has no `workstation-corpus/` tree at all (the zone exists in `containment.py`'s `ZONES`, the paths do not) and so no change log for a Rule-8 row to land in. Row #60 (opened 2026-09-17, `backlog`) names exactly this: "Rule-8 presumes every system has a host; a pure authoring system on a host another system tends has no clause for where its host actions (if any) are recorded", elevated from `agent-corpus/audits/2026-09-17-sysadmin-minimum.md` attack 3, whose own result records that the host here is the workstation system's. So the plan's host-side path names no place in this instance today. Recorded as the condition; which system takes it, and when, is not decided here. |
| 5 | n=1 is not a mode; #48 belongs in G, or nowhere. | Refuted | G requires a mechanism that does what its design does not. #48's two attacks refuted both candidates for such a mechanism — one broken test (two kills, two unrelated stall points) and a deterministic corpus bug (identical command, 2-fail then 0-fail). No G mechanism survives, so the row has nowhere else to sit. An independent pass reached the same place: row 24 of `agent-corpus/audits/2026-09-16-pydantic-schema-prevention.md` (d-work #56) classes #48 **C — out of reach**, noting it was "Diagnosed, correctly, as external interruption — explicitly not a corpus defect." |

The candidate survives as stated, with attack 4 scoping it: no corpus-side remediation, and the
host-side one has no recorded home in this instance — the gap row #60 already holds — rather than
being merely unwanted.

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #125 (Rule-9 Form). Remediation
itself is a further Operator prompt on this row, never taken here.
