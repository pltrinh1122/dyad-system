# chronicle craft vocabulary (Tended terms)

One row per term; `rule` names the craft rule (`../rules/<rule>.md`) that owns it. A craft term is referenced,
never defined, by the Agent vocabulary (`dyad/vocabulary/VOCABULARY.md`, Rule-6 Boundaries), as `chronicle:<term>`;
no Agent term is redefined here — `Operator`, `provenance record`, `seat`, `failure mode`, `audit` are the core's.
Checked by the craft guard (`dyad craft check chronicle`).

| term | definition | rule |
|------|------------|------|
| episode | one instalment of the serial: a file under `<site>/episodes/` whose header names its title, season, number, time and cited repos, whose body tells events, and whose footnotes cite every one of them | chronicle |
| season outline | the arcs of one season, their interleave, and the repos read and not reached, approved by the Operator before any episode of the season is drafted against it | chronicle |
| record citation | a footnote naming an artifact of the record: `path:<repo-relative path>` in the serial's own repo, or `repo:<owner>/<repo>@<40-hex sha>:<path>` in another, or `commit:<owner>/<repo>@<40-hex sha>` for a commit itself, immutable once written | chronicle |
| context citation | a footnote naming the Operator's own words about the world around the work: `prov:#<row id>/<entry n>`, one entry of a provenance record | chronicle |
| persona | the main character: the Operator as the Operator chooses to appear, under a name the Operator gives | chronicle |
| fiction layer | the persona's character, inner life and daemons, written as fiction based on a real-life model with no citations, and labelled twice: the episode header's `fiction: persona, based on a real-life model` and a `*(fiction)*` marker opening each such passage; never a system event, a seat's thought or a statement about the real Operator | chronicle |
| interleave | the order in which a season alternates its present thread (the system as it grows now) and its past thread (the back-story), set by the season outline | chronicle |
| private-repo flag | the `=private` visibility an episode header's `repos:` line gives a cited repo, which makes the episode's publication name that repo for the Operator's approval | chronicle |
