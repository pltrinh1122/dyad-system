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
