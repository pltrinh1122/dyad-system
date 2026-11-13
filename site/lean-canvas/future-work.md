# The map of future work: ways of working with agents (layer a)

The target axis of this canvas set (`crafts/chronicle/rules/collateral.md` §5): the work a person does with AI agents,
anchored on the future, the Operator's decision (d-work #696, entry 32). Each way of working is mapped to the problems
of working with agents it meets. Every line is **H**. Its applicability to today's occupations is layer (b),
`professions.md`.

## The premise, and what would refute it
- **H** Most of today's roles gain from working well with agents.
- Refuted by a high count of `absent` and `net-cost` occupations in `professions.md`. At their best way of working, 62
  of the 923 sourced occupations are one or the other; per way, between 186 (evaluation) and 434 (decision framing).

## The problem classes (observable failure modes)
What the person sees, judged plain at its proficiency by `collateral-problem-plainness` (d-work #696, phase 1). Every
class carries a **human-attention cost**, time (to check) and effort (cognitive overload), and the condition of one
session or many.

| class | what you see | proficiency | roots |
|---|---|---|---|
| **O1** content | It told me something false: wrong (counter to what I know), stale (true once, not now) or invented. It may be just as sure when wrong (O2, a facet) | cursory | X1.1.1, X2.1.1 |
| **O4** target | It answered, or did, something other than what I asked | cursory | X1.1.1, N1.1.1.2.1 |
| **O10** target | It did what I said, not what I meant | cursory | N1.1.1.2.1, X1.1.1 |
| **O13** understanding the product | It gave me something I can't follow, so I can't stand behind it | cursory | X2.1.1, F1.1, F3.1 |
| **O9** altitude | The wrong level of detail: too fine and I drown in questions and steps; too coarse and it doesn't ask what it needed to | cursory (coarse), intermediate (fine) | N1.1.1.2.1 |
| **O5** extent | It did more, or less, than I agreed to | intermediate | N1.1.1.2.1, N4.1.1, N9.2.1.1 |
| **O6** understanding the process | Afterwards I can't understand what it did, or why | intermediate | N5.1.1, N10.2.1.1 |
| **O7** permission | It asked my permission the same way for a harmless step as for a harmful one | advanced | N2.1.1.1 |
| **O12** consistency | It follows my rules sometimes and not others, so I can't rely on it | advanced | U1.1.1, X1.1.1 |

Reference trees, in `reference/`: `hallucination.md` (X), `lose-track.md` (T, the effort cost of many sessions),
`rules-sometimes.md` (U), `cant-follow.md` (F).

## The ways of working
| way | what the person does | classes it meets | cost |
|---|---|---|---|
| **intent specification** | says what they want, at the right level of detail | O4, O10, O9 | — |
| **decision framing** | shapes what comes back to them as a question: what is asked, at what grain, at what risk | O9, O7 | effort |
| **evaluation** | judges what an agent produced before relying on it | O1, O13 | time |
| **oversight** | follows and bounds what an agent does while it acts | O5, O6, O7 | time |
| **orchestration** | runs many agents and sessions, and keeps rules holding across them | O12, O6 | effort |

Every class lands in at least one way. O7 sits in two (decision framing asks, oversight bounds) and O6 in two (oversight
while it acts, orchestration across sessions); each pair observes a different moment, so the overlap is stated, not
merged. A sixth way is admitted only for a class none holds.
