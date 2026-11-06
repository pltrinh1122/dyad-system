# Run-book: audit (the standing whole-system audit) — play-book `dyad/playbooks/audit.md`, #223, #619
# sections: Report, Fences, Drift, Record

A core run-book (package, `dyad/runbooks/`; agent zone): the steps of the audit play-book as `dyad-cmd`
blocks, run by either party through the core runner, which prints the native line, records an event in the
instance's `<runbooks>/events/audit.jsonl` and tests the postcondition. Its section set is its own (the
`# sections:` line above; the sysadmin craft's server sections are a server's). The audit takes no parameter:
it reads the running system, and reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11
property 3). Every command runs from the git root and every command is **read-only**: the audit detects and
sizes, and the writing it leads to — the record, a proposed row, a mitigation's own PR — is the agent's own
d-work work under its own plan-`Y` (Rule-3), never a run-book command. Since #619 the coded checks are the
automaton's: the first step runs `dyad automaton sweep` with no `--row`, whose report carries every check the
automaton runs after each landed merge, the audit's own among them (`dyad/scripts/audits.py`, the sweep part
`sweep_audit`), and the stall lines the home reads. The steps after it are what only the auditor's checkout can
read, and the reading the play-book keeps as inference.

```text
dyad runbook list audit
dyad runbook run audit report
```

## Report
Phases 0 to 3b, coded: `dyad automaton sweep` with no `--row`, run on `origin/main` as fetched. It prints the
readings first — the watermark (`reading: audit watermark: … unchanged | changed | first exercise`, the gate of
phase 0, read off the code tree with the dated audit records pruned), the registry's count and digest, the incident
sizing and the hardening watermark, stale presence files, unmerged branches, the suite per root and the invariant
pass — then the findings in two groups, `standing` (told to the home already) and `new`, every check of the tree
among them (the suite observed, every root, never from a memo), then the stall block the home reads, and last
`checks-sha256=`, `report-sha256=` and where the text is stored (`<git common dir>/dyad-sweep/`, never tracked). It
posts nothing and lands nothing. Its exit is the sweep's: 1 when a finding fails. The postcondition tests what the
report reads, a fetched `main`:
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
Phase 2's one local check, what only the auditor's checkout holds: `core.hooksPath`, which the report cannot read
(the sweep's worktree is the automaton's), beside the newest record's `**Fences:**` line, into which the auditor
writes it. The registry's count and digest, a guard that left the registry, and the mode of `dyad/hooks/*` and
`dyad/bin/*` (`syseng/naming`) are in the report. The postcondition is the fence itself: hooks enabled:
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
Phase 3's one listing the report does not hold: the host documents and when each was last edited, beside the
running kernel, for the operate unit's reading of whether a document older than the kernel still holds (the frame's
convention: re-verify before relying on it). The Rules against the newest Rule-5 sweep record, presence and
branches are in the report; rows with no activity are the home's read. Staleness is stated and the pruning question
asked by the auditor; nothing here judges it:
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
Phase 4: the record is the auditor's, written after the report, its mechanical section the report verbatim, cited by
its two digests. `record` reads the newest record's `**Audited:**` and `**Fences:**` lines back through the same
function the report's P19 finding uses (`audits.py record`): a check of the new file, which the report, run before it
existed, could not see. The postcondition is the same reading:
```dyad-cmd
name: record
class: read-only
role: any
undo: none
postcondition: dyad/bin/dyad-python dyad/scripts/audits.py record >/dev/null
scope: <instance>/audits/ (read)

dyad/bin/dyad-python dyad/scripts/audits.py record
```
