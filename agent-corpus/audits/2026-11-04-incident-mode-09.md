# Incident mode 09 — a CLI verb takes unknown flags (--help) or malformed args as positionals or skips them, then writes or runs

*Per-mode record of `agent-corpus/audits/INCIDENTS.md`, d-work #571 (2026-11-04, seat audit-e73be78c); 12 of the 252 rows. Index: `2026-11-04-incident-failure-modes.md`.*

## Definition
a CLI verb takes unknown flags (--help) or malformed args as positionals or skips them, then writes or runs.

**What would have to change** (the derivation's one-sentence test): every entrypoint verb parses with a refusing parser (argparse), at argument parse.

**Predecessor:** mode G of the 2026-10-10 derivation and its deltas (`2026-10-10-incident-mode-g.md`), which stays where it is.

## Incidents

| row | date | d-work | view 1 |
|-----|------|--------|--------|
| 15 | 2026-09-14 | #13 | V1-08 |
| 46 | 2026-09-22 | #116 | V1-08 |
| 50 | 2026-09-23 | #128, #135 | V1-08 |
| 66 | 2026-09-23 | #128 | V1-08 |
| 88 | 2026-10-02 | #203 | V1-08 |
| 159 | 2026-10-15 | #301 | V1-08 |
| 179 | 2026-10-15 | #297 | V1-28 |
| 182 | 2026-10-15 | #321 | V1-08 |
| 196 | 2026-10-22 | #372 | V1-08 |
| 211 | 2026-10-24 | #373, #377, #398, #400 | V1-09 |
| 213 | 2026-10-24 | #401 | V1-08 |
| 217 | 2026-10-25 | #433 | V1-08 |

Secondary mechanism on rows: 159 (V2-29), 182 (V2-29), 196 (V2-29), 213 (V2-28), 217 (V2-29). Recurrence after a mitigation the cells describe: yes: 88, 159, 179, 182, 196, 211, 213, 217 after #133's '-' title refusal on dwork new.

## Mitigations at `eeea31fc` (read from the code, never from an audit's prose)

| mitigation | path:identifier | moment | rows reached | rows not reached | shipped/candidate | recurrence after |
|---|---|---|---|---|---|---|
| `dwork` verbs refuse undeclared flags; flag values never positional; title cannot start with `-` | `package.py:1855` `DWORK_VERB_FLAGS`, `:1862` `dwork_args`, `:2018-2022`, `:2070` | parse | 46, 50, 66 | 15, 88, 159, 179, 182, 196, 211, 213, 217 (other verbs) | shipped 2026-09-29 (`0d59f1a3` #191, `06d4a55b` #133) | yes: 88, 159, 179, 182, 196, 211, 213, 217 after |
| `session touch` refuses any word but `-r`/`-f`; `--help` exits before writing | `sessions.py:715-723` | parse | 159, 182, 196, 217 | 211, 213 | shipped 2026-10-28 (`46924789`, #479) | none after |
| `merge`, `board`, `inbox` print usage on `-h/--help` | `merge.py:145`, `board.py:423`, `inbox.py:358` | parse | — | — | shipped 10-31 / 11-02 | — |

Still live at HEAD (read, not run): `dyad check --help` falls to `cmd_check` (`package.py` `__main__`: `--help` matches no branch, last line runs `cmd_check`) — row 88; `dyad session --help` runs `check_package(Path("--help"))` and prints `ok [sessions]` (`sessions.py:767-771`) — row 213; `dyad craft export <c> --help` writes a file named `--help` (`craft.py:182`, `out = Path(a[1])`) — row 15; `touch -r "a b"` keeps the quoted value whole (`sessions.py:305`) — row 211; `check --tests <unqualified>` is not refused (`package.py:872` `cmd_tests`) — row 179.

Closure: (2) backlog #268 (mode G). NEW fence: one refusing parser shared by every `dyad` entrypoint verb (unknown words and `-h/--help` handled before any write or run, `-r` values split on whitespace), with a test iterating every verb with `--help` and asserting no write and no run, at argument parse; owner engineer.

## Status
Exit 2 — backlog row; fence row proposed: **R-a** (index, Proposals).
