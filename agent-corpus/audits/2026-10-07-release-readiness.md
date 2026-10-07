# Release readiness: what the next release delivers, and what is holding it (2026-10-07)

*d-work #231. The Operator's prompts, verbatim: "evaluate readiness for next release by scanning all
active branches", then "what are the significant enhancements that the new release would bring". The
branch scan is the method named for the second question, not the whole of it. This audit detects and
sizes; it changes no Rule and no code, cuts no tag, and opens no row. The decision to hold countersign
and disclosure out is the Operator's, disposed in #232.*

**On the seconds below:** an absolute second is a property of one machine and one day; only a ratio
travels (carried from `2026-10-02-test-execution-profile.md` §0). Every figure in Part A1 is read from
the audit that measured it — `2026-09-30-test-performance-refactor.md`, n = 3 in each of two
independent clones — and none is re-derived here. Read the ratios.

## Method
1. `git fetch --all --prune --tags`; fast-forward `main`, which was 240 commits behind this checkout.
2. All 160 remote branches: `git rev-list --count origin/main..<branch>`, and the three-dot diff of
   every branch that is ahead; `gh pr list --state open`; the one local branch.
3. Per component, `<newest tag>..HEAD -- <root>`: commit subjects, files changed, insertions, deletions.
4. Every `VERSION` against `git tag -l '<component>-v*'`; `BUNDLE.md` rows against the tree; every
   craft's `MANIFEST.md` `requires:` floor against the tags that exist.
5. `dyad check` locally — exit status and `fail` count, not a glance at the tail;
   `gh run list --branch main` and the failing job's own step list.

## Part A — what the release would deliver

The core craft is 27 commits and 75 files past `dyad-operator-v0.9.0` (`+5920 / −756`). Grouped by
what a downstream installation gains, not by commit.

### A1. The push gate stops costing two and a half minutes (#199, and #164, #162, #176 within it)
| act | before | after | ratio |
|-----|-------:|------:|------:|
| `check --guards`, empty range | 145.16 s | 2.68 s | **0.018** |
| `--pre-push`, tree already passed (suite memo) | 147.41 s cold | 2.73 s hit | **0.0185** |
| `check --evidence` (the merge evidence) | 143.52 s | 149.24 s | 1.040 |

The **suite memo** is a per-checkout record that one exact tree passed every root of Rule-12's suite,
keyed by the tree's sha256, the interpreter, git's version, the roots run and the instance's settings.
The pre-push path reads it; `check --evidence` never does. That asymmetry is the design, and the third
row is its proof: the evidence path became *slower* — the cost of 39 more tests, 0.998 per test, inside
the noise floor — because no skip may make the merge evidence cheaper. An empty range skips for the
same reason a ledger-only range does: there is nothing for the suite to judge. And an installed,
unmodified craft tree skips its own test root at the gate, so a downstream system does not re-run the
author's tests to push its own ledger.

### A2. The test mass shrank without losing a check (#203)
`dyad/tests` went **634 → 584** cases across six nodes, each measured at its own head:

| node | what it did | Δ cases |
|------|-------------|--------:|
| N1 | retire the irrelevant — a stale-floor test, a live `>40 incidents` pin | −1 |
| N2 | merge the overlaps — tests whose assertion a surviving check already made | −39 |
| P1 | syseng's fail-loud invariant protocol as a craft rule (its guard: +9 cases) | 0 |
| P2 | core modules enforce their pure `INVARIANTS` at import | +2 |
| P3 | the syseng guard fails a core module that does not enforce them | 0 |
| N3 | 12 tests become fail-loud checks at their strategic points | −12 |

A **fail-loud check** is a check in the code itself — not a test, not error handling — that raises when
a condition that should be impossible holds, placed where control passes once per process or rarely: a
module's import-time `enforce`, or a function that raises before the one write it guards. A broken data
model now fails on load rather than waiting for a suite, and `TREE_INVARIANTS` holds the predicates that
must read the tree instead of smuggling I/O into an import.

### A3. A system can put its host records where it wants (#175, #179, #169)
`host-path` and `host-zone` become Operator preferences, seeded by the template: a system that keeps no
separate host corpus runs **four** zones with its host records in `infra`, one that does keeps **five**.
The manifest gains a `profile` cell (`authoring` / `operating` / `both`) and a system's own operating rows
become its instance contribution — the core craft stops shipping one machine's operating dependencies to
every install. `.claude/*` is classified `infra`, so committed harness adapters have a zone. The host
tests are hermetic: a suite run never touches the real host.

### A4. Provenance fails where the gap is born, not forever after (#191)
The provenance guard splits in two by what a failure costs. A **transaction** check judges each pushed
commit against its parent — a new row brings its words, a `backlog`→`open` brings the prompt, k new
dispositions bring k entries, and a record only ever grows — so a gap fails on the push that creates it,
in the session that wrote it, including a concurrent session that never loaded the Rule. The **state**
check reads an instance-owned legacy list instead of a hard-coded `SINCE_ID` that had drifted into
warning about unrelated rows and exempting rows that held dispositions. `dwork new|state` refuse to write
a row or a disposition without its words, and make every refusal before the first write.

### A5. The pre-push hook judges what git is actually pushing (#194)
It read `origin/main..HEAD` and the tree on disk. It now reads the refs from git's stdin and refuses a
push it cannot judge — a ref that is not the checked-out HEAD, or a working tree with changes the push
does not carry. A deletion, or a ref already on `origin/main`, carries no new commit and passes. This
audit's own session hit the new refusal once, for an uncommitted presence file: it works.

### A6. Two recurring clerical faults are fenced at the source (#133)
A `;` inside disposition text used to split into a second ledger entry and fail Rule-7 property 5 — four
recurrences across #47, #67 and #100. `dwork new` used to take a flag such as `--backlog` as the row's
*title*, which is immutable, so six rows on `main` are permanently titled `--backlog`. Both are refused
at the source now. A downstream system inherits the fences without inheriting the scars.

### A7. Measurement and review become standing procedures (#213, #223, #166, #227)
- **d-work trace** — one d-work's measured time from its first anchored prompt to its Done-`Y`, every
  second in exactly one bucket (the Operator's wait, the Agent's inference, or a mechanical kind), with a
  play-book, a run-book, a store and its own guard. The new preference `dwork-trace` decides whether every
  completion cites one. No transcript is ever committed (Rule-7 property 2), so an ephemeral session's
  timing survives the session.
- **the standing audit play-book** — the review exercise, repeatable rather than re-invented.
- **ds-report-incidents** with one parser for the incident log, and the trace store checked in the guard
  pass rather than only inside the suite, which a guard-only push had skipped.

### A8. The Tended crafts
- **syseng** — the fail-loud invariant protocol as a craft rule, plus the guard that fails a core module
  which does not enforce its `INVARIANTS` (`+529 / −76`). This is the rule behind A2.
- **sysarch, sysadmin** — read the host path (A3); sysadmin also loses a duplicated rule table.
- **countersign and disclosure are not in this release.** The Operator has disposed that they are not
  meant for release yet and are held until ready (#232). Both are unreleased and absent from `BUNDLE.md`,
  which Rule-11 property 7 permits while a craft has no tag, and `dyad bundle build` builds once per row,
  so nothing publishes them. Named here only to record that they are *not* part of what this release
  delivers.

**In one line.** The release makes the practice cheap to run (A1, A2), portable to a system shaped
differently from this one (A3), and self-recording where it had relied on the Agent remembering (A4, A6,
A7). Four components: dyad-operator, sysarch, syseng, sysadmin.

## Part B — readiness

### B1. Nothing is waiting to be merged
Of 160 remote branches, three carry any commit `main` lacks, each exactly one ledger-only commit:

| branch | commit | status |
|--------|--------|--------|
| `origin/ledger-198-open` | `ledger: #198 opened` | superseded — row 198 on `main` is `done` |
| `origin/ledger-206-open` | `ledger: open #206` | superseded — row 206 on `main` is `done` |
| `origin/ledger-224-open` | `ledger: open #224` | superseded — row 224 on `main` is `done` |

Each landed by a later branch that carried the same row forward; the three refs are leftovers, not work.
`gh pr list --state open` is empty. The one local branch, `agent/178-chat-surface`, is 0 ahead. The hold
#198 placed on the release — PRs #223 and #224 — is discharged.

### B2. Every component is unreleased, and the core's number understates its tree
| component | `VERSION` | newest tag | commits to its root since `VERSION` was set |
|-----------|-----------|-----------|---------------------------------------------|
| dyad-operator | 0.10.1 | `dyad-operator-v0.9.0` | 21 |
| sysarch | 0.3.0 | `sysarch-v0.2.2` | 0 |
| syseng | 0.4.0 | `syseng-v0.3.0` | 2 |
| sysadmin | 0.2.1 | `sysadmin-v0.1.3` | 1 |
| countersign | 0.2.0 | none (held, #232) | 2 |
| disclosure | 0.1.0 | none (held, #232) | 0 |
| bundle | 0.12.1 | `v0.11.0` | — |

Part A is what `0.10.1` is labelling: a new guard, amendments to Rules 1, 3, 7, 11, 12 and 14, and changes
to the one distribution code path. That is minor-level change wearing a patch label. syseng is the same
case one order smaller — its `0.4.0` predates A8's protocol. No guard fails either number, because
neither version is tagged, so the drift guard has nothing to compare; these are corrections owed, not
gates.

### B3. The tag order is forced
sysadmin, sysarch and syseng each declare `requires: dyad-operator>=0.10.0`; disclosure declares `>=0.9.1`.
The floor resolves against tags, and the newest core tag is `0.9.0` — so **every craft's install is
refused today** for an unmet `requires:` (Rule-11 property 2), one `dyad check` warn per craft saying
exactly that. The core tag must exist, at ≥ 0.10.0, before any craft tag; the bundle last.

`BUNDLE.md`'s row set is settled by #232: four components. The #170 ordering problem — a craft-zone
`VERSION` bump and an infra-zone `BUNDLE.md` row that no order lands separately — therefore does not arise
for this release. It returns whenever either held craft is first released, and its backlog row stands.

### B4. Blocker: the only mechanical check of what a release publishes is red
`rule-11 package` has failed on every push to `main` since 2026-09-25, most recently at `0699b69`
(2026-10-06). The failing step is, verbatim: *install core, then export and install the sysadmin craft,
into a scratch repo; run the guards there; install both again (idempotent)*. The `check` and `build` steps
of the same job pass. That step is Rule-11 property 5's only mechanical check of the install path, and an
install of that path is precisely what a release publishes.

Row #201 holds the diagnosis: the core install writes a bundled craft's tree but no `crafts/REGISTRY.md`
row, so a subsequent `craft install` of that same craft is refused as locally authored. Row #228 is open
to repair it.

Locally the runner is green — `dyad check` exits 0 with no `fail` line, 130 package files, warnings only
(the craft floors of B3, the Rule-4 Agent-token warnings, the invariant follow-ups, two stale
`naming_rules.txt` allows, `pydantic` declared with no token). Local green and hosted red do not
disagree: the red step installs into a scratch repo, which the kernel-only path never does. Rule-14
property 3 makes that path the merge evidence, and it is — but it says nothing about the install.

### B5. Verdict
**Not ready, and the cost of the hold is explicit.** Part A is what sits behind B4: a 55× cheaper push
gate, a smaller suite, a portable host layout, and four fences that keep the practice honest without the
Agent remembering to.

| item | kind | state |
|------|------|-------|
| `rule-11 package` install step | blocker | #201 diagnosed, #228 open to repair |
| core `VERSION` → 0.11.0 | correction owed | its own agent-zone PR |
| syseng `VERSION` → 0.5.0 | correction owed | its own craft-zone PR |
| countersign, disclosure in the bundle | decided | held out (#232) |
| tag count and order | decided | five tags, core first, bundle last |

When the blocker clears and the two versions are corrected, the sequence is `dyad-operator-v0.11.0`,
then `sysarch-v0.3.0`, `syseng-v0.5.0`, `sysadmin-v0.2.1`, then the bundle's own `vX.Y.Z` — each its own
counter-prompt (Rule-11 Ratification events) unless the Operator takes the release-batch form. Cutting
anything before the blocker clears means publishing the core-then-craft upgrade path that every
downstream system takes, unverified for twelve days and known broken. That is the Operator's to dispose;
this audit's recommendation is to clear #228 first.

Disposition: see ledger #231.
