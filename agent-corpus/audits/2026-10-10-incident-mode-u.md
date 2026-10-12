# Incident mode U — the World moved

*Per-mode audit of `agent-corpus/audits/INCIDENTS.md`, d-work #259 (2026-10-10); 6 of 140 rows.*

## Definition
Something outside The Dyad System changed state or failed — a hosting write path, a CI integration's
effective permissions, the active account on the host, the machine's available memory, a peer
process's load — and the dyad's act failed, hung, or produced a measurement that was wrong for a
reason the corpus cannot read. Nothing in the tree could have seen it before the act, because
Rule-14 property 4 observes The World and never pins it.

**What would have to change.** The World would have to be observable, or pinned, at the moment of the
act — which is the one thing Rule-14's partition says it is not.

Boundaries against the neighbours it is most easily confused with:
- **T, a stale or partial view of shared state** — Separating test: is the mover part of The Dyad
  System (Operator, Agent, crafts, instance — vocabulary)? T yes, a peer session or the remote's
  refs, which a fetch or a shared allocator would reveal; U no. Boundary row: row 112, where an hour
  of hosting refusals cost an id collision — assigned here because the hosting failure started it
  and the stale view is its consequence (phase 1's primary-mechanism rule).
- **I, verified in one environment, run in another** — I's two environments are both the dyad's and
  both readable: a scratch repo, a container, a CI runner. Separating test: was the difference
  knowable before the act? I yes; U no.
- **C, a value stated from memory instead of read from its source** — Separating test: was the
  authoritative value readable at all? C yes and it was not read; U no.
- **Q, an obligation no mechanism reads** — row 17's "open, unresolved" looks like an unmet
  obligation. Separating test: whose obligation? Q the dyad's, skipped; U nobody's — row 17 is a
  403 from a hosting integration whose cause was never established.

## Incidents (6)
| date | d-work | what happened | why this mode |
|------|--------|---------------|---------------|
| 2026-09-14 | #13, #16 | a tag-push run and a re-dispatched run both failed at the release step with HTTP 403 despite explicit write permissions | the cause was **never established**: the repo setting was changed to write and the identical 403 persisted; still open and unresolved |
| 2026-09-16 | #48 | the suite showed 2 failures then 0 on an identical unchanging tree, and two further runs were killed by the OS for low memory | the host runs several sessions, a local inference server and heavy browser use; memory swung transiently |
| 2026-09-28 | #178 | `gh pr create` refused with `must be a collaborator`; no PR could be opened for the d-work | the active `gh` account on the host had changed to one that is not a collaborator, not by this session |
| 2026-09-29 | #190 | a profile block was measured while a peer session ran the guards and a test discovery in the same container | nothing tells one session that another's suite is running; the presence store records rows and files, not load |
| 2026-10-07 | #232 | the hosting refused every write for about five minutes: three pushes rejected and two PR creations failed, while reads worked | a GitHub-side fault, not an account, credential or guard fault; the same credentials had just worked |
| 2026-10-07 | #234 | a ledger push failed seven times over about an hour, and the hour of held state cost an id collision and a reallocation | the hosting rejected pushes; an hour of blocked pushing is an hour of stale view |

## Pattern
Six rows, five distinct Worlds: a hosting integration's permissions (17), the host machine's memory
under concurrent load (35), the `gh` account configured on the host (65), a peer process's CPU load
corrupting a measurement (74), and the hosting's write path (97, 112). Nothing links them but the
partition they fall on.

What the rows share is the *handling*, not the fault. Every one was absorbed rather than prevented: a
failed check reported as **absent** rather than red (65); both the contended and the quiet
measurement sets published rather than one discarded (74); retries bounded at three rather than
looped, with the completion evidence gathered meanwhile on both heads (97); a reset and a
reallocation, and the Operator told not to archive until a push succeeded (112); no code change made,
because two OS kills at two unrelated tests cannot be one broken test (35); and one left open, with
the cause stated as unknown (17). Row 17's cause cell says so in as many words — "the actual cause is
not yet known" — and this record does not supply one.

Recurrence evidence. Rows 97 and 112 are the same hosting write fault on the same day (2026-10-07,
#232 and #234). The mitigations any consequence cell describes are both Rule text and both were
available and used, so neither is a mitigation that failed: Rule-2's Binding sentence on an absent
check, cited by name in row 65's consequence, and Rule-14 property 3's local-merge path, cited in row
97's ("Had it persisted, the path was Rule-14 property 3's local `git merge --no-ff` on the Done-`Y`
with 'hosting unreachable' stated in the reply, as #178 did"). Row 112's cause cell also calls the
*staleness* consequence "the same failure mode as #178, #223 and #225 in this log", which is mode T's
family, not this one — the cross-reference is to the consequence, and the primary mechanism is the
hosting.

## Mitigations (phase 2)
1. **Rule-14 property 3's local-merge path** — `dyad/rules/RULE-14-system-infrastructure.md:38-52`,
   the clause "When the hosting is unreachable a ratified merge executes locally — `git merge
   --no-ff` of the branch into `main`, commit message citing the PR and the Done-Y — and is pushed
   when the hosting returns … and the completion reply states 'evidence at <sha>, hosting
   unreachable' (#138)"; mirrored in Rule-2's Binding. Moment: inference, stated, in the reply that
   receives the Done-`Y`. **Shipped** as Rule text. Reach: rows 97 and 112 (97 names it), and row 65
   partially — there a PR could not be opened at all, and the branch was pushed and verified while
   the check was reported absent. Does not reach rows 17, 35 or 74. Nothing of this mode recurred
   through it: it was used, and it held.
2. **Rule-2's Binding sentence on an absent check** — "A CI failure that is an account or adapter
   failure (no job started) is not a red check but an absent one, reported as such"
   (`dyad/rules/RULE-2-no-self-ratify.md`, Binding of approval). Moment: inference, stated, in the
   completion reply. **Shipped** as Rule text. Reach: row 65, whose consequence cites it by name, and
   row 17, whose 403 is the same class. Not rows 35, 74, 97, 112.
3. **The kernel-only path itself** — `package.py check --guards` and `--evidence`
   (`dyad/rules/RULE-14-system-infrastructure.md:38-52`; `dyad/hooks/pre-push:4`;
   `dyad/scripts/package.py:583`). Moment: before every push, and on the exact head being merged.
   **Shipped.** It is the structural answer to the whole mode and should be read as such: because
   every guard runs on the kernel alone, no World outage in these six rows left the dyad unable to
   *verify* anything — row 97's completion evidence was gathered while the hosting refused writes. It
   reaches none of the six as a fence against the fault, only as the reason the fault cost no
   verification.
4. **Nothing observes machine load or peer process activity. There is no mechanism at all for rows
   35 and 74.** Row 74's cause cell says it in those words — "nothing tells one session that another
   session's suite is running: the presence store (Rule-16) records rows and touched files … and says
   nothing about machine load". Verified in the code: `dyad/guards/agent/sessions.py:34` declares
   `FIELDS = ("session", "seen", "root", "rows", "files")` — no load, no pid set, no running-command
   field — and the guard is `TRANSACTION = False` (`sessions.py:33`), so it never runs at a push.
   Row 74's own detection was a sub-agent reading `/proc/*/cmdline` by hand, which is not a
   mechanism.
5. **Nothing reads a hosting integration's effective permissions, and row 17 has no mitigation of any
   kind.** Verified: no guard, script or workflow in the tree queries the hosting's permission
   settings; `.github/workflows/dyad-release.yml` declares its own `permissions` and the failure was
   on the hosting's side of that declaration. The row's cause was never established, and this record
   records that rather than closing it.

## Remediation candidate, under attack
Not a fence — the mode admits none — but a *declaration*: a World-observation section printed beside
the evidence block by `dyad check --evidence` (`dyad/scripts/package.py`, the evidence path), naming
the observed state of each World component the merge depends on: hosting reachability, the active
`gh` account, and the machine's load at the moment of the run. It fires on the exact head being
merged, so a reply that says "CI absent" or "measured under load" reports a read value instead of an
inference.

| # | Attack | Result | Survivor |
|---|---|---|---|
| 1 | It puts a network read in `check --evidence`, which Rule-14 property 3 makes the merge evidence and which must run on the kernel alone (`dyad/rules/RULE-14-system-infrastructure.md:38`). A hosting probe means no evidence block when the hosting is down — rows 97 and 112 exactly. | confirmed | A probe whose failure fails the command does not survive. Survivor: the probe's failure *is* the observation ("hosting: unreachable"), never a non-zero exit — the `world`-kind warn pattern of Rule-20 property 2. |
| 2 | It changes the evidence block, which carries "a sha256 of those lines" the Operator may re-run and compare (`evidence block`, vocabulary; `RULE-14:44-48`). World observations are non-deterministic by construction, so the Operator's re-run would never match the block the reply pasted. | confirmed | The World lines cannot be inside the hashed block. Survivor: printed beside it, outside the digest, labelled as observation — which means the candidate changes no byte Rule-2's Binding relies on. |
| 3 | Coverage, with attacks 1 and 2 applied: it reaches row 65 (account), 97 and 112 (reachability) and 74 (load) as *observations*, and rows 35 (a transient OOM at an unknown moment) and 17 (a cause never established) not at all. It prevents nothing in any of the six. | survives (scoped) | Survives only as a reporting improvement that makes four of six rows' reports read rather than inferred. As a fence, refuted — which is the point of proposing it under this mode's exit rather than as its closure. |
| 4 | Easy agreement (Rule-9 Conditions): "the World is unfenceable" was the conclusion reached on first reading, so attack the framing itself. Rule-14 property 1's manifest *does* record versions for World-facing components, so perhaps these faults are pinnable library rows rather than The World. | confirmed | The framing holds. Rule-14 property 4 says The World is "observed, not pinned", and each of the six names a component that partition places there: a hosting API, a host's free memory, a peer process's load, an account. The manifest pins none of them, and `dyad/infrastructure/INFRASTRUCTURE.md:14` pins Git (kernel) and not the hosting. |
| 5 | Attack the exit rather than the candidate: row 35 and row 74 are faults of the *host machine*, which the kernel does contain (Python, Git and the CLI agent all run on it), so exit 3's Rule-14 property 2 reading does not cover them. | survives (scoped) | Correct, and said in the exit below rather than hidden: rows 17, 65, 97 and 112 are hosted-service faults that property 2 covers plainly; rows 35 and 74 are host-contention faults covered only by property 4's observed-never-pinned clause, which is a reading the Operator should dispose. |

## Proposed exit (phase 4)
**Recorded unfenceable on this kernel**, naming `dyad/rules/RULE-14-system-infrastructure.md:37` —
"A hosted git service is never kernel" (property 2) — together with property 4, The World observed
and never pinned.

Rows 17, 65, 97 and 112 are faults living in a hosted service the kernel never contains: a release
integration's effective permissions, the account the hosting authorizes, and the hosting's write
path. No kernel-only mechanism can see any of them before the act, and Rule-14 property 3 forbids
the package depending on a hosting adapter to enforce a Rule, so a probe could only ever report.

Rows 35 and 74 are the scoped part of this exit, and the scope is stated rather than smoothed: they
are contention on the host machine, which the kernel does contain, so property 2's hosted-service
clause does not cover them and only property 4's partition does. Nothing in the corpus reads machine
load today (`sessions.py:33-34`), and whether that is unfenceable or merely unbuilt is a judgment for
the Operator — a load field in the presence store is buildable, and whether a measurement taken under
unknown load is a *fault* or a *limit* is the question underneath it. Row 17 is additionally recorded
as open with its cause never established, exactly as its own cells state.

Proposed only — the mode is not closed here, and the Agent never records an exit as taken (play-book
Conduct; Rule-2).
