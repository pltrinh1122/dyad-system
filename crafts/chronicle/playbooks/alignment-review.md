# Play-book: alignment review (the chronicle craft; d-work #696)

How the operator and the agent align on a canvas set's **target segments** and each target's **problems**: its problem
classes, its root-cause nodes and its anchor branch. The records it reads and writes are `../rules/collateral.md` §5
(segmentation, the two perspectives, significance, rank) and §6 (source trees and their projection). A run changes
records, the Targets and the trees, so each run is a d-work with its own plan and Done (Rule-3 of the core). It is
never monitoring.

## Inputs
A canvas set whose map is cut by `collateral-segmentation`, ranked by `collateral-segment-rank`, with its projection
and source trees judged by `collateral-why-tree`.

## Knobs
Each run states the value it uses; the default holds when a run states none. A tuning changes a default (Tuning, below).

| knob | values | default | what it changes |
|---|---|---|---|
| `order` | `top-down` · `bottom-up` | `top-down` | top-down agrees the classes, then picks targets, then reviews only the targets' problems; bottom-up reviews every segment's problems before any pick |
| `targets` | 1–3 | at most 3 | how many targets phase 2 may pick |
| `batch` | `no` · `yes` | `no` | `yes` asks phases 1 and 2 in one reply |
| `depth` | `targets` · `all` | `targets` | which segments' trees phase 3 reviews |
| `tree-first` | `always` · `never` | `always` | a target with no source tree gets one, derived independently (§6, Adding a segment), before phase 3 reviews it |

## Steps
Each phase shows one view, a page made for that phase alone, and ends in one question in plain form. The operator's
answer is entered verbatim as a `prompt` entry of the row (Rule-7), so nothing is ratified before the row's done-`Y`.
1. **Problem classes.** View: each class, with its wording, the roots grouped into it, the segments that suffer it,
   and the shared anchor. Question: "accept the classes, or amend?" An amendment changes the grouping, the wording
   or both, and the segment × class table and both surfaces follow.
2. **Targets.** View: the segment cards in rank order, each with its phase-1 classes, and any rank tie or untested
   axis the map carries. Question: "which segments are targets?" The pick is the operator's alone (the rank orders,
   never targets). A tie or an axis is settled only where it touches a pick.
3. **Problems per target.** Under `tree-first: always`, a target with no source tree first gets one, derived by a fresh
   drafter briefed with the segment, the anchor, §6's Steps and the gate, and given no other tree, then projected.
   View: one page per target, its source tree sliced to its selected roots, the branches that reach them, the anchor
   branch, and its symptoms in the segment's words. Question: "accept these as the target's problems, or amend a
   node?" An amended node is written as a superseding node in the source tree (§6, append-only), and the projection is
   rebuilt and judged.
4. **Record.** The canvas set's index gains a **Targets** section in the operator's words: per target, its classes,
   root node ids and anchor branch. The run record is written, and the row's Done question is asked on the PRs that
   carry both.

## Run record
Every run leaves `<canvas set>/reviews/<row>.md`, instance data in the canvas set, never in this craft. It holds:
- the knobs as set;
- each phase's question, the operator's answer by provenance entry, and what changed;
- the time each phase took, from the row's d-work trace;
- the agent's proposed tunings, each labelled hypothesis and citing the phase that suggests it.

## Tuning
A tuning changes a step or a knob's default by a craft-zone PR on the operator's prompt, citing the run records behind
it (the core's Rule-13: recurrence proposes, the operator disposes). A run proposes tunings; it never applies one to
itself.

## Evidence
The run record, the Targets section, and every tree the run derived or amended, each judged.
