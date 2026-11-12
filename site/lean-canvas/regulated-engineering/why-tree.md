judged: ready (source 1b0765f234050d7d8650b6b3765c701b4217534aed461aa71152788b19309f38)
R0 [symptom; H] An agent's change lands under my name, and I cannot show that I approved it rather than only ran it.
  R0.1 [cause; H] My approval was a word in a chat or a click, and it is not in the change record.
    R0.1.1 [cause; H] The agent's tools keep what was done, not what I was asked and what I answered.
      R0.1.1.1 [root-cause; H] My approval and the change it approved are kept apart, so either can change or vanish without the other.
        removal test [H]: if each approval sat with the identity of the change it approved, R0, R0.1, R0.1.1, R0.2.1, R1.1 and R2.1 fall away and R1 and R2 shrink; R1.2 and R2.2 remain.
  R0.2 [cause; E] The agent and I commit under one identity, so the history cannot tell who proposed from who approved: the system states this of git in `dyad/rules/RULE-2-no-self-ratify.md` (Enforcement).
    R0.2.1 [cause; H] The only place a separate approver could show is the approval itself, and it is not kept.
      → R0.1.1.1
  R0.3 [cause; H] Why must I show it at all? A change board or an auditor asks, for each change, who approved it and on what.
    R0.3.1 [cause; H] My sign-off is the control they rely on, and a sign-off they cannot tie to a change counts against me.
      → R0.1.1.1
      R0.3.1.1 [anchor; H] I answer for the result: my name is on the approval the auditor reads.
R1 [symptom; H] Before an audit I spend days rebuilding who approved each sampled change from tickets, chats and commit logs.
  R1.1 [cause; H] Each tool holds one part: the ticket the request, the chat the answer, git the change.
    → R0.1.1.1
  R1.2 [cause; H] Sometimes the change that shipped is not the one that was approved, and I find the difference by hand.
    R1.2.1 [cause; H] The agent kept working after I said yes, and nothing stopped the newer version.
      R1.2.1.1 [root-cause; H] A yes given on one version of a change still lets a later version through.
        removal test [H]: if a yes held only for the version it was given on, R1.2, R1.2.1 and R3.2 fall away and R1 shrinks; R0, R1.1 and R2.2 remain.
      → R3.1.1
  R1.3 [cause; H] The auditor also asks what was checked before the change shipped, and the check's log has expired.
    → R2.2.1.1
  R1.4 [cause; H] Why must I rebuild it at all? The auditor samples changes and asks whether what shipped is what was approved.
    → R1.2.1.1
    → R0.3.1.1
R2 [symptom; H] I keep the agent off change-controlled work and do that work by hand, so the agent only drafts.
  R2.1 [cause; H] Our change process asks for a named approver on each change, and the agent's work gives me nowhere to put one.
    → R0.1.1.1
  R2.2 [cause; H] Using it would mean checking every line it wrote, and I do not have that time.
    R2.2.1 [cause; H] I cannot tell which checks the agent's change already passed, so I check everything again.
      R2.2.1.1 [root-cause; H] What was checked on a change is lost when the check ends, so my review cannot cite it.
        removal test [H]: if the checks a change passed stayed with it in a form I can cite, R2.2, R2.2.1 and R1.3 fall away and R2 shrinks; R2.1 remains.
  R2.3 [cause; H] Why must I do it by hand at all? If it goes wrong, it is my sign-off on a controlled system.
    → R2.2.1.1
    → R0.3.1.1
R3 [symptom; H] The agent changed more than the ticket said, and I found out at review.
  R3.1 [cause; H] What I approved was one sentence, and the agent read it wider than I meant.
    R3.1.1 [root-cause; H] The agent begins changing things before what it will change is written down and agreed.
      removal test [H]: if what the agent would change were written and agreed first, R3, R3.1 and R1.2.1 fall away; R3.2 remains.
  R3.2 [cause; H] Nothing compared what landed with what I had agreed to.
    → R1.2.1.1
  R3.3 [cause; H] Why must the scope hold at all? A change outside its approval is an unapproved change on a controlled system.
    → R3.1.1
    → R0.3.1.1
