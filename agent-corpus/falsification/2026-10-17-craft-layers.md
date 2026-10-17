# Falsification record — the craft layer: base, system, admin, practice (d-work #341)

**Claim (Operator prompt, 2026-10-17, a compressed claim chain from a side thread on #340).** Four crafts fill
three layers named by what each does for the Operator, a fourth layer `practice` is defined by one test,
Rule-11 property 2 is unmet twice, `sysarch` and `syseng` stay apart, and `countersign` consolidates into the
base. The audit is `../audits/2026-10-17-craft-layers.md`; its §1 holds the re-run of every claim. This record
attacks the re-run and each proposal.

**Disposition:** disposed by the Done-`Y` of d-work #341 (Rule-2; see ledger #341).

## The chain

| # | attack | result | survivor |
|---|---|---|---|
| F1 | The chain is the Operator's; re-running it is theatre. | refuted | Three results moved: `sysarch` is cited by eight Rules, not six (Rules 5, 7, 18 added — `git grep -l '\`crafts/sysarch' -- dyad/rules`); the sysarch/syseng change rates are alike, not different (`git log --oneline -- crafts/<c>`: 15 vs 11 commits, 10 vs 7 bumps, 8 vs 5 tags since 2026-09-14); a core play-book cites `disclosure`. |
| F2 | "Only `sysadmin` declares `BUNDLED_WITH_CORE`" could be stale. | confirmed at `8b7fc27` | `git grep -n BUNDLED_WITH_CORE -- crafts` finds one declaration, `crafts/sysadmin/guards/changelog.py:36`; `countersign/README.md` says it has none. |
| F3 | "Cited by a core Rule" is ambiguous: a citation in prose, a `Set:` line and a backticked path differ. | survives, scoped | The audit uses the one the reference guard resolves — a backticked `crafts/<c>/…` token in Rule text (`rule.text->path`) — and counts `Set:` lines separately (five name sysarch or syseng, one sysadmin). Prose mentions (`countersign-system` in Rule-12) are not counted. |
| F4 | The `practice` test fails on its own member: `disclosure` is cited by the core. | refuted as a Rule citation; survives as a caveat | No Rule and no `Set:` line cites it; `dyad/playbooks/ds-report-incidents.md` does (lines 36, 42, 59). The test says "core Rule"; the audit states the play-book citation as L6 rather than widening or dropping the test. |
| F5 | Equal change rates refute "two crafts", so claim 4 should be marked refuted. | refuted | A reason is refuted, not a conclusion: the chain gave two reasons (kind of knowledge; change rate) and one stands. The record states which. |
| F6 | Claim 8's "second device" has evidence: cloud sessions are a second host. | survives, scoped | `host-platform.md` counts the cloud sessions under Linux, verified; the second *device* the Operator means is macOS or Windows, both "in scope, unmet". One `host-path` per system holds either way. |
| F7 | Easy agreement with a model the Operator already derived. | pushed | F1's three movements; F4's caveat; L2's counter (the base alone becomes uninstallable by choice) is the strongest case against the Operator's own proposal and is stated. |

## The proposals

| # | attack | result | survivor |
|---|---|---|---|
| C1 | L1 adds a vocabulary row for a layer with one member. | survives, scoped | The row is the *test*, not the member; the test is mechanical in principle (tokens per craft) and could become a `TREE_INVARIANT`. Stated as such. |
| C2 | L2 is one-way: once bundled, a base-only install is impossible, and `distribution.md` (#178) says it never worked green anyway — so nothing is lost; or the Operator wanted it and L2 forecloses it. | survives, scoped | Both are stated in L2's counter and reconciliation; the Operator chooses. |
| C3 | L2's two declarations change two released crafts: `BUNDLE.md` fails the push until the rows move. | refuted by Rule-11 p7 | A released craft whose `VERSION` moved ahead of its tag *warns* until the infra row; it fails only once the new version is tagged. Sequence: craft PR, tags, infra PR. |
| C4 | L3 reopens on "a change in what the crafts are", which is unmeasurable. | survives, scoped | The measurable half (rates) was measured and found alike; the kind-of-knowledge half is inference and said so. |
| C5 | L4 ignores that the shared model's other two systems may not exist or may already carry it. | survives, scoped | Not observed (§4); the ordering constraint — a home outside this repo first — is the Operator's own open question, carried, not resolved. |
| C6 | L6's "take the counter" edits a play-book that Rule-3 reads: is that a Rule edit? | refuted | A play-book is "read by a Rule, never a Rule" (vocabulary `play-book`); its edit is agent-zone content with no Rule-4 block and no Rule-5 statement. |
