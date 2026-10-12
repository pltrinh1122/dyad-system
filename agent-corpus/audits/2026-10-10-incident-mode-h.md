# Incident mode H — the present enumeration pinned as an invariant

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10, 6 rows.*

## Definition
A check states the current membership of an open set as a literal — a list of crafts, projectors,
guard entities, run-books, manifest components, or one system's own preference values — so a legal
addition to that set, or a legal difference in another install, makes the check false and turns the
addition itself into a red gate.

**What would have to change.** A check over an open set would have to derive the whole set from the
store that owns it and pin only the subset it actually means to assert, so that a new member costs
no edit while a dropped known member still fails.

Boundaries against the neighbours it is most easily confused with:
- **C, a value stated from memory instead of read from its source** — C's wrong value sits in prose,
  a reply or a plan and is wrong *now*; H's value was right when written and is falsified by a later
  legal addition, and it sits inside a mechanical check. Separating test: was the statement true at
  the moment it was written? For all six H rows it was.
- **I, verified in one environment, run in another** — the sharpest boundary, and row 59 is the
  boundary row. I's check is true here and false there because the *environment* differs; H's check
  is false here as soon as the set grows. Row 59 is assigned H because the mechanism is a literal
  pinning this instance's own preference values and component counts, which the live-read and the
  pinned-default are indistinguishable from in the authoring system; rows 19, 26, 83 and 123 are I.
- **Q, an obligation no mechanism reads** — Q has no check at all; H has one check too specific.
  Separating test: delete the obligation's subject and see whether anything goes red. For H it does.
- **T, a stale or partial view of shared state** — T's staleness is of live state read at the wrong
  moment and is cured by re-reading; H's is frozen in tracked source and is cured only by an edit.

## Incidents (6)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-15 | #1 | five red Actions runs on the first two pushes to `main` and on tag `v0.3.1`, one cause being `rule-11 package` | the core and craft suites assumed the `sysadmin` and `lan-git` crafts were present, the defect this d-work fixes |
| 2026-09-22 | #114 | bundling `sysadmin` broke 11 core tests that pass on `main` — 7 failures and 4 errors, including a `test_build_deterministic` archive file-list assertion | the core suite encodes "a core install carries no craft" as an invariant, and a bundled craft makes it false by design |
| 2026-09-23 | #137 | shipping a second core run-book broke the core suite: a test asserts the literal `ok   [rule-19] 1 run-book(s), 8 commands` and the install now reports 2 and 14 | the test pins the core's run-book count and command total as literals rather than deriving them |
| 2026-09-24 | #156 | adding the countersign craft left the core suite red: two tests expect exactly the six sysarch and sysadmin projector surfaces, so the craft's one new projector failed both | both tests enumerate the installed crafts' projectors as a literal list instead of deriving it from the tree |
| 2026-09-25 | #175 | #175's tests asserted dyad-system's own instance values against the live repo, so once countersign-system set a non-default host path its pre-push gate failed 9 tests | the tests were written and verified only in the authoring system, whose preferences are the defaults, so a live read and a pinned default were indistinguishable there |
| 2026-10-06 | #227 | the first push of the guards branch was refused by 5 tests, one of them in the released sysarch craft, which asserts that `incident` has no guard | the pin is the one `incidents.py`'s own docstring names, and the plan's attack on a red gate was answered by running two checks rather than the crafts' suites |

## Pattern
Five of the six are a legal *addition* to the system — a bundled craft, a second core run-book, a
new craft's projector, a new guard entity — meeting a check that had written down the previous
count. The sixth, row 59, is the same mechanism pointed sideways rather than forward: the literal
pinned this instance's values, and the addition that falsified it was another *system* rather than
another member. Every one of the six was caught on a branch or at a push gate and none reached
`main` — the mode's cost is a blocked legal change, not corruption. Rows 1, 9 and 51 say so of each
other: row 9's cause names "exactly the class backlog #10 names"; row 51's names "the class backlog
#10 names, and the same shape as #114's" ; row 1's names "the #46/#98 class again (`KNOWN_CRAFTS`),
and #137's run-book-count row, on a third registry".

Recurrence evidence, mitigation by mitigation:
- Row 1's consequence describes the derive-from-disk repair ("Both tests now derive the set from
  discovery on disk and keep the known sysarch/sysadmin surfaces asserted"). Row 59 (2026-09-25) and
  row 95 (2026-10-06) post-date it.
- Row 51's consequence describes the same repair for the run-book count ("The assertion now derives
  the count from `dyad/runbooks/*.md`"). Rows 1, 59 and 95 post-date it.
- Row 59's consequence describes #179's repair (pin `DYAD_HOST`/`DYAD_HOST_ZONE` when a test means
  the defaults, derive from the live repo's own preferences when it means the live repo, plus
  `FourZoneSystemTests`). Row 95 (2026-10-06) post-dates it, on the guard registry rather than on
  host paths.
- Backlog row #10, said to name the general fence, is the oldest mitigation of all and nothing has
  been built under it; see M5.

## Mitigations (phase 2)

**M1 — derive the set from disk, pin a known subset (shipped, by convention, in five places).**
`dyad/tests/test_dyadlib.py:358-366`: `on_disk = [(p.parents[1].name, p.stem) for p in
sorted(crafts.glob("*/projectors/project_*.py"))]`, asserted equal to the discovered stems, then a
`known` dict of the two crafts' surfaces asserted as a sub-check — the comment at `:359` states the
intent ("Expected set derived from the tree, not a literal list (#156 I1, the #46/#98 class)").
`dyad/tests/test_package.py:783-787` does the same for the `craft/surface` registry keys.
`dyad/tests/test_package.py:503-504`: `core_rbs = sorted(...glob("*.md"))` then `assertIn(f"ok
[rule-19] {len(core_rbs)} run-book(s), ", r.stdout)`, with the comment "the count is derived, never
pinned (backlog #10)".
`dyad/tests/test_package.py:986-988`: the invariant-pass label order is derived from
`dyadlib.guard_files()` and `pkg.PROJECTORS`.
`dyad/tests/test_runbook.py:129-132`: `core = rb.core_runbooks(...)` then `{1 + len(core)}
run-book(s), {11 + sum(len(rb.parse(p)) for p in core.values())} commands` — derived for the core's
run-books, still literal for the fixture's own 11 commands.
Moment: Rule-12's suite, i.e. `package.py check` in the runner and `dyad check --guards --pre-push`
whenever the suite is not skipped.
Reach: row 1 — met (both named tests now derive). Row 51 — met. Row 9 — partly: the projector and
run-book pins are derived, but the "a core install carries no craft" premise is handled by skipping
rather than deriving; see M2. Row 59 — not reached by this pattern; see M3. Row 95 — not reached:
the guard-registry literal survives; see the live surface below.
Shipped: `dyad/tests/test_dyadlib.py:361`, `dyad/tests/test_package.py:783`, `:504`, `:988`,
`dyad/tests/test_runbook.py:129`. Recurred after it shipped: yes — rows 59 and 95.

**M2 — the absent-craft and empty-store skips (shipped).**
`dyad/scripts/livetest.py:86-88` `crafts_installed`, `:95-124` `LiveCase` with `require_store`,
`require_instance`, `require_craft` (`:113-117`, skip `"{ABSENT}: {names} not installed (crafts/)"`)
and `require_guard` (`:119-124`, skip when no installed craft provides the entity). The class
docstring at `:96-99` states the discipline: "Every such test states what it does when that store is
empty or the craft is absent: it asserts the documented behaviour, or calls one of the `require_*`
methods below and is skipped with the reason printed and counted."
`dyad/tests/test_package.py:9-14` `craft_guards` falls back to `crafts/<name>/guards/*.py` for a
craft `KNOWN_CRAFTS` has not caught up to — so a *new* craft needs no edit of that dict.
Moment: Rule-12's suite, at test collection and run time.
Reach: row 1 — met, and this is the structural answer to it. Row 9 — met for the premise's absent
direction (a core-only install) but not for the present direction; row 9's own consequence says the
design question "whether a craft-less core install still exists as a concept" went to the Operator
rather than being decided, and `require_craft`/`require_guard` is the shape that answer took. Rows
51, 59, 95 — not reached.
Shipped: `dyad/scripts/livetest.py:113`, `:119`, `dyad/tests/test_package.py:9`. Recurred after it
shipped: yes — rows 51, 59, 95 all post-date `livetest`'s introduction under #171/#163.

**M3 — pin the environment or derive from the live preferences, plus a four-zone fixture (shipped).**
`dyad/tests/test_runbook.py:125`: `env.update(DYAD_HOST=dyadlib.DEFAULT_HOST,
DYAD_HOST_ZONE=dyadlib.DEFAULT_HOST_ZONE)` with the comment "the fixture's default host path, never
the live repo's preferences (#179)".
`dyad/tests/test_dyadlib.py:107`: `assertEqual(dyadlib.host_path(), (dyadlib.preference("host-path",
live) or dyadlib.DEFAULT_HOST)…)` — the live read, not a literal.
`dyad/tests/guards/infra/test_containment.py:225-249` `FourZoneSystemTests`: a scratch repo whose
preferences set `host-zone: infra`, committed and checked end to end; `:211` carries the reason
("never assumed from the live preferences (#179: a four-zone system is a legal instance)").
Moment: Rule-12's suite.
Reach: row 59 — met, and this is the fix its consequence cell names. Rows 1, 9, 51, 95 — not
reached: none is about the host path or the zone table.
Shipped: `dyad/tests/test_runbook.py:125`, `dyad/tests/guards/infra/test_containment.py:225`.
Recurred after it shipped: yes — row 95, 2026-10-06.

**M4 — the derive-both-ways shape, shipped as a guard but never applied to the registry pins
(shipped, elsewhere).** `crafts/syseng/guards/naming.py`'s `env:` kind: the module docstring at
`:18-20` states it fails "either way: unlisted or stale" — the listed `DYAD_*` set must equal the set
scanned out of `dyad/scripts`, `dyad/guards`, and every craft's `guards/`, `projectors/`, `scripts/`
(`CODE_GLOBS`, `crafts/syseng/guards/naming.py:36`). `crafts/syseng/guards/tests.py` is the other
model: `modules()` at `:40-44` discovers every mapped module and `check_package` at `:51-52` fails
only on a *missing* test — no count is ever pinned.
Moment: `package.py check` in the runner, and `dyad check --guards --pre-push`, as `syseng/naming`
and `syseng/tests`.
Reach: none of the six rows directly — no `env:` or test-mapping pin is among them. Cited here
because it is the only shipped instance in the tree of the exact shape the mode needs, and it shows
the shape is affordable on this kernel.
Shipped: `crafts/syseng/guards/naming.py:36`, `crafts/syseng/guards/tests.py:40`.

**M5 — backlog row #10 (shipped as a row, and it is not the general fence).**
Read today, `agent-corpus/d-work/rows/10.md`:
`title: core tests hardcode sibling-craft presence and a minimum row count — delivered by #1 (PRs
#1, #2); note only`; `state: backlog`; `opened: 2026-09-14`; `disposed: 2026-09-14 Y intake
(workstation#196 message, 2026-09-14)`; `refs: workstation-184 1 syseng`.
Three findings. First, the row exists and is still `backlog` after 26 days. Second, its title names
one delivered instance ("delivered by #1 … note only"), not a general fence, so rows 9 and 51 cite it
as the class while the row itself claims no fence to build. Third, a row's title is immutable
(Rule-16 Store; enforced at `dyad/guards/agent/rows.py:139-140`), so #10 cannot be made to name the
general fence — only a new row can.
Moment: none; a `backlog` row is a record, not a check.
Reach: as a record, rows 9 and 51 by citation. As a fence, none.

**Live surface read today (M1 to M4 do not reach it):**
`dyad/tests/test_package.py:5-6` holds `CORE`, a literal list of the 16 core guard entities
(`"agent/frame"` … `"preferences/preferences"`). It is compared to the derived set with equality at
three places: `:60` `self.assertEqual(expected, CORE + CRAFT)`, `:450`, `:494`. So the set is
derived at `:59` (`expected = [f"{dyadlib.guard_key(py)[1]}/{py.stem}" for py in
dyadlib.guard_files()]`) and then checked *equal* to a literal — the derivation is present and the
pin defeats it. Adding a core guard entity still turns three assertions red, which is row 95's shape
exactly. Row 95's consequence confirms it was patched per-occurrence: "plan revision 2 … updates the
four core tests that list the registry".
`dyad/tests/test_package.py:7` `KNOWN_CRAFTS` is still a literal dict of four crafts and their
entities, read through `craft_guards` at `:12-13` and so into `CRAFT` at `:15` and the assertion at
`:450`; the fallback at `:14` saves a *new* craft but not a change to a listed one. A second,
independent literal of the same four sysadmin entities sits inline at `:495`.

## Remediation candidate, under attack
One fence: a `syseng` check — a new kind in `crafts/syseng/guards/naming.py`'s data or a small guard
beside it — that fails any test module comparing a set derived from one of the system's registries
(`dyadlib.guard_files`, `dyadlib.craft_dirs`, `projector_files`, `core_runbooks`, the manifest rows)
to a literal collection with `==` rather than `<=`. Paired with the one live fix the mode needs:
`CORE` at `dyad/tests/test_package.py:5` becomes a *required subset* asserted with `<=`, and the
derived set is asserted non-empty and self-consistent. The exact moment: `package.py check` in the
runner and `dyad check --guards --pre-push`, as `syseng/naming` (or a sibling entity), on every push
whose range touches anything outside `<instance>/d-work/`.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Easy agreement (Rule-9 Conditions): "derive everything" is the obvious fix, so attack it. A fully derived assertion cannot catch a *silently dropped* member — a guard module deleted by a bad merge would leave the derived set smaller and the test green. `dyad/tests/test_dyadlib.py:364`'s comment says exactly this: "a known craft silently dropping a projector still fails". | confirmed | "Derive everything" does not survive. What survives is derive-the-whole-set, pin-a-required-subset, with `<=` and never `==` — a known minimum, never a known maximum. That is the one-line change the candidate makes to `CORE`. |
| 2 | A check that detects "a literal collection of registry keys in a test module" must itself know what a registry key looks like — a pattern over `<corpus>/<entity>` strings. That is mode H planted in mode H's own fence, and the fence would go red when a corpus is added. | confirmed | The semantic form does not survive. The syntactic one does, narrowly: flag `assertEqual` whose two operands are a derived call and a module-level literal collection, naming neither corpora nor entities. Even that is a heuristic and will miss an indirection through a helper, which must be stated rather than claimed away. |
| 3 | Backlog row #10 already names this class, so exit 2 is already taken and the mode is already closed by the play-book's own rules. | refuted | Read today, `agent-corpus/d-work/rows/10.md`'s title ends "delivered by #1 (PRs #1, #2); note only" — it records a delivered instance, names no fence, and lists no incidents it would catch. Its title cannot be amended (`dyad/guards/agent/rows.py:139-140`). A new row is required, and #10 should be referenced by it, not reused as it. |
| 4 | Coverage: the candidate reaches row 95 (the `CORE` pin) and row 1 (the projector pin, already derived) but not row 59, whose literals were this instance's *preference values* rather than a registry's membership, nor row 9, whose pin was a premise about install shape rather than a set. | survives, scoped | Scoped to registry membership, 2 of 6 rows reached and stated as that. Row 59's shape is already fenced by M3's `FourZoneSystemTests`; row 9's remains a design question the Operator answered once and no check holds. Any reading of the candidate as a remedy for the mode does not survive. |
| 5 | The candidate's own data is a list of registry accessor names, so a sixth registry added without a row in it is unchecked — the generalisation failure that produced four of these rows, one level up. | survives, scoped | Only if the accessor set is itself derived — every module-level function of `dyadlib` returning a sorted list of tracked paths — which is a weaker and noisier rule. Stated as the candidate's residual: the fence degrades to silence rather than to a false failure, which is the right direction but is not closure. |

Read together: the `<=` change to `CORE` survives cleanly and is one line in one test; the
detecting fence survives only in a syntactic, heuristic form, and the mode is not closed by either.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes. Backlog
row #10 is referenced by it and is not it, for the reason attack 3 gives.

What the row would say: *registry pins assert a required subset, never equality — change `CORE` at
`dyad/tests/test_package.py:5` and its three `assertEqual` sites (`:60`, `:450`, `:494`) to a
`<=` containment against the set derived from `dyadlib.guard_files()`, keeping the literal as the
known minimum; and add a `syseng` check that flags an `assertEqual` between a registry-derived call
and a module-level literal collection. refs: 10, 95.*

Which rows it would have caught: row 95 (the first push of #227's guards branch, refused by the
core tests that list the registry) and row 1 (the countersign projector, had the `==` not already
been repaired by hand in #156's PR-0). Rows 9, 51 and 59 are each fenced by their own shipped
mitigation (M2, M1, M3) and would not have needed it.

The mode is not fenced today: `dyad/tests/test_package.py:5-6`'s literal is live, compared with
`==` at three sites, and the most recent occurrence (row 95, 2026-10-06) is four days old.
