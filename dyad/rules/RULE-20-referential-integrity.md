# Rule-20: referential integrity

**Intent:** Resolve every reference from one entity instance to another mechanically, by one
registered resolver per reference kind, so that no audit or guard bridges a reference by inference
where a resolver exists.
**Target:** a reference

## Boundaries (out of scope)
- What a reference means and whether it should exist — the Rule that owns the source entity
  (Rule-3 for rows, plans and incidents; Rule-8 for change-log rows; Rule-18 for ops-script
  headers; Rule-6 for terms; Rule-14 for the manifest; Rule-5 for the coherence of the Rule set).
  Rule-20 decides only that the target exists.
- Transaction-time gates that read a reference and its state — Rule-3's `prs.py` (a PR
  body's `d-work #N`); Rule-20 resolves references held in stores, never in a transaction.
- Resolvers that other Rules already own (`vocabulary.py`, Rule-6; `manifest.py`, Rule-14;
  `prs.py`, Rule-3; `frame.py`, the frame's imports): listed in the register as theirs, never
  re-implemented. Where a guard lives and what it declares — Rule-11 property 1 and
  `crafts/sysarch/rules/guards.md`.
- References into The World — a PR number, a hosting URL, a memory-cache `source:` line outside
  the repo (Rule-14; frame convention): listed as unresolvable, checked by inference, stated.
- Free prose: a mention of a Rule, a row or a path in a record's attack, an audit's body or a
  README is not a reference. Rule-20 reads parsed fields and, as prose, only Rule texts, the
  frame and the preference table.
- The register's design — one register, one resolver per kind, existence and nothing more, the
  surface sharing the guard's data, the leaf entities, craft-contributed rows — and which surface
  shows the edges: the sysarch craft's `crafts/sysarch/rules/references.md` and
  `crafts/sysarch/rules/projection.md` (#160). Rule-20 keeps the severity and the run, which
  Rule-3's completion evidence relies on.

## Conditions (triggers)
- Every push and PR: `dyad/guards/agent/references.py` runs through `package.py check`
  (`agent/references`) and on the kernel-only path (`check --guards`, Rule-14 property 3).
- An audit or sweep states that a reference resolves: it cites the guard's line, or states the
  kind as unresolvable by the register.
- A reference kind is added, or an entity's parser or store changes: the register adapts in the
  same d-work (`references.md`, When).

## Properties
1. **One register, one resolver per kind, existence only.** `references.REFERENCES` (data, in the
   guard) lists every reference kind with exactly one resolver — the guard's own, another Rule's
   guard (`guard:<corpus>/<entity>.py`, listed and not re-run), or `world` — which decides that
   the target instance exists and nothing more (`crafts/sysarch/rules/references.md`, properties 1–3).
2. **Severity.** An unresolved reference fails. A `world` kind prints one `warn … inference` line.
   A target store that is absent or holds no instance (a fresh install, Rule-11 property 5), or a
   kind whose parser is a craft guard no installed craft provides, skips its kinds with a printed
   line, never a failure.

## Enforcement
`dyad/guards/agent/references.py` (`check_package`; agent corpus, placed per Rule-11 property 1),
tests in `dyad/tests/guards/agent/test_references.py` (Rule-12), registered in Rule-11's runner as
`agent/references` and in `check --guards`; Rule-20 owns its semantics, the runner none (S4).
Whether an unresolved kind's inference is right, and whether a resolved reference names the
intended instance, is inference at falsification time.

## Provenance
Operator rule, 2026-09-14 (ledger #142). Falsified; see
`../falsification/rules/rule-20-referential-integrity.md`. Properties 1, 2, 3, 5, 6 and
conditions 2 and 4 moved to `crafts/sysarch/rules/references.md` 2026-09-14 (#160); the kernel
(severity, the run) stays here.

Set: System Requirements (kernel; content: crafts/sysarch/rules/references.md).
