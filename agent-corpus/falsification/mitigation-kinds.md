# Falsification — mitigation kind and mitigation capture

**Claims (Operator, 2026-09-23):** (1) all mitigations are mechanical, that is, coded. (2) For an
inference-based mitigation, it is captured as a run-book or play-book.

Ledger #135. The population is the mitigation inventory compiled for #128 from the code and the Rule
text; every corpus fact below was re-verified in the tree.

## Observed corpus facts
- `dyad/playbooks/` holds exactly one file: `craft-instantiation.md`.
- `dyad/runbooks/` holds exactly one file: `craft.md`, whose own header names it "the steps of the
  craft play-book as `dyad-cmd` blocks" (#165).
- `workstation-corpus/runbooks/` does not exist in this instance; no craft ships a `runbooks/` tree.
- Four Agent Rules declare their Enforcement "Inference only, stated": Rules 5, 8, 9 and 10. Rule-2
  declares "Inference-only, with one mechanical fence"; Rule-13 "Inference for the plan clause";
  Rule-15 "Inference otherwise".

## Claim 1 — "all mitigations are mechanical (i.e. coded)"
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Classify #128's inventory by kind. | **Refuted** | Inference-only mitigations in the inventory: Rule-3's merge-sequence clause (#68), Rule-1's #23 states-the-rest-and-asks clause, Rule-9's easy-agreement trigger, Rule-15 phase 2's re-plan-on-drift, the `ledger-pr-merge` preference, the `delegation` + `concise-mode` pair (#113), and two memory-cache notes. Seven corpus items — the `delegation` + `concise-mode` pair counts two, one preference each — and two cache items, none of them code. |
| 2 | Steel-man: perhaps the mitigations that *work* are the coded ones, and the inference ones are decoration. | **Refuted** | The one sub-mode that has actually gone quiet — merging before the Done-`Y`, silent since 2026-09-18 — is fenced by nothing mechanical at all. What changed was Rule-3's clause and #113's delegation coupling. Meanwhile the coded fences caught two of mode A's nine, both after the act. |
| 3 | Steel-man: read "mitigation" narrowly as "the guards", making the claim true by definition. | **Refuted as empty, and contradicted** | Under that reading the claim says only "the guards are code". The corpus contradicts the wider reading in its own voice: four Rules declare Enforcement "Inference only, stated", and Rule-2 declares one fence against an otherwise inferential rule. |
| 4 | Could every mitigation be coded, so that the claim is at least reachable? | **Refuted for three classes** | A merge is normally `gh pr merge`, a World action, and Rule-14 property 2 fixes that a hosted git service is never kernel, so no package guard runs at that moment; the local `git merge --no-ff` path Rule-14 property 3 keeps for an unreachable hosting is kernel, but no hook is installed for a merge commit, so nothing fences it there either. Rule-5 states outright that no script can decide coherence or orthogonality. Rule-8's read-before-act and Rule-9's attack quality are judgments of meaning, not facts about a file. "All mechanical" is not merely false here, it is unreachable on this kernel. |
| 5 | Grant the claim for the coded subset: is that subset sufficient? | **Refuted** | #128's attack 3 stands: five of nine modes (B, D, E, H, I) have no mechanical fence at any moment, and each fence that exists covers a minority sub-mode. |
| 6 | Where code does exist, does it fire before the fault? | **Survives, scoped** | Almost every fence fires at pre-push over `origin/main..HEAD` — after the act, before publication. Two fire earlier: pre-commit containment, and `dwork state`'s transition refusal at the command. So the coded layer is mostly a publication fence, not a prevention fence, which is what Rule-2's Binding actually asks of it. |

**Verdict 1.** Refuted. The accurate sentence is narrower: the system is mechanical wherever the
kernel can decide a fact about a file, a path or a commit range, and inferential wherever a judgment
or a World action is involved — with Rule-13 governing the boundary, since it makes recurrence
propose code rather than declaring that code already covers everything.

## Claim 2 — "for inference-based mitigation, it's captured as a run-book/play-book"
| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Enumerate the play-books and run-books and see which mitigation each captures. | **Refuted** | One play-book, `craft-instantiation.md`, which decides whether a prompt opens a new craft instance or advises a new dyad system. One core run-book, `craft.md`, which is that play-book's steps. Neither captures a mitigation of any incident mode. No other play-book or run-book exists anywhere in the tree. |
| 2 | Is a run-book even the right container? | **Refuted as a category** | Rule-19's Target is a server instance, and property 1 binds a run-book to one at `<runbooks>/<instance>.md`. A mitigation is not a server instance. The one core run-book is admissible only because #165 made it a play-book's steps, which is the exception, not the pattern. |
| 3 | Is a play-book the right container? | **Survives, scoped** | The vocabulary defines a play-book as an executable procedure the Agent follows for a recurring decision, read by a Rule and never a Rule. Several inference mitigations have exactly that shape — Rule-8's read-before-act, the unencoded "fetch before asserting a ref does not exist" discipline, Rule-1's state-the-collision-and-ask. So the container fits; it has simply never been used for one. |
| 4 | Does any Rule require this capture, so that the claim states a standing discipline? | **Refuted** | No Rule requires it. The one Rule that mandates a play-book at all — Rule-3's Plan clause, for craft instantiation — binds a decision procedure, never a mitigation. Rule-13 prescribes the opposite remedy for recurring inference: property 1 makes the second occurrence yield a code path in the plan, not a play-book. The corpus's own answer to repeated inference is code, and the claim describes a discipline it does not have. |
| 5 | Steel-man: the inference mitigations are captured *somewhere*, and the claim is loose about where. | **Survives, scoped** | They are written down, in three containers with unequal properties. Rule text is corpus, versioned, loaded every session and falsified. The memory cache is per-machine, explicitly not corpus, and demonstrably insufficient — #67 recurred within an hour of its note. The log's "rule learned" sentences are read by no Rule and no command — `agent/references` resolves the log's d-work column and nothing else. None of the three is executable, none records an event, and none is checked *for use*: `rules.py` and `vocabulary.py` check a Rule file's shape and its terms, and nothing anywhere checks that the discipline the text states was followed. |
| 6 | Convert the claim to a proposal: would the capture it describes be worth having? | **Not an attack on claim 2 — the constructive reading, recorded unfalsified** | A play-book's steps are a run-book run through the core runner, which prints the native line, tests the postcondition and appends an event the completion reply cites (the native line, the postcondition and the telemetry are the sysadmin craft's `crafts/sysadmin/rules/server-instances.md` properties 7–9, which Rule-19's Boundaries hold out of its own scope; that the completion reply cites those events is Rule-3's Plan clause; Rule-20 resolves the event references). That is the only shape in the core craft which appends an *event* when a procedure is followed; Rule-18's ops script is the corpus's other mechanical witness — a committed, checked file whose exit code is completion evidence — and nothing here tests whether it would serve a recurring inference decision instead. No answer to "would it be worth having?" could refute a claim about what the corpus holds, so this row records the constructive reading rather than an attack. |

**Verdict 2.** Refuted as a description of the corpus and sound as a proposal. What survives: the
play-book is the right container for a recurring inference *decision*, it has been used exactly once,
for craft instantiation, and no mitigation of any incident mode is captured in one. The reason the
proposal has force is row 6 of the table, which is not an attack but the constructive reading: a
play-book is the core craft's one shape that turns an inference procedure into an event.

## Row opened from this record
#136, `backlog`: capture recurring inference mitigations as play-books whose steps run through the
core runner, so that following one leaves an event. It is row 6 of claim 2's table, the constructive reading
recorded there rather than an attack result — no attack in either table returned Confirmed. Writing any such play-book is that row's own work under its own plan-`Y`.

## Disposition
Surfaced for the Operator; nothing here adopts either claim's proposal or builds anything.
Disposition: see ledger #135.
