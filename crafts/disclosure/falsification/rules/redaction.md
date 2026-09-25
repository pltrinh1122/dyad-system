# Falsification record — the redaction rule (disclosure craft)

**Claim:** an incident corpus written for insiders can be turned into a document that is safe to hand
to a party outside the system, and still useful to that party.

| # | attack | result | survivor |
|---|--------|--------|----------|
| 1 | Useful or safe, never both: strip every rule, module and path and only dates remain. | survives, scoped | Class B pseudonymizes rather than deletes, so counts, groupings and repetition survive. Conceded: the per-row prose cannot be machine-redacted into usefulness, so a summary is written for the audience instead of derived from the corpus. |
| 2 | A deny-list cannot be complete; a redaction rule resting on one is theatre. | **confirmed** | Which is why property 1 makes the allow-list the mechanism and property 2 makes the deny-list a gate. A gate need not be complete to be worth having: it catches a *shape* that slipped into prose, which is the failure actually observed in practice. |
| 3 | The gate will be overridden the first time it is inconvenient. | survives | No override exists: property 2 has no flag, and a finding removes the document. The cost is a refused build, which is cheap; the alternative cost is unbounded. |
| 4 | Stable pseudonyms leak by correlation: enough documents and a reader reconstructs the map. | survives, scoped | True in the limit, and stated: a reader learns the *shape* of the system — how many components, which fails most — which is exactly what the document is for. What no document yields is a name, a path, an address or a rule's text. A reader who needs more asks, and the Operator disposes. |
| 5 | The map is the crown jewels and is tracked in the repository. | survives | It is instance state, never craft content, and it never enters a document. Tracking it is what makes a pseudonym stable across sessions; the alternative — regenerating labels per report — silently falsifies every comparison. |
| 6 | Determinism is a nicety, not a property worth a rule. | refuted | A document's sha256 is quoted in the completion evidence and in the delivery question. Without determinism the hash is a fact about the run, not about the content, and re-verification is impossible. |
| 7 | A month is not a failure mode: grouping by date is not the grouping that was asked for. | **confirmed** | Recorded as a limit, not hidden: the month is the coarsest grouping the log's own data supports without inference. Mode-level grouping waits for mode records that carry their row ids (a backlog row of d-work #166). |

No gap found beyond attack 7, which is carried as a backlog row rather than a survivor.

Disposition: see ledger #166.
