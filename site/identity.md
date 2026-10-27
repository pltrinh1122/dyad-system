# The Dyad System — identity record

The record, [`identity.jsonld`](identity.jsonld), states what this system is and what it is for, as JSON-LD that an agent can parse and compare with
another system's. It reuses schema.org wherever schema.org has the term; the `dyad:` prefix resolves to this repo's
[vocabulary](../dyad/vocabulary/VOCABULARY.md), and every `dyad:` class it types is a term defined there, a hyphen standing
for the term's space (`dyad:core-craft` is *core craft*). Every key schema.org does not define carries the `dyad:`
prefix, at every depth, so no key falls under schema.org's vocabulary by default. It holds no
version, date, commit or email: versions are in `BUNDLE.md` and on the Releases page. Every path it names exists in
this repository.

## Keys

| key | from | required | holds |
|---|---|---|---|
| `@id` | JSON-LD | yes | the system's stable IRI |
| `@type` | schema.org | yes | `SoftwareSourceCode` |
| `name`, `alternateName` | schema.org | yes | `The Dyad System`, `dyad-system` |
| `description` | schema.org | yes | one paragraph following the vocabulary's definition of The Dyad System |
| `codeRepository`, `url`, `license` | schema.org | yes | the repository URL, twice, and the license's SPDX IRI |
| `author` | schema.org | yes | a `Person`, by profile URL only |
| `isBasedOn` | schema.org | no | the practice and the bond repositories |
| `programmingLanguage`, `runtimePlatform` | schema.org | yes | `Python`; the kernel, Python 3.12 and git |
| `softwareRequirements` | schema.org | yes | what the system runs on: a CLI inferencing agent, with the kernel |
| `audience` | schema.org | yes | an `Audience`: who the system is for |
| `keywords` | schema.org | no | search terms |
| `hasPart` | schema.org | yes | each craft `BUNDLE.md` names, typed `dyad:core-craft` or `dyad:Tended-craft`, with its `name` and `dyad:path` |
| `dyad:purpose` | extension | yes | `{dyad:goal, dyad:problem, dyad:approach, dyad:target, dyad:nonGoals[]}`: the purpose every dyad system shares |
| `dyad:appliedTo` | extension | yes | this instance's domains, `[{name, dyad:path[]}]` |
| `dyad:source` | extension | yes | the paths that state the purpose |
| `dyad:party` | extension | yes | the two parties: `{dyad:role, dyad:kind, dyad:act}` |
| `dyad:invariant` | extension | yes | the craft invariants, as short names |
| `dyad:frame`, `dyad:rules`, `dyad:vocabulary` | extension | yes | the paths of the operating frame, the Agent Rules and the vocabulary |
| `dyad:entrypoint` | extension | yes | `{dyad:path, dyad:install}`: the one command-line entry and the install command |
| `dyad:releases` | extension | yes | `{url, dyad:tags{dyad:bundle, dyad:core-craft, dyad:Tended-craft}}`: the Releases URL and the three tag schemes |
| `dyad:registration` | extension | yes | the system's standing with the practice commons |
| `dyad:path` | extension | — | a path relative to the repository root |
| `subjectOf` | schema.org | no | a `CreativeWork` whose `url` is [`what-why-how.md`](what-why-how.md): the record's expansion |

## How to read it

- Parse [`identity.jsonld`](identity.jsonld) as JSON-LD. Its `@context` is schema.org plus the `dyad:` prefix, so every
  key resolves to either a schema.org term or a row of the [vocabulary](../dyad/vocabulary/VOCABULARY.md).
- Every `dyad:path`, and every path in `dyad:source`, `dyad:frame`, `dyad:rules`, `dyad:vocabulary` and
  `dyad:entrypoint`, is relative to the repository root, not to this directory.
- The record names no version. To pin one, read `BUNDLE.md` or a release tag (`dyad:releases`).
- `subjectOf` links the record's expansion, [`what-why-how.md`](what-why-how.md). That map takes the record's fields
  layer by layer — what the system is, why it is so, and how a party works it — and gives each claim a footnote to
  the artifact that holds it. Unlike the record, the map is pinned to a commit and dated, because its footnotes cite
  blobs. It stays beside the record, never inside it.
- To compare two dyad systems, compare their records key by key. `dyad:purpose` is shared by every dyad system.
  `dyad:appliedTo` is the instance's own.
