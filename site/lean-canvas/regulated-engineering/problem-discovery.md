# Problem discovery: `regulated-engineering`

Segment: engineers whose changes pass change control, an audit or a regulator, and who must show who approved what.
Method: `crafts/chronicle/rules/collateral.md` §6, Steps 1–5. Every line is **H** unless it cites a path.

## 1. Anchor
- **H** When I let an agent change code or configuration on a change-controlled system, I want to trust it enough to answer for the result, so that my sign-off holds up when an auditor asks who approved each change and on what.
- **E** Root anchor: `site/identity.jsonld`, `dyad:problem` (the accountable person must evaluate every delegated output).

## 2. Diverge, by lens (not judged here)
- visibility
  - **H** I cannot see, after the fact, which lines the agent wrote and which I wrote.
  - **H** I cannot see what the agent ran on the way to the change, only the diff it left.
- verifiability
  - **H** I cannot check that the change that shipped is the one I approved.
  - **H** I cannot cite which tests the change passed once the CI log has expired.
- predictability
  - **H** The agent sometimes does more than the ticket says.
  - **H** I do not know, before it starts, which files it will touch.
- reversibility
  - **H** Rolling back an agent's change still needs its own change ticket and approval.
  - **H** I cannot tell which later changes depend on the one I want to undo.
- attribution
  - **H** The agent's commit carries my name, so it looks as if I wrote and approved it.
  - **H** My yes was typed in a chat, and the chat is not part of the change record.
- competence
  - **H** The agent does not know our change procedure or which systems are controlled.
  - **H** It writes plausible code for a domain rule it has misread.
- intent
  - **H** I approved a sentence, and the agent read it wider than I meant.
  - **H** It fixed the symptom the ticket named and changed behaviour the ticket did not mention.
- attention
  - **H** Reviewing every line the agent wrote takes longer than writing it myself.
  - **H** Before an audit I spend days rebuilding the approval trail by hand.
- consequence
  - **H** An unapproved change on a controlled system is an audit finding.
  - **H** A wrong change can stop a release or trigger a report to a regulator.
- accountability to others
  - **H** The change board holds the named approver to account, and that is me.
  - **H** The auditor samples changes and asks for the approval of each one.
- other
  - **H** Our tooling records approvals as a field in a ticket, filled in after the work.
  - **H** So I keep the agent off controlled work and use it only for drafts.

## 3. Decompose
The tree is `why-tree.md` beside this file. Four top-level symptoms, by prevalence (**H**): R0 attribution under my
name, R1 rebuilding the trail before an audit, R2 keeping the agent off controlled work, R3 scope wider than the ticket.
Each has an anchor branch (R0.3, R1.4, R2.3, R3.3) reaching R0.3.1.1, the anchor, directly or by a join.

## 4. Test
Per node (`collateral-problem-depth`): four symptoms, eighteen causes, four root causes (R0.1.1.1, R1.2.1.1,
R2.2.1.1, R3.1.1), one anchor (R0.3.1.1), none solution-shaped (each root is worded as what the segment suffers).
The whole tree (`collateral-why-tree`), in order:
- open-branch: holds. Every leaf is a root cause, the anchor or a join.
- circular: holds. Closest call R0.1.1.1 against R0.1: R0.1 says where the approval lives; R0.1.1.1 says it is not tied to the change's identity, and it explains R1.1 and R2.1, which R0.1 does not.
- too-deep: holds. The deepest branch is three whys.
- no-anchor-branch: holds. Each symptom has one.
- untested: holds. Each root cause has a removal-test line.
- untagged / untested-tag: not applicable as written. This is a one-segment source tree, so every node is `regulated-engineering`; each root has its line.
- stale: holds at writing. No reader evidence has arrived; the header digest matches the lines.
- Outcome: **ready** (H throughout: no reader of the segment has confirmed any node).

## 5. Select
Ranked first by anchor-branch exits, then by joins:
1. **R0.1.1.1** approval kept apart from the change: exits R0's anchor branch; 4 joins (R0.2.1, R0.3.1, R1.1, R2.1).
2. **R1.2.1.1** a yes on one version lets a later version through: exits R1's anchor branch; 2 joins (R1.4, R3.2).
3. **R2.2.1.1** what was checked is lost when the check ends: exits R2's anchor branch; 2 joins (R1.3, R2.3).
- Not selected: R3.1.1 (exits R3's anchor branch; 2 joins: R1.2.1, R3.3). The three-way tie at 2 joins is broken by the prevalence of the symptom whose anchor branch exits through it (R1 > R2 > R3). That tie-break is mine, not the record's.

## 6. Projection (d-work #685)
The source tree above was derived by a fresh drafter briefed with this segment, the anchor, §6's Steps and the gate. The drafter was not given `../why-tree.md` or `../platform-ops/` (the brief is in PR #685's infra PR body). It was then projected into `../why-tree.md` by §6, Adding a segment, step 2.
Each source node was looked up by meaning (inference, stated); every pair can be disputed.

| source | projected | lookup | note |
|---|---|---|---|
| R0.1.1.1 | N5.1.1 | **known** | "approval kept apart from the change" is platform-ops' "nothing ties what the agent did to what I approved": the top root of both segments |
| R3.1.1 | N1.1.1.2.1 | **known** | "it begins changing before what it will change is agreed" is platform-ops' "nothing captures the intent as an object I can approve"; unselected in both segments |
| R3.2 | N4.1.1 | **known**, a different outcome | "nothing compared what landed with what I agreed to" is platform-ops' root N4.1.1; for this segment it is a **cause**, its next why going to R1.2.1.1 (the yes holds across versions) |
| R0.3.1.1 | N7.1.1 | **known** | the anchor |
| R0, R1, R2, R3 | N8, N9, N10, N11 | new | the segment's own top-level symptoms; none matched N0 |
| R1.2.1.1, R2.2.1.1 | N9.2.1.1, N10.2.1.1 | new | roots no platform-ops branch reached |
| every other R node | N8.*–N11.* | new | placed under the projected node its source parent maps to |

Near misses, kept new: R2.2 ("I do not have the time to check every line") against N6 (attention), since one is a cause and the other a
symptom of another act; R0.1 against N5.1 (an approval, not output, is what goes missing).

Result: 4 of the segment's 27 node lines map to known nodes, and 23 are new. N0, `platform-ops`' entry symptom, takes
no `regulated-engineering` tag. The draft that looked up the tree first had tagged it (#685, revision 3).
