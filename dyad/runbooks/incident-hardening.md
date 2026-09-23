# Run-book: incident-hardening (the incident-to-mitigation exercise) — play-book `dyad/playbooks/incident-hardening.md`, #137
# sections: Survey, Group, Inventory, Plan, Execute, Verify

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the incident-hardening play-book as
`dyad-cmd` blocks, run by either party through the core runner, which prints the native line, records an
event in the instance's `<runbooks>/events/incident-hardening.jsonl` and tests the postcondition. Its
section set is its own (the `# sections:` line above; the sysadmin craft's server sections are a server's).
The two steps that read a ledger take its path from the environment — `LEDGER`, the play-book's parameter,
defaulting to `${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md`, the incident log of the instance
location (Rule-11 property 3: a craft file reaches an instance path through that one location, so the
default is the expansion and not a written-out path) — and each resolves that default itself, in its
command's first line and in the postcondition that tests it, so one expansion is the only form in which
either step reads the parameter. The other four take none: the guard registry, the row store and the
evidence block are the same reads whatever ledger is being hardened, exactly as the craft run-book's own
argument-less commands are. Every command runs from the git root, and every command is **read-only**: the
exercise reads and reports, and the writing it leads to — a mode record, an index audit, a `backlog` row,
a mitigation's own PR — is the Agent's own d-work work under its own plan-`Y` (Rule-3), never a run-book
command.

```text
LEDGER=<path> dyad runbook list incident-hardening
LEDGER=<path> dyad runbook run incident-hardening survey
```

## Survey
Phase 0, the idempotence gate: the live row count and latest row date of `${LEDGER}`, then the watermark
of the most recent index audit naming that same ledger
(`**Ledger:** … · **covered through:** <n> rows, latest <YYYY-MM-DD>`). Equal numbers are the no-op —
phases 1 to 3 do not run, and Verify still does. No watermark line at all is the first exercise, and the
step says so rather than failing. The watermark is only ever compared, never believed: the pair beside it
is derived from the ledger here, now — the count, and the date that answers the count's own weakness, a
row inserted mid-file while the total stands still. The postcondition tests what makes the comparison
possible — the ledger exists and holds at least one dated row; that no index audit names it yet is an
outcome, not a failure:
```dyad-cmd
name: survey
class: read-only
role: any
undo: none
postcondition: grep -q '^| 20' "${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
scope: <LEDGER> and the audits/ directory beside it (read)

LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
printf 'live: %s rows, latest %s  (%s)\n' "$(grep -c '^| 20' "$LEDGER")" "$(grep -o '^| 20[0-9-]*' "$LEDGER" | tr -d '| ' | sort | tail -n 1)" "$LEDGER"
grep -h 'covered through:' "$(dirname "$LEDGER")"/*-incident-failure-modes.md 2>/dev/null | grep -F "$LEDGER" | sed -n '$p' || echo "no index audit names $LEDGER: first exercise, full derivation"
```

## Group
Phase 1: what the last exercise left beside this ledger — one record per observed failure mode, and the
index audit that lists them. Only the exercise's own names are listed
(`<date>-incident-mode-<letter>.md`, `<date>-incident-failure-modes.md`); an empty listing is the first
exercise. The listing says what there is to update, never what the modes are: phase 1 re-derives the modes
from the ledger itself each time, because the taxonomy is not closed — #128 found a pattern the nine modes
of #116 do not name:
```dyad-cmd
name: group
class: read-only
role: any
undo: none
postcondition: none
scope: the audits/ directory beside <LEDGER> (read)

LEDGER="${LEDGER:-${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md}"
ls -1 "$(dirname "$LEDGER")" | grep -E 'incident-(failure-modes|mode-[a-z])\.md$' || echo "no mode record or index audit beside $LEDGER: first exercise"
```

## Inventory
Phase 2 inventories every live mitigation of a mode from the code and the Rule text, never from an audit's
prose — the failure of #116 and #128 was a candidate surfaced as a paragraph with no row and no moment. The
guard registry is where the mechanical ones are: corpus (or craft), entity, module, whether it runs as a
transaction guard, and the root that ships it — one line per guard, discovered under `dyad/guards/` and
every `crafts/<craft>/guards/` and never hand-listed (Rule-11 Enforcement). A mode whose mitigation is not
in this list is inference stated in a Rule, or nothing at all, and phase 2 says which:
```dyad-cmd
name: inventory
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --list
```

## Plan
Phase 2 ends by falsifying "this mode is addressed"; what survives and is not yet built is a `backlog` row
naming the fence still to build — one of phase 4's three exits, and the one that makes an undisposed
candidate visible as a row instead of a paragraph. This lists that state of the row store (Rule-16). The
store is the instance's, not the ledger's: a ledger hardened here has its records and its rows in this same
instance, which is what the parameter means and how far it reaches (play-book boundary; no guard reaches
another repository) — so this step takes no `LEDGER`. Each row is still opened by the Operator's own
prompt, and the d-work a mitigation is executed under is its own:
```dyad-cmd
name: plan
class: read-only
role: any
undo: none
postcondition: none
scope: <instance>/d-work/rows/ (read)

dyad/bin/dyad dwork list --state backlog
```

## Execute
Phase 3: each survivor runs as its own d-work under its own plan-`Y`, one zone per PR (Rule-1). Nothing
here mutates — this step shows the evidence command that d-work runs on the exact head it will merge: head
sha, tree hash, working-tree cleanliness, every check and guard result, and a sha256 of those lines
(Rule-14 property 3). Its block is what the completion reply pastes verbatim and the Operator may re-run on
the same head to compare (Rule-2, Binding). Run from here it is the same read, on this head:
```dyad-cmd
name: execute
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --evidence
```

## Verify
Phase 4 is not gated by the watermark: a shipped fence can rot with no new incident logged, and the
survey's no-op would hide exactly that — so an invocation on an unchanged ledger is not "do nothing" but
"re-verify the fences and report", writing no file when every fence still holds. Each closed mode is
re-tested against two reads: the guard registry, which says what is installed rather than what a record
claims, and the evidence path, every check and guard as observed on this head. The registry is read first
and unconditionally, so a fence that has left the registry stays visible in the same run that reports a red
check; the step's own exit status is the evidence run's. A check that no longer passes, or a fence no
longer in the registry, reopens its mode; a mode closes only by one of the play-book's three exits — fenced
at a named moment, a `backlog` row naming the fence to build, or recorded unfenceable on this kernel — and
a mode holding none of them is open whatever its record says:
```dyad-cmd
name: verify
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --list; dyad/bin/dyad check --evidence
```
