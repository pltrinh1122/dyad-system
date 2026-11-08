# Run-book: automaton (the d-work automaton and its sweeps, on GitHub Actions) — d-work #564, #617, #619, #626
# sections: Status/health, Sweep, Logs, Data

Instance: two GitHub Actions workflows, supervised by the hosting, logic `dyad automaton` (`dyad/scripts/automaton.py`).
The workflows are distribute's; this run-book, its events and its health are operate's (`MANDATES.md`). Start is a push
to `main`; stop is the operator's (the variable `DYAD_AUTOMATON`, or disabling a workflow); upgrade is a PR to a
workflow (distribute) or to `automaton.py` (engineer). Nothing runs from here but reads.

**Trigger.**
- `dyad-automaton.yml` (`d-work automaton`): every ledger or events push to `main`. It runs `dyad automaton run`, then
  the stores sweep, `dyad automaton sweep --stores`, and dispatches the full sweep when its run landed a merge.
- `dyad-sweep.yml` (`d-work sweep`): the full sweep, after each landed merge (a code push to `main`, or the automaton's
  dispatch), and on manual dispatch. No clock.

**Evidence.** The full sweep's event, appended by the runner to `<runbooks>/events/automaton.jsonl` and committed
events-only by `dyad-sweep.yml`; the stores sweep leaves none (#617), so health reads the hosting. What the sweeps
check is Rule-14 property 3; the stall findings are the home's read in `dyad board resume`.

## Status/health
Step: `dmc:automaton-health`, read from `dyad board resume` on a freshly pulled `main`. The command prints the stall
block's header and each line that decides it; exit 0 is the pass. The postcondition is the same check, silent.
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: o=$(dyad/bin/dyad board resume 2>&1); printf '%s\n' "$o" | grep -q '^stalls (' && ! printf '%s\n' "$o" | grep -qE '^  finding: (delivery:|corroboration.*not read)'
scope: the ledger and board at this checkout's HEAD, and the hosting's workflow runs (read)

o=$(dyad/bin/dyad board resume 2>&1); h=$(printf '%s\n' "$o" | grep -m1 '^stalls'); b=$(printf '%s\n' "$o" | grep -E '^  finding: (delivery:|corroboration.*not read)'); printf '%s\n' "${h:-stalls: not printed}" | cut -d';' -f1; [ -z "$b" ] || printf '%s\n' "$b"; case "$h" in "stalls ("*) [ -z "$b" ] ;; *) false ;; esac
```

## Sweep
The full sweep, as `dyad-sweep.yml` runs it; read-only by hand too. It prints one line per finding and a summary
`sweep of main <sha>: <n> finding(s), <f> failing, <k> new`; exit 1 when a finding fails.
```dyad-cmd
name: sweep
class: read-only
role: any
undo: none
postcondition: none
scope: every store and the suite (read), origin's tags and Releases and the hosting's workflow runs (read), one notice in the home's inbox when a finding is new

dyad/bin/dyad automaton sweep --row 564
```

## Logs
The two workflows' last runs, from the hosting's public endpoint; a run's log is read on its page.
```dyad-cmd
name: logs
class: read-only
role: any
undo: none
postcondition: none
scope: the hosting's workflow runs for dyad-sweep.yml and dyad-automaton.yml (read)

r=$(git remote get-url origin | sed -E 's#^https?://([^@]*@)?github.com/##; s#^git@github.com:##; s#\.git$##'); for w in dyad-sweep.yml dyad-automaton.yml; do curl -sf "https://api.github.com/repos/$r/actions/workflows/$w/runs?per_page=5" | python3 -c "import json,sys; [print('$w', x['run_number'], x['event'], x['status'], x['conclusion'], x['html_url']) for x in json.load(sys.stdin).get('workflow_runs', [])]" || echo "$w: no runs readable"; done
```

## Data
State lives in the rows and board the automaton reads, the home's inbox, this run-book's events and the hosting's
runs; nothing on this host, and a fresh deployment needs only `main`. The command lists the recorded sweeps.
```dyad-cmd
name: data
class: read-only
role: any
undo: none
postcondition: none
scope: workstation-corpus/runbooks/events/automaton.jsonl (read)

f=workstation-corpus/runbooks/events/automaton.jsonl; if [ -f "$f" ] && grep -q '"name": "sweep"' "$f"; then grep -h '"name": "sweep"' "$f" | python3 -c "import json,sys; [print(x['ts'], 'exit', x['exit'], x['output_tail'][-120:]) for x in map(json.loads, sys.stdin)]"; else echo "no sweep recorded yet"; fi
```
