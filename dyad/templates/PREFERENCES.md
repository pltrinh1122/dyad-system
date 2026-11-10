# Operator preferences (preferences zone)

Operator-owned settings that the rules read. The Agent never changes a value on its own:
it proposes a change by a preferences-zone PR, and the Operator disposes it like any other.
Loaded at session start through `agent-corpus/CLAUDE.md`; the rule named in `read by`
defines what each value means.

| key | value | allowed | read by |
|-----|-------|---------|---------|
| merge-disposition | with-done | `separate` \| `with-done` | Rule-2 (binding), Rule-3 (counter-prompt form) |
| import-licenses | MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, PSF-2.0 | SPDX identifiers | Rule-13 (import criteria) |
| import-support | release within 12 months; packaged in the kernel ecosystem (PyPI for Python) | free text | Rule-13 (import criteria) |
| delegation | none | `none` \| `plan-and-execute` | Rule-3 (subagent clause) |
| delegation-posture | responsive | `responsive` \| `balanced` \| `efficient` | the cabinet Operating Guide (Posture), Rule-3 (subagent clause, under `delegation: plan-and-execute`) |
| delegation-posture-unattended | efficient | `responsive` \| `balanced` \| `efficient` | the cabinet Operating Guide (Posture), Rule-3 (subagent clause, under `delegation: plan-and-execute`) |
| cli-pattern | industry-standard | `industry-standard` \| `explicit-python` | Rule-19 (run-book commands), Rule-11 (entrypoint) |
| batch-disposition-mode | off | `off` \| `on-ignore` \| `always` | Rule-2 (binding), Rule-3 (counter-prompt form) |
| ledger-pr-merge | ask | `ask` \| `agent` | Rule-2 (not-ratification list), Rule-1 (branch-fence case) |
| concise-mode | off | `off` \| `on` | Rule-10 (reply form), Rule-3 (what the reply carries) |
| accretion | explicit | `explicit` \| `implicit` | Rule-3 (scope, plan, ledger, completion), Rule-2 (binding) |
| host-path | workstation-corpus | a repo-relative directory | Rule-1 (host row of the zone table), Rule-14 (instance contribution) |
| host-zone | workstation | `workstation` \| `infra` | Rule-1 (host row of the zone table) |
| dwork-trace | always | `always` \| `on-demand` | Rule-3 (completion evidence) |
| organization | m4 | `flat` \| `m4` | Rule-16 (Presence: the seat-name form), Rule-3 (Ledger: what a session reads at start) |
| paired-units | none | `none` \| seat names, or seat names without `-<hp>` | Rule-16 (Presence: attendance, declared) |
| attendance-window | 7 | a positive number of days | Rule-16 (Presence: attendance, checked against the records) |
| relay-form | verbatim | `verbatim` \| `brief` | the cabinet Operating Guide (§8, the route table), Rule-3 (Completion counter-prompt: the form a relayed Done question's evidence takes) |
| intent-reading | off | `on` \| `off` | Rule-3 (Plan, Answer grammar: the intent question before the plan), Rule-15 (phase 1: what accepts the definition of done) |
| dwork-slug | on | `on` \| `off` | Rule-3 (What a `Y` binds and Ledger: a row's slug and how a row id is presented) |
| awaiting-you | on | `on` \| `off` | Rule-3 (Batch disposition: the closing line every reply ends with) |
| coming | on | `on` \| `off` | Rule-3 (Batch disposition: the Coming part of the closing line) |
| hygiene-stale-days | 30 | a positive integer (days) | Rule-3 (backlog hygiene, the `hygiene I…` and `candidate:` lines of the home's read (`dyad board resume`): `dyad/scripts/hygiene.py`; default `dyad/dmc/backlog-hygiene.jsonld`) |
| hygiene-similar | 0.35 | a number between 0 and 1 | Rule-3 (backlog hygiene, the `hygiene I…` and `candidate:` lines of the home's read (`dyad board resume`): `dyad/scripts/hygiene.py`; default `dyad/dmc/backlog-hygiene.jsonld`) |
| hygiene-top | 10 | a positive integer (pairs) | Rule-3 (backlog hygiene, the `hygiene I…` and `candidate:` lines of the home's read (`dyad board resume`): `dyad/scripts/hygiene.py`; default `dyad/dmc/backlog-hygiene.jsonld`) |
| inflight-unread-hours | 4 | a positive integer (hours) | Rule-3 (work in flight, the `inflight W…` lines of the home's read: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-planned-quiet-days | 3 | a positive integer (days) | Rule-3 (work in flight, the `inflight W…` lines of the home's read: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-unplanned-hours | 24 | a positive integer (hours) | Rule-3 (work in flight, the `inflight W…` lines of the home's read: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-pr-still-days | 3 | a positive integer (days) | Rule-3 (work in flight, the `inflight W…` lines of the home's read: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-promise-days | 3 | a positive integer (days) | Rule-3 (work in flight, the `inflight W…` lines of the home's read: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-question-hours | 24 | a positive integer (hours) | Rule-3 (work in flight, the `inflight W…` lines of the home's read: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| inflight-done-ready-hours | 4 | a positive integer (hours) | Rule-3 (work in flight, the home's read's `inflight W11` line for a `done-ready` board entry: `dyad/scripts/hygiene.py`; default `dyad/dmc/work-in-flight.jsonld`) |
| sweep-landing-hours | 24 | a positive integer (hours) | Rule-14 (the stall findings of the home's read, `dyad board resume`: `dyad/scripts/automaton.py`; default `dyad/dmc/sweep-findings.jsonld`) |
| sweep-board-stale-days | 3 | a positive integer (days) | Rule-14 (the stall findings of the home's read, `dyad board resume`: `dyad/scripts/automaton.py`; default `dyad/dmc/sweep-findings.jsonld`) |
| sweep-ci-hours | 24 | a positive integer (hours) | Rule-14 (the stall findings of the home's read, `dyad board resume`: `dyad/scripts/automaton.py`; default `dyad/dmc/sweep-findings.jsonld`) |
| promotion-ceiling | 2 | a positive integer (rows proposed at once, never more than the idle units) | Rule-3 (backlog promotion, judged by the home: `dyad/playbooks/d-work.md`; default `dyad/dmc/promotion.jsonld`) |
| promotion-adjacency-min | 3 | a positive integer (the adjacency score that alone makes a candidate adjacent) | Rule-3 (backlog promotion, judged by the home: `dyad/playbooks/d-work.md`; default `dyad/dmc/promotion.jsonld`) |

- `merge-disposition`
  - `separate` — every PR merge is its own counter-prompt (`Y/N: merge #N?`) before the
    d-work's completion counter-prompt. This duplicates the plan-`Y` (Rule-3) at the PR;
    choose it only if the duplicate is wanted.
  - `with-done` — the completion counter-prompt names the d-work's unmerged PR(s). The
    Done-`Y` is the Operator's verification that the output matches intent; the Agent then
    merges as clerical execution. Two `Y`s per d-work: plan and Done. A PR whose d-work is
    *not* yet done **waits for that d-work's Done-`Y`**, which names it: the Agent holds it,
    rebases it as `main` moves, never merges `main` into it, and reports the wait and the
    rebase count in the completion evidence. The Operator is not asked about a merge — the
    Done-`Y` verifies the output as it stands in the PR, before merge, which is what Rule-3's
    completion clause exists for. The hold has a price, and the protocol for it is the
    play-book's (`dyad/playbooks/disposition-digest.md`, the held-PR protocol): a PR touching
    a file every session appends to is cut narrow and landed first. Decided in d-work #290,
    after a merge ratified by a Done-`Y` that was never executed and a clean PR conflicted
    within the hour by a concurrent session's merge into the same append-only file.

- `import-licenses` — licenses under which code may be imported into the package (it is
  redistributed under Rule-11). Tools merely invoked are not subject to it (Rule-14 rows).
- `import-support` — the maintenance and packaging evidence an import must show.
- `delegation` — `plan-and-execute`: subagents draft plan files and execution branches so the
  main Agent stays free for the next prompt; the main Agent alone writes rows, asks the plan-Y,
  pushes, opens PRs and asks Done. `none`: subagents read, search and draft text only. Seeded
  `none`: the more contained behavior, until the Operator has reviewed the workflow and chosen
  `plan-and-execute`.
- `delegation-posture` — how much of an attended seat's own work runs in its main chat and how much in the
  sub-agents it spawns: `responsive` (the main chat does only what Rule-3's subagent clause keeps for it),
  `balanced` (work it can finish within a budget) or `efficient` (it drafts and verifies itself). A form
  preference: it authorizes nothing, and it is inert under `delegation: none`. Seeded `responsive`, the cabinet
  Operating Guide's fallback for an attended seat.
- `delegation-posture-unattended` — the same three values, for every seat that is not attended. Seeded
  `efficient`, the Guide's fallback for an unattended seat (#603: every key `dyad/surface.md` S3 freezes is
  seeded here, so a fresh install passes its own suite).
- `cli-pattern` — `industry-standard`: a run-book command is the tool's own CLI shown verbatim
  (`docker compose … stop`); a runner may wrap it for telemetry but prints and runs the identical
  line; the dyad's own commands go through one entrypoint, `dyad/bin/dyad`, as `<noun> <verb>`
  (`dyad check`, `dyad dwork new`, `dyad runbook git-server status`). `explicit-python`: commands
  are written as `python3.12 dyad/scripts/<script>.py …`, no entrypoint (ledger #152). Seeded
  `industry-standard`: `dyad/bin/dyad` ships executable as part of the core craft's own tree, so
  a fresh install has a working entrypoint immediately.
- `batch-disposition-mode` — `off`: every plan and completion counter-prompt is asked and
  disposed singly. `on-ignore`: singly, until the Operator leaves one outstanding — the
  engagement signal itself — after which the Agent holds a pending queue and asks the batch
  forms (Rule-3, Batch disposition), lapsing back to singly once the queue drains. `always`:
  never singly. Seeded `off`: the existing single-question behavior, until the Operator has
  engaged it once. `on-ignore` carries a known cost: the signal is conversational and nothing
  mechanical raises it, so a session can miss an ignored counter-prompt and go on asking singly
  (d-work #290); `always` removes the signal rather than detecting it.
- `ledger-pr-merge` — who executes the merge when a *ledger-only* change reaches `main` as a PR
  rather than as the direct commit Rule-3 prescribes. Rule-2 already classes a ledger-only commit
  (touching nothing outside `<instance>/d-work/`) as *not ratification*: it records a prompt
  received or a disposition already given, never a decision. A session-level branch fence can
  forbid the direct push and force the same content through a PR (Rule-1); this preference says
  what happens then. `ask`: the Agent states the collision and asks, per instance, before that PR
  is merged. `agent`: the Agent merges it without a counter-prompt, provided its *entire* diff is
  ledger-only — scope is the path prefix, not the zone and not authorship, so a PR carrying even
  one path outside `<instance>/d-work/` is unaffected and follows `merge-disposition`; the Agent
  checks the whole diff mechanically before each such merge, and the merge commit cites this
  preference and the file list, so `git log` alone shows why no counter-prompt preceded it.
  Seeded `ask`: it is an authority preference (a standing mandate), and an install never ships
  an authorization its own Operator has not disposed.
- `concise-mode` — `off`: the Agent may speak before and between its actions. `on`: exactly one
  reply per Operator prompt, the synthesis, emitted when the turn ends (done, or stopped at a
  blocking question); every finding, incident, evidence block and queue count a Rule requires is
  in it, written to the corpus first where a Rule stores it; long execution is delegated to a
  fork (`delegation`) so the reply is prompt and the Agent stays free; a harness mid-turn prompt
  gets one status line, never a second reply (Rule-10 Form, Rule-3 Incidents; d-work #113).
  Seeded `off`: the harness's own default, until the Operator has read the trade.
- `accretion` — whether a row the Agent opens *while executing another row* needs its own
  dispositions, or inherits them. An **accreted row** is one the Agent brought into being
  mid-execution rather than one the Operator prompted for. `explicit`: the accreted row needs its
  own opening disposition, its own plan-`Y`, and its own Done-`Y`. `implicit`: a row whose
  existence the **authorized plan already describes**, inside the *mandate scope* that plan
  states, is born `open` under that plan-`Y` and takes no disposition of its own; its Done rides
  the mandate's Done-`Y`, which names it, and the completion evidence lists every row accreted
  under it. Anything the mandate scope does not name returns to `explicit` and is asked: a
  destructive host action (Rule-8 keeps its own counter-prompt), a release (Rule-11), a Rule-3
  Intake (its words are another Operator's, Rule-7 property 4), a preference change, or any
  mutation outside the plan — the escalate-edge test of
  `dyad/playbooks/disposition-digest.md`. This is the countersign model's **implicit mode**
  countersigned by a **mandate**, adopted rather than coined (Rule-13 property 1); in that
  model's own classification (`dyad/playbooks/countersign-model.md` Part II §5) it is an **authority
  preference** — a standing countersignature that authorizes a class of act — where
  `concise-mode`, `batch-disposition-mode`, `merge-disposition` and `delegation` are **form
  preferences**, which authorize nothing. Seeded `explicit`: an authority preference is a
  mandate, and an install never ships one its own Operator has not disposed (Rule-2).
- `host-path` — where this system keeps its host and operating records (change log, ops scripts,
  run-books, its own operating manifest rows `INFRASTRUCTURE.md`); the host row of the zone table
  is `<host-path>/*` (Rule-1, `dyad/guards/infra/containment.py`). Default `workstation-corpus`.
- `host-zone` — the zone that row belongs to. `workstation` (default): the five zones. `infra`: the
  host records are infrastructure of the repo and the system has four zones (no `workstation`).
- `dwork-trace` — whether each d-work's performance trace (play-book `dyad/playbooks/dwork-trace.md`,
  d-work #213) is part of its completion evidence. `always`: every completion cites the d-work's
  trace, so a baseline exists before anyone optimizes and no d-work's timing is lost when an
  ephemeral session ends (its transcript is never committed, Rule-7). `on-demand`: a trace only
  when the Operator prompts for one; a d-work whose session has ended can then be traced from git
  and the ledger only (d-work #215). Seeded `always`: it authorizes nothing, and a d-work whose
  harness keeps no transcript is still traced from git and the ledger with its buckets marked
  absent, so the value costs a fresh install nothing it cannot produce.
- `organization` — the shape of the system's seats (d-work #369). `m4`: a tree of operator–agent pairs,
  the program seat its cos, a secretary per function and desks under them, each keeping a board, authority granted by content-scoped mandates (the `mandates`
  table the organization craft's template seeds, `crafts/cabinet/templates/mandates.md`), every pair
  sharing the same ledgers; a presence file's name is a seat name in the form
  `<function>[-<topic>]-<hp>` (Rule-16 Presence), checked advisorily by the installed organization
  craft and printed by `dyad session name`. `flat`: one pair, one board, desks by row; no seat form is
  read. Seeded `m4`, the Operator's default: it authorizes nothing by itself — a charter is a
  preferences-zone row the Operator writes — and a one-pair system under `m4` is the Operating
  Guide's one-pair case (`crafts/cabinet/docs/operating-guide.md` §6).
- `paired-units` — the seats the Operator attends beside the leader, which is always attended (d-work
  #412; named `attended-seats` until #553, that name no longer read since dyad-operator 1.0 and refused by
  the presence guard, #604): a space-list of seat names, or of seat names without their `-<hp>` (`counsel` names every holder
  of the counsel seat), or `none`. The constraint it states is the Operator's span — how many seats the
  Operator sits at — never how many seats run: a hundred seats are one span while only the leader is
  attended and orchestrates the rest. Over the live seats the reading is a mode — every seat attended
  (M4), only the leader (M3), some (hybrid) — and a seat's counter-prompt is asked in its own chat when
  attended and relayed through the leader otherwise; `dyad session list` prints the set, the mode and
  each seat's route (Rule-16 Presence). Seeded `none`: by default only the leader is attended.
- `attendance-window` — how many days the records are read back to check `paired-units` (d-work #388,
  #412): a seat holds an own disposition when a provenance record whose `session:` line names it holds a
  disposition whose note holds neither `mandate #<id>` nor `relayed via`, anywhere, within the window. A
  live seat holding one that the preference does not declare prints `undeclared`; a declared seat holding
  none prints `warn`.
  Derived by `dyad session list` on every read, never written anywhere (the record is the proof, #295).
  Seeded `7`: a week of silence in a declared seat's chat is worth a warning; a longer or shorter window
  is the Operator's number.
- `relay-form` — how the leader, the cos, presents to the Operator a question a seat that is not attended owes
  (d-work #424): the Operator-bound direction of a relay. The seat-bound direction never varies — the Operator's
  words reach a seat verbatim (the core's relayed prompt, #253 R29). `verbatim`: the seat's question and its
  evidence passed through as the seat wrote them, the last line the seat's question. `brief`: the cos meets the
  Operator at the Operator's altitude and presents WHAT (the matter and its state), WHY (what it bears on) and HOW
  (the path, its strongest counter and the reconciliation — Rule-10's form applied by the cos to the seat's
  question), the seat's text quoted as citation and evidence, never the body, and the seat's evidence block
  verbatim; the last `Y/N` line is the seat's own question text, so the `Y` binds to what the seat asked
  (Rule-2, Binding). Either way the form authorizes nothing: it shapes what the Operator reads, never what a `Y`
  binds to. Seeded `verbatim`: the conservative default for a fresh install — the seat's own words pass through
  until the Operator has chosen the cos's brief.
- `intent-reading` — whether a prompt that opens a row, or reopens one from `backlog`, is first answered by an
  intent reading and its own question, before any plan is drafted (Rule-3 Plan and Answer grammar, Rule-15 phase 1;
  the criterion `dyad/dmc/intent-reading.jsonld`; d-work #615). A form preference: it changes how many questions a
  row takes and authorizes nothing.
  - `off` — two `Y` per row, plan and done: the plan-`Y` accepts the definition of done, and no intent question is
    asked. The value this template ships, and the reading of an absent key.
  - `on` — three `Y`: the intent question `Y/N: intent aligned for #<id> <title>?` comes first, its `Y` accepting
    the reading and the definition of done; `N` with text amends the reading; a bare `N` archives the row, since
    nothing was built. The plan follows the intent-`Y`, and `dyad plan check` warns on a prompt-opened row planned
    without one.
  - When to opt in: in the authoring system's ledger (602 rows, audited for d-work #615), 27 of 60 refusals restated
    intent or scope after a full plan had been written, and six of them refused a whole delivery. An operator who
    refuses plans for what they misread is the one the third `Y` saves.
  - Why `off` ships, in the authoring operator's words. First: "We’ve managed, albeit less efficiently, without
    intent-Y, so it should be an optional preference with a default being engaged. This means that most operators
    would benefit from three Y, while only the most masterful would benefit from the two Y". Then, reversing the
    default: "actually, i think most operators wouldn't appreciate the third 'Y' until they see it as an
    optimization. so default should be 'off'."
- `dwork-slug` — whether a row id is presented to the operator with its row slug after the number, `#<id>-<slug>`
  (Rule-3 What a `Y` binds and Ledger, Rule-16 Store; d-work #622). A form preference: it authorizes nothing, and a
  question still binds the rows it names by their numbers.
  - `on` — `dyad dwork new` refuses a row without `--slug`; replies, counter-prompt lines, relays and the CLI's
    listings read `#<id>-<slug>`, a row without a slug `#<id>`. The value this template ships.
  - `off` — row ids read bare; `--slug` is still accepted and stored, so turning the preference on later finds the
    slugs there. The reading of an absent key, so a system that has not added the key keeps today's behaviour and its
    run-books are not refused at `dwork new`.
  - Why: the authoring operator's prompt, "to assist operator with identifying d-work by its identifier, as a
    preference ("on" by default), d-work id should be presented along with 2-3 tag slugs after then number, e.g.
    "#621-release-intent-Y"".
- `awaiting-you` — the form of the line every reply ends with before its one `Y/N` (Rule-3 Batch disposition; d-work
  #646). A form preference: it authorizes nothing. What is owed is a fact of the records, never of this value: only the
  line's form is chosen here.
  - `on` — `Awaiting you: <n> <kind> (#id…), …`, or `Awaiting you: nothing.`, then `Coming: <n> <kind>`, each
    part only when non-zero. It counts the questions asked and not answered, by kind, a batch once, and then the rows
    ready for a question not yet asked. `dyad board` generates it from the asks the board records. The value this
    template ships, and the reading of an absent key, so an upgrading system shows the new line from its upgrade on.
  - `off` — the pending queue's counts, as before #646, while any is non-empty.
  - Why: the authoring operator's prompts, "use "Awaiting you" and fold it into a row", then ""Awaiting you" is a
    preference setting. falsify." and ""Awaiting you" is mechanically generated or can be mechanically generated.
    falsify.", and, setting the default, "default setting is "On" to display "Awaiting you:" ."
- `coming` — whether the closing line shows its `Coming: <n> <kind>` part (Rule-3 Batch disposition; d-work #665). A form
  preference: it authorizes nothing, and it hides only that part — the pending queue is still derived and recorded, and
  `dyad board` still prints its queue line.
  - `on` — the Coming part is shown after the Awaiting part, as `awaiting-you: on` describes. The value this template
    ships, and the reading of an absent key, so an upgrading system's line does not change; a value outside `on|off`
    reads as `on` at the board and is warned by the preferences guard.
  - `off` — the closing line is the Awaiting part alone, ending with its `.`.
  - Inert under `awaiting-you: off`, whose queue line is the Coming part's content.
  - Why: the authoring operator's prompt, "making "Coming:" a preferences setting with default of "on"".
- The tunables (d-work #590) — `hygiene-stale-days`, `hygiene-similar`, `hygiene-top`, the seven `inflight-*` keys,
  the three `sweep-*` keys, `promotion-ceiling` and `promotion-adjacency-min`: the numbers whose change alters what
  reaches the Operator, or when. Each value's one default is the `dyad:defaultValue` of the decision criterion that
  claims the key under `dyad:tunables` (`dyad/dmc/schema.md`; the record named in the row's `read by`), and the rows
  are seeded at those defaults. The code reads each through `dyadlib.tunable` when it runs: a value that is absent, or
  that does not parse or is outside the `allowed` cell, reads as the default. The `promotion-*` keys are read by the
  play-book (`dyad/playbooks/d-work.md`, Promotion), by the home's judgment, not by code. `attendance-window`, above,
  is the same kind (its record `dyad/dmc/attendance-check.jsonld`).
