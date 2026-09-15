# Play-book: craft instantiation (core craft, `dyad-operator`; #165)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision; its steps are a run-book. This one decides, for a body of work that has no home in
an existing craft, whether the Agent instantiates a **new craft** in this dyad system or advises a **new
dyad system** — the Operator never instantiates a craft and does not judge craft-versus-system (Operator
prompt, ledger #165). Read by Rule-3's Plan clause. Steps: `dyad/runbooks/craft.md` (run through
`dyad runbook run craft <name>`, the core runner, so each step leaves an event). Criteria: plan #153
(`agent-corpus/d-work/plans/153.md` in this instance; the audit of #153 in `agent-corpus/audits/`).

## Trigger
An Operator prompt opens a body of work that no installed craft (`dyad craft list`) practises: its
rules, vocabulary or guards would not be *consistent* (Rule-6) with any craft here, and it is not a
further instance of one (another server for the sysadmin craft is *not* a trigger; a tax filing is).
The play-book runs inside the d-work the prompt opened, before its plan file (Rule-15) is written.

## Default
**New craft instance.** Unless a criterion below fires, the plan proposes `crafts/<name>/` in this
system — authored (`dyad craft new <name>`) or, when the craft already exists as a craft corpus,
imported (`dyad craft install <src>`). The Operator is asked nothing beyond the plan-`Y`; the plan
states "craft-instantiation-criteria: none fire" and names the run-book steps it will run.

## craft-instantiation-criteria
The D-criteria of #153, applied in this order (the order encodes the cost of being wrong, #153
attack 1); any one firing → the plan advises a **new dyad system**, quoting the criterion's id and
text, and stops at the plan-`Y` — the Operator disposes; the Agent never instantiates either on
its own.

| id | criterion | fires when |
|----|-----------|------------|
| D1 | **Classification boundary.** The work holds sensitive data (PII, financial, credentials) while this system is non-sensitive, or vice versa. | different class → new system, on the remote its class requires |
| D2 | **Disposer identity.** A different Operator, or the same Operator acting for a distinct party (a client, a family member's affairs, an employer), must dispose; Rule-2's disposer is one party per system. | different disposer → new system |
| D3' | **Craft availability** (restated). If the craft exists as a craft corpus, import it; if a craft of that practice exists here, extend it — *never* a new system on this ground. A craft that does not exist yet is authored here first and extracted later. | never fires "new system"; decides author-or-import within the default |
| D4 | **Ledger coupling.** Its d-works would rarely `refs` this ledger's rows and its audits would sweep its own Tended Rules only. | mostly disjoint → new system |
| D5 | **Lifecycle.** Its own beginning and end (a filing year, a project) or its own retention or deletion requirement, distinct from the host's. | own lifecycle → new system |
| D6 | **Zone fit** (Rule-1). It would need a zone beyond `agent`, `workstation`, `preferences`, `infra`, `craft`. | needs a zone → new system |

None firing → the default (new craft). D3' is applied in every case: even a new system imports or
authors the craft; it never decides between craft and system (#153, revision 2).

## Steps: new craft
The run-book `dyad/runbooks/craft.md`, in order; the events are the evidence:
1. `new` — `dyad craft new <name>` (reversible; undo `rm -r crafts/<name>`), or `install` for an
   existing craft corpus (its registry row is written by the command).
2. `check` — `dyad craft check <name>` passes (the scaffold's postcondition).
3. Author the craft's rules, vocabulary, templates, guards and records in the d-work's craft-zone
   PR (Rule-1); `guards` and `tests` pass on the kernel-only path (Rule-14 property 3).
4. `registry` — an installed craft's row is shown; an authored craft has none (`dyad craft list`:
   `authored`).
5. `export` when the craft is to be reused elsewhere: the archive's sha256 is cited.

## Steps: new dyad system
Advised, never executed unprompted. Once the plan-`Y` confirms a new system, the run-book's
`system-new` step (role `operator`: a remote credential is needed) installs the core craft into a
fresh clone on the remote D1 selects; then, in that system: the registry row per #143 C6
(`agent-corpus/systems/` of the parent), `dyad craft install` of each craft it practises (D3'), and
its first ledger row (`dyad dwork new`). This system's d-work completes when the advice is disposed;
the new system's first d-work is its own.

## Evidence
The completion reply (Rule-3) cites: the criteria's outcome (which fired, or "none"); the event ids of
the run-book commands run (`<runbooks>/events/craft.jsonl`); the PRs by number and zone. A step run
outside the runner is an incident (Rule-3).
