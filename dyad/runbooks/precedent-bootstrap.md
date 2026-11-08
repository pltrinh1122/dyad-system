# Run-book: precedent-bootstrap (the decision log's first precedents) — play-book `dyad/playbooks/precedent-bootstrap.md`, #645
# sections: Structured, Prompt, Score, Gate, Agreement

A core run-book (package, `dyad/runbooks/`; agent zone). It holds the commands of the precedent-bootstrap play-book as
`dyad-cmd` blocks, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/precedent-bootstrap.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above). Each command reads the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3)
and runs from the git root; the files it reads and writes are named by parameters that point into the scratchpad, never
into the tree. Every step is **read-only**: a command prints or writes a working file, and every judgement it leads to —
which records qualify, a case's facts and label, an arbitration, the question — is the agent's reading under the
play-book, never a run-book command. Only the precedent-`Y`'s own clerical commit writes the decision log.

```text
dyad runbook list precedent-bootstrap
STRUCTURED=<file> dyad runbook run precedent-bootstrap structured
CASES=<file> PROMPT=<file> dyad runbook run precedent-bootstrap prompt
CASES=<file> ANSWERS_CHEAP=<file> ANSWERS_DEFAULT=<file> KEPT=<file> dyad runbook run precedent-bootstrap score
KEPT=<file> ADMITTED=<file> dyad runbook run precedent-bootstrap gate
RECORD=<id> dyad runbook run precedent-bootstrap agreement
```

## Structured
`backfill.py`: one candidate per case whose source cell already holds a record's own outcome name, as JSON lines in the
form a `--decisions` file takes, source `structured`; the per-record counts and every skipped cell's count on stderr. A
fresh install prints no candidate and exits 0:
```dyad-cmd
name: structured
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/{rows,plans}/, <instance>/falsification/, dyad/falsification/ and <host>/CHANGELOG.md (read); $STRUCTURED (scratch, written)

dyad/bin/dyad-python dyad/scripts/backfill.py > "$STRUCTURED"
```

## Prompt
`dyad precedent prompt`: the blind prompt, built from the case file (`{case, record, row, facts, label}` per line, `record` the bare id) and the
records it names — each record's question, outcomes, precedence and default, and each case's id and facts, never a label
— in record then case order, so the same inputs give the same bytes. It refuses, exit 1, a case whose record is not
judged by inference or whose consequences name a ratifying act:
```dyad-cmd
name: prompt
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/dmc/ and $CASES (read); $PROMPT (scratch, written)

dyad/bin/dyad precedent prompt "$CASES" --out "$PROMPT"
```

## Score
`dyad precedent score`: the two readers' answers against the labels — per record the count and each reader's score, the
kept cases (both readers match), and each mismatch classed by how many readers missed it; `--kept` writes the kept cases
as `--decisions` input, source `two-readers`:
```dyad-cmd
name: score
class: read-only
role: any
undo: none
postcondition: none
scope: $CASES, $ANSWERS_CHEAP and $ANSWERS_DEFAULT (read); $KEPT (scratch, written)

dyad/bin/dyad precedent score "$CASES" "$ANSWERS_CHEAP" "$ANSWERS_DEFAULT" --kept "$KEPT"
```

## Gate
`dyad precedent gate`: `dmc:precedent-admission` over each kept case — the structured candidates appended to the kept
file — judged as if the precedent-`Y` had already named it; the admitted cases written to `--out` as `--decisions` input,
every other case printed with the record's outcome. Run before the question, so the question lists only cases admission
admits. It does not see a ruling the log already holds under another id, so the kept file holds one case id per ruling
(the play-book's prose-cases step):
```dyad-cmd
name: gate
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/dmc/, <instance>/d-work/decisions/, git history of each record and its home, and $KEPT (read); $ADMITTED (scratch, written)

dyad/bin/dyad precedent gate "$KEPT" --out "$ADMITTED"
```

## Agreement
`dyad precedent agreement`: after the precedent-`Y`, the record's admitted cases frozen to a temporary set and measured
leave-one-out — n, reproduced, abstained and agreement, beside the record's bar where it states one. It writes nothing
to the tree:
```dyad-cmd
name: agreement
class: read-only
role: any
undo: none
postcondition: none
scope: dyad/dmc/ and <instance>/d-work/decisions/ (read)

dyad/bin/dyad precedent agreement "$RECORD"
```
