# Incident mode O — a git write used as a read

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 3 of 140 rows.*

## Definition
A git command that writes the index and the working tree — `git checkout <ref> -- <path>`, in all
three rows — is used for a purpose a read would have served, so live state is overwritten as a side
effect the author did not intend and did not look for. The command's name suggests selection; its
effect is assignment, and the state it assigns over is whatever the tree currently holds:
uncommitted edits, a branch's own content, a hand-resolved merge.

**What would have to change.** The read would have to be done by a command that writes nothing
(`git show <ref>:<path>`), or the writing command would have to refuse while the tree it overwrites
holds anything not yet committed.

Boundaries against the neighbours it is most easily confused with:
- **N, a target named by an ambiguous pattern** — row 44 (`git checkout main -- .`) is the same
  command family and is assigned to N. Separating test: remove the ambiguity and does the fault go
  away? Row 44 with `origin/main` spelled becomes row 5 — a bounded overwrite, caught by `git
  status`; with the bare name it rewrote 156 files to a 328-commit-old state, so the ambiguity set
  the scale and is primary there. In these three rows there is nothing to remove: the ref was
  exactly the one meant and the verb was wrong. N's record states the same split from its side.
- **P, unplanned cleanup under momentum** — both touch git state the plan never named. Separating
  test: did the Agent intend to change state? P yes, deliberately; O no — the intent was a read in
  all three.
- **T, a stale or partial view of shared state** — both can destroy another party's work (row 62
  dropped a peer session's own incident row). Separating test: would a fetch have prevented it? T
  yes; O no — the refs were current and the verb did the damage.
- **D, the wrong object read** — D's fault is confined to what was concluded from it. Separating
  test: was the tree mutated? O yes in all three; D never.

## Incidents (3)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-22 | #114 | `git checkout <branch> -- agent-corpus/d-work/` destroyed three uncommitted ledger edits by overwriting from that branch's committed tree | a path-scoped checkout used to carry edits, over work that had never been committed |
| 2026-09-23 | #127 | `git checkout origin/main -- .` was run over an already-merged local branch to read one file, staging newer content across the tree and index | a path-scoped checkout used as a read; a read needs `git show <ref>:<path>`, which touches nothing |
| 2026-09-25 | #166 | `git checkout --theirs .` chained after a correct hand resolution overwrote the resolved file and silently dropped a peer session's row | the flag resolves unmerged paths; over an already-resolved path it is simply an overwrite |

## Pattern
One command family, three kinds of live state, four days: uncommitted ledger edits (row 10), a
merged branch's whole tree (row 5), a hand-resolved merge file (row 62). Each was caught by the
Agent's own next read — `git status` (5), re-reading the row (10), diffing the row list against
`origin/main` rather than trusting the resolution (62) — and never by a mechanism; nothing was
pushed in any of the three, and row 62's dropped peer row was restored before any commit.

The log counts the family itself, and its count crosses this mode's boundary with N. Row 5 calls
itself "the third occurrence of the mechanism #128 attack 7 names (after #110 and #114)"; row 62
calls itself "the fourth time in this instance (#110, #114, #127 before it)". Both counts include
#110, which is row 44 and is assigned to N here — so the log's own family is four rows and this
mode's three, with the fourth one boundary away.

Recurrence evidence. Every mitigation a consequence cell names is prose, and each was written before
the next occurrence: row 10 (2026-09-22) — "the safe form was a commit on the source branch first,
or `git stash`, never a path-scoped checkout over uncommitted work"; row 5 (2026-09-23) — "a read
needs `git show <ref>:<path>`"; row 62 (2026-09-25) — "after a hand resolution, the only safe next
command is `git add <path>`, and nothing that takes a side". Row 5 post-dates row 10's prose by one
day; row 62 post-dates both, and post-dates #128 attack 7, which had already named the mechanism.
Three statements, three recurrences after the first.

## Mitigations (phase 2)
**There is no mechanism at all for this mode.** Verified: `dyad check --list` prints 24 registered
guards and every one reads a store, a tracked tree or a commit range; none sits between the Agent
and a command it types. The conduct that carries it instead is Rule-8's first trigger
(`dyad/rules/RULE-8-host-mutation.md:23-24`) with the class table at
`crafts/sysadmin/rules/host-mutation.md:13-20` — a path-scoped checkout changes state and has a
stated undo, so it is **reversible** and authorized by the plan-`Y` of the plan that names it
(`RULE-8:38`); no row's plan names it. Rule-8's Enforcement is "Inference only, stated"
(`RULE-8:58`), and `workstation-corpus/CHANGELOG.md` holds no row for any of the three (grepped
today), which `RULE-8:58-59` makes a Rule-8 breach in each case — stated here as a finding.

Two shipped mechanisms are named for the part of the damage they *would* have made loud, since the
mode's reach is what phase 2 asks for:
1. **The row fence and the provenance transaction check** — `dyad/guards/agent/rows.py:94`
   (`check_disposed`), `rows.py:117` (`check_commit`), and `provenance.py`'s transaction half, whose
   "a record only grows — its earlier entries stay word for word and the file is never deleted"
   clause is `dyad/rules/RULE-7-provenance.md` Enforcement. Moment: `dyad check --guards
   --pre-push` (`dyad/hooks/pre-push:4`) over each non-merge commit being pushed. **Shipped.**
   Reach: row 10's three destroyed ledger edits, had they been reconstructed wrongly rather than
   "redone deterministically", would have failed at that push. It reaches nothing of rows 5 (156
   files of code and craft content) or 62 (an audits file outside `<instance>/d-work/`). And it
   reaches row 10 only *after* the destruction, as a check on the repair.
2. **The incident-log shape check** — `dyad/scripts/incidents.py:88-107` (`check_log`), run through
   Rule-12's suite by `dyad/tests/test_incidents.py` `LiveTests`, deliberately a script and not a
   registry guard (`incidents.py:14-19`; Rule-3 Mechanisms says the same, pending row #170). It
   validates cell count, date parse, a `#<id>` in the d-work cell and non-empty `what`/`cause`/
   `consequence` — and nothing about *which* rows exist. Row 62's consequence cell reports "the
   parser green" as part of the recovery; this is the precise statement of what that green proved:
   the file was well-formed with a peer's row missing, and would have stayed green had the row not
   been restored. A silently dropped row is invisible to every mechanism in the tree.

## Remediation candidate, under attack
A harness-side deny rule — the Operator-side fence `RULE-8:19-21` places outside the corpus —
refusing the whole form `git checkout <ref> -- <pathspec>` and the flags `--theirs`/`--ours`, at the
moment the tool call is issued, before the command runs. The safe substitutes (`git show`, `git
restore`, `git add`) are unaffected.

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | It is not the dyad's fence. `RULE-8:19-21` makes the harness permission mode an Operator-side fence outside the corpus; the craft cannot ship it, Rule-12 property 1 cannot test it, and no completion reply can cite it as a guard result. | confirmed | "A fence the dyad builds" does not survive. What survives is a fence the Operator may set, carried in this record and in a row, with the corpus holding the proposal and not the mechanism. |
| 2 | `git checkout <ref> -- <path>` has a legitimate use: taking one file from another ref deliberately, which is exactly what row 10's *intended* operation would have been had the edits been committed first. A blanket deny refuses real work. | survives (scoped) | Only as a deny the Operator lifts per command, which is what the harness mode already is — the refusal makes the write deliberate and stated instead of incidental. A blanket, unliftable deny does not survive. |
| 3 | Coverage: the form-based deny reaches rows 5 and 10 (and N's boundary row 44); row 62's command is `git checkout --theirs .`, so the pattern must cover the side-taking flags too — and row 62's real fault was *chaining* the command after a hand resolution in one line, which no pattern over a single command's text can see as "after a resolution". | survives (scoped) | Reaches 2 of 3 plus the boundary row. Row 62's chaining is invisible to it, and nothing proposed here reaches that: the only thing that knows a resolution just happened is the index's unmerged-path state, which no fence in the corpus reads. |
| 4 | Easy agreement (Rule-9 Conditions): "a read needs `git show`" reads as obviously right, so attack it as the *mitigation* rather than as advice. It was stated three times in three rows and failed three times, and the play-book's phase 2 exists because of exactly that. | confirmed | Prose does not survive as a mitigation for this mode. The claim survives as correct advice and is refuted as a fence, which is the distinction this section is for. |
| 5 | A corpus-side alternative exists and should be attacked before the host-side one is accepted: a `dyad` read verb wrapping `git show`. It fails Rule-13 property 1 (nothing recurring is being replaced — `git show` already exists and is already safe) and pays Rule-12 property 1's cost for a wrapper that adds no check. | confirmed | The corpus-side candidate does not survive, which is why the surviving candidate is host-side despite attack 1. Stated so the exit is read as constrained, not as preferred. |

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** The row would read: *set a host-side deny rule on
`git checkout <ref> -- <pathspec>` and on `git checkout --theirs|--ours`, firing at tool-call time
before the command runs, liftable per command by the Operator; record its text in
`workstation-corpus/` where the instance's host facts live, and name in the row that a read is `git
show <ref>:<path>`, a restore is `git restore`, and the only safe command after a hand resolution is
`git add <path>`.* It would have caught rows 5 and 10, and N's boundary row 44; it would **not** have
caught row 62, whose fault was the chaining and not the form.

Stated against the exit: the fence lives outside the corpus by `RULE-8:19-21`, so the row delivers a
proposal and a record, never a guard, and no completion evidence will cite it. Neither exit-3 Rule
applies — the fault is not in a hosted service (Rule-14 property 2) and is not a judgment no script
could decide (Rule-5 Enforcement), since the command form is a string match; what the corpus lacks
is a moment at which to run one, not the ability to decide. Proposed only — the mode is not closed
here, and row 62 is unreached by anything above.

## Delta 2026-10-24 (#259 revision 5; 3 → 4 rows)
**Row added:** 190 (#331: `git reset --soft origin/main` as a sync, which assigned the pre-merge index
over a peer's three files). **Mitigations re-read:** none in the tree. **Exit:** exit 2 as proposed
(#276 `backlog`); the row's own rule — `merge --ff-only` or `reset --keep`, never `--soft` — would join
the deny-rule candidate's list.

## Delta 2026-10-26 (d-work #472, seat audit-e73be78c)

Rows from the delta of 2026-10-26 (index `2026-10-10-incident-failure-modes.md`, its section of that date, where the reconciliation, the code read at `d36b1bd` and the attacks are).

- **225** (2026-10-20, #348): `git merge --ff-only origin/main` (284 commits) run to read the current Rules and allocate an id. Its cell says P, but this record's definition covers it word for word: a git write used as a read, where `git show origin/main:<path>` existed.
- **231** (2026-10-25, #346; placed here by #463's note and confirmed by the second view): `dwork state 346 done` run to read its refusal. The dyad's own verbs have no read-only form, so #464 (`backlog`, R1, `dwork state … --check`) is the fence to build. The definition widens from git to the dyad's CLI. The git face stays conduct, because its non-writing read exists. **6 rows.** Status: exit 2 named, unbuilt.
