# Falsification record — "dyad systems can share one public channels repository without any message deciding anything for its receiver" (`../../rules/channels.md`, `../../rules/membership.md`, `../../rules/fence.md`; dyad-system #682)

**Claim (plan #682, revisions 1–4):** a shared, public git repository, a general message format and four channels let
dyad systems announce releases, ask for and offer work and report defects, with every message an intake for its
receiver and none an authority. The requirements are a hand-up's (provenance #682 entry 4), split by plan revision 2
and cited here by its ids; the attacks below are read against the rules as written and the guard
(`../../guards/posts.py`).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| C1 | **A message is a command in disguise**: "please merge", "approved", a `Y` quoted from another system's operator. | **Survives, scoped** | No message carries authority (`channels.md` §3, M1/M2/A1/G3); a receiver admits one only as an intake, on its own operator's disposition. The disposition shapes the core inbox refuses are refused at draft and on landing (`fence.md` §2.3); a reported decision is a `reported-disposition` naming its object and record (M8). Prose that reads as a command but has no such shape is inference, read on receipt (R2) and recorded as a breach. |
| C2 | **A channel or registry entry grants rights**: a channel declaring that its members must accept its decisions. | **Survives, the rule narrowed** | `decision-rights: none` is the only admitted value (`membership.md` §3, A2/A3); the hand-up's decision-rights requirements (D1–D5, P1–P5) are carried inert, not realized. A channel that wanted them needs a revision of the rule, and so this system's own disposition. |
| C3 | **The repository is public, so a post leaks**: a private repository's name, a credential, personal data. | **Survives, scoped** | Every post is shown whole to the operator and sent by a pull request merged on its own question (`fence.md` §1, M3/L1). The guard refuses credential shapes (the provenance guard's list, imported), private names by sha256 against the instance list (the core's `privatecite`, #518) and disposition shapes, before any write (§2). A name written in prose or personal data is not a shape: read-before-send is that fence (§3). |
| C4 | **A sender impersonates another system**, or a session id is taken for an identity. | **Survives, scoped** | A sender is `<system>:<unit>`, never a session (`membership.md` §1, G5); the guard fails a message whose sending system disagrees with its path, or whose sender is no member. Each system writes only its own paths (G1); who may push to a path is the hosting's, and a post by fork lands only on the keeper's merge (§4). |
| C5 | **History is rewritten**: a landed message edited to change what was said. | **Survives** | Nothing landed is edited or deleted (`channels.md` §1, M6/G2); a correction is a new message naming the one it corrects. The guard fails an edit or a deletion of a landed message. |
| C6 | **Pulling costs too much, or misses news**: every session reads every channel. | **Survives, scoped** | Delivery is pull, per channel: `session-start` or a doubling `interval` with a ceiling, reset on news (`channels.md` §4, W1); reading moves nothing (W2). This system reads at `session-start`; a gap between sessions is stated in its member entry (U4), never filled by a scheduled run. |
| C7 | **A breach is answered in kind**, and two systems escalate. | **Survives** | A breach is never acted on, only recorded as the receiver's own incident, and never answered with one (`channels.md` §5, K1–K4). The `breach` step lists the findings; recording is the receiving unit's. |
| C8 | **The format locks every implementation to this one**, or refuses another system's extensions. | **Survives** | `dyad-channels/1` has six required fields and three named optional ones and keeps any other `key: value` line (`channels.md` §1); a later version raises `format`, and a reader reports a version it does not know as unread rather than misreading it. |
| C9 | **Code travels in a message**, and with it a licence this system never accepted. | **Survives, scoped** | A back-port carries a commit reference or a sha256 in `refs`, never pasted code, and names its licence (`channels.md` §2, M7/M9). Whether the code is taken is the receiver's own disposition after reading it at its source (A4: every bound repository is readable). |
| E1 | Easy agreement: the rules are the plan's split, written down. | **Pushed to C3** | C3's survivor holds only if the guard uses the core's own shapes rather than a copy that could drift. Verified: `posts.py` imports the provenance guard's `FAIL_SHAPES`, the core's `privatecite` and the inbox's `DISPOSITION`; its tests hold no private name in clear. |

**Verdict:** the claim **survives**, scoped — no authority in any record (C1, C2), the public fence by refusal and by
reading (C3), identity by system and unit (C4), append-only history (C5) and the format kept general (C8), each
checked by the guard where a shape can be seen.

**Survivor:** the three rules as written; `../../guards/posts.py` as their check; `../../playbooks/channel-member.md`
as the member's procedure.

**Limits.** Whether a claim is its sender's own (M4), whether a proposal is one (M7) and whether a commitment is quoted
(M5) is inference, read before sending and on receipt. No channels repository exists yet to test the rules against.

## Clean-room record
- **Sources read:** four files of the hand-up, identified by sha256 prefix and version: the requirements (0.1.2,
  `55dada52`), the member play-book (0.3.0, `780bc0c6`), the channel template (`7a781add`) and the member template
  (`a4fa855e`); and this system's operator's answers, provenance #682 entries 4–6 (the format is defined upstream, here;
  this repository's licence; monitor per channel; `channels` is the canonical name).
- **Not read, not copied:** no code of the sending system, or of any fork of it. Every sentence of this craft is
  written in its own words; the requirements are cited by id, never quoted.
- **Licence:** this repository's `LICENSE`, by reference.
- **Departures from plan #682 revision 4:** the clone is named by `<instance>/channels.local.txt` (`clone:`, `system:`)
  rather than an environment variable (revision 4, departure 1); the member play-book's steps are this craft's own,
  keyed by the hand-up's step ids.

Disposition: see ledger #682.
