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
| pydantic | kernel | 2.14.1 pinned (observed 2026-10-17 in the ledgerd venv under fastapi 0.141.1, which needs >=2.9.0; adopted by #336; 2.13.5 was the pin checked via `pip index versions pydantic` on 2026-09-16, never installed) | data-model schema definition, validation and JSON Schema emission for corpus entities (evaluated `agent-corpus/falsification/schema-definition-language.md`, d-work #30); adopted by #336 (FastAPI models: `ledgerd.core.Query`, `SavedView`), installed into <state>/venv by `dyad ledger install` with the ledgerd rows | MIT | a stdlib JSON Schema emitter over the existing guard contract (`dyadlib.FIELDS` + `describe()`) | both |
| bash + GNU coreutils, grep, awk, sed | library | 5.2.21 observed | interpreter of the five guards and Operator ops scripts (Rule-18) | GPL-3.0 | Python (kernel), gap I1 | both |
| GitHub (hosting) | library | — | remote of `main`, PRs; mirror for remote sessions once the LAN server is deployed (#24, Q2) | GitHub terms | Gitea on the LAN (`crafts/lan-git/server/`, the lan-git craft, #181; `crafts/sysadmin/server/` before it, #155), #24 | authoring |
| GitHub Actions + `actions/checkout@v4` | library | — | runs the guards on push and PR; absent since 2026-09-14 (billing); replacement pending #24 | GitHub terms / MIT | LAN runner or kernel-only path, gap I2 | authoring |
| `actions/setup-python@v5` | library | v5 | installs the pinned Python in CI (`dyad-package.yml`, `dyad-release.yml`) | MIT | kernel Python on a LAN runner, #24 | authoring |
| FastAPI | library | 0.141.1 pinned (released 2026-07-29; the last release before 0.142.0 made `opentelemetry-api`, Apache-2.0, a required dependency — outside the MIT-or-more-lenient bar) | ledgerd only; installed per instance into <state>/venv by `dyad ledger install`, never by `dyad install`: the HTTP API, routing and request models of `dyad/server/ledgerd/` (plan #336 revision 9); transitive as observed 2026-10-17: starlette BSD-3-Clause, pydantic-core MIT, anyio MIT, idna BSD-3-Clause, annotated-types MIT, annotated-doc MIT, typing-extensions PSF-2.0, typing-inspection MIT | MIT | Bottle (MIT), or the stdlib `http.server` | both |
| uvicorn | library | 0.54.0 pinned | ledgerd only; installed per instance into <state>/venv by `dyad ledger install`, never by `dyad install`: the ASGI server process (plain, not `[standard]`); transitive: click BSD-3-Clause, h11 MIT | BSD-3-Clause | the stdlib `http.server` (ThreadingHTTPServer) | both |
| SQLAlchemy | library | 2.1.5 pinned | ledgerd only; installed per instance into <state>/venv by `dyad ledger install`, never by `dyad install`: Core only — the schema's tables as `Table` objects, inserts, reflection for `/schema`; no ORM | MIT | authored DDL strings over the stdlib `sqlite3` | both |
| Jinja2 | library | 3.1.6 pinned | ledgerd only; installed per instance into <state>/venv by `dyad ledger install`, never by `dyad install`: the navigator's page and fragments (`dyad/server/ledgerd/templates/`); transitive: MarkupSafe BSD-3-Clause | BSD-3-Clause | string templates (`str.format`) | both |
| htmx | library | 2.0.4 pinned (vendored at dyad/server/ledgerd/static/htmx.min.js, sha256 e209dda5c8235479f3166defc7750e1dbcd5a5c1808b7792fc2e6733768fb447, from the GitHub release asset) | ledgerd only; the one JavaScript file, served same-origin at `/static/htmx.min.js`: swaps server-rendered fragments into the page, no application logic in it (never a CDN, crafts/syseng/rules/determinism.md p2) | 0BSD | plain HTML forms (a full page per request) | both |
| gh | library | 2.45.0 observed | PR create, merge, checks (Agent workflow) | MIT | GitHub REST via Python, or LAN server API | authoring |
| jq | library | 1.7 observed | JSON in Agent workflow | MIT | Python `json` (kernel) | both |
| Linux (OS) | The World | 7.0.0-31 observed | provides the kernel | — | observed, never pinned | both |
