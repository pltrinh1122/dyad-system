# Rule-14: System Infrastructure

**Intent:** Declare every integration dependency of The Dyad System on The World in one
manifest, split into a minimal pinned kernel and a library of replaceable adapters.
**Target:** the System Infrastructure

## Boundaries (out of scope)
- Which library to import and on what criteria — Rule-13.
- Which implementation path to take — Rule-12. Package layout — Rule-11. Zones — Rule-1.
- The Dyad System itself (Operator, Agent, the core craft, the Tended crafts, the instance):
  Rule-14 governs its surface, not its content.
- The manifest's form — one manifest of seven cells, library rows replaceable and naming their
  replacement, The World observed and never pinned: the sysarch craft's
  `crafts/sysarch/rules/manifest.md`. Rule-14 keeps the kernel and the kernel-only path, the
  sentences Rule-2's Binding relies on (#160).
- How the guard's token and import scan works — interpreters, argv[0], command words, `uses:`
  and `run:`, the stdlib / internal / third-party classification, `import:<module>` tokens: the
  syseng craft's `crafts/syseng/rules/imports.md` property 4 (#162).

## Conditions (triggers)
- A craft file or the Agent's workflow invokes anything not in the manifest, or imports a
  Python package not in the manifest.
- A kernel version changes on the host, or a library entry is added, replaced or removed.
- Every push and PR: `dyad/guards/infra/manifest.py` (Rule-14 owns it) runs, registered in
  Rule-11's runner (`package.py check`) and on the kernel-only path (property 3).

## Properties
1. **One manifest.** Every dependency on The World is a row in the manifest at the package
   root (`dyad/infrastructure/INFRASTRUCTURE.md`); its form — component, partition, version,
   purpose, license, replacement, profile — is `crafts/sysarch/rules/manifest.md`. The profile
   cell (`authoring`, `operating` or `both`; a kernel row is `both`) says which activity needs the
   row, and a system's own operating rows are its instance contribution, `INFRASTRUCTURE.md` under
   its host path (Rule-1), joined to the core's and the crafts' rows as one manifest (#175).
2. **Kernel.** Claude Code (or another CLI inferencing agent), Python at a pinned version, Git
   as a local repository, and pydantic at a pinned version — the one third-party package the
   kernel-only path may import directly. Minimal; versions recorded as observed, with the
   minimum the package was last verified on. A hosted git service is never kernel.
3. **Kernel-only path.** Every guard runs on the kernel alone: `package.py check --guards`,
   called by `dyad/hooks/pre-push` before every push (I2). CI, hosting
   and any runner are library adapters; the package must not depend on them to enforce a Rule.
   The kernel-only path is the merge evidence for every merge: `package.py check --evidence`,
   run by the main Agent on the exact head being merged, prints the evidence block (head sha,
   tree hash, working-tree cleanliness, every check and guard result, and a sha256 of those
   lines) that the completion reply pastes verbatim and the Operator may re-run on the same
   head to compare (Rule-2, Binding). Hosted CI corroborates and never replaces the block, and
   it is never a gate: it runs on `main` after a merge and on manual dispatch, never on a branch
   push or a PR event, and never on a ledger-only commit; the pre-push hook is the only check
   run before a merge (local CI first, ledger #168). When the hosting is unreachable a ratified merge executes locally — `git merge
   --no-ff` of the branch into `main`, commit message citing the PR and the Done-Y — and is
   pushed when the hosting returns; the plan gate and the fence read the local `main`, and
   the completion reply states "evidence at <sha>, hosting unreachable" (#138).
4. **Library and The World.** Everything else the package or the Agent's workflow invokes is a
   library row; The World is observed, not pinned (`manifest.md`, properties 2 and 3).

## Enforcement
`dyad/guards/infra/manifest.py` (I5, ledger #102; placed per Rule-11 property 1) runs on every push
and PR, registered in Rule-11's runner. It checks that the manifest is well-formed (seven cells;
partition `kernel`, `library` or `The World`; profile `authoring`, `operating` or `both`, a kernel
row `both`; no component declared twice across core, crafts and instance) and that every invocation and every third-party
Python import the package makes maps, through `dyad/guards/infra/manifest_rules.txt` (beside the
guard), to a declared component — an unmapped one fails, a component with no token warns; the
scan's mechanics are `crafts/syseng/rules/imports.md` property 4 (#117, #162). Rule-11's runner
invokes it; Rule-14 owns its semantics (S4). Whether a row's version, license and replacement are
right stays inference (Rule-13 criteria).

## Provenance
Operator rule, 2026-09-13 (Architecture Rule 4). Falsified; see
`../falsification/rules/rule-14-system-infrastructure.md`. Properties 1 (the six cells), 4 and 5
moved to `crafts/sysarch/rules/manifest.md` 2026-09-14 (#160); the kernel stays here. The token map
and import-scan mechanics of Enforcement moved to `crafts/syseng/rules/imports.md` 2026-09-14 (#162).
Property 1 gains the profile cell and the instance contribution 2026-09-25 (d-work #175): the core
manifest had shipped one system's operating rows to every install; see the same record, amendment #175.

Set: System Requirements (kernel; content: crafts/sysarch/rules/manifest.md, crafts/syseng/rules/imports.md).
