# cabinet craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`) and by
`dyad craft install`. `requires:` names the minimum version of another craft this one depends on; `dyad craft
install` refuses an unmet requirement.

`dyad-operator>=0.11.0`: the core that carries the countersign model (`dyad/playbooks/countersign-model.md`, #369
C3) and whose vocabulary holds the terms this craft's rules use — `mandate`, `mode`, `implicit mode`, `escalation`,
`accreted row`, `seat`, `holder`, `presence file` — so the craft requires the core only (plan #369 revision 4,
attack 5: born after C2, `requires: countersign` never). The floor is the core's live `VERSION` at authoring
(0.11.0, not yet tagged); the craft guard warns while the tag is absent and refuses at install only below it.

No `seeds:`. The mandates table this craft templates (`templates/mandates.md`) lives in the preferences corpus
(`preferences-corpus/MANDATES.md`, the Operator's, by a preferences-zone PR), and the craft guard admits a `seeds:`
destination only into a zone one of the craft's own guards claims as `CORPUS` (#180) — `seats.py` claims `agent`,
never `preferences`. Stated here and in the README's *Installing the organization*, as the countersign craft stated
its own (its record, D25); nothing warns while the table is absent, and `seats.py` prints one `skip` line.

name: cabinet
requires: dyad-operator>=0.11.0
