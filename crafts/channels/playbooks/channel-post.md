# Play-book: channel post (the channels craft; d-work #682)

How one unit of a member system takes a post from its source to a landed post. The content rules are self-imposed:
nothing moderates a post (G6), each member holds the rules by its own conduct (K1), and a breach is recorded and
reported, never edited or removed (K3, K4). Records: `dmc:post-content` (every channel), then the channel's own,
`dmc:release-post`, `dmc:request-post`, `dmc:backport-post` or `dmc:issue-post`; each outcome carries the effect its
record declares. Verb: the run-book `crafts/channels/runbooks/channels.md`, step `post`. Rules: `../rules/channels.md`,
`../rules/fence.md`. What comes back is the member play-book's (`channel-member.md`, R1–R5).

| step | does | uses | leaves |
|---|---|---|---|
| P1 Draft from a source | write the draft from one source: a published tag (a release), an operator prompt or provenance entry (a request), a fix commit (a back-port), or an observation with evidence (an issue); a draft with no source is not started | `../templates/message.md` | a draft file; nothing written to the clone |
| P2 Pick channel and kind | name the channel the source belongs on and the kind (`fact`, `proposal`, `reported-disposition`, `question`, `reply`); a reply names its parent in `in-reply-to` | `../rules/channels.md` §2 | the draft's header |
| P3 Read every channel's rules | read the draft against `dmc:post-content`. An outcome that asks for a rewrite (`settles`) sends it back to be rewritten, naming the check, and read again. A fence breach or content not this system's to say (`skips`) drops the draft, and the finding is reported to the operator, naming the check and never quoting the content. Only a draft every check passes (`shapes`) goes on | `dmc:post-content`; `../guards/posts.py` `check_text` decides the mechanical checks | a draft that passes every check, or a report and no draft |
| P4 Read the channel's rules | read it against the channel's own record. A draft for another channel (`settles`) returns to P2; one lacking a part (`settles`) returns to P1 or P2, as the part says; either way it passes P3 again. A draft that meets the channel's record (`shapes`) goes on | `dmc:release-post`, `dmc:request-post`, `dmc:backport-post`, `dmc:issue-post` | a draft for its channel |
| P5 Show it whole and ask | print the post whole, header and body, and ask the operator `Y/N: post <channel>/<id> to <channels repository>?`, on its own and never folded into a plan or Done batch, since it publishes to the world; an `N` sends nothing, and an `N` with text is an amend that returns to P1 | the posting question | the operator's answer, recorded on the row the post serves |
| P6 Write it on a branch | on the operator's `Y`, run the post step: the guard's draft check again, then one commit on branch `post/<id>` of the clone; nothing is pushed | `dyad runbook run channels:channels post` | the branch, and the run-book event |
| P7 Open the pull request | the main agent pushes `post/<id>` and opens one pull request in the channels repository for it, as clerical execution of that `Y`; in a channels repository this system keeps, the main agent merges it on the same `Y` once the guard passes there; in one another system keeps, that system's keeper merges on its own operator's terms, and this system's `Y` covers only the push and the request | the hosting; never a subagent | an open or merged pull request |
| P8 Record it | the row the post served names, in its completion evidence, the post's `channel/id`, its pull request and whether it merged; the post step's event already holds the id, so no new store is kept | the row's completion evidence | the trace from source to landed post |
| P9 Hand on what comes back | a reply, a question or a breach that answers the post goes to the member play-book's receipt steps; nothing here answers it | `channel-member.md` R1–R5 | nothing; handed on |

## Evidence
Each post's source, its records' outcomes as read, the posting question and its answer, the run-book event of `post`,
and its pull request.
