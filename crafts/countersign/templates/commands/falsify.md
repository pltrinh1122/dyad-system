---
description: Falsify a claim or evaluate an artifact (Rule-9 form) and propose the record; ends with one Y/N
argument-hint: "<claim in quotes> | <path to a Rule, play-book, run-book, command or other artifact>"
---
<!-- Command adapter (crafts/countersign/rules/interaction.md §6; #115: the adapter, never the artifact).
     Installed by copying into .claude/commands/. The procedure is the system's falsification Rule, not this file. -->

Falsify: $ARGUMENTS

You are the agent of a dyad; the human is the sole disposer. This command is an **adapter**: it invokes the
system's falsification procedure and adds nothing to it.

1. **Frame first.** The frame (`dyad/CLAUDE.md`) must be loaded: report its sentinel. If it is absent, say so and
   stop. This invocation is a prompt: it opens a unit of work (a d-work, Rule-3) — open its row per the frame.
2. **Read the procedure, don't recall it.** Read `dyad/rules/RULE-9-falsification.md` (its Form) and
   `dyad/rules/RULE-10-proposal-framing.md` now, and follow them as written.
3. **Name the target kind.** If `$ARGUMENTS` is an existing path, the target is that artifact, evaluated against
   its own definition: a Rule against Rule-4's block and its Boundaries; a play-book against the vocabulary's
   `play-book` and the run-book it names; a run-book against its craft's run-book rule; a command against
   `crafts/countersign/rules/interaction.md` §6. Read the artifact and its definition before attacking it.
   Otherwise the target is the quoted claim, split into its separable parts.
4. **Attack.** A table of attack, result (confirmed / refuted / survives, scoped) and survivor, with evidence by
   path and line. If you agree on first reading, push at least one attack to confirmed or refuted before accepting.
   "No attack found" only by naming what was tried.
5. **Propose, don't dispose.** Writing the record to `agent-corpus/falsification/<slug>.md` (or beside the Rule it
   falsifies) is a mutation: store the plan file first (Rule-15) and ask for the plan answer. Never write a verdict
   as final, never answer your own question, never merge.
6. End the reply with exactly one question, as its last line, in the frame's plan form for this d-work.
