# Rule-7: provenance

**Intent:** Preserve verbatim, in the corpus, every Operator prompt and disposition a d-work is
built on.
**Target:** a provenance record

## Boundaries (out of scope)
- The chain of authorization as *data* — Rule-3: the row's `disposed` column records that a
  disposition was given and of what kind. Rule-7 records the words it was given in, and nothing
  else; the row keeps owning the chain, and Rule-7 is checked against it.
- What a prompt authorizes, when a d-work opens or closes, and the counter-prompt forms — Rule-3;
  who may dispose — Rule-2. Rule-7 stores; it never disposes and never gates.
- The Agent's own words: a plan is the plan file (Rule-15), a verdict is a falsification record
  (Rule-9), a departure is an incident row (Rule-3). None is a provenance record.
- The raw session transcript the harness writes (`~/.claude/.../*.jsonl` for one kernel, nothing
  at all for another): never a corpus file (property 2). Copying one elsewhere on the machine is a
  host action — Rule-8 classes it, Rule-7 neither requires nor forbids it.
- The per-machine memory cache — the frame convention; it summarises ratified corpus and is not
  provenance.
- Where the store's guard lives and what it declares — Rule-11 property 1 and the sysarch craft's
  `crafts/sysarch/rules/guards.md`; the reference from a record to its row — Rule-20; zones —
  Rule-1 (the store is agent zone).

## Conditions (triggers)
- An Operator prompt opens or is received on a d-work: its text is written as an entry, then.
- The Operator disposes a counter-prompt: the disposition's text is written as an entry, then,
  in the same clerical commit that records it in the row (Rule-3).
- Every push and PR: `dyad/guards/agent/provenance.py` runs through `package.py check`
  (`agent/provenance`) and on the kernel-only path (`check --guards`, Rule-14 property 3), where it
  also judges the commits being pushed as a transaction guard (Enforcement).
- A `*.jsonl` is about to be tracked under the d-work store: forbidden (property 2).

## Properties
1. **One record per d-work.** The provenance store is `<instance>/d-work/provenance/`; a record is
   `<instance>/d-work/provenance/<id>.md`, one file per id, beside the
   row and the plan file and collision-free in the same way (Rule-16). It opens with
   `# Provenance #<id>`, may carry `session:` and `raw transcript:` lines, and holds entries:

       ## <n> <kind> <YYYY-MM-DD>[ <note>]

   numbered from 1 without gaps, `kind` either `prompt` or `disposition`, each followed by a fenced
   block holding the text exactly as the Operator gave it. The fence is what makes the text data:
   a prompt containing a heading, a pipe or a backtick cannot reshape the file that stores it.
2. **The raw transcript is never committed.** It carries whatever the session carried, credentials
   included; it is megabytes per session, permanent once pushed; and its location is a property of
   one kernel and one host, not of the dyad (Rule-14 property 2). The Agent therefore writes the
   entry from the prompt it received, and never reads a harness file to do it.
3. **Written when it happens, never gathered later.** An entry is appended in the clerical commit
   of the event it records (Rule-3: the store is under `<instance>/d-work/`, so the fence already
   admits it). No session is required to reach its own end, because nothing waits for the end.
4. **The Operator's words only.** A provenance record holds what the Operator wrote. The Agent's
   text lives in the plan, the row, the record and the incident log, each already owned. An
   Operator prompt relayed by another agent (Rule-3, Intake) is still an Operator's words: entered
   verbatim as the message carried it, the entry note `relayed via <session>`; the relaying agent's
   own words are never entered — a defect's observation stays in the plan file (#34).
5. **Checked against the row.** The `disposition` entries of a record correspond one-to-one, in
   order, with the entries of its row's `disposed` column; a mismatch is a failing check, so a
   dropped or invented disposition is visible without reading the chat. A row the instance lists as
   predating enforcement (Enforcement) holds exactly as many fewer as the list says its earlier
   dispositions were, whose words were never written and which property 3 forbids writing now;
   every disposition after enforcement is exact.

## Enforcement
`dyad/guards/agent/provenance.py` (`check_package` and `check_transaction`; agent corpus, placed
per Rule-11 property 1; tests in `dyad/tests/guards/agent/test_provenance.py`, Rule-12; registered in
Rule-11's runner as `agent/provenance`). Its two checks are split by what a failure costs (#191):
- **Transaction**, each non-merge commit being pushed (the range's own history, merge base to head)
  against its parent, as property 3 binds a commit: a row the commit adds brings at least one new
  entry in its record — a `disposition` when it is born `backlog`, which only a disposition opens
  (Rule-3); a row going `backlog` → `open` brings a `prompt` (Rule-3: the Operator prompts for it); a
  row whose `disposed` gains k entries gains k `disposition` entries; and a record only grows — its
  earlier entries stay word for word and the file is never deleted, a merge commit's records judged
  against each of its parents. This check blocks only the push
  that creates the gap, on the session that wrote it, which is what a concurrent session (Rule-16)
  that has not loaded this Rule needs. `dyad dwork new|state` write the entries with the row
  (`--prompt`, `--said`, each also `-file`), make every refusal before the first write, and refuse a
  row, a disposition or a `backlog` → `open` without its words.
- **State**, over the store: it fails on a record whose title id differs from its file name;
  entries not numbered from 1 without gaps; an unknown `kind`; a missing or unterminated fenced
  body; a `disposition` count that differs from the row's `disposed` count (property 5); a credential
  shape in any body (property 2's residue: `gh[pous]_…`, `github_pat_…`, a PEM private-key header,
  an `Authorization:` bearer or token value); any tracked `*.jsonl` under the d-work store; and a
  row with no record that the instance does not name in `<instance>/provenance_legacy.local.txt`.
  That list holds the rows that predate enforcement, one `<id> <n> <reason>` per line, n the
  dispositions the row held whose words were never written (property 3 forbids writing them now): a
  listed row's record holds exactly n fewer disposition entries than the row, and a listed row with
  no record passes only while its `disposed` holds n. A list line of another shape, an id listed
  twice, a listed id that is no row, or an n above the row's count fails too. With the transaction
  check in place, a gap reaches the tree only around the hook; it then fails this check in every
  session until it is recorded or listed — the alarm for that bypass, a cost the design accepts.
  Naming a row in the list is a decision, made in a reviewed agent-zone PR (the list lies outside
  `<instance>/d-work/`, so no ledger-only commit can touch it). The list is instance data and never
  the core's (Rule-11 property 1). It warns on every unrecorded row while an instance keeps no list
  — a system installing this version, which writes its own — and on a bare 40-hex string, which a
  commit sha and a Gitea token share.
Whether an entry is a faithful transcription is inference, as every clerical write is
(`../../agent-corpus/falsification/e3-plan-gate.md` states it of the `Y plan` entry); property 5's
count is its mechanical fence, and the Operator's own copy of the chat is the other.

## Provenance
Operator gap, ledger #54 (2026-09-12, deferred) and #55; prompted again and planned as #164
(2026-09-14). Falsified; see `../falsification/rules/rule-7-provenance.md`. Property 4 gains the
relayed-prompt sentence 2026-09-16 (d-work #34, Rule-3 Intake). Enforcement split into a
transaction check that fails the gap where it is born and a state check that fails against the
instance's legacy list, replacing `SINCE_ID` (an id of an earlier ledger that had come to warn on
unrelated rows and to exempt rows holding dispositions); property 5 gains the legacy sentence
2026-09-29 (d-work #191); see the same record, amendment #191.

Set: System Requirements.
