# Collateral (chronicle craft, Tended rule): pieces that present a product

A form section of the chronicle core (`chronicle.md` §7). It narrows the core and never loosens it: every piece of
collateral is a piece, its record layer cited as §1 says, published only on the Operator's approval (§6). Records:
`../dmc/collateral-review.jsonld`, `../dmc/collateral-pitch.jsonld`, `../dmc/collateral-lean-canvas.jsonld` and
its nine section records `../dmc/collateral-lean-canvas-<section>.jsonld`, `../dmc/collateral-problem-depth.jsonld`,
`../dmc/collateral-segmentation.jsonld`, `../dmc/collateral-segment-significance.jsonld`,
`../dmc/collateral-segment-rank.jsonld`,
`../dmc/collateral-why-tree.jsonld`; falsification:
`../falsification/rules/collateral.md`. Source: dyad-system d-work #668; the lean canvas, d-work #671; segment significance,
d-work #673; problem discovery, d-work #674; the why-tree, d-work #678; one tree per canvas set, d-work #684; source
trees, their projection and the segment rank, d-work #685; segmentation and the two perspectives, d-work #693.

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

**Segmentation.** A segment is a **cell**, or a named group of cells, on stated axes, never a job title alone. The axes
are an input to the record, never fixed by it; for this instance they are **who holds me to it** (myself · team or
employer · client · regulator or auditor · customers and users), **whose agent** (mine · people I answer for) and **what
it acts on** (code · hosts · content · data). A cell holds segments, never people, and one person may sit in several.
`collateral-segmentation` decides whether a candidate is a segment of the map, and which, before significance and rank,
its outcomes in order: **off-axis** (defined by something other than the axes: restate it as cells) · **idle-axis** (an
axis value that changes no anchor branch: merge across it) · **overlapping** (it shares a cell, or the same problem
classes and anchor branch, with a segment on the map: merge, or name what separates them) · **too-broad** (its readers'
anchor branches differ: split) · **off-class** (it suffers no problem class: its source tree is owed, or it leaves the
map) · **unspanned** (judged over the map: a problem class's sufferers include a cell no segment holds: add one) ·
**cut** (distinct: judge its significance).

**Two perspectives, for corroboration.** The map is read from both ends. **(a) Segment → problem classes**: a segment's
source tree (§6) gives the problem classes it suffers. **(b) Problem class → segments**: a **problem class** is a root
cause of the projection, or a named group of roots, the grouping written down; each class lists the segments that suffer
it. Both are projections of one **segment × class table** in the canvas set's index, each cell labelled from a source
tree or as a hypothesis, rendered as two surfaces, `<canvas set>/by-segment.md` (a) and `<canvas set>/by-problem.md`
(b), never edited by hand. Where they disagree the record acts (`off-class`, `overlapping`, `unspanned`); where they
agree for every segment and class the map is **corroborated**, which is internal consistency, labelled hypothesis until
a reader's evidence refreshes the trees. The order is segmentation → significance → rank.

**The segment map.** A canvas set may map many segments, one folder each, and lists only those whose problem is
significant. `collateral-segment-significance` decides it, its conditions in order: **not-accountable** (the segment
does not answer for work an AI agent did: at most a beneficiary, left off) · **costless** (an unchecked error costs it
nothing real: no money, safety, reputation, regulator or user's trust; left off) · **rare** (such an error does not
recur within the segment's week; left off) · **significant** (all three hold: on the map, each reading labelled
hypothesis or evidence). The record decides who is on the map, never which segment to target: that is the
go-to-market's decision.

**The segment rank.** `collateral-segment-rank` orders the segments on the map, so the next one worked is chosen by a
stated order rather than a reading. Its keys, in order: **harm per week** (the cost of an unchecked error, 3 a
regulator, contract or safety · 2 an outage, a breach or money · 1 reputation or time; times its recurrence, 3 daily ·
2 weekly · 1 rarely within the week) · **served** (2 served today, shown by evidence · 1 in part · 0 not yet, or only
hypothesised) · **nodes added** (how many nodes the segment's source tree is expected to add to the projection, since
the projection exists to screen). Every score is labelled hypothesis or evidence. Its outcomes: **unscored** (a score cannot be read, even as a
hypothesis: put to the Operator) · **tied** (equal on all three keys: put to the Operator) · **ranked** (the order is
recorded in the canvas set's index). It orders the map and targets nothing: the go-to-market picks.

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
4. **Test.** Each node of the segment's source tree by `collateral-problem-depth` — **symptom** · **cause** ·
   **root-cause** (removing it removes most of the symptoms whose branches reach it, the next why reaches the anchor,
   and it does not reword an ancestor in its branch) · **anchor** (the answer is the root anchor itself) ·
   **solution-shaped** (it names a missing feature). **known** (the claim maps to a node already in the projection)
   is a screening outcome, never tested while a source tree is derived. Then the tree by `collateral-why-tree`, in
   order — **open-branch** (a leaf that is neither a root cause, the anchor nor a join) · **circular** (a root cause
   rewords an ancestor in its branch) · **too-deep** (a branch passes five whys) · **no-anchor-branch** (no branch
   reaches the anchor) · **untested** (a root cause has not passed the removal test) · **untagged** (a projected node
   carries no tag) · **untested-tag** (a tag's outcome is root-cause and that tag has no removal-test line) ·
   **unsourced** (a projected line names no source) · **unprojected** (a source line has no projected line) · **stale**
   (the lines no longer match the digest the reader depends on, a source's digest differs from the one the projection
   names, or evidence arrived after the tree was judged) · **ready**. A source tree skips the four projection tests
   (untagged, untested-tag, unsourced, unprojected).
5. **Select** one to three root causes from the segment's ready source tree, ranked first by whether its anchor branch
   exits through them, then by how many of its branches join them. Each canvas problem entry and each symptom beneath
   it cites its **source** id.

**The records: source trees and their projection.** A canvas set keeps two kinds of why-tree.
- **Source trees.** One per segment, `<canvas set>/<segment>/why-tree.md`: the segment's own decomposition, derived
  independently (Adding a segment, below), and its provenance. Header `judged: <outcome> (source <sha256>)`, the
  sha256 of every line after the header (`tail -n +2 why-tree.md | sha256sum`); a file cannot name the commit that
  adds it, so a tree carries a digest of itself instead. Then one node per line, children indented two spaces beneath
  their parent: `<id> [<outcome>; <H|E>] <statement>`, its ids local to the segment and never reused; a join
  `→ <id>`; beneath a root cause `removal test [<H|E>]: …`, counting only the segment's symptoms. Several top-level
  symptoms are allowed, the most prevalent first.
- **The projection.** One per canvas set, `<canvas set>/why-tree.md`, rebuilt from the source trees and never edited
  by hand. Its purpose is screening: when a new problem comes up, it is traversed against the **whole** projection, so
  a problem a segment already explains is caught as a red herring instead of being decomposed again. **Segments are
  tags** on every node, and different segments share nodes. Every line names its sources:
  `N<id> [<tag>: <outcome>, <tag>: <outcome>; <H|E>] <statement> ⟵ <segment>:<id>, …`; a join
  `→ N<id> [<tag>, …] ⟵ <segment>:<id>, …`, naming the source nodes whose join it carries; a removal test
  `removal test [<tag>, <H|E>]: … ⟵ <segment>:<id>`. Its header
  `judged: <outcome> (tree <sha256>; <tag> <sha256>, …; source <segment> <sha256>, …)` holds the projection's digest,
  each tag's (`tail -n +2 why-tree.md | grep -F '<tag>' | sha256sum`) and each source tree's, as projected.
- **Append-only.** In a source tree a node is never edited or deleted, only superseded (`supersedes <id>`), and an id
  is never reused, so a citation stays true of what it said. In the projection a line is rebuilt, never edited by
  hand; a projected id is never reused, and a source node that maps to an existing projected node adds its tag and its
  source to that line — the node's tag list and source list grow, its statement never changes.

**Adding or refreshing a segment.** The projection is updated only through a source tree, in four steps.
1. **Derive** the segment's source tree independently: from its own anchor, through the lenses, by Steps 1–5 above,
   **without reading the projection or another segment's source tree**. The deriving party is briefed with the
   segment, its anchor, this section's Steps and the gate, and the brief is kept with the change, so what it was not
   given can be checked. Reading the projection first fits a new segment onto the segments already there.
2. **Project.** Each source node, in source order, is looked up in the projection (Lookup, below):
   - **known:** it maps to that projected node, which gains the segment's tag, its outcome for the segment, and the
     source; a source edge to a parent the projection places elsewhere becomes a projected join;
   - **new:** it is placed under the projected node its source parent maps to, with the next free `N` id.

   A projected node keeps neutral wording: the first source's words, or, when sources differ, a wording true of each,
   while each segment's own words stay in its source tree. The mapping is the `⟵` list on every line, so the
   projection is a function of the source trees and their mappings, and each pair can be disputed.
3. **Judge** the source tree, then the projection, by `collateral-why-tree`. A changed source makes the projection
   `stale` until it is projected again.
4. **Use.** The segment's canvas cites its source ids. Screening reads the projection, and a red herring is named by
   the projected node and its sources.

**Lookup.** A new problem is matched by meaning against every projected node, whatever its tags, and the match states
the node's id, its path and its sources. A match is **known**: the problem is not new, and if it was raised as new it is
named a **red herring**. It takes the node's outcome for the claim's segment, with its label (an H node validates a claim
as H, never as fact). A known symptom raised again with new information goes into the segment's source tree as a new
symptom node joined to its known parent, with its source, and is projected; it is not decomposed again. A match from a
segment the node is not tagged with is a **tag candidate**, labelled H, until that segment's source tree holds the node
and its removal test. A claim that matches no node is **new**: it is placed in a source tree first and projected, never
judged off the tree. Only a tree judged `ready`, whose lines still match the digest the lookup depends on (the
projection's for screening, the source tree's for a segment's selection), answers; otherwise the lookup says so and
returns no outcome.

**Refresh.** A source tree is re-derived, not merely looked up, at two moments: when evidence from a real reader of the
segment arrives, and before a pitch grounded in it goes to publication. Between those moments a lookup answers. The
projection is rebuilt after every change to a source tree.
