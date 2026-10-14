# Falsification record — batch-disposition-mode (d-work #17)

**Claim (Operator, 2026-09-15):** the Operator wants to dispose a set of plan counter-prompts
with one `Y`, and a set of completion counter-prompts with one `Y`; an ignored counter-prompt
(the Operator's next message is a prompt, not its bare disposal) is itself the signal to engage.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A batch `Y` is self-ratification by aggregation — bundling lets a weak item ride on strong ones (Rule-2). | Refuted | The disposer is still the Operator, and every named item carries its own evidence in the same reply; nothing removes the Operator's ability to answer `N` and ask for the set to be split. |
| 2 | "Ignored" is ambiguous with forgotten or distracted, silently degrading Rule-3's completion verification. | Survives, scoped | The Agent restates the pending queue's counts at the end of every reply while either is non-empty, so an unintended engagement surfaces within one turn; the Operator can always dispose the standing batch question directly. |
| 3 | A batch that mixes a plan-`Y` and a Done-`Y` in one question hides which mutation a `Y` actually authorizes. | Confirmed, as a risk if allowed | The batch forms never mix kinds: a plan batch and a done batch are always separate questions. |
| 4 | Batching the release or a destructive-action counter-prompt could let an irreversible action ride inside a batch of ordinary merges. | Confirmed, as a risk if allowed | Both stay one-per-question unconditionally, batched or not (Rule-3 Boundaries; Rule-8, Rule-11 texts unchanged). |
| 5 | The pending queue needs its own persisted store, like the ledger, or it is lost across a session boundary. | Survives, scoped | It is inference over the ledger and the stored plan files (which rows are plan-ready or done-ready is always re-derivable); nothing is lost, a fresh session re-derives it at the cost of re-asking rather than resuming an unwritten mid-batch state. |
| 6 | `always` mode can stall forever — nothing is ever asked singly, so a distracted Operator never unblocks it. | Survives, scoped | The standing queue is restated at the end of every reply; the trade (latency for fewer interruptions) is the one `merge-disposition: with-done` already makes for merges. |
| 7 | Every d-work's Rule-7 provenance record needs new machinery for a disposition that answers several rows at once. | Refuted | Property 4 already holds: the Operator's one `Y` is the same text; it is written as one entry into each named d-work's own record. Property 5's count still matches per row — no Rule-7 edit needed. |

## Rule-5 pairwise
- 2–3: Rule-2 gains one Binding sentence naming the batch counter-prompt; Rule-3 owns the forms,
  the queue and the preference. One-way each for what it does not own; unchanged concerns
  otherwise (Rule-2 still only ratification, Rule-3 still only the d-work lifecycle).
- 3–7: unaffected (attack 7). 3–8, 3–11: excluded explicitly (Boundaries, attack 4); their forms
  stay one-per-question. 3–15: a batch plan-`Y` still requires each item's stored plan file
  first; unchanged. 3–16: the queue is conversational, not the row/presence store; no overlap.
  3–6: two new vocabulary rows, owner 3, `used by` 2 3 / 3; both terms occur in the Rule text
  they are attributed to.
- Others (1, 4, 5, 9, 10, 12, 13, 14, 18, 19, 20): no path — batching changes who answers how
  many questions at once, not zones, rule shape, falsification, framing, code paths, imports,
  infrastructure, ops scripts or server instances. Coherent, orthogonal.

Disposition: see ledger #17.

## Amendment — d-work #106 (2026-09-21, release's reason split from destructive's)

**Claim (Operator, 2026-09-21):** release isn't destructive — a new release can supersede any
error, and that remediation is accepted — so release isn't subject to attack 4's "batched or not"
exclusion above.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A superseding release is a true undo, like Rule-8's reversible examples (`git config`, a kept-copy edit, stopping a service). | Refuted | Those restore the *prior* observable state; a superseding release doesn't — the erroneous tag stays forever resolvable (Rule-11 property 4: tags "never retagged," "do not move"). Forward patch, not a reversal. |
| 2 | Even without a true undo, if remediation is accepted, release fails Rule-8's own disjunctive test (no undo / loses data / untested undo) on its own terms. | Survives, scoped | Fair reading, but reveals release was never a Rule-8 *class* to begin with — Rule-8's Target is "a host action"; release is Rule-11's own domain. Asking "is release destructive" is a category error either direction. |
| 3 | Since release isn't Rule-8-destructive (or isn't Rule-8's business at all), and attack 4 above was specifically about destructive actions riding along, its exclusion has no surviving basis against release. | Refuted | Rule-11 gives release an independent reason, unconnected to destructiveness: "A release publishes to the world, so it is the Operator's to ratify however few d-works it gathers." Holds regardless of later fixability. |
| 4 | Attack 4 above bundles release with destructive under one shared "batched or not" exclusion, as if one risk. | Confirmed | Split: destructive stays unconditional (Rule-8's own criteria genuinely apply); release gains its own narrower form (Rule-11 Ratification events), scoped to tags of one already-`done` d-work's own already-surfaced output. |
| 5 | Any carve-out invites scope creep — "these releases were all just named" is a judgment call, not a mechanical gate. | Survives, scoped | The gate is conservative by construction: a batchable release must already appear, unmerged, individually named, in the *same reply's own completion evidence* — exactly this record's own attack 2 survivor (the pending queue's visibility discipline), extended to the one case attack 4 arbitrarily excluded it from, not invented fresh. |
| 6 | One live instance (three release tags batched under one `Y`, no visible loss of scrutiny) doesn't prove safety in general. | Survives, scoped | Not offered as proof by itself — the *gate* above (already-named, already-Done, same d-work) is what made it safe, now the formal requirement rather than an ad hoc reading of one bare `Y`. |

Rule-3's Boundaries bullet reworded: destructive-action counter-prompts stay always one-per-
question, never batched (Rule-8, unaffected by this amendment); release counter-prompts stay
one-per-question by default, with a release-specific batch form now owned by Rule-11 (Ratification
events), never Rule-3's own plan or Done batch. Pairwise: 3–11 (attack 4 above) updated to reflect
the split, not excluded wholesale any longer for release; 3–8 unchanged (destructive). No other
Rule's concern moves. Coherent, orthogonal.

Disposition: see ledger #106.

## Amendment — d-work #290 (2026-10-14, the mandate beside the batch: compression is not supersession)

**Claim (Operator, 2026-10-14, refusing revision 4 of plan #290):** "batch is a solution **if**
individual dispositions can be superseded with a 'meta-disposition'." The conditional is the
correction, and this record is where it belongs: the batch form **compresses** questions and the
`countersign:mandate` **supersedes** dispositions, and the second is lawful here only because the
first already established that one Operator `Y` becomes the provenance entry of several rows
(attack 7 above: "the Operator's one `Y` is the same text; it is written as one entry into each
named d-work's own record"). A mandate extends that act from a **named set** to a **stated class**.
Beside it, `batch-disposition-mode` moves `on-ignore` → `always` (PR-1, preferences zone).

**What the batch form has actually bought, measured at `main` 6ca6827.** 110 of the ledger's 509
`disposed` entries are batch entries, written by **36 distinct batch answers** over 280 rows — set
sizes 2 (×12), 3 (×9), 4 (×5), 5 (×2), 6, 7 (×3), 8, 10, 14, 15 — so batching has **compressed about
73 questions and removed none**. The same `Y` count stands behind the same number of
authorizations, which is exactly what this record's attack 1 promised ("nothing removes the
Operator's ability to answer `N` and ask for the set to be split") and exactly what the Operator's
conditional says is not enough.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 8 | A mandate is just a batch over rows that do not yet exist, so this record's attack 1 already covers it and no new form is needed. | **Refuted — the difference is the whole risk.** A batch question *names* its items, and Rule-2's Binding makes the `Y` ratify exactly that named set; a mandate cannot name rows that do not exist. The two are not the same act and must not share a question. | Two forms, never mixed — the same discipline attack 3 above imposed on plan and done batches: a **plan batch** names rows whose plans are stored, a **mandate** names a class and a ceiling in the plan the `Y` answers. A question that did both would hide which authorization the `Y` gave. |
| 9 | Then the mandate belongs in the pending queue, as every other pending item does. | **Refuted.** The queue holds plan-ready and done-ready d-works — items **awaiting a question**. An accreted row awaits nothing: it is already authorized by the mandate's plan-`Y` and its Done rides the mandate's Done-`Y`. Putting it in the queue would re-create the question the design removes and would make the counts meaningless. | The mandate form never enters the pending queue; the accreted rows appear instead in the **completion evidence's accreted list**, which is where the Operator sees what it got. The queue's counts stay what they measure today. |
| 10 | `always` makes every reply carry a queue the Operator must track: one kind of attention traded for another (this record's attack 6, under the preference's own value). | **Survives, scoped, and the log decides it.** `agent-corpus/audits/INCIDENTS.md` row 76 (#183, 2026-09-29) records the `on-ignore` signal being **missed** — "the Operator left a counter-prompt outstanding and sent a prompt instead, and the Agent went on asking singly and reported no pending-queue counts for four consecutive prompts", cause "the signal is conversational … and nothing mechanical raises it". It fired a second time during d-work #290's own planning and was caught only by re-reading the Rule. | `always` deletes the conversational signal rather than fixing it: the queue opens on the first pending item, which is the Operator's own allowed value, reversible by one preferences-zone PR, and the queue is three short numbers. |
| 11 | A mandate inherits a batch `Y`'s weakest property — one `N` discards the whole set — and makes it worse, because the set is unknown when the `Y` is given. | **Confirmed, and priced.** The refusal path is 28 of 509 entries (22 `N plan`, 6 `N done`), 5.5%. A refused *mandate* costs more than a refused batch: the work was done under it. | The escalate edge is the mitigation and is structural, not a promise: anything outside the stated scope returns to explicit mode **before** the work, so what a Done-`N` can discard is bounded by what the Operator already read in the plan. The accreted list is what makes a partial `N` expressible at all. |
| 12 | The release batch (Rule-11, `#106` above) is the nearer precedent, so the mandate should take its shape: several already-named artefacts under one `Y`. | **Refuted.** The release batch's precondition is that each tag is *already named individually, unmerged, in the same reply's own completion evidence* — content a Done-`Y` has already verified. A mandate authorizes work that has not happened. Opposite direction in time, so its fence has to be the stated ceiling, not the prior naming. | Rule-11's release form is untouched and a release stays never-accretable ("a release publishes to the world"). The mandate borrows the *enumeration* half of that discipline for its Done question, and nothing of its authorization half. |
| 13 | Rule-7 needs new machinery after all: a `Y` written into a record whose row the Operator never saw. | **Refuted, as attack 7 was.** The entry is `<date> Y plan (mandate #<id>)` and its matching record entry is the mandate's own words with the note `mandate #<id>, <date>` (Rule-7 property 4, amendment #290); `k == dk` holds per commit (`dyad/guards/agent/provenance.py:265-269`). The note is the one thing a batch entry does not need, because a batch's rows are named in the question. | Property 5's count is unchanged, and the disclosure is in the note rather than in a new field or a new store. |

**Rule-5 pairwise (#290).** **2–3**: unchanged in shape — Rule-2's Binding gains the mandate clause
(its record, amendment #290), Rule-3 owns the forms, the queue, the mandate scope and the accreted
list, and the preference stays Rule-3's to read. **3–7**: attack 13. **3–11**: attack 12 — the
release batch keeps its own narrower form and its own reason. **3–8**: destructive stays
unconditional and unbatched, as `#106` settled. **3–15**: a plan batch still requires each named
item's stored plan file; a mandate requires the mandate's, which is Rule-15's amendment #290.
**3–16**: the queue is still conversational and still not a store; what is stored is the row's
`mode` field and the new `backlog → archived` edge, both Rule-16's. **3–6**: no term is defined
here — `mandate`, `implicit mode`, `basis`, `delegate edge`, `escalate edge` and `amend` are
referenced as `countersign:<term>` by the Agent vocabulary, and `accreted row` and `mandate scope`
are Rule-3's. Others (1, 4, 5, 9, 10, 12, 13, 14, 18, 19, 20): no path, as before — this amendment
changes how many times the Operator is asked and what one `Y` covers, not zones, rule shape,
falsification, framing, code paths, imports, infrastructure, ops scripts or server instances.
Coherent, orthogonal.

Disposition: see ledger #290.
