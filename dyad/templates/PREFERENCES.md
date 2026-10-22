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
| cli-pattern | industry-standard | `industry-standard` \| `explicit-python` | Rule-19 (run-book commands), Rule-11 (entrypoint) |
| batch-disposition-mode | off | `off` \| `on-ignore` \| `always` | Rule-2 (binding), Rule-3 (counter-prompt form) |
| ledger-pr-merge | ask | `ask` \| `agent` | Rule-2 (not-ratification list), Rule-1 (branch-fence case) |
| concise-mode | off | `off` \| `on` | Rule-10 (reply form), Rule-3 (what the reply carries) |
| accretion | explicit | `explicit` \| `implicit` | Rule-3 (scope, plan, ledger, completion), Rule-2 (binding) |
| host-path | workstation-corpus | a repo-relative directory | Rule-1 (host row of the zone table), Rule-14 (instance contribution) |
| host-zone | workstation | `workstation` \| `infra` | Rule-1 (host row of the zone table) |
| dwork-trace | always | `always` \| `on-demand` | Rule-3 (completion evidence) |
| organization | m4 | `flat` \| `m4` | Rule-16 (Presence: the seat-name form), Rule-3 (Ledger: what a session reads at start) |
| attendance-window | 7 | a positive number of days | Rule-16 (Presence: attendance, derived from the records) |

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
  each seat a cos keeping a cos-board, authority granted by content-scoped mandates (the `mandates`
  table the organization craft's template seeds, `crafts/cos/templates/mandates.md`), every pair
  sharing the same ledgers; a presence file's name is a seat name in the form
  `<function>[-<topic>]-<hp>` (Rule-16 Presence), checked advisorily by the installed organization
  craft and printed by `dyad session name`. `flat`: one pair, one board, cabinets by row; no seat form is
  read. Seeded `m4`, the Operator's default: it authorizes nothing by itself — a charter is a
  preferences-zone row the Operator writes — and a one-pair system under `m4` is the Operating
  Guide's one-pair case (`crafts/cos/docs/operating-guide.md` §6).
- `attendance-window` — how many days a disposition the Operator gave in a seat's own record keeps that
  seat *attended* (d-work #388): a seat is attended when a provenance record whose `session:` line
  names it holds a disposition noted neither `mandate #<id>` nor `relayed via` within the window;
  derived by `dyad session list` on every read, never written anywhere (the record is the proof, #295).
  Over the live seats the reading is a mode — every seat attended (M4), only the leader (M3), some
  (hybrid) — and a seat's counter-prompt is asked in its own chat when attended and relayed through the
  leader otherwise. Seeded `7`: a week of silence in a seat's chat reads as the Operator having left
  it, which is what a sliding window can say; a longer or shorter window is the Operator's number.
