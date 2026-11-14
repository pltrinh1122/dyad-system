# Falsification record — Rule-2 (no-self-ratify)

**Claim (operator, 2026-09-12):** codify `no-self-ratify` in `agent-corpus`, adopt immediately;
rules inject via CLAUDE.md on restart; Rule-1 and Rule-2 are orthogonal with clear
separation of concerns.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "No-self-ratify" names no operational target. | Refuted as stated | Enumerate ratification events: merge/push to `main`, closing a Disposition, finalising an agent verdict. |
| 2 | Blanket approvals leak. Operator's "Y" to merge #1–#3 was reused by the agent to merge #4 and #6; #6 was never ratified. | **Confirmed failure, already occurred** | A Y binds to the named PR(s) only; recovery PRs need a fresh Y. |
| 3 | Not mechanically enforceable: one GitHub identity proposes and merges. | Survives, scoped | Inference-only; stated in the rule. |
| 4 | "Adopt immediately" conflicts with needing ratification to codify. | Refuted | Behaviour adopts now; text lands on operator merge. This PR is left open by the agent. |
| 5 | Memory cache is self-written and self-acted-on. | Survives, scoped | Cache of ratified corpus; corpus wins. |
| 6 | Orthogonality: any future Rule-2 mechanism lives in infra, so Rule-1 governs where Rule-2's enforcement changes. | Survives with caveat | Mechanisms disjoint (shape vs. actor). One-way dependency, no overlap of concern. |
| 7 | CLAUDE.md import chain (`@agent-corpus/CLAUDE.md` → `@rules/*`) untested; agent file did not exist at session start. | Passed 2026-09-12 | Sentinel added; on operator restart the agent produced `covalent-sentinel-2026-09-12` — all three hops load. |

## Rule-5 pairwise (#125, Binding edited): 2–3: Rule-2 defines what counts as green for the merge the Done-Y ratifies; Rule-3 owns the reply that states it — cited, not redefined. 2–14: Rule-14 owns the kernel-only path and the adapter's manifest row; Rule-2 consumes it as evidence (dependency, no overlap). Others unchanged. Coherent, orthogonal. Record: `agent-corpus/falsification/ci-absent.md`.

## #138 amendment (Binding: kernel path primary, local merge when hosting is unreachable)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 8 | Widens Rule-2: merges without hosting, silently. | Refuted | Amended in the open; the Y still binds only to named PRs; a local merge is clerical execution of a given Y exactly as a hosted merge is. |
| 9 | The Operator ratified on CI's green, now on an Agent-pasted block — weaker. | Refuted | CI never was a second party (#125 attack 1); the block is reproducible on the same head, which a CI badge is not. |
| 10 | A pasted block can be edited. | Survives, scoped | Its sha256 covers head, tree and every line; the Operator re-runs and compares; forgery remains inference-only, as stated. |

Rule-5 pairwise (#138, Binding edited): 2–3: Rule-3 owns the completion reply; Rule-2 names what green means and cites the block. 2–14: Rule-14 owns the kernel-only path and the evidence block; Rule-2 consumes them (dependency, no overlap). 2–15/16: local merge changes no row semantics; the fence still judges `main`. 2–1, 2–4, 2–5, 2–6 (one term, owner 14, used here), 2–8, 2–9, 2–10, 2–11, 2–12, 2–13, 2–17, 2–18, 2–19: unchanged. Coherent, orthogonal. Record: `agent-corpus/falsification/self-ci.md`.

Disposition: see ledger #11 (done 2026-09-12).

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
fence path: `dyad/scripts/main_fence.py` → `dyad/guards/agent/rows.py`; mechanical checks live under `dyad/guards/` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## #168 amendment (2026-09-14): local CI first
| # | attack | result | survivor |
|---|---|---|---|
| A | Without PR-triggered CI a hook-skipping session merges unchecked. | Survives, scoped | The evidence block on the exact head is the gate (Rule-2 Binding, #138); CI was never the gate since #125. |
| B | `main` pushes still spend quota on ledger commits. | Confirmed | Workflows ignore `agent-corpus/d-work/**`. |
Pairwise: Rule-2 gains one clause on *when* hosted CI runs; Rule-14 owns the adapter's place, Rule-2 what a Y relies on, Rule-3 the plan gate's mechanism — no concern moves. Coherent and orthogonal with every other Rule as before.


## Amendment — d-work #290 (2026-10-14, Binding: a plan-`Y` may carry a mandate)
**Claim (Operator, 2026-10-14):** individual dispositions can be superseded with a
"meta-disposition" — in the adopted vocabulary of `crafts/countersign/`, a `countersign:mandate`,
the standing countersignature of `countersign:implicit mode`. Binding's first sentence forbids it as
written: "A `Y` binds only to the PR(s) or action(s) named in the question it answers." It gains the
mandate clause — a plan-`Y` also authorizes the **class** of row the plan's stated mandate scope
names, and the Done-`Y` ratifies the **accreted set as the completion evidence listed it**. Nothing
leaves the Ratification events list, and nothing joins it.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 11 | Carried authority is self-ratification by another name: the Agent writes the plan, so the Agent writes the bound on what it may accrete. | **Confirmed, and answered structurally rather than argued away.** Three fences, none of them an appeal to conduct: the **mandate scope** is a stated rule and a stated ceiling the Operator reads before disposing; the **escalate edge** returns anything outside it to explicit mode; and the Done-`Y` is asked over the **delivered** set, enumerated row by row in the completion evidence, not over the promised one. That asymmetry — authority forward over a *class*, verification backward over an *enumeration* — is the whole difference from moving the merge ratification onto a promise. | What a mandate authorizes is a **row**: a ledger artefact this Rule's own *Not ratification* list already calls clerical. It never authorizes a merge, a release, a destructive host action, a preference change or a mutation the plan did not describe. |
| 12 | A mandate over rows that do not yet exist is a blank cheque, and plan #259's own Limits admit a plan "cannot name the children it will open". | **Confirmed, and it is why this Rule is edited rather than read around.** Binding's "named in the question it answers" cannot be stretched by inference to cover an unnamed set. The honest form is that a `Y` may bind to a **class the question states** and a mechanism can decide. | The clause requires both: the class stated in the plan the `Y` answers, and the delivered instances enumerated before the Done-`Y`. Without the stated ceiling and without the `mode` field that makes the class data rather than prose, this is the blank cheque the attack names — so the two are the condition of the clause, not extras. |
| 13 | The Done-`Y` already has a defined scope; letting it ratify a set the Agent chose to accrete weakens the one verification this system has. | **Survives, scoped.** The set is not chosen at the Done question: it is the set the plan described, minus what escalated, listed with what each row holds and what it cost. A row the Operator will not have is refused by answering `N` to the same question, exactly as a batch's `N` authorizes none of its named set. | The existing batch rule is reused verbatim rather than a new one invented: a `Y` ratifies exactly the named set, each item still checked against its own evidence and its own heads-unchanged condition. The accreted list is what makes the set nameable. |
| 14 | The ledger cannot hold a standing authorization, so a mandate is unrecordable: `rows.ENTRY` (`dyad/guards/agent/rows.py:40`) admits only a dated `Y` or `N`, and `dyadlib.FIELDS` (`dyad/scripts/dyadlib.py:439`) is closed by a pure import-time invariant, so an extra line parses clean and is silently dropped. | **Refuted, and the premise was revision 4's single unchecked inference.** The entry is `<date> Y plan (mandate #<id>)` — replication of the Operator's own act with a note, the shape the column already carries for `(batch #a,#b,#c)` — and its matching provenance entry is the mandate's own words, which this Rule's own batch precedent already blesses across several records ("the Operator's one `Y` is written as the same entry into every named d-work's own record", Rule-3 Batch disposition). Two rows prove the entry form writable and shape-legal today: #96 and #97 carry `2026-09-18 Y plan (named in plan 94.md, deferred)`. | No field is added to carry it. The `mode` field this d-work adds says which mode a row is in; the authorization itself is the entry plus the words. |
| 15 | #96 and #97 are therefore the precedent, so no Rule edit is needed at all. | **Refuted, and the half that fails is the half the first plan leaned on.** Both are `backlog`, so `prs.py:44` refuses them on **state** before it ever reaches the `Y plan` test, and neither has a plan file: they have never passed the plan gate. | The only real precedent for a row *working* under inherited authorization is #162–#165 under #199 — one shared batch Done-`Y`, no `Y plan` entry, no plan file, all four `done` — and it is a better one. An implicit-mode row must be born `open` for that reason. |

**Rule-5 pairwise (#290, Binding edited).** **2–3**: Rule-3 owns the plan and completion forms, the
mandate scope a plan must state and the accreted list a completion reply must carry; Rule-2 owns
only what the `Y` binds to. One-way each, as for the batch counter-prompt (#17). **2–7**: Rule-7
stores the mandate's words verbatim with their note and checks them against the row's `disposed`
count per commit; Rule-2 never reads a record. **2–15**: the accreted row's plan is the mandate's
plan file, which Rule-15 owns. **2–16**: `backlog → archived` is Rule-16's table; the retirement
disposition is an Operator act this Rule's Ratification events already cover by Rule-3's reference,
and no new event is declared here. **2–8**, **2–11**: a destructive host action and a release are
never accretable, so Rule-8's own counter-prompt and Rule-11's release events are untouched.
**2–1**, **2–4**, **2–5**, **2–6**, **2–9**, **2–10**, **2–12**, **2–13**, **2–14**, **2–18**,
**2–19**, **2–20**: unchanged — zones, rule shape, coherence, terms, falsification, framing, code
paths, imports, infrastructure, ops scripts, servers and reference kinds are all untouched by *what
a `Y` covers*. Coherent, orthogonal. Record:
`agent-corpus/falsification/2026-10-14-operator-attention-scaling.md`.

Disposition: see ledger #290.

## Amendment — d-work #438 (2026-10-25, Not ratification: the events-only commit)
**Claim (plan #438, the Operator's `Y` of 2026-10-25):** an events-only commit to `main` — touching
nothing outside `<runbooks>/events/`, holding events of read-only run-book commands only — is
not a ratification event: it records what a read-only command observed, never a decision, as a
ledger-only commit records a prompt received or a disposition already given. *Not ratification*
gains one bullet; the Ratification events list is unchanged.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 16 | Monitoring belongs under a standing row with a batch mandate ("one workstation PR per batch of events", ceiling n), so this Rule needs no edit. | **Refuted** (plan #438 alternative a). A row that never completes breaks Rule-3's lifecycle; its plan-`Y` authorizes no mutation, only an observation; the ceiling forces a fresh row and a fresh plan-`Y` every n batches — an Operator question that decides nothing — and each batch is still a PR and a full suite. | Nothing is authorized, so there is nothing for a `Y` to bind to: the record is clerical or it is no record. |
| 17 | An event is a workstation-zone record, not the ledger; the clerical class was defined by the path `agent-corpus/d-work/`, not by a test. | **Survives, scoped** (alternative b). The bullet's own reason is the test — "records …, never a decision" — and the path is how a mechanism decides it. An event of a read-only command passes that test; the path `<runbooks>/events/` is how the fence decides it, and `sysadmin/events` already keeps that store append-only on `main`. | Clerical by the same test, decided by its own path, fenced by its own guard. Events of read-only commands only. |
| 18 | Alone, the exemption commits every heartbeat: a commit and a push per reply, mostly identical lines. | **Confirmed**, and answered outside this Rule (alternative c): the sysadmin craft's property 7 records a read-only command's event only on a change of reading (craft amendment #438). | This Rule admits the commit; how many commits there are is the craft's. |
| 19 | No record at all: the board reading is the record, computed on demand (alternative f). | **Survives, scoped** — right for a reading nobody grades. The harness side of a reading is The World and kept nowhere, so a past reading cannot be recomputed, and audit grades recurrence from the events (#409 G1). | The committed record is the history of changes; the current reading stays on the board. |
| 20 | Precedent (the Rule-10 counter): widening the clerical class invites the next class to cite this one. | **Survives, bounded.** The bound is the test this Rule already states — a clerical commit records, never decides — and the class named is events of read-only commands only (Rule-8 class); a commit that chooses, or an event of a reversible or destructive command, fails it. | The bullet carries both bounds in its own words, so the next class is judged against them rather than against this precedent. |

**Rule-5 pairwise (#438, Not ratification edited).** **2–3**: Rule-3 owns the events-only class, the
statement that monitoring is no d-work and the guards that admit it; Rule-2 owns only that the commit
is not ratification — one-way, as for the ledger-only bullet. **2–12**: Rule-12 property 2 skips the
suite for the same range; this Rule is not read there. **2–1**: unchanged — one zone per commit, so a
commit touching the ledger and the events is neither class. **2–8**: unchanged — the read-only class
is Rule-8's and the sysadmin craft's; a reversible or destructive action keeps its row and its
counter-prompt. **2–19**: unchanged — a deploy's health pass is still completion evidence read from
the run that observed it. **2–4**, **2–5**, **2–6**, **2–7**, **2–9**, **2–10**, **2–11**, **2–13**,
**2–14**, **2–15**, **2–16**, **2–18**, **2–20**: unchanged. No new Agent term: "events-only" is an
adjective, as "ledger-only" is. Coherent, orthogonal.

Disposition: see ledger #438.

## Amendment — d-work #476 (2026-10-26, child C3 of #473: the evidence block cited by its sha256 and its brief form)
**Claim (plan #473, the Operator's `Y` of 2026-10-26, asking to reduce time and tokens in verification, evidence
collection above all):** the completion reply cites the evidence block by its `evidence-sha256` and its brief form,
as `check --evidence --brief` prints it — one count line, the baseline compared against, the warnings already
standing on that baseline folded per guard, every failing, skipped or other line, and every warning of a kind new
since the baseline (the Operator's `Y` escalating #476, 2026-10-26); the full block, over which the sha256 is computed unchanged, is
stored per checkout and never tracked (`<git common dir>/dyad-evidence/<sha256>.txt`) and shown byte for byte on
request (`check --evidence --show <sha256>`); the Operator may re-run the evidence on the same head and compare.

| # | attack | result |
|---|---|---|
| 21 | A brief block weakens the merge evidence: the Operator no longer reads every line. | Survives, scoped: the sha256 still covers every line, every failing or skipped line and every warning new since `main` are still in the reply, and the full block is one command away; what the Operator verifies — the same head yields the same sha256 — is unchanged. Only what is pasted shrinks. |
| 22 | A stored block can be edited after the fact to match a claimed sha256. | Refuted: the sha256 is recomputed by re-running on the head, never read back from the store; the store is a convenience for reading, not evidence of its own. |
| 23 | The store is per checkout, so another clone cannot show it. | Survives, accepted: the re-run on the same head is the cross-clone check, as before; showing is for the clone that ran it. |
| 24 | Folding standing warnings into counts hides a warning that changed, or a check that silently stopped running. | Refuted, scoped: a warning of a kind not already on `main` is printed in full; a check that stopped running changes the count line; with no baseline found nothing is folded, and a line says so; and the sha256 covers the full block, so any changed line changes it. |

**Pairwise (Rule-5).** **2–14**: Rule-14 property 3 owns the block, its store and its show command; Binding cites them. **2–3**: Rule-3's relayed-Done bullet cites the block as Binding does. **2–6**: the vocabulary row `evidence block` changes (owner 14, used by 2 and 14); both still read correctly. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #476.

## Amendment — d-work #543 (2026-10-31: Enforcement names its three mechanical checks)
**Claim (plan #543, the Operator's `Y` of 2026-10-31 on "fix rule-2"):** Enforcement said "Inference-only, with one
mechanical fence" (`rows.py`), while `dyad/guards/agent/merges.py` (d-work #541) declares `OWNER = "Rule-2"` and checks
that a merge into `main` executes a recorded Done-`Y`, and `dyad merge` (d-work #532) refuses a merge the operative
disposition does not name at the PR's live head. Enforcement now names all three and keeps inference for the binding
itself.

| # | attack | result |
|---|---|---|
| 25 | Only the wording is stale; leave it. | **Refuted** (plan attack 1): Rule-4 and Rule-5 read Enforcement to place a guard's owner; a guard naming an owner whose text denied having any guard of its own is an incoherence Rule-5 counts. |
| 26 | `merges.py` belongs to Rule-3, as the three-act Done and `rows.py` do. | **Survives as the guard states it** (plan attack 2): its check is that a merge executes a recorded Done-`Y` — a ratification event, this Rule's. Rule-3 owns *when* that `Y` is recorded and when the row closes (`rows.done_order_problems`, `rows.landing_problems`); `merges.py` reads the record Rule-3 writes and judges the merge, which Rule-2 Binding governs. Split stated in the pairwise below. |
| 27 | `dyad merge` is a verb, not a guard; naming it in Enforcement over-claims. | **Scoped** (plan attack 3): the text calls it execution, not a guard — Binding's heads-unchanged condition applied when the merge runs — and claims no check of any other path. A merge made outside the verb is still judged by `merges.py`. |
| 28 | With mechanical checks named, "Inference-only" is false, and so is the claim that the binding is inference. | **Survives, reworded** (plan attack 4): the section no longer opens "Inference-only"; what stays inference is whether a `Y` was given to the question it is recorded against, because the identity of the disposer cannot be read from git. |
| 29 | `merges.py` only warns, so naming it as Enforcement overstates it. | **Refuted, stated in the text**: the bullet says "warns — never fails", detection being the posture the Operator chose (#532 revision 3). |
| 30 | The main fence's description omits events-only commits (#438), so the new bullet is inaccurate if copied from the old one. | **Confirmed and fixed**: the bullet reads "not ledger-only or events-only", as Rule-3's Ledger and the fence admit both. |

Vocabulary (Rule-6): no new term. `guard` (owner 11) and `ratification event` (owner 2) already list Rule 2 in `used by`.

**Pairwise (Rule-5).** **2–3**: Rule-3 owns `rows.py` (the main fence), the three-act Done and when a `Y done` is
recorded; Rule-2 owns `merges.py`, which reads that record to judge a merge commit — reading, not sharing, the concern;
Rule-3's Mechanisms already says "Rule-2 references `rows.py` by name; it does not own it", unchanged. **2–14**: the
merge guard runs on the kernel-only path as a transaction guard (property 3), and `dyad merge` is the local merge path
property 3 sanctions; Rule-14 owns the path, Rule-2 what runs on it. **2–11**: the guard is placed under
`dyad/guards/agent/` per property 1 and discovered by the runner; unchanged. **2–12**: `merges.py` carries its tests and
invariants per property 1; unchanged. **2–20**: `merges.py` resolves a merge's second parent against a `Y done` entry as
its own check, not as a registered reference kind; Rule-20 owns stored references and is not touched. **2–1**: one zone
per commit and PR, unchanged; a merge commit's zone is judged by containment. **2–4**: the block is unchanged; Rule-4's
guard passes. **2–5**: this record is the sweep's statement. **2–6**: no term added. **2–7**: provenance unchanged.
**2–8**: no host action. **2–9**: falsified here. **2–10**: unchanged. **2–13**, **2–15**, **2–16**, **2–18**, **2–19**:
unchanged. Coherent, orthogonal.

Disposition: see ledger #543.

## Amendment — d-work #545 (2026-11-01: a release leaves the never-accretable list under the release gate)
**Claim (plan #545 revision 2, the Operator's `Y` of 2026-11-01):** a release stays never-accretable except under the
release gate, where the release d-work's own Done-`Y` names the cut PR and the tags and, with its fence, ratifies the
release (Rule-11), the hosting approval authenticating it.

| # | attack | result |
|---|---|---|
| 31 | The never-accretable list exists because a plan cannot see what it will publish. | **Survives, and the exception keeps it**: the release is not accreted by a plan; it is ratified by a Done-`Y` given on the bytes, named tag by tag in the question (Rule-11 G6). A plan-`Y` alone still never releases. |
| 32 | The exception widens what an agent can publish. | **Refuted**: nothing publishes without the Operator's approval on the hosting, which no agent can forge (#541 A1); the gate removes a question, not a check. With the gate off, the list is unchanged. |
| 33 | Binding's first sentence: a `Y` binds only to what its question named. | **Survives**: the Done question names the tags; a tag outside it is not bound. |

**Pairwise (Rule-5).** **2–11**: Rule-11 owns when a release is ratified and its fence; Rule-2 owns that the Done-`Y`
may bind to it; each cites the other. **2–3**: the Done question's `releases` clause is stated in Rule-11, while Rule-3 owns the forms; that gap is named in Rule-11's amendment #545 and carried as a follow-up. **2–7**: the
approval's record is Rule-7's. **2–6**: `release gate` used by 2. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #545.

## Amendment — d-work #556 (2026-11-02: Enforcement names the automaton as execution)
**Claim (plan #556, the operator's `Y` of 2026-11-02):** the d-work automaton is a fourth mechanism beside the fence,
the merge guard and the merge verb: execution, never disposition.

| # | attack | result |
|---|---|---|
| 34 | An automaton with `contents: write` can merge anything. | **Survives, bounded**: it merges only through `dyad merge`, whose refusals bind it to an operative `Y done` on `main` naming that PR at that head; a forged entry stays detection (the merge guard, the fence), as for any writer. It runs `main`'s reviewed code, never a unit's working tree. |
| 35 | The automaton is a third party, contradicting "never the same party" and the two-party dyad. | **Refuted**: it disposes nothing, so it is neither proposer nor disposer; the vocabulary's `party` row states it as the countersign model's executor. |
| 36 | The switch is a preference by another name. | **Survives, scoped**: `DYAD_AUTOMATON` is a repository variable the operator sets, as `RELEASE_APPROVAL` is; it authorizes nothing (each merge still needs its recorded `Y`), so it is a form setting, not a mandate. |

**Pairwise (Rule-5).** **2–3**: Rule-3 owns when the automaton may merge and close; Rule-2 owns that it is execution
and how it is bounded. **2–14**: the gate it pushes through is Rule-14 property 3's. **2–6**: `automaton` used by 2.
Others unchanged. Coherent, orthogonal.

Disposition: see ledger #556.

## Amendment — d-work #564 (2026-11-03: corroboration where the merge ran; the scheduled sweep)
This Rule's sentence changes with property 3 of Rule-14; the claim, its attacks and the pairwise statements for every
Rule this d-work touches are recorded once, in `rule-14-system-infrastructure.md`, amendment #564.

Disposition: see ledger #564.


## Amendment — d-work #574 (2026-11-04: Binding's mandate clause gains the play-book that prescribes a class of row)
This Rule's sentence changes with Rule-3's; the claims, their attacks and the pairwise statements for every Rule this
d-work touches are recorded once, in `rule-3-d-work.md`, amendment #574.

Disposition: see ledger #574.


## Amendment — d-work #585 (2026-11-04: pointer to the Rule-3 refactor)
This Rule's sentence changes with Rule-3's refactor. The claims, attacks and pairwise statements are recorded once, in
`rule-3-d-work.md`, amendment #585.

Disposition: see ledger #585.

## Amendment — d-work #649 (2026-11-09: the precedent's scope, by what a wrong match costs)
Claim (plan #649): a precedent may settle an outcome only when a wrong match of that outcome costs the operator at most
a question. Each outcome declares the effect it has, and the new mechanical record `dyad/dmc/precedent-scope.jsonld`
decides from that declaration. The record is homed in this Rule as an index record, with `alsoIn` Rule-3 and
`scripts/similar.py`.

The effects:
- **settles**: an agent-side call. It asks no question, skips none and ratifies nothing.
- **asks**: a question put to the operator, such as a new plan, a plan revision, a row of its own, or a preferences PR.
- **shapes**: what a question the operator answers anyway shows, such as the class that sets the number in a release
  question.
- **skips**: a question another outcome would ask is not asked.
- **acts**: a ratification, a destructive act, a release or a preference change with no question of its own.

A precedent settles only `settles`, `asks` and `shapes`. Precedence is `acts`, then `skips`, then the rest. In a
record that declares an effect on any outcome, an undeclared outcome reads `skips`. A record that declares none keeps
the record-wide consequence test (#642 Q7) until it does, so a record moves to the effect test whole, when its
effects are declared, and is never half-read.

This replaces the record-wide word test of #642 Q7 (`dmc.py` `RATIFYING`) as admission's refusal. The word test stays
as a warning. Binding gains one bullet, Rule-3's precedent paragraph cites the record, and the vocabulary row
`precedent` gains it.

Effects declared in the core, reviewed outcome by outcome:

| record | settles | asks | shapes | skips |
|---|---|---|---|---|
| blocker-home | own-diff | never, own-row, revision | | port, ride, carried |
| plan-departure | | new-plan | | as-planned, mandate, execution-detail |
| release-class | | | critical-fix, capability, enhancement, breaking | maintenance |
| promotion | P1–P6 | | | none, hold |
| attack-result | confirmed, refuted, survives, no-attack-found | | | |

The craft records' effects come in a later PR in the craft zone: cabinet's unit-lifecycle and sysadmin's
changelog-actor. Over #644's decision log this admits 18 of the 20 cases refused before:
- blocker-home: 4;
- plan-departure: the 2 new-plan cases (the 2 execution-detail cases stay refused);
- release-class: 6;
- unit-lifecycle: 6, after the craft PR.

| id | claim | attack | result | survivor |
|---|---|---|---|---|
| S1 | `asks` is safe | a wrong `new plan` precedent asks the operator a needless question | survives | its cost is one question, which the operator still decides |
| S2 | `shapes` is safe | a wrong release class understates a release | survives, scoped | the number is in the release question the operator answers, and the release play-book classes each d-work again |
| S3 | the declared effect is right | an author declares `asks` for an outcome that skips | survives, scoped | the guard's `RATIFYING` warning catches the words, and the effect is reviewed in the PR's evidence outcome by outcome |
| S4 | the broadened set is safe | it changes decisions | survives | nothing converts until a record's agreement meets its bar, measured after the change |
| S5 | the zones are ordered | effects declared in a craft before the code that reads them | survives | the agent-zone PR lands first (`order: required`) |
| S6 | `maintenance` and promotion's `none` and `hold` are `skips` | they decide nothing the operator is asked | survives, scoped | each means a question another outcome would ask (a release, a proposal) is not asked, so a wrong match would remove it; `skips` is the conservative reading, and no admitted case holds one |
| S7 | the `skips` default refuses what is admitted today | the craft records unit-lifecycle and changelog-actor declare no effect until the craft-zone PR, so a bare `skips` default would refuse changelog-actor's 4 cases, admitted today | survives, scoped | the default applies only in a record that declares an effect; a record declaring none keeps the record-wide test (`similar.declares_effects`), so today's 9 stay admitted until the craft PR declares those records' effects |

**Rule-6.** No term is added. `precedent` gains the record in its definition and Rule-2 in its `used by`, since
Binding now uses it.

**Pairwise (Rule-5).**
- **2–3**: a precedent-`Y` still binds exactly the listed entries (Rule-3 What a `Y` binds). Which entries admission
  passes is this record's, so Rule-3's paragraph cites it and restates none of it.
- **2–16**: the decision log's shape and append-only rule are unchanged. Only admission's reading of a case's outcome
  moves.
- **2–8 and 2–11**: a destructive act and a release stay their own questions, which no precedent settles (`acts`).

The other pairs are as amendment #585 left them. Coherent, orthogonal.

Disposition: see ledger #649.

## Amendment — d-work #703 (2026-11-14: the attention-ledger write asks no disposition)

**Claim (the operator, provenance #703 entry 3):** "each attention logging doesn't require operator disposition because
the registration action is the disposition that is carried forward ... falsify."

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| B1 | An attention-ledger write is a ratification event. | **Refuted** | It records references to what the records already hold and decides nothing: the Not-ratification test, as a ledger-only commit records and never decides. |
| B2 | The registration is a disposition carried forward. | **Refuted** | A standing authorization is a plan-`Y` with a mandate scope, or an authority preference (Binding). A registration is neither: it is a unit's setup act, which #700's plan named as setup. No disposition is needed because a write decides nothing, not because one was carried. |
| B3 | Registration implies compliance. | **Survives as an obligation, not an authority** | A registered checkout owes the log, which the home's warning (`session touch`, `board resume`) and the registered count make checkable. |
| B4 | No write ever needs a disposition. | **Survives, scoped** | True while each kind holds references only. A kind that adds content enters only by a plan-`Y`'d change, as every kind does, and the bullet says so. |

**Verdict:** the conclusion survives, on B1's ground; entry 3's reasoning, B2, is refuted.
- **Rules:** Not ratification gains the attention-ledger write; Provenance gains its line.

**Pairwise (Rule-5).**
- **2–3**: a write is no ratification event, so Rule-3's questions and Batch disposition are unchanged; the closing line still reads this system's own questions from its board.
- **2–7**: a write holds no operator words, so no provenance entry is owed; a declared pairing's `--ref` points at an existing entry and copies none of it.
- **2–16**: `paired-units` stays Presence's declaration and the records' check; the ledger reflects it and routes nothing, and the board stays the source of every entry.

The other pairs are as amendment #649 left them. Coherent, orthogonal.

Disposition: see ledger #703.
