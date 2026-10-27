# chronicle guards

One guard, `episodes.py` (entity `episode`, corpus `infra`), meeting the guard contract (`crafts/sysarch/rules/guards.md`;
`dyad check --list` shows it as `chronicle/episodes`), its test at `../tests/guards/test_episodes.py`. It reads every
episode under `<site>/episodes/*.md` (`DYAD_SITE`, default `site`; absent store, one `warning: skip` line) and fails
what the record cannot hold — a missing header key, a malformed `time:` line, a footnote in no citation form, a
`path:` not in the tree, a `prov:` entry not in its provenance record, a `repo:` undeclared in `repos:` or without a
40-hex sha, a `repo:` a reachable clone does not hold. A `repo:` with no local clone (`DYAD_REPOS_DIR/<repo>`) is The
World: one `warning: … inference` line per episode, never a pass by assumption (`../rules/chronicle.md` §7).
