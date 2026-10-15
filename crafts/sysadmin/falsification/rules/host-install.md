# Falsification record — sysadmin craft rule `host-install.md` (d-work #81)

**Claim:** the sysadmin craft includes the scope for packaging and installation of the Dyad System —
narrowed by its own attacks to: what a host must provide for an install to succeed, how that is
verified, and how the act is authorized, recorded and known complete on a live host, as a Tended
Rule no core kernel reads (adjacent: Rule-11 p2, Rule-8).

Attacks carried from plan #81 (`agent-corpus/d-work/plans/81.md`: the original plan of 2026-09-18,
the re-plan of 2026-09-23, revision 3 of 2026-10-15), by id:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| A1 | Rule-11 already owns packaging and installation; adding sysadmin is shared ownership, which Rule-5 forbids. | Confirmed, scoped | True of a literal reading. Rule-11 and `distribution.md` keep what is distributed and what an install writes; this rule holds what a host must provide and how the act is performed, authorized and recorded on a live host. Different targets; the rule's Boundaries name the seam. |
| A2 | There is no leftover: "packaging and installation" is exactly what Rule-11 names. | Survives, scoped (re-scored by the re-plan; originally *refuted*) | The original refutation rested on one observation — `dyad/bin/dyad` failing on a `python3` below the pin, owned by nobody — which #82 then repaired inside the core with no sysadmin rule. What survives is narrower: the *judgment* behind the repair (plan #82's F2, F3, backlog item 2) was made three times and written nowhere a second host could read. The rule's opening states this case and not the stronger one. |
| A3 | That leftover is Rule-14's — the kernel row already pins Python. | Refuted, scoped | Rule-14 declares the dependency and its Boundaries put the host outside it. Declaring a pin is not owning the act of satisfying it on a machine. The rule's Prerequisites cite the manifest for the pin and own only the satisfying. |
| A4 | Then it is already Rule-8's and needs no new rule. | Survives, scoped | Rule-8 classes and records any host action, install included, and keeps doing so; it says nothing about prerequisites, verification or an install's postcondition. The rule's Authorization section applies Rule-8's classes and the host-mutation rule's columns rather than restating them. |
| A5 | This is a new craft, not an extension. | Refuted | The craft play-book's D3': a craft of this practice exists here, so extend it; no criterion D1–D6 fires. |
| A6 | Siting host-install ownership in a Tended craft leaves it absent on a system that installs only the core. | Refuted, newly | #114 made this craft bundled (Rule-11 p2): `dyad install` writes it. Before 2026-09-22 this attack would have confirmed and the plan never met it. The rule states the fact descriptively (Bundled with the core) and does not raise `MANIFEST.md`'s floor on it. |
| A7 | The craft's `rules/README.md` convention is that each rule opens by naming the core Rule whose kernel reads it; no core Rule cites this one, so the plan's claimed opening ("read by Rule-11 p2, Rule-8") was wrong. | Confirmed | The index gains a second category — craft-owned rules no core kernel reads, `read by` `—`, `adjacent:` naming the neighbours — and the rule opens by saying it is read by no core kernel and which Rules it borders. The reciprocal core citation is a `backlog` row under #81's mandate. |
| A8 | #82 repaired A2's own evidence inside the core without any sysadmin rule, so the leftover needs no rule. | Survives, scoped, weakening | The repair had an owner; the judgment behind it did not and was made three times in one plan without record. The rule is proposed on recurrence (Rule-13 p1), not on a hole in the ownership map. Recorded as a weakening, not argued away; whether recurrence alone justifies a Tended rule was put before the authorizing disposition, not behind it. |
| A9 | The re-plan's question was asked 2026-09-23 and never answered; executing now on the 2026-09-18 `Y` reads silence as consent. | Confirmed as the reason for revision 3's question | Nothing was executed on that silence; revision 3 asked its own authorization on today's tree. |
| A10 | The same 2026-09-18 `Y` said "don't remediate"; executing #81 at all is remediation of the sysadmin craft. | Refuted | That `Y` queued this plan's execution and deferred the *audit's* remediation, which became #84–#89; none of those rows is touched. |
| A11 | Easy agreement with two earlier revisions. | Pushed | A9 is the attack that made revision 3 a question at all; the VERSION line (0.2.1 → 0.3.0), the Rule-4 warning count (3, the two new rules token-free) and the #248 floor warning were read from the tree on the day, not carried. |

Findings stated by the drafting, beside the table: the shell prerequisite is two things, not one —
`/bin/sh` for the entrypoints and `bash` for the hooks and ops scripts — and pydantic, though a
kernel row, is imported by no module today, so the rule names it a prerequisite-in-waiting rather
than one verified before the act.

Disposition: see ledger #81.
