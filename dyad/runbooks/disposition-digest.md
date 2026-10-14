# Run-book: disposition-digest (how the Operator's attention is spent) — play-book `dyad/playbooks/disposition-digest.md`, #290
# sections: Board, Budget, Accrete, Held, Sweep, Retire

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the disposition-digest play-book as
`dyad-cmd` blocks, run by either party through the core runner, which prints the native line, records an
event in the instance's `<runbooks>/events/disposition-digest.jsonl` and tests the postcondition. Its
section set is its own (the `# sections:` line above; the sysadmin craft's server sections are a server's).
The steps that read the board take the play-book's parameter from the environment — `BOARD_THRESHOLD`,
defaulting to `40` — exactly as `dyad/runbooks/incident-hardening.md` reads `LEDGER` and
`dyad/runbooks/dwork-trace.md` reads `DWORK`; the steps that act on one row or one set take their ids the
same way, with no default, because a digest of the wrong d-work is worse than none: `DWORK`, `MANDATE`,
`TITLE`, `ROWS` and `SAID`. Every step reaches the instance through `${DYAD_INSTANCE:-agent-corpus}`
(Rule-11 property 3: a craft file reaches an instance path through that one location, so the default is
the expansion and not a written-out path), and every command runs from the git root.

Four steps are **read-only** — `budget`, `held`, `sweep` and the reading half of the board. Three write,
and each writes only what a disposition already given makes clerical (Rule-2): `board` renders the
untracked ledger view, `accrete` writes one row and its provenance record under a mandate the plan-`Y`
already authorized, and `retire` sets `archived` on the rows one retirement question named. None of the
three decides anything. The decision each executes — the mandate scope, the escalate-edge test, the
retirement sweep's candidate set — is the Agent's own d-work work under its own plan-`Y` and the
Operator's own `Y`, never a run-book command (`dyad/runbooks/incident-hardening.md` says the same of the
hardening exercise's records).

```text
BOARD_THRESHOLD=<n> dyad runbook list disposition-digest
BOARD_THRESHOLD=<n> dyad runbook run disposition-digest board
```

## Board
The pending board the play-book puts at the end of every reply: the rendered view refreshed first, since
Rule-16 requires the ledger view to be rendered and never read from the tracked tree, then the counts and
every row that is neither `done` nor `archived`. The three state counts are what the Operator reads; the
fourth figure of the play-book's board line — the opening candidates named and not opened — is
conversational and derivable from no store, so this step prints what there is and the reply carries the
rest. The postcondition is the render's own idempotence: the view is already the newest file of itself and
every row file, so a second run in a session that opened no row is `already satisfied` and does nothing —
the `0 changes` shape `crafts/syseng/rules/idempotence.md` property 1 sets for the install. Its undo
deletes a generated, untracked file (`.gitignore`; Rule-11 property 6), which loses nothing:
```dyad-cmd
name: board
class: reversible
role: any
undo: rm -f "${DYAD_INSTANCE:-agent-corpus}/d-work/LEDGER.md"
postcondition: test "$(ls -t "${DYAD_INSTANCE:-agent-corpus}"/d-work/LEDGER.md "${DYAD_INSTANCE:-agent-corpus}"/d-work/rows/*.md 2>/dev/null | head -n 1)" = "${DYAD_INSTANCE:-agent-corpus}/d-work/LEDGER.md"
scope: <instance>/d-work/LEDGER.md (rendered, untracked) and <instance>/d-work/rows/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; dyad/bin/dyad ledger >/dev/null && printf 'board: %s planned - %s open - %s blocked - %s backlog (threshold %s) - %s rows\n' "$(dyad/bin/dyad dwork list --state planned | wc -l)" "$(dyad/bin/dyad dwork list --state open | wc -l)" "$(dyad/bin/dyad dwork list --state blocked | wc -l)" "$(dyad/bin/dyad dwork list --state backlog | wc -l)" "${BOARD_THRESHOLD:-40}" "$(ls -1 "$I"/d-work/rows/*.md | wc -l)"; dyad/bin/dyad dwork list | grep -vE '\[(done|archived)\]'
```

## Budget
The disposition budget a plan declared, against the count its row actually carries. Both are corpus — one
line of `<instance>/d-work/plans/<DWORK>.md` (Rule-15 phase 1) and the `disposed` column of
`<instance>/d-work/rows/<DWORK>.md` (Rule-16) — which is what makes the budget the checkable half of a
play-book whose reply shape nothing can check. A plan that declares no budget is an outcome and says so
rather than failing: 123 of this instance's stored plans carry no `files touched` line either, and a
missing declaration is read as a plan written before the line existed. The entry count splits the column
on its own separator, so a row with an empty `disposed` reads `0` and not a parse error:
```dyad-cmd
name: budget
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/{plans,rows}/<DWORK>.md (read)

I="${DYAD_INSTANCE:-agent-corpus}"; D="${DWORK:?d-work id}"; grep -h '^disposition budget:' "$I/d-work/plans/$D.md" 2>/dev/null || echo "declared: none - plan $D states no disposition budget"; awk -v d="$D" '/^disposed:/{v=substr($0,11); n=split(v,a,";"); printf "actual: %d disposition(s) on #%s\n", (v==""?0:n), d}' "$I/d-work/rows/$D.md"
```

## Accrete
One accreted row, born in implicit mode under a mandate the plan-`Y` already authorized: `open`, with
`disposed: <date> Y plan (mandate #<MANDATE>)` and a provenance record whose entry 1 is that mandate's own
Operator words copied verbatim, noted `mandate #<MANDATE>, <the mandate's own date>` (Rule-7 property 4).
The verb refuses a target carrying no `Y plan` disposition, so a mandate that was never authorized
accretes nothing, and it writes the entry and the record together, so no row is ever born with a
`disposed` entry its record does not match (Rule-7 Enforcement, the transaction check). **The
escalate-edge test is applied before this step runs, not by it** — the play-book's five questions are
inference, and a row the test sends back to explicit mode is asked for and never passed to this command.
The postcondition is the accretion's own idempotence: a row already carrying this mandate and this title
exists, so a repeat is `already satisfied` and opens no duplicate. The undo removes the two files the
step just wrote, both uncommitted, named by modification time — so it is run in the same turn or not at
all, and after any further row is written it is the wrong row:
```dyad-cmd
name: accrete
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; N="$(basename "$(ls -t "$I"/d-work/rows/*.md | head -n 1)")"; rm -f "$I/d-work/rows/$N" "$I/d-work/provenance/$N"
postcondition: grep -l "(mandate #${MANDATE:?mandate id})" "${DYAD_INSTANCE:-agent-corpus}"/d-work/rows/*.md 2>/dev/null | xargs -r grep -lxF "title: ${TITLE:?row title}" | grep -q .
scope: <instance>/d-work/rows/<new id>.md and <instance>/d-work/provenance/<new id>.md (two new files)

dyad/bin/dyad dwork new "${TITLE:?row title}" "parent #${MANDATE:?mandate id}" --mandate "${MANDATE:?mandate id}"
```

## Held
Every open PR with its mergeability as observed, which is what the held-PR protocol reads: a PR of a
d-work not yet `done` waits for that d-work's Done-`Y` and is never asked about
(`merge-disposition: with-done`), so the figures that matter are its age and whether `main` has moved
under it. The `planned` rows are listed beside it because a held PR whose row is `planned` is the normal
case, while a held PR whose row cannot reach its Done question at all is the incident the protocol's step
5 names — and the join between a PR and its row is the `d-work #<id>` its body cites, which the Agent
reads, since no field of `gh pr list` carries it. The hosting is a library adapter and never kernel
(Rule-14 property 3), so this step is evidence and never a gate; when it is unreachable the step's own
failure is the report:
```dyad-cmd
name: held
class: read-only
role: any
undo: none
postcondition: none
scope: the hosting's open pull requests and <instance>/d-work/rows/ (read)

gh pr list --state open --json number,headRefName,mergeable,mergeStateStatus,additions,deletions,updatedAt -q '.[] | "PR #\(.number) \(.headRefName) \(.mergeable)/\(.mergeStateStatus) +\(.additions)/-\(.deletions) \(.updatedAt)"'; dyad/bin/dyad dwork list --state planned
```

## Sweep
The retirement sweep's trigger and its candidate set: the live `backlog` count against
`BOARD_THRESHOLD`, then every `backlog` row oldest first, which is the order the play-book proposes them
in. The count is derived from the row store here and now, never carried between sessions and never read
from a watermark — the comparison the incident-hardening survey makes against its own ledger, on a store
instead of a log. This step proposes nothing: the candidate a row becomes needs a reading of what it was
for and where its fence now lives, which is inference and goes in the reply, and **a row the Agent has
not read is proposed as a reading and never as a retirement**:
```dyad-cmd
name: sweep
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/rows/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; T="${BOARD_THRESHOLD:-40}"; B="$(dyad/bin/dyad dwork list --state backlog | wc -l)"; printf 'backlog %s - threshold %s - %s\n' "$B" "$T" "$([ "$B" -ge "$T" ] && echo 'propose a retirement sweep' || echo 'below threshold, no sweep')"; for f in "$I"/d-work/rows/*.md; do grep -qx 'state: backlog' "$f" && printf '%s #%s %s\n' "$(sed -n 's/^opened: //p' "$f")" "$(sed -n 's/^id: //p' "$f")" "$(sed -n 's/^title: //p' "$f" | cut -c1-90)"; done | sort
```

## Retire
The retirement itself: `backlog` to `archived` on the rows one `Y/N: archive #a, #b, ... #k?` named, the
retirement form of Rule-3's `archived` bullet, which `dyadlib.TRANSITIONS` admits from `backlog` since
#290 and which that bullet has always described — "retired from the working board by an Operator
disposition naming the row(s)". The verb is the k-row form of the `dyad dwork state <id> archived` the
same bullet names for one row, and nothing else about it differs. Clerical execution of a
disposition already given, a ledger-only commit (Rule-3 Ledger): the Agent never archives on its own
judgment, and the step is run after the `Y`, never to ask for one. `SAID` names the file holding that one
Operator utterance, which is written as the same `disposition` entry into every named row's own record —
Rule-3's Batch disposition already prescribes exactly that copy, and it is what keeps Rule-7 property 5's
one-to-one count true per row. The postcondition is the end state of every named row, so a partially
applied sweep re-runs cleanly and a complete one is `already satisfied`. The undo restores just those
files from `HEAD`, which is real only before the ledger commit: once `archived` is on `main` the state is
terminal (`archived -> none`, Rule-16 Store) and a new row refs it rather than reopening it — which is
why the Operator's `Y` precedes this command and not the reverse:
```dyad-cmd
name: retire
class: reversible
role: any
undo: for n in ${ROWS:?row ids}; do git restore --source=HEAD --worktree -- "${DYAD_INSTANCE:-agent-corpus}/d-work/"{rows,provenance}"/$n.md"; done
postcondition: for n in ${ROWS:?row ids}; do grep -qx 'state: archived' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/$n.md" || exit 1; done
scope: <instance>/d-work/{rows,provenance}/<ROWS>.md (the rows one retirement question named)

dyad/bin/dyad dwork retire ${ROWS:?row ids} --said-file "${SAID:?the file holding the Operator's words}"
```
