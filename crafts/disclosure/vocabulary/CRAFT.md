# disclosure craft vocabulary (Tended terms)

One row per term; `rule` names the craft rule (`../rules/<rule>.md`) that owns it. A craft term is referenced,
never defined, by the Agent vocabulary (Rule-6).

| term | definition | rule |
|------|------------|------|
| disclosure | one self-contained document handed to a party outside the dyad system, assembled by allow-list and passed by the deny-list gate | redaction |
| audience | the party a disclosure is built for, named on it as they should see themselves named; a parameter, never a value in a craft or core file | redaction |
| redaction class | one of three treatments a value receives in a disclosure: A removed, B pseudonymized, C retained | redaction |
| pseudonym map | the instance file mapping each Class B value to the stable pseudonym a disclosure shows instead; the inverse of every disclosure, and never delivered with one | redaction |
| deny-list | the shapes that must not appear in an assembled disclosure; the fail-closed gate, never the mechanism that produces one | redaction |
| watermark | the line naming the source a disclosure covers — row count and latest date — by which one disclosure is told from a later one | redaction |
