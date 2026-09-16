# Rule-13: reuse over inference

**Intent:** Replace every recurring task done by inference with reusable code, imported rather
than authored whenever a fit candidate exists.
**Target:** a recurring task

## Boundaries (out of scope)
- What the code checks — the System Requirements Rule that owns it.
- Which implementation path — Rule-12. The manifest that declares the import — Rule-14.
  Package layout — Rule-11.
- Tools merely invoked (not redistributed with the package): Rule-14 library rows, any license.
- How an import is chosen, declared and scanned — import over author, pinning, kernel ecosystem
  first, the token scan: the syseng craft's `crafts/syseng/rules/imports.md` (#162). Rule-13 keeps
  the process: recurrence proposes code, and the criteria are the Operator's preferences.

## Conditions (triggers)
- The Agent performs the same operation by inference a second time.
- A plan proposes new code.
- A library entry is added to the manifest.

## Properties
1. **Recurrence proposes code.** The second occurrence of an inference task yields, in the
   plan, a code path (chosen per Rule-12). The Operator may decline it.
2. **Criteria are preferences.** `import-licenses` and `import-support` in
   `preferences-corpus/PREFERENCES.md`, Operator-owned, read here; what they select — import over
   author, every import declared and pinned, kernel ecosystem first — is the syseng craft's
   `crafts/syseng/rules/imports.md` (properties 1–3).

## Enforcement
Inference for the plan clause. The manifest guard (Rule-14, `dyad/guards/infra/manifest.py`)
fails an undeclared invocation or import; the scan's form is `crafts/syseng/rules/imports.md`
property 4.

## Provenance
Operator rule, 2026-09-13 (Architecture Rule 3). Falsified; see
`../falsification/rules/rule-13-reuse-over-inference.md`. Properties 2, 4, 5 and the scan
mechanics moved to `crafts/syseng/rules/imports.md` 2026-09-14 (#162); the kernel — recurrence
proposes code (p1), criteria are preferences (p2) — stays here.

Set: System Requirements (kernel; content: crafts/syseng/rules/imports.md).
