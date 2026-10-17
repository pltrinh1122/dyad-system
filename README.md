# dyad-system

The authoring repository of one Dyad Practice system: the core craft `dyad-operator` (`dyad/`)
and the three Tended crafts it ships — `crafts/sysadmin/`, `crafts/sysarch/`, `crafts/syseng/`
— developed here under their own Rules. The d-work ledger, provenance, incident log and
falsification records live in `agent-corpus/`; the Operator's preferences in
`preferences-corpus/`. The root `CLAUDE.md` holds one import line; the operating frame is
`dyad/CLAUDE.md`.

**Layout.** `dyad/` — the frame, the Agent Rules (`rules/`: 1–16 and 18–20; 17 and 21 are retired
into the sysarch craft), the vocabulary, guards, templates, run-books and the falsification
record behind every Rule; `dyad/README.md` maps it. `crafts/<craft>/` — one Tended craft each:
rules, vocabulary, guards with tests, templates, records, installable on its own. `BUNDLE.md` —
the bundle manifest, every craft in the tree at its live `VERSION`. `agent-corpus/` — instance
state, never inside a craft.

**Releases.** Every craft carries a `VERSION`; a release is a git tag —
`dyad-operator-vX.Y.Z` for the core craft, `<craft>-vX.Y.Z` for a Tended craft, and the
unprefixed `vX.Y.Z` for the bundle (`v` + the version `BUNDLE.md` names) — each cut only on the
Operator's `Y` (Rule-11). Pin the whole distribution from one bundle Release, or only what you
need from a craft's own tag. Tags do not move: a mistake is superseded by the next version,
never retagged.

**Install.** From a checkout, `dyad/bin/dyad install <path-to-repo>` writes `dyad/`, one import
line in the host's `CLAUDE.md` and the documented, `dyad-`prefixed host-side hooks, never
overwriting a host file; a second install changes nothing. `dyad/bin/dyad craft install
<archive-or-tree>` writes `crafts/<craft>/` and its `crafts/REGISTRY.md` row only.
`dyad/bin/dyad bundle build [dir]` builds every component `BUNDLE.md` names through the one
distribution code path. Everything runs on the kernel alone — Python 3.12 and git
(`dyad/infrastructure/INFRASTRUCTURE.md`).

**Check.** `git config core.hooksPath dyad/hooks`, then `dyad/bin/dyad check` (the invariant
pass, the tests, every guard of both roots); `check --guards` runs before every push, `check --pr
<base> <head>` before a PR, and `check --evidence` prints the merge-evidence block (Rule-14).

**Read** `dyad/CLAUDE.md` first, then `dyad/rules/` alongside `dyad/falsification/rules/`,
`dyad/vocabulary/VOCABULARY.md`, `dyad/README.md`, and each craft's own `rules/`.

Practice: [the-dyad-practice](https://github.com/The-Dyad-Practice-Commons/the-dyad-practice)
and [dyad-bond](https://github.com/pltrinh1122/dyad-bond); not registered with the commons.

## The Dyad System — what, why, how

A map of the system in three layers, each a run of short claims with a footnote to the artifact that
holds it. The three words are used in the sense this instance aligned on in d-work #330: **design**
answers *why* (the choices made and the alternatives refused), **architecture** answers *what* (the
entities, stores, states and boundaries), **framework** answers *how* (the procedure a party follows to
produce and move instances of the architecture). A statement that names an alternative is design, one a
projector could draw is architecture, one with a verb a party performs is framework.[^330][^row330]

**Pin.** Written against `main` at commit `7aee667` (2026-10-17), whose tree holds bundle 0.14.0,
`dyad-operator` 0.11.0, `sysarch` 0.3.0, `syseng` 0.4.0, `sysadmin` 0.3.0, `countersign` 0.3.0 and
`disclosure` 0.1.0.[^versions] The newest release tags on `main` — `v0.12.1`, `dyad-operator-v0.10.1`,
`sysarch-v0.3.0`, `syseng-v0.4.0`, `sysadmin-v0.2.1` — all name one commit, `74180d5` (2026-10-07), so
the live tree is ahead of every release and a tag alone cannot pin what this section describes. Each
footnote therefore gives the cited path and its **blob** at the pin (`git rev-parse 7aee667:<path>`;
`git show <blob>` returns the exact text cited whatever `main` does later), followed by `(v0.12.1)` when
that blob is the one the release tags hold and `(unreleased at the pin)` when it is not. A `#N` is a
ledger row, resolved at `agent-corpus/d-work/rows/N.md`; a PR number resolves on the hosting, a
reference into The World that no guard checks. Re-pinning is a later d-work on this file; until then the
commit above says what the reader holds.

### Architecture (WHAT)

- **Two parties.** The Operator is the human party and the sole disposer; the Agent is the model party
  and the sole proposer.[^vocab] The Agent runs as a CLI inferencing agent (Claude Code at the pin),
  one of four kernel rows: a CLI agent, Python 3.12 pinned, Git as a local repository, and pydantic
  pinned.[^infra][^rule14] A hosted git service is never kernel; everything else the system invokes is
  a library row or The World, declared in one manifest.[^rule14]
- **One frame.** The host's root `CLAUDE.md` holds a single import line; the operating frame is
  `dyad/CLAUDE.md`, which names the practice, the core craft, the Tended crafts, the five retained
  principles, the Rules it imports, the vocabulary, the preferences and an injection
  sentinel.[^rootframe][^frame]
- **Five zones.** Every path belongs to exactly one of `agent`, `workstation`, `preferences`, `craft`,
  `infra`; the table is defined only in the containment guard's `ZONES`, and a commit or a PR touches
  exactly one zone.[^containment][^rule1] The host row is instance data read from the preferences
  `host-path` and `host-zone`.[^rule1][^prefs]
- **Crafts and instance.** Every tracked file is craft or instance. The core craft `dyad-operator`
  (`dyad/`) is the one craft every system has; a Tended craft lives at `crafts/<craft>/` with its own
  `VERSION`, rules, vocabulary, guards and tests, installable on its own; `sysadmin` is bundled with the
  core by its own declaration.[^rule11][^bundlemd] The tree holds five Tended crafts — `sysadmin`,
  `sysarch`, `syseng`, and `countersign` and `disclosure`, which the Operator holds back from the bundle
  until ready (#232).[^bundlemd][^versions] The instance — ledger, provenance, audits, falsification
  records, preference values, host corpus — is never inside a craft.[^rule11][^dyadreadme]
- **Two sets of rules, three homes.** *System Requirements* are the core craft's Agent Rules
  (`dyad/rules/`: 1–16 and 18–20; 17 and 21 retired into the sysarch craft), each with the countable
  block Intent, Target, Boundaries, Conditions.[^rule4][^rule5] *System Architecture* is the sysarch
  craft's six Tended rules — distribution, guards, manifest, projection, references, stores — which say
  how infrastructure and guards are built and run and never redefine what a guard checks.[^rule5][^sysarch]
  The implementation discipline — naming, invariants, verifiable code, imports, determinism, idempotence
  — is the syseng craft's rules, a third home.[^dyadreadme][^syseng] Every term the Agent Rules use is
  defined once, in the vocabulary.[^rule6][^vocab]
- **Five d-work records.** One d-work is made of a row, a plan, a provenance record, a presence file
  and a trace, each one file per id under `agent-corpus/d-work/`, each with one guard that is its
  parser.[^playbook][^rule16] The row carries `id`, `title`, `opened`, `state`, `disposed`, `refs` and an
  optional `mode`; a provenance record holds the Operator's prompts and dispositions verbatim in
  numbered fenced entries; a presence file names a seat's root, rows, files, host and holder.[^rule16][^rule7]
- **One machine.** Six states — `open`, `planned`, `blocked`, `backlog`, `done`, `archived` — two birth
  states, a transition table that never regresses, and one input per edge of three kinds: an Operator
  prompt, an Operator disposition, or a clerical act a disposition already covers. The data is
  `dyadlib.STATES`, `NEW_STATES`, `TRANSITIONS`, `INPUT_KINDS` and `INPUTS`; the play-book's tables are
  pinned to it by test.[^dyadlib][^playbook][^rule16]
- **Guards.** One module per entity kind, under `dyad/guards/<corpus>/` for the core and
  `crafts/<craft>/guards/` for a Tended craft, its data beside it, discovered by the runner and never
  hand-listed; at the pin `dyad check --list` prints 24 guards, 16 core and 8 craft, of which five are
  transaction guards: `infra/containment`, `agent/rows`, `agent/prs`, `agent/provenance`,
  `sysadmin/events`.[^packagepy][^guardsmd][^rule11] A reference register in `references.py` lists every
  reference kind with exactly one resolver that decides existence and nothing more.[^rule20]
- **Checks in the code.** Every model module carries `INVARIANTS`, pure predicates enforced at import
  so a false one fails every import, and `TREE_INVARIANTS`, which read the tree and run only in the
  runner's pass; `assert` is banned outside tests.[^rule12][^invariants]
- **Releases.** Every craft has a `VERSION`; a release is a tag — `dyad-operator-vX.Y.Z`,
  `<craft>-vX.Y.Z`, or the unprefixed `vX.Y.Z` for the bundle `BUNDLE.md` names — built by one
  distribution code path and checked for drift against its own tag.[^rule11][^bundlemd][^distribute]
- **Seats.** A seat is a role name bound to one presence file, held by one harness session at a time
  and by many over time; `cos` and `cabinet` are roles a seat plays, and a cabinet reports to the cos by
  state — rows, plans, dispositions, presence — never by message.[^seat][^vocab][^msgarch]
- **Countersign.** The `countersign` craft states one core schema — eight entities (party, act,
  proposal, countersignature, mandate, release, event, escalation) and one attribute — that every
  Countersign system maps to by projection, keeping its own entities as a profile; it binds no
  system's agent by itself.[^schema][^interaction] The d-work framework is a profile of it, derived from
  the d-work stores by one projector under derivation rules D1–D8; the audit of #330 tables the mapping
  and its divergences, and #334 (`planned` at the pin) is falsifying the claims "the core = countersign" and
  "d-work is an instance of countersign".[^330][^projector][^row334]

### Design (WHY)

- **No self-ratification.** The proposer and the disposer of every ratification event are distinct:
  the Agent proposes, the Operator disposes — a merge into `main`, a direct push, a final verdict.
  Enforcement is inference with one mechanical fence, because every commit carries the Operator's git
  identity and the platform cannot tell the two apart.[^rule2][^rec2] The invariant comes from the
  dyad-bond craft, `bond:no-self-ratify`.[^rule2]
- **Ledger-only commits are clerical.** A commit touching nothing outside `agent-corpus/d-work/`
  records a prompt received or a disposition already given, never a decision, so it goes to `main`
  without a PR; the row guard fails any other direct commit, so the one exception cannot widen
  silently.[^rule3][^rule2][^rows]
- **Falsify before encoding.** Every claim a Rule, plan, preference or verdict would encode is attacked
  first; only survivors are implemented, and "no attack found" is permitted only by naming what was
  tried. Rule-9 and Rule-10 were frame principles promoted to Rules on an Operator decision after an
  audit found the gap.[^rule9][^rec910] Three principles stay conduct, not Rules, by Operator choice:
  the standing license to challenge unasked, detect-don't-dispose, and the craft invariants two-models,
  no-self-ratify, anti-cave.[^frame]
- **One path, its strongest counter, one question.** Every proposal is framed as a recommended path, the
  best case against it stated fairly, a reconciliation, and one `Y/N` as the last line; a fabricated
  counter is a breach.[^rule10]
- **The kernel is the gate; CI only corroborates.** Every guard runs on the kernel alone before every
  push; hosted CI runs on `main` after a merge and on dispatch, never on a branch push or a PR, because
  the package must not depend on a library adapter to enforce a Rule. The merge evidence is the
  kernel-only evidence block the Agent runs on the exact head, which the Operator may re-run and
  compare.[^rule14][^rec14][^workflows]
- **The Operator's words, verbatim; the transcript, never.** A provenance record holds every prompt
  and disposition exactly as given, written in the clerical commit of the event, and is checked one-to-one
  against the row's dispositions. The raw harness transcript is never committed: it carries whatever the
  session carried, credentials included, and its location is a property of one kernel and one
  host.[^rule7][^rec7]
- **`done` follows the merge.** Recording the Done-`Y` used to set the row `done`; `done` is terminal and
  the plan gate refuses every commit citing a terminal row, so a ratified merge that still needed one push
  had no admissible sequence — twelve incident rows in fifteen days were that one mechanism. The record of
  the `Y` is now the `disposed` entry and its provenance entry; the state moves in a second commit once
  the head the `Y` named is on `main` (#202).[^rule3][^plan202][^incidents]
- **A craft is one zone and one tree.** Every craft changes by craft PRs and never mixes with instance
  PRs, which is what makes it exportable to another dyad system; an install writes only under the
  craft's root plus a documented, prefixed set of hooks and never overwrites a host file, which is why
  the host's `CLAUDE.md` holds one import line.[^rule1][^rule11][^rec11] Tags never move: a drift guard
  fails a push whose tree differs from its own tag under an unchanged `VERSION`, added after four drifted
  releases in two days (#91).[^rule11]
- **Mandates compress acts, batches compress questions.** An audit of 280 rows found 117 accreted by
  the Agent, costing the Operator more dispositions than prompt-born rows, `archived` used zero times
  and 75 rows in `backlog`; the response (#290) was the mandate — a plan states the class and ceiling of
  rows it will open, and one plan-`Y` and one Done-`Y` cover them — with the vocabulary adopted from the
  countersign craft rather than coined.[^rule3][^plan290][^prefs]
- **Code enters with its check.** Among the implementation paths that satisfy a plan, the one chosen
  leaves reusable code carrying a mechanical check; a check that could be code is not left to
  inference, and a recurring inference task proposes code on its second occurrence.[^rule12][^rule13][^verifiable]
- **One file per id, so sessions seldom merge.** The d-work store is one row file per d-work, ids
  allocated `max(origin, local)+1`, a rendered ledger view untracked; concurrent sessions touch disjoint
  files and a push rejects only a true collision on one id.[^rule16][^stores][^rec16]
- **Decision records.** The architecture for disposition under a chief-of-staff is an ADR falsified
  across alternatives (#252); the messaging architecture between holders was audited against the
  Operator's synthesis (#302) and is tracked by one living implementation reference.[^adr252][^adr302][^msgarch]

### Framework (HOW)

- **Session start.** The Agent reads the frame and reports its sentinel, reads the ledger and reports
  every row that is not `done` with the current `merge-disposition`, touches its own presence file and
  reads every other seat's. If the frame is absent, the only permitted action is to say so and
  stop.[^rule3][^rule16]
- **Open.** Every Operator prompt opens a d-work; `dyad dwork new` allocates the id, writes the row and
  the provenance record's first entry with the prompt verbatim, and refuses a row without its
  words.[^rule3][^rule7][^packagepy] A prompt relayed by another agent is entered with the note
  `relayed via <session>`; an agent's own idea is an intake, surfaced to the Operator and opening
  nothing until the Operator disposes.[^rule3][^rule7]
- **Plan.** Before the first mutation the Agent stores a plan at `agent-corpus/d-work/plans/<id>.md` —
  intent as read, mutation, files touched, base commit of `main`, falsification — framed per Rule-10 and
  ending `Y/N: proceed with #<id> as planned?`; the plan-`Y` binds every PR of the d-work to that file,
  sets the row `planned`, and execution may start in any later session, re-planning if `main` moved past
  a touched file.[^rule15][^dyadlib][^rule3]
- **Answer.** Three answers to a counter-prompt: `Y` gives the disposition asked for; a bare `N`
  authorizes nothing; `N` with text refuses and asks for the revision in the same words — the
  countersign craft's answer grammar. Silence is never consent.[^rule3][^interaction]
- **Execute.** Work lands on a branch; the PR body cites `d-work #<id>`, and the plan gate resolves the
  id against the ledger on the base branch and requires a `Y plan` disposition.[^rule3][^prs] The
  pre-commit hook runs containment on the staged paths; the pre-push hook runs every guard over the refs
  being pushed and refuses a push it cannot judge; `dyad check --pr <base> <head>` judges the PR's whole
  diff as one zone before it is opened.[^hooks][^rule1][^rule14]
- **Host actions.** Anything on the machine that is neither a repo transaction nor read-only is
  classed read-only, reversible or destructive; a reversible action is authorized by the plan-`Y` that
  names it with its undo, a destructive one needs its own counter-prompt, and every one gets a change-log
  row. A command the Operator runs for the Agent is a committed, checked ops script, never an inline
  block.[^rule8][^hostmutation][^rule18]
- **Complete.** The reply that believes a d-work done carries the evidence: every PR by number and zone,
  each check's result as observed, every host action with its class, every accreted row, every departure
  from the plan, the evidence block of `dyad check --evidence` on the exact head, and the d-work trace;
  its last line is `Y/N: Done with #<id> <title> (merges PR #a)?`. The reply that receives the `Y`
  records it, merges as clerical execution, then closes the row — three acts in that order.[^rule3][^rule14][^trace]
- **Preferences shape the forms.** `merge-disposition: with-done` folds the merge into the Done
  question; `batch-disposition-mode: always` asks plan and Done questions over sets; `accretion:
  implicit` lets a plan's mandate scope cover the rows it opens; `concise-mode: on` means one reply per
  prompt; `delegation: plan-and-execute` lets subagents draft while the main Agent alone writes rows,
  asks and merges.[^prefs][^rule3]
- **Play-books and run-books.** Seven play-books under `dyad/playbooks/` — audit, craft-instantiation,
  d-work, disposition-digest, ds-report-incidents, dwork-trace, incident-hardening — each with its
  run-book under `dyad/runbooks/`, run through `dyad runbook run`, which prints the native command,
  tests the postcondition and appends an event.[^playbook][^runbook][^rule19]
- **Release.** `dyad bundle build` builds every component the bundle names through the one distribution
  code path; a tag is cut only on `Y/N: release <tag>?`, and the release workflow runs on the tag
  push.[^rule11][^bundlemd][^wfrelease]
- **Seats and relay.** A cos holds attention, never authority; it spins up a cabinet seat by creating a
  session and relaying the Operator's verbatim prompt, and the cabinet opens its own row, asks its own
  counter-prompts, and reports by state.[^spec253][^plan285][^seat]

## Footnotes

[^330]: `agent-corpus/audits/2026-10-17-dwork-countersign-mapping.md` @ `32a901a` (unreleased at the pin) — the audit of d-work #330: §1 the three terms as aligned, §2 the layer table, §3–§5 the mapping, §6 the divergences for the refactor.
[^row330]: `agent-corpus/d-work/rows/330.md` @ `7df0684` (unreleased at the pin) — the row: plan-`Y` 2026-10-17 (the alignment), Done-`Y` merging PR #413; the plan file is `agent-corpus/d-work/plans/330.md` @ `8346d56`.
[^versions]: `BUNDLE.md` @ `ca5d53c`, `dyad/VERSION` @ `d9df1bb`, `crafts/sysadmin/VERSION` and `crafts/countersign/VERSION` @ `0d91a54` (all unreleased at the pin); `crafts/sysarch/VERSION` @ `0d91a54`, `crafts/syseng/VERSION` @ `1d0ba9e`, `crafts/disclosure/VERSION` @ `6e8bf73` (v0.12.1) — the versions named in the pin paragraph.
[^vocab]: `dyad/vocabulary/VOCABULARY.md` @ `c110e59` (unreleased at the pin) — the master record of Agent terms: Operator, Agent, d-work, ledger, seat, holder, relayed prompt and the rest; one definition per term (Rule-6).
[^infra]: `dyad/infrastructure/INFRASTRUCTURE.md` @ `0f95143` (v0.12.1) — the manifest: the four kernel rows (Claude Code observed, Python 3.12 pinned, Git observed, pydantic pinned and not yet imported), the library rows, The World.
[^rule14]: `dyad/rules/RULE-14-system-infrastructure.md` @ `f62b829` (v0.12.1) — one manifest, the kernel, the kernel-only path as the merge evidence, hosted CI as corroboration that never gates.
[^rootframe]: `CLAUDE.md` @ `729e54e` (v0.12.1) — the host's root frame: one import line, `@dyad/CLAUDE.md`.
[^frame]: `dyad/CLAUDE.md` @ `914a42e` (v0.12.1) — the operating frame: practice, crafts, the five retained principles (two promoted to Rules, three kept as conduct), the Rule imports, vocabulary, preferences, the sentinel, repo conventions.
[^containment]: `dyad/guards/infra/containment.py` @ `92c5ea7` (v0.12.1) — the zone guard; `ZONES` is the only definition of the zone→path table (`python3 dyad/guards/infra/containment.py zones` prints it).
[^rule1]: `dyad/rules/RULE-1-containment.md` @ `996d9c9` (v0.12.1) — one zone per commit and per PR; the five zones; the host row read from the preferences; commits and range modes; the hooks as the only blocking enforcement.
[^prefs]: `preferences-corpus/PREFERENCES.md` @ `629adaf` (unreleased at the pin) — the Operator-owned table: `merge-disposition`, `batch-disposition-mode`, `delegation`, `concise-mode`, `host-path`, `host-zone`, `dwork-trace`, `accretion` and the rest, each with the Rule that reads it.
[^rule11]: `dyad/rules/RULE-11-distribution-structure.md` @ `43c3138` (v0.12.1) — craft versus instance, no clash on install, craft-relative paths, versioned releases and the drift guard, one build and install code path, generated files never tracked, the bundle release; the bundled craft and the release counter-prompt.
[^bundlemd]: `BUNDLE.md` @ `ca5d53c` (unreleased at the pin) — the bundle manifest at 0.14.0: `dyad-operator` 0.11.0, `sysarch` 0.3.0, `syseng` 0.4.0, `sysadmin` 0.3.0; `countersign` and `disclosure` held back by the Operator (#232).
[^dyadreadme]: `dyad/README.md` @ `5b07159` (v0.12.1) — the package map: every path of the core craft and the instance with its owner, what it holds and whether it reaches `main` without a `Y`; the two sets and three homes.
[^rule4]: `dyad/rules/RULE-4-integrity.md` @ `c1e7c3f` (v0.12.1) — every Agent Rule's countable block: one Intent, one Target, Boundaries, Conditions; the guard `rules.py`.
[^rule5]: `dyad/rules/RULE-5-coherence.md` @ `6f8b1ec` (v0.12.1) — coherence and orthogonality of the Rule set; `## Sets`: System Requirements (core) and System Architecture (sysarch, Tended).
[^sysarch]: `crafts/sysarch/README.md` @ `5bf06fd` and `crafts/sysarch/rules/README.md` @ `5c0c08b` (v0.12.1) — the system-architecture craft: six Tended rules, seven terms, templates, projectors, one guard; extracted from Rules 11, 12, 14, 16, 17, 20, 21 by #160.
[^syseng]: `crafts/syseng/README.md` @ `3af0eec` (v0.12.1) — the system-engineering craft: implementation discipline extracted from Rules 11–14 by #162 (naming, invariants, verifiable code, imports, determinism, idempotence).
[^rule6]: `dyad/rules/RULE-6-vocabulary.md` @ `a603d01` (v0.12.1) — every term defined once, in the vocabulary; a Rule restates consequences, never redefines; craft terms referenced by craft name.
[^playbook]: `dyad/playbooks/d-work.md` @ `5c1601b` (unreleased at the pin) — the d-work play-book (#309): the five entity records with their guards and fields, the machine table δ(state, input) → state, the lifecycle; pinned to `dyadlib` and the guards by `dyad/tests/test_playbooks.py`.
[^rule16]: `dyad/rules/RULE-16-concurrent-sessions.md` @ `59dffee` (unreleased at the pin) — the store: one row file per d-work, the transition table, the optional `mode`; presence files with `root`, `rows`, `files`, `host`, `holder`; the same-root signal.
[^rule7]: `dyad/rules/RULE-7-provenance.md` @ `8debc57` (unreleased at the pin) — one record per d-work, numbered fenced entries, the Operator's words only, written when it happens, checked against the row; the transcript never committed.
[^dyadlib]: `dyad/scripts/dyadlib.py` @ `164b8cd` (unreleased at the pin) — `STATES`, `NEW_STATES`, `TRANSITIONS`, `INPUT_KINDS`, `TERMINAL_STATES`, `INPUTS` (one entry per edge and birth), `PLAN_PARTS`; the shared library of the runner and the guards.
[^packagepy]: `dyad/scripts/package.py` @ `2743ca3` (unreleased at the pin) — the runner: `check`, `check --list` (the guard registry: 24 modules at the pin, 16 core, 8 craft, 5 transaction — observed output), `check --guards --pre-push`, `check --pr`, `check --evidence`, `dwork new|state|retire|list|trace`, `session touch|list`, `ledger`, `build`, `install`, `bundle`, `craft`, `project`, `runbook`.
[^guardsmd]: `crafts/sysarch/rules/guards.md` @ `ee2adf8` (v0.12.1) — the guard contract and layout: one module per entity kind under the corpus of its store, data beside it, the parser other code imports, discovered over two roots.
[^rule20]: `dyad/rules/RULE-20-referential-integrity.md` @ `8268359` (v0.12.1) — one register, one resolver per reference kind, existence only; severity: unresolved fails, `world` warns, an absent store skips. Guard `dyad/guards/agent/references.py` @ `511d6a0` (v0.12.1).
[^rule12]: `dyad/rules/RULE-12-verifiable-code.md` @ `35be2b9` (v0.12.1) — code enters the package with its mechanical check; `INVARIANTS` enforced at import, `TREE_INVARIANTS` in the runner's pass; the suite run by the runner, not by hand.
[^invariants]: `crafts/syseng/rules/invariants.md` @ `f9216f1` (v0.12.1) — the invariant protocol: pure predicates in `INVARIANTS`, tree-reading ones in `TREE_INVARIANTS`, never `assert`.
[^distribute]: `dyad/scripts/distribute.py` @ `20c38fb` (v0.12.1) — the one distribution code path: deterministic build, idempotent install, the instance-state scan, used by `dyad build|install` and `dyad craft export|install`; the drift guard is `dyad/guards/infra/bundle.py` @ `a9ad3f2` (v0.12.1).
[^seat]: `agent-corpus/falsification/seat-vs-harness-session.md` @ `c95ecb2` (unreleased at the pin) — the seat model (#295): a seat is a durable name bound to one presence file, held by one harness session at a time and many over time, never verifiable by the dyad; `cos` and `cabinet` are roles a seat plays.
[^msgarch]: `agent-corpus/architecture/MESSAGING-ARCHITECTURE.md` @ `c1f3e00` (unreleased at the pin) — the living implementation reference (#310): what is built (the presence store, the ledger as state, the relayed prompt, the intake), the transport substitute in use, the `backlog` rows that build the rest.
[^schema]: `crafts/countersign/rules/schema.md` @ `d97aad2` (v0.12.1) — the Countersign core schema: eight entities and one attribute, mapped to by projection; "logical, not a storage format"; the JSON Schema at `crafts/countersign/templates/countersign-core.json`.
[^interaction]: `crafts/countersign/rules/interaction.md` @ `41f1566` (v0.12.1) — the interaction model: five primitives, eight imperatives, one lifecycle per mode, the answer grammar (§2), the escalate edge (§4), preferences classed as form or authority (§5), the four refactors owed by dyad-system (§7); it binds no system's agent by itself.
[^projector]: `crafts/countersign/projectors/project_countersign.py` @ `0bd735c` (unreleased at the pin) — the projector that derives the core from the d-work stores under derivation rules D1–D8; `validate` and `check` are the countersign side's mechanical check.
[^row334]: `agent-corpus/d-work/rows/334.md` @ `14d5c41` (unreleased at the pin) — row #334, `planned` at the pin, seat `ds-cabinet-cloud-1`: falsify "the core = countersign" and "d-work is an instance of countersign"; its record will be `agent-corpus/falsification/core-vs-countersign.md`.
[^rule2]: `dyad/rules/RULE-2-no-self-ratify.md` @ `61ef282` (unreleased at the pin) — disposer ≠ proposer; the ratification events; what is not ratification; the binding of a `Y` to the action named, the kernel-only evidence, the mandate clause; provenance `bond:no-self-ratify`.
[^rec2]: `dyad/falsification/rules/rule-2-no-self-ratify.md` @ `ea92605` (unreleased at the pin) — the record behind Rule-2: the attacks on inference-only enforcement, the batch-binding amendment (#17) and the mandate amendment (#290).
[^rule3]: `dyad/rules/RULE-3-d-work.md` @ `a55e935` (unreleased at the pin) — the d-work: scope, the answer grammar, the plan gate, the ledger states, mechanisms (the fence), the completion counter-prompt and its three-act Done order (#202), batch disposition, intake, incidents, ratification events; provenance of every amendment.
[^rows]: `dyad/guards/agent/rows.py` @ `33b0e6d` (unreleased at the pin) — the main fence: append-only rows, immutable ids and titles, transitions in the table, ledger-only direct commits to `main`, the Done order and landing checks.
[^rule9]: `dyad/rules/RULE-9-falsification.md` @ `4e003e2` (v0.12.1) — falsify every claim before it is encoded; the record form (attack, result, survivor); "no attack found" only by naming what was tried; easy agreement pushed.
[^rec910]: `dyad/falsification/rules/rules-9-10-promotion.md` @ `113bd93` (v0.12.1) — the record of promoting falsification and proposal-framing from frame principles to Rules (gap E2, audit 2026-09-12).
[^rule10]: `dyad/rules/RULE-10-proposal-framing.md` @ `dc65403` (v0.12.1) — one path, its strongest counter, a reconciliation, one `Y/N` last; the `concise-mode` form.
[^rec14]: `dyad/falsification/rules/rule-14-system-infrastructure.md` @ `22edf0c` (v0.12.1) — the record behind Rule-14: attacks on the kernel definition, the kernel-only path (I2), the pre-push amendment (#194).
[^workflows]: `.github/workflows/dyad-containment.yml` @ `372d5b8`, `.github/workflows/dyad-d-work.yml` @ `d2a461d`, `.github/workflows/dyad-package.yml` @ `f7e8d15` (v0.12.1) — the CI wrappers: `on: push: branches: [main]` with `agent-corpus/d-work/**` ignored, and `workflow_dispatch`; no PR trigger (removed by #168).
[^rec7]: `dyad/falsification/rules/rule-7-provenance.md` @ `f49aa6f` (unreleased at the pin) — the record behind Rule-7: why the transcript is never committed, the transaction/state split (#191), the mandate note (#290).
[^plan202]: `agent-corpus/d-work/plans/202.md` @ `469c5c6` (unreleased at the pin) — the plan that moved `done` after the merge: the mechanism, the eleven instances, the three-act order.
[^incidents]: `agent-corpus/audits/INCIDENTS.md` @ `147e937` (unreleased at the pin) — the incident log (date, d-work, what, cause, consequence), the ledger the incident-hardening play-book groups into failure modes.
[^rec11]: `dyad/falsification/rules/rule-11-distribution-structure.md` @ `1b75139` (v0.12.1) — the record behind Rule-11: the craft reframing (#153, #154), one code path (#156), the tag prefixes (#196), the drift guard (#91), the bundled craft (#114), the bundle's released-craft sentence (#230).
[^plan290]: `agent-corpus/d-work/plans/290.md` @ `ce3fa3d` (unreleased at the pin) — the plan that introduced the mandate and the `accretion` preference: the audit numbers (117 of 280 rows accreted, mean 2.65 dispositions against 2.15, `archived` used 0 times, 75 rows in `backlog`) and the five revisions.
[^rule13]: `dyad/rules/RULE-13-reuse-over-inference.md` @ `fb3d5aa` (v0.12.1) — recurrence proposes code; the import criteria are the Operator's preferences.
[^verifiable]: `crafts/syseng/rules/verifiable-code.md` @ `ab30415` (v0.12.1) — code over inference, the chosen path and its reuse yield, the module-to-test mapping.
[^stores]: `crafts/sysarch/rules/stores.md` @ `7fbf938` (v0.12.1) — the store pattern: one file per instance, a rendered view untracked, ids `max(origin, local)+1`, no hand edits, the append-only fence.
[^rec16]: `dyad/falsification/rules/rule-16-concurrent-sessions.md` @ `39fa70e` (unreleased at the pin) — the record behind Rule-16: the live cross-session near-miss that produced the presence store (#185), `backlog → archived` and `mode` (#290), `host` and `holder` (#294).
[^adr252]: `agent-corpus/audits/2026-10-08-adr-disposition-architecture.md` @ `dcd9730` (unreleased at the pin) — the ADR (#252): alternative architectures for disposition under a chief-of-staff, falsified; the specification is `agent-corpus/audits/2026-10-08-spec-session-messaging-control.md` @ `117e582` (#253, R1–R29).
[^adr302]: `agent-corpus/audits/2026-10-15-messaging-architecture.md` @ `c28c0ea` (unreleased at the pin) — the topic audit (#302) of the messaging architecture and framework between holders, gaps G1–G8.
[^rule15]: `dyad/rules/RULE-15-d-work-phases.md` @ `ee64de2` (unreleased at the pin) — planning stored at `plans/<id>.md` before the counter-prompt, execution in any later session, re-planning when `main` moved past a touched file; an accreted row has no plan of its own. Guard `dyad/guards/agent/plans.py` @ `b1dc474` (v0.12.1).
[^prs]: `dyad/guards/agent/prs.py` @ `80a3d3b` (v0.12.1) — the plan gate: a PR body or branch commit messages citing `d-work #<id>` resolve to a row on the base branch that is `open`, `planned` or `blocked` and carries `Y plan`; a ledger-only range is exempt.
[^hooks]: `dyad/hooks/pre-commit` @ `c2eac54` and `dyad/hooks/pre-push` @ `eceda8c` (v0.12.1) — containment over the staged paths; `package.py check --guards --pre-push` over the refs being pushed; installed by `git config core.hooksPath dyad/hooks`.
[^rule8]: `dyad/rules/RULE-8-host-mutation.md` @ `d9cca0c` (v0.12.1) — three classes of host action, the authorization each needs, the change-log row, read-before-act, never from a subagent.
[^hostmutation]: `crafts/sysadmin/rules/host-mutation.md` @ `d500ad8` (v0.12.1) — the sysadmin craft's class table with examples, the read-before-act procedure, the change log's columns.
[^rule18]: `dyad/rules/RULE-18-ops-scripts.md` @ `77176b2` (v0.12.1) — a command the Operator runs for the Agent is a committed, executable, syntax-checked shell file whose text and outcome are provenance; never an inline block.
[^trace]: `dyad/playbooks/dwork-trace.md` @ `e8bed85` (unreleased at the pin) — the d-work trace play-book (#213): one timeline from the first prompt to the Done question, every second in one bucket; written by the Done record commit under `dwork-trace: always`.
[^runbook]: `dyad/runbooks/d-work.md` @ `19417fb` (unreleased at the pin) — the d-work run-book: `open`, `plan`, `authorize`, `execute`, `evidence`, `record`, `complete`, `defer`, `resume`, run as `DWORK=<id> dyad runbook run d-work <step>`.
[^rule19]: `dyad/rules/RULE-19-server-instances.md` @ `a01d809` (v0.12.1) — every server instance leaves a run-book and a health command; the core runner `dyad runbook` records an event per command.
[^wfrelease]: `.github/workflows/dyad-release.yml` @ `3310439` (v0.12.1) — the release workflow: `on: push: tags: ["v*", "*-v*"]` and dispatch with an existing tag.
[^spec253]: `agent-corpus/audits/2026-10-08-spec-session-messaging-control.md` @ `117e582` (unreleased at the pin) — the specification (#253): R4 a cabinet reports by state, never by message; R28–R29 the cos and cabinet roles and the relayed prompt.
[^plan285]: `agent-corpus/d-work/plans/285.md` @ `abb157f` (unreleased at the pin) — the cos's standing discipline: the six rules of the role, defined by the plan the Operator ratified; a cos holds attention, never authority.
