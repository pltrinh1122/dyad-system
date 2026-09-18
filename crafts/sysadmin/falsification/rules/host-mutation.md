# Falsification record — sysadmin craft rule `host-mutation.md` (d-work #155)

**Claim:** the class table, the read-before-act procedure and the change-log columns of Rule-8 bind
the sysadmin craft, not the Agent's process, and can live as a Tended Rule the kernel cites by path.

Attacks carried from the core record (`dyad/falsification/rules/rule-8-host-mutation.md`), by id:

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 8.1 | Class edges are fuzzy (`git config` is not a repo transaction; is it a host action?). | Survives | Definition by exclusion stays in the kernel (host action, Rule-8 Target); the examples that place `git config` as reversible are this rule's. |
| 8.2 | The Agent classifies its own actions. | Survives, scoped | Doubt resolves to destructive ("when in doubt, destructive" — this rule); the class is in the plan the Operator authorizes (kernel). |
| 8.4 | A stated undo can be wrong. | Survives | An untested undo makes the action destructive (this rule's class table); the undo column is the change log's (this rule). |
| 155.3 | A moved sentence binds the Agent's process → misplaced Agent Rule (Rule-4 guard). | Confirmed for 3 sentences, kept in the kernel | Kept core: "destructive needs its own counter-prompt", "reversible authorized by the plan-`Y` naming it", "a conflict … is a blocking question, the Agent stops". Moved here: the class *definitions and examples*, the procedure's file list, the columns. |
| 155.13 | `dyad/templates/CHANGELOG.md` leaving core breaks the fresh install. | Confirmed | The seed is `templates/CHANGELOG.md` here; the core `TEMPLATES` drops it; the craft README states the hand copy until #156. |
| 216.1 | Adding `actor` widens what this rule's column list requires, but Rule-8's kernel governs only Agent-taken host actions — recording an Operator-independent action (Gitea UI) is outside the kernel's scope. | Survives, scoped | The column is craft-owned (Rule-8 Conduct: "the row's columns and its guard … are the craft rule's"); the kernel's scope is unaffected. An Operator-only action has no row the *kernel* requires until it widens (reported to `dyad-system`, d-work #216) — but the craft may still record one it learns of. |
| 216.2 | A guard that accepts a 6-column header as well as 7 (`OPTIONAL` suffix) is a weakened check during the migration window. | Refuted | Forced, not chosen: Rule-1 orders a craft PR before its dependent workstation PR, so `main` briefly carries the new guard against the old 6-column instance data; without the tolerance no push in that window would pass `pre-push`. The **template** stays exactly `FIELDS` (7 columns) throughout — only the *instance* header may lag, and only until the workstation-zone PR of the same d-work lands. |

Disposition: see ledger #155, #216.
