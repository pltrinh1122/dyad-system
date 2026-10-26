# Incident mode J — a call site added without its call graph

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10, 3 rows.*

## Definition
A second caller or a second writer is added to something that already had one, and the question
"what else reaches this in the same process, or writes this same store" is never asked — so the
guard, gate or precondition the first path carries is not carried by the new one, and the two paths
interact in a way neither was written against.

**What would have to change.** The guarded thing would have to be reachable only through one
chokepoint that refuses a second entry itself, so that adding a caller cannot omit the guard —
rather than each entry point repeating a convention the new one is free to skip.

Boundaries against the neighbours it is most easily confused with:
- **K, a plan incomplete against its own text** — K's gap is between the plan and its own delivery;
  J's gap is in the code's call graph and would exist under any plan. Boundary rows: d-work #228
  supplies one J row (106) and two K rows (107, 108), so the separating test matters — did the plan
  name the thing and the delivery miss it (K), or did neither plan nor delivery know the second
  path existed (J)?
- **E, an instrument narrower than the question** — E's instrument answered a narrower question than
  was asked; J's instrument was right for the path it ran and simply never ran the other one. Row
  106 is the near case: "The unit test passed, because it never ran the second writer" — assigned J
  because the missing thing is the second writer, not a wrong instrument. E holds rows 49, 98, 102
  and 124.
- **D, the wrong object read** — D reads object A where B was meant; J reads the right object and
  misses that another path also reaches it. Separating test: was anything read that should not have
  been? In all three J rows, no.
- **T, a stale or partial view of shared state** — T's sharing is across sessions or across time; J's
  is within one process (rows 52, 53) or between two code paths over one store (row 106), and
  re-reading cures nothing.

## Incidents (3)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-24 | #155 | the first cut of the gated suite recursed: `cmd_guards` called `cmd_tests()` with no `DYAD_NO_NESTED_TESTS` guard, leaving 44 orphaned `unittest` processes past a 600 s timeout | the early return has existed since `check_rule_12` was written, and the new call site was added beside it without it |
| 2026-09-24 | #155 | the gated suite made `check --evidence` pay for the whole suite twice and print two sets of `[Rule-12]` lines, about 40 s longer than needed | the new call site was added without asking which other entry point already reaches it in the same process; the gate was reasoned per-push, not per-process |
| 2026-10-07 | #228 | the first fix recorded a registry row for every bundled craft on every core install, which broke idempotence and made the second core install report 1 changes where CI greps 0 changes | the fix was written against the refusal branch alone; the row has two writers and only one of them was considered |

## Pattern
Two writers, or two callers, of one guarded thing. Rows 52 and 53 are the same event's two faces
within one d-work and one function: `cmd_guards` gained a call to the suite, and the two things that
already reached the suite — the test child that re-enters `check`, and `cmd_evidence`'s own
`cmd_check` — were both missed, the first costing 44 orphaned processes and the second 40 s of
doubled work. Row 106, two weeks later, is the store version of the same shape: `crafts/REGISTRY.md`
had one writer and the fix added a second without asking what the first one wrote.

All three were caught by running the thing end to end rather than by the unit test. Row 52: "caught
by the timeout on the very first exercise of the verb". Row 53: "caught by the pre-merge evidence
run over the branch, whose doubled `[Rule-12]` lines were visible in the output". Row 106: "caught
before any commit, by running the CI block's whole sequence locally rather than the unit test
alone". The log states the lesson in row 106's own consequence — "a second test pins the full
sequence end to end" — and that is the only instrument that has ever caught this mode.

Recurrence evidence, mitigation by mitigation:
- Rows 52 and 53's consequences name two shipped fixes: `DYAD_NO_NESTED_TESTS` early returns in both
  new entry points with `test_tests_verb_and_guard_suite_do_not_recurse_inside_a_test_run`, and a
  module-level `_SUITE_RAN` with `test_evidence_runs_the_suite_once`. Row 106 (2026-10-07)
  post-dates both by thirteen days — on a different guarded thing, which is the point: the
  per-site fix did not generalise.
- Row 106's own consequences shipped on 2026-10-07 and nothing of this mode is logged after them,
  three days as of this audit — too short an interval to be evidence either way, and stated as that.

## Mitigations (phase 2)

**M1 — the nesting flag, checked at each entry point that spawns the suite (shipped).**
`dyad/scripts/package.py:222-223` in `check_rule_12`: `if os.environ.get("DYAD_NO_NESTED_TESTS"):
return msgs  # already inside a test run (test_package.py calls `check`); do not recurse`.
`dyad/scripts/package.py:428-429` in `cmd_tests`: the same early return, commented "already inside a
test run (a suite invoking `check`); do not recurse".
`dyad/scripts/package.py:404` `suite_env` sets `DYAD_NO_NESTED_TESTS: "1"` in every test child, so
the flag is what makes the recursion impossible rather than merely unlikely.
Moment: process start of any `check`, `check --guards`, `check --tests` or `check --evidence` that
is itself running inside a test child.
Reach: row 52 — met, and this is the fix its consequence names. Row 53 — not reached by the flag
alone: `cmd_evidence` runs outside a test child, so the flag is unset and both its calls would run
the suite; row 53 needs M2. Row 106 — not reached at all.
Shipped: `dyad/scripts/package.py:222`, `:404`, `:428`. Recurred after it shipped: yes — row 106,
on a different guarded thing.

**M2 — `_SUITE_RAN`, one suite per process (shipped).**
`dyad/scripts/package.py:212-214` declares it, with the reason in the comment: "`cmd_evidence` calls
both `cmd_check` and `cmd_guards`, and without this the evidence block paid for the whole suite
twice (caught by the pre-merge evidence run, #155)". Set at `:224` by `check_rule_12` and at `:430`
by `cmd_tests`. Consulted at `dyad/scripts/package.py:349`: `if
os.environ.get("DYAD_NO_NESTED_TESTS") or _SUITE_RAN: return False, None` inside `suite_gate`, which
`cmd_guards` calls at `:640`.
Moment: in-process, at `cmd_guards`'s suite gate, after the guards and before `cmd_tests`.
Reach: row 53 — met. Row 52 — met redundantly with M1. Row 106 — not reached.
Shipped: `dyad/scripts/package.py:212`, `:349`, `:640`. Recurred after it shipped: yes — row 106.

**M3 — the two tests that pin M1 and M2 (shipped, and they pin the known sites only).**
`dyad/tests/test_package.py:151-158`
`test_tests_verb_and_guard_suite_do_not_recurse_inside_a_test_run`: asserts
`DYAD_NO_NESTED_TESTS` appears in the source of `cmd_tests` and of `suite_gate` and that
`cmd_guards`'s source contains `suite_gate(`.
`dyad/tests/test_package.py:160-180` `test_evidence_runs_the_suite_once`: empties the registry,
drops the nesting flag so `_SUITE_RAN` alone must stop it, runs `cmd_guards` and asserts no
`[Rule-12]` line and no call into `cmd_tests`; then asserts by `inspect.getsource` that
`_SUITE_RAN` appears in `suite_gate` (`:178`) and `_SUITE_RAN = True` in `check_rule_12` (`:179`)
and in `cmd_tests` (`:180`).
Moment: Rule-12's suite, i.e. `package.py check` in the runner and `dyad check --guards --pre-push`
whenever the suite is not skipped.
Reach: rows 52 and 53 — met, and the behavioural half of `test_evidence_runs_the_suite_once` would
catch a regression of either. **A fourth entry point is not reached**: the three
`inspect.getsource` assertions name `check_rule_12`, `cmd_tests` and `suite_gate` as literals, so a
new function that spawns `unittest` without the gate passes this test unchanged. The mode is
"a call site added without its call graph", and this fence enumerates the call sites — which is the
same shape as incident mode H.
Shipped: `dyad/tests/test_package.py:151`, `:160`, `:178-180`. Recurred after it shipped: yes — row
106.

**M4 — the registry's row filter and preserved `d-work` cell (shipped).**
`dyad/scripts/package.py:751`: `rows += [(c, cc.guard().version(REPO / "crafts" / c), REPO.name) for
c in bundled if cc.unmodified(target, c) is None]` — a bundled craft's row is asserted by the core
install only where the installed tree is not already recorded unmodified. The comment at `:746-750`
states the mechanism being guarded against: "`dyad craft install` of that same craft writes a richer
row (its archive as `source`, its d-work), and re-asserting this one would clobber it on the next
core install — the two commands would then ping-pong and neither install would be `0 changes`".
`dyad/scripts/craft.py:94-96` in `record_install` preserves the existing `d-work` cell
(`"d-work": rows.get(name, {}).get("d-work", "")`) and writes the registry only when some row
differs (`:96-101`), so a second install of the same source is 0 changes.
`dyad/scripts/craft.py:71-77` `unmodified` is the single predicate both sides use.
Moment: at `dyad install` and `dyad craft install` run time — not at any push gate.
Reach: row 106 — met, and this is the fix its consequence names. Rows 52 and 53 — not reached.
Shipped: `dyad/scripts/package.py:751`, `dyad/scripts/craft.py:94`, `:71`. Recurred after it
shipped: not yet; it is three days old.

**M5 — the end-to-end sequence test (shipped, and it pins this one sequence).**
`dyad/tests/test_craft.py:195-200` `BundledRowTests` docstring names the mechanism and the CI step.
`:201-219` `test_bundled_craft_has_an_unmodified_row_after_a_core_install` asserts
`craft.unmodified(d, name)` is not None after a real core install and that re-recording the same
rows is 0 changes.
`:222-249` `test_core_install_does_not_clobber_a_bundled_craft_row_a_craft_install_wrote` runs the
full CI sequence — export, `craft install --dwork 156`, `craft install` again (asserting ` 0
changes`), then `package.py install` (asserting ` 0 changes`). Its docstring at `:224-228` says
why: "Found by running the CI sequence, not by the unit test above, which is why it is pinned here."
Moment: Rule-12's suite.
Reach: row 106 — met for a regression of this exact pair of writers. A *third* writer of
`crafts/REGISTRY.md`, or a second writer of any other store, is not reached.
Shipped: `dyad/tests/test_craft.py:222`.

**Live surface read today (none of M1 to M5 fences the mode as such):**
`crafts/REGISTRY.md` still has two write paths. `dyad/scripts/craft.py:57-60` `write_registry` is
called from `record_install` at `:101` and, independently, from `cmd_install` at `:227` (`rows[name]
= new; write_registry(repo, rows); changed += 1`). `write_registry` carries no name-mangling and no
precondition, so a third caller is one line away. The suite is likewise spawnable without the gate:
`subprocess.run([sys.executable, "-m", "unittest", …])` appears at `dyad/scripts/package.py:227`
inside `check_rule_12` and through `run_suite` at `:409-417` (the `-m unittest` argv at `:413`), and nothing refuses a fourth caller of
either.

## Remediation candidate, under attack
One fence: make each guarded thing reachable only through a chokepoint that refuses a second entry
itself — a fail-loud check in the sense Rule-12 property 1 names. Concretely, two chokepoints:
(a) a module-level `spawn_suite(...)` in `dyad/scripts/package.py` that is the only function calling
`unittest`, and that raises when `DYAD_NO_NESTED_TESTS` is set or `_SUITE_RAN` is already true, so
the gate cannot be omitted by a new caller; and (b) `write_registry` renamed `_write_registry` with
`record_install` its only caller, `cmd_install` routed through it. The exact moment: (a) at the
first attempt to spawn the suite in any process, every time; (b) at the one registry write, every
time — both in-process, before the side effect, not at a push gate.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Easy agreement (Rule-9 Conditions): "one chokepoint" is the obvious fix, so attack it. A chokepoint is still a call site: a new entry point can call `subprocess.run([sys.executable, "-m", "unittest", …])` directly, or write `crafts/REGISTRY.md` with `Path.write_text`, and the chokepoint never sees it. Python has no private functions. | confirmed | "Impossible to bypass" does not survive. "Impossible to bypass by accident" does: the `_` prefix and a raising chokepoint make the omission deliberate and visible in review, and `crafts/syseng/guards/naming.py`'s `symbol:` kind (module docstring, `:19-20`) is the existing shape for asserting which module defines which top-level name — so the residual bypass is checkable, not merely hoped against. |
| 2 | The chokepoint's own test would pin the caller set by name, exactly as `dyad/tests/test_package.py:178-180` does today — mode H inside mode J's fence, and a fifth caller passes it. | confirmed | A by-name test does not survive. What survives is a derived assertion: scan `dyad/scripts/*.py` and every craft's code globs for the spawn token and the registry-write token, and fail when the set of modules holding it is larger than one — the shape `naming.py`'s `env:` kind already uses, which "fails either way: unlisted or stale" (`crafts/syseng/guards/naming.py:18-20`). |
| 3 | Coverage: (a) reaches rows 52 and 53; (b) reaches row 106. Each half reaches exactly the rows its own d-work already fixed, so the candidate buys generalisation and nothing else — no row of this mode would have been caught by it that is not already caught. | confirmed | The candidate's value does not survive as remediation of the logged rows. It survives only as prevention of the *next* row, and the mode's own evidence for that is row 106 post-dating rows 52 and 53 by thirteen days on a different guarded thing. Stated as that, not as a fix. |
| 4 | A raising chokepoint is a fail-loud check, and the vocabulary's own definition restricts those to "a boundary, a state transition, an impossible condition … where control passes once per process or rarely, never per item, with no off-switch". The suite spawn passes once per process, so (a) qualifies; the registry write passes once per install, so (b) qualifies. But a raise in `cmd_evidence`'s path would turn a doubled call into a crashed evidence run, and the evidence block is what Rule-2's Binding rests on. | survives, scoped | Only with the raise placed so that the *second* call is refused and the first still completes — i.e. the chokepoint returns the first run's result on a second entry rather than raising, and raises only when the two entries disagree about scope (a full run after a partial one). Otherwise the fence makes `check --evidence` fragile at exactly the moment Rule-14 property 3 needs it. |
| 5 | The instrument that caught all three rows was running the thing end to end, not a unit test, and `dyad/tests/test_craft.py:222` already institutionalises that for one sequence. The cheaper candidate is therefore "add an end-to-end case per externally-sequenced path", not a chokepoint. | survives, scoped | Both are admissible and they are not alternatives: the end-to-end case detects, the chokepoint prevents, and the mode's three rows were all detected and none prevented. Scoped survivor: the chokepoint is the fence, and the end-to-end case stays the instrument — but an end-to-end case per path is itself an enumeration of paths, so it cannot be the fence. |

Read together: the chokepoint survives as prevention with the second-entry behaviour of attack 4,
the by-name test does not survive, and the candidate's claim on the logged rows does not survive.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes.

What the row would say: *one chokepoint per guarded thing, plus a derived check that there is only
one — route every `unittest` spawn through a single `spawn_suite` in `dyad/scripts/package.py` that
consults `DYAD_NO_NESTED_TESTS` and `_SUITE_RAN` itself and returns the first run's result on a
second entry; rename `craft.write_registry` to `_write_registry` with `record_install` its only
caller and `cmd_install` routed through it; and add a `syseng` check, in the shape of
`naming.py`'s `env:` kind, failing when more than one module of `dyad/scripts/`, `dyad/guards/` or
any craft's code globs holds the suite-spawn token or the registry-write token. refs: 155, 228.*

Which rows it would have caught: rows 52 and 53 (the suite chokepoint) and row 106 (the single
registry writer) — all three, though each is already fixed at its own site, so the row's claim is
on the next occurrence rather than on these.

The mode is not fenced today: `dyad/scripts/craft.py:57` `write_registry` has two callers (`:101`,
`:227`), the suite is spawnable from any new function, and the one test that pins the gate
(`dyad/tests/test_package.py:178-180`) names the three known sites as literals. The most recent
occurrence (row 106, 2026-10-07) is three days old.

## Delta 2026-10-26 (d-work #472, seat audit-e73be78c)

Rows from the delta of 2026-10-26 (index `2026-10-10-incident-failure-modes.md`, its section of that date, where the reconciliation, the code read at `d36b1bd` and the attacks are).

- **218, 219, 220, 221** (2026-10-25; 29 closes from 2026-10-15 to 2026-10-25): #202's close path rebound `refs` to its list of branches in an added loop, and the verb wrote that name into the row. One mechanism, four rows; Q is secondary (no guard read the shape, and `row.refs->row` reads only `#N`). Fenced by #439: the loop moved into `landing_refusal`, and `rows.refs_shape_problems` (`rows.py:206`, called in the transaction check) refuses a bracketed `refs`. 0 rows on `main` carry it. The fence covers one field's shape and not the mechanism: a rebind written into another field would pass. **7 rows.** Status: exit 1 for the refs shape; the mechanism stays open.
