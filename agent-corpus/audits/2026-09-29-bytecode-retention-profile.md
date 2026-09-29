# Bytecode-retention profile — what the write suppression actually costs (2026-09-29)

*d-work #190, refs #180 #185 #192. Measured by a delegated sub-agent in three throwaway clones under
`/tmp`; nothing in the working repo was touched and no `__pycache__` was deleted at any point. Raw
per-run data: `/tmp/claude-0/prof190-out/{part1,part2,part2b}.tsv` and the gate transcripts beside
them — session-local, not corpus, and gone with the container. Every figure below that comes from
those files is marked; the paired and three-way blocks come from the run log only. Detects and
counts; disposes nothing.*

**§0, carried from `2026-09-25-optimization-opportunities.md`: an absolute second is a property of
one machine and one day; only a ratio travels.** Every absolute here is given beside its ratio, and
the ratios are what a later reader should use.

## The question
`dyadlib.load_module` sets `sys.dont_write_bytecode = True` around every by-path import, and
`dyad/guards/craft/crafts.py` does the same inside the floor-check subprocess template. Row #185
asked whether that line is worth its keep. Three arguments in this corpus — #185's row, #187's
accepted answer and #183's reply — had reasoned about its cost without anyone measuring it. This is
the measurement.

## Environment
4 CPUs, 16 GB, kernel 6.18.44-fc-v37. Interpreter the runner resolves: `/usr/bin/python3.13`
(3.13.12); `/usr/local/bin/python3` is 3.11.15, below the Rule-14 pin, and `dyad/bin/dyad-python`
correctly skips it. Every suite run as `dyad/bin/dyad check --tests <root>` — the runner's own child
(Rule-12 property 2), never a hand-typed `unittest discover`. 1-minute load average recorded before
every timed run; any block taken under contention was re-run quiet and both sets kept.

Three clones, each `git clone --no-hardlinks` + `git config core.hooksPath dyad/hooks`:
`prof190` baseline (unmodified), `prof190b` suppression off (both sites `True`→`False`, 2 files /
2 insertions / 2 deletions), and `prof190c` — a second suppression-off clone, built mid-run as a
control, which is what makes this audit worth reading.

## Part 1 — baseline, from a clone holding zero bytecode
`part1.tsv`. Bytecode before the first run: **0 directories, 0 files.**

| root | run 1 | run 2 | run 3 | tests | run 1 vs the later mean |
|------|------:|------:|------:|------:|------:|
| `crafts/disclosure/tests` | 0.75 | 0.75 | 0.75 | 35 | ±0% |
| `crafts/countersign/tests` | 1.35 | 1.42 | 1.35 | 41 | −2.5% (joint fastest) |
| `crafts/syseng/tests` | 1.45 | 1.51 | 1.47 | 53 | **−2.7% (fastest)** |
| `crafts/sysarch/tests` | 2.61 | 2.88 | 2.66 | 89 | **−5.8% (fastest)** |
| `crafts/sysadmin/tests` | 5.07 | 5.52 | 5.45 | 100 | **−7.6% (fastest)** |
| `dyad/tests` | 106.80 | 102.36 | 101.69 | 530 (3 skipped) | +4.7% |

Gate paths, once each: `check --guards` **115.41 s**, `check --evidence` **119.64 s**, both exit 0.

After Part 1: **19 `__pycache__` directories / 68 `.pyc` files**, and **none under any guard-module
directory** — `dyad/guards/*/` and `crafts/*/guards/` stayed clean, which is precisely what the two
suppression sites are for. `__pycache__/` is `.gitignore:5`, so `git status` stayed clean throughout.

**Finding 1 — retaining bytecode does not make the later runs faster.** Four of six roots have run 1
as their *fastest* run, on a clone where run 1 is the one creating every cache. Nothing resembling
the 2× first run `#180` saw.

## Part 2 — the suppression removed
`part2b.tsv` (quiet); `part2.tsv` holds the contended first attempt and is kept for the record.
Bytecode before: 0 / 0. All 848 tests pass and **no guard flags the change**, corroborating row
#185's claim that the line is untested.

After Part 2: **26 directories / 92 files.** The difference from Part 1 is exactly **7 directories
and 24 files**, and they are exactly the guard-module directories:

```
dyad/guards/agent/__pycache__          crafts/sysadmin/guards/__pycache__
dyad/guards/craft/__pycache__          crafts/sysarch/guards/__pycache__
dyad/guards/infra/__pycache__          crafts/syseng/guards/__pycache__
dyad/guards/preferences/__pycache__
```

**Finding 2 — three of the seven are inside craft trees.** That is what the suppression prevents,
stated exactly: 7 directories and 24 files, three craft trees, no more.

## Part 3 — the comparison, and the result that was withdrawn
| root | base mean | off mean | Δ | Δ% | larger than within-condition spread? |
|------|----------:|---------:|------:|------:|---|
| `crafts/countersign/tests` | 1.37 | 1.39 | +0.02 | +1.5% | no (spread 0.07 / 0.04) |
| `crafts/disclosure/tests` | 0.75 | 0.68 | −0.07 | −8.9% | marginal (spread 0.00 / 0.01) |
| `crafts/sysadmin/tests` | 5.35 | 5.38 | +0.03 | +0.6% | no (spread 0.45 / 0.19) |
| `crafts/sysarch/tests` | 2.72 | 2.16 | −0.55 | −20.4% | comparable to spread (0.27 / 0.31) |
| `crafts/syseng/tests` | 1.48 | 1.54 | +0.06 | +4.1% | no (spread 0.06 / 0.13) |
| `dyad/tests` | 103.62 | 104.02 | +0.40 | +0.4% | no (spread 5.11 / 5.48) |
| `check --guards` | 115.41 | 117.23 | +1.82 | +1.6% | no |
| `check --evidence` | 119.64 | 112.11 | −7.53 | −6.3% | no |

### The withdrawal — the most useful thing in this audit
Three runs per condition was not enough for `dyad/tests`, so the sub-agent ran **interleaved paired**
runs, then reversed the ordering to cancel ordering bias (run log, not TSV):

| pair | order | baseline | suppression off | Δ |
|---|---|---:|---:|---:|
| 1 | A→B | 106.13 | 98.18 | −7.95 (−7.5%) |
| 2 | A→B | 103.89 | 98.38 | −5.51 (−5.3%) |
| 3 | B→A | 102.24 | 94.79 | −7.45 (−7.3%) |
| 4 | B→A | 102.75 | 94.98 | −7.77 (−7.6%) |

Four pairs, both orderings, all the same sign, mean **−7.17 s (−6.9%)**. A 7% win for writing
bytecode — and **it is not real.**

A third clone, `prof190c`, carrying the identical two-line edit and never having run a gate, gave
100.82 / 102.79 / 103.88 s: indistinguishable from baseline. A three-way interleaved pass gave
base 106.15 / 108.64, `prof190b` 102.46 / 98.97, `prof190c` 102.11 / 105.95. Pooled over the whole
session: baseline **104.52 s** (n=9, spread 6.95), `prof190b` **99.98 s** (n=9, spread **11.55**),
`prof190c` **103.11 s** (n=5, spread 5.13).

**Two clones of identical code differ by 3.1 s, and the faster one has the largest internal spread of
any condition.** The −7 s was a property of one clone's history, not of the flag. It is unexplained —
"the gate warms the guard `.pyc` cache" was considered and rejected, since `prof190c` writes all 23
guard `.pyc` files during its own first run and is still ~103 s — and it is published here rather
than deleted, because a paired, both-orderings, same-sign result across four trials is exactly the
kind that enters a corpus as fact when the profile stops one experiment early.

**The method finding, for whoever profiles next: pairing and order-reversal do not protect you from a
per-artifact offset. The control that catches it is a second, independently built copy of the
identical code.**

### The one effect that replicates
`crafts/sysarch/tests`, three-way interleaved, 5 passes: base mean **2.660**, `prof190b` **2.314**,
`prof190c` **2.346**. Both suppression-off clones agree with each other and sit **0.33 s (−12.5%)**
below baseline, with all **10 paired comparisons negative** across two independently built clones.
Plausible mechanism: sysarch's suite by-path-imports guard modules repeatedly, which is exactly what
the suppression stops from caching.

Stated precisely: 0.33 s is *about the size of the within-condition single-run spread* (0.27–0.41 s).
It is not distinguishable in an unpaired comparison; it is distinguishable only as a paired, repeated
effect. **In context it is 0.33 s out of ~115 s of total suite time — 0.3%.** Real and negligible.

`disclosure` paired 5× gave −0.07, −0.07, −0.10, −0.04, **+0.11**; `syseng` gave −0.06, −0.07, −0.07,
**+0.09**, −0.28. One reversal each, magnitude ≈ spread. Not distinguishable.

## The three answers
1. **Does retaining bytecode make runs 2 and 3 faster?** No. Run 1 is fastest on four of six roots
   from a zero-bytecode clone. **The 195.9 s first run of #180 was not bytecode** — #180 deleted the
   caches before a warm run and saw nothing; #190 started with none and saw no first-run penalty.
   Both approaches now agree, from opposite directions.
2. **Does writing bytecode make anything faster?** Only `crafts/sysarch/tests`, by 0.3% of total
   suite time. Nothing got meaningfully slower. **The suppression costs about 0.3 s per full gate**
   and buys 7 fewer `__pycache__` directories and 24 fewer `.pyc` files, three of them in craft trees.
3. **Is any difference larger than the within-condition spread?** Essentially no. On the dominant
   root and both gate paths, retaining and writing bytecode are **not distinguishable from noise**.

**Bottom line: the suppression is a determinism and cleanliness measure. The performance argument,
in either direction, is not supported by these numbers.**

## Consequences for #185
- **Option 4** — compile the cache `--invalidation-mode checked-hash` at install and drop the
  suppression, which #192 established is honoured by the by-path loader — buys back 0.3 s per gate at
  the price of a `compileall` step in the one install code path (Rule-11 property 5). **Refused on
  price.**
- **Option 2b** — drop the suppression outright — buys the same 0.3 s, gives up the property #192
  measured (a by-path import returning `111` from a source reading `222` when two same-size writes
  share an mtime) and writes bytecode into three craft trees. **Refused.**
- **Option 2a** — keep both suppressions, stop `manifest.py` scanning generated directories, correct
  the docstring — survives, now with a measured cost in place of an assumed one.

## Three observations, not findings of this measurement
1. **A push gate on an *empty* range pays the full suite.** `package.py` `ledger_only_range` ends
   `return bool(paths) and all(...)`, so an empty range is `False` and Rule-12's suite runs: the fresh
   clone's `check --guards` cost **115.41 s** where a genuinely ledger-only *non-empty* range costs
   ~2.3 s. This is backlog row **#164** (`#161` candidate C1) arrived at from the opposite direction —
   corroboration, not a new row.
2. **`suite_env()` sets no `PYTHONDONTWRITEBYTECODE`.** It returns `DYAD_NO_NESTED_TESTS` and drops
   `GIT_VARS`; only `dyad/tests/test_package.py:20` and `.github/workflows/dyad-package.yml:23` set
   the variable. The line that actually holds is the two `sys.dont_write_bytecode` sites, and only for
   by-path imports. My own earlier claim to the contrary is quoted inside
   `agent-corpus/d-work/provenance/183.md` — because the Operator's prompt quoted it back to me — and
   **that record is not corrected**: Rule-7 property 4 holds the Operator's words, and editing it
   would destroy the evidence of the error. The correction lives here and in `INCIDENTS.md`.
3. **195.9 s was never reproduced.** The slowest of 23 `dyad/tests` runs was 108.64 s. The container
   was warm throughout and there is no privileged way to drop the page cache here, so #183's
   cold-page-cache hypothesis stays untested from this side — narrowed, not answered.

## Disposition
Disposed by the Done-`Y` of d-work #190 (Rule-2, Rule-9 Form); see ledger #190.
