# Play-book: d-work trace (core craft, `dyad-operator`; #213, format agreed in plan #212)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision; its steps are a run-book. This one decides where a d-work's time went, so that the
Operator and the Agent read a bottleneck by the same measures instead of by impression — the measurement
done by hand three times before it became code (#204 by workflow, #212 twice; Rule-13 property 1). Read by
Rule-3's Completion counter-prompt clause: the completion evidence cites the d-work trace. Where the trace is
stored and when it is written: plan #213, revision 2. Steps: `dyad/runbooks/dwork-trace.md` — `locate`,
`trace`, `compare` — run through `DWORK=<id> dyad runbook run dwork-trace <step>`, the core runner, so each
step leaves an event. The code the steps call is `dyad dwork trace` (`dyad/scripts/trace.py`).

## Parameter
`DWORK` — the id of the d-work to trace. The run-book's steps take it from the environment, exactly as the
incident-hardening run-book reads `LEDGER` and the craft run-book `CRAFT`:

    DWORK=<id> dyad runbook run dwork-trace trace

The transcript is not a parameter of the run-book. `dyad dwork trace` reads the newest one of the working
tree's harness project directory (`projects/<slug>/` under the harness's home directory, `~/.claude/`; the
slug is the working tree's path with every non-alphanumeric character a `-`). When that is not the session
that worked the d-work, the Agent runs `dyad dwork trace <id> --transcript <path> [--transcript <path>]…`
itself, with `--out` at the Done-`Y`, and names the paths in the reply.

## Trigger
The preference `dwork-trace` (`preferences-corpus/PREFERENCES.md`; Rule-3, Completion counter-prompt)
decides which d-works are traced: `always` (the default) — every d-work; `on-demand` — only a d-work whose
Operator has prompted for a trace, and any d-work the Operator names later. A traced d-work is traced at two
moments, both inside it:
1. **Done-ready.** The completion evidence is being gathered and the Done question is about to be asked.
   `dyad dwork trace <id>`, without `--out`, prints a **preview**: the window runs from the first anchored
   prompt to the transcript's last record — the Done question being asked. Nothing is written.
2. **Done-`Y` received.** The reply that receives it records the disposition first (`dyad dwork state <id>
   done -d … --said …`, which writes the row and its provenance entry in the working tree), then runs the
   run-book's `trace` step (`--out`) before the clerical Done ledger commit, so that commit carries the
   trace with the row and the record. The window now runs through the Done-`Y`: it covers the work PR's
   push, its evidence run and the Operator's wait on the Done question. The merge comes after that commit
   (Rule-3: the record of the `Y` precedes every merge it ratifies), so it is the clerical tail, visible in
   git and never in the trace (plan #213, attack 3).

A d-work traced later, on the Operator's word, is traced the same way: the window is set by the anchors,
never by when the command runs.

## Default
Under `always`, trace it, at both moments. The completion reply prints the preview's bottleneck line and agent-side seconds
beside the median of the traced d-works, so the Operator reads them before answering. At the Done-`Y` the
`trace` step writes `<instance>/d-work/traces/<id>.md`, the **trace store**: it lies under
`<instance>/d-work/`, so the Done ledger commit stays ledger-only (Rule-3 Ledger: clerical) — no extra PR,
push or suite run — and the main fence and the plan gate's ledger-only exemption admit it as they admit the
row. A d-work whose transcript is absent — another kernel, a session whose harness keeps none (Rule-14: Claude
Code is one kernel row, "another CLI inferencing agent" its replacement) — is still traced: the trace holds
the git and ledger timeline and says the buckets are absent. That is a stated limit, never a reason to skip
the step.

## Format
One file per d-work, `<instance>/d-work/traces/<id>.md`, opening `# Trace #<id> — <title>`, then a header line
naming its sources (the row, the provenance record, the plan file, git HEAD and every transcript read, with
counts of each), then five sections in this order:

1. **Timeline.** Every event in UTC order with its actor: each anchored provenance entry (the Operator's
   prompt, each disposition), each counter-prompt asked, each commit and merge (git, a ledger-only one
   marked), each suite-kind, GitHub and subagent call with its duration. Events after the Done-`Y` are
   marked as the clerical tail; events after a preview's window as after the window.
2. **Buckets of wall time,** over the window — the first anchored prompt to the Done-`Y`; in a preview, to
   the transcript's last record; to the last d-work event when the record holds a Done the transcript does
   not, said under Limits. Every second is in exactly one bucket, and the buckets sum to the window:
   - Operator partition: **operator** — a reply ending in a `Y/N:` line, to the Operator's next message;
     **idle** — a reply with no `Y/N:` line, to the Operator's next message.
   - Agent partition: **inference** — a tool result or a message, to the Agent's next tool call or reply;
     **background** — a finished turn, to a background task's notification; and the mechanical kinds by
     tool-call duration (call to result): **suite** (a Bash call running `git push`, `check --evidence` or
     `--tests` whose result shows a test run, `Ran N tests`), **guards** (a `git push` whose gate ran guards
     only — a ledger-only or empty range, Rule-12 p2), **github** (a GitHub tool, or Bash `gh api`), **git/local** (any other Bash), **subagent**
     (Agent, Task or Workflow), **other** (any other tool).
   - Overlap is counted once: calls made together take the first kind of the order suite, guards, github,
     git/local, subagent, other; a background launch is counted for its launch only and listed under the
     table, its run never summed a second time.
3. **Counts.** Commits (ledger-only among them) and merges, ledger and work (git); PRs created by head
   branch (`ledger-…` is a ledger PR) and merged, full-suite runs and guards-only push gates, tool calls and output tokens
   (transcript, the window only).
4. **Bottleneck.** The top three buckets by share; then `**Agent-side:** <n> s` — inference plus every
   mechanical kind, the Operator's partition excluded, because only that is what a change to the system can
   move — beside the median of every other trace in the store.
5. **Limits.** Every provenance entry left unmatched or ambiguous; a preview, said as one; shared turns (a
   `Y/N:` naming this d-work with others: counted whole, split evenly only in the line that names them);
   turns asking only about other d-works; agent-side segments of fifteen minutes or more (a restart, a sleep
   or a lost turn reads as its bucket); more than one harness session in the window; and always: inference
   is a wall gap and overstates the model's own time, and the trace stops at the Done-`Y`.

**Anchors.** Each provenance entry (Rule-7) is matched to the Operator message that carried it —
whitespace-normalized, equal, or contained when the entry is twenty characters or longer — in record order,
each after the previous anchor. A disposition is anchored only to a message answering a `Y/N:` line that
names `#<id>`; a prompt that matches twice is ambiguous. An entry that is not anchored is reported, never
guessed.

**What a trace never holds.** Transcript text: only timestamps, durations, tool names and numbers derived
from it. The transcript is read in place, never copied and never committed (Rule-7 property 2). Git
subjects and provenance notes are corpus text already, and appear as they are.

**The store's shape.** `dyad/scripts/trace.py` `check_store` holds it well-formed — every file `<id>.md` for
an existing row, its first line `# Trace #<id> — <title>` naming that same id, its five sections in order —
and `dyad/tests/test_trace.py` runs it over the live store with Rule-12's suite on every push.

## Reading
- **The bottleneck line first.** The top bucket names where the window went. A mechanical bucket on top is a
  system cost a fence, a cache or a skipped step can move; inference on top is the model's turns, which a plan
  that asks less or delegates moves; operator on top is the Operator's wait, which the system can only shorten
  by asking fewer or batched questions (`batch-disposition-mode`).
- **Agent-side against the median.** An agent-side figure well above the median of the traced d-works is
  worth one sentence in the completion reply naming its top agent bucket; one at or below the median needs
  none. The comparison is between d-works of different sizes, so it flags, never judges: a large d-work is
  expected to be slow, and the timeline says whether the time went to the work or around it. A preview's
  figure lacks the Done wait the stored traces hold; the agent-side figure, which excludes it, is the one to
  compare.
- **Limits before conclusions.** A trace with unmatched anchors, shared turns or long agent-side segments
  is read with them: a lost turn reads as inference, and a shared turn's seconds belong partly elsewhere.
- **No verdict without a second trace.** One slow d-work is a fact about that d-work; a bucket that leads
  across several traces is a claim about the system, and it is falsified (Rule-9) before any plan encodes it.

## Evidence
For a traced d-work (Trigger: the preference `dwork-trace`), the completion reply (Rule-3) prints the preview's bottleneck line and agent-side seconds with the median,
every unmatched or ambiguous anchor from its Limits, and the transcript paths when they are not the default.
The reply that receives the Done-`Y` names the trace file its Done ledger commit carries and the event id of
the `trace` step (`<runbooks>/events/dwork-trace.jsonl`). A trace made outside the runner is stated as such.
