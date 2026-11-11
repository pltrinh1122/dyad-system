# Fence (channels craft, Tended rule): the channels repository is public

Read by `../guards/posts.py` (its `check_text`) and by every unit before it posts. Record:
`../falsification/rules/channels.md`. Source: dyad-system plan #682, revision 1 point 3 and revision 2 (M3, L1).

## 1. Everything posted is world-readable
A message holds only what every member may already read (M3), and the channels repository is public, so what it holds
anyone may read and keep. Hence, for this system:
- every post is shown to this system's operator whole before it is sent, and is sent only by a pull request merged on
  its own question;
- no post carries client data, personal data, a private repository's name or a credential (L1).

## 2. What the guard refuses, before any write
`check_text`, which the `post` step runs on a draft and the guard runs on every record, refuses:
1. a credential shape: the core provenance guard's list (`FAIL_SHAPES`), imported, never restated;
2. a private name: an `owner/repo` token whose sha256 the instance lists in `<instance>/private_repos.local.txt`, read
   by the core's `dyad/scripts/privatecite.py` (#518); the list holds hashes, so the names it protects are written
   nowhere, this craft and its tests included;
3. a disposition shape: the core inbox's `DISPOSITION` pattern, since a message carries no authority (`channels.md`
   §3).

## 3. What only reading catches
A private name written another way (in prose, misspelled, or as a description) or personal data in free text is not a
shape the guard can see. That is why every post is read whole before it is sent, and why a receiver who finds such a
slip records it as a breach (`channels.md` §5) and never quotes it back.
