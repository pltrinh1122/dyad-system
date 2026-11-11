# Knowledge harvest: aged content, ingest once and consume many, split by `dmc:intake-split` (d-work #677)

Study, not a build (plan #677, A1). Source: the hand-up held in `agent-corpus/d-work/plans/677.md`, Appendix, as received
2026-11-11, from a downstream dyad system of the same operator; its repository name is withheld there and here. The
operator's words that frame this study: provenance #677 entry 1. The split is decided by `dyad/dmc/intake-split.jsonld`
(#676, on `main`).

## 1. The aged knowledge record (R4, R3, C1)
A **knowledge record** is one claim about the world, with five parts:
- **its content**: a typed body (`@type` one of the install's record types), JSON-LD like the core's decision records
  (C1);
- **its source**: the artifact it was read from, by an id the ingester resolves (R3), and the span quoted, exactly;
- **its time**: `validFrom` (when the source says it became true) and `recordedAt` (when it was ingested);
- **its standing**: `supersededBy` (a later record of the same subject from a newer source) and `overturnedBy` (a
  ruling, a person's decision, named by its own record), either of which ends its currency (R4, #194/8 both);
- **its freshness**: fresh until `recordedAt` + its type's review interval, set per record type and never per record
  (#194/8); a stale record is still read, marked stale, until reviewed or replaced.

Currency is computed at read time from these fields, never stored: a record is *current* when nothing supersedes or
overturns it, and *fresh* when its review interval has not passed. So nothing rewrites a record when it ages, and the
store stays append-only, as this system's own stores are.

**This system already has aged content.** A precedent is overturned by a later ruling (a revised record, a
superseding row), a plan revision supersedes the one before, and a row's state ends its currency. The core's index
(`dyad/scripts/similar.py`, #642) indexes such content as static and is refitted only at named events (#642 Q5). The
same five parts describe it: a decision-log entry's source is its row, its standing is `precedent-entry` and later
blocks, its freshness the owner Rule's movement since the set's base. So the model is general (the prompt's "not only
just static content but aged content as well") and is the core's to define once (§4).

## 2. The flow: ingest once, consume many (R1, R2, R6)
1. **Ingest.** Each knowledge base has one ingester, run by its owner (R6, #194/13). It reads each artifact once and
   writes records in the generic form, typed by the schema its install declares (R2, #194/3–4).
2. **Store.** The intermediate form is the records, append-only, one store per knowledge base.
3. **Consume.** A consumer (a dyad system) reads the union of the knowledge bases it may read (R7), resolves duplicates
   (the same source span read twice, or the same claim from two sources, by its source id and a content digest), and
   selects by relevance to its own purpose (R1, R5).
Nothing is ingested twice for two consumers, and no consumer writes back into a store.

## 3. Selection by relevance (R5, C2)
Two steps (#194/10):
- **A cheap first selection.** TF-IDF cosine is what the core already runs (`similar.py`: `tokens`, `tfidf`,
  `cosine`); an embedding search is the operator's example of the kind meant (#194/10). Both answer "related to this
  purpose" with a score, and both apply the currency filter of §1 at read time.
- **A judgement step** only for what the first cannot settle: below a threshold, or within a margin of the runner-up.
  That is the abstention `similar.label` already makes.
An embedding search needs a model and a host. Under C2 the host is one the operator controls, so it is a **library
row** (Rule-14) with its replacement named (TF-IDF), never kernel, and its endpoint and key are instance data, never in a
craft.

## 4. The sharing boundary (R7, C3, C4)
A knowledge base's owner elects to share it, all or nothing at first (#194/14). The sources include other people's
correspondence (C4), so the boundary is hard:
- no record, store or copy of a client's mail or transcripts ever comes into this repository or a craft (the privacy
  rule of `dmc:intake-split`);
- a craft may ship the switch, the reader check and the fixtures it writes itself, never data.
How a reader proves its access (C3: by repository access, or a key) is the operator's to settle downstream; asked back.

## 5. Where the mechanism lives (A2): the craft-instantiation criteria
Applied to "a harvest practice: ingesters, the generic record and schema hook, the union, the sharing switch":
- **D1 classification.** The *practice* holds no sensitive data; its *instances* do (C4). The craft is non-sensitive
  and stays here; each instance's data stays in its own system. Not fired for the craft.
- **D2 disposer.** The same operator disposes. Not fired.
- **D3' craft availability.** No installed craft practises harvesting; the downstream craft is not offered (the
  hand-up, "Not an offer of code"). So a new craft is authored here.
- **D4 ledger coupling.** Its rows would `refs` the core's aged-record row and the embedding adapter's. Not fired.
- **D5 lifecycle.** No lifecycle of its own beyond its releases. Not fired.
- **D6 zone fit.** `craft` holds it. Not fired.
Outcome: **a new Tended craft here**, authored from scratch. No run-book step ran: `dyad runbook run craft new`
scaffolds, which is the carried row's work, so this study cites no event.

## 6. The order (R9, A4)
Downstream's first use case is served first, and generality it does not need waits (#194/16). Upstream's order follows:
the aged record (§1) first, since every consumer reads it; then the craft's ingest and union for one knowledge base;
the embedding adapter last, since TF-IDF already gives a first selection. Which consumer and record types come first is
downstream's (asked back, open questions 1–3).

## 7. The split, by `dmc:intake-split`
| item | outcome | ground |
|---|---|---|
| R1 ingest once, consume many | both | the flow (§2) is every operator's; which consumers, and their purposes, are the sender's |
| R2 a generic record, specific per install | both | the generic record and the schema hook are the craft's; each install's schema is the sender's |
| R3 every record traces to its source | upstream craft | every harvested record needs it, and it needs no instance data |
| R4 knowledge ages | upstream core | the aged record (§1) also describes this system's own indexed content, so it is a core record's concern |
| R5 select by relevance | both | the two-step selection and its adapter are upstream; the embedding host, its model choice and its key are the sender's (C2) |
| R6 several knowledge bases, one owner each, read as a union | both | union and duplicate resolution are the craft's; the bases and their owners are the sender's |
| R7 the owner decides sharing | both | the all-or-nothing switch and the reader check are the craft's; each owner's choice is the sender's |
| R8 one place for transcripts | downstream instance | a location is instance data |
| R9 the first use case first | asked back | rests on open questions 1–3, unsettled |
| C1 JSON-LD | upstream craft | the record format the craft ships, beside the core's JSON-LD records |
| C2 embeddings on an operator-controlled host | both | upstream, a library row naming no third-party service; the host and key are the sender's |
| C3 access by repository | asked back | open question 6, unsettled |
| C4 client mail and transcripts | downstream instance | another party's records: the privacy rule keeps them down |
| C5 a criterion for what is configurable | upstream craft | a decision record the craft ships, by which each install decides; which values are configurable at launch is the sender's (open question 7) |
| open questions 1–8 | asked back | the sender's operator has not settled them |

The provisional reading of plan #677 holds unchanged.

## 8. The builds this split names (the carried rows)
Grouped by the unit of work that would build them (plan #677's mandate scope, ceiling 4); three:
1. **#679, aged records in the core** (R4; the core half of R5): a core record of the aged knowledge record's five parts and
   currency at read time, read by `similar.py`'s callers as a filter.
2. **#680, a harvest craft** (R1–R3, R6, R7, C1, C5; the upstream halves of the `both` items): a new Tended craft by the craft
   play-book, with fixtures it writes itself and no instance data.
3. **#681, an embedding search adapter** (R5, C2): a library row (Rule-14) and its client, its replacement TF-IDF, never
   kernel.
Each is born `backlog` under plan #677's plan-`Y` (`Y backlog (mandate #677)`), `refs: 677`; no fourth row is needed.

## 9. The hand-down (draft, not sent)
Shown to the operator in this row's Done; sent downstream only on the operator's own `Y`, as its own question.

```
Hand-down, 2026-11-11: the knowledge harvester hand-up (your d-work #202), split by dmc:intake-split

from: pltrinh1122/dyad-system
status: draft, not sent

Upstream builds, each as a row of its own (no dates promised):
- R4 (upstream core): an aged knowledge record — source, validFrom, supersededBy, overturnedBy, a review interval
  per record type — with currency computed at read time.
- R3, C1, C5 (upstream craft): a new harvest craft, JSON-LD records that trace to their source, and a decision record
  for what an install may configure.
- R1, R2, R6, R7 (both, upstream half): the craft's ingest-once flow, a generic record with a schema hook, union and
  duplicate resolution across knowledge bases, and an owner's all-or-nothing sharing switch.
- R5, C2 (both, upstream half): a two-step relevance selection, TF-IDF first; an embedding search adapter as a library
  row, no third-party service.

Stays with you:
- R8, C4 (downstream instance): where transcripts land, and every client record; none comes upstream.
- R1, R2, R5, R6, R7, C2 (both, your half): your consumers and purposes, your record schemas, your knowledge bases and
  their owners, each owner's sharing choice, the embedding host, its model and its key.

Asked back (nothing is built for these until answered):
- R9 and open questions 1–3: which consumer is first, its record types on day one, and what "working solidly" means in
  checks your operator can evaluate.
- C3 and open question 6: access by repository, or its intent only.
- Open questions 4, 5, 7 and 8: where and how often ingest runs, languages, the configurability criterion's values,
  and who reads a shared base.
```

## Limits
- Inference throughout: the split is the home's judgement under `dmc:intake-split`, each ground stated; nothing is
  measured.
- No code was read from the sender, and none was written here.
