# Run-book: audit (the standing whole-system audit) — play-book `dyad/playbooks/audit.md`, #223, #619, #626
# sections: Report, Fences, Drift, Record

The audit play-book's steps, every one read-only, run through the core runner from the git root; each records an
event in `<runbooks>/events/audit.jsonl`. No parameter; the instance is `${DYAD_INSTANCE:-agent-corpus}`. The first
step runs the automaton sweep's report, which carries every coded check; the rest read what only the auditor's
checkout holds. The record is the party's to write, never a command's.

```text
dyad runbook list audit
dyad runbook run audit report
```

## Report
Phases 0 to 3b, coded:
```dyad-cmd
name: report
class: read-only
role: any
undo: none
postcondition: git rev-parse --verify -q origin/main
scope: origin/main (read, fetched), the git common dir's sweep worktree and dyad-sweep/ store

dyad/bin/dyad automaton sweep
```

## Fences
Phase 2's one local check, what only the auditor's checkout holds:
```dyad-cmd
name: hooks
class: read-only
role: any
undo: none
postcondition: [ "$(git config core.hooksPath)" = dyad/hooks ]
scope: the checkout's git config and <instance>/audits/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; printf 'live: hooksPath %s\n' "$(git config core.hooksPath || echo unset)"
grep -h '^\*\*Fences:\*\*' "$I"/audits/*-audit.md 2>/dev/null | sed -n '$p' || echo "no record carries a Fences line: first exercise"
```

## Drift
Phase 3's one listing the report does not hold:
```dyad-cmd
name: host
class: read-only
role: any
undo: none
postcondition: none
scope: the host path's tracked documents (read)

H="$(dyad/bin/dyad-python -c 'import sys;sys.path.insert(0,"dyad/scripts");import dyadlib;print(dyadlib.host_path(dyadlib.repo_root()))')" || exit
printf 'running kernel: %s · %s\n' "$(uname -sr)" "$(dyad/bin/dyad-python --version 2>&1)"
git ls-files -- "$H" | grep '[.]md$' | while read -r f; do printf '%s last edited %s\n' "$f" "$(git log -1 --format='%ad (%h)' --date=short -- "$f")"; done
```

## Record
Phase 4:
```dyad-cmd
name: record
class: read-only
role: any
undo: none
postcondition: dyad/bin/dyad-python dyad/scripts/audits.py record >/dev/null
scope: <instance>/audits/ (read)

dyad/bin/dyad-python dyad/scripts/audits.py record
```
