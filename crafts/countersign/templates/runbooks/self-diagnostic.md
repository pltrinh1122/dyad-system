# Run-book: self-diagnostic (a system's four diagnostic levels, run on itself) — model `crafts/countersign/rules/self-diagnostic.md`, dyad-system #308
# sections: Level 1, Level 2, Level 3, Level 4

A run-book in the sysadmin craft's run-book form (`crafts/sysadmin/rules/server-instances.md`), seeded from the
countersign craft's `templates/runbooks/self-diagnostic.md` to `<host>/runbooks/self-diagnostic.md` (by hand, the
craft's README; `<host>` the host path, preference `host-path`) and from then on the system's own, changed by its own
units of work. Its section set is its own (the `# sections:` line above), one section per diagnostic level in the
model's order — L1 unit × coded check, L2 system × coded check, L3 unit × prose claim, L4 system × prose claim
(`rules/self-diagnostic.md` §2) — so the sysadmin craft's run-book guard checks it against these four and not
against a server's ten. Each step is a `dyad-cmd` block run by either party through the core runner, which prints
the native line, tests the postcondition and appends one event to `<host>/runbooks/events/self-diagnostic.jsonl`
(`DYAD_RUNBOOKS` overrides `<host>/runbooks`): the runner's telemetry, which the gate below reads. Every command
runs from the git root, with `main` checked out at the head diagnosed (model §2, L2), and every command is
**read-only**. A run writes two things, in two zones (model §8): the runner's events, in the host path's zone —
committed, and append-only on `main` (the sysadmin craft's `server-instances.md` property 7) — and its record,
`${DYAD_INSTANCE:-agent-corpus}/audits/<YYYY-MM-DD>-self-diagnostic.md` (model §7; its form is under Level 4), in
the agent zone. The record holds what the reading found, so it is written by the party that ran the diagnostic,
never by a step. The two land as two changes, the events first and then the record that cites their ids — the
referent before the referrer (dyad-system Rule-1) — and the last step, `record`, reads the record back against the
events. What a finding becomes is the system's own process — in a dyad system its core Rules (model §5) — never a
command here: nothing is repaired inside a run.

Two parameters, read from the environment: `K`, the units L3 reads (default 4), and `P`, the samples L4 reads
(default 3) — model §4. The rotation cursor is the newest previous record's `**Cursor:**` line; `health` prints it,
and `units`, `acts` and `pairs` start where it points and print where the next run starts.

```text
dyad/bin/dyad runbook list self-diagnostic
K=4 P=3 dyad/bin/dyad runbook run self-diagnostic health
```

**The gate** (model §3). Every step after `unit` except `record` opens with one line that reads the event store:
the latest event of each step it names must have exit 0 at the commit checked out now. Otherwise the line prints
`gate closed at <sha>: not passed at this head: <steps>` and the step exits 3 having run nothing else; the record
writes that level, and every later one, `not run (gate)`. A run asked to end after level n (`/diagnose n`) runs no
later step, and the record writes each later level `not run (last level <n>)` (model §3). Exit status throughout:
0 pass, 1 fail, 2 refused — by the runner (a role, a missing run-book or command) or by `levels.py list` (no levels
file), or by `evidence` when it cannot make its clone — 3 gate closed. The gate keys on the head, so on a head whose
earlier levels already passed a later level may be run alone. The run's own events are a change in the working tree
until they are committed, so the evidence block is never computed there: `evidence` runs it in a clean clone of the
head (below), and prints first what the checkout holds besides the event store (L4's S4 reads that line). The gate
is mechanical between coded steps only: L3's prose half — no attack landed on a sampled unit — is read, so the
L3 → L4 gate is the reading's, and the record holds it. The diagnostic reads the head of `main`: off `main` the
evidence block's plan gate judges the checked-out ref's own range rather than the system (model §2, L2), so
`health` names the branch and its pass criterion fails off `main`.

## Level 1 (unit × coded check)
`health` first: whether the diagnostic can run here at all. It prints the head and the branch, the budget, the
newest previous record's `**Diagnosed:**` and `**Cursor:**` lines (none: the first run, and every rotation starts at
its first item) and the levels file's own check (`crafts/countersign/scripts/levels.py`, model §6 — a script, not a
guard, so this step and the `list` calls below are the only places it runs, never a push); its pass criterion, the
postcondition, is that `main` is checked out and the levels file exists and passes that check, so a run off `main`,
or a file that is absent, classifies too little or names what is gone, is red before any test runs. It is named
`health` because a run-book under `<host>/runbooks/` carries a health command whose postcondition is its pass
criterion (dyad-system Rule-19 property 1; the core's live run-book test asserts it of every instance run-book). A
record already carrying today's date is named: the record's path is one per day, so this run reads its cursor and
then rewrites it (model §7):
```dyad-cmd
name: health
class: read-only
role: any
undo: none
postcondition: [ "$(git symbolic-ref -q --short HEAD)" = main ] && dyad/bin/dyad-python crafts/countersign/scripts/levels.py list unit >/dev/null 2>&1
scope: HEAD and its branch, <host>/self-diagnostic-levels.txt and <instance>/audits/ (read)

I="${DYAD_INSTANCE:-agent-corpus}"; R="$(ls -1 "$I"/audits/*-self-diagnostic.md 2>/dev/null | tail -n 1)"; T="$I/audits/$(date -u +%F)-self-diagnostic.md"; B="$(git symbolic-ref -q --short HEAD || echo 'a detached HEAD')"
printf 'head %s on %s · K %s · P %s · today %s\n' "$(git rev-parse --short HEAD)" "$B" "${K:-4}" "${P:-3}" "$(date -u +%F)"
[ "$B" = main ] || echo "not on main: the evidence block would judge this ref's own range, not the system (model §2, L2)"
printf 'last record: %s\n' "${R:-none: the first run, every rotation starts at its first item}"; [ -z "$R" ] || grep -h '^\*\*Diagnosed:\*\*\|^\*\*Cursor:\*\*' "$R"
[ ! -f "$T" ] || echo "a record already carries today's date: $T"
dyad/bin/dyad-python crafts/countersign/scripts/levels.py
```

`unit` runs every module the levels file classifies `unit`, one at a time through the runner's one-target path
(`dyad check --tests <path>`, the same child the full suite spawns, dyad-system Rule-12 property 2; a file path is a
target `unittest` accepts from the git root). `levels.py list` refuses (exit 1) a levels file that fails its check,
or any run while one of the script's own invariants is false, and (exit 2) an absent file, so an unclassified module
never drops silently out of both coded levels. The step runs every module rather than stopping at the first failure,
so the record names each, and ends on one summary line:
```dyad-cmd
name: unit
class: read-only
role: any
undo: none
postcondition: none
scope: the test modules classified unit (read; a test writes only its own temporary directories)

L="$(dyad/bin/dyad-python crafts/countersign/scripts/levels.py list unit)" || exit
n=0; f=0; bad=""; for m in $L; do n=$((n+1)); dyad/bin/dyad check --tests "$m" || { f=$((f+1)); bad="$bad $m"; }; done
printf 'L1 unit: %s modules, %s failed%s\n' "$n" "$f" "${bad:+:$bad}"; [ "$f" -eq 0 ]
```

## Level 2 (system × coded check)
`integration` runs every module classified `integration` — the ones that build a scratch repo, run git, install or
spawn the runner (model §6) — exactly as `unit` runs its own, behind the gate on `unit`:
```dyad-cmd
name: integration
class: read-only
role: any
undo: none
postcondition: none
scope: the test modules classified integration (read; scratch repos and installs live in their own temporary directories)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit || exit
L="$(dyad/bin/dyad-python crafts/countersign/scripts/levels.py list integration)" || exit
n=0; f=0; bad=""; for m in $L; do n=$((n+1)); dyad/bin/dyad check --tests "$m" || { f=$((f+1)); bad="$bad $m"; }; done
printf 'L2 integration: %s modules, %s failed%s\n' "$n" "$f" "${bad:+:$bad}"; [ "$f" -eq 0 ]
```

`evidence` is the kernel-only path's evidence block on this head (dyad-system Rule-14 property 3): the invariant
pass, every check — the whole suite, observed and never read from a suite memo — every guard on the live tree, the
coded checks of prose among them (Rule blocks, vocabulary, references, provenance counts, zones, the manifest), the
transaction guards, and the sha256 of those lines. It runs in a clean clone of the head, made in its own temporary
directory and removed on exit: the same commit, the same branch name, `origin/main` set to the checkout's, nothing
uncommitted. So the block reads `dirty=no` and the event store as committed, never this run's own events, and a
clean re-run of `dyad check --evidence` on the same head, on `main`, prints the same block (D4, D21). Its last line,
`evidence-sha256=…`, is the level's evidence: it lands in the step's event (`output_tail`), the record copies it
into its `**Diagnosed:**` line, and anyone may re-run the block on the same head and compare. What the checkout holds
besides the event store is printed first — S4's coded half, at L4. The step's exit status is the evidence run's, or
2 when the clone cannot be made:
```dyad-cmd
name: evidence
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read); a clean clone of HEAD in its own temporary directory, removed on exit

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration || exit
D="$(git status --porcelain | grep -Ev 'runbooks/events/(self-diagnostic\.jsonl)?$' || true)"; printf 'changed besides the event store: %s\n' "${D:-none}"
H="$(git rev-parse HEAD)"; B="$(git symbolic-ref -q --short HEAD || true)"; O="$(git rev-parse -q --verify origin/main || true)"; T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
git clone -q --shared --no-checkout . "$T/r" || exit 2
if [ -n "$B" ]; then git -C "$T/r" checkout -q -B "$B" "$H"; else git -C "$T/r" checkout -q --detach "$H"; fi || exit 2
if [ -n "$O" ]; then git -C "$T/r" update-ref refs/remotes/origin/main "$O"; else git -C "$T/r" update-ref -d refs/remotes/origin/main; fi || exit 2
printf 'evidence in a clean clone at %s on %s, origin/main %s\n' "${H:0:7}" "${B:-a detached HEAD}" "$(printf '%.7s' "${O:-absent}")"
(cd "$T/r" && dyad/bin/dyad check --evidence)
```

## Level 3 (unit × prose claim)
`invariants` is L3's coded half: the runner's invariant pass, one `[invariant]` line per module — the runner's own
function, `cmd_invariants` in `dyad/scripts/package.py`, which `dyad check`, `--guards` and `--evidence` each run
before any check (L2's block already holds the same lines, and a false invariant has already turned it red, D2).
Called alone it runs no guard and no test, so re-reading the lines costs under a second and puts them in this
level's own event. It exits 1 on any `FAIL [invariant]` line — the pass's own exit status — or when no invariant
line is printed at all:
```dyad-cmd
name: invariants
class: read-only
role: any
undo: none
postcondition: none
scope: repo (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration evidence || exit
O="$(dyad/bin/dyad-python -c 'import sys;sys.path.insert(0,"dyad/scripts");import package;sys.exit(package.cmd_invariants())' 2>&1)"; rc=$?; printf '%s\n' "$O"
printf 'invariant pass: %s ok, %s FAIL\n' "$(printf '%s\n' "$O" | grep -c '^ok   \[invariant\]')" "$(printf '%s\n' "$O" | grep -c '^FAIL \[invariant\]')"
[ "$rc" -eq 0 ] && printf '%s\n' "$O" | grep -q '^ok   \[invariant\]'
```

`units` names the K units the prose half reads: a unit is a tracked module declaring an `INVARIANTS` list
(templates and test modules aside), in sorted path order, starting at the first at or after the cursor's `units=`
and wrapping at the end (model §4). Each is printed with its docstring's first line and the test modules found by
its name; its contract is that docstring and the rule that owns it. For each, the reading holds the claim *"this
unit's invariants and tests cover its stated contract"* against the attack *"name a contract clause whose breaking
no invariant and no test would catch"*; a landed attack is a finding, the uncovered clause and the invariant or test
that would cover it, and it stops the run before L4 (model §3). The last line is the next run's `units=`:
```dyad-cmd
name: units
class: read-only
role: any
undo: none
postcondition: none
scope: the tracked modules and test modules, <instance>/audits/ (read)

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration evidence invariants || exit
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
The fixed claims, each with its attack and its coded half where it has one (model §2, L4) — the interaction
model's eight imperatives, then three of the system's own: S1 only a human countersigns (I1); S2 one question per
reply, its last line (I2); S3 falsified before proposed (I3); S4 detect, don't dispose (I4); S5 the ledger and the
provenance agree (I5); S6 no act is self-initiated (I6); S7 every act carries its mode and a countersignature
reference (I7); S8 silence is not consent (I8); S9 the host record matches the host; S10 the Rules are coherent; S11
the frame loads. Then the instance's own claims (below). Each landed attack is a finding (model §5). Three steps print
what the reading needs, behind the gate on L3's coded half; the L3 → L4 gate's prose half is the reading's (the
gate, above): after a landed L3 attack these steps are not run. S2, S4 and S11 are read by no step, over the
session running the diagnostic (below).

`acts` serves S1, S3 and S5–S8. It runs this craft's projector without writing its document — `collect`, `check`
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

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration evidence invariants || exit
dyad/bin/dyad-python -c 'import sys;sys.path[:0]=["dyad/scripts","crafts/countersign/projectors"];import dyadlib,project_countersign as pc;d=pc.collect(dyadlib.repo_root(),dyadlib.PKG);p=pc.check(d);[print("FAIL [project] countersign:",x) for x in p];print(("ok  " if not p else "FAIL")+" [project] countersign: "+pc.counts(d));print(pc.interaction_line(pc.interaction(d)));sys.exit(1 if p else 0)'; rc=$?
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

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration evidence invariants || exit
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

dyad/bin/dyad-python -c 'import subprocess,sys;sys.path.insert(0,"dyad/scripts");import runbook as r;h=subprocess.check_output(["git","rev-parse","--short","HEAD"],text=True).strip();ev={e["name"]:e for e in r.read_events(r.events_path(r.dyadlib.repo_root(),"self-diagnostic"))};bad=[n for n in sys.argv[1:] if not(n in ev and ev[n]["exit"]==0 and ev[n]["commit"]==h)];print("gate "+("open" if not bad else "closed")+" at "+h+("" if not bad else ": not passed at this head: "+" ".join(bad)));sys.exit(3 if bad else 0)' unit integration evidence invariants || exit
H="$(dyad/bin/dyad-python -c 'import sys;sys.path.insert(0,"dyad/scripts");import dyadlib;print(dyadlib.host_path(dyadlib.repo_root()))')"
printf 'observed: %s · %s · python %s · %s · %s\n' "$(uname -sr)" "$(git --version)" "$(dyad/bin/dyad-python -c 'import sys;print("%d.%d.%d" % sys.version_info[:3])')" "$(dyad/bin/dyad-python -c 'import pydantic;print("pydantic", pydantic.VERSION)' 2>/dev/null || echo 'pydantic not importable')" "$(timeout 10 claude --version 2>/dev/null || echo 'claude not on PATH')"
grep -H '| kernel |' dyad/infrastructure/INFRASTRUCTURE.md "$H/INFRASTRUCTURE.md" 2>/dev/null | cut -c1-200
grep -HE '^\| (Claude Code|Git|Python|pydantic) \|' "$H"/*.md 2>/dev/null | grep -v '| kernel |' | cut -c1-200 || echo "no kernel lines in $H/*.md beyond the manifest's"
```

S2, S4 and S11 are read whole and by no step, over the one conversation a run can see, the session running the
diagnostic (model §2, L4; D23): S2 finds a reply of that session asking more than one question, or one anywhere but
its last line, or does not; S4 finds a finding of this run repaired rather than proposed, or a change to the tree
since the head diagnosed besides the run's two writes — `evidence`'s first line is its coded half — or does not; S11
finds the frame's sentinel in that session's start report, or does not. No step prints the sentinel, since a step's
output lands in the committed event store and the frame's sentinel is never cached anywhere.

### Instance claims
A system adds its own L4 claims here, in the model's three columns, by its own unit of work; each is read whole or
over the same P samples, and its coded half, where it has one, has already run in L2 (model §2: countersign-system
adds its hand-over criteria H1–H5, each *"its status is as recorded"* against *"find an H whose stated status the
corpus contradicts"*). A system with none keeps the row below as its placeholder, and its record says so:

| # | claim | attack | coded half |
|---|-------|--------|------------|
| <id> | <the claim, as the system states it> | <what would have to be found for it to be false> | <the check that decides part of it, or none> |

### The record
Written once per run by the party that ran it, after the last step it reached, in this form — the bold lines are the
seams the next run's `health` and this run's `record` step read; a level the gate stopped keeps its heading and says
`not run (gate)`, a level after the one a run was asked to end at says `not run (last level <n>)`; a run that did
not reach L3 or L4 carries the previous `**Cursor:**` values forward (`none` on a first run). A second run on one
day rewrites that day's record (model §7):

    # Self-diagnostic <YYYY-MM-DD>
    **Diagnosed:** head <short sha> · K <k> · P <p> · evidence-sha256 <the evidence step's value, or not run>

    ## Level 1 — unit × coded check
    **Result:** pass | fail | not run (gate) | not run (last level <n>)
    Evidence: the `unit` summary line, its event id. Findings: each failing module, or none.

    ## Level 2 — system × coded check
    **Result:** pass | fail | not run (gate) | not run (last level <n>)
    Evidence: the `integration` summary line; the `evidence` step's `evidence-sha256=` line, its event id.
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
event of each step there (`pass`, `fail`, `gate` or `absent`) and the `evidence` step's `evidence-sha256` — so a
commit made since the run (the plan file's, the record's own) moves nothing it reads. It fails when that head does
not resolve, when the record's evidence sha is not the events', when a level's result is one the events rule out —
a step that failed recorded as anything but `fail`, a gated step recorded as anything but `not run (gate)`, a coded
level recorded `pass` that its events do not show, a level whose steps all left no event recorded as anything but
`not run (last level <n>)` for the level before it, a level only partly run — when a level after a `fail` or a
`not run (gate)` is anything but `not run (gate)`, or one after a `not run (last level <n>)` anything but the same,
or when the cursor lacks `units=`, `rows=` or `pairs=`. L1 always runs, so an L1 with no event fails. What it cannot
check is the reading itself, L3's and L4's tables, which stay inference (model, Inference, stated):
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
d = re.search(r"^\*\*Diagnosed:\*\*.*?head ([0-9a-f]{7,40})\b.*?evidence-sha256 (.+?)\s*$", text, re.M)
if not d:
    print(f"FAIL [record] {rec}: no **Diagnosed:** line naming a head and an evidence-sha256"); sys.exit(1)
h = d.group(1)
if subprocess.run(["git", "rev-parse", "--verify", "-q", f"{h}^{{commit}}"], capture_output=True).returncode:
    fails.append(f"**Diagnosed:** names head {h}, which this repository does not hold")
at = lambda c: bool(c) and (c.startswith(h) or h.startswith(c))
ev = {e["name"]: e for e in r.read_events(r.events_path(r.dyadlib.repo_root(), "self-diagnostic")) if at(e.get("commit", ""))}
st = lambda n: "absent" if n not in ev else {0: "pass", 3: "gate"}.get(ev[n]["exit"], "fail")
for n in ("health", "unit", "integration", "evidence", "invariants", "units", "acts", "pairs", "host"):
    print(f"event {n}: {st(n)}" + (f" ({ev[n]['id']})" if n in ev else ""))
m = re.search(r"evidence-sha256=(\w+)", ev["evidence"]["output_tail"]) if "evidence" in ev else None
sha = m.group(1) if m else "not run"
print(f"record {rec}: head {h} · evidence-sha256 {sha} in its events")
if d.group(2) != sha:
    fails.append(f"**Diagnosed:** evidence-sha256 {d.group(2)}, the events at {h} {sha}")
got, lv = {}, None
for line in text.splitlines():
    lv = int(mm.group(1)) if (mm := re.match(r"## Level (\d)", line)) else lv
    if lv and (mm := re.match(r"\*\*Result:\*\*\s*(pass|fail|not run \((?:gate|last level \d)\))", line)):
        got.setdefault(lv, mm.group(1))
LEVELS = {1: ("unit",), 2: ("integration", "evidence"), 3: ("invariants", "units"), 4: ("acts", "pairs", "host")}
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
