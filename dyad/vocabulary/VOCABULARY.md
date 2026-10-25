# Agent vocabulary (master record, Rule-6)

One row per term. The definition here is the only definition; Agent Rules use the term and
cite this file. `owner` is the Rule whose concern the term belongs to; `used by` lists the
Rules that use it (checked by `dyad/guards/agent/vocabulary.py`: owner exists, no orphan, no duplicate).
Terms defined elsewhere (preference keys in `preferences-corpus/`, Tended Rules' terms) are
referenced, never defined, here. Craft terms are defined in `crafts/<craft>/vocabulary/CRAFT.md`
and referenced here by craft name (the sysarch craft's: `projection`, `projector`, `surface`,
`library`, `reference`, `resolver`, `guard contract`, #160; the sysadmin craft's: `read-only`, `reversible`, `destructive`,
`change log`, `undo`, `ops script`, `postcondition`, `supervisor`, `run-book`, `health command`,
`run-book command`, `event`, `role`, `scope`; #155; the cabinet craft's (`crafts/cabinet/`, renamed from `cos` by #417): `charter`, `cos`,
`desk`, `roll-up`, `function`, `topic`, #383). The countersign model's terms are no longer a
craft's: the ones an Agent Rule uses are rows below (`mandate`, `mode`, `explicit mode`, `implicit mode`,
`escalate edge`, `escalation`, `answer grammar`, `amend`, `party`, adopted by #369 C2), the rest are the
glossary of `dyad/playbooks/countersign-model.md`, five more rows below entering with C3's Rule sentences (`countersign`, `delegate edge`, `mode lifecycle`, `coded check`, `prose claim`; #369 C3; the reconciliation table:
`agent-corpus/falsification/countersign-consolidation.md`).

| term | definition | owner | used by |
|------|------------|-------|---------|
| Operator | the human party of the dyad; the sole disposer | frame | 2 3 4 5 6 |
| Agent | the model party of the dyad; the sole proposer | frame | 1 2 3 4 5 6 |
| Agent Rule | a Rule in `dyad/rules/`; the set Rules 4, 5 and 6 govern | 4 | 4 5 6 |
| Tended Rule | an Operator-tended rule in `workstation-corpus/rules/` or a Tended craft's `rules/` governing the craft or host, never the dyad's process; a separately contained set | 4 | 4 5 8 |
| block | the countable header of an Agent Rule: one Intent, one Target, Boundaries, Conditions | 4 | 4 |
| zone | a named set of paths; a repo transaction touches exactly one | 1 | 1 2 3 4 |
| host path | the repo-relative directory holding a system's host and operating records, the host row of the zone table; preference `host-path` (default `workstation-corpus`), its zone preference `host-zone` (`workstation` or `infra`) | 1 | 1 14 |
| repo transaction | a commit or a PR | 1 | 1 |
| ratification event | an act only the Operator may perform: merge, direct push, finalising a verdict, or an event another Rule declares | 2 | 2 3 |
| proposer | the party that authors a proposal, PR, verdict or record — always the Agent | 2 | 2 |
| disposer | the party that answers a counter-prompt — always the Operator | 2 | 2 |
| clerical | execution of a decision already disposed; not a ratification event | 2 | 2 3 7 |
| d-work | a unit of work opened by an Operator prompt and closed only by Done-Y; the countersign model's `act` (one row projects to one act) | 3 | 2 3 4 6 7 |
| ledger | the row-file store `agent-corpus/d-work/rows/` (Rule-16), one row per d-work, append-only; `LEDGER.md` is its rendered view | 3 | 2 3 4 5 16 |
| row file | `<instance>/d-work/rows/<id>.md`: one d-work's id, title, opened, state, disposed, refs; never deleted, id and title immutable | 16 | 16 |
| rendered view | `LEDGER.md` produced by `package.py ledger` from the row files; untracked | 16 | 16 |
| plan | the Agent's first substantive reply to a prompt: intent as read plus the mutation proposed | 3 | 3 |
| play-book | an executable procedure of the operator craft (`dyad/playbooks/<name>.md`) the Agent follows for a recurring decision; its steps are a run-book (`dyad/runbooks/<name>.md`) run through the core runner; read by a Rule, never a Rule | 3 | 3 |
| d-work trace | one d-work's measured time, from its first anchored Operator prompt to its Done-`Y` (to the Done question in the completion reply's preview): a timeline, every second in exactly one bucket (the Operator's wait, the Agent's inference, or a mechanical kind), counts and a bottleneck line; stored at `<instance>/d-work/traces/<id>.md` by the commit that records the Done-`Y`; made by `dyad dwork trace` under the play-book `dyad/playbooks/dwork-trace.md`; never holds transcript text | 3 | 3 |
| craft-instantiation-criteria | the D-criteria of plan #153 (D1 classification, D2 disposer, D3' import-or-extend, D4 ledger coupling, D5 lifecycle, D6 zone fit) the craft play-book applies: any firing advises a new dyad system, none a new craft instance | 3 | 3 |
| plan-Y | the Operator's `Y` to a plan; authorizes the mutation and binds every PR of the d-work to the plan | 3 | 3 |
| Done-Y | the Operator's `Y` to a completion counter-prompt; verifies the output against intent and, under `with-done`, ratifies the named merges | 3 | 2 3 |
| counter-prompt | a one-line `Y/N:` question the Agent asks; the Operator's answer is a disposition | 3 | 2 3 |
| intake | a candidate d-work carried by another agent's message — a defect as an observation with evidence, or an enhancement with its Operator's verbatim prompt behind it; opens nothing until the Operator disposes; the countersign model's `signal` | 3 | 3 7 |
| accreted row | a row the Agent opens while executing another, inside the mandate scope its authorized plan states: born `open` under that plan-`Y`, carrying no disposition of its own, its Done riding the mandate's Done-`Y`, which names it; the countersign craft's implicit mode under a mandate, adopted rather than coined | 3 | 2 3 7 15 16 |
| mandate scope | what a plan states if it is to accrete at all: a rule for the class of row it will open and a ceiling on how many; a plan stating none accretes nothing, and a row outside it returns to explicit mode and is asked | 3 | 2 3 |
| batch counter-prompt | a plan or completion counter-prompt (Rule-3) naming several d-works in one question, under `batch-disposition-mode` | 3 | 2 3 |
| pending queue | the conversational set of plan-ready and done-ready d-works not yet named in a batch counter-prompt; reported each reply while non-empty, never a corpus file | 3 | 3 |
| disposition | an Operator answer to a counter-prompt (`Y` or `N`, optionally with text); the countersign model's `countersignature` | 3 | 2 3 7 |
| open | ledger state: started; being worked or suspended by a newer prompt | 3 | 3 |
| blocked | ledger state: the Operator deferred it naming another d-work; reopens when that one is done | 3 | 3 |
| backlog | ledger state: opened by a disposition, not started; opens when the Operator prompts for it | 3 | 3 |
| planned | ledger state: the plan file is authorized by plan-Y; execution may start in any session | 15 | 3 15 |
| transition | a change of a row's state; legal only if in Rule-16's table (`dyadlib.TRANSITIONS`) | 16 | 3 16 |
| presence file | `<instance>/d-work/sessions/<id>.md`: one session's claim of what it is currently working — its working tree's root, the d-work ids and the files their stored plans touch and, when written, its holder's host and harness session id; touched at session start and plan-Y, read before a new plan; advisory, never a lock | 16 | 3 16 |
| plan file | `agent-corpus/d-work/plans/<id>.md`: the stored plan a plan-Y binds to — intent as read, mutation, files touched, base commit | 15 | 7 15 |
| base commit | the `main` commit a plan file was written against; execution re-plans if `main` moved past a touched file | 15 | 15 |
| done | ledger state: the Operator answered `Y` to the completion counter-prompt and the head that `Y` was given on is on `main`; the `Y` itself is recorded in `disposed` when it is given, with the state left as it was, and the state follows the merge (Rule-3, Completion counter-prompt) | 3 | 3 |
| archived | ledger state: a `done` or `backlog` d-work retired from the working board by an Operator disposition naming it; terminal; its files stay where they are | 3 | 3 16 |
| coherent | of Rules: no two instruct differently on the same trigger, and every cross-reference resolves to an existing Rule and heading | 5 | 5 6 |
| orthogonal | of Rules: every concern has exactly one owning Rule; a Rule names a neighbour in its Boundaries only for what it does not own; ownership is never shared | 5 | 5 |
| sweep | a pairwise coherence and orthogonality check of the Agent Rules, recorded in `agent-corpus/audits/` | 5 | 5 |
| falsification record | a table of attacks on a claim and their survivors, in `agent-corpus/falsification/`; a Rule's record lives in `rules/` and is package, any other is instance; disposed by the Done-Y of its d-work | 9 | 2 4 5 6 9 11 |
| audit | an agent-authored review elevating gaps for Operator disposition, in `agent-corpus/audits/` | frame | 2 4 5 |
| preference | an Operator-owned setting in `preferences-corpus/`, read by the Rule it names | frame | 1 2 3 4 5 13 |
| vocabulary | this file: the master record of Agent terms | 6 | 4 5 6 |
| subagent | a process the Agent spawns for part of its work; its actions are the Agent's; it reads, searches and drafts (plan files and branch changes under `delegation`), never acts on the Operator's behalf | 3 | 3 8 |
| delegation | the preference under which subagents draft plan files and execution branches while the main Agent keeps every act a disposition binds to | 3 | 3 |
| host action | anything the Agent does on the machine that is neither a repo transaction nor read-only | 8 | 3 7 8 |
| mutation | a change to the repo or the host that a plan proposes and a plan-Y authorizes; the unit the plan binds to | 3 | 3 8 |
| blocking question | a question the Agent must have answered by the Operator before continuing; the Agent never resolves it | 8 | 8 |
| plan gate | the check that a PR's cited d-work carries a `Y plan` disposition (`dyad/guards/agent/prs.py`) | 3 | 3 |
| completion reply | the Agent's reply that ends with a completion counter-prompt; carries the evidence the Operator's verification needs — the countersign model's `countersign report`, which is that evidence and asks nothing — before its last line | 3 | 3 |
| incident | an action or outcome the plan did not name, or a plan item not achieved as the plan said; reported at once and recorded | 3 | 3 |
| failure mode | the mechanism by which an incident happened — the thing that would have to change for it not to recur; never the Rule breached and never the harm caused | 3 | 3 |
| claim | anything a Rule, plan, preference or verdict would encode; falsified before it is | 9 | 9 |
| provenance record | `<instance>/d-work/provenance/<id>.md`: one d-work's Operator prompts and dispositions, verbatim, as numbered `## <n> <kind> <date>` entries each holding a fenced body; the Agent's own text is never in one | 7 | 7 |
| provenance store | `<instance>/d-work/provenance/`: the set of provenance records, one file per d-work id, written clerically beside the rows; raw session transcripts never enter it | 7 | 7 |
| attack | a test that could refute a claim; recorded with its result | 9 | 9 |
| survivor | the form of a claim that outlives its attacks; the only form implemented | 9 | 9 |
| proposal | anything the Agent asks a disposition on; the countersign model's `countersign proposal` (a plan file is the proposal its plan-Y answers) | 10 | 10 |
| counter | the strongest case against the proposed path, stated fairly | 10 | 10 |
| reconciliation | why the path holds despite the counter, or what it concedes | 10 | 10 |
| sentinel | the phrase in `dyad/CLAUDE.md` whose report at session start proves the frame loaded; never cached | 3 | 3 |
| memory cache | the per-machine `~/.claude/.../memory/` files summarising ratified corpus; each names its source path and ledger id; corpus wins | frame | 2 7 8 |
| System Requirements | the core craft's Agent Rules (`dyad/rules/`): what the dyad's process must satisfy and what each guard checks, the kernels of Rules 11, 12, 14, 16 and 20 included; a Requirement Rule owns its guard's check semantics | frame | 5 |
| System Architecture | the sysarch craft's rules (`crafts/sysarch/rules/`): how the infrastructure and guards are built, run and deployed; Tended since #160, never redefining what a guard checks (Rule-13 pending #162) | frame | 5 |
| package | the core craft's distributable form (`dyad/`): frame, Rules, vocabulary, guards, preference schema, templates; one root; identical across systems; the name the runner (`package.py`), its data and Rules 12–20 use for the core craft | 11 | 11 |
| instance | one system's state: ledger, incidents, audits, records, preference values, host corpus, Tended Rules, archives | 11 | 11 |
| craft | one unit of reusable practice: a contained tree with one root, `VERSION`, rules, vocabulary, templates, guard data, records, docs and no instance state; installed into any dyad system, idempotently | 11 | 1 4 5 11 14 |
| core craft | the craft every dyad system has, `dyad-operator`, at `dyad/`: frame, Agent Rules, Agent vocabulary, guards, templates; what Rule-11 formerly called the package | 11 | 4 5 11 14 |
| Tended craft | any craft other than the core craft: its rules are Tended Rules; its root is `crafts/<craft>/` (zone `craft`) | 11 | 1 4 5 11 14 |
| bundled craft | a Tended craft the core release carries: `dyad build` archives its tree and `dyad install` writes it, so a core-only install still has it; a Tended craft in every other respect, and bundled only by its own `BUNDLED_WITH_CORE` declaration, never by a list the core keeps | 11 | 11 |
| export | the deterministic archive of one craft's tracked tree at HEAD, `<craft>-<version>.tar.gz` (entries under `crafts/<craft>/`), produced by the one distribution code path (`dyad/scripts/distribute.py`); the core craft's export is `dyad build` | 11 | 11 |
| craft registry | `crafts/REGISTRY.md`: one row per installed craft — every Tended craft `dyad craft install` writes, and the core craft (`dyad-operator`) `dyad install` writes — craft, version, source, sha256 (the installed tree's identity, `distribute.archive_sha256`), d-work; instance state in the craft zone; never written by hand | 11 | 11 12 |
| craft corpus | the tree of one craft as a Rule-1 unit: the core craft's `dyad/` in the agent zone, a Tended craft's `crafts/<craft>/` in the craft zone | 11 | 1 11 |
| release | a git tag marking a craft's published version with its VERSION file and exported archive, or a bundle's (property 7) — `dyad-operator-vMAJOR.MINOR.PATCH` for the core craft, `<craft>-vMAJOR.MINOR.PATCH` for a Tended craft, `vMAJOR.MINOR.PATCH` for a bundle; cut only on the Operator's `Y` to `Y/N: release <tag>?`; the countersign model's `countersign release` | 11 | 11 |
| bundle | the whole distribution one repo authors, named at pinned versions in one `BUNDLE.md`: the core craft plus every Tended craft in the tree, each row's version equal to that craft's live `VERSION`; its own version, independent of the core's; released as the unprefixed `vMAJOR.MINOR.PATCH` tag | 11 | 11 |
| install | writing the package into another session's repo under its root plus documented prefixed hooks and its craft registry row, never overwriting a host file | 11 | 11 |
| invariant | a named predicate over a module's data model, in one of two lists: `INVARIANTS`, pure (the module's own literals only; no filesystem, version control, module loading or environment), enforced at import by the module itself (a fail-loud check); `TREE_INVARIANTS`, which read the package tree or load modules, never run at import; the runner's pass runs both lists before any check and reports each module as `[invariant]`; a false one is an incident | 12 | 11 12 |
| fail-loud check | a check in the code itself, neither a test nor error handling, that raises when a condition that should be impossible holds — a module's import-time `enforce` of its `INVARIANTS`, or a function that raises before the one write it guards; placed only at a strategic point (a boundary, a state transition, an impossible condition) where control passes once per process or rarely, never per item, with no off-switch; a test that only exercises its condition is redundant with it | 12 | 12 |
| suite memo | a per-checkout file under `<git common dir>/dyad-suite-memo/`, shared by every worktree and never tracked, recording that one tree passed every root of Rule-12's suite: named by the sha256 of that tree, the interpreter, git's version, the roots run, the instance's environment settings, a digest of `refs/tags`, a digest of the instance's `*.local.txt` files and the UTC date; written only after a full, all-roots pass on a clean tree, read only by the pre-push path, never by `check --evidence` | 12 | 12 |
| The Dyad System | the Operator, the Agent, the core craft, the Tended crafts and the instance | 14 | 14 |
| The World | everything that is not The Dyad System: the OS, hosting, services, packages, network | 14 | 14 |
| System Infrastructure | the surface between The Dyad System and The World; the container for every integration dependency; partitioned into kernel and library | 14 | 14 |
| kernel | the minimal pinned part of the System Infrastructure: a CLI inferencing agent, Python at a pinned version, Git as a local repository, and pydantic at a pinned version | 14 | 14 |
| manifest | the one list of every System Infrastructure dependency: component, partition, version, purpose, license, replacement, profile; the union of the core file, every craft's contribution and the instance's (under the host path) | 14 | 14 |
| profile | the manifest cell saying which activity of a system needs a row: `authoring`, `operating` or `both`; a kernel row is `both` | 14 | 14 |
| evidence block | the output of `package.py check --evidence` on an exact head: head sha, tree hash, dirty flag, every check and guard line, and a sha256 of those lines; pasted verbatim in the completion reply as the merge evidence, re-runnable by the Operator | 14 | 2 14 |
| recurring task | an operation the Agent has performed by inference before and will perform again; Rule-13's trigger | 13 | 13 |
| consistent | of a term: every Agent Rule uses it in the vocabulary's sense (Rule-6; distinct from *coherent*) | 6 | 6 |
| server instance | a long-running service on the host that the Agent deploys or is asked to operate: one run-book, one health command; its supervisor and the run-book's form are the sysadmin craft's | 19 | 8 19 |
| entrypoint | `dyad/bin/dyad`: the package's one command-line entry, `dyad <noun> <verb>`; invoked by path, never installed on the host's PATH | 11 | 11 |
| guard | one craft module that mechanically checks one entity kind: `dyad/guards/<corpus>/<entity>.py` (core) or `crafts/<craft>/guards/<entity>.py` (a Tended craft's), its data beside it, its test under that craft's `tests/guards/`; the entity's parser, imported by projectors and other guards (the contract: `crafts/sysarch/rules/guards.md`) | 11 | 1 2 3 4 6 8 11 12 13 14 15 16 18 19 20 |
| corpus | the Rule-1 zone of an entity's store: for a core guard the directory under `dyad/guards/` that holds it (`agent`, `workstation`, `preferences`, `infra`); for a craft guard its declared `CORPUS`, a zone name or `workstation`, the logical host corpus, which resolves to the host path's zone; the core craft stays one tree in the agent zone | 11 | 11 12 20 |
| seat | a role name (`cos`, `ds-cabinet-term-1`) bound to one presence file, `<instance>/d-work/sessions/<id>.md`, its `id` the `DYAD_SESSION` the holder runs `dyad` under; held by one harness session at a time and by many over time, never verifiable by the dyad; `cos` and `cabinet` are roles a seat plays (`agent-corpus/falsification/seat-vs-harness-session.md`, #295) | 16 | 16 |
| holder | the harness session that holds a seat now, as the presence file's optional `holder` line records it from `CLAUDE_CODE_SESSION_ID` beside `host`, written by `touch()` and never typed; what the process says, never proven; holder history is git's (#294, #295) | 16 | 16 |
| relayed prompt | an Operator prompt carried to a session by another agent and entered verbatim as the receiving row's `prompt` entry with the note `relayed via <session>` (`--relayed-via`, which attaches to `--prompt` and never to `--said`): the Operator's words, carrying no disposition; within one dyad system it opens a row as a prompt does, across systems it is an intake's enhancement shape (#34, #253 R29) | 3 | 3 |
| party | who acts in the dyad: the Operator (the human party, the sole disposer) or the Agent (the sole proposer); the countersign model's third kind, an executor, the dyad has none of | 2 | 2 3 18 19 |
| mode | the way a row obtains its disposition and who processes it: `explicit` (asked live, per row) or `implicit` (under a mandate); the row's optional field (Rule-16), absent meaning explicit; the countersign model's countersign mode, whose third value, automatic, the dyad does not realize | 3 | 3 16 |
| explicit mode | asked live: the row's plan and completion each take the Operator's own disposition | 3 | 2 3 |
| implicit mode | disposed in advance by a mandate: an accreted row born under the mandate's plan-`Y`, its Done riding the mandate's Done-`Y` | 3 | 3 |
| mandate | a standing disposition for one class of row: the plan-`Y` of a plan that states a mandate scope (Rule-3), or an authority preference (`accretion: implicit`, `ledger-pr-merge: agent`); the countersign model's standing countersignature of implicit mode | 3 | 2 3 7 15 16 |
| escalation | the unexpected returned to the Operator for a live disposition: an accreted row returned to explicit mode by the escalate edge, an incident, or an intake's origin; opens an explicit row or none | 3 | 3 |
| escalate edge | the mode change implicit → explicit: the row's work departs from the mandate scope, so the Agent reports it and asks | 3 | 3 |
| answer grammar | the three answers to a counter-prompt — `Y`, bare `N`, `N` with text (amend) — and what each authorizes (Rule-3) | 3 | 3 |
| amend | the third answer: the proposal refused and its revision asked for in the same words; `N` with text, entered as a `prompt` entry of the refused d-work's own record | 3 | 3 |
| countersign | to answer, as the second and independent party, what the first party proposed, without which nothing moves: in the dyad the Operator's disposition of the Agent's proposal; the name of the model the d-work framework is checked against (`dyad/playbooks/countersign-model.md`) | 3 | 3 |
| delegate edge | the mode change explicit → implicit: a live disposition becomes a mandate — the plan-`Y` of a plan that states a mandate scope (Rule-3) | 3 | 3 |
| mode lifecycle | the sequence of exchanges one mode's row passes through: explicit — prompt, plan, disposition, execution, completion evidence and Done question, disposition; implicit — a row born under a mandate, executed within its scope, reported, or returned to explicit mode by the escalate edge (`dyad/playbooks/countersign-model.md` Part II §4) | 3 | 3 |
| coded check | a check code runs — a test, a guard or an invariant: mechanical, re-runnable, cheap; one of the two kinds of check the audit play-book's self-diagnostic runs, named for how it checks and never for what it examines | 12 | 12 |
| prose claim | a sentence a system asserts about itself, checked by reading it against a written attack that names what would make it false; a claim with no attack is no check; the other kind the self-diagnostic runs, which may examine code | 12 | 12 |
| seat name | the name of a presence file and so of its seat: under `organization: m4` the form `<function>[-<topic>]-<hp>` — a function the organization's mandates table lists, an optional topic, and the first eight hex of the holder's harness session id — the installed organization craft's data (`crafts/cabinet/guards/seats_rules.txt`) where one is installed, the bare form of `sessions.py` otherwise; read advisorily by `touch()`, printed with the session title by `dyad session name`; under `flat` any path-safe name (#369 C7) | 16 | 3 16 |
| cos-board | the board a seat with a function keeps over its scope and reads at every reply: the rows of its charter's domain and the seats under it; the leader's (the cos's) is the board of programs, a secretary's the board of its function and its desks; its form and reading are the organization craft's Operating Guide, never a Rule (#369) | 16 | 3 16 |
| secretary | a seat beside the leader that keeps a cos-board over one function's domain under a charter (a row of the mandates table), named `<function>-<hp>`; one of the at most seven lines the leader reads; it opens desks, seats of one topic each, as its concurrent work needs (#368, #369, #416, #417) | 16 | 3 16 |
| attended | of a seat: the Operator sits at it — the leader always, and every seat the `attended-seats` preference names (default `none`), by seat name or by that name without its `-<hp>`; declared by the preference, checked against the records: a live seat whose provenance record (its `session:` line naming it) holds a disposition the Operator gave there — noted neither `mandate #<id>` nor `relayed via` — within the `attendance-window` preference, and which is not declared, prints `undeclared` (a board reading, reported by the leader alone), a declared seat holding none prints `warn`; never written to a presence file (#388, #393, #412, #414) | 16 | 16 |
