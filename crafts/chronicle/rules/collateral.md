# Collateral (chronicle craft, Tended rule): pieces that present a product

A form section of the chronicle core (`chronicle.md` §7). It narrows the core and never loosens it: every piece of
collateral is a piece, its record layer cited as §1 says, published only on the Operator's approval (§6). Records:
`../dmc/collateral-review.jsonld`, `../dmc/collateral-pitch.jsonld`, `../dmc/collateral-lean-canvas.jsonld` and
its nine section records `../dmc/collateral-lean-canvas-<section>.jsonld`, `../dmc/collateral-problem-depth.jsonld`,
`../dmc/collateral-segment-significance.jsonld`, `../dmc/collateral-why-tree.jsonld`; falsification:
`../falsification/rules/collateral.md`. Source: dyad-system d-work #668; the lean canvas, d-work #671; segment significance,
d-work #673; problem discovery, d-work #674; the why-tree, d-work #678.

## 1. What collateral is
**Collateral** is a piece whose job is to present a product to a reader: a pitch (a README opening, a site's front
page, a press release's lede, a short post), a lean canvas, a product vision board, or one element of either. It has
no style guide and no structure here yet; those wait for real copy (Rule-13 of the core: recurrence proposes them).

## 2. How a piece of collateral is judged
Every piece answers one question before it reaches the Operator: **what does it need before it is put to the
Operator?** Two records answer it, in order, and in each the tests run in a fixed order and the first that fails gives
the outcome.
- **The gate**, `collateral-review`, which every piece passes first, whatever its kind:
  1. **fenced** — it names a private repository, a client, an employer, a person or personal context: strike it before
     anything else;
  2. **invented** — it claims a capability the system's own statement of purpose and its practice do not hold: cut
     the claim;
  3. **unanchored** — a claim cites no path, command output or count, was not falsified, or compares with a named
     product it cannot show: anchor it or cut it. An entry of a lean canvas labelled hypothesis claims nothing as
     fact and passes (§5); a pitch's claims face the reader and never do;
  4. **decorated** — ornament the reader cannot use: superlatives, unexplained jargon, more than one idea a sentence.
     Plain words naming a feeling the reader really has are not decoration;
  5. **passes** — every test holds: go on to the kind's own record.
- **The kind's record**, which holds only the tests that kind adds, never the gate's again. A pitch's is
  `collateral-pitch`:
  1. **no-reader** — no named reader, or no one question the pitch answers for them: stop drafting;
  2. **ungrounded** — the pitch's reader, problem or value proposition does not trace to a section of the lean canvas
     the Operator accepted (§5): ground it there, or ground the canvas first;
  3. **manufactured** — emotion beyond the truth: false urgency or scarcity, fear larger than the real stakes,
     flattery, or a feeling attributed to the reader that the problem the pitch states does not support: strike it;
  4. **cold** — the reader's felt problem is not named in the reader's own terms before the product appears — what
     they worry about, are tired of or want: name it;
  5. **abstract** — no concrete moment the reader recognizes from their own day — a scene, an example, a before and
     after — only categories: show one;
  6. **no-pull** — no picture of what changes for the reader (relief, confidence, time or attention given back) and
     no next step they can take: add both;
  7. **uncountered** — the strongest objection a skeptical reader would raise is not stated with how the copy meets
     it: add it;
  8. **ready** — every test holds: the piece goes to the Operator's publication question (§6). Ready never publishes.

## 3. Emotion is a claim
A feeling a piece names is a claim about its reader. It is anchored to the problem the piece states, or to the reader
as the piece's brief names them (`../templates/brief.md`, Audience), and judged by inference. Feeling is required of a
pitch, and never made up: **cold** asks for it, **manufactured** strikes what goes beyond the truth.

## 4. The family
- One record per kind, `collateral-<kind>` (`collateral-pitch`; later, on their own prompts,
  `collateral-lean-canvas`, `collateral-vision-board`), and one per element judged alone,
  `collateral-<kind>-<element>` (e.g. `collateral-lean-canvas-unfair-advantage`).
- Each answers "what does this <kind> need before it is put to the Operator?", its tests in a fixed order, its last
  outcome **ready**, which never publishes. A kind that needs feeling takes the pitch's outcome names for it.
- Every record is judged by inference: the agent applies it to its own draft before the draft is shown, and the
  Operator may apply it to any piece. Agreed rulings may later become precedents (the core's
  `dmc:judgement-complexity`).

## 5. The lean canvas: the foundation a pitch is crafted from
A **lean canvas** is not put to a reader. It is the foundation: every pitch's reader, problem and value proposition
trace to its sections (`ungrounded`, §2). It is judged in this order — the gate, then each section's record in any
order, then the fit record — and a canvas the fit record finds ready goes to the Operator to be **accepted** as the
foundation the pitches cite. It is never published by any record. Each section's sub-field is judged inside that
section's record. An entry is labelled **hypothesis** or **evidence**; a hypothesis passes the gate's `unanchored`, and
the fit record fails a canvas whose entries are not labelled.

| section record (`collateral-lean-canvas-…`) | outcomes, in precedence |
|---|---|
| `problem` | **solution-shaped** (written as the lack of the solution) · **symptom** (it states what the segment observes, not the root cause it would remove; `collateral-problem-depth`, §6) · **not-theirs** (not in the segment's own words) · **unranked** (more than three, or none marked top) · **no-alternatives** (what the segment uses today is missing) · **ready** |
| `customer-segments` | **too-broad** (one person in it cannot be found) · **no-early-adopters** · **ready** |
| `unique-value-proposition` | **not-one-line** · **not-tied** (not to the top problem) · **pitch-fails** (fails `collateral-pitch`'s no-reader, cold or abstract) · **ready** |
| `solution` | **untied** (a feature names no problem) · **not-minimal** (more than one feature for a top problem) · **ready** |
| `channels` | **vague** (a category, not a path) · **unreachable** (it does not reach the early adopters) · **ready** |
| `revenue-streams` | **empty** (no model, and no "none, and why") · **unpriced** (no price, or one unrelated to the value) · **ready** |
| `cost-structure` | **empty** · **incomplete** (omits what the canvas's own solution or channels cost) · **ready** |
| `key-metrics` | **vanity** (counts activity, not the value received) · **uncountable** · **ready** |
| `unfair-advantage` | **copyable** (a competitor could copy or buy it; "none yet", said honestly, passes) · **ready** |

**The fit record**, `collateral-lean-canvas`, holds only what crosses sections: **unmarked** (entries unlabelled, or no
riskiest assumption named) · **section-fails** (a section record is not ready) · **unmapped** (features and problems
do not match one to one) · **misaimed** (the value proposition, channels or metrics aim at another segment, or a
problem does not trace to the root anchor, §6) · **off-tree** (a problem entry or a symptom cites no node of the
segment's why-tree, or its node's outcome differs: a problem entry must be a root-cause node, a symptom a symptom node) ·
**ready**.

**What the canvas grounds** (pitch test ← section): `no-reader` ← customer segments and early adopters; `cold` ←
problem, in the segment's words; `no-pull` ← unique value proposition and solution, the next step ← channels; the
gate's `invented` and `unanchored` ← every labelled section. Partly: `manufactured` ← problem and existing
alternatives; `uncountered` ← existing alternatives and unfair advantage.

**Gaps**, named for augmentation by later records and built by none yet:
1. **the reader's moment** — no section holds a concrete scene from the reader's day, which `abstract` asks for;
2. **objections** — the canvas lists alternatives, not the objections a skeptical reader raises;
3. **the stakes** — the problem section states the problem, not what leaving it unsolved costs the reader.

**The segment map.** A canvas set may map many segments, one folder each, and lists only those whose problem is
significant. `collateral-segment-significance` decides it, its conditions in order: **not-accountable** (the segment
does not answer for work an AI agent did: at most a beneficiary, left off) · **costless** (an unchecked error costs it
nothing real: no money, safety, reputation, regulator or user's trust; left off) · **rare** (such an error does not
recur within the segment's week; left off) · **significant** (all three hold: on the map, each reading labelled
hypothesis or evidence). The record decides who is on the map, never which segment to target: that is the
go-to-market's decision.

## 6. Problem discovery: diverge by lens, decompose as a tree
A problem entry names a **root cause**: what the segment would remove, not what it observes. It is found by a
jobs-to-be-done statement (the anchor), a fishbone's categories (the divergence) and the five whys asked as a tree (the
decomposition), and it is kept as a record, the **why-tree**, so that a claim is checked by looking it up rather than by
deriving the whys again.

**Steps.**
1. **Anchor.** The **root anchor** is the system's own problem: a person accountable for what an agent did must trust
   it enough to answer for the result (`site/identity.jsonld`, `dyad:problem`, for this instance). Write it for the
   segment: "When I let an agent `<act>` on `<what I answer for>`, I want to trust it enough to answer for the result,
   so that `<the stake>`."
2. **Diverge, by lens.** At least two statements per lens, none judged yet; a statement fitting no lens is kept as
   *other*. The ten lenses of trust: **visibility** (can I see what it did), **verifiability** (can I check it is
   right), **predictability** (will it do what it said), **reversibility** (can I undo it), **attribution** (can I show
   who decided), **competence** (does it know this domain), **intent** (did it understand what I meant), **attention**
   (do I have time to check), **consequence** (what breaks if it is wrong), **accountability to others** (who will hold
   me to it).
3. **Decompose, as a tree.** Each symptom is a node; each node is asked why, and may have several answers, each a
   child. An answer already in the tree is a **join**, recorded by its id and never copied. One branch always asks the
   reverse question, "why do I feel I must do this at all?", the **anchor branch**, which shows what the symptom
   protects. A branch stops at a root cause, at the anchor, at a join, or at five whys: five is a ceiling, never a
   quota.
4. **Test.** Each node by `collateral-problem-depth` — **symptom** · **cause** · **root-cause** (removing it removes
   most of the symptoms whose branches reach it, the next why reaches the anchor, and it does not reword an ancestor in
   its branch) · **anchor** (the answer is the root anchor itself) · **solution-shaped** (it names a missing feature).
   Then the whole tree by `collateral-why-tree`, in order — **open-branch** (a leaf that is neither a root cause, the
   anchor nor a join) · **circular** (a root cause rewords an ancestor in its branch) · **too-deep** (a branch passes
   five whys) · **no-anchor-branch** (no branch reaches the anchor) · **untested** (a root cause has not passed the
   removal test) · **stale** (the node lines no longer match the header's digest, or evidence arrived after the tree was judged) · **ready**.
5. **Select** one to three root causes from a ready tree, ranked first by whether the anchor branch exits through
   them, then by how many branches join them. Each canvas problem entry and each symptom beneath it cites its node id.

**The record.** One tree per segment, `<canvas set>/<segment>/why-tree.md`. Its header line is
`judged: <collateral-why-tree outcome> (nodes <sha256>)`, the sha256 of the file's node lines, every line after the
header as committed (`tail -n +2 why-tree.md | sha256sum`). A file cannot name the commit that adds it, so the tree
carries a digest of itself instead. Then one node per line, children indented beneath their parent:
`N<id> [<outcome>, <H|E>] <statement>`, a join as `→ N<id>`, and a node that replaces another adds `supersedes N<id>`.
The tree is **append-only**: a node is never edited or deleted, only superseded, and an id is never reused, so a
citation of a node stays true of what it said.

**Lookup.** A claim that a problem is a symptom or a root cause is answered from the tree. Lookup matches by meaning,
states the node's id and its path to the symptom, and returns the node's outcome **with its label**: a node labelled H
validates a claim as H, never as fact. Only a tree judged `ready`, whose node lines still match its digest,
answers; otherwise the lookup says so and returns no outcome. A claim that matches no node is placed in the tree first,
never judged off it.

**Refresh.** The tree is re-derived, not merely looked up, at two moments: when evidence from a real reader of the
segment arrives, and before a pitch grounded in it goes to publication. Between those moments a lookup answers.
