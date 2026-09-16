# Falsification record — Rule-14 (System Infrastructure), Architecture Rule 4 (ledger #75)

**Claim (operator, 2026-09-13):** the System Infrastructure is the surface between The Dyad
System and The World and encapsulates integration dependency; kernel = Claude Code (or other
CLI agents), Python (pinned), Git (local, not hosted); library = everything not kernel.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "Git local, not hosted" vs GitHub running every guard today. | Confirmed | GitHub is library, an adapter; #24 is its named replacement; property 3 requires a kernel-only path (gap I2). |
| 2 | Bash is not kernel; all five guards sit on library. | Confirmed | Gap I1: migrate to Python with tests. |
| 3 | Where does the OS sit? | Survives | The World provides the kernel; the OS is observed, never pinned (property 5). |
| 4 | Claude Code's version cannot be pinned by us. | Survives | Recorded as observed with the minimum last verified. |
| 5 | "Everything else is library" is unbounded. | Survives | Only what the package or the Agent's workflow invokes. |
| 6 | A manifest nobody reads. | Survives | `infrastructure.sh` will read it (gap I5); until then it is the declared surface. |

## Rule-5 pairwise statements (Rule-14 added)
- 14–1: manifest is agent zone; no path change. 14–2: no event. 14–3: gaps are d-works. 14–4:
  block. 14–5: this statement. 14–6: six terms. 14–8: host actions cross the surface through
  declared entries; Rule-8 classes them, Rule-14 declares them; one-way each. 14–9: this record.
  14–10: gaps framed per Rule-10. 14–11: manifest moves to the package root with A1; Rule-14
  names Rule-11. 14–12: Rule-12 chooses paths; Rule-14 names what they may call. 14–13
  (pending): Rule-13 chooses library entries; Rule-14 declares them. Coherent, orthogonal.

## Rule-6: six terms added, owner 14.

## Rule-5 pairwise (#125, property 3 sentence added): 14–2: Rule-14 owns the kernel-only path and the adapter row; Rule-2 consumes it as evidence, no check semantics move (S4). 14–3: Rule-3 states the state, Rule-14 defines it. 14–11: the scratch-install test (Rule-11 p5) has no kernel-only path — gap `check --install`, noted, Rule-11's. 14–12/13 unchanged. Coherent, orthogonal. Record: `agent-corpus/falsification/ci-absent.md`.

## #138 amendment (property 3: the kernel-only path is the evidence for every merge)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 7 | Property 3 already had a kernel-only path; #125 made it evidence only "when the CI adapter is absent", so CI's mere presence overrode it. | Confirmed | Order inverted: `check --evidence` on the exact head is always the evidence; hosted CI corroborates when it runs. |
| 8 | "Unreachable hosting" stops the ratified merge, not the checks: no push, no PR merge. | Confirmed | Git is kernel, hosting is library: the merge executes locally (`git merge --no-ff`, message citing PR and Done-Y) and pushes on reconnect. |
| 9 | A self-run check is a self-report. | Survives, scoped | The evidence block carries head, tree, dirty flag and a sha256 the Operator can reproduce; a lying Agent is still inference (Rule-2 Enforcement). |
| 10 | Plan gate and fence read `origin/main`; offline that is stale. | Survives, scoped | They read the local `main`; the reply states "evidence at <sha>, hosting unreachable"; re-run on reconnect before push. |
| 11 | Local merges bypass the LAN server's future required checks (#16). | Refuted for now | None exist; when #16 lands the fallback applies only when *it* is unreachable, which #16 must state. |

Rule-5 pairwise (#138, property 3 reworded): 14–1: no zone or path change. 14–2: Rule-14 owns the path and the evidence block; Rule-2 consumes it as the binding evidence and classes the local merge as clerical — dependency, no overlap. 14–3: Rule-3 owns the completion reply; Rule-14 says what the reply pastes, not when it is asked. 14–4: block intact. 14–5: this statement. 14–6: one term, `evidence block`, owner 14. 14–8: no host action (git is repo transaction). 14–9: this record. 14–10: framed in plan #138. 14–11: `check --evidence` is a `package.py` subcommand the Rule-11 runner exposes; Rule-14 owns its semantics (S4). 14–12: the subcommand carries tests. 14–13: no import. 14–15/16: the local merge respects the transition table and plan gate on local `main`. 14–17: no surface. 14–18: no Operator-run command. 14–19: no server. Coherent, orthogonal. Record: `agent-corpus/falsification/self-ci.md`.

Disposition: see ledger #75.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/infrastructure.py` → `dyad/guards/infra/manifest.py`, data `infrastructure_rules.txt` → `manifest_rules.txt` beside it; the scan covers `guards/` and `tests/guards/` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.

## Amendment — d-work #154 (2026-09-14, craft reframe)
Boundaries: The Dyad System = Operator, Agent, the core craft, the Tended crafts, the instance
(vocabulary row edited, owner 14). Conditions: "a craft file". Manifest, kernel and evidence path
untouched.
| # | attack | result | survivor |
|---|---|---|---|
| 12 | "process kernel" (Rule-5 Homes) collides with Rule-14's `kernel`. | Confirmed | Rule-5 says "process kernel of a Rule that splits", never bare "kernel"; no new vocabulary row; Rule-14's `kernel` is untouched. |

Pairwise: 14–11: the system definition is Rule-14's term; the craft tree is Rule-11's. 14–1: a
Tended craft's files fall under the same manifest scan when they invoke anything — no zone or
path change now. No other concern moves. Coherent, orthogonal.

Disposition: see ledger #154.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
p1's six cells, p4 (library) and p5 (The World observed) moved to `crafts/sysarch/rules/manifest.md`; p4 here now points
there; the kernel (p2, p3 with the evidence block, Enforcement's run) stays. `manifest` stays an Agent term (its kernel
uses it; plan #160 attack 14); `library` moves. Enforcement's token-map mechanics stay pending #162 (D1). Pairwise:
14–11, 14–12 as above; 14–13 unchanged. Coherent, orthogonal. Disposition: see ledger #160.

## #168 amendment (2026-09-14): local CI first
| # | attack | result | survivor |
|---|---|---|---|
| A | Without PR-triggered CI a hook-skipping session merges unchecked. | Survives, scoped | The evidence block on the exact head is the gate (Rule-2 Binding, #138); CI was never the gate since #125. |
| B | `main` pushes still spend quota on ledger commits. | Confirmed | Workflows ignore `agent-corpus/d-work/**`. |
Pairwise: Rule-14 gains one clause on *when* hosted CI runs; Rule-14 owns the adapter's place, Rule-2 what a Y relies on, Rule-3 the plan gate's mechanism — no concern moves. Coherent and orthogonal with every other Rule as before.

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
Enforcement's scan mechanics (the token classes, the stdlib / internal / third-party classification, `import:<module>`)
moved to `crafts/syseng/rules/imports.md` property 4; Enforcement keeps that the guard runs, what it fails and what it
warns; Boundaries name the craft rule. `import` leaves the Agent vocabulary for the craft's. Pairwise: 14–11, 14–12
unchanged; 14–13: Rule-13 keeps the process clauses, the craft the selection and the scan — no shared concern.
Coherent, orthogonal. Disposition: see ledger #162.

## Amendment — d-work #31 (2026-09-16, pydantic admitted to the kernel)
d-work #30 evaluated a schema-definition flow for the syseng craft and found pydantic the fitter
library on every ground except one: `pydantic-core` is a compiled wheel, and putting it on the
kernel-only path (property 3) would break `check --evidence`'s reproducibility on a bare kernel.
Its reconciliation named the fork explicitly and left it to the Operator. The Operator disposed it:
pydantic joins the kernel by name.
| # | attack | result | survivor |
|---|---|---|---|
| 13 | Kernel is explicitly "minimal" (three items); a fourth, third-party package changes it from zero-install to "run one `pip install` first," eroding property 3's basis. | Survives, scoped | Python itself already requires an install step matched to a pinned version — kernel was never "nothing to set up," only "nothing beyond {agent, Python, git}, pinned and observed." Extending that discipline to one named, pinned package is a difference of degree, not kind, and is scoped to pydantic by name — not a standing invitation for the next library to self-nominate. |
| 14 | `pydantic-core` is a compiled Rust wheel; a compiled dependency has no place in a kernel meant to run "on the kernel alone." | Refuted | Both existing non-Python kernel members are themselves compiled binaries (the CPython interpreter, git). "No compiled code" was never the real constraint; property 3's actual constraint is reproducibility without a library/hosting adapter — installable, pinned, offline-capable once installed, exactly as Python's own interpreter is. |
| 15 | This reverses d-work #30's own recommended path (a stdlib emitter) without amending that record. | Confirmed | #30's reconciliation named this precise fork as the Operator's to decide. That record is not rewritten — it stands as the reasoning that led here — and gains one pointer line to this amendment so it is not read as still-current advice against pydantic. |
| 16 | Nothing in the corpus imports pydantic yet; naming it kernel before any code uses it is premature. | Survives, scoped | Classification and adoption are separate acts — Rule-12 still chooses the implementation path when code is actually written. This d-work only clears the kernel-membership question; the manifest row pins a real, current release (2.13.5, checked via `pip index versions pydantic` the same day) rather than a placeholder. |

Pairwise: 14–13: Rule-13's criteria (`import-licenses`, `import-support`) already clear pydantic as
an import; this amendment only reclassifies its Rule-14 partition, not Rule-13's selection process.
14–12: Rule-12 still chooses the implementation path when code is written; this removes one
objection to that future choice and decides nothing about it. 14–11: no package-layout change, the
manifest stays at the package root. 14–1: no zone or path change. 14–6: the vocabulary's `kernel`
row is edited in the same d-work to keep pace (Rule-6 master record: on divergence the vocabulary
wins and the Rule is a bug). No other concern moves. Coherent, orthogonal.

*Residue, not fixed here:* `crafts/sysarch/rules/manifest.md`'s own header paraphrases the kernel
list and is now stale by the same margin; craft zone, its own PR (Rule-1: change the referent,
Rule-14, before the referrer, the craft rule).

Disposition: see ledger #31.
