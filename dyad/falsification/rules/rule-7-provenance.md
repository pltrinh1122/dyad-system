# Falsification record — Rule-7: provenance (ledger #164)

**Claim (as the Operator put it):** *"Per provenance rule, chat transcript from the session is
preserved in `agent-corpus` in the archival store."*

Stated as a fact, it was false at 859f7c9: no Rule-7 (row #54, `backlog`, disposed
`2026-09-12 N plan (not critical; operator retrieves chat log manually)`), no `archive/` or
`provenance/` directory, no transcript in the tree, and "archival store" in no Rule and no
vocabulary row. Read as a proposal, it was falsified before anything was written.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | It is not preserved; the claim describes nothing that exists. | Confirmed | Read as a proposal; the reply said so plainly, and that every earlier session's transcript is already unrecoverable. |
| 2 | A raw transcript carries live credentials. #135's session read the Gitea agent token with `docker exec dyad-git cat /data/dyad/agent_token`; that value is in its transcript, and GitHub remains a mirror, so a commit publishes it irreversibly. | Confirmed, decisive | Property 2: raw transcripts are never committed. What is preserved is text the Agent writes deliberately and a guard scans (FAIL_SHAPES), not a byte-stream it copies. |
| 3 | A remote session's transcript dies with its container; a gitignored archive directory preserves nothing. | Confirmed | Preservation must be a commit, so what is committed must be safe to commit (attack 2). Both constraints meet at one small written object. |
| 4 | The corpus already holds the provenance: the row's `disposed` column records every disposition in order (Rule-3 D4), plans record intent, incidents record departures. Rule-5 refuses a second owner. | Survives, scoped | The ledger records *that* a `Y` was given and of what kind, never the words. Rule-7 owns the verbatim text and nothing else (Boundaries, property 4); the row keeps owning the chain, and property 5 checks one against the other. |
| 5 | Size: 2.7 MB for one partial session, permanent in git history, cloned by every install. | Confirmed for raw jsonl; refuted for a written record (KBs) | Reinforces attack 2's survivor. |
| 6 | The Operator disposed `N` on this on 2026-09-12 ("not critical; operator retrieves chat log manually"). | Survives | That `N` stood until the plan-`Y` of #164. #54 and #55 are parents, re-opened by the prompt, never bypassed. |
| 7 | A rule that fires "at session end" never fires: no session reliably reaches its end (context exhaustion, container reclaim, a closed terminal). | Confirmed | Property 3: an entry is appended in the clerical commit of the event it records. Nothing waits for the end. |
| 8 | The Operator's own words can carry a secret (a pasted token). | Survives, scoped | FAIL_SHAPES fails the check on a GitHub token, a PAT, a PEM private-key header or an `Authorization:` value. A bare 40-hex only warns: a commit sha and a Gitea token are the same shape, and the Operator pastes shas constantly. |
| 9 | Cost: a Rule needs its block (Rule-4), this record (Rule-9), vocabulary rows (Rule-6), a frame import (#137's incident), a guard and test (Rules 12, 21), a register entry (Rule-20). Large, for something once called not critical. | Survives, scoped | Real, and the price of an owned concern; staging it would leave an unowned store, which Rule-5 refuses. Held down by one target and one store. |
| 10 | Reading the harness's per-session transcript file binds the core craft to one kernel implementation and to one host's home directory; Rule-14 property 2 admits "another CLI inferencing agent", for which no such file exists. | Confirmed, decisive | Property 2: the Agent never reads a harness file. It writes the entry from the prompt it received. Kernel-agnostic. |
| 11 | If the Agent transcribes, the Agent can paraphrase or omit; the record is only as honest as its writer. | Survives, scoped | Identical to every clerical write (`agent-corpus/falsification/e3-plan-gate.md` states it of the `Y plan` entry). Two fences: property 5's count check makes a dropped disposition a red check, and the Operator keeps their own copy of the chat — which is what the 2026-09-12 `N` already assumed. Stated in Enforcement as inference. |
| 12 | Retroactivity: 163 rows existed with no record; requiring one per row makes the check red on arrival. | Confirmed | `SINCE_ID = 164`. Rows below it need no record. |
| 13 | Worse than retroactivity: a *concurrent* session (Rule-16) opens rows above SINCE_ID without having loaded Rule-7. Row #165 existed before this branch was cut. | Confirmed | A missing record warns; it never fails. A red `main` is the wrong way to teach a Rule to a session that has not read it. Everything wrong *inside* a record that exists still fails. |
| 14 | "archival store" is undefined; Rule-6 forbids a Rule using an undefined term. | Confirmed | The phrase is not used. `provenance record` and `provenance store` are defined in the vocabulary, owner 7. |
| 15 | A blanket `*.jsonl` gitignore would untrack `workstation-corpus/runbooks/events/git-server.jsonl`, a Rule-19 event store. | Confirmed | No gitignore change. The guard fails only on a tracked `*.jsonl` under the d-work store, which keeps the whole mutation in one zone (Rule-1). |
| 16 | #55 asks for "clerical fence widening"; widening a fence weakens Rule-2's one mechanical guarantee. | Refuted | No widening was needed or made. `guards/agent/rows.py` already admits any direct commit under `<instance>/d-work/`; #164's own record pushed through it unchanged. |
| 17 | #56 asks to backfill Rules 1–6 "from the archived transcript". | Confirmed | There is no archived transcript and those sessions are gone. #56 is unachievable as written; reported for the Operator to re-scope or drop, never silently executed or closed. |
| 18 | An Operator prompt containing a `##` heading, a table row or a fence could reshape the file that stores it. | Confirmed | Property 1 puts every body inside a fence; `parse` reads to the closing fence, and a test asserts that a body containing a heading and a `# Provenance #99` line stays one entry's text. |
| 19 | The count check (property 5) is satisfiable by writing two empty `disposition` entries. | Survives, scoped | An entry with no fenced body fails. Beyond that the check is a count, not a semantics: it catches omission and invention, not a wrong transcription, which stays inference by attack 11. |

## Rule-5: coherence and orthogonality, pairwise
Rule-7 owns one concern: **the verbatim text of the Operator's prompts and dispositions**. No other
Rule owns it; Rule-7 owns nothing else.

| Rule | coherent | orthogonal |
|------|----------|------------|
| 1 containment | yes: the store is `agent-corpus/*`, agent zone; no transaction spans zones | yes: Rule-1 sees paths, Rule-7 sees content of one store |
| 2 no-self-ratify | yes: writing a record is clerical, never a ratification event; Rule-7 declares none | yes: Rule-2 owns who disposes, Rule-7 only stores what was said |
| 3 d-work | yes: entries are written on the events Rule-3 defines, in its clerical commits, under its fence | yes: Rule-3 owns the chain as data (`disposed`), Rule-7 the words; property 5 reads Rule-3's field and never writes it |
| 4 rule integrity | yes: Rule-7 carries the block (intent 1, target 1, boundaries 6, conditions 4) | yes: Rule-4 checks shape of Rules, Rule-7 stores prompts |
| 5 coherence | yes: this section | yes: Rule-5 owns the set's relations |
| 6 vocabulary | yes: two terms added, owner 7, and Rule-7 cites rather than defines | yes: Rule-6 owns definitions |
| 8 host mutation | yes: copying a transcript elsewhere on the machine is named in Boundaries as Rule-8's, not Rule-7's | yes: Rule-8 owns host actions; Rule-7 requires none |
| 9 falsification | yes: this record is Rule-9's form; the Agent's verdicts are Rule-9's, not provenance | yes: Rule-9 owns claims and attacks, Rule-7 the Operator's words |
| 10 proposal-framing | yes: the counter-prompt whose answer a record stores is framed by Rule-10 | yes: Rule-10 owns the asking, Rule-7 the storing of the answer |
| 11 distribution | yes: the Rule and guard are core craft, the store is instance; no instance path enters `dyad/` | yes: Rule-11 owns craft/instance |
| 12 verifiable code | yes: the guard carries `test_provenance.py`, 16 tests, run by `check_rule_12` | yes: Rule-12 owns the code/inference choice |
| 13 reuse over inference | yes: no new import; stdlib and `git` only | yes: Rule-13 owns import versus author |
| 14 System Infrastructure | yes: no new World row; property 2 exists precisely so no kernel implementation is assumed | yes: Rule-14 owns the manifest |
| 15 d-work phases | yes: a plan file is the Agent's text and is named in Boundaries as not a provenance record | yes: Rule-15 owns the plan file |
| 16 concurrent sessions | yes: one file per id, the same collision-free shape as rows and plans; attack 13's warning exists for its sake | yes: Rule-16 owns the store's concurrency, Rule-7 one store's content |
| 18 ops scripts | yes: an ops script is the Agent's delivery of a command, never an Operator prompt | yes: Rule-18 owns Operator-executed commands |
| 19 server instances | yes: an event records a command run, not words said | yes: Rule-19 owns run-books and events |
| 20 referential integrity | yes: `provenance.id->row` registered, resolver `row_exists` | yes: Rule-20 owns that the target exists |

Numbers 17 and 21 are retired from the core set (#160): their concerns are the sysarch craft's
`projection.md` and `guards.md`. The guard's placement and contract, and the entities card `describe`
gives, are stated against `crafts/sysarch/rules/guards.md` and Rule-11 property 1 instead; a Tended
craft sweeps its own rules by its own form (Rule-5 `## Sets`), so no pairwise line is owed here.

No gap found. What was searched: every Rule's Target and Boundaries for a claim on verbatim Operator
text (none), and every store for one already holding it (rows hold dispositions as data, plans and
records hold the Agent's text, incidents hold departures, events hold command runs).

| 20 | This record cannot state attack 10 in full: naming the operator's home directory or the agent CLI's private project directory spells a literal that `package_rules.txt` forbids inside the core craft, and a Rule's record is core craft (Rule-11 A6). | Confirmed, found by the guard | `package.py check` failed this file on exactly those two `string:` entries on its first run. Attack 10 is stated without the literals. The fence is right and the record was wrong: a package file that must quote a host path has no way to do it, which is the point — the path does not belong in the package, and neither does Rule-7's mechanism depend on it. |

Disposition: see ledger #164.

## Amendment — d-work #34 (2026-09-16, a relayed Operator prompt)
Property 4 gains one sentence: an Operator prompt relayed by another agent (Rule-3 Intake) is
entered verbatim as the message carried it, entry note `relayed via <session>`; the relaying
agent's words never; a defect's observation stays in the plan file. Attacks and pairwise: Rule-3's
record, amendment #34 (attacks 4, 5). The guard is unchanged: the entry kind is still `prompt`,
the note is free text the record form already admits. Disposition: see ledger #34.
