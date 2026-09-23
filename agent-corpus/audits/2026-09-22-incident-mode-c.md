# Incident mode C — concurrent-session races

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #119, child of #116 (2026-09-22).*

## Definition
Two sessions on one instance write into a namespace they share — row ids, provenance ids, the
presence store — while each session's view of the other's claims is a snapshot the peer can
invalidate between the read and the write. The mechanism is not a broken part; it is a correct part
whose design assumes one session. Rule-16 Presence states the assumption plainly: one file per
session, "only that session ever writes it — zero cross-session write conflict by construction."
When two sessions resolve to one identity that construction is void, and neither can read the
other's claim.

Two neighbours are easily confused with it.

- **B, stale local view.** In B the information existed on the remote and the session did not fetch
  it (#22's unfetched branch tip, #80's unfetched tags). In C the information did not exist to be
  fetched: a peer's id is allocated locally and is invisible until its push lands. The boundary case
  is #3 (2026-09-14, a peer had already landed the identical fix), which the parent audit files
  under B; by the reasoning that puts #30's duplicate-execution half in C, it could sit here. It is
  left where #116 put it and named as a boundary, not moved.
- **G, mechanism defect.** G is a guard, hook or CLI not doing what its own design says. C is the
  design doing exactly what it says while assuming a single session. The boundary case is the #35
  row (`dyad session touch` writing a peer's rows into this session's presence file), filed under G
  although its own text assigns it to #32, the row that owns the concurrent-session store defects.
  Also left where #116 put it; its consequence is load-bearing for the Pattern below.

## Incidents (3)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #30 | Diagnosed and executed d-work #23, a row a concurrent session already owned, pushing a duplicate to PR #16 with a restarted attack numbering. Separately, this d-work's own id collided twice with the same peer: opened as #24 while the peer took #24, renumbered to #25, and the peer took #25 too; it landed on #30 with deliberate headroom, a stated one-time deviation from `max(origin, local)+1`. | A second session shared the presence identity `web-sysarch`, so neither session's read of `sessions/web-sysarch.md` could show the other's claim on #23. The id races are the same cause one level up: `max(origin, local)+1` computed independently by two sessions, invisible to each other until a push lands, and a PR-fenced session structurally loses every close race to one pushing straight to `main`. Caught both times by a `check --guards` run after a fresh fetch, never by the presence store. |
| 2026-09-16 | #26, #34 | Twice in one hour, `<id>.md` files were written before `dwork new` printed the allocated id: 22 and 27 assumed, 26 and 34 actually allocated, a second session having opened rows meanwhile. The second time the peer's real #27 plan and provenance were overwritten on `origin/main` for about a minute, restored byte-for-byte at `60ccead`. | The id was taken from the last row this session had seen rather than read from the allocator, which fetches. Allocation is the shared namespace; the write outran the read of it, and the overwrite reached `origin/main` because nothing between allocation and push looks at row identity on the PR path. |
| 2026-09-16 | #27 | The provenance record for #27 was first written as `26.md`. Id 26 had just been taken by a peer session's row, a preferences proposal pushed to `origin/main` mid-turn. Caught in the same turn: the stray file was untracked and removed, `provenance/27.md` written instead, nothing of the peer's overwritten. | `dyad dwork new` and the `cat > provenance/<id>.md` were issued in one command, so the file was named before the allocator's answer could be read. Same assumed-id mechanism as the row above, at a second store; Rule-7 property 1 places the provenance record under the same id as the row, so one assumed id mis-names both. |

## Pattern
All three occurred on 2026-09-16, each against a concurrent session on this one instance — the log
names the peer's identity (the shared `web-sysarch`) only for #30; for #26/#34 and #27 it says only
"a second session" and "a peer session", so whether one peer or two is not in the record — and all
three are one shape: a
write committed against a snapshot of a shared namespace that a peer had already invalidated. What
varies is only what was assumed — another session's ownership of a row (#30), the next row id
(#26/#34), the provenance id derived from it (#27) — and how far it travelled, from caught in the
same turn to a minute of overwritten files on `origin/main`. Remediation has shipped since: #32,
done the same day, added the `writer` field and collision warning in `dyad/guards/agent/sessions.py`,
`check_id_collisions` in `dyad/guards/agent/rows.py` for every branch, and the allocator's
fetch-failure warning in `dyad/scripts/package.py`, and #45 corrected the id-allocation bullet in
`crafts/sysarch/rules/stores.md`; none of the three makes a collision impossible, as #32's own
record says. No mode-C row has been logged in the six days since, but that is weak evidence: the
store's own overlap signal is still unusable, because `sessions.touch_from_open_rows` derives `rows`
from the ledger's whole open-or-planned set, so every presence file still claims every open row (the
#35 row, unfixed), and a race that was never noticed would leave no row here either.

## Remediation candidate (falsified, not disposed)
Every incident above is a write judged against a view of the shared namespace whose age was not
stated. The one place that age is still invisible after #32 is the pre-push guard run itself:
`package.cmd_guards` runs `rows.check_transaction` — which off `main` is `rows.check_id_collisions`
— over `base="origin/main"` as the local clone last fetched it, performing no fetch and saying
nothing about how old that ref is, while
`dyad/hooks/pre-push` makes it the only check before a merge. **Candidate: have the transaction-guard
run state the age of the view it judged on — print, beside the `agent/rows` transaction line, when
`origin/main` was last fetched — so a collision check made against a stale base is loud rather than
silent.**

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | A third file on the same defects: #32 already owns the concurrent-session store defects, so this is duplication. | refuted, re-scoped | `agent-corpus/d-work/rows/32.md` reads `state: done`, not backlog as `plans/119.md` states; its three mechanisms shipped and #45 closed its undelivered item 7. The candidate is the residue #32's own record names ("none of this makes a collision impossible"), not a re-opening of it. |
| 2 | Then fetch `origin/main` before the transaction guards — `dwork new` already fetches before allocating. | refuted | Rule-14 property 2 puts Git as a *local* repository in the kernel and says a hosted git service is never kernel; property 3 requires every guard to run on the kernel alone. A guard whose verdict depends on the network leaves the kernel-only path, and the pre-push hook is the only check before a merge. `dwork new` may fetch because it is a command, not a guard. Survivor: no fetch inside the guard, report the age of the local view only. |
| 3 | The age of `origin/main` is not knowable without the network either, so there is nothing to print. | refuted | Both reads are local: `.git/FETCH_HEAD`'s mtime and `origin/main`'s own committer date. Neither asserts the ref is current; they state only when it was last refreshed, which is exactly the claim being made. |
| 4 | A warning does not interrupt. The parent audit's trend shows a memory note and a Rule sentence each failed to stop mode A recurring; #32's own F3 fetch-failure warning is the same shape and the same limit. | survives, scoped | Conceded: this buys a stated view-age, not a stop. It is scoped to making one silent input visible at the point of use, which is the shape #27's fail-loud rule asks for, and it is not claimed to prevent anything. The one remedy #116 found structurally interrupting was #113's delegation fence. |
| 5 | The real fix is a shared allocator; anything a single session can do locally is palliative. | confirmed | `crafts/sysarch/rules/stores.md` and #32's record both say only a shared allocator removes the race. The row they cite for it is `#24`, an authoring-instance id: this ledger's #24 is the exec-bit-gap row, so the named remediation does not resolve here — the foreign-id class the 2026-09-18 sysadmin sweep records as A1. The candidate is a palliative and claims nothing more. |
| 6 | This audit's own plan checked Rule-16 overlap and found none, so the mode is not live even for this work. | refuted in part | `plans/119.md` states "no presence file names `agent-corpus/audits/`"; five of the seven presence files do, four of them naming `agent-corpus/audits/INCIDENTS.md`, which the parent #116's own mutation edits. None names this file, so the plan's conclusion holds for this mutation while its stated ground does not. |

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #119 (Rule-9 Form). Remediation
itself is a further Operator prompt on this row, never taken here.
