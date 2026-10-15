# sysadmin — the system-administration craft (Tended craft, `crafts/sysadmin/`, zone `craft`)

What the dyad *does* on a host — host actions, Operator-run ops scripts, server instances with
run-books and telemetry — as one contained, versioned, exportable tree (Rule-11: a Tended craft;
Rule-1: zone `craft`). Extracted from `workstation-corpus/` and from Agent Rules 8, 18 and 19 by
d-work #155 (plan `agent-corpus/d-work/plans/155.md`, classification table adopted from #157). The
core craft `dyad-operator` (`dyad/`) keeps the process kernels of those Rules; each kernel cites the
craft rule it reads by path ("the active craft's <rule> rule"). Version: `VERSION` (0.3.0).

Authored at `pltrinh1122/workstation` since #155; its authoring home moved here by d-work #58
(2026-09-17, this repo's own audit `agent-corpus/audits/2026-09-17-sysadmin-minimum.md`), tree
taken byte-for-byte from workstation `main` `0d50804`. Workstation now installs this craft from the
`dyad-system` release rather than authoring it (its own d-work); `workstation-corpus/` keeps every
host-specific rule, run-book, ops script and change log unchanged.

| path | holds |
|------|-------|
| `rules/` | the five Tended Rules — `host-mutation.md` (Rule-8), `ops-scripts.md` (Rule-18; its mechanics cite the syseng craft's `idempotence.md` since #162), `server-instances.md` (Rule-19), and the two no core kernel reads, `host-install.md` and `host-platform.md` (adjacent: Rule-11 p2, Rule-8; #81) — and their index `README.md` |
| `vocabulary/CRAFT.md` | the craft's terms (fourteen rows moved from the Agent vocabulary, referenced there, never defined; four added by #81: `host platform`, `platform contract`, `prerequisite`, `host install`) |
| `templates/` | `runbook.md` (seeded by `dyad runbook new <instance>`), `ops-script.sh` (skeleton), `CHANGELOG.md` (the change log's seed; declared in `MANIFEST.md` `seeds:` — `dyad craft check`/`install` warn if `workstation-corpus/CHANGELOG.md` is absent, naming the `cp` to run by hand; never copied automatically, Rule-11 p2, #180), `events-README.md` (seed for `<runbooks>/events/README.md`) |
| `guards/` | `changelog.py`, `ops_scripts.py`, `runbooks.py`, `events.py` — discovered by the core runner (`dyad check --list`) as `sysadmin/<entity>`; each declares `CORPUS = "workstation"`, the Rule-1 zone of the entity's *store* (the stores stay in `workstation-corpus/`) |
| `projectors/project_events.py` | the events surface (`dyad project events`), discovered by the core runner; the discipline it follows is the sysarch craft's `crafts/sysarch/rules/projection.md` (#160 D5) |
| `tests/` | `guards/test_<entity>.py` per guard, `test_project_events.py` for the projector; run by `dyad check` (Rule-12 mapping for crafts) |
| `docs/backup-timeshift.md` | the Timeshift snapshot and backup procedure (generic) |
| `falsification/rules/` | one record per craft rule, carrying the attacks of the core Rule's record that concern the moved text |

The reference git-server deployment moved to its own craft, `crafts/lan-git/` (`requires:
sysadmin>=0.1.0`), by d-work #181 — its run-book still follows `server-instances.md` below.

## Scope
Four areas, each one rule or a pair: **host actions** (`host-mutation.md`: class, procedure,
record), **operator-run commands** (`ops-scripts.md`), **server instances** (`server-instances.md`:
run-book, health, events), and — since d-work #81 — **host-side packaging and installation**
(`host-install.md`: what a host must provide, how the act is verified, authorized, recorded and
known complete) and **the host infrastructure abstraction** (`host-platform.md`: which platforms
this system supports, with a status per platform, and what each one demands). The last two land on
ground three neighbours already hold, so #81 cut the seam below rather than share ownership
(Rule-5); each neighbour keeps what it had, and the two new rules state the seam from this side
only. The reciprocal sentence in each neighbour is a `backlog` row of #81's, not an edit made here.

| today's owner | what it owns | verdict |
|---|---|---|
| Rule-11 kernel | craft/instance split; what an install *writes*; VERSION, tag, bundle | keeps it |
| `crafts/sysarch/rules/distribution.md` | the *design*: archive shape, version seed, entrypoint, upgrade order | keeps it |
| `crafts/syseng/rules/idempotence.md`, `determinism.md` | the *implementation discipline*: scripted, idempotent, byte-identical | keeps it |
| `crafts/syseng/rules/host-facts.md` | "this rule is about *portability*" — one place per host fact, `hostadapter.py`, two functions not a framework | the seam: syseng keeps *how a host fact is read in code*; sysadmin keeps *which platforms exist and what each requires* |
| Rule-8 / `host-mutation.md` | classes and records *any* host action, an install included | keeps it |

Rule-11 and sysarch say what is distributed and what an install writes; sysadmin says what a host
must provide for that install to succeed, and how the act is performed, authorized and recorded on
a live host. Different targets; no shared ownership. Which platforms the dyad runs on is a property
of the practice, not of the code — hence the second seam.

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
the host's env file and instance docs; nothing under this tree names a host. This craft is also a
bundled craft (Rule-11 p2, d-work #114): the core release carries its tree, so `dyad install` of
the core writes `crafts/sysadmin/` too and a system that installs the core alone still has it —
`dyad craft install` is the path for a craft-only update, not the only path.
