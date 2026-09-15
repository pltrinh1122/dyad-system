# Falsification record — Rule-20 (referential integrity), Operator rule 2026-09-14 (ledger #142)

**Claim (operator, 2026-09-14):** extend the Rules to minimize inferencing and manual bridging
during audit verification and guard execution; entity instance references (a change-log row's
`d-work`, for one) should be mechanically verified against a valid instance.

Observed at the base commit (5363edc): 24 reference kinds in the corpus (plan #142, table); 4 have a
resolver today (`vocabulary.py` owner and used-by, `infrastructure.py` rules→manifest,
`dwork_link.py` PR body→row); 2 are unresolvable by design (PR numbers; the memory cache); 18 are
bridged by inference — sweeps 5 and 6 each state "every `Rule-N` cited … resolves" by hand, and the
#137 incident (Rules 17 and 18 unimported for a day) is an unresolved reference nobody checked.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Not a new Rule: Rule-12 already prefers code over inference wherever a check can be mechanical; one property there suffices. | Refuted | Rule-12 chooses among implementation paths *of a plan* and never widens it (its Boundaries); it cannot name what must be checked. Rule-17 p1 makes parsed data the source of a surface, not of a resolution. No Rule owns "a reference resolves"; Rule-5 owns it for Rule↔Rule only, by inference. A concern with its own guard, data and register is a Rule (Rule-18 attack 6, same reasoning, Operator's choice). |
| 2 | Rule-5 owns cross-reference resolution ("every cross-reference resolves to an existing Rule and heading"); Rule-20 shares the concern — a Rule-5 gap by Rule-5's own definition. | Survives, scoped | Rule-5 keeps the meaning (coherence of the set); Rule-20 owns the mechanism for every entity, of which Rule↔Rule is one kind — the S4 pattern (Rule-11 runs, the owner defines; Rule-14 scans, Rule-13 judges). Rule-5's Enforcement ("no script can decide coherence") stays true; its cross-reference clause becomes mechanically evidenced. Rule-5 is not edited in this d-work; a one-line Enforcement pointer is Q1. Boundaries of Rule-20 name Rule-5 as owner of meaning. |
| 3 | Rule-3 owns `dwork_link.py`, Rule-6 `vocabulary.py`, Rule-14 `infrastructure.py`: a second resolver for the same reference breaches "exactly one resolver" in Rule-20's own words. | Refuted | The register names the existing guard (`guard:<script>`) and refint never re-runs it; the projector gets the edge from the one list. Rule-20 adds resolvers only where none exists. Rule-20 Boundaries list them as theirs. |
| 4 | False positives: `Rule-7` appears 15 times (backlog #54); "#16 blocked" in prose; `merge #164` is a PR, not a row. | Refuted | Fields, not prose: refint scans parsed fields and, as prose, only Rule texts, the frame and the preference table — where every `Rule-N` resolves today (`grep -rhoE 'Rule-[0-9]+' dyad/rules dyad/vocabulary` → 1–6, 8–19). Records and audits are scanned for `ledger #N` only. `PR…` segments and `merge #n` are typed `pr` → `world`. `Rule-7` in `dyad/README.md` and in attack prose is never read, and the Boundaries say so. |
| 5 | Cross-zone read: `workstation-corpus/CHANGELOG.md` and `ops/*.sh` cite agent-zone rows; a guard reading both zones breaks Rule-1. | Refuted | Rule-1 sees transactions (paths in one commit), not reads; `ops_scripts.py` already reads the workstation zone from agent-zone code. The guard is agent-zone code; the PR touches one zone. |
| 6 | The package cites the instance (`ledger #52` in Rule-3, `#108` in Rule-11, `d-work #24` in Rule-1): in a scratch install (Rule-11 p5 CI runs `check --guards` there) the rows are absent and the guard turns green CI red. | Confirmed | Property 4: an absent or empty target store skips its kinds with a printed line; the scratch-install fixture tests it. The deeper finding — Rule text carrying instance ids is a Rule-11 p1 leak the current `package_rules.txt` does not catch — is reported as Q2, not fixed here. Closed by #177: property 4's skip only ever covered an *empty* store; the first row opened in any receiving instance turned this from Q2's tolerated gap into 118 FAIL (109 `record.ledger->row`, 9 `rule.text->row`), reproduced and fixed — `record.ledger->row`/`rule.text->row` split by the citing file's source path (`dyad/` and a Tended craft's `falsification/rules/` or `rules/` resolve `world`, unconditionally; `agent-corpus/` keeps resolving against the local row store). See `## Amendment — d-work #177` below. |
| 7 | Grandfathering needs a hand list (rows before #46 carry no disposition chain, Rule-3). | Refuted | Property 3: resolvers test existence only; rows 1–142 all exist; ranges (`#1–#3`) expand to ends that exist. No list, no cutoff. |
| 8 | Performance: every store read on every hook. | Refuted | Pre-push only (`check --guards`), never pre-commit; ~300 small files and one `git cat-file --batch-check`; the fixture test bounds it and the live run is expected under a second. |
| 9 | #139 (frame-import guard) deserves its own row and Done. | Survives, scoped | Folded as kind 12 (frame `@rules/` → Rule file and the reverse); #139 is blocked on #142 and closed by its Done (Rule-3 child pattern). Separate would mean a second resolver for the frame entity or a second register. |
| 10 | Existence is weak: a typo `#135` for `#136` resolves. | Survives, scoped | Stated in property 3 and Enforcement: existence is what a guard can decide; the intended target is the owning Rule's (Rule-3 completion evidence, Rule-8 change log). Property 5 draws the edge so a wrong target is visible on the surface. |
| 11 | Writing the `REFERENCES` entries in the plan implements before plan-Y (Rule-9: only survivors are implemented). | Refuted | The entries are the mutation stated exactly (Rule-15 phase 1); execution writes the code after plan-Y and may not depart (Rule-3). |
| 12 | The projector's authored `RELATIONS` was Rule-17's "one authored table"; importing it from a guard makes a surface depend on a check. | Refuted | Rule-17 p1: a projector consumes the parser the owning Rule provides. Rule-20 now owns the relation data, so the import is the property; Rule-17's record already called the table "a schema's arrow labels" — which is what a resolver list is. |
| 13 | Paths in Rule text are patterns (`dyad/rules/RULE-*.md`, `plans/<id>.md`), commands (`package.py check`) or generated (`LEDGER.md`); a literal existence check fails all eleven today. | Confirmed | Extractor cuts at the first space; `<…>` and `*` are glob wildcards needing one match; a `generated:` pattern match (Rule-11 data) is accepted. Verified against the eleven observed. |
| 14 | Rule-19's run-book will cite ops scripts and compose files: a kind the register does not have. | Survives, scoped | Condition 2: a new kind lands with its entry in the same d-work; until then the audit names it as unresolvable. The register is data; the Rule-19 guard d-work adds the row. |

Deferred, named: content resolution (does the change-log action match the plan's H-row; does a
pairwise `18–8` statement hold) stays inference by the owning Rule. Q1–Q3 in plan #142 await the
Operator.

## Rule-5 pairwise statements (Rule-20 added; no other Rule edited)
- 20–1: agent-zone code reading every zone's stores; a transaction still touches one zone; this PR
  is agent zone only. 20–2: no ratification event. 20–3: rows, plans and incidents are read, never
  written; `dwork_link.py` stays Rule-3's transaction gate, listed as `guard:`; the Done-Y and plan-Y
  untouched. 20–4: block conforms (intent 1, target 1, boundaries 6, conditions 4). 20–5: Rule-5
  owns coherence (meaning); Rule-20 owns resolution (mechanism) for every entity; Rule-5's
  cross-reference clause gains mechanical evidence without an edit (Q1 later). 20–6: two terms,
  `reference` and `resolver`, owner 20, used by 20; `vocabulary.py` stays Rule-6's resolver, listed.
  20–8: the change-log row is read; class, undo and row remain Rule-8's; the Operator's example
  (`d-work` → row) is kind 15. 20–9: this record; every claim in the plan attacked. 20–10: framed
  in the plan (path, counter, reconciliation, one Y/N). 20–11: package code under one root; the
  runner invokes `check_rule_20` and owns none of its semantics (S4); empty-store skip keeps the
  scratch install green; instance ids in Rule text reported (Q2). 20–12: `refint.py` carries
  `test_refint.py`; Rule-12 chooses the path, Rule-20 names what is checked. 20–13: no import; stdlib.
  20–14: no new World row; `git` and Python are kernel; `world` kinds name The World as
  unresolvable. 20–15: the plan file's id and base commit are kinds 4 and 5; the plan store is
  Rule-15's. 20–16: row files read at the working tree, never edited; ids and transitions stay the
  fence's. 20–17: property 5 — the projector consumes `REFERENCES`; Rule-17 p1 satisfied, its own
  table removed. 20–18: `# d-work:` and `# change-log:` values resolve (kinds 18, 19); presence
  stays `ops_scripts.py`'s. 20–19: no run-book kind yet (attack 14). Coherent, orthogonal.

## Rule-6: two terms added (`reference`, `resolver`), owner 20.

Disposition: see ledger #142.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/refint.py` → `dyad/guards/agent/references.py`; `guard:` resolvers name `<corpus>/<entity>.py`; kinds 12 and 13 (frame imports) are `guard:agent/frame.py`'s (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
no Rule edit. Mechanism: kind 11 (`rule.text->path`) extracts backticked `crafts/…` tokens too, so a kernel's citation of "the active craft's <rule> rule" is resolved; on a core-only install (no `crafts/` tree) those tokens skip with one line (property 4); the five kinds whose parser is a craft guard skip with a line when no installed craft provides it (`GUARD_KINDS`). Tests: `test_rule_text_craft_path`, `test_core_only_install_skips_craft_paths`, `test_absent_craft_guard_skips_its_kinds`.

## Amendment — d-work #160 (2026-09-14, sysarch extraction R-craft-3)
Properties 1, 2, 3, 5, 6 and conditions 2 and 4 moved to `crafts/sysarch/rules/references.md` (with the leaf entities and
the craft-contributed-rows design, plan #160 D6, attack 10); the kernel (one register / one resolver / existence as one
property, severity, the run) stays. `reference` and `resolver` move to the craft vocabulary. Kind 15 (`registry.module->file`)
now resolves repo-relative `crafts/<craft>/projectors/…` paths from the discovered registry. Pairwise: 20–5 unchanged; 20–11
paths resolve. Coherent, orthogonal. Disposition: see ledger #160.

## Amendment — d-work #177 (2026-09-14, install-portability G1: attack 6's Q2 closed)
Attack 6 was Confirmed with Q2 left open ("Rule text carrying instance ids is a Rule-11 p1 leak
… reported, not fixed"); #176 (G1) reproduced the consequence exactly: a scratch install of the
core craft plus all three Tended crafts passes `check --guards` at 0 FAIL with an empty ledger
(property 4's skip), then fails at 118 (109 `record.ledger->row`, 9 `rule.text->row`) the instant
a single d-work is opened anywhere in the receiving instance — permanently, since a fresh
instance's own numbering never coincides with this authoring instance's. Mechanism (no Rule-20 or
`crafts/sysarch/rules/references.md` text edit; property 2's severity model — "a `world` kind
prints one `warn … inference` line" — already covers it; S4, register data only): `record.ledger->row`
and `rule.text->row` now partition by the *citing file's own path*, not by whether the cited
number happens to exist. A falsification record or Rule under `dyad/` or a Tended craft's
`falsification/rules/`/`rules/` (`crafts/*/…`) — package-shipped either way — resolves its
`ledger #N` / `d-work #N` citations `world`: two new kinds, `record.ledger->provenance` and
`craft_rule.text->provenance` (the latter previously unscanned in any form — a Tended craft's own
rule text, e.g. `crafts/sysadmin/rules/host-mutation.md`'s "d-work #155", carries the identical
problem); `rule.text->row`'s resolver becomes `world` in place (its source, core Rule text, is
always package — no instance-authored numbered Agent Rule exists, so the split degenerates to
"always world" for that one kind, stated rather than built as a dead branch). `record.ledger->row`
keeps its name, position and resolver (`row_exists`), narrowed to instance-only records
(`agent-corpus/falsification/`, `agent-corpus/audits/`, never under a `rules/` directory) — an
instance's own record citing its own missing row is still a real, checked bug. Two new
`INVARIANTS` hold the split in place: `package-ledger-kinds-stay-world`,
`instance-record-ledger-stays-checked`. Traded away, stated rather than hidden (plan #177 attack
1): a genuine typo in a package Rule's or record's own citation is no longer mechanically caught
anywhere, including in this authoring repo — existence-only checking never verified *content*
correctness in the first place (attack 10, above), and the real defense for this class of
citation was always the Operator's Done-`Y` at authoring time, not this guard. Tests:
`dyad/tests/guards/agent/test_references.py` (new kinds, the source-path split, the register-shape
counts); `dyad/tests/test_package.py` `test_scratch_install_with_one_row_survives_referential_integrity`
— the Rule-11 property-5 scratch-install fixture's missing "one row present" case, now covered so
this exact regression is a red test, not just a green-until-the-first-d-work CI step. Pairwise:
20–11's "instance ids in Rule text reported (Q2)" is now "… resolved (#177)"; no other pairwise
statement changes (the register's shape — one row per kind, one resolver each — is unchanged;
three rows changed or gained a `world` resolver, which #142's own design already provided for).
Coherent, orthogonal. Disposition: see ledger #177.
