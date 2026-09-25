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

## Amendment — d-work #105 (2026-09-21, craft-contributed token map)

**Finding (workstation, intake):** `infrastructure_contrib.md` lets a craft contribute manifest
*rows* (Rule-11 property 2, #101), but `manifest.py`'s token map (`manifest_rules.txt`) is
core-only, with no equivalent. Three mechanisms verified against the live code: (1) `scan()`
treated every non-`.py` file under a scanned craft directory as shell text, so a craft's own
`guards/README.md` had its prose parsed for "invoked tokens"; (2) a craft's own script invoking a
tool only that craft knows about failed even after the craft declared the component, because the
token itself still resolved only against the core file; (3) `craft_python_dirs()` did not scan a
craft's `server/` directory — already an anticipated craft-file location
(`crafts/syseng/rules/invariants.md`'s own `exempt: crafts/*/server/*.py`) — so a sibling test's
import of the craft's own server module was misread as an undeclared third-party import.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | A craft's `manifest_rules_contrib.txt` could silently redirect an existing core token to a different component. | Refuted | The merge is `dict.setdefault` per component and `check`'s own `tok2comp.setdefault` per token — both first-wins; a core-resolved token is never reassigned, only an unresolved one gains a resolver. |
| 2 | Skipping every non-`.py`, non-`.sh`, non-shebang file in `scan()` could silently stop scanning a real script with an unconventional extension. | Survives, scoped | Every script this repo or a craft ships either ends `.sh` or opens with a shebang line (the same two signals `shebang()` already used); a file with neither is, by the same evidence, not a script the package or craft actually executes. |
| 3 | `manifest_rules_contrib.txt` is a *new* trust boundary, wider than `infrastructure_contrib.md`'s (a row can only ever be inert data; a token can silence a real undeclared-invocation failure). | Survives, scoped | The same boundary `REFERENCES_CONTRIB` and `infrastructure_contrib.md` already accept for craft-shipped data (Rule-11 property 2); a craft's own manifest gap is reported under the contributing craft's own name, never silently, exactly as those two already are. |

Mutation: `craft_manifest_rules()` (new, mirrors `craft_infra_rows()`), merged into `check_manifest()`'s
`rules` before `check()` runs; `scan()`'s file loop only treats `.sh` or a real-shebang file as
shell text; `craft_python_dirs()` gains `server/`.

Pairwise: 14–11: no package-layout change, the contribution mechanism is Rule-11 property 2's, not
a new one. 14–13: no import. 14–12: the fix's own tests are the check. 14–1: agent-zone file only.
No other concern moves. Coherent, orthogonal.

*Residue, not fixed here:* `crafts/sysarch/rules/manifest.md` gains the matching craft-contribution
sentence in its own, later PR (Rule-1: this file, the referent, before the craft rule, the
referrer — the same order this record's own #31 amendment already established for this exact
craft-zone file).

Disposition: see ledger #105.

## Amendment — d-work #175 (2026-09-25, profiles and the instance contribution)
**Finding:** the core manifest (`dyad/infrastructure/INFRASTRUCTURE.md`) shipped dyad-system's own
operating rows — Gitea, Docker Engine + Compose, GHCR, curl — to every install, and
`crafts/sysarch/rules/manifest.md` said the running manifest "stays core: its values are observed on
this system". Observed values are instance. Survivor: one kernel, two library profiles, one manifest
as a union; a seventh cell `profile` (`authoring` | `operating` | `both`, kernel rows `both`); the
instance contribution `<host path>/INFRASTRUCTURE.md` beside the craft contributions; the four
operating rows move there (`workstation-corpus/INFRASTRUCTURE.md` on dyad-system).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Two manifests (authoring, operating) are simpler. | Refuted | Contradicts property 1 (one manifest) and duplicates the kernel, which then drifts between them. |
| 2 | A profile cell alone fixes the shipped operating rows. | Refuted | The rows still ship in the core file; they must leave it, hence the instance contribution. |
| 3 | The instance contribution breaks "one manifest". | Refuted | The union is one manifest exactly as craft contributions already are (#101); a component declared twice across core, crafts and instance fails naming both (`test_duplicate_across_core_and_instance_fails`). |
| 4 | Moving rows breaks token mapping mid-sequence. | Survives as ordering | The instance file lands first (unread by the old guard); this PR reads it and removes the core rows together. The four rows' `manifest_rules.txt` lines leave the core too: a core map naming a component only one instance declares would fail on every other system. |
| 5 | An instance row with no token warns forever ("declared but no token maps"). | Refuted by construction | The scan covers the core and the crafts only; the package never invokes an instance row, so `check` exempts instance rows from that warning (`untokened`). Core and craft rows keep it. |
| 6 | A kernel row marked `authoring` or `operating` is a quiet split of the kernel. | Refuted | `check` fails a kernel row whose profile is not `both` (`test_kernel_row_must_be_both`); the invariant `profiles-fixed` pins the set. |
| 7 | A craft's existing six-cell `infrastructure_contrib.md` now reads as malformed. | Confirmed, accepted | No craft in this tree ships one; the form (`manifest.md` p1) now says seven cells for all three sources, and core 0.10.0 is the minor bump that announces it. |
| 8 | The union changes dyad-system's manifest. | Refuted | Same 15 components, same values; rows only moved (the guard reports `15 components`, as before), plus the added `profile` cell. |

Pairwise: 14–1: the instance file's path is Rule-1's host path, read, not redefined. 14–11: the
instance contribution is instance data outside every craft (property 1); the craft contribution
mechanism (property 2) is unchanged. 14–13: no import. 14–12: the guard's tests carry the change.
14–19: server software rows are still manifest rows — now instance rows where the server is the
system's own. New term `profile` (owner 14); `manifest` redefined as the union (Rule-6, used by 14
only; it still reads correctly). Others unchanged. Coherent, orthogonal.

Disposition: see ledger #175.
