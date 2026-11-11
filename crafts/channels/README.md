# channels — messages between dyad systems over a shared repository (Tended craft, `crafts/channels/`, zone `craft`)

Dyad systems that install this craft subscribe to a shared, public channels repository and exchange messages there:
a release channel each upgrade is read from, request and back-port channels for enhancements and offered fixes, and
an issue channel for defects. A message carries information, never authority: what a system receives is an intake its
own operator admits or not (Rule-3 Intake). The craft defines the canonical message format, `dyad-channels/1`, kept
general — few required fields, any unknown field kept — so another system's records conform to it. Authored in
dyad-system under d-work #682, a clean-room implementation; it requires the core only (`MANIFEST.md`). Version
`VERSION` (0.1.0). Not bundled with the core: no core Rule cites this craft by path.

| path | holds |
|------|-------|
| `templates/message.md` | the message record, `channels/<channel>/<system>/<id>.md`: required `format`, `id`, `channel`, `kind`, `from`, `sent`; optional `holder`, `in-reply-to`, `refs`; then the body |
| `templates/channel.md` | a channel's registry entry, `registry/channels/<channel>.md`: creator, owner, sources and the policy slots (admission, posting, monitor, limits, decision-rights) |
| `templates/member.md` | a member's registry entry, `registry/members/<system>.md`: system, units, bound repository, play-book version |
| `guards/posts.py` | the guard (entity `post`, corpus `craft`), over the clone `<instance>/channels.local.txt` names (`clone:`): record shape, kinds, membership, replies, paths, size limits, append-only, and the world-facing fence (credentials, private names by hash, disposition shapes); its `check_text` is the check a post passes before it is written |
| `scripts/channels.py` | the verbs `subscribe`, `read` (by each channel's monitor slot; the marker under the git common dir), `post` (checked, printed, written on a branch, never pushed) and `breach` (findings on received messages, recorded by the agent) |
| `runbooks/channels.md` | the verbs as the run-book `channels:channels`, run through the core runner |
| `tests/` | the guard and the verbs |
