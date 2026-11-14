# Prompt Therapy: the phase plan of a new dyad system

**Prompt Therapy v1.0** is a user-agent chat service. A user brings what they saw an AI agent do; the agent matches it
to this canvas set's symptom canon, walks its why-tree with them (asking their why, offering the tree's causes as
hypotheses), reaches the anchor, says what helps, and asks consent before keeping the symptom. **v2.0 and on**: a
multi-user forum (roadmap only). The name, the Operator's (d-work #701, entries 3–4; #702, entry 1), is a working
name: no trademark or domain search has been run. Every page and first message says it is no therapy and no
professional advice (#702, T1).

## Why a separate dyad system
The craft play-book's criteria (`dyad/playbooks/craft-instantiation.md`), on d-work #702:
- **D1 fires**: users' conversations carry names, clients, code and feelings, and this system is public and
  non-sensitive.
- **D5 fires**: those conversations need their own retention and deletion, and a repository's history is permanent.

So Prompt Therapy is its own dyad system, `pltrinh1122/prompt-therapy`, its code under **0BSD**. Its users'
conversations live in the service's own store and never in a repository.

## The phases (each a row of the new system's own ledger)
| phase | definition of done (proposed for that row) |
|---|---|
| **P0 bootstrap** | the core installed into the repository by `system-new` (`dyad/runbooks/craft.md`); the first rows filed |
| **P1 infrastructure** | a PRD, an Architecture and a UX/UI Design, accepted; a service skeleton; a test harness that runs a whole conversation against fixtures with no live provider |
| **P2 adversarial tests** | the Operator's own symptom prompts as fixtures, cited by provenance entry (this system: #696 entries 5, 10, 11, 12, 22; #699 entry 4), each also run reworded, combined, hostile and off-topic; the harness fails a walk that diagnoses, names a person, or keeps a symptom without consent |
| **P3 inference** | one provider interface, each provider an adapter behind it, the choice configuration; a dated price comparison; the cheapest that passes P2 chosen; the key a saved credential, never a file |
| later | the agent's tone and colour (#702, entry 2); self-funding by donation, toward The Dyad Practice Foundation as a non-profit (roadmap only) |

## What lives where (`dmc:intake-split`)
| item | where |
|---|---|
| the symptom canon, the anchor canon, the why-trees and their records | **here**, contained apart from the service (#702, entry 3); the service reads them and never writes them |
| the PRD, Architecture, UX/UI Design, the code, the harness, the adapters | **prompt-therapy** |
| the conversation walk | **prompt-therapy**, authored there; a craft upstream once a second system needs it |
| the adversarial fixtures | **both**: the Operator's words stay in this system's provenance; the fixtures there cite them by entry |
| the consent and de-identification rule | **both**: the rule here (the canon's `agent:` source), its enforcement there |
| users' conversations, the provider key | **neither repository**: the service's store; a saved credential |

## The hand-up, and what it still needs
Only a consented, de-identified symptom, in the user's words, travels up, to be judged by `collateral-symptom-canon`
and `collateral-anchor-canon`. Two gaps stand before it runs:
1. **Rule-3's Intake has no shape for an observation report.** A user's symptom is neither a defect nor an
   enhancement, so Intake would return it. A core change, a row of its own.
2. **No record places a single row in a system.** The table above is a reading.
