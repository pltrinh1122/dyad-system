# Play-book: monitor unit (the cabinet craft; dyad-system #682)

How a cabinet opens, runs and retires a unit whose one job is to watch a stream (a channel, a mailbox, a hosting's
runs). Record: `dmc:monitor-setup`. A monitor reads the stream, runs its code checks, classifies what it read and
routes it to the home's inbox; as a stream's sole sender it posts only the exact bytes a recorded posting `Y` names
by id and sha256. It never drafts, edits, answers, disposes or acts on what it read, and it accretes nothing. Opening
any unit is the Operating Guide's §3, which this play-book cites for the steps every unit shares; ending one is the
session-tidy play-book's (`session-tidy.md`). This play-book holds only what a monitor adds: the model named at spawn,
the first prompt that fences it, its loop and its wake.

| step | does | uses |
|---|---|---|
| M1 Decide what holds the watch | read the stream against `dmc:monitor-setup`; when the home reads it itself, or an automaton runs it, this play-book ends here and the stream's own play-book takes over | `dmc:monitor-setup` |
| M2 The charter | the desk's mandates row: `<function>-<topic>-<hp>` under the function whose domain holds the stream; its fence read-only, plus inbox posts to the home and, as sole sender, posts of exactly the bytes a recorded posting `Y` names; ceiling 0; every candidate, breach and sha256 mismatch an escalation to the home. The secretary of that function drafts the preferences-zone PR (the Guide's §3 item 5), and its merge is asked as `dmc:merge-question` decides: under `merge-disposition: with-done`, it rides the Done of the row that opens the desk | `MANDATES.md`; `dmc:merge-question` |
| M3 Name it | the topic names the stream (`channels`); the `<hp>` is known once the session exists (the Guide's §3 item 1) | `../rules/naming.md` |
| M4 Spawn it | the home creates the session: solo (not in `paired-units`), its posture `efficient` (`delegation-posture-unattended`), its model named at spawn as the record's outcome says and never written into the repository, and titled as the Guide's §3 item 2 says | the harness's session tool |
| M5 First prompt | the home sends one prompt, taken verbatim from the stream's loop play-book: the stream, its record, its loop, the never-list above and its registration, a touch with no row (M6) | the stream's loop play-book |
| M6 Register | the desk's first act is `dyad session touch` with no row: a monitor desk opens no row of its own, since its loop is monitoring, which opens none (Rule-3 Ledger). Its other acts ride a row that already exists: a post rides the row that holds its posting `Y` (`channel-post.md` P5, P8), and a set-up host action rides the row that spawned or configures the desk, with its change-log row (Rule-8). A unit that executes rows registers as the Guide's §3 item 3 says | `dyad session touch` |
| M7 Run the loop | the desk runs the stream's loop play-book and reports only to the home's inbox | the stream's loop play-book |
| M8 Retire | when the stream ends or another holder takes the watch, the tidy census classes the desk and its retire act ends it; its mandates row is removed by a preferences-zone PR | `session-tidy.md`; `dmc:session-tidy` |

## Evidence
The record's outcome as read, the mandates row's PR, the spawn (the session and its title), the desk's presence file (M6),
and the stream play-book's own evidence.
