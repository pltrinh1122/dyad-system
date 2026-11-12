# Problem: `regulated-engineering`

Ranked root causes from `why-tree.md` (selection in `problem-discovery.md` §5). Symptoms are in the segment's words.

1. **Top. H** My approval and the change it approved are kept apart, so either can change or vanish without the other. (R0.1.1.1)
   - **H** "An agent's change lands under my name, and I cannot show that I approved it rather than only ran it." (R0)
   - **H** "Before an audit I spend days rebuilding who approved each sampled change." (R1)
   - **H** "I keep the agent off change-controlled work and do that work by hand." (R2)
2. **H** A yes given on one version of a change still lets a later version through. (R1.2.1.1)
   - **H** "Before an audit I spend days rebuilding who approved each sampled change." (R1)
   - **H** "The agent changed more than the ticket said, and I found out at review." (R3)
3. **H** What was checked on a change is lost when the check ends, so my review cannot cite it. (R2.2.1.1)
   - **H** "I keep the agent off change-controlled work and do that work by hand." (R2)
   - **H** "Before an audit I spend days rebuilding who approved each sampled change." (R1)

## Existing alternatives
- **H** An approval field in the change ticket, filled in after the work.
- **H** A review approval on the code-hosting platform's pull request, tied to that platform's account.
- **H** Change board minutes and a spreadsheet of sampled changes, built by hand before each audit.
- **H** Screenshots or exports of the chat in which the yes was given.
- **H** Keeping the agent off controlled work, so every approved change was written by a person.

Record `collateral-lean-canvas-problem`: **ready** (H: every entry is a hypothesis; not-theirs is judged by inference with no reader's words to compare).
