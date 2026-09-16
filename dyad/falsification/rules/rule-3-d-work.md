# Falsification record — Rule-3 (d-work)

**Claim (operator, 2026-09-12):** a d-work starts with an Operator prompt and terminates only
on Operator `Y` to the Agent's completion counter-prompt; anything else leaves it incomplete
for later resumption.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Resumed later" has no persistence across restart; memory is a cache. | Refuted as stated | Ledger outside the conversation. |
| 2 | A ledger in `agent-corpus` needs a PR + Y per state change (Rule-2) — Y's would need Y's. | Refuted, then re-disposed | First survivor: GitHub issues. Operator disposed N on off-corpus ledger (G7, d-work #21). Second survivor: in-corpus `d-work/LEDGER.md`; ledger-only commits are clerical and bypass PR; CI fences the bypass. |
| 3 | Every prompt a d-work ⇒ counter-prompt on trivial replies; transaction friction. | Survives, unscoped | Agent proposed a `/btw` exemption; Operator disposed N on 2026-09-12 (G6, d-work #20): no exemptions. Friction accepted. |
| 4 | Overlap with Rule-2: "Y to Done" is a ratification event. | Survives with caveat | Rule-3 defines the event; Rule-2's list gains it. One-way dependency. |
| 5 | A new prompt is "not Y" ⇒ it both suspends and opens. | Survives | Stack; agent lists open d-works at session start. |
| 6 | Rule-1 and Rule-2 d-works were never closed with a Done-Y. | Confirmed backlog | Logged as open issues for operator disposal. |

## Rule-5 pairwise (#125, evidence bullet edited): 3–2: Rule-3's bullet names the state ("CI absent") and cites Rule-2 Binding for what counts as green; 3–14: Rule-14 defines when the adapter is absent, Rule-3 only requires it stated. Others unchanged. Coherent, orthogonal. Record: `agent-corpus/falsification/ci-absent.md`.

Disposition: see ledger #12 (done 2026-09-12).

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard paths: `main_fence.py` → `dyad/guards/agent/rows.py`, `dwork_link.py` → `dyad/guards/agent/prs.py`; both are transaction guards on the kernel-only path (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #165 (2026-09-14, craft play-book)
One Plan bullet: a prompt opening a new body of work is planned by the craft play-book (`dyad/playbooks/craft-instantiation.md`); default new craft instance, a firing `craft-instantiation-criteria` (plan #153's D1, D2, D4–D6; D3' import-or-extend) advises a new dyad system at the plan-Y. Attacks (plan #165): a play-book is a Rule by another name — survives scoped: it is *read by* Rule-3 as preferences are, revisable without a Rule edit, no Rule-4 block; "default new craft" hides D1 — refuted: the criteria run before the default, D1 first, the plan-Y decides. Pairwise: 3–2: the advice is a proposal; the plan-Y disposes it (no new event). 3–6: two terms, `play-book` and `craft-instantiation-criteria`, owner 3. 3–9/10: the play-book's plan is falsified and framed as any plan. 3–11: play-book and run-book are package (`dyad/playbooks/`, `dyad/runbooks/`); their events instance. 3–15: the play-book runs before the plan file is written; the file records its outcome. 3–19: the run-book is a core run-book with its own section set (Rule-19 Boundaries); Rule-19 keeps the form's home in the craft rule. Others unchanged. Coherent, orthogonal.

## #168 amendment (2026-09-14): local CI first
| # | attack | result | survivor |
|---|---|---|---|
| A | Without PR-triggered CI a hook-skipping session merges unchecked. | Survives, scoped | The evidence block on the exact head is the gate (Rule-2 Binding, #138); CI was never the gate since #125. |
| B | `main` pushes still spend quota on ledger commits. | Confirmed | Workflows ignore `agent-corpus/d-work/**`. |
Pairwise: Rule-3 gains one clause on *when* hosted CI runs; Rule-14 owns the adapter's place, Rule-2 what a Y relies on, Rule-3 the plan gate's mechanism — no concern moves. Coherent and orthogonal with every other Rule as before.


## Amendment — d-work #185 (2026-09-14, session-start presence)
| # | attack | result | survivor |
|---|---|---|---|
| A | The session-start report grows another mandatory step for no return most sessions. | Survives, scoped | The write is one file, the read is a directory listing of files already usually near-empty; the cost is a few milliseconds, the benefit is exactly the class of near-miss #185 records. |
Pairwise: Rule-16 owns the store and its semantics; Rule-3 states only that the report includes it, same pattern as the ledger report it already carries. Coherent, orthogonal. Disposition: see ledger #185.
