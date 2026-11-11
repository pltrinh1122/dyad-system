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

## The pick (d-work #672, reading revision 3)
- **H** The most significant segment served today is `platform-ops`: the highest cost of an unchecked error, the most often.
- **H** Runner-up: `regulated-engineering`, at a higher cost and served only in part.

## The riskiest assumption
- **H** Platform engineers feel the risk of an agent acting on a host strongly enough to accept a `Y` before every
  change and again before it closes.

## Fit (`collateral-lean-canvas`), for `platform-ops`
Judged in the d-work #672 completion reply; this file records the canvas, not its verdict.

## Sections
Shared: `solution.md`, `cost-structure.md`, `unfair-advantage.md`. For `platform-ops`: `platform-ops/`.
