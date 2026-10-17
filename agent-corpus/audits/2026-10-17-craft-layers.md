# The craft layer — base, system, admin, practice: the Operator's taxonomy re-run against the tree (2026-10-17)

*d-work #341, seat `ds-cabinet-cloud-7`. Companion to `2026-10-17-dyad-taxonomy.md` (#340), which classifies the
files inside the core craft; this audit classifies the **crafts** against each other. Tree `8b7fc27` on `main`
(`dyad-operator` 0.11.0; sysarch 0.3.0, syseng 0.4.0, sysadmin 0.3.0, countersign 0.3.0, disclosure 0.1.0;
`BUNDLE.md` v0.14.0). Every claim came from the Operator's side thread and was re-run here, never trusted (§1);
every count is a command on `8b7fc27`. Detects, classifies and costs; disposes nothing; executes nothing.
Falsification: `../falsification/2026-10-17-craft-layers.md`.*

**Disposition:** disposed by the Done-`Y` of d-work #341 (Rule-2; see ledger #341).

## 1. The chain, re-run

| # | the Operator's claim (compressed) | re-run result | what moved |
|---|---|---|---|
| 1 | Four crafts fill three layers named by what each does for the Operator: `base` (`dyad-operator`) makes a craft exist and runs the process; `system` (`sysarch`, `syseng`) makes a craft well-formed; `admin` (`sysadmin`) makes host operation admissible and portable in practice, not in state (one host path, one change log, one run-book and events store per system). The layers are a classification, not the tree. | **held** | "one per system" verified: `host-path` is one preference value (`preferences-corpus/PREFERENCES.md`); `sysadmin/changelog` reads one `<host>/CHANGELOG.md`; run-books and their events live under one `<host>/runbooks/`. |
| 2 | "Core" was a misnomer for the four together; the system's word for that set is the bundle (`BUNDLE.md` v0.14.0). `dyad-operator` is base: the only craft every other presupposes, the only one that may carry Agent Rules (Rule-4), the only one that can mint, check, export and install a craft; sufficient to make a craft exist, not well-formed. | **held** | `dyad craft new \| check \| export \| install` are `dyad/scripts/craft.py` (core); every craft's `MANIFEST.md` `requires:` names `dyad-operator` and nothing requires a Tended craft; Rule-4 keeps Agent Rules in `dyad/rules/`; `BUNDLE.md` names exactly the four. |
| 3 | Rule-11 property 2 is unmet twice: a core Rule citing a craft by path is the ground for bundling; Rules 11–14, 16, 20 cite `sysarch` and `syseng`, Rules 8, 18, 19 cite `sysadmin`; only `sysadmin` declares `BUNDLED_WITH_CORE`. | **held, widened** | The declaration exists once, `crafts/sysadmin/guards/changelog.py:36`. Citations by path (backticked `crafts/<c>/…` in Rule text, resolved by `rule.text->path`): **`sysarch` — Rules 5, 7, 11, 12, 14, 16, 18, 20 (23 tokens)**; `syseng` — 11, 12, 13, 14 (21); `sysadmin` — 5, 8, 11, 18, 19 (14); `countersign` — 3 (5); `disclosure` — 0; `lan-git` — 0. Eight Rules cite `sysarch`, not six. |
| 4 | `sysarch` and `syseng` stay two crafts; consolidation priced (six Rule kernels' `Set:` lines, projectors re-homed, two tags retired) and declined: different kinds of knowledge at different change rates. | **conclusion survives; reason refuted** | Since 2026-09-14, their common birth: sysarch 15 commits, 10 `VERSION` bumps, 8 tags, 8 commits to `rules/`; syseng 11, 7, 5, 7. The rates are alike. Five `Set:` lines name sysarch or syseng content (Rules 11, 12, 13, 14, 20); the sixth (Rule-19) names sysadmin. Two crafts rests on kind of knowledge, which is inference. |
| 5 | "Tended" is not a fourth layer; every non-base craft is Tended; the Agent/Tended cut runs between `base` and everything else. | **held** | Vocabulary `Tended craft`: "any craft other than the core craft"; Rule-4 Boundaries. |
| 6 | The fourth layer is `practice`: a Tended craft no core Rule cites, so optional, never bundled, never required. `disclosure` fits. "practice" over "plug-in". | **held, with a caveat** | `disclosure` is cited by no Rule and no `Set:` line. But the core play-book `dyad/playbooks/ds-report-incidents.md` (read by Rule-3) cites `crafts/disclosure/rules/redaction.md`, `<instance>/disclosure/pseudonyms.md` and runs `dyad project disclosure` (lines 36, 42, 59): a core *procedure* depends on a craft the core does not ship, which Rule-11 property 2's letter (a core *Rule*) does not reach. §3 L6. |
| 7 | `countersign` consolidates into `dyad-operator`: its adopted content is process, which only the base may own; costs as #340 P10 priced; open question — three systems adopt `interaction.md`; reopens #232's hold for `countersign` and `disclosure`. | **as #340 P10 verified; costed there** | No guard module; 23 files; `requires: dyad-operator>=0.10.1`; no tag; Rule-3 cites it five times; `references.craft_state` warns, never fails, on a receiving system. #340 P10 priced bundle against consolidate and recommended neither; the Operator's direction is consolidate (§3 L4). |
| 8 | Operator profiles: `base` any Operator of a deployed system; `system` the extending Operator; `admin` the host-operating Operator, including on a second device; `practice` the Operator who wants that practice. Gap: no per-host model of the host corpus. | **held, sharpened** | `crafts/sysadmin/rules/host-platform.md`: Linux **verified**, macOS and Windows **in scope, unmet**. "A second device" is a Linux-only fact today; one `host-path` per system means a second host has no corpus of its own (§3 L5). |

## 2. The layer table

| craft | layer | does, for the Operator | cited by core Rules (by path) | bundled | released (tags) | Operator profile |
|---|---|---|---|---|---|---|
| `dyad-operator` (`dyad/`) | **base** | makes a craft exist (`dyad craft new`), checks, exports and installs it; runs the d-work process; the only carrier of Agent Rules | — (it is the citer) | is the core | yes (`dyad-operator-v*`) | any Operator of a deployed system |
| `sysarch` | **system** | how infrastructure and guards are built, run and deployed: distribution, guards, manifest, projection, references, stores | 5, 7, 11, 12, 14, 16, 18, 20 (23 tokens) | **no** | yes (8) | the extending Operator |
| `syseng` | **system** | how code is written so it stays verifiable: naming, invariants, verifiable code, imports, determinism, idempotence, host facts, failure | 11, 12, 13, 14 (21) | **no** | yes (5) | the extending Operator |
| `sysadmin` | **admin** | host actions, ops scripts, server instances, host install and platform | 5, 8, 11, 18, 19 (14) | yes (`changelog.py`) | yes (5) | the host-operating Operator |
| `countersign` | adopted process (claim 7: belongs to **base**) | the interaction model (primitives, answer grammar, lifecycles, mode) three systems adopt; a self-diagnostic | 3 (5) | no | no (held, #232) | — |
| `disclosure` | **practice** | an anonymized, redacted incident report for a third party | none (one core play-book) | no | no (held, #232) | the Operator who wants that practice |

Reading the table: the three bundled-or-not cells marked **no** against a non-empty citation column are the two
instances of Rule-11 property 2's disagreement (claim 3) and the `countersign` case #340 P10 priced. The one
`practice` row is the only Tended craft whose citation column is empty at the Rule level.

## 3. Proposals (Rule-10 form; costed by zone and PR; none executed)

**L1 — the layer as a classification, zero code.**
- *Path.* `dyad/README.md`'s craft rows gain a `layer` column (`base`, `system`, `admin`, `practice`); the Agent
  vocabulary gains one row, **`practice`** — *a Tended craft no core Rule cites by path: optional, never bundled,
  never required for the base to run or a craft to be well-formed* — and the `craft` row references the four
  layer names. Agent zone, one PR; Rule-6's trigger: the record names the `used by` Rules of `craft` (1, 4, 5, 11,
  14) and states each still reads. No code, no guard, no craft edit.
- *Counter.* A classification nothing checks drifts (the README already has, #340 P3); a vocabulary row for a
  layer with one member is premature.
- *Reconciliation.* The test is mechanical in principle — `rule.text->path`'s tokens per craft, printed by
  `git grep` — and could become a `TREE_INVARIANT` later if the Operator wants it checked; the row is what makes
  the test citable. `disclosure` is the member today; the test, not the member, is the row.

**L2 — bundle every craft a core Rule cites.**
- *Path.* `BUNDLED_WITH_CORE = True` in `crafts/sysarch/guards/registry.py` and in one syseng guard
  (`naming.py`); sysarch 0.3.0 → 0.4.0, syseng 0.4.0 → 0.5.0 in **one craft-zone PR** (one zone); `BUNDLE.md`'s
  two rows follow in an infra PR after the tags. `dyad build` then carries three crafts and `dyad install` writes
  them, so a core-only install stops printing a `warn` per citation (44 for the two) and `distribution.md`'s
  receiving-instance order paragraph (#178) describes a case that no longer arises.
- *Counter.* The core archive grows from one tree to four; an Operator who wanted the base alone cannot have it;
  and the declaration's home is a guard module, which `sysarch` has one of and `syseng` three — the choice is
  arbitrary, as it was for `sysadmin`.
- *Reconciliation.* Rule-11 property 2 already states the invariant: "what the core ships and what its own
  Rules depend on must not disagree". The base alone has never been installable green (`distribution.md`, #178);
  bundling makes the archive say so. Released crafts, so Rule-11's release form applies to the tags that follow.

**L3 — keep `sysarch` and `syseng` apart, on the right reason.**
- *Path.* No change; the record states that the two-crafts conclusion rests on kind of knowledge (design versus
  engineering), not on change rate, which the history shows to be alike (§1 claim 4).
- *Counter.* Equal rates and a shared birthday are evidence *for* one `system` craft; the consolidation cost is
  five `Set:` lines and citations in Rules 11, 12, 13, 14, 20 (records and a Rule-5 statement each), five projectors
  re-homed under one `projectors/`, two tag series retired.
- *Reconciliation.* The cost is a Rule-set edit of five kernels for a labelling gain; the layer column (L1)
  already says they are one layer. Reopen on a change in what the crafts *are*, not in how often they change.

**L4 — consolidate `countersign` into the base.**
- *Path.* #340 P10's counter, now the Operator's direction: define the four terms in the Agent vocabulary
  (today referenced by craft name), move the answer grammar and the two lifecycles' text into Rule-3 where
  Rule-3 does not already carry them, drop the five path citations, and retire or re-home `schema.md`,
  `self-diagnostic.md`, `levels.py`, the projector and the eight templates (Rule-4 keeps Tended rules out of
  `dyad/rules/`; #160 moved projectors out of the core). Agent zone (Rule-3 and Rule-6 edits with records, a
  Rule-5 statement), craft zone (the craft's removal), and the moved text ships with the next core tag —
  Rule-11's release form, not only a plan-`Y`. Reopens #232's hold.
- *Counter.* `interaction.md` ¶1 names three adopting systems (dyad-system, dsys, countersign-system) and the
  adapters serve the other two; consolidating here discards the shared model's only home. The open question
  the Operator named — a home for the shared model outside this repo first — is the ordering constraint.
- *Reconciliation.* The direction is the Operator's; the order is the counter's: find or make the shared
  model's home, then consolidate what dyad-system adopts. A d-work of its own, outside #340, #341 and #336.

**L5 — the multi-device gap.**
- *Path.* Named, not designed: one `host-path` per system means one host corpus; `host-platform.md` verifies
  Linux only. An Operator on a second device has no change log, run-book store or host rules of that device's
  own. A `sysadmin`-craft and preferences finding for the Operator to open as a row.
- *Counter.* The second device is a second *system* (its own instance, its own host corpus) under the
  architecture as it stands; nothing is missing, only unnamed.
- *Reconciliation.* The counter is the first design to test when the row opens; the audit records only that
  the gap is real at the preference's cardinality.

**L6 — a core play-book depends on a `practice` craft.**
- *Path.* `dyad/playbooks/ds-report-incidents.md` cites `crafts/disclosure/` and runs `dyad project
  disclosure`. Either the play-book states the install it needs (`dyad craft install crafts/disclosure`) as its
  first step, or Rule-11 property 2's ground ("a core Rule that cites a craft by path") widens to the core's
  play-books and `disclosure` is bundled. Agent zone (the play-book) or a Rule-11 amendment with its record.
- *Counter.* A play-book is read on a prompt (its trigger), so the Operator who asks for the report is the
  Operator who wants the practice; stating the install is enough and bundling over-reaches.
- *Reconciliation.* Take the counter: one line in the play-book; the property's letter stays. Named because
  the `practice` test (L1) rests on "cited by no core Rule", and this is the one core citation that is not a
  Rule's.

## 4. Not observed
No shape was prototyped. `dyad build` with `sysarch` and `syseng` declared bundled was not run; the archive's
size and `dyad install`'s behaviour under three bundled crafts are inferred from `bundled_crafts` and
`core_roots` in `dyad/scripts/package.py`. The other adopting systems of `interaction.md` were not read.
