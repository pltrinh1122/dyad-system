judged: ready (tree 3dff592e0d076e91e24218ac579c82e9ee436501c1af57d9fddd40e082303e1d; platform-ops 3dff592e0d076e91e24218ac579c82e9ee436501c1af57d9fddd40e082303e1d)
N0 [platform-ops: symptom; H] I can't review every command it wants to run.
  N1 [platform-ops: symptom; H] There are too many: it proposes commands faster than I can read them.
    N1.1 [platform-ops: cause; H] Every step of the work reaches me as its own command.
      N1.1.1 [platform-ops: cause; H] The unit of approval is the command, not the change.
        N1.1.1.1 [platform-ops: cause; H] The tool can only show me commands; the intent behind them is not something it can put in front of me.
          N1.1.1.1.1 [platform-ops: root-cause; H] Nothing captures the work's intent as an object I can approve before anything runs.
        N1.1.1.2 [platform-ops: cause; H] The tool asks for approval at the moment of execution, not at the moment of intent. supersedes N1.1.1.1
          N1.1.1.2.1 [platform-ops: root-cause; H] Nothing captures the work's intent as an object I can approve before anything runs. supersedes N1.1.1.1.1
            removal test [platform-ops, H]: with an approvable intent, N1 and N6 fall away: the reader approves the change once, not each command.
  N2 [platform-ops: symptom; H] Each one is hard to judge: one line doesn't tell me what it will do.
    N2.1 [platform-ops: cause; H] Its effect depends on the host's state, which the prompt doesn't show.
      N2.1.1 [platform-ops: cause; H] The prompt shows the command, not its target, its risk or its undo.
        N2.1.1.1 [platform-ops: root-cause; H] Nothing classes an action by what it risks before it runs.
          removal test [platform-ops, H]: with every action classed by risk before it runs, N2, N3 and half of N6 fall away: the reader reads the risky ones.
  N3 [platform-ops: symptom; H] I can't tell which ones matter, so all of them seem to need reading.
    N3.1 [platform-ops: cause; H] A restart and a delete look the same at the moment I'm asked.
      → N2.1.1.1 [platform-ops]
  N4 [platform-ops: symptom; H] Reading isn't checking: even a command I read, I can't confirm was right.
    N4.1 [platform-ops: cause; H] Whether it was right only shows in what happens afterwards.
      N4.1.1 [platform-ops: root-cause; H] Nothing compares what happened with what was intended before the work is called finished.
        removal test [platform-ops, H]: with the result checked against the intent before the work closes, N4 falls away, and the anchor branch (N7.1) gains the evidence of care it lacks.
  N5 [platform-ops: symptom; H] What I didn't read, I can't review later either.
    N5.1 [platform-ops: cause; H] Its output scrolled past and is gone when the session ends.
      N5.1.1 [platform-ops: root-cause; H] Nothing ties what the agent did to what I approved, and why.
        removal test [platform-ops, H]: with every action tied to its approval and its reason, N5 falls away, and the anchor branch (N7.1) gains a record to show.
  N6 [platform-ops: symptom; H] My attention is spent elsewhere.
    N6.1 [platform-ops: cause; H] Review effort grows with the number of commands, not with their risk.
      → N1.1.1.2.1 [platform-ops]
      → N2.1.1.1 [platform-ops]
  N7 [platform-ops: cause; H] I feel I must review every one: every unreviewed error is mine to answer for. (the anchor branch)
    N7.1 [platform-ops: cause; H] Reviewing each command is the only evidence of care I can show.
      → N4.1.1 [platform-ops]
      → N5.1.1 [platform-ops]
      N7.1.1 [platform-ops: anchor; H] I answer for the result.
