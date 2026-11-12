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
  done-`Y` of a Rule-3 completion counter-prompt that names the PR. Either way the operator
  ratifies; only the number of questions changes (ledger #41).
- Pushing directly to `main` — except ledger-only commits, which Rule-3 defines as clerical.
- Declaring an agent-authored verdict final.

A falsification record or audit is disposed by the done-`Y` of its d-work (Rule-3); its
*Disposition* line records that by reference (`see ledger #N`) and is updated clerically in
any later agent-zone PR. It is not a separate ratification event (C2).

Any other rule that creates a ratification event declares it under its own
`## Ratification events` heading; this rule applies to those by reference and is
not edited when they are added (G5).

## Not ratification (agent may do freely)
- Commits on a branch; opening or updating a PR; running checks.
- Ledger-only commits to `main` (touching nothing outside `agent-corpus/d-work/`): they
  record a prompt received or a disposition already given, never a decision (Rule-3).
- Events-only commits to `main` (touching nothing outside `<runbooks>/events/`, the run-book
  store Rule-19 names, `DYAD_RUNBOOKS`): they record what a read-only run-book command observed, never
  a decision (Rule-3; #438).
- Writing proposals, falsification attacks, and proposed survivors.
- Reading `preferences-corpus/`. Changing a value there is a preferences-zone PR the
  operator disposes; the agent acts on the value on `main`.
- Writing the per-machine memory cache — it is a cache of ratified corpus; corpus wins on divergence.

## Binding of approval
- A "Y" binds only to the PR(s) or action(s) named in the question it answers. A done-`Y`
  archives only the rows the counter-prompt named under `retires` (Rule-3, What a `Y` binds; #574), and
  merges only the PRs the counter-prompt named, only on the guards' observed passes — the
  kernel-only path (`package.py check --evidence`, Rule-14 property 3) run by the main agent
  on the exact head being merged, its evidence block cited in the completion reply (Rule-3) by
  its `evidence-sha256` and its brief form — every failing or skipped line and every warning new
  since `main`, the standing ones folded per guard — the full block stored and shown on request (Rule-14 property 3), which the operator may re-run on that head and compare; corroboration
  runs after the merge, on `main`, where the merge ran (Rule-14 property 3, #168, #564), and never substitutes — and only if their heads are unchanged since it
  was asked; otherwise the agent stops and re-prompts. A CI failure that is an account or
  adapter failure (no job started) is not a red check but an absent one, reported as such.
  When the hosting is unreachable, a ratified merge is executed locally (`git merge --no-ff`
  into `main`, message citing the PR and the done-`Y`) and pushed on reconnect: clerical
  execution of the given `Y`, exactly as a hosted merge is; the row's `disposed` and the
  completion reply record it (#138).
- A new PR, including one created to recover from an error, needs a fresh Y.
- A precedent never settles a question's absence or an act: it decides only an outcome whose wrong match costs the
  operator at most a question, by the outcome's declared effect (`dmc:precedent-scope`) — `settles` (an agent-side
  call), `asks` (a question put to the operator) or `shapes` (what a question the operator answers anyway shows). An
  outcome that `skips` a question another outcome would ask, or `acts` with no question of its own, is never settled by
  a precedent, which abstains. In a record that declares an effect on any outcome, an undeclared outcome reads `skips`;
  a record that declares none keeps the record-wide consequence test until it does (#649).
- The agent may *execute* a merge the operator has ratified; execution is clerical, not disposal.
- A batch counter-prompt (Rule-3, Batch disposition) names several d-works, PRs, or both in one
  question; the binding is unchanged — a `Y` ratifies exactly the named set, each still checked
  against its own evidence and its own heads-unchanged condition.
- A plan counter-prompt whose plan states a **mandate scope** (Rule-3, Plan), or runs a play-book
  whose step prescribes a class of row — that step's class its rule and the play-book's own count, stated in the plan as
  a number, its ceiling (#574, #585) — binds wider than one
  action and no wider than that scope: the plan-`Y` authorizes the mutation *and* the class of row
  the scope names, so an **accreted row** inside it carries that `Y` as its own authorization and
  is never asked for separately, while the done-`Y` ratifies the accreted set exactly as the
  completion evidence listed it (Rule-3) — the delivered set, never the promised one. A row the
  stated rule does not cover, or one past the stated ceiling, was not named by the question and so
  is not bound by the `Y`: it returns to explicit mode and is asked. Never accretable, whatever a
  plan says: a destructive host action (Rule-8 keeps its own counter-prompt), a release (Rule-11:
  it publishes to the world) — except under the release gate, where the release d-work's own done-`Y`
  names the PR whose merge is the cut and the tags it publishes, and Rule-11 makes that `Y`, with its
  fence, the release's ratification and the hosting approval its authentication (#545) — a Rule-3 Intake (its words are another operator's, Rule-7 property
  4), a change to a preference value (*Not ratification*, above: the operator disposes that as its
  own PR), and any mutation the plan did not describe, which Rule-3 already calls a new plan. The
  preference `accretion` (`preferences-corpus/PREFERENCES.md`) selects between the two: under
  `explicit` a plan-`Y` authorizes the mutation alone and every accreted row is asked for.
- A third authority preference is a mandate for one class of row: under `hardening-mandate: on`
  (`preferences-corpus/PREFERENCES.md`) a `backlog` row of hardening work (`dmc:hardening-work`) is opened when it is due
  (`dmc:hardening-due`; Rule-3 Scope), its `disposed` entry `<date> Y plan (mandate preference hardening-mandate)` and its
  plan-`Y` the operator's grant of the preference, so it binds no wider than that class and the ceiling
  `hardening-ceiling`. It carries none of the never-accretable acts above, which the record's W3 excludes, and the row's
  done-`Y` is always asked, so every merge it ratifies stays the operator's answer (#692).

## Enforcement
Three mechanical checks read the record; the binding itself stays inference.
- **The main fence**, `dyad/guards/agent/rows.py` (owned by Rule-3), fails any direct commit to `main` that is
  not ledger-only or events-only, so the sole exceptions to "pushing directly to `main`" cannot widen silently.
- **The merge guard**, `dyad/guards/agent/merges.py` (this Rule's own; entity `merge`, a transaction guard on
  the kernel-only path, Rule-14 property 3), warns — never fails — on a merge commit on `main`'s first-parent line
  whose tree is not the merge of its two parents, or whose second parent no operative `Y done` names: so a merge
  that executes no recorded done-`Y`, or carries content neither parent holds, is visible (d-work #541).
- **The merge verb**, `dyad merge <pr> --head <sha>` (`dyad/scripts/merge.py`), is execution, not a guard: it
  refuses unless `origin/main` holds the operative `Y done` naming that PR at that head, the PR's live head is that
  head, and the head is not yet on `main` — Binding's "only if their heads are unchanged" applied at the moment of
  execution (d-work #532).
- **The automaton**, `dyad automaton scan|run` (`dyad/scripts/automaton.py`), is execution too, never a disposer:
  while the operator's repository variable `DYAD_AUTOMATON` is `on` it runs from ledger lines on `main` alone,
  merges each PR an operative `Y done` names through the merge verb above, so under the same refusals, and closes a
  row once its named heads are on `main`; anything else it posts to the home's inbox and leaves (Rule-3 Completion
  counter-prompt; d-work #556). Its commits carry the identity of whoever runs it; its inbox messages come from the unit
  `automaton`.
Everything else is inference: whether a `Y` was given to the question it is recorded against, because all commits
carry the operator's git identity and the platform cannot distinguish proposer from disposer. Any mechanical check lives in the package (`dyad/guards/`, agent zone; Rule-11 property 1) and its
workflow wrapper in the infra zone — a dependency on Rule-1, not an overlap (A1).

## Provenance
Craft invariant `bond:no-self-ratify` (dyad-bond). Falsified 2026-09-12; see
`../falsification/rules/rule-2-no-self-ratify.md`. Binding gains one sentence on the batch
counter-prompt (Rule-3) 2026-09-15 (d-work #17); see `../falsification/rules/rules-2-3-batch-disposition.md`.
Binding gains the mandate clause 2026-10-14 (d-work #290): a batch `Y` had been found to compress
73 questions and remove no authorizations at all, so the operator asked for a disposition that
supersedes the individual ones — which Binding's first sentence forbade in so many words, since a
row accreted after the question was asked is named by no question; the clause states what a plan-`Y`
may bind to instead, and the list of what it may never bind to; see
`../falsification/rules/rule-2-no-self-ratify.md`, amendment #290. Not ratification gains the
events-only commit 2026-10-25 (d-work #438): a standing health check's events, each a read-only
command's observation, needed a row, a PR and the full suite to reach `main`, and the operator asked
why monitoring should have a row at all; an observation passes the test the ledger-only bullet
already states — it records, never decides — and only events of read-only commands do; see
`../falsification/rules/rule-2-no-self-ratify.md`, amendment #438. Binding cites the evidence block by its
sha256 and its brief form 2026-10-26 (d-work #476, child C3 of #473): a pasted block was read in full at every
merge (267 lines on that day; the brief form 140, its standing warnings kept), while its sha256 already covered every
line and the operator could re-run it; see
`../falsification/rules/rule-2-no-self-ratify.md`, amendment #476. Enforcement names its three mechanical checks 2026-10-31 (d-work #543):
it said "one mechanical fence" after #541 had added a merge guard that names this Rule its owner and #532 a merge
verb that refuses an unbound merge, so a guard claimed an owner whose text denied having one; see the same record,
amendment #543. Binding's never-accretable list lets a release go under the release gate 2026-11-01 (d-work #545): the
chat release question after a done-`Y` that had verified the very bytes of the cut added no information, while the
hosting approval, the one input no agent can forge, stays; see the same record, amendment #545. Enforcement names the automaton as execution 2026-11-02 (d-work #556): it executes the merges a
recorded done-`Y` names, through the merge verb, and decides nothing; see the same record, amendment #556. Binding's
after-merge check is corroboration where the merge ran 2026-11-03 (d-work #564): the automaton's merges started no hosted CI; see
`../falsification/rules/rule-14-system-infrastructure.md`, amendment #564. Operator and agent are lowercase in prose and done-`Y` replaces Done-`Y`, 2026-11-02
(d-work #553): the dyad-native terms; see `../falsification/rules/rule-6-vocabulary.md`, amendment #553 (part D). Binding's mandate clause gains the play-book that prescribes a class of row
2026-11-04 (d-work #574): the plan-`Y` that ran the incident-hardening play-book had already answered for the fence rows
that play-book prescribes, and they were asked again; the never-accretable list is unchanged; see the same record,
amendment #574. Binding's first bullet names the rows a done-`Y` retires 2026-11-04 (d-work #585, absorbing #574
revision 3): a delivered row's report retires rows the operator had been asked about again in the retirement form; see
`../falsification/rules/rule-3-d-work.md`, amendment #585. Binding gains the precedent's scope 2026-11-09 (d-work #649):
admission refused every case of a record when any of its consequences held a ratifying word, so a release class that
only sets the number a release question shows, and a new plan that only asks one, were refused with the outcomes that
skip a question; the line is drawn by what a wrong match costs, declared per outcome; see the same record, amendment
#649. Binding names the third authority preference, `hardening-mandate`, 2026-11-12 (d-work #692); see
`../falsification/rules/rule-3-d-work.md`, amendment #692.

Set: System Requirements.
