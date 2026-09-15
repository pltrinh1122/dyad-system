# Imports (syseng craft, Tended rule)

Read by Rule-13's kernel (`dyad/rules/RULE-13-reuse-over-inference.md`: recurrence proposes code;
criteria are preferences) and Rule-14's (`dyad/rules/RULE-14-system-infrastructure.md`: one
manifest, the kernel, the kernel-only path). Text cut from Rule-13 p2, p4, p5 and from the
Enforcement sections of Rules 13 and 14 by d-work #162 (plan (a)4). Terms (`import`, `author`,
arriving from the core vocabulary): `../vocabulary/CRAFT.md`. The guard is Rule-14's,
`dyad/guards/infra/manifest.py` (it does not move; only the prose does).

## Properties
1. **Import over author.** *"When a candidate meets the criteria, import it. Author only when
   none does, and the plan states what was searched."* (Rule-13 p2.) The criteria are the
   preferences `import-licenses` and `import-support` (Rule-13 p3, kept core).
2. **Every import is declared and pinned.** *"A Rule-14 library row with version, license and
   replacement."* (Rule-13 p4.)
3. **Kernel ecosystem first.** *"Python packages before tools outside the kernel."* (Rule-13 p5.)
4. **The token scan.** From Rule-13's Enforcement: the manifest guard *"refuses any invocation
   token — shebang interpreter, `subprocess` argv[0], hook and workflow command words — that maps
   to no declared component"*. From Rule-14's: *"Python `import` statements are scanned too,
   classified stdlib / package-internal / third-party; only third-party needs a row (token
   `import:<module>`), and an undeclared one fails (#117)."* The map is data,
   `dyad/guards/infra/manifest_rules.txt`; a declared component with no token warns.

## Inference, stated
Whether a row's version, license and replacement are right stays inference (Rule-13 criteria);
whether a candidate *fits* is a claim the plan falsifies.
