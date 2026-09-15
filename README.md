# dyad-system

The core craft of the Dyad Practice as this operator runs it: `dyad-operator`, the package a dyad
session installs — its operating frame, Agent Rules, vocabulary, guards, templates, run-books and the
falsification records behind every Rule. Package only: no instance state (no ledger, no host corpus,
no preferences values) lives here.

**Source.** Built by `dyad build` at release `v0.3.1` of the private development repository; the
archive attached to this repo's `v0.3.1` Release is that build, sha256
`d98cb26ce3292eebcc44299feb8c094a1e1aa38a3f740d2690cf79a45653c417`. Development, the d-work ledger and the falsification of
each change stay in the private repo; this repository is the distribution channel (Rule-14: a library
adapter, replaceable). Each release is republished here from the same archive.

**Install** into a repository: `python3.12 dyad/scripts/package.py install <path-to-repo>` (or, from
inside a repo that already has the package, `dyad/bin/dyad install <path>`) — writes `dyad/`, one
import line in the host's `CLAUDE.md`, a `.gitignore` seed and the `dyad-*` workflows, and never
overwrites a host file (Rule-11). Installing twice changes nothing. `dyad/bin/dyad check` runs the
guards on Python 3.12 and git alone.

**Read** `dyad/CLAUDE.md` first (the operating frame), then `dyad/rules/` (Rules 1–20, each with its
block and its falsification record under `dyad/falsification/rules/`), `dyad/vocabulary/VOCABULARY.md`
and `dyad/README.md`.

Practice: [the-dyad-practice](https://github.com/The-Dyad-Practice-Commons/the-dyad-practice) and
[dyad-bond](https://github.com/pltrinh1122/dyad-bond); not registered with the commons.
