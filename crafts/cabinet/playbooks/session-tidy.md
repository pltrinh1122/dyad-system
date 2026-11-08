# Play-book: session tidy (the cabinet craft; #444, #640)

The census of open sessions and the consolidation it proposes, toward one state: the only sessions open are live
seats and live desks. Steps: `crafts/cabinet/runbooks/session-tidy.md`, run as `dyad runbook run cabinet:session-tidy
<step>`. Read by the cos and by the unit whose charter holds the host.

## Trigger
Session start, and the program's request. A census is a reading: an event is written only when it changes (#438).

## Steps
1. **Census** — `census`: the classifier, `crafts/cabinet/scripts/tidy.py`, prints each open session's facts
   (presence, rows, holder) and its class by `dmc:session-tidy`. On a cloud kernel a container sees only its own
   harness session (#434), so the cos transcribes the harness list from the operator's interface and passes it as a
   file; without one, sessions with no presence file are reported as not read.
2. **Report** — one line per class to the board of the unit whose charter holds the host.
3. **Propose** — to the cos, one batch in the record's order; an archivable session retires as
   `dmc:unit-lifecycle` says.
4. **Archive** — the cos archives each session the operator's `Y` named: a hosting act, Rule-8 reversible (undo
   `unarchive_session`), one change-log row per call. No other unit archives, retitles or touches another unit's
   presence; a desk is closed by its secretary when its topic's rows close.

## Question
One batch proposal per census, relayed by the cos: `Y/N: archive sessions <a>, <b>, …?`, each listed with its class
and what it holds; a charter seat with nothing open is asked alone. A `Y` archives exactly the named sessions.

## Evidence
The census output and its event id, the batch asked and its answer, and one change-log row per archive call.
