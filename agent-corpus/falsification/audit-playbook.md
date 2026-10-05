# Falsification — the standing audit play-book, and its first exercise (d-work #223)

**Claim (Operator, 2026-10-05, verbatim):** "this session will execute the audit playbook on this
dyad-system, or create the playbook if it doesn't exists." Revision 2 followed the Operator's N:
"should audit playbook include analysis and ingestion of INCIDENCES.md?"

**Reading.** There is no audit play-book here, so the claim becomes "a play-book for the standing audit
should exist, and running it once is what the prompt asks". The standing audit is the one #220 names:
"unit regression of everything else is an audit job", cadence open.

**Basis.** The plan file (`../d-work/plans/223.md`) holds attacks A1 to A11, made before anything was
written. This record carries them, and adds the attacks the first exercise
(`../audits/2026-10-05-audit.md`) made on its own findings.

## Attacks on the play-book (plan #223, before execution)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A1 | **The gate can never match.** If the watermark is the tree hash, the record an audit commits changes the tree, so the next audit always sees a difference and "no-op" never happens. | **Confirmed.** The first draft of the plan had this flaw. | The hash is over the tree minus the dated audit records; `INCIDENTS.md` is undated and stays in. Pinned by `AuditPlaybookTests.test_survey_watermark_ignores_dated_records_and_counts_everything_else`, which commits a record into a scratch repo and finds the verdict `unchanged`, then commits an incident row and finds `changed`. |
| A2 | **"The audit" is not one thing.** The 21 earlier records are topic reviews the Operator asked for. | **Confirmed, scoped.** | The play-book is the standing audit only. A topic audit stays an Operator prompt with its own plan and may borrow the Conduct section. |
| A3 | **Overlap with incident-hardening.** Shared ownership of a concern is a gap (Rule-5). | **Confirmed as a risk; revision 2 narrows it.** | Phase 3b ingests and sizes the log and runs hardening's own `survey`. Classification, mode records, mitigation inventory and child rows stay hardening's. |
| A4 | **An unchanged tree can still rot** (an exec bit, an interpreter, a guard no longer discovered). | **Confirmed.** | The watermark carries python and git versions; phase 2 runs on every invocation. |
| A5 | **Regression already runs at every merge, so a standing pass is waste.** | **Refuted, scoped.** | Waste only under #220's adoption (a), where evidence stays full; under (b) it is the only full run left. The play-book names the adoption it assumes. |
| A6 | **The author validates its own procedure.** The same session wrote the play-book and ran its first exercise. | **Confirmed, scoped.** | The Operator's Done-`Y` disposes both. The first record is a baseline, not a verdict; every command is an existing one. E8 below is what the exercise found about the play-book itself. |
| A7 | **A play-book no Rule reads is inert.** | **Survives, scoped.** | `ds-report-incidents` is the precedent. The test pins the play-book's shape; making it required is the cadence decision, the Operator's. |
| A8 | **Cost.** The whole suite is minutes on one machine. | **Survives.** | The record states the interpreter and the container and gives a ratio only against a later run on the same kind of container. |
| A9 | **"Include the analysis" means classify the delta in the audit.** | **Refuted as the path, scoped.** | Classification is inference done again when hardening runs, and would open a child row per mode. The audit ingests, sizes and surfaces the gap; the Operator may widen it. |
| A10 | **Ingestion is already code, so the audit adds nothing.** | **Refuted, scoped.** | `incidents.py` checks shape only; phase 3b is the first reader that asks the coverage question, and it uses the parser rather than `grep`. |
| A11 | **A gap line that always says "run hardening" is noise.** | **Survives, scoped.** | It is true today (E2) and it reads the watermark, so it goes quiet once a hardening run writes one. |

## Attacks the first exercise made on its own findings
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| E1 | **Finding 1 is the runner's environment, not the repo.** The hosted `rule-11 package` job has failed on 83 consecutive pushes to `main`. | **Refuted.** | Reproduced in this container (Python 3.12, git 2.43; CI ran 3.12.14 and git 2.55): `package.py install` of a scratch repo writes the bundled `sysadmin` craft, the next `craft install` of the same craft is refused with "crafts/sysadmin is locally modified or authored here", and the exported archive has the same sha256 prefix, `0b09a903`, as the hosted log. |
| E2 | **Finding 1 would have been caught by the local gate.** | **Refuted.** | `check --evidence` at `9f765fe` shows 0 FAIL and 926 tests passing while the same sequence is refused. Nothing in the kernel-only path runs core-install then craft-install of a bundled craft. Scope: the claim is that no test or guard failed on it, not that none touches it. |
| E3 | **Hosted CI is absent here (billing), as merge messages of 2026-09-22 and 2026-09-23 say.** | **Refuted for the window read.** | Jobs start and run: the job of run 169 lasted 1 m 43 s and lists its steps; the failing step ran two seconds. The merge-message sentence does not describe these runs. |
| E4 | **Hosted CI is not a gate (Rule-14 property 3), so red is no finding.** | **Survives, scoped.** | Nothing gates on it. But it is the one place Rule-11 property 5's scratch install runs, and #220's survivor counts an install smoke as CI's own job. A corroborator red for 83 pushes corroborates nothing, and nothing in the system noticed. |
| E5 | **#201 already records this, so the finding is a duplicate.** | **Confirmed, scoped.** | #201 (`backlog`, opened 2026-10-01, no plan) names the mechanism. It dates the red from 2026-09-25 for "8 runs"; the runs show a streak of 83 from run 87 (2026-09-23T03:04Z, the merge that added the bundled-craft clause), the install step failing in the first run where `check` passed (run 91) and in every sampled run after (91, 119, 139, 169). Steps were read for 6 of the 83 runs; conclusions for all 83. The audit adds the scale and the date, not the cause. |
| E6 | **Finding 2: the incident log's last grouping is stale.** The index audit carries no `covered through:` line, so a missing watermark is a format gap and not proof the log was not worked since. | **Refuted, scoped.** | `grep -h 'covered through' agent-corpus/audits/*.md` returns nothing, and hardening's own `survey`, run through the runner, printed "no index audit names agent-corpus/audits/INCIDENTS.md: first exercise". The records beside the log are the nine mode records and the index of 2026-09-22; none is later. The two counts differ and both are stated: 55 rows beyond the index's population of 34 (89 at the survey), 48 rows dated after 2026-09-22. |
| E7 | **Finding 3: release state is lag, not drift.** Live VERSIONs are ahead of the last tags (core 0.10.1 against `dyad-operator-v0.9.0`; bundle 0.12.1 against `v0.11.0`; countersign and disclosure never tagged). | **Refuted as a defect, confirmed as state.** | Tags were fetched: `git ls-remote --tags origin` lists 45, the same 45 as the local clone (the positive control). A tag is the Operator's `Y/N: release <tag>?`, so lag is theirs to set. The one consequence checked: `check_drift`, Rule-11 property 4's converse, has nothing to compare for any of the six components and prints six skip lines. |
| E8 | **Finding 4: the run-book never reads hosted CI, so the exercise found finding 1 by luck.** | **Confirmed.** | Finding 1 came from an ad hoc read through the GitHub tool, outside the runner. Hosted CI is a library adapter (Rule-14 property 3), so the package must not depend on it; the play-book can still say "read it where an adapter exists, otherwise `unobserved`", as it says of host documents. Changing the play-book is a departure from plan #223, so it is a proposed row, not an edit. |
| E9 | **Stale rows and presence files are findings.** Two rows have had no activity for over two weeks and 45 presence files are stale. | **Refuted as findings; kept as drift facts.** | A row waiting on the Operator is not stale, and Rule-16 makes a stale presence file advisory. The record prints dates and counts and judges neither. |
| E10 | **The two unmerged remote branches are pruning candidates.** `origin/ledger-198-open` and `origin/ledger-206-open` each hold one ledger-only commit not in `main`. | **Survives, scoped.** | Rows 198 and 206 exist on `main`, in a different state from the branch's copy, so the branches are superseded as far as `git diff` shows. Deleting a remote branch is its own destructive counter-prompt (Rule-8); the record lists them and proposes nothing. |

## Survivor
The play-book as planned (phases 0 to 4, run-book of six read-only steps, five tests), with A1's hash.
The first exercise's findings stand in the audit record, three of them proposed as rows and none opened.
No Rule, vocabulary, preference or code changed.

Disposition: see ledger #223 (Rule-2: the Done-`Y` of d-work #223 disposes this record).
