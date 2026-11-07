# Rule-14: System Infrastructure

**Intent:** Declare every integration dependency of The Dyad System on The World in one
manifest, split into a minimal pinned kernel and a library of replaceable adapters.
**Target:** the System Infrastructure

## Boundaries (out of scope)
- Which library to import and on what criteria — Rule-13.
- Which implementation path to take — Rule-12. Package layout — Rule-11. Zones — Rule-1.
- The Dyad System itself (operator, agent, the core craft, the Tended crafts, the instance):
  Rule-14 governs its surface, not its content.
- The manifest's form — one manifest of seven cells, library rows replaceable and naming their
  replacement, The World observed and never pinned: the sysarch craft's
  `crafts/sysarch/rules/manifest.md`. Rule-14 keeps the kernel and the kernel-only path, the
  sentences Rule-2's Binding relies on (#160).
- How the guard's token and import scan works — interpreters, argv[0], command words, `uses:`
  and `run:`, the stdlib / internal / third-party classification, `import:<module>` tokens: the
  syseng craft's `crafts/syseng/rules/imports.md` property 4 (#162).

## Conditions (triggers)
- A craft file or the agent's workflow invokes anything not in the manifest, or imports a
  Python package not in the manifest.
- A kernel version changes on the host, or a library entry is added, replaced or removed.
- Every push and PR: `dyad/guards/infra/manifest.py` (Rule-14 owns it) runs, registered in
  Rule-11's runner (`package.py check`) and on the kernel-only path (property 3).

## Properties
1. **One manifest.** Every dependency on The World is a row in the manifest at the package
   root (`dyad/infrastructure/INFRASTRUCTURE.md`); its form — component, partition, version,
   purpose, license, replacement, profile — is `crafts/sysarch/rules/manifest.md`. The profile
   cell (`authoring`, `operating` or `both`; a kernel row is `both`) says which activity needs the
   row, and a system's own operating rows are its instance contribution, `INFRASTRUCTURE.md` under
   its host path (Rule-1), joined to the core's and the crafts' rows as one manifest (#175).
2. **Kernel.** Claude Code (or another CLI inferencing agent), Python at a pinned version, Git
   as a local repository, and pydantic at a pinned version — the one third-party package the
   kernel-only path may import directly. Minimal; versions recorded as observed, with the
   minimum the package was last verified on. A hosted git service is never kernel. The kernel is
   one and serves both profiles, because the agent is the proposer of every system; but the
   kernel-only path (property 3) and every run of an automaton need only Python, Git and pydantic,
   so a host that runs only those — the guards and the automaton, with no agent session — runs on
   the kernel without its agent, while the system it serves keeps its agent party elsewhere, or it
   is no dyad system (#593).
3. **Kernel-only path.** Every guard runs on the kernel alone: `package.py check --guards`,
   called by `dyad/hooks/pre-push` before every push (I2). The hook runs it as `check --guards
   --pre-push`, which judges the refs git pushes (read from its stdin) and refuses a push it cannot
   judge: a ref other than the checked-out HEAD, or a working tree with changes; a deletion, or a
   ref already on `origin/main`, carries no new commit and passes (d-work #194). It judges only what git sends: a
   terminal on stdin is refused before any read, a hand run with no ref line fails, and git's own call with no ref
   line — an up-to-date push, or one git rejected locally — passes with one line; a clone missing the core's release
   tag fails before any guard runs, except on a ledger-only or events-only push, which runs no check that reads tags
   and prints one skip line instead (#621), and a shallow clone warns (#592). CI, hosting
   and any runner are library adapters; the package must not depend on them to enforce a Rule.
   The kernel-only path is the merge evidence for every merge: `package.py check --evidence`,
   run by the main agent on the exact head being merged, prints the evidence block (head sha,
   tree hash, working-tree cleanliness, every check and guard result, and a sha256 of those
   lines). The completion reply cites it by that sha256 and by its brief form, as
   `check --evidence --brief` prints it: head, tree and dirty flag; one count line over the whole block; the
   baseline the fold compared against (`origin/main`, or a line saying none was found, in which case nothing
   is folded); for each guard, its warnings already standing on that baseline folded into one line; every
   warning of a kind new since the baseline; and every failing, skipped or other line. The full block, from which the sha256 is computed, is
   stored per checkout and never tracked (`<git common dir>/dyad-evidence/<evidence-sha256>.txt`)
   and shown byte for byte on request (`check --evidence --show <sha256>`), and the operator may
   re-run the evidence on the same head and compare the sha256 (Rule-2, Binding; #476). The block also prints the head's
   code digest (`code=`), the identity of the tree with `<instance>/d-work/` and `<runbooks>/events/` pruned; under
   `--pre-push` the hook skips the suite on a pushed tree whose code equals that of a head an operative `Y done` names
   (Rule-12 property 2; #562), and `check --evidence` itself never skips. **Corroboration** (`dyad check --corroborate`) never replaces the
   block and is never a gate: it runs on `main` after a merge, where the merge ran — in the automaton's own job after
   its push, since a push made with the workflow's token starts no other workflow, or in hosted CI for any other push
   to `main` — once per landed tree (a newer push to `main` cancels the run on the older one), never on a branch push,
   a PR event, or a ledger-only or events-only commit. It runs the guards, the containment range, the fence, the
   build and a scratch install every time, and the suite only when the landed code differs from code an operative
   `Y done`'s evidence passed; the **automaton sweep** (`dyad automaton sweep`) runs after each landed merge, once
   per landed cut, the suite on `main` in the hosting's environment, every whole-store guard and drift, read-only,
   and its `--stores` mode runs the whole-store guards alone after each ledger push, in the automaton's job; each
   posts one notice to the home's inbox only for what is new or failing (#564, #617). The full sweep also runs the
   audit's coded checks, its part `sweep_audit` — the audit watermark and fences, the Rules edited since the newest
   Rule-5 sweep record, incident sizing and the hardening index, the newest audit record's lines, the levels file —
   each a warning, never a failure, its counts `reading:` lines that are never posted; and run with no `--row` it
   lands and posts nothing and prints the **report** — every check line, every finding `standing` or `new`, the
   readings, the stall block, `checks-sha256` over the tree's own check lines and `report-sha256` over the whole text,
   stored per checkout and never tracked — which the audit play-book reads in place of running those checks itself
   (#619). No clock starts it: each check
   follows the activity that can change what it reads. Which activity that is, is the check-trigger criterion
   (`check-trigger`, a decision record of `dyad/dmc/`): a check reads one or more inputs and runs on the union of their triggers — the
   **code tree**, which only a merge changes, after each landed merge; the **ledger stores**, after each ledger push,
   by `--stores`; the **event store**, after each events-only push, by `--stores` too; **absence**, the time since an
   event — heads not landed, a code push not corroborated, a sweep not delivered, a stale board, work in flight,
   backlog hygiene — which
   nothing changes, at the home's read in `dyad board resume` at each operator prompt (Rule-3 Ledger); and the
   **outside world** — the runner image, released assets, a mirror — at the next merge's sweep. The suite is split by
   the same reading: `suite`, the tests that read the code tree, after each landed merge, and `suite:live`, the
   tests that read the stores, in `--stores`. A registry label or sweep part the criterion's table does not class,
   or an input with no delivered trigger, fails a test (#618), and so does a part classed with an input whose
   trigger never calls it (#619). The
   pre-push hook is the only check run before a merge (local CI first, ledger #168). When the hosting is unreachable a ratified merge executes locally — `git merge
   --no-ff` of the branch into `main`, commit message citing the PR and the done-Y — and is
   pushed when the hosting returns; the plan gate and the fence read the local `main`, and
   the completion reply states "evidence at <sha>, hosting unreachable" (#138).
4. **Library and The World.** Everything else the package or the agent's workflow invokes is a
   library row; The World is observed, not pinned (`manifest.md`, properties 2 and 3).

## Enforcement
`dyad/guards/infra/manifest.py` (I5, ledger #102; placed per Rule-11 property 1) runs on every push
and PR, registered in Rule-11's runner. It checks that the manifest is well-formed (seven cells;
partition `kernel`, `library` or `The World`; profile `authoring`, `operating` or `both`, a kernel
row `both`; no component declared twice across core, crafts and instance) and that every invocation and every third-party
Python import the package makes maps, through `dyad/guards/infra/manifest_rules.txt` (beside the
guard), to a declared component — an unmapped one fails, a component with no token warns; the
scan's mechanics are `crafts/syseng/rules/imports.md` property 4 (#117, #162). Rule-11's runner
invokes it; Rule-14 owns its semantics (S4). Whether a row's version, license and replacement are
right stays inference (Rule-13 criteria).

## Provenance
Operator rule, 2026-09-13 (Architecture Rule 4). Falsified; see
`../falsification/rules/rule-14-system-infrastructure.md`. Properties 1 (the six cells), 4 and 5
moved to `crafts/sysarch/rules/manifest.md` 2026-09-14 (#160); the kernel stays here. The token map
and import-scan mechanics of Enforcement moved to `crafts/syseng/rules/imports.md` 2026-09-14 (#162).
Property 1 gains the profile cell and the instance contribution 2026-09-25 (d-work #175): the core
manifest had shipped one system's operating rows to every install; see the same record, amendment #175.
Property 3 gains the pre-push sentence 2026-09-29 (d-work #194): the hook judged `origin/main..HEAD`
and the tree on disk, not the refs git pushes; see the same record, amendment #194. Property 3 cites
the evidence block by its sha256 and its brief form, the full block stored per checkout and shown on request,
2026-10-26 (d-work #476, child C3 of #473); see the same record, amendment #476. Operator and agent are lowercase in prose and done-`Y` replaces Done-`Y`, 2026-11-02
(d-work #553): the dyad-native terms; see `../falsification/rules/rule-6-vocabulary.md`, amendment #553 (part D). Property 3's
evidence block gains the code digest and the hook's skip on a head a `Y done` names 2026-11-03 (d-work #562); see
`../falsification/rules/rule-14-system-infrastructure.md`, amendment #562. Property 3 names corroboration, run where the
merge ran, and the scheduled sweep 2026-11-03 (d-work #564): the automaton's merges had had no corroboration at all, and
every merge of a stack started its own full run on a tree nobody lands on; see the same record, amendment #564. Property 3
names the pre-push outcomes on a terminal, an empty stdin and a missing core tag 2026-11-05 (d-work #606, stating #592);
see `../falsification/rules/rule-3-d-work.md`, amendment #606. Property 2
states what a host running only the automaton needs 2026-11-04 (d-work #593, backlog row #55): the kernel listed a CLI
agent, so such a host had no reading; see the same record, amendment #593. Property 3's
scheduled sweep becomes the automaton sweep 2026-11-06 (d-work #617): run after each landed merge, with a guards-only
`--stores` mode after each ledger push, and no clock, the stall findings moving to the home's read; GitHub delivered
the twice-daily schedule about seven hours late (#609); see the same record, amendment #617. Property 3 names the
check-trigger criterion and its five inputs 2026-11-06 (d-work #618): #617 gave the code and the ledger their triggers,
and the event store, which only events-only pushes change, had none but the next merge; see the same record, amendment
#618. Property 3 gives the full sweep the audit's coded checks and the no-`--row` report, names a sweep not delivered
among the absences, and makes the test fail on a part its inputs' triggers never call 2026-11-06 (d-work #619): the
audit's steps ran checks the automaton could run after every merge, and `sweep_ci` was classed with an input whose
sweep never called it; see the same record, amendment #619. Property 3's missing-tag refusal spares a ledger-only or events-only
push 2026-11-07 (d-work #621): after the v1.0 cut the refusal held every clerical push, the release-ready lines and the
automaton's close included, until a tag that needed those lines existed; see the same record, amendment #621.

Set: System Requirements (kernel; content: crafts/sysarch/rules/manifest.md, crafts/syseng/rules/imports.md).
