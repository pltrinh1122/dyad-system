# Operator preferences (preferences zone)

Operator-owned settings that the rules read. The Agent never changes a value on its own:
the cos seat — and no other seat (#426; the program charter in `MANDATES.md`) — proposes a change by a
preferences-zone PR, presented as its own question, and the Operator disposes it like any other.
Loaded at session start through `agent-corpus/CLAUDE.md`; the rule named in `read by`
defines what each value means.

| key | value | allowed | read by |
|-----|-------|---------|---------|
| merge-disposition | with-done | `separate` \| `with-done` | Rule-2 (binding), Rule-3 (counter-prompt form) |
| import-licenses | MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, PSF-2.0 | SPDX identifiers | Rule-13 (import criteria) |
| import-support | release within 12 months; packaged in the kernel ecosystem (PyPI for Python) | free text | Rule-13 (import criteria) |
| delegation | plan-and-execute | `none` \| `plan-and-execute` | Rule-3 (subagent clause) |
| delegation-posture | responsive | `responsive` \| `balanced` \| `efficient` | the cabinet Operating Guide (Posture), Rule-3 (subagent clause, under `delegation: plan-and-execute`) |
| delegation-posture-unattended | efficient | `responsive` \| `balanced` \| `efficient` | the cabinet Operating Guide (Posture), Rule-3 (subagent clause, under `delegation: plan-and-execute`) |
| cli-pattern | industry-standard | `industry-standard` \| `explicit-python` | Rule-19 (run-book commands), Rule-11 (entrypoint) |
| batch-disposition-mode | always | `off` \| `on-ignore` \| `always` | Rule-2 (binding), Rule-3 (counter-prompt form) |
| ledger-pr-merge | agent | `ask` \| `agent` | Rule-2 (not-ratification list), Rule-1 (branch-fence case, #23) |
| concise-mode | on | `off` \| `on` | Rule-10 (reply form), Rule-3 (what the reply carries) |
| host-path | workstation-corpus | a repo-relative directory | Rule-1 (host row of the zone table), Rule-14 (instance contribution) |
| host-zone | workstation | `workstation` \| `infra` | Rule-1 (host row of the zone table) |
| dwork-trace | always | `always` \| `on-demand` | Rule-3 (completion evidence) |
| accretion | implicit | `explicit` \| `implicit` | Rule-3 (scope, plan, ledger, completion), Rule-2 (binding) |
| organization | m4 | `flat` \| `m4` | Rule-16 (Presence: the seat-name form), Rule-3 (Ledger: what a session reads at start) |
| paired-units | communicate, communicate-marketing | `none`, or seat names (with or without their `-<hp>`) | Rule-16 (Presence: attendance, declared), the cabinet Operating Guide (§8) |
| attendance-window | 7 | a positive number of days | Rule-16 (Presence: attendance, checked against the records) |
| relay-form | brief | `verbatim` \| `brief` | the cabinet Operating Guide (§8, the route table), Rule-3 (Completion counter-prompt: the form a relayed Done question's evidence takes) |
| intent-reading | on | `on` \| `off` | Rule-3 (Plan, Answer grammar: the intent question before the plan), Rule-15 (phase 1: what accepts the definition of done) |
| dwork-slug | on | `on` \| `off` | Rule-3 (What a `Y` binds and Ledger: a row's slug and how a row id is presented) |
| awaiting-you | on | `on` \| `off` | Rule-3 (Batch disposition: the closing line every reply ends with) |
| coming | on | `on` \| `off` | Rule-3 (Batch disposition: the Coming part of the closing line) |
| hygiene-stale-days | 30 | a positive integer (days) | Rule-3 (backlog hygiene, the sweep's `hygiene I…` and `candidate:` lines; default `dyad/dmc/backlog-hygiene.jsonld`) |
| hygiene-similar | 0.35 | a number between 0 and 1 | Rule-3 (backlog hygiene; default `dyad/dmc/backlog-hygiene.jsonld`) |
| hygiene-top | 10 | a positive integer (pairs) | Rule-3 (backlog hygiene; default `dyad/dmc/backlog-hygiene.jsonld`) |
| inflight-unread-hours | 4 | a positive integer (hours) | Rule-3 (work in flight, the sweep's `inflight W…` lines; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-planned-quiet-days | 3 | a positive integer (days) | Rule-3 (work in flight; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-unplanned-hours | 24 | a positive integer (hours) | Rule-3 (work in flight; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-pr-still-days | 3 | a positive integer (days) | Rule-3 (work in flight; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-promise-days | 3 | a positive integer (days) | Rule-3 (work in flight; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-question-hours | 24 | a positive integer (hours) | Rule-3 (work in flight; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-done-ready-hours | 4 | a positive integer (hours) | Rule-3 (work in flight, W11: a done-ready row whose Done is not asked; default `dyad/dmc/work-in-flight.jsonld`; d-work #587) |
| sweep-landing-hours | 24 | a positive integer (hours) | Rule-14 (the scheduled sweep's findings over time; default `dyad/dmc/sweep-findings.jsonld`) |
| sweep-board-stale-days | 3 | a positive integer (days) | Rule-14 (the scheduled sweep; default `dyad/dmc/sweep-findings.jsonld`) |
| sweep-ci-hours | 24 | a positive integer (hours) | Rule-14 (the scheduled sweep; default `dyad/dmc/sweep-findings.jsonld`) |
| promotion-ceiling | 2 | a positive integer (rows proposed at once, never more than the idle units) | Rule-3 (backlog promotion, judged by the home; default `dyad/dmc/promotion.jsonld`) |
| promotion-adjacency-min | 3 | a positive integer (the adjacency score that alone makes a candidate adjacent) | Rule-3 (backlog promotion, judged by the home; default `dyad/dmc/promotion.jsonld`) |

- `merge-disposition`
  - `separate` — every PR merge is its own counter-prompt (`Y/N: merge #N?`) before the
    d-work's completion counter-prompt. This duplicates the plan-`Y` (Rule-3) at the PR;
    choose it only if the duplicate is wanted.
  - `with-done` — the completion counter-prompt names the d-work's unmerged PR(s). The
    Done-`Y` is the Operator's verification that the output matches intent; the Agent then
    merges as clerical execution. Two `Y`s per d-work: plan and Done. A PR whose d-work is
    *not* yet done **waits for that d-work's Done-`Y`**, which names it: the Agent holds it,
    rebases it as `main` moves, never merges `main` into it, and reports the wait and the rebase
    count in the completion evidence. The Operator is not asked about a merge — the Done-`Y`
    verifies the output as it stands in the PR, before merge, which is what Rule-3's completion
    clause exists for. The hold has a price, and the protocol for it is the play-book's: a PR
    touching a tail-append file is cut narrow and landed first. Decided in d-work #290 after two
    live instances of the price — PR #355, a merge ratified on 2026-10-08 that never ran, and
    PR #371, clean for two days and conflicted by a concurrent session's merge within the hour.

- `import-licenses` — licenses under which code may be imported into the package (it is
  redistributed under Rule-11). Tools merely invoked are not subject to it (Rule-14 rows).
- `import-support` — the maintenance and packaging evidence an import must show.
- `delegation` — `plan-and-execute`: subagents draft plan files and execution branches so the
  main Agent stays free for the next prompt; the main Agent alone writes rows, asks the plan-Y,
  pushes, opens PRs and asks Done. `none`: subagents read, search and draft text only.
- `delegation-posture` — how much of an **attended** seat's own work — the cos always, and any seat
  `paired-units` names (Rule-16 Presence) — runs in its main chat and how much in the subagents it spawns (forks,
  worktrees) (d-work #436, #441). It never routes an act between seats: which seat
  owns an act is the charter's (`MANDATES.md`), unchanged by any value. The floor is Rule-3's subagent clause: a
  seat's main chat alone writes rows, asks and answers counter-prompts, pushes, opens PRs, merges and runs host
  actions; a subagent never. Above the floor: `responsive` — the main chat does only the floor; every draft (plan
  file, analysis, falsification text, a branch's changes), every evidence run in a worktree and every board
  rendering runs in a subagent, so the chat answers its next message at once. `balanced` — the main chat does
  work it can finish within a budget, 2 minutes of tool time per act, the one number the Operator tunes; longer
  work goes to a subagent. `efficient` — the main chat drafts and verifies itself and spawns a subagent only for
  work that must run in parallel or in an isolated worktree, or that Rule-10 delegates (under `concise-mode: on`,
  execution longer than a few tool calls). The cost is tokens against chat latency: a subagent
  re-reads its context and is the dear hop, so `responsive` spends the most tokens for the least latency and
  `efficient` the fewest, the chat unavailable for the duration. The cos's availability rule (#432: its checkout
  runs nothing longer than a ledger-only push) holds under every value. It refines `plan-and-execute` and is inert
  under `delegation: none`. A form preference: it authorizes nothing, and who disposes never changes.
  dyad-system: `responsive`, the Operator's choice (#436), in the words of its revision-2 prompt:
  "clarification: tuning criteria is not for outside of seat delegation but within seat:  `main-chat`  vs. `sub-agent`."
  — followed, after two blank lines, by a lone "not", kept verbatim in the provenance record and read as a truncated line.
- `delegation-posture-unattended` — the same three values, for every seat that is not attended: under
  `paired-units: none`, every secretary and desk (d-work #441). No Operator waits on such a seat's chat. What
  reaches it comes through the cos, which relays and moves on, so the cos stays free whatever this value is,
  and a matter routed to the seat waits at most for the act the seat is in. Inert under `organization: flat`
  (its one seat is the leader). Where neither posture row exists, a seat runs `responsive` attended and
  `efficient` unattended (the cabinet Guide's fallback). A form preference: it authorizes nothing.
  dyad-system: `efficient`, the Operator's prompt of 2026-10-25: "Adjustment to the key setting.  The
  `delegation-posture` is especially important only when operator is attending.  Otherwise, secretary seats
  should default to `efficient` while `cos` seat defaults to `responsive`."
- `cli-pattern` — `industry-standard`: a run-book command is the tool's own CLI shown verbatim
  (`docker compose … stop`); a runner may wrap it for telemetry but prints and runs the identical
  line; the dyad's own commands go through one entrypoint, `dyad/bin/dyad`, as `<noun> <verb>`
  (`dyad check`, `dyad dwork new`, `dyad runbook git-server status`). `explicit-python`: commands
  are written as `python3.12 dyad/scripts/<script>.py …`, no entrypoint (ledger #152).
- `batch-disposition-mode`
  - `off` — every plan and completion counter-prompt is asked and disposed singly.
  - `on-ignore` — singly, until the Operator leaves one counter-prompt outstanding (the next
    message is a prompt, not its bare disposal, Rule-3 Scope): the engagement signal itself,
    nothing else needed. The Agent then holds a pending queue and asks the batch forms
    (Rule-3, Batch disposition), lapsing back to singly once the queue drains.
  - `always` — never singly: the first pending item already opens the queue.
- `ledger-pr-merge` — who executes the merge when a *ledger-only* change reaches `main` as a PR
  rather than as the direct commit Rule-3 prescribes. Rule-2 already classes a ledger-only commit
  (touching nothing outside `agent-corpus/d-work/`) as *not ratification* — it records a prompt
  received or a disposition already given, never a decision. A session-level branch fence can
  forbid the direct push and force the same content through a PR (Rule-1, the #23 case); this
  preference says what happens then.
  - `ask` — the Agent states the collision and asks, per instance, before that PR is merged.
  - `agent` — the Agent merges it without a counter-prompt, provided its *entire* diff is
    ledger-only. Scope is the path prefix, not the zone and not authorship: a PR carrying even one
    path outside `agent-corpus/d-work/` — `agent-corpus/audits/INCIDENTS.md`, for instance — is
    unaffected and follows `merge-disposition`. The Agent checks the whole diff mechanically
    before each such merge, and the merge commit cites this preference and the file list, so
    `git log` alone shows why no counter-prompt preceded it.
- `concise-mode`
  - `off` — the Agent may speak before and between its actions: a preface, progress lines,
    interim findings, then the synthesis.
  - `on` — exactly one reply per Operator prompt: the synthesis, emitted when the turn ends —
    done, or stopped at a blocking question (Rule-8) — with no preface and no progress lines.
    Everything a Rule requires reported appears in it: findings, incidents, the evidence block,
    the pending-queue counts, the one `Y/N` last (Rule-10) — each written to the corpus first
    where a Rule stores it (the plan file, `INCIDENTS.md`, provenance), so an interrupted turn
    loses narration, never record. Execution longer than a few tool calls is delegated to a
    fork in its own worktree (`delegation: plan-and-execute`, Rule-3 Scope), so the reply comes
    at once and the Agent stays free for the next prompt; the fork's findings appear in the next
    synthesis, and only the main Agent commits, pushes and asks. A harness "say what you're
    doing" prompt gets one status line, never a second synthesis; a mid-turn Operator message is
    answered in the same reply under the batch queue. Determined in d-work #113: delegation
    detects nothing sooner — it fences execution from the plan-`Y` structurally and frees the
    Agent; that is what is bought.
- `accretion` — whether a row the Agent opens *while executing another row* needs its own
  dispositions, or inherits them. An **accreted row** is one the Agent brought into being
  mid-execution rather than one the Operator prompted for; 117 of this instance's 280 rows are
  such rows (d-work #290's audit).
  - `explicit` — as before this preference: the accreted row needs its own opening disposition,
    its own plan-`Y`, and its own Done-`Y`.
  - `implicit` — a row whose existence the **authorized plan already describes**, inside the
    *mandate scope* that plan states, is born `open` under that plan-`Y` and takes no disposition
    of its own; its Done rides the mandate's Done-`Y`, which names it, and the completion evidence
    lists every row accreted under it. Anything the mandate scope does not name returns to
    `explicit` and is asked: a destructive host action (Rule-8 keeps its own counter-prompt), a
    release (Rule-11), a Rule-3 Intake (its words are another Operator's, Rule-7 property 4), a
    preference change, or any mutation outside the plan. This is the countersign model's
    **implicit mode** countersigned by a **mandate**, adopted rather than coined (Rule-13
    property 1; the model is the core play-book `dyad/playbooks/countersign-model.md` since #369 C3);
    in that model's own classification (`dyad/playbooks/countersign-model.md`, Part II §5)
    it is an **authority preference** — a standing countersignature that authorizes a class of act
    — where `concise-mode`, `batch-disposition-mode`, `merge-disposition` and `delegation` are
    **form preferences**, which authorize nothing.

- `host-path` — where this system keeps its host and operating records (change log, ops scripts,
  run-books, its own operating manifest rows `INFRASTRUCTURE.md`); the host row of the zone table
  is `<host-path>/*` (Rule-1). dyad-system: `workstation-corpus` (d-work #175).
- `host-zone` — the zone that row belongs to. `workstation`: five zones. `infra`: the host records
  are infrastructure of the repo and the system has four zones.
- `dwork-trace` — whether each d-work's performance trace (play-book `dyad/playbooks/dwork-trace.md`,
  d-work #213) is part of its completion evidence. `always`: every completion cites the d-work's trace, so a
  baseline exists before anyone optimizes and no d-work's timing is lost when an ephemeral session ends
  (its transcript is never committed, Rule-7). `on-demand`: a trace only when the Operator prompts for one;
  a d-work whose session has ended can then be traced from git and the ledger only (d-work #215).
- `organization` — the shape of this system's seats (d-work #369, plan revisions 1–13; #385 PR-B). `m4`: a
  tree of operator–agent pairs — the program seat its cos, a secretary per function and desks under them, each keeping a board — authority granted by the content-scoped
  charters of `MANDATES.md` beside this file (seeded from `crafts/cabinet/templates/mandates.md`), every pair
  sharing the same ledgers; a presence file's name is a seat name, `<function>[-<topic>]-<hp>` (Rule-16
  Presence; the cabinet craft's `rules/naming.md`), read advisorily by the cabinet craft's `seat` guard and printed
  by `dyad session name`. `flat`: one pair, one board, desks by row; no seat form is read. dyad-system:
  `m4`, the Operator's default since 2026-10-21 ("codify M4 as the default organizational preference").
- `paired-units` (named `attended-seats` until d-work #573; the old name is refused, naming this one, since d-work #604) — the seats the Operator attends beside the program seat, which is always attended (d-work
  #412): seat names, or seat names without their `-<hp>` (`counsel` names every holder of the counsel seat), or
  `none`. The constraint it states is the Operator's span — how many seats the Operator sits at, a limit of the
  interface the Operator reads through — never how many seats run: in the Operator's words, "we can have one
  hundred sessions and that wouldn't bother me if the `program` session is the only one i'm `attending` and it's
  orchestrating across all of the other sessions." `dyad session list` reads the mode over the live seats —
  every seat attended (M4), only the program seat (M3), some (hybrid) — and a seat's counter-prompt is asked in
  its own chat when attended and relayed through the program seat otherwise. dyad-system: `communicate`, the
  Operator's prompt of 2026-10-27 ("I need to have this conversation in the `communicate` session.  Mark that session as 'attended' because i'll need to hard-context switch whenever i'm working on the story.  the story is also asynchronous and has no dependency on other matters, persistent for the duration of the dyad-system at a minimimum - so it's an exemplar for when operator attendance should happen.") — the instance's reading: a seat is attended when its work is a
  hard context switch for the Operator, asynchronous, independent of other matters and long-lived; the leader is
  always attended.
  dyad-system adds `communicate-marketing`, the product-marketing desk of the communicate function (d-work #666), on the
  Operator's prompt of 2026-11-10: "i'll be attending the dyad unit after you spawn it".
- `attendance-window` — how many days the records are read back to check `paired-units` (d-work #388, #412): a
  seat holds an own disposition when a provenance record whose `session:` line names it holds a disposition
  whose note holds neither `mandate #<id>` nor `relayed via`, anywhere (#422), within the window. A live seat holding one that
  `paired-units` does not declare prints `undeclared` (the leader reports it); a declared seat holding none prints `warn`.
  dyad-system: `7`, plan #388's default.
- `relay-form` — how the leader, the cos, presents to the Operator a question a seat that is not attended owes
  (d-work #424): the Operator-bound direction of a relay. The seat-bound direction never varies — the Operator's
  words reach a seat verbatim (the core's relayed prompt, #253 R29). `verbatim`: the seat's question and its
  evidence passed through as the seat wrote them, the last line the seat's question. `brief`: the cos meets the
  Operator at the Operator's altitude and presents WHAT (the matter and its state), WHY (what it bears on) and HOW
  (the path, its strongest counter and the reconciliation — Rule-10's form applied by the cos to the seat's
  question), the seat's text quoted as citation and evidence, never the body, and the seat's evidence block
  verbatim; the last `Y/N` line is the seat's own question text, so the `Y` binds to what the seat asked
  (Rule-2, Binding). Either way the form authorizes nothing: it shapes what the Operator reads, never what a `Y`
  binds to.
  dyad-system: `brief`, the Operator's prompt of 2026-10-25 ("I need dispositions to be presented by you by
  explaining WHAT is the matter, WHY is the matter important and HOW is the matter being addressed").
- `intent-reading` — whether a prompt that opens a row, or reopens one from `backlog`, is first answered by an
  intent reading and its own question, `Y/N: intent aligned for #<id> <title>?`, before any plan is drafted (Rule-3
  Plan and Answer grammar, Rule-15 phase 1; the criterion `dyad/dmc/intent-reading.jsonld`; d-work #615). `off`: two
  `Y`, the plan-`Y` accepting the definition of done; `on`: three `Y`, the intent-`Y` accepting it, a bare `N`
  archiving the row. The template ships `off`. A form preference: it authorizes nothing.
  dyad-system: `on`, the Operator's prompt of 2026-11-06: "even though default is 'off' for shipping, i want it 'on'
  for current use."
- `dwork-slug` — whether a row id is presented to the Operator with its row slug after the number, `#<id>-<slug>`
  (Rule-3 What a `Y` binds and Ledger; Rule-16 Store; d-work #622). `on`: replies, counter-prompt lines, relays and the
  human-readable listings show `#<id>-<slug>`; `off`: the bare `#<id>`. Stored references stay the bare number either way.
  The template ships `on`; an absent key reads `off`. A form preference: it authorizes nothing.
  dyad-system: `on`, the Operator's prompt of 2026-11-07: "to assist operator with identifying d-work by its identifier,
  as a preference ("on" by default), d-work id should be presented along with 2-3 tag slugs after then number, e.g.
  "#621-release-intent-Y""
- `awaiting-you` — the form of the closing line every reply ends with (Rule-3 Batch disposition; d-work #646; the
  template's description). dyad-system: `on`, the Operator's prompt of 2026-11-08: "default setting is "On" to display
  "Awaiting you:" ." Seeded here 2026-11-10 (d-work #665), the value it already read when absent.
- `coming` — whether the closing line ends with its `Coming:` part, read only under `awaiting-you: on` (Rule-3 Batch
  disposition; d-work #665; the template's description). dyad-system: `on`, the Operator's prompt of 2026-11-10:
  "making "Coming:" a preferences setting with default of "on"". Seeded here with it, the value an absent key reads.
- The tunables (d-work #590) — `hygiene-stale-days`, `hygiene-similar`, `hygiene-top`, the seven `inflight-*` keys (`inflight-done-ready-hours` added by d-work #587, at its default),
  the three `sweep-*` keys, `promotion-ceiling` and `promotion-adjacency-min`: the numbers whose change alters what
  reaches the Operator, or when. Each default is the `dyad:defaultValue` of the decision criterion that claims the key
  (`dyad/dmc/schema.md`, `dyad:tunables`), and the code reads each through `dyadlib.tunable`, so a missing or
  out-of-range value reads as that default. dyad-system: every one at its default, the values the code used as
  constants before #590, so nothing changes in behaviour; altitude has no key, its knob being the definition of done
  (plan #570 revision 4).
