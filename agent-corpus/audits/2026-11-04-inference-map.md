# Where inference is required — the inference map (d-work #572, v1.0 T1, under mandate #570)

**Definition of done (the operator's words, #570 revision 4):** "a report showing exactly where inferencing is required"
(everything else the operator assumes the automaton handles), with the sweep thresholds listed under where tuning is
the operator's.

Measured over `main` from 2026-11-03 00:00Z to 2026-11-04 02:00Z: 364 first-parent commits, rows #561–#568. The
inventory and its falsification are in `agent-corpus/d-work/plans/572.md`.

## 1. Where inference is required
These are the only acts that need a party that reads and decides. Everything not listed here is in §2.

| # | act | who | why no ledger line decides it |
|---|---|---|---|
| I1 | **Drafting a plan**, including its definition of done when the operator gives none | home or the owner unit | It reads the operator's prompt. A prompt is words, not a record of a decision (Rule-3, Rule-9). |
| I2 | **Drafting a question to the operator** (plan, Done, release, destructive act) and its evidence | home, orchestrate | A question is a proposal, and the agent proposes (Rule-2, Rule-10). |
| I3 | **Recording the operator's answer** (`dwork state … -d … --said`) | home, the party the operator answered | Only the party that received the words can enter them (Rule-7 property 4). It rides the reply that receives them, so it costs no extra reply. |
| I4 | **Ringing a unit** (`send_message` doorbell) | home | It needs a session, and the automaton has none (#570 A4, #569 A2). The other option is a self-armed inbox check-in per unit, which costs a turn per wake even when the inbox is empty. That is refuted for idle units. |
| I5 | **A relay that says more than the plan** (review requests, sequencing, a correction) | home | Its content is not in any record. A relay that only restates the plan is §2 (K2). |
| I6 | **Choosing a row's owner** (the board's `owner` at the row's opening) | home | Which unit should do the work is a judgement about the charter's domains (`MANDATES.md`). |
| I7 | **A board write that changes the next act or the owner** | home | It records a decision made by reading the work. Re-wording a report is not one (§2, K5). |
| I8 | **The work itself:** code, Rules, records, falsification, evidence runs, PRs | the owner unit | It is the work the d-work was opened for. |
| I9 | **The d-work trace** (`dwork trace`) | home | It reads the home's transcript, which is never a record (Rule-7 property 2). |
| I10 | **Composing the Done entry's `merges PR #a at <head>` list** | home | Today it is copied from the Done question. It could be read from the board's question, but the entry's form is Rule-3's, so that is counsel's call and is not built here (K13, a candidate). |

## 2. Everything else: the automaton or code, not inference
| # | act | where it runs | status |
|---|---|---|---|
| K1 | board flip on a plan-`Y`: `waiting-on unit <owner>`, question removed | automaton, with the plan notice | PR A, after PR #640 (#569) lands. It shares `automaton.py` |
| K2 | the relay that restates the plan becomes the plan notice, quoting the unit's part from the plan's `parts:` line | automaton | PR A, as above. The `parts:` line is counsel's play-book paragraph |
| K3 | board flip on a Done-`Y` whose cut is still pending: `waiting-on external merge` | automaton | PR A, as above |
| K4 | the pending queue (`plan-ready`, `done-ready`) | `dyad board` and `board resume`, derived at read | **this PR** (board.py). A stored `_cos` `queue` is still read until H3's alias removal |
| K5 | no board re-wording when a report arrives: the report is the record | conduct; W10' (#569) shows a report newer than the board | counsel's play-book paragraph |
| K6 | one report to home and its copy to orchestrate | `inbox post --cc`: one land, one message per box | **this PR** (inbox.py) |
| K7 | `holder` re-taken by every writer | `board set` keeps the holder unless one is given | **this PR** (board.py) |
| K8 | merge of a Done-`Y`'s PRs, close, accreted rows closed, board dropped | automaton (#556, #562) | landed |
| K9 | the `row #N planned` notice to the owners | automaton (#556) | landed |
| K10 | sweep, hygiene and work-in-flight findings to home | automaton sweep (#564, #565, #569) | #564 and #565 landed; #569 is PR #640 |

Measured share: on rows #561–#568 the home made 5.25 board writes and relays per disposition (median), plus about 2
`queue` writes. K1–K5 remove about 4 of those. What remains is I2, I3 and I4, which together are about **2–3 home
replies per disposition**, against T2's target of 3. That is an estimate until the attention row's trace measures
it.

## 3. Where tuning is yours
Each value is a constant in code today, so a change is a one-line agent-zone PR the operator disposes. C1 (tunables as
preferences) is withdrawn by #570 revision 4, so this list is where tuning lives.

| tunable | value | where | what it decides |
|---|---|---|---|
| sweep schedule | 06:00 and 18:00 America/Los_Angeles | `.github/workflows/dyad-sweep.yml` (`cron`) | how often every finding below is read. Each threshold is a minimum age plus up to 12 h |
| `SWEEP_LANDING_HOURS` | 24 h | `dyad/scripts/automaton.py` | a Done-`Y` whose heads have not landed is a finding |
| `SWEEP_STALE_DAYS` | 3 days | `dyad/scripts/automaton.py` | a board entry unchanged this long is a finding |
| `SWEEP_CI_HOURS` | 24 h | `dyad/scripts/automaton.py` | the window of code pushes checked for corroboration |
| `NOTICE_CHARS` | 3000 | `dyad/scripts/automaton.py` | one notice's size before it splits |
| `RACE_TRIES` | 5 | `dyad/scripts/automaton.py` | re-merges after a lost push race |
| `HYGIENE_STALE_DAYS` | 30 days | `dyad/scripts/hygiene.py` | I1: a backlog row untouched this long |
| `HYGIENE_SIMILAR` | 0.35 | `dyad/scripts/hygiene.py` | the lowest similarity listed as a candidate pair |
| `HYGIENE_MAX_DF` | 0.20 | `dyad/scripts/hygiene.py` | a word in more than this share of rows is ignored as boilerplate |
| `HYGIENE_TOP` | 10 | `dyad/scripts/hygiene.py` | at most this many candidate pairs |
| `INFLIGHT_W1_HOURS` | 4 h | `dyad/scripts/hygiene.py` (PR #640) | W1: a relay unread this long |
| `INFLIGHT_W2_DAYS` | 3 days | same | W2: a planned row on a unit quiet this long |
| `INFLIGHT_W3_HOURS` | 24 h | same | W3: an open row with no plan this long |
| `INFLIGHT_W6_DAYS` | 3 days | same | W6: an open PR's head unchanged this long |
| `INFLIGHT_W8_DAYS` | 3 days | same | W8: a promise listed this long |
| `INFLIGHT_W9_HOURS` | 24 h | same | W9: a question to the operator this old |
| `STALE_AFTER` | 6 h | `dyad/guards/agent/sessions.py` | a presence file past this is stale (`session list`; W7b) |
