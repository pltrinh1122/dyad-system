# Falsification record — "a `cos` or `cabinet` session maps 1:1 to a Claude Code / agent session" (d-work #295)

**Claim (Operator, 2026-10-14, refusing #293's plan):** a `cos` or `cabinet` session is in 1:1
correspondence with a Claude Code (or other agent-CLI) session. Plan #293 had assumed it silently —
"the cabinet's file is `ds-cabinet-term-1.md`", one seat, one session.

## Terms
- **harness session**: what the kernel CLI calls a session — one transcript, one
  `CLAUDE_CODE_SESSION_ID`, resumable, compactable, restartable (`CLAUDE_CODE_WORKER_EPOCH=5` was
  observed in the session that wrote this: five worker restarts under one id). Subagents inherit the
  id (plan #285 rule 1).
- **dyad session / seat**: what Rule-16 calls a session — a presence file
  `<instance>/d-work/sessions/<id>.md`, `id` = `DYAD_SESSION` when set, else a fresh `unnamed-*` per
  call (`dyad/guards/agent/sessions.py` `session_id`). `cos` and `cabinet` are roles a seat plays
  (plan #253 R28).

## Attacks
| # | attack | result | survivor |
|---|--------|--------|----------|
| F1 | **One harness session, many seats.** One harness session wrote three presence files in one turn (#285 incident, `INCIDENTS.md` row 145) because `session_id()` mints a fresh id each call when `DYAD_SESSION` is unset; 58 of 65 files on `main` at `f7c26c2` are `unnamed-*`. | **confirmed — the claim fails 1:N** | A harness session with no configured seat is no seat, or several; the mapping is a configuration, not a fact. |
| F2 | **One seat, many harness sessions.** `web-sysadmin-scope` is the `session:` line of 18 provenance records, `web-sysarch` of 14 — ephemeral web containers carried one seat name across days; `sessions.py` builds a `writer` field (F1 of d-work #32) *because* two processes can share one `DYAD_SESSION`. | **confirmed — the claim fails N:1** | A seat outlives any harness session; it is a name re-attached at each start. |
| F3 | **Make the seat id the harness id** — the peer cos session did (`e2c6869c-62a7-…` is its seat and its harness id, in 4 records and its presence file). | refuted as a rule | It holds for one harness lifetime; the next resume gets a new id and the seat's history forks across files. The Operator named the cabinet `term-1`, a seat meant to outlive the sessions that terminal runs — which F3 cannot give. |
| F4 | **The dyad can verify which harness session holds a seat.** | **confirmed impossible on this kernel** | One shared git credential, `CLAUDE_CODE_SESSION_ID` inherited by subagents, `DYAD_SESSION` set by nothing (plan #285 rule 1; plan #252, "cannot authenticate a session"). The record can hold the holder's id beside the seat, never prove it. |
| F5 | **1:1 holds at an instant**: one seat, one live holder; two live writers on one file is the #32 collision, warned loudly. | survives, scoped | The correct shape: a seat is a **lease** — at most one harness session at a time (enforced by warning only), many in sequence; a harness session holds at most one seat (two from one process is the #285 incident, a defect). 1:1 at an instant, N:1 over time, 0:1 when unconfigured. |
| F6 | Easy agreement with the `N`: over-correct to "no mapping at all". | pushed | F5 lands against it — the instant-level 1:1 is what Rule-16's "only that session ever writes it" relies on; the survivor keeps it. |

## Survivor
A `cos` or `cabinet` is a **seat**: a role name (`cos`, `ds-cabinet-term-1`) bound to one presence id,
held by one harness session at a time and by many over time, never verifiable by the dyad. A
registration record names the seat and records beside it, as the process reports them, the current
holder's harness session id and host (d-work #294: `holder:`, `host:`) — "who holds the seat now",
refreshed at every touch, not "which session the seat is".

## Consequences
- Plan #293 revision 3: the cabinet sets `DYAD_SESSION=ds-cabinet-term-1` persistently for its
  terminal, registers once, and later holders touch; this cos takes the seat name `cos`.
- Plan #294 revision 2: `touch()` writes `holder:` from `CLAUDE_CODE_SESSION_ID` when the kernel
  exposes it, beside `host:`.
- Not a Rule change: Rule-16 already says a presence file is "one session's claim", advisory, never a
  lock; this record names what "session" means there and what the claim can and cannot carry.

Disposition: see ledger #295 (Rule-2: the Done-`Y` of d-work #295 disposes this record).
