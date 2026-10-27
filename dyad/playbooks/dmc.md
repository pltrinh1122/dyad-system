# Play-book: decision-making criteria (core craft, `dyad-operator`; #507)

A play-book (vocabulary, Rule-3): an executable procedure of the operator craft the Agent follows for a
recurring decision. This one decides how a **decision-making criterion** (DMC) — one recurring decision of the
dyad, stated as a question, its inputs and a finite set of outcomes — is written down as a record and where
that record lives. A DMC record is an index of prose, never its master: the Rule, craft rule, play-book or
preference that defines the outcomes stays the one definition (Rule-6 by analogy), and the record names it as
`dyad:home`. The shape is `dyad/dmc/schema.md`, the one context `dyad/dmc/context.jsonld`, and the check the
guard `dyad/guards/agent/dmc.py` (entity `dmc`, run on every push through `package.py check --guards`). It has
no run-book: its one mechanical step is the guard, which every push already runs.

## Trigger
- A file that defines the outcomes of a recurring decision is added, or its outcomes change: the record is
  written or revised in the same d-work, in the zone of the container that holds it (Rule-1).
- An audit or sweep finds a decision with no record, or a record whose outcomes the home file no longer states.

## Steps
1. **Find the home.** The home is the file that *defines the outcomes*, not one that cites them. When two files
   each define part of a decision, they are two decisions and two records (the authorization each host-action
   class needs is Rule-8's; which actions fall in each class is the sysadmin craft's), each naming the other in
   `dyad:alsoIn` where it helps a reader.
2. **Place it by the home's container.** A home under `dyad/` puts the record in `dyad/dmc/`; under
   `crafts/<craft>/`, in `crafts/<craft>/dmc/`, so the record travels with the craft (Rule-11 property 1); an
   instance file (a preference value, an instance audit), in `<instance>/dmc/`. One record per criterion, never two.
3. **Read the home, then write.** Re-read the home file; state only what it says. The question is
   `dyad:decides`; what it reads is `dyad:inputs`; each outcome is a `DefinedTerm` whose `name` is quoted from
   the home (the guard compares case-insensitively, whitespace collapsed) and whose `dyad:when` and `dyad:then`
   are its condition and consequence. `dyad:precedence` and `dyad:default` are written only where the home
   states them.
4. **Say how it is judged.** `dyad:kind` is `mechanical` when code decides, `inference` when the Agent reads
   and judges, `declared` when a party states it; `dyad:implementation` names the module that decides, or is
   null, with core code or a run-book named in `dyad:alsoIn` instead.
5. **Keep it still.** No date, version, commit sha or address outside the path fields and `dyad:owner`: the
   record states the criterion as it stands, and its history is git's.
6. **Check.** `dyad check --guards` prints the `agent/dmc` line; a failing record names its file and its fault.

## Not decided here
Whether a criterion's outcomes are right, whether its `dyad:kind` is true, and whether a decision deserves a
record at all are inference, judged when the record is written and when its home changes.
