# Naming (syseng craft, Tended rule)

Read by every core Rule and craft rule that names a file, symbol or token pattern (the `owner`
column below): the core keeps the *sentence* that a pattern exists ("a row file is
`<instance>/d-work/rows/<id>.md`"); this rule keeps the one table every pattern belongs to, so
that a pattern is defined once and drift is found by a guard, not by reading eleven Rules
(#113 named the drift; plan #162 (a)1 collected the table). Terms (`naming pattern`, `allow
line`): `../vocabulary/CRAFT.md`. Guard: `../guards/naming.py` (registry label `syseng/naming`,
entity `name`), data `../guards/naming_rules.txt`. Rationale: `../docs/naming.md`.

## The table
One row per pattern. `checkable` says whether `naming.py` verifies it (from a `kind:`, `symbol:`
or `env:` line of `naming_rules.txt`); a row marked *no* is inference, or another guard's. The
guard fails on a `kind:` whose pattern is not in this table, so the two cannot drift.

| pattern | names | owner | example | checkable |
|---|---|---|---|---|
| `dyad/rules/RULE-<n>-<slug>.md` | an Agent Rule file | Rule-4 | `RULE-12-verifiable-code.md` | yes (`<n>` unique) |
| `crafts/<craft>/rules/<slug>.md` | a Tended rule of a craft | Rule-11 (a craft's tree) | `crafts/syseng/rules/naming.md` | yes (kebab; `README.md` allowed) |
| `crafts/<craft>/` (+ `VERSION`, `README.md`, `MANIFEST.md`, `rules/`, `vocabulary/CRAFT.md`, `templates/`, `guards/`, `tests/`, `falsification/`, `docs/`, `projectors/`, `scripts/`, `server/`) | a craft corpus tree | Rule-11 (the sysarch `distribution.md`) | `crafts/sysadmin/` | yes (allowed children) |
| `<instance>/d-work/rows/<id>.md` | a row file | Rule-16 | `rows/162.md` | yes (`<id>` digits, unique; `README.md` allowed) |
| `<instance>/d-work/plans/<id>.md` | a plan file | Rule-15 | `plans/162.md` | yes |
| `<instance>/d-work/sessions/<id>.md` | a session presence file | Rule-16 | `sessions/lan-git-install.md` | yes (`<id>` a path-safe session name, no digits-only requirement) |
| `<instance>/falsification/<slug>.md` | an instance falsification record | Rule-9 | `sysarch-extraction.md` | yes (kebab) |
| `dyad/falsification/rules/rule-<n>-<slug>.md` | a Rule's falsification record (package) | Rule-9 | `rule-12-verifiable-code.md` | yes (`rule-<n>-`; `rules-9-10-promotion.md` fits; `rule-sets.md` is an allow line) |
| `crafts/<craft>/falsification/rules/<slug>.md`, `crafts/<craft>/falsification/<slug>.md` | a craft rule's record; a craft's own record | Rule-9 (records travel with their rules) | `crafts/syseng/falsification/rules/naming.md` | yes (kebab) |
| `<instance>/audits/<YYYY-MM-DD>-<slug>.md`, `<instance>/audits/INCIDENTS.md` | an audit; the incident log | frame / Rule-3 | `2026-09-13-guards-vs-rule-12.md` | yes |
| `dyad/guards/<corpus>/<entity>.py` | a core guard module | Rule-11 property 1 (the sysarch `guards.md`) | `guards/agent/rows.py` | yes (snake; `<corpus>` a zone; `_`-prefixed is not a guard) |
| `crafts/<craft>/guards/<entity>.py` | a craft guard module | the sysarch `guards.md` | `crafts/syseng/guards/naming.py` | yes |
| `<entity>_rules.txt` beside its guard | a guard's data file | the sysarch `guards.md` | `manifest_rules.txt` | yes (`<entity>.py` exists beside it) |
| `dyad/bin/<name>`, `dyad/hooks/<hook>` tracked `100755` | a package file the host executes by name: the CLI entrypoint, the hooks an install points `core.hooksPath` at | Rule-11 p5 (the hook ships at `dyad/hooks/pre-commit`) | `dyad/hooks/pre-commit` | yes (`mode:` line; the **tracked** mode, never the bit on disk) |
| `crafts/<craft>/templates/*.sh`, `crafts/<craft>/server/*.sh` tracked `100755` | a shell file a craft ships to be run: an ops-script skeleton, a container entrypoint | the sysadmin `ops-scripts.md`; the sysadmin `server-instances.md` | `crafts/sysadmin/server/entrypoint.sh` | yes (`mode:` line) |
| `dyad/tests/test_<name>.py` ↔ `dyad/scripts/<name>.py`; `dyad/tests/guards/<corpus>/test_<entity>.py` ↔ the core guard; `crafts/<craft>/tests/guards/test_<entity>.py` ↔ the craft guard; `crafts/<craft>/tests/test_<name>.py` ↔ a craft projector or script | a test module and its mapping | this craft, `verifiable-code.md` (from Rule-12) | `test_dyadlib.py` | shape yes; the mapping by `tests.py`, not `naming.py` |
| `crafts/<craft>/projectors/project_<surface>.py` ↔ `crafts/<craft>/tests/test_project_<surface>.py` | a projector and its test | the sysarch `projection.md` | `project_erd.py` | yes |
| `check_rule_<n>` | a Rule's own check function in the runner | Rule-11 (S4) | `check_rule_12` | yes (symbol) |
| `INVARIANTS`, `check_invariants`, `InvariantError` | the invariant protocol names | this craft, `invariants.md` | `dyadlib.INVARIANTS` | yes (symbol) |
| `ENTITY`, `CORPUS`, `FIELDS`, `TRANSACTION`, `check_package`, `check_transaction`, `describe`, `summary` | the guard contract symbols | the sysarch `guards.md` (`dyadlib.CONTRACT`) | — | yes (symbol; the registry's contract check too) |
| `main` | a projector's entrypoint | the sysarch `projection.md` p4 | `project_erd.main` | yes (symbol) |
| `.github/workflows/dyad-<slug>.yml` | a package workflow wrapper | Rule-11 p2 (Rule-14 library) | `dyad-package.yml` | yes (prefix; an unprefixed workflow is instance and an allow line) |
| `dyad-<version>.tar.gz`, `<craft>-<version>.tar.gz`, `vMAJOR.MINOR.PATCH` = `v` + `VERSION` | a release archive and tag | Rule-11 p4 | `dyad-0.1.0.tar.gz`, `v0.1.0` | tag: no (The World); `VERSION` shape: Rule-11's check and the craft guard |
| `DYAD_<NAME>` | an environment variable the package reads | Rule-11 p3 | `DYAD_INSTANCE`, `DYAD_OPS`, `DYAD_RUNBOOKS`, `DYAD_ROLE`, `DYAD_NO_NESTED_TESTS` | yes (`env:` line; every variable the package code reads is listed, and every listed one is read) |
| `dyad <noun> <verb>` | a CLI command | preference `cli-pattern` (#152) | `dyad check --evidence` | no (inference over `package.py`'s usage text) |
| `<key>` kebab-case | a preference key | frame (`preferences.py`) | `merge-disposition` | no (the preferences guard's shape check) |
| `<term>` lower-case noun phrase | a vocabulary term | Rule-6 | `plan file` | no (prose; Rule-6's guard) |
| `<ops>/<d-work>-<hN>-<slug>.sh`, `<same>-undo.sh`, `ops/*.log` (generated) | an ops script, its undo, its log | the sysadmin `ops-scripts.md` (Rule-18 kernel) | `135-h4-etc-hosts.sh` | yes (shape; its tracked `100755` is `ops_scripts.py`'s, part of the Rule-18 form — not a `mode:` line here: one owner) |
| `<runbooks>/<instance>.md`, `<runbooks>/events/<instance>.jsonl` | a run-book and its event store | the sysadmin `server-instances.md` (Rule-19 kernel) | `git-server.md` | yes |
| `<instance>-<utc ts>-<name>` | an event id | the sysadmin `server-instances.md` | `git-server-20260914T101500Z-status` | no (the events guard already) |
| `#<id>`, `d-work #<id>`, `merge #<n>`, `<date> <Y\|N> <plan\|done\|merge #n\|reason>` | a reference token; a disposition entry | Rule-3 / Rule-20 | `d-work #162` | no (Rule-20 resolves; the rows guard has the shape) |
| `Y/N: proceed with #<id> as planned?`, `Y/N: Done with #<id> <title> (merges PR #a, #b)?`, `Y/N: run <action>?`, `Y/N: release vX.Y.Z?` | counter-prompt forms | Rules 3, 8, 11 | — | no (chat, not repo) |
| `<instance>/projections/<surface>.html` (generated) | a projection | the sysarch `projection.md`; `determinism.md` here | `erd.html` | yes (a `generated:` pattern of `package_rules.txt`; never tracked, Rule-11's check) |
| `dyad/templates/<Name>` (seeds; `package.TEMPLATES` maps them) | an instance seed | Rule-11 | `INCIDENTS.md` | yes (shape); every `TEMPLATES` key exists: the runner's `templates-exist` invariant |
| `guard:<corpus>/<entity>.py`, `world`, `import:<module>` | a resolver token; a manifest token | Rule-20 / Rule-14 | `guard:agent/vocabulary.py` | no here (shape in the references and manifest guards; the register's `resolver-shape` invariant) |
| `<YYYY-MM-DD>` dates in rows, change log, audits | a date | Rule-3 / Rule-8 | `2026-09-14` | no (the rows and changelog guards already) |

## The guard
`naming.py` reads `naming_rules.txt`: a `kind:` line per checkable path row (`kind: <pattern> =
<path glob> = <regex over the whole path>`; a named group `id` must be unique within the kind, a
group `beside` names `<dir>/<beside>.py` that must exist); a `mode:` line per mode row (`mode:
<pattern> = <path glob> = <tracked mode>`): every selected path is tracked at that mode in git's
index (`dyadlib.tracked_mode`), never judged by the bit on disk — with `core.fileMode=false` (an
NTFS checkout) every file reads 755 on disk whatever git holds, which is how an entrypoint tracked
`100644` reached an image and could not exec (#135, #141); a path not yet in the index warns
(`untracked: disk mode used`) and falls back to the disk bit. A `mode:` pattern must be a table row
like a `kind:`. One owner per path: the mode of an ops script belongs to the Rule-18 form
(`crafts/sysadmin/guards/ops_scripts.py`), so `<ops>/*.sh` is not a `mode:` line. A `symbol:` line per symbol row
(`symbol: <module glob> : <name> …`, each a plain name the module must define at top level or a
regex at least one top-level name matches); one `env:` line naming every `DYAD_<NAME>` the package
code reads; and `allow:` lines. Every path the tree holds (tracked or not yet committed) that a
glob selects must match its regex or be allowed. An `allow: <path> # <reason>` line without a
reason fails, a stale one (the path is gone) fails when the path is package (`dyad/`, `crafts/`)
and warns when it is instance (the data travels to installs whose instance differs), one the path no
longer needs warns — the list only shrinks, and its count is printed in the summary. No pattern is grandfathered by date.

## Inference, stated
Whether a name is *apt* is inference. The rows marked *no* are checked elsewhere or not at all,
as the column says.
