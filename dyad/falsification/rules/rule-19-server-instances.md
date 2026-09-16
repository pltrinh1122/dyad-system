# Falsification record — Rule-19 (server instances), Operator rule 2026-09-14 (ledger #134)

**Claim (operator, 2026-09-14):** once the git server is running it remains running independent
of any Claude chat session; it has a run-book both Agent and Operator can use, documenting
shell commands (CLI preferred) for common operations including health status; every server
instance follows the same rule.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | `restart: unless-stopped` does not survive `docker compose down`: the containers are removed and nothing restarts them. | Confirmed | Persistence is a property of the supervisor, not of the container: `down` is a stop by the operating party and is a run-book `Stop` command with its class and undo (property 3). What the Rule promises is that no *session* ending, harness exit or reboot stops the server (property 1); a deliberate `down` is not that. Restart policy is the supervisor for the Docker case; a systemd unit that runs `compose up` is the named replacement when a stronger guarantee is wanted (open question Q1). |
| 2 | The run-book rots against the compose file: a renamed service, port or data path leaves the run-book wrong and the reader trusts it. | Survives, scoped | Condition 2 binds the run-book to the same PR as any compose/unit/image change; condition 3 makes every use a test and every failure a correction PR. The proposed `check_rule_19` catches structure (headings, restart policy), never content; content rot stays inference, stated in Enforcement. |
| 3 | Health via HTTP (`curl /api/healthz`) and health via `docker inspect .State.Health` can disagree: the container may be healthy while the port is bound to the wrong interface, or the reverse. | Survives, scoped | Property 4 requires one health command with one pass criterion and prefers reading the shipped healthcheck. The git server's run-book should carry both reads under `Status/health` (container health and an HTTP probe from the host), each with its criterion; which is *the* pass criterion for Done is the plan's to name (Q2). |
| 4 | "Servers stay running" is a statement about the host's desired state: a Tended Rule, not an Agent Rule (Rule-4 guard). | Refuted, in part | The Rule binds what the Agent must deliver and when a d-work may close: name a supervisor in the plan, leave a run-book, cite a passing health command before Done. Those bind the Agent's process — Agent Rule by the Rule-4 guard. What *is* Tended: host-specific constraints (which interface to bind, where data lives, which services may run privileged). Rule-19 Boundaries send those to `workstation-corpus/rules/`; a Tended Rule may add, never remove, properties 1–6. |
| 5 | The run-book should be package: another install wants the same git server. | Refuted | The run-book carries host values (`/srv/git`, `git.lan`, container names) and `package.py check` refuses host-specific strings in the package (Rule-11 p1). The server itself was moved to instance by #124 for the same reason. A run-book *template* under `dyad/templates/` is possible later; the location is resolved through `DYAD_RUNBOOKS` so an install with another layout needs no Rule edit. |
| 6 | Overlap with Rule-8: the change log already records every start/stop; a run-book duplicates it. | Refuted | The change log is a history of actions taken (one row per event); the run-book is a reference of commands available (one file per instance). Rule-8 keeps class, authorization and the row; Rule-19 names the reference and cites Rule-8 for every state-changing command (property 3). One-way: Rule-8 gains a Boundaries pointer, nothing else. |
| 7 | Overlap with Rule-18: a run-book command the Operator runs is an Operator-executed command and must be an ops script. | Survives, scoped | Rule-18 governs commands the Agent *asks* the Operator to run for a planned action. A run-book command is reference the reader runs by choice; when a plan names a run-book command as an H-row for the Operator, Rule-18 applies and the run-book cites the ops script (Boundaries). Rule-18 is not edited. |
| 8 | A vLLM container already runs on the host (port 8000, privileged, per the audit). The Rule as worded ("all server instances") pulls it in with no d-work, no run-book, and a breach on day one. | Survives, scoped | Property 6 scopes the Rule to services the Agent deploys or is asked to operate; a pre-existing service enters when a d-work touches it, through that d-work's plan. Whether the Operator wants vLLM brought under the Rule now is Q3. |
| 9 | Property 5 ("not Done until health passes") lets a flaky healthcheck block a d-work whose intent was delivered. | Survives, scoped | The Done-`Y` is the Operator's (Rule-3); a failing health command is reported as evidence and the Operator may still dispose. The property states what the completion reply must carry, not that the Agent withholds the counter-prompt. Worded so in property 5 ("cites … the observed output"). |
| 10 | `sudo`-free is impossible for a service owning `/srv/git` (mode 750, uid 1000) or a systemd unit. | Refuted | The operator's uid owns `/srv/git`; docker commands run through the docker group; only the subvolume creation and a system unit need `sudo`, and property 3 says a command may need it if it says so. "Wherever the host permits" is the scope. |
| 11 | A run-book with ten mandatory sections for a single container is ceremony. | Survives, scoped | Ten sections is what the prompt asks (common operations incl. health) plus what recovery needs (backup, restore, data). Each may be one line ("Upgrade: see `server/README.md` Upgrade"); the check proposed counts headings, not length. |
| 12 | The persistence property is unverifiable from inside a session: the Agent cannot end its own session and look. | Survives, scoped | Verified structurally (restart policy in the compose file; `docker inspect --format '{{.HostConfig.RestartPolicy.Name}}'`) and by the Operator across a reboot; recorded as observed in the run-book's `Status/health`. Stated as inference in Enforcement until `check_rule_19`. |

No mechanical check in this d-work: the prompt asks for a Rule and a run-book discipline; the
guard is proposed for a later d-work so this PR stays agent-zone (Rule-1) and the check can be
falsified against a real run-book (the git server's, #121/#135).

## Rule-5 pairwise statements (Rule-19 added; Rule-8 gains one Boundaries bullet)
- 19–1: run-books are workstation-zone paths (`ZONES` already claims `workstation-corpus/`);
  this PR is agent zone only. 19–2: no ratification event; Done-`Y` stays Rule-3's; property 5
  adds evidence, not a question. 19–3: property 5 is one item of completion evidence; conditions
  1 and 4 hang on the plan and the completion reply; nothing about lifecycle moves. 19–4: block
  conforms (intent 1, target 1, boundaries 5, conditions 4). 19–5: this statement. 19–6: four
  terms — `server instance`, `supervisor`, `run-book`, `health command` — owner 19; `server
  instance` and `run-book` used by 8 19, the rest by 19. 19–8: Rule-8 owns class, authorization
  and the change-log row for every start/stop/upgrade; Rule-19 owns what a deployment leaves
  behind (supervisor, run-book, health) and cites Rule-8 for each state-changing command; one
  Boundaries pointer added to Rule-8, one-way. 19–9: this record. 19–10: framing as in the plan.
  19–11: run-book is instance; `DYAD_RUNBOOKS` follows property 3; no package path added; a
  later `check_rule_19` registers in the runner (S4). 19–12: no code enters the package in this
  d-work; the check is named and deferred with its scope. 19–13: no import; a systemd or compose
  supervisor is a World/library concern declared under 14. 19–14: Docker, compose and Gitea are
  library rows already; systemd, if chosen, is The World observed; no new token in the package.
  19–15: the plan names supervisor and run-book path; no phase change. 19–16: no row-store
  change. 19–17: no surface. 19–18: Rule-18 owns delivery of Operator-run actions; a run-book
  command is reference, an ops script is delivery; the run-book cites, never replaces; Rule-18
  not edited. Coherent, orthogonal.

Disposition: see ledger #134.

## #152 amendment (2026-09-14): preference `cli-pattern`
| # | attack | result | survivor |
|---|---|---|---|
| A | The entrypoint is a host-side install artifact (Rule-11 p2 clash). | Refuted | It lives under the package root and is invoked by path; nothing is written to PATH. |
| B | A wrapper that prints the native line is still a second way to run a command. | Survives, scoped | The printed line is the native one; the wrapper adds telemetry (Rule-19, #150) and nothing else. |
Pairwise: Rule-19 gains one sentence reading a preference value; no other Rule's concern moves (Rule-11 owns the entrypoint's placement, Rule-19 the run-book command's form, the preference the value). Coherent and orthogonal with every other Rule as before.


## Amendment — d-work #150: telemetry, one execution path, contained mutation (properties 7–9)

**Claim (operator, 2026-09-14, plan #150):** every run-book command has telemetry an audit can review
conveniently; every run-book command reduces the error between Operator and Agent execution; every
run-book command mutation is contained. Mechanism: `dyad/scripts/runbook.py` (parser, `check_rule_19`,
runner, events store), `project_events.py`, `main_fence.py` events rule, two Rule-20 kinds.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Telemetry belongs on the host (syslog/journal), not in the corpus. | Refuted | The audit reads the corpus (Rule-9 records, Rule-3 incidents, Rule-8 change log); host logs are World and vanish with the machine. Volume is small (a few events a day) and append-only. Property 7. |
| 2 | Events are generated files (Rule-11 property 6) and must not be committed. | Refuted | A generated file is reproducible from the tree by running the package; an event is not — it records something that happened once. Same class as a change-log row, whose pasting the Operator wants replaced. `package_rules.txt` unchanged; the `name: .jsonl` entry keeps event stores out of the package, not out of the instance. |
| 3 | Committing events from the agent role is a self-report (Rule-2). | Survives, scoped | An event is evidence of an execution the plan-Y authorized, not a ratification; the Operator's own runs produce operator-role events in the same store. A lying Agent could forge one — stated, as for `check --evidence` (#138); `main_fence` keeps the store append-only so a forged line cannot replace a true one. |
| 4 | Two execution paths already exist (ops scripts, run-book prose); a runner is a third. | Refuted | The runner is the only path for recurring operations; ops scripts stay for one-off d-work actions and share the header vocabulary (Rule-18 Boundaries bullet); prose commands are removed from run-books by `check_rule_19` (a bare shell block fails). Property 8. |
| 5 | Role gating by keyword (`sudo`) is inference. | Survives, scoped | The check is mechanical over `runbook.CREDENTIAL_WORDS`; a command that hides `sudo` behind a script is caught only when the runner sees a permission error — recorded as an event with exit ≠ 0, the audit signal. The reverse false positive is real and accepted: `merge-gate-status` carries Gitea's header word `token` and is role operator although the agent's own token is read; the run-book says so beside it. |
| 6 | "Contained" cannot be verified: a command may touch anything. | Survives, scoped | Scope is declared and recorded in the event; the runner verifies the postcondition only. The plan's "container set unchanged" check for compose commands is not implemented (it would need the runner to know Docker, a World dependency the package must not take — Rule-14); stated in property 9. Full sandboxing is out of scope. |
| 7 | Rule-18 and Rule-19 now overlap on header form. | Refuted | One vocabulary (class, undo, postcondition, destructive confirmation) owned by Rule-18; Rule-19 cites it and adds role, scope, event (property 8, last sentence; Rule-18 Boundaries). Ownership: Rule-18 the form, Rule-19 the run-book's use of it (S4 pattern). |
| 8 | Operators will not type `package.py runbook run git-server status` when `docker ps` is shorter. | Survives, scoped | The block still shows the native line and the runner prints it before running (Operator design note, #150; a short entrypoint is #152). The runner is what makes it an event; adoption is conduct. |
| 9 | A pre-tested postcondition makes `restart` a no-op on a healthy server. | Confirmed | The postcondition must be false before and true after: `restart` tests "started within the last 60 s", `backup-dump` "today's dump exists", `restore-snapshot` "the live subvolume's parent is the snapshot". A postcondition that already holds is the idempotence contract (Rule-18 property 6), not a bug; the run-book chooses postconditions accordingly and the check cannot judge them (inference, Enforcement). |
| 10 | The check reads `workstation-corpus/` from the package, which Rule-19's Enforcement said no guard does. | Refuted | Through `DYAD_RUNBOOKS` (property 2, Rule-11 property 3 manner), never a literal instance path in the package; a missing directory passes (fresh install, Rule-11 property 5). Rule-18's `ops_scripts.py` set the precedent. |
| 11 | The agent-zone PR's guard fails until the workstation-zone run-book is converted. | Confirmed | Referent first (Rule-1): the workstation PR (converted run-book) merges before the agent PR; the live run-book test skips while a run-book holds no `dyad-cmd` block, and `check_rule_19` fails on prose blocks — the failure is the intended order, reported in the completion reply. |

## Rule-5 pairwise statements (#150: Rule-19 properties 7–9; Rule-8 one Conduct bullet; Rule-18 one Boundaries bullet)
- 19–1: events and run-books are workstation-zone paths; the package changes are agent zone; two PRs.
  19–2: no ratification event; the run-time `Y` of a destructive command executes what a chat
  counter-prompt ratified (Rule-18 Conduct, unchanged); an event is evidence, not a disposition
  (attack 3). 19–3: the runner is a mechanism, not a lifecycle change; a read-only run needs no
  plan item; a reversible or destructive run is a host action of its d-work as before. 19–4: block
  conforms (intent 1, target 1, boundaries 5, conditions 5). 19–5: this statement. 19–6: four terms
  added — `run-book command`, `event`, `role`, `scope` — owner 19, used-by literal; `event` is
  defined as distinct from `ratification event`. 19–8: Rule-8 still owns class, authorization and
  the change-log row; it gains one Conduct bullet saying the event is the row's evidence
  (`event: <id>`); Rule-19 owns the event's shape and store. 19–9: this record. 19–10: framing as
  in the plan. 19–11: `runbook.py`, `project_events.py` and tests enter the package; the run-book
  and events are instance; `package_rules.txt` unchanged (attack 2); Rule-11's runner registers
  `check_rule_19` and `PROJECTORS["events"]` and owns no semantics (S4). 19–12: every script carries
  its test (`test_runbook.py`, `test_project_events.py`; `main_fence`, `refint`, `project_entities`,
  `package` tests extended). 19–13: no import; stdlib only. 19–14: `bash` and `git` are declared
  tokens; the runner invokes nothing else; Docker is invoked by the run-book's lines, from the
  instance, as before. 19–15/16: no phase or row-store change; the events store borrows Rule-16's
  append-only discipline, enforced by Rule-3's fence (`main_fence.py`) with the rule stated in
  Rule-19 property 7. 19–17: one surface (`events`) registered; the entities surface gains
  `run-book command` and `event`. 19–18: Rule-18 owns the header form and ops scripts; Rule-19 owns
  the run-book's use and the runner; one Boundaries bullet in Rule-18 distinguishes recurring
  run-book commands from one-off ops scripts (attack 7). 19–20: two kinds appended to the register
  (`event.command->command`, `changelog.event->event`) with existence resolvers; Rule-20 owns
  resolution, Rule-19 what the references mean. Coherent, orthogonal.

Disposition: see ledger #150.

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
the check half of `runbook.py` is the guard `dyad/guards/workstation/runbooks.py` (the runner imports its parser); the event store's shape and append-only fence are `dyad/guards/workstation/events.py` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
text moved to `crafts/sysadmin/rules/server-instances.md` (#155): Properties 1–4 and 6–9 and the Enforcement check list; the guards to `crafts/sysadmin/guards/runbooks.py` and `events.py` (labels `sysadmin/runbooks`, `sysadmin/events`); a run-book template at `crafts/sysadmin/templates/runbook.md`, seeded by `dyad runbook new`. Kept: a reworded Intent, Target, Boundaries (one added naming the craft rule), Conditions, two properties (run-book and health; deployed means run-book and health — attack 3). Amendment applied during execution (Operator-pending, reported by the main Agent): the runner `dyad/scripts/runbook.py` stays core and now holds the parser and the event store's primitives; the craft guards import and re-export them (the reverse of #151's direction), so `dyad runbook list | run | new` work with no craft and `check` exits 2 when none provides it; plan attack 11 is superseded. Pairwise: 19–8 and 19–18 unchanged; 19–4: block holds (intent 1, target 1, boundaries 6, conditions 5); 19–6: `supervisor`, `run-book`, `health command`, `run-book command`, `event`, `role`, `scope` left for `CRAFT.md`; `server instance` stays (definition trimmed of the craft's terms), used by 8 19; 19–17: the events surface reads the runner's primitives, skipping nothing; 19–20: event kinds resolve through the craft guard, skipping when absent; 19–21: two craft guards on the second root. Coherent, orthogonal.
## Amendment — d-work #165 (2026-09-14, core run-books)
Boundaries bullet 2 gains one sentence: a run-book's section set is declared in its header (`# sections:`), default the craft rule's ten; a core run-book (`dyad/runbooks/`, a play-book's steps) is checked with its own set. The clause's form lives in the craft rule (`crafts/sysadmin/rules/server-instances.md`, property 2); the runner's parser gains `declared_sections`, `core_runbooks`, `all_runbooks` and resolves `dyad runbook list | run <name>` to `dyad/runbooks/<name>.md` when the instance has none (events still under `<runbooks>/events/`). Attack (plan #165, 4): the ten sections would fail a core run-book — confirmed, this mutation. Pairwise: 19–3: the play-book's run-book is Rule-3's evidence, the runner Rule-19's mechanism; 19–4: block holds (boundaries 6, conditions 5); 19–11: `dyad/runbooks/` is package, its events instance; 19–21: the sysadmin guard reads a second root (`dyad/runbooks/`) for the entity it owns; the check stays the craft's. Coherent, orthogonal.

## Amendment — d-work #162 (2026-09-14, clerical: the `Set:` label)
`Set: System Architecture.` → `Set: System Requirements (kernel; content: crafts/sysadmin/rules/server-instances.md).`
— the System Architecture set is the sysarch craft's directory since #160 and Rule-19 is a core kernel whose content
is the sysadmin craft's (#160 finding). No clause changes. Disposition: see ledger #162.
