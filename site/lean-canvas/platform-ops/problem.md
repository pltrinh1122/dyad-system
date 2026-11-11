# Problem — `platform-ops`

Root causes selected from `why-tree.md` (`crafts/chronicle/rules/collateral.md` §6), ranked: first those the anchor
branch exits through (N7.1), then by the branches that join them. Each entry and each symptom cites its node.

1. **H** (top) Nothing ties what the agent did to what I approved, and why. — N5.1.1
   - symptom: **H** "What I didn't read, I can't review later either." — N5
   - symptom: **H** "I can't review every command it wants to run." — N0
2. **H** Nothing compares what happened with what was intended before the work is called finished. — N4.1.1
   - symptom: **H** "Reading isn't checking: even a command I read, I can't confirm was right." — N4
   - symptom: **H** "I can't review every command it wants to run." — N0
3. **H** Nothing classes an action by what it risks before it runs. — N2.1.1.1
   - symptom: **H** "Each one is hard to judge: one line doesn't tell me what it will do." — N2
   - symptom: **H** "I can't tell which ones matter, so all of them seem to need reading." — N3

Not selected (fourth by the rule, kept in the tree): N1.1.1.2.1, "Nothing captures the work's intent as an object I can
approve before anything runs", joined once (N6.1).

Existing alternatives:
- **H** Approving each command in the agent's own permission prompt.
- **H** Keeping agents off production hosts entirely.
- **H** Infrastructure as code with human review of every change.
