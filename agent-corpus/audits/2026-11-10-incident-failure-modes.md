# Incident audit by failure mode — 2026-11-10 (delta 253–306)

*Audit of `agent-corpus/audits/INCIDENTS.md` on branch `651-incidents` (base `main` `8c9fab79`), with the 16 rows this
d-work logs from the home's board. d-work #651 (Mutation 2), unit audit-90a13c0e. Play-book
`dyad/playbooks/incident-hardening.md`, phases 0, 1, 2 and 4; phase 3 (execute) is each child's own row. Detects and
proposes; disposes nothing and opens no row (audit charter, `preferences-corpus/MANDATES.md`): the home creates the
children listed below with `dwork new … --mandate 651`. A delta on the 2026-11-04 index
(`2026-11-04-incident-failure-modes.md`), whose 51 modes and their records stay as they are, never renumbered.*

**Ledger:** `agent-corpus/audits/INCIDENTS.md` · **covered through:** 306 rows, latest 2026-11-09

## Phase 0 — survey
`LEDGER=agent-corpus/audits/INCIDENTS.md dyad runbook run incident-hardening survey`, event
`incident-hardening-20261110T004105Z-survey` (landed on `main` at `8c9fab79`, events-only): live 290 rows, latest
2026-11-07, against the watermark 252 (latest 2026-11-03); verdict `delta`. This d-work then adds rows 291–306 (the
board's promised incidents not yet logged), so the delta is rows **253–306, 54 rows**. One row's mechanism (257) is
named by no existing mode, so a new mode, 52, is derived for it (the play-book's second trigger, scoped to that row);
the rest is grouped against the 51 modes, re-derived from each row's cells, never read off the cells' own
`Failure mode` notes.

## Phase 1 — group
Each row was read cause first and given one mode by `dmc:failure-mode-primary` (the mechanism that started the
incident). The rows' own `Failure mode NN` notes, written by counsel and the home on rows 261–290, were compared
afterwards: 29 of 30 agree (rows 291–306 carry this audit's own notes, so they are not a comparison). **Row 263** is noted mode 29 (presence identity), but its mechanism is the automaton's
planned flip writing a board entry over a newer one, the mechanism of rows 268 and 279: re-derived as mode 07. Rows
253–260, which carry no note, were classed here. Mechanical check: every row of 253–306 in exactly one mode, counts
summing to 54.

| mode | observed failure mode | delta rows | rows | exit | fence row | fence | proposed child |
|------|-----------------------|-----------|------|------|-----------|-------|----------------|
| 01 | a test asserts or reads live repo or instance state that a legitimate change or the clock falsifies | 3 | 269, 291, 305 | 2 | #595 | — | none: #595 (R-g) |
| 02 | cross-zone coupled state whose guards admit no one-zone PR order | 3 | 262, 272, 278 | 2 | #595 | — | none: #595 (R-h) |
| 05 | a figure or rule clause stated from memory or a digest, not re-read from its source | 4 | 258, 267, 274, 299 | 3 | — | — | none (Rule-9, Rule-10: inference only) |
| 06 | a claim about a mechanism accepted on a proxy without positive observation | 3 | 253, 273, 293 | 2 | #595 | — | none: #595 (R-g) |
| 07 | a stale view of shared state written over the live one | 3 | 263, 268, 279 | 2 | — | — | K-07 |
| 12 | an act (ask, relay, dispatch) taken before the record or check that must precede it | 4 | 255, 261, 294, 302 | 2 | — | — | K-12 |
| 16 | a PR held for its done-`Y` conflicts on a file concurrent writes change | 1 | 295 | 2 | — | — | K-16 |
| 17 | a plan's closure or a question written without checking what authorizes each step | 2 | 254, 259 | 1 | — | `dyad/scripts/package.py:cmd_plan` | none |
| 18 | a plan's files or surfaces listed from the deliverables, not derived from the mutation | 2 | 271, 285 | 2 | — | — | K-18 |
| 19 | a corpus artifact written in a guarded form from memory; the guard runs only later | 2 | 266, 281 | 2 | — | — | K-19 |
| 21 | success read before, or other than, the command's own exit and the remote state | 5 | 264, 277, 297, 298, 301 | 2 | — | — | K-21 |
| 22 | an ad hoc shell step or a CLI form typed from memory | 2 | 275, 289 | 3 | — | — | none (Rule-14 p3; a harness hook is operator-side) |
| 27 | a checker judges a proxy of its object | 4 | 270, 283, 284, 286 | 2 | — | — | K-27 |
| 28 | a check passes or reports confidently over empty or absent input | 3 | 265, 276, 287 | 2 | — | — | K-28 |
| 33 | an environment property the step relies on differs from the authoring host | 1 | 282 | 3 | — | — | none (Rule-14 p4: the next unknown property) |
| 35 | concurrent processes on one host contend for CPU, so a wall-clock ceiling fails | 2 | 288, 306 | 2 | — | — | K-35 |
| 37 | a new form or writer added without enumerating the other paths to the same state | 3 | 280, 290, 303 | 2 | — | — | K-37 |
| 40 | the practice requires an act the CLI or store has no form for | 5 | 256, 260, 292, 296, 304 | 2 | — | — | K-40 |
| 46 | coordination carried on a channel the acting session does not read before acting | 1 | 300 | 3 | — | — | none (Rule-3: the inbox is read at the start of each turn; the residue is that latency) |
| 52 | a read that changes state as a side effect | 1 | 257 | 1 | — | `dyad/guards/agent/inbox.py:read` | none |

Exit: 1 fenced, 2 a `backlog` row naming the fence (here #595, or a proposed child K-nn until the home opens it), 3
unfenceable on this kernel (`dmc:mode-exit`). The `fence row` cell of a K-nn mode stays `—` until its row exists, so
the sweep's P16 reads no row that is not there; the home rewrites it to `#<id>` with the children.

Sum: 20 modes; 3+3+4+3+3+4+1+2+2+2+5+2+4+3+1+2+3+5+1+1 = 54 rows.

## Mode records (the delta)
Each: the delta's incidents, the pattern, the live mitigations (Phase 2 inventory, read from code at `8c9fab79`), and
one candidate.

- **01.** 269 (#570/#592, 11-05: three core tests read this instance's plan files), 291 (#620, 11-07: StallTests read
  the live instance), 305 (#650, 11-09: `test_list_runs` reads presence freshness by the clock). *Shipped:* #608 skips
  the three plan-file tests where the plan is absent; `livetest.LiveCase` classes tests that read the stores
  (`dyadlib.CHECK_INPUTS` `suite:live`, #618 H4). *Recurred after shipping:* 291, 305 — `LiveCase` moves no test out
  of the gate (see 35). *Candidate:* R-g's `syseng/tests` warning on a test reading live state, carried by #595.
- **02.** 262 (#590: preference PR needed #660's keys), 272 (#609: S7 pins workflow files both ways), 278 (#570: tag
  check deadlock after the v1.0 cut). *Shipped:* #621 spares a ledger-only or events-only push the missing-tag refusal
  (Rule-14 p3), which closes 278's face. *Candidate:* R-h's one-zone order, carried by #595.
- **05.** 258, 267, 274, 299. *Shipped:* `dwork new --mandate` refuses a row past the ceiling (it caught 267);
  `dmc:plan-departure` now lists internal realization (#643, after 299). *Residue:* what the agent states in chat
  reaches no guard; exit 3 stands, naming Rule-9 and Rule-10 Enforcement.
- **06.** 253 (#575: a 30-minute window read as a refutation), 273 (#575/#609: one run read as GitHub ignoring
  `timezone`), 293 (#622: `LiveCase` read by its name as leaving the gate). *Candidate:* R-g's `records.py` warning on
  an attack confirmed or refuted that cites no observation, carried by #595.
- **07.** 263, 268, 279: the automaton's planned flip, computed from the board as it stood at the `Y plan` commit,
  lands on a newer tip and overwrites the home's later entry. *Shipped:* `automaton.board_after_plan_y` (#587 S11)
  skips the flip when the board was written after the `Y` commit, read on `base`. *Recurred after shipping:* 279
  (11-06), the race engineer diagnosed on 2026-11-05 (the read is on the run's base, the landing on a newer tip).
  *Candidate K-07:* the flip carries the board text it read and refuses at landing when the tip's `board/<id>.md`
  differs (`automaton.py`, a test replaying `52e1f6f`, `a9168dd`, `61bf885`).
- **12.** 255 (#573: relays before the record), 261 (#574: relay before owner), 294 (#622: Done asked before the
  plan's evidence block), 302 (#644: precedent question before admission). *Shipped:* the write-ahead relay fence
  (#552), `dwork batch` validating every line first (#586), `inbox post` adding an owner (#586). *Not reached:* 294,
  302 — nothing ties an asked question to the check its plan or its record requires first. *Candidate K-12:* the
  asking verbs refuse a question whose prerequisite has no recorded pass: `board advance … asked` for a Done refuses
  without an evidence sha256 on the named head, and the precedent question lists only lines `similar.admit` admits.
- **16.** 295 (#625: an engineer presence file on a held PR branch). *Shipped:* none for this face (R-f, #595, warns
  on tail-append paths at evidence, not on presence files). *Candidate K-16:* the pre-push gate refuses a PR branch
  whose range touches `<instance>/d-work/sessions/` outside a ledger-only commit, or the automaton resolves a
  presence-only conflict to the base.
- **17.** 254, 259 (both 2026-11-04). *Shipped:* Rule-3's What a `Y` binds and the carried row (#574, #585, Rule
  text); `dyad plan check` at `planned` (#592, `package.py:cmd_plan`). *No recurrence* after 2026-11-05. Exit 1.
- **18.** 271 (#609: probe file names against S7 and `syseng/naming`), 285 (#617: the automaton run-book left on the
  old design). *Shipped:* `dyad plan check` lists callers of a function the mutation names (#592). *Recurred after
  shipping:* 285 — a run-book's prose naming a renamed term is no caller. *Candidate K-18:* `plan check` warns on
  every tracked file outside the plan's list that names a term or path the mutation renames or removes.
- **19.** 266 (#611: an abbreviated head in a `Y done`), 281 (#617: a DMC outcome name dropped). *Shipped:* the push
  gate caught 281 as designed. *Not reached:* 266 reached `main` and was caught only by `merge.py` at merge.
  *Candidate K-19:* `dwork state` and `dwork batch` refuse, before any write, a `merges PR #n at <head>` whose head is
  not 40 hex.
- **21.** 264, 277, 297, 301 (the home rang a unit beside a post that was then refused: four times over 11-05 to
  11-08), 298 (#642: a push reported landed from the local commit). *Shipped:* none; the doorbell route
  (`dmc:message-route`, #584) says when to ring, not after what. *Candidate K-21:* `inbox post` prints its ring line
  only after the post's commit lands on `main`, and the home rings only on that line.
- **22.** 275, 289. *Shipped:* `inbox post --body-file`; every verb's `-h` (#592). *Residue:* exit 3 stands.
- **27.** 270 (#570: corroboration cancelled by a newer push read as failing), 283 (#617: the stores step judged a PR
  body on a sweep), 284 (#617: counts read as new findings), 286 (#618: `sweep_ci` classed with an input whose trigger
  never calls it). *Shipped:* #619's test fails a part classed with an input whose trigger never calls it (286).
  *Live defect:* `automaton.finding_key` masks shas only (`HEXWORD`), so a count that grows with the ledger is a new
  finding (284). *Candidate K-27:* `finding_key` masks counts as well as shas, with a test.
- **28.** 265 (#570: a refusal with an empty reason), 276 (#614: "NO TESTS RAN"), 287 (#564: the mirror check never
  runs). *Shipped:* #681 prints a refusal's reason (265); the gate's split runner fails a module that runs no test
  (276). *Live defect:* `automaton.sweep_drift` reads `MIRROR` and, unset, prints no line. *Candidate K-28:*
  `sweep_drift` prints one `skip` line when `MIRROR` is unset, or `dyad-sweep.yml` sets it.
- **33.** 282 (#617: a check that read only with `GITHUB_TOKEN`). Caught by the home's review. Exit 3 as in the
  2026-11-04 record's residue: the next unknown property of the environment is The World's (Rule-14 p4).
- **35.** 288 (#619: 7.74 s), 306 (#650: 5.27 s on #743). *Shipped:* #619's stall pool; #622 revision 2's `LiveCase`.
  *Live defect:* `package.py`'s suite filters nothing, so a `LiveCase` still runs in `check --evidence` and the
  pre-push gate (row 293). *Candidate K-35:* the code suite (`suite`) excludes `LiveCase` tests, which run only in
  `suite:live` (`--stores`), so no wall-clock ceiling over live stores gates code evidence.
- **37.** 280 (#616: the plans guard required a base commit of a reading-only file), 290 (#621: a release row's
  post-close steps have no board entry), 303 (#647: the Done template has no releases clause). *Shipped:* `plan check`
  lists callers (#592); none for a new form's other writers. *Candidate K-37:* `board advance`'s Done template derives
  its clauses from the row's Done question form, `releases` under the release gate included, with a test that the
  stored question equals the asked one for a release d-work.
- **40.** 256, 260 (2026-11-04: ring owed, dispatch from memory), 292, 296 (#498: a withheld provenance entry, twice),
  304 (#650: a revision asked mid-build has no recordable question). *Shipped:* #586's batch prints the units to ring;
  #587's phases and `board advance` (256, 260). *Not reached:* 292, 296, 304. *Candidate K-40:* a Rule-7 withheld
  entry: a provenance entry noted `withheld by the operator` whose fenced body holds the operator's own direction, which
  the guard counts as the disposition or prompt it stands for (counsel's text, the intake communicate suggested). 304's
  fence (an orchestration event `revision-asked`) is this mode's second candidate, recorded here and not proposed: one
  child per mode.
- **46.** 300 (#644: a relay crossed a build). Exit 3: the inbox is read at the start of each turn (Rule-3 Batch
  disposition), and a build already under way reads it next turn; the cost was one rebuild, caught before any PR.
- **52 (new).** 257 (#568, #571: `inbox read` marked messages read while the home showed only the tail). *Definition:*
  a command named as a read writes state as a side effect, so what it marks is not what was seen; bounded against 43 (a
  mutating verb run to probe a check), where the verb is known to mutate. *Shipped:* `inbox.read` lists without
  marking and marks only the messages named (observed 2026-11-10: "none marked — mark what you have read"). Exit 1.

## Phase 2 — falsification of "this mode is addressed"
Written here because `agent-corpus/falsification/` is counsel's, not audit's.

| # | claim | attack | result | survivor |
|---|---|---|---|---|
| 1 | each delta row's own `Failure mode` note is right | re-derive each from its cause cell, blind to the note | **confirmed** for 1 of 30: row 263 is 07, not 29 | the table above |
| 2 | the 51 modes cover the delta | a row whose mechanism no mode names | **confirmed** for row 257 | mode 52 |
| 3 | 07 is fenced by S11 | recurrence after `board_after_plan_y` shipped (#587, 2026-11-05) | **confirmed**: row 279 on 2026-11-06 | K-07 |
| 4 | 35 is fenced by `LiveCase` | does `package.py` drop a `LiveCase` from the code suite? | **confirmed**: it filters nothing; rows 293, 306 | K-35 |
| 5 | 21 is a conduct slip, not a mode | count recurrences after the home named the discipline (2026-11-05) | **confirmed** as a mode: three more (297, 301, and 277) after it was named | K-21 |
| 6 | 17 is fenced | recurrence after #592 and #585 | **refuted**: none since 2026-11-04 | exit 1 |
| 7 | 52 is fenced | run `dyad inbox read` with one unread message | **refuted**: it listed and marked none | exit 1 |
| 8 | 01, 02 and 06 need new children | is a fence row already open for them? | **refuted**: #595 (`backlog`) carries R-g and R-h | #595, recurrence noted |
| 9 | 05, 22, 33 and 46 are cop-outs at exit 3 | a moment a guard could read | **survives**: chat, a typed shell line, The World and a turn's latency reach no guard on this kernel | exit 3 |
| 10 | 11 children fit the ceiling | count | **survives**: 11 of 12 | the list below |

## Proposed children (for the home: `dwork new … --mandate 651`, born `backlog`, `refs: parent #651`)
Ceiling 12 (plan #651); proposed 11. Owner of each fence engineer, unless noted.

| child | mode | title | slug | its one mitigation candidate | rows |
|---|---|---|---|---|---|
| K-21 | 21 | ring a unit only after its post lands | `ring-after-land` | `inbox post` prints the ring line only once the post's commit is on `main`; the home rings only on that line | 5 |
| K-40 | 40 | a withheld provenance entry form (Rule-7) | `withheld-entry` | a provenance entry noted `withheld by the operator`, its body the operator's direction, counted by `provenance.py` as the entry it stands for (counsel's Rule-7 text) | 5 |
| K-07 | 07 | the planned flip refuses a board moved since its read | `flip-board-cas` | the flip carries the board text it read and refuses at landing when the tip's `board/<id>.md` differs | 3 |
| K-12 | 12 | an asked question waits for its prerequisite check | `ask-after-check` | `board advance … asked` for a Done refuses without an evidence sha256 on the named head; the precedent question lists only `similar.admit`'s admitted lines | 4 |
| K-27 | 27 | sweep findings masked by count as well as sha | `finding-key-counts` | `automaton.finding_key` masks counts, with a test | 4 |
| K-28 | 28 | the mirror check says when it skips | `mirror-skip-line` | `sweep_drift` prints one `skip` line when `MIRROR` is unset | 3 |
| K-35 | 35 | live tests out of the code gate | `live-out-of-gate` | the code suite excludes `LiveCase` tests, run only in `suite:live` | 2 |
| K-37 | 37 | the Done template carries the releases clause | `done-template-releases` | `board advance`'s Done template derives its clauses from the row's question form, `releases` included, with a test | 3 |
| K-18 | 18 | plan check reads prose that names a renamed term | `plan-check-terms` | `dyad plan check` warns on a tracked file outside the plan's list naming a term or path the mutation renames or removes | 2 |
| K-19 | 19 | a `Y done` head is the full sha | `full-head` | `dwork state` and `dwork batch` refuse a `merges PR #n at <head>` whose head is not 40 hex, before any write | 2 |
| K-16 | 16 | no presence file on a PR branch | `presence-off-branch` | the pre-push gate refuses a non-ledger range touching `<instance>/d-work/sessions/`, or the automaton resolves a presence-only conflict to the base | 1 |

## Phase 4 — verify
`LEDGER=agent-corpus/audits/INCIDENTS.md dyad runbook run incident-hardening verify` (`dyad check --list; dyad
automaton sweep`), on `main` at `8c9fab79`, event `incident-hardening-20261110T004330Z-verify` (landed on `main` at
`e87c388d`, events-only): exit 0, 243 s; `sweep of main 8c9fab79064f: 94 finding(s), 0 failing, 2 new`, both `inflight
W8` promises listed over three days; `checks-sha256=eef0a690…`, `report-sha256=fd3ec94d…`. The report's
`agent/merges` warning on `07d79833` (a conflicted merge differing on `sessions/engineer-1537d8fb.md`) is row 295's
merge, read back as #541 A3 designed. Every fence the table names resolves (`audits.index_fences`: none unresolved),
and the survey on this branch reads `no-op` (306 rows against this index's 306).

**Closure of the delta.**

| exit | modes | rows |
|---|---|---|
| 1 fenced | 2: 17, 52 | 3 |
| 2 backlog: #595 | 3: 01, 02, 06 | 9 |
| 2 backlog: proposed K-nn | 11: 07, 12, 16, 18, 19, 21, 27, 28, 35, 37, 40 | 34 |
| 3 unfenceable | 4: 05, 22, 33, 46 | 8 |

Sum: 20 modes; 3 + 9 + 34 + 8 = 54 rows. The 11 exit-2 modes close as `backlog` only once the home opens their
children; until then each is open in the index (`dmc:mode-exit`), named to its K-nn.

## Limits
- Nothing was run except the read-only survey and verify steps and one `dyad inbox read`. Every mitigation claim is
  read from code at `8c9fab79` and cited by path and name; none was exercised.
- Rows 291–306 were written from the home's board line (`board/_cos.md` `promised:` at `2c0069c49a1f`) and the home's
  relay, not from each incident's own session; their dates for undated entries (303–306) are those of the commits
  that put them on the board.
- The two #498 rows name no private repository and quote nothing of their source.
- The delta re-derives one mode (52) and re-classes one row (263); the 51 records of 2026-11-04 are not rewritten.
