# countersign craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`)
and by `dyad craft install`. `requires:` names the minimum version of another craft this one
depends on; `dyad craft install` refuses to install this craft when a requirement is unmet.

`0.10.1` since 0.3.0 (d-work #308). The self-diagnostic's levels check (`scripts/levels.py`) reads the host
path (`dyadlib.host_path`, #175), which no core tag before `dyad-operator-v0.10.1` carries: its own invariant
`core-provides-the-symbols-this-script-calls` is false on any older core. The floor is stated, not checked:
the craft guard's floor check (`crafts.floor_problems`) loads a craft's guards and projector against the floor
tag's `dyadlib.py`, and since #308's plan revision 2 the levels check is a script, not a guard
(`falsification/self-diagnostic.md` D20), so the floor check judges the projector alone and the script runs
that invariant itself, wherever it runs (`levels.self_check`), and in the craft's suite. `0.10.1` is also the
core countersign-system runs (`falsification/self-diagnostic.md` D10). The script does not call
`dyadlib.enforce` (#203), as no Tended craft module does yet: that core was labelled 0.10.1 before this repo's
tag was cut and ships no `enforce`, so the call would stop the script loading there. Before 0.3.0 the floor
was `0.9.0`: the core version this craft was authored and verified against (d-work #156), whose parsers the
projector reads — `dyadlib.read_rows`, the `agent/provenance` and `preferences/preferences` guards,
`runbook.all_events` — and needs no symbol newer than. No other Tended craft is required: the projector is
discovered by the core runner (`dyad project`), and the sysarch craft's registry guard, when installed, checks
it like any other projector.

No `seeds:` since 0.3.0 (`falsification/self-diagnostic.md` D25): the craft guard admits a seed only into a
zone one of the craft's own guards claims as `CORPUS` (#180), and the craft has no guard, its levels check
being a script (D20). The self-diagnostic's two instance files — the levels file and the run-book, both under
`<host>`, the receiving system's host path (preference `host-path`, default `workstation-corpus`;
countersign-system `infrastructure`; #175; `rules/self-diagnostic.md` §6 and §8) — are copied by hand, by the
two commands the README's *Installing the self-diagnostic* gives (the run-book's needs `mkdir -p
<host>/runbooks` first where a system keeps no run-book yet, as countersign-system does not). An install never
copies either (Rule-11 property 2: a Tended craft install writes only its own root), and nothing warns while
either is absent.

name: countersign
requires: dyad-operator>=0.10.1
