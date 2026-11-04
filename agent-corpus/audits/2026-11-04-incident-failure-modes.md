# Incident audit by failure mode — 2026-11-04 (full re-derivation)

*Audit of `agent-corpus/audits/INCIDENTS.md` as of `origin/main` `eeea31fc`. d-work #571 (v1.0 H1, accreted under
mandate #570), seat audit-e73be78c. Play-book `dyad/playbooks/incident-hardening.md`, phases 0, 1, 2 and 4; phase 3
(execute) is each fence owner's row. Detects and proposes; disposes nothing and opens no row (audit charter, #433).
Supersedes the 2026-10-10 index (`2026-10-10-incident-failure-modes.md`) as the current one; that index and its 25
mode records stay where they are, never moved or renumbered.*

**Ledger:** `agent-corpus/audits/INCIDENTS.md` · **covered through:** 252 rows, latest 2026-11-03

## Resolved incidents (definition of done)

The operator's definition of done for #571 (plan #570 revision 4): "a report showing the number of resolved INCIDENTS"
(by mode, with the fence, row or impossibility per mode).

**Every one of the 252 incidents is in exactly one mode, and every mode is closed one of three ways:**

| closed by | modes | incidents |
|---|---|---|
| a fence shipped on this kernel | 20 | 84 |
| an impossibility on this kernel, its Rule named | 11 | 40 |
| **resolved now** | **31** | **124** |
| a fence row proposed (R-a…R-h), not yet built | 20 | 128 |
| total | 51 | 252 |

124 of 252 are resolved today. The other 128 resolve as R-a…R-h are opened and built. Until then each is named, by
mode, to the row that would fence it. Modes 21 and 33 are mixed (one face fenced, a residue impossible) and are counted
as fenced.

| mode | incidents | closed by | fence, row or impossibility |
|---|---|---|---|
| 01 | 7 | row (proposed) | R-g |
| 02 | 9 | row (proposed) | R-h |
| 03 | 4 | row (proposed) | R-c |
| 04 | 6 | fenced | `dwork new --land` at the call; `rows.check_id_collisions`, `contiguity_problems` at push |
| 05 | 11 | impossible | Rule-9/Rule-10 Enforcement "inference only"; Rule-7 keeps the transcript out of the corpus |
| 06 | 20 | row (proposed) | R-g |
| 07 | 7 | row (proposed) | R-e |
| 08 | 5 | impossible | Rule-14 p3 (kernel-only path); a harness hook is Operator-side (Rule-1 Boundaries) |
| 09 | 12 | row (proposed) | R-a |
| 10 | 4 | fenced | `rows.check_commit` (`disposed_problems`) at push; `--land`, `--check` at the call |
| 11 | 4 | fenced | `dwork new|state --said` refusals at the call; `provenance.check_transaction` at push |
| 12 | 8 | row (proposed) | R-d |
| 13 | 5 | fenced | `dyad merge` refuses at merge (#532); `merges.py` warns at push (#541) |
| 14 | 2 | fenced | `rows.done_head_refusals` at push |
| 15 | 6 | fenced | `rows.done_order_problems`, `landing_problems` at push; `dwork state` refusals at the call |
| 16 | 7 | row (proposed) | R-f |
| 17 | 6 | row (proposed) | R-c |
| 18 | 8 | row (proposed) | R-c |
| 19 | 6 | row (proposed) | R-g |
| 20 | 5 | fenced | `prs.CITE` and `agent/references` at push |
| 21 | 7 | fenced | rows 7, 98, 197, 232: the verbs read the remote and their own exit; rows 8, 124, 187 (filtering own tool output) impossible, Rule-14 p2 |
| 22 | 3 | impossible | Rule-14 p3; harness hook Operator-side |
| 23 | 2 | impossible | Rule-14 p3; harness hook Operator-side |
| 24 | 2 | fenced | the hooks exec `dyad-python <guard>` (no exec bit needed); call sites pinned by the suite at push |
| 25 | 2 | impossible | Rule-14 p3; harness hook Operator-side; Rule-1 Enforcement already says never bypass |
| 26 | 6 | fenced | `suite_env` at spawn; `checkout_snapshot` at suite end |
| 27 | 5 | row (proposed) | R-d |
| 28 | 3 | row (proposed) | R-a |
| 29 | 12 | fenced | `sessions.touch` keys claims from the holder at the call (#350, #567) |
| 30 | 6 | impossible | Rule-10 Enforcement "inference only"; Rule-14 p3 |
| 31 | 2 | row (proposed) | R-c |
| 32 | 4 | impossible | Rule-14 p3; harness hook Operator-side |
| 33 | 8 | fenced | fenced per property met (interpreter, clone depth/tags, CI git, hosting account/draft); the next unknown property impossible, Rule-14 p4 |
| 34 | 2 | impossible | Rule-14 p4 (The World); damage bounded by Rule-2 Binding local merge (#138) |
| 35 | 3 | row (proposed) | R-f |
| 36 | 2 | fenced | `run_suite` temp-root sweep at every suite run |
| 37 | 3 | row (proposed) | R-c |
| 38 | 2 | fenced | pre-push gate runs the full guard set at push |
| 39 | 2 | fenced | `dyadlib.split_cells` at parse |
| 40 | 7 | row (proposed) | R-h |
| 41 | 6 | row (proposed) | R-b |
| 42 | 4 | fenced | `rows.refs_shape_problems` at push |
| 43 | 2 | fenced | `dwork state --check` at the call |
| 44 | 2 | fenced | `release.py` publishes from the rows push; sweep `released` health detects |
| 45 | 3 | impossible | Rule-3 Completion: the reply is chat; the evidence sha256 fences only what it cites (Rule-2 Binding) |
| 46 | 3 | row (proposed) | R-e |
| 47 | 2 | fenced | `automaton.sweep_ci` twice daily; `automaton.corroborate` at each landed cut |
| 48 | 1 | impossible | Rule-18 (ops script form) covers delivery; the chat print itself is read by no mechanism |
| 49 | 2 | row (proposed) | R-b |
| 50 | 1 | fenced | `privatecite.check_push` at push, fail-closed |
| 51 | 1 | impossible | Rule-14 p4: the 403 lies in the hosting; mechanism not established by the cells |

## Phase 0 — survey
`LEDGER=agent-corpus/audits/INCIDENTS.md dyad runbook run incident-hardening survey`, event
`incident-hardening-20261104T020220Z-survey` (landed on `main`, events-only). Live count 252 against the watermark 233:
19 rows (234–252) ungrouped. #570's prompt ("re-run over all 252") was read as the Operator's word for a full
re-derivation, the play-book's second trigger, which also answers the question the 2026-10-24 delta left open.

## Method
Two subagents each derived modes over all 252 rows, both forbidden the index, the mode records and
`agent-corpus/falsification/`, both reporting the sentinel first:
- **View 1** read `cause` first and kept small modes apart where their fences differ: **62 modes**.
- **View 2** worked bottom-up with the one-sentence test (two mechanisms are one mode only if one sentence names a
  change that stops both at one moment): **51 modes**.

Agreement, read as "View 2's mode is the union of whole View 1 modes on this row": **193 of 252** rows. The 59 others
were reconciled one by one against the one-sentence test. The reconciled set is View 2's 51; View 1's finer splits are
kept inside each record as faces (its `view 1` column). Mechanical check: every row in exactly one mode, counts sum to
252.

## Modes
Exit: 1 fenced, 2 a `backlog` row naming the fence (here a proposal, R-a…R-h below), 3 impossible on this kernel.
Records: `2026-11-04-incident-mode-<nn>.md`.

| mode | observed failure mode | rows | predecessor | exit | fence row |
|------|-----------------------|------|-------------|------|-----------|
| 01 | test asserts a literal snapshot of the authoring tree or live repo (crafts, counts, instance values, tags) that a legitimate change falsifies | 7 | H | 2 | R-g |
| 02 | cross-zone coupled state (VERSION, BUNDLE.md rows, tags, craft-zone naming table) whose guards admit no one-zone PR order | 9 | M | 2 | R-h |
| 03 | a file or command uses an id assumed or remembered before the allocator's printed answer is read | 4 | C | 2 | R-c |
| 04 | ids allocated max(origin,local)+1 by sessions holding unpushed ids collide | 6 | T | 1 | — |
| 05 | a figure, sha, state or rule clause stated from the Agent's memory or a digest, not re-read from its source in the same turn | 11 | C | 3 | — |
| 06 | a claim about a mechanism accepted on a proxy (name, docstring, advertised field, one grep, wrong tree/function/base, correlation) without positive observation | 20 | D | 2 | R-g |
| 07 | an unfetched or local-only view of shared state (refs, tags, local main, pre-rebase sha) read as origin's | 7 | T | 2 | R-e |
| 08 | a raw path-scoped git checkout/reset used over live uncommitted or hand-resolved state | 5 | O | 3 | — |
| 09 | a CLI verb takes unknown flags (--help) or malformed args as positionals or skips them, then writes or runs | 12 | G | 2 | R-a |
| 10 | dwork verbs write a commit or entry the fence or format will refuse (open+planned in one commit, doubled date) | 4 | S | 1 | — |
| 11 | disposition/provenance entries written by free text without the Operator's words or for no disposition | 4 | B | 1 | — |
| 12 | an act (mutation, dispatch, ask) taken before the record that must precede it (plan file, plan-Y, board entry); no verb checks order | 8 | A | 2 | R-d |
| 13 | a merge executed before the Done-Y is recorded on origin | 5 | A | 1 | — |
| 14 | a push to a PR branch already named by a pending or given Done-Y | 2 | A | 1 | — |
| 15 | the Done record sets the row terminal before the merge, so a needed post-record push/merge has no path and the ledger claims merges that did not run | 6 | M | 1 | — |
| 16 | PRs held for a Done-Y on a shared tail-append file conflict with concurrent appends | 7 | X | 2 | R-f |
| 17 | a plan's step order or closure written without checking what authorizes each step (with-done, plan gate, backlog children) | 6 | L | 2 | R-c |
| 18 | a plan's files/zones/version/old-behaviour-tests list written from the deliverables instead of derived from the mutation | 8 | K | 2 | R-c |
| 19 | a corpus artifact written in a guarded form from memory or local habit; the guard runs only at push | 6 | S | 2 | R-g |
| 20 | a token in prose or a field (d-work #N, PR #N in a d-work cell) read by a parser as a claim or reference | 5 | F | 1 | — |
| 21 | success read from filtered output, a pipeline's exit or a string match rather than the command's own exit and the remote state | 7 | E | 1 | — |
| 22 | an ad hoc shell script continues after a failed step (set -e inside &&, unquoted heredoc) | 3 | E | 3 | — |
| 23 | a -f process match whose pattern appears in the matching command's own line | 2 | N | 3 | — |
| 24 | the hook execs its guard by path, so a mode change or missing exec bit kills it | 2 | V | 1 | — |
| 25 | a working hook bypassed (--no-verify, hooksPath=/dev/null) | 2 | V | 3 | — |
| 26 | suite or scratch children reach the live repository through inherited git env, cwd or the package path | 6 | W | 1 | — |
| 27 | a checker judges a proxy of its object (checked-out branch, the entrypoint's own tree, on-disk dirs, one merge base, index vs working tree) | 5 | D | 2 | R-d |
| 28 | a check passes or reports confidently over empty or absent input | 3 | E | 2 | R-a |
| 29 | presence identity and claims not bound to the holder (fresh uuid per call, per-process writer, shared name, rows from the whole ledger, root string compare) | 12 | R | 1 | — |
| 30 | a conduct preference (concise, delegation, batch signal) loaded but read by no mechanism at reply time | 6 | Q | 3 | — |
| 31 | a plan question not checked against stored constraints (refs dependencies, charter ceiling) | 2 | Q | 2 | R-c |
| 32 | unnamed local branches deleted as cleanup under momentum | 4 | P | 3 | — |
| 33 | an environment property the step relies on differs from the authoring host (interpreter, gh account, clone depth/tags, draft PRs, CI git version, token semantics) | 8 | I | 1 | — |
| 34 | hosting outage refuses writes | 2 | U | 3 | — |
| 35 | concurrent processes on one host contend for memory/CPU and corrupt runs | 3 | Y | 2 | R-f |
| 36 | test fixtures leak host resources (tmp dirs, inodes) | 2 | Y | 1 | — |
| 37 | a new call site or writer added without enumerating other paths to the same code or state | 3 | J | 2 | R-c |
| 38 | delegated or targeted verification ran a subset of what the push gate runs | 2 | E | 1 | — |
| 39 | the table parser splits on separators inside quoted or escaped cells | 2 | J | 1 | — |
| 40 | the practice requires an act the CLI or store has no form or verb for, so it is hand-written or routed around | 7 | M | 2 | R-h |
| 41 | trace windows anchor by text match and mixed date bases, and previews enter the store | 6 | R | 2 | R-b |
| 42 | the close path's landing test rebinds refs and writes it into the row | 4 | J | 1 | — |
| 43 | a mutating verb run on live state to probe its check | 2 | O | 1 | — |
| 44 | a release's publication step is untied to the tag mechanism; hand path used | 2 | A | 1 | — |
| 45 | evidence carried as paraphrase or selection instead of the command's own output form | 3 | C | 3 | — |
| 46 | cross-session coordination carried on channels the acting session does not read before acting (unpushed work, chat queue) | 3 | T | 2 | R-e |
| 47 | a hosted CI result produced and never read back, or its absence never compared | 2 | Q | 1 | — |
| 48 | an Operator-run command delivered inline and pasted | 1 | S | 3 | — |
| 49 | provenance transcription not verbatim; nothing compares it with the Operator's typed words | 2 | B | 2 | R-b |
| 50 | a push to a public remote quotes private material; no check at push | 1 | Q | 1 | — |
| 51 | mechanism not established by the cells | 1 | — | 3 | — |

## Reconciliation decisions
1. **View 2's granularity.** Where View 1 split one mechanism by surface (e.g. its five CLI-parsing modes), the split
   fails the one-sentence test, since one refusing parser stops all five. Kept as faces.
2. **View 1's granularity kept** where the fences differ at different moments: 13 (merge before the Done record) and 14
   (push to a PR a Done-Y names) stay apart, as do 21 (success read from filtered output) and 22 (shell continues after
   a failed step).
3. **Row 17** carries no mechanism the cells establish (cause empty in substance): mode 51, exit 3, stated as a limit.
4. **Harness hooks are not kernel fences.** Six modes (08, 22, 23, 25, 30, 32) have a candidate fence only as a harness
   hook or permission rule (`.claude/settings.json`). Rule-14 property 3 makes every guard run on the kernel alone, and
   Rule-1/Rule-8 Boundaries class the harness permission mode as an Operator-side fence outside the corpus. On this
   kernel they are exit 3, naming Rule-14 property 3. The hooks are listed below as an Operator option, not a row.
   Mode 13's harness deny rule likewise; its kernel fence is `dyad merge` (#532) plus `merges.py` (#541), exit 1.
5. **Mode 37** (a new call site added without enumerating other paths to the same state) is carried by R-c's
   callers-listed clause; old row #271 (J) is superseded rather than kept as its fence row.

## Predecessors
Every letter of the 2026-10-10 derivation and its deltas maps to at least one new mode; no old mode is lost.

| old | new modes |
|---|---|
| A | 12, 13, 14, 44 |
| B | 11, 49 |
| C | 03, 05, 45 |
| D | 06, 27 |
| E | 21, 22, 28, 38 |
| F | 20 |
| G | 09 |
| H | 01 |
| I | 33 |
| J | 37, 39, 42 |
| K | 18 |
| L | 17 |
| M | 02, 15, 40 |
| N | 23 |
| O | 08, 43 |
| P | 32 |
| Q | 30, 31, 47, 50 |
| R | 29, 41 |
| S | 10, 19, 48 |
| T | 04, 07, 46 |
| U | 34 |
| V | 24, 25 |
| W | 26 |
| X | 16 |
| Y | 35, 36 |
| — | 51 |

## Phase 2 — mitigations (summary; each record holds its table)
Read from the code and the Rule text at `eeea31fc`, never from this index's earlier prose, path and identifier cited
in each record. Fences shipped since the 2026-10-26 delta and verified `done`: #464–#467, #474, #479–#484, #495, #518
(F4), #519 (F2), #532 (`dyad merge`), #541 (`merges.py`), #547, #551, #552 (write-ahead fence on relays), #560 (row-id
contiguity). Still `backlog` and named as fences by a record: #548, #549, #550, #311, #313.

Live defects verified while reading (each in its record, none fixed here):
- `rows.py:462` takes the fence's mode from the checked-out branch, not the range judged (mode 27, R-d).
- the entrypoint compares its own tree, not the caller's (`package.py:267`; mode 27, R-d).
- `session touch` computes `behind_origin` without a fetch, contrary to #482's title (mode 07, R-e).
- the survey's listing command (`dyad/runbooks/incident-hardening.md:64`) matches `incident-mode-[a-z].md` only, so it
  lists none of this derivation's 51 numbered records; the play-book's naming (`<letter>`) cannot name more than 26
  modes. Mode 28's face (a check reporting confidently over empty input); proposed under R-g.

## Falsification of "this mode is addressed"
Written here because `agent-corpus/falsification/` is counsel's fence, not audit's; the amendment of
`2026-10-10-incident-modes-addressed.md` is proposed to counsel, as on 2026-10-24.

| # | claim | attack | result | survivor |
|---|---|---|---|---|
| 1 | #570 A2: modes were last derived over 140 rows | read the watermark at `0e54601` | **refuted**: 233; 19 ungrouped | plan #571 attack 1 |
| 2 | the 25 old modes are the right set | full re-derivation from the cells, two views blind to them | **refuted**: 51 modes; every old letter maps, but A, C, E, J, M, Q, S, T each held 3–4 mechanisms with different fences | the 51 |
| 3 | each exit-1 mode is fenced | for each of the 20, read the fence at `eeea31fc` and ask whether a recurrence path bypasses it | **survives, scoped**: 13 (raw `gh pr merge` or MCP merge bypasses `dyad merge`; `merges.py` detects after) and 21 (one face fenced) | exit 1, scope stated in records 13 and 21 |
| 4 | a harness hook closes 08/22/23/25/30/32 | Rule-14 p3, Rule-1/8 Boundaries | **refuted** as a kernel fence | exit 3, the hook an Operator option |
| 5 | exit 3 is a cop-out for 05 and 45 (statements from memory, paraphrased evidence) | look for a moment a guard could read | **survives**: what the agent says in chat reaches no guard; the evidence block's sha256 fences only what is cited by it (Rule-2 Binding) | exit 3 naming Rule-2's inference clause |
| 6 | the shipped fences since 10-26 reached their rows | recurrence after each ship date in the cells | **confirmed** for #532, #541, #552, #560 (no recurrence); 07's #482 **refuted** (defect above) | records 07, 12–15, 29 |
| 7 | easy agreement: View 2's 51 is the set | View 1's 62 against the one-sentence test | **pushed to confirmed** for 44 of 51; 7 kept merged with a face note | decisions 1–2 |
| 8 | the exercise measures without hardening (2026-10-24 attack 15) | count fences proposed per recurrence | **survives, conceded**: this seat proposes only; R-a…R-h cover 20 modes, 128 rows | proposals ranked below |

## Phase 4 — closure
| exit | modes | rows |
|---|---|---|
| 1 fenced | 20: 04 10 11 13 14 15 20 21 24 26 29 33 36 38 39 42 43 44 47 50 | 84 |
| 2 backlog (proposed R-a…R-h) | 20: 01 02 03 06 07 09 12 16 17 18 19 27 28 31 35 37 40 41 46 49 | 128 |
| 3 impossible on this kernel | 11: 05 08 22 23 25 30 32 34 45 48 51 | 40 |

Sum: 20 + 20 + 11 = 51 modes; 84 + 128 + 40 = 252 rows.

## Resolution of the mode rows #262–#283
21 rows stand `backlog`; #267 (F) and #284 (W) are `archived`. Each `backlog` row's mechanism is carried by the new
modes below. None stays owed under its old letter: each is either fenced, or its fence is now a proposed row R-x that
names it at one moment, or an impossibility is recorded. So all 21 are proposed for retirement in one retirement-form
question; the grounds are listed here.

| row | old | new modes (exit: fence) | ground |
|---|---|---|---|
| #262 | A | 12 (2: R-d), 13 (1), 14 (1), 44 (1) | fenced, rest superseded by R-d |
| #263 | B | 11 (1), 49 (2: R-b) | fenced, rest superseded by R-b |
| #264 | C | 03 (2: R-c), 05 (3), 45 (3) | superseded by R-c; impossibility recorded |
| #265 | D | 06 (2: R-g), 27 (2: R-d) | superseded by R-g, R-d |
| #266 | E | 21 (1), 22 (3), 28 (2: R-a), 38 (1) | fenced; superseded by R-a; impossibility |
| #268 | G | 09 (2: R-a) | superseded by R-a |
| #269 | H | 01 (2: R-g) | superseded by R-g |
| #270 | I | 33 (1) | fenced |
| #271 | J | 37 (2: R-c), 39 (1), 42 (1) | fenced; superseded by R-c |
| #272 | K | 18 (2: R-c) | superseded by R-c |
| #273 | L | 17 (2: R-c) | superseded by R-c |
| #274 | M | 02 (2: R-h), 15 (1), 40 (2: R-h) | fenced; superseded by R-h |
| #275 | N | 23 (3) | impossibility recorded |
| #276 | O | 08 (3), 43 (1) | fenced; impossibility |
| #277 | P | 32 (3) | impossibility recorded |
| #278 | Q | 30 (3), 31 (2: R-c), 47 (1), 50 (1) | fenced; superseded by R-c; impossibility |
| #279 | R | 29 (1), 41 (2: R-b) | fenced; superseded by R-b |
| #280 | S | 10 (1), 19 (2: R-g), 48 (3) | fenced; superseded by R-g; impossibility |
| #281 | T | 04 (1), 07 (2: R-e), 46 (2: R-e) | fenced; superseded by R-e |
| #282 | U | 34 (3) | impossibility recorded |
| #283 | V | 24 (1), 25 (3) | fenced; impossibility |

A row superseded by R-x is only safely retired once R-x exists, so the retirement question goes to the cos after the
fence-row proposal, or the two in one reply with the retirement conditional on R-a…R-h being opened.

## Proposed fence rows (owner engineer unless noted; opened by the cos, never here)
Ranked by rows reached.

| row | fence | moment | modes | rows |
|---|---|---|---|---|
| R-g | `syseng/tests` warns on a test that reads live repo state; `records.py` warns on an attack `confirmed`/`refuted` that cites no observation; seed verbs for guarded forms; the survey's listing pattern reads numbered records | push | 01 06 19 | 33 |
| R-c | `dyad plan check <id>`: plan title immutable; files, zones and version derived from the mutation; `order: required` steps checked; refs and charter-ceiling warnings at `dwork state planned`; callers of a changed function listed (counsel for the one Rule-3 sentence it needs) | `dwork state planned` | 03 17 18 31 37 | 23 |
| R-h | `dwork renumber` verb (row 121); a one-zone order for the coupled-state face (rows 60, 61, 188) | the act | 02 40 | 16 |
| R-a | one refusing parser for every `dyad` verb (`craft export --help`, `check --help`, `session --help`, `-r "a b"`); a distinct line for empty pre-push stdin | argument parse | 09 28 | 15 |
| R-d | `rows.py` takes its mode from the range, not the branch (`rows.py:462`); the entrypoint compares the caller's tree (`package.py:267`); the fence fails a `Y done` with no `Y plan` (row 111) | push | 12 27 | 13 |
| R-e | `session touch` fetches before `behind_origin`; a `hold:` line in `board/_cos.md` that pre-push refuses on | session start; push | 07 46 | 10 |
| R-f | evidence warns when a held PR touches a tail-append path; a host-wide suite `flock`, with load recorded | evidence; suite start | 16 35 | 10 |
| R-b | provenance entries dated by UTC; `trace --out` refuses before the Done; `check_store` refuses a preview; `dwork trace` labels non-verbatim entries | write | 41 49 | 8 |

## Operator option (not a row)
A harness hook or permission rule (`.claude/settings.json`, Operator-side, Rule-1 Boundaries) would prevent:
- 08: a raw path-scoped `git checkout`/`reset` over uncommitted state;
- 13: raw merges (`gh pr merge`, MCP merge);
- 22: `set -e` inside `&&`;
- 23: a self-matching `pgrep -f`;
- 25: `--no-verify` or `hooksPath=/dev/null`;
- 30: replies at a conduct preference;
- 32: branch deletion.

It is the Operator's to weigh and commit; this seat edits no settings.

## Limits
- Row 17's mechanism is unknown (mode 51). Row 123's is inferred from its consequence cell.
- Rows' dates for a few early rows were read from `git log -S`.
- Nothing was run except the read-only survey. Every mitigation claim is read from code at `eeea31fc` and cited
  `path:line`; none was exercised.
- No incident is appended to `INCIDENTS.md` by this PR (mode X): any incident of this exercise goes to the cos
  for the next narrow incidents PR.
