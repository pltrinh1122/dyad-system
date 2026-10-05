# Falsification — trace instrumentation is organic and free; traces only when optimizing (d-work #215)

**Claims (Operator, 2026-10-05, verbatim):**
- A. "instrumentation for trace is in place is organic and adds no additional overhead. falsify."
- B. "trace report should only be activated when we're optimizing for performance. falsify."

**Context.** #213 builds `dyad dwork trace`. It reads the harness transcript, git and the ledger, and
writes `<instance>/d-work/traces/<id>.md` in the Done ledger commit (revision 2). As planned, Rule-3
makes the completion evidence cite it at every Done.

**Observed (2026-10-05).**
- The harness writes a transcript per session under `~/.claude/projects/<slug>/`: here 59 `.jsonl`
  files and 90 MB, the main one 40 MB.
- Subagent and workflow transcripts are separate files (`<session>/subagents/`, `workflows/`).
- This is a cloud container: "the container is reclaimed after a period of inactivity", and
  "anything worth keeping needs to be committed and pushed".

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A1 | Every input the trace reads is already written by something that runs anyway. | **Survives, scoped to this kernel.** | Transcript timestamps, tool-call and tool-result times, and token usage are written by Claude Code whatever we do. Git commit and merge times and the ledger's dated entries exist already. No probe, timer or log was added. On another kernel (Rule-14 allows "another CLI inferencing agent") there may be no transcript, and the trace degrades to git and ledger events, as #213 specifies. |
| A2 | It adds no overhead. | **Refuted, as worded; small.** | Collection is free (A1). Producing and using a trace is not. Each trace parses the whole session transcript, which grows with the session (40 MB now), so the cost grows per d-work. It also costs one tool call, the inference to read the output and cite it in the completion reply, and one more file in the Done commit. That commit is ledger-only, so there is no extra push, PR or suite run (#214). The seconds and tokens are #214's measurement, not yet taken. |
| A3 | Subagent work is in the same instrumentation. | **Survives, with a cost.** | It is, in separate files. A trace that counts subagent time must open them too, which adds to A2's parse. |
| B1 | A trace is useful only while optimizing. | **Refuted.** | A bottleneck is defined against a baseline: #212's bottleneck line compares with the median of traced d-works. Traces taken only during optimization have no normal d-work to compare with, so they show where time went, but not whether that is unusual. |
| B2 | Since the instrumentation is organic (A1), traces can be made later, on demand, for any d-work. | **Refuted in this environment.** | The transcript is per machine and never committed (Rule-7 property 2). In this cloud container it is lost when the container is reclaimed. A d-work not traced before then can never be traced; only its git and ledger skeleton remains. "Activate later" silently loses the time buckets for every d-work done in between. On a persistent host the attack is weaker. |
| B3 | Always-on costs too much. | **Refuted, provisionally.** | By A2 the cost is one parse, one tool call and a few hundred tokens of citation per d-work, with no suite run. Against a d-work's typical 3 to 5 PR cycles that is marginal. #214's measurement can still overturn this, and if it does, B survives. |
| B4 | Whether to trace is a policy the Operator should be able to switch. | **Survives.** | Behaviour that varies by the Operator's intent belongs in a preference (`preferences-corpus/`, Rule-2), not hard-wired in Rule-3. |

**Survivor.**
- A holds for collection and fails for use. The instrumentation is organic. Producing and citing a
  trace costs a parse that grows with the session, one tool call and some tokens, and no suite run.
  The exact figure is #214's.
- B is refuted as a default. Traces made only while optimizing have no baseline. In an ephemeral
  container the transcript they need is gone by the time anyone decides to optimize.
- The Operator's intent survives as a switch. A preference `dwork-trace: always | on-demand`, read by
  Rule-3, defaulting to `always`. With `on-demand`, a trace is made only when the Operator prompts for
  one, with the stated risk that d-works whose session has ended can no longer be traced.
- This revises #213 item 5 from an unconditional Rule-3 bullet to one conditioned on the preference.
  The preference itself is a separate preferences-zone PR (Rule-1).

Disposition: see ledger #215.
