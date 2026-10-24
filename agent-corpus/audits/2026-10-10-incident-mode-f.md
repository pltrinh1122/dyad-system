# Incident mode F — the `d-work #N` citation form used for a cross-reference

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 3 of 140 rows.*

## Definition
One phrase carries two meanings that no mechanism separates at the moment it is typed: `d-work #N`
is both the plan gate's claim-of-work token (`dyad/guards/agent/prs.py:25`, `CITE`) and the natural
English way to mention another row, so an author who means "see also" writes the token that means
"this commit is work on". Nothing composes a commit message, so the phrase is always hand-typed into
prose that a scanner later reads as structure.

**What would have to change.** The claim would have to be carried by a field a mechanism supplies
rather than by a phrase an author types into free prose, so that mentioning a row and claiming one
could not be spelled the same way.

Boundaries against the neighbours it is most easily confused with:
- **S, a form typed from memory rather than seeded from its governing definition** — S is the
  general case of a shape typed instead of generated. Separating test: does the fault turn on a
  *scanner's* reading of a phrase that is itself correctly spelled? F yes; in all three F rows the
  number is right and the form is right, and only the author's intent differs.
- **R, a derived key that does not identify** — R's key resolves to nothing or to the wrong record
  because the derivation is wrong. Separating test: is the id correct for what the author meant to
  point at? F yes (141, 164, 260 are each the intended referent); R no.
- **Q, an obligation no mechanism reads** — Q's faults reach `main` because nothing looks. Separating
  test: did a mechanism fire? All three F rows end in a FAIL from `agent/prs`; Q's rows, by
  definition, in silence.
- **N, a target named by an ambiguous pattern** — nearest in shape, a pattern matching more than
  intended. Separating test: whose namespace? N's ambiguity is resolved by an external tool (git
  refs, the process table); F's by the dyad's own guard over prose. No boundary row between them.

## Incidents (3)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #15 | commit `e74f3a2` wrote the citation form naming 141 in prose as historical precedent; `agent/prs` FAILed with `#141 not in ledger` | the phrase was meant as a mention of a row this ledger does not hold; the gate read it as a claim of work |
| 2026-10-01 | #199 | a `d-work #164` phrase copied out of a code skip line into commit prose; the gate refused the push, #164 having no `Y plan` | same phrase, same reading; the skip line in code keeps the phrase, which no gate reads |
| 2026-10-09 | #259 | the commit message credited the drafting fork as `d-work #260`, a row whose plan-`Y` was outstanding; the gate FAILed the push | a cross-reference written in the citation form, third occurrence of one mechanism |

## Pattern
All three are one fault with one cost: a cross-reference spelled as a citation, refused at the
pre-push gate, one amended commit message. Nothing reached `origin` in any of the three; row 36's
amendment needed the Operator's explicit `Y` to force-push because the commit was already on a
branch, and rows 86 and 137 were amended before any push at all, so the cost fell over time.

Recurrence evidence. The only mitigation any consequence cell describes is prose, and the prose
predates every row: Rule-3's Ledger clause already read "the phrase is a claim of work on that
d-work, not a mention, in a commit message exactly as in a PR body — cross-reference other rows as
plain `#<id>` (#23)" (`dyad/rules/RULE-3-d-work.md:101-103`) before 2026-09-16. Row 36's own cause
cell says so in as many words. Row 36 then added a second prose mitigation ("a historical reference
is never `d-work #<id>`, not even in prose explaining precedent"); rows 86 and 137 both post-date
it. Row 137's consequence states the measurement outright: the fence "fires reliably every time,
and nothing stops the phrase being written."

## Mitigations (phase 2)
1. **The plan gate's citation scan** — `dyad/guards/agent/prs.py:25` (`CITE = re.compile(r"d-work
   #(\d+)")`), `prs.py:28` (`cited`), `prs.py:31-48` (`check`, which FAILs an id not in the ledger,
   an id not `open`/`planned`/`blocked`, or an id without `Y plan`). Moment: the branch's commit
   messages are read as the PR body by `check_transaction` (`prs.py:59-67`, the `git log
   --format=%B` at `prs.py:66`), run by `dyad check --guards --pre-push` from
   `dyad/hooks/pre-push:4`. **Shipped.** Reach, row by row: row 36 caught (`#141 not in ledger`),
   row 86 caught (`#164` without `Y plan`), row 137 caught (`#260 has no 'Y plan' disposition`) —
   3 of 3. It is a detector at the push, not a preventer at the keystroke, and the mode recurred
   twice after it shipped (rows 86, 137).
   Two holes in its reach, neither of them in this mode's own evidence: `check_transaction` returns
   `[]` unconditionally on `main` (`prs.py:62-63`) and skips any range touching only
   `<instance>/d-work/` (`prs.py:54-57`, `prs.py:64-65`, the `ledger_only` exemption of #191), so the
   same phrase in a ledger-only commit message is unread. All three rows were zone commits, so this
   is stated as a gap, not as an uncaught incident.
2. **Rule-3's Ledger clause** — `dyad/rules/RULE-3-d-work.md:101-103`. Moment: inference, stated,
   at the time the Agent writes the message. **Shipped** as Rule text. Reach: none mechanically; it
   predates all three rows and prevented none of them.
3. **At write time there is no mechanism at all.** Nothing in the tree composes a non-ledger commit
   message: `dyad dwork new|state` (`dyad/scripts/package.py:935-975`) writes the ledger commits'
   content and no commit message for a zone commit, and `dyad/hooks/` holds only `pre-commit` and
   `pre-push` (`dyad/hooks/pre-commit:4`, `dyad/hooks/pre-push:4`). There is no `commit-msg` hook
   and no message template.

## Remediation candidate, under attack
A `commit-msg` hook, `dyad/hooks/commit-msg`, running `prs.check` over the message being written
against the rows at `HEAD`. It fires at commit time, before `pre-push` — the same check, one moment
earlier, so the refusal costs an unmade commit rather than an amended pushed one.

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | A third blocking local hook is not in Rule-1's Enforcement list, which names `pre-commit` and `pre-push` as "the only *blocking* enforcement" until d-work #24 (`dyad/rules/RULE-1-containment.md:47-52`); adding one amends a Rule and changes the install's hook set. | survives (scoped) | Admissible: the hook set is already data in one distribution code path (Rule-11 property 5) and an install sets `core.hooksPath dyad/hooks`, so the file installs itself. Scoped to a Rule-1 amendment named in the plan, never discovered at execution. |
| 2 | It prevents nothing. The Agent still types the phrase; it now meets a refusal at commit instead of push, and the mode's rows were all caught already. | confirmed | Prevention does not survive. What survives is cost: row 36 needed the Operator's explicit `Y` to force-push an amendment to a pushed branch; at commit time the same fault costs an unmade commit. |
| 3 | The check cannot be "only one id may appear", because a commit legitimately claims two d-works — this ledger carries rows cited as `#133, #191` and `#25, #27, #35`. A hook refusing a second id breaks real work. | survives (scoped) | Only as "every cited id is a ledger row that is `open`/`planned`/`blocked` and carries `Y plan`" — which is exactly `prs.check` (`prs.py:31-48`), so the candidate adds no new semantics. |
| 4 | Attack 3 reduces the candidate to "run the existing gate earlier", which means its whole content is a moment. Then the honest question is whether the moment is worth a Rule-1 amendment for a mode whose fence already catches 3 of 3. | survives (scoped) | Survives only as a cost reduction, offered as such. It does not survive as a closure argument: the mode is already fenced, and this moves the fence, it does not add one. |
| 5 | Easy agreement (Rule-9 Conditions): the candidate read as obviously right on first reading. Attack it at the input — `prs.check` needs the rows, and at commit time the rows are read at `HEAD`, not at the merge base, so a commit that opens its own row in the same range would be judged against rows that do not yet hold it. | survives (scoped) | Only with the ledger-only skip (`prs.py:54-57`) applied at commit time too, by the same `dyadlib.ledger_only` the push path uses, so a clerical commit is exempt at both moments or neither. |

## Proposed exit (phase 4)
**Fenced at a named moment** — `dyad/guards/agent/prs.py` `check_transaction` (`prs.py:59-67`),
run by `dyad check --guards --pre-push` from `dyad/hooks/pre-push:4` on every push whose range is
not ledger-only. A fault of this mode presented at that moment would meet it: it met it three times
out of three, with the exact message each row records.

Two things the exit does not claim, stated so the Operator can judge it rather than accept it.
First, the fence catches and does not prevent; the recurrence (rows 86 and 137 after row 36) is the
measurement of that, and the candidate above is offered as a cost reduction, not as a condition of
this exit. Second, the fence does not reach a ledger-only range or a commit made on `main`
(`prs.py:62-65`); no row of this mode is in either class, so the gap is a finding about the fence's
reach and not an uncaught incident. Proposed only — the mode is not closed here.

## Delta 2026-10-24 (#259 revision 5; 3 → 4 rows)
**Row added:** 166 (#297: `d-work #1` in a commit message's prose, caught by `dyad check --pr` before
the push).
**Fence re-verified (phase 4):** `prs.check_transaction` (`dyad/guards/agent/prs.py:59-67`) on any
branch but `main`, over a non-ledger-only range, at `dyad check --guards --pre-push` and `check --pr`.
Row 166 met it exactly as rows 36, 86 and 137 did — four of four. A fault of this shape presented today
meets the same fence; read from the code on 2026-10-24, unchanged since 2026-10-10.
**Exit after the delta:** exit 1 holds (fenced at a named moment; catches, does not prevent — the
recurrence is the measurement, now four).
