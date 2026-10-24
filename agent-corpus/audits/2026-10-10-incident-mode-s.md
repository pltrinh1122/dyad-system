# Incident mode S — a form typed from memory, not seeded from its governing definition

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`. d-work #259, 2026-10-10, 4 rows.*

## Definition
A corpus artifact whose shape a guard owns — a file name's pattern, a table's header, a table's cell
count, a required line — is written by recalling the shape rather than by reading the definition
that governs it, and is caught only afterwards by the check that owns it.

**What would have to change.** The artifact's shape would have to be emitted from the definition
that governs it, at the moment of writing, so the wrong shape is never typed — rather than checked
after the fact by the one definition nobody read.

Boundaries against the neighbours it is most easily confused with:
- **C, a value stated from memory or a digest instead of read from its source** — the sharpest
  boundary, and the separating test is value against structure: C writes down the wrong *content*
  (a sha, a state, a count, a claim); S writes down the right content in the wrong *shape*. In all
  four S rows the substance was correct and the container was wrong. C holds rows 3, 4, 8, 27, 28,
  29, 63, 71, 92, 113, 114, 130 and 131.
- **G, a flag taken as a positional argument** — G's typing was correct and the reader misread it;
  S's typing was wrong against a reader that read it correctly. Separating test: would the
  documented form have worked as typed? For G yes, for S no.
- **H, the present enumeration pinned as an invariant** — H freezes a form's current membership
  inside a check; S breaks a form while writing one instance of it. Separating test: is the wrong
  artifact a check or a record? For S it is always a record.
- **Q, an obligation no mechanism reads** — Q's obligation has no check anywhere; S's form has a
  check and it fired every time. Separating test: did anything go red? For all four S rows it did,
  and that is precisely what makes them detected rather than prevented.

## Incidents (4)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-22 | #116–#125 | the nine per-mode records were first written as `2026-09-22-incident-mode-A.md` through `-I.md`, and all nine failed `syseng/naming`, which requires a lower-case slug | the file name was fixed in each child's plan before the guard's pattern was read, and the uppercase mode letter was carried from the audit into a path |
| 2026-10-05 | #220 | the first push of the falsification record was refused: `agent/records` failed for a missing `Disposition:` line, and one test failed with it | the record was written from the table form and closed with a `## Disposition` heading instead of the `Disposition: see ledger #N` line Rule-9 Form and the guard require |
| 2026-10-06 | #226 | the first push of the falsification record was refused: the records guard reported no attack table and one core test failed with it, over one header cell | the table was written with the header `Claim` because that is what its cells hold, without reading `records.py` `FIELDS` or the existing records' header first |
| 2026-10-10 | #261 | an incident row was first appended with six cells, the five of this table plus an `agent` actor cell that belongs to the change log, and the parser refused it | two adjacent corpus tables of different width written in the same stretch of work, and nothing seeds a row of either, so a row is typed from memory of the neighbouring file |

## Pattern
Every row is a *first write* of an artifact whose governing definition was readable, in the tree, at
the moment of writing, and was not read. The rows name the source each time: row 48's cause says the
name "was fixed in each child's plan before the guard's pattern was read"; row 109's says the header
was chosen "without reading `records.py` `FIELDS` or the existing records' header"; row 140's says
"nothing seeds a row of either — a row is typed from memory of the neighbouring file".

Row 109 states the family explicitly: "The same failure family as the first-push refusals already in
this log (#199, #220, #223, #227): the form was readable and was not read." Row 140 states the
mitigation gap in the play-book's own vocabulary: "The fence here is a script the suite runs rather
than a template that would make the shape unwritable, which is the difference between a defect
detected and a defect prevented."

All four were caught by the owning check, before `main`, and the cost each time was a rewrite: nine
renames plus every in-file and index reference (row 48), one extra commit (row 89), one amended
commit and one refused push (row 109), one rewrite each of two rows within two turns (row 140). No
row of this mode reached `main`.

Recurrence evidence, mitigation by mitigation:
- `syseng/naming`'s audit-name kind (M1) predates all four rows and fired on row 48. Rows 89, 109
  and 140 post-date it; none is a file name, so this is evidence about the mode's spread, not about
  the fence.
- `agent/records`'s `Disposition:` check (M2) fired on row 89. Row 109 (2026-10-06) post-dates it by
  one day, on the *other* clause of the same guard — so the guard caught the second fault too, and
  prevented neither.
- `incidents.py`'s cell-count check (M3) fired on row 140 **twice inside two turns**: row 140's own
  text says "Second occurrence inside two turns, after candidate Q of this same batch, which was
  first written with six cells for the same reason". That is the mode's strongest recurrence
  evidence and it is four hours old.
- The one shipped *seeder* in the tree, `runbook new` (M4), reaches no row of this mode.

## Mitigations (phase 2)

**M1 — the naming guard's audit-file kind (shipped, a check after the fact).**
`crafts/syseng/guards/naming_rules.txt:30`:
`kind: <instance>/audits/<YYYY-MM-DD>-<slug>.md = <instance>/audits/* =
<instance>/audits/(\d{4}-\d{2}-\d{2}-[a-z0-9-]+|INCIDENTS)\.md`.
Read by `crafts/syseng/guards/naming.py` (`ENTITY, CORPUS, TRANSACTION = "name", "craft", False`,
`:31`; `DATA` at `:35`), over every path the tree holds tracked or not — the docstring at `:4-6`
says `git ls-files -co --exclude-standard`.
Moment: `package.py check` in the runner and `dyad check --guards --pre-push`, as `syseng/naming`;
because the scan includes untracked paths, it fires before the file is even committed.
Reach: row 48 — met, and this is the check that failed nine times. Rows 89, 109, 140 — not reached:
none is a file name.
Shipped: `crafts/syseng/guards/naming_rules.txt:30`, `crafts/syseng/guards/naming.py:35`. Recurred
after it shipped: not on file names; the mode moved to table shapes.

**M2 — the records guard's two clauses (shipped, a check after the fact).**
`dyad/guards/agent/records.py:21` `FIELDS = ("#", "Attack", "Result", "Survivor")  # the attack-table
header, as the records write it`; `:22` `REQUIRED = ("attack", "result", "survivor")`; `:25`
`DISPOSITION = re.compile(r"\bDisposition:")`.
`check_record` at `:44-51` emits `no attack table (header cells attack, result, survivor)` (`:48`)
and `no \`Disposition:\` line (Rule-9 Form)` (`:50`). `INVARIANTS` at `:23-24` pins `FIELDS` as the
header, enforced at import by `dyadlib.enforce` at `:86`.
Moment: `package.py check` in the runner and `dyad check --guards --pre-push`, as `agent/records`
(`TRANSACTION = False` at `:19`, so the package check only, never a transaction mode).
Reach: row 89 — met, by the `Disposition:` clause. Row 109 — met, by the attack-table clause, one
day later. Rows 48, 140 — not reached.
Shipped: `dyad/guards/agent/records.py:21`, `:25`, `:48`, `:50`. Recurred after it shipped: yes —
row 109 one day after row 89, on the same guard's other clause.

**M3 — the incident parser's shape check (shipped, a check after the fact).**
`dyad/scripts/incidents.py:31` `FIELDS = ("date", "d-work", "what", "cause", "consequence")  # the
header of the log's table, as Rule-3 Incidents names it`; `INVARIANTS` at `:34-40` pin it
(`fields-are-the-log-header`, `:38`) and are enforced at import at `:132`.
`check_log` at `:88-110`: the header must be `FIELDS` (`:91-92`), then per row `if r["cells"] !=
len(FIELDS): msgs.append(f"{where}: {r['cells']} cells, not {len(FIELDS)}")` at `:98-99`, plus date
parse (`:100-101`), at least one `#<id>` (`:102-103`), and no empty `what`/`cause`/`consequence`
(`:104-106`).
Moment: Rule-12's suite, through `dyad/tests/test_incidents.py:54-58` `LiveTests.test_live_log_passes`
— so `package.py check` in the runner and `dyad check --guards --pre-push` whenever the suite is not
skipped. It is deliberately *not* a registry guard: the module docstring at `:14-20` says so, and
`INVARIANTS` has `("not-a-guard", lambda: "ENTITY" not in globals())` at `:39`, because a new
registry entry falsifies a released craft's pinned tests and row #170 carries that gap.
Reach: row 140 — met, twice. Rows 48, 89, 109 — not reached.
Shipped: `dyad/scripts/incidents.py:99`, `dyad/tests/test_incidents.py:55`. Recurred after it
shipped: yes — twice within two turns, which is row 140 itself.
Noted as a gap in this mitigation's own reach: the suite can be skipped at the push gate by the
suite memo and by the installed-root skip (Rule-12 property 2), and skipped outright for a
ledger-only range (`dyad/scripts/package.py:358-360`). `INCIDENTS.md` lives under
`<instance>/audits/`, not `<instance>/d-work/`, so a range touching it is never ledger-only — the
skip does not reach this check — but a push whose range touches only the ledger and whose tree is
unchanged will not re-run it. That is correct and is stated rather than counted as a hole.

**M4 — the one shipped seeder in the tree (shipped, and it reaches no row of this mode).**
`dyad/scripts/runbook.py:326-343`: `template()` finds the first `crafts/*/templates/runbook.md`
(`:328-330`) and `new()` copies it to `<runbooks>/<instance>.md`, refusing to overwrite (`:337-341`),
`shutil.copyfile(t, dst)` at `:342`. Rule-19 property 1 names it: `dyad runbook new <instance>`
seeds it from the craft's template.
Moment: when the Agent or Operator runs `dyad runbook new`, at the moment of creation.
Reach: none of the four rows. Cited because it is the only command in the tree that emits a governed
form at write time, and so is the shape the candidate generalises.
Shipped: `dyad/scripts/runbook.py:332`.

**M5 — install-time templates (shipped; they seed files, never rows).**
`dyad/scripts/package.py:115` `TEMPLATES` maps `INCIDENTS.md` to `<instance>/audits/INCIDENTS.md`,
and `dyad/templates/INCIDENTS.md` carries the correct five-cell header
(`| date | d-work | what | cause | consequence |`). `crafts/sysadmin/templates/CHANGELOG.md` is the
change log's, named in `crafts/sysadmin/guards/changelog.py:5`.
Moment: `dyad install`, once per install, never again.
Reach: none of the four rows. All four are writes *into* an artifact that already existed; a file
seeder cannot reach them.
Shipped: `dyad/scripts/package.py:115`, `dyad/templates/INCIDENTS.md`.

**Finding — one template is tied to its definition and the other is not.**
`crafts/sysadmin/guards/changelog.py:127-129` checks the craft's own template against `FIELDS`:
`if tmpl.exists() and tuple(dyadlib.table_header(tmpl.read_text())) != FIELDS: msgs.append(
f"templates/CHANGELOG.md: header is not {list(FIELDS)}")` — and `OPTIONAL` at `:39-40` says the
template "is always FIELDS exactly — never truncated".
`dyad/templates/INCIDENTS.md` has no equivalent: nothing compares its header to
`incidents.FIELDS`. Grepped today — `templates/INCIDENTS` appears only at
`dyad/scripts/package.py:115`, as a seed destination. So the one template that seeds the five-cell
log the mode's newest row broke can drift from the definition that refused that row. Not an incident
yet; a live gap, and directly load-bearing on the candidate below (attack 1).

**Direct answer to the question put to this mode: for each of the four rows, does anything seed the
right shape, or is every fence a check after the fact?**
- Row 48, the audit file name — nothing seeds it. There is no `dyad audit new`; `dyad`'s verbs are
  `check`, `build`, `install`, `craft`, `bundle`, `runbook`, `session`, `ledger`, `dwork`, `project`
  (`dyad/scripts/package.py:1047-1074`). Check after the fact: `syseng/naming`.
- Row 89 and row 109, the falsification record — nothing seeds it. `dyad/guards/agent/records.py`
  has `check_package`, `summary`, `describe` and `main`, and no `new`. Check after the fact:
  `agent/records`.
- Row 140, the incident row — nothing seeds a row. `dyad/scripts/incidents.py` is a parser and a
  check only (`parse`, `check_log`, `check`, `summary`, `main`); it has no writer. Check after the
  fact: `check_log` through Rule-12's suite.
Every fence of this mode is a check after the fact. The only seeder in the system
(`runbook new`) governs a form none of these four rows touches.

## Remediation candidate, under attack
One fence: a `new` verb per governed artifact, emitting the shape from the definition rather than
from a template file — `dyad record new <slug>` writing the title, the `**Claim**` line, an attack
table headed from `records.FIELDS` and the `Disposition: see ledger #N` line; `dyad incident new`
appending a row with exactly `len(incidents.FIELDS)` cells, prompting for each by name; and in both
cases the file name allocated from the `kind:` regex `crafts/syseng/guards/naming_rules.txt` holds
for that kind, so the name is derived and not typed. The exact moment: at creation, in the command
that writes, before the artifact exists in any shape — not at a push gate.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Easy agreement (Rule-9 Conditions): "seed every corpus file from a template" is the obvious fix, so attack it. A template file is a second copy of the form, and this mode *is* a form copied by hand — so a template relocates the mode rather than closing it. Evidence in the tree today: `crafts/sysadmin/guards/changelog.py:128` exists precisely because the template can drift, and `dyad/templates/INCIDENTS.md` has no such check, so the one template seeding the log row 140 broke is itself unchecked against `incidents.FIELDS`. | confirmed | "Seed from a template" does not survive. "Emit from the definition" does — the header built from `FIELDS` at write time, the file name built from the `kind:` regex — and any template that remains must carry a check tying it to its `FIELDS`, which `dyad/templates/INCIDENTS.md` lacks today and should gain whatever else is decided. |
| 2 | Coverage: rows 89 and 109 are not a new file but an *edit* of a record already being written — the attack table and the `Disposition:` line went into a file that existed. A creation-time seeder reaches neither. | confirmed for a file seeder, survives scoped for a stanza seeder | A `new` verb that emits only the empty file does not survive. One that emits the whole skeleton — title, claim, headed table, `Disposition:` line — reaches rows 89 and 109, because both faults are in parts the skeleton would have carried. Row 140 needs a *row* emitter, not a file emitter. So the candidate is "emit the stanza", and must be stated as that. |
| 3 | The checks caught all four rows before `main`, so prevention buys nothing but convenience, and it buys it at package cost: Rule-12 property 1 (each new module carries its mechanical check), `crafts/syseng/guards/tests.py`'s mapping (a new `dyad/scripts/` module needs `dyad/tests/test_<n>.py`), and `naming.py`'s `symbol:` lines. | survives, scoped | Correctness is not what is bought. What is bought is the rewrite cost the rows record — nine renames with every in-file and index reference (row 48), one refused push and one amended commit (row 109), two rewrites in two turns (row 140) — and the fact that a check which fires twice within two turns is not deterring the fault. Admissible on Rule-13 property 1: writing a governed form is a recurring task done by inference, and recurrence proposes code. Scoped to the `runbook new` shape, one verb per artifact, never a new subsystem. |
| 4 | The candidate adds CLI verbs, and incident mode G is a flag taken as a positional argument on exactly this surface — four subcommand forms in four d-works. A `dyad record new --help` would, on the code read today, be handled by whatever dispatch the new verb gets, and `dyad check --help` still runs a 120 s suite (`dyad/scripts/package.py:1062-1074`). The fix for one mode is new surface for another. | confirmed | The candidate does not survive as a standalone. It must land after, or with, mode G's dispatch refusal, and its own argument reading must go through the one table rather than a fifth positional reader. Stated as an ordering constraint on the backlog row, not as a reason not to build it. |
| 5 | `incidents.py` is deliberately a script and not a guard (`dyad/scripts/incidents.py:14-20`, `INVARIANTS` `("not-a-guard", …)` at `:39`) because a new registry entry falsifies a released craft's pinned tests, which row #170 carries. An `incident new` writer in the same module inherits that constraint, and a writer that cannot be registered cannot be reached by the registry's own contract checks. | survives, scoped | Only as a writer inside the existing script, invoked through the entrypoint and tested by `dyad/tests/test_incidents.py` — no `ENTITY`, no registry entry, so `("not-a-guard", …)` still holds and row #170 is not blocked on. The candidate must not move `incidents.py` under `dyad/guards/`; that move is row #170's, not this mode's. |
| 6 | Row 48 is a file name, and a name allocator must know *which* kind a new path belongs to — a mapping from artifact to `kind:` pattern that the guard's data does not expose as a forward index (it exposes glob-to-regex, for checking). Building the reverse index is new data, and new data of the enumerating sort is incident mode H. | survives, scoped | Narrowly: the verb knows its own kind because the verb is per-artifact, so it names one `kind:` pattern by key and no index is built. The residual is that a verb and its pattern can drift, which is answered by a check that each `new` verb's emitted shape passes the guard that owns it — one test per verb, asserting the emitted artifact passes `check_package` cleanly. |

Read together: "emit the stanza from the definition" survives, "seed from a template" does not, the
candidate's claim on correctness does not survive, and the candidate is ordered behind mode G's
dispatch fence.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build.** Proposed, not taken; the Operator disposes.

What the row would say: *emit each governed form from its definition at write time — `dyad record
new <slug>` writing the full skeleton (title, `**Claim**`, an attack table headed from
`records.FIELDS`, a `Disposition: see ledger #N` line) with the file name derived from the `kind:`
pattern in `crafts/syseng/guards/naming_rules.txt`, and an incident-row writer inside
`dyad/scripts/incidents.py` appending exactly `len(incidents.FIELDS)` named cells and staying a
script, not a guard (row #170). One test per verb asserting the emitted artifact passes the guard
that owns it. Ordered after mode G's dispatch refusal, and separately: tie
`dyad/templates/INCIDENTS.md`'s header to `incidents.FIELDS` the way
`crafts/sysadmin/guards/changelog.py:128` ties the change log's. refs: 116, 220, 226, 261, 170.*

Which rows it would have caught: row 89 and row 109 (both faults live in the skeleton the record
verb would emit), row 140 (the row writer), and row 48 (the name derived from the `kind:` pattern
rather than carried from the audit's uppercase letter) — all four.

The mode is not fenced today, by the play-book's own definition of the word: every one of its four
fences is a check after the fact, each fired, and the most recent row (140, 2026-10-10) is this
exercise's own day and records the same fault twice within two turns. Row 140's consequence cell
states the gap in the play-book's terms and is the reason this mode's exit is a row rather than a
closure.

## Delta 2026-10-24 (#259 revision 5; 4 → 6 rows)
**Rows added:** 164 (#297: a date typed into `-d` text the CLI dates itself), 211 (`-r "a b"` as one
token, against a usage line that says one id per flag). **Mitigations re-read:** `cmd_dwork` refuses `;`
and a line break in `-d` and not a leading date; `touch` validates no `-r` token. Both are write-time
refusals one line each. **Exit:** exit 2 as proposed (#280 `backlog`).
