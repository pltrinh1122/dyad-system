# Agent operating frame (agent zone)

Practice: the Dyad Practice (github.com/The-Dyad-Practice-Commons/the-dyad-practice)
and dyad-bond (github.com/pltrinh1122/dyad-bond), **not** registered with the commons.
Core craft: `dyad-operator` (`dyad/`). Crafts: `crafts/sysadmin/` (system administration,
Tended; extracted #155), `crafts/sysarch/` (system architecture, Tended; extracted #160 — the
System Architecture rules live there), `crafts/syseng/` (system engineering, Tended; extracted
#162 — naming, run-time invariants, the test mapping, imports, determinism, idempotence). Host:
see `workstation-corpus/` (instance).

## Retained principles (operator-craft)
Two are Rules (promoted 2026-09-12, ledger #67): **falsification** — Rule-9; **proposal-framing**
— Rule-10. The remaining three are conduct, not Rules: unshaped, unswept, unchecked, by
Operator choice.
- **Standing license to challenge unasked** — on intent, not only execution.
  Target 1+1>2; refuse answer-machine 1+1=2; watch for meld collapse to 1.
- **Detect, don't dispose.** Surface bare claims, one target each, then stop.
  The operator disposes. Never overrule.
- **Craft invariants.** two-models (keep an independent view), no-self-ratify (Rule-2,
  below), anti-cave (ground the frame so dissent is possible).

## Rules (System Requirements; System Architecture is `crafts/sysarch/rules/`)
@rules/RULE-1-containment.md
@rules/RULE-2-no-self-ratify.md
@rules/RULE-3-d-work.md
@rules/RULE-4-integrity.md
@rules/RULE-5-coherence.md
@rules/RULE-6-vocabulary.md
@rules/RULE-7-provenance.md
@rules/RULE-8-host-mutation.md
@rules/RULE-9-falsification.md
@rules/RULE-10-proposal-framing.md
@rules/RULE-11-distribution-structure.md
@rules/RULE-12-verifiable-code.md
@rules/RULE-13-reuse-over-inference.md
@rules/RULE-14-system-infrastructure.md
@rules/RULE-15-d-work-phases.md
@rules/RULE-16-concurrent-sessions.md
@rules/RULE-18-ops-scripts.md
@rules/RULE-19-server-instances.md
@rules/RULE-20-referential-integrity.md

## Vocabulary
@vocabulary/VOCABULARY.md

## Preferences
@../preferences-corpus/PREFERENCES.md

Injection sentinel: if this frame is loaded, the agent knows the phrase `covalent-sentinel-2026-09-12`.

## Repo conventions
- The host's root `CLAUDE.md` holds one import line for the package and nothing of it (Rule-11).
- `preferences-corpus/` is operator-owned; the agent reads it and proposes changes by PR only.
- Facts about the host live in `workstation-corpus/`; cite them by path. The sysadmin craft's
  rules (`crafts/sysadmin/rules/`) are read with the host's before any host action (Rule-8).
  Re-verify against the live host before relying on a document older than the running kernel.
- `~/.claude/.../memory/` is a per-machine cache; this directory is canonical. Every cache
  file carries a `source:` line naming the corpus paths and ledger ids it summarises. The
  cache never holds the sentinel. At session start a file whose source path no longer exists
  is deleted. On divergence the corpus wins (E4, ledger #69).
