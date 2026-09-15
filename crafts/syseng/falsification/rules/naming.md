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

Disposition: see ledger #162.
