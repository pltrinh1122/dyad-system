# chronicle — writing for readers from a dyad system's own record (Tended craft, `crafts/chronicle/`, zone `craft`)

A dyad system's journey told to readers, in any form — a serial, an essay, a blog post, a press release — in which
every event cites the artifact that holds it: the record (rows, plans, provenance, incidents, audits, releases, in
this repo or another at a pinned sha) or the Operator's own words about the world around the work, kept verbatim in
provenance records. The form shapes order, viewpoint and emphasis, never facts. The Operator may appear as a persona,
whose character alone is written as labelled fiction. The craft is a **core** that binds every form
(`rules/chronicle.md`) and **one section per form** (`rules/<form>.md`); the serial is the first form
(`rules/serial.md`). Authored in dyad-system under #498 (child C4, row #502), scaffolded by `dyad craft new
chronicle` (the craft play-book, `dyad/playbooks/craft-instantiation.md`); it requires the core only
(`MANIFEST.md`). Version `VERSION` (0.2.0: the core and its form sections, d-work #521; 0.1.0, released as
`chronicle-v0.1.0`, was the serial alone). Not bundled with the core: no core Rule cites this craft by path.

| path | holds |
|------|-------|
| `rules/chronicle.md` | the core, for every form: fact anchoring and the record layer (§1), the persona and the fiction layer (§2), flaws and the real Operator (§3), the private-repo flag (§4), roles by function — Operator, editor, writer (§5), publication and change (§6), forms (§7), the guard and its severity (§8) |
| `rules/serial.md` | the serial's section: episodes (§1), characters (§2), time and interleave (§3), the serial's documents — series bible, season arc, episode outline and beat sheet, continuity bible, canon, buffer (§4), the Story Circle as a lens (§5), the rolling wave (§6), the guard (§7) |
| `vocabulary/CRAFT.md` | the core's terms (`piece`, `form`, `record citation`, `context citation`, `persona`, `fiction layer`, `private-repo flag`, `editor`, `writer`, `style guide`, `brief`, `canon`) and the serial's (`episode`, `showrunner`, `series bible`, `season arc`, `interleave`, `episode outline`, `beat sheet`, `continuity bible`, `buffer`, `Story Circle`, `rolling wave`), each with its source — referenced by the Agent vocabulary as `chronicle:<term>`, never defined there |
| `templates/episode.md` | an episode: the header (`title`, `season`, `episode`, `time`, `repos`, `fiction`), the body, a marked fiction passage, the citations as footnotes in the four forms |
| `templates/brief.md` | one writer's assignment: purpose, audience, length, the beats and their citations, the deadline |
| `guards/episodes.py` | entity `episode`, corpus `infra`: every episode under `<site>/episodes/` — header, time line, each footnote's citation form, `path:` in the tree, `prov:` in a provenance record, `repo:` and `commit:` declared and resolved when a clone is reachable, else one `warning: … inference` line; the fiction layer's labels (absent store, one `skip`) |
| `dmc/*.jsonld` | the craft's decision-making-criterion records (`dyad/dmc/schema.md`) |
| `falsification/rules/chronicle.md` | the record of the rules: plan #498's attacks, and the amendments #511, #515 and #521 |
| `tests/guards/test_episodes.py` | the guard over temp-dir fixtures: absent store, a good episode, each failing shape, the inference warning, the provenance entry, the fiction labels, the invariants, the live repo |

## Not in this craft
The pieces, their style guides and the documents of each form (series bible, season arc, continuity bible) and the
site that serves them (`site/`, instance, infra zone); the Pages workflow and its manifest row (the instance's); the
communicating seat's charter (the Operator's mandates table); any host value.
