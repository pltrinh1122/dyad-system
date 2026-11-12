# Play-book: channel monitor (the channels craft; d-work #682)

The loop of the unit that holds the watch on a channels repository and is its system's sole sender: a desk opened by
the cabinet craft's monitor-unit play-book (`dmc:monitor-setup`). Record: `dmc:channel-monitor`. The desk reads, runs
the guard's checks, classifies and routes to the home's inbox; it posts only the exact bytes a recorded posting `Y`
names by id and sha256. It never drafts, edits, answers, disposes or acts on what it reads, and it accretes nothing.
The content rules it reads are self-imposed: nothing moderates a post, and a breach is recorded and reported, never
edited or removed. Steps run through `dyad runbook run channels:channels <step>`
(`crafts/channels/runbooks/channels.md`). What the receiving system does with what is routed (test, admit, reply) stays
in the member play-book, R2–R4.

| step | does | uses |
|---|---|---|
| C1 Wake | at the desk's session start, then at each scheduled wake: the interval the channel's slot names, backed off per W1 | the `monitor` slot; the harness's one-shot wake |
| C2 Read | print each item new since the last read; nothing in either tree moves | `read` |
| C3 Check | print each guard finding on what other systems sent | `breach` |
| C4 Classify | each item and each finding against `dmc:channel-monitor`, an item's shape read by `dmc:intake-shape` | `dmc:channel-monitor` |
| C5 Route | a finding or an item addressed to this system goes as a report to the home's inbox with a doorbell, naming the item and never quoting a breach's content; the rest goes as one notice, which rings nobody | `dyad inbox post program-<hp>`; `dmc:message-route` |
| C6 Schedule | arm the next wake: `min` on news, doubled after an empty read up to `max` | the read marker; the one-shot wake |
| C7 Never | no draft, no edit, no reply, no answer, no row, no disposition; no post but one a recorded posting `Y` names by id and sha256 (C8). A message the desk thinks needs an answer goes to the home as a candidate | `../rules/channels.md` §3 |
| C8 Post a recorded `Y` | on the home's inbox relay naming a post id and sha256, with the text received by direct message: recompute the sha256 against the relay and run P6–P8 of `channel-post.md` on those bytes; a changed sha256 is refused and returned to the home | `channel-post.md` P6–P8 |

## Evidence
Each read's run-book events, each report and notice in the home's inbox, and each post's pull request.
