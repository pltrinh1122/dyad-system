# Ops scripts (sysadmin craft, Tended Rule)

Read by Rule-18's kernel (`dyad/rules/RULE-18-ops-scripts.md`): the core Rule binds *that* a command
the Operator runs for the Agent is one committed, executable, checked file whose text and outcome are
provenance; this rule is the *form* of that file. Text moved verbatim from Rule-18 Properties 1–7 by
d-work #155; a Tended Rule — any form, no Rule-4 block, no sweep, no Agent-vocabulary row. Terms
(`ops script`, `postcondition`): `crafts/sysadmin/vocabulary/CRAFT.md`. Skeleton:
`crafts/sysadmin/templates/ops-script.sh`. Guard: `crafts/sysadmin/guards/ops_scripts.py`
(registry label `sysadmin/ops_scripts`; `<ops>` is `DYAD_OPS`, default `workstation-corpus/ops`).

## Properties
1. **One file per change-log row.** `<ops>/<d-work>-<hN>-<slug>.sh` (instance,
   workstation zone), tracked mode `100755` — the mode git records, which is what a clone and a
   checkout reproduce — first line `#!/usr/bin/env bash`, then `set -euo pipefail`.
2. **Header.** Comment lines `# d-work:`, `# class:` (Rule-8 class), `# undo:`, `# change-log:`
   (the row it fills). An undo of more than one command is a sibling `<same>-undo.sh`; a
   one-command undo stays in the header line.
3. **Body.** The form of the body — provenance printed first, each command under `set -x`, the
   read-only verification block — is the syseng craft's `crafts/syseng/rules/idempotence.md`
   (property 3); the Agent re-runs that block as the outcome's check.
4. **Provenance.** The change-log `action` cell cites the script path and the commit that
   introduced it; the Operator runs it as
   `bash <script> 2>&1 | tee <script-with-.log>` and pastes the output; the Agent records the
   outcome as observed. `ops/*.log` is generated (`package_rules.txt`), never tracked.
5. **Check.** `ops_scripts.py` fails when any `ops/*.sh` fails `bash -n`, is tracked at a mode other
   than `100755` (git's index, never the bit on disk: `core.fileMode=false` hides a `100644` behind a
   755 on disk, #135/#141; a script not yet in the index falls back to the disk bit and warns), lacks the shebang, `set -euo pipefail`, or a header line (including `# postcondition:` and `# destructive:`),
   defines no `postcondition()` function, names the token `postcondition` fewer than three times
   (definition, pre-check, final assert), or — when `# destructive:` is not `none` — defines no
   `confirm()` function or names the token `confirm` fewer than twice in code (definition, one
   call). Whether a call precedes the right command is inference. A missing `ops/` directory passes.
6. **Idempotent.** Run any number of times, the script converges to one host state and exits 0
   once it holds; a header line `# postcondition:` states the end state in words and a
   `postcondition()` function tests it (vocabulary). The form — guarded mutations, the
   "already satisfied" pre-test, the final assert, a re-run that continues — is the syseng
   craft's `crafts/syseng/rules/idempotence.md` (property 2). The check (property 5) verifies the
   contract's shape only; that the script converges is inference, tested by the Operator's
   re-run ("already satisfied").
7. **Destructive steps confirmed at run time.** A header line `# destructive:` — `none`, or each
   destructive command (Rule-8 class) in words — and, when not `none`, a `confirm()` gate before
   each such command, in the form of `crafts/syseng/rules/idempotence.md` (property 4: the prompt
   on `/dev/tty`, declined exits 2, fail closed without a terminal, exit codes 0/1/2). The gate
   adds to, never replaces, Rule-8's chat counter-prompt: the chat `Y` authorizes, the run-time
   `Y` executes.

Mechanics moved: the block #155 marked ("to `crafts/syseng/rules/…` on #162") — the body form of
property 3, the guarded-mutation form of property 6 (a)–(d) and the confirmation form of property
7 (a), (b), (d), (e), (f) — is `crafts/syseng/rules/idempotence.md` since d-work #162 (record:
`../falsification/rules/ops-scripts.md`, attack 155.A). This rule keeps what an ops script is *for*
(properties 1, 2, 4, 5) and the two sentences of 6 and 7 that bind the process.

## Provenance
Rule-18 Properties 1–7, moved by #155 (plan `agent-corpus/d-work/plans/155.md`, attack 3); the
mechanics of 3, 6 and 7 moved on to `crafts/syseng/rules/idempotence.md` by #162 (plan
`agent-corpus/d-work/plans/162.md` (a)6). Record: `../falsification/rules/ops-scripts.md`.
