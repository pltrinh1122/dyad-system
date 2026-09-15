# Falsification record — syseng craft rule `idempotence.md` (d-work #162)

**Claim:** The install's idempotence and an ops script's convergence and confirmation form are one engineering discipline.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 18.7 | Idempotence is unverifiable mechanically. | Survives, scoped | Unchanged: the sysadmin guard verifies shape; convergence is the Operator's re-run. |
| 18.13 | A script piped through `tee` cannot prompt. | Refuted | `read … < /dev/tty` (property 4b here); fail closed without a terminal (4d). |
| 162.8 | A sysadmin reader loses the form. | Survives, scoped | Each sysadmin property keeps one sentence and the citation; `templates/ops-script.sh` carries the form whole. |
| 162.16 | Property 7 (c) ("the chat `Y` authorizes, the run-time `Y` executes") binds the process and must not move. | **Confirmed** | Kept in the sysadmin rule; only (a), (b), (d), (e), (f) moved. |

Cut from: Rule-11 p5; sysadmin `ops-scripts.md` p3, p6, p7 mechanics (its record, amendment #162).

Disposition: see ledger #162.
