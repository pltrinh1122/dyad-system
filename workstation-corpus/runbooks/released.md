# Run-book: released (the release service on GitHub Actions) — d-work #461
# sections: Status/health, Pending, Retry, Logs, Data

Instance: not a server on this host — the workflow `.github/workflows/dyad-release.yml` (display name `released`; its
logic `.github/released.py`), run by GitHub Actions with the hosting's token on a push to `main` that touches the
ledger rows, and on manual dispatch (plan #461 revisions 3 and 4). Its supervisor is the hosting: nothing here starts, stops
or restarts it, and it survives every session because no session runs it (plan #461 attack 1). The workflow is the
distribute seat's (its fence, `.github/workflows/`); this run-book, its events location and its health are the operate
seat's (`MANDATES.md`; #461 revision 2). So this run-book declares its own section set (the sysadmin craft's
`server-instances.md` property 2). Every command but `retry` is **read-only**. There is no process to start, stop or
restart: start is a release entry landing on `main` (or `retry`, below); stop is disabling the workflow in the
hosting's settings, the Operator's act; upgrade and credential rotation are changes to the two workflow files, each a
distribute-seat infra-zone PR, and none is run from here.

**Trigger.** The only trigger is the ledger entry that records the Operator's release `Y` on the release's row,
`Y release <tag> at <cut sha> (archive <sha256>)`, written by the cos as a ledger-only clerical commit (Rule-11
Ratification events; Rule-2). There is no request file. `released` reads `main`, finds a release entry whose tag does
not exist yet, checks the tag equals its `VERSION` at the cut sha, builds by the one code path, verifies the archive's
sha256, creates the annotated tag and the Release. A forged entry would publish (plan #461 attack 4): the
optional one-tap environment gate is the Operator's to ask for, by the cos.

**Record.** `released` writes nothing to the repo (plan #461 revision 4): no events file and no commit. Its record is
what it creates — the annotated tag, whose message names the cut sha, the archive sha256 and the row, and the Release
with its archive — and the workflow run, all read through the hosting (The World; Rule-20 `world`). The health below
reads that record against the ledger, and the cos closes the release row once health shows its tag. This run-book's
own commands, run through the core runner, leave the runner's events (Rule-19), written only when a reading changes
(#438) and committed as events-only: they are observations of the record, never part of it.

Every command runs from the git root as either party, `sudo`-free and with no GitHub token: tags are read with
`git ls-remote`, Releases through the public REST endpoint. The repo is read from `origin`.

```text
dyad runbook list released
dyad runbook run released health
```

## Status/health
Health (server-instances rule, property 4; Rule-19 kernel): every recorded release entry has its tag, at its cut sha,
and its GitHub Release. The command reads every row's `disposed` for the form `Y release <tag> at <sha>`, resolves the
tag on `origin` (the peeled commit of an annotated tag), and asks the hosting for the Release. One line per gap, `no
tag: <tag>`, `tag not at cut: <tag> (<sha>)` or `no Release: <tag>`, then a count line. **Pass: exit 0 and no gap
line**; the postcondition is the same check, silent. Entries recorded before #461 carry no `at <sha>` and are not read. With no entry in the new form, the command
reads zero entries and passes: there is nothing yet to reconcile.
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: r=$(git remote get-url origin | sed -E 's#^https?://([^@]*@)?github.com/##; s#^git@github.com:##; s#\.git$##'); fail=0; n=0; for e in $(grep -hoE 'Y release [A-Za-z0-9._-]+ at [0-9a-f]{7,40}' agent-corpus/d-work/rows/*.md | awk '{print $3"@"$5}' | sort -u); do n=$((n+1)); t=${e%@*}; s=${e#*@}; p=$(git ls-remote --tags origin "refs/tags/$t" "refs/tags/$t^{}" | awk -v t="refs/tags/$t" '$2==t"^{}"{pe=$1} $2==t{pl=$1} END{print (pe?pe:pl)}'); if [ -z "$p" ]; then fail=1; else case "$p" in "$s"*) ;; *) fail=1;; esac; fi; curl -sf -o /dev/null "https://api.github.com/repos/$r/releases/tags/$t" || fail=1; done; exit $fail
scope: agent-corpus/d-work/rows/ (read), origin's tags and the hosting's Releases (read)

r=$(git remote get-url origin | sed -E 's#^https?://([^@]*@)?github.com/##; s#^git@github.com:##; s#\.git$##'); fail=0; n=0; for e in $(grep -hoE 'Y release [A-Za-z0-9._-]+ at [0-9a-f]{7,40}' agent-corpus/d-work/rows/*.md | awk '{print $3"@"$5}' | sort -u); do n=$((n+1)); t=${e%@*}; s=${e#*@}; p=$(git ls-remote --tags origin "refs/tags/$t" "refs/tags/$t^{}" | awk -v t="refs/tags/$t" '$2==t"^{}"{pe=$1} $2==t{pl=$1} END{print (pe?pe:pl)}'); if [ -z "$p" ]; then echo "no tag: $t"; fail=1; else case "$p" in "$s"*) ;; *) echo "tag not at cut: $t ($s)"; fail=1;; esac; fi; curl -sf -o /dev/null "https://api.github.com/repos/$r/releases/tags/$t" || { echo "no Release: $t"; fail=1; }; done; echo "$n release entr(ies) checked"; exit $fail
```

## Pending
The release entries the service has not acted on yet: a recorded `Y release <tag> at <sha>` whose tag does not exist
on `origin`. Empty is the normal state between releases. A line that stays here after the workflow has run on that
entry's commit is a failed run: read its log (below) and report it to the distribute seat.
```dyad-cmd
name: pending
class: read-only
role: any
undo: none
postcondition: none
scope: agent-corpus/d-work/rows/ (read), origin's tags (read)

for e in $(grep -hoE 'Y release [A-Za-z0-9._-]+ at [0-9a-f]{7,40}' agent-corpus/d-work/rows/*.md | awk '{print $3"@"$5}' | sort -u); do t=${e%@*}; git ls-remote --exit-code --tags origin "refs/tags/$t" >/dev/null || echo "pending: $t at ${e#*@}"; done; echo "pending check done"
```

## Retry
A manual run of the service for one recorded entry, after a refused or failed run whose cause has been fixed — the
workflow's dispatch with its `tag` input. It executes a release the Operator already ratified, so it is no new
disposition and never a first release: the entry must already be on the row. It publishes, and tags never move, so it
is **destructive** and Operator-run (a token); the runner confirms it on the terminal. The postcondition holds when the
tag exists on `origin` and its Release exists. A cloud seat without a token reaches the same dispatch through the
hosting's actions API, as the distribute seat does, on the Operator's word.
```dyad-cmd
name: retry
class: destructive
role: operator
undo: none (a tag never moves; a wrong Release is deleted by hand on the hosting, the tag kept)
postcondition: r=$(git remote get-url origin | sed -E 's#^https?://([^@]*@)?github.com/##; s#^git@github.com:##; s#\.git$##'); git ls-remote --exit-code --tags origin "refs/tags/${TAG:?release tag}" >/dev/null && curl -sf -o /dev/null "https://api.github.com/repos/$r/releases/tags/$TAG"
scope: tag ${TAG}, its Release, one run of dyad-release.yml

gh workflow run dyad-release.yml -f tag="${TAG:?release tag}"
```

## Logs
The workflow's last runs, from the hosting's public REST endpoint: run number, event, status, conclusion and the run's
page. A run's log itself needs a token and is read on the run's page.
```dyad-cmd
name: logs
class: read-only
role: any
undo: none
postcondition: none
scope: the hosting's workflow runs for dyad-release.yml (read)

r=$(git remote get-url origin | sed -E 's#^https?://([^@]*@)?github.com/##; s#^git@github.com:##; s#\.git$##'); curl -sf "https://api.github.com/repos/$r/actions/workflows/dyad-release.yml/runs?per_page=5" | python3 -c "import json,sys; [print(x['run_number'], x['event'], x['status'], x['conclusion'], x['html_url']) for x in json.load(sys.stdin).get('workflow_runs', [])]"
```

## Data
Where state lives: the ledger rows that record each release `Y` (`agent-corpus/d-work/rows/`), the tags and Releases
and the workflow runs on the hosting. Nothing lives on this host, and the service keeps no file in the repo. A fresh deployment
needs only `main`: the workflow file and the ledger; every release it has made is recomputable from the tags. The
command lists the recorded release entries in the new form.
```dyad-cmd
name: data
class: read-only
role: any
undo: none
postcondition: none
scope: agent-corpus/d-work/rows/ (read)

grep -HoE 'Y release [A-Za-z0-9._-]+ at [0-9a-f]{7,40}( \(archive [0-9a-f]{64}\))?' agent-corpus/d-work/rows/*.md || echo "no release entry in the #461 form yet"
```
