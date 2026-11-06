# Run-book: automaton (the d-work automaton and its sweeps, on GitHub Actions) — d-work #564, #617, #619
# sections: Status/health, Sweep, Logs, Data

Instance: not a server on this host. It is two workflows run by GitHub Actions with the hosting's token, whose logic
is the core verb `dyad automaton` (`dyad/scripts/automaton.py`):
- `.github/workflows/dyad-automaton.yml` (display name `d-work automaton`, #556) runs on every ledger or events push
  to `main`. It runs `dyad automaton run`, then the **stores sweep**, `dyad automaton sweep --stores` (the whole-store
  guards, no suite, #617). When its run landed a merge, it dispatches the full sweep once for the cut.
- `.github/workflows/dyad-sweep.yml` (display name `d-work sweep`, #564, #617) runs this run-book's `sweep`, the **full
  sweep**, after each landed merge. It is started by a push to `main` that changes code, or by the automaton's dispatch
  when the automaton's own run landed the merge (a push made with the workflow token starts no workflow, but a dispatch
  does). It also runs on manual dispatch. It has no clock.

Its supervisor is the hosting: nothing here starts, stops or restarts it, and no session runs it. The workflows are
the distribute seat's (`.github/workflows/`); this run-book, its events and its health are the operate seat's
(`MANDATES.md`). So this run-book declares its own section set (the sysadmin craft's `server-instances.md`
property 2).

Start, stop and upgrade:
- **Start** is a push to `main`: a ledger or events push (the automaton and its stores sweep), or a landed merge (the
  full sweep).
- **Stop** is the Operator's act: the repository variable `DYAD_AUTOMATON` for the automaton, or disabling a workflow
  in the hosting's settings.
- **Upgrade** is a change to a workflow file (a distribute-seat infra-zone PR) or to `automaton.py` (an engineer
  agent-zone PR). None is run from here.

**The full sweep** (plans #564, #617, #619).
- It is read-only. It runs every guard over every store and the full suite, plus checks the push gate never had:
  - published archives against `BUNDLE.sha256` and their tags, and moved tags (through `released`'s health);
  - the mirror against `main`;
  - the audit's checks (`sweep_audit`, #619).
- It folds its findings against the notices already in the home's inbox. It posts one `notice` only for a finding
  that is new or failing; a clean sweep sends nothing.
- Its exit is 1 when any finding fails.
- The stall findings are not the sweep's since #617: Y dones whose heads have not landed, code pushes with no
  corroboration, a stale board, the work in flight, the backlog's hygiene, and sweeps not delivered (#619). The home
  reads them at each prompt, in `dyad board resume`'s stall block.

**Record.** Every sweep's event is this run-book's event:
- The core runner appends it to `<runbooks>/events/automaton.jsonl`.
- `dyad-sweep.yml` commits it as an events-only commit (clerical, Rule-3; no row, no PR) and pushes it through the
  pre-push gate.
- The runner records a read-only command only when its reading changes (#438). A sweep's reading names the `main` it
  read, and every sweep's own event commit moves `main`, so every sweep's reading differs from the last and every
  sweep leaves an event.
- The stores sweep leaves no event (#617), so the event store alone cannot show that the sweeps ran. Health reads the
  hosting instead (below).

Every command runs from the git root as either party, `sudo`-free. The hosting's workflow runs are read from its
public endpoint, with `GITHUB_TOKEN` when it is set; the repository is named by `GITHUB_REPOSITORY` or by `origin`.

```text
dyad runbook list automaton
dyad runbook run automaton health
```

## Status/health
Health (server-instances rule, property 4; Rule-19 kernel): every sweep owed has been delivered (plan #619, Decision
4). It reads the stall block of `dyad board resume`, which is read from the ledger at this checkout's HEAD, so run it
from a freshly pulled `main`. Delivery means two things:
- the newest landed merge on `main` has a `d-work sweep` run at it or at a later first-parent commit;
- the newest ledger or events push has a `d-work automaton` run at it or later.
A run counts when it is queued, in progress, or completed with a result. A push younger than five minutes is not yet
judged (`DELIVERY_GRACE_S`).
The command prints the stall block's header and every `finding: delivery` line and every line saying the hosting was
not read. **Pass: exit 0**, a stall block was read, it holds no `finding: delivery` line, and the hosting was read. An
unread hosting is not a pass. The postcondition is the same check, silent.
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
The full sweep itself, as `dyad-sweep.yml` runs it. Running it by hand in a seat is the same read-only check. Its
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
