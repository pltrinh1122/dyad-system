# Audit — 2026-10-15, the messaging architecture and framework between holders

*d-work #302. Opened 2026-10-15 in the `cos` seat on the Operator's synthesis of the cos/cabinet
communication stack ("FALSIFY. recommend VOCABULARY updates for survivors."), refused once with the
amend "delegate #302 to a cloud cabinet session to refine scope to include a comprehensive review and
explanation of the `Messaging Architecture and Framework` between `holder`", and planned on revision 2
of `agent-corpus/d-work/plans/302.md` (plan-`Y` 2026-10-15, given in the cos's session; both prompts
verbatim in `agent-corpus/d-work/provenance/302.md`). Executed by the cabinet seat `ds-cabinet-cloud-3`
under Rule-15 phase 2, in its own session. Standing: `main` at `29fa5ea`, 295 numeric rows, 69
presence files (58 `unnamed-*`, 4 carrying `host`/`holder`), python 3.13.16, git 2.43.0.*

Disposition: see ledger #302 (Rule-2: the Done-`Y` of d-work #302 disposes this record).

**What this is.** A topic audit (`dyad/playbooks/audit.md`: a review the Operator asks for on one
subject "stays an Operator prompt with its own plan; it may borrow the Conduct below and nothing else
here"). No watermark line, no regression block, no phase 0. It borrows the Conduct: it detects and
sizes, disposes nothing, changes no Rule and no code, opens no row; gaps are *proposed, not opened*.
It explains the framework **as specified** (#252's ADR and #253's specification, both `done`, both
landed "only the document": `2026-10-08-adr-disposition-architecture.md` at PR #386 and
`2026-10-08-spec-session-messaging-control.md` at PR #388, `70135e4`, Done-`Y` 2026-10-15 batch
#253,#307 — the landed text is plan #253 verbatim, `diff` empty against `plans/253.md`; this audit
cites it as the ratified frame and re-decides none of it) and **as
built** (what a session can do today, with the code and the Rule line that make it so). Every claim
carries a `file:line`, a row id, or a command's observed output; what was observed only in this
session and cannot be re-derived from the corpus is marked **[session]**. The companion falsification
record is `agent-corpus/falsification/communication-planes.md`.

**Incorporation of #253's outcome** (the Operator's prompt received on this row mid-execution,
`provenance/302.md` entry 4: "incorporate/supersede outcome of d-work #253 which has recently been
completed which overlaps the objective of this session"). #253 completed while this audit was being
written. Read as: #253's landed, Done-verified text is the specification this audit explains and the
record falsifies against; where the cos's revision-1 record or this audit overlaps it, #253 governs
and this audit supersedes nothing of it — it adds what #253 could not hold: what is built, what the
live record shows, and the gaps between the two. Three things #253's completion changes here are
stated in §4a; nothing in §1–§3 or §5–§8 contradicts R1–R29.

## 1. The parties

| party | what it is | where that is written | as built today |
|---|---|---|---|
| **Operator** | the human party; the sole disposer (vocabulary) | `dyad/vocabulary/VOCABULARY.md`; Rule-2 | one person, one git credential shared by every session (#252: "cannot authenticate a session") |
| **harness session** | what the kernel CLI calls a session: one transcript, one `CLAUDE_CODE_SESSION_ID`, resumable, compactable, restartable; subagents inherit the id | `agent-corpus/falsification/seat-vs-harness-session.md` Terms; plan #285 rule 1 | the cloud container this audit runs in reports `CLAUDE_CODE_SESSION_ID=5fdc4e6e-…` and `CLAUDE_CODE_REMOTE=true` **[session]** |
| **seat** | a role name bound to one presence file `<instance>/d-work/sessions/<id>.md`, `id` = `DYAD_SESSION`; held by one harness session at a time and by many over time; never verifiable by the dyad; `cos` and `cabinet` are roles a seat plays | #295 survivor; Rule-16 Presence (`RULE-16:55-56`, "where the file's name is the seat"); `sessions.py` `session_id()` | `DYAD_SESSION` is set by nothing in the repo (#285 rule 1): a cloud seat prefixes it on every command, a terminal seat persists it in a shell profile (#293 revision 3); 58 of 69 files are `unnamed-*`, the seats no one configured |
| **holder** | the harness session holding a seat now, as the file's optional `holder` line records it from `CLAUDE_CODE_SESSION_ID`, beside `host` (`<kernel> <os> <arch>`) | Rule-16 Presence (`RULE-16:51-56`); `sessions.py` `holder()`, `host_line()`, `touch()`; d-work #294 (PR #381) | written by code, never typed; "a hand-added key does not survive the next `touch()`" (`sessions.py` docstring). Holder *history* is git's: `git log -- sessions/cos.md` shows the seat renamed from `unnamed-b04e526aeab2` at `f2869ed` and re-touched with host and holder at `6a61c5f` |
| **cos** | an ordinary session distinguished by three things — tuning across every topic, the `cos/board` surface, a band permitting it to publish relayed prompts and nothing else; "holds no authority of its own; it holds attention" | #253 R28; #252 D3 and revision 3 ("a directory, not a courier") | all three are unbuilt (#285 F-a: no `cos` token in any `.py`, re-verified at this standing: `git grep -lw cos -- '*.py'` is empty); the role is the discipline of #285's six rules, applied by hand, with the board rendered by hand (#298) |
| **cabinet** | a seat the cos delegates to; it opens its own row on the relayed prompt, plans, and asks its own counter-prompts in its own session | #253 R29; plans #293, #296, #299 | four exist: `ds-cabinet-term-1` (#297, terminal), `ds-cabinet-cloud-1` (#296, no row on `main` at this standing), `ds-cabinet-cloud-2` (#301; #307 `done`; it landed #252 and #253), `ds-cabinet-cloud-3` (this one, #302) |
| **subagent** | a process a seat spawns; its actions are the seat's; it reads, searches and drafts, never writes a row, asks or answers a counter-prompt, pushes, or runs a host action | Rule-3 Scope (E7, #107); vocabulary `subagent` | the one party with no seat and no presence file; it inherits the holder's harness id (#295 Terms), which is why `holder` cannot distinguish a seat from its subagents |

The live seats at this standing (`DYAD_SESSION=ds-cabinet-cloud-3 ./dyad/bin/dyad session list`,
`live` = `seen` inside the 6 h window, `sessions.py` `STALE_AFTER`):

| seat | rows | host | holder | root |
|---|---|---|---|---|
| `cos` | 296 299 | cloud linux x86_64 | `59cec502-…` | `/home/user/dyad-system` |
| `ds-cabinet-cloud-2` | 301 307 | cloud linux x86_64 | `92e3d665-…` | `/home/user/dyad-system` |
| `ds-cabinet-cloud-3` | 302 | cloud linux x86_64 | `5fdc4e6e-…` | `/home/user/dyad-system` |
| `ds-cabinet-term-1` | 297 | terminal linux x86_64 | `e2c6869c-…` | `/mnt/shared_data/dyad/dyad-system` |
| `e2c6869c-62a7-49ac-813d-8a4f2925afc2` | 259 | (none) | (none) | `/mnt/shared_data/dyad/dyad-system` |
| `unnamed-b04e526aeab2` | 18 rows | (none) | (none) | `/home/user/dyad-system` |

Two of those six rows are findings (§8, G2 and G3): the UUID-named seat is the same harness session
that holds `ds-cabinet-term-1` (its name equals term-1's `holder`), and the `unnamed-*` file was
refreshed today by the cos's own plan-`Y` commit (`9e17777`) through the no-argument touch, so it
claims 18 rows and a `files` field of prose tokens.

## 2. The three planes (#253 R1–R4), as specified and as built

#253 R1: traffic divides into exactly three planes, typed by graph shape; no message is on more than
one. The ADR derives the typing in revision 3 (the question is the edge; a broadcast has no edge) and
revision 7 (E33: control divides by shape, not by name).

| plane | shape | what travels | carrier (specified) | record | as built today |
|---|---|---|---|---|---|
| **announcement** | undirected, unaddressed, zero or many readers, no authorization | intake, status, questions, notes (`kind` closed set, R9) | the store ("the bus", §2, S1) across systems; the presence store within one system (R14) | the store itself | **the presence store and the ledger on `main`** (§3.1, §3.2). The bus does not exist (row #303 `backlog`); the directed notice stands in for it (§3.6) |
| **command** | directed: one asker, one answer, binds the named set | counter-prompt, disposition, band supersession, stop | **none** — the session's own chat (R2: "the edge is the session") | row `disposed` + provenance (Rule-3, Rule-7) | exactly as specified, and the only plane with a mechanical fence: `--relayed-via` attaches to `--prompt` and never to `--said` (`dyad/scripts/package.py:976-979`); the plan gate `prs.py`; the main fence `rows.py` |
| **interrupt** | directed, preempting | the Operator entering a node mid-turn | the harness's mechanism (R3) | provenance (R20) and status (R21) only | provenance only: a mid-turn prompt is a `prompt` entry (R20; eight in #252 alone); R21's `suspended` status is unbuilt (S2) |

R4, the exclusion that every mechanism below is measured against: **no node may send another node an
instruction, a disposition, or a question that obliges an answer. A node may only announce.** The
Operator's synthesis drew two planes (control = relay, data = announcement); the record
`communication-planes.md` F2 finds both inside #253's announcement plane — a relayed prompt is
published *as an announcement* (R29, `kind: intake-enhancement`) — and the plane the synthesis left out
is the command plane, which has no carrier at all.

## 3. Every mechanism that exists today, with its record

### 3.1 The presence store (Rule-16 Presence; #253 R14's within-system home)
- **What.** One file per seat, `<instance>/d-work/sessions/<id>.md`, `key: value` lines `session`,
  `seen`, `root`, `rows`, `files`, plus optional `writer`, `host`, `holder` (`sessions.py` `FIELDS`,
  `touch()`). Touched at session start and at every plan-`Y` (`RULE-16:41-50`); read by
  `dyad session list` or directly; "advisory, never a lock".
- **Carries.** State of the seat: what it holds and from where. Two signals: `files` overlap across
  rows (`sessions.overlaps`) and same `root` (`sessions.same_root`, the sharper one, #185).
- **Authorizes.** Nothing. `agent/sessions` declares `TRANSACTION = False` (`sessions.py:43`); its
  guard checks shape only (`check_record`).
- **Record.** The file itself, on `main`, by a ledger-only commit (Rule-3: `<instance>/d-work/` is
  clerical). Holder history is `git log` over the file.
- **Observed.** This seat's registration: `dyad session touch -r 302` at `f9abe2d`, pushed direct to
  `main` (#300: the Operator disposes d-work, not git commands). The explicit `-r` path writes
  `files:` empty (§8 G1); the re-touch with `-f` per file of plan #302 is what made this seat's
  `files` true.

### 3.2 The ledger as state: rows, plans, provenance, traces on `main`
- **What.** The row-file store (`rows/<id>.md`), the plan file (`plans/<id>.md`, Rule-15), the
  provenance record (`provenance/<id>.md`, Rule-7), the trace (`traces/<id>.md`, #213). All on `main`
  by ledger-only commits; the fence `rows.py` admits nothing else direct.
- **Carries.** Everything a cabinet reports *to* the cos and everything the cos reads *about* a
  cabinet: a row's state and `disposed` chain, a plan's revisions, the Operator's verbatim words.
  "Report to the cos by state only — rows, plans, dispositions, your presence file — never by
  message" is the bound every relayed registration carries (#296, #299, #302 plan revision 2).
- **Authorizes.** The state does: a `planned` row carries its plan-`Y` on `main`, and Rule-15
  phase 2 lets *any* session execute it ("in the same or any later session"). That is how #302
  moved seats: the cos asked the plan-`Y` in its session, recorded it at `62a173e`, and this seat
  executes against the file — the authority never left `main`.
- **Record.** The commits. The plan gate reads the row at the base commit (`prs.py`); the provenance
  guard reads the record against the row (`provenance.py`, property 5).
- **Observed.** #301's walk (plan #301, step table): every step a plan revision on `main`, every
  question asked of the Operator in `ds-cabinet-cloud-2`'s session.

### 3.3 The relayed prompt (#253 R29; Rule-7 property 4; Rule-3 Intake)
- **What.** The Operator's verbatim prompt, carried by another agent and entered as the receiving
  row's `prompt` entry with the note `relayed via <session>` (`RULE-3:281-282`; `RULE-7:51-55`).
  CLI: `dyad dwork new|state … --prompt <p> --relayed-via <session>`; `--relayed-via` without
  `--prompt` is refused (`package.py:976-977`), and no flag attaches a relay note to `--said`.
- **Carries.** Node-creating words (#252 revision 3): within one dyad system they open a row as a
  prompt does (#301 entry 1, `relayed via cos`); across systems they are the enhancement shape of an
  intake and wait for the receiving Operator's `Y` (Rule-3 Intake). Six records on `main` carry the
  note: #26, #139, #175, #176, #226, #301.
- **Authorizes.** Nothing the words did not already authorize: a relay carries no disposition. The
  cabinet asks its own plan-`Y` in its own session (#296 F1, #299 F1).
- **Record.** The provenance entry, plus the relaying seat's plan file, which holds what it sent
  (#296 "The relayed prompt", #299 "The relayed prompt", #302 revision 2 "Mutation").
- **Observed.** `provenance/301.md` entry 1 ("spin up cloud cabinet session: …", `relayed via cos`).

### 3.4 Hand-carry (#293; `provenance/297.md`)
- **What.** The Operator types into a session a text another seat drafted. `provenance/297.md`
  entry 1 is a plain `prompt` with no `relayed via` note — correctly, by Rule-7 property 3 ("the
  Agent writes the entry from the prompt it received"): the Operator sent it, so it is that
  session's own Operator prompt. The draft is the cos's Agent text until the Operator sends it
  (plan #293 "The hand-carried prompt"; `communication-planes.md` F4).
- **Carries.** Whatever the Operator chooses to send; today, a seat's registration mechanics.
- **Authorizes.** As any Operator prompt: it opens a row; its plan is asked there.
- **Record.** The receiving row's provenance (the Operator's act) and the drafting seat's plan file
  (the draft) — two files, and the chain between them is prose (#293 names the cabinet; #297 refs
  293).
- **Reach.** The one carrier that reaches a terminal seat with no remote session id (§5).

### 3.5 The intake and its two lifts (Rule-3 Intake, `RULE-3:269-287`)
- **What.** A message from another agent opens no d-work; what it may carry is a candidate row in
  one of two shapes — a defect with evidence, or an enhancement with its Operator's verbatim prompt
  behind it. Anything else is returned with the missing shape named.
- **Lifts.** Two, both the Operator's: a `Y` opens an intake *from another agent*; a *prompt* opens a
  row for the Agent's own finding ("the Operator may still open a row for it by prompting",
  `RULE-3:286`). The carrier never lifts (`communication-planes.md` F7).
- **As built.** The admissible set is exactly the broadcast-admissible subset (#252 revision 3),
  which is why the bus's `kind` set (R9) is Intake's two shapes plus status, question and note. The
  cross-system carrier has never existed: 29 rows of this ledger were opened by an intake from
  another dyad system, every one carried by the Operator's hand (#252 G2).

### 3.6 The directed notice: `send_message` / a created session's first message, as a transport substitute
- **What.** The hosting's session-to-session message (`create_session` with a first prompt, or
  `send_message` to a session id). Used by the cos to reach each cloud cabinet: #296
  (`ds-cabinet-cloud-1`), #299 (`ds-cabinet-cloud-2`), #302 revision 2 (`ds-cabinet-cloud-3`, this
  seat — the message that opened this session **[session]**). A terminal seat is reached by hand-carry
  instead (#293).
- **Is it a plane?** No. By #253's own definition an announcement is undirected and unaddressed;
  a message to one session id is directed. By R2 the command plane has no transport. So the directed
  notice is a **transport substitute while the store is unbuilt** (#253 §2 / S1, row #303 `backlog`):
  admissible only when its content would be a legal announcement and obliges nothing — R4's negative
  test, applied by the sender's conduct (`communication-planes.md` F6).
- **What the four notices carried.** The Operator's verbatim words (already in a provenance record
  on `main`), the plan already authorized on `main` (#302), the registration mechanics (seat name,
  `DYAD_SESSION` prefix, `add_repo`, hooks path, `touch -r`), the Rules to read, and the bounds
  (ask your own counter-prompts; report by state; open no row the cos's words do not warrant). Each
  is restatable from `main` except the mechanics, which live only in the sending seat's plan file.
- **Mechanical fence outside the corpus.** The receiving harness frames a peer's message as not the
  Operator's: this session received the cos's hand-over wrapped as a system notification stating
  that it is not user input and carries no approval **[session]**; the hosting's `send_message`
  likewise marks a message "as sent by this session, not typed by a person" and tells the target to
  treat it as data from a peer. That is half of R4 enforced by the kernel's library, never by a
  guard — which Rule-14 property 3 forbids depending on (#252 revision 7 M2: the command and
  interrupt planes are outside the corpus by construction).
- **Record.** None in the corpus beyond the sending seat's plan file. What a cabinet received is
  reconstructible only from the sender's plan and the hosting's own log (§8 G4).

### 3.7 The hosting as a notification edge (#252 option E; PR events)
- **What.** PR comments, reviews and CI results arrive in a subscribed session as events; the
  hosting authenticates the Operator where a bus message never could.
- **Status.** "Kept as an optional edge, not an architecture" (#252 E): Rule-14 forbids any guard
  depending on it, CI is detecting-only and never a gate (#168), and a `Y` typed there is still read
  in the session that asked. No cabinet of this instance uses it as a channel to another seat.

### 3.8 The mandate (accretion), named here because it is the one standing authorization in use
- **What.** A plan that states a mandate scope lets its own plan-`Y` cover rows the Agent opens while
  executing it (`accretion: implicit`, Rule-3 Scope; `dwork new --mandate <id>`, `package.py:989-999`).
- **Between holders?** No. A mandate binds within one row's plan; it is not a channel and travels to
  no other seat. It is listed so that the reader does not mistake it for a band (#253 R23–R27, S4,
  unbuilt): the only standing dispositions in force are the twelve preference values (#285 rule 5,
  counted at this standing: `preferences-corpus/PREFERENCES.md` has twelve rows).

## 4. Specified and unbuilt

| item | specified | status at this standing |
|---|---|---|
| the bus (announcement store, envelope, publish-side fence, `dyad bus`) | #253 §2 R5–R13, S1; ADR option B/D | row #303 `backlog` (born under #252's mandate at `b4b2730`) |
| status fields on the presence file (`state`, `working`, `suspended`, `waiting-on`) and the manifest row | #253 R14–R16, S2 | unbuilt; #253 F5 confirms the optional-field path is open (`sessions.py` `writer`, `host`, `holder` already use it) |
| the `cos/board` surface and runner | #253 R17–R19, S3; #252 D1 | row #304 `backlog`; the board is rendered by hand (#285, #298) |
| bands (sovereignty) | #253 R23–R27, S4 | row #306 `backlog` (the cos's standing rules); no bands table |
| the edge register (question store) | #252 D2, revisions 3–5 | row #305 `backlog`; the edge set is derivable only as a union (#285 F-c) |
| Rule-3 Intake's store amendment | #253 R29, S5 | not opened |
| the ADR and the specification as corpus records | #252, #253 "only the document" | both landed and `done`: the ADR (`2026-10-08-adr-disposition-architecture.md`, PR #386, `be4347b`), the specification (`2026-10-08-spec-session-messaging-control.md`, PR #388, `70135e4`) |

Nothing above is re-decided here. Where this audit names a gap the specification already closes on
paper (G4 is R7/R8; G1 is R14's own substrate), it says so and sizes the gap as built.

### 4a. What #253's completion changes for this audit
1. **The frame is ratified text, not a plan.** R1–R29 are now Operator-verified (Done-`Y`,
   `provenance/253.md` entry 3); the cos's revision-1 record attacked the same words in the plan file.
   Every citation of `plans/253.md` in this audit and its record reads equally against the landed
   audit, which holds the plan verbatim.
2. **`node` (#253 §0) and `seat` (#295) are two words for two things, not one.** #253 defines a node
   as "one dyad-system session, of any system, on any host" and R28 calls a cos "an ordinary
   dyad-system session"; #295, written later and `done` earlier (PR #380), finds that a session is a
   holder and the durable thing is the seat. Reconciled, not superseded: a node is a seat's holder at
   an instant, and the envelope's `session` cell (R8) names the seat when `DYAD_SESSION` is set and a
   fresh `unnamed-*` when not — the same configuration gap #295 F1 names. The bus craft's row (#303)
   reads #295 before it fixes R8's `session` cell. Stated here, not decided.
3. **The build sequence has rows for S1, S3, S4 and D2 and none for S2 and S5.** #252's mandate
   opened #303 (the bus, S1), #304 (the surface and runner, S3), #305 (the edge register, D2) and
   #306 (the standing rules, S4's text); R14–R16 status (S2) and the Rule-3 Intake amendment (S5,
   R29's store sentence) have no row. Both are what a cos needs first — R21's `suspended` is the one
   record the interrupt plane gets, and R29 is the relay this audit's §3.3 runs on. Elevated as G8.
4. **#253 §8 names eight Rule-6 terms; this PR adds three others.** `node`, `edge`, `announcement`,
   `store`, `topic`, `tuning`, `band`, `board` enter with S1–S4 as the specification says; `seat`,
   `holder` and `relayed prompt` are not among them and pre-empt none — they define words three Rules
   already use (G7).

## 5. The reach of each kind of seat

| kind | addressed how | registers how | persists `DYAD_SESSION` how | known cost |
|---|---|---|---|---|
| **cloud seat** (`host: cloud`) | by hosting session id (`send_message`, `create_session`) — the only seats a cos can reach by message | `add_repo` → clone → `git config core.hooksPath dyad/hooks` → `touch -r <row>` → ledger commit direct to `main` | cannot: no shell profile survives the container; the prefix is restated on every command (#296 "Seat") | the clone is shallow with no tags, so the first push fails 11 `plan.base->commit` references and the bundle guard until `git fetch --unshallow --tags` (INCIDENTS row 167, #301; repeated here under #302, row below); the relayed mechanics of #296, #299 and #302 do not say so |
| **terminal seat** (`host: terminal`) | not addressable from a cloud seat; reached by hand-carry (#293) and read by state (§3.2) | the Operator types the drafted prompt; the first holder opens the row (#297) | in the shell profile, so every later session re-takes the seat (#293 revision 3) | a terminal session that also carries a UUID-named seat from before #295 appears twice on the board (§8 G3) |
| **the Operator** | in every session, as its disposer | — | — | every seat's counter-prompts are theirs to answer, in that seat's session: four live seats, one Operator (#296 F2, #299 F4, #302 R3) |

"Remote Control" (a terminal session linked to the hosting) would give a terminal seat a remote id;
not observed in this instance and not relied on.

## 6. The invariants, and what enforces each

| # | invariant | written where | enforced how |
|---|---|---|---|
| I1 | **Authority does not travel; attention does.** A `Y` is given only in the session that asked; a relay carries prompts, never dispositions | #252 (the organising finding), revision 3; #253 R2; #285 rule 1; Rule-2 Binding | **mechanical:** `--relayed-via` attaches only to `--prompt` (`package.py:976-979`); the provenance guard's count (`provenance.py`, property 5) fails a disposition entry no row carries. Inference: that a `Y` typed in one session is not read in another (#252 E8) |
| I2 | **The question is the edge.** One asker, one answer, bound to the named set; a changed head or a new PR needs a fresh `Y` | #252 revision 3; Rule-2 Binding | inference (E4, E5: no mechanism compares the asked head to the merged head); the plan gate checks only that a `Y plan` exists (`prs.py`) |
| I3 | **Agent-to-agent control is excluded.** A seat may announce; never instruct, dispose, or ask a question that obliges an answer | #253 R4; #252 E34; #285 rule 4 | conduct, stated in every relayed registration; the hosting marks a peer message as not user input (§3.6) — a library fence, outside the corpus |
| I4 | **The Operator's words only** in a provenance record; a relayed prompt is still the Operator's, noted; the relaying agent's words never enter | Rule-7 property 4 (`RULE-7:51-61`) | **mechanical** for shape and count (`provenance.py` state and transaction checks); inference for authorship (the record cannot tell a hand-carried draft from a composed prompt — §3.4) |
| I5 | **A cos may propose, never open.** A row opens on the Operator's prompt or `Y`; a cos relays and surfaces | #253 R29; #285 rule 3 | conduct; the fence `rows.py` admits any ledger-only commit from any seat, so a cos *could* open a row — nothing mechanical stops it (#301 F1 is the same gap from the cabinet's side) |
| I6 | **Report by state only.** Cabinet → cos through rows, plans, dispositions and presence on `main`, never by message | #296, #299, #302 bounds; #253 R14 | conduct; the hosting's `send_message` is available to every cloud seat, so the fence is the seat's own (`communication-planes.md` F10) |
| I7 | **Identity is unverifiable.** One credential; `CLAUDE_CODE_SESSION_ID` inherited by subagents; `DYAD_SESSION` set by nothing; `writer` per process | #252 E7; #253 R24, §10; #295 F4 | none possible on this kernel; accepted, and the reason I1 is the design and not a policy |
| I8 | **Degradation.** Every Rule, guard and disposition works with no bus and no cos | #253 R6 | **true by construction today**, because none of it is built: this audit is the test R6 asks for, run on an instance where the store is absent |

## 7. Failure modes already recorded, and what each shows about the framework

| mode | rows (`agent-corpus/audits/INCIDENTS.md`) | what it shows |
|---|---|---|
| **id collision** between seats | `:98` (#223), `:127` (#256), `:155` (#291; #298 renumbered likewise) | ids are allocated `max(origin, local)+1` and two seats holding unpushed ids cannot see each other (`crafts/sysarch/rules/stores.md`: the checks make a collision loud, not impossible). A branch-fenced seat allocates against a `main` it cannot advance (`:155`). The framework's one shared substrate is `origin/main`, and the allocator reads it only at fetch time |
| **the no-argument touch** | `:159` (#290); live again today in `unnamed-b04e526aeab2.md` at `9e17777` (18 rows, a `files` field of prose tokens) | `touch_from_open_rows` (`sessions.py`) claims every `open`/`planned` row of the instance because a seat has no record of its own rows but the file it is about to write; the recommended `-r` form has the converse defect (G1). Rule-16's one signal is right only when the invocation is hand-built |
| **the writer warning on every touch** | `:160` (#290); fired on this seat's second touch **[session]** | `_WRITER` is per process (`uuid4()` at import) where the check needs per-session; on the CLI every invocation is a new process, so the F1-#32 collision signal fires on the seat's own previous touch and cannot distinguish the case it was built for |
| **shed `unnamed-*` files** | `:103` (#231), `:152` (#285), `:166` (#301) | `session_id()` mints a fresh id per call when `DYAD_SESSION` is unset (`sessions.py:59-67`); 58 of 69 files are this. The seat model (#295) is the answer; nothing in session start supplies the name |
| **same-root false positive across containers** | plan #301 "Same-root finding"; this seat's `touch` and `list` print `[SAME ROOT AS YOU]` for `cos` and `ds-cabinet-cloud-2` **[session]** | `same_root` compares the `root` string only (`sessions.py` `same_root`); every cloud container checks out `/home/user/dyad-system`, so three separate containers read as one shared checkout. Since #294 the file carries `host` and `holder`, which the comparison does not read (G2) |
| **the shallow clone** | `:167` (#301); repeated under #302 (row appended by this PR) | a cloud seat's clone resolves no plan base commit and no tag, so the kernel-only path refuses its first push on references the seat never touched; the registration mechanics relayed to three cloud seats omit the fetch (G5) |
| **the unanchored trace** | `:100` (#212), `:120` (#229), `:134` (#251) | `trace.anchor` binds a disposition to a reply by date and id, and a preview is not reproducible from the transcript as stored. For a d-work that crossed seats — #302: planned in the cos's session, executed here — the harness transcript the trace reads is this container's, which holds no plan-`Y`; the trace must be cited with its buckets marked absent (#213) or run against transcripts this seat cannot reach (§ Not observed) |
| **one harness session, two seats** | #295 F1/F5 (a defect); live at this standing (G3) | the board reads two seats where one holder sits; nothing mechanical reads `holder` across files |

## 8. Gaps elevated for disposition (proposed rows, never opened; Rule-3 intake shape, defect with evidence)

- **G1 — `touch -r` leaves `files` empty.** Observed: `agent-corpus/d-work/sessions/cos.md`,
  `ds-cabinet-cloud-2.md` and this seat's first touch (`f9abe2d`) carry `files:` with no entry while
  their rows' plan files name 4+4, 12+3 and 9 paths (`sessions.files_touched` over plans #296, #299, #301, #307, #302). Mechanism: `touch(root, rows, files)` writes the
  `files` it is given (`sessions.py` `touch()`); only `touch_from_open_rows` reads plan files, and
  `main()` takes that path only when neither `-r` nor `-f` is passed. So the invocation Rule-16's
  signal needs — the seat's own rows *and* their plans' files — exists in no form: `-r` alone is
  blind, no argument over-claims (`:159`). Reproduce: `DYAD_SESSION=x dyad session touch -r 302`;
  read `files:`. Suggested shape: `-r` reads the named rows' plan files unless `-f` is also given.
- **G2 — `same_root` ignores `host` and `holder`.** Observed: `[SAME ROOT AS YOU]` printed for two
  seats in other containers, every time, since every cloud checkout is `/home/user/dyad-system`.
  Mechanism: `same_root()` compares `root` strings and `is_stale`; the `host`/`holder` lines written
  since #294 are not read. Suggested shape: same `root` *and* same `holder` (or absent `holder` on
  both) before the warning; print the differing holders otherwise.
- **G3 — one holder, two seats.** Observed: `sessions/e2c6869c-62a7-49ac-813d-8a4f2925afc2.md`
  (rows 259, no `host`/`holder`, `seen` 2026-10-14T20:29Z) and `sessions/ds-cabinet-term-1.md`
  (`holder: e2c6869c-62a7-49ac-813d-8a4f2925afc2`, `seen` 2026-10-15T01:31Z), same `root`. The
  UUID-named seat is the pre-#295 form (#295 F3: seat id = harness id) and the same harness session
  now holds `term-1`; #295 F5 calls two seats from one process a defect. Mechanism: nothing reads
  `holder` across files; `dyad session list` shows both as live. Suggested shape: `list` flags a
  `holder` equal to another live file's `session` or `holder`; the old file is retired by the
  holder's next touch under its seat name, as `unnamed-b04e526aeab2` was meant to be for the cos —
  and was not: the cos's `9e17777` re-touched it.
- **G4 — the directed notice has no corpus record.** Observed: what `ds-cabinet-cloud-3` received is
  in no file on `main`; plan #302 revision 2 describes it, this audit paraphrases it, and only the
  hosting holds it. Mechanism: §3.6 is a transport substitute with no store; #253 R7/R8 is the store
  that would hold it (`topics/<topic>/<date>-<system>-<session>-<n>.md`, one fenced body). Suggested
  shape: until S1 lands, the sending seat's plan file quotes the notice verbatim under its own
  heading (as #296 and #299 nearly do), so the receiving row can cite it by path.
- **G5 — cloud registration mechanics omit the unshallow fetch.** Observed: `:167` under #301 and the
  row appended under #302 — two cloud seats, the same day, the same refusal, the same fix. Mechanism:
  the hosting's clone is shallow and tagless; `references.py` `plan.base->commit` and
  `bundle.py` read the whole history. Suggested shape: one line in the relayed mechanics
  (`git fetch --unshallow --tags origin` before the first push), or the pre-push path printing that
  advice when `git rev-parse --is-shallow-repository` is `true`.
- **G6 — the relayed `planned` row.** Observed: #302 was opened and planned in the cos's session and
  handed to this seat `planned`; #253 R29 names only the relayed *prompt* (a row the cabinet opens).
  Mechanism: Rule-15 phase 2 already admits execution "in any later session", so the hand-over is
  legal by state (§3.2) and needed no message to be legal; what the notice added was the seat's
  registration. Not a defect: a shape to name in #253's successor or in the bus craft's `kind` set
  (a `status` naming a row offered for execution), so the record says which of its two mechanisms a
  hand-over used. Stated, not proposed as a row.
- **G8 — S2 and S5 of #253's build sequence have no row.** Observed: rows #303–#306 (`backlog`,
  born under #252's mandate at `b4b2730`) cover S1, S3, D2 and S4; no row names R14–R16 status or
  R29's Rule-3 Intake amendment (§4a item 3). Mechanism: #252's mandate named four rows; #253 §9 names
  five steps, and the two are not the same partition. Suggested shape: two `backlog` rows, each
  `refs 253`, opened by the Operator's disposition (Rule-3: a cos may propose, never open).
- **G7 — three terms used by Rules and defined nowhere.** `seat` and `holder` (Rule-16 Presence
  since #294) and `relayed prompt` (Rule-3 Intake since #34) occur in Rule text with no vocabulary
  row. Closed by this d-work's PR (three rows, `communication-planes.md` F8). The four bus terms
  (`announcement`, `carrier`, `relay`, `report by state`) are #253's and wait for S1 as `bus:` craft
  terms; adding them now would fail the orphan check.

## Not observed
- The cos's and `ds-cabinet-term-1`'s harness transcripts, and the hosting's message log: on other
  machines; the directed notices are known here only from the sending plans and from the one this
  seat received.
- Whether `ds-cabinet-term-1`'s shell profile persisted `DYAD_SESSION`: a host fact on
  `/mnt/shared_data/dyad/dyad-system` (Rule-8: not read from here). Its two touches on `main`
  (`c33cb5a`, `e515bf4` "touched from an unconfigured shell") are consistent with it not having.
- `ds-cabinet-cloud-1`'s state: no presence file and no row on `main` at this standing
  (`grep -l cloud-1 agent-corpus/d-work/rows/*.md` finds only #296, the cos's). Plan #301 step 2
  reads `8e4fe0b` as that cabinet's row #302; `git show --stat 8e4fe0b` is the cos's opening of
  *this* #302 ("#302 opened on the Operator's prompt, plan stored"). A misread of the board by
  state, left for `ds-cabinet-cloud-2` to read by state in turn; whether cloud-1 ever registered is
  unresolvable from here.
- Nothing of #253's: its landed text was compared to its plan file (`diff` empty) and read whole.
