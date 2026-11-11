# Collateral (chronicle craft, Tended rule): pieces that present a product

A form section of the chronicle core (`chronicle.md` §7). It narrows the core and never loosens it: every piece of
collateral is a piece, its record layer cited as §1 says, published only on the Operator's approval (§6). Records:
`../dmc/collateral-review.jsonld`, `../dmc/collateral-pitch.jsonld`; falsification:
`../falsification/rules/collateral.md`. Source: dyad-system d-work #668.

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
     product it cannot show: anchor it or cut it;
  4. **decorated** — ornament the reader cannot use: superlatives, unexplained jargon, more than one idea a sentence.
     Plain words naming a feeling the reader really has are not decoration;
  5. **passes** — every test holds: go on to the kind's own record.
- **The kind's record**, which holds only the tests that kind adds, never the gate's again. A pitch's is
  `collateral-pitch`:
  1. **no-reader** — no named reader, or no one question the pitch answers for them: stop drafting;
  2. **manufactured** — emotion beyond the truth: false urgency or scarcity, fear larger than the real stakes,
     flattery, or a feeling attributed to the reader that the problem the pitch states does not support: strike it;
  3. **cold** — the reader's felt problem is not named in the reader's own terms before the product appears — what
     they worry about, are tired of or want: name it;
  4. **abstract** — no concrete moment the reader recognizes from their own day — a scene, an example, a before and
     after — only categories: show one;
  5. **no-pull** — no picture of what changes for the reader (relief, confidence, time or attention given back) and
     no next step they can take: add both;
  6. **uncountered** — the strongest objection a skeptical reader would raise is not stated with how the copy meets
     it: add it;
  7. **ready** — every test holds: the piece goes to the Operator's publication question (§6). Ready never publishes.

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
