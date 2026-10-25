# Falsification record — sysadmin craft rule `server-instances.md` (d-work #155)

**Claim:** the run-book's form (supervisor, sections, commands, health, telemetry, one execution
path, contained mutation) is craft practice; the kernel keeps existence at the instance path and an
observed health pass as completion evidence.

Attacks carried from the core record (`dyad/falsification/rules/rule-19-server-instances.md`), by id:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 19.1 | `restart: unless-stopped` does not survive `docker compose down`. | Confirmed | Persistence is the supervisor's (property 1, here); a deliberate `down` is a run-book `Stop`. |
| 19.4 | "Servers stay running" is a Tended Rule, not an Agent Rule. | Refuted, in part | Exactly the split #155 makes: what the Agent must deliver and when Done may be asked stays in Rule-19's kernel; the host's desired state and the run-book's form are this rule. |
| 19.5 | The run-book should be package: another install wants the same git server. | Refuted, then scoped by #155 | The run-book *instance* carries host values and stays instance; the *template* (`templates/runbook.md`) and the reference deployment (`server/`) are craft. |
| 19.11 | Ten mandatory sections for a single container is ceremony. | Survives, scoped | The guard counts headings, not length; each may be one command. |
| 150.5 | Role gating by keyword (`sudo`) is inference. | Survives, scoped | Mechanical over `runbook.CREDENTIAL_WORDS` (core runner constant; the guard checks it). |
| 150.6 | "Contained" cannot be verified. | Survives, scoped | Scope is declared and recorded (property 9, here); the runner verifies the postcondition only. |
| 155.3 | A moved sentence binds the Agent's process. | Confirmed for 2 sentences, kept in the kernel | Kept core: "not Done until run-book and health" (property 5), "the plan names the supervisor and run-book path" (condition). Borderline, moved with a note: property 8's "the runner refuses `operator` commands under the agent role" binds the runner. |
| 155.4 | The Docker/Gitea image is one implementation, not craft-generic. | Survives, scoped | This rule is implementation-neutral; `server/` is one reference deployment, documented as such; the host value baked into `compose.yaml` (`extra_hosts: git.lan`) is parameterised through `DYAD_DOMAIN`. |
| 155.7 | The template's placeholder `dyad-cmd` blocks fail the guard. | Refuted | The template lives in `templates/`, outside `<runbooks>`; the guard globs `<runbooks>/*.md` only; `dyad runbook new` instantiates it and the check is the guide (core test `test_new_seeds_the_template`). |
| 155.8 | The kernel cannot verify a form it does not own. | Refuted | The kernel binds existence at the instance path and an observed health pass; the form is this rule's, checked by this craft's guards, discovered by the core runner. |
| 155.11 | `dyad runbook` dispatching to craft code inverts S4. | Superseded by the #155 amendment | The runner stays core (parser, store primitives, `list`/`run`/`new`); this craft's guards import its parser; `runbook check` calls the guard and exits 2 when no craft provides one. |

Disposition: see ledger #155.

## Amendment — d-work #438 (2026-10-25, property 7: a read-only command's event only on a change of reading)
**Claim (plan #438, the Operator's `Y` of 2026-10-25):** a `class: read-only` command's event is appended only when
its output's digest differs from the digest of the last event of that command for that instance; a heartbeat that
repeats the last reading is not an event. Every other class appends on every execution; a deploy's health pass
(Rule-19 property 2) is read from the run that observed it and is unaffected.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 438.1 | "Every execution leaves an event" records something that happened; a heartbeat per reply is that. | **Refuted** | On a cloud kernel nearly every reading is identical by construction (every other live seat reads `no harness session`, the seat's own `title differs`, #434): a run whose digest equals the last event's records nothing that happened. A change of reading — a mismatch appearing or clearing — is what happened, and it is still recorded. |
| 438.2 | Change-only is enough on its own; the Rules need no edit (plan #438 alternative c alone). | **Confirmed, partial** | It turns a per-reply stream into a few events a day, but each still needed a row and a PR under the old fence; the core makes an events-only commit clerical (Rule-2, Rule-3 and Rule-12, amendment #438 there). The two stand together. |
| 438.3 | Change-only loses the "last seen healthy" timestamp an every-run store carried. | **Survives, scoped** | The current reading is on the board and in the presence store, computed on demand; a change's event carries its own time, so the store still says since when the reading has held. What is lost is only the repeated confirmation, which no audit grades (#409 G1 grades recurrence of a change). |
| 438.4 | A deploy's health pass (Rule-19 property 2) would be skipped when it repeats an earlier reading. | **Refuted** | The completion evidence cites the health command's observed output from the run that observed it, not the store; and a deploy's commands of other classes append on every execution as before. |
| 438.5 | Comparing digests needs a memory the runner lacks. | **Refuted** | The last event of that command for that instance is in the store the runner appends to (`runbook.py`); the digest is already an event field (`runbook.EVENT_FIELDS`). |

Disposition: see ledger #438.
