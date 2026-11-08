# Play-book: craft instantiation (core craft, `dyad-operator`; #165, #626)

For a body of work with no home in an installed craft: a craft in this dyad system, or advice to start another dyad
system. The operator never instantiates a craft and does not judge craft against system (ledger #165). Read by
Rule-3's Plan clause. Steps: `dyad/runbooks/craft.md`, run as `dyad runbook run craft <name>`. Criteria: plan #153
(`agent-corpus/d-work/plans/153.md`).

## Trigger
An operator prompt opens work as `dmc:craft-trigger` decides against `dyad craft list`; the play-book runs inside that
d-work, before its plan file is written (Rule-15).

## Default
Decide by `dmc:craft-instantiation` over the criteria below, and the craft's source by `dmc:craft-source`. With none
firing the plan proposes `crafts/<name>/` here — authored (`dyad craft new <name>`) or imported (`dyad craft install
<src>`) — states "craft-instantiation-criteria: none fire", names the run-book steps, and asks only the plan question.

## craft-instantiation-criteria
The D-criteria of #153, applied in this order (it encodes the cost of being wrong); one firing advises another dyad
system, quoting the criterion, and stops at the plan question.

| id | criterion | fires when |
|----|-----------|------------|
| D1 | **Classification boundary.** The work holds sensitive data (PII, financial, credentials) while this system is non-sensitive, or vice versa. | different class → another system, on the remote its class requires |
| D2 | **Disposer identity.** A different operator, or the same operator acting for a distinct party, must dispose; Rule-2's disposer is one party per system. | different disposer → another system |
| D3' | **Craft availability** (restated). Import a craft that exists as a craft corpus, build on one of that practice here; author one that does not exist yet, here first. | never advises another system; decides the source within the default |
| D4 | **Ledger coupling.** Its d-works would rarely `refs` this ledger's rows and its audits would sweep its own Tended Rules only. | mostly disjoint → another system |
| D5 | **Lifecycle.** Its own beginning and end, or its own retention or deletion requirement, distinct from the host's. | own lifecycle → another system |
| D6 | **Zone fit** (Rule-1). It would need a zone beyond `agent`, `workstation`, `preferences`, `infra`, `craft`. | needs a zone → another system |

## Steps: a craft here
1. `new` — `dyad craft new <name>`, or `install` for an existing craft corpus.
2. `check` — `dyad craft check <name>` passes.
3. Author its rules, vocabulary, templates, guards and records in the d-work's craft-zone PR (Rule-1); `guards` and
   `tests` pass.
4. `registry` — an installed craft's row is shown; an authored craft has none.
5. `export` when it is to be reused elsewhere; the archive's sha256 is cited.

## Steps: another dyad system
Advised, never executed unprompted. On the plan-`Y`, `system-new` (role `operator`: a remote credential) installs the
core craft into a fresh clone on the remote D1 selects; then that system's registry row (#143 C6), `dyad craft
install` of each craft it practises, and its first ledger row. This d-work completes when the advice is disposed.

## Evidence
The criteria's outcome (which fired, or "none"); the event ids (`<runbooks>/events/craft.jsonl`); the PRs by number
and zone. A step run outside the runner is an incident (Rule-3).
