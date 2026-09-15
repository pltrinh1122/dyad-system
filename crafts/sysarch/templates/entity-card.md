# Entity card (what a guard's `describe(root, pkg)` yields; crafts/sysarch/rules/guards.md property 3)

The entities surface (`crafts/sysarch/projectors/project_entities.py`) draws one card per guard from
this dict; a guard whose `fields` do not start with its `FIELDS`, in order, is a bug and the
projector raises. Relations are not part of the card: they come from the reference register
(`references.REFERENCES`, `crafts/sysarch/rules/references.md` property 4).

| key | type | meaning |
|-----|------|---------|
| `store` | text | where instances live, as a path pattern (`<instance>/d-work/rows/<id>.md`); `<…>` segments are anchors a relation may name |
| `parser` | text | the function that yields one instance's fields (`` `rows.parse_row_file` ``) |
| `observed` | int | how many instances the store holds on this system (0 on a fresh install) |
| `note` | text | one line: what the guard checks and what stays inference |
| `fields` | list | one tuple per field, `FIELDS` first and in order, then derived fields |

Each `fields` tuple: `(name, type, meaning, required, example, source)` —

| position | meaning |
|----------|---------|
| `name` | the field as `FIELDS` spells it |
| `type` | `text`, `int`, `date`, `enum`, `path`, `bool`, `list` |
| `meaning` | one clause; for `enum`, the allowed values |
| `required` | `True` if every instance carries it |
| `example` | one value from this system's store (`""` when the store is empty) |
| `source` | the constant the field comes from (`rows.FIELDS`, `crafts.FIELDS`) |

Module-level, beside the contract: `NAME` (the entity as the card titles it) and `OWNER` (the Rule
or craft rule whose check it is); absent, the card uses `ENTITY` and an empty owner.
