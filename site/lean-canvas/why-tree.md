judged: ready (tree 9228fa059768e825e1546f14eeb0948ada4ff427ccb92dd0adb740925d7c7e4e; platform-ops cb5682d1473a2b1b465bf9e938ad69421279da54f0600e1cf1fd50d09df3256d, regulated-engineering 67fc2d50f9658a43b0dab4f117f3b5a7e8673d3a8756f2a19ef9f2dfb3de102e; source platform-ops 7fcba0229140ba033a34595e908fc78532d840b033582e1054d4f4049ed42b6b, regulated-engineering 1b0765f234050d7d8650b6b3765c701b4217534aed461aa71152788b19309f38)
N0 [platform-ops: symptom; H] I can't review every command it wants to run. ⟵ platform-ops:N0
  N1 [platform-ops: symptom; H] There are too many: it proposes commands faster than I can read them. ⟵ platform-ops:N1
    N1.1 [platform-ops: cause; H] Every step of the work reaches me as its own command. ⟵ platform-ops:N1.1
      N1.1.1 [platform-ops: cause; H] The unit of approval is the command, not the change. ⟵ platform-ops:N1.1.1
        N1.1.1.1 [platform-ops: cause; H] The tool can only show me commands; the intent behind them is not something it can put in front of me. ⟵ platform-ops:N1.1.1.1
          N1.1.1.1.1 [platform-ops: root-cause; H] Nothing captures the work's intent as an object I can approve before anything runs. ⟵ platform-ops:N1.1.1.1.1
        N1.1.1.2 [platform-ops: cause; H] The tool asks for approval at the moment of execution, not at the moment of intent. supersedes N1.1.1.1 ⟵ platform-ops:N1.1.1.2
          N1.1.1.2.1 [platform-ops: root-cause, regulated-engineering: root-cause; H] Nothing captures the work's intent as an object I can approve before anything runs. supersedes N1.1.1.1.1 ⟵ platform-ops:N1.1.1.2.1, regulated-engineering:R3.1.1
            removal test [platform-ops, H]: with an approvable intent, N1 and N6 fall away: the reader approves the change once, not each command. ⟵ platform-ops:N1.1.1.2.1
            removal test [regulated-engineering, H]: if what the agent would change were written and agreed first, N11, N11.1 and N9.2.1 fall away; N4.1.1 (for this segment) remains. ⟵ regulated-engineering:R3.1.1
  N2 [platform-ops: symptom; H] Each one is hard to judge: one line doesn't tell me what it will do. ⟵ platform-ops:N2
    N2.1 [platform-ops: cause; H] Its effect depends on the host's state, which the prompt doesn't show. ⟵ platform-ops:N2.1
      N2.1.1 [platform-ops: cause; H] The prompt shows the command, not its target, its risk or its undo. ⟵ platform-ops:N2.1.1
        N2.1.1.1 [platform-ops: root-cause; H] Nothing classes an action by what it risks before it runs. ⟵ platform-ops:N2.1.1.1
          removal test [platform-ops, H]: with every action classed by risk before it runs, N2, N3 and half of N6 fall away: the reader reads the risky ones. ⟵ platform-ops:N2.1.1.1
  N3 [platform-ops: symptom; H] I can't tell which ones matter, so all of them seem to need reading. ⟵ platform-ops:N3
    N3.1 [platform-ops: cause; H] A restart and a delete look the same at the moment I'm asked. ⟵ platform-ops:N3.1
      → N2.1.1.1 [platform-ops] ⟵ platform-ops:N3.1
  N4 [platform-ops: symptom; H] Reading isn't checking: even a command I read, I can't confirm was right. ⟵ platform-ops:N4
    N4.1 [platform-ops: cause; H] Whether it was right only shows in what happens afterwards. ⟵ platform-ops:N4.1
      N4.1.1 [platform-ops: root-cause, regulated-engineering: cause; H] Nothing compares what happened with what was intended before the work is called finished. ⟵ platform-ops:N4.1.1, regulated-engineering:R3.2
        removal test [platform-ops, H]: with the result checked against the intent before the work closes, N4 falls away, and the anchor branch (N7.1) gains the evidence of care it lacks. ⟵ platform-ops:N4.1.1
        → N9.2.1.1 [regulated-engineering] ⟵ regulated-engineering:R3.2
  N5 [platform-ops: symptom; H] What I didn't read, I can't review later either. ⟵ platform-ops:N5
    N5.1 [platform-ops: cause; H] Its output scrolled past and is gone when the session ends. ⟵ platform-ops:N5.1
      N5.1.1 [platform-ops: root-cause, regulated-engineering: root-cause; H] Nothing ties what the agent did to what I approved, and why. ⟵ platform-ops:N5.1.1, regulated-engineering:R0.1.1.1
        removal test [platform-ops, H]: with every action tied to its approval and its reason, N5 falls away, and the anchor branch (N7.1) gains a record to show. ⟵ platform-ops:N5.1.1
        removal test [regulated-engineering, H]: if each approval sat with the identity of the change it approved, N8, N8.1, N8.1.1, N8.2.1, N9.1 and N10.1 fall away and N9 and N10 shrink; N9.2 and N10.2 remain. ⟵ regulated-engineering:R0.1.1.1
  N6 [platform-ops: symptom; H] My attention is spent elsewhere. ⟵ platform-ops:N6
    N6.1 [platform-ops: cause; H] Review effort grows with the number of commands, not with their risk. ⟵ platform-ops:N6.1
      → N1.1.1.2.1 [platform-ops] ⟵ platform-ops:N6.1
      → N2.1.1.1 [platform-ops] ⟵ platform-ops:N6.1
  N7 [platform-ops: cause; H] I feel I must review every one: every unreviewed error is mine to answer for. (the anchor branch) ⟵ platform-ops:N7
    N7.1 [platform-ops: cause; H] Reviewing each command is the only evidence of care I can show. ⟵ platform-ops:N7.1
      → N4.1.1 [platform-ops] ⟵ platform-ops:N7.1
      → N5.1.1 [platform-ops] ⟵ platform-ops:N7.1
      N7.1.1 [platform-ops: anchor, regulated-engineering: anchor; H] I answer for the result. ⟵ platform-ops:N7.1.1, regulated-engineering:R0.3.1.1
N8 [regulated-engineering: symptom; H] An agent's change lands under my name, and I cannot show that I approved it rather than only ran it. ⟵ regulated-engineering:R0
  N8.1 [regulated-engineering: cause; H] My approval was a word in a chat or a click, and it is not in the change record. ⟵ regulated-engineering:R0.1
    N8.1.1 [regulated-engineering: cause; H] The agent's tools keep what was done, not what I was asked and what I answered. ⟵ regulated-engineering:R0.1.1
      → N5.1.1 [regulated-engineering] ⟵ regulated-engineering:R0.1.1
  N8.2 [regulated-engineering: cause; E] The agent and I commit under one identity, so the history cannot tell who proposed from who approved: the system states this of git in `dyad/rules/RULE-2-no-self-ratify.md` (Enforcement). ⟵ regulated-engineering:R0.2
    N8.2.1 [regulated-engineering: cause; H] The only place a separate approver could show is the approval itself, and it is not kept. ⟵ regulated-engineering:R0.2.1
      → N5.1.1 [regulated-engineering] ⟵ regulated-engineering:R0.2.1
  N8.3 [regulated-engineering: cause; H] Why must I show it at all? A change board or an auditor asks, for each change, who approved it and on what. ⟵ regulated-engineering:R0.3
    N8.3.1 [regulated-engineering: cause; H] My sign-off is the control they rely on, and a sign-off they cannot tie to a change counts against me. ⟵ regulated-engineering:R0.3.1
      → N5.1.1 [regulated-engineering] ⟵ regulated-engineering:R0.3.1
      → N7.1.1 [regulated-engineering] ⟵ regulated-engineering:R0.3.1
N9 [regulated-engineering: symptom; H] Before an audit I spend days rebuilding who approved each sampled change from tickets, chats and commit logs. ⟵ regulated-engineering:R1
  N9.1 [regulated-engineering: cause; H] Each tool holds one part: the ticket the request, the chat the answer, git the change. ⟵ regulated-engineering:R1.1
    → N5.1.1 [regulated-engineering] ⟵ regulated-engineering:R1.1
  N9.2 [regulated-engineering: cause; H] Sometimes the change that shipped is not the one that was approved, and I find the difference by hand. ⟵ regulated-engineering:R1.2
    N9.2.1 [regulated-engineering: cause; H] The agent kept working after I said yes, and nothing stopped the newer version. ⟵ regulated-engineering:R1.2.1
      N9.2.1.1 [regulated-engineering: root-cause; H] A yes given on one version of a change still lets a later version through. ⟵ regulated-engineering:R1.2.1.1
        removal test [regulated-engineering, H]: if a yes held only for the version it was given on, N9.2, N9.2.1 and N4.1.1 (for this segment) fall away and N9 shrinks; N8, N9.1 and N10.2 remain. ⟵ regulated-engineering:R1.2.1.1
      → N1.1.1.2.1 [regulated-engineering] ⟵ regulated-engineering:R1.2.1
  N9.3 [regulated-engineering: cause; H] The auditor also asks what was checked before the change shipped, and the check's log has expired. ⟵ regulated-engineering:R1.3
    → N10.2.1.1 [regulated-engineering] ⟵ regulated-engineering:R1.3
  N9.4 [regulated-engineering: cause; H] Why must I rebuild it at all? The auditor samples changes and asks whether what shipped is what was approved. ⟵ regulated-engineering:R1.4
    → N9.2.1.1 [regulated-engineering] ⟵ regulated-engineering:R1.4
    → N7.1.1 [regulated-engineering] ⟵ regulated-engineering:R1.4
N10 [regulated-engineering: symptom; H] I keep the agent off change-controlled work and do that work by hand, so the agent only drafts. ⟵ regulated-engineering:R2
  N10.1 [regulated-engineering: cause; H] Our change process asks for a named approver on each change, and the agent's work gives me nowhere to put one. ⟵ regulated-engineering:R2.1
    → N5.1.1 [regulated-engineering] ⟵ regulated-engineering:R2.1
  N10.2 [regulated-engineering: cause; H] Using it would mean checking every line it wrote, and I do not have that time. ⟵ regulated-engineering:R2.2
    N10.2.1 [regulated-engineering: cause; H] I cannot tell which checks the agent's change already passed, so I check everything again. ⟵ regulated-engineering:R2.2.1
      N10.2.1.1 [regulated-engineering: root-cause; H] What was checked on a change is lost when the check ends, so my review cannot cite it. ⟵ regulated-engineering:R2.2.1.1
        removal test [regulated-engineering, H]: if the checks a change passed stayed with it in a form I can cite, N10.2, N10.2.1 and N9.3 fall away and N10 shrinks; N10.1 remains. ⟵ regulated-engineering:R2.2.1.1
  N10.3 [regulated-engineering: cause; H] Why must I do it by hand at all? If it goes wrong, it is my sign-off on a controlled system. ⟵ regulated-engineering:R2.3
    → N10.2.1.1 [regulated-engineering] ⟵ regulated-engineering:R2.3
    → N7.1.1 [regulated-engineering] ⟵ regulated-engineering:R2.3
N11 [regulated-engineering: symptom; H] The agent changed more than the ticket said, and I found out at review. ⟵ regulated-engineering:R3
  N11.1 [regulated-engineering: cause; H] What I approved was one sentence, and the agent read it wider than I meant. ⟵ regulated-engineering:R3.1
    → N1.1.1.2.1 [regulated-engineering] ⟵ regulated-engineering:R3.1
  → N4.1.1 [regulated-engineering] ⟵ regulated-engineering:R3
  N11.2 [regulated-engineering: cause; H] Why must the scope hold at all? A change outside its approval is an unapproved change on a controlled system. ⟵ regulated-engineering:R3.3
    → N1.1.1.2.1 [regulated-engineering] ⟵ regulated-engineering:R3.3
    → N7.1.1 [regulated-engineering] ⟵ regulated-engineering:R3.3
