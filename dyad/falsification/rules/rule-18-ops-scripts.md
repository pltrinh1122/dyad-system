# Falsification record — Rule-18 (ops scripts), Operator rule 2026-09-14 (ledger #128)

**Claim (operator, 2026-09-14):** all Operator-executed commands shall be captured as executable
shell files for provenance and verification.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | An inline block pasted into the change log is already provenance. | Refuted | The block is prose in a cell; a file is executable, diffable, syntax-checked (`bash -n`, `ops_scripts.py`), and its commit is the provenance. |
| 2 | The Operator may edit the file before running it; the record lies. | Survives, scoped | The script prints its commit and sha256 first (property 3); the pasted output shows any mismatch; the Agent compares before writing the row and reports a mismatch as an incident (Conduct). |
| 3 | Scripts encourage running without reading. | Survives, scoped | The header states class and undo; `set -x` echoes each command; Rule-8's plan-`Y` / destructive counter-prompt remain per action. |
| 4 | One file per action is clutter. | Refuted | One-to-one with change-log rows is the provenance; #126 yields one file. Slugs and the `<d-work>-<hN>` prefix sort by d-work. |
| 5 | bash is not kernel (Rule-14 p3): a Rule that mandates bash breaks the kernel-only path. | Refuted | Nothing in the package runs them; the guard is `bash -n` via Python's `subprocess` of an already-declared library row (`bash` token, `infrastructure_rules.txt`); `package.py check` Rule-14 passes with no new row. |
| 6 | An Operator-executed command is a sub-case Rule-8 could carry as one bullet; a new Rule is overhead. | Survives, scoped | Rule-8 classes and records; Rule-18 owns a file format and a check — a distinct concern with its own guard (Rule-12 p2). Operator chose a Rule. |
| 7 | Idempotence is unverifiable mechanically; the check is theatre. | Survives, scoped | The check verifies the contract's shape (header, function, three `postcondition` tokens in code); convergence is the Operator's test: run, run again, expect "already satisfied". Stated as inference in property 6. |
| 8 | `sudo` prompts on every guarded command; re-runs annoy. | Refuted | sudo caches credentials for the run; the guard `subvolume show` is itself under sudo once and cached thereafter. |
| 9 | Guards make short scripts long and less legible. | Refuted | One `test \|\| cmd` line per command; `set -x` still echoes what ran; H1 v2 is four mutating lines. |
| 10 | Rewriting a run script loses provenance. | Survives, scoped | Per-commit hash in the change log (property 4); the run text is recoverable by `git show <commit>:<path>` and its sha256. |
| 11 | A postcondition that passes before the script mutates masks a wrong postcondition. | Survives, scoped | The Operator reads the `# postcondition:` line (Conduct: reading before running); the final assert catches a postcondition the commands cannot reach. A token count cannot tell a pre-check from a comment, so the check counts only non-comment lines (test `test_postcondition_in_comments_not_counted`). |
| 12 | The chat `Y` already covers it; a second prompt is friction. | Refuted | The chat `Y` is given before the run, minutes or days earlier, possibly by pasting; the run-time prompt is per step, with the consequence and undo printed at the moment it matters. |
| 13 | A script piped through `tee` cannot prompt. | Refuted | `tee` leaves stdin as the terminal; `read … < /dev/tty` binds to the terminal regardless; (e) fails closed when none exists (cron, ssh without `-t`). |
| 14 | An Operator who types `Y` reflexively gains nothing. | Survives, scoped | The prompt prints consequence and undo, not "continue?"; the class already forced a chat counter-prompt naming the action; reflex is the Operator's, outside what a Rule can fence. |
| 15 | Declined mid-script leaves partial state. | Refuted | Declined steps are skipped, never half-run; property 6 makes the re-run continue from the guards; exit 2 is distinct from a failed postcondition (1). |

Property 6 (idempotent) added 2026-09-14, ledger #131 (attacks 7–11). Property 7 (destructive steps
confirmed at run time) added 2026-09-14, ledger #132 (attacks 12–15).

Deferred, named: shellcheck catches what `bash -n` misses (unquoted expansions, unreachable
code). It is a new World row (Rules 13/14) for a handful of short scripts; deferred until the
script count justifies it. The location `workstation-corpus/ops/` is resolved through one
setting, `DYAD_OPS` (default `workstation-corpus/ops`, relative to the git root), in the manner
of Rule-11 property 3, so an install with another instance layout needs no edit.

## Rule-5 pairwise statements (Rule-18 added; Rule-8 edited)
- 18–8: Rule-8 owns class, authorization, change log; 18 owns delivery form and cites 8; Rule-8
  names 18 in Boundaries and one Conduct bullet (one-way ownership). 18–3: the script is named in
  the plan as the H-row; completion evidence cites its path and outcome; a hash mismatch is a
  Rule-3 incident. 18–11: instance, workstation zone; `ops/*.log` generated (p6); the guard is
  package code with `check_rule_18` registered in the runner. 18–12: `ops_scripts.py` with
  `test_ops_scripts.py` is the mechanical check; scripts' verification tails are host checks, not
  package tests. 18–14: the bash row covers (purpose cell amended); no new dependency. 18–16: no
  row-store change. 18–15: the plan names the script; no phase change. 18–17: no surface. 18–13:
  no import. 18–1: ops scripts are workstation-zone paths (`ZONES` already claims
  `workstation-corpus/`); this PR is agent zone only. 18–2, 18–9, 18–10: no ratification event;
  this record; framing as in the plan. 18–4: block conforms (intent 1, target 1, boundaries 5,
  conditions 4). 18–6: one term, `ops script`, owner 18, used by 8 18. Coherent, orthogonal.

## Rule-5 pairwise statements (property 6, ledger #131)
- 18–8: class, undo, change-log row unchanged; idempotence is delivery form, Rule-18's own; Rule-8
  not edited. 18–12: the new check is package code with tests (p2); the postcondition itself is a
  host check, not a package test. 18–3: a re-run is the same H-row, not a new plan; a hash mismatch
  or a failed final assert is an incident. 18–14: no new dependency. 18–11, 18–1, 18–2, 18–9,
  18–10, 18–13, 18–15, 18–16, 18–17: unchanged from above. 18–4: block counts hold (intent 1,
  target 1, boundaries 5, conditions 4). 18–6: one new term, `postcondition`, owner 18, used by
  18. Coherent, orthogonal.

## Rule-5 pairwise statements (property 7, ledger #132)
- 18–8: Rule-8 owns class, the chat counter-prompt and the change-log row; 18 owns the run-time
  gate as delivery form, citing 8 one-way; Rule-8 not edited. 18–2: no new ratification event —
  the run-time `Y` executes what the chat `Y` disposed (Conduct); Rule-2 untouched. 18–3: a
  declined run (exit 2) is an incident and the row's outcome; exit codes are completion evidence.
  18–12: the check is package code with tests (p2); whether the call precedes the right command is
  inference, stated. 18–14: `read`, `/dev/tty` and `[[ -t 0 ]]` are bash and the OS; no new row.
  18–11, 18–1, 18–9, 18–10, 18–13, 18–15, 18–16, 18–17: unchanged from above. 18–4: block counts
  hold (intent 1, target 1, boundaries 5, conditions 4). 18–6: no new term; `destructive` in
  Rule-8's sense. Coherent, orthogonal.

Disposition: see ledger #128 (Rule); ledger #131 (property 6); ledger #132 (property 7).

## Amendment — d-work #151 (2026-09-14, Rule-21 guard containment)
guard path: `dyad/scripts/ops_scripts.py` → `dyad/guards/workstation/ops_scripts.py`, test under `dyad/tests/guards/workstation/`, runner label `workstation/ops_scripts` (Rule-21). Pairwise: see `rule-21-guard-containment.md`; the Rule's own concern is unchanged.
## Amendment — d-work #155 (2026-09-14, craft extraction R-craft-1)
text moved to `crafts/sysadmin/rules/ops-scripts.md` (#155): Properties 1–7 verbatim (with the #162 mechanics block marked); the guard to `crafts/sysadmin/guards/ops_scripts.py` (label `sysadmin/ops_scripts`, test `crafts/sysadmin/tests/guards/test_ops_scripts.py`); a skeleton at `crafts/sysadmin/templates/ops-script.sh`. Kept: Intent, Target, Boundaries (one added naming the craft rule), Conditions, one property (Form) and Conduct whole (attack 3: never inline, mismatch is an incident, exit codes are evidence). Pairwise: 18–8 unchanged (one-way); 18–19 unchanged (the header vocabulary is now cited as the craft's); 18–4: block holds (intent 1, target 1, boundaries 7, conditions 4); 18–6: `ops script` and `postcondition` left for `CRAFT.md`; 18–11/12/21: the guard and its test are a Tended craft's, discovered by the core runner's second root; 18–14: no new token in the core. Coherent, orthogonal.
