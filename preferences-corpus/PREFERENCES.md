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
| delegation | plan-and-execute | `none` \| `plan-and-execute` | Rule-3 (subagent clause) |
| cli-pattern | industry-standard | `industry-standard` \| `explicit-python` | Rule-19 (run-book commands), Rule-11 (entrypoint) |
| batch-disposition-mode | on-ignore | `off` \| `on-ignore` \| `always` | Rule-2 (binding), Rule-3 (counter-prompt form) |
| ledger-pr-merge | agent | `ask` \| `agent` | Rule-2 (not-ratification list), Rule-1 (branch-fence case, #23) |

- `merge-disposition`
  - `separate` — every PR merge is its own counter-prompt (`Y/N: merge #N?`) before the
    d-work's completion counter-prompt. This duplicates the plan-`Y` (Rule-3) at the PR;
    choose it only if the duplicate is wanted.
  - `with-done` — the completion counter-prompt names the d-work's unmerged PR(s). The
    Done-`Y` is the Operator's verification that the output matches intent; the Agent then
    merges as clerical execution. Two `Y`s per d-work: plan and Done. A PR whose d-work is
    *not* yet done still needs its own merge `Y`.

- `import-licenses` — licenses under which code may be imported into the package (it is
  redistributed under Rule-11). Tools merely invoked are not subject to it (Rule-14 rows).
- `import-support` — the maintenance and packaging evidence an import must show.
- `delegation` — `plan-and-execute`: subagents draft plan files and execution branches so the
  main Agent stays free for the next prompt; the main Agent alone writes rows, asks the plan-Y,
  pushes, opens PRs and asks Done. `none`: subagents read, search and draft text only.
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
