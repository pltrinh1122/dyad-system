# Incident mode T — a stale or partial view of shared state

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 10 of 140 rows.*

## Definition
An act is taken on a local view of state that another party inside The Dyad System — a peer session,
or the remote's refs — has already moved, and nothing makes the staleness visible at the moment of
the act. The view was refreshed at some earlier moment the actor chose, or never, and the act
reads it as current.

**What would have to change.** The view would have to be refreshed, or shared, at the moment it is
read rather than at a moment the actor picks — which for the id half means a shared allocator and for
the ref half means a fetch the act itself performs.

Boundaries against the neighbours it is most easily confused with:
- **C, a value stated from memory or a digest instead of read from its source** — Separating test:
  was the authoritative value reachable locally at the moment of the read? C yes, and it was not
  read; T no — the value needed a fetch, or sat unpushed in another session's checkout.
- **U, the World moved** — Separating test: is the mover part of The Dyad System (Operator, Agent,
  crafts, instance — vocabulary)? T yes, always a peer session or the remote's refs; U no — a
  hosting API, an account, the machine's memory. Boundary row: row 112 (#234), where an hour of
  hosting refusals cost an id collision; assigned to **U** because the hosting failure started it
  and the stale view is its consequence, which is phase 1's primary-mechanism rule.
- **D, the wrong object read** — Separating test: right object? T yes, read at the wrong time; D no.
- **R, a derived key that does not identify** — Separating test: was the derivation correct for the
  data it had? T yes — `max(origin, local) + 1` is right over the rows it could see; R no, the
  derivation itself fails to identify.

## Incidents (10)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14 | #3 | a planned craft-zone fix and a `--no-verify` push were both withdrawn before execution | a concurrent session had already landed the identical fix on `origin/main` first |
| 2026-09-16 | #22 | a `plan.base->commit` FAIL was reported to the Operator as a ledger defect with an unrecoverable sha | the clone had never fetched the branch whose tip is that sha; diagnosed from `git cat-file` with no fetch |
| 2026-09-16 | #22 | branches were cut from a stale `main` four commits behind, and rebasing regressed row #6 from done to backlog | the clone was never fetched before branching, and a peer's d-work had completed meanwhile |
| 2026-09-16 | #30 | work a concurrent session already owned was diagnosed and pushed as a duplicate, and this row's id collided twice | two sessions shared one presence-file identity, so neither read could show the other's claim |
| 2026-09-18 | #80 | a release claim was falsified as false and the conclusion merged; six tags existed already, cut the day before | every check used an explicit refspec, which suppresses tag auto-following, so no tag was ever fetched |
| 2026-09-28 | #178 | a backlog row allocated as #180 collided with a peer's #180 already on `origin/main` | the peer's row landed between this allocation and this branch's verification |
| 2026-10-05 | #223 | the first push was refused because seven plan files name base commits that did not resolve | the container's clone was depth-limited and the guard resolves every live plan's base commit |
| 2026-10-05 | #223 | a row allocated #222 was refused at push because another session had pushed its own #222 | the allocator read an `origin/main` tracking ref this session had not fetched since its start |
| 2026-10-05 | #225 | the ledger PR opening row #224 could not merge; another session had opened its own #224 a minute earlier | two sessions fetching the same `main` allocate the same id, and the fence rejects it at merge |
| 2026-10-09 | #256 | id 255 was allocated twice; the push of `main` was rejected and the row renumbered to #256 | two sessions holding unpushed ids cannot see each other; no shared allocator exists |

Note on ordering: rows 90, 91 and 94 share the date 2026-10-05 and are listed in row-file order
within it; the log's own dates are used throughout, as mode A's record does for #58 and #67.

## Pattern
The ten rows are two families, and the split matters because their mitigations differ completely.

**Id-allocation races — rows 25, 64, 91, 94, 120 (5 rows).** Every one is `max(origin, local) + 1`
computed against a view a peer had moved or was about to. Every one was caught before anything
landed, by four *different* mechanisms: `rows.check_id_collisions` at the push (64, 91), the
hosting's refusal at merge (94), git's non-fast-forward refusal (120), and a `check --guards` run
after a fresh fetch (25). Every one of the five cost a renumber, and row 120 cost three hand-built
commits and a third plan revision.

**Unfetched or partial views — rows 14, 22, 24, 42, 90 (5 rows).** Five different namespaces: a peer's
merged work (14), an unfetched branch tip (22), an unfetched `main` before branching (24), tags
never fetched because an explicit refspec suppressed auto-following (42), and a depth-limited clone's
missing objects (90). Row 42 is the only row of this mode whose wrong conclusion reached `main`: a
falsification verdict merged as PR #55 and retracted by amendment.

Recurrence evidence, and this is the unusual part of this mode: **the id family's recurrence is not
evidence against its mitigations — it is the mitigations working, and every row says so.** Row 64:
"The mechanism worked exactly as designed." Row 91: "the fence caught the collision as designed".
Row 94: "the fence only rejects the collision at merge (Rule-16, by design)". Row 120: "neither of
its two checks makes a collision impossible, only loud. No shared allocator exists until d-work
#24." The design's own claim is that it makes a collision loud, not impossible, and the five rows
are five loud collisions. The fetch family's recurrence is ordinary: row 22's prose ("a reference
that names a commit is never called missing until the remote has been fetched", 2026-09-16) was
followed by row 42 (2026-09-18, tags) and row 90 (2026-10-05, clone depth) in namespaces the prose
did not name.

## Mitigations (phase 2)
1. **Fetch-then-allocate in `dyad dwork new`** — `dyad/scripts/package.py:948-950` (`git fetch -q
   origin main`, then `remote = {r.id for r in dyadlib.read_rows(REPO, at="origin/main")}`),
   `package.py:956` (`rid = max(set(rows) | remote, default=0) + 1`), with a printed warning and a
   local-only fallback when the fetch fails (`package.py:951-953`). Moment: inside the `dwork new`
   command, as the id is taken. **Shipped.** Reach: it narrows all five id rows and prevents none —
   in rows 25, 64, 94 and 120 the peer's id was unpushed or landed between allocation and
   verification, which no fetch can see. Every one of the five post-dates it.
   One thing I could not verify: row 91's cause cell says "this session had not fetched since its
   start, so the ref was stale when the id was taken", which is inconsistent with
   `package.py:948` fetching on every `new` unless that fetch failed into the warning path. Whether
   #223's allocation ran the fetch and it failed, or the id was taken another way, is not
   recoverable from the ledger row and is not stated there.
2. **`rows.check_id_collisions`** — `dyad/guards/agent/rows.py:212-243`, FAILing at `rows.py:239-243`
   when a row file the range adds or modifies names an id that exists at `base` under a *different*
   title; invoked on any branch but `main` by `check_transaction` (`rows.py:164-172`). Moment:
   `dyad check --guards --pre-push` (`dyad/hooks/pre-push:4`) and `check --evidence`. **Shipped.**
   Reach, row by row: row 64 yes (its cause cell quotes the guard's own message), row 91 yes
   (`agent/rows (row-id)`); row 94 no — that collision was on `main` and the refusal came from the
   hosting at merge with a moved base; row 120 no — git's non-fast-forward did it; row 25 no — it
   predates the guard, #32 being the backlog row row 25 itself opened; rows 14, 22, 24, 42, 90 no,
   none involves an id.
   **What it makes impossible versus loud, precisely.** Impossible: a push landing a second row file
   under one id with a different title, on the branch path, where a fast-forward add/add merge or a
   reset-then-push would otherwise have overwritten one silently. Not impossible, and never claimed:
   two sessions *choosing* the same id, because the guard can only compare against `base`, and an id
   a peer holds unpushed exists in no base. `crafts/sysarch/rules/stores.md:29-32` states exactly
   that — "Neither check makes a collision impossible — two sessions holding unpushed ids cannot see
   each other, which only a shared allocator (the LAN git server, #24) changes — only loud rather
   than silent, at the earliest point each path can reach."
3. **Git's own non-fast-forward refusal** — not dyad code, and named here because it is the only
   mechanism that caught row 120. Moment: the push. It reaches the direct-to-`main` path and nothing
   on the PR path, which is why mitigation 2 exists (`stores.md:24-28`).
4. **The presence store** — Rule-16 Presence (`dyad/rules/RULE-16-concurrent-sessions.md:35-60`),
   guard `dyad/guards/agent/sessions.py`. It is declared a non-transaction guard
   (`sessions.py:33`, `TRANSACTION = False`), so it never runs over a range at a push; its check
   "only validates shape … and never fails on overlap, same-root, or staleness"
   (`sessions.py:15-17`), its fields are `("session", "seen", "root", "rows", "files")`
   (`sessions.py:34`). Moment: written at `dyad session touch` (session start and each plan-`Y`),
   read when a reader chooses to. **Shipped**, advisory by design. Reach: row 25 is the row it
   *failed* — two sessions shared one presence identity `web-sysarch`, so "neither session's read of
   `sessions/web-sysarch.md` could show the other's claim on #23". Two fixes for that have since
   shipped and post-date row 25: the `writer` field and its loud warning when a different live
   process holds the same session name (`sessions.py:100`, the F1/#32 fix), and `same_root`
   (`sessions.py:164`, warned at `sessions.py:219-221`) for #185's shared-checkout near-miss. Reach
   of the store over the other nine rows: none. It says nothing about the remote's refs and nothing
   about an id a peer holds unpushed.
5. **`references.py` `plan.base->commit`** — `dyad/guards/agent/references.py:414`, which resolves the
   base commit of every live plan. Moment: `package.py check` in the runner and the kernel-only path.
   **Shipped.** It is the mechanism that *surfaced* two rows: row 22 as a false alarm from an
   unfetched ref, row 90 as a true refusal from a depth-limited clone. It detects a partial view and
   fences nothing against one. Rule-20 property 2's per-instance exemption (a terminal row's base
   commit is skipped silently) narrows row 90's shape without removing it.
6. **Nothing fetches at the two moments the fetch family needed one, and the push gate's own base is
   a local ref nobody refreshes.** `cmd_guards` takes `base="origin/main"` (`package.py:583`) and
   does not fetch; `pushed_refs` compares against that same local tracking ref
   (`package.py:549-579`). No hook, guard or `dyad` verb runs a fetch before a branch is cut (row
   24) or before a tag claim (row 42). For those two rows there is **no mechanism at all**.

## Remediation candidate, under attack
One candidate at the one moment the whole system already converges: a base-freshness observation in
`cmd_guards` (`dyad/scripts/package.py:583`), on the kernel-only path at `dyad check --guards
--pre-push`, printing the age of the `origin/main` tracking ref and, where a fetch succeeds and shows
the base has moved, saying so before any check runs.

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | It puts a network read on the kernel-only path, which Rule-14 property 3 defines as running "on the kernel alone" and whose property 2 says "A hosted git service is never kernel" (`dyad/rules/RULE-14-system-infrastructure.md:34-38`). A gate that fetches cannot produce evidence when the hosting is down — exactly U's rows 97 and 112. | confirmed | A *blocking* fetch does not survive. Survivor: the probe's failure is itself the observation ("base freshness: unknown, fetch failed"), never a non-zero exit — the `world`-kind warn pattern Rule-20 property 2 already uses. |
| 2 | Easy agreement (Rule-9 Conditions): "fetch more" reads as the obvious answer, so attack it against the larger family. Even a successful fetch reaches none of the five id rows: in rows 25, 64, 94 and 120 the colliding id was *unpushed*, and `stores.md:29-32` says only a shared allocator changes that. | confirmed | The candidate does not reach the id family at all. It reaches the fetch family — rows 24, 42, 90, and row 22's false alarm — and must be offered as that, not as a remedy for the mode. |
| 3 | A refusal here would be routinely wrong and routinely bypassed: a session legitimately pushes a branch cut from an older base and the merge resolves it. Teaching bypass is what mode V's two rows cost. | survives (scoped) | Only as a warning line, never a FAIL — which puts it in the same class as `agent/references`'s `world` warn, and makes it a report rather than a fence. |
| 4 | Attacks 1 to 3 reduce the candidate to "print the base's freshness", and the play-book's exit 1 requires a mechanical check, not a printed line. So the mode's larger family ends with no surviving candidate fence. | confirmed | Stated as the finding rather than softened: this mode has no surviving candidate fence for either family, and the two families' honest exits differ. |
| 5 | Attack the mode's own boundary, since the attacks above turn on it: if the id family and the fetch family take different exits, is T one mode? | survives (scoped) | T holds as one *mechanism* — an act on a view another party moved — and splits on *who moved it and whether a fetch reveals it*. The recommendation below is that the next exercise derive them as two modes, which `dyad/playbooks/incident-hardening.md` phase 1 expressly allows ("the modes are re-derived from the ledger each exercise, never read off the previous index"). |

## Proposed exit (phase 4)
**Open.** The mode holds no single exit, and saying so is the finding rather than a deferral.

The two families reach two different exits, which is why:
- **Id races (rows 25, 64, 91, 94, 120)** reach exit 3, *recorded unfenceable on this kernel*: the
  only thing that makes two unpushed ids visible to each other is a shared allocator, and
  `crafts/sysarch/rules/stores.md:29-32` names it as the LAN git server of d-work #24, which
  `dyad/rules/RULE-14-system-infrastructure.md:37` puts outside the kernel — "A hosted git service
  is never kernel." The stretch in that reading, stated for the Operator: exit 3 as the play-book
  words it covers a fault that *lives in* a hosted service, and this fault lives in the *absence* of
  one. The Operator should dispose whether that counts.
- **Unfetched views (rows 14, 22, 24, 42, 90)** reach exit 2, *a `backlog` row naming the fence*: the
  base-freshness observation that survived above, in `cmd_guards` (`package.py:583`), printing the
  tracking ref's age before any check runs and warning when a successful fetch shows the base has
  moved. It would have caught rows 24 and 42 and reported rows 22 and 90 as freshness rather than as
  defects; it would not have caught row 14, where a peer's identical fix had already merged.

The recommendation to the Operator is therefore to split T at the next exercise and let each half
take its own exit; until that is disposed, T stays open in the index whatever this record says about
it, which is the play-book's own rule. Proposed only — nothing closed here.

## Delta 2026-10-24 (#259 revision 5; 10 → 14 rows)
**Rows added:** 148 (#291: an id allocated by a branch-fenced session against an `origin/main` it cannot
advance), 168 (#243: PR #349's id collision), 170 and 178 (#301, #297: the `dbfe778` wedge — a plan's
base commit taken from an unpushed local `HEAD`, failing every other clone's pre-push for 19–40
minutes). Secondary member of 172 (the writer's side) and 197.
**Mitigations re-read from the code.** The id half: `dwork new`'s fetch-then-allocate and
`check_id_collisions` (`rows.py:356`) unchanged; both rows are the branch-fenced or in-review case the
2026-10-10 record said neither reaches. The base-commit half is new to the mode: `references.base_commit`
checks existence in the local object store and not ancestry of `origin/main`; no row names that fence.
**Exit after the delta:** open, and the 2026-10-10 recommendation to split T stands with a third family
added — unpushed state published as if shared (170, 172, 178). Candidate stated: `plan.base->commit`
must be an ancestor of `origin/main`, checked at the writer's push.
