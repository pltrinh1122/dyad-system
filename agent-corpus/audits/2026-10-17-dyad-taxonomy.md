# The `dyad/` taxonomy, reviewed whole — best fit for `ledgerd`, every other refactoring costed, and the carry-back for #336 (2026-10-17)

*d-work #340, seat `ds-cabinet-cloud-7`, relayed from #339 (`ds-cabinet-cloud-6`). Tree `1eb21a3` on `main`
(the core craft `dyad-operator` 0.11.0; syseng 0.4.0, sysarch 0.3.0, sysadmin 0.3.0, countersign 0.3.0,
disclosure 0.1.0). Detects, classifies and costs; disposes nothing. Every proposal is Rule-10 form and is
executed by no one here. Falsification: `../falsification/2026-10-17-dyad-taxonomy.md`.*

**Disposition:** disposed by the Done-`Y` of d-work #340 (Rule-2; see ledger #340).

**How to read this.** §0 is the one-page answer. §1 says what was read. §2 classifies every tracked file under
`dyad/` (128 files, 21 kinds) against the Operator's partition of a craft into **knowledge base**, **guards
(rules)** and **tools** (#336 revision 13, attack K2). §3 names every mechanism that stands on a path pattern
(23, not the eight #336 revision 14 Y2 listed) and what moving each pattern costs. §4 costs four shapes for
`ledgerd`. §5 lists every other refactoring found, each as one path, its strongest counter and a
reconciliation. §6 says what was not observed. §7, the last section, is the carry-back: directions #336's
revision 16 can be drafted from. Every count is a `git grep` or a script the record names (§1), re-runnable on
`1eb21a3`.

## 0. The one-page answer

1. **`server` is already a kind in the architecture, and it is a *peer* of `scripts/`, not its sub-type.** The
   naming table's one row for a craft tree (`crafts/syseng/rules/naming.md`, row 3; `naming_rules.txt` `kind:
   crafts/<craft>/`) enumerates `scripts/`, `projectors/` and `server/` side by side as allowed children. No
   `tools/` level exists anywhere in the tree, the table, the guards or the vocabulary. The Operator's "tools"
   is therefore a **partition** — the class {`bin/`, `hooks/`, `scripts/`, `projectors/`, `server/`} — and
   the question is whether that partition should become a *directory*. Today it is neither a directory nor a
   documented classification: the vocabulary's `craft` row lists "rules, vocabulary, templates, guard data,
   records, docs" and names no tools and no tests (K2's finding, confirmed in §2).
2. **The core tree is open; a Tended craft's is closed.** The table enumerates a craft's allowed children and
   has no row for `dyad/` itself (§3 M1). Nothing selects `dyad/server/…` or `dyad/tools/…`, so either passes
   the naming guard today with zero rows, and the test mapping (§3 M4) sees only what it globs. Adding a kind
   to the core is not a checked decision anywhere — the gap the Operator's question exposes (§5 P1).
3. **Renaming `dyad/scripts/` is the most expensive single edit in the tree.** The string is hardcoded in
   **37 non-test modules across six zones** — every core guard, three core scripts and every Tended craft's guards,
   projectors and scripts insert it on `sys.path` by literal (§3 M16) — plus 46 test files, both hooks and the entrypoint,
   ten occurrences in Rule text that the reference guard enforces, twelve in workflows and one in the
   preferences table. Under Rule-1 the core and the crafts cannot change in one PR, so the rename needs a
   compatibility window or a red interval on `main` (§4 A). No revision of #336 priced this.
4. **The precondition that makes the rename cheap exists and is worth doing on its own:** read the core
   library's location in one place (§5 P2). After it, the rename is one agent-zone PR plus prose.
5. **Four of the twenty-three mechanisms are hand-lists that a new code directory silently escapes:** the test
   mapping's flat globs, the runner's invariant pass (`("runbook", "craft", "distribute")`), the manifest
   guard's import-scan directories, and the runner's test roots (§3 M4, M6, M15, M9). A module under
   `dyad/server/ledgerd/` or `dyad/tools/ledgerd/` would today need **no test, appear in no `[invariant]`
   line, and have its third-party imports unscanned** — the last of these is new against revision 14's Y4 and
   is the one that lets an undeclared `fastapi` import pass the manifest guard (§5 P6).
6. **Carry-back (§7):** place `ledgerd` at **`dyad/server/ledgerd/`** (shape B), with the syseng change written
   as a **generic component clause** — `dyad/<kind>/<component>/` with its own `tests/` — rather than a
   `server`-specific one, so the same clause serves `tools/<x>/` if the Operator later adopts the rename;
   three PRs (syseng craft, agent, workstation) in that order, one Done batch; the manifest scan and the
   invariant pass extended in the agent PR. The rename to `tools/` is a separate program, gated on P2.

## 1. Inputs and reach

| source | what was read | how a reader re-derives it |
|---|---|---|
| the tree at `1eb21a3` | every tracked file under `dyad/` (`git ls-files dyad`: 128), every Tended craft's tree, `BUNDLE.md`, `crafts/REGISTRY.md`, `.github/workflows/` | `git ls-files dyad \| wc -l` |
| the Operator's partition | plan #336 revision 13 attack K2 — knowledge base (vocabulary, docs, records, templates, play-books), guards (the mechanical checks beside the rules they enforce), tools (scripts, projectors, servers) — and revisions 14 (Y2, Y4, Y5) and 15 (S1–S5) | `agent-corpus/d-work/plans/336.md` |
| the naming table | `crafts/syseng/rules/naming.md`, `crafts/syseng/guards/naming_rules.txt` (24 `kind:`, 4 `mode:`, 5 `symbol:`, 1 `env:`, 3 `allow:` lines), `crafts/syseng/docs/naming.md` | `dyad check --list`; `grep -c '^kind:' crafts/syseng/guards/naming_rules.txt` |
| the architecture rules | `crafts/sysarch/rules/distribution.md`, `guards.md`, `projection.md`, `stores.md`, `references.md` (Leaves) | — |
| the test mapping and invariants | `crafts/syseng/guards/tests.py` (`modules`, `test_for`, `CRAFT_CODE`), `invariants.py` (`python_files`, (i)–(v)), `invariants_rules.txt`, `crafts/syseng/rules/verifiable-code.md` p4, `invariants.md` | — |
| the runner and library | `dyad/scripts/package.py` (`CORE_ROOTS`, `CORE_HOOKS`, `TEMPLATES`, `test_suites`, `installed_roots`, `registry`, `invariant_modules`, `projectors`), `dyadlib.py` (`PKG`, `GUARDS`, `guard_files`, `craft_glob`, `craft_dirs`, `projector_files`, `runner_module`, `package_rules`), `distribute.py` (`files`, `instance_state`, `Hooks.template_dir`), `craft.py` (`SCAFFOLD`), `runbook.py` (`CORE_RUNBOOKS`, `all_runbooks`) | the invariant pass's labels: `dyad/bin/dyad-python -c 'import sys; sys.path.insert(0,"dyad/scripts"); import package; print([l for l,_,_ in package.invariant_modules()])'` |
| the guards that read core paths | `dyad/guards/agent/references.py` (`REFERENCES`, `package_paths`), `frame.py`, `rules.py`, `records.py`, `vocabulary.py`, `infra/manifest.py` (`python_imports` dirs, the invocation scan's file list), `infra/bundle.py`, `infra/containment.py` (`ZONES`), `craft/crafts.py` (`DIRS`, the floor script), `crafts/sysadmin/guards/runbooks.py` (`SERVER_GLOBS`) | — |
| hooks, entrypoint, workflows, tests that pin paths | `dyad/hooks/pre-commit`, `pre-push`, `dyad/bin/dyad`, `dyad-python`; `.github/workflows/dyad-*.yml` (6); `dyad/tests/test_entrypoint.py`, `test_playbooks.py` | `git grep -n 'dyad/scripts\|dyad/guards\|dyad/bin' .github` |
| the `dyad/scripts` literal | every tracked occurrence, by location | `for p in …; do git grep -o dyad/scripts -- $p \| wc -l; done` (the counts of §3 M16 and §4 A) |
| inputs the brief names | `agent-corpus/audits/2026-10-17-token-efficiency.md` (#333) §§3–5; `2026-10-15-messaging-architecture.md` (#253 R4, R29); `agent-corpus/falsification/seat-vs-harness-session.md` (#295) | — |
| what the plan said and the tree showed | plan #340 said 134 files and 31 modules; `git ls-files dyad` says 128, and the literal count by module class is 37 (M16) — both plan numbers came from a first pass and are corrected here, not carried | `git ls-files dyad \| wc -l`; the M16 command |

Not an input: the content of `ledgerd` (revisions 4–9 of plan #336), which the Operator settled; `#336`'s own
host actions; any running system.

## 2. The tree classified

### 2.1 The kinds

Twenty-one kinds under the core root, grouped by the Operator's partition. "K2 silent" marks a kind the
three-way partition does not name; the audit classes it and says so rather than forcing it.

| partition | kind | files | path shape | has a `kind:`/`mode:` row (M1/M2)? |
|---|---|---:|---|---|
| **knowledge base** | frame | 1 | `CLAUDE.md` | no |
| | map | 1 | `README.md` | no |
| | vocabulary | 1 | `vocabulary/VOCABULARY.md` | no |
| | Rule records | 20 | `falsification/rules/rule-<n>-<slug>.md` (+ `rules-…`, `rule-sets.md`) | yes (+ 1 allow) |
| | play-books | 7 | `playbooks/<name>.md` | **no** |
| | core run-books | 7 | `runbooks/<name>.md` | **no** |
| | instance seeds | 4 | `templates/<Name>` | yes |
| | manifest | 1 | `infrastructure/INFRASTRUCTURE.md` | no |
| **guards (rules)** | Agent Rules | 19 | `rules/RULE-<n>-<slug>.md` | yes |
| | guards | 16 | `guards/<corpus>/<entity>.py` | yes |
| | guard data | 2 | `guards/<corpus>/<entity>_rules.txt` | yes |
| | runner data | 1 | `scripts/package_rules.txt` — the Rule-11 check's data, beside its reader (the runner), so under a *tools* directory | **no** (`dyad/tests/*.py` and `dyad/guards/*/*.txt` have rows; `dyad/scripts/*` has none) |
| **tools** | entrypoint | 2 | `bin/dyad`, `bin/dyad-python` | mode only |
| | hooks | 2 | `hooks/pre-commit`, `hooks/pre-push` | mode only |
| | runner | 1 | `scripts/package.py` | **no kind row**; `symbol:` row |
| | library | 1 | `scripts/dyadlib.py` | **no kind row**; `symbol:` row |
| | scripts | 7 | `scripts/<name>.py` | **no** |
| **tests** (K2 silent) | script tests | 13 | `tests/test_<name>.py` | yes |
| | guard tests | 16 | `tests/guards/<corpus>/test_<entity>.py` | yes |
| | package markers | 5 | `tests/guards/**/__init__.py` | yes (the regex admits `__init__`) |
| **metadata** (K2 silent) | version | 1 | `VERSION` | no (Rule-11's check and the bundle guard) |

Reading the table against K2:
- **The partition fits every kind but two.** Tests are checks *of the tools and guards* (Rule-12 property 1:
  "code entering the package carries its mechanical check"), so they are guards in function but of code, not
  of corpus entities; `VERSION` is the craft's identity, none of the three. Both are stated, not forced.
- **Where the Rules sit is a reading.** The Operator wrote "guards (rules)". This audit reads it as *the
  normative text and the checks that enforce it are one partition*, and classes `rules/` and
  `falsification/rules/`… differently: the Rule is the thing enforced, the record is knowledge about it.
  The other reading — Rules are knowledge base — changes one row of the table and nothing in §3–§7.
- **`scripts/` holds four things under one name**: the runner, the shared library, five CLI modules and
  one data file. K2 calls all four code "tools"; the data file is guards data that lives beside its reader.
  `package.py` is also the one module the test mapping exempts (`tests.py EXEMPT`).
- **Two knowledge-base kinds have no naming row at all** (play-books, run-books) and the whole tools
  partition has no `kind:` row (only `mode:` rows for `bin/` and `hooks/`, and `symbol:` rows for two
  modules). Compare a Tended craft, whose every child is enumerated by one regex (M10). See §5 P1.
- **The core and the crafts already differ in kinds.** Core-only: `bin/`, `hooks/`, `playbooks/`,
  `runbooks/`, `infrastructure/`, `CLAUDE.md`. Craft-only: `MANIFEST.md`, `docs/`, `projectors/`,
  `server/`. Shared: `VERSION`, `README.md`, `rules/`, `vocabulary/`, `templates/`, `guards/`, `tests/`,
  `falsification/`, `scripts/`. The core's `README.md` is its map; a craft's `docs/` is its procedures; the
  core's procedures are `playbooks/`. The asymmetry is history, not design: every craft-only kind arrived
  with an extraction (#155, #160, #181) and every core-only kind with a Rule (#165, #213, #223).

### 2.2 Every file

One row per tracked file under `dyad/` at `1eb21a3`. Columns: the kind (§2.1), the K2 partition, the owning
Rule or craft rule, and the mechanisms of §3 that select the file by its path (`M<n>`; a mechanism in
parentheses is one the file is exempt from or absent from). Generated by a script over `git ls-files dyad`
and a kind map; the map is the audit's claim, the listing is git's.

| path | kind | partition (K2) | owner | selecting mechanisms |
|---|---|---|---|---|
| `dyad/CLAUDE.md` | frame | knowledge base (frame) | frame | M13 M12 M11(import line) |
| `dyad/README.md` | map | knowledge base (map) | frame / Rule-11 | none (prose; M11 ships it) |
| `dyad/VERSION` | version | metadata (craft identity) | Rule-11 p4 | M14(check_rule_11, bundle.py) M11 |
| `dyad/bin/dyad` | entrypoint | tools (host-executed) | Rule-11 p2 | M2 M17 M22 M11 M12 |
| `dyad/bin/dyad-python` | entrypoint | tools (host-executed) | Rule-11 p2 | M2 M17 M22 M11 M12 |
| `dyad/falsification/rules/rule-1-containment.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-11-distribution-structure.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-12-verifiable-code.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-13-reuse-over-inference.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-14-system-infrastructure.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-15-d-work-phases.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-16-concurrent-sessions.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-18-ops-scripts.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-19-server-instances.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-2-no-self-ratify.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-20-referential-integrity.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-3-d-work.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-4-integrity.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-5-coherence.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-6-vocabulary.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-7-provenance.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-8-host-mutation.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rule-sets.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rules-2-3-batch-disposition.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/falsification/rules/rules-9-10-promotion.md` | Rule record | knowledge base (record) | Rule-9 (travels with its Rule, A6) | M1 M14(records.py; rule.provenance->record) M11 |
| `dyad/guards/agent/frame.py` | guard | guards | frame (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/plans.py` | guard | guards | Rule-15 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/provenance.py` | guard | guards | Rule-7 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/prs.py` | guard | guards | Rule-3 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/records.py` | guard | guards | Rule-9 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/references.py` | guard | guards | Rule-20 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/rows.py` | guard | guards | Rule-3/16 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 M18 |
| `dyad/guards/agent/rules.py` | guard | guards | Rule-4 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 M18 |
| `dyad/guards/agent/sessions.py` | guard | guards | Rule-16 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/traces.py` | guard | guards | Rule-3 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/agent/vocabulary.py` | guard | guards | Rule-6 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 M18 |
| `dyad/guards/craft/crafts.py` | guard | guards | Rule-11 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/craft/crafts_rules.txt` | guard data | guards (data beside its guard) | the guard's Rule | M1(<entity>_rules.txt) M11 M12 |
| `dyad/guards/infra/bundle.py` | guard | guards | Rule-11 p7 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/infra/containment.py` | guard | guards | Rule-1 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 M17 M18 |
| `dyad/guards/infra/manifest.py` | guard | guards | Rule-14 (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/guards/infra/manifest_rules.txt` | guard data | guards (data beside its guard) | the guard's Rule | M1(<entity>_rules.txt) M11 M12 |
| `dyad/guards/preferences/preferences.py` | guard | guards | frame (placed per Rule-11 p1, sysarch guards.md) | M1 M3 M4 M5 M6 M7 M15 M16 M11 M12 |
| `dyad/hooks/pre-commit` | hook | tools (git-executed) | Rule-1 / Rule-14 p3 | M2 M17 M15 M11 M12 |
| `dyad/hooks/pre-push` | hook | tools (git-executed) | Rule-1 / Rule-14 p3 | M2 M17 M15 M11 M12 |
| `dyad/infrastructure/INFRASTRUCTURE.md` | manifest | knowledge base (record of dependencies) | Rule-14 p1 | M14(manifest.py) M11 M12 |
| `dyad/playbooks/audit.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/playbooks/craft-instantiation.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/playbooks/d-work.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/playbooks/disposition-digest.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/playbooks/ds-report-incidents.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/playbooks/dwork-trace.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/playbooks/incident-hardening.md` | play-book | knowledge base (procedure) | Rule-3 (read by a Rule, never a Rule) | M20 M12 M11; no M1 row |
| `dyad/rules/RULE-1-containment.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-10-proposal-framing.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-11-distribution-structure.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-12-verifiable-code.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-13-reuse-over-inference.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-14-system-infrastructure.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-15-d-work-phases.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-16-concurrent-sessions.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-18-ops-scripts.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-19-server-instances.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-2-no-self-ratify.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-20-referential-integrity.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-3-d-work.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-4-integrity.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-5-coherence.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-6-vocabulary.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-7-provenance.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-8-host-mutation.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/rules/RULE-9-falsification.md` | Agent Rule | guards (rules) — the normative text its guards enforce | Rule-4 (shape), Rule-5 (set); the Rule's own concern | M1 M12(source) M13 M14(rules.py, vocabulary.py used-by, dyadlib.rule_files) M11 |
| `dyad/runbooks/audit.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/runbooks/craft.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/runbooks/d-work.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/runbooks/disposition-digest.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/runbooks/ds-report-incidents.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/runbooks/dwork-trace.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/runbooks/incident-hardening.md` | core run-book | knowledge base (procedure as data, run by a tool) | Rule-19 kernel / Rule-3 (the play-book's steps) | M19 M20 M12 M11; no M1 row |
| `dyad/scripts/craft.py` | script | tools (CLI module or library) | Rule-11 p5 | M4 M5 M15 M16 M11 M12 M6 |
| `dyad/scripts/distribute.py` | script | tools (CLI module or library) | Rule-11 p5 | M4 M5 M15 M16 M11 M12 M6 |
| `dyad/scripts/dyadlib.py` | library | tools (shared library) | Rule-11 p3 / S4 | M3 M4 M5 M6 M15 M16 M11 M12 |
| `dyad/scripts/hostadapter.py` | script | tools (CLI module or library) | syseng host-facts | M4 M5 M15 M16 M11 M12 (not in M6: the pass never lists it) |
| `dyad/scripts/incidents.py` | script | tools (CLI module or library) | Rule-3 (Incidents) | M4 M5 M15 M16 M11 M12 (not in M6: the pass never lists it) |
| `dyad/scripts/livetest.py` | script | tools (CLI module or library) | syseng verifiable-code p6 | M4 M5 M15 M16 M11 M12 (not in M6: the pass never lists it) |
| `dyad/scripts/package.py` | runner | tools (the runner) | Rule-11 (S4) | M3 M5 M6 M15 M16 M17 M18 M22 M11 M12; exempt from M4 |
| `dyad/scripts/package_rules.txt` | runner data | guards (data of the Rule-11 check) | Rule-11 p1/p6 | M21 M11 M12 |
| `dyad/scripts/runbook.py` | script | tools (CLI module or library) | Rule-19 | M4 M5 M15 M16 M11 M12 M6 |
| `dyad/scripts/trace.py` | script | tools (CLI module or library) | Rule-3 (dwork-trace play-book) | M4 M5 M15 M16 M11 M12 (not in M6: the pass never lists it) |
| `dyad/templates/INCIDENTS.md` | instance seed | knowledge base (seed) | Rule-11 p2 | M1 M11(TEMPLATES, template_dir, templates-exist, instance_state exempt) |
| `dyad/templates/PREFERENCES.md` | instance seed | knowledge base (seed) | Rule-11 p2 | M1 M11(TEMPLATES, template_dir, templates-exist, instance_state exempt) |
| `dyad/templates/VERSION` | instance seed | knowledge base (seed) | Rule-11 p2 | M1 M11(TEMPLATES, template_dir, templates-exist, instance_state exempt) |
| `dyad/templates/rows-README.md` | instance seed | knowledge base (seed) | Rule-11 p2 | M1 M11(TEMPLATES, template_dir, templates-exist, instance_state exempt) |
| `dyad/tests/guards/__init__.py` | test package marker | tests (package marker) | Rule-12 Enforcement | M1 M9 M15 |
| `dyad/tests/guards/agent/__init__.py` | test package marker | tests (package marker) | Rule-12 Enforcement | M1 M9 M15 |
| `dyad/tests/guards/agent/test_frame.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_plans.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_provenance.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_prs.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_records.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_references.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_rows.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_rules.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_sessions.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_traces.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/agent/test_vocabulary.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/craft/__init__.py` | test package marker | tests (package marker) | Rule-12 Enforcement | M1 M9 M15 |
| `dyad/tests/guards/craft/test_crafts.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/infra/__init__.py` | test package marker | tests (package marker) | Rule-12 Enforcement | M1 M9 M15 |
| `dyad/tests/guards/infra/test_bundle.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/infra/test_containment.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/infra/test_manifest.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/guards/preferences/__init__.py` | test package marker | tests (package marker) | Rule-12 Enforcement | M1 M9 M15 |
| `dyad/tests/guards/preferences/test_preferences.py` | guard test | tests (check of a guard) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_concurrency.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_craft.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_distribute.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_dyadlib.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_dyadlib_rows.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_entrypoint.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 M22 |
| `dyad/tests/test_hostadapter.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_incidents.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_livetest.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_package.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_playbooks.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 M20 |
| `dyad/tests/test_runbook.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/tests/test_trace.py` | script test | tests (check of a tool) | Rule-12 / syseng verifiable-code p4 | M1 M4(target) M9 M15 M16 |
| `dyad/vocabulary/VOCABULARY.md` | vocabulary | knowledge base (master record of terms) | Rule-6 | M13 M14(vocabulary.py; term.* references) M11 M12 |

## 3. Mechanisms by path pattern

Plan #336 revision 14 (attack Y2) named eight mechanisms that stand on the kind layout. Tracing every path
literal and glob to the code that reads it finds twenty-three. Each row: the pattern read, where it is
defined (file, zone), and what moving that pattern costs. "Zone" is the Rule-1 zone of the file that holds
the mechanism, which is the PR that changes it.

| id | mechanism | pattern(s) it reads | defined in (zone) | what a move of the pattern costs |
|---|---|---|---|---|
| **M1** | naming `kind:` rows (Y2 #1) | 24 patterns; for the core: `dyad/rules/RULE-*`, `dyad/falsification/rules/*`, `dyad/guards/<corpus>/<entity>.py`, `dyad/guards/*/*_rules.txt`, `dyad/tests/*.py`, `dyad/tests/guards/**.py`, `dyad/templates/*`; **none** for `dyad/` itself, `scripts/`, `playbooks/`, `runbooks/`, `bin/`, `hooks/`, `infrastructure/`, `vocabulary/`, `CLAUDE.md`, `README.md`, `VERSION` | `crafts/syseng/guards/naming_rules.txt` + the table `rules/naming.md` (craft: syseng, `VERSION` bump; `BUNDLE.md` row, infra) | one syseng PR per changed pattern; a path no glob selects passes silently (the guard fails only a *selecting* kind's regex) — so an unlisted new directory costs nothing and is checked by nothing |
| **M2** | naming `mode:` rows | `dyad/bin/*`, `dyad/hooks/*` tracked `100755` | same file | same PR if `bin/` or `hooks/` move |
| **M3** | naming `symbol:` rows | `dyad/scripts/package.py` (`check_rule_\d+ PROJECTORS CHECKS INVARIANTS`), `dyad/scripts/dyadlib.py` (`INVARIANTS check_invariants InvariantError CONTRACT`), `dyad/guards/*/*.py` (the contract), `crafts/*/guards/*.py`, `crafts/*/projectors/*.py` | same file | two lines per rename of `scripts/` |
| **M4** | the test mapping (Y2 #2) | `dyad/scripts/*.py` **flat**, `guard_files()` (M7), `crafts/*/{scripts,projectors}/*.py` flat → `dyad/tests/test_<n>.py`, `dyad/tests/guards/<c>/test_<e>.py`, `crafts/<c>/tests/[guards/]test_<n>.py`; `package.py` and `_*` exempt | `crafts/syseng/guards/tests.py` `modules`, `test_for`, `CRAFT_CODE` (syseng) | a module in any directory the globs do not name needs **no test** (revision 14 Y4); a rename of `scripts/` is one literal (`pkg / "scripts"`); a component directory is a new clause |
| **M5** | the invariants guard (Y2 #3) | (i) `assert` ban and (ii) must-declare-`INVARIANTS`: **`rglob("*.py")` under `dyad/` and `crafts/`** — layout-independent; (iii) pair shape and (iv) `enforce` at module level: over "the modules the runner's pass covers" (M6) and over every module that declares the list; `ENFORCE_FAILS_UNDER = ("dyad",)` | `crafts/syseng/guards/invariants.py`, `invariants_rules.txt` (one `exempt: crafts/*/server/*.py`) | **no cost for a move inside `dyad/`**: revision 14 Y4's "no invariant" is half right — a nested module *must* declare `INVARIANTS` (ii) but nothing runs it unless imported (M6) |
| **M6** | the runner's invariant pass | `dyadlib`, `package`, every registry guard (M7), every projector (M8), then a **hand-list** `("runbook", "craft", "distribute")` resolved as `PKG / "scripts" / f"{name}.py"` — `hostadapter`, `incidents`, `livetest`, `trace` are not in the pass (verified: 37 labels, none of the four) | `dyad/scripts/package.py` `invariant_modules` (agent) | a renamed `scripts/` is one literal; a new module is one tuple entry *if someone remembers*; a component directory is invisible until the list grows. See §5 P5 |
| **M7** | guard discovery (Y2 #4) | `dyad/guards/*/*.py` (names not `_*`), then `crafts/*/guards/*.py`; `load_guard(corpus, entity)` resolves `dyad/guards/<corpus>/<entity>.py` first; `GUARDS = PKG / "guards"`; `registry.module->file` (M12's register) checks each module path exists | `dyad/scripts/dyadlib.py` `guard_files`, `guard_key`, `load_guard`, `find_guard` (agent); contract in `dyadlib.CONTRACT` | a rename of `guards/` touches dyadlib, 16 guards' own CLI docstrings, Rule text (M12), workflows (M18), the hook (M17), `guards.md` (sysarch) — the most-cited directory after `scripts/`; **no proposal here moves it** |
| **M8** | projector discovery (Y2 #5) | `crafts/*/projectors/project_*.py`, keyed `craft/surface`; test at `crafts/<c>/tests/test_project_<s>.py` | `dyadlib.projector_files`, `package.projectors` (agent); `crafts/sysarch/guards/registry.py` (sysarch) | reads no core path: the core has no projectors since #160; unaffected by every shape in §4 |
| **M9** | the runner's test roots (Y2 #6) | `dyad/tests/` + `crafts/*/tests/`; `installed_roots` derives a root's craft as `dyad-operator` when `rel == "dyad/tests"` else `rel.split("/")[1]` | `package.test_suites`, `installed_roots` (agent) | a component's own `tests/` (`dyad/server/ledgerd/tests/`) is **not discovered** and would not run under the gate or `--evidence`; one glob in `test_suites` and one branch in `installed_roots` |
| **M10** | the craft guard's allowed children (Y2 #7) | the `kind: crafts/<craft>/` regex: `VERSION\|README.md\|MANIFEST.md\|(rules\|vocabulary\|templates\|guards\|tests\|falsification\|docs\|projectors\|scripts\|server)/.+`; `crafts.py DIRS = (rules, vocabulary, templates, guards, docs, falsification)` for `describe`; `craft.py SCAFFOLD` writes six of them | `naming_rules.txt` (syseng), `dyad/guards/craft/crafts.py`, `dyad/scripts/craft.py` (agent) | adding a child kind to crafts (a `tools/`) is one regex (syseng) and, for the scaffold and the card, two tuples (agent); **the core has no counterpart row** (M1) |
| **M11** | the distribution scan and build (Y2 #8) | `CORE_ROOTS = ["dyad"]` + `dyad-*` workflows; `instance_state` over every tracked file under the roots, `templates/` exempt; `Hooks.template_dir = "dyad/templates"`, `TEMPLATES` → instance seeds (+ the runner's `templates-exist` invariant); `IMPORT_LINE` into the host frame | `package.py` (agent), `distribute.py` (agent) | **layout-independent inside `dyad/`**: anything under the root ships; only `templates/` is named |
| **M12** | `rule.text->path` | every backticked `dyad/…`, `crafts/…`, `.github/workflows/dyad-…` token in Rule text must exist as a path or glob — `dyad/scripts/…` appears 10 times in 3 Rules (11, 12, 19), `dyad/guards/…` 31 times in 12, `dyad/hooks/…` 6 in 3, `dyad/rules/…` 4, `dyad/playbooks/…` 4 (Rule-3), `dyad/tests/…` 3, `dyad/runbooks/…` 2, `dyad/bin/…` 1, `dyad/vocabulary/…` 1, `dyad/infrastructure/…` 1, `dyad/templates/…` and `dyad/falsification/…` 0 (`git grep -o '\`dyad/<dir>[^\`]*\`' -- dyad/rules`) | `dyad/guards/agent/references.py` `package_paths` (agent) | **every path move is a Rule edit in the same agent PR**, and a Rule edit carries its record (Rule-9) and its pairwise statement (Rule-5); this is the enforcement that makes "update the Rule later" impossible |
| **M13** | the frame's imports | `@rules/RULE-*.md` (every Rule file must be imported — reverse check), `@vocabulary/VOCABULARY.md`, `@../preferences-corpus/PREFERENCES.md`; the install appends `IMPORT_LINE` to the host's `CLAUDE.md` | `dyad/guards/agent/frame.py`; `references` kinds `frame.import->rule|file` (agent) | a move of `rules/` or `vocabulary/` is a frame edit; nothing else in §4–§5 touches it |
| **M14** | guards that read one core store by literal | `rules.py` → `dyad/rules/*.md`; `vocabulary.py` → `dyad/vocabulary/VOCABULARY.md`; `records.py` → `dyad/falsification/rules/*.md`; `manifest.py` → `dyad/infrastructure/INFRASTRUCTURE.md`; `check_rule_11` → `dyad/VERSION`, `templates/<T>`; `bundle.py` → `dyad/VERSION`, `crafts/*/VERSION`; `dyadlib.rule_files` → `rules/` | the guards named (agent) | one literal each; none of §4's shapes touch them |
| **M15** | the manifest guard's scan | **imports** scanned in `dyad/scripts/*.py`, `dyad/guards/<c>/*.py`, `dyad/tests/**`; **invocations** scanned in `dyad/scripts/*`, `dyad/guards/*/*`, `dyad/hooks/*`, every `*.sh`, and each craft's `guards/`, `scripts/`, `projectors/` | `dyad/guards/infra/manifest.py` `python_imports`, the invocation file list (agent) | **a new code directory is unscanned**: its third-party imports (`fastapi`, `sqlalchemy`, `jinja2`) would pass undeclared — Rule-14's one mechanical fence silent. New against revision 14 Y4. §5 P6 |
| **M16** | `sys.path.insert` literals to the core library | `parents[2] / "scripts"` in **16 core guards**; `PKG / "scripts"` or `parents[2] / "scripts"` in **3 core scripts** (`package.py`, `craft.py`, `incidents.py`); `parents[3] / "dyad" / "scripts"` in **18 craft modules** (sysadmin 5, sysarch 6, syseng 3, countersign 2, disclosure 2) plus 2 sysarch templates and 2 syseng templates; 10 inline `sys.path.insert(0,"dyad/scripts")` lines in `crafts/countersign/templates/runbooks/self-diagnostic.md` and 2 in the core run-books `audit.md`, `ds-report-incidents.md`; **60 lines in 46 test files**; the craft guard's floor script (`crafts.py` `_FLOOR_SCRIPT`) — 37 non-test modules, 113 lines in all (`git grep -l sys.path.insert … \| xargs grep -l '"scripts"\|dyad/scripts'`, by top directory) | every module named (agent for the core; craft for the five crafts) | **the cost that makes a rename of `scripts/` a six-zone change**: `git grep -c` by location — core 72 (tests 15, falsification 20, rules 10, scripts 7, guards 5, runbooks 5, playbooks 3, templates 2, hooks 1, bin 1, vocabulary 1), crafts 102 (syseng 50, sysarch 22, countersign 15, sysadmin 10, disclosure 5), `.github` 12, `preferences-corpus` 1, instance prose 491 (records; never rewritten) |
| **M17** | the hooks and the entrypoint | `bin/dyad` → `$(dirname $0)/dyad-python`, `../scripts/package.py`; `hooks/pre-commit` → `dyad/bin/dyad-python`, `dyad/guards/infra/containment.py staged`; `hooks/pre-push` → `dyad/scripts/package.py check --guards --pre-push` | `dyad/bin/dyad`, `dyad/hooks/*` (agent) | three literals; a hook that cannot exec leaves Rule-1's blocking enforcement vacuous (Rule-1), so these move only with the run that proves them |
| **M18** | the workflows | `dyad/scripts/package.py` (check, build, install, craft export, bundle build), `dyad/scripts/craft.py export`, `dyad/guards/agent/rules.py`, `vocabulary.py`, `infra/containment.py range|tree`, `agent/rows.py` | `.github/workflows/dyad-{package,release,containment,d-work,rule-integrity,vocabulary}.yml` (infra) | one infra PR per rename of `scripts/` or `guards/`; CI corroborates only (#168), so a stale path is a red corroboration, not a gate |
| **M19** | the run-book runner's core run-books | `CORE_RUNBOOKS = "dyad/runbooks"`; `all_runbooks` = the instance's `<runbooks>/*.md` ∪ `dyad/runbooks/*.md`; the sysadmin `runbooks` guard checks both (section set from the `# sections:` header); `references` `event.command->command` resolves event names against them | `dyad/scripts/runbook.py` (agent); `crafts/sysadmin/guards/runbooks.py` (sysadmin) | one literal in the core; the *check* of a core kind lives in a Tended craft — bundled, so every install has it (Rule-11 p2) |
| **M20** | play-book ↔ run-book pairing | `dyad/playbooks/<n>.md` cites `dyad/runbooks/<n>.md`; Rule-3 cites four play-books by path (M12); the test asserts each pair and that the Rule names them | `dyad/tests/test_playbooks.py` (agent); Rule-3 text | a rename of either directory is a Rule-3 edit (record + sweep statement) plus the test |
| **M21** | the Rule-11 check's data | `dyadlib.package_rules` → `scripts/package_rules.txt` (+ `<instance>/package_rules.local.txt`); `hostadapter.ignore_patterns` derives `.gitignore` from its `generated:` list; the seeded `.gitignore` header names the path | `dyadlib.py`, `hostadapter.py` (agent) | one literal; the data file follows the runner wherever it goes |
| **M22** | the interpreter pin | `dyad/bin/dyad-python` `PIN_MAJOR/PIN_MINOR` ≡ `dyad/scripts/package.py` `sys.version_info < (3, 12)` | `dyad/tests/test_entrypoint.py` (agent) | one literal |
| **M23** | zones | `dyad/*` → `agent`; `crafts/*` → `craft`; `.github/*`, `BUNDLE.md` → `infra`; `<host-path>/*` → `host-zone`; `preferences-corpus/*` → `preferences` | `dyad/guards/infra/containment.py` `ZONES` (agent) | **layout-independent inside `dyad/`**; it is what makes every §4 shape a multi-PR sequence rather than one |

Three mechanisms are layout-independent inside the core root (M5's rglob, M11's root scan, M23's zone) and
would notice no re-layout. Four are hand-lists or flat globs that a new directory escapes (M4, M6, M9, M15).
The rest are literals that follow the directory they name, and M12 is what turns every literal in Rule text
into a same-PR obligation.


## 4. The shapes for `ledgerd`

The content of `ledgerd` is revisions 4–9 of plan #336 (a Python package of seven modules and one schema,
Jinja2 templates and a vendored `htmx.min.js`, a systemd unit and a launchd plist, a test suite with a
fixture schema, a README). Every shape below places that same content; none changes it. Costs are stated as
**files changed by zone**, **PRs under Rule-1**, **`VERSION` bumps** (a craft-zone change to a released craft
also owes `BUNDLE.md` an infra-zone row later, Rule-11 p7), and **the compatibility window** — whether `main`
has a red interval between two PRs that cannot be one.

Common to every shape, because four mechanisms are hand-lists (§3): wherever the package lands, the agent-zone
PR must (a) add its `tests/` to the runner's roots (M9: `test_suites`, and `installed_roots`' name derivation),
(b) make the invariant pass cover its modules (M6), and (c) make the manifest guard scan its imports (M15) —
otherwise its test suite never runs under the gate, its invariants never print, and its five third-party
imports are never checked against the manifest. Revision 15 named (a); (b) and (c) are new here.

### 4.1 Shape A — `dyad/tools/` as the rename of `dyad/scripts/`; `ledgerd` at `dyad/tools/ledgerd/`

The Operator's hypothesis: `tools/` is the kind, `server` a sub-type marked not by a directory level but by
what a component is — a directory with its own `tests/`, a unit file and a run-book, beside the flat modules.
- **What it buys.** The tree says what K2 says: one directory for the tools partition (the runner, the library,
  the CLI modules, and every packaged component). `import ledgerd` works for anything that already has the
  library directory on `sys.path`, with no second insert (contrast B). The craft table's `scripts/` child could
  follow for symmetry, or not.
- **What it costs (M16, M3, M4, M12, M17, M18, M21, M22 and prose):**
  - *agent zone*, one PR: `git mv` of 10 files; `dyadlib` (3 literals), `package.py` (5 inserts, the `later`
    hand-list, usage text), `craft.py`, `incidents.py`, `crafts.py` (the floor script), 16 guards' inserts,
    both hooks, `bin/dyad`, 46 test files (60 lines), `test_entrypoint.py`; **Rule text**: Rules 11, 12 and 19 (10
    tokens; each a Rule edit with its record amendment and Rule-5 pairwise statement); the vocabulary's
    `rendered view` row (`package.py ledger`); 2 templates; 8 play-book/run-book literals (incl. the
    `audit` and `ds-report-incidents` run-books' inline `sys.path.insert(0,'dyad/scripts')`); the README;
    20 occurrences in the Rules' falsification records (prose; records travel with their Rules — optional
    but the records then cite paths that do not exist). ≈ 100 files.
  - *craft zone*, one PR covering all five crafts (one zone): **18 craft modules** (M16), 4 templates, 10 inline
    inserts in `countersign/templates/runbooks/self-diagnostic.md`;
    syseng `tests.py` (`pkg / "scripts"` → `tools`, plus the component clause), `naming_rules.txt` (2
    `symbol:` lines; the `kind: crafts/<craft>/` children list if crafts follow), `rules/naming.md`,
    `rules/verifiable-code.md` p4, `docs/naming.md`; sysarch `guards.md` p1 ("stay in `dyad/scripts/`"),
    `distribution.md`, `templates/guard.py`, `project_surface.py`; sysadmin, countersign, disclosure prose.
    **Five `VERSION` bumps** (three released crafts → three `BUNDLE.md` rows).
  - *infra zone*, one PR: 3 workflows (12 literals) and the `BUNDLE.md` rows.
  - *preferences zone*, one PR the Operator disposes: `cli-pattern`'s `explicit-python` text names
    `dyad/scripts/<script>.py`.
  - *instance*: 491 occurrences in `agent-corpus/` (plans, audits, records, provenance) are history and are
    never rewritten; the 36 in `agent-corpus/audits/` become stale citations, which Rule-20 does not read.
- **The compatibility window.** The core PR and the craft PR cannot be one (Rule-1). After the core lands and
  before the craft PR does, every craft guard's `import dyadlib` fails: the registry reports 8 guards as
  "does not load", `dyad check` is red on `main`, and the craft PR's own pre-push gate — which runs every
  guard — is red until the craft PR's content is what is being pushed. Two sequences avoid the red interval:
  (i) the craft PR goes **first** with a dual-path insert (`tools` if it exists, else `scripts`) in all 18
  modules, then the core PR, then an optional cleanup craft PR — **two craft rounds**; or (ii) §5 P2 goes
  first, after which no craft module names the directory at all and the rename is **one agent PR plus
  prose**. Without either, the rename is a planned red interval on `main` of one merge.
- **Verdict.** Four to five PRs in four zones, five `VERSION` bumps, and a compatibility window — or P2
  first. The sub-type "server" gets no name of its own in the table: it is "a component directory", which
  the generic component clause (4.5) can state, but nothing distinguishes a server component from a
  non-server one at the tree level. Rule-19 does that at the instance (the run-book), which is where
  revision 15's S1 located the difference anyway.

### 4.2 Shape B — `dyad/server/ledgerd/` under a `server/` kind added to the core (revision 15)

- **What it buys.** The kind the craft table already has, at the core root: `crafts/<craft>/server/` and
  `dyad/server/` read the same. The whole component is one directory (revision 14's by-component intent,
  honoured for the one kind whose components are whole things). Nothing existing moves. No compatibility
  window: the syseng clause matches nothing until the core directory exists (a `kind:` whose glob selects no
  path passes — `mode: crafts/<craft>/server/*.sh` selects nothing today, `lan-git` being gone, and the gate
  is green).
- **What it costs:**
  - *craft zone (syseng)*, PR S: one `kind:` row (`dyad/server/<name>/ = dyad/server/** = dyad/server/[a-z][a-z0-9-]*/.+`)
    and its table row; the **component clause** in `tests.py` (4.5) with its test; `rules/naming.md`,
    `rules/verifiable-code.md` p4 one sentence; the record amended. `VERSION` 0.4.0 → 0.5.0 (one `BUNDLE.md`
    row later, infra; the guard warns meanwhile, Rule-11 p7).
  - *agent zone*, PR A: the component; `package.py` — `test_suites` (+ `dyad/*/*/tests`), `installed_roots`
    (the name of a nested root), `invariant_modules` (discover component modules, or extend the hand-list),
    `dyad ledger …` dispatch; `manifest.py` scan dirs (+ component directories) and `manifest_rules.txt`
    tokens; `INFRASTRUCTURE.md` rows; `README.md` map row for `server/`; `VERSION` 0.12.0; one more
    `sys.path.insert` in the component for the core library (M16 +1). No Rule edit: no Rule cites
    `dyad/server/` and none needs to.
  - *workstation zone*, PR B: as revision 15 (`workstation-corpus/server/ledgerd/README.md` keeps the
    sysadmin run-book guard's `server*/` citation warning off, S5).
  - *later, infra*: `BUNDLE.md` rows for syseng 0.5.0 and the core 0.12.0 after their tags — not #336's.
- **What it leaves.** `server` stays a peer of `scripts/` and the tools partition stays a classification.
  If the Operator later adopts the rename (A), `dyad/server/` moves under `dyad/tools/` with one `git mv`,
  one `kind:` row and no Rule edit — B forecloses nothing. The sysadmin run-book guard's `SERVER_GLOBS`
  (`crafts/*/server*`, `<host>/server*`) does not see `dyad/server/`; S5's instance directory is the
  honest answer today, a one-line glob in a released craft the follow-on.
- **Verdict.** Three PRs, one `VERSION` bump, no window. The cheapest shape that files a server under the
  kind the architecture already names for it.

### 4.3 Shape C — the partition as directory levels for the whole core

`dyad/{CLAUDE.md,README.md,VERSION}` + `dyad/kb/{vocabulary,playbooks,runbooks,templates,falsification,
infrastructure}/` + `dyad/guards/{rules/,<corpus>/}` + `dyad/tools/{bin,hooks,*.py,ledgerd/}` + `dyad/tests/`.
- **What it buys.** The tree *is* K2; a reader learns the partition from `ls`.
- **What it costs.** Every mechanism in §3 but M5, M11 and M23 — M1 (seven `kind:` rows and the table), M2,
  M3, M4, M6, M7 (the single most-cited directory, 31 Rule-text tokens in 12 Rules), M9, M12 (every Rule
  that cites a path — 15 of 19 — edited with records), M13 (the frame's `@rules/`, `@vocabulary/`), M14 (six
  literals), M15, M16 (113 inserts), M17, M18, M19, M20, M21, M22; the `IMPORT_LINE` an install appends to
  every host frame changes, so every *installed* system's `CLAUDE.md` needs a hand edit on upgrade (Rule-11
  p2's "never hand-editing" is the property at stake); `references.py`'s `_PKG_PATH` regex; the memory
  cache's `source:` lines on every machine. Four zones, two craft rounds, a `dyad-operator` major bump.
- **Verdict.** A program, not a d-work: weeks of PRs for a labelling gain that §5 P3/P4 deliver as a column
  at zero code. Listed because the review was asked to be exhaustive; not recommended.

### 4.4 Shape D — `dyad/scripts/ledgerd/` as a package inside the existing kind

- **What it buys.** No new kind row; the component is one directory; `import ledgerd` works for everything
  that has `scripts/` on its path.
- **What it costs.** The same component clause as B (4.5) in syseng — revision 14 Y4's "not free" — and the
  same agent-zone extensions (M6, M9, M15). One `VERSION` bump. Two PRs plus the workstation one.
- **What it leaves.** A server filed as a script: the Operator's revision 15 claim (S1), confirmed there on
  the architecture's own distinction (Rule-19, the run-book guard's `server*/`), is set aside for a
  directory name. If the rename (A) comes later, `scripts/ledgerd/` becomes `tools/ledgerd/` with the
  rest, which is exactly where A puts it — D is A's end state under A's old name.
- **Verdict.** Costs what B costs minus one `kind:` row, and spends it to file the thing under the wrong
  name. Not recommended unless the rename is already decided, in which case A's own sequencing applies.

### 4.5 The component clause (serves A, B and D alike)

Whatever the kind, the syseng change that lets a *packaged* component live under it should be written once
and generically, not as a `server` clause: **a component is `dyad/<kind>/<component>/` (or
`crafts/<craft>/<kind>/<component>/`) that holds its own `tests/`**; every `*.py` under it outside `tests/`
maps to `<component>/tests/test_<stem>.py` (a stem collision across sub-packages fails); the runner adds
every such `tests/` as a root; the invariant pass covers every component module (by discovery of
`INVARIANTS`/`TREE_INVARIANTS` declarations under the component, not by name); the manifest scan includes
the component's modules. Written this way the syseng PR of B is the syseng PR of A and D, and a later
`tools/<x>/` needs only a `kind:` row. The `exempt: crafts/*/server/*.py` line in `invariants_rules.txt`
(a reference deployment's own code, never loaded by the pass) is the precedent that a server directory has
already needed special handling once; the component clause replaces that special case with a general one.

### 4.6 Side by side

| | A `tools/ledgerd/` + rename | B `server/ledgerd/` | C partition as directories | D `scripts/ledgerd/` |
|---|---|---|---|---|
| PRs (Rule-1) | 4–5 (agent, craft×1–2, infra, preferences) | 3 (craft, agent, workstation) + infra later | many, four zones, two craft rounds | 3 + infra later |
| `VERSION` bumps | core + 5 crafts | core + syseng | core (major) + 5 crafts | core + syseng |
| Rule edits (M12) | Rules 11, 12, 19 | none | 15 of 19 | none |
| compatibility window | yes (or P2 first) | no | yes | no |
| files the tools partition as a directory | yes | no (a column, §5 P3/P4) | yes | no |
| names the server as what it is | no (a component directory) | yes (`server/`, the craft table's own kind) | yes (`tools/server/`?) | no |
| forecloses the rename | no | no (one `git mv` later) | — | no |
| mechanisms extended in the agent PR | M6 M9 M15 (+M4 via syseng) | same | all | same |

## 5. Every other refactoring found

Each in Rule-10 form — one path, its strongest counter, a reconciliation — and costed as §4 costs are.
None is executed here; each is a candidate row for the Operator to open or decline. **P0** is the component
clause of 4.5 and belongs to #336; the rest are independent of `ledgerd`.

**P1 — close the core tree: a `kind:` row for `dyad/` itself.**
- *Path.* One row in `naming_rules.txt` mirroring the craft row: `kind: dyad/ = dyad/** =
  dyad/(VERSION|README\.md|CLAUDE\.md|(bin|hooks|scripts|guards|tests|templates|rules|vocabulary|playbooks|runbooks|falsification|infrastructure)/.+)`
  (plus `server` the day B lands), and its table row. Craft zone (syseng, `VERSION` bump), `BUNDLE.md`
  row later. Adding a core kind then *is* a syseng edit — a taxonomy decision made in the table that owns
  the taxonomy, which is what the Operator's question asked for.
- *Counter.* The core's children change more often than a craft's (four kinds added since September); each
  new kind would cost a released-craft PR and a bundle row, and the `kind:` row would also have to admit
  every file the kinds hold today (`__init__.py`, `package_rules.txt`).
- *Reconciliation.* That cost is the point: today a new core directory is free and unchecked (§0 ¶2). The
  regex is one line, its admissions are listed above, and the three kinds the core added in a month each
  came with a Rule edit anyway.

**P2 — one place for the core library's location.**
- *Path.* `dyad/bin/dyad-python` exports the library directory on `PYTHONPATH` (one shell line; it already
  resolves the interpreter for the entrypoint and both hooks) and the runner's `suite_env` sets it for the
  test child; every `sys.path.insert(… "scripts")` is deleted — 16 core guards, 3 core scripts, 18 craft modules, 4
  craft templates, 60 lines in 46 test files, 10 inline inserts in the countersign run-book template and 2 in
  core run-books (113 lines), the `crafts.py` floor script kept (it deliberately pins a *floor* checkout). The
  sysarch `guards.md` property 5 ("the CLI stays") is reworded to `dyad/bin/dyad-python <guard>`, which the
  hooks already use. Zones: agent (one PR), craft (one PR, five crafts, five bumps, three bundle rows),
  craft prose. **Precondition for A** (§4.1) and the only thing that makes a rename of `scripts/` a one-zone
  edit.
- *Counter.* Plain `python3 dyad/guards/<c>/<e>.py` by hand stops working, and a `PYTHONPATH` set by a
  wrapper is one more environment fact the kernel-only path depends on; 113 one-line deletions across six
  zones is itself a large diff for a layout fact nobody has yet needed to change.
- *Reconciliation.* The host-facts rule (`crafts/syseng/rules/host-facts.md` p1) and Rule-13's recurrence
  trigger both say a fact read in 113 places is read in 112 too many; the wrapper is already the one entry
  for the hooks and the entrypoint, so the fact moves to where the kernel pin already lives. The hand-run
  form changes from `python3 <guard>` to `dyad/bin/dyad-python <guard>`, which is what Rule-1's hooks
  already print. Do it before any rename, or never rename.

**P3 — the README map is stale against the tree.**
- *Path.* One agent-zone PR: rows for `playbooks/` (7 files, #165/#213/#223/#290/#309) and `runbooks/`
  (7 files, M19) — the map's own rule says "any d-work that adds a directory here updates this map in the
  same PR", and four d-works did not; delete the duplicate `bin/dyad` row (a two-cell row after the
  `tests/` row); the `scripts/` row's holds-list gains `hostadapter.py`, `incidents.py`, `livetest.py`,
  `trace.py`; the `../crafts/sysadmin/` row stops naming `crafts/lan-git/` as if present; and a
  **`partition` column** (knowledge base / guards / tools / tests) — K2 as a classification, zero code.
- *Counter.* Prose with no guard: it will drift again, and a column is not a taxonomy anyone enforces.
- *Reconciliation.* The README is what the frame points a new reader at, and the only place the tools
  partition can be *stated* without moving a file. The drift is the finding; a mechanical check of the map
  (every top-level kind has a row) is one more `TREE_INVARIANT` in the runner if the Operator wants it, and
  is named here rather than proposed.

**P4 — the vocabulary's `craft` row names the partitions.**
- *Path.* Amend the `craft` definition ("a contained tree with one root, `VERSION`, rules, vocabulary,
  templates, guard data, records, docs and no instance state") to name its three partitions and that
  *tools* (scripts, projectors, servers, the entrypoint and hooks) and *tests* are elements too. Agent
  zone; Rule-6's trigger: the record names Rules 1, 4, 5, 11, 14 (the `used by` column) and states each
  still reads correctly.
- *Counter.* A definition that enumerates elements goes stale with every kind added (it already has: no
  tools, no tests, no play-books); a definition that names three *partitions* and no elements would not.
- *Reconciliation.* Take the counter: name the partitions, not the elements, and let the README map (P3)
  hold the enumeration. One row, one record, five Rules re-read.

**P5 — the invariant pass by discovery, not a hand-list.**
- *Path.* Replace `("runbook", "craft", "distribute")` in `invariant_modules` with discovery: every module
  under the core's code directories (and, after P0, every component) that declares `INVARIANTS` or
  `TREE_INVARIANTS`. Four modules enter the pass today (`hostadapter` declares none; `incidents`, `livetest`,
  `trace` do). Agent zone, one PR; the syseng guard's (iii) follows the pass automatically.
- *Counter.* The four already enforce at import (M5 (iv)), so nothing is unchecked, only unreported; and
  discovery costs a directory walk on every `dyad check`.
- *Reconciliation.* The `[invariant]` lines are what the evidence block carries and the Operator re-runs
  (Rule-14 p3); an invariant that holds but never prints is not evidence. The walk is the same one `tests.py`
  already does.

**P6 — the manifest guard's scan directories are a hand-list.**
- *Path.* `python_imports` scans `scripts/`, `guards/<c>/`, `tests/`; the invocation scan a fixed file list.
  Derive both from one discovery shared with the test mapping (every `*.py` and `*.sh` under the core and
  the crafts, tests included), so a new code directory is scanned the day it appears. Agent zone, one PR.
  **Prerequisite for every shape in §4** that adds a package: without it `ledgerd`'s five imports pass
  Rule-14's one mechanical fence unexamined.
- *Counter.* A scan over everything slows the guard and will flag a vendored `static/htmx.min.js`'s
  neighbours or a fixture's imports; the list was narrow on purpose.
- *Reconciliation.* The manifest's scope is "every import the package makes" (Rule-14 Enforcement); a
  narrow list is a gap the first package directory falls through. Fixtures are under `tests/`, which the
  scan already includes.

**P7 — citations of a craft that is not in the tree.**
- *Path.* `crafts/lan-git/` is cited by `dyad/README.md`, `dyad/infrastructure/INFRASTRUCTURE.md`,
  `crafts/sysadmin/README.md`, `crafts/sysadmin/rules/server-instances.md`, and two `allow:` lines in
  `naming_rules.txt` that the naming guard warns about on every run. Reword each citation as history ("its
  own craft since #181, authored elsewhere") and delete the two allow lines. Zones: agent (one PR), craft
  (sysadmin + syseng, two bumps, two bundle rows). Fold into the next PR of each zone rather than open a
  row for it.
- *Counter.* Two permanent warnings cost nothing and the history is true; two released-craft bumps for
  prose is a poor trade.
- *Reconciliation.* The naming rule itself says an allow list "only shrinks"; a warning on every evidence
  block is noise the Operator reads every merge. Fold, do not open.

**P8 — Rule text cites the runner by file path rather than by command.**
- *Path.* Ten tokens in Rules 11, 12 and 19 name `dyad/scripts/package.py …` where the entrypoint
  (`dyad check`, `dyad build`) is the one command line under `cli-pattern: industry-standard`. Reword to
  the command, keeping the one sentence that names where the runner lives. Agent zone; each Rule edit
  carries its record and Rule-5 statement — fold into the next edit of each Rule, never a sweep.
- *Counter.* The path is what the reference guard resolves (M12); a command is not a path and would not be
  checked.
- *Reconciliation.* Keep one path token per Rule for M12 and reword the rest; the gain is that A or any
  later move of the runner edits one token per Rule instead of ten.

**P9 — observations, not proposals.** (i) `sessions/ds-cabinet-cloud-4.md` claims six rows other live
seats hold, with 84 files — the shape of a bare `dyad session touch` (#130, #325's concern). (ii) A second
`dyad session touch` from a new process of the *same* harness session printed "last written by a
different, still-live process … under this same session id" — the writer id is per process, so one seat's
own re-touch trips the two-sessions warning; a defect observation for Rule-16's guard, not this audit's to
fix. (iii) `scripts/package_rules.txt` is guards data under a tools directory, but it sits beside its one
reader (the runner), which is the placement rule for guard data; consistent, stated. (iv) Core run-books
(`dyad/runbooks/`) are checked by a Tended craft's guard (sysadmin), which is bundled, so a core-only
install still checks them — consistent with Rule-11 p2, stated.

## 6. Not observed

- No shape was prototyped: no file was moved, no guard edited, no clause written. Every cost is a count of
  files and literals read from the tree, not a measured diff.
- The behaviour of `tests.py` and `naming.py` on a `kind:` row whose glob selects nothing was *inferred*
  from the live `mode: crafts/<craft>/server/*.sh` line (which selects nothing and passes), not run.
- Whether any *installed* system (another repo running this core) holds its own `sys.path.insert` to
  `dyad/scripts` — P2 and A would reach it on its next core upgrade through the crafts' tags, not through
  anything this repo controls.
- The host (`workstation-corpus/`) and the hosting's CI were not read; nothing here depends on them.
- The content of `ledgerd` and the OAuth, supervisor and run-book decisions of plan #336 revisions 4–9.

## 7. Carry-back: directions for #336

Read from `main` by `ds-cabinet-cloud-6`, which writes #336 revision 16 and asks its plan-`Y` in its own
session; nothing here is a disposition (#252 D3) and nothing here instructs (#253 R4).

**Placement.** `dyad/server/ledgerd/` — shape B (§4.2). `server` is the kind the architecture already keeps
for this thing, as a peer of `scripts/` and `projectors/`; the tools partition stays a classification
(P3/P4), not a directory. The Operator's sub-type reading is honoured where the architecture places it: the
component is one directory, and what makes it a *server* rather than a script is Rule-19's run-book and
health command at the instance, which revision 15's S1 already located there.

**Kinds to add or rename first.** One: the `server/` kind at the core root, by the syseng `kind:` row. **No
rename.** A rename of `scripts/` to `tools/` is a separate program whose first step is P2 (§5), and whose
cost without P2 is four zones and a red interval (§4.1); it is listed for the Operator to open as its own
row, and B does not foreclose it (one `git mv` and one `kind:` row later).

**Write the syseng change as the component clause (P0, §4.5), not a `server` clause**, so the same PR serves
`dyad/tools/<x>/` or `crafts/<craft>/<kind>/<x>/` later.

**PR sequence by zone**, one Done batch:
1. **PR S — craft zone (syseng, `VERSION` 0.4.0 → 0.5.0):** `naming_rules.txt` `kind: dyad/server/<name>/`;
   `rules/naming.md` row; `guards/tests.py` the component clause (`dyad/<kind>/<component>/` with `tests/`
   → `<component>/tests/test_<stem>.py`) and its test; `rules/verifiable-code.md` p4 one sentence; the
   record amended. Lands first; selects nothing until PR A; `BUNDLE.md` warns on the syseng row until the
   tag (Rule-11 p7, by design).
2. **PR A — agent zone (core `VERSION` 0.11.0 → 0.12.0):** `dyad/server/ledgerd/` as revision 15 lays it
   out; `package.py` — `test_suites` adds `dyad/*/*/tests`, `installed_roots` derives the core's name for a
   nested root, `invariant_modules` discovers the component's modules (P5's shape, at least for the
   component), the `dyad ledger …` dispatch; `guards/infra/manifest.py` scans the component's modules (P6's
   shape, at least for the component) and `manifest_rules.txt` gains the four import tokens;
   `infrastructure/INFRASTRUCTURE.md` the five rows with the per-instance note; `README.md` a `server/` row
   (the map's own rule; take P3's other rows in the same PR only if the Operator says so — they are not
   `ledgerd`'s); `hostadapter.py` as revision 13; tests. The PR's own test asserts that the mapping, the
   invariant pass and the manifest scan each name every `ledgerd` module — the three silent exemptions
   cannot occur in the delivered order.
3. **PR B — workstation zone:** as revision 15 (the run-book, the linger ops script, the instance manifest
   rows, `workstation-corpus/server/ledgerd/README.md`; then the host session's change-log rows and the
   health event).
4. **Not #336's:** the infra-zone `BUNDLE.md` rows after the syseng and core tags; the releases; the
   sysadmin run-book guard's `SERVER_GLOBS` gaining `dyad/server*` (one line in a released craft); P1–P8.

**What #336 revision 16 should state that revision 15 did not:** the manifest-scan gap (M15) and the
invariant-pass gap (M6), both closed in PR A; that the syseng clause is generic; and that the rename is a
named, separate program gated on P2.
