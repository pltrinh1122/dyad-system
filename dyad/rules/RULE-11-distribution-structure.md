# Rule-11: distribution structure

**Intent:** Shape every craft so it can be built, versioned, released and installed in another
dyad system without clashes or hand-editing.
**Target:** a craft (its tree in the repo; the core craft `dyad-operator` at `dyad/` and every Tended craft at `crafts/<craft>/`)

## Boundaries (out of scope)
- What any guard checks — the System Requirements Rule that owns it.
- Zones and transactions — Rule-1; a structural change is an infra-zone PR citing a Rule-11 d-work.
- The content of Rules, vocabulary, preferences — their owning Rules.
- The host and Tended Rules' content — instance or a Tended craft's; never the core craft.
- Which craft a rule belongs to — Rule-4 classifies (an Agent Rule binds the Agent's process and
  lives in the core craft; a Tended Rule lives in a Tended craft or in `workstation-corpus/rules/`
  until extracted).
- The design behind these kernels — what is craft and what instance, craft-relative paths, the
  archive and version seed, the entrypoint shape: the sysarch craft's `crafts/sysarch/rules/distribution.md`;
  the full guard contract and layout: `crafts/sysarch/rules/guards.md`. Rule-11 keeps the sentences
  Rule-2's Binding and Rule-3's completion evidence rely on (#160).

## Conditions (triggers)
- A file is added to or moved within a craft.
- A release is cut (see Ratification events).
- An install is performed in another session.
- A craft is exported or installed (`dyad craft export|install`; `dyad build|install` for the core craft).
- Every push and PR: `dyad/scripts/package.py` (check, build, install; Rule-11 owns it) and, from A4, the release workflow (`dyad-release.yml`).
- A generated file is tracked (`package.py check` refuses it).
- `BUNDLE.md` is added or edited, or a craft's `VERSION` changes while a bundle exists (`dyad
  bundle check|build`).

## Properties
1. **Craft / instance.** Every tracked file is one or the other. The **core craft**,
   `dyad-operator` — what this Rule called *the package* — is the one craft every system has; its
   root is `dyad/`; the falsification records of Rules travel with it (`falsification/rules/`, A6).
   A **Tended craft** is any other craft; its root is `crafts/<craft>/` (zone `craft`, Rule-1).
   Every craft is one directory tree with one root (a craft corpus, Rule-1). The guards live under
   `dyad/guards/<corpus>/`, one module per entity kind beside its data, and a Tended craft's under
   `crafts/<craft>/guards/` (the layout and the guard contract: `crafts/sysarch/rules/guards.md`).
   The instance is never inside a craft: `package.py check` refuses host-specific strings and
   instance artifacts (by name or header) inside the core craft — the list is data,
   `dyad/scripts/package_rules.txt` (A7) — and the craft guard runs the same scan over every Tended
   craft.
2. **No clash on install.** Installing a craft writes only under that craft's root plus, for the
   core craft, a documented, prefixed set of host-side hooks (workflow files prefixed `dyad-`; one
   import line in the host's frame). It never overwrites a host file. A Tended craft install writes
   only `crafts/<craft>/` and its row in `crafts/REGISTRY.md` (the craft registry: craft, version,
   source, sha256, d-work — instance state in the craft zone, written by `dyad craft install`, never
   by hand); host-side hooks are the core craft's only. An install refuses to overwrite a tree the
   receiving system modified or authored (the registry's `sha256` is the proof of an unmodified
   tree) unless told `--force`, and refuses an unmet `requires:` of the craft's `MANIFEST.md`
   (`<craft>>=<semver>`, a craft another craft's rules cite; never fetched). A `seeds:` entry of
   the same file (`<template>-><instance path>`) names an instance file one of the craft's own
   templates corresponds to; `craft check`/`install` warn when the destination is absent —
   advisory only, never written by install (host-side hooks stay the core craft's only, above).
   The one command-line entrypoint is `dyad/bin/dyad`, invoked by path (its shape: `distribution.md`).
   A core-owned table that holds craft-varying data accepts a craft-shipped contribution,
   discovered like a guard and reported under the contributing craft's own name, so the data
   leaves when the craft does (`agent-corpus/falsification/extensibility.md`, #101). A **bundled
   craft** is a Tended craft the core release carries: `dyad build` puts its tree in the core's
   archive and `dyad install` writes it, so a system that installs the core alone still has it.
   It stays a Tended craft in every other respect — its own root, its own zone, its own `VERSION`
   and its own `<craft>-vX.Y.Z` tag (property 4) — and it is bundled only because it says so
   itself, in the contribution shape above (a `BUNDLED_WITH_CORE` declaration in one of its own
   guard modules, discovered like a guard), never by a list the core keeps: a craft removed from
   the tree takes its own claim with it. A core Rule that cites a craft by path is the reason to
   bundle one — what the core ships and what its own Rules depend on must not disagree — and it is
   the only reason the core's install may write outside its own root.
3. **Craft-relative paths.** Craft files reference their own paths relative to the craft root, and
   instance paths through one instance location, `DYAD_INSTANCE` (default `agent-corpus`;
   `crafts/sysarch/rules/distribution.md`). Paths printed in Rule text are the defaults.
4. **Versioned releases.** Every craft carries a `VERSION` at its root. The core craft's release
   is a git tag `dyad-operator-vMAJOR.MINOR.PATCH` equal to `dyad-operator-v` + `dyad/VERSION`; a
   Tended craft's release is a git tag `<craft>-vMAJOR.MINOR.PATCH` equal to `<craft>-v` +
   `crafts/<craft>/VERSION` — every craft, core or Tended, prefixed by its own name (#191, #196),
   so a craft's tags never collide with another's or with the bundle's (property 7) in one repo —
   a craft released on its own cadence in the monorepo that authors it, its archive the `export` of
   that tag's tree, distributable to a separate repo without moving where the craft is authored.
   Archive shape and version seed: `distribution.md`. The converse holds too: once a craft's tag
   exists, the tree under its root at HEAD is the tree that tag holds, or `VERSION` has moved —
   `dyad/guards/infra/bundle.py` `check_drift` fails the push that differs from its own tag under
   an unchanged `VERSION`, and skips with one line where the tag does not resolve locally (#91,
   after four drifted releases in two days: #61, #67, #71, #90).
5. **Built and installed by one code path, tested in CI.** A craft, core or Tended, is built and
   installed by `dyad/scripts/distribute.py` — `dyad build|install` for the core craft (with the
   core's hooks), `dyad craft export|install` for a Tended craft (`dyad/scripts/craft.py`, no
   hooks) — and the difference between them is data (the hook set), not a second path; CI installs
   the core and a Tended craft into a scratch repo and runs the guards there (`dyad-package.yml`).
   The hook ships at `dyad/hooks/pre-commit`; an install sets `core.hooksPath dyad/hooks` and never
   writes a host's `.githooks/`. A failing craft is neither exported nor installed. That the build
   is deterministic and the install idempotent (a second install is `0 changes`) is the syseng
   craft's discipline: `crafts/syseng/rules/idempotence.md` (property 1) and
   `crafts/syseng/rules/determinism.md` (property 4).
6. **Generated files are never tracked.** `package.py check` refuses any tracked path matching a
   generated pattern; the list is data (`package_rules.txt`, `generated:` entries, ledger #108).
   What counts as generated and why it is never committed is the syseng craft's
   `crafts/syseng/rules/determinism.md` (property 1).
7. **Bundle release.** The whole distribution this repo authors — the core craft plus every Tended
   craft in the tree — is named at pinned versions by one bundle manifest, `BUNDLE.md` at the repo
   root (infra zone, Rule-1: a distribution artifact of the authoring repo, never craft content, so
   a core-only install carries no bundle naming a craft it lacks; property 1's instance-inside-a-craft
   refusal is unaffected — the bundle sits outside every craft). One row per craft in the tree, each
   row's version equal to that craft's live `VERSION`; the bundle carries its own version, independent
   of the core's — a craft-only change bumps the bundle, never forcing an unrelated core bump. An
   unreleased craft (no `<craft>-vMAJOR.MINOR.PATCH` tag of its own, property 4) may be absent from
   the bundle until its first release, whose release adds its row; a released craft without a row
   fails. Its release is a git tag `vMAJOR.MINOR.PATCH` equal to `v` + `BUNDLE.md`'s version: the
   unprefixed form, the GitHub convention and the repo's one front door, built by sequencing
   property 5's one code path once per row (never a second build mechanism) and publishing every
   component's archive together. A system that wants only some components pins them individually by their own crafts'
   tags (property 4); the bundle is the convenience of pinning all of them at once, never the only way.

## Ratification events
- Answering `Y` to a release counter-prompt, form `Y/N: release <tag>?` — `<tag>` is
  `vMAJOR.MINOR.PATCH` for the bundle (property 7), `dyad-operator-vMAJOR.MINOR.PATCH` for the core
  craft and `<craft>-vMAJOR.MINOR.PATCH` for a Tended craft (property 4). The `Y` binds to that one
  tag only; creating and pushing the tag, exporting the archive, publishing any artifact it names
  (an image, an archive to a distribution repo) are clerical execution of it. Rule-2 applies by
  reference (S2). A release publishes to the world, so it is the Operator's to ratify however few
  d-works it gathers — distinct from a d-work's Done-`Y`, which verifies that d-work's own output.
- Or, naming several tags in one question — `Y/N: release <tag-a>, <tag-b>, <tag-c>?` — whose
  content was already verified and ratified by one d-work's own Done-`Y`, each tag already named
  individually, unmerged, in the same reply's completion evidence before this question (the same
  discipline Rule-3's own Done-batch items already carry). Never a tag of a different d-work;
  never folded into Rule-3's plan or Done batch, so a release stays its own, visibly-a-publication
  moment. A `Y` ratifies exactly the named tags; anything else, none of them (Rule-2, Binding).

## Enforcement
`dyad/scripts/package.py check` on every push and PR (A5): a runner that first runs the invariant
pass — every model module's `INVARIANTS`, one `[invariant]` line each, before any check
(`crafts/syseng/rules/invariants.md`; the term `invariant` is Rule-12's) — then Rule-12's check
and every guard of the registry it discovers under `dyad/guards/` and every Tended craft's
`crafts/<craft>/guards/` (`check --list` prints it) and owns none of their semantics; Rule-11's own
check is structural — craft versus instance, paths, VERSION (S4). The same structural check over
every Tended craft is the craft guard, `dyad/guards/craft/crafts.py` (entity `craft`, corpus `craft`,
data `dyad/guards/craft/crafts_rules.txt`; the runner invokes it as `craft/crafts`; `dyad craft check`
runs it by hand): `VERSION` one semver line; no instance state inside the tree
(`distribute.instance_state`, the scan the core uses, with `package_rules.txt` plus the
craft-specific names — `REGISTRY.md`, `events/`, `rows/`, `*.jsonl`); the craft vocabulary namespaced
(`vocabulary.py check_craft`, Rule-6's); every craft guard meets the contract (`dyadlib.contract_problem`,
the one definition `crafts/sysarch/rules/guards.md` describes); Agent-process tokens in a Tended rule
warn (`rules.py check_tended`, Rule-4's); an unmet `requires:` warns at check and fails at install.
The guard composes those scans by import; it owns only the craft's shape (S4). Property 7's bundle
is checked the same way: `dyad/guards/infra/bundle.py` (entity `bundle`, corpus `infra`; a missing
`BUNDLE.md` skips, never fails — property 4's absent-store pattern), registered by discovery like
every other guard (no hand-listing here either).

## Provenance
Operator rule, 2026-09-13 (Architecture Rule 1). Falsified; see
`../falsification/rules/rule-11-distribution-structure.md`. Reframed 2026-09-14 (#154, per #153
revision 2): the package is the core craft; properties bind every craft. One distribution code path,
the craft guard, `crafts/REGISTRY.md`: 2026-09-14 (#156, attacks A8–A18). Design clauses (p1's
craft/instance lists, p3's mechanism, p4's archive shape, the entrypoint shape) moved to
`crafts/sysarch/rules/distribution.md` 2026-09-14 (#160); the kernel stays here. Implementation
clauses (p5's determinism and idempotence, p6's discipline) moved to `crafts/syseng/rules/idempotence.md`
and `crafts/syseng/rules/determinism.md` 2026-09-14 (#162); one-line stubs keep the data and the
check here; the runner's invariant pass is named in Enforcement. Property 2 gains one sentence,
`MANIFEST.md` `seeds:` (advisory instance-seed mapping; never written by install) 2026-09-14 (#180).
Property 7 added, property 4 reprefixed (#196, d-work #21): the core craft's tag gains the
`dyad-operator-` prefix it lacked, freeing the unprefixed `vX.Y.Z` for a new bundle release naming
the whole distribution — `v0.3.1`, `v0.3.2`, `v0.4.0` predate this and stay core-only tags, cut
under the superseded convention, never retagged (tags do not move). See
`../falsification/rules/rule-11-distribution-structure.md`, amendment #196. Property 4 gains its
converse and the drift guard 2026-09-18 (d-work #91); see the same record, amendment #91. Property
2 gains the craft-contribution sentence 2026-09-20 (d-work #100, per #101's survivor); see the same
record, amendment #100. Ratification events gains the release-batch form 2026-09-21 (d-work #106):
several tags whose content one d-work's own Done-`Y` already verified, each already named
individually beforehand — split from destructive's unconditional one-per-question rule, which
rested on a different, unaffected basis; see the same record, amendment #106. Property 2 gains the
bundled craft 2026-09-22 (d-work #114): four core Agent Rules cite `crafts/sysadmin/` by path while
the core release shipped without it, and a core-only install of `main` was red; see the same
record, amendment #114. Property 7 gains the unreleased-craft sentence 2026-09-24 (d-work #156):
adding any new craft had no order satisfying both Rule-1 (one zone per PR) and the bundle guard; see
the same record, amendment #156 (2026-09-24).

Set: System Requirements (kernel; content: crafts/sysarch/rules/distribution.md, crafts/syseng/rules/idempotence.md, crafts/syseng/rules/determinism.md).
