# Problem — `platform-ops`

1. **H** (top) "If the agent runs the wrong command on a host, I'm the one who gets paged, and I can't read every command it wants to run."
2. **H** "After the fact I can't tell what the agent changed on the host, or why."
3. **H** "Approving each command one by one is so slow that I end up approving them blind."

Existing alternatives:
- **H** Approving each command in the agent's own permission prompt.
- **H** Keeping agents off production hosts entirely.
- **H** Infrastructure as code with human review of every change.
