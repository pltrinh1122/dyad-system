# Host facts (syseng craft, Tended rule)

Read by Rule-14's kernel (`dyad/rules/RULE-14-system-infrastructure.md`, property 4, "Library and
The World": The World is observed, not pinned — a host's own filesystem layout, e.g. macOS's `/var`
-> `/private/var`, is such an observation) and by Rule-11's kernel
(`dyad/rules/RULE-11-distribution-structure.md`, property 2: an install destination is host
filesystem the package does not control). Distinct from `determinism.md` (the same input state
yields byte-identical output *over time* — one host, run twice) and `idempotence.md` (a script
converges): this rule is about *portability* — one code path giving the same answer regardless of
*which* host asked and *where in the code* it was asked from. Term (`host fact`):
`../vocabulary/CRAFT.md`. No guard of its own: `dyad/tests/test_hostadapter.py` and the
scratch-install assertions of `dyad/tests/test_package.py` are the checks (d-work #179; a
symlinked-path test proves `resolve` collapses one, since the macOS bug itself — a *different* host
resolving a *different* path differently — cannot be reproduced on this kernel's Linux host).

## Properties
1. **One place per host fact.** A host fact — path resolution (symlinks), filesystem
   case-sensitivity, line endings — is read through `dyad/scripts/hostadapter.py`, never inlined at
   a call site. A second inline occurrence of a fact this module already reads is Rule-13's
   recurrence: propose reusing (or extending) the function; never add a second inline call.
2. **Two functions, not a framework.** `hostadapter.py` is `resolve` and `ignore_patterns` (plus a
   `write_gitignore` helper); no registration or discovery mechanism, no per-OS conditional branch.
   A third host fact either fits one of the two functions or earns its own, new function, justified
   in the plan that adds it — never a generic hook (the line d-work #176's falsification, attack 3,
   drew against scope creep to hypothetical future OSes; #179 keeps it concrete).

## Inference, stated
Whether a given fact is a *host* fact (belongs here) or an *architectural* one (belongs in
`invariants.md`) is inference. Whether a call site has drifted back to an inline `.resolve()` is not
yet scanned mechanically (property 1's converse); today that is caught by the same falsification
discipline that found G5 (Rule-9), not by a guard. This rule's own falsification lives in the d-work
that added it (`agent-corpus/d-work/plans/179.md`), not a dedicated extraction record: unlike the
craft's other five rules, no text here was cut from an existing core Rule.
