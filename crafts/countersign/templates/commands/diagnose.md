---
description: Run the self-diagnostic on this system, one level at a time up to the level given (default 4), and propose its record
argument-hint: "[last level to run, 1-4; default 4]"
---
<!-- Command adapter (crafts/countersign/rules/interaction.md §6; #115: the adapter, never the artifact).
     Installed by copying into .claude/commands/. The model is crafts/countersign/rules/self-diagnostic.md; the steps
     are this system's run-book <host>/runbooks/self-diagnostic.md, seeded from the craft's
     templates/runbooks/self-diagnostic.md (copied by hand: the craft's README). -->

Self-diagnostic. Last level: $ARGUMENTS

You are the agent of a dyad; the human is the sole disposer. This command is an **adapter** for the self-diagnostic
`crafts/countersign/rules/self-diagnostic.md` and this system's run-book of it; it adds nothing to them.

1. **Frame first.** Report the frame's sentinel (`dyad/CLAUDE.md`); if the frame is absent, say so and stop. This
   invocation is a prompt: it opens a d-work (Rule-3) — open its row per the frame.
2. **Read the procedure now**, in full: the model `crafts/countersign/rules/self-diagnostic.md` and the run-book
   `<host>/runbooks/self-diagnostic.md` (`<host>` the host path, preference `host-path`). Follow them as written;
   where this command and either of them differ, they win. If the run-book or `<host>/self-diagnostic-levels.txt`
   is absent, the diagnostic is not installed here: say so, name the two copy commands the craft's README gives
   (`crafts/countersign/README.md`, *Installing the self-diagnostic*) — the run-book's copy needs `mkdir -p <host>/runbooks` first where that directory does not exist — and
   stop: copying them is a mutation under its own plan answer.
   The diagnostic reads the head of `main`: run it with `main` checked out (`health` names the branch).
3. The last level to run is the one given above (1 to 4), or 4 when none was given: `2` runs the two coded levels
   and spends no inference, and the record writes each later level `not run (last level 2)`. `K` and `P` are the
   run-book's defaults unless the prompt names others.
4. Run the steps in the run-book's order through `dyad/bin/dyad runbook run self-diagnostic <step>`, starting with
   `health`, so each leaves an event to cite. A step that exits 3 found its gate closed: that level and every later
   one are `not run (gate)`. Repair nothing inside the run; L3 and L4 detect and never prove.
5. The commands are read-only, but a run leaves two writes in two zones: the runner's events, appended to
   `<host>/runbooks/events/self-diagnostic.jsonl` (the host path's zone) as the steps run, and the record (agent
   zone). Committing both, and every row, invariant, test or fix a finding leads to, are mutations under their own
   plan answer (Rule-3, Rule-15): store the plan file first, holding the record as the run found it, falsified (Rule-9) and framed as one
   path, its strongest counter and a reconciliation (Rule-10), and naming both writes as two changes in that order —
   the events first, the record citing their ids after (Rule-1: one zone per transaction, the referent before the
   referrer). Propose each finding; never adopt one. Once the record is written under that answer, run the `record`
   step and cite its line.
6. End the reply with exactly one question, as its last line, in the frame's plan form for this d-work.
