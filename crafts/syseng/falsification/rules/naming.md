# Falsification record — syseng craft rule `naming.md` (d-work #162)

**Claim:** One table, one owner per pattern, checked as data, is the fix for name drift (#113).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The table and the data file drift: a kind is added to one and not the other. | **Confirmed** | The guard fails on a `kind:` whose pattern is not a table row (`check_table`); the reverse (a table row without a kind) is the `checkable` column's *no*, stated. |
| 2 | `fnmatch` globs span `/`, so `crafts/*/rules/*` selects `crafts/x/falsification/rules/y.md` and false-positives. | **Confirmed** | `glob_re`: `*` is one segment, `**` any (`test_glob_re_segments`). |
| 3 | A committed-only view misses a badly named file until after its commit. | **Confirmed** | `git ls-files -co --exclude-standard`: untracked, not-ignored files are judged too. |
| 4 | Legacy paths are grandfathered and the list grows. | Refuted | Allow lines carry a reason, fail when stale, warn when unneeded; two at 0.1.0. |
| 5 | Symbol rules over `_`-prefixed helpers demand a contract they never promised. | **Confirmed** | `_`-prefixed modules are not judged by symbol rules (as the registry ignores them). |

Cut from: nothing verbatim — collected from Rules 3, 4, 9, 11, 15, 16, 20, the README and the vocabulary (plan #162 (a)1).

## Amendment — d-work #141 (2026-09-14, the `mode:` kind)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 141.4 | Nothing checked the mode of the files the host executes by name (`dyad/bin/dyad`, `dyad/hooks/*`, a craft's shipped `*.sh`); one of them already shipped at 644 and could not exec. | **Confirmed** (#135, `entrypoint.sh`) | A `mode: <pattern> = <path glob> = <tracked mode>` kind, four globs, checked like a `kind:` (pattern must be a table row) against git's index. |
| 141.5 | A mode is not a name; this is the naming guard checking content. | Refuted | It checks what the *name* promises — a file under `hooks/` is called by name by git, one under `bin/` by the Operator — the same shape as `<entity>_rules.txt` requiring `<entity>.py` beside it. No content is read. |
| 141.6 | A scratch install or a fresh clone has these paths untracked, so the guard fails an install that is fine. | Refuted, tested | Untracked warns and falls back to the disk bit; CI commits the scratch tree before running the guards, and `distribute` copies the executable bit. |

Disposition: see ledger #141.

## Amendment — d-work #15 (craft-contributed data)
**Claim:** an installed craft may contribute its own `kind:`/`mode:`/`symbol:`/`env:`/`allow:` rows
directly (`crafts/<craft>/guards/naming_contrib.txt`), discovered and merged into the checks that
run over the tree, without needing to be a row of *this* table.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 15.1 | The rows that should move to a craft (sysadmin's `<ops>/…`/`<runbooks>/…`/mode rows, lan-git's workflow allows) can be proved live, right now, in this repo. | Refuted | This repo installs only `sysarch` and `syseng` (`ls crafts/`); neither sysadmin nor lan-git is here. The mechanism is proved by tests against a scratch craft; no native row moves. |
| 15.2 | The file name plan #153/#1 first named, `crafts/<craft>/guards/naming_rules.txt`, is the contributed file. | Refuted | That path matches the existing `<entity>_rules.txt` kind and fails its own `beside` group (`naming.py:162`) in any craft without a `naming.py` — every craft but syseng. A distinct suffix, `_contrib.txt`, was needed, with its own kind row and a narrowed glob on the neighbouring `_rules.txt` row so the two do not double-match one file. |
| 15.3 | A contributed `kind:`/`mode:` pattern must be a row of `rules/naming.md` like a native one, or the table and the data can drift silently (attack 1's own finding, turned back on this amendment). | Refuted | It is documented in the *contributing* craft's own rule, which owns it — requiring a syseng-table row for another craft's pattern would recreate the drift attack 1 fixed, one level up. `check_table` runs on the native `kind`/`mode` lists only. |
| 15.4 | The `env:` unlisted check (a var read but declared nowhere) can be run once per source, native and each contributing craft, and just concatenate the results. | **Confirmed**, then fixed before merge | The first implementation passed `found={}` to skip the per-craft call's *unlisted* sub-check, which also zeroed its *stale* sub-check (`n not in found` was vacuously true for every name) — every contributed `env:` token reported stale even when read. Caught by `test_contributed_env_recognized_and_stale_names_its_craft` before this PR was opened. Fixed: `check_env` gained an explicit `check_unlisted` flag; the real `found` dict is passed to every call, native and contributed alike. |
| 15.5 | Removing a craft's `naming_contrib.txt` (or the craft itself) leaves its rows stale somewhere, the way a native row does when its target is gone. | Refuted, tested | A contributed row simply is not discovered; its paths, if any linger in the tree, match no kind and are never mentioned — `test_craft_absent_means_its_rows_are_simply_gone`. The asymmetry with a native row (which *does* go stale when its target disappears) is the whole point: a craft's own rows are its own responsibility exactly as long as it is installed. |
| 15.6 | A malformed contributed line is silently absorbed into `naming_rules.txt`'s own "malformed line" report, obscuring which craft wrote it. | Refuted, tested | `check_package` parses each contributed file separately and prefixes its own bad lines with that craft's own path (`crafts/<craft>/guards/naming_contrib.txt: malformed line …`), never `naming_rules.txt` — `test_malformed_contributed_line_names_its_craft`. |

**Departure from plan #15, stated:** the plan named a new standalone record,
`crafts/syseng/falsification/rules/craft-contributed-data.md`. Amending this file instead follows
the closer, already-established precedent immediately above (#141's own amendment, the same rule
gaining a new checkable capability), and keeps one record per Rule rather than splitting it.
`invariants.md`'s own falsification record carries the matching amendment for
`invariants_contrib.txt`.

Disposition: see ledger #15.

Disposition: see ledger #162.
