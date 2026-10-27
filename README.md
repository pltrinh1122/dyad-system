# dyad-system

**The Dyad System** is a way for one person to delegate real work to an AI agent and stay accountable for it.

## Why

A human Operator wants the most effect on the world through work, within a budget of time and cost. The Operator is
accountable for that effect, so every output delegated to an agent must be evaluated and validated — and that spends
the Operator's daily attention, a budget that cannot grow.

The answer here is an Operator–Agent **dyad**. The Agent proposes, tests its own claims and does the work; only the
Operator decides, `Y` or `N`. Guards check the record mechanically, so the Operator's attention goes to decisions,
not to re-checking. The target is 1+1>2: the pair achieves more than either alone, and neither voice absorbs the
other.

It is not an autonomous agent, not a general workflow engine or CI product, and not an affiliate of the practice
commons.

## Who it is for

An Operator who delegates building and operating work to an AI agent and stays accountable for the result. It runs on
a CLI inferencing agent — Claude Code or another — with Python 3.12 and git.

## How it works, in brief

Every piece of work is a **d-work**. The Operator's prompt opens it; the Agent answers with a plan, and nothing
changes until the Operator says `Y` to that plan. The Agent then does the work, shows the evidence, and asks whether it
is done; only the Operator's `Y` closes it. The Rules that say so live in `dyad/rules/`, and the guards that check them
run before every push.

This repository authors the core craft `dyad-operator` (`dyad/`) and the Tended crafts it ships (`crafts/`). This
instance also uses the system to administer the Operator's workstation (`workstation-corpus/`).

## Start

    dyad/bin/dyad install <path-to-repo>     # install the core craft into a repository
    dyad/bin/dyad check                      # run the invariants, the tests and every guard

## Read next

- [`site/identity.md`](site/identity.md) — what this system is, as a record an agent can parse.
- [`site/what-why-how.md`](site/what-why-how.md) — the system in three layers, each claim footnoted.
- [`dyad/CLAUDE.md`](dyad/CLAUDE.md) — the operating frame, then [`dyad/README.md`](dyad/README.md).

Practice: [the-dyad-practice](https://github.com/The-Dyad-Practice-Commons/the-dyad-practice)
and [dyad-bond](https://github.com/pltrinh1122/dyad-bond); not registered with the commons.

## Reference (for agents and contributors)

The authoring repository of one Dyad Practice system: the core craft `dyad-operator` (`dyad/`)
and the four Tended crafts it ships — `crafts/sysadmin/`, `crafts/sysarch/`, `crafts/syseng/`,
`crafts/cabinet/` — developed here under their own Rules. The d-work ledger, provenance, incident log and
falsification records live in `agent-corpus/`; the Operator's preferences in
`preferences-corpus/`. The root `CLAUDE.md` holds one import line; the operating frame is
`dyad/CLAUDE.md`.

**Identity.** The facts above, as data: [`site/identity.jsonld`](site/identity.jsonld), the JSON-LD identity record;
[`site/identity.md`](site/identity.md), its schema and how to read it; and
[`site/what-why-how.md`](site/what-why-how.md), its expansion (the record's `subjectOf`), pinned to a commit with a
footnote per claim. Every recurring decision of the system is a decision-making-criterion record under `dyad/dmc/`,
`crafts/<craft>/dmc/` and `agent-corpus/dmc/`, shaped by `dyad/dmc/schema.md`.

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
