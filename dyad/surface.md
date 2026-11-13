# Public surface of `dyad-operator` (d-work #573; v1.0 exit criterion H3, mandate #570)

This file lists everything that a system installing the core craft types, reads or writes, and that would break if it
changed. Under semver, 1.0.0 freezes it (plan #570, attack A1). The bundle and the core move to 1.0. Every Tended
craft keeps its own number and its own surface, so crafts are out of scope here (decision 1 of #570).

Each item has a status:
- `frozen`: removing, renaming or narrowing it needs a major; adding beside it is a minor.
- `moving (#<row>)`: a 1.0 child row is still changing it.
- `alias → <new>`: an old spelling still accepted beside the new one. None is left: the #554 aliases warned in
  `dyad-operator-v0.18.0` and were removed by #604 for 1.0.0 (the operator's decision on B3, provenance #573), and a
  stored old form now fails its guard naming the new one. The suite fails on any `alias` mark.

`dyad/tests/test_surface.py` pins this file (`dyad/surface.md`) against the code in both directions. A surface change without an edit
here fails the suite, and so does an entry here that the code no longer has, or any `alias` mark (#604). With
`DYAD_SURFACE_RELEASE=1`, any `moving` mark fails too, which is the gate before R1's cut.

**Not surface:**
- internal modules, their functions and their flags to git;
- `LEDGER.md` (rendered, untracked);
- the suite memo, the `dyad-evidence/` cache and the `dyad-sweep/` report cache (#619);
- falsification records and audits (history);
- the cabinet guard's entity `seat`, a craft identifier (`dyad/vocabulary/crosswalk.md`).

## S1 CLI

The entrypoint is `dyad/bin/dyad`, invoked by path (Rule-11 p2), in the form `dyad <noun> [<verb>] [flags]`. The
nouns are the dispatch in `dyad/scripts/package.py`. Every form is a row of one table, `dyadlib.CLI`, which this section
equals (the flags of each row, both directions) and which a gate reads before any dispatch (#592): `-h` or `--help`
anywhere outside a flag's value prints the form's usage and exits 0, running nothing; a flag the form does not take
prints `refused: dyad <noun> <verb> does not take <flag>` and exits 1, as does a word past the form's positionals; a
flag given twice that the form reads once prints `refused: dyad <noun> <verb> takes <flag> once` and exits 1
(`inbox post --cc`, `dwork trace --transcript`, `session touch -r`/`-f` repeat). A flag that takes a value takes the
next word whole, whatever it spells; a word not shaped like a flag (`-`, `- item`, `-1 rows`) is a word, and from
`inbox post`'s body on every word is.

| form | flags | status |
|---|---|---|
| `dyad check` | — | frozen |
| `dyad check --list` | — | frozen |
| `dyad check --guards` | `--pre-push [<remote> <url>]` (empty stdin fails with its line on a hand run, passes when git sends `<remote> <url>`; a tty is refused; a missing core tag fails, except on a ledger-only or events-only push, which prints one skip line, #621) | frozen |
| `dyad check --corroborate [<before> [<after>]]` | — | frozen |
| `dyad check --pr <base> [<head>]` | — | frozen |
| `dyad check --tests [<target>]` | — (a dotted target whose first part names nothing at the repo root is refused, with the qualified name of every test-root module of that path, at any depth, #592) | frozen |
| `dyad check --evidence` | `--brief`, `--at <rev>`, `--show <sha256>` | frozen |
| `dyad build [<out>]` | — | frozen |
| `dyad install <repo>` | `--from <src>` | frozen |
| `dyad bundle check` / `build [<dir>]` | — | frozen |
| `dyad craft new <name>` / `list` / `check [<craft>]` / `export <craft> [<out>]` / `install <src>` | `--force`, `--dwork <N>`, `--craft <name>`, `--source <text>` | frozen |
| `dyad craft diff <craft>` | `--against <src>`, `--patch` | frozen |
| `dyad ledger` | — | frozen |
| `dyad dwork new <title> [<refs>]` | `--backlog`, `-d`, `-r`, `--prompt`, `--prompt-file`, `--said`, `--said-file`, `--relayed-via`, `--mandate` (refuses past the plan's stated ceiling, #592), `--slug` (refused without it under `dwork-slug: on`, #622), `--land`, `--mirror` | frozen |
| `dyad dwork state <id> <state>` | `-d`, `-r`, `--prompt`, `--prompt-file`, `--said`, `--said-file`, `--said-ref`, `--relayed-via`, `--mandate`, `--retired-by` (#574), `--slug` (once, on a row that holds none and is not terminal, #622), `--decisions` (the decision log, with a `Y done` or a `Y precedent (…)`, #644), `--mandate-preference` (`backlog` → `open` under a mandate preference, #692), `--check`, `--land`, `--mirror` (`planned` prints the plan check, #592) | frozen |
| `dyad dwork retire <id>...` | `-d`, `--said`, `--said-file` | frozen |
| `dyad dwork intent <id>` | — (read-only: the rows of any state and the surface items nearest the row's prompts, ten each, no threshold, #615) | frozen |
| `dyad playbook profile <name>` | — (read-only: a play-book's steps with their words, `dmc:` citations and commands, its cited records' words and kind, the run total, and the median trace seconds of rows whose plan names it, #642) | frozen |
| `dyad precedent prompt <cases-file>` | `--out` (read-only: the blind prompt, each record's question and outcomes and each case's facts, never its label; refuses a record not judged by inference or operator-side, #645) | frozen |
| `dyad precedent score <cases-file> <answers-a> <answers-b>` | `--kept` (read-only: each reader's score per record, the kept cases and each mismatch, model-limit or context-gap; `--kept` writes the kept as a decisions input file, #645) | frozen |
| `dyad precedent gate <kept-file>` | `--out` (read-only: each line judged by precedent-admission as its case's precedent line would be, before the question; prints each refused line and writes the admitted, #645) | frozen |
| `dyad precedent agreement <record>` | — (read-only: the record's admitted cases re-measured leave-one-out: n, reproduced, abstained, agreement, its bar, #645) | frozen |
| `dyad dwork list` | `--state`, `--craft` | frozen |
| `dyad dwork land <path>...` | `-m`, `--mirror` | frozen |
| `dyad dwork batch <file>\|-` | `--land`, `--mirror` | frozen |
| `dyad dwork trace <id>` | `--transcript <path>`, `--out`, `--said-file <f>` (#592: `--out` needs the Done words; `--said-file` needs `--out`) | frozen |
| `dyad plan check <id>` | — | frozen |
| `dyad session [<root>]` | — (the presence guard by hand) | frozen |
| `dyad session name` | `--function`, `--topic`, `--hp`, `--system`, `--on` | frozen |
| `dyad session touch` | `-r <row>`, `-f <file>` (`-r` splits on whitespace; fetches origin first) | frozen |
| `dyad session list` | — | frozen |
| `dyad session reconcile` | — | frozen |
| `dyad project <surface>` / `--list` | `--craft <name>` (the kanban projector's, #22) | frozen |
| `dyad runbook check` / `list <instance>` / `run <instance> <name>` / `new <instance>` | `--as operator\|agent\|automaton` (automaton: a read-only command only, #593); `<instance>` may be `<craft>:<name>`, a craft's `crafts/<craft>/runbooks/<name>.md` (#640) | frozen |
| `dyad release` | `--scan` | frozen |
| `dyad release ready <row> <tag>` | `--at <cut>`, `--archive <sha256>` | frozen |
| `dyad merge <pr>` | `--head <sha>` | frozen |
| `dyad board` / `board set <id>\|_cos[-<operator>] key=value...` / `board resume` / `board advance <id>... <event>` / `board phases` / `board draft <id>` / `board groom` | `--drop`; advance: `--expect`, `--said-file`, `--decisions` (the Done answer's candidate rulings, #648), `--mirror`; draft: `--out <file>`, `--decisions-out <file>` (the row's candidate rulings as a decisions input file, #648) | frozen |
| `dyad inbox post <unit> [<body>...]` / `list [<unit>]` | `--row`, `--kind report\|relay\|ack\|notice`, `--body-file` | frozen |
| `dyad inbox read [<message>...]` | — (no name prints the unread messages and writes nothing; names mark exactly those read in one land and fire the machine's `read`, which changes no board entry; the flag --all removed, #587 S10) | frozen |
| `dyad inbox post … --cc <unit>` | — | frozen |
| `dyad automaton scan` / `run` | — | frozen |
| `dyad automaton run --evidence-from <file>` / `evidence --out <file>` | — | frozen |
| `dyad automaton sweep` | `--row <id>`, `--stores` (the whole-store guards only, after each ledger push, #617) | frozen |
| `dyad steps verify-prs` / `done-record` / `close-landed` / `sync-mirror` | `--land` | frozen |
| `dyad bootstrap` | `--check` | frozen |

## S2 Store formats

Paths are relative to `<instance>` (`DYAD_INSTANCE`, default `agent-corpus`) or `<runbooks>` (`DYAD_RUNBOOKS`). Keys
are each guard's own constant, the source the test reads.

| store | path | keys | source | status |
|---|---|---|---|---|
| row | `d-work/rows/<id>.md` | `id`, `title`, `opened`, `state`, `disposed`, `refs`; optional `mode`, `slug` (#622); every date UTC from dyad-operator 1.0.0 on, earlier entries as written (#592) | `dyadlib.FIELDS`, `OPTIONAL_FIELDS` | frozen |
| row states | — | `open`, `planned`, `blocked`, `backlog`, `done`, `archived` and Rule-16's transitions (open → archived on the bare intent-N, #615; open or planned → archived on the retirement form's sweep entry, #697) | `dyadlib.TRANSITIONS` | frozen |
| board entry | `d-work/board/<id>.md` | `holder`, `phase`, `owner`, `waiting-on`, `next`, `since`, `question`, `promised`, `note`, `writer`; optional `cabinet`, absent meaning program | `board.FIELDS` | frozen |
| board `cabinet` value | — | `program`, `program-<operator>`; an operator ending in eight hex reads as a seat's hp and is no cabinet | `board.CABINET` | frozen |
| board `waiting-on` value | — | `operator`, `unit <name>`, `external <ref>` | `board.WAITING` | frozen |
| board cross-row | `d-work/board/_cos.md` \| `_cos-<operator>.md`, one per cabinet | `holder`, `queue`, `seats`, `next`, `since`, `question`, `promised`, `release-plan`, `audit-due`, `recommended`, `read`, `writer`; `release-plan` the backlog grooming play-book's (#625); `audit-due` the audit's due conditions by the audit trigger, counted in the Coming part (#691); `recommended` the home's inferred items for the Recommended part (#695); `read` the home's grooming readings, one line per row, its id, date, outcome and ground (#697); `queue` derived at read from #572 (K4) and `seats` a seat-era name | `board.COS_FIELDS` | frozen |
| plan `parts:` line | `d-work/plans/<id>.md` | `parts: <unit>: <part>; …`, matched by unit name or function | `automaton.PARTS` | frozen |
| inbox message | `d-work/inbox/<unit>/<stamp>-<from>-<n>.md` | `from`, `to`, `row`, `kind`, `sent`, `body`, `writer` | `inbox.FIELDS` | frozen |
| inbox marker | the message's name + `.read` | `read`, `reader`, `writer` | `inbox.MARK_FIELDS` | frozen |
| presence | `d-work/sessions/<id>.md` | `session`, `seen`, `root`, `rows`, `files`; optional `writer`, `host`, `holder` | `sessions.FIELDS` | frozen |
| provenance | `d-work/provenance/<id>.md` | title `# Provenance #<id>`; entries `## <n> <kind> <date>[ <note>]`, kind `prompt` or `disposition`, fenced body; the date UTC from dyad-operator 1.0.0 on, earlier entries as written (#592) | `provenance.FIELDS` | frozen |
| plan file | `d-work/plans/<id>.md` | `Base commit of main:` and `Files touched` as the guards read them | `plans.FIELDS`, `dyadlib.PLAN_PARTS` | frozen |
| trace | `d-work/traces/<id>.md` | sections `Timeline`, `Buckets`, `Counts`, `Bottleneck`, `Limits`; a stored trace is never a preview (#592) | `trace.SECTIONS` | frozen |
| trace preview legacy | `traces_preview_legacy.local.txt` | `<id>` per line, `#` a comment: the stored previews before #592 | `trace.check_store` | frozen |
| provenance legacy | `provenance_legacy.local.txt` | `<id> <n> <reason>` per line: the rows that predate provenance enforcement and the dispositions each holds without words (Rule-7 Enforcement) | `provenance.LEGACY` | frozen |
| public remotes | `public_remotes.local.txt` | one remote per line, compared after `normalize_remote`: the remotes the private-citation fence reads pushes to (#518) | `privatecite.PUBLIC` | frozen |
| private repos | `private_repos.local.txt` | one sha256 hex of a lowercased `owner/repo` per line: the repositories whose quoted text never leaves for a public remote (#518) | `privatecite.PRIVATE` | frozen |
| event | `<runbooks>/events/<instance>.jsonl`, a craft run-book's `<craft>-<name>.jsonl` (#640) | `id`, `ts`, `role`, `instance`, `name`, `cmd`, `class`, `scope`, `exit`, `duration_ms`, `postcondition`, `output_sha256`, `output_tail`, `commit`, `runbook_sha256` | `runbook.EVENT_FIELDS` | frozen |
| run-book command header | `<runbooks>/<instance>.md` | `name`, `class`, `role`, `undo`, `postcondition`, `scope` | `runbook.FIELDS` | frozen |
| evidence block | stdout of `check --evidence` | `head=`, `tree=`, `dirty=`, `code=`, `counts:`, `baseline:`, `stored:`, `evidence-sha256=` | `package.py` | frozen |

## S3 Preference keys

These are the keys a core Rule reads (the `read by` column of `preferences-corpus/PREFERENCES.md`). Their values are
the operator's. The key names and allowed values are the surface.

| key | status |
|---|---|
| merge-disposition | frozen |
| import-licenses | frozen |
| import-support | frozen |
| delegation | frozen |
| delegation-posture | frozen |
| delegation-posture-unattended | frozen |
| cli-pattern | frozen |
| batch-disposition-mode | frozen |
| ledger-pr-merge | frozen |
| concise-mode | frozen |
| host-path | frozen |
| host-zone | frozen |
| dwork-trace | frozen |
| accretion | frozen |
| organization | frozen |
| paired-units | frozen |
| attendance-window | frozen |
| relay-form | frozen |
| intent-reading | frozen |
| dwork-slug | frozen |
| awaiting-you | frozen |
| coming | frozen |
| recommended-next | frozen |
| hygiene-stale-days | frozen |
| hygiene-similar | frozen |
| hygiene-top | frozen |
| inflight-unread-hours | frozen |
| inflight-planned-quiet-days | frozen |
| inflight-unplanned-hours | frozen |
| inflight-pr-still-days | frozen |
| inflight-promise-days | frozen |
| inflight-question-hours | frozen |
| inflight-done-ready-hours | frozen |
| sweep-landing-hours | frozen |
| sweep-board-stale-days | frozen |
| sweep-ci-hours | frozen |
| promotion-ceiling | frozen |
| promotion-adjacency-min | frozen |
| hardening-mandate | frozen |
| hardening-ceiling | frozen |

## S4 Rules

| rule | file | headings | status |
|---|---|---|---|
| 1 | `RULE-1-containment.md` | Boundaries; Conditions; Provenance | frozen |
| 2 | `RULE-2-no-self-ratify.md` | Boundaries; Conditions; Ratification events; Not ratification; Binding of approval; Enforcement; Provenance | frozen |
| 3 | `RULE-3-d-work.md` | Boundaries; Conditions; Scope; Answer grammar; What a `Y` binds; Plan; Completion counter-prompt; Batch disposition; Ledger; Mechanisms; Intake; Incidents; Ratification events; Provenance | frozen |
| 4 | `RULE-4-integrity.md` | Boundaries; Conditions; Criteria; Mechanisms; Provenance | frozen |
| 5 | `RULE-5-coherence.md` | Boundaries; Conditions; Definitions; Sets; Enforcement; Provenance | frozen |
| 6 | `RULE-6-vocabulary.md` | Boundaries; Conditions; Master record; Mechanisms; Provenance | frozen |
| 7 | `RULE-7-provenance.md` | Boundaries; Conditions; Properties; Enforcement; Provenance | frozen |
| 8 | `RULE-8-host-mutation.md` | Boundaries; Conditions; Classes; Conduct; Ratification events; Enforcement; Provenance | frozen |
| 9 | `RULE-9-falsification.md` | Boundaries; Conditions; Form; Enforcement; Provenance | frozen |
| 10 | `RULE-10-proposal-framing.md` | Boundaries; Conditions; Form; Enforcement; Provenance | frozen |
| 11 | `RULE-11-distribution-structure.md` | Boundaries; Conditions; Properties; Ratification events; Enforcement; Provenance | frozen |
| 12 | `RULE-12-verifiable-code.md` | Boundaries; Conditions; Properties; Enforcement; Provenance | frozen |
| 13 | `RULE-13-reuse-over-inference.md` | Boundaries; Conditions; Properties; Enforcement; Provenance | frozen |
| 14 | `RULE-14-system-infrastructure.md` | Boundaries; Conditions; Properties; Enforcement; Provenance | frozen |
| 15 | `RULE-15-d-work-phases.md` | Boundaries; Conditions; Phases; Enforcement; Provenance | frozen |
| 16 | `RULE-16-concurrent-sessions.md` | Boundaries; Conditions; Store; Presence; Enforcement; Provenance | frozen |
| 18 | `RULE-18-ops-scripts.md` | Boundaries; Conditions; Properties; Conduct; Enforcement; Provenance | frozen |
| 19 | `RULE-19-server-instances.md` | Boundaries; Conditions; Properties; Enforcement; Provenance | frozen |
| 20 | `RULE-20-referential-integrity.md` | Boundaries; Conditions; Properties; Enforcement; Provenance | frozen |
| 17 | — | retired; the number is never reused | frozen |

## S5 DMC ids

Every `@id` is `urn:dyad:dmc:dyad-operator/<name>`; `context.jsonld` is the shared context and carries none.

| name | status |
|---|---|
| agent-vs-tended-rule | frozen |
| altitude | frozen |
| amend-scope | frozen |
| answer-grammar | frozen |
| attack-result | frozen |
| attendance-check | frozen |
| attendance-mode | frozen |
| attendance | frozen |
| audit-fences | frozen |
| audit-trigger | frozen |
| audit-watermark | frozen |
| backlog-hygiene | frozen |
| backlog-staleness | frozen |
| batch-engagement | frozen |
| blocker-home | frozen |
| board-lines | frozen |
| bundle-row | frozen |
| bundled-craft | frozen |
| check-kind | frozen |
| check-trigger | frozen |
| ci-red-vs-absent | frozen |
| codify-candidate | frozen |
| containment-mode | frozen |
| countersign-basis | frozen |
| countersign-mode | frozen |
| craft-instantiation | frozen |
| craft-source | frozen |
| craft-trigger | frozen |
| credential-shape | frozen |
| deployed-done | frozen |
| derivation-d3-text | frozen |
| derivation-d3 | frozen |
| derivation-d7 | frozen |
| derivation-d8 | frozen |
| diag-finding-route | frozen |
| diag-level | frozen |
| diag-levels-file | frozen |
| diag-result | frozen |
| direct-commit-class | frozen |
| disposition-budget | frozen |
| disposition-request | frozen |
| done-order | frozen |
| dwork-input-kind | frozen |
| dwork-state | frozen |
| escalate-edge-test | frozen |
| evidence-fold | frozen |
| failure-mode-primary | frozen |
| groom-trigger | frozen |
| hardening-due | frozen |
| hardening-survey | frozen |
| hardening-work | frozen |
| held-pr | frozen |
| hook-failure | frozen |
| host-action-class | frozen |
| incident-record-home | frozen |
| incident | frozen |
| initiation-severity | frozen |
| install-refusal | frozen |
| intake-shape | frozen |
| intake-split | frozen |
| intent-reading | frozen |
| judgement-cause | frozen |
| judgement-complexity | frozen |
| label-case | frozen |
| mandate-accretable | frozen |
| manifest-token | frozen |
| merge-question | frozen |
| message-kind | frozen |
| message-route | frozen |
| message-overhead | frozen |
| mitigation-status | frozen |
| mode-edge | frozen |
| mode-exit | frozen |
| ops-outcome | frozen |
| ops-script-needed | frozen |
| parent-askable | frozen |
| party-kind | frozen |
| plan-departure | frozen |
| plan-gate | frozen |
| port-diff | frozen |
| port-direction | frozen |
| port-row | frozen |
| precedent-admission | frozen |
| precedent-scope | frozen |
| preference-kind | frozen |
| prepush-judgeable | frozen |
| promotion | frozen |
| provenance-entry | frozen |
| provenance-legacy | frozen |
| ratification-event | frozen |
| re-present | frozen |
| read-only-answer | frozen |
| recommended-next | frozen |
| recurrence | frozen |
| reference-severity | frozen |
| reference-vs-prose | frozen |
| release-batch | frozen |
| release-break | frozen |
| release-class | frozen |
| release-number | frozen |
| release-plan | frozen |
| release-reply | frozen |
| release-timing | frozen |
| replan | frozen |
| report-level | frozen |
| retirement-candidate | frozen |
| retirement-sweep | frozen |
| rule-block | frozen |
| rule-pair-coherence | frozen |
| rule-set | frozen |
| session-overlap | frozen |
| session-reconcile | frozen |
| suite-or-guards | frozen |
| sweep-findings | frozen |
| tag-drift | frozen |
| tended-conflict | frozen |
| term-home | frozen |
| trace-agent-side | frozen |
| trace-anchor | frozen |
| trace-bottleneck | frozen |
| trace-bucket | frozen |
| trace-gate-kind | frozen |
| trace-in-evidence | frozen |
| trace-window | frozen |
| transaction-containment | frozen |
| work-in-flight | frozen |
| y-binding | frozen |
| zone-classification | frozen |
| zone-set | frozen |

## S6 Environment and repository variables

| name | kind | status |
|---|---|---|
| `DYAD_INSTANCE` | environment | frozen |
| `DYAD_SESSION` | environment | frozen |
| `DYAD_RUNBOOKS` | environment | frozen |
| `DYAD_OPS` | environment | frozen |
| `DYAD_HOST` | environment | frozen |
| `DYAD_HOST_ZONE` | environment | frozen |
| `DYAD_ROLE` | environment | frozen |
| `DYAD_HARNESS_DIR` | environment | frozen |
| `DYAD_NO_NESTED_TESTS` | environment, internal to the runner | not surface |
| `DYAD_AUTOMATON` | repository variable | frozen |
| `RELEASE_APPROVAL` | repository variable | frozen |

## S7 Host-side hooks

| item | status |
|---|---|
| `dyad/hooks/pre-commit`, `dyad/hooks/pre-push` (`core.hooksPath dyad/hooks`) | frozen |
| `.github/workflows/dyad-package.yml` | frozen |
| `.github/workflows/dyad-automaton.yml` | frozen |
| `.github/workflows/dyad-release.yml` | frozen |
| `.github/workflows/dyad-sweep.yml` | frozen |
| the host frame's import line `@dyad/CLAUDE.md` | frozen |

## S8 Tag forms

| form | status |
|---|---|
| `dyad-operator-vMAJOR.MINOR.PATCH` (core) | frozen |
| `<craft>-vMAJOR.MINOR.PATCH` (a Tended craft) | frozen |
| `vMAJOR.MINOR.PATCH` (bundle) | frozen |

## S9 Install contracts

What an installed system's own crafts and instance files depend on, beyond the forms above: a change to any of them
is "an install contract changed", breaking under `dyad/playbooks/release.md` (Classes; Major releases after 1.0.0),
so each is listed and pinned like the rest (#612, plan #570 revision 10).

| contract | form | source | status |
|---|---|---|---|
| core library path | `dyad/scripts/`, which every Tended craft guard puts on `sys.path` to import the core's modules | `dyadlib.CORE_LIBRARY`, and the inserts in `crafts/*/guards/*.py` | frozen |
| guard contract | a guard module declares `ENTITY`, `CORPUS`, `FIELDS`, `TRANSACTION`, `check_package`, and `check_transaction` when `TRANSACTION`; a craft guard's `CORPUS` is a zone name (`crafts/sysarch/rules/guards.md`) | `dyadlib.CONTRACT`, `dyadlib.contract_problem` | frozen |
| craft registry row | `crafts/REGISTRY.md`, one row per installed craft: `craft`, `version`, `source`, `sha256`, `d-work` (Rule-11 property 2) | `craft.REGISTRY_FIELDS` | frozen |
| craft manifest | `crafts/<craft>/MANIFEST.md` `key: value` lines; `requires: <craft>>=<semver> …` and `seeds: <template>-><dest> …`, a leading `<host>` in a destination the host path (Rule-11 property 2) | `crafts.FIELDS`, `crafts.requires`, `crafts.seeds` | frozen |
| bundled-craft declaration | `BUNDLED_WITH_CORE = True` in one of the craft's own guard modules, and `PURPOSE = "<one line>"` beside it when no core Rule cites the craft, both read as text (Rule-11 property 2) | `bundle.DECLARED`, `bundle.PURPOSE_LINE` | frozen |
| instance manifest contribution | `<host-path>/INFRASTRUCTURE.md`, rows of seven cells: `component`, `partition` (`kernel`, `library`, `The World`), `version`, `purpose`, `license`, `replacement`, `profile` (`authoring`, `operating`, `both`) (Rule-14 property 1) | `manifest.FIELDS`, `manifest.PARTITIONS`, `manifest.PROFILES` | frozen |
| Tended craft layout | `crafts/<craft>/` is a craft when it holds `VERSION`; the runner discovers `guards/` and `tests/` under it, and `vocabulary/CRAFT.md` is its vocabulary (Rule-11 property 1, Rule-6) | `dyadlib.CRAFT_LAYOUT`, read by `dyadlib.craft_dirs`, `dyadlib.guard_files`, `package.test_suites` and `vocabulary.check_craft` | frozen |

The three instance `*.local.txt` lists are in S2 beside `traces_preview_legacy.local.txt`.
