# Rule-3 clause map — d-work #585 (draft, 2026-11-04)

The DoD report of plan #585. It has one row for each sentence, or tightly coupled sentence group, of today's
`dyad/rules/RULE-3-d-work.md` (base: branch `572-playbook` at `9bbb5cc8`, identical to `main`'s Rule-3 at `3c51c9d`),
in order. Fates:
- **kept**: the same obligation, reworded or shortened;
- **merged**: folded into a broader statement of the new text;
- **moved**: now stated by the Rule or play-book that owns the concern, and only pointed at here;
- **dropped**: history or a restatement; nothing it obliged is lost.

New sections are referred to by heading: *Scope (what opens a row)*, *Answer grammar*, *What a `Y` binds* (new),
*Plan*, *Completion counter-prompt*, *Batch disposition*, *Ledger*, *Mechanisms*, *Intake*, *Incidents*,
*Ratification events*, *Provenance*.

## Map

| § | sentence (first words) | fate | where in the new Rule / target | reason | origin |
|---|---|---|---|---|---|
| title | "# Rule-3: d-work" | kept | title | Rule-4 block | #12 |
| head | "**Intent:** Run every body of operator-prompted work as a d-work that opens…" | kept | Intent | gains the binding model: "each `Y` binding every act its question names and nothing it does not" (R2) | #12, #553 |
| head | "**Target:** a d-work" | kept | Target | unchanged | #12 |
| Bound. | "Who may ratify — Rule-2 (applied by reference…)" | kept | Boundaries 1 | now also names Rule-2 as owner of the never-carried list | #12, #290 |
| Bound. | "Which zone a change belongs to — Rule-1." | merged | Boundaries 2 | merged with pointers to Rules 7, 15, 16 (R3: neighbours named, not restated) | #12 |
| Bound. | "Bare `Y`/`N` disposals: they answer a counter-prompt and open nothing." | merged | Scope, second bullet | not a boundary but a scope fact; already stated in Scope | #12 |
| Bound. | "What the agent may do on the live host — Rule-8…" | kept | Boundaries 3 | unchanged | E5 |
| Bound. | "Destructive-action counter-prompts: always one-per-question, never batched — Rule-8." | merged | Boundaries 3 | one bullet for Rule-8, now "never batched and never carried" | #106 |
| Bound. | "Release counter-prompts: one-per-question by default; a release-specific batch…" | merged | Boundaries 4 | stated as Rule-11's (question, batch form, release gate) | #106, #545 |
| Bound. | "How another agent frames a proposal to its own operator — that system's Rule-10…" | kept | Boundaries 5 | unchanged | #34 |
| Bound. | (new) "The machine step by step — … the d-work play-book" | moved | Boundaries 6 ← Ledger "machine whole" bullet | a pointer is a boundary | #309 |
| Cond. | "The operator sends a prompt (text, including text accompanying a disposal)." | kept | Conditions 1 | merged with "answers a counter-prompt" (a trigger that was implicit) | #12 |
| Cond. | "The agent is about to mutate the repo for a d-work (plan gate)." | merged | Conditions 2 | merged with the Done trigger | #12, E3 |
| Cond. | "The agent believes a d-work is done (completion counter-prompt)." | merged | Conditions 2 | as above | #12 |
| Cond. | "A session starts (ledger report)." | kept | Conditions 5 | unchanged | E1 |
| Cond. | "A PR is opened or edited (`prs.py`); a commit is pushed to `main` (`rows.py`…)" | kept | Conditions 6 | unchanged | #151, #191 |
| Cond. | "The operator's reply to a counter-prompt is a new prompt… `on-ignore`…" | kept | Conditions 7 | unchanged | #17 |
| Cond. | "A message from another agent — a peer session… — proposes work" | kept | Conditions 4 | the parenthetical examples dropped | #34 |
| Cond. | "The agent opens a row while executing another, inside the mandate scope…" | kept | Conditions 3 | now "under the plan-`Y` that carries it", which covers a play-book's prescribed rows (#574 rev 2) | #290, #574 |
| Cond. | "A `d-work` starts with an operator prompt and terminates only when… `Y/N: Done with {d-work}?`… Any other response leaves it incomplete" | merged | Scope, first bullet | the lifecycle sentence belongs with what opens a row | #12 |
| Scope | "Every operator prompt opens a d-work, with one exemption: … reads the corpus… (#492)" | kept | Scope, first bullet | shortened; DMC `read-only-answer` names kept | #492 |
| Scope | "A new prompt while a d-work is open suspends it and opens another. d-works stack." | kept | Scope, first bullet | unchanged | #12 (attack 5) |
| Scope | "A **bare** disposal response… opens nothing. Text accompanying a disposal is a prompt…" | kept | Scope, second bullet | now with the disposition that opens a row (intake `Y`, `Y backlog`) named beside it | #12, #34 |
| Scope | "A third thing opens a row… **accretion**… An **accreted row** is…" | kept | Scope, third bullet | unchanged in substance | #290 |
| Scope | "Under the preference `accretion: implicit`… a row the authorized plan already describes, inside the mandate scope… born `open`… its Done rides the mandate's done-`Y`" | merged | Scope, third bullet + *What a `Y` binds* + Plan (carried row) | rewritten as "a plan-`Y` carries…"; absorbs #574 rev 2 (a play-book's prescribed rows) | #290, #574 |
| Scope | "It opens no d-work in the sense of this section's first bullet… nothing stacks. Under `accretion: explicit`…" | kept | Scope, third bullet | unchanged | #290 |
| Scope | "The terms are the countersign model's… mandate… delegate edge… escalate edge… mode lifecycle" | kept | Scope, paragraph after bullets | terms kept for the vocabulary guard | #290, #381 |
| Scope | "Which acts are never accretable… is Rule-2's list (Binding of approval)" | moved → Rule-2 | *What a `Y` binds*, "Never carried" | one statement of the never-carried list, by pointer to Rule-2 (R5) | #290 |
| Scope | "A subagent's actions are the agent's actions… Subagents never write a row… (E7, #107)" | kept | Scope, last paragraph | shortened; every prohibition kept | E7, #107 |
| Ans. | "Three answers to a counter-prompt, not two — the countersign model's **answer grammar**…" | kept | Answer grammar intro | unchanged | #290, #381 |
| Ans. | "`Y` — the disposition asked for is given, bound as Rule-2's Binding…" | kept | Answer grammar, `Y` | now points to *What a `Y` binds* | #290 |
| Ans. | "`N`, bare — nothing is authorized…" | kept | Answer grammar | unchanged | #290 |
| Ans. | "`N` with text — **amend**… same proposal revised… something else… authorizes nothing until…" | kept | Answer grammar | shortened; DMC `amend-scope` names kept | #290 |
| Ans. | "An answer is read by its meaning, never by its case or spelling…" | kept | Answer grammar, paragraph | unchanged in substance | #553 |
| Ans. | "A `Y` with text is a `Y` plus a prompt… Silence is not consent…" | kept | Answer grammar, paragraph | unchanged | #290 |
| Ans. | "Until 2026-10-14 `amend` had no name here… revision 5." | dropped | → record (history) | history, not an obligation | #290 |
| Plan | "The agent's first substantive reply to a prompt is a plan, stored first as a plan file… `Y/N: proceed with #<id> as planned?`" | kept | Plan 1 | gains the definition of done as the plan's first part (#574 rev 1) | #12, #290, #574 |
| Plan | "`Y` authorizes the mutation and binds every PR of the d-work to the plan. Work that departs… new plan… Any other response…" | kept | Plan 2 | unchanged | #12 |
| Plan | "An **execution detail** is not a departure: …(`dyad/dmc/plan-departure.jsonld`, #555)" | kept | Plan 3 | shortened; every condition kept | #555 |
| Plan | "No exemptions, with one: the row the plan-`Y` has already authorized…" | kept | Plan 2 | the exemption now reads "a row the plan-`Y` carries" | #12 (G6), #290 |
| Plan | "**Mandate scope.** A plan that intends to accrete states it: a *rule*… a *ceiling*…" | kept | Plan 4 | unchanged in substance | #290 |
| Plan | "A plan that states no mandate scope accretes nothing, however much it describes" | merged | Plan 4 | absorbs #574 rev 2: "…beyond the rows a play-book it runs prescribes, whose rule is that step's class and whose ceiling the play-book's own count" | #290, #574 |
| Plan | "a row the stated rule does not cover, or the row after the stated ceiling… a new plan" | kept | Plan 4; *What a `Y` binds* | unchanged | #290 |
| Plan | "How large a ceiling may be is the operator's number, never this Rule's." | merged | Plan 4 | "both the operator's to read and to refuse" | #290 |
| Plan | (new) carried row born `open` or `backlog` | — | Plan 5 | absorbs #574 rev 2 (F3: its own work waits for a prompt) | #574 |
| Plan | "A prompt that opens a new body of work is planned by the craft play-book…" | kept | Plan 6 | test-pinned strings kept | #165 |
| Plan | "The plan-`Y` is disposition (2) of the operator's model (audit 2026-09-12, disposition chain)…" | dropped | → record | history; the two questions are now stated in *What a `Y` binds* | audit 2026-09-12 |
| Ledger | "The ledger is the row-file store `agent-corpus/d-work/rows/`… `state` is … defined in the vocabulary" | kept | Ledger 1 | unchanged | #12, #309 |
| Ledger | "`open` — started…" | kept | Ledger 1 | unchanged | #12 |
| Ledger | "`planned` — the plan file is authorized…" | kept | Ledger 1 | unchanged | Rule-15 |
| Ledger | "`blocked` — the operator disposed a deferral…" | kept | Ledger 1 | unchanged | #12 |
| Ledger | "`backlog` — opened by an operator disposition… Becomes `open`… or `archived`…" | kept | Ledger 1 | gains the carried route (#574 rev 2) | #290, #574 |
| Ledger | "`done` — the operator answered `Y`… *and* every merge… state guard reads that interval…" | kept | Ledger 1 | unchanged | #202 |
| Ledger | "`archived` — retired from the working board by an operator disposition naming the row(s)… terminal… reached from `done` or `backlog`" | kept | Ledger 1 | unchanged | #37, #290 |
| Ledger | "Nothing moves: its row, plan and provenance stay where they are (Rule-16 store; Rule-20 references)." | kept | Ledger 1 | unchanged | #290 |
| Ledger | "The agent never archives on its own judgment; `dyad dwork state <id> archived` is clerical…" | kept | Ledger 1 | unchanged | #37 |
| Ledger | "The question that names them is the **retirement form**, `Y/N: archive #a, #b, … #k?`…" | merged | Ledger 1 | absorbs #574 rev 3: the Done question's `(retires …)` clause is the first route; the retirement form remains "for rows no Done covers" | #290, #574 |
| Ledger | "A `Y` archives exactly the named rows… It is not a plan or Done batch… pending queue" | kept | Ledger 1; Batch disposition 3 | unchanged | #290 |
| Ledger | "The machine whole — … `dyadlib.INPUTS`… d-work play-book… read here, never a Rule (#309)." | moved → play-book | Boundaries 6 | a pointer to the play-book; test-pinned strings kept | #309 |
| Ledger | "The agent may decompose a d-work into child rows… The parent's counter-prompt is asked only when…" | kept | Ledger 2 | DMC `parent-askable` names kept | #290 |
| Ledger | "…`backlog` is admitted for the reason `blocked` already was… one parent… 23 `backlog` children…" | merged | Ledger 2 | reason kept in one clause; the instance count dropped (history) | #290 |
| Ledger | "The agent appends a row when a d-work starts, records the operator's `Y`… sets `done` only once…" | merged | Completion counter-prompt (Record, Close) | stated once, in the three acts | #202 |
| Ledger | "Ledger-only commits (touching nothing outside `agent-corpus/d-work/`…) are clerical… `rows.py` fails any direct commit…" | kept | Ledger 4; Mechanisms 2 | the fence's half moved to Mechanisms | #12 (attack 2), #191 |
| Ledger | "Events-only commits are clerical in the same way…" | kept | Ledger 4 | the range-reading clause moved to Mechanisms (plan gate) | #438 |
| Ledger | "One commit stays one zone (Rule-1), so a commit touching both… is neither class." | kept | Ledger 4 | DMC `direct-commit-class` names kept | #438 |
| Ledger | "Monitoring is therefore no d-work… (#438). The scheduled sweep… is such a check… (#564)." | kept | Ledger 4 | unchanged | #438, #564 |
| Ledger | "The `disposed` column records every disposition… `<date> <Y\|N> <plan\|done\|merge #n\|reason>`… (D4)… not backfilled." | kept | Ledger 3 | unchanged | D4, #46 |
| Ledger | "An accreted row's first entry is the mandate's own plan-`Y`, written `<date> Y plan (mandate #<id>)`… record's entry 1… note `mandate #<id>, <date>`" | merged | Ledger 3 | one sentence covers every carried row: accreted `Y plan (mandate #<id>)`, carried backlog `Y backlog (mandate #<id>)` (#574 rev 2), retired `Y archive (done #<id>)` (#574 rev 3) | #290, #574 |
| Ledger | "A row may also carry the optional field `mode`…" | kept | Ledger 3 | gains "a carried `backlog` row carries none" (#574 rev 2, F3) | #290, #574 |
| Ledger | "At session start the agent reads the ledger and reports every row that is not `done`… sentinel… (E1)" | kept | Ledger 5 | unchanged | E1 |
| Ledger | "The agent also touches its own presence file and reads every other session's (Rule-16)…" | kept | Ledger 5 | unchanged | #185 |
| Ledger | "Under `organization: m4`… the home — titled cos — reads the board of programs, a unit with a function… (`secretary`, `cos-board`)…" | moved → cabinet Operating Guide | Ledger 5 | the Rule keeps "reads its unit's board"; which board each role reads is the organization craft's | #369 C7, #379, #419, #560 |
| Ledger | "PR bodies… cite `d-work #<id>`; the guard resolves each id… `open`, `planned` or `blocked`… `Y plan`… (E3)" | kept | Ledger 6 | DMC `plan-gate` names kept | E3, #23 |
| Ledger | "The phrase is a claim of work… cross-reference other rows as plain `#<id>` (#23)." | kept | Ledger 6 | unchanged | #23 |
| Ledger | "A ledger-only range claims no d-work… the gate skips it… (#191)" | merged | Mechanisms 3 | stated once, with the plan gate | #191 |
| Mech. | "The fence keeps the Done order… on a direct commit… ledger-only branch… merge commit's resolution…" | kept | Mechanisms 2 | unchanged in substance | #202 |
| Mech. | "one commit may not both record a `Y done`… (`rows.done_order_problems`)" | kept | Mechanisms 2 | unchanged | #202 |
| Mech. | "the commit that does set `done` must find a `Y done`… (`rows.landing_problems`)… cross-clone denial of service (#321)" | kept | Mechanisms 2 | the rationale clause shortened | #202, #321 |
| Mech. | "the interval… one warning per row (`rows.done_recorded_not_closed`)…" | kept | Mechanisms 2 | unchanged | #202 |
| Mech. | "Whether a merge ran is not decidable from git… only the closing commit is fenced… (#202)" | kept | Mechanisms 2 | shortened | #202 |
| Mech. | "The same fence keeps the trace clause… (`rows.trace_problems`)… exempts a mandate close… `package.py trace_refusal`… `land <instance>/d-work/traces/<id>.md` (#465)" | kept | Mechanisms 2 | every name kept | #465 |
| Mech. | "Rule-3 owns the row guard `rows.py` (the main fence) and the PR guard `prs.py` (the plan gate)… agent zone…" | kept | Mechanisms 1 | unchanged | #151 |
| Mech. | "their workflow wrapper (`.github/workflows/dyad-package.yml`… `rule-3 fence (push range)`…)" | kept | Mechanisms 1 | names "corroboration" (vocabulary `used by` 3) | #477, #564 |
| Mech. | "Changing a guard is an agent-zone PR, changing the wrapper an infra-zone PR…" | kept | Mechanisms 1 | unchanged | #151 |
| Mech. | "The plan gate is enforced before a push by the kernel-only path… the wrapper corroborates on `main` only (#168)." | kept | Mechanisms 1, 3 | unchanged | #168 |
| Mech. | "A state guard beside them checks the trace store… `traces.py`… `trace.check_store` (#227)" | kept | Mechanisms 2 | unchanged | #227 |
| Mech. | "the incident log's check stays a script run by the suite until #170…" | kept | Mechanisms 3 | shortened | #170 |
| Mech. | "A range that touches only `<instance>/d-work/` is exempt from the plan gate (`prs.ledger_only`, #191)… commit by commit with rename detection off…" | kept | Mechanisms 3 | unchanged in substance | #191 |
| Mech. | "…so a branch that ever touched anything else — a move into the ledger, a reverted edit… — is not ledger-only." | merged | Mechanisms 3 | follows from "every non-merge commit"; examples dropped | #191 |
| Mech. | "Before the exemption, a session fenced off a direct push… moved uncited ledger commits around the hook…" | dropped | → record | history | #191, #23 |
| Mech. | "The exemption rests on `main` admitting the same commits, so the fence judges each commit… each of its merge commits against both parents…" | kept | Mechanisms 3 | unchanged | #191 |
| Mech. | "The PR guard (`prs.py`) skips an events-only range (`dyadlib.events_only`…)… a range mixing… is gated; …events guard's (`crafts/sysadmin/guards/events.py`, `sysadmin/events`)" | kept | Mechanisms 3 | unchanged | #438 |
| Mech. | "Rule-2 references `rows.py` by name; it does not own it." | kept | Mechanisms 1 | unchanged | #290 (Rule-2 A1) |
| Compl. | "The done-`Y` is the operator's verification… before merge, so `main` never carries unverified output." | kept | Completion 1 | unchanged | #68, #202 |
| Compl. | "Always the last line of the agent's reply that believes the d-work is done." | kept | Completion 1 | unchanged | #12 |
| Compl. | "The reply that asks does not merge. The reply that receives the done-`Y` records it, merges, and only then closes the row — three acts…" | kept | Completion, Record, merge, Close | unchanged | #68, #202 |
| Compl. | "(1) **Record.** … `-d 'Y done (merges PR #a at <head-a>)'`. That entry *is* the ledger's record…" | kept | Completion, Record | the entry gains `retires #r, #s` (#574 rev 3) | #202, #574 |
| Compl. | "(2) **Merge**, as clerical execution of it." | kept | Completion, Merge | unchanged | #202 |
| Compl. | "(3) **Close.** The merge and the close may be executed by the **automaton**… `DYAD_AUTOMATON`… decides nothing…" | kept | Completion, The automaton | own bullet; gains "archives each retired row; a retired row neither `backlog` nor `done` is a refusal" (#574 rev 3, G5) | #556, #574 |
| Compl. | "A second, dispositionless ledger commit sets `done`, once git shows the head the **operative** entry names…" | kept | Completion, Close | gains "and archives each retired row" (#574 rev 3) | #202, #574 |
| Compl. | "…where a hosting squashes or rebases, the entry records `landed <sha>` instead." | kept | Completion, Close | unchanged | #202 |
| Compl. | "A done-`Y` that names no merge is recorded `done` at once…" | kept | Completion, Close | DMC `done-order` "at once" kept | #202 |
| Compl. | "A merge before the `Y` is self-ratification (Rule-2) and an incident… (#47, #58, #67)" | kept | Completion 6 | unchanged | #47, #58, #67, #68 |
| Compl. | "`done` written while the head… is not yet on `main` is the converse breach, and the fence refuses…" | kept | Completion 6 | unchanged | #202 |
| Compl. | "What the fence can decide is that head's reachability, not that PR #n merged…" | merged | Mechanisms 2 | stated once with the fence | #202 |
| Compl. | "The state is what the merge moves, because `done` is terminal… the row is still `open` or `planned`… (not `blocked`…)" | kept | Completion 6 | shortened; "never `blocked`" kept | #202 |
| Compl. | "What the interval does not do is re-bind the `Y`: a resolution that changes a head voids it…" | kept | Completion 6 | unchanged | #202 |
| Compl. | "The completion reply carries the evidence the verification needs (E8): every PR… checks… host action… accreted… escalation… not delivered… departure… could not verify" | kept | Completion, Evidence | opens with the definition of done, quoted, and the report answering it (#574 rev 1); gains retired rows with state and ground (#574 rev 3) and each child's state (from Ledger) | E8, #125, #290, #574 |
| Compl. | "An omission is a breach of this Rule, not a style choice." | kept | Completion, Evidence | unchanged | E8 |
| Compl. | "When the preference `dwork-trace`… `always`… `on-demand`… preview… `<instance>/d-work/traces/<id>.md`… A trace with no transcript is still cited…" | kept | Completion, Trace | test-pinned strings kept; gains the mandate-close exemption, from Mechanisms (DMC `trace-in-evidence`) | #213, #215, #465 |
| Compl. | "Form: `Y/N: Done with #<ledger id> <title>?`… A d-work that accreted rows names them… a row left out… breach" | merged | Completion, Form | one parenthetical, in the order accreted, retires, merges (#574 rev 3) | #12, #290, #574 |
| Compl. | "When `merge-disposition` is `with-done`… `(merges PR #a, #b)`… With an accreted set the one clause carries both…" | merged | Completion, Form | same parenthetical | #41, #290 |
| Compl. | (new) "A row is named under `retires` only while it is `backlog` or `done`…" | — | Completion, Form | #574 rev 3 (G2) | #574 |
| Compl. | "A Done question the home… relays to the operator for a solo… `relay-form`… `evidence-sha256`… brief form…" | kept | Completion, A relayed Done | shortened | #424, #476, #553 |
| Batch | "Preference `batch-disposition-mode`… `off`… `on-ignore`… `always`…" | kept | Batch 1 | DMC `batch-engagement` names kept | #17 |
| Batch | "Release counter-prompts have their own, narrower batch form, owned by Rule-11…" | moved → Rule-11 | Boundaries 4; Batch 2 | Rule-11 owns it; one clause here says it never enters the queue | #106 |
| Batch | "Nor is a mandate a batch… neither plan-ready nor done-ready items (the mandate form, below)." | merged | Batch 2 | merged with the mandate-form paragraph | #290 |
| Batch | "Once engaged, the agent holds a **pending queue**: every plan-ready… done-ready…" | kept | Batch 1 | unchanged | #17 |
| Batch | "Both counts are reported at the end of every reply… visible within one turn." | kept | Batch 1 | unchanged | #17 |
| Batch | "The queue is recorded, not conversational… **board store**… **hop**…" | kept | Batch 3 | shortened | #535 |
| Batch | "The board is written **write-ahead**…" | kept | Batch 3 | shortened | #535 |
| Batch | "Its guard checks the files' shape only; whether an entry is true… is inference (#535)." | kept | Batch 3 | "checks shape only" | #535 |
| Batch | "What a unit reports and what the home relays… travel by the **inbox**… read at the start of every turn" | kept | Batch 4 | unchanged | #536 |
| Batch | "a message to a session is at most a doorbell saying one waits, never the carrier…" | kept | Batch 4 | gains #584's sentence: an actionable post is followed by a doorbell unless the receiver cannot receive one, in which case it polls (`dyad/dmc/message-route.jsonld`) | #536, #584 |
| Batch | "The inbox carries information, never authority… verbatim, citing the provenance entry…" | kept | Batch 4 | unchanged | #536 |
| Batch | "The batch forms replace the single forms above, one kind at a time…" | kept | Batch 2 | unchanged | #17 |
| Batch | "`Y/N: proceed with #a, #b, #c as planned?` — authorizes the mutation of every named d-work…" | kept | Batch 2 | unchanged | #17 |
| Batch | "`Y/N: Done with #a <title-a>, #b <title-b> (merges PR #w, #x, #y)?` — … full completion evidence… a d-work not yet done-ready waits" | kept | Batch 2 | gains each d-work's accreted and retired rows in its own clause; "waits for a later batch" follows from the done-ready queue | #17, #290, #574 |
| Batch | "Beside the batch forms, and never one of them, is the **mandate form**… two questions whatever the set's size… acts… questions" | kept | Batch 2 | the term is kept (the cabinet Guide cites it); the explanation is now *What a `Y` binds* | #290 |
| Batch | "The queue drains as its items are named… `on-ignore`… `always` it never lapses." | kept | Batch 1 | unchanged | #17 |
| Batch | "Each disposed row's ledger entry names the full set… `(batch #a,#b,#c)`… every PR with the head…" | kept | Batch 2 | unchanged | #17, #202 |
| Batch | "Provenance (Rule-7) is unaffected: the operator's one `Y` is written as the same entry into every named d-work's own record." | kept | Batch 2 | unchanged | #17, #164 |
| Intake | "A message from another agent opens no d-work: only an operator prompt or disposition does…" | kept | Intake | unchanged | #34 |
| Intake | "What a message may carry is an intake… the operator's `Y` opens the row… `<system>-<id>`" | kept | Intake | unchanged | #34 |
| Intake | "A **defect** is admissible as an observation with evidence… (Rule-7 property 4)." | kept | Intake | "a fix's shape may be suggested" dropped as redundant | #34 |
| Intake | "An **enhancement** is admissible only with its operator behind it… `relayed via <session>`… An agent's own idea…" | kept | Intake | shortened | #34, #253 |
| Intake | "Anything else is returned to the sender with the missing shape named…" | kept | Intake | DMC `intake-shape` names kept | #34 |
| Intake | "The operator may still open a row for it by prompting…" | kept | Intake | unchanged | #34 |
| Incid. | "An incident is any action taken or outcome reached that the plan did not name…" | kept | Incidents 1 | DMC `incident` names kept | E9 |
| Incid. | "Reported in the reply where it occurred or in the completion reply, whichever comes first." | kept | Incidents 1 | unchanged | E9 |
| Incid. | "Recorded: as an attack… otherwise as a row in `agent-corpus/audits/INCIDENTS.md`…" | kept | Incidents 1 | DMC `incident-record-home` names kept | E9 |
| Incid. | "If the plan changes as a result, a fresh plan-`Y` precedes any further mutation. (E9)" | kept | Incidents 1 | unchanged | E9 |
| Incid. | "Under `concise-mode: on`… the record… is written during the turn…" | kept | Incidents 2 | shortened | #113 |
| Incid. | "Periodically the incident log is worked whole… incident-hardening play-book…" | kept | Incidents 3 | the `backlog` fence row is "carried under the plan-`Y` that runs the exercise, never asked again" (#574 rev 2) | #137, #116, #128, #135, #574 |
| Ratif. | "Answering `Y` to a plan counter-prompt (mutation authorization)." | kept | Ratification events 1 | gains "with every row the plan carries" | #12 |
| Ratif. | "Answering `Y` to a d-work completion counter-prompt (intent verification; under `with-done`… merges)." | kept | Ratification events 2 | gains accreted and retired rows | #12, #41, #574 |
| Ratif. | (new) "Answering `Y` to the retirement form." | — | Ratification events 3 | the play-book already said so ("the done-`Y` and the retirement form are ratification events"); now the Rule declares it, so Rule-2 applies by reference | #290 |
| Prov. | "Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-3-d-work.md`." | kept | Provenance | the one line R4 keeps, with the refactor note | #12 |
| Prov. | Batch disposition added 2026-09-15 (#17) | moved → record | `dyad/falsification/rules/rule-3-d-work.md` (history) | R4 | #17 |
| Prov. | Intake added 2026-09-16 (#34) | moved → record | as above | R4 | #34 |
| Prov. | `archived` state added 2026-09-16 (#37) | moved → record | as above | R4 | #37 |
| Prov. | Completion clause gains the merge-sequence bullet 2026-09-18 (#68) | moved → record | as above | R4 | #68 |
| Prov. | Boundaries and Batch disposition reworded 2026-09-21 (#106) | moved → record | as above | R4 | #106 |
| Prov. | Incidents gains the `concise-mode` bullet 2026-09-22 (#113) | moved → record | as above | R4 | #113 |
| Prov. | Incidents gains the periodic-exercise bullet 2026-09-23 (#137) | moved → record | as above | R4 | #137 |
| Prov. | Ledger and Mechanisms gain the ledger-only exemption 2026-09-29 (#191) | moved → record | as above | R4 | #191 |
| Prov. | Completion gains the d-work trace bullet 2026-10-05 (#213, #215) | moved → record | as above | R4 | #213, #215 |
| Prov. | Mechanisms gains the trace guard 2026-10-06 (#227) | moved → record | as above | R4 | #227 |
| Prov. | Accretion under a mandate and Answer grammar 2026-10-14 (#290) | moved → record | as above | R4 | #290 |
| Prov. | Three-act Done order 2026-10-15 (#202) | moved → record | as above | R4 | #202 |
| Prov. | The d-work play-book 2026-10-15 (#309) | moved → record | as above | R4 | #309 |
| Prov. | Countersign model by core path 2026-10-22 (#381) | moved → record | as above | R4 | #381, #369 |
| Prov. | Organization sentence 2026-10-22 (#379) | moved → record | as above | R4 | #379, #369 |
| Prov. | Cos and secretary, the cabinet path 2026-10-25 (#419) | moved → record | as above | R4 | #419, #417 |
| Prov. | Relayed-Done sentence 2026-10-25 (#424) | moved → record | as above | R4 | #424 |
| Prov. | Events-only commit 2026-10-25 (#438) | moved → record | as above | R4 | #438 |
| Prov. | `dyad-package.yml` in place of `dyad-d-work.yml` 2026-10-26 (#477) | moved → record | as above | R4 | #477, #473 |
| Prov. | Fence's trace clause 2026-10-26 (#465) | moved → record | as above | R4 | #465 |
| Prov. | Relayed Done cites sha256 and brief form 2026-10-26 (#476) | moved → record | as above | R4 | #476, #473 |
| Prov. | Read-only answer 2026-10-27 (#492) | moved → record | as above | R4 | #492, #490, #491 |
| Prov. | Pending queue in the board store 2026-11-02 (#535) | moved → record | as above | R4 | #535 |
| Prov. | The inbox 2026-11-02 (#536) | moved → record | as above | R4 | #536 |
| Prov. | The execution detail 2026-11-02 (#555) | moved → record | as above | R4 | #555 |
| Prov. | Dyad-native terms 2026-11-02 (#553) | moved → record | as above (its record is `rule-6-vocabulary.md`) | R4 | #553 |
| Prov. | The automaton executes merge and close 2026-11-02 (#556) | moved → record | as above | R4 | #556 |
| Prov. | Organization craft's roles 2026-11-02 (#560) | moved → record | as above (record `rule-6-vocabulary.md`) | R4 | #560 |
| Prov. | Scheduled sweep and corroboration 2026-11-03 (#564) | moved → record | as above (record `rule-14-system-infrastructure.md`) | R4 | #564 |
| Set | "Set: System Requirements." | kept | last line | unchanged | #160 |

## Summary

**Length** (`wc -w`): today's Rule-3 has **7,343** words, its Provenance 1,515 of them. The new Rule-3 has
**4,397** words, its Provenance 79. That is 60% of today's length, or 75% of today's text without its Provenance
(5,831 words; Provenance 1,510 by this count, 1,515 in plan #585). It also absorbs #574 (revisions 1–3) and #584.

**Fates** (rows above, excluding the 3 "new" rows marked —):

| fate | rows |
|---|---|
| kept | 118 |
| merged | 20 |
| moved | 34: 29 Provenance amendments to the record; 5 to Rule-2, Rule-11, the d-work play-book (counted at both ends) and the cabinet Operating Guide |
| dropped | 3, all history: the `amend` naming note, the disposition (1)/(2) note and the pre-#191 bypass story. The instance's 23-children count went with its merged row. |

No obligation is dropped. Each dropped row is history that stays in the falsification record.

**Fixed points of R5, and where each lives in the new text:**

| fixed point | where |
|---|---|
| the operator disposes every ratification | Boundaries 1 (Rule-2 by reference); *Answer grammar* (silence is not consent); *Ratification events* (three events, Rule-2 by reference); Scope ("never the agent's own finding"); Ledger `archived` ("the agent never archives on its own judgment") |
| every carried act was named in a question the operator answered | *What a `Y` binds*, paragraph 2 ("A carried act was named in a question the operator answered, or it is not carried"); Plan 4 (rule and ceiling read before the `Y`; a play-book's own count); Completion Form (the `Y` binds the sets as listed; a row left out is left out) |
| the never-carried list is unchanged | *What a `Y` binds*, "**Never carried** … is Rule-2's list". The list is named by pointer to Rule-2, which keeps it; the release-gate exception is Rule-2's own (#545) |
| done follows the merge | Completion, "Record, merge, Close" and the bullet after it; Ledger `done`; Mechanisms 2 (the fence: `done_order_problems`, `landing_problems`, `done_recorded_not_closed`) |

**Vocabulary guard: terms whose `used by` lists 3.** All 64 rows of the `572-playbook` vocabulary were checked against
the new text, case-insensitively, with emphasis stripped and across line breaks. This is the guard's own
normalization (`vocabulary.py`).
- **Would have been orphaned in the first draft:** `batch counter-prompt` and `corroboration`. Both are now named:
  "A batch counter-prompt binds…" in *What a `Y` binds*, and "re-run after the merge by corroboration" in
  Mechanisms 1.
- **Orphaned in the final text:** none.
- `definition of done` (used by 3 15 on this branch) is present.
- **New words the vocabulary may need:**
  - "carried" (a carried row or act) is used in prose but is not a vocabulary row. Rule-6 asks for a row when a new
    term is introduced; see notes.md, Q2.
  - "doorbell" is used but not defined, as the brief requires. #584 adds its row.

**Headings.** No heading was renamed in a way that breaks a citation:
- `## Scope` became `## Scope (what opens a row)`. The name every citation uses ("Rule-3 Scope", "Rule-3, Scope") is
  unchanged, as with `## Plan (mutation authorization)`.
- `## What a \`Y\` binds` is new.
- Every other heading is kept verbatim: Answer grammar, Plan (mutation authorization), Ledger, Mechanisms, Completion
  counter-prompt (intent verification), Batch disposition, Intake (work proposed by another agent), Incidents,
  Ratification events, Provenance.

So nothing needs re-pointing for a renamed heading. notes.md lists the citations that point at content which moved
between headings or out of the Rule.
