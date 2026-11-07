# Play-book: backlog grooming (core craft, `dyad-operator`; #625)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the agent follows for a recurring
decision; its steps are a run-book. This one grooms the backlog whole: it runs, in one order and over every `backlog`
row, the parts that each had a criterion of their own and ran at their own moment — hygiene, retirement, sizing,
promotion — and adds the one part none of them covered, a **release plan** that looks forward: which groomed rows the
next release of each craft should hold. It is run by the home, which owns the backlog and promotion (Rule-3 Ledger;
the cabinet craft's Operating Guide). Its one step is `dyad/runbooks/backlog-groom.md` — `report` — run through
`dyad runbook run backlog-groom report`, the core runner, so each run leaves an event; the other four steps are the
home's reading of that report, each against the criterion it cites, and redefine none.

A run is **monitoring**, never a d-work (Rule-3 Ledger, #438): the report is read-only, its record is the run-book's
event, an events-only commit, and nothing opens a row. It asks the operator at most one question, the retirement form,
and only when a row has a retirement ground; promotion keeps its own moment and the release plan asks nothing.

## Parameter
None. The run reads the live backlog, the board and the release tags; it reaches the instance through
`${DYAD_INSTANCE:-agent-corpus}` (Rule-11 property 3).

## Trigger
`dyad/dmc/groom-trigger.jsonld` decides whether a run is due. In precedence order:
- **operator prompt** (G1): the operator asks for a grooming. Due, whatever the floor says.
- The **floor**: no run while the backlog's rows and the board are unchanged since the last grooming event (the newest
  event of the run-book's store, which the report prints as `last-groom`), except under G1. It is what stops G3 firing
  again on a run that promoted nothing.
- **release landed** (G2): a release tag was published since the last grooming event, so the release plan the last run
  projected is spent.
- **promotion found nothing** (G3): `dyad/dmc/promotion.jsonld` reached **no proposal** while a unit is idle and the
  backlog is not empty. Due once per backlog state.
- **hygiene over the count** (G4): `dyad board resume` prints five or more hygiene lines. Five is the record's fixed
  count, not a preference: changing it is a change to the record.
- **not due**, the default: no run.

## Steps
In order, each citing its criterion:
1. **`report`** — the run-book's one step, `dyad board groom`. A head line, `groom report: N backlog row(s) on <sha12>;
   K board anchor(s)`; then one block per `backlog` row, by id — `#<id>[-<slug>] [backlog, <age>d] <title>`, then
   `refs:` each ref with its state, `adjacency:` the nearest board anchor (a row with a board entry, not terminal) with
   its cosine by the hygiene code's weighting, `promised:` the `_cos` files whose `promised` names the row, `roots:` the
   crafts the row's plan file names by path, and the hygiene lines naming the row, verbatim from the hygiene code and
   never recomputed (`dyad/dmc/backlog-hygiene.jsonld`); then `releases:`, per craft its last tag and live `VERSION`,
   and the bundle's; and last `last grooming:`, the newest event of this run-book's step. It prints facts, never a
   judgement: the class each step below assigns is the home's.
2. **retire** — `dyad/dmc/retirement-candidate.jsonld` per row, then `dyad/dmc/retirement-sweep.jsonld` over the set.
   A row with a retirement ground is listed in the retirement form, the one question a run may ask.
3. **size** — `dyad/dmc/altitude.jsonld` per remaining row: one definition of done, or split. A row altitude splits is
   **not plannable** in the step after next until it is split; the split is a row of its own, asked as any row.
4. **promote** — `dyad/dmc/promotion.jsonld`'s ranking over the remaining rows, recorded in the grooming reply. It is
   proposed only at a unit's idle moment, as the d-work play-book's promotion section says; a grooming run never asks
   it.
5. **plan the release** — `dyad/dmc/release-plan.jsonld` per remaining row, with the classes and numbers of
   `dyad/dmc/release-class.jsonld` and `dyad/dmc/release-number.jsonld` read by reference:
   - **next release**: the row's projected class releases and is the highest among its craft's backlog rows, or it is
     a critical fix; no ref is unresolved; altitude sizes it as one definition of done;
   - **a later release**: the row releases, below the class that sets the next release's theme, or a ref is not yet
     terminal;
   - **rides any release**: maintenance, which needs no release of its own;
   - **held for a major**: breaking, planned only on the operator's prompt for a major;
   - **not plannable**, the default: no craft root can be read from its plan, title or refs, or altitude says split;
     the reply names what is missing.

   The projected number per craft is `release-number` applied to the highest class among that craft's next-release
   rows. The plan is written to the home's cross-row board file as its `release-plan` line (`dyad board set`), which
   the promotion criterion reads (within a class, a next-release candidate first), and posted to the unit that ships
   crafts as a notice: information, never authority. It publishes nothing and ratifies nothing: whether a change set
   releases, and at what number, stays the release play-book's call after landing (`dyad/playbooks/release.md`), and a
   release stays Rule-11's question.

## Question
At most one per run: the retirement form, `Y/N: archive #a, #b, … #k?`, each row listed before it with what it holds
and its ground (Rule-3 Ledger). A `Y` archives exactly the named rows; any other answer archives none, and the rows
stay groomed. Nothing else in a run is asked.

## Evidence
The grooming reply cites the run-book event's id and the `release-plan` line as written, then each step's result: the
retirement ground per row, the size per row, the promotion ranking, and the plan per craft with its projected number.
A first run on a backlog whose `release-plan` key the board guard does not yet admit cites the plan as the reply states
it, and the line is written once the key is admitted.

## Conduct
- Each step cites its criterion and restates none of its outcomes beyond naming them; on divergence the record wins.
- The report is the run's only command. A run that needs a fact the report does not print reads it by hand and names
  it in the reply, and a fact read by hand twice is a recurring task (Rule-13 property 1), proposed as a column of the
  report.
- A run never opens, plans or closes a row: an archive is the operator's `Y` to the retirement form, executed
  clerically (`dyad dwork retire`), and a promotion is the promotion question at its own moment.
