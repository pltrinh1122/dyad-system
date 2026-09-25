# Redaction (disclosure craft, Tended rule)

**What it governs:** what may leave a dyad system in a document handed to a party outside it, and in
what form. Read by `dyad/playbooks/ds-report-incidents.md`; checked by `crafts/disclosure/scripts/redaction.py`.

This is a Tended rule: it governs the craft, never the Agent's process (Rule-4). It says what a
disclosure must look like. *When* one is produced, *who* releases it, and *what question* precedes the
release are the play-book's and the Agent Rules' (Rule-2, Rule-3) — never this file's.

## 1. Allow-list first
A disclosure is **assembled**, never filtered. Only the fields the producing procedure names may appear
in it, and none of them is copied verbatim from the corpus. The reason is not caution, it is
arithmetic: a deny-list can enumerate the shapes it knows (an address literal, a path, a key) and can
never enumerate an English sentence that explains an internal. A corpus of prose written for insiders
is exactly such a corpus.

## 2. The deny-list is the fail-closed gate, not the mechanism
The deny-list runs over the **assembled output**, before it is written and again after. Any finding
means **nothing is written and nothing is delivered**. There is no "redact and re-check", no override
flag, and no partial write: a document that fails the gate is removed, and the failure is an incident
for the procedure that produced it.

## 3. Three classes
| class | treatment | why |
|-------|-----------|-----|
| **A — identity** | **removed** | who and where: host names, absolute paths, address literals, e-mail addresses, session names and ids, repository URLs, request numbers, personal names, and the key shapes the core's provenance guard already recognises (imported, never re-listed) |
| **B — proprietary substance** | **pseudonymized, never deleted** | what the practice is made of: rule numbers, guard, module and craft names, file paths, defined terms, ledger ids. Deleting them leaves a document of dates; replacing them with stable pseudonyms keeps what an outside reader can act on — how many faults in one subsystem, which failure mode repeats, whether a class is closed |
| **C — retained** | kept, and gated like everything else | dates, the failure-mode class, the consequence shape, the mitigation status, and prose written *for the audience* rather than taken from the corpus |

## 4. Class B is a map, and the map never leaves
Pseudonyms live in one instance file (`<instance>/disclosure/pseudonyms.md`, agent zone), never in this
craft (Rule-11 property 1). A pseudonym, once allocated, is never reassigned and never reused for a
different real value: a reassignment silently falsifies every document already delivered. The map is
the exact inverse of every document produced from it, so it is never copied into one, never attached to
a delivery, and never printed by a command that a document quotes.

## 5. A disclosure names its audience
Every document carries the party it was built for, as that party should see themselves named, and the
watermark of the source it covers (`covered through: <n> rows, latest <date>`). A document that does
not name its reader cannot be checked against the disposition that released it, and a document without
a watermark cannot be told from a later one.

No file of this craft, and no file of the core craft, names any recipient: the audience is a parameter.

## 6. A disclosure is one self-contained file
One file, no external reference of any kind — no stylesheet, script, image or font fetched at open
time. It is delivered by hand, on a stick, or as an attachment, to a reader who may open it offline and
who must not, by opening it, tell anyone that they did.

## 7. Deterministic
Two runs over an unchanged source and an unchanged map produce byte-identical files, so that a
document's sha256 is a fact about its content and can be quoted alongside it. No timestamp of its own,
no ordering by hash iteration.

## Checked, and not
`crafts/disclosure/scripts/redaction.py` checks: the class data is well-formed and every regex compiles;
every class named above has at least one rule; no pattern is duplicated; the pseudonym map, when
present, has unique pseudonyms and no real value mapped twice. `verify <file>` is the gate of property
2, runnable on any file by either party. Tests: `crafts/disclosure/tests/`.

What stays inference: whether a summary written for an audience actually discloses nothing (property 1
is the reason it is reviewed, property 2 the reason a slip of *shape* is caught), and whether a
pseudonym's `kind` is the right one.

## Provenance
d-work #166, the `ds-report-incidents` play-book. Falsified in plan `agent-corpus/d-work/plans/166.md`
(attacks A1, A2, A9) and in `falsification/rules/redaction.md`.
