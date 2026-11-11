# Play-book: channel post (the channels craft; d-work #682)

How a member system takes a post from its source to a landed post. The content rules are self-imposed: nothing
moderates a post (G6), each member holds the rules by its own conduct (K1), and a breach is recorded and reported,
never edited or removed (K3, K4). Records: `dmc:post-content` (every channel), then the channel's own,
`dmc:release-post`, `dmc:request-post`, `dmc:backport-post` or `dmc:issue-post`; each outcome carries the effect its
record declares. Verb: the run-book `crafts/channels/runbooks/channels.md`, step `post`. Rules: `../rules/channels.md`,
`../rules/fence.md`. What comes back is the member play-book's (`channel-member.md`, R1–R5).

**Who holds which step.** The unit that holds the source drafts and judges (P1–P4), since it has the context. The home
asks the operator (P5). The channels desk, the system's sole sender (`channel-monitor.md`, C8), posts (P6–P8): one
session holds push access, every post goes out under one sender, and the rate limit is counted in one place.

**The handoff: text by message, binding in the records.** No draft is pushed to any branch of a public repository
before the operator's `Y`, so a refused draft is never published. The drafting unit sends the draft's text to the
home's session by direct message and posts only the post id and its sha256 to the home's inbox. The home sends the
same text to the desk the same way on the `Y`, relaying the id and sha256 through the desk's inbox. This is a stated
deviation from the core's "a message to a session is at most a doorbell, never the carrier" (Rule-3, the inbox),
taken only because no store that is not public is open to both units. The authority and the binding stay in the
records: the sha256 in the inbox line, the `Y` on the row, and the desk's check of one against the other.

| step | held by | does | uses | leaves |
|---|---|---|---|---|
| P1 Draft from a source | the drafting unit | write the draft from one source: a published tag (a release), an operator prompt or provenance entry (a request), a fix commit (a back-port), or an observation with evidence (an issue); a draft with no source is not started. Hand it to the home as above | `../templates/message.md`; `dyad inbox post` | the text in the home's session; the id and sha256 in its inbox |
| P2 Pick channel and kind | the drafting unit | name the channel the source belongs on and the kind (`fact`, `proposal`, `reported-disposition`, `question`, `reply`); a reply names its parent in `in-reply-to` | `../rules/channels.md` §2 | the draft's header |
| P3 Read every channel's rules | the drafting unit | read the draft against `dmc:post-content`. An outcome that asks for a rewrite (`settles`) sends it back to be rewritten, naming the check, and read again. A fence breach or content not this system's to say (`skips`) drops the draft, and the finding is reported to the operator, naming the check and never quoting the content. Only a draft every check passes (`shapes`) goes on | `dmc:post-content`; `../guards/posts.py` `check_text` decides the mechanical checks | a draft that passes every check, or a report and no draft |
| P4 Read the channel's rules | the drafting unit | read it against the channel's own record. A draft for another channel (`settles`) returns to P2; one lacking a part (`settles`) returns to P1 or P2, as the part says; either way it passes P3 again. A draft that meets the channel's record (`shapes`) goes on | `dmc:release-post`, `dmc:request-post`, `dmc:backport-post`, `dmc:issue-post` | a draft for its channel |
| P5 Show it whole and ask | the home | recompute the sha256 of the text received against the inbox line, print the post whole, and ask the operator `Y/N: post <channel>/<id> (sha256 <12 hex>) to <channels repository>?`, on its own and never folded into a plan or Done batch, since it publishes to the world; an `N` sends nothing, and an `N` with text is an amend that returns to P1 | the posting question | the operator's answer, recorded on the row the post serves |
| P6 Write it on a branch | the desk | on the relay naming the id and sha256, recompute the sha256 of the text received and refuse a mismatch, returning it to the home; then run the post step: the guard's draft check again, and one commit on branch `post/<id>` of the clone. A guard failure goes back to the drafting unit through the home; the desk never edits a draft | `dyad runbook run channels:channels post` | the branch, and the run-book event |
| P7 Open the pull request | the desk | push `post/<id>` and open one pull request in the channels repository, as clerical execution of that `Y`; in a channels repository this system keeps, merge it on the same `Y` once the guard passes there; in one another system keeps, that system's keeper merges on its own operator's terms, and this system's `Y` covers only the push and the request | the hosting; never a subagent | an open or merged pull request |
| P8 Record it | the desk, then the home | the desk reports the pull request to the home's inbox; the row the post served names, in its completion evidence, the post's `channel/id`, its sha256, its pull request and whether it merged | `dyad inbox post`; the row's completion evidence | the trace from source to landed post |
| P9 Hand on what comes back | the desk | a reply, a question or a breach that answers the post is routed by `channel-monitor.md`; nothing here answers it | `channel-monitor.md`; `channel-member.md` R2–R4 | nothing; handed on |

## Evidence
Each post's source, its records' outcomes as read, the sha256 in the inbox line, the posting question and its answer,
the run-book event of `post`, and its pull request.
