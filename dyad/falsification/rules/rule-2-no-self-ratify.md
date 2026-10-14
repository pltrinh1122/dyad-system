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
