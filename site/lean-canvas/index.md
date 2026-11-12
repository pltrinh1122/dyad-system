# Lean canvas: the Dyad System as a product

The foundation every pitch of the Dyad System traces to (`crafts/chronicle/rules/collateral.md` §5). It is not a
pitch. Each entry is one line, labelled **H** (hypothesis: a guess, claiming nothing as fact) or **E** (evidence: what
the repository shows, with its path or count). Accepted by the operator on the done-`Y` of d-work #672.

## Segmentation (`collateral-segmentation`, d-work #693)
A segment is a cell, or a named group of cells, on three axes (`crafts/chronicle/rules/collateral.md` §5). The axes are
the record's input, and each is **H** until two source trees that differ only in it show different anchor branches:
- **who holds me to it**: myself · team or employer · client · regulator or auditor · customers and users;
- **whose agent**: mine · people I answer for;
- **what it acts on**: code · hosts · content · data.

The twelve candidates (the ten of #672, consultants and solopreneurs) and the record's outcome for each. Every reading
is **H** unless it cites a tree.

| candidate | outcome | ground |
|---|---|---|
| `platform-ops` | cut | team or employer × mine × hosts |
| `regulated-engineering` | cut | regulator or auditor × mine × code, hosts |
| `agencies` (as #672 had it, "consultancies") | **too-broad**, split | client × mine and client × people I answer for differ at the anchor (S10): **agencies** keeps the staff cell, **consultants** the solo one |
| consultants (new) | cut | client × mine, from the split |
| `team-leads` | cut | team or employer × people I answer for |
| `org-leaders` | **overlapping**, merged into `team-leads` | the same cells; what separated them, scale, is not an axis: a candidate axis, **H**, to be split if `team-leads`' tree shows a different anchor for it |
| `security-audit` | **off-axis**, restated, then cut | defined by a function; its cells are regulator or auditor × people I answer for × code, hosts |
| `writers-analysts` | **off-axis**, restated, then cut | defined by a role; in-house: team or employer × mine × content, data. Freelance writers sit in `consultants` |
| `oss-maintainers` | cut | customers and users × people I answer for × code |
| `solo-developers` | cut | myself × mine × code |
| solopreneurs (new) | cut | customers and users × mine × code, hosts, content, data |
| `researchers` | **overlapping** with solopreneurs at customers and users × mine × data; kept | the separator, peers who judge reproducibility, is not an axis: a candidate value, **H** |
| (map) | **unspanned**: `employed-developers` added | problem classes K1–K3 are suffered by team or employer × mine × code, which no segment held: developers answering to their employer for code their own agent changed |
| (map) | idle-axis **undecided**, put to the operator | no two source trees yet differ in one axis value only: `platform-ops` and `regulated-engineering` differ in holder and in object, so neither axis is shown idle or live |

No candidate is **off-class**: every segment suffers at least one problem class.

## Problem classes (the projection's roots, grouped)
| class | roots | grouped because |
|---|---|---|
| **K1** the record does not travel with the change: who approved it, and what was checked | N5.1.1, N10.2.1.1 | both are something kept apart from the change |
| **K2** the result is not compared with what was intended | N4.1.1 | — |
| **K3** an approval is not bound to what it approved: the intent before the work, the version after | N1.1.1.2.1, N9.2.1.1 | both bind a yes to the thing it was given on |
| **K4** an action is not classed by what it risks before it runs | N2.1.1.1 | — |

## The segment × class table
The one record both perspectives are rendered from: [`by-segment.md`](by-segment.md) (a, segment → classes) and
[`by-problem.md`](by-problem.md) (b, class → segments). ● from the segment's own source tree · ○ a reading, **H**. `regulated-engineering`'s K2 is held in its
tree as a cause (N4.1.1, from R3.2), not as a root.

| segment | cells | K1 | K2 | K3 | K4 |
|---|---|---|---|---|---|
| `platform-ops` | team or employer × mine × hosts | ● | ● | ● | ● |
| `regulated-engineering` | regulator or auditor × mine × code, hosts | ● | ● | ● | ○ |
| `agencies` | client × people I answer for × code, hosts, content, data | ○ | ○ | ○ |  |
| `team-leads` | team or employer × people I answer for × code, hosts, content, data | ○ | ○ | ○ | ○ |
| `consultants` | client × mine × code, hosts, content, data | ○ | ○ | ○ |  |
| `employed-developers` | team or employer × mine × code | ○ | ○ | ○ |  |
| `solopreneurs` | customers and users × mine × code, hosts, content, data |  | ○ |  | ○ |
| `oss-maintainers` | customers and users × people I answer for × code | ○ |  | ○ |  |
| `security-audit` | regulator or auditor × people I answer for × code, hosts | ○ |  | ○ | ○ |
| `solo-developers` | myself × mine × code |  | ○ |  |  |
| `writers-analysts` | team or employer × mine × content, data |  | ○ |  |  |
| `researchers` | customers and users × mine × data (separated from solopreneurs by peers, a candidate axis value, H) | ○ |  |  |  |

**Corroboration.** Before the re-cut, the two perspectives disagreed in four places:
- (b) found K1–K3's sufferers in a cell no segment held, so `unspanned` added `employed-developers`;
- (a) had two segments in one cell, `org-leaders` and `team-leads`;
- (a) had two segments defined off the axes, `security-audit` and `writers-analysts`;
- (a) had one segment whose anchor branches differ, `agencies`.

After the re-cut, every segment suffers at least one class and every class's sufferers are segments on the map, so the
map is **corroborated**. That is internal consistency, **H**, until a reader's evidence refreshes the trees. The
thinnest segments are `solo-developers`, `writers-analysts` and `researchers`, one class each.

## Significance (`collateral-segment-significance`, re-run)
Every segment is **H** significant: each answers for an agent's work, an unchecked error costs it something real, and
it recurs within its week. `employed-developers`, new, answers to its employer for an outage or a defect, daily.

## The rank (`collateral-segment-rank`, re-run on the re-cut map)
The keys, in order:
- **harm per week:** cost × recurrence. Cost is 3 for a regulator, contract or safety; 2 for an outage, breach or
  money; 1 for reputation or time. Recurrence is 3 daily; 2 weekly; 1 rarely.
- **served:** 2 if served today, shown by evidence; 1 if in part; 0 if not yet.
- **nodes added:** **E** once projected. Before that, **H**, read as the axis values the segment's tree would test for
  the first time.

Every cost, recurrence and served score is **H**. Outcome: **tied**, at rank 4, which is put to the operator. The tie
does not hold up rank 3.

| rank | segment | harm per week | served | nodes added | state |
|---|---|---|---|---|---|
| 1 | `platform-ops` | 6 (2×3) | 2 | **E** 25 | worked: `platform-ops/` |
| 2 | `regulated-engineering` | 6 (3×2) | 2 | **E** 23 (4 known) | worked: `regulated-engineering/` |
| 3 | `agencies` | 6 (3×2) | 2 | **H** 2 new values: client, people I answer for | next |
| 4= | `team-leads` | 6 (2×3) | 2 | **H** 1: people I answer for | **tied** |
| 4= | `consultants` | 6 (3×2) | 2 | **H** 1: client | **tied** |
| 6 | `employed-developers` | 6 (2×3) | 2 | **H** 0 | |
| 7 | `solopreneurs` | 6 (2×3) | 1 (needs git and a CLI today) | **H** 1: customers and users | |
| 8 | `oss-maintainers` | 6 (2×3) | 0 | **H** 2 | |
| 9 | `security-audit` | 4 (2×2) | 1 | **H** 1 | |
| 10 | `solo-developers` | 3 (1×3) | 2 | **H** 1: myself | |
| 11 | `writers-analysts` | 3 (1×3) | 1 | **H** 2: content, data | |
| 12 | `researchers` | 2 (1×2) | 1 | **H** 2 | |

## The riskiest assumption
- **H** Platform engineers feel the risk of an agent acting on a host strongly enough to accept a `Y` before every
  change and again before it closes.

## Fit (`collateral-lean-canvas`), for `platform-ops`
Judged in the d-work #672 completion reply; this file records the canvas, not its verdict.

## Sections
Shared: `solution.md`, `cost-structure.md`, `unfair-advantage.md`. Per segment: `platform-ops/`, `regulated-engineering/`,
each with its own source `why-tree.md`. The canvas set's `why-tree.md` is their projection (§6), read for screening.
The two perspectives on the segment × class table: `by-segment.md` (a) and `by-problem.md` (b).
