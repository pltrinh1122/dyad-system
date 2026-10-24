# Incident mode G — a flag taken as a positional argument

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10, 5 rows.*

## Definition
A verb's argument reader accepts a token beginning with `-` as data — a title, an output path, a
destination, or nothing at all — because the reader is positional and holds no list of the flags that
verb knows, so the flag is consumed as a value and the verb's real work runs on it.

**What would have to change.** Every entrypoint verb would have to refuse an unrecognised
`-`-leading token at dispatch, before any work or write, from one shared reader that knows each
verb's flag set — rather than each verb inspecting its own `argv` positionally.

Boundaries against the neighbours it is most easily confused with:
- **N, a target named by an ambiguous pattern** — N's token is a legitimate value whose pattern
  selected more or less than intended; G's token was never a value at all and the parser had no
  concept of it. Separating test: strip the leading `-` — if the token would then be a sensible
  value, it is G, not N. Boundary rows: N holds row 44, row 54 and row 56, all `sed`/glob/`grep`
  patterns over real content.
- **S, a form typed from memory** — S's fault is at the writing end, against a readable definition
  the Agent did not read; G's fault is at the reading end, in code, and the Agent's typing was
  correct for the documented usage. Separating test: was the string the Agent typed the right
  string? In all five G rows it was.
- **M, no legal order, no verb** — M has no command that can do the thing; G has the right command
  doing the wrong thing with the right words. Separating test: does a correct invocation exist? For
  G it does and is one token away.
- **R, a derived key that does not identify** — R's bad value is computed; G's is a literal the
  Operator or Agent typed, passed through unexamined. Boundary: row 50 sits closest, because the
  flag became an immutable key (a row title), but the mechanism that put it there is the positional
  read, not a derivation.

## Incidents (5)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14 | #13 | `craft.py export sysarch --help` wrote a stray file literally named `--help` | positional-argument parsing took `--help` as the output path, not a flag |
| 2026-09-22 | #116 | `dyad dwork new --help` allocated id 116 and wrote `rows/116.md` with `title: --help`, a real row for a help request | `dwork new` took its first argument as the title with no flag parsing, so the allocator ran and the row file was written |
| 2026-09-23 | #128, #135 | seven backlog rows were written with `title: --backlog` and their intended title text in `refs`; six reached `main` and their titles are immutable | `dwork new --backlog "<title>"` took `a[1]` as the title and the first non-flag positional as `refs`, so flag became title and title became refs |
| 2026-09-23 | #128 | rows #129 to #134 were born titled `--backlog`, the intended title landing in `refs`, found 2026-09-29 by #133 | `dwork new` took the first argument as the title without a flag parse and nothing refused a title beginning with `-` |
| 2026-10-02 | #203 | a drafting subagent ran `dyad/bin/dyad check --help` to learn `--tests` syntax and started a full `dyad check` that no plan named, about 120 s | the entrypoint reads `--help` after `check` as no option at all, so `check` runs its default |

Rows 50 and 66 are two log rows over one event, written in different d-works (#128/#135 and #128):
50 is the discovery pass, 66 the later record under the fix. Counted as the reconciled set counts
them, two rows, one event — so five rows, four distinct events, across four subcommand forms:
`craft export`, `dwork new`, `dwork new --backlog`, `check`.

## Pattern
All five share one shape: the verb's reader is positional and has no closed flag set, so a
`-`-leading token is indistinguishable from a value. The log itself names the generalisation failure
each time — row 46 says of row 15 that it was "never generalised beyond the one command it was found
on"; row 88 says it is "now on a fourth subcommand form after `craft export`, `dwork new` and `dwork
new --backlog`". The per-command fix is the recurrence mechanism, not an incidental detail.

Recurrence evidence, mitigation by mitigation:
- Row 46's consequence names a candidate — argparse subparsers plus one `--help` test per subcommand
  — surfaced 2026-09-22 in `agent-corpus/audits/2026-09-22-incident-mode-g.md` (d-work #123). Rows
  50, 66 and 88 all post-date it. Row 88's own consequence says so: "Mode G's remediation (`--help`
  exits 0 and runs nothing, per subcommand) stays open".
- Row 66's consequence names a shipped fix: "#133 makes `dwork new` refuse a title beginning with
  `-`". Row 88 (2026-10-02) post-dates it, on a verb that fix never touched.
- Rows 50 and 66 both post-date row 46's own event by one day, on the same verb, with a second flag.

## Mitigations (phase 2)

**M1 — the `dwork` flag table and positional/flag split (shipped).**
`DWORK_VERB_FLAGS` at `dyad/scripts/package.py:825-828` declares, per verb (`new`, `state`, `list`),
the value flags it takes, the bare flags it takes, and the most positionals it accepts.
`dwork_args` at `dyad/scripts/package.py:830-844` splits `argv` into positionals, flag values and
bare flags by position, never by a second `index()` lookup. `cmd_dwork` refuses the leftovers at
`dyad/scripts/package.py:909-914`: `extra = sorted((set(vals) - takes) | (bare - flags))` then
`sys.exit(f"refused: dwork {verb} does not take {' '.join(extra)}")`.
Moment: inside `cmd_dwork`, before any row or provenance write, and before the id allocator's
`git fetch` — reached at every `dyad dwork new|state|list` invocation, whoever runs it.
Reach: row 46 — met (`dwork new --help` now gives `refused: dwork new does not take --help`, since
`--help` lands in `bare`, verb is `new`, and `--help` is not in that verb's flag set). Rows 50 and
66 — met (`--backlog` is now a declared bare flag at `package.py:826`, so it leaves `pos` and the
title is `pos[1]`). Row 15 — not reached: `craft.py` has its own dispatch. Row 88 — not reached:
`check` never enters `cmd_dwork`.
Shipped: `dyad/scripts/package.py:825`, `:830`, `:909`. Recurred after it shipped: yes — row 88,
2026-10-02, on `check`.

**M2 — `dwork new` refuses a title beginning with `-` (shipped).**
`dyad/scripts/package.py:938-941`: `if a[0] != "new" or title.startswith("-"): sys.exit(f"refused:
usage: dwork new <title> …, the verb first")`.
Moment: inside `cmd_dwork`, before the allocator and before `dyadlib.write_row`.
Reach: rows 50 and 66 — met, and this is the fix their consequence cells name (#133). Row 46 — met,
redundantly with M1. Rows 15 and 88 — not reached; neither writes a row.
Shipped: `dyad/scripts/package.py:939`. Recurred after it shipped: yes — row 88.

**M3 — the containment guard refuses an unclassified added path (shipped).**
`dyad/guards/infra/containment.py:146`: `fails.append(f"FAIL [{label}]: unclassified path: {path}")`,
with the tree form at `:172`. A repo-root file named `--help` is claimed by no zone.
Moment: `dyad/hooks/pre-commit` (which execs `containment.py staged`, `dyad/hooks/pre-commit:4`) at
commit time, and again on every push through `dyad check --guards --pre-push`.
Reach: row 15 — reached, but only after the write, and only if the file is staged; the log says the
file was removed before commit, so this guard was never the catch. Rows 46, 50, 66 — not reached:
`rows/<id>.md` is a classified agent-zone path whatever its title says. Row 88 — not reached: no
file was written at all.
Shipped: `dyad/guards/infra/containment.py:146`. Recurred after it shipped: yes, all five rows
post-date it.

**M4 — the row fence makes a title immutable (shipped, and here a cost not a mitigation).**
`dyad/guards/agent/rows.py:139-140` and `:206-207` fail any range that changes a row file's id or
title; `:239-242` refuses an id already naming different work at the base.
Moment: `dyad check --guards --pre-push`, and on `main`.
Reach: it is why rows 50 and 66's six wrong titles stand on `main` — row 50's consequence says "a
row's title cannot change (the fence refuses it …) so correcting them needs the Operator's
disposition to archive and reopen". It mitigates nothing of this mode and converts one occurrence
into permanent corpus damage.
Shipped: `dyad/guards/agent/rows.py:139`.

**M5 — the candidate of 2026-09-22, never built (candidate).**
Row 46's consequence names it: "argparse subparsers for the affected commands plus one test per
subcommand asserting that `--help` exits 0 and writes nothing", surfaced in
`agent-corpus/audits/2026-09-22-incident-mode-g.md` (d-work #123).
Read today: `grep -rn "\-\-help" dyad/tests/ crafts/*/tests/` returns exactly one hit,
`dyad/tests/test_package.py:972`, a docstring sentence about the invariant pass — no test anywhere
asserts a `--help` exit code or that it writes nothing. `argparse` appears in no module of
`dyad/scripts/`. Candidate, not shipped. Row 88 post-dates it by six weeks.

**Live surface read today (none of M1 to M4 reaches these):**
- `dyad check --help` → `dyad/scripts/package.py:1062` admits `check`, `:1064-1073` match none of
  `--evidence`, `--pr`, `--guards`, `--list`, `--tests`, so `:1074` calls `cmd_check()` and runs the
  invariant pass, Rule-11's check, Rule-12's whole suite and every guard. Row 88 exactly, unfixed.
- `dyad craft export <craft> --help` → `dyad/scripts/craft.py:171`, `out = Path(a[1]) if len(a) > 1
  else …`, then `distribute.build(repo, …, out)` at `:172`. Writes a file named `--help`. Row 15
  exactly, unfixed.
- `dyad build --help` → `dyad/scripts/package.py:1074` calls `cmd_build("--help")`;
  `dyad/scripts/package.py:728` passes it straight to `distribute.build` as the archive path.
- `dyad install --help` → `dyad/scripts/package.py:1074` calls `cmd_install("--help")`;
  `dyad/scripts/package.py:741` resolves it through `hostadapter.resolve` as the destination repo.
- `dyad bundle build --help` → `dyad/scripts/package.py:795`, `out_dir = Path(a[1])`, then
  `out_dir.mkdir(parents=True, exist_ok=True)` at `:801`.
- `dyad check --tests --help` → `dyad/scripts/package.py:1073` hands `--help` to `cmd_tests` as the
  dotted target.
I could not verify these five by running them: each would write a file, a directory or a 120 s
suite in the live worktree, and this subagent may take no such action. They are read from the code
paths cited.

## Remediation candidate, under attack
One fence: a shared `verb_args(verb, argv)` in `dyad/scripts/dyadlib.py`, driven by one table of
`{verb: (value flags, bare flags, most positionals)}` — the `DWORK_VERB_FLAGS` discipline lifted out
of `cmd_dwork` — called by the dispatch in `dyad/scripts/package.py`'s `__main__` block and by
`craft.main`, which refuses any unrecognised `-`-leading token and prints that verb's docstring for
`-h`/`--help`, exiting 0. The exact moment: at CLI dispatch, before `cmd_*` is entered — so before
any guard, any suite, any allocator and any write.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | "argparse everywhere" is the obvious fix and is stdlib, so no Rule-14 row is needed. But argparse needs each verb's flags declared as subparser code, and the usage text today lives in `package.py`'s module docstring (`dyad/scripts/package.py:2-40`) and `craft.py`'s (`:2-25`), which is what `sys.exit(__doc__)` at `package.py:1063` and `print(__doc__)` at `craft.py:239` print. Two declarations of one form is mode S's own mechanism, planted in the fix for mode G. argparse also replaces the refusal wording that existing tests read, so every CLI test changes in the same PR. | confirmed | "argparse everywhere" does not survive. A refusal driven by one data table, with the docstring still the single usage text, does — the shape `DWORK_VERB_FLAGS` already is. |
| 2 | The candidate is per-verb again, one level up: a sixth verb form added without a table row repeats the mode, exactly as four forms did in four d-works. | survives, scoped | Only if the table is the dispatch: a verb absent from the table must be refused rather than defaulted, so adding a verb without its row fails loudly at its first invocation instead of silently falling through. That inverts `package.py:1062`'s current default-on-unknown. |
| 3 | Coverage: `--help` handling reaches rows 15, 46 and 88 only. Rows 50 and 66's flag was `--backlog`, a real flag of the verb taken as the title positional — no `--help` test would ever have fired. | confirmed | The candidate is two halves, and must be stated as two: the dispatch refusal (rows 15, 46, 88) and the positional/flag split (rows 50, 66), the second already shipped for `dwork` alone at `dyad/scripts/package.py:830-844` and nowhere else. |
| 4 | Refusing every unrecognised flag changes `dyad check --anything` from "run the default" to "refuse", and `dyad/hooks/pre-push:4` runs `check --guards --pre-push`. A host whose installed core predates a hook flag would have every push refused rather than degraded, and Rule-11 property 2 makes a core install and a host's hooks separately versioned in practice. | survives, scoped | Only with the refusal naming the verb's known flags and the package version, and with `--pre-push` tolerated by any `check` that knows `--guards`. Otherwise an upgrade-order skew turns a cosmetic defect into an unpushable repo. |
| 5 | Easy agreement (Rule-9 Conditions): the fix looks free, so attack its necessity. `dyad/guards/infra/containment.py:146` already refuses a tracked `--help`, and `dyad/scripts/package.py:939` already refuses a `-`-leading title, so the harm is bounded at both ends. | refuted as a replacement | Neither reaches row 88, which wrote no file and allocated no row and cost 120 s of a planned node; neither reaches rows 50 and 66, whose paths were legally classified and whose titles are now immutable on `main` (`dyad/guards/agent/rows.py:139`). A downstream path guard is not a fence on an argument reader. |
| 6 | The candidate is package code and carries package cost: Rule-12 property 1 (a mechanical check that runs), the syseng test mapping `crafts/syseng/guards/tests.py` (a new `dyad/scripts/` module needs `dyad/tests/test_<n>.py`), and `crafts/syseng/guards/naming.py`'s `symbol:` lines. | survives, scoped | Admissible on Rule-13 property 1: argument reading is a recurring task done by inference, and recurrence proposes code. Scoped to a function in the existing `dyadlib` plus one table, never a new module and never a second dispatch. The check it carries is the per-verb `--help` test row 46's candidate already named. |

Read together: the dispatch refusal survives as the fence, the framework does not, and the mode's
own history (four subcommand forms, four d-works) is the argument for putting it at the dispatch
rather than in a fifth verb.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes.

What the row would say: *one shared argument reader at CLI dispatch — a `{verb: (value flags, bare
flags, most positionals)}` table in `dyadlib`, consulted by `package.py`'s `__main__` and
`craft.main`, that refuses an unrecognised `-`-leading token before the verb runs and prints the
verb's docstring for `-h`/`--help` with exit 0, plus one test per verb asserting `--help` exits 0,
writes nothing and spawns no suite; a verb absent from the table is refused, not defaulted.*

Which rows it would have caught: row 15 (`craft export sysarch --help`), row 46 (`dwork new
--help`), row 88 (`check --help`). Rows 50 and 66 are caught by the positional/flag split already
shipped for `dwork` (`dyad/scripts/package.py:830-844`, `:939`) and would be caught on any other
verb once that split is shared.

The mode is not fenced today: three of the five rows' own verbs are fixed, and the five live
surfaces read above (`check`, `craft export`, `build`, `install`, `bundle build`) are not. No
existing `backlog` row names this fence — the candidate has lived in
`agent-corpus/audits/2026-09-22-incident-mode-g.md` (#123) as prose since 2026-09-22 and recurred
once since, which is the failure the hardening play-book's Conduct section names.

## Delta 2026-10-24 (#259 revision 5; 5 → 9 rows)
**Rows added:** 159 (#301, `session touch --help`, cloud), 182 (#321, `session touch --help`, terminal,
hours later), 196 (#372, `session touch --help`, counsel's registration), 213 (#401, `session --help`
read as a root path). Four recurrences on one command family across four seats and three weeks, with
#268 `backlog` against the mode throughout.
**Mitigations re-read from the code.** `sessions.main` (`sessions.py:449-488`): the `touch` loop skips
any word it does not recognize (`:456`) and falls through to `touch_from_open_rows` when no `-r`/`-f`
survived; the verb-less path takes `a[0]` as a root (`:484`). `dwork` alone has the flag table
(`DWORK_VALUE_FLAGS`, `package.py:902-904`). Unchanged since 2026-10-10 except `name` added (#379).
**Recurrence after a mitigation shipped:** all four post-date #133's per-command fix and are on the
verbs it did not cover — the measurement attack 7 of the 2026-10-10 record asked for, answered: yes,
four times.
**Exit after the delta:** exit 2 as proposed (one dispatch-level reader); #268 `backlog`, nothing
built. The cheapest reach for three of the four rows is one line: `touch` refuses an unknown word.
