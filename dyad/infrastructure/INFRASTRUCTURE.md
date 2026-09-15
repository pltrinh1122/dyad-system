# System Infrastructure manifest (Rule-14)

Every dependency of The Dyad System on The World. `partition` is `kernel` or `library`;
`version` is pinned for Python, observed for the rest (this instance's host, 2026-09-13; an install re-observes).

| component | partition | version | purpose | license | replacement |
|-----------|-----------|---------|---------|---------|-------------|
| Claude Code | kernel | 2.1.270 observed | inferencing and workflow agent | Anthropic terms | another CLI inferencing agent |
| Python | kernel | 3.12 pinned (3.12.3 observed) | code: guards and tooling (target; guards are bash today, gap I1) | PSF | — |
| Git | kernel | 2.43.0 observed | local repository, history, hooks | GPL-2.0 | — |
| bash + GNU coreutils, grep, awk, sed | library | 5.2.21 observed | interpreter of the five guards and Operator ops scripts (Rule-18) | GPL-3.0 | Python (kernel), gap I1 |
| GitHub (hosting) | library | — | remote of `main`, PRs; mirror for remote sessions once the LAN server is deployed (#24, Q2) | GitHub terms | Gitea on the LAN (`crafts/lan-git/server/`, the lan-git craft, #181; `crafts/sysadmin/server/` before it, #155), #24 |
| Gitea | library | 1.27.3 pinned (image `gitea/gitea:1.27.3`, Alpine 3.24) | LAN git server image base: `main`, PRs, branch protection requiring the `dyad/guards` status, operator/agent accounts (`crafts/lan-git/server/`, the lan-git craft, #181; `crafts/sysadmin/server/`'s reference deployment before it, #155; instance #124 before that; selected #24) | MIT | Forgejo (GPL-3.0-or-later) — same API surface; or GitHub (hosting) |
| Docker Engine + Compose | library | 29.1.3 / Compose v2.29.2 observed on the host (2026-09-14) | builds and runs the git server image (`crafts/lan-git/server/compose.yaml`, the lan-git craft, #181; `server/tests/test_server.py`) — invoked by the Agent's workflow and `scripts/deploy.py`, never by the core package | Apache-2.0 | Podman + podman-compose |
| GHCR (ghcr.io) | library | — | hosts the published lan-git image (`crafts/lan-git/server/IMAGE.md` the lock, #181); private, same classification as the repo (#146 C1) | GitHub terms | Docker Hub, a LAN registry, or a `docker save` archive shipped with the craft export |
| GitHub Actions + `actions/checkout@v4` | library | — | runs the guards on push and PR; absent since 2026-09-14 (billing); replacement pending #24 | GitHub terms / MIT | LAN runner or kernel-only path, gap I2 |
| `actions/setup-python@v5` | library | v5 | installs the pinned Python in CI (`dyad-package.yml`, `dyad-release.yml`) | MIT | kernel Python on a LAN runner, #24 |
| curl | library | 8.5.0 observed | health and API probes in ops scripts and the run-book (`workstation-corpus/ops/`, `runbooks/git-server.md`) — invoked by the Agent's workflow and the Operator, never by the package | curl (MIT-like) | wget, or Python `urllib` (kernel) |
| gh | library | 2.45.0 observed | PR create, merge, checks (Agent workflow) | MIT | GitHub REST via Python, or LAN server API |
| jq | library | 1.7 observed | JSON in Agent workflow | MIT | Python `json` (kernel) |
| Linux (OS) | The World | 7.0.0-31 observed | provides the kernel | — | observed, never pinned |
