# chronicle — a serial told from a dyad system's own record (Tended craft, `crafts/chronicle/`, zone `craft`)

A dyad system's journey told as a story — characters, flaws, conflicts, climax and release — in which every event
cites the artifact that holds it: the record (rows, plans, provenance, incidents, audits, releases, in this repo or
another at a pinned sha) or the Operator's own words about the world around the work, kept verbatim in provenance
records. Story form shapes order, viewpoint and emphasis, never facts (`rules/chronicle.md`). The main character
is the Operator's persona; the other characters are the system's parties and seats, their flaws the failure modes
an audit has classed. Authored in dyad-system under #498 (child C4, row #502), scaffolded by `dyad craft new
chronicle` (the craft play-book, `dyad/playbooks/craft-instantiation.md`); it requires the core only
(`MANIFEST.md`). Version `VERSION` (0.1.0: first authored, d-work #502 (C4 of #498); unreleased). Not bundled with
the core: no core Rule cites this craft by path.

| path | holds |
|------|-------|
| `rules/chronicle.md` | fact anchoring and the two kinds of material (§1), the main character (§2), characters and flaws (§3), time and interleave (§4), the private-repo flag (§5), outline then episodes (§6), the guard and its severity (§7) |
| `vocabulary/CRAFT.md` | `episode`, `season outline`, `record citation`, `context citation`, `persona`, `interleave`, `private-repo flag` — referenced by the Agent vocabulary as `chronicle:<term>`, never defined there |
| `templates/episode.md` | an episode: the header (`title`, `season`, `episode`, `time`, `repos`), the body, the citations as footnotes in the three forms |
| `guards/episodes.py` | entity `episode`, corpus `infra`: every episode under `<site>/episodes/` — header, time line, each footnote's citation form, `path:` in the tree, `prov:` in a provenance record, `repo:` and `commit:` declared and resolved when a clone is reachable, else one `warning: … inference` line (absent store, one `skip`) |
| `falsification/rules/chronicle.md` | the record of the rule: plan #498's attacks 1, 3, 11, 12, 16, 17 and 19 on the rule as written |
| `tests/guards/test_episodes.py` | the guard over temp-dir fixtures: absent store, a good episode, each failing shape, the inference warning, the provenance entry, the invariants, the live repo |

## Not in this craft
The episodes, season outlines and the site that serves them (`site/`, instance, infra zone); the Pages workflow
and its manifest row (the instance's); the `communicate-<hp>` seat's charter (the Operator's mandates table); any
host value.
