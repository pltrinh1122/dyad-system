# Play-book: play-book optimization (core craft, `dyad-operator`; #642)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the agent follows for a recurring
decision; its steps are a run-book. This one is run over another play-book, to cut what a run of it costs in tokens and
in time. It keeps the agent's inference only for the judgements that neither code nor ratified precedent can derive:
each judgement a step cites is classed by `dmc:judgement-complexity`. The criterion's falsification is
`agent-corpus/falsification/judgement-complexity.md`. Its first step is `dyad/runbooks/playbook-optimize.md` —
`profile` — run through `dyad runbook run playbook-optimize profile`, the core runner, so each run leaves an event;
the other three steps are the agent's reading of that profile, each against the criterion it cites.

A run is **monitoring**, never a d-work (Rule-3 Ledger, #438): the profile is read-only, its record is the run-book's
event, and nothing opens a row unless the operator answers the run's one question. A run proposes and never applies:
converting a record is the work of the row the question opens, under its own plan.

## Parameter
`PLAYBOOK`: the stem of the play-book to optimize, a file in `dyad/playbooks/`. The run reaches the instance's traces
and stores through `${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3).

## Trigger
The operator's prompt, or a play-book whose profile has not been read since its last change: a run reads only what a
change can move (Rule-14 property 3's reading of a check's inputs).

## Steps
In order, each citing its criterion:
1. **`profile`** — the run-book's one step, `dyad playbook profile <name>`. Per step: its heading, its words, and the
   `dmc:` ids and commands it cites. Per cited record: its words and its kind. Then the run's total words (#626's
   measure) and the time side: over the d-work traces of rows whose plan names the play-book, the median seconds of
   inference and of mechanical work. A trace is per d-work, not per step, so time is printed as the play-book's, and
   the profile prints that limit. It prints facts, never a class.
2. **class** — `dmc:judgement-complexity` for each cited record judged by inference, #641's test first (the
   criterion's precedence). A record already decided by code or declared by a party is not classed again.
3. **measure** — for each record the criterion leaves to precedent, a precedent set is frozen from that record's
   past cases a plan-`Y` or done-`Y` covered, each with the record's decisive inputs and the outcome it set
   (`dyad/scripts/similar.py` `freeze`, which refuses a case whose covering row holds no `Y` on `main`, its sha256 and
   base commit printed), each of its inputs declared structured or prose, and its agreement is measured on a held-out
   share (`agreement`). The set stays in the scratchpad. A record with no ratified cases cannot be measured, and the
   run says so; an agent ruling no `Y` covered is no precedent, and neither is an outcome the code gave by itself.
   Each held-out case is run through `decide`, which cites the precedent's row and score or abstains with its reason;
   the run lists the abstentions by reason, which are what still reaches the agent.
4. **propose** — one candidate row per record that passes, naming its class, its module or its precedent set, and
   its measured agreement against the bar. A record that fails stays inference, the failed condition named. A word
   the profile shows any step restating from a record it cites is a candidate too: the step cites the record and drops
   the copy (#626).

Each step cites its criterion and restates none of its outcomes. The profile is the run's only command: a fact read by
hand twice is a recurring task (Rule-13 property 1), proposed as a column of the profile.

## Question
At most one per run, and none when nothing passes: the batch of candidate rows, `Y/N: open #a, #b, … #k as backlog?`,
each row listed before it with its record, class and evidence. A `Y` opens exactly the named rows as `backlog`; any
other answer opens none. A candidate row's plan is asked as any plan, and a record's kind changes only there.

## Evidence
The reply cites the run-book event's id, then the profile's totals, each cited record's class with the condition that
decided it, each measured set's sha256 and agreement, and each candidate's ground.
