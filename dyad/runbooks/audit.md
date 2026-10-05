# Run-book: audit (the standing whole-system audit) — play-book `dyad/playbooks/audit.md`, #223
# sections: Survey, Regression, Fences, Drift, Incidents, Record

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the audit play-book as `dyad-cmd`
blocks, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/audit.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above; the sysadmin craft's server sections are a server's). The audit takes no parameter:
it reads the running system, and reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11
property 3). Every command runs from the git root and every command is **read-only**: the audit detects and
sizes, and the writing it leads to — the record, a proposed row, a mitigation's own PR — is the Agent's own
d-work work under its own plan-`Y` (Rule-3), never a run-book command. No command here is new code: each is one
the system already has (`dyad check`, `dyad dwork list`, `dyad session list`, the incident parser,
`incident-hardening`'s own `survey`, `git`); what the run-book adds is their order and the record they feed.

```text
dyad runbook list audit
dyad runbook run audit survey
```

## Survey
Phase 0, the idempotence gate: the live watermark of the tree, then the one of the newest record
(`**Audited:** tree <hash> · python <v> · git <v> · covered through <sha>, <date>`), and the verdict of their
comparison. The tree hash is that of `git ls-tree -r HEAD` **minus the dated audit records** of the instance
(`<instance>/audits/<date>-*.md`), which are the audit's own output — with them in the hash, the record the
audit commits would change the tree and no later audit could ever find it unchanged. `INCIDENTS.md` is not
dated and stays in. An unchanged line makes phases 1 and 3 a no-op and phase 2 still runs; a changed line is
the full exercise; no line anywhere is the first one, and the step says so rather than failing. The
postcondition tests the one thing the comparison needs, a head to hash:
```dyad-cmd
name: survey
class: read-only
role: any
undo: none
postcondition: git rev-parse --verify HEAD
scope: the tracked tree at HEAD and <instance>/audits/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; T="$(git ls-tree -r HEAD | awk -F'\t' -v re="^$I/audits/20[0-9-]+-.*[.]md\$" '$2 !~ re' | sha256sum | cut -d' ' -f1)"; PYV="$(dyad/bin/dyad-python --version 2>&1)"; PYV="${PYV#Python }"; GV="$(git --version)"; GV="${GV#git version }"; LIVE="tree $T · python $PYV · git $GV"; LAST="$(grep -h '^\*\*Audited:\*\*' "$I"/audits/*-audit.md 2>/dev/null | sed -n '$p')"
printf 'live: %s · head %s\n' "$LIVE" "$(git rev-parse --short HEAD)"; printf 'last: %s\n' "${LAST:-none}"
case "$LAST" in "") echo "verdict: no record carries a watermark: first exercise, full derivation";; *"$LIVE"*) echo "verdict: unchanged: phases 1 and 3 are a no-op, phase 2 still runs, nothing is written";; *) echo "verdict: changed: the full exercise";; esac
```

## Regression
Phase 1: the whole suite, every root, observed on the exact head and never read from the suite memo — the
evidence command the merge evidence already runs (Rule-14 property 3), so the audit's result and a merge's are
the same read at different heads. Its block is pasted into the record verbatim. The step's exit status is the
evidence run's: a red check makes the step red, and the record says which:
```dyad-cmd
name: regression
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad check --evidence
```

## Fences
Phase 2, ungated: the guard registry as installed, with its line count and a digest to compare against the
newest record's `**Fences:**` line; `core.hooksPath`; and the mode of every file git or the entrypoint runs by
path, which must be `100755` (#24). The registry is what is installed, not what a record claims. The step
exits non-zero when a mode is wrong, so a fence that cannot execute shows red in the event. The
postcondition tests that the hooks exist to be checked:
```dyad-cmd
name: fences
class: read-only
role: any
undo: none
postcondition: test -d dyad/hooks
scope: repo and <instance>/audits/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; L="$(dyad/bin/dyad check --list)"; printf 'live: registry %s lines, sha256 %s · hooksPath %s\n' "$(printf '%s\n' "$L" | wc -l | tr -d ' ')" "$(printf '%s\n' "$L" | sha256sum | cut -c1-16)" "$(git config core.hooksPath || echo unset)"
grep -h '^\*\*Fences:\*\*' "$I"/audits/*-audit.md 2>/dev/null | sed -n '$p' || echo "no record carries a Fences line: first exercise"
git ls-files -s -- dyad/hooks dyad/bin | awk '$1 != "100755" {print "not 100755: " $4; bad = 1} END {exit bad}'
```

## Drift
Phase 3, detect only: when the Rules were last edited against the newest sweep record in the audits
directory (a sweep is inference, Rule-5, so the step prints both dates and the Agent states the staleness); the
last activity of every `open`, `planned` and `blocked` row, and the `backlog` count; presence files past the
stale window; and the remote branches not merged into `origin/main`. Host documents are not read here: they are
read only on the host that keeps them, and the record says "unobserved" anywhere else. The postcondition tests
the row store the listing reads:
```dyad-cmd
name: drift
class: read-only
role: any
undo: none
postcondition: test -d "${DYAD_INSTANCE:-agent-corpus}/d-work/rows"
scope: repo, <instance>/audits/ and <instance>/d-work/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; git log -1 --format='rules last edited %ad (%h)' --date=short -- dyad/rules
ls -1 "$I/audits" | grep -i sweep | tail -n 1 || echo "no sweep record in $I/audits"
for s in open planned blocked; do dyad/bin/dyad dwork list --state "$s" | while read -r id rest; do printf '%s last activity %s %s\n' "$id" "$(git log -1 --format=%ad --date=short -- "$I/d-work/rows/${id#\#}.md")" "$rest"; done; done | cut -c1-150
printf 'backlog: %s rows\n' "$(dyad/bin/dyad dwork list --state backlog | wc -l | tr -d ' ')"; printf 'presence files stale: %s\n' "$(dyad/bin/dyad session list | grep -c ' stale ' || true)"
git branch -r --no-merged origin/main
```

## Incidents
Phase 3b: the incident log ingested through its one parser — the shape verdict and count of `incidents.py`, then
the rows per month and the d-works that carry two or more rows, read from `incidents.parse()` — and then the
survey of `incident-hardening`, the comparison of the live row count to the newest index audit's watermark, run
through the runner so it leaves its own event. Nothing is grouped here: the delta is reported and
`incident-hardening` classifies it. The postcondition tests the log exists to be read:
```dyad-cmd
name: incidents
class: read-only
role: any
undo: none
postcondition: test -f "${DYAD_INSTANCE:-agent-corpus}/audits/INCIDENTS.md"
scope: <instance>/audits/ (read)

dyad/bin/dyad-python dyad/scripts/incidents.py
dyad/bin/dyad-python -c "import sys,collections;sys.path.insert(0,'dyad/scripts');import incidents;r=incidents.parse();m=incidents.by_year_month(r);c=collections.Counter(i for x in r for i in set(x['ids']));print(len(r),'rows;',', '.join(k+': '+str(len(v)) for k,v in sorted(m.items())));print(sum(v>=2 for v in c.values()),'d-works carry two or more rows')"
dyad/bin/dyad runbook run incident-hardening survey
```

## Record
Phase 4, last: the newest record and its two watermark lines, read back after the Agent writes it. The record
is written by the Agent under the d-work's plan-`Y`, never by this step; the step tests that what was written
carries both lines, so the next audit's survey has something to compare to. An unchanged tree writes no record
and this step is not run for it:
```dyad-cmd
name: record
class: read-only
role: any
undo: none
postcondition: R="$(ls -1 "${DYAD_INSTANCE:-agent-corpus}"/audits/*-audit.md 2>/dev/null | tail -n 1)"; test -n "$R" && grep -q '^\*\*Audited:\*\*' "$R" && grep -q '^\*\*Fences:\*\*' "$R"
scope: <instance>/audits/ (read)

R="$(ls -1 "${DYAD_INSTANCE:-agent-corpus}"/audits/*-audit.md 2>/dev/null | tail -n 1)"; echo "newest record: ${R:-none}"; grep -H '^\*\*Audited:\*\*\|^\*\*Fences:\*\*' "$R"
```
