# Rule-1: containment

**Intent:** Confine every repo transaction to exactly one zone.
**Target:** a repo transaction (a commit or a PR).

## Boundaries (out of scope)
- Who may merge or push — Rule-2. When work opens or closes — Rule-3.
- What a Rule must look like — Rule-4; how Rules relate — Rule-5.
- Content of files: Rule-1 sees paths only. The live host — Rule-8.

## Conditions (triggers)
- A commit is created (`dyad/hooks/pre-commit`, blocking).
- Commits are pushed (`dyad/hooks/pre-push` → `dyad check --guards`, blocking; each commit of the
  range, never the range itself — a push range is not a transaction, #166).
- A PR is about to be opened or updated (`dyad check --pr <base> <head>`, run by the Agent), and
  `main` is pushed (`.github/workflows/dyad-containment.yml`, detecting, after the merge).
- A path is added that no zone claims (forbidden).

The repo has five zones — `agent`, `workstation`, `preferences`, `infra`, `craft` (`crafts/*`: every
Tended craft's tree (a craft corpus), one zone so a craft changes by craft PRs and never mixes with
instance PRs — what makes it exportable, #153). A commit touches exactly one.
A PR touches exactly one. The zone→path table is defined **only** in
`dyad/guards/infra/containment.py` (`ZONES`; the zone guard, placed per Rule-11 property 1); print it with
`dyad/guards/infra/containment.py zones`.

Unclassified paths are forbidden. Cross-zone work = separate branches, separate PRs;
change the referent before the referrer.

The guard runs in two modes, because the Rule binds a commit and a PR and nothing else: *commits*
— each non-merge commit of a range, what `dyad check --guards` runs before every push, so a push of
several single-zone commits that together span zones is correct; and *range* — those commits **and**
the whole `base...head` diff, which is the PR, run by `dyad check --pr <base> <head>` before a PR is
opened and by the detector over what lands on `main` (#166). Since the PR trigger was removed (#168)
no runner judges a PR's whole diff *before* it merges: one zone per PR is the Agent's conduct plus
that command, reported in the completion evidence, not a gate.

Enforcement: `dyad/hooks/pre-commit` (local, blocking; `git config core.hooksPath dyad/hooks`),
`dyad/hooks/pre-push` (local, blocking, commits mode) and `.github/workflows/dyad-containment.yml`
(CI, detecting, range mode). All call `dyad/guards/infra/containment.py`. Before any commit in this repo,
run `git config core.hooksPath dyad/hooks` if not already set. Until d-work #24 (internal
LAN git server with required status checks) lands, these hooks are the only *blocking*
enforcement of Rule-1; CI only detects.


## Provenance
Operator rule, 2026-09-12. Falsified; see `../falsification/rules/rule-1-containment.md`.
Lived in the root `CLAUDE.md` until 2026-09-13 (A2, Rule-11 property 2: host files hold only an import line).

Set: System Requirements.
