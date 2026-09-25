# Run-book: ds-report-incidents (the anonymized, redacted incident report) — play-book `dyad/playbooks/ds-report-incidents.md`, #166
# sections: Survey, Group, Map, Summarize, Project, Verify

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the `ds-report-incidents`
play-book as `dyad-cmd` blocks, run by either party through the core runner, which prints the native
line, records an event in the instance's `<runbooks>/events/ds-report-incidents.jsonl` and tests the
postcondition. Its section set is its own (the `# sections:` line above).

Three parameters, taken from the environment (the play-book's table): `LEDGER`, defaulting to
`${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md` — the instance location's incident log, so the
default is the expansion and not a written-out path (Rule-11 property 3); `AUDIENCE`, required by the
steps that name the reader; and `LEVEL`, `standard` or `minimal`. Every step that reads the log resolves
the `LEDGER` default itself, in its command's first line and in the postcondition that tests it, so one
expansion is the only form in which a step reads the parameter.

Five of the six steps are **read-only**: they read and report, and the writing they lead to — a
summary, a pseudonym, a backlog row — is the Agent's own d-work work under its own plan-`Y` (Rule-3),
never a run-book command. Only `project` writes, and what it writes is generated and untracked
(`generated: projections/*`), so it is not a repo transaction; its undo is a file removal.

```text
AUDIENCE="<party>" dyad runbook list ds-report-incidents
AUDIENCE="<party>" dyad runbook run ds-report-incidents survey
```

## Survey
Phase 0, the idempotence gate: the log's live row count and latest date, then the watermark of the
report already on disk (`covered through: <n> rows, latest <YYYY-MM-DD>`, which the projector writes
into the file it produces). Equal numbers are the no-op — `group` through `project` do not run, and
`verify` still does. No report on disk at all is the first build, and the step says so rather than
failing. The watermark is only ever compared, never believed: the pair beside it is derived from the
log here, now — the count, and the date that answers the count's own weakness, a row inserted mid-file
while the total stands still. The postcondition tests what makes the comparison possible — the log
exists and holds at least one dated row:
```dyad-cmd
name: survey
class: read-only
role: any
undo: none
postcondition: grep -q '^| 20' "${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
scope: <LEDGER> (read) and <instance>/projections/disclosure.html (read)

LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
printf 'live: %s rows, latest %s  (%s)\n' "$(grep -c '^| 20' "$LEDGER")" "$(grep -o '^| 20[0-9-]*' "$LEDGER" | tr -d '| ' | sort | tail -n 1)" "$LEDGER"
grep -o 'covered through:[^<]*' "${DYAD_INSTANCE:-agent-corpus}/projections/disclosure.html" 2>/dev/null | sed -n '$p' || echo "no report on disk: first build, full derivation"
```

## Group
Phase 1: the failure modes present in the log, by the grouping `incident-hardening` already performs —
one exercise's grouping, two uses. What this step adds is the count per group, which is what survives
redaction and what the reader acts on. The parser is the log's one parser
(`dyad/scripts/incidents.py` `parse`, the log's one parser), never a fresh regex:
```dyad-cmd
name: group
class: read-only
role: any
undo: none
postcondition: test -f "${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
scope: <LEDGER> (read) and the mode records in <instance>/audits/ (read)

LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
dyad/bin/dyad-python dyad/scripts/incidents.py >/dev/null && printf 'log parses\n'
dyad/bin/dyad-python -c 'import sys;sys.path.insert(0,"dyad/scripts");import dyadlib;i=dyadlib.load_guard("agent","incidents");r=i.parse();print("\n".join(f"{k}: {len(v)} rows" for k,v in i.by_year_month(r).items()))'
ls "${DYAD_INSTANCE:-agent-corpus}"/audits/*-incident-mode-*.md 2>/dev/null | sed 's|.*/||' || echo "no mode records beside this log yet"
```

## Map
Phase 2: what the pseudonym map already carries, and what this log mentions that it does not. Allocation
itself is the Agent's write, not this step's: a pseudonym that changed between two reports would make
the two incomparable, which is the one thing the map exists to prevent:
```dyad-cmd
name: map
class: read-only
role: any
undo: none
postcondition: test -f "${DYAD_INSTANCE:-agent-corpus}/disclosure/pseudonyms.md"
scope: <instance>/disclosure/pseudonyms.md (read) and <LEDGER> (read)

MAP="${DYAD_INSTANCE:-agent-corpus}/disclosure/pseudonyms.md"
printf 'map: %s entries  (%s)\n' "$(grep -c '^| `' "$MAP")" "$MAP"
dyad/bin/dyad-python crafts/disclosure/scripts/redaction.py unmapped "${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}" || echo "redaction module absent: install the disclosure craft"
```

## Summarize
Phase 3: which groups still need an external summary, and which already have one. The summaries are the
only inference in the chain and the Agent writes them in its own d-work, for this audience, at
`<instance>/disclosure/summaries/<YYYY-MM>.md`; both redaction gates apply to their text exactly as to
everything else. At `LEVEL=minimal` the step reports that none are needed:
```dyad-cmd
name: summarize
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/disclosure/summaries/ (read)

D="${DYAD_INSTANCE:-agent-corpus}/disclosure/summaries"
printf 'level: %s\n' "${LEVEL:-standard}"
test "${LEVEL:-standard}" = minimal && printf 'minimal: no summaries needed\n' || { ls "$D" 2>/dev/null | sed 's|^|have: |' || printf 'have: none (%s is empty or absent)\n' "$D"; }
```

## Project
Phase 4, the only step that writes: the deliverable. `dyad project disclosure` renders the groups, the
counts, the manifest and the watermark into one self-contained file under `<instance>/projections/`,
after the redaction gate has run over the assembled output — if any forbidden shape survives, the
projector writes nothing and exits non-zero, and the postcondition below then fails too. `AUDIENCE` is
required: a report that does not name its reader cannot be checked against the disposition that
released it:
```dyad-cmd
name: project
class: reversible
role: any
undo: rm -f <instance>/projections/disclosure.html
postcondition: grep -q 'covered through:' "${DYAD_INSTANCE:-agent-corpus}/projections/disclosure.html"
scope: <instance>/projections/disclosure.html (written; generated and untracked)

test -n "${AUDIENCE:-}" || { echo "AUDIENCE is required (the play-book's parameter table)" >&2; exit 2; }
AUDIENCE="$AUDIENCE" LEVEL="${LEVEL:-standard}" LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}" dyad project disclosure
```

## Verify
Phase 5: the gate re-run over the file as written, independently of the projector that wrote it, plus
the manifest and the file's sha256 — the three things the completion reply cites. A pass here is what
makes the delivery question askable; a failure is an incident (Rule-3), and the file is removed rather
than delivered:
```dyad-cmd
name: verify
class: read-only
role: any
undo: none
postcondition: dyad/bin/dyad-python crafts/disclosure/scripts/redaction.py verify "${DYAD_INSTANCE:-agent-corpus}/projections/disclosure.html"
scope: <instance>/projections/disclosure.html (read)

F="${DYAD_INSTANCE:-agent-corpus}/projections/disclosure.html"
dyad/bin/dyad-python crafts/disclosure/scripts/redaction.py verify "$F"
grep -o 'manifest:[^<]*' "$F" | sed -n '$p'
dyad/bin/dyad-python -c 'import hashlib,sys;print("sha256="+hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$F"
```
