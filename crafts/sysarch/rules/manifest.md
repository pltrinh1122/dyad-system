# Manifest (sysarch craft, Tended rule)

Read by Rule-14's kernel (`dyad/rules/RULE-14-system-infrastructure.md`): the core Rule binds the
kernel (a CLI inferencing agent, Python at a pinned version, Git as a local repository; a hosted
git service is never kernel) and the kernel-only path (every guard runs on the kernel alone; the
evidence block is the merge evidence, Rule-2 Binding). This rule is the *form* of the manifest
those sentences read. Text moved from Rule-14 properties 1, 4 and 5 by d-work #160; a Tended rule —
any form, no Rule-4 block, no sweep. Terms (`library`): `crafts/sysarch/vocabulary/CRAFT.md`;
`manifest`, `kernel`, `The World`, `System Infrastructure`, `The Dyad System` stay Agent terms
(owner Rule-14). The running manifest, `dyad/infrastructure/INFRASTRUCTURE.md`, stays core: its
values are observed on this system; only its *form* is this craft's.

## Properties
1. **One manifest.** Every dependency of The Dyad System on The World is a row in the one
   manifest at the package root: six cells — component, partition (`kernel`, `library` or
   `The World`), version, purpose, license, replacement. Nothing reaches The World except through
   a row.
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
   `syseng` on #162; the *design* — a token is either mapped or refused — is this rule's.)

## Inference, stated
Whether a row's version, license and replacement are right stays inference (Rule-13 criteria,
until #162).
