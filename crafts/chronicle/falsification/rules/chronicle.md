# Falsification record — "a serial can tell a dyad system's journey in story form without inventing it" (`../../rules/chronicle.md`; dyad-system #502, #498 C4)

**Claim (Operator's, plan #498 revisions 1–3):** a serial blog chronicles the complete journey of The Dyad System in
story form — characters, character flaws, conflicts, climax and release — with Operator-0 as the main character,
the world context his own, and present growth interleaved with the back-story across every `pltrinh1122` repo. The
rule as written is plan #498's survivor of attacks 1, 3, 11, 12, 16, 17 and 19; the attacks below are those, read
against the rule and its guard.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | **A story invents** (#498 attack 1): characters, flaws and a climax pull toward fiction, and fiction presented as a system's record is fabrication. | **Survives, scoped** | Every event cites the artifact that holds it, as a footnote; story form shapes order, viewpoint and emphasis, never facts (§1). The guard resolves every citation and fails an episode that cites nothing or cites in no known form (§7). |
| 2 | **Real people's words and flaws go public** (#498 attack 3): the Operator is a character. | **Survives, scoped** | The Operator's words enter only from provenance records, by a context citation (§1); a flaw is attributed to the Operator only where the Operator approves it at publication (§3); no other real person is a character (§2). |
| 3 | **Hopes, dreams and a life outside the repo are not in the record** (#498 attack 11), which breaks attack 1's survivor. | **Survives, the rule refined** | Two kinds of material and nothing else: the record (`path:`, `repo:`) and the Operator's context — his own words given as prompts on the serial's rows, kept verbatim (`prov:#<id>/<n>`). The guard parses the provenance record with the core's own parser, so an entry that is not there fails. |
| 4 | **The persona is a real person under a thin pseudonym** (#498 attack 12). | **Survives, scoped** | The persona is the Operator's choice of how to appear, named by the Operator (§2); what context is given and each episode's publication are the Operator's (§6). |
| 5 | **The back-story is outside this repo, so the guard cannot resolve it** (#498 attack 16). | **Confirmed, the rule extended** | `repo:<owner>/<repo>@<40-hex sha>:<path>` — immutable once written; resolved against a local clone when one is reachable (`DYAD_REPOS_DIR`), failing when the clone lacks it; otherwise one `warning: … inference` line per episode, the `world` severity of Rule-20's register, property 2 — never a pass by assumption (§7). |
| 6 | **Quoting a private repo publishes it** (#498 attack 17). | **Survives, an escalation** | Every cited repo is declared in `repos:` with its visibility; an undeclared repo fails; a private one prints a warning naming it, and the episode's publication question names it for the Operator's approval (§5). |
| 7 | **Two timelines confuse readers** (#498 attack 19). | **Survives, scoped** | Every episode's header states `time: present|past, YYYY-MM-DD`, checked by the guard; the season outline sets the interleave, approved before its episodes (§4, §6). |
| 8 | Easy agreement: the rule is the plan's survivor, written down. | **Pushed to 3** | 3's survivor holds only if the guard reads the record with the parser Rule-7's guard uses; a re-parse here could drift. Verified: `episodes.py` loads `agent/provenance` by `dyadlib.find_guard` and calls its `store` and `parse`. |

**Verdict:** the claim **survives** — with the two kinds of material (3), the cross-repo form and its `world`
severity (5), the private-repo flag (6) and the time line (7), each checked mechanically where a check can run.

**Survivor:** `../../rules/chronicle.md` as written; `../../guards/episodes.py` as its check.

**Limits.** Whether a cited artifact says what the episode says it does is inference, read at each publication; no
episode exists yet to test the rule against; a `repo:` citation with no clone is resolved by nobody until one is
reachable.

Disposition: see ledger #502.
