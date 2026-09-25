---
description: Run the craft-instantiation play-book on a new body of work (new craft here, or advise a new dyad system)
argument-hint: "<the body of work, in a sentence>"
---
<!-- Command adapter (crafts/countersign/rules/interaction.md §6; #115: the adapter, never the artifact).
     Installed by copying into .claude/commands/. The procedure is dyad/playbooks/craft-instantiation.md. -->

Craft instantiation for: $ARGUMENTS

You are the agent of a dyad; the human is the sole disposer. This command is an **adapter** for the play-book
`dyad/playbooks/craft-instantiation.md`; it adds nothing to it.

1. **Frame first.** Report the frame's sentinel (`dyad/CLAUDE.md`); if the frame is absent, say so and stop. This
   invocation is a prompt: it opens a d-work (Rule-3) — open its row per the frame.
2. **Read the play-book now**, in full, and its run-book `dyad/runbooks/craft.md`. Follow them as written; where
   this command and the play-book differ, the play-book wins.
3. Check the trigger against the installed crafts (`dyad/bin/dyad craft list`). If the work is a further instance
   of an existing craft, say so: the play-book does not apply.
4. Apply the `craft-instantiation-criteria` in the play-book's order, quoting each one's id and outcome. None
   firing → the plan proposes the new craft (author or import, D3'); any firing → the plan advises a new dyad
   system, naming the criterion. Never instantiate either on your own.
5. Store the plan file (Rule-15) naming the run-book steps to run, falsified first (Rule-9) and framed as one path,
   its strongest counter and a reconciliation (Rule-10). Run no step before the plan answer is `Y`; after it, run
   each step through `CRAFT=<name> dyad/bin/dyad runbook run craft <step>` so each leaves an event to cite.
6. End the reply with exactly one question, as its last line, in the frame's plan form for this d-work.
