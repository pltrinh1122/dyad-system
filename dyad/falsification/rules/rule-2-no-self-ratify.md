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

