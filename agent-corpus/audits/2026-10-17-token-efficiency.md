# Token-efficiency audit — what the Agent spends tokens on, and which frequent acts code should take (2026-10-17)

*d-work #333, seat `ds-cabinet-cloud-4`, relayed from #331. Tree `b60056b` on `main`. Detects, counts,
ranks; disposes nothing. Survivors are proposed as rows in the completion reply; none is opened here.
Falsification: `../falsification/2026-10-17-token-efficiency.md`. Builds on #154
(`2026-09-24-performance-bottlenecks.md`), #161 (`2026-09-25-optimization-opportunities.md`) and #204
(`2026-10-02-test-execution-profile.md`), which measured **seconds**; this audit measures **tokens and
dollars**, what an inference budget (#143) is spent in.*

**Measured** = read from a system (the hosting's per-session `usage`, git, the corpus files).
**Derived** = computed here, formula stated. Bytes/4 ≈ tokens is a derivation, not a measurement.

## 1. Sources and their reach

| source | reach | gap |
|---|---|---|
| hosting `list_sessions` → `external_metadata.usage` (input, output, cache read, cache write, `cost_usd`) | 150 sessions on the account, 68 carrying usage; **18 on `dyad-system`, 16 with usage** | terminal sessions (`ds-cabinet-term-1`, the host peer) report nothing; purged sessions are gone; no per-call split |
| `git log origin/main` (full history fetched) | 1,416 commits, 2026-09-14 → 10-17; 418 merges, 998 non-merge | branches never merged, PR bodies and review threads are not in git |
| `agent-corpus/d-work/` | 323 rows, 223 plans, 310 provenance records, 82 traces | 19 traces "absent: no window"; trace output-token counts overlap across shared batch turns |
| `agent-corpus/audits/INCIDENTS.md` | 188 rows; the A–W taxonomy of 2026-10-10 | free-text causes; keyword grouping is heuristic |
| tools | `dyad --help`, `dyad check --list` (24 guards), 7 play-books, run-books, `dyad/scripts/`, `crafts/*/scripts/` | — |

PRs were read from their merge commits (`git rev-list --no-merges p1..p2` per hosted merge), not from
the GitHub API; review rounds and PR bodies are therefore not counted.

## 2. Where the money goes — measured

The 16 `dyad-system` sessions with usage report **$4,050**, **21.1 M output tokens**, **208 M
cache-write tokens** and **6.88 B cache-read tokens** (input tokens 0.7 M: everything but the newest
message is served from cache).

Priced at the first-party per-MTok rates (Sonnet 5.5 $2 in / $10 out / $0.20 cache read; Opus 5.5
$4 / $20 / $0.20; Fable 5.1 $10 / $50 / $0.25) with **cache writes at 2× input**, the 1-hour cache a
Claude Code session uses, the derived cost reproduces the reported `cost_usd` to within 3% for every
session under $150 (e.g. cos $122.2 derived vs $115.3 reported; cabinet-cloud-3 $47.7 vs $47.6;
this audit's own session $1.6 vs $1.6). Writes at 1.25× fall 20–30% short, so the 2× calibration is
the one used below. The four largest Sonnet sessions (sysadmin, syseng, sysarch craft, September)
report up to 2.3× the derived figure; the excess is unexplained here (stated, not guessed).

**Cost shares, derived over the 14 sessions on currently priced models ($2,815 derived):**

| component | share of cost |
|---|---:|
| cache read (the context re-read on every call) | **49%** |
| cache write (the context written into cache as it grows or is invalidated) | **40%** |
| output tokens (everything the Agent writes) | **10%** |
| uncached input | ~0% |

Per session, cache read / output runs **200× to 450×**: each output token arrives with 200–450
tokens of context re-read. **Cost is turns × context size, not words written.** Two consequences
govern the ranking in §5:

1. A recurring sequence of *n* tool calls done by hand costs *n* full-context reads. Collapsing it into
   one command saves *n−1* reads at whatever the context is at that moment, regardless of how little
   text each step emits.
2. The same act costs more in a long session than in a short one. The four craft sessions of
   September ran at 530–680 k tokens of context and cost $290–$1,738 each; the three cabinet sessions
   of 2026-10-15, scoped to one question each, cost $47–$93.

### The fixed floor: the frame
Every call of every session carries the frame `CLAUDE.md` imports: **156,305 bytes ≈ 39 k tokens**
(derived, bytes/4) — the 19 Rules (124 kB; Rule-3 alone 34 kB, Rule-11 16 kB), the vocabulary and the
preference table. The Rules were 75 kB on 2026-09-14 (`git show 52024e6:dyad/rules/…`); they grew 65%
in a month. At a typical 300 k context (derived below) the frame is **~13% of every read**, a share
that rises as Rules grow and falls only as a session's own context grows.

### Per d-work and per call — derived
- Traces report 2,716,254 output tokens over 77 traced d-works: **mean 35.3 k, median 11.9 k**, and
  2,638 tool calls: **mean 34, median 14** (measured by `dwork trace`).
- Over the 16 sessions, $4,050 ÷ 21.1 M output = **$0.19 per 1 k output tokens**, all-in (derived).
- So a mean traced d-work costs ≈ 35.3 k × $0.19/k ≈ **$6.7**, and a tool call ≈ $6.7 ÷ 34 ≈
  **$0.20** (derived; the median d-work ≈ $2.3). Cache read per call ≈ 300 k tokens, which is the
  context size used above (derived from cache read / output ≈ 300 and 35.3 k / 34 ≈ 1 k output per
  call).

These per-call figures are the exchange rate for §5: **one avoided tool call ≈ $0.20** at typical
context, more in a long session.

## 3. What the Agent does repeatedly — measured

**Clerical outweighs substantive 4.3 : 1 in git.** Of 998 non-merge commits, **737 (74%) are
ledger-only**; with the 418 merges, 1,155 commits are clerical against 261 substantive. Per d-work
(1,139 commits attributable to one id, 232 d-works): **median 4 commits, of which 3 are ledger-only**;
93 d-works have no substantive commit at all. In the traced windows, 259 of 273 commits (95%) are
ledger-only, and the push gate ran guards-only 405 times against 150 full suites.

Recurring commit shapes (subject regexes, first match wins):

| shape | count | the tool that writes the files | still done by hand, every time |
|---|---:|---|---|
| `ledger: #N opened …` | 233 | `dwork new --prompt-file` | the prompt file, the plan file (median 68 lines, no skeleton), presence touch, `git add`, a free-prose subject (median 209 chars), push, retry on race |
| `ledger: #N planned …` | 168 | `dwork state planned` + `session touch` | the said-file, commit, push, retry |
| `ledger: #N … Done-Y recorded` | 123 | `dwork state … -d 'Y done (merges PR #a at <head>)'` + `dwork trace --out` | looking up each PR's head, composing the entry, commit, push |
| `ledger: #N done / landed` | 48 | `dwork state <id> done` | checking the head is on `main`, commit, push |
| merges (hosted 312, custom 70, other 36) | 418 | none | PR body, merge call, heads-unchanged check |
| ledger-only PRs (whole diff under `d-work/`) | 126 hosted, 190 ledger-only merges | none | branch, push, PR, merge — for content Rule-3 sends straight to `main`, forced through a PR by a branch fence (#23) |
| plan revisions / plans-only | 44 / 90 | none | edit, commit |
| incident rows | 80 commits, 205 lines | `incidents.py` parses only | the row, a tail append that conflicts across seats (a 7-merge chain on 10-01) |
| version / BUNDLE / tags | 68 commits, 50 tags | `bundle check` detects drift | bump, row, tag, zone ordering |
| rebase / re-record | 22 subjects, 34 rewritten commits | none | fetch, rebase, re-run evidence, re-record the Done entry, re-ask |

**No script in the package runs `git commit`, `git push`, `git fetch`, `git rebase`, `git merge` or
opens a PR.** Every one of the 1,416 commits had its staging, message and push composed by inference.
The clerical commit messages alone total 254 k characters, more than the 222 k of substantive ones.

**Session housekeeping is the costliest work class per row.** Classifying the 323 titles: sync with
remote 11, "falsify that all changes are banked" 6 (#234, #235, #239, #242, #243, #325), archive /
resume / stand-down 12, board and id reports 7 (three "rendered by hand": #298, #324, #327), spin-up
and seat registration 10, landing recovery 11 — **51 rows, 16%**. Spin-up rows cost 3.00 dispositions
each and 90 k output tokens per trace, landing recovery 2.73 dispositions, against a ledger mean of
1.93. The banked / archive / spin-up traces hold **729 k output tokens over 16 traces — 27% of all
traced output** for work with no new design content.

**Inference dominates agent-side time and delegation barely fires.** Excluding #261 (a 48-hour lost
segment booked as inference), agent-side time is 41% inference, 24% background, 13% suite, 11% git,
10% guards. Of 28 traces that report a delegated share, **24 report 0%**; subagent time is 0.2% of
agent-side. `delegation: plan-and-execute` is set and not used.

**Plans are the largest Agent-authored stream**: 223 files, 1.85 MB ≈ 463 k tokens (derived), mean
8.3 kB, **20.5× the bytes of the Operator's words** they answer; 29 were revised, one 16 times. The
top ten plans hold 22% of the bytes. By §2, the cost of a plan is less its writing (output is 10%)
than its re-reading: every later call in that session carries it.

**Incidents that cost turns** (188 rows; keyword groups, non-exclusive): guard / hook refusal 83;
version / tag / zone ordering 38; acting before the `Y` 32; ledger row form 29; stale view of
`origin` 26; concurrent-session interference 25; merge conflict / rebase 16; push race on `main` 12;
a flag parsed as a positional (`--backlog` as a title) 8 — six rows, #129–#134, carry the literal
title `--backlog`. 49 rows name a recovery act (a re-cut, a new branch or PR, a redo). The landing
loop (#196, #200, #245, #246, #321–#323) is the single most expensive recurring recovery.

## 4. What earlier audits proposed, and where it went

| audit | candidate | state at `b60056b` |
|---|---|---|
| #154 | never hand-run a whole test root | **landed** — `dyad check --tests` (#155), Rule-12 property 2 |
| #154 | `check --evidence` once per merge | conduct only; not mechanized |
| #154 | delegation is where the minutes are | falsified as conduct (#188, #192, #195); traces still show 0% delegation in 24 of 28 |
| #161 C1, C2, C4 | empty-range skip, suite memo, one install per module | **landed** — #164, #162, #163, under #199 |
| #204 #1 | a single-guard path, `dyad check --guard <label>` (55 full checks run to read one guard line) | **not landed**; `package.py` has no such flag |
| #204 #3 | unsigned fixture commits | **landed** — #206 |
| #204 #2, #4–#8 | memo hit rate, in-process CLI tests, fixture reuse, parallel roots, manifest scan cache | no rows opened; not in code |

Every landed survivor was a **test-time** saving: the mechanical seconds those audits measured. None
addressed the clerical sequences of §3 or the context-size cost of §2, which those audits could not
see because they measured time, not tokens.

## 5. Candidates, ranked

Rank is by **calls avoided × frequency**, each call valued at the derived ≈ $0.20 (§2). A rank is kept
only if it survives a 2× error in the per-call estimate against its neighbour (falsification F1).
"Saving" is derived, over the observed 30 days, and states its arithmetic.

| # | candidate | what it replaces (measured frequency) | calls saved each | derived saving, 30 days | kind |
|---|---|---|---:|---:|---|
| **1** | **One ledger-transaction verb**: `dwork new|state … --commit` stages exactly the files the verb wrote, writes the subject from the transition, then fetch → rebase → guarded push → retry, falling back under `ledger-pr-merge: agent` to branch → PR → merge | 737 ledger-only commits; 126 ledger PRs / 190 ledger merges; 12 push-race and 26 stale-view incidents | 3–5 (add, commit, push, retry; +3 when fenced) | ≈ 737 × 3 + 190 × 3 ≈ 2,800 calls ≈ **$560** | code (core CLI) |
| **2** | **Slim the always-loaded frame**: the import loads each Rule's block (Intent, Target, Boundaries, Conditions) and a path; full Rule text is read on demand by the step that needs it | every call of every session: 39 k tokens (derived), ~13% of cache read+write | 0 calls; ~13% of every call | ≈ 13% × 89% × $4,050 ≈ **$470**, rising with Rule growth | Rule-11 / frame change |
| **3** | **Done three-act verb**: `dwork done-record` composes `Y done (merges PR #a at <head>)` from git and writes the trace; `dwork close --when-landed` checks ancestry and closes | 123 record + 48 close commits; 22 re-records; the landing-loop recovery rows | 4–6 | ≈ 171 × 4 ≈ 680 calls ≈ **$140** + recovery rows | code (core CLI) |
| **4** | **Session housekeeping as commands**: `dyad session bank-check` (unpushed branches, dirty trees, `Y done` heads not on `main`, open PRs), `dyad board` (the board report), a sync report | 51 rows; 729 k output tokens over 16 traces | most of a d-work: 28–95 calls per trace | ≈ 51 rows × $8.7 ≈ **$440** (derived: 729 k × $0.19/k ≈ $139 over 16 traced rows, ≈ $8.7 per row) | code (core CLI) |
| **5** | **Work at small context**: one seat per question (the cabinet shape), and reading-heavy work (mining, audits, record sweeps) delegated to subagents whose context is discarded, on a cheaper model where judgment allows | the September craft sessions at 530–680 k context, $290–$1,738 each; 0% delegation in 24 of 28 traces | — | not derivable per act; the cabinet sessions cost 3–32% of a craft session each | conduct / preference |
| 6 | **Plan skeleton** from `PLAN_PARTS` (`dwork new --plan`), with base commit and files touched filled | 223 plans written freehand, 44 revisions for omissions | 1–2 | ≈ $60 | code |
| 7 | **`dyad check --guard <label>`** (#204 #1) | full checks run to read one guard line | 0 calls; ~40 s and its output each | small in tokens | code |
| 8 | **Date-ordered incident append** (`dyad incident add`) | 80 single-row commits; merge chains on tail-append | 2–4 on conflict | ≈ $30 + conflict recoveries | code |
| 9 | **Refuse a value starting with `--`** as a title or `-d` text | 6 malformed rows, 8 incidents, each a recovery row | — | small; removes a recurring incident mode (G) | code (guard) |
| 10 | **The activity miner as a `dyad` verb** (this audit's scripts) | the 4th hand-run activity audit (#154, #161, #204, #333) | — | one audit's mining ≈ $2 here; recurrence ~2 weeks | code |

Release and version sequencing (68 commits, 50 tags; the most disposition-heavy class at 2.52
entries per row) is not ranked: its cost is ordering across zones and Operator questions, not tool
calls, and #230 and #156 already reshaped it.

### What this audit does not support
- **Shortening replies or plans for their own sake.** Output is 10% of cost (§2). A plan matters by
  being re-read, so candidate 5 (context) moves more than any word count.
- **Cheaper models for the main seat.** Not measured here, and not the Agent's call to make.
- **Pushing less.** Pushes are the Rule-3 record. Making each one cost one call (candidate 1) is the
  survivor; pushing less often is not.

## 6. Reproducing the numbers
The mining reports, scripts and the per-session usage table are banked as stored text in
`2026-10-17-token-efficiency-data.md` (d-work #338); this d-work adds no code (plan #333). Each figure above can be re-derived with:
- sessions: `list_sessions` (mine, paged), filter `session_context.sources[].git_repository.url`
  containing `dyad-system`, sum `external_metadata.usage`; price as in §2.
- commits: `git log origin/main --numstat --no-renames --format='%H|%P|%aI|%s'`; ledger-only = every
  path under `agent-corpus/d-work/`; zones from `python3 dyad/guards/infra/containment.py zones`.
- PR size: `git rev-list --no-merges --count <merge>^1..<merge>^2` per `Merge pull request #N`.
- rows, plans, provenance: `key: value` lines of `rows/*.md`; `wc -c plans/*.md provenance/*.md`.
- traces: the bucket and count lines of `traces/*.md` (format: `dyad/playbooks/dwork-trace.md`).
- frame: `wc -c CLAUDE.md dyad/CLAUDE.md dyad/rules/RULE-*.md dyad/vocabulary/VOCABULARY.md preferences-corpus/PREFERENCES.md`.
Candidate 10 is the proposal to make this a command.
