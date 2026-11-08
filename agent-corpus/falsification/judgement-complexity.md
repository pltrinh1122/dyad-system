# Falsification record — which judgements stay inference (d-work #642)

**Claim (operator prompt, provenance #642 entry 1):**
- (C1) only complex judgement should remain agent inference;
- (C2) a judgement is not complex if a cosine-similarity analysis can derive it;
- (C3) that means the comparator data set is fixed.

The decision record is `dyad/dmc/judgement-complexity.jsonld`, whose home is the play-book
`dyad/playbooks/playbook-optimize.md`. The attacks were read in the row's intent reading
(`agent-corpus/d-work/plans/642.md`), against `main` at e4f47115.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A1 | Cosine gives a score, not a decision; something must turn the score into an outcome. | **Confirmed** | A fixed threshold, a tunable with its default in the record (#590's form), turns the score into a label. "Derive" means a score and a threshold, never the score alone. |
| A2 | Lexical similarity is not meaning. This system's own TF-IDF flagged #597 against #538 and #539 as similar (0.42–0.43), when #597 had absorbed those archived rows: similar, not duplicate. | **Confirmed** | Similarity derives a judgement only where the label follows from resemblance to labelled examples. Where it does not, as with duplicate against absorbed, the case stays inference. The hygiene ranking stays a candidate for review, never a finding. |
| A3 | A comparator set that grows changes the IDF weights, so the same input scores differently tomorrow. | **Confirmed: C3 holds as a necessary condition** | The comparator set and its vocabulary are fixed **per version**: frozen in a file with a digest, re-fitted only at a named event. That makes the result deterministic (syseng `determinism.md`) without freezing it forever. |
| A4 | "Can derive" is untested until measured: a threshold may agree with past judgements by chance. | **Confirmed** | A judgement qualifies only when similarity over the fixed set reproduces a held-out sample of past recorded judgements at a stated agreement bar. The measure is stored, and a fall below the bar returns the judgement to inference. |
| A5 | Some judgements carry authority: a cosine label for a disposition, an intent reading or a ratification would let code decide what is the operator's. | **Confirmed** | A similarity label is a proposal, a candidate or a pre-class, never a disposition (Rule-2), and never for an outcome whose consequence is a destructive act. |
| A6 | Near-ties: a score just over the threshold is as uncertain as one just under. | **Confirmed** | A margin around the threshold falls back to inference: the label abstains, and the agent judges. |
| A7 | A vectorizer beyond the standard library (embeddings) is a new dependency on The World. | **Survives, scoped** | Stdlib TF-IDF (`hygiene.tokens`, `tfidf`, `cosine`, moved to `dyad/scripts/similar.py`) is the kernel's. An embedding model is a manifest row (Rule-14), a separate decision. |
| A8 | C1 needs a definition of "complex" that is not circular. | **Survives** | Complex is what fails every other class. That gives three classes, not two: mechanical (#641's test), similarity-derivable (the six conditions below) and complex. |

**Survivor, first reading.** A recurring judgement a play-book step cites is **similarity-derivable**, not complex, when
its outcomes are a finite label set, a fixed versioned comparator set of past labelled judgements exists with a digest, a
fixed vectorizer (stdlib TF-IDF over the set's frozen vocabulary) and a fixed threshold and margin are used, agreement on
a held-out sample meets a stated bar, its result is a proposal or a pre-class and never a disposition or the trigger of a
destructive act, and a score inside the margin or a fall in agreement returns the case to inference. Otherwise it is
**complex**, unless #641's test makes it **mechanical**. C1 survives with that definition, C2 only under A1–A6's
conditions, and C3 is necessary and holds per version.

## Revision 2: the class is precedent (operator prompt, provenance #642 entry 4: "fold precedent into #642")
The home falsified "precedent is a type of judgement similarity can derive" before plan revision 2 (`plans/642.md`).
The attacks, as the revision records their survivors:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| Q1 | A precedent is a past case's outcome, not its text; a set labelled by anything else compares with nothing binding. | **Confirmed** | Each entry carries the outcome it set. |
| Q2 | Whole-text similarity matches cases on their wording, not on what decided them. | **Confirmed** | Similarity is over the record's decisive inputs, its `dyad:inputs` as stored facts. |
| Q3 | Precedent binds only like cases; telling a case from its precedent (distinguishing) is itself a judgement. | **Confirmed** | Distinguishing stays inference: a case that may differ stays with the agent, which departs by naming the input that differs. |
| Q4 | An agent's own past ruling is not precedent: nothing ratified it. | **Confirmed** | The set holds ratified cases only, each with the row whose plan-`Y` or done-`Y` covered it; `freeze` refuses an entry with no covering `Y` on `main`. |
| Q5 | Precedent is overruled: a Rule amended, or a later Done superseding a case, leaves a stale set deciding. | **Confirmed** | The set is rebuilt at a change of the owner Rule or the home, or a superseding or retiring done-`Y`; it records its base commit and the guard warns when the owner Rule moved after it. |
| Q6 | A first case has no precedent; matching it to the nearest is a guess. | **Confirmed** | `label` abstains with no precedent, as below the threshold or inside the margin, and the case goes to the agent. |
| Q7 | Precedent applied to a disposition would let past `Y`s stand in for the operator's next one. | **Confirmed** | Precedent settles agent-side calls only; a record whose outcome is a disposition, or whose consequence stands in for an operator's `Y`, is never `precedent`. |

**Survivor (as implemented).** A recurring judgement a play-book step cites is **precedent-derivable**, not complex, when
all six hold:
1. the comparison set is ratified precedents, each labelled with the outcome it set;
2. similarity is over the record's decisive inputs;
3. the set is frozen per version, and rebuilt at a Rule change or a superseding Done;
4. the threshold and margin are fixed, and below or inside them the case goes to the agent;
5. a case that may differ from its precedent stays with the agent;
6. the result settles only agent-side calls, never a disposition.

Otherwise it is **complex** (inference), unless #641's test makes it **mechanical**. A1–A8 stand, A3's fixed set now a
precedent set and A5's authority bar now Q7's.

## Revision 3: precedent is performed mechanically when confident (operator prompt, provenance #642 entry 6: "fold mechanical precedent into #642")
The home falsified "precedent judgement should be mechanically performed" before plan revision 3 (`plans/642.md`).
Revision 2's Q3 survivor, "distinguishing stays inference", is narrowed. The attacks, as the revision records their
survivors:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| R1 | A confident match is as good as a reading; keeping every precedent case with the agent leaves the cost the play-book exists to cut. | **Confirmed** | Precedent is performed mechanically when the match clears the threshold and margin, every structured decisive input equals the precedent's, and the last agreement re-measure meets the bar. |
| R2 | Distinguishing is judgement only on prose; a state, a zone, a count or a commit's existence differs or it does not. | **Confirmed** | A precedent record declares each input structured or prose; `decide` matches on prose and compares each structured input field by field, a difference a `distinguish <field>`. |
| R3 | Agreement measured once goes stale as cases accrue and the code ages. | **Confirmed** | Agreement is stored with its date and the set's base commit, re-measured by the automaton sweep's audit part after each landed merge that touches the set, with an audit sample of recent applications drawn for the agent; below the bar the record is reported `fallen` and the guard warns. |
| R4 | What the code cannot settle must still reach someone. | **Confirmed** | `decide` abstains with its reason — `no-match`, `near-tie`, `distinguish <field>`, `prose-only` — and only those reach inference. |
| R5 | A mechanical precedent for a disposition would decide for the operator. | **Confirmed (Q7 stands)** | Never a disposition. |
| R6 | An outcome the code gave, written back as a precedent, ratifies itself. | **Confirmed** | No mechanical outcome enters a set; `freeze` admits a case only under an operator's `Y` on `main`. |
| R7 | An uncited mechanical outcome cannot be checked. | **Confirmed** | `decide` returns the precedent's row id and score, printed beside every outcome. |

**Survivor (as implemented).** The precedent-derivable outcome of `dyad/dmc/judgement-complexity.jsonld` states revision
2's six conditions as revision 3 narrows them: precedent judgement is performed mechanically when confident, each
application cites its precedent row and score, the residue — no match, a near-tie, a structured difference, a prose input
marked `read`, a fallen record — goes to the agent, and a mechanical outcome becomes a precedent only under a later `Y`
and never decides a disposition.

Survivor implemented: `dyad/dmc/judgement-complexity.jsonld`; the kind `precedent` and its `dyad:precedents`
(`dyad/dmc/schema.md`, `dyad/guards/agent/dmc.py`); `dyad/scripts/similar.py`; the play-book and run-book
`playbook-optimize`.

Cut from: nothing; a new record (plan `agent-corpus/d-work/plans/642.md`).

Disposition: see ledger #642.
