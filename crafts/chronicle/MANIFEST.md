# chronicle craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`) and by
`dyad craft install`. `requires:` names the minimum version of another craft this one depends on; `dyad craft
install` refuses an unmet requirement.

`dyad-operator>=0.13.1`: the core whose provenance guard (`dyad/guards/agent/provenance.py`, Rule-7) parses the
records a context citation names — `episodes.py` imports it (`dyadlib.load_guard`) rather than re-parsing — and whose
vocabulary holds the terms this craft's rule uses (`Operator`, `provenance record`, `seat`, `failure mode`,
`audit`). The craft requires the core only: a seat is a character whatever organization opened it, so the cabinet
craft is read, never required. The floor is the core's live `VERSION` at authoring (0.13.1).

No `seeds:`. The template (`templates/episode.md`) seeds episodes under the instance's site (`site/episodes/`),
which no guard of this craft claims as a seeded destination and which grows one file per episode, not one file
per system.

name: chronicle
requires: dyad-operator>=0.13.1
