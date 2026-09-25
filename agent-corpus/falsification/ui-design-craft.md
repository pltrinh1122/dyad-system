# Falsification — a `design` craft for surface rendering

**Claim (Operator, 2026-09-25):** `design` should be included as a core craft, because surface
rendering would benefit from a holistic design system rather than the current ad-hoc approach to
modifying surface UIs.

Ledger #174. **Settled by the Operator before this record was written** — the settlement is below,
after the attacks that produced it. Nothing here is a recommendation.

## The craft play-book, applied
(Rule-3, Plan; `dyad/playbooks/craft-instantiation.md`)
Rule-3 makes this play-book mandatory for a prompt that opens a new body of work, so it runs before
this plan file rather than as an afterthought.

**Trigger.** Fires. `dyad craft list` shows five crafts — `dyad-operator` (core), `countersign`,
`sysadmin`, `sysarch`, `syseng` — and none practises design: none carries a token set, a layout
rule, a contrast criterion or a rendering vocabulary.

**craft-instantiation-criteria:** D1 classification — no fire, no sensitive data. D2 disposer — no
fire, one Operator. D3' import-or-extend — **decides author-or-import inside the default, and is the
live question**: see attack 3. D4 ledger coupling — no fire, its d-works would ref this ledger
constantly. D5 lifecycle — no fire, no separate beginning or end. D6 zone fit — no fire, it lives at
`crafts/design/`, zone `craft`.

**None fires → the play-book's default: a new craft instance in this system, not a new dyad
system.** The play-book ends at a plan-`Y`; the Agent never instantiates either on its own, and
this plan proposes no instantiation. The run-book `dyad/runbooks/craft.md` belongs to the
instantiation d-work, so this d-work's completion reply cites no events.

## What "ad-hoc" measures, today
| projector | lines | style blocks | distinct colour literals | font-family declarations |
|---|---:|---:|---:|---:|
| `sysarch/project_instances` | 425 | 1 | 29 | 0 |
| `sysarch/project_schema` | 332 | 1 | 20 | 0 |
| `sysarch/project_erd` | 257 | 1 | 13 | 0 |
| `sysarch/project_kanban` | 207 | 1 | 18 | 0 |
| `sysarch/project_entities` | 171 | 1 | 27 | 5 |
| `sysadmin/project_events` | 129 | 1 | 28 | 2 |
| `countersign/project_countersign` | 349 | 0 | 3 | 0 |
**94 distinct colour literals across six style blocks**, and no two projectors share a helper. That
is the ad-hoc approach the prompt names, quantified.

## Attacks
**Claim:** `design` should be included as a core craft, because surface rendering would benefit
from a holistic design system.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Take "core craft" literally. | **Refuted as stated** | The core craft is singular: Rule-11 property 1 and the vocabulary define `core craft` as "the craft every dyad system has, `dyad-operator`, at `dyad/`". There is no second one. The shapes actually available are a **Tended craft** (`crafts/design/`, zone `craft`) and, on one further condition, a **bundled craft** — a Tended craft the core release carries (#114). |
| 2 | Then bundle it, so every install has it — which is what "core" was probably reaching for. | **Refuted** | Rule-11 property 2: "A core Rule that cites a craft by path is the reason to bundle one … and it is **the only reason** the core's install may write outside its own root." No core Rule cites a design path; the three core Rules that contain the word "design" use it as an ordinary noun about their own kernels. Projection is a *Tended* rule, the sysarch craft's. So `design` ships as an ordinary Tended craft, installed by the systems that want it — and if a core Rule ever cites it, bundling becomes available then, on that reason. |
| 3 | D3': sysarch already owns surfaces — extend it instead of authoring a craft. | **Survives, and it carries a prerequisite** | Two different practices: sysarch owns what a surface *is* (parsed data, one projector per surface, the registry); design would own how it *reads* (tokens, layout, contrast, typography). But `crafts/sysarch/rules/projection.md` property 4 ends "Every data model and **every rendering decision** lives in the projector (#71 S4)" — an explicit ownership statement a design craft contradicts. **So the craft is admissible only if that sentence is amended first**, in the sysarch craft's own form, as its own d-work. Naming that prerequisite is the main result of this evaluation. |
| 4 | A craft that is only prose is not a craft. | **Confirmed — and it is the design's shape** | Rule-11 property 1 has a craft carry guard data, and Rule-12 property 1 wants a mechanical check. A `design` craft earns its place only with a guard — `design/tokens`, failing a projector that emits a colour, font or spacing literal outside the declared set. It has immediate work: 94 literals today. Without that guard this is a style document, and #135 already recorded what a corpus does with guidance nothing checks. |
| 5 | Measure the benefit: is the ad-hoc approach actually costing anything? | **Survives, scoped** | The projections are generated, never committed, and read by one Operator, so nothing user-facing is at stake and no incident in the log traces to a surface's appearance. The cost is legibility across surfaces and the per-surface re-decision the table above shows — real, and smaller than the prompt's "greatly". The honest case is consistency and a place to put rendering decisions, not a defect being fixed. |
| 6 | Sequence it against the alternative: one shared helper module inside sysarch would remove the duplication without a new craft. | **Survives, scoped — the cheaper half** | A shared `style.py` in sysarch would deduplicate the six style blocks and needs no Rule change, but it cannot bind `countersign`'s or `sysadmin`'s projectors, which live in other crafts and other zones; a craft can, because a craft is installable and a guard discovered by the runner reaches every craft's tree. The helper is the cheaper half of the same idea and is named here so the Operator can take it instead. |
| 7 | Do nothing: the surfaces work. | **Survives, scoped** | They do. This evaluation opens a `backlog` row and no more; nothing is instantiated, and the row waits for a prompt. |

**Verdict.** Not a core craft — that shape does not exist and bundling has no admissible reason
today. Admissible as a **Tended craft**, contingent on one prerequisite (attack 3's sentence in the
sysarch projection rule) and on carrying a guard rather than prose (attack 4). The benefit is
consistency, not a defect repaired.

## The Operator's settlement (2026-09-25)
The Operator disposed `N` and decided the question, so the evaluation stops here and the record
becomes the settlement rather than a recommendation. What was decided:
- **The surface stays self-contained.** That is the syseng craft's output form
  (`crafts/syseng/rules/determinism.md`, cited by `crafts/sysarch/rules/projection.md` property 3):
  a projection is self-contained, generated, never committed. Nothing about that changes.
- **The assets it embeds may be authored upstream**, by a separate craft named **`ui-design`**.
  The projector still inlines them, so the output form is untouched.
- **A separate craft, and not part of the core bundle** — which agrees with attack 2's finding for
  its own reason: Rule-11 property 2 admits bundling only where a core Rule cites the craft by path,
  and none does.
- **A bolt-on, carried by the ASG bundle downstream** rather than by this repo's bundle. The ASG
  bundle is the Operator's; this evaluation records the destination as given and asserts nothing
  about it.

**Attack 3's prerequisite falls away.** It rested on `projection.md` property 4's "every rendering
decision lives in the projector". With upstream-authored assets inlined by the projector, the
projector still emits every byte of its own surface, so the sentence is not contradicted and the
sysarch rule needs no amendment. The backlog row that would have amended it is dropped.

**Attack 4 stands and travels with the craft.** A craft that is only prose is not a craft
(Rule-11 property 1, Rule-12 property 1); `ui-design` earns its place with a guard over the assets
it authors, wherever it is installed. That belongs to the craft's own d-work, not here.

## Row opened from this record
#177, `backlog`: author `ui-design` as a bolt-on craft for the ASG bundle downstream — assets
authored upstream and inlined by each projector, with its own guard; not core, not in this repo's
bundle. `refs: 174, 165`. Not started; it waits for an Operator prompt.

## Disposition
The question is settled; this record holds how it was reached and what was decided. Nothing is
instantiated and no craft, Rule or projector changed.
Disposition: see ledger #174.
