---
description: Run the incident-hardening play-book over an incident ledger (default the instance's INCIDENTS.md)
argument-hint: "[path to the incident ledger; default agent-corpus/audits/INCIDENTS.md]"
---
<!-- Command adapter (crafts/countersign/rules/interaction.md §6; #115: the adapter, never the artifact).
     Installed by copying into .claude/commands/. The procedure is dyad/playbooks/incident-hardening.md. -->

Incident hardening. Ledger parameter: $ARGUMENTS

You are the agent of a dyad; the human is the sole disposer. This command is an **adapter** for the play-book
`dyad/playbooks/incident-hardening.md`; it adds nothing to it.

1. **Frame first.** Report the frame's sentinel (`dyad/CLAUDE.md`); if the frame is absent, say so and stop. This
   invocation is a prompt: it opens a d-work (Rule-3) — open its row per the frame.
2. **Read the play-book now**, in full, and its run-book `dyad/runbooks/incident-hardening.md`. Follow them as
   written; where this command and the play-book differ, the play-book wins.
3. The play-book's parameter `LEDGER` is the path given above, or its default when none was given. A ledger outside
   this system's own tree is not hardened from here: it is an intake (the play-book's Boundary).
4. Run Phase 0 first: `LEDGER=<path> dyad/bin/dyad runbook run incident-hardening survey` (read-only). If the ledger
   has not grown past its watermark, phases 1 to 3 do not run; Phase 4 (verify) still does.
5. The run-book's steps are read-only; every record, row and mitigation they lead to is a mutation under its own
   plan answer (Rule-3, Rule-15): store the plan file first, falsified (Rule-9) and framed (Rule-10). Propose each
   grouping, survivor and closure; never adopt a remediation or close a mode on your own judgment.
6. End the reply with exactly one question, as its last line, in the frame's plan form for this d-work.
