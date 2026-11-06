# Intent and scope: a ledger audit (2026-11-06)

*Audit for d-work #615, filed by counsel-0032b4c0 from plan #615's Evidence section (602 rows, read 2026-11-06 at
`05bd60a8`). It measures how often the operator refused a proposal to restate intent or scope, and how many rows were
abandoned. It disposes nothing: what it supports is the decision criterion `dyad/dmc/intent-reading.jsonld` and the
preference `intent-reading`, which plan #615's plan-`Y` authorized.*

## Where rows come from

| source | rows |
|---|---|
| a prompt answered by a plan or Done question | 349 |
| carried under a mandate | 103 |
| an operator `Y backlog` | 70 |
| intakes and other dispositions | 80 |

## Refusals
61 `N` entries on 36 rows: 49 plan, 6 done, 5 amend, 1 release. Provenance holds the operator's words for 60 of them.

| class | entries | rows | an intent reading would have |
|---|---|---|---|
| I. intent or scope restated: the operator says what was wanted | 27 | #116, #137, #145, #146, #148, #149, #174, #184, #191, #221, #223, #231, #290, #302, #336, #366, #368, #369, #461, #496, #531, #532, #564 (23) | asked it before the plan |
| of which `N done`: a whole delivery refused | 6 | #145, #146, #148 (2), #149, #184 | saved a delivery |
| II. a design challenged once proposed ("falsify") | 19 | #100, #152, #175, #178, #216, #252, #293, #336, #366, #368, #369 | not changed: needs the proposal |
| III. scope added in flight | 5 | #336 | partly: scope bounds asked first |
| IV. order or timing | 5 | #113, #155, #185, #369 | not changed |
| V. wrapped up for a hand-over | 3 | #221, #222, #336 | not changed |
| VI. a release held | 1 | #489 | not changed |

The 60 entries by class, each `#<row> e<n>` a provenance entry number:
- **I (27):** #116 e2; #137 e2; #145 e2; #146 e2; #148 e2, e3; #149 e2; #174 e2; #184 e2; #191 e2; #221 e3; #223 e2;
  #231 e2; #290 e2; #302 e2; #336 e2, e3; #366 e2; #368 e6, e7; #369 e3, e7; #461 e3; #496 e2; #531 e2; #532 e4;
  #564 e2. Of these, refusals of a delivered Done: #145 e2, #146 e2, #148 e2 and e3, #149 e2, #184 e2.
- **II (19):** #100 e2; #152 e2; #175 e2, e3; #178 e2, e3; #216 e2; #252 e2; #293 e2; #336 e11 to e16; #366 e3;
  #368 e2, e3; #369 e2.
- **III (5):** #336 e5 to e9.
- **IV (5):** #113 e2; #155 e2; #185 e2; #369 e5, e6.
- **V (3):** #221 e4; #222 e2; #336 e10.
- **VI (1):** #489 e4.

Quoted examples of class I:
- #191 e2: "The counter aligns more with the spirit of my intent".
- #532 e4: "most of the issue is the harness restricting rather than seats expanding".
- #461 e3: the release workflow plan refused, a released service asked for (the row's note; the entry is a bare `N`).
- #184 e2 (done): "why do we need to stop the write during testing?".

### Re-read, entry by entry
Each of the 60 entries was re-read against its provenance record on `main` (2026-11-06). The classes above are filed
as plan #615 drew them. Three entries read differently on this re-read. They are findings, and the classes above are
not changed for them:
- **#336 e2**, "evaluate CLI-based query versus "SQL-like" syntax": reads as II, an evaluation asked of the
  proposal, rather than I.
- **#155 e2**, "don't we have a local CI check test set up? evaluate performing unittest during commits only": reads
  as II, a design challenged, rather than IV.
- **#369 e6**, "before doing so, what should the primary cos ("leader") be named?": reads as I, a question about what
  is wanted, rather than IV.

Applied, the counts would be I 27, II 21, IV 3, the rest unchanged. Class I, the one the intent reading acts on
directly, keeps 27 entries (45%) either way.

## Re-planning and clarification
- 70 of 373 plan files carry revision headings, and 31 have three or more. The most revised: #336 and #570 (16
  each), #369 (13), #252 (9), #532 (7).
- 24 rows hold three or more prompt entries: #498 (49), #570 (16), #609 (11), #561 (8), #252 (7).

## Overlap and duplication
- Incidents:
  - #3: a concurrent session had already landed the identical fix.
  - #30: duplicated execution of #23, which another session owned.
  - #81: a delegated draft written on a false premise ("#82 has since repaired").
  - #221: "no bus exists", read from the wrong branch.
  - #348: a prompt read as opening nothing.
- Retirements: 21 rows were retired as carried by other rows (retirement batch 5).

## Abandoned
- 82 rows are archived, every one never worked. They spent a median of 25 days in backlog (maximum 49) before
  retirement. Their origins:

  | origin | rows |
  |---|---|
  | an operator `Y backlog` | 39 |
  | carried by a mandate | 17 |
  | intakes | 15 |
  | the archive is the first recorded entry (legacy) | 10 |
  | `Y open backlog` | 1 |

- 22 rows were in backlog at the reading. Nine were older than 30 days (#4, #5, #60, #96, #97, #102, #139, #177,
  #181), and the scheduled sweep had named five of them that morning.
- #498 (`planned`) and #503 (`open`) had been quiet since 2026-10-27. They are the chronicle, long-lived by the
  operator's design, so not abandoned.

## What an intent question would reduce
- Directly: class I, 27 of 60 refusals (45%), on 23 of the 349 prompt-opened rows (6.6%). Six of them refused whole
  deliveries.
- Partly: class III; the four overlap incidents, through the candidate search over live rows; and false premises in
  any portion, a backlog row a prompt reopens included.
- Not at all: classes II and IV to VI, and backlog filed by a disposition, which the sweep's hygiene already watches.

## Disposition
Disposed by the done-`Y` of d-work #615 (Rule-2); see ledger #615.
