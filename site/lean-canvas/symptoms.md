# Symptoms of working with AI agents: the canon

What readers see when they work with AI agents, in their words: the first thing a piece shows them
(`crafts/chronicle/rules/collateral.md` §5, the symptom canon; record `collateral-symptom-canon`). It grows by
observation: the Operator's own, cited by provenance entry, then interviews and readers' feedback through the channels,
cited by a reference that names no one. A tree node roots an entry but observes nothing; a tree symptom no one has
reported waits under **Candidates**. Append-only: an entry is superseded, never edited, and its id is never reused.
Coverage is checked by `crafts/chronicle/scripts/symptom_canon.py check site/lean-canvas`.

Read it two ways: **by reader**, an entry's proficiency and way of working; **as a roadmap**, every entry `served: not
yet` or `partly` is a candidate for the dyad-system's development, never a row of work by itself. Every entry has one
observer so far, the Operator, and reads as one observer's.

## S1 It states something false as if it were true.
class: O1
proficiency: cursory
way: evaluation
when: during, after one prompt or a series; found late, after you relied on it
served: partly
cite: dyad/rules/RULE-9-falsification.md
sources: observed:696#5, hallucination:X0, evaluation:V1
> The Operator's reference symptom ("AI hallucination"). Partly served: the dyad falsifies every claim before a Rule,
> plan or verdict encodes it; nothing yet checks an answer the agent gives in passing.

## S2 It told me something counter to what I know, and I knew at once.
class: O1 (kind: wrong)
proficiency: cursory
way: evaluation
when: during, at once
served: not yet
sources: observed:696#22
> A kind of S1 the reader catches by their own knowledge.

## S3 It told me something stale: true once and not now, and I knew at once or found out later.
class: O1 (kind: stale)
proficiency: cursory
way: evaluation
when: during or resumed; at once or later
served: not yet
sources: observed:696#22
> A kind of S1: the source was right once.

## S4 It leads me down a rabbit hole of clarifying questions.
class: O9 (altitude, too fine)
proficiency: intermediate
way: intent specification; decision framing
when: during, after a series
served: partly
cite: dyad/rules/RULE-3-d-work.md
sources: observed:696#10, intent-specification:I2
> Its cost is effort. Partly served: the dyad batches its questions and asks each kind once per row (Rule-3, Batch
> disposition); a plan can still be revised many times.

## S5 It did what I prompted, not what I actually intended.
class: O10
proficiency: cursory
way: intent specification
when: new or during, after one prompt; seen in the result
served: partly
cite: dyad/rules/RULE-3-d-work.md
sources: observed:696#10, intent-specification:I1, evaluation:V4
> Partly served: under `intent-reading: on` the agent states its reading of the request, and the Operator accepts it,
> before any plan (Rule-3, Plan). V4 is the same symptom found while evaluating.

## S6 With so many sessions open and ongoing, I lose track of what each one is doing.
class: the human-attention cost (effort), under the condition of many sessions
proficiency: advanced
way: orchestration
when: resumed, after a series
served: partly
cite: dyad/rules/RULE-16-concurrent-sessions.md
sources: observed:696#11, lose-track:T0
> Partly served: each session's presence file and the board record what each unit is working and what waits on the
> Operator (Rule-16); the Operator still reads them unit by unit.

## S7 It follows my rules sometimes and not others, so I can't trust it to be reliable.
class: O12
proficiency: advanced
way: orchestration
when: new or resumed
served: partly
cite: dyad/CLAUDE.md
sources: observed:696#12, rules-sometimes:U0
> Partly served: the frame's sentinel proves the rules were loaded at a session's start, and guards check the record
> mechanically before every push; whether a rule held in an act stays inference.

## candidates
- evaluation:V0 unobserved: checking takes about as long as doing the work (the time cost)
- evaluation:V2 unobserved: it gives me something I can't follow, so I can't stand behind it
- cant-follow:F0 unobserved: the same symptom as V2, from the reference tree; one entry when observed
- evaluation:V5 unobserved: it gives way when I push back, even when it was right (O1's facet, O2)
- intent-specification:I0 unobserved: it came back with something other than what I asked for (O4)
- platform-ops:N0 unobserved: I can't review every command it wants to run
- regulated-engineering:R0 unobserved: an agent's change lands under my name, and I cannot show that I approved it
- regulated-engineering:R1 unobserved: before an audit I rebuild who approved each sampled change
- regulated-engineering:R2 unobserved: I keep the agent off change-controlled work
- regulated-engineering:R3 unobserved: the agent changed more than the ticket said (O5)

## excluded
- evaluation:V3 restated: it rewords V0.3, a cause of V0 (#696, entry 37, S2)
- intent-specification:I3 restated: it is I0 or I1 over a series, with the effort cost (#696, entry 37, S4)
