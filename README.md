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
