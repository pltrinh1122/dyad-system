# Mandates (preferences zone; the organization's charters — cos craft, `rules/organization.md` §3; seeded from `crafts/cos/templates/mandates.md` by #385 PR-B, d-work #379)

Operator-owned, like every value under `preferences-corpus/`: one row per seat, a standing mandate the Operator
holds and a seat reads; changed only by a preferences-zone PR the Operator disposes, never by a seat. Columns as
`crafts/cos/guards/seats.py` reads them (`MANDATE_COLUMNS`): `seat` is the seat name, or the name's form with
`<hp>` until the seat is opened; `function` one of `crafts/cos/guards/seats_rules.txt`; `fence` the paths and
kinds of act the seat's rows may touch (what the zone guard and the plan gate read); `ceiling` how many rows one
plan of the seat may accrete; `escalations` what returns to the Operator as its own question whatever a plan says;
`revocation` the preferences-zone change that ends the charter. Under every row stand the core's never-accretable
acts (Rule-2 Binding, Rule-3 Scope): a merge or push to `main`, a destructive host action, a release, a preference
value, an intake's words, any mutation no plan described — a charter narrows and never widens.

| seat | function | domain | fence | ceiling | escalations | revocation |
|------|----------|--------|-------|---------|-------------|------------|
| program-59cec502 | program | the board of programs: every parent row and its children across the members; relay and roll-up | `<instance>/d-work/` rows, plans, provenance and its own presence file; `preferences-corpus/` by PR only — the cos alone among seats proposes a preference value or a charter, each as its own question the Operator disposes (#426); no other zone; accretes nothing | 0 | every question a member asks; every preference value or charter proposed; a board longer than seven lines; a seat the table does not name | this row removed or rewritten |
| counsel-0032b4c0 | counsel | the Rules, the vocabulary, the countersign model, the crafts' governance and shape | `dyad/rules/`, `dyad/vocabulary/`, `dyad/playbooks/`, `dyad/falsification/`, `crafts/<craft>/rules`, `/vocabulary`, `/falsification`, `/docs`; its own records under `<instance>/falsification/` | 8 | a Rule edit that changes a trigger or a ratification event; a term another craft defines; a path outside the fence | this row removed or rewritten |
| audit-<hp> | audit | the standing audit, the self-diagnostic, incident hardening, the Rule-5 sweeps | read-only over the whole tree; writes only `<instance>/audits/` and `<host>/runbooks/events/`; proposes rows, opens and fixes none | 0 | every finding; a fix of any kind | this row removed or rewritten |
| engineer-1537d8fb | engineer | the machine: the core's guards, CLI, stores, trace, board and their tests | `dyad/scripts/`, `dyad/guards/`, `dyad/tests/`, `dyad/templates/`, `dyad/infrastructure/`; `dyad/rules/` only by one sentence a code change needs | 8 | a Rule sentence beyond the one a change needs; a store's shape; a reference kind added or removed | this row removed or rewritten |
| distribute-b7a0a9fc | distribute | the shipping of every craft: install, port, release, bundle, registry and their tests | `dyad/scripts/distribute.py`, `craft.py`, `package.py build/install`, `.github/workflows/`, `BUNDLE.md`, `crafts/REGISTRY.md`, the port play-book | 6 | every release tag (never accretable); a port into another system (an intake there); a bundle row | this row removed or rewritten |
| operate-<hp> | operate | the host: read-before-act, classes, ops scripts, run-books, change-log rows, the services behind boards | `<host>/` (ops, run-books, change log, host records), `crafts/sysadmin/`; no host action outside an ops script or run-book the Operator runs | 6 | every destructive action (never accretable); a run-book command that does not work as written | this row removed or rewritten |

Seats open at seeding (2026-10-22): `program-59cec502`, `counsel-0032b4c0`, `engineer-1537d8fb`, `distribute-b7a0a9fc`; `audit-<hp>` and `operate-<hp>` keep the form until the Operator opens them (plan #369 revision 7). Each row is #368 revision 3's charter as the template carries it; the Operator rewrites a row by a preferences-zone PR.
