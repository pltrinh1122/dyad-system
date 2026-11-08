# Play-book: precedent bootstrap (core craft, `dyad-operator`; #645)

A play-book (vocabulary, Rule-3) is an executable procedure of the operator craft that the agent follows for a recurring decision. Its steps are a run-book.

This one fills an instance's decision log with its first precedents. It reads only the instance's own past rulings: its ledger, its plans, its falsification records and its change log. So an instance that upgrades to a core carrying the `precedent` kind starts from its own history, and nothing of another instance's travels (#644 F6).

The procedure is #644's hand-run backfill shipped as code. It runs the admission gate *before* the question. #644 asked first and gated after, and 20 of its 29 admitted cases were refused afterwards (#644's incident).

Its commands are `dyad/runbooks/precedent-bootstrap.md`, run through `dyad runbook run precedent-bootstrap <step>`, the core runner, so each command leaves an event. Every other step is the agent's reading, each against the criterion it cites.

A run proposes and never converts. Its one question is the precedent-`Y` (Rule-3). Converting a record to kind `precedent` is the work of a row of its own, under its own plan.

## Parameter
`RECORD`, optionally: one DMC record id to bootstrap. Absent, every record step 1 lists. The run reaches the instance through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3) and runs from the git root. Its working files (the case files, the prompt, the two readers' answers, the kept and admitted lists) stay in the scratchpad and are never tracked. The commands' `scope` lines name them.

## Trigger
The run is due in either of two cases:
- the operator prompts for it;
- the first session after a `dyad install` brings a core whose `dyad/dmc/schema.md` names the `precedent` kind while the instance's decision log (`<instance>/d-work/decisions/`, Rule-16) holds none.

Once one precedent-`Y` has been recorded, the upgrade trigger never fires again. From then on, new precedents arrive with each Done (Rule-3), and the run is only ever due by prompt.

## Steps
In order, each citing its criterion:

1. **records** — the records the run may fill:
   - Only records judged by inference qualify. A record already decided by code or declared by a party is not a candidate.
   - Each record is classed by `dmc:judgement-complexity`. Only one it leaves to precedent goes on.
   - A record whose consequences name a ratifying act is dropped here, before any case is built. `dmc:precedent-admission`'s first test judges that, and it would refuse every case of such a record later (#644's two such records).
   - An empty list ends the run with zero cases (Evidence).
2. **structured** — the run-book's `structured` step. It reads the sources whose cells already hold a record's own outcome name and prints one candidate per case. No reader labels these, and they are never sent to the readers.
3. **prose cases** — the agent assembles, per record, the cases whose outcome is written in prose: plans, rows, falsification records and the change log. Each case is one line of the case file, `{case, record, row, facts, label}`:
   - `facts`: the decisive inputs, stated neutrally, with no outcome name and no verdict;
   - `label`: the outcome, quoted from the source that set it;
   - `row`: the row whose plan-`Y` or Done-`Y` covered the ruling. A case no `Y` covered is not built.
   - `record`: the record's bare id (`changelog-actor`), never craft-prefixed (`sysadmin/changelog-actor`); a prefixed id names no record, and the `prompt` step refuses the case.
   - Cap: at most 12 cases per record, the most recent first (#645 F1).
4. **readers** — the run-book's `prompt` step builds the blind prompt from the case file. It holds each record's question, outcomes, precedence and default, and each case's id and facts, never a label.
   - Two readers answer it blind, by role: `cheap` and `default`. Each instance names its own models, and the event records which.
   - The run-book's `score` step compares each answer with the label. A case is kept only when both readers match.
   - Each mismatch is arbitrated by the agent:
     - one reader missed: a limit of that model, and the case is set aside;
     - both missed: a gap in the record's context, and the agent proposes either refactoring the record or overruling the label, never both.
5. **gate** — the run-book's `gate` step runs `dmc:precedent-admission` over the kept cases, the structured candidates among them. It judges each case as if the question had already admitted it. Only the admitted cases go on; every other case is listed refused, with the record's own outcome.
6. **question** — the precedent-`Y` over the admitted cases alone (Question). The set-aside and refused lists stand beside it, never in it.
7. **convert or wait** — once the precedent-`Y` is recorded, the run-book's `agreement` step measures each record's frozen set against that record's bar:
   - a record at the bar is proposed for conversion as a row of its own;
   - a record below it stays inference, and the run reports the count of cases it lacks.

Each step cites its criterion and restates none of its outcomes.

## Question
At most one per run, and none when the gate admits nothing: the precedent question of Rule-3, `Y/N: admit as precedents <cases>?`, over the admitted cases. Each case is listed before the question with its record, its label, its covering row and its source (`structured` or `two-readers`).
- A `Y` is recorded with `dyad dwork state … -d 'Y precedent (…)' --decisions "$ADMITTED"`. That writes exactly the named cases to the decision log as precedents.
- Any other answer writes none.

## Evidence
The reply cites, in order:
- each run-book event's id;
- step 1's record list, with the condition that dropped each excluded record;
- per record:
  - the structured count;
  - the prose count;
  - each reader's score (`<n matched>/<n>`);
  - the kept, set-aside and refused lists, each case with its reason;
- after the `Y`, each record's agreement against its bar, and each conversion proposed.

A fresh install, or a ledger with no ruling a `Y` covered, reports zero cases at step 1 or 2 and stops without a question (#645 F3).
