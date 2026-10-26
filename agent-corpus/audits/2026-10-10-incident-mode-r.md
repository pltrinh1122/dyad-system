# Incident mode R — a derived key that does not identify

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259, 2026-10-10, 7 of 140 rows.*

## Definition
The mechanism: a module composes a key — an id, a name, a pattern, a branch, a cell boundary, a
text match — and uses it to identify a thing, but the key does not identify. It is not unique (one
value for many things), or not stable (a new value each call for one thing), or not the dimension
the question is about, or not able to match the form the system actually writes. The resolution
then succeeds and lands on the wrong object, or silently yields nothing, and because the code ran
clean there is no error to read. This recurs on every run, by construction, until the key is
changed.

**What would have to change.** Every key a module uses to identify a thing must be shown to
identify it — unique, stable, and matching the form the system writes — with the coverage of that
claim checked where the key is defined rather than assumed where it is used.

Boundaries against the neighbours it is most easily confused with:
- **C, a value stated from memory or a digest**, and **D, the wrong object read** — C and D are
  each other's nearest neighbours, separated by whether anything was read at the moment of use; R
  is the code's own version of the same family. In C and D a party composes or mis-resolves a value
  by hand, once, in one reply or one plan; in R a *module* composes it on every run and no party is
  reading anything at that moment. Boundary pair against C: row 92 (C, the Agent typed a sha from
  memory) and row 139 (R, `rows.check_transaction` keys the rule it applies on the checked-out
  branch name, `rows.py:169`, every invocation). Boundary pair against D: row 104 (D, the Agent
  resolved a Rule-text `#N` against the local row store, once, in three plan revisions) and row 135
  (R, `references._MERGE` resolves a disposition's PR token to nothing at all, `references.py:90`,
  on every run of the guard).
- **H, the present enumeration pinned as an invariant** — H freezes a correct reading of a thing
  that later changes; R's key was never able to identify. Test: was the key ever right? Row 135's
  `_MERGE` has matched one row of 250 since `merge-disposition` was `with-done`; nothing changed
  under it.
- **N, a target named by an ambiguous pattern** — N's pattern is given by a party to a command, in
  the moment, and selects more or less than intended; R's lives in a module and governs every
  resolution it performs. Row 127 is the boundary: the anchor's text match is a *module's* pattern
  (`trace._matches`, `trace.py:293-295`) over a corpus that grows, so it degrades on every use —
  module-side, hence R.
- **T, a stale or partial view of shared state** — in T the key is right and the data behind it
  moved; in R the data is current and the key cannot name it. Row 31 is the boundary case and is R:
  the presence file's `rows` list is current at every touch and is derived from the wrong dimension
  — the instance's open rows rather than this session's claims.

## Incidents (7)

| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-16 | #35 | `dyad session touch` wrote `rows: 22 23 24 25 27 33 34 35` into this session's presence file; #33 and #34 were a concurrent session's | the row set is derived from the ledger's open and planned rows rather than from what this session claims, so with two sessions every file claims every open row |
| 2026-10-05 | #212 | `dyad dwork trace --out` anchored #206's and #207's `Y plan` to Operator `Y`s of a later date, collapsing #207's window to 29 seconds | the anchor fell back to wrong-date candidates and accepted any `Y/N:` reply naming the id, whatever question that reply answered |
| 2026-10-07 | #231 | the plan-`Y` touch wrote a second presence file for this same working tree, and `dyad session touch` warned against this session's own earlier file | `sessions.session_id()` returns a fresh uuid on every call when `DYAD_SESSION` is unset, so an unconfigured session has no stable identity and sheds one file per touch |
| 2026-10-07 | #231 | the push was refused by the gate: the live-log test reported INCIDENTS.md row 98 as 6 cells, not 5 | the row quoted a literal table separator inside a cell and the table parser splits on it; backlog #171's defect met from the authoring side for the first time |
| 2026-10-08 | #226 | a falsification record asserted that both the PR and merge tokens of a row's `disposed` column are read by the reference register; the PR half is false | the merge pattern matches only the `separate` form, while the live `merge-disposition: with-done` writes a form it never matches, so the link is unread |
| 2026-10-09 | #251 | the completion reply previewed #251's trace as 3h46m02s with 77 tool calls; the stored trace holds 1m07s and 2 tool calls, and the preview was withdrawn | an anchor is a text match over the whole transcript, and the prompt's own later quotations made entry 1 ambiguous, correctly refused, collapsing the window to the plan-`Y` |
| 2026-10-10 | #261 | `dyad check --pr main <head>` run from the `main` checkout reported four false main-fence failures that vanish when run from each branch's own checkout | the transaction check dispatches on the checked-out branch name, not on the `base..head` range it was handed, so a branch's commits are judged by the rule for direct pushes |

## Pattern
Seven rows, seven different keys, four modules: the presence store's session id and its row list
(`sessions.py`), the trace anchor (`trace.py`), the table cell boundary (`dyadlib.py`), the
disposition-to-PR token and the fence's branch dispatch (`references.py`, `rows.py`). Three distinct
ways a key fails to identify, and each appears at least twice:
- **not stable** — row 96 (a fresh uuid per call) and row 127 (a text anchor whose match count
  grows with every later quotation of the prompt it anchors).
- **not the right dimension** — row 31 (the instance's open rows standing in for this session's
  claims), row 139 (the checked-out branch standing in for the range handed to the guard), row 99
  (a `|` character standing in for a cell boundary).
- **not able to match the form written** — row 135 (`merge #N` standing in for `merges PR #N`), and
  row 93's first half (any `Y/N:` reply naming the id standing in for a reply to the matching
  question).
Two of the seven are each other's opposite faces inside one module, and the log says so: row 127
calls itself "the opposite face of `:100` (#212), where the anchor accepted a wrong-date candidate
and collapsed a window to 29 s." One mitigation of a non-identifying key made the other failure mode
visible.

Recurrence against the mitigations a consequence cell describes:
- Row 93's consequence names plan revision 3 and the fix shipped with two tests: "a disposition
  anchors only to a reply of its own kind and date, a mismatch is stated unmatched". Read today
  that is `trace.py:311-315`. Row 127 (#251) post-dates it, inside the same module, on the
  *prompt*-anchor half the fix did not touch — so the mode recurred after this mitigation shipped,
  one ledger generation later.
- Row 99's consequence names the standing fix as backlog #171 and calls itself "Evidence for that
  row, not a new defect". Read today `dyadlib.tables` is unchanged (`dyadlib.py:489-492`), so #171
  is still owed; rows 135, 127 and 139 post-date it.
- Row 96's consequence names the available mitigation and states it was not applied: "`DYAD_SESSION`
  set to a stable segment is the available mitigation and was not applied here, being outside plan
  #231's mutation." Measured again today: the store holds **64 presence files, 57 of them
  `unnamed-*`**, against the row's own 55 and 49 — the ratio has not improved, and `DYAD_SESSION` is
  unset in this session too.
- Row 31's consequence assigns the defect to backlog #32, "which already owns the concurrent-session
  store defects". `sessions.touch_from_open_rows` is unchanged (`sessions.py:118-128`), so that part
  of #32 is still owed; rows 96 and 139 post-date it.
- Row 135's consequence gives the measurement: "140 of 243 rows cite a PR number in `disposed` and
  the register extracts exactly one". Re-measured today: **144 of 250 row files carry a `PR #`
  token, and exactly 1 carries a `merge #` token** — the figure has grown and the gap is unchanged.

## Mitigations (phase 2)
The four keys this mode turns on, read today:

**1. The trace anchor — the kind-and-date filter (shipped), the text match (unfixed).**
`dyad/scripts/trace.py:293-295`, `_matches(entry_text, msg_text)`: `norm`-ed equality, or
containment when the entry is at least `SHORT = 20` characters (`:56`). `dyad/scripts/trace.py:297-323`,
`anchor`: candidates are the Operator messages at or after the last anchored position (`:309`); for a
`disposition` they are then filtered to replies that answer a `Y/N:` naming this id and whose
question kind matches the note (`:311-313`, `want = _note_kind(e["note"])`), filtered to the entry's
own date (`:314`, "a wrong date is unmatched, never guessed"), and truncated to the first (`:315`);
more than one candidate is `ambiguous` (`:316-317`) and only an anchored entry carries a timestamp
(`:318-320`). Non-anchored entries are reported as limit lines in the trace itself (`:456-459`) and
a Done question is labelled as such only when its timestamp equals the Done disposition's
(`:467`). Fires when `dyad dwork trace` runs, under the `dwork-trace: always` preference at every
completion (Rule-3 completion evidence). **Shipped** — the kind, date and sequence filters at
`:311-315` are row 93's own fix, blamed to 2026-10-05. **Reaches row 93** and does not reach **row
127**: the `prompt` entry takes no kind or date filter at all (the block at `:310-315` is guarded by
`if e["kind"] == "disposition"`), so a prompt's anchor is bare `_matches` over the whole transcript
and degrades monotonically as the Agent quotes its own prompt. The mode recurred on that half after
the fix shipped, and the row's last sentence is exact: "nothing warns."

**2. The presence session id — stable within a process, fresh across them.**
`dyad/guards/agent/sessions.py:50-58`, `session_id()`: `DYAD_SESSION` when it matches
`_SESSION_ID` (`:39`), "else a fresh id *each call*", explicitly "Not memoized". `touch()` resolves
it once per call and uses the same value for the path and the body (`:95`, "resolved once (F4,
d-work #32): the path and the body must agree"), and `main` passes `exclude=p.stem` so the same-root
warning cannot fire against the file just written (`:219`, "the id `touch()` actually wrote, not a
fresh call"). A separate per-*process* id, `_WRITER = uuid.uuid4().hex[:12]` at `:40-42`, is
computed once at import and written as an optional `writer` field (`:115`), with a loud warning when
a different, still-live writer holds the same file (`:99-104`). Fires at `dyad session touch`, at
session start and at every plan-`Y` (Rule-16 Presence). **Shipped** — the F4 same-call fix and the
F1 writer field both reach row 96's *symptoms* (the warning against its own file, the path/body
disagreement). **They do not reach row 96's defect**: `session_id()` is unchanged, so each process
with `DYAD_SESSION` unset still writes a new file, and the store's 57-of-64 `unnamed-*` ratio
measured today is the standing cost. **Row 31 is reached by nothing**:
`sessions.touch_from_open_rows` (`:118-128`) still derives `rows` as `[str(r.id) for r in
dyadlib.read_rows(root) if r.state in ("open", "planned")]`, every open row of the instance. The
`-r` flag exists and takes this session's own claims (`:214-217` in `main`), and the session-start
path never uses it.

**3. The table cell boundary — unfixed.** `dyad/scripts/dyadlib.py:482-496`, `tables(text)`: a
header line and a `|---|` separator, then `[c.strip() for c in lines[i].strip().strip("|").split("|")]`
at `:492`. The split is unconditional: no escape, no quote, no fence is recognised, so a `|`
anywhere inside a cell makes an extra cell. Fires wherever a table is parsed — `incidents.check_log`
(`dyad/scripts/incidents.py:98-99`, "`{r['cells']} cells, not {len(FIELDS)}`"), the changelog guard,
the manifest guard, the vocabulary guard — in Rule-11's runner and on the kernel-only path.
**Shipped as the defect**, with no mitigation of it anywhere in the tree. What reaches **row 99** is
the *gate*, not a fix: `dyad/tests/test_incidents.py:54-55`, `LiveTests.test_live_log_passes`, run
by Rule-12's suite at `dyad check --guards --pre-push`, refused the push before the malformed row
landed — detection at the one moment that matters, and the row says so ("caught before the push
landed, by the gate rather than by review"). Backlog #171 is the standing row.

**4. The disposition-to-PR token — unfixed, and unresolvable by design.**
`dyad/guards/agent/references.py:90`, `_MERGE = re.compile(r"\bmerge #(\d+)\b")`, used at `:241`
inside `pr_tokens` (`:237-243`), which also reads `PR`-prefixed segments of `refs` at `:242`; the
register row at `:412`, `("row.disposed->pr", "row", "disposed", pr_tokens, "pr", "world")`, so
whatever it extracts is a `world` kind and prints one `warn … inference` line (Rule-20 property 2).
Fires as `agent/references` in Rule-11's runner and in `check --guards`. **Shipped as the defect.**
Reaches **row 135** as the thing the row reports, and nothing mitigates it: measured today, 144 of
250 row files carry a `PR #` token in `disposed` and 1 carries a `merge #`, so the only corpus-side
link from a disposition to the merge it ratified is extracted once and resolved never.

**5. The fence's branch dispatch — unfixed.** `dyad/guards/agent/rows.py:164-173`,
`check_transaction(root, base, head)`: `if branch(root) != "main"` at `:169` selects the branch
path, and otherwise `check_range(base, head, cwd=root)` at `:173` — the first-parent walk for direct
commits to `main` (`:160`). The key is the checked-out branch name, not the range. Fires at `dyad
check --guards --pre-push` and at `dyad check --pr <base> <head>`, which Rule-1 Conditions names as
the command the Agent runs before a PR is opened without saying where it must be run from. **Shipped
as the defect**, one day old; **row 139** is its first observation and nothing mitigates it. The
row's own closing sentence names the fix by analogy to one already made: "the inverse of the plan
gate's own ledger-only exemption, where the guard was taught to judge the range rather than the
place it was run from."

**6. The guard registry and the invariant pass.** `dyad/scripts/package.py:447-452` (discovery, never
hand-listed) and Rule-12 property 1's two lists: `INVARIANTS`, pure, enforced at import by
`dyadlib.enforce`, and `TREE_INVARIANTS`, run by the runner's pass before any check. `trace.py:67-69`
declares bucket invariants; `sessions.py:43-45` declares `fields-are-five`, `stale-window-positive`
and `writer-is-well-formed`. Fires at every import of each module and in the runner's `[invariant]`
pass. **Shipped.** Reaches **none of this mode's seven rows**: read today, not one of the four
modules declares an invariant about whether its *key identifies* — the invariants cover field
counts, bucket partitions, window positivity and the shape of the writer id. This is the gap the
candidate below takes.

**7. Rule-16's own statement that the store is advisory.** `dyad/rules/RULE-16-concurrent-sessions.md`,
Presence and Enforcement: "Advisory only… never a guard failure"; the presence guard "checks only
that a presence file is well-formed (every field present, `seen` parses) — never overlap, never
staleness", which `sessions.check_record` (`:176-185`) implements exactly. Fires: **inference,
stated.** Reaches rows 31 and 96 as the reason neither is a failing check, and it is the correct
design — but it means that for those two rows **the mode's only mitigation is inference, stated**.

## Remediation candidate, under attack
One fence: a **key-coverage invariant** on the reference register. Add a `TREE_INVARIANTS` entry to
`dyad/guards/agent/references.py` asserting that, for each value the `merge-disposition` preference
admits (`separate` and `with-done`, `preferences-corpus/PREFERENCES.md`), the register's extractor
for `row.disposed->pr` matches at least one token in a literal sample of the form that value writes
— `"2026-01-01 Y merge #7"` for `separate`, `"2026-01-01 Y done (merges PR #7)"` for `with-done`.
It lives where the key is defined, beside `_MERGE` at `:90`, and it fires in the runner's invariant
pass (`package.py` `invariant_modules`, before any check) at `package.py check`, at `dyad check
--guards --pre-push`, and in `check --evidence`. `TREE_INVARIANTS` rather than `INVARIANTS` because
it reads the preference table, which Rule-12 property 1 reserves to the second list.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | It is already owned. `dyadlib.tables` has backlog #171 and the presence-store keys have backlog #32, so the mode has rows and does not need a new fence. | refuted | #171 and #32 cover two of seven keys, and row 99 (ledger #231) post-dates #171 while rows 96 and 139 post-date #32 — both open backlog rows while the mode kept recurring on keys neither names. A backlog row that covers one key is not a fence on the mode, and the play-book's Conduct says in terms that a candidate with no row is the failure it exists to prevent. Rule-9 easy agreement: this is the attack pushed to a verdict before the candidate was accepted. |
| 2 | Pointless: the resolver for `row.disposed->pr` is `world` (`references.py:412`), so Rule-20 property 2 makes every token it extracts one warn line. Fixing `_MERGE` turns 1 unresolvable warning into 144. | confirmed | "Extract more" does not survive. What survives is *coverage*: the invariant fails when the extractor cannot match the form the live preference writes, and the register row stays `world`, so the output is one red line about the extractor and never 144 lines about PRs. The fence reports on the key, not on the corpus. |
| 3 | A core-craft guard reading `preferences-corpus/PREFERENCES.md` puts instance state inside the core craft, which `package.py check` refuses by `package_rules.txt` (Rule-11 property 1). | survives, scoped | Scoped to the key's *allowed values*, which are schema and therefore package (vocabulary: "package — … preference schema"), and `dyad/guards/preferences/preferences.py` is already a core guard over the instance's table. No host-specific string enters, which is what the refusal list actually names. If even that is judged a coupling, the fallback is to assert both literal forms unconditionally, with no read of the preference at all. |
| 4 | Coverage: 1 of 7 rows. The other six are six different keys in four modules — a uuid per call, a row set from the wrong dimension, a split on the table separator, a bare text match, a branch-name dispatch. One invariant on one extractor does not reach any of them. | confirmed | Survives only as a partial. What generalises is the *placement*, not this instance: a key's coverage claim belongs in the module that defines the key, in a list the runner already runs before every check, and five more such entries are five separate d-works. Named as 1 of 7 and no more. |
| 5 | A false invariant is an incident (Rule-12 property 1), so an invariant asserting a regex's coverage will fail the whole runner the moment the preference gains a third value — turning a warn-level reporting gap into a hard stop on unrelated work. | survives, scoped | Conceded and scoped: the entry asserts coverage only for the values the table declares, and a new value arrives through a preferences-zone PR the Operator disposes — the same d-work that would add its token form. That is the intended coupling: the register cannot silently fall behind the preference it reads. Rule-12 property 1's "nothing switches it off" is the point, not a side effect. |

Read together: as a remedy for mode R the candidate does not survive — attack 4 holds without
reconciliation, and five of seven keys are untouched by it. What survives is the placement claim,
instantiated once: a key's coverage is checked where the key is defined, in the runner's invariant
pass, and the measurement carries the rest — 144 of 250 rows carry the token, 1 is extracted.

## Proposed exit (phase 4)
**A `backlog` row naming the fence to build** (exit 2), proposed only. What the row would say: a
`TREE_INVARIANTS` entry in `dyad/guards/agent/references.py` beside `_MERGE` (`:90`), asserting that
the `row.disposed->pr` extractor matches a literal sample of each form `merge-disposition` admits,
run in the runner's invariant pass before any check and so at `package.py check`, at `dyad check
--guards --pre-push` and in `check --evidence`; the register row stays `world`, so the failure is one
line about the extractor. Which row it would have caught: 135 — and it would have caught it at the
moment `merge-disposition` was set to `with-done`, before 144 rows accumulated an unread token.
The remaining six hold none of the three exits: rows 99 and 31 have open backlog rows (#171, #32)
that name the defect but not a fence and have been open while the mode recurred; rows 93 and 127 are
two faces of one anchor, half of which is fenced at `trace.py:311-315` and half of which "nothing
warns" about; row 96 has an available mitigation (`DYAD_SESSION`) that no mechanism applies, and the
store measured 64 files, 57 unnamed, today; row 139 is one day old and unmitigated. The mode stays
**open** in the index, and the Agent neither closes it nor asserts it addressed (play-book Conduct,
Rule-2).

## Delta 2026-10-24 (#259 revision 5; 7 → 19 rows)
**Rows added:** 145 (#285: two files shed by one touch), 146 (#261: `check --evidence` judging the
entrypoint's tree, not the head), 152 (#290: `rows` derived from the whole store), 153 (#290: `_WRITER`
per process where the check needs per session), 155 (#290: `parent-46`, a form `hash_ids` cannot
match), 167 (#297: a local date against a UTC comparison), 180 (#301) and 192 (#341) (bare touch claims
the board), 201 (the trace window's end branch), 203 (a comparison line computed over a transient
store), 205 (a third stray on `main`), 208 (`same_root` on the path alone). Twelve rows in twelve
days: the mode has nearly tripled, and twelve of its nineteen rows are the presence store or the trace.
**Mitigations re-read from the code.** Shipped since 2026-10-10 and reaching this mode: nothing that
changes a key. #294 (`e146b29`) added `host` and `holder` to the file and `same_root` does not read
them (`sessions.py:396-404`); #393 added attendance, which reads `holder` for nothing either. The
`backlog` rows #311, #312, #313 (2026-10-15, under #310's mandate) each name one fence of this mode —
`-r` reads plan files, `same_root` compares `holder`, `list` flags one holder behind two seats — and
none is built. Row 167's two frames (`package.py` local date, `trace.py` UTC) unchanged. Row 155's
regex unchanged.
**Recurrence after a mitigation shipped:** every row post-dates #294 or is the store the 2026-10-10
record measured at 64 files (88 today, 58 `unnamed-*`).
**Exit after the delta:** open; #279 `backlog`. Exit 2 is reachable for four sub-shapes by rows that
already exist (#311, #312, #313, #286), which is the measurement: four named fences, zero built, twelve
recurrences.

## Delta 2026-10-26 (d-work #472, seat audit-e73be78c)

Rows from the delta of 2026-10-26 (index `2026-10-10-incident-failure-modes.md`, its section of that date, where the reconciliation, the code read at `d36b1bd` and the attacks are).

- **214** (2026-10-25, #412–#414): `crafts.crafts()` (`crafts.py:413–416`) lists every directory under `crafts/`, so a retired craft's ignored `__pycache__/` read as a craft and failed the push. Directory existence stands in for being a craft (`dyadlib.craft_dirs()` already requires a `VERSION`). Proposed as P5.
- **228** (2026-10-21, #348): the presence writer was keyed on a per-process uuid. Fenced by #350, which keys the writer on the holder (`sessions.py:19–24`). **21 rows.** Status: open.
