# Falsification record — sysadmin craft rule `host-platform.md` (d-work #81)

**Claim:** maintaining and operating the host infrastructure abstraction — portability on macOS and
Windows — is the sysadmin craft's scope: which host platforms this system supports and what each one
demands, stated as obligation with a status per platform, as a Tended Rule no core kernel reads
(adjacent: Rule-11 p2, Rule-8); how a host fact is read in code stays the syseng craft's.

Attacks carried from plan #81 (`agent-corpus/d-work/plans/81.md`: the original plan of 2026-09-18,
the re-plan of 2026-09-23, revision 3 of 2026-10-15), by id:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| B1 | `crafts/syseng/rules/host-facts.md` already owns portability — it says "this rule is about *portability*" in as many words. Direct collision. | Confirmed | The sharpest attack: either a seam is cut or one owner yields. The seam is cut, from this side, in the rule's opening and Boundaries. |
| B2 | No seam is possible; both are "portability". | Refuted | syseng's target is implementation discipline — its two properties are about call sites and module shape. Which platforms the dyad runs on is not a property of the code. Different targets, so no shared ownership once both are stated. |
| B3 | `host-facts.md` property 2 forbids what this needs: "no per-OS conditional branch", drawn deliberately against scope creep to hypothetical OSes (#176 attack 3). | Confirmed, and the real cost | The line was drawn against *speculative* generality; the operator has now named two platforms. The rule does not reverse it: a supported platform earns a named function per fact, never a hook or a generic branch, and the rule says so in its seam paragraph and in *Where a divergence is recorded*. The reciprocal amendment to `host-facts.md` is a `backlog` row under #81's mandate. |
| B4 | Unimplementable: Windows has no POSIX shell, and `ops-script.sh`, `core.hooksPath` and `dyad/bin/dyad` all assume one. | Survives, scoped | A finding, not a refutation; it is why the scope is worth stating. The rule's contract item 2 inventories the files, read by shebang, and marks the platform unmet. No implementation is claimed. |
| B5 | Stating a scope the system cannot meet is worse than silence — it reads as a capability claim. | Survives, shapes the text | The platform table carries a status per platform — Linux verified; macOS and Windows in scope, unmet — and the rule says in its own words that a row is an obligation and never a capability. |
| B6 | #82 adds a fourth POSIX-shell file (`dyad/bin/dyad-python`) to the core's critical path, so the Windows contract recedes while this rule declares it in scope. | Survives, confirms B5's shaping | One more reason the status is stated per platform. The inventory in contract item 2 is the four core files plus the ops-script skeleton, verified 2026-10-15. |
| B7 | Writing the rule without the craft guard's Agent-process tokens is evasion of the Rule-4 guard, not compliance. | Refuted, scoped | The tokens mark text that binds the process; a Tended rule's proper voice is the practice's — what a platform must provide, where a divergence is recorded, who names a platform ("the operator's decision"). The token-free text is the better text. The three existing rules are not rewritten here; that is #88's own adjudication. |

Findings stated by the drafting, beside the table: the shell obligation splits — the two entrypoints
are `#!/bin/sh`, the two hooks and the skeleton `#!/usr/bin/env bash` — so a platform could meet one
half and not the other; the rule records both. The macOS row's one known fact (`/var` →
`/private/var`) is tested on Linux by a symlink proxy (host-facts rule), which is exactly why its
status stays unmet: nothing has been observed on a macOS host.

Disposition: see ledger #81.
