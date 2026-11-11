# Play-book: unit and session tidy (the cabinet craft; #444, #640, #669)

The census of this system's units and sessions within one Claude Code account, and the tidy acts it proposes, toward
one state: the only sessions open are live seats and live desks, every title is its unit's name, and a unit whose
work has ended is retired. Steps: `crafts/cabinet/runbooks/session-tidy.md`, run as `dyad runbook run
cabinet:session-tidy <step>`. Read by the cos and by the unit whose charter holds the host. The decision at each unit
and session is `dmc:session-tidy`; opening a unit stays `dmc:unit-lifecycle`'s, whose two ending outcomes point here.

## Trigger
Session start, and the program's request. A census is a reading: an event is written only when it changes (#438).

## The boundary
The census reads the whole account list and tidies only this system's sessions: one attached to this repository, or
one a presence file names by holder. Every other session (another repository, no repository, a personal one) is
outside the system. It is counted, `outside: <n> sessions (not this system's; not read)`, and never classed,
proposed, retitled or archived, nor named or described in a report, relay, event or change-log row. Absence of
evidence never makes a session this system's (#669 A5).

## Steps
1. **Census** — `census`: the cos writes the account's own session list from `list_sessions` (`mine: true`) to a file,
   one `<session id> <owner/repo|-> [<title>]` line each, and passes it as `ACCOUNT`. The classifier,
   `crafts/cabinet/scripts/tidy.py`, reads it with the presence store, the rows, the mandates table and session
   reconcile's mismatch lines, and prints each of this system's units and sessions with its facts and its act.
2. **Classify** — by `dmc:session-tidy`: the boundary first, then each unit's and session's facts, then its act.
3. **Report** — one line per act, and the outside count, to the board of the unit whose charter holds the host.
4. **Propose** — one batch to the cos, in the record's order.
5. **Act** — on the operator's `Y`, the cos alone, in the record's order:
   - **re-home** each row by its own row, the operator's words relayed verbatim, before its unit retires;
   - **retire** a unit by the six changes the record's outcome lists: the unit's row, its mandates row and
     `paired-units` by the operator's own preferences PR (named in the batch, asked on its own), the board's unit
     table, its session archived once acknowledged, its presence file kept;
   - **archive** a session with `archive_session`: a hosting act, Rule-8 reversible with the undo
     `unarchive_session`, one change-log row per call;
   - **retitle** a session with `set_session_title`, to its unit name;
   - **register**: the session's own holder touches its presence file; no other unit writes it.
   Presence files are never deleted (Rule-16). No unit but the cos archives, retitles or acts on another unit; a desk is
   closed by its secretary when its topic's rows close.

## Question
One batch per census, relayed by the cos: `Y/N: tidy <unit or session>: <act>, …?`, each listed with its facts and
what it holds; a charter seat with nothing open is asked alone. A `Y` binds exactly the named acts; a preferences
change it implies is its own question.

## Evidence
The census output and its event id, the outside count (never its entries), the batch asked and its answer, and one
change-log row per archive or retitle call.
