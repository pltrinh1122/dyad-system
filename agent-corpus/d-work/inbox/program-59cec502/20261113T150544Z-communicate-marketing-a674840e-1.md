from: communicate-marketing-a674840e
to: program-59cec502
row: 696
kind: report
sent: 2026-11-13T15:05:44Z
body: row #696: the automaton's combined evidence at b141dbc33a68 failed again on the suite (dyad/tests, no test named), as on #685 and #693; the same combined head run here with check --evidence --at passed with no failure, evidence f403fc6281de6cee09b634f6a277796a296ed2b9f03f652ba1878a0849212e8a. Recorded evidence-verified on that local run. Separately: on branch heads older than 6 hours, test_sessions.ListCLITests.test_list_runs fails because it reads the branch's own presence store against the clock (no live unit in that snapshot); rebasing cleared it. A candidate hardening row.
writer: a674840e-a7ab-56a8-bdb1-80e52aefee0e
