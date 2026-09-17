# Tended Rules of the sysadmin craft

Operator-tended rules of the system-administration craft: what the dyad *does* on a host, as
opposed to how the dyad runs itself. Any form. They are not Agent Rules (Rule-4 classifies): no
block, no coherence sweep, no Agent-vocabulary discipline; their terms are `../vocabulary/CRAFT.md`.
Each opens with one line naming the core Rule whose kernel reads it; the kernel binds the Agent's
process, the craft rule the craft's practice (#155, attack 3).

| rule | read by | what it holds |
|------|---------|---------------|
| `host-mutation.md` | Rule-8 | the three host-action classes with their examples, the read-before-act procedure, the change log's columns and its guard |
| `ops-scripts.md` | Rule-18 | the form of an Operator-executed command: file name, header, body, provenance, check, idempotence, run-time confirmation (mechanics move to `crafts/syseng/` on #162) |
| `server-instances.md` | Rule-19 | the run-book's form: supervisor, sections, commands, health, telemetry, one execution path, contained mutation; the guards' check list; the reference deployment |

Host-specific Tended Rules (this workstation's constraints) live in `workstation-corpus/rules/`,
outside the craft; Rule-8 reads both before any reversible or destructive host action. A rule here
that binds the Agent's process is an Agent Rule by Rule-4's guard: the Agent obeys it conservatively
and reports the misplacement.
