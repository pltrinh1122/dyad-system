# Messaging architecture — the implementation reference

**Status (revise this line in every PR that closes a row below):** as of `main` `fb7fb95`, 2026-10-15.
Built: the presence store, the ledger as state, the relayed prompt, hand-carry, the intake, PR events.
Transport substitute in use: the directed notice. Specified and `backlog`: the bus #303, the board #304,
the edge register #305, the cos's standing rules #306, status #316, the Rule-3 Intake amendment #317.
Gap rows `backlog` with stored plans: #311–#317. Owner of this document: d-work #310; a closing PR of
any row named here updates the row's line in §6 and this status line in the same PR.

**What this is.** The one living document an implementer reads first. It does not restate the
specification or the audit; it cites them and holds what neither can: what is built now, which row
builds what next, and what every component must keep true. Normative text is the specification,
`agent-corpus/audits/2026-10-08-spec-session-messaging-control.md` (d-work #253, `done`; its
requirements are cited below as R1–R29 and its build steps as S1–S5). Reasoning and the edge-case
register are the ADR, `agent-corpus/audits/2026-10-08-adr-disposition-architecture.md` (#252). What was
built and observed on 2026-10-15 is the audit, `agent-corpus/audits/2026-10-15-messaging-architecture.md`
(#302), whose gaps G1–G8 this document tracks. The seat model is
`agent-corpus/falsification/seat-vs-harness-session.md` (#295); the planes as falsified against the
Operator's synthesis are `agent-corpus/falsification/communication-planes.md` (#302). Where this document
and the specification differ, the specification governs and this document is wrong.

## 1. The model (by citation)
| term | defined in | one line |
|---|---|---|
| Operator, Agent, seat, holder, relayed prompt, intake, presence file, disposition, counter-prompt | `dyad/vocabulary/VOCABULARY.md` | the only definitions; never restated here |
| harness session, seat as a lease (1:1 at an instant, N:1 over time, unverifiable) | #295 survivor | a seat is the durable name; a holder is who holds it now |
| node, edge, announcement, store, topic, tuning, band, board | spec §0 | enter the vocabulary with S1–S4 (spec §8); a node is a seat's holder at an instant (audit §4a item 2) |
| cos, cabinet | spec R28–R29; plan #285 (the six rules of the discipline) | roles a seat plays; a cos holds attention, never authority |

## 2. The planes (spec R1–R4) and the one exclusion
Three planes, typed by graph shape; no message on more than one (R1). **Announcement** — undirected,
unaddressed, no authorization; carrier the store (S1) across systems, the presence store within one.
**Command** — directed; counter-prompt and disposition; **no transport ever** (R2): the edge is the
session that asked. **Interrupt** — the harness's (R3); records only. **R4:** no node sends another
an instruction, a disposition, or a question that obliges an answer. Every component below is
admissible only on the announcement plane or as a record of the other two.

## 3. Components and interfaces
Built components, with the store, guard, CLI and owning Rule an implementer touches. Rows in
*italics* are specified and not built; their row holds the plan.

| component | plane | store | guard (entity) | CLI | owner | state |
|---|---|---|---|---|---|---|
| presence store | announcement (R14, within system) | `<instance>/d-work/sessions/<seat>.md` | `dyad/guards/agent/sessions.py` (`presence`, shape only, `TRANSACTION = False`) | `dyad session touch [-r] [-f]`, `dyad session list` | Rule-16 | built; defects G1–G3 → #311, #312, #313 |
| ledger as state (rows, plans, provenance, traces) | announcement | `<instance>/d-work/{rows,plans,provenance,traces}/` | `rows.py` (fence), `prs.py` (plan gate), `plans.py`, `provenance.py`, `traces.py` | `dyad dwork new\|state\|retire\|trace` | Rule-3, -7, -15, -16 | built; a `planned` row is executable by any seat (Rule-15 phase 2) — how a row crosses seats without a message |
| relayed prompt | announcement (R29) | the receiving row's provenance entry, note `relayed via <seat>` | `provenance.py` (count and shape) | `dyad dwork new\|state … --prompt … --relayed-via <seat>` (`package.py:976-979`; never on `--said`) | Rule-7 p4, Rule-3 Intake | built; the Rule-3 sentence for the within-system relay → #317 |
| hand-carry | (the Operator prompting) | the receiving row's provenance, a plain `prompt` | — | — | Rule-7 p3 | built; the draft lives in the drafting seat's plan file |
| intake | announcement | the receiving row (opened by the Operator's `Y` or prompt) | — | `dwork new … --said` (defect) / `--prompt --relayed-via` (enhancement) | Rule-3 Intake | built; no cross-system carrier until S1 |
| directed notice (`create_session` first message, `send_message`) | **not a plane**: a transport substitute while S1 is unbuilt | none in the corpus | none; the hosting marks a peer message as not user input | hosting tools | audit §3.6; R4's negative test | in use; its record → #314 |
| PR events | hosting notification edge | the hosting | never a guard (Rule-14 p3) | `subscribe_pr_activity` | ADR option E | optional; never a channel between seats |
| *the bus (announcement store)* | announcement, across systems | `topics/<topic>/<date>-<system>-<session>-<n>.md` in a separate repo (R5, R7) | the publish-side fence refusing anything disposition-shaped (R10) and credential shapes (R11) | `dyad bus init\|publish\|pull\|list` (S1) | Rule-14 library row; a Tended craft `bus` (Rule-11) | **#303** `backlog` |
| *status fields* | announcement (R14–R16) | optional presence fields `state`, `working`, `suspended`, `waiting-on` | `sessions.py`, checked when present | `touch --state … --on <row>` at R15's moments | Rule-16 | **#316** `backlog` (S2) |
| *the board* `cos/board` | projection | untracked surface over rows, presence, the store (R19; never reads the clock) | — | `dyad project cos` / `dyad cos` runner | sysarch projection rules | **#304** `backlog` (S3) |
| *bands* | standing disposition | `preferences-corpus/` only (R23); content-scoped (R24); mechanical predicate (R25); ceiling (R26) | the preferences guard | — | Rule-2 *Not ratification* | **#306** `backlog` (S4; the cos's standing rules) |
| *the edge register* | record of the command plane | one file per asked counter-prompt, closed by the disposition's clerical commit | — | — | Rule-3 (an amendment; ADR D2) | **#305** `backlog` |
| *Rule-3 Intake amendment* | — | the Rule text | `rules.py`, `vocabulary.py` | — | Rule-3 | **#317** `backlog` (S5) |

## 4. Invariants every component must keep (acceptance tests)
From audit §6, stated as what an implementer's tests assert. A component that breaks one is refused
at its plan-`Y`, not patched after.
1. **Authority does not travel.** No code path records or carries a disposition for a row in any
   session but the one that asked. Test: the bus fence refuses a bare `Y`/`N`, a disposition-form
   line and any `kind` naming disposal, and admits `kind: question` carrying a verbatim `Y/N:` line
   (spec F4's discriminating pair); `--relayed-via` still attaches to `--prompt` only.
2. **The question is the edge.** A disposition binds the set the question named; a changed head or a
   new PR needs a fresh `Y` (Rule-2 Binding). Test: the edge register (#305) records the asked head.
3. **Agent-to-agent control is excluded (R4).** A published message is admissible only if it would be
   a legal announcement and obliges nothing. Test: the bus `kind` set is closed (R9); no kind names an
   order or an answer.
4. **The Operator's words only** in provenance (Rule-7 p4); the relaying agent's words never.
5. **A cos may propose, never open** (R29); report by state only. Test: no cos code path writes
   another seat's presence file or opens a row without the Operator's prompt or `Y` behind it.
6. **Identity is unverifiable** (R24, spec §10). Test: no guard or band predicate reads `holder`,
   `session`, `writer` or a commit author as proof of who acted.
7. **Degradation (R6).** With the store unreachable every Rule, guard, gate, counter-prompt and
   disposition works as today. Test: the whole suite passes with `DYAD_BUS` unset or unreachable;
   first test of S1.
8. **One seat, one writer.** Only a seat's own holder writes its presence file (Rule-16); a status or
   notice is a claim, never a lock.

## 5. Build sequence and order
Spec §9, with rows. Order is forced only at S1→S2/S3 and S1→S5; S4 is independent.

| step | what | row | depends on | notes |
|---|---|---|---|---|
| S1 | the `bus` craft: envelope (R8, R9), fence (R10, R11), `dyad bus` | #303 | — | lands with R6 tested first; reads #295 before fixing R8's `session` cell (audit §4a item 2) |
| S2 | status (R14–R16) and the manifest row (R5) | #316 (fields); #303 (row) | S1 for the cross-system half | the within-system half may land first |
| S3 | the `cos/board` surface (R17–R19) | #304 | S1 for the store's questions | renders rows and presence alone until then |
| S4 | bands (R23–R27) | #306 | — | preferences zone; the Operator writes the values |
| S5 | the Rule-3 Intake amendment (R29) | #317 | S1 for the transport sentence | the relay sentence may land alone |
| — | the edge register (ADR D2) | #305 | — | what makes R16's four states computable |
| — | presence defects | #311, #312, #313 | — | small; any seat; before S2 widens the file |
| — | notice record; cloud registration | #314, #315 | — | conventions until S1; #315 touches the pre-push path |

## 6. Gap register (audit §8 → rows)
| gap | row | state | closes when |
|---|---|---|---|
| G1 `touch -r` leaves `files` empty | #311 | backlog, plan stored | `-r` derives `files` from the named rows' plans; Rule-16 sentence; tests |
| G2 `same_root` ignores `host`/`holder` | #312 | backlog, plan stored | holder compared beside root; `list` prints the difference |
| G3 one holder, two seats | #313 | backlog, plan stored | `list` flags it; the two live cases retired by their holders |
| G4 the directed notice has no record | #314 | backlog, plan stored | sending plans carry `## Notice sent`; with S1, `kind: note` |
| G5 cloud registration omits the unshallow fetch | #315 | backlog, plan stored | the pre-push path advises on a shallow clone; the mechanics carry the line |
| G6 the relayed `planned` row is a shape R29 does not name | — | stated, not a defect | named in S5's amendment or the bus `kind` set when either lands |
| G7 `seat`, `holder`, `relayed prompt` undefined | — | **closed**, PR #390 (#302) | — |
| G8 S2 and S5 have no row | #316, #317 | backlog, plans stored | the rows exist; the gap is closed, the work is theirs |

## 7. Conventions for implementers (until the rows above land)
- **Registering a seat.** `DYAD_SESSION=<seat>` on every `dyad` command (a cloud seat) or in the shell
  profile (a terminal seat); `git config core.hooksPath dyad/hooks`; on a cloud clone
  `git fetch --unshallow --tags origin` before the first push (#315); `dyad session touch -r <row>
  -f <each file the plan touches>` (until #311); the touch is a ledger-only commit direct to `main`.
- **Handing a row to another seat.** By state: open and plan it in the sending session, record its
  plan-`Y` there, drop it from the sender's presence, and let the receiving seat execute under
  Rule-15 phase 2. A notice may carry the mechanics; it carries no authority and is quoted verbatim in
  the sending plan under `## Notice sent` (#314).
- **Relaying a prompt.** The Operator's words verbatim, `--prompt … --relayed-via <seat>`; never a
  disposition; the receiving seat asks its own plan-`Y` in its own session.
- **Reporting back.** Rows, plans, dispositions and the presence file on `main`; never a message to
  the cos. The cos reads the board (hand-rendered until #304).
- **Adding a message kind, a field or a term.** A d-work, not a convention: R9 closes the `kind` set;
  Rule-16 names the presence fields; Rule-6 owns the terms.

## 8. Updating this document
A PR that closes a row named here: moves the row's line in §6 to its closing state (or deletes it
when the gap is gone), updates the component's row in §3 and the status line at the top, and cites
the PR. A PR that adds a component: one row in §3, one line in §5, its invariants in §4 if new. This
document is instance state (row ids, seats); the craft-portable part — §2, §4 — moves to the `bus`
craft's docs when S1 lands, by that row's own plan (plan #310 F6).
