# Token-efficiency audit — data appendix (2026-10-17)

*d-work #338, banking the analysis behind `2026-10-17-token-efficiency.md` (d-work #333), which the
audit's §6 disclosed as uncommitted. Everything here is stored text: nothing in this file is run by
the package or by a guard. The scripts are not executable files; copy one out to run it (`python3 -I`).
Paths inside the reports and scripts name the session scratchpad they were written in
(`/tmp/claude-0/.../scratchpad/`) and `/home/user/ds-cc4`, the worktree they read; both are gone, and
the commands in the audit's §6 reproduce the figures from `origin/main` and the hosting.*

## 1. Session usage (measured, hosting `list_sessions` → `external_metadata.usage`, read 2026-10-17)

The 18 sessions on this account whose source repository is `dyad-system` (150 sessions on the
account in all, 68 with usage; the other projects' sessions are not reproduced). Two report no usage
and two report cost without token counts. `derived $` is the audit's §2 derivation: first-party
per-MTok rates (Sonnet 5.5 $2 in / $10 out / $0.20 cache read; Opus 5.5 $4 / $20 / $0.20; Fable 5.1
$10 / $50 / $0.25), cache write at 2× input, cost = (input×in + output×out + cache_write×2×in +
cache_read×read) / 1e6; unpriced models and sessions without token counts carry `-`. The audit's
totals (16 sessions with usage) are $4,050.2, 21,070,576 output, 208,435,775 cache-write and
6,877,159,491 cache-read tokens.

| session | created | model | reported $ | derived $ | output tokens | cache write | cache read |
|---|---|---|---:|---:|---:|---:|---:|
| ds: sysadmin craft | 2026-09-18 | claude-sonnet-5-5 | 1737.7 | 743.3 | 7,454,596 | 75,545,960 | 1,831,257,100 |
| ds: syseng craft | 2026-09-16 | claude-sonnet-5-5 | 1003.5 | 835.8 | 5,727,148 | 65,705,269 | 2,575,682,750 |
| ds: countersign-seeding | 2026-09-24 | claude-opus-5-5 | 451.9 | 496.3 | 3,417,368 | 25,840,972 | 1,104,899,384 |
| ds: sysarch craft | 2026-09-16 | claude-sonnet-5-5 | 290.3 | 215.7 | 1,999,438 | 21,009,870 | 557,898,120 |
| asg-peter: dwork #272 continuation | 2026-09-25 | claude-opus-5-5 | 142.2 | 145.3 | 1,078,478 | 5,466,423 | 397,938,090 |
| cos: ds-cloud | 2026-10-13 | claude-fable-5-1 | 115.3 | 122.2 | 227,944 | 4,254,031 | 101,832,042 |
| cabinet-cloud-2: (92e3d665) work the un-closed d-work rows in DAG order | 2026-10-15 | claude-fable-5-1 | 92.7 | 95.5 | 283,579 | 2,843,367 | 97,297,828 |
| cabinet-cloud-1: (242a5502) d-work framework architecture | 2026-10-15 | claude-fable-5-1 | 62.9 | 70.4 | 234,134 | 2,155,132 | 61,872,120 |
| Dyad Instantiation Protocol | 2026-07-05 | claude-opus-4-8 | 47.8 | - | n/a | n/a | n/a |
| cabinet-cloud-3: (5fdc4e6e) #302 messaging architecture between holders | 2026-10-15 | claude-fable-5-1 | 47.6 | 47.7 | 177,241 | 1,495,848 | 35,361,835 |
| ds: audit craft | 2026-10-05 | claude-sonnet-5-5 | 31.7 | 31.7 | 269,522 | 2,663,769 | 91,581,725 |
| leo-dev: digest | 2026-07-22 | claude-opus-4-8 | 15.2 | - | 152,273 | 780,967 | 10,711,722 |
| ds-cabinet-cloud-5: the Dyad System's README — architecture, design, framework,  | 2026-10-17 | claude-fable-5-1 | 5.9 | 5.9 | 25,445 | 156,549 | 5,756,665 |
| client-dyad-system: push the v0.1.0 release tags (asg-peter #277) | 2026-09-25 | claude-opus-5-5 | 2.5 | 2.5 | 7,104 | 268,851 | 902,454 |
| ds: cabinet cloud-4 — token-efficiency audit | 2026-10-17 | claude-opus-5-5 | 1.6 | 1.6 | 10,634 | 118,513 | 2,144,529 |
| ui-design craft implementation | 2026-09-25 | claude-opus-5-5 | 1.6 | 1.6 | 5,672 | 130,254 | 2,023,127 |
| Uncommitted changes verification | 2026-10-13 | - | n/a | - | n/a | n/a | n/a |
| pt-ms-7d75-steady-owl | 2026-10-07 | - | n/a | - | n/a | n/a | n/a |

## 2. Cost shares (derived, the 14 sessions on priced models)

~~~~
ds-cabinet-cloud-5: the Dyad System's README  claude-fable-5-1   reported      5.9 est(cw1.25x)      4.7 est(cw2x)      5.9 | shares out 22% cw 53% cr 25% | cr/out 226
ds: cabinet cloud-4 — token-efficiency audit  claude-opus-5-5    reported      1.6 est(cw1.25x)      1.2 est(cw2x)      1.6 | shares out 13% cw 60% cr 27% | cr/out 202
cabinet-cloud-3: (5fdc4e6e) #302 messaging ar claude-fable-5-1   reported     47.6 est(cw1.25x)     36.4 est(cw2x)     47.7 | shares out 19% cw 63% cr 19% | cr/out 200
cabinet-cloud-2: (92e3d665) work the un-close claude-fable-5-1   reported     92.7 est(cw1.25x)     74.2 est(cw2x)     95.5 | shares out 15% cw 60% cr 25% | cr/out 343
cabinet-cloud-1: (242a5502) d-work framework  claude-fable-5-1   reported     62.9 est(cw1.25x)     54.2 est(cw2x)     70.4 | shares out 17% cw 61% cr 22% | cr/out 264
cos: ds-cloud                                 claude-fable-5-1   reported    115.3 est(cw1.25x)     90.3 est(cw2x)    122.2 | shares out 9% cw 70% cr 21% | cr/out 447
ds: audit craft                               claude-sonnet-5-5  reported     31.7 est(cw1.25x)     27.7 est(cw2x)     31.7 | shares out 9% cw 34% cr 58% | cr/out 340
client-dyad-system: push the v0.1.0 release t claude-opus-5-5    reported      2.5 est(cw1.25x)      1.7 est(cw2x)      2.5 | shares out 6% cw 87% cr 7% | cr/out 127
ui-design craft implementation                claude-opus-5-5    reported      1.6 est(cw1.25x)      1.2 est(cw2x)      1.6 | shares out 7% cw 67% cr 26% | cr/out 357
asg-peter: dwork #272 continuation            claude-opus-5-5    reported    142.2 est(cw1.25x)    128.9 est(cw2x)    145.3 | shares out 15% cw 30% cr 55% | cr/out 369
ds: countersign-seeding                       claude-opus-5-5    reported    451.9 est(cw1.25x)    418.8 est(cw2x)    496.3 | shares out 14% cw 42% cr 45% | cr/out 323
ds: sysadmin craft                            claude-sonnet-5-5  reported   1737.7 est(cw1.25x)    630.0 est(cw2x)    743.3 | shares out 10% cw 41% cr 49% | cr/out 246
ds: syseng craft                              claude-sonnet-5-5  reported   1003.5 est(cw1.25x)    737.2 est(cw2x)    835.8 | shares out 7% cw 31% cr 62% | cr/out 450
ds: sysarch craft                             claude-sonnet-5-5  reported    290.3 est(cw1.25x)    184.2 est(cw2x)    215.7 | shares out 9% cw 39% cr 52% | cr/out 279
TOTAL reported 3987.3 est 2815.2 {'in': '0%', 'out': '10%', 'cw': '40%', 'cr': '49%'}
~~~~

## 3. Mining reports (verbatim; delegated read-only subagents, tree `b60056b`)

### Ledger and traces miner

~~~~
# Ledger mining for a token-efficiency audit

Read-only. Tree: `/home/user/ds-cc4` at `b60056b` (2026-10-17). Nothing in the repo was modified.
Scripts and their raw outputs are in this scratchpad directory
(`/tmp/claude-0/-home-user-dyad-system/216584db-f1aa-5051-85cf-6d32fd758702/scratchpad/`):

| script | run as | output |
|---|---|---|
| `mine_rows.py` | `python3 -I mine_rows.py /home/user/ds-cc4` (also writes `rows.json`) | `rows_out.txt` |
| `classify.py` | `python3 -I classify.py rows.json [--other]` | `classify_out.txt` |
| `batches.py` | `python3 -I batches.py` | `batches_out.txt` |
| `mine_files.py` | `python3 -I mine_files.py /home/user/ds-cc4` | `files_out.txt` |
| `trace_extra.py` | `python3 -I trace_extra.py /home/user/ds-cc4` | `trace_extra_out.txt` |
| `mine_incidents.py` | `python3 -I mine_incidents.py /home/user/ds-cc4` | `inc_out.txt` |

"Derived" means computed by me from bytes or heuristics, not measured by the system.

---

## 1. Rows (`agent-corpus/d-work/rows/[0-9]*.md`)

There are 323 row files with ids from 1 to 335. The 12 missing ids (28, 29, 63, 64, 72–79) are not on this tree. `rows/README.md` is excluded.

**By state:** done 227 · backlog 69 · archived 19 · planned 6 · open 2.

**Disposed entries per row** (split on `;`). There are 622 entries in all. Mean 1.93, median 2.

| entries | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| rows | 9 | 111 | 136 | 47 | 11 | 5 | 1 | 1 | 2 |

Mean entries by state: done 2.28, planned 1.67, archived 1.68, backlog 0.91, open 0.

**Entry kinds** (`<date> <Y|N> <word>`):

| kind | n | kind | n |
|---|---|---|---|
| Y done | 228 | Y archive | 19 |
| Y plan | 209 | Y release | 8 |
| Y backlog | 51 | N done | 6 |
| Y intake | 30 | Y merge | 4 |
| Y open | 26 | Y departure | 3 |
| N plan | 24 | one-off forms (Y shape, spinout, push, harness, re-plan, adopt, I4, …) | 16 |

Substring flags inside entries: `merges` 169, `batch` 160, `from #` 29 (inherited authorization), `revision` 24, `mandate` 14, `deferred` 4, `named in plan` 3, `relayed` 2, `landed` 1.

The `N` count is 30 out of 622 entries (4.8%). 24 of those are `N plan`. Plans are refused about once in every nine plan dispositions (24 N against 209 Y).

**Batch questions** (distinct date+kind+id-set; `batches.py`):
- Y plan: 21 batch questions covered 54 rows. Sizes were mostly 2; the largest was 10.
- Y done: 27 batch questions covered 82 rows. Sizes ran from 1 to 10, median 3.
- Y archive: 3 batch questions covered 19 rows, sizes 2, 3 and 14.

So about 36% of Y done entries (82/228) came through a batch, and about 26% of Y plan entries (54/209).

**Rows opened per day:** 30 days, 323 rows, mean 10.8 per day. The peaks were 09-16 (33), 10-15 (28), 10-10 (24), 09-18 (21) and 09-25 (21).

**Accreted vs prompted:**
- No row carries `mode: implicit`, so the field is unused so far.
- 42 rows carry an inherited authorization: `mandate` in disposed, `from #N's plan-Y`, or `named in plan`. Examples: #96, #97, #240, #257, #262–#284 (the incident-mode children of #259) and #303–#320 (children of #310 and #309).
- 75 rows were born by a disposition (first entry `Y backlog` or `Y open`), not by a prompt.
- 9 rows have no disposed entry.

**refs:**
- Mean 2.24 numbers per row, median 2, max 13. 28 rows have none.
- `parent #N` depth is at most 1: 39 child rows. Parents with the most children: #259 (23), #116 (9), #310 (7).
- Most-referenced rows: #116 (38, incident audit), #259 (29), #137 (29, incident play-book), #253 (15), #285 (14), #252 (12), #185 (12), #302 (11).
- The incident-hardening family is the gravitational centre of the ledger.

**Data-quality finding:** 6 rows (#129–#134) have the literal title `--backlog`. A flag was taken as a positional argument, which is incident mode G. #129's real title ended up in `refs`. Four of these rows are archived.

---

## 2. Work classes by title (`classify.py`)

**Method:** case-insensitive regexes over the title. The first match wins, in the order listed in `classify.py`:
1. malformed
2. landing
3. session sync
4. banked/archive
5. board reports
6. spin-up
7. incident
8. release
9. tests
10. trace
11. multi-session architecture
12. analysis Q&A
13. Rule/preference
14. guard/code
15. craft
16. docs

The keywords are stated in the script. The heuristic is coarse; for example, a "falsify X about tests" row lands in tests, not analysis. Only 6 rows fall through to "other".

| class | rows | share | done | backlog | archived | mean disposed entries | examples |
|---|---|---|---|---|---|---|---|
| incident records / hardening | 47 | 15% | 19 | 27 | 0 | 1.55 | #116–#125, #259, #262–#284 |
| test suite / performance | 45 | 14% | 39 | 4 | 2 | 2.00 | #107, #108, #155, #162–#165, #199, #203–#211 |
| multi-session architecture (cos/cabinet/presence/bus) | 38 | 12% | 27 | 10 | 0 | 1.84 | #252, #253, #285, #290, #302–#316 |
| release / version / drift | 33 | 10% | 27 | 2 | 3 | **2.52** | #13, #16–#21, #46, #67, #71, #90, #126, #241, #249 |
| analysis Q&A (falsify/evaluate/explain/audit/ADR) | 32 | 10% | 30 | 0 | 1 | 1.91 | #30, #35, #43, #142–#150, #154, #161 |
| guard / code / CLI change | 25 | 8% | 13 | 9 | 3 | 2.00 | #4–#9, #24, #25, #39, #250 |
| Rule / preference / vocabulary amendment | 25 | 8% | 9 | 11 | 5 | 1.76 | #17, #26, #34, #106, #113, #170 |
| session: banked?/archive/resume/stand-down | 12 | 4% | 12 | 0 | 0 | 1.75 | #234, #235, #238, #239, #242, #243, #255, #258, #325 |
| session: sync with remote | 11 | 3% | 11 | 0 | 0 | 1.64 | #59, #140, #141, #157, #167, #168, #233, #237 |
| landing / merge recovery | 11 | 3% | 11 | 0 | 0 | **2.73** | #196, #200, #245, #246, #249, #321, #322, #323 |
| session: spin-up / seat registration / clone | 10 | 3% | 8 | 0 | 0 | **3.00** | #151, #152, #293, #296, #297, #299, #331, #332 |
| craft work | 8 | 2% | 6 | 2 | 0 | 2.00 | #22, #36, #92, #97, #181 |
| d-work trace / measurement | 7 | 2% | 6 | 1 | 0 | 2.14 | #212–#215, #240, #247, #288 |
| session: board / status / id reports | 7 | 2% | 5 | 0 | 0 | 0.86 | #224, #225, #298, #324, #327, #328, #329 |
| other | 6 | 2% | 3 | 2 | 1 | 1.50 | #27, #47, #54, #136, #257, #289 |
| malformed (`--backlog`) | 6 | 2% | 1 | 1 | 4 | 1.00 | #129–#134 |

**Non-exclusive title tallies (`mine_files.py`):**
- `falsif*` 40
- tests/suite 50
- `incident mode` 33
- `releas*` 26
- `evaluate|explain|why` at the start 18
- `sync` 12
- `land`/re-land/recovery 8
- archive this/the session 7
- `banked` 6
- `rendered by hand` 4
- spin up 4
- board report 3

**Reading:**
- **Session housekeeping is one large, repetitive family.** Sync, "falsify 'all changes banked'", archive, resume, board report, id report, spin-up and landing recovery together account for 51 rows (16%). These are procedural and predictable.
  - "falsify 'all changes have been banked'" was asked 6 times: #234, #235, #239, #242, #243, #325.
  - "sync with remote" was asked 12 times.
  - The board report was "rendered by hand" 3 times: #298, #324, #327. By Rule-13 property 1, that is past the second-occurrence threshold for code.
  - Spin-up and landing recovery carry the highest disposition cost per row: 3.00 and 2.73 entries.
- **Release rows are disposition-heavy (2.52).** Drift, version bump and re-release form a recurring sub-loop: #67, #71, #90 and #126 are all "drifted, bump, re-release".
- **The incident family is the backlog.** 27 of the 69 backlog rows (39%) are incident rows. Most are the A–W mode children of #259.

---

## 3. Plan and provenance sizes (`mine_files.py`)

| store | files | total bytes | ~tokens (bytes/4, derived) | mean | median | p90 | max |
|---|---|---|---|---|---|---|---|
| plans (Agent prose) | 223 | 1,850,796 | ~462,700 | 8,300 | 5,538 | 17,113 | 81,177 (#252) |
| provenance (Operator words) | 310 | 107,950 | ~27,000 | 348 | 226 | 668 | 7,777 (#100) |

- **Top 10 plans (bytes):** #252 81,177 · #290 61,095 · #142 39,918 · #221 37,942 · #203 37,221 · #259 36,369 · #81 35,461 · #228 34,787 · #301 30,621 · #202 27,167.
- **Top 10 provenance records (bytes):** #100 7,777 · #252 3,182 · #302 2,902 · #297 1,857 · #152 1,821 · #249 1,591 · #290 1,193 · #148 1,136 · #203 1,086 · #221 1,008.
- **Ratio:** over the 223 ids that have both, plans are **20.5×** the bytes of the Operator's words. The Agent writes about 20 bytes of plan for every byte the Operator gives.
- **Plan revisions:** 194 plans carry no `Revision N` heading. 29 are revised: 11 once, 7 twice, 5 three times, 3 four times, 1 five, 1 six and 1 sixteen.
- **Provenance entries:** 227 prompts and 616 dispositions.
- **Concentration:** the top 10 plans hold 412 kB, 22% of all plan bytes. They are the architecture and ADR rows (#252, #142, #221), the meta-process rows (#290, #259, #202) and the test-refactor plans (#203, #228).

---

## 4. Traces (`agent-corpus/d-work/traces/*.md`; format per `dyad/playbooks/dwork-trace.md`)

There are 82 trace files. 63 have buckets; 19 are "Absent: no window", where no anchored provenance entry precedes a Done question.

**Buckets summed over the 63 traces** (`mine_files.py`):

| bucket | seconds | share of all | share of agent-side |
|---|---|---|---|
| operator (wait on a `Y/N:`) | 522,795 | 56.8% | — |
| inference | 214,724 | 23.3% | 75.5% |
| idle (wait, no `Y/N:`) | 112,605 | 12.2% | — |
| background | 28,009 | 3.0% | 9.9% |
| suite | 14,578 | 1.6% | 5.1% |
| git/local | 13,555 | 1.5% | 4.8% |
| guards | 11,908 | 1.3% | 4.2% |
| github | 823 | 0.1% | 0.3% |
| subagent | 495 | 0.1% | 0.2% |
| other (Read/Edit/Write/Grep…) | 146 | 0.0% | 0.1% |
| **total** | 919,638 (255.5 h) | | agent-side 284,238 s (79.0 h) |

**Outlier:** #261 ("resume after the session exited") alone holds 172,655 agent-side seconds. That is a 48-hour lost segment booked as inference.

**Excluding #261** (`trace_extra.py`), agent-side is 111,583 s:

| inference | background | suite | git/local | guards | github | subagent | other |
|---|---|---|---|---|---|---|---|
| 40.7% | 24.0% | 12.7% | 10.9% | 10.3% | 0.7% | 0.4% | 0.1% |

- Mechanical (suite + guards + git/local + github + subagent + other) is 35%. Test gates (suite + guards) are 23%.
- The median per-trace inference share of agent-side is 39%.
- **Top-1 bucket per trace:** operator 36 · inference 15 · suite 4 · idle 3 · guards 3 · background 2.
- **In top 3:** inference 56 · operator 55 · suite 21 · guards 19 · git/local 14 · background 11.
- **Agent-side per trace:** median 819 s, mean 4,512 s, p90 5,180 s. The largest are #261 172,655 s, #285 11,458, #290 10,041, #301 10,025 and #202 8,134.

**Counts columns** (77–82 traces report them):

| count | sum | mean | median | max |
|---|---|---|---|---|
| commits | 273 | — | 2 | 20 |
| tool calls | 2,638 | 34 | 14 | 228 |
| output tokens | 2,716,254 | 35.3k | 11.9k | 337k (#290) |
| full-suite runs | 150 | — | 0 | 32 (#202) |
| guards-only push gates | 405 | 5.3 | 3 | 37 |

- **Ledger-only commits:** 259 of the 273 commits (**95%**). In the traced windows, almost every commit is clerical ledger bookkeeping.
- **Guards-only push gates vs full-suite runs:** 405 against 150. Pushes are dominated by ledger pushes.
- **Delegated share:** 28 traces report it, and 24 of those are 0%. Mean 1.6%, max 29.6%. Subagent time is 0.2% of agent-side, so `delegation: plan-and-execute` barely fires in traced d-works.
- **Test-exec/inference ratio:** n=10, median 1.05.

**Output tokens by title class** (traced rows only; shared turns may double-count):

| class | traces | output tokens | mean | mean tool calls |
|---|---|---|---|---|
| multi-session architecture | 16 | 858,487 | 53.7k | 39 |
| test suite / performance | 14 | 519,659 | 37.1k | 44 |
| session banked/archive/resume | 12 | 368,124 | 30.7k | 28 |
| session spin-up / seat | 4 | 361,281 | **90.3k** | 95 |
| release / version | 4 | 237,164 | 59.3k | 72 |
| Rule / preference | 2 | 154,449 | 77.2k | 69 |
| analysis Q&A | 5 | 55,081 | 11.0k | 12 |
| incident records | 3 | 49,955 | 16.7k | 16 |
| landing / recovery | 6 | 18,506 | 3.1k | 5 |
| board/status reports | 5 | 15,900 | 3.2k | 5 |
| sync with remote | 2 | 11,760 | 5.9k | 7 |

- **Top output-token traces:** #290 337k · #292 205k · #261 203k · #223 159k · #301 159k · #202 153k · #241 122k · #212 109k.
- **Session housekeeping is expensive:** banked/archive plus spin-up together cost **729k output tokens over 16 traces**, about 27% of all traced output tokens, for work with no new design content.

**Limits:**
- Inference is a wall-clock gap and overstates the model's time.
- 19 traces have no window.
- Shared batch turns are counted whole in each trace.
- Output tokens cover the window only and are not deduplicated across traces.

---

## 5. Incidents (`agent-corpus/audits/INCIDENTS.md`; `mine_incidents.py`)

**188 rows:** 86 in September and 102 in October.
- **Top days:** 10-15 (25), 09-16 (17), 10-09 (16), 10-14 (14), 09-29 (13), 10-05 (13).
- **d-works with the most incident rows:** #256 (10), #259 (9), #297 (9), #290 (8), #114 (5), #221 (5), #22 (4), #116 (4), #166 (4), #223 (4).
- The rows are long: 192,680 characters of what/cause/consequence (~48k tokens, derived). Mean 1,025 characters per row, max 3,653.

**Keyword groups** (non-exclusive, over what + cause; regexes in the script):

| group | rows | e.g. |
|---|---|---|
| a guard/hook FAIL or refusal is mentioned (broad) | 83 | #156, #126, #114, #1, #16 |
| VERSION / tag / bundle / zone ordering | 38 | #156, #126, #114, #13 |
| act before the Y (self-ratify, plan-before-ask, never gave) | 32 | #17, #18, #22, #32 |
| ledger row form (state, id, title, disposed, collision) | 29 | #1, #16, #30, #35, #116 |
| stale local view / unfetched origin | 26 | #127, #3, #22, #26 |
| concurrent session interference | 25 | #3, #22, #30, #27 |
| git write used as a read (checkout/reset/restore) | 20 | #127, #114, #1, #110 |
| provenance / disposition record mismatch | 18 | #114, #26, #27, #185 |
| merge conflict / rebase | 16 | #22, #166, #196, #200, #242 |
| value from memory / wrong number / wrong object | 15 | #186, #223, #242, #256 |
| delegation / subagent | 15 | #81, #114, #188, #192 |
| test suite red from hardcoded enumeration | 14 | #156, #114, #137, #166 |
| push rejected / race on main | 12 | #178, #232, #234, #242 |
| flag parsed as positional (`--help`, `--backlog`) | 8 | #13, #116, #203, #297, #301 |
| environment (py 3.11, CI 403, tmp inodes) | 7 | #13, #22, #256, #202 |
| lost turn / session exited / compaction | 6 | #114, #251, #259, #297 |

**Outcomes:**
- 49 rows name a recovery act in their consequence (re-cut, new row, fresh plan/branch/PR, redone, restored, re-run). These are the rows that cost extra commits and inference.
- 57 say the error was caught before push, commit or main.
- 12 mention main being affected.

**The A–W failure-mode taxonomy** (2026-10-10, 140 rows; `audits/2026-10-10-incident-failure-modes.md`). The largest modes:

| mode | name | rows |
|---|---|---|
| A | acting before the authorizing disposition | 13 |
| C | value stated from memory | 13 |
| Q | an obligation no mechanism reads | 12 |
| M | no legal order, no verb | 11 |
| T | stale or partial view of shared state | 10 |
| D | wrong object read | 9 |
| K | plan incomplete against its own text | 8 |
| R | derived key that does not identify | 7 |
| H | present enumeration pinned as an invariant | 6 |
| U | the World moved | 6 |

Fence status across the 23 modes: **2 fenced** (F, W), **15 closed only by a backlog row** (#262–#284, most still `backlog`), **4 open** (I, K, M, T), **2 unfenceable** (B, U).

Since the taxonomy, only 31 rows carry an explicit `mode X` label in their text. The most frequent label is G (8).

**Recurring and mechanizable incidents:**
- **The record-then-merge / landing loop** (merge conflict, rebase, tail-append race, re-land). It was #202's amendment (12 incident rows) and caused recovery rows #196, #200, #245, #246, #321, #322 and #323.
- **Self-ratify / act-before-Y (32).** This is inference-only by design.
- **Stale view / unfetched (26) and concurrent sessions (25).** These are mechanizable at session start and before allocation.
- **Flag-as-positional (8)**, which is still producing rows (#297, #301).

---

## 6. Earlier efficiency audits and what landed

### #154 — `audits/2026-09-24-performance-bottlenecks.md`

Frequencies over one session's 1,503 Bash calls:
- `git push` 321, `git commit` 281, `unittest` by hand 134 (3,894 s, none required).
- `check --evidence` 79 against 29 merges (2.72×).
- `dwork new`/`state` 86/96.
- Bash was 99.2% of tool time but only about a third of busy time; the rest was model time.
- Main thread: 1.03 B tokens and $519, against a 7% delegation share.

| # | candidate | outcome |
|---|---|---|
| 1 | never hand-run a whole test root | **landed**: #155 (`dyad check --tests`, done), #158/#159 (directive released, done), Rule-12 property 2 |
| 2 | `check --evidence` once per merge | conduct only; no row; not mechanized |
| 3 | leave push frequency alone | taken (no change) |
| 4 | the delegation axis is where the minutes are | became #188/#192/#195 (falsify delegation conduct, done). The traces still show 0% delegation in 24 of 28 |

### #161 — `audits/2026-09-25-optimization-opportunities.md` (plan `plans/161.md`)

| cand. | what | est. saving | row | state |
|---|---|---|---|---|
| C2 | push-gate suite memo | ~2.0 h/week | #162 | **done** (under #199 N2, commit 2fc6dd2) |
| C4 | one install per module in tests | 1.2–2.2 h/week | #163 | **done** (under #199) |
| C1 | empty range skips the suite | bounded | #164 | **done** |
| — | worktree GIT_DIR isolation defect found on the way | — | #165 | **done** |
| C3 | evidence pays the package checks twice (2.4%) | — | — | refuted; not taken |
| C5 | run roots in parallel | ≤9.4 s | — | refuted as a priority |
| C6 | push frequency | — | — | unchanged |

Follow-ons:
- #176 (authoring suites at an operating push gate) is **done**; it became the installed-root skip in Rule-12 property 2.
- #180, #183–#187, #190 (profiles and bytecode) are all **done**.
- #199 (holistic refactor over #162–#165 and #176) is **done**.

### #204 — `audits/2026-10-02-test-execution-profile.md`

Main-thread active time split about 49% inference and 49% mechanical. Direct test runs were 71% of main tool time. Output was ≥1.80 M tokens; cache-read was 1.03 B.

None of its 8 ranked "proposed backlog rows" was opened as a row. They were followed by a falsify chain: #205 batch scenarios, #206 signing, #207/#208 batch signing/commits, #209 single d-work, #210/#211 skip the suite for record/ledger-only pushes. All are done.

| # | candidate | outcome (checked in code at `b60056b`) |
|---|---|---|
| 1 | single-guard path (`dyad check --guard <label>`); 55 full checks, 5.7k s, often run to grep one guard line | **not landed**: `package.py` has no such flag (flags: `--guards --pr --evidence --tests --list --pre-push`) |
| 2 | memo never hit at push (0/11) | no row. `check_rule_12` writes the memo after any full clean pass (package.py:256), unchanged since #162. Hit rate not re-measured |
| 3 | unsigned fixture commits (26–48 s/run) | **landed** via #206: commit 6aa1a94, `suite_env` sets `commit.gpgsign=false` (package.py:430) |
| 4 | in-process CLI calls in tests (20–30 s/run) | no row; not evident (only 4 test files use `redirect_stdout`) |
| 5 | subagent polling loops → notifications/Monitor | no row; conduct only |
| 6 | git fixtures built once / fast-import (27 s/run) | no row; no `fast-import` in `dyad/tests` |
| 7 | parallel core root on 4 vCPU | no row; no pool in `package.py` |
| 8 | manifest AST scan run twice per pass (~1 s/gate) | no row; no cache found in `manifest.py` |

Related later work:
- #203 test reduction, **done**.
- #227 promoted suite-only checks to guards, **done**.
- #212–#216 created the trace (**done**). It is the instrument §4 reads.
- #326 sweep of the suite temp root after inode exhaustion, done on 10-15.
- #331 and #333 (this token-efficiency evaluation) are **planned**.

---

## 7. Candidates this data suggests (for the audit to falsify, not adopted)

1. **Mechanize session housekeeping.** It is 51 rows (16%) and about 729k output tokens in the 16 traced banked/archive/spin-up d-works.
   - A `dyad session bank-check` would cover the 6 repeats of "falsify all changes banked": unpushed branches, a dirty tree, unlanded `Y done` heads, open PRs.
   - A `dyad board` would cover the 3 hand-rendered board reports.
   - A scripted `sync` report would cover the 12 sync rows.
   - The spin-up/seat run-book is the highest disposition cost per row (3.00).
2. **Make the ledger commit cheaper, not rarer.** 95% of commits in traced windows are ledger-only, and there are 405 guards-only gates against 150 suites. Each record is a CLI call plus a commit plus a guarded push. Fold `dwork state … -d` plus commit plus push into one verb.
3. **Inference dominates agent-side (41–76%), and delegation does not fire** (0% in 24 of 28 traces). Plans average 8.3 kB, 20× the Operator's words, and the top 10 plans hold 22% of the plan bytes. Plan length is the largest Agent-authored text stream (~463k tokens derived, before revisions are re-read).
4. **#204 #1, the single-guard path, is still open.** It is cheap, and the suite plus guards are 23% of agent-side time excluding #261.
5. **Landing/recovery loop.** 11 rows at 2.73 entries each, plus 16 rows on merge conflict/rebase. These sit on the tail-append files (INCIDENTS.md) that the `merge-disposition` note already names.
6. **Flag-as-positional** (6 `--backlog` rows, 8 incidents). The CLI could refuse a title or `-d` value that starts with `--`.
~~~~

### Git and tools miner

~~~~
# git + tool mining — token-efficiency audit input (read-only, worktree /home/user/ds-cc4, origin/main)

Sentinel: covalent-sentinel-2026-09-12. Nothing in the repo was modified.
Scripts: `mine.py` (this scratchpad; `python3 -I mine.py`, raw output `partA.txt`) plus the ad-hoc
`git log` / `git grep` one-liners quoted inline. Zones per `python3 dyad/guards/infra/containment.py zones`.
Main parse: `git log origin/main --numstat --no-renames --format=<H,P,aI,cI,s,b>`.

## A1. Volume

- 1,416 commits, 2026-09-14 .. 2026-10-17 (30 active days): **418 merges, 998 non-merge**.
- Non-merge by zone: **ledger-only 737 (73.8%)**, agent (non-ledger) 179, craft 36, infra 30,
  workstation 9, preferences 7. No unclassified, no multi-zone non-merge commit.
- Merges whose whole diff (`git diff p1...p2`) is ledger-only: **190 of 418**; per ISO week
  (`git log --merges --date=format:%G-W%V`, L=ledger-only / O=other):
  W38 14/71, W39 64/59, W40 41/37, W41 56/31, W42 15/30.
- Per day (total / merges / ledger-only non-merge), peaks: 10-15 129/13/97, 10-05 123/58/49,
  09-16 120/32/63, 09-25 95/30/46, 09-24 93/35/48, 09-22 88/31/25. Mean ~47 commits/active day.
  Full table: `partA.txt`.
- Commit-message text: ledger-only 737 msgs, median 209 chars, **254k chars total**; other 261 msgs,
  median 601, 222k total. i.e. more message text is written for clerical commits than substantive ones.

## A2. Recurring subject shapes (first match wins; regexes in mine.py `shapes`)

| shape | count |
|---|---:|
| merge: `Merge pull request #N` (hosted) | 312 |
| merge: other — `Merge PR #N:`/`Merge ledger PR #N` custom 70, `(#N)`-titled 21, main→branch / branch→branch 15 | 106 |
| ledger: #N opened (… plan stored, presence …) | 233 |
| ledger: #N planned / plan-Y (+ presence touched) | 168 |
| ledger: #N Done-Y recorded (… with its trace) | 123 |
| ledger: #N done / close act ("landed at <sha>") | 48 |
| ledger: plan revision / corrected | 44 |
| ledger: backlog / archived / blocked | 15 |
| ledger: presence / seat only | 15 |
| ledger: other | 85 |
| incident rows (subject says incident) | 54 |
| version bump / release / re-pin / BUNDLE | 25 |
| workstation change-log | 3 |
| substantive (d-work #N / zone-prefixed work) | 185 |

- **Clerical : substantive ≈ 4.3 : 1** by subject (1,149 vs 267) and 4.43 : 1 by path
  (737 ledger-only + 418 merges = 1,155 vs 261 substantive non-merge).
- 65 non-merge subjects mention presence/seat; 180 commits touch `d-work/sessions/` (10 touch only it).
- 71 commit subjects say "trace"; 82 trace files on main (mean 70 lines, 5,756 lines total).

Per d-work (commit attributed when it names exactly one id via `d-work #N`, `ledger: #N`, or a
trailing `(#N)`; 1,139 of 1,416 attributed, 232 d-works):
- commits per d-work: **median 4, mean 4.91, p75 6, p90 9, max 29**;
  histogram 1:35 2:25 3:32 4:26 5:35 6:23 7:20 8:8 9:8 10:6 11:5 12:3 13:1 15+:5.
- **ledger-only commits per d-work: median 3, mean 3.03, p90 5, max 13**; merges 0.81; substantive
  mean 1.07, median 1. **93 d-works have zero substantive commits** (pure-ledger rows).
- heaviest: #199 29 (L6/M15/S8), #259 20 (L10/M2/S8), #203 18, #175 18, #100 16 (L10), #301 13 (L13/S0),
  #297 12, #241 12 (L10/S1), #114 12, #202 11, #249 11, #290 11.
- Rows on main: 324 (done 227, backlog 69, archived 19, planned 6, open 2); plan files 223 (101 rows with
  none). Provenance entries 843 (616 disposition, 227 prompt) → 1.9 dispositions per row.
  **`mode: implicit` rows: 0** — the mandate/accretion path (#290) has not yet been used once.

## A3. Files

Top 30 by non-merge commits (commits, lines churned):
```
  80     205  agent-corpus/audits/INCIDENTS.md
  40    2146  dyad/tests/test_package.py
  30     152  agent-corpus/d-work/sessions/web-sysarch.md
  28    1546  dyad/scripts/package.py
  24     133  BUNDLE.md
  20      39  dyad/VERSION
  18     139  dyad/vocabulary/VOCABULARY.md
  16     498  dyad/rules/RULE-3-d-work.md
  15     358  agent-corpus/d-work/plans/301.md
  14     506  dyad/falsification/rules/rule-3-d-work.md
  13     733  dyad/scripts/dyadlib.py
  13     734  dyad/tests/guards/agent/test_references.py
  12      74  agent-corpus/d-work/sessions/ds-cabinet-cloud-2.md
  12     397  dyad/tests/test_dyadlib.py
  11     723  dyad/guards/agent/references.py
  11     444  dyad/tests/guards/craft/test_crafts.py
  10      62  agent-corpus/d-work/sessions/ds-cabinet-term-1.md
  10     471  dyad/tests/guards/agent/test_rows.py
  10     369  dyad/falsification/rules/rule-11-distribution-structure.md
  10     239  dyad/rules/RULE-11-distribution-structure.md
  10      72  agent-corpus/d-work/sessions/web-sysadmin-scope.md
  10      19  crafts/sysarch/VERSION
  10      44  agent-corpus/d-work/sessions/dev-main.md
   9     487  dyad/guards/agent/rows.py
   9      55  agent-corpus/d-work/provenance/241.md
   9      26  agent-corpus/d-work/rows/241.md
   8      53  agent-corpus/d-work/provenance/301.md
   8      24  agent-corpus/d-work/rows/301.md
   8     336  dyad/tests/test_craft.py
   8     318  dyad/guards/infra/containment.py
```
By kind (file-touches / lines): rows 904/4,022; provenance 830/5,816; **plans 382/23,533** (largest
churn of anything in the repo); agent-other 261/17,295; dyad/tests 206/8,852; sessions 180/1,092;
traces 83/5,814; dyad/guards 88/4,365; dyad/scripts 70/4,375; dyad/rules 82/1,948; INCIDENTS.md 80/205.
Plan files: 223, 21,101 lines, median 68, p90 178, max 832 (all hand-written; no command writes one).

Co-change sets (kinds per non-merge commit), top:
```
 247  provenance+rows                 (dwork state/new)
 134  plans+provenance+rows           (open with plan)
  95  provenance+rows+sessions        (plan-Y + presence touch)
  90  plans                           (plan revisions)
  59  plans+provenance+rows+sessions
  55  provenance+rows+traces          (Done-Y record act)
  37  agent:other   30 infra:other   25 INCIDENTS.md   18 rows   14 falsification
  13  INCIDENTS.md+agent:other        10 sessions       9 agent:other+dyad/rules
```
Non-ledger pairs: package.py+test_package.py 18; INCIDENTS.md+test_package.py 14; INCIDENTS.md+package.py 9;
RULE-3 + its falsification record 8; RULE-11 + record 7; RULE-3+VOCABULARY 5; sysarch/VERSION + its test 5.
Version files: 68 non-merge commits touch `dyad/VERSION`, `crafts/*/VERSION` or `BUNDLE.md`; 50 tags.

## A4. Recovery / rework signals (non-merge subjects; subject+body in 2nd column)
```
fix 18/84  correct 27/70  revert 1/10  re-<verb> 25/71  rebase 4/19  incident 83/193
conflict 4/19  amend 11/58  recover 5/11  resolve 6/47  retry|again 4/73
any pattern in subject: 163 (16.3% of non-merge)
```
- 22 subjects re-record / re-ask / rebased / re-plan / re-touch / re-pin (e.g. 5822bf4 "#202 Done-Y
  re-recorded on the rebased head 0a4060e").
- 34 non-merge commits have committer-date − author-date > 5 min (rebased/amended; 6 ledger).
- 15 main→branch / branch→branch merges, incl. a 7-merge chain on 10-01 for #199's landing
  ("INCIDENTS rows kept in date order") — tail-append conflicts on INCIDENTS.md.
- 44 "plan revision / corrected" ledger commits; 90 plans-only commits.
- INCIDENTS.md: 80 commits, but only 205 lines — ~2.6 lines per commit, i.e. one row per commit,
  each a separate tail-append that conflicts across concurrent sessions.

## A5. PRs
- 312 `Merge pull request #N` commits (PR #1..#414), plus ~70 `Merge PR #N:` / `Merge ledger PR #N`
  custom-subject merges and ~21 `(#N)`-titled merges → ~400 PR merges.
- Commits per PR (`git rev-list --no-merges p1..p2`, hosted merges): **median 1, mean 1.17, p90 2,
  max 5; 275 of 312 are 1-commit PRs.**
- Hours first commit → merge: **median 0.11 h, p75 0.79, p90 8.7, max 49.6; 241 of 312 under 1 h.**
- **126 of 312 hosted PRs are ledger-only** (whole diff under agent-corpus/d-work/), 118 subjects say
  "ledger"; zones of the rest: agent 121, craft 27, infra 26, workstation 8, preferences 4.
  These exist because a session branch fence forbids the direct push Rule-3 prescribes (#23); the
  `ledger-pr-merge: agent` preference (d-work #66, 2026-09-18) removed the question but not the PR.

## B6. Tool inventory — what each mechanizes

CLI (`dyad/bin/dyad --help`):
| verb | mechanizes |
|---|---|
| `check` | full run: invariant pass, Rule-11 structure, Rule-12 suites, every guard |
| `check --list` | prints the guard registry |
| `check --guards [--pre-push]` | the pre-push gate: guards + transaction guards over pushed refs, suite memo skip |
| `check --pr <base> [<head>]` | Rule-1 whole-diff PR check before opening a PR |
| `check --tests [<target>]` | one suite/module/method the runner's way (~39 s vs ~120 s) |
| `check --evidence` | the evidence block (head, tree, dirty, all lines, sha256) for Done |
| `build` / `install <repo>` | core-craft archive / idempotent install + registry row |
| `bundle check|build` | BUNDLE.md vs craft VERSIONs; builds every component |
| `craft new|list|check|export|install` | Tended-craft scaffold, listing, guard, export, install |
| `ledger` | renders LEDGER.md from rows |
| `dwork new [... --mandate <id>]` | allocate id, write row + provenance entry 1 (prompt / disposition / mandate) |
| `dwork state <id> <s> [-d --said --prompt -r]` | transition + `disposed` entry + provenance entry in one write |
| `dwork retire <ids> -d --said` | retirement form over k rows (batch suffix composed) |
| `dwork list [--state] [--craft]` | board listing |
| `dwork trace <id> [--transcript] [--out]` | the d-work trace (timeline, buckets, bottleneck) |
| `session touch [-r] [-f] | list` | presence file write / list with same-root flag |
| `project <surface> | --list` | run a sysarch projector |
| `runbook check|list|run|new` | run-book commands through the runner, recording an event |

Guards (`dyad check --list`, 24): agent/{frame, plans, provenance*, prs*, records, references, rows*,
rules, sessions, traces, vocabulary}; craft/crafts; infra/{bundle, containment*, manifest};
preferences/preferences; sysadmin/{changelog, events*, ops_scripts, runbooks}; sysarch/registry;
syseng/{invariants, naming, tests}  (* = transaction guard). All are checks: none writes a record.

Play-books (`dyad/playbooks/`) → run-books (`dyad/runbooks/`, same names):
| play-book | recurring decision |
|---|---|
| d-work | which transition is legal, its input, which record it writes; steps open/plan/authorize/execute/evidence/record/complete/defer/resume |
| disposition-digest | how many Operator questions a d-work spends; mandate scope; retirement |
| dwork-trace | where a d-work's time went (trace) |
| incident-hardening | group incidents into failure modes, pick fences |
| audit | the standing whole-system audit |
| craft-instantiation (run-book `craft.md`) | new craft vs new dyad system |
| ds-report-incidents | redacted incident report for third parties |
Run-book events recorded on main: **6 total** (dwork-trace 3, incident-hardening 3) — the d-work
run-book has never been run through the runner; the native commands are used (by design, #247).

Scripts: `dyad/scripts/package.py` (runner/CLI), `dyadlib.py` (paths, rows, registry, INPUTS/TRANSITIONS),
`distribute.py` (one build/install path), `craft.py` (craft CLI), `runbook.py` (run-book runner+events),
`trace.py` (trace), `incidents.py` (incident-log parser), `hostadapter.py` (host facts), `livetest.py`
(scratch-repo test support); `crafts/countersign/scripts/levels.py` (test-level check),
`crafts/disclosure/scripts/redaction.py` (+rules: redaction for reports).

**No script runs `git commit`, `git push`, `git fetch`, `git rebase`, `git merge` or opens a PR**
(`grep -nE "git commit|'push'|'rebase'|'fetch'|gh pr|'merge'" dyad/scripts/*.py` → only livetest's
scratch commit). Every one of the 1,416 commits had its staging, message, push and (for 400) PR/merge
done by the Agent by hand.

## B7. Commit shapes → producing tool; hand-made sequences flagged

| shape (count) | tool that writes the files | done by hand each time |
|---|---|---|
| opened (233) | `dwork new --prompt-file` writes row+provenance | prompt file, plan file (68 median lines, no skeleton), presence touch, `git add`/commit message (~209 chars), push; if fenced: branch, PR, merge |
| planned (168) | `dwork state planned -d "Y plan" --said-file` + `session touch -r` (run-book `authorize`) | said file, commit, push/PR/merge; 95+59 commits co-change sessions |
| Done-Y record (123) | `dwork state <cur> -d 'Y done (merges PR #a at <head>)'` + `dwork trace --out` | composing the entry with PR numbers and heads, commit, push |
| merge of PR (312+70+21) | none (hosting / `git merge --no-ff`) | PR body, merge call, heads-unchanged check vs the Y |
| close (48; 6 since #202) | `dwork state <id> done` | watching for the head to land, commit "landed at <sha>", push/PR |
| ledger PRs (126 hosted, 190 ledger-only merges total) | none | branch, PR, merge for content that Rule-3 says goes direct to main |
| plan revisions (44) / plans-only (90) | none | edit in place, commit |
| presence-only (15; 180 touches) | `session touch` | commit/push of the touch |
| incident rows (54 subjects, 80 file commits) | `incidents.py` parses only | row text, date-ordered tail insert, conflict resolution on concurrent landings (10-01 merge chain) |
| version/BUNDLE (68 commits, 50 tags) | `bundle check` detects drift | bump VERSION, update BUNDLE row, tag, release sequencing across zones |
| rebase/re-record (22 + 34 rewritten) | none | fetch → rebase → re-run `check --evidence` → re-record Done entry on new head → re-ask |
| evidence block | `check --evidence` | paste verbatim into reply (not in git; unmeasurable here) |
| trace | `dwork trace --out` | invoking at the right moment, preview paste |

Documented-but-manual multi-step sequences (`dyad/playbooks/d-work.md`, lifecycle 1–6 and run-book):
1. **Done three acts** — record (`dwork state` + `trace --out` + commit) → merges (per PR) → close
   (`dwork state done` + commit after the head is on main). Run-book has `record` and `complete` steps,
   but no step does the commits, the merges, or the "is the head on main yet" wait; 3+ commits and
   ≥1 merge per d-work, more with ledger PRs (#308: 6 merge+ledger commits for 1 substantive).
2. **Open** — `dwork new` + hand-written plan + presence + commit ≈ 134 plans+provenance+rows commits.
3. **Plan-Y** — `dwork state planned` + `session touch` + commit (95 commits carry exactly that triple).
4. **Branch-fenced ledger write** — branch → push → PR → merge for a ledger-only diff: 126+ PRs.
5. **Commit message composition** — every ledger commit's subject is free prose re-deriving
   "#N <event> on the Operator's <Y|prompt>, <side effects>" (~254k chars over 737 commits); the
   event is already known to `dwork new|state`, which could emit it.

Mechanization candidates ranked by commit volume:
- a `dwork ... --commit` (or `dyad ledger commit`) that stages exactly the files the verb wrote and
  writes a canonical subject from the transition table → covers ~737 commits / ~254k chars of messages;
- a ledger-push helper that does fetch → rebase-on-main → re-run guards → push, falling back to a
  ledger PR + self-merge under `ledger-pr-merge: agent` → removes the 126–190 ledger PRs/merges by hand;
- `dwork done-record|done-close` that composes the `Y done (merges PR #a at <head>)` entry from
  `gh`/git, and a `dwork close --when-landed` that checks ancestry and commits → the 123+48 Done commits;
- a `dwork new --plan-skeleton` writing `PLAN_PARTS` headings + base commit + files touched placeholder
  (223 plans; `plans.py` already parses the parts) — saves skeleton, not inference;
- an incidents append tool that inserts in date order (80 single-row commits; merge-chain conflicts);
- a release/bump helper (68 VERSION/BUNDLE commits, 50 tags) driven by `bundle check`'s drift output.
Delegable (subagent-draftable, per `delegation: plan-and-execute`): plan drafts (23.5k lines),
falsification records (65 commits), incident-row text, trace previews; not delegable: commits, pushes,
PRs, merges, rows (Rule-3 Scope).

Limits: PR bodies, chat replies (evidence block, Done questions) and force-pushed/abandoned branch
history are not in `origin/main`, so the reply-side token cost is not measured here; per-d-work
attribution misses 277 commits naming no or several ids; shape regexes are heuristic (first-match).
~~~~

## 4. Mining scripts (verbatim text)

### mine_rows.py

~~~~
"""Mine d-work rows. Usage: python3 -I mine_rows.py <repo-root>"""
import sys, os, re, glob, statistics, collections, json

root = sys.argv[1]
rowsdir = os.path.join(root, "agent-corpus/d-work/rows")
rows = {}
for p in glob.glob(os.path.join(rowsdir, "[0-9]*.md")):
    d = {}
    for line in open(p, encoding="utf-8"):
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            if k in ("id", "title", "opened", "state", "disposed", "refs", "mode") and k not in d:
                d[k] = v.strip()
    rows[int(d["id"])] = d

out = {}
C = collections.Counter
print("rows", len(rows), "ids", min(rows), "-", max(rows))
print("\n## state"); print(C(r["state"] for r in rows.values()).most_common())

def entries(r):
    s = r.get("disposed", "").strip()
    return [e.strip() for e in s.split(";") if e.strip()] if s else []

n = [len(entries(r)) for r in rows.values()]
print("\n## disposed entries per row: dist", sorted(C(n).items()), "mean %.2f median %s total %d" % (statistics.mean(n), statistics.median(n), sum(n)))
for st in sorted(set(r["state"] for r in rows.values())):
    ns = [len(entries(r)) for r in rows.values() if r["state"] == st]
    print("  state %-9s n=%3d mean entries %.2f" % (st, len(ns), statistics.mean(ns)))

kinds = C(); flags = C()
for r in rows.values():
    for e in entries(r):
        m = re.match(r"(\d{4}-\d\d-\d\d)\s+(Y|N)\s+(\S+)", e)
        if not m:
            kinds["<unparsed>"] += 1; continue
        yn, word = m.group(2), m.group(3).rstrip("(,")
        kinds[f"{yn} {word}"] += 1
        low = e.lower()
        for f in ("batch", "mandate", "merges", "revision", "landed", "named in plan", "from #", "deferred", "relayed"):
            if f in low: flags[f] += 1
print("\n## entry kinds"); print(kinds.most_common(25))
print("## entry flags (substring)"); print(flags.most_common())

print("\n## opened per day")
perday = C(r["opened"] for r in rows.values())
for d, c in sorted(perday.items()): print(" ", d, c)
print("  days", len(perday), "mean/day %.1f max %s" % (statistics.mean(perday.values()), max(perday.items(), key=lambda x: x[1])))

# accreted / inherited authorization
def accreted(r):
    d = r.get("disposed", "").lower()
    return r.get("mode") == "implicit" or "mandate" in d or "named in plan" in d or "from #" in d and "plan-y" in d
acc = [i for i, r in rows.items() if accreted(r)]
print("\n## accreted/inherited-authorization rows", len(acc), "mode=implicit:", sum(1 for r in rows.values() if r.get("mode") == "implicit"))
print("  ids", acc)
# prompted vs disposition-born
born_backlog = [i for i, r in rows.items() if entries(r) and re.search(r"\b(Y|N) (backlog|open)", entries(r)[0])]
print("  rows whose first entry is a 'Y backlog'/'Y open' disposition (disposition-born):", len(born_backlog))
noent = [i for i, r in rows.items() if not entries(r)]
print("  rows with no disposed entry:", len(noent))

# refs depth: parent chains via 'parent #N' or first ref
def parents(r):
    refs = r.get("refs", "")
    m = re.search(r"parent #?(\d+)", refs)
    return int(m.group(1)) if m else None
childcount = C()
depths = C()
for i, r in rows.items():
    d, cur, seen = 0, r, set()
    while True:
        p = parents(cur)
        if p is None or p in seen or p not in rows: break
        seen.add(p); d += 1; cur = rows[p]
    depths[d] += 1
    p = parents(r)
    if p: childcount[p] += 1
print("\n## refs: 'parent #N' depth dist", sorted(depths.items()))
print("  parents with most children", childcount.most_common(8))
nrefs = [len(re.findall(r"\d+", r.get("refs", ""))) for r in rows.values()]
print("  refs numbers per row: mean %.2f median %s max %d; rows with 0 refs %d" % (statistics.mean(nrefs), statistics.median(nrefs), max(nrefs), nrefs.count(0)))
inbound = C()
for r in rows.values():
    for x in set(re.findall(r"\d+", r.get("refs", ""))): inbound[int(x)] += 1
print("  most-referenced rows", [(i, c, rows[i]["title"][:50]) for i, c in inbound.most_common(8) if i in rows])

json.dump({str(k): v for k, v in rows.items()}, open(os.path.join(os.path.dirname(__file__), "rows.json"), "w"))
~~~~

### classify.py

~~~~
"""Classify row titles by keyword heuristics (first match wins). Usage: python3 -I classify.py <scratch>/rows.json"""
import sys, json, re, collections

rows = json.load(open(sys.argv[1]))
CLASSES = [
    ("malformed title (--backlog)", r"^--backlog$"),
    ("landing / merge recovery", r"^land |re-land|recovery of PR|^rebuild #|PR #\d+ is stale|why haven't you pushed"),
    ("session: sync with remote", r"^sync\b|\bsync (local|with)"),
    ("session: banked?/archive/resume/stand-down", r"banked|archiv(e|ing) (this|the)|archiving|stand down|^resume|^final verification|blocks archiving"),
    ("session: board/status/id reports", r"board report|^report |report open rows|^show the"),
    ("session: spin-up/seat registration/clone", r"spin up|^assign|registration of seat|^clone |^seed |establish this checkout|^cabinet ds-"),
    ("incident records / hardening", r"incident"),
    ("release / version / drift", r"releas|\bVERSION\b|drift|\bbump\b|upgraded|\btag\b"),
    ("test suite / performance", r"\btests?\b|suite|profile|performance|bytecode|__pycache__|inode|slow"),
    ("d-work trace / measurement", r"\btrace\b|tokens and time"),
    ("multi-session architecture (cos/cabinet/presence/bus/messaging)", r"\bcos\b|cabinet|\bseat\b|presence|\bbus\b|messag|directed notice|registration|disposition|session"),
    ("analysis Q&A: falsify/evaluate/explain/audit/ADR", r"falsify|^evaluate|^explain|^why |audit|^compare|^propose|^synthesi|^ADR|^survey|^how much|^identify|^recommend|^which |^is '|^decide|^diagnose|^frame |^design spec|^align|^document|^what "),
    ("Rule / preference / vocabulary amendment", r"Rule-\d|preference|concise-mode|batch-disposition|\bterm\b|LICENSE|standing (form|rules)"),
    ("guard / code / CLI change", r"\.py\b|guard|hook|\bdyad (ledger|session|project|check|runbook)|CLI|install|registry|manifest|references|provenance|zone|DYAD_|gitignore|plan gate|enumerator|platform"),
    ("craft work (new/changed craft)", r"craft|sysadmin|sysarch|syseng|countersign|ponytail|surface"),
    ("docs / README", r"README|docs?/|docstring"),
]

counts = collections.Counter(); ex = collections.defaultdict(list); bystate = collections.defaultdict(collections.Counter)
nent = collections.defaultdict(list)
for i, r in sorted(rows.items(), key=lambda x: int(x[0])):
    t = r["title"]
    cls = "other"
    for name, pat in CLASSES:
        if re.search(pat, t, re.I):
            cls = name; break
    counts[cls] += 1; ex[cls].append(int(i)); bystate[cls][r["state"]] += 1
    s = r.get("disposed", "").strip()
    nent[cls].append(len([e for e in s.split(";") if e.strip()]) if s else 0)
tot = sum(counts.values())
print("| class | rows | share | done | backlog | archived | mean disposed entries | example ids |")
print("|---|---|---|---|---|---|---|---|")
for cls, c in counts.most_common():
    st = bystate[cls]
    print(f"| {cls} | {c} | {100*c/tot:.0f}% | {st['done']} | {st['backlog']} | {st['archived']} | {sum(nent[cls])/len(nent[cls]):.2f} | {', '.join('#'+str(x) for x in ex[cls][:8])} |")
if "--other" in sys.argv:
    for i in ex["other"]: print(i, rows[str(i)]["title"][:100])
~~~~

### batches.py

~~~~
"""Batch sizes of disposition entries. python3 -I batches.py"""
import json,re,collections,os
rows=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"rows.json")))
seen={}
for r in rows.values():
    for e in r.get("disposed","").split(";"):
        m=re.search(r"(\d{4}-\d\d-\d\d) (Y|N) (\w+).*?batch[^#]*((?:#\d+,?\s*)+)",e)
        if m:
            ids=tuple(sorted(set(re.findall(r"#(\d+)",m.group(4)))))
            seen[(m.group(1),m.group(2),m.group(3),ids)]=len(ids)
k=collections.defaultdict(list)
for (d,yn,w,ids),n in seen.items(): k[f"{yn} {w}"].append(n)
for w,v in k.items(): print(f"{w}: {len(v)} distinct batch questions, sizes {sorted(v)}, rows covered {sum(v)}")
~~~~

### mine_files.py

~~~~
"""Sizes of plans/provenance; trace aggregation; keyword tallies. Usage: python3 -I mine_files.py <repo-root>"""
import sys, os, re, glob, statistics, collections, json
root = sys.argv[1]
D = os.path.join(root, "agent-corpus/d-work")
rows = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rows.json")))

def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]

def sizes(sub):
    fs = [f for f in glob.glob(os.path.join(D, sub, "[0-9]*.md"))]
    sz = {int(os.path.basename(f)[:-3]): os.path.getsize(f) for f in fs}
    v = list(sz.values())
    print(f"\n## {sub}: files {len(v)} total {sum(v):,} B (~{sum(v)//4:,} tokens derived) mean {statistics.mean(v):,.0f} median {statistics.median(v):,.0f} p90 {pct(v,.9):,} max {max(v):,}")
    print("  top10:", ", ".join(f"#{i} {s:,}" for i, s in sorted(sz.items(), key=lambda x: -x[1])[:10]))
    return sz
ps = sizes("plans"); vs = sizes("provenance")
both = [i for i in ps if i in vs]
print(f"  plan:provenance byte ratio over {len(both)} ids with both: {sum(ps[i] for i in both)/sum(vs[i] for i in both):.1f}x")
# plan revisions
revs = collections.Counter()
for i in ps:
    t = open(os.path.join(D, "plans", f"{i}.md"), encoding="utf-8").read()
    revs[len(re.findall(r"^#+ .*[Rr]evision \d", t, re.M))] += 1
print("  plan files by count of 'Revision N' headings:", sorted(revs.items()))
# provenance entry counts and prompt bytes
pk = collections.Counter(); pb = []
for i in vs:
    t = open(os.path.join(D, "provenance", f"{i}.md"), encoding="utf-8").read()
    for m in re.finditer(r"^## \d+ (prompt|disposition) ", t, re.M): pk[m.group(1)] += 1
print("  provenance entries by kind:", dict(pk))

# traces
print("\n## traces")
tf = sorted(glob.glob(os.path.join(D, "traces", "[0-9]*.md")))
B = collections.Counter(); withb = 0; agentside = []; top1 = collections.Counter(); top3 = collections.Counter()
counts = collections.defaultdict(list); deleg = []; absent = 0; ratio = []; per = {}
for f in tf:
    t = open(f, encoding="utf-8").read(); i = int(os.path.basename(f)[:-3])
    sec = t.split("## Buckets", 1)[1].split("## Counts", 1)[0]
    rowsb = re.findall(r"^\| ([a-z/]+) \| (operator|agent) \| (\d+) \|", sec, re.M)
    if not rowsb: absent += 1
    else:
        withb += 1; d = {}
        for name, part, s in rowsb: B[name] += int(s); d[name] = int(s)
        per[i] = d
    m = re.search(r"\*\*Top 3:\*\* (.*)", t)
    if m:
        items = re.findall(r"([a-z/]+) \d+%", m.group(1))
        if items: top1[items[0]] += 1
        for x in items: top3[x] += 1
    m = re.search(r"\*\*Agent-side:\*\* (\d+) s", t)
    if m: agentside.append((int(m.group(1)), i))
    cs = t.split("## Counts", 1)[1].split("## Bottleneck", 1)[0]
    for key, pat in [("commits", r"\| commits \| (\d+)"), ("ledger_only", r"\| commits \| \d+ \((\d+) ledger-only"), ("suite_runs", r"full-suite runs[^|]*\| (\d+)"),
                     ("guard_gates", r"guards-only push gates \| (\d+)"), ("tool_calls", r"\| tool calls \| (\d+)"), ("out_tokens", r"\| output tokens \| (\d+)")]:
        mm = re.search(pat, cs)
        if mm: counts[key].append(int(mm.group(1)))
    mm = re.search(r"delegated share \| ([\d.]+)%", cs)
    if mm: deleg.append(float(mm.group(1)))
    mm = re.search(r"test execution / inference = (\d+(?:\.\d+)?)", t)
    if mm: ratio.append(float(mm.group(1)))
print(f"traces {len(tf)}; with buckets {withb}; buckets absent {absent}")
tot = sum(B.values())
agent = {k: v for k, v in B.items() if k not in ("operator", "idle")}
at = sum(agent.values())
print("| bucket | seconds | share of all | share of agent-side |")
for k, v in B.most_common():
    print(f"| {k} | {v:,} | {100*v/tot:.1f}% | {'' if k in ('operator','idle') else f'{100*v/at:.1f}%'} |")
print(f"| total | {tot:,} ({tot/3600:.1f} h) | | agent-side {at:,} s ({at/3600:.1f} h) |")
mech = sum(v for k, v in agent.items() if k not in ("inference", "background"))
print(f"inference {B['inference']:,} s; mechanical (suite+guards+github+git/local+subagent+other) {mech:,} s; background {B['background']:,} s; wait (operator+idle) {B['operator']+B['idle']:,} s")
print("top-1 bucket tally:", top1.most_common()); print("in-top-3 tally:", top3.most_common())
a = sorted(x for x, _ in agentside)
if a: print(f"agent-side s: n {len(a)} median {statistics.median(a):,.0f} mean {statistics.mean(a):,.0f} p90 {pct(a,.9):,} max {max(agentside)}; top5 {sorted(agentside, reverse=True)[:5]}")
for k, v in counts.items():
    if v: print(f"count {k}: n {len(v)} sum {sum(v):,} mean {statistics.mean(v):.1f} median {statistics.median(v)} max {max(v)}")
if deleg: print(f"delegated share: n {len(deleg)} zero {sum(1 for x in deleg if x == 0)} mean {statistics.mean(deleg):.1f}% max {max(deleg)}%")
if ratio: print(f"test-exec/inference ratio: n {len(ratio)} median {statistics.median(ratio)} mean {statistics.mean(ratio):.2f}")
# per-trace share of inference in agent side
sh = [d.get("inference", 0) / max(1, sum(v for k, v in d.items() if k not in ("operator", "idle"))) for d in per.values()]
print(f"per-trace inference share of agent-side: median {100*statistics.median(sh):.0f}%")
# git/local per trace leaders
gl = sorted(((d.get('git/local', 0), i) for i, d in per.items()), reverse=True)[:5]
print("largest git/local:", gl)

# keyword tallies over titles (non-exclusive)
print("\n## title keyword tallies (non-exclusive)")
for k, p in [("falsify", r"falsif"), ("sync", r"\bsync\b"), ("banked", r"banked"), ("archive session", r"archiv(e|ing) (this|the)|archiving"), ("board report", r"board report"),
             ("incident mode X", r"incident mode"), ("release", r"releas"), ("test/suite", r"\btests?\b|suite"), ("rendered by hand", r"by hand"), ("evaluate/explain/why", r"^(evaluate|explain|why)"),
             ("spin up", r"spin up"), ("land/re-land/recovery", r"^land |re-land|recovery")]:
    ids = [int(i) for i, r in rows.items() if re.search(p, r["title"], re.I)]
    print(f"  {k}: {len(ids)}  e.g. {sorted(ids)[:10]}")
~~~~

### trace_extra.py

~~~~
"""Trace extras: excl. outliers, output tokens per title class. python3 -I trace_extra.py <repo>"""
import sys,os,re,glob,json,collections,statistics
root=sys.argv[1]; D=os.path.join(root,"agent-corpus/d-work/traces")
here=os.path.dirname(os.path.abspath(__file__))
rows=json.load(open(os.path.join(here,"rows.json")))
src=open(os.path.join(here,"classify.py")).read()
ns={}; exec(src.split("counts =")[0].replace("rows = json.load(open(sys.argv[1]))","pass"),ns); CL=ns["CLASSES"]
def cls(t):
    for n,p in CL:
        if re.search(p,t,re.I): return n
    return "other"
tok=collections.defaultdict(list); B=collections.Counter(); calls=collections.defaultdict(list); per=[]
for f in glob.glob(os.path.join(D,"[0-9]*.md")):
    i=os.path.basename(f)[:-3]; t=open(f,encoding="utf-8").read()
    m=re.search(r"\| output tokens \| (\d+)",t); c=cls(rows[i]["title"])
    if m: tok[c].append(int(m.group(1))); per.append((int(m.group(1)),int(i),rows[i]["title"][:60]))
    m2=re.search(r"\| tool calls \| (\d+)",t)
    if m2: calls[c].append(int(m2.group(1)))
    if i=="261": continue
    for name,part,s in re.findall(r"^\| ([a-z/]+) \| (operator|agent) \| (\d+) \|",t.split("## Counts")[0],re.M): B[name]+=int(s)
ag={k:v for k,v in B.items() if k not in("operator","idle")}; at=sum(ag.values())
print("agent-side excl #261:",at,"s;",", ".join(f"{k} {v} ({100*v/at:.1f}%)" for k,v in sorted(ag.items(),key=lambda x:-x[1])))
print("| class | traces | output tokens sum | mean | tool calls mean |")
for c,v in sorted(tok.items(),key=lambda x:-sum(x[1])):
    print(f"| {c} | {len(v)} | {sum(v):,} | {statistics.mean(v):,.0f} | {statistics.mean(calls[c]):.0f} |")
print("top output-token traces:",sorted(per,reverse=True)[:8])
~~~~

### mine_incidents.py

~~~~
"""Mine INCIDENTS.md. Usage: python3 -I mine_incidents.py <repo-root>"""
import sys, os, re, collections
t = open(os.path.join(sys.argv[1], "agent-corpus/audits/INCIDENTS.md"), encoding="utf-8").read()
rows = []
for line in t.splitlines():
    if not re.match(r"^\| 20\d\d-\d\d-\d\d", line): continue
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
    if len(cells) < 5: cells += [""] * (5 - len(cells))
    rows.append(dict(date=cells[0], dwork=cells[1], what=cells[2], cause=cells[3], cons="|".join(cells[4:])))
print("incident rows", len(rows))
C = collections.Counter
bym = C(r["date"][:7] for r in rows); print("by month", sorted(bym.items()))
byd = C(r["date"] for r in rows); print("top days", byd.most_common(6))
dw = C(x for r in rows for x in re.findall(r"#(\d+)", r["dwork"])); print("d-works with most incident rows", dw.most_common(10))
modes = C(m.upper() for r in rows for m in re.findall(r"\b[Mm]ode ([A-W])\b", r["what"] + " " + r["cause"] + " " + r["cons"]))
print("explicit 'mode X' labels (taxonomy 2026-10-10, A-W):", sorted(modes.items(), key=lambda x: -x[1]))
print("rows carrying a mode label:", sum(1 for r in rows if re.search(r"\b[Mm]ode [A-W]\b", r["what"] + r["cause"] + r["cons"])))
K = [
    ("merge/act before Y (self-ratify, plan-before-ask)", r"before (the |its )?(Operator'?s? )?(Done-|plan-)?`?Y|self-ratif|before .*asked|never gave|without .*Y\b"),
    ("push rejected / non-fast-forward / race on main", r"non-fast-forward|rejected|\brace\b|peer'?s? (conflicting )?push|moved under"),
    ("merge conflict / rebase", r"conflict|rebase"),
    ("guard/hook FAIL caught the error", r"FAIL|refused|refuses|guard (failed|refus)|hook refus"),
    ("provenance/disposition record mismatch", r"provenance"),
    ("ledger row form (state, id, title, disposed)", r"\brow\b.*(planned|state|disposed|title)|born planned|id collision|collided"),
    ("stale local view / unfetched", r"stale|fetch|behind origin|origin/main"),
    ("concurrent session interference", r"concurrent|peer session|another session|two sessions"),
    ("test suite red / hardcoded enumeration", r"test_|suite (red|fail)|hardcod|literal list|enumerat"),
    ("VERSION / tag / bundle / zone ordering", r"VERSION|BUNDLE|\btag\b|drift|zone"),
    ("value from memory / wrong number / wrong object", r"from memory|digest|wrong (number|object)|stated .* instead"),
    ("git write used as read (checkout/reset)", r"checkout|reset --hard|git restore"),
    ("environment (python version, tmp, CI 403, inodes)", r"3\.11|403|inode|tmpfs|No space|python3"),
    ("flag parsed as positional (--help, --backlog)", r"--help|--backlog|positional"),
    ("delegation/subagent", r"subagent|sub-agent|delegat|fork"),
    ("lost turn / session exited / compaction", r"lost|session exited|compaction|timed out"),
]
print("\n| cause keyword group (non-exclusive, what+cause) | rows | example d-works |")
print("|---|---|---|")
for name, p in K:
    hits = [r for r in rows if re.search(p, r["what"] + " " + r["cause"], re.I)]
    ex = []
    for r in hits:
        ex += re.findall(r"#\d+", r["dwork"])[:1]
    print(f"| {name} | {len(hits)} | {', '.join(list(dict.fromkeys(ex))[:6])} |")
rc = [r for r in rows if re.search(r"recovery|re-?cut|new row|fresh (plan|branch|PR)|second PR|re-land|redone|restored|re-run|rewr", r["cons"], re.I)]
print("\nrows whose consequence names a recovery act (recovery|re-cut|new row|fresh plan/branch/PR|redone|restored|re-run|rewrite):", len(rc))
caught = [r for r in rows if re.search(r"before any (push|commit|merge)|caught .* before|never (reached|on) `?main|no `?main`? impact|nothing (reached|pushed)", r["cons"], re.I)]
print("rows whose consequence says caught before push/commit/main:", len(caught))
onmain = [r for r in rows if re.search(r"left `?main`? red|on `?main`?|landed on main|reached `?main", r["cons"] + r["what"], re.I) and r not in caught]
print("rows mentioning main impact (not in caught set):", len(onmain))
L = [len(r["what"]) + len(r["cause"]) + len(r["cons"]) for r in rows]
print(f"row text: total {sum(L):,} chars, mean {sum(L)/len(L):,.0f}, max {max(L):,}")
~~~~

### mine.py

~~~~
import subprocess, re, sys, collections, itertools, json, datetime
REPO = '/home/user/ds-cc4'
def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, check=True).stdout

SEP = '\x1e'
raw = git('log', 'origin/main', '--numstat', '--no-renames',
          f'--format={SEP}%H%x1f%P%x1f%aI%x1f%cI%x1f%s%x1f%b%x1f')
commits = []
for chunk in raw.split(SEP)[1:]:
    head, _, rest = chunk.rpartition('\x1f')
    h, p, ad, cd, s, b = head.split('\x1f', 5)
    files = []
    for ln in rest.strip().splitlines():
        parts = ln.split('\t')
        if len(parts) == 3:
            a, d, f = parts
            files.append((f, int(a) if a != '-' else 0, int(d) if d != '-' else 0))
    commits.append(dict(h=h, parents=p.split(), ad=ad, cd=cd, s=s, b=b, files=files))

def zone(path):
    for pre, z in [('agent-corpus/', 'agent'), ('dyad/', 'agent'), ('workstation-corpus/', 'workstation'),
                   ('preferences-corpus/', 'preferences'), ('crafts/', 'craft'), ('.github/', 'infra'),
                   ('.githooks/', 'infra'), ('.claude/', 'infra')]:
        if path.startswith(pre): return z
    if path in ('CLAUDE.md', 'README.md', 'LICENSE', '.gitignore', 'BUNDLE.md'): return 'infra'
    return 'UNCLASSIFIED'

out = []
P = out.append
merges = [c for c in commits if len(c['parents']) > 1]
non = [c for c in commits if len(c['parents']) <= 1]
P(f"## A1 totals\ncommits {len(commits)}; merges {len(merges)}; non-merge {len(non)}")
first = min(c['ad'] for c in commits); last = max(c['ad'] for c in commits)
P(f"span {first[:10]} .. {last[:10]}")

def ledger_only(c):
    return c['files'] and all(f.startswith('agent-corpus/d-work/') for f, _, _ in c['files'])
lo = [c for c in non if ledger_only(c)]
P(f"ledger-only non-merge {len(lo)} ({100*len(lo)/len(non):.1f}%); other non-merge {len(non)-len(lo)}; empty-diff non-merge {sum(1 for c in non if not c['files'])}")
zc = collections.Counter()
for c in non:
    zs = {zone(f) for f, _, _ in c['files']}
    key = '+'.join(sorted(zs)) if zs else '(empty)'
    if ledger_only(c): key = 'agent[ledger-only]'
    zc[key] += 1
P("zone of non-merge commits: " + ', '.join(f"{k} {v}" for k, v in zc.most_common()))
day = collections.Counter(c['ad'][:10] for c in commits)
dayM = collections.Counter(c['ad'][:10] for c in merges)
dayL = collections.Counter(c['ad'][:10] for c in lo)
P("\nper day (date: total / merges / ledger-only):")
for d in sorted(day):
    P(f"  {d}: {day[d]} / {dayM[d]} / {dayL[d]}")

# A2 shapes
shapes = [
 ('merge: PR', lambda c: len(c['parents'])>1 and c['s'].startswith('Merge pull request')),
 ('merge: other (local --no-ff / main into branch)', lambda c: len(c['parents'])>1),
 ('ledger: opened', lambda c: re.match(r'ledger: (open|.*#\d+.*\bopen(ed)?\b)', c['s']) and not re.search(r'\bplan(ned)?\b on|plan-?Y|Y plan|done', c['s'].split('opened')[0] if 'opened' in c['s'] else '')),
 ('ledger: Done-Y recorded', lambda c: c['s'].startswith('ledger') and re.search(r'Done-?Y|done Y|Y done|Done Y', c['s'])),
 ('ledger: done/close', lambda c: c['s'].startswith('ledger') and re.search(r'\bdone\b', c['s'])),
 ('ledger: planned / plan-Y', lambda c: c['s'].startswith('ledger') and re.search(r'planned|plan-?Y|Y plan', c['s'])),
 ('ledger: plan revision/correction', lambda c: c['s'].startswith('ledger') and re.search(r'plan .*revision|revision|plan #\d+ (corrected|records|revised|amended)|corrected', c['s'])),
 ('ledger: backlog/archived/blocked', lambda c: c['s'].startswith('ledger') and re.search(r'backlog|archiv|blocked', c['s'])),
 ('ledger: presence/seat only', lambda c: c['s'].startswith('ledger') and re.search(r'presence|seat|session', c['s'])),
 ('ledger: other', lambda c: c['s'].startswith('ledger')),
 ('incident rows', lambda c: re.search(r'incident', c['s'], re.I)),
 ('version bump / release / re-pin', lambda c: re.search(r'VERSION|bump|release|re-?pin|BUNDLE|\bv\d+\.\d+', c['s'])),
 ('change-log / workstation', lambda c: c['s'].startswith('workstation')),
 ('substantive (d-work #N / zone-prefixed)', lambda c: True),
]
def shape(c):
    for name, f in shapes:
        if f(c): return name
sc = collections.Counter(shape(c) for c in commits)
P("\n## A2 subject shapes (first match wins, order as listed)")
for name, _ in shapes:
    P(f"  {sc[name]:5d}  {name}")
clerical = sum(v for k, v in sc.items() if k.startswith('ledger') or k.startswith('merge'))
P(f"clerical (ledger+merge shapes) {clerical} vs rest {len(commits)-clerical}: ratio {clerical/(len(commits)-clerical):.2f}")
P(f"by path: ledger-only {len(lo)} + merges {len(merges)} = {len(lo)+len(merges)} vs substantive non-merge {len(non)-len(lo)}: ratio {(len(lo)+len(merges))/(len(non)-len(lo)):.2f}")

# per d-work
def ids(c):
    t = c['s'] + '\n' + c['b']
    m = re.findall(r'd-work #(\d+)', t)
    if not m:
        m2 = re.match(r'ledger:\s*(?:open |plan )?#(\d+)', c['s'])
        if m2: m = [m2.group(1)]
    if not m:
        m = re.findall(r'\(#(\d+)\)\s*$', c['s'])
    return set(m)
per = collections.defaultdict(lambda: collections.Counter())
for c in commits:
    i = ids(c)
    if len(i) != 1: continue
    (d,) = tuple(i)
    k = 'merge' if len(c['parents'])>1 else ('ledger' if ledger_only(c) else 'subst')
    per[d][k] += 1
tot = sorted(sum(v.values()) for v in per.values())
def q(xs, p): return xs[min(len(xs)-1, int(p*len(xs)))]
attrib = sum(tot)
P(f"\nper d-work (commits attributed to exactly one id via 'd-work #N', 'ledger: #N', or trailing '(#N)'): {len(per)} d-works, {attrib} of {len(commits)} commits attributed")
P(f"  commits per d-work: median {q(tot,.5)}, p75 {q(tot,.75)}, p90 {q(tot,.9)}, max {tot[-1]}, mean {attrib/len(per):.2f}")
lc = sorted(v['ledger'] for v in per.values()); mc = sorted(v['merge'] for v in per.values()); sc2 = sorted(v['subst'] for v in per.values())
P(f"  ledger-only commits per d-work: median {q(lc,.5)}, mean {sum(lc)/len(lc):.2f}, p90 {q(lc,.9)}, max {lc[-1]}")
P(f"  merge commits per d-work: mean {sum(mc)/len(mc):.2f}; substantive: mean {sum(sc2)/len(sc2):.2f}, median {q(sc2,.5)}")
P(f"  d-works with 0 substantive commits (pure-ledger rows): {sum(1 for v in per.values() if v['subst']==0)}")
hist = collections.Counter(min(t, 15) for t in tot)
P("  histogram (commits:count; 15=15+): " + ', '.join(f"{k}:{hist[k]}" for k in sorted(hist)))
top = sorted(per.items(), key=lambda kv: -sum(kv[1].values()))[:12]
P("  top d-works by commits: " + '; '.join(f"#{d} {sum(v.values())} (L{v['ledger']}/M{v['merge']}/S{v['subst']})" for d, v in top))

# A3 files
fc = collections.Counter(); churn = collections.Counter()
for c in non:
    for f, a, d in c['files']:
        fc[f] += 1; churn[f] += a + d
P("\n## A3 top 30 files by non-merge commits touching them (commits, lines churned)")
for f, n in fc.most_common(30):
    P(f"  {n:4d} {churn[f]:7d}  {f}")
def kind(f):
    m = re.match(r'agent-corpus/d-work/(rows|plans|provenance|sessions|traces)/', f)
    if m: return m.group(1)
    if f.startswith('agent-corpus/audits/INCIDENTS'): return 'INCIDENTS.md'
    if f.startswith('agent-corpus/falsification/'): return 'falsification'
    if f.startswith('workstation-corpus/CHANGELOG'): return 'CHANGELOG'
    if f.startswith('dyad/rules/'): return 'dyad/rules'
    if f.startswith('dyad/tests/'): return 'dyad/tests'
    if f.startswith('dyad/guards/'): return 'dyad/guards'
    if f.startswith('dyad/scripts/'): return 'dyad/scripts'
    if f.startswith('crafts/'): return 'crafts/' + f.split('/')[1]
    return zone(f) + ':other'
kc = collections.Counter(); kchurn = collections.Counter()
for c in non:
    for f, a, d in c['files']:
        kc[kind(f)] += 1; kchurn[kind(f)] += a + d
P("\nfile kinds (file-touches, lines): " + ', '.join(f"{k} {v}/{kchurn[k]}" for k, v in kc.most_common(25)))
combo = collections.Counter()
for c in non:
    ks = frozenset(kind(f) for f, _, _ in c['files'])
    combo[ks] += 1
P("\nco-change sets (kinds per non-merge commit), top 20:")
for ks, n in combo.most_common(20):
    P(f"  {n:4d}  {'+'.join(sorted(ks)) or '(empty)'}")
pair = collections.Counter()
for c in non:
    fs = sorted({f for f, _, _ in c['files'] if not f.startswith('agent-corpus/d-work/')})
    if len(fs) > 12: continue
    for a, b in itertools.combinations(fs, 2): pair[(a, b)] += 1
P("\nnon-ledger file pairs changed together (commits with <=12 files), top 15:")
for (a, b), n in pair.most_common(15):
    P(f"  {n:3d}  {a} + {b}")

# A4 recovery
pats = {'fix': r'\bfix', 'correct': r'correct', 'revert': r'revert', 're- (re-touch/re-record/re-ask...)': r'\bre-\w+',
        'rebase': r'rebas', 'incident': r'incident', 'conflict': r'conflict', 'amend': r'amend', 'recover': r'recover',
        'resolve': r'resolv', 'retry/again': r'retry|again'}
P("\n## A4 recovery/rework vocabulary in subjects (non-merge; case-insens.; a commit may hit several)")
anyhit = 0
for c in non:
    if any(re.search(p, c['s'], re.I) for p in pats.values()): anyhit += 1
for k, p in pats.items():
    n = sum(1 for c in non if re.search(p, c['s'], re.I))
    nb = sum(1 for c in non if re.search(p, c['s'] + ' ' + c['b'], re.I))
    P(f"  {k:40s} subject {n:4d}  subject+body {nb:4d}")
P(f"  any pattern in subject: {anyhit} ({100*anyhit/len(non):.1f}% of non-merge)")
lm = [c for c in merges if not c['s'].startswith('Merge pull request')]
P(f"  non-PR merge commits (local --no-ff, main-into-branch, conflict resolution): {len(lm)}")
for c in lm[:12]: P(f"    {c['h'][:7]} {c['ad'][:10]} {c['s'][:100]}")

# A5 PRs
P("\n## A5 PR merges")
pr = [c for c in merges if c['s'].startswith('Merge pull request')]
nums = [int(re.match(r'Merge pull request #(\d+)', c['s']).group(1)) for c in pr]
P(f"PR merge commits {len(pr)}; distinct PR numbers {len(set(nums))}; range #{min(nums)}..#{max(nums)}")
sizes = []; lat = []; ledgerPR = 0; prz = collections.Counter()
for c in pr:
    p1, p2 = c['parents'][:2]
    lst = git('rev-list', '--no-merges', f'{p1}..{p2}').split()
    sizes.append(len(lst))
    if lst:
        t0 = git('log', '-1', '--format=%aI', lst[-1]).strip()
        dt = (datetime.datetime.fromisoformat(c['cd']) - datetime.datetime.fromisoformat(t0)).total_seconds()/3600
        lat.append(dt)
    files = git('diff', '--name-only', f'{p1}...{p2}').split()
    zs = {zone(f) for f in files}
    if files and all(f.startswith('agent-corpus/d-work/') for f in files):
        ledgerPR += 1; prz['agent[ledger-only]'] += 1
    else:
        prz['+'.join(sorted(zs)) or '(empty)'] += 1
sizes.sort(); lat.sort()
P(f"commits per PR (merge-base..PR head, non-merge): median {q(sizes,.5)}, mean {sum(sizes)/len(sizes):.2f}, p90 {q(sizes,.9)}, max {sizes[-1]}; 1-commit PRs {sizes.count(1)}")
P(f"hours first-commit->merge: median {q(lat,.5):.2f}, p75 {q(lat,.75):.2f}, p90 {q(lat,.9):.2f}, max {lat[-1]:.1f}; under 1h: {sum(1 for x in lat if x<1)} of {len(lat)}")
P(f"ledger-only PRs (whole diff under agent-corpus/d-work/): {ledgerPR} of {len(pr)}")
P("PR zone: " + ', '.join(f"{k} {v}" for k, v in prz.most_common()))
prl = [c for c in pr if re.search(r'#\d+:?\s*ledger|: ledger', c['s'])]
P(f"PR merge subjects containing 'ledger': {sum(1 for c in pr if 'ledger' in c['s'])}")
print('\n'.join(out))
json.dump({'n': len(commits)}, open('/tmp/claude-0/-home-user-dyad-system/216584db-f1aa-5051-85cf-6d32fd758702/scratchpad/meta.json', 'w'))
~~~~

