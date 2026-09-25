# System Infrastructure — instance contribution (Rule-14)

This system's own operating rows, as observed on it: the part of the one manifest that is instance, not
core (`dyad/infrastructure/INFRASTRUCTURE.md` holds the kernel and the authoring library; crafts add
theirs through `infrastructure_contrib.md`). Same seven cells; read by `dyad/guards/infra/manifest.py`
from the host path (preference `host-path`, default `workstation-corpus`; #175). A component declared
here and anywhere else fails, naming both.

| component | partition | version | purpose | license | replacement | profile |
|-----------|-----------|---------|---------|---------|-------------|---------|
| Gitea | library | 1.27.3 pinned (image `gitea/gitea:1.27.3`, Alpine 3.24) | LAN git server image base: `main`, PRs, branch protection requiring the `dyad/guards` status, operator/agent accounts (`crafts/lan-git/server/`, the lan-git craft, #181; `crafts/sysadmin/server/`'s reference deployment before it, #155; instance #124 before that; selected #24) | MIT | Forgejo (GPL-3.0-or-later) — same API surface; or GitHub (hosting) | operating |
| Docker Engine + Compose | library | 29.1.3 / Compose v2.29.2 observed on the host (2026-09-14) | builds and runs the git server image (`crafts/lan-git/server/compose.yaml`, the lan-git craft, #181; `server/tests/test_server.py`) — invoked by the Agent's workflow and `scripts/deploy.py`, never by the core package | Apache-2.0 | Podman + podman-compose | operating |
| GHCR (ghcr.io) | library | — | hosts the published lan-git image (`crafts/lan-git/server/IMAGE.md` the lock, #181); private, same classification as the repo (#146 C1) | GitHub terms | Docker Hub, a LAN registry, or a `docker save` archive shipped with the craft export | operating |
| curl | library | 8.5.0 observed | health and API probes in ops scripts and the run-book (`workstation-corpus/ops/`, `runbooks/git-server.md`) — invoked by the Agent's workflow and the Operator, never by the package | curl (MIT-like) | wget, or Python `urllib` (kernel) | operating |
