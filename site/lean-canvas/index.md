# Lean canvas: the Dyad System as a product

The foundation every pitch of the Dyad System traces to (`crafts/chronicle/rules/collateral.md` §5). It is not a
pitch. Each entry is one line, labelled **H** (hypothesis: a guess, claiming nothing as fact) or **E** (evidence: what
the repository shows, with its path or count). Accepted by the operator on the done-`Y` of d-work #672.

## The segment map
Each segment judged by `collateral-segment-significance` (accountable for an agent's work; an unchecked error costs
something real; it recurs within the segment's week). Every reading is **H** unless marked otherwise.

| segment | reading | served today |
|---|---|---|
| `solo-developers` — developers running a CLI coding agent on repositories they own | **H** significant | **E** yes: the core craft, `dyad/` |
| `oss-maintainers` — open-source maintainers receiving agent-written contributions | **H** significant | **H** in part: review and provenance on their side only |
| `team-leads` — engineering leads answering for a small team's agent-written changes | **H** significant | **E** yes, one operator per dyad: `dyad/rules/RULE-2-no-self-ratify.md` |
| `platform-ops` — platform, DevOps and SRE engineers letting agents act on hosts | **H** significant | **E** yes: `dyad/rules/RULE-8-host-mutation.md`, `crafts/sysadmin/` |
| `regulated-engineering` — engineers who must show who approved what | **H** significant | **E** in part: every approval kept verbatim, `dyad/rules/RULE-7-provenance.md`; no certification is claimed |
| `security-audit` — security and audit teams reviewing agent activity | **H** significant | **E** in part: the record exists; no audit tooling is claimed |
| `agencies` — consultancies answering to clients for agent-assisted work | **H** significant | **E** yes, as `team-leads` |
| `researchers` — researchers needing reproducible, attributable agent-assisted work | **H** significant | **E** in part: provenance and decision records, `dyad/dmc/` |
| `writers-analysts` — writers, analysts and marketers delegating drafts to agents | **H** significant | **E** in part: `crafts/chronicle/`; it needs git and a CLI today |
| `org-leaders` — leaders answering for an organization's adoption of agents | **H** significant | **E** not yet: one operator per dyad, no organization view |

## The rank (`collateral-segment-rank`, d-work #685)
Keys, in order:
- **harm per week**: the cost of an unchecked error times its recurrence. Cost is 3 for a regulator, contract or safety; 2 for an outage, breach or money; 1 for reputation or time. Recurrence is 3 daily, 2 weekly, 1 rarely within the week.
- **served**: 2 if served today with evidence; 1 if in part; 0 if not yet, or only hypothesised.
- **nodes added**: how many nodes the segment's source tree adds to the projection. It is counted (**E**) once projected, and a hypothesis before.

Every cost, recurrence and served score is **H**. Outcome: **ranked**. It orders the work; the go-to-market picks the target.

| rank | segment | harm per week | served | nodes added | state |
|---|---|---|---|---|---|
| 1 | `platform-ops` | 6 (2×3) | 2 | **E** 25 | source tree and canvas, `platform-ops/` |
| 2 | `regulated-engineering` | 6 (3×2) | 1, **re-read 2** | **E** 23 (4 known) | source tree and canvas, `regulated-engineering/` |
| 3 | `team-leads` | 6 (2×3) | 2 | **H** many: answering for agents other people ran | next |
| 4 | `agencies` | 6 (3×2) | 2 | **H** few: its client is mostly N8.3's auditor | |
| 5 | `oss-maintainers` | 6 (2×3) | 0 | **H** | |
| 6 | `security-audit` | 4 (2×2) | 1 | **H** | |
| 7 | `solo-developers` | 3 (1×3) | 2 | **H** | |
| 8 | `writers-analysts` | 3 (1×3) | 1 | **H** | |
| 9 | `org-leaders` | 3 (3×1) | 0 | **H** | |
| 10 | `researchers` | 2 (1×2) | 1 | **H** | |

- **H** `regulated-engineering` was scored served 1 ("in part") on the map. Its own canvas names what the system holds today against its top root (an approval kept verbatim and bound to a head, `dyad/rules/RULE-7-provenance.md`, `RULE-2-no-self-ratify.md`). Read: served 2 on the root the rank asks about. It is in rank 2 either way, so the re-read changes no order.
- `platform-ops` and `regulated-engineering` are listed first because they were worked first. On these keys they tie with `team-leads` and `agencies` on harm per week and on served (re-read 2), and nodes added put them ahead: each was counted at 23 or more.

## The riskiest assumption
- **H** Platform engineers feel the risk of an agent acting on a host strongly enough to accept a `Y` before every
  change and again before it closes.

## Fit (`collateral-lean-canvas`), for `platform-ops`
Judged in the d-work #672 completion reply; this file records the canvas, not its verdict.

## Sections
Shared: `solution.md`, `cost-structure.md`, `unfair-advantage.md`. Per segment: `platform-ops/`, `regulated-engineering/`,
each with its own source `why-tree.md`. The canvas set's `why-tree.md` is their projection (§6), read for screening.
