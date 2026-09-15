# Idempotence (syseng craft, Tended rule)

Read by Rule-11's kernel (`dyad/rules/RULE-11-distribution-structure.md`, the p5 stub: build and
install are subcommands, tested in CI) and by the sysadmin craft's `crafts/sysadmin/rules/ops-scripts.md`
(which keeps what an ops script is *for* and cites this rule for the mechanics of properties 3, 6
and 7, moved here by d-work #162 from the block #155 marked) and `server-instances.md` (the
run-book runner's "already satisfied" pre-test, a second instance of the same form). Term
(`idempotent`): `../vocabulary/CRAFT.md`. Guards: the shape of an ops script is the sysadmin
guard's (`crafts/sysadmin/guards/ops_scripts.py`); the install's idempotence is `test_package`'s
(`installed … 0 changes`).

## Properties
1. **Scripted, idempotent, tested install.** *"Build and install are `package.py` subcommands;
   installing twice is a no-op; CI builds the package at HEAD, installs it into a scratch repo, and
   runs the guards there (`dyad-package.yml`)."* (Rule-11 p5 as cut; one code path,
   `dyad/scripts/distribute.py`, for the core and every Tended craft.)
2. **A script converges.** Run any number of times, a script converges to one host state and
   exits 0 once it holds. (a) Every mutating command is guarded by its own state check
   (create-if-absent, set-if-different: `test || cmd`) or is naturally idempotent (`chown`,
   `chmod`, `chattr`). (b) A header line `# postcondition:` states the end state in words and a
   `postcondition()` function tests it. The body runs `postcondition && { echo "already
   satisfied"; exit 0; }` before any mutation and asserts `postcondition` last, exiting 1
   otherwise; the verification block is that function. (c) A partial failure leaves a state a
   re-run continues from: each guard skips what is done, so the same file is re-run — never a
   second script. (d) `set -euo pipefail` stays; it orders, it does not skip — the guards do.
   (ops-scripts.md p6 as moved.)
3. **Provenance printed first.** A script prints `git rev-parse --short HEAD` and its own
   `sha256sum` first, then each command under `set -x`, then a verification block whose commands
   are read-only and re-runnable. (ops-scripts.md p3 as moved.)
4. **Destructive steps confirmed at run time.** (a) A header line `# destructive:` — `none`, or
   each destructive command in words, one clause each. (b) When not `none`, the script defines
   `confirm()` — prints the step, its consequence and its undo (or "no undo"), then
   `read -r -p "... Y/N: " ans < /dev/tty; [[ $ans == Y ]] || { echo "declined"; exit 2; }` — and
   calls it immediately before each destructive command. A declined step never runs and no later
   step runs (exit 2; `set -e` is not involved). (c) With property 2, a guarded destructive command
   asks only when its guard says it would act (`guard || { confirm "..."; cmd; }`), so an "already
   satisfied" re-run asks nothing. (d) Fail closed without a terminal: `[[ -t 0 ]] || { echo "no
   tty"; exit 2; }` before the first destructive step. (e) Exit codes: 0 done or already
   satisfied; 2 declined or no tty; 1 failed postcondition. (ops-scripts.md p7 (a), (b), (d), (e),
   (f) as moved; (c) — the chat authorization the run-time confirmation adds to — stays the
   sysadmin rule's, it binds the process.)
5. **The runner's form is the same form.** A run-book command's postcondition is tested before
   (already satisfied: exit 0, nothing runs) and after (failed: exit 1); a destructive command is
   confirmed on the terminal (exit 2 without one) — `dyad/scripts/runbook.py`, the sysadmin
   `server-instances.md` p9.

## Inference, stated
The ops-script guard verifies the contract's *shape* (shebang, headers, `postcondition()` present
and named three times, `confirm()` when destructive); that a script converges is inference, tested
by the Operator's re-run ("already satisfied").
