# Test-performance refactor — what the six nodes of #199 bought (2026-09-30)

*d-work #199, node M, plan `agent-corpus/d-work/plans/199.md` (Falsification A5, the M row, Revision 2).
Measured 2026-10-01 by a delegated sub-agent in three throwaway clones under the session scratchpad.
Nothing in the working repo was touched, and no ref outside the clones moved. The raw per-run data
(`out/runs.tsv`, `out/runs2.tsv` and one log per run) is session-local, not corpus, and goes with the
container. Detects and counts; disposes nothing. Each finding below is proposed as a backlog row and
none is opened.*

**§0, carried from `2026-09-25-optimization-opportunities.md`: an absolute second is a property of
one machine and one day; only a ratio travels.** The absolutes are printed so the ratios can be
recomputed. A later reader should use the ratios. **§ method, carried from
`2026-09-29-bytecode-retention-profile.md`: pairing and order reversal do not catch a per-artifact
offset; a second, independently built copy of identical code does.** The per-node drafters skipped
that control. This audit restores it.

## Method
Three clones, each made with `git clone --no-hardlinks /home/user/dyad-system` and then
`git config core.hooksPath dyad/hooks`:
- **BASE** at `0d0ed58`, the plan's base commit;
- **AFTER** at `e236e6c`, the head of `origin/dwork-199-n5`, which carries the whole stack N0→N3a→N1→N2→N3b→N5;
- **AFTER2**, a second clone of `e236e6c` built independently. It is the control, and the
  AFTER/AFTER2 ratio is the noise floor.

The git-ignored `agent-corpus/provenance_legacy.local.txt` was copied into each clone, byte-identical
to the working repo's. Every clone stayed clean (`git status --porcelain` empty), which the memo key
and the pre-push refusal both require.

Only the runner's own commands were used (Rule-12 p2):
- **(a)** `dyad/bin/dyad check --tests <root>` for every test root;
- **(b)** `check --guards` on an empty range, after `git update-ref refs/remotes/origin/main HEAD`
  inside the clone. In BASE this runs the full suite, which is the point;
- **(c)** `check --guards --pre-push` on `HEAD~1..HEAD`, a non-empty range that is not ledger-only.
  Stdin carried one ref line naming `HEAD`. The memo was deleted first; `check --evidence` wrote
  it; then the gate ran once with a memo hit; then the memo was deleted again and the gate ran cold.
  AFTER clones only;
- **(d)** `check --evidence` with the same `origin/main := HEAD~1`.

n = 3 per condition, interleaved by condition, with the clone order rotated each round:
B·A·A2, A·A2·B, A2·B·A. The 1-minute load was recorded before every run and stayed between 0.25 and
1.26. A second phase used the same rotation for N3a's two modules (`check --tests
dyad.tests.test_package`, `dyad.tests.test_craft`) and for N3b's guard (`dyad craft check`). It also
counted `/tmp/dyad-floor-*` before and after each run.

**Environment.** 4 CPUs, 15 GB, kernel 6.18.44-fc-v50, git 2.43.0. The interpreter the runner
resolves is `python3.13` (3.13.12), which `dyad/bin/dyad-python` tries first. Every exit code was 0
except (b), whose exit 1 is explained under Findings, item 10.

## Results

### Gate paths — the ratios the plan asked for
| act | BASE | AFTER | AFTER2 | AFTER/BASE | AFTER2/BASE | AFTER2/AFTER (noise) |
|-----|-----:|------:|-------:|-----------:|------------:|---------------------:|
| (b) `check --guards`, empty range | 145.16 | 2.68 | 2.64 | **0.018** | **0.018** | 0.984 |
| (d) `check --evidence` | 143.52 | 149.24 | 146.70 | 1.040 | 1.022 | 0.983 |
| (c) `--pre-push`, memo hit | — | 2.73 | 2.63 | | | 0.961 |
| (c) `--pre-push`, cold | — | 147.41 | 145.57 | | | 0.987 |

Mean seconds; n = 3 each. Spreads (max − min): (b) BASE 3.79, AFTER 0.24, AFTER2 0.15. (d) 13.05 /
7.95 / 6.88. (c) hit 0.27 / 0.06, cold 8.81 / 7.37.

- **N1 (empty range): 0.018 in both clones**, against a noise floor of 1.6%. At BASE the
  empty-range gate costs a full evidence run (145.16 / 143.52 = 1.011). The skip line printed was
  `skip [guards] Rule-12 suite: origin/main..HEAD is empty (d-work #164)`, 6 of 6 runs.
- **N2 (memo): hit / cold = 0.0185 (AFTER) and 0.0181 (AFTER2).** The cross-clone pairings give
  0.0188 and 0.0178, and hit / BASE evidence is 0.019. The skip line printed was `… already passed on
  this checkout (d-work #162)`, 6 of 6 hits. Every cold run ran the full suite (958 tests).
- **Evidence still observes.** AFTER/BASE 1.040 and 1.022 is the cost of 39 more tests (+4.2%).
  Per test it is 0.998 and 0.981, inside the noise floor (0.983). That is what the invariant
  requires: no node may make `--evidence` cheaper by skipping. A cold `--pre-push` costs what
  evidence costs (147.41 / 149.24 = 0.988).

### Test roots (a)
| root | BASE | AFTER | AFTER2 | AFTER/BASE | AFTER2/BASE | AFTER2/AFTER (noise) |
|------|-----:|------:|-------:|-----------:|------------:|---------------------:|
| `dyad/tests` | 133.88 | 131.36 | 133.55 | 0.981 | 0.998 | 1.017 |
| `crafts/sysadmin/tests` | 5.49 | 5.18 | 5.13 | 0.943 | 0.933 | 0.990 |
| `crafts/sysarch/tests` | 2.94 | 3.16 | 2.54 | 1.074 | 0.864 | 0.805 |
| `crafts/syseng/tests` | 1.80 | 1.75 | 1.76 | 0.970 | 0.976 | 1.006 |
| `crafts/countersign/tests` | 1.43 | 1.48 | 1.56 | 1.040 | 1.093 | 1.052 |
| `crafts/disclosure/tests` | 0.81 | 0.80 | 0.81 | 0.984 | 0.996 | 1.013 |

On the core root, the whole stack's change is inside the noise floor (0.981 / 0.998 against 1.017,
spreads 6–9 s). That holds while the root grew by 39 tests. Per test, the core root is **0.922 /
0.937** of BASE. No craft root moved by more than its own control spread; sysarch's control ratio
(0.805) is the widest, on a 2.5 s root.

### N3a's modules and N3b's guard (phase 2)
| act | BASE | AFTER | AFTER2 | AFTER/BASE | AFTER2/AFTER (noise) | `dyad-floor-*` left per run (B / A / A2) |
|-----|-----:|------:|-------:|-----------:|---------------------:|---:|
| `test_package` | 65.85 | 62.77 | 63.42 | 0.953 | 1.010 | **8 / 0 / 0** |
| `test_craft` | 16.11 | 17.88 | 18.22 | 1.109 | 1.019 | 0 / 0 / 0 |
| `dyad craft check` | 0.40 | 0.41 | 0.43 | 1.034 | 1.057 | **1 / 0 / 0** |

- `test_package` grew from 66 to 89 cases: N0 added 3, N1 4, N2 9 and N5 7. It is 0.953 of BASE as
  a whole and **0.707 per case**.
- `test_craft` (15 → 16) moved by less than its own spread (3.2–4.7 s, 20–29%).
- `craft check` is unchanged within noise. **N3b's leak fix is confirmed**: BASE leaves one
  `dyad-floor-*` directory per craft check and eight per `test_package` run; the stack leaves none.

### `Ran N` per root — must not fall
| root | BASE | AFTER | where the difference comes from |
|------|-----:|------:|-------|
| `dyad/tests` | 608 | **647** | +23 `test_package` (N0 3, N1 4, N2 9, N5 7), +4 `test_livetest` (N3a), +7 `test_crafts` (N3b), +1 `test_craft` (N5), +4 from #196's PR #223 (`test_crafts` 1, `test_manifest` 1, `test_dyadlib` 2), which landed on `main` after the base |
| `crafts/sysadmin/tests` | 94 | 94 | |
| `crafts/sysarch/tests` | 89 | 89 | |
| `crafts/syseng/tests` | 53 | 53 | |
| `crafts/countersign/tests` | 40 | 40 | |
| `crafts/disclosure/tests` | 35 | 35 | |
| total (evidence) | 919 | **958** | |

No root fell. N3a's three narrowed cases kept their count: they changed what each one spawns, not
whether it runs.

## Per-node results
| node | PR | claim, and its source | re-measured here | verdict |
|------|----|-----------------------|------------------|---------|
| N0 | #234 | none: test-only, the safety floor | not separable; 3 cases added | — |
| N3a | #235 | `test_package` **0.736**: 75.05 → 55.26 s, n=3 interleaved, N3a's head against its parent (commit `d2925f2`) | whole stack, `test_package` 0.953 as a module, carrying 23 more cases; **0.707 per case** | consistent with the claim, not confirmed; the node was not isolated (see What was cut) |
| N1 | #236 | **0.021**: empty-range `check --guards`, 139.83 → 2.97 s, n=3 interleaved (commit `1a55697`) | **0.018 / 0.018** (AFTER / AFTER2 against BASE); noise 0.984 | **confirmed** |
| N2 | #239 | **0.022**: memo hit 3.27 s against cold 149.50 s, n=3, one throwaway clone (Revision 2) | **0.0185 / 0.0181** (hit/cold within each clone); noise 0.961 on the hit | **confirmed**, now with a control |
| N3b | #240 | no measurable gain here, the floor check being 83% of `craft/crafts`' 0.21 s; estimated ~0.24 (~1.9 → ~0.45 s) once the 0.10.0 floor resolves (commit `5136123`) | `dyad craft check` 1.034 (noise 1.057); leaks 1 → 0 per call and 8 → 0 per `test_package` run | **no gain confirmed; leak fix confirmed**; the ~0.24 estimate is untested (no second floor resolves here) |
| N5 | #241 + #242 (craft-zone prose) | **0.056** on a scratch operating install: 129.12 → 7.19 s, n=3 (commit `e236e6c`) | not re-measured (cut). In this authoring repo, which has no registry rows, a cold `--pre-push` costs what evidence costs (0.988), as the node says it should | unverified here |

**What the stack buys, in one line each.**
- An empty range at the gate: about 2% of a full run.
- A tree that already passed: about 2% at the push gate.
- Evidence: unchanged.
- The core root: unchanged in seconds while it carries 6.4% more tests.
- `/tmp`: stops filling.

## Findings carried out of the execution — proposed backlog rows, not opened
1. `test_incidents.LiveTests.test_live_log_passes` (`dyad/tests/test_incidents.py` l.67) asserts more
   than 40 incidents, so the core suite fails on every fresh operating install. Found by N5's
   measurement.
2. `references.py` warns instead of skipping when a registry holds only the core row. Recorded in
   Rule-11's record, amendment #199, attack A5: the siblings `sysarch` and `syseng` read
   `warn … absent and not in crafts/REGISTRY.md` where they read `skip`.
3. Bundled crafts get no registry row, so their roots always run at an operating system's gate
   (#201).
4. The `merge_base=False` branch of `dyadlib.ledger_only` (l.297) no longer serves the caller its
   docstring names (#155's suite skip, which N1 moved to `range_paths` directly). **Correction to
   the finding as carried:** it does have a caller at the stack's head, N2's second memo clause
   (`package.py` l.309). What remains true is that the docstring is stale (N1, N2).
5. `package.py`'s REPO discovery (l.92–93) strips a hand-written tuple (`GIT_DIR`, `GIT_WORK_TREE`,
   `GIT_INDEX_FILE`) that lacks `GIT_COMMON_DIR`, instead of calling `dyadlib.git_env()`, whose
   `GIT_VARS` has all four (N0).
6. `/tmp/dyad-floor-*` directories leaked before N3b remain on this host. There were 1,402 when this
   measurement started and **1,564 after it**: this audit's own BASE runs, at pre-N3b code, added
   162 (8 per `test_package` run, 1 per craft check, and the rest from BASE's gate and evidence
   runs). Removing them is a host action (Rule-8). Not done.
7. N3b's batch-child residual: a target that mutates a shared preseeded module, `os.environ` or the
   cwd could affect later targets in the same floor child.
8. `test_package`'s composition tests could share one output per runner verb, saving about 5 s
   (N3a).
9. A Tended craft's `requires:` dependencies are not hashed into its root's skip (Rule-12's record,
   amendment #199 (N5), attack 6).
10. *New, found by this measurement:* `check --guards` on an empty range exits 1 because
    `agent/prs` fails it with `PR body cites no 'd-work #N'`, at BASE and AFTER alike. N1 made that
    run take 2% of the time, but its verdict is still red. The hook never meets an empty range
    (`pushed_refs` returns None for a ref already on the base), so this only affects the Agent's own
    hand-run.

## Departures from the plan, as executed
- **Revision 2, R2-1.** The base sha is out of N2's memo key, and a digest of `<instance>/*.local.txt`
  is in it. Disposed by the plan-`Y` of revision 2.
- **N3b's cache lives per `check_package` call, not per process.** `FloorCache` is built once per
  call. The plan said "per process".
- **N5 added two conservative rules the plan did not name:** a range that changes the registry runs
  every root, and a Tended root skips only while the core is unmodified too.
- **The `INCIDENTS.md` append conflict with `main` is deferred to landing.**
- **The drafters skipped the control clones.** A5 asked for them; each node's figure came from one
  clone, or one clone per condition. This audit restores them for N1, N2, N3a's modules and N3b. N1's
  and N2's figures survive the control.

## What was cut, and why
- **Per-node isolation.** Only BASE and the stack's head were cloned. N3a's 0.736 is therefore
  neither confirmed nor refuted, since 23 cases were added across the same span. Node-level figures
  would need one clone pair per intermediate head, at about 25 min per node at n=3.
- **N5's scratch operating install.** Not rebuilt; its 0.056 stands as the node measured it, without
  a control.
- **(c) in BASE** was not run, as instructed: BASE has no memo.
- **The baseline is not `0d0ed58` plus the six nodes alone.** AFTER also carries #196's PR #223
  (`097e7ac`), merged to `main` after the base, with 4 tests and a `crafts.py` comment.

## Disposition
Disposed by the Done-`Y` of d-work #199 (Rule-2, Rule-9 Form); see ledger #199.
