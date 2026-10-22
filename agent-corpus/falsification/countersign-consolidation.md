# Falsification — the consolidation of `dyad-operator` and `countersign`: D-10 decided as (c) carried to its end (d-work #369, child C1 — #374)

The direction of the consolidation the #330 audit elevated as its one design decision
(`agent-corpus/audits/2026-10-17-dwork-countersign-mapping.md` §6, D-10) and chose none of, recorded here as
the Operator's words of #369 and #370 gave it: **countersign is retired as a craft and kept as the model.**
Written by the counsel seat under mandate #369 (plan `agent-corpus/d-work/plans/369.md`, revision 3,
child C1; the attacks below are that revision's, re-run against the tree at the base commit of plan #374,
with four more found while recording). The claim #334 left undecided (`core-vs-countersign.md`, survivor
C1: "which of the two should own the spine going forward is D-10 of #330") is decided by this record's
survivor and by nothing else in it.

## The three directions (#330 §6, D-10), and the one taken
| option | what it does | cost (#330) | result here |
|---|---|---|---|
| (a) stay a profile by projection | keep the stores and the Rules, repair D-1…D-4, land D-5 and D-7; two vocabularies forever, one bridge | days | refused: the Operator asked whether the consolidation was done (#370, 2026-10-21) and then widened #369 to do it (#369 entry 3); (a) is the state #370 found and reported as not done |
| (b) adopt the core natively | rename row→act, plan→proposal, disposition→countersignature, provenance entry→initiation, incident→escalation across every Rule, guard, verb and 319 rows | weeks and a release of every craft | refused: attack 1 below — (c) reaches the same single vocabulary without a rename, because a row *is* an act by projection (#334 C2) |
| **(c) adopt the core's framework vocabulary while keeping the stores** | the direction #290 already took (mandate, implicit mode, escalate edge, amend adopted by craft name, stores untouched), continued to its end | days per row, incremental | **taken, carried to its end**: the core adopts countersign's *vocabulary and model* and keeps its *stores and verbs*; the craft tree is retired once the core carries everything a Rule cites |

**The decision, in one sentence.** The core craft `dyad-operator` becomes the one home of the countersigning
spine's words and model — its vocabulary gains the model's terms where an Agent Rule uses them, a core
play-book holds the rest of the model non-normatively, the projector and the levels check move into the core
with their tests and manifest rows — and `crafts/countersign/` is deleted when nothing a Rule cites remains
under it; its last tree stays reachable as history and no `countersign-v*` tag is cut or moved.

## Attacks (Rule-9)
Rows 1–5 are plan #369 revision 3's, re-run; 6–9 were found while recording and are new to this record.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | This is (b) in disguise: adopting the vocabulary means renaming the stores. | refuted | Rule-6 lets a Rule restate a term's operational consequences without redefining it; a row *is* an `act` by projection (#334 C2, confirmed scoped), and a projection needs no rename. The verbs (`dwork new`, `state`, `retire`) and the files (rows, plans, provenance, incidents) stay; the vocabulary gains the model's terms where a Rule uses them, each row's definition naming the store it is realized by. |
| 2 | Retiring a 0.3.0 craft that two other systems may have installed breaks them (countersign-system, dyad-system #152; the two client repos, #345). | survives, as a sequencing constraint | The craft's last tree stays in history and, if ever tagged, its tag never moves (Rule-11 property 4); no `countersign-v*` tag exists today (`git tag -l 'countersign-*'` is empty at the base commit), so there is nothing to retract. A downstream port is an intake each receiving Operator disposes (Rule-3 Intake), never accretable (Rule-2 Binding). Child C8 (the distribute seat) carries the notice; the port play-book gains one row. |
| 3 | Rule-6 forbids orphans: a craft term no Rule uses cannot enter the vocabulary (`vocabulary.py`: every term occurs in at least one Agent Rule). | confirmed, and used as the rule of the reconciliation | A term enters the Agent vocabulary only where an Agent Rule uses it in the vocabulary's sense; the rest of the model lives in the core play-book, referenced and not defined. Today the Rules already carry `mandate` (2, 3, 7, 15, 16), `implicit mode` (3), `explicit mode` (2, 3), `escalate edge` (3), `amend` (3), `answer grammar` (3), `countersignature` (3), `escalation` (3) in the model's sense; `act`, `party`, `basis`, `signal` occur only in their ordinary sense, so each of those is a C2 decision, not an adoption by count. |
| 4 | The projector and the self-diagnostic's levels check are code with checks (Rule-12); moving them is a test-mapping change under syseng's guard (`syseng/tests`), a manifest change (Rule-14) and a naming change (`syseng/naming`). | survives, scoped | One child (C4, the engineer seat) moves the code with its tests and manifest rows together, through `check --evidence`; the test mapping is read from the guard, never from memory. |
| 5 | `escalation` (craft) and `incident` (core) are not the same thing, and `initiation` has no core entity (#330 D-6). | survives, as the reconciliation's hardest rows | Decided in C2's table, each with its own attack, never by renaming: an incident is one kind of escalation (#330 §4; `schema.md` D7 derives an escalation from every incident row *and* from every intake origin), so `escalation` is the wider term and `incident` keeps its row; `initiation` is a derived profile field (D8) with no store of its own. |
| 6 | **Adoption collides with the craft while both exist.** `vocabulary.py` `check_craft` fails a craft term equal, folded, to an Agent vocabulary term ("a craft term is referenced there, never defined; Rule-6"), and the craft guard runs on every push (`check --guards`) and in every evidence block. So C2's `VOCABULARY.md` rows cannot land while `crafts/countersign/vocabulary/CRAFT.md` still defines the same terms, and revision 3's sentence that this check "forces the craft to retire after adoption" names the right fence but the wrong moment: the push that adopts is the push the fence refuses. | **confirmed** | Referent before referrer (Rule-1) applied to one term at a time: the row leaves `CRAFT.md` before it enters `VOCABULARY.md`. Two shapes satisfy the fence, both reported to the Operator by this record and by the counsel seat's state, neither taken without a `Y` (Rule-3 Plan: a mutation the plan did not describe is a new plan): (i) a craft-zone PR ahead of C2 that removes from `CRAFT.md` exactly the rows C2's table adopts, with a line naming where each now lives, the craft's `VERSION` to 0.3.1 — the craft is unreleased, so no bundle row and no drift check is touched (Rule-11 property 7); or (ii) C2's table lands now and its `VOCABULARY.md` rows land after C5 has deleted the tree, which re-orders the program's chain. The seat recommends (i): it keeps revision 3's order, under which C3's Rule text and C9's craft are written against a vocabulary that already holds the terms. |
| 7 | Rule-11 property 2 says a core Rule citing a craft by path is *the* reason to bundle one; the taxonomy audit (P10) found countersign cited five times by Rule-3 and never bundled. Retiring the craft, rather than bundling it, leaves that disagreement unresolved. | refuted | The consolidation removes the cause rather than paying for the symptom: after C3 every citation is to a core path (`dyad/playbooks/countersign-model.md`, `dyad/vocabulary/VOCABULARY.md`), so the core ships what its Rules depend on by construction, and the permanent `warn` line P10 describes on a receiving system disappears with the citation. Bundling would have kept two vocabularies (attack 3). |
| 8 | Rule-13 property 1 says the terms are *adopted, not coined*; moving their definitions into the core turns adoption into authorship and loses the provenance that justified it. | refuted | Adoption is of the words and the model, and the model's own provenance travels with it: C3 moves the craft's three falsification records into `dyad/falsification/` and the play-book opens by naming the craft, its version and its records as the model's source (Rule-7 property 4 for the Operator's words; the Agent's text has its own homes). The core already authored the craft (#146–#156, #334 attack 1.5), so the direction of adoption was never outward. |
| 9 | Easy agreement (Rule-9 Conditions): the direction reads naturally after #330, #334 and #370, and the Operator already said it. | pushed to 6 | Attack 6 is confirmed and changes C2's shape; a disposition is not a claim (Rule-9 Boundaries), but the plan that carries it out is, and it was falsified. |

**Survivor.** D-10 is (c) carried to its end, under the five children of plan #369 revision 3 that touch the
craft and its words (C1–C5), with one sequencing survivor from attack 6: a term is removed from the craft's
vocabulary before it is defined in the core's, by a craft-zone PR the Operator disposes, or by C5 running
before the adoption rows land. Nothing in the stores, the verbs or the 319-plus rows is renamed.

## The reconciliation rule (C2 fills the table)
Each of the craft's 39 terms (`crafts/countersign/vocabulary/CRAFT.md` at the base commit) takes exactly one
of four dispositions, each decided by an attack in C2's table, appended to this record:
- **adopt** — becomes an Agent vocabulary row, owner the Rule that uses it, `used by` every Rule that does;
- **alias** — the same thing as an existing core term; one definition kept, the craft's name recorded in the
  definition as the model's name for it (`act` → `d-work` by projection, `countersign proposal` → `plan`,
  `countersignature` → `disposition`, `countersign release` → `release`, `countersign event` → `event`;
  `escalation` → `incident` *or* adopted, by attack);
- **model-only** — no Rule uses it; kept in the model play-book, outside the vocabulary;
- **drop** — nothing in this corpus realizes or reads it.
`vocabulary.py` (owner, no orphan, no duplicate, `used by`) is the mechanical check of the table's *adopt*
rows; `check_craft`'s collision check is the fence attack 6 names.

## The children, by zone (plan #369 revisions 3–5; seats of S0)
| child | zone | seat | content |
|---|---|---|---|
| C1 | agent | counsel | this record; the #330 audit's D-10 row marked decided by reference |
| C2 | agent (and, per attack 6, one craft-zone PR or a re-order the Operator disposes) | counsel | the 39-row table appended here; `VOCABULARY.md` gains the adopted rows; Rule-6's condition stated per term |
| C3 | agent | counsel | `interaction.md` and `schema.md` → `dyad/playbooks/countersign-model.md`; `self-diagnostic.md` → `dyad/playbooks/audit.md` with its run-book template; the three craft records → `dyad/falsification/`; Rules 3 and 12 cite core paths |
| C4 | agent | engineer | the projector, `levels.py`, the command templates, the schema file and the levels seed → the core, with tests and manifest rows; the bridge repaired (#330 D-1…D-4) |
| C5 | craft | counsel | `crafts/countersign/` deleted; `check_craft` no longer sees it |
| C6 | infra | distribute | `BUNDLE.md` line removed; `crafts/REGISTRY.md` row if present (craft zone, with C5); CI green on `main` |
| C7 | agent, then preferences | engineer | M4's core side on the consolidated vocabulary; PR-B is the Operator's |
| C8 | none here | distribute | the downstream notice and the port play-book row |
| C9 | craft | counsel | the `cos` craft, born after C2, requiring the core only |
Order: C1 → C2 → C3 → C4 → C5 → C6 → C7 → C9; C8 with C6. Referent before referrer at every step (Rule-1).

## Not decided here
The preference value (`organization`, PR-B: the Operator's own PR, Rule-2 *Not ratification*); the core
release that follows C6 and the `cos-v0.1.0` release (Rule-11 ratification events, each asked as its own
`Y/N: release <tag>?`); the downstream ports (intakes). Each is on plan #369's never-accretable list.

Disposition: see ledger #369 (the mandate's Done-`Y` names #374 among the rows accreted under it).
