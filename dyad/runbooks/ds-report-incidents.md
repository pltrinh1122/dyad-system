# Run-book: ds-report-incidents (the anonymized, redacted incident report) — play-book `dyad/playbooks/ds-report-incidents.md`, #166, #626
# sections: Survey, Group, Map, Summarize, Project, Verify

The ds-report-incidents play-book's steps, run through the core runner from the git root, each recording an event in
`<runbooks>/events/ds-report-incidents.jsonl`. Parameters `LEDGER`, `AUDIENCE` (required) and `LEVEL` (default
`standard`), as the play-book names them; the instance is `${DYAD_INSTANCE:-agent-corpus}`. Every step but `project` is
read-only; the report it writes is generated and untracked.

```text
AUDIENCE="<party>" dyad runbook list ds-report-incidents
AUDIENCE="<party>" dyad runbook run ds-report-incidents survey
```

## Survey
Phase 0, the idempotence gate:
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
Phase 1:
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
Phase 2:
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
Phase 3:
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
Phase 4, the only step that writes:
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
Phase 5:
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
