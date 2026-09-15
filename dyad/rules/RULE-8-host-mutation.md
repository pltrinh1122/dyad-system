# Rule-8: host mutation

**Intent:** Classify, authorize and record every host action the Agent takes.
**Target:** a host action

## Boundaries (out of scope)
- Repo transactions — Rule-1. Who ratifies — Rule-2. When work opens and closes — Rule-3.
- What the host *should* look like — Tended Rules (Rule-4 classifies them); Rule-8 reads
  them, never writes them. Which actions fall in which class, the read-before-act procedure and
  the change log's columns — the active craft's host-mutation rule
  (`crafts/sysadmin/rules/host-mutation.md`, a Tended Rule; #155); Rule-8 reads it and keeps the
  authorization each class needs and the record's existence.
- The memory cache (`~/.claude/.../memory/`): not a host action; Rule-2 and the frame
  convention govern it.
- The harness permission mode: an Operator-side fence outside the corpus, per command; it
  neither replaces nor is replaced by this Rule.
- The form in which a command the Operator runs for the Agent is delivered — Rule-18 (ops
  script); Rule-8 keeps its class, authorization and change-log row.
- A server instance's lifetime, supervisor and run-book — Rule-19; Rule-8 keeps the class and
  change-log row of every command that starts, stops or alters it.

## Conditions (triggers)
- The Agent is about to run anything on the machine that is neither a repo transaction nor
  read-only.
- A plan names a host action (the class is stated there for the Operator's review).
- A host action has completed (change log row, same d-work).
- Before any reversible or destructive host action the Agent reads every rule of the active
  crafts (`crafts/*/rules/`) and of the host (`workstation-corpus/rules/`); the procedure (once
  per d-work, again if it changed) is the craft rule's. A conflict between the planned action
  and a Tended Rule, or doubt about a Tended Rule's meaning, is a blocking question: the Agent
  stops and asks, never resolves it, never edits a Tended Rule to fit a plan. A Tended Rule that
  binds the Agent's process is obeyed conservatively and reported as misplaced (Rule-4 guard). (E6)

## Classes
Three classes, named here; which actions fall in which class, with examples, is the active
craft's host-mutation rule (`crafts/sysadmin/rules/host-mutation.md`):
- **read-only** — free.
- **reversible** — authorized by the plan-`Y` of the plan that names it, with its undo.
- **destructive** — needs its own counter-prompt naming the action, even inside a planned
  d-work.

## Conduct
- Detect, don't dispose: what the Agent finds on the host is reported; fixing it unplanned is
  a new plan.
- Every reversible or destructive action gets a row in `workstation-corpus/CHANGELOG.md` in a
  workstation-zone PR of the same d-work; the row's columns and its guard (`sysadmin/changelog`)
  are the craft rule's. A run-book command's event (Rule-19) is its change-log evidence: the
  row's outcome cites `event: <id>` instead of a pasted transcript, and Rule-20 resolves the id.
- A host action never runs from a subagent (Rule-3, Scope).
- An action the Operator runs for the Agent is delivered as an ops script (Rule-18), never as
  an inline block; its outcome is still this Rule's change-log row.

## Ratification events
- Answering `Y` to a destructive-action counter-prompt (`Y/N: run <action>?`). Rule-2 applies
  by reference; the `Y` binds to the named action only.

## Enforcement
Inference only, stated. The change log is the record; its absence for a known mutation is a
Rule-8 breach reported in the completion reply.

## Provenance
Operator gap E5 (audit 2026-09-12, completeness). Falsified; see
`../falsification/rules/rule-8-host-mutation.md`. Kernel since #155: the class table, the
read-before-act procedure and the change-log columns moved to the sysadmin craft.

Set: System Requirements.
