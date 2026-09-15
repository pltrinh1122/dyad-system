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
  (`agent/provenance`) and on the kernel-only path (`check --guards`, Rule-14 property 3).
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
   text lives in the plan, the row, the record and the incident log, each already owned.
5. **Checked against the row.** The `disposition` entries of a record correspond one-to-one, in
   order, with the entries of its row's `disposed` column; a mismatch is a failing check, so a
   dropped or invented disposition is visible without reading the chat.

## Enforcement
`dyad/guards/agent/provenance.py` (`check_package`; agent corpus, placed per Rule-11 property 1;
tests in `dyad/tests/guards/agent/test_provenance.py`, Rule-12; registered in Rule-11's runner as
`agent/provenance`). It fails on: a record whose title id differs from its file name; entries not
numbered from 1 without gaps; an unknown `kind`; a missing or unterminated fenced body; a
`disposition` count that differs from the row's `disposed` count (property 5); a credential shape in
any body (property 2's residue: `gh[pous]_…`, `github_pat_…`, a PEM private-key header, an
`Authorization:` bearer or token value); and any tracked `*.jsonl` under the d-work store. It warns
on: a row with id at or above `provenance.SINCE_ID` that has no record — a warning, not a failure,
because a concurrent session (Rule-16) opens rows without having loaded this Rule, and a red `main`
is the wrong way to learn that; and a bare 40-hex string, which a commit sha and a Gitea token
share.
Whether an entry is a faithful transcription is inference, as every clerical write is
(`../../agent-corpus/falsification/e3-plan-gate.md` states it of the `Y plan` entry); property 5's
count is its mechanical fence, and the Operator's own copy of the chat is the other.

## Provenance
Operator gap, ledger #54 (2026-09-12, deferred) and #55; prompted again and planned as #164
(2026-09-14). Falsified; see `../falsification/rules/rule-7-provenance.md`.

Set: System Requirements.
