# Chronicle (chronicle craft, Tended rule)

Read by `../guards/episodes.py` (the check) and by whoever drafts a serial from a dyad system's own record. A
Tended rule: any form, no Rule-4 block, no sweep. Terms: `../vocabulary/CRAFT.md` (`episode`, `season outline`,
`record citation`, `context citation`, `persona`, `interleave`, `private-repo flag`); the core's `Operator`,
`provenance record`, `seat`, `failure mode`, `audit`. Record: `../falsification/rules/chronicle.md`. Source:
dyad-system plan #498 revisions 1–3 (attacks 1, 3, 11, 12, 16, 17, 19), authored as its child C4 (#502).

## Intent
Tell a dyad system's journey as a serial — characters, flaws, conflicts, climax and release — without one sentence
of it being invented: story form decides order, viewpoint and emphasis, and the record decides what happened.

## 1. Fact anchoring
An episode draws on exactly two kinds of material, and nothing else:
- **the record** — what the system's repos hold: rows, plans, provenance, incidents, audits, falsification
  records, releases. A **record citation** names it by an in-repo path, `path:<repo-relative path>`, or, for a
  repo other than the one the serial lives in, by `repo:<owner>/<repo>@<40-hex sha>:<path>` — a full commit sha,
  so the citation is immutable once written — or, for a commit itself (its message, its diff), by
  `commit:<owner>/<repo>@<40-hex sha>`, which has no path;
- **the Operator's context** — the Operator's own words about the world outside the repo (hopes, dreams, the life
  around the work), given as prompts on the serial's rows and kept verbatim in their provenance records. A
  **context citation** names one entry: `prov:#<row id>/<entry n>`. It is the Operator's words only outside the
  entry's quoted lines: a line beginning `>` quotes the earlier reply the Operator was answering, and is never
  told as the Operator's voice.
Every event an episode tells cites one or the other, as a footnote (`[^n]: <citation>`, the template's form). A
seat's "thinking" is its plan or its falsification record; the inner life of the main character is only what the
Operator gave. A commit message is record, never the Operator's voice: commits carry the Operator's git identity
whoever wrote them, so authorship in git says nothing of who wrote the words. A gap in the record is reported as a gap,
never filled.

## 2. The main character
The main character is the Operator's **persona**, named by the Operator, and the arc
is the persona's growth in the Dyad-Operator craft, readable in the record: the preferences set, the corrections
given, the amends that turned plans, the Rules made. The persona is the Operator's choice of how to appear; no
other real person is a character, and the commons and its people are not named.

## 3. Characters and flaws
The other characters are the parties and the seats of the system (the cos, counsel, audit, engineer,
distribute, operate, communicate, and any seat the organization opens). A seat's flaws are the failure modes an audit has
classed, each cited to the incident ledger or the audit that classed it. A flaw is attributed to the Operator only
where the Operator approves that attribution, at the episode's publication.

## 4. Time and interleave
Every episode's header carries its time: `time: present, <YYYY-MM-DD>` or `time: past, <YYYY-MM-DD>` — the present
thread is the system as it grows now, the past thread the back-story in the earlier repos. A season outline sets
the **interleave**: which past arc sits beside which present one (a natural pairing is a present conflict beside
the past moment that set it up), approved with the outline.

## 5. The private-repo flag
Every repo a `repo:` or `commit:` citation names is declared in the episode header's `repos:` line with its visibility,
`<owner>/<repo>=public` or `<owner>/<repo>=private` (space-separated; `none` when the episode cites no other
repo). An episode citing a private repo names that repo in its publication question, so the Operator approves
quoting it before it goes public; quoting a private repo is never a side effect of publishing an episode.

## 6. Outline, then episodes
A season outline — its arcs, its interleave, the repos it has read and the ones it could not reach — is approved
by the Operator before any episode of that season is drafted against it. Each episode is approved at its
publication, by the Operator, on the episode as it will appear. An episode the outline does not cover waits for
an outline that does.

## 7. The guard and its severity
`../guards/episodes.py` reads every episode under `<site>/episodes/*.md` (`DYAD_SITE`, default `site`; an absent
store prints one `skip` line). It fails an episode whose header lacks a key or whose `time:` line is malformed; a
footnote that is not one of the four citation forms; a `path:` that does not exist in the tree; a `prov:` that
names no provenance record or no such entry in it; a `repo:` or `commit:` whose repo is not declared in `repos:` or whose sha is
not 40 hex. A `repo:` citation is resolved when a clone of that repo is reachable locally (`DYAD_REPOS_DIR/<repo>`,
`git cat-file -e <sha>:<path>`), and fails when the clone lacks it; a `commit:` citation likewise, by
`git cat-file -e <sha>^{commit}`; with no clone it is unresolvable — The World,
the `world` severity of the core's Rule-20 register, property 2 — and the guard prints one `warning: … inference`
line per episode counting them: never a pass by assumption. A citation into a private repo prints one warning
naming the repo (§5). Whether a cited artifact says what the episode says it does is inference, read at the
episode's publication.
