# syseng craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`)
and by `dyad craft install`. See `crafts/sysarch/MANIFEST.md` for why `0.2.0`: Rules 11, 12, 13
and 14 (`dyad/rules/`) cite `crafts/syseng/rules/*.md` paths, and `dyad/VERSION` moved 0.1.0 ->
0.2.0 at the same d-work (#162) that extracted them — `0.2.0` is the exact version, not merely a
safe floor (#178).

D1 (#100): `0.2.0` was never checked mechanically against this craft's own code. `crafts.floor_problems`
(`git rev-parse -q --verify dyad-operator-v<X>^{commit}`, then this craft's guard `INVARIANTS`
re-run against that tag's real `dyad/`) passes cleanly at `0.5.0`, `0.5.1` and `0.6.0` — the local
tags available to check against; `0.2.0`/`0.3.0`/`0.4.0` are not fetched here, so their tags could
not be mechanically confirmed or refuted. Raised to `0.5.0`, matching what could actually be
verified, rather than left at a value never checked.

name: syseng
requires: dyad-operator>=0.5.0
