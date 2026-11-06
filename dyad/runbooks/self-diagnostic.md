# Run-book: self-diagnostic (a system's four diagnostic levels, run on itself) — play-book `dyad/playbooks/audit.md`, The self-diagnostic; #308, #381
# sections: Level 1, Level 2, Level 3, Level 4

A core run-book (package, `dyad/runbooks/`; agent zone) in the sysadmin craft's run-book form
(`crafts/sysadmin/rules/server-instances.md`), run by `dyad runbook run self-diagnostic <step>`; a system that wants
its own L4 claims in a run-book copies it to `<host>/runbooks/self-diagnostic.md` (`<host>` the host path,
preference `host-path`), which the runner then finds first (`runbook.all_runbooks`: an instance run-book of the
same name wins), and from then on that copy is the system's own. The
levels file it reads is instance data: `<host>/self-diagnostic-levels.txt`, seeded by hand from
`dyad/templates/self-diagnostic-levels.txt` and the levels script `dyad/scripts/levels.py` (the core's since C4 of #369, d-work #378, which re-pointed the paths below from the craft's). Since #619 the coded halves are not run here: `unit` runs the automaton sweep's report once (`dyad automaton sweep` with no `--row`, the audit's report), and `unit`, `integration` and `invariants` read it, classing its failing tests by the levels file (`audits.py level`), so no step re-runs a check the report carries. Its section set is its own (the `# sections:` line above), one section per diagnostic level in the
model's order — L1 unit × coded check, L2 system × coded check, L3 unit × prose claim, L4 system × prose claim
(the play-book §2) — so the sysadmin craft's run-book guard checks it against these four and not
against a server's ten. Each step is a `dyad-cmd` block run by either party through the core runner, which prints
the native line, tests the postcondition and appends one event to `<host>/runbooks/events/self-diagnostic.jsonl`
(`DYAD_RUNBOOKS` overrides `<host>/runbooks`): the runner's telemetry, which the gate below reads. Every command
runs from the git root, with `main` checked out at the head diagnosed (play-book §2, L2), and every command is
**read-only**. A run writes two things, in two zones (play-book §8): the runner's events, in the host path's zone —
committed, and append-only on `main` (the sysadmin craft's `server-instances.md` property 7) — and its record,
`${DYAD_INSTANCE:-agent-corpus}/audits/<YYYY-MM-DD>-self-diagnostic.md` (play-book §7; its form is under Level 4), in
the agent zone. The record holds what the reading found, so it is written by the party that ran the diagnostic,
never by a step. The two land as two changes, the events first and then the record that cites their ids — the
referent before the referrer (dyad-system Rule-1) — and the last step, `record`, reads the record back against the
events. What a finding becomes is the system's own process — in a dyad system its core Rules (play-book §5) — never a
command here: nothing is repaired inside a run.

Two parameters, read from the environment: `K`, the units L3 reads (default 4), and `P`, the samples L4 reads
(default 3) — play-book §4. The rotation cursor is the newest previous record's `**Cursor:**` line; `health` prints it,
and `units`, `acts` and `pairs` start where it points and print where the next run starts.

```text
dyad/bin/dyad runbook list self-diagnostic
K=4 P=3 dyad/bin/dyad runbook run self-diagnostic health
```

**The gate** (play-book §3). Every step after `unit` except `record` opens with one line that reads the event store:
the latest event of each step it names must have exit 0 at the commit checked out now. Otherwise the line prints
`gate closed at <sha>: not passed at this head: <steps>` and the step exits 3 having run nothing else; the record
writes that level, and every later one, `not run (gate)`. A run asked to end after level n (`/diagnose n`) runs no
later step, and the record writes each later level `not run (last level <n>)` (play-book §3). Exit status throughout:
0 pass, 1 fail, 2 refused — by the runner (a role, a missing run-book or command), or by `levels.py list` or
`audits.py level` (no levels file, no stored report at this head) — 3 gate closed. The gate keys on the head, so on a head whose
earlier levels already passed a later level may be run alone. The run's own events are a change in the working tree
until they are committed, so the report is never computed there: the sweep runs in its own worktree, on `main` as
fetched, and `unit` prints first what the checkout holds besides the event store (L4's S4 reads that line). The gate
is mechanical between coded steps only: L3's prose half — no attack landed on a sampled unit — is read, so the
L3 → L4 gate is the reading's, and the record holds it. The diagnostic reads the head of `main`: the report is
always `origin/main`'s, so `health` names the branch and the fetched `main`, and its pass criterion fails off `main`
or on a head that is not `origin/main` (D24).

## Level 1 (unit × coded check)
`health` first: whether the diagnostic can run here at all. It prints the head and the branch, `origin/main`, the
budget, and the newest previous record's `**Diagnosed:**` and `**Cursor:**` lines (none: the first run, and every
rotation starts at its first item). The levels file's own check (`dyad/scripts/levels.py`, play-book §6) is in the
report (`finding: levels: …`, #619 P21); its pass criterion, the postcondition, is that `main` is checked out at
`origin/main` and the levels file classifies (`levels.py list unit`, the classification the levels use), so a run off
`main`, on a head the report does not read, or with a file that is absent, classifies too little or names what is
gone, is red before the report runs. It is named
`health` because a run-book under `<host>/runbooks/` carries a health command whose postcondition is its pass
criterion (dyad-system Rule-19 property 1; the core's live run-book test asserts it of every instance run-book). A
record already carrying today's date is named: the record's path is one per day, so this run reads its cursor and
then rewrites it (play-book §7):
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: [ "$(git symbolic-ref -q --short HEAD)" = main ] && [ "$(git rev-parse HEAD)" = "$(git rev-parse -q --verify origin/main)" ] && dyad/bin/dyad-python dyad/scripts/levels.py list unit >/dev/null 2>&1
scope: HEAD, its branch and origin/main, <host>/self-diagnostic-levels.txt and <instance>/audits/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; R="$(ls -1 "$I"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)"; T="$I/audits/$(date -u +%F)-self-diagnostic.md"; B="$(git symbolic-ref -q --short HEAD || echo 'a detached HEAD')"
printf 'head %s on %s · K %s · P %s · today %s\n' "$(git rev-parse --short HEAD)" "$B" "${K:-4}" "${P:-3}" "$(date -u +%F)"
[ "$B" = main ] || echo "not on main: the report reads main, not this ref (play-book §2, L2)"
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
`integration` — the ones that build a scratch repo, run git, install or spawn the runner (play-book §6) — and every
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
and wrapping at the end (play-book §4). Each is printed with its docstring's first line and the test modules found by
its name; its contract is that docstring and the rule that owns it. For each, the reading holds the claim *"this
unit's invariants and tests cover its stated contract"* against the attack *"name a contract clause whose breaking
no invariant and no test would catch"*; a landed attack is a finding, the uncovered clause and the invariant or test
that would cover it, and it stops the run before L4 (play-book §3). The last line is the next run's `units=`:
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
The fixed claims, each with its attack and its coded half where it has one (play-book §2, L4) — the interaction
model's eight imperatives, then three of the system's own: S1 only a human countersigns (I1); S2 one question per
reply, its last line (I2); S3 falsified before proposed (I3); S4 detect, don't dispose (I4); S5 the ledger and the
provenance agree (I5); S6 no act is self-initiated (I6); S7 every act carries its mode and a countersignature
reference (I7); S8 silence is not consent (I8); S9 the host record matches the host; S10 the Rules are coherent; S11
the frame loads. Then the instance's own claims (below). Each landed attack is a finding (play-book §5). Three steps print
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
```

S2, S4 and S11 are read whole and by no step, over the one conversation a run can see, the session running the
diagnostic (play-book §2, L4; D23): S2 finds a reply of that session asking more than one question, or one anywhere but
its last line, or does not; S4 finds a finding of this run repaired rather than proposed, or a change to the tree
since the head diagnosed besides the run's two writes — `unit`'s first line is its coded half — or does not; S11
finds the frame's sentinel in that session's start report, or does not. No step prints the sentinel, since a step's
output lands in the committed event store and the frame's sentinel is never cached anywhere.

### Instance claims
A system adds its own L4 claims in the play-book's three columns, by its own d-work — in its own copy of this
run-book under `<host>/runbooks/`, or as rows of its record's Level 4 table — each read whole or over the same P
samples, its coded half, where it has one, already run in L2 (play-book §2: countersign-system adds its hand-over
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
day rewrites that day's record (play-book §7):

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

`record` runs last, whatever the gate did, and needs no gate, once the record is written. It reads the newest
record's `**Diagnosed:**` head and judges the record against the events the steps left **at that head** — the latest
event of each step there (`pass`, `fail`, `gate` or `absent`) and the `unit` step's `checks-sha256` — so a
commit made since the run (the plan file's, the record's own) moves nothing it reads. It fails when that head does
not resolve, when the record's checks sha is not the events', when a level's result is one the events rule out —
a step that failed recorded as anything but `fail`, a gated step recorded as anything but `not run (gate)`, a coded
level recorded `pass` that its events do not show, a level whose steps all left no event recorded as anything but
`not run (last level <n>)` for the level before it, a level only partly run — when a level after a `fail` or a
`not run (gate)` is anything but `not run (gate)`, or one after a `not run (last level <n>)` anything but the same,
or when the cursor lacks `units=`, `rows=` or `pairs=`. L1 always runs, so an L1 with no event fails. What it cannot
check is the reading itself, L3's and L4's tables, which stay inference (play-book, Inference, stated):
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
