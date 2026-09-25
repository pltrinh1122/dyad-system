# disclosure — a Tended craft (`crafts/disclosure/`, zone `craft`)

What may leave a dyad system in a document handed to a party outside it, and in what form. One rule
(`rules/redaction.md`), one gate (`scripts/redaction.py verify <file>`) and one surface
(`dyad project disclosure`). Authored in d-work #166 for the `ds-report-incidents` play-book, which is
core (`dyad/playbooks/ds-report-incidents.md`) because a play-book belongs to the operator craft; the
practice of deciding what is safe to disclose belongs here, where it can be installed into another
dyad system that needs it.

The one idea worth carrying away: **a disclosure is assembled by allow-list and gated by deny-list.**
Filtering a corpus written for insiders cannot be made safe — you cannot enumerate the sentences you
do not know. Building a document out of counts, dates, controlled values and stable pseudonyms can be,
and the deny-list is then what catches a slip of *shape* rather than what does the work.

| path | holds |
|------|-------|
| `rules/redaction.md` | the Tended rule: allow-list first, the fail-closed gate, the three classes, the map, the audience, self-containment, determinism |
| `vocabulary/CRAFT.md` | `disclosure`, `audience`, `redaction class`, `pseudonym map`, `deny-list`, `watermark` |
| `scripts/redaction.py` | the class data's parser and check, plus `verify <file>` (the gate) and `unmapped <file>` |
| `scripts/redaction_rules.txt` | the shapes and the allowed fields (data, beside the guard) |
| `projectors/project_disclosure.py` | the surface: assemble, gate, write `<instance>/projections/disclosure.html` |
| `tests/` | the gate's fixtures, the map's rules, determinism, self-containment, the refusals |
| `falsification/rules/redaction.md` | the record for the rule |

## What lives outside this craft
- **The pseudonym map** — `<instance>/disclosure/pseudonyms.md`, instance state (Rule-11 property 1).
  It is the inverse of every document produced here and is never delivered with one.
- **The summaries** — `<instance>/disclosure/summaries/<YYYY-MM>.md`, Agent prose for one audience.
- **The audience** — a parameter. No file of this craft names any recipient.
- **When a disclosure is produced and who releases it** — the play-book and the Agent Rules.

## Installing it elsewhere
`dyad craft install <src>`; it needs `dyad-operator >= 0.9.1` for the incident guard the surface parses
with. Without that guard the surface refuses with a stated reason rather than parsing the log a second
way — the shape every other store in this system uses when its parser is absent.
