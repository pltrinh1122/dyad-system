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

## Amendment — d-work #137 (2026-09-23, the incident-hardening play-book)
**Claim (Operator, 2026-09-23):** the incident-to-mitigation exercise run by hand in #116, #128
and #135 is a repeatable procedure of the core craft — group the incident log into observed
failure modes, plan a mitigation per mode, execute it, verify it — run periodically so that
reliability keeps up with the system's own mutation; named `incident-hardening`, taking an
incident ledger as its parameter, and doing no work when that ledger has not grown.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A play-book is the wrong container: Rule-13 says recurrence proposes *code*, so this procedure should be a script. | **Refuted, scoped** | Rule-13 property 1 yields a code path for a recurring *task*; this is a recurring *decision* — which incident belongs to which mode, and which mitigation is worth building — and the vocabulary's `play-book` is exactly "an executable procedure … for a recurring decision". The steps that *are* mechanical do become commands: that is the run-book half. |
| 2 | Rule-5 already owns periodic review, so this duplicates a sweep (Rule-5 Conditions: "The operator prompts a sweep of the set"). | **Refuted** | A sweep's target is the Agent Rule set, checked pairwise for coherence and orthogonality; this one's target is the incident log, grouped by mechanism and closed by fences. Different target, different verdict, no shared ownership (Rule-5's own orthogonality test). The name `incident-sweep` is excluded for the term's sake, not the Rule's. |
| 3 | The exercise produced nine records and zero fences last time (#128): formalizing it institutionalizes an audit nobody builds. | **Confirmed — and the reason phase 4 is written as it is** | The strongest attack, and it is why a mode may close only by one of three named exits, and why phase 2's inventory must be read from code rather than prose — the failure in #116/#128 was that a surfaced candidate had no row and no moment. The play-book cannot make the Operator dispose; it can make an undisposed candidate visible as a row instead of a paragraph. |
| 4 | The run-book half is unrunnable in this instance: `runbook.py`'s `DEFAULT_RUNBOOKS` is `workstation-corpus/runbooks`, and `workstation-corpus/` does not exist here. | **Survives, scoped** | It runs: `runbook.py`'s `run` makes the events directory itself — `ep.parent.mkdir(parents=True, exist_ok=True)` beside the `events_path(root, instance)` call — so the first run creates it. The consequence is real and is stated in the play-book rather than solved here — the events file is instance state in the *workstation* zone, so it lands in its own PR (Rule-1), and this instance's want of a host is backlog #60. `DYAD_RUNBOOKS` can redirect it. |
| 5 | Phase 1's "one observed failure mode per row" was already falsified as lossy: two rows carry two mechanisms. | **Survives, scoped** | Carried over from #116 with its answer: primary is the mechanism that *started* it, the second is named secondary in that mode's record. #116's own attack, kept rather than re-litigated. |
| 6 | The taxonomy is not closed: #128 attack 7 found a tenth pattern the nine modes do not name. | **Confirmed** | Which is why phase 1 re-derives the modes from the log each exercise instead of reading the previous index's list — stated in the play-book as a step, not an assumption. |
| 7 | Rule-3 is already the longest Rule; another clause worsens it (Rule-4 shape, Rule-5 coherence). | **Survives, scoped** | One sentence, in the clause that already owns incidents, delegating the procedure to a file — which is what a play-book is for. The alternative, a new Rule, would need its own block and a coherence statement against all nineteen. |
| 8 | The watermark belongs in the events file the runner already appends, not in a prose audit — an audit can be hand-edited and drift from the ledger. | **Refuted, scoped** | The events store is `<runbooks>/events/`, workstation-zone instance state this system does not have (backlog #60, and attack 4 above); an idempotence gate that needs a zone the instance lacks is unusable on the first invocation. The audit is agent zone, always present, and is the artifact a reader consults anyway. The drift risk is real and is answered by deriving the live count at survey time rather than trusting the watermark alone: the watermark is only ever compared, never believed. |
| 9 | A row count is a weak watermark: rows are inserted mid-file by concurrent sessions (the #114 rows sit at lines 9–13), so a count can stay equal while content changes. | **Survives, scoped** | True, and the reason the watermark carries the latest row's date beside the count. Two rows added and one removed would still defeat it, but `INCIDENTS.md` is append-mostly and a removed row would be its own incident. The cheap, kernel-only check is a count plus a date; a content hash would be stronger and is named here as the upgrade if the pair is ever seen to fail. |
| 10 | Parameterizing by ledger path lets the play-book write records into another system's instance, which Rule-1 does not govern across repositories. | **Survives, scoped** | The parameter names a path inside the running system's own tree; hardening a peer's log means having that log in this tree, which is an intake (Rule-3), not a cross-repository write. Stated in the play-book as a boundary rather than enforced, since no guard reaches another repository. |
| 11 | Idempotence means the play-book can never notice a mitigation that regressed, because an unchanged ledger stops the exercise before phase 4. | **Confirmed — and it changes phase 4** | A shipped fence can rot without any new incident being logged, and the no-op gate would hide exactly that. Phase 4's verification of *already-closed* modes is therefore not gated by the watermark: the survey's no-op stops phases 1 to 3, and phase 4 re-tests each closed mode's fence against the incidents it claimed whenever the exercise is invoked. So an invocation on an unchanged ledger is not "do nothing" but "re-verify the fences and report"; it writes no file when every fence still holds, which is what `0 changes` means here. |

Pairwise (Rule-5), for the one sentence Incidents gains. The four neighbours it could have
collided with, and why each is untouched: **3–5** — Rule-5's `sweep` is the pairwise coherence and
orthogonality check of the Agent Rule set, recorded in `agent-corpus/audits/`; the exercise this
sentence names reads an incident ledger and closes failure modes by fences. Different target,
different verdict, and the one name that would have blurred them (`incident-sweep`) was excluded
in the plan's own naming table (attack 2), so Rule-5 keeps sole ownership of the periodic review
*of Rules*. **3–9** — Rule-9 owns falsification: each mitigation candidate the exercise surfaces
is a claim, attacked and recorded as any other, and phase 2's "falsify the claim *this mode is
addressed*" is Rule-9's form used, not a second one declared. Rule-3 states when the exercise
happens and what closes a mode; it says nothing about how a claim is attacked. **3–19** — Rule-19
owns a *server instance's* run-book and health command; the steps here are a core run-book
(`dyad/runbooks/`, its own section set, Rule-19 Boundaries), run through the same core runner,
which is the arrangement the craft play-book already uses. No server is deployed, so Rule-19's
property 2 is never reached and its concern does not move. **3–13** — Rule-13 property 1
(recurrence proposes code) is satisfied, not displaced: the mechanical steps become the run-book's
commands, and what stays in the play-book is a decision, which `play-book` is defined as covering
(attack 1). Rule-13 keeps ownership of when inference must yield code; nothing here exempts
anything from it.

The rest: **3–1** the exercise's own output lands zone by zone, one PR each, as the play-book says
and Rule-1 already requires (attack 4's events file is the workstation case). **3–2** an exercise
opens no ratification event: each mode's mitigation is an ordinary d-work with its own plan-`Y`
and Done-`Y`, and the no-op writes nothing to dispose. **3–4** the Rule-4 block is unchanged — one
bullet inside an existing clause, no new Intent, Target, Boundary or Condition, so the counts the
guard checks are as before. **3–6** one term, `failure mode` (owner 3, used by 3); the compound
*incident ledger* names the play-book's parameter and is never the `ledger` the vocabulary defines
(the row-file store, owner 3), a distinction the new bullet holds by never writing `ledger`
unqualified. **3–11** the play-book and its run-book are core-craft files under `dyad/`, their
events instance — the split Rule-11 property 1 already draws. **3–15** the exercise runs *inside*
the d-work the prompt opened, its phases planned in that d-work's own plan file first, and each
mode's child d-work stores its own plan before its plan-`Y` — Rule-15 phase 1 as it already reads,
no phase added. **3–16** the modes' child d-works are ordinary rows in the row-file store, each
its own file. **3–20** the bullet's one package path (`dyad/playbooks/incident-hardening.md`) is a
`rule.text->path` reference the register already resolves; no kind is added. Others unchanged.
Coherent, orthogonal.

Disposition: see ledger #137.
