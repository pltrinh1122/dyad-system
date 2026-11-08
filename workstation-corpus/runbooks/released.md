# Run-book: released (the release service on GitHub Actions) — d-work #461, #626
# sections: Status/health, Pending, Retry, Logs, Data

Instance: the workflow `.github/workflows/dyad-release.yml` (`released`; logic `dyad release`, `dyad/scripts/release.py`),
supervised by the hosting. The workflow is distribute's; this run-book and its health are operate's (`MANDATES.md`).
Stop is disabling the workflow (the operator's); upgrade and credential rotation are distribute's infra-zone PRs.
Every command but `retry` is read-only, runs from the git root with no token, and reads the repo from `origin`.

**Trigger.** A push to `main` that lands the ledger entry `Y release <tag> at <cut sha> (archive <sha256>)` on a
release's row (Rule-11 Ratification events), or `retry`. `released` builds at the cut by the one code path, refuses an
archive whose sha256 differs from the recorded one, and creates the annotated tag and the Release. The archive's sha256
is distribute's one build per tag (`dyad/playbooks/release.md`); the CI rebuild is the determinism proof.

**Evidence.** `released` writes nothing to the repo: its record is the tag, the Release and the workflow run, read
through the hosting. The cos closes the release row once health shows its tag.

## Status/health
Step: `dmc:release-entry-state`, for every recorded entry. One line per gap, then a count line; exit 0 is the pass. The
postcondition is the same check, silent.
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
Entries whose tag does not exist yet (`dmc:release-entry-state`). A line that outlasts the workflow's run on the
entry's commit goes to distribute, with the run's log.
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
Question: the operator runs it for one already-recorded entry after its cause is fixed. It publishes and a tag never
moves, so it is destructive and operator-run; the runner confirms it on the terminal. A cloud seat without a token
reaches the same dispatch through the hosting's actions API, on the operator's word.
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
The workflow's last runs, from the hosting's public endpoint; a run's log is read on its page.
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
State lives in the release entries on the rows and in the tags, Releases and runs on the hosting; nothing on this host,
no file in the repo. A fresh deployment needs only `main`. The command lists the recorded entries.
```dyad-cmd
name: data
class: read-only
role: any
undo: none
postcondition: none
scope: agent-corpus/d-work/rows/ (read)

grep -HoE 'Y release [A-Za-z0-9._-]+ at [0-9a-f]{7,40}( \(archive [0-9a-f]{64}\))?' agent-corpus/d-work/rows/*.md || echo "no release entry in the #461 form yet"
```
