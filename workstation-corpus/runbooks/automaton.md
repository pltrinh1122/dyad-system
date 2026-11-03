# Run-book: automaton (the d-work automaton and its scheduled sweep, on GitHub Actions) — d-work #564
# sections: Status/health, Sweep, Logs, Data

Instance: not a server on this host. It is two workflows run by GitHub Actions with the hosting's token, whose logic
is the core verb `dyad automaton` (`dyad/scripts/automaton.py`):
- `.github/workflows/dyad-automaton.yml` (display name `d-work automaton`, #556) runs `dyad automaton run` on a push to
  `main` that touches the ledger's rows or board.
- `.github/workflows/dyad-sweep.yml` (display name `d-work sweep`, #564) runs this run-book's `sweep` twice a day, at
  6:00 and 18:00 America/Los_Angeles, and on manual dispatch.

Its supervisor is the hosting: nothing here starts, stops or restarts it, and no session runs it. The workflows are
the distribute seat's (`.github/workflows/`); this run-book, its events and its health are the operate seat's
(`MANDATES.md`). So this run-book declares its own section set (the sysadmin craft's `server-instances.md`
property 2).

Start, stop and upgrade:
- **Start** is a push to `main` (the automaton) or the schedule (the sweep).
- **Stop** is the Operator's act: the repository variable `DYAD_AUTOMATON` for the automaton, or disabling a workflow
  in the hosting's settings.
- **Upgrade** is a change to a workflow file (a distribute-seat infra-zone PR) or to `automaton.py` (an engineer
  agent-zone PR). None is run from here.

**The sweep** (plan #564).
- It is read-only. It runs every guard over every store and the full suite, plus checks the push gate never had:
  - published archives against `BUNDLE.sha256` and their tags, and moved tags (through `released`'s health);
  - the mirror against `main`;
  - code pushes to `main` with no successful corroboration;
  - a `Y done` whose heads have not landed, and a stale board entry.
- It folds its findings against the notices already in the home's inbox. It posts one `notice` only for a finding
  that is new or failing; a clean sweep sends nothing.
- Its exit is 1 when any finding fails.

**Record.** Every sweep's event is this run-book's event:
- The core runner appends it to `<runbooks>/events/automaton.jsonl`.
- `dyad-sweep.yml` commits it as an events-only commit (clerical, Rule-3; no row, no PR) and pushes it through the
  pre-push gate.
- The runner records a read-only command only when its reading changes (#438). A sweep's reading names the `main` it
  read, and every sweep's own event commit moves `main`, so every sweep's reading differs from the last and every
  sweep leaves an event.
- That commit is also repository activity, so GitHub never disables the schedule for inactivity.

Every command runs from the git root as either party, `sudo`-free. `sweep` reads the hosting's workflow runs with
`GITHUB_TOKEN` and `GITHUB_REPOSITORY` when they are set. Without them, that one check prints a single `finding` line
and the rest runs.

```text
dyad runbook list automaton
dyad runbook run automaton health
```

## Status/health
Health (server-instances rule, property 4; Rule-19 kernel): the last `sweep` event in
`<runbooks>/events/automaton.jsonl` is under 13 hours old. That is one twice-daily slot plus one hour of the
hosting's schedule delay. The command prints the age of the last sweep and its exit, or `no sweep yet`.
**Pass: exit 0**, a sweep event under 13 hours old. The postcondition is the same check, silent.
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: python3 -c "import json,sys,datetime as d; p='workstation-corpus/runbooks/events/automaton.jsonl'; e=[json.loads(l) for l in open(p) if l.strip()] if __import__('os').path.exists(p) else []; s=[x for x in e if x.get('name')=='sweep']; sys.exit(0 if s and (d.datetime.now(d.timezone.utc)-d.datetime.strptime(s[-1]['ts'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=d.timezone.utc)).total_seconds()<13*3600 else 1)"
scope: workstation-corpus/runbooks/events/automaton.jsonl (read)

python3 -c "import json,sys,datetime as d; p='workstation-corpus/runbooks/events/automaton.jsonl'; e=[json.loads(l) for l in open(p) if l.strip()] if __import__('os').path.exists(p) else []; s=[x for x in e if x.get('name')=='sweep']; a=(d.datetime.now(d.timezone.utc)-d.datetime.strptime(s[-1]['ts'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=d.timezone.utc)).total_seconds()/3600 if s else None; print('no sweep yet' if a is None else f'last sweep {s[-1][\"ts\"]}: {a:.1f} h ago, exit {s[-1][\"exit\"]}'); sys.exit(0 if a is not None and a<13 else 1)"
```

## Sweep
The sweep itself, as `dyad-sweep.yml` runs it. Running it by hand in a seat is the same read-only check, with one
difference: without `GITHUB_TOKEN`, the corroboration check prints a `finding` instead of reading the runs. Its
findings print one per line, followed by one summary line, `sweep of main <sha>: <n> finding(s), <f> failing, <k>
new`. The postcondition is `none`: the exit is the reading, 1 when a finding fails.
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
The two workflows' last runs, from the hosting's public REST endpoint: workflow, run number, event, status,
conclusion and the run's page. A run's log itself needs a token and is read on the run's page.
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
Where state lives:
- the ledger rows and board the automaton reads (`agent-corpus/d-work/rows/`, `agent-corpus/d-work/board/`);
- the home's inbox, which holds the sweep's notices (`agent-corpus/d-work/inbox/`);
- this run-book's events;
- the workflow runs on the hosting.

Nothing lives on this host. A fresh deployment needs only `main`. The command lists the recorded sweeps.
```dyad-cmd
name: data
class: read-only
role: any
undo: none
postcondition: none
scope: workstation-corpus/runbooks/events/automaton.jsonl (read)

f=workstation-corpus/runbooks/events/automaton.jsonl; if [ -f "$f" ] && grep -q '"name": "sweep"' "$f"; then grep -h '"name": "sweep"' "$f" | python3 -c "import json,sys; [print(x['ts'], 'exit', x['exit'], x['output_tail'][-120:]) for x in map(json.loads, sys.stdin)]"; else echo "no sweep recorded yet"; fi
```
