# Problem discovery: intent specification

Procedure: `crafts/chronicle/rules/collateral.md` §6, steps 1 and 2. Derived independently for d-work #696: nothing
under `site/` was read (no other source tree, no projection, no canvas or segment file).

## Brief (kept with the change)
- **Segment:** a way of working with AI agents, not a job: **intent specification** — the person says what they want
  from an agent, at the right level of detail, so that what comes back is what they meant.
- **Readers:** anyone who asks agents for work, at any proficiency, from out-of-the-box chat users to people running
  agents that act.
- **Anchor given:** "I answer for the result" (the person is held to what the agent did on their request).
- **Context only, not nodes:** failure classes this way meets — "it answered or did something other than what I asked",
  "it did what I said, not what I meant", "the wrong level of detail: too fine and I drown in questions, too coarse and
  it doesn't ask what it needed to".
- **Not given:** the projection, any other segment's tree, `site/identity.jsonld`'s wording of the root anchor (the
  anchor above is used as given).

## Step 1: frame (the anchor, written for the segment)
"When I let an agent **do work or act on my request** on **the work I hand over or put my name to**, I want to trust it
enough to answer for the result, so that **what goes out under my name is what I meant, and I am not held to something
I never asked for**."

## Step 2: diverge, by lens (none judged yet)

**Visibility** (can I see what it did)
- I see what it produced, but not what it took my request to mean.
- When it acts rather than answers, I see the end state, not which of my words led it there.

**Verifiability** (can I check it is right)
- I can check it did what I typed; I cannot easily check it did what I meant, because what I meant was partly never written.
- To check a long result against my intent I have to rebuild my intent first, from memory.

**Predictability** (will it do what it said)
- The same request worded slightly differently gets a different kind of result.
- I can't tell in advance whether it will stop and ask or just go ahead.

**Reversibility** (can I undo it)
- A misread chat answer costs a retry; a misread action may have already changed something.
- Undoing the result does not undo the misreading: the next try starts from the same words.

**Attribution** (can I show who decided)
- When it filled a gap with a guess, nobody can show afterwards that the guess was its and not mine.
- My request is the only record of what I wanted, and it says less than I meant.

**Competence** (does it know this domain)
- It reads a word of my trade in its everyday sense.
- It does not know the unwritten rules of my work that anyone in my place would assume.

**Intent** (did it understand what I meant)
- It took my example as the whole of the request.
- It followed the steps I suggested even where they missed the outcome I wanted.
- I only find out what I really wanted when I see something that is not it.

**Attention** (do I have time to check)
- Writing out everything up front takes longer than doing the work myself.
- Answering a stream of small questions breaks my concentration more than a wrong result would.

**Consequence** (what breaks if it is wrong)
- A misread request produces a confident, finished result that looks right and isn't.
- The cost of a misreading grows with how far it went before I saw it.

**Accountability to others** (who will hold me to it)
- Whoever receives the result holds me to it, not the agent.
- "That's not what I asked for" is not an answer I can give anyone else about work I handed over.

**Other**
- Each correction I make is a patch on the last; after a few rounds what I want is scattered across my messages.
- It never tells me where it was unsure what I meant; it picks a reading and goes on.
