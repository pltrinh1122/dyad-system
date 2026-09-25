# Falsification record — "one interaction model spans explicit, implicit and automatic, in every Countersign system" (d-work #152)

**Claim (Operator's, provenance #152 entry 4):** a single interaction model across explicit, implicit and
automatic can be adopted consistently by dyad-system, dsys-repo and countersign-system, refactoring as
necessary. The candidate is plan #152 revision 2 §1 (`agent-corpus/d-work/plans/152.md`), now
`../rules/interaction.md`. R1–R7 are the plan's attacks, restated; R8–R12 were found while drafting the rule, the
command adapters and the projector's I6 check.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| R1 | One model cannot span a human-prompted agent, a mandated agent and an inference-free executor. | **Refuted** | Five primitives cover all three lifecycles (`../rules/interaction.md` §4). The only mode-specific parts are *which* basis the countersignature has and *who* processes — both attributes of the act (#153), not parts of the model. |
| R2 | dsys's five disposition kinds break I2's three answers. | **Refuted** | They are bases and occasions (#156 F4), not answers: `set_standing` is basis `mandate`, the rest `per-act`. The answers stay yes / no / counter, which map one-to-one onto yes / no / amend (§2). |
| R3 | "Text with a disposal opens a new d-work" (dyad-system Rule-3) conflicts with `amend`. | **Survives as a gap, scheduled** | Today amend happens de facto — #145, #148 and #149 were `N` with text, re-entered as linked rows. The projector never derives `amend` (schema D3); the Rule-3 wording change is §7's first row, not adopted here. |
| R4 | Committing slash commands breaks Rule-1. | **Confirmed** | `.claude/` belongs to no zone in dyad-system's `containment.py`, so a committed `.claude/commands/*.md` is an unclassified path. This craft ships the adapters as *templates* under its own `templates/commands/` (craft zone, an allowed child per syseng `naming_rules.txt`); installing them into `.claude/commands/` waits for #152 PR-1 (`("infra", ".claude/*")`). |
| R5 | A report that never asks weakens oversight. | **Refuted** | Oversight sits in the countersignature that covered the act. A report that surfaces something unsigned raises an escalation, which does ask (§1). |
| R6 | Copying dsys slash-command texts is fine; they are docs. | **Refuted** | dsys-repo has no licence: all rights reserved. The four templates here are authored fresh; dsys is cited by name only (§6, Sources). |
| R7 | Presence overlap. | **Checked at execution by the main agent** | The drafting subagent writes only under `crafts/countersign/` in its own worktree; the presence read before the push is the main agent's (Rule-16), not this record's. |
| R8 | **I6 cannot be checked on dyad-system's data.** Every row predates a store that records an initiation. | **Refuted as "cannot", survives as "only as a warning"** | D8 (`interaction.md` §3) finds an initiation for most acts from three stores already kept: a provenance `prompt` entry, an intake origin in refs, an opening disposition. On this instance at the base commit: 122 of 144 acts initiated, 22 not. dyad-system's `provenance.SINCE_ID` (164) lies above every row id here (1–156), so an id cut-off cannot separate legitimate gaps from real ones; the check therefore warns and never fails, as Rule-7's own missing-record check does. |
| R9 | **The I6 warnings are noise** — pre-Rule-7 rows only. | **Refuted** | Read case by case, several are what I6 forbids: backlog rows with an empty `disposed` (e.g. #38, #129 — the latter titled `--backlog`, a CLI argument taken as a title) are rows opened on the agent's own finding, not on a prompt or a disposition; #16's only records are its plan and done answers, the plan having been proposed inside #13's reply after an incident. The warning makes them visible; judging them is the Operator's. |
| R10 | **An I6 check forces a core-schema change** (Initiation is a primitive, so it must be an entity). | **Refuted, for now** | The derivation lives in each act's `profile.initiation` (F5: the profile is the system's own), so `countersign-core.json` keeps its eight entities; only `schema_version` moves with `VERSION` (0.2.0), as `schema.md` When requires. A stored Initiation entity is a later schema change, driven by what D8 could only derive (the #156 reconciliation's order). dsys's pinned copy of 0.1.0 stays valid for 0.1.0; re-pinning is dsys's own change. |
| R11 | **`interaction.md` binds the agent's process, so it belongs in the core craft** (Rule-4 Boundaries guard). | **Survives, scoped** | Its imperatives are the process; but in dyad-system nothing obeys this file — only the Agent Rules bind, and §7 lists what they still lack. The file is the model a projection is checked against and countersign-system's target. The craft guard's agent-token scan reports no token after drafting; the rule's first paragraph states the scoping. Adopting an imperative in dyad-system remains a core Rule change by its own d-work. |
| R12 | **A command adapter drifts into being the procedure** (the #115 failure: the command's own steps replace the play-book's). | **Survives as a risk, mitigated** | Each template tells the agent to *read* the play-book or Rule file now and says the file wins where they differ; its numbered lines only frame the invocation (sentinel, d-work, plan answer, one question). Nothing checks this mechanically: whether a template has grown procedure is inference, at the review of each change to `templates/commands/`. |

**Verdict:** the claim **survives, scoped**: one model — five primitives, eight imperatives, three lifecycles —
spans the three modes (R1, R2, R5), is checkable on dyad-system's data for I1, I7 and (as a warning) I6 (R8, R10),
and is *adopted* by no system yet: dyad-system's Rules differ on I2's amend (R3), I6's recording and I7's stored
fields (§7), dsys's commands need the `/falsify` refactor, and committing adapters waits for a zone (R4).

**Survivor:** `../rules/interaction.md` as the model; `../templates/commands/` as adapters, installed only once
`.claude/` has a zone; the projector's `interaction` as the I6 check (warnings), beside `check`'s I1 and I7;
§7's refactors as each system's own later d-works.

**Limits.** The dsys column (answers, disposition kinds, commands) is read from plan #152 and #156's reading of
dsys-repo, not re-verified here. The I6 counts are this instance's at the drafting base (`ec20f7a`). Whether a
flagged act was really self-initiated is inference.

Disposition: disposed by the Done-Y of dyad-system d-work #152 (see ledger #152).
