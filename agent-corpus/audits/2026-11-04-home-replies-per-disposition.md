# Home replies per disposition, measured now — T2 of v1.0 (2026-11-04)

*Audit for d-work #591 (accreted under mandate #570), unit audit-e73be78c. Plan `agent-corpus/d-work/plans/591.md`.
It measures, names drivers and proposes cuts; it opens no row and changes no code.*

## Definition of done
Proposed by the cos and adopted by plan #591: "the measure over the release's rows so far, from their traces, the drivers
named with their share, and the cuts proposed, each owned by a row."

## Sources
- **Trace previews** of the release rows, run by the home in its own session at 19:06Z (`dyad dwork trace <id>`,
  read-only), because its transcript is not in this unit's container (Rule-7 property 2). They were posted to this
  unit's inbox (row 591, report `20261104T190623Z-program-59cec502-1`); #573's is its stored Done trace. Windows end at
  19:05:52Z.
- **git**: `origin/main` first-parent from #570's opening (`fa17b98e`, 01:51:55Z) to 19:02Z, 364 commits, each
  classified by the store it writes.
- **The provenance store**: disposition and prompt entries added in the same window.

## The measure
### Per row, as the trace computes it (T2's stated instrument)
| row | window | replies | dispositions | replies per disposition | tool calls |
|---|---|---|---|---|---|
| #570 | 01:50–19:05 | 85 | 2 | 42.5 | 320 |
| #573 | 15:52–18:54 (Done) | 31 | 3 | 10.3 | 152 |
| #574 | 02:52–19:05 | 55 | 2 | 27.5 | 238 |
| #575 | 02:34–19:05 | 68 | 2 | 34.0 | 276 |
| #584 | 16:59–19:05 | 28 | 1 | 28.0 | 174 |
| #585 | 17:25–19:05 | 21 | 1 | 21.0 | 157 |
| #586 | 17:42–19:05 | 13 | 1 | 13.0 | 130 |
| #587 | 17:45–19:05 | 11 | 1 | 11.0 | 127 |

No window: #571, #572, #588, #589, #590, #591 (accreted or opened by a disposition, so no anchored prompt in the
home's transcript).

**T2 as stated, the median of the release's last 5 rows with a window (#575, #584–#587): 21.0. Target 3: not met.**
Over all 8 rows the median is 24.3.

### Release-wide, each reply counted once
#570's window spans the release, so its 85 replies are every home reply in it.

| denominator | count | replies per unit |
|---|---|---|
| disposition entries (all rows, the trace's kind) | 54 | 1.6 |
| distinct operator answers (commits adding a non-mandate disposition) | 13 | 6.5 |
| operator messages (answers + prompts, 13 + 18) | 31 | 2.7 |

**Overlap factor:** the per-row numerators sum to 312 against 85 distinct replies, 3.7. On average each home reply is
counted in 3.7 rows' figures.

## Drivers
### 1. The instrument (about 3.7× of the per-row figure, and the denominator)
`trace.replies` (`dyad/scripts/trace.py:426`, used at `:614`) counts every home reply in a row's window: turns about
other rows, and turns woken by a harness notice, included. It divides by that row's own dispositions on the window's
days. Under concurrency, each window holds the whole home's traffic:
- #575's 68 replies span 16.5 hours of the release, over its 2 dispositions.
- A batch `Y` writes one entry into every named row (54 entries for 13 answers). So the same release reads 1.6, 6.5 or
  42.5 depending on the denominator.

The per-row figure measures the home's concurrency more than its cost per decision. This is mode 28's face in the
2026-11-04 incident index: an instrument narrower than the question it reports on.

### 2. Wakes that are not the operator (at least 64% of replies)
85 replies, of which at most 31 follow an operator message. **At least 54 (64%)** end turns woken otherwise. The
transcript classes these as `notify`; the trace does not print the split, so the bound is from the counts, an
inference.

The wake sources in git over the window, 95 messages in all:

| wake source | messages | share of the 95 |
|---|---|---|
| unit reports to the home (each followed by a doorbell send) | 56 | 59% |
| automaton notices | 32 | 34% |
| unit notices | 5 | 5% |
| acks | 2 | 2% |

Background-task completions add more; the transcript holds those, and git does not.

### 3. Home writes per turn (the cost inside each reply: tool calls, tokens, pushes)
| home write | commits | share of 178 |
|---|---|---|
| board entries (`board/<id>.md` 91, `board/_cos.md` 37) | 128 | 72% |
| relays to units | 37 | 21% |
| inbox read markers | 13 | 7% |

Every board write and every relay is a ledger-only push, and a moved `main` makes it retry. Two board pushes in this
unit's own session today retried twice.

## Cuts, each with its owner
| # | cut | driver | expected effect | owning row |
|---|---|---|---|---|
| K1 | The trace counts, per row, only the replies of turns that name that row (`turns_naming_others` already finds them). It divides by distinct operator answers, and prints replies by trigger (operator, notify, compact) beside the total | 1 | removes the ~3.7× overlap; makes driver 2 measured, not bounded. The T2 figure becomes decidable | **none owns it**: proposed to the cos as a new engineer row, or as a clause of #572 (T1) if the cos prefers |
| K2 | A report doorbells the home only when the home must act (a question owed, a refusal). Other reports wait in the inbox for the home's next turn | 2 (59% of wakes) | up to 56 fewer wakes; the bulk of the non-operator replies | **#584** (message-route criterion: inbox plus doorbell by default) |
| K3 | An automaton notice that decides nothing the home acts on (plan noted, row closed) is read at the next turn, never a wake. The board update it implies is the automaton's | 2 (34% of wakes), 3 | up to 32 fewer wakes and the board writes behind them | **#572** (T1, clerical-act inventory) |
| K4 | Board phase advanced only by recorded lines, written by the automaton, not by a home turn | 3 (72% of writes) | most of the 128 board pushes leave the home's turns | **#587** (orchestration as a finite-state machine) |
| K5 | A relay adds its receiver as owner in one commit (board and inbox together) | 3 (relays 21%) | one push per relay instead of two | **#586** (mechanize two CLI errors) |

**Order of effect:** K1 first, because until it lands T2 cannot be read. Without K1 the release-wide replies per
operator answer (6.5) is the honest figure to set against 3, then K2 and K3 (wakes), then K4 and K5 (cost per reply).

## Limits
- The reply split by trigger is bounded from counts, not measured (K1 measures it).
- Distinct operator answers are counted by commits adding a non-mandate disposition entry. Answers given in one
  message to several questions count once per commit.
- The previews' windows end at 19:05:52Z and the git counts at 19:02Z. Entries in between are not counted.
- The home's session was compacted once today. The previews read the whole transcript file, as the home reports.
- Nothing was run but read-only git, corpus reads and the home's own previews.
