---
description: "Template: the /pb-<playbook> adapter pattern — copy to pb-<name>.md and replace <playbook>"
argument-hint: "<the play-book's parameter, if it takes one>"
---
<!-- Template for a command adapter (crafts/countersign/rules/interaction.md §6; #115: the adapter, never the
     artifact). To add one: copy to .claude/commands/pb-<name>.md, replace every <playbook> with the play-book's
     file stem and <parameter> with its parameter (or delete that line), and list it in interaction.md §6. The
     play-book must already exist as dyad/playbooks/<playbook>.md with a run-book dyad/runbooks/<playbook>.md: a
     command is never written in place of a play-book. The pattern is dsys's pb-* family, cited by name only. -->

Play-book `<playbook>`. Parameter: $ARGUMENTS

You are the agent of a dyad; the human is the sole disposer. This command is an **adapter** for the play-book
`dyad/playbooks/<playbook>.md`; it adds nothing to it.

1. **Frame first.** Report the frame's sentinel (`dyad/CLAUDE.md`); if the frame is absent, say so and stop. This
   invocation is a prompt: it opens a d-work (Rule-3) — open its row per the frame.
2. **Read the play-book now**, in full, and its run-book `dyad/runbooks/<playbook>.md`. Follow them as written;
   where this command and the play-book differ, the play-book wins.
3. The play-book's parameter `<parameter>` is the value given above, or its documented default.
4. Every mutation the play-book leads to waits for its plan answer (Rule-3, Rule-15): store the plan file first,
   falsified (Rule-9) and framed as one path, its strongest counter and a reconciliation (Rule-10). Run each step
   through `dyad/bin/dyad runbook run <playbook> <step>` so it leaves an event to cite. Propose; never dispose.
5. End the reply with exactly one question, as its last line, in the frame's plan form for this d-work.
