# Incident mode D — the wrong object read

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10, 9 of 140 rows.*

## Definition
The mechanism: a read was made at the moment of use, and the thing read was not the thing in
question — a neighbouring function instead of the one the gate calls, a docstring instead of the
function body, a different branch of the same repository, a different ledger numbering space, one
module literal instead of the module that qualifies it, a file name instead of the host it was
supposed to describe. The reading is accurate; the conclusion is true of what was read and false of
what was asked. Because the instrument worked and returned a clean answer, the fault carries the
authority of evidence: six of the nine reached a stored plan file, a reply to the Operator or an
ADR as a verified statement.

**What would have to change.** Every claim about a mechanism must name the object it was read
from, and the object must be shown to be the one the question is about before the conclusion is
stated.

Boundaries against the neighbours it is most easily confused with:
- **C, a value stated from memory or a digest** — C and D are each other's nearest neighbours, and
  the test that separates them is whether anything was read at the moment of use. In D something
  was, and it was the wrong object; in C nothing was, and the value came from memory or a digest.
  Boundary pair: row 125 (D) read a `.pyc` file name actually present in the worktree and used it
  for the host's interpreter version; row 92 (C) typed a sha from the short form seen earlier in
  push output, with nothing read at all.
- **R, a derived key that does not identify** — R is the code's own version of the same family: a
  module composes a key, a pattern or an id and resolves it to the wrong object or to nothing, on
  every run, with no party reading anything at that moment. D is a party doing it once, by hand.
  Boundary pair: row 104 (D, the Agent resolved a `#N` out of core Rule text against the local row
  store) and row 135 (R, `references._MERGE` resolves a disposition's PR token to nothing at all,
  every run, because the pattern names the other preference's form).
- **E, an instrument narrower than the question** — in E the object is the right one and the
  instrument's coverage is short: a pattern that cannot match the form present, an exit code taken
  from a pipeline rather than the command. In D the instrument worked and pointed at the wrong
  object. The two sit side by side inside one d-work: row 100 (D, the sub-agent's search was sound
  over the wrong branch) and row 102 (E, one grep pattern over the right repository could not match
  `git -c credential.helper= push`).
- **H, the present enumeration pinned as an invariant** — H reads the right object and freezes what
  it currently holds, so a later change makes the claim false. D's claim was already false of the
  named object when it was made. Test: was the claim ever true of the object named?

## Incidents (9)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-29 | #192 | plan #185's attack A5 scored hash-based bytecode invalidation as confirmed-better-but-unavailable, and asked for a plan-`Y` on that option set | the consumer's loader API was read instead of a compiled artifact; producer and consumer conflated, and the claim was never executed |
| 2026-09-30 | #185 | the delegated drafter reported "Rule-15 phase 2 does not fire" for six files, having compared its own clone's head against `main` | phase 2 names one base, the plan file's own; a clone taken after the plan was written always looks unmoved against itself, so the right comparison was never made |
| 2026-10-05 | #221 | a sub-agent redirected to branch `build/half1` searched the default branch and returned "No pub/sub message bus exists in dsys-repo" | the negative was scoped to the 192-file tree the agent had rather than the 400-file tree it was sent to, with no check that the object matched the instruction |
| 2026-10-05 | #221 | the Agent reported "broadcast = commit and push the store repo" as the reference module's behaviour; `publish()` writes a file and does neither | a docstring sentence describing the caller's duty was read as a description of the code, without reading the function body for a git call |
| 2026-10-05 | #221 | plan #221 revisions 1 to 3 cite `#185` for Rule-16's presence store; the local #185 is the bytecode d-work and `sessions.py` arrived under #32 | a `#N` taken out of core-craft Rule text was resolved against the local row store without checking which numbering space it belonged to |
| 2026-10-05 | #222 | attack B1 was scored refuted on the peer's record carrying `cross_session_inbound: available`; `SendMessage` then found no reachable agent of that name | reachability was judged from the recipient's advertised willingness to receive, never from the sender's own address space, which is what resolves the name |
| 2026-10-08 | #241 | plan #241 and the reply asking for the core tag asserted that a craft's `requires:` floor resolves against release tags, so every craft install had been refused | the behaviour was inferred from `floor_problems()`, which does need the tag, instead of being read from `unmet()`, the gate `craft install` actually calls |
| 2026-10-08 | #253 | ADR #252 revision 6 recorded a session's status as unrepresentable in the presence store and carried edge case E30 as an impossibility | `FIELDS` and its invariant were read without the module header three lines above, which documents an optional `writer` field outside them |
| 2026-10-09 | #256 | plan #256 revision 1 surfaced Python 3.14 bytecode in the fork's worktree against a kernel pinned at 3.12+ as a finding, withdrawn in revision 4 | the host's interpreter was never read; `python3 -V` here is 3.14.4, which satisfies the floor, and 74 such files sit in the main tree too |

## Pattern
Eight of the nine are a claim about a *mechanism* — what a loader honours, what a gate calls, what a
function does, what an invariant forbids, which numbering space an id lives in, what a floor
resolves against, whether a name is reachable, whether a version conforms — and in each the object
that would have settled it was present and cheap to read. The ninth, row 81, is a claim about a
*comparison*, and is the only one where the right object is named in a corpus file (the plan's own
`base commit:` line) and the wrong one was reachable only because a sub-agent had its own clone.

Two things concentrate: five of the nine sit in d-work #221/#222's two days, and four of those are
claims that went into stored plan revisions before any plan-`Y` bound to them. And the two most
recent, rows 117 and 118, are the same sub-shape at one remove: a mechanism's reach inferred from
one literal or one neighbouring function rather than read from the thing that runs. Row 118's own
cause cell says so — "the same class as the row above".

Recurrence against the mitigations a consequence cell describes:
- Row 81's consequence names the conduct adopted — "The same check from the plan's base is now
  written into the PR check-in routine's own prompt". Rows 100, 101, 104, 105, 117, 118 and 125 all
  post-date it by ledger id and none is a base-commit fault, so that one holds on the log's own
  evidence for its own sub-shape and reaches no other.
- Row 104's consequence names the correction in plan #221's research appendix S2; rows 117, 118 and
  125 post-date it. The register had already declared `rule.text->row` unresolvable
  (`references.py:419`) before row 104 happened, so the declaration is older than the fault.
- Row 117's consequence names backlog #248 for the floor check's own tag dependence; row 125
  post-dates it and is a different object again.
No consequence cell of this mode names a mechanism that was built. All nine were caught by a party
re-reading: the Operator's deferral (row 72), the main Agent re-running from the plan's base (row
81), hand re-verification against the live branch (row 100), a plan revision before any `Y` (rows
101, 102-adjacent, 125), execution itself (row 105), skeptic review (rows 117, 118).

## Mitigations (phase 2)

**1. The declared numbering space.** `dyad/guards/agent/references.py:419`, the register row
`("rule.text->row", "rule", "text", rule_text_rows, "row", "world")` — a `#N` in Rule text is an
*unresolvable* kind, the authoring system's ledger id, printed as one `warn … inference` line
(Rule-20 property 2). Fires in Rule-11's runner as `agent/references` (`package.py check`) and on
the kernel-only path (`check --guards`). **Shipped.** Reaches row 104 exactly, and already did: the
register names the fault's whole mechanism and names it as beyond resolution. A declaration the
Agent can read is not a check on the Agent, and the row happened anyway, three plan revisions deep.

**2. The plan's base commit, existence only.** `dyad/guards/agent/references.py:251-262`
(`base_commit`) and the register row at `:414`, `("plan.base->commit", "plan", "base commit",
base_commit, "commit", commit_exists)` — the base commit of every row still `open`, `planned` or
`blocked` must resolve to a commit; a terminal row's is skipped silently (`:257-258`, Rule-20
property 2). Fires at the same two moments. **Shipped.** Reaches row 81 in the weakest possible
sense: it proves the base exists, never that the base a drafter *used* is the base the plan *names*.
Read today, `grep -rn "phase 2|base moved|moved past" dyad/scripts/*.py dyad/guards/*/*.py` returns
exactly one hit — the docstring at `references.py:252` — so row 81's cause sentence is exact:
"Nothing checks that the base a drafter used is the plan's."

**3. The install gate and its neighbour.** `dyad/guards/craft/crafts.py:109-118`, `unmet(repo,
craft_dir)` — for each `requires:` it compares `installed_version(repo, name)` (`:97-107`, which
reads `dyad/VERSION` or `crafts/<name>/VERSION`) by semver and reads no tag; and
`crafts.floor_problems`, `:300-338`, which resolves `dyad-operator-v<floor>` with `git rev-parse`
(`:323`) and emits `warning: … no tag {tag} here` at `:325` when it is absent. Fires: `unmet` at
`dyad craft install` (fails) and `craft check` (warns); `floor_problems` through `check_package` in
the runner. Both **shipped.** Reaches row 117 as the object that should have been read, and nothing
in the module distinguishes them to a reader: the two functions sit 190 lines apart, neither
docstring names the other, and only `unmet`'s one-line docstring ("Requirements `repo` does not
satisfy") says it is the gate.

**4. The presence store's optional field.** `dyad/guards/agent/sessions.py:18-22`, the module
header: "An optional `writer` field (outside FIELDS, checked only when present) is this process's
own id, written by `touch()`"; `FIELDS` at `:37`; `INVARIANTS` with `fields-are-five` at `:43`;
`check_record` at `:176-185`, which reports only *missing* FIELDS and forbids nothing beside them;
`touch()` writing `writer:` at `:115`. Fires: the invariant at every import of the module
(`dyadlib.enforce`, Rule-12 property 1's fail-loud check); `check_record` at `package.py check`.
**Shipped.** Reaches row 118 as the text that was skipped — three lines above the literal that was
read. No mechanism makes a reader of a literal read its module's docstring, and this is the mode's
clearest statement of its own unfenceability.

**5. Probe the object, never its name.** `dyad/bin/dyad-python:16-17`: "Each candidate is probed by
RUNNING it and asking `sys.version_info` — never by parsing a version string. The printed version is
diagnostic only; the decision is the probe's exit code." Fires at every hook and every `dyad`
invocation, resolving the interpreter. **Shipped.** Reaches row 125's *shape* — a version decided by
executing the object rather than reading a name — and not row 125, which is the Agent reading a file
name in a worktree listing while this file was resolving the interpreter correctly a few processes
away. The precedent is in the tree; the discipline is not enforced on the Agent.

**6. The recorded resolution of row 72's own question.** `dyad/scripts/dyadlib.py:62-63`: "being
correct is available at the price of a `compileall --invalidation-mode checked-hash` step in the
install path, refused on that price (plan #185 A5, revision 3)". Fires: nothing — this is a record,
not a check; `sys.dont_write_bytecode = True` at `:67` and `dyad/guards/craft/crafts.py:170` is the
course actually taken. **Shipped as a record.** Reaches row 72 only after the fact: the correct
object was eventually executed on the pinned kernel and the record now names it. No mechanism would
have refused the first scoring, which was an attack table's cell.

**7. Rule-3 Scope's subagent clause and `delegation: plan-and-execute`**
(`preferences-corpus/PREFERENCES.md`): subagents read, search and draft; the main Agent alone acts,
and reports every delegated d-work's state each turn. Fires: **inference, stated.** This is the only
mitigation that reached rows 81 and 100 — in both, the main Agent's own re-verification is what
caught the fault, per the rows' consequence cells. Mechanically nothing: no guard can see a
sub-agent's checkout, which branch it holds, or which base it compared against.

**8. The plan guard's stated limit.** `dyad/guards/agent/plans.py:5-6`: "Existence of these parts,
nothing more: what a plan says stays inference (plan #151, mutation 6)." Fires at `package.py check`
as `agent/plans`. **Shipped**, and it is the explicit statement that rows 72, 101, 104 and 117 —
four wrong claims that lived in stored plan files through one or more revisions — are unreachable by
that guard by design.

Rows 101 and 105 have **no mitigation but inference, stated.** Row 105's object, `SendMessage`'s name
resolution from the sender's address space, is a World surface the kernel never contains (Rule-14
property 2), so no guard can reach it at all.

## Remediation candidate, under attack
One fence: a **plan-base drift warning** on the kernel-only path. For every row whose state is
`open`, `planned` or `blocked`, read its plan file's `base commit:` line through the parser
`references.base_commit` already uses (`references.py:251-262`, pattern `_BASE` at `:91`) and its
`files touched:` list through `sessions.files_touched` (`sessions.py:63-90`), then print one
`warn [guards]` line per file that `main` has changed since that base, naming the row, the file and
the commit that moved it. Lives in `dyad/guards/agent/plans.py` as a second check beside its
existing shape check (Rule-15 owns the plan file; the guard is placed per Rule-11 property 1).
Fires at `dyad check --guards --pre-push` and in Rule-11's runner — the moment before anything
leaves the machine, which is also the moment Rule-15 phase 2 has to have been answered.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | It would have caught row 81. | refuted | Row 81's fault was a *sub-agent's* comparison inside its own clone, and the row's consequence cell records that the main Agent re-ran the check from `e4ea08a` before applying anything — at the very moment this fence would fire, and got the right answer. The fence does not prevent the wrong comparison; it makes the right one uniform and free at a named moment, which is the only thing a guard can do here. Rule-9 easy agreement: this is the attack pushed to a verdict before the candidate was accepted. |
| 2 | It rests on an under-reporting parser. `sessions.files_touched`'s own docstring (`sessions.py:63-72`) says a `{a,b}` brace group is dropped whole and that the `## files touched` heading form some plans use "is not read" — so a clean warn-free run would mean nothing for those plans. | confirmed | "A clean run means the plan is current" does not survive. What survives: the warn must print the parsed file list, so a short or empty list is visible as the parser's limit rather than as a clean bill, and a plan using the heading form must be reported as unparsed. Advisory in exactly the way Rule-16 Presence already is. |
| 3 | It must be a warn, not a fail. A FAIL would block every push on any open row whose plan is older than the last `main` move, which is most of them most of the time — and a refusal routinely bypassed teaches bypass. | survives, scoped | Scoped to a warn line at `check --guards`, with the judgment (re-plan or execute) left to the Agent, which is what Rule-15 Enforcement already says: "Inference otherwise". |
| 4 | Coverage: 1 of 9 rows. The other eight are a wrong object read in prose, a plan or an ADR — a neighbouring function, a docstring, a branch, a numbering space, one literal. No guard can know which object a sentence meant. | confirmed | Survives only as a partial. Rule-5's Enforcement states the shape of that limit for judgments no script can decide, and `plans.py:5-6` states it for plan content specifically. Eight of nine stay inference. |
| 5 | Duplication: `references.py` already resolves `plan.base->commit`, so a second reader of the same line is a second place to drift (Rule-13 property 1 argues the opposite way too). | survives, scoped | Scoped to importing `references.base_commit` and `sessions.files_touched` rather than re-deriving either — the guard contract (`crafts/sysarch/rules/guards.md`) makes an entity's parser the thing other guards import, and this reuses two of them and authors no third. |

Read together: as a remedy for mode D the candidate does not survive — attack 4 holds without
reconciliation, and attack 1 refutes even its claim on the one row it targets. What survives is a
cheap, uniform, advisory reading of a comparison Rule-15 requires and nothing performs, whose own
parser limits must be printed.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build** (exit 2), proposed only. What the row would say: a
plan-base drift warning in `dyad/guards/agent/plans.py`, firing at `dyad check --guards --pre-push`
and in the runner, importing `references.base_commit` and `sessions.files_touched`, printing one
warn line per touched file `main` has changed since the plan's base and printing the parsed file
list so the parser's own limits are visible. Which row it would have caught: 81 — and attack 1
scopes even that to "made the right comparison free", not "prevented the wrong one". The remaining
eight, rows 72, 100, 101, 104, 105, 117, 118 and 125, hold none of the three exits: each is a
sentence about a mechanism, and `dyad/guards/agent/plans.py:5-6` and Rule-5's Enforcement both say
in terms that no script decides whether a sentence names the right object. The mode stays **open**
in the index, and the Agent neither closes it nor asserts it addressed (play-book Conduct, Rule-2).

## Delta 2026-10-24 (#259 revision 5; 9 → 12 rows)
**Rows added:** 156 (#290: the row's write format read, not the readers that apply it at other commits),
184 (#202: a live row written where the test fixture was the object), 191 (#363: Rule-16's text read for
what `touch -r` does, the code not run). All three read a real object that did not govern the question.
**Mitigations re-read from the code.** `dyad/guards/agent/plans.py` still checks part existence only
(`:5-6`); nothing reads whether a sentence names the right object (Rule-5 Enforcement, inference). Row
184's probe is now refused by the fence it was probing (`cmd_dwork state … done` without a `Y done`
entry, `package.py:1110-1112`), which is a fence for its *consequence*, not for choosing the live row.
**Recurrence after a mitigation shipped:** n/a — no mitigation fires at the moment of reading.
**Exit after the delta:** open; #265 `backlog`. The drift-warning candidate (plan base vs touched files)
would have reached none of the three.
