# Falsification record — sysadmin craft rule `ops-scripts.md` (d-work #155)

**Claim:** Rule-18's seven properties are the *form* of an ops script — craft practice — and the
kernel keeps only delivery (one file, never inline, hash compared, exit codes as evidence).

Attacks carried from the core record (`dyad/falsification/rules/rule-18-ops-scripts.md`), by id:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 18.2 | The Operator may edit the file before running it; the record lies. | Survives, scoped | The script prints its commit and sha256 first (property 3, here); the comparison and the incident are the kernel's Conduct. |
| 18.7 | Idempotence is unverifiable mechanically; the check is theatre. | Survives, scoped | The guard (`guards/ops_scripts.py`) verifies the contract's shape (property 5, here); convergence is the Operator's re-run. |
| 18.11 | A postcondition that passes before the script mutates masks a wrong postcondition. | Survives, scoped | Property 6 form here; the final assert; the token count over non-comment lines (guard test `test_postcondition_in_comments_not_counted`). |
| 18.13 | A script piped through `tee` cannot prompt. | Refuted | `read … < /dev/tty` (property 7b, here); (e) fails closed without a terminal. |
| 18.15 | Declined mid-script leaves partial state. | Refuted | Declined steps are skipped (property 7); re-run continues from the guards (property 6). |
| 155.3 | A moved sentence binds the Agent's process. | Confirmed for 3 sentences, kept in the kernel | Kept core (Rule-18 Conduct): "never an inline block", "a mismatch is an incident", "exit codes are completion evidence". Moved here: file name, header, body, provenance, check, idempotence and confirmation mechanics. |
| 155.A | #161/#162 assign the mechanics (properties 3, 6, 7) to `crafts/syseng/`; moving them here first is a second move. | Survives, scoped | Moved whole with a marked block naming #162; #162 edits this file by a craft-zone PR and nothing in #155 waits on it. |
| 162.1 | After the cut, a reader of this rule alone cannot write a conforming script. | Survives, scoped | Properties 6 and 7 keep one sentence each naming the header line and the function; the form is one path away (`crafts/syseng/rules/idempotence.md` p2–p4) and the skeleton `templates/ops-script.sh` carries it whole. `dyad craft check` warns when the syseng craft is absent only through `requires:`, which this craft does not declare (the guard checks shape, not the citation). |

## Amendment — d-work #162 (2026-09-14, syseng extraction R-craft-4)
The mechanics block (property 3's body form; 6 (a)–(d); 7 (a), (b), (d), (e), (f)) moved to `crafts/syseng/rules/idempotence.md`;
this rule keeps properties 1, 2, 4, 5 and the process sentences of 6 and 7 (`# postcondition:` names the end state; the gate adds
to Rule-8's chat `Y`). The guard `ops_scripts.py` is unchanged (it checks shape). Disposition: see ledger #162.

## Amendment — d-work #141 (2026-09-14, the mode is git's, not the disk's)
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 141.1 | The check "is executable" read `os.access(p, os.X_OK)`, so on a checkout with `core.fileMode=false` (NTFS) it passed a script tracked `100644`. | **Confirmed** (#135: `135-h2/h4/h5` green while tracked non-executable) | `ops_scripts.check_mode` reads git's index (`dyadlib.tracked_mode`) and fails with `tracked mode 100644 (git update-index --chmod=+x)`. |
| 141.2 | A script just written is not in the index, so the new check sees nothing and says nothing. | Refuted | Untracked falls back to the disk bit and adds `warning: <name>: untracked: disk mode used`; the guard's `main` learned the runner's `warning:` convention, so the fallback is visible without being a failure. |
| 141.3 | `DYAD_OPS` may point outside the work tree, where no index holds the scripts. | Survives, scoped | Same fallback: the disk bit, warned. This is also why the ops script's mode stays this guard's and is not a `mode:` line of the syseng naming guard (one owner). |

Disposition: see ledger #141.

Disposition: see ledger #155.
