# sysadmin — the system-administration craft (Tended craft, `crafts/sysadmin/`, zone `craft`)

What the dyad *does* on a host — host actions, Operator-run ops scripts, server instances with
run-books and telemetry — as one contained, versioned, exportable tree (Rule-11: a Tended craft;
Rule-1: zone `craft`). Extracted from `workstation-corpus/` and from Agent Rules 8, 18 and 19 by
d-work #155 (plan `agent-corpus/d-work/plans/155.md`, classification table adopted from #157). The
core craft `dyad-operator` (`dyad/`) keeps the process kernels of those Rules; each kernel cites the
craft rule it reads by path ("the active craft's <rule> rule"). Version: `VERSION` (0.1.0).

Authored at `pltrinh1122/workstation` since #155; its authoring home moved here by d-work #58
(2026-09-17, this repo's own audit `agent-corpus/audits/2026-09-17-sysadmin-minimum.md`), tree
taken byte-for-byte from workstation `main` `0d50804`. Workstation now installs this craft from the
`dyad-system` release rather than authoring it (its own d-work); `workstation-corpus/` keeps every
host-specific rule, run-book, ops script and change log unchanged.

| path | holds |
|------|-------|
| `rules/` | the three Tended Rules — `host-mutation.md` (Rule-8), `ops-scripts.md` (Rule-18; its mechanics cite the syseng craft's `idempotence.md` since #162), `server-instances.md` (Rule-19) — and their index `README.md` |
| `vocabulary/CRAFT.md` | the craft's terms (fourteen rows moved from the Agent vocabulary; referenced there, never defined) |
| `templates/` | `runbook.md` (seeded by `dyad runbook new <instance>`), `ops-script.sh` (skeleton), `CHANGELOG.md` (the change log's seed; declared in `MANIFEST.md` `seeds:` — `dyad craft check`/`install` warn if `workstation-corpus/CHANGELOG.md` is absent, naming the `cp` to run by hand; never copied automatically, Rule-11 p2, #180), `events-README.md` (seed for `<runbooks>/events/README.md`) |
| `guards/` | `changelog.py`, `ops_scripts.py`, `runbooks.py`, `events.py` — discovered by the core runner (`dyad check --list`) as `sysadmin/<entity>`; each declares `CORPUS = "workstation"`, the Rule-1 zone of the entity's *store* (the stores stay in `workstation-corpus/`) |
| `projectors/project_events.py` | the events surface (`dyad project events`), discovered by the core runner; the discipline it follows is the sysarch craft's `crafts/sysarch/rules/projection.md` (#160 D5) |
| `tests/` | `guards/test_<entity>.py` per guard, `test_project_events.py` for the projector; run by `dyad check` (Rule-12 mapping for crafts) |
| `docs/backup-timeshift.md` | the Timeshift snapshot and backup procedure (generic) |
| `falsification/rules/` | one record per craft rule, carrying the attacks of the core Rule's record that concern the moved text |

The reference git-server deployment moved to its own craft, `crafts/lan-git/` (`requires:
sysadmin>=0.1.0`), by d-work #181 — its run-book still follows `server-instances.md` below.

## What stays in the core craft
The runner `dyad runbook` (`dyad/scripts/runbook.py`): the run-book parser, the event store's
primitives and `list | run | new` — so a system with no sysadmin craft can still run a run-book
(#155 amendment). `runbook check` calls this craft's guard and exits 2 when no craft provides one.
`dyadlib.HOST_CLASSES` (the three class names Rule-8's kernel names; the guards import it).

## What stays in the instance (`workstation-corpus/`)
The change log, the ops scripts already run, the run-book instance and its events, the host docs
(`GIT_SERVER.md`, audit, device fixes), host-specific Tended Rules (`rules/`), host tools
(`scripts/`). Never inside a craft (Rule-11 property 1).

## Importing this craft into another dyad system
`dyad craft install <src> --craft sysadmin` (or an exported archive) writes `crafts/sysadmin/` and
its `crafts/REGISTRY.md` row — nothing else (Rule-11 p2: host-side hooks are the core craft's
only). It warns if `workstation-corpus/CHANGELOG.md` is still absent, naming the exact `cp` to run
by hand (`MANIFEST.md` `seeds:`, #180) — copying it is a manual, one-line step, not automatic.
`dyad check --list` then shows the four guards as `sysadmin/<entity>`. Host values live only in
the host's env file and instance docs; nothing under this tree names a host.
