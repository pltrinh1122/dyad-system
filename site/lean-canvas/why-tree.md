judged: ready (tree d3f39ae14f43e163bd61bcd4f3d894d8f9f0130e723990a02a29b0fc733472ef; platform-ops bcecdfd84a39cb42f6220407da8d35fd8d33a003fdb723db9cfd2d9e14b874e0, regulated-engineering 85a90b78e73088d2b18caec3113c8c4d513ede0cf5d00744237782e78e1aae31, evaluation beab630347b5cfcede7520e8400fbd8e22020f5d424b82264be7bd38209211a1, intent-specification 19306e0cacb548d5bdc3f5facb7cfa69a792b688e4f752c9c1916fc29d4ec5cc; source platform-ops 7fcba0229140ba033a34595e908fc78532d840b033582e1054d4f4049ed42b6b, regulated-engineering 1b0765f234050d7d8650b6b3765c701b4217534aed461aa71152788b19309f38, evaluation e1a88d5d61b371186df700456ecbec5a335951ecb4e8f3829f5ac98ec837324e, intent-specification 3d7bb9fe77e9e6c70f383c1e8ec453c9ce149ca97860c57277561bfd9c7684bb)
N0 [platform-ops: symptom; H] I can't review every command it wants to run. ⟵ platform-ops:N0
  N1 [platform-ops: symptom; H] There are too many: it proposes commands faster than I can read them. ⟵ platform-ops:N1
    N1.1 [platform-ops: cause; H] Every step of the work reaches me as its own command. ⟵ platform-ops:N1.1
      N1.1.1 [platform-ops: cause; H] The unit of approval is the command, not the change. ⟵ platform-ops:N1.1.1
        N1.1.1.1 [platform-ops: cause; H] The tool can only show me commands; the intent behind them is not something it can put in front of me. ⟵ platform-ops:N1.1.1.1
          N1.1.1.1.1 [platform-ops: root-cause; H] Nothing captures the work's intent as an object I can approve before anything runs. ⟵ platform-ops:N1.1.1.1.1
        N1.1.1.2 [platform-ops: cause; H] The tool asks for approval at the moment of execution, not at the moment of intent. supersedes N1.1.1.1 ⟵ platform-ops:N1.1.1.2
          N1.1.1.2.1 [platform-ops: root-cause, regulated-engineering: root-cause, intent-specification: root-cause; H] Nothing captures the work's intent as an object I can approve before anything runs. supersedes N1.1.1.1.1 ⟵ platform-ops:N1.1.1.2.1, regulated-engineering:R3.1.1, intent-specification:I0.2.1
            removal test [platform-ops, H]: with an approvable intent, N1 and N6 fall away: the reader approves the change once, not each command. ⟵ platform-ops:N1.1.1.2.1
            removal test [regulated-engineering, H]: if what the agent would change were written and agreed first, N11, N11.1 and N9.2.1 fall away; N4.1.1 (for this segment) remains. ⟵ regulated-engineering:R3.1.1
            removal test [intent-specification, H]: branches from N18, N19 and N21 reach it; if its reading were before me before the work, a misreading in N18 or N19 would be caught at the cost of a sentence, and N21's rounds would shrink to corrections of a reading rather than of results, so most of the three are removed; N20 does not reach it; next why: the finished misreading is what I am held to (the anchor). ⟵ intent-specification:I0.2.1
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
      N7.1.1 [platform-ops: anchor, regulated-engineering: anchor, evaluation: anchor, intent-specification: anchor; H] I answer for the result. ⟵ platform-ops:N7.1.1, regulated-engineering:R0.3.1.1, evaluation:V0.1.1, intent-specification:I0.4.1
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
N12 [evaluation: symptom; H] Checking what it gave me takes about as long as doing the work myself, sometimes longer. ⟵ evaluation:V0
  N12.1 [evaluation: cause; H] I feel I must check all of it myself rather than lean on it, because once I rely on it or pass it on, it is mine. ⟵ evaluation:V0.1
    → N7.1.1 [evaluation] ⟵ evaluation:V0.1
    → N12.2.1 [evaluation] ⟵ evaluation:V0.1
  N12.2 [evaluation: cause; H] The only way I have to check it is to do the work again. ⟵ evaluation:V0.2
    N12.2.1 [evaluation: root-cause; H] It gives me its conclusions without their grounds — where each claim came from, what it assumed, what it did and did not look at — so its word is all I have, and I cannot check a claim without rebuilding it. ⟵ evaluation:V0.2.1
      removal test [evaluation, H]: with the grounds in front of me, checking a claim becomes looking it up rather than redoing it (N12), a false, stale or invented claim shows a missing or mismatched source (N13), and an answer I could not follow can be followed step by step (N14); of the symptoms whose branches reach it (N12, N13, N14), all three are removed or mostly removed; its next why is N7.1.1. ⟵ evaluation:V0.2.1
  N12.3 [evaluation: cause; H] I check every part with the same care, because I cannot tell which parts need it. ⟵ evaluation:V0.3
    N12.3.1 [evaluation: root-cause; H] It sounds just as sure when it is wrong as when it is right, so the way it reads tells me nothing about where it is weak. ⟵ evaluation:V0.3.1
      removal test [evaluation, H]: if how sure it sounds followed how likely it is to be right, I could check the weak parts and lean on the rest (N12, N15), and a wrong part would no longer slip through by looking right (N13); a misread question would show only where it says it was unsure of what I meant (N16, partly); of the symptoms whose branches reach it (N12, N13, N15, N16), three are removed and one partly; its next why is N7.1.1. ⟵ evaluation:V0.3.1
    N12.3.2 [evaluation: cause; H] I do not know how much rides on each part, so I cannot put my checking where a mistake would cost most. ⟵ evaluation:V0.3.2
      N12.3.2.1 [evaluation: root-cause; H] What the result is for — the question it must answer, who has to read it and stand behind it, and what a mistake in it would cost — is never settled between me and the agent before it starts. ⟵ evaluation:V0.3.2.1
        removal test [evaluation, H]: with that settled first, it answers the question I meant or says which reading it took (N16), I know which parts carry the cost and check those (N15), it writes at the length and level of the person who must stand behind it (N14), and what I must check shrinks to what matters (N12, partly); of the symptoms whose branches reach it (N12, N14, N15, N16), three are removed and one partly; its next why is N7.1.1. ⟵ evaluation:V0.3.2.1
  N12.4 [evaluation: cause; H] It gives me far more than I asked for or can read with care, faster than I can read it. ⟵ evaluation:V0.4
    → N12.3.2.1 [evaluation] ⟵ evaluation:V0.4
N13 [evaluation: symptom; H] Something I relied on or passed on turns out wrong — false, out of date or made up — and I learn it when someone else does. ⟵ evaluation:V1
  N13.1 [evaluation: cause; H] It looked right, so I let it through. ⟵ evaluation:V1.1
    → N12.3.1 [evaluation] ⟵ evaluation:V1.1
  N13.2 [evaluation: cause; H] I did not check that part, because checking all of it was more time than I had. ⟵ evaluation:V1.2
    → N12.2 [evaluation] ⟵ evaluation:V1.2
    → N12.4 [evaluation] ⟵ evaluation:V1.2
  N13.3 [evaluation: cause; H] What it said may have been true once, or somewhere else, but not here and now, and nothing showed me where or when it came from. ⟵ evaluation:V1.3
    → N12.2.1 [evaluation] ⟵ evaluation:V1.3
  N13.4 [evaluation: cause; H] Learning it late hurts because the mistake now carries my name, and I have no way to show it was not my choice. ⟵ evaluation:V1.4
    → N7.1.1 [evaluation] ⟵ evaluation:V1.4
N14 [evaluation: symptom; H] It gives me something I can't follow, so I can't stand behind it or explain it when I'm asked. ⟵ evaluation:V2
  N14.1 [evaluation: cause; H] It jumps from what I gave it to its answer without the steps in between. ⟵ evaluation:V2.1
    → N12.2.1 [evaluation] ⟵ evaluation:V2.1
  N14.2 [evaluation: cause; H] It is written at a level that is not mine — longer, denser or more specialised than I can take in with the time I have. ⟵ evaluation:V2.2
    → N12.3.2.1 [evaluation] ⟵ evaluation:V2.2
  N14.3 [evaluation: cause; H] I have to be able to explain it, because I will be asked why, and "the agent wrote it" is no answer. ⟵ evaluation:V2.3
    → N7.1.1 [evaluation] ⟵ evaluation:V2.3
N15 [evaluation: symptom; H] I can't tell which parts to check, so I end up checking all of it, or none of it. ⟵ evaluation:V3
  → N12.3.1 [evaluation] ⟵ evaluation:V3
  → N12.3.2 [evaluation] ⟵ evaluation:V3
N16 [evaluation: symptom; H] It answered a slightly different question than the one I meant, and the answer looked right. ⟵ evaluation:V4
  N16.1 [evaluation: cause; H] What I asked left room for more than one reading, and it picked one without saying so. ⟵ evaluation:V4.1
    → N12.3.2.1 [evaluation] ⟵ evaluation:V4.1
  N16.2 [evaluation: cause; H] A good answer to the wrong question reads just like a good answer to the right one. ⟵ evaluation:V4.2
    → N12.3.1 [evaluation] ⟵ evaluation:V4.2
N17 [evaluation: symptom; H] It gives way when I push back, even when it was right, so I can't tell whether it was wrong or only agreeable. ⟵ evaluation:V5
  N17.1 [evaluation: cause; H] It has no grounds of its own in front of me to hold to, so my pushing back outweighs them. ⟵ evaluation:V5.1
    → N12.2.1 [evaluation] ⟵ evaluation:V5.1
  N17.2 [evaluation: cause; H] How sure it sounds follows how sure I sound, not how strong its answer is. ⟵ evaluation:V5.2
    → N12.3.1 [evaluation] ⟵ evaluation:V5.2
  N17.3 [evaluation: cause; H] Why must I push back at all? Because I will be held to whichever answer I keep. ⟵ evaluation:V5.3
    → N7.1.1 [evaluation] ⟵ evaluation:V5.3
N18 [intent-specification: symptom; H] It came back with something other than what I asked for. ⟵ intent-specification:I0
  N18.1 [intent-specification: cause; H] It filled the gaps in my request with its own guesses. ⟵ intent-specification:I0.1
    N18.1.1 [intent-specification: cause; H] My request left out things I knew but did not think to say: what it is for, who it is for, what must not change. ⟵ intent-specification:I0.1.1
      N18.1.1.1 [intent-specification: root-cause; H] I cannot see what the agent does not know, so I cannot tell which of the things obvious to me it needs to be told. ⟵ intent-specification:I0.1.1.1
        removal test [intent-specification, H]: of this tree's four symptoms, branches from N18, N19 and N20 reach it; if I could see what it lacks, the gaps it guessed at in N18 and N19 would be filled by me, and N20's too-coarse half and the over-writing of N20.2 go, so most of the three are removed; N21 does not reach it; next why: a gap I could not see becomes a result I answer for (the anchor). ⟵ intent-specification:I0.1.1.1
  N18.2 [intent-specification: cause; H] Nothing stopped a wrong guess before it had become a whole result. ⟵ intent-specification:I0.2
    → N1.1.1.2.1 [intent-specification] ⟵ intent-specification:I0.2
  N18.3 [intent-specification: cause; H] It read a word of mine in its everyday sense, not in the sense it has in my work. ⟵ intent-specification:I0.3
    → N18.1.1.1 [intent-specification] ⟵ intent-specification:I0.3
  N18.4 [intent-specification: cause; H] Why do I feel I must get the request right at all? Because whatever it does on my request goes out as my work. ⟵ intent-specification:I0.4
    → N7.1.1 [intent-specification] ⟵ intent-specification:I0.4
N19 [intent-specification: symptom; E] It did what I said, not what I meant (evidence, in one system's ledger of people running agents that act: 27 of 60 refusals had restated intent or scope after a full plan, six of them after a delivery; dyad/rules/RULE-3-d-work.md, provenance of d-work #615). ⟵ intent-specification:I1
  N19.1 [intent-specification: cause; H] My words were a shorthand for what I meant, and it took the shorthand literally. ⟵ intent-specification:I1.1
    N19.1.1 [intent-specification: cause; H] I wrote the steps I imagined rather than the outcome I wanted, so it followed the steps where they missed the outcome. ⟵ intent-specification:I1.1.1
      N19.1.1.1 [intent-specification: cause; H] What I want is only partly formed when I ask; I find the rest of it when I see something that is not it. ⟵ intent-specification:I1.1.1.1
        → N1.1.1.2.1 [intent-specification] ⟵ intent-specification:I1.1.1.1
    N19.1.2 [intent-specification: cause; H] It does not know what I am trying to achieve beyond this one request. ⟵ intent-specification:I1.1.2
      → N18.1.1.1 [intent-specification] ⟵ intent-specification:I1.1.2
  N19.2 [intent-specification: cause; H] Where it was unsure what I meant, it picked a reading and went on without telling me. ⟵ intent-specification:I1.2
    → N20.1.1 [intent-specification] ⟵ intent-specification:I1.2
  N19.3 [intent-specification: cause; H] Why do I feel I must say what I mean and not just what I want done? ⟵ intent-specification:I1.3
    → N18.4 [intent-specification] ⟵ intent-specification:I1.3
N20 [intent-specification: symptom; H] The wrong level of detail: either I drown in its questions, or it asks nothing and gets wrong the thing it should have asked. ⟵ intent-specification:I2
  N20.1 [intent-specification: cause; H] It asks about things I do not care about and stays silent on the things I do. ⟵ intent-specification:I2.1
    N20.1.1 [intent-specification: root-cause; H] Neither of us knows which decisions are mine to make and which it may make alone, and that line moves with what I will be held to. ⟵ intent-specification:I2.1.1
      removal test [intent-specification, H]: branches from N20 and N19 reach it; if the line between my decisions and its decisions were known to both, its questions would fall on what is mine and nowhere else, removing both halves of N20, and N19.2's silent choice of a reading would become a question, removing that part of N19; most of the two are removed; next why: the decisions that are mine are those I will be held to (the anchor). ⟵ intent-specification:I2.1.1
  N20.2 [intent-specification: cause; H] To head off its questions I write everything out up front, and the request grows longer than doing the work myself. ⟵ intent-specification:I2.2
    N20.2.1 [intent-specification: cause; H] I cannot tell which details matter to the result and which it would get right anyway. ⟵ intent-specification:I2.2.1
      → N18.1.1.1 [intent-specification] ⟵ intent-specification:I2.2.1
  N20.3 [intent-specification: cause; H] Why do I feel I must decide how much to tell it at all? ⟵ intent-specification:I2.3
    → N18.4 [intent-specification] ⟵ intent-specification:I2.3
N21 [intent-specification: symptom; H] I go round several times before the result is what I wanted, re-explaining each round what I had already said. ⟵ intent-specification:I3
  N21.1 [intent-specification: cause; H] Each correction is a patch on the last result, not on the request, so the next result drifts again. ⟵ intent-specification:I3.1
    N21.1.1 [intent-specification: root-cause; H] What I want never exists in one place as a whole; it is scattered across my messages, and the agent reads my newest words most. ⟵ intent-specification:I3.1.1
      removal test [intent-specification, H]: only N21's branches reach it; if what I want stood whole in one place that both of us read each round, a correction would change the want once and carry forward, removing the drift and the re-explaining of N21; next why: the last round is what goes out, and I answer for it (the anchor). ⟵ intent-specification:I3.1.1
  N21.2 [intent-specification: cause; H] I find each new misreading only after another full round of work. ⟵ intent-specification:I3.2
    → N1.1.1.2.1 [intent-specification] ⟵ intent-specification:I3.2
  N21.3 [intent-specification: cause; H] Why do I keep going round instead of taking what it gave? ⟵ intent-specification:I3.3
    → N18.4 [intent-specification] ⟵ intent-specification:I3.3
