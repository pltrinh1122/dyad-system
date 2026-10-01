# Craft registry (instance state in the craft zone, Rule-11 property 2; #156)

One row per *installed* craft, never written by hand: a Tended craft's by `dyad craft install`, the core
craft's (`dyad-operator`, tree `dyad/`) by `dyad install` (#199). A craft authored in this system has no row
(`dyad craft list` shows it as `authored`). `sha256` is `distribute.archive_sha256` of the installed tree —
the proof it is unmodified, and what lets the push gate skip its test root (Rule-12 property 2); `source` is
where the archive came from (a `world` reference); `d-work` the installing d-work. No date: a second install
of the same version changes nothing.

| craft | version | source | sha256 | d-work |
|-------|---------|--------|--------|--------|
