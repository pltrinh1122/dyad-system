# Rule-2: no-self-ratify

**Intent:** Keep the proposer and the disposer of every ratification event distinct: the agent proposes, the operator disposes.
**Target:** a ratification event

## Boundaries (out of scope)
- Repo shape and zones — Rule-1.
- When a d-work opens, is planned, or completes — Rule-3; Rule-2 applies to the events Rule-3 declares by reference.
- Work that is not a ratification event (see *Not ratification*).

## Conditions (triggers)
- A PR is to be merged into `main`.
- A commit is to be pushed directly to `main`.
- An agent-authored verdict is to be declared final.
- Another Rule declares a ratification event under its own `## Ratification events` heading.

Disposer ≠ proposer (vocabulary, Rule-6). The agent proposes; the operator disposes. Never the same party.

## Ratification events (operator only)
Base events, owned by this rule:
- Merging any PR into `main`. Asked as its own counter-prompt, or — when the preference
  `merge-disposition` is `with-done` (`preferences-corpus/PREFERENCES.md`) — ratified by the
  Done-`Y` of a Rule-3 completion counter-prompt that names the PR. Either way the operator
  ratifies; only the number of questions changes (ledger #41).
- Pushing directly to `main` — except ledger-only commits, which Rule-3 defines as clerical.
- Declaring an agent-authored verdict final.

A falsification record or audit is disposed by the Done-`Y` of its d-work (Rule-3); its
*Disposition* line records that by reference (`see ledger #N`) and is updated clerically in
any later agent-zone PR. It is not a separate ratification event (C2).

Any other rule that creates a ratification event declares it under its own
`## Ratification events` heading; this rule applies to those by reference and is
not edited when they are added (G5).

## Not ratification (agent may do freely)
- Commits on a branch; opening or updating a PR; running checks.
- Ledger-only commits to `main` (touching nothing outside `agent-corpus/d-work/`): they
  record a prompt received or a disposition already given, never a decision (Rule-3).
- Writing proposals, falsification attacks, and proposed survivors.
- Reading `preferences-corpus/`. Changing a value there is a preferences-zone PR the
  operator disposes; the agent acts on the value on `main`.
- Writing the per-machine memory cache — it is a cache of ratified corpus; corpus wins on divergence.

## Binding of approval
- A "Y" binds only to the PR(s) or action(s) named in the question it answers. A Done-`Y`
  merges only the PRs the counter-prompt named, only on the guards' observed passes — the
  kernel-only path (`package.py check --evidence`, Rule-14 property 3) run by the main Agent
  on the exact head being merged, its evidence block pasted verbatim in the completion reply
  (Rule-3), which the Operator may re-run on that head and compare; the hosting's CI
  corroborates after the merge, on `main` (Rule-14 property 3, #168), and never substitutes — and only if their heads are unchanged since it
  was asked; otherwise the agent stops and re-prompts. A CI failure that is an account or
  adapter failure (no job started) is not a red check but an absent one, reported as such.
  When the hosting is unreachable, a ratified merge is executed locally (`git merge --no-ff`
  into `main`, message citing the PR and the Done-`Y`) and pushed on reconnect: clerical
  execution of the given `Y`, exactly as a hosted merge is; the row's `disposed` and the
  completion reply record it (#138).
- A new PR, including one created to recover from an error, needs a fresh Y.
- The agent may *execute* a merge the operator has ratified; execution is clerical, not disposal.

## Enforcement
Inference-only, with one mechanical fence: `dyad/guards/agent/rows.py` (the main fence, owned by
Rule-3) fails any direct commit to `main` that is not ledger-only, so the sole exception
to "pushing directly to `main`" cannot widen silently. Everything else is inference: all
commits carry the operator's git identity and the platform cannot distinguish proposer
from disposer. Any mechanical check lives in the package (`dyad/guards/`, agent zone; Rule-11 property 1) and its
workflow wrapper in the infra zone — a dependency on Rule-1, not an overlap (A1).

## Provenance
Craft invariant `bond:no-self-ratify` (dyad-bond). Falsified 2026-09-12; see
`../falsification/rules/rule-2-no-self-ratify.md`.

Set: System Requirements.
