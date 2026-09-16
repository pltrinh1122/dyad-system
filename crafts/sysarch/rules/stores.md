# Stores (sysarch craft, Tended rule)

Read by Rule-16's kernel (`dyad/rules/RULE-16-concurrent-sessions.md`): the core Rule binds the
canonical row path (`<instance>/d-work/rows/<id>.md`, one file per d-work) and the transition
table (state never regresses). This rule is the *pattern* those sentences instantiate — the
file-per-instance store any craft store follows (rows, plans, ops scripts and events already do).
Text moved from Rule-16 Store by d-work #160 (#159: the transitions are operator-craft semantics
and stay); a Tended rule — any form, no Rule-4 block, no sweep. Terms: none of its own (`row
file`, `rendered view`, `transition` stay Agent terms, owner Rule-16). Code: `dyad/scripts/dyadlib.py`
(`read_rows`, `parse_row_file`, `format_row_file`) and `dyad/guards/agent/rows.py` (the fence) stay
core; this rule adds no check on core rows (plan #160 attack 13).

## The pattern
- **One file per instance, `key: value` lines.** A store is a directory of files, one per
  instance, named by the instance's id; each file holds its fields as `key: value` lines in a
  fixed order (`dyadlib.FIELDS` for rows). Two sessions editing different instances touch
  disjoint files and never merge.
- **A rendered view, untracked.** A table over the store (`LEDGER.md` for rows) is produced on
  demand (`dyad ledger`) and never tracked; the files are canonical, the view is generated
  (`distribution.md`).
- **Ids are allocated, never chosen.** `dyad dwork new` allocates `max(id on fetched
  origin/main, local) + 1`, warning and falling back to local ids alone if the fetch fails (d-work
  #32 F3 — a session sees the fallback, never a silent under-allocation). No session hand-edits a
  file. **Collision is caught at two different points, not one.** A direct push to `main` racing
  another session's id is rejected by git's own non-fast-forward — but on the PR path a collision
  is invisible to that check (a fast-forward add/add merge, or a silent overwrite if the branch was
  reset onto `main` first), so `rows.py` `check_id_collisions` (d-work #32 F2) checks every branch,
  before the push: a row id the range adds or modifies must not already exist at `base` under a
  *different* title, the signature of two sessions racing the allocator. Neither check makes a
  collision impossible — two sessions holding unpushed ids cannot see each other, which only a
  shared allocator (the LAN git server, #24) changes — only loud rather than silent, at the
  earliest point each path can reach.
- **Append-only under a fence.** A transaction guard on `main` (`rows.py` for rows; `events.py`
  for events) keeps the store append-only: a file is never deleted, its id and title are
  immutable, and a state change must be in the owning Rule's transition table.
- **Phase-ordered edits.** Edits to one instance follow Rule-15's phases: the planning phase
  writes the plan file and the state `planned`; the execution phase works branches, PRs and
  `done`. Whichever session holds a phase, the edits to one id are ordered by the transition
  table, never concurrent.

## Instances of the pattern
| store | path | fence |
|-------|------|-------|
| ledger rows | `<instance>/d-work/rows/<id>.md` | `dyad/guards/agent/rows.py` (transaction) |
| plan files | `<instance>/d-work/plans/<id>.md` | `dyad/guards/agent/plans.py` (shape) |
| run-book events | `<runbooks>/events/<instance>.jsonl` (one line per event) | `crafts/sysadmin/guards/events.py` (transaction) |
| ops scripts | `<ops>/<d-work>-<hN>-<slug>.sh` | `crafts/sysadmin/guards/ops_scripts.py` (shape) |
