# Rule-1: containment

**Intent:** Confine every repo transaction to exactly one zone.
**Target:** a repo transaction (a commit or a PR).

## Boundaries (out of scope)
- Who may merge or push — Rule-2. When work opens or closes — Rule-3.
- What a Rule must look like — Rule-4; how Rules relate — Rule-5.
- Content of files: Rule-1 sees paths only. The live host — Rule-8.
- A session-level restriction on which branches may be pushed (a harness's, a hosting's): an
  Operator-side fence outside the corpus, per session, as Rule-8 says of the harness permission
  mode per command; it neither replaces nor is replaced by this Rule. Where such a fence forbids
  what a Rule prescribes — the ledger-only commit to `main` that Rule-2 and Rule-3 make clerical is
  the case found (#23) — the Agent does the corpus-legal part it can, states the rest and asks; it
  never reads permission out of the Rule alone.

## Conditions (triggers)
- A commit is created (`dyad/hooks/pre-commit`, blocking).
- Commits are pushed (`dyad/hooks/pre-push` → `dyad check --guards --pre-push`, blocking, over the
  refs being pushed — Rule-14 property 3, #194; each commit of the range, never the range itself — a
  push range is not a transaction, #166).
- A PR is about to be opened or updated (`dyad check --pr <base> <head>`, run by the Agent), and
  `main` is pushed (corroboration, `dyad check --corroborate`, Rule-14 property 3 — run by `.github/workflows/dyad-package.yml`
  or by the automaton's job — its step `rule-1 containment (push range)`, detecting, after the merge, over each PR the push lands and each
  direct commit, #589).
- A path is added that no zone claims (forbidden).

The repo has five zones — `agent`, `workstation`, `preferences`, `infra`, `craft` (`crafts/*`: every
Tended craft's tree (a craft corpus), one zone so a craft changes by craft PRs and never mixes with
instance PRs — what makes it exportable, #153). A commit touches exactly one.
A PR touches exactly one. The zone→path table is defined **only** in
`dyad/guards/infra/containment.py` (`ZONES`; the zone guard, placed per Rule-11 property 1); print it with
`python3 dyad/guards/infra/containment.py zones`. Its host row alone is instance data: the host path
and its zone are the preferences `host-path` and `host-zone` (`preferences-corpus/PREFERENCES.md`;
defaults `workstation-corpus` and `workstation`), and `infra` puts the host path in the infra zone,
a four-zone system with no `workstation` zone (#175).

Unclassified paths are forbidden. Cross-zone work = separate branches, separate PRs;
change the referent before the referrer.

The guard runs in two modes, because the Rule binds a commit and a PR and nothing else: *commits*
— each non-merge commit of a range, what `dyad check --guards` runs before every push, so a push of
several single-zone commits that together span zones is correct; and *range* — those commits **and**
the whole `base...head` diff, which is the PR, run by `dyad check --pr <base> <head>` before a PR is
opened and by the detector over each PR that lands on `main` — the merge's own range, so a push landing a cut of
several single-zone PRs is correct — with a direct, non-merge commit on `main` judged alone in *commits* mode (#166,
#589; containment's `landed` mode). Since the PR trigger was removed (#168)
no runner judges a PR's whole diff *before* it merges: one zone per PR is the Agent's conduct plus
that command, reported in the completion evidence, not a gate.

Enforcement: `dyad/hooks/pre-commit` (local, blocking; `git config core.hooksPath dyad/hooks`),
`dyad/hooks/pre-push` (local, blocking, commits mode) and corroboration (`dyad check --corroborate`, Rule-14 property 3:
its steps `rule-1 containment (push range)` and `rule-1 containment (tree)`)
(after the merge, detecting: each PR the push lands in range mode, each direct commit in commits mode, #589). All call `dyad/guards/infra/containment.py`. Before any commit in this repo,
run `git config core.hooksPath dyad/hooks` if not already set. Until d-work #24 (internal
LAN git server with required status checks) lands, these hooks are the only *blocking*
enforcement of Rule-1; CI only detects. A hook that cannot execute at all — an exec bit lost from
the guard it runs by path, an interpreter below the kernel pin — leaves that enforcement vacuous,
so the Agent runs the guard by hand, records its observed line and the bypass in the commit
message, and reports an incident (Rule-3); it never repairs the hook inside an unrelated d-work,
and never bypasses a hook that runs and fails (#23).


## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-1-containment.md`.
Lived in the root `CLAUDE.md` until 2026-09-13 (A2, Rule-11 property 2: host files hold only an import line).
The host row is read from the preferences 2026-09-25 (d-work #175); see the same record, amendment #175.
The push condition names `--pre-push` and the refs being pushed 2026-09-29 (d-work #194); see the same
record, amendment #194. Conditions and Enforcement names `.github/workflows/dyad-package.yml` and its step in place of `dyad-containment.yml` 2026-10-26 (d-work #477, C4
of #473): the four guard wrappers became steps of one CI job, same guards, same triggers, still detecting; see the same
record, amendment #477. Conditions and Enforcement name corroboration's steps in place of the CI job's 2026-11-03 (d-work #564): the
job's steps became one command, `dyad check --corroborate`, run in hosted CI and in the automaton's job; same guards, still
detecting; see `../falsification/rules/rule-14-system-infrastructure.md`, amendment #564. Conditions, the modes paragraph and Enforcement say the detector judges each PR a push lands and each
direct commit alone 2026-11-04 (d-work #589): since #562 one push to `main` lands a cut of several PRs, and judging the
push range as one PR failed #573's three-PR cut (agent plus preferences); see the same record, amendment #589.

Set: System Requirements.
