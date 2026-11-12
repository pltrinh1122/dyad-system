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

## Amendment — d-work #381 (2026-10-22, the countersign model carried by the core; #369 C3)
Scope and Answer grammar cited the countersign craft by path five times (`crafts/countersign/vocabulary/CRAFT.md`,
`rules/interaction.md` ×3, `crafts/countersign/`), and the craft is retired by #369 (direction (c) of the #330
audit's D-10, `agent-corpus/falsification/countersign-consolidation.md`). The citations now name the core
play-book `dyad/playbooks/countersign-model.md`; Scope also names the **delegate edge** (the plan-`Y` that creates
a mandate) and the **mode lifecycle**, two of the five terms the reconciliation table (C2) adopts with this child.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A citation of a path the craft's retirement deletes turns `rule.text->path` red at C5 if any Rule still names it. | **Confirmed; closed here** | `grep -rn crafts/countersign dyad/rules/` is empty after this amendment; the one remaining mention of the craft is Provenance's history, by name and not by path. |
| 2 | Naming the delegate edge and the mode lifecycle adds two terms with no vocabulary row, breaking Rule-6's "defined once" at the push. | **Survives, scoped** | The rows are written (the C2 table) and held by the collision fence C1's attack 6 found: they enter `VOCABULARY.md` the moment `crafts/countersign/vocabulary/CRAFT.md` stops defining them, in the same d-work (#369), which is what Rule-6's condition asks; until then the words are prose a reader finds in the play-book's glossary. The orphan check is unaffected (it reads the vocabulary's rows, not the Rule's words). |
| 3 | A play-book is "an executable procedure … whose steps are a run-book" (the vocabulary); the model has no steps, so citing it as a play-book misuses the term. | **Survives as a concession** | The play-book says so in its second paragraph: it is the model the d-work play-book's steps realize, and it has no run-book. Rule-3's Ledger clause already reads one play-book (`d-work.md`); this citation adds a second file under the same directory, not a second kind. Whether the vocabulary's `play-book` row should widen is a C9-era question, not this child's. |
| 4 | Easy agreement: the edit is a path change. | **Pushed to 2 and 3** | Both change what the sentence commits to. |

Pairwise (Rule-5): 3–2 unchanged — Binding still owns what a plan-`Y` binds to and Scope still cites it. 3–6 two
terms named before their rows land, scoped by attack 2; the vocabulary stays the only definition. 3–12 Rule-12's
Boundaries gain the audit play-book's two kinds of check in the same child; neither Rule restates the other's.
3–13 "adopted rather than coined" still cites property 1, now of a core play-book. 3–15, 3–16 the accreted-row
bullets are untouched. 3–7, 3–9, 3–10, 3–11, 3–14, 3–18, 3–19, 3–20, 3–1, 3–4, 3–5, 3–8 untouched. Coherent,
orthogonal.

Disposition: see ledger #381 (accreted under #369; its Done rides that mandate's Done-`Y`).
## Amendment — d-work #379 (2026-10-22, #369 C7: what a session reads at start under `organization: m4`)
**Claim (plan #369):** under `m4` a session reads and reports its seat's board — the leader the cos-board of
programs, a member-cos the cos-board of its charter's domain — and how a board is read is the organization
craft's Operating Guide, never a Rule.

| # | attack | result | survivor |
|---|---|---|---|
| 1 | The session-start bullet already says "reports every row that is not `done`"; a board is a narrower read and the two conflict. | Refuted: the sentence scopes the read by seat under `m4` and leaves it whole under `flat`; the leader's board of programs is every parent row and its children, which is the whole working board for one pair. | Kept, with `flat` unchanged. |
| 2 | A core Rule citing a craft's Guide binds the Agent's process through a Tended document (Rule-4). | Refuted by the Rule-8/sysadmin precedent (revision 4 attack 1): the sentence keeps the process residue — read a board, report by seat — and cites the Guide for the practice. | Kept. |
| 3 | Three vocabulary terms for one sentence. | Survives as the price Rule-6 sets: a Rule uses a term only if the vocabulary defines it, and the terms are Rule-16's (owner 16). | Kept. |

**Pairwise (Rule-5).** **3–16**: Rule-16 owns the seat name and the form, Rule-3 what a session reads;
one owner each. **3–2**: nothing ratified. **3–6**: the three terms, owner 16, used by 3. Others unchanged.

Disposition: see ledger #379 (accreted under mandate #369; Done rides its Done-`Y`).

## Amendment — d-work #419 (2026-10-25, child C2 of #417: the cabinet craft's terms in the session-start bullet)
**Claim (plan #417, the Operator's `Y` of 2026-10-25; #416 revision 2):** the organization craft is renamed `cabinet`;
the leader's role is the cos and a member's a secretary. Ledger's session-start bullet names both and the Guide's
new path. A term rename, no change of what a session reads.

| # | attack | result |
|---|---|---|
| 1 | Renaming a term Rule-3 uses changes what the bullet binds. | Refuted: the bullet still says the leader reads the board of programs and a member seat the board of its charter's domain; only the names of the two roles and the path change. |
| 2 | `secretary` collides with an existing term. | Refuted: no Agent term, no preference key and no craft term is `secretary` (`vocabulary.py`, the craft guard's `check_craft`). |

**Pairwise (Rule-5).** **3–16**: Rule-16 owns the seat name and now the term `secretary`; Rule-3 uses it. **3–6**:
`member-cos` → `secretary`, owner 16, used by 3 and 16; `cos-board` reworded. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #419 (accreted under mandate #417; Done rides its Done-`Y`).

## Amendment — d-work #424 (2026-10-25, the form of a Done question relayed to the Operator)
**Claim (plan #424, the Operator's `Y` of 2026-10-25, batch #422,#423,#424):** a Done question the cos relays to the
Operator for a seat that is not attended is presented in the form the preference `relay-form` names — under `brief`
WHAT, WHY and HOW at the Operator's altitude — with the seat's evidence block quoted verbatim and the seat's own
question its last line; Rule-2's Binding is unchanged.

| # | attack | result |
|---|---|---|
| 1 | R29 ("a cos relays verbatim, never answers") and the Guide's "relay the words, not a summary" say the opposite. | Confirmed, and scoped: both bind the words that reach a *seat* — the Operator's prompt and disposition, which the seat acts on (Rule-7 property 4, the relayed prompt). Nothing bound the form in which a seat's question reaches the Operator; the two directions had been conflated. The sentence binds only the Operator-bound one; the vocabulary row `relayed prompt` (the seat-bound one) is unchanged. |
| 2 | Rule-10 already requires path, counter, reconciliation and one `Y/N` of every proposal. | Confirmed, partial: Rule-10 shapes the Agent's own proposal; a relayed one arrives in the seat's shape (#423's question did, and was passed through). WHAT/WHY/HOW is Rule-10's form applied by the cos to a seat's question, the seat's text quoted as evidence — Rule-10 still owns the form, this sentence only says it is applied on relay. |
| 3 | A preference is needed only if two values are wanted. | Survives: `verbatim` (the seat's question and evidence passed through, its last line the question) and `brief` (the cos's WHAT/WHY/HOW, the seat's words quoted); both keep the seat's question text as the `Y/N` line, so the `Y` binds to what the seat asked and Binding needs no edit. |

**Pairwise (Rule-5).** **3–2**: Binding untouched — the last line is the seat's own question, so the `Y` names what
the question named; a summary never stands in for the evidence block. **3–10**: Rule-10 owns the form of a proposal;
this sentence names where the cos applies it, owning no part of it. **3–7**: the seat-bound relay (verbatim, the
relayed prompt) is untouched; the Operator's answer is still entered verbatim. **3–16**: Rule-16 owns attendance and
the route; Rule-3 states only what a relayed Done question carries. **3–6**: no new Agent term — `relay-form` is a
preference key, defined in `preferences-corpus/`. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #424.

## Amendment — d-work #438 (2026-10-25, monitoring is no d-work: the events-only commit)
**Claim (plan #438, the Operator's `Y` of 2026-10-25, answering "Why should there be a standing row? Evaluate
alternatives for "monitoring" activities."):** monitoring is its own activity class, not a d-work — read-only,
standing, with nothing for a plan-`Y` to authorize and no Done to reach — so it opens no row. Its only write, the
events of read-only run-book commands, is clerical: an events-only range (every non-merge commit touching nothing
outside `<runbooks>/events/`, read commit by commit with rename detection off) goes to `main` without a row or a
PR; the PR guard skips it and the fence admits it as a ledger-only one; append-only is the events guard's.

| # | attack | result |
|---|---|---|
| 1 | A standing operate row with a batch mandate fits Rule-3 as it stands (alternative a). | Refuted: a row that never completes is the shape "terminates only when the Operator disposes `Y`" excludes; its plan-`Y` authorizes no mutation; the mandate's ceiling forces a fresh row and plan-`Y` every n batches, a question that decides nothing, and each batch is still a PR and a four-minute suite. |
| 2 | An events-only exemption beside the ledger-only one (alternative b). | Survives, scoped: an observation is no decision, the test Rule-2 states; the store's append-only guard (`sysadmin/events`) already exists; one commit stays one zone (Rule-1). Alone it commits every heartbeat (attack 3). |
| 3 | Events only on a change of reading (alternative c). | Survives, and is the craft's: the sysadmin craft's property 7 (amendment #438 there). With it a per-reply stream becomes a few events a day, and a mismatch appearing or clearing is still recorded. It does not stand without attack 2: a few events still each need a row and a PR under the old fence. |
| 4 | No record: the board reading, computed on demand (alternative f). | Survives, scoped: right for a reading nobody grades; the harness side is The World and kept nowhere, so recurrence (#409 G1) cannot be graded without the events. |
| 5 | Precedent (Rule-10 counter): the next class asking for a clerical exemption will cite this one. | Survives, bounded: Rule-2's own test — records, never a decision — and events of read-only commands only; a commit that chooses, or an event of a reversible or destructive command, fails it. |
| 6 | A commit carrying a ledger row and an event together would pass as both. | Refuted: one commit stays one zone (Rule-1), and each class is decided commit by commit by its own path, so a mixed commit is neither. |

**Pairwise (Rule-5).** **3–2**: Rule-2's *Not ratification* gains the matching bullet; Rule-3 owns the class and its
guards, Rule-2 only that it is not ratification. **3–12**: property 2's suite skip names the same range; Rule-3 owns
the definition, Rule-12 cites it. **3–1**: unchanged — one zone per commit; the events path is the host zone's.
**3–8**: unchanged — the read-only class is Rule-8's and the sysadmin craft's. **3–19**: unchanged — a deploy's health
pass is still completion evidence read from the run that observed it. **3–6**: no new Agent term; "events-only" is an
adjective, as "ledger-only" is. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #438.

## Amendment — d-work #477 (2026-10-26, C4 of #473: the guard wrapper is a step of `dyad-package.yml`)
**Claim (plan #473, the Operator's `Y` of 2026-10-26, and the Y recorded on #477 at 3393b19):** the CI wrapper this
Rule names, `.github/workflows/dyad-d-work.yml`, becomes a named step of `.github/workflows/dyad-package.yml` (job `package`),
same guard, same trigger (push to `main`, ledger-only paths ignored, and dispatch), still detecting; the Rule's
sentence names the new file and step, meaning unchanged.

| # | attack | result |
|---|---|---|
| 1 | One job couples the guards: a failure in one step hides the others. | Survives, scoped: CI here only corroborates after the merge (Rule-14 property 3); the blocking checks run before the push on the kernel-only path, every guard in one run. |
| 2 | Re-pointing before the old file is removed leaves two names for one check. | Refuted: this PR lands first and resolves on today's `main`, where both files exist; the removal PR follows, so no state names a missing file. |

**Pairwise (Rule-5).** **3–1**: the wrapper stays infra zone; changing it is still an infra-zone PR citing a Rule-3 d-work. **3–14**: unchanged — the step corroborates on `main` only. **3–20**: the new path resolves on today's `main`. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #477.

## Amendment — d-work #465 (2026-10-26, a `Y done` entry travels with its trace)
**Claim (plan #465, the Operator's `Y` of 2026-10-26):** the completion clause already requires, under
`dwork-trace: always`, that the Done **record** commit carry the d-work's trace; the fence now refuses that commit when
the trace is neither carried by it nor already on its base (`rows.trace_problems`), and `dwork state` refuses before
its first write. Six Done records (#455–#460) had carried none, a refused `dwork trace` going unseen (row 232, modes
E and Q of the incident index).

| # | attack | result |
|---|---|---|
| 1 | A mandate's accreted rows each gain a `Y done`, so each would need its own trace. | Refuted, scoped: an accreted row's Done rides the mandate's Done-`Y` (Scope), so the mandate's trace covers the set; the clause exempts an entry noted `mandate #<id>`, the note Rule-7 property 4 prescribes. The mandate's own entry still needs its trace. |
| 2 | Under the three-act Done, which commit must carry it? | Answered by the clause itself: the **record** commit, which adds the entry; the closing commit adds none and is not judged. A re-asked Done adds a second entry and finds the trace already on its base. |
| 3 | One batch entry might be read as covered by one trace. | Refuted: Batch disposition writes the same entry into every named d-work's own record, and the evidence cites each one's own trace; each named row needs `traces/<id>.md`. |
| 4 | The clause turns `main` red for history. | Refuted: it judges only entries a commit adds; earlier rows are never re-judged. |
| 5 | A commit that flips `dwork-trace` and adds an entry is judged under the wrong value. | Survives, accepted: a preference change is its own preferences-zone PR and never rides a ledger commit, so a ledger commit's tree holds the value it is judged under; `on-demand` disables the clause, which is that value's meaning. |
| 6 | Counter (Rule-10): a state check over the store — every row with a `Y done` holds a trace. | Survives as the weaker path: it would fail today on every row before the preference and on accreted rows and need a legacy list; the transaction clause judges only new records, where they are written, and needs none. |

**Pairwise (Rule-5).** **3–7**: unchanged — the provenance entry of the same disposition is still written in the same
commit; the trace is the play-book's measurement and never transcript text (Rule-7 property 2). **3–2**: unchanged —
the clause fences a clerical record, it ratifies nothing. **3–16**: unchanged — no transition is added or refused; the
clause reads the row's `disposed`, not its state. **3–12**: the clause is code carrying its test (`test_rows`,
`test_package`, `test_land`), as property 1 requires. **3–1**: unchanged — the trace and the row are both under
`<instance>/d-work/`, one zone. **3–6**: no new term; `d-work trace` is already defined. Others unchanged. Coherent,
orthogonal.

Disposition: see ledger #465.

## Amendment — d-work #476 (2026-10-26, child C3 of #473: the evidence block cited by its sha256 and its brief form)
**Claim (plan #473, the Operator's `Y` of 2026-10-26, asking to reduce time and tokens in verification, evidence
collection above all):** the completion reply cites the evidence block by its `evidence-sha256` and its brief form,
as `check --evidence --brief` prints it — one count line, the baseline compared against, the warnings already
standing on that baseline folded per guard, every failing, skipped or other line, and every warning of a kind new
since the baseline (the Operator's `Y` escalating #476, 2026-10-26); the full block, over which the sha256 is computed unchanged, is
stored per checkout and never tracked (`<git common dir>/dyad-evidence/<sha256>.txt`) and shown byte for byte on
request (`check --evidence --show <sha256>`); the Operator may re-run the evidence on the same head and compare.

| # | attack | result |
|---|---|---|
| 1 | A brief block weakens the merge evidence: the Operator no longer reads every line. | Survives, scoped: the sha256 still covers every line, every failing or skipped line and every warning new since `main` are still in the reply, and the full block is one command away; what the Operator verifies — the same head yields the same sha256 — is unchanged. Only what is pasted shrinks. |
| 2 | A stored block can be edited after the fact to match a claimed sha256. | Refuted: the sha256 is recomputed by re-running on the head, never read back from the store; the store is a convenience for reading, not evidence of its own. |
| 3 | The store is per checkout, so another clone cannot show it. | Survives, accepted: the re-run on the same head is the cross-clone check, as before; showing is for the clone that ran it. |
| 4 | Folding standing warnings into counts hides a warning that changed, or a check that silently stopped running. | Refuted, scoped: a warning of a kind not already on `main` is printed in full; a check that stopped running changes the count line; with no baseline found nothing is folded, and a line says so; and the sha256 covers the full block, so any changed line changes it. |

**Pairwise (Rule-5).** **3–2**: the relayed-Done bullet now cites the evidence as Binding does; Binding is unchanged in force. **3–14**: the block's form is property 3's. **3–7**: unchanged — no Operator words are touched; the evidence is the Agent's text. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #476.

## Amendment — d-work #492 (2026-10-27, a read-only answer opens no d-work)
**Claim (plan #492, the Operator's `Y` of 2026-10-27, falsifying "showing the board should not be a ledger record
because it only reads the ledger"):** Scope's "every Operator prompt opens a d-work" gains one exemption — a prompt
whose answer only reads the corpus, writes nothing and asks no question opens none — and its boundary: a reply that
writes, proposes, or carries a `Y/N` line opens its d-work before its question. The test is the reply's form.

| # | attack | result |
|---|---|---|
| 1 | Scope says there are no exemptions. | Confirmed as the text before this amendment: the claim is a Rule change, not a reading of the Rule; it is made here. |
| 2 | Monitoring is no d-work (#438) because a read-only check authorizes nothing and never completes. | Supports the claim: a read answer authorizes nothing either, and completes in the reply. |
| 3 | Cost: a board shown on request (#490) took a row, a provenance record, a trace, two ledger pushes and a Done question. | Supports the claim. |
| 4 | Without a row the prompt's words go unrecorded, since Rule-7 fires on a prompt that opens a d-work. | Survives, conceded: the words of a read request authorize nothing, so no chain of authorization is lost; the transcript still holds them. |
| 5 | A read reply often ends in a proposal (#490 proposed archiving three rows), and #491 shows a `Y` given with no row to land on. | Refutes the bare claim and scopes it: the line is the question, not the read — a reply that asks anything opens its row before the question. |
| 6 | Who classifies "read-only"? The Agent, by inference (modes S and C of the incident index). | Survives, scoped: classified by the reply's form, observable — no write, no proposal, no `Y/N` line. |

**Pairwise (Rule-5).** **3–7**: unchanged in text — Rule-7's trigger is "a prompt that opens or is received on a
d-work", so a read-only answer, opening none, writes no entry; attack 4 states what that concedes. **3–2**: unchanged — a
read-only answer asks nothing, so no ratification event arises; a reply that asks opens a row first, and Binding applies
to its question as before. **3–10**: unchanged — Rule-10 frames proposals; a read-only answer is none. **3–15**: a reply
that opens its row writes its plan file before its question, as Phase 1 requires. **3–16**: unchanged — no state or
transition is added. **3–6**: no new term; `d-work` still reads correctly ("opened by an Operator prompt" names how one
opens, not that every prompt opens one). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #492.

## Amendment — d-work #535 (2026-11-02, Batch disposition: the pending queue recorded in the board store, written ahead)
**Claim (plan #535, the Operator's `Y` of 2026-11-02 on: "if `cos` is a mode, the orchestration needs to be continuous and
seamless during seat-hops."):** the pending queue, and every open row's orchestration in flight, is recorded in the board
store (Rule-16), written before the act it records, so a hop of the session holding it loses nothing and asks the
Operator nothing about state.

| # | attack | result |
|---|---|---|
| B1 | The rows and plans already hold the orchestration. | **Refuted** (plan attack 1): a row says `planned`, never who holds the work, what it waits on, the next act or the question outstanding; the plan's inventory of 2026-11-01/02 found six kinds of item in no store. |
| B2 | "Conversational, not a corpus file" was chosen deliberately (#17): recording the queue costs a commit per change. | **Survives, priced** (plan attack 7): a board write is a ledger-only commit, which runs no suite (Rule-12 property 2); turns already make one to three, and the board adds about one. What #17 bought — no file to drift — is kept by overwriting, never accumulating. |
| B3 | A hop mid-turn loses what the old holder had not yet written. | **Survives with write-ahead** (plan attack 3): the entry precedes the act, so a hop loses at most the reply being composed. |
| B4 | A new holder re-asks or re-derives the Operator's question. | **Survives, procedure** (plan attack 4): the question is stored verbatim with when it was asked; the new holder re-presents it unchanged or reports it pending. |
| B5 | Recording the queue makes it a check, and a wrong entry a failing one. | **Refuted, stated**: the guard checks shape only (Rule-16); whether an entry is true of the work stays inference, as the sentence it replaces said of the queue. |
| B6 | The board is the cos's, so it belongs to the cabinet craft, not a core Rule. | **Survives, scoped**: the queue is Rule-3's own concept and exists under `organization: flat` too, where the one pair's Agent holds the board; the cos is named only as the m4 case. The Guide (§10) carries the hop's practice. |

**Pairwise (Rule-5).** **3–16**: Rule-16 owns the store, its path, keys, guard and its overwrite semantics; Rule-3
owns the queue and the write-ahead conduct, and cites the store. **3–2**: a board write is clerical, ledger-only (Not
ratification), and records no disposition; unchanged. **3–7**: a board entry quotes a question the Agent asked, never
the Operator's words, so it is no provenance record; unchanged. **3–1**: one zone, the agent zone. **3–6**: `board
store`, `write-ahead` and `hop` added, `pending queue` reworded. **3–10**: concise-mode's single reply still carries the
counts; unchanged. **3–12**: no suite for a ledger-only range; unchanged. **3–15**, **3–20**: plans and references
untouched (the board is not a reference kind; the guard resolves its ids itself). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #535.

## Amendment — d-work #536 (2026-11-02, Batch disposition: reports and relays by the inbox)
**Claim (plan #536, the Operator's `Y` of 2026-11-02: "proceed as recommended"):** a seat's report and the cos's relay
travel by the inbox store (Rule-16), addressed by seat and read at every turn start; a message to a session is at most
a doorbell; the inbox carries information, never authority.

| # | attack | result |
|---|---|---|
| I1 | Reading a store at turn start cannot interrupt a busy session (#252 M2). | **Conceded, scoped** (plan attack 1): reports and relays wait for the next turn; interruption stays with the harness's messages, now a doorbell. Write-ahead (#535) means no act waits mid-turn on a report. |
| I2 | An unread report is invisible, so silence reads as consent. | **Refuted** (plan attack 2): the unread count prints at every resume and touch, and a report the board expects shows as the row's `waiting-on seat` past its `since`; nothing is inferred from silence, as this Rule already says of an unanswered counter-prompt. |
| I3 | The inbox becomes a channel for authority. | **Refuted** (plan attack 5): a disposition-shaped body is refused by the guard, and a disposition is read from the row and its provenance record only. |
| I4 | A relay through the inbox paraphrases the Operator. | **Refuted, by the text**: the Operator's words still travel verbatim, citing their provenance entry; the inbox changes the carrier, never the words. |
| I5 | A report forged as another seat's misleads the cos. | **Survives, detection only** (plan attack 4): the commit records who wrote it, and a report carries no authority, so its worst case is a misleading report audit can trace. |

**Pairwise (Rule-5).** **3–16**: Rule-16 owns the inbox store, its keys, its guard and append-only; Rule-3 owns that
reports and relays travel by it. **3–2**: an inbox message is ledger-only and records no disposition; the never-
authority clause keeps Rule-2's events in the ledger. **3–7**: a relayed prompt's verbatim words and their
provenance entry are unchanged; the inbox cites, never stores, them as provenance. **3–6**: `inbox` added. **3–1**:
agent zone. **3–20**: the message's `row` is resolved by its own guard, not a registered reference kind. Others
unchanged. Coherent, orthogonal.

Disposition: see ledger #536.

## Amendment — d-work #555 (2026-11-02, Plan: an execution detail is not a departure)
**Claim (plan #555, the Operator's `Y` of 2026-11-02, on: "I agree that execution order (unless explicitly stated as
requirement) is execution details that is covered in the original mandate."):** a change of order, PR split or
stacking, executing seat within its charter, or tooling route, with the mutation's content unchanged, no such
requirement stated, the same end state and no irreversible or outward intermediate state, is covered by the plan-`Y`,
never asked, and reported at the Done.

| # | attack | result |
|---|---|---|
| X1 | Order can change an outcome (#526: the bundle PR before the evidence fix could not cut). | **Survives with condition 3** (plan attack 1): where an intermediate state is outward or irreversible, order is not detail; #526's cut order fell under it and was rightly asked. |
| X2 | "Same end state" is the Agent's own judgment. | **Survives, priced** (plan attack 2): it is a departure line in the completion evidence, and the Done verifies it; a wrong judgment costs one amend, not an unauthorized outcome, since the content was authorized. |
| X3 | A plan could omit requirements to widen the Agent's latitude. | **Refuted** (plan attack 3): the latitude covers order, split, executing seat and route only, never content; a content change stays a new plan. |
| X4 | Rule-2 Binding: a `Y` binds only to what its question named. | **Refuted** (plan attack 4): the question named the mutation; the order was the plan's narration of how, unless marked a requirement. |
| X5 | "Executing seat within its charter" lets a plan's work move to a seat the Operator did not expect. | **Survives, bounded**: only within the charter that already owns the act (the cabinet's mandates table); a seat outside it is a new plan. |

**Pairwise (Rule-5).** **3–2**: Binding is unchanged; the plan-`Y` binds the mutation, and the execution detail sits
inside what it named. **3–15**: Rule-15 phase 1 states the requirement that removes the latitude; Rule-3 owns what
departs. **3–8**: a destructive host action is excluded by condition 3 and keeps its own counter-prompt. **3–11**: a
release cut or tag is excluded by condition 3. **3–1**: one zone per PR is unchanged; re-splitting never mixes zones.
**3–7**: no provenance change. **3–6**: no new vocabulary row ("execution detail" is the criterion's outcome, defined in
the DMC record and named here). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #555.

## Amendment — d-work #556 (2026-11-02: the automaton executes the merge and the close)
**Claim (plan #556 revisions 1–3, the operator's `Y` of 2026-11-02):** after a done-`Y` is recorded, the merges it
names and the close are clerical execution of a ledger line, so a non-inferring automaton may run them; the record
stays the inferring unit's, and the d-work play-book states the three layers — interaction (the home), orchestration
and execution (a solo), run-book execution (auto) — and that units run run-book steps by name.

| # | attack | result |
|---|---|---|
| 1 | A merge by code is self-ratification moved into a workflow. | **Refuted**: the `Y` is the operator's, recorded before the merge (the Record act); the automaton merges only what the operative entry names, through `dyad merge`, which refuses a moved head, a missing entry or a head already on `main` (Rule-2 Enforcement). It decides nothing. |
| 2 | The three-act order breaks: the automaton could close before it merges. | **Refuted**: it closes only a row whose every named head is an ancestor of `main` (`close-landed`), the same test the fence applies (`rows.landing_problems`); a close it writes is judged by the fence like any other. |
| 3 | The completion reply's evidence no longer covers the merge. | **Survives, scoped**: the reply asks before any merge, as before; the merge evidence is the evidence block on the head the `Y` names, which the automaton does not re-run, and the hosting's CI corroborates on `main` (Rule-14 property 3). |
| 4 | A conflict or a moved head stalls the row silently. | **Refuted**: every refusal is one notice to the home's inbox, and the row keeps its state, so the board and the home see it; resolving it is inference, the home's or a solo's. |
| 5 | With the switch off, the Rule now describes a mechanism that does not run. | **Survives**: the sentence is permissive ("may be executed … while `DYAD_AUTOMATON` is `on`"); off, the acts stay with the agent as before. |
| 6 | The layer table puts orchestration on a solo no charter names. | **Survives, scoped**: the play-book says the home executes that layer until row #557's charter exists; the charter is the operator's `MANDATES.md` change, never accreted (Rule-2 Binding). |

**Pairwise (Rule-5).** **3–2**: Rule-2 Enforcement names the automaton as execution and its refusals; Rule-3 owns when
the merge and the close happen; each cites the other. **3–14**: the merge evidence stays Rule-14 property 3's block,
unchanged. **3–16**: the automaton reads and writes the board and the inbox as any writer does; Rule-16 owns their
shape, unchanged. **3–13**: the play-book's conduct rule — run steps by name, harvest a recurring script into a step by
its own row — is Rule-13 property 1 applied, stated in the play-book, not a Rule. **3–6**: `automaton` used by 3.
**3–1**: agent zone; the workflow is infra zone, in engineer's PR. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #556.

## Amendment — d-work #564 (2026-11-03: corroboration where the merge ran; the scheduled sweep)
This Rule's sentence changes with property 3 of Rule-14; the claim, its attacks and the pairwise statements for every
Rule this d-work touches are recorded once, in `rule-14-system-infrastructure.md`, amendment #564.

Disposition: see ledger #564.


## Amendment — d-work #574 (2026-11-04: the definition of done; the row a play-book the plan runs prescribes)
**Where the sentences land.** Rule-3's own sentences for both claims are not written by this amendment: #585 refactors
Rule-3 and absorbs them (plan #585, R7). This amendment changes Rule-15, Rule-2, Rule-7, the vocabulary and the
play-books, and records the attacks the Rule-3 rewrite carries.

**Claims.** (1) A row is partitioned by the operator's definition of done (DoD): the plan opens with it (Rule-15 phase
1) and the completion evidence opens with it, quoted, and the report that answers it (this Rule, Completion
counter-prompt). (2) A plan that runs a play-book carries the rows that play-book's own steps prescribe (Scope, Plan,
Ledger, Incidents; Rule-2 Binding; Rule-7 property 4 and Enforcement): the incident-hardening play-book's `backlog`
row naming a fence is born `backlog` under that plan-`Y`, entry `Y backlog (mandate #<id>)`, never asked again.

| # | attack | result | survivor |
|---|--------|--------|----------|
| E1 | The play-book alone can make the evidence open with the DoD. | **confirmed: not enough.** A play-book is read by a Rule, never a Rule; the completion evidence is this Rule's list, whose omissions are breaches. | The evidence bullet gains the opening clause; Rule-15 phase 1 gains the plan part; the play-book holds the procedure. |
| E2 | Adding a plan part is free. | **confirmed.** `dyadlib.PLAN_PARTS` drives `agent/plans` warnings over about 570 stored plans and an invariant pins five parts. | The guard part is engineer's PR, after this text, asked only of plans from this landing on. |
| E3 | A DoD costs a question per row. | **survives.** It rides the plan question: the operator's words, or one marked proposed; `Y` accepts, `N` with text amends. | — |
| E4 | A proposed DoD is the agent's text dressed as the operator's. | **survives.** Marked proposed until a plan-`Y`; the operator's own words are quoted only from a `prompt` entry (Rule-7). | — |
| E5 | Accreted rows break one DoD per row. | **survives, scoped.** A child is work inside its parent's DoD, verified through the parent's report; a child the operator would judge on its own terms takes its own DoD and an explicit row (the escalate edge). | — |
| E6 | The agent can decide what the operator can evaluate. | **survives.** It proposes; the operator's amendments correct it, and the amendment count measures the fit. | — |
| E8 | A guard can check the evidence opens with the DoD. | **survives, stated.** The completion reply is chat; inference, as the rest of the evidence list is. | — |
| F1 | A play-book-prescribed row needs no disposition of its own. | **confirmed against the old text** ("a plan that states no mandate scope accretes nothing"), which is what changes. | The play-book's step is the rule, its own count the ceiling; a row the step does not prescribe returns to explicit mode. |
| F2 | This widens a `Y` past what the operator read. | **survives.** The question named the play-book, ratified corpus as legible before the `Y` as a stated scope; Rule-2's never-accretable list is unchanged, so a step that would open one of those still asks. | — |
| F3 | A carried `backlog` row could be worked without the operator. | **survives, unchanged.** Carrying changes only its birth: `backlog → open` still needs the operator's prompt, after which it is explicit with its own pair of `Y`; it carries no `mode: implicit`, and a parent's Done stays askable over `backlog` children. | — |
| F4 | Provenance breaks. | **survives.** Entry 1 is the carrying plan-`Y`'s words noted `mandate #<id>, <date>`; Rule-7's transaction clause names the carried case; property 5's count holds one for one. | — |
| F5 | The verb already does it. | **confirmed: a verb change.** `dwork new --mandate` refuses `--backlog` today. | Engineer's PR admits `--backlog --mandate <id>`; until it lands, a carried row is written by hand to the same form. |
| F6 | Every play-book that opens rows gains the power unseen. | **survives, stated.** Intended; the step's own text decides, and a play-book that wants a question says so (promotion's promise row opens only on a `Y` by its text). | — |

**Pairwise (Rule-5).** **3–2**: Rule-2 owns what a `Y` binds; its mandate clause names the play-book case, the
never-accretable list unchanged; this Rule owns when a row is born. **3–7**: Rule-7 stores the carried row's entry 1 as an
accreted row's; this Rule owns the `disposed` form. **3–15**: Rule-15 owns the plan's parts; this Rule owns the evidence
list. **3–16**: no new state or transition; a carried row is born `backlog`, already in `dyadlib.NEW_STATES`.
**3–1, 4, 5, 6, 8–14, 18–20**: untouched. Coherent, orthogonal.

**Terms (Rule-6).** New: `definition of done` (owner 15, used by 15; Rule-3 joins its `used by` with #585); Rule-15 reads correctly. Changed: `backlog` (used
by 3), `mandate scope` (used by 2 3), `accreted row` (used by 2 3 7 15 16); each Rule in their `used by` still reads
correctly, the carried case being an addition to each definition.

Disposition: see ledger #574.


## Amendment — d-work #585 (2026-11-04: the refactor; absorbs #574 revisions 1–3 and #584)
**Claim.** Rule-3 is rewritten, not amended. It is organised around what opens a row, what a `Y` binds (every act its
question names: merges, accreted and carried rows, play-book-prescribed rows, retirements), the two questions, what is
never carried (Rule-2's list, by pointer), the record of each `Y` and the automaton's execution. The new text
supersedes every earlier version and amendment of Rule-3. Other Rules keep their own concerns and point to Rule-3 where
they restated its machinery. The sentence-by-sentence fate of the old text is the clause map,
`agent-corpus/audits/2026-11-04-rule-3-clause-map.md`.

The attacks are plan #585's R1–R7, #574's E1–E8 and F1–F6 (amendment #574 above), #574 revision 3's G1–G6, and #584's
M1–M5 (`agent-corpus/d-work/plans/574.md`, `584.md`, `585.md`). Their survivors are the text. Beyond them:

| # | attack | result | survivor |
|---|--------|--------|----------|
| X1 | A shorter Rule drops an obligation a guard or test relies on | **refuted by check.** Every string `dyad/tests/test_playbooks.py` asserts of Rule-3 is kept. Every outcome name of the 14 DMCs homed in Rule-3 appears in it. Every vocabulary term used by 3 appears. Every path it cites resolves. Every heading another file cites by name is kept: `Scope` becomes `Scope (what opens a row)`, its prefix unchanged. | — |
| X2 | The retirement form becomes a new ratification event | **survives.** Rule-3 already made the operator's `Y` to it the act that archives. Ratification events now lists it, which states what was true. Rule-2 applies it by reference (G5) with no edit. | — |
| X4 | The definition-of-done step, as #646 writes it, is enough | **confirmed partly.** Tested on 49 backlog rows (`agent-corpus/audits/2026-11-04-backlog-dod.md` section 5, PR #654). It is unclear where a row opened by a bare `Y` keeps the operator's words, and how backlog rows merged under a new DoD leave (they cannot be accreted). It also lacks the route out, the outcomes merged-into-a-new-row and already-delivered, a still-owed check, and a rule for quoting in tracked files. | The play-book's DoD paragraph gains them: the record lookup order, retirement under the new row's `retires`, a still-owed check against `retirement-candidate.jsonld`, and quoting only what may be published. Its `archived` line names the Done route. The step's Rule-3 citations resolve with this text (#585 absorbs #574's sentences). |
| X3 | Code lags the text | **confirmed.** Three statements are true only once engineer's code lands: `dwork new --backlog --mandate` (#574 PR 2), a `Y done (retires …)` entry, and the automaton archiving on close (#574 revision 3). | Until they land, a carried row and a retirement are written by hand in the stated forms. The completion evidence of #585 states which have landed. |

**Pairwise (Rule-5).**
- **3–2:** Rule-2 owns what a `Y` binds and the never-accretable list. Rule-3's "What a `Y` binds" points to it and
  states the two questions. Rule-2's first Binding bullet gains `retires`.
- **3–7:** Rule-7 stores the copied entries (carried, accreted, retired). Rule-3 states when they are written.
- **3–15:** Rule-15 owns the phases and the plan's parts. Its accreted-row bullet points here.
- **3–16:** Rule-16 owns the stores and the transition table. No state or transition changes; `archived` gains the
  Done route.
- **3–1, 4, 5, 6, 8–14, 18–20:** their references to Rule-3's sections still resolve. Coherent and orthogonal.

**Terms (Rule-6).**
- New: `carried` (owner 3, used by 3 7), `doorbell` (owner 3, used by 3).
- Changed: `definition of done` (now used by 3 15), `done-Y` (used by 2 3), `archived` (used by 3 16).
- Each Rule in their `used by` reads correctly.

### Revision 2 (2026-11-04): the operator's definition of done
The operator's words (provenance #585, entry 3): "claims must passes falsification" / "claim should be re-scoped to avoid
exceptions". Every claim of the Rule below carries at least one attack with its result and survivor, and only survivors
stay in the Rule. Every exception clause is removed by narrowing a claim, splitting the excepted case into its own claim,
or moving it to the Rule that owns it. An independent attack pass by audit (audit-e73be78c, B1–B10 and A1–A11) is
answered row by row.
### Rule-3 claim table — d-work #585, plan revision 2

Draft: `RULE-3-d-work.md` in this directory (built on PR #670 head 9bd2481a). The operator's definition of done:
"claims must passes falsification" / "claim should be re-scoped to avoid exceptions".

A claim is a sentence of the revised Rule that asserts what the Rule requires, permits or forbids. Results:
**confirmed** — the attack found the draft sentence false or carrying an exception, and the survivor replaces it;
**refuted** — the attack failed, the sentence stands; **survives, scoped** — it stands within the scope stated.
"Draft" below means PR #670 at 9bd2481a unless it says "v2 draft" (this revision's own earlier text). Audit items
(A1–A11, B1–B10) are from `audit-585.txt`, answered in the last section.

| id | section | claim | attack | result | survivor |
|----|---------|-------|--------|--------|----------|
| C1 | Scope | "Three things open a row: an operator prompt, an operator disposition, and a plan-`Y` whose plan names the row's class" | B1: incident-hardening opens `backlog` fence rows from the agent's own finding (#571's 8 rows), against the draft's "never the agent's own finding" | confirmed (draft) | Third source restated as a plan-`Y` naming the class; the finding reaches a row through it (C10) |
| C2 | Scope | "A prompt: operator text sent alone, text sent with a `Y`, and an amend's text that asks for something else" | B2: amend text asking for the same proposal revised "opens no second row" (Answer grammar), against the draft's "Every operator prompt opens a d-work" | confirmed (draft) | Prompt defined by a partition of operator text (alone / with `Y` / with `N`); the same-proposal amend is received on its row (C17), so no carve-out |
| C3 | Scope | "It opens its d-work when the reply writes, proposes or carries a `Y/N` line, … before that question" | #491: a read's own proposal got a `Y` with no row to land on | refuted (holds) | kept (#492's survivor) |
| C4 | Scope | "The test is the reply's form, never the agent's inference" | does "proposes" need inference? A proposal carries its one `Y/N` (Rule-10), so the form shows it | survives, scoped | kept |
| C5 | Scope | "A new prompt while a d-work is open suspends it and opens another: d-works stack" | under `batch-disposition-mode: on-ignore` a new prompt in place of an answer is the engagement signal; does it still open? Yes: both hold (Conditions bullet 7) | refuted | kept |
| C6 | Scope | "A bare answer … is not a prompt; the rows it opens are the ones its question names" | the draft said a bare answer "opens nothing" beside "the `Y` that admits an intake" opens a row: a bare `Y` to the intake question | confirmed (draft) | survivor as quoted; message-kind DMC's `bare` outcome still names the no-prompt case |
| C7 | Scope | "an accreted row is one the agent opens while executing another, under that row's plan-`Y`; under `accretion: implicit` a plan-`Y` carries the rows its plan names a class for; no disposition of its own; nothing suspended" | #290: 117 of 280 rows accreted, each costing more dispositions than prompt-born rows | refuted | kept, "names a class for" pointing to Plan C37 |
| C8 | Scope | "Under `accretion: explicit` it is asked for like any other row" | preference partition complete? `accretion` has two values | refuted | kept |
| C9 | Scope | "A read-only answer … opens no row and records nothing" | A1: draft's "One exemption: a prompt whose answer only reads …" is an exception to "every prompt opens"; #490 cost a row for a pure read | confirmed (draft form) | split into its own claim, scoped by the reply's form, the complement of C3 |
| C10 | Scope | "A finding of the agent's reaches a row through one of the three above" | B1 (fence rows from findings) | survives, scoped | stated as routing through C1's three sources |
| C11 | Scope | "A d-work a prompt opened terminates on the operator's `Y` to its Done question … A `backlog` row, never started, ends when a `Y` archives it" | v2 draft "A d-work terminates on one event": a `backlog` row retired by the retirement form (`backlog → archived`, Rule-16) ends with no Done | confirmed (v2 draft) | split by scope: prompt-opened d-work vs never-started `backlog` row |
| C12 | Scope | subagents read, search, draft; a delegated subagent reports the sentinel first | this report, drafted by a delegated subagent, opens with the sentinel; Rule-8 Conduct agrees | refuted | kept |
| C13 | Scope | writing a row, counter-prompts, commit, push, PR, merge, reversible/destructive host action "are the main agent's alone"; it reports delegated state each turn | brief of this d-work forbids those acts to the subagent; PREFERENCES `delegation-posture` floor states the same | refuted | kept ("alone" restores the old "Subagents never …") |
| C14 | Answer grammar | `Y` — the disposition is given, binding the acts the question names | Rule-2 Binding "binds only to the PR(s) or action(s) named" | refuted | kept |
| C15 | Answer grammar | "`N`, bare — nothing is authorized; the agent revises" | answer-grammar DMC `bare` | refuted | kept |
| C16 | Answer grammar | amend: entered as a `prompt` entry of the refused d-work's record | Rule-7 trigger "opens or is received on a d-work" | refuted | kept |
| C17 | Answer grammar | same proposal revised → no second row, plan revised in place; something else → own d-work; the `N` authorizes nothing | #290 plan refused 2026-10-14 in the words that became revision 5; amend-scope DMC | refuted | kept ("until" clause restated positively: the revision takes its own `Y`) |
| C18 | Answer grammar | "A `Y` with text is a `Y` plus a prompt" | a `Y` whose text asks to change the plan just approved: the `Y` binds the plan as asked, the text opens a d-work that re-plans | survives, scoped | kept |
| C19 | Answer grammar | "Silence is not consent" | `on-ignore` reads an unanswered question as an engagement signal — a signal for the form, never a `Y` | refuted | kept |
| C20 | Answer grammar | an answer is read by its meaning; row records the token, provenance the words | label-case DMC, #553 | refuted | kept |
| C21 | Answer grammar | "Where two readings lead to different acts the agent asks …; a difference of case or spelling alone leads to one act" | draft "never about spelling alone" was a carve-out on asking | survives, re-scoped | split: ask when readings differ in act; spelling never differs in act |
| C22 | What a `Y` binds | "A `Y` binds exactly the acts its question names …: what the question states and what it cites directly" | B4: binding transitive through citations (plan → play-book → rows) with no depth limit | confirmed (draft) | "directly"; the plan file names each carried class, a play-book step by id |
| C23 | What a `Y` binds | the plan question's plan-`Y` binds the mutation, every PR, every carried row | Rule-2 Binding mandate clause (#290, #574) | refuted | kept |
| C24 | What a `Y` binds | the Done question's done-`Y` verifies, closes accreted, archives retired, ratifies merges exactly | Rule-2 Binding first bullet gains `retires` (#585) | refuted | kept |
| C25 | What a `Y` binds | a batch counter-prompt binds each d-work as its single question would | Rule-2 Binding batch bullet | refuted | kept |
| C26 | What a `Y` binds | "A row or act is carried when another's question names it … so that `Y` binds it with no question of its own" | v2 draft "carried when a question the operator answered names it" made every named act carried; vocabulary `carried` says "without a question of its own" | confirmed (v2 draft) | survivor as quoted, matching the vocabulary |
| C27 | What a `Y` binds | work the plan does not describe, and a row its scope or step does not cover, is a new plan | plan-departure DMC `new plan` | refuted | kept |
| C28 | What a `Y` binds | a plan-`Y` carries no act of these kinds: destructive host action, release, intake, preference value, undescribed mutation | Rule-2's list reads "a release — except under the release gate" | survives, scoped | stated as a scope ("carries no act of these kinds"); the gate case split to C29 |
| C29 | What a `Y` binds | "A release under the release gate is named in its own d-work's Done question, so that done-`Y` binds it as a named act" | Rule-11 gate form `Y/N: Done with #<id> <title> (merges PR #a, releases <tag-a>)?` | refuted | kept: a named act is never carried, so C28 needs no carve-out |
| C30 | Plan | "The agent's first substantive reply to a prompt that opens a d-work is a plan …" | v2 draft "to a prompt": a read-only answer (C9) is a reply to a prompt with no plan | confirmed (v2 draft) | scoped to prompts that open a d-work |
| C31 | Plan | the definition of done is the operator's words or one marked proposed; one row per definition of done | #574 X4: 49 backlog rows; where a bare-`Y` row keeps the operator's words | survives, scoped | kept; the lookup order is the play-book's |
| C32 | Plan | the plan-`Y` authorizes the mutation and binds every PR to the plan | prs.py plan gate requires `Y plan` | refuted | kept |
| C33 | Plan | departing work is a new plan; until a `Y` nothing is authorized | draft "any other answer leaves …" was a complement clause | survives, re-scoped | "until a `Y`" |
| C34 | Plan | "Every plan is asked, a one-line plan included; a row the plan-`Y` carries was named in that question and is asked no second time" | A2: "No exemptions … and a row … is never asked a second time" states one | confirmed (draft form) | every question is asked once; the carried row was asked in the plan question |
| C35 | Plan | an execution detail (order, split, unit, tooling) with content and end state unchanged, none stated as requirement, no irreversible or world-reaching intermediate state, is covered and reported | #555; #553 rev 3 and #532 rev 6 cost a question for an order change | refuted | kept |
| C36 | Plan | a change meeting fewer than all of these conditions is a new plan | draft "if any condition fails" | refuted | kept, restated |
| C37 | Plan | a plan carries rows from two sources, each stated in the plan file: (a) mandate scope, (b) a play-book step cited by id | A3: "accretes nothing beyond the rows a play-book … prescribes" | confirmed (draft form) | split into two sources, no "beyond" |
| C38 | Plan | rule and ceiling are the operator's to read before the plan-`Y`; the play-book count stated in the plan as a number; rows countable only in execution are born `backlog`, each listed in the completion evidence | B3: #571's 8 fence rows were unknown at plan-`Y` time, so "the play-book's own count" was not readable | confirmed (draft) | survivor as quoted (a strengthening: no row is carried open past what the operator read) |
| C39 | Plan | a play-book that wants a question for a row says so in its step | incident-hardening step for fence rows | refuted | kept |
| C40 | Plan | a plan stating neither source carries no row; a row outside the rule or past the ceiling is a new plan | escalate edge (countersign model Part II §4) | refuted | kept |
| C41 | Plan | a carried row is born `open` (done riding this done-`Y`) or `backlog` (explicit once prompted) | #574 carried `backlog` rows, Rule-7 property 4 | refuted | kept |
| C42 | Plan | craft play-book: no criterion fires → new craft instance; one fires → advise a new dyad system | A4: "unless one of its criteria fires" | survives, re-scoped | partition by the criteria; test string `craft-instantiation-criteria` kept |
| C43 | Completion | done-`Y` asked on the output in the PR(s), before merge, "so `main` never carries a PR's output before its done-`Y`" | B5: plan files, inbox reports and events land on `main` by ledger-only and events-only commits before any done-`Y` (#571, #591 plan files) | confirmed (draft) | scoped to a PR's output |
| C44 | Completion | the Done question is the last line of the reply that believes the d-work is done | Rule-10 one `Y/N` last | refuted | kept |
| C45 | Completion | the form's one parenthetical, in order; the `Y` binds the sets exactly as listed; leaving a row out is a breach | #290: the delivered set, never the promised one | refuted | kept ("present only when" → "present when") |
| C46 | Completion | a row named under `retires` is `backlog` or `done`; an `open`/`planned` superseded row closes by its own Done first | Rule-16 table: archived only from `done` or `backlog` | refuted | kept |
| C47 | Completion | the E8 evidence list, in order; an omission is a breach | #465 six Done records lacked traces unseen | refuted | kept |
| C48 | Completion | under `dwork-trace` `always` the evidence cites the trace; under `on-demand` when prompted; preview printed, file written by the commit that records the `Y` | trace-in-evidence DMC; #213, #215 | refuted | kept |
| C49 | Completion | "A mandate close rides the mandate's own trace" | an accreted row has no Done question of its own, so no trace of its own exists to cite | refuted | kept |
| C50 | Completion | "The reply that asks does not merge" | #47, #58, #67: merges before the `Y` | refuted | kept |
| C51 | Completion | "A done-`Y` that names no merge has nothing in flight: one ledger commit holds its entries and the trace, and sets `done` at once" | by meaning (audit): "recorded done at once" was an exception to Record/Merge/Close | confirmed (draft form) | split: Record/Merge/Close is scoped to a done-`Y` that names a merge (C52) |
| C52 | Completion | Record, merge, Close, in order, for a done-`Y` naming a merge; Close once every head the operative entry names is on `main` | #202: twelve INCIDENTS.md rows, eleven instances, of `done` set before the merge | refuted | kept |
| C53 | Completion | a merge before the `Y` is self-ratification, an incident; `done` before the heads land is the converse breach, refused by the fence | `rows.done_order_problems`, `rows.landing_problems` | refuted | kept |
| C54 | Completion | while a merge owes a push the row stays `open` or `planned` — the states the plan gate admits that have an edge to `done` — its plan-`Y` carrying the push | by meaning (audit): "never `blocked`" | survives, re-scoped | stated by the property that selects the two states |
| C55 | Completion | a resolution that changes a head voids the `Y`; asked again, a further entry | Rule-2 Binding "only if their heads are unchanged"; merge verb refuses a moved head (#532) | refuted | kept |
| C56 | Completion | while `DYAD_AUTOMATON` is `on` the automaton executes merge and Close from the recorded entry; refusals go to the home's inbox; it decides nothing | #556; Rule-2 Enforcement automaton bullet | refuted | kept; refusal list names `archived` explicitly (was "neither `backlog` nor `done`") |
| C57 | Completion | while it is `off` the agent executes both by hand | partition of the variable | refuted | kept |
| C58 | Completion | a relayed Done presents evidence per `relay-form`, the unit's question last, the `Y` binding what the unit asked | #423, #424 | refuted | kept |
| C59 | Batch | the three modes; the pending queue; both counts every reply while non-empty; `on-ignore` lapses when empty | PREFERENCES `batch-disposition-mode` | refuted | kept |
| C60 | Batch | batch forms replace single forms, one kind per question; a `Y` binds the named set; every answer short of `Y` binds none | Rule-2 batch bullet; draft "anything else, none of it" | survives, re-scoped | "short of `Y`" |
| C61 | Batch | each row's entry names the whole set; one provenance entry in every named record | Rule-7 property 5 count | refuted | kept |
| C62 | Batch | mandate form: two questions whatever the set's size; a carried row, a release question and the retirement form never enter the queue | Rule-11 release batch is its own form | refuted | kept, restated without "nor" |
| C63 | Batch | the queue's counts and last question live in the board store; a hop loses none | #535 | refuted | kept |
| C64 | Batch | the board is written write-ahead; its guard checks shape | board.py | refuted | kept ("shape only" → "shape") |
| C65 | Batch | the inbox carries information, never authority; relays travel verbatim, citing their provenance entry | inbox.py refuses a disposition-shaped body (Rule-16) | refuted | kept |
| C66 | Batch | a message to a session is at most a doorbell; the five routes | B10: no live session → no doorbell target | survives, scoped | actionable post rings when a direct message reaches the unit's session; a unit with no live session polls |
| C67 | Ledger | states move along Rule-16's table | `dyadlib.TRANSITIONS`, fence | refuted | kept |
| C68 | Ledger | `blocked` → `open` "when that one is terminal (`done` or `archived`)" | B7: an archived blocker never becomes `done` | confirmed (draft) | survivor as quoted |
| C69 | Ledger | `backlog`: opened by disposition or carried; `open` when prompted, `archived` when retired | Rule-16 `backlog → open, archived` | refuted | kept |
| C70 | Ledger | `done` = Done `Y` and every named merge landed; interval warned once per row | `rows.done_recorded_not_closed` | refuted | kept |
| C71 | Ledger | `archived` from `done` or `backlog`; terminal; the two question forms; a `Y` archives exactly the named rows; the agent archives on an operator `Y` alone | #290: 0 archives in 280 rows; draft "anything else none" and "never archives on its own judgment" | survives, re-scoped | "every answer short of `Y` archives none"; "on an operator `Y` alone" |
| C72 | Ledger | the parent's question is asked only when every child is terminal, `blocked`, `backlog` or holding its recorded done-`Y` | B6: an `archived` child blocked the parent by the draft's list | confirmed (draft) | `archived` added as terminal |
| C73 | Ledger | the parent completes on its own done-`Y`, evidence naming each child's state | #290: 23 `backlog` children | refuted | kept |
| C74 | Ledger | "For every row opened from 2026-09-12 #46 on, `disposed` records every disposition …" | A5: "rows before … are not backfilled" | survives, re-scoped | scope stated first |
| C75 | Ledger | carried rows' entry forms and the copied words with their notes | Rule-7 property 4 (#290, #574, #585) | refuted | kept |
| C76 | Ledger | `mode` names a row's Done route: `implicit` for a row whose done rides another's done-`Y`; `explicit` or absent for a row its own Done closes | A6: "a carried `backlog` row carries none" | confirmed (draft form) | survivor as quoted; the carried `backlog` row falls in the second class |
| C77 | Ledger | ledger-only and events-only commits are clerical and go direct to `main` | Rule-2 Not ratification; `rows.py` | refuted | kept |
| C78 | Ledger | a commit touching both is **neither** and goes by PR, as a commit that **touches anything else** does | Rule-1 one zone per commit | survives, scoped | kept: two named classes, each a claim; "touches anything else" is the direct-commit-class DMC outcome name, the complement class, not a carve-out |
| C79 | Ledger | monitoring is no d-work, opens no row; its writes are its events and, for the sweep, one inbox notice | B8: the draft said "writes only its events" beside an inbox notice | confirmed (draft) | survivor as quoted |
| C80 | Ledger | session start: report rows not `done`, `merge-disposition`, sentinel; frame absent → say so and stop | E1 | refuted | kept |
| C81 | Ledger | under `flat` a session reads the whole ledger; under `m4` its unit's board | A7: "instead of the whole ledger" | survives, re-scoped | partition by `organization` |
| C82 | Ledger | it touches its presence file, reads every other session's, reports a bearing overlap | #185 near-miss | refuted | kept |
| C83 | Ledger | PR bodies and branch commit messages cite `d-work #<id>` as a claim of work; other rows as plain `#<id>` | #23 | refuted | kept |
| C84 | Ledger | the plan gate requires `open`/`planned`/`blocked` with `Y plan`, and refuses every commit citing a terminal row | plan-gate DMC `refuses` | refuted | kept |
| C85 | Mechanisms | Rule-3 owns `rows.py` and `prs.py`, run on the kernel-only path and by corroboration; guard change agent-zone PR, wrapper infra-zone | Rule-2 Enforcement cites rows.py as Rule-3's | refuted | kept |
| C86 | Mechanisms | the main fence admits a ledger-only or events-only direct commit and fails every direct commit of another class | direct-commit-class DMC | refuted | kept (was "neither … nor") |
| C87 | Mechanisms | Done order on the three paths; heads judged on what this clone resolves, an unresolvable sha a printed line stating no judgement | A8: "never failing" | survives, re-scoped | the judgement's domain is stated (#321's cross-clone denial of service) |
| C88 | Mechanisms | under `dwork-trace: always` a `Y done` commit carries or finds the trace of each d-work its Done question named; an accreted row's mandate close needs the mandate's | A9: "a mandate close exempt" | survives, re-scoped | scoped to what the question named; "mandate close" (trace-in-evidence DMC) kept |
| C89 | Mechanisms | `dwork state`/`dwork batch` refuse an entry lacking its trace before the first write | `package.py trace_refusal`, #465 | refuted | kept |
| C90 | Mechanisms | the plan gate judges ranges that claim a d-work; an all-ledger-only or all-events-only range claims none and is skipped; a mix claims one and is gated | A10, A11: "is exempt", "the exemption rests on" | survives, re-scoped | scope of the gate stated; plan-gate DMC outcomes kept |
| C91 | Mechanisms | since the skip rests on `main` admitting the same commits, the fence judges each commit of such a branch as on `main` | #191: uncited ledger commits pushed around the hook | refuted | kept |
| C92 | Intake | within one dyad system an operator prompt relayed verbatim by another unit is a relayed prompt, a prompt | B9: the draft's "A message from another agent opens no d-work" forbade in-system relays the vocabulary admits | confirmed (draft) | survivor as quoted; the bound applies to messages with no relayed prompt (C93) |
| C93 | Intake | a message carrying no relayed prompt opens no d-work; an intake is surfaced as carried; the operator's `Y` opens it with `refs` `<system>-<id>` | #34: three intakes in two days | refuted | kept |
| C94 | Intake | a defect is an observation with evidence, never a verdict or required fix; first entry the operator's `Y` | intake-shape DMC | refuted | kept |
| C95 | Intake | an enhancement carries its operator's verbatim prompt or its provenance; an agent's own idea is a proposal for its own operator | #34 | refuted | kept ("only with" → "carrying") |
| C96 | Intake | a message of neither shape is returned to the sender and reported as received, not as work | draft "Anything else is returned" | survives, re-scoped | "neither shape" |
| C97 | Intake | the shapes bound what an agent's message may bring; an operator prompt on the matter opens a row as every prompt does | draft "The operator may still open a row …" functioned as a carve-out on the Intake bound | survives, re-scoped | two claims with two scopes |
| C98 | Incidents | incident definition; reported where it occurred or in the completion reply; recorded as a falsification attack when it falsifies a Rule or mechanism, as an INCIDENTS.md row when it falsifies neither | incident DMC, incident-record-home DMC | refuted | kept ("otherwise" → "when it falsifies neither") |
| C99 | Incidents | a changed plan takes a fresh plan-`Y` before further mutation | E9 | refuted | kept |
| C100 | Incidents | under `concise-mode: on` the record is written before the single reply | #113 | refuted | kept |
| C101 | Incidents | the hardening play-book closes each failure mode by a fence, a carried `backlog` row, or a recorded impossibility; on an ungrown log its one act is re-testing | draft "only re-tests"; B3 applies to the carried rows (C38) | survives, re-scoped | as quoted |
| C102 | Ratification events | `Y` to a plan, to a Done, to the retirement form are ratification events | Rule-2 G5: applied by reference, no edit | refuted | kept |

Tally: 102 claims, each with at least one attack. Confirmed 18 (the attack found the PR #670 or v2-draft sentence false
or carrying an exception; the survivor is the Rule's text): C1, C2, C6, C9, C11, C22, C26, C30, C34, C37, C38, C43, C51,
C68, C72, C76, C79, C92. Survives, scoped or re-scoped 21: C4, C10, C18, C21, C28, C31, C33, C42, C54, C60, C66, C71, C74, C78, C81, C87, C88, C90, C96, C97, C101. Refuted (the attack failed; the
sentence stands) 63. Every claim in the Rule has a survivor, and the survivor is the Rule's text.

#### Not claims (pointers)
- Boundaries, all six bullets: ownership pointers to Rules 2, 1, 15, 16, 7, 8, 11, 10 and the d-work play-book.
- Conditions, all seven bullets: triggers (when the Rule applies), checked for count by Rule-4.
- Scope's terms paragraph: definitions adopted from the countersign model and the vocabulary (Rule-6).
- "the countersign model's answer grammar" (Answer grammar opening), `dyad/dmc/label-case.jsonld`, the plan-departure
  and message-route DMC paths: citations.
- What a `Y` binds: "(Rule-2, Binding of approval)" and the pointer to Rule-2's list.
- Ledger: "Its states are defined in the vocabulary (Rule-6)"; the Operating Guide path; Rule-16 Presence pointers.
- Mechanisms: "Rule-2 cites `rows.py` by name and does not own it"; the events guard is the sysadmin craft's; the
  incident log's check stays a script until #170; `traces.py` checks the trace store.
- Provenance and `Set:`.

#### Exception count
Command (run from the scratchpad; `check.py` in this directory does the same and more):

```
P='\b(except|excepted|unless|exemption|exempt|but not|other than|save)\b'
grep -oiE "$P" main-rule3.md | wc -l                # main (git show origin/main:dyad/rules/RULE-3-d-work.md)
grep -oiE "$P" r585v2/RULE-3-d-work.md | wc -l      # this draft
python3 r585v2/check.py r585v2/RULE-3-d-work.md --main main-rule3.md
```

| text | brief regex, whole file | brief regex, above Provenance | audit regex, above Provenance | inflected forms (audit regex plus plurals and verb forms), whole file |
|------|----|----|----|----|
| main's Rule-3 (`origin/main` a1de842f) | 7 | 5 | 7 | 11 |
| PR #670 head 9bd2481a | 5 | 5 | 10 | 11 |
| this draft | **0** | **0** | **0** | **0** |

The audit reported 11 on both main and #670; the inflected column reproduces that 11 (its "No exemptions" matches only
with the plural). Manual scan for "only … not": no line of this draft holds the construction; `check.py` lists every
`only` line (none above Provenance asserts an exclusion: "asked only when" is the parent-askable DMC outcome, a
condition, not a carve-out). Manual scan for exception-like phrases (`anything else`, `every other`, `beyond`,
`otherwise`): two hits, both kept and judged in C78 and C82 ("reads every other session's" is a scope, all sessions
but its own, that names no carve-out of a rule).

#### Exceptions removed
| old phrase (PR #670 head) | move | new text |
|---|---|---|
| "One exemption: a prompt whose answer only reads the corpus … opens none" | split | C9, its own claim scoped by the reply's form |
| "Every operator prompt opens a d-work" (carved by amend and read-only) | narrow | C2/C3: partition of operator text, opening scoped by the reply's form |
| "and never the agent's own finding" | narrow | C1, C10 |
| "never about spelling alone" | split | C21 |
| "binds every act its question names and nothing else" / "nothing it does not" (Intent) | narrow | "binds exactly the acts its question names", "directly" (C22) |
| "A carried act was named …, or it is not carried: anything the plan does not describe …" | split | C26, C27 |
| "Never carried … a release outside the release gate" | split + scope | C28 (positive list), C29 (the gate's release is a named act); Rule-2's own "except" noted for Rule-2 |
| "any other answer leaves the d-work open" | narrow | "until a `Y`" (C33) |
| "No exemptions: a plan may be one line … never asked a second time" | narrow | C34 |
| "if any condition fails it is a new plan" | narrow | C36 |
| "accretes nothing beyond the rows a play-book it runs prescribes" | split | C37 (two sources) |
| "a new craft instance unless one of its criteria fires" | narrow (partition) | C42 |
| "each clause present only when it names something" | narrow | "present when" (C45) |
| "under `on-demand` only when the operator prompted" | narrow | "cites one when the operator prompted for one" (C48) |
| "A done-`Y` that names no merge is recorded `done` at once" (by meaning) | split | C51; Record/Merge/Close scoped to a named merge (C52) |
| "(never `blocked`, which has no edge to `done`)" (by meaning) | narrow | C54 |
| "a retired row that is neither `backlog` nor `done`" | narrow | listed states (C56) |
| "With it off" | kept as a partition | C57 |
| "anything else, none of it" (batch) | narrow | "every answer short of `Y` binds none" (C60) |
| "Beside them, never one of them … nor do a release question or the retirement form" | narrow | C62 |
| "The queue is recorded, not conversational"; "checks shape only" | narrow | C63, C64 |
| "a self-addressed post needs none" / polling as the only fallback | narrow | C66 |
| "from `done` or `backlog` only"; "anything else none"; "never archives on its own judgment" | narrow | C71 |
| "rows before 2026-09-12 #46 are not backfilled" | narrow | C74 |
| "a carried `backlog` row carries none" | narrow | C76 |
| "writes only its events" | narrow | C79 |
| "reads its unit's board instead of the whole ledger" | split by `organization` | C81 |
| "fails a direct commit … that is neither ledger-only nor events-only" | narrow | C86 |
| "an unresolvable sha printing one line, never failing" | narrow | C87 |
| "a mandate close exempt" | narrow | C88 |
| "claims no d-work and is exempt"; "Since the exemption rests on …" | narrow | C90, C91 |
| "A message from another agent opens no d-work" | split | C92 (relayed prompt), C93 |
| "an enhancement, only with its operator behind it" | narrow | C95 |
| "Anything else is returned to the sender" | narrow | C96 |
| "The operator may still open a row by prompting" | split | C97 |
| "otherwise as a row of INCIDENTS.md" | narrow | C98 |
| "it only re-tests the fences already closed" | narrow | C101 |
| "never one of Rule-2's never-accretable acts" in vocabulary `carried`; Rule-2 "except under the release gate" | move to Rule-2 / vocabulary | pointer only here (C28); the wording change is listed in notes.md |

#### Audit pass answered
| item | fix, or the reason it stands | claim |
|------|------------------------------|-------|
| A1 One exemption (read-only) | split: read-only answer is its own claim; opening scoped by the reply's form | C3, C9 |
| A2 No exemptions … never asked a second time | every plan asked once; the carried row was asked in the plan question | C34 |
| A3 nothing beyond the play-book rows | two carrying sources, each its own claim | C37 |
| A4 unless a criterion fires | partition by the criteria | C42 |
| A5 not backfilled | scope stated first: rows opened from #46 on | C74 |
| A6 carried backlog row carries none | `mode` is the row's Done route; the `backlog` row is in the own-Done class | C76 |
| A7 instead of the whole ledger | partition by `organization` (`flat` ledger, `m4` board) | C81 |
| A8 never failing | the fence's judgement is scoped to resolvable heads; an unresolvable one is a stated non-judgement | C87 |
| A9 mandate close exempt | the trace needed is that of each d-work the Done question named; the mandate close needs the mandate's | C88 |
| A10 range is exempt | the gate judges ranges that claim a d-work; a clerical range claims none | C90 |
| A11 exemption rests on main | gone with A10 ("the skip rests on") | C91 |
| by meaning: no-merge `done` at once | split; Record/Merge/Close scoped to a done-`Y` naming a merge | C51, C52 |
| by meaning: never `blocked` | stated by the property: the gate-admitted states with an edge to `done` | C54 |
| B1 never the agent's own finding | third source is a plan-`Y` naming the class; findings route through the three | C1, C10 |
| B2 every prompt opens a d-work | partition of operator text; the same-proposal amend is received on its row | C2, C17 |
| B3 play-book ceiling unreadable | the count is stated in the plan as a number; rows countable only in execution are born `backlog` and listed in the evidence (open question 1 in notes.md) | C38 |
| B4 transitive citation | "cites directly"; a play-book step cited by id | C22, C37 |
| B5 main never carries unverified output | scoped to a PR's output | C43 |
| B6 archived child missing | terminal (`done` or `archived`) added | C72 |
| B7 blocked on an archived row | `open` again when the blocker is terminal | C68 |
| B8 writes only its events | its writes are its events and the sweep's one inbox notice | C79 |
| B9 in-system relays | a relayed prompt within one system is a prompt; the intake bound is scoped to messages with none | C92, C93 |
| B10 doorbell with no live session | the doorbell is scoped to a unit whose session a direct message reaches; one with no live session polls | C66 |


### Revision 2, audit's re-attack answered (audit-e73be78c on head 01141148)
Exceptions: 0, confirmed. Remaining refutations, each fixed in the Rule:

| item | refutation | fix |
|---|---|---|
| R1 | A play-book step counted only in execution has no ceiling to refuse, so carriage is unbounded. | The plan states a number for every play-book step, an upper bound where the count is known only in execution; a row past it is a new plan. Rows born `backlog` and listed after the fact are dropped. This closes counsel's open point 1. |
| R2 | Plan question, plan file, play-book step is two hops, not "directly". | The plan file states the step's class in words and its number; the step id is only a pointer, so the question cites what binds directly. |
| R3 | `ledger-pr-merge: agent` merges a ledger-only PR with no done-`Y`. | Scoped to a PR holding a path outside `agent-corpus/d-work/`. |
| R4 | A Done with `retires` and no merge had no archive act. | The no-merge commit archives each retired row it names. |
| R5 | #571 and #591 carry `mode: implicit` and closed on their own done-`Y`. | `mode` names how a row was opened (born under another row's plan-`Y`), not which Done closes it; this matches Rule-16's never-lost field. |
| R6 | A relay of the home's instruction about an open row is neither shape, so it would be returned. | Intake judges only a message proposing work no row holds; a message about an open row is information. |
| R7 | "case or spelling alone" is overbroad, since `Y` and `N` differ in spelling. | "The listed variants of one answer lead to one act" (`label-case.jsonld`'s table). |

### Revision 2, audit's third pass answered (audit-e73be78c on head d979e5d7)
R1–R4, R6 and R7 were confirmed answered; exceptions 0. One item remained:

| item | refutation | fix |
|---|---|---|
| R8 | The `mode` fix (R5) was half done. Plan's carried-row bullet still said an open carried row's done rides this done-`Y`, and the vocabulary's `accreted row`, `implicit mode` and `mode` still stated a Done route. #571 and #591 refute this: both were born open under #570 and closed on their own done-`Y`. | The carried-row bullet now says its Done is the question its plan names, this d-work's done-`Y` or its own. `mode` names how a row was opened: `implicit` for an accreted row born `open`, `explicit` or absent for every other row. The vocabulary rows `accreted row`, `mode`, `explicit mode` and `implicit mode` now say how a row is born, never which Done closes it. |

**Terms (Rule-6).** These terms changed. For each, the Rules listed in its `used by` column were re-read and still read correctly:

| term | `used by` |
|---|---|
| `accreted row` | 2, 3, 7, 15, 16 |
| `mode` | 3, 16 |
| `explicit mode` | 2, 3 |
| `implicit mode` | 3 |

Rule-7 property 4's mandate close and Rule-16's never-lost field still hold, since they state what is written when a mandate closes a row, not that one must.

### Revision 2, audit's fourth pass answered (audit-e73be78c on head 374a6360)
Exceptions 0; R8 confirmed answered. Two vocabulary divergences fixed (the vocabulary alone changes):

| item | refutation | fix |
|---|---|---|
| R9 | The vocabulary's `implicit` ("born under another row's plan-`Y`") covered a carried `backlog` row, which the Rule calls explicit. #576–#583 carry no mode line. | `mode`: `implicit` is an accreted row born `open` under another row's plan-`Y`; `explicit` is every other row. `explicit mode` says the same, naming a carried `backlog` row. |
| R10 | `accreted row` said "carrying no disposition of its own". #571 and #591 each hold their own `Y done`. | It now says "asking no plan question of its own". |

**Terms (Rule-6).** `mode` is used by 3 and 16, `explicit mode` by 2 and 3, and `accreted row` by 2, 3, 7, 15 and 16. Each Rule re-read and found to read correctly. The Rules' wording on the never-accretable list, and Rule-7 property 4's copied mandate entry, are unaffected.

### Revision 2, audit's fifth pass answered (audit-e73be78c on head da681201)
The Rule passes; R9 and R10 are confirmed. One vocabulary residue:

| item | refutation | fix |
|---|---|---|
| R11 | `accreted row` covered "one a play-book … prescribes", which includes the play-book's fence rows born `backlog`, while also calling every accreted row born `open`. `mode` therefore read those rows two ways. | `accreted row` is a row born `open` under the row's plan-`Y`, from its mandate scope or a play-book step that prescribes `open` rows. A carried `backlog` row is outside the term, as Rule-3 and `mode` already treat it. |

**Terms (Rule-6).** `accreted row` is used by 2, 3, 7, 15 and 16; each Rule was re-read. Rule-2's mandate clause binds the class of row a play-book step prescribes, which still covers the carried `backlog` row. Rule-7 property 4 copies that row's entry in its own sentence. Rule-15's accreted-row bullet concerns rows with no plan file, and Rule-16's plan-less row bullet concerns open rows. All read correctly.

### Rule-3's Provenance section before #585 (history, moved here verbatim)
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-3-d-work.md`. Batch
disposition added 2026-09-15 (d-work #17): a queued batch counter-prompt over several d-works, engaged
by an ignored counter-prompt or the `always` preference; see
`../falsification/rules/rules-2-3-batch-disposition.md`. Intake added 2026-09-16 (d-work #34):
three intakes from peer sessions in two days — one carrying its operator's plan-`Y`, one a defect
with evidence, one an agent's own proposal — showed Scope had no clause for a message that is not
an operator prompt; see `../falsification/rules/rule-3-d-work.md`, amendment #34. `archived` state added 2026-09-16 (d-work #37): a terminal step after `done`, by operator disposition; see the same record, amendment #37. Completion clause gains the merge-sequence bullet 2026-09-18 (d-work #68): three merges run before their done-`Y` in one session; see the same record, amendment #68. Boundaries and Batch disposition reworded 2026-09-21 (d-work #106): release's one-per-question rule rests on Rule-11's own "publishes to the world" reason, not Rule-8 destructiveness, and gains its own narrower batch form (Rule-11); destructive stays unconditional; see the same record, amendment #106. Incidents gains the
`concise-mode` bullet 2026-09-22 (d-work #113): under one reply per prompt the record precedes the
reply; see the same record, amendment #113. Incidents gains the periodic-exercise bullet
2026-09-23 (d-work #137): the grouping-and-mitigation exercise run by hand in #116, #128 and #135
becomes a play-book Rule-3 reads, parameterized by the ledger it hardens and idempotent on one
that has not grown; see the same record, amendment #137. Ledger and Mechanisms gain the plan
gate's ledger-only exemption 2026-09-29 (d-work #191): the gate refused a clerical range, which
pushed ledger commits around the hook and past every other guard; see the same record, amendment
#191. Completion counter-prompt gains the d-work trace bullet 2026-10-05 (d-work #213): the
per-d-work performance measurement done by hand three times (#204, #212) becomes a play-book whose
trace the completion evidence cites, previewed in the completion reply and stored by the Done ledger
commit (plan revision 2), as the preference `dwork-trace` reads (revision 3, #215); see the same
record, amendment #213. Mechanisms gains the trace guard 2026-10-06 (d-work #227): the store's check
ran only inside Rule-12's suite, which a guard-only push skips (#217); see the same record, amendment #227.
Scope, Plan, Ledger, Completion counter-prompt and Batch disposition gain accretion under a mandate,
and Answer grammar is added, 2026-10-14 (d-work #290): 117 of this instance's 280 rows had been
accreted, and the ones actually worked cost the operator *more* than prompt-born rows — mean 2.65
disposed entries against 2.15, with not one closing on a single disposition except #162–#165, the
four handled as a mandate under #199; meanwhile `archived` had been used 0 times in 280 rows, 75
rows sat in `backlog` at a median age of 21 days, and the transition table gave `backlog` one
successor, so the one parent ever gated on `backlog` children could not be asked its Done question
at all. The vocabulary is the countersign model's (then the Tended craft countersign, since #381
`dyad/playbooks/countersign-model.md`) — mandate, implicit mode, escalate edge, amend — adopted rather
than coined (Rule-13 property 1), and `amend` is the first of the four refactors that model's Part II
§7 lists as owed by this system. See the same record, amendment #290. Completion counter-prompt, Ledger and Mechanisms gain the three-act Done order 2026-10-15 (d-work
#202): recording the done-`Y` set the row `done`, `done` is terminal, and the plan gate refuses every
commit citing a terminal row, so a ratified merge that still needed one push — a rebase onto a moved
`main`, a conflict resolved, the second PR of a sequenced set — had no admissible sequence at all.
Twelve rows of `agent-corpus/audits/INCIDENTS.md` between 2026-09-30 and 2026-10-15 are that one
mechanism — eleven distinct instances, two of them recorded as one event's two rows, four recovery rows were paid for it, and 164 rows' `disposed` claims a merge that nothing
reads — five of those claims are known false. The record of the `Y` is now the `disposed` entry and
its provenance entry, which still precede the merge; the state follows it. See the same record,
amendment #202. Ledger gains the d-work play-book 2026-10-15 (d-work #309): the lifecycle was spread over
five Rules, two play-books and the CLI help, and the transition table named no inputs — a successor relation,
not a machine; the input alphabet is now `dyadlib.INPUTS` with its invariants, and the play-book's tables are
pinned to it and to the guards; see the same record, amendment #309. Scope and Answer grammar cite the countersign
model by its core path, and Scope names the delegate edge and the mode lifecycle beside the escalate edge it already
named, 2026-10-22 (d-work #381, child C3 of #369): the countersign craft is retired and its model carried by the core
as a play-book; see the same record, amendment #381. Ledger's session-start bullet gains
the organization sentence 2026-10-22 (d-work #379, #369 C7): under `m4` a session reads a board, not the
whole ledger, and the Guide that says how is the organization craft's; see the same record, amendment #379. Ledger's
session-start bullet names the cos and a secretary, and the Guide's path the cabinet craft, 2026-10-25 (d-work #419,
child C2 of #417): the organization craft is renamed `cabinet` and its role terms cos and secretary; see the same
record, amendment #419. Completion counter-prompt gains the relayed-Done sentence 2026-10-25
(d-work #424): a seat's Done question reached the operator in the seat's own shape (#423), while what the operator
reads from the cos is the matter at the operator's altitude; the form is the preference `relay-form`, the
evidence block and the question stay the seat's; see the same record, amendment #424. Ledger
and Mechanisms gain the events-only commit 2026-10-25 (d-work #438): a standing health check's
events needed an `open` row with a `Y plan`, a PR and the full suite, the row behind them (#431) was
`done` and refused by the plan gate, and the events held uncommitted blocked the seat's own ledger
pushes; a standing row would be a d-work that never completes and authorizes no mutation, so
monitoring is stated to be no d-work and its events clerical, as the ledger's are; see the same
record, amendment #438. Mechanisms names `.github/workflows/dyad-package.yml` and its step in place of `dyad-d-work.yml` 2026-10-26 (d-work #477, C4
of #473): the four guard wrappers became steps of one CI job, same guards, same triggers, still detecting; see the same
record, amendment #477. Mechanisms gains the fence's trace clause 2026-10-26 (d-work
#465): the completion clause said the Done record commit carries the trace, and nothing checked it; six Done records
(#455–#460) carried none, because a refused `dwork trace` went unseen; see the same record, amendment #465. Completion's relayed-Done bullet cites the seat's evidence as
Rule-2's Binding does, by its sha256 and its brief form, 2026-10-26 (d-work #476, child C3 of #473); see the same
record, amendment #476. Scope gains the read-only answer
2026-10-27 (d-work #492): a board shown on request had cost a row, a provenance record, a trace, two ledger pushes
and a Done question for a pure read (#490), while a read's own proposal had been given a `Y` with no row to land on
(#491); see the same record, amendment #492. Batch disposition records
the pending queue in the board store, written ahead, 2026-11-02 (d-work #535): the orchestration in flight — the
queue, every question owed, every dispatched act and its wait — lived only in the cos's chat, and a hop of the cos
from one session to another would have lost it; see the same record, amendment #535. Batch disposition gains the
inbox 2026-11-02 (d-work #536): reports and relays travelled as messages to session ids, lost on a hop and
unreceivable by a terminal holder; see the same record, amendment #536. Plan gains the execution detail
2026-11-02 (d-work #555): a change of order with the content unchanged had been read as a departure and cost the
operator a question (#553 revision 3, #532 revision 6), while the operator holds that execution order not stated as a
requirement is covered by the original mandate; see the same record, amendment #555. Intent, Ledger, Answer grammar,
Completion counter-prompt and Batch disposition move to the dyad-native terms 2026-11-02 (d-work #553): a d-work is
a body of work, `unit` now naming a position; a seat is a unit, the leader the home and an unattended seat a solo;
done-`Y`, operator and agent are lowercase in prose; and Answer grammar reads an answer by meaning, because the
operator's case and spelling reach no machine directly; history keeps the old words and
`dyad/vocabulary/crosswalk.md` maps them; see `../falsification/rules/rule-6-vocabulary.md`, amendment #553 (part D). Completion counter-prompt lets the automaton execute the merge and the close
2026-11-02 (d-work #556): after each done-`Y` the home spent six to ten turns dispatching merges, reading reports,
verifying ancestry and closing, every one of them clerical execution of a recorded `Y`; see
`../falsification/rules/rule-3-d-work.md`, amendment #556. Ledger's session-start bullet cites the organization craft's roles
2026-11-02 (d-work #560): `secretary` and `cos-board` were defined in this vocabulary though only a multi-unit
organization has them; see `../falsification/rules/rule-6-vocabulary.md`, amendment #560. Ledger names the scheduled sweep as monitoring, and Mechanisms the fence's corroboration step in place of the CI job's,
2026-11-03 (d-work #564); see
`../falsification/rules/rule-14-system-infrastructure.md`, amendment #564.

Disposition: see ledger #585.

## Amendment — d-work #606 (2026-11-05: the fences of #592 stated in their Rules)
Claim (plan #606, carried under mandate #570): every refusal, warning or write #592's four code PRs (#673, #675, #676,
#678) landed and listed as a stated departure has one sentence in the Rule that owns it, saying what a reader may rely
on. One amendment here covers the sentences this d-work adds to Rules 3, 7, 11, 12 and 14.

| # | attack | result |
|---|---|---|
| 1 | (D1) The text could land before the code. | Refuted: the referent goes before the referrer (Rule-1). The code landed with #592's done-`Y`; this text follows it. |
| 2 | (D2) The verb gate belongs in Rule-14 property 3. | Refuted: property 3 owns the kernel-only path, the guards. The gate is the entrypoint's, which Rule-11 property 2 names; Rule-11 states it. |
| 3 | (D3) Each refusal line belongs in its Rule. | Survives, scoped: this Rule holds no exception clause (amendment #585, X1–X4). Each sentence states what a reader relies on — a `planned` row's plan was read, a mandate is never accreted past its ceiling, a stored trace carries the Done words — and names the command. The lines it prints stay the code's. |
| 4 | (D4) The plan-title warning needs a Rule. | Refuted: counsel ruled during #592 that an amend may retitle a plan's heading while the row's title stays immutable (Rule-16), so a retitled plan is no breach. The fence's warning is advisory; no sentence is added, and engineer may drop it. |
| 5 | (D5) UTC is Rule-7's alone. | Refuted: Rule-3 owns the `disposed` form `<date> …`, Rule-7 the entry heading. Each states its own date as UTC (`dyadlib.utc_date`). |
| 6 | The plan check refuses. | Refuted by the code: `dyad plan check` warns and exits 0 on every finding; only a missing plan, a bad id or an unknown flag exits 1. The sentence says "never a refusal". |
| 7 | The charter's ceiling also refuses. | Refuted by the code: `dwork new --mandate` refuses past the plan's stated ceiling and only warns past the charter's (`MANDATES.md`), which is the home's to reconcile (#679). The sentence names only the plan's. |
| 8 | (Rule-7 p2) A `not verbatim` label quotes the entry. | Refuted: the trace names the entry by its number and kind alone, and exempts an entry noted `relayed via` or `mandate #<id>`, whose words were given in another chat. Property 2 states that the trace writes none of the transcript's text. |
| 9 | (Rule-14 p3) An empty stdin is always a failure. | Refuted: git calls the hook with no ref line for an up-to-date push or one it rejected locally, and failing it would block nothing real. Only a hand run with no ref line fails; a terminal on stdin is refused before any read. |

**Rule-6.** No term is added or changed: `d-work trace`, `plan file`, `mandate scope`, `entrypoint` and `kernel` are used
in their existing senses.
**Pairwise (Rule-5).** **3–15**: Rule-15 owns the plan file and its phases; Rule-3's new bullet states what `planned`
guarantees of it, not its parts. **3–2**: the ceiling refusal executes Rule-2's "a row past the stated ceiling is not
bound"; Rule-2 is unchanged. **3–7**: each states its own date. **3–16**: the transition into `planned` stays Rule-16's;
Rule-3 states what the verb runs on it. **7–3**: property 2's sentence names the trace, which Rule-3 owns, only for what
it writes. **11–14**: the gate is the entrypoint's (Rule-11); the pre-push outcomes are the kernel-only path's
(Rule-14). **12–11**: `--tests` is Rule-12's child, behind the gate Rule-11 states. Others unchanged. Coherent,
orthogonal.

Disposition: see ledger #606.

## Amendment — d-work #593 (2026-11-05: the automaton as the third party, P6)
Claim (plan #593, accreted under mandate #570, P6): Rule-3 names the automaton as a party — an executor that opens no
row, answers no question and decides nothing, recording what it runs under its own name. Rules 8, 14 and 19 carry
#593's other sentences (their own records, amendment #593); this one is Rule-3's, and the vocabulary's `used by` cells
follow.

| # | attack | result |
|---|---|---|
| 1 | Naming a third party lets it dispose. | Refuted: the sentence says it decides nothing; Rule-2's Enforcement already classes it as execution, and Rule-3's Scope lists only prompts, dispositions and plan-`Y`s as what opens a row. |
| 2 | It duplicates Rule-2's automaton bullet. | Refuted, scoped: Rule-2 owns what the automaton may execute; Rule-3 states only that it is a party of the d-work, with no row, question or decision of its own, and points to the records it writes (Rules 8 and 19). |
| 3 | The vocabulary already says so. | Confirmed for `party`: its definition names the automaton since #556. Its `used by` gains 8 and 14, which now use the word; `automaton` gains 8, 14 and 19; `host action` names an automaton's, bounded by Rule-8's Classes. |

**Rule-6.** `party` used by 2 3 8 14 18 19; `automaton` used by 2 3 8 14 16 19; `host action` redefined to include an
automaton's, used by unchanged (3 7 8): each still reads correctly.
**Pairwise (Rule-5).** **3–2**: what the automaton executes stays Rule-2's. **3–8**, **3–19**: the records it writes
are theirs. **3–14**: its kernel is Rule-14 property 2's. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #593.

## Amendment — d-work #615 (2026-11-06: the intent question, under the preference `intent-reading`)
Claim (plan #615, revision 6): under `intent-reading: on`, the first reply to a prompt that opens a row, or reopens
one from `backlog`, is the intent reading — each portion of the prompt classed by `dyad/dmc/intent-reading.jsonld` —
asked as `Y/N: intent aligned for #<id> <title>?` before any plan. Its `Y` accepts the reading and the definition of
done; an amend corrects it; a bare `N` archives the row. Under `off`, the shipped default, nothing changes. The
evidence is the ledger audit `agent-corpus/audits/2026-11-06-intent-and-scope.md`: 27 of 60 refusals restated intent
or scope after a full plan, six of them after a delivery.

| # | attack | result |
|---|---|---|
| 1 | The plan-`Y` already checks intent. | Refuted as sufficient: the 27 class-I refusals each came after a full plan, six after a delivery (the audit). |
| 2 | A third question costs more attention than it saves. | Survives, scoped: the reading replaces the plan's opening, which the operator reads either way; the cost is one round trip per prompt-opened row, batchable (Batch disposition gains the intent form); and it is the operator's preference, `off` by default, never the agent's judgment. |
| 3 | The agent could ask only when it judges the reading unclear. | Refuted as a gate: #461 and #532 were misreads the agent judged clear. Who skips the question is the preference. |
| 4 | A bare `N` that archives breaks the answer grammar. | Survives, scoped: on a plan a bare `N` leaves a proposal to revise; at intent nothing is built, so there is nothing to revise from. The bare `N` archives at intent only; `N` with text amends there as everywhere. |
| 5 | `open → archived` lets the agent abandon work. | Refuted: the input is the operator's bare `N` to the intent question, a disposition, and the fence admits the edge only on a row whose last entry is `N intent` and that holds no `Y plan` (Rule-16). "Only the operator closes" holds. |
| 6 | Refusing a plan with no intent-`Y` would be a fence. | Refuted for 1.x: a Rule that now refuses what its text allowed is a break (#611 Q3). `plan check` warns instead, as #592's checks do. |
| 7 | "Intake" names the step. | Refuted: Rule-3's `intake` is another agent's message. The step is the intent reading, its answer the intent-`Y`. |
| 8 | The intent-`Y` is a plan-`Y` under another name. | Refuted: it binds the reading and the definition of done and authorizes no mutation, row or PR (What a `Y` binds); the plan-`Y` still authorizes the mutation. |
| 9 | A preference doubles the machine. | Refuted: the table is one table; the new edge fires only on `N intent`, which `off` never asks, so `off` is the earlier machine exactly. |

**Rule-6.** New terms `intent reading` (used by 3 15) and `intent-Y` (used by 3 15). Amended: `definition of done`
(accepted by the intent-`Y` under `on`), `archived` (reached from `open` by the intent question's bare `N`), `answer
grammar` (a bare `N` to the intent question archives), `pending queue` (intent-ready rows). Each Rule in their `used by`
still reads correctly.
**Pairwise (Rule-5).** **3–2**: the intent-`Y` is a ratification event Rule-2 applies to by reference; it carries no act
of Rule-2's never-carried list, since it carries no act at all. **3–7**: the intent question's answer is a disposition,
its words a record entry as every disposition's are. **3–15**: the plan file opens with the reading; phase 1 states
which `Y` accepts the definition of done. **3–16**: the edge and the `intent-asked` phase are Rule-16's table and
board. **3–10**: the intent question is a proposal framed like the others. **3–11**: a new verb (`dwork intent`) is one
`dyadlib.CLI` row. Others unchanged. Coherent, orthogonal.

Disposition: see ledger #615.

## Amendment — d-work #617 (2026-11-06: the automaton sweep)
This Rule's sentence changes with Rule-14's (Ledger names the automaton sweep and the home's read of `dyad board resume`). The claims, attacks and pairwise statements are recorded once,
in `rule-14-system-infrastructure.md`, amendment #617.

Disposition: see ledger #617.

## Amendment — d-work #619 (2026-11-06: a sweep not delivered)
This Rule's sentence changes with Rule-14's (Ledger's list of what the home reads gains a sweep not delivered). The claims, attacks and pairwise statements are recorded once,
in `rule-14-system-infrastructure.md`, amendment #619.

Disposition: see ledger #619.

## Amendment — d-work #622 (2026-11-07: the row slug)
Claim (plan #622, the operator's intent-`Y` and plan-`Y`, batch #620,#622): under the preference `dwork-slug: on`
(absent, `off`; the template ships `on`), every row id presented to the operator reads `#<id>-<slug>`, the row's row
slug after its number: 2 to 4 hyphen-joined pieces, 2–3 tags the agent chooses from the row's title when the row
opens, a defined term keeping its case, at most 32 characters, the first piece opening with a letter. It is an
optional row field (Rule-16 Store), written at birth or once on a row that holds none, never changed or removed
(`rows.slug_problems`); a terminal row never gains one. The slug is presentation only: a question binds the rows it
names by their numbers, and every stored reference — `refs`, `disposed`, provenance, the inbox, a PR body's
`d-work #<id>` — stays bare. The operator's words (provenance #622, entry 1): "d-work id should be presented along with
2-3 tag slugs after then number, e.g. "#621-release-intent-Y"".

The plan's attacks, as its falsification table states them:

| # | claim | attack | result | survivor |
|---|---|---|---|---|
| F1 | A label after `#<id>` breaks no reader | grep every pattern that reads `#<n>`: `board.ids_of`, `check_phased`, `accreted_in`, `trace.ROW_ID`, `references._RANGE` and `_HASH`, `prs.CITE`, `inbox.PLANNED_NOTICE` | survives, scoped | all read `#(\d+)` with a boundary or a non-digit after it, except `accreted_in` (fixed) and `PLANNED_NOTICE` (the inbox stays bare, F18); the slug's first piece opens with a letter, so no label reads as a range |
| F2 | A slug may be gained after birth | does any reader decide from it? | survives | no reader of `slug` but the label; authority is `disposed`, and a `Y` binds by number |
| F3 | The writers keep the slug | read every `Row(…)` that rebuilds a row | refuted as written | three writers pass `r.mode` last and would drop it; `dataclasses.replace`, and a test for each |
| F4 | The backfill lands as one batch | `land.already_landed` on `state <id> <same state>` | refuted as written | it answers "already open"; it now reads `--slug`, with a test |
| F5 | A Done asked before the flip binds after it | `ledger_lines` compares the stored question with a fresh one | refuted | the home asks PR 2 when no entry is `done-asked`; otherwise the Done is re-asked (Rule-2 Binding); plan and intent compare ids only |
| F6 | The term can be `slug` | grep the Agent Rules and the crafts | refuted | Rule-18 and syseng's naming use `<slug>` for a file name; the term is `row slug` |
| F7 | An absent key reads `on`, the template value, as `intent-reading`'s does | an upgraded system with no key | refuted for `on` | its run-books and scripts would be refused at `dwork new`; absent reads `off`; both keys keep today's behaviour when absent |
| F8 | The guard checks "2–3 tags" | `intent-Y` is one tag of two pieces | survives, scoped | the guard checks 2–4 pieces and 32 characters; the tag count is the agent's, read by you in the row's first question |
| F9 | Slugs stay unique | two sessions open rows at once | survives, scoped | under `--land` a moved `main` rebuilds the `new`, and the refusal sees the first; without it a duplicate is possible and harmless to binding |
| F10 | You can correct a bad slug | the slug never changes (item 2) | conceded | you read every backfill slug here, before the plan-`Y`; a new row's slug is fixed when it opens; a bad one costs only reading |
| F11 | The stall block can carry labels | `finding_key` folds findings by text | refuted | labels would re-tell every standing finding once; the sweep's lines stay bare (Q4) |
| F12 | #622 gets its own slug | the automaton closes it in the run that merges PR 1 | refuted | terminal before the backfill; it stays bare (A3) |
| F13 | PR 2 may be based on `main` | `test_surface` S3 with an instance key the template lacks | refuted | #590's preferences PR failed so; PR 2 stacks on PR 1, as #708 did |
| F14 | Labels keep `board resume` under its 5 s ceiling | it would read rows a second time | survives | `resume_view` reads the rows once in place of `row_states`; one preference read; the ceiling test stays |
| F15 | `VERSION` 1.1.1 is right | `check_drift` after the 1.1.0 tag | survives | the first change under `dyad/` since the tag needs the working bump; the release sets 1.2.0 |
| F16 | No overlap with work in flight | presence files and #620's draft | finding | none live; #620 touches `crafts/cabinet/` only |
| F17 | The run-books still work under `on` | `dyad/runbooks/d-work.md` and `disposition-digest.md` call `dwork new` with no slug | refuted as written | both take `SLUG`; a missing one is the verb's refusal, naming `--slug` |
| F18 | Inbox bodies can carry labels | `PLANNED_NOTICE` is `^row #(\d+) planned\b` | refuted | a label breaks it, so `handed_rows` would miss a planned notice; the inbox stays bare |
| F19 | PR 2 can be pushed at any time | the plan gate refuses a branch commit citing a terminal row | survives, scoped | it is pushed in step 2, while #622 is open; the merge itself is on `main`, which the gate skips; a later rebase is refused, and only another preferences PR can force one |
| F20 | PR 2's merge is silent | `merges.py` on a merge no `Y done` names | conceded | one warning, as #708 had; the `Y merge` entry's note keeps the `merge-disposition` warning silent |

**Rule-6.** One term is added, `row slug` (owner Rule-3, used by 3 and 16). Rule-3 reads correctly: What a `Y` binds
(the presentation and the binding by number) and Ledger (who chooses it and when). Rule-16 reads correctly: Store (the
field and its form) and Enforcement (the write-once fence). The bare word `slug` stays the file-name word of Rule-18
property 1 (`<d-work>-<hN>-<slug>.sh`) and of the syseng naming table; the term is `row slug` so the two never share a
sense (F6).
**Pairwise (Rule-5), Rule-3.** **3–1**: zones are untouched; a slug is a field of a row file in the agent zone.
**3–2**: a `Y` still binds by number (Binding); the label is in the question's text and in no entry it writes, so the
heads-unchanged and the batch rules read as before; a Done asked before the flip and answered after it is re-asked, as
a moved head is (F5). **3–4, 3–5, 3–6**: the block and coherence are kept; one term added, defined once. **3–7**:
provenance keeps the operator's words verbatim and stores no label. **3–8**: no host action. **3–9, 3–10**: the claim
was falsified (the table) and framed with its counter in the plan. **3–11**: a new preference row and a new optional
store field; surface rows S1–S3 name them; no release changes. **3–12**: the code carries its tests and invariants.
**3–13, 3–14**: no import, no manifest row. **3–15**: the plan file is untouched; its title line stays bare. **3–16**:
the field is Rule-16's to store and fence, the presentation Rule-3's. **3–18**: the file-name `<slug>` is unchanged (F6).
**3–19**: no run-book event changes. **3–20**: a slug is no reference kind; `references._RANGE` needs `#` on both
sides, which a slug never holds (F1).
**Pairwise (Rule-5), Rule-16.** **16–1**: one zone. **16–2**: the fence's new clause is a guard of the store, binding
nothing. **16–3**: Store holds the field, Rule-3 its use. **16–7**: the provenance store is unchanged and verbatim.
**16–15**: the plan file is unchanged. **16–20**: a slug is a field, never a reference the register resolves. Others
unchanged. Coherent, orthogonal.

Disposition: see ledger #622.

## Amendment — d-work #623 (2026-11-07: the blocker home)
Claim (plan #623): a fault that stops a row's next act from outside the row's own diff takes the home the decision
record `dyad/dmc/blocker-home.jsonld` gives it, stated in the d-work play-book: its own question for an act Rule-2 never
lets a `Y` carry; the row's own for a cause in the row's diff; port the fix when it is on `main`; ride another open row
whose plan describes it or whose PR holds it; its own row for a fix that adds what the system did not have, or that no
row can carry or revise; a carried row for a restore under a plan that states the blocker-fix class with its ceiling
unspent; and a revision of the blocked row's plan otherwise, the default. A restore changes no stated text and moves no
check out of the evidence block or the pre-push gate; anything else is a change. Rule-3 Incidents gains one bullet.

| id | attack | result | survivor |
|---|---|---|---|
| F1 | Rule-2's never list: "any mutation the plan did not describe" | survives, scoped | a restore's end state is already stated and ratified, and the class names it decidably (escalate-edge T2), as #570 named its children by an unmet criterion; a change's is stated nowhere, so it is asked |
| F2 | Rule-3 Scope; escalate-edge T5, "not the Agent's" | survives, scoped | Scope's route is a plan-`Y` naming the class; entry 1 is the plan-`Y`'s words; #589 and #603, found on cuts, were born so |
| F3 | The play-book step alone carries the class | refuted | Rule-3 Plan wants the class in words with a number in the plan: each plan states one line; a plan without it carries none, and its restore costs a revision |
| F4 | Restore or change is decidable (#622 revision 2: a classing text supported moving a test out of the evidence) | survives, scoped | judged against the stated text plus the coverage clause; undecidable reads as a change |
| F5 | A fix that stops every push needs its own row | refuted | spread changes when the fix lands, not who judges it: one question to land first against three; none when it joins a Done already owed |
| F6 | A recurrence needs the operator now | refuted as a gate | the incident-hardening exercise reads the incident row and the Done names the recurrence; conceded, a third occurrence may come first |
| F7 | Another zone or unit needs a question | refuted | a second zone is a second PR (Rule-1); a unit within its charter is execution detail; a preference value and a host action still ask |
| F8 | Riding the open row whose files the fix shares is cheapest | refuted | #622 revision 2 cost a question and tied #620's Done to #622's landing; shared files are a PR order |
| F9 | A carried row whose Done rides leaves its parent askable | survives, scoped | Completion's `accreted` closes it with the parent's Done, as 70 rows closed; the parent sentence's letter is left as it is |
| F10 | One carried blocker row per plan is enough | survives | none of the five cases met two; a second is asked, where two are a signal |
| F11 | A carried row may edit a Rule (#589 edited Rule-1 under #570) | refuted for this class | a Rule edit changes stated text, so a revision; #589 was a criterion #570 named |
| F12 | Rule-2 needs a sentence | refuted | its mandate clause already binds a play-book step's class of row, and the never list is unchanged |
| F13 | The record saves questions on the week's five cases (#618 r3, #619 F16, #621, #622 r2, #529) | survives | nine under the draft threshold, two as practised, one once plans state the class |
| F14 | The PR may be based on `main` before #722 lands | refuted, then moot | four shared files and the `VERSION` bump; #722 landed before the PR was built, so it is based on `main` |
| F15 | Another session works these files | finding | #622's units, whose PR has landed; #620's files are under `crafts/cabinet/` |
| F16 | The outcome names can be checked | survives | `agent/dmc` finds each name verbatim in the play-book paragraph |
| F17 | A carried row's PR passes the plan gate | survives | `Y plan (mandate #<id>)` is a `Y plan` entry; #589's and #603's PRs passed |
| F18 | Fewer questions means the operator sees less before it lands | survives, scoped | nothing lands before a Done names it (`merge-disposition: with-done`); what asks no question restores ratified text only; conceded, a wrong restore call is caught at the Done, after the work |

**Rule-6.** No term is added. "Carried", "accreted row", "mandate scope" and "revision" read as defined or as plain
words; the bullet uses no new term, and the record's outcome names are its own, never vocabulary terms.
**Pairwise (Rule-5).** **3–1**: a fix in another zone is its own PR; the zones are unchanged. **3–2**: the class carries
restores only, whose end state a ratified text already states, so it is a mutation the plan described; the never list
is unchanged, and the mandate clause already binds a play-book step's class of row, so no Rule-2 sentence (F1, F12).
**3–4, 3–5, 3–6**: the block keeps its counts; the bullet sits in Incidents, which owns what follows a fault; no term.
**3–7**: a carried row's entry 1 is the plan-`Y`'s words, copied with the mandate note (property 4). **3–8**: a host
action still goes to a question — a reversible one to a revision that names it, a destructive one to its own
counter-prompt. **3–9, 3–10**: falsified above and framed with its counter in plan #623. **3–11**: no release changes,
and a release stays its own question. **3–12**: the restore test keeps every check in the evidence block and the
pre-push gate; a fix that moves one is a change. **3–13, 3–14**: no import, no manifest row; the kernel-only path is
untouched. **3–15**: a carried row has its own plan file, unasked, as #589's did; the parent's base commit governs
re-planning. **3–16**: `refs: parent #<id>` and the ceiling count are the store's as they stand. **3–18, 3–19**: no ops
script or run-book changes. **3–20**: the record's paths resolve; no reference kind is added. Coherent, orthogonal.

Disposition: see ledger #623.

## Amendment — d-work #643 (2026-11-08: internal realization as execution detail)
Claim (plan #643): Rule-3 Plan's execution-detail bullet, and the `execution detail` outcome of
`dyad/dmc/plan-departure.jsonld`, admit an **internal realization**, a change whose effect stays inside the PR, in one
of three forms. **Placement**: a file's path differs while the move stays within one zone and one craft root, the content
is byte-identical, the old path never landed on `main`, no file outside the PR refers to the old path, the path is in no
released craft's tree, and the plan did not name the path as a requirement. **Implied means**: the plan's text names the
effect, and the means adds no public surface. **Compatible extension**: an optional parameter of an internal function,
defaulting to the old behaviour, with no caller changed and a test showing it. Public surface is a `dyadlib.CLI` row, a
`dyad/surface.md` row, a path in a released craft's tree, or Rule or preference text; each use is a departure line in the
completion evidence. Origin: #626 and #640 each moved files and were ruled execution detail, which the record's words did
not admit; a blind precedent test then read two #619 cases (`audits.py level`, ratified as planned, and `code_digest`'s
`repo=`, ratified as execution detail) as new plans too.

Moves — the home's read-only falsification of the record's wording (W1–W6):

| id | attack | result | survivor |
|---|---|---|---|
| W1 | The list is exhaustive: only the order of steps, the split or stacking of PRs, the unit executing a step within its charter, or the tooling route may differ; a path is not on it | confirmed | a move fails "only … differs", and precedence gives new plan, so placement must be named to be admitted |
| W2 | A path is part of the plan's files touched and of the tree it ends with | confirmed | a move changes the stated mutation and its end state, so placement is admitted only where nothing outside the PR sees the path |
| W3 | "Tooling route" stretches to where code lives | refuted reading | tooling route is how a step is executed (which command, tool or route), not where a file sits |
| W4 | A path is a contract once referenced: resolvers, a craft's archive, installs; moving a path in a released craft's tree breaks installs | confirmed | any allowance excludes a path that ever landed on `main`, one a file outside the PR refers to, and one in a released craft's tree |
| W5 | #626 moved four records from the agent zone to the workstation zone, changing which zone, PR and charter own them | confirmed | a zone change, or a move across craft roots, is never placement |
| W6 | A new `Y` for every forced move costs the operator a question each time (#623's target) | survives, scoped | the old wording's cost, which this amendment reduces for moves inside the fence alone |

The two further classes — the plan's own falsification (I1, I2, C1, C2, U1):

| id | attack | result | survivor |
|---|---|---|---|
| I1 | "Implied means" admits any new artifact a builder claims the plan required, a new verb included | confirmed | admitted only when the plan's text names the effect the means achieves and the means adds no public surface: no `dyadlib.CLI` row, no `dyad/surface.md` row, no path in a released craft's tree, no Rule or preference text |
| I2 | A new subcommand of an internal script (`audits.py level`) is still a way in | survives, scoped | a script's own argv that no `dyadlib.CLI` row or `surface.md` row lists is internal; #619's case passes under I1 |
| C1 | "Compatible extension" covers a new CLI flag, which installing systems see | confirmed | admitted only for an optional parameter of an internal function, defaulting to the old behaviour, with no caller changed; a CLI flag, a record field or a file format is public surface, and so a new plan |
| C2 | An optional parameter can still change behaviour through its default | survives | the default reproduces the old behaviour, and a test the plan lists, or one added, shows it |
| U1 | Three new classes widen the plan-`Y`'s cover | survives, scoped | all three share one fence, no effect outside the PR: no public surface, nothing landed at an old path, nothing released; past it, a change stays a new plan |

**Survivor (as implemented).** One clause, internal realization, in three forms — placement with its six conditions,
implied means, compatible extension — fenced by public surface and reported as a departure line, added to the
execution-detail bullet and to the record's `execution detail` condition. No outcome name changes, so the record's
index check reads the Rule as before.

**Verdicts on the precedents.** #619 case 3 (`audits.py level`) and case 4 (`code_digest(repo=)`) pass as execution
detail under internal realization; case 3's label `as planned` is read as execution detail, a relabel, not an overrule.
#640's `tidy.py` move, from `crafts/cabinet/guards/` to `crafts/cabinet/scripts/`, was a new plan under the old wording and
passes as placement under this one. #626's records move, a zone change, was a new plan under any reading and stays a
misruling. None is reopened: their Dones stand, and the two misrulings are incidents.

**Rule-6.** No term is added: "internal realization", "placement", "implied means" and "compatible extension" are
prose inside the bullet, and "public surface" is defined in the same sentence; the record's outcome names are its own.
**Pairwise (Rule-5).** **3–1**: placement's first condition reads the zone table and the craft root; it never moves a
path across a zone, so containment is untouched and a zone move stays a new plan (W5). **3–11**: the released-craft
condition reads each craft's tags and tree; nothing in a released craft's tree may move, and a release stays Rule-11's
question. **3–15**: "the plan did not name it as a requirement" reads Rule-15 phase 1's stated requirements; a plan that
names a path makes it a requirement. **3–20**: "no file outside the PR refers to it" reads references as they stand; the
register gains no kind, and a moved path no reference resolves to is the condition, not a new check. The other pairs
are as amendment #555 left them, since the bullet's existing conditions and its Rule-2 bound are unchanged. Coherent,
orthogonal.

Disposition: see ledger #643.

## Amendment — d-work #644 (2026-11-08: the precedent question)
Claim (plan #644): a ruling a d-work's completion evidence names on a decision record becomes a precedent of that
record only by the operator's `Y` to a question naming it. What a `Y` binds gains the **precedent question**,
`Y/N: admit as precedents <cases>?`, listing decision-log entries by record and case id, whose **precedent-Y** binds exactly
those lines and nothing else; Batch disposition names it its own kind, never folded into a Done question, asked as one
batch at the next backlog grooming or once at least five candidates are pending; Ledger gives its entry,
`<date> Y precedent (<n> cases: <record>×<k>, …)`; Ratification events gains a fifth bullet. Rule-16 Store gains the
decision log, the store a Done's named rulings are written to as candidates with the `Y` that covers the work. The
d-work play-book's Evidence step names departure and class lines as its candidates. With it, four records whose
context the plan's blind precedent test found missing are restated so a reader reads them one way: `attack-result`
(its outcomes renamed to read one way only — attack holds, attack fails, claim survives, no attack found — their
termCodes kept, and Rule-9 gains one Form line mapping the table's confirmed, refuted and survives onto them), `release-class` (a
decision record with its test that changes what a check runs or when is a significant enhancement, as #621 classed
#618, and no longer maintenance), `retirement-candidate` (a retirement decided before #626 stated its grounds is not a
case of it) and `craft-instantiation` (each criterion's input states its firing condition, as the play-book's table
does). Only `attack-result`'s outcome names change; every termCode stays.

| id | claim | attack | result | survivor |
|---|---|---|---|---|
| F1 | a `precedent-Y` is needed beside the Done | a Done naming each ruling would do | refuted for practice | a Done covers the work, and its rulings were not examined (#626's zone move); a separate question the operator answers on a listed batch is the examination |
| F2 | it adds little attention | one more question per batch | survives, scoped | batches of five or more, asked at grooming or at the count, never per ruling; the backfill is one question |
| F3 | its entry needs no guard change | `rows.py` and Rule-7's count read every `Y …` entry as a disposition | survives | `Y precedent (…)` is a disposition like `Y archive (…)`, so its words are copied into the provenance record (Rule-7 property 5) |
| F4 | the two-reader backfill is sound | both readers may agree with each other and still be wrong | survives, scoped | a case is kept only when both match the source's own wording too, and the precedent-`Y` reads the listed entries |
| F5 | order is needed | conversions before admission would freeze unadmitted cases | confirmed | `order: required` for the record fixes, the admission and the conversions; `freeze` refuses a set with any line not `precedent` |
| F6 | instance precedents serve core records | a core record pointing at instance data | survives | a record's precedents resolve through `DYAD_INSTANCE` (Rule-11 property 3), so each system keeps its own and a fresh install has none |
| F7 | the decision log fits the d-work store as planned | a `<row>.jsonl` there is a tracked `*.jsonl` under the d-work store, which Rule-7 property 2 and `provenance.tracked_jsonl` refuse as a raw transcript | confirmed (counsel, during PR A) | the store takes the d-work store's own pattern, `decisions/<row>.md`, one `## <case id>` block of `key: value` lines per ruling, a status change a later block (plan revision 2, the operator's `Y`), and Rule-7 is unchanged |

**Rule-6.** `precedent-Y` and `precedent` (the kind, and a decision-log entry's status) are added, owner Rule-3; `precedent`
is used by Rules 3 and 16, `precedent-Y` by Rule-3. No other term changes.
**Pairwise (Rule-5).** **3–2**: the precedent question is a ratification event declared under Rule-3's own heading, to
which Rule-2 applies by reference with no edit (G5); its `Y` binds exactly the listed entries, as Binding's first sentence
binds every `Y`, and it is never carried by a plan-`Y` or a done-`Y`. **3–7**: the entry is a disposition, its words
copied with the row (property 5); the decision log holds the agent's record of rulings, never the operator's words, and
no `*.jsonl` is tracked under the d-work store (F7). **3–9**: the one Form line maps the table's three words onto the record's renamed
outcomes, which the record's index check reads in Rule-9; the attack table's words are unchanged. **3–16**: the decision log is a store beside the inbox, written in the
clerical commit that records the `Y` it rests on, so it is ledger-only; its guard checks shape and append-only, as the
inbox's does. The other pairs are as amendment #643 left them. Coherent, orthogonal.

Disposition: see ledger #644.

## Amendment — d-work #646 (2026-11-08: the closing line, awaiting you)
Claim (plan #646): the line every reply ends with should count what waits on the operator. That is the questions asked
and not answered, by kind, with a batch question counted once. The rows ready for a question not yet asked are the
agent's own work and come after it. The line is generated from the asks the board records, and its form is a preference.

Batch disposition loses "reports their counts at the end of every reply" and gains the **closing line** bullet. Its form
is the preference `awaiting-you`:
- `on` — `Awaiting you: …` then `Coming: …`;
- `off` — the counts as before.

The template ships `on`, and an absent key reads `on` (plan revision 2, provenance #646 entries 9 and 10; the name
`closing-line` of revision 1 was withdrawn before it landed). `dyad board` generates the line from the
questions the board records. Each question is recorded on its row's entry before it is asked: by its phase for intent,
plan and Done, and as the entry's `question` for precedent, release and destructive. So a question asked unrecorded is
an incident, never a line written by hand. The vocabulary gains `awaiting you`.

The finding behind it: the line counted rows ready to be asked and never a question owed. The free-text
`waiting-on: operator` of a board entry was no substitute: #503's entry said it while recording no question.

### Falsification of "Awaiting you" is a preference setting (provenance #646, entry 6)
| id | attack | result | survivor |
|---|---|---|---|
| Q1 | a preference chooses among values; are there two? | survives, scoped | two forms of the closing line: `on` (questions owed, then coming) and `off` (the counts as before) |
| Q2 | the count itself is a preference | confirmed | what is owed is a fact of the records; no value may change it. Only the line's **form** is a preference |
| Q3 | a preference here authorizes something | refuted | like `relay-form` and `dwork-slug`, it shapes what the operator reads, never what a `Y` binds: a form preference |
| Q4 | an installing system's behaviour changes silently | survives, scoped; reversed by revision 2 | revision 1 read an absent key as the old line; the operator set the default `on` (entry 9), so an upgrading system shows the new line, stated in the release's changes (R1) |
| Q5 | it costs no more | confirmed, then moot | setting a value here is a preferences-zone PR with its own merge question; with the default `on` this instance sets none, so that PR is dropped (R2) |

### Falsification of "Awaiting you" is mechanically generated (provenance #646, entry 7)
| id | attack | result | survivor |
|---|---|---|---|
| G1 | it is generated today | confirmed | nothing generated it: the line in the replies before this amendment was written by hand |
| G2 | intent, plan and Done can be | survives | `board advance … asked` records each ask and `answered-Y`/`answered-N` each answer, so owed is a predicate over the board |
| G3 | precedent, release and destructive can be | confirmed as first planned, survives as revised | none has a phase, and #644's precedent question was recorded on no board entry; recording each as its entry's `question` before it is asked makes all six kinds mechanical |
| G4 | complete only if every ask is recorded | survives, scoped | write-ahead is already this section's rule; a question asked unrecorded is the incident, and the line is never patched by hand |
| G5 | the reply itself is generated | refuted | the line's content is generated; placing it last before the `Y/N` is the agent's copy, which no harness hook makes mechanical. Out of scope |
| G6 | a gap between the reply and its recording | survives, scoped | for the moments before `answered-Y` lands, the line still shows the question as owed, and the next `dyad board` read corrects it |

### Revision 2 (provenance #646, entry 9: "default setting is "On" to display "Awaiting you:" .")
| id | attack | result | survivor |
|---|---|---|---|
| R1 | a default that changes an upgrading system's output breaks it | survives, scoped | the line is presentation; it authorizes nothing and no code parses it, so nothing downstream reads the old text; the release's changes name it |
| R2 | dropping the instance's preference PR leaves the instance unrecorded | survives, scoped | the preference guard warns that the template's key has no row here, naming its own fix, until the instance's table is next edited |
| R3 | `on`/`off` loses the two-form reading | refuted | `off` is the old form, so both forms stay |

### Revision 3 (provenance #646, entries 11 and 12: the kinds are a decision record's outcomes)
The kinds the line counts are the outcomes of a new mechanical record, `dyad/dmc/disposition-request.jsonld`, homed
in this Rule as an index record (each outcome name appears in Batch disposition), `alsoIn` Rules 2, 8 and 11, which own
the merge, destructive and release forms, and implemented by `board.awaiting`. Its two groups are d-work (`intent`,
`plan`, `done` by phase; `retirement` and `precedent` by form) and merge (`merge`, `release`, `destructive` by form);
the phase takes precedence over the form, and the default `none` counts nothing and warns. A merge asked as its own
question and the retirement form, which revision 2 missed, now count.

| id | attack | result | survivor |
|---|---|---|---|
| D1 | an existing record already decides it | refuted | no record of `dyad/dmc/` or `crafts/*/dmc/` classes a question asked of the operator; `merge-question`, `held-pr` and `disposition-budget` decide other things |
| D2 | the forms change and the record goes stale | survives, scoped | each form is the one its owning Rule states (Rule-3, Rule-8, Rule-11), so a changed form is a Rule edit, whose falsification names this record |
| D3 | an intake is a request for disposition too | survives, scoped | Rule-3 Intake gives it no fixed `Y/N` form, so it falls to the default, and the guard's warning names it |
| D4 | two groups add words to every reply | survives, scoped | each group is printed only when it is non-zero |
| L1 | a record cannot be made without a Rule | refuted as a mechanism | the schema asks only for a home file; 47 records name no Rule in their home or `alsoIn` (a finding, not this row's) |
| L2 | a record must have one | survives as discipline | only a Rule path in the record lets that Rule's falsification find it when the Rule changes (D2 rests on it) |
| L3 | this record has one | survives | homed in this Rule, which owns the questions, as an index record whose outcome names the dmc guard finds in its text |

**Survivor.** The count is a fact of the board store, generated by `dyad board` for every kind
`dmc:disposition-request` names and never written by hand. The line's form is the form preference `awaiting-you`,
`on` or `off`, the template shipping `on` and an absent key reading `on`.

**Rule-6.** `awaiting you` is added, owner Rule-3, used by Rule-3, its kinds cited from `dmc:disposition-request`. `pending queue` keeps its definition: it is still the
agent's batch store, now reported as the line's `Coming` part. No other term changes.

**Pairwise (Rule-5).**
- **3–2**: Binding is unchanged. The line counts questions and binds nothing, and a `Y` still binds exactly what its
  question names; the record's merge form is Rule-2's, cited in `alsoIn`. **3–8** and **3–11**: the destructive and
  release forms are theirs, read by the record and never restated, so either Rule's change of form names the record
  (D2).
- **3–10**: the closing line stands before the reply's last line, which is still its one `Y/N` (Rule-10 Form). The
  line is a count and never a second question.
- **3–16**: the line reads the board store and writes nothing to it. The board's phases and its `question` field are
  Rule-16's, unchanged.

The other pairs are as amendment #644 left them. Coherent, orthogonal.

Disposition: see ledger #646.

## Amendment — d-work #648 (2026-11-09: precedent capture at every Done)
Claim (plan #648): the rulings a row's Done names reach the decision log as candidates in the commit that records that
Done, so the set of precedents grows with the work and no backfill has to find them later.

What changes:
- Completion counter-prompt's Record step gains the candidates. The commit carries the file `dyad board draft <id>
  --decisions-out <file>` writes: the structured candidates of the row's own sources (its plan's verdict tables, its own
  entries, the change-log rows naming it, each case `<record>-<row>-<n>`, kept only where `dmc:precedent-admission`
  could admit it), and the prose lines the agent fills in the draft's `TODO plan-departure: facts | outcome` slots.
- The file is recorded by `--decisions` on `dwork state … -d 'Y done …'` or on `board advance … answered-Y`.
  `dwork state` refuses, before any write, a `Y done` with no `--decisions` on a row whose draft lists a candidate.
- The no-merge Done path names the candidates in its one commit.
- The d-work play-book's Evidence and Record steps name the draft's Candidates section and the file.

| id | claim | attack | result | survivor |
|---|---|---|---|---|
| K1 | capture cannot be skipped | the agent records `Y done` by `dwork state` by hand, around `board advance` | survives | both paths take `--decisions`, and `dwork state` refuses a `Y done` with none while the draft lists a candidate |
| K2 | the case ids are unique | two rows' tables hold the same attack id | survives | the id carries the row, `<record>-<row>-<n>` |
| K3 | one ruling, one id (#645) | backfill already lists the same ruling under another id | survives, scoped | capture uses the one id form, and `precedent gate` refuses a case the log already names |
| K4 | the refusal costs no question | the agent disputes a candidate | survives | the agent may drop a line from the file, and the completion evidence names each dropped line with its reason |
| K5 | the candidates are a disposition | a candidate written with the `Y done` is read as admitted | refuted | the block is written `candidate`; only a later precedent-`Y` naming it makes it a precedent (What a `Y` binds, #644) |

**Rule-6.** No term is added or changed.

**Pairwise (Rule-5).**
- **3–7**: the Record commit's provenance entry is unchanged. The decision log holds the agent's record of rulings,
  never the operator's words.
- **3–16**: the decision log's store, shape and append-only rule are Rule-16's, unchanged; this Rule names only when its
  candidate blocks are written.
- **3–2**: a done-`Y` binds what its question names. A candidate is no act it binds, so Binding is unchanged.

The other pairs are as amendment #646 left them. Coherent, orthogonal.

Disposition: see ledger #648.

## Amendment — d-work #665 (2026-11-10: the Coming part as its own preference)

**Claim (the operator, provenance #665 entry 1):** "making "Coming:" a preferences setting with default of "on"". The
closing line's Coming part, which counts the pending queue, is shown under its own preference `coming`, absent read as
`on`; with `off` the line is the Awaiting part alone. The key is read only under `awaiting-you: on`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| C1 | An upgrading system changes its line, having no `coming` row. | **Refuted** | An absent key reads `on`, today's line; the guard's "seed it" warning is the only effect, as for `awaiting-you`. |
| C2 | Hiding Coming hides something owed: a row ready for a question drops from the operator's sight. | **Survives, scoped** | Coming counts rows not yet asked, the agent's work and never the operator's (#646); Awaiting is unchanged, and `dyad board` still prints the queue line. |
| C3 | Under `awaiting-you: off` an operator sets `coming: on` and expects a Coming part. | **Survives, scoped** | `off` prints the queue line, which is the Coming part's content; the template says `coming` is inert there. |
| C4 | A bad value (`coming: Off`, a typo) breaks a reply's last line. | **Refuted** | The board reads it as `on`, and the preferences guard warns on a value outside `on|off`; the line still prints. |
| C5 | One PR carries the instance's seed with the code. | **Confirmed, so planned apart** | `preferences-corpus/` is its own zone (Rule-1); the seed is a second PR, asked as its own merge question. |

**Verdict:** the claim survives.
- **Rules:** Batch disposition's closing-line bullet names the preference; Provenance gains its line.
- **Vocabulary:** `awaiting you` names the key. No term is added.
- **Template:** the `coming` row and its description; `surface.md` freezes the key.
- **Code:** `board.py` reads the key (the engineer's part).

**Pairwise (Rule-5).**
- **3–6**: one row's definition gains the key; the row's `used by` (Rule-3) still reads correctly.
- **3–2**: the closing line authorizes nothing, so Binding is unchanged; `coming` is a form preference.
- **3–1**: the code PR is agent zone and the instance seed a separate preferences-zone PR.
- **3–16**: the board store and its derived queue are unchanged; only the line's form reads the key.

The other pairs are as amendment #648 left them. Coherent, orthogonal.

Disposition: see ledger #665.

## Amendment — d-work #670 (2026-11-11: Awaiting you names where to answer)

**Claim (the operator, provenance #670 entry 1):** "since #668 is assigned to a `dyad` unit (attended by operator), the
unit should be included because i was looking for the Y/N counterprompt in this unit when i should have looked for it in
another". Inside each kind's parentheses of the closing line, the reader's own questions come first, then each other
dyad unit's as `<labels> in <unit>`. A solo's question, relayed through the home, names no unit; counts are unchanged.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| U1 | The holder is not where the question was asked: the home records a question it relays for a solo. | **Refuted** | That question is answered in the home's own chat, which names nothing; a solo's question has the home as holder or is relayed, so it is answered there either way. |
| U2 | A question is named twice: a batch spans entries of two holders. | **Survives, scoped** | A batch is asked once, in one chat; the first entry's holder is read, and write-ahead records the same question on each entry. |
| U3 | A unit unpaired after asking keeps its `in`. | **Survives, scoped** | The holder is the record and dyad-ness is read now: an unpaired holder's question loses its `in`, and the home relays it, the route Rule-16 gives an unpaired unit. |
| U4 | Many places make the line long. | **Survives** | One group per place per kind; today the line shows two places at most. |
| U5 | A reader-less run (a script, the automaton) changes the line. | **Refuted** | With no `DYAD_SESSION` nothing is named, so today's string is unchanged. |

**Verdict:** the claim survives.
- **Rules:** Batch disposition's closing-line bullet names the unit; Provenance gains its line.
- **Vocabulary:** `awaiting you` says the same. No term is added.
- **Code:** `board.py`'s `awaiting` keeps the holder and `answered_in` names it (the engineer's part).

**Pairwise (Rule-5).**
- **3–16**: dyad unit, solo and the relay route are Rule-16's, read and unchanged; the line reports the route, never
  sets it.
- **3–2**: the line authorizes nothing, so Binding is unchanged.
- **3–6**: one row's definition gains the clause; its `used by` (Rule-3) still reads correctly.

The other pairs are as amendment #665 left them. Coherent, orthogonal.

Disposition: see ledger #670.

## Amendment — d-work #676 (2026-11-11: the intake split)

**Claim (the operator, provenance #676 entry 1: "need a formal `dmc` for intaking work that can be shared with downstream
as well"):** an admitted hand-up from a downstream dyad system of the same operator is split item by item by a core
record, `dmc:intake-split`: upstream core, upstream craft, downstream instance, both, or asked back. Another party's
records and every credential stay downstream data. The hand-down is shown to the operator before it is sent.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| I1 | Five outcomes do not cover an item that is half a mechanism and half one client's data. | **Refuted** | That is `both`, the privacy rule saying which half stays down. |
| I2 | A trivial mechanism is cheaper to build with the sender's sample data. | **Refuted** | The privacy rule makes another party's records downstream data whatever the cost; upstream builds against fixtures it writes itself. |
| I3 | It overlaps `dmc:intake-shape`, which reads the same message. | **Refuted** | intake-shape decides admission and runs first; intake-split runs only on an admitted hand-up and decides placement. |
| I4 | It overlaps `dmc:bundled-craft`: an upstream-craft item makes a craft bundled. | **Refuted** | Placement says where a mechanism is built; whether the core release carries that craft stays bundled-craft's, judged on the craft's own tree (#663). |
| I5 | Downstream cannot read a record its older core lacks. | **Survives, scoped** | It arrives with the next core release; until then the hand-down states each item's outcome and ground in words. |
| I6 | A precedent could settle a split wrongly. | **Survives** | `asked-back` is `asks` and the four placements `shapes`: a wrong match costs at most a question the operator answers anyway, since every build is a row of its own. |

**Verdict:** the claim survives.
- **Rules:** Intake gains one sentence naming the record and its five outcomes; Provenance gains its line.
- **DMC:** `dyad/dmc/intake-split.jsonld`, an index record homed here, inference, its effects declared.

**Pairwise (Rule-5).**
- **3–2**: every build the split names is a row of its own, asked as any row is; the hand-down's send is a `Y` like
  every outward communication. Binding is unchanged.
- **3–7**: the hand-up's operator words are cited by the sender's provenance, and a relayed prompt is entered as
  property 4 says; nothing of the sender's own text becomes a provenance entry here.
- **3–11**: Rule-11 property 1's craft/instance line is read, never changed: `downstream-instance` is instance state,
  which no craft may hold, and `upstream-craft` is a craft's.
- **3–16**: no store changes.

The other pairs are as amendment #670 left them. Coherent, orthogonal.

Disposition: see ledger #676.

## Amendment — d-work #690 (2026-11-12: the judgement trace)

**Claim (the operator, provenance #690; the intent-Y's words: "Y, call it judgement trace. now propose the playbook and
corresponding `dmc` for the judgement portion of the playbook"):** an act of the agent's that the operator questions is
examined by a play-book, the judgement trace. The act is traced back to the texts on `main` that decided it, and its
cause is classed by a core record, `dmc:judgement-cause`: misapplied, conflict, stale, gap, intended or undetermined.
Incidents gains the one sentence that reads the play-book.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| J1 | The agent cannot class its own act honestly: it is judge of its own conduct. | **Survives, scoped** | Every class rests on cited text the operator can read; the class is presented, never final (Rule-2: an agent-authored verdict is the operator's to finalise); the play-book's two fences, anti-cave and two-models, bar a class chosen to please or to defend. |
| J2 | An `intended` trace that records nothing loses the explanation when the chat ends. | **Survives, scoped** | The explanation is the product, and a read-only answer records nothing (Scope, #492); an operator who wants it kept prompts a change, which opens a row and stores it. |
| J3 | The six classes are disjoint. | **Refuted as disjointness; kept as precedence** | #689 held four at once; classes are given per traced line and per finding, every class present gets its outcome, and the trace's cause is the highest by the record's precedence. |
| J4 | The play-book needs no Rule sentence. | **Confirmed** | The vocabulary guard fails a term no Rule uses, and a play-book no Rule reads is never triggered by one (Boundaries: play-books are read by a Rule, never a Rule); hence the one Incidents sentence. |
| J5 | The sentence overlaps Incidents' existing definition: a questioned act is already an incident. | **Refuted** | The definition says what an incident is and how it is recorded; the new sentence says how a questioned act is examined before anything is known to be an incident. Only `misapplied` makes one, recorded by the existing bullet, which is unchanged. |
| J6 | It overlaps the blocker home (`dmc:blocker-home`). | **Refuted** | The blocker home places a fix for a fault that stops a row; the trace finds a cause. Its `stale` outcome hands the restore to the blocker home, which still decides where it rides. |

**Verdict:** the claim survives.
- **Rules:** Incidents gains one bullet naming the play-book and the record; Provenance gains its line.
- **Vocabulary:** `judgement trace` (owner 3, used by 3).
- **Play-book and record:** `dyad/playbooks/judgement-trace.md`, its run-book and `dmc:judgement-cause`, the master record homed in the play-book.

**Pairwise (Rule-5).**
- **3–2**: the class is an agent-authored verdict and so never final; its outcomes that change a text open or revise a row, asked as any row is. Binding is unchanged.
- **3–7**: a trace writes nothing to a provenance record; the operator's prompt that starts it is entered as any prompt is.
- **3–9**: the trace's attacks are its T3 conflicts; its record is the plan file of the row it opens or revises, as #689's was.
- **3–16**: no store changes.

The other pairs are as amendment #676 left them. Coherent, orthogonal.

Disposition: see ledger #690.

## Amendment — d-work #691 (2026-11-12: the audit's due state in the Coming part)

**Claim (the operator, provenance #691 entry 1: "yes, propose automated sweep based on trigger conditions (not
time)"; plan revision 3):** the closing line's Coming part counts, beside the pending queue, the conditions of the
audit's due state that `dmc:audit-trigger` records on the home's cross-row board entry, as `audit-due <n>`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A1 | Coming counts the agent's own queue; an audit's due state is not a queued question. | **Survives, scoped** | Coming already counts what the operator will be asked and has not been; an audit due is such a matter, shown unasked. It authorizes nothing, as the line's form never does (#646). |
| A2 | The count could drift from the readings. | **Refuted** | `dmc:audit-trigger` records the conditions on `_cos.md` (`audit-due`), and `dyad board` derives the part from that field, as the rest of the line is derived; no unit writes it by hand. |
| A3 | Under `coming: off` the operator loses the signal. | **Survives** | That is what the preference says: Coming is the operator's to hide (#665), and the board entry still holds the state. |
| A4 | It overlaps Awaiting you. | **Refuted** | Awaiting counts questions asked and not answered; `audit-due` is no question until the home asks one, at which point it is counted there instead. |

**Verdict:** the claim survives.
- **Rules:** Batch disposition's Coming sentence names `audit-due`; Provenance gains its line.
- **Vocabulary:** the `awaiting you` row names the part.

**Pairwise (Rule-5).** 3–16: the field is the board store's, `audit-due` on the cross-row file (`board.COS_FIELDS`), shape-checked by its guard; no other pair changes. The other pairs are as amendment #690 left them. Coherent, orthogonal.

Disposition: see ledger #691.

## Amendment — d-work #692 (2026-11-12: a standing mandate for hardening work)

**Claim (the operator, provenance #692 entry 1: "i prefer (preference) to provide a standing disposition to work on
hardening work once it meets aligned conditions established by an aligned `dmc`"):** a third authority preference,
`hardening-mandate`, opens a `backlog` row of hardening work (`dmc:hardening-work`) when it is due
(`dmc:hardening-due`), with no intent or plan question; its Done is always asked.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| M1 | Plan says every plan is asked; a row opened with no plan question breaks it. | **Survives, scoped** | Plan's sentence names the one exception, as it already names the carried row: the operator's grant of the preference stands for the plan, as a plan-`Y` stands for its accreted rows. Rule-2 already counts an authority preference as a mandate. |
| M2 | A standing mandate removes the operator from the merge. | **Refuted** | The row's Done is always asked (Scope), and a merge is ratified only by a done-`Y` naming it (Rule-2, Binding). Two questions go, the intent and the plan; none goes at the merge. |
| M3 | The mandate could carry a never-accretable act. | **Refuted** | `dmc:hardening-work` W3 excludes public surface and every act on Rule-2's list, and W2 admits only a restore. A row that fails either is ordinary backlog and is asked. |
| M4 | The row has no prompt, so Rule-7's transaction check refuses the `backlog → open` commit. | **Survives, the Rule extended** | Property 4 gains the mandate preference's entry: the grant's words, copied verbatim and noted `mandate preference <key>, <the grant's date>`, and Enforcement accepts it in place of the prompt. |
| M5 | The note names an instance row id in the core. | **Refuted** | The core names the form, `granted: d-work #<id> entry <n>`, read from the instance's description of the key; no row id of this instance is written in the core (the engineer's departure from the plan's "provenance #692 entry 1", reported in the completion evidence). |
| M6 | Rule-16's attendance reading counts a note holding `mandate preference` as an own disposition of the unit that ran the verb. | **Confirmed; the Rule extended (plan revision 2)** | The reading excluded `mandate #` and `relayed via` only; a mandate-preference entry is no more given in that unit than a mandate's is. Revision 2 adds `mandate preference` to Rule-16 Presence's exclusions, and `sessions.own_disposition` with its test. |

**Verdict:** the claim survives; M6 is closed by plan revision 2.
- **Rules:** Scope gains the mandate preference; Plan its exception; Ledger's `backlog` bullet names it. Rule-2's Binding names the third authority preference. Rule-7 property 4 and Enforcement gain its entry.
- **Vocabulary:** the `mandate` row names `hardening-mandate: on`.
- **Rule-16** (revision 2): Presence's own-disposition clause excludes a `mandate preference` note.

**Pairwise (Rule-5).**
- **3–2**: the mandate's reach is one class and one ceiling, and the never-accretable list is unchanged; Binding names it, Rule-3 says when it opens a row.
- **3–7**: property 4 holds the grant's words, and property 5's count is exact, since the row gains one `disposed` entry and one `disposition` entry.
- **3–16**: no store changes; the attendance reading names the new note beside `mandate #` and `relayed via`, so a row
  opened under the mandate reads as no unit's own disposition (M6).

The other pairs are as amendment #690 left them. Coherent, orthogonal.

Disposition: see ledger #692.

## Amendment — d-work #695 (2026-11-12: Recommended for next, the closing line's third part)

**Claim (the operator, provenance #695 entries 1 and 2):** the closing line gains a third part, `Recommended for next:`,
for the outcomes of triggers — mechanically generated where it can be, the rest by the agent's judgement — under a
preference `recommended-next`, `on` by default.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| N1 | The part is generated from records alone, yet some outcomes need judgement. | **Survives, scoped** | The judgement is the home's, recorded first as `recommended:` lines on its cross-row board entry (write-ahead); `dyad board` generates the part from those lines and the outcomes it computes, so a reply cannot claim what no record holds (the line written by hand on 2026-11-10). |
| N2 | An inferred entry stays true after it is written. | **Survives, scoped** | An entry naming a row no longer `backlog`, or written before that row's last change, is dropped with a warning until re-recorded; staleness of any other input is the home's to re-record. |
| N3 | A recommendation authorizes work. | **Refuted** | The part is a form preference's and authorizes nothing; an item becomes work only by its trigger's own question or an operator prompt, and a hardening row a mandate opens unasked reads `starting`. |
| N4 | It duplicates Coming or Awaiting you. | **Refuted** | Awaiting counts questions asked, Coming rows ready for a question the agent will ask and the audit's due state; this counts what is due and nobody has started, and leaves out every row counted in either and the audit while Coming shows `audit-due`. |

**Verdict:** the claim survives.
- **Rules:** Batch disposition's closing line names the third part, its preference and its kinds; Provenance gains its line.
- **Vocabulary:** the `awaiting you` row names the part.

**Pairwise (Rule-5).**
- **3–2**: the part authorizes nothing and binds no `Y`; Binding is unchanged.
- **3–16**: the key `recommended` is the board store's, on the cross-row file (`board.COS_FIELDS`), shape-checked by its guard, written write-ahead as every board entry is.

The other pairs are as amendment #690 left them. Coherent, orthogonal.

Disposition: see ledger #695.
