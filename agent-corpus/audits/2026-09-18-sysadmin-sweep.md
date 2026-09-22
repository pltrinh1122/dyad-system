# Audit — sysadmin craft: completeness and coherence sweep

d-work #83 (plan `agent-corpus/d-work/plans/83.md`). Swept 2026-09-18 at `15c127b`;
**re-verified 2026-09-22 at `25a1834`** before recording, because `main` had moved 30 rows and the
craft itself had changed in nine files (`095a824`, `a2f5753`). Every number below is the re-verified
one; where re-verification changed a finding, the change is stated rather than overwritten.

Disposition: see ledger #83 (Rule-2: the Done-`Y` of this d-work disposes this record).

## Scope and method
The sysadmin craft (`crafts/sysadmin/`) only. Read-only. Every rule, the vocabulary, the manifest,
the templates, the guards, the tests, the records and the README; then five mechanical cross-checks,
each reproducible:

1. every vocabulary term's `rule` column resolves to an existing rule, and the term is used in one;
2. every guard has an owning rule and a test;
3. every template and doc is referenced by a rule, the README or `MANIFEST.md` `seeds:`;
4. every `agent-corpus/…` path a craft file cites exists in this instance;
5. every bare `#<id>` a craft file cites resolves against **this** ledger (Rule-3: a bare `#<id>`
   is a cross-reference into this instance's rows).

## What is sound
Checks 1 and 2 are clean. Fourteen vocabulary terms, each owned by an existing rule and used in it.
Four guards — `changelog`, `events`, `ops_scripts`, `runbooks` — each with a test and a rule that
names it; one projector with a test; one falsification record per rule. `dyad check` is 0 FAIL.
The run-book's ten sections agree across three places — `server-instances.md`, the craft
vocabulary's `run-book` term, and `runbooks.py`'s `SECTIONS` — `Backup` and `Restore` included.

*Correction, recorded rather than dropped:* the sweep first reported `Backup`/`Restore` as missing
from `server-instances.md`. That was a case-sensitive grep on the auditor's part, not a defect in
the craft. Nothing else in checks 1–2 changed on re-verification.

## Findings

### A1 — two ledgers' id spaces are interleaved with no marker (row #84)
The craft's prose cites **16** distinct `#<id>`s (13 at the first sweep; the recent craft commits
added more). **Two resolve locally and correctly** — `#58` (the d-work that moved this craft's
authoring home here) and `#100` (cited by `MANIFEST.md`, resolving to this instance's row on bundle
defects). The other **14** — `#135 #141 #150 #152 #155 #156 #157 #160 #162 #165 #178 #180 #181 #216`
— are `pltrinh1122/workstation` ids, carried over when authoring moved. **Nothing in the text
distinguishes the two kinds.**

Today the 14 resolve to nothing. As this ledger grows past each one they begin resolving **silently
to an unrelated local row**, and a confidently wrong resolution is worse than an unresolved one. The
margin is closing fast: at the first sweep this instance's max id was 89; four days later it is 113,
against a next crossing at `#135`.

The re-verification sharpened the remediation. **The convention already exists and is already in
use in this repo** — row #92's own title reads `workstation#241:…`, and `refs` columns carry
`workstation-184`, `surfacer-242`. So #84 is not "invent a convention"; it is **apply the one
already in use, and guard it.**

Systemic, not sysadmin-only: core Rules aside, sysarch cites 18 foreign ids and syseng 18. The fix
belongs at craft-system altitude.

### A2 — Rule-11 property 1 is enforced for files but not for citations (row #85)
Three craft rules cite `agent-corpus/d-work/plans/155.md`, `162.md` and `216.md`; none exists here.
`distribute.instance_state` — the scan that keeps the instance out of a craft — reads content and
file names, never references, so a craft may not *contain* instance state yet may freely *point at*
it. On re-verification the craft cites two more instance paths than before
(`agent-corpus/falsification/`, `…/extensibility.md`); those two do exist, but the trend is toward
more craft→instance coupling, not less.

`references.py` classes these as `craft_rule.text->provenance … unresolvable (The World),
inference`. That is the wrong class: they are not World references, they are references into a
*named other instance's* ledger, which is resolvable in principle. A1 and A2 are one fault seen
twice — as ids and as paths — and should be remediated together.

### A3 — an undeclared seed (row #86)
The craft README calls `templates/events-README.md` "seed for `<runbooks>/events/README.md`", but
`MANIFEST.md` `seeds:` declares only `CHANGELOG.md->workstation-corpus/CHANGELOG.md`. The mechanism
built for exactly this — warn at `craft check`/`install` when a seed's destination is absent, naming
the copy — therefore never fires for it. Unchanged on re-verification.

### A4 — host-level backup and restore is unowned (row #87)
`docs/backup-timeshift.md` ships a whole-machine snapshot and restore procedure. No rule owns it, no
guard checks it, no vocabulary term names it — it is a doc in a craft whose other content is all
rule-backed. Distinct from a server instance's `Backup`/`Restore` run-book sections, which
`server-instances.md` does own; this is the host itself, and the host is this craft's whole subject.

### A5 — three permanent guard warnings with no recorded adjudication (row #88)
All three rules trip `craft/crafts`'s Rule-4 warning ("mentions 'the Agent', 'counter-prompt' —
binds the Agent's process?"). The classification was deliberately left to inference. But nothing
records that the judgment was *made*, so a reader cannot tell an adjudicated warning from an ignored
one, and the three lines are permanent noise in every `dyad check`. The row asks for the judgment to
be recorded — not for the warning to be silenced.

### A6 — no ops-script scaffolder (row #89)
`dyad runbook new <instance>` seeds a run-book from the craft's template; nothing seeds an ops
script from `templates/ops-script.sh`. Every ops script is hand-copied against a rule with seven
form properties and a guard that enforces them. Rule-13 property 1 (recurrence proposes code).
Minor.

## Confirmed but not re-filed
- The craft's two unwritten scope areas — host-side packaging and installation, and the host
  platform abstraction — are **#81**. The sweep confirms the gap: `rules/README.md` has three rows
  against a stated scope that now has five areas.
- A dyad system with no host at all is **#60**.
- The launcher defect that disables this craft's own guards on a host whose `python3` is below the
  kernel pin is **#82**.

## Drift found on re-verification, outside this sweep's scope
`main` moved past three files **#81**'s stored plan names — `crafts/sysadmin/VERSION`,
`MANIFEST.md` and `rules/host-mutation.md` — and past `BUNDLE.md`. `crafts/sysadmin/VERSION` is now
`0.1.2`, not the `0.1.0` that plan's mutation assumes. Under Rule-15 phase 2 **#81 requires a
re-plan and a fresh plan-`Y` before execution**; its plan-`Y` of 2026-09-18 no longer binds a
current base. Reported here because the sweep found it; disposing it is the Operator's.

**#82**'s own files (`dyad/bin/`, `dyad/hooks/`) did not move, and its defect persists at
`25a1834`: all three launchers still `exec python3`, `python3` is still 3.11.15, the entrypoint
still exits 1. It executes as planned.

## Limits of this sweep, stated
`dyad craft install` into a scratch repo was not exercised, so A3's practical effect — the
absent-destination warning that never fires — is reasoned from the manifest, not observed. Worth
doing when #86 is worked. And the sweep was scoped to one craft while its central finding is
systemic; sysarch's and syseng's counts are given so the altitude is visible, without auditing
either.
