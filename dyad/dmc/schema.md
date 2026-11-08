# DMC record schema

A **decision-making criterion** (DMC) record states one recurring decision of the dyad as data: the
question, what it reads, its outcomes and the condition and consequence of each, how it is judged and
which file defines it. One JSON-LD file per criterion; schema.org supplies the shape, the `dyad:`
terms below the rest (plan #507). Checked by `dyad/guards/agent/dmc.py` (entity `dmc`, Rule-12).

## Where records live
| container | directory | `@id` / `isPartOf` | path base |
|---|---|---|---|
| core | `dyad/dmc/` | `urn:dyad:dmc:dyad-operator/<identifier>` / `urn:dyad:craft:dyad-operator` | `dyad/` |
| a Tended craft | `crafts/<craft>/dmc/` | `urn:dyad:dmc:<craft>/<identifier>` / `urn:dyad:craft:<craft>` | `crafts/<craft>/` |
| the instance | `<instance>/dmc/` (`DYAD_INSTANCE`) | `urn:dyad:dmc:instance/<identifier>` / `urn:dyad:instance` | the repo root |

The file is `<identifier>.jsonld`. `dyad/dmc/context.jsonld` is the one context and is not a record.

## Keys
| key | required | value |
|---|---|---|
| `@context` | yes | equal to `context.jsonld`'s: `["https://schema.org", {"dyad": "urn:dyad:term:"}]` |
| `@id` | yes | `urn:dyad:dmc:<container>/<identifier>` |
| `@type` | yes | a list holding `DefinedTermSet` and `dyad:DecisionCriterion` |
| `identifier` | yes | the slug, equal to the file stem |
| `name` | yes | a short name |
| `description` | yes | one sentence |
| `dyad:decides` | yes | the question it answers |
| `dyad:inputs` | yes | a non-empty list of strings: what it reads |
| `hasDefinedTerm` | yes | a list of ≥ 2 outcomes, each `{"@type": "DefinedTerm", "termCode", "name", "dyad:when", "dyad:then"}`, every value a non-empty string, `termCode` unique in the record |
| `dyad:precedence` | no | the order or tie-break among outcomes |
| `dyad:default` | no | the outcome when the inputs cannot decide |
| `dyad:tunables` | no | a non-empty list of the numbers this criterion lets the operator tune, each `{"dyad:preference": <key>, "dyad:defaultValue", "dyad:allowed", "dyad:readBy": <path>}`, every value a non-empty string: the preference key (lowercase, hyphenated), the value used when the preference is absent, what the `allowed` cell says, and the file that reads it; a key is claimed by one record only; core records only (`dyad/dmc/`), since `dyadlib.tunable` reads no craft or instance record (#590) |
| `dyad:judgedBy` | yes | `{"dyad:kind": "mechanical" \| "inference" \| "declared", "dyad:implementation": <path> \| null}` |
| `isPartOf` | yes | the container's urn (table above) |
| `dyad:home` | yes | a path: the file that defines the criterion |
| `dyad:alsoIn` | no | a list of paths: other files that state part of it |
| `dyad:owner` | yes | the Rule or craft rule that owns it (`Rule-11`, `sysadmin:host-mutation`) |

## dyad: terms
Defined here and nowhere else; a craft uses them, never defines one.

| term | meaning |
|---|---|
| `dyad:DecisionCriterion` | the record's type beside `DefinedTermSet`: a set of outcomes that answers one question |
| `dyad:decides` | the question the criterion answers |
| `dyad:inputs` | what the decision reads |
| `dyad:when` | an outcome's condition |
| `dyad:then` | an outcome's consequence |
| `dyad:precedence` | how outcomes are ordered or a tie is broken |
| `dyad:default` | the outcome taken when the inputs cannot decide |
| `dyad:tunables` | the operator-tunable numbers of the criterion, each a preference with its default here |
| `dyad:preference` | a tunable's preference key (`preferences-corpus/PREFERENCES.md`) |
| `dyad:defaultValue` | a tunable's value when the preference is absent: the one home of that default |
| `dyad:allowed` | a tunable's allowed values, as the preference row's `allowed` cell states them |
| `dyad:readBy` | the file that reads a tunable |
| `dyad:judgedBy` | how the decision is made: its kind and its implementation |
| `dyad:kind` | `mechanical` (code decides), `inference` (the Agent reads and judges), `declared` (a party states it, e.g. a preference) |
| `dyad:implementation` | the code that decides, as a path, or null |
| `dyad:home` | the defining file |
| `dyad:alsoIn` | other files stating part of it |
| `dyad:owner` | the Rule or craft rule that owns the criterion |

## Conventions
- **Paths** are relative to the container's path base (table above). `../` may reach another craft
  (`../crafts/sysadmin/rules/host-mutation.md` from the core) but must resolve inside the repo.
- **`dyad:implementation` may be null** for any kind: a decision made by core code that is not one
  module, or by a run-book's shell step, names those files in `dyad:alsoIn`. It may be present for any kind.
- **Master or index, by the home** (#626). A record whose `dyad:home` is under `playbooks/` or `runbooks/` (relative to
  its path base) is the **master**: the record alone defines its outcomes, and the home cites it exactly as
  `dmc:<identifier>`. The home names every outcome of a master record at most partly: a home that holds every outcome
  `name` restates the decision. Any other record is an **index**, and its outcome names are quoted from the home file:
  each `name` appears in `dyad:home`, compared case-insensitively with every whitespace run collapsed to one space.
- **No moving values.** Outside the path fields (`dyad:home`, `dyad:alsoIn`, `dyad:implementation`, a tunable's
  `dyad:readBy`) and
  `dyad:owner`, no value holds a date (`YYYY-MM-DD`), a version (`[v]N.N.N`), a 40-hex commit sha or an
  email address: a criterion is stated as it stands, and history is git's.

## What the guard checks
Every rule above, mechanically, per record: JSON parses; the required keys; `@context`; `@type`; `@id`,
`identifier` and `isPartOf` against the container and file; the shapes of `dyad:inputs`,
`hasDefinedTerm` and `dyad:judgedBy`; that every path exists inside the repo; for an index record, that every
outcome name appears in the home file; for a master record, that its home cites `dmc:<identifier>` and does not
hold every outcome name; that every `dmc:<id>` a play-book or run-book cites names a record; the forbidden values; a `dyad:tunables` list's shape and paths; and, across all records, that no `@id` is
declared twice and no preference is claimed as a tunable twice. A tunable whose key has no row in
`dyad/templates/PREFERENCES.md` warns.
A path into a craft this system has not installed warns instead of failing (Rule-20 property 2). No
record anywhere passes, its summary saying so. Whether the outcomes are right, whether the home file
states them and whether `dyad:kind` is true is inference.
