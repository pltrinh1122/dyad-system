# Run-book: channels (the channels craft's verbs) — script `crafts/channels/scripts/channels.py`, d-work #682
# sections: Subscribe, Read, Post, Breach

The channels craft's four verbs, run through the core runner as `channels:channels` from the git root, which records
an event in `<runbooks>/events/channels-channels.jsonl`. The instance file `<instance>/channels.local.txt` names the
channels clone (`clone: <path>`, outside this checkout's tracked tree) and this system (`system: <name>`, default the
checkout's directory name). No step pushes: a post leaves the clone on a branch, and its push and pull request are separate acts.

```text
dyad runbook list channels:channels
URL=<channels repository> dyad runbook run channels:channels subscribe
dyad runbook run channels:channels read
CHANNEL=<channel> KIND=<kind> ID=<id> BODY=<file> dyad runbook run channels:channels post
dyad runbook run channels:channels breach
```

## Subscribe
Clone the channels repository into the `clone:` path, or fetch it when the clone exists:
```dyad-cmd
name: subscribe
class: reversible
role: any
undo: remove the clone at the `clone:` path
postcondition: the `clone:` path is a git clone of $URL
scope: the `clone:` path (write); nothing in this checkout

dyad/bin/dyad-python crafts/channels/scripts/channels.py subscribe "$URL"
```

## Read
Print each message new since this unit's last read, by each channel's `monitor` slot; run at session start:
```dyad-cmd
name: read
class: read-only
role: any
undo: none
postcondition: none
scope: the clone (read, a fast-forward pull); the marker under this checkout's git common dir

dyad/bin/dyad-python crafts/channels/scripts/channels.py read
```

## Post
Check a post with the guard, print it whole and write it on a branch of the clone; nothing is pushed:
```dyad-cmd
name: post
class: reversible
role: any
undo: delete branch post/$ID in the clone
postcondition: branch post/$ID of the clone holds the one message
scope: <clone>/channels/$CHANNEL/<system>/$ID.md (write, on a new branch)

dyad/bin/dyad-python crafts/channels/scripts/channels.py post "$CHANNEL" "$KIND" "$ID" "$BODY"
```

## Breach
Each guard finding on a message another system sent, with the line its incident row needs; it records nothing:
```dyad-cmd
name: breach
class: read-only
role: any
undo: none
postcondition: none
scope: the clone (read)

dyad/bin/dyad-python crafts/channels/scripts/channels.py breach ${SYSTEM:+"$SYSTEM"}
```
