# System Infrastructure manifest (Rule-14)

Every dependency of The Dyad System on The World that the core carries: the kernel and the authoring
library. `partition` is `kernel`, `library` or `The World`; `profile` is `authoring`, `operating` or
`both` (a kernel row is `both`); `version` is pinned for Python, observed for the rest (this instance's
host, 2026-09-13; an install re-observes). A system's own operating rows, as observed on it, live in its
instance contribution `<host>/INFRASTRUCTURE.md` (same seven cells); every installed craft's own in its
`infrastructure_contrib.md`. The one manifest is their union (Rule-14 property 1, #175).

| component | partition | version | purpose | license | replacement | profile |
|-----------|-----------|---------|---------|---------|-------------|---------|
| Claude Code | kernel | 2.1.270 observed | inferencing and workflow agent | Anthropic terms | another CLI inferencing agent | both |
| Python | kernel | 3.12 pinned (3.12.3 observed) | code: guards and tooling (target; guards are bash today, gap I1) | PSF | — | both |
| Git | kernel | 2.43.0 observed | local repository, history, hooks | GPL-2.0 | — | both |
| pydantic | kernel | 2.13.5 pinned (checked via `pip index versions pydantic`, 2026-09-16; not yet installed — adopted when a plan first imports it) | data-model schema definition, validation and JSON Schema emission for corpus entities (evaluated `agent-corpus/falsification/schema-definition-language.md`, d-work #30) | MIT | a stdlib JSON Schema emitter over the existing guard contract (`dyadlib.FIELDS` + `describe()`) | both |
| bash + GNU coreutils, grep, awk, sed | library | 5.2.21 observed | interpreter of the five guards and Operator ops scripts (Rule-18) | GPL-3.0 | Python (kernel), gap I1 | both |
| GitHub (hosting) | library | — | remote of `main`, PRs; mirror for remote sessions once the LAN server is deployed (#24, Q2) | GitHub terms | Gitea on the LAN (`crafts/lan-git/server/`, the lan-git craft, #181; `crafts/sysadmin/server/` before it, #155), #24 | authoring |
| GitHub Actions + `actions/checkout@v4` | library | — | runs the guards on push and PR; absent since 2026-09-14 (billing); replacement pending #24 | GitHub terms / MIT | LAN runner or kernel-only path, gap I2 | authoring |
| `actions/setup-python@v5` | library | v5 | installs the pinned Python in CI (`dyad-package.yml`, `dyad-release.yml`) | MIT | kernel Python on a LAN runner, #24 | authoring |
| gh | library | 2.45.0 observed | PR create, merge, checks (Agent workflow) | MIT | GitHub REST via Python, or LAN server API | authoring |
| jq | library | 1.7 observed | JSON in Agent workflow | MIT | Python `json` (kernel) | both |
| Linux (OS) | The World | 7.0.0-31 observed | provides the kernel | — | observed, never pinned | both |
