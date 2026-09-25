# Producing a disclosure (generic; no host values)

The procedure is the play-book's; this is the reviewer's side of it — what to look at before a document
is released, in an order that puts the cheap checks first.

1. **Does it name its reader?** A document without an audience cannot be matched to the disposition
   that released it (rule property 5).
2. **Does it carry a watermark?** `covered through: <n> rows, latest <date>`. Two documents without
   watermarks cannot be told apart, and a stale one will be read as current (property 5).
3. **Does the gate pass on the file as written**, not on the text that was assembled?
   `redaction.py verify <file>` — run it yourself rather than believing the producer's own run
   (property 2). A finding means the document is removed, not repaired.
4. **Is it one file?** Open it with the network off. Anything it fetches at open time tells a third
   party when the reader opened it (property 6).
5. **Is the prose written for this reader?** The only inference in the chain is the summary. Read it
   as an outsider would: a sentence that would make sense only to someone who knows the system is a
   sentence that discloses the system.
6. **Do the labels mean what they meant last time?** A pseudonym is stable or the reader's comparison
   with the previous document is false (property 4).
7. **Is the map still inside?** It is never attached, never quoted, never in the same folder as the
   thing being delivered.

## What this procedure cannot do
It cannot tell you that a *true* summary is a *safe* one. Counts and dates are mechanical; prose is
not. The gate catches shapes, the reviewer catches meaning, and a document nobody reviewed should not
leave.
