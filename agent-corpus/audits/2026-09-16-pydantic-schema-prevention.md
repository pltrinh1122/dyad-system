# Audit — what a pydantic schema plus mechanical verifiers would have prevented (d-work #56)

Prompted: "perform an audit sweep for incidences and errors (in chat history) that could have been
prevented if 'pydantic' was used to define all the schema along with mechanical verifiers...
at the end of the audit, i want an evaluation for migrating to 'pydantic' schemas."

Scope: all 25 rows of `agent-corpus/audits/INCIDENTS.md` as it stands at this d-work's base
commit, plus two session errors that occurred but were never given their own row (named below,
each with why). Every row is classified once against the rubric below; a row bundling more than
one distinct cause is split and each part classified separately.

## Rubric
- **A — schema-preventable.** A pydantic model with typed fields and a validated constructor,
  used at the point of construction, makes the specific mistake unrepresentable or immediately
  rejected — not merely detectable later by a guard.
- **B — schema-assisted.** A model helps (usually by making an existing, already-correct check
  run *earlier*, at construction, or by unifying two writes that must stay in lock-step into one
  operation), but the rule it enforces is owned by a Rule that governs more than one entity's own
  fields (a zone, a ratification sequence, a cross-file consistency) — the schema is not, by
  itself, the fix.
- **C — out of reach.** Environment, CI, concurrency, process/attention discipline, analysis
  error, prose, or the *shape* of a store (files vs. one blob) — no entity's field types bear on
  it.

## Classification

| # | Incident (date, d-work) | Class | Why |
|---|--------------------------|-------|-----|
| 1 | 2026-09-15 #1 — five red Actions runs (seed zones; v0.3.1 missing import; core/craft suites assumed sysadmin/lan-git) | C | A one-time zone-ratification event, a missing-file packaging assumption, and a test's hardcoded environment assumption — none is a field on a modeled entity. |
| 2a | 2026-09-14 #1 — row #1 committed already `planned` (no intervening `open` commit) | C | A *commit-sequencing* rule (how many commits, in what order) — Rule-15's phase discipline, invisible to a single row's own field values, which were individually valid. |
| 2b | 2026-09-14 #1 — the `-d` disposition text carried a doubled date | **A** | `cmd_dwork`'s `-d` handling *prepends* today's date by string concatenation onto whatever text the caller passed, with no check that the caller's own text is bare. A typed `Disposition` (a date field plus a bare-text field, joined only at render time, and constructed by one path that takes text with no leading date) makes handing it an already-dated string either rejected or a no-op. Recurrence 1 of 2 — see row 26 below. |
| 3 | 2026-09-14 #3 — a fix withdrawn after a concurrent session landed the identical one first | C | Cross-session race; no schema sees another session's clock. |
| 4 | 2026-09-14 #13 — `craft.py export sysarch --help` wrote a file literally named `--help` | C | Positional CLI-argument parsing, not an entity's data. (Adjacent, not equivalent: a typed CLI-args model — `pydantic-settings` or similar — is a different tool than the one this audit was asked to evaluate, and is named here only so the distinction is not silently lost.) |
| 5 | 2026-09-14 #16 — row #16 committed already `planned`, "same pattern as #1's" | C | Same sequencing rule as 2a; the row's cause note does not claim a second doubled date here. |
| 6 | 2026-09-14–15 #13, #16 — `v0.3.2` release 403, cause still unknown | C | Hosting/permissions; the incident's own text says the cause "is not yet known." |
| 7a | 2026-09-15 #17 — falsification-record path picked wrong for its zone (core vs. craft naming pattern) | B | The naming table (`naming.py`) already validates this pattern *mechanically* — but only when the guard runs, after the plan is written. A plan model that resolved and validated each touched path's naming kind at construction would have caught this before the file was ever created. The table and its guard are naming's own Rule; a plan model consuming them is assistance, not a new schema of its own. |
| 7b | 2026-09-15 #17 — two zones grouped into one PR | **B** | `containment.py zones` already computes a path's zone *mechanically* — again, only when the guard runs. A `Plan` model whose constructor maps every touched path to a zone and asserts they are all equal would fail at plan-writing time instead of at push time. This is the clearest B in the set: the check exists, owned by Rule-1; a model would only move it earlier. |
| 8 | 2026-09-15 #17 — falsification file uncommitted before the scratch-install suite first ran | C | Staging order in one turn's shell commands, not a value. |
| 9 | 2026-09-15 #18 — a plan-`Y` disposition recorded before the Operator was actually asked | B | Caught, as designed, by `agent/provenance` property 5 — an *inspection-time* cross-file count check (row `disposed` entries vs. provenance entries) that already exists and worked. A model that made "append a disposed entry" and "append the matching provenance entry" one atomic constructor call, rather than two independently-callable writes, would remove the chance to do one without the other — but the rule it protects (ask before recording) is Rule-3's, not a field type. |
| 10 | 2026-09-16 #22 — a host action run before its plan-`Y` | C | Rule-8 authorization sequencing; a schema for host-action classes does not stop an agent from acting before asking. |
| 11 | 2026-09-16 #22 — a reference misdiagnosed as unrecoverable without fetching first | C | Analysis error (a conclusion drawn from an incomplete local clone), not a construction defect. |
| 12 | 2026-09-16 #22 — a `VERSION` bump would have dragged `BUNDLE.md` into a two-zone plan | **B** | Same shape as 7b: a zone-computing `Plan` model construction check would have caught the cross-zone drag immediately; the precedent it violated (versions bump only in release d-works) is craft practice, not a field. |
| 13 | 2026-09-16 #22 — branches cut from a stale `main`; a rebase regressed row `#6` | C | Fetch-freshness and a concurrent session's own completed work; no entity's fields were malformed. |
| 14 | 2026-09-16 #30 — duplicate work on a concurrent session's d-work; two id collisions with direct pushes | C | The concurrent-allocator race itself (this session's own #32 later closed part of it — not with a schema, with a branch-side diff check, `check_id_collisions`, over what the *base* already holds). |
| 15 | 2026-09-16 #6 — the mode correction set every `.py` to 644, breaking the pre-commit hook | C | A tracked-mode/tooling defect, not a data value. |
| 16 | 2026-09-16 #6 — a wrong stated cause for 108 mis-mode paths, retracted | C | An analysis error, retracted on better evidence — never a constructed value. |
| 17a | 2026-09-16 #26, #34 — an id assumed rather than read from the allocator (twice in one hour) | **A** | The one thing every occurrence of this family shares: a row/provenance filename chosen from a *guess* rather than the allocator's own return value. A model whose only row-constructing entry point is `Row.allocate(...)` — which calls the allocator and returns an object already carrying the real id, with no other way to obtain one — makes "write `<guessed-id>.md` first" a type the caller cannot construct. Recurrence 2 of 3. |
| 17b | (same row) — the second time, a peer's real `#27` plan and provenance were overwritten on `origin/main` for about a minute | **A** | Same defect, worse consequence; not a separate cause. |
| 18 | 2026-09-16 #27 — the provenance record for `#27` first written as `26.md` | **A** | Same family, third occurrence: "`dyad dwork new` and the `cat > provenance/<id>.md` were issued in one command, so the file was named before the allocator's answer was read." Recurrence 3 of 3. |
| 19 | 2026-09-16 #25, #27, #35 — three `--no-verify` pushes, pre-commit hook broken | C | A blocked local hook (mode/exec-bit), worked around by hand each time per Rule-1's own stated procedure — infrastructure, not a value. |
| 20 | 2026-09-16 #35 — a presence file claimed every open/planned row in the ledger, not just this session's | C | `touch_from_open_rows` queries the *whole instance's* open rows rather than the calling session's own claims — an algorithm/filter defect. **Still live**: d-work #32 (this session's own later fix) added writer-collision detection but did not touch this function; it still pulls every open/planned row regardless of caller. Worth a fresh d-work of its own; a schema on `Row` or `Presence` does not fix a query that reads the wrong set. |
| 21 | 2026-09-16 #35 — a plan's own mutation item executed in the ledger commit that wrote the plan, before its batch plan-`Y` | C | Rule-3 Plan's authorization-before-mutation rule; conduct, not a field. |
| 22 | 2026-09-16 #32 — a plan's own item 7 not delivered, sequencing vs. `merge-disposition` | C | A preference/process interaction across two d-works, not an entity's construction. |
| 23 | 2026-09-16 #47 — a PR merged before the Done-`Y` was asked | B | The incident's own text: "no mechanical guard against an agent running a merge outside the `Y` flow." A typed ratification-state precondition on the merge action (refuse to call `merge_pull_request` while the row's state has no matching Done-`Y` disposed entry) would help — but Rule-2 already states this class of enforcement is "inference-only," because git cannot distinguish proposer from disposer; a schema-enforced precondition still depends on the same agent choosing to run it. |
| 24 | 2026-09-16 #48 — `dyad/tests` flaked under real memory contention on a shared host | C | Diagnosed, correctly, as external interruption — explicitly not a corpus defect. |
| 25 | 2026-09-16 #15 — a historical reference to `naming.md`'s own amendment 141, written in commit-message *prose*, parsed as a work-claim | C | `prs.py` deliberately treats the `d-work #<id>` text pattern in free prose as a citation (Rule-3's own design); the fix was wording, not a field — matching #56's own plan finding F4 for the analogous case. |
| 26 | *(not yet its own row)* — row `45`'s `disposed` entry was written `2026-09-16 2026-09-17 Y spinout (#32 Done-Y)`, a second, wrong date prepended onto text that itself began with a date | **A** | Identical mechanism to 2b, caught and corrected in the same turn before any push. Recurrence 2 of 2 for the doubled-date family — Rule-13 p1's "second occurrence proposes code" trigger has now fired. |
| 27 | *(not yet its own row)* — this session's own presence-file `writer` field (shipped in d-work #32 to fix F1) discarded this session's own prior `rows`/`files` claim minutes after being merged, warning that a "different, still-live process" owned the file, when the only other writer was this same session's own earlier CLI invocation | C | `_WRITER` is a per-*process* random id; `dyad session touch` runs as a fresh process every invocation, so a session re-touching its own file *always* looks like a different writer inside the 6-hour stale window. A logic/lifetime-choice defect in code written specifically to prevent incidents, not a value a schema would have typed differently — and a reminder that F3 (construction vs. inspection) applies to the guards themselves: `test_same_writer_reunites_silently` calls `touch()` twice *in-process*, where `_WRITER` is stable by construction, and never exercises the two-separate-invocations case that is the tool's only real usage. Undisposed; flagged to the Operator, no row opened yet. |

### Tally
- **Class A — 3 incident rows, 1 unlogged error, 5 total occurrences, 2 recurring families**
  (doubled date: rows 2b, 26 — 2 occurrences; id assumed before the allocator answers: rows
  17a/17b/18 — 3 occurrences).
- **Class B — 4 rows** (7a, 7b, 9, 12 nearly identical in shape; 23 similar but weaker, since
  Rule-2 already names its enforcement as inference-only).
- **Class C — 18 rows, 1 unlogged error (still live) — the majority.**

## The structural finding (why A is small and where it is)

The corpus already carries a schema in everything but name. `dyadlib.Row` is a dataclass;
`FIELDS`, `STATES`, `NEW_STATES`, `TRANSITIONS`, `CONTRACT` and every guard's own `INVARIANTS`
are declared, checked data; `describe()` already projects an entity card per guard
(`crafts/sysarch/rules/guards.md` calls `FIELDS` "the schema constant" outright — d-work #30's own
record, attack 1). Twenty-one modules declare a `FIELDS` tuple; twenty hand-roll `key: value` or
line parsing to fill it.

What is missing is not a schema — it is **typed values, built through a validating constructor**.
`parse_row_file` turns text into a `Row` with **zero validation**: every field but `id` is a bare
`str`; `opened` is a date-shaped string, `disposed` a semicolon-joined list of entries each shaped
`<date> <Y|N> <plan|done|merge #n|reason>`, `refs` a space-joined list of reference tokens — and
none of the three is parsed into anything but a string until a *later*, separate guard
(`rows.py`, `references.py`, `provenance.py`) inspects the file on disk.

That is the whole shape of every Class A incident: **the wrong value is built at a call site,
written to a file, and only then met — by a guard that runs later, if at all.** The two
recurring families are not two unrelated bugs; they are the same gap at two call sites:
`cmd_dwork`'s string-concatenation build of a `disposed` entry, and its id allocation built from
`max(local | remote)` with no type forcing the *caller* to use that value rather than a guess.
Every Class B incident is the mirror image at one level up: a **mechanically correct, already-
existing check** (the naming table, the zone table, the provenance count) that runs at
*inspection* time (a guard, at push or CI) rather than at *construction* time (when the plan or
the row is written) — Rule-12's own "verifiable code" gap between existing and *early*.

## Migration evaluation

**Verdict: migrate, narrowly and in stages — construction, not storage.**

**Stage 1 (closes the two Class A families).** Pydantic models for the ledger entities whose
*values* are built by code, not typed today: a `Disposition` (a `date` field and a bare-text
field, rendered only at serialization — makes a caller-supplied leading date either stripped or a
validation error, never doubled) and a `Row` id obtained only through one validated constructor
path (`Row.allocate(title, refs)`, calling the allocator and returning a `Row` that already
carries the real id — no other path to a `Row` accepts a bare int). `cmd_dwork`'s `new`/`state`
handlers build through these models instead of string concatenation. `parse_row_file` becomes
`Row.model_validate` over the parsed dict, so a malformed file fails at *read* time with a named
field, not silently as an all-`str` dataclass. This is a small, bounded change: one file
(`dyadlib.py`), the models it exports, and the two `cmd_dwork` call sites that build values today.

**Stage 2 (closes the strongest Class B, only if stage 1 pays for itself).** A `Plan` model whose
construction resolves every touched path's zone (via the existing `containment.zones` table) and
naming kind (via the existing `naming.py` table) and raises at construction on a mixed zone or an
unmatched kind — moving 7a/7b/12's already-correct checks from push-time to plan-time. This
reuses the existing tables; it does not duplicate them into a second schema.

**Not proposed:** rewriting the twenty hand-rolled parsers wholesale (#1's own attack 3 already
named a two-guards-at-once data-model change as a hazard, and F3 shows the parsers are the
*inspection* layer, not where the incidents originate); moving the store to JSON or any other
single-blob format (`schema-definition-language.md` attack 4 already stands, and this very d-work
supplied fresh, live evidence: the `INCIDENTS.md` merge conflict during #15's own close resolved
line-by-line because the file is text — a JSON blob would have forced a whole-object conflict);
touching Class C at all (nothing here reaches environment, CI, concurrency, or conduct).

**Cost, stated plainly.** `dyad check --evidence` — the block Rule-2's Binding reads to verify a
merge — is stdlib-only today. `pydantic-core` is a compiled wheel; putting a validating model on
that path means the evidence block depends on a wheel being importable in whatever environment
re-runs it. Rule-14 property 2 already admits pydantic to the kernel (d-work #31), so *membership*
is disposed — but the *evidence-path dependency* is a fresh cost this migration would spend, not
one already paid. Stage 1 is scoped to make that cost worth spending: two named recurrence
families, evidenced above, nothing speculative.

**Abandonment point.** If stage 1's models do not eliminate a doubled date or an assumed id in
practice — because the discipline that already stopped both (conduct: "never write `<id>.md`
before the id is printed") turns out to carry the weight, not the type — stage 1 is reverted with
nothing else touched: the store never moved, no guard was rewritten, and stage 2 was never
started.

Disposition: see ledger #56.
