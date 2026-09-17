# Audit — is a minimum `sysadmin` craft needed, and does the release lack it? (d-works #57, #58)

Prompted (#57): "evaluate the need to have a minimum `sysadmin` craft to maintain and evolve the
host infrastructure". Then, with #57's plan-`Y` (#58): "Release doesn't include `sysadmin` was the
claim from another installation. falsify. implement survivor." This audit is #57's deliverable and
the falsification #58 asks for; #58 implements what survives here. Disposition: see ledger #57.

## 1. The claim, stated precisely
Two claims travel together and are separated here:
- **C1 (fact):** the dyad-system release does not include a `sysadmin` craft.
- **C2 (need):** it should — an installation cannot maintain and evolve its host without one, and
  the core's own Rules presume one.

## 2. Evidence (observed 2026-09-17 on `main` `b13d67e`; workstation on its `main`)
**E1 — the release.** `gh release view v0.6.0` assets: `BUNDLE.sha256`, `dyad-0.6.0.tar.gz`,
`sysarch-0.1.4.tar.gz`, `syseng-0.1.3.tar.gz`. `BUNDLE.md` rows: dyad-operator 0.6.0, sysarch
0.1.4, syseng 0.1.3. `crafts/`: `REGISTRY.md` (no rows), `sysarch/`, `syseng/`. C1 is true, and
was true of every bundle release (`v0.5.0`, `v0.5.1`, `v0.6.0`).

**E2 — what the core names and cannot resolve here.** `dyad/rules/RULE-8-host-mutation.md`,
`RULE-18-ops-scripts.md`, `RULE-19-server-instances.md` cite `crafts/sysadmin/rules/
{host-mutation,ops-scripts,server-instances}.md` and the guards `sysadmin/{changelog,ops_scripts,
runbooks,events}`; `dyad/vocabulary/VOCABULARY.md` references 14 sysadmin terms by craft name
(`read-only`, `reversible`, `destructive`, `change log`, `undo`, `ops script`, `postcondition`,
`supervisor`, `run-book`, `health command`, `run-book command`, `event`, `role`, `scope`).
`dyad check --guards` on `main`:
`warn [guards] agent/references warn rule.text->path: craft sysadmin absent and not in
crafts/REGISTRY.md … 13 token(s) unresolved here`, and four `skip … guard sysadmin/… absent (no
installed craft provides it)` lines (`changelog.action->ops`, `ops.dwork->row`,
`ops.changelog->changelog`, `changelog.event->event`; `event.command->command` skips by the same
mechanism). `dyad runbook check` → `refused: no craft provides the run-book check
(crafts/*/guards/runbooks.py)`. `dyad/tests/guards/agent/test_references.py`: 7 cases carry
`needs_sysadmin` and skip — "the sysadmin craft's guards are not installed here; their kinds skip
by design". The core craft is therefore released and tested with the craft-side content of three of
its Rules absent; every release so far has been.

**E3 — what exists elsewhere.** `pltrinh1122/workstation` `crafts/sysadmin/`: VERSION `0.1.0`, 38
files, `MANIFEST.md` `requires: dyad-operator>=0.2.0`, `seeds: CHANGELOG.md->workstation-corpus/
CHANGELOG.md`; `rules/`: `host-mutation.md`, `ops-scripts.md`, `server-instances.md` (+README);
`guards/`: `changelog.py`, `events.py`, `ops_scripts.py`, `runbooks.py`; `templates/`:
`CHANGELOG.md`, `events-README.md`, `ops-script.sh`, `runbook.md`; `projectors/`:
`project_events.py`; `vocabulary/CRAFT.md`: the same 14 terms. Its `workstation-corpus/rules/`
holds only a README — host specifics are instance, not craft. Workstation's tags: `v0.1.0`–`v0.3.1`
only; no `sysadmin-vX.Y.Z` tag or archive exists in any repo. `dyad/CLAUDE.md` (core content,
shipped to every install) already lists `crafts/sysadmin/ (system administration, Tended;
extracted #155)` beside sysarch (#160) and syseng (#162): all three were extracted from the same
pre-split monorepo; when `dyad-system` was split out, sysarch and syseng came with it and sysadmin
stayed at workstation.

**E4 — this system's host.** This repo has no `workstation-corpus/` and no host record of any kind.
The machine it runs on is workstation's host (that system's session runs here). Rule-8 Conduct
requires a `workstation-corpus/CHANGELOG.md` row for every reversible or destructive host action
and calls its absence a breach; this system cannot write one.

## 3. Falsification
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | C1 is false: sysadmin is in the release under another name or inside the core. | Refuted | E1: three archives, three rows, no sysadmin; the core's `dyad/` holds only the kernels (Rules 8/18/19) that *name* it. C1 stands as fact. |
| 2 | C2 is false: the absence is by design — #155/#157 made Rules 8/18/19 kernels precisely so the core needs no craft; install, references and tests all tolerate its absence. | Survives, scoped | Tolerated is not satisfiable. The kernels keep "the authorization each class needs and the record's existence" (Rule-8) and the record cannot exist without the craft's guard and template; Rule-18/19 keep "that it is one checked file" and "the observed health pass" with nothing to check either. The tolerance (absent-store skip, `needs_sysadmin`) is Rule-11 p5's fresh-install pattern — a state to pass through, not to ship. C2 stands for any installation that has a host. |
| 3 | C2 is false for *this* system: it needs no sysadmin because it tends no host. | Confirmed, for R1 | E4: the host is workstation's; a second change log here would split one host's record between two systems. This system installs sysadmin so its Rules resolve and its tests run, not to keep a host record. Elevated, not fixed: Rule-8 presumes every system has a host; a pure authoring system on a host another system tends has no clause saying where its host actions (if any) are recorded. |
| 4 | The need is for a *new*, smaller craft — a "minimum" carved from workstation's. | Refuted | E3 vs E2: workstation's sysadmin 0.1.0 is already exactly the kernel contract — 3 rules, 4 guards, 14 terms, no host content. There is nothing smaller. A second craft named `sysadmin` would collide on install (Rule-11 p2 refuses an authored tree). |
| 5 | The survivor is B: keep authorship at workstation, have it publish `sysadmin-v0.1.0`, install from there; the bundle is "what this repo authors" (Rule-11 p7) and stays as it is. | Refuted as sufficient | It fixes installability (no archive exists today — E3) but not E2: the core would still release untested against three of its own Rules' content, unless its CI fetched another repo's release to test itself — a library dependency the kernel-only path is built to avoid (Rule-14 p3). And the enterprise installs #224 plans (backlog #51–#55) would take a craft from a personal workstation repo as their host-administration front door. Kept as the honest counter; not the survivor. |
| 6 | The survivor is C: install sysadmin here as a registry row (not authored), and widen p7 so the bundle carries installed crafts. | Refuted | Rule-11 p7's "what this repo authors" is the property that makes the bundle's sha256 the authoring repo's own claim; an installed craft's archive would be re-published under this repo's tag with its provenance one hop away. Muddier than A for no gain over it. |
| 7 | Moving authorship here (A) contradicts the Operator's arrangement — "workstation is an installation tending the sysadmin craft" — and takes a host practice away from the only system with a host. | Survives, scoped | The Operator is the one party in both systems and is prompting this. What workstation tends is its *host* — `workstation-corpus` (instance) keeps every host-specific rule, run-book, ops script and change log; the craft holds the practice, which is generic (E3). That is already the arrangement for sysarch and syseng: authored here, used live at workstation, defects arriving as intakes with evidence (Rule-3 Intake; #224's five did today). Scoped: the tree that moves is workstation's *current* `main` tree, byte-for-byte, so no change made there since the split is lost. |
| 8 | A breaks workstation: its authored `crafts/sysadmin/` and a bundle `sysadmin-vX.Y.Z` collide. | Refuted | Nothing at workstation changes until its own d-work does it: delete the authored tree, `dyad craft install` from the release (registry row, sha256). Until then its tree is unchanged and its Rules resolve as they do today. Named as the follow-on it is. |
| 9 | A is untestable here: the craft's live checks (`runbook check`, the change-log guard) run on a system with no host. | Refuted | Its guards are fixture-tested (Rule-12; 4 test modules travel with it), and over this instance the absent store skips by Rule-20 p2 — the same footing sysarch and syseng stand on here. Live verification is the installation's, as it is for every craft. |

## 4. Survivor
**C1 is true; C2 is true for any installation with a host; the minimum craft already exists.** The
need is not authoring but a **home and a release**: the survivor is **A** — sysadmin's authoring
home moves to `dyad-system`, as sysarch's and syseng's did, taking workstation's current tree
byte-for-byte; it becomes the fourth bundle row; workstation installs it from the release and keeps
tending its host in `workstation-corpus`. R1 (this system's own host) is answered no, with attack 3's
gap elevated.

## 5. What #58 implements (the survivor's mutation, planned in `plans/58.md`)
1. Craft zone: `crafts/sysadmin/` = workstation `main`'s tree, unchanged; `dyad craft check sysadmin`
   green; its own tests and the 7 core `needs_sysadmin` cases pass on the kernel-only path; any
   drift fix since the split is a craft-zone change and bumps `VERSION` (0.1.0 → 0.1.1), named.
2. Infra zone: `BUNDLE.md` row `sysadmin`; bundle `0.6.0 → 0.7.0` (a new component).
3. Agent zone (docs only): `README.md` names the four components; no Rule edit (the Rules already
   name the craft at the path it will have).
4. Follow-ons, each its own d-work: releases `sysadmin-v0.1.x`, `dyad-operator`/bundle `v0.7.0` (one
   `Y` per tag, Rule-11); a message to workstation with the release and the install step (its
   Operator's d-work there); backlog row for attack 3's Rule-8 gap.

## 6. Elevated for disposition (not fixed here)
- Rule-8 on a hostless system (attack 3): where a pure authoring system records a host action it
  takes on a host another system tends. Proposed: a backlog row.
- The core's CI (`dyad-package.yml`) installs "the core and a Tended craft" into a scratch repo;
  with four crafts it should install all four, so Rules 8/18/19's craft side is exercised on every
  `main` push. Part of #58 step 2 if the workflow change is one line; else its own row.
