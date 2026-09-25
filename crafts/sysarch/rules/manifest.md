# Manifest (sysarch craft, Tended rule)

Read by Rule-14's kernel (`dyad/rules/RULE-14-system-infrastructure.md`): the core Rule binds the
kernel (a CLI inferencing agent, Python at a pinned version, Git as a local repository; a hosted
git service is never kernel) and the kernel-only path (every guard runs on the kernel alone; the
evidence block is the merge evidence, Rule-2 Binding). This rule is the *form* of the manifest
those sentences read. Text moved from Rule-14 properties 1, 4 and 5 by d-work #160; a Tended rule —
any form, no Rule-4 block, no sweep. Terms (`library`): `crafts/sysarch/vocabulary/CRAFT.md`;
`manifest`, `kernel`, `The World`, `System Infrastructure`, `The Dyad System` stay Agent terms
(owner Rule-14). The core file, `dyad/infrastructure/INFRASTRUCTURE.md`, holds the kernel and the
authoring library — what every system needs to author with the core; a system's own operating rows,
observed on it, are instance and live in its instance contribution (property 1), never in the core
(#175: the core had shipped one system's operating rows to every install). Only the *form* is this
craft's.

## Properties
1. **One manifest.** Every dependency of The Dyad System on The World is a row in the one
   manifest: seven cells — component, partition (`kernel`, `library` or `The World`), version,
   purpose, license, replacement, profile (`authoring`, `operating` or `both`: which activity of the
   system needs it; one kernel serves both, so a kernel row is `both`). Nothing reaches The World
   except through a row. The one manifest is a union: the core file at the package root; every
   craft's own rows through `infrastructure_contrib.md` beside its root (Rule-11 property 2's
   craft-shipped contribution, #101); and the instance contribution, `<host>/INFRASTRUCTURE.md`
   under the system's host path (preference `host-path`, default `workstation-corpus`), holding its
   own operating rows as observed (#175). All three carry the same seven cells; a name already
   declared elsewhere fails, naming both sources — a component leaves the manifest when its craft,
   or its instance, does. An instance row needs no token (property 4): the package never invokes it.
2. **Library rows are replaceable.** Everything the package or the workflow invokes that is not
   kernel is a library row, and each names its replacement (what would be used if the component
   went away). CI, hosting and any runner are library adapters; the package must not depend on
   them to enforce a Rule.
3. **The World is observed, not pinned.** The OS and what it provides are recorded as observed
   (versions, the minimum the package was last verified on), never assumed. A kernel version
   change on the host is a manifest edit in the same d-work.
4. **Tokens map to rows.** Every interpreter, subprocess argv[0], shell command word in the hooks,
   `uses:` / `run:` word in the `dyad-*` workflows and third-party Python import maps, through a
   data file beside the guard (`dyad/guards/infra/manifest_rules.txt`), to a declared component; an
   unmapped token fails, a component with no token warns. (The scan's mechanics are implementation,
   `syseng` on #162; the *design* — a token is either mapped or refused — is this rule's.) A craft
   ships its own `manifest_rules_contrib.txt` beside its root, the same grammar, to map a token
   only its own files invoke — the token-map half of property 1's craft-shipped-contribution
   mechanism, which `infrastructure_contrib.md` alone only carried for rows (Rule-11 property 2,
   #105).

## Inference, stated
Whether a row's version, license and replacement are right stays inference (Rule-13 criteria,
until #162).
