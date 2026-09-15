# Distribution (sysarch craft, Tended rule)

Read by Rule-11's kernel (`dyad/rules/RULE-11-distribution-structure.md`): the core Rule binds
*that* every tracked file is craft or instance, that a craft is one tree with one root, that an
install writes only under that root plus documented hooks and never overwrites a host file, and
what a release is. This rule is the *design* those sentences rest on. Text moved from Rule-11
properties 1–4 by d-work #160 (as reframed by #154 and #156); a Tended rule — any form, no Rule-4
block, no sweep. Terms: `crafts/sysarch/vocabulary/CRAFT.md` (none of its own; `package`,
`instance`, `release`, `install` stay Agent terms, owner Rule-11).

## What is craft, what is instance
- A **craft** is what another dyad system installs and is identical across systems. The core
  craft `dyad-operator` (`dyad/`) is the one craft every system has: the frame, its Agent Rules,
  its Agent vocabulary, the guards with their data (`dyad/guards/<corpus>/`, `guards.md`), the
  preference schema, the templates, the falsification records of Rules (`falsification/rules/`,
  #71 A6). A **Tended craft** (`crafts/<craft>/`) holds Tended rules, a craft vocabulary,
  templates, guards with their tests, projectors with their tests, guard data, records, docs.
- The **instance** is one system's state — ledger rows and plans, incidents, audits, the other
  falsification records, preference values, the host corpus, the craft registry
  (`crafts/REGISTRY.md`), archives — and is never inside a craft. The core's scan refuses
  host-specific strings and instance artifacts (by name or header) inside a craft; the list is
  data, `dyad/scripts/package_rules.txt` (#72 A7), and the craft guard runs the same scan over
  every Tended craft with its own additions (`dyad/guards/craft/crafts_rules.txt`).
- Generated output (rendered views, projections, bytecode, logs) is neither: it is never tracked
  (Rule-11 property 6; `generated:` entries of the same data file).

## Craft-relative paths
Craft files reference their own paths relative to the craft root, and instance paths through one
configurable instance location: `DYAD_INSTANCE`, default `agent-corpus`, relative to the git root
(`dyad/scripts/dyadlib.py` `instance()`, #72 A3). Paths printed in Rule text are the defaults. A
Tended craft finds the core at `dyad/` beside `crafts/` (`dyadlib.crafts_dir`), never by an
absolute path.

## Archive and version
- Every craft carries one `VERSION` line, `MAJOR.MINOR.PATCH`, at its root.
- The core's archive is `dyad-<version>.tar.gz` (built by the release workflow on the tag); a
  Tended craft's export is `<craft>-<version>.tar.gz` with entries under `crafts/<craft>/`, so it
  installs into any repo at the same path. Two builds of one tree are byte-identical (entries
  sorted, mtime 0, no owner, gzip header mtime 0), so an archive's sha256 identifies a tree — the
  craft registry's proof of an unmodified install.
- An installed instance records the core version it runs in `<instance>/d-work/VERSION`, seeded
  by `dyad install` (#72 A4); a Tended craft's version is its row in `crafts/REGISTRY.md`.

## Entrypoint
One command line for the whole system: `dyad/bin/dyad`, `dyad <noun> <verb>` (the shape the
preference `cli-pattern` selects, #152). It is invoked by path and never placed on the host's
PATH by an install; a Tended craft adds verbs to it only through the core's dispatch
(`dyad craft …`, `dyad project …`), never a second entrypoint.

## Receiving-instance upgrade order (#178)
A system that already runs an older core and adopts a newer one is not installing a single
craft: it is catching up on every Tended craft the newer core's Rule text now cites by path
(`references.md` `rule.text->path`). Empirically (four real commits of this repo's own history
replayed into scratch receiving instances, #178's plan): `dyad craft install` does not exist
before #156, so a pre-#156 core cannot install any Tended craft — the verb ships inside the core
craft it would be used to extend. Once the verb exists, installing one cited craft alone
(`sysarch`) while its siblings (`sysadmin`, `syseng`) stay absent leaves `dyad check --guards` —
the pre-push gate, Rule-14 property 3 — red: `references.py`'s craft-presence skip
(`Corpus.crafts_absent`) is one flag for the whole `crafts/` tree, not per craft, so once any
craft is present every `crafts/<name>/…` citation is checked, including ones naming a sibling
that is not yet there. Installing every craft the receiving core's Rule text currently cites —
today `sysadmin`, `sysarch`, `syseng`, together — clears it (`check --guards`: 0 FAIL, verified).
**Order: the core craft first, then every Tended craft its Rule text cites, as one follow-on
pass; each is still its own Rule-1 zone and PR, but the pass's completion — not each PR — is what
`check --guards` is asked to be clean against**, the same pattern this repo's own operator already
lived with landing #135, #155, #160 and #162 (plan #176, G2 verification). `requires:` (a craft's
`MANIFEST.md`, checked by `dyad craft install` and `crafts.unmet`) is a narrower, independent
guard for a different failure: a core new enough to run `dyad craft install` but older than the
version a craft's citations need (`dyad/VERSION` was not bumped at #160 itself, only at #162) —
it stops a bad install outright; it does not by itself make a one-craft-at-a-time subset green,
which is why this paragraph is inference, stated, not a new guard (#178 falsification: a per-craft
`crafts_absent` would make the subset case green too, but is a separate, unscoped change to
`references.py`'s design).

## What stays elsewhere
The scripted, idempotent, tested install and the generated-file refusal are implementation
(Rule-11 properties 5 and 6, `syseng`, #162). The guard layout inside a craft is `guards.md`.
