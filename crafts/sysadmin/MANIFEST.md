# sysadmin craft manifest (Rule-11 property 2: `requires:`, `seeds:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`)
and by `dyad craft install`. See `crafts/sysarch/MANIFEST.md` for why `0.2.0`: Rules 5, 8, 18 and
19 (`dyad/rules/`) cite `crafts/sysadmin/rules/*.md` paths (extracted #155), and `dyad/VERSION`
first reached `0.2.0` at #162 — the earliest recorded version guaranteed to postdate every core
change this craft's kernels depend on (#178). `seeds:` (#180) names a template this craft
ships and the instance file it corresponds to; install never copies it (Rule-11 property 2: a
Tended craft install writes only its own root), `dyad craft check` warns and names the exact
copy command when the destination is absent.

D1 (#100): `0.2.0` was never checked mechanically against this craft's own code.
`crafts.floor_problems` passes cleanly at `0.5.0`, `0.5.1`, `0.6.0`, `0.6.1`, `0.6.2` and `0.7.0` —
every local tag available to check against; `0.2.0`-`0.4.0` are not fetched here, so their tags
could not be mechanically confirmed or refuted. Raised to `0.5.0`, matching what could actually be
verified, rather than left at a value never checked.

name: sysadmin
requires: dyad-operator>=0.5.0
seeds: CHANGELOG.md->workstation-corpus/CHANGELOG.md
