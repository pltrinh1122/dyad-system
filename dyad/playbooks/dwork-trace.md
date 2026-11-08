# Play-book: d-work trace (core craft, `dyad-operator`; #213, #626)

Where a d-work's time went, read by the operator and the agent by the same measures. Read by Rule-3's Completion
counter-prompt: the completion evidence cites the trace. Steps: `dyad/runbooks/dwork-trace.md` — `locate`, `trace`,
`compare` — each a call of `dyad dwork trace` (`dyad/scripts/trace.py`), which decides the window, the anchors, the
buckets and the gate kind (`dyad/dmc/trace-window.jsonld`, `trace-anchor`, `trace-bucket`, `trace-gate-kind`). The
agent runs the command directly, not through the runner, whose event a ledger-only Done commit cannot carry (#247);
`DWORK=<id> dyad runbook run dwork-trace <step>` stays for a run that wants an event.

## Parameter
The d-work's id: `dyad dwork trace <id> [--transcript <path>]... [--out [--said-file <f>]]`; in the run-book, `DWORK`,
and for `trace` also `SAID`, the file holding the operator's Done words. The transcript defaults to the newest of the
working tree's harness project directory; another session's is named with `--transcript`, and the reply names it.

## Trigger
The preference `dwork-trace`: `always`, every d-work; `on-demand`, one the operator asked to trace. Two moments:
1. **Done-ready** — `dyad dwork trace <id>` prints a preview, its window to the transcript's last record; nothing is
   written.
2. **Done-`Y` received** — write the operator's words to a file, run `dyad dwork trace <id> --out --said-file <f>`,
   then record the disposition from the same file; under `--land` a `land <instance>/d-work/traces/<id>.md` line before
   the `state` line, so the Done record commit carries the trace. `--out` with no Done words refuses: a stored trace is
   never a preview (#592). The merges and the close come after and are not in it (#202).

## Default
Trace at both moments. The trace store is `<instance>/d-work/traces/<id>.md`, under `<instance>/d-work/`, so the Done
record commit stays ledger-only. A d-work with no transcript is still traced from git and the ledger, its buckets
marked absent.

## Format
`# Trace #<id> — <title>`, a sources line, then five sections in order — **Timeline**, **Buckets**, **Counts**,
**Bottleneck** (the top three buckets and `**Agent-side:** <n> s` beside the store's median, the agent partition as a
table, and `suite + guards` against `inference`), **Limits** (every unmatched or ambiguous anchor, shared turns, long
segments, range-booked pushes; inference is a wall gap). A trace holds no transcript text, only timestamps, durations,
tool names and numbers (Rule-7 property 2). `trace.check_store` holds the store's shape; `dyad/tests/test_trace.py`
runs it.

## Reading
Read the bottleneck line by `dmc:trace-bottleneck`, and the agent-side figure against the median by
`dmc:trace-agent-side`. Read Limits before conclusions. One slow d-work is a fact about it; a bucket leading several
traces is a claim, falsified (Rule-9) before any plan encodes it.

## Evidence
The completion reply prints the preview's bottleneck line and agent-side seconds with the median, every unmatched or
ambiguous anchor, and any non-default transcript path. The reply that receives the Done-`Y` names the trace file its
Done record commit carries; a trace run through the runner names its event id.
