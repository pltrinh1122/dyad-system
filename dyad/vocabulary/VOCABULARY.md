# Agent vocabulary (master record, Rule-6)

One row per term. The definition here is the only definition; Agent Rules use the term and
cite this file. `owner` is the Rule whose concern the term belongs to; `used by` lists the
Rules that use it (checked by `dyad/guards/agent/vocabulary.py`: owner exists, no orphan, no duplicate).
Terms defined elsewhere (preference keys in `preferences-corpus/`, Tended Rules' terms) are
referenced, never defined, here. Craft terms are defined in `crafts/<craft>/vocabulary/CRAFT.md`
and referenced here by craft name (the sysarch craft's: `projection`, `projector`, `surface`,
`library`, `reference`, `resolver`, `guard contract`, #160; the sysadmin craft's: `read-only`, `reversible`, `destructive`,
`change log`, `undo`, `ops script`, `postcondition`, `supervisor`, `run-book`, `health command`,
`run-book command`, `event`, `role`, `scope`; #155).

| term | definition | owner | used by |
|------|------------|-------|---------|
| Operator | the human party of the dyad; the sole disposer | frame | 2 3 4 5 6 |
| Agent | the model party of the dyad; the sole proposer | frame | 1 2 3 4 5 6 |
| Agent Rule | a Rule in `dyad/rules/`; the set Rules 4, 5 and 6 govern | 4 | 4 5 6 |
| Tended Rule | an Operator-tended rule in `workstation-corpus/rules/` or a Tended craft's `rules/` governing the craft or host, never the dyad's process; a separately contained set | 4 | 4 5 8 |
| block | the countable header of an Agent Rule: one Intent, one Target, Boundaries, Conditions | 4 | 4 |
| zone | a named set of paths; a repo transaction touches exactly one | 1 | 1 2 3 4 |
| repo transaction | a commit or a PR | 1 | 1 |
| ratification event | an act only the Operator may perform: merge, direct push, finalising a verdict, or an event another Rule declares | 2 | 2 3 |
| proposer | the party that authors a proposal, PR, verdict or record — always the Agent | 2 | 2 |
| disposer | the party that answers a counter-prompt — always the Operator | 2 | 2 |
| clerical | execution of a decision already disposed; not a ratification event | 2 | 2 3 7 |
| d-work | a unit of work opened by an Operator prompt and closed only by Done-Y | 3 | 2 3 4 6 7 |
| ledger | the row-file store `agent-corpus/d-work/rows/` (Rule-16), one row per d-work, append-only; `LEDGER.md` is its rendered view | 3 | 2 3 4 5 16 |
| row file | `<instance>/d-work/rows/<id>.md`: one d-work's id, title, opened, state, disposed, refs; never deleted, id and title immutable | 16 | 16 |
| rendered view | `LEDGER.md` produced by `package.py ledger` from the row files; untracked | 16 | 16 |
| plan | the Agent's first substantive reply to a prompt: intent as read plus the mutation proposed | 3 | 3 |
| play-book | an executable procedure of the operator craft (`dyad/playbooks/<name>.md`) the Agent follows for a recurring decision; its steps are a run-book (`dyad/runbooks/<name>.md`) run through the core runner; read by a Rule, never a Rule | 3 | 3 |
| craft-instantiation-criteria | the D-criteria of plan #153 (D1 classification, D2 disposer, D3' import-or-extend, D4 ledger coupling, D5 lifecycle, D6 zone fit) the craft play-book applies: any firing advises a new dyad system, none a new craft instance | 3 | 3 |
| plan-Y | the Operator's `Y` to a plan; authorizes the mutation and binds every PR of the d-work to the plan | 3 | 3 |
| Done-Y | the Operator's `Y` to a completion counter-prompt; verifies the output against intent and, under `with-done`, ratifies the named merges | 3 | 2 3 |
| counter-prompt | a one-line `Y/N:` question the Agent asks; the Operator's answer is a disposition | 3 | 2 3 |
| intake | a candidate d-work carried by another agent's message — a defect as an observation with evidence, or an enhancement with its Operator's verbatim prompt behind it; opens nothing until the Operator disposes | 3 | 3 7 |
| batch counter-prompt | a plan or completion counter-prompt (Rule-3) naming several d-works in one question, under `batch-disposition-mode` | 3 | 2 3 |
| pending queue | the conversational set of plan-ready and done-ready d-works not yet named in a batch counter-prompt; reported each reply while non-empty, never a corpus file | 3 | 3 |
| disposition | an Operator answer to a counter-prompt (`Y` or `N`, optionally with text) | 3 | 2 3 7 |
| open | ledger state: started; being worked or suspended by a newer prompt | 3 | 3 |
| blocked | ledger state: the Operator deferred it naming another d-work; reopens when that one is done | 3 | 3 |
| backlog | ledger state: opened by a disposition, not started; opens when the Operator prompts for it | 3 | 3 |
| planned | ledger state: the plan file is authorized by plan-Y; execution may start in any session | 15 | 3 15 |
| transition | a change of a row's state; legal only if in Rule-16's table (`dyadlib.TRANSITIONS`) | 16 | 3 16 |
| presence file | `<instance>/d-work/sessions/<id>.md`: one session's claim of what it is currently working — its working tree's root, the d-work ids and the files their stored plans touch; touched at session start and plan-Y, read before a new plan; advisory, never a lock | 16 | 3 16 |
| plan file | `agent-corpus/d-work/plans/<id>.md`: the stored plan a plan-Y binds to — intent as read, mutation, files touched, base commit | 15 | 7 15 |
| base commit | the `main` commit a plan file was written against; execution re-plans if `main` moved past a touched file | 15 | 15 |
| done | ledger state: the Operator answered `Y` to the completion counter-prompt | 3 | 3 |
| coherent | of Rules: no two instruct differently on the same trigger, and every cross-reference resolves to an existing Rule and heading | 5 | 5 6 |
| orthogonal | of Rules: every concern has exactly one owning Rule; a Rule names a neighbour in its Boundaries only for what it does not own; ownership is never shared | 5 | 5 |
| sweep | a pairwise coherence and orthogonality check of the Agent Rules, recorded in `agent-corpus/audits/` | 5 | 5 |
| falsification record | a table of attacks on a claim and their survivors, in `agent-corpus/falsification/`; a Rule's record lives in `rules/` and is package, any other is instance; disposed by the Done-Y of its d-work | 9 | 2 4 5 6 9 11 |
| audit | an agent-authored review elevating gaps for Operator disposition, in `agent-corpus/audits/` | frame | 2 4 5 |
| preference | an Operator-owned setting in `preferences-corpus/`, read by the Rule it names | frame | 2 3 4 5 13 |
| vocabulary | this file: the master record of Agent terms | 6 | 4 5 6 |
| subagent | a process the Agent spawns for part of its work; its actions are the Agent's; it reads, searches and drafts (plan files and branch changes under `delegation`), never acts on the Operator's behalf | 3 | 3 8 |
| delegation | the preference under which subagents draft plan files and execution branches while the main Agent keeps every act a disposition binds to | 3 | 3 |
| host action | anything the Agent does on the machine that is neither a repo transaction nor read-only | 8 | 3 7 8 |
| mutation | a change to the repo or the host that a plan proposes and a plan-Y authorizes; the unit the plan binds to | 3 | 3 8 |
| blocking question | a question the Agent must have answered by the Operator before continuing; the Agent never resolves it | 8 | 8 |
| plan gate | the check that a PR's cited d-work carries a `Y plan` disposition (`dyad/guards/agent/prs.py`) | 3 | 3 |
| completion reply | the Agent's reply that ends with a completion counter-prompt; carries the evidence the Operator's verification needs | 3 | 3 |
| incident | an action or outcome the plan did not name, or a plan item not achieved as the plan said; reported at once and recorded | 3 | 3 |
| claim | anything a Rule, plan, preference or verdict would encode; falsified before it is | 9 | 9 |
| provenance record | `<instance>/d-work/provenance/<id>.md`: one d-work's Operator prompts and dispositions, verbatim, as numbered `## <n> <kind> <date>` entries each holding a fenced body; the Agent's own text is never in one | 7 | 7 |
| provenance store | `<instance>/d-work/provenance/`: the set of provenance records, one file per d-work id, written clerically beside the rows; raw session transcripts never enter it | 7 | 7 |
| attack | a test that could refute a claim; recorded with its result | 9 | 9 |
| survivor | the form of a claim that outlives its attacks; the only form implemented | 9 | 9 |
| proposal | anything the Agent asks a disposition on | 10 | 10 |
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
| export | the deterministic archive of one craft's tracked tree at HEAD, `<craft>-<version>.tar.gz` (entries under `crafts/<craft>/`), produced by the one distribution code path (`dyad/scripts/distribute.py`); the core craft's export is `dyad build` | 11 | 11 |
| craft registry | `crafts/REGISTRY.md`: one row per installed Tended craft — craft, version, source, sha256, d-work; instance state in the craft zone; written by `dyad craft install`, never by hand | 11 | 11 |
| craft corpus | the tree of one craft as a Rule-1 unit: the core craft's `dyad/` in the agent zone, a Tended craft's `crafts/<craft>/` in the craft zone | 11 | 1 11 |
| release | a git tag marking a craft's published version with its VERSION file and exported archive, or a bundle's (property 7) — `dyad-operator-vMAJOR.MINOR.PATCH` for the core craft, `<craft>-vMAJOR.MINOR.PATCH` for a Tended craft, `vMAJOR.MINOR.PATCH` for a bundle; cut only on the Operator's `Y` to `Y/N: release <tag>?` | 11 | 11 |
| bundle | the whole distribution one repo authors, named at pinned versions in one `BUNDLE.md`: the core craft plus every Tended craft in the tree, each row's version equal to that craft's live `VERSION`; its own version, independent of the core's; released as the unprefixed `vMAJOR.MINOR.PATCH` tag | 11 | 11 |
| install | writing the package into another session's repo under its root plus documented prefixed hooks, never overwriting a host file | 11 | 11 |
| invariant | a named predicate over a module's constants, listed in that module's `INVARIANTS`, run by the runner before any check and reported as `[invariant]`; a false one is an incident | 12 | 11 12 |
| The Dyad System | the Operator, the Agent, the core craft, the Tended crafts and the instance | 14 | 14 |
| The World | everything that is not The Dyad System: the OS, hosting, services, packages, network | 14 | 14 |
| System Infrastructure | the surface between The Dyad System and The World; the container for every integration dependency; partitioned into kernel and library | 14 | 14 |
| kernel | the minimal pinned part of the System Infrastructure: a CLI inferencing agent, Python at a pinned version, Git as a local repository, and pydantic at a pinned version | 14 | 14 |
| manifest | the one file listing every System Infrastructure dependency: component, partition, version, purpose, license, replacement | 14 | 14 |
| evidence block | the output of `package.py check --evidence` on an exact head: head sha, tree hash, dirty flag, every check and guard line, and a sha256 of those lines; pasted verbatim in the completion reply as the merge evidence, re-runnable by the Operator | 14 | 2 14 |
| recurring task | an operation the Agent has performed by inference before and will perform again; Rule-13's trigger | 13 | 13 |
| consistent | of a term: every Agent Rule uses it in the vocabulary's sense (Rule-6; distinct from *coherent*) | 6 | 6 |
| server instance | a long-running service on the host that the Agent deploys or is asked to operate: one run-book, one health command; its supervisor and the run-book's form are the sysadmin craft's | 19 | 8 19 |
| entrypoint | `dyad/bin/dyad`: the package's one command-line entry, `dyad <noun> <verb>`; invoked by path, never installed on the host's PATH | 11 | 11 |
| guard | one craft module that mechanically checks one entity kind: `dyad/guards/<corpus>/<entity>.py` (core) or `crafts/<craft>/guards/<entity>.py` (a Tended craft's), its data beside it, its test under that craft's `tests/guards/`; the entity's parser, imported by projectors and other guards (the contract: `crafts/sysarch/rules/guards.md`) | 11 | 1 2 3 4 6 8 11 12 13 14 15 16 18 19 20 |
| corpus | the Rule-1 zone of an entity's store: for a core guard the directory under `dyad/guards/` that holds it (`agent`, `workstation`, `preferences`, `infra`); for a craft guard its declared `CORPUS`, a zone name; the core craft stays one tree in the agent zone | 11 | 11 12 20 |
