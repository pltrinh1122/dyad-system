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
| 6 | **Adoption collides with the craft while both exist.** `vocabulary.py` `check_craft` fails a craft term equal, folded, to an Agent vocabulary term ("a craft term is referenced there, never defined; Rule-6"), and the craft guard runs on every push (`check --guards`) and in every evidence block. So C2's `VOCABULARY.md` rows cannot land while `crafts/countersign/vocabulary/CRAFT.md` still defines the same terms, and revision 3's sentence that this check "forces the craft to retire after adoption" names the right fence but the wrong moment: the push that adopts is the push the fence refuses. | **confirmed** (observed, a temporary copy with one row added: `crafts/cs/vocabulary/CRAFT.md 'escalate edge': equals the Agent vocabulary term 'escalate edge' (a craft term is referenced there, never defined; Rule-6)`) | Referent before referrer (Rule-1) applied to one term at a time: the row leaves `CRAFT.md` before it enters `VOCABULARY.md`. Two shapes satisfy the fence, both reported to the Operator by this record and by the counsel seat's state, neither taken without a `Y` (Rule-3 Plan: a mutation the plan did not describe is a new plan): (i) a craft-zone PR ahead of C2 that removes from `CRAFT.md` exactly the rows C2's table adopts, with a line naming where each now lives, no `VERSION` bump (the craft is unreleased: no tag, no bundle row, no drift check — the craft's own record R15); or (ii) C2's table lands now and its `VOCABULARY.md` rows land after C5 has deleted the tree, which re-orders the program's chain. The seat recommends (i): it keeps revision 3's order, under which C3's Rule text and C9's craft are written against a vocabulary that already holds the terms. |
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

## C2 — the vocabulary table (d-work #380)
The 39 terms of `crafts/countersign/vocabulary/CRAFT.md` (at `main` `b5cba43`), one disposition each, decided by
the attack in its row. **adopt (C2)**: an Agent Rule already uses the term in the model's sense, so the row may
enter `VOCABULARY.md` as soon as the collision fence admits it (attack 6). **adopt (C3)**: the row enters with
C3's PR, in the sentence C3 writes into Rule-3 or Rule-12, since until then the orphan check (`vocabulary.py`:
every term occurs in at least one Agent Rule) would refuse it. **alias**: no new row; the existing core row's
definition gains the model's name, an edit that collides with nothing and lands with this table. **model-only**:
no Rule uses it; it lives in `dyad/playbooks/countersign-model.md` (C3), outside the vocabulary. **drop**:
nothing in the corpus realizes or reads it. The guard's mention check is a folded substring match (`fold(term)
in fold(rule)`), so the "Rule reads correctly" column is this record's inference per term, as Rule-6 asks, and
never the guard's.

| # | term (craft) | disposition | attack | result | Rule-6: the `used by` Rules read correctly |
|---|---|---|---|---|---|
| 1 | countersign | adopt (C3), owner 3 | No Rule uses the verb; Rule-3 and Rule-12 say "countersign" only as a craft's or a system's name. | survives only with C3: Rule-3's Scope sentence, rewritten to cite the core play-book, names "the countersign model"; the row enters with it | Rule-3 (after C3): the model's name, the verb its definition states |
| 2 | countersignature | alias → `disposition` | Rule-3 uses "the standing countersignature of implicit mode", so a reader may look for a row. | refuted as a second row: a countersignature *is* a disposition (`schema.md` D3 derives one from every `disposed` entry); the `disposition` row's definition names it as the model's word | Rule-3's one use reads as `disposition` |
| 3 | Countersign core | model-only | The eight entities are a schema a Rule could cite. | refuted: no Rule cites the schema; the projector (C4) and the play-book's schema section carry it | — |
| 4 | party | adopt (C2), owner 2, used by 2 3 18 19 | Rule-2 "never the same party", Rule-3 "the party the Operator disposes to", Rules 18/19 "either party" — the ordinary word, not a term. | refuted: each use is exactly the model's sense (who acts; which of the two may dispose); Rule-14's "third-party" is a different word and is not listed | Rule-2: proposer and disposer are two parties; Rule-3: the main Agent is the party disposed to; Rules 18, 19: either party runs a command |
| 5 | act | alias → `d-work` | Rule-3 uses "acts" ("a mandate compresses acts"; "which acts are never accretable"). | refuted as a row: a d-work row *is* one act by projection (#334 C2); the `d-work` row's definition names it as the model's word; the ordinary uses ("three acts in that order") need no term | Rule-3's uses read as `d-work` or as the plain word |
| 6 | countersign mode | adopt (C2) **as `mode`**, owner 3, used by 3 16 | The craft prefixed it to keep `mode` from dsys's `DispositionMode`; in this corpus `mode` is already the row field (Rule-16 Store) and Rule-3's `mode: implicit`. | survives, renamed to the field's own name: no collision exists here, and a term that names a stored field is named as the field is | Rule-3 (Scope, Ledger: the field and its two values), Rule-16 (Store: the optional field) |
| 7 | explicit mode | adopt (C2), owner 3, used by 2 3 | Already referenced by craft name (#290). | confirmed as a use: Rule-2 Binding and Rule-3 Scope both say a row "returns to explicit mode" | Rule-2: the row outside a mandate scope is asked; Rule-3: the escalate edge's destination |
| 8 | implicit mode | adopt (C2), owner 3, used by 3 | As 7. | confirmed: Rule-3 Scope ("the countersign craft's implicit mode under a mandate") | Rule-3: a row born under a mandate's plan-`Y` |
| 9 | automatic mode | model-only | The dyad has no executor and no automatic act (`schema.md` F3, D1). | confirmed: kept in the play-book as the model's third mode, realized by nothing here | — |
| 10 | executor | model-only | As 9. | confirmed | — |
| 11 | basis | model-only | The plan listed it among the terms adopted "today" (#290's record references `countersign:basis`). | refuted for the vocabulary: no Rule uses the word in the model's sense (Rule-11's "basis" is the plain word); the dyad's basis is the `(mandate #<id>)` note on a `disposed` entry, which Rule-3 states by its shape, and the projector derives it (C4, #330 D-3) | — |
| 12 | mandate | adopt (C2), owner 3, used by 2 3 7 15 16 | The craft's definition names `ledger-pr-merge`; the dyad's mandate since #290 is the plan-`Y` of a plan with a mandate scope. | survives with the definition rewritten to the dyad's realization — a standing disposition for one class of row: the plan-`Y` over a stated mandate scope (Rule-3), or an authority preference — the craft's words kept as the model's | Rule-2 (Binding: what a plan-`Y` binds), Rule-3 (Scope, Plan, Ledger), Rule-7 (property 4), Rule-15, Rule-16 (the plan-less accreted row) |
| 13 | countersign proposal | alias → `proposal` | The core already defines `proposal` (Rule-10: anything the Agent asks a disposition on). | refuted as a row: one thing, two words; the `proposal` row's definition names the model's word; a plan file is the proposal of its plan-`Y` (`schema.md` D2) | Rule-10 unchanged |
| 14 | countersign release | alias → `release` | `release` is Rule-11's (a git tag). | refuted as a row: the model's release is the dyad's tag (`schema.md` D5); the `release` row names it | Rule-11 unchanged |
| 15 | countersign event | alias → `sysadmin:event` (in the play-book) | The Agent vocabulary references sysadmin's `event` and may not redefine it (Rule-6 Boundaries). | survives as a play-book alias only: the model's event is a run-book event (`schema.md` D6); recorded in `countersign-model.md`, not in a sysadmin row the core cannot edit | — |
| 16 | escalation | adopt (C2), owner 3, used by 3 | The plan left it open: alias to `incident`, or adopt. | adopt: Rule-3's completion evidence names "every escalation that returned one to explicit mode", which is not an incident (an incident is what the plan did not name; the escalate edge is what the plan's mandate scope did not cover); and `schema.md` D7 derives an escalation from every incident *and* every intake origin — the wider term, with `incident` kept as one of its kinds | Rule-3: the Completion counter-prompt's evidence list |
| 17 | delegate edge | adopt (C3), owner 3 | No Rule names it; the plan-`Y` over a mandate scope *is* the edge (a live disposition becomes a mandate). | survives only with C3: the Scope sentence C3 rewrites names the edge beside the escalate edge it already names; the row enters with it | Rule-3 (after C3): the plan-`Y` that creates a mandate |
| 18 | codify edge | model-only | No automatic mode here (9). | confirmed; the self-diagnostic's `codify?` column (C3's audit play-book) cites the play-book for it | — |
| 19 | escalate edge | adopt (C2), owner 3, used by 3 | As 7. | confirmed: Rule-3 Scope names it | Rule-3: the accreted row returned to explicit mode |
| 20 | check timing | model-only | Rule-20 and sysarch's `guards.md` speak of guards that block before a transaction. | refuted as a term: `before`/`after` is the projector's `Check.timing` (C4); no Rule names the attribute | — |
| 21 | system profile | model-only | A projection detail. | confirmed | — |
| 22 | derivation rule | model-only | D1–D8 are the projector's and move with it (C4). | confirmed; the play-book keeps them as the mapping's record | — |
| 23 | Countersign Interaction Model | model-only | The model's own name. | confirmed: it is the play-book's title, never a term a Rule uses | — |
| 24 | interaction primitive | model-only | The five primitives map onto Rules 3, 7, 10 (#330 §4). | refuted as a term: each primitive is already a core term (prompt and intake, plan and counter-prompt, disposition, completion reply, incident); the table of the mapping is the play-book's | — |
| 25 | initiation | model-only (adopt when a Rule names it) | The plan expected adoption; #330 D-6 found no core entity. | refuted for now: no Rule uses the word; the dyad's initiation is the Operator prompt, the relayed prompt, the intake's `Y` or the mandate's plan-`Y` (Rule-3 Scope, each already a term), and the projector derives it (D8) | — |
| 26 | signal | alias → `intake` | Rule-3 and Rule-16 use "signal" in the plain sense ("engagement signal", "one signal that matters"). | refuted as a row, which would redefine those plain uses: the model's signal is an intake the Operator's `Y` admitted (`CRAFT.md`); the `intake` row names it | Rule-3's and Rule-16's plain uses stay plain |
| 27 | release trigger | model-only | Automatic mode only (9). | confirmed | — |
| 28 | countersign report | alias → `completion reply` | A report "never asks"; the completion reply asks the Done question. | survives scoped: the model's report is the *evidence* the reply carries before its last line (`d-work.md` play-book, step 5); the `completion reply` row names it so | Rule-3 unchanged |
| 29 | answer grammar | adopt (C2), owner 3, used by 3 | As 7. | confirmed: Rule-3's heading of that name | Rule-3: the three answers |
| 30 | amend | adopt (C2), owner 3, used by 3 | As 7. | confirmed: Rule-3 Answer grammar | Rule-3: `N` with text |
| 31 | interaction imperative | model-only | I1–I8 are Rules 2, 3, 7, 9, 10 and the frame (#330 §4). | refuted as a term: the imperatives are the Rules; the play-book keeps the table of which is which and which is checked | — |
| 32 | mode lifecycle | adopt (C3), owner 3 | #330 §7 item 6: Rule-3 cites the craft for the mandate and the escalate edge but not the lifecycle itself. | survives only with C3: the same Scope sentence cites "the mode lifecycle" of the play-book's §4; the row enters with it | Rule-3 (after C3): the sequence an implicit row passes through |
| 33 | form preference | model-only | `preferences-corpus/PREFERENCES.md` uses it (the `accretion` entry). | refuted for the vocabulary: a preference file is instance, not a Rule; no Rule names the class. The play-book keeps §5's classification; the preference text's citation of `crafts/countersign/rules/interaction.md` §5 is the Operator's to re-point (preferences zone; PR-B or its own PR), and `dyad/templates/PREFERENCES.md`'s is C3's | — |
| 34 | authority preference | model-only | As 33. | as 33 | — |
| 35 | command adapter | model-only | The templates move to the core (C4). | confirmed: the play-book's §6 describes them; no Rule names an adapter | — |
| 36 | coded check | adopt (C3), owner 12 | Rule-12 speaks of "a mechanical check" and of inference "stated where it cannot"; the self-diagnostic's two kinds are those two. | survives only with C3: the sentence C3 adds to Rule-12 names the two kinds the audit play-book runs; the row enters with it | Rule-12 (after C3): a test, a guard or an invariant |
| 37 | prose claim | adopt (C3), owner 12 | As 36. | as 36 | Rule-12 (after C3): a claim read against a written attack |
| 38 | diagnostic level | model-only | The grid's cells name the audit play-book's steps (C3). | refuted as a term: no Rule names a level; the play-book's grid does | — |
| 39 | self-diagnostic | model-only | The plan expected adoption. | refuted for the vocabulary: the procedure merges into `dyad/playbooks/audit.md` (C3), which Rule-3 reads as a play-book, a term the vocabulary already holds; no Rule names the diagnostic itself | — |

**Counts.** adopt (C2) 9 — `party`, `mode`, `explicit mode`, `implicit mode`, `mandate`, `escalation`, `escalate
edge`, `answer grammar`, `amend`; adopt (C3) 5 — `countersign`, `delegate edge`, `mode lifecycle`, `coded check`,
`prose claim`; alias 7 — `act`, `countersignature`, `countersign proposal`, `countersign release`, `countersign
event`, `signal`, `countersign report`; model-only 18; drop 0 — every term is realized by the play-book, the
projector or a store, so nothing is dropped, which is itself a finding against "drop" as a needed class.

**What lands with this table (agent zone, collides with nothing).** The six alias edits: the definitions of
`d-work`, `proposal`, `disposition`, `release`, `intake` and `completion reply` each gain the model's word.
**What is held** (attack 6): the nine adopt-(C2) rows, written out below so the PR that lands them is clerical,
and the header sentence of `VOCABULARY.md` that names the countersign craft as a place terms are defined.

| term | definition | owner | used by |
|------|------------|-------|---------|
| party | who acts in the dyad: the Operator (the human party, the sole disposer) or the Agent (the sole proposer); the model's third kind, an executor, the dyad has none of | 2 | 2 3 18 19 |
| mode | the way a row obtains its disposition and who processes it: `explicit` (asked live, per row) or `implicit` (under a mandate); the row's optional field (Rule-16), absent meaning explicit; the model's countersign mode, whose third value, automatic, the dyad does not realize | 3 | 3 16 |
| explicit mode | asked live: the row's plan and completion each take the Operator's own disposition | 3 | 2 3 |
| implicit mode | disposed in advance by a mandate: an accreted row born under the mandate's plan-`Y`, its Done riding the mandate's Done-`Y` | 3 | 3 |
| mandate | a standing disposition for one class of row: the plan-`Y` of a plan that states a mandate scope (Rule-3), or an authority preference (`accretion: implicit`, `ledger-pr-merge: agent`); the model's standing countersignature of implicit mode | 3 | 2 3 7 15 16 |
| escalation | the unexpected returned to the Operator for a live disposition: an accreted row returned to explicit mode by the escalate edge, an incident, or an intake's origin; opens an explicit row or none | 3 | 3 |
| escalate edge | the mode change implicit → explicit: the row's work departs from the mandate scope, so the Agent reports it and asks | 3 | 3 |
| answer grammar | the three answers to a counter-prompt — `Y`, bare `N`, `N` with text (amend) — and what each authorizes (Rule-3) | 3 | 3 |
| amend | the third answer: the proposal refused and its revision asked for in the same words; `N` with text, entered as a `prompt` entry of the refused d-work's own record | 3 | 3 |

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
