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

## Amendment — d-work #23 (2026-09-16, the plan gate reads commit messages)
The Ledger bullet said "PR bodies cite `d-work #<id>` … the phrase is a claim of work, not a
mention". `prs.py check_transaction` reads, on a branch, "the commit messages of base..head" as the
body. The Rule named one artifact and the guard binds another, so nothing told the Agent that the
claim/mention distinction governs a commit message.
| # | attack | result | survivor |
|---|---|---|---|
| A | A style nit; the Agent should infer it from the guard. | Refuted mechanically | It was not inferred. An incident sentence reading "since d-work #6" in a commit message failed the push with `agent/prs [d-work]: #6 is done, not open` (#22), costing a cycle. Rule-6's own standard applies by analogy: where text and mechanism diverge, the text is the bug. |
| B | Fix the guard instead — scan only a real PR body. | Refuted | The guard has no PR body before the PR exists; reading the range's commit messages is what enforces the plan gate *before* a push, which Rule-3 Mechanisms requires and #168 left as the only pre-merge check. Narrowing it would delete the gate. |
| C | The guard cannot tell a claim from a quotation, so the phrase cannot be discussed in a commit message at all. | **Confirmed; open, scoped** | Found writing this very amendment: a commit message explaining the rule, quoting the offending phrase as an example, failed the gate the same way. `prs.CITE` is one regex over the whole body with no quoting form. The clause is still right — it tells the Agent the distinction governs here — and the residue is that the phrase is unquotable in a commit message; write it broken (`<d-work> #N`) or name it in prose. A quoting form (a fenced block the scan skips, say) is a guard change, a later row, not this d-work's. |
| D | The clause makes the bullet harder to read. | Survives, scoped | It is longer by one em-dash clause and one phrase; the alternative is a rule that is silently false of the artifact the Agent actually writes. |

Pairwise: Rule-3 keeps the plan gate and its mechanism; only the Rule's description of what the
guard reads is corrected to match `prs.py`. Rule-1 owns the commit as a transaction by path — this
is its message text, a different concern. Rule-7 owns the Operator's words, not the Agent's commit
messages. Rule-15's `planned` state at the gate is unaffected. No new term (Rule-6); no mechanism
change, so Rule-12 and Rule-11 are untouched. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #23.

## Amendment — d-work #34 (2026-09-16, Intake: work proposed by another agent)
**Claim (Operator, 2026-09-16):** a d-work carried by another agent's message is admissible as a
defect only as an observation with evidence, and as an enhancement only with the verbatim Operator
prompt (or provenance to one) behind it.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | Scope already says "every Operator prompt opens a d-work" — a message is simply not one, so no clause is needed. | Refuted | Three messages in two days each carried work that ended in this ledger (#4–#15, an untracked defect, #26); without a clause the Agent decided admissibility by inference each time, differently each time. The clause names the two shapes and the return path. |
| 2 | The rule keeps a good idea out while letting a defect in — asymmetric. | Survives, as designed | A defect is falsifiable on its evidence; an enhancement is a want, and only the Operator has wants here (Rule-2: proposer ≠ disposer applies across systems too — an agent may not be the originating disposer of another system's work). |
| 3 | The Operator's own `Y` to a bare agent proposal launders it into an intake. | Survives, scoped | The rule bounds what an *agent* may bring; the Operator may open anything by prompting, which is what happened for #26. Stated in the clause's last sentence, so it is a permitted path, not a loophole. |
| 4 | A relayed prompt breaks Rule-7 p4 / p2 (words not the Operator's; a harness file read). | Refuted | The words are an Operator's, quoted as the message carried them; the entry note names the relay; no harness file is read. Rule-7 p4 gains the sentence; p2 untouched. A defect's observation is the sender's words and therefore stays out of provenance — in the plan file. |
| 5 | "Provenance to a prompt" is unverifiable from here (another system's ledger). | Survives, scoped | It is a `world` reference (Rule-20): the sender's row id and quoted prompt are recorded, inference stated; a sender that misquotes has breached its own Rule-7, which is that system's to catch. |
| 6 | Returning a message "with the missing shape named" is a counter-prompt to a peer, which Rule-3 says subagents and peers never receive. | Refuted | It is not a disposition question; it names a form. Nothing here lets a peer dispose anything. |

Pairwise (Rule-5): 3–7 Rule-7 stores the relayed words (one sentence), Rule-3 decides
admissibility — one-way each. 3–10 the sender's framing is its own system's Rule-10, named in
Boundaries. 3–16 `refs` already carries `<system>-<id>` (#4–#15). 3–2 the `Y` is still the
Operator's; a peer never disposes. 3–20 the sender-ledger id is a `world` kind (attack 5). Others
unchanged. Coherent, orthogonal. Rule-6: `intake` added (owner 3, used by 3 7).

Disposition: see ledger #34.

## Amendment — d-work #37 (2026-09-16, the `archived` state)
**Claim (Operator, 2026-09-16):** the d-work life-cycle needs an archive stage; `done` is terminal
and the finished set only grows.
| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A new state reopens the "done is terminal" promise (Rule-16). | Survives, scoped | `done` still never reaches `open`/`planned`; `archived` is one further step in the same direction and is itself terminal. `dyadlib` invariant renamed `archived-is-terminal` and a second, `done-never-reopens` (`TRANSITIONS["done"] <= {archived}`), keeps the old promise mechanical. |
| 2 | Archive as a view (age, id cutoff) needs no state. | Refuted | Age needs a clock (a projection must be deterministic, syseng determinism.md); an id cutoff is arbitrary; "retired" is a fact about the row, and Rule-16 stores state explicitly. |
| 3 | Archive by moving files out of the store. | Refuted | Row files are never deleted or moved (vocabulary `row file`); every `refs`, plan id and provenance id resolves by path (Rule-20). Nothing moves. |
| 4 | The Agent will archive on its own to tidy the board. | Refuted | Stated: an Operator disposition names the row(s); the transition is clerical execution of it, never the Agent's judgment — the same shape as backlog intake. |
| 5 | Every state-reading guard and test needs a change. | Refuted (checked) | The fence (`rows.py`), `prs.py`, sessions and the kanban invariant read `dyadlib.STATES`/`TRANSITIONS`; one test asserted `done → none` and is updated; the kanban `COLUMNS` tuple gains the column its invariant forces. |
Pairwise (Rule-5): 3–16 the table gains one row, the store sentence one clause; 3–6 one term
(`archived`, owner 3, used by 3 16); 3–20 unchanged (nothing moves). Others unchanged. Coherent,
orthogonal. Disposition: see ledger #37.

## Amendment — d-work #68 (2026-09-18, the reply that asks does not merge)
**Claim:** the Completion clause's "asked … before merge" is enough to keep the merge after the
Done-`Y`. Observed three times false in one session — #47 (PR #35), #58 (PRs #45–#47), #67 (PRs
#50–#52): the Agent ran the throwaway-merge evidence, merged, confirmed `main` green, then asked
the counter-prompt in the with-done form naming PRs already closed. Each was disclosed in the
same reply and ratified retroactively; the second came with a plan file that itself said
"merged … under one Done-`Y`", the third within an hour of a memory note stating the rule. A
sibling fault, same root: #67's plan-`Y` was asked before its plan file existed (Rule-15 phase 1).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The rule was clear and the conduct failed anyway — a sentence cannot fix a motor sequence. | Survives, scoped | True of a *principle* sentence; the new bullet names an *artifact* in the sequence: `dwork state <id> done` precedes the merge, so the ledger's record of the `Y` orders it. The Agent's cache holds the same rule operationally (the merge command only in a block that begins with the `done` transition). If a fourth occurrence follows, this amendment says the sentence was not the fix. |
| 2 | A guard, not a bullet. | Refuted | `gh pr merge` is a World action (Rule-14); nothing in the package runs at that instant. A hosting-side fence (a required check reading the row) is #24's LAN-git territory. |
| 3 | Rule creep: conduct amended into a Rule. | Refuted | No new requirement; the first bullet already says "before merge". The bullet adds the sequence and the ordering artifact, which three readings of the existing sentence failed to produce. |
| 4 | The retroactive `Y`s launder the breaches. | Survives, stated | Each `Y` verified output that was already on `main`; the Operator's verification was real, the sequence was wrong. Recorded as incidents, not erased by the `Y`. |

Pairwise (Rule-5): 3–2 unchanged in substance — Rule-2 owns the event, Rule-3 names when its
clerical execution happens; 3–15 the sibling fault cites Rule-15 phase 1 without editing it. Others
unchanged. Coherent, orthogonal. Disposition: see ledger #68.

## Amendment — d-work #113 (2026-09-22, `concise-mode`: the record precedes the one reply)
Incidents gains one bullet: under `concise-mode: on` the reply where an incident occurred and the
completion reply are one reply, so the incident's record (attack row or `INCIDENTS.md` row, and
the plan file's falsification section) is written during the turn, before the reply reports it.
The attack table is in `rules-9-10-promotion.md`, amendment #113 (attacks 2 and 4 are this
Rule's: an interrupted turn loses narration, never record; delegation moves the two
execute-before-plan-`Y` incident classes out of reach of the actor that drafts, since a subagent
may not commit, push or open a PR — Scope's subagent sentence, unchanged). Pairwise: 3–10 the
key is read by both for different concerns; 3–8 unchanged; 3–15 the plan file is where a
mid-turn finding is written first, as phase 1 already requires. Coherent, orthogonal.
Disposition: see ledger #113.
