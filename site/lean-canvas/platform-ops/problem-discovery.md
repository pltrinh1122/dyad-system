# Problem discovery — `platform-ops`

The run of `crafts/chronicle/rules/collateral.md` §6 for this segment. Every line is **H** (hypothesis) until a reader
of the segment confirms it. Source: the run in PR #757's description (d-work #674), re-checked against §6 as it
landed. Added: the statement under *other* (cost of adoption). Struck: none.

Since d-work #683 its steps 3 onward are kept as a tree, `why-tree.md` (§6 as revised by #678): that file, not §3–§6
below, is the reference a claim is looked up in. The sections below stay as the first run's record.

## 1. Anchor
- **H** When I let an agent run commands on hosts I am paged for, I want to trust it enough to answer for the result, so that no outage is one I cannot explain.

## 2. Diverge, by lens
- visibility: **H** I can't see what the agent changed on a host after the session ends.
- visibility: **H** Its commands scroll past and are gone.
- verifiability: **H** I can't tell a change was right until something breaks.
- verifiability: **H** Nothing records what it checked before acting.
- predictability: **H** It says it will restart one service and touches three.
- predictability: **H** The same request gives a different command next time.
- reversibility: **H** I don't know which of its changes can be undone.
- reversibility: **H** Undoing means first reconstructing what it did.
- attribution: **H** In the postmortem I can't show who decided, me or the agent.
- attribution: **H** My approval was a click; nobody can see what I approved.
- competence: **H** It doesn't know our hosts' quirks.
- competence: **H** It is confident on systems it has never seen.
- intent: **H** It solved the ticket's words, not what I meant.
- intent: **H** It took "clean up" as "delete".
- attention: **H** I can't read every command it wants to run.
- attention: **H** Approving one by one, I end up approving blind.
- consequence: **H** One wrong command takes production down.
- consequence: **H** A small change cascades across hosts.
- accountability to others: **H** My team and my manager hold me to every change, agent or not.
- accountability to others: **H** An auditor asks for a change record I don't have.
- other: **H** Adding another approval step is the last thing my on-call rotation needs.

## 3. Cluster
- **H** C1, no trail: both visibility statements; verifiability, "nothing records what it checked"; reversibility, "undoing means first reconstructing"; attribution, "who decided"; the auditor.
- **H** C2, approval at the wrong grain: both attention statements; attribution, "my approval was a click"; predictability, "touches three"; other, "another approval step".
- **H** C3, no sense of risk: both consequence statements; reversibility, "which can be undone".
- **H** C4, unknown judgement: both competence statements; both intent statements; predictability, "a different command next time"; verifiability, "right until something breaks".
- **H** Accountability to others, "my team and my manager", sits under every cluster: it is the anchor restated.

## 4. Converge, by asking why
- **H** C1: why is there no trail? Session output is gone when the session ends. Why? Nothing ties an agent's action to an approval and an outcome.
- **H** C2: why approve blind? Approvals come one command at a time, without the plan they serve. Why? The only gate on offer is the command prompt.
- **H** C3: why does a restart look like a delete? Nothing classes an action by what it risks before it runs.
- **H** C4: why can't I trust its judgement? Because it is a model; the next why reaches the anchor at once. Dropped: no segment cause the product removes.

## 5. Test (`collateral-problem-depth`)
- **H** "I can't read every command it wants to run": symptom.
- **H** "The only gate on offer is the command prompt": cause; a deeper why (the approval is cut off from the plan it serves) explains it.
- **H** C1's answer, "Nothing ties what an agent did to what I approved, and why": root-cause.
- **H** C2's answer, "The only approval I can give is per command, so I approve keystrokes, not intent": root-cause.
- **H** C3's answer, "At the moment of approval, every action looks the same, whatever it risks": root-cause.
- **H** C4's answer, "The agent's judgement is unknown": dropped at step 4, kept as the pitch's strongest objection.

## 6. Select
- **H** The three root causes become `problem.md`'s entries, ranked by how many symptoms each removes: C1 (six), C2 (five), C3 (three).
