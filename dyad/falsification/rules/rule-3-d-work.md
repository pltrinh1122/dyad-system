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

## Amendment — d-work #191 (2026-09-29, the plan gate exempts a ledger-only range)
Ledger and Mechanisms gain one sentence each: a range that touches only `<instance>/d-work/` claims no
d-work, so the plan gate (`prs.py`) skips it (`prs.ledger_only`, three-dot, so paths `main` gained after
the branch point never count as the branch's).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The gate is harmless on a ledger-only branch. | Refuted | It refused every uncited ledger commit, and a commit opening or planning a row can cite nothing (no `Y plan` exists yet). A session fenced off `main` (Rule-1, #23) then pushed around the hook — #204, #208–#210, and #207, which could have cited its planned row — and the hook it skipped holds every guard. The gate was causing the bypass it exists to prevent. |
| 2 | The exemption lets unplanned work in. | Refuted | A ledger-only range cannot change code, a Rule or a preference; Rule-2 already classes it clerical, and on `main` the same commit passes the fence with no gate at all. Any other path in the range re-arms the gate. |
| 3 | A plan-`Y` could be forged in a row by a ledger-only range and then cited. | Survives, unchanged | The same row edit pushed directly to `main` was always admitted by the fence; forging a disposition is self-ratification (Rule-2). Rule-7's per-commit check now requires a record entry with every `disposed` entry, so a forgery must also forge the Operator's words — a second act, in a store the Operator reads. |
| 4 | A two-dot range judges a stale branch as touching code. | Confirmed | `ledger_only` diffs the merge base to head. |
| 5 | `git diff --name-only` lists every path a range touched. | Refuted by review | Rename detection lists only a move's destination, so a `git mv` of code into `<instance>/d-work/` read as ledger-only and skipped the gate — a code deletion with no plan. Survivor: `dyadlib.range_paths`, `--no-renames -z`, for the gate and for Rule-12's suite skip (which had the same hole since #155). |
| 6 | "`main` would admit the same commits" holds for a branch merged by PR. | Refuted by review | The fence walks `--first-parent` and skips merges, so a ledger-only branch merged `--no-ff` landed commits it never saw: a row regressed `done` → `planned`, deleted or retitled on the branch passed every guard. Survivor: the fence judges each commit of a ledger-only branch as it would on `main` (`rows.check_ledger_branch`). |
| 7 | The net diff decides whether a branch is ledger-only. | Refuted by review, round 2 | A branch that edited code and reverted it, or whose code was squashed into `main`, has a ledger-only net diff; the gate skipped it while the fence, walking commits, refused its code commit — and a branch citing a planned d-work was stuck. Survivor: ledger-only is decided commit by commit, the same walk the fence makes; such a branch goes through the plan gate. |
| 8 | Merge commits on a ledger-only branch need no fence. | Refuted by review, round 2 | A row kept at `planned` while resolving a merge of a `main` that had it `done` regressed and passed. Survivor: each merge commit's rows are judged against both parents (no drop, no retitle, no illegal transition). |

Pairwise: Rule-7's record, amendment #191, carries the table for this d-work; for Rule-3 the change is one
exemption inside its own mechanism. **3–1**: no zone moves; the containment guard still judges the range.
**3–2**: the exemption's ground is Rule-2's own "not ratification" list. **3–7**: Rule-7's transaction check
is what makes the exempted range safe. **3–16**: the transitions are untouched; the fence now also runs, per commit, on a ledger-only branch,
enforcing the table Rule-16 owns where it was not reached before. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #191.

## Amendment — d-work #213 (2026-10-05, the d-work trace play-book)
**Claim (Operator, via #212 and #213):** the per-d-work performance trace whose format #212 proposes is a
repeatable procedure of the core craft — a play-book, a run-book whose steps run it through the core runner,
and the code those steps call (`dyad dwork trace`) — and Rule-3's completion evidence cites its output for
every d-work. Completion counter-prompt gains one bullet; the vocabulary gains `d-work trace` (owner 3, used
by 3). Plan revision 2 (from #214, before execution finished): the trace store is
`<instance>/d-work/traces/<id>.md`, written at the Done-`Y` before the Done ledger commit that carries it;
the completion reply prints a preview, prompt to Done question; the store's well-formedness is tested.
Plan revision 3 (from #215): the bullet is conditional on the preference `dwork-trace` (`always`, the
default, or `on-demand`), which Rule-3 reads and the play-book's Trigger applies; the preference row lands in
#215's preferences-zone PR, merged before this one.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A core command that depends on Claude Code's transcript layout breaks on another kernel (Rule-14 property 2: "another CLI inferencing agent"). | **Confirmed** | The transcript is an optional input. Without one the trace holds the git and ledger timeline and marks every bucket absent; it never fails (`trace.py`, `test_trace.py` `test_no_transcript_gives_git_and_ledger_only`). The default path is derived, never configured: no new `DYAD_` variable, no host path in the core (`package_rules.txt` refuses the layout's directory name as a string, so the code builds it from parts). |
| 2 | Tracing every d-work adds cost to each completion. | **Survives, measured** | One parse of the 42 MB transcript of this session took 1.2 s wall (`dyad dwork trace 211`); a suite run is about 40 s. Accepted — "for each d-work" is the Operator's own scope (#212). |
| 3 | A trace inside the completion reply cannot hold its own Done-`Y` or merge. | **Confirmed; narrowed by revision 2** | The completion reply holds a preview whose window ends at the Done question. The stored trace is written at the Done-`Y`, after `dwork state <id> done` has written the disposition's entry and before the Done ledger commit, so its window runs through the Done-`Y` and covers the work PR's push and evidence run; only that commit and the merge after it stay out, as git events marked "after the window (clerical tail)". Stated in the bullet, the play-book and every trace's Limits (`test_before_the_done_y_the_trace_is_a_preview`). |
| 4 | Anchoring provenance to the transcript fails on a disposition like a bare `Y`. | **Partly confirmed** | A disposition anchors only to an Operator message that answers a `Y/N:` line naming `#<id>`, in record order after the previous anchor, preferring the entry's own date; a prompt matching more than one message is ambiguous. An entry not anchored is listed under Limits and never guessed (`test_unmatched_and_ambiguous_entries_are_reported_never_guessed`; the fixture's `Y` to another d-work's question is never taken). |
| 5 | A Rule-3 change under a "codify" prompt widens scope. | **Refuted, scoped** | A play-book is "read by a Rule, never a Rule" (vocabulary): without a Rule citing it, it binds nothing, so the citation is the codification. The bullet adds evidence to an existing list; it opens no event, gates nothing, and the Operator may drop it and keep the play-book as reference. |
| 6 | An Operator message is a `user` record with text (found while implementing). | **Refuted** | A prompt sent while a turn runs is recorded as a queued-command attachment, not a `user` record; #211's two prompts are both of that kind. The loader reads both shapes, and a harness notification (a task finishing) starts an agent turn, never an Operator one. |
| 7 | A module named `trace` is imported as `import trace`. | **Refuted** | `trace` is also a standard-library module; the runner and the test load `dyad/scripts/trace.py` by path (`dyadlib.load_module`), so neither depends on `sys.path` order. |
| 8 | A trace file written by the Done ledger commit breaks that commit's ledger-only status (revision 2). | **Refuted, scoped** | The store lies under `<instance>/d-work/`, the one prefix the main fence (`rows.py`) and the plan gate's exemption (`prs.ledger_only`) read as ledger-only, so the commit adds no PR, push or suite run. Scoped: the provenance guard refuses only `*.jsonl` there, and the naming guard selects no `d-work/traces/*` path, so nothing in the guard registry checks the store's shape; `trace.check_store` does (one `<id>.md` per existing row, `# Trace #<id> — <title>`, the five sections), run over the live store by `test_trace.py` `LiveTests` with Rule-12's suite. A `kind:` row in the syseng naming table is a craft-zone follow-up, not this PR (Rule-1). |
| 9 | An unconditional bullet is the only way to make the trace binding (revision 3). | **Refuted** | A preference the Operator owns makes it binding by default (`always`) and lets the Operator turn it to `on-demand` without a Rule edit — the same shape as `merge-disposition` and `concise-mode`, whose values Rule-3 reads. Scoped: no guard requires a key a Rule names to exist in the live table (`preferences.py` checks the table's own rows and that each `read by` Rule exists; `references.py` resolves `preference.read_by->rule`, not rule→preference), so the order "#215's preference PR first" is conduct, stated here, not a gate. The package's preference schema (`dyad/templates/PREFERENCES.md`, whose missing keys warn) does not yet carry `dwork-trace`; until it does, an install reads the default `always`. |
| 10 | A trace leaks transcript text (credentials, the Operator's unrecorded words) into the corpus. | **Refuted by construction, tested** | Text is kept only on Operator messages, for matching, and never formatted; the report prints timestamps, durations, tool names and counts. The test plants a marker in every assistant text and tool result of its fixture and asserts it, the prompt and the tool inputs are absent from the output. |

Pairwise (Rule-5). **3–1**: the trace file is instance state under `<instance>/d-work/traces/` (agent zone),
carried by the Done ledger commit; no zone added. **3–2**: a trace is evidence, not a ratification event; the
Done-`Y` binds as before. The preference `dwork-trace` is read by Rule-3 alone (its `read by` cell, #215); no other Rule's trigger
reads it, so no pair instructs differently on it. **3–4**: one bullet inside an existing clause — Intent, Target, Boundaries and
Conditions unchanged, so the counts are as before. **3–5**: no Rule's concern moves. **3–6**: one term,
`d-work trace` (owner 3, used by 3), used verbatim by the new bullet. **3–7**: the trace reads provenance
records and never writes one; Rule-7 property 2 (the raw transcript is never committed) is what the trace
obeys by reading in place and printing no text. **3–8**: running the trace writes one repo file, a repo
transaction's content, not a host action; the run-book step is classed reversible with its undo, the
sysadmin form. **3–9**: the attacks above are Rule-9's form. **3–10**: the bottleneck line informs a
proposal, never frames one. **3–11**: play-book, run-book and script are core-craft files under `dyad/`, the
traces instance — Rule-11 property 1's split; no host string enters the core. **3–12**: `trace.py` carries
`INVARIANTS`, enforced at import, and `dyad/tests/test_trace.py` at the mapped path. **3–13**: this is
Rule-13 property 1 discharged — the third hand measurement became code. **3–14**: Claude Code stays the kernel
row it is; its transcript is read as an optional input, never a dependency a guard needs. **3–15**: the
trace reads the plan file and changes no phase. **3–16**: the d-work store gains one directory of one file per id, written once by the session that
receives the Done-`Y` — collision-free in the same way as rows and plans; rows, transitions and presence
untouched. **3–18**: no
Operator-run command. **3–19**: a core run-book with its own section set (Rule-19 Boundaries), no server.
**3–20**: the new paths in Rule-3's text are `rule.text->path` references the register already resolves.
Coherent, orthogonal.

Disposition: see ledger #213.

## Amendment — d-work #227 (2026-10-06, the trace guard)
**Claim (Operator, via #227: "recommend next best action per DAG sequence", plan-`Y` 2026-10-06; revision 2
plan-`Y` the same day):** Rule-3's records whose check runs only inside Rule-12's suite move to registered
guards, and the live tests that only re-asserted a core guard's verdict lose that assertion (#217).
Mechanisms gains one sentence naming the trace guard.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A new registry entry falsifies a released craft's pinned entity list, so it cannot land (the reason `incidents.py` stayed a script, row #170). | **Confirmed for `incident`; refuted for `trace`.** | `crafts/sysarch/tests/test_project_entities.py` asserts `incident` has no card, and the first push was refused on it (incident row, 2026-10-06). The incident guard waits on #170. `trace` is not pinned: the craft derives its entity set from the registry (#98). |
| 2 | A guard needs a references-register entry, and `trace` has none. | **Confirmed.** | `trace.id->row` added to `references.REFERENCES`, resolved by the trace guard itself (`guard:agent/traces.py`, listed, not re-run). |
| 3 | The guard doubles the check: the suite runs it too. | **Refuted after the edit.** | `test_live_trace_store_is_well_formed` is deleted; the store's fixture tests stay. |
| 4 | Deleting a duplicate live assertion loses coverage. | **Refuted.** | Each removed assertion was the same call over the same tree the guard pass makes on every push and evidence run (#217 attack 4). Where a live test also pinned a count (`test_records`' 20 package records, `test_rules`' 15 Rules, `test_vocabulary`'s 90 terms, the register's kind count, provenance's no-warning floor), the count stays. |

**Pairwise (Rule-5).** **3–1**: agent zone, one PR. **3–2**: a guard is not a ratification event. **3–4**:
Rule-3 keeps its block; one Mechanisms sentence. **3–5**: Rule-3 alone owns the trace store; orthogonal.
**3–6**: no new Agent term. **3–7**: the provenance guard is untouched. **3–8**: no host action. **3–9, 3–10**:
the table above; one `Y/N`. **3–11**: the guard sits under `dyad/guards/agent/` and is discovered, never
hand-listed. **3–12**: it carries `INVARIANTS` and a mapped test. **3–13, 3–14**: no import; kernel only.
**3–15, 3–16**: no phase or store change. **3–18, 3–19**: no Operator command, no server. **3–20**: one
register row, resolved by the new guard. Coherent, orthogonal.

Disposition: see ledger #227.

## Amendment — d-work #290 (2026-10-14, the mandate: an accreted row in implicit mode, and the board's one exit)
**Claim (Operator, 2026-10-14, refusing revision 4 of plan #290):** "batch is a solution **if**
individual dispositions can be superseded with a 'meta-disposition'." Read with the prompt that
opened the row — "as the cos session, you primary objective is to ensure that operator's attention
is scaled in the way that Operator chooses", and "asking me to disposition a merge is indicative of
a failure mode of the `d-work` workflow" — the claim is that one d-work's dispositions may stand for
the rows it spawns, so that a tree of any size costs the Operator two acts: one plan-`Y` and one
Done-`Y`.

The design is **adopted, not coined** (Rule-13 property 1). `crafts/countersign/` already models it:
`countersign:implicit mode` ("countersigned in advance by a standing mandate"), the
`countersign:mandate` that countersigns it, `countersign:basis` for a disposition's kind of cover,
the `countersign:delegate edge` and `countersign:escalate edge` for the two mode changes, and
`countersign:amend` for the `N`-with-text this amendment answers
(`crafts/countersign/vocabulary/CRAFT.md`). That craft's `rules/interaction.md` §4 writes the
implicit lifecycle — "is it covered by a mandate? If yes: execute within the mandate's scope, then a
countersign report. If no: escalation → explicit" — and its §7 lists three of this amendment's four
pieces as owed to dyad-system and **not yet adopted**: `amend` in the answer grammar (I2), a mandate
record rather than preference prose (I7), and a `mode` field on rows (I7). An **accreted row** — one
the Agent opens while executing another — is **117 of this instance's 280 rows**, measured in
`agent-corpus/audits/2026-10-14-operator-attention.md`; the preference that switches the mode is
`accretion` (`preferences-corpus/PREFERENCES.md`, an **authority preference** in that craft's §5
classification, where `concise-mode`, `batch-disposition-mode`, `merge-disposition` and `delegation`
are form preferences that authorize nothing).

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | **This record's own `#137` amendment forbids the design.** Survivor **3–15** reads "each mode's child d-work stores its own plan before its plan-`Y`", disposed by the Operator's Done-`Y` on 2026-09-23. Rule-9's Form implements only survivors, so either 3–15 is refuted by name or this whole amendment is a Rule-9 breach. | **Refuted by name, 21 days later, by the ledger 3–15 was written about.** 3–15 was the Rule-5 *pairwise* answer to a coherence question — does the hardening exercise add a phase to Rule-15? — and the half that answers it is "its phases planned in that d-work's own plan file first … no phase added". The per-child plan-`Y` rode along as a by-product, asserted of rows none of which existed. Both exercises that have since run it refute it. #116: 9 children (#117–#125), all `done`, **exactly 2 disposed entries each, 18 dispositions for one exercise**. #259: 23 children (#262–#284) opened 2026-10-10, **23 of 23 `backlog`, no plan file for any of them** (`ls agent-corpus/d-work/plans/` holds none of 262–284), so the parent gate — "asked only when every child is `done` or `blocked`" — makes #259's own Done question **unaskable**, and `dyadlib.TRANSITIONS` (`dyad/scripts/dyadlib.py:448`) gives `backlog` exactly one successor, `open`. And the only four rows in 280 that ever reached `done` on **one** disposition — #162–#165, under #199 — hold no `Y plan` entry and have **no plan file at all**: one shared batch Done-`Y` closed all four (`rows/162.md`–`rows/165.md`). 3–15 is false of every child row this ledger has. | **3–15 is narrowed, not deleted.** Its coherence half stands verbatim: the exercise runs inside the d-work the prompt opened, its phases are planned in that d-work's own plan file first, and Rule-15 gains no phase. Its plan half is replaced: **a child row whose existence the authorized plan describes, inside the mandate scope that plan states, stores no plan of its own — the mandate's plan file is its plan (Rule-15 phase 2, amendment #290), and the mandate's Done-`Y`, which names it in the accreted list, is its verification. A child whose work departs from the mandate scope leaves implicit mode by the escalate edge and is then planned and disposed exactly as 3–15 said.** So 3–15 survives for every escalated row and for every child of a plan that states no mandate scope — which is every plan written before this amendment, #137's own included. |
| 2 | Scope has no clause for a row the Agent opens: "Every Operator prompt opens a d-work. There are no exemptions." A third origin is self-initiation, which `interaction.md`'s **I6** forbids by name and which this ledger already shows the cost of — **14 rows born with no Operator act whatsoever (#38, #70, #129–#132, #134, #136, #170–#173, #177, #181), every one still `backlog`, not one ever moved.** | **Confirmed, and it removed half the design.** The "park a row with nothing" option is dropped: `provenance.py:254-258` refuses a row whose record gains no entry, `:259-261` a `backlog` row with no disposition entry, and `package.py:946` refuses `dwork new` without the Operator's words. The refusals are right, and I6 says why. | Scope names accretion as a **third thing that opens a row**, beside a prompt and a disposition, and in the same breath says what it is not: it **opens no d-work** in the sense of Scope's first bullet — no Operator prompt was sent, so nothing is suspended and nothing stacks. I6 holds because the row is not self-initiated: its record's entry 1 is the **mandate's own Operator words**, copied verbatim with the note `mandate #<id>, <the mandate's own date>` (Rule-7 property 4, amendment #290), so its initiation is a prompt the Operator did write, on another row, disclosed as such. |
| 3 | Plan's "No exemptions: a plan may be one line … but the question is asked" gains its first exemption, and the Agent writes the plan that bounds what it may accrete. | **Confirmed, answered structurally.** Three fences, each an artefact rather than an argument: the **mandate scope** is a stated rule and a stated ceiling the Operator reads *before* disposing; the **escalate edge** returns anything outside it to explicit mode; and the **completion evidence lists every row actually accreted** — id, mode, what it holds, what it cost — so the Done-`Y` sees the delivered set, not the promised one. | The exemption is to the *question*, never to the plan: the mutation of an accreted row is authorized by the mandate's plan-`Y` only while the plan describes it. A plan stating no mandate scope accretes nothing. |
| 4 | Never-accretable classes are a judgment call the Agent makes at speed. | **Survives, scoped — and the list is Rule-2's, not this Rule's.** What a `Y` may bind to is Rule-2's concern, so Binding of approval holds the list and Scope defers to it in one sentence. Four of its items are mechanical to recognise: a destructive host action (Rule-8 keeps its own counter-prompt), a release (Rule-11 — it publishes to the world), a **Rule-3 Intake** (its words are another Operator's, Rule-7 property 4), and a preference change. The fifth — "any mutation outside the plan" — is the escalate edge and is inference, as "work that departs from the plan is a new plan" already is. | The list is in Rule-2's Binding, read before the plan states a scope, not consulted at the moment of accreting. 28 of the 117 accreted rows are Intakes, so the exclusion is load-bearing rather than decorative. |
| 5 | The Done-`Y` becomes a rubber stamp: one `Y` over a parent and 23 children, on a plan of four revisions. | **Confirmed and conceded.** #259 is the live case, and it is worse than heavy today — the question cannot lawfully be asked at all. A single `Y` is verification only while the reply is readable in one sitting. | **No cap is proposed**: how many rows one plan-`Y` may stand for is the Operator's number, and the Rule requires only that the ceiling be *stated*. What makes refusal possible is the accreted list, which is why its omission is a breach of this Rule as every other omission in the completion evidence already is. |
| 6 | The Operator uses an accreted row's plan-`Y` as a veto, so inheritance removes a power in use. | **Confirmed, by two rows.** #249 reads `2026-10-08 Y backlog` then `Y shape (…)` then `2026-10-08 N plan` — opened by the Operator and its plan then refused. #175 holds two `N plan` entries. Inheritance would have authorized what the Operator declined. | The escalate edge is in the mutation because of this, and #249 is named in it: its plan stands refused and no mandate reaches it. |
| 7 | The parent gate should stay strict: accepting a `backlog` child lets a parent close over work it never delivered. | **Survives, scoped.** It is why the amendment changes only whether the question may be *asked*. Rule-3 already accepts `blocked`, which is equally undelivered, and the table refuses `blocked → done` as well, so the escape admitted here is no wider than the one the gate already names. | "The parent completes only on its own Done-`Y`" is unchanged; the completion evidence lists every deferred child by id and state, so closing the parent loses nothing a reader could have had. |
| 8 | The board needs no exit: `archived` is unused because nothing needs archiving. | **Refuted, measured.** `archived` has **0 uses in 280 rows**; **75 rows sit in `backlog`**, median age **21 days**, 44 of them ≥14 days, the oldest 30; of the 37 rows ever born with a `Y backlog` first entry, **35 are still `backlog` — a 5.4% drain**. Rule-3's own `archived` bullet already *defines* the act ("retired from the working board by an Operator disposition naming the row(s)"); only `dyadlib.TRANSITIONS` forbade it from where 75 of the rows are. | `backlog → archived` and a **retirement form**, `Y/N: archive #a, #b, … #k?` — one Operator question over k rows, clerically executed by `dyad dwork state <id> archived` (`dyad/rules/RULE-3-d-work.md`, the `archived` bullet) — no new verb, one new legal source state. Cheapening the inflow without opening the drain makes the board worse, which is why the drain is item (1) of the mutation and not an extra. |
| 9 | `amend` is already covered by "any other response", so naming it is vocabulary for its own sake. | **Refuted.** "Any other response" says what an answer does *not* authorize and nothing about a refusal that asks for a revision in the same words — the disposition this very amendment answers, and the one the Operator has given twice (#175, #249). `interaction.md` §2 maps it as the third answer of the grammar and §7 lists its absence as an I2 gap. | Rule-3 gains an `## Answer grammar` section naming all three answers as the craft defines them — `Y`, bare `N`, and `N` with text as **amend**: the proposal refused and its revision asked for in the same words, a linked re-entry whose text is entered as a `prompt` entry of the refused d-work's own record and which opens no second row when what it asks for is that same proposal revised. Silence is not consent is stated there too (I8). No new behaviour: the practice is already this, and this amendment is its own live instance. |
| 10 | A mandate carried in `disposed` is a pointer, and `rows.ENTRY` (`dyad/guards/agent/rows.py:40`) admits only a dated `Y` or `N`, so there is nowhere to put it. | **Confirmed, and it fixed the entry shape.** A mandate is carried by **replication plus a note**, never by a bare reference: `disposed: <date> Y plan (mandate #<id>)`, beside the `(batch #a,#b,#c)` shape the column already admits. Verified live during planning against the kernel itself, by calling `prs.check` on synthetic rows: `open` + `Y plan (mandate #259)` **passes** the plan gate; `open` with an empty `disposed`, `open` with `Y mandate #259`, and `backlog` + `Y plan (mandate #259)` all fail. | An implicit-mode row is born **`open`** — never `backlog`, which `provenance.py:262-264` and `package.py:971-972` can only open on the Operator's own prompt — carrying that entry, with the mandate's words as record entry 1. No code change is needed to make it lawful. |
| 11 | `'Y plan' in row.disposed` is a substring test on free text (`prs.py:46`), so an inherited authorization inherits that unreliability. | **Confirmed, and not fixed here.** `Y plan; N plan (withdrawn)` passes the gate, and the 2026-10-08 audit's L2-1 lists five strings that pass it while meaning the opposite. A mandate makes that string load-bearing for more rows than before. | Named as the follow-on it already is (that audit's candidate row 2, *parse `disposed` into kinded entries*), and as the condition under which the `mode` field is data rather than prose. The audit records it; this amendment does not build it. |
| 12 | The completion evidence is already the largest thing the Operator is handed, and the accreted list makes it longer. | **Confirmed.** ~217 lines × the 190 `Y done` dispositions this ledger holds. The list grows it by one line per accreted row. | Accepted, and stated: moving the evidence block to the PR body with its `evidence-sha256` in the reply is the larger reduction, a Rule-2 and Rule-14 property 3 change with its own d-work, named in the plan and not taken here. |

**Pairwise (Rule-5).** The amendment touches Scope, Plan, Ledger, Completion, Batch disposition and
the answer grammar, and the neighbours it could have collided with are these. **3–1** — no zone
moves: rows, plan files, provenance records and traces are all `<instance>/d-work/` (agent zone),
the preference is its own zone's PR, and a retirement is a ledger-only commit the fence already
admits. **3–2** — Rule-2 owns the events and gains the mandate clause in its own Binding (its
record, amendment #290): a plan-`Y` also authorizes the class its mandate scope names, and the
Done-`Y` ratifies the accreted set *as the evidence listed it*. Rule-2 also keeps the list of what is **never** accretable, since that is a
statement about what a `Y` may bind to; Rule-3 keeps only what the question looks like and what the
reply must carry; **no ratification event is removed and none is added** —
an accreted row is a ledger artefact, which Rule-2 already classes clerical. **3–4** — the block is
unchanged: one Intent, one Target, and no Boundary or Condition count moves, so the counts
`rules.py` checks are as before. **3–5** — concerns stay put: Rule-15 owns the phases (it gains the
accreted row's want of a base commit, in its own record), Rule-16 the store and the transition table
(it gains `backlog → archived`), Rule-7 the words (it gains the mandate note), Rule-2 the binding.
Nothing is owned twice. **3–6** — two terms are defined, `accreted row` and `mandate scope`,
owner 3; seven are **referenced** as `countersign:<term>` in the header — `mandate`,
`implicit mode`, `explicit mode`, `basis`, `delegate edge`, `escalate edge`, `amend` — exactly as
the `sysarch:` and `sysadmin:` terms are, never redefined (Rule-6, Master record). One term
*changes*: `archived` now reads "a `done` or `backlog` d-work retired …", and Rule-6's trigger
requires every Rule in its `used by` to be named and still read correctly — 3 (the state's bullet
and the retirement form) and 16 (the table and the Store sentence), both of which this d-work edits
in the same PR. **3–7** — Rule-7 stores the mandate's
words with their note and keeps property 5's per-commit count, which the replicated entry satisfies
by construction; Rule-3 decides which rows a mandate may reach. **3–8** — a destructive host action
is never accretable and keeps its own counter-prompt, unconditionally and unbatched, as this
record's `#106` amendment already settled. **3–9** — this table is Rule-9's form, and survivor 3–15
is refuted here rather than worked around. **3–10** — one `Y/N`, last line, per reply; a mandate
changes how many questions exist, never how one is framed. **3–11** — a release is never accretable
("a release publishes to the world"), and Rule-11's own release batch form is untouched; the
play-book, the run-book and the CLI verbs are core-craft files, the rows and traces instance.
**3–12** — `dyadlib.TRANSITIONS`, `dyadlib.FIELDS`, the row fence and the `retire` verb each carry
their mapped test, and `dyad/tests/test_dyadlib_rows.py:17-28` already parses Rule-16's
transition sentence and asserts it equals the table, so the Rule and the code move in one commit. **3–13** —
property 1 discharged twice over: the vocabulary and the lifecycle are imported from a craft already
in the tree rather than authored, and **owed** once: 27 rows already carry an inherited
authorization in two ad-hoc note shapes — #96 and #97 as `Y plan (named in plan 94.md, deferred)`,
#240, #257 and #262–#284 as `Y backlog (… from #N's plan-Y)` — so the recurrence proposes a
`dwork new --mandate <id>` that writes the entry and copies the mandate's words, which the plan
names and the Operator may decline (property 1's own last sentence). Until it exists the entry is
hand-written in the one shape this amendment fixes. **3–14** — kernel only: no import, no World row, and the mandate's own
check runs on the kernel-only path with every other guard. **3–15** — attack 1: the coherence half
of 3–15 stands and Rule-15 still gains no phase; its plan half is narrowed, and Rule-15's own record
carries the phase-2 sentence. **3–16** — the store gains one transition and one **optional** field,
`mode` (absent reads `explicit`, so no row is migrated and a row that carries it never loses it);
rows stay one file per id, and a retirement touches exactly the rows it names. Rule-16 also records
what the design costs its own store: a plan-less row contributes nothing to the presence `files`
union. **3–18** — no
Operator-executed command: 0 ops scripts exist on this instance. **3–19** — no server instance, and
the digest play-book's steps are a core run-book with its own section set (Rule-19 Boundaries).
**3–20** — the mandate id in a row's `disposed` is read by the same free-text column Rule-20 already
declines to resolve (`row.disposed->pr` is a `world` kind); no reference kind is added here, and the
unresolved-kind gap is the audit's finding, not a new one. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #290.

## Amendment — d-work #309 (2026-10-15, the d-work play-book: entity records and the machine's inputs)
Claim: the d-work framework can be stated whole, as a play-book and as data, without a second text on any
trigger a Rule owns. The Operator's prompt (relayed via cos, #296): formalize the architecture of the d-work
framework — play-book and entity records — and d-work as a finite-state machine that carries state to
complete a countersigned work session. Plan `agent-corpus/d-work/plans/309.md` (asked and answered as #298;
re-allocated after an id collision, the plan's revision note).

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | The architecture already exists across Rules 3, 7, 15 and 16; a play-book restating it is a second text on one trigger, a Rule-5 hazard. | survives, scoped | A play-book is not a Rule and instructs on no trigger (Rule-4 Boundaries; the vocabulary: read by a Rule, never a Rule). It cites every state, form and store to its owner and adds only what no Rule holds — the input and the record per edge — as data pinned by a test; on divergence the Rule wins and the test turns red, the arrangement `test_dyadlib_rows.py` already keeps between Rule-16 and `TRANSITIONS`. |
| 2 | A play-book is for a recurring decision; a lifecycle is a process. | survives, scoped | The decision recurs at every state change — which transition is legal, what input, what record — and was made by inference against the CLI help and four Rules (Rule-13's trigger). |
| 3 | `TRANSITIONS` already is the machine; `INPUTS` is dead data. | refuted | A successor relation cannot say `planned → open` is an Agent act and `open → done` the Operator's. `INPUTS` has a consumer on day one (the pinning test) and its invariants encode Rule-2 and countersign I6 at import. Driving `dwork state`'s refusals from it is a named follow-on, not claimed. |
| 4 | A core change needs a `VERSION` bump with no landable bundle order (#230). | refuted here | `VERSION` 0.10.2 is already past `dyad-operator-v0.10.1`; the drift guard fails only an unchanged `VERSION`; the bundle guard already warns on this state (#170's shape). |
| 5 | The countersign mapping is the craft's (D1–D8); restating it breaches the craft/core boundary. | survives, scoped | The play-book names the craft's terms by craft name and cites §4 and D1–D8; it adds the mapping of inputs — which answer moves which state — which is core process. The craft's own drift (D1 derives `explicit` for every row although rows carry `mode` since #290) is named in the plan, not fixed here. |
| 6 | Easy agreement. | pushed | Attacks 1 and 5 landed and bound the text: cite, never redefine; data where the Rule has none; the craft's drift left to the craft. |
| 7 | "Entity records" means the records of the play-book entity (its run-book's events). | survives, stated | The run-book supplies those too; the entity table would then be over-delivery. The Operator's `Y` to the plan as read disposes the reading. |
| 8 | The one Rule-3 sentence is unnecessary: `disposition-digest.md` says "read by Rule-3" and Rule-3 does not name it, so the precedent is to cite nothing. | refuted | Three of the five play-books are named by Rule-3 where it reads them, and `test_playbooks.py` asserts the citation for each; the digest's missing sentence is a gap the plan names, not a precedent to extend. |

Pairwise (Rule-5), this edit against every other Rule. **3–1** — the play-book, run-book, data, test and
record are one tree, `dyad/*`, agent zone; one PR. **3–2** — the invariant *only the Operator closes* is
Rule-2's Binding restated as data, not a new ratification event; Rule-2 is not edited. **3–4** — one
bullet under Ledger; the block (Intent, Target, Boundaries, Conditions) is unchanged. **3–5** — this
statement. **3–6** — no term is added or redefined: `play-book`, `transition`, `disposition`, `plan-Y`,
`Done-Y`, `accreted row` are used in their vocabulary sense; the countersign terms are cited by craft
name, as #290 already does. **3–7** — the machine's `prompt` and `disposition` kinds are Rule-7's two entry
kinds; the `backlog → open` invariant is its transaction check as data; Rule-7 is not edited. **3–8** — no
host action; the run-book's classes are read-only or reversible, none destructive. **3–9** — this record.
**3–10** — the play-book's lifecycle step 2 cites Rule-10's form; no form changes. **3–11** — `VERSION`
unchanged (attack 4); the play-book and run-book are core-craft files; the instance's rows are untouched.
**3–12** — `INPUTS` carries six invariants enforced at import and a mapped test; the run-book is checked by
the sysadmin craft's guard where present, as the other core run-books are. **3–13** — property 1 discharged:
the inference at every row write becomes data; the criteria are untouched. **3–14** — kernel only: stdlib,
no World row; the invariants run on the kernel-only path. **3–15** — the play-book cites Rule-15's phases and
the accreted-row bullet; no phase is added; `planned → open` names Rule-15 phase 2 as the clerical input.
**3–16** — `TRANSITIONS`, `NEW_STATES` and the store are unchanged; `INPUTS` is derived over them and its
first invariant holds them equal; Rule-16's bullet still parses to the same table. **3–18** — no
Operator-executed command. **3–19** — the run-book is a core run-book with its own section set (Rule-19
Boundaries), its events the sysadmin craft's where recorded. **3–20** — no reference kind is added; the
entity table lists the register's existing kinds per record, read from `references.REFERENCES`, and the
play-book's path is resolved by `rule.text->path`. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #309.

## Amendment — d-work #202 (2026-10-15, the Done state follows the merge)

Claim: *recording the Done-`Y` should set the row `done`.* Four Rules are each correct and jointly
leave a ratified merge that still needs one push with no admissible sequence — Rule-3 orders the record
before the merge, the record's command sets the state, `done` is terminal (Rule-16), and the plan gate
refuses every commit citing a terminal row (`prs.py:43-45`). Twelve rows of
`agent-corpus/audits/INCIDENTS.md` between 2026-09-30 and 2026-10-15 are that one mechanism (`:89`,
`:91`, `:123`, `:136`, `:156`, `:170`, `:175`, `:176`, `:178`, `:180`, `:181`, `:182`) — eleven distinct
instances, since `:175` and `:176` are the two rows of one event (#243) — four recovery
rows were paid for it (#196, #200, #246, #245→#239), three rows exist only because of it (#321, #322,
#323), and 164 rows' `disposed` claims `merges PR #n` where nothing reads the claim — five of those
claims are false, one of them (#309 / PR #394) found while planning this and not in the log at all.

| # | attack | result | survivor |
|---|--------|--------|----------|
| A1 | This weakens Rule-2: the record no longer precedes the merge. | refuted | The record is the `disposed` entry plus the provenance entry — what `dwork state … -d --said` writes and what Rule-3's own sentence calls "the ledger's own record of the `Y`". It still precedes the merge, by one commit. Rule-2 is not edited; its #138 hosting-unreachable sentence ("the row's `disposed` and the completion reply record it") becomes exactly right. |
| A2 | The order cannot be declared: making the `→ done` edge honest about being traversed by a clerical act falsifies `only-the-operator-closes` (`dyadlib.py:653`), false for `{clerical}` and for `{disposition, clerical}` alike. | refuted | The input does not change: it is the Operator's `Y`. The landing is a precondition on a clerical write, exactly as the merge is clerical execution of that same `Y` (Rule-2, Binding). Only the two `INPUTS` description strings change, so the invariant holds unweakened and no new state is needed to keep it true. |
| A3 | A row that never reaches `done` is invisible — `dwork list` prints `[planned]` either way — and the second commit is an obligation no mechanism reads. | survives, scoped | `rows.done_recorded_not_closed` is the witness, read where it cannot be missed: every push and every `check --evidence`, inside the block the completion reply pastes and inside its sha256. A warn and not a FAIL, because a FAIL would refuse exactly the pushes the interval exists to permit. Zero rows were in that state when this shipped. |
| A4 | During the interval the row is a live citation target, so a branch citing it can carry content the Done-`Y` never verified. | survives, scoped, wider than first written | **Unbounded by mechanism, bounded by conduct.** The first draft of this survivor said Rule-2's heads-unchanged clause bounds it; the adversarial pass refuted that — the clause bounds re-*executing* the old `Y` on a moved head, and says nothing about the plan gate admitting a *second* branch citing the same row. Demonstrated: after the Done record, a second branch citing the row is admitted, both PRs merge, and the closing commit still passes, because `landing_problems` asks only whether the operative entry's head is reachable, never whether anything else landed. What remains is the warn (the interval is visible in every evidence block) and the Agent's conduct. The tight mechanical bound — admit a range only when its non-ledger tree equals `git merge-tree`'s resolution of the ratified head against `main` — is named and declined: it would refuse a legitimate resolution that differs mechanically from the predicted one, and a false refusal is a new closure of the same kind. |
| A5 | It does not save the second Done-`Y`: a rebase changes the head, so the `Y` is voided and the question re-asked (`disposition-digest.md` step 3). | confirmed | Stated in the Rule text. What goes is the recovery row — three dispositions, a new plan, reworded commit messages — not the re-prompt, which is one. The interval gives the mandatory re-prompt a live row to land on; it is not a licence to execute the old `Y`. |
| A6 | A named state (`verified`) is the better design: the board shows it, the parent clause and the retirement form can admit it, and its exit is exact. | survives, scoped | Its exactness is the head sha plus `merge-base --is-ancestor`, adopted here whole. What it adds beyond that is visibility, at the price of four PRs across three zones in a fixed order (a craft projector's `columns-are-states` equality relaxed first, Rule-16's table, a vocabulary row, a run-book `land` step), which is the version/zone family of this same failure mode (#170): a fence whose landing needs the ordering discipline it supplies. Named as the follow-on if the warn proves too quiet. |
| A7 | "Every merge the `Y` named has landed" is decidable from git, so the warn should be a FAIL. | refuted as message-scanning, confirmed as ancestor-testing, and scoped: what is decided is the *head's* reachability, never that PR #n merged | Scanning merge subjects is unsound both ways: the live subject `Merge pull request #401: d-work #239 bank the file PR #355 never landed` reads as a merge of PR #355, the one PR this instance documents as never merged, and a tight `^Merge pull request #(\d+)` misses 34 of this repo's own conventions. Testing an ancestor is sound — hence `at <sha>` in the entry, and hence `landing_problems` may FAIL where `done_recorded_not_closed` only warns. |
| A8 | Easy agreement (Rule-9's trigger): mode M recurred within a day of every earlier warn-window mitigation. | pushed | The mechanical half those lacked is here: the order fence and the ancestor check FAIL, and only the interval's visibility warns. The refutation test is stated in advance — a thirteenth gate-after-Done row after this ships refutes the design, not the diagnosis. |
| A9 | The 164 rows already claiming `merges PR #n` should be migrated or re-judged. | refuted | Rows are append-only and the fence judges only commits in a pushed range, so nothing migrates and the false claims stay false — which is what an append-only store means. `references.py`'s `row.disposed->pr` extractor is `merge #(\d+)` and matches 2 tokens against 413 claims: a latent Rule-20 gap, named and left to Rule-20's own row. |
| A10 | One PR is too big: cut the three incident rows out and land them first, as the hold protocol's item 1 prescribes for a tail-append file. | refuted | Two PRs under one Done-`Y` must merge in sequence, and the second merge is the deadlock this amendment exists to fix — row #200's title is that finding ("one PR, one merge, nothing to push after it"). One PR, one merge. |

Pairwise (Rule-5), this edit against every other Rule. **3–1** — every path is one tree in the agent
zone (`dyad/*`, `agent-corpus/*`); one PR, one merge. **3–2** — no edit: Binding never mentions the row
state, it binds a `Y` to named PRs, to the guards' observed passes, to the evidence block and to
unchanged heads; the sentence it relies on stays literally true because the record is the entry, not the
state. One mechanical consequence, found by the adversarial pass and answered: the 2026-10-08
chain-of-authority audit's row C2 recorded that *nothing couples a state transition to a disposition* —
`dwork state <id> done` with no `-d/--said` writes the state with no entry behind it, and only conduct
(180 `done` rows, 0 without a done entry) stood in the way. This amendment makes that dispositionless
write the prescribed closing act, so the conduct regularity is deliberately broken; `landing_problems`
therefore refuses a commit that sets `done` on a row carrying no `Y done` entry, which restores the
coupling mechanically at the moment this change moves it. **3–4** — the block is untouched; the edits sit inside Ledger, Completion counter-prompt and
Mechanisms. **3–5** — this statement. **3–6** — one definition changes (`done`) and no term is coined;
"the Done record commit" is a description, so `vocabulary.py`'s checks are unaffected. **3–7** — property
3 is what the record act obeys (the entry is written in the commit of the event it records) and property
5's one-to-one count holds per commit: the record commit adds one `disposed` entry and one `disposition`
entry, the closing commit adds neither. **3–8** — no host action; the interval makes a post-merge
change-log row physically possible, which is Rule-8's record inside Rule-3's window, ownership unchanged.
**3–9** — this record, with the easy-agreement attack pushed and a refutation test named in advance.
**3–10** — the plan carried one path, the `verified` state as its counter, and one `Y/N`. **3–11** — every
changed file is core-craft content under `dyad/` with no instance string; no `VERSION` or `BUNDLE.md`
change is implied by a guard edit and none is made, which keeps the version/zone closure out of this PR.
**3–12** — the new clauses carry their mechanical check as tests (`test_rows.py`, eight cases); no new
`rows.INVARIANTS` entry, because `crafts/sysarch/tests/test_project_entities.py:319` pins that list to one
name and a second would redden a craft test inside an agent PR. **3–13** — property 1 discharged: the
reading of a row's `Y done` against its state becomes code. **3–14** — kernel only, Python and git
(`cat-file`, `merge-base --is-ancestor`), running at `check --guards --pre-push` and inside
`check --evidence`; the hosting stays a library adapter and is deliberately not consulted, which is why
the interval warns. **3–15** — no phase changes; phase 2 now spans three acts instead of one. **3–16** —
`TRANSITIONS`, `STATES`, `NEW_STATES` and `TERMINAL_STATES` are untouched: the order moves *when* the
terminal edge is taken and adds no way back, so "state never regresses" and "a done d-work is never
reopened" are unweakened. The interval's states are therefore `open` and `planned` only: the first draft
of the completion clause also named `blocked`, which the table gives no edge to `done`, so the close
would have been refused by the pre-existing state clause — corrected before the push, and the lesson is
that an interval sentence must be read against the table rather than against the plan gate's admissible
set. A row in the interval stays in its session's presence `rows` for longer, which
is more disclosure, not less. **3–18** — no Operator-executed command. **3–19** — the core run-book's
`Complete` splits into `Record` + `Complete`, keeping its own declared section set (Rule-19 Boundaries).
**3–20** — a commit sha enters a parsed store field for the first time (`HEAD_AT` over `row.disposed`,
which the register already reads as `row.disposed->pr`, resolver `world`). The structurally identical kind
exists for the other store — `plan.base->commit`, resolver `commit_exists` — so `row.disposed->commit`
is a kind with a resolver already written, and it is **deliberately left unregistered**: Rule-20 property 2
makes an unresolved reference *fail*, and a PR head resolves in the clone that pushed it and in no other,
so registering it would reproduce the sixteen-minute cross-clone push block of `INCIDENTS.md:184` on every
clone that had not fetched the branch. `landing_problems` makes the same judgment itself and skips rather
than fails. Named as the open edge it is, for Rule-20's own row to take or refuse. A second interaction,
accepted rather than fixed: `references.base_commit` skips a plan's base commit only for a `done` or
`archived` row, so a row in this interval keeps that check live, where before the amendment the Done
record quieted it at once — one more reading in every clone for as long as the interval lasts, and the
asymmetry #321's I7 already recorded. Others unchanged. Coherent, orthogonal.

**Not delivered, and said here rather than in the completion reply alone.** The authorized plan's item 4
promised `--landed <sha>` as an explicit override for a hosting that squashes or rebases. It is not
shipped and the sentence that described it is gone from the Rule: the entry is written *before* the merge,
so a squash's sha cannot be in it, and the only routes to adding one afterwards are a second disposition
entry (which would read as a second Done-`Y` in Rule-7's chain) or an in-place rewrite of an entry the
fence judges only on append. What takes its place is the route the Rule already has: ask the Done again on
the head that did land, and the later entry governs. An instance whose hosting never produces the ratified
head as an ancestor therefore pays one extra Done question per merge, which is stated and not fenced.

Disposition: see ledger #202.
