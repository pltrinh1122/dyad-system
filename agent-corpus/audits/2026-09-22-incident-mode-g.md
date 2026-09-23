# Incident mode G — mechanism defect

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #123, child of #116 (2026-09-22).*

## Definition
A hook, guard, CLI or suite did not do what its design says. The departure is in a corpus
artifact's own behaviour, not in the work that artifact was judging: the Agent used the
mechanism as written and the mechanism produced the wrong outcome, or none.

Boundaries against the modes it is most easily confused with:
- **F (form error in a clerical record)** — F is the Agent writing a record in the wrong shape or
  order with a sound tool; G is the tool. Both appear under d-work #1: the row born `planned`
  (2026-09-14) is F, the suites assuming two crafts (2026-09-15) is G.
- **A (acting before the Operator's `Y`)** — A is an ordering step the Agent skipped. The three
  `--no-verify` pushes below look like A and are not: bypassing a hook that cannot execute is
  Rule-1's own prescribed procedure (Enforcement: run the guard by hand, record the observed line
  and the bypass, report an incident), so the departure belongs to the dead hook.
- **C (concurrent-session race)** — C is two sessions colliding on identity or id. G's `session
  touch` row is the mechanism built to *surface* such a collision failing to carry the signal;
  the race and the instrument for it are separate faults.
- **D (wrong cause asserted)** — D is a diagnosis stated then retracted. Both appear under #6 on
  2026-09-16: the hook dying at exit 126 is G, the `git add` explanation of the 755 modes is D.

## Incidents (6)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-15 | #1 | item (c) of five red Actions runs: the core and craft suites assumed the `sysadmin` and `lan-git` crafts were present, so `rule-11 package` ran red in a system without them | a suite that encodes one instance's craft set is not the reusable code carrying a mechanical check that Rule-12's Intent asks for; the red was the suite's, not the tree's |
| 2026-09-14 | #13 | `craft.py export sysarch --help` wrote a stray file literally named `--help` | the CLI took a flag as the positional output path; caught before commit, never tracked |
| 2026-09-16 | #6 | the mode correction set every `.py` to 644, including `dyad/guards/infra/containment.py`, which `dyad/hooks/pre-commit` exec'd by path; the hook dies at exit 126 in any fresh checkout | the modes were right per the syseng rules and the hook's invocation form was wrong, leaving Rule-1's only blocking enforcement vacuous everywhere but this mount |
| 2026-09-16 | #25, #27, #35 | three further commits pushed with `--no-verify`, two ledger-only to `main` and one per zone branch, while the fix for that hook was unmerged (PR #18) | consequence of the row above, not of the Agent's ordering: Rule-1 Enforcement prescribes exactly this bypass for a hook that cannot execute, and `containment.py staged` was run by hand and recorded in each commit message |
| 2026-09-16 | #35 | `dyad session touch` wrote `rows: 22 23 24 25 27 33 34 35` into `sessions/web-sysarch.md`; #33 and #34 were a concurrent session's rows, never this one's | the CLI derives `rows` from the ledger's open and planned set rather than from what the session claims, so the `files` overlap signal Rule-16 built the store for carries nothing |
| 2026-09-22 | #116 | `dyad dwork new --help` allocated an id and wrote `rows/116.md` titled `--help`; untracked, removed at once, the id then reallocated with the real title | #13's parse defect recurring on a second subcommand eight days later: `cmd_dwork` takes `a[1]` as the title with no flag parsing |

The last row entered `INCIDENTS.md` through the parent d-work's own work (plan #116, Mutation
item 2, on that plan's own falsification bullet, which first recorded it). Every date and d-work id
above is transcribed from `INCIDENTS.md`, none inferred.

## Pattern
All six are an artifact of the corpus behaving exactly as its code says and not as the rule that
names it says — a suite, a CLI twice, a hook, and the presence store's CLI — and no dyad guard
caught any of them: #1 surfaced as red Actions runs, #6 was found by a peer session's #24, and #13,
#35 and #116 were read off the output by the Agent (#116 by `git status`). What each cost differs,
and the log is explicit about it: #13's stray file and #116's stray row were caught before any
commit and never tracked, while #1's suite stood until that d-work's own two PRs and #6's hook left
Rule-1's blocking enforcement dead in fresh checkouts until #24 merged (PR #18) — the three
`--no-verify` pushes of the fourth row ran inside that window. No corpus content was lost in any of
the six.

The count is six in both plan #123 and plan #116's mode-G cell, and six rows of `INCIDENTS.md`
carry it, so no reconciliation was required.

What varies is closure. Two of the four mechanisms are shut at `1dd364f`, by three changes:
`package.test_suites` discovers every `crafts/<craft>/tests/` present (`dyadlib.craft_glob`)
instead of naming crafts; both hooks read `exec python3 "$(git rev-parse --show-toplevel)/…"`, so a lost
exec bit on a guard module can no longer kill them, and `crafts/syseng/guards/naming_rules.txt`
line 47 holds `dyad/hooks/*` at tracked mode `100755`. Two are live: `cmd_dwork` still builds
`dyadlib.Row(rid, a[1], …)` and `craft.cmd_export` still takes `out = Path(a[1])` with no flag
parse, and `sessions.touch_from_open_rows` still lists every `open` or `planned` row — visible now
in `agent-corpus/d-work/sessions/unnamed-8c933cda2944.md`, whose `rows:` line carries 114, 116–125,
81, 82 and 99. The mode's most recent occurrence, #116, is the one live mechanism recurring.

## Remediation candidate (falsified, not disposed)
As plan #123 states it, and as nothing decided here: every `dyad` subcommand that takes a
positional argument would parse flags before positionals, so that a leading-dash token never
reaches disk as a title or a path — `--help` exiting 0, printing usage and writing nothing — with
the core suite gaining one case per such subcommand asserting that no file appeared.

| # | attack | result | survivor |
|---|--------|--------|----------|
| G1 | The candidate covers mode G. | refuted | It covers 2 of the 6 rows (#13, #116) and is silent on #1, #6, #25/#27/#35 and #35. Restated as covering one of the mode's four mechanisms, the one that has recurred. |
| G2 | Then it is the wrong priority: the other mechanisms are still open. | refuted | At `1dd364f` the suite, the hook invocation and the hook's own mode are each closed (test-root discovery; `exec python3 <path>` in both hooks; `naming_rules.txt` line 47). Two mechanisms are live, and this candidate is one of them. |
| G3 | argparse — plan #123's named mechanism — is new code where a two-line refusal of a leading-dash positional would do. | survives scoped | Rule-12 property 1 asks that code entering the package carry its mechanical check; the check here is the test, which is the same whichever parser is used. The candidate holds with the test as the deliverable and the parser left open as a Rule-12 path choice. |
| G4 | A case per subcommand does not bind the next subcommand. | confirmed | `package.py` dispatches its noun subcommands by an `if`-chain (`__main__` at line 533, its arms at 535–548, each handing `a[1:]` to its own `cmd_*`); the dict at line 559 covers only `check`, `build` and `install`, which no noun subcommand reaches. There is no table naming them, so the cases must be hand-listed and a new subcommand ships untested by construction. The candidate survives only if it also names a dispatch table to enumerate — a widening not falsified here. |
| G5 | The remaining live mechanism, #35's row derivation, is already carried by an open row. | refuted | The incident's own consequence assigns it to backlog #32; #32 is `done` (`2026-09-16 Y done (merges PR #26)`) and its plan's findings F1–F4 are presence identity, branch-path id collision, silent allocator degradation and an unmemoized `session_id` — not the row derivation. No open row carries it. A second candidate is visible (`sessions.main` already accepts `-r`, so `touch` could record only what the session names) and is complicated by Rule-16 Presence, whose own wording — `rows` is "the space-list of d-work ids this session has open or planned" — is what the CLI implements literally. Surfaced, not folded in. |

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #123 (Rule-9 Form). Remediation
itself is a further Operator prompt on this row, never taken here.
