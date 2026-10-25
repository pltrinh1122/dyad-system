# Naming (cabinet craft, Tended rule)

Read by Rule-16's Presence clause — the seat-name form exists; the installed organization craft checks it; absent
the craft, the core's `touch()` prints one advisory line (#369 C7) — by `../guards/seats.py` (the check, advisory)
and by the core's `dyad session name`, which prints a seat's name and session title from the environment and
reads the form from `../guards/seats_rules.txt` when this craft is installed. A Tended rule: any form, no Rule-4
block, no sweep. Terms: `../vocabulary/CRAFT.md` (`function`, `topic`); the core's `seat`, `holder`, `presence
file`, `seat name`. Record: `../falsification/rules/naming.md`. Source: #365 (when a name carries no row id and
when ordinals earn their place), #366 (a name carries the Operator's mental model), #369 revisions 6, 8, 9 and 10
(the form, falsified four times).

## Intent
Name every seat so that a reader with the name alone knows what the Operator watches there, which board it
sits on, and which harness session holds it — and never by an ordinal, a row id, or a role token that tells a
reader nothing (plan #369 revision 10, attack 3).

## 1. The form
    <function>[-<topic>]-<hp>
- `function` — one of the standing functions of the mandates table (`../guards/seats_rules.txt`: `program`,
  `counsel`, `audit`, `engineer`, `distribute`, `operate` by default); lower-case letters.
- `topic` — optional: the one subject a desk holds under its function (`engineer-ledgerd-1537d8fb`,
  `operate-host-23d654aa`); lower-case letters and digits, hyphenated. For `program` the middle token is not a
  topic but the Operator's handle, naming a member pair's leader in a multi-Operator tree (`program-alice-<hp>`);
  the solo default is bare.
- `hp` — the first eight hex characters of the harness session id the holder runs under
  (`CLAUDE_CODE_SESSION_ID`; the core's `holder` line carries the whole id). It is a handle, never a proof of
  identity (#295): the presence file's `holder` says what the process says.
The regex is the one line `form:` of `seats_rules.txt`; a system that changes the form changes that line and this
rule together. The form is **not** a row of the syseng craft's naming table: a path kind there is conjunctive with
the native kind for presence files and would reject every name from before the form (the record, attack 2), so
the form lives in this craft's data, where its reading stays advisory.

## 2. The reading rule
A name is read from its tokens alone:
- one function and a handle, `program-<hp>` — **the cos**, and `program-<operator>-<hp>` a member pair's
  leader in a multi-Operator tree (the leader keeps no desk, so `program` never carries a topic); a seat list
  sorts the leaders first by construction;
- one function and a handle, any other function — **a secretary**, keeping the board of that function;
- a function, a topic and a handle — **a desk** on that function's board;
- `cos` is the vocabulary's word for a seat that keeps a board, never a name token (revision 10, attack 3).

## 3. The session title
The Operator sets the harness session's title on creation; the seat writes the presence file. The title form is
`<seat>: cloud (ds) - <topic>` — the seat name first, the kernel (`cloud`, `terminal`), the system's handle, and
what the seat is on now — so the harness's own session list reads as the board does. `dyad session name` prints
both from the environment, for the Operator to paste or compare.

## 4. The names history keeps
A presence file is never deleted or renamed (Rule-16): `cos.md`, `cos-1.md`, `cos-59cec502.md`, `cab-2-8c27a6fd.md`,
`unnamed-<hex>.md` and the rest stay as the record of who sat where. `seats.py` counts them as outside the form,
in one line, and fails nothing; a holder that takes a new seat writes a new file and leaves the old one. A
`unnamed-<hex>` file is what a bare `dyad session touch` writes under no `DYAD_SESSION`: one of the costs this
form exists to make visible, not an error of the store.

## When
- A function is added to the mandates table: its `function:` line is added to `seats_rules.txt` in the same
  craft-zone change, so the guard and `dyad session name` read the same list the Operator wrote.
- The form changes: `seats_rules.txt`, this rule, the guard's test and the craft's `VERSION` change together.
