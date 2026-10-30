# chronicle craft vocabulary (Tended terms)

One row per term; `rule` names the craft rule (`../rules/<rule>.md`) that owns it. A craft term is referenced,
never defined, by the Agent vocabulary (`dyad/vocabulary/VOCABULARY.md`, Rule-6 Boundaries), as `chronicle:<term>`;
no Agent term is redefined here — `Operator`, `provenance record`, `seat`, `failure mode`, `audit` are the core's.
The core's terms (`rule` = `chronicle`) bind every form; the serial's (`rule` = `serial`) bind the serial. A source in
parentheses names the field a term is taken from (DR-3). Checked by the craft guard (`dyad craft check chronicle`).

| term | definition | rule |
|------|------------|------|
| piece | one work written for readers from a dyad system's record, in one form: an episode, an essay, a blog post, a press release; it has a record layer and may have a fiction layer | chronicle |
| form | a kind of piece, with its own section `rules/<form>.md` naming its pieces, header, documents, structure and style guide; the serial is the first | chronicle |
| record citation | a footnote naming an artifact of the record: `path:<repo-relative path>` in the serial's own repo, or `repo:<owner>/<repo>@<40-hex sha>:<path>` in another, or `commit:<owner>/<repo>@<40-hex sha>` for a commit itself, immutable once written | chronicle |
| context citation | a footnote naming the Operator's own words about the world around the work: `prov:#<row id>/<entry n>`, one entry of a provenance record | chronicle |
| persona | the main character: the Operator as the Operator chooses to appear, under a name the Operator gives | chronicle |
| fiction layer | everything in a piece the record layer does not hold — the persona's character, inner life and daemons, the world around the work, and composites — written as fiction based on real-life models with no citations, and labelled twice: the piece header's `fiction:` line (`persona, based on a real-life model`; `composites: <name>, …`) and a `*(fiction)*` marker opening each such passage; never a system event, a seat's thought or the Operator's recorded prompts and approvals | chronicle |
| record layer | the system's record as a piece tells it: the agents' work — the system's events, the seats and their audited flaws — and the Operator's recorded prompts and approvals, every event cited by a record or context citation | chronicle |
| composite | a character drawn from more than one real person and from no single one: fiction, never a real person, declared as a composite in the form's character list and in the `fiction:` line of every piece it appears in, appearing only in marked passages | chronicle |
| private-repo flag | the `=private` visibility an episode header's `repos:` line gives a cited repo, which makes the episode's publication name that repo for the Operator's approval | chronicle |
| editor | the communicating seat in its role: it assigns, edits and keeps a form's documents across every form, and never edits a draft it wrote (prose publishing's editor) | chronicle |
| writer | the role that drafts a piece, one assignment at a time: a fresh subagent given only the form's style guide, the brief and the cited record (prose publishing) | chronicle |
| style guide | a form's standing voice and conventions, given to every writer of that form (prose publishing) | chronicle |
| brief | one assignment: purpose, audience, length, the beats and their citations, the deadline; `templates/brief.md` (prose publishing) | chronicle |
| canon | the published pieces of a form: never rewritten; a contradiction found later gets a correction note (web serials) | chronicle |
| episode | one piece of the serial: a file under `<site>/episodes/` whose header names its title, season, number, time and cited repos, whose body tells events, and whose footnotes cite every one of them (web serials' instalment) | serial |
| showrunner | the Operator's role in the serial: the final creative say over the whole series, a name for that authority and never a new right (television, used where prose has no term) | serial |
| series bible | what holds for the whole serial: premise, characters, tone, style guide (television, used where prose has no term) | serial |
| season arc | one season's arcs, its interleave and the repos read and not reached, approved before any of its episodes is drafted; the frame the rolling wave fills (web serials) | serial |
| interleave | the order in which a season alternates its present thread (the system as it grows now) and its past thread (the back-story), set by the season arc | serial |
| episode outline | one episode's plan, filled in as the episode comes up, its beats in a beat sheet (web serials) | serial |
| beat sheet | one episode's beats, each with its citation, labelled with the Story Circle's steps (screenwriting) | serial |
| continuity bible | the serial's setups and payoffs and which episode holds each (television) | serial |
| buffer | the episodes drafted and not yet published, two, so a payoff can be fixed before its setup is canon (web serials) | serial |
| Story Circle | an eight-step structure (you, need, go, search, find, take, return, change), used as a lens on the record and never a mould (Harmon) | serial |
| rolling wave | planning the season arc whole and the next one or two episodes in detail, the rest one line each, filled in as each comes up (project management) | serial |
