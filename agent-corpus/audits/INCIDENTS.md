# Incidents (Rule-3)

One row per incident: what departed from the plan, why, and what it cost. Rows before
2026-09-12 #66 are backfilled from the session transcript and memory, and say so.

| date | d-work | what | cause | consequence |
|------|--------|------|-------|-------------|
| 2026-09-15 | #1 | five red Actions runs on the first two pushes to `main` and on tag `v0.3.1` | (a) `rule-3 d-work` and `rule-1 containment` detected the three seed commits of workstation#194 — direct pushes to `main` spanning three zones, ratified as such (Rule-2); one-time. (b) `rule-11 release` at `v0.3.1`: the frame imported a preferences file a package-only repo did not have; exists since the seed. (c) `rule-11 package`: the core and craft suites assumed the `sysadmin`/`lan-git` crafts (workstation#184's class) — the defect this d-work fixes. | runs left as the record; (c) fixed by #1's two PRs |
