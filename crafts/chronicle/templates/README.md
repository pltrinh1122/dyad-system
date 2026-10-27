# chronicle templates

Seeds an instance copies by hand (exempt from the instance-state scan; never written by `dyad craft install`,
Rule-11 property 2, and declared by no `seeds:` line — `../MANIFEST.md` says why):

| template | copied to | holds |
|---|---|---|
| `episode.md` | `<site>/episodes/s<season>e<episode>.md` (instance; `DYAD_SITE`, default `site`) | an episode's header (`title`, `season`, `episode`, `time`, `repos`), its body, and its citations as footnotes in the three forms (`../rules/chronicle.md` §1) |
