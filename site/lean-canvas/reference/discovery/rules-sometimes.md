# Discovery: "sometimes it follows my rules and other times it won't" (o12)

Segment: advanced users who write standing rules for their agents, let agents act (edit files, run commands, send
things) and run several sessions or agents at once. Every statement below is a hypothesis (H).

## Anchor (Step 1)
When I let an agent edit, run and send things under standing rules I wrote, on work I answer for, I want to trust it
enough to answer for the result, so that what goes out under my name is what my rules allowed. [H]

## Divergence by lens (Step 2; unjudged)
- **visibility**
  - I can't see which of my rules a session actually has in front of it when it acts. [H]
  - When it skips a rule it doesn't say so; the reply reads the same either way. [H]
  - With several sessions running I can't see them all at once. [H]
- **verifiability**
  - A kept rule and a broken one produce output that looks alike until I check line by line. [H]
  - I can't check a rule like "never touch X" without reviewing everything it did. [H]
- **predictability**
  - The same rule is kept after one prompt and dropped after a series. [H]
  - A fresh session keeps it; a resumed or long one drifts. [H]
  - Two sessions started with the same rules behave differently. [H]
- **reversibility**
  - A sent message or a run command can't be taken back when the lapse is found. [H]
  - Even a reversible file edit has to be found before it can be undone. [H]
- **attribution**
  - I can't show whether the agent broke the rule or whether the rule never reached it. [H]
  - Nothing ties an act to the rules held when it was taken. [H]
- **competence**
  - It knows the task but not why my rule exists, so it bends it where the task seems to need it. [H]
  - In an unfamiliar area it falls back to its own habits over my rules. [H]
- **intent**
  - It keeps the letter of a rule and misses what I meant. [H]
  - It stretches a rule to a case I never meant it for, or misses a case I did. [H]
  - When the prompt in front of it pulls against a rule, it reads the prompt as overriding. [H]
- **attention**
  - I can't review every act of several sessions; the point of rules was not having to. [H]
  - I check closely at first and less later, which is exactly when it drifts. [H]
- **consequence**
  - One lapse in a sent message or a destructive command costs more than many kept rules save. [H]
  - A lapse in one session can spread to work another session builds on. [H]
- **accountability to others**
  - My team or client holds me to the result, not the agent. [H]
  - "It usually follows the rule" is not an answer I can give when it didn't. [H]
- **other**
  - My own rules conflict in cases I never pictured, and it settles them silently. [H]
  - I keep adding rules to patch lapses, and the longer list is followed less. [H]

## Tree and tests (Steps 3–4)
Source tree: `o12-rules-sometimes.md`. Per node by collateral-problem-depth: U0 symptom; U1, U1.1, U2, U2.1, U2.2, U3,
U3.1, U3.2, U3.3, U4, U4.1, U5 cause; U1.1.1, U2.1.1, U2.2.1, U3.1.1, U3.2.1 root-cause (each with a removal test, none
rewording an ancestor, the next why reaching the anchor); U5.1 anchor; joins U3.3 → U3.2.1, U4.1 → U1.1.1. No node is
solution-shaped. Tree by collateral-why-tree: open-branch no, circular no, too-deep no (deepest branch three whys),
no-anchor-branch no (U5 → U5.1), untested no; projection tests skipped (source tree) → ready.

## Selection (Step 5)
The anchor branch exits through no root cause (it reaches the anchor directly), so ranking falls to joins:
1. U1.1.1 — I can't see which of my rules a session is holding at the moment it acts (two branches: U1, U4 by join).
2. U3.2.1 — Every act I don't check myself is one I answer for blind (two branches: U3.2, U3.3 by join).
3. U3.1.1 — A broken rule looks just like a kept one until I check the result myself (one branch).
