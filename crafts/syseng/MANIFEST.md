# syseng craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`)
and by `dyad craft install`. See `crafts/sysarch/MANIFEST.md` for why `0.2.0`: Rules 11, 12, 13
and 14 (`dyad/rules/`) cite `crafts/syseng/rules/*.md` paths, and `dyad/VERSION` moved 0.1.0 ->
0.2.0 at the same d-work (#162) that extracted them — `0.2.0` is the exact version, not merely a
safe floor (#178).

name: syseng
requires: dyad-operator>=0.2.0
