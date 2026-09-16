# Falsification record — concurrent-session races in the d-work store (d-work #32)

**Claim (row #32, opened from live incidents on #23/#24/#25):** two sessions sharing a presence
identity, or independently allocating the same row id, are collisions this instance can turn from
silent corruption or a false alarm into a loud, correctly-scoped stop using only information a
single session already has — without a shared allocator.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "A palliative: only a shared allocator actually fixes this, so this is code that buys nothing." | Survives, scoped | It buys one thing precisely: the difference between a collision discovered by hand three times in one session (#23, then #24, then #25) and a collision that stops a push with both titles named. Rule-13's trigger is recurrence, and recurrence is established in `INCIDENTS.md` (two classes, three occurrences, one session). If the Operator would rather carry the collisions until #24's LAN git server lands, `N` was coherent and nothing else depended on this. |
| 2 | "F2's check belongs in `prs.py`, the branch's transaction guard." | Refuted | `prs.py`'s entity is the PR and its concern the plan gate; the row store is `rows.py`'s entity (Rule-3 content, Rule-16 store). Putting a row-identity check in the PR guard would give one concern two owners — the gap Rule-5 names. Same guard, new mode (`check_id_collisions`, run from `check_transaction`'s off-`main` branch), is the orthogonal placement. |
| 3 | "Adding `writer` breaks every presence file already written." | Refuted by construction | It is optional, outside `FIELDS`, checked only when present — `dev-main.md` and `web-sysarch.md` (and every other file already on `main`) keep passing `check_package`, since the check only validates required-field presence and `seen`'s shape, never rejects an unrecognized extra field. |
| 4 | "F1's warning fires on a session's own second touch." | Refuted | `_WRITER` is computed once at import and is stable for the process's life; a session re-touching its own file matches its own `writer` and stays silent — verified by `test_same_writer_reunites_silently`. |
| 5 | "F4 is a one-line fix that needs no d-work." | Refuted | The one line is small, its blast radius is not — it is why a session warned about itself, why a written presence file disagreed with its own name, and why the store grows a file per unconfigured invocation. Small fixes to live stores are exactly what this record exists to hold — and attack 7 below shows the "one line" first proposed was itself wrong. |
| 6 | "F3 is cosmetic — the allocation is still correct." | Refuted | It is correct only over the ids it can see, and the whole point of the fetch is that local ids are not enough. Degrading from "authoritative" to "local-only" without a word is the exact failure mode `#27`'s fail-loud rule calls unnamed. |
| 7 | "F4's fix is `session_id()` memoized at module scope, computed once, so the filename, the `session:` field and every `exclude` argument are one value." — the plan's own first-written text, itself a claim accepted on first reading (Rule-9, Easy agreement) and therefore owed an attack before being encoded in code. | Refuted, live, while reading the existing test suite before writing code | `dyad/tests/guards/agent/test_sessions.py::TouchTests::test_unset_session_gets_a_fresh_id_each_time` (already on `main`, predates this d-work) asserts that two unconfigured `touch()` calls *in one process* must get *different* ids — an intentional per-invocation safety design (F1's own text: "an unconfigured caller writes its own file and never overwrites another's"), not a bug. Module-scope memoization would have silently collapsed every unconfigured call in a process onto one id, breaking that guarantee without failing loud about it — the exact failure shape this whole d-work exists to close. Survivor: resolve `session_id()` once **per call site** instead — `touch()` resolves it once at its own top and threads that value through the path and the written body; `main()`'s touch handler reuses the path `touch()` actually returned (`p.stem`) for `same_root`'s `exclude` instead of a fresh call. `session_id()` itself stays unmemoized; the fresh-id-per-call behaviour the test locks in is untouched. This closes two of F4's three named consequences (the filename/body mismatch, the self-warning); the third — an unconfigured session adds a new file per invocation, unbounded — is not a defect either fix touches, since it is the accepted cost of the same safety design, retired only by naming `DYAD_SESSION` consistently. |
| 8 | "F4's fix, once corrected by attack 7, closes every `session_id()`-consistency defect in the file." | Refuted, scoped | `main()`'s `list` verb computes its own `same_flag` inline (`s.get("session") != session_id()`) with the identical fresh-call bug — a *third* call site F4's original text never named, found only while implementing attacks 4–7's fix to the other two. Left undisposed here (frame conduct: detect, don't dispose) rather than folded into an unauthorized fourth fix under this plan-`Y`; named in the plan's own correction and in the completion evidence for a future d-work to pick up. |
| 9 | Overlap (Rule-16): read before writing the plan and again before this record. | Checked, none found | `web-sysarch-adh151` holds only row 32 with `files:` naming exactly the four files this d-work touches (self, not a peer). No other live presence file names any of `sessions.py`, `rows.py`, `package.py` or `stores.md`. |

**Path (Rule-10):** implement all three mechanisms — F1's writer-collision detection in
`sessions.py`, F2's branch-side `check_id_collisions` in `rows.py`, F3's loud fetch-failure warning
in `package.py` — with F4's fix corrected, per attack 7, from module-scope memoization to a
per-call-site resolve-once-and-thread-through; leave the `list` verb's identical-shaped bug
(attack 8) undisposed for its own future d-work.

**Strongest counter:** none of this makes a collision *impossible*. Two sessions holding unpushed,
unfetched ids still cannot see each other, and no local mechanism changes that — only a shared
allocator can (the LAN git server, #24). Shipping a partial mitigation risks being read as "solved"
when it is only "louder," and attack 7 shows that even the mitigation's first draft was wrong until
an existing test caught it.

**Reconciliation:** the record claims exactly that, no more — the difference between a collision
this session found by hand three times (#23, #24, #25) and one that now stops a branch push with
both titles named, or warns instead of silently merging two sessions' presence, or admits out loud
that an allocation is local-only. That is the gap between a fault "knowable earlier than it is
reported" and one actually reported loud, which #32 was opened to close, and it is unrelated to
whether #24 ever lands. Attack 7's correction is the same discipline applied to this record's own
first draft, not a reason to distrust the rest of it.

Disposition: see ledger #32.
