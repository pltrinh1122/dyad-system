# Incident mode H — fence collision not surfaced

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #124, child of #116 (2026-09-22).*

## Definition

One mechanism: a Rule prescribes a route, a session-level fence outside the corpus forbids that
route, and the Agent does the corpus-legal half of the response Rule-1 prescribes and not the other
half. Rule-1 Boundaries class such a fence — a harness's restriction on which branches may be
pushed — as an Operator-side fence, per session, which neither replaces nor is replaced by a Rule,
and state the conduct at the collision: the Agent "does the corpus-legal part it can, states the
rest and asks; it never reads permission out of the Rule alone" (the #23 case). Mode H is the
second clause omitted. The work is done and lawfully shaped — the row records no guard, hook or CLI
fault — and the residue lands on the Operator as a task nobody named.

Boundaries against the neighbouring modes:

- **A (acting before the Operator's `Y`).** Both are a question owed and not asked. A proceeds
  anyway, so its residue is on a branch or on `main`; H stops, so its residue is an open PR on the
  Operator's desk. A is unauthorized action; H is unrequested inaction.
- **G (mechanism defect).** Nothing malfunctioned. The fence did what it is for, and the row names
  no mechanism fault. The nearby G rows are the three `--no-verify` pushes of #25/#27/#35: there a
  hook was genuinely dead (`pre-commit` exits 126) and Rule-1's stated bypass procedure *was*
  followed. Here nothing failed and the stated conduct was not followed.
- **F (form error in a clerical record).** F's fault is in what reached the corpus. The log records
  no form fault in H's five PRs — they are ledger-only; the fault is in what the reply did not say.

## Incidents (1)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-17 | #65 | Five ledger-only PRs of one session (`#27` closing #32, `#38` closing #15, `#40` and `#41` opening and planning #56, `#43` closing #56) were each opened and then left for the Operator to merge, with no counter-prompt naming the collision and no standing disposition sought | Rule-3 Ledger routes a ledger-only commit straight to `main` without a PR; only the session's branch fence made these PRs. The corpus-legal half was done and Rule-1's #23 clause — state the rest and ask — was not, so each PR parked. `merge-disposition: with-done` was defeated in purpose while its letter held: no duplicate merge counter-prompt was asked, and five merges sat on the Operator's desk anyway |

## Pattern

One row, five occurrences, one session, one day; nothing varies across them except what each PR
carried — three closing a d-work (`#27` closing #32, `#38` closing #15, `#43` closing #56), one
opening #56 and one recording its plan. The count agrees with plan #124 and with #116's index, and
no other row of the log carries this mechanism: the three `--no-verify` pushes of #25/#27/#35, the
nearest candidates, are dead-hook rows #116 places in mode G. This is the only one of the 34
incidents (35 rows; #47 is logged twice and counted once, per #116) that the Operator named rather
than the Agent detected — the log records the words, "you're not honoring my preference by waiting
on my merge" — and the only one whose whole cost was borne by the Operator. Rule-13 property 1 —
the second occurrence of an inference task yields, in the plan, a code path — reads on this
sequence only if the decision whether to ask is such a task; no plan of that session proposed one,
and what followed was a preference row, not code. Whether property 1's trigger reaches a conduct
decision is left open here. The row is dated 2026-09-17; #66, opened the same day and `done`
2026-09-18 (PR #49), added `ledger-pr-merge: agent` to `preferences-corpus/PREFERENCES.md`,
verified live in this audit's read of that file, which removes the parked state for a PR whose
entire diff sits under `agent-corpus/d-work/`. It does not remove it for a fenced PR carrying any path outside that
prefix — the preference names `agent-corpus/audits/INCIDENTS.md` as its own counter-example — so
the mode stays live for that narrower class, which includes the PR carrying this audit.

## Remediation candidate (falsified, not disposed)

**Candidate.** No further mechanism is proposed. The observed population of mode H is closed by
#66's `ledger-pr-merge: agent`, whose row is live in `preferences-corpus/PREFERENCES.md`; what
remains is the conduct Rule-1's #23 clause already prescribes, and this audit's contribution is to
record that the exposure narrowed rather than to add a second mechanism. Stated limit: the
preference row was read and is live, and plan #81 already names it as the route for its ledger
branch (that row is still `planned`); whether a merge has yet executed under it was not verified
here, because this audit runs no git commands.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | One incident is not a mode. Fold H into A, or drop it. | survives, scoped | Refuted as a merge into A: the mechanisms are opposites (A acts without the `Y`, H withholds the act and the question both), and A's nine are, per #116's own totals, all disclosed in the same or the next reply while H's one was surfaced externally, so folding it would corrupt what A's count measures. Survives as a caution: n=1 carries no trend, and nothing here should be read as one. |
| 2 | The candidate is false. #66 does not close mode H; it closes only the class whose whole diff is under `agent-corpus/d-work/`. | confirmed | The candidate narrows: closed for the ledger-only class, open for the fenced PR that carries one path outside that prefix. That residual class has no preference, no guard and no counter-prompt form of its own; it rests on Rule-1 #23 conduct alone. |
| 3 | Then widen `ledger-pr-merge` to any agent-zone PR the Agent opens, and the residual class closes too. | refuted | Plan #66's F2 scopes the preference to the path prefix, not the zone and not authorship, precisely so it cannot widen silently, and the preference's own text repeats it. A non-ledger PR carries output that Rule-3's completion counter-prompt verifies "on the output as it stands in the PR(s), before merge, so `main` never carries unverified output"; merging it with no counter-prompt would be the Agent disposing its own output, a Rule-2 proposer/disposer breach rather than a fence question. |
| 4 | A guard would have caught it: fail when a PR this Agent opened sits open and unmentioned. | refuted | Rule-14 property 3 requires every guard to run on the kernel alone, in which Git is a local repository and "a hosted git service is never kernel" (property 2). An open-PR census needs the hosting, a library adapter the package must not depend on to enforce a Rule. Detection of this mode is conversational, which is why Rule-1 states it as conduct, and why the remedy that worked removes the parked state instead of detecting it. |
| 5 | The Operator naming it is detection enough; no candidate is needed. | refuted | All five PRs were opened and parked in one session with nothing surfacing them; the log does not record which of them the naming followed, only that the Operator's words, not the Agent's, are what surfaced the mode. Relying on that channel makes the Operator the detector of the Agent's own omissions, which inverts the frame's "detect, don't dispose" — the Agent surfaces, the Operator disposes. |

## Disposition

Surfaced for the Operator; disposed by the Done-`Y` of its d-work — see ledger #124. Rule-2 states
that form for a falsification record or an audit; Rule-9 Form governs the attack table it carries,
and is cited for that only, this file living in `agent-corpus/audits/`. Remediation itself is a
further Operator prompt on this row, never taken here.
