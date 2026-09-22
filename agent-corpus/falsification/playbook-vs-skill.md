# Falsification record — a dyad play-book is similar to a Claude Skill (d-work #115)

**Claim (Operator, 2026-09-22):** dyad play-books (`dyad/playbooks/<name>.md`, vocabulary owner
Rule-3) are similar to Claude Code Skills (a `SKILL.md` with `name`/`description` frontmatter,
loaded into the turn on invocation — the model's judgment when a task matches, or the user's
`/<name>` — some running in a subagent and returning the result). No Skill exists in this
repository; the comparison is of the two designs, read from the play-book text
(`craft-instantiation.md`, its run-book `dyad/runbooks/craft.md`, Rule-3's Plan clause) and the
harness's own description of Skills.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Same shape: both are a named, reusable procedure kept as a document outside the rule/frame text and loaded when a recurring occasion arises, never a Rule. | Confirmed | The similarity is real at exactly this level — "procedure as data, read on occasion" — and it is the level the claim names. |
| 2 | Trigger. A play-book is *read by a Rule*: Rule-3's Plan clause makes the craft play-book mandatory on its trigger, inside the d-work the prompt opened, before the plan file is written; a Skill is invoked at the model's discretion or the user's slash command, and nothing in any Rule binds a turn to it. | Refuted as similar | Obligation versus option. A play-book is how a Rule delegates a decision procedure without becoming longer; a Skill is how a harness offers one. |
| 3 | Evidence. A play-book's steps *are a run-book*: each runs through the core runner (`dyad runbook run craft <step>`), which prints the native line, tests the postcondition and appends an event to `<runbooks>/events/craft.jsonl` that the completion reply cites (Rule-19 telemetry, Rule-20 resolves the id). A Skill's execution is the turn's tool calls — never a corpus record (Rule-7 property 2: the transcript never enters). | Refuted as similar | A play-book is mechanically evidenced; a Skill is inference. The difference is the one Rule-12 draws between code with a check and code without. |
| 4 | Home and governance. A play-book is core-craft content: `dyad/` (agent zone), versioned and released with the craft (Rule-11), a vocabulary term (Rule-6), falsified (#165's record), changed only by an agent-zone PR the Operator ratifies, installed into every dyad system with the craft. A Skill is harness configuration: a project Skill lives under `.claude/`, a path *no zone claims* — Rule-1 forbids committing it here at all without a zone change — and a user Skill lives on one machine, one kernel (Rule-14 property 2's class: per-kernel, per-host). | Refuted as similar in kind | A Skill is a library adapter of one kernel (Rule-14: the kernel row is "Claude Code *or another CLI inferencing agent*", replacement "another CLI inferencing agent"); a play-book is a System artifact that must survive the kernel being replaced. |
| 5 | Termination. The craft play-book ends at a plan-`Y` — it decides what to *propose*, "the Agent never instantiates either on its own"; a Skill typically executes (deploy steps, a review). | Survives, scoped | True of this play-book, not of the kind: a Skill could also end in a question, and a future play-book could execute clerical steps. Not a difference in kind. |
| 6 | Skills that "run in a subagent and return the finished result". | Refuted as a play-book analogue | That is delegation (#113, Rule-3 Scope's subagent clause), not a procedure-for-a-decision; it resembles the `delegation` preference, not `dyad/playbooks/`. |
| 7 | The claim inverted: a Skill could *carry* a play-book — a `SKILL.md` whose body says "read `dyad/playbooks/<name>.md` and run its run-book", giving this one kernel a discoverable entry point. | Survives, as the reconciliation | A Skill can be the *adapter* that surfaces a play-book to one harness; it can never *be* the play-book, because the play-book must also work when the kernel is another agent. If ever wanted: a Rule-14 library row and a Rule-1 zone for `.claude/` — a d-work of its own. |

**Verdict.** Similar in one respect only — a named procedure kept as data and read on a recurring
occasion (attack 1). Dissimilar in the three respects that make a play-book what it is: it is
*bound* (a Rule reads it), *evidenced* (its steps leave events), and *of the System* (versioned,
falsified, kernel-independent), where a Skill is discretionary, unrecorded, and a fixture of one
kernel. The accurate sentence is not "a play-book is like a Skill" but "a Skill is one harness's
way to *offer* a play-book" — the adapter, never the artifact.

No Rule, term or mechanism changes; nothing to sweep (Rule-5). Disposition: see ledger #115.
