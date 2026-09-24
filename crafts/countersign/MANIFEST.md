# countersign craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`)
and by `dyad craft install`. `requires:` names the minimum version of another craft this one
depends on; `dyad craft install` refuses to install this craft when a requirement is unmet.

`0.9.0` is the core craft's `dyad/VERSION` this craft was authored and verified against (d-work
#156). The projector reads the core's own parsers — `dyadlib.read_rows`, the `agent/provenance`
and `preferences/preferences` guards, `runbook.all_events` — and needs no symbol newer than those;
an older floor was not checked mechanically against its tag, so none is claimed. No other Tended
craft is required: the projector is discovered by the core runner (`dyad project`), and the
sysarch craft's registry guard, when installed, checks it like any other projector.

name: countersign
requires: dyad-operator>=0.9.0
