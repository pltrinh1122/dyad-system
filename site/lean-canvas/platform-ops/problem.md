# Problem — `platform-ops`

Root causes from `problem-discovery.md` (`crafts/chronicle/rules/collateral.md` §6), ranked. Each keeps its
symptoms beneath it, in the segment's words.

1. **H** (top) Nothing ties what an agent did on a host to what I approved, and why.
   - symptom: **H** "In the postmortem I can't show who decided, me or the agent."
   - symptom: **H** "Its commands scroll past and are gone."
   - symptom: **H** "An auditor asks for a change record I don't have."
2. **H** The only approval I can give is per command, so I approve keystrokes, not intent.
   - symptom: **H** "I can't read every command it wants to run."
   - symptom: **H** "Approving one by one, I end up approving blind."
3. **H** At the moment of approval, every action looks the same, whatever it risks.
   - symptom: **H** "One wrong command takes production down."
   - symptom: **H** "I don't know which of its changes can be undone."

Existing alternatives:
- **H** Approving each command in the agent's own permission prompt.
- **H** Keeping agents off production hosts entirely.
- **H** Infrastructure as code with human review of every change.
