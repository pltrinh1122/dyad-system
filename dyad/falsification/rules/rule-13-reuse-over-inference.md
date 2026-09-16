# Falsification record — Rule-13 (reuse over inference), Architecture Rule 3 (ledger #76)

**Claim (operator, 2026-09-13):** minimize recurring inference cost with reusable code;
prefer importing (open-source, unrestrictive license, broad community support) over authoring.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Unrestrictive license" and "broad community support" are vague. | Confirmed | Preference keys `import-licenses`, `import-support` with defaults; Operator-owned. |
| 2 | Tokens are not observable in the corpus. | Survives | Recurrence is: the second occurrence triggers. |
| 3 | Imports are supply-chain surface. | Survives | Pinned Rule-14 row; the support criterion is the maintenance check. |
| 4 | Licenses cut two ways: Git is GPL and kernel. | Survives | Criteria apply to code redistributed with the package (Rule-11); invoked tools are Rule-14 rows, any license. |
| 5 | A niche need may have no candidate. | Survives | Author, stating what was searched. |
| 6 | Overlap with Rules 12 and 14. | Survives | 12 chooses the path; 13 chooses import or author within it; 14 declares. One-way each. |
| 7 | "Second time by inference" fires constantly. | Survives | Each recurrence is a proposal the Operator may decline; V1, V2, I1, I2 are the first batch. |

## Rule-5 pairwise statements (Rule-13 added)
- 13–1: none. 13–2: no event; a declined proposal is an `N`. 13–3: proposals are plans.
  13–4: block. 13–5: this statement. 13–6: three terms; `preference` gains a user. 13–8: an
  import that installs on the host is a host action (Rule-8 classes it). 13–9: candidates are
  claims, falsified. 13–10: import vs author framed per Rule-10. 13–11: redistributed code is
  package. 13–12: named. 13–14: named; Rule-14's `import` mention resolves to this term.
  Coherent, orthogonal.

## Rule-6: `recurring task`, `import`, `author` added, owner 13.

Disposition: see ledger #76.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
Enforcement names the manifest guard at `dyad/guards/infra/manifest.py` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
p2 (import over author), p4 (declared and pinned), p5 (kernel ecosystem first) and Enforcement's scan sentence moved to
`crafts/syseng/rules/imports.md`; the kernel keeps p1 (recurrence proposes code — the plan clause) and the criteria
preference (now p2), and its `Set:` line reads `System Requirements (kernel; content: crafts/syseng/rules/imports.md)`
(it was the last `System Architecture` label after #160). `import` and `author` leave the Agent vocabulary for the
craft's `CRAFT.md`; `recurring task` stays. Pairwise: 13–3 the plan clause unchanged; 13–12 named in Boundaries, one-way;
13–14 the manifest guard is Rule-14's, the scan's form the craft's; no other pair changes. Coherent, orthogonal.
Disposition: see ledger #162.
