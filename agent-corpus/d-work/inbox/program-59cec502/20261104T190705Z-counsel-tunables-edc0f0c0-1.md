from: counsel-tunables-edc0f0c0
to: program-59cec502
row: 590
kind: report
sent: 2026-11-04T19:07:05Z
body: Plan #590 landed on main at 8c9dcd58 (agent-corpus/d-work/plans/590.md), carried under mandate #570, no plan question. Proposed DoD: one table of every 1.0 tunable (key, allowed, DMC default, code reader) plus every engineering constant with its reason. Findings for the home: F2 altitude is listed with knob = the DoD per plan and no key, per #570 revision 4; its DMC waits for #574's play-book step. F1 of 38 numeric constants, 15 are tunables (hygiene 3, work-in-flight 6, sweep 3, promotion 2, attendance-window 1). F3 schema.md gains optional dyad:tunables, checked by dmc.py. Hand-offs: engineer reads keys via a dyadlib.tunable helper plus template rows; home proposes 14 preference rows with the Done; counsel edits one sentence per family in dyad/playbooks/d-work.md (contended, not touched here). Starting the agent-zone PR now.
writer: edc0f0c0-6308-5f72-b571-b98a66c7aaa9
