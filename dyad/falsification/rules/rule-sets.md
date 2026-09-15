# Falsification record — naming the Rule sets (ledger #71)

**Claim (operator, 2026-09-13):** the existing Rules target Agent inference plus scripted
guards — "System Requirements"; the next set specifies the architecture of the infrastructure
and guards — "System Architecture".

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Rule-1 targets repo transactions, both parties, not Agent inference. | Refuted in part | "System Requirements" is the right name because it is not "Agent Requirements". |
| 2 | A set that "specifies the guards" shares ownership with Rules 1, 3, 4, 6, which own theirs (Rule-5 gap on arrival). | Confirmed | Boundary: Requirement owns *what* a guard checks; Architecture owns *where and how* it is built, run, deployed; never redefines a check. |
| 3 | Architecture Rules are not Agent Rules. | Refuted | They bind what the Agent may build (Rule-4 guard): same directory, continuous numbers, Rules 4/5/6 apply, Rule-5 sweeps across both sets. |
| 4 | Set membership by number range is fragile (Rule-7 pending). | Confirmed | Declared per Rule: `Set:` line under Provenance. |
| 5 | Rule-6 forbids defining the set names outside the vocabulary; the orphan check needs a Rule to use them. | Confirmed | Rule-5's target names both sets; two vocabulary rows, owner frame. |

## Rule-5 pairwise statement (Rule-5 target edited; `Set:` line appended to every Rule)
- The `Set:` line is provenance text, not a block field; Rule-4 counts are unchanged (checked).
  5–4: Rule-4 still recognizes; Rule-5 still relates; the set names change no ownership.
  Others unchanged. Coherent, orthogonal.

## Rule-6: two terms added, owner frame, used by 5.

Disposition: see ledger #71.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
The System Architecture set has left the core: its rules are the sysarch craft's (`crafts/sysarch/rules/`), Tended; the
kernels of Rules 11, 12, 14 and 20 stay System Requirements with a `Set: System Requirements (kernel; content: …)` line
(attack 4's survivor holds: membership is still declared per Rule). Two vocabulary rows reworded (owner frame, used by 5).
Disposition: see ledger #160.
