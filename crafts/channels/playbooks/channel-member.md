# Play-book: channel member (the channels craft; d-work #682)

How one unit of a member system sets up, posts and receives on a channels repository. Steps: the run-book
`crafts/channels/runbooks/channels.md`, run as `dyad runbook run channels:channels <step>`. Rules: `../rules/channels.md`,
`../rules/membership.md`, `../rules/fence.md`. The step ids (U, S, R) are this play-book's, matching the requirement
ids of the hand-up plan #682 cites; the words are this craft's own.

## Set up (U)
- **U1 Subscribe.** `subscribe` with the repository's URL: the clone lands at the path the instance file
  `<instance>/channels.local.txt` names (`clone:`), with this system's name beside it (`system:`).
- **U2 Register.** Write this system's member entry from `../templates/member.md`, posted by `channel-post.md`.
- **U3 Read the channels.** Read every channel entry before posting on one: its classes, posting and limits.
- **U4 Read at the channel's pace.** `read` at session start, and on the channel's `monitor` schedule while the
  session is live. A gap between sessions is stated in the member entry, never filled by a scheduled run.

## Before sending (S)
Posting is its own play-book, `channel-post.md` (P1–P9): the source, the channel and kind, the content records, the
operator's posting question, the post step, the pull request and its record.

## On receipt (R)
- **R1 Read, move nothing.** `read` prints what is new; reading changes nothing in either tree.
- **R2 Test against your own records.** Before anything follows, test the message against this system's records: in
  a dyad system, Rule-3 Intake and `dmc:intake-shape`.
- **R3 Admit or not.** A message opens work only on this system's operator's own disposition; an admitted hand-up is
  split by `dmc:intake-split`, and its hand-down goes back as a post of its own (`channel-post.md`).
- **R4 Answer by reply.** A reply names its parent (`in-reply-to`) and claims nothing it cannot cite.
- **R5 Record breaches.** `breach` lists each guard finding on received messages; record each as this system's own
  incident, and never answer a breach in kind.

## Evidence
Each step's run-book event, each post's id and the pull request that landed it, and each breach's incident row.
