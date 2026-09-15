# Why one naming table

Before #162 the corpus's name patterns were stated in eleven places — Rules 3, 4, 9, 11, 15, 16,
20, the README, the vocabulary and two craft rules — and drifted by hand (#113: a path renamed in
one Rule and not another). A pattern stated twice has two owners; Rule-5 calls that a gap.

`rules/naming.md` is the one table; `guards/naming_rules.txt` is its checkable half as data; the
guard fails when the two disagree (a `kind:` whose pattern the table does not list). A core Rule
keeps the *sentence* — "a row file is `<instance>/d-work/rows/<id>.md`" — because a process Rule
must be readable alone; the table keeps the *shape* and the owner.

Legacy paths are never grandfathered by date: an `allow:` line names the path and its reason, and
the guard fails when the path is gone, so the list can only shrink. Two allow lines exist at
0.1.0: `.github/workflows/server.yml` (an instance workflow, unprefixed by design) and
`dyad/falsification/rules/rule-sets.md` (the record of the two Rule sets, not of one Rule).
