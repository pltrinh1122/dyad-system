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
