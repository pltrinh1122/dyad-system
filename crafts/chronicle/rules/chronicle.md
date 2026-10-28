# Chronicle (chronicle craft, Tended rule): the core, for every form

Read by `../guards/episodes.py` (the check) and by whoever writes, from a dyad system's own record, any piece meant
for readers: an episode of a serial, an essay, a blog post, a press release. A Tended rule: any form, no Rule-4
block, no sweep. Each form adds its own section beside this one (§7); the serial's is `serial.md`. Terms:
`../vocabulary/CRAFT.md`; the core's `Operator`, `provenance record`, `seat`, `subagent`, `failure mode`, `audit`.
Record: `../falsification/rules/chronicle.md`. Source: dyad-system plan #498 revisions 1–3, authored as its child
C4 (#502); the commit form (#511); the fiction layer (#515); the core and its form sections (#521, decision record
DR-9).

## Intent
Tell a dyad system's journey to readers, in whatever form the piece takes, without one sentence of its record layer
being invented: the form decides order, viewpoint and emphasis, and the record decides what happened. The one thing
the record cannot hold, the persona's character, is written as fiction and labelled so (§2).

## 1. Fact anchoring
A **piece** has two layers. Its **record layer** — the system's events, the seats and their audited flaws — draws
on exactly two kinds of material, and nothing else:
- **the record** — what the system's repos hold: rows, plans, provenance, incidents, audits, falsification
  records, releases. A **record citation** names it by an in-repo path, `path:<repo-relative path>`, or, for a
  repo other than the one the piece lives in, by `repo:<owner>/<repo>@<40-hex sha>:<path>` — a full commit sha,
  so the citation is immutable once written — or, for a commit itself (its message, its diff), by
  `commit:<owner>/<repo>@<40-hex sha>`, which has no path;
- **the Operator's context** — the Operator's own words about the world outside the repo (hopes, dreams, the life
  around the work), given as prompts on the rows that commission the writing and kept verbatim in their provenance
  records. A **context citation** names one entry: `prov:#<row id>/<entry n>`. It is the Operator's words only
  outside the entry's quoted lines: a line beginning `>` quotes the earlier reply the Operator was answering, and is
  never told as the Operator's voice.
Every event a piece tells cites one or the other, as a footnote (`[^n]: <citation>`, the templates' form). A
seat's "thinking" is its plan or its falsification record, never fiction. A commit message is record, never the
Operator's voice: commits carry the Operator's git identity whoever wrote them, so authorship in git says nothing
of who wrote the words. A gap in the record is reported as a gap, never filled — and a structure a form uses is a
lens on the record, never a mould: a part the record does not hold is a gap, not a cue to invent one. A piece's
other layer, the **fiction layer**, is the persona's alone (§2): it cites nothing and is labelled wherever it appears.

## 2. The persona and the fiction layer
The Operator may appear in a piece as a **persona**, named by the Operator: the Operator's choice of how to appear.
No other real person is a character, and the commons and its people are not named.

The persona's character, inner life and daemons are private, and the record is not asked to prove them: they are
written as **fiction based on a real-life model**, in the fiction layer, with no citations. Fiction is admitted here
only because it is labelled, twice:
- the piece's header carries `fiction: persona, based on a real-life model` whenever its text holds the layer;
- each interior passage is a paragraph that opens with the marker `*(fiction)*`, so the layer of any sentence can be
  decided by reading its paragraph.
A marked passage tells only the persona's interior. It never tells a system event, a seat's thought or a statement
about the real Operator: those are the record layer's and cite as §1 says.

## 3. Flaws and the real Operator
A seat's flaws are the failure modes an audit has classed, each cited to the incident ledger or the audit that
classed it. A flaw is attributed to the Operator only where the Operator approves that attribution, at the piece's
publication; that approval binds every statement about the real Operator in the record layer, and is moot for the
persona's daemons, which are fiction (§2).

## 4. The private-repo flag
Every repo a `repo:` or `commit:` citation names is declared in the piece's header `repos:` line with its visibility,
`<owner>/<repo>=public` or `<owner>/<repo>=private` (space-separated; `none` when the piece cites no other repo). A
piece citing a private repo names that repo in its publication question, so the Operator approves quoting it before
it goes public; quoting a private repo is never a side effect of publishing a piece.

## 5. Roles, by function
Roles are named by what they do, never by a seat, so any organization fills them:
- **The Operator** disposes. In every form the Operator has the final creative say, and nothing reaches readers
  without the Operator's approval (§6). A form may give that authority its own name; the serial's is the
  showrunner (`serial.md`). No role changes who disposes.
- **The editor** is the communicating seat: it assigns, edits and keeps the form's documents, across every form.
- **The writer** drafts prose, one assignment at a time: a fresh subagent per assignment, given only the form's
  **style guide**, the assignment's **brief** (`../templates/brief.md`: purpose, audience, length, the beats and
  their citations, the deadline) and the cited record — never the editor's notes on another draft, never an earlier
  draft. A notes round is the editor's notes on a draft, answered by a fresh writer given that draft and those notes.
- **The editor never edits its own draft**: whoever wrote a draft is never the one who edits it, so every draft gets
  a second view before the Operator reads it. A writer that persists — a seat of its own — is the organization's
  choice when two forms need drafting at once; the rule is the same.
Editing runs in stages: fact check first, so a beat the record fails is cut before anyone polishes it; then the
structural edit, the line edit, and the copy edit and proofread. The Operator reads at two points only: notes on
the structural edit, and the publication question.

## 6. Publication and change
Each piece is approved at its publication, by the Operator, on the piece as it will appear. A published piece is
**canon**: it is never rewritten, and a contradiction found later gets a correction note. Changes to what is not yet
published flow down freely — from a form's long-lived documents to its plans to its drafts — and flow up only on the
Operator's `Y`. Each publication question lists what the piece adds to the form's continuity and which planned
pieces it moved.

## 7. Forms
A **form** is a kind of piece — the serial, the essay, the blog post, the press release. Each form has its own
section beside this one, `<form>.md`, which names its pieces and their header, its documents, its structure (a lens,
§1) and its style guide, and which may narrow this core but never loosen it. A form with no section yet is written
under this core alone, its pieces carrying the header lines §2 and §4 name. The serial's section is `serial.md`, the
first form.

## 8. The guard and its severity
`../guards/episodes.py` checks the serial's pieces, its episodes (`serial.md` §7), and with them every rule of this
core that a file can show. It fails a footnote that is not one of the four citation forms; a marked passage
(`*(fiction)*`) under a header that lacks `fiction: persona, based on a real-life model`, a `fiction:` value other
than that label, or a footnote reference inside a marked passage; a `path:` that does not exist in the tree; a
`prov:` that names no provenance record or no such entry in it; a `repo:` or `commit:` whose repo is not declared in
`repos:` or whose sha is not 40 hex. A `repo:` citation is resolved when a clone of that repo is reachable locally
(`DYAD_REPOS_DIR/<repo>`, `git cat-file -e <sha>:<path>`), and fails when the clone lacks it; a `commit:` citation
likewise, by `git cat-file -e <sha>^{commit}`; with no clone it is unresolvable — The World, the `world` severity of
the core's Rule-20 register, property 2 — and the guard prints one `warning: … inference` line per piece counting
them: never a pass by assumption. A citation into a private repo prints one warning naming the repo (§4). A
`fiction:` header over a text with no marked passage prints one warning. Whether a cited artifact says what the piece
says it does, and whether a marked passage tells only the persona's interior, is inference, read at the piece's
publication. A form whose pieces no guard reads yet is checked by inference alone, stated in its publication
question.
