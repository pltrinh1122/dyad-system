# Falsification record — Rule-11 (distribution structure), Architecture Rule 1 (ledger #72)

**Claim (operator, 2026-09-13):** the repo structure should reduce error (naming clashes) and
friction (specific release version) for building and releasing distribution packages for
installation in other dyad sessions.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | No package boundary exists; "structure reduces error" has no referent. | Confirmed | Property 1: package / instance, every file one or the other, one package root. |
| 2 | Clashes are concrete: root `CLAUDE.md`, `README.md`, `.github/workflows/*` (GitHub-fixed path). | Confirmed | Property 2: write only under the root plus prefixed hooks and one import line; never overwrite. |
| 3 | Root-relative paths everywhere make relocation break every guard. | Confirmed | Property 3: package-relative paths, one instance location. |
| 4 | No versions to pin. | Confirmed | Property 4: tags, VERSION, archive, instance records its version. |
| 5 | Restructuring is a migration, not a Rule. | Survives | Rule states properties; the audit lists gaps A1–A7 as d-works. |
| 6 | Overlap with Rule-1 (zones). | Survives | Rule-11 names Rule-1 in Boundaries; zone changes are infra PRs citing Rule-11 d-works. One-way. |
| 7 | Overlap with Requirement Rules that own guards. | Survives | Set boundary (#71): Rule-11 owns where/how; never what a guard checks. |
| 8 | Nobody has asked to install elsewhere. | Survives | Package / instance also keeps the archive and host report out of anything shared. |

## Rule-5 pairwise statements (Rule-11 added)
- 11–1: structure vs transactions; one-way, named. 11–2: releases and installs are ratification
  events? A release is a push of a tag to `main`'s history — an Operator act; Rule-11 declares
  no new event; cutting a release is a d-work whose Done-`Y` ratifies the tag (Rule-3). 11–3:
  each gap is a d-work. 11–4: block conforms. 11–5: this statement; Rule-5 sweeps across sets.
  11–6: four terms. 11–8: the host is instance. 11–9: this record. 11–10: gaps framed per
  Rule-10 when proposed. Coherent, orthogonal.

## Rule-6: `package`, `instance`, `release`, `install` added, owner 11.

Disposition: see ledger #72.

## #152 amendment (2026-09-14): preference `cli-pattern`
| # | attack | result | survivor |
|---|---|---|---|
| A | The entrypoint is a host-side install artifact (Rule-11 p2 clash). | Refuted | It lives under the package root and is invoked by path; nothing is written to PATH. |
| B | A wrapper that prints the native line is still a second way to run a command. | Survives, scoped | The printed line is the native one; the wrapper adds telemetry (Rule-19, #150) and nothing else. |
Pairwise: Rule-11 gains one sentence reading a preference value; no other Rule's concern moves (Rule-11 owns the entrypoint's placement, Rule-19 the run-book command's form, the preference the value). Coherent and orthogonal with every other Rule as before.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
p1 gains one sentence — guards live under `dyad/guards/<corpus>/`, one module per entity kind beside its data (Rule-21) — and a Boundary naming Rule-21; Enforcement names the discovered registry instead of hand-listed check functions. Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #154 (2026-09-14, craft reframe)
Intent, Target and properties 1–6 reframed per #153 revision 2: the package is the core craft
`dyad-operator` (`dyad/`); the properties bind every craft (one root, `VERSION`, no instance state,
idempotent scripted install, generated files never committed); a Tended craft's root is
`crafts/<craft>/`. Tended-craft install/check deferred to #156. Full record: plan #154.
| # | attack | result | survivor |
|---|---|---|---|
| 2 | Renaming "package" breaks code, data and tests that say "package" (`package.py`, `package_rules.txt`, `package_files()`, `check_package`, guard messages, `tree:package`, `test_package.py`). | Confirmed, scoped | Nothing in code, data, messages or tests is renamed; `package` stays a vocabulary term for the core craft's distributable form; the Rule says "what this Rule called *the package*". Renaming is #160's or #156's, if ever. |
| 3 | Rule-6: `package` exists; adding `core craft` defines the same thing twice. | Refuted | `core craft` is the practice (a craft with a role in the system); `package` is its distributable form (the tree the runner builds and checks). The `package` row now says it names the core craft's form, so the definitions nest. Retiring `package` would touch Rules 12–21 and every message — #160's decision. |
| 6 | The core craft needs `crafts/dyad-operator` (symlink or registry row) so every craft has the same shape. | Refuted | A symlink puts one file in two zones (Rule-1 breach) and breaks `package_files()`. Uniformity is in the properties, which `dyad/` already satisfies; the root stays `dyad/` (#153 rev 2). |
| 9 | Target changes from "the repo structure" to "a craft"; the repo structure is un-owned. | Refuted | Zones were always Rule-1's; instance corpora are named by p1 (what a craft is not) and Rule-16 (the store). A craft is the more precise noun phrase for the one tree every property governs. |

Rule-6 (terms added or changed, each used-by Rule re-read): `craft` (1 4 5 11 14), `core craft`
(4 5 11 14), `Tended craft` (1 4 5 11 14), `craft corpus` (1 11) — new, owner 11, each carried
verbatim by every listed Rule. `package` (11) — nests under `core craft`; Rule-11 still reads
correctly. `Tended Rule` (4 5 8) — widened to a Tended craft's `rules/`; Rules 4 and 5 read
correctly; Rule-8 reads `workstation-corpus/rules/` today and widens in #155. `The Dyad System`
(14) — reads correctly with the new Boundaries bullet. `instance` (11) — "one system's state";
reads correctly.

Pairwise (Rule-5), Rule-11 against 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20,
21: no concern moves. Rule-11's target is wider by one kind (Tended craft) that no other Rule
owns; 11–1: the `craft` zone is Rule-1's, the craft's tree is Rule-11's (referent-pattern before
referrer, attack 4 of plan #154); 11–4: classification of a rule's home stays Rule-4's, named in
Boundaries; 11–5: the Homes paragraph scopes the sweep, Rule-11 the tree; 11–14: the system
definition is Rule-14's term; 11–12/13/17/18/19/20/21: "package" kept for the runner, registry,
projectors, ops scripts, run-books and guard placement — unchanged. Gap stated: Rule-8's "read every
file in `workstation-corpus/rules/`" and Rule-19's run-book path stay until #155 (#153 attack 12);
a Tended craft's rules under `crafts/` would not yet be read by Rule-8 — an ordered gap (#163), not
a contradiction, since no such craft exists before #155. Coherent, orthogonal.

Disposition: see ledger #154.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
a Tended craft carries guards with their tests (property 1 list); Enforcement names the second registry root. `package.py check`'s own scan (`package_files`) stays over `dyad/` and `dyad-*` workflows; the craft's own check is #156's. Pairwise: 11–21 as in `rule-21-guard-containment.md`. Coherent, orthogonal.
## Amendment — d-work #156 (2026-09-14, R-craft-2: one distribution code path, `dyad craft`, the craft guard)
p2 gains the Tended-craft install (writes `crafts/<craft>/` and its `crafts/REGISTRY.md` row only; refuses a
modified or authored tree without `--force`; refuses an unmet `requires:`); p4 the Tended craft's export name;
p5 the one code path (`dyad/scripts/distribute.py`), deterministic builds, prune, CI's export+install of a
Tended craft; Conditions gains "a craft is exported or installed"; Enforcement names the craft guard
(`dyad/guards/craft/crafts.py`). Full plan: `agent-corpus/d-work/plans/156.md` (instance).
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A8 | A craft exports host strings (a sysadmin doc names a LAN address or the Operator's home path — the `string:` markers of `package_rules.txt`). | Refuted | `export` runs the craft check first; `distribute.instance_state` applies `package_rules.txt` `string:` entries over `crafts/<craft>/`; a hit fails the check and blocks the export (`test_failing_craft_not_exported_nor_installed`). |
| A9 | Install overwrites a craft the receiving system modified locally (or authored). | Refuted | The registry `sha256` (deterministic archive hash of the tree on disk) is the proof of an unmodified tree; mismatch or no row → refused unless `--force` (`test_install_refuses_modified_tree_unless_forced`, `test_install_refuses_authored_craft`). |
| A10 | A craft depends on another (sysadmin's `ops-scripts.md` cites syseng's form); nothing declares it. | Survives, scoped | `MANIFEST.md` `requires:`: install refuses an unmet requirement, check warns (`test_requires_refused_at_install_and_met`). Not scoped: the *content* of the cited form (a Rule-20 `world` reference). The sysadmin craft declares no `requires:` today (nothing it cites is a craft yet). |
| A11 | Core install writes hooks, templates and an import line; a craft install must not — two shapes. | Refuted | One `distribute.install()` with a `hooks` parameter (`distribute.Hooks`); the core passes `CORE_HOOKS`, a craft passes `None`. Test: a craft install changes nothing outside `crafts/<craft>/` + the registry (`test_install_twice_writes_only_the_craft_and_registry`). |
| A12 | The Rule-4 heuristic false-positives on Tended text that says "the Agent reads every file here". | Confirmed | Therefore warn, not fail (`rules.py check_tended`); `README.md` exempt; tokens are data (`crafts_rules.txt`). Observed on `main`: the three sysadmin rules warn (`the Agent`, `counter-prompt`, `Y/N:`) — candidates for the sweep, not failures. |
| A13 | The registry duplicates #143 C6's `REPOSITORIES.md`. | Refuted | Different entity and zone: a repo's remote/classification (workstation) vs an installed craft's version/hash (craft zone). Cross-reference, no reuse. |
| A14 | Scratch install order: a craft installed before the core has no runner to check it; CI could pass by accident. | Refuted | `dyad-package.yml` installs the core first, then exports and installs the sysadmin craft into the scratch repo, then runs `dyad check` there. `requires: dyad-operator>=x` (checked against `dyad/VERSION` in the receiving repo) makes the order a checked precondition where a craft declares it. |
| A15 | A registry row in `agent-corpus/` forces a two-zone install. | Confirmed | Registry at `crafts/REGISTRY.md` (craft zone, outside every craft tree, refused inside one by `crafts_rules.txt` `name: REGISTRY.md`). |
| A16 | "Idempotent" is defeated by an `installed:` date, by tar mtimes, or by stale files of an older version. | Confirmed | No date column; deterministic archive (sorted, mtime 0, uid/gid 0, gzip mtime 0); `prune=True` for crafts. Tests: byte-identical builds (`test_two_builds_byte_identical_despite_mtimes`, `test_build_deterministic`), `0 changes` on the second install, `test_new_version_prunes_dropped_file`. The core `build` gains determinism in passing — the previous `cmd_build` leaked file mtimes. |
| A17 | Putting the Rule-4 and Rule-6 checks inside the craft guard makes it own three Rules' semantics (S4 breach). | Refuted | The scans live in `rules.py` (`check_tended`) and `vocabulary.py` (`check_craft`); the contract check in `dyadlib.contract_problem` (Rule-21's, shared with the runner); the craft guard composes them by `load_guard`. It owns only the craft's shape. |
| A18 | `prune` on install deletes an Operator's local file placed inside `crafts/<craft>/`. | Survives, scoped | A9 fires first: a local file changes the tree hash → refused without `--force`; with `--force` the Operator has said so (tested: `local.md` pruned only under `--force`). Stated cost: a craft tree is owned by the craft. |
| A19 | The plan's "any `<instance>` path string inside a craft fails" would fail the sysadmin craft on `main` (its rules cite `agent-corpus/d-work/plans/155.md` and `workstation-corpus/…` paths, as Rule-11 p3 permits: instance paths are referenced through the default location). | Confirmed | Scoped at execution: instance *state* is detected by file name, header and store directory (`events/`, `rows/`, `*.jsonl`, `REGISTRY.md`, the `package_rules.txt` names), never by a path mention in prose. Deviation from plan §2b, reported in the completion reply. |
| A20 | `CRAFT.md`'s third column is `rule` on `main` (#155), not the plan's `used by`. | Confirmed | `check_craft` reads `term \| definition \| rule` and requires every `rule` cell to name an existing `rules/<rule>.md` of the craft — a mechanical cross-reference the plan's free-text `used by` could not give. |

Rule-6 (terms added, each used-by Rule re-read): `export` (11), `craft registry` (11) — new, owner 11; Rule-11
p4/p5 and p2 carry them. No term changed or removed.

Pairwise (Rule-5), Rule-11 against every other Rule: 11–4: Rule-4 keeps the classification (inference); its
Boundaries name the craft guard's warning as a pointer, the scan lives in Rule-4's guard (`check_tended`),
its data beside the craft guard — no concern moves. 11–6: Rule-6 owns `check_craft` and the namespacing
rule (a craft term is referenced, never defined); Rule-11 only says the craft guard invokes it. 11–21: the
contract has one definition (`dyadlib.contract_problem`) that Rule-21 owns; the craft guard lives at
`dyad/guards/craft/` with corpus `craft`, a zone Rule-1 already declares, so Rule-21 p1's corpus list gains
`craft` (P1 of the plan, conditional edit). 11–1: no zone change; the registry is instance state inside an
existing zone. 11–8: the install refusal is Rule-8's "detect, don't dispose" applied to the repo, stated as
such, not a host action. 11–12/13/14: every new module has its test (`test_distribute`, `test_craft`,
`guards/craft/test_crafts`); stdlib only, no manifest row; nothing imported. 11–20: `crafts/REGISTRY.md` is a
path Rule-11 names, so it exists on `main` (header only, craft zone) and `references.py` resolves it. All
other pairs unchanged. Coherent, orthogonal.

Disposition: see ledger #156.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
p1's craft/instance lists, p3's mechanism (`DYAD_INSTANCE`), p4's archive shape and version seed, and the entrypoint
shape moved to `crafts/sysarch/rules/distribution.md`; the kernel — every tracked file is craft or instance, one tree one
root, the guards-layout sentence, install writes only under the root and never overwrites, the release tag — stays, and
the Boundaries name the craft rule. p5/p6 stay pending #162 (D1). Pairwise for the shrunken set (Rules 17 and 21 gone):
11–1 zones unchanged; 11–2 release event unchanged; 11–3 no lifecycle change; 11–4 Tended path already names a craft's
`rules/`; 11–5 the set text is Rule-5's; 11–6 `guard` and `corpus` re-owned by Rule-11 (their definitions unchanged);
11–12 Rule-12 keeps "carries a check", Rule-11 keeps the layout sentence; 11–14 the manifest's *form* is the craft's, the
running manifest stays core; 11–16 the store pattern is the craft's, the canonical path Rule-16's; 11–20 every craft path
a Rule names exists (kind 11 green). Coherent, orthogonal. Disposition: see ledger #160.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
p5's determinism and idempotence clauses moved to `crafts/syseng/rules/idempotence.md` (p1) and `determinism.md` (p4);
p6's discipline (what counts as generated, why never committed) to `determinism.md` (p1). One-line stubs keep the data
(`package_rules.txt`) and the checks (`check_generated`, `dyad build|install`, `dyad-package.yml`) here (plan #162
attack 10: ownership of code stays where the code runs). Enforcement names the runner's invariant pass, run before any
check (`crafts/syseng/rules/invariants.md`; the term is Rule-12's). `generated file` leaves the Agent vocabulary for the
craft's `CRAFT.md`. Pairwise: 11–12 Rule-12 owns `invariant`, Rule-11 runs the pass; 11–14 unchanged; 11–1 the `craft`
zone holds the new craft; no other pair changes. Coherent, orthogonal. Disposition: see ledger #162.

## Amendment — d-work #180 (2026-09-14, craft-declared instance seeds, warn-only)
**Claim:** a Tended craft's install should tell the Operator/Agent when one of its templates has
not been copied to the instance path it corresponds to (G7, plan #176's verification).
| # | attack | result | survivor |
|---|--------|--------|----------|
| A21 | This reopens A11 (#156: "Core install writes hooks, templates and an import line; a craft install must not — two shapes") — the exact question #154/#156 already settled as "host-side hooks are the core craft's only". | Refuted | Nothing is written outside `crafts/<craft>/` by this change; `distribute.py` and `craft.py`'s `hooks=None` are untouched. `seeds:` is read-only metadata; `seed_status()` only calls `Path.exists()` and prints. `test_install_twice_writes_only_the_craft_and_registry`'s `# A11: nothing else` assertion is extended (a fixture with a declared seed) and still holds. |
| A22 | Property 2 already names `requires:` without a general "MANIFEST.md may carry other declarative fields" clause; is `seeds:` in scope for a fresh sentence or is it scope creep on a row ranked lowest-urgency? | Survives, scoped | `requires:` earned a sentence precisely because it is real, checked package behavior (`unmet`, refused at install); `seeds:` is the same shape (a new MANIFEST.md key, parsed and checked the same way) and the same size (one clause) — consistent with, not larger than, the existing precedent. |
| A23 | The destination-zone check (a seed's zone must be one the craft's own guards claim as `CORPUS`) reaches into Rule-1's zone table from a Rule-11-owned guard. | Refuted | `crafts.py` already reaches into `containment.ZONES` for the *existing* guard-contract check (`zones = {z for z, _ in dyadlib.load_guard("infra", "containment", pkg).ZONES}`, present since #156); this reuses the identical, already-falsified pattern for one more purpose. Rule-11's Boundaries already name Rule-1 as a dependency, one-way (11–1 pairwise, #154 amendment). |

Pairwise (Rule-5): Rule-11 gains one sentence in property 2, documenting a second `MANIFEST.md`
key the same way it already documents `requires:`; no other Rule's concern moves — Rule-8's
change-log row, Rule-9's falsification (this record), Rule-12's per-file test mapping (`crafts.py`
keeps its own `dyad/tests/guards/craft/test_crafts.py`) all read as before. Coherent and orthogonal
with every other Rule as before (compact form, per the #152 amendment above: a one-clause addition,
not a reframe).

## Amendment — d-work #21 (2026-09-16, ledger #196: bundle release, core tag reprefixed)
**Claim (Operator, #196):** the unprefixed `vX.Y.Z` tag should name the whole distribution this
repo authors (core + every Tended craft, pinned together) as one GitHub-convention release; anyone
wanting only some components pins them individually by their own crafts' tags.

| # | attack | result | survivor |
|---|--------|--------|----------|
| A24 | Rule-4's Target must be one noun phrase naming a single kind of thing; Rule-11's stays "a craft" while property 7 governs a manifest that is explicitly *not* a craft (vocabulary: a craft is "a contained tree with one root… VERSION…"; `BUNDLE.md` is one file at the repo root). | Survives, scoped | Not refuted — a real, named tension. Kept under "a craft" rather than widened or split into a new Rule because every property here already reads as "how a craft is released," and the bundle is that same release event applied to the set of crafts in the tree, not a new governed *kind*; it introduces no new store with its own lifecycle (Rule-3), zone (Rule-1 already classifies `BUNDLE.md` as infra) or ratification form (still `Y/N: release <tag>?`, Rule-11's own). If a second bundle-shaped concern arrives later, this pairing should be revisited, not silently re-stretched again. |
| A25 | Reprefixing the core's tag (`vX.Y.Z` → `dyad-operator-vX.Y.Z`) could be read as *moving* `v0.3.1`/`v0.3.2`/`v0.4.0` under the new scheme. | Refuted | Property 4's text is prospective (what a release *is* from here); Provenance states the three existing tags predate this and are never retagged — tags do not move, stated as existing conduct (property 4's own sentence on cadence, unchanged). |
| A26 | `BUNDLE.sha256`, written at bundle-build time, could be tracked by accident and then drift from the archives it describes (Rule-11 property 6). | Confirmed, as a risk if untreated | Added to `package_rules.txt`'s `generated:` list (`*.tar.gz`, `BUNDLE.sha256`) in the same PR; `package.py check` refuses either tracked, same as any other generated path. |
| A27 | A craft added to `crafts/` without a bundle row (or a bundle row for a craft no longer in the tree) should be visible, not silently ignored. | Refuted (already handled) | `infra/bundle`'s check is bidirectional by construction (property 7's design): every craft needs a row, every row names a craft — the guard `check_bundle` in `dyad/guards/infra/bundle.py` fails both directions. |
| A28 | The bundle guard's absence-handling (no `BUNDLE.md` → skip, never fail) could hide a bundle that *should* exist going stale after this repo starts using one. | Survives, scoped | Same discipline as every other absent-store guard here (property 4's pattern, Rule-20 property 2): a core-only or partial install has nothing to check against; once `BUNDLE.md` exists in *this* authoring repo it is never absent, so the risk is scoped to receiving installs, which never carry the authoring repo's release mechanics at all. |

Pairwise (Rule-5): 11–1 `BUNDLE.md` added to `containment.ZONES` as `infra` (one more fixed-name
row, same shape as `README.md`/`CLAUDE.md`); 11–20 one new reference kind, `bundle.component->craft`,
delegated to `guard:infra/bundle.py` (owned there, not re-implemented in `references.py`, per
Rule-20's own Boundaries); 11–6 one vocabulary term (`bundle`), `release`'s row reworded, both cite
Rule-11; 11–4 the Target tension is A24, named and scoped, not silently absorbed. No other Rule's
concern moves — Rule-2's release ratification form gains a third tag shape but no new event kind;
Rule-3, 7, 8, 12–19 read as before. Coherent, orthogonal with the one named exception (A24).
Disposition: see ledger #196.

Disposition: see ledger #180.

## Amendment — d-work #91 (2026-09-18, property 4's converse: the drift guard)
**Claim:** property 4 ("a release is a tag equal to `<name>-v` + `VERSION`") keeps a released
version naming one tree. Falsified four times in two days: sysarch-v0.1.4's archive predated #50
(#61, surfacer's report); `dyad/` and `crafts/sysarch/` diverged from their tags by two and three
d-works (#67); `crafts/syseng/` by #15 (#71, workstation's report, after #67's by-hand sweep checked
only the two crafts that had been named); `dyad/` again by #68, the session's own change an hour
after #67 (#90, caught only by comparing a rebuilt sha to a published asset). Nothing checked the
converse — that the tree under a craft's root at HEAD equals its own tag's while `VERSION` is
unchanged.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The craft guard (`craft/crafts`) owns a craft's shape; put it there. | Refuted | It runs per craft with no notion of a release; the bundle guard already owns "row version == live VERSION" and knows every component and the tag-name rule (`tag_name`, invariant `tag-name-is-prefix-v-version`). One module, discovered like every guard — no hand-listing. |
| 2 | Local tags can be stale, so the check lies. | Survives, scoped | A tag never moves (this record, #196), so a fetched tag is *the* tag; the only staleness is a tag not yet fetched, which skips with one `warning: skip … tags not fetched` line — the kernel-only path never fetches (Rule-14 p3). CI's full-depth checkout has every tag and corroborates. |
| 3 | Too strict: a typo fix in a craft's README forces a version bump. | Survives, stated | That *is* the property: a released version names a tree, a different tree is a different version. Only the first content commit after a release needs the bump; once bumped the new tag is absent and later commits skip until release. |
| 4 | Check the working tree, so `dyad check` catches it before the commit. | Refuted | HEAD is what a push carries and what `pre-push` judges; the working tree's state is Rule-14's `dirty=` flag in the evidence block. |
| 5 | The guard refuses its own introducing commit (bundle.py changed under an unbumped core). | Confirmed, by design | Demonstrated in #91's own execution: `FAIL 'dyad-operator': dyad/ differs from tag dyad-operator-v0.6.2 (2 file(s))` on the guard's first commit; the `VERSION` bump to 0.7.0 in the same PR makes the tag absent and the push pass. Every craft-content PR will meet the same gate. |

Mechanism: `bundle.check_drift(root, pkg)` — per live component, `git rev-parse --verify
<tag>^{commit}` then `git diff --name-only <tag> HEAD -- <root>`; run from `check_package` after the
row check, so it is on the kernel-only path and in `check --guards`. Tests: `DriftTests` in
`dyad/tests/guards/infra/test_bundle.py` (unchanged tree silent; a changed file fails naming the
count; the core is a component; a bumped `VERSION` skips; no tags skips; no commit skips; the CLI
prints `warn` for a skip and exits 0). Pairwise (Rule-5): 11–14 the guard shells to git only,
the kernel; 11–20 the tag is not a Rule-20 reference (a World object resolved by git, not by the
register). Others unchanged. Coherent, orthogonal. Disposition: see ledger #91.

## Amendment — d-work #100 (2026-09-20, property 2's craft-contribution sentence)
**Claim:** property 2's no-clash guarantee (an install writes only its own root) is enough; nothing
about property 2 need say how a craft *contributes* to a table the core owns. Falsified by
`agent-corpus/falsification/extensibility.md` (d-work #101): eight of ten craft-varying-data tables
this repo owns have no craft-declared discovery path, and every one found in four days of
downstream use (#51, #22/#196, #99/D3, D4, D2, D1, #46 vs #98) was answered by editing this repo's
own tracked content instead. Disposed by the Operator's `Y` on #101's one-sentence proposal.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | This belongs in property 5 (the one code path) or property 1 (craft/instance split), not property 2. | Refuted | Property 2 already owns "what an install writes and does not overwrite" — the contribution sentence is the same shape one step further: what a craft may *add* to a table it does not own outright. Properties 5 and 1 are unaffected. |
| 2 | The sentence is unfalsifiable prose with no guard behind it. | Refuted, by the plan it authorizes | d-work #100 (same reply this amendment lands in) builds three concrete instances — zone, World-dependency, and reference contribution — each discovered and merged, none hand-listing a craft. |
| 3 | This reopens every core-owned table to craft data, including ones #101 found correctly closed. | Refuted | #101's own record scopes the sentence to categories (a)/(b) of its catalogue (8 of 10 rows) and names `STATES`/Agent-process Rules as excluded; #100's plan does not touch either. |

Pairwise (Rule-5): 11–1 (craft/instance) unaffected — a contribution file is still the contributing
craft's own tracked content, never instance; 11–5 (one code path) unaffected — contribution is
discovery, the same primitive `dyadlib.craft_dirs` every existing mechanism already uses. Others
unchanged. Coherent, orthogonal. Disposition: see ledger #100.

## Amendment — d-work #106 (2026-09-21, release-batch ratification form)
**Claim:** release's one-per-question rule and destructive's shared one root justification
(irreversibility, `dyad/falsification/rules/rules-2-3-batch-disposition.md` #17 attack 4). The full
attack table falsifying this claim, and the survivor it yields, live in that record's own
`Amendment — d-work #106` (not duplicated here, the shared mechanism's own home). Summary: release
was never a Rule-8 class to begin with (Rule-8's Target is a host action; release is this Rule's
own domain), and Rule-11's existing "publishes to the world" reason for one-per-question is
independent of destructiveness, so it survives that record's attacks untouched — but a narrower
batch form is now warranted, gated exactly the way Rule-3's own Done-batch already gates its items
(named individually, unmerged, in the same reply, before the question).

Ratification events gains a second form: several tags whose content one d-work's own Done-`Y`
already verified, each already named individually beforehand, never mixed with a different
d-work's tag, never folded into Rule-3's plan or Done batch.

Pairwise (Rule-5): 11–3 Rule-3's Boundaries and Batch-disposition sections cross-reference this
form by name, own none of its mechanics (S4); 11–8 unaffected — destructive's own rule and reason
are untouched by this amendment; 11–2 unaffected — Rule-2's existing batch-counter-prompt Binding
sentence already covers "names several d-works, PRs, or both," binding a release-batch `Y` the
same way. Others unchanged. Coherent, orthogonal. Disposition: see ledger #106.

## Amendment — d-work #114 (2026-09-22, the bundled craft)

**Claim:** the core release should carry the `sysadmin` craft.

| # | attack | result |
|---|--------|--------|
| R1 | The bundle (property 7, tag `vX.Y.Z`) already releases the core and every Tended craft together. | **refuted as sufficient** — the bundle is a manifest over separate archives; the receiver installs each craft in its own step. A system that pins the *core* tag gets no `sysadmin` at all. Co-release is not core-inclusion. |
| R2 | Preference, not defect: the core stands alone. | **refuted, measured** — four core Agent Rules (5, 8, 18, 19) cite `crafts/sysadmin/` by path, nine distinct paths, and a core-only install of `main` at `25a1834` was red (`FAIL [Rule-12] tests failed (dyad/tests)`, 1 failure + 1 error; backlog #10 names that class). The dependency is real already; only the shipping was missing. |
| R3 | Then merge the craft into `dyad/`. | **refuted** — it reverses the extraction that created the craft and collapses Rule-4's Agent Rule / Tended Rule split. The survivor ships the tree without absorbing it: a bundled craft keeps its root, its zone, its `VERSION` and its own tag. |
| R4 | Forcing a host craft on every system breaks craft optionality. | **survives — conceded** — a system with no host carries a tree it never uses. The cost is disk, not doctrine: the craft stays separately versioned and separately removable, and removing it removes its own claim to being bundled. |
| R5 | Fix the coupling instead — stop core Rules citing craft paths. | **survives as the honest alternative**, and is recorded as such rather than dismissed. It preserves optionality and is arguably more correct, but it is a large Rule-text change across four Agent Rules. The Operator chose this branch; that one stays available. |
| R6 | Property 2 forbids a core install writing another craft's root. | **confirmed — which is why this is a Rule amendment and not a build change.** A `dyad install` that quietly wrote `crafts/sysadmin/` without amending p2 would be a Rule breach dressed as a feature. |
| R7 | Bundling one craft reddens the siblings' citations, because `references.py`'s `crafts_absent` is one flag for the whole tree. | **refuted by reading the code** — `craft_state` resolves per craft (#167): an absent sibling with no registry is `skip`, with a registry that omits it `warn`; `FAIL` is reserved for installed-then-deleted. `crafts/sysarch/rules/distribution.md`'s paragraph claiming a one-craft subset leaves `check --guards` red predates #167 and is stale. |
| R8 | The core should keep the list of which crafts it bundles — it is the core's release. | **refuted** — property 2's own craft-contribution sentence (#100, per `agent-corpus/falsification/extensibility.md`) already settles this shape for craft-varying data: discovered, reported under the contributing craft's name, gone when the craft is. A core-kept list would need editing every time a craft arrived or left, and would outlive the craft it named. |
| R9 | A craft declaring itself bundled lets a craft decide what the core ships. | **survives, scoped** — true, and bounded by the same limit as every other contribution: the declaration only has effect for a craft that is *in the tree*, which is already the authoring repo's decision. What it removes is a second place to keep the same fact in sync. |

**Survivor.** Property 2 gains the bundled craft: a Tended craft the core release carries, declared
by the craft itself (`BUNDLED_WITH_CORE` in one of its own guard modules, discovered like a guard),
Tended in every other respect, bundled only because a core Rule cites it by path. `release_roots()`
is used by `build` and `install` alone — never by `check`, whose craft/instance scan still judges
the core craft by itself, so bundling changes what ships and not what anything *is*.

Pairwise (Rule-5): 11–1 a bundled craft's tree stays zone `craft`, so a change to it is still a
craft-zone PR — the bundling is the core's *release* reaching it, never the zone moving; 11–4 the
craft keeps its own `VERSION` and its own `<craft>-vX.Y.Z` tag, so the drift guard is unaffected;
11–12 the mechanism carries its own tests (`BundledCraftTests`); 11–20 no new reference kind — the
declaration is a module constant, not a citation. Others unchanged. Coherent, orthogonal.
Disposition: see ledger #114.

## Amendment — d-work #156 (2026-09-24, property 7's unreleased-craft sentence)
Not the 2026-09-14 amendment of the same number above (R-craft-2): the ledger's ids restarted, and
this is the later row #156 (the countersign craft, plan Revision 2, incident I2).

**Claim:** property 7's "one row per craft in the tree", enforced in both directions (A27 above),
admits an order in which a new craft can be added. Falsified in #156's own execution: with the craft
first, `'countersign' is in the tree but has no bundle row`; with the row first, `'countersign': not a
craft in this tree`. Rule-1 puts `crafts/` (zone `craft`) and `BUNDLE.md` (zone `infra`) in different
PRs, and the pre-push hook runs the guard, so neither branch could be pushed without bypassing a hook
that runs and fails, which Rule-1 forbids. Never hit before because every existing craft predates
`BUNDLE.md`. A Rule-5 coherence gap between Rule-1 and property 7.

| # | attack | result | survivor |
|---|--------|--------|----------|
| A1 | Softening the missing-row check weakens the bundle's completeness guarantee: `BUNDLE.md` no longer names every craft in the tree. | Survives, scoped | Only an *unreleased* craft may be absent, one with no `<craft>-v*` tag of its own. It has no archive, so there is nothing for the bundle to pin or publish (the bundle is built by sequencing each row's release, property 7). A released craft without a row still fails, and so does a row naming a craft not in the tree. A27's two-way check stands for every craft that has a release. |
| A2 | A craft could stay unreleased forever and never be bundled. | Survives, as a risk | It is visible: every `dyad check` and every push prints `warn [bundle] '<craft>' is in the tree but unreleased … not yet bundled`. Releasing is the Operator's call (Ratification events), and the first release's own PR must add the row, because the tag makes the guard strict for that craft. |
| A3 | Rule-1 coherence: is there now a legal order? | Refuted as a gap (coherence restored) | Yes, and it is the one Rule-1 names: change the referent before the referrer. The craft lands first in a craft-zone PR (it warns). Its first release adds the row in an infra-zone PR (strict from then on). Each PR is one zone, and every push passes. |
| A4 | Client impact: does a receiving system see a change? | Refuted | A core-only install carries no `BUNDLE.md`, so the guard skips (property 7; this record, A28). In the authoring repo, only a missing row for an unreleased craft changes, from FAIL to warning. |
| A5 | Local tags can be missing (not fetched), so a released craft reads as unreleased and its missing row only warns. | Survives, scoped | Same staleness as the drift guard (#91 attack 2). The kernel-only path never fetches, and a clone without tags softens only this one case to a warning. It never hides a row naming a craft not in the tree, and never hides a version mismatch. CI's full-depth checkout has every tag and corroborates strictly. |
| A6 | The bundle's own unprefixed `vX.Y.Z` tag, or another craft's tag, could count as a craft's release. | Refuted | The pattern is `<craft>-v*` (property 4's prefix, `bundle.tag_pattern`). The core's is `dyad-operator-v*`, and `v0.10.0` matches no craft. The test `test_released_components_reads_local_tags` covers both. |

**Survivor.** Property 7 gains one sentence: an unreleased craft (no `<craft>-vMAJOR.MINOR.PATCH` tag
of its own) may be absent from the bundle until its first release, whose release adds its row; a
released craft without a row fails. Mechanism: `bundle.released_components(root, components)` reads
the local tags (`git tag -l '<craft>-v*'`, the kernel's Git only). `bundle.check(version, rows, live,
released)` stays pure: when `released` is omitted every component counts as released (strict). Tests:
`UnreleasedCraftTests` in `dyad/tests/guards/infra/test_bundle.py`.

Pairwise (Rule-5): 11–1 coherent again: the referent-before-referrer order now exists for a new
craft (A3), and neither Rule's zone table changes. 11–2 unaffected: a release is still ratified by
`Y/N: release <tag>?`, and the row follows the release. 11–3 unaffected: no new state or
counter-prompt. 11–4 the block is unchanged; one sentence in a property. 11–5 this record carries
the statement. 11–6 no term added or changed, see below. 11–7 unaffected. 11–8 unaffected: `git tag
-l` is read-only. 11–9 falsified here. 11–10 unaffected. 11–12 the mechanism carries its tests.
11–13 no new import. 11–14 shells to Git only, the kernel; the kernel-only path is unchanged.
11–15, 11–16, 11–18, 11–19 unaffected. 11–20 no new reference kind: a tag is a World object that git
resolves, as in #91. Coherent, orthogonal.

Rule-6: no term added or changed. One finding is named rather than absorbed. The vocabulary's
`bundle` row reads "the core craft plus every Tended craft in the tree", and property 7's opening
sentence still reads the same way. Both describe the bundle as released, and the new sentence scopes
the interim. If the Operator wants the row to say "every released craft", that is a vocabulary edit
for a later agent-zone PR; this PR does not make it.

Disposition: disposed by the Done-`Y` of d-work #156; see ledger #156.
