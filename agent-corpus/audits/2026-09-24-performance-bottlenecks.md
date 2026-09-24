# Performance audit — where this practice spends its time (2026-09-24)

*d-work #154. Two sources: the code, timed on this tree at `097b0ce`, and this session's own
transcript, 16,488 lines over 2026-09-15 to 2026-09-24, read (never copied, never committed —
Rule-7 property 2) by a delegated reader. Detects and counts; disposes nothing.*

## Cost per act
Each act timed once on this tree, and separately derived from the transcript's own
`tool_use`-to-`tool_result` spans. The two columns are independent measurements of the same act,
and they agree.

| act | timed here | transcript, isolated runs | what it does |
|-----|-----------:|--------------------------:|--------------|
| `check --guards` (the pre-push hook) | **1.75 s** | 1.65 s mean, 1.15 s median (n=29) | 61 checks, **no tests** |
| `check --evidence` (merge evidence) | **42.75 s** | 48.0 s mean, 45.3 s median (n=23) | 113 checks **and 717 tests** |
| `check` (the full runner) | 42.13 s | 35.6 s mean (n=38) | checks and tests, no evidence block |
| `git push` (hook included) | 3.80 s | 4.27 s mean, 2.52 s median (n=73) | ~1.75 s hook, ~2 s network |
| `git fetch origin main` | 1.60 s | — | what `dwork new` runs before allocating |
| `dwork new` / `dwork state` | — | 2.47 s / 2.06 s mean | the fetch dominates `new` |
| `gh pr create` / `gh pr merge` | — | 2.40 s / 12.15 s mean | network only |
| `gh pr view` / `gh pr list` | 0.34 s / 0.35 s | — | network only |
| `git worktree add` / `remove` | 0.05 s / 0.00 s | — | negligible; chained runs make it look costly |
| `python3 -m unittest discover -s dyad/tests` | **120.06 s** | 30.7 s mean, **300.1 s max** (n=127) | 479 tests, nested scratch installs run their own suites |
| the same, `DYAD_NO_NESTED_TESTS=1` | **39.13 s** | — | what the runner itself sets (`package.py:186`) |

**The single largest avoidable cost is in the last two rows.** Run by hand, the core suite spawns a
full nested suite inside each scratch install; the runner sets `DYAD_NO_NESTED_TESTS=1` and does
not. Every hand-run of that command therefore paid about three times the runner's price, and eight
of the ten longest Bash executions of the whole session are that one command.

## Frequency observed
Occurrences across 1,503 Bash calls; 38% of commands chain several classes, so these are
occurrences, not commands, and the wall-clock column charges a chained command in full to every
class it contains (overlapping, never additive).

| class | occurrences | wall-clock (containment) |
|-------|------------:|-------------------------:|
| `python3 -m unittest` | 134 | **3,894 s** |
| `check --evidence` | **79** | **3,527 s** |
| `git push` | **321** | 3,169 s |
| `git commit` | 281 | 2,399 s |
| `git merge` | 118 | 1,311 s |
| `gh pr merge` | 67 | 1,102 s |
| `check --pr` | 84 | 1,009 s |
| `gh pr create` | 74 | 973 s |
| `check --guards` | 80 | 606 s |
| `dwork new` / `dwork state` | 86 / 96 | 393 s / 734 s |

Total Bash execution 12,573 s (3.49 h), which is 99.2% of all tool time and about a third of the
10.43 h the harness records as machine-busy across 216 turns. The other two thirds are model time.

On `main` over 2026-09-21 to 24, both sessions together: **203 commits — 72 merges, 85 non-merge
ledger-only, 46 other.** The plan's figure of 201 was taken an hour earlier and before merges were
counted separately; a merge's file list is empty, so a naive classifier calls every merge
ledger-only, which is the trap this audit was written to avoid.

## Frequency required, and by what
| act | what requires it | required granularity | observed |
|-----|------------------|----------------------|---------:|
| ledger commit and push | Rule-3 Ledger — written clerically when the disposition is given; Rule-3 Completion — the record precedes the merge it ratifies; Rule-16 — the allocator and `check_id_collisions` both read `origin/main` | once per disposition | 85 ledger-only commits on `main` |
| `check --guards` | Rule-14 property 3, through the pre-push hook | once per push | 80 |
| `check --evidence` | Rule-2 Binding — on the exact head being merged | **once per merge** | **79 runs against 29 completed d-works — 2.72×** |
| `check --pr` | Rule-1, the Agent's own conduct before opening a PR | once per PR | 84 |
| `python3 -m unittest` | nothing. The runner runs the suites itself | **zero** | 134 |

## Observed minus required
1. **Hand-run test suites: ~3,894 s, none of it required.** The runner already runs every suite, with
   the nested-test flag set. A hand-run is for reading one failure, and costs three times the
   runner's price when it names the whole root.
2. **Evidence runs: 79 against 29 merges.** Re-verifying after a change to the head is correct; the
   surplus is running it before the PR, again after the PR, and again after the merge. At ~48 s a
   run, halving the surplus returns roughly 20 minutes of this session.
3. **Pushes: 321 occurrences, and this is the smallest of the three.** A bare push is 2.5 s, of which
   1.65 s is the hook. All 85 ledger pushes to `main` together cost about five minutes across four
   days and two sessions.

## The delegation axis
Eight delegated launches: 32 agent transcripts, 587 API messages, **77.1 M tokens** (1,204 input,
31,733 output, 3.96 M cache-creation, 73.1 M cache-read). The largest single launch ran **31.8 min**
across 6 agents; the nine-mode fan-out ran 11.5 min across 18. Against that, the main thread
deduplicated by message id is **1.03 B tokens** across 2,224 API responses, and the harness's own
running total at 99.2% through the transcript is **$519.15** — a lower bound, since its cache-read
figure lags the file's end.

So delegation is about 7% of the token spend, and no git act is within two orders of magnitude of
either. The longest *machine-busy turn* of the session is 64.1 min, and the single most expensive
turn is 186 M tokens, 18.1% of the whole main thread on its own.

One accounting note, on the record: plan #154 cited 1.15 M and 2.37 M subagent tokens for two
workflows, taken from the harness's own completion notices. Measured from the per-agent transcripts
instead, the same two are 1.087 M and 2.086 M billed. Same ordering, two bases, five to twelve per
cent apart; a figure should name which basis it uses.

## Candidates (surfaced, not adopted — each is its own d-work)
1. Never hand-run a whole test root: name the module or the case, or let the runner do it; if a root
   must be run whole, set `DYAD_NO_NESTED_TESTS=1` as the runner does.
2. Run `check --evidence` once per merge, on the head being merged, as Rule-2 Binding asks —
   re-running only when that head moves.
3. Leave push frequency alone. The ledger push is what makes a disposition visible to the other
   session before it allocates an id, and the races it prevents cost this ledger three renumberings
   and one overwrite (#30, #26/#34, #27).
4. If wall-clock is the target, the delegation axis is where the minutes are, and the question there
   is what a fan-out buys, not what it costs.

## Disposition
Surfaced for the Operator; disposed by the Done-`Y` of ledger #154. No remedy is taken here.
