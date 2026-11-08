# Run-book: disposition-digest (how the operator's attention is spent) — play-book `dyad/playbooks/disposition-digest.md`, #290, #626
# sections: Board, Budget, Accrete, Held, Sweep, Retire

The disposition-digest play-book's steps, run through the core runner from the git root, each recording an event in
`<runbooks>/events/disposition-digest.jsonl`. `BOARD_THRESHOLD` (default `40`) is the play-book's parameter; `DWORK`,
`MANDATE`, `TITLE`, `ROWS` and `SAID` are per-step ids with no default. The instance is `${DYAD_INSTANCE:-agent-corpus}`.
`budget`, `held` and `sweep` are read-only; `board`, `accrete` and `retire` write only what a disposition already
made clerical (Rule-2), and decide nothing.

```text
BOARD_THRESHOLD=<n> dyad runbook list disposition-digest
BOARD_THRESHOLD=<n> dyad runbook run disposition-digest board
```

## Board
The pending board the play-book puts at the end of every reply:
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
The disposition budget a plan declared, against the count its row actually carries:
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
One accreted row, born in implicit mode under a mandate the plan-`Y` already authorized:
```dyad-cmd
name: accrete
class: reversible
role: any
undo: I="${DYAD_INSTANCE:-agent-corpus}"; N="$(basename "$(ls -t "$I"/d-work/rows/*.md | head -n 1)")"; rm -f "$I/d-work/rows/$N" "$I/d-work/provenance/$N"
postcondition: grep -l "(mandate #${MANDATE:?mandate id})" "${DYAD_INSTANCE:-agent-corpus}"/d-work/rows/*.md 2>/dev/null | xargs -r grep -lxF "title: ${TITLE:?row title}" | grep -q .
scope: <instance>/d-work/rows/<new id>.md and <instance>/d-work/provenance/<new id>.md (two new files)

dyad/bin/dyad dwork new "${TITLE:?row title}" "parent #${MANDATE:?mandate id}" --mandate "${MANDATE:?mandate id}" ${SLUG:+--slug "$SLUG"}
```

## Held
Every open PR with its mergeability as observed, which is what the held-PR protocol reads:
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
The retirement sweep's trigger and its candidate set:
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
The retirement itself:
```dyad-cmd
name: retire
class: reversible
role: any
undo: for n in ${ROWS:?row ids}; do git restore --source=HEAD --worktree -- "${DYAD_INSTANCE:-agent-corpus}/d-work/"{rows,provenance}"/$n.md"; done
postcondition: for n in ${ROWS:?row ids}; do grep -qx 'state: archived' "${DYAD_INSTANCE:-agent-corpus}/d-work/rows/$n.md" || exit 1; done
scope: <instance>/d-work/{rows,provenance}/<ROWS>.md (the rows one retirement question named)

dyad/bin/dyad dwork retire ${ROWS:?row ids} --said-file "${SAID:?the file holding the Operator's words}"
```
