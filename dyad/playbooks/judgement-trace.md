# Play-book: judgement trace (core craft, `dyad-operator`; #690)

How the agent examines one of its own acts that the operator questions: from the symptom, back through every Rule
sentence, decision record and preference that decided it, to its cause. Its first product is clarity, the operator's
model and the agent's reading made to agree; a change is a possible second product, never a required one. The worked
example is plan #689, revisions 1–3. Steps with a command are `dyad/runbooks/judgement-trace.md`, run through the core
runner (`dyad runbook run judgement-trace <step>`); the rest are inference, and no command decides any step.

**Trigger.** The operator writes "judgement trace: <the behavior>", or asks why the agent did something and asks for it
traced. Never started by the agent on its own act, which is an incident (Rule-3 Incidents), nor on another unit's act
without the operator's prompt.

## Steps
- **T1 Symptom.** The act, quoted from the reply or the record where it happened, with its row and commit. Run-book
  step `symptom` prints the row's stored files and its commits.
- **T2 Trace back.** Each decision that led to the act, one line each, newest first, every one cited by path and line as
  it reads on `main` now, never from memory or from the agent's earlier summary. Run-book step `trace` prints a cited
  line from `origin/main`. A line the agent cannot cite is written `uncited` and is a finding of its own.
- **T3 Conflicts.** Every pair of cited texts that decide the same case differently, and every cited text that no longer
  matches the code or the store on `main`.
- **T4 Cause.** Each line of T2 and each finding of T3 classed by `dmc:judgement-cause`, and the trace's cause stated: the
  highest class by that record's precedence. Run-book step `cause` prints the record's classes in that order.
- **T5 Outcome.** What the class says, and nothing more.
- **T6 Report.** One reply, in this order: the symptom, the trace, the conflicts, the cause, the outcome; and
  **corrections**, every earlier statement of the agent's that the trace overturns, named as a correction with what it
  said (#689 revision 3's corrections are the form).

## Defaults
A trace whose cause is `intended` or `undetermined` writes nothing and opens no row: it is a read-only answer (Rule-3
Scope), so the examination costs the operator no question. A trace whose outcome opens or revises a row is stored in
that row's plan file, as #689's revisions were, so the record of why survives the chat.

## Conduct
The class is the agent's reading, presented to the operator, never declared final (Rule-2: an agent-authored verdict is
the operator's to finalise). Two fences on that reading, from the craft invariants:
- **anti-cave:** the agent never classes its act `misapplied` because the operator questioned it, only because a cited
  text decided otherwise;
- **two-models:** it never classes an act `intended` to defend it, only because every cited text agrees with the act.

Where the operator's model and the trace differ and the trace's cause is `intended`, the trace says so plainly: that is
the clarity this play-book exists for.
