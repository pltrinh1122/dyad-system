# Run-book: self-diagnostic (a system's four diagnostic levels, run on itself) — play-book `dyad/playbooks/audit.md`, The self-diagnostic; #308, #381, #626
# sections: Level 1, Level 2, Level 3, Level 4

The self-diagnostic's steps, each read-only, run through the core runner from the git root with `main` checked out at
the head diagnosed; each appends one event to `<host>/runbooks/events/self-diagnostic.jsonl` (`DYAD_RUNBOOKS`
overrides). A system's own L4 claims go in its copy at `<host>/runbooks/self-diagnostic.md`, which the runner finds
first. The levels file is `<host>/self-diagnostic-levels.txt`, checked by `dyad/scripts/levels.py`. Coded halves are
read from the automaton sweep's report, which `unit` runs once (`audits.py level` classes its failing tests); no step
re-runs a check it carries. A run writes its events, then its record (`${DYAD_INSTANCE:-agent-corpus}/audits/
<YYYY-MM-DD>-self-diagnostic.md`, written by the party, never by a step) citing them: two changes, referent first
(Rule-1). Parameters: `K` (default 4) and `P` (default 3); the cursor is the newest record's `**Cursor:**` line.

```text
dyad/bin/dyad runbook list self-diagnostic
K=4 P=3 dyad/bin/dyad runbook run self-diagnostic health
```

**The gate.** Every step after `unit` except `record` first checks the event store: each step it names must have
exit 0 at the commit checked out, or it prints `gate closed at <sha>: not passed at this head: <steps>` and exits 3.
Exit status: 0 pass, 1 fail, 2 refused, 3 gate closed. The L3 → L4 gate's prose half is the reading's. `health`
fails off `main` or on a head that is not `origin/main` (D24).

## Level 1 (unit × coded check)
`health` first: whether the diagnostic can run here at all. It prints the head and the branch, `origin/main`, the
budget, and the newest previous record's `**Diagnosed:**` and `**Cursor:**` lines (none: the first run, and every
rotation starts at its first item). The levels file's own check (`dyad/scripts/levels.py`, the audit play-book's self-diagnostic) is in the
report (`finding: levels: …`, #619 P21); its pass criterion, the postcondition, is that `main` is checked out at
`origin/main` and the levels file classifies (`levels.py list unit`, the classification the levels use), so a run off
`main`, on a head the report does not read, or with a file that is absent, classifies too little or names what is
gone, is red before the report runs. It is named
`health` because a run-book under `<host>/runbooks/` carries a health command whose postcondition is its pass
criterion (dyad-system Rule-19 property 1; the core's live run-book test asserts it of every instance run-book). A
record already carrying today's date is named: the record's path is one per day, so this run reads its cursor and
then rewrites it (the audit play-book's self-diagnostic):
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: [ "$(git symbolic-ref -q --short HEAD)" = main ] && [ "$(git rev-parse HEAD)" = "$(git rev-parse -q --verify origin/main)" ] && dyad/bin/dyad-python dyad/scripts/levels.py list unit >/dev/null 2>&1
scope: HEAD, its branch and origin/main, <host>/self-diagnostic-levels.txt and <instance>/audits/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; R="$(ls -1 "$I"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)"; T="$I/audits/$(date -u +%F)-self-diagnostic.md"; B="$(git symbolic-ref -q --short HEAD || echo 'a detached HEAD')"
printf 'head %s on %s · K %s · P %s · today %s\n' "$(git rev-parse --short HEAD)" "$B" "${K:-4}" "${P:-3}" "$(date -u +%F)"
[ "$B" = main ] || echo "not on main: the report reads main, not this ref (the audit play-book's self-diagnostic)"
O="$(git rev-parse -q --verify origin/main || echo absent)"; [ "$O" = "$(git rev-parse HEAD)" ] || echo "HEAD is not origin/main (${O:0:7}): the report reads origin/main (D24)"
printf 'last record: %s\n' "${R:-none: the first run, every rotation starts at its first item}"; [ -z "$R" ] || grep -h '^\*\*Diagnosed:\*\*\|^\*\*Cursor:\*\*' "$R"
[ ! -f "$T" ] || echo "a record already carries today's date: $T"
```

`unit` runs the report once — `dyad automaton sweep` with no `--row`, every check of `main` the automaton runs after
each landed merge, the whole suite observed among them, its text stored under the git common dir — after one line
naming what the checkout holds besides the event store (S4's coded half, at L4). It then reads the report's failing
tests of the modules the levels file classifies `unit` (`audits.py level unit`, through `levels.py`'s own listing,
which refuses a levels file that fails its check, exit 1, or an absent one, exit 2, so an unclassified module never
drops silently out of both coded levels), and ends on one summary line and the report's `checks-sha256=` and
`report-sha256=`, so the step's event (`output_tail`) carries both digests. A report whose check ran no suite fails
the level:
```dyad-cmd
name: unit
class: read-only
role: any
undo: none
postcondition: none
scope: origin/main (read, fetched), the sweep's worktree and dyad-sweep/ store under the git common dir

D="$(git status --porcelain | grep -Ev 'runbooks/events/(self-diagnostic\.jsonl)?$' || true)"; printf 'changed besides the event store: %s\n' "${D:-none}"
T="$(mktemp)"; trap 'rm -f "$T"' EXIT; dyad/bin/dyad automaton sweep >"$T" 2>&1; printf 'report: exit %s\n' "$?"; cat "$T"
dyad/bin/dyad-python dyad/scripts/audits.py level unit "$(sed -n 's/^report-sha256=//p' "$T")"
```

## Level 2 (system × coded check)
`integration` reads the same stored report, behind the gate on `unit`: the failing tests of every module classified
`integration` — the ones that build a scratch repo, run git, install or spawn the runner (the audit play-book's self-diagnostic) — and every
failing check line, the coded checks of prose among them (Rule blocks, vocabulary, references, provenance counts,
zones, the manifest). It runs nothing; `checks-sha256=`, the tree's own check lines, is the level's evidence, and
anyone may re-run the report on the same head and compare it (D4, D21):
```dyad-cmd
name: integration
class: read-only
role: any
undo: none
postcondition: none
scope: the stored report at HEAD under the git common dir (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit || exit
dyad/bin/dyad-python dyad/scripts/audits.py level integration
```

## Level 3 (unit × prose claim)
`invariants` is L3's coded half: the runner's invariant pass, as the report counts it (`reading: invariants <i> ok,
<f> FAIL`, read off the check's own `[invariant]` lines, which a false invariant has already turned red, D2). It runs
nothing, so this level's own event holds the count. It exits 1 on any `FAIL`, or when the report holds no invariant
reading at all:
```dyad-cmd
name: invariants
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration || exit
dyad/bin/dyad-python dyad/scripts/audits.py level invariants
```

`units` names the K units the prose half reads: a unit is a tracked module declaring an `INVARIANTS` list
(templates and test modules aside), in sorted path order, starting at the first at or after the cursor's `units=`
and wrapping at the end (the audit play-book's self-diagnostic). Each is printed with its docstring's first line and the test modules found by
its name; its contract is that docstring and the rule that owns it. For each, the reading holds the claim *"this
unit's invariants and tests cover its stated contract"* against the attack *"name a contract clause whose breaking
no invariant and no test would catch"*; a landed attack is a finding, the uncovered clause and the invariant or test
that would cover it, and it stops the run before L4 (the audit play-book's self-diagnostic). The last line is the next run's `units=`:
```dyad-cmd
name: units
class: read-only
role: any
undo: none
postcondition: none
scope: the tracked modules and test modules, <instance>/audits/ (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration invariants || exit
I="${DYAD_INSTANCE:-agent-corpus}"; C="$(grep -h '^\*\*Cursor:\*\*' "$(ls -1 "$I"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)" 2>/dev/null | sed -n '$p')"
dyad/bin/dyad-python - "${K:-4}" "$C" <<'PY'
import ast, re, subprocess, sys
from pathlib import Path
k, c = int(sys.argv[1]), re.search(r"units=(\S+)", sys.argv[2])
units = sorted(subprocess.check_output(["git", "grep", "-l", "-E", "^INVARIANTS[ :=]", "--", "dyad", "crafts",
                                        ":!:*/templates/*", ":!:*/tests/*"], text=True).split())
i = next((j for j, u in enumerate(units) if c and c.group(1) != "none" and u >= c.group(1)), 0)
sample = [units[(i + j) % len(units)] for j in range(min(k, len(units)))]
for u in sample:
    doc = (ast.get_docstring(ast.parse(Path(u).read_text())) or "(no docstring)").splitlines()[0]
    tests = sorted(str(t) for g in ("dyad/tests", "crafts/*/tests") for t in Path(".").glob(f"{g}/**/test_{Path(u).stem}*.py"))
    print(f"unit {u}\n  contract: {doc[:150]}\n  tests: {' '.join(tests) or 'none found by name'}")
print(f"{len(units)} units, {len(sample)} read; next units={units[(i + len(sample)) % len(units)] if units else 'none'}")
PY
```

## Level 4 (system × prose claim)
The fixed claims, each with its attack and its coded half where it has one — the interaction model's eight
imperatives (`countersign-model.md` Part II §3, I1–I8), then three of the system's own:

| # | claim | attack | coded half |
|---|---|---|---|
| S1 | only a human countersigns (`countersign-model.md` I1) | among P sampled acts, find a countersignature whose signer is not the human party, or a disposition with no human's words behind it | the projector's `check` (I1), where the countersign projector runs: its live test at L2 and the `acts` step |
| S2 | one question per reply, its last line (I2) | in the session that runs the diagnostic, find a reply asking more than one question, or asking one anywhere but its last line | none: a question lives in the conversation, not in a store (`countersign-model.md` Part II §3) |
| S3 | falsified before proposed (I3) | among P sampled rows, find one carrying a plan whose plan file holds no falsification section and no pointer to a falsification record | none: the record's existence is the evidence (`countersign-model.md` Part II §3) |
| S4 | detect, don't dispose (I4) | in the session that runs the diagnostic, find a finding repaired rather than proposed, or a change to the tree since the head diagnosed besides the run's two writes (§8) | the line naming what the checkout holds besides the event store, printed before the report |
| S5 | the ledger and the provenance agree (I5) | for P sampled rows, find a `disposed` entry whose provenance text does not carry that answer | dyad-system's `agent/provenance` (the count, Rule-7 property 5) |
| S6 | no act is self-initiated (I6) | among the projector's I6 warnings and P sampled acts, find an act opened on a non-human party's own finding | the projector's `interaction`, warnings only |
| S7 | every act carries its mode and a countersignature reference (I7) | among P sampled acts, find one with no mode, a mode its processor contradicts, or an answered question no countersignature resolves to | the projector's schema validation and `check` (I7): a red one is the finding, and the reading confirms the sample |
| S8 | silence is not consent (I8) | among P sampled rows, find a state past `open` or a merge for which the row's `disposed` column records no answer: an act taken on silence | the projector derives no countersignature from an absent answer (`countersign-model.md` I8); dyad-system's plan gate (`agent/prs`) refuses a branch whose cited row carries no `Y plan` |
| S9 | the host record matches the host | find a kernel component whose observed version or presence differs from the system's host record under its host path, or a zone or profile the observed host contradicts | the manifest guard (the record's form, never its truth) |
| S10 | the Rules are coherent | for P Rule pairs in rotation, find a trigger on which the two instruct differently | none: coherence is inference (dyad-system Rule-5) |
| S11 | the frame loads | find the frame's sentinel absent from the start report of the session that runs the diagnostic | none |

Then the instance's own claims (below). Each landed attack is a finding (the audit play-book's self-diagnostic). Three steps print
what the reading needs, behind the gate on L3's coded half; the L3 → L4 gate's prose half is the reading's (the
gate, above): after a landed L3 attack these steps are not run. S2, S4 and S11 are read by no step, over the
session running the diagnostic (below).

`acts` serves S1, S3 and S5–S8. It runs the countersign projector without writing its document — `collect`, `check`
(references, the human signer of I1, the mode–processor rule and the countersignature references of I7) and the I6
line of `interaction` — and then prints the P rows the reading samples, by id from the cursor's `rows=` and
wrapping: each with its state, its `disposed` entries (S8 reads whether every state past `open` and every merge has
the answer that allows it), how many `disposition` entries its provenance record holds (dyad-system Rule-7 property 5
counts them; S5 reads whether each one's text carries the answer its `disposed` entry records) and its plan file,
with whether that file holds a falsification section or a pointer to a record (S3). The step exits 1 when the
projector's check fails — S1's and S7's coded half red — and its last line is the next run's `rows=`:
```dyad-cmd
name: acts
class: read-only
role: any
undo: none
postcondition: test -d "${DYAD_INSTANCE:-agent-corpus}/d-work/rows"
scope: <instance>/d-work/ and <instance>/audits/ (read; the projection is computed, not written)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration invariants || exit
dyad/bin/dyad-python -c 'import sys;sys.path[:0]=["dyad/scripts"];import dyadlib,project_countersign as pc;d=pc.collect(dyadlib.repo_root(),dyadlib.PKG);p=pc.check(d);[print("FAIL [project] countersign:",x) for x in p];print(("ok  " if not p else "FAIL")+" [project] countersign: "+pc.counts(d));print(pc.interaction_line(pc.interaction(d)));sys.exit(1 if p else 0)'; rc=$?
I="${DYAD_INSTANCE:-agent-corpus}"; C="$(grep -h '^\*\*Cursor:\*\*' "$(ls -1 "$I"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)" 2>/dev/null | sed -n '$p')"
dyad/bin/dyad-python - "${P:-3}" "$C" "$I" <<'PY'
import re, sys
from pathlib import Path
p, c, inst = int(sys.argv[1]), re.search(r"rows=(\d+)", sys.argv[2]), Path(sys.argv[3])
ids = sorted(int(f.stem) for f in (inst / "d-work" / "rows").glob("*.md") if f.stem.isdigit())
i = next((j for j, x in enumerate(ids) if c and x >= int(c.group(1))), 0)
sample = [ids[(i + j) % len(ids)] for j in range(min(p, len(ids)))]
for x in sample:
    row = dict(l.split(": ", 1) for l in (inst / "d-work" / "rows" / f"{x}.md").read_text().splitlines() if ": " in l)
    rec = inst / "d-work" / "provenance" / f"{x}.md"
    n = len(re.findall(r"^## \d+ disposition", rec.read_text(), re.M)) if rec.is_file() else None
    plan = inst / "d-work" / "plans" / f"{x}.md"
    fal = bool(re.search(r"^#+ .*[Ff]alsif|falsification/", plan.read_text(), re.M)) if plan.is_file() else None
    print(f"row {x} {row.get('state', '?')}: disposed {row.get('disposed', '')}")
    print(f"  provenance: {f'{n} disposition entries in {rec}' if n is not None else 'no record'}")
    print(f"  plan: {plan if plan.is_file() else 'no plan file'}" + ("" if fal is None else f"; falsification section or pointer: {'yes' if fal else 'none found'}"))
print(f"{len(ids)} rows, {len(sample)} read; next rows={ids[(i + len(sample)) % len(ids)] if ids else 'none'}")
PY
exit $rc
```

`pairs` serves S10: the P pairs of Agent Rules (`dyad/rules/RULE-*.md`) the reading compares, in sorted pair order by
Rule number, starting at the first pair at or after the cursor's `pairs=` and wrapping. For each pair the attack is
*"find a trigger on which the two instruct differently"*; coherence has no coded half (dyad-system Rule-5: inference
only). The last line is the next run's `pairs=`:
```dyad-cmd
name: pairs
class: read-only
role: any
undo: none
postcondition: test -d dyad/rules
scope: dyad/rules/ and <instance>/audits/ (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration invariants || exit
I="${DYAD_INSTANCE:-agent-corpus}"; C="$(grep -h '^\*\*Cursor:\*\*' "$(ls -1 "$I"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)" 2>/dev/null | sed -n '$p')"
dyad/bin/dyad-python - "${P:-3}" "$C" <<'PY'
import re, sys
from itertools import combinations
from pathlib import Path
p, c = int(sys.argv[1]), re.search(r"pairs=(\d+)-(\d+)", sys.argv[2])
rules = {int(m.group(1)): f.name for f in Path("dyad/rules").glob("RULE-*.md") if (m := re.match(r"RULE-(\d+)-", f.name))}
pairs = list(combinations(sorted(rules), 2))
i = next((j for j, x in enumerate(pairs) if c and x >= (int(c.group(1)), int(c.group(2)))), 0)
sample = [pairs[(i + j) % len(pairs)] for j in range(min(p, len(pairs)))]
for a, b in sample:
    print(f"pair {a}-{b}: {rules[a]} x {rules[b]}")
nxt = pairs[(i + len(sample)) % len(pairs)] if pairs else None
print(f"{len(rules)} Rules, {len(pairs)} pairs, {len(sample)} read; next pairs={f'{nxt[0]}-{nxt[1]}' if nxt else 'none'}")
PY
```

`host` serves S9: the kernel as observed here — the OS, Git, the interpreter `dyad-python` resolves, pydantic as
that interpreter imports it, the CLI inferencing agent — beside the kernel rows of the manifest (the core's and the
instance's `<host>/INFRASTRUCTURE.md`) and the kernel lines of the host records under the host path. The manifest
guard (L2) checks the record's form, never its truth; the reading compares the two, for a component whose observed
version or presence differs, or a zone or profile the observed host contradicts. Read whole, never sampled:
```dyad-cmd
name: host
class: read-only
role: any
undo: none
postcondition: none
scope: the host's kernel and the host path's records (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration invariants || exit
H="$(dyad/bin/dyad-python -c 'import sys;sys.path.insert(0,"dyad/scripts");import dyadlib;print(dyadlib.host_path(dyadlib.repo_root()))')"
printf 'observed: %s · %s · python %s · %s · %s\n' "$(uname -sr)" "$(git --version)" "$(dyad/bin/dyad-python -c 'import sys;print("%d.%d.%d" % sys.version_info[:3])')" "$(dyad/bin/dyad-python -c 'import pydantic;print("pydantic", pydantic.VERSION)' 2>/dev/null || echo 'pydantic not importable')" "$(timeout 10 claude --version 2>/dev/null || echo 'claude not on PATH')"
grep -H '| kernel |' dyad/infrastructure/INFRASTRUCTURE.md "$H/INFRASTRUCTURE.md" 2>/dev/null | cut -c1-200
grep -HE '^\| (Claude Code|Git|Python|pydantic) \|' "$H"/*.md 2>/dev/null | grep -v '| kernel |' | cut -c1-200 || echo "no kernel lines in $H/*.md beyond the manifest's"
```S2, S4 and S11 are read whole by no step, over the session running the diagnostic (D23); no step prints the
sentinel.

### Instance claims
A system adds its own L4 claims in the play-book's three columns, by its own d-work — in its own copy of this
run-book under `<host>/runbooks/`, or as rows of its record's Level 4 table — each read whole or over the same P
samples, its coded half, where it has one, already run in L2 (the audit play-book's self-diagnostic: countersign-system adds its hand-over
criteria H1–H5, each *"its status is as recorded"* against *"find an H whose stated status the corpus
contradicts"*). This core run-book carries none; a system with none keeps the row below as its placeholder, and its
record says so:

| # | claim | attack | coded half |
|---|-------|--------|------------|
| <id> | <the claim, as the system states it> | <what would have to be found for it to be false> | <the check that decides part of it, or none> |

### The record
Written once per run by the party that ran it, after the last step it reached, in this form — the bold lines are the
seams the next run's `health` and this run's `record` step read; a level the gate stopped keeps its heading and says
`not run (gate)`, a level after the one a run was asked to end at says `not run (last level <n>)`; a run that did
not reach L3 or L4 carries the previous `**Cursor:**` values forward (`none` on a first run). A second run on one
day rewrites that day's record (the audit play-book's self-diagnostic):

    # Self-diagnostic <YYYY-MM-DD>
    **Diagnosed:** head <short sha> · K <k> · P <p> · checks-sha256 <the unit step's value, or not run>

    ## Level 1 — unit × coded check
    **Result:** pass | fail | not run (gate) | not run (last level <n>)
    Evidence: the `unit` summary line, its event id. Findings: each failing module, or none.

    ## Level 2 — system × coded check
    **Result:** pass | fail | not run (gate) | not run (last level <n>)
    Evidence: the `integration` summary line, its event id; the report's `checks-sha256=` line.
    Findings: each failing module or check line, or none.

    ## Level 3 — unit × prose claim
    **Result:** pass | fail | not run (gate) | not run (last level <n>)
    Evidence: the `invariants` summary line; the K units `units` printed.
    | claim | attack | result | codify? |
    |-------|--------|--------|---------|
    | <unit> covers its stated contract | name a contract clause whose breaking no invariant and no test would catch | held, or landed: <clause> | no, or candidate (<the runs that read it so>) |

    ## Level 4 — system × prose claim
    **Result:** pass | fail | not run (gate) | not run (last level <n>)
    Evidence: the `acts` projector lines and P rows, the `pairs` P pairs, the `host` lines.
    | claim | attack | result | codify? |
    |-------|--------|--------|---------|
    | S1 … S11, then each instance claim — one row per claim sample | … | … | … |

    **Cursor:** units=<path> rows=<id> pairs=<a>-<b>

`record` runs last, needs no gate, and judges the record against the events left at its `**Diagnosed:**` head; the
L3 and L4 tables stay inference:
```dyad-cmd
name: record
class: read-only
role: any
undo: none
postcondition: R="$(ls -1 "${DYAD_INSTANCE:-agent-corpus}"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)"; test -n "$R" && grep -q '^\*\*Diagnosed:\*\*' "$R" && grep -q '^\*\*Cursor:\*\*' "$R"
scope: the event store and <instance>/audits/ (read)

dyad/bin/dyad-python - "${DYAD_INSTANCE:-agent-corpus}" <<'PY'
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, "dyad/scripts"); import runbook as r
recs = sorted((Path(sys.argv[1]) / "audits").glob("*-self-diagnostic.md"))
if not recs:
    print("no record yet: write it, then run this step"); sys.exit(1)
rec, text, fails = recs[-1], recs[-1].read_text(), []
d = re.search(r"^\*\*Diagnosed:\*\*.*?head ([0-9a-f]{7,40})\b.*?checks-sha256 (.+?)\s*$", text, re.M)
if not d:
    print(f"FAIL [record] {rec}: no **Diagnosed:** line naming a head and a checks-sha256"); sys.exit(1)
h = d.group(1)
if subprocess.run(["git", "rev-parse", "--verify", "-q", f"{h}^{{commit}}"], capture_output=True).returncode:
    fails.append(f"**Diagnosed:** names head {h}, which this repository does not hold")
at = lambda c: bool(c) and (c.startswith(h) or h.startswith(c))
ev = {e["name"]: e for e in r.read_events(r.events_path(r.dyadlib.repo_root(), "self-diagnostic")) if at(e.get("commit", ""))}
st = lambda n: "absent" if n not in ev else {0: "pass", 3: "gate"}.get(ev[n]["exit"], "fail")
for n in ("health", "unit", "integration", "invariants", "units", "acts", "pairs", "host"):
    print(f"event {n}: {st(n)}" + (f" ({ev[n]['id']})" if n in ev else ""))
m = re.search(r"checks-sha256=(\w+)", ev["unit"]["output_tail"]) if "unit" in ev else None
sha = m.group(1) if m else "not run"
print(f"record {rec}: head {h} · checks-sha256 {sha} in its events")
if d.group(2) != sha:
    fails.append(f"**Diagnosed:** checks-sha256 {d.group(2)}, the events at {h} {sha}")
got, lv = {}, None
for line in text.splitlines():
    lv = int(mm.group(1)) if (mm := re.match(r"## Level (\d)", line)) else lv
    if lv and (mm := re.match(r"\*\*Result:\*\*\s*(pass|fail|not run \((?:gate|last level \d)\))", line)):
        got.setdefault(lv, mm.group(1))
LEVELS = {1: ("unit",), 2: ("integration",), 3: ("invariants", "units"), 4: ("acts", "pairs", "host")}
CODED = {1: True, 2: True, 3: False, 4: False}
stopped = None
for lv, steps in LEVELS.items():
    s, res = [st(n) for n in steps], got.get(lv)
    if stopped:
        ok, why = {stopped}, "an earlier level ended the run"
    elif "fail" in s:
        ok, why = {"fail"}, "a step failed"
    elif "gate" in s:
        ok, why = {"not run (gate)"}, "a step found its gate closed"
    elif set(s) == {"absent"}:
        ok, why = ({f"not run (last level {lv - 1})"} if lv > 1 else set()), "no step left an event" if lv > 1 else "L1 always runs and left no event"
    elif "absent" in s:
        ok, why = set(), "the level was only partly run: " + " ".join(n for n in steps if st(n) == "absent") + " left no event"
    else:
        ok, why = ({"pass"} if CODED[lv] else {"pass", "fail"}), "every step passed"
    if res not in ok:
        fails.append(f"Level {lv}: **Result:** {res or 'missing'}; {why}, so it may be {' | '.join(sorted(ok)) or 'nothing'}")
    stopped = None if res == "pass" else res if res and res.startswith("not run (last") else "not run (gate)"
cur = re.search(r"^\*\*Cursor:\*\*(.*)$", text, re.M)
if not cur or not all(f" {k}=" in " " + cur.group(1) for k in ("units", "rows", "pairs")):
    fails.append("**Cursor:** missing, or without units=, rows= and pairs=")
for f in fails:
    print(f"FAIL [record] {rec}: {f}")
print(f"ok   [record] {rec} agrees with the events at {h}" if not fails else f"{len(fails)} disagreement(s)")
sys.exit(1 if fails else 0)
PY
```
