# cabinet guards

One guard, `seats.py` (entity `seat`, corpus `agent`), meeting the guard contract (`crafts/sysarch/rules/guards.md`;
`dyad check --list` shows it as `cabinet/seats`), its data `seats_rules.txt` beside it and its test at
`../tests/guards/test_seats.py`. Advisory by construction: it counts presence files outside the seat form and reads
the mandates table against the template's columns, and never fails a push (Rule-16 Presence: a presence file is a
claim, not a lock; the names from before the form are history the store keeps).
