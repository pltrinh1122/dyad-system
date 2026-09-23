# Incident mode D — wrong cause asserted then retracted

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #120, child of #116 (2026-09-22).*

## Definition
Mode D names one mechanism: a causal diagnosis written as fact — in a plan, an incident row or a
completion reply — acted on before any observation separated it from its leading alternative, then
refuted by later evidence. The fault is the inference, not the input. In #6 the observation
that would have discriminated was reachable when the cause was written; in the 403 it was not —
that cause is still "not yet known" (`INCIDENTS.md`, that row) — and what puts the row here is that
the diagnosis was stated as fact and built on before anything separated it from its alternatives.

Against **B** (stale local view of the remote): B's wrong conclusion follows from a ref that was
never read, so a fetch prevents it; D's follows from data already in hand. Where both are present
the unread ref started it and is primary — the parent audit files #22's `plan.base->commit`
misdiagnosis and #80's "no release exists" under B, with the wrong cause secondary.

Against **E** (plan content wrong): E is a claim about the corpus's own state — a path, a zone, a
precedent, a sequence — found false when the plan is executed, inside the d-work. D is a claim about
*why* something failed, refuted after action was taken on it, in both cases here by a party outside
the asserting session.

Against **G** (mechanism defect): G logs a hook, guard, CLI or suite behaving against its own
design. The 403 sits next to G because the release workflow does not publish, but that defect is
still undiagnosed and has no row of its own under G; what the log carries is the Agent's assertion
about its cause.

## Incidents (2)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14–15 | #13, #16 | The `v0.3.2` tag-push run and its re-dispatch both failed at the release step with `HTTP 403: Resource not accessible by integration`, despite the workflow's explicit `permissions: contents: write`. The cause was stated as the repo's read-only `default_workflow_permissions`. | The Operator changed that setting to `write` (confirmed via the API) and the identical 403 persisted; the row records the real cause as "not yet known". Nothing had been observed that separated the repo default from the other candidates before it was asserted, and the party who paid for the refutation was the Operator, acting on the Agent's diagnosis. |
| 2026-09-16 | #6 | The 108 tracked paths wrongly recorded `100755` were blamed on "`git add` of a new path on this mount records 755"; a residual hazard and a guard for it were then proposed on that cause at the d-work's close (the cause is stated in `plans/6.md`, Finding 2026-09-16, and acted on as its Mutation 3; that plan's Correction 2026-09-16 records the hazard as "reported at #6's close"). | Tested afterwards: under `core.fileMode=false` a new path records `100644`, and `git ls-tree 2dad9be -- dyad/CLAUDE.md` → `100755` shows them already present at the clone point — they came from the all-0755 `v0.3.1` archive extracted in the workstation#194 seed, one cause (`_mode()`) end to end. Both observations were available on the spot; neither was made before the cause was written, proposed on and merged. Retracted after workstation#212's observation with evidence; the false hazard was withdrawn, and PR #12/#13's commit messages carry the wrong cause, uneditable. |

## Pattern
Both causes were written as fact before any observation separated them from an alternative, and in
both the refutation arrived from outside the asserting session — an Operator configuration change in
one, a peer system's observation with evidence in the other. Both had already been built on by the
time they fell: an Operator-executed repo setting; a withdrawn residual hazard, a proposed guard and
two merged commit messages that cannot be edited. What varies is the residue — #6's cause was
replaced end to end, while the 403's was retracted with nothing put in its place, leaving backlog
row #20 ("every credential tried", `plans/19.md`) and `plans/21.md`'s note that the release step
still 403s. The corrective conduct did appear once, one d-work later and written nowhere as a rule:
`plans/18.md` names its next cause together with the experiment that would settle it ("falsified by
running it … either way it is observed, not assumed"). Whether that experiment ever ran is not in
the corpus: #18 was superseded before its PR merged (`plans/19.md` mutation item 2; `plans/43.md`,
"PR #8 closed, superseded by #19"), and what the log kept is the backlog row above. Most recent
occurrence 2026-09-16; nothing shipped since bears on how a cause is asserted — the 2026-09-16
schema-prevention audit classed both of these C, out of reach of the mechanism it was evaluating,
and Rule-9 predates both — so six quiet days over two incidents is too thin to call the mode
closed.

## Remediation candidate (falsified, not disposed)
Candidate: a cause written into a plan, an incident row or a completion reply is marked as a
hypothesis until the same row or reply names one observation that would have come out differently
under the leading alternative; where no such observation has been made, the cause says so. Conduct,
no mechanism; scope is the `cause` cell of `INCIDENTS.md`, a plan's stated cause, and a completion
reply's diagnosis.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | No guard can read a cause and tell a hypothesis from a fact. This is conduct, and conduct is what has already failed nine times in mode A, after a memory-cache note and a Rule-3 bullet. | Confirmed | Conceded and stated: no mechanism is shipped or proposed. What survives is narrower — the candidate's unit is an artifact, not a habit: the named discriminating observation, or the sentence saying none was made, is visible in the row to any reader, which a habit is not. Whether that is worth a clause is the Operator's to judge. |
| 2 | Rule-9 already owns this. A cause is a claim, the Agent falsifies a claim before it is encoded, and the easy-agreement trigger already forces one attack to confirmed or refuted. A second duty on the same concern is a Rule-5 breach. | Refuted | Rule-9 Conditions name the carriers: a Rule, a plan, a preference, a verdict. An `INCIDENTS.md` cause cell is none of them, though Rule-3 Incidents requires the column; a completion reply's diagnosis (Rule-3 Completion) is none of them either. The candidate creates no owner and no new duty — it names two carriers Rule-9's triggers do not reach. It is an amendment's worth of text at most. |
| 3 | It would have prevented neither incident. | Survives, scoped | For #6 it would have exposed that no observation had been made: the discriminating one was a single command, run later by a peer. For the 403 an observation *was* made — the setting change — but as a remedy, after the cause was written, at the Operator's cost. So the candidate reorders when the experiment happens and who pays for it; it never supplies one, and against a cause that stays unknown it buys only an honest label. |
| 4 | Two of 34 incidents, the most recent six days old, do not earn a new conduct clause. | Confirmed | The frequency case is weak and is not made here. What is surfaced is cost: an Operator action spent on a wrong diagnosis, a cause still unknown and parked as backlog #20, and a wrong cause published into merged commit messages that cannot be edited. Declining on the count alone is a coherent disposition. |
| 5 | Hedging every cause makes the log worse: a reader opens `INCIDENTS.md` for the cause, not for a caveat. | Survives, scoped | The scope holds the marker to causes no observation has separated. Rows that already carry their discriminating observation are unchanged — the 2026-09-22 #110 row names the stale local ref and the commit it last moved at, 328 behind `origin/main`, which is the observation. If most rows turned out to need the marker, that is itself the finding the candidate exists to produce. |

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #120 (Rule-2, Ratification
events: "A falsification record or audit is disposed by the Done-`Y` of its d-work"; the attack
table's form is Rule-9 Form). Remediation itself is a further Operator prompt on this row, never
taken here.
