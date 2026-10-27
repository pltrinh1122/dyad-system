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

## Amendment — d-work #511: the commit form, the quoted-line rule, no persona named

**Claim (plan #511, from the communicate seat's outline research):** the rule cannot cite a commit, it lets a quoted
line or a commit message pass as the Operator's words, and it names one instance's persona inside a craft.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 9 | A commit is citable by `repo:<owner>/<repo>@<sha>:<path>`. | **Refuted** | A commit message has no path; fourteen of the season outline's past citations are commits. `commit:<owner>/<repo>@<40-hex sha>` is declared in `repos:` like `repo:`, resolved against a local clone by `git cat-file -e <sha>^{commit}`, failing when the clone lacks it, and otherwise counted in the same `warning: … inference` line (§1, §5, §7). |
| 10 | Text under the Operator's git identity, or a `>` line in a provenance entry, is the Operator's words. | **Refuted** | Commits carry the Operator's git identity whoever wrote them, and a `>` line quotes the reply the Operator was answering. A context citation is the Operator's words only outside quoted lines; a commit message is record, never the Operator's voice (§1). Inference, stated: the guard resolves the entry, not which of its lines an episode quotes. |
| 11 | The persona's instance name inside the rule is harmless. | **Refuted, hygiene** | A craft carries no instance example (Rule-11 property 1). §2 and the vocabulary's `persona` row name no persona; the name is the Operator's to give, at the instance, and a change of it changes nothing here. |

**Verdict:** the claim survives in all three parts; `episodes.py` gains the fourth form (`FORMS`, its invariant
`four-citation-forms`) with two tests, and the template gains a `commit:` footnote. No `VERSION` bump: the craft has
no tag.

Disposition: see ledger #511.

## Amendment — d-work #515: a labelled fiction layer for the persona

**Claim (the Operator, relayed from the communicate seat):** the persona's character is private and needs no evidence;
whatever is written of it is labelled fiction based on a real-life model.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 12 | The craft's premise is that nothing is invented (attack 1); a fiction layer breaks it. | **Survives, scoped** | The premise binds the record layer — the system's events, the seats and their audited flaws — which stays cited and guarded as before. The fiction layer is confined to the persona's character, inner life and daemons, the one thing the record cannot hold and the Operator declares private (§1, §2). |
| 13 | A reader cannot tell the layers apart. | **Survives, two labels** | The header key `fiction: persona, based on a real-life model` and a `*(fiction)*` marker opening each interior paragraph make any sentence's layer decidable by its paragraph. The guard fails a marked passage under no such header and a `fiction:` value other than the label, and warns on the header with no marked passage (§2, §7). |
| 14 | Fiction leaks into the record layer: an invented event, or a seat's invented thought. | **Survives, fenced** | A footnote inside a marked passage fails, so a passage cannot be both fiction and record. Every footnoted event still needs its citation, and a seat's thinking stays its plan or falsification record (§1). Inference, stated: whether a marked passage tells only the persona's interior is read at publication. |
| 15 | §3's approval rule for a flaw attributed to the Operator becomes moot. | **Confirmed, scoped** | It is moot for the persona's daemons, which are fiction. It still binds every statement about the real Operator in the record layer (§3). |

**Verdict:** the claim survives with the two labels and the fence of attack 14. `episodes.py` gains `marked_passages`,
the constants `FICTION_KEY`, `FICTION_LABEL` and `MARKER` and their invariant, with six tests. The template carries the
header key and a marked passage. The vocabulary gains `fiction layer`, and the `material-kind` DMC record gains it as
an outcome. No `VERSION` bump: the craft has no tag.

Disposition: see ledger #515.
