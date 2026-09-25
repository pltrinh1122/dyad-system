# Play-book: ds-report-incidents (an anonymized, redacted incident report for a third party) — d-work #166

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision; its steps are a run-book. This one turns an instance's incident log into **one file
that is safe to hand to a party outside the dyad** — a VAR, an auditor, an insurer — grouped so that
reader can use it, and stripped of both senses of *IP*: the host's identity and the practice's
intellectual property. Steps: `dyad/runbooks/ds-report-incidents.md`, run through
`dyad runbook run ds-report-incidents <step>`, the core runner, so each step leaves an event.
Read on an Operator prompt; no Rule requires this report (contrast `incident-hardening.md`, which
Rule-3's Incidents clause requires).

## Trigger
An Operator prompt asks for an incident report that will leave this system. The play-book runs inside
the d-work that prompt opened. It is **not** triggered by the hardening exercise, which reads the same
log inward — group a failure mode, close it with a fence — and never produces a deliverable.

## Parameters
| name | default | what it selects |
|------|---------|-----------------|
| `LEDGER` | `${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md` | the incident log to report on (Rule-11 property 3: an instance path through the one instance location) |
| `AUDIENCE` | — required | the party the report is built for, as they should see themselves named on it |
| `LEVEL` | `standard` | `standard` — groups, counts and one summary each; `minimal` — groups and counts only, no prose |

No craft or core file names any recipient: the audience is this parameter, and the recipient list is
instance data (Rule-11 property 1).

## Redaction: allow-list first, deny-list as the fail-closed gate
A deny-list can catch a hostname, an IPv4 literal, a credential shape. It cannot catch a sentence that
explains a guard's internals in ordinary English — and that is what an incident row *is*. So:

1. The report is assembled by **allow-list**. Only the fields the run-book's Project step names may
   appear in it. Nothing is copied from the log verbatim.
2. The **deny-list is a second gate**, run over the assembled output before it is written and again in
   Verify. If any forbidden shape survives, nothing is written. Fail closed, never "redact and hope".

Three classes, defined by the disclosure craft's Tended rule `crafts/disclosure/rules/redaction.md`:
- **Class A — identity: removed.** Hostnames, absolute paths, IP literals, email addresses, session
  ids and names, repository URLs, PR numbers, personal names, and the credential shapes
  `dyad/guards/agent/provenance.py` already knows (reused, Rule-13).
- **Class B — proprietary substance: pseudonymized, never deleted.** Rule numbers, guard, module and
  craft names, file paths, vocabulary terms and ledger ids become stable pseudonyms from the map at
  `<instance>/disclosure/pseudonyms.md`, which never leaves the system. Deleting them would leave a
  report of dates; pseudonymizing them keeps what a third party can act on — counts per subsystem,
  repeated failure modes, whether a class of fault is closed.
- **Class C — retained.** The date, the failure-mode class (vocabulary, Rule-3), the consequence shape,
  the mitigation status, and — at `LEVEL=standard` — one Agent-authored external summary per group,
  written for this audience and passed through both gates like everything else.

## Steps
The run-book, in order; the events are the evidence:
1. `survey` — the log's live row count and latest date, and the watermark of the last report built from
   it. Equal numbers are the no-op: the report on disk is current, and Verify still runs.
2. `group` — the failure modes present, by the same grouping `incident-hardening` uses (cited, not
   duplicated: one exercise's grouping, two uses).
3. `map` — pseudonyms for anything Class B that the map does not yet carry, allocated stably so two
   reports of different dates are comparable.
4. `summarize` — the Agent writes one external summary per group. Inference, and the only inference in
   the chain; both gates apply to its output.
5. `project` — `dyad project disclosure` writes the deliverable.
6. `verify` — the gate re-run over the written file, plus the redaction manifest: how many values of
   each class were removed or replaced.

## Delivery
The file is generated and untracked; it is written under the instance so the Operator can open it, and
it is self-contained so it hand-carries or emails as one file.

**Before it leaves the system the Agent asks `Y/N: deliver <report> to <audience>?`** and does not
send, attach, upload or print it otherwise. This is conduct, not a declared ratification event: only an
Agent Rule may declare one (Rule-2), a play-book is not a Rule, and a Tended rule may not bind the
Agent's process (Rule-4). The Rule amendment that would make it a declared event is a backlog row of
d-work #166.

## Evidence
The completion reply (Rule-3) cites: the event ids of the steps run
(`<runbooks>/events/ds-report-incidents.jsonl`), the report's path and sha256, the redaction manifest's
counts, the audience and level, the `verify` step's observed pass, and the PRs by number and zone. A
step run outside the runner is an incident (Rule-3).
