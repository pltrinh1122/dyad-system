# Vocabulary crosswalk (old → new, d-work #553)

The dyad-native vocabulary replaced several terms on 2026-11-02 (plan #553, scope 2: the terms change; mechanisms,
Rules' force and history are kept). History is never rewritten — rows, plans, provenance and presence files keep the
words they were written in — so this table is how a reader of older text finds the term it means now. The vocabulary
(`VOCABULARY.md`, Rule-6) is the one place each new term is defined; this file defines nothing and only maps.

`kind`: **term** (prose; no tool reads it), **key** (a preference, row, board or front-matter key a tool reads),
**form** (a value or line shape a tool reads), **entity** (a guard's entity name), **file** (a path).
`alias until`: tooling accepted the old spelling beside the new one until the release after next (the backlog row
#553's mandate opens); `removed (#604, …)` once tooling refuses it, naming the new one; `—` where no tool read the old
spelling.

| old | new | kind | alias until | note |
|---|---|---|---|---|
| seat (the generic) | unit | term | — | any position: one holder at a time, many over time. the vocabulary's `seat` alias row was removed by #604 |
| attended seat | dyad unit | term | — | a unit where the operator and the agent are both present, so a live disposition is possible; say "dyad unit" when the system is also in view |
| unattended seat | solo | term | — | a unit where the agent works alone, on authority carried verbatim from the ledger; it never receives a live disposition while it is a solo |
| executor (the countersign model's party kind) | automaton (party); auto (unit kind) | term | — | a non-inferring party running a released definition: automatic, not autonomous; `executor` stays in the countersign play-book as the model's word; its vocabulary alias row was removed by #604 |
| cos (as the structural name) | home | term | — | the dyad unit the operator always returns to; every solo's questions reach the operator through it; `cos` stays as its title |
| cos-board | home board | term | — | optional, as the operator allowed; `cos-board` is still read |
| the cos as a mode (cabinet Guide §10) | home follows you | term | — | "mode" collided with the vocabulary's `mode` and the harness's auto mode; the office the home is, held by one session at a time (#560, F2) |
| toggling `attended-seats` | pair / unpair | term | — | the operator starts or stops attending a unit; a unit's kind follows (decision 3) |
| a unit of work (as d-work's definition) | d-work (redefined) | term | — | a body of work opened by an operator prompt and closed only by done-Y; its scope is set by its plan and widens under a mandate |
| Done-Y, Done-`Y` | done-Y | term | — | the answer token `Y` keeps its case (decision 1) |
| Plan-Y | plan-Y | term | — | as above |
| Operator, Agent (in prose) | operator, agent | term | — | lowercase in prose (decision 2); `Agent Rule` and other names that are themselves terms keep their form |
| `attended-seats` | `paired-units` | key | removed (#604, the first core release after `dyad-operator-v0.18.0`) | preferences; a table still holding the old key fails the presence guard, naming the new one; renaming the operator's own value is a preferences-zone question of its own |
| `waiting-on: seat <name>` | `waiting-on: unit <name>` | form | removed (#604, the first core release after `dyad-operator-v0.18.0`) | board store; a stored old form fails the guard and `board set` refuses it, each naming the new one |
| `dyad session list`, the attendance column (`attended` / not) | the unit kind: `dyad` (paired) or `solo`; `auto` reserved, printed for no presence file yet since no automaton keeps one | form | — | the route column keeps `chat` / `relayed`, its header now `route`; the mode line says units for seats |
| `seat` (the cabinet guard's entity), `seats.py`, `seats_rules.txt` | not renamed (identifier) | entity | — | renaming them would change the registry, `check --list`, the references register and the tests, a mechanism; only their messages say unit; `function:` lines unchanged |
| a preference value typed off-canonical (`With-Done`) | casefolded to its canonical spelling | form | — | the preferences guard compares casefolded and warns, naming the canonical spelling; never fails (`label-case` L6) |
| uppercase files (`RULE-*.md`, `VOCABULARY.md`, `PREFERENCES.md`, …) | unchanged | file | — | kept as the closed uppercase list of syseng `naming.md` (decision 4) |
| `Y plan`, `Y done`, `Y release`, `N amend` (ledger entries) | unchanged | form | — | ledger grammar, written by tooling in exact case (`label-case` L2); never renamed |

Not adopted: "bond" for the pair — dyad-bond is another system.
